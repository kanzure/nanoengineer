# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
GLPane.py -- Atom's main model view, based on Qt's OpenGL widget.

BRUCE IS TEMPORARILY OWNING this file (and all mode files) for a few days starting 040922,
in order to fix mode-related bugs by revising the interface between modes.py,
all specific modes, and GLPane.py. During this period, please consult Bruce
before any changes to these files.

$Id$
"""
from qt import *
from qtgl import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLE import *
import math
from LinearAlgebra import *
from commands import *

import os,sys
import time
from VQT import *
import drawer
from shape import *
from assembly import *
import re
from constants import *
from modifyMode import *
from cookieMode import cookieMode # fyi: was 'import *' before bruce 040920
from extrudeMode import extrudeMode
from selectMode import *
from depositMode import *

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

debug_menu_enabled = 1 # enable the undocumented debug menu by default [bruce 040920]
debug_events = 0 # set this to 1 to print info about most mouse events

class GLPane(QGLWidget):
    """Mouse input and graphics output in the main view window.
    """
    def __init__(self, assem, master=None, name=None, win=None):
        QGLWidget.__init__(self,master,name)
        global paneno
        self.name = str(paneno)
        paneno += 1
        self.initialised = 0

        self.mode = 0

        self.debug_menu = self.makemenu( self.debug_menu_items() )

        # The background color
        self.backgroundColor = normalBackground
        self.gridColor = normalGridLines

        self.trackball = Trackball(10,10)
        self.quat = Q(1, 0, 0, 0)

        # Current coordinates of the mouse.
        self.MousePos = V(0,0)

        # the little corner axis icon
        self.drawAxisIcon = 1

        # the toggle button state for Csys
        self.cSysToggleButton = True
 
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
        self.singlet = None

        self.makeCurrent()

        drawer.setup()

        self.win = win

        self.setAssy(assem)

    def setAssy(self, assem):
        assem.o = self
        self.assy = assem

        # set up the interaction mode
        self.modetab={}
        
        selectMode(self)
        cookieMode(self)
        extrudeMode(self)
        modifyMode(self)
        depositMode(self)

        self.setMode('SELECT')

        
    def setMode(self, mode):
        """give the modename as a string.
        """
        self.modetab[mode].setMode()
        self.paintGL()

    # return space vectors corresponding to various directions
    # relative to the screen
    def __getattr__(self, name):
        if name == 'lineOfSight':
            return self.quat.unrot(V(0,0,-1))
        elif name == 'right':
            return self.quat.unrot(V(1,0,0))
        elif name == 'left':
            return self.quat.unrot(V(-1,0,0))
        elif name == 'up':
            return self.quat.unrot(V(0,1,0))
        elif name == 'down':
            return self.quat.unrot(V(0,-1,0))
        elif name == 'out':
            return self.quat.unrot(V(0,0,1))
        else:
            raise AttributeError, 'GLPane has no "%s"' % name


    def initializeGL(self):
        """set up lighting in the model
        """
        self.makeCurrent()
        glEnable(GL_NORMALIZE)
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

    _saved_buttons = 0
    def fix_buttons(self, but, when):
        """Every mouse event's button and modifier key flags should be filtered through this method, which does two things:
           1. Store those flags from a mouse-press, and reuse them on the subsequent mouse-drag and mouse-release events (but not on pure mouse-moves),
             so the caller can just switch on the flags to process the event, and will always call properly paired begin/end routines
             (this matters if the user releases or presses a modifier key during the middle of a drag; it's common to release a mod key then);
           2. On the Mac, remap Option/leftButton to middleButton, so that the Option key (also called the Alt key) simulates the middle mouse button.
           (Note that Qt/Mac, by default, lets Control key simulate rightButton and remaps Command key to the same flag we call cntlButton;
            we like this and don't change it here.)
        """
        # [by bruce, 040917. At time of commit, tested only on Mac with one-button mouse.]
        
        allButtons = (leftButton|midButton|rightButton)
        allModKeys = (shiftButton|cntlButton|altButton)
        allFlags = (allButtons|allModKeys)
        _debug = 0 # set this to 1 to see some debugging messages
        if when == 'move' and (but & allButtons):
            when = 'drag'
        assert when in ['move','press','drag','release']
        
        # 1. bugfix: make mod keys during drag and button-release the same as on the initial button-press.
        # Do the same with mouse buttons, if they change during a single drag (though I hope that will be rare).
        # Do all this before remapping the modkey/mousebutton combinations in part 2 below!
        if when == 'press':
            self._saved_buttons = but & allFlags # we'll reuse this button/modkey state during the same drag and release
            if _debug and self._saved_buttons != but:
                print "fyi, debug: fix_buttons: some event flags unsaved: %d - %d = 0x%x" % (but, self._saved_buttons, but - self._saved_buttons)
                # fyi: on Mac I once got 2050 - 2 = 0x800 from this statement; don't know what flag 0x800 means; shouldn't be a problem
        elif when in ['drag','release']:
            if (self._saved_buttons & allButtons):
                but0 = but
                but &= ~allFlags
                but |= self._saved_buttons # restore the modkeys and mousebuttons from the mousepress
                if _debug and but0 != but:
                    print "fyi, debug: fix_buttons rewrote but0 0x%x to but 0x%x" % (but0, but) #works
            else:
                # fyi: This case might happen in the following rare and weird situation:
                # - the user presses another mousebutton during a drag, then releases the first one, still in the drag;
                # - Qt responds to this by emitting two mouseReleases in a row, one for each released button.
                # (I don't know if it does this; testing it requires a 3-button mouse, but the one I own is unreliable.)
                #
                # In that case, this code might make some sense of this, but it's not worth analyzing exactly what it does for now.
                #
                # If Qt instead suppresses the first mouseRelease until all buttons are up (as I hope), this case never happens;
                # instead the above code pretends the same mouse button was down during the entire drag.
                print "warning: Qt gave us two mouseReleases without a mousePress; ignoring this if we can, but it might cause bugs"
                pass # don't modify 'but'
        else:
            pass # pure move (no mouse buttons down): don't revise the event flags
        if when == 'release':
            self._saved_buttons = 0
        
        # 2. let the Mac's Alt/Option mod key simulate middle mouse button.
        if sys.platform in ['darwin']: ### please try adding your platform here, and tell me whether it breaks anything... see below.
            # As of 040916 this hasn't been tested on other platforms, so I used sys.platform to limit it to the Mac.
            # Note that sys.platform is 'darwin' for my MacPython 2.3 and Fink python 2.3 installs, but might be 'mac' or 'macintosh' or so
            # for some other Macintosh Pythons. When we find out, we should add those to the above list.
            # As for non-Mac platforms, what I think this code would do (if they were added to the above list)
            # is either nothing, or remap some other modifier key (different than Shift or Control) to middleButton.
            # If it does the latter, maybe we'll decide that's good (for users with less than 3 mouse buttons) and document it.
            # -- bruce 040916-17
            if (but & altButton) and (but & leftButton):
                but = but - altButton - leftButton + midButton
        return but

    def mouseDoubleClickEvent(self, event):
        self.debug_event(event, 'mouseDoubleClickEvent')
        but = event.stateAfter()
        but = self.fix_buttons(but, 'press') #k I'm guessing this event comes in place of a mousePressEvent; test this [bruce 040917]
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
        if self.debug_event(event, 'mousePressEvent', permit_debug_menu_popup = 1):
            return
        but = event.stateAfter()
        but = self.fix_buttons(but, 'press')
        
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
        self.debug_event(event, 'mouseReleaseEvent')
        but = event.state()
        but = self.fix_buttons(but, 'release')
        
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
        ##self.debug_event(event, 'mouseMoveEvent')
        but = event.state()
        but = self.fix_buttons(but, 'move')

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
        self.debug_event(event, 'wheelEvent')
        self.mode.Wheel(event)
        
    def mousepoints(self,event):
        """Returns a pair (tuple) of points (arrays) that lie under
        the mouse pointer at (just beyond) the near clipping plane
        and in the plane of the center of view.
        """
        x = event.pos().x()
        y = self.height - event.pos().y()

        p1 = A(gluUnProject(x, y, 0.0))
        p2 = A(gluUnProject(x, y, 1.0))

        los = self.lineOfSight
        
        k = dot(los, -self.pov - p1) / dot(los, p2 - p1)

        p2 = p1 + k*(p2-p1)
        p1 = A(gluUnProject(x, y, 0.01))
        return (p1, p2)

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

    def setDisplay(self, disp):
        for mol in self.assy.molecules:
            if mol.display == diDEFAULT: mol.changeapp()
        self.display = disp
            

    def paintGL(self):
        """the main screen-drawing function.
        Sets up point of view projection, position, angle.
        Calls draw member fns for everything in the screen.
        """
        if not self.initialised: return

        ##start=time.time()
     
        c=self.mode.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

	aspect = (self.width + 0.0)/(self.height + 0.0)
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
        self.width = width
        self.height = height
        
	glViewport(0, 0, self.width, self.height)
        
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
        if not filename: return

        width = self.width
        height = self.height
        if filename[-3:] == "pov": self.povwrite(filename, width, height)
        else:  self.jpgwrite(filename, width, height)

    def povwrite(self, filename, width, height):

        aspect = (width*1.0)/(height*1.0)
            
        f=open(filename,"w")
        f.write(povheader)

        f.write("background { color rgb " +
                povpoint(self.mode.backgroundColor*V(1,1,-1)) +
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

    def minimize(self):
        self.assy.writemmp("minimize.mmp")
        s = getoutput("simulator -m minimize.mmp")
        if s[:8] != "Minimize":
            QMessageBox.warning(self, "Minimization Failed:", s)
        else:
            self.startmovie("minimize.dpb")


    def startmovie(self,filename):
        self.assy.movsetup()
        self.xfile=open(filename,'rb')
        self.clock = unpack('i',self.xfile.read(4))[0]
        self.startTimer(30)

    def timerEvent(self, e):
        self.clock -= 1
        if self.clock<0:
            self.killTimers()
            self.assy.movend()
        else:
            self.assy.movatoms(self.xfile)
            self.paintGL()

    def __str__(self):
        return "<GLPane " + self.name + ">"

    def makemenu(self, lis): #bruce 040909-16 moved this method from basicMode to GLPane, leaving a delegator for it in basicMode.
        "make and return a reusable popup menu from lis, which gives pairs of command names and callables"
        win = self
        menu = QPopupMenu(win)
        for m in lis:
            if m:
                act = QAction(win,m[0]+'Action')
                act.setText(win.trUtf8(m[0]))
                act.setMenuText(win.trUtf8(m[0]))
                act.addTo(menu)
                win.connect(act, SIGNAL("activated()"), m[1])
            else:
                menu.insertSeparator()
        return menu

    def debug_menu_items(self):
        return [
            ('print self', self._debug_printself),
            # None, # separator
            ('run py code', self._debug_runpycode),
         ]

    def debug_event(self, event, funcname, permit_debug_menu_popup = 0):
        """Debugging method -- no effect on normal users.
           Does two things -- if a global flag is set, prints info about the event;
           if a certain modifier key combination is pressed, and if caller passed permit_debug_menu_popup = 1,
           puts up an undocumented debugging menu, and returns 1 to caller.
           As of 040916, the debug menu is put up by Shift-Option-Command-click on the Mac,
           and for other OS's I predict it either never happens or happens only for some similar set of 3 modifier keys.
           -- bruce 040916
        """
        # in constants.py: debugButtons = cntlButton | shiftButton | altButton # on the mac, this really means command-shift-alt
        if debug_menu_enabled and permit_debug_menu_popup and ((event.state() & debugButtons) == debugButtons):
            print "\n* * * fyi: got debug click, will try to put up a debug menu...\n"
            self.do_debug_menu(event)
            return 1 # caller should detect this and not run its usual event code...
        if debug_events:
            try:
                after = event.stateAfter()
            except:
                after = "<no stateAfter>" # needed for Wheel events, at least
            print "%s: event; state = %r, stateAfter = %r; time = %r" % (funcname, event.state(), after, time.asctime())
        # It seems, from doc and experiments, that event.state() is from just before the event (e.g. a button press or release, or move),
        # and event.stateAfter() is from just after it, so they differ in one bit which is the button whose state changed (if any).
        # But the doc is vague, and the experiments incomplete, so there is no guarantee that they don't sometimes differ in other ways.
        # -- bruce ca. 040916
        return 0

    def do_debug_menu(self, event):
        menu = self.debug_menu
        self.current_event = event
        # this code written from Qt/PyQt docs... note that some Atom modules use menu.exec_loop() but others use menu.popup();
        # I don't know for sure whether this matters here, or which is best. -- bruce ca. 040916
        menu.exec_loop(event.globalPos(), 1)
        self.current_event = None
        return 1

    def _debug_printself(self):
        print self

    def _debug_runpycode(self):
        title = "debug: run py code"
        label = "one line of python to exec in GLPane.py's globals()\n(or use @@@ to fake \\n for more lines)\n(or use execfile)"
        text, ok = QInputDialog.getText(title, label)
        if ok:
            # fyi: type(text) == <class '__main__.qt.QString'>
            command = str(text) #k not yet well tested
            command = command.replace("@@@",'\n')
            debug_run_command(command, source = "debug menu")
        else:
            print "run py code: cancelled"
        return

    pass # end of class GLPane

def debug_run_command(command, source = "user debug input"): #bruce 040913-16 #e move this to somewhere more general?
    """Execute a python command, supplied by the user via some sort of debugging interface (named by source),
       in GLPane.py's globals. Return 1 for ok (incl empty command), 0 for any error.
       Caller should not print diagnostics -- this function should be extended to do that, though it doesn't yet.
    """
    #e someday we might record time, history, etc
    command = "" + command # i.e. assert it's a string
    #k what's a better way to do the following?
    while command and command[0] == '\n':
        command = command[1:]
    while command and command[-1] == '\n':
        command = command[:-1]
    if not command:
        print "empty command (from %s), nothing executed" % (source,)
        return
    if '\n' not in command:
        print "will execute (from %s): %s" % (source, command)
    else:
        nlines = command.count('\n')+1
        print "will execute (from %s; %d lines):\n%s" % (source, nlines, command)
    command = command + '\n' #k probably not needed
    try:
        exec command in globals()
    except:
        print "exception from that, discarded (sorry)" #e should print compact traceback
    else:
        print "did it!"
    return

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
