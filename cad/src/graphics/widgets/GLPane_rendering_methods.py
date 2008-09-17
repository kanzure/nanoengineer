# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_rendering_methods.py

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

bruce 080913 split this out of class GLPane
"""

TEST_DRAWING = False # True  ## Debug/test switch.  Never check in a True value.
if TEST_DRAWING:
    from prototype.test_drawing import test_drawing
    pass

from OpenGL.GL import GL_CURRENT_RASTER_POSITION_VALID
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_LEQUAL
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_MODELVIEW_STACK_DEPTH
from OpenGL.GL import GL_RGB
from OpenGL.GL import GL_STENCIL_BUFFER_BIT
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import glDepthFunc
from OpenGL.GL import glDisable
from OpenGL.GL import glDrawPixels
from OpenGL.GL import glEnable
from OpenGL.GL import glFlush
from OpenGL.GL import glGetBooleanv
from OpenGL.GL import glGetInteger
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glRasterPos3f
from OpenGL.GL import glReadPixels

from OpenGL.GLU import gluUnProject

import graphics.drawing.drawing_globals as drawing_globals

from graphics.drawing.drawers import drawOriginAsSmallAxis
from graphics.drawing.drawers import drawaxes

from graphics.drawing.gl_lighting import disable_fog
from graphics.drawing.gl_lighting import enable_fog
from graphics.drawing.gl_lighting import setup_fog

from graphics.drawing.drawcompass import drawcompass
from graphics.drawing.Guides import Guides

from utilities import debug_flags

from utilities.debug import print_compact_traceback, print_compact_stack

### from utilities.debug import profile, doProfile ###

import foundation.env as env

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

# ==

class GLPane_rendering_methods(object):
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
            # see also self.object_for_glselect_name()
            # (which replaces env.obj_with_glselect_name[] as of 080220 --
            #  though in outside code, that's still used as of 080915.
            #  A fuller story: it's in the middle of an unfinished
            #  cleanup (changing from global to per-assy), started on 080220.)

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

    ### def _paintGL(self):                             ###
    ###     profile( self.paintGL2)                     ###
    ###     doProfile(False)                            ###

    def _paintGL(self):
        """
        [private; the body of paintGL in GLPane.py]
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
        self._needs_repaint = False
            # do this now, even if we have an exception during the repaint

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

    def render_scene(self):#bruce 061208 split this out so some modes can override it (also removed obsolete trans_feature experiment)

        #k not sure whether next things are also needed in the split-out standard_repaint [bruce 050617]

        drawing_globals.glprefs.update() #bruce 051126; kluge: have to do this before lighting *and* inside standard_repaint_0

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
        """
        This is the main rendering routine -- it clears the OpenGL window,
        does all drawing done during paintGL, and does hit-testing if
        requested by event handlers before this call of paintGL.
        """
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
            enable_fog() #k needed?? [bruce 080915 question]
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

        self.do_glselect_if_wanted()
            # note: if self.glselect_wanted, this sets up a special projection
            # matrix, and leaves it in place (effectively trashing the
            # projection matrix of the caller)

        self._setup_projection() # setup the usual projection matrix

        # Compute frustum planes required for frustum culling - piotr 080331
        # Moved it right after _setup_projection is called (piotr 080331)
        # Note that this method is also called by "do_glselect_if_wanted".
        # The second call will re-compute the frustum planes according to 
        # the current projection matrix.
        if self._use_frustum_culling:
            self._compute_frustum_planes()

        # In the glselect_wanted case, we now know (in glselect_dict)
        # which objects draw any pixels at the mouse position,
        # but not which one is in front. (The near/far info from
        # GL_SELECT has too wide a range to tell us that.)
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
            newpicked = self.preDraw_glselect_dict() # retval is new mouseover object, or None
            # now record which object is hit by the mouse in self.selobj
            # (or None if none is hit); and (later) overdraw it for highlighting.
            if newpicked is not selobj:
                self.set_selobj( newpicked, "newpicked")
                selobj, hicolor = self.validate_selobj_and_hicolor()
                    # REVIEW: should set_selobj also do this, and save hicolor
                    # in an attr of self?
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
            # It was already drawn normally, but we redraw it now for three reasons:
            # - it might be in a display list in non-highlighted form (and if so,
            #   the above draw used that form);
            # - if fog is enabled, the above draw was inside fog; this one won't be;
            # - we need to draw it into the stencil buffer too, so subsequent calls
            #   of self.graphicsMode.bareMotion event handlers can find out whether
            #   the mouse is still over it, and avoid asking for hit-test again
            #   if it was (probably an important optimization).
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
        # Piotr reply: Yes, I think this is a bug.
        # It should be moved inside the stereo loop.
        #
        # Bruce 080915 update: we'll fix that when someone has time to test it.

        try: # try/finally for drawing_phase
            self.drawing_phase = 'main/Draw_after_highlighting'
            self.graphicsMode.Draw_after_highlighting()
                # e.g. draws water surface in Build mode
                # note: this is called in the main model coordinate system,
                # just like self.graphicsMode.Draw() [bruce 061208 comment]
        finally:
            self.drawing_phase = '?'

        # let parts (other than the main part) draw a text label, to warn
        # the user that the main part is not being shown [bruce 050408]
        try:
            self.drawing_phase = 'main/draw_text_label' #bruce 070124
            self.part.draw_text_label(self)
        except:
            # if this happens at all, it'll happen too often to bother non-debug
            # users with a traceback (but always print an error message)
            if debug_flags.atom_debug:
                print_compact_traceback( "atom_debug: exception in self.part.draw_text_label(self): " )
            else:
                print "bug: exception in self.part.draw_text_label; use ATOM_DEBUG to see details"
        self.drawing_phase = '?'

        # draw the compass (coordinate-orientation arrows) in chosen corner
        if env.prefs[displayCompass_prefs_key]:
            self.drawcompass()
            # review: needs drawing_phase? [bruce 070124 q]

        # draw the "origin axes"
        if env.prefs[displayOriginAxis_prefs_key]:
            for stereo_image in self.stereo_images_to_draw:
                self._enable_stereo(stereo_image, preserve_colors = True)

                # REVIEW: can we simplify and/or optim by moving this into
                # the same stereo_image loop used earlier for graphicsMode.Draw?
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

        # draw some test images related to the confirmation corner

        ccdp1 = debug_pref("Conf corner test: redraw at lower left",
                           Choice_boolean_False,
                           prefs_key = True)
        ccdp2 = debug_pref("Conf corner test: redraw in-place",
                           Choice_boolean_False,
                           prefs_key = True)
        
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

        # restore standard glMatrixMode, in case drawing code outside of paintGL
        # forgets to do this [precaution]
        glMatrixMode(GL_MODELVIEW)
            # (see discussion in bug 727, which was caused by that)
            # (todo: it might also be good to set mode-specific
            #  standard GL state before checking self.redrawGL in paintGL)

        return # from standard_repaint_0 (the main rendering submethod of paintGL)

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
        drawcompass(self,
                    self.aspect,
                    self.quat,
                    self.compassPosition,
                    self.graphicsMode.compass_moved_in_from_corner,
                    env.prefs[displayCompassLabels_prefs_key]
                   )
        return
    
    pass

# end
