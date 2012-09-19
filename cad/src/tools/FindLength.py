#!/usr/bin/env python

# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

"""
Find the length of a vector, given the coordinates of the two ends.
The 2D vectors are offset by a constant Z amount, and one is rotated
by a constant angle.

"""

import sys
import math

dtheta = -36.0 * math.pi / 180.0

s = math.sin(dtheta)
c = math.cos(dtheta)

while True:
    line = sys.stdin.readline()
    if (not line):
        break
    splitLine = line.split()
    x1 = float(splitLine[0])
    y1 = float(splitLine[1])

    x2i = float(splitLine[2])
    y2i = float(splitLine[3])

    x2 = x2i * c - y2i * s
    y2 = x2i * s + y2i * c

    dx = x1 - x2
    dy = y1 - y2
    dz = 0.318

    length = math.sqrt(dx * dx + dy * dy + dz * dz)

    print "(%f %f) -> (%f %f) %6.2f" % (x1, y1, x2, y2, length * 1000)
