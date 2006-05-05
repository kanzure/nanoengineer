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


class Font3D:

    WIDTH = 5
    HEIGHT = 7
    SCALE = 0.08

    def __init__(self, xoff, yoff, right, up, rot90):
        if rot90:
            self.xflip = xflip = right[1] < 0.0
            self.yflip = yflip = up[0] < 0.0
        else:
            self.xflip = xflip = right[0] < 0.0
            self.yflip = yflip = up[1] < 0.0

        xgap = self.WIDTH
        halfheight = 0.5 * self.HEIGHT

        if xflip:
            xgap *= -self.SCALE
            def fx(x): return self.SCALE * (self.WIDTH - 1 - x)
        else:
            xgap *= self.SCALE
            def fx(x): return self.SCALE * x

        if yflip:
            def fy(y): return self.SCALE * (self.HEIGHT - 1 - y)
        else:
            def fy(y): return self.SCALE * y

        if rot90:
            yoff += xgap
            xoff -= halfheight * self.SCALE
            def tfm(x, y, yoff1):
                return Numeric.array((xoff + yoff1 + fy(y), yoff + fx(x), 0.0))
        else:
            xoff += xgap
            yoff -= halfheight * self.SCALE
            def tfm(x, y, yoff1):
                return Numeric.array((xoff + fx(x), yoff + yoff1 + fy(y), 0.0))
        self.tfm = tfm

    def drawCharacter(self, ch, tfm):
        from dimensions import _font
        if _font.has_key(ch):
            seq = _font[ch]
        else:
            seq = _font['X']
        seq = map(lambda tpl: apply(tfm,tpl), seq)
        for i in range(len(seq) - 1):
            pos1, pos2 = seq[i], seq[i+1]
            # somebody has already taken care of glBegin(GL_LINES)
            glVertex(pos1[0], pos1[1], pos1[2])
            glVertex(pos2[0], pos2[1], pos2[2])
            # somebody has already taken care of glEnd()

    def drawString(self, str, yoff):
        n = len(str)
        if self.xflip:
            def fi(i): return i - (n + 1)
        else:
            def fi(i): return i
        for i in range(n):
            def tfm2(x, y):
                return self.tfm(x + 5 * fi(i), y, yoff)
            self.drawCharacter(str[i], tfm2)


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
    def __init__(self, point0, z, uhint, uhint2):
        # u and v and zn are unit vectors
        # z is NOT a unit vector
        self.p0 = point0
        self.p1 = point1 = point0 + z
        self.z = z
        zlen = vlen(z)
        if zlen:
            self.zinv = 1.0 / zlen
        else:
            self.zinv = 1.
        self.zn = zn = norm(z)
        u = norm(uhint - (dot(uhint, z) / zlen**2) * z)
        if vlen(u) < 1.0e-4:
            u = norm(uhint2 - (dot(uhint2, z) / zlen**2) * z)
        v = cross(zn, u)
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
    def drawLine(self, color, rtz1, rtz2):
        drawline(color, self.xyz(rtz1), self.xyz(rtz2))
    def drawArc(self, color, r, theta1, theta2, z):
        n = int((30 / pi) * fabs(theta2 - theta1) + 1)
        step = (1.0 * theta2 - theta1) / n
        for i in range(n):
            t = theta1 + step
            self.drawLine(color, (r, theta1, z), (r, t, z))
            theta1 = t

def drawLinearDimension(color, right, up, p0, p1, text):
    csys = CylindricalCoordinates(p0, p1 - p0, up, right)
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

def drawAngleDimension(color, right, up, p0, p1, p2, text):
    h = 1.0e-3
    z = cross(p0 - p1, p2 - p1)
    r = max(vlen(p0 - p1), vlen(p2 - p1))
    csys = CylindricalCoordinates(p1, z, up, right)
    theta1 = csys.rtz(p0)[1]
    theta2 = csys.rtz(p2)[1]
    if theta2 < theta1 - math.pi:
        theta2 += 2 * math.pi
    elif theta2 > theta1 + math.pi:
        theta2 -= 2 * math.pi
    if theta2 < theta1:
        theta1, theta2 = theta2, theta1
    e0 = csys.xyz((r + 10, theta1, 0))
    e1 = csys.xyz((r + 10, theta2, 0))
    drawline(color, p1, e0)
    drawline(color, p1, e1)
    csys.drawArc(color, r + 9.5, theta1, theta2, 0)
    # draw some arrowheads
    e00 = csys.xyz((r + 9.5, theta1, 0))
    e10 = csys.xyz((r + 9.5, theta2, 0))
    e0a = norm(csys.xyz((r + 9.5, theta1 + h, 0)) - e00)
    e0b = norm(csys.xyz((r + 10.5, theta1, 0)) - e00)
    e1a = norm(csys.xyz((r + 9.5, theta2 + h, 0)) - e10)
    e1b = norm(csys.xyz((r + 10.5, theta2, 0)) - e10)
    drawline(color, e00, e00 + e0a + 0.25 * e0b)
    drawline(color, e00, e00 + e0a - 0.25 * e0b)
    drawline(color, e10, e10 - e1a + 0.25 * e1b)
    drawline(color, e10, e10 - e1a - 0.25 * e1b)

    midangle = (theta1 + theta2) / 2
    tmidpoint = csys.xyz((r + 10, midangle, 0))
    textx = norm(csys.xyz((r + 10, midangle + h, 0)) - tmidpoint)
    texty = norm(csys.xyz((r + 10 + h, midangle, 0)) - tmidpoint)

    # make sure the text runs from left to right
    if dot(textx, right) < 0:
        textx = -textx

    # make sure the text isn't upside-down
    outOfScreen = cross(right, up)
    textForward = cross(textx, texty)
    if dot(outOfScreen, textForward) < 0:
        tmidpoint = csys.xyz((r + 11, midangle, 0))
        texty = -texty

    textxyz = tmidpoint - (0.5 * len(text)) * textx

    def tfm(x, y):
        x = (x / 5.) * textx
        y = (y / 7.) * texty
        return textxyz + x + y
    drawString(text, color, tfm)


def drawDihedralDimension(color, right, up, p0, p1, p2, p3, text):
    # Draw a frame of lines that shows how the four atoms are connected
    # to the dihedral angle
    csys = CylindricalCoordinates(p1, p2 - p1, up, right)
    r1, theta1, z1 = csys.rtz(p0)
    r2, theta2, z2 = csys.rtz(p3)
    e0a = csys.xyz((r1, theta1, 0.5))
    e1a = csys.xyz((r2, theta2, 0.5))
    drawline(color, p1, p0)
    drawline(color, p0, e0a)
    drawline(color, p3, e1a)
    drawline(color, p2, p3)
    drawline(color, p1, p2)
    # Use the existing angle drawing routine to finish up
    drawAngleDimension(color, right, up,
                       e0a, (p1 + p2) / 2, e1a, text)
