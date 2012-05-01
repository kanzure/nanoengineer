# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Slab.py - a slab in space, with a 3d-point-in-slab test

@author: not sure; could be found from svn/cvs annotate
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

Module classification: geometry

Note: bruce 071215 split class Slab our of shape.py into its own module.
"""

from numpy import dot

from geometry.VQT import norm

class Slab:
    """
    defines a slab in space which can tell you if a point is in the slab
    """
    def __init__(self, point, normal, thickness):
        self.point = point
        self.normal = norm(normal)
        self.thickness = thickness

    def isin(self, point):
        d = dot(point - self.point, self.normal)
        return d >= 0 and d <= self.thickness

    def __str__(self):
        return '<slab of '+`self.thickness`+' at '+`self.point`+'>'

    pass
    
# end
