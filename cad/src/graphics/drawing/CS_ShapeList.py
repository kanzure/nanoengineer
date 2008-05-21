# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
CS_ShapeList.py - The C++ ColorSorter's arrays of primitives to draw.

Does some memoization as a speedup.

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

#=

import graphics.drawing.drawing_globals as drawing_globals
if drawing_globals.quux_module_import_succeeded:
    import quux

class ShapeList_inplace:

    """
    Records sphere and cylinder data and invokes it through the native C++
    rendering system.

    This has the benefit over ShapeList that shapes aren't first stored in
    lots of Python lists, and then turned into lots of Numeric arrays.
    Instead, it stores directly in a list of fixed-size Numeric arrays.
    It shows some speedup, but not a lot.  And tons of memory is being
    used.  I'm not sure where. -grantham

    """

    __author__ = "grantham@plunk.org"

    _blocking = 512     # balance between memory zeroing and drawing efficiency

    def __init__(self):

        #
        # Lists of lists, each list containing a Numeric array and the
        # number of objects in that array.  E.g. Each element in
        # sphere is [l, n], where l is array((m, 9), 'f'), n is the
        # number of valid 9 element slices in l that represent
        # spheres, and m is equal to or more than n+1.
        #
        self.spheres = []
        self.cylinders = []

        # If this is true, disallow future adds.
        self.petrified = False


    def draw(self):

        """
        Draw all the objects represented in this shape list.
        """

        for (spheres, count) in self.spheres:
            quux.shapeRendererDrawSpheresIlvd(count, spheres)
        for (cylinders, count) in self.cylinders:
            quux.shapeRendererDrawCylindersIlvd(count, cylinders)


    def add_sphere(self, color4, pos, radius, name = 0):
        """
        Add a sphere to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        if self.petrified:
            raise ValueError, "Tried to add a sphere to a petrified ShapeList_inplace"

        # struct Sphere {
        #     float m_color[4];
        #     float m_nameUInt;
        #     float m_center[3];
        #     float m_radius;
        # };

        if len(self.spheres) == 0 or self.spheres[-1][1] == ShapeList_inplace._blocking:
            # size of struct Sphere in floats is 9
            block = Numeric.zeros((ShapeList_inplace._blocking, 9), 'f')
            self.spheres.append([block, 0])

        (block, count) = self.spheres[-1]

        block[count] = (\
            color4[0], color4[1], color4[2], color4[3],
            float(name),
            pos[0], pos[1], pos[2],
            radius)

        self.spheres[-1][1] += 1


    def add_cylinder(self, color4, pos1, pos2, radius, name = 0, capped=0):
        """
        Add a cylinder to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        if self.petrified:
            raise ValueError, "Tried to add a cylinder to a petrified ShapeList_inplace"

        # struct Cylinder {
        #     float m_color[4];
        #     float m_nameUInt;
        #     float m_cappedBool;
        #     float m_pos1[3];
        #     float m_pos2[3];
        #     float m_radius; 
        # };

        if len(self.cylinders) == 0 or self.cylinders[-1][1] == ShapeList_inplace._blocking:
            # size of struct Cylinder in floats is 13
            block = Numeric.zeros((ShapeList_inplace._blocking, 13), 'f')
            self.cylinders.append([block, 0])

        (block, count) = self.cylinders[-1]

        block[count] = (\
            color4[0], color4[1], color4[2], color4[3],
            float(name),
            float(capped),
            pos1[0], pos1[1], pos1[2],
            pos2[0], pos2[1], pos2[2],
            radius)

        self.cylinders[-1][1] += 1


    def petrify(self):
        """
        Make this object

        Since the last block of shapes might not be full, this
        function copies them to a new block exactly big enough to hold
        the shapes in that block.  The gc has a chance to release the
        old block and reduce memory use.  After this point, shapes
        must not be added to this ShapeList.
        """

        self.petrified = True

        if len(self.spheres) > 0:
            count = self.spheres[-1][1]
            if count < ShapeList_inplace._blocking:
                block = self.spheres[-1][0]
                newblock = Numeric.array(block[0:count], 'f')
                self.spheres[-1][0] = newblock

        if len(self.cylinders) > 0:
            count = self.cylinders[-1][1]
            if count < ShapeList_inplace._blocking:
                block = self.cylinders[-1][0]
                newblock = Numeric.array(block[0:count], 'f')
                self.cylinders[-1][0] = newblock


