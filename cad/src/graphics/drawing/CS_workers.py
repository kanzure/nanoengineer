# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
CS_workers.py - Drawing functions for primitives drawn by the ColorSorter.

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
from graphics.drawing.drawers import renderSurface

try:
    from OpenGL.GLE import glePolyCone
except:
    print "GLE module can't be imported. Now trying _GLE"
    from OpenGL._GLE import glePolyCone

try:
    from OpenGL.GL import glScale
except:
    # The installed version of OpenGL requires argument-typed glScale calls.
    from OpenGL.GL import glScalef as glScale

from OpenGL.GL import glScalef
    # Note: this is NOT redundant with the above import of glScale --
    # without it, displaying an ESP Image gives a NameError traceback
    # and doesn't work. [Fixed by bruce 070703; bug caught by Eric M using
    # PyChecker; bug introduced sometime after A9.1 went out.]

### Substitute this for drawsphere_worker to test drawing a lot of spheres.
def drawsphere_worker_loop(params):
    (pos, radius, detailLevel) = params
    for x in range(100): ## 500
        for y in range(100):
            newpos = pos + (x+x/10+x/100) * V(1, 0, 0) + (y+y/10+y/100) * V(0, 1, 0)
            drawsphere_worker((newpos, radius, detailLevel))
            continue
        continue
    return

def drawsphere_worker(params):
    """Draw a sphere.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see below)"""

    (pos, radius, detailLevel) = params

    vboLevel = drawing_globals.use_drawing_variant

    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)

    if vboLevel is 0:
        glCallList(drawing_globals.sphereList[detailLevel])
    else:                               # Array variants.
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        size = len(drawing_globals.sphereArrays[detailLevel])
        GLIndexType = drawing_globals.sphereGLIndexTypes[detailLevel]

        if vboLevel is 1:               # DrawArrays from CPU RAM.
            verts = drawing_globals.sphereCArrays[detailLevel]
            glVertexPointer(3, GL_FLOAT, 0, verts)
            glNormalPointer(GL_FLOAT, 0, verts)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, size)

        elif vboLevel is 2:             # DrawElements from CPU RAM.
            verts = drawing_globals.sphereCElements[detailLevel][1]
            glVertexPointer(3, GL_FLOAT, 0, verts)
            glNormalPointer(GL_FLOAT, 0, verts)
            # Can't use the C index in sphereCElements yet, fatal PyOpenGL bug.
            index = drawing_globals.sphereElements[detailLevel][0]
            glDrawElements(GL_TRIANGLE_STRIP, size, GLIndexType, index)

        elif vboLevel is 3:             # DrawArrays from graphics RAM VBO.
            vbo = drawing_globals.sphereArrayVBOs[detailLevel]
            vbo.bind()
            glVertexPointer(3, GL_FLOAT, 0, None)
            glNormalPointer(GL_FLOAT, 0, None)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, vbo.size)
            vbo.unbind()

        elif vboLevel is 4: # DrawElements from index in CPU RAM, verts in VBO.
            vbo = drawing_globals.sphereElementVBOs[detailLevel][1]
            vbo.bind()              # Vertex and normal data comes from the vbo.
            glVertexPointer(3, GL_FLOAT, 0, None)
            glNormalPointer(GL_FLOAT, 0, None)
            # Can't use the C index in sphereCElements yet, fatal PyOpenGL bug.
            index = drawing_globals.sphereElements[detailLevel][0]
            glDrawElements(GL_TRIANGLE_STRIP, size, GLIndexType, index)
            vbo.unbind()

        elif vboLevel is 5: # VBO/IBO buffered DrawElements from graphics RAM.
            (ibo, vbo) = drawing_globals.sphereElementVBOs[detailLevel]
            vbo.bind()              # Vertex and normal data comes from the vbo.
            glVertexPointer(3, GL_FLOAT, 0, None)
            glNormalPointer(GL_FLOAT, 0, None)
            ibo.bind()              # Index data comes from the ibo.
            glDrawElements(GL_TRIANGLE_STRIP, size, GLIndexType, None)
            vbo.unbind()
            ibo.unbind()
            pass

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        pass

    glPopMatrix()
    return

