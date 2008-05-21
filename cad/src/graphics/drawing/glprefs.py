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

import os
import sys

# the imports from math vs. Numeric are as discovered in existing code
# as of 2007/06/25.  It's not clear why acos is coming from math...
from math import floor, ceil, acos, atan2
import Numeric
from Numeric import sin, cos, sqrt, pi
degreesPerRadian = 180.0 / pi

# russ 080519 No doubt many of the following imports are unused.
# When the dust settles, the unnecessary ones will be removed.
from OpenGL.GL import GL_AMBIENT
from OpenGL.GL import GL_AMBIENT_AND_DIFFUSE
from OpenGL.GL import glAreTexturesResident
from OpenGL.GL import GL_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_BACK
from OpenGL.GL import glBegin
from OpenGL.GL import glBindTexture
from OpenGL.GL import GL_BLEND
from OpenGL.GL import glBlendFunc
from OpenGL.GL import glCallList
from OpenGL.GL import glColor3f
from OpenGL.GL import glColor3fv
from OpenGL.GL import glColor4fv
from OpenGL.GL import GL_COLOR_MATERIAL
from OpenGL.GL import GL_COMPILE
from OpenGL.GL import GL_COMPILE_AND_EXECUTE
from OpenGL.GL import GL_CONSTANT_ATTENUATION
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import GL_CURRENT_BIT
from OpenGL.GL import glDeleteLists
from OpenGL.GL import glDeleteTextures
from OpenGL.GL import glDepthMask
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_DIFFUSE
from OpenGL.GL import glDisable
from OpenGL.GL import glDisableClientState
from OpenGL.GL import glDrawArrays
from OpenGL.GL import glDrawElements
from OpenGL.GL import glDrawElementsub
from OpenGL.GL import glDrawElementsui
from OpenGL.GL import glDrawElementsus
from OpenGL.GL import GL_ELEMENT_ARRAY_BUFFER_ARB
from OpenGL.GL import glEnable
from OpenGL.GL import glEnableClientState
from OpenGL.GL import glEnd
from OpenGL.GL import glEndList
from OpenGL.GL import GL_EXTENSIONS
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_FILL
from OpenGL.GL import glFinish
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FOG
from OpenGL.GL import GL_FOG_COLOR
from OpenGL.GL import GL_FOG_END
from OpenGL.GL import GL_FOG_MODE
from OpenGL.GL import GL_FOG_START
from OpenGL.GL import GL_FRONT
from OpenGL.GL import GL_FRONT_AND_BACK
from OpenGL.GL import glGenLists
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGetString
from OpenGL.GL import GL_LIGHT0
from OpenGL.GL import GL_LIGHT1
from OpenGL.GL import GL_LIGHT2
from OpenGL.GL import glLightf
from OpenGL.GL import glLightfv
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LINE
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_LINE_LOOP
from OpenGL.GL import GL_LINES
from OpenGL.GL import GL_LINE_SMOOTH
from OpenGL.GL import glLineStipple
from OpenGL.GL import GL_LINE_STIPPLE
from OpenGL.GL import GL_LINE_STRIP
from OpenGL.GL import glLineWidth
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import glMaterialf
from OpenGL.GL import glMaterialfv
from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import glNewList
from OpenGL.GL import glNormal3fv
from OpenGL.GL import glNormalPointer
from OpenGL.GL import glNormalPointerf
from OpenGL.GL import GL_NORMAL_ARRAY
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import glPointSize
from OpenGL.GL import GL_POINTS
from OpenGL.GL import GL_POINT_SMOOTH
from OpenGL.GL import GL_POLYGON
from OpenGL.GL import glPolygonMode
from OpenGL.GL import glPopAttrib
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPopName
from OpenGL.GL import GL_POSITION
from OpenGL.GL import glPushAttrib
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPushName
from OpenGL.GL import GL_QUADS
from OpenGL.GL import GL_QUAD_STRIP
from OpenGL.GL import GL_RENDERER
from OpenGL.GL import GL_RGBA
from OpenGL.GL import glRotate
from OpenGL.GL import glRotatef
from OpenGL.GL import GL_SHININESS
from OpenGL.GL import GL_SPECULAR
from OpenGL.GL import GL_SRC_ALPHA
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import glTexCoord2f
from OpenGL.GL import glTexCoord2fv
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import glTranslate
from OpenGL.GL import glTranslatef
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_TRIANGLE_STRIP
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import GL_UNSIGNED_SHORT
from OpenGL.GL import GL_VENDOR
from OpenGL.GL import GL_VERSION
from OpenGL.GL import glVertex
from OpenGL.GL import glVertex2f
from OpenGL.GL import glVertex3f
from OpenGL.GL import glVertex3fv
from OpenGL.GL import GL_VERTEX_ARRAY
from OpenGL.GL import glVertexPointer
from OpenGL.GL import glVertexPointerf

