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
digrid=[]
n=2
sp=1.7586
sp2=sp/2.0
# note that these are balanced about 0 (range vs. x+sp)
for x in range(-n, n):
    for y in range(-n, n):
        for z in range(-n, n):
            if (x+y+z+1)%2:
                a=x*sp
                b=y*sp
                c=z*sp
                digrid += [((a,b,c), (a+sp2, b+sp2, c+sp2))]
                digrid += [((a+sp2, b+sp2, c+sp2), (a+sp,b+sp,c))]
                digrid += [((a,b+sp,c+sp), (a+sp2, b+sp2, c+sp2))]
                digrid += [((a+sp2, b+sp2, c+sp2), (a+sp,b,c+sp))]

DiGridSp = 2*n*sp

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

def drawsphere(color, pos, radius, detailLevel, picked=0):

    if picked: glPolygonMode(GL_FRONT, GL_LINE)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glScale(radius,radius,radius)
    glCallList(sphereList[detailLevel])

    glPopMatrix()
    if picked: glPolygonMode(GL_FRONT, GL_FILL)

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

def drawline(color1,pos1,color2,pos2):
    glDisable(GL_LIGHTING)
    glColor3fv(color1)
    glBegin(GL_LINES)
    glVertex(pos1[0], pos1[1], pos1[2])
    glColor3fv(color2)
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


def drawgrid(x):
    #draw grid
    glColor3f(0.5, 0.5, 1.0)
    glDisable(GL_LIGHTING)
    x1 = y1 = z1 = -x
    x2 = y2 = z2 = x
    i1 = int(floor((x1+DiGridSp*0.5)/DiGridSp))
    i2 = int(ceil((x2+DiGridSp*0.5)/DiGridSp))
    j1 = int(floor((y1+DiGridSp*0.5)/DiGridSp))
    j2 = int(ceil((y2+DiGridSp*0.5)/DiGridSp))
    k1 = int(floor((z1+DiGridSp*0.5)/DiGridSp))
    k2 = int(ceil((z2+DiGridSp*0.5)/DiGridSp))
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
