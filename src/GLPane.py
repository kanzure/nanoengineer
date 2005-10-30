# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
GLPane.py -- Atom's main model view, based on Qt's OpenGL widget.

Mostly written by Josh; partly revised by Bruce for mode code revision, 040922-24.
Revised by many other developers since then (and perhaps before).

$Id$

bruce 050913 used env.history in some places.
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
from modes import modeMixin

import operator
import struct
##bruce 050413 removed: from povheader import povheader, povpoint

from fileIO import * #bruce 050414 comment: this might no longer be needed;
    # at least most symbols defined in fileIO (now moved to files_mmp)
    # don't occur in GLPane; but I didn't check for the few that are still
    # defined in fileIO.
from HistoryWidget import greenmsg, redmsg
from platform import fix_event_helper
import platform # for platform.atom_debug
from widgets import makemenu_helper
from debug import DebugMenuMixin, print_compact_traceback
import preferences
import env
from changes import SubUsageTrackingMixin


debug_lighting = False #bruce 050418

trans_feature = False ###@@@ bruce 050627 experimental code disabled for commit [DO NOT COMMIT with true]


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


class GLPane(QGLWidget, modeMixin, DebugMenuMixin, SubUsageTrackingMixin):
    """Mouse input and graphics output in the main view window.
    """
    # Note: external code expects self.mode to always be a working
    # mode object, which has certain callable methods.  Our modes
    # themselves expect certain other attributes (like self.modetab)
    # to be present.  This is all set up and maintained by our mixin
    # class, modeMixin. [bruce 040922]
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

    # class constants (needed by modeMixin):
    mode_classes = [selectMolsMode, selectAtomsMode, modifyMode, depositMode,
                    cookieMode, extrudeMode, revolveMode, fusechunksMode,
                    movieMode, zoomMode, panMode, rotateMode]
    
    def __init__(self, assy, master=None, name=None, win=None):
        
        self.win = win

        modeMixin._init1(self)

        #bruce 050610 set gl format to request stencil buffer
        # (needed for mouseover-highlighting of objects of general shape in depositMode.bareMotion)
        glformat = QGLFormat()
        glformat.setStencil(True)
        
        QGLWidget.__init__(self, glformat, master, name)

        self.stencilbits = 0 # conservative guess, will be set to true value below
        
        if not self.format().stencil():
            # It's apparently too early to also test "or glGetInteger(GL_STENCIL_BITS) < 1" --
            # that glGet returns None even when the bits are actually there
            # (on my system this is 8 when tested later). Guess: this won't work until
            # the context is initialized.
            msg = ("Warning: your graphics hardware did not provide an OpenGL stencil buffer.\n"
                   "This will slow down some graphics operations.")
            ## env.history.message( regmsg( msg)) -- too early for that to work (need to fix that sometime, to queue the msg)
            print msg
            if platform.atom_debug:
                print "atom_debug: details of lack of stencil bits: " \
                      "self.format().stencil() = %r, glGetInteger(GL_STENCIL_BITS) = %r" % \
                      ( self.format().stencil() , glGetInteger(GL_STENCIL_BITS) )
                      # Warning: these values can be False, None -- I don't know why, since None is not an int!
                      # But see above for a guess. [bruce 050610]
            pass
        else:
            ## self.stencilbits = int( glGetInteger(GL_STENCIL_BITS) ) -- too early!
            self.stencilbits = 1 # conservative guess that if we got the buffer, it has at least one bitplane
                #e could probably be improved by testing this in initializeGL or paintGL (doesn't matter yet)
