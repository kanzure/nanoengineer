# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPane_minimal.py -- common superclass for GLPane-like widgets.

$Id$

History:

bruce 070914 made this to remind us that GLPane and ThumbView
need a common superclass (and have common code that needs merging).
It needs to be in its own file to avoid import loop problems.
"""

from OpenGL.GL import glDepthRange

from PyQt4.Qt import QGLFormat
from PyQt4.Qt import QGLWidget

from VQT import V, Q, Trackball
from Utility import Csys

from prefs_constants import undoRestoreView_prefs_key

from debug_prefs import Choice
from debug_prefs import debug_pref

import env

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

class GLPane_minimal(QGLWidget): #bruce 070914
    """
    Mostly a stub superclass, just so GLPane and ThumbView can have a common
    superclass.

    TODO:
    They share a lot of code, which ought to be merged into this superclass.
    Once that happens, it might as well get renamed.
    """

    # default values of instance variables:
    
    glselectBufferSize = 10000 # guess, probably overkill, seems to work, no other value was tried

    shareWidget = None

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
        self.scale = 10.0

        # zoom factor
        self.zoomFactor = 1.0

        self.trackball = Trackball(10,10)

    
    def should_draw_valence_errors(self):
        """
        Return a boolean to indicate whether valence error
        indicators (of any kind) should ever be drawn in self.
        (Each specific kind may also be controlled by a prefs
        setting, checked independently by the caller. As of 070914
        there is only one kind, drawn by class Atom.)
        """
        return False

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


    def current_view_for_Undo(self, assy): #e shares code with saveNamedView
        """Return the current view in this glpane which is showing this assy,
        with additional attributes saved along with the view by Undo (i.e. the index of the current selection group).
        (The assy arg is used for multiple purposes specific to Undo.)
        WARNING: present implem of saving current Part (using its index in MT) is not suitable for out-of-order Redo.
        """
        oldc = assy.all_change_counters()

        csys = Csys(assy, "name", self.scale, self.pov, self.zoomFactor, self.quat)

        newc = assy.all_change_counters()
        assert oldc == newc

        csys.current_selgroup_index = assy.current_selgroup_index() # storing this on the csys is a kluge, but should be safe

        return csys # ideally would not return a Node but just a "view object" with the same 4 elements in it as passed to Csys

    def set_view_for_Undo(self, assy, csys): # shares code with Csys.set_view; might be very similar to some GLPane method, too
        """Restore the view (and the current Part) to what was saved by current_view_for_Undo.
        WARNING: present implem of saving current Part (using its index in MT) is not suitable for out-of-order Redo.
        WARNING: might not gl_update, assume caller does so [#k obs warning?]
        """
        ## compare to Csys.set_view (which passes animate = True) -- not sure if we want to animate in this case [we do, for A8],
        # but if we do, we might have to do that at a higher level in the call chain
        restore_view = env.prefs[undoRestoreView_prefs_key] #060314
        restore_current_part = True # always do this no matter what
        ## restore_mode?? nah (not for A7 anyway; unclear what's best in long run)
        if restore_view:
            if type(csys) == type(""):
                #####@@@@@ code copied from GLPane.__init__, should be shared somehow, or at least comment GLPane and warn it's copied
                #e also might not be the correct view, it's just the hardcoded default view... but i guess it's correct.
                # rotation
                self.quat = Q(1, 0, 0, 0)
                # point of view (i.e. negative of center of view)
                self.pov = V(0.0, 0.0, 0.0)
                # half-height of window in Angstroms (gets reset by certain view-changing operations [bruce 050615 comment])
                self.scale = 10.0
                # zoom factor
                self.zoomFactor = 1.0
            else:
                self.animateToView(csys.quat, csys.scale, csys.pov, csys.zoomFactor, animate = False)
                    # if we want this to animate, we probably have to move that higher in the call chain and do it after everything else
        if restore_current_part:
            if type(csys) == type(""):
                if env.debug():
                    print "debug: fyi: cys == '' still happens" # does it? ###@@@ 060314 remove if seen, or if not seen
                current_selgroup_index = 0
            else:
                current_selgroup_index = csys.current_selgroup_index
            sg = assy.selgroup_at_index(current_selgroup_index)
            assy.set_current_selgroup(sg)
                #e how might that interact with setting the selection? Hopefully, not much, since selection (if any) should be inside sg.
        #e should we update_parts?
        return

# end
