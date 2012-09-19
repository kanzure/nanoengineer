# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
dimensions.py - code to help draw dimensions

$Id$

History:

wware 060324 - created this file

bruce 071030 - split Font3D out of dimensions module (since used in drawer.py)
"""

__author__ = "Will"

import math
import Numeric
from Numeric import dot

from utilities import debug_flags
from geometry.VQT import cross
from geometry.VQT import vlen
from geometry.VQT import norm
from graphics.drawing.CS_draw_primitives import drawline

from graphics.drawing.Font3D import Font3D, WIDTH, HEIGHT
    # TODO: WIDTH, HEIGHT should be Font3D attributes [bruce 071030 comment]

class ZeroLengthCylinder(Exception):
    pass

class CylindricalCoordinates:
    def __init__(self, point0, z, uhint, uhint2):
        # u and v and zn are unit vectors
        # z is NOT a unit vector
        self.p0 = point0
        self.p1 = point1 = point0 + z
        self.z = z
        zlen = vlen(z)
        if zlen < 1.0e-6:
            raise ZeroLengthCylinder()
        self.zinv = 1.0 / zlen
        self.zn = zn = norm(z)
        u = norm(uhint - (dot(uhint, z) / zlen**2) * z)
        if vlen(u) < 1.0e-4:
            u = norm(uhint2 - (dot(uhint2, z) / zlen**2) * z)
        v = cross(zn, u)
        self.u = u
        self.v = v
    def __repr__(self):
        def vecrepr(v):
            return "[%g %g %g]" % tuple(v)
        return ("<CylindricalCoordinates p0=%s p1=%s\n  z=%s u=%s v=%s>" %
                (vecrepr(self.p0), vecrepr(self.p1), vecrepr(self.z),
                 vecrepr(self.u), vecrepr(self.v)))
    def rtz(self, pt):
        d = pt - self.p0
        z = dot(d, self.zn)
        d = d - z * self.zn
        r = vlen(d)
        theta = Numeric.arctan2(dot(d, self.v), dot(d, self.u))
        return Numeric.array((r, theta, z), 'd')
    def xyz(self, rtz):
        r, t, z = rtz
        du = (r * math.cos(t)) * self.u
        dv = (r * math.sin(t)) * self.v
        dz = z * self.z
        return self.p0 + du + dv + dz
    def drawLine(self, color, rtz1, rtz2, width=1):
        drawline(color, self.xyz(rtz1), self.xyz(rtz2), width=width)
    def drawArc(self, color, r, theta1, theta2, z,
                width=1, angleIncrement = math.pi / 50):
        n = int(math.fabs(theta2 - theta1) / angleIncrement + 1)
        step = (1.0 * theta2 - theta1) / n
        for i in range(n):
            t = theta1 + step
            self.drawLine(color, (r, theta1, z), (r, t, z), width=width)
            theta1 = t

THICKLINEWIDTH = 20

def drawLinearDimension(color,      # what color are we drawing this in
                        right, up,  # screen directions mapped to xyz coords
                        bpos,       # position of the handle for moving the text
                        p0, p1,     # positions of the ends of the dimension
                        text, highlighted=False):
    outOfScreen = cross(right, up)
    bdiff = bpos - 0.5 * (p0 + p1)
    csys = CylindricalCoordinates(p0, p1 - p0, bdiff, right)
    # This works OK until we want to keep the text right side up, then the
    # criterion for right-side-up-ness changes because we've changed 'up'.
    br, bt, bz = csys.rtz(bpos)
    e0 = csys.xyz((br + 0.5, 0, 0))
    e1 = csys.xyz((br + 0.5, 0, 1))
    drawline(color, p0, e0)
    drawline(color, p1, e1)
    v0 = csys.xyz((br, 0, 0))
    v1 = csys.xyz((br, 0, 1))
    if highlighted:
        drawline(color, v0, v1, width=THICKLINEWIDTH)
    else:
        drawline(color, v0, v1)
    # draw arrowheads at the ends
    a1, a2 = 0.25, 1.0 * csys.zinv
    arrow00 = csys.xyz((br + a1, 0, a2))
    arrow01 = csys.xyz((br - a1, 0, a2))
    drawline(color, v0, arrow00)
    drawline(color, v0, arrow01)
    arrow10 = csys.xyz((br + a1, 0, 1-a2))
    arrow11 = csys.xyz((br - a1, 0, 1-a2))
    drawline(color, v1, arrow10)
    drawline(color, v1, arrow11)
    # draw the text for the numerical measurement, make
    # sure it goes from left to right
    xflip = dot(csys.z, right) < 0
    # then make sure it's right side up
    theoreticalRight = (xflip and -csys.z) or csys.z
    theoreticalOutOfScreen = cross(theoreticalRight, bdiff)
    yflip = dot(theoreticalOutOfScreen, outOfScreen) < 0
    if debug_flags.atom_debug:
        print "DEBUG INFO FROM drawLinearDimension"
        print csys
        print theoreticalRight, theoreticalOutOfScreen
        print xflip, yflip
    if yflip:
        def fx(y):
            return br + 1.5 - y / (1. * HEIGHT)
    else:
        def fx(y):
            return br + 0.5 + y / (1. * HEIGHT)
    if xflip:
        def fz(x):
            return 0.9 - csys.zinv * x / (1. * WIDTH)
    else:
        def fz(x):
            return 0.1 + csys.zinv * x / (1. * WIDTH)
    def tfm(x, y, fx=fx, fz=fz):
        return csys.xyz((fx(y), 0, fz(x)))
    f3d = Font3D()
    f3d.drawString(text, tfm=tfm, color=color)

def drawAngleDimension(color, right, up, bpos, p0, p1, p2, text,
                       minR1=0.0, minR2=0.0, highlighted=False):
    z = cross(p0 - p1, p2 - p1)
    try:
        csys = CylindricalCoordinates(p1, z, up, right)
    except ZeroLengthCylinder:
        len0 = vlen(p1 - p0)
        len2 = vlen(p1 - p2)
        # make sure it's really a zero-degree angle
        assert len0 > 1.0e-6
        assert len2 > 1.0e-6
        assert vlen(cross(p1 - p2, p1 - p0)) < 1.0e-6
        # For an angle of zero degrees, there is no correct way to
        # orient the text, so just draw a line segment
        if len0 > len2:
            L = len0
            end = p0
        else:
            L = len2
            end = p2
        Lb = vlen(bpos - p1)
        if Lb > L:
            L = Lb
            end = p1 + (Lb / L) * (end - p1)
        drawline(color, p1, end)
        return
    br, bt, bz = csys.rtz(bpos)
    theta1 = csys.rtz(p0)[1]
    theta2 = csys.rtz(p2)[1]
    if theta2 < theta1 - math.pi:
        theta2 += 2 * math.pi
    elif theta2 > theta1 + math.pi:
        theta2 -= 2 * math.pi
    if theta2 < theta1:
        theta1, theta2 = theta2, theta1
    e0 = csys.xyz((max(vlen(p0 - p1), br, minR1) + 0.5, theta1, 0))
    e1 = csys.xyz((max(vlen(p2 - p1), br, minR2) + 0.5, theta2, 0))
    drawline(color, p1, e0)
    drawline(color, p1, e1)
    if highlighted:
        csys.drawArc(color, br, theta1, theta2, 0, width=THICKLINEWIDTH)
    else:
        csys.drawArc(color, br, theta1, theta2, 0)
    # draw some arrowheads
    e00 = csys.xyz((br, theta1, 0))
    e10 = csys.xyz((br, theta2, 0))
    dr = 0.25
    dtheta = 1 / br
    e0a = csys.xyz((br + dr, theta1 + dtheta, 0))
    e0b = csys.xyz((br - dr, theta1 + dtheta, 0))
    e1a = csys.xyz((br + dr, theta2 - dtheta, 0))
    e1b = csys.xyz((br - dr, theta2 - dtheta, 0))
    drawline(color, e00, e0a)
    drawline(color, e00, e0b)
    drawline(color, e10, e1a)
    drawline(color, e10, e1b)
    midangle = (theta1 + theta2) / 2
    tmidpoint = csys.xyz((br + 0.5, midangle, 0))
    h = 1.0e-3
    textx = norm(csys.xyz((br + 0.5, midangle + h, 0)) - tmidpoint)
    texty = norm(csys.xyz((br + 0.5 + h, midangle, 0)) - tmidpoint)

    # make sure the text runs from left to right
    if dot(textx, right) < 0:
        textx = -textx

    # make sure the text isn't upside-down
    outOfScreen = cross(right, up)
    textForward = cross(textx, texty)
    if dot(outOfScreen, textForward) < 0:
        tmidpoint = csys.xyz((br + 1.5, midangle, 0))
        texty = -texty

    textxyz = tmidpoint - (0.5 * len(text)) * textx

    def tfm(x, y):
        x = (x / (1. * WIDTH)) * textx
        y = (y / (1. * HEIGHT)) * texty
        return textxyz + x + y
    f3d = Font3D()
    f3d.drawString(text, tfm=tfm, color=color)

def drawDihedralDimension(color, right, up, bpos, p0, p1, p2, p3, text,
                          highlighted=False):
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
    drawAngleDimension(color, right, up, bpos,
                       e0a, (p1 + p2) / 2, e1a, text,
                       minR1=r1, minR2=r2, highlighted=highlighted)

# end
