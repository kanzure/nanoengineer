#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>
#include <string.h>

#include <GL/glx.h>
#include <GL/gl.h>
#include <GL/glu.h>

#define XK_MISCELLANY
#define XK_LATIN1
#include <X11/keysymdef.h>

#include "allocate.h"

struct ObjectLine
{
  float x1, y1, z1; // endpoint1
  float x2, y2, z2; // endpoint2
  float r, g, b;    // color
};

struct ObjectSphere 
{
  float x, y, z; // center
  float radius;
  float r, g, b; // color
};

struct Object
{

#define OBJ_LINE 0
#define OBJ_SPHERE 1
#define OBJ_FRAME 2
  int type;
  
  union {
    struct ObjectLine line;
    struct ObjectSphere sphere;
  };
};

// A movie is a sequence of frames.  Each frame is a sequence of
// Objects, the last of which is of type OBJ_FRAME.  The movie array
// contains all of the Objects in all of the frames.  The frame array
// contains indexes of the first object in each frame.
struct Object *movie = NULL;
int *frames = NULL;
int numFrames = 0;
int numObjects = 0; // total in all frames
int startOfLastFrame = 0;
int currentFrame = 0;

int followLastFrame = 1; // if true, render a new frame whenever we get one.

static int attributeList[] = { GLX_RGBA, None };

static Bool WaitForNotify(Display *d, XEvent *e, char *arg)
{
    return (e->type == MapNotify) && (e->xmap.window == (Window)arg);
}

static double eyeR;
static double eyeTheta;
static double eyePhi;

static int windowWidth;
static int windowHeight;

static GLUquadricObj *quad;
static Display *xDisplay;

static void
resetEye()
{
  eyeR = 100.0;
  eyeTheta = 0.0;
  eyePhi = 0.0;
}

static void
sphere(double x, double y, double z, double radius, double r, double g, double b)
{
  float materialColor[4];

  materialColor[0] = r;
  materialColor[1] = g;
  materialColor[2] = b;
  materialColor[3] = 1.0; // alpha
  
  glEnable(GL_LIGHTING);
  glEnable(GL_LIGHT0);
  glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, materialColor);

  glPushMatrix();
  glTranslated(x, y, z);
  gluSphere(quad, radius, 8, 8);
  glPopMatrix();

  glDisable(GL_LIGHTING);
  glDisable(GL_LIGHT0);
}

static void
line(float x1, float y1, float z1,
     float x2, float y2, float z2,
     float r, float g, float b)
{
  glBegin(GL_LINES);
  glColor3f(r, g, b);
  glVertex3f(x1, y1, z1);
  glVertex3f(x2, y2, z2);
  glEnd();
}

static void
renderObject(struct Object *o)
{
  if (o==NULL) {
    return;
  }
  switch (o->type) {
  case OBJ_LINE:
    line(o->line.x1, o->line.y1, o->line.z1,
         o->line.x2, o->line.y2, o->line.z2,
         o->line.r,  o->line.g,  o->line.b);
    break;
  case OBJ_SPHERE:
    sphere(o->sphere.x, o->sphere.y, o->sphere.z,
           o->sphere.radius,
           o->sphere.r, o->sphere.g, o->sphere.b);
    break;
  case OBJ_FRAME:
    break;
  default:
    fprintf(stderr, "unknown object type: %d\n", o->type);
  }
}

static void
renderFrame()
{
  struct Object *o;
  
  if (currentFrame < 0) currentFrame = 0;
  if (currentFrame >= numFrames) currentFrame = numFrames - 1;
  if (currentFrame >= 0) {
    o = &movie[frames[currentFrame]];
    while (o->type != OBJ_FRAME) {
      renderObject(o);
      o++;
    }
  }
}

