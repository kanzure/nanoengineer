# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

"""
This program can be used to translate cartesian coordinates of PAM5
strut ends into the basis necessary to generate gromacs virtual
particles (which are used to represent the ends of those struts).
First it reads the locations of the three real atoms which represent
and define the base pair plane, and the coordinate basis within that
plane.  Those atoms are the groove (a Gv5 or Gr5 pseudo-atom), which
is at the origin of the virtual particle basis; an Ss5 referred to as
'a'; and another Ss5 referred to as 'b'.  In a normal strand of BDNA,
the two 'a' sugars on a stacked pair of base pairs are farther apart
than the 'b' sugars.  The 'a' sugars are on opposite strands from each
other.

Next, a set of positions of strut ends are read.  These should be
co-planer to the three atoms read in above.  The vector 'va'
represents the displacement from the groove atom to sugar 'a', and
'vb' represents the displacement from the groove atom to sugar 'b'.
The location of the strut end is then (groove + A*va + B*vb).

The three coefficients A, B, and C necessary to reach the strut end
are printed.  The third basis vector is the cross product of the first
two.  For strut ends which are coplaner, C should be negligable.  The
length of the displacement from the read strut end position to the one
calculated based on the new basis is printed as 'error'.  This same
quantity calculated without the C component is printed as 'error2d'.
Both error values should be small.

"""

import sys
import math

from Numeric import array
from LinearAlgebra import inverse

# a nice upgrade would be to read values selected from the NE1 history
# buffer, which look like this:
#
# [X = 20.260] [Y = 7.700] [Z = 3.480]
def readVector():
    line = sys.stdin.readline()
    (xs, ys, zs) = line.strip().split(" ")
    return [float(xs), float(ys), float(zs)]

# most of the routines below can probably be replaced with Numeric
# calls...
def vsub(a, b):
    return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]

def vadd(a, b):
    return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]

def vdot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def vmulk(a, k):
    return [a[0]*k, a[1]*k, a[2]*k]

def vcross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]

print "enter groove position"
g = readVector()
print "enter a"
a = readVector()
print "enter b"
b = readVector()

va = vsub(a, g)
vb = vsub(b, g)
vc = vcross(va, vb)

mat = array([[va[0], vb[0], vc[0]], [va[1], vb[1], vc[1]], [va[2], vb[2], vc[2]]])
inv = inverse(mat)

while (True):
    print "enter vector"
    v = readVector()
    vv = vsub(v, g)

    A = vv[0]*inv[0, 0] + vv[1]*inv[0, 1] + vv[2]*inv[0, 2]
    B = vv[0]*inv[1, 0] + vv[1]*inv[1, 1] + vv[2]*inv[1, 2]
    C = vv[0]*inv[2, 0] + vv[1]*inv[2, 1] + vv[2]*inv[2, 2]

    vcalc1 = vadd(vmulk(va, A), vmulk(vb, B))
    vcalc = vadd(vcalc1, vmulk(vc, C))
    delta = vsub(vv, vcalc)
    error = math.sqrt(vdot(delta, delta))
    delta2d = vsub(vv, vcalc1)
    error2d = math.sqrt(vdot(delta2d, delta2d))

    print "A: %f  B: %f  C: %f  error: %e  error2d: %e" % (A, B, C, error, error2d)
