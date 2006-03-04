# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
shape.py

Handle the freehand curves for selection and cookie-cutting

$Id$
"""
__author__ = "Josh"

from Numeric import array, zeros, logical_or

from VQT import *
from OpenGL.GL import glNewList, glEndList, glCallList, glGenLists
from OpenGL.GL import GL_COMPILE_AND_EXECUTE

from drawer import *
from constants import *

from debug import print_compact_traceback
import platform 


class BBox:
    """ implement a bounding box in 3-space
    BBox(PointList)
    BBox(point1, point2)
    BBox(2dpointpair, 3dx&y, slab)
    data is stored hi, lo so we can use subtract.reduce
    """
    def __init__(self, point1=None, point2=None, slab = None):
        """Huaicai 4/23/05: added some comments as below to help understand the code. """
        if slab:
            # convert from 2d (x, y) coordinates into its 3d world (x, y, 0) coordinates(the lower-left and upper-right corner). In another word, the 3d coordinates minus the z offset of the plane.
            x=dot(A(point1),A(point2))
            # Get the vector from upper-right point to the lower-left point
            dx = subtract.reduce(x)
            # Get the upper-left and lower right corner points
            oc=x[1]+V(point2[0]*dot(dx,point2[0]),point2[1]*dot(dx,point2[1]))
            # Get the four 3d cooridinates on the bottom cookie-cutting plane
            sq1 = cat(x,oc) + slab.normal*dot(slab.point, slab.normal)
            # transfer the above 4 3d coordinates in parallel to get that on the top plane, put them together
            sq1 = cat(sq1, sq1+slab.thickness*slab.normal)
            self.data = V(maximum.reduce(sq1), minimum.reduce(sq1))
        elif point2:
            # just 2 3d points
            self.data = V(maximum(point1, point2),minimum(point1, point2))
        elif point1:
            # list of points: could be 2d or 3d?  +/- 1.8 to make the bounding box enclose the vDw ball of an atom?
            self.data = V(maximum.reduce(point1) + 1.8, minimum.reduce(point1) - 1.8)
        else:
            # a null bbox
            self.data = None
    
            
    def add(self, point):
        vl = cat(self.data, point)
        self.data = V(maximum.reduce(vl), minimum.reduce(vl))

    def merge(self, bbox):
        if self.data and bbox.data: self.add(bbox.data)
        else: self.data = bbox.data

    def draw(self):
        if self.data:
            drawwirebox(black,add.reduce(self.data)/2,
                        subtract.reduce(self.data)/2)

    def center(self):
        if self.data: return add.reduce(self.data)/2.0
        else: return V(0,0,0)

    def isin(self, pt):
        return (minimum(pt,self.data[1]) == self.data[1] and
                maximum(pt,self.data[0]) == self.data[0])

    def scale(self):
        if not self.data: return 10.0
        #x=1.2*maximum.reduce(subtract.reduce(self.data))
        dd = 0.5*subtract.reduce(self.data)
        x = sqrt(dd[0]*dd[0] + dd[1]*dd[1] + dd[2]*dd[2])
        #return max(x, 2.0)
        return x

    def copy(self, offset=None):
        if offset: return BBox(self.data[0]+offset, self.data[1]+offset)
        return BBox(self.data[0], self.data[1])


############################
#         Slab             #
############################


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

    def __str__(self):
        return '<slab of '+`self.thickness`+' at '+`self.point`+'>'


def fill(mat,p,dir):
    """ Fill a curve drawn in matrix mat in 1's on 0's with 1's.
    p is V(i,j) of a point to fill from. dir is 1 or -1 for the
    standard recursive fill algorithm. 
    Huaicai: This function is used to fill the area between the rectangle bounding box and the boundary
    of the curve with 1's. The bounding box is extended by (lower left corner -2, right top corner + 2). 
    The curve boundary is filled with 1's. So mat[1,:] = 0, mat[-1,:]=0, mat[:, 1]=0;
    mat[:, -1]=0, which mean the area is connected. If we start from mat[1,1], dir =1, then we scan the 
    first line from left to right. If it's 0, fill it as 1 until we touch 1. For each element in the line, we also 
    check it's neighbor above and below. For the neighbor elements, if the neighbor touches 1 but 
    previous neighbor is 0, then scan the neighbor line in the reverse order. I think this algorithm is better
    than the simple recursive flood filling algorithm. The seed mat[1,1] is always inside the area, and 
    most probably this filling area is smaller than that inside the curve. I think it also reduces repeated 
    checking/filling of the classical algorithm.
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


#bruce 041214 made a common superclass for curve and rectangle classes,
# so I can fix some bugs in a single place, and since there's a
# lot of common code. Some of it could be moved into class shape (for more
# efficiency when several curves in one shape), but I didn't do that, since
# I'm not sure we'll always want to depend on that agreement of coord systems
# for everything in one shape.

