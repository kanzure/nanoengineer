# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
drawer.py

OpenGL drawing utilities.

$Id$
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GLUT as glut
import math
from VQT import *

# the golden ratio
phi=(1.0+sqrt(5.0))/2.0
vert=norm(V(phi,0,1))
a=vert[0]
b=vert[1]
c=vert[2]

# vertices of an icosahedron

icosa = ((-a,b,c), (b,c,-a), (b,c,a), (a,b,-c), (-c,-a,b), (-c,a,b),
         (b,-c,a), (c,a,b), (b,-c,-a), (a,b,c), (c,-a,b), (-a,b,-c))

icosix = ((9, 2, 6), (1, 11, 5), (11, 1, 8), (0, 11, 4), (3, 1, 7),
          (3, 8, 1), (9, 3, 7), (0, 6, 2), (4, 10, 6), (1, 5, 7),
          (7, 5, 2), (8, 3, 10), (4, 11, 8), (9, 7, 2), (10, 9, 6),
          (0, 5, 11), (0, 2, 5), (8, 10, 4), (3, 9, 10), (6, 0, 4))

# generate geodesic spheres by subdividing the faces of an icosahedron
# recursively:
#          /\              /\
#         /  \            /  \
#        /    \          /____\
#       /      \   =>   /\    /\
#      /        \      /  \  /  \
#     /__________\    /____\/____\
#
# and normalizing the resulting vectors to the surface of a sphere

def subdivide(tri,deep):
    if deep:
        a=tri[0]
        b=tri[1]
        c=tri[2]
        a1=norm(A(tri[0]))
        b1=norm(A(tri[1]))
        c1=norm(A(tri[2]))
        d=tuple(norm(a1+b1))
        e=tuple(norm(b1+c1))
        f=tuple(norm(c1+a1))
        return subdivide((a,d,f), deep-1) + subdivide((d,e,f), deep-1) +\
               subdivide((d,b,e), deep-1) + subdivide((f,e,c), deep-1)
    else: return [tri]

## Get the specific detail level of triangles approximation of a sphere 
def getSphereTriangles(level):
        ocdec=[]
        for i in icosix:
            ocdec+=subdivide((icosa[i[0]],icosa[i[1]],icosa[i[2]]),level)
        return ocdec

# generate two circles in space as 13-gons,
# one rotated half a segment with respect to the other
# these are used as cylender ends
slices=13
circ1=map((lambda n: n*2.0*pi/slices), range(slices+1))
circ2=map((lambda a: a+pi/slices), circ1)
drum0=map((lambda a: (cos(a), sin(a), 0.0)), circ1)
drum1=map((lambda a: (cos(a), sin(a), 1.0)), circ2)
drum1n=map((lambda a: (cos(a), sin(a), 0.0)), circ2)

circle=zip(drum0[:-1],drum0[1:],drum1[:-1]) +\
       zip(drum1[:-1],drum0[1:],drum1[1:])
circlen=zip(drum0[:-1],drum0[1:],drum1n[:-1]) +\
        zip(drum1n[:-1],drum0[1:],drum1n[1:])

cap0n=(0.0, 0.0, -1.0)
cap1n=(0.0, 0.0, 1.0)
drum0.reverse()

###data structure to construct the rotation sign for rotary motor
numSeg = 20
rotS = map((lambda n: pi/2+n*2.0*pi/numSeg), range(numSeg*3/4 + 1))
zOffset = 0.005; scaleS = 0.4
rotS0n = map((lambda a: (scaleS*cos(a), scaleS*sin(a), 0.0 - zOffset)), rotS)
rotS1n = map((lambda a: (scaleS*cos(a), scaleS*sin(a), 1.0 + zOffset)), rotS)
halfEdge = 3.0 * scaleS * sin(pi/numSeg)
arrow0Vertices = [(rotS0n[-1][0]-halfEdge, rotS0n[-1][1], rotS0n[-1][2]), 
                            (rotS0n[-1][0]+halfEdge, rotS0n[-1][1], rotS0n[-1][2]), 
                            (rotS0n[-1][0], rotS0n[-1][1] + 2.0*halfEdge, rotS0n[-1][2])] 
