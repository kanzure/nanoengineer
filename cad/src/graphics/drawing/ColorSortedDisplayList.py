# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
ColorSortedDisplayList.py - A set of primitives to be drawn as a unit,
under runtime-determined drawing styles

@author: Russ
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

This was originally written by Russ in ColorSorter.py.
See that file for its pre-090220 history.

bruce 090220 added reentrancy, split it into this file.

bruce 090312 generalizing API (and soon, functionality) to support
other kinds of non-shader drawing besides color-sorted DLs.

TODO:

Change ColorSorter into a normal class with distinct instances.
Give it a stack of instances rather than its current _suspend system.
Refactor some things between ColorSorter and ColorSortedDisplayList
(which needs renaming). [bruce 090220 comment]
"""

from OpenGL.GL import GL_COMPILE
from OpenGL.GL import glNewList
from OpenGL.GL import glEndList
from OpenGL.GL import glCallList
from OpenGL.GL import glDeleteLists
from OpenGL.GL import glGenLists
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import glPushName
from OpenGL.GL import glPopName
from OpenGL.GL import glColor3fv
from OpenGL.GL import GL_LIGHTING


from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import hoverHighlightingColorStyle_prefs_key
from utilities.prefs_constants import HHS_HALO
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import SS_HALO

from utilities.debug import print_compact_traceback


import foundation.env as env


from graphics.drawing.CS_workers import drawpolycone_multicolor_worker
from graphics.drawing.CS_workers import drawpolycone_worker
from graphics.drawing.CS_workers import drawtriangle_strip_worker

from graphics.drawing.patterned_drawing import isPatternedDrawing
from graphics.drawing.patterned_drawing import startPatternedDrawing
from graphics.drawing.patterned_drawing import endPatternedDrawing

import graphics.drawing.drawing_constants as drawing_constants

import graphics.drawing.drawing_globals as drawing_globals

from graphics.drawing.gl_lighting import apply_material

# ==

_csdl_id_counter = 0
_warned_del = False

# ==

class ColorSortedDisplayList:    #Russ 080225: Added.
    """
    The ColorSorter's parent uses one of these to store color-sorted display
    list state.  It's passed in to ColorSorter.start() .

    CSDLs are now created with a TransformControl reference as an argument (and
    are internally listed in it while they exist). This TransformControl
    reference is constant (although the transform in the TransformControl is
    mutable).

    For convenience, the TransformControl argument can be left out if you don't
    want to use a TransformControl to move the CSDL. This has the same effect as
    giving a TransformControl whose transform remains as the identity matrix.

    @note: as of 090223, the transformControl can also be a Chunk.
           Details to be documented later.
    """

    # default values of instance variables [note: incomplete]

    ### todo: some of these and/or the dl variables not listed here
    #   could be renamed to indicate that they are private.

    transformControl = None # might be a TransformControl or a Chunk
    reentrant = False #bruce 090220
    _transform_id = None #bruce 090223
    _untransformed_data = None #bruce 090223
    spheres = () #bruce 090224
    cylinders = () #bruce 090224
    _drawing_funcs = () #bruce 090312

    def __init__(self, transformControl = None, reentrant = False):
        """
        """
        self._clear_when_deallocate_DLs_might_be_unsafe()
            #bruce 090224 moved this earlier, made it do more,
            # removed inits from this method which are now redundant

        if reentrant:
            self.reentrant = True # permits reentrant ColorSorter.start

        # [Russ 080915: Added.
        # A unique integer ID for each CSDL.
        global _csdl_id_counter
        _csdl_id_counter += 1
        self.csdl_id = _csdl_id_counter

        # Support for lazily updating drawing caches, namely a
        # timestamp showing when this CSDL was last changed.
        self.changed = drawing_constants.eventStamp()

        if transformControl is not None:
            self.transformControl = transformControl
            try:
                ##### KLUGE (temporary), for dealing with a perhaps-permanent change:
                # transformControl might be a Chunk,
                # which has (we assume & depend on) no transform_id
                _x = self.transformControl.transform_id # should fail for Chunk
            except AttributeError:
                # Assume transformControl is a Chunk.
                # Note: no point in doing self.updateTransform() yet (to record
                # untransformed data early) -- we have no data, since no
                # shader primitives have been stored yet. Untransformed data
                # will be recorded the first time it's transformed (after init,
                # and after each time primitives get cleared and remade).
                pass
            else:
                assert _x is not None
                assert _x is not -1
                self._transform_id = _x
            pass

# CSDLs should not have a glname since they are never a selobj.
# Any testCases which depend on this should be rewritten.
# [bruce 090311]
##        # Russ 081122: Mark CSDLs with a glname for selection.
##        # (Note: this is a temporary kluge for testing. [bruce 090223 comment])
##        self.glname = env._shared_glselect_name_dict. \
##                      alloc_my_glselect_name(self)
##        ###self.glname = 0x12345678 ### For testing.

        # Whether to draw in the selection over-ride color.
        self.selected = False

        ### TODO [bruce 090114 comment]: a near-term goal is to remove
        # self.selected and self.dl, so that self only knows
        # how to draw either way, but always finds out as-needed
        # (from client state) which way to actually draw.
        # Reviewing the current code, I think the only remaining
        # essential use of self.dl is in CrystalShape.py
        # (see new comment in its docstring for how to clean that up),
        # and the only remaining essential use of self.selected
        # (aside from maintaining self.dl, no longer needed if it's removed)
        # is in ColorSorter.finish (which should be replaced by
        # passing finish the same drawing-style arguments that
        # CSDL.draw accepts).

        return

    def __repr__(self): #bruce 090224
        name = self.__class__.__name__.split('.')[-1]
        if self.transformControl:
            return "<%s at %#x for %r>" % (name, id(self), self.transformControl)
        else:
            return "<%s at %#x>" % (name, id(self))
        pass

    # Russ 080925: Added.
    def transform_id(self):
        """
        Return the transform_id of the CSDL, or None if there is no associated
        TransformControl (including if self.transformControl is not an instance
        of TransformControl).
        """
        return self._transform_id

    def has_nonempty_DLs(self): #bruce 090225 [090312: maybe inline all uses and remove from API]
        """
        Are any of our toplevel OpenGL display lists nonempty
        (i.e. do they have any drawing effect)?

        @note: This test is useful, since we build all our toplevel display
            lists even if they are empty, due to some client code which may
            require this. When shaders are turned on, having all DLs empty
            will be common.
        """
        return bool( self._per_color_dls)

    def has_nonshader_drawing(self): #bruce 090312
        """
        Do we have any drawing to do other than shader primitives?
        """
        # (see comments in GLPrimitiveSet for how this might evolve further)
        return self.has_nonempty_DLs() or self._drawing_funcs

    # ==

    def start(self, pickstate): #bruce 090224 split this out of caller
        """
        Clear self and start collecting new primitives for use inside it.

        (They are collected by staticmethods in the ColorSorter singleton class,
         and saved partly in ColorSorter class attributes, partly in self
         by direct assignment (maybe not anymore), and partly in self by
         methods ColorSorter calls in self.)

        [meant to be called only by ColorSorter.start, for now]
        """
        if pickstate is not None:
            # todo: refactor to remove this deprecated argument
            ### review: is it correct to not reset self.selected when this is None??
            self.selectPick(pickstate)
            pass

        # Russ 080915: This supports lazily updating drawing caches.
        self.changed = drawing_constants.eventStamp()

        # Clear the primitive data to start collecting a new set.

        # REVIEW: is it good that we don't also deallocate DLs here?
        # Guess: yes if we reuse them, no if we don't.
        # It looks like finish calls _reset, which deallocates them,
        # so we might as well do that right here instead. Also, that
        # way I can remove _reset from finish, which is good since
        # I've made _reset clearPrimitives, which is a bug if done
        # in finish (when were added between start and finish).
        # [bruce 090224 comment and revision]
        ## self._clearPrimitives()
        self._reset()

        if 0: # keep around, in case we want a catchall DL in the future
            #bruce 090114 removed support for
            # [note: later: these are no longer in drawing_globals]
            # (not (drawing_globals.allow_color_sorting and
            #       drawing_globals.use_color_sorted_dls)):
            # This is the beginning of the single display list created when
            # color sorting is turned off. It is ended in
            # ColorSorter.finish . In between, the calls to
            # draw{sphere,cylinder,polycone} methods pass through
            # ColorSorter.schedule_* but are immediately sent to *_worker
            # where they do OpenGL drawing that is captured into the display
            # list.
            try:
                if self.dl == 0:
                    self.activate() # Allocate a display list for our use.
                    pass
                # Start a single-level list.
                glNewList(self.dl, GL_COMPILE)
            except:
                print ("data related to following exception: self.dl = %r" %
                       (self.dl,)) #bruce 070521
                raise
            pass
        return

    # ==

    def finish(self, sorted_by_color): #bruce 090224 split this out of caller
        """
        Finish collecting new primitives for use in self, and store them all
        in self, ready to be drawn in various ways.

        [meant to be called only by ColorSorter.start, for now]
        """
##        self._reset()
##            # (note: this deallocates any existing display lists)

        if self.transformControl and (self.spheres or self.cylinders):
            self.updateTransform()
                # needed to do the transform for the first time,
                # even if it didn't change. Review: refactor to
                # whereever we first compile these down? That
                # might be a different place in self.draw vs.
                # draw from DrawingSet.

        selColor = env.prefs[selectionColor_prefs_key]

        # Note: if sorted_by_color is empty, current code still builds all
        # toplevel display lists, though they are noops. This may be needed
        # by some client code which uses those dls directly. Client code
        # wanting to know if it needs to draw our dls should test
        # self.has_nonempty_DLs(), which tests self._per_color_dls,
        # or self.has_nonshader_drawing(), which reports on that or any
        # other kind of nonshader (immediate mode opengl) drawing we might
        # have. [bruce 090225/090312 comment]

        # First build the lower level per-color sublists of primitives.

        for color, funcs in sorted_by_color.iteritems():
            sublists = [glGenLists(1), 0]

            # Remember the display list ID for this color.
            self._per_color_dls.append([color, sublists])

            glNewList(sublists[0], GL_COMPILE)
            opacity = color[3]

            if opacity == -1:
                #russ 080306: "Unshaded colors" for lines are signaled
                # by an opacity of -1 (4th component of the color.)
                glDisable(GL_LIGHTING) # Don't forget to re-enable it!
                pass

            for func, params, name in funcs:
                if name:
                    glPushName(name)
                else:
                    pass ## print "bug_2: attempt to push non-glname", name
                func(params)    # Call the draw worker function.
                if name:
                    glPopName()
                    pass
                continue

            if opacity == -1:
                # Enable lighting after drawing "unshaded" objects.
                glEnable(GL_LIGHTING)
                pass
            glEndList()

            if opacity == -2:
                # piotr 080419: Special case for drawpolycone_multicolor
                # create another display list that ignores
                # the contents of color_array.
                # Remember the display list ID for this color.

                sublists[1] = glGenLists(1)

                glNewList(sublists[1], GL_COMPILE)

                for func, params, name in funcs:
                    if name:
                        glPushName(name)
                    else:
                        pass ## print "bug_3: attempt to push non-glname", name
                    if func == drawpolycone_multicolor_worker:
                        # Just to be sure, check if the func
                        # is drawpolycone_multicolor_worker
                        # and call drawpolycone_worker instead.
                        # I think in the future we can figure out
                        # a more general way of handling the
                        # GL_COLOR_MATERIAL objects. piotr 080420
                        pos_array, color_array_junk, rad_array = params
                        drawpolycone_worker((pos_array, rad_array))
                    elif func == drawtriangle_strip_worker:
                        # piotr 080710: Multi-color modification
                        # for triangle_strip primitive (used by
                        # reduced protein style).
                        pos_array, normal_array, color_array_junk = params
                        drawtriangle_strip_worker((pos_array,
                                                   normal_array,
                                                   None))
                    if name:
                        glPopName()
                        pass
                    continue
                glEndList()

            continue

        # Now the upper-level lists call all of the per-color sublists.
        #### REVIEW: these are created even when empty. Is that necessary?
        # [bruce 090224 Q]

        # One with colors.
        color_dl = self.color_dl = glGenLists(1)
        glNewList(color_dl, GL_COMPILE)

        for color, dls in self._per_color_dls:

            opacity = color[3]
            if opacity < 0:
                #russ 080306: "Unshaded colors" for lines are signaled
                # by a negative alpha.
                glColor3fv(color[:3])
                # piotr 080417: for opacity == -2, i.e. if
                # GL_COLOR_MATERIAL is enabled, the color is going
                # to be ignored, anyway, so it is not necessary
                # to be tested here
            else:
                apply_material(color)

            glCallList(dls[0])

            continue
        glEndList()

        # A second one without any colors.
        nocolor_dl = self.nocolor_dl = glGenLists(1)
        glNewList(nocolor_dl, GL_COMPILE)
        for color, dls in self._per_color_dls:
            opacity = color[3]

            if opacity == -2 \
               and dls[1] > 0:
                # piotr 080420: If GL_COLOR_MATERIAL is enabled,
                # use a regular, single color dl rather than the
                # multicolor one. Btw, dls[1] == 0 should never
                # happen.
                glCallList(dls[1])
            else:
                glCallList(dls[0])

        glEndList()

        # A third DL implements the selected appearance.
        selected_dl = self.selected_dl = glGenLists(1)
        glNewList(selected_dl, GL_COMPILE)
        # russ 080530: Support for patterned selection drawing modes.
        patterned = isPatternedDrawing(select = True)
        if patterned:
            # Patterned drawing needs the colored dl drawn first.
            glCallList(color_dl)
            startPatternedDrawing(select = True)
            pass
        # Draw solid color (unpatterned) or an overlay pattern, in the
        # selection color.
        apply_material(selColor)
        glCallList(nocolor_dl)
        if patterned:
            # Reset from patterning drawing mode.
            endPatternedDrawing(select = True)
        glEndList()
        pass

    # ==

    # Russ 080925: For batched primitive drawing, drawing-primitive functions
    # conditionally collect lists of primitive IDs here in the CSDL, rather than
    # sending them down through the ColorSorter schedule methods into the DL
    # layer. Later, those primitive lists are collected across the CSDLs in
    # a DrawingSet, into the per-primitive-type VBO caches and MultiDraw indices
    # managed by its GLPrimitiveSet.  Most of the intermediate stuff will be
    # cached in the underlying GLPrimitiveBuffer, since GLPrimitiveSet is meant
    # to be very transient.
    #
    # This can be factored when we get a lot of primitive shaders.  For now,
    # simply cache the drawing-primitive IDs at the top level of CSDL.

    def addSphere(self, center, radius, color, glname):
        """
        Allocate a shader sphere primitive (in the set of all spheres
         that are able to be drawn in this GL resource context),
        set up its drawing parameters,
        and add its primID to self's list of spheres
        (so it will be drawn when self is drawn, or included in
        DrawingSet drawing indices when they are drawn and include self).

        . center is a VQT point.
        . radius is a number.
        . color is a list of components: [R, G, B].
        . glname comes from the _gl_name_stack.
        """
        self.spheres += drawing_globals.sphereShaderGlobals.primitiveBuffer.addSpheres(
            [center], radius, color, self.transform_id(), glname)
        self._clear_derived_primitive_caches()
        return

    # Russ 090119: Added.
    def addCylinder(self, endpts, radii, color, glname):
        """
        Like addSphere, but for cylinders. See addSphere docstring for details.

        . endpts is a tuple of two VQT points.
        . radii may be a single number, or a tuple of two radii for taper.
        . color is a list of components: [R, G, B] or [R, G, B, A].
        . glname comes from the _gl_name_stack.
        """
        self.cylinders += drawing_globals.cylinderShaderGlobals.primitiveBuffer.addCylinders(
            [endpts], radii, color, self.transform_id(), glname)
        self._clear_derived_primitive_caches()
        return

    # ==

    def clear_drawing_funcs(self):
        self._drawing_funcs = ()

    def add_drawing_func(self, func):
        if not self._drawing_funcs:
            self._drawing_funcs = []
        self._drawing_funcs += [func]

    # ==

#### NOTE: the methods draw_in_abs_coords and nodes_containing_selobj
# don't make sense in this class in the long run, since it is not meant
# to be directly used as a "selobj" or as a Node. I presume they are
# only needed by temporary testing and debugging code, and they should be
# removed when no longer needed. [bruce 090114 comment]
#
# Update, bruce 090311: I'm removing them now (since we need to test the
# claim that nothing but test code depends on them). Any testCases this
# breaks should be rewritten to put their CSDLs inside wrapper objects
# which provide these methods.
#
##    # Russ 081128: Used by preDraw_glselect_dict() in standard_repaint_0(), and
##    # _draw_highlighted_selobj() in _do_other_drawing_inside_stereo().
##    def draw_in_abs_coords(self, glpane, color):
##        self.draw(highlighted = True, highlight_color = color)
##        return
##
##    # Russ 081128: Used by GLPane._update_nodes_containing_selobj().
##    def nodes_containing_selobj(self):
##        # XXX Only TestGraphics_GraphicsMode selects CSDL's now, so no
##        # XXX connection to the Model Tree.
##        return []

    # ==

    ##### TODO: FIX TERMINOLOGY BUG:
    # in the following three methodnames and all localvar names and comments
    # where they are used, replace shader with primitiveBuffer. [bruce 090303]

    def shaders_and_primitive_lists(self): #bruce 090218
        """
        Yield each pair of (primitiveBuffer, primitive-list) which we need to draw.
        """
        if self.spheres:
            assert drawing_globals.sphereShaderGlobals.primitiveBuffer
            yield drawing_globals.sphereShaderGlobals.primitiveBuffer, self.spheres
        if self.cylinders:
            assert drawing_globals.cylinderShaderGlobals.primitiveBuffer
            yield drawing_globals.cylinderShaderGlobals.primitiveBuffer, self.cylinders
        return

    def shader_primID_pairs(self): #bruce 090223
        for shader, primitives in self.shaders_and_primitive_lists():
            for p in primitives:
                yield shader, p
        return

    def draw_shader_primitives(self, *args): #bruce 090218, needed only for CSDL.draw
        for shader, primitives_junk in self.shaders_and_primitive_lists():
            index = self.drawIndices[shader]
            shader.draw(index, *args)
            continue
        return

    def updateTransform(self): #bruce 090223
        """
        Update transformed version of cached coordinates,
        using the current transform value of self.transformControl.
        This should only be called if transformControl was provided to__init__,
        and must be called whenever its transform value changes, sometime before
        we are next drawn.

        @note: in current implem, this is only needed if self is drawn using
               shader primitives, and may only work properly if
               self.transformControl is a Chunk.
        """
        try:
            s_p_pairs = list(self.shader_primID_pairs())

            if not s_p_pairs:
                # optimization
                return

            if not self._untransformed_data:
                # save untransformed data here for reuse (format depends on shader)
                _untransformed_data = []
                    # don't retain this in self until it's all collected
                    # (otherwise we get confusing bugs from its being too short,
                    #  if there's an exception while collecting it)
                for shader, p in s_p_pairs:
                    ut = shader.grab_untransformed_data(p)
                    _untransformed_data += [ut]
                    continue
                self._untransformed_data = _untransformed_data
                # print "remade len %d of utdata in" % len(self._untransformed_data), self
                assert len(self._untransformed_data) == len( s_p_pairs )
                assert s_p_pairs == list(self.shader_primID_pairs())
                    # this could fail if shader_primID_pairs isn't deterministic
                    # or if its value gets modified while collecting it
                    # (either scenario would be a bug)
                pass
            else:
                # print "found %d utdata in" % len(self._untransformed_data), self
                assert len(self._untransformed_data) == len( s_p_pairs )
                    # this could fail if the length of s_p_pairs could vary
                    # over time, without resets to self._untransformed_data
                    # (which would be a bug)

            transform = self.transformControl
            for (shader, p), ut in zip( s_p_pairs , self._untransformed_data ):
                shader.store_transformed_primitive( p, ut, transform)
                continue
            pass
        except:
            # might as well skip the update but not mess up anything else
            # being drawn at the same time (this typically runs during drawing)
            msg = "bug: ignoring exception in updateTransform in %r" % self
            print_compact_traceback(msg + ": ")
        return

    def draw(self,
             highlighted = False,
             selected = False,
             patterning = True,
             highlight_color = None,
             draw_shader_primitives = True, #bruce 090312 renamed from draw_primitives
             transform_nonshaders = True, #bruce 090312 renamed from transform_DLs
         ):
        """
        Simple all-in-one interface to CSDL drawing.

        Allocate a CSDL in the parent class and fill it with the ColorSorter:
            self.csdl = ColorSortedDisplayList()
            ColorSorter.start(glpane, self.csdl)
            drawsphere(...), drawcylinder(...), drawpolycone(...), and so on.
            ColorSorter.finish()

        Then when you want to draw the display lists call csdl.draw() with the
        desired options:

        @param highlighted: Whether to draw highlighted.

        @param selected: Whether to draw selected.

        @param patterning: Whether to apply patterned drawing styles for
          highlighting and selection, according to the prefs settings.
          If not set, it's as if the solid-color prefs are chosen.

        @param highlight_color: Option to over-ride the highlight color set in
          the color scheme preferences.

        @param draw_shader_primitives: Whether to draw our shader primitives.
            Defaults to True.

        @param transform_nonshaders: Whether to apply self.transformControl to
            our non-shader drawing (such as DLs). Defaults to True.
        """

        patterned_highlighting = (patterning and
                                  isPatternedDrawing(highlight = highlighted))
        halo_selection = (selected and
                          env.prefs[selectionColorStyle_prefs_key] == SS_HALO)
        halo_highlighting = (highlighted and
                             env.prefs[hoverHighlightingColorStyle_prefs_key] ==
                             HHS_HALO)


        # KLUGES which should be replaced by our having suitable new attrs,
        # such as glpane or glprefs or glresourcecontext (replacing drawing_globals):

        drawing_phase = drawing_globals.drawing_phase # kluge in CSDL.draw

        # (the other kluge is not having glpane.glprefs to pass to apply_material,
        #  in draw; we do have glpane in finish but no point in using it there
        #  until we have it in .draw too, preferably by attr rather than arg
        #  (should review that opinion).)


        # Russ 081128 (clarified, bruce 090218):
        #
        # GLPrimitiveSet.draw() calls this method (CSDL.draw) on the CSDLs
        # in its _CSDLs_with_nonshader_drawing attribute (a list of CSDLs),
        # passing draw_shader_primitives = False to only draw the DLs, and
        # transform_nonshaders = False to avoid redundantly applying their
        # TransformControls.
        #
        # It gathers the shader primitives in a set of CSDLs into one big
        # drawIndex per primitive type, and draws each drawIndex in a big batch.
        #
        # This method (CSDL.draw) is also called to
        # draw *both* DLs and primitives in a CSDL, e.g. for hover-highlighting.
        #
        # Russ 081208: Skip drawing shader primitives while in GL_SELECT.
        #
        # Bruce 090218: support cylinders too.
        prims_to_do = (drawing_phase != "glselect" and
                       draw_shader_primitives and
                       (self.spheres or self.cylinders))
        if prims_to_do:
            # Cache drawing indices for just the primitives in this CSDL,
            # in self.drawIndices, used in self.draw_shader_primitives below.
            if not self.drawIndices:
                for shader, primitives in self.shaders_and_primitive_lists():
                    self.drawIndices[shader] = shader.makeDrawIndex(primitives)
                    continue
                pass
            pass

        if self._drawing_funcs and drawing_phase != "glselect_glname_color": #bruce 090312
            # These ignore our drawing-style args;
            # they also are cleared independently of start/finish,
            # and changing them doesn't set our last-changed timestamp.
            # All this is intentional. (Though we might decide to add a kind
            # which does participate in patterned drawing; this might require
            # supplying more than one func, or a dict of colors and nocolor
            # funcs....)
            if self.transformControl and transform_nonshaders:
                glPushMatrix()
                self.transformControl.applyTransform()
            for func in self._drawing_funcs:
                try:
                    func()
                except:
                    msg = "bug: exception in drawing_func %r in %r, skipping it" % (func, self)
                    print_compact_traceback(msg + ": ")
                    pass
                continue
            if self.transformControl and transform_nonshaders:
                glPopMatrix()
            pass

        # Normal or selected drawing are done before a patterned highlight
        # overlay, and also when not highlighting at all.  You'd think that when
        # we're drawing a solid highlight appearance, there'd be no need to draw
        # the normal appearance first, because it will be obscured by the
        # highlight.  But halo selection extends beyond the object and is only
        # obscured by halo highlighting.  [russ 080610]
        # Russ 081208: Skip DLs when drawing shader-prims with glnames-as-color.
        DLs_to_do = (drawing_phase != "glselect_glname_color"
                     and self.has_nonempty_DLs())

        # the following might be changed, then are used repeatedly below;
        # this simplifies the various ways we can handle transforms [bruce 090224]
        callList = glCallList # how to call a DL, perhaps inside our transform
        transform_once = False # whether to transform exactly once around the
            # following code (as opposed to not at all, or once per callList)

        if self.transformControl and transform_nonshaders:
            if prims_to_do and DLs_to_do:
                # shader primitives have transform built in, but DLs don't,
                # so we need to get in and out of local coords repeatedly
                # (once for each callList) during the following
                # (note similar code in DrawingSet.draw): [bruce 090224]
                callList = self._callList_inside_transformControl
            elif DLs_to_do:
                # we need to get into and out of local coords just once
                transform_once = True
            else:
                pass # nothing special needed for just shader prims (or nothing)
            pass

        if transform_once:
            glPushMatrix()
            self.transformControl.applyTransform()

        if (patterned_highlighting or not highlighted or
            (halo_selection and not halo_highlighting)) :
            if selected:
                # Draw the selected appearance.
                if prims_to_do:                  # Shader primitives.
                    self.draw_shader_primitives( highlighted, selected,
                               patterning, highlight_color)
                    pass

                if DLs_to_do:                    # Display lists.
                    # If the selection mode is patterned, the selected_dl does
                    # first normal drawing and then draws an overlay.
                    callList(self.selected_dl)
                    pass
                pass
            else:
                # Plain, old, solid drawing of the base object appearance.
                if prims_to_do:
                    self.draw_shader_primitives()   # Shader primitives.
                    pass

                if DLs_to_do:
                    callList(self.color_dl)    # Display lists.
                    pass
                pass
            pass

        if highlighted:

            if prims_to_do:                      # Shader primitives.
                self.draw_shader_primitives( highlighted, selected,
                           patterning, highlight_color)
                pass

            if DLs_to_do:                        # Display lists.
                if patterned_highlighting:
                    # Set up a patterned drawing mode for the following draw.
                    startPatternedDrawing(highlight = highlighted)
                    pass

                # Draw a highlight overlay (solid, or in an overlay pattern.)
                if highlight_color is not None:
                    hcolor = highlight_color
                else:
                    hcolor = env.prefs[hoverHighlightingColor_prefs_key]
                apply_material(hcolor)
                callList(self.nocolor_dl)

                if patterned_highlighting:
                    # Reset from a patterned drawing mode set up above.
                    endPatternedDrawing(highlight = highlighted)
                    pass
                pass

            pass

        if transform_once:
            glPopMatrix()

        return

    def _callList_inside_transformControl(self, DL): #bruce 090224
        glPushMatrix()
        self.transformControl.applyTransform()
        glCallList(DL)
        glPopMatrix()
        return

    # == CSDL state maintenance

    def activate(self):
        """
        Make a top-level display list id ready, but don't fill it in.
        """
        ### REVIEW: after today's cleanup, I think this can no longer be called.
        # (Though it may be a logic bug that CrystalShape.py never calls it.)
        # [bruce 090114 comment]

        # Display list id for the current appearance.
        if not self.selected:
            self.color_dl = glGenLists(1)
        else:
            self.selected_dl = glGenLists(1)
            pass
        self.selectDl()
            #bruce 070521 added these two asserts
        assert type(self.dl) in (type(1), type(1L))
        assert self.dl != 0    # This failed on Linux, keep checking. (bug 2042)
        return

    def selectPick(self, boolVal):
        """
        Remember whether we're selected or not.
        """
        self.selected = boolVal
        self.selectDl()
        return

    def selectDl(self):
        """
        Change to either the normal-color display list or the selected one.
        """
        self.dl = self.selected and self.selected_dl or self.color_dl
        return

    # == state clearing methods, also used to set up initial state
    #    (should be refactored a bit more [bruce 090224 comment])

    def _reset(self):
        """
        Return to initialized state (but don't clear constructor parameters).

        Only legal when our GL context is current.
        """
        #bruce 090224 revision: not worth the bug risk and maintenance issue
        # to figure out whether we have any state that needs clearing --
        # so just always clear it all.
        self.deallocate_displists()
        return

    def deallocate_displists(self):
        """
        Free any allocated display lists.
        (Also clear or initialize shader primitives and all other cached
         drawing state, but not constructor parameters.)

        @note: this is part of our external API.

        @see: _clear_when_deallocate_DLs_might_be_unsafe,
              which does all possible clearing *except* for
              deallocating display lists, for use when we're not sure
              deallocating them is safe.
        """
        # With CSDL active, self.dl duplicates either selected_dl or color_dl.

        #bruce 090224 rewrote to make no assumptions about which DLs
        # are currently allocated or overlapping -- just delete all valid ones.
        DLs = {}
        for dl in [self.dl, self.color_dl, self.nocolor_dl, self.selected_dl]:
            DLs[dl] = dl
        # piotr 080420: The second level dl's are 2-element lists of DL ids
        # rather than just a list of ids. The second DL is used in case
        # of multi-color objects and is required for highlighting
        # and selection (not in rc1)
        for clr_junk, dls in self._per_color_dls: # Second-level dl's.
            for dl in dls: # iterate over DL pairs.
                DLs[dl] = dl
        for dl in DLs:
            if dl: # skip 0 or None (not sure if None ever happens)
                glDeleteLists(dl, 1)
            continue
        self._clear_when_deallocate_DLs_might_be_unsafe()
        return

    def _clear_when_deallocate_DLs_might_be_unsafe(self):
        """
        Clear and initialize cached and stored drawing state (but not
        constructor parameters), except for deallocating OpenGL display lists.
        (In theory, this is safe to call even when our GL context is not
         current.)

        @note: this does not deallocate display lists.
               Therefore, it might be a VRAM memory leak if any DLs
               are allocated. So don't call it except via
               deallocate_displists, if possible.
        """
        #bruce 090224 added _clearPrimitives, renamed, revised docstring
        self.dl = 0             # Current display list (color or selected.)
        self.color_dl = 0       # DL to set colors, call each lower level list.
        self.selected_dl = 0    # DL with a single (selected) over-ride color.
        self.nocolor_dl = 0     # DL of lower-level calls for color over-rides.
        self._per_color_dls = [] # Lower level, per-color primitive sublists.
        self._clearPrimitives()
        return

    def _clearPrimitives(self):
        """
        Clear cached and stored drawing state related to shader primitives.
        """
        # REVIEW: any reason to keep this separate from its caller,
        # _clear_when_deallocate_DLs_might_be_unsafe? Maybe other callers
        # can call that instead? For now, there are some calls for which
        # this is unclear, so I'm not merging them. [bruce 090224 comment]

        # Free them in the GLPrimitiveBuffers.
        # TODO: refactor to use self.shaders_and_primitive_lists().

        #bruce 090224 revised conditions so they ignore current prefs
        if self.spheres:
            drawing_globals.sphereShaderGlobals.primitiveBuffer.releasePrimitives(self.spheres)
        if self.cylinders:
            drawing_globals.cylinderShaderGlobals.primitiveBuffer.releasePrimitives(self.cylinders)

        # Included drawing-primitive IDs. (These can be accessed more generally
        # using self.shaders_and_primitive_lists().)
        self.spheres = []
        self.cylinders = []

        self._clear_derived_primitive_caches()
        return

    def _clear_derived_primitive_caches(self): #bruce 090224 split this out
        """
        Call this after modifying our lists of shader primitives.
        """
        # Russ 081128: A cached primitives drawing index.  This is only used
        # when drawing individual CSDLs for hover-highlighting, for testing,
        # and during development.  Normally,
        # primitives from a number of CSDLs are collected into a GLPrimitiveSet
        # with a drawing index covering all of them.
        #bruce 090218: corrected above comment, and changed drawIndex ->
        # drawIndices so it can support more than one primitive type.
        self.drawIndices = {}

        self._untransformed_data = None
        return

    def __del__(self): # Russ 080915
        """
        Called by Python when an object is being freed.
        """
        self.destroy()
        return

    def destroy(self):
        """
        Free external resources and break reference cycles.
        """
        # Free any OpenGL resources.
        ### REVIEW: Need to wait for our OpenGL context to become current when
        # GLPane calls its method saying it's current again.  See chunk dealloc
        # code for details. This hangs NE1 now, so it's commented out.
        ## self.deallocate_displists()

        # Free primitives stored in VBO hunks.
        self._clearPrimitives() #bruce 090223 guess implem; would be redundant
            # with deallocate_displists if we called that here
            ## REVIEW: call _clear_when_deallocate_DLs_might_be_unsafe instead?

        # clear constructor parameters if they might cause reference cycles.
        self.transformControl = None #bruce 090223
        return

    pass # end of class ColorSortedDisplayList

# end
