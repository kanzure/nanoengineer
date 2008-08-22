# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
BoundingBox.py

@author: Josh
@version:$Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

This class BBox was originally in shape.py. Moved to its own module on 
2007-10-17.

Module classification: [bruce 080103]

This is mainly geometry, so I will put it there ("optimistically"),
even though it also includes graphics code, and hardcoded constants
(at least 1.8 and 10.0, as of now) whose values come from considerations
about its use for our model objects (atoms).
"""

from graphics.drawing.drawers import drawwirebox
from Numeric import add, subtract, sqrt 
from Numeric import maximum, minimum, dot

from geometry.VQT import V, A, cat
from utilities.constants import black

# piotr 080402 moved this to constants, default value = 1.8A 
from utilities.constants import BBOX_MARGIN

class BBox:
    """
    implement a bounding box in 3-space
    BBox(PointList)
    BBox(point1, point2)
    BBox(2dpointpair, 3dx&y, slab)
    data is stored hi, lo so we can use subtract.reduce
    """
    def __init__(self, point1 = None, point2 = None, slab = None):
        # Huaicai 4/23/05: added some comments below to help understand the code.
        if slab:
            # convert from 2d (x, y) coordinates into its 3d world (x, y, 0) 
            #coordinates(the lower-left and upper-right corner). 
            #In another word, the 3d coordinates minus the z offset of the plane
            x = dot(A(point1), A(point2))
            # Get the vector from upper-right point to the lower-left point
            dx = subtract.reduce(x)
            # Get the upper-left and lower right corner points
            oc = x[1] + V(point2[0]*dot(dx,point2[0]), 
                          point2[1]*dot(dx,point2[1]))
            # Get the four 3d cooridinates on the bottom crystal-cutting plane
            sq1 = cat(x,oc) + slab.normal*dot(slab.point, slab.normal)
            # transfer the above 4 3d coordinates in parallel to get that on
            #the top plane, put them together
            sq1 = cat(sq1, sq1+slab.thickness*slab.normal)
            self.data = V(maximum.reduce(sq1), minimum.reduce(sq1))
        elif point2:
            # just 2 3d points
            self.data = V(maximum(point1, point2), minimum(point1, point2))
        elif point1:
            # list of points: could be 2d or 3d?  +/- 1.8 to make the bounding 
            #box enclose the vDw ball of an atom?
            self.data = V(maximum.reduce(point1) + BBOX_MARGIN, 
                          minimum.reduce(point1) - BBOX_MARGIN)
        else:
            # a null bbox
            self.data = None


    def add(self, point):
        vl = cat(self.data, point)
        self.data = V(maximum.reduce(vl), minimum.reduce(vl))

    def merge(self, bbox):
        if self.data and bbox.data:
            self.add(bbox.data)
        else:
            self.data = bbox.data

    def draw(self):
        if self.data:
            drawwirebox(black, add.reduce(self.data)/2,
                        subtract.reduce(self.data)/2)

    def center(self):
        if self.data:
            return add.reduce(self.data)/2.0
        else:
            return V(0, 0, 0)

    def isin(self, pt):
        return (minimum(pt,self.data[1]) == self.data[1] and
                maximum(pt,self.data[0]) == self.data[0])

    def scale(self):
        """
        Return the maximum distance from self's geometric center
        to any point in self (i.e. the corner-center distance).

        Note: This is the radius of self's bounding sphere,
        which is as large as, and usually larger than, the
        bounding sphere of self's contents.

        Note: self's box dimensions are slightly larger than
        needed to enclose its data, due to hardcoded constants
        in its construction methods. [TODO: document, make optional]
        """
        if not self.data: return 10.0
        #x=1.2*maximum.reduce(subtract.reduce(self.data))

        dd = 0.5*subtract.reduce(self.data)
            # dd = halfwidths in each dimension (x,y,z)
        x = sqrt(dd[0]*dd[0] + dd[1]*dd[1] + dd[2]*dd[2])
            # x = half-diameter of bounding sphere of self
        #return max(x, 2.0)
        return x

    def copy(self, offset = None):
        if offset:
            return BBox(self.data[0] + offset, self.data[1] + offset)
        return BBox(self.data[0], self.data[1])

    pass

# end