def drawwiresphere_worker(params):
    """
    Draw a wireframe sphere.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see below)
    """

    (color, pos, radius, detailLevel) = params
    ## assert detailLevel == 1 # true, but leave out for speed
    from utilities.debug_prefs import debug_pref, Choice_boolean_True
    newway = debug_pref("new wirespheres?", Choice_boolean_True) #bruce 060415 experiment, re iMac G4 wiresphere bug; fixes it!
    oldway = not newway
    # These objects want a constant line color even if they are selected or highlighted.
    glColor3fv(color)
    glDisable(GL_LIGHTING)
    if oldway:
        glPolygonMode(GL_FRONT, GL_LINE)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    if oldway:
        glCallList(drawing_globals.sphereList[detailLevel])
    else:
        glCallList(drawing_globals.wiresphere1list)
    glEnable(GL_LIGHTING)
    glPopMatrix()
    if oldway:
        glPolygonMode(GL_FRONT, GL_FILL)
    return

def drawcylinder_worker(params):
    """
    Draw a cylinder.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see below)

    WARNING: our circular cross-section is approximated by a 13-gon
    whose alignment around the axis is chosen arbitrary, in a way
    which depends on the direction of the axis; negating the axis usually
    causes a different alignment of that 13-gon. This effect can cause
    visual bugs when drawing one cylinder over an identical or slightly
    smaller one (e.g. when highlighting a bond), unless the axes are kept
    parallel as opposed to antiparallel.
    """

    (pos1, pos2, radius, capped) = params

    glPushMatrix()
    vec = pos2-pos1
    axis = norm(vec)
    glTranslatef(pos1[0], pos1[1], pos1[2])

    ##Huaicai 1/17/05: To avoid rotate around (0, 0, 0), which causes 
    ## display problem on some platforms
    angle = -acos(axis[2])*180.0/pi
    if (axis[2]*axis[2] >= 1.0):
        glRotate(angle, 0.0, 1.0, 0.0)
    else:
        glRotate(angle, axis[1], -axis[0], 0.0)

    glScale(radius,radius,Numeric.dot(vec,vec)**.5)
    glCallList(drawing_globals.CylList)
    if capped: glCallList(drawing_globals.CapList)

    glPopMatrix()

    return

def drawpolycone_worker(params):
    """
    Draw a polycone.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see below)
    """
    (pos_array, rad_array) = params
    glePolyCone(pos_array, None, rad_array)
    return

def drawpolycone_multicolor_worker(params):
    """
    Draw a polycone.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see below)
    piotr 080311: this variant accepts a color array as an additional parameter
    """
    (pos_array, color_array, rad_array) = params
    glEnable(GL_COLOR_MATERIAL) # have to enable GL_COLOR_MATERIAL for
                                # the GLE function
    glPushAttrib(GL_CURRENT_BIT) # store current attributes in case glePolyCone
                                    # modifies the (e.g. current color)
                                    # piotr 080411
    glePolyCone(pos_array, color_array, rad_array)
    glPopAttrib() # This fixes the 'disappearing cylinder' bug
                    # glPopAttrib doesn't take any arguments
                    # piotr 080415
    glDisable(GL_COLOR_MATERIAL)    
    return

def drawsurface_worker(params):
    """Draw a surface.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see below)"""

    (pos, radius, tm, nm) = params
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    renderSurface(tm, nm)
    glPopMatrix()
    return

def drawline_worker(params):
    """
    Draw a line.  Receive parameters through a sequence so that this
    function and its parameters can be passed to another function for
    deferment.  Right now this is only ColorSorter.schedule (see below)
    """
    (endpt1, endpt2, dashEnabled, stipleFactor, width, isSmooth) = params

    ###glDisable(GL_LIGHTING)
    ###glColor3fv(color)
    if dashEnabled: 
        glLineStipple(stipleFactor, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
    if width != 1:
        glLineWidth(width)
    if isSmooth:
        glEnable(GL_LINE_SMOOTH)
    glBegin(GL_LINES)
    glVertex(endpt1[0], endpt1[1], endpt1[2])
    glVertex(endpt2[0], endpt2[1], endpt2[2])
    glEnd()
    if isSmooth:
        glDisable(GL_LINE_SMOOTH)
    if width != 1:
        glLineWidth(1.0) # restore default state
    if dashEnabled: 
        glDisable(GL_LINE_STIPPLE)
    ###glEnable(GL_LIGHTING)
    return
