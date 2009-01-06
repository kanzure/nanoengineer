# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_highlighting_methods.py - highlight drawing and hit-detection

@author: Bruce
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

bruce 080915 split this out of class GLPane_rendering_methods
"""

from OpenGL.GL import GL_ALWAYS
from OpenGL.GL import GL_BACK
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_DEPTH_COMPONENT
from OpenGL.GL import GL_DEPTH_FUNC
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_EQUAL
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_KEEP
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_RENDER
from OpenGL.GL import GL_REPLACE
from OpenGL.GL import GL_RGBA
from OpenGL.GL import GL_SELECT
from OpenGL.GL import GL_STENCIL_TEST
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import GL_VIEWPORT
from OpenGL.GL import glClear
from OpenGL.GL import glColorMask
from OpenGL.GL import glDepthMask
from OpenGL.GL import glDepthFunc
from OpenGL.GL import glDisable
from OpenGL.GL import glDrawPixels
from OpenGL.GL import glEnable
from OpenGL.GL import glFinish
from OpenGL.GL import glFlush
from OpenGL.GL import glGetInteger
from OpenGL.GL import glGetIntegerv
from OpenGL.GL import glInitNames
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glWindowPos3i
from OpenGL.GL import glReadBuffer
from OpenGL.GL import glReadPixels
from OpenGL.GL import glReadPixelsf
from OpenGL.GL import glRenderMode
from OpenGL.GL import glSelectBuffer
from OpenGL.GL import glStencilFunc
from OpenGL.GL import glStencilOp
from OpenGL.GL import glViewport

from utilities import debug_flags
from utilities.debug import print_compact_traceback
import foundation.env as env

from utilities.constants import white, orange

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice_boolean_False

import graphics.drawing.drawing_globals as drawing_globals

# suspicious imports [should not really be needed, according to bruce 070919]
from model.bonds import Bond # used only for selobj ordering

# ==

class GLPane_highlighting_methods(object):
    """
    private mixin for providing highlighting/hit-test methods to class GLPane
    (mostly or entirely called from its other mixin GLPane_rendering_methods,
     rather than directly from methods defined in class GLPane)
    """
    # default values for instance variables related to glSelectBuffer feature [bruce 050608]
    # [note, SIZE_FOR_glSelectBuffer is also part of this set, but is now defined in GLPane_minimal.py]
    glselect_wanted = 0 # whether the next paintGL should start with a glSelectBuffer call [bruce 050608]
    current_glselect = False # [bruce 050616] False, or a 4-tuple of parameters for GL_SELECT rendering
        ### TODO: document this better

    # note: self.glselect_dict is defined and initialized in
    # GLPane_rendering_methods, since it's also used there,
    # as well as in methods defined here and called there.
    
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
            pwSize = 1 # Pick window size.  Russ 081128: Was 3.
              # Bruce: Replace 3, 3 with 1, 1? 5, 5? not sure whether this will
              # matter...  in principle should have no effect except speed.
              # Russ: For glname rendering, 1x1 is better because it doesn't
              # have window boundary issues.  We get the coords of a single
              # pixel in the window for the mouse position.

            #bruce 050615 for use by nodes which want to set up their own projection matrix.
            self.current_glselect = (wX, wY, pwSize, pwSize)
            self._setup_projection( glselect = self.current_glselect ) # option makes it use gluPickMatrix

            # Russ 081209: Added.
            debugPicking = debug_pref("GLPane: debug mouseover picking?",
                                      Choice_boolean_False, prefs_key = True )

            if drawing_globals.use_batched_primitive_shaders:
                # Russ 081122: There seems to be no way to access the GL name
                # stack in shaders.  Instead, for mouseover, draw shader
                # primitives with glnames as colors in glRenderMode(GL_RENDER),
                # then read back the pixel color (glname) and depth value.

                # Temporarily replace the full-size viewport with a little one
                # at the mouse location, matching the pick matrix location.
                # Otherwise, we will draw a closeup of that area into the whole
                # window, rather than a few pixels.  This isn't a problem in
                # GL_SELECT rendering mode, because it doesn't modify the frame
                # buffer, just returning hits by graphics primitives when they
                # are inside the clipping boundaries.
                saveVwpt = glGetIntegerv(GL_VIEWPORT)
                # (Don't set the viewport *before* _setup_projection(), it needs
                # to read the current whole-window viewport to set up glselect.
                # See explanation in the _setup_projection() docstring.)
                glViewport(wX, wY, pwSize, pwSize) # Same as current_glselect.
                
                # First, clear the pixel RGBA to zeros and a depth of 1.0
                # (far), so we won't confuse a color with a glname if there are
                # no shader primitives drawn.
                saveDepthFunc = glGetInteger(GL_DEPTH_FUNC)
                glDepthFunc(GL_ALWAYS)
                glWindowPos3i(wX, wY, 1) # Note the Z coord.
                gl_format, gl_type = GL_RGBA, GL_UNSIGNED_BYTE
                glDrawPixels(pwSize, pwSize, gl_format, gl_type, (0, 0, 0, 0))
                glDepthFunc(saveDepthFunc)

                # Should be already in glRenderMode(GL_RENDER).
                # Note: _setup_projection leaves the matrix mode as GL_PROJECTION.
                glMatrixMode(GL_MODELVIEW) 
                try:
                    # Use glnames-as-color mode in shaders, and draw only primitives.
                    drawing_globals.sphereShader.setPicking(True)
                    self.set_drawing_phase("glselect_glname_color")

                    for stereo_image in self.stereo_images_to_draw:
                        self._enable_stereo(stereo_image)
                        self.graphicsMode.Draw()
                        self._disable_stereo()
                except:
                    print_compact_traceback(
                        "exception in graphicsMode.Draw() during glname_color;"
                        "drawing ignored; restoring modelview matrix: ")
                    self._disable_stereo()
                    glMatrixMode(GL_MODELVIEW)
                    self._setup_modelview( ) ### REVIEW: correctness of this is unreviewed!
                    # now it's important to continue, at least enough to restore other gl state
                    pass
                drawing_globals.sphereShader.setPicking(False)
                self.set_drawing_phase('?')

                # Restore the viewport.
                glViewport(saveVwpt[0], saveVwpt[1], saveVwpt[2], saveVwpt[3])

                # Read pixel value from the back buffer and re-assemble glname.
                glFinish() # Make sure the drawing has completed.
                rgba = glReadPixels( wX, wY, 1, 1, gl_format, gl_type )[0][0]
                pixZ = glReadPixelsf( wX, wY, 1, 1, GL_DEPTH_COMPONENT)[0][0]
                # Comes back sign-wrapped, in spite of specifying UNSIGNED_BYTE.
                def us(b):
                    if b < 0: return 256 + b
                    return b
                bytes = tuple([us(b) for b in rgba])
                glname = (bytes[0] << 24 | bytes[1] << 16 |
                          bytes[2] << 8 | bytes[3])
                if debugPicking:
                    print ("shader mouseover xy %d %d, " %  (wX, wY) +
                           "rgba bytes (0x%x, 0x%x, 0x%x, 0x%x), " % bytes +
                           "Z %f, glname 0x%x" % (pixZ,glname))
                    pass

                ### XXX These need to be merged with the DL selection below.
                if glname:
                    obj = self.object_for_glselect_name(glname)
                    if debugPicking:
                        print "shader mouseover glname=%r, obj=%r." % (glname, obj)
                    if obj is None:
                        print "bug: object_for_glselect_name returns None for glname %r." % glname
                    else:
                        self.glselect_dict[id(obj)] = obj
                        pass
                    pass
                pass

            if self._use_frustum_culling:
                self._compute_frustum_planes() 
                # piotr 080331 - the frustum planes have to be setup after the 
                # projection matrix is setup. I'm not sure if there may
                # be any side effects - see the comment below about
                # possible optimization.
            glSelectBuffer(self.SIZE_FOR_glSelectBuffer)
                # Note: this allocates a new select buffer,
                # and glRenderMode(GL_RENDER) returns it and forgets it, 
                # so it's required before *each* call of glRenderMode(GL_SELECT) +
                # glRenderMode(GL_RENDER), not just once to set the size.
                # Ref: http://pyopengl.sourceforge.net/documentation/opengl_diffs.html
                # [bruce 080923 comment]
            glInitNames()

            # REVIEW: should we also set up a clipping plane just behind the
            # hit point, as (I think) is done in ThumbView, to reduce the
            # number of candidate objects? This might be a significant
            # optimization, though I don't think it eliminates the chance
            # of having multiple candidates. [bruce 080917 comment]
            
            glRenderMode(GL_SELECT)
            glMatrixMode(GL_MODELVIEW)
            try:
                self.set_drawing_phase('glselect') #bruce 070124
                for stereo_image in self.stereo_images_to_draw:
                    self._enable_stereo(stereo_image)
                    self.graphicsMode.Draw()
                    self._disable_stereo()
            except:
                print_compact_traceback("exception in graphicsMode.Draw() during GL_SELECT; "
                                        "ignored; restoring modelview matrix: ")
                self._disable_stereo()
                glMatrixMode(GL_MODELVIEW)
                self._setup_modelview( ) ### REVIEW: correctness of this is unreviewed!
                # now it's important to continue, at least enough to restore other gl state

            self._frustum_planes_available = False # piotr 080331 
                # just to be safe and not use the frustum planes computed for 
                # the pick matrix
            self.set_drawing_phase('?')
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
            if debugPicking:
                print "DLs %d hits" % len(hit_records)
            for (near, far, names) in hit_records: # see example code, renderpass.py
                ## print "hit record: near, far, names:", near, far, names
                    # e.g. hit record: near, far, names: 1439181696 1453030144 (1638426L,)
                    # which proves that near/far are too far apart to give actual depth,
                    # in spite of the 1- or 3-pixel drawing window (presumably they're vertices
                    # taken from unclipped primitives, not clipped ones).
                del near, far
                if 1:
                    # partial workaround for bug 1527. This can be removed once that bug (in drawer.py)
                    # is properly fixed. This exists in two places -- GLPane.py and modes.py. [bruce 060217]
                    if names and names[-1] == 0:
                        print "%d(g) partial workaround for bug 1527: removing 0 from end of namestack:" % env.redraw_counter, names
                        names = names[:-1]
                if names:
                    # For now, we only use the last element of names,
                    # though (as of long before 080917) it is often longer:
                    # - some code pushes the same name twice (directly and
                    #   via ColorSorter) (see 060725 debug print below);
                    # - chunks push a name even when they draw atoms/bonds
                    #   which push their own names (see 080411 comment below).
                    #
                    # Someday: if we ever support "name/subname paths" we'll
                    # probably let first name interpret the remaining ones.
                    # In fact, if nodes change projection or viewport for
                    # their kids, and/or share their kids, they'd need to
                    # push their own names on the stack, so we'd know how
                    # to redraw the kids, or which ones are meant when they
                    # are shared.
                    if debug_flags.atom_debug and len(names) > 1: # bruce 060725
                        if len(names) == 2 and names[0] == names[1]:
                            if not env.seen_before("dual-names bug"): # this happens for Atoms (colorsorter bug??)
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
                        print "bug: object_for_glselect_name returns None for name %r at end of namestack %r" % (names[-1], names)
                    else:
                        self.glselect_dict[id(obj)] = obj
                            # now these can be rerendered specially, at the end of mode.Draw
                        ##if 0:
                        ##    # this debug print was useful for debugging bug 2945,
                        ##    # and when it happens it's usually a bug,
                        ##    # but not always:
                        ##    # - it's predicted to happen for chunk.renderOverlayText
                        ##    # - and whenever we're using a whole-chunk display style
                        ##    # so we can't leave it in permanently. [bruce 081211]
                        ##    if isinstance( obj, self.assy.Chunk ):
                        ##        print "\n*** namestack topped with a chunk:", obj
                    pass
                continue # next hit_record
            #e maybe we should now sort glselect_dict by "hit priority" (for depth-tiebreaking), or at least put selobj first.
            # (or this could be done lower down, where it's used.) [I think we do this now...]

        return # from do_glselect_if_wanted

    def object_for_glselect_name(self, glname): #bruce 080220
        """
        """
        return self.assy.object_for_glselect_name(glname)

    def alloc_my_glselect_name(self, obj): #bruce 080917
        """
        """
        return self.assy.alloc_my_glselect_name(obj)

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
            self.set_drawing_phase('selobj') #bruce 070124
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
        self.set_drawing_phase('?')

        self.setDepthRange_Normal()

        # restore other gl state
        # (but don't do unneeded OpenGL ops
        #  in case that speeds up OpenGL drawing)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
            # no need to undo glStencilFunc state, I think -- whoever cares will set it up again
            # when they reenable stenciling.
        if not highlight_into_color:
            glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        if not highlight_into_depth:
            glDepthMask(GL_TRUE)
        
        if debug_pref("GLPane: draw stencil buffer?", 
                      Choice_boolean_False,
                      prefs_key = True
                      ):
            # draw stencil buffer in orange [bruce 090105]
            glStencilFunc(GL_EQUAL, 1, 1) # only draw where stencil is set
            glDepthMask(GL_FALSE)
            glDisable(GL_DEPTH_TEST)
            self.draw_solid_color_everywhere(orange)
                # note: we already drew highlighting selobj above, so that won't obscure this
            glEnable(GL_DEPTH_TEST)
            glDepthMask(GL_TRUE)
            pass
        
        glDisable(GL_STENCIL_TEST)

        return # from draw_highlighted_objectUnderMouse

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

                        self.set_drawing_phase('selobj/preDraw_glselect_dict') # bruce 070124
                        method(self, white) # draw depth info (color doesn't matter since we're not drawing pixels)

                        self._disable_stereo()

                    self.set_drawing_phase('?')
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
                    self.set_drawing_phase('?')
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
            if debug_prefix and len(items) > 1: #bruce 081209
                print "%s (%d): complete list of candidates were:" % (debug_prefix, env.redraw_counter), items
            hicolor = self.selobj_hicolor( newpicked)
            if hicolor is None:
                if report_failures:
                    print "debug_pref: preDraw_glselect_dict failure: " \
                          "it worked, but %r hicolor is None, so discarding it" % \
                          (newpicked,) #bruce 081209
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
                counter = env.redraw_counter
                print "%s (%d): target depth %r reached by %r at %r" % \
                      (debug_prefix, counter, targetdepth, candidate, newdepth)
                if newdepth > targetdepth:
                    print "  (too deep by %r, but fudge factor is %r)" % \
                          (newdepth - targetdepth, fudge)
                elif newdepth < targetdepth:
                    print "  (in fact, object is nearer than targetdepth by %r)" % \
                          (targetdepth - newdepth,)
                pass
            return candidate
                # caller should not call us again without clearing depth buffer,
                # otherwise we'll keep returning every object even if its true
                # depth is too high
        if debug_prefix:
            counter = env.redraw_counter
            print "%s (%d): target depth %r NOT reached by %r at %r" % \
                  (debug_prefix, counter, targetdepth, candidate, newdepth)
            print "  (too deep by %r, but fudge factor is only %r)" % \
                  (newdepth - targetdepth, fudge)
        return None

    pass

# end