arrow0Vertices.reverse()                            
arrow1Vertices = [(rotS1n[-1][0]-halfEdge, rotS1n[-1][1], rotS1n[-1][2]), 
                            (rotS1n[-1][0]+halfEdge, rotS1n[-1][1], rotS1n[-1][2]), 
                            (rotS1n[-1][0], rotS1n[-1][1] + 2.0*halfEdge, rotS1n[-1][2])]                             

###Linear motor arrow sign data structure
halfEdge = 1.0/3.0 ##1.0/8.0
linearArrowVertices = [(0.0, -halfEdge, 0.0), (0.0, halfEdge, 0.0), (0.0, 0.0,2*halfEdge)]

# a chunk of diamond grid, to be tiled out in 3d

sp0 = 0.0
sp1=1.52/sqrt(3.0)
sp2=2.0*sp1
sp3=3.0*sp1
sp4=4.0*sp1

digrid=[[[sp0, sp0, sp0], [sp1, sp1, sp1]], [[sp1, sp1, sp1], [sp2, sp2, sp0]],
        [[sp2, sp2, sp0], [sp3, sp3, sp1]], [[sp3, sp3, sp1], [sp4, sp4, sp0]],
        [[sp2, sp0, sp2], [sp3, sp1, sp3]], [[sp3, sp1, sp3], [sp4, sp2, sp2]],
        [[sp2, sp0, sp2], [sp1, sp1, sp1]], [[sp1, sp1, sp1], [sp0, sp2, sp2]],
        [[sp0, sp2, sp2], [sp1, sp3, sp3]], [[sp1, sp3, sp3], [sp2, sp4, sp2]],
        [[sp2, sp4, sp2], [sp3, sp3, sp1]], [[sp3, sp3, sp1], [sp4, sp2, sp2]],
        [[sp4, sp0, sp4], [sp3, sp1, sp3]], [[sp3, sp1, sp3], [sp2, sp2, sp4]],
        [[sp2, sp2, sp4], [sp1, sp3, sp3]], [[sp1, sp3, sp3], [sp0, sp4, sp4]]]
        
