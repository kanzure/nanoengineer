"""Handle the freehand curves for selection and cookie-cutting"""

from Numeric import array, zeros, logical_or

from VQT import *
from OpenGL.GL import glNewList, glEndList, glCallList, glGenLists
from OpenGL.GL import GL_COMPILE_AND_EXECUTE

from drawer import *
from constants import *

color = [0.22, 0.35, 0.18, 1.0]

def logicColor(logic):
    if logic==0: return orange
    if logic==1: return aqua
    if logic==2: return yellow

class BBox:
    """ implement a bounding box in 3-space
    BBox(PointList)
    BBox(point1, point2)
    BBox(2dpointpair, 3dx&y, slab)
    data is stored hi, lo so we can use subtract.reduce
    """
    def __init__(self, point1=None, point2=None, slab = None):
        if slab:
            # convert from a 2d box and axes

            x=dot(A(point1),A(point2))
            dx = subtract.reduce(x)
            oc=x[1]+V(point2[0]*dot(dx,point2[0]),point2[1]*dot(dx,point2[1]))
            sq1 = cat(x,oc) + slab.normal*dot(slab.point, slab.normal)
            sq1 = cat(sq1, sq1+slab.thickness*slab.normal)
            self.data = V(maximum.reduce(sq1), minimum.reduce(sq1))
        elif point2:
            # just 2 3d points
            self.data = V(maximum(point1, point2),minimum(point1, point2))
        elif point1:
            # list of points
            self.data = V(maximum.reduce(point1), minimum.reduce(point1))
        else:
            # a null bbox
            self.data = None
            
    def add(self, point):
        vl = cat(self.data, point)
        self.data = V(maximum.reduce(vl), minimum.reduce(vl))

    def merge(self, bbox):
        self.add(bbox.data)

    def draw(self):
        if self.data:
            drawwirebox(black,add.reduce(self.data)/2,
                        subtract.reduce(self.data)/2)


class Slab:
    """ defines a slab in space which can tell you if a point is in the slab
    """
    def __init__(self, point, normal, thickness):
        self.point = point
        self.normal = norm(normal)
        self.thickness = thickness

    def isin(self, point):
        d = dot(point-self.point, self.normal)
        return d>=0 and d<= self.thickness


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
    def __init__(self, shp, ptlist, point, logic, eyeball=None):
        """ptlist is a list of 3d points describing a selection.
        point is the center of view, and normal gives the direction
        of the line of light. Form a structure for telling whether
        arbitrary points fall inside the curve from the point of view.
        """
        normal = shp.normal
        c=sum(ptlist)/len(ptlist)
        # establish a plane thru point normal to normal
        # its axes are (3-vectors) x and y
        x = norm(ptlist[0]-c)
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
        self.z = self.normal
        # how thick in what direction
        self.slab = shp.slab
        # boolean raster of filled-in shape
        self.matrix = mat1
        # where matrix[0,0] is in x,y space
        self.matbase = ibblo
        # bounding rectangle (2d)
        self.bboxhi = bboxhi
        self.bboxlo = bboxlo
        # 3d bounding box
        if self.slab: self.bbox = BBox(V(bboxlo, bboxhi), V(x,y), self.slab)
        # 2-d points of the curve
        self.points=ptlist
        # origin to which x and y are relative
        self.org = point+0.0
        # cookie front and back, measured along normal
        self.logic = logic
        # for projecting if not in ortho mode
        self.eyeball = eyeball

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
        color = logicColor(self.logic)
        pl = zip(self.points[:-1],self.points[1:])
        for p in pl:
            drawline(color,p[0],color,p[1])
        
            
        # for debugging
        self.bbox.draw()
        #if self.eyeball:
        #    for p in self.points:
        #        drawline(red,self.eyeball,white,p)
        #drawline(white,self.org,white,self.org+10*self.z)
        #drawline(white,self.org,white,self.org+10*self.x)
        #drawline(white,self.org,white,self.org+10*self.y)

        

    def isin(self, pt):
        """Project pt onto the curve's plane and return 1 if it falls
        inside the curve.
        """
        if self.slab and not self.slab.isin(pt): return 0
        p2 = V(dot(pt, self.x), dot(pt, self.y))
        if self.eyeball:
            p2 = p2 / (dot(pt - self.eyeball, self.normal) / 
                       vlen(self.org - self.eyeball))
        if logical_or.accumulate(less(p2,self.bboxlo)): return 0
        if logical_or.accumulate(greater(p2,self.bboxhi)): return 0
        ij = map(int,p2*8)-self.matbase
        return not self.matrix[ij]

