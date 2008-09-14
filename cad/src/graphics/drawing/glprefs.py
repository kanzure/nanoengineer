# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
glprefs.py - Attributes from drawing-related prefs stored in the prefs db cache.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

Originated by Josh as drawer.py .

Various developers extended it since then.

Brad G. added ColorSorter features.

At some point Bruce partly cleaned up the use of display lists.

071030 bruce split some functions and globals into draw_grid_lines.py
and removed some obsolete functions.

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
"""

from utilities.prefs_constants import material_specular_highlights_prefs_key
from utilities.prefs_constants import material_specular_shininess_prefs_key
from utilities.prefs_constants import material_specular_finish_prefs_key
from utilities.prefs_constants import material_specular_brightness_prefs_key
from utilities.prefs_constants import selectionColorStyle_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import haloWidth_prefs_key

import graphics.drawing.drawing_globals as drawing_globals
if drawing_globals.quux_module_import_succeeded:
    import quux

import foundation.env as env #bruce 051126

# grantham 20051118; revised by bruce 051126
class glprefs:

    def __init__(self):
        ##  self.override_material_specular = None
        ##     # Set 4-element sequence to override material specular component.
        ##  self.override_shininess = None
        ##     # If exists, overrides shininess.
        ##  self.override_light_specular = None
        ##     # Set to 4-element sequence to override light specular component.

        #bruce 051126 KLUGE: make sure env.prefs exists
        # (could use cleanup, but that's not trivial.)
        import foundation.preferences as preferences
        self.update()

    def update(self): #bruce 051126 added this method
        """
        Update attributes from current drawing-related prefs stored in prefs db
        cache. This should be called at the start of each complete redraw, or
        whenever the user changes these global prefs values (whichever is more
        convenient).

        (Note: When this is called during redraw, its prefs db accesses (like
        any others) record those prefs as potentially affecting what should be
        drawn, so that subsequent changes to those prefs values cause an
        automatic gl_update.)

        Using these attributes in drawing code (rather than directly accessing
        prefs db cache) is desirable for efficiency, since direct access to
        prefs db cache is a bit slow.  (Our drawing code still does that in
        other places -- those might also benefit from this system, though this
        will soon be moot when low-level drawing code gets rewritten in C.)
        """
        self.enable_specular_highlights = not not env.prefs[
            material_specular_highlights_prefs_key] # boolean
        if self.enable_specular_highlights:
            self.override_light_specular = None # used in glpane
            # self.specular_shininess: float; shininess exponent for all
            # specular highlights
            self.specular_shininess = float(
                env.prefs[material_specular_shininess_prefs_key])
            # self.specular_whiteness: float; whiteness for all material
            # specular colors
            self.specular_whiteness = float(
                env.prefs[material_specular_finish_prefs_key])
            # self.specular_brightness: float; for all material specular colors
            self.specular_brightness = float(
                env.prefs[material_specular_brightness_prefs_key])
        else:
            self.override_light_specular = (0.0, 0.0, 0.0, 0.0) # used in glpane
            # Set these to reasonable values, though these attributes are
            # presumably never used in this case.  Don't access the prefs db in
            # this case, since that would cause UI prefs changes to do
            # unnecessary gl_updates.  (If we ever add a scenegraph node which
            # can enable specular highlights but use outside values for these
            # parameters, then to make it work correctly we'll need to revise
            # this code.)
            self.specular_shininess = 20.0
            self.specular_whiteness = 1.0
            self.specular_brightness = 1.0

        drawing_globals.allow_color_sorting = env.prefs.get(
            drawing_globals.allow_color_sorting_prefs_key,
            drawing_globals.allow_color_sorting_default)

        drawing_globals.use_color_sorted_dls = env.prefs.get(
            drawing_globals.use_color_sorted_dls_prefs_key,
            drawing_globals.use_color_sorted_dls_default)

        drawing_globals.use_color_sorted_vbos = env.prefs.get(
            drawing_globals.use_color_sorted_vbos_prefs_key,
            drawing_globals.use_color_sorted_vbos_default)

        drawing_globals.use_sphere_shaders = env.prefs.get(
            drawing_globals.use_sphere_shaders_prefs_key,
            drawing_globals.use_sphere_shaders_default)

        drawing_globals.use_drawing_variant = env.prefs.get(
            drawing_globals.use_drawing_variant_prefs_key,
            drawing_globals.use_drawing_variant_default)

        drawing_globals.use_c_renderer = (
            drawing_globals.quux_module_import_succeeded and
            env.prefs.get(drawing_globals.use_c_renderer_prefs_key,
                          drawing_globals.use_c_renderer_default))

        if drawing_globals.use_c_renderer:
            quux.shapeRendererSetMaterialParameters(self.specular_whiteness,
                                                    self.specular_brightness,
                                                    self.specular_shininess);
        return

    def materialprefs_summary(self): #bruce 051126
        """
        Return a Python data object summarizing our prefs which affect chunk
        display lists, so that memoized display lists should become invalid (due
        to changes in this object) if and only if this value becomes different.
        """
        res = (self.enable_specular_highlights,)
        if self.enable_specular_highlights:
            res = res + ( self.specular_shininess,
                          self.specular_whiteness,
                          self.specular_brightness )

        # grantham 20060314
        res += (drawing_globals.quux_module_import_succeeded and 
                env.prefs.get(drawing_globals.use_c_renderer_prefs_key,
                              drawing_globals.use_c_renderer_default),)

        # grantham 20060314 - Not too sure this next addition is
        # really necessary, but it seems to me that for testing
        # purposes it is important to rebuild display lists if the
        # color sorting pref is changed.
        res += (env.prefs.get(drawing_globals.allow_color_sorting_prefs_key,
                              drawing_globals.allow_color_sorting_default),)
        res += (env.prefs.get(drawing_globals.use_color_sorted_dls_prefs_key,
                              drawing_globals.use_color_sorted_dls_default),)
        res += (env.prefs.get(drawing_globals.use_color_sorted_vbos_prefs_key,
                              drawing_globals.use_color_sorted_vbos_default),)
        res += (env.prefs.get(drawing_globals.use_drawing_variant_prefs_key,
                              drawing_globals.use_drawing_variant_default),)
        res += (env.prefs.get(drawing_globals.use_sphere_shaders_prefs_key,
                              drawing_globals.use_sphere_shaders_default),)

        # russ 080530: Selection style preference controls select_dl contents.
        res += (env.prefs[selectionColorStyle_prefs_key],)
        res += (env.prefs[selectionColor_prefs_key],)
        res += (env.prefs[haloWidth_prefs_key],)

        return res

    pass # end of class glprefs

drawing_globals.glprefs = glprefs()

### TODO: CLEAN UP the assignment above, which is very bad in several ways:
# 1. imports of modules should not be necessary for their side effects on other modules,
#    unless there is a good reason (which there is not in this case).
#    It makes the imports falsely appear unnecessary, and confuses tools which
#    import the module in which the assignment is made (drawing_globals)
#    but not the one which makes the assignment (this one).
# 2. Bugs can be caused by something importing this module and looking for that value
#    before it's been assigned. Revising import orders of other modules in ways
#    that ought not to matter can trigger such bugs.
# 3. a class in one module should have the same name as an instance of it in another module.
#    (Since two globals should not in general have the same name, and this is an especially confusing case of that.)
# [bruce 080913 comment]

# end