cubeVertices = [[-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, -1.0], [-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [1.0, -1.0, 1.0], [1.0, -1.0, -1.0]]
sq3 = sqrt(3.0)/3.0
cubeNormals = [[-sq3, sq3, -sq3], [-sq3, sq3, sq3], [sq3, sq3, sq3], [sq3, sq3, -sq3], [-sq3, -sq3, -sq3], [-sq3, -sq3, sq3], [sq3, -sq3, sq3], [sq3, -sq3, -sq3]]
cubeIndices = [[0, 1, 2, 3], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [0, 3, 7, 4], [4, 7, 6, 5]]        

digrid = A(digrid)

DiGridSp = sp4

sphereList = []
numSphereSizes = 3
CylList = diamondGridList = CapList = CubeList = solidCubeList = lineCubeList = None
rotSignList = linearLineList = linearArrowList = circleList = lonsGridList = None

halfHeight = 0.45

##Some variable used by the Lonsdaleite lattice construction
ux = 1.262; uy = 0.729; dz = 0.5153; ul = 1.544
XLen = 2*ux
YLen = 6*uy
ZLen = 2*(ul + dz)
lonsEdges = None

def _makeLonsCell():
    """Data structure to construct a Lonsdaleite lattice cell"""
    lVp = [# 2 outward vertices
          [-ux, -2*uy, 0.0], [0.0, uy, 0.0],
          # Layer 1: 7 vertices
          [ux, -2*uy, ul],      [-ux, -2*uy, ul],     [0.0, uy, ul], 
          [ux, 2*uy, ul+dz], [-ux, 2*uy, ul+dz], [0.0, -uy, ul+dz],
                                     [-ux, 4*uy, ul],
          # Layer 2: 7 vertices
          [ux, -2*uy, 2*(ul+dz)], [-ux, -2*uy, 2*(ul+dz)], [0.0, uy, 2*(ul+dz)],
          [ux, 2*uy, 2*ul+dz],    [-ux, 2*uy, 2*ul+dz],     [0.0, -uy, 2*ul+dz],
                                           [-ux, 4*uy, 2*(ul+dz)]
         ]

    lonsEdges = [ # 2 outward vertical edges for layer 1
                      [lVp[0], lVp[3]], [lVp[1], lVp[4]],
                      #  6 xy Edges for layer 1
                      [lVp[2], lVp[7]], [lVp[3], lVp[7]], [lVp[7], lVp[4]],
                      [lVp[4], lVp[6]], [lVp[4], lVp[5]],
                      [lVp[6], lVp[8]],        
                      #  2 outward vertical edges for layer 2
                      [lVp[14], lVp[7]],  [lVp[13], lVp[6]], 
                      # 6 xy Edges for layer 2
                      [lVp[14], lVp[9]], [lVp[14], lVp[10]], [lVp[14], lVp[11]],
                      [lVp[11], lVp[13]], [lVp[11], lVp[12]],
                      [lVp[13], lVp[15]]
                    ]
                     
    return lonsEdges 

#Some variables for Graphite lattice
gUx = 1.228; gUy = 0.709; gZLen = 1.674
gXLen = 2*gUx; gYLen = 4*gUy

def _makeGraphiteCell(zIndex):
    """Data structure to construct a Graphite lattice cell"""
    gVp = [[-gUx, -gUy, 0.0],   [0.0, 0.0, 0.0],        [gUx, -gUy, 0.0],
              [-gUx, 3*gUy, 0.0], [0.0, 2*gUy, 0.0],  [gUx, 3*gUy, 0.0],
              [gUx, 5*gUy, 0.0]
         ]

    grpEdges = [ 
                      [gVp[0], gVp[1]], [gVp[1], lVp[2]],
                      ##Not finished yet. We need double bond to do this??
                    ]
                     
    return lonsEdges 



def setup():
    global CylList, diamondGridList, CapList, CubeList, solidCubeList
    global sphereList, rotSignList, linearLineList, linearArrowList
    global circleList, lonsGridList, lonsEdges, lineCubeList

    listbase = glGenLists(numSphereSizes + 19)

    for i in range(numSphereSizes):
        sphereList += [listbase+i]
        glNewList(sphereList[i], GL_COMPILE)
        glBegin(GL_TRIANGLES)
        ocdec = getSphereTriangles(i)
        for tri in ocdec:
            glNormal3fv(tri[0])
            glVertex3fv(tri[0])
            glNormal3fv(tri[1])
            glVertex3fv(tri[1])
            glNormal3fv(tri[2])
            glVertex3fv(tri[2])
        glEnd()
        glEndList()


    CylList = listbase+numSphereSizes
    glNewList(CylList, GL_COMPILE)
    glBegin(GL_TRIANGLES)
    for i in range(len(circle)):
        glNormal3fv(circlen[i][0])
        glVertex3fv(circle[i][0])
        glNormal3fv(circlen[i][1])
        glVertex3fv(circle[i][1])
        glNormal3fv(circlen[i][2])
        glVertex3fv(circle[i][2])
    glEnd()
    glEndList()

    CapList = CylList + 1
    glNewList(CapList, GL_COMPILE)
    glNormal3fv(cap0n)
    glBegin(GL_POLYGON)
    for p in drum0:
        glVertex3fv(p)
    glEnd()
    glNormal3fv(cap1n)
    glBegin(GL_POLYGON)
    for p in drum1:
        glVertex3fv(p)
    glEnd()
    glEndList()

    diamondGridList = CapList + 1
    glNewList(diamondGridList, GL_COMPILE)
    glBegin(GL_LINES)
    for p in digrid:
        glVertex(p[0])
        glVertex(p[1])
    glEnd()
    glEndList()
    
    lonsGridList = diamondGridList + 1
    lonsEdges = _makeLonsCell()
    glNewList(lonsGridList, GL_COMPILE)
    glBegin(GL_LINES)
    for p in lonsEdges:
        glVertex(p[0])
        glVertex(p[1])
    glEnd()
    glEndList()

    CubeList = lonsGridList + 1
    glNewList(CubeList, GL_COMPILE)
    glBegin(GL_QUAD_STRIP)
    glVertex((-1,-1,-1))
    glVertex(( 1,-1,-1))
    glVertex((-1, 1,-1))
    glVertex(( 1, 1,-1))
    glVertex((-1, 1, 1))
    glVertex(( 1, 1, 1))
    glVertex((-1,-1, 1))
    glVertex(( 1,-1, 1))
    glVertex((-1,-1,-1))
    glVertex(( 1,-1,-1))
    glEnd()
    glEndList()
    
    solidCubeList = CubeList + 1
    glNewList(solidCubeList, GL_COMPILE)
    glBegin(GL_QUADS)
    for i in xrange(len(cubeIndices)):
        for j in xrange(4) :    
                nTuple = tuple(cubeNormals[cubeIndices[i][j]])
                vTuple = tuple(cubeVertices[cubeIndices[i][j]])
                glNormal3fv(nTuple)
                glVertex3fv(vTuple)
    glEnd()
    glEndList()                

    rotSignList = solidCubeList + 1
    glNewList(rotSignList, GL_COMPILE)
    glBegin(GL_LINE_STRIP)
    for ii in xrange(len(rotS0n)):
            glVertex3fv(tuple(rotS0n[ii]))
    glEnd()
    glBegin(GL_LINE_STRIP)
    for ii in xrange(len(rotS1n)):
            glVertex3fv(tuple(rotS1n[ii]))
    glEnd()
    glBegin(GL_TRIANGLES)
    for v in arrow0Vertices + arrow1Vertices:
        glVertex3f(v[0], v[1], v[2])
    glEnd()
    glEndList()

    linearArrowList = rotSignList + 1
    glNewList(linearArrowList, GL_COMPILE)
    glBegin(GL_TRIANGLES)
    for v in linearArrowVertices:
        glVertex3f(v[0], v[1], v[2])
    glEnd()
    glEndList()

    linearLineList = linearArrowList + 1
    glNewList(linearLineList, GL_COMPILE)
    glEnable(GL_LINE_SMOOTH)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, -halfHeight)
    glVertex3f(0.0, 0.0, halfHeight)
    glEnd()
    glDisable(GL_LINE_SMOOTH)
    glEndList()
    
    circleList = linearLineList + 1 #glGenLists(1)
    glNewList(circleList, GL_COMPILE)
    glBegin(GL_LINE_LOOP)
    for ii in range(60):
        x = cos(ii*2.0*pi/60)
        y = sin(ii*2.0*pi/60)
        glVertex3f(x, y, 0.0)
    glEnd()    
    glEndList()
    
    cvIndices = [0,1, 2,3, 4,5, 6,7, 0,3, 1,2, 5,6, 4,7, 0,4, 1,5, 2,6, 3,7]
    lineCubeList = circleList + 1
    glNewList(lineCubeList, GL_COMPILE)
    glBegin(GL_LINES)
    for i in cvIndices:
        glVertex3fv(tuple(cubeVertices[i]))
    glEnd()    
    glEndList()
    
    