##            if platform.atom_debug:
##                print "atom_debug: glGetInteger(GL_STENCIL_BITS) = %r" % ( glGetInteger(GL_STENCIL_BITS) , )
            pass

        global paneno
        self.name = str(paneno)
        paneno += 1
        self.initialised = 0

        DebugMenuMixin._init1(self) # provides self.debug_event() [might provide or require more things too... #doc]

        self.trackball = Trackball(10,10)


        # [bruce 050419 new feature:]
        # The current Part to be displayed in this GLPane.
        # Logically this might not be the same as it's assy's current part, self.assy.part,
        # though in initial implem it will be the same except
        # when the part is changing... but the brief difference is important
        # since that's how the GLPane knows which previous part to store its
        # current view attributes in, before grabbing them from the new current part.
        # But some code might (incorrectly in principle, ok for now)
        # use self.assy.part when it should be using self.part.
        # The only thing we're sure self.part must be used for is to know in which
        # part the view attributes belong.
        self.part = None
        
        # Current view attributes (sometimes saved in or loaded from
        #  the currently displayed part or its mmp file):
        
        # rotation
        self.quat = Q(1, 0, 0, 0)
        # point of view (i.e. negative of center of view)
        self.pov = V(0.0, 0.0, 0.0)
        # half-height of window in Angstroms (gets reset by certain view-changing operations [bruce 050615 comment])
        self.scale = 10.0
        # zoom factor
        self.zoomFactor = 1.0


        # Other "current preference" attributes. ###e Maybe some of these should
        # also be part-specific and/or saved in the mmp file? [bruce 050418]

        # clipping planes, as percentage of distance from the eye
        self.near = 0.66
        self.far = 12.0  ##2.0, Huaicai: make this bigger, so models will be
                               ## more likely sitting within the view volume
        # start in perspective mode
        self.ortho = 0

        # Current coordinates of the mouse.
        self.MousePos = V(0,0)
 
        ##Huaicai 2/8/05: If this is true, redraw everything. It's better to split
        ##the paintGL() to several functions, so we may choose to draw 
        ##every thing, or only some thing that has been changed.
        self.redrawGL = True  
        
        # not selecting anything currently
        # [as of 050418 (and before), this is used in cookieMode and selectMode]
        self.shape = None

        self.setMouseTracking(True)

        # bruce 041220 let the GLPane have the keyboard focus, to fix bugs.
        # See comments above our keyPressEvent method.
        ###e I did not yet review  the choice of StrongFocus in the Qt docs,
        # just copied it from MWsemantics.
        self.setFocusPolicy(QWidget.StrongFocus)

        self.singlet = None
        self.selatom = None # josh 10/11/04 supports depositMode

        # [bruce 050608]
        self.glselect_dict = {} # only used within individual runs
            # see also env.obj_with_glselect_name

        ###### User Preference initialization ##############################
        
        # Get glpane related settings from prefs db.
        # Default values are set in "prefs_table" in prefs_constants.py.
        # Mark 050919.
        
        self.displayCompass = env.prefs[displayCompass_prefs_key]
        self.compassPosition = env.prefs[compassPosition_prefs_key]
        self.displayOriginAxis = env.prefs[displayOriginAxis_prefs_key]
        self.displayPOVAxis = env.prefs[displayPOVAxis_prefs_key]
        self.ortho = env.prefs[defaultProjection_prefs_key]
        # This updates the checkmark in the View menu. Fixes bug #996 Mark 050925.
        self.setViewProjection(self.ortho) 

        # default display form for objects in the window
        # even tho there is only one assembly to a window,
        # this is here in anticipation of being able to have
        # multiple windows on the same assembly
        self.display = env.prefs[defaultDisplayMode_prefs_key]
            #bruce 050810 diVDW -> default_display_mode (equivalent)
        self.win.dispbarLabel.setText( "Current Display: " + dispLabel[self.display] )
        
        ###### End of User Preference initialization ########################## 
        
        self.makeCurrent()
        
        drawer.setup()
        self.setAssy(assy) # leaves self.mode as nullmode, as of 050911

        self.loadLighting() #bruce 050311
        
        return # from GLPane.__init__        

    # self.part maintainance [bruce 050419]
    
    def set_part(self, part):
        """change our current part to the one given, and take on that part's view;
        ok if old or new part is None;
        note that when called on our current part,
        effect is to store our view into it
        (which might not actually be needed, but is fast enough and harmless)
        """
        if self.part is not part:
            self.gl_update() # we depend on this not doing the redraw until after we return
        self._close_part() # saves view into old part (if not None)
        self.part = part
        self._open_part() # loads view from new part (if not None)

    def forget_part(self, part):
        "[public] if you know about this part, forget about it (call this from dying parts)"
        if self.part is part:
            self.set_part(None)
        return

    def _close_part(self):
        "[private] save our current view into self.part [if not None] and forget about self.part"
        if self.part:
            self._saveLastViewIntoPart( self.part)
        self.part = None

    def _open_part(self):
        "[private] after something set self.part, load our current view from it"
        if self.part:
            self._setInitialViewFromPart( self.part)
        # else our current view doesn't matter
        return

    def saveLastView(self):
        "[public method] update the view of all parts you are displaying (presently only one or none) from your own view"
        if self.part:
            self._saveLastViewIntoPart( self.part)
    
    #bruce 050418 split the following Csys methods into two methods each,
    # so MWsemantics can share code with them. Also revised their docstrings,
    # and revised them for assembly/part split (i.e. per-part csys records),
    # and renamed them as needed to reflect that.
    
    def _setInitialViewFromPart(self, part):
        """Set the initial (or current) view used by this GLPane
        to the one stored in part.lastCsys, i.e. to part's "Last View".
        """
        # Huaicai 1/27/05: part of the code of this method comes
        # from original setAssy() method. This method can be called
        # after setAssy() has been called, for example, when opening
        # an mmp file. 
        self.setViewFromCsys( part.lastCsys)

    def setViewFromCsys(self, csys):
        "Set the initial or current view used by this GLPane to the one stored in the given Csys object."
        self.quat = Q(csys.quat)
        self.scale = csys.scale
        self.pov = V(csys.pov[0], csys.pov[1], csys.pov[2])
        self.zoomFactor = csys.zoomFactor
    
    def _saveLastViewIntoPart(self, part):
        """Save the current view used by this GLPane into part.lastCsys,
        which (when this part's assy is later saved in an mmp file)
        will be saved as that part's "Last View".
        [As of 050418 this still only gets saved in the file for the main part]
        """
        # Huaicai 1/27/05: before mmp file saving, this method
        # should be called to save the last view user has, which will
        # be used as the initial view when it is opened again.
        self.saveViewInCsys( part.lastCsys)

    def saveViewInCsys(self, csys):
        "Save the current view used by this GLPane in the given Csys object."
        #e [bruce comment 050418: it would be good to verify csys has the right type,
        #   since almost any python object could be used here without any immediately
        #   detectable error. Maybe this should be a method in csys.]
        csys.quat = Q(self.quat)
        csys.scale = self.scale
        csys.pov = V(self.pov[0], self.pov[1], self.pov[2])
        csys.zoomFactor = self.zoomFactor

    # ==
    
    def setAssy(self, assy): #bruce 050911 revised this
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
           Revised 050911: leaves self.mode as nullmode.
        """
        assy.o = self ###@@@ should only the part know the glpane?? or, only the mode itself? [bruce 050418 comment]
        self.assy = assy
        try:
            mainpart = assy.tree.part
            assert mainpart
        except:
            # I hope this never happens... but I don't know; if it does, reorder things?? [bruce 050418 comment]
            # [bruce 050428: I've never seen it that I noticed...]
            if platform.atom_debug:
                print "atom_debug: no mainpart yet in setAssy (ok during init); using a fake one"
            mainpart = Part(self) #bruce 050418 -- might be common during init; use this just for its lastCsys
            self._setInitialViewFromPart( mainpart)
        else:
            # [bruce 050428: this apparently always happens]
            self.set_part( mainpart)
        
        # defined in modeMixin [bruce 040922]; requires self.assy
        self._reinit_modes() # leaves mode as nullmode as of 050911
        return

    # == view toolbar helper methods
    
    # [bruce 050418 made these from corresponding methods in MWsemantics.py,
    #  which still exist but call these, perhaps after printing a history message.
    #  Also revised them for assembly/part split, i.e. per-part csys attributes.]
    
    def setViewHome(self):
        "Change current view to our model's home view (for glpane's current part), and gl_update."
        self.setViewFromCsys( self.part.homeCsys)
        self.gl_update()

    def setViewFitToWindow(self):
        "Change current view so that our model's bbox fits in our window, and gl_update."
        #Recalculate center and bounding box for the current part
        part = self.part
        part.computeBoundingBox()
        self.scale = float( part.bbox.scale() ) #bruce 050616 added float() as a precaution, probably not needed
            # appropriate height to show everything, for square or wide glpane [bruce 050616 comment]
        aspect = float(self.width) / self.height
        if aspect < 1.0:
            # tall (narrow) glpane -- need to increase self.scale
            # (defined in terms of glpane height) so part bbox fits in width
            # [bruce 050616 comment]
            self.scale /= aspect
        self.pov = V(-part.center[0], -part.center[1], -part.center[2]) 
        self.setZoomFactor(1.0)
        self.gl_update()

    def setViewHomeToCurrent(self):
        "Save our current view as home view of glpane's current part, and mark part as changed."
        self.saveViewInCsys( self.part.homeCsys)
        self.part.changed() # Mark [041215]

    def setViewRecenter(self):
        "Recenter our current view around the origin of modeling space in our current part, and gl_update."
        part = self.part
        self.pov = V(0,0,0)
        part.computeBoundingBox()
        self.scale = part.bbox.scale() + vlen(part.center)
            #bruce 050418 comments:
            # - doesn't this need to correct for aspect ratio, like setViewFitToWindow does? ###e
            # - why does it mark part as changed? I doubt it should (side effect of computeBoundingBox shouldn't require it).
        part.changed()
        self.gl_update()
        
    def setViewProjection(self, projection): # Added by Mark 050918.
        '''Set projection, where 0 = Perspective and 1 = Orthographic.  It does not set the 
        prefs db value itself, since we don't want all user changes to projection to be stored
        in the prefs db, only the ones done from the Preferences dialog.
        '''

        # Set the checkmark for the Ortho/Perspective menu item in the View menu.  
        # This needs to be done before comparing the value of self.ortho to projection
        # because self.ortho and the toggle state of the corresponding action may 
        # not be in sync at startup time. This fixes bug #996.
        # Mark 050924.
        if projection:
            self.win.setViewOrthoAction.setOn(1)
        else:
            self.win.setViewPerspecAction.setOn(1)
        
        if self.ortho == projection:
            return
            
        self.ortho = projection
        self.gl_update()
    
    # == "callback methods" from modeMixin:

    def update_after_new_mode(self):
        """do whatever updates are needed after self.mode might have changed
        (ok if this is called more than needed, except it might be slower)
        """
        if self.selatom is not None: #bruce 050612 precaution (scheme could probably be cleaned up #e)
            if platform.atom_debug:
                print "atom_debug: update_after_new_mode storing None over self.selatom", self.selatom
            self.selatom = None
        if self.selobj is not None: #bruce 050612 bugfix; to try it, in Build drag selatom over Select Atoms toolbutton & press it
            if platform.atom_debug:
                print "atom_debug: update_after_new_mode storing None over self.selobj", self.selobj
            self.set_selobj(None)
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
                ##e [bruce 050615 comment, moved here from a wrong location by bruce 050702:]
                # for modes with transparent surfaces covering screen, this ought to blend that in
                # (or we could change how they work so the blank areas looked like the specified bgcolor)
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

            ###@@@ need to merge this with env.history.message
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
            env.history.message( greenmsg( "Lighting preferences saved" ))
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
            if debug_lighting:
                print "debug_lighting: fyi: Lighting preferences loaded"
            return True
        except:
            print_compact_traceback("bug: exception in loadLighting (current prefs not altered): ")
            #e redmsg?
            return False
        pass

    def restoreDefaultLighting(self, gl_update = True): # not yet tested, sole caller not yet used ###@@@
        "restore the default (built-in) lighting preferences (but don't save them)."
        self.setLighting( self._default_lights,  gl_update = gl_update )
        ## env.history.message( greenmsg( "Lighting preferences restored to defaults (but not saved)" )) # not desired for now
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

    def fix_event(self, but, when, target): #bruce 050913 revised this from fix_buttons
        return fix_event_helper(self, but, when, target)

    def mouseDoubleClickEvent(self, event):
        self.debug_event(event, 'mouseDoubleClickEvent')
        ## but = event.stateAfter()
        #k I'm guessing this event comes in place of a mousePressEvent; test
        #this [bruce 040917]
        #print "Double clicked: ", but
        
        but = self.fix_event(event, 'press', self.mode)
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
        ## but = event.stateAfter()
        but = self.fix_event(event, 'press', self.mode)
        
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
        ## but = event.state()
        but = self.fix_event(event, 'release', self.mode)
        
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
        ## Huaicai 8/4/05. 
        self.makeCurrent()
        
        ##self.debug_event(event, 'mouseMoveEvent')
        ## but = event.state()
        but = self.fix_event(event, 'move', self.mode)
        
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

    def setDisplay(self, disp, default_display=False):
        '''Set the display mode of the GLPane, where:
            "disp" is the display mode, and
            "default_display" changes the header of the display status bar to either "Default Display" (True)
            or "Current Display (False, the default).
        '''
        
        # Fix to bug 800. Mark 050807
        if default_display:
            # Used when the user presses "Default Display" or changes the "Default Display"
            # in the preferences dialog.  
            header = "Default Display: " 
        else:
            # Used for all other purposes.
            header = "Current Display: " 
            
        if disp == diDEFAULT:
            #disp = default_display_mode #bruce 041129 to fix bug 21
            prefs = preferences.prefs_context() #mark 050802 to fix bug 799
            disp = prefs.get(defaultDisplayMode_prefs_key, default_display_mode)
        #e someday: if self.display == disp, no actual change needed??
        # not sure if that holds for all init code, so being safe for now.
        self.display = disp
        ##Huaicai 3/29/05: Add the condition to fix bug 477
        if self.mode.modename == 'COOKIE':
            self.win.dispbarLabel.setText("    ")
        else:    
            #self.win.dispbarLabel.setText( "Default Display: " + dispLabel[disp] )
            self.win.dispbarLabel.setText( header + dispLabel[disp] )
        #bruce 050415: following should no longer be needed
        # (and it wasn't enough, anyway, since missed mols in non-current parts;
        #  see comments in chunk.py about today's bugfix in molecule.draw for
        #  bug 452 item 15)
        ## for mol in self.assy.molecules:
        ##     if mol.display == diDEFAULT: mol.changeapp(1)
        return

    def setZoomFactor(self, zFactor):
            self.zoomFactor = zFactor
    def getZoomFactor(self):
            return self.zoomFactor        

    _needs_repaint = 1 #bruce 050516 experiment -- initial value is true
    
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
        self._needs_repaint = 1 #bruce 050516 experiment
        # (To restore the pre-050127 behavior, it would be sufficient to
        # change the next line from "self.update()" to "self.paintGL()".)
        self.update()
            # QWidget.update() method -- ask Qt to call self.paintGL()
            # (via some sort of paintEvent to our superclass)
            # very soon after the current event handler returns
        return

    # default values for instance variables related to glSelectBuffer feature [bruce 050608]
    ## glselect = 0 # whether we're inside a glSelectBuffer call (not presently needed)
    glselect_wanted = 0 # whether the next paintGL should start with a glSelectBuffer call [bruce 050608]
    glselectBufferSize = 10000 # guess, probably overkill, seems to work, no other value was tried
    current_glselect = False #bruce 050616 #doc; might be approx. same as above commented-out "glselect" attr #k
    
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

        env.after_op() #bruce 050908

        if not self.initialised: return

        #e Future: it might be good to set standard GL state, e.g. matrixmode, before checking self.redrawGL here,
        # in order to mitigate bugs in other code (re bug 727), but only if the current mode gets to
        # redefine what "standard GL state" means, since some modes which use this flag to avoid standard
        # repaints also maintain some GL state in nonstandard forms. [bruce 050707 comment]
        
        if not self.redrawGL: return

##        if not self._needs_repaint: #bruce 050516 experiment
##            # This probably happens fairly often when Qt calls paintGL but our own code
##            # didn't change anything and therefore didn't call gl_update.
##            # The plan is to return in this case, but until I'm sure that's safe
##            # (and/or know what else needs to be checked, like the GLPane widget size in case that changed),
##            # I'll just print a debug message about the missed chance for an optimization.
##            # (Removed message since it happens a lot, mainly when context menu is put up, window goes bg or fg, etc.
##            #  What we need is a debug pref to turn off repainting then, so we can see if it's needed on each platform.
##            #  Even if it is, we might optimize by somehow painting from the existing buffer
##            # without swapping or clearing it. ###@@@)
##            pass
####            if platform.atom_debug:
####                print_compact_stack("atom_debug: paintGL called with _needs_repaint false; needed?\n  ")

        env.redraw_counter += 1 #bruce 050825
        
        #bruce 050707 (for bond inference -- easiest place we can be sure to update bonds whenever needed)
        #bruce 050717 bugfix: always do this, not only when "self._needs_repaint"; otherwise,
        # after an atomtype change using Build's cmenu, the first redraw (caused by the cmenu going away, I guess)
        # doesn't do this, and then the bad bond (which this routine should have corrected, seeing the atomtype change)
        # gets into the display list, and then even though the bondtype change (set_v6) does invalidate the display list,
        # nothing triggers another gl_update, so the fixed bond is not drawn right away. I suppose set_v6 ought to do its own
        # gl_update, but for some reason I'm uncomfortable with that for now (and even if it did, this bugfix here is
        # probably also needed). And many analogous LL changers don't do that.
        env.post_event_updates( warn_if_needed = False)
        
        self._needs_repaint = 0 # do this now, even if we have an exception during the repaint

        #k not sure whether next two things are also needed in the split-out standard_repaint [bruce 050617]
        
        self._restore_modelview_stack_depth() #bruce 050608 moved this here (was after _setup_lighting ###k verify that)
        
        if self.need_setup_lighting:
            # I don't know if it matters to avoid calling this every time...
            # in case it's slow, we'll only do it when it might have changed.
            self.need_setup_lighting = False # set to true again if setLighting is called
            self._setup_lighting()

        if trans_feature: # if we're top glpane and doing trans feature
            part = self.part #e correct? might worry if not same as self.assy.part
            if platform.atom_debug and part is not self.assy.part:
                print "atom_debug: glpane redraw sees different self.part %r and self.assy.part %r" % (self.part,self.assy.part)
            topnode = part.topnode
            try:
                import demo_trans
                reload(demo_trans)
                rendertop = demo_trans.translate(topnode, self)
            except:
                print_compact_traceback( "glpane redraw: ignoring exception in demo_trans (using untrans form): ")
                    #e improve if module missing, or don't commit
                self.standard_repaint()
            else:
                # rendertop is the actual nodes to draw... no, not enough, need the modified render loop too... ####e
                # or can that just be inserted into the nodes for use when you draw them? if so, they also need to encode the
                # standard render loop! ie a call of standard_repaint (and self's other attrs) need passing in. well we did pass self!
                # is that enough? if so, then right now, rather than std repaint we would just call rendertop.draw! (when no exc above)
                self.rendertop = rendertop # will be needed later for mouse-event processing, maybe more ###@@@
                rendertop.draw(self, self.display)
            pass
        else:
            self.standard_repaint()
        
        glFlush()
        ##self.swapBuffers()  ##This is a redundant call, Huaicai 2/8/05
        
        return # from paintGL

    special_topnode = None #bruce 050627 only used experimentally so far

    # The following behavior (in several methods herein) related to wants_gl_update
    # should probably also be done in ThumbViews
    # if they want to get properly updated when graphics prefs change. [bruce 050804 guess] ####@@@@
    
    wants_gl_update = True #bruce 050804
        # this is set to True after we redraw, and to False by the following method

    def wants_gl_update_was_True(self): #bruce 050804
        """Outside code should call this if it changes what our redraw would draw,
        and then sees self.wants_gl_update being true,
        if it might not otherwise call self.gl_update
        (which is also ok to do, but might be slower -- whether it's actually slower is not known).
           This can also be used as an invalidator for passing to self.end_tracking_usage().
        """
        self.wants_gl_update = False
        self.gl_update()
    
    def standard_repaint(self, special_topnode = None): #bruce 050617 split this out, added arg
        ###e not sure of name or exact role; might be called on proxy for subrect?
        """#doc... this trashes both gl matrices! caller must push them both if it needs the current ones.
        this routine sets its own matrixmode but depends on other gl state being standard when entered.
        """
        self.special_topnode = special_topnode # this will be detected by assy.draw()
        match_checking_code = self.begin_tracking_usage() #bruce 050806
        try:
            try:
                self.standard_repaint_0()
            except:
                print "exception in standard_repaint_0 (being reraised)"
                    # we're not restoring stack depths here, so this will mess up callers, so we'll reraise;
                    # so the caller will print a traceback, thus we don't need to print one here. [bruce 050806]
                raise
        finally:
            self.wants_gl_update = True #bruce 050804
            self.special_topnode = None #k or old one??
            self.end_tracking_usage( match_checking_code, self.wants_gl_update_was_True ) # same invalidator even if exception
        return

    def standard_repaint_0(self):
        c = self.mode.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT )
            #e if stencil clear is expensive, we could optim and only do it when needed [bruce ca. 050615]

        
        #Huaicai 7/15/05 added this for Mark
        #The following are used to set the glpane background colors
        if self.mode.backgroundGradient:
            # vtColors = ((0.8, 0.8, 0.8), (0.8, 0.8, 0.8), (0.1, 0.2, 0.8), (0.1, 0.2, 0.8)) # "Blue Sky" gradient
            # New "Blue Sky" gradient.  Mark 051012.
            vtColors = ((0.9, 0.9, 0.9), (0.9, 0.9, 0.9), (0.33, 0.73, 1.0), (0.33, 0.73, 1.0)) 
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            drawer.drawFullWindow(vtColors)

        aspect = (self.width + 0.0)/(self.height + 0.0)
        vdist = 6.0 * self.scale
        self.vdist = vdist #bruce 050616 new feature (storing vdist in self), not yet used where it ought to be
        
        self._setup_modelview( vdist)
            #bruce 050608 moved modelview setup here, from just before the mode.Draw call

        # if GL_SELECT pass is needed (for hit test of objects with mouse), do it first.
        ###e note: if any objects moved since they were last rendered, this hit-test will still work (using their new posns),
        # but the later depth comparison (below) might not work right. See comments there for details.
        self.glselect_dict.clear()
            # this will be filled iff we do a gl_select draw,
            # then used only in the same paintGL call to alert some objects they might be the one

        if self.selobj is not None: #bruce 050702 part of fixing bug 716 (and possibly 715-5, though that's untested)
            try:
                # this 'try' might not be needed once the following method is fully implemented,
                # but it's good anyway for robustness
                if not self.mode.selobj_still_ok(self.selobj) or self.selobj_hicolor(self.selobj) is None:
                    #bruce 050822 added the selobj_hicolor test
                    self.set_selobj(None)
            except:
                # bug, but for now, don't disallow this selobj in this case
                # (message would be too verbose except for debug version)
                if platform.atom_debug:
                    print_compact_traceback("atom_debug: exception ignored: ")
                pass
            pass
        
        if self.glselect_wanted:
            wX, wY, self.targetdepth = self.glselect_wanted # wX,wY is the point to do the hit-test at
                # targetdepth is the depth buffer value to look for at that point, during ordinary drawing phase
                # (could also be used to set up clipping planes to further restrict hit-test, but this isn't yet done)
                # (Warning: targetdepth could in theory be out of date, if more events come between bareMotion
                #  and the one caused by its gl_update, whose paintGL is what's running now, and if those events
                #  move what's drawn. Maybe that could happen with mousewheel events or (someday) with keypresses
                #  having a graphical effect. Ideally we'd count intentional redraws, and disable this picking in that case.)
            self.wX, self.wY = wX,wY
            self.glselect_wanted = 0
            self.current_glselect = (wX,wY,3,3) #bruce 050615 for use by nodes which want to set up their own projection matrix
            self._setup_projection( aspect, vdist, glselect = self.current_glselect ) # option makes it use gluPickMatrix
                # replace 3,3 with 1,1? 5,5? not sure whether this will matter... in principle should have no effect except speed
            glSelectBuffer(self.glselectBufferSize)
            glRenderMode(GL_SELECT)
            glInitNames()
            ## glPushName(0) # this would be ignored if not in GL_SELECT mode, so do it after we enter that! [no longer needed]
            ## self.glselect = 1
            glMatrixMode(GL_MODELVIEW)
            try:
                self.mode.Draw() # should perhaps optim by skipping chunks based on bbox... don't know if that would help or hurt
                    # note: this might call some display lists which, when created, registered namestack names,
                    # so we need to still know those names!
            except:
                print_compact_traceback("exception in mode.Draw() during GL_SELECT; ignored; restoring modelview matrix: ")
                glMatrixMode(GL_MODELVIEW)
                self._setup_modelview( vdist) ###k correctness of this is unreviewed! ####@@@@
                # now it's important to continue, at least enough to restore other gl state
            self.current_glselect = False
            ###e On systems with no stencil buffer, I think we'd also need to draw selobj here in highlighted form
            # (in case that form is bigger than when it's not highlighted), or (easier & faster) just always pretend
            # it passes the hit test and add it to glselect_dict -- and, make sure to give it "first dibs" for being
            # the next selobj. I'll implement some of this now (untested when no stencil buffer) but not yet all. [bruce 050612]
            obj = self.selobj
            if obj is not None:
                self.glselect_dict[id(obj)] = obj
                    ###k unneeded, if the func that looks at this dict always tries selobj first
                    # (except for a kluge near "if self.glselect_dict", commented on below)
            ## self.glselect = 0
            glFlush()
            hit_records = list(glRenderMode(GL_RENDER))
            ## print "%d hits" % len(hit_records)
            for (near,far,names) in hit_records: # see example code, renderpass.py
                ## print "hit record: near,far,names:",near,far,names
                    # e.g. hit record: near,far,names: 1439181696 1453030144 (1638426L,)
                    # which proves that near/far are too far apart to give actual depth,
                    # in spite of the 1-pixel drawing window (presumably they're vertices
                    # taken from unclipped primitives, not clipped ones).
                if names:
                    # for now, len is always 0 or 1, i think; if not, best to use only the last element...
                    # tho if we ever support "name/subname paths" we'll probably let first name interpret the remaining ones.
                    ###e in fact, when nodes change projection or viewport for kids, and/or share their kids, they need to
                    # put their own names on the stack, so we'll know how to redraw the kids, or which ones are meant when shared.
                    obj = env.obj_with_glselect_name.get(names[-1]) #k should always return an obj
                    self.glselect_dict[id(obj)] = obj # now these can be rerendered specially, at the end of mode.Draw
            #e maybe we should now sort glselect_dict by "hit priority" (for depth-tiebreaking), or at least put self.selobj first.
            # (or this could be done lower down, where it's used.)
            
        self._setup_projection( aspect, vdist)

        # In the glselect_wanted case, we now know (in glselect_dict) which objects draw any pixels at the mouse position,
        # but not which one is in front (the near/far info from GL_SELECT has too wide a range to tell us that).
        # So we have to get them to tell us their depth at that point (as it was last actually drawn
            ###@@@dothat for bugfix; also selobj first)
        # (and how it compares to the prior measured depth-buffer value there, as passed in glselect_wanted,
        #  if we want to avoid selecting something when it's obscured by non-selectable drawing in front of it).
        if self.glselect_dict:
            # kluge: this is always the case if self.glselect_wanted was set and self.selobj was set,
            # since selobj is always stored in glselect_dict then; if not for that, we might need to reset
            # selobj to None here for empty glselect_dict -- not sure, not fully analyzed. [bruce 050612]
            newpicked = self.preDraw_glselect_dict() # retval is new mouseover object, or None ###k verify
            ###e now tell this obj it's picked (for highlighting), which might affect how the main draw happens.
            # or, just store it so code knows it's there, and (later) overdraw it for highlighting.
            self.set_selobj( newpicked, "newpicked")
            ###e we'll probably need to notify some observers that selobj changed (if in fact it did). ###@@@
            ## env.history.statusbar_msg("%s" % newpicked) -- messed up by depmode "click to do x" msg
        
        # otherwise don't change prior selobj -- we have a separate system to set it back to None when needed
        # (which has to be implemented in the bareMotion routines of client modes -- would self.bareMotion be better? ###@@@ review)
        
        # draw according to mode
        glMatrixMode(GL_MODELVIEW) # this is assumed within Draw methods [bruce 050608 comment]
        self.mode.Draw()

        # highlight selobj if necessary -- we redraw it now (though it was part of
        # what was just drawn above) for two reasons:
        # - it might be in a display list in non-highlighted form (and if so, the above draw used that form);
        # - we need to draw it into the stencil buffer too, so mode.bareMotion can tell when mouse is still over it.
        if self.selobj is not None:
            # draw the selobj as highlighted, and make provisions for fast test
            # (by external code) of mouse still being over it (using stencil buffer)

            # first gather info needed to know what to do -- highlight color (and whether to draw that at all)
            # and whether object might be bigger when highlighted (affects whether depth write is needed now).
            hicolor = self.selobj_hicolor( self.selobj) #bruce 050822 revised this; ###@@@ should record it from earlier test above
            # if that is None, should we act as if selobj is not still_ok?
            # guess: yes, but related code needs review.
            # I think I've now effectively implemented this separately, next to the still_ok test above.
            # [bruce 050822 comment]
            if hicolor is None:
                if platform.atom_debug:
                    print "atom_debug: probable bug: self.selobj_hicolor( self.selobj) is None for %r" % self.selobj #bruce 050822
            highlight_might_be_bigger = True # True is always ok; someday we might let some objects tell us this can be False

            # color-writing is needed here, iff the mode asked for it, for this selobj.
            highlight_into_color = (hicolor is not None)

            if highlight_into_color:
                # depth-writing is needed here, if highlight might be drawn in front of not-yet-drawn transparent surfaces
                # (like Build mode water surface) -- otherwise they will look like they're in front of some of the highlighting
                # even though they're not. (In principle, the preDraw_glselect_dict call above needs to know whether this depth
                # writing occurred ###doc why. Probably we should store it into the object itself... ###@@@ review, then doit
                highlight_into_depth = highlight_might_be_bigger
            else:
                highlight_into_depth = False ###@@@ might also need to store 0 into obj...see discussion above

            if not highlight_into_depth:
                glDepthMask(GL_FALSE) # turn off depth writing (but not depth test)
            if not highlight_into_color:
                glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE) # don't draw color pixels
                        
            # Note: stencil buffer was cleared earlier in this paintGL call.
            glStencilFunc(GL_ALWAYS, 1, 1)
                # These args make sure stencil test always passes, so color is drawn if we want it to be,
                # and so we can tell whether depth test passes in glStencilOp (even if depth *writing* is disabled ###untested);
                # this also sets reference value of 1 for use by GL_REPLACE.
                # (Args are: func to say when drawing-test passes; ref value; comparison mask.
                #  Warning: Passing -1 for reference value, to get all 1's, does not work -- it makes ref value 0!)
            glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
                # turn on stencil-buffer writing based on depth test
                # (args are: what to do on fail, zfail, zpass (see OpenGL "red book" p. 468))
            glEnable(GL_STENCIL_TEST)
                # this enables both aspects of the test: effect on drawing, and use of stencil op (I think #k);
                # apparently they can't be enabled separately
            ##print glGetIntegerv( GL_STENCIL_REF)
            
            # Now "translate the world" slightly closer to the screen,
            # to ensure depth test passes for appropriate parts of highlight-drawing
            # even if roundoff errors would make it unreliable to just let equal depths pass the test.
            # The amount of translation is a guess (ideally it should be just enough to achieve the mentioned purpose).
            # (Note: In principle, this motion towards the screen needs to be accounted for when testing depths in
            #  preDraw_glselect_dict (and we might want to store it on the object itself as a reliable record of whether
            #  it happened and for which object). In practice, as long as the stencil optim works, this isn't needed,
            #  and it's not yet implemented. This is predicted to result in highlight flickering if no stencil bits are
            #  available. ###e should fix sometime, if that ever happens.)
            
            glMatrixMode(GL_PROJECTION) # prepare to "translate the world"
            glPushMatrix() # could avoid using another matrix-stack-level if necessary, by untranslating when done
            glTranslatef(0.0, 0.0, +0.01) # move the world a bit towards the screen
                # (this works, but someday verify sign is correct in theory #k)
            glMatrixMode(GL_MODELVIEW) # probably required!
            
            ####@@@@ TODO -- rename draw_in_abs_coords and make it imply highlighting so obj knows whether to get bigger
            # (note: having it always draw selatoms bigger, as if highlighted, as it does now, would probably be ok in hit-test,
            #  since false positives in hit test are ok, but this is not used in hit test; and it's probably wrong in depth-test
            #  of glselect_dict objs (where it *is* used), resulting in "premonition of bigger size" when hit test passed... ###bug);
            # make provisions elsewhere for objs "stuck as selobj" even if tests to retain that from stencil are not done
            # (and as optim, turn off stencil drawing then if you think it probably won't be needed after last draw you'll do)
            
            self.selobj.draw_in_abs_coords(self, hicolor or black) ###@@@ test having color writing disabled here, does stencil still happen??
            
            # restore gl state (but don't do unneeded OpenGL ops in case that speeds it up somehow)
            if not highlight_into_depth:
                glDepthMask(GL_TRUE)
            if not highlight_into_color:
                glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)                
            glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
                # no need to undo glStencilFunc state, I think -- whoever cares will set it up again
                # when they reenable stenciling.
            glDisable(GL_STENCIL_TEST)
            
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW) #k maybe not needed

        self.mode.Draw_after_highlighting() # e.g. draws water surface in Build mode

        ###@@@ move remaining items back into caller? sometimes yes sometimes no... need to make them more modular... [bruce 050617]
        
        # let parts (other than the main part) draw a text label, to warn
        # the user that the main part is not being shown [bruce 050408]
        try:
            self.part.draw_text_label(self)
        except:
            if platform.atom_debug:
                print_compact_traceback( "atom_debug: exception in self.part.draw_text_label(self): " )
            pass # if it happens at all, it'll happen too often to bother users with an error message
        
        # draw coordinate-orientation arrows at upper right corner of glpane
        if self.displayCompass:
            self.drawcompass(aspect) #bruce 050608 moved this here, and rewrote it to behave then

        glMatrixMode(GL_MODELVIEW) #bruce 050707 precaution in case drawing code outside of paintGL forgets to do this
            # (see discussion in bug 727, which was caused by that)
            # (it might also be good to set mode-specific standard GL state before checking self.redrawGL in paintGL #e)
        
        return # from standard_repaint_0 (which is the central submethod of paintGL)
    
    def selobj_hicolor(self, obj): #bruce 050822 split this out
        """If obj was to be highlighted as selobj (whether or not it's presently self.selobj),
        what would its highlight color be?
        Or return None if obj should not be allowed as selobj.
        """
        try:
            hicolor = self.mode.selobj_highlight_color( obj) #e should implem noop version in basicMode [or maybe i did]
            # mode can decide whether selobj should be highlighted (return None if not), and if so, in what color
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: selobj_highlight_color exception for %r: " % obj)
            hicolor = None #bruce 050822 changed this from LEDon to None
        return hicolor
    
    selobj = None #bruce 050609

    def set_selobj(self, selobj, why = "why?"):
        if selobj is not self.selobj:
            #bruce 050702 partly address bug 715-3 (the presently-broken Build mode statusbar messages).
            # Temporary fix, since Build mode's messages are better and should be restored.
            if selobj is not None:
                try:
                    try:
                        #bruce 050806 let selobj control this
                        method = selobj.mouseover_statusbar_message # only defined for atoms, for now
                    except AttributeError:
                        msg = "%s" % (selobj,)
                    else:
                        msg = method()
                except:
                    msg = "<exception in selobj statusbar message code>"
            else:
                msg = " "
            env.history.statusbar_msg(msg)
        self.selobj = selobj
        #e notify some observers?
        return

    def preDraw_glselect_dict(self): #bruce 050609
        # We need to draw glselect_dict objects separately, so their drawing code runs now rather than in the past
        # (when some display list was being compiled), so they can notice they're in that dict.
        # We also draw them first, so that the nearest one (or one of them, if there's a tie)
        # is sure to update the depth buffer. (Then we clear it so that this drawing doesn't mess up
        # later drawing at the same depth.)
        # (If some mode with special drawing code wants to join this system, it should be refactored
        #  to store special nodes in the model which can be drawn in the standard way.)
        glMatrixMode(GL_MODELVIEW)
        glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE) # optimization -- don't draw color pixels (depth is all we need)
        newpicked = None # in case of errors, and to record found object
        # here we should sort the objs to check the ones we most want first (esp selobj)...
        #bruce 050702 try sorting this, see if it helps pick bonds rather than invis selatoms -- it seems to help.
        # This removes a bad side effect of today's earlier fix of bug 715-1.
        objects = self.glselect_dict.values()
        items = [] # (order, obj) pairs, for sorting objects
        for obj in objects:
            if obj is self.selobj:
                order = 0
            elif obj.__class__ is Bond:
                order = 1
            else:
                order = 2
            items.append((order, obj))
        items.sort()
        for orderjunk, obj in items:
            try:
                method = obj.draw_in_abs_coords
            except AttributeError:
                print "bug? ignored: %r has no draw_in_abs_coords method" % (obj,)
            else:
                try:
                    method(self, white) # draw depth info (color doesn't matter since we're not drawing pixels)
                        #bruce 050822 changed black to white in case some draw methods have boolean-test bugs for black (unlikely)
                        ###@@@ in principle, this needs bugfixes; in practice the bugs are tolerable in the short term
                        # (see longer discussion in other comments):
                        # - if no one reaches target depth, or more than one does, be smarter about what to do?
                        # - try current selobj first [this is done, as of 050702],
                        #   or give it priority in comparison - if it passes be sure to pick it
                        # - be sure to draw each obj in same way it was last drawn, esp if highlighted:
                        #    maybe drawn bigger (selatom)
                        #    moved towards screen
                    newpicked = self.check_target_depth( obj)
                        # returns obj or None -- not sure if that should be guaranteed [bruce 050822 comment]
                    if newpicked is not None:
                        break
                except:
                    print_compact_traceback("exception in %r.draw_in_abs_coords ignored: " % (obj,))
        ##e should check depth here to make sure it's near enough but not too near
        # (if too near, it means objects moved, and we should cancel this pick)
        glClear(GL_DEPTH_BUFFER_BIT) # prevent those predraws from messing up the subsequent main draws
        glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
        self.glselect_dict.clear() #k needed? even if not, seems safer this way.
            # do this now to avoid confusing the main draw methods,
            # in case they check this dict to decide whether they're
            # being called by draw_in_abs_coords
            # [which would be deprecated! but would work, not counting display lists.]
        #bruce 050822 new feature: objects which had no highlight color should not be allowed in self.selobj
        # (to make sure they can't be operated on without user intending this),
        # though they should still obscure other objects.
        if newpicked is not None:
            hicolor = self.selobj_hicolor( newpicked)
            if hicolor is None:
                newpicked = None
        return newpicked # might be None in case of errors

    def check_target_depth(self, candidate): #bruce 050609; tolerance revised 050702
        """[private helper method]
           WARNING: docstring is obsolete -- no newpicked anymore, retval details differ: ###@@@
        Candidate is an object which drew at the mouse position during GL_SELECT drawing mode
        (using the given gl_select name), and which (1) has now noticed this, via its entry in self.glselect_dict
        (which was made when GL_SELECT mode was exited; as of 050609 this is in the same paintGL call as we're in now),
        and (2) has already drawn into the depth buffer during normal rendering (or an earlier rendering pass).
        (It doesn't matter whether it's already drawn into the color buffer when it calls this method.)
           We should read pixels from the depth buffer (after glFlush)
        to check whether it has just reached self.targetdepth at the appropriate point,
        which would mean candidate is the actual newly picked object.
           If so, record this fact and return True, else return False.
        We might quickly return False (checking nothing) if we already returned True in the same pass,
        or we might read pixels anyway for debugging or assertions.
           It's possible to read a depth even nearer than targetdepth, if the drawing passes round
        their coordinates differently (as the use of gluPickMatrix for GL_SELECT is likely to do),
        or if events between the initial targetdepth measurement and this redraw tell any model objects to move.
        Someday we should check for this.
        """
        glFlush()
        wX, wY = self.wX, self.wY
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        newdepth = wZ[0][0]
        targetdepth = self.targetdepth
        ####@@@@ here we could effectively move selobj forwards... warning: worry about scales of coord systems in doing that...
        # due to that issue it is probably be easier to fix this when drawing it, instead
        if newdepth <= targetdepth + 0.0001: # use fudge factor in case of roundoff errors
            # [bruce 050702: 0.000001 was not enough! 0.00003 or more was needed, to properly highlight some bonds
            #  which became too hard to highlight after today's initial fix of bug 715-1.]
            #e could check for newdepth being < targetdepth - 0.002 (error), but best
            # to just let caller do that (NIM), since we would often not catch this error anyway,
            # since we're turning into noop on first success
            # (no choice unless we re-cleared depth buffer now, which btw we could do... #e).
            ## print "target depth reached by",candidate,newdepth , targetdepth
            return candidate
                # caller should not call us again without clearing depth buffer,
                # otherwise we'll keep returning every object even if its true depth is too high
        ## print "target depth NOT reached by",candidate,newdepth , targetdepth
        return None

    def _restore_modelview_stack_depth(self): #bruce 050608 split this out
        "restore GL_MODELVIEW_STACK_DEPTH to 1, if necessary"
        #bruce 040923: I'd like to reset the OpenGL state
        # completely, here, incl the stack depths, to mitigate some
        # bugs. How??  Note that there might be some OpenGL init code
        # earlier which I'll have to not mess up. Incl displaylists in
        # drawer.setup.  What I ended up doing is just to measure the
        # stack depth and pop it 0 or more times to make the depth 1.
        #   BTW I don't know for sure whether this causes a significant speed
        # hit for some OpenGL implementations (esp. X windows)...
        # test sometime. #e
        glMatrixMode(GL_MODELVIEW)
        
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
        return

    def _setup_modelview(self, vdist): #bruce 050608 split this out; 050615 added explanatory comments
        "set up modelview coordinate system"
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef( 0.0, 0.0, - vdist)
            # [bruce comment 050615]
            # translate coords for drawing, away from eye (through sreen and beyond it) by vdist;
            # this places origin at desired position in eyespace for "center of view" (and for center of trackball rotation).
            
            # bruce 041214 comment: some code assumes vdist is always 6.0 * self.scale
            # (e.g. eyeball computations, see bug 30), thus has bugs for aspect < 1.0.
            # We should have glpane attrs for aspect, w_scale, h_scale, eyeball,
            # clipping planes, etc, like we do now for right, up, etc. ###e

        q = self.quat 
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z) # rotate those coords by the trackball quat
        glTranslatef( self.pov[0], self.pov[1], self.pov[2]) # and translate them by -cov, to bring cov (center of view) to origin
        return

    def _setup_projection(self, aspect, vdist, glselect = False): #bruce 050608 split this out; 050615 revised docstring
        """Set up standard projection matrix contents using aspect, vdist, and some attributes of self.
        (Warning: leaves matrixmode as GL_PROJECTION.)
        Optional arg glselect should be False (default) or a 4-tuple (to prepare for GL_SELECT picking).
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        scalezoom = self.scale * self.zoomFactor #bruce 050608 used this to clarify following code
        near, far = self.near, self.far

        if glselect:
            x,y,w,h = glselect
            gluPickMatrix(
                    x,y,
                    w,h,
                    glGetIntegerv( GL_VIEWPORT ) #k is this arg needed? it might be the default...
            )
         
        if self.ortho:
            glOrtho( - scalezoom * aspect, scalezoom * aspect,
                     - scalezoom,          scalezoom,
                       vdist * near, vdist * far )
        else:
            glFrustum( - scalezoom * near * aspect, scalezoom * near * aspect,
                       - scalezoom * near,          scalezoom * near,
                         vdist * near, vdist * far)
        return

    def drawcompass(self, aspect):
        """Draw the "compass" (the perpendicular colored arrows showing orientation of model coordinates)
        in a corner of the GLPane specified by preference variables.
        No longer assumes a specific glMatrixMode, but sets it to GL_MODELVIEW on exit.
        No longer trashes either matrix, but does require enough GL_PROJECTION stack depth
        to do glPushMatrix on it (though the guaranteed depth for that stack is only 2).
        """
        #bruce 050608 improved behavior re GL state requirements and side effects; 050707 revised docstring accordingly.
        #mark 0510230 switched Y and Z colors.  Now X = red, Y = green, Z = blue, standard in all CAD programs.
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity() #k needed?
        
        # Set compass position using glOrtho
        if self.compassPosition == UPPER_RIGHT:
            glOrtho(-50*aspect, 5.5*aspect, -50, 5.5,  -5, 500) # Upper Right
        elif self.compassPosition == UPPER_LEFT:
            glOrtho(-5*aspect, 50.5*aspect, -50, 5.5,  -5, 500) # Upper Left
        elif self.compassPosition == LOWER_LEFT:
            glOrtho(-5*aspect, 50.5*aspect, -5, 50.5,  -5, 500) # Lower Left
        else:
            glOrtho(-50*aspect, 5.5*aspect, -5, 50.5,  -5, 500) # Lower Right
        
        q = self.quat
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)
        glEnable(GL_COLOR_MATERIAL)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDisable(GL_CULL_FACE)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # X Arrow (Red)      
        glePolyCone([[-1,0,0], [0,0,0], [4,0,0], [3,0,0], [5,0,0], [6,0,0]],
                    [[0,0,0], [1,0,0], [1,0,0], [.5,0,0], [.5,0,0], [0,0,0]],
                    [.3,.3,.3,.75,0,0])
        
        # Y Arrow (Green) 
        glePolyCone([[0,-1,0], [0,0,0], [0,4,0], [0,3,0], [0,5,0], [0,6,0]],
                    [[0,0,0], [0,.9,0], [0,.9,0], [0,.4,0], [0,.4,0], [0,0,0]],
                    [.3,.3,.3,.75,0,0])
        
        # Z Arrow (Blue)
        glePolyCone([[0,0,-1], [0,0,0], [0,0,4], [0,0,3], [0,0,5], [0,0,6]],
                    [[0,0,0], [0,0,1], [0,0,1], [0,0,.4], [0,0,.4], [0,0,0]],
                    [.3,.3,.3,.75,0,0])
                    
        glEnable(GL_CULL_FACE)
        glDisable(GL_COLOR_MATERIAL)
           
        ##Adding "X, Y, Z" text labels for Axis. By test, the following code will get
        # segmentation fault on Mandrake Linux 10.0 with libqt3-3.2.3-17mdk
        # or other 3.2.* versions, but works with libqt3-3.3.3-26mdk. Huaicai 1/15/05
           
        if True:###sys.platform in ['darwin', 'win32']:
                glDisable(GL_LIGHTING)
                glDisable(GL_DEPTH_TEST)
                ## glPushMatrix()
                font = QFont( QString("Helvetica"), 12)
                self.qglColor(QColor(200, 75, 75)) # Dark Red
                self.renderText(5.3, 0.0, 0.0, QString("x"), font)
                self.qglColor(QColor(25, 100, 25)) # Dark Green
                self.renderText(0.0, 4.8, 0.0, QString("y"), font)
                self.qglColor(QColor(50, 50, 200)) # Dark Blue
                self.renderText(0.0, 0.0, 5.0, QString("z"), font)
                ## glPopMatrix()
                glEnable(GL_DEPTH_TEST)
                glEnable(GL_LIGHTING)

        #bruce 050707 switched order to leave ending matrixmode in standard state, GL_MODELVIEW
        # (though it doesn't matter for present calling code; see discussion in bug 727)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        return
           
    def resizeGL(self, width, height):
        """Called by QtGL when the drawing window is resized.
        """
        self.width = width
        self.height = height
           
	## glViewport(10, 15, (self.width-10)/2, (self.height-15)/3)######@@@@@@@@
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

    def makemenu(self, menu_spec):
        # this overrides the one from DebugMenuMixin (with the same code), but that's ok,
        # since we want to be self-contained in case someone later removes that mixin class;
        # this method is called by our modes to make their context menus.
        # [bruce 050418 comment]
        return makemenu_helper(self, menu_spec)
    
    def debug_menu_items(self): #bruce 050515 experiment
        "overrides method from DebugMenuMixin"
        super = DebugMenuMixin
        usual = super.debug_menu_items(self)
            # list of (text, callable) pairs, None for separator
        ours = list(usual)
        try:
            # submenu for available custom modes [bruce 050515]
            #e should add special text to the item for current mode (if any) saying we'll reload it
            modemenu = []
            for modename, modefile in self.custom_mode_names_files():
                modemenu.append(( modename,
                                  lambda arg1 = None, arg2 = None, modename = modename, modefile = modefile:
                                    self.enter_custom_mode(modename, modefile) # not sure how many args are passed
                                ))
            if modemenu:
                ours.append(("custom modes", modemenu))
        except:
            print_compact_traceback("exception ignored: ")
        return ours

    def custom_mode_names_files(self):
        modes_dir = os.path.join( self.win.tmpFilePath, "Modes")
        if not os.path.isdir( modes_dir):
            return []
        res = []
        for file in os.listdir( modes_dir):
            if file.endswith('.py'):
                modename, ext = os.path.splitext(file)
                modefile = os.path.join( modes_dir, file)
                res.append(( modename, modefile ))
        return res

    def enter_custom_mode( self, modename, modefile): #bruce 050515 experiment
        fn = modefile
        if not os.path.exists(fn):
            env.history.message("should never happen: file does not exist: [%s]" % fn)
            return
        dir, file = os.path.split(fn)
        base, ext = os.path.splitext(file)
        ## modename = base
        ###e need better way to import from this specific file!
        # (Like using an appropriate function in the import-related Python library module.)
        # This kluge is not protected against weird chars in base.
        if dir not in sys.path:
            sys.path.append(dir)
        exec("import %s as _module" % (base,)) ###e use the platform or debug func to limit this to GPL versions
        reload(_module)
        exec("from %s import %s as _modeclass" % (base,base))
        modeobj = _modeclass(self) # this should put it into self.modetab under the name defined in the mode module
        self.modetab[modename] = modeobj # also put it in under this name, if different [### will this cause bugs?]
        self.setMode(modename)
        return

    pass # end of class GLPane

# end