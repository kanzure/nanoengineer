from OpenGL.GL import *
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
#        /    \          /----\
#       /      \  =>    / \  / \
#      /        \      /   \/   \
#      ----------      ----------
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

digrid = A(digrid)

DiGridSp = sp4

sphereList = []
numSphereSizes = 3
CylList = GridList = CapList = CubeList = None

def setup():
    global CylList, GridList, CapList, CubeList
    global sphereList

    listbase = glGenLists(numSphereSizes + 4)

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

    GridList = CapList + 1
    glNewList(GridList, GL_COMPILE)
    glBegin(GL_LINES)
    for p in digrid:
        glVertex(p[0])
        glVertex(p[1])
    glEnd()
    glEndList()

    CubeList = GridList + 1
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

def drawcylinder(color, pos1, pos2, radius, picked=0, capped=0):
    global CylList, CapList
    if picked: glEnable(GL_LIGHT2)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
    glPushMatrix()
    vec = pos2-pos1
    vecn = norm(vec)
    glTranslatef(pos1[0], pos1[1], pos1[2])
    glRotate(-acos(vecn[2])*180.0/pi,vecn[1],-vecn[0], 0.0)
    glScale(radius,radius,vlen(vec))
    glCallList(CylList)
    if capped: glCallList(CapList)
    glPopMatrix()
    if picked: glDisable(GL_LIGHT2)

def drawline(color,pos1,pos2):
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glBegin(GL_LINES)
    glVertex(pos1[0], pos1[1], pos1[2])
    glVertex(pos2[0], pos2[1], pos2[2])
    glEnd()
    glEnable(GL_LIGHTING)

def drawwirecube(color, pos, radius):
    global CubeList
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    glCallList(CubeList)
    glPopMatrix()
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)

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

def drawaxes(n,point):
    glPushMatrix()
    glTranslate(point[0], point[1], point[2])
    glDisable(GL_LIGHTING)
    glColor3f(0.0, 0.0, 0.6)
    glBegin(GL_LINES)
    glVertex(n,0,0)
    glVertex(-n,0,0)
    glVertex(0,n,0)
    glVertex(0,-n,0)
    glVertex(0,0,n)
    glVertex(0,0,-n)
    glEnd()
    glEnable(GL_LIGHTING)
    glPopMatrix()

def genDiam(bblo, bbhi):
    for i in range(int(floor(bblo[0]/DiGridSp)),
                   int(ceil(bbhi[0]/DiGridSp))):
        for j in range(int(floor(bblo[1]/DiGridSp)),
                       int(ceil(bbhi[1]/DiGridSp))):
            for k in range(int(floor(bblo[2]/DiGridSp)),
                           int(ceil(bbhi[2]/DiGridSp))):
                off = V(i*DiGridSp, j*DiGridSp, k*DiGridSp)
                for p in digrid:
                    yield p[0]+off, p[1]+off
    yield None

def drawgrid(scale, center):
    
    #draw grid
    glDisable(GL_LIGHTING)

    bblo = center-scale
    bbhi = center + scale
    i1 = int(floor(bblo[0]/DiGridSp))
    i2 = int(ceil(bbhi[0]/DiGridSp))
    j1 = int(floor(bblo[1]/DiGridSp))
    j2 = int(ceil(bbhi[1]/DiGridSp))
    k1 = int(floor(bblo[2]/DiGridSp))
    k2 = int(ceil(bbhi[2]/DiGridSp))
    glPushMatrix()
    glTranslate(i1*DiGridSp,  j1*DiGridSp, k1*DiGridSp)
    for i in range(i1, i2):
        glPushMatrix()
        for j in range(j1, j2):
            glPushMatrix()
            for k in range(k1, k2):
                glCallList(GridList)
                glTranslate(0.0,  0.0, DiGridSp)
            glPopMatrix()
            glTranslate(0.0,  DiGridSp, 0.0)
        glPopMatrix()
        glTranslate(DiGridSp, 0.0, 0.0)
    glPopMatrix()
    glEnable(GL_LIGHTING)


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
    
def drawbrick(pos, len, q, color):
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glPushMatrix()
    glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(len[0], len[1], len[2])
    glCallList(CubeList)
    glPopMatrix()
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glPolygonMode(GL_FRONT, GL_FILL)
    
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

               