def drawCircle(color, center, radius, normal):
    """Scale, rotate/translate the unit circle properly """
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
    glCallList(circleList)
    glEnable(GL_LIGHTING)
    glPopMatrix()
            

def drawLinearArrows(longScale):   
    glCallList(linearArrowList)
    newPos = halfHeight*longScale
    glPushMatrix()
    glTranslate(0.0, 0.0, -newPos)
    glCallList(linearArrowList)
    glPopMatrix()
    glPushMatrix()
    glTranslate(0.0, 0.0, newPos -2.0*halfEdge)
    glCallList(linearArrowList)
    glPopMatrix()


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
        glCallList(linearLineList)
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
        glCallList(linearLineList)
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
        glCallList(linearLineList)
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
        glCallList(linearLineList)
        glPopMatrix()
        if l < 2.6:
            glScale(1.0, sl, sl)
        if w < 1.0:
            glScale(1.0, w, w)
        drawLinearArrows(l)
        glPopMatrix()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
        

        
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
        glScale(radius,radius,vlen(vec))
        
        glLineWidth(2.0)
        glDisable(GL_LIGHTING)
        glCallList(rotSignList)
        glEnable(GL_LIGHTING)
        glLineWidth(1.0)
        
        glPopMatrix()
        

def drawsphere(color, pos, radius, detailLevel):
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    glCallList(sphereList[detailLevel])

    glPopMatrix()


