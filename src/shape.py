"""Handle the freehand curves for selection and cookie-cutting"""

from Numeric import array, zeros, logical_or

from VQT import *
from OpenGL.GL import glNewList, glEndList, glCallList, glGenLists
from OpenGL.GL import GL_COMPILE_AND_EXECUTE

from drawer import drawsphere,  drawline


color = [0.22, 0.35, 0.18, 1.0]

diDEFAULT = -1
diINVISIBLE = 0
diLINES = 1
diCPK = 2
diVDW = 3

def fill(mat,p,dir):
    """ Fill a curve drawn in matrix mat in 1's on 0's with 1's.
    p is V(i,j) of a point to fill from. dir is 1 or -1 for the
    standard recursive fill algorithm
    """
    if mat[p]: return
    up = dn = 0
    o1 = array([1,0])
    od = array([0, dir])
    while not mat[p-od]: p -= od
    while not mat[p]:
        mat[p] = 1
        if mat[p-o1]:
            if up:
                fill(mat, p-[1,dir], -dir)
                up = 0
        else: up = 1
        if mat[p+o1]:
            if dn:
                fill(mat, p+[1,-dir], -dir)
                dn = 0
        else: dn = 1
        p += od
    fill(mat, p-od+o1, -dir)
    fill(mat, p-od-o1, -dir)

class curve:
    """Represents a single closed curve in 3-space, projected to a
    specified plane.
    """
    def __init__(self, ptlist, point, normal):
        """ptlist is a list of 3d points describing a selection.
        point is the center of view, and normal gives the direction
        of the line of light. Form a structure for telling whether
        arbitrary points fall inside the curve from the point of view.
        """
        # establish a plane thru point normal to normal
        # its axes are (3-vectors) x and y
        x = norm(ptlist[0]-point)
        y = norm(cross(normal, x))
        # project the (3d) path onto the plane
#        pt2d = map(lambda p: V(dot(p-point, x), dot(p-point, y)), ptlist)
        pt2d = map(lambda p: V(dot(p, x), dot(p, y)), ptlist)
        # 2d bounding box
        bboxhi = reduce(maximum,pt2d)
        bboxlo = reduce(minimum,pt2d)
        # again in integer (scaled 8 to the angstrom)
        ibbhi = array(map(int,ceil(8*bboxhi)+2))
        ibblo = array(map(int,floor(8*bboxlo)-2))
        # draw the curve in these matrices and fill it
        mat = zeros(ibbhi-ibblo)
        mat1 = zeros(ibbhi-ibblo)
        mat1[0,:] = 1
        mat1[-1,:] = 1
        mat1[:,0] = 1
        mat1[:,-1] = 1
        pt0 = pt2d[0]
        for pt in pt2d[1:]:
            l=ceil(vlen(pt-pt0)*8)
            if l<0.01: continue
            v=(pt-pt0)/l
            for i in range(1+int(l)):
                ij=2+array(map(int,floor((pt0+v*i-bboxlo)*8)))
                mat[ij]=1
            pt0 = pt
        mat1 += mat
        fill(mat1,array([1,1]),1)
        mat1 -= mat

        # line of sight
        self.normal = norm(normal)
        # axes of the plane
        self.x = x
        self.y = y
        # only used for debugging
        self.z = self.normal*dot(point,self.normal)
        # boolean raster of filled-in shape
        self.matrix = mat1
        # where matrix[0,0] is in x,y space
        self.matbase = ibblo
        # bounding rectangle
        self.bboxhi = bboxhi
        self.bboxlo = bboxlo
        # 2-d points of the curve
        self.points=ptlist
        # origin to which x and y are relative
        self.org = point+0.0
        # cookie front and back, measured along normal
        self.thick = V(-5.0, 5.0)

    def xdraw(self):
        """draw the actual grid of the matrix in 3-space.
        Used for debugging only.
        """
        col=(0.0,0.0,0.0)
        dx = self.x/8.0
        dy = self.y/8.0
        for i in range(self.matrix.shape[0]):
            for j in range(self.matrix.shape[1]):
                if not self.matrix[i,j]:
                    p= (V(i,j)+self.matbase)/8.0
                    p=p[0]*self.x + p[1]*self.y + self.z
                    drawline(col,p,col,p+dx+dy)
                    drawline(col,p+dx,col,p+dy)

    def draw(self):
        """Draw two projections of the curve at the limits of the
        thickness that defines the cookie volume.
        The commented code is for debugging.
        """
        if self.clockwise: col = (0.0,0.0,1.0)
        else: col=(1.0,0.0,0.0)
        xp0=self.normal*self.thick[0]
        xp1=self.normal*self.thick[1]
        pl = zip(self.points[:-1],self.points[1:])
        for p in pl:
            drawline(col,p[0]+xp0,col,p[1]+xp0)
            drawline(col,p[0]+xp1,col,p[1]+xp1)