static void
repaint()
{
  float lightPosition[4] = { 1.0, 0.5, -0.1, 0.0 };

  double eyeX;
  double eyeY;
  double eyeZ;

  if (eyeR < 10.0) eyeR = 10.0;
  // we don't allow Phi to get all the way to Pi/2 so that our
  // vertical vector will always be valid.
  if (eyePhi < -1.55) eyePhi = -1.55;
  if (eyePhi > 1.55) eyePhi = 1.55;
  eyeX = eyeR * cos(eyeTheta) * cos(eyePhi);
  eyeY = eyeR * sin(eyeTheta) * cos(eyePhi);
  eyeZ = eyeR * sin(eyePhi);

  glClearColor(0.2, 0.2, 0.2, 1.0);
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  glLoadIdentity();
  glLightfv(GL_LIGHT0, GL_POSITION, lightPosition);

  glEnable(GL_DEPTH_TEST);
        
  gluPerspective(45.0, (float)windowWidth / (float)windowHeight, 10.0, 1000.0);
  gluLookAt(eyeX, eyeY, eyeZ,
            0.0, 0.0, 0.0,
            0.0, 0.0, 1.0);

#define AXISLEN 10.0
  line(0.0, 0.0, 0.0, AXISLEN, 0.0, 0.0, 1.0, 0.0, 0.0); // x axis in red
  line(0.0, 0.0, 0.0, 0.0, AXISLEN, 0.0, 0.0, 1.0, 0.0); // y axis in green
  line(0.0, 0.0, 0.0, 0.0, 0.0, AXISLEN, 0.0, 0.0, 1.0); // z axis in blue

  renderFrame();
  
  //sphere(0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0);
  //sphere(10.0, 0.0, -10.0, 1.0, 1.0, 0.0, 1.0);
  //sphere(0.0, 10.0, 10.0, 1.0, 0.0, 1.0, 1.0);
        
  glFlush();
}

// radians
#define dAngle 0.08

static void
keypress(XEvent *event)
{
  char buffer[20];
  int bufsize = 20;
  KeySym key;
  XComposeStatus compose;
  int charcount;
  int modifiers = event->xkey.state;
  
  charcount = XLookupString((XKeyEvent *)event, buffer, bufsize, &key, &compose);
  
  switch (key) {
  case XK_Left:
    eyeTheta += dAngle;
    break;
  case XK_Right:
    eyeTheta -= dAngle;
    break;
  case XK_Up:
    if (modifiers & 0x01) {
      eyeR--;
    } else {
      eyePhi -= dAngle;
    }
    break;
  case XK_Down:
    if (modifiers & 0x01) {
      eyeR++;
    } else {
      eyePhi += dAngle;
    }
    break;

  case XK_q:
  case XK_Escape:
    exit(0);

  case XK_r:
    resetEye();
    break;

  case XK_comma:
    currentFrame--;
    break;
    
  case XK_period:
    currentFrame++;
    break;
    
  case XK_less:
    currentFrame = 0;
    break;
    
  case XK_greater:
    currentFrame = numFrames - 1;
    break;
    
  default:
    fprintf(stderr, "keypress: 0x%x, 0x%x\n", key, modifiers);
    break;
  }
  repaint();
}

static char stdinBuffer[1024];
static int stdinPosition = 0;

static void
processLine(char *s)
{
  float x1, y1, z1;
  float x2, y2, z2;
  float r, g, b;
  float radius;
  struct Object *o;
  
  movie = (struct Object *)accumulator(movie, sizeof(struct Object) * (numObjects + 1), 0);
  o = &movie[numObjects];
  fprintf(stderr, "line: <<%s>>\n", s);
  if (*s == 's') { // s x y z radius r g b
    if (7 == sscanf(s+1,
                    "%f%f%f%f%f%f%f",
                    &o->sphere.x,
                    &o->sphere.y,
                    &o->sphere.z,
                    &o->sphere.radius,
                    &o->sphere.r,
                    &o->sphere.g,
                    &o->sphere.b))
    {
      o->type = OBJ_SPHERE;
      numObjects++;
    } else {
      fprintf(stderr, "couldn't parse sphere line: <<%s>>\n", s);
    }
  } else if (*s == 'l') {
    if (9 == sscanf(s+1,
                    "%f%f%f%f%f%f%f%f%f",
                    &o->line.x1,
                    &o->line.y1,
                    &o->line.z1,
                    &o->line.x2,
                    &o->line.y2,
                    &o->line.z2,
                    &o->line.r,
                    &o->line.g,
                    &o->line.b))
    {
      o->type = OBJ_LINE;
      numObjects++;
    } else {
      fprintf(stderr, "couldn't parse line line: <<%s>>\n", s);
    }
  } else if (*s == 'f') {
    o->type = OBJ_FRAME;
    numObjects++;
    numFrames++;
    frames = (int *)accumulator(frames, sizeof(int) * numFrames, 0);
    frames[numFrames-1] = startOfLastFrame;
    startOfLastFrame = numObjects;
    if (followLastFrame) {
      currentFrame = numFrames - 1;
      repaint(); // could be smarter about skipping frames if we get a bunch
    }
  }
}


