# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
ColorSorter.py - A set of primitives to be drawn as a unit,
under runtime-determined drawing styles

@author: Grantham, Russ
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

This was originally written by Brad Grantham (as part of drawer.py)
as a GL optimization to minimize calls on apply_material, 
by sorting primitives into display lists based on color.

Later, it was repurposed by Russ to support runtime-determined drawing styles
and to permit some primitives to be drawn using GLSL shaders.

For early details see drawer.py history. More recent details are here
(though some of them cover the time before drawer.py was split
and might be redundant with drawer.py history):

080210 russ Split the single display-list into two second-level lists (with and
without color) and a set of per-color sublists so selection and hover-highlight
can over-ride Chunk base colors.  ColorSortedDisplayList is now a class in the
parent's displist attr to keep track of all that stuff.

080311 piotr Added a "drawpolycone_multicolor" function for drawing polycone
tubes with per-vertex colors (necessary for DNA display style)

080313 russ Added triangle-strip icosa-sphere constructor, "getSphereTriStrips".

080420 piotr Solved highlighting and selection problems for multi-colored
objects (e.g. rainbow colored DNA structures).

080519 russ pulled the globals into a drawing_globals module and broke drawer.py
into 10 smaller chunks: glprefs.py setup_draw.py shape_vertices.py
ColorSorter.py CS_workers.py CS_ShapeList.py CS_draw_primitives.py drawers.py
gl_lighting.py gl_buffers.py

081003 russ Added sphere shader-primitive support to CSDLs.

081126 russ Added CSDL shader hover-highlight support, including glname drawing.

REVIEW:

bruce 090114: 

* there are a lot of calls of glGenLists(1) that would be VRAM memory leaks
if they didn't deallocate any prior display list being stored in the same attribute
as the new one. I *think* they are not leaks, since self.reset is called
before them, and it calls self.deallocate_displists, but it would be good 
to confirm this by independent review, and perhaps to assert that all 
re-allocated DL id attributes are zero (and zero them in deallocate_displists),
to make this very clear.

* see my comments dated 090114 about cleaning up .dl, .selected, .selectPick,
and activate (and related comments in CrystalShape.py and chunk.py).

