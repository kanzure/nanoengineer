from qt import *
from qtgl import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLE import *
import math

import os,sys
from time import time
from VQT import *
import drawer
from shape import *
from assembly import *
import re
from constants import *
from modes import *

import Image
import operator
import struct
from povheader import povheader

paneno = 0
#  ... what a Pane ...

normalBackground = 217/256.0, 214/256.0, 160/256.0

normalGridLines = (0.0, 0.0, 0.6)

pi2 = pi/2.0
pi3 = pi/3.0
pi4 = pi/4.0
xquats = [Q(1,0,0,0), Q(V(0,0,1),pi2), Q(V(0,0,1),pi), Q(V(0,0,1),-pi2),
          Q(V(0,0,1),pi4), Q(V(0,0,1),3*pi4),
          Q(V(0,0,1),-pi4), Q(V(0,0,1),-3*pi4)]
pquats = [Q(1,0,0,0), Q(V(0,1,0),pi2), Q(V(0,1,0),pi), Q(V(0,1,0),-pi2), 
          Q(V(1,0,0),pi2), Q(V(1,0,0),-pi2)]

quats100 = []
for q in pquats:
    for q1 in xquats:
        quats100 += [q+q1]

rq = Q(V(0,1,0),pi2)
pquats = [Q(V(0,1,0),pi4), Q(V(0,1,0),3*pi4),
          Q(V(0,1,0),-pi4), Q(V(0,1,0),-3*pi4),
          Q(V(1,0,0),pi4), Q(V(1,0,0),3*pi4),
          Q(V(1,0,0),-pi4), Q(V(1,0,0),-3*pi4),
          rq+Q(V(1,0,0),pi4), rq+Q(V(1,0,0),3*pi4),
          rq+Q(V(1,0,0),-pi4), rq+Q(V(1,0,0),-3*pi4)]

quats110 = []
for q in pquats:
    for q1 in xquats:
        quats110 += [q+q1]

cq = Q(V(1,0,0),0.615479708)
xquats = [Q(1,0,0,0), Q(V(0,0,1),pi3), Q(V(0,0,1),2*pi3), Q(V(0,0,1),pi),
          Q(V(0,0,1),-pi3), Q(V(0,0,1),-2*pi3)]
pquats = [Q(V(0,1,0),pi4), Q(V(0,1,0),3*pi4),
          Q(V(0,1,0),-pi4), Q(V(0,1,0),-3*pi4)]

quats111 = []
for q in pquats:
    for q1 in xquats:
        quats111 += [q+cq+q1, q-cq+q1]

allQuats = quats100 + quats110 + quats111

