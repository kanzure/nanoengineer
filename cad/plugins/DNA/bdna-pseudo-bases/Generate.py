

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
# usage:
#
# python Generate.py adenine > adenine.mmp

import sys
import math

zSpacing = 3180 # 0.1 pm
minorGroveDegrees = 133
baseTwistDegrees = 33.75

sugarRadius = 6760 # pm -- Value from EricD's pdb: 6760
sugarPhosphateDistance = 3640 # Value from EricD's pdb: 3574

baseTwist = math.pi * baseTwistDegrees / 180

if (len(sys.argv) < 2):
    print >>sys.stderr, "must specify base name"
    sys.exit(1)

baseName = sys.argv[1]

prefix = """mmpformat 050920 required; 060421 preferred
kelvin 300
group (View Data)
info opengroup open = True
csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)
csys (LastView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)
egroup (View Data)
group (%s)
info opengroup open = True
mol (%s) def""" % (baseName, baseName)

postfix = """egroup (%s)
end1
group (Clipboard)
info opengroup open = False
egroup (Clipboard)
end molecular machine part %s"""  % (baseName, baseName)

def printAtom(index, type, position, bondedTo):
    print "atom %d (%d) (%d, %d, %d) def" % (index, type, position[0], position[1], position[2])
    if (bondedTo):
        print "bond1 %d" % bondedTo

def rotate(x, y, theta):
    sinTheta = math.sin(theta)
    cosTheta = math.cos(theta)
    return (x * cosTheta - y * sinTheta, x * sinTheta + y * cosTheta)

def midpoint(position1, position2):
    x = (position1[0] + position2[0]) / 2
    y = (position1[1] + position2[1]) / 2
    z = (position1[2] + position2[2]) / 2
    return (x, y, z)

def extendToRadius(position, radius):
    oldR = math.sqrt(position[0] * position[0] + position[1] * position[1])
    factor = radius / oldR
    return (position[0] * factor, position[1] * factor, position[2])

# given the position of a pseudo atom in strand1, return the position
# of the same pseudo atom in strand2
def strand2(position):
    x = position[0]
    y = position[1]
    z = position[2]
    theta = math.pi * (180 - minorGroveDegrees) / 180
    newX, newY = rotate(-x, y, theta)
    return (newX, newY, -z)

sugar = (sugarRadius, 0, 0)

sugar2xy = rotate(sugarRadius, 0, baseTwist)
sugar2 = (sugar2xy[0], sugar2xy[1], zSpacing)

def distance(xyz):
    return math.sqrt(xyz[0] * xyz[0] + xyz[1] * xyz[1] + xyz[2] * xyz[2])

dist = 0
phosphateRadius = sugarRadius
while (dist < sugarPhosphateDistance):
    phosphate = extendToRadius(midpoint(sugar, sugar2), phosphateRadius)
    dist = distance((sugar[0] - phosphate[0], sugar[1] - phosphate[1], sugar[2] - phosphate[2]))
    phosphateRadius += 1
print >>sys.stderr, "phosphateRadius %d" % phosphateRadius
print >>sys.stderr, "dist %d" % dist

phosphate0xy = rotate(phosphate[0], phosphate[1], -baseTwist)
phosphate0 = (phosphate0xy[0], phosphate0xy[1], phosphate[2] - zSpacing)

bondpoint1 = midpoint(phosphate, sugar2)
bondpoint2 = midpoint(phosphate0, sugar)

print prefix

if (baseName == 'end1'):
    # Axis
    printAtom(1, 200, (0, 0, 0), 0) # Ax
    printAtom(2, 204, (0, 0, zSpacing/2), 1) # Ae
    printAtom(3, 0, (0, 0, -zSpacing/2), 1) # Axis bondpoint

    # Strand1
    printAtom(4, 201, sugar, 1) # Ss
    printAtom(5, 205, phosphate, 4) # Pe
    printAtom(6, 0, bondpoint2, 4)

    # Strand2
    printAtom(7, 201, strand2(sugar), 1) # Ss
    printAtom(8, 202, strand2(phosphate), 7) # Pl
    printAtom(9, 0, strand2(bondpoint1), 8)
    printAtom(10, 206, strand2(bondpoint2), 7) # Sh

elif (baseName == 'end2'):
    # Axis
    printAtom(1, 200, (0, 0, 0), 0) # Ax
    printAtom(2, 204, (0, 0, -zSpacing/2), 1) # Ae
    printAtom(3, 0, (0, 0, zSpacing/2), 1) # Axis bondpoint

    # Strand1
    printAtom(4, 201, sugar, 1) # Ss
    printAtom(5, 202, phosphate, 4) # Pl
    printAtom(6, 0, bondpoint1, 5)
    printAtom(7, 206, bondpoint2, 4) # Sh

    # Strand2
    printAtom(8, 201, strand2(sugar), 1) # Ss
    printAtom(9, 205, strand2(phosphate), 8) # Pe
    printAtom(10, 0, strand2(bondpoint2), 8)

else:
    
    # Axis
    printAtom(1, 200, (0, 0, 0), 0) # Ax
    printAtom(2, 0, (0, 0, zSpacing/2), 1) # Axis bondpoint
    printAtom(3, 0, (0, 0, -zSpacing/2), 1) # Axis bondpoint

    # Strand1
    printAtom(4, 201, sugar, 1) # Ss
    printAtom(5, 202, phosphate, 4) # Pl
    printAtom(6, 0, bondpoint1, 5)
    printAtom(7, 0, bondpoint2, 4)

    # Strand2
    printAtom(8, 201, strand2(sugar), 1) # Ss
    printAtom(9, 202, strand2(phosphate), 8) # Pl
    printAtom(10, 0, strand2(bondpoint1), 9)
    printAtom(11, 0, strand2(bondpoint2), 8)

print postfix