class simple_shape_2d: 
    "common code for selection curve and selection rectangle"
    def __init__(self, shp, ptlist, origin, selSense, opts):
        """ptlist is a list of 3d points describing a selection
        (in a subclass-specific manner).
        origin is the center of view, and shp.normal gives the direction
        of the line of light.
        """
        # store orthonormal screen-coordinates from shp
        self.right = shp.right
        self.up = shp.up
        self.normal = shp.normal
        
        # store other args
        self.ptlist = ptlist
        self.org = origin + 0.0
        self.selSense = selSense
        self.slab = opts.get('slab', None) # how thick in what direction
        self.eyeball = opts.get('eye', None) # for projecting if not in ortho mode
        
        if self.eyeball:
            self.eye2Pov = vlen(self.org - self.eyeball)
        
        # project the (3d) path onto the plane. Warning: arbitrary 2d origin!
        # Note: original code used project_2d_noeyeball, and I think this worked
        # since the points were all in the same screen-parallel plane as
        # self.org (this is a guess), but it seems better to not require this
        # but just to use project_2d here (taking eyeball into account).
        self._computeBBox()
        
    def _computeBBox(self):
        """ Construct the 3d bounding box for the area """  
        # compute bounding rectangle (2d)
        self.pt2d = map( self.project_2d, self.ptlist)
        assert not (None in self.pt2d)
        
        self.bboxhi = reduce(maximum, self.pt2d)
        self.bboxlo = reduce(minimum, self.pt2d)
        bboxlo, bboxhi = self.bboxlo, self.bboxhi
        
        # compute 3d bounding box
        # Note: bboxlo, bboxhi are 2d coordinates relative to the on plane
        # 2D coordinate system: self.right and self.up. When constructing
        # the 3D bounding box, the coordinates will be transformed back to 
        # 3d world coordinates.
        if self.slab:
            x, y = self.right, self.up
            self.bbox = BBox(V(bboxlo, bboxhi), V(x,y), self.slab)
        else:
            self.bbox = BBox()
        return

    def project_2d_noeyeball(self, pt):
        """Bruce: Project a point into our plane (ignoring eyeball). Warning: arbitrary origin!
           
           Huaicai 4/20/05: This is just to project pt into a 2d coordinate 
           system (self.right, self.up) on a plane through pt and parallel to the screen 
           plane. For perspective projection, (x,y) on this plane is different than that on the plane 
           through pov.
        """
        x, y = self.right, self.up
        return V(dot(pt, x), dot(pt, y))

    def project_2d(self, pt):
        """like project_2d_noeyeball, but take into account self.eyeball;
        return None for a point that is too close to eyeball to be projected
        [in the future this might include anything too close to be drawn #e]
        """
        p = self.project_2d_noeyeball(pt)
        if self.eyeball:
            # bruce 041214: use "pfix" to fix bug 30 comment #3
            pfix = self.project_2d_noeyeball(self.org)
            p -= pfix
            try:
                ###e we recompute this a lot; should cache it in self or self.shp--Bruce
                ## Huaicai 04/23/05: made the change as suggested by Bruce above.
                p = p / (dot(pt - self.eyeball, self.normal) / self.eye2Pov)
            except:
                # bruce 041214 fix of unreported bug:
                # point is too close to eyeball for in-ness to be determined!
                # [More generally, do we want to include points which are
                #  projectable without error, but too close to the eyeball
                #  to be drawn? I think not, but I did not fix this yet
                #  (or report the bug). ###e]
                if platform.atom_debug:
                    print_compact_traceback("atom_debug: ignoring math error for point near eyeball: ")
                return None
            p += pfix
        return p

    def isin_bbox(self, pt):
        "say whether a point is in the optional slab, and 2d bbox (uses eyeball)"
        # this is inlined and extended by curve.isin
        if self.slab and not self.slab.isin(pt):
            return False
        p = self.project_2d(pt)
        if p == None:
            return False
        return p[0]>=self.bboxlo[0] and p[1]>=self.bboxlo[1] \
            and p[0]<=self.bboxhi[0] and p[1]<=self.bboxhi[1]

    pass # end of class simple_shape_2d


class rectangle(simple_shape_2d): # bruce 041214 factored out simple_shape_2d
    "selection rectangle"
    def __init__(self, shp, pt1, pt2, origin, selSense, **opts):
        simple_shape_2d.__init__( self, shp, [pt1, pt2], origin, selSense, opts)        
    def isin(self, pt):
        return self.isin_bbox(pt)
    def draw(self):
        """Draw the rectangle"""
        color = get_selCurve_color(self.selSense)
        drawrectangle(self.ptlist[0], self.ptlist[1], self.right, self.up, color)
    pass


class curve(simple_shape_2d): # bruce 041214 factored out simple_shape_2d
    """Represents a single closed curve in 3-space, projected to a
    specified plane.
    """
    def __init__(self, shp, ptlist, origin, selSense, **opts):
        """ptlist is a list of 3d points describing a selection.
        origin is the center of view, and normal gives the direction
        of the line of light. Form a structure for telling whether
        arbitrary points fall inside the curve from the point of view.
        """
        # bruce 041214 rewrote some of this method
        simple_shape_2d.__init__( self, shp, ptlist, origin, selSense, opts)
        
        # bounding rectangle, in integers (scaled 8 to the angstrom)
        ibbhi = array(map(int,ceil(8*self.bboxhi)+2))
        ibblo = array(map(int,floor(8*self.bboxlo)-2))
        bboxlo = self.bboxlo
        
        # draw the curve in these matrices and fill it
        # [bruce 041214 adds this comment: this might be correct but it's very
        # inefficient -- we should do it geometrically someday. #e]
        mat = zeros(ibbhi-ibblo)
        mat1 = zeros(ibbhi-ibblo)
        mat1[0,:] = 1
        mat1[-1,:] = 1
        mat1[:,0] = 1
        mat1[:,-1] = 1
        pt2d = self.pt2d
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
        mat1 -= mat #Which means boundary line is counted as inside the shape.
        # boolean raster of filled-in shape
        self.matrix = mat1  ## For any element inside the matrix, if it is 0, then it's inside.
        # where matrix[0,0] is in x,y space
        self.matbase = ibblo

        # axes of the plane; only used for debugging
        self.x = self.right
        self.y = self.up
        self.z = self.normal

    def isin(self, pt):
        """Project pt onto the curve's plane and return 1 if it falls
        inside the curve.
        """
        # this inlines some of isin_bbox, since it needs an
        # intermediate value computed by that method
        if self.slab and not self.slab.isin(pt):
            return False
        p = self.project_2d(pt)
        if p == None:
            return False
        in_bbox = p[0]>=self.bboxlo[0] and p[1]>=self.bboxlo[1] \
               and p[0]<=self.bboxhi[0] and p[1]<=self.bboxhi[1]
        if not in_bbox:
            return False
        ij = map(int,p*8)-self.matbase
        return not self.matrix[ij]

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
                    drawline(col,p,p+dx+dy)
                    drawline(col,p+dx,p+dy)

    def draw(self):
        """Draw two projections of the curve at the limits of the
        thickness that defines the cookie volume.
        The commented code is for debugging.
        [bruce 041214 adds comment: the code looks like it
        only draws one projection.]
        """
        color = get_selCurve_color(self.selSense)
        pl = zip(self.ptlist[:-1],self.ptlist[1:])
        for p in pl:
            drawline(color,p[0],p[1])
        
        # for debugging
        #self.bbox.draw()
        #if self.eyeball:
        #    for p in self.ptlist:
        #        drawline(red,self.eyeball,p)
        #drawline(white,self.org,self.org+10*self.z)
        #drawline(white,self.org,self.org+10*self.x)
        #drawline(white,self.org,self.org+10*self.y)

    pass # end of class curve