class rectangle:
    def __init__(self, shp, pt1, pt2, origin, logic, eye=None):
        self.point1 = pt1
        self.point2 = pt2
        self.logic = logic
        
        self.right = shp.right
        self.up = shp.up
        self.normal = shp.normal
        self.org = origin+0.0

        self.slab = shp.slab

        pt2d1 = V(dot(pt1,self.right), dot(pt1, self.up))
        pt2d2 = V(dot(pt2,self.right), dot(pt2, self.up))

        self.bboxlo = minimum(pt2d1, pt2d2)
        self.bboxhi = maximum(pt2d1, pt2d2)
        
        # 3d bounding box
        if self.slab: self.bbox = BBox(V(self.bboxlo, self.bboxhi),
                                       V(self.right, self.up), self.slab)

        # for projecting if not in ortho mode
        self.eyeball = eye

    def isin(self, pt):

        if self.slab and not self.slab.isin(pt): return 0

        p = V(dot(pt, self.right), dot(pt, self.up))

        if self.eyeball:
            p = p / (dot(pt - self.eyeball, self.normal) / 
                     vlen(self.org - self.eyeball))
        
        v = p[0]>=self.bboxlo[0] and p[1]>=self.bboxlo[1]
        v = v and p[0]<=self.bboxhi[0] and p[1]<=self.bboxhi[1]
        return v
        
    def draw(self):
        """Draw the rectangle
        """
        color = logicColor(self.logic)
        drawrectangle(self.point1, self.point2, self.right, self.up, color)
 

class shape:
    """Represents a sequence of curves, each of which may be
    additive or subtractive.
    """
    def __init__(self, right, up, normal, slab=None):
        """A shape is a set of curves defining the whole cutout.
        """
        self.curves = []
        self.center=V(0,0,0)
        self.right = right
        self.up = up
        self.normal = normal
        self.bboxhi=None
        self.bboxlo=None
        self.picked=[]
        # for caching the display as a GL call list
        self.displist = glGenLists(1)
        self.havelist = 0
        self.slab = slab
        self.bbox = BBox()


    def pickline(self, ptlist, point, logic, eye=None):
        """Add a new curve to the shape.
        Args define the curve (see curve) and the logic operator
        for the curve telling whether it adds or removes material.
        """
        self.havelist = 0
        c = curve(self, ptlist, point, logic, eye)
        if self.slab: self.bbox.merge(c.bbox)
        self.curves += [c]

    def pickrect(self, pt1, pt2, org, logic, eye=None):
        """Add a new retangle to the shape.
        Args define the rectangle and the logic operator
        for the curve telling whether it adds or removes material.
        """
        self.havelist = 0
        c = rectangle(self, pt1, pt2, org, logic, eye)
        if self.slab: self.bbox.merge(c.bbox)
        self.curves += [c]
            
    def isin(self, pt):
        """returns 1 if pt is properly enclosed by the curves.
        curve.logic = 1 ==> include if inside
        curve.logic = 0 ==> remove if inside
        curve.logic = 2 ==> remove if outside
        """
        val = 0
        for c in self.curves:
            if c.logic == 1: val = val or c.isin(pt)
            elif c.logic == 2: val = val and c.isin(pt)
            elif c.logic == 0: val = val and not c.isin(pt)
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
        bblo, bbhi = self.bbox.data[1], self.bbox.data[0]
        self.bbox.draw()

        griderator = genDiam(bblo, bbhi)
        pp=griderator.next()
        while (pp):
            if self.isin(pp[0]):
                if self.isin(pp[1]):
                    drawcylinder(gray,pp[0], pp[1], 0.2)
                else: drawcylinder(gray,pp[0], (pp[1]+pp[0])/2, 0.2)
            elif self.isin(pp[1]):
                drawcylinder(gray, (pp[1]+pp[0])/2, pp[1], 0.2)
            pp=griderator.next()
        glEndList()
        self.havelist = 1

    def select(self, assy):
        """Loop thru all the atoms that are visible and select any
        that are 'in' the shape, ignoring the thickness parameter.
        """
        if assy.selmols:
            self.partselect(assy)
            return
        c=self.curves[0]
        if c.logic == 1:
            for mol in assy.molecules:
                if mol.display == diINVISIBLE: continue
                for a in mol.atoms.itervalues():
                    if a.display == diINVISIBLE: continue
                    if c.isin(a.posn()): a.pick()
        elif c.logic == 2:
            for a in assy.selatoms.values():
                if not c.isin(a.posn()): a.unpick()
        else:
            for a in assy.selatoms.values():
                if c.isin(a.posn()): a.unpick()

    def partselect(self, assy):
        """Loop thru all the atoms that are visible and select any
        that are 'in' the shape, ignoring the thickness parameter.
        pick the parts that contain them
        """
        c=self.curves[0]
        if c.logic == 1:
            for mol in assy.molecules:
                if mol.display == diINVISIBLE: continue
                for a in mol.atoms.itervalues():
                    if a.display == diINVISIBLE: continue
                    if c.isin(a.posn()): a.pick()
        elif c.logic == 2:
            for a in assy.selatoms.values():
                if not c.isin(a.posn()): a.unpick()
        else:
            for a in assy.selatoms.values():
                if c.isin(a.posn()): a.unpick()

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
