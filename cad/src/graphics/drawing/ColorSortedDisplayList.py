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

TODO:

Change ColorSorter into a normal class with distinct instances.
Give it a stack of instances rather than its current _suspend system.
Refactor some things between ColorSorter and ColorSortedDisplayList
(which needs renaming). [bruce 090220 comment]
"""

from OpenGL.GL import glCallList
from OpenGL.GL import glDeleteLists
from OpenGL.GL import glGenLists

import foundation.env as env

from graphics.drawing.gl_lighting import isPatternedDrawing
from graphics.drawing.gl_lighting import startPatternedDrawing
from graphics.drawing.gl_lighting import endPatternedDrawing

from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import hoverHighlightingColorStyle_prefs_key
from utilities.prefs_constants import HHS_HALO
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import SS_HALO

from utilities.debug import print_compact_traceback

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
    """

    # default values of instance variables
    transformControl = None
    reentrant = False #bruce 090220
    
    def __init__(self, transformControl = None, reentrant = False):
        """
        """
        if reentrant:
            self.reentrant = True # permits reentrant ColorSorter.start
        
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

        if transformControl is not None:
            self.transformControl = transformControl
            # Note: this requires the csdlID to be already set!
            self.transformControl.addCSDL(self)
            pass

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

        # Unregister self from its TransformControl, breaking the Python
        # reference cycle so the CSDL can be reclaimed.
        if self.transformControl is not None:
            try:
                self.transformControl.removeCSDL(self)
                    #bruce 090218 fixed two bugs in this line; untested either way
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

    pass # end of class ColorSortedDisplayList

# end
