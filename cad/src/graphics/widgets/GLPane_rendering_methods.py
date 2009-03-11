# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_rendering_methods.py

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

bruce 080913 split this out of class GLPane
"""

TEST_DRAWING = False # True  ## Debug/test switch.  Never check in a True value.
    # Also can be changed at runtime by external code.

if TEST_DRAWING:
    from prototype.test_drawing import test_drawing
        # review: is this needed here for its side effects?
        # guess yes, should document if so.
    pass

from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_LEQUAL
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_MODELVIEW_STACK_DEPTH
from OpenGL.GL import GL_STENCIL_BUFFER_BIT
from OpenGL.GL import glDepthFunc
from OpenGL.GL import glFlush
from OpenGL.GL import glGetInteger
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glPopMatrix

# kluge for debug bruce 081218 (temporary)
##from OpenGL.GL import glEnable
##from OpenGL.GL import glLogicOp
##from OpenGL.GL import glDisable
##from OpenGL.GL import GL_COLOR_LOGIC_OP
##from OpenGL.GL import GL_XOR

from PyQt4.QtOpenGL import QGLWidget


from utilities import debug_flags

from utilities.debug import print_compact_traceback, print_compact_stack

from utilities.Comparison import same_vals

from utilities.prefs_constants import displayCompass_prefs_key
from utilities.prefs_constants import displayOriginAxis_prefs_key
from utilities.prefs_constants import displayOriginAsSmallAxis_prefs_key
from utilities.prefs_constants import displayCompassLabels_prefs_key
from utilities.prefs_constants import displayRulers_prefs_key
from utilities.prefs_constants import showRulersInPerspectiveView_prefs_key
from utilities.prefs_constants import fogEnabled_prefs_key

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice_boolean_False

from utilities.GlobalPreferences import use_frustum_culling
from utilities.GlobalPreferences import pref_skip_redraws_requested_only_by_Qt


import foundation.env as env


import graphics.drawing.drawing_globals as drawing_globals

from graphics.drawing.drawers import drawOriginAsSmallAxis
from graphics.drawing.drawers import drawaxes

from graphics.drawing.gl_lighting import disable_fog
from graphics.drawing.gl_lighting import enable_fog
from graphics.drawing.gl_lighting import setup_fog

from graphics.drawing.drawcompass import Compass
from graphics.drawing.Guides import Guides


from graphics.widgets.GLPane_image_methods import GLPane_image_methods


# ==

class GLPane_rendering_methods(GLPane_image_methods):
    """
    private mixin for providing rendering methods to class GLPane
    (including calls to highlighting/hit-test methods
     defined in mixin class GLPane_highlighting_methods,
     which must be a mixin of class GLPane along with this class)
    """
    def _init_GLPane_rendering_methods(self):
        """
        """
        # clipping planes, as percentage of distance from the eye
        self.near = 0.25 # After testing, this is much, much better.  Mark 060116. [Prior value was 0.66 -- bruce 060124 comment]
        self.far = 12.0  ##2.0, Huaicai: make this bigger, so models will be
                    ## more likely sitting within the view volume

        ##Huaicai 2/8/05: If this is true, redraw everything. It's better to split
        ##the paintGL() to several functions, so we may choose to draw 
        ##every thing, or only some thing that has been changed.
        self.redrawGL = True  

        # [bruce 050608]
        self.glselect_dict = {} # only used within individual runs [of what? paintGL I guess?]
            # see also self.object_for_glselect_name(), defined in GLPane_highlighting_methods

        self.makeCurrent() # REVIEW: safe now? needed for loadLighting? [bruce 080913 questions]

        # don't call GLPane_minimal._setup_display_lists yet -- this will be
        # called later by GLPane_minimal.initializeGL. [bruce 080913 change]

        # NOTE: before bruce 080913 split out this file, setAssy was done
        # at this point. Hopefully it's ok to do it just after we return,
        # instead. (Seems to work.)
        
        self.loadLighting() #bruce 050311 [defined in GLPane_lighting_methods]
            #bruce question 051212: why doesn't this prevent bug 1204
            # in use of lighting directions on startup?

        self.guides = Guides(self) # rulers, and soon, grid lines. Mark 2008-02-24.

        self.compass = Compass(self) #bruce 081015 refactored this
        
        return
    
    def model_is_valid(self): #bruce 080117
        """
        whether our model is currently valid for drawing
        [overrides GLPane_minimal method]
        """
        return self.assy.assy_valid

    def should_draw_valence_errors(self):
        """
        [overrides GLPane_minimal method]
        """
        return True

    def _paintGL(self):
        """
        [private; the body of paintGL in GLPane.py]

        Decide whether we need to call _paintGL_drawing,
        and if so, prepare for that (this might modify the model)
        and then call it.
        
        Also (first) call self._call_whatever_waits_for_gl_context_current()
        if that would be safe.

        @return: whether we modified GL buffer state (by clear or draw).
        @rtype: boolean
        """
        #bruce 081222 added return flag
        if TEST_DRAWING:  # See prototype/test_drawing.py
            from prototype.test_drawing import test_drawing, USE_GRAPHICSMODE_DRAW
                # intentionally redundant with toplevel import [bruce 080930]
            if USE_GRAPHICSMODE_DRAW:
                # Init and continue on, assuming that test_Draw_model will be called
                # separately (in an override of graphicsMode.Draw_model).
                
                # LIKELY BUG: USE_GRAPHICSMODE_DRAW is now a constant
                # but needs to depend on the testCase or be a separately
                # settable variable. This might be fixable inside test_drawing.py
                # since we reimport it each time here. [bruce 081211 comment]
                test_drawing(self, True)
            else:
                self.graphicsMode.gm_start_of_paintGL(self)
                test_drawing(self)
                self.graphicsMode.gm_end_of_paintGL(self)
                return True
        
        self._frustum_planes_available = False

        if not self.initialised:
            return False
        
        if not self.model_is_valid():
            #bruce 080117 bugfix in GLPane and potential bugfix in ThumbView;
            # for explanation see my same-dated comment in files_mmp
            # near another check of assy_valid.
            return False
        
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
            return False
        
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
            # [doing this experimentally, 080919; see class GLPane_image_methods]

            # disabling this debug print (see long comment above), bruce 080512
            ## if debug_flags.atom_debug:
            ##     sys.stdout.write("#") # indicate a repaint is being skipped
            ##     sys.stdout.flush()

            return False # skip the following repaint

        # at this point, we've decided to call _paintGL_drawing.
        
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
            # TODO: doc what else it does - break interpart bonds? dna updater? undo checkpoint?

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
            self._paintGL_drawing()
        except:
            print_compact_traceback("exception in _paintGL_drawing ignored: ")

        return True # from paintGL

    def _paintGL_drawing(self):
        """
        [private submethod of _paintGL]
        
        Do whatever OpenGL drawing paintGL should do (then glFlush).

        @note: caller must handle TEST_DRAWING, redrawGL, _needs_repaint.
        """
        #bruce 080919 renamed this from most_of_paintGL to _paintGL_drawing

##        if 'kluge for debug bruce 081218':
##            glEnable(GL_COLOR_LOGIC_OP)
##            glLogicOp(GL_XOR)
##            glDisable(GL_COLOR_LOGIC_OP)

        self._needs_repaint = False
            # do this now, even if we have an exception during the repaint

        self.graphicsMode.gm_start_of_paintGL(self)

        #k not sure whether _restore_modelview_stack_depth is also needed
        # in the split-out standard_repaint [bruce 050617]
        self._restore_modelview_stack_depth()

        self._use_frustum_culling = use_frustum_culling()
            # there is some overhead calling the debug_pref,
            # and we want the same answer used throughout
            # one call of paintGL. Note that this is checked both
            # in this file and in GLPane_highlighting_methods.py.
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

        self.graphicsMode.gm_end_of_paintGL(self)

        ##self.swapBuffers()  ##This is a redundant call, Huaicai 2/8/05

        return # from _paintGL_drawing

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

    def render_scene(self):#bruce 061208 split this out so some modes can override it (also removed obsolete trans_feature experiment)

        #k not sure whether next things are also needed in the split-out standard_repaint [bruce 050617]

        self.glprefs.update()
            #bruce 051126; kluge: have to do this before lighting *and* inside standard_repaint_0
            # [addendum, bruce 090304: I assume that's because we need it for lighting, but also
            #  need its prefs accesses to be usage-tracked, so changes in them do gl_update;
            #  maybe a better solution would be to start usage-tracking sooner?]

        self.setup_lighting_if_needed() # defined in GLPane_lighting_methods

        self.standard_repaint()

        return # from render_scene

    __subusage = None #bruce 070110

    def standard_repaint(self):
        """
        call standard_repaint_0 inside "usage tracking". This is so subsequent
        changes to tracked variables (such as env.prefs values) automatically
        cause self.gl_update to be called.
        
        @warning: this trashes both gl matrices! caller must push them both
                  if it needs the current ones. this routine sets its own
                  matrixmode, but depends on other gl state being standard
                  when entered.
        """
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
    
    drawing_phase = '?' # set to different fixed strings for different drawing phases
        # [new feature, bruce 070124] [also defined in GLPane_minimal]
        #
        # WARNING: some of the strings are hardcoded in condition checks in
        # various places in the code. If spelling is changed, or new strings are
        # added, or the precise drawing covered by each string is modified,
        # all existing uses need to be examined for possibly needing changes.
        # (Ideally, this would be cleaned up by defining in one place the
        #  possible values, as symbolic constants, and the functions for testing
        #  aspect of interest from them, e.g. whether to draw shader primitives,
        #  whether to draw OpenGL display lists, which DrawingSet cache to use.)
        # [bruce 090227 comment]
    
    drawing_globals.drawing_phase = drawing_phase # KLUGE (as is everything about drawing_globals)
    
    def set_drawing_phase(self, drawing_phase): 
        """
        Set self.drawing_phase to the specified value, and do any updates
        this requires (presently, copy it into drawing_globals.drawing_phase).

        Various internal code looks at self.drawing_phase (and/or
        drawing_globals.drawing_phase) so it can behave differently during
        different drawing phases. See code and code comments for details, and
        a list of permitted values of drawing_phase and what they mean.

        @note: setting self.drawing_phase directly (not using this method)
            would cause bugs.
        """
        # Russ 081208: Encapsulate setting, to tell shaders as well.
        self.drawing_phase = drawing_phase
        drawing_globals.drawing_phase = drawing_phase
        # Note, there are direct calls of GL_SELECT drawing not from class
        # GLPane, which ought to set this but don't. (They have a lot of other
        # things wrong with them too, especially duplicated code). The biggest
        # example is for picking jigs. During those calls, this attr will
        # probably equal '?' -- all the draw calls here reset it to that right
        # after they're done. (## todo: We ought to set it to that at the end of
        # paintGL as well, for safety.)
        #
        # Explanation of possible values: [### means explan needs to be filled in]
        # - '?' -- drawing at an unexpected time, or outside of paintGL
        # - 'glselect' -- only used if mode requested object picking
        #              -- Only draws Display Lists since the glSelect stack is not available to shaders.
        #              -- glRenderMode(GL_SELECT) in effect; reduced projection matrix
        # - 'glselect_glname_color' -- only used if mode requested object picking
        #              -- Only draws shader primitives, and reads the glnames back as pixel colors.
        #              -- glRenderMode(GL_RENDER) in effect; reduced projection matrix and viewport (one pixel.)
        # - 'main' -- normal drawing, main coordinate system for model (includes trackball/zoom effect)
        # - 'main/Draw_after_highlighting' -- normal drawing, but after selobj is drawn ### which coord system?
        # - 'main/draw_glpane_label' -- ###
        # - 'overlay' -- ###
        # - 'selobj' -- we're calling selobj.draw_in_abs_coords (not drawing the entire model), within same coordsys as 'main'
        # - 'selobj/preDraw_glselect_dict' -- like selobj, but color buffer drawing is off ### which coord system, incl projection??
        # [end]
        return

    _drawingset_cachename_from_drawing_phase = {
        '?': 'main', # theory: used by event methods that draw entire model for
            # selection, e.g. jigGLselect (sp?); should clean them up #### review
        'glselect': 'main',
        'glselect_glname_color': 'main',
        'main': 'main',
        'main/Draw_after_highlighting': 'main/Draw_after_highlighting',
        'main/draw_glpane_label': 'temp',
        'overlay': 'temp',
        'selobj': 'selobj',
        'selobj/preDraw_glselect_dict': 'temp',
     }

    _drawingset_temporary_cachenames = {
        'temp': True
     }
    def _choose_drawingset_cache_policy(self): #bruce 090227
        """
        Based on self.drawing_phase, decide which cache to keep DrawingSets in
        and whether it should be temporary.

        @return: (temporary, cachename)
        @rtype: (bool, string)

        [overrides a method defined in a mixin of a superclass
         of the class we mix into]
        """
        # Note: mistakes in what we return will reduce graphics performance,
        # and could increase VRAM usage, but have no effect on what is drawn.

        # About the issue of using too much ram: all whole-model caches should
        # be the same; small ones don't matter too much, but might be best
        # temporary in case they are not always small;
        # at least use the same cache in all temp cases.

        # todo: Further optimization is possible but not yet done:
        # for drawing main model for selobj tests, just reuse
        # the cached drawingsets without even scanning the model
        # to see if they need to be modified. This is worth
        # doing if we have time, but less urgent than several
        # other things we need to do.
        
        drawing_phase = self.drawing_phase
        if drawing_phase == '?':
            print_compact_stack("warning: _choose_drawingset_cache_policy during '?' -- should clean up: ") ######
        cachename = self._drawingset_cachename_from_drawing_phase.get(drawing_phase)
        if cachename is None:
            cachename = 'temp'
            print "bug: unknown drawing_phase %r, using cachename %r" % \
                  (drawing_phase, cachename)
            assert self._drawingset_temporary_cachenames.get(cachename, False) == True
            pass
        temporary = self._drawingset_temporary_cachenames.get(cachename, False)
        return (temporary, cachename)

    # ==

    def setup_shaders_each_frame(self): #bruce 090304
        """
        This must be called once near the start of each call of paintGL,
        sometime after self.glprefs.update has been first called during that
        call of paintGL. It makes sure shaders exist and are loaded, but does
        not configure them (since that requires some GL state which is
        not yet set when this is called, and may need to be done more
        than once per frame).
        """
        if self.permit_shaders:
            drawing_globals.setup_desired_shaders( self.glprefs)
            # review: is it good that we condition this on self.permit_shaders?
            # it doesn't matter for now, since ThumbView never calls it.
        return
    
    def enabled_shaders(self): #bruce 090303
        return drawing_globals.enabled_shaders(self)
            #### todo: refactor: self.drawing_globals (but renamed)

    def configure_enabled_shaders(self): #bruce 090303
        """
        This must be called before any drawing that might use shaders,
        but after all preferences are cached (by glprefs.update or any other
        means), and after certain other GL drawing state is set up (in case
        configShader reads that state). The state it reads from glpane
        (including from glpane.glprefs) are related to debug_code, material,
        perspective, clip/DEPTH_TWEAK, and lights (see configShader
        for details).

        It is ok to call it multiple times per paintGL call. If in doubt
        about where to correctly call it, just call it in both places.
        However, it is believed that in current code, it only uses state
        set by user pref changes, which means a single call per paintGL
        call should be sufficient if it's in the right place. (It never
        uses the GL matrices or glpane.drawing_phase. But see setPicking.)

        @note: setup_shaders_each_frame must have been called
            before this, during the same paintGL call.
        """
        for shader in self.enabled_shaders():
            shader.configShader(self)
        return

    # ==

    _cached_bg_image_comparison_data = None
        # note: for the image itself, see attrs of class GLPane_image_methods

    _last_general_appearance_prefs_summary = None #bruce 090306
    _general_appearance_change_indicator = 0 # also defined in GLPane_minimal
    
    def standard_repaint_0(self):
        """
        [private indirect submethod of paintGL]
        
        This is the main rendering routine -- it clears the OpenGL window,
        does all drawing done during paintGL, and does hit-testing if
        requested by event handlers before this call of paintGL.

        @note: this is called inside a begin_tracking_usage/end_tracking_usage
            pair, invalidation of which results (indirectly) in self.gl_update().

        @note: self.graphicsMode can control whether this gets called;
               for details see the call of self.render_scene in this class.
        """
        if self.width != QGLWidget.width(self) or \
           self.height != QGLWidget.height(self): #bruce 080922; never yet seen
            print "\n*** debug fyi: inconsistent: self width/height %r, %r vs QGLWidget %r, %r" % \
                  (self.width, self.height, QGLWidget.width, QGLWidget.height)
            pass
        
        self.glprefs.update()
            # (kluge: have to do this before lighting *and* inside standard_repaint_0)
            # (this is also required to come BEFORE setup_shaders_each_frame)

        # optimization: compute a change indicator for Chunk & ExternalBondSet
        # display lists here, not every time we draw one of them!
        # (kluge: assume no need for same_vals, i.e. no Numeric arrays
        #  in this value)
        # [bruce 090306]
        current_summary = self.part.general_appearance_prefs_summary(self)
        if self._last_general_appearance_prefs_summary != current_summary:
            self._general_appearance_change_indicator += 1 # invalidates display lists
            self._last_general_appearance_prefs_summary = current_summary
            pass

        self.clear_and_draw_background( GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
            # also sets self.fogColor

        # fog added by bradg 20060224
        # piotr 080605 1.1.0 rc1 - replaced fog debug pref with user pref
        self._fog_test_enable = env.prefs[fogEnabled_prefs_key]

        if self._fog_test_enable:
            # piotr 080515 fixed fog
            # I think that the bbox_for_viewing_model call can be expensive.
            # I have to preserve this value or find another way of computing it.
            bbox = self.assy.bbox_for_viewing_model()
            scale = bbox.scale()
            enable_fog() #k needed?? [bruce 080915 question]
            setup_fog(self.vdist - scale, self.vdist + scale, self.fogColor)
            # [I suspect the following comment is about a line that has since
            #  been moved elsewhere -- bruce 080911]
            # this next line really should be just before rendering
            # the atomic model itself.  I dunno where that is. [bradg I think]

        # ask mode to validate self.selobj (might change it to None)
        # (note: self.selobj is used in do_glselect_if_wanted)
        self._selobj_and_hicolor = self.validate_selobj_and_hicolor()

        # do modelview setup (needed for GL_SELECT or regular drawing)
        self._setup_modelview()
            #bruce 050608 moved modelview setup here, from just before the mode.Draw call

        # set self.stereo_* attributes based on current user prefs values
        # (just once per draw event, before anything might use these attributes)
        self._update_stereo_settings()

        # do hit-testing, if requested by some event handler before this
        # call of paintGL (mostly done in do_glselect_if_wanted)

        ###e note: if any objects moved since they were last rendered,
        # this hit-test will still work (using their new posns),
        # but the later depth comparison (below, inside preDraw_glselect_dict)
        # might not work right. See comments there for details.

        self.glselect_dict.clear()
            # this will be filled iff we do a gl_select draw,
            # then used only in the same paintGL call to alert some objects
            # they might be the one under the mouse

        self.setup_shaders_each_frame()
        
        self.configure_enabled_shaders()
            # I don't know if this is needed this early (i.e. before
            # do_glselect_if_wanted), but it shouldn't hurt (though it
            # can't come much earlier than this, and must come after
            # setup_shaders_each_frame which must come after glprefs.update).
            # Supposedly we only need one call of this per paintGL call
            # (see its docstring for details), so we'll see if only this one
            # is sufficient. [bruce 090304]

        self.do_glselect_if_wanted()
            # note: if self.glselect_wanted, this sets up a special projection
            # matrix, and leaves it in place (effectively trashing the
            # projection matrix of the caller)

        self._setup_projection() # setup the usual projection matrix

        # Compute frustum planes required for frustum culling - piotr 080331
        # Moved it right after _setup_projection is called (piotr 080331)
        # Note that this method is also called by "do_glselect_if_wanted",
        # but computes different planes. The second call (here) will 
        # re-compute the frustum planes according to the current projection 
        # matrix.
        if self._use_frustum_culling:
            self._compute_frustum_planes()

        # In the glselect_wanted case, we now know (in glselect_dict)
        # which objects draw any pixels at the mouse position,
        # but not which one is in front. (The near/far info from
        # GL_SELECT has too wide a range to tell us that.)
        # (In the shader primitive case we might know a specific object,
        #  but not always, as long as some objects are not drawn
        #  using shaders.)
        # So we have to get them to tell us their depth at that point
        # (as it was last actually drawn)
            ###@@@ should do that for bugfix; also selobj first
        # (and how it compares to the prior measured depth-buffer value there,
        #  as passed in glselect_wanted, if we want to avoid selecting
        #  something when it's obscured by non-selectable drawing in
        #  front of it).
        if self.glselect_dict:
            # kluge: this is always the case if self.glselect_wanted was set
            # and self.selobj was set, since selobj is always stored in
            # glselect_dict then; if not for that, we might need to reset
            # selobj to None here for empty glselect_dict -- not sure, not
            # fully analyzed. [bruce 050612]

##            self.configure_enabled_shaders() #### new call 090304, maybe not needed
            
            newpicked = self.preDraw_glselect_dict() # retval is new mouseover object, or None
            # now record which object is hit by the mouse in self.selobj
            # (or None if none is hit); and (later) overdraw it for highlighting.
            if newpicked is not self.selobj:
                self.set_selobj( newpicked, "newpicked")
                self._selobj_and_hicolor = self.validate_selobj_and_hicolor()
                    # REVIEW: should set_selobj also call that, and save hicolor
                    # in an attr of self, so self._selobj_and_hicolor is not needed?
                # future: we'll probably need to notify some observers that
                # selobj changed (if in fact it did).
                # REVIEW: we used to print this in the statusbar:
                ## env.history.statusbar_msg("%s" % newpicked)
                # but it was messed up by Build Atoms "click to do x" msg.
                # that message is nim now, so we could restore this if desired.
                # should we? [bruce 080915 comment]

        # otherwise don't change prior selobj -- we have a separate system
        # to set it back to None when needed (which has to be implemented
        # in the bareMotion methods of instances stored in self.graphicsMode --
        # would self.bareMotion (which doesn't exist now) be better? (REVIEW)
        # [later: see also UNKNOWN_SELOBJ, I think]
        
        ### REVIEW: I suspect the above comment, and not resetting selobj here,
        # is wrong, at least when selobj has no depth at all at the current 
        # location; and that this error causes a "selobj stickiness" bug
        # when moving the mouse directly from selobj onto non-glname objects
        # (or buggy-glname objects, presently perhaps including shader spheres 
        # in Build Atoms when the debug_pref 'Use batched primitive shaders?' 
        # is set). [bruce 090105 comment]

        # draw according to self.graphicsMode

        glMatrixMode(GL_MODELVIEW) # this is assumed within Draw methods

        # these are modified below as needed:
        draw_saved_bg_image = False # whether to draw previously cached image, this frame
        capture_saved_bg_image = False # whether to capture a new image from what we draw this frame
        bg_image_comparison_data = None # if this changes, discard any previously cached image
        
        if debug_pref("GLPane: use cached bg image? (experimental)",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True):
            # experimental implementation, has bugs (listed here or in
            # submethods when known, mostly in GLPane_image_methods)
            if self._resize_just_occurred:
                self._cached_bg_image_comparison_data = None
                # discard cached image, and do *neither* capture nor draw of
                # cached image on this frame (the first one drawn after resize).
                # This seems to prevent crash due to resize (in GEForceFX OpenGL
                # driver, in a "processing colors" routine),
                # at least when we meet all of these conditions: [bruce 080922]
                # - test on iMac G5, Mac OS 10.3.9
                # - do the print below
                # - comment out self.do_glselect_if_wanted() above (highlighting)
                # - comment out drawing the depth part of the cached image
                ## print "debug fyi: skipping bg image ops due to resize"
                # ... Actually, crash can still happen if we slightly expand width
                # and then trigger redraw by mouseover compass.
            else:
                bg_image_comparison_data = self._get_bg_image_comparison_data()
                cached_image_is_valid = same_vals( bg_image_comparison_data,
                                                   self._cached_bg_image_comparison_data)
                if cached_image_is_valid:
                    draw_saved_bg_image = True
                else:
                    capture_saved_bg_image = True
                    if bg_image_comparison_data == self._cached_bg_image_comparison_data: 
                        print "DEBUG FYI: equal values not same_vals:\n%r, \n%r" % \
                          ( bg_image_comparison_data, self._cached_bg_image_comparison_data ) ###
                pass
            pass
        else:
            self._cached_bg_image_comparison_data = None
            
        if draw_saved_bg_image:
            self._draw_saved_bg_image() # in GLPane_image_methods
                # saved and drawn outside of stereo loop (intentional)
                # (instead of ordinary drawing inside it, separate code below)
        else:
            # capture it below, and only after that, do this assignment:
            # self._cached_bg_image_comparison_data = bg_image_comparison_data
            pass

##        self.configure_enabled_shaders() ##### REVIEW where to call this, and how often [this is the only pre-090304 call]

        for stereo_image in self.stereo_images_to_draw:
            self._enable_stereo(stereo_image)
                # note: this relies on modelview matrix already being correctly
                # set up for non-stereo drawing

            if not draw_saved_bg_image:
                self._do_drawing_for_bg_image_inside_stereo()
                # otherwise, no need, we called _draw_saved_bg_image above
                
            if not capture_saved_bg_image:
                self._do_other_drawing_inside_stereo()
                # otherwise, do this later (don't mess up captured image)
            
            self._disable_stereo()
            continue # to next stereo_image

        if capture_saved_bg_image:
            self._capture_saved_bg_image() # in GLPane_image_methods
            self._cached_bg_image_comparison_data = bg_image_comparison_data
            for stereo_image in self.stereo_images_to_draw:
                self._enable_stereo(stereo_image)
                self._do_other_drawing_inside_stereo()
                self._disable_stereo()
                continue # to next stereo_image
            pass

        # let parts (other than the main part) draw a text label, to warn
        # the user that the main part is not being shown [bruce 050408]
        # [but let the GM control this: moved and renamed
        #  part.draw_text_label -> GM.draw_glpane_label; bruce 090219]
        try:
            self.set_drawing_phase('main/draw_glpane_label') #bruce 070124, renamed 090219
            self.graphicsMode.draw_glpane_label(self)
        except:
            # if this happens at all, it'll happen too often to bother non-debug
            # users with a traceback (but always print an error message)
            if debug_flags.atom_debug:
                print_compact_traceback( "atom_debug: exception in self.graphicsMode.draw_glpane_label(self): " )
            else:
                print "bug: exception in self.graphicsMode.draw_glpane_label; use ATOM_DEBUG to see details"
        self.set_drawing_phase('?')

        # draw the compass (coordinate-orientation arrows) in chosen corner
        if env.prefs[displayCompass_prefs_key]:
            self.drawcompass()
            # review: needs drawing_phase? [bruce 070124 q]

        # draw the "origin axes"
        ### TODO: put this, and the GM part of it (now at start of basicGraphicsMode.Draw),
        # into one of the methods
        # _do_other_drawing_inside_stereo or _do_drawing_for_bg_image_inside_stereo
        if env.prefs[displayOriginAxis_prefs_key]:
            for stereo_image in self.stereo_images_to_draw:
                self._enable_stereo(stereo_image, preserve_colors = True)

                # REVIEW: can we simplify and/or optim by moving this into
                # the same stereo_image loop used earlier for _do_graphicsMode_Draw?
                # [bruce 080911 question]
                
                # WARNING: this code is duplicated, or almost duplicated,
                # in GraphicsMode.py and GLPane.py.
                # It should be moved into a common method in drawers.py.
                # [bruce 080710 comment]

                #ninad060921 The following draws a dotted origin axis
                # if the correct preference is checked. The GL_DEPTH_TEST is
                # disabled while drawing this, so that if axis is behind a
                # model object, it will just draw it as a dotted line (since
                # this drawing will occur, but the solid origin axes drawn
                # in other code, overlapping these, will be obscured).
                #bruce 080915 REVIEW: can we clarify that by doing the solid
                # axis drawing here as well?
                if env.prefs[displayOriginAsSmallAxis_prefs_key]:
                    drawOriginAsSmallAxis(self.scale, (0.0, 0.0, 0.0), dashEnabled = True)
                else:
                    drawaxes(self.scale, (0.0, 0.0, 0.0), coloraxes = True, dashEnabled = True)

                self._disable_stereo()

        self._draw_cc_test_images()
            # draw some test images related to the confirmation corner
            # (needs to be done before draw_overlay)
        
        # draw various overlays

        self.set_drawing_phase('overlay')

        # Draw ruler(s) if "View > Rulers" is checked
        # (presently in main menus, not in prefs dialog)
        if env.prefs[displayRulers_prefs_key]:
            if (self.ortho or env.prefs[showRulersInPerspectiveView_prefs_key]):
                self.guides.draw()

        # draw the confirmation corner
        try:
            glMatrixMode(GL_MODELVIEW) #k needed?
            self.graphicsMode.draw_overlay() #bruce 070405 (misnamed)
        except:
            print_compact_traceback( "exception in self.graphicsMode.draw_overlay(): " )
        
        self.set_drawing_phase('?')

        # restore standard glMatrixMode, in case drawing code outside of paintGL
        # forgets to do this [precaution]
        glMatrixMode(GL_MODELVIEW)
            # (see discussion in bug 727, which was caused by that)
            # (todo: it might also be good to set mode-specific
            #  standard GL state before checking self.redrawGL in paintGL)

        return # from standard_repaint_0 (the main rendering submethod of paintGL)

    def _do_drawing_for_bg_image_inside_stereo(self): #bruce 080919 split this out
        """
        """
        if self._fog_test_enable:
            enable_fog()

        self.set_drawing_phase('main')
        
        try:
            self._do_graphicsMode_Draw()
                # draw self.part (the model), with chunk & atom selection
                # indicators, and graphicsMode-specific extras,
                # including axes, and handles/rubberbands/labels (Draw_other).
                # Some GraphicsModes only draw portions of the model.
                #
                ### todo: Likely refactoring: call only some of the 4 Draw_*
                # methods this calls as of 090310, in case some of them depend
                # on more prefs than the model itself does (should help with
                # the optim of caching a fixed background image).
                # [bruce 080919/090311 comment]
        finally:
            self.set_drawing_phase('?')

            if self._fog_test_enable: #bruce 090219 moved inside 'finally'
                disable_fog()

        return

    def _do_graphicsMode_Draw(self): #bruce 090219, revised 090311
        """
        Private helper for various places in which we need to draw the model
        (in this GLPane mixin and others).
        """
        def func():
            # see comment in _do_drawing_for_bg_image_inside_stereo
            # for refactoring suggestions [bruce 090311]
            self.graphicsMode.Draw_preparation()
            self.graphicsMode.Draw_axes()
            self.graphicsMode.Draw_model()
            self.graphicsMode.Draw_other()
            return            
        self._call_func_that_draws_model( func)
        return

    def _whole_model_drawingset_change_indicator(self):
        """
        #doc
        """
        ## BUG:
        #
        # The following implementation is not correct:
        # - view changes are not taken into account, but need to affect
        #   drawingsets due to frustum culling
        # - doesn't include effect of visual preferences
        # (workaround for both: select something to update the display)
        #
        # Also, current code that uses this has bugs:
        # - ignores necessary drawing not inside DrawingSets
        #   - jigs, dna/protein styles, overlap indicators, atom sel wireframes, bond vanes...
        #   - extra drawing by graphicsMode, e.g. expr handles, dna ribbons
        #   - probably more
        #
        # So it is only used when a debug_pref is set.
        # Another comment or docstring has more info on purpose and status.
        # [bruce 090309]
        return self.part and \
               (self.part,
                self.assy.model_change_indicator(),
                self.assy.selection_change_indicator()
               )

    def _do_other_drawing_inside_stereo(self): #bruce 080919 split this out
        """
        [might be misnamed -- does not (yet) do *all* other drawing
         currently done inside stereo]
        """
        # highlight selobj if necessary, by drawing it again in highlighted
        # form (never inside fog).
        # It was already drawn normally, but we redraw it now for three reasons:
        # - it might be in a display list in non-highlighted form (and if so,
        #   the above draw used that form);
        # - if fog is enabled, the above draw was inside fog; this one won't be;
        # - we need to draw it into the stencil buffer too, so subsequent calls
        #   of self.graphicsMode.bareMotion event handlers can find out whether
        #   the mouse is still over it, and avoid asking for hit-test again
        #   if it was (probably an important optimization).
        selobj, hicolor = self._selobj_and_hicolor
        if selobj is not None:
            self.draw_highlighted_objectUnderMouse(selobj, hicolor)
                # REVIEW: is it ok that the mode had to tell us selobj and hicolor
                # (and validate selobj) before drawing the model?

        # draw transparent things (e.g. Build Atoms water surface,
        # parts of Plane or ESPImage nodes)
        # [bruce 080919 bugfix: do this inside the stereo loop]

        self.call_Draw_after_highlighting(self.graphicsMode)
        return

    def call_Draw_after_highlighting(self, graphicsMode, pickCheckOnly = False):
        """
        Call graphicsMode.Draw_after_highlighting() in the correct way
        (with appropriate drawing_phase), with exception protection,
        and return whatever it returns. Pass pickCheckOnly.

        @note: calls of this should be inside a stereo loop, to be correct.

        @note: event processing or drawing code should use this method to call
            graphicsMode.Draw_after_highlighting(), rather than
            calling it directly. But implementations of Draw_after_highlighting
            itself should call their superclass versions directly.
        """
        # note: some existing calls of this are buggy since not in a stereo
        # loop. They are bad in other ways too. See comment there for more info.
        
        ### REVIEW: any need for _call_func_that_draws_model? I guess not now,
        # but revise if we ever want to use csdls with objects drawn by this,
        # in any GraphicsMode. [bruce 090219 comment]
        self.set_drawing_phase('main/Draw_after_highlighting')
        try:
            res = self.graphicsMode.Draw_after_highlighting( pickCheckOnly)
                # e.g. draws water surface in Build mode [###REVIEW: ok inside stereo loop?],
                # or transparent parts of ESPImage or Plane (must be inside stereo loop).
                # Note: this is called in the main model coordinate system
                # (perhaps modified for current stereo image),
                # just like self.graphicsMode.Draw_model, etc
                # [bruce 061208/080919 comment]
        except:
            res = None
            msg = "bug in %r.Draw_after_highlighting ignored" % (graphicsMode,)
            print_compact_traceback(msg + ": ")
            pass
        self.set_drawing_phase('?')
        return res

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

    def selobj_hicolor(self, obj):
        """
        If obj was to be highlighted as selobj
        (whether or not it's presently self.selobj),
        what would its highlight color be?
        Or return None if obj should not be allowed as selobj.
        """
        try:
            hicolor = self.graphicsMode.selobj_highlight_color( obj)
                #e should implem noop version in basicMode [or maybe i did]
            # mode can decide whether selobj should be highlighted
            # (return None if not), and if so, in what color
        except:
            if debug_flags.atom_debug:
                msg = "atom_debug: selobj_highlight_color exception for %r" % (obj,)
                print_compact_traceback(msg + ": ")
            else:
                print "bug: selobj_highlight_color exception for %r; " \
                      "for details use ATOM_DEBUG" % (obj,)
            hicolor = None
        return hicolor

    def drawcompass(self):
        #bruce 080910 moved body into its own file
        #bruce 080912 removed aspect argument
        #bruce 081015 put constant parts into a display list (possible speedup),
        # and created class Compass to make this easier
        self.compass.draw(
            self.aspect,
            self.quat,
            self.compassPosition,
            self.graphicsMode.compass_moved_in_from_corner,
            env.prefs[displayCompassLabels_prefs_key]
         )
        return

    pass # end of class

# ==

if "test same_vals during import": #bruce 080922, of interest to GLPane_image_methods
    # note: we don't want to define this test in utilities.Comparison itself,
    # since it should not import geometry.VQT. REVIEW: move it into VQT?
    from utilities.Comparison import same_vals, SAMEVALS_SPEEDUP
    # not a full test, just look for known bugs and print warnings if found
    ALWAYS_PRINT = False
    used_version = SAMEVALS_SPEEDUP and "C" or "python"
        # no way to test the other version (see comment where same_vals is defined)
    from geometry.VQT import Q
    if not same_vals( Q(1,0,0,0), Q(1,0,0,0) ):
        # this bug was in the C version but not the Python version;
        # Eric M fixed it in samevalshelp.c rev 14311, 080922
        print "BUG: not same_vals( Q(1,0,0,0), Q(1,0,0,0) ) [%s version]" % used_version
    elif ALWAYS_PRINT:
        print "fyi: same_vals( Q(1,0,0,0), Q(1,0,0,0) ) is True (correct) [%s version]" % used_version
    pass

# end