russ 090119 Added cylinder shader-primitive support.
"""

from OpenGL.GL import GL_BLEND
from OpenGL.GL import glBlendFunc
from OpenGL.GL import glCallList
from OpenGL.GL import glColor3fv
from OpenGL.GL import GL_COMPILE
from OpenGL.GL import GL_COMPILE_AND_EXECUTE
from OpenGL.GL import glDeleteLists
from OpenGL.GL import glDepthMask
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import glEndList
from OpenGL.GL import GL_FALSE
from OpenGL.GL import glGenLists
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glNewList
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import glPopName
from OpenGL.GL import glPushName
from OpenGL.GL import GL_SRC_ALPHA

from OpenGL.GL import GL_TRUE

import foundation.env as env

from graphics.drawing.gl_lighting import isPatternedDrawing
from graphics.drawing.gl_lighting import startPatternedDrawing
from graphics.drawing.gl_lighting import endPatternedDrawing

from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import hoverHighlightingColorStyle_prefs_key
from utilities.prefs_constants import HHS_HALO
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import SS_HALO

from utilities.debug import print_compact_traceback

import graphics.drawing.drawing_globals as drawing_globals
if drawing_globals.quux_module_import_succeeded:
    import quux

from graphics.drawing.CS_ShapeList import ShapeList_inplace
from graphics.drawing.CS_workers import drawcylinder_worker
from graphics.drawing.CS_workers import drawline_worker
from graphics.drawing.CS_workers import drawpolycone_multicolor_worker
from graphics.drawing.CS_workers import drawpolycone_worker
from graphics.drawing.CS_workers import drawsphere_worker
from graphics.drawing.CS_workers import drawsphere_worker_loop
from graphics.drawing.CS_workers import drawsurface_worker
from graphics.drawing.CS_workers import drawwiresphere_worker
from graphics.drawing.CS_workers import drawtriangle_strip_worker
from graphics.drawing.gl_lighting import apply_material
from graphics.drawing.TransformControl import TransformControl

# ==

_csdl_id_counter = 0
_warned_del = False

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
    """
    def __init__(self, transformControl = None):
        
        # [Russ 080915: Added.
        # A unique integer ID for each CSDL.
        global _csdl_id_counter
        _csdl_id_counter += 1
        self.csdl_id = _csdl_id_counter

        # Support for lazily updating drawing caches, namely a
        # timestamp showing when this CSDL was last changed.
        self.changed = drawing_globals.eventStamp()

        # Included drawing-primitive IDs.
        self.spheres = []
        self.cylinders = []

        # Russ 081128: A cached primitives drawing index.  This is only used
        # when drawing individual CSDLs for hover-highlighting, for testing,
        # and during development.  Normally,
        # primitives from a number of CSDLs are collected into a GLPrimitiveSet
        # with a drawing index covering all of them.
        #bruce 090218: corrected above comment, and changed drawIndex ->
        # drawIndices so it can support more than one primitive type.
        self.drawIndices = {}

        # TransformControl constructor argument is optional.
        self.transformControl = transformControl
        if self.transformControl is not None:
            # Note: this requires the csdlID to be already set!
            self.transformControl.addCSDL(self)
            pass
        # Russ 080915]

        # Russ 081122: Mark CSDLs with a glname for selection.
        self.glname = env._shared_glselect_name_dict.\
                      alloc_my_glselect_name(self)
        ###self.glname = 0x12345678 ### For testing.

        self.clear()

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

    # Russ 080925: Added.
    def transform_id(self):
        """
        Return the transform_id of the CSDL, or None if there is no associated
        TransformControl.
        """
        if self.transformControl is None:
            return None
        return self.transformControl.transform_id

    # Russ 080915: Added.
    def __del__(self):         # Called by Python when an object is being freed.
        self.destroy()
        return
    
    def destroy(self):         # Called by us to break cyclic reference loops.
        # Free any OpenGL resources.
        ### REVIEW: Need to wait for our OpenGL context to become current when
        # GLPane calls its method saying it's current again.  See chunk dealloc
        # code for details. This hangs NE1 now, so it's commented out.
        ## self.deallocate_displists()

        # Unregister the CSDL from its TransformControl, breaking the Python
        # reference cycle so the CSDL can be reclaimed.
        if self.transformControl is not None:
            try:
                transformControl.removeCSDL(self.csdl_id)
            except:
                global _warned_del
                if not _warned_del:
                    print_compact_traceback(
                        "bug (printed only once per session): "
                        "exception in ColorSortedDisplayList.destroy ignored: ")
                    _warned_del = True
                    pass
                pass
            pass
        return

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
    def clearPrimitives(self):
        # Free them in the GLPrimitiveBuffers.
        if drawing_globals.use_batched_primitive_shaders:
            drawing_globals.spherePrimitives.releasePrimitives(self.spheres)

            if drawing_globals.use_cylinder_shaders:
                drawing_globals.cylinderPrimitives.releasePrimitives(
                    self.cylinders)
                pass
            pass
        self.spheres = []
        self.cylinders = []
        self.drawIndices = {}
        return
        
    def addSphere(self, center, radius, color, glname):
        """
        Allocate a sphere primitive and add its ID to the sphere list.
        . center is a VQT point.
        . radius is a number.
        . color is a list of components: [R, G, B].
        . glname comes from the _gl_name_stack.
        """
        self.spheres += drawing_globals.spherePrimitives.addSpheres(
            [center], radius, color, self.transform_id(), glname)
        self.drawIndices = {}
        return

    # Russ 090119: Added.
    def addCylinder(self, endpts, radii, color, glname):
        """
        Allocate a cylinder primitive and add its ID to the cylinder list.
        . endpts is a tuple of two VQT points.
        . radii may be a single number, or a tuple of two radii for taper.
        . color is a list of components: [R, G, B] or [R, G, B, A].
        . glname comes from the _gl_name_stack.
        """
        self.cylinders += drawing_globals.cylinderPrimitives.addCylinders(
            [endpts], radii, color, self.transform_id(), glname)
        self.drawIndices = {}
        return
    
    # ==

    ### REVIEW: the methods draw_in_abs_coords and nodes_containing_selobj
    # don't make sense in this class in the long run, since it is not meant
    # to be directly used as a "selobj" or as a Node. I presume they are
    # only needed by temporary testing and debugging code, and they should be
    # removed when no longer needed. [bruce 090114 comment]
    
    # Russ 081128: Used by preDraw_glselect_dict() in standard_repaint_0(), and
    # draw_highlighted_objectUnderMouse() in _do_other_drawing_inside_stereo().
    def draw_in_abs_coords(self, glpane, color):
        self.draw(highlighted = True, highlight_color = color)
        return

    # Russ 081128: Used by GLPane._update_nodes_containing_selobj().
    def nodes_containing_selobj(self):
        # XXX Only TestGraphics_GraphicsMode selects CSDL's now, so no
        # XXX connection to the Model Tree.
        return []

    # ==

    def shaders_and_primitives(self): #bruce 090218, needed only for CSDL.draw 
        """
        Yield each pair of (shader, primitive-list) which we need to draw.
        """
        if self.spheres:
            assert drawing_globals.spherePrimitives
            yield drawing_globals.spherePrimitives, self.spheres
        if self.cylinders:
            assert drawing_globals.cylinderPrimitives
            yield drawing_globals.cylinderPrimitives, self.cylinders
        return

    def draw_shader_primitives(self, *args): #bruce 090218, needed only for CSDL.draw
        for shader, primitives in self.shaders_and_primitives():
            index = self.drawIndices[shader]            
            shader.draw(index, *args)
            continue
        return
            
    def draw(self, 
             highlighted = False, 
             selected = False,
             patterning = True, 
             highlight_color = None,
             draw_primitives = True ):
        """
        Simple all-in-one interface to CSDL drawing.

        Allocate a CSDL in the parent class and fill it with the ColorSorter:
            self.csdl = ColorSortedDisplayList()
            ColorSorter.start(self.csdl)
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

        @param draw_primitives: Whether to draw shader primitives in the CSDL.
          Defaults to True.
        """

        patterned_highlighting = (patterning and
                                  isPatternedDrawing(highlight = highlighted))
        halo_selection = (selected and
                          env.prefs[selectionColorStyle_prefs_key] == SS_HALO)
        halo_highlighting = (highlighted and
                             env.prefs[hoverHighlightingColorStyle_prefs_key] ==
                             HHS_HALO)

        # Russ 081128 (clarified, bruce 090218):
        # GLPrimitiveSet.draw() calls this method (CSDL.draw) on CSDLs_with_DLs,
        # passing draw_primitives = False to only draw the DLs.
        # It gathers the primitives in a set of CSDLs into one big drawIndex
        # per primitive type, and draws each drawIndex in a big batch.
        #
        # This method (CSDL.draw) is also called to
        # draw *both* DLs and primitives in a CSDL, e.g. for hover-highlighting.
        #
        # Russ 081208: Skip drawing shader primitives while in GL_SELECT.
        #
        # Bruce 090218: support cylinders too.
        prims_to_do = (drawing_globals.drawing_phase != "glselect" and
                       draw_primitives and (self.spheres or self.cylinders))
        if prims_to_do:
            # Cache drawing indices for just the primitives in this CSDL,
            # in self.drawIndices, used in self.draw_shader_primitives below.
            if not self.drawIndices:
                for shader, primitives in self.shaders_and_primitives():
                    self.drawIndices[shader] = shader.makeDrawIndex(primitives)
                    continue
                pass
            pass

        # Normal or selected drawing are done before a patterned highlight
        # overlay, and also when not highlighting at all.  You'd think that when
        # we're drawing a solid highlight appearance, there'd be no need to draw
        # the normal appearance first, because it will be obscured by the
        # highlight.  But halo selection extends beyond the object and is only
        # obscured by halo highlighting.  [russ 080610]
        # Russ 081208: Skip DLs when drawing shader-prims with glnames-as-color.
        DLs_to_do = (drawing_globals.drawing_phase != "glselect_glname_color"
                     and len(self.per_color_dls) > 0)
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
                    glCallList(self.selected_dl)
                    pass
                pass
            else:
                # Plain, old, solid drawing of the base object appearance.
                if prims_to_do:
                    self.draw_shader_primitives()   # Shader primitives.
                    pass

                if DLs_to_do:
                    glCallList(self.color_dl)    # Display lists.
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
                apply_material(highlight_color is not None and highlight_color
                               or env.prefs[hoverHighlightingColor_prefs_key])
                glCallList(self.nocolor_dl)

                if patterned_highlighting:
                    # Reset from a patterned drawing mode set up above.
                    endPatternedDrawing(highlight = highlighted)
                    pass
                pass

            pass
        return

    # ==
    # CSDL state maintenance.

    def clear(self):
        """
        Empty state.
        """
        self.dl = 0             # Current display list (color or selected.)
        self.color_dl = 0       # DL to set colors, call each lower level list.
        self.selected_dl = 0    # DL with a single (selected) over-ride color.
        self.nocolor_dl = 0     # DL of lower-level calls for color over-rides.
        self.per_color_dls = [] # Lower level, per-color primitive sublists.
        return

    def not_clear(self):
        """
        Check for empty state.
        """
        return (self.dl or self.color_dl or self.nocolor_dl or
                self.selected_dl or
                self.per_color_dls and len(self.per_color_dls))

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

    def reset(self):
        """
        Return to initialized state.
        """
        if self.not_clear():
            # deallocate leaves it clear.
            self.deallocate_displists()
            pass
        return

    def deallocate_displists(self):
        """
        Free any allocated display lists.
        """
        # With CSDL active, self.dl duplicates either selected_dl or color_dl.
        if (self.dl != self.color_dl and
            self.dl != self.selected_dl):
            glDeleteLists(self.dl, 1)
        for dl in [self.color_dl, self.nocolor_dl, self.selected_dl]:
            if dl != 0:
                glDeleteLists(dl, 1) 
                pass
            continue
        # piotr 080420: The second level dl's are 2-element lists of DL ids 
        # rather than just a list of ids. The second DL is used in case
        # of multi-color objects and is required for highlighting 
        # and selection (not in rc1)
        for clr, dls in self.per_color_dls: # Second-level dl's.
            for dl in dls: # iterate over DL pairs.
                if dl != 0:
                    glDeleteLists(dl, 1) 
                    pass
                continue
            continue
        self.clear()
        return

    pass # End of ColorSortedDisplayList.