static void
processStdin()
{
  int nread;
  int startOfLine;
  int endOfLine;

  nread = read(0, stdinBuffer+stdinPosition, 1024-stdinPosition);
  if (nread < 0) {
    perror("read stdin");
    return;
  }
  if (nread > 0) {
    stdinPosition += nread;
    startOfLine = 0;
    endOfLine = 0;
    while (endOfLine < stdinPosition) {
      if (stdinBuffer[endOfLine] == '\n') {
        stdinBuffer[endOfLine] = '\0';
        processLine(stdinBuffer+startOfLine);
        startOfLine = endOfLine + 1;
      }
      endOfLine++;
    }
    if (startOfLine < stdinPosition) {
      if (startOfLine > 0) {
        memmove(stdinBuffer, stdinBuffer+startOfLine, stdinPosition - startOfLine);
        stdinPosition -= startOfLine;
      }
    } else {
      stdinPosition = 0;
    }
  }
}

static void
processX()
{
  XEvent event;

  XNextEvent(xDisplay, &event);
  switch (event.type) {

    // the following event type is selected by KeyPressMask
  case KeyPress:
    keypress(&event);
    break;
        
    // the following event type is selected by ExposureMask
  case Expose:
    repaint();
    break;
        
    // the following event types are selected by StructureNotifyMask
  case ConfigureNotify:
    windowWidth = event.xconfigure.width;
    windowHeight = event.xconfigure.height;
    glViewport(0, 0, windowWidth, windowHeight);
    break;
        
  case ReparentNotify:
    break;

  case DestroyNotify:
    exit(0);
        
  case CirculateNotify:
  case GravityNotify:
  case MapNotify:
  case UnmapNotify:

    // the following event types are always selected
  case MappingNotify:
  case ClientMessage:
  case SelectionClear:
  case SelectionNotify:
  case SelectionRequest:
  default:
    fprintf(stderr, "got event type %d\n", event.type);
    break;
  }
}

int main(int argc, char **argv)
{
  XVisualInfo *vi;
  Colormap cmap;
  XSetWindowAttributes swa;
  Window win;
  GLXContext cx;
  XEvent event;
  fd_set readfds;
  int xServerFD;
  int nselected;
    
  /* get a connection */
  xDisplay = XOpenDisplay(0);
  if (xDisplay == NULL) {
    fprintf(stderr, "can't open display\n");
    exit(1);
  }
    
  /* get an appropriate visual */
  vi = glXChooseVisual(xDisplay, DefaultScreen(xDisplay), attributeList);
  if (vi == NULL) {
    fprintf(stderr, "can't get visual\n");
    exit(1);
  }
    
  /* create a GLX context */
  cx = glXCreateContext(xDisplay, vi, 0, GL_FALSE);
  if (cx == NULL) {
    fprintf(stderr, "can't create GL context\n");
    exit(1);
  }
    
  /* create a color map */
  cmap = XCreateColormap(xDisplay, RootWindow(xDisplay, vi->screen), vi->visual, AllocNone);
    
  /* create a window */
  swa.colormap = cmap;
  swa.border_pixel = 0;
  swa.event_mask = StructureNotifyMask;

  windowWidth = 500;
  windowHeight = 500;
    
  win = XCreateWindow(xDisplay, RootWindow(xDisplay, vi->screen), 0, 0, windowWidth, windowHeight,
                      0, vi->depth, InputOutput, vi->visual,
                      CWBorderPixel|CWColormap|CWEventMask, &swa);

  XSelectInput(xDisplay, win, KeyPressMask | ExposureMask | StructureNotifyMask);
    
  XMapWindow(xDisplay, win);
  // wait for the window to be mapped
  XIfEvent(xDisplay, &event, WaitForNotify, (char*)win);
  /* connect the context to the window */
  glXMakeCurrent(xDisplay, win, cx);

  quad = gluNewQuadric();
  if (quad == NULL) {
    fprintf(stderr, "can't allocate quadric\n");
    exit(1);
  }

  resetEye();

  xServerFD = ConnectionNumber(xDisplay);
  XFlush(xDisplay);
  
  while (1) {
    FD_ZERO(&readfds);
    FD_SET(0, &readfds);
    FD_SET(xServerFD, &readfds);
    nselected = select(xServerFD+1, &readfds, NULL, NULL, NULL);
    if (nselected < 0) {
      perror("select");
      continue;
    }
    if (nselected == 0) {
      continue;
    }
    if (FD_ISSET(0, &readfds)) {
      processStdin();
    }
    if (FD_ISSET(xServerFD, &readfds)) {
      processX();
    }
  }
}
