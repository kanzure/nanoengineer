# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
shape.py -- handle freehand curves for selection and crystal-cutting

@author: Josh, Huaicai, maybe others
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

By Josh. Portions rewritten or extended by at least Bruce & Huaicai,
perhaps others.

Bruce 071215 split classes CrystalShape and Slab into their own modules.

Module classification and refactoring:  [bruce 071215]

Perhaps SelectionShape should also be split out?
The rest seems pretty closely integrated, though it may still be
"vertically integrated" in the sense of combining several kinds of
code, including geometry, graphics_behavior (incl selection),
maybe more.

The public defs are at least get_selCurve_color,
simple_shape_2d, shape, SelectionShape. For now, I'll guess
that I can call all these "graphics_behavior". We'll see.
(This feels more natural than "operations", though for that
I'd be more confident that a package import cycle was unlikely.)
"""

from Numeric import array, zeros, maximum, minimum, ceil, dot, floor

from geometry.VQT import A, vlen, V

from graphics.drawing.drawers import drawrectangle
from graphics.drawing.CS_draw_primitives import drawline

from utilities.constants import black
from utilities.constants import DELETE_SELECTION
from utilities.constants import SUBTRACT_FROM_SELECTION
from utilities.constants import ADD_TO_SELECTION
from utilities.constants import START_NEW_SELECTION
from utilities.constants import white
from utilities.constants import red

from utilities.debug import print_compact_traceback
from utilities import debug_flags 

import foundation.env as env
##from utilities.constants import colors_differ_sufficiently
from utilities.prefs_constants import DarkBackgroundContrastColor_prefs_key
from utilities.prefs_constants import LightBackgroundContrastColor_prefs_key

from geometry.BoundingBox import BBox

def get_selCurve_color(selSense, bgcolor = white):
    """
    [public]
    Returns line color of the selection curve. 
    Returns <black> for light colored backgrounds (and Sky Blue).
    Returns <white> for dark colored backgrounds.
    Returns <red> if <selSense> is DELETE_SELECTION mode.
    """
    if selSense == DELETE_SELECTION: 
        return red
    
    # Problems with this when the user picks a light gradient (i.e. Blue Sky)
    # but the bgcolor is a dark color. Simply returning 
    # "DarkBackgroundContrastColor_prefs_key" works fine. Mark 2008-07-10
    #if colors_differ_sufficiently(bgcolor, black):
    #    return env.prefs[DarkBackgroundContrastColor_prefs_key]
    #else:
    #    return env.prefs[LightBackgroundContrastColor_prefs_key]
    
    return env.prefs[DarkBackgroundContrastColor_prefs_key]

def fill(mat, p, dir): # TODO: rename (less generic so searchable), and perhaps make private
    """
    [helper for class curve; unknown whether it has other uses]
    
    Fill a curve drawn in matrix mat, as 1's over a background of 0's, with 1's.
    p is V(i, j) of a point to fill from. dir is 1 or -1 for the
    standard recursive fill algorithm.

    Here is an explanation of how this is used and how it works then, by Huaicai:
    This function is used to fill the area between the rectangle bounding box and the boundary
    of the curve with 1's. The bounding box is extended by (lower left corner -2, right top corner + 2). 
    The curve boundary is filled with 1's. So mat[1,:] = 0, mat[-1,:] = 0, mat[:, 1] = 0;
    mat[:, -1]=0, which means the area is connected. If we start from mat[1, 1], dir = 1, then we scan the 
    first line from left to right. If it's 0, fill it as 1 until we touch 1. For each element in the line, we also 
    check it's neighbor above and below. For the neighbor elements, if the neighbor touches 1 but 
    previous neighbor is 0, then scan the neighbor line in the reverse order. I think this algorithm is better
    than the simple recursive flood filling algorithm. The seed mat[1, 1] is always inside the area, and 
    most probably this filling area is smaller than that inside the curve. I think it also reduces repeated 
    checking/filling of the classical algorithm.
    """
    if mat[p]:
        return
    up = dn = 0
    o1 = array([1, 0])
    od = array([0, dir])
    while not mat[p - od]: p -= od
    while not mat[p]:
        mat[p] = 1
        if mat[p - o1]:
            if up:
                fill(mat, p - [1, dir], -dir)
                up = 0
        else: up = 1
        if mat[p + o1]:
            if dn:
                fill(mat, p + [1, -dir], -dir)
                dn = 0
        else: dn = 1
        p += od
    fill(mat, p - od + o1, -dir)
    fill(mat, p - od - o1, -dir) # note: we have (probably) seen recursion limit errors from this line. [bruce 070605 comment]


#bruce 041214 made a common superclass for curve and rectangle classes,
# so I can fix some bugs in a single place, and since there's a
# lot of common code. Some of it could be moved into class shape (for more
# efficiency when several curves in one shape), but I didn't do that, since
# I'm not sure we'll always want to depend on that agreement of coord systems
# for everything in one shape.

class simple_shape_2d: 
    """
    common code for selection curve and selection rectangle;
    also used in CrystalShape.py
    """
    def __init__(self, shp, ptlist, origin, selSense, opts):
        """
        ptlist is a list of 3d points describing a selection
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
        """
        Construct the 3d bounding box for the area
        """  
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
            self.bbox = BBox(V(bboxlo, bboxhi), V(x, y), self.slab)
        else:
            self.bbox = BBox()
        return

    def project_2d_noeyeball(self, pt):
        """
        Bruce: Project a point into our plane (ignoring eyeball). Warning: arbitrary origin!
           
        Huaicai 4/20/05: This is just to project pt into a 2d coordinate 
        system (self.right, self.up) on a plane through pt and parallel to the screen 
        plane. For perspective projection, (x, y) on this plane is different than that on the plane 
        through pov.
        """
        x, y = self.right, self.up
        return V(dot(pt, x), dot(pt, y))

    def project_2d(self, pt):
        """
        like project_2d_noeyeball, but take into account self.eyeball;
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
                if debug_flags.atom_debug:
                    print_compact_traceback("atom_debug: ignoring math error for point near eyeball: ")
                return None
            p += pfix
        return p

    def isin_bbox(self, pt):
        """
        say whether a point is in the optional slab, and 2d bbox (uses eyeball)
        """
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
    """
    selection rectangle
    """
    def __init__(self, shp, pt1, pt2, origin, selSense, **opts):
        simple_shape_2d.__init__( self, shp, [pt1, pt2], origin, selSense, opts)        
    def isin(self, pt):
        return self.isin_bbox(pt)
    def draw(self):
        """
        Draw the rectangle
        """
        color = get_selCurve_color(self.selSense)
        drawrectangle(self.ptlist[0], self.ptlist[1], self.right, self.up, color)
    pass


class curve(simple_shape_2d): # bruce 041214 factored out simple_shape_2d
    """
    Represents a single closed curve in 3-space, projected to a
    specified plane.
    """
    def __init__(self, shp, ptlist, origin, selSense, **opts):
        """
        ptlist is a list of 3d points describing a selection.
        origin is the center of view, and normal gives the direction
        of the line of light. Form a structure for telling whether
        arbitrary points fall inside the curve from the point of view.
        """
        # bruce 041214 rewrote some of this method
        simple_shape_2d.__init__( self, shp, ptlist, origin, selSense, opts)
        
        # bounding rectangle, in integers (scaled 8 to the angstrom)
        ibbhi = array(map(int, ceil(8 * self.bboxhi)+2))
        ibblo = array(map(int, floor(8 * self.bboxlo)-2))
        bboxlo = self.bboxlo
        
        # draw the curve in these matrices and fill it
        # [bruce 041214 adds this comment: this might be correct but it's very
        # inefficient -- we should do it geometrically someday. #e]
        mat = zeros(ibbhi - ibblo)
        mat1 = zeros(ibbhi - ibblo)
        mat1[0,:] = 1
        mat1[-1,:] = 1
        mat1[:,0] = 1
        mat1[:,-1] = 1
        pt2d = self.pt2d
        pt0 = pt2d[0]
        for pt in pt2d[1:]:
            l = ceil(vlen(pt - pt0)*8)
            if l<0.01: continue
            v=(pt - pt0)/l
            for i in range(1 + int(l)):
                ij = 2 + array(map(int, floor((pt0 + v * i - bboxlo)*8)))
                mat[ij]=1
            pt0 = pt
        mat1 += mat
        
        fill(mat1, array([1, 1]),1)
        mat1 -= mat #Which means boundary line is counted as inside the shape.
        # boolean raster of filled-in shape
        self.matrix = mat1  ## For any element inside the matrix, if it is 0, then it's inside.
        # where matrix[0, 0] is in x, y space
        self.matbase = ibblo

        # axes of the plane; only used for debugging
        self.x = self.right
        self.y = self.up
        self.z = self.normal

    def isin(self, pt):
        """
        Project pt onto the curve's plane and return 1 if it falls
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
        ij = map(int, p * 8)-self.matbase
        return not self.matrix[ij]

    def xdraw(self):
        """
        draw the actual grid of the matrix in 3-space.
        Used for debugging only.
        """
        col = (0.0, 0.0, 0.0)
        dx = self.x/8.0
        dy = self.y/8.0
        for i in range(self.matrix.shape[0]):
            for j in range(self.matrix.shape[1]):
                if not self.matrix[i, j]:
                    p = (V(i, j)+self.matbase)/8.0
                    p = p[0]*self.x + p[1]*self.y + self.z
                    drawline(col, p, p + dx + dy)
                    drawline(col, p + dx, p + dy)

    def draw(self):
        """
        Draw two projections of the curve at the limits of the
        thickness that defines the crystal volume.
        The commented code is for debugging.
        [bruce 041214 adds comment: the code looks like it
        only draws one projection.]
        """
        color = get_selCurve_color(self.selSense)
        pl = zip(self.ptlist[:-1],self.ptlist[1:])
        for p in pl:
            drawline(color, p[0],p[1])
        
        # for debugging
        #self.bbox.draw()
        #if self.eyeball:
        #    for p in self.ptlist:
        #        drawline(red, self.eyeball, p)
        #drawline(white, self.org, self.org + 10 * self.z)
        #drawline(white, self.org, self.org + 10 * self.x)
        #drawline(white, self.org, self.org + 10 * self.y)

    pass # end of class curve

class shape:
    """
    Represents a sequence of curves, each of which may be
    additive or subtractive.
    [This class should be renamed, since there is also an unrelated
    Numeric function called shape().]
    """
    def __init__(self, right, up, normal):
        """
        A shape is a set of curves defining the whole cutout.
        """
        self.curves = []
        self.bbox = BBox()

        # These arguments are required to be orthonormal:
        self.right = right
        self.up = up
        self.normal = normal
    
    def pickline(self, ptlist, origin, selSense, **xx):
        """
        Add a new curve to the shape.
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

# ==

class SelectionShape(shape): # review: split this into its own file? [bruce 071215 Q]
    """
    This is used to construct shape for atoms/chunks selection.
    A curve or rectangle will be created, which is used as an area
    selection of all the atoms/chunks
    """
    def pickline(self, ptlist, origin, selSense, **xx):
        self.curve = shape.pickline(self, ptlist, origin, selSense, **xx)

    def pickrect(self, pt1, pt2, org, selSense, **xx):
        self.curve = shape.pickrect(self, pt1, pt2, org, selSense, **xx)
        
    def select(self, assy):
        """
        Loop thru all the atoms that are visible and select any
        that are 'in' the shape, ignoring the thickness parameter.
        """
        #bruce 041214 conditioned this on a.visible() to fix part of bug 235;
        # also added .hidden check to the last of 3 cases. Left everything else
        # as I found it. This code ought to be cleaned up to make it clear that
        # it uses the same way of finding the selection-set of atoms, for all
        # three selSense cases in each of select and partselect. If anyone adds
        # back any differences, this needs to be explained and justified in a
        # comment; lacking that, any such differences should be considered bugs.
        #
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
                assy.unpickall_in_GLPane() # was unpickatoms and unpickparts [bruce 060721]
##                    assy.unpickparts() # Fixed bug 606, partial fix for bug 365.  Mark 050713.
##                    assy.unpickatoms() # Fixed bug 1598. Mark 060303.
            self._atomsSelect(assy)   
    
    def _atomsSelect(self, assy):
        """
        Select all atoms inside the shape according to its selection selSense.
        """    
        c = self.curve
        if c.selSense == ADD_TO_SELECTION:
            for mol in assy.molecules:
                if mol.hidden:
                    continue
                disp = mol.get_dispdef()
                for a in mol.atoms.itervalues():
                    if c.isin(a.posn()) and a.visible(disp):
                        a.pick()
        elif c.selSense == START_NEW_SELECTION:
            for mol in assy.molecules:
                if mol.hidden:
                    continue
                disp = mol.get_dispdef()
                for a in mol.atoms.itervalues():
                    if c.isin(a.posn()) and a.visible(disp):
                        a.pick()
                    else:
                        a.unpick()
        elif c.selSense == SUBTRACT_FROM_SELECTION:
            for a in assy.selatoms.values():
                if a.molecule.hidden:
                    continue #bruce 041214
                if c.isin(a.posn()) and a.visible():
                    a.unpick()
        elif c.selSense == DELETE_SELECTION:
            todo = []
            for mol in assy.molecules:
                if mol.hidden:
                    continue
                disp = mol.get_dispdef()
                for a in mol.atoms.itervalues():
                    if c.isin(a.posn()) and a.visible(disp):
                        if a.is_singlet():
                            continue
                        todo.append(a)
            for a in todo[:]:
                if a.filtered():
                    continue
                a.kill()
        else:
            print "Error in shape._atomsSelect(): Invalid selSense =", c.selSense
            #& debug method. mark 060211.

    def _chunksSelect(self, assy):
        """
        Loop thru all the atoms that are visible and select any
        that are 'in' the shape, ignoring the thickness parameter.
        pick the parts that contain them
        """
        #bruce 041214 conditioned this on a.visible() to fix part of bug 235;
        # also added .hidden check to the last of 3 cases. Same in self.select().
        c = self.curve
        if c.selSense == START_NEW_SELECTION:
            # drag selection: unselect any selected Chunk not in the area, 
            # modified by Huaicai to fix the selection bug 10/05/04
            for m in assy.selmols[:]:
                m.unpick()
                        
        if c.selSense == ADD_TO_SELECTION or c.selSense == START_NEW_SELECTION:
            for mol in assy.molecules:
                if mol.hidden:
                    continue
                disp = mol.get_dispdef()
                for a in mol.atoms.itervalues():
                    if c.isin(a.posn()) and a.visible(disp):
                        a.molecule.pick()
                        break

        if c.selSense == SUBTRACT_FROM_SELECTION:
            for m in assy.selmols[:]:
                if m.hidden:
                    continue #bruce 041214
                disp = m.get_dispdef()
                for a in m.atoms.itervalues():
                    if c.isin(a.posn()) and a.visible(disp):
                        m.unpick()
                        break   
                                
        if c.selSense == DELETE_SELECTION: # mark 060220.
            todo = []
            for mol in assy.molecules:
                if mol.hidden:
                    continue
                disp = mol.get_dispdef()
                for a in mol.atoms.itervalues():
                    #bruce 060405 comment/bugfix: this use of itervalues looked dangerous (since mol was killed inside the loop),
                    # but since the iterator is not continued after that, I suppose it was safe (purely a guess).
                    # It would be safer (or more obviously safe) to build up a todo list of mols to kill after the loop.
                    # More importantly, assy.molecules was not copied in the outer loop -- that could be a serious bug,
                    # if it's incrementally modified. I'm fixing that now, using the todo list.
                    if c.isin(a.posn()) and a.visible(disp):
                        ## a.molecule.kill()
                        todo.append(mol) #bruce 060405 bugfix
                        break
            for mol in todo:
                mol.kill()
        return
    
    def findObjInside(self, assy):
        """
        Find atoms/chunks that are inside the shape.
        """
        rst = []
        
        c = self.curve
        
        if assy.selwhat: ##Chunks
           rstMol = {} 
           for mol in assy.molecules:
                if mol.hidden:
                    continue
                disp = mol.get_dispdef()
                for a in mol.atoms.itervalues():
                    if c.isin(a.posn()) and a.visible(disp):
                            rstMol[id(a.molecule)] = a.molecule
                            break 
           rst.extend(rstMol.itervalues())
        else: ##Atoms
           for mol in assy.molecules:
                if mol.hidden:
                    continue
                disp = mol.get_dispdef()
                for a in mol.atoms.itervalues():
                   if c.isin(a.posn()) and a.visible(disp):
                     rst += [a] 
        return rst
    
    pass # end of class SelectionShape

# end
