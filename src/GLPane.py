# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
GLPane.py -- Atom's main model view, based on Qt's OpenGL widget.

Mostly written by Josh; partly revised by Bruce for mode code revision, 040922-24.
Revised by many other developers since then (and perhaps before).

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

from modifyMode import modifyMode
# fyi: was 'import *' before bruce 040920; same with other modes here, 040922
from cookieMode import cookieMode 
from extrudeMode import extrudeMode, revolveMode
from selectMode import *
from depositMode import depositMode
from movieMode import movieMode
from zoomMode import zoomMode
from modes import modeMixin

import Image
import operator
import struct
from povheader import povheader

from fileIO import *
from HistoryWidget import greenmsg, redmsg
from platform import fix_buttons_helper
from widgets import makemenu_helper
from debug import DebugMenuMixin

paneno = 0
#  ... what a Pane ...

normalBackground = 216/255.0, 213/255.0, 159/255.0

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
        quats100 += [(q+q1, 0)]

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
        quats110 += [(q+q1, 1)]

cq = Q(V(1,0,0),0.615479708)
xquats = [Q(1,0,0,0), Q(V(0,0,1),pi3), Q(V(0,0,1),2*pi3), Q(V(0,0,1),pi),
          Q(V(0,0,1),-pi3), Q(V(0,0,1),-2*pi3)]
pquats = [Q(V(0,1,0),pi4), Q(V(0,1,0),3*pi4),
          Q(V(0,1,0),-pi4), Q(V(0,1,0),-3*pi4)]

quats111 = []
for q in pquats:
    for q1 in xquats:
        quats111 += [(q+cq+q1, 2), (q-cq+q1, 2)]

allQuats = quats100 + quats110 + quats111


