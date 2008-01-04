# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPane.py -- NE1's main model view, based on Qt's OpenGL widget.

Mostly written by Josh; partly revised by Bruce for mode code revision, 040922-24.
Revised by many other developers since then (and perhaps before).

$Id$

Module classification: [bruce 080104]

It's graphics/widgets, but this is not as obvious as it sounds.
It is "optimistic", as if we'd already refactored -- it's not fully
accurate today.

Refactoring needed: [bruce 080104]

- split into several classes (either an inheritance tree, or cooperating
objects);

- move more common code into GLPane_minimal;

- most urgently, make the main GLPane not be the
same object as the CommandSequencer.

Some of this might be a prerequisite for some ways of
optimizing the graphics code.

"""

import math
import os
import sys
import time

from PyQt4.Qt import QPalette
from PyQt4.Qt import QColor
from PyQt4.Qt import QEvent
from PyQt4.Qt import QMouseEvent
from PyQt4.Qt import QHelpEvent
from PyQt4.Qt import QPoint

from PyQt4.Qt import Qt, QFont, QMessageBox, QString
from PyQt4.Qt import SIGNAL, QTimer
from PyQt4.Qt import QGLWidget


from OpenGL.GL import glGenLists
from OpenGL.GL import glNewList
from OpenGL.GL import glEndList
from OpenGL.GL import glCallList
from OpenGL.GL import glDepthFunc
from OpenGL.GL import GL_STENCIL_BITS
from OpenGL.GL import GL_NORMALIZE
from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import GL_SMOOTH
from OpenGL.GL import glShadeModel
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import glEnable
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import GL_DEPTH_COMPONENT
from OpenGL.GL import glReadPixelsf
from OpenGL.GL import GL_LEQUAL
from OpenGL.GL import GL_MODELVIEW_STACK_DEPTH
from OpenGL.GL import glGetInteger
from OpenGL.GL import glClearColor
from OpenGL.GL import GL_COLOR_BUFFER_BIT
from OpenGL.GL import GL_STENCIL_BUFFER_BIT
from OpenGL.GL import glSelectBuffer
from OpenGL.GL import GL_SELECT
from OpenGL.GL import glRenderMode
from OpenGL.GL import glInitNames
from OpenGL.GL import glFlush
from OpenGL.GL import GL_RENDER
from OpenGL.GL import glDepthMask
from OpenGL.GL import GL_ALWAYS
from OpenGL.GL import glStencilFunc
from OpenGL.GL import GL_KEEP
from OpenGL.GL import GL_REPLACE
from OpenGL.GL import glStencilOp
from OpenGL.GL import GL_STENCIL_TEST
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glDisable
from OpenGL.GL import glPopMatrix
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_FALSE
from OpenGL.GL import glColorMask
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import glClear
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_VIEWPORT
from OpenGL.GL import glGetIntegerv
from OpenGL.GL import glFrustum
from OpenGL.GL import glOrtho
from OpenGL.GL import glRotatef
from OpenGL.GL import GL_COLOR_MATERIAL
from OpenGL.GL import GL_FILL
from OpenGL.GL import GL_FRONT_AND_BACK
from OpenGL.GL import glPolygonMode
from OpenGL.GL import GL_AMBIENT_AND_DIFFUSE
from OpenGL.GL import glColorMaterial
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glViewport
from OpenGL.GL import GL_RGB
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import glReadPixels
from OpenGL.GL import glRasterPos3f
from OpenGL.GL import GL_CURRENT_RASTER_POSITION_VALID
from OpenGL.GL import glGetBooleanv
from OpenGL.GL import glDrawPixels

from OpenGL.GLU import gluUnProject, gluPickMatrix

try:
    from OpenGL.GLE import glePolyCone
except:
    print "GLE module can't be imported. Now trying _GLE"
    from OpenGL._GLE import glePolyCone

from VQT import V, Q, A, norm, vlen
from Numeric import dot
import drawer

from modifyMode      import modifyMode
from cookieMode      import cookieMode 
from extrudeMode     import extrudeMode
from fusechunksMode  import fusechunksMode
from selectMolsMode  import selectMolsMode
from selectAtomsMode import selectAtomsMode
from depositMode     import depositMode
from PasteMode       import PasteMode
from PartLibraryMode import PartLibraryMode
from movieMode       import movieMode
from ZoomMode        import ZoomMode
from PanMode         import PanMode
from RotateMode      import RotateMode
from LineMode        import LineMode
from DnaLineMode     import DnaLineMode
from DnaDuplex_EditCommand import DnaDuplex_EditCommand
from Plane_EditCommand     import Plane_EditCommand
from RotaryMotor_EditCommand import RotaryMotor_EditCommand
from LinearMotor_EditCommand import LinearMotor_EditCommand
#from SketchMode    import SketchMode #Not implemented yet - 2007-10-25
from CommandSequencer import modeMixin

import platform

from utilities.Log import greenmsg, redmsg, orangemsg
from PlatformDependent import fix_event_helper
from PlatformDependent import wrap_key_event
from widgets import makemenu_helper
from DebugMenuMixin import DebugMenuMixin
from debug import print_compact_traceback, print_compact_stack
import preferences
import env
from changes import SubUsageTrackingMixin

from DynamicTip import DynamicTip

from state_utils import transclose

from prefs_constants import glpane_lights_prefs_key
from prefs_constants import compassPosition_prefs_key
from prefs_constants import defaultProjection_prefs_key
from prefs_constants import defaultDisplayMode_prefs_key
from prefs_constants import backgroundColor_prefs_key
from prefs_constants import backgroundGradient_prefs_key
from prefs_constants import animateStandardViews_prefs_key
from prefs_constants import animateMaximumTime_prefs_key
from prefs_constants import light1Color_prefs_key
from prefs_constants import light2Color_prefs_key
from prefs_constants import light3Color_prefs_key
from prefs_constants import displayCompass_prefs_key
from prefs_constants import displayOriginAxis_prefs_key
from prefs_constants import displayOriginAsSmallAxis_prefs_key
from prefs_constants import UPPER_RIGHT
from prefs_constants import UPPER_LEFT
from prefs_constants import LOWER_LEFT
from prefs_constants import displayCompassLabels_prefs_key

from constants import diDEFAULT
from constants import dispLabel
from constants import GL_FAR_Z
from constants import bluesky
from constants import white
from constants import MULTIPANE_GUI

from debug_prefs import Choice
from debug_prefs import Choice_boolean_False
from debug_prefs import debug_pref

from GLPane_minimal import GLPane_minimal

import qt4transition

# suspicious imports [should not really be needed, according to bruce 070919]
from bonds import Bond # used only for selobj ordering


debug_lighting = False #bruce 050418

debug_set_selobj = False # do not commit with true


paneno = 0
#  ... what a Pane ...

## normalGridLines = (0.0, 0.0, 0.6) # bruce 050410 removed this, and related code

pi2 = math.pi/2.0
pi3 = math.pi/3.0
pi4 = math.pi/4.0
xquats = [Q(1,0,0,0), Q(V(0,0,1),pi2), Q(V(0,0,1),math.pi), Q(V(0,0,1),-pi2),
          Q(V(0,0,1),pi4), Q(V(0,0,1),3*pi4),
          Q(V(0,0,1),-pi4), Q(V(0,0,1),-3*pi4)]
pquats = [Q(1,0,0,0), Q(V(0,1,0),pi2), Q(V(0,1,0),math.pi), Q(V(0,1,0),-pi2), 
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
xquats = [Q(1,0,0,0), Q(V(0,0,1),pi3), Q(V(0,0,1),2*pi3), Q(V(0,0,1),math.pi),
          Q(V(0,0,1),-pi3), Q(V(0,0,1),-2*pi3)]
pquats = [Q(V(0,1,0),pi4), Q(V(0,1,0),3*pi4),
          Q(V(0,1,0),-pi4), Q(V(0,1,0),-3*pi4)]

quats111 = []
for q in pquats:
    for q1 in xquats:
        quats111 += [(q+cq+q1, 2), (q-cq+q1, 2)]

allQuats = quats100 + quats110 + quats111

MIN_REPAINT_TIME = 0.01 # minimum time to repaint (in seconds)

## button_names = {0:None, 1:'LMB', 2:'RMB', 4:'MMB'} 
button_names = {Qt.NoButton:None, Qt.LeftButton:'LMB', Qt.RightButton:'RMB', Qt.MidButton:'MMB'}
    #bruce 070328 renamed this from 'button' (only in Qt4 branch), and changed the dict keys from ints to symbolic constants,
    # and changed the usage from dict lookup to iteration over items, to fix some cursor icon bugs.
    # For the constants, see http://www.riverbankcomputing.com/Docs/PyQt4/html/qmouseevent.html
    # [Note: if there is an import of GLPane.button elsewhere, that'll crash now due to the renaming. Unfortunately, for such
    #  a common word, it's not practical to find out except by renaming it and seeing if that causes bugs.]

# ==

class GLPane_mixin_for_DisplistChunk(object): #bruce 070110 moved this here from exprs/DisplistChunk.py and made GLPane inherit it
    """
    Private mixin class for GLPane. Attr and method names must not interfere with GLPane.
    Likely to be merged into class GLPane in future (as directly included methods rather than a mixin superclass).
    """
    compiling_displist = 0 #e rename to be private? probably not.
    compiling_displist_owned_by = None
    def glGenLists(self, *args):
        return glGenLists(*args)
    def glNewList(self, listname, mode, owner = None):
        """
        Execute glNewList, after verifying args are ok and we don't think we're compiling a display list now.
        (The OpenGL call is illegal if we're *actually* compiling one now. Even if it detects that error (as is likely),
        it's not a redundant check, since our internal flag about whether we're compiling one could be wrong.)
           If owner is provided, record it privately (until glEndList) as the owner of the display list being compiled.
        This allows information to be tracked in owner or using it, like the set of sublists directly called by owner's list.
        Any initialization of tracking info in owner is up to our caller.###k doit
        """
        #e make our GL context current? no need -- callers already had to know that to safely call the original form of glNewList
        #e assert it's current? yes -- might catch old bugs -- but not yet practical to do.
        assert self.compiling_displist == 0
        assert self.compiling_displist_owned_by is None
        assert listname
        glNewList(listname, mode)
        self.compiling_displist = listname
        self.compiling_displist_owned_by = owner # optional arg in general, but required for the tracking done in this module
        return
    def glEndList(self, listname = None):
        assert self.compiling_displist != 0
        if listname is not None: # optional arg
            assert listname == self.compiling_displist
        glEndList() # no arg is permitted
        self.compiling_displist = 0
        self.compiling_displist_owned_by = None
        return
    def glCallList(self, listname):
        """
        Compile a call to the given display list.
        Note: most error checking and any extra tracking is responsibility of caller.
        """
        ##e in future, could merge successive calls into one call of multiple lists
        ## assert not self.compiling_displist # redundant with OpenGL only if we have no bugs in maintaining it, so worth checking
            # above was WRONG -- what was I thinking? This is permitted, and we'll need it whenever one displist can call another.
            # (And I'm surprised I didn't encounter it before -- did I still never try an MT with displists?)
            # (Did I mean to put this into some other method? or into only certain uses of this method??
            # For now, do an info print, in case sometimes this does indicate an error, and since it's useful
            # for analyzing whether nested displists are behaving as expected. [bruce 070203]
        if self.compiling_displist and debug_pref("GLPane: print nested displist compiles?", Choice_boolean_False, prefs_key = True):
            print "debug: fyi: displist %r is compiling a call to displist %r" % (self.compiling_displist, listname)
        assert listname # redundant with following?
        glCallList(listname)
        return
    def ensure_dlist_ready_to_call( self, dlist_owner_1 ): #e rename the local vars, revise term "owner" in it [070102 cmt]
        """
        [private helper method for use by DisplistChunk]
           This implements the recursive algorithm described in DisplistChunk.__doc__.
        dlist_owner_1 should be a DisplistOwner ###term; we use private attrs and/or methods of that class,
        including _key, _recompile_if_needed_and_return_sublists_dict().
           What we do: make sure that dlist_owner_1's display list can be safely called (executed) right after we return,
        with all displists that will call (directly or indirectly) up to date (in their content).
           Note that, in general, we won't know which displists will be called by a given one
        until after we've updated its content (and thereby compiled calls to those displists as part of its content).
           Assume we are only called when our GL context is current and we're not presently compiling a displist in it.
        """
        ###e verify our GL context is current, or make it so; not needed now since only called during some widget's draw call
        assert self.compiling_displist == 0
        toscan = { dlist_owner_1._key : dlist_owner_1 }
        def collector( obj1, dict1):
            dlist_owner = obj1
            direct_sublists_dict = dlist_owner._recompile_if_needed_and_return_sublists_dict() # [renamed from _ensure_self_updated]
                # This says to dlist_owner: if your list is invalid, recompile it (and set your flag saying it's valid);
                # then you know your direct sublists, so we can ask you to return them.
                #   Note: it only has to include sublists whose drawing effects might be invalid.
                # This means, if its own effects are valid, it can optim by just returning {}.
                # [#e Someday it might maintain a dict of invalid sublists and return that. Right now it returns none or all of them.]
                #   Note: during that call, the glpane (self) is modified to know which dlist_owner's list is being compiled.
            dict1.update( direct_sublists_dict )
        seen = transclose(  toscan, collector )
        # now, for each dlist_owner we saw, tell it its drawing effects are valid.
        for dlist_owner in seen.itervalues():
            dlist_owner._your_drawing_effects_are_valid()
                # Q: this resets flags which cause inval propogation... does it retain consistency?
                # A: it does it in reverse logic dir and reverse arrow dir (due to transclose) as inval prop, so it's ok.
                # Note: that comment won't be understandable in a month [from 070102]. Need to explain it better. ####doc
        return
    pass # end of class GLPane_mixin_for_DisplistChunk

# ==

class GLPane(GLPane_minimal, modeMixin, DebugMenuMixin, SubUsageTrackingMixin, GLPane_mixin_for_DisplistChunk, object):
    """
    Mouse input and graphics output in the main view window.
    """
    # bruce 070920 added object superclass, to make this a new-style class
    # (so I can use a property in it)

    # Note: classes GLPane and ThumbView share lots of code,
    # which ought to be merged into their common superclass GLPane_minimal
    # (currently empty). [bruce 070914 comment]

    # Note: external code expects self.graphicsMode to always be a working
    # GraphicsMode object, which has certain callable methods [which should
    # be formalized as a new class GraphicsMode_API or so]. Similarly, it
    # expects self.currentCommand to be a Command object, and self.mode
    # to be an object that meets both APIs (for compatibility with old modes
    # which are basicMode subclasses). The Command API of self.mode (and
    # some private aspects of our commands/modes) are used by self.modeMixin
    # to "switch between modes". Soon, the modeMixin part will become part of
    # the planned Command Sequencer and be removed from this class GLPane
    # [that's partly done as of 071030, since it's now in CommandSequencer.py],
    # and the Command and GraphicsMode class hierarchies will be separated.
    # Of the attributes mentioned, only self.graphicsMode will remain in GLPane.
    # [bruce 071011]

    # class constants (needed by modeMixin to map commandNames to mode classes):
    mode_classes = [selectMolsMode, selectAtomsMode, modifyMode, depositMode,
                    cookieMode, extrudeMode, fusechunksMode,
                    movieMode, ZoomMode, PanMode, RotateMode, 
                    PasteMode, PartLibraryMode, 
                    LineMode, DnaLineMode, DnaDuplex_EditCommand,
                    Plane_EditCommand,
                    LinearMotor_EditCommand,
                    RotaryMotor_EditCommand]
                    ##SketchMode] #Sketchmode not implemented yet

    always_draw_hotspot = False #bruce 060627; not really needed, added for compatibility with class ThumbView

    def __init__(self, assy, parent = None, name = None, win = None):

        shareWidget = None
        useStencilBuffer = True

        GLPane_minimal.__init__(self, parent, shareWidget, useStencilBuffer)
        self.win = win

        modeMixin._init_modeMixin(self)

        self.partWindow = parent

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



        # Other "current preference" attributes. ###e Maybe some of these should
        # also be part-specific and/or saved in the mmp file? [bruce 050418]

        # clipping planes, as percentage of distance from the eye
        self.near = 0.25 # After testing, this is much, much better.  Mark 060116. [Prior value was 0.66 -- bruce 060124 comment]
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

        # Cursor position of the last timer event. Mark 060818
        self.timer_event_last_xy = (0, 0)

        self.setMouseTracking(True)

        # bruce 041220 let the GLPane have the keyboard focus, to fix bugs.
        # See comments above our keyPressEvent method.
        ###e I did not yet review  the choice of StrongFocus in the Qt docs,
        # just copied it from MWsemantics.
        self.setFocusPolicy(Qt.StrongFocus)

##        self.singlet = None #bruce 060220 zapping this, seems to be old and to no longer be used
        self.selatom = None # josh 10/11/04 supports depositMode

        self.jigSelectionEnabled = True # mark 060312

        self.is_animating = False # mark 060404
            # Set to True while animating between views in animateToView() so that update_selobj() in
            # selectAtomsMode will not hover highlight objects under the cursor. mark 060404

        # [bruce 050608]
        self.glselect_dict = {} # only used within individual runs
            # see also env.obj_with_glselect_name

        self._last_few_repaint_times = []
            # repaint times will be appended to this,
            # but it will be trimmed to keep only the last 5 (or fewer) times
        self._repaint_duration = MIN_REPAINT_TIME

        self.triggerBareMotionEvent = True 
            # Supports timerEvent() to minimize calls to bareMotion(). Mark 060814.

        self.cursorMotionlessStartTime = time.time() #bruce 070110 fix bug when debug_pref turns off glpane timer from startup

        ###### User Preference initialization ##############################

        # Get glpane related settings from prefs db.
        # Default values are set in "prefs_table" in prefs_constants.py.
        # Mark 050919.

        # (Note: if we wanted concurrent sessions to share bgcolor pref,
        # then besides this, we'd also need to clear the prefs cache for
        # this key... and update it more often.)
        self.backgroundColor = env.prefs[backgroundColor_prefs_key]
        self.backgroundGradient = env.prefs[backgroundGradient_prefs_key]

        self.compassPosition = env.prefs[compassPosition_prefs_key]
        self.ortho = env.prefs[defaultProjection_prefs_key]
        # This updates the checkmark in the View menu. Fixes bug #996 Mark 050925.
        self.setViewProjection(self.ortho) 

        # default display form for objects in the window even tho there is only one assembly to a window,
        # this is here in anticipation of being able to have multiple windows on the same assembly.
        # Start the GLPane's current display mode in "Default Display Mode" (pref).
        self.displayMode = env.prefs[defaultDisplayMode_prefs_key]
        #self.win.statusBar().dispbarLabel.setText( "Current Display: " + dispLabel[self.displayMode] )

        ###### End of User Preference initialization ########################## 

        self.makeCurrent()

        ## drawer.setup_drawer()
        self._setup_display_lists() # defined in GLPane_minimal. [bruce 071030]

        self.setAssy(assy) # leaves self.currentCommand/self.graphicsMode as nullmode, as of 050911

        self.loadLighting() #bruce 050311
        #bruce question 051212: why doesn't this prevent bug 1204 in use of lighting directions on startup?

        self.dynamicToolTip = DynamicTip(self)

        self.add_whats_this_text()

        # Triple-click Timer: for the purpose of implementing a triple-click
        #                     event handler, which is not supported by Qt.
        #
        # See: mouseTripleClickEvent()

        self.tripleClick       =  False
        self.tripleClickTimer  =  QTimer(self)
        self.tripleClickTimer.setSingleShot(True)
        self.connect(self.tripleClickTimer, SIGNAL('timeout()'), self._tripleClickTimeout)

        return # from GLPane.__init__ 

    def should_draw_valence_errors(self):
        """
        [overrides GLPane_minimal method]
        """
        return True

    def add_whats_this_text(self):
        """
        Adds What's This description to this glpane.
        """
        # We must do this here (and not in whatsthis.py) because in the future
        # there will be multiple part windows, each with its own glpane.
        # Problem - I don't believe this text is processed by fix_whatsthis_text_and_links()
        # in whatsthis.py. Discuss this with Bruce. Mark 2007-06-01

        if sys.platform == "darwin":
            ctrl_or_cmd = "Cmd"
        else:
            ctrl_or_cmd = "Ctrl"

        glpaneText = \
                   "<u><b>3D Graphics Area</b></u><br> "\
                   "<br>This is where the action is."\
                   "<p><b>Mouse Button Commands :</b><br> "\
                   "<br> "\
                   "<b>Left Mouse Button (LMB)</b> - Select<br> "\
                   "<b>LMB + Shift</b> - add to current selection <br> "\
                   "<b>LMB + " + ctrl_or_cmd + "</b> - remove from current selection <br> "\
                   "<b>LMB + Shift + " + ctrl_or_cmd + "</b> - delete highlighted object <br> "\
                   "<br> "\
                   "<b>Middle Mouse Button (MMB)</b> - Rotate view <br> "\
                   "<b>MMB + Shift</b> - Pan view <br> "\
                   "<b>MMB + " + ctrl_or_cmd + "</b> - Rotate view around POV Axis <br> "\
                   "<br> "\
                   "<b>Right Mouse Button (RMB)</b> - Display context-sensitive menus "\
                   "</p>"

        self.setWhatsThis(glpaneText)
    
    # ==
    
    def renderTextNearCursor(self, textString):
        """
        Renders text near the cursor position, on the top right side of the
        cursor (slightly above it).

        See example in DNA Line mode.

        @param textString: string
        
        @see: DnaLineMode.Draw
        @see: self._getFontForTextNearCursor
        """
        pos = self.cursor().pos()  
        # x, y coordinates need to be in window coordinate system. 
        # See QGLWidget.mapToGlobal for more details.
        pos = self.mapFromGlobal(pos)
        
        # Important to turn off the lighting. Otherwise the text color would 
        # be dull and may also become even more light if some other object 
        # is rendered as a transparent object. Example in DNA Line mode, when the
        # second axis end sphere is rendered as a transparent sphere, it affects
        # the text rendering as well (if GL_Lighting is not disabled)
        # [-- Ninad 2007-12-03]
        glDisable(GL_LIGHTING)
              
        # Note: It is necessary to set the font color, otherwise it may change!
        self.qglColor(QColor(0, 0, 0))
        x = pos.x() + 5
        y = pos.y() - 5
        
        # Note: self.renderText is QGLWidget.renderText method.
        self.renderText(x,
                        y,
                        QString(textString),
                        self._getFontForTextNearCursor())
        self.qglClearColor(QColor(0, 0, 0))
            # question: is this related to glClearColor? [bruce 071214 question]
        glEnable(GL_LIGHTING)
    
    def _getFontForTextNearCursor(self):
        """
        Returns the font for text near the cursor. 
        @see: self.renderTextNearCursor
        """
        font = QFont("Arial", 10)
        ##font.setBold(True)
        ##font.setPixelSize(15)                
        return font

    # == Background color helper methods. Moved here from basicMode (modes.py). Mark 060814.

    def restoreDefaultBackground(self):
        """
        Restore the default background color and gradient (Sky Blue).
        Always do a gl_update.
        """
        env.prefs.restore_defaults([
            backgroundColor_prefs_key, 
            backgroundGradient_prefs_key, 
        ])

        self.setBackgroundColor(env.prefs[ backgroundColor_prefs_key ])
        self.setBackgroundGradient(env.prefs[ backgroundGradient_prefs_key ] )
        self.gl_update()

    def setBackgroundColor(self, color): # bruce 050105 new feature [bruce 050117 cleaned it up]
        """
        Sets the mode\'s background color and stores it in the prefs db.
        """
        self.backgroundColor = color
        env.prefs[ backgroundColor_prefs_key ] = color
        return

    def setBackgroundGradient(self, gradient): # mark 050808 new feature
        """
        Stores the background gradient prefs value in the prefs db.
        gradient can be either:
            0 - the background color is used to fill the GLPane.
            1 - the background gradient is set to a 'Blue Sky' gradient.

        See GLPane.standard_repaint_0() to see how this is used when redrawing the glpane.
        """
        self.backgroundGradient = gradient
        env.prefs[ backgroundGradient_prefs_key ] = gradient
        return

    # self.part maintenance [bruce 050419]

    def set_part(self, part):
        """
        change our current part to the one given, and take on that part's view;
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
        """
        [public]
        if you know about this part, forget about it (call this from dying parts)
        """
        if self.part is part:
            self.set_part(None)
        return

    def _close_part(self):
        """
        [private]
        save our current view into self.part [if not None] and forget about self.part
        """
        if self.part:
            self._saveLastViewIntoPart( self.part)
        self.part = None

    def _open_part(self):
        """
        [private]
        after something set self.part, load our current view from it
        """
        if self.part:
            self._setInitialViewFromPart( self.part)
        # else our current view doesn't matter
        return

    def saveLastView(self):
        """
        [public method]
        update the view of all parts you are displaying (presently only one or none) from your own view
        """
        if self.part:
            self._saveLastViewIntoPart( self.part)

    #bruce 050418 split the following Csys methods into two methods each,
    # so MWsemantics can share code with them. Also revised their docstrings,
    # and revised them for assembly/part split (i.e. per-part csys records),
    # and renamed them as needed to reflect that.

    def _setInitialViewFromPart(self, part):
        """
        Set the initial (or current) view used by this GLPane
        to the one stored in part.lastCsys, i.e. to part's "Last View".
        """
        # Huaicai 1/27/05: part of the code of this method comes
        # from original setAssy() method. This method can be called
        # after setAssy() has been called, for example, when opening
        # an mmp file. 

        self.snapToCsys( part.lastCsys)

    def _saveLastViewIntoPart(self, part):
        """
        Save the current view used by this GLPane into part.lastCsys,
        which (when this part's assy is later saved in an mmp file)
        will be saved as that part's "Last View".
        [As of 050418 this still only gets saved in the file for the main part]
        """
        # Huaicai 1/27/05: before mmp file saving, this method
        # should be called to save the last view user has, which will
        # be used as the initial view when it is opened again.
        self.saveViewInCsys( part.lastCsys)

    def saveViewInCsys(self, csys):
        """
        Save the current view used by this GLPane in the given Csys object.
        """
        #e [bruce comment 050418: it would be good to verify csys has the right type,
        #   since almost any python object could be used here without any immediately
        #   detectable error. Maybe this should be a method in csys.]
        csys.quat = Q(self.quat)
        csys.scale = self.scale
        csys.pov = V(self.pov[0], self.pov[1], self.pov[2])
        csys.zoomFactor = self.zoomFactor

    # ==

    def setAssy(self, assy): #bruce 050911 revised this
        """
        [bruce comment 040922] This is called from self.__init__,
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
           Revised 050911: leaves mode as nullmode.
        """
        ##e should previous self.assy be destroyed, or at least made to no longer point to self? [bruce 051227 question]
        assy.o = self ###@@@ should only the part know the glpane?? or, only the mode itself? [bruce 050418 comment]
        self.assy = assy
        mainpart = assy.tree.part
        assert mainpart
            # This assert was added by bruce 050418, in a try/except which tried to patch things up if it failed.
            # No one has reported it ever failing, so hopefully it never does, but it depends on the order
            # in which global objects (glpane, assy) are set up during startup or when opening a new file,
            # so it might happen someday. It turns out the patchup code was wrong (or became wrong later),
            # as noticed by PyChecker (the Part args are wrong), so I removed it [bruce 070621].
            # If we ever need it back, this is what it was (below);
            # it looks like it could be replaced by just initializing our viewpoint to default;
            # it was meant to run instead of the set_part after it (but that is probably safe with mainpart of None, anyway):
            ##if platform.atom_debug:
            ##    print "atom_debug: no mainpart yet in setAssy (ok during init); using a fake one"
            ##mainpart = Part(self) # use this just for its lastCsys
            ##self._setInitialViewFromPart( mainpart)        
        self.set_part( mainpart)

        # defined in modeMixin [bruce 040922]; requires self.assy
        self._reinit_modes() # leaves mode as nullmode as of 050911

        return # from GLPane.setAssy

    # ==

    def center_and_scale_from_bbox(self, bbox, klugefactor = 1.0):
        #bruce 070919 split this out of some other methods here.
        ### REVIEW: should this be a BBox method (taking aspect as an argument)?
        """
        Compute a center and a value of self.scale sufficient to show the
        contents which were used to construct bbox (a BBox object), taking
        self.aspect into account.
           But reduce its size by mutiplying it by klugefactor (typically 0.75
        or so, though the default value is 1.0 since anything less can make some
        bbox contents out of the view), as a kluge for the typical bbox corners
        being farther away than they need to be for most shapes of bbox
        contents. (KLUGE)
           (TODO: Ideally this should be fixed by computing bbox.scale()
        differently, e.g. doing it in the directions corresponding to glpane
        axes.)
        """
        center = bbox.center()

        scale = float( bbox.scale() * klugefactor) #bruce 050616 added float() as a precaution, probably not needed
            # appropriate height to show everything, for square or wide glpane [bruce 050616 comment]
        aspect = self.aspect
        if aspect < 1.0:
            # tall (narrow) glpane -- need to increase self.scale
            # (defined in terms of glpane height) so part bbox fits in width
            # [bruce 050616 comment]
            scale /= aspect
        return center, scale

    # == view toolbar helper methods

    # [bruce 050418 made these from corresponding methods in MWsemantics.py,
    #  which still exist but call these, perhaps after printing a history message.
    #  Also revised them for assembly/part split, i.e. per-part csys attributes.]

    def setViewHome(self):
        """
        Change view to our model's home view (for glpane's current part).
        """
        self.animateToCsys( self.part.homeCsys)

    def setViewFitToWindow(self, fast = False):
        """
        Change view so that the visible part of the entire model
        fits in the glpane.
        If <fast> is True, then snap to the view (i.e. don't animate).
        """
        # Recalculate center and bounding box for all the visible chunks in the current part.
        # The way a 3d bounding box is used to calculate the fit is not adequate. I consider this a bug, but I'm not sure
        # how to best use the BBox object to compute the proper fit. Should ask Bruce. This will do for now. Mark 060713.

        # BUG: only chunks are considered. See comment in bbox_for_viewing_model.
        # [bruce 070919 comment]

        bbox = self.assy.bbox_for_viewing_model()

        center, scale = self.center_and_scale_from_bbox( bbox, klugefactor = 0.75 )

        pov = V(-center[0], -center[1], -center[2])
        if fast:
            self.snapToView(self.quat, scale, pov, 1.0)
        else:
            self.animateToView(self.quat, scale, pov, 1.0)


    def setViewZoomToSelection(self, fast = False): #Ninad 60903
        """
        Change the view so that only selected atoms, chunks and Jigs fit in the GLPane. 
        (i.e. Zoom to the selection) If <fast> is True, then snap to the view
        """
        #ninad060905: 
        #This considers only selected atoms, movable jigs and chunks while doing fit to window. 
        #Zoom to selection ignores other immovable jigs. (it clearly tells this in a history msg)
        # For future:  Should work when a non movable jig is selected
        #Bugs due to use of Bbox remain as in fit to window.

        bbox = self.assy.bbox_for_viewing_selection()

        if bbox is None:
            env.history.message( orangemsg(
                " Zoom To Selection: No visible atoms , chunks or movable jigs selected" \
                " [Acceptable Jigs: Motors, Grid Plane and ESP Image]" ))
            # KLUGE: the proper content of this message depends on the behavior
            # of bbox_for_viewing_selection, which should be extended to cover more
            # kinds of objects.
            return

        center, scale = self.center_and_scale_from_bbox( bbox, klugefactor = 0.85 )
            #ninad060905 experimenting with the scale factor
            # [which was renamed to klugefactor after this comment was written].
            # I see no change with various values!

        pov = V(-center[0], -center[1], -center[2])
        if fast:
            self.snapToView(self.quat, scale, pov, 1.0)
        else:
            self.animateToView(self.quat, scale, pov, 1.0)
        return

    def setViewHomeToCurrent(self):
        """
        Set the Home view to the current view.
        """
        self.saveViewInCsys( self.part.homeCsys)
        self.part.changed() # Mark [041215]

    def setViewRecenter(self, fast = False):
        """
        Recenter the current view around the origin of modeling space.
        """
        part = self.part
        part.computeBoundingBox()
        scale = (part.bbox.scale() * 0.75) + (vlen(part.center) * .5)
            # regarding the 0.75, it has the same role as the klugefactor
            # option of self.center_and_scale_from_bbox(). [bruce comment 070919]
        aspect = self.aspect
        if aspect < 1.0:
            scale /= aspect
        pov = V(0,0,0) 
        if fast:
            self.snapToView(self.quat, scale, pov, 1.0)
        else:
            self.animateToView(self.quat, scale, pov, 1.0)

    def setViewProjection(self, projection): # Added by Mark 050918.
        """
        Set projection, where 0 = Perspective and 1 = Orthographic.  It does not set the 
        prefs db value itself, since we don\'t want all user changes to projection to be stored
        in the prefs db, only the ones done from the Preferences dialog.
        """
        # Set the checkmark for the Ortho/Perspective menu item in the View menu.  
        # This needs to be done before comparing the value of self.ortho to projection
        # because self.ortho and the toggle state of the corresponding action may 
        # not be in sync at startup time. This fixes bug #996.
        # Mark 050924.

        if projection:
            self.win.setViewOrthoAction.setChecked(1)
        else:
            self.win.setViewPerspecAction.setChecked(1)

        if self.ortho == projection:
            return

        self.ortho = projection
        self.gl_update()

    def snapToCsys(self, csys):
        """
        Snap to the destination view defined by csys.
        """
        self.snapToView(csys.quat, csys.scale, csys.pov, csys.zoomFactor)

    def animateToCsys(self, csys, animate = True):
        """
        Animate to the destination view defined by csys.
        If animate is False *or* the user pref "Animate between views" is not selected, 
        then do not animate;  just snap to the destination view.
        """
        # Determine whether to snap (don't animate) to the destination view.
        if not animate or not env.prefs[animateStandardViews_prefs_key]:
            self.snapToCsys(csys)
            return
        self.animateToView(csys.quat, csys.scale, csys.pov, csys.zoomFactor, animate)
        return

    def snapToView(self, q2, s2, p2, z2, update_duration = False):
        """
        Snap to the destination view defined by
        quat q2, scale s2, pov p2, and zoom factor z2.
        """
        # Caller could easily pass these args in the wrong order.  Let's typecheck them.
        typecheckViewArgs(q2, s2, p2, z2)

        self.quat = Q(q2)
        self.pov = V(p2[0], p2[1], p2[2])
        self.zoomFactor = z2
        self.scale = s2

        if update_duration:
            self.gl_update_duration()
        else:
            self.gl_update()

    def rotateView(self, q2): 
        """
        Rotate current view to quat (viewpoint) q2
        """
        self.animateToView(q2, self.scale, self.pov, self.zoomFactor, animate = True)
        return

    # animateToView() uses "Normalized Linear Interpolation" 
    # and not "Spherical Linear Interpolation" (AKA slerp), 
    # which traces the same path as slerp but works much faster.
    # The advantages to this approach are explained in detail here:
    # http://number-none.com/product/Hacking%20Quaternions/
    def animateToView(self, q2, s2, p2, z2, animate = True):
        """
        Animate from the current view to the destination view defined by
        quat q2, scale s2, pov p2, and zoom factor z2.
        If animate is False *or* the user pref "Animate between views" is not selected, 
        then do not animate;  just snap to the destination view.
        """
        # Caller could easily pass these args in the wrong order.  Let's typecheck them.
        typecheckViewArgs(q2, s2, p2, z2)

        # Determine whether to snap (don't animate) to the destination view.
        if not animate or not env.prefs[animateStandardViews_prefs_key]:
            self.snapToView(q2, s2, p2, z2)
            return

        # Make copies of the current view parameters.
        q1 = Q(self.quat)
        s1 = self.scale
        p1 = V(self.pov[0], self.pov[1], self.pov[2])
        z1 = self.zoomFactor

        # Compute the normal vector for current and destination view rotation.
        wxyz1 = V(q1.w, q1.x, q1.y, q1.z)
        wxyz2 = V(q2.w, q2.x, q2.y, q2.z)

        # The rotation path may turn either the "short way" (less than 180) or the "long way" (more than 180).
        # Long paths can be prevented by negating one end (if the dot product is negative).
        if dot(wxyz1, wxyz2) < 0: 
            wxyz2 = V(-q2.w, -q2.x, -q2.y, -q2.z)

        # Compute the maximum number of frames for the maximum possible 
        # rotation (180 degrees) based on how long it takes to repaint one frame.
        max_frames = max(1, env.prefs[animateMaximumTime_prefs_key]/self._repaint_duration)

        # Compute the deltas for the quat, pov, scale and zoomFactor.
        deltaq = q2 - q1
        deltap = vlen(p2 - p1)
        deltas = abs(s2 - s1)
        deltaz = abs(z2 - z1)

        # Do nothing if there is no change b/w the current view to the new view.
        # Fixes bugs 1350 and 1170. mark 060124.
        if deltaq.angle + deltap + deltas + deltaz == 0: # deltaq.angle is always positive.
            return

        # Compute the rotation angle (in degrees) b/w the current and destination view.
        rot_angle = deltaq.angle * 180/math.pi # rotation delta (in degrees)
        if rot_angle > 180:
            rot_angle = 360 - rot_angle # go the short way

        # For each delta, compute the total number of frames each would 
        # require (by itself) for the animation sequence.
        rot_frames = int(rot_angle/180 * max_frames)
        pov_frames = int(deltap * .2) # .2 based on guess/testing. mark 060123
        scale_frames = int(deltas * .05) # .05 based on guess/testing. mark 060123
        zoom_frames = int(deltaz * .05) # Not tested. mark 060123

        # Using the data above, this formula computes the ideal number of frames
        # to use for the animation loop.  It attempts to keep animation speeds consistent.
        total_frames = int( \
            min(max_frames, \
                max(3, rot_frames, pov_frames, scale_frames, zoom_frames)))

        #print "total_frames =", total_frames

        # Compute the increments for each view parameter to use in the animation loop.
        rot_inc = (wxyz2 - wxyz1) / total_frames
        scale_inc = (s2 - s1) / total_frames
        zoom_inc = (z2 - z1) / total_frames
        pov_inc = (p2 - p1) / total_frames

        # Disable standard view actions on toolbars/menus while animating.
        # This is a safety feature to keep the user from clicking another view 
        # animation action while this one is still running.
        self.win.enableViews(False)

        # 'is_animating' is checked in selectAtomsMode.update_selobj() to determine whether the 
        # GLPane is currently animating between views.  If True, then update_selobj() will 
        # not select any object under the cursor. mark 060404.
        self.is_animating = True

        try: #bruce 060404 for exception safety (desirable for both enableViews and is_animating)

            # Main animation loop, which doesn't draw the final frame of the loop.  
            # See comments below for explanation.
            for frame in range(1, total_frames): # Notice no +1 here.
                wxyz1 += rot_inc
                self.quat = Q(norm(wxyz1))
                self.pov += pov_inc
                self.zoomFactor += zoom_inc
                self.scale += scale_inc
                self.gl_update_duration()
                # Very desirable to adjust total_frames inside the loop to maintain
                # animation speed consistency. mark 060127.

            # The animation loop did not draw the last frame on purpose.  Instead,
            # we snap to the destination view.  This also eliminates the possibility
            # of any roundoff error in the increment values, which might result in a 
            # slightly wrong final viewpoint.
            self.snapToView(q2, s2, p2, z2, update_duration = True)
                # snapToView() must call gl_update_duration() and not gl_update(), 
                # or we'll have an issue if total_frames ever ends up = 1. In that case,
                # self._repaint_duration would never get set again because gl_update_duration()
                # would never get called again. BTW,  gl_update_duration()  (as of 060127)
                # is only called in the main animation loop above or when a new part is loaded.
                # gl_update_duration() should be called at other times, too (i.e. when 
                # the display mode changes or something significant happens to the 
                # model or display mode that would impact the rendering duration),
                # or better yet, the number of frames should be adjusted in the 
                # main animation loop as it plays.  This is left as something for me to do
                # later (probably after A7). This verbose comment is left as a reminder
                # to myself about all this.  mark 060127.

        except:
            print_compact_traceback("bug: exception (ignored) during animateToView's loop: ")
            pass

        # Enable standard view actions on toolbars/menus.
        self.win.enableViews(True)

        # Finished animating.
        self.is_animating = False

    # == "callback methods" from modeMixin:

##    def setCursor(self, cursor):# bruce 070628 for debug only
##        print_compact_stack( "glpane setcursor to %r: " % cursor )
##        return QGLWidget.setCursor(self, cursor)

    def update_after_new_mode(self): ### TODO: this will be split between GLPane and CommandSequencer
        """
        do whatever updates are needed after self.mode might have changed
        (ok if this is called more than needed, except it might be slower)
        """
        self.update_after_new_graphicsMode()
        self.update_after_new_currentCommand()
        return

    def update_after_new_graphicsMode(self):
        """
        do whatever updates are needed after self.graphicsMode might have changed
        (ok if this is called more than needed, except it might be slower)
        """
        # TODO: optimize: some of this is not needed if the old & new graphicsMode are equivalent...
        # the best solution is to make them the same object in that case,
        # i.e. to get their owning commands to share that object,
        # and then to compare old & new graphicsMode objects before calling this. [bruce 071011]

        # note: self.selatom is deprecated in favor of self.selobj.
        # self.selobj will be renamed, perhaps to self.objectUnderMouse.
        # REVIEW whether it belongs in self at all (vs the graphicsMode,
        #  or even the currentCommand if it can be considered part of the model
        #  like the selection is). [bruce 071011]

        if self.selatom is not None: #bruce 050612 precaution (scheme could probably be cleaned up #e)
            if platform.atom_debug:
                print "atom_debug: update_after_new_mode storing None over self.selatom", self.selatom
            self.selatom = None
        if self.selobj is not None: #bruce 050612 bugfix; to try it, in Build drag selatom over Select Atoms toolbutton & press it
            if platform.atom_debug:
                print "atom_debug: update_after_new_mode storing None over self.selobj", self.selobj
            self.set_selobj(None)

        self.set_mouse_event_handler(None) #bruce 070628 part of fixing bug 2476 (leftover CC Done cursor)
        self.graphicsMode.update_cursor()
            # do this always (since set_mouse_event_handler only does it if the handler changed) [bruce 070628]
            # Note: the above updates are a good idea,
            # but they don't help with generators [which as of this writing don't change self.mode],
            # thus the need for other parts of that bugfix -- and given those, I don't know if this is needed.
            # But it seems a good precaution even if not. [bruce 070628]

        if sys.platform == 'darwin':
            self.set_widget_erase_color( self.backgroundColor)
            # Note: this was called here when the graphicsMode could determine
            # the background color, but that's no longer true, so it could probably
            # just be called at startup and whenever the background color is changed.
            # Try that sometime, it might be an optim. [bruce 071011]
            #
            # REVIEW: what is self.backgroundColor when we're using the new default
            # of "Blue Sky Gradient". For best effect here, what it ought to be
            # is the average or central bg color in that gradient. I think it's not,
            # which makes me wonder if this bugfix is still needed at all. [bruce 071011]
            #
            # Note: calling this fixed the bug in which the glpane or its edges
            # flickered to black during a main-window resize. [bruce 050408]
            #
            # Note: limited this to Mac, since it turns out that bug (which has
            # no bug number yet) was Mac-specific, but this change caused a new bug 530
            # on Windows. (Not sure about Linux.) See also bug 141 (black during
            # mode-change), related but different. [bruce 050413]
            #
            # Note: for graphicsModes with a translucent surface covering the screen
            # (i.e. Build Atoms water surface), it would be better to blend that surface
            # color with self.backgroundColor for passing to this method, to approximate
            # the effective background color. Alternatively, we could change how those
            # graphicsModes set up OpenGL clearcolor, so that their empty space areas
            # looked like self.backgroundColor.) [bruce 050615 comment]
            pass

        return

    def set_widget_erase_color(self, bgcolor): # revised, bruce 071011
        """
        Change this widget's erase color (seen only if it's resized,
        and only briefly -- it's independent of OpenGL clearColor) to
        the given color.

        Usage note: if that color is the same as the current graphics
        area background color (self.backgroundColor), this will minimize
        the visual effect of widget resizes which temporarily show the erase
        color. See comments near the call for caveats about that.
        """
        r = int(bgcolor[0]*255 + 0.5) # (same formula as in elementSelector.py)
        g = int(bgcolor[1]*255 + 0.5)
        b = int(bgcolor[2]*255 + 0.5)
        pal = QPalette()
        pal.setColor(self.backgroundRole(), QColor(r, g, b))
        self.setPalette(pal)
            # see Qt docs for this and for backgroundRole
        return

    def update_after_new_currentCommand(self): ### TODO: move this out of GLPane into Command Sequencer
        """
        do whatever updates are needed after self.currentCommand might have changed
        (ok if this is called more than needed, except it might be slower)
        """
        #e also update tool-icon visual state in the toolbar? [presumably done elsewhere now]
        # bruce 041222 [comment revised 050408]:
        # changed this to a full update (not just a glpane update),
        # though technically the non-glpane part is the job of our caller rather than us,
        # and changed MWsemantics to make that safe during our __init__.
        self.win.win_update()

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
        mc = env.begin_op("(keypress)") #bruce 060127
            # Note: we have to wrap press and release separately; later, we might pass them tags
            # to help the diffs connect up for merging
            # (same as in drags and maybe as in commands doing recursive event processing).
            # [bruce 060127]
        try:
            #print "GLPane.keyPressEvent(): self.in_drag=",self.in_drag
            if not self.in_drag:
                #bruce 060220 new code; should make it unnecessary (and incorrect)
                # for modes to track mod key press/release for cursor,
                # once update_modkeys calls a cursor updating routine
                #but = e.stateAfter()
                #self.update_modkeys(but)
                self.update_modkeys(e.modifiers())
            self.graphicsMode.keyPressEvent( wrap_key_event(e) )
        finally:
            env.end_op(mc)
        return

    def keyReleaseEvent(self, e):
        mc = env.begin_op("(keyrelease)") #bruce 060127
        try:
            if not self.in_drag:
                #bruce 060220 new code; see comment in keyPressEvent
                #but = e.stateAfter()
                #self.update_modkeys(but)
                self.update_modkeys(e.modifiers())
            self.graphicsMode.keyReleaseEvent( wrap_key_event(e) )
        finally:
            env.end_op(mc)
        return

    def warning(self, str, bother_user_with_dialog = 0, ensure_visible = 1):
        """
        [experimental method by bruce 040922]

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
    def __getattr__(self, name): # in class GLPane
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
        """
        Set current lighting parameters as specified
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
            for c,a,d,s,x,y,z,e in lights:
                # check values, give them standard types
                r = float(c[0])
                g = float(c[1])
                b = float(c[2])
                a = float(a)
                d = float(d)
                s = float(s)
                x = float(x)
                y = float(y)
                z = float(z)
                assert 0.0 <= r <= 1.0
                assert 0.0 <= g <= 1.0
                assert 0.0 <= b <= 1.0
                assert 0.0 <= a <= 1.0
                assert 0.0 <= d <= 1.0
                assert 0.0 <= s <= 1.0
                assert e in [0,1,True,False]
                e = not not e
                res.append( ((r,g,b),a,d,s,x,y,z,e) )
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
        """
        Return the current lighting parameters.
        [For now, these are a list of 3 tuples, one per light,
        each giving several floats and booleans
        (specific format is only documented in other methods or in their code).]
        """
        return list(self._lights)

    # default value of instance variable:
    # [bruce 051212 comment: not sure if this needs to be in sync with any other values;
    #  also not sure if this is used anymore, since __init__ sets _lights from prefs db via loadLighting.]
    _lights = drawer._default_lights

    _default_lights = _lights # this copy will never be changed

    need_setup_lighting = True # whether the next paintGL needs to call _setup_lighting

    _last_glprefs_data_used_by_lights = None #bruce 051212, replaces/generalizes _last_override_light_specular

    def _setup_lighting(self): # as of bruce 060415, this is mostly duplicated between GLPane (has comments) and ThumbView ###@@@
        """
        [private method]
        Set up lighting in the model (according to self._lights).
        [Called from both initializeGL and paintGL.]
        """
        glEnable(GL_NORMALIZE)
            # bruce comment 050311: I don't know if this relates to lighting or not
            # grantham 20051121: Yes, if NORMALIZE is not enabled (and normals
            # aren't unit length or the modelview matrix isn't just rotation)
            # then the lighting equation can produce unexpected results.  

        #bruce 050413 try to fix bug 507 in direction of lighting:
        ##k might be partly redundant now; not sure whether projection matrix needs to be modified here [bruce 051212]
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glprefs = None
            #e someday this could be an argument providing a different glprefs object
            # for local use in part of a scenegraph (if other code was also revised) [bruce 051212 comment]

        #bruce 051212 moved most code from this method into new function, setup_standard_lights
        drawer.setup_standard_lights( self._lights, glprefs)

        # record what glprefs data was used by that, for comparison to see when we need to call it again
        # (not needed for _lights since another system tells us when that changes)
        self._last_glprefs_data_used_by_lights = drawer.glprefs_data_used_by_setup_standard_lights(glprefs)
        return

    def saveLighting(self):
        """
        save the current lighting values in the standard preferences database
        """
        try:
            prefs = preferences.prefs_context()
            key = glpane_lights_prefs_key
            # we'll store everything in a single value at this key,
            # making it a dict of dicts so it's easy to add more lighting attrs (or lights) later
            # in an upward-compatible way.
            # [update, bruce 051206: it turned out that when we added lots of info it became
            #  not upward compatible, causing bug 1181 and making the only practical fix of that bug
            #  a change in this prefs key. In successive commits I moved this key to prefs_constants,
            #  then renamed it (variable and key string) to try to fix bug 1181. I would also like to find out
            #  what's up with our two redundant storings of light color in prefs db, ###@@@
            #  but I think bug 1181 can be fixed safely this way without my understanding that.]

            (((r0,g0,b0),a0,d0,s0,x0,y0,z0,e0), \
             ( (r1,g1,b1),a1,d1,s1,x1,y1,z1,e1), \
             ( (r2,g2,b2),a2,d2,s2,x2,y2,z2,e2)) = self._lights

            # now process it in a cleaner way
            val = {}
            for (i, (c,a,d,s,x,y,z,e)) in zip(range(3),self._lights):
                name = "light%d" % i
                params = dict( color = c, \
                               ambient_intensity = a, \
                               diffuse_intensity = d, \
                               specular_intensity = s, \
                               xpos = x, ypos = y, zpos = z, \
                               enabled = e )
                val[name] = params
            # save the prefs to the database file
            prefs[key] = val
            # This was printing many redundant messages since this method is called 
            # many times while changing lighting parameters in the Preferences | Lighting dialog.
            # Mark 051125.
            #env.history.message( greenmsg( "Lighting preferences saved" ))
        except:
            print_compact_traceback("bug: exception in saveLighting (pref changes not saved): ")
            #e redmsg?
        return

    def loadLighting(self, gl_update = True):
        """
        load new lighting values from the standard preferences database, if possible;
        if correct values were loaded, start using them, and do gl_update unless option for that is False;
        return True if you loaded new values, False if that failed
        """
        try:
            prefs = preferences.prefs_context()
            key = glpane_lights_prefs_key
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
                params = val[name] # a dict of ambient, diffuse, specular, x, y, z, enabled
                color = params['color'] # light color (r,g,b)
                a = params['ambient_intensity'] # ambient intensity
                d = params['diffuse_intensity'] # diffuse intensity
                s = params['specular_intensity'] # specular intensity
                x = params['xpos'] # X position
                y = params['ypos'] # Y position
                z = params['zpos'] # Z position
                e = params['enabled'] # boolean

                res.append( (color,a,d,s,x,y,z,e) )
            self.setLighting( res, gl_update = gl_update)
            if debug_lighting:
                print "debug_lighting: fyi: Lighting preferences loaded"
            return True
        except:
            print_compact_traceback("bug: exception in loadLighting (current prefs not altered): ")
            #e redmsg?
            return False
        pass

    def restoreDefaultLighting(self, gl_update = True):
        """
        restore the default (built-in) lighting preferences (but don't save them).
        """
        # Restore light color prefs keys.
        env.prefs.restore_defaults([
            light1Color_prefs_key, 
            light2Color_prefs_key, 
            light3Color_prefs_key,
        ])

        self.setLighting( self._default_lights,  gl_update = gl_update )

        return True

    # ==

    def initializeGL(self):
        """
        #doc [called by Qt]
        """
        self.makeCurrent() # bruce comment 050311: probably not needed since Qt does it before calling this
        self._setup_lighting()
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        return

    #bruce 060220 changes related to supporting self.modkeys, self.in_drag.
    # These changes are unfinished in the following ways: ###@@@
    # - need to fix the known bugs in fix_event_helper, listed below
    # - update_modkeys needs to call some sort of self.graphicsMode.updateCursor routine
    # - then the modes which update the cursor for key press/release of modkeys need to stop doing that
    #   and instead just define that updateCursor routine properly
    # - ideally we'd capture mouseEnter and call both update_modkeys and the same updateCursor routine
    # - (and once the cursor works for drags between widgets, we might as well fix the statusbar text for that too)

    modkeys = None
    in_drag = False
    button = None
    mouse_event_handler = None # None, or an object to handle mouse events and related queries instead of self.graphicsMode
        # [bruce 070405, new feature for confirmation corner support, and for any other overlay widgets which are handled
        #  mostly independently of the current mode -- and in particular which are not allowed to depend on the recent APIs
        #  added to selectMode, and/or which might need to be active even if current mode is doing xor-mode OpenGL drawing.]

    _last_event_wXwY = (-1,-1) #bruce 070626

    def fix_event(self, event, when, target): #bruce 060220 added support for self.modkeys
        """
        [For most documentation, see fix_event_helper. Argument <when> is one of 'press', 'release', or 'move'.
         We also set self.modkeys to replace the obsolete mode.modkey variable.
         This only works if we're called for all event types which want to look at that variable.]
        """
        qt4transition.qt4todo('reconcile state and stateAfter')
        # fyi: for info about event methods button and buttons (related to state and stateAfter in Qt3) see
        # http://www.riverbankcomputing.com/Docs/PyQt4/html/qmouseevent.html#button
        # [bruce 070328]
        but, mod = fix_event_helper(self, event, when, target)
            # fix_event_helper has several known bugs as of 060220, including:
            # - target is not currently used, and it's not clear what it might be for [in this method, it's self.mode ###REVIEW WHAT IT IS]
            # - it's overly bothered by dialogs that capture press and not release;
            # - maybe it can't be called for key events, but self.modkeys needs update then [might be fixed using in_drag #k];
            # - not sure it's always ok when user moves from one widget to another during a drag;
            # - confused if user releases two mouse buttons at different times to end a drag (thinks the first one ended it).
            # All these can be fixed straightforwardly when they become important enough. [bruce 060220]

        # How we'll update self.mouse_event_handler, so its new value can handle this event after we return
        # (and handle queries by update_cursor and the like, either after we return or in this same method call):
        # - press: change based on current point (event position in window coords)
        # - move: if in_drag, leave unchanged, else (bareMotion) change based on current point.
        # - release: leave unchanged (since release is part of the ongoing drag).
        # We can't do this all now, since we don't know in_drag yet,
        # nor all later, since that would be after a call of update_cursor -- except that
        # in that case, we're not changing it, so (as a kluge) we can ignore that issue
        # and do it all later.

        wX = event.pos().x()
        wY = self.height - event.pos().y()
        self._last_event_wXwY = wX, wY #bruce 070626 for use by mouse_event_handler (needed for confcorner)

        if when == 'release':
            self.in_drag = False
            self.button = None
            # leave self.mouse_event_handler unchanged, so it can process the release if it was handling the drag
            self.graphicsMode.update_cursor()
        else:
            #bruce 070328 adding some debug code/comments to this (for some Qt4 or Qt4/Mac specific bugs), and bugfixing it.
            olddrag = self.in_drag
            self.in_drag = but & (Qt.LeftButton|Qt.MidButton|Qt.RightButton) # Qt4 note: this is a PyQt4.QtCore.MouseButtons object
                # you can also use this to see which mouse buttons are involved.
                # WARNING: that would only work in Qt4 if you use the symbolic constants listed in button_names.keys().
            if not olddrag: # this test seems to still work in Qt4 (apparently MouseButtons.__nonzero__ is sensibly defined)
                #bruce 070328 revised algorithm, since PyQt evidently forgot to make MouseButtons constants work as dict keys.
                # It works now for bareMotion (None), real buttons (LMB or RMB), and simulated MMB (option+LMB).
                # In the latter case I think it fixes a bug, by displaying the rotate cursor during option+LMB drag.
                for lhs, rhs in button_names.iteritems():
                    if self.in_drag == lhs:
                        self.button = rhs
                        break
                    continue
                # Note: if two mouse buttons were pressed at the same time (I think -- bruce 070328), we leave self.button unchanged.

            if when == 'press' or (when == 'move' and not self.in_drag):
                new_meh = self.graphicsMode.mouse_event_handler_for_event_position( wX, wY)
                self.set_mouse_event_handler( new_meh) # includes update_cursor if handler is different
                pass

        self.update_modkeys(mod)
            # need to call this when drag starts; ok to call it during drag too,
            # since retval is what came from fix_event
        return but, mod

    def set_mouse_event_handler(self, mouse_event_handler): #bruce 070628 (related to fixing bug 2476 (leftover CC Done cursor))
        """
        [semi-private]
        Set self.mouse_event_handler (to a handler meeting the MouseEventHandler_API, or to None)
        and do some related updates.
        """
        if self.mouse_event_handler is not mouse_event_handler:
            self.mouse_event_handler = mouse_event_handler
            self.graphicsMode.update_cursor()
            #e more updates?
            # - maybe tell the old mouse_event_handler it's no longer active
            #   (i.e. give it a "leave event" if when == 'move')
            #   and/or tell the new one it is (i.e. give it an "enter event" if when == 'move') --
            #   not needed for now [bruce 070405]
            # - maybe do an incremental gl_update, i.e. gl_update_confcorner?
        return

    def update_modkeys(self, mod):
        """
        Call this whenever you have some modifier key flags from an event (as returned from fix_event,
        or found directly on the event as stateAfter in events not passed to fix_event).
        Exception: don't call it during a drag, except on values returned from fix_event, or bugs will occur.
        There is not yet a good way to follow this advice. This method and/or fix_event should provide one. ###e

        This method updates self.modkeys, setting it to None, 'Shift', 'Control' or 'Shift+Control'.
        (All uses of the obsolete mode.modkey variable should be replaced by this one.)
        """
        shift_control_flags = mod & (Qt.ShiftModifier | Qt.ControlModifier)
        oldmodkeys = self.modkeys
        if shift_control_flags == Qt.ShiftModifier:
            self.modkeys = 'Shift'
        elif shift_control_flags == Qt.ControlModifier:
            self.modkeys = 'Control'
        elif shift_control_flags == (Qt.ShiftModifier | Qt.ControlModifier):
            self.modkeys = 'Shift+Control'
        else:
            self.modkeys = None
        if self.modkeys != oldmodkeys:

            ## This would be a good place to tell the GraphicsMode it might want to update the cursor,
            ## based on all state it knows about, including self.modkeys and what mouse is over,
            ## but it's not enough, since it doesn't cover mouseEnter (or mode Enter),
            ## where we need that even if modkeys didn't change. [bruce 060220]
            self.graphicsMode.update_cursor()

            if self.selobj and self.graphicsMode.hover_highlighting_enabled:
                if self.modkeys == 'Shift+Control' or oldmodkeys == 'Shift+Control':
                    # If something is highlighted under the cursor and we just pressed or released 
                    # "Shift+Control", repaint to update its correct highlight color.
                    self.gl_update_highlight()

        return

    def begin_select_cmd(self):
        # Warning: same named method exists in assembly, GLPane, and ops_select, with different implems.
        # More info in comments in assembly version. [bruce 051031]
        if self.assy:
            self.assy.begin_select_cmd()
        return

    def _tripleClickTimeout(self):
        """
        [private method]

        This method is called whenever the tripleClickTimer expires.
        """
        return

    def mouseTripleClickEvent(self, event):
        """
        Triple-click event handler for the L{GLPane}.

        Code can check I{self.tripleClick} to determine if an event is a
        triple click.

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}

        @see: L{ops_connected_Mixin.getConnectedAtoms()} for an example of use.
        """
        # Implementation: We start a <tripleClickTimer> (a single shot timer)
        # whenever we get a double-click mouse event, but only if there is no 
        # other active tripleClickTimer.
        # If we get another mousePressEvent() before <tripleClickTimer> expires,
        # then we consider that event a triple-click event and mousePressEvent()
        # sends the event here.
        #
        # We then set instance variable <tripleClick> to True and send the 
        # event to mouseDoubleClickEvent(). After mouseDoubleClickEvent() 
        # processes the event and returns, we reset <tripleClick> to False.
        # Code can check <tripleClick> to determine if an event is a
        # triple click.
        #
        # For an example, see ops_connected_Mixin.getConnectedAtoms()
        #
        # Note: This does not fully implement a triple-click event handler
        # (i.e. include mode.left/middle/rightTriple() methods),
        # but it does provides the guts for one. I intent to discuss this with
        # Bruce to see if it would be worth adding these mode methods.
        # Since we only need this to implement NFR 2516 (i.e. select all 
        # connected PAM5 atoms when the user triple-clicks a PAM5 atom), 
        # it isn't necessary.
        #
        # See: mouseDoubleClickEvent(), mousePressEvent(), _tripleClickTimeout()

        #print "Got TRIPLE-CLICK"
        self.tripleClick = True
        try:
            self.mouseDoubleClickEvent(event)
        finally:
            self.tripleClick = False
        return

    def mouseDoubleClickEvent(self, event):
        """
        Double-click event handler for the L{GLPane}.

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        if not self.tripleClickTimer.isActive(): # See mouseTripleClickEvent(). 
            self.tripleClickTimer.start( 200 )   # 200-millisecond singleshot timer.

        # (note: mouseDoubleClickEvent and mousePressEvent share a lot of code)
        self.makeCurrent() #bruce 060129 precaution, presumably needed for same reasons as in mousePressEvent
        self.begin_select_cmd() #bruce 060129 bugfix (needed now that this can select atoms in depositMode)

        self.debug_event(event, 'mouseDoubleClickEvent')

        but, mod = self.fix_event(event, 'press', self.graphicsMode)
        ## but = event.stateAfter()
        #k I'm guessing this event comes in place of a mousePressEvent;
        # need to test this, and especially whether a releaseEvent then comes
        # [bruce 040917 & 060124]
        ## print "Double clicked: ", but

        self.checkpoint_before_drag(event, but) #bruce 060323 for bug 1747 (caused by no Undo checkpoint for doubleclick)
            # Q. Why didn't that bug show up earlier??
            # A. guess: modelTree treeChanged signal, or (unlikely) GLPane paintGL, was providing a checkpoint
            # which made up for the 'checkpoint_after_drag' that this one makes happen (by setting self.__flag_and_begin_retval).
            # But I recently removed the checkpoint caused by treeChanged, and (unlikely cause) fiddled with code related to after_op.
            #   Now I'm thinking that checkpoint_after_drag should do one whether or not checkpoint_before_drag
            # was ever called. Maybe that would fix other bugs... but not cmenu op bugs like 1411 (or new ones the above-mentioned
            # change also caused), since in those, the checkpoint_before_drag happens, but the cmenu swallows up the
            # releaseEvent so the checkpoint_after_drag never has a chance to run. Instead, I'm fixing those by wrapping
            # most_of_paintGL in its own begin/end checkpoints, and (unlike the obs after_op) putting them after
            # env.postevent_updates (see its call to find them). But I might do the lone-releaseEvent checkpoint too. [bruce 060323]
            # Update, 060326: reverting the most_of_paintGL checkpointing, since it caused bug 1759 (more info there).

        handler = self.mouse_event_handler # updated by fix_event [bruce 070405]
        if handler is not None:
            handler.mouseDoubleClickEvent(event)
            return

        if but & Qt.LeftButton:
            self.graphicsMode.leftDouble(event)
        if but & Qt.MidButton:
            self.graphicsMode.middleDouble(event)
        if but & Qt.RightButton:
            self.graphicsMode.rightDouble(event)

        return

    # == DUPLICATING checkpoint_before_drag and checkpoint_after_drag in TreeWidget.py -- should clean up ####@@@@ [bruce 060328]

    __pressEvent = None #bruce 060124 for Undo
    __flag_and_begin_retval = None

    def checkpoint_before_drag(self, event, but): #bruce 060124; split out of caller, 060126
        if but & (Qt.LeftButton|Qt.MidButton|Qt.RightButton):
            # Do undo_checkpoint_before_command if possible.
            #
            #bruce 060124 for Undo; will need cleanup of begin-end matching with help of fix_event;
            # also, should make redraw close the begin if no releaseEvent came by then (but don't
            #  forget about recursive event processing) [done in a different way in redraw, bruce 060323]
            if self.__pressEvent is not None and platform.atom_debug:
                # this happens whenever I put up a context menu in GLPane, so don't print it unless atom_debug ###@@@
                print "atom_debug: bug: pressEvent didn't get release:", self.__pressEvent
            self.__pressEvent = event
            self.__flag_and_begin_retval = None
            ##e we could simplify the following code using newer funcs external_begin_cmd_checkpoint etc in undo_manager
            if self.assy:
                begin_retval = self.assy.undo_checkpoint_before_command("(mouse)") # text was "(press)" before 060126 eve
                    # this command name should be replaced sometime during the command
                self.__flag_and_begin_retval = True, begin_retval
            pass
        return

    def makeCurrent(self):
        QGLWidget.makeCurrent(self)
        # also tell the MainWindow that my PartWindow is the active one
        if MULTIPANE_GUI:
            pw = self.partWindow
            pw.parent._activepw = pw

    def mousePressEvent(self, event):
        """
        Mouse press event handler for the L{GLPane}. It dispatches mouse press
        events depending on B{Shift} and B{Control} key state.

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        if self.tripleClickTimer.isActive():
            # This event is a triple-click event.
            self.mouseTripleClickEvent(event)
            return

        # (note: mouseDoubleClickEvent and mousePressEvent share a lot of code)

        self.makeCurrent()
            ## Huaicai 2/25/05. This is to fix item 2 of bug 400: make this rendering context
            ## as current, otherwise, the first event will get wrong coordinates

        self.begin_select_cmd() #bruce 051031
        if self.debug_event(event, 'mousePressEvent', permit_debug_menu_popup = 1):
            #e would using fix_event here help to avoid those "release without press" messages,
            # or fix bugs from mouse motion? or should we set some other flag to skip subsequent
            # drag/release events until the next press? [bruce 060126 questions]
            return
        ## but = event.stateAfter()
        but, mod = self.fix_event(event, 'press', self.graphicsMode)
            # Notes [bruce 070328]:
            # but = <PyQt4.QtCore.MouseButtons object at ...>,
            # mod = <PyQt4.QtCore.KeyboardModifiers object at ...>.
            # for doc on these objects see http://www.riverbankcomputing.com/Docs/PyQt4/html/qt-mousebuttons.html
            # and for info about event methods button and buttons (related to state and stateAfter in Qt3) see
            # http://www.riverbankcomputing.com/Docs/PyQt4/html/qmouseevent.html#button

        # (I hope fix_event makes sure at most one button flag remains; if not,
        #  following if/if/if should be given some elifs. ###k
        #  Note that same applies to mouseReleaseEvent; mouseMoveEvent already does if/elif.
        #  It'd be better to normalize it all in fix_event, though, in case user changes buttons
        #  without releasing them all, during the drag. Some old bug reports are about that. #e
        #  [bruce 060124-26 comment])

        ## print "Button pressed: ", but

        self.checkpoint_before_drag(event, but)

        handler = self.mouse_event_handler # updated by fix_event [bruce 070405]
        if handler is not None:
            handler.mousePressEvent(event)
            return

        if but & Qt.LeftButton:
            if mod & Qt.ShiftModifier:
                self.graphicsMode.leftShiftDown(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.leftCntlDown(event)
            else:
                self.graphicsMode.leftDown(event)

        if but & Qt.MidButton:
            if mod & Qt.ShiftModifier and mod & Qt.ControlModifier: # mark 060228.
                self.graphicsMode.middleShiftCntlDown(event)
            elif mod & Qt.ShiftModifier:
                self.graphicsMode.middleShiftDown(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.middleCntlDown(event)
            else:
                self.graphicsMode.middleDown(event)

        if but & Qt.RightButton:
            if mod & Qt.ShiftModifier:
                self.graphicsMode.rightShiftDown(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.rightCntlDown(event)
            else:
                self.graphicsMode.rightDown(event)         

        return

    def mouseReleaseEvent(self, event):
        """
        The mouse release event handler for the L{GLPane}.

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        self.debug_event(event, 'mouseReleaseEvent')
        ## but = event.state()
        but, mod = self.fix_event(event, 'release', self.graphicsMode)
        ## print "Button released: ", but

        handler = self.mouse_event_handler # updated by fix_event [bruce 070405]
        if handler is not None:
            handler.mouseReleaseEvent(event)
            self.checkpoint_after_drag(event)
            return

        try:
            if but & Qt.LeftButton:
                if mod & Qt.ShiftModifier:
                    self.graphicsMode.leftShiftUp(event)
                elif mod & Qt.ControlModifier:
                    self.graphicsMode.leftCntlUp(event)
                else:
                    self.graphicsMode.leftUp(event)

            if but & Qt.MidButton:
                if mod & Qt.ShiftModifier and mod & Qt.ControlModifier: # mark 060228.
                    self.graphicsMode.middleShiftCntlUp(event)
                elif mod & Qt.ShiftModifier:
                    self.graphicsMode.middleShiftUp(event)
                elif mod & Qt.ControlModifier:
                    self.graphicsMode.middleCntlUp(event)
                else:
                    self.graphicsMode.middleUp(event)

            if but & Qt.RightButton:
                if mod & Qt.ShiftModifier:
                    self.graphicsMode.rightShiftUp(event)
                elif mod & Qt.ControlModifier:
                    self.graphicsMode.rightCntlUp(event)
                else:
                    self.graphicsMode.rightUp(event)
        except:
            print_compact_traceback("exception in mode's mouseReleaseEvent handler (bug, ignored): ") #bruce 060126

        self.checkpoint_after_drag(event) #bruce 060126 moved this later, to fix bug 1384, and split it out, for clarity
        return

    # == DUPLICATING checkpoint_before_drag and checkpoint_after_drag in TreeWidget.py -- should clean up ####@@@@ [bruce 060328]

    def checkpoint_after_drag(self, event): #bruce 060124; split out of caller, 060126 (and called it later, to fix bug 1384)
        """
        Do undo_checkpoint_after_command(), if a prior press event did an 
        undo_checkpoint_before_command() to match.

        @note: This should only be called *after* calling the mode-specific 
               event handler for this event!
        """
        # (What if there's recursive event processing inside the event handler... when it's entered it'll end us, then begin us...
        #  so an end-checkpoint is still appropriate; not clear it should be passed same begin-retval -- most likely,
        #  the __attrs here should all be moved into env and used globally by all event handlers. I'll solve that when I get to
        #  the other forms of recursive event processing. #####@@@@@
        #  So for now, I'll assume recursive event processing never happens in the event handler
        #  (called just before this method is called) -- then the simplest
        #  scheme for this code is to do it all entirely after the mode's event handler (as done in this routine),
        #  rather than checking __attrs before the handlers and using the values afterwards. [bruce 060126])

        # Maybe we should simulate a pressEvent's checkpoint here, if there wasn't one, to fix hypothetical bugs from a
        # missing one. Seems like a good idea, but save it for later (maybe the next commit, maybe a bug report). [bruce 060323]

        if self.__pressEvent is not None: ####@@@@ and if no buttons are still pressed, according to fix_event?
            self.__pressEvent = None
            if self.__flag_and_begin_retval:
                flagjunk, begin_retval = self.__flag_and_begin_retval
                self.__flag_and_begin_retval = None
                if self.assy:
                    #k should always be true, and same assy as before
                    # (even for file-closing cmds? I bet not, but:
                    #  - unlikely as effect of a mouse-click or drag in GLPane;
                    #  - probably no harm from these checkpoints getting into different assys
                    #  But even so, when solution is developed (elsewhere, for toolbuttons), bring it here
                    #  or (better) put it into these checkpoint methods. ####@@@@)
                    self.assy.undo_checkpoint_after_command( begin_retval)
        return

    def mouseMoveEvent(self, event):
        """
        Mouse move event handler for the L{GLPane}. It dispatches mouse motion
        events depending on B{Shift} and B{Control} key state.

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        ## Huaicai 8/4/05. 
        self.makeCurrent()

        ##self.debug_event(event, 'mouseMoveEvent')
        ## but = event.state()
        but, mod = self.fix_event(event, 'move', self.graphicsMode)

        handler = self.mouse_event_handler # updated by fix_event [bruce 070405]
        if handler is not None:
            handler.mouseMoveEvent(event)
            return

        if but & Qt.LeftButton:
            if mod & Qt.ShiftModifier:
                self.graphicsMode.leftShiftDrag(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.leftCntlDrag(event)
            else:
                self.graphicsMode.leftDrag(event)

        elif but & Qt.MidButton:
            if mod & Qt.ShiftModifier and mod & Qt.ControlModifier: # mark 060228.
                self.graphicsMode.middleShiftCntlDrag(event)
            elif mod & Qt.ShiftModifier:
                self.graphicsMode.middleShiftDrag(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.middleCntlDrag(event)
            else:
                self.graphicsMode.middleDrag(event)

        elif but & Qt.RightButton:
            if mod & Qt.ShiftModifier:
                self.graphicsMode.rightShiftDrag(event)
            elif mod & Qt.ControlModifier:
                self.graphicsMode.rightCntlDrag(event)
            else:
                self.graphicsMode.rightDrag(event)

        else:
            self.graphicsMode.bareMotion(event)
        return

    def wheelEvent(self, event):
        """
        Mouse wheel event handler for the L{GLPane}.

        @param event: A Qt mouse wheel event.
        @type  event: U{B{QWheelEvent}<http://doc.trolltech.com/4/qwheelevent.html>}
        """
        self.debug_event(event, 'wheelEvent')
        if not self.in_drag:
            #but = event.buttons() # I think this event has no stateAfter() [bruce 060220]
            self.update_modkeys(event.modifiers()) #bruce 060220
        self.graphicsMode.Wheel(event) # mode bindings use modkeys from event; maybe this is ok?
            # Or would it be better to ignore this completely during a drag? [bruce 060220 questions]
        return

#== Timer helper methods

    highlightTimer = None #bruce 070110 (was not needed before)

    def _timer_debug_pref(self): #bruce 070110 split this out and revised it
        res = debug_pref("glpane timer interval", Choice([100, 0, 5000, None]), non_debug = True, prefs_key = True)
        if res is not None and type(res) is not type(1):
            # support prefs values stored by future versions (or by a brief bug workaround which stored "None")
            res = None
        return res

    def enterEvent(self, event): # Mark 060806. [minor revisions by bruce 070110]
        """
        Event handler for when the cursor enters the GLPane.

        @param event: The mouse event after entering the GLpane.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        choice = self._timer_debug_pref()
        if choice is None:
            if not env.seen_before("timer is turned off"):
                print "warning: GLPane's timer is turned off by a debug_pref"
            if self.highlightTimer:
                self.killTimer(self.highlightTimer)
            self.highlightTimer = None
            return
        interval = int( choice)
        self.highlightTimer = self.startTimer(interval) # 100-millisecond repeating timer
        return

    def leaveEvent(self, event): # Mark 060806. [minor revisions by bruce 070110]
        """
        Event handler for when the cursor leaves the GLPane.

        @param event: The last mouse event before leaving the GLpane.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        # If an object is "hover highlighted", unhighlight it when leaving the GLpane.
        if self.selobj is not None:
            self.selobj = None ### REVIEW: why not set_selobj?
            self.gl_update_highlight()

        # Kill timer when the cursor leaves the GLpane. It is (re)started in enterEvent() above.
        if self.highlightTimer:
            self.killTimer(self.highlightTimer)
        return

    def timerEvent(self, e): # Mark 060806.
        """
        When the GLpane's timer expires, a signal is generated calling this
        slot method. The timer is started in L{enterEvent()} and killed in 
        L{leaveEvent()}, so the timer is only active when the cursor is in 
        the GLpane.

        This method is part of a hover highlighting optimization and works in
        concert with mouse_exceeded_distance(), which is called from
        L{selectMode.bareMotion()}. It works by creating a 'MouseMove' event
        using the current cursor position and sending it to 
        L{mode.bareMotion()} whenever the mouse hasn't moved since the previous
        timer event.

        @see: L{enterEvent()}, L{leaveEvent()}, 
              L{selectMode.mouse_exceeded_distance()}, and 
              L{selectMode.bareMotion()}
        """
        if not self.highlightTimer or (self._timer_debug_pref() is None): #bruce 070110
            if platform.atom_debug:
                print "debug note (not a bug): GLPane got timerEvent but has no timer"
                    # should happen once when we turn it off or maybe when mouse leaves -- not other times, not much
            #e should we do any of the following before returning??
            return

        # Get the x, y position of the cursor and store as tuple in <xy_now>.
        cursor = self.cursor()
        cursorPos = self.mapFromGlobal(cursor.pos()) # mapFromGlobal() maps from screen coords to GLpane coords.
        xy_now = (cursorPos.x(), cursorPos.y()) # Current cursor position
        xy_last = self.timer_event_last_xy # Cursor position from last timer event.

        # If this cursor position hasn't changed since the last timer event, and no mouse button is
        # being pressed, create a 'MouseMove' mouse event and pass it to mode.bareMotion().  
        # Only selectMode (mouse_exceeded_distance()) makes use of this event. 
        if xy_now == xy_last and self.button == None:
            # Only pass a 'MouseMove" mouse event once to bareMotion() when the mouse stops 
            # and hasn't moved since the last timer event.

            if self.triggerBareMotionEvent:
                #print "Calling bareMotion. xy_now = ", xy_now
                mouseEvent = QMouseEvent( QEvent.MouseMove, cursorPos, Qt.NoButton, Qt.NoButton, Qt.NoModifier)
                                #Qt.NoButton & Qt.MouseButtonMask,
                                #Qt.NoButton & Qt.KeyButtonMask )
                self.graphicsMode.bareMotion(mouseEvent) # Only selectMode.mouse_exceeded_distance() makes use of this.

            self.triggerBareMotionEvent = False

            helpEvent = QHelpEvent(QEvent.ToolTip, QPoint(cursorPos), QPoint(cursor.pos()) )


            if self.dynamicToolTip: # Probably always True. Mark 060818.
                # The cursor hasn't moved since the last timer event. See if we should display the tooltip now.
                self.dynamicToolTip.maybeTip(helpEvent) # maybeTip() is responsible for displaying the tooltip.

        else:

            self.cursorMotionlessStartTime = time.time()
                # Reset the cursor motionless start time to "zero" (now). 
                # Used by maybeTip() to support the display of dynamic tooltips.

            self.triggerBareMotionEvent = True

        self.timer_event_last_xy = xy_now
        return

#== end of Timer helper methods

    def selectedJigTextPosition(self):
        return A(gluUnProject(5, 5, 0))

    def mousepoints(self, event, just_beyond = 0.0):
        """
        Returns a pair (tuple) of points (Numeric arrays of x,y,z)
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

    def eyeball(self): #bruce 060219 ##e should call this to replace equivalent formulae in other places
        """
        Return the location of the eyeball in model coordinates.
        """
        return self.quat.unrot(V(0,0,self.vdist)) - self.pov # note: self.vdist is (usually??) 6 * self.scale
        ##k need to review whether this is correct for tall aspect ratio GLPane

    def SaveMouse(self, event):
        """
        Extracts the mouse position from event and saves it in the I{MousePos}
        property. (localizes the API-specific code for extracting the info)

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
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
        a = 1.1
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

    def setDisplay(self, disp, default_display = False):
        """
        Set the display mode of the GLPane, where:
        "disp" is the display mode, and
        "default_display" changes the header of the display status bar
        to either "Default Display" (True)
        or "Current Display (False, the default).
        """
        #&&& print_compact_stack("GLPane.setDisplay():")
        #&&& print "Current Display Mode = ", self.displayMode
        #&&& print "Default Display Mode = ", env.prefs[defaultDisplayMode_prefs_key]
        #&&& print "setDisplay(disp = ", disp, ", default_display=", default_display, ")"

        # Fix to bug 800. Mark 050807
        if default_display:
            # Used when the user presses "Default Display" or changes the "Default Display"
            # in the preferences dialog.  
            header = "Default Display: " 
        else:
            # Used for all other purposes.
            header = "Current Display: " 

        if disp == diDEFAULT:
            disp = env.prefs[ defaultDisplayMode_prefs_key ]
        #e someday: if self.displayMode == disp, no actual change needed??
        # not sure if that holds for all init code, so being safe for now.
        self.displayMode = disp
        ##Huaicai 3/29/05: Add the condition to fix bug 477
        if self.currentCommand.commandName == 'COOKIE':
            self.win.statusBar().dispbarLabel.setText("    ")
        else:    
            #self.win.statusBar().dispbarLabel.setText( "Default Display: " + dispLabel[disp] )
            self.win.statusBar().dispbarLabel.setText( header + dispLabel[disp] )
        #bruce 050415: following should no longer be needed
        # (and it wasn't enough, anyway, since missed mols in non-current parts;
        #  see comments in chunk.py about today's bugfix in molecule.draw for
        #  bug 452 item 15)
        ## for mol in self.assy.molecules:
        ##     if mol.display == diDEFAULT: mol.changeapp(1)
        return

    # note: as of long before 060829, set/getZoomFactor are never called, and I suspect that nothing
    # ever sets self.zoomFactor to anything other than 1.0, though I didn't fully analyze the calls
    # of the code that looks like it might. So I'll comment these out for now. [bruce 060829 comment]
##    def setZoomFactor(self, zFactor): 
##        self.zoomFactor = zFactor
##    
##    def getZoomFactor(self):
##        return self.zoomFactor

    def dragstart_using_GL_DEPTH(self, event, more_info = False): #bruce 061206 added more_info option
        """
        Use the OpenGL depth buffer pixel at the coordinates of event
        (which works correctly only if the proper GL context (of self) is current -- caller is responsible for this)
        to guess the 3D point that was visually clicked on.
        If that was too far away to be correct, use a point under the mouse and in the plane of the center of view.
           By default, return (False, point) when point came from the depth buffer, or (True, point) when point came from the
        plane of the center of view. Callers should typically do further sanity checks on point and the "farQ" flag (the first
        value in the returned tuple),
        perhaps replacing point with an object's center, projected onto the mousepoints line, if point is an unrealistic
        dragpoint for the object which will be dragged. [#e there should be a canned routine for doing that to our retval]
           If the optional flag more_info is true, then return a larger tuple (whose first two members are the same as in the
        2-tuple we return by default). The larger tuple is (farQ, point, wX, wY, depth, farZ) where wX, wY are the OpenGL window
        coordinates of event within self (note that Y is 0 on the bottom, unlike in Qt window coordinates; glpane.height minus
        wY gives the Qt window coordinate of the event), and depth is the current depth buffer value at the position of the event --
        larger values are deeper; 0.0 is the nearest possible value; depths of farZ or greater are considered "background",
        even though they might be less than 1.0 due to drawing of a background rectangle. (In the current implementation,
        farZ is always GL_FAR_Z, a public global constant defined in constants.py, but in principle it might depend on the
        GLPane and/or vary with differently drawn frames.)
        """
        wX = event.pos().x()
        wY = self.height - event.pos().y()
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        depth = wZ[0][0]
        farZ = GL_FAR_Z

        if depth >= farZ:
            junk, point = self.mousepoints(event)
            farQ = True
        else:
            point = A(gluUnProject(wX, wY, depth))
            farQ = False

        if more_info:
            return farQ, point, wX, wY, depth, farZ
        return farQ, point
    
    def dragstart_using_plane_depth(self, event, plane, more_info = False):
        """
        NOT USED YET,  DOESNT WORK, intended first use in LineMode.leftDown
        """
        #First compute the intersection point of the mouseray with the plane 
        #This will be our first self.handle_MovePt upon left down. 
        #This value is further used in handleLeftDrag. -- Ninad 20070531
        p1, p2     = self.mousepoints(event)
        linePoint  = p2
        lineVector = norm(p2 - p1)
        planeAxis  = plane.getaxis()
        planeNorm  = norm(planeAxis)
        planePoint = plane.center
        from VQT import planeXline, ptonline
        #Find out intersection of the mouseray with the plane. 
        intersection = planeXline(planePoint, planeNorm, linePoint, lineVector)
        if intersection is None:
            intersection =  ptonline(planePoint, linePoint, lineVector)
            
        point = intersection
        
        return point
        

    def rescale_around_point(self, factor, point = None): #bruce 060829; 070402 moved user prefs functionality into caller
        """
        Rescale around point (or center of view == - self.pov, if point is not supplied),
        by multiplying self.scale by factor (and shifting center of view if point is supplied).
           Note: factor < 1 means zooming in, since self.scale is the model distance from screen center
        to edge in plane of center of view.
           Note: not affected by zoom in vs. zoom out, or by user prefs.
        For that, see callers such as basicMode.rescale_around_point_re_user_prefs.
           Note that point need not be in the plane of the center of view, and if it's not, the depth
        of the center of view will change. If callers wish to avoid this, they can project point onto
        the plane of the center of view.
        """
        self.gl_update() #bruce 070402 precaution
        self.scale *= factor
            ###e The scale variable needs to set a limit, otherwise, it will set self.near = self.far = 0.0
            ###  because of machine precision, which will cause OpenGL Error. [needed but NIM] [Huaicai comment 10/18/04]
            # [I'm not sure that comment is still correct -- nothing is actually changing self.near and self.far.
            #  But it may be referring to the numbers made from them and fed to the glu projection routines;
            #  if so, it might still apply. [bruce 060829]]
        # Now use point, so that it, not center of view, gets preserved in screen x,y position and "apparent depth" (between near/far).
        # Method: we're going to move point, in eyespace, relative to center of view (aka cov == -self.pov)
        # from oldscale * (point - cov) to newscale * (point - cov), in units of oldscale (since we're in them now),
        # so we're moving it by (factor - 1) * (point - cov), so translate back, by moving cov the other way (why the other way??):
        # cov -= (factor - 1) * (point - cov). I think this will work the same in ortho and perspective, and can ignore self.quat.
        # Test shows that works; but I don't yet understand why I needed to move cov in the opposite direction as I assumed.
        # But I worry about whether it will work if more than one Wheel event occurs between redraws (which rewrite depth buffer).
        # [bruce 060829]
        if point is not None:
            self.pov += (factor - 1) * (point - (-self.pov))
        return

    def gl_update_duration(self, new_part = False):
        """
        Redraw GLPane and update the repaint duration variable <self._repaint_duration>
        used by animateToView() to compute the proper number of animation frames.
        Redraws the GLPane twice if <new_part> is True and only saves the repaint 
        duration of the second redraw.  This is needed in the case of drawing a newly opened part,
        which takes much longer to draw the first time than the second (or thereafter).
        """
        # The first redraw of a new part takes much longer than the second redraw.
        if new_part: 
            self.gl_update()
            env.call_qApp_processEvents() # Required!

        self._repaint_start_time = time.time()
        self.gl_update()
        env.call_qApp_processEvents() # This forces the GLPane to update before executing the next gl_update().
        self._repaint_end_time = time.time()

        self._repaint_duration =  max(MIN_REPAINT_TIME, self._repaint_end_time - self._repaint_start_time)

        # _last_few_repaint_times is currently unused. May need it later.  Mark 060116.
        self._last_few_repaint_times.append( self._repaint_duration)
        self._last_few_repaint_times = self._last_few_repaint_times[-5:] # keep at most the last five times

        #if new_part:
        #    print "repaint duration = ", self._repaint_duration
        #print "repaint duration = ", self._repaint_duration

        return

    _needs_repaint = 1 #bruce 050516 experiment -- initial value is true

    def gl_update(self): #bruce 050127
        """
        External code should call this when it thinks the GLPane needs
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

    def gl_update_highlight(self): #bruce 070626
        """
        External code should call this when it thinks the hover-highlighting in self
        needs redrawing (but when it doesn't need to report any other need for redrawing).
           This is an optimization, since if there is no other reason to redraw,
        the highlighting alone may be redrawn faster by using a saved color/depth image of
        everything except highlighting, rather than by redrawing everything else.
        [That optim is NIM as of 070626.]
        """
        self.gl_update() # stub for now
        return

    def gl_update_for_glselect(self): #bruce 070626
        """
        External code should call this instead of gl_update when the only reason
        it would have called that is to make us notice self.glselect_wanted and use it to
        update self.selobj. [That optim is NIM as of 070626.]
        """
        self.gl_update() # stub for now
        return

    def gl_update_confcorner(self): #bruce 070627
        """
        External code should call this when it thinks the confirmation corner may need
        redrawing (but when it doesn't need to report any other need for redrawing).
           This is an optimization, since if there is no other reason to redraw,
        the confirmation corner alone may be redrawn faster by using a saved color image of
        the portion of the screen it covers (not including the CC overlay itself),
        rather than by redrawing everything.
        [That optim is NIM as of 070627 and A9.1. Its OpenGL code would make use of the
         conf_corner_bg_image code in this class. Deciding when to do it vs full update
         is the harder part.]
        """
        self.gl_update() # stub for now
        return

    # default values for instance variables related to glSelectBuffer feature [bruce 050608]
    # [note, glselectBufferSize is also part of this set, but is now defined in GLPane_minimal.py]
    glselect_wanted = 0 # whether the next paintGL should start with a glSelectBuffer call [bruce 050608]
    current_glselect = False # [bruce 050616] False, or a 4-tuple of parameters for GL_SELECT rendering
        ### TODO: document this better

    def paintGL(self): #bruce 050127 revised docstring to deprecate direct calls
        """
        [PRIVATE METHOD -- call gl_update instead!]

        The main screen-drawing method, called internally by Qt when our
        superclass needs to repaint (and quite a few other times when it
        doesn't need to).

        THIS METHOD SHOULD NOT BE CALLED DIRECTLY
        BY OUR OWN CODE -- CALL gl_update INSTEAD.
        """

        env.after_op() #bruce 050908
            # [disabled in changes.py, sometime before 060323;
            #  probably obs as of 060323; see this date below]

        if not self.initialised:
            return

        # SOMEDAY: it might be good to set standard GL state, e.g. matrixmode,
        # before checking self.redrawGL here, in order to mitigate bugs in other
        # code (re bug 727), but only if the current mode gets to redefine what
        # "standard GL state" means, since some modes which use this flag to
        # avoid standard repaints also maintain some GL state in nonstandard
        # forms (e.g. for XOR-mode drawing). [bruce 050707 comment]

        if not self.redrawGL:
            return

        self._call_whatever_waits_for_gl_context_current() #bruce 071103

        if debug_pref("GLPane: skip redraws requested only by Qt?",
                      Choice_boolean_False,
                      prefs_key = True):

            # if we don't think this redraw is needed,
            # skip it (but print '#' if atom_debug is set).

            #bruce 070109 restored/empowered the following code, but
            # only within this new debug pref [persistent as of 070110].
            #
            # ITS USE IS PREDICTED TO CAUSE SOME BUGS: one in changed bond
            # redrawing [described below, "bruce 050717 bugfix"]
            # (though the fact that _needs_repaint is not reset until below
            #  makes me think it either won't happen now,
            #  or is explained incorrectly in that comment),
            # and maybe some in look of glpane after resizing, toolbar changes,
            # or popups/dialogs going up or down, any of which might be
            # platform-dependent. The debug_pref's purpose is experimentation --
            # if we could figure out which repaints are really needed, we could
            # probably optimize away quite a few unneeded ones.
            #
            # Update, bruce 070414: so far I only found one bug this debug_pref
            # causes: MT clicks which change chunk selection don't cause redraws,
            # but need to (to show their selection wireframes). That could be
            # easily fixed.

            if not self._needs_repaint: #bruce 050516 experiment
                # This probably happens fairly often when Qt calls paintGL but
                # our own code didn't change anything and therefore didn't call
                # gl_update.
                #
                # This is known to happen when a context menu is put up,
                # the main app window goes into bg or fg, etc.

                # SOMEDAY:
                # An alternative to skipping the redraw would be to optimize it
                # by redrawing a saved image. We're likely to do that for other
                # reasons as well (e.g. to optimize redraws in which only the
                # selection or highlighting changes).

                if platform.atom_debug:
                    sys.stdout.write("#") # indicate a repaint is being skipped
                    sys.stdout.flush()

                return # skip the following repaint
            pass

        env.redraw_counter += 1 #bruce 050825

        #bruce 050707 (for bond inference -- easiest place we can be sure to update bonds whenever needed)
        #bruce 050717 bugfix: always do this, not only when "self._needs_repaint"; otherwise,
        # after an atomtype change using Build's cmenu, the first redraw (caused by the cmenu going away, I guess)
        # doesn't do this, and then the bad bond (which this routine should have corrected, seeing the atomtype change)
        # gets into the display list, and then even though the bondtype change (set_v6) does invalidate the display list,
        # nothing triggers another gl_update, so the fixed bond is not drawn right away. I suppose set_v6 ought to do its own
        # gl_update, but for some reason I'm uncomfortable with that for now (and even if it did, this bugfix here is
        # probably also needed). And many analogous LL changers don't do that.

        env.do_post_event_updates( warn_if_needed = False)
            # WARNING: this calls command-specific ui updating methods
            # like model_changed and selection_changed, even when it
            # doesn't need to (still true 071115). That needs to be fixed,
            # or they all need to be fast when no changes are needed,
            # or this will make redraw needlessly slow. [bruce 071115 comment]

        # Note: at one point we surrounded this repaint with begin/end undo
        # checkpoints, to fix bugs from missing mouseReleases (like bug 1411)
        # (provided they do a gl_update like that one does), from model changes
        # during env.do_post_event_updates(), or from unexpected model changes
        # during the following repaint. But this was slow, and caused bug 1759,
        # and a better fix for 1411 was added (in the menu_spec processor in
        # widgets.py). So the checkpoints were zapped [by bruce 060326].
        # There might be reasons to revive that someday, and ways to avoid
        # its slowness and bugs, but it's not needed for now.

        try:
            self.most_of_paintGL()
        except:
            print_compact_traceback("exception in most_of_paintGL ignored: ")

        return # from paintGL

    def most_of_paintGL(self): #bruce 060323 split this out of paintGL
        """
        Do most of what paintGL should do.
        """
        self._needs_repaint = 0
            # do this now, even if we have an exception during the repaint

        #k not sure whether _restore_modelview_stack_depth is also needed
        # in the split-out standard_repaint [bruce 050617]

        self._restore_modelview_stack_depth()

        # fog_test_enable debug_pref can be removed if fog is implemented fully
        # (added by bradg 20060224)
        fog_test_enable = debug_pref("Use test fog?", Choice_boolean_False)

        if fog_test_enable:
            drawer.setup_fog(125, 170, self.backgroundColor)
            # this next line really should be just before rendering
            # the atomic model itself.  I dunno where that is.
            drawer.enable_fog()

        glDepthFunc( GL_LEQUAL) #bruce 070921; GL_LESS causes bugs
            # (e.g. in exprs/Overlay.py)
            # TODO: put this into some sort of init function in GLPane_minimal;
            # not urgent, since all instances of GLPane_minimal share one GL
            # context for now, and also they all contain this in paintGL.

        self.setDepthRange_setup_from_debug_pref()
        self.setDepthRange_Normal()

        method = self.graphicsMode.render_scene # revised, bruce 070406/071011
        if method is None:
            self.render_scene() # usual case
                # [TODO: move that code into basicGraphicsMode and let it get
                #  called in the same way as the following]
        else:
            method( self) # let the graphicsMode override it

        if fog_test_enable:
            # this next line really should be just after rendering
            # the atomic model itself.  I dunno where that is. [bradg]
            drawer.disable_fog()

        glFlush()

        ##self.swapBuffers()  ##This is a redundant call, Huaicai 2/8/05

        return # from most_of_paintGL

    _conf_corner_bg_image_data = None

    def grab_conf_corner_bg_image(self): #bruce 070626
        """
        Grab an image of the top right corner, for use in confirmation corner
        optimizations which redraw it without redrawing everything.
        """
        width = self.width
        height = self.height
        subwidth = min(width, 100)
        subheight = min(height, 100)
        gl_format, gl_type = GL_RGB, GL_UNSIGNED_BYTE
            # these seem to be enough; GL_RGBA, GL_FLOAT also work but look the same
        image = glReadPixels( width - subwidth,
                              height - subheight,
                              subwidth, subheight,
                              gl_format, gl_type )
        if type(image) is not type("") and \
           not env.seen_before("conf_corner_bg_image of unexpected type"):
            print "fyi: grabbed conf_corner_bg_image of unexpected type %r:" % \
                  ( type(image), )

        self._conf_corner_bg_image_data = (subwidth, subheight,
                                           width, height,
                                           gl_format, gl_type, image)

            # Note: the following alternative form probably grabs a Numeric array, but I'm not sure
            # our current PyOpenGL (in release builds) supports those, so for now I'll stick with strings, as above.
            ## image2 = glReadPixelsf( width - subwidth, height - subheight, subwidth, subheight, GL_RGB)
            ## print "grabbed image2 (type %r):" % ( type(image2), ) # <type 'array'>

        return

    def draw_conf_corner_bg_image(self, pos = None): #bruce 070626 (pos argument is just for development & debugging)
        """
        Redraw the previously grabbed conf_corner_bg_image,
        in the same place from which it was grabbed,
        or in the specified place (lower left corner of pos, in OpenGL window coords).
        Note: this modifies the OpenGL raster position.
        """
        if not self._conf_corner_bg_image_data:
            print "self._conf_corner_bg_image_data not yet assigned"
        else:
            subwidth, subheight, width, height, gl_format, gl_type, image = self._conf_corner_bg_image_data
            if width != self.width or height != self.height:
                # I don't know if this can ever happen; if it can, caller might need
                # to detect this itself and do a full redraw.
                # (Or we might make this method return a boolean to indicate it.)
                print "can't draw self._conf_corner_bg_image_data -- glpane got resized" ###
            else:
                if pos is None:
                    pos = (width - subwidth, height - subheight)
                x, y = pos

                # If x or y is exactly 0, then numerical roundoff errors can make the raster position invalid.
                # Using 0.1 instead apparently fixes it, and causes no noticable image quality effect.
                # (Presumably they get rounded to integer window positions after the view volume clipping,
                #  though some effects I saw implied that they don't get rounded, so maybe 0.1 is close enough to 0.0.)
                # This only matters when GLPane size is 100x100 or less,
                # or when drawing this in lower left corner for debugging,
                # so we don't have to worry about whether it's perfect.
                # (The known perfect fix is to initialize both matrices, but we don't want to bother,
                #  or to worry about exceeding the projection matrix stack depth.)
                x = max(x, 0.1)
                y = max(y, 0.1)

                depth = 0.1 # this should not matter, as long as it's within the viewing volume
                x1, y1, z1 = gluUnProject(x, y, depth)
                glRasterPos3f(x1, y1, z1) # z1 does matter (when in perspective view), since this is a 3d position
                    # Note: using glWindowPos would be simpler and better, but it's not defined
                    # by the PyOpenGL I'm using. [bruce iMac G5 070626]

                if not glGetBooleanv(GL_CURRENT_RASTER_POSITION_VALID):
                    # This was happening when we used x,y = exact 0,
                    # and was causing the image to not get drawn sometimes (when mousewheel zoom was used).
                    # It can still happen for extreme values of mousewheel zoom (close to the ones
                    # which cause OpenGL exceptions), mostly only when pos = (0,0) but not entirely.
                    # Sometimes the actual drawing positions can get messed up then, too.
                    # This doesn't matter much, but indicates that reiniting the matrices would be
                    # a better solution if we could be sure the projection stack depth was sufficient
                    # (or if we reset the standard projection when done, rather than using push/pop).
                    print "bug: not glGetBooleanv(GL_CURRENT_RASTER_POSITION_VALID); pos =", pos

                glDisable(GL_DEPTH_TEST) # otherwise it can be obscured by prior drawing into depth buffer
                # Note: doing more disables would speed up glDrawPixels,
                # but that doesn't matter unless we do it many times per frame.
                glDrawPixels(subwidth, subheight, gl_format, gl_type, image)
                glEnable(GL_DEPTH_TEST)
            pass
        return

    def _restore_modelview_stack_depth(self): #bruce 050608 split this out
        """
        restore GL_MODELVIEW_STACK_DEPTH to 1, if necessary
        """
        #bruce 040923: I'd like to reset the OpenGL state
        # completely, here, incl the stack depths, to mitigate some
        # bugs. How??  Note that there might be some OpenGL init code
        # earlier which I'll have to not mess up. Incl displaylists in
        # drawer.setup_drawer.  What I ended up doing is just to measure the
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

    # The following behavior (in several methods herein) related to wants_gl_update
    # should probably also be done in ThumbViews
    # if they want to get properly updated when graphics prefs change. [bruce 050804 guess] ####@@@@

    wants_gl_update = True #bruce 050804
        # this is set to True after we redraw, and to False by the following method

    def wants_gl_update_was_True(self): #bruce 050804
        """
        Outside code should call this if it changes what our redraw would draw,
        and then sees self.wants_gl_update being true,
        if it might not otherwise call self.gl_update
        (which is also ok to do, but might be slower -- whether it's actually slower is not known).

        This can also be used as an invalidator for passing to self.end_tracking_usage().
        """
        #bruce 070109 comment: it looks wrong to me that the use of this as an invalidator in end_tracking_usage
        # is not conditioned on self.wants_gl_update, either inside or outside this routine. I'm not sure it's really wrong,
        # and I didn't analyze all calls of this, nor how it might interact with self._needs_repaint.
        # If it's wrong, it means the intended optim (avoiding lots of Qt update calls) is not happening.
        self.wants_gl_update = False
        self.gl_update()

    selobj = None #bruce 050609

    # ** Note: all code between the two comments containing "changes merged in from exprs/GLPane_overrider.py"
    # ** was copied from here into that file by bruce 061208, modified somewhat in that file, then moved back here
    # ** by bruce 070110, in order to make GLPane_overrider obsolete, with minor further changes to make this file not
    # ** depend on the exprs module.

    def render_scene(self):#bruce 061208 split this out so some modes can override it (also removed obsolete trans_feature experiment)

        #k not sure whether next things are also needed in the split-out standard_repaint [bruce 050617]

        drawer._glprefs.update() #bruce 051126; kluge: have to do this before lighting *and* inside standard_repaint_0

        if self.need_setup_lighting \
           or self._last_glprefs_data_used_by_lights != drawer.glprefs_data_used_by_setup_standard_lights() \
           or debug_pref("always setup_lighting?", Choice_boolean_False):
            #bruce 060415 added debug_pref("always setup_lighting?"), in GLPane and ThumbView [KEEP DFLTS THE SAME!!];
            # using it makes specularity work on my iMac G4,
            # except for brief periods as you move mouse around to change selobj (also observed on G5, but less frequently I think).
            # BTW using this (on G4) has no effect on whether "new wirespheres" is needed to make wirespheres visible.
            #
            # (bruce 051126 added override_light_specular part of condition)
            # I don't know if it matters to avoid calling this every time...
            # in case it's slow, we'll only do it when it might have changed.
            self.need_setup_lighting = False # set to true again if setLighting is called
            self._setup_lighting()

        self.standard_repaint()

        return # from render_scene

    __subusage = None #bruce 070110

    def standard_repaint(self): #bruce 050617 split this out; bruce 061208 removed obsolete special_topnode experiment
        """
        #doc... this trashes both gl matrices! caller must push them both if it needs the current ones.
        this routine sets its own matrixmode but depends on other gl state being standard when entered.
        """
        if 0:
            #bruce 070109 see if a nonempty subslist is present -- it might be part of my _app contin redraw bug -- offer to empty it
            #WRONG, this is the wrong subslist, it's for usage of the glpane, whhat i need is invals that might come to it.
            # that's whatweused in the onetimesubslist in the usage tracker terminated by end_tracking_usage.
            try:
                subslist = self._SelfUsageTrackingMixin__subslist
            except AttributeError: # this is common at all times -- in fact it's the only case here I've yet seen
                ## print "fyi: glpane had no __subslist" ## this is the only one that got printed, so it doesn't explain my _app redraw bug.
                pass
            else:
                lis = subslist._list_of_subs()
                if not lis:
                    print "fyi: glpane had empty __subslist"###
                else:
                    remove = debug_pref("GLPane: empty __subslist?", Choice_boolean_False, prefs_key = True)
                    print "bug??: glpane had %d things in __subslist%s" % (len(subslist), remove and " -- will remove them" or "")
                    print subslist ###
                    if remove:
                        subslist.remove_all_subs()
                    pass
                pass
            pass

        # zap any leftover usage tracking from last time
        #
        # [bruce 070110 new feature, for debugging and possibly as a bugfix;
        #  #e it might become an option of begin_tracking_usage, but an "aspect" would need to be passed
        #  to permit more than one tracked aspect to be used -- it would determine the attr
        #  corresponding to __subusage in this code. Maybe the same aspect could be passed to
        #  methods of SelfUsageTrackingMixin, but I'm not sure whether the two tracking mixins
        #  would or should interact -- maybe one would define an invalidator for the other to use?]
        #
        if self.__subusage is None: 
            # usual the first time
            pass
        elif self.__subusage == 0:
            # should never happen
            print_compact_stack( "bug: apparent recursive usage tracking in GLPane: ")
            pass
                # it'd be better if we'd make invals illegal in this case, but in current code
                # we don't know the obj to tell to do that (easy to fix if needed)
        elif self.__subusage == -1:
            print "(possible bug: looks like the last begin_tracking_usage raised an exception)"
            pass
        else:
            # usual case except for the first time
            self.__subusage.make_invals_illegal(self)
        self.__subusage = -1

        match_checking_code = self.begin_tracking_usage() #bruce 050806
        self.__subusage = 0

        debug_prints_prefs_key = "A9 devel/debug prints for my bug?" # also defined in exprs/test.py
        if env.prefs.get(debug_prints_prefs_key, False):
            print "glpane begin_tracking_usage" #bruce 070110
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
            self.__subusage = self.end_tracking_usage( match_checking_code, self.wants_gl_update_was_True )
                # same invalidator even if exception
            if env.prefs.get(debug_prints_prefs_key, False):
                print "glpane end_tracking_usage" #bruce 070110
        return

    def validate_selobj_and_hicolor(self): #bruce 070919 split this out, slightly revised behavior, and simplified code
        """
        Return the selobj to use, and its highlight color (according to self.graphicsMode),
        after validating the graphicsmode says it's still ok and has a non-None hicolor.
        Return a tuple (selobj, hicolor) (with selobj and hicolor not None) or (None, None).
        """
        selobj = self.selobj # we'll use this, or set it to None and use None
        if selobj is None:
            return None, None
        if not self.graphicsMode.selobj_still_ok(selobj):
            #bruce 070919 removed local exception-protection from this method call
            self.set_selobj(None)
            return None, None
        hicolor = self.selobj_hicolor(selobj) # ask the mode; protected from exceptions
        if hicolor is None:
            # the mode wants us to not use it.
            # REVIEW: is anything suboptimal about set_selobj(None) here,
            # like disabling the stencil buffer optim?
            # It might be better to retain self.selobj but not draw it in this case.
            # [bruce 070919 comment]
            self.set_selobj(None)
            return None, None
        # both selobj and hicolor are ok and not None
        return selobj, hicolor

    drawing_phase = '?' # new feature, bruce 070124 (set to different fixed strings for different drawing phases)
        # For now, this is only needed during draw (or draw-like) calls which might run drawing code in the exprs module.
        # (Thus it's not needed around internal drawing calls like drawcompass, whose drawing code can't use the exprs module.)
        # The purpose is to let some of the drawing code behave differently in these different phases.
        #
        # Note, there are direct calls of GL_SELECT drawing not from class GLPane, which now need to set this but don't.
        # (They have a lot of other things wrong with them too, esp. duplicated code). Biggest example is for picking jigs.
        # During those calls, this attr will probably equal '?' -- all the draw calls here reset it to that right after they're done.
        # (##e We ought to set it to that at the end of paintGL as well, for safety.)
        #
        # Explanation of possible values: [###e means explan needs to be filled in]
        # - 'glselect' -- only used if mode requested object picking -- glRenderMode(GL_SELECT) in effect; reduced projection matrix
        # - 'main' -- normal drawing, main coordinate system for model (includes trackball/zoom effect)
        # - 'main/Draw_after_highlighting' -- normal drawing, but after selobj is drawn ###e which coord system?
        # - 'main/draw_text_label' -- ###e
        # - 'selobj' -- we're calling selobj.draw_in_abs_coords (not drawing the entire model), within same coordsys as 'main'
        # - 'selobj/preDraw_glselect_dict' -- like selobj, but color buffer drawing is off ###e which coord system, incl projection??
        # [end]

    def get_vdist(self): # [revised bruce 070920]
        """
        Recompute and return the desired distance between
        eyeball and center of view.
        """
        return 6.0 * self.scale

    vdist = property(get_vdist)

    def standard_repaint_0(self):

        # do something (what?) so prefs changes do gl_update when needed [bruce 051126]
        drawer._glprefs.update()
            # (kluge: have to do this before lighting *and* inside standard_repaint_0)

        # clear, and draw background

        c = self.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        del c

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT )
            #e if stencil clear is expensive, we could optim and only do it when needed [bruce ca. 050615]

        # "Blue Sky" is the only gradient supported in A7. [Mark]
        if self.backgroundGradient:
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            drawer.drawFullWindow(bluesky)
            # Note: it would be possible to optimize by not clearing the color buffer
            # when we'll call drawFullWindow, if we first cleared depth buffer (or got
            # drawFullWindow to ignore it and effectively clear it by writing its own
            # depths into it everywhere, if that's possible). [bruce 070913 comment]

        # ask mode to validate self.selobj (might change it to None)
        # (note: self.selobj is used in do_glselect_if_wanted)
        selobj, hicolor = self.validate_selobj_and_hicolor()

        # do modelview setup (needed for GL_SELECT or regular drawing)
        self._setup_modelview()
            #bruce 050608 moved modelview setup here, from just before the mode.Draw call

        # do GL_SELECT drawing if needed (for hit test of objects with mouse)

        ###e note: if any objects moved since they were last rendered, this hit-test will still work (using their new posns),
        # but the later depth comparison (below) might not work right. See comments there for details.

        self.glselect_dict.clear()
            # this will be filled iff we do a gl_select draw,
            # then used only in the same paintGL call to alert some objects they might be the one under the mouse

        self.do_glselect_if_wanted() # note: this sets up its own special projection matrix

        self._setup_projection()

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
            if newpicked is not selobj:
                self.set_selobj( newpicked, "newpicked")
                selobj, hicolor = self.validate_selobj_and_hicolor()
                    # REVIEW: should set_selobj also do this, and save hicolor in an attr of self?
                ###e we'll probably need to notify some observers that selobj changed (if in fact it did). ###@@@
                ## env.history.statusbar_msg("%s" % newpicked) -- messed up by depmode "click to do x" msg

        # otherwise don't change prior selobj -- we have a separate system to set it back to None when needed
        # (which has to be implemented in the bareMotion routines of client modes -- would self.bareMotion be better? ###@@@ review)

        # draw according to mode
        glMatrixMode(GL_MODELVIEW) # this is assumed within Draw methods [bruce 050608 comment]
        try: #bruce 070124 added try/finally for drawing_phase
            self.drawing_phase = 'main' #bruce 070124
            self.graphicsMode.Draw()
        finally:
            self.drawing_phase = '?'

        # highlight selobj if necessary, by drawing it again in highlighted form.
        # It was already drawn normally, but we redraw it now for two reasons:
        # - it might be in a display list in non-highlighted form (and if so, the above draw used that form);
        # - we need to draw it into the stencil buffer too, so mode.bareMotion can tell when mouse is still over it.

        if selobj is not None:
            self.draw_highlighted_objectUnderMouse(selobj, hicolor) #bruce 070920 split this out                
                # REVIEW: is it ok that the mode had to tell us selobj and hicolor
                # (and validate selobj) before drawing the model?

        try: #bruce 070124 added try/finally for drawing_phase
            self.drawing_phase = 'main/Draw_after_highlighting' #bruce 070124
            self.graphicsMode.Draw_after_highlighting() # e.g. draws water surface in Build mode
                # note: this is called with the same coordinate system as mode.Draw() [bruce 061208 comment]
        finally:
            self.drawing_phase = '?'

        ###@@@ move remaining items back into caller? sometimes yes sometimes no... need to make them more modular... [bruce 050617]

        # let parts (other than the main part) draw a text label, to warn
        # the user that the main part is not being shown [bruce 050408]
        try:
            self.drawing_phase = 'main/draw_text_label' #bruce 070124
            self.part.draw_text_label(self)
        except:
            # if it happens at all, it'll happen too often to bother non-debug users with a traceback
            if platform.atom_debug:
                print_compact_traceback( "atom_debug: exception in self.part.draw_text_label(self): " )
            else:
                print "bug: exception in self.part.draw_text_label; use ATOM_DEBUG to see details"
        self.drawing_phase = '?'

        # draw coordinate-orientation arrows at upper right corner of glpane
        if env.prefs[displayCompass_prefs_key]:
            self.drawcompass(self.aspect) #bruce 050608 moved this here, and rewrote it to behave then [#k needs drawing_phase?? bruce 070124]

        #ninad060921 The following draws a dotted origin axis if the correct preference is checked. 
        # The GL_DEPTH_TEST is disabled while drawing this so that if axis is below a model, 
        # it will just draw it as dotted line. (Remember that we are drawing 2 origins superimposed over each other;
        # the dotted form will be visible only when the solid form is obscured by a model in front of it.)
        if env.prefs[displayOriginAxis_prefs_key]:
            if env.prefs[displayOriginAsSmallAxis_prefs_key]:
                drawer.drawOriginAsSmallAxis(self.scale, (0.0,0.0,0.0), dashEnabled = True)
            else:
                drawer.drawaxes(self.scale, (0.0,0.0,0.0), coloraxes = True, dashEnabled = True)

        # draw some test images related to the confirmation corner

        from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False

        ccdp1 = debug_pref("Conf corner test: redraw at lower left", Choice_boolean_False, prefs_key = True)
        ccdp2 = debug_pref("Conf corner test: redraw in-place", Choice_boolean_False, prefs_key = True) # default changed, same prefs_key

        if ccdp1 or ccdp2:
            self.grab_conf_corner_bg_image() #bruce 070626 (needs to be done before draw_overlay)

        if ccdp1:
            self.draw_conf_corner_bg_image((0,0))

        if ccdp2:
            self.draw_conf_corner_bg_image()

        # draw the confirmation corner itself, and/or related overlays

        self.drawing_phase = 'overlay'
        try:
            glMatrixMode(GL_MODELVIEW) #k needed?
            self.graphicsMode.draw_overlay() #bruce 070405
        except:
            print_compact_traceback( "exception in self.graphicsMode.draw_overlay(): " )
        self.drawing_phase = '?'

        # restore standard glMatrixMode, in case drawing code outside of paintGL forgets to do this [precaution]
        glMatrixMode(GL_MODELVIEW)
            # (see discussion in bug 727, which was caused by that)
            # (it might also be good to set mode-specific standard GL state before checking self.redrawGL in paintGL #e)

        return # from standard_repaint_0 (which is the central submethod of paintGL)

    def selobj_hicolor(self, obj):
        """
        If obj was to be highlighted as selobj (whether or not it's presently self.selobj),
        what would its highlight color be?
        Or return None if obj should not be allowed as selobj.
        """
        try:
            hicolor = self.graphicsMode.selobj_highlight_color( obj) #e should implem noop version in basicMode [or maybe i did]
            # mode can decide whether selobj should be highlighted (return None if not), and if so, in what color
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: selobj_highlight_color exception for %r: " % (obj,) )
            else:
                print "bug: selobj_highlight_color exception for %r; for details use ATOM_DEBUG" % (obj,)
            hicolor = None
        return hicolor

    def do_glselect_if_wanted(self): #bruce 070919 split this out
        """
        Do the glRenderMode(GL_SELECT) drawing for one frame
        (and related individual object depth/stencil buffer drawing)
        if desired for this frame.
        """
        if self.glselect_wanted: # note: this will be reset below.
            ####@@@@ WARNING: The original code for this, here in GLPane, has been duplicated and slightly modified
            # in at least three other places (search for glRenderMode to find them). This is bad; common code
            # should be used. Furthermore, I suspect it's sometimes needlessly called more than once per frame;
            # that should be fixed too. [bruce 060721 comment]
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
            self._setup_projection( glselect = self.current_glselect ) # option makes it use gluPickMatrix
                # replace 3,3 with 1,1? 5,5? not sure whether this will matter... in principle should have no effect except speed
            glSelectBuffer(self.glselectBufferSize)
            glRenderMode(GL_SELECT)
            glInitNames()
            ## glPushName(0) # this would be ignored if not in GL_SELECT mode, so do it after we enter that! [no longer needed]
            glMatrixMode(GL_MODELVIEW)
            try:
                self.drawing_phase = 'glselect' #bruce 070124
                self.graphicsMode.Draw()
                    # OPTIM: should perhaps optim by skipping chunks based on bbox... don't know if that would help or hurt
                    # Note: this might call some display lists which, when created, registered namestack names,
                    # so we need to still know those names!
            except:
                print_compact_traceback("exception in mode.Draw() during GL_SELECT; ignored; restoring modelview matrix: ")
                glMatrixMode(GL_MODELVIEW)
                self._setup_modelview( ) ### REVIEW: correctness of this is unreviewed!
                # now it's important to continue, at least enough to restore other gl state
            self.drawing_phase = '?'
            self.current_glselect = False
            ###e On systems with no stencil buffer, I think we'd also need to draw selobj here in highlighted form
            # (in case that form is bigger than when it's not highlighted), or (easier & faster) just always pretend
            # it passes the hit test and add it to glselect_dict -- and, make sure to give it "first dibs" for being
            # the next selobj. I'll implement some of this now (untested when no stencil buffer) but not yet all. [bruce 050612]
            selobj = self.selobj
            if selobj is not None:
                self.glselect_dict[id(selobj)] = selobj
                    ###k unneeded, if the func that looks at this dict always tries selobj first
                    # (except for a kluge near "if self.glselect_dict", commented on below)
            glFlush()
            hit_records = list(glRenderMode(GL_RENDER))
            ## print "%d hits" % len(hit_records)
            for (near,far,names) in hit_records: # see example code, renderpass.py
                ## print "hit record: near,far,names:",near,far,names
                    # e.g. hit record: near,far,names: 1439181696 1453030144 (1638426L,)
                    # which proves that near/far are too far apart to give actual depth,
                    # in spite of the 1-pixel drawing window (presumably they're vertices
                    # taken from unclipped primitives, not clipped ones).
                if 1:
                    # partial workaround for bug 1527. This can be removed once that bug (in drawer.py)
                    # is properly fixed. This exists in two places -- GLPane.py and modes.py. [bruce 060217]
                    if names and names[-1] == 0:
                        print "%d(g) partial workaround for bug 1527: removing 0 from end of namestack:" % env.redraw_counter, names
                        names = names[:-1]
##                        if names:
##                            print " new last element maps to %r" % env.obj_with_glselect_name.get(names[-1])
                if names:
                    # for now, len is always 0 or 1, i think; if not, best to use only the last element...
                    # tho if we ever support "name/subname paths" we'll probably let first name interpret the remaining ones.
                    ###e in fact, when nodes change projection or viewport for kids, and/or share their kids, they need to
                    # put their own names on the stack, so we'll know how to redraw the kids, or which ones are meant when shared.
                    if platform.atom_debug and len(names) > 1: ###@@@ bruce 060725
                        if len(names) == 2 and names[0] == names[1]:
                            if not env.seen_before("dual-names bug"): # this happens for Atoms, don't know why (colorsorter bug??)
                                print "debug (once-per-session message): why are some glnames duplicated on the namestack?",names
                        else:
                            print "debug fyi: len(names) == %d (names = %r)" % (len(names), names)
                    obj = env.obj_with_glselect_name.get(names[-1]) #k should always return an obj
                    if obj is None:
                        print "bug: obj_with_glselect_name returns None for name %r at end of namestack %r" % (names[-1],names)
                    self.glselect_dict[id(obj)] = obj # now these can be rerendered specially, at the end of mode.Draw
            #e maybe we should now sort glselect_dict by "hit priority" (for depth-tiebreaking), or at least put selobj first.
            # (or this could be done lower down, where it's used.)

        return # from do_glselect_if_wanted

    def draw_highlighted_objectUnderMouse(self, selobj, hicolor): #bruce 070920 split this out
        """
        Draw selobj in highlighted form, using its "selobj drawing interface"
        (not yet a formal interface; we use several methods including draw_in_abs_coords).
        Record the drawn pixels in the OpenGL stencil buffer to optimize future
        detection of the mouse remaining over the same selobj (to avoid redraws then).
           Assume we have standard modelview and projection matrices on entry,
        and restore that state on exit (copying or recreating it as we prefer).
           Note: Current implementation uses an extra level on the projection matrix stack
        by default (selobj can override this). This could be easily revised if desired.
        """
        # draw the selobj as highlighted, and make provisions for fast test
        # (by external code) of mouse still being over it (using stencil buffer)

        # note: if selobj highlight is partly translucent or transparent (neither yet supported),
        # we might need to draw it depth-sorted with other translucent objects
        # (now drawn by some modes using Draw_after_highlighting, not depth-sorted or modularly);
        # but our use of the stencil buffer assumes it's drawn at the end (except for objects which
        # don't obscure it for purposes of highlighting hit-test). This will need to be thought through
        # carefully if there can be several translucent objects (meant to be opaque re hit-tests),
        # and traslucent highlighting. See also the comment about highlight_into_depth, below. [bruce 060724 comment]

        # first gather info needed to know what to do -- highlight color (and whether to draw that at all)
        # and whether object might be bigger when highlighted (affects whether depth write is needed now).

        assert hicolor is not None #bruce 070919

        highlight_might_be_bigger = True # True is always ok; someday we might let some objects tell us this can be False

        # color-writing is needed here, iff the mode asked for it, for this selobj.
        #
        # Note: in current code this is always True (as assertion above implies),
        # but it's possible we'll decide to retain self.selobj even if its
        # hicolor is None, but just not draw it in that case, or even to draw it
        # in some ways and not others -- so just in case, keep this test for now.
        # [bruce 070919 comment]
        highlight_into_color = (hicolor is not None)

        if highlight_into_color:
            # depth-writing is needed here, if highlight might be drawn in front of not-yet-drawn transparent surfaces
            # (like Build mode water surface) -- otherwise they will look like they're in front of some of the highlighting
            # even though they're not. (In principle, the preDraw_glselect_dict call above needs to know whether this depth
            # writing occurred ###doc why. Probably we should store it into the object itself... ###@@@ review, then doit )
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
        # As of 070921 we use glDepthRange for this.

        self.setDepthRange_Highlighting()

        try:
            self.drawing_phase = 'selobj' #bruce 070124
                #bruce 070329 moved set of drawing_phase from just after selobj.draw_in_abs_coords to just before it.
                # [This should fix the Qt4 transition issue which is the subject of reminder bug 2300,
                #  though it can't be tested yet since it has no known effect on current code, only on future code.]

            self.graphicsMode.drawHighlightedObjectUnderMouse( self, selobj, hicolor)
                # TEST someday: test having color writing disabled here -- does stencil write still happen??
                # (not urgent, since we definitely need color writing here.)
        except:
            # try/except added for GL-state safety, bruce 061218
            print_compact_traceback(
                "bug: exception in %r.drawHighlightedObjectUnderMouse for %r ignored: " % \
                (self.graphicsMode, selobj)
            )
            pass
        self.drawing_phase = '?'

        self.setDepthRange_Normal()

        # restore other gl state (but don't do unneeded OpenGL ops
        # in case that speeds up OpenGL drawing)
        if not highlight_into_depth:
            glDepthMask(GL_TRUE)
        if not highlight_into_color:
            glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)                
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
            # no need to undo glStencilFunc state, I think -- whoever cares will set it up again
            # when they reenable stenciling.
        glDisable(GL_STENCIL_TEST)

        return # from draw_highlighted_objectUnderMouse

    def set_selobj(self, selobj, why = "why?"):
        if selobj is not self.selobj:
            # Note: we don't call gl_update_highlight here, so the caller needs to
            # if there will be a net change of selobj. I don't know if we should call it here --
            # if any callers call this twice with no net change (i.e. use this to set selobj to None
            # and then back to what it was), it would be bad to call it here. [bruce 070626 comment]
            if debug_set_selobj:
                print_compact_stack("debug_set_selobj: %r -> %r: " % (self.selobj, selobj))
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
                    if platform.atom_debug:
                        #bruce 070203 added this print; not if 1 in case it's too verbose due as mouse moves
                        print_compact_traceback(msg + ': ')
                    else:
                        print "bug: %s; use ATOM_DEBUG to see details" % msg
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
        report_failures = debug_pref("GLPane: preDraw_glselect_dict: report failures?", Choice_boolean_False, prefs_key = True)
        if debug_pref("GLPane: check_target_depth debug prints?", Choice_boolean_False, prefs_key = True):
            debug_prefix = "check_target_depth"
        else:
            debug_prefix = None
        fudge = self.graphicsMode.check_target_depth_fudge_factor #bruce 070115 kluge for testmode
            ### REVIEW: should this be an attribute of each object which can be drawn as selobj, instead?
            # The reasons it's needed are the same ones that require a nonzero DEPTH_TWEAK in GLPane_minimal.
            # See also the comment about it inside check_target_depth. [bruce 070921 comment]
        for orderjunk, obj in items:
            try:
                method = obj.draw_in_abs_coords
            except AttributeError:
                print "bug? ignored: %r has no draw_in_abs_coords method" % (obj,)
                print "   items are:", items
            else:
                try:
                    self.drawing_phase = 'selobj/preDraw_glselect_dict' # bruce 070124
                    method(self, white) # draw depth info (color doesn't matter since we're not drawing pixels)
                    self.drawing_phase = '?'
                        #bruce 050822 changed black to white in case some draw methods have boolean-test bugs for black (unlikely)
                        ###@@@ in principle, this needs bugfixes; in practice the bugs are tolerable in the short term
                        # (see longer discussion in other comments):
                        # - if no one reaches target depth, or more than one does, be smarter about what to do?
                        # - try current selobj first [this is done, as of 050702],
                        #   or give it priority in comparison - if it passes be sure to pick it
                        # - be sure to draw each obj in same way it was last drawn, esp if highlighted:
                        #    maybe drawn bigger (selatom)
                        #    moved towards screen
                    newpicked = self.check_target_depth( obj, fudge, debug_prefix = debug_prefix)
                        # returns obj or None -- not sure if that should be guaranteed [bruce 050822 comment]
                    if newpicked is not None:
                        break
                except:
                    self.drawing_phase = '?'
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
                # [note: there are one or two other checks of the same thing,
                #  e.g. to cover preexisting selobjs whose hicolor might have changed [bruce 060726 comment]]
        else:
            #bruce 060217 debug code re bug 1527. Not sure only happens on a bug, so using atom_debug.
            # (But I couldn't yet cause this to be printed while testing that bug.)
            #bruce 060224 disabling it since it's happening all the time when hover-highlighting in Build
            # (though I didn't reanalyze my reasons for thinking it might be a bug, so I don't know if it's a real one or not).
            #070115 changing condition from if 0 to a debug_pref, and revised message
            if report_failures:
                print "debug_pref: preDraw_glselect_dict failure: targetdepth is %r, items are %r" % (self.targetdepth, items)
        ###e try printing it all -- is the candidate test just wrong?
        return newpicked # might be None in case of errors (or if selobj_hicolor returns None)

    def check_target_depth(self, candidate, fudge, debug_prefix = None): #bruce 050609; revised 050702, 070115
        """
        [private helper method]
           [required arg fudge is the fudge factor in threshhold test]
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
        glFlush() # In theory, glFinish might be needed here;
            # in practice, I don't know if even glFlush is needed.
            # [bruce 070921 comment]
        wX, wY = self.wX, self.wY
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        newdepth = wZ[0][0]
        targetdepth = self.targetdepth
        ### possible change: here we could effectively move selobj forwards (to give it an advantage over other objects)...
        # but we'd need to worry about scales of coord systems in doing that...
        # due to that issue it is probably easier to fix this solely when drawing it, instead.
        if newdepth <= targetdepth + fudge: # use fudge factor in case of roundoff errors (hardcoded as 0.0001 before 070115)
            # [bruce 050702: 0.000001 was not enough! 0.00003 or more was needed, to properly highlight some bonds
            #  which became too hard to highlight after today's initial fix of bug 715-1.]
            # [update, bruce 070921: fyi: one reason this factor is needed is the shorten_tubes flag used to
            #  highlight some bonds, which changes the cylinder scaling, and conceivably (due solely to
            #  roundoff errors) the precise axis direction, and thus the precise cross-section rotation
            #  around the axis. Another reason was a bug in bond_drawer which I fixed today, so the
            #  necessary factor may now be smaller, but I didn't test this.]
            #
            #e could check for newdepth being < targetdepth - 0.002 (error), but best
            # to just let caller do that (NIM), since we would often not catch this error anyway,
            # since we're turning into noop on first success
            # (no choice unless we re-cleared depth buffer now, which btw we could do... #e).
            if debug_prefix:
                print "%s: target depth %r reached by %r at %r" % (debug_prefix, targetdepth, candidate, newdepth)
            return candidate
                # caller should not call us again without clearing depth buffer,
                # otherwise we'll keep returning every object even if its true depth is too high
        if debug_prefix:
            print "%s: target depth %r NOT reached by %r at %r" % (debug_prefix, targetdepth, candidate, newdepth)
        return None

    def _setup_modelview(self):
        """
        set up modelview coordinate system
        """
        #bruce 070919 removed vdist arg, getting it from self.vdist
        vdist = self.vdist
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef( 0.0, 0.0, - vdist)
            # [bruce comment 050615]
            # translate coords for drawing, away from eye (through screen and beyond it) by vdist;
            # this places origin at desired position in eyespace for "center of view" (and for center of trackball rotation).

            # bruce 041214 comment: some code assumes vdist is always 6.0 * self.scale
            # (e.g. eyeball computations, see bug 30), thus has bugs for aspect < 1.0.
            # We should have glpane attrs for aspect, w_scale, h_scale, eyeball,
            # clipping planes, etc, like we do now for right, up, etc. ###e

        q = self.quat 
        glRotatef( q.angle*180.0/math.pi, q.x, q.y, q.z) # rotate those coords by the trackball quat
        glTranslatef( self.pov[0], self.pov[1], self.pov[2]) # and translate them by -cov, to bring cov (center of view) to origin
        return

    def _setup_projection(self, glselect = False): ### WARNING: This is not actually private! TODO: rename it.
        """
        Set up standard projection matrix contents using various attributes of self.
        (Warning: leaves matrixmode as GL_PROJECTION.)
        Optional arg glselect should be False (default) or a 4-tuple (to prepare for GL_SELECT picking).
        """
        #bruce 070919 removed aspect, vdist args, getting them from attrs
        # (as was already done in ThumbView.py)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        scale = self.scale * self.zoomFactor #bruce 050608 used this to clarify following code
        near, far = self.near, self.far

        aspect = self.aspect
        vdist = self.vdist

        if glselect:
            x,y,w,h = glselect
            gluPickMatrix(
                x,y,
                w,h,
                glGetIntegerv( GL_VIEWPORT ) #k is this arg needed? it might be the default...
            )

        if self.ortho:
            glOrtho( - scale * aspect, scale * aspect,
                     - scale,          scale,
                     vdist * near, vdist * far )
        else:
            glFrustum( - scale * near * aspect, scale * near * aspect,
                       - scale * near,          scale * near,
                       vdist * near, vdist * far)
        return

    def drawcompass(self, aspect):
        """
        Draw the "compass" (the perpendicular colored arrows showing orientation of model coordinates)
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
            # hack for use in testmode [revised bruce 070110 when GLPane_overrider merged into GLPane]:
            if self.graphicsMode.compass_moved_in_from_corner:
                glOrtho(-40*aspect, 15.5*aspect, -50, 5.5,  -5, 500)
            else:
                glOrtho(-50*aspect, 3.5*aspect, -50, 4.5,  -5, 500) # Upper Right
        elif self.compassPosition == UPPER_LEFT:
            glOrtho(-3.5*aspect, 50.5*aspect, -50, 4.5,  -5, 500) # Upper Left
        elif self.compassPosition == LOWER_LEFT:
            glOrtho(-3.5*aspect, 50.5*aspect, -4.5, 50.5,  -5, 500) # Lower Left
        else:
            glOrtho(-50*aspect, 3.5*aspect, -4.5, 50.5,  -5, 500) # Lower Right

        q = self.quat
        glRotatef(q.angle*180.0/math.pi, q.x, q.y, q.z)
        glEnable(GL_COLOR_MATERIAL)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDisable(GL_CULL_FACE)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        #ninad 070122 - parametrized the compass drawing. (also added some doc). 
        #Also reduced the overall size of the compass. 

        p1 = -1 # ? start point of arrow cyl? 
        p2 = 3.25 #end point of the arrow cylinderical portion
        p3 = 2.5 #arrow head start point
        p4 = 3.8 # ??? may be used to specify the slant of the arrow head (conical portion).?
        p5 = 4.5 # cone tip

        r1 = 0.2 #cylinder radius 
        r2 =0.2
        r3 = 0.2
        r4 = 0.60 #cone base radius

        glePolyCone([[p1,0,0], [0,0,0], [p2,0,0], [p3,0,0], [p4,0,0], [p5,0,0]],
                    [[0,0,0], [1,0,0], [1,0,0], [.5,0,0], [.5,0,0], [0,0,0]],
                    [r1,r2,r3,r4,0,0])

        glePolyCone([[0,p1,0], [0,0,0], [0,p2,0], [0,p3,0], [0,p4,0], [0,p5,0]],
                    [[0,0,0], [0,.9,0], [0,.9,0], [0,.4,0], [0,.4,0], [0,0,0]],
                    [r1,r2,r3,r4,0,0])

        glePolyCone([[0,0,p1], [0,0,0], [0,0,p2], [0,0,p3], [0,0,p4], [0,0,p5]],
                    [[0,0,0], [0,0,1], [0,0,1], [0,0,.4], [0,0,.4], [0,0,0]],
                    [r1,r2,r3,r4,0,0])

        glEnable(GL_CULL_FACE)
        glDisable(GL_COLOR_MATERIAL)

        ##Adding "X, Y, Z" text labels for Axis. By test, the following code will get
        # segmentation fault on Mandrake Linux 10.0 with libqt3-3.2.3-17mdk
        # or other 3.2.* versions, but works with libqt3-3.3.3-26mdk. Huaicai 1/15/05

        if env.prefs[displayCompassLabels_prefs_key]: ###sys.platform in ['darwin', 'win32']:
            glDisable(GL_LIGHTING)
            glDisable(GL_DEPTH_TEST)
            ## glPushMatrix()
            font = QFont( QString("Helvetica"), 12)
            self.qglColor(QColor(200, 75, 75)) # Dark Red
            self.renderText(p4, 0.0, 0.0, QString("x"), font)
            self.qglColor(QColor(25, 100, 25)) # Dark Green
            self.renderText(0.0, p4, 0.0, QString("y"), font)
            self.qglColor(QColor(50, 50, 200)) # Dark Blue
            self.renderText(0.0, 0.0, p4+0.2, QString("z"), font)
            ## glPopMatrix()
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)

        #bruce 050707 switched order to leave ending matrixmode in standard state, GL_MODELVIEW
        # (though it doesn't matter for present calling code; see discussion in bug 727)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        return # from drawcompass

    # ** note: all code between the two comments containing "changes merged in from exprs/GLPane_overrider.py"
    # ** was modified by bruce 070110. For more info see the other such comment, above.

    # ==

    def resizeGL(self, width, height):
        """
        Called by QtGL when the drawing window is resized.
        """
        self.width = width
        self.height = height
        self.aspect = (self.width + 0.0)/(self.height + 0.0)
            #bruce 070919 made this self.aspect rather than aspect,
            # and moved it here from standard_repaint_0

        ## glViewport(10, 15, (self.width-10)/2, (self.height-15)/3) # (guess: just an example of using a smaller viewport)
        glViewport(0, 0, self.width, self.height)
        if not self.initialised:
            self.initialised = 1
        if width < 300: width = 300
        if height < 300: height = 300
        self.trackball.rescale(width, height)
        self.gl_update()
        return

    def xdump(self):
        """
        for debugging
        """
        print " pov: ", self.pov
        print " quat ", self.quat

    def __str__(self):
        return "<GLPane " + self.name + ">"

    def makemenu(self, menu_spec, menu):
        # this overrides the one from DebugMenuMixin (with the same code), but that's ok,
        # since we want to be self-contained in case someone later removes that mixin class;
        # this method is called by our modes to make their context menus.
        # [bruce 050418 comment]
        return makemenu_helper(self, menu_spec, menu)

    def debug_menu_items(self): #bruce 050515
        """
        overrides method from DebugMenuMixin
        """
        super = DebugMenuMixin
        usual = super.debug_menu_items(self)
            # list of (text, callable) pairs, None for separator
        ours = list(usual)
        try:
            # submenu for available custom modes [bruce 050515]
            #e should add special text to the item for current mode (if any) saying we'll reload it
            modemenu = []
            for commandName, modefile in self.custom_mode_names_files():
                modemenu.append(( commandName,
                                  lambda arg1 = None, arg2 = None, commandName = commandName, modefile = modefile:
                                  self.enter_custom_mode(commandName, modefile) # not sure how many args are passed
                              ))
            if modemenu:
                ours.append(("custom modes", modemenu))
        except:
            print_compact_traceback("exception ignored: ")
        return ours

    def custom_mode_names_files(self): #bruce 061207 & 070427 revised this
        res = []
        try:
            # special case for cad/src/testmode.py (or .pyc)
            for filename in ('testmode.py', 'testmode.pyc'):
                testmodefile = os.path.join( os.path.dirname(__file__), filename) # fails inside site-packages.zip (in Mac release)
                if os.path.isfile(testmodefile):
                    res.append(( 'testmode', testmodefile ))
                    break
            if not res and os.path.dirname(__file__).endswith('site-packages.zip'):
                res.append(( 'testmode', testmodefile )) # special case for Mac release (untested) (do other platforms need this?)
            assert res
        except:
            if platform.atom_debug:
                print "fyi: error adding testmode.py from cad/src to custom modes menu (ignored)"
            pass
        try:
            import gpl_only
        except ImportError:
            pass
        else:
            modes_dir = os.path.join( self.win.tmpFilePath, "Modes")
            if os.path.isdir( modes_dir):
                for file in os.listdir( modes_dir):
                    if file.endswith('.py') and '-' not in file:
                        commandName, ext = os.path.splitext(file)
                        modefile = os.path.join( modes_dir, file)
                        res.append(( commandName, modefile ))
            pass
        res.sort()
        return res

    def enter_custom_mode( self, commandName, modefile): #bruce 050515
        # TODO: move to CommandSequencer.py, and call on self.win.commandSequencer rather than on self
        fn = modefile
        if not os.path.exists(fn) and commandName != 'testmode':
            env.history.message("should never happen: file does not exist: [%s]" % fn)
            return
        if commandName == 'testmode':
            #bruce 070429 explicit import probably needed for sake of py2app (so an explicit --include is not needed for it)
            # (but this is apparently still failing to let the testmode item work in a built release -- I don't know why ###FIX)
            print "enter_custom_mode specialcase for testmode" #e remove this print, when it works in a built release
            import testmode
            ## reload(testmode) # This reload is part of what prevented this case from working in A9 [bruce 070611]
            from testmode import testmode as _modeclass
            print "enter_custom_mode specialcase -- import succeeded"
        else:
            dir, file = os.path.split(fn)
            base, ext = os.path.splitext(file)
            ## commandName = base
            ###e need better way to import from this specific file!
            # (Like using an appropriate function in the import-related Python library module.)
            # This kluge is not protected against weird chars in base.
            oldpath = list(sys.path)
            if dir not in sys.path:
                sys.path.append(dir)
                    # Note: this doesn't guarantee we load file from that dir --
                    # if it's present in another one on path (e.g. cad/src),
                    # we'll load it from there instead. That's basically a bug,
                    # but prepending dir onto path would risk much worse bugs
                    # if dir masked any standard modules which got loaded now.
            import gpl_only # make sure exec is ok in this version (caller should have done this already)
            _module = _modeclass = None # fool pylint into realizing this is not undefined 2 lines below
            exec("import %s as _module" % (base,))
            reload(_module)
            exec("from %s import %s as _modeclass" % (base,base))
            sys.path = oldpath
        modeobj = _modeclass(self) # this should put it into self.commandTable under the name defined in the mode module
            # note: this self is probably supposed to be the command sequencer
        self.commandTable[commandName] = modeobj # also put it in under this name, if different [### will this cause bugs?]
        self.userEnterCommand(commandName)
            # note: self is acting as the command sequencer here; in future we'll get it from somewhere,
            # e.g. self.win.commandSequencer, or just move this whole method there (and get cmdseq from win when we call it)
        return

    pass # end of class GLPane

# ==

def typecheckViewArgs(q2, s2, p2, z2): #mark 060128
    """
    Typecheck the view arguments quat q2, scale s2, pov p2, and zoom factor z2
    used by GLPane.snapToView() and GLPane.animateToView().
    """
    assert isinstance(q2, Q)
    assert isinstance(s2, float)
    assert len(p2) == 3
    assert isinstance(p2[0], float)
    assert isinstance(p2[1], float)
    assert isinstance(p2[2], float)
    assert isinstance(z2, float)
    return

# end

