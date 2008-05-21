# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
gl_buffers.py - OpenGL data buffer objects.

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

# Vertex Buffer Object (VBO) and Index Buffer Object (IBO) support.
# For docs see http://www.opengl.org/sdk/docs/man/xhtml/glBufferData.xml .

# Notice that the ARB-suffixed versions of the OpenGL calls are used here.
# They're the ones with PyConvert ctypes wrappers, see: (the incomprehensible)
#   http://pyopengl.sourceforge.net/ctypes/pydoc/OpenGL.GL.ARB.vertex_buffer_object.html
# The sources will do you more good.   Also see "Array Handling Routines" here:
#   http://pyopengl.sourceforge.net/documentation/opengl_diffs.html
#
from OpenGL.GL.ARB.vertex_buffer_object import glGenBuffersARB
from OpenGL.GL.ARB.vertex_buffer_object import glDeleteBuffersARB
# Patched versions.
from graphics.drawing.vbo_patch import glBufferDataARB, glBufferSubDataARB

from OpenGL.raw.GL.ARB.vertex_buffer_object import glBindBufferARB # Unwrappered.

class GLBufferObject(object):
    """
    Buffer data in the graphics card's RAM space.

    Useful man pages for glBind, glBufferData, etc. for OpenGL 2.1 are at:
    http://www.opengl.org/sdk/docs/man
    PyOpenGL versions are at:
    http://pyopengl.sourceforge.net/ctypes/pydoc/OpenGL.html

    'target' is GL_ARRAY_BUFFER_ARB for vertex/normal buffers (VBO's), and
    GL_ELEMENT_ARRAY_BUFFER_ARB for index buffers (IBO's.)

    'data' is a numpy.array, with dtype=numpy.<datatype> .

    'usage' is one of the hint constants, like GL_STATIC_DRAW.
    """

    def __init__(self, target, data, usage):
        self.buffer = glGenBuffersARB(1) # Returns a numpy.ndarray for > 1.
        self.target = target

        self.bind()
        self.size = len(data)

        # Push the data over to Graphics card RAM.
        glBufferDataARB(target, data, usage)

        self.unbind()
        return

    def __del__(self):
        """
        Delete a GLBufferObject.  We don't expect that there will be a lot of
        deleting of GLBufferObjects, but don't want them to sit on a lot of graphics
        card RAM if we did.
        """

        # Since may be too late to clean up buffer objects through the Graphics
        # Context while exiting, we trust that OpenGL or the device driver will
        # deallocate the graphics card RAM when the Python process exits.
        try:
            glDeleteBuffersARB(1, [self.buffer])
        except:
            ##print "Exception in glDeleteBuffersARB."
            pass
        return

    def bind(self):
        """
        Have to bind a particular buffer to its target to fill or draw from it.
        Don't forget to unbind() it!
        """
        glBindBufferARB(self.target, self.buffer)
        return

    def unbind(self):
        """
        Unbind a buffer object from its target after use.
        Failure to do this can kill Python on some graphics platforms!
        """
        glBindBufferARB(self.target, 0)
        return

    pass # End of class GLBufferObject.