#        w = (1.0,1.0,1.0)
#        drawline(w,self.org,w,self.org+self.z)
#        drawline(w,self.org,w,self.org+10*self.x)
#        drawline(w,self.org,w,self.org+10*self.y)

    def isin(self, pt, ignthic=0):
        """Project pt onto the curve's plane and return 1 if it falls
        inside the curve. if ignthic is 1, it can be any distance from the
        plane; otherwise it must lie within the bounds of self.thick.
        """
        k = dot(self.org - pt, self.normal)
        if not (ignthic or self.thick[0] < k < self.thick[1]): return 0
        p2 = V(dot(pt, self.x), dot(pt, self.y))
        if logical_or.accumulate(less(p2,self.bboxlo)): return 0
        if logical_or.accumulate(greater(p2,self.bboxhi)): return 0
        ij = map(int,p2*8)-self.matbase
        return not self.matrix[ij]

class shape:
    """Represents a sequence of curves, each of which may be
    additive or subtractive.
    """
    def __init__(self, ptlist, point, normal, angle):
        """A shape is a set of curves defining the whole cutout.
        Args define the first curve (see curve) and the total angle
        of the curve telling whether it adds or removes material.
        """
        self.curves = []
        self.center=V(0,0,0)
        self.bboxhi=V(-100,-100,-100)
        self.bboxlo=V(100,100,100)
        self.picked=[]
        # for caching the display as a GL call list
        self.displist = glGenLists(1)
        self.havelist = 0
        self.pickline(ptlist, point, normal, angle)

    def pickline(self, ptlist, point, normal, angle):
        """Add a new curve to the shape.
        """
        self.havelist = 0
        c = curve(ptlist, point, normal)
        c.clockwise = angle < 0
        self.curves += [c]
        for p in ptlist:
            self.bboxhi = maximum(self.bboxhi,
                                  p + normal*c.thick[1])
            self.bboxlo = minimum(self.bboxlo,
                                  p + normal*c.thick[0])

    def isin(self, pt):
        """returns 1 if pt is in any clockwise curve drawn later than
        the last counterclockwise curve it is in.
        """
        val = 0
        for c in self.curves:
            if c.clockwise: val = val or c.isin(pt)
            else: val = val and not c.isin(pt,1)
        return val

    def draw(self,win):
        """Draw the shape. win, not used, is for consistency among
        drawing functions (and may be used if drawing logic gets
        more sophisticated.

        Find  binding box for the curve and check the position each
        carbon atom in a diamond lattice would occupy for being 'in'
        the shape.  Spheres representing the atoms thus selected are
        saved as a GL call list for fast drawing.
        
        """
        global color
        if not self.curves: return
        for c in self.curves: c.draw()
        if self.havelist:
            glCallList(self.displist)
            return
        glNewList(self.displist, GL_COMPILE_AND_EXECUTE)
        sp=1.7586
        sp2 = sp * 0.5
        lo = floor(self.bboxlo / sp)
        ilo = map(int, lo)
        ioff = (sum(ilo)+1) % 2
        lo = sp * lo
        ihi = map(int, ceil(self.bboxhi / sp))
        for i in range(ilo[0], ihi[0]+1):
            for j in range(ilo[1], ihi[1]+1):
                for k in range(ilo[2], ihi[2]+1):
                    if (i+j+k+ioff)%2:
                        abc=V(i,j,k)*sp
                        if self.isin(abc):
                            drawsphere(color, abc, 0.7, 2)
                        if self.isin(abc+sp2):
                            drawsphere(color, abc+sp2, 0.7, 2)
        glEndList()
        self.havelist = 1

    def select(self, assy):
        """Loop thru all the atoms that are visible and select any
        that are 'in' the shape, ignoring the thickness parameter.
        """
        assy.unpickparts()
        c=self.curves[0]
        if c.clockwise:
            for mol in assy.molecules:
                if mol.display == diINVISIBLE: continue
                for a in mol.atoms.itervalues():
                    if a.display == diINVISIBLE: continue
                    if c.isin(a.posn(),1): a.pick()
        else:
            for a in assy.selatoms.values():
                if c.isin(a.posn(),1): a.unpick()


    def undo(self):
        """This would work for shapes, if anyone called it.
        """
        if self.curves: self.curves = self.curves[:-1]
        self.havelist = 0

    def drawlines(self,win):
        pass

    def drawvdw(self, win):
        pass

    def drawbns(self, win):
        pass

    def drawpick(self, win):
        pass

    def __str__(self):
        return "<Shape at " + `self.center` + ">"
