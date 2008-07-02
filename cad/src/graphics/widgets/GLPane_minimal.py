# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPane_minimal.py -- common superclass for GLPane-like widgets.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

bruce 070914 made this to remind us that GLPane and ThumbView
need a common superclass (and have common code that needs merging).
It needs to be in its own file to avoid import loop problems.
"""

from OpenGL.GL import glDepthRange

from PyQt4.QtOpenGL import QGLFormat
from PyQt4.QtOpenGL import QGLWidget

from geometry.VQT import V, Q
from graphics.behaviors.Trackball import Trackball
from model.NamedView import NamedView

from utilities.prefs_constants import undoRestoreView_prefs_key
from utilities.prefs_constants import startup_GLPane_scale_prefs_key

from utilities.debug_prefs import Choice
from utilities.debug_prefs import debug_pref

from utilities.debug import print_compact_traceback

import foundation.env as env

from graphics.drawing.setup_draw import setup_drawer
from graphics.drawing.draw_grid_lines import setup_draw_grid_lines

DEPTH_TWEAK_UNITS = (2.0)**(-32)
DEPTH_TWEAK_VALUE = 100000
    # For bond cylinders subject to shorten_tubes:
    # on my iMac G5, 300 is enough to prevent "patchy highlighting" problems
    # except sometimes at the edges. 5000 even fixes the edges and causes no
    # known harm, so we'd use that value if only that platform mattered.
    #
    # But, on Windows XP (Ninad & Tom), much higher values are needed.
    # By experiment, 100000 is enough on those platforms, and doesn't seem to
    # be too large on them or on my iMac, so we'll go with that for now,
    # but leave it in as a debug_pref. (We made no attempt to get a precise
    # estimate of the required value -- we only know that 10000 is not enough.)
    #
    # We don't know why a higher value is needed on Windows. Could the
    # depth buffer bit depth be different?? This value works out to a bit
    # more than one resolution unit for a 16-bit depth buffer, so that might
    # be a plausible cause. But due to our limited testing, the true difference
    # in required values on these platforms might be much smaller.
    #
    # [bruce 070926]

DEPTH_TWEAK = DEPTH_TWEAK_UNITS * DEPTH_TWEAK_VALUE
    # changed by setDepthRange_setup_from_debug_pref

DEPTH_TWEAK_CHOICE = \
                   Choice( [0,1,3,10,
                            100,200,300,400,500,600,700,800,900,1000,
                            2000,3000,4000,5000,
                            10000, 100000, 10**6, 10**7, 10**8],
                            defaultValue = DEPTH_TWEAK_VALUE )

class GLPane_minimal(QGLWidget, object): #bruce 070914
    """
    Mostly a stub superclass, just so GLPane and ThumbView can have a common
    superclass.

    TODO:
    They share a lot of code, which ought to be merged into this superclass.
    Once that happens, it might as well get renamed.
    """

    # bruce 070920 added object superclass to our subclass GLPane;
    # bruce 080220 moved object superclass from GLPane to this class.
    # Purpose is to make this a new-style class so as to allow
    # defining a python property in any subclass.

    # note: every subclass defines .assy as an instance variable or property
    # (as of bruce 080220), but we can't define a default value or property
    # for that here, since some subclasses define it in each way
    # (and we'd have to know which way to define a default value correctly).

    # default values of instance variables:

    glselectBufferSize = 10000 # guess, probably overkill, seems to work, no other value was tried

    shareWidget = None

    is_animating = False #bruce 080219 fix bug 2632 (unverified)

    # default values of subclass-specific constants

    permit_draw_bond_letters = True #bruce 071023

    def __init__(self, parent, shareWidget, useStencilBuffer):
        """
        If shareWidget is specified, useStencilBuffer is ignored: set it in the widget you're sharing with.
        """

        if shareWidget:
            self.shareWidget = shareWidget #bruce 051212
            glformat = shareWidget.format()
            QGLWidget.__init__(self, glformat, parent, shareWidget)
            if not self.isSharing():
                print "Request of display list sharing is failed."
                return
        else:
            glformat = QGLFormat()
            if (useStencilBuffer):
                glformat.setStencil(True)
                    # set gl format to request stencil buffer
                    # (needed for mouseover-highlighting of objects of general
                    #  shape in depositMode.bareMotion) [bruce 050610]

            QGLWidget.__init__(self, glformat, parent)

        # Current view attributes (sometimes saved in or loaded from
        #  the currently displayed part or its mmp file):

        # rotation
        self.quat = Q(1, 0, 0, 0)

        # point of view (i.e. negative of center of view)
        self.pov = V(0.0, 0.0, 0.0)

        # half-height of window in Angstroms (reset by certain view-changing operations)
        self.scale = float(env.prefs[startup_GLPane_scale_prefs_key])
        
        # zoom factor
        self.zoomFactor = 1.0

        self.trackball = Trackball(10,10)

        self._functions_to_call_when_gl_context_is_current = []

        return

    def _setup_display_lists(self): # bruce 071030
        """
        This needs to be called during __init__ if a new display list context
        is being used.

        WARNING: the functions this calls store display list names in
        global variables (as of 071030); until this is cleaned up, only the
        most recently set up display list context will work with the
        associated drawing functions in the same modules.
        """
        setup_drawer()
        setup_draw_grid_lines()
        return

    # ==

    def model_is_valid(self): #bruce 080117
        """
        Subclasses should override this to return a boolean
        saying whether their model is currently valid for drawing.

        Subclass implementations of paintGL are advised to call this
        at the beginning and return immediately if it's false.
        """
        return False

    # ==

    def is_sphere_visible(self, center, radius): # piotr 080331
        """
        Frustum culling test. Subclasses should override it
        to disable drawing objects outside of the view frustum.
        """
        return True

    # ==

    def is_lozenge_visible(self, pos1, pos2, radius): # piotr 080402
        """
        Frustum culling test for lozenge-shaped objects. Subclasses should 
        override it to disable drawing objects outside of the view frustum.
        """
        return True

    # ==

    def _call_whatever_waits_for_gl_context_current(self): #bruce 071103
        """
        For whatever functions have been registered to be called (once)
        when our GL context is next current, call them now (and then discard them).

        Note: subclasses wishing to support self.call_when_glcontext_is_next_current
        MUST call this at some point during their paintGL method
        (preferably before doing any drawing in that method, though this is
        not at present guaranteed). Subclasses not wishing to support that
        should override it to discard functions passed to it immediately.
        """
        functions = self._functions_to_call_when_gl_context_is_current
        self._functions_to_call_when_gl_context_is_current = []
        for func in functions:
            try:
                func()
            except:
                print_compact_traceback(
                    "bug: %r._call_whatever_waits_for_gl_context_current ignoring exception in %r: " % \
                    (self, func) )
            continue
        return

    def call_when_glcontext_is_next_current(self, func): #bruce 071103
        """
        Call func at the next convenient time when we know our OpenGL context
        is current.

        (Subclasses are permitted to call func immediately if they happen
        to know their gl context is current right when this is called.
        Conversely, subclasses are permitted to never call func, though
        that will defeat the optimizations this is used for, such as
        deallocating OpenGL display lists which are no longer needed.)
        """
        self._functions_to_call_when_gl_context_is_current.append( func)
        return

    # ==

    def should_draw_valence_errors(self):
        """
        Return a boolean to indicate whether valence error
        indicators (of any kind) should ever be drawn in self.
        (Each specific kind may also be controlled by a prefs
        setting, checked independently by the caller. As of 070914
        there is only one kind, drawn by class Atom.)
        """
        return False

    # ==

    def setDepthRange_setup_from_debug_pref(self):
        global DEPTH_TWEAK
        DEPTH_TWEAK = DEPTH_TWEAK_UNITS * \
                    debug_pref("GLPane: depth tweak", DEPTH_TWEAK_CHOICE)
        return

    def setDepthRange_Normal(self):
        glDepthRange(0.0 + DEPTH_TWEAK, 1.0) # args are near, far
        return

    def setDepthRange_Highlighting(self):
        glDepthRange(0.0, 1.0 - DEPTH_TWEAK)
        return

    # ==

    def current_view_for_Undo(self, assy): #e shares code with saveNamedView
        """
        Return the current view in this glpane (which we assume is showing
        this assy), with additional attributes saved along with the view by Undo
        (i.e. the index of the current selection group).
        (The assy arg is used for multiple purposes specific to Undo.)

        @warning: present implem of saving current Part (using its index in MT)
                  is not suitable for out-of-order Redo.
        """
        # WARNING: not reviewed for use in subclasses which don't
        # have and draw a .assy attribute, though by passing assy into this method,
        # we remove any obvious bug from that. [bruce 080220 comment]

        oldc = assy.all_change_counters()

        namedView = NamedView(assy, "name", self.scale, self.pov, self.zoomFactor, self.quat)

        newc = assy.all_change_counters()
        assert oldc == newc

        namedView.current_selgroup_index = assy.current_selgroup_index()
            # storing this on the namedView is a kluge, but should be safe

        return namedView # ideally would not return a Node but just a
            # "view object" with the same 4 elements in it as passed to NamedView

    def set_view_for_Undo(self, assy, namedView): # shares code with NamedView.set_view; might be very similar to some GLPane method, too
        """
        Restore the view (and the current Part) to what was saved by current_view_for_Undo.
        WARNING: present implem of saving current Part (using its index in MT) is not suitable for out-of-order Redo.
        WARNING: might not gl_update, assume caller does so [#k obs warning?]
        """
        ## compare to NamedView.set_view (which passes animate = True) -- not sure if we want to animate in this case [we do, for A8],
        # but if we do, we might have to do that at a higher level in the call chain
        restore_view = env.prefs[undoRestoreView_prefs_key] #060314
        restore_current_part = True # always do this no matter what
        ## restore_mode?? nah (not for A7 anyway; unclear what's best in long run)
        if restore_view:
            if type(namedView) == type(""):
                #####@@@@@ code copied from GLPane.__init__, should be shared somehow, or at least comment GLPane and warn it's copied
                #e also might not be the correct view, it's just the hardcoded default view... but i guess it's correct.
                # rotation
                self.quat = Q(1, 0, 0, 0)
                # point of view (i.e. negative of center of view)
                self.pov = V(0.0, 0.0, 0.0)
                
                # half-height of window in Angstroms (gets reset by certain 
                #view-changing operations [bruce 050615 comment])                
                #@REVIEW: Should self.scale here should be set from 
                #startup_GLPane_scale_prefs_key ??
                self.scale = 10.0
                # zoom factor
                self.zoomFactor = 1.0
            else:
                self.animateToView(namedView.quat, namedView.scale, namedView.pov, namedView.zoomFactor, animate = False)
                    # if we want this to animate, we probably have to move that higher in the call chain and do it after everything else
        if restore_current_part:
            if type(namedView) == type(""):
                if env.debug():
                    print "debug: fyi: cys == '' still happens" # does it? ###@@@ 060314 remove if seen, or if not seen
                current_selgroup_index = 0
            else:
                current_selgroup_index = namedView.current_selgroup_index
            sg = assy.selgroup_at_index(current_selgroup_index)
            assy.set_current_selgroup(sg)
                #e how might that interact with setting the selection? Hopefully, not much, since selection (if any) should be inside sg.
        #e should we update_parts?
        return

    pass

# end
