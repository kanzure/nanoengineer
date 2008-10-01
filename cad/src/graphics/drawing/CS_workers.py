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

drawbonds = True # False  ## Debug/test switch.  Never check in a False value.

# the imports from math vs. Numeric are as discovered in existing code
# as of 2007/06/25.  It's not clear why acos is coming from math...
from math import acos
import Numeric
from Numeric import pi

# russ 080519 No doubt many of the following imports are unused.
# When the dust settles, the unnecessary ones will be removed.
from OpenGL.GL import glBegin
from OpenGL.GL import GL_BACK 
from OpenGL.GL import glCallList
from OpenGL.GL import glColor3fv
from OpenGL.GL import GL_COLOR_MATERIAL
from OpenGL.GL import GL_CULL_FACE 
from OpenGL.GL import GL_CURRENT_BIT
from OpenGL.GL import glDisable
from OpenGL.GL import glDisableClientState
from OpenGL.GL import glDrawArrays
from OpenGL.GL import glDrawElements
from OpenGL.GL import glEnable
from OpenGL.GL import glEnableClientState
from OpenGL.GL import glEnd
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_FILL
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRONT
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LIGHT_MODEL_TWO_SIDE
from OpenGL.GL import glLightModelfv
from OpenGL.GL import GL_LINE
from OpenGL.GL import GL_LINES
from OpenGL.GL import GL_LINE_SMOOTH
from OpenGL.GL import glLineStipple
from OpenGL.GL import GL_LINE_STIPPLE
from OpenGL.GL import glLineWidth
from OpenGL.GL import glNormal3fv
from OpenGL.GL import glNormalPointer
from OpenGL.GL import GL_NORMAL_ARRAY
from OpenGL.GL import glPolygonMode
from OpenGL.GL import glPolygonOffset 
from OpenGL.GL import glPopAttrib
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushAttrib
from OpenGL.GL import glPushMatrix
from OpenGL.GL import GL_QUAD_STRIP
from OpenGL.GL import glRotate
from OpenGL.GL import glTranslatef
from OpenGL.GL import GL_TRIANGLE_STRIP
from OpenGL.GL import glVertex
from OpenGL.GL import glVertex3fv
from OpenGL.GL import GL_VERTEX_ARRAY
from OpenGL.GL import glVertexPointer
from OpenGL.GL import GL_TRUE

from geometry.VQT import norm, vlen, V, Q, A

import graphics.drawing.drawing_globals as drawing_globals
from graphics.drawing.drawers import renderSurface
from graphics.drawing.gl_GLE import glePolyCone
from graphics.drawing.gl_Scale import glScale

### Substitute this for drawsphere_worker to test drawing a lot of spheres.
def drawsphere_worker_loop(params):
    (pos, radius, detailLevel, n) = params
    pos += V(-n/2, -n/2, 0)             # Centered on the origin.
    for x in range(n):
        for y in range(n):
            newpos = pos + (x+x/10+x/100) * V(1, 0, 0) + \
                   (y+y/10+y/100) * V(0, 1, 0)
            drawsphere_worker((newpos, radius, detailLevel, 1))
            continue
        continue
    return