class GLPane(QGLWidget):
    """Mouse input and graphics output in the main view window.
    """

    def __init__(self, assem, master=None, name=None, form1=None):
        QGLWidget.__init__(self,master,name)
        global paneno
        self.name = str(paneno)
        paneno += 1
        self.initialised = 0
        self.assy = assem
        self.mode = 0
        

        # The background color
        self.backgroundColor = normalBackground
        self.gridColor = normalGridLines

        self.trackball = Trackball(10,10)
        self.quat = Q(1, 0, 0, 0)

        # Current coordinates of the mouse.
        self.MousePos = V(0,0)

        # the little corner axis icon
        self.drawAxisIcon = 1

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

        # 1 for selecting, 0 for deselecting, 2 for selecting parts
        self.selSense = 1
        # 0 if selecting as lasso, 1 if as rectangle
        self.selLassRect = 1

        self.picking = False

        self.setMouseTracking(True)

        # default display form for objects in the window
        # even tho there is only one assembly to a window,
        # this is here in anticipation of being able to have
        # multiple windows on the same assembly
        self.display = diVDW

        self.makeCurrent()

        drawer.setup()

        self.scm = form1.selectMenu
        self.form1 = form1

        # set up the interaction mode
        self.modetab={}
        
        selectMode(self)
        cookieMode(self)
        modifyMode(self)

        self.setMode('SELECT')

        
    def setMode(self, mode):
        """give the modename as a string.
        """
        self.modetab[mode].setMode()
        self.paintGL()

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

    def mouseDoubleClickEvent(self, event):
        but = event.stateAfter()
        if but & leftButton:
            self.mode.leftDouble(event)
        if but & midButton:
            self.mode.middleDouble(event)
        if but & rightButton:
            self.mode.rightDouble(event)

    def mousePressEvent(self, event):
        """Dispatches mouse press events depending on shift and
        control key state.
        """
        but = event.stateAfter()
        
        if but & leftButton:
            if but & shiftButton:
                self.mode.leftShiftDown(event)
            elif but & cntlButton:
                self.mode.leftCntlDown(event)
            else:
                self.mode.leftDown(event)

        if but & midButton:
            if but & shiftButton:
                self.mode.middleShiftDown(event)
            elif but & cntlButton:
                self.mode.middleCntlDown(event)
            else:
                self.mode.middleDown(event)

        if but & rightButton:
            if but & shiftButton:
                self.mode.rightShiftDown(event)
            elif but & cntlButton:
                self.mode.rightCntlDown(event)
            else:
                self.mode.rightDown(event)         

    def mouseReleaseEvent(self, event):
        """Only used to detect the end of a freehand selection curve.
        """
        but = event.state()
        
        if but & leftButton:
            if but & shiftButton:
                self.mode.leftShiftUp(event)
            elif but & cntlButton:
                self.mode.leftCntlUp(event)
            else:
                self.mode.leftUp(event)

        if but & midButton:
            if but & shiftButton:
                self.mode.middleShiftUp(event)
            elif but & cntlButton:
                self.mode.middleCntlUp(event)
            else:
                self.mode.middleUp(event)

        if but & rightButton:
            if but & shiftButton:
                self.mode.rightShiftUp(event)
            elif but & cntlButton:
                self.mode.rightCntlUp(event)
            else:
                self.mode.rightUp(event)         


    def mouseMoveEvent(self, event):
        """Dispatches mouse motion events depending on shift and
        control key state.
        """
        but = event.state()

        if but & leftButton:
            if but & shiftButton:
                self.mode.leftShiftDrag(event)
            elif but & cntlButton:
                self.mode.leftCntlDrag(event)
            else:
                self.mode.leftDrag(event)

        elif but & midButton:
            if but & shiftButton:
                self.mode.middleShiftDrag(event)
            elif but & cntlButton:
                self.mode.middleCntlDrag(event)
            else:
                self.mode.middleDrag(event)

        elif but & rightButton:
            if but & shiftButton:
                self.mode.rightShiftDrag(event)
            elif but & cntlButton:
                self.mode.rightCntlDrag(event)
            else:
                self.mode.rightDrag(event)

        else:
            self.mode.bareMotion(event)

    def wheelEvent(self, event):
        self.mode.Wheel(event)
        
    def mousepoints(self,event):
        """Returns a pair (tuple) of points (arrays) that lie under
        the mouse pointer at the near and far clipping planes.
        """
        x = event.pos().x()
        y = self.height - event.pos().y()

        p1 = A(gluUnProject(x, y, 0.0))
        p2 = A(gluUnProject(x, y, 1.0))
        
        k = (dot(self.lineOfSight,  (- self.pov) - p1) /
             dot(self.lineOfSight, p2 - p1))

        p1 = A(gluUnProject(x, y, 0.01))
        p2 = p1 + k*(p2-p1)
        return (p1, p2)


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

    def SaveMouse(self, event):
        """Extracts mouse position from event and saves it.
        (localizes the API-specific code for extracting the info)
        """
        self.MousePos = V(event.pos().x(), event.pos().y())

    def snapquat100(self):
        self.snapquat(quats100)

    def snapquat110(self):
        self.snapquat(quats110)

    def snapquat111(self):
        self.snapquat(quats111)

    def snap2trackball(self):
        self.snapquat(allQuats)

    def snapquat(self, qlist):
        q1 = self.quat
        a=1.1
        for q2 in qlist:
            a2 = vlen((q2-q1).axis)
            if a2 < a:
                a = a2
                q = q2
        self.quat = Q(q)
        self.paintGL()
            

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
        c=self.mode.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if self.drawAxisIcon: self.drawarrow(aspect)
        
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

        glTranslatef(0.0, 0.0, - vdist)

        q = self.quat
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)

        glTranslatef(self.pov[0], self.pov[1], self.pov[2])

        # draw according to mode
        self.mode.Draw()
        glFlush()                           # Tidy up
        self.swapBuffers()

    def drawarrow(self, aspect):
        glOrtho(-50*aspect, 5*aspect, -50, 5,  -5, 500)
        q = self.quat
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)
        glEnable(GL_COLOR_MATERIAL)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDisable(GL_CULL_FACE)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glePolyCone([[-1,0,0], [0,0,0], [4,0,0], [3,0,0], [5,0,0], [6,0,0]],
                    [[0,0,0], [1,1,1], [0,1,0], [1,0,0], [1,0,0], [0,0,0]],
                    [.3,.3,.3,1,0,0])
        glePolyCone([[0,-1,0], [0,0,0], [0,4,0], [0,3,0], [0,5,0], [0,6,0]],
                    [[0,0,0], [1,1,1], [1,0,0], [0,0,1], [0,0,1], [0,0,0]],
                    [.3,.3,.3,1,0,0])
        glePolyCone([[0,0,-1], [0,0,0], [0,0,4], [0,0,3], [0,0,5], [0,0,6]],
                    [[0,0,0], [1,1,1], [0,0,1], [0,1,0], [0,1,0], [0,0,0]],
                    [.3,.3,.3,1,0,0])
        glEnable(GL_CULL_FACE)
        glDisable(GL_COLOR_MATERIAL)
        glLoadIdentity()


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

    #################
        # UI fns
    #################

    # functions from the "Display" menu

    # this will pop up a new window onto the same assembly
    def dispNewView(self):
        foo = Form1()
        foo.assy = foo.glpane.assy = self.assy
        foo.assy.windows += [foo]
        foo.glpane.scale=1.5*max(foo.assy.bboxhi[0], foo.assy.bboxhi[1])
        for mol in foo.glpane.assy.molecules:
            mol.changeapp()
        foo.show()
        self.assy.updateDisplays()
	

    # GLPane.ortho is checked in GLPane.paintGL
    def dispOrtho(self):
        self.ortho = 1
        self.paintGL()

    def dispPerspec(self):
        self.ortho = 0
        self.paintGL()

    # set display formats in whatever is selected,
    # or the GLPane global default if nothing is
    def dispDefault(self):
        self.setdisplay(diDEFAULT)

    def dispInvis(self):
        self.setdisplay(diINVISIBLE)

    def dispVdW(self):
        self.setdisplay(diVDW)

    def dispCPK(self):
        self.setdisplay(diCPK)

    def dispTubes(self):
        self.setdisplay(diTUBES)

    def dispLines(self):
        self.setdisplay(diLINES)

    def setdisplay(self, form):
        if self.assy.selatoms:
            for ob in self.assy.selatoms.itervalues():
                ob.display = form
                ob.molecule.changeapp()
            self.assy.updateDisplays()
        elif self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.display = form
                ob.changeapp()
            self.assy.updateDisplays()
        else:
            if self.display == form: return
            self.display = form
            for ob in self.assy.molecules:
                if ob.display == diDEFAULT:
                    ob.changeapp()
            self.paintGL()
        

    # set the color of the selected part(s) (molecule)
    # or the background color if no part is selected.
    # atom colors cannot be changed singly
    def dispColor(self):
        c = self.colorchoose()
        if self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.setcolor(c)
            self.assy.updateDisplays()
        else: self.mode.backgroundColor = c
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


def rectgrid(o):
    """Assigned as griddraw for a rectangular grid that is always parallel
    to the screen.
    """
    drawer.drawaxes(5,-o.pov)
    glColor3fv(self.gridColor)
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
