from qt import *
from qtgl import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from math import asin

import os,sys
from time import time
from VQT import *
import drawer
from shape import *
from assembly import *
import re
from constants import *

import Image
import operator
import struct
from povheader import povheader

paneno = 0
#  ... what a Pane ...

class GLPane(QGLWidget):
    """Mouse input and graphics output in the main view window.
    """

    def __init__(self, assem, master=None, name=None):
        QGLWidget.__init__(self,master,name)
        global paneno
        self.name = str(paneno)
        paneno += 1
        self.initialised = 0
        self.assy = assem
        self.mode = 0
        

        # The background color
        self.backgroundColor = 34/256.0, 148/256.0, 137/256.0

        self.trackball = Trackball(10,10)
        self.quat = Q(1, 0, 0, 0)

        # Current coordinates of the mouse.
        self.MousePos = V(0,0)

        # point of view, and half-height of window in Angstroms
        self.pov = V(0.0, 0.0, 0.0)
        self.scale = 10.0

        # clipping planes, as percentage of distance from the eye
        self.near = 0.66
        self.far = 2.0

        # start in perspective mode
        self.ortho = 0

        # not selecting anything currently
        self.sellist = None
        self.shape = None

        self.picking = False

        # default display form for objects in the window
        # even tho there is only one assembly to a window,
        # this is here in anticipation of being able to have
        # multiple windows on the same assembly
        self.display = diVDW

        self.makeCurrent()

        drawer.setup()

    # return space vectors corresponding to various directions
    # relative to the screen
    def __getattr__(self, name):
        if name in ('lineOfSight', 'in'):
            return dot(V(0,0,-1), self.quat.matrix3)
        elif name == 'right':
            return dot(V(1,0,0), self.quat.matrix3)
        elif name == 'left':
            return dot(V(-1,0,0), self.quat.matrix3)
        elif name == 'up':
            return dot(V(0,1,0), self.quat.matrix3)
        elif name == 'down':
            return dot(V(0,-1,0), self.quat.matrix3)
        elif name in 'out':
            return dot(V(0,0,1), self.quat.matrix3)
        else:
            raise AttributeError, 'GLPane has no "%s"' % name


    def initializeGL(self):
        """set up lighting in the model
        """
        self.makeCurrent()
        glLightfv(GL_LIGHT0, GL_POSITION, (-50, 70, 30, 0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        glLightfv(GL_LIGHT1, GL_POSITION, (-20, 20, 20, 0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.4, 0.4, 0.4, 1.0))
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
        glLightfv(GL_LIGHT2, GL_POSITION, (0, 0, 100, 0))
        glLightfv(GL_LIGHT2, GL_AMBIENT, (1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glDisable(GL_LIGHT2)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def mousePressEvent(self, e):
        """Dispatches mouse press events depending on shift and
        control key state.
        """
        but = e.stateAfter()
        if but & shiftButton:
            if but & leftButton: self.StartPick(e)
            if but & rightButton: self.SelAtom(e)
            if but & midButton: self.SelPart(e)
        elif but & cntlButton:
            if but & leftButton: self.StartSelRot(e)
            if but & rightButton: self.SaveMouse(e)
            if but & midButton: self.SaveMouse(e)
        else:
            if but & leftButton: self.StartRotate(e)
            if but & rightButton: self.SaveMouse(e)
            if but & midButton: self.SaveMouse(e)

    def mouseReleaseEvent(self, e):
        """Only used to detect the end of a freehand selection curve.
        """
        if self.picking:
            self.picking = False
            self.EndPick(e)

    def mouseMoveEvent(self, e):
        """Dispatches mouse motion events depending on shift and
        control key state.
        """
        but = e.state()
        if but & shiftButton:
            if but & leftButton: self.ContinPick(e)
        elif but & cntlButton:
            if but & leftButton: self.SelRotate(e)
            if but & rightButton: self.SelVert(e)
            if but & midButton: self.SelHoriz(e)
        else:
            if but & leftButton: self.Rotate(e)
            if but & rightButton: self.Pan(e)
            if but & midButton: self.Zoom(e)

    def mousepoints(self,event):
        """Returns a pair (tuple) of points (arrays) that lie under
        the mouse pointer at the near and far clipping planes.
        """
        x = event.pos().x()
        y = self.height - event.pos().y()

        p1 = A(gluUnProject(x, y, 0.))
        p2 = A(gluUnProject(x, y, 1.))
        return (p1, p2)

    def StartPick(self, event):
        """Start a selection curve
        """
        self.picking = 1
        self.SaveMouse(event)
        self.prevvec = None
        self.totangle = 0.0

        (p1, p2) = self.mousepoints(event)
        startpiecepick(self, p1, p2)


    def ContinPick(self, event):
        """Add another segment to a selection curve
        """
        x = event.pos().x()
        y = self.height - event.pos().y()

        # sum the differences in heading angles to tell handedness of curve
        xy = V(x, y)
        oxy = V(self.MousePos[0], self.height-self.MousePos[1])
        nuvec = norm(xy-oxy)
        if self.prevvec:
            # note this is wrong if angle is sharper than pi/2
            self.totangle += asin(dot(nuvec,V(-self.prevvec[1],self.prevvec[0])))
        self.prevvec = nuvec
        (p1, p2) = self.mousepoints(event)
        piecepick(self, p1, p2)
        self.assy.updateDisplays()

    def EndPick(self, event):
        """Close a selection curve and do the selection
        """

        (p1, p2) = self.mousepoints(event)

        pieceendpick(self, p1, p2)
        self.assy.updateDisplays()


    def SelPart(self, event):
        """Select the part containing the atom the cursor is on.
        """
        (p1, p2) = self.mousepoints(event)

        self.assy.pickpart(p1,norm(p2-p1))

        self.assy.updateDisplays()

    def SelAtom(self, event):
        """Select the atom the cursor is on.
        """
        (p1, p2) = self.mousepoints(event)

        self.assy.pickatom(p1,norm(p2-p1))

        self.assy.updateDisplays()

    def StartSelRot(self, event):
        """Setup a trackball action on each selected part.
        """
        self.SaveMouse(event)
        self.trackball.start(self.MousePos[0],self.MousePos[1])

    def SelRotate(self, event):
        """Do an incremental trackball action on each selected part.
        """
        self.SaveMouse(event)
        q = self.trackball.update(self.MousePos[0],self.MousePos[1], self.quat)
        self.assy.rotsel(q)
        self.assy.updateDisplays()

    def SelHoriz(self, event):
        """Move the selected object(s) on an imaginary tabletop
        following the mouse as if you'd pushed the screen over backwards.
        """
        w=self.width+0.0
        h=self.height+0.0
        deltaMouse = V(event.pos().x() - self.MousePos[0], 0.0, event.pos().y() - self.MousePos[1])
        move = self.scale * deltaMouse/(h*0.5)
        move = dot(move, self.quat.matrix3)
        self.assy.movesel(move)
        self.assy.updateDisplays()
        self.SaveMouse(event)

    def SelVert(self, event):
        """Move the selected object(s) in the plane of the screen following
        the mouse.
        """
        w=self.width+0.0
        h=self.height+0.0
        deltaMouse = V(event.pos().x() - self.MousePos[0], self.MousePos[1] - event.pos().y(), 0.0)
        move = self.scale * deltaMouse/(h*0.5)
        move = dot(move, self.quat.matrix3)
        self.assy.movesel(move)
        self.assy.updateDisplays()
        self.SaveMouse(event)


    def SaveMouse(self, event):
        """Extracts mouse position from event and saves it.
        (localizes the API-specific code for extracting the info)
        """
        self.MousePos = V(event.pos().x(), event.pos().y())


    def StartRotate(self, event):
        """Initialize the screen (point of view) trackball.
        """
        self.SaveMouse(event)
        self.trackball.start(self.MousePos[0],self.MousePos[1])

    def Rotate(self, event):
        """Incremental virtual trackball motion (point of view)
        """
        self.SaveMouse(event)
        q = self.trackball.update(self.MousePos[0],self.MousePos[1])
        self.quat += q 
        self.paintGL()


    def zpush(self, dist):
        """Helper dunction for Zoom
        """
        dist = dot(V(0, 0, dist), self.quat.matrix3)
        self.pov -= dist


    def Zoom(self, event):
        """push scene away (mouse goes up) or pull (down)
           widen field of view (right) or narrow (left)

        """
        h=self.height+0.0
        w=self.width+0.0
        dist = self.scale * 2.0 * (self.MousePos[1]+0.0-event.pos().y())/h
        self.zpush(dist)
        swell = 1.0 + (event.pos().x()-self.MousePos[0]+0.0)/w
        self.scale *= swell
        self.paintGL()
        self.SaveMouse(event)

    def Pan(self, event):
        """Move point of view so that objects appear to follow
        the mouse on the screen.
        """
        w=self.width+0.0 
        h=self.height+0.0
        deltaMouse = V(event.pos().x() - self.MousePos[0], self.MousePos[1] - event.pos().y(), 0.0)
        move = self.scale * deltaMouse/(h*0.5)
        move = dot(move, self.quat.matrix3)
        self.pov += move
        self.paintGL()
        self.SaveMouse(event)

    def paintGL(self):
        """the main screen-drawing function.
        Sets up point of view projection, position, angle.
        Calls draw member fns for everything in the screen.
        """
        if not self.initialised: return

        start=time()
        self.makeCurrent()

        w=self.width
        h=self.height
        aspect = (w+0.0)/(h+0.0)
        glViewport(0, 0, w, h)
        c=self.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        vdist = 6.0 * self.scale
        if self.ortho:
            glOrtho(-self.scale*aspect, self.scale*aspect,
                    -self.scale, self.scale,
                    vdist*self.near, vdist*self.far)
        else:
            glFrustum(-self.scale*aspect*self.near, self.scale*aspect*self.near,
                      -self.scale*self.near, self.scale*self.near,
                      vdist*self.near, vdist*self.far)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, - vdist)

        q = self.quat
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)

        glTranslatef(self.pov[0], self.pov[1], self.pov[2])

        self.griddraw(self)
        if self.sellist: self.pickdraw(self)
        if self.shape and self.mode: self.shape.draw(self)
        if self.assy: self.assy.draw(self)
        glFlush()                           # Tidy up
        self.swapBuffers()

    def griddraw(self, *dummy):
        """This finction is replaced with whatever grid-drawing
        function is appropriate to the current mode.
        """
        drawer.drawaxes(5,-self.pov)

    def pickdraw(self, *dummy):
        """Draw the (possibly unfinished) freehand selection curve.
        """
        pl = zip(self.sellist[:-1],self.sellist[1:])
        if self.totangle<0:
            for pp in pl:
                drawer.drawline((0.0,0.0,1.0),pp[0],(0.0,0.0,1.0),pp[1])
        else:
            for pp in pl:
                drawer.drawline((1.0,0.0,0.0),pp[0],(1.0,0.0,0.0),pp[1])


    def resizeGL(self, width, height):
        """Called by QtGL when the drawing window is resized.
        """
        self.makeCurrent()
        self.width = width
        self.height = height
        if not self.initialised:
            self.initialised = 1
        self.trackball.rescale(width, height)
        self.paintGL()

    def xdump(self):
        """for debugging"""
        print " pov: ", self.pov
        print " quat ", self.quat

    def image(self, filename):
        """saves an image of the screen to file filename
        width and height default to current size
        (and only that works currently)
        """
        width = self.width
        height = self.height
        if filename[-3:] == "pov": self.povwrite(filename, width, height)
        else:  self.jpgwrite(filename, width, height)

    def povwrite(self, filename, width, height):

        aspect = (width*1.0)/(height*1.0)
            
        f=open(filename,"w")
        f.write(povheader)

        f.write("background { color rgb " +
                povpoint(self.backgroundColor*V(1,1,-1)) +
                "}\n")

        light1 = self.out + self.left + self.up
        light2 = self.right + self.up
        light3 = self.right + self.down + self.out/2.0
        f.write("light_source {" + povpoint(light1) +
                " color Gray50 parallel}\n")
        f.write("light_source {" + povpoint(light2) +
                " color Gray25 parallel}\n")
        f.write("light_source {" + povpoint(light3) +
                " color Gray25 parallel}\n")
        

        f.write("camera {\n location " +
                povpoint(3.0*self.scale*self.out-self.pov) +
                "\nup " + povpoint(0.7 * self.up) +
                "\nright " + povpoint(0.7 * aspect*self.right) +
                "\nsky " + povpoint(self.up) +
                "\nlook_at " + povpoint(-self.pov) +
                "\n}\n")
        
        self.assy.povwrite(f, self)

        f.close()
        print "povray +P +W" + str(width) + " +H" +str(height)  + " +A " + filename
    def jpgwrite(self, filename, width, height):

        buf = array(glReadPixelsub(0, 0, width, height, GL_RGB))
        buf = reshape(buf, (height, width, 3))
        
        buf = reshape(buf[::-1],(width*height,3))

        buf = map(lambda x: struct.unpack("BBB", x), buf)

        pic = Image.new("RGB", (width, height))
        pic.putdata(buf)
        pic.save(filename, "JPEG", quality=85)

    def startmovie(self,filename):
        self.xfile=open(filename,'rb')
        self.clock = unpack('i',self.xfile.read(4))[0]
        self.startTimer(30)

    def timerEvent(self, e):
        self.clock -= 1
        if self.clock<0: self.killTimers()
        else:
            self.assy.movatoms(self.xfile)
            self.assy.updateDisplays()

    def __str__(self):
        return "<GLPane " + self.name + ">"


def povpoint(p):
    # note z reversal -- povray is left-handed
    return "<" + str(p[0]) + "," + str(p[1]) + "," + str(-p[2]) + ">"

def pppoint(o,p1,p2):
    """Return the point where the segment from p1 to p2 intersects
    the plane through the center of view parallel to the screen.
    """
    k = dot(o.normal,  - o.pov - p2) / dot(o.normal, p1 - p2)
    return k*p1 + (1-k)*p2

def startpiecepick(o,p1,p2):
    """Set up the screen normal vector and initalize the
    point list for a freehand selection curve.
    """
    o.normal = dot(V(0, 0, 1), o.quat.matrix3)
    o.sellist = [pppoint(o,p1,p2)]

def piecepick(o,p1,p2):
    """Add a point to a selection curve.
    """
    p = pppoint(o,p1,p2)
    o.sellist += [p]

def pieceendpick(o,p1,p2):
    """Close the selection curve (by adding the first point to the end).
    If cookie-cutting, add the curve to the shape (creating the shape
    if this is the first curve). Otherwise, select or unselect immediately
    (selection curves are not accumulated).
    """
    piecepick(o,p1,p2)
    o.sellist += [o.sellist[0]]
    if o.mode:
        if not o.shape: o.shape=shape(o.sellist, -o.pov, o.normal, o.totangle)
        else: o.shape.pickline(o.sellist, -o.pov, o.normal, o.totangle)
    else:
        o.shape=shape(o.sellist, -o.pov, o.normal, o.totangle)
        if o.assy: o.shape.select(o.assy)
    o.sellist = []


def nogrid(o):
    """Assigned as griddraw for no grid (only draws point-of-view axes)
    """
    drawer.drawaxes(5,-o.pov)

def rectgrid(o):
    """Assigned as griddraw for a rectangular grid that is always parallel
    to the screen.
    """
    drawer.drawaxes(5,-o.pov)
    glColor3f(0.5, 0.5, 1.0)
    n=int(ceil(1.5*o.scale))
    # the grid is in eyespace
    glPushMatrix()
    q = o.quat
    glTranslatef(-o.pov[0], -o.pov[1], -o.pov[2])
    glRotatef(- q.angle*180.0/pi, q.x, q.y, q.z)
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    for x in range(-n, n+1):
        glVertex(x,n,0)
        glVertex(x,-n,0)
        glVertex(n,x,0)
        glVertex(-n,x,0)
    glEnd()
    glEnable(GL_LIGHTING)
    glPopMatrix()

def diamondgrid(o):
    """Assigned as griddraw for a diamond lattice grid that is fixed in
    space but cut out into a slab one nanometer thick parallel to the screen
    (and is equivalent to what the cookie-cutter will cut).
    """
    # the grid is in modelspace but the clipping planes are in eyespace
    glPushMatrix()
    q = o.quat
    glTranslatef(-o.pov[0], -o.pov[1], -o.pov[2])
    glRotatef(- q.angle*180.0/pi, q.x, q.y, q.z)
    glClipPlane(GL_CLIP_PLANE0, (0.0, 0.0, -1.0, 2.7))
    glClipPlane(GL_CLIP_PLANE1, (0.0, 0.0, 1.0, 3.7))
    glEnable(GL_CLIP_PLANE0)
    glEnable(GL_CLIP_PLANE1)
    glPopMatrix()
    drawer.drawgrid(1.5*o.scale)
    glDisable(GL_CLIP_PLANE0)
    glDisable(GL_CLIP_PLANE1)
    drawer.drawaxes(5,-o.pov)
