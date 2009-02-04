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

import math

from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import GL_SMOOTH
from OpenGL.GL import GL_VIEWPORT
from OpenGL.GL import glDepthRange
from OpenGL.GL import glEnable
from OpenGL.GL import glFrustum
from OpenGL.GL import glGetIntegerv
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glOrtho
from OpenGL.GL import glRotatef
from OpenGL.GL import glShadeModel
from OpenGL.GL import glTranslatef
from OpenGL.GL import glViewport

from OpenGL.GLU import gluPickMatrix

from PyQt4.QtOpenGL import QGLFormat
from PyQt4.QtOpenGL import QGLWidget

from Numeric import dot

from geometry.VQT import norm, angleBetween
from geometry.VQT import V, Q

from graphics.behaviors.Trackball import Trackball
from model.NamedView import NamedView

from utilities.prefs_constants import undoRestoreView_prefs_key
from utilities.prefs_constants import startup_GLPane_scale_prefs_key
from utilities.prefs_constants import enableAntiAliasing_prefs_key

from utilities.constants import default_display_mode

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

    # Russ 080925: Moved DEPTH_TWEAK in to GLPane_minimal.
    # DEPTH_TWEAK = DEPTH_TWEAK_UNITS * DEPTH_TWEAK_VALUE
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

    # class constants

    SIZE_FOR_glSelectBuffer = 10000 # guess, probably overkill, seems to work, no other value was tried
    
    # default values of instance variables:

    shareWidget = None

    is_animating = False #bruce 080219 fix bug 2632 (unverified)

    initialised = False

    _resize_counter = 0

    # default values of subclass-specific constants

    permit_draw_bond_letters = True #bruce 071023

    useMultisample = env.prefs[enableAntiAliasing_prefs_key]

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
                    #  shape in BuildAtoms_Graphicsmode.bareMotion) [bruce 050610]

            if (self.useMultisample):
                # use full scene anti-aliasing on hardware that supports it
                # (note: setting this True works around bug 2961 on some systems)
                glformat.setSampleBuffers(True)
                
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
            # Note: I believe (both now, and in a comment dated 060829 which is
            # now being removed from GLPane.py) that nothing ever sets
            # self.zoomFactor to anything other than 1.0, though there is code
            # which could do this in theory. I think zoomFactor was added as
            # one way to implement zoomToArea, but another way (changing scale)
            # was chosen, which makes zoomFactor useless. Someday we should
            # consider removing it, unless we think it might be useful for
            # something in the future. [bruce 080910 comment]

        # Initial value of depth "constant" (changeable by prefs.)
        self.DEPTH_TWEAK = DEPTH_TWEAK_UNITS * DEPTH_TWEAK_VALUE

        self.trackball = Trackball(10, 10)

        self._functions_to_call_when_gl_context_is_current = []

        # piotr 080714: Defined this attribute here in case
        # chunk.py accesses it in ThumbView. 
        self.lastNonReducedDisplayMode = default_display_mode
        
        # piotr 080807
        # Most recent quaternion to be used in animation timer.
        self.last_quat = None
        
        return

    # define properties which return model-space vectors
    # corresponding to various directions relative to the screen
    # (can be used during drawing or when handling mouse events)
    #
    # [bruce 080912 turned these into properties, and optimized;
    #  before that, this was done by __getattr__ in each subclass]

    def __right(self, _q = V(1, 0, 0)):
        return self.quat.unrot(_q)
    right = property(__right)

    def __left(self, _q = V(-1, 0, 0)):
        return self.quat.unrot(_q)
    left = property(__left)

    def __up(self, _q = V(0, 1, 0)):
        return self.quat.unrot(_q)
    up = property(__up)

    def __down(self, _q = V(0, -1, 0)):
        return self.quat.unrot(_q)
    down = property(__down)

    def __out(self, _q = V(0, 0, 1)):
        return self.quat.unrot(_q)
    out = property(__out)
    
    def __lineOfSight(self, _q = V(0, 0, -1)):
        return self.quat.unrot(_q)
    lineOfSight = property(__lineOfSight)

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

    def __get_vdist(self):
        """
        Recompute and return the desired distance between
        eyeball and center of view.
        """
        #bruce 070920 revised; bruce 080912 moved from GLPane into GLPane_minimal
        # Note: an old comment from elsewhere in GLPane claims:
            # bruce 041214 comment: some code assumes vdist is always 6.0 * self.scale
            # (e.g. eyeball computations, see bug 30), thus has bugs for aspect < 1.0.
            # We should have glpane attrs for aspect, w_scale, h_scale, eyeball,
            # clipping planes, etc, like we do now for right, up, etc. ###e
        # I don't know if vdist could ever have a different value,
        # or if we still have aspect < 1.0 bugs due to some other cause.
        return 6.0 * self.scale

    vdist = property(__get_vdist)

    def eyeball(self): #bruce 060219 ##e should call this to replace equivalent formulae in other places
        """
        Return the location of the eyeball in model coordinates.

        @note: this is not meaningful except when using perspective projection.
        """
        ### REVIEW: whether this is correct for tall aspect ratio GLPane.
        # See also the comment in __get_vdist, above, mentioning bug 30.
        # There is related code in writepovfile which computes a camera position
        # which corrects vdist when aspect < 1.0:
        ##    # Camera info
        ##    vdist = cdist
        ##    if aspect < 1.0:
        ##            vdist = cdist / aspect
        ##    eyePos = vdist * glpane.scale * glpane.out - glpane.pov
        # [bruce comment 080912]
        #bruce 0809122 moved this from GLPane into GLPane_minimal,
        # and made region selection code call it for the first time.
        return self.quat.unrot(V(0, 0, self.vdist)) - self.pov

    def __repr__(self):
        return "<%s at %#x>" % (self.__class__.__name__.split('.')[-1], id(self))

    def initializeGL(self):
        """
        Called once by Qt when the OpenGL context is first ready to use.
        """
        #bruce 080912 merged this from subclass methods, guessed docstring
        self._setup_lighting()
        
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        if not self.isSharing():
            self._setup_display_lists()
        return

    def resizeGL(self, width, height):
        """
        Called by QtGL when the drawing window is resized.
        """
        #bruce 080912 moved this from GLPane into GLPane_minimal

        self._resize_counter += 1 #bruce 080922
        
        self.width = width
        self.height = height

        glViewport(0, 0, self.width, self.height)
            # example of using a smaller viewport:
            ## glViewport(10, 15, (self.width - 10)/2, (self.height - 15)/3)

        # modify width and height for trackball
        # (note: this was done in GLPane but not in ThumbView until 080912)
        if width < 300:
            width = 300
        if height < 300:
            height = 300
        self.trackball.rescale(width, height)
        
        self.initialised = True
        
        return

    def __get_aspect(self):
        #bruce 080912 made this a property, moved to this class
        return (self.width + 0.0) / (self.height + 0.0)
    
    aspect = property(__get_aspect)
    
    def _setup_projection(self, glselect = False): ### WARNING: This is not actually private! TODO: rename it.
        """
        Set up standard projection matrix contents using various attributes of
        self (aspect, vdist, scale, zoomFactor).  Also reads the current OpenGL
        viewport bounds in window coordinates.
        
        (Warning: leaves matrixmode as GL_PROJECTION.)
        
        @param glselect: False (default) normally, or a 4-tuple
               (format not documented here) to prepare for GL_SELECT picking by
               calling gluPickMatrix().

        If you are really going to draw in the pick window (for GL_RENDER and
        glReadPixels picking, rather than GL_SELECT picking), don't forget to
        set the glViewport *after* calling _setup_projection.  Here's why:

           gluPickMatrix needs to know the current *whole-window* viewport, in
           order to set up a projection matrix to map a small portion of it to
           the clipping boundaries for GL_SELECT.

           From the gluPickMatrix doc page:
             viewport:
               Specifies the current viewport (as from a glGetIntegerv call).
             Description:
               gluPickMatrix creates a projection matrix that can be used to
               restrict drawing to a small region of the viewport.

           In the graphics pipeline, the clipper actually works in homogeneous
           coordinates, clipping polygons to the {X,Y}==+-W boundaries.  This
           saves the work of doing the homogeneous division: {X,Y}/W==+-1.0,
           (and avoiding problems when W is zero for points on the eye plane in
           Z,) but it comes down to the same thing as clipping to X,Y==+-1 in
           orthographic.

           So the projection matrix decides what 3D model-space planes map to
           +-1 in X,Y.  (I think it maps [near,far] to [0,1] in Z, because
           they're not clipped symmetrically.)

           Then glViewport sets the hardware transform that determines where the
           +-1 square of clipped output goes in screen pixels within the window.

           Normally you don't actually draw pixels while picking in GL_SELECT
           mode because the pipeline outputs hits after the clipping stage, so
           gluPickMatrix only reads the viewport and sets the projection matrix.
        """
        #bruce 080912 moved this from GLPane into GLPane_minimal
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        scale = self.scale * self.zoomFactor
        near, far = self.near, self.far

        aspect = self.aspect
        vdist = self.vdist

        if glselect:
            x, y, w, h = glselect
            gluPickMatrix(
                x, y,
                w, h,
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

    def _setup_modelview(self):
        """
        set up modelview coordinate system
        """
        #bruce 080912 moved this from GLPane into GLPane_minimal
        # note: it's not yet used in ThumbView, but maybe it could be.
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef( 0.0, 0.0, - self.vdist)
            # translate coordinate system for drawing, away from eye
            # (-Z direction) by vdist. This positions center of view
            # in eyespace.
        q = self.quat
        glRotatef( q.angle * 180.0 / math.pi, q.x, q.y, q.z)
            # rotate coordinate system for drawing by trackball quat
            # (this rotation is around the center of view, since that is what
            #  is positioned at drawing coordsystem's current origin,
            #  by the following code)
        glTranslatef( self.pov[0], self.pov[1], self.pov[2])
            # translate model (about to be drawn) to bring its center of view
            # (cov == - pov) to origin of coordinate system for drawing.
            # We translate by -cov to bring model.cov to origin.
        return
    
    def _setup_lighting(self):
        # note: in subclass GLPane, as of 080911 this is defined in
        # its mixin superclass GLPane_lighting_methods
        assert 0, "subclass must override this"
        
    def _setup_display_lists(self): # bruce 071030
        """
        This needs to be called during __init__ if a new display list context
        is being used.

        WARNING: the functions this calls store display list names in
        global variables (as of 071030); until this is cleaned up, only the
        most recently set up display list context will work with the
        associated drawing functions in the same modules.
        """
        # TODO: warn if called twice (see docstring for why)
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
        return True #bruce 080913 False -> True (more useful default)

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
        self.DEPTH_TWEAK = DEPTH_TWEAK_UNITS * \
                    debug_pref("GLPane: depth tweak", DEPTH_TWEAK_CHOICE)
        return

    def setDepthRange_Normal(self):
        glDepthRange(0.0 + self.DEPTH_TWEAK, 1.0) # args are near, far
        return

    def setDepthRange_Highlighting(self):
        glDepthRange(0.0, 1.0 - self.DEPTH_TWEAK)
        return

    # ==

    # REVIEW:
    # the following "Undo view" methods probably don't work in subclasses other
    # than GLPane. It might make sense to have them here, but only if they are
    # refactored a bit, e.g. so that self.animateToView works in other
    # subclassses even if it doesn't animate. Ultimately it might be better
    # to refactor them a lot and/or move them out of this class hierarchy
    # entirely. [bruce 080912 comment]
    
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

        oldc = assy.all_change_indicators()

        namedView = NamedView(assy, "name", self.scale, self.pov, self.zoomFactor, self.quat)

        newc = assy.all_change_indicators()
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
