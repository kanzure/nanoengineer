#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""Arbitrary 2D surfaces in 3D space can be represented as:

    f(v) = 0

where f takes a 3D vector v and returns a scalar. For a
sphere, where f(x,y,z) = x**2 + y**2 + z**2 - R**2.

By convention, the points where f(v) < 0 are the interior of the
shape, and the points where f(v) > 0 are the exterior.

We can perform constructive solid geometry of such shapes using
some simple operations. The union of two shapes represented by
functions f1 and f2 is represented by the function f3, where

    f3(v) = min(f1(v), f2(v))

The intersection of two shapes is given by

    f3(v) = max(f1(v), f2(v))

The difference of two shapes is the intersection of the first
shape's interior with the second shape's exterior:

    f3(v) = max(f1(v), -f2(v))

These simple operations will give sharp edges where the two shapes
meet. We will sometimes want the option of smooth, beveled edges.
This will be the case, for example, when we want to tile the
resulting surface with graphene.

I think smooth, beveled edges can be achieved by replacing max and
min with maxb and minb, where

                (  y           if y - x > C
                (
    maxb(x,y) = (  x           if y - x < -C
                (
                (  x + (1/4C) * (y-x+C)**2    otherwise

    minb(x,y) = -maxb(-x, -y)

The smoothness of the edge is controlled by the parameter C. When
C = 0, these are the same as max and min.

To build this into a really useful library, there should be a set
of standard primitives where f and the combiners are implemented in
C. But it should be made to work correctly first.

Some primitives with example functions:

Planar slab   f(x,y,z) = (x-xcenter)**2 - width**2
Cylinder      f(x,y,z) = x**2 + y**2 - R**2
Sphere        f(x,y,z) = x**2 + y**2 + z**2 - R**2
Torus         f(x,y,z) = x**2 + y**2 + z**2 + R2**2 - 2*R1*sqrt(x**2 + y**2)
Saddle        f(x,y,z) = x**2 - y**2
Wall          f(x) = x - x0

Things shapes should always be able to give you: the gradient of the
function at any point, a way to get from any point to a nearby point
on the surface, the unit normal to the surface (this is just the
gradient vector normalized), a bounding box (which must include
representations for infinity).
"""

import os
import random
import types

INFINITY = 1.0e20

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def tuple(self):
        return (self.x, self.y, self.z)
    def __repr__(self):
        return ("<" +
                repr(self.x) + "," +
                repr(self.y) + "," +
                repr(self.z) + ">")
    def __len__(self):
        return 3
    def __abs__(self):
        return self.magsq() ** 0.5
    def magsq(self):
        return self.x**2 + self.y**2 + self.z**2
    def scale(self, k):
        return Vector(k * self.x, k * self.y, k * self.z)
    def normalize(self):
        return self.scale(1.0 / abs(self))
    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y, self.z + v.z)
    def __sub__(self, v):
        return self + (-v)
    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)
    def int(self):
        return Vector(int(self.x), int(self.y), int(self.z))
    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z
    def cross(self, v):
        return Vector(self.y * v.z - self.z * v.y,
                      self.z * v.x - self.x * v.z,
                      self.x * v.y - self.y * v.x)

MININF = Vector(-INFINITY, -INFINITY, -INFINITY)
MAXINF = Vector(INFINITY, INFINITY, INFINITY)

class BoundingBox:
    def __init__(self, vec1=MININF, vec2=MAXINF):
        self.xmin = min(vec1.x, vec2.x)
        self.xmax = max(vec1.x, vec2.x)
        self.ymin = min(vec1.y, vec2.y)
        self.ymax = max(vec1.y, vec2.y)
        self.zmin = min(vec1.z, vec2.z)
        self.zmax = max(vec1.z, vec2.z)
    def __repr__(self):
        return ('<BBox %g %g %g' % (self.xmin, self.ymin, self.zmin) +
                ' %g %g %g>' % (self.xmax, self.ymax, self.zmax))
    def union(self, other):
        xmin = min(self.xmin, other.xmin)
        ymin = min(self.xmin, other.xmin)
        zmin = min(self.xmin, other.xmin)
        xmax = max(self.xmax, other.xmax)
        ymax = max(self.xmax, other.xmax)
        zmax = max(self.xmax, other.xmax)
        return BoundingBox(Vector(xmin, ymin, zmin),
                           Vector(xmax, ymax, zmax))
    def intersection(self, other):
        xmin = max(self.xmin, other.xmin)
        ymin = max(self.ymin, other.ymin)
        zmin = max(self.zmin, other.zmin)
        xmax = max(min(self.xmax, other.xmax), xmin)
        ymax = max(min(self.ymax, other.ymax), ymin)
        zmax = max(min(self.zmax, other.zmax), zmin)
        return BoundingBox(Vector(xmin, ymin, zmin),
                           Vector(xmax, ymax, zmax))
    def difference(self, other):
        return BoundingBox(Vector(self.xmin, self.ymin, self.zmin),
                           Vector(self.xmax, self.ymax, self.zmax))

def maxb(x, y, C=1.0):
    if C < 0.0001:
        return max(x, y)
    diff = y - x
    if diff < -C:
        return x
    elif diff > C:
        return y
    else:
        return x + (diff + C)**2 / (4 * C)

def minb(x, y, C=1.0):
    return -maxb(-x, -y, C)

class Shape:
    def __init__(self, f, bbox):
        self.f = f
        self.bbox = bbox
    def gradient(self, v):
        f = self.f
        h = 1.0e-10
        e = f(v)
        return Vector((f(v + Vector(h, 0, 0)) - e) / h,
                      (f(v + Vector(0, h, 0)) - e) / h,
                      (f(v + Vector(0, 0, h)) - e) / h)
    def union(self, other, C=0.0):
        def f3(v, f1=self.f, f2=other.f, C=C):
            return minb(f1(v), f2(v), C)
        return Shape(f3, self.bbox.union(other.bbox))
    def intersection(self, other, C=0.0):
        def f3(v, f1=self.f, f2=other.f, C=C):
            return maxb(f1(v), f2(v), C)
        return Shape(f3, self.bbox.intersection(other.bbox))
    def difference(self, other, C=0.0):
        def f3(v, f1=self.f, f2=other.f, C=C):
            return maxb(f1(v), -f2(v), C)
        return Shape(f3, self.bbox.difference(other.bbox))
    def shell(self, gridsize):
        print self.bbox
        lst = [ ]
        x = self.bbox.xmin
        while x <= self.bbox.xmax:
            y = self.bbox.ymin
            while y <= self.bbox.ymax:
                z = self.bbox.zmin
                while z <= self.bbox.zmax:
                    if -1.0 <= self.f(Vector(x, y, z)) <= 0.0:
                        lst.append((x, y, z))
                    z += gridsize
                y += gridsize
            x += gridsize
        return lst

def ellipsoid(center, size):
    def f(v):
        return (((v.x - center.x) / size.x) ** 2 +
                ((v.y - center.y) / size.y) ** 2 +
                ((v.z - center.z) / size.z) ** 2  - 1.0)
    bbox = BoundingBox(center - size, center + size)
    return Shape(f, bbox)

def rectangularSolid(center, size, C=0.0):
    def f(v):
        def fx(v, center=center, size=size):
            return (v.x - center.x)**2 - size.x ** 2
        def fy(v, center=center, size=size):
            return (v.y - center.y)**2 - size.y ** 2
        def fz(v, center=center, size=size):
            return (v.z - center.z)**2 - size.z ** 2
        f =  maxb(fx(v), fy(v), C)
        return maxb(f, fz(v), C)
    bbox = BoundingBox(center - size, center + size)
    return Shape(f, bbox)

def cylinder(center, direction, radius):
    """This cylinder is not bounded at the ends. If the direction is along
    one of the coordinate axes, it's possible to have a meaningful bounding
    box in this case, but I'm too lazy to figure it out right now."""
    def f(v, center=center, direction=direction.normalize(), radius=radius):
        return abs((v - center).cross(direction)) - radius
    return Shape(f, BoundingBox())

def closedCylinder(center, direction, radius, length):
    def f1(v, center=center, direction=direction.normalize(), radius=radius):
        return abs((v - center).cross(direction)) - radius
    def f2(v, center=center, direction=direction.normalize(), radius=radius):
        return (v - center).dot(direction)**2 - length**2
    def f(v, f1=f1, f2=f2):
        return max(f1(v), f2(v))
    k = (radius**2 + length**2)**.5
    vec = Vector(-k, -k, -k)
    return Shape(f, BoundingBox(center - vec, center + vec))

def wall(pt, normal):
    def f(v, pt=pt, normal=normal):
        return (v - pt).dot(normal)
    return Shape(f, BoundingBox())

mmpfile = """mmpformat 050920 required; 051103 preferred
kelvin 300
group (View Data)
info opengroup open = True
csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)
csys (LastView) (1.000000, 0.000000, 0.000000, 0.000000) (10.943023) (0.000000, 0.000000, 0.000000) (1.000000)
egroup (View Data)
group (Nanotube)
info opengroup open = True
mol (Nanotube-1) def
%s
egroup (Nanotube)
group (Clipboard)
info opengroup open = False
egroup (Clipboard)
end molecular machine part 1
"""

def writeMmp(shape, filename):
    # fill the solid with densely packaged hydrogen atoms
    # so that we can study it in nE-1, place the atoms in
    # a rectangular grid every half-angstrom
    atoms = shape.shell(0.5)
    atomtext = ''
    i = 1
    for a in atoms:
        atomtext += 'atom %d (1) (%d, %d, %d) def\n' % \
                    (i, int(1000 * a[0]), int(1000 * a[1]), int(1000 * a[2]))
        if (i & 1) == 0 and i > 0:
             atomtext += 'bond1 %d\n' % (i - 1)
        i += 1
    open(filename, "w").write(mmpfile % atomtext[:-1])


e = ellipsoid(Vector(0.0, 0.0, 0.0),
              Vector(2.0, 6.0, 5.0))

e = e.union(closedCylinder(Vector(0.0, 0.0, 0.0),
                           Vector(0.0, 0.0, 1.0),
                           1.3, 8.0))

w = wall(Vector(0.0, 0.0, 0.0), Vector(0.0, 0.0, 1.0))

e = e.intersection(w)

writeMmp(e, '/tmp/shape.mmp')