def drawwiresphere(color, pos, radius, detailLevel=1):
    glColor3fv(color)
    glDisable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_LINE)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    glCallList(sphereList[detailLevel])
    glEnable(GL_LIGHTING)
    glPopMatrix()
    glPolygonMode(GL_FRONT, GL_FILL)

def drawcylinder(color, pos1, pos2, radius, capped=0):
    global CylList, CapList
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
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
  
    glScale(radius,radius,vlen(vec))
    glCallList(CylList)
    if capped: glCallList(CapList)
    glPopMatrix()

def drawline(color, pos1, pos2, dashEnabled = False, width = 1):
    """Draw a line from pos1 to pos2 of the given color.
    If dashEnabled is True, it will be dashed.
    If width is not 1, it should be an int or float (more than 0)
    and the line will have that width, in pixels.
    (Whether the line is antialiased is determined by GL state variables
     which are not set by this code.)
    """
    # WARNING: some callers pass dashEnabled as a positional argument rather than a named argument.
    # [bruce 050831 added docstring, this comment, and the width argument.]
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    if dashEnabled: 
        glLineStipple(1, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
    if width != 1:
        glLineWidth(width)
    glBegin(GL_LINES)
    glVertex(pos1[0], pos1[1], pos1[2])
    glVertex(pos2[0], pos2[1], pos2[2])
    glEnd()
    if width != 1:
        glLineWidth(1.0) # restore default state
    if dashEnabled: 
        glDisable(GL_LINE_STIPPLE)
    glEnable(GL_LIGHTING)

def drawLineCube(color, pos, radius):
    cubeVertices = [-1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, -1.0]
    vtIndices = [0,1,2,3, 0,4,5,1, 5,4,7,6, 6,7,3,2]
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, cubeVertices)
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
    

def drawwirecube(color, pos, radius):
    global CubeList, lineCubeList
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    #glCallList(CubeList)
    glLineWidth(3.0)
    glCallList(lineCubeList)
    glLineWidth(1.0) ## restore its state
    glPopMatrix()
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)
    glPolygonMode(GL_BACK, GL_FILL) #bruce 050729 to help fix bug 835 or related bugs

def drawwirebox(color, pos, len):
    global CubeList
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(len[0], len[1], len[2])
    glCallList(CubeList)
    glPopMatrix()
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)
    glPolygonMode(GL_BACK, GL_FILL) #bruce 050729 to help fix bug 835 or related bugs

def segstart(color):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINES)

def drawsegment(pos1,pos2):
    glVertex3fv(pos1)
    glVertex3fv(pos2)

def segend():
    glEnd()
    glEnable(GL_LIGHTING)

def drawaxes(n,point,coloraxes=False):
    from constants import blue, red, green
    glPushMatrix()
    glTranslate(point[0], point[1], point[2])
    glDisable(GL_LIGHTING)
    if coloraxes: glColor3f(red[0], red[1], red[2])
    else: glColor3f(blue[0], blue[1], blue[2])
    glBegin(GL_LINES)
    glVertex(n,0,0)
    glVertex(-n,0,0)
    glColor3f(blue[0], blue[1], blue[2])
    glVertex(0,n,0)
    glVertex(0,-n,0)
    if coloraxes: glColor3f(green[0], green[1], green[2])
    else: glColor3f(blue[0], blue[1], blue[2])
    glVertex(0,0,n)
    glVertex(0,0,-n)
    glEnd()
    glEnable(GL_LIGHTING)
    glPopMatrix()

def findCell(pt, latticeType):
    """Return the cell which contains the point <pt> """
    if latticeType == 'DIAMOND':
        a = 0; cellX = cellY = cellZ = DiGridSp
    elif latticeType == 'LONSDALEITE':
        a = 1; cellX = XLen; cellY = YLen; cellZ = ZLen
    
    i = int(floor(pt[0]/cellX))
    j = int(floor(pt[1]/cellY))
    k = int(floor(pt[2]/cellZ))
    
    orig = V(i*cellX, j*cellY, k*cellZ)
    
    return orig, sp1
    