class Circle(simple_shape_2d):
    """Represents the area of a circle ortho projection intersecting with a slab. """
    def __init__(self, shp, ptlist, origin, selSense, **opts):
        """<Param> ptlist: the circle center and a point on the perimeter """
        simple_shape_2d.__init__( self, shp, ptlist, origin, selSense, opts)
            
    def draw(self):
        """the profile circle draw"""
        color =  get_selCurve_color(self.selSense)
        drawCircle(color, self.ptlist[0], self.rad, self.slab.normal)
        
    def isin(self, pt):
        """Test if a point is in the area """
        if self.slab and not self.slab.isin(pt):
            return False
            
        p2d = self.project_2d(pt)
        dist = vlen(p2d - self.cirCenter)
        if dist <= self.rad :
            return True
        else:
            return False
   
    def _computeBBox(self):
        """Construct the 3D bounding box for this volume. """
        self.rad = vlen(self.ptlist[1] - self.ptlist[0])
        self.cirCenter = self.project_2d(self.ptlist[0])
        
        bbhi = self.cirCenter + V(self.rad, self.rad)
        bblo = self.cirCenter - V(self.rad, self.rad)
        
        x, y = self.right, self.up
        self.bbox = BBox(V(bblo, bbhi), V(x,y), self.slab)
        
    
class shape:
    """Represents a sequence of curves, each of which may be
    additive or subtractive.
    [This class should be renamed, since there is also an unrelated
    Numeric function called shape().]
    """
    def __init__(self, right, up, normal):
        """A shape is a set of curves defining the whole cutout.
        """
        self.curves = []
        self.bbox = BBox()

        # These arguments are required to be orthonormal:
        self.right = right
        self.up = up
        self.normal = normal
    
    def pickline(self, ptlist, origin, selSense, **xx):
            """Add a new curve to the shape.
            Args define the curve (see curve) and the selSense operator
            for the curve telling whether it adds or removes material.
            """
            c = curve(self, ptlist, origin, selSense, **xx)
            #self.curves += [c]
            #self.bbox.merge(c.bbox)
            return c
            
    def pickrect(self, pt1, pt2, org, selSense, **xx):
            c = rectangle(self, pt1, pt2, org, selSense, **xx)
            #self.curves += [c]
            #self.bbox.merge(c.bbox)
            return c

    def __str__(self):
        return "<Shape of " + `len(self.curves)` + ">"

    pass # end of class shape
    
class SelectionShape(shape):
        """This is used to construct shape for atoms/chunks selection. A curve or rectangle will be created, which is used as an area selection of all the atoms/chunks """
        def pickline(self, ptlist, origin, selSense, **xx):
            self.curve = shape.pickline(self, ptlist, origin, selSense, **xx)
   
        def pickrect(self, pt1, pt2, org, selSense, **xx):
            self.curve = shape.pickrect(self, pt1, pt2, org, selSense, **xx)
            
        def select(self, assy):
            """Loop thru all the atoms that are visible and select any
                that are 'in' the shape, ignoring the thickness parameter.
            """
            #bruce 041214 conditioned this on a.visible() to fix part of bug 235;
            # also added .hidden check to the last of 3 cases. Left everything else
            # as I found it. This code ought to be cleaned up to make it clear that
            # it uses the same way of finding the selection-set of atoms, for all
            # three selSense cases in each of select and partselect. If anyone adds
            # back any differences, this needs to be explained and justified in a
            # comment; lacking that, any such differences should be considered bugs.
            # (BTW I don't know whether it's valid to care about selSense of only the
            # first curve in the shape, as this code does.)
            
            # Huaicai 04/23/05: For selection, every shape only has one curve, so 
            # the above worry by Bruce is not necessary. The reason of not reusing
            # shape is because after each selection user may change view orientation,
            # which requires a new shape creation.
        
            if assy.selwhat:
                self._chunksSelect(assy)
            else:
                if self.curve.selSense == START_NEW_SELECTION: 
                    # New selection curve. Consistent with Select Chunks behavior.
                    assy.unpickparts() # Fixed bug 606, partial fix for bug 365.  Mark 050713.
                    assy.unpickatoms() # Fixed bug 1598. Mark 060303.
                self._atomsSelect(assy)   
        
        
        def _atomsSelect(self, assy):
            """Select all atoms inside the shape according to its selection selSense."""    
            c=self.curve
            if c.selSense == ADD_TO_SELECTION:
                for mol in assy.molecules:
                    if mol.hidden: continue
                    disp = mol.get_dispdef()
                    for a in mol.atoms.itervalues():
                        if c.isin(a.posn()) and a.visible(disp):
                            a.pick()
            elif c.selSense == START_NEW_SELECTION:
                for mol in assy.molecules:
                    if mol.hidden: continue
                    disp = mol.get_dispdef()
                    for a in mol.atoms.itervalues():
                        if c.isin(a.posn()) and a.visible(disp):
                            a.pick()
                        else:
                            a.unpick()
            elif c.selSense == SUBTRACT_FROM_SELECTION:
                for a in assy.selatoms.values():
                    if a.molecule.hidden: continue #bruce 041214
                    if c.isin(a.posn()) and a.visible():
                        a.unpick()
            elif c.selSense == DELETE_SELECTION:
                todo = []
                for mol in assy.molecules:
                    if mol.hidden: continue
                    disp = mol.get_dispdef()
                    for a in mol.atoms.itervalues():
                        if c.isin(a.posn()) and a.visible(disp):
                            if a.is_singlet(): continue
                            todo.append(a)
                for a in todo[:]:
                    if a.filtered(): continue
                    a.kill()
            else:
                print "Error in shape._atomsSelect(): Invalid selSense=", c.selSense
                #& debug method. mark 060211.

        def _chunksSelect(self, assy):
            """Loop thru all the atoms that are visible and select any
            that are 'in' the shape, ignoring the thickness parameter.
            pick the parts that contain them
            """

        #bruce 041214 conditioned this on a.visible() to fix part of bug 235;
        # also added .hidden check to the last of 3 cases. Same in self.select().
            c=self.curve
            if c.selSense == START_NEW_SELECTION:
                # drag selection: unselect any selected molecule not in the area, 
                # modified by Huaicai to fix the selection bug 10/05/04
                for m in assy.selmols[:]:
                    m.unpick()
                            
            if c.selSense == ADD_TO_SELECTION or c.selSense == START_NEW_SELECTION:
                for mol in assy.molecules:
                    if mol.hidden: continue
                    disp = mol.get_dispdef()
                    for a in mol.atoms.itervalues():
                        if c.isin(a.posn()) and a.visible(disp):
                            a.molecule.pick()
                            break
    
            if c.selSense == SUBTRACT_FROM_SELECTION:
                for m in assy.selmols[:]:
                    if m.hidden: continue #bruce 041214
                    disp = m.get_dispdef()
                    for a in m.atoms.itervalues():
                        if c.isin(a.posn()) and a.visible(disp):
                            m.unpick()
                            break   
                                    
            if c.selSense == DELETE_SELECTION: # mark 060220.
                for mol in assy.molecules:
                    if mol.hidden: continue
                    disp = mol.get_dispdef()
                    for a in mol.atoms.itervalues():
                        if c.isin(a.posn()) and a.visible(disp):
                            a.molecule.kill()
                            break
        
        def findObjInside(self, assy):
            '''Find atoms/chunks that are inside the shape. '''
            rst = []
            
            c=self.curve
            
            if assy.selwhat: ##Chunks
               rstMol = {} 
               for mol in assy.molecules:
                    if mol.hidden: continue
                    disp = mol.get_dispdef()
                    for a in mol.atoms.itervalues():
                        if c.isin(a.posn()) and a.visible(disp):
                                rstMol[id(a.molecule)] = a.molecule
                                break 
               rst.extend(rstMol.itervalues())
            else: ##Atoms
               for mol in assy.molecules:
                    if mol.hidden: continue
                    disp = mol.get_dispdef()
                    for a in mol.atoms.itervalues():
                       if c.isin(a.posn()) and a.visible(disp):
                         rst += [a] 
            return rst
           
