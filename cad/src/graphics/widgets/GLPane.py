# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPane.py -- NE1's main model view. A subclass of Qt's OpenGL widget, QGLWidget.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

NOTE: If you add code to class GLPane, please carefully consider
whether it belongs in one of its mixin superclasses (GLPane_*.py)
instead of in the main class in this file.

These separate files are topic-specific and should be kept as self-contained
as possible, in methods, attributes, helper functions, and imports.
(Someday, some of them should evolve into separate cooperating
objects and not be part of GLPane's class hierarchy at all.)

(Once the current refactoring is complete, most new code will belong
 in one of those superclass files, not in this file. [bruce 080912])

Module classification: [bruce 080104]

It's graphics/widgets, but this is not as obvious as it sounds.
It is "optimistic", as if we'd already refactored -- it's not fully
accurate today.

Refactoring needed: [bruce 080104]

- split into several classes (either an inheritance tree, or cooperating
objects); [080910 doing an initial step to this: splitting into mixins
in their own files]

- move more common code into GLPane_minimal;

- most urgently, make the main GLPane not be the
same object as the CommandSequencer. [see GLPANE_IS_COMMAND_SEQUENCER --
this is now done by default on 080911, but still needs code cleanup
to completely remove support for the old value, after the next release.]

Some of this might be a prerequisite for some ways of
optimizing the graphics code.

History:

Mostly written by Josh; partly revised by Bruce for mode code revision, 040922-24.
Revised by many other developers since then (and perhaps before).

bruce 080910 splitting class GLPane into several mixin classes in other files.
"""

TEST_DRAWING = False # True  ## Debug/test switch.  Never check in a True value.
if TEST_DRAWING:
    from prototype.test_drawing import test_drawing
    pass

import sys
import time

from PyQt4.Qt import QEvent
from PyQt4.Qt import QMouseEvent
from PyQt4.Qt import QHelpEvent
from PyQt4.Qt import QPoint
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL, QTimer

from PyQt4.QtOpenGL import QGLWidget

from OpenGL.GL import glDepthFunc
from OpenGL.GL import GL_STENCIL_BITS
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import glEnable
from OpenGL.GL import GL_DEPTH_COMPONENT
from OpenGL.GL import glReadPixelsf
from OpenGL.GL import GL_LEQUAL
from OpenGL.GL import GL_MODELVIEW_STACK_DEPTH
from OpenGL.GL import glGetInteger
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
from OpenGL.GL import glDisable
from OpenGL.GL import glPopMatrix
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_FALSE
from OpenGL.GL import glColorMask
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import glClear
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_LIGHTING 
from OpenGL.GL import GL_RGB
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import glReadPixels
from OpenGL.GL import glRasterPos3f
from OpenGL.GL import GL_CURRENT_RASTER_POSITION_VALID
from OpenGL.GL import glGetBooleanv
from OpenGL.GL import glDrawPixels

from OpenGL.GLU import gluUnProject, gluPickMatrix

from geometry.VQT import V, Q, A, norm, angleBetween
from geometry.VQT import planeXline, ptonline

from Numeric import dot

import graphics.drawing.drawing_globals as drawing_globals
from graphics.drawing.CS_draw_primitives import drawwiresphere
from graphics.drawing.drawers import drawOriginAsSmallAxis
from graphics.drawing.drawers import drawaxes

from graphics.drawing.gl_lighting import disable_fog
from graphics.drawing.gl_lighting import enable_fog
from graphics.drawing.gl_lighting import setup_fog

from graphics.drawing.glprefs import glprefs

from command_support.GraphicsMode_API import GraphicsMode_API # for isinstance assertion

from utilities import debug_flags
### from utilities.debug import profile, doProfile ###

from platform_dependent.PlatformDependent import fix_event_helper
from platform_dependent.PlatformDependent import wrap_key_event
from widgets.menu_helpers import makemenu_helper
from widgets.DebugMenuMixin import DebugMenuMixin
from utilities.debug import print_compact_traceback, print_compact_stack
import foundation.env as env
from foundation.changes import SubUsageTrackingMixin
from ne1_ui.cursors import createCompositeCursor

from graphics.widgets.DynamicTip import DynamicTip
from graphics.drawing.Guides import Guides

from utilities.prefs_constants import compassPosition_prefs_key
from utilities.prefs_constants import defaultProjection_prefs_key
from utilities.prefs_constants import startupGlobalDisplayStyle_prefs_key
from utilities.prefs_constants import displayCompass_prefs_key
from utilities.prefs_constants import displayOriginAxis_prefs_key
from utilities.prefs_constants import displayOriginAsSmallAxis_prefs_key
from utilities.prefs_constants import displayCompassLabels_prefs_key
from utilities.prefs_constants import displayRulers_prefs_key
from utilities.prefs_constants import showRulersInPerspectiveView_prefs_key
from utilities.prefs_constants import startup_GLPane_scale_prefs_key
from utilities.prefs_constants import GLPane_scale_for_atom_commands_prefs_key
from utilities.prefs_constants import GLPane_scale_for_dna_commands_prefs_key
from utilities.prefs_constants import fogEnabled_prefs_key

from utilities.constants import diDEFAULT
from utilities.constants import dispLabel
from utilities.constants import GL_FAR_Z
from utilities.constants import diDNACYLINDER
from utilities.constants import diPROTEIN
from utilities.constants import default_display_mode
from utilities.constants import MULTIPANE_GUI
from utilities.constants import white

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice
from utilities.debug_prefs import Choice_boolean_False

from utilities.GlobalPreferences import DEBUG_BAREMOTION
from utilities.GlobalPreferences import use_frustum_culling
from utilities.GlobalPreferences import pref_show_highlighting_in_MT
from utilities.GlobalPreferences import pref_skip_redraws_requested_only_by_Qt
from utilities.GlobalPreferences import GLPANE_IS_COMMAND_SEQUENCER

from graphics.widgets.GLPane_minimal import GLPane_minimal

import utilities.qt4transition as qt4transition

# suspicious imports [should not really be needed, according to bruce 070919]
from model.bonds import Bond # used only for selobj ordering

from graphics.widgets.GLPane_mixin_for_DisplayListChunk import GLPane_mixin_for_DisplayListChunk
from graphics.widgets.GLPane_lighting_methods import GLPane_lighting_methods
from graphics.widgets.GLPane_text_and_color_methods import GLPane_text_and_color_methods
from graphics.widgets.GLPane_stereo_methods import GLPane_stereo_methods
from graphics.widgets.GLPane_frustum_methods import GLPane_frustum_methods
from graphics.widgets.GLPane_view_change_methods import GLPane_view_change_methods

from graphics.drawing.drawcompass import drawcompass

_DEBUG_SET_SELOBJ = False # do not commit with true

## button_names = {0:None, 1:'LMB', 2:'RMB', 4:'MMB'} 
button_names = {Qt.NoButton:None, Qt.LeftButton:'LMB', Qt.RightButton:'RMB', Qt.MidButton:'MMB'}
    #bruce 070328 renamed this from 'button' (only in Qt4 branch), and changed the dict keys from ints to symbolic constants,
    # and changed the usage from dict lookup to iteration over items, to fix some cursor icon bugs.
    # For the constants, see http://www.riverbankcomputing.com/Docs/PyQt4/html/qmouseevent.html
    # [Note: if there is an import of GLPane.button elsewhere, that'll crash now due to the renaming. Unfortunately, for such
    #  a common word, it's not practical to find out except by renaming it and seeing if that causes bugs.]

# ==

if GLPANE_IS_COMMAND_SEQUENCER: #bruce 080813
    from commandSequencer.CommandSequencer import CommandSequencer
    _CommandSequencer_for_glpane = CommandSequencer
else:
    class _CommandSequencer_for_glpane(object):
        pass

class GLPane(
    # these superclasses need to come first, since they need to
    # override methods in GLPane_minimal:
    GLPane_lighting_methods, # needs to override _setup_lighting
    GLPane_frustum_methods, # needs to override is_sphere_visible etc
    
    # these don't yet need to come first, but we'll put them first
    # anyway in case someone adds a default def of some method
    # into GLPane_minimal in the future:
    GLPane_text_and_color_methods,
    GLPane_stereo_methods,
    GLPane_view_change_methods,

    GLPane_minimal, # the "main superclass"; inherits QGLWidget

    _CommandSequencer_for_glpane,
    DebugMenuMixin,
    SubUsageTrackingMixin,
    GLPane_mixin_for_DisplayListChunk
    ):
    """
    Widget for OpenGL graphics and associated mouse/key input,
    with lots of associated/standard behavior and helper methods.

    Note: if you want to add code to this class, consider whether it
    ought to go into one of the mixin superclasses listed above.
    (Once the current refactoring is complete, most new code will belong
     in one of those superclasses, not in this file. [bruce 080912])
    See module docstring for more info.

    Effectively a singleton object:

    * owned by main window (perhaps indirectly via class PartWindow)

    * never remade duringan NE1 session

    * contains public references to other singletons
      (e.g. win (permanent), assy (sometimes remade))

    * some old code stores miscellaneous attributes
      inside it (e.g. shape, stored by Build Crystal)

    Also mixes in class CommandSequencer when GLPANE_IS_COMMAND_SEQUENCER is true.
    This will soon be deprecated and turned off.

    A few of the GLPane's public attributes:

    * several "point of view" attributes (some might be inherited
      from superclass GLPane_minimal)

    * graphicsMode - an instance of GraphicsMode_API

    * currentCommand [when GLPANE_IS_COMMAND_SEQUENCER] - a command object
      (see Command.py and/or baseCommand.py)
    """
    # Note: classes GLPane and ThumbView still share lots of code,
    # which ought to be merged into their common superclass GLPane_minimal.
    # [bruce 070914/080909 comment]
    
    always_draw_hotspot = False #bruce 060627; not really needed, added for compatibility with class ThumbView

    assy = None #bruce 080314

    # the stereo attributes are maintained by the methods in
    # our superclass GLPane_stereo_methods, and used in both
    # that class and this one.
    stereo_enabled = False # piotr 080515 - stereo disabled by default
    stereo_images_to_draw = (0,)
    current_stereo_image = 0

    # note: is_animating is defined and maintained in our superclass
    # GLPane_view_change_methods
    ## self.is_animating = False

    def __init__(self, assy, parent = None, name = None, win = None):
        """
        """
        shareWidget = None
        useStencilBuffer = True

        GLPane_minimal.__init__(self, parent, shareWidget, useStencilBuffer)
        self.win = win

        if GLPANE_IS_COMMAND_SEQUENCER: #bruce 080813 made this conditional
            CommandSequencer._init_modeMixin(self)
            # otherwise, each Assembly owns one, as assy.commandSequencer

        self.partWindow = parent

        self._nodes_containing_selobj = []
            # will be set during set_selobj to a list of 0 or more nodes
            # [bruce 080507 new feature]
        self._nodes_containing_selobj_is_from_selobj = None
            # records which selobj was used to set _nodes_containing_selobj

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
            if debug_flags.atom_debug:
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
##            if debug_flags.atom_debug:
##                print "atom_debug: glGetInteger(GL_STENCIL_BITS) = %r" % ( glGetInteger(GL_STENCIL_BITS) , )
            pass

        self.name = "?"
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
        self.MousePos = V(0, 0)

        # Selection lock state of the mouse for this glpane.
        # See selectionLock() in the ops_select_Mixin class for details.
        self.mouse_selection_lock_enabled = False

        ##Huaicai 2/8/05: If this is true, redraw everything. It's better to split
        ##the paintGL() to several functions, so we may choose to draw 
        ##every thing, or only some thing that has been changed.
        self.redrawGL = True  

        # not selecting anything currently
        # [as of 050418 (and before), this is used in BuildCrystal_Command and selectMode]
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
        self.selatom = None # josh 10/11/04 supports BuildAtoms_Command

        self.jigSelectionEnabled = True # mark 060312

        # [bruce 050608]
        self.glselect_dict = {} # only used within individual runs [of what? paintGL I guess?]
            # see also self.object_for_glselect_name()
            # (which replaces env.obj_with_glselect_name[] as of 080220)

        self.triggerBareMotionEvent = True 
            # Supports timerEvent() to minimize calls to bareMotion(). Mark 060814.
        self.wheelHighlight = False
            # russ 080527: Fix Bug 2606 (highlighting not turned on after wheel event.)
            # Indicates handling bareMotion for highlighting after a mousewheel event.

        self.cursorMotionlessStartTime = time.time() #bruce 070110 fix bug when debug_pref turns off glpane timer from startup

        ###### User Preference initialization ##############################

        # Get glpane related settings from prefs db.
        # Default values are set in "prefs_table" in prefs_constants.py.
        # Mark 050919.

        self._init_background_from_prefs()
        
        self.compassPosition = env.prefs[compassPosition_prefs_key]
        self.ortho = env.prefs[defaultProjection_prefs_key]
        # This updates the checkmark in the View menu. Fixes bug #996 Mark 050925.
        self.setViewProjection(self.ortho) 

        # default display style for objects in the window.
        # even though there is only one assembly to a window,
        # this is here in anticipation of being able to have
        # multiple windows on the same assembly.
        # Start the GLPane's current display mode in "Default Display Mode" (pref).
        self.displayMode = env.prefs[startupGlobalDisplayStyle_prefs_key]
            # TODO: rename self.displayMode (widely used as a public attribute
            # of self) to self.displayStyle. [bruce 080910 comment]
        
        # piotr 080714: Remember last non-reduced display style.
        if self.displayMode == diDNACYLINDER or \
           self.displayMode == diPROTEIN:
            self.lastNonReducedDisplayMode = default_display_mode
        else:
            self.lastNonReducedDisplayMode = self.displayMode
        #self.win.statusBar().dispbarLabel.setText( "Current Display: " + dispLabel[self.displayMode] )

        ###### End of User Preference initialization ########################## 

        self.makeCurrent()

        self._setup_display_lists() # defined in GLPane_minimal. [bruce 071030]

        self.setAssy(assy) # leaves self.currentCommand/self.graphicsMode as nullmode, as of 050911

        self.loadLighting() #bruce 050311 [defined in GLPane_lighting_methods]
        #bruce question 051212: why doesn't this prevent bug 1204 in use of lighting directions on startup?

        self.dynamicToolTip = DynamicTip(self)

        # Guides include rulers and soon, grid lines. Mark 2008-02-24.
        self.guides = Guides(self) 

        # Triple-click Timer: for the purpose of implementing a triple-click
        #                     event handler, which is not supported by Qt.
        #
        # See: mouseTripleClickEvent()

        self.tripleClick       =  False
        self.tripleClickTimer  =  QTimer(self)
        self.tripleClickTimer.setSingleShot(True)
        self.connect(self.tripleClickTimer, SIGNAL('timeout()'), self._tripleClickTimeout)

        return # from GLPane.__init__ 

    def resizeGL(self, width, height):
        """
        Called by QtGL when the drawing window is resized.
        """
        #bruce 080912 moved most of this into superclass
        GLPane_minimal.resizeGL(self, width, height) # call superclass method
        self.gl_update() # REVIEW: ok for superclass?
            # needed here? (Guess yes, to set needs_repaint flag)
        return
    
    # ==
    
    if not GLPANE_IS_COMMAND_SEQUENCER:
        
        #bruce 080813 get .graphicsMode from commandSequencer
        
        def _get_graphicsMode(self):
            res = self.assy.commandSequencer.currentCommand.graphicsMode
                # don't go through commandSequencer.graphicsMode,
                # maybe that attr is not needed
            assert isinstance(res, GraphicsMode_API)
            return res

        graphicsMode = property( _get_graphicsMode)

        # same with .currentCommand, but complain;
        # uses should go through command sequencer

        def _get_currentCommand(self):
            print_compact_stack( "deprecated: direct ref of glpane.currentCommand: ") #bruce 080813
            return self.assy.commandSequencer.currentCommand

        currentCommand = property( _get_currentCommand)

        pass # end of if statement

    # ==
    
    def should_draw_valence_errors(self):
        """
        [overrides GLPane_minimal method]
        """
        return True

    # ==

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

    #bruce 050418 split the following NamedView methods into two methods each,
    # so MWsemantics can share code with them. Also revised their docstrings,
    # and revised them for assembly/part split (i.e. per-part csys records),
    # and renamed them as needed to reflect that.
    #
    #bruce 080912: the ones that are slot methods are now moved to
    # GLPane_view_change_methods.py. The "view" methods that remain are involved
    # in the relation between self and self.part, rather than in implementing
    # view changes for the UI, so they belong here rather than in that file.

    def _setInitialViewFromPart(self, part):
        """
        Set the initial (or current) view used by this GLPane
        to the one stored in part.lastView, i.e. to part's "Last View".
        """
        # Huaicai 1/27/05: part of the code of this method comes
        # from original setAssy() method. This method can be called
        # after setAssy() has been called, for example, when opening
        # an mmp file. 

        self.snapToNamedView( part.lastView) # defined in GLPane_view_change_methods

    def _saveLastViewIntoPart(self, part):
        """
        Save the current view used by this GLPane into part.lastView,
        which (when this part's assy is later saved in an mmp file)
        will be saved as that part's "Last View".
        [As of 050418 this still only gets saved in the file for the main part]
        """
        # Huaicai 1/27/05: before mmp file saving, this method
        # should be called to save the last view user has, which will
        # be used as the initial view when it is opened again.
        part.lastView.setToCurrentView(self)

    # ==

    def setAssy(self, assy): #bruce 050911 revised this
        """
        [bruce comment 040922, partly updated 080812]
        This is called from self.__init__, and from
        MWSemantics._make_and_init_assy when user asks to open a new file
        or close current file.

        Apparently, it is supposed to forget whatever is happening now,
        and reinitialize the entire GLPane. However, it does nothing to
        cleanly leave the current mode, if any; my initial guess [040922]
        is that that's a bug. (As of 040922 I didn't yet try to fix that...
        only to emit a warning when it happens. Any fix requires modifying
        our callers.)

        I also wonder if setAssy ought to do some of the other things
        now in __init__, e.g. setting some display prefs to their
        defaults.

        Yet another bug (in how it's called now): user is evidently not given
        any chance to save unsaved changes, or get back to current state if the
        openfile fails... tho I'm not sure I'm right about that, since I didn't
        test it.

        Revised 050911: leaves mode as nullmode.
        """
        if self.assy:
            # make sure the old assy (if any) was closed [bruce 080314]
            # Note: if future changes to permit MDI allow one GLPane to switch
            # between multiple assys, then the following might not be a bug.
            # Accordingly, we only complain, we don't close it.
            # Callers should close it before calling this method.
            if not self.assy.assy_closed:
                print "\nlikely bug: GLPane %r .setAssy(%r) but old assy %r " \
                      "was not closed" % (self, assy, self.assy)
            ##e should previous self.assy be destroyed, or at least
            # made to no longer point to self? [bruce 051227 question]
            pass
        self.assy = assy
        mainpart = assy.tree.part
        assert mainpart #bruce 050418; depends on the order in which
            # global objects (glpane, assy) are set up during startup
            # or when opening a new file, so it might fail someday.
            # It might not be needed if set_part (below) doesn't mind
            # a mainpart of None and/or if we initialize our viewpoint
            # to default, according to an older version of this comment.
            # [comment revised, bruce 080812]    

        assy.set_glpane(self) # sets assy.o and assy.glpane
            # logically I'd prefer to move this to just after set_part,
            # but right now I have no time to fully analyze whether set_part
            # might depend on this having been done, so I won't move it down
            # for now. [bruce 080314]

        self.set_part( mainpart)

        if GLPANE_IS_COMMAND_SEQUENCER:
            # defined in CommandSequencer [bruce 040922]; requires self.assy
            self._reinit_modes() # leaves mode as nullmode as of 050911
        else:
            self.assy.commandSequencer._reinit_modes()
                # todo: move this out of this method, once it's the usual case

        return # from GLPane.setAssy

    # ==

    def setCursor(self, inCursor = None):
        """
        Sets the cursor for the glpane

        This method is also responsible for adding special symbols to the 
        cursor that should be persistent as cursors change (i.e. the selection
        lock symbol).

        @param incursor: Either a cursor or a list of 2 cursors (one for a dark
                    background, one for a light background). 
                    If cursor is None, reset the cursor to the
                    most recent version without the selection lock symbol.
        @type  type: U{B{QCursor}<http://doc.trolltech.com/4/qcursor.html>} or
                    a list of two {B{QCursors}<http://doc.trolltech.com/4/qcursor.html>} or
        """
        # If inCursor is a list (of a dark and light bg cursor), set
        # cursor to one or the other based on the current background.
        if isinstance(inCursor, list):
            if self.is_background_dark():
                cursor = inCursor[0] # dark bg cursor
            else:
                cursor = inCursor[1] # light bg cursor
            pass
        else:
            cursor = inCursor
            
        if not cursor:
            cursor = self.cursorWithoutSelectionLock
        self.cursorWithoutSelectionLock = cursor

        if self.mouse_selection_lock_enabled: # Add the selection lock symbol.
            cursor = createCompositeCursor(cursor,
                                           self.win.selectionLockSymbol,
                                           offsetX = 2, offsetY = 19)
        return QGLWidget.setCursor(self, cursor)

    # == update methods [refactored between self and CommandSequencer, bruce 080813]

    def update_after_new_graphicsMode(self): # maybe rename to update_GLPane_after_new_graphicsMode?
        """
        do whatever updates are needed in self after self.graphicsMode might have changed
        (ok if this is called more than needed, except it might be slower)

        @note: this should only do updates related specifically to self
               (as a GLPane). Any updates to assy, command sequencer or stack,
               active commands, or other UI elements should be done elsewhere.
        """
        # note: as of 080813, called from _cseq_update_after_new_mode and Move_Command
        
        # TODO: optimize: some of this is not needed if the old & new graphicsMode are equivalent...
        # the best solution is to make them the same object in that case,
        # i.e. to get their owning commands to share that object,
        # and then to compare old & new graphicsMode objects before calling this. [bruce 071011]

        # note: self.selatom is deprecated in favor of self.selobj.
        # self.selobj will be renamed, perhaps to self.objectUnderMouse.
        # REVIEW whether it belongs in self at all (vs the graphicsMode,
        #  or even the currentCommand if it can be considered part of the model
        #  like the selection is). [bruce 071011]

        # selobj

        if self.selatom is not None: #bruce 050612 precaution (scheme could probably be cleaned up #e)
            if debug_flags.atom_debug:
                print "atom_debug: update_after_new_graphicsMode storing None over self.selatom", self.selatom
            self.selatom = None
        if self.selobj is not None: #bruce 050612 bugfix; to try it, in Build drag selatom over Select Atoms toolbutton & press it
            if debug_flags.atom_debug:
                print "atom_debug: update_after_new_graphicsMode storing None over self.selobj", self.selobj
            self.set_selobj(None)

        # event handlers
        
        self.set_mouse_event_handler(None) #bruce 070628 part of fixing bug 2476 (leftover CC Done cursor)

        # cursor (is this more related to event handlers or rendering?)
        
        self.graphicsMode.update_cursor()
            # do this always (since set_mouse_event_handler only does it if the handler changed) [bruce 070628]
            # Note: the above updates are a good idea,
            # but they don't help with generators [which as of this writing don't change self.currentCommand],
            # thus the need for other parts of that bugfix -- and given those, I don't know if this is needed.
            # But it seems a good precaution even if not. [bruce 070628]

        # rendering-related
        
        if sys.platform == 'darwin':
            self._set_widget_erase_color()
            # sets it from self.backgroundColor;
            # attr and method defined in GLPane_text_and_color_methods;
            # see comments in that method's implem for caveats

        self.gl_update() #bruce 080829
        
        return

    def update_GLPane_after_new_command(self): #bruce 080813
        """
        [meant to be called only from CommandSequencer._cseq_update_after_new_mode]
        """
        self._adjust_GLPane_scale_if_needed()
        return
    
    def _adjust_GLPane_scale_if_needed(self): # by Ninad
        """
        Adjust the glpane scale while in a certain command. 

        Behavior --

        Default scale remains the same (i.e. value of 
        startup_GLPane_scale_prefs_key) 

        If user enters BuildDna command and if --
        a) there is no model in the assembly AND 
        b) user didn't change the zoom factor , the glpane.scale would be 
        adjusted to 50.0 (GLPane_scale_for_dna_commands_prefs_key)

        If User doesn't do anything in BuildDna AND also doesn't modify the zoom
        factor, exiting BuildDna and going into the default command
        (or any command such as BuildAtoms), it should restore zoom scale to 
        10.0 (value for GLPane_scale_for_atom_commands_prefs_key)

        @see: self.update_after_new_current_command() where it is called. This
              method in turn, gets called after you enter a new command.
        @see: Command.start_using_new_mode()
        """
        #Implementing this method fixes bug 2774

        #bruce 0808013 revised order of tests within this method

        #hasattr test fixes bug 2813
        if hasattr(self.assy.part.topnode, 'members'):
            numberOfMembers = len(self.assy.part.topnode.members)
        else:
            #It's a clipboard part, probably a chunk or a jig not contained in 
            #a group.
            numberOfMembers = 1

        if numberOfMembers != 0: # do nothing except for an empty part
            return

        # TODO: find some way to refactor this to avoid knowing the
        # explicit list of commandNames (certainly) and prefs_keys /
        # preferred scales (if possible). At least, define a
        # "command scale kind" attribute to test here in place of
        # having the list of command names. [bruce 080813 comment]

        dnaCommands = ('BUILD_DNA', 'DNA_DUPLEX', 'DNA_SEGMENT', 'DNA_STRAND')

        startup_scale = float(env.prefs[startup_GLPane_scale_prefs_key])

        dna_preferred_scale = float(
            env.prefs[GLPane_scale_for_dna_commands_prefs_key])

        atom_preferred_scale = float(
            env.prefs[GLPane_scale_for_atom_commands_prefs_key])

        if self.assy.commandSequencer.currentCommand.commandName in dnaCommands:
            if self.scale == startup_scale:                
                self.scale = dna_preferred_scale
        else:
            if self.scale == dna_preferred_scale:
                self.scale = atom_preferred_scale

        return

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

    # ==

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
            # - target is not currently used, and it's not clear what it might be for
            #   [in this method, it's self.mode ###REVIEW WHAT IT IS]
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
            # This would be a good place to tell the GraphicsMode it might want to update the cursor,
            # based on all state it knows about, including self.modkeys and what the mouse is over,
            # but it's not enough, since it doesn't cover mouseEnter (or mode Enter),
            # where we need that even if modkeys didn't change. [bruce 060220]
            self.graphicsMode.update_cursor()
            highlighting_enabled = self.graphicsMode.command.isHighlightingEnabled()
            if self.selobj and highlighting_enabled:
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
        # but it does provides the guts for one. I intend to discuss this with
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
        self.begin_select_cmd() #bruce 060129 bugfix (needed now that this can select atoms in BuildAtoms_Command)

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

    __pressEvent = None #bruce 060124 for Undo
    __flag_and_begin_retval = None

    def checkpoint_before_drag(self, event, but): #bruce 060124; split out of caller, 060126
        if but & (Qt.LeftButton|Qt.MidButton|Qt.RightButton):
            # Do undo_checkpoint_before_command if possible.
            #
            #bruce 060124 for Undo; will need cleanup of begin-end matching with help of fix_event;
            # also, should make redraw close the begin if no releaseEvent came by then (but don't
            #  forget about recursive event processing) [done in a different way in redraw, bruce 060323]
            if self.__pressEvent is not None and debug_flags.atom_debug:
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

        self.checkpoint_before_drag(event, but)

        self.current_stereo_image = self.stereo_image_hit_by_event(event)
            # note: self.current_stereo_image will remain unchanged until the
            # next mouse press event. (Thus even drags into the other image
            # of a left/right pair will not change it.)
            ### REVIEW: even bareMotion won't change it -- will this cause
            # trouble for highlighting when the mouse crosses the boundary?
            # [bruce 080911 question]

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

        # piotr 080320:
        # "fast manipulation" mode where the external bonds are not displayed
        # the glpane has to be redrawn after mouse button is released
        # to show the bonds again
        #
        # this has to be moved to GlobalPreferences (this debug_pref is
        # also called in chunk.py) piotr 080325
        if debug_pref("GLPane: suppress external bonds when dragging?",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True
                      ):
            self.gl_update()

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
        #  the other forms of recursive event processing. ###@@@
        #  So for now, I'll assume recursive event processing never happens in the event handler
        #  (called just before this method is called) -- then the simplest
        #  scheme for this code is to do it all entirely after the mode's event handler (as done in this routine),
        #  rather than checking __attrs before the handlers and using the values afterwards. [bruce 060126])

        # Maybe we should simulate a pressEvent's checkpoint here, if there wasn't one, to fix hypothetical bugs from a
        # missing one. Seems like a good idea, but save it for later (maybe the next commit, maybe a bug report). [bruce 060323]

        if self.__pressEvent is not None: ###@@@ and if no buttons are still pressed, according to fix_event?
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
                    #  or (better) put it into these checkpoint methods. ###@@@)
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

        # russ 080527: Fix Bug 2606 (highlighting not turned on after wheel event.)
        self.wheelHighlight = True

        return

    #== Timer helper methods

    highlightTimer = None #bruce 070110 (was not needed before)

    def _timer_debug_pref(self):
        #bruce 070110 split this out and revised it
        #bruce 080129 removed non_debug and changed prefs_key
        # (so all developer settings for this will start from scratch),
        # since behavior has changed since it was first implemented
        # in a way that makes it likely that changing this will cause bugs.
        res = debug_pref("GLPane: timer interval",
                         Choice([100, 0, 5000, None]),
                         # NOTE: the default value defined here (100)
                         # determines the usual timer behavior,
                         # not just debug pref behavior.
                         ## non_debug = True,
                         prefs_key = "A10 devel/glpane timer interval"
                         )
        if res is not None and type(res) is not type(1):
            # support prefs values stored by future versions (or by a brief bug workaround which stored "None")
            res = None
        return res

    #russ 080505: Treat focusIn/focusOut events the same as enter/leave events.
    # On the Mac at least, Cmd-Tabbing to another app window that pops up on top
    # of our pane doesn't deliver a leave event, but does deliver a focusOut.
    # Unless we handle it as a leave, the timer is left active, and a highlight
    # draw can occur.  This steals the focus from the upper window, popping NE1
    # on top of it, which is very annoying to the user.
    def focusInEvent(self, event):
        if DEBUG_BAREMOTION:
            print "focusInEvent"
            pass
        self.enterEvent(event)

    def focusOutEvent(self, event):
        if DEBUG_BAREMOTION:
            print "focusOutEvent"
            pass
        self.leaveEvent(event)

    def enterEvent(self, event): # Mark 060806. [minor revisions by bruce 070110]
        """
        Event handler for when the cursor enters the GLPane.

        @param event: The mouse event after entering the GLpane.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        if DEBUG_BAREMOTION:
            print "enterEvent"
            pass
        choice = self._timer_debug_pref()
        if choice is None:
            if not env.seen_before("timer is turned off"):
                print "warning: GLPane's timer is turned off by a debug_pref"
            if self.highlightTimer:
                self.killTimer(self.highlightTimer)
                if DEBUG_BAREMOTION:
                    print "  Killed highlight timer %r"% self.highlightTimer
                    pass
                pass
            self.highlightTimer = None
            return
        if not self.highlightTimer:
            interval = int(choice)
            self.highlightTimer = self.startTimer(interval) # Milliseconds interval.
            if DEBUG_BAREMOTION:
                print "  Started highlight timer %r"% self.highlightTimer
                pass
            pass
        return

    def leaveEvent(self, event): # Mark 060806. [minor revisions by bruce 070110]
        """
        Event handler for when the cursor leaves the GLPane.

        @param event: The last mouse event before leaving the GLpane.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        if DEBUG_BAREMOTION:
            print "leaveEvent"
            pass
        # If an object is "hover highlighted", unhighlight it when leaving the GLpane.
        if self.selobj is not None:
            ## self.selobj = None # REVIEW: why not set_selobj?
            self.set_selobj(None) #bruce 080508 bugfix (turn off MT highlight)
            self.gl_update_highlight() # REVIEW: this redraw can be slow -- is it worthwhile?
            pass

        # Kill timer when the cursor leaves the GLpane.
        # It is (re)started in enterEvent() above.
        if self.highlightTimer:
            self.killTimer(self.highlightTimer)
            if DEBUG_BAREMOTION:
                print "  Killed highlight timer %r"% self.highlightTimer
                pass
            self.highlightTimer = None
            pass
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
            if debug_flags.atom_debug or DEBUG_BAREMOTION:
                print "note (not a bug unless happens a lot): GLPane got timerEvent but has no timer"
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
        # This event is intended only for eventual use in selectMode.mouse_exceeded_distance
        # by certain graphicsModes, but is sent to all graphicsModes.
        if (xy_now == xy_last and self.button == None) or self.wheelHighlight:
            # Only pass a 'MouseMove" mouse event once to bareMotion() when the mouse stops 
            # and hasn't moved since the last timer event.

            if self.triggerBareMotionEvent or self.wheelHighlight:
                #print "Calling bareMotion. xy_now = ", xy_now
                mouseEvent = QMouseEvent( QEvent.MouseMove, cursorPos, Qt.NoButton, Qt.NoButton, Qt.NoModifier)
                                #Qt.NoButton & Qt.MouseButtonMask,
                                #Qt.NoButton & Qt.KeyButtonMask )
                if DEBUG_BAREMOTION:
                    #bruce 080129 re highlighting bug 2606 reported by Paul
                    print "debug fyi: calling %r.bareMotion with fake zero-motion event" % (self.graphicsMode,)

                # russ 080527: Fix Bug 2606 (highlighting not turned on after wheel event.)
                # Keep generating fake zero-motion events until one is handled rather than discarded.
                discarded = self.graphicsMode.bareMotion(mouseEvent)
                if not discarded:
                    self.triggerBareMotionEvent = False
                    self.wheelHighlight = False

            # The cursor hasn't moved since the last timer event. See if we should display the tooltip now.
            # REVIEW:
            # - is it really necessary to call this 10x/second?
            # - Does doing so waste significant cpu time?
            # [bruce 080129 questions]
            helpEvent = QHelpEvent(QEvent.ToolTip, QPoint(cursorPos), QPoint(cursor.pos()) )
            if self.dynamicToolTip: # Probably always True. Mark 060818.
                self.dynamicToolTip.maybeTip(helpEvent) # maybeTip() is responsible for displaying the tooltip.

        else:

            self.cursorMotionlessStartTime = time.time()
                # Reset the cursor motionless start time to "zero" (now).
                # Used by maybeTip() to support the display of dynamic tooltips.

            self.triggerBareMotionEvent = True

        self.timer_event_last_xy = xy_now
        return

    #== end of Timer helper methods

    def mousepoints(self, event, just_beyond = 0.0):
        """
        @return: a pair (2-tuple) of points (Numeric arrays of x,y,z in model
                 coordinates) that lie under the mouse pointer. The first point
                 lies at (or just beyond) the near clipping plane; the other
                 point lies in the plane of the center of view.
        @rtype: (point, point)

        @param just_beyond: how far beyond the near clipping plane
                            the first point should lie. Default value of 0.0
                            means on the near plane; 1.0 would mean on the
                            far plane. Callers often pass 0.01 for this.
                            Some callers pass this positionally, and some as
                            a keyword argument.
        @type just_beyond: float

        If stereo is enabled, self.current_stereo_image determines which
        stereo image's coordinate system is used to get the mousepoints
        (even if the mouse pointer is not inside that image now).
        (Note that self.current_stereo_image is set (by other code in self)
        based on the mouse position in each mouse press event. It's not affected
        by mouse position in mouse drag, release, or bareMotion events.)
        """
        x = event.pos().x()
        y = self.height - event.pos().y()
        
        # modify modelview matrix in side-by-side stereo view modes [piotr 080529]
        # REVIEW: does no_clipping disable enough? especially in anaglyph mode,
        # we might want to disable even more side effects, for efficiency.
        # [bruce 080912 comment]
        self._enable_stereo(self.current_stereo_image, no_clipping = True)

        p1 = A(gluUnProject(x, y, just_beyond))
        p2 = A(gluUnProject(x, y, 1.0))

        self._disable_stereo()

        los = self.lineOfSight

        k = dot(los, -self.pov - p1) / dot(los, p2 - p1)

        p2 = p1 + k*(p2-p1)
        return (p1, p2)

    def SaveMouse(self, event):
        """
        Extracts the mouse position from event and saves it in the I{MousePos}
        property. (localizes the API-specific code for extracting the info)

        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        self.MousePos = V(event.pos().x(), event.pos().y())

    def setGlobalDisplayStyle(self, disp):
        """
        Set the global display style of self (the GLPane).

        @param disp: The desired global display style, which
                     should be one of the following constants
                     (this might not be a complete list;
                      for all definitions see constants.py):
                     - diDEFAULT (the "NE1 start-up display style", as defined
                       in the Preferences | General dialog)
                     - diLINES (Lines display style)
                     - diTUBES (Tubes display style)
                     - diBALL (Ball and stick display style)
                     - diTrueCPK (Space filling display style)
                     - diDNACYLINDER (DNA cylinder display style)
        @type  disp: int

        @note: doesn't update the MT, and callers typically won't need to,
               since the per-node display style icons are not changing.

        @see: setDisplayStyle methods in some model classes

        @see: setDisplayStyle_of_selection method in another class
        """
        # review docstring: what about diINVISIBLE? diPROTEIN?
        from utilities.constants import diDNACYLINDER
        from utilities.constants import diPROTEIN
        
        if disp == diDEFAULT:
            disp = env.prefs[ startupGlobalDisplayStyle_prefs_key ]
        #e someday: if self.displayMode == disp, no actual change needed??
        # not sure if that holds for all init code, so being safe for now.
        self.displayMode = disp

        # piotr 080714: Remember last non-reduced display style.
        if disp != diDNACYLINDER and \
           disp != diPROTEIN:
            self.lastNonReducedDisplayMode = disp
            
        # Huaicai 3/29/05: Add the condition to fix bug 477 (keep this note)
        if self.assy.commandSequencer.currentCommand.commandName == 'CRYSTAL':
            self.win.statusBar().dispbarLabel.setEnabled(False)
            self.win.statusBar().globalDisplayStylesComboBox.setEnabled(False)
        else:
            self.win.statusBar().dispbarLabel.setEnabled(True)
            self.win.statusBar().globalDisplayStylesComboBox.setEnabled(True)

        self.win.statusBar().globalDisplayStylesComboBox.setDisplayStyle(disp)
        # Note: we don't need to call changeapp on all chunks with no individual
        # display style set, because their draw methods compare self.displayMode
        # (or their currently set individual display style) to the one they used
        # to make their display lists. [bruce 080305 comment]
        return
    
    def get_angle_made_with_screen_right(self, vec):
        """
        Returns the angle (in degrees) between screen right direction
        and the given vector. It returns positive angles (between 0 and
        180 degrees) if the vector lies in first or second quadrants
        (i.e. points more up than down on the screen). Otherwise the
        angle returned is negative.
        """
        #Ninad 2008-04-17: This method was added AFTER rattlesnake rc2.
        #bruce 080912 bugfix: don't give theta the wrong sign when
        # dot(vec, self.up) < 0 and dot(vec, self.right) == 0.
        vec = norm(vec)        
        theta = angleBetween(vec, self.right)
        if dot(vec, self.up) < 0:
            theta = - theta
        return theta

    def dragstart_using_GL_DEPTH(self, 
                                 event, 
                                 more_info = False,
                                 always_use_center_of_view = False): #bruce 061206 added more_info option
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
        @param always_use_center_of_view: If True it always uses the depth of the
             center of view (returned by self.mousepoints) . This is used by
             Line_GraphicsMode.leftDown(). 

        """
        #@NOTE: Argument  always_use_center_of_view added on April 20, 2008 to 
        #fix a bug for Mark's Demo.
        #at FNANO08 -- This was the bug: In CPK display style,, start drawing 
        #a duplex,. When the rubberbandline draws 20 basepairs, move the cursor 
        #just over the last sphere drawn and click to finish duplex creation
        #Switch the view to left view -- the duplex axis is not vertical 

        wX = event.pos().x()
        wY = self.height - event.pos().y()
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        depth = wZ[0][0]
        farZ = GL_FAR_Z

        if depth >= farZ or always_use_center_of_view:
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
        Returns the 3D point on a specified plane, at the coordinates of event
              
        @param plane: The point is computed such that it lies on this Plane 
                      at the given event coordinates. 
                     
        @see: Line_GraphicsMode.leftDown()
        @see: DnaDuplex_GraphicsMode.
        
        @TODO: There will be some cases where the intersection of the mouseray 
        and the given plane is not possible or returns a very large number.
        Need to discuss this. 
        """
        # TODO: refactor this so the caller extracts Plane attributes,
        # and this method only receives geometric parameters (more general).
        # [bruce 080912 comment]
        
        #First compute the intersection point of the mouseray with the plane        
        p1, p2     = self.mousepoints(event)
        linePoint  = p2
        lineVector = norm(p2 - p1)
        planeAxis  = plane.getaxis()
        planeNorm  = norm(planeAxis)
        planePoint = plane.center
        
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

        @see: gl_update_duration (defined in superclass GLPane_view_change_methods)
        """
        self._needs_repaint = 1 #bruce 050516 experiment
        # (To restore the pre-050127 behavior, it would be sufficient to
        # change the next line from "self.update()" to "self.paintGL()".)
        self.update()
            # QWidget.update() method -- ask Qt to call self.paintGL()
            # (via some sort of paintEvent to our superclass)
            # very soon after the current event handler returns
            #
            ### REVIEW: why does this not call self.updateGL() like ThumbView.py does?
            # I tried calling self.updateGL() here, and got an exception
            # inside a paintGL subroutine (AttributeError on self.guides),
            # captured somewhere inside it by print_compact_stack,
            # which occurred before a print statement here just after my call.
            # The toplevel Python call shown in print_compact_stack was paintGL.
            # This means: updateGL causes an immediate call by Qt into paintGL,
            # in the same event handler, but from C code which stops print_compact_stack
            # from seeing what was outside it. (Digression: we could work around
            # that by grabbing the stack frame here and storing it somewhere!)
            # Conclusion: never call updateGL in GLPane, and review whether
            # ThumbView should continue to call it. [bruce 080912 comment]
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

    def model_is_valid(self): #bruce 080117
        """
        whether our model is currently valid for drawing
        [overrides GLPane_minimal method]
        """
        return self.assy.assy_valid

    ### def paintGL(self):                              ###
    ###     profile( self.paintGL2)                     ###
    ###     doProfile(False)                            ###

    def paintGL(self): #bruce 050127 revised docstring to deprecate direct calls
        """
        [PRIVATE METHOD -- call gl_update instead!]

        The main screen-drawing method, called internally by Qt when our
        superclass needs to repaint (and quite a few other times when it
        doesn't need to).

        THIS METHOD SHOULD NOT BE CALLED DIRECTLY
        BY OUR OWN CODE -- CALL gl_update INSTEAD.
        """

        if TEST_DRAWING:                # See prototype/test_drawing.py .
            test_drawing(self)
            return

        self._frustum_planes_available = False

        if not self.initialised:
            return

        if not self.model_is_valid():
            #bruce 080117 bugfix in GLPane and potential bugfix in ThumbView;
            # for explanation see my same-dated comment in files_mmp
            # near another check of assy_valid.
            return

        env.after_op() #bruce 050908; moved a bit lower, 080117
            # [disabled in changes.py, sometime before 060323;
            #  probably obs as of 060323; see this date below]

        # SOMEDAY: it might be good to set standard GL state, e.g. matrixmode,
        # before checking self.redrawGL here, in order to mitigate bugs in other
        # code (re bug 727), but only if the current mode gets to redefine what
        # "standard GL state" means, since some modes which use this flag to
        # avoid standard repaints also maintain some GL state in nonstandard
        # forms (e.g. for XOR-mode drawing). [bruce 050707 comment]

        if not self.redrawGL:
            return

        self._call_whatever_waits_for_gl_context_current() #bruce 071103

        if not self._needs_repaint and \
           pref_skip_redraws_requested_only_by_Qt():
            # if we don't think this redraw is needed,
            # skip it (but print '#' if atom_debug is set -- disabled as of 080512).

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
            # easily fixed. [Bug no longer exists as of 080512; I don't recall
            # why. But I have had this always on for a long time and don't
            # recall noticing any bugs. So I'm turning it on by default, and
            # disabling the printing of '#'; if we need it back for debugging
            # we can add a debug_pref for it and/or for drawing redraw_counter
            # as text in the frame. bruce 080512]
            #
            # older comments:
            #
            #bruce 050516 experiment
            #
            # This probably happens fairly often when Qt calls paintGL but
            # our own code didn't change anything and therefore didn't call
            # gl_update.
            #
            # This is known to happen when a context menu is put up,
            # the main app window goes into bg or fg, etc.
            #
            # SOMEDAY:
            # An alternative to skipping the redraw would be to optimize it
            # by redrawing a saved image. We're likely to do that for other
            # reasons as well (e.g. to optimize redraws in which only the
            # selection or highlighting changes).

            # disabling this debug print (see long comment above), bruce 080512
            ## if debug_flags.atom_debug:
            ##     sys.stdout.write("#") # indicate a repaint is being skipped
            ##     sys.stdout.flush()

            return # skip the following repaint

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
            # like model_changed, even when it doesn't need to (still true
            # 080804). They all need to be revised to be fast when no changes
            # are needed, or this will make redraw needlessly slow.
            # [bruce 071115/080804 comment]

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

        self._use_frustum_culling = use_frustum_culling()
            # there is some overhead calling the debug_pref,
            # and we want the same answer used throughout
            # one call of paintGL
            # piotr 080402: uses GlobalPreferences
        assert not self._frustum_planes_available

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
                    # This was happening when we used x, y = exact 0,
                    # and was causing the image to not get drawn sometimes (when mousewheel zoom was used).
                    # It can still happen for extreme values of mousewheel zoom (close to the ones
                    # which cause OpenGL exceptions), mostly only when pos = (0, 0) but not entirely.
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

    def _restore_modelview_stack_depth(self):
        """
        restore GL_MODELVIEW_STACK_DEPTH to 1, if necessary
        """
        #bruce 040923 [updated 080910]:
        # I'd like to reset the OpenGL state
        # completely, here, including the stack depths, to mitigate some
        # bugs. How??  Note that there might be some OpenGL init code
        # earlier which I'll have to not mess up, including _setup_display_lists.
        #   What I ended up doing is just to measure the
        # stack depth and pop it 0 or more times to make the depth 1.
        #   BTW I don't know for sure whether this causes a significant speed
        # hit for some OpenGL implementations (esp. X windows)...
        # TODO: test the performance effect sometime.
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
    # if they want to get properly updated when graphics prefs change. [bruce 050804 guess]

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

    ## selobj = None #bruce 050609

    _selobj = None #bruce 080509 made this private

    def __get_selobj(self): #bruce 080509
        return self._selobj

    def __set_selobj(self, val): #bruce 080509
        self.set_selobj(val)
            # this indirection means a subclass could override set_selobj,
            # or that we could revise this code to pass it an argument
        return

    selobj = property( __get_selobj, __set_selobj)
        #bruce 080509 bugfix for MT crosshighlight sometimes lasting too long

    def render_scene(self):#bruce 061208 split this out so some modes can override it (also removed obsolete trans_feature experiment)

        #k not sure whether next things are also needed in the split-out standard_repaint [bruce 050617]

        drawing_globals.glprefs.update() #bruce 051126; kluge: have to do this before lighting *and* inside standard_repaint_0

        self.setup_lighting_if_needed() # defined in GLPane_lighting_methods

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


    def standard_repaint_0(self):

        # do something (what?) so prefs changes do gl_update when needed [bruce 051126]
        drawing_globals.glprefs.update()
            # (kluge: have to do this before lighting *and* inside standard_repaint_0)

        self.clear_and_draw_background( GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
            # also sets self.fogColor

        # fog_test_enable debug_pref can be removed if fog is implemented fully
        # (added by bradg 20060224)
        # piotr 080605 1.1.0 rc1 - replaced fog debug pref with user pref
        fog_test_enable = env.prefs[fogEnabled_prefs_key]

        if fog_test_enable:
            # piotr 080515 fixed fog
            # I think that the bbox_for_viewing_model call can be expensive.
            # I have to preserve this value or find another way of computing it.
            bbox = self.assy.bbox_for_viewing_model()
            scale = bbox.scale()
            enable_fog()
            setup_fog(self.vdist - scale, self.vdist + scale, self.fogColor)
            # [I suspect the following comment is about a line that has since
            #  been moved elsewhere -- bruce 080911]
            # this next line really should be just before rendering
            # the atomic model itself.  I dunno where that is. [bradg I think]

        # ask mode to validate self.selobj (might change it to None)
        # (note: self.selobj is used in do_glselect_if_wanted)
        selobj, hicolor = self.validate_selobj_and_hicolor()

        # do modelview setup (needed for GL_SELECT or regular drawing)
        self._setup_modelview()
            #bruce 050608 moved modelview setup here, from just before the mode.Draw call

        # set self.stereo_* attributes based on current user prefs values
        # (just once per draw event, before anything might use these attributes)
        self._update_stereo_settings()
        
        # do GL_SELECT drawing if needed (for hit test of objects with mouse)

        ###e note: if any objects moved since they were last rendered, this hit-test will still work (using their new posns),
        # but the later depth comparison (below) might not work right. See comments there for details.

        self.glselect_dict.clear()
            # this will be filled iff we do a gl_select draw,
            # then used only in the same paintGL call to alert some objects they might be the one under the mouse

        self.do_glselect_if_wanted() # note: this sets up its own special projection matrix

        self._setup_projection()

        # Compute frustum planes required for frustum culling - piotr 080331
        # Moved it right after _setup_projection is called (piotr 080331)
        # Note that this method is also called by "do_glselect_if_wanted".
        # The second call will re-compute the frustum planes according to 
        # the current projection matrix.
        if self._use_frustum_culling:
            self._compute_frustum_planes()

        # In the glselect_wanted case, we now know (in glselect_dict) which objects draw any pixels at the mouse position,
        # but not which one is in front (the near/far info from GL_SELECT has too wide a range to tell us that).
        # So we have to get them to tell us their depth at that point (as it was last actually drawn)
            ###@@@ should do that for bugfix; also selobj first
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

        # draw according to self.graphicsMode

        glMatrixMode(GL_MODELVIEW) # this is assumed within Draw methods

        vboLevel = drawing_globals.use_drawing_variant
        
        for stereo_image in self.stereo_images_to_draw:
            self._enable_stereo(stereo_image)

            if fog_test_enable:
                enable_fog()
                
            try: # try/finally for drawing_phase
                self.drawing_phase = 'main'

                if vboLevel == 6:   # russ 080714
                    drawing_globals.sphereShader.configShader(self)
                    pass

                self.graphicsMode.Draw()
            finally:
                self.drawing_phase = '?'

            if fog_test_enable:
                disable_fog()            
                
            # highlight selobj if necessary, by drawing it again in highlighted
            # form (never inside fog).
            # It was already drawn normally, but we redraw it now for two reasons:
            # - it might be in a display list in non-highlighted form (and if so,
            #   the above draw used that form);
            # - we need to draw it into the stencil buffer too, so mode.bareMotion
            #   can tell when mouse is still over it.
            if selobj is not None:
                self.draw_highlighted_objectUnderMouse(selobj, hicolor)
                    # REVIEW: is it ok that the mode had to tell us selobj and hicolor
                    # (and validate selobj) before drawing the model?

            self._disable_stereo()
            continue # to next stereo_image

        ### REVIEW [bruce 080911 question]:
        # why is Draw_after_highlighting not inside the loop over stereo_image? 
        # Is there any reason it should not be moved into that loop?
        # I.e. is there a reason to do it only once and not twice?
        # For water surface this may not matter
        # but for its use in deprecated ESPImage class
        # (draw transparent stuff) it seems like a bug.
        # I am not sure if it has other uses now.
        # (I'll check shortly, when I have time.)
        #
        # Piotr reply: Yes, I think this is a bug. It should be moved inside the stereo loop.

        try: # try/finally for drawing_phase
            self.drawing_phase = 'main/Draw_after_highlighting'
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
            if debug_flags.atom_debug:
                print_compact_traceback( "atom_debug: exception in self.part.draw_text_label(self): " )
            else:
                print "bug: exception in self.part.draw_text_label; use ATOM_DEBUG to see details"
        self.drawing_phase = '?'

        # draw coordinate-orientation arrows at upper right corner of glpane
        if env.prefs[displayCompass_prefs_key]:
            self.drawcompass()
            # review: needs drawing_phase? [bruce 070124 q]

        for stereo_image in self.stereo_images_to_draw:
            self._enable_stereo(stereo_image, preserve_colors = True)

            # REVIEW: can we simplify and/or optim by moving this into the same
            # stereo_image loop used earlier for graphicsMode.Draw?
            # [bruce 080911 question]
            
            # Draw the Origin axes.
            # WARNING: this code is duplicated, or almost duplicated,
            # in GraphicsMode.py and GLPane.py.
            # It should be moved into a common method in drawers.py.
            # [bruce 080710 comment]

            #ninad060921 The following draws a dotted origin axis if the correct preference is checked. 
            # The GL_DEPTH_TEST is disabled while drawing this so that if axis is below a model, 
            # it will just draw it as dotted line. (Remember that we are drawing 2 origins superimposed over each other;
            # the dotted form will be visible only when the solid form is obscured by a model in front of it.)
            if env.prefs[displayOriginAxis_prefs_key]:
                if env.prefs[displayOriginAsSmallAxis_prefs_key]:
                    drawOriginAsSmallAxis(self.scale, (0.0, 0.0, 0.0), dashEnabled = True)
                else:
                    drawaxes(self.scale, (0.0, 0.0, 0.0), coloraxes = True, dashEnabled = True)

            self._disable_stereo()

##        # REVIEW: isn't this redundant with another call of disable_fog above? [bruce 080911 question]
##        # piotr reply: Yes, it is redundant, it should be removed. [did that, bruce 080911, needs TEST]
##        if fog_test_enable:
##            # this next line really should be just after rendering
##            # the atomic model itself.  I dunno where that is. [bradg]
##            disable_fog()            

        # draw some test images related to the confirmation corner

        ccdp1 = debug_pref("Conf corner test: redraw at lower left",
                           Choice_boolean_False,
                           prefs_key = True)
        ccdp2 = debug_pref("Conf corner test: redraw in-place",
                           Choice_boolean_False,
                           prefs_key = True) # default changed, same prefs_key

        if ccdp1 or ccdp2:
            self.grab_conf_corner_bg_image() #bruce 070626 (needs to be done before draw_overlay)

        if ccdp1:
            self.draw_conf_corner_bg_image((0, 0))

        if ccdp2:
            self.draw_conf_corner_bg_image()
        
        # draw various overlays

        self.drawing_phase = 'overlay'

        # Draw ruler(s) if "View > Rulers" is checked.
        if env.prefs[displayRulers_prefs_key]:
            if (self.ortho or env.prefs[showRulersInPerspectiveView_prefs_key]):
                self.guides.draw()

        # draw the confirmation corner
        try:
            glMatrixMode(GL_MODELVIEW) #k needed?
            self.graphicsMode.draw_overlay() #bruce 070405 (misnamed)
        except:
            print_compact_traceback( "exception in self.graphicsMode.draw_overlay(): " )
        
        self.drawing_phase = '?'

        # restore standard glMatrixMode, in case drawing code outside of paintGL forgets to do this [precaution]
        glMatrixMode(GL_MODELVIEW)
            # (see discussion in bug 727, which was caused by that)
            # (it might also be good to set mode-specific standard GL state before checking self.redrawGL in paintGL #e)\

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
            if debug_flags.atom_debug:
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
            wX, wY, self.targetdepth = self.glselect_wanted # wX, wY is the point to do the hit-test at
                # targetdepth is the depth buffer value to look for at that point, during ordinary drawing phase
                # (could also be used to set up clipping planes to further restrict hit-test, but this isn't yet done)
                # (Warning: targetdepth could in theory be out of date, if more events come between bareMotion
                #  and the one caused by its gl_update, whose paintGL is what's running now, and if those events
                #  move what's drawn. Maybe that could happen with mousewheel events or (someday) with keypresses
                #  having a graphical effect. Ideally we'd count intentional redraws, and disable this picking in that case.)
            self.wX, self.wY = wX, wY
            self.glselect_wanted = 0
            self.current_glselect = (wX, wY, 3, 3) #bruce 050615 for use by nodes which want to set up their own projection matrix
            self._setup_projection( glselect = self.current_glselect ) # option makes it use gluPickMatrix
                # replace 3, 3 with 1, 1? 5, 5? not sure whether this will matter... in principle should have no effect except speed
            if self._use_frustum_culling:
                self._compute_frustum_planes() 
                # piotr 080331 - the frustum planes have to be setup after the 
                # projection matrix is setup. I'm not sure if there may
                # be any side effects - see the comment below about
                # possible optimization.
            glSelectBuffer(self.glselectBufferSize)
            glRenderMode(GL_SELECT)
            glInitNames()
            ## glPushName(0) # this would be ignored if not in GL_SELECT mode, so do it after we enter that! [no longer needed]
            glMatrixMode(GL_MODELVIEW)

            try:
                self.drawing_phase = 'glselect' #bruce 070124

                for stereo_image in self.stereo_images_to_draw:
                    self._enable_stereo(stereo_image)

                    self.graphicsMode.Draw()
                        # OPTIM: should perhaps optim by skipping chunks based on bbox... don't know if that would help or hurt
                        # Note: this might call some display lists which, when created, registered namestack names,
                        # so we need to still know those names!

                    self._disable_stereo()

            except:
                print_compact_traceback("exception in mode.Draw() during GL_SELECT; ignored; restoring modelview matrix: ")
                glMatrixMode(GL_MODELVIEW)
                self._setup_modelview( ) ### REVIEW: correctness of this is unreviewed!
                # now it's important to continue, at least enough to restore other gl state

            self._frustum_planes_available = False # piotr 080331 
                # just to be safe and not use the frustum planes computed for 
                # the pick matrix
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
            for (near, far, names) in hit_records: # see example code, renderpass.py
                ## print "hit record: near, far, names:", near, far, names
                    # e.g. hit record: near, far, names: 1439181696 1453030144 (1638426L,)
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
##                            print " new last element maps to %r" % self.object_for_glselect_name(names[-1])
                if names:
                    # for now, len is always 0 or 1, i think; if not, best to use only the last element...
                    # tho if we ever support "name/subname paths" we'll probably let first name interpret the remaining ones.
                    ###e in fact, when nodes change projection or viewport for kids, and/or share their kids, they need to
                    # put their own names on the stack, so we'll know how to redraw the kids, or which ones are meant when shared.
                    if debug_flags.atom_debug and len(names) > 1: ###@@@ bruce 060725
                        if len(names) == 2 and names[0] == names[1]:
                            if not env.seen_before("dual-names bug"): # this happens for Atoms, don't know why (colorsorter bug??)
                                print "debug (once-per-session message): why are some glnames duplicated on the namestack?", names
                        else:
                            # Note: as of sometime before 080411, this became common --
                            # I guess that chunks (which recently acquired glselect names)
                            # are pushing their names even while drawing their atoms and bonds.
                            # I am not sure if this can cause any problems -- almost surely not
                            # directly, but maybe the nestedness of highlighted appearances could
                            # violate some assumptions made by the highlight code... anyway,
                            # to reduce verbosity I need to not print this when the deeper name
                            # is that of a chunk, and there are exactly two names. [bruce 080411]
                            if len(names) == 2 and \
                               isinstance( self.object_for_glselect_name(names[0]), self.assy.Chunk ):
                                if not env.seen_before("nested names for Chunk"):
                                    print "debug (once-per-session message): nested glnames for a Chunk: ", names
                            else:
                                print "debug fyi: len(names) == %d (names = %r)" % (len(names), names)
                    obj = self.object_for_glselect_name(names[-1]) #k should always return an obj
                    if obj is None:
                        print "bug: obj_with_glselect_name returns None for name %r at end of namestack %r" % (names[-1],names)
                    self.glselect_dict[id(obj)] = obj # now these can be rerendered specially, at the end of mode.Draw
            #e maybe we should now sort glselect_dict by "hit priority" (for depth-tiebreaking), or at least put selobj first.
            # (or this could be done lower down, where it's used.)

        return # from do_glselect_if_wanted

    def object_for_glselect_name(self, glname): #bruce 080220
        """
        """
        return self.assy.object_for_glselect_name(glname)

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
            glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE) # don't draw color pixels

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
        """
        Set self._selobj to selobj (might be None) and do appropriate updates.
        Possible updates include:

        - env.history.statusbar_msg( selobj.mouseover_statusbar_message(),
                                     or "" if selobj is None )

        - help the model tree highlight the nodes containing selobj

        @note: as of 080509, all sets of self.selobj call this method, via a
               property. If some of them don't want all our side effects,
               they will need to call this method directly and pass options
               [nim] to prevent those.
        """
        # note: this method should access and modify self._selobj,
        # not self.selobj (setting that here would cause an infinite recursion).
        if selobj is not self._selobj:
            previous_selobj = self._selobj
            self._selobj = selobj #bruce 080507 moved this here

            # Note: we don't call gl_update_highlight here, so the caller needs to
            # if there will be a net change of selobj. I don't know if we should call it here --
            # if any callers call this twice with no net change (i.e. use this to set selobj to None
            # and then back to what it was), it would be bad to call it here. [bruce 070626 comment]
            if _DEBUG_SET_SELOBJ:
                # todo: also include "why" argument, and make more calls pass one
                print_compact_stack("_DEBUG_SET_SELOBJ: %r -> %r: " % (previous_selobj, selobj))
            #bruce 050702 partly address bug 715-3 (the presently-broken Build mode statusbar messages).
            # Temporary fix, since Build mode's messages are better and should be restored.
            if selobj is not None:
                try:
                    try:
                        #bruce 050806 let selobj control this
                        method = selobj.mouseover_statusbar_message
                            # only defined for some objects which inherit Selobj_API
                    except AttributeError:
                        msg = "%s" % (selobj,)
                    else:
                        msg = method()
                except:
                    msg = "<exception in selobj statusbar message code>"
                    if debug_flags.atom_debug:
                        #bruce 070203 added this print; not if 1 in case it's too verbose due as mouse moves
                        print_compact_traceback(msg + ': ')
                    else:
                        print "bug: %s; use ATOM_DEBUG to see details" % msg
            else:
                msg = " "

            env.history.statusbar_msg(msg)

            if pref_show_highlighting_in_MT():
                # help the model tree highlight the nodes containing selobj
                # [bruce 080507 new feature]
                self._update_nodes_containing_selobj(
                    selobj, # might be None, and we do need to call this then
                    repaint_nodes = True,
                    # this causes a side effect which is the only reason we're called here
                    even_if_selobj_unchanged = False
                    # optimization;
                    # should be safe, since changes to selobj parents or node parents
                    # which would otherwise require this to be passed as true
                    # should also call mt_update separately, thus doing a full
                    # MT redraw soon enough
                )
            pass # if selobj is not self._selobj

        self._selobj = selobj # redundant (as of bruce 080507), but left in for now

        #e notify more observers?
        return

    def _update_nodes_containing_selobj(self,
                                        selobj,
                                        repaint_nodes = False,
                                        even_if_selobj_unchanged = False
                                        ): #bruce 080507
        """
        private; recompute self._nodes_containing_selobj from the given selobj,
        optimizing when selobj and/or our result has not changed,
        and do updates as needed and as options specify.

        @return: None

        @param repaint_nodes: if this is true and we change our cached value of
                              self._nodes_containing_selobj, then also call the
                              model tree method repaint_some_nodes.

        @param even_if_selobj_unchanged: if this is true, assume that our
                                         result might differ even if selobj
                                         itself has not changed since our
                                         last call.

        @note: called in two circumstances:
        - when we know selobj has changed (repaint_nodes should be True then)
        - when the MT explicitly calls get_nodes_containing_selobj
          (repaint_nodes should probably be False then)

        @note: does not use or set self._selobj (assuming external code it calls
               doesn't do so).

        @warning: if this method or code it calls sets self.selobj, that would
                  cause infinite recursion, since self.selobj is a property
                  whose setter calls this method.
        """
        # review: are there MT update bugs related to dna updater moving nodes
        # into new groups?
        if selobj is self._nodes_containing_selobj_is_from_selobj and \
           not even_if_selobj_unchanged:
            # optimization: nothing changed, no updates needed
            return

        # recompute and perhaps update
        nodes = []
        if selobj is not None:
            try:
                method = selobj.nodes_containing_selobj
            except AttributeError:
                # should never happen, since Selobj_API defines this method
                print "bug: no method nodes_containing_selobj in %r" % (selobj,)
                pass
            else:
                try:
                    nodes = method()
                    assert type(nodes) == type([])
                except:
                    msg = "bug in %r.nodes_containing_selobj " \
                        "(or invalid return value from it)" % (selobj,)
                    print_compact_traceback( msg + ": ")
                    nodes = []
                pass
            pass
        if self._nodes_containing_selobj != nodes:
            # assume no need to sort, since they'll typically be
            # returned in inner-to-outer order
            all_changed_nodes = self._nodes_containing_selobj + nodes
                # assume duplications are ok;
                # could optim by leaving out any nodes that appear
                # in both lists, assuming the way they're highlighted in
                # the MT doesn't depend on anything but their presence
                # in the list; doesn't matter for now, since the MT
                # redraw is not yet incremental [as of 080507]
            self._nodes_containing_selobj = nodes
            if repaint_nodes:
                ## self._nodes_containing_selobj_has_changed(all_changed_nodes)
                self.assy.win.mt.repaint_some_nodes( all_changed_nodes)
                    # review: are we sure self.assy.win.mt.repaint_some_nodes will never
                    # use self.selobj by accessing it externally?
        self._nodes_containing_selobj_is_from_selobj = selobj
        return

    def get_nodes_containing_selobj(self): #bruce 080507
        """
        @return: a list of nodes that contain self.selobj
                 (possibly containing some nodes more than once).

        @warning: repeated calls with self.selobj unchanged are *not* optimized.
                  (Doing so correctly would be difficult.)
                  Callers should temporarily store our return value as needed.
        """
        self._update_nodes_containing_selobj(
            self.selobj,
            repaint_nodes = False,
            even_if_selobj_unchanged = True
        )
        return self._nodes_containing_selobj

    def preDraw_glselect_dict(self): #bruce 050609
        # We need to draw glselect_dict objects separately, so their drawing code runs now rather than in the past
        # (when some display list was being compiled), so they can notice they're in that dict.
        # We also draw them first, so that the nearest one (or one of them, if there's a tie)
        # is sure to update the depth buffer. (Then we clear it so that this drawing doesn't mess up
        # later drawing at the same depth.)
        # (If some mode with special drawing code wants to join this system, it should be refactored
        #  to store special nodes in the model which can be drawn in the standard way.)
        glMatrixMode(GL_MODELVIEW)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE) # optimization -- don't draw color pixels (depth is all we need)
        newpicked = None # in case of errors, and to record found object
        # here we should sort the objs to check the ones we most want first (esp selobj)...
        #bruce 050702 try sorting this, see if it helps pick bonds rather than invis selatoms -- it seems to help.
        # This removes a bad side effect of today's earlier fix of bug 715-1.
        objects = self.glselect_dict.values()
        items = [] # (order, obj) pairs, for sorting objects
        for obj in objects:
            if obj is self.selobj:
                order = 0
            elif isinstance(obj, Bond):
                #bruce 080402 precaution: don't say obj.__class__ is Bond,
                # in case obj has no __class__
                order = 1
            else:
                order = 2
            order = (order, id(obj))
                #bruce 080402 work around bug in Bond.__eq__ for bonds not on
                # the same atom; later on 080402 I fixed that bug, but I'll
                # leave this for safety in case of __eq__ bugs on other kinds
                # of selobjs (e.g. dependence on other.__class__)
            items.append( (order, obj) )
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
        for orderjunk, obj in items: # iterate over candidates
            try:
                method = obj.draw_in_abs_coords
            except AttributeError:
                print "bug? ignored: %r has no draw_in_abs_coords method" % (obj,)
                print "   items are:", items
            else:
                try:
                    for stereo_image in self.stereo_images_to_draw:
                        # REVIEW: would it be more efficient, and correct,
                        # to iterate over stereo images outside, and candidates
                        # inside (i.e. turn this pair of loops inside out)?
                        # I guess that would require knowing which stereo_image
                        # we're sampling in... and in that case we'd want to use
                        # only one of them anyway to do the testing
                        # (probably even if they overlap, just pick one and
                        # use that one -- see related comments in _enable_stereo).
                        # [bruce 080911 comment]
                        self._enable_stereo(stereo_image)

                        self.drawing_phase = 'selobj/preDraw_glselect_dict' # bruce 070124
                        method(self, white) # draw depth info (color doesn't matter since we're not drawing pixels)

                        self._disable_stereo()

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
                    print_compact_traceback("exception in or near %r.draw_in_abs_coords ignored: " % (obj,))
        ##e should check depth here to make sure it's near enough but not too near
        # (if too near, it means objects moved, and we should cancel this pick)
        glClear(GL_DEPTH_BUFFER_BIT) # prevent those predraws from messing up the subsequent main draws
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
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

    def drawcompass(self):
        #bruce 080910 moved body into its own file
        #bruce 080912 removed aspect argument
        drawcompass(self,
                    self.aspect,
                    self.quat,
                    self.compassPosition,
                    self.graphicsMode.compass_moved_in_from_corner,
                    env.prefs[displayCompassLabels_prefs_key]
                   )
        return
    
    # ==

    def makemenu(self, menu_spec, menu):
        # this overrides the one from DebugMenuMixin (with the same code), but that's ok,
        # since we want to be self-contained in case someone later removes that mixin class;
        # this method is called by our modes to make their context menus.
        # [bruce 050418 comment]
        return makemenu_helper(self, menu_spec, menu)

    def debug_menu_items(self): #bruce 050515
        """
        [overrides method from DebugMenuMixin]
        """
        usual = DebugMenuMixin.debug_menu_items(self)
            # list of (text, callable) pairs, None for separator
        ours = list(usual)
        try:
            # submenu for available custom modes [bruce 050515]
            # todo [080209]: just include this submenu in the DebugMenuMixin version
            # (no reason it ought to be specific to glpane)
            modemenu = self.win.commandSequencer.custom_modes_menuspec()
            if modemenu:
                ours.append(("custom modes", modemenu))
        except:
            print_compact_traceback("exception ignored: ")
        return ours

    pass # end of class GLPane

# end