def getGridCellPoints(pt, latticeType): 
    grid=A([[sp0, sp0, sp0], [sp1, sp1, sp1], [sp2, sp2, sp0], [sp3, sp3, sp1], 
        [sp4, sp4, sp0], [sp2, sp0, sp2], [sp3, sp1, sp3], [sp4, sp2, sp2],
        [sp0, sp2, sp2], [sp1, sp3, sp3], [sp2, sp4, sp2], [sp4, sp0, sp4], 
        [sp2, sp2, sp4], [sp0, sp4, sp4]])
    
    cubeCorner = [[sp0, sp0, sp0], [sp4, sp0, sp0], [sp4, sp4, sp0], [sp0, sp4, sp0],
                            [sp0, sp0, sp4], [sp4, sp0, sp4], [sp4, sp4, sp4], [sp0, sp4, sp4]]
    
    if latticeType == 'DIAMOND':
        a = 0; cellX = cellY = cellZ = DiGridSp
    elif latticeType == 'LONSDALEITE':
        a = 1; cellX = XLen; cellY = YLen; cellZ = ZLen       
    i = int(floor(pt[0]/cellX))
    j = int(floor(pt[1]/cellY))
    k = int(floor(pt[2]/cellZ))
    
    orig = V(i*cellX, j*cellY, k*cellZ)
    
    return orig + grid 
    
def genDiam(bblo, bbhi, latticeType):
    """Generate a list of possible atom positions within the area enclosed by (bblo, bbhi).
    <Return>: A list of unit cells"""
    if latticeType == 'DIAMOND':
        a = 0; cellX = cellY = cellZ = DiGridSp
    elif latticeType == 'LONSDALEITE':
        a = 1; cellX = XLen; cellY = YLen; cellZ = ZLen
    
    allCells = []    
    for i in range(int(floor(bblo[0]/cellX)),
                   int(ceil(bbhi[0]/cellX))):
        for j in range(int(floor(bblo[1]/cellY)),
                       int(ceil(bbhi[1]/cellY))):
            for k in range(int(floor(bblo[2]/cellZ)),
                           int(ceil(bbhi[2]/cellZ))):
                off = V(i*cellX, j*cellY, k*cellZ)
                if a == 0: allCells += [digrid + off]
                elif a ==1: allCells += [lonsEdges + off]
    return allCells  


def drawGrid(scale, center, latticeType):
    """Construct the grid model and show as position references for cookies. The model is build around "pov" and has size of 2*"scale" on each of the (x, y, z) directions. This should be optimized latter. For "scale = 200", it takes about 1479623 loops. ---Huaicai """
    
    
    glDisable(GL_LIGHTING)

    # bruce 041201:
    #   Quick fix to prevent "hang" from drawing too large a cookieMode grid
    # with our current cubic algorithm (bug 8). The constant 120.0 is still on
    # the large side in terms of responsiveness -- on a 1.8GHz iMac G5 it can
    # take many seconds to redraw the largest grid, or to update a selection
    # rectangle during a drag. I also tried 200.0 but that was way too large.
    # Since some users have slower machines, I'll be gentle and put 90.0 here.
    #   Someday we need to fix the alg to be quadratic by teaching this code
    # (and the cookie baker code too) about the eyespace clipping planes. 
    #   Once we support user prefs, this should be one of them (if the alg is
    # not fixed by then).
    
    MAX_GRID_SCALE = 90.0
    if scale > MAX_GRID_SCALE:
        scale = MAX_GRID_SCALE

    if latticeType == 'DIAMOND':
        cellX = cellY = cellZ = DiGridSp
    elif latticeType == 'LONSDALEITE':
        cellX = XLen; cellY = YLen; cellZ = ZLen
    
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
                    glCallList(diamondGridList)
                 else:
                    glCallList(lonsGridList)
                 glTranslate(0.0,  0.0, cellZ)
            glPopMatrix()
            glTranslate(0.0,  cellY, 0.0)
        glPopMatrix()
        glTranslate(cellX, 0.0, 0.0)
    glPopMatrix()
    glEnable(GL_LIGHTING)
    
    #drawCubeCell(V(1, 0, 0))


