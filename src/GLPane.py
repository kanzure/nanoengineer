# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
GLPane.py -- Atom's main model view, based on Qt's OpenGL widget.

Mostly written by Josh; partly revised by Bruce for mode code revision, 040922-24.
Revised by many other developers since then (and perhaps before).

$Id$
"""

## bruce 050408 removed several "import *" below
from qt import QFont, QWidget, QMessageBox 
from qtgl import QGLWidget
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
import re
from constants import *

from modifyMode import modifyMode
from cookieMode import cookieMode 
from extrudeMode import extrudeMode, revolveMode
from fusechunksMode import fusechunksMode
from selectMode import *
from depositMode import depositMode
from movieMode import movieMode
from zoomMode import zoomMode
from panMode import panMode
from rotateMode import rotateMode
from translateMode import translateMode
from modes import modeMixin

import operator
import struct
##bruce 050413 removed: from povheader import povheader, povpoint

from fileIO import * #bruce 050414 comment: this might no longer be needed;
    # at least most symbols defined in fileIO (now moved to files_mmp)
    # don't occur in GLPane; but I didn't check for the few that are still
    # defined in fileIO.
from HistoryWidget import greenmsg, redmsg
from platform import fix_buttons_helper
import platform # for platform.atom_debug
from widgets import makemenu_helper
from debug import DebugMenuMixin, print_compact_traceback
import preferences


paneno = 0
#  ... what a Pane ...

## normalGridLines = (0.0, 0.0, 0.6) # bruce 050410 removed this, and related code

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
    other_mode_classes = [selectAtomsMode, modifyMode, depositMode, cookieMode,
                          extrudeMode, revolveMode, fusechunksMode, movieMode,
                          zoomMode, panMode, rotateMode, translateMode]
    
    def __init__(self, assem, master=None, name=None, win=None):
        
        self.win = win

        modeMixin._init1(self)
        
        QGLWidget.__init__(self,master,name)
        global paneno
        self.name = str(paneno)
        paneno += 1
        self.initialised = 0

        DebugMenuMixin._init1(self) # provides self.debug_event(); needs self.makemenu()

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

        self.zoomFactor = 1.0
        # start in perspective mode
        self.ortho = 0

        ##Huaicai 2/8/05: If this is true, redraw everything. It's better to split
        ##the paintGL() to several functions, so we may choose to draw 
        ##every thing, or only some thing that has been changed.
        self.redrawGL = True  
        
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

        self.loadLighting() #bruce 050311
        
        return # from GLPane.__init__        
        
    def setInitialView(self, assy):
        """Huaicai 1/27/05: part of the code of this method comes
        from original setAssy() method. This method can be called
        after setAssy() has been called, for example, when opening
        an mmp file. Sets the initial view.
        """   
        self.quat = Q(assy.lastCsys.quat)
        self.scale = assy.lastCsys.scale
        self.pov = V(assy.lastCsys.pov[0], assy.lastCsys.pov[1], assy.lastCsys.pov[2])
        self.zoomFactor = assy.lastCsys.zoomFactor
    
    def saveLastView(self, assy):
        """Huaicai 1/27/05: before mmp file saving, this method
        should be called to save the last view user has, which will
        be used as the initial view when it is opened again.
        """    
        assy.lastCsys.quat = Q(self.quat)
        assy.lastCsys.scale = self.scale
        assy.lastCsys.pov = V(self.pov[0], self.pov[1], self.pov[2])
        assy.lastCsys.zoomFactor = self.zoomFactor
            
            
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
        
        self.setInitialView(assem)
        
        # defined in modeMixin [bruce 040922]; requires self.assy
        self._reinit_modes() 

    # "callback methods" from modeMixin:

    def update_after_new_mode(self):
        """do whatever updates are needed after self.mode might have changed
        (ok if this is called more than needed, except it might be slower)
        """
        #bruce 050408: change widget's erase color (seen only if it's resized,
        # and only briefly -- unrelated to OpenGL clearColor) to current mode's
        # background color; this fixes the bug in which the glpane or its edges
        # flicker to black during a main-window resize.
        #bruce 050413: limit this to Mac, since it turns out that bug (which has
        # no bug number yet) was Mac-specific, but this change caused a new bug 530
        # on Windows. (Not sure about Linux.)
        # See also bug 141 (black during mode-change), related but different.
        if sys.platform == 'darwin':
            bgcolor = self.mode.backgroundColor
            r = int(bgcolor[0]*255 + 0.5) # (same formula as in elementSelector.py)
            g = int(bgcolor[1]*255 + 0.5)
            b = int(bgcolor[2]*255 + 0.5)
            self.setPaletteBackgroundColor(QColor(r, g, b))
                # see Qt docs for this and for backgroundMode
        
        #e also update tool-icon visual state in the toolbar?
        # bruce 041222 [comment revised 050408]:
        # changed this to a full update (not just a glpane update),
        # though technically the non-glpane part is the job of our caller rather than us,
        # and changed MWsemantics to make that safe during our __init__.
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

            ###@@@ need to merge this with self.win.history.message
            or make a sibling method! [bruce 041223]
        
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

    # == lighting methods [bruce 050311 rush order for Alpha4]
    
    def setLighting(self, lights, _guard_ = 6574833, gl_update = True): 
        """Set current lighting parameters as specified
        (using the format as described in the getLighting method docstring).
        This does not save them in the preferences file; for that see the saveLighting method.
        If option gl_update is False, then don't do a gl_update, let caller do that if they want to.
        """
        assert _guard_ == 6574833 # don't permit optional args to be specified positionally!!
        try:
            # check, standardize, and copy what the caller gave us for lights
            res = []
            lights = list(lights)
            assert len(lights) == 3
            for a,d,e in lights:
                # check values, give them standard types
                a = float(a)
                d = float(d)
                assert 0.0 <= a <= 1.0
                assert 0.0 <= d <= 1.0
                assert e in [0,1,True,False]
                e = not not e
                res.append( (a,d,e) )
            lights = res
        except:
            print_compact_traceback("erroneous lights %r (ignored): " % lights)
            return
        self._lights = lights
        # set a flag so we'll set up the new lighting in the next paintGL call
        self.need_setup_lighting = True
        #e maybe arrange to later save the lighting in prefs... don't know if this belongs here
        # update GLPane unless caller wanted to do that itself
        if gl_update:
            self.gl_update()
        return

    def getLighting(self):
        """Return the current lighting parameters
        [for now, these are a list of 3 triples, one per light,
        each giving 2 floats from 0 to 1 and a boolean,
        which are ambient, diffuse, enabled for that light]
        """
        return list(self._lights)

    # default value of instance variable:
    _lights = [(0.3, 0.8, True), (0.4, 0.4, True), (1.0, 1.0, False)] #e might revise format
        # for each of 3 lights (at hardcoded positions for now), this stores (a,d,e)
        # giving gray levels for GL_AMBIENT and GL_DIFFUSE and an enabled boolean

    _default_lights = list( _lights) # this copy will never be changed

    need_setup_lighting = True # whether the next paintGL needs to call it
    
    def _setup_lighting(self):
        """[private method]
        Set up lighting in the model (according to self._lights).
        [Called from both initializeGL and paintGL.]
        """
        glEnable(GL_NORMALIZE) # bruce comment 050311: I don't know if this relates to lighting or not

        #bruce 050413 try to fix bug 507 in direction of lighting:
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        try:
            # new code
            ((a0,d0,e0),(a1,d1,e1),(a2,d2,e2)) = self._lights #e might revise format
            
            glLightfv(GL_LIGHT0, GL_POSITION, (-50, 70, 30, 0))
            glLightfv(GL_LIGHT0, GL_AMBIENT, (a0, a0, a0, 1.0))
            glLightfv(GL_LIGHT0, GL_DIFFUSE, (d0, d0, d0, 1.0))
            glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
            
            glLightfv(GL_LIGHT1, GL_POSITION, (-20, 20, 20, 0))
            glLightfv(GL_LIGHT1, GL_AMBIENT, (a1, a1, a1, 1.0))
            glLightfv(GL_LIGHT1, GL_DIFFUSE, (d1, d1, d1, 1.0))
            glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
            
            glLightfv(GL_LIGHT2, GL_POSITION, (0, 0, 100, 0))
            glLightfv(GL_LIGHT2, GL_AMBIENT, (a2, a2, a2, 1.0))
            glLightfv(GL_LIGHT2, GL_DIFFUSE, (d2, d2, d2, 1.0))
            glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)
            
            glEnable(GL_LIGHTING)
            
            if e0:
                glEnable(GL_LIGHT0)
            else:
                glDisable(GL_LIGHT0)
                
            if e1:
                glEnable(GL_LIGHT1)
            else:
                glDisable(GL_LIGHT1)
                
            if e2:
                glEnable(GL_LIGHT2)
            else:
                glDisable(GL_LIGHT2)
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: _setup_lighting reverting to old code, because: ")
            # old code
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
        return

    def saveLighting(self):
        "save the current lighting values in the standard preferences database"
        try:
            prefs = preferences.prefs_context()
            key = "glpane lighting" # hardcoded in two methods
            # we'll store everything in a single value at this key,
            # making it a dict of dicts so it's easy to add more lighting attrs (or lights) later
            # in an upward-compatible way.
            
            # first, verify format of self._lights is what we expect:
            ((a0,d0,e0),(a1,d1,e1),(a2,d2,e2)) = self._lights #e might revise format
            # now process it in a cleaner way
            val = {}
            for (i, (a,d,e)) in zip(range(3),self._lights):
                name = "light%d" % i
                ambient_color = (a,a,a) # someday we'll store any color; for now, reading code assumes r==g==b in this color
                diffuse_color = (d,d,d)
                params = dict( ambient = ambient_color, diffuse = diffuse_color, enabled = e )
                val[name] = params
            # save the prefs to the database file
            prefs[key] = val
            self.win.history.message( greenmsg( "Lighting preferences saved" ))
        except:
            print_compact_traceback("bug: exception in saveLighting (pref changes not saved): ")
            #e redmsg?
        return

    def loadLighting(self, gl_update = True):
        """load new lighting values from the standard preferences database, if possible;
        if correct values were loaded, start using them, and do gl_update unless option for that is False;
        return True if you loaded new values, False if that failed
        """
        try:
            prefs = preferences.prefs_context()
            key = "glpane lighting" # hardcoded in two methods
            try:
                val = prefs[key]
            except KeyError:
                # none were saved; not an error and not even worthy of a message
                # since this is called on startup and it's common for nothing to be saved.
                # Return with no changes.
                return False
            # At this point, you have a saved prefs val, and if this is wrong it's an error.        
            # val format is described (partly implicitly) in saveLighting method.
            res = [] # will become new argument to pass to self.setLighting method, if we succeed
            for name in ['light0','light1','light2']:
                params = val[name] # a dict of ambient, diffuse, enabled
                ac = params['ambient'] # ambient color
                dc = params['diffuse'] # diffuse color
                e = params['enabled'] # boolean
                a = ac[0] # only grays are saved for now
                d = dc[0]
                res.append( (a,d,e) )
            self.setLighting( res, gl_update = gl_update)
            ## self.win.history.message( greenmsg( "Lighting preferences loaded" )) # not desired for now
            if platform.atom_debug:
                print "atom_debug: fyi: Lighting preferences loaded"
            return True
        except:
            print_compact_traceback("bug: exception in loadLighting (current prefs not altered): ")
            #e redmsg?
            return False
        pass

    def restoreDefaultLighting(self, gl_update = True): # not yet tested, sole caller not yet used ###@@@
        "restore the default (built-in) lighting preferences (but don't save them)."
        self.setLighting( self._default_lights,  gl_update = gl_update )
        ## self.win.history.message( greenmsg( "Lighting preferences restored to defaults (but not saved)" )) # not desired for now
        return True
    
    # ==
    
    def initializeGL(self):
        "#doc [called by Qt]"
        self.makeCurrent() # bruce comment 050311: probably not needed since Qt does it before calling this
        self._setup_lighting()
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        return

    def fix_buttons(self, but, when):
        return fix_buttons_helper(self, but, when)

    def mouseDoubleClickEvent(self, event):
        self.debug_event(event, 'mouseDoubleClickEvent')
        but = event.stateAfter()
        #k I'm guessing this event comes in place of a mousePressEvent; test
        #this [bruce 040917]
        #print "Double clicked: ", but
        
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
        ## Huaicai 2/25/05. This is to fix item 2 of bug 400: make this rendering context
        ## as current, otherwise, the first event will get wrong coordinates
        self.makeCurrent()
        
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
        
        #print "Button released: ", but
        
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
            #Huaicai: To fix bugs related to multiple rendering contexts existed in our application.
            # See comments in mousePressEvent() for more detail.
            self.makeCurrent()
            
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

        p1 = A(gluUnProject(x, y, just_beyond))
        p2 = A(gluUnProject(x, y, 1.0))

        los = self.lineOfSight
        
        k = dot(los, -self.pov - p1) / dot(los, p2 - p1)

        p2 = p1 + k*(p2-p1)
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
        self.gl_update()
        return what

    def setDisplay(self, disp):
        if disp == diDEFAULT:
            disp = default_display_mode #bruce 041129 to fix bug 21
        #e someday: if self.display == disp, no actual change needed??
        # not sure if that holds for all init code, so being safe for now.
        self.display = disp
        ##Huaicai 3/29/05: Add the condition to fix bug 477
        if self.mode.modename == 'COOKIE':
            self.win.dispbarLabel.setText("    ")
        else:    
            self.win.dispbarLabel.setText( "Default Display: " + dispLabel[disp] )
        for mol in self.assy.molecules:
            if mol.display == diDEFAULT: mol.changeapp(1)

    def setZoomFactor(self, zFactor):
            self.zoomFactor = zFactor
    def getZoomFactor(self):
            return self.zoomFactor        

    def gl_update(self): #bruce 050127
        """External code should call this when it thinks the GLPane needs
        redrawing, rather than directly calling paintGL, unless it really
        knows it needs to wait until the redrawing has been finished
        (which should be very rare).
           Unlike calling paintGL directly (which can be very slow for
        large models, and redoes all its work each time it's called),
        this method is ok to call many times during the handling of one
        user event, since this will cause only one call of paintGL, after
        that user event handler has finished.
        """
        # (To restore the pre-050127 behavior, it would be sufficient to
        # change the next line from "self.update()" to "self.paintGL()".)
        self.update()
            # QWidget.update() method -- ask Qt to call self.paintGL()
            # (via some sort of paintEvent to our superclass)
            # very soon after the current event handler returns
        return
    
    def paintGL(self): #bruce 050127 revised docstring to deprecate direct calls
        """[PRIVATE METHOD -- call gl_update instead!]
        The main screen-drawing function, called internally by Qt when our
        superclass needs to repaint. THIS SHOULD NO LONGER BE CALLED DIRECTLY
        BY EXTERNAL CODE -- CALL gl_update INSTEAD.
           Sets up point of view projection, position, angle.
        Calls draw member fns for everything in the screen.
        """
        # bruce comment 041220: besides our own calls of this function
        # [later: which no longer exist after 050127], it can
        # be called directly from the app.exec_loop() in atom.py; I'm not sure
        # exactly why or under what circumstances, but one case (on Mac) is when you
        # switch back into the app by clicking in the blank part of the model tree
        # (multiple repaints by different routes in that case),
        # or on the window's title bar (just one repaint); another case is when
        # you switch *out* of the app by clicking on some other app's window.
        # Guess: it's a special method name known to the superclass widget.
        # (Presumably the Qt docs spell this out... find out sometime! #k)

        if not self.initialised: return
       
        if not self.redrawGL: return

        if self.need_setup_lighting:
            # I don't know if it matters to avoid calling this every time...
            # in case it's slow, we'll only do it when it might have changed.
            self.need_setup_lighting = False # set to true again if setLighting is called
            self._setup_lighting()

        ###e bruce 040923: I'd like to reset the OpenGL state
        # completely, here, incl the stack depths, to mitigate some
        # bugs. How??  Note that there might be some OpenGL init code
        # earlier which I'll have to not mess up. Incl displaylists in
        # drawer.setup.  What I ended up doing is just to measure the
        # stack depth and pop it 0 or more times to make the depth 1
        # -- see below.
        c = self.mode.backgroundColor
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
            glOrtho(-self.scale*aspect*self.zoomFactor, self.scale*aspect*self.zoomFactor,
                    -self.scale*self.zoomFactor, self.scale*self.zoomFactor,
                    vdist*self.near, vdist*self.far)
        else:
            glFrustum(-self.scale*aspect*self.near*self.zoomFactor, self.scale*aspect*self.near*self.zoomFactor,
                      -self.scale*self.near*self.zoomFactor, self.scale*self.near*self.zoomFactor,
                      vdist*self.near, vdist*self.far)

        glMatrixMode(GL_MODELVIEW)
        
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
        
        # let parts (other than the main part) draw a text label, to warn
        # the user that the main part is not being shown [bruce 050408]
        try:
            self.assy.part.draw_text_label(self)
        except:
            if platform.atom_debug:
                print_compact_traceback( "atom_debug: exception in self.assy.part.draw_text_label(self): " )
            pass # if it happens at all, it'll happen too often to bother users with an error message
        
        glFlush()  #Tidy up
        ##self.swapBuffers()  ##This is a redundant call, Huaicai 2/8/05
        return # from paintGL       


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
           
        ##Adding "X, Y, Z" text labels for Axis. By test, the following code will get
        # segmentation fault on Manrake Linux 10.0 with libqt3-3.2.3-17mdk
        # or other 3.2.* versions, but works with libqt3-3.3.3-26mdk. Huaicai 1/15/05
           
        if True:###sys.platform in ['darwin', 'win32']:
                glDisable(GL_LIGHTING)
                glDisable(GL_DEPTH_TEST)
                glPushMatrix()
                font = QFont( QString("Times"), 10)#QFont(QString("Helvetica"), 12, QFont.Normal)
                self.qglColor(QColor(75, 75, 75))
                self.renderText(5.3, 0.0, 0.0, QString("x"), font)
                self.renderText(0.0, 4.8, 0.0, QString("y"), font)
                self.renderText(0.0, 0.0, 5.0, QString("z"), font)
                glPopMatrix()
                glEnable(GL_DEPTH_TEST)
                glEnable(GL_LIGHTING)
           
        glLoadIdentity()
        return
           
    def resizeGL(self, width, height):
        """Called by QtGL when the drawing window is resized.
        """
        self.width = width
        self.height = height
           
	glViewport(0, 0, self.width, self.height)
           
        if not self.initialised:
            self.initialised = 1
        self.trackball.rescale(width, height)
        self.gl_update()
        return
           
    def xdump(self):
        """for debugging"""
        print " pov: ", self.pov
        print " quat ", self.quat

    def __str__(self):
        return "<GLPane " + self.name + ">"

    def makemenu(self, lis):
        return makemenu_helper(self, lis)

    pass # end of class GLPane

# end
