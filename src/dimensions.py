# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
dimensions.py - code to help draw dimensions

$Id$

History (most recent first):

wware 060324 - created this file
"""

__author__ = "Will"

import math
from VQT import *
from drawer import *
from debug import *

"""
The font is a vector-drawing thing. The entries in the font are
integer coordinates. The drawing space is 5x7.
"""

_font = {
    'X': ((0, 0),
          (3, 6),
          (1, 2),
          (2, 2),
          (0, 6),
          (3, 0)),
    '.': ((1, 0),
          (2, 0),
          (2, 1),
          (1, 1),
          (1, 0)),
    '/': ((0, 0),
          (3, 6)),
    '-': ((0, 3),
          (3, 3)),
    '0': ((1, 0),
          (0, 1),
          (0, 5),
          (1, 6),
          (2, 6),
          (3, 5),
          (3, 1),
          (2, 0),
          (1, 0)),
    '1': ((1, 0),
          (3, 0),
          (2, 0),
          (2, 6),
          (1, 5)),
    '2': ((0, 5),
          (1, 6),
          (2, 6),
          (3, 5),
          (3, 3),
          (0, 1),
          (0, 0),
          (3, 0)),
    '3': ((0, 5),
          (1, 6),
          (2, 6),
          (3, 5),
          (3, 4),
          (2, 3),
          (1, 3),
          (2, 3),
          (3, 2),
          (3, 1),
          (2, 0),
          (1, 0),
          (0, 1)),
    '4': ((1, 6),
          (0, 3),
          (3, 3),
          (3, 6),
          (3, 0)),
    '5': ((3, 6),
          (0, 6),
          (0, 3),
          (2, 3),
          (3, 2),
          (3, 1),
          (2, 0),
          (0, 0)),
    '6': ((2, 6),
          (0, 4),
          (0, 1),
          (1, 0),
          (2, 0),
          (3, 1),
          (3, 2),
          (2, 3),
          (1, 3),
          (0, 2)),
    '7': ((0, 6),
          (3, 6),
          (1, 0)),
    '8': ((1, 3),
          (0, 4),
          (0, 5),
          (1, 6),
          (2, 6),
          (3, 5),
          (3, 4),
          (2, 3),
          (1, 3),
          (0, 2),
          (0, 1),
          (1, 0),
          (2, 0),
          (3, 1),
          (3, 2),
          (2, 3)),
    '9': ((1, 0),
          (3, 3),
          (3, 5),
          (2, 6),
          (1, 6),
          (0, 5),
          (0, 4),
          (1, 3),
          (2, 3),
          (3, 4)),
    }

def drawCharacter(char, color, xfm):
    if _font.has_key(char):
        seq = _font[char]
    else:
        seq = _font['X']
    seq = map(lambda tpl,xfm=xfm: apply(xfm,tpl), seq)
    for i in range(len(seq) - 1):
        drawline(color, seq[i], seq[i+1])

def drawString(str, color, xfm):
    for i in range(len(str)):
        def xfm2(x, y):
            return xfm(x + i * 5, y)
        drawCharacter(str[i], color, xfm2)

class CylindricalCoordinates:
    def __init__(self, point0, point1, right, up):
        # u and v and zn are unit vectors
        # z is NOT a unit vector
        self.p0 = point0
        self.p1 = point1
        self.z = z = point1 - point0
        zlen = vlen(z)
        if zlen:
            self.zinv = 1.0 / zlen
        else:
            self.zinv = 1.
        self.zn = zn = norm(z)
        u = cross(cross(z, up), z)
        if vlen(u) < 1.0e-4:
            u = cross(cross(z, right), z)
        u = norm(u)
        v = cross(zn, u)
        if dot(u, up) < 0:
            u, v = -u, -v
        self.u = u
        self.v = v
    def rtz(self, pt):
        d = pt - self.p0
        z = dot(d, self.zn)
        d = d - z * self.zn
        r = vlen(d)
        theta = arctan2(dot(d, self.v), dot(d, self.u))
        return Numeric.array((r, theta, z), 'd')
    def xyz(self, rtz):
        r, t, z = rtz
        du = (r * cos(t)) * self.u
        dv = (r * sin(t)) * self.v
        dz = z * self.z
        return self.p0 + du + dv + dz

def drawLinearDimension(owner, color, right, up, p0, p1, text):
    csys = CylindricalCoordinates(p0, p1, right, up)
    e0 = csys.xyz((10, 0, 0))
    e1 = csys.xyz((10, 0, 1))
    drawline(color, p0, e0)
    drawline(color, p1, e1)
    v0 = csys.xyz((9.5, 0, 0))
    v1 = csys.xyz((9.5, 0, 1))
    drawline(color, v0, v1)
    # draw arrowheads at the ends
    a1, a2 = 0.25, 1.0 * csys.zinv
    arrow00 = csys.xyz((9.5+a1, 0, a2))
    arrow01 = csys.xyz((9.5-a1, 0, a2))
    drawline(color, v0, arrow00)
    drawline(color, v0, arrow01)
    arrow10 = csys.xyz((9.5+a1, 0, 1-a2))
    arrow11 = csys.xyz((9.5-a1, 0, 1-a2))
    drawline(color, v1, arrow10)
    drawline(color, v1, arrow11)
    # draw the text for the numerical measurement, make
    # sure it goes from left to right
    if dot(csys.z, right) > 0:
        def tfm(x, y):
            return csys.xyz((10 + y / 7., 0, 0.1 + csys.zinv * x / 5.))
    else:
        def tfm(x, y):
            return csys.xyz((10 + y / 7., 0, 0.9 - csys.zinv * x / 5.))
    drawString(text, color, tfm)