def drawrectangle(pt1, pt2, rt, up, color):
    glColor3f(color[0], color[1], color[2])
    glDisable(GL_LIGHTING)
    c2 = pt1 + rt*dot(rt,pt2-pt1)
    c3 = pt1 + up*dot(up,pt2-pt1)
    glBegin(GL_LINE_LOOP)
    glVertex(pt1[0],pt1[1],pt1[2])
    glVertex(c2[0],c2[1],c2[2])
    glVertex(pt2[0],pt2[1],pt2[2])
    glVertex(c3[0],c3[1],c3[2])
    glEnd()
    glEnable(GL_LIGHTING)

def drawRubberBand(pt1, pt2, c2, c3, color):
       """Huaicai: depth test should be disabled to make the xor work """
       glBegin(GL_LINE_LOOP)
       glVertex(pt1[0],pt1[1],pt1[2])
       glVertex(c2[0],c2[1],c2[2])
       glVertex(pt2[0],pt2[1],pt2[2])
       glVertex(c3[0],c3[1],c3[2])
       glEnd()
       

# Wrote drawbrick for the Linear Motor.  Mark [2004-10-10]
def drawbrick(color, center, axis, l, h, w):
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
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
    glut.glutSolidCube(1.0)
    #glCallList(solidCubeList)
    glPopMatrix()

def drawLineLoop(color,lines):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINE_LOOP)
    for v in lines:
        glVertex3fv(v)
    glEnd()
    glEnable(GL_LIGHTING)    
    
def drawlinelist(color,lines):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINES)
    for v in lines:
        glVertex3fv(v)
    glEnd()
    glEnable(GL_LIGHTING)

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

# mat mult by rowvector list and max/min reduce to find extrema
D = sqrt(2.0)/2.0
T = sqrt(3.0)/3.0
#              0  1  2  3   4  5   6  7   8  9  10  11  12
#             13 14 15 16  17 18  19 20  21 22  23  24  25
polyXmat = A([[1, 0, 0, D,  D, D,  D,  0,   0, T,  T,  T,  T],
                       [0, 1, 0, D, -D, 0,   0,  D,  D, T,  T, -T, -T],
                       [0, 0, 1, 0,  0,  D, -D,  D, -D, T, -T,  T, -T]])

polyMat = cat(transpose(polyXmat),transpose(polyXmat))

polyTab = [( 9, (0,7,3), [3,0,5,2,7,1,3]),
           (10, (0,1,4), [3,1,8,15,6,0,3]),
           (11, (8,11,7), [4,14,21,2,5,0,4]),
           (12, (8,4,9), [4,0,6,15,20,14,4]),
           (22, (5,10,9), [18,13,16,14,20,15,18]),
           (23, (10,6,11), [16,13,19,2,21,14,16]),
           (24, (1,2,5), [8,1,17,13,18,15,8]),
           (25, (3,6,2), [7,2,19,13,17,1,7])]

def planepoint(v,i,j,k):
    mat = V(polyMat[i],polyMat[j],polyMat[k])
    vec = V(v[i],v[j],v[k])
    return solve_linear_equations(mat, vec)


def makePolyList(v):
    xlines = [[],[],[],[],[],[],[],[],[],[],[],[]]
    segs = []
    for corner, edges, planes in polyTab:
        linx = []
        for i in range(3):
            l,s,r = planes[2*i:2*i+3]
            e = remainder(i+1,3)
            p1 = planepoint(v,corner,l,r)
            if abs(dot(p1,polyMat[s])) <= abs(v[s]):
                p2 = planepoint(v,l,s,r)
                linx += [p1]
                xlines[edges[i]] += [p2]
                xlines[edges[e]] += [p2]
                segs += [p1,p2]
            else:
                p1 = planepoint(v,corner,l,s)
                p2 = planepoint(v,corner,r,s)
                linx += [p1,p2]
                xlines[edges[i]] += [p1]
                xlines[edges[e]] += [p2]
        e=edges[0]
        xlines[e] = xlines[e][:-2] + [xlines[e][-1],xlines[e][-2]]
        for p1,p2 in zip(linx, linx[1:]+[linx[0]]):
            segs += [p1,p2]

    for lis in xlines:
        segs += [lis[0],lis[3],lis[1],lis[2]]

    assert type(segs) == type([]) #bruce 041119
    return segs

