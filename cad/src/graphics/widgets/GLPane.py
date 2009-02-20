# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPane.py -- NE1's main model view. A subclass of Qt's OpenGL widget, QGLWidget.

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

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

- move more common code into GLPane_minimal [mostly done, 080914 or so,
except for GL_SELECT code, common to several files];

Some of this will make more practical some ways of optimizing the graphics code.

History:

Mostly written by Josh; partly revised by Bruce for mode code revision, 040922-24.
Revised by many other developers since then (and perhaps before).

bruce 080910 splitting class GLPane into several mixin classes in other files.

bruce 080925 removed support for GLPANE_IS_COMMAND_SEQUENCER
"""

# TEST_DRAWING has been moved to GLPane_rendering_methods

_DEBUG_SET_SELOBJ = False # do not commit with true

import sys

from OpenGL.GL import GL_STENCIL_BITS
from OpenGL.GL import glGetInteger

from command_support.GraphicsMode_API import GraphicsMode_API # for isinstance assertion

import foundation.env as env

from utilities import debug_flags

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice_boolean_False
from utilities.debug_prefs import Choice_boolean_True

from utilities.debug import print_compact_traceback, print_compact_stack

from utilities.prefs_constants import compassPosition_prefs_key
from utilities.prefs_constants import defaultProjection_prefs_key
from utilities.prefs_constants import startupGlobalDisplayStyle_prefs_key
from utilities.prefs_constants import startup_GLPane_scale_prefs_key
from utilities.prefs_constants import GLPane_scale_for_atom_commands_prefs_key
from utilities.prefs_constants import GLPane_scale_for_dna_commands_prefs_key

from utilities.constants import diDEFAULT
from utilities.constants import diDNACYLINDER
from utilities.constants import diPROTEIN
from utilities.constants import default_display_mode

from utilities.GlobalPreferences import pref_show_highlighting_in_MT

from graphics.widgets.GLPane_lighting_methods import GLPane_lighting_methods
from graphics.widgets.GLPane_frustum_methods import GLPane_frustum_methods
from graphics.widgets.GLPane_event_methods import GLPane_event_methods
from graphics.widgets.GLPane_rendering_methods import GLPane_rendering_methods
from graphics.widgets.GLPane_highlighting_methods import GLPane_highlighting_methods
from graphics.widgets.GLPane_text_and_color_methods import GLPane_text_and_color_methods
from graphics.widgets.GLPane_stereo_methods import GLPane_stereo_methods
from graphics.widgets.GLPane_view_change_methods import GLPane_view_change_methods

from graphics.widgets.GLPane_minimal import GLPane_minimal

from foundation.changes import SubUsageTrackingMixin
from graphics.widgets.GLPane_mixin_for_DisplayListChunk import GLPane_mixin_for_DisplayListChunk

from PyQt4.Qt  import QApplication, QCursor, Qt

# ==

class GLPane(
    # these superclasses need to come first, since they need to
    # override methods in GLPane_minimal:
    GLPane_lighting_methods, # needs to override _setup_lighting
    GLPane_frustum_methods, # needs to override is_sphere_visible etc
    GLPane_event_methods, # needs to override makeCurrent, setCursor,
        # and many *Event methods (not sure if GLPane_minimal defines
        # those, so it may not matter)
    GLPane_rendering_methods, # needs to override paintGL, several more
    
    # these don't yet need to come first, but we'll put them first
    # anyway in case someone adds a default def of some method
    # into GLPane_minimal in the future:
    GLPane_highlighting_methods,
    GLPane_text_and_color_methods,
    GLPane_stereo_methods,
    GLPane_view_change_methods,

    GLPane_minimal, # the "main superclass"; inherits QGLWidget

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

    Qt-called methods are overridden in some superclasses:
    * GLPane_event_methods overrides makeCurrent, setCursor, and many *Event methods
    * this class overrides paintGL, resizeGL, initializeGL

    Effectively a singleton object:

    * owned by main window (perhaps indirectly via class PartWindow)

    * never remade duringan NE1 session

    * contains public references to other singletons
      (e.g. win (permanent), assy (sometimes remade))

    * some old code stores miscellaneous attributes
      inside it (e.g. shape, stored by Build Crystal)

    A few of the GLPane's public attributes:

    * several "point of view" attributes (some might be inherited
      from superclass GLPane_minimal)

    * graphicsMode - an instance of GraphicsMode_API
    """
    # Note: classes GLPane and ThumbView still share lots of code,
    # which ought to be merged into their common superclass GLPane_minimal.
    # [bruce 070914/080909 comment]
    
    always_draw_hotspot = False #bruce 060627; not really needed, added for compatibility with class ThumbView

    assy = None #bruce 080314
    
    # the stereo attributes are maintained by the methods in
    # our superclass GLPane_stereo_methods, and used in that class,
    # and GLPane_rendering_methods, and GLPane_event_methods.
    stereo_enabled = False # piotr 080515 - stereo disabled by default
    stereo_images_to_draw = (0,)
    current_stereo_image = 0

    # note: is_animating is defined and maintained in our superclass
    # GLPane_view_change_methods
    ## self.is_animating = False

    _resize_just_occurred = False #bruce 080922
    
    #For performance reasons, whenever the global display style
    #changes, the current cursor is replaced with an hourglass cursor.
    #The following flag determines whether to turn off this wait cursor.
    #(It is turned off after global display style operation is complete.
    # see self._setWaitCursor_globalDisplayStyle().) [by Ninad, late 2008]
    _waitCursor_for_globalDisplayStyleChange = False 

    def __init__(self, assy, parent = None, name = None, win = None):
        """
        """
        self.name = name or "glpane" # [bruce circa 080910 revised this; probably not used]
        shareWidget = None
        useStencilBuffer = True

        GLPane_minimal.__init__(self, parent, shareWidget, useStencilBuffer)
        self.win = win

        self.partWindow = parent # used in GLPane_event_methods superclass

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

        # == User Preference initialization ==

        # Get glpane related settings from prefs db.
        # Default values are set in "prefs_table" in prefs_constants.py.
        # Mark 050919.

        self._init_background_from_prefs() # defined in GLPane_text_and_color_methods
        
        self.compassPosition = env.prefs[compassPosition_prefs_key]
            ### TODO: eliminate self.compassPosition (which is used and set,
            # in sync with this pref, in ne1_ui/prefs/Preferences.py)
            # and just use the pref directly when rendering. [bruce 080913 comment]
        
        self.ortho = env.prefs[defaultProjection_prefs_key]
            # REVIEW: should self.ortho be replaced with a property that refers
            # to that pref, or would that be too slow? If too slow, is there
            # a refactoring that would clean up the current requirement
            # to keep these in sync? [bruce 080913 questions]
        
        self.setViewProjection(self.ortho) 
            # This updates the checkmark in the View menu. Fixes bug #996 Mark 050925.

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

        # == End of User Preference initialization ==

        self._init_GLPane_rendering_methods()

        self.setAssy(assy) # leaves self.currentCommand/self.graphicsMode as nullmode, as of 050911
            # note: this loads view from assy.part (presumably the default view)

        self._init_GLPane_event_methods()

        return # from GLPane.__init__ 

    def resizeGL(self, width, height):
        """
        Called by QtGL when the drawing window is resized.
        """
        #bruce 080912 moved most of this into superclass
        self._resize_just_occurred = True
        GLPane_minimal.resizeGL(self, width, height) # call superclass method
        self.gl_update() # REVIEW: ok for superclass?
            # needed here? (Guess yes, to set needs_repaint flag)
        return

    _defer_statusbar_msg = False
    _deferred_msg = None
    _selobj_statusbar_msg = " "
    
    def paintGL(self):
        """
        [PRIVATE METHOD -- call gl_update instead!]

        The main OpenGL-widget-drawing method, called internally by Qt when our
        superclass needs to repaint (and quite a few other times when it
        doesn't need to).

        THIS METHOD SHOULD NOT BE CALLED DIRECTLY
        BY OUR OWN CODE -- CALL gl_update INSTEAD.
        """
        # debug_prefs related to bug 2961 in swapBuffers on Mac
        # (maybe specific to Leopard; seems to be a MacOS bug in which
        #  swapBuffers works but the display itself is not updated after
        #  that, or perhaps is not updated from the correct physical buffer)
        # [bruce 081222]
        debug_print_paintGL_calls = \
            debug_pref("GLPane: print all paintGL calls?",
                        Choice_boolean_False,
                        non_debug = True, # temporary ###
                        prefs_key = True )
        manual_swapBuffers = \
            debug_pref("GLPane: do swapBuffers manually?",
                        # when true, disable QGLWidget.autoBufferSwap and
                        # call swapBuffers ourselves when desired;
                        # this is required for some of the following to work,
                        # so it's also done when they're active even if it's False
                        Choice_boolean_False,
                        non_debug = True, # temporary ###
                        prefs_key = True )
        no_swapBuffers_when_nothing_painted = \
            debug_pref("GLPane: no swapBuffers when paintGL returns early?",
                        # I hoped this might fix some bugs in zoom to area
                        # rubber rect when swapBuffers behaves differently
                        # (e.g. after the bug in swapBuffers mentioned above),
                        # but it doesn't.
                        Choice_boolean_True,
                            # using True fixes a logic bug in this case,
                            # which fixes "related bug (B)" in bug report 2961
                        non_debug = True, # temporary ###
                        prefs_key = True )
        simulate_swapBuffers_with_CopyPixels = False