class ColorSorter:

    """
    State Sorter specializing in color (Really any object that can be
    passed to apply_material, which on 20051204 is only color 4-tuples)

    Invoke start() to begin sorting.
    Call finish() to complete sorting and draw all sorted objects.

    Call schedule() with any function and parameters to be sorted by color.
    If not sorting, schedule() will invoke the function immediately.  If
    sorting, then the function will not be called until "finish()".

    In any function which will take part in sorting which previously did
    not, create a worker function from the old function except the call to
    apply_material.  Then create a wrapper which calls
    ColorSorter.schedule with the worker function and its params.

    Also an app can call schedule_sphere and schedule_cylinder to
    schedule a sphere or a cylinder.  Right now this is the only way
    to directly access the native C++ rendering engine.
    """
    __author__ = "grantham@plunk.org"

    # For now, these are class globals.  As long as OpenGL drawing is
    # serialized and Sorting isn't nested, this is okay.  When/if
    # OpenGL drawing becomes multi-threaded, sorters will have to
    # become instances.  This is probably okay because objects and
    # materials will probably become objects of their own about that
    # time so the whole system will get a redesign and
    # reimplementation.

    sorting = False     # Guard against nested sorting
    _sorted = 0         # Number of calls to _add_to_sorter since last
                        # _printstats
    _immediate = 0      # Number of calls to _invoke_immediately since last
                        # _printstats
    _gl_name_stack = [0]     # internal record of GL name stack; 0 is a sentinel
    _parent_csdl = None  # Passed from the start() method to finish().

    def pushName(glname):
        """
        Record the current pushed GL name, which must not be 0.
        """
        #bruce 060217 Added this assert.
        assert glname, "glname of 0 is illegal (used as sentinel)"
        ColorSorter._gl_name_stack.append(glname)

    pushName = staticmethod(pushName)


    def popName():
        """
        Record a pop of the GL name.
        """
        del ColorSorter._gl_name_stack[-1]

    popName = staticmethod(popName)


    def _printstats():
        """
        Internal function for developers to call to print stats on number of
        sorted and immediately-called objects.
        """
        print ("Since previous 'stats', %d sorted, %d immediate: " %
               (ColorSorter._sorted, ColorSorter._immediate))
        ColorSorter._sorted = 0
        ColorSorter._immediate = 0

    _printstats = staticmethod(_printstats)


    def _add_to_sorter(color, func, params):
        """
        Internal function that stores 'scheduled' operations for a later
        sort, between a start/finish
        """
        ColorSorter._sorted += 1
        color = tuple(color)
        if not ColorSorter.sorted_by_color.has_key(color):
            ColorSorter.sorted_by_color[color] = []
        ColorSorter.sorted_by_color[color].append(
            (func, params, ColorSorter._gl_name_stack[-1]))

    _add_to_sorter = staticmethod(_add_to_sorter)


    def schedule(color, func, params): # staticmethod
        if ColorSorter.sorting:

            ColorSorter._add_to_sorter(color, func, params)

        else:

            ColorSorter._immediate += 1 # for benchmark/debug stats, mostly

            # 20060216 We know we can do this here because the stack is
            # only ever one element deep
            name = ColorSorter._gl_name_stack[-1]
            if name:
                glPushName(name)
            ## Don't check in immediate drawing, e.g. preDraw_glselect_dict.
            ## else:
            ##   print "bug_1: attempt to push non-glname", name

            #Apply appropriate opacity for the object if it is specified
            #in the 'color' param. (Also do necessary things such as 
            #call glBlendFunc it. -- Ninad 20071009

            if len(color) == 4:
                opacity = color[3]
            else:
                opacity = 1.0

            if opacity >= 0.0 and opacity != 1.0:	
                glDepthMask(GL_FALSE)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            elif opacity == -1: 
                # piotr 080429: I replaced the " < 0" condition with " == -1"
                # The opacity flag is now used to signal either "unshaded
                # colors" (opacity == -1) or "multicolor object" (opacity == -2)
                glDisable(GL_LIGHTING)          # Don't forget to re-enable it!
                glColor3fv(color[:3])
                pass

            apply_material(color)
            func(params)                # Call the draw worker function.

            if opacity > 0.0 and opacity != 1.0:
                glDisable(GL_BLEND)
                glDepthMask(GL_TRUE)
            elif opacity == -1: 
                # piotr 080429: See my comment above.
                glEnable(GL_LIGHTING)

            if name:
                glPopName()
        return

    schedule = staticmethod(schedule)

    def schedule_sphere(color, pos, radius, detailLevel,
                        opacity = 1.0, testloop = 0):
        """
        Schedule a sphere for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color
            ColorSorter._cur_shapelist.add_sphere(
                lcolor, pos, radius, ColorSorter._gl_name_stack[-1])
            # 20060208 grantham - I happen to know that one detailLevel
            # is chosen for all spheres, I just record it over and
            # over here, and use the last one for the render
            if (ColorSorter.sphereLevel > -1 and
                ColorSorter.sphereLevel != detailLevel):
                raise ValueError, \
                      "unexpected different sphere LOD levels within same frame"
            ColorSorter.sphereLevel = detailLevel
            pass
        else: 
            # Non-C-coded material rendering (might be sorted and/or use shaders)
            vboLevel = drawing_globals.use_drawing_variant
            sphereBatches = drawing_globals.use_batched_primitive_shaders
            if vboLevel == 6 and not sphereBatches:
                #russ 080714: Individual "shader spheres" are signaled
                # by an opacity of -3 (4th component of the color.)
                lcolor = (color[0], color[1], color[2], -3)
            elif len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color	
                pass

            if testloop > 0:
                worker = drawsphere_worker_loop
            else:
                worker = drawsphere_worker
                pass
            
            if sphereBatches and ColorSorter._parent_csdl: # Russ 080925: Added.
                # Collect lists of primitives in the CSDL, rather than sending
                # them down through the ColorSorter schedule methods into DLs.
                assert ColorSorter.sorting # since _parent_csdl is present
                ColorSorter._parent_csdl.addSphere(
                    pos, radius, lcolor,
                    # Mouseover glnames come from ColorSorter.pushName() .
                    ColorSorter._gl_name_stack[-1])
            else:
                ColorSorter.schedule(
                    lcolor, worker, (pos, radius, detailLevel, testloop))

    schedule_sphere = staticmethod(schedule_sphere)

    def schedule_wiresphere(color, pos, radius, detailLevel = 1):
        """
        Schedule a wiresphere for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            assert 0, "Need to implement a C add_wiresphere function."
            ColorSorter._cur_shapelist.add_wiresphere(
                lcolor, pos, radius, ColorSorter._gl_name_stack[-1])
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor, drawwiresphere_worker,
                                 # Use constant-color line drawing.
                                 (color, pos, radius, detailLevel))

    schedule_wiresphere = staticmethod(schedule_wiresphere)

    def schedule_cylinder(color, pos1, pos2, radius, capped = 0, opacity = 1.0):
        """
        Schedule a cylinder for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            ColorSorter._cur_shapelist.add_cylinder(
                lcolor, pos1, pos2, radius,
                ColorSorter._gl_name_stack[-1], capped)
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color		    

            # Russ 090119: Added.
            cylinderBatches = (drawing_globals.use_batched_primitive_shaders and
                               drawing_globals.use_cylinder_shaders)
            if cylinderBatches and ColorSorter._parent_csdl:
                # Collect lists of primitives in the CSDL, rather than sending
                # them down through the ColorSorter schedule methods into DLs.
                assert ColorSorter.sorting # since _parent_csdl is present
                ColorSorter._parent_csdl.addCylinder(
                    # For a tapered cylinder or cone, pass a tuple of two radii.
                    (pos1, pos2), radius, lcolor,
                    # Mouseover glnames come from ColorSorter.pushName() .
                    ColorSorter._gl_name_stack[-1])
            else:
                ColorSorter.schedule(lcolor,
                                 drawcylinder_worker,
                                 (pos1, pos2, radius, capped))

    schedule_cylinder = staticmethod(schedule_cylinder)

    def schedule_polycone(color, pos_array, rad_array,
                          capped = 0, opacity = 1.0):
        """
        Schedule a polycone for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            assert 0, "Need to implement a C add_polycone_multicolor function."
            ColorSorter._cur_shapelist.add_polycone(
                lcolor, pos_array, rad_array,
                ColorSorter._gl_name_stack[-1], capped)
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor, drawpolycone_worker,
                                 (pos_array, rad_array))

    schedule_polycone = staticmethod(schedule_polycone)

    def schedule_polycone_multicolor(color, pos_array, color_array, rad_array,
                                     capped = 0, opacity = 1.0):
        """
        Schedule a polycone for rendering whenever ColorSorter thinks is
        appropriate.

        piotr 080311: this variant accepts a color array as an additional
        parameter
        """
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            assert 0, "Need to implement a C add_polycone function."
            ColorSorter._cur_shapelist.add_polycone_multicolor(
                lcolor, pos_array, color_array, rad_array, 
                ColorSorter._gl_name_stack[-1], capped)
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor,
                                 drawpolycone_multicolor_worker,
                                 (pos_array, color_array, rad_array))

    schedule_polycone_multicolor = staticmethod(schedule_polycone_multicolor)

    def schedule_surface(color, pos, radius, tm, nm):
        """
        Schedule a surface for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if len(color) == 3:		
            lcolor = (color[0], color[1], color[2], 1.0)
        else:
            lcolor = color		    
        ColorSorter.schedule(lcolor, drawsurface_worker, (pos, radius, tm, nm))

    schedule_surface = staticmethod(schedule_surface)

    def schedule_line(color, endpt1, endpt2, dashEnabled,
                      stipleFactor, width, isSmooth):
        """
        Schedule a line for rendering whenever ColorSorter thinks is
        appropriate.
        """
        #russ 080306: Signal "unshaded colors" for lines by an opacity of -1.
        color = tuple(color) + (-1,)
        ColorSorter.schedule(color, drawline_worker,
                             (endpt1, endpt2, dashEnabled,
                              stipleFactor, width, isSmooth))

    schedule_line = staticmethod(schedule_line)


    def schedule_triangle_strip(color, triangles, normals, colors):
        """
        Schedule a line for rendering whenever ColorSorter thinks is
        appropriate.
        """
        ColorSorter.schedule(color, drawtriangle_strip_worker,
                             (triangles, normals, colors))

    schedule_triangle_strip = staticmethod(schedule_triangle_strip)

    def start(csdl, pickstate = None): # staticmethod
        """
        Start sorting - objects provided to "schedule" and primitives such as
        "schedule_sphere" and "schedule_cylinder" will be stored for a sort at
        the time "finish" is called.

        csdl is a ColorSortedDisplayList or None, in which case immediate
        drawing is done.

        pickstate (optional) indicates whether the parent is currently selected.
        """
        #russ 080225: Moved glNewList here for displist re-org.
        # (bruce 090114: removed support for use_color_sorted_vbos)
        
        assert ColorSorter._parent_csdl is None #bruce 090105
        ColorSorter._parent_csdl = csdl  # used by finish()
        if pickstate is not None:
            csdl.selectPick(pickstate)
            pass

        if csdl is not None:
            # Russ 080915: This supports lazily updating drawing caches.
            csdl.changed = drawing_globals.eventStamp()

            # Clear the primitive data to start collecting a new set.
            csdl.clearPrimitives()

            if 0: 
                #bruce 090114 removed support for 
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
                    if csdl.dl == 0:
                        csdl.activate() # Allocate a display list for our use.
                        pass
                    # Start a single-level list.
                    glNewList(csdl.dl, GL_COMPILE)
                except:
                    print ("data related to following exception: csdl.dl = %r" %
                           (csdl.dl,)) #bruce 070521
                    raise
                pass
            pass
        assert not ColorSorter.sorting, \
               "Called ColorSorter.start but already sorting?!"
        ColorSorter.sorting = True
        if drawing_globals.use_c_renderer:
            ColorSorter._cur_shapelist = ShapeList_inplace()
            ColorSorter.sphereLevel = -1
        else:
            ColorSorter.sorted_by_color = {}

    start = staticmethod(start)

    def finish(draw_now = True): # staticmethod
        """
        Finish sorting -- objects recorded since "start" will be sorted and
        invoked now. If there's no CSDL, we're in all-in-one-display-list mode,
        which is still a big speedup over plain immediate-mode drawing.
        """
        if not ColorSorter.sorting:
            assert draw_now, "finish(draw_now = False) makes no sense unless ColorSorter.sorting"
            return                      # Plain immediate-mode, nothing to do.

        from utilities.debug_prefs import debug_pref, Choice_boolean_False
        debug_which_renderer = debug_pref(
            "debug print which renderer",
            Choice_boolean_False) #bruce 060314, imperfect but tolerable

        parent_csdl = ColorSorter._parent_csdl
        ColorSorter._parent_csdl = None
            # this must be done sometime before we return;
            # it can be done here, since nothing in this method after this
            # should use it directly or add primitives to it [bruce 090105]
        if drawing_globals.use_c_renderer:
            quux.shapeRendererInit()
            if debug_which_renderer:
                #bruce 060314 uncommented/revised the next line; it might have
                # to come after shapeRendererInit (not sure); it definitely has
                # to come after a graphics context is created and initialized.
                # 20060314 grantham - yes, has to come after
                # quux.shapeRendererInit .
                enabled = quux.shapeRendererGetInteger(quux.IS_VBO_ENABLED)
                print ("using C renderer: VBO %s enabled" %
                       (('is NOT', 'is')[enabled]))
            quux.shapeRendererSetUseDynamicLOD(0)
            if ColorSorter.sphereLevel != -1:
                quux.shapeRendererSetStaticLODLevels(ColorSorter.sphereLevel, 1)
            quux.shapeRendererStartDrawing()
            ColorSorter._cur_shapelist.draw()
            quux.shapeRendererFinishDrawing()
            ColorSorter.sorting = False

            # So chunks can actually record their shapelist
            # at some point if they want to
            # ColorSorter._cur_shapelist.petrify()
            # return ColorSorter._cur_shapelist      

        else:
            if debug_which_renderer:
                print "using Python renderer"
            color_groups = len(ColorSorter.sorted_by_color)
            objects_drawn = 0

            if parent_csdl is None:
                # Either all in one display list, or immediate-mode drawing.
                ### REVIEW [bruce 090114]: are both possibilities still present, 
                # now that several old options have been removed?
                objects_drawn += ColorSorter.draw_sorted(
                    ColorSorter.sorted_by_color)

                if parent_csdl is not None:
                    # (Note [bruce 090114]: this can't happen now, but I think
                    # it could happen when color sorter was off, before I removed
                    # support for that. ### REVIEW: any future use for this code?)
                    # Terminate a single display list, created when color
                    # sorting is turned off. Started in ColorSorter.start .
                    #russ 080225: Moved glEndList here for displist re-org.
                    glEndList()
                    pass
                pass

            else: #russ 080225

                parent_csdl.reset() 
                    # (note: this deallocates any existing display lists)
                selColor = env.prefs[selectionColor_prefs_key]
                vboLevel = drawing_globals.use_drawing_variant

                # First build the lower level per-color sublists of primitives.
                for color, funcs in ColorSorter.sorted_by_color.iteritems():
                    sublists = [glGenLists(1), 0]

                    # Remember the display list ID for this color.
                    parent_csdl.per_color_dls.append([color, sublists])

                    glNewList(sublists[0], GL_COMPILE)
                    opacity = color[3]

                    if opacity == -1:
                        #russ 080306: "Unshaded colors" for lines are signaled
                        # by an opacity of -1 (4th component of the color.)
                        glDisable(GL_LIGHTING) # Don't forget to re-enable it!
                        pass

                    if opacity == -3 and vboLevel == 6:
                        #russ 080714: "Shader spheres" are signaled
                        # by an opacity of -3 (4th component of the color.)
                        drawing_globals.sphereShader.use(True)
                        pass

                    for func, params, name in funcs:
                        objects_drawn += 1
                        if name:
                            glPushName(name)
                        else:
                            pass ## print "bug_2: attempt to push non-glname", name
                        func(params)    # Call the draw worker function.
                        if name:
                            glPopName()
                            pass
                        continue

                    if opacity == -3 and vboLevel == 6:
                        drawing_globals.sphereShader.use(False)
                        pass

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
                            objects_drawn += 1
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
                                pos_array, color_array, rad_array = params
                                drawpolycone_worker((pos_array, rad_array))
                            elif func == drawtriangle_strip_worker:
                                # piotr 080710: Multi-color modification
                                # for triangle_strip primitive (used by 
                                # reduced protein style).
                                pos_array, normal_array, color_array = params
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
                # One with colors.
                color_dl = parent_csdl.color_dl = glGenLists(1)
                glNewList(color_dl, GL_COMPILE)

                for color, dls in parent_csdl.per_color_dls:

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
                nocolor_dl = parent_csdl.nocolor_dl = glGenLists(1)
                glNewList(nocolor_dl, GL_COMPILE)
                for color, dls in parent_csdl.per_color_dls:                    
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
                selected_dl = parent_csdl.selected_dl = glGenLists(1)
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

            ColorSorter.sorted_by_color = None
            pass
        ColorSorter.sorting = False

        if draw_now:
            # Draw the newly-built display list, and any shader primitives as well.
            if parent_csdl is not None:
                parent_csdl.draw(
                    # Use either the normal-color display list or the selected one.
                    selected = parent_csdl.selected)
        return

    finish = staticmethod(finish)

    def draw_sorted(sorted_by_color):   #russ 080320: factored out of finish().
        """
        Traverse color-sorted lists, invoking worker procedures.
        """
        objects_drawn = 0               # Keep track and return.
        glEnable(GL_LIGHTING)

        for color, funcs in sorted_by_color.iteritems():

            opacity = color[3]
            if opacity == -1:
                #piotr 080429: Opacity == -1 signals the "unshaded color".
                # Also, see my comment in "schedule".
                glDisable(GL_LIGHTING) # Don't forget to re-enable it!
                glColor3fv(color[:3])
            else:
                apply_material(color)
                pass

            for func, params, name in funcs:
                objects_drawn += 1
                if name:
                    glPushName(name)
                else:
                    pass ## print "bug_4: attempt to push non-glname", name
                func(params)            # Call the draw worker function.
                if name:
                    glPopName()
                    pass
                continue

            if opacity == -1:
                glEnable(GL_LIGHTING)

            continue
        return objects_drawn

    draw_sorted = staticmethod(draw_sorted)

    pass # End of class ColorSorter.

# end