def drawsphere_worker(params):
    """
    Draw a sphere.  Receive parameters through a sequence so that this function
    and its parameters can be passed to another function for deferment.  Right
    now this is only ColorSorter.schedule (see below)
    """

    (pos, radius, detailLevel, n) = params

    vboLevel = drawing_globals.use_drawing_variant

    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)

    if vboLevel == 0:  # OpenGL 1.0 - glBegin/glEnd tri-strips vertex-by-vertex.
        glCallList(drawing_globals.sphereList[detailLevel])

    elif vboLevel == 6:  # Russ 080710: OpenGL 1.4/2.0 - GLSL Vert/Frag shaders.
        drawing_globals.sphereShader.use(True)
        glDisable(GL_CULL_FACE)

        # Draw a bounding box through the shader.  A single "billboard" quad
        # (just front face of a box) oriented toward the eye would be faster.
        glCallList(drawing_globals.shaderCubeList)
        
        drawing_globals.sphereShader.use(False)
        glEnable(GL_CULL_FACE)

        pass
    else:                             # OpenGL 1.1/1.5 - Array/VBO/IBO variants.
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        size = len(drawing_globals.sphereArrays[detailLevel])
        GLIndexType = drawing_globals.sphereGLIndexTypes[detailLevel]

        if vboLevel == 1:               # DrawArrays from CPU RAM.
            verts = drawing_globals.sphereCArrays[detailLevel]
            glVertexPointer(3, GL_FLOAT, 0, verts)
            glNormalPointer(GL_FLOAT, 0, verts)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, size)

        elif vboLevel == 2:             # DrawElements from CPU RAM.
            verts = drawing_globals.sphereCElements[detailLevel][1]
            glVertexPointer(3, GL_FLOAT, 0, verts)
            glNormalPointer(GL_FLOAT, 0, verts)
            # Can't use the C index in sphereCElements yet, fatal PyOpenGL bug.
            index = drawing_globals.sphereElements[detailLevel][0]
            glDrawElements(GL_TRIANGLE_STRIP, size, GLIndexType, index)

        elif vboLevel == 3:             # DrawArrays from graphics RAM VBO.
            vbo = drawing_globals.sphereArrayVBOs[detailLevel]
            vbo.bind()
            glVertexPointer(3, GL_FLOAT, 0, None)
            glNormalPointer(GL_FLOAT, 0, None)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, vbo.size)
            vbo.unbind()

        elif vboLevel == 4: # DrawElements from index in CPU RAM, verts in VBO.
            vbo = drawing_globals.sphereElementVBOs[detailLevel][1]
            vbo.bind()              # Vertex and normal data comes from the vbo.
            glVertexPointer(3, GL_FLOAT, 0, None)
            glNormalPointer(GL_FLOAT, 0, None)
            # Can't use the C index in sphereCElements yet, fatal PyOpenGL bug.
            index = drawing_globals.sphereElements[detailLevel][0]
            glDrawElements(GL_TRIANGLE_STRIP, size, GLIndexType, index)
            vbo.unbind()

        elif vboLevel == 5: # VBO/IBO buffered DrawElements from graphics RAM.
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
    #bruce 060415 experiment, re iMac G4 wiresphere bug; fixes it!
    newway = debug_pref("new wirespheres?", Choice_boolean_True)
    oldway = not newway
    # These objects want a constant line color even if they are selected or
    # highlighted.
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

    @warning: our circular cross-section is approximated by a 13-gon
    whose alignment around the axis is chosen arbitrary, in a way
    which depends on the direction of the axis; negating the axis usually
    causes a different alignment of that 13-gon. This effect can cause
    visual bugs when drawing one cylinder over an identical or slightly
    smaller one (e.g. when highlighting a bond), unless the axes are kept
    parallel as opposed to antiparallel.
    """
    if not drawbonds:
        return

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
    if not drawbonds:
        return
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
    # Note: See the code in class ColorSorter for GL_COLOR_MATERIAL objects.
    
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

def drawtriangle_strip_worker(params):
    """ 
    Draw a triangle strip using a list of triangle vertices
    and (optional) normals.
    """
    # Note: See the code in class ColorSorter for GL_COLOR_MATERIAL objects.
    
    # piotr 080904 - This method could be optimized by using vertex
    # arrays or VBOs.
    
    (triangles, normals, colors) = params

    # It needs to support two-sided triangles, therefore we disable
    # culling and enable two-sided lighting. These settings have to be 
    # turned back to default setting.
    
    glDisable(GL_CULL_FACE)
    glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

    # Use color material mode if colors are present.
    
    if colors:
        glEnable(GL_COLOR_MATERIAL)

    glBegin(GL_TRIANGLE_STRIP)
    if normals:
        if colors:
            for p in range(len(triangles)):
                n = normals[p]
                v = triangles[p]
                c = colors[p]
                glNormal3fv(n)
                glColor3fv(c[:3])
                glVertex3fv(v)
        else:
            for p in range(len(triangles)):
                n = normals[p]
                v = triangles[p]
                glNormal3fv(n)
                glVertex3fv(v)
    else:
        for v in triangles:
            glVertex3fv(v)
    glEnd()

    if colors:
        glDisable(GL_COLOR_MATERIAL)

    # piotr 080904 - are these settings really default?

    glEnable(GL_CULL_FACE)
    glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)

    return