##        simulate_swapBuffers_with_CopyPixels = \
##            debug_pref("GLPane: simulate swapBuffers with CopyPixels?", # NIM
##                        Choice_boolean_False,
##                        non_debug = True, # temporary ###
##                        prefs_key = True )
        debug_verify_swapBuffers = False
##        debug_verify_swapBuffers = \
##            debug_pref("GLPane: verify swapBuffers worked?", # NIM
##                        # verify by reading back a changed pixel, one in each corner
##                        Choice_boolean_False,
##                        non_debug = True, # temporary ###
##                        prefs_key = True )
        if debug_verify_swapBuffers:
            manual_swapBuffers = True # required
        if simulate_swapBuffers_with_CopyPixels:
            pass ## manual_swapBuffers = True
                # not strictly required, left out for now, but put it in if this becomes real ###


        if debug_print_paintGL_calls:
            print
            print "calling paintGL"
        
        #bruce 081230 part of a fix for bug 2964
        # (statusbar not updated by hover highlighted object, on Mac OS 10.5.5-6)
        self._defer_statusbar_msg = True
        self._deferred_msg = None
        glselect_was_wanted = self.glselect_wanted 
            # note: self.glselect_wanted is defined and used in a mixin class
            # in another file; review: can this be more modular?
        
        painted_anything = self._paintGL()
            # _paintGL method is defined in GLPane_rendering_methods
            # (probably paintGL itself would work fine if defined there --
            #  untested, since having it here seems just as good)

        want_swapBuffers = True # might be modified below
        
        if painted_anything:
            if debug_print_paintGL_calls:
                print " it painted (redraw %d)" % env.redraw_counter
            pass
        else:
            if debug_print_paintGL_calls:
                print " it didn't paint ***"
                    # note: not seen during zoom to area (nor is painted); maybe no gl_update then?
            if no_swapBuffers_when_nothing_painted:
                want_swapBuffers = False
            pass

        if want_swapBuffers and manual_swapBuffers:
            # do it now (and later refrain from doing it automatically)
            self.do_swapBuffers( debug = debug_print_paintGL_calls,
                                 use_CopyPixels = simulate_swapBuffers_with_CopyPixels,
                                 verify = debug_verify_swapBuffers )
            want_swapBuffers = False # it's done, so we no longer want to do it this frame

        # tell Qt whether to do swapBuffers itself when we return
        if want_swapBuffers:
            self.setAutoBufferSwap(True)
            ## assert not simulate_swapBuffers_with_CopyPixels # Qt can't do this on its own swapBuffers call -- ok for now
            assert not debug_verify_swapBuffers # Qt can't do this on its own swapBuffers call
        else:
            self.setAutoBufferSwap(False)
            if debug_print_paintGL_calls:
                print " (not doing autoBufferSwap)"
        
        # note: before the above code was added, we could test the default state
        # like this:
        ## if not self.autoBufferSwap():
        ##     print " *** BUG: autoBufferSwap is off"
        # but it never printed, so there is no bug there
        # when the above-mentioned bug in swapBuffers occurs.
        
        #bruce 081230 part of a fix for bug 2964
        self._defer_statusbar_msg = False
        if self._deferred_msg is not None:
            # do this now rather than inside set_selobj (re bug 2964)
            env.history.statusbar_msg( self._deferred_msg)
        elif glselect_was_wanted:
            # This happens when the same selobj got found again;
            # this is common when rulers are on, and rare but happens otherwise
            # (especially when moving mouse slowly from one selobj to another);
            # when it happens, I think we need to use this other way to get the
            # desired message out. Review: could we simplify by making
            # this the *only* way, or would that change the interaction
            # between this code and unrelated sources of statusbar_msg calls
            # whose messages we should avoid overriding unless selobj changes?
            env.history.statusbar_msg( self._selobj_statusbar_msg )
            pass
            
        self._resize_just_occurred = False

        self._resetWaitCursor_globalDisplayStyle()

        return

    def do_swapBuffers( self,
                        debug = False,
                        use_CopyPixels = False,
                        verify = False ): #bruce 081222
        """
        """
        if verify:
            # record pixels, change colors to make buffers differ, compare later
            print "verify is nim" ###
        if use_CopyPixels:
            print "use_CopyPixels is nim, no swapBuffers is occurring" ### Q: does this prevent all drawing??
        else:
            self.swapBuffers()
        if verify:
            # compare, print
            pass ###
        return
    
    # ==
            
    #bruce 080813 get .graphicsMode from commandSequencer
    
    def _get_graphicsMode(self):
        res = self.assy.commandSequencer.currentCommand.graphicsMode
            # don't go through commandSequencer.graphicsMode,
            # maybe that attr is not needed
        assert isinstance(res, GraphicsMode_API)
        return res

    graphicsMode = property( _get_graphicsMode)

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

        self.assy.commandSequencer._reinit_modes()
            # TODO: move this out of this method, now that it's the usual case

        return # from GLPane.setAssy

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

        dnaCommands = ('BUILD_DNA', 'INSERT_DNA', 'DNA_SEGMENT', 'DNA_STRAND')

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
    
    def _setWaitCursor_globalDisplayStyle(self):
        """
        For performance reasons, whenever the global display style
        changes, the current cursor is replaced with an hourglass cursor,
        by calling this method.
        
        @see: self._paintGL()
        @see: self.setGlobalDisplayStyle()
        @see: self._setWaitCursor()
        @see: self._resetWaitCursor_globalDisplayStyle
        """
        if self._waitCursor_for_globalDisplayStyleChange:
            #This avoids setting the wait cursor twice.
            return
        self._waitCursor_for_globalDisplayStyleChange = True
        self._setWaitCursor()
    
    def _resetWaitCursor_globalDisplayStyle(self):
        """
        Reset hourglass cursor that was set while NE1 was changing the global
        display style of the model (by _setWaitCursor_globalDisplayStyle).
        
        @see: self._paintGL()
        @see: self.setGlobalDisplayStyle()
        @see: self._setWaitCursor()
        @see: self._setWaitCursor_globalDisplayStyle()
        """
        if self._waitCursor_for_globalDisplayStyleChange:
            self._resetWaitCursor()
            self._waitCursor_for_globalDisplayStyleChange = False
        return
    
    def _setWaitCursor(self):
        """
        Set the hourglass cursor whenever required.
        """        
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        
    def _resetWaitCursor(self):
        """
        Reset the hourglass cursor.
        
        @see: self._paintGL()
        @see: self.setGlobalDisplayStyle()
        @see: self._setWaitCursor()
        @see: self._setWaitCursor_globalDisplayStyle()
        """
        QApplication.restoreOverrideCursor()
        
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
        @see: self.self._setWaitCursor_globalDisplayStyle()
        """
        
        self._setWaitCursor_globalDisplayStyle()
                        
        # review docstring: what about diINVISIBLE? diPROTEIN?        
        if disp == diDEFAULT:
            disp = env.prefs[ startupGlobalDisplayStyle_prefs_key ]
        #e someday: if self.displayMode == disp, no actual change needed??
        # not sure if that holds for all init code, so being safe for now.
        self.displayMode = disp
            # note: chunks check this when needed before drawing, so this code
            # doesn't need to tell them to invalidate their display lists.

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
        return
    
    _needs_repaint = True #bruce 050516
        # used/modified in both this class and GLPane_rendering_methods
        # (see also wants_gl_update)

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
        self._needs_repaint = True
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

    # The following behavior (in several methods herein) related to wants_gl_update
    # should probably also be done in ThumbViews
    # if they want to get properly updated when graphics prefs change. [bruce 050804 guess]

    wants_gl_update = True #bruce 050804
        # this is set to True after we redraw, and to False by wants_gl_update_was_True
        # used/modified in both this class and GLPane_rendering_methods
        # (see also _needs_repaint)

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
        #bruce 080913 comment: I doubt the intended optim matters, anyway.
        # REVIEW whether this should simply be scrapped in favor of just
        # calling gl_update instead.
        self.wants_gl_update = False
        self.gl_update()

    # ==

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
                # todo: make more calls pass "why" argument
                print_compact_stack("_DEBUG_SET_SELOBJ: %r -> %r (%s): " % (previous_selobj, selobj, why))
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

            self._selobj_statusbar_msg = msg #bruce 081230 re bug 2964
            
            if self._defer_statusbar_msg:
                self._deferred_msg = msg #bruce 081230 re bug 2964
            else:
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

    pass # end of class GLPane

# end
