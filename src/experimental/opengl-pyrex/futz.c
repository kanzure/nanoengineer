#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>

#include <GL/glx.h>
#include <GL/gl.h>
#include <GL/glu.h>

// Position of the eye in spherical coordinates
#define EYE_THETA  0.0
#define EYE_PHI  0.0
#define EYE_R  100.0

// Position of the eye in cartesian coordinates
#define EYE_X  (EYE_R * cos(EYE_THETA) * cos(EYE_PHI))
#define EYE_Y  (EYE_R * sin(EYE_THETA) * cos(EYE_PHI))
#define EYE_Z  (EYE_R * sin(EYE_PHI))

static GLUquadric *quad = NULL;

void
glSetup(int windowWidth, int windowHeight)
{
    float lightPosition[4] = { 1.0, 0.5, -0.1, 0.0 };
    glClearColor(0.2, 0.2, 0.2, 1.0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glLoadIdentity();
    glLightfv(GL_LIGHT0, GL_POSITION, lightPosition);

    glEnable(GL_DEPTH_TEST);

    gluPerspective(45.0, (double)windowWidth / (double)windowHeight, EYE_R/10.0, EYE_R*20.0);
    gluLookAt(EYE_X, EYE_Y, EYE_Z,
	      0.0, 0.0, 0.0,
	      0.0, 0.0, 1.0);

    quad = gluNewQuadric();
    if (quad == NULL) {
	perror("can't allocate quadric");
	exit(1);
    }
}


void
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


void
sphere(double x, double y, double z, double radius, double r, double g, double b)
{
    const GLfloat materialColor[4] = {
	r, g, b, 1.0
    };

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