class GLPane(QGLWidget, modeMixin, DebugMenuMixin):
    """Mouse input and graphics output in the main view window.
    """
    # Note: external code expects self.mode to always be a working
    # mode object, which has certain callable methods.  Our modes
    # themselves expect certain other attributes (like
    # self.default_mode, self.modetab) to be present.  This is all set
    # up and maintained by our mixin class, modeMixin. [bruce 040922]
    #
    # [bruce 050112 adds: the reason the glpane is central to holding
    #  and switching a mode object might be that the mode object gets
    #  to process most mouse events on the glpane... but it might also
    #  be somewhat of a historical accident, since (esp. in the future)
    #  the mode might filter some other widgets' events too, esp. some
    #  of the operation buttons in the toolbars. Or, alternatively,
    #  modes might turn out to often apply to specific objects displayed
    #  in the glpane rather than to the pane as a whole. We'll see.
    #  For now, here it is.]

    # constants needed by modeMixin:
    default_mode_class = selectMolsMode
    other_mode_classes = [selectAtomsMode, modifyMode, depositMode, cookieMode, extrudeMode, revolveMode, movieMode, zoomMode]
    
    def __init__(self, assem, master=None, name=None, win=None):
        
        self.win = win

        modeMixin._init1(self)
        
        QGLWidget.__init__(self,master,name)
        global paneno
        self.name = str(paneno)
        paneno += 1
        self.initialised = 0

        DebugMenuMixin._init1(self) # provides self.debug_event(); needs self.makemenu()

        # The background color
        ### bruce 040928 thinks backgroundColor is never used from here,
        ### only from self.mode
        self.backgroundColor = normalBackground
        ### bruce 040928 -- i'm not sure whether or not gridColor is still used
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
        self.far = 12.0  ##2.0, Huaicai: make this bigger, so models will be
                               ## more likely sitting within the view volume

        # start in perspective mode
        self.ortho = 0

        # not selecting anything currently
        self.shape = None

        self.setMouseTracking(True)

        # bruce 041220 let the GLPane have the keyboard focus, to fix bugs.
        # See comments above our keyPressEvent method.
        ###e I did not yet review  the choice of StrongFocus in the Qt docs,
        # just copied it from MWsemantics.
        self.setFocusPolicy(QWidget.StrongFocus)

        # default display form for objects in the window
        # even tho there is only one assembly to a window,
        # this is here in anticipation of being able to have
        # multiple windows on the same assembly
        self.display = default_display_mode #bruce 041129
        self.win.dispbarLabel.setText( "Default Display: " + dispLabel[self.display] )
        self.singlet = None
        self.selatom = None # josh 10/11/04 supports depositMode

        self.makeCurrent()

        drawer.setup()

        self.setAssy(assem)

        return # from GLPane.__init__
        
    def setAssy(self, assem):
        """[bruce comment 040922] This is called from self.__init__,
        and from MWSemantics.__clear when user asks to open a new
        file, etc.  Apparently, it is supposed to forget whatever is
        happening now, and reinitialize the entire GLPane.  However,
        it does nothing to cleanly leave the current mode, if any; my
        initial guess [040922 1035am] is that that's a bug.  (As of
        040922 I didn't yet try to fix that... only to emit a warning
        when it happens. Any fix requires modifying our callers.)  I
        also wonder if setAssy ought to do some of the other things
        now in __init__, e.g. setting some display prefs to their
        defaults.  Yet another bug (in how it's called now): user is
        evidently not given any chance to save unsaved changes, or get
        back to current state if the openfile fails... tho I'm not
        sure I'm right about that, since I didn't test it.
        """
        
        assem.o = self
        self.assy = assem
        self.quat = self.assy.csys.quat
        self.scale = self.assy.csys.scale

        # defined in modeMixin [bruce 040922]; requires self.assy
        self._reinit_modes() 

    # "callback methods" from modeMixin:

    def update_after_new_mode(self):
        """do whatever updates are needed after self.mode might have changed
        (ok if this is called more than needed, except it might be slower)
        """
        #e also update tool-icon visual state in the toolbar?
        # bruce 041222 changed this to a full update, and changed MWsemantics to
        # make that safe during our __init__.
        self.win.win_update()

    # def setMode(self, modename) -- moved to modeMixin [bruce 040922]
    
    # ==

    # bruce 041220: handle keys in GLPane (see also setFocusPolicy, above).
    # Also call these from MWsemantics whenever it has the focus. This fixes
    # some key-focus-related bugs. We also wrap the Qt events with our own
    # type, to help fix Qt's Mac-specific Delete key bug (bug 93), and (in the
    # future) for other reasons. The fact that clicking in the GLPane now gives
    # it the focus (due to the setFocusPolicy, above) is also required to fully
    # fix bug 93.
    
    def keyPressEvent(self, e):
        #e future: also track these to match releases with presses, to fix
        # dialogs intercepting keyRelease? Maybe easier if they just pass it on.
        self.mode.keyPressEvent( atom_event(e) )
        
    def keyReleaseEvent(self, e):
        self.mode.keyReleaseEvent( atom_event(e) )

    def warning(self, str, bother_user_with_dialog = 0, ensure_visible = 1):
        
        """[experimental method by bruce 040922]

            ###@@@ need to merge this with self.win.history.message or make a sibling method! [bruce 041223]
        
           Show a warning to the user, without interrupting them
           (i.e. not in a dialog) unless bother_user_with_dialog is
           true, or unless ensure_visible is true and there's no other
           way to be sure they'll see the message.  (If neither of
           these options is true, we might merely print the message to
           stdout.)

           In the future, this might go into a status bar in the
           window, if we can be sure it will remain visible long
           enough.  For now, that won't work, since some status bar
           messages I emit are vanishing almost instantly, and I can't
           yet predict which ones will do that.  Due to that problem
           and since the stdout/stderr output might be hidden from the
           user, ensure_visible implies bother_user_with_dialog for
           now.  (And when we change that, we have to figure out
           whether all the calls that no longer use dialogs are still
           ok.)

           In the future, all these messages will also probably get
           timestamped and recorded in a log file, in addition to
           whereever they're shown now.

           This is an experimental method, not yet uniformly used
           (most uses are in modes.py), and it's likely to be revised
           a few times in API as well as in implemention. [bruce
           040924]
        """
        
        use_status_bar = 0 # always 0, for now
        use_dialog = bother_user_with_dialog
        
        if ensure_visible:
            prefix = "WARNING"
            use_dialog = 1 ###e for now, and during debugging --
            ### status bar would be ok when we figure out how to
            ### guarantee it lasts
        else:
            prefix = "warning"
        str = str[0].upper() + str[1:] # capitalize the sentence
        msg = "%s: %s" % (prefix,str,)
        ###e add a timestamp prefix, at least for the printed one

        # always print it so there's a semi-permanent record they can refer to
        print msg 
        
        if use_status_bar: # do this first
            ## [this would work again as of 050107:] self.win.statusBar().message( msg)
            assert 0 # this never happens for now
        if use_dialog:
            # use this only when it's worth interrupting the user to make
            # sure they noticed the message.. see docstring for details
            ##e also linebreak it if it's very long? i might hope that some
            # arg to the messagebox could do this...
            QMessageBox.warning(self, prefix, msg) # args are title, content
        return
        
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

    def fix_buttons(self, but, when):
        return fix_buttons_helper(self, but, when)

    def mouseDoubleClickEvent(self, event):
        self.debug_event(event, 'mouseDoubleClickEvent')
        but = event.stateAfter()
        #k I'm guessing this event comes in place of a mousePressEvent; test
        #this [bruce 040917]
        but = self.fix_buttons(but, 'press')
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
        
        #print "Button pressed: ", but
        
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
        
    def mousepoints(self, event, just_beyond = 0.0):
        """Returns a pair (tuple) of points (Numeric arrays of x,y,z)
        that lie under the mouse pointer at (or just beyond) the near clipping
        plane and in the plane of the center of view. Optional argument
        just_beyond = 0.0 tells how far beyond the near clipping plane
        the first point should lie. Before 041214 this was 0.01.
        """
        x = event.pos().x()
        y = self.height - event.pos().y()
        # bruce 041214 made just_beyond = 0.0 an optional argument,
        # rather than a hardcoded 0.01 (but put 0.01 into most callers)

        #Trivial optimization, change the point of the next line from(x, y, 0.0) to (x, y, 0.01)
        #So we don't need the p1 calculation next to the return statment---Huaicai 10/18, 04
        p1 = A(gluUnProject(x, y, just_beyond))
        p2 = A(gluUnProject(x, y, 1.0))

        los = self.lineOfSight
        
        k = dot(los, -self.pov - p1) / dot(los, p2 - p1)

        p2 = p1 + k*(p2-p1)
        #p1 = A(gluUnProject(x, y, just_beyond))
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
        return self.snapquat(allQuats)

    def snapquat(self, qlist):
        q1 = self.quat
        a=1.1
        what = 0
        for q2,n in qlist:
            a2 = vlen((q2-q1).axis)
            if a2 < a:
                a = a2
                q = q2
                what = n
        self.quat = Q(q)
        self.paintGL()
        return what

    def setDisplay(self, disp):
        if disp == diDEFAULT:
            disp = default_display_mode #bruce 041129 to fix bug 21
        #e someday: if self.display == disp, no actual change needed??
        # not sure if that holds for all init code, so being safe for now.
        self.display = disp
        self.win.dispbarLabel.setText( "Default Display: " + dispLabel[disp] )
        for mol in self.assy.molecules:
            if mol.display == diDEFAULT: mol.changeapp(1)


    def paintGL(self):
        """the main screen-drawing function.
        Sets up point of view projection, position, angle.
        Calls draw member fns for everything in the screen.
        """
        # bruce comment 041220: besides our own calls of this function, it can
        # be called directly from the app.exec_loop() in atom.py; I'm not sure
        # exactly why or under what circumstances, but one case (on Mac) is when you
        # switch back into the app by clicking in the blank part of the model tree
        # (multiple repaints by different routes in that case),
        # or on the window's title bar (just one repaint); another case is when
        # you switch *out* of the app by clicking on some other app's window.
        # Guess: it's a special method name known to the superclass widget.
        # (Presumably the Qt docs spell this out... find out sometime! #k)

        if not self.initialised: return

        ##print_compact_stack("paintGL called by: ")

        ##start=time.time()

        ###e bruce 040923: I'd like to reset the OpenGL state
        # completely, here, incl the stack depths, to mitigate some
        # bugs. How??  Note that there might be some OpenGL init code
        # earlier which I'll have to not mess up. Incl displaylists in
        # drawer.setup.  What I ended up doing is just to measure the
        # stack depth and pop it 0 or more times to make the depth 1
        # -- see below.
     
        c=self.mode.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	glMatrixMode(GL_MODELVIEW)

	# restore GL_MODELVIEW_STACK_DEPTH if necessary [bruce 040923,
	# to partly mitigate the effect of certain drawing bugs] btw I
	# don't know for sure whether this causes a significant speed
	# hit for some OpenGL implementations (esp. X windows)...
	# test sometime. #e
        
	depth = glGetInteger(GL_MODELVIEW_STACK_DEPTH)
        # this is normally 1
        # (by experiment, qt-mac-free-3.3.3, Mac OS X 10.2.8...)
	if depth > 1:
            print "apparent bug: glGetInteger(GL_MODELVIEW_STACK_DEPTH) = %r in GLPane.paintGL" % depth
            print "workaround: pop it back to depth 1"
            while depth > 1:
                depth -= 1
                glPopMatrix()
            newdepth = glGetInteger(GL_MODELVIEW_STACK_DEPTH)
            if newdepth != 1:
                print "hmm, after depth-1 pops we should have reached depth 1, but instead reached depth %r" % newdepth
            pass	
	
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
        if aspect < 1.0:
             vdist /= aspect
        
        glTranslatef(0.0, 0.0, - vdist)
	# bruce 041214 comment: some code assumes vdist is always 6.0 * self.scale
	# (e.g. eyeball computations, see bug 30), thus has bugs for aspect < 1.0.
	# We should have glpane attrs for aspect, w_scale, h_scale, eyeball,
	# clipping planes, etc, like we do now for right, up, etc. ###e

        q = self.quat
        
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)

        glTranslatef(self.pov[0], self.pov[1], self.pov[2])

        # draw according to mode
        self.mode.Draw()
        glFlush()                           # Tidy up
        self.swapBuffers()

    def drawarrow(self, aspect):
        glOrtho(-50*aspect, 5.5*aspect, -50, 5.5,  -5, 500)
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
        
        ##Adding "X, Y, Z" text labels for Axis. By test, the following code will get segmentation fault on Manrake Linux 10.0 with libqt3-3.2.3-17mdk or other 3.2.* versions, but works with libqt3-3.3.3-26mdk. Huaicai 1/15/05
        
        if True:###sys.platform in ['darwin', 'win32']:
                glDisable(GL_LIGHTING)
                glDisable(GL_DEPTH_TEST)
                glPushMatrix()
                font = QFont(QString("Helvetica"), 12, QFont.Normal)
                self.qglColor(QColor(75, 75, 75))
                self.renderText(5.3, 0.0, 0.0, QString("x"), font)
                self.renderText(0.0, 4.8, 0.0, QString("y"), font)
                self.renderText(0.0, 0.0, 5.0, QString("z"), font)
                glPopMatrix()
                glEnable(GL_DEPTH_TEST)
                glEnable(GL_LIGHTING)
        
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
        if filename[-3:] == "pov": self.writepov(filename, width, height)
        else:  self.jpgwrite(filename, width, height)

    def jpgwrite(self, filename, width, height):

        buf = array(glReadPixelsub(0, 0, width, height, GL_RGB))
        buf = reshape(buf, (height, width, 3))
        
        buf = reshape(buf[::-1],(width*height,3))

        buf = map(lambda x: struct.unpack("BBB", x), buf)

        pic = Image.new("RGB", (width, height))
        pic.putdata(buf)
        pic.save(filename, "JPEG", quality=85)

    def __str__(self):
        return "<GLPane " + self.name + ">"

    def makemenu(self, lis):
        return makemenu_helper(self, lis)

    pass # end of class GLPane

# ==

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

# end