class ShapeList:

    """
    Records sphere and cylinder data and invokes it through the native C++
    rendering system.

    Probably better to use "ShapeList_inplace".
    """

    __author__ = "grantham@plunk.org"

    def __init__(self):

        self.memoized = False

        self.sphere_colors = []
        self.sphere_radii = []
        self.sphere_centers = []
        self.sphere_names = []

        self.cylinder_colors = []
        self.cylinder_radii = []
        self.cylinder_pos1 = []
        self.cylinder_pos2 = []
        self.cylinder_cappings = []
        self.cylinder_names = []


    def _memoize(self):

        """
        Internal function that creates Numeric arrays from the data stored
        in add_sphere and add-cylinder.
        """

        self.memoized = True

        # GL Names are uint32.  Numeric.array appears to have only
        # int32.  Winging it...

        self.sphere_colors_array = Numeric.array(self.sphere_colors, 'f')
        self.sphere_radii_array = Numeric.array(self.sphere_radii, 'f')
        self.sphere_centers_array = Numeric.array(self.sphere_centers, 'f')
        self.sphere_names_array = Numeric.array(self.sphere_names, 'i')

        self.cylinder_colors_array = Numeric.array(self.cylinder_colors, 'f')
        self.cylinder_radii_array = Numeric.array(self.cylinder_radii, 'f')
        self.cylinder_pos1_array = Numeric.array(self.cylinder_pos1, 'f')
        self.cylinder_pos2_array = Numeric.array(self.cylinder_pos2, 'f')
        self.cylinder_cappings_array = Numeric.array(self.cylinder_cappings, 'f')
        self.cylinder_names_array = Numeric.array(self.cylinder_names, 'i')


    def draw(self):

        """
        Draw all the objects represented in this shape list.
        """

        # ICK - SLOW - Probably no big deal in a display list.

        if len(self.sphere_radii) > 0:
            if not self.memoized:
                self._memoize()
            quux.shapeRendererDrawSpheres(len(self.sphere_radii),
                                          self.sphere_centers_array,
                                          self.sphere_radii_array,
                                          self.sphere_colors_array,
                                          self.sphere_names_array)

        if len(self.cylinder_radii) > 0:
            if not self.memoized:
                self._memoize()
            quux.shapeRendererDrawCylinders(len(self.cylinder_radii),
                                            self.cylinder_pos1_array,
                                            self.cylinder_pos2_array,
                                            self.cylinder_radii_array,
                                            self.cylinder_cappings_array,
                                            self.cylinder_colors_array,
                                            self.cylinder_names_array)


    def add_sphere(self, color4, pos, radius, name = 0):
        """
        Add a sphere to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        self.sphere_colors.append(color4)
        self.sphere_centers.append(list(pos))
        self.sphere_radii.append(radius)
        self.sphere_names.append(name)
        self.memoized = False


    def add_cylinder(self, color4, pos1, pos2, radius, name = 0, capped=0):
        """
        Add a cylinder to this shape list.

        "color4" must have 4 elements.  "name" is the GL selection name.
        """

        self.cylinder_colors.append(color4)
        self.cylinder_radii.append(radius)
        self.cylinder_pos1.append(list(pos1))
        self.cylinder_pos2.append(list(pos2))
        self.cylinder_cappings.append(capped)
        self.cylinder_names.append(name)
        self.memoized = False


    def petrify(self):
        """
        Delete all but the cached Numeric arrays.

        Call this when you're sure you don't have any more shapes to store
        in the shape list and you want to release the python lists of data
        back to the heap.  Additional shapes must not be added to this shape
        list.
        """
        if not self.memoized:
            self._memoize()

        del self.sphere_colors
        del self.sphere_radii
        del self.sphere_centers
        del self.sphere_names

        del self.cylinder_colors
        del self.cylinder_radii
        del self.cylinder_pos1
        del self.cylinder_pos2
        del self.cylinder_cappings
        del self.cylinder_names