def drawLonsdaleiteGrid(scale, center):
    """This function is obsolete. Call dragGrid() and pass approriate parameter to draw the Lonsdaleite Lattice """
    glDisable(GL_LIGHTING)
    
    bblo = center- scale
    bbhi = center + scale
    i1 =  int(floor(bblo[0]/XLen))
    i2 = int(ceil(bbhi[0]/XLen))
    j1 = int(floor(bblo[1]/YLen))
    j2 = int(ceil(bbhi[1]/YLen))
    k1 = int(floor(bblo[2]/ZLen))
    k2 = int(ceil(bbhi[2]/ZLen))
    glPushMatrix()
    glTranslate(i1*XLen,  j1*YLen, k1*ZLen)
    for i in range(i1, i2):
        glPushMatrix()
        for j in range(j1, j2):
            glPushMatrix()
            for k in range(k1, k2):
                glCallList(lonsGridList)
                glTranslate(0.0,  0.0, ZLen)
            glPopMatrix()
            glTranslate(0.0,  YLen, 0.0)
        glPopMatrix()
        glTranslate(XLen, 0.0, 0.0)
    glPopMatrix()
    glEnable(GL_LIGHTING)        

    
###Huaicai: test function    
def drawDiamondCubic(color):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINES)
    for jj in range(5):
         for kk in range(5):
              glVertex3f(sp0, sp1*jj, sp1*kk)
              glVertex3f(sp4, sp1*jj, sp1*kk)
    
    for jj in range(5):
         for ii in range(5):
              glVertex3f(sp1*ii, sp1*jj, sp0)
              glVertex3f(sp1*ii, sp1*jj, sp4)
    
    for kk in range(5):
         for ii in range(5):
              glVertex3f(sp1*ii, sp0, sp1*kk)
              glVertex3f(sp1*ii, sp4, sp1*kk)
              
    glEnd()
    glEnable(GL_LIGHTING)    

def drawCubeCell(color):
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


def drawPlane(color, w, h):
    '''Draw polygon with size of <w>*<h> and with color <color>. '''
    vs = [[-0.5, 0.5, 0.0], [-0.5, -0.5, 0.0], [0.5, -0.5, 0.0], [0.5, 0.5, 0.0]]
    
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    
    glPushMatrix()
    glScalef(w, h, 1.0)
    
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glDisable(GL_CULL_FACE) 
    
    glBegin(GL_QUADS)
    for v in vs:
        glVertex3fv(v)
    glEnd()
    
    glEnable(GL_CULL_FACE) 
    
    glPopMatrix()
    glEnable(GL_LIGHTING)
    
            
def drawPlaneGrid(color, w, h, uw, uh):
    '''Draw grid lines with <color>, unit size is <uw>*<uh>'''

    if uw > w: uw = w
    if uh > h: uh = h
    
    Z_OFF = 0.001
    
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    
    hw = w/2.0; hh = h/2.0

    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)#_MINUS_SRC_ALPHA)
        
    glBegin(GL_LINES)
    
    #Draw horizontal lines
    y1 = hh
    while y1 >= -hh:
        glVertex3f(-hw, y1, Z_OFF)
        glVertex3f(hw, y1, Z_OFF)
    
        y1 -= uh
        
    #Draw vertical lines    
    x1 = -hw
    while x1 <= hw:        
        glVertex3f(x1, hh, Z_OFF)
        glVertex3f(x1, -hh, Z_OFF)
    
        x1 += uw
            
    glEnd()
    
    glDisable(GL_LINE_SMOOTH)
    glDisable(GL_BLEND)
    
    glEnable(GL_LIGHTING)
    


def drawFullWindow(vtColors):
    """Draw gradient background color.
       <vtColors> is a 4 element list specifying colors for the  
       left-down, right-down, right-up, left-up window corners.
       To draw the full window, the modelview and projection should be set in identity.
       """
    from constants import GL_FAR_Z
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
    
