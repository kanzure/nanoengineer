# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
drawers.py - Miscellaneous drawing functions that are not used as primitives.

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

Originated by Josh as drawer.py

Various developers extended it since then.

At some point Bruce partly cleaned up the use of display lists.

071030 bruce split some functions and globals into draw_grid_lines.py
and removed some obsolete functions.

080519 russ pulled the globals into a drawing_globals module and broke drawer.py
into 10 smaller chunks: glprefs.py setup_draw.py shape_vertices.py
ColorSorter.py CS_workers.py c_renderer.py CS_draw_primitives.py drawers.py
gl_lighting.py gl_buffers.py
"""

# the imports from math vs. Numeric are as discovered in existing code
# as of 2007/06/25.  It's not clear why acos is coming from math...
from math import floor, ceil, acos
import numpy
from numpy import pi

import foundation.env as env

from OpenGL.GL import GL_BACK
from OpenGL.GL import glBegin
from OpenGL.GL import GL_BLEND
from OpenGL.GL import glBlendFunc
from OpenGL.GL import glCallList
from OpenGL.GL import glColor3f
from OpenGL.GL import glColor3fv
from OpenGL.GL import glColor4fv
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import glDepthMask
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import glDisable
from OpenGL.GL import glDisableClientState
from OpenGL.GL import glDrawElements
from OpenGL.GL import glEnable
from OpenGL.GL import glEnableClientState
from OpenGL.GL import glEnd
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_FILL
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRONT
from OpenGL.GL import GL_FRONT_AND_BACK
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LINE
from OpenGL.GL import GL_LINE_LOOP
from OpenGL.GL import GL_LINES
from OpenGL.GL import glLineStipple
from OpenGL.GL import GL_LINE_STIPPLE
from OpenGL.GL import GL_LINE_STRIP
from OpenGL.GL import glLineWidth
from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import glNormal3fv
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import glPointSize
from OpenGL.GL import GL_POINTS
from OpenGL.GL import GL_POINT_SMOOTH
from OpenGL.GL import GL_POLYGON
from OpenGL.GL import glPolygonMode
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix
from OpenGL.GL import GL_QUADS
from OpenGL.GL import glRotate
from OpenGL.GL import glRotatef
from OpenGL.GL import GL_SRC_ALPHA
from OpenGL.GL import glTexCoord2fv
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import glTranslate
from OpenGL.GL import glTranslatef
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import glVertex
from OpenGL.GL import glVertex3f
from OpenGL.GL import glVertex3fv
from OpenGL.GL import GL_VERTEX_ARRAY
from OpenGL.GL import glVertexPointer
from OpenGL.GL import GL_COLOR_MATERIAL
from OpenGL.GL import GL_TRIANGLE_STRIP
from OpenGL.GL import glTexEnvf
from OpenGL.GL import GL_TEXTURE_ENV
from OpenGL.GL import GL_TEXTURE_ENV_MODE
from OpenGL.GL import GL_MODULATE

from OpenGL.GL import glNormalPointer
from OpenGL.GL import glTexCoordPointer
from OpenGL.GL import glDrawArrays


from OpenGL.GL import GL_NORMAL_ARRAY
from OpenGL.GL import GL_TEXTURE_COORD_ARRAY

from geometry.VQT import norm, V, Q, A

from utilities.constants import blue, red, darkgreen, black

from utilities.prefs_constants import originAxisColor_prefs_key
from utilities.prefs_constants import povAxisColor_prefs_key

import graphics.drawing.drawing_globals as drawing_globals
from graphics.drawing.gl_lighting import apply_material
from graphics.drawing.gl_GLE import glePolyCone, gleGetNumSides, gleSetNumSides
from graphics.drawing.gl_Scale import glScale, glScalef

def drawCircle(color, center, radius, normal):
    """
    Scale, rotate/translate the unit circle properly.
    """
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glColor3fv(color)
    glDisable(GL_LIGHTING)

    glTranslatef(center[0], center[1], center[2])
    rQ = Q(V(0, 0, 1), normal)
    rotAngle = rQ.angle*180.0/pi

    #This may cause problems as proved before in Linear motor display.
    #rotation around (0, 0, 0)
    #if vlen(V(rQ.x, rQ.y, rQ.z)) < 0.00005:
    #      rQ.x = 1.0

    glRotatef(rotAngle, rQ.x, rQ.y, rQ.z)
    glScalef(radius, radius, 1.0)
    glCallList(drawing_globals.circleList)
    glEnable(GL_LIGHTING)
    glPopMatrix()
    return

def drawFilledCircle(color, center, radius, normal):
    """
    Scale, rotate/translate the unit circle properly.
    Added a filled circle variant, piotr 080405
    """
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix() 
    glColor3fv(color)
    glDisable(GL_LIGHTING)

    glTranslatef(center[0], center[1], center[2])
    rQ = Q(V(0, 0, 1), normal)
    rotAngle = rQ.angle*180.0/pi

    #This may cause problems as proved before in Linear motor display.
    #rotation around (0, 0, 0)
    #if vlen(V(rQ.x, rQ.y, rQ.z)) < 0.00005:
    #      rQ.x = 1.0

    glRotatef(rotAngle, rQ.x, rQ.y, rQ.z)
    glScalef(radius, radius, 1.0)
    glCallList(drawing_globals.filledCircleList)
    glEnable(GL_LIGHTING)
    glPopMatrix()
    return

def drawLinearArrows(longScale):   
    glCallList(drawing_globals.linearArrowList)
    newPos = drawing_globals.halfHeight*longScale
    glPushMatrix()
    glTranslate(0.0, 0.0, -newPos)
    glCallList(drawing_globals.linearArrowList)
    glPopMatrix()
    glPushMatrix()
    glTranslate(0.0, 0.0, newPos -2.0*drawing_globals.halfEdge)
    glCallList(drawing_globals.linearArrowList)
    glPopMatrix()
    return

def drawLinearSign(color, center, axis, l, h, w):
    """Linear motion sign on the side of squa-linder """
    depthOffset = 0.005
    glPushMatrix()
    glColor3fv(color)
    glDisable(GL_LIGHTING)
    glTranslatef(center[0], center[1], center[2])

    ##Huaicai 1/17/05: To avoid rotate around (0, 0, 0), which causes 
    ## display problem on some platforms
    angle = -acos(axis[2])*180.0/pi
    if (axis[2]*axis[2] >= 1.0):
        glRotate(angle, 0.0, 1.0, 0.0)
    else:
        glRotate(angle, axis[1], -axis[0], 0.0)

    glPushMatrix()
    glTranslate(h/2.0 + depthOffset, 0.0, 0.0)
    glPushMatrix()
    glScale(1.0, 1.0, l)
    glCallList(drawing_globals.linearLineList)
    glPopMatrix()
    if l < 2.6:
        sl = l/2.7
        glScale(1.0, sl, sl)
    if w < 1.0:
        glScale(1.0, w, w)
    drawLinearArrows(l)
    glPopMatrix()

    glPushMatrix()
    glTranslate(-h/2.0 - depthOffset, 0.0, 0.0)
    glRotate(180.0, 0.0, 0.0, 1.0)
    glPushMatrix()
    glScale(1.0, 1.0, l)
    glCallList(drawing_globals.linearLineList)
    glPopMatrix()
    if l < 2.6:
        glScale(1.0, sl, sl)
    if w < 1.0:
        glScale(1.0, w, w)
    drawLinearArrows(l)
    glPopMatrix()

    glPushMatrix()
    glTranslate(0.0, w/2.0 + depthOffset, 0.0)
    glRotate(90.0, 0.0, 0.0, 1.0)
    glPushMatrix()
    glScale(1.0, 1.0, l)
    glCallList(drawing_globals.linearLineList)
    glPopMatrix()
    if l < 2.6:
        glScale(1.0, sl, sl)
    if w < 1.0:
        glScale(1.0, w, w)
    drawLinearArrows(l)
    glPopMatrix()

    glPushMatrix()
    glTranslate(0.0, -w/2.0 - depthOffset, 0.0 )
    glRotate(-90.0, 0.0, 0.0, 1.0)
    glPushMatrix()
    glScale(1.0, 1.0, l)
    glCallList(drawing_globals.linearLineList)
    glPopMatrix()
    if l < 2.6:
        glScale(1.0, sl, sl)
    if w < 1.0:
        glScale(1.0, w, w)
    drawLinearArrows(l)
    glPopMatrix()

    glEnable(GL_LIGHTING)
    glPopMatrix()
    return

def drawRotateSign(color, pos1, pos2, radius, rotation = 0.0):
    """Rotate sign on top of the caps of the cylinder """
    glPushMatrix()
    glColor3fv(color)
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
    glRotate(rotation, 0.0, 0.0, 1.0) #bruce 050518
    glScale(radius,radius,numpy.dot(vec,vec)**.5)

    glLineWidth(2.0)
    glDisable(GL_LIGHTING)
    glCallList(drawing_globals.rotSignList)
    glEnable(GL_LIGHTING)
    glLineWidth(1.0)

    glPopMatrix()
    return

def drawArrowHead(color, 
                  basePoint, 
                  drawingScale, 
                  unitBaseVector, 
                  unitHeightVector):



    arrowBase = drawingScale * 0.08
    arrowHeight = drawingScale * 0.12
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glTranslatef(basePoint[0],basePoint[1],basePoint[2])
    point1 = V(0, 0, 0)
    point1 = point1 + unitHeightVector * arrowHeight    
    point2 = unitBaseVector * arrowBase    
    point3 = - unitBaseVector * arrowBase
    #Draw the arrowheads as filled triangles
    glColor3fv(color)
    glBegin(GL_POLYGON)
    glVertex3fv(point1)
    glVertex3fv(point2)
    glVertex3fv(point3)
    glEnd()    
    glPopMatrix()
    glEnable(GL_LIGHTING)

def drawSineWave(color, startPoint, endPoint, numberOfPoints, phaseAngle):
    """
    Unimplemented.
    """
    pass    

def drawPolyLine(color, points):
    """
    Draws a poly line passing through the given list of points
    """
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINE_STRIP)
    for v in points:
        glVertex3fv(v)
    glEnd()

    glEnable(GL_LIGHTING)
    return

def drawPoint(color, 
              point, 
              pointSize = 3.0,
              isRound = True):
    """
    Draw a point using GL_POINTS. 
    @param point: The x,y,z coordinate array/ vector of the point 
    @type point: A or V
    @param pointSize: The point size to be used by glPointSize
    @type pointSize: float
    @param isRound: If True, the point will be drawn round otherwise square
    @type isRound: boolean
    """
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glPointSize(float(pointSize))
    if isRound:
        glEnable(GL_POINT_SMOOTH)
    glBegin(GL_POINTS)
    glVertex3fv(point)       
    glEnd()
    if isRound:
        glDisable(GL_POINT_SMOOTH)

    glEnable(GL_LIGHTING)
    if pointSize != 1.0:
        glPointSize(1.0)
    return

def drawLineCube(color, pos, radius):
    vtIndices = [0,1,2,3, 0,4,5,1, 5,4,7,6, 6,7,3,2]
    glEnableClientState(GL_VERTEX_ARRAY)
    #bruce 051117 revised this
    glVertexPointer(3, GL_FLOAT, 0, drawing_globals.flatCubeVertices)
        #grantham 20051213 observations, reported/paraphrased by bruce 051215:
        # - should verify PyOpenGL turns Python float (i.e. C double) into C
        #     float for OpenGL's GL_FLOAT array element type.
        # - note that GPUs are optimized for DrawElements types GL_UNSIGNED_INT
        #     and GL_UNSIGNED_SHORT.
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    glDrawElements(GL_LINE_LOOP, 4, GL_UNSIGNED_BYTE, vtIndices)
    #glDrawElements(GL_LINE_LOOP, 4, GL_UNSIGNED_BYTE, vtIndices[4])
    #glDrawElements(GL_LINE_LOOP, 4, GL_UNSIGNED_BYTE, vtIndices[8])
    #glDrawElements(GL_LINE_LOOP, 4, GL_UNSIGNED_BYTE, vtIndices[12])
    glPopMatrix()
    glEnable(GL_LIGHTING)
    glDisableClientState(GL_VERTEX_ARRAY)
    return    

def drawwirecube(color, pos, radius, lineWidth = 3.0):
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    if type(radius) == type(1.0):
        glScale(radius,radius,radius)
    else: 
        glScale(radius[0], radius[1], radius[2])
    glLineWidth(lineWidth)
    glCallList(drawing_globals.lineCubeList)
    glLineWidth(1.0) ## restore its state
    glPopMatrix()
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)
    #bruce 050729 to help fix bug 835 or related bugs
    glPolygonMode(GL_BACK, GL_FILL)
    return

def drawwirebox(color, pos, length):
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(length[0], length[1], length[2])
    glCallList(drawing_globals.CubeList)
    glPopMatrix()
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)
    #bruce 050729 to help fix bug 835 or related bugs
    glPolygonMode(GL_BACK, GL_FILL)
    return

def segstart(color):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINES)
    return

def drawsegment(pos1,pos2):
    glVertex3fv(pos1)
    glVertex3fv(pos2)
    return

def segend():
    glEnd()
    glEnable(GL_LIGHTING)
    return

def drawAxis(color, pos1, pos2, width = 2): #Ninad 060907
    """
    Draw chunk or jig axis
    """
    #ninad060907 Note that this is different than draw 
    # I may need this function to draw axis line. see its current implementation
    # in branch "ninad_060908_drawAxis_notAsAPropOfObject"
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glLineStipple(3, 0x1C47) # dash-dot-dash line
    glEnable(GL_LINE_STIPPLE)
    if width != 1:
        glLineWidth(width)
    glBegin(GL_LINES)
    glVertex(pos1[0], pos1[1], pos1[2])
    glVertex(pos2[0], pos2[1], pos2[2])
    glEnd()
    if width != 1:
        glLineWidth(1.0) # restore default state
    glDisable(GL_LINE_STIPPLE)
    glEnable(GL_LIGHTING)
    return

def drawPointOfViewAxes(scale, point):
    """
    Draw point of view (POV) axes.
    """
    color = env.prefs[povAxisColor_prefs_key]
    drawaxes(scale * 0.1, point, color, coloraxes = False, dashEnabled = False)
    
def drawaxes(scale, point, color = black, coloraxes = False, dashEnabled = False):
    """
    Draw axes.

    @note: used for both origin axes and point of view axes.

    @see: drawOriginAsSmallAxis (related code)
    """
    n = scale
    glPushMatrix()
    glTranslate(point[0], point[1], point[2])
    glDisable(GL_LIGHTING)
    
    if dashEnabled:
        #ninad060921 Note that we will only support dotted origin axis 
        #(hidden lines) but not POV axis. (as it could be annoying)
        glLineStipple(5, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
        glDisable(GL_DEPTH_TEST)
    
    glColor3fv(color)
    
    if coloraxes: 
        glColor3fv(red)
        
    glBegin(GL_LINES)
    glVertex( n, 0, 0)
    glVertex(-n, 0, 0)
    
    if coloraxes: 
        glColor3fv(darkgreen)
        
    glVertex(0,  n, 0)
    glVertex(0, -n, 0)
    
    if coloraxes: 
        glColor3fv(blue)
        
    glVertex(0, 0,  n)
    glVertex(0, 0, -n)
    
    glEnd()

    if dashEnabled:
        glDisable(GL_LINE_STIPPLE)
        glEnable(GL_DEPTH_TEST)

    glEnable(GL_LIGHTING)
    glPopMatrix()
    return

def drawOriginAsSmallAxis(scale, origin, dashEnabled = False):
    """
    Draws a small wireframe version of the origin. It is rendered as a 
    3D point at (0, 0, 0) with 3 small axes extending from it in the positive
    X, Y, Z directions.

    @see: drawaxes (related code)
    """
    #Perhaps we should split this method into smaller methods? ninad060920
    #Notes:
    #1. drawing arrowheads implemented on 060918
    #2. ninad060921 Show the origin axes as dotted if behind the mode. 
    #3. ninad060922 The arrow heads are drawn as wireframe cones if behind the
    #   object the arrowhead size is slightly smaller (otherwise some portion of
    #   the the wireframe arrow shows up!
    #4 .Making origin non-zoomable is acheived by replacing hardcoded 'n' with
    #   glpane's scale - ninad060922

    #ninad060922 in future , the following could be user preferences. 
    if (dashEnabled):
        dashShrinkage = 0.9
    else:
        dashShrinkage = 1
    x1, y1, z1 = scale * 0.01, scale * 0.01, scale * 0.01
    xEnd, yEnd, zEnd = scale * 0.04, scale * 0.09, scale * 0.025
    arrowBase = scale * 0.0075 * dashShrinkage
    arrowHeight = scale * 0.035 * dashShrinkage
    lineWidth = 1.0

    glPushMatrix()

    glTranslate(origin[0], origin[1], origin[2])
    glDisable(GL_LIGHTING)
    glLineWidth(lineWidth)

    gleNumSides = gleGetNumSides()
    #Code to show hidden lines of the origin if some model obscures it
    #  ninad060921
    if dashEnabled:
        glLineStipple(2, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
        glDisable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        gleSetNumSides(5)   
    else:   
        gleSetNumSides(10)

    glBegin(GL_LINES)

    color = env.prefs[originAxisColor_prefs_key]
    
    glColor3fv(color)

    #start draw a point at origin . 
    #ninad060922 is thinking about using GL_POINTS here

    glVertex(-x1, 0.0, 0.0)
    glVertex( x1, 0.0, 0.0)
    glVertex(0.0, -y1, 0.0)
    glVertex(0.0,  y1, 0.0)
    glVertex(-x1,  y1,  z1)
    glVertex( x1, -y1, -z1)    
    glVertex(x1,   y1,  z1)
    glVertex(-x1, -y1, -z1)    
    glVertex(x1,   y1, -z1)
    glVertex(-x1, -y1,  z1)    
    glVertex(-x1,  y1, -z1)
    glVertex(x1,  -y1,  z1)   
    #end draw a point at origin 

    #start draw small origin axes

    glColor3fv(color)
    glVertex(xEnd, 0.0, 0.0)
    glVertex( 0.0, 0.0, 0.0)

    glColor3fv(color)
    glVertex(0.0, yEnd, 0.0)
    glVertex(0.0,  0.0, 0.0)

    glColor3fv(color)
    glVertex(0.0, 0.0, zEnd)
    glVertex(0.0, 0.0,  0.0)
    glEnd() #end draw lines
    glLineWidth(1.0)

    # End push matrix for drawing various lines in the origin and axes.
    glPopMatrix()
    
    #start draw solid arrow heads  for  X , Y and Z axes
    glPushMatrix() 
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glTranslatef(xEnd, 0.0, 0.0)
    glRotatef(90, 0.0, 1.0, 0.0)

    glePolyCone([[0, 0, -1],
                 [0, 0, 0],
                 [0, 0, arrowHeight],
                 [0, 0, arrowHeight+1]],
                None,
                [arrowBase, arrowBase, 0, 0])

    glPopMatrix()

    glPushMatrix()
    glColor3fv(color)
    glTranslatef(0.0, yEnd, 0.0)
    glRotatef(-90, 1.0, 0.0, 0.0)

    glePolyCone([[0, 0, -1],
                 [0, 0, 0],
                 [0, 0, arrowHeight],
                 [0, 0, arrowHeight+1]],
                None,
                [arrowBase, arrowBase, 0, 0])

    glPopMatrix()

    glPushMatrix()
    glColor3fv(color)
    glTranslatef(0.0,0.0,zEnd)

    glePolyCone([[0, 0, -1],
                 [0, 0, 0],
                 [0, 0, arrowHeight],
                 [0, 0, arrowHeight+1]],
                None,
                [arrowBase, arrowBase, 0, 0])

    #Disable line stipple and Enable Depth test
    if dashEnabled:
        glLineStipple(1, 0xAAAA)
        glDisable(GL_LINE_STIPPLE)
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    gleSetNumSides(gleNumSides)
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPopMatrix() 
    #end draw solid arrow heads  for  X , Y and Z axes
    return

def findCell(pt, latticeType):
    """
    Return the cell which contains the point <pt>
    """
    if latticeType == 'DIAMOND':
        cellX = cellY = cellZ = drawing_globals.DiGridSp
    elif latticeType == 'LONSDALEITE':
        cellX = drawing_globals.XLen
        cellY = drawing_globals.YLen
        cellZ = drawing_globals.ZLen

    i = int(floor(pt[0]/cellX))
    j = int(floor(pt[1]/cellY))
    k = int(floor(pt[2]/cellZ))

    orig = V(i*cellX, j*cellY, k*cellZ)

    return orig, drawing_globals.sp1

def genDiam(bblo, bbhi, latticeType):
    """
    Generate a list of possible atom positions within the area enclosed by
    (bblo, bbhi).

    <Return>: A list of unit cells
    """
    if latticeType == 'DIAMOND':
        a = 0
        cellX = cellY = cellZ = drawing_globals.DiGridSp
    elif latticeType == 'LONSDALEITE':
        a = 1
        cellX = drawing_globals.XLen
        cellY = drawing_globals.YLen
        cellZ = drawing_globals.ZLen

    allCells = []    
    for i in range(int(floor(bblo[0]/cellX)),
                   int(ceil(bbhi[0]/cellX))):
        for j in range(int(floor(bblo[1]/cellY)),
                       int(ceil(bbhi[1]/cellY))):
            for k in range(int(floor(bblo[2]/cellZ)),
                           int(ceil(bbhi[2]/cellZ))):
                off = V(i*cellX, j*cellY, k*cellZ)
                if a == 0:
                    allCells += [drawing_globals.digrid + off]
                elif a ==1:
                    allCells += [drawing_globals.lonsEdges + off]
    return allCells  


def drawGrid(scale, center, latticeType):
    """
    Construct the grid model and show as position references for cookies.
    The model is build around "pov" and has size of 2*"scale" on each of
    the (x, y, z) directions.

    @note: This should be optimized later. 
    For "scale = 200", it takes about 1479623 loops. ---Huaicai
    """
    glDisable(GL_LIGHTING)

    # bruce 041201:
    #   Quick fix to prevent "hang" from drawing too large a BuildCrystal_Command grid
    # with our current cubic algorithm (bug 8). The constant 120.0 is still on
    # the large side in terms of responsiveness -- on a 1.8GHz iMac G5 it can
    # take many seconds to redraw the largest grid, or to update a selection
    # rectangle during a drag. I also tried 200.0 but that was way too large.
    # Since some users have slower machines, I'll be gentle and put 90.0 here.
    #   Someday we need to fix the alg to be quadratic by teaching this code
    # (and the Crystal builder code too) about the eyespace clipping planes. 
    #   Once we support user prefs, this should be one of them (if the alg is
    # not fixed by then).

    MAX_GRID_SCALE = 90.0
    if scale > MAX_GRID_SCALE:
        scale = MAX_GRID_SCALE

    if latticeType == 'DIAMOND':
        cellX = cellY = cellZ = drawing_globals.DiGridSp
    elif latticeType == 'LONSDALEITE':
        cellX = drawing_globals.XLen
        cellY = drawing_globals.YLen
        cellZ = drawing_globals.ZLen

    bblo = center - scale
    bbhi = center + scale
    i1 = int(floor(bblo[0]/cellX))
    i2 = int(ceil(bbhi[0]/cellX))
    j1 = int(floor(bblo[1]/cellY))
    j2 = int(ceil(bbhi[1]/cellY))
    k1 = int(floor(bblo[2]/cellZ))
    k2 = int(ceil(bbhi[2]/cellZ))
    glPushMatrix()
    glTranslate(i1*cellX,  j1*cellY, k1*cellZ)
    for i in range(i1, i2):
        glPushMatrix()
        for j in range(j1, j2):
            glPushMatrix()
            for k in range(k1, k2):
                if latticeType == 'DIAMOND':
                    glCallList(drawing_globals.diamondGridList)
                else:
                    glCallList(drawing_globals.lonsGridList)
                glTranslate(0.0,  0.0, cellZ)
            glPopMatrix()
            glTranslate(0.0,  cellY, 0.0)
        glPopMatrix()
        glTranslate(cellX, 0.0, 0.0)
    glPopMatrix()
    glEnable(GL_LIGHTING)

    #drawCubeCell(V(1, 0, 0))
    return


def drawrectangle(pt1, pt2, rt, up, color):
    """
    Draws a (hollow) rectangle outline of the given I{color}.

    @param pt1: First corner of the rectangle.
    @type  pt1: Point

    @param pt1: Opposite corner of the rectangle.
    @type  pt1: Point

    @param rt: Right vector of the glpane.
    @type  rt: Unit vector

    @param up: Right vector of the glpane.
    @type  up: Unit vector

    @param color: Color
    @type  color: color
    """
    glColor3f(color[0], color[1], color[2])
    glDisable(GL_LIGHTING)
    c2 = pt1 + rt * numpy.dot(rt, pt2 - pt1)
    c3 = pt1 + up * numpy.dot(up, pt2 - pt1)
    glBegin(GL_LINE_LOOP)
    glVertex(pt1[0], pt1[1], pt1[2])
    glVertex(c2[0], c2[1], c2[2])
    glVertex(pt2[0], pt2[1], pt2[2])
    glVertex(c3[0], c3[1], c3[2])
    glEnd()
    glEnable(GL_LIGHTING)

#bruce & wware 060404: drawRubberBand apparently caused bug 1814 (Zoom Tool
# hanging some Macs, requiring power toggle) so it should not be used until
# debugged. Use drawrectangle instead. (For an example of how to translate
# between them, see ZoomMode.py rev 1.32 vs 1.31 in ViewCVS.) That bug was only
# repeatable on Bruce's & Will's iMacs G5.
#
# Bruce's speculations (not very definite; no evidence for them at all) about
# possible causes of the bug in drawRubberBand:
# - use of glVertex instead of glVertex3f or so??? This seems unlikely, since we
#   have other uses of it, but perhaps they work due to different arg types.
# - use of GL_LINE_LOOP within OpenGL xor mode, and bugs in some OpenGL
#   drivers?? I didn't check whether BuildCrystal_Command does this too.
##def drawRubberBand(pt1, pt2, c2, c3, color):
##    """Huaicai: depth test should be disabled to make the xor work """
##    glBegin(GL_LINE_LOOP)
##    glVertex(pt1[0],pt1[1],pt1[2])
##    glVertex(c2[0],c2[1],c2[2])
##    glVertex(pt2[0],pt2[1],pt2[2])
##    glVertex(c3[0],c3[1],c3[2])
##    glEnd()
##    return

# Wrote drawbrick for the Linear Motor.  Mark [2004-10-10]
def drawbrick(color, center, axis, l, h, w, opacity = 1.0):

    if len(color) == 3:
        color = (color[0], color[1], color[2], opacity)

    if opacity != 1.0:	
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  


    apply_material(color)
    glPushMatrix()
    glTranslatef(center[0], center[1], center[2])

    ##Huaicai 1/17/05: To avoid rotate around (0, 0, 0), which causes 
    ## display problem on some platforms
    angle = -acos(axis[2])*180.0/pi
    if (axis[2]*axis[2] >= 1.0):
        glRotate(angle, 0.0, 1.0, 0.0)
    else:
        glRotate(angle, axis[1], -axis[0], 0.0)



    glScale(h, w, l)
    #bruce 060302 revised the contents of solidCubeList while fixing bug 1595
    glCallList(drawing_globals.solidCubeList)

    if opacity != 1.0:	
        glDisable(GL_BLEND)
        glDepthMask(GL_TRUE)

    glPopMatrix()
    return

def drawLineLoop(color,lines, width = 1):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glLineWidth(width)
    glBegin(GL_LINE_LOOP)
    for v in lines:
        glVertex3fv(v)
    glEnd()
    glEnable(GL_LIGHTING)  
    #reset the glLineWidth to 1
    if width!=1:
        glLineWidth(1)
    return


def drawlinelist(color,lines):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINES)
    for v in lines:
        glVertex3fv(v)
    glEnd()
    glEnable(GL_LIGHTING)
    return

cubeLines = A([[-1,-1,-1], [-1,-1, 1],
               [-1, 1,-1], [-1, 1, 1],
               [ 1,-1,-1], [ 1,-1, 1],
               [ 1, 1,-1], [ 1, 1, 1],

               [-1,-1,-1], [-1, 1,-1],
               [-1,-1, 1], [-1, 1, 1],
               [ 1,-1,-1], [ 1, 1,-1],
               [ 1,-1, 1], [ 1, 1, 1],

               [-1,-1,-1], [ 1,-1,-1],
               [-1,-1, 1], [ 1,-1, 1],
               [-1, 1,-1], [ 1, 1,-1],
               [-1, 1, 1], [ 1, 1, 1]])

def drawCubeCell(color):
    sp0 = drawing_globals.sp0
    sp4 = drawing_globals.sp4
    vs = [[sp0, sp0, sp0], [sp4, sp0, sp0], [sp4, sp4, sp0], [sp0, sp4, sp0],
          [sp0, sp0, sp4], [sp4, sp0, sp4], [sp4, sp4, sp4], [sp0, sp4, sp4]]

    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINE_LOOP)
    for ii in range(4):
        glVertex3fv(vs[ii])
    glEnd()

    glBegin(GL_LINE_LOOP)
    for ii in range(4, 8):
        glVertex3fv(vs[ii])
    glEnd()

    glBegin(GL_LINES)
    for ii in range(4):
        glVertex3fv(vs[ii])
        glVertex3fv(vs[ii+4])
    glEnd()

    glEnable(GL_LIGHTING) 
    return

def drawPlane(color, w, h, textureReady, opacity,
              SOLID = False, pickCheckOnly = False, tex_coords = None):
    """
    Draw polygon with size of <w>*<h> and with color <color>. Optionally, it
    could be texuture mapped, translucent.

    @pickCheckOnly This is used to draw the geometry only, used for OpenGL pick
      selection purpose.

    @param tex_coords: texture coordinates to be explicitly provided (for 
    simple image transformation purposes)
    """
    vs = [[-0.5, 0.5, 0.0], [-0.5, -0.5, 0.0],
          [0.5, -0.5, 0.0], [0.5, 0.5, 0.0]]
    
    # piotr 080529: use external texture coordinates if provided
    if tex_coords is None:
        vt = [[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]    
    else:
        vt = tex_coords
    
    if textureReady:
        opacity = 1.0
            
    glDisable(GL_LIGHTING)
    glColor4fv(list(color) + [opacity])

    glPushMatrix()
    glScalef(w, h, 1.0)

    if SOLID:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glDisable(GL_CULL_FACE) 
    
    if not pickCheckOnly:
        # This makes sure a translucent object will not occlude another
        # translucent object.
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if textureReady:
            glEnable(GL_TEXTURE_2D)  

    glBegin(GL_QUADS)
    for ii in range(len(vs)):
        t = vt[ii]
        v = vs[ii]
        if textureReady:
            glTexCoord2fv(t)
        glVertex3fv(v)
    glEnd()

    if not pickCheckOnly:
        if textureReady:
            glDisable(GL_TEXTURE_2D)

        glDisable(GL_BLEND)
        glDepthMask(GL_TRUE) 

    glEnable(GL_CULL_FACE)
    if not SOLID:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glPopMatrix()
    glEnable(GL_LIGHTING)
    return


def drawHeightfield(color, w, h, textureReady, opacity,
                    SOLID = False, pickCheckOnly = False, hf = None):
    """
    Draw a heighfield using vertex and normal arrays. Optionally, it could be
    texture mapped.

    @pickCheckOnly This is used to draw the geometry only, used for OpenGL pick
      selection purpose.
    """        

    if not hf:
        # Return if heightfield is not provided
        return
    
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)

    # Don't use opacity, otherwise the heighfield polygons should be sorted
    # - something to implement later...
    ## glColor3v(list(color))
    
    if textureReady:
        # For texturing, use white color (to be modulated by the texture)
        glColor3f(1,1,1)
    else:
        glColor3fv(list(color))
        
    glPushMatrix()
    glScalef(w, h, 1.0)

    if SOLID:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    
    glDisable(GL_CULL_FACE) 
    
    if not pickCheckOnly:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if textureReady:
            glEnable(GL_TEXTURE_2D)  
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    for tstrip_vert, tstrip_norm, tstrip_tex in hf:
        glVertexPointer(3, GL_FLOAT, 0, tstrip_vert)
        glNormalPointer(GL_FLOAT, 0, tstrip_norm)
        glTexCoordPointer(2, GL_FLOAT, 0, tstrip_tex)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, len(tstrip_vert))
        
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    glDisable(GL_COLOR_MATERIAL)
    
    if not pickCheckOnly:
        if textureReady:
            glDisable(GL_TEXTURE_2D)

        glDepthMask(GL_TRUE) 

    glEnable(GL_CULL_FACE)
    if not SOLID:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glPopMatrix()
    glEnable(GL_LIGHTING)
    
    return

def drawFullWindow(vtColors):
    """
    Draw gradient background color.

    <vtColors> is a 4 element list specifying colors for the  
       left-down, right-down, right-up, left-up window corners.

    To draw the full window, the modelview and projection should be set in
    identity.
    """
    from utilities.constants import GL_FAR_Z
    glDisable(GL_LIGHTING)

    glBegin(GL_QUADS)
    glColor3fv(vtColors[0])
    glVertex3f(-1, -1, GL_FAR_Z)
    glColor3fv(vtColors[1])            
    glVertex3f(1, -1, GL_FAR_Z)
    glColor3fv(vtColors[2])
    glVertex3f(1, 1, GL_FAR_Z)
    glColor3fv(vtColors[3])
    glVertex3f(-1, 1, GL_FAR_Z)
    glEnd()

    glEnable(GL_LIGHTING)
    return

def drawtext(text, color, origin, point_size, glpane):
    """
    """
    # see also: _old_code_for_drawing_text()

    if not text:
        return

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    from PyQt4.Qt import QFont, QString ##, QColor
    font = QFont( QString("Helvetica"), point_size)
    #glpane.qglColor(QColor(75, 75, 75))
    from widgets.widget_helpers import RGBf_to_QColor
    glpane.qglColor(RGBf_to_QColor(color))
    glpane.renderText(origin[0], origin[1], origin[2], QString(text), font)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    return

### obsolete code:
### The following code used to be for drawing text on a QGLWidget --
### some of it might still be useful if integrated into drawtext() above
### [moved here from elementColors.py and slightly cleaned up by bruce 080223]
##def _old_code_for_drawing_text(glpane):
##    self = glpane
##    glDisable(GL_LIGHTING)
##    glDisable(GL_DEPTH_TEST) 
##    self.qglColor(QColor(0, 0, 0))
##    font = QFont( QString("Times"), 10)
##    text = QString('Rvdw = ' + str(self.rad))
##    fontMecs = QFontMetrics(font)
##    strWd = fontMecs.width(text)
##    strHt = fontMecs.height()
##    w = self.width/2 - strWd/2
##    h = self.height - strHt/2 
##    self.renderText(w, h, text, font)
##    glEnable(GL_DEPTH_TEST)
##    glEnable(GL_LIGHTING)        

def renderSurface(surfaceEntities, surfaceNormals):
    ####@@@@ bruce 060927 comments:
    # - The color needs to come before the vertex. I fixed that, but left a
    #   debug_pref that can change it so you can see the effect of that bug
    #   before it was fixed. (Same for the normal, but it already did come
    #   before.)
    # - I suspect normals are not used (when nc > 0) due to lighting being
    #   off. But if it's on, colors are not used.  I saw that problem before,
    #   and we had to use apply_material instead, to set color; I'm not sure
    #   why, it might just be due to specific OpenGL settings we make for other
    #   purposes. So I'll use drawer.apply_material(color) (again with a debug
    #   pref to control that).
    # The effect of the default debug_pref settings is that it now works
    # properly with color -- but only for the 2nd chunk, if you create two, and
    # not at all if you create only one. I don't know why it doesn't work for
    # the first chunk.
    (entityIndex, surfacePoints, surfaceColors) = surfaceEntities
    e0 = entityIndex[0]
    n = len(e0)
    nc = len(surfaceColors)
    if 1:
        ### bruce 060927 debug code; when done debugging, we can change them to
        ### constants & simplify the code that uses them.
        from utilities.debug_prefs import debug_pref, Choice_boolean_True
        from utilities.debug_prefs import Choice_boolean_False
        disable_lighting = debug_pref("surface: disable lighting?",
                                      Choice_boolean_False)
        if nc:
            color_first = debug_pref("surface: color before vertex?",
                                     Choice_boolean_True)
            use_apply_material = debug_pref("surface: use apply_material?",
                                            Choice_boolean_True)

    ## old code was equivalent to disable_lighting = (nc > 0)
    #bruce 060927 Split this out, so we can change how we apply color in a
    #  single place in the code.
    def use_color(color):
        if use_apply_material:
            # This makes the colors visible even when lighting is enabled.
            apply_material(color)
        else:
            # Old code did this. These colors are only visible when lighting is
            # not enabled.
            glColor3fv(color)
            pass
        return

    #bruce 060927 Split this out, for code clarity, and so debug prefs are
    #  used in only one place.
    def onevert(vertex_index):
        glNormal3fv(surfaceNormals[vertex_index])
        # This needs to be done before glVertex3fv.
        if nc > 0 and color_first:
            use_color(surfaceColors[vertex_index])
        glVertex3fv(surfacePoints[vertex_index])
        # Old code did it here -- used wrong colors sometimes.
        if nc > 0 and not color_first:
            use_color(surfaceColors[vertex_index])
            pass
        return
    ## if nc > 0 :
    ##     glDisable(GL_LIGHTING)
    if disable_lighting:
        glDisable(GL_LIGHTING)
    if n == 3:
        glBegin(GL_TRIANGLES)
        for entity in entityIndex:
            onevert(entity[0])
            onevert(entity[1])
            onevert(entity[2])
        glEnd()
    else:	
        glBegin(GL_QUADS)
        for entity in entityIndex:
            onevert(entity[0])
            onevert(entity[1])
            onevert(entity[2])
            onevert(entity[3])
        glEnd()
    if disable_lighting:
        glEnable(GL_LIGHTING)
    return

# end