class CookieShape(shape):
    """ This class is used to create cookies. It supports multiple parallel layers, each curve sits on a particular layer."""
    def __init__(self, right, up, normal, mode, latticeType):
            shape.__init__(self, right, up, normal)
            ##Each element is a dictionary object storing "carbon" info for a layer
            self.carbonPosDict = {} 
            self.hedroPosDict = {}
            self.markedAtoms = {}
            #Each element is a dictionary for the bonds info for a layer
            self.bondLayers = {} 
            
            self.displist = glGenLists(1)
            self.havelist = 0
            self.dispMode = mode
            self.latticeType = latticeType
            self.layerThickness = {}
            self.layeredCurves = {} #A list of (merged bb, curves) for each layer

    def pushdown(self, lastLayer):
            """Put down one layer from last layer """
            th, n = self.layerThickness[lastLayer]
            #print "th, n", th, n
            return th*n

    def _saveMaxThickness(self, layer, thickness, normal):
            if layer not in self.layerThickness:
                self.layerThickness[layer] = (thickness, normal)
            elif thickness > self.layerThickness[layer][0]:
                self.layerThickness[layer] = (thickness, normal)
    
    def isin(self, pt, curves=None):
        """returns 1 if pt is properly enclosed by the curves.
        curve.selSense = 1 ==> include if inside
        curve.selSense = 0 ==> remove if inside
        curve.selSense = 2 ==> remove if outside
        """
        #& To do: docstring needs to be updated.  mark 060211.
        # bruce 041214 comment: this might be a good place to exclude points
        # which are too close to the screen to be drawn. Not sure if this
        # place would be sufficient (other methods call c.isin too).
        # Not done yet. ###e
        val = 0
        if not curves: curves = self.curves
        for c in curves:
            if c.selSense == ADD_TO_SELECTION: 
                val = val or c.isin(pt)
            elif c.selSense == OUTSIDE_SUBTRACT_FROM_SELECTION:
                val = val and c.isin(pt)
            elif c.selSense == SUBTRACT_FROM_SELECTION:
                val = val and not c.isin(pt)
        return val
    
    def pickCircle(self, ptlist, origin, selSense, layer, slabC):
        """Add a new circle to the shape. """
        c = Circle(self, ptlist, origin, selSense, slab=slabC)
        self._saveMaxThickness(layer, slabC.thickness, slabC.normal)
        self._cutCookie(layer, c)
        self._addCurve(layer, c)
    
    def pickline(self, ptlist, origin, selSense, layer, slabC):
        """Add a new curve to the shape.
        Args define the curve (see curve) and the selSense operator
        for the curve telling whether it adds or removes material.
        """
        c = shape.pickline(self, ptlist, origin, selSense, slab=slabC)
        self._saveMaxThickness(layer, slabC.thickness, slabC.normal)
        self._cutCookie(layer, c)
        self._addCurve(layer, c)
        
    def pickrect(self, pt1, pt2, org, selSense, layer, slabC):
        """Add a new rectangle to the shape.
        Args define the rectangle and the selSense operator
        for the curve telling whether it adds or removes material.
        """
        c = shape.pickrect(self, pt1, pt2, org, selSense, slab=slabC)
        self._saveMaxThickness(layer, slabC.thickness, slabC.normal)
        self._cutCookie(layer, c)
        self._addCurve(layer, c)

    def _updateBBox(self, curveList):
        """Re-compute the bounding box for the list of curves"""
        bbox = BBox()
        for c in curveList[1:]:
            bbox.merge(c.bbox)
        curveList[0] = bbox
        
    
    def undo(self, currentLayer):
        """This would work for shapes, if anyone called it.
        """
        if self.layeredCurves.has_key(currentLayer):
            curves = self.layeredCurves[currentLayer]
            if len(curves) > 1: 
                curves = curves[:-1]
            self._updateBBox(curves)
            self.layeredCurves[currentLayer] = curves
            
            ##Kludge to make the undo work.
            self.carbonPosDict[currentLayer] = {} 
            self.hedroPosDict[currentLayer] = {}
            self.bondLayers[currentLayer] = {}
            for c in curves[1:]:
                self._cutCookie(currentLayer, c)
            
            self.havelist = 0

    def clear(self, currentLayer):
        """This would work for shapes, if anyone called it.
        """
        curves = self.layeredCurves[currentLayer]
        curves = []
        self.layeredCurves[currentLayer] = curves
        self.havelist = 0

    def anyCurvesLeft(self):
        """Return True if there are curve(s) left, otherwise, False. 
            This can be used by user to decide if the shape object
            can be deleted. """
        for cbs in self.layeredCurves.values():
            if len(cbs) > 1:
                return True
        return False
            
    def combineLayers(self):
        """Experimental code to add all curves and bbox together to make the molmake working. It may be removed later. """
        for cbs in self.layeredCurves.values():
            if cbs:
                self.bbox.merge(cbs[0])
                self.curves += cbs[1:]
   
    def _hashAtomPos(self, pos):
        return int(dot(V(1000000, 1000,1),floor(pos*1.2)))
    
    def _addCurve(self, layer, c):
        """Add curve into its own layer, update the bbox"""
        self.havelist = 0
        
        if not layer in self.layeredCurves:
            bbox = BBox()
            self.layeredCurves[layer] = [bbox, c]
        else: self.layeredCurves[layer] += [c]
        self.layeredCurves[layer][0].merge(c.bbox)
    
    def _cellDraw(self, color, p0, p1):
        hasSinglet = False
        if type(p1) == type((1,)): 
                v1 = p1[0]
                hasSinglet = True
        else: v1 = p1
        if self.dispMode == 'Tubes':
             drawcylinder(color, p0, v1, 0.2)
        else:
            drawsphere(color, p0, 0.5, 1)
            if hasSinglet:
                drawsphere(color, v1, 0.2, 1)
            else:    
                drawsphere(color, v1, 0.5, 1)
            drawline(white, p0, v1)
    
    def _anotherDraw(self, layerColor):
        """The original way of selecting cookies, but do it layer by layer, so we can control how to display each layer. """
        if self.havelist:
            glCallList(self.displist)
            return
        glNewList(self.displist, GL_COMPILE_AND_EXECUTE)
        for layer in self.layeredCurves.keys():
            bbox = self.layeredCurves[layer][0]
            curves = self.layeredCurves[layer][1:]
            if not curves: continue
            color = layerColor[layer]
            for c in curves: c.draw()
            try:
                bblo, bbhi = bbox.data[1], bbox.data[0]
                allCells = genDiam(bblo-1.6, bbhi+1.6, self.latticeType)
                for cell in allCells:
                    for pp in cell:
                        p1 = p2 = None
                        if self.isin(pp[0], curves):
                            if self.isin(pp[1], curves):
                                p1 = pp[0]; p2 = pp[1]
                            else: 
                                p1 = pp[0]; p2 = ((pp[1]+pp[0])/2, )
                        elif self.isin(pp[1], curves):
                                p1 = pp[1]; p2 = ((pp[1]+pp[0])/2, )
                        if p1 and p2: self._cellDraw(color, p1, p2) 
            except:
            # bruce 041028 -- protect against exceptions while making display
            # list, or OpenGL will be left in an unusable state (due to the lack
            # of a matching glEndList) in which any subsequent glNewList is an
            # invalid operation. (Also done in chem.py; see more comments there.)
                print_compact_traceback( "bug: exception in shape.draw's displist; ignored: ")
        glEndList()
        self.havelist = 1 #
    
    
    def _cutCookie(self, layer, c):
        """For each user defined curve, cut the cookie for it, store carbon postion into a global dictionary, store the bond information into each layer. """
        self.havelist = 0
        
        bblo, bbhi = c.bbox.data[1], c.bbox.data[0]
        #Without +(-) 1.6, cookie for lonsdaileite may not be right
        allCells = genDiam(bblo-1.6, bbhi+1.6, self.latticeType)
        if self.carbonPosDict.has_key(layer):
            carbons = self.carbonPosDict[layer]
        else: carbons = {}
        
        if self.hedroPosDict.has_key(layer):
            hedrons = self.hedroPosDict[layer]
        else: hedrons = {}
        
        if c.selSense == SUBTRACT_FROM_SELECTION:
            markedAtoms = self.markedAtoms
            if not self.bondLayers or not self.bondLayers.has_key(layer):   return
            else:
                bonds = self.bondLayers[layer]
                for cell in allCells:
                    for pp in cell:
                       ppInside = [False, False]
                       for ii in range(2):
                            if c.isin(pp[ii]): 
                                ppInside[ii] = True
                       if ppInside[0] or ppInside[1]:
                            self._logic0Bond(carbons, bonds, markedAtoms, hedrons, ppInside, pp)
                self. _removeMarkedAtoms(bonds, markedAtoms, 
                                                                            carbons, hedrons)
        
        elif c.selSense == OUTSIDE_SUBTRACT_FROM_SELECTION:
            #& This differs from the standard selection scheme for Shift+Drag. mark 060211.
            if not self.bondLayers or not self.bondLayers.has_key(layer):       return
            bonds = self.bondLayers[layer]
            newBonds = {}; newCarbons = {}; newHedrons = {}; 
            insideAtoms = {}
            newStorage = (newBonds, newCarbons, newHedrons)
            for cell in allCells:
                for pp in cell:
                    pph = [None, None]
                    for ii in range(2):
                        if c.isin(pp[ii]): 
                            pph[ii] = self._hashAtomPos(pp[ii])
                            if bonds.has_key(pph[ii]):
                                insideAtoms[pph[ii]] = pp[ii]
                    
                    if (not pph[0]) and pph[1] and carbons.has_key(pph[1]):
                        pph[0] = self._hashAtomPos(pp[0])
                        if bonds.has_key(pph[0]):
                            newCarbons[pph[1]] = pp[1]
                            newHedrons[pph[0]] = pp[0]
                            if not newBonds.has_key(pph[0]):
                                newBonds[pph[0]] = [(pph[1], 1)]
                            else: newBonds[pph[0]] += [(pph[1], 1)]
            if insideAtoms:
                self._logic2Bond(carbons, bonds, hedrons, insideAtoms, newStorage)
            bonds, carbons, hedrons = newStorage
            
        elif c.selSense == ADD_TO_SELECTION:
            if self.bondLayers.has_key(layer):
                bonds = self.bondLayers[layer]
            else:
                bonds = {}
            for cell in allCells:
                for pp in cell:
                    pph=[None, None]
                    ppInside = [False, False]
                    for ii in range(2):
                        pph[ii] = self._hashAtomPos(pp[ii]) 
                        if c.isin(pp[ii]):
                            ppInside[ii] = True
                    if ppInside[0] or ppInside[1]:
                        self._logic1Bond(carbons, hedrons, bonds, pp, pph, ppInside)        
                        
        self.bondLayers[layer] = bonds
        self.carbonPosDict[layer] = carbons
        self.hedroPosDict[layer] = hedrons
        
        #print "bonds", bonds   
        self.havelist = 1
    
    
    def _logic0Bond(self, carbons, bonds, markedAtoms, hedrons, ppInside, pp):
            """For each pair of points<pp[0], pp[1]>, if both points are inside the
                curve and are existed carbons, delete the bond, and mark the 
                'should be' removed atoms. Otherwise, delete half bond or 
                change full to half bond accoringly. """
            
            def _deleteHalfBond(which_in):
                """Internal function: when the value-- carbon atom is removed from an half bond, delete the half bond. """
                markedAtoms[pph[which_in]] = pp[which_in]    
                try:
                    values = bonds[pph[0]]
                    values.remove((pph[1], which_in))
                    bonds[pph[0]] = values
                    if len(values) == 0: del bonds[pph[0]]
                    #print "Delete half bond: ", pph[0], (pph[1], which_in)
                except:
                    print "No such half bond: ", pph[0], (pph[1], which_in)
                
            def _changeFull2Half(del_id, which_in):
                """internal function: If there is a full bond and when the value(2ndin a bond pair) carbon atom is removed, change it to half bond"""
                if not hedrons.has_key(pph[del_id]): hedrons[pph[del_id]] = pp[del_id]
                markedAtoms[pph[del_id]] = pp[del_id]
                if bonds.has_key(pph[0]):
                    values = bonds[pph[0]]
                    idex = values.index(pph[1])
                    values[idex] = (pph[1], which_in)
                    bonds[pph[0]] = values
                    #print "Change full to half bond: ", pph[0], (pph[1], which_in)
                
            pph = []
            pph += [self._hashAtomPos(pp[0])]
            pph += [self._hashAtomPos(pp[1])]
            if ppInside[0] and ppInside[1]:
                # Delete full bond
                if carbons.has_key(pph[0]) and carbons.has_key(pph[1]):
                    markedAtoms[pph[0]] = pp[0]
                    markedAtoms[pph[1]] = pp[1]
                    values = bonds[pph[0]]
                    values.remove(pph[1])
                    bonds[pph[0]] = values
                    if len(values) == 0: del bonds[pph[0]]
                # Delete half bond                              
                elif carbons.has_key(pph[0]):
                    #markedAtoms[pph[0]] = pp[0]
                    _deleteHalfBond(0)
                # Delete half bond
                elif carbons.has_key(pph[1]):
                    _deleteHalfBond(1)
            elif ppInside[0]:
                # Full bond becomes half bond, carbon becomes hedron
                if carbons.has_key(pph[0]) and carbons.has_key(pph[1]):
                    markedAtoms[pph[0]] = pp[0]
                    #_changeFull2Half(0, 1)
                # Delete half bond    
                elif carbons.has_key(pph[0]):
                    #markedAtoms[pph[0]] = pp[0]
                    _deleteHalfBond(0)
            elif ppInside[1]:
                # Full bond becomes half bond, carbon becomes hedron
                if carbons.has_key(pph[1]) and carbons.has_key(pph[0]):
                    _changeFull2Half(1, 0)
                # Delete half bond    
                elif carbons.has_key(pph[1]):
                    _deleteHalfBond(1)
                           
    
    def _logic1Bond(self, carbons, hedrons, bonds, pp, pph, ppInside):
            """For each pair of points <pp[0], pp[1]>, create a full bond if 
                necessary and if both points are inside the curve ; otherwise, 
                if one point is in while the other is not, create a half bond if 
                necessary."""
            if ppInside[0] and ppInside[1]:
                if (not pph[0] in carbons) and (not pph[1] in carbons):
                    if pph[0] in hedrons: del hedrons[pph[0]]
                    if pph[1] in hedrons: del hedrons[pph[1]]
                    carbons[pph[0]] = pp[0]
                    carbons[pph[1]] = pp[1]
                    # create a new full bond
                    self._createBond(bonds, pph[0], pph[1], -1, True) 
                elif not pph[0] in carbons:
                    if pph[0] in hedrons: del hedrons[pph[0]]
                    carbons[pph[0]] = pp[0]
                    # update half bond to full bond
                    self._changeHf2FullBond(bonds, pph[0], pph[1], 1) 
                elif not pph[1] in carbons:
                    if pph[1] in hedrons: del hedrons[pph[1]]
                    carbons[pph[1]] = pp[1]
                    # update half bond to full bond
                    self._changeHf2FullBond(bonds, pph[0], pph[1], 0) 
                # create full bond
                else: self._createBond(bonds, pph[0], pph[1])
                
            elif ppInside[0]:
                if (not pph[0] in carbons) and (not pph[1] in carbons):
                    if pph[0] in hedrons: del hedrons[pph[0]]
                    carbons[pph[0]] = pp[0]
                    if not pph[1] in hedrons: hedrons[pph[1]] = pp[1]
                    # create new half bond
                    self._createBond(bonds, pph[0], pph[1], 0, True) 
                elif not pph[0] in carbons:
                    if pph[0] in hedrons: del hedrons[pph[0]]
                    carbons[pph[0]] = pp[0]
                    #update half bond to full bond
                    self._changeHf2FullBond(bonds, pph[0], pph[1], 1) 
                elif not pph[1] in carbons:
                    if not pph[1] in hedrons: hedrons[pph[1]] = pp[1]
                    # create half bond, with 0 in, 1 out
                    self._createBond(bonds, pph[0], pph[1], 0) 
                # create full bond
                else: self._createBond(bonds, pph[0], pph[1])
                
            elif ppInside[1]:
                if (not pph[0] in carbons) and (not pph[1] in carbons):
                    if pph[1] in hedrons: del hedrons[pph[1]]
                    carbons[pph[1]] = pp[1]
                    if not pph[0] in hedrons: hedrons[pph[0]] = pp[0]
                    # create new half bond, with 1 in, 0 out
                    self._createBond(bonds, pph[0], pph[1], 1, True) 
                elif not pph[0] in carbons:
                    if not pph[0] in hedrons: hedrons[pph[0]] = pp[0]
                    # create half bond, with 1 in, 0 out
                    self._createBond(bonds, pph[0], pph[1], 1) 
                elif not pph[1] in carbons:
                    if pph[1] in hedrons: del hedrons[pph[1]]
                    carbons[pph[1]] = pp[1]
                    #update half bond to full bond
                    self._changeHf2FullBond(bonds, pph[0], pph[1], 0) 
                # create full bond
                else: self._createBond(bonds, pph[0], pph[1])      
    
    
    def _logic2Bond(self, carbons, bonds, hedrons, insideAtoms,  \
                                                         newStorage):
        """Processing all bonds having key inside the current selection curve.
            For a bond with the key outside, the value inside the selection 
            curve, we deal with it when we scan the edges of each cell. To 
            make sure no such bonds are lost, we need to enlarge the 
            bounding box at least 1 lattice cell.
        """
        newBonds, newCarbons, newHedrons = newStorage
        
        for a in insideAtoms.keys():
            values = bonds[a]
            newValues = []
            # The key <a> is carbon:
            if carbons.has_key(a):
                if not newCarbons.has_key(a):
                    newCarbons[a] = insideAtoms[a]
                for b in values:
                    if type(b) == type(1): #Full bond
                        # If the carbon inside, keep the bond
                        if insideAtoms.has_key(b):
                            if not newCarbons.has_key(b):
                                newCarbons[b] = insideAtoms[b]
                            newValues += [b]
                        else: # outside carbon, change it to h-bond
                            if not newHedrons.has_key(b):
                                newHedrons[b] = carbons[b]
                            newValues += [(b, 0)]
                    else: # Half bond, keep it
                        if insideAtoms.has_key(b[0]):
                            p = insideAtoms[b[0]]
                        elif hedrons.has_key(b[0]):
                            p = hedrons[b[0]]
                        else: 
                            raise ValueError, (a, b[0])
                        if not newHedrons.has_key(b[0]):
                            newHedrons[b[0]] = p
                        newValues += [b]
            else: # The key <a> is not a carbon
                if not newHedrons.has_key(a):
                    newHedrons[a] = insideAtoms[a]
                for b in values:
                    # Inside h-bond, keep it
                    if insideAtoms.has_key(b[0]):
                        if not newHedrons.has_key(b[0]): 
                            newHedrons[b[0]] = insideAtoms[b[0]]
                        newValues += [b]
            if newValues: newBonds[a] = newValues        
        
    def _removeMarkedAtoms(self, bonds, markedAtoms, 
                                                                                carbons, hedrons):
        """ Remove all carbons that should have been removed because of 
            the new selection curve. Update bonds that have the carbon as 
            key. For a bond who has the carbon as its value, we'll leave them 
            as they are, untill the draw() call. When it finds a value of a bond 
            can't find its carbon position, either remove the bond if it was a 
            half bond or change it to half bond if it was full bond, and find its 
            carbon position in markedAtoms{}"""
        
        for ph in markedAtoms.keys(): 
             if carbons.has_key(ph):
                #print "Remove carbon: ", ph    
                if bonds.has_key(ph):
                    values = bonds[ph]
                    for b in values[:]:
                        if type(b) == type(1):
                            idex = values.index(b)
                            values[idex]  = (b, 1)
                            #print "Post processing: Change full to half bond: ", ph, values[idex]
                        else:
                            values.remove(b)
                            # print "Erase half bond:", ph, b # commented out.  Mark 060205.
                    bonds[ph] = values        
                    if len(values) == 0:
                        del bonds[ph]
                    else:
                        hedrons[ph] = carbons[ph]
                del carbons[ph]
    
    
    def _changeHf2FullBond(self, bonds, key, value, which_in):
            """If there is a half bond, change it to full bond. Otherwise, create
               a new full bond. 
               <which_in>: the atom which exists before. """
            foundHalfBond = False
            
            if bonds.has_key(key):
                values = bonds[key]
                for ii in range(len(values)):
                    if type(values[ii]) == type((1,1)) and values[ii][0] == value:
                        values[ii] = value
                        foundHalfBond = True                
                        break
                if not foundHalfBond: values += [value]
                #bonds[key] = values
            elif not bonds.has_key(key):
                bonds[key] = [value]
                
                                  
    def _createBond(self, dict, key, value, half_in = -1, 
                                                                        new_bond = False):
            """Create a new bond if <new_bond> is True. Otherwise, search if
                there is such a full/half bond, change it appropriately if found. 
                Otherwise, create a new bond.
                If <half_in> == -1, it's a full bond; otherwise, it means a half 
                bond with the atom of <half_in> is inside. """
            if not key in dict:
                if half_in < 0:
                   dict[key] = [value]
                else: dict[key] = [(value, half_in)]
            else:
                values = dict[key]
                if half_in < 0:
                    if new_bond:
                        values += [value]
                    else:
                        found = False
                        for ii in range(len(values)):
                            if type(values[ii]) == type(1):
                                if value == values[ii]:
                                    found = True
                                    break
                            elif value == values[ii][0]:
                                values[ii] = value
                                found = True
                                break
                        if not found:
                            values += [value]     
                else:
                    if new_bond:
                        values +=[(value, half_in)]
                    else:
                        try:
                            idex = values.index((value, half_in))
                        except:
                            values += [(value, half_in)]
                dict[key] = values
                
   
    def changeDisplayMode(self, mode):
        self.dispMode = mode
        self.havelist = 0
        
    def _bondDraw(self, color, p0, p1, carbonAt):
        if self.dispMode == 'Tubes':
            drawcylinder(color, p0, p1, 0.2)
        else:
            if carbonAt < 0:
                drawsphere(color, p0, 0.5, 1)
                drawsphere(color, p1, 0.5, 1)
            elif carbonAt == 0:
                drawsphere(color, p0, 0.5, 1)
                drawsphere(color, p1, 0.2, 1)
            elif carbonAt == 1:
                drawsphere(color, p0, 0.2, 1)
                drawsphere(color, p1, 0.5, 1)
            
            drawline(white, p0, p1)  
                    
   
    def draw(self, win, layerColor):
        """Draw the shape. win, not used, is for consistency among
        drawing functions (and may be used if drawing logic gets
        more sophisticated.

        Find  the bounding box for the curve and check the position of each
        carbon atom in a lattice would occupy for being 'in'
        the shape. A tube representation of the atoms thus selected is
        saved as a GL call list for fast drawing.
        
        This method is only for cookie-cutter mode. --Huaicai
        """
        if 0: 
            self._anotherDraw(layerColor)
            return
        
        markedAtoms = self.markedAtoms
        
        if self.havelist:
            glCallList(self.displist)
            return
        glNewList(self.displist, GL_COMPILE_AND_EXECUTE)
        ColorSorter.start() # grantham 20051205
        try:
            for layer, bonds in self.bondLayers.items():
                color = layerColor[layer]
                self.layeredCurves[layer][-1].draw()
                bonds = self.bondLayers[layer]
                carbons = self.carbonPosDict[layer]
                hedrons = self.hedroPosDict[layer]
                              
                for cK, bList in bonds.items():
                  if carbons.has_key(cK):  p0 = carbons[cK]
                  for b in bList[:]:
                       carbonAt = -1
                       if type(b) == type(1): #Full bond
                           if carbons.has_key(b):
                                p1 = carbons[b]
                           else: #which means the carbon was removed
                                p1 = markedAtoms[b]
                                #print "Carbon was removed: ", b, p1
                                idex = bList.index(b)
                                bList[idex] = (b, 0)
                                hedrons[b] = p1
                                p1 = (p0 + p1) / 2.0
                                carbonAt = 0
                       else: #Half bond
                           carbonAt = b[1]
                           if b[1]: 
                                if carbons.has_key(b[0]): # otherwise, means the carbon has been removed.
                                    p1 = carbons[b[0]]
                                    if hedrons.has_key(cK):
                                        p0 = hedrons[cK]
                                        p0 = (p0 + p1) / 2.0
                                    else: #half bond becomes full bond because of new selection
                                        p0 = carbons[cK]
                                        idex = bList.index(b)
                                        bList[idex] = b[0]
                                else: # remove the half bond
                                    bList.remove(b)
                                    #print "delete half bond: (%d: " %cK, b
                                    if len(bList) == 0: 
                                        del bonds[cK]
                                        break
                                    continue
                           else:
                                if hedrons.has_key(b[0]):
                                    p1 = hedrons[b[0]]
                                    p1 = (p0 + p1) / 2.0
                                else: #Which means half bond becoms full bond because of new selection
                                    p1 = carbons[b[0]]
                                    idex = bList.index(b)
                                    bList[idex] = b[0]
                       
                       self._bondDraw(color, p0, p1, carbonAt)    
                  bonds[cK] = bList
        except:
            # bruce 041028 -- protect against exceptions while making display
            # list, or OpenGL will be left in an unusable state (due to the lack
            # of a matching glEndList) in which any subsequent glNewList is an
            # invalid operation. (Also done in chem.py; see more comments there.)
            print "cK: ", cK
            print_compact_traceback( "bug: exception in shape.draw's displist; ignored: ")
        self.markedAtoms = {}
        ColorSorter.finish() # grantham 20051205
        glEndList()
        self.havelist = 1 # always set this flag, even if exception happened.
    
    def buildChunk(self, assy):
        """Build molecule for the cookies. First, combine bonds from
        all layers together, which may fuse some half bonds to full bonds. """
        from chunk import molecule
        from chem import gensym, atom
        
        numLayers = len(self.bondLayers)
        if numLayers:
            allBonds = {}
            allCarbons = {}
            
            #Copy the bonds, carbons and hedron from the first layer
            for ii in range(numLayers):
                if self.bondLayers.has_key(ii):
                    for bKey, bValue in self.bondLayers[ii].items():
                        allBonds[bKey] = bValue
            
                    del self.bondLayers[ii]
                    break
            
            for carbons in self.carbonPosDict.values():
                for cKey, cValue in carbons.items():
                        allCarbons[cKey] = cValue
                        
            for hedrons in self.hedroPosDict.values():        
                    for hKey, hValue in hedrons.items():
                        allCarbons[hKey] = hValue
                    
            for bonds in self.bondLayers.values():
                for bKey, bValues in bonds.items():
                    if bKey in allBonds:
                        existValues = allBonds[bKey]
                        for bValue in bValues:
                            if type(bValue) == type((1,1)):
                                if bValue[1]: ctValue = (bValue[0], 0)
                                else: ctValue = (bValue[0], 1)
                                if ctValue in existValues:
                                    idex = existValues.index(ctValue)
                                    existValues[idex] = bValue[0]
                                else:
                                    existValues += [bValue]
                            else: existValues += [bValue]
                        allBonds[bKey] = existValues
                    else: allBonds[bKey] = bValues
            
            #print "allbonds: ", allBonds
            #print "allCarbons: ", allCarbons
                
            carbonAtoms = {}
            mol = molecule(assy, gensym("Cookie."))
            for bKey, bBonds in allBonds.items():
                keyHedron = True
                if len(bBonds):
                    for bond in bBonds:
                        if keyHedron:
                            if type(bBonds[0]) == type(1) or (not bBonds[0][1]):
                                if not bKey in carbonAtoms:
                                    keyAtom = atom("C", allCarbons[bKey], mol) 
                                    carbonAtoms[bKey] = keyAtom
                                else: keyAtom = carbonAtoms[bKey]
                                keyHedron = False
                        
                        if keyHedron:    
                            if type(bond) != type((1,1)): raise ValueError, (bKey, bond, bBonds)
                            else:
                                xp = (allCarbons[bKey] + allCarbons[bond[0]])/2.0
                                keyAtom = atom("X", xp, mol)         
                            
                        if type(bond) == type(1) or bond[1]:
                            if type(bond) == type(1):
                                bvKey = bond
                            else: bvKey = bond[0]
                            if not bvKey in carbonAtoms:
                                bondAtom = atom("C", allCarbons[bvKey], mol) 
                                carbonAtoms[bvKey] = bondAtom
                            else: bondAtom = carbonAtoms[bvKey]
                        else:
                            xp = (allCarbons[bKey] + allCarbons[bond[0]])/2.0
                            bondAtom = atom("X", xp, mol)     
                        
                        mol.bond(keyAtom, bondAtom)
        
            if len(mol.atoms) > 0:
            #bruce 050222 comment: much of this is not needed, since mol.pick() does it.
                assy.addmol(mol)
                assy.unpickparts()
                mol.pick()
                assy.mt.mt_update()                