from OpenGL.GLU import gluBuild2DMipmaps

from geometry.VQT import norm, vlen, V, Q, A

from utilities.constants import white, blue, red
from utilities.constants import darkgreen, lightblue
from utilities.constants import DIAMOND_BOND_LENGTH
from utilities.prefs_constants import material_specular_highlights_prefs_key
from utilities.prefs_constants import material_specular_shininess_prefs_key
from utilities.prefs_constants import material_specular_finish_prefs_key
from utilities.prefs_constants import material_specular_brightness_prefs_key

from utilities.debug_prefs import Choice
import utilities.debug as debug # for debug.print_compact_traceback

import graphics.drawing.drawing_globals as drawing_globals
if drawing_globals.quux_module_import_succeeded:
    import quux

#=
import foundation.env as env #bruce 051126

# grantham 20051118; revised by bruce 051126
class glprefs:

    def __init__(self):
##	self.override_material_specular = None
##	    # set to 4-element sequence to override material specular component
##	self.override_shininess = None
##	    # if exists, overrides shininess
##	self.override_light_specular = None
##	    # set to 4-element sequence to override light specular component
        import foundation.preferences as preferences #bruce 051126 KLUGE: make sure env.prefs exists (could use cleanup, but that's not trivial)
        self.update()

    def update(self): #bruce 051126 added this method
        """Update attributes from current drawing-related prefs stored in prefs db cache.
           This should be called at the start of each complete redraw, or whenever the user changes these global prefs values
        (whichever is more convenient).
           (Note: When this is called during redraw, its prefs db accesses (like any others)
        record those prefs as potentially affecting what should be drawn, so that subsequent
        changes to those prefs values cause an automatic gl_update.)
           Using these attributes in drawing code (rather than directly accessing prefs db cache)
        is desirable for efficiency, since direct access to prefs db cache is a bit slow.
        (Our drawing code still does that in other places -- those might also benefit from this system,
         though this will soon be moot when low-level drawing code gets rewritten in C.)
        """
        self.enable_specular_highlights = not not env.prefs[
            material_specular_highlights_prefs_key] # boolean
        if self.enable_specular_highlights:
            self.override_light_specular = None # used in glpane
            # self.specular_shininess: float; shininess exponent for all specular highlights
            self.specular_shininess = float(env.prefs[material_specular_shininess_prefs_key])
            # self.specular_whiteness: float; whiteness for all material specular colors
            self.specular_whiteness = float(env.prefs[material_specular_finish_prefs_key])
            # self.specular_brightness: float; for all material specular colors
            self.specular_brightness = float(env.prefs[material_specular_brightness_prefs_key])
        else:
            self.override_light_specular = (0.0, 0.0, 0.0, 0.0) # used in glpane
            # Set these to reasonable values, though these attributes are presumably never used in this case.
            # Don't access the prefs db in this case, since that would cause UI prefs changes to do unnecessary gl_updates.
            # (If we ever add a scenegraph node which can enable specular highlights but use outside values for these parameters,
            #  then to make it work correctly we'll need to revise this code.)
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
        Return a Python data object summarizing our prefs which affect chunk display lists,
        so that memoized display lists should become invalid (due to changes in this object)
        if and only if this value becomes different.
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
        return res

    pass # end of class glprefs

drawing_globals.glprefs = glprefs()
