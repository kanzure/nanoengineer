#!/usr/bin/env python

# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

"""
Transform coordinates from one basis set to another.

The original purpose of this program is to transform standard DNA
coordinates, such as those used by the 3DNA program, into coefficients
for creating GROMACS virtual sites.  It should be general enough to be
able to transform any 3D coordinate frame into another 3D frame.

You need to specify the translation of the origin from one frame to
the other, and the coordinates of the three basis vectors of one frame
in terms of the other.

For the DNA case, the vectors are all 2D, so we ignore Z.

The source frame is a rectalinear frame (basis vectors are
orthonormal).  The origin sits on the central axis of the DNA duplex,
at the location which would be occupied by an Ax3 pseudo-atom.
Positive X points towards the Gv5 major groove pseudo atom.  Positive
Y is orthogonal to X, in the plane of the two Ss5 pseudo atoms, and on
the side of the Ss5 pseudo atom which is closer to it's brother in the
neighboring base pair.

In the neighboring base pair, this frame would be rotated around Z
(based on the duplex twist), and rotated 180 degrees around X, so the
Z axes of the neighboring frames are anti-parallel.

The destination frame is neither orthogonal nor normalized.  The
origin is at the Gv5 pseudo atom.  The basis vectors will be called P
and Q.  Each extends from the origin to one of the Ss5 pseudo atoms in
the same base pair.  P in the negative Y direction, and Q in the
positive Y direction.

  Q
   \
    \
   y \
   ox O
     /
    /
   /
  P

 or, after translating the origins to be coincident:

  Q
   \  y
    \ |
     \|
      O--x
     /
    /
   /
  P

"""

import sys

# Coordinates of the destination origin in the source frame
origin = [ 0.4996, 0.0, 0.0 ]

x_g = 0.75075
y_m = 0.53745

# Coordinates of the source vector (1,0,0) in the destination frame
e1 = [ -0.5/x_g, -0.5/x_g, 0.0 ]

# Coordinates of the source vector (0,1,0) in the destination frame
e2 = [ -0.5/y_m, 0.5/y_m, 0.0 ]

# Coordinates of the source vector (0,0,1) in the destination frame
e3 = [ 0.0, 0.0, 1.0 ]

while True:
    line = sys.stdin.readline()
    if (not line):
        break
    splitLine = line.split()
    xi = float(splitLine[0])
    yi = float(splitLine[1])
    #zi = float(splitLine[2])
    zi = 0

    x = xi - origin[0]
    y = yi - origin[1]
    z = zi - origin[2]

    p = x * e1[0] + y * e2[0] + z * e3[0]
    q = x * e1[1] + y * e2[1] + z * e3[1]
    r = x * e1[2] + y * e2[2] + z * e3[2]

    #print "(%f %f %f) -> (%f %f %f) -> (%f %f %f)" % (xi, yi, zi, x, y, z, p, q, r)
    print "(%f %f) -> (%f %f) -> (%f %f)" % (xi, yi, x, y, p, q)
