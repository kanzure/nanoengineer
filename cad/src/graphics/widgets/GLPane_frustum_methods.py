# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_frustum_methods.py

@author: Piotr
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:

piotr circa 080331 wrote these in GLPane.py

bruce 080912 split this code into its own file

Explanation of code:

# The following comment comes from emails exchanged between Russ and Piotr
# on 080403.
#
# This code is based on the information from OpenGL FAQ on clipping and culling:
# http://www.opengl.org/resources/faq/technical/clipping.htm
#
# I tried to dust off the math behind it and I found the following paper
# dealing with the homogeneous coordinates in great detail:
# http://www.unchainedgeometry.com/jbloom/pdf/homog-coords.pdf
#
# The computations are in homogeneous coordinates, so every vertex is
# represented by four coordinates (x,y,z,w). The composite matrix C (cmat
# in the code) transforms a point from the Euclidean coordinates to the
# homogeneous coordinates.
#
# Let's transform a point p(xp,yp,zp,wp) using the computed composite
# matrix:
#
# C[4][4] (in 3D Euclidean space, wp = 1):
#
# r = p^T * C
#
# so we get a transformed point r(p*C0,p*C1,p*C2,p*C3), where Cx represents
# a corresponding row of the matrix C. In homogeneous coordinates, if
# the transformed point is inside the viewing frustum, the following
# inequalities have to be true:
#
# -wr < xr < wr
# -wr < yr < wr
# -wr < zr < wr
#
# So if -wr < xr, the point p is on + side of the left frustum plane,
# if xr < wr it is on + side of the right frustum plane, if -wr < yr,
# the point is on + side of the bottom plane, and so on. Let's take the
# left frustum plane:
#
# -wr < xr
#
# so:
#
# -p*C3 < p*C0
#
# so:
#
# 0 < p*C0+p*C3
#
# that is equal to:
#
# 0 < p*(C0+C3)
#
# which gives us the plane equation (ax+bx+cx+d=0):
#
# x*(C0[0]+C3[0]) + y*(C0[1]+C3[1]) + z*(C0[2]+C3[2]) + w(C0[3]+C3[3]) = 0
#
# Because w = 1:
#
# x*(C0[0]+C3[0]) + y*(C0[1]+C3[1]) + z*(C0[2]+C3[2]) + (C0[3]+C3[3]) = 0
#
# so the plane coefficients are as follows:
#
# a = C0[0] + C3[0]
# b = C0[1] + C3[1]
# c = C0[2] + C3[2]
# d = C0[3] + C3[3]
#
# Similarly, for the right plane (xr < wr) we get:
#
# a = -C0[0] + C3[0]
# b = -C0[1] + C3[1]
# c = -C0[2] + C3[2]
# d = -C0[3] + C3[3]
#
# and so on for every plane.
"""

import math

from geometry.VQT import vlen

from OpenGL.GL import GL_MODELVIEW_MATRIX
from OpenGL.GL import GL_PROJECTION_MATRIX
from OpenGL.GL import glGetFloatv

class GLPane_frustum_methods(object):
    """
    Private mixin superclass to provide frustum culling support to class GLPane.
    The main class needs to call these methods at appropriate times
    and use some attributes we maintain in appropriate ways.
    For documentation see the method docstrings and code comments.

    All our attribute names and method names contain the string 'frustum',
    making them easy to find by text-searching the main class source code.
    """

    def _compute_frustum_planes(self): # Piotr 080331
        """
        Compute six planes to be used for frustum culling
        (assuming the use of that feature is enabled,
         which is up to the client code in the main class).

        Whenever the main class client code changes the projection matrix,
        it must either call this method, or set
        self._frustum_planes_available = False to turn off frustum culling.

        @note: this must only be called when the matrices are set up
               to do drawing in absolute model space coordinates.
               Callers which later change those matrices should review
               whether they need to set self._frustum_planes_available = False
               when they change them, to avoid erroneous culling.
        """
        # Get current projection and modelview matrices
        pmat = glGetFloatv(GL_PROJECTION_MATRIX)
        mmat = glGetFloatv(GL_MODELVIEW_MATRIX)

        # Allocate a composite matrix float[4, 4]
        cmat = [None] * 4
        for i in range(0, 4):
            cmat[i] = [0.0] * 4

        # Compute a composite transformation matrix.
        # cmat = mmat * pmat
        for i in range(0, 4):
            for j in range (0, 4):
                cmat[i][j] = (mmat[i][0] * pmat[0][j] +
                              mmat[i][1] * pmat[1][j] +
                              mmat[i][2] * pmat[2][j] +
                              mmat[i][3] * pmat[3][j])

        # Allocate six frustum planes
        self.fplanes = [None] * 6
        for p in range(0, 6):
            self.fplanes[p] = [0.0] * 4

        # subtract and add the composite matrix rows to get the plane equations

        for p in range(0, 3):
            for i in range(0, 4):
                self.fplanes[2*p][i] = cmat[i][3] - cmat[i][p]
                self.fplanes[2*p+1][i] = cmat[i][3] + cmat[i][p]

        # normalize the plane normals
        for p in range(0, 6):
            n = math.sqrt(float(self.fplanes[p][0] * self.fplanes[p][0] +
                                self.fplanes[p][1] * self.fplanes[p][1] +
                                self.fplanes[p][2] * self.fplanes[p][2]))
            if n > 1e-8:
                self.fplanes[p][0] /= n
                self.fplanes[p][1] /= n
                self.fplanes[p][2] /= n
                self.fplanes[p][3] /= n

        # cause self.is_sphere_visible() to use these planes
        self._frustum_planes_available = True # [bruce 080331]

        return

    def is_sphere_visible(self, center, radius): # Piotr 080331
        """
        Perform a simple frustum culling test against a spherical object
        in absolute model space coordinates. Assume that the frustum planes
        are allocated, i.e. glpane._compute_frustum_planes was already called.
        (If it wasn't, the test will always succeed.)

        @warning: this will give incorrect results unless the current
                  GL matrices are in the same state as when _compute_frustum_planes
                  was last called (i.e. in absolute model space coordinates).
        """
        ### uncomment the following line for the bounding sphere debug
        ### drawwiresphere(white, center, radius, 2)

        if self._frustum_planes_available:
            c0 = center[0]
            c1 = center[1]
            c2 = center[2]
            for p in range(0, 6): # go through all frustum planes
                # calculate a distance to the frustum plane 'p'
                # the sign corresponds to the plane normal direction
                # piotr 080801: getting the frustum plane equation
                # before performing the test gives about 30% performance
                # improvement
                fp = self.fplanes[p]
                dist =  (fp[0] * c0 +
                         fp[1] * c1 +
                         fp[2] * c2 +
                         fp[3])
                # sphere outside of the plane - exit
                if dist < -radius:
                    return False
                continue
            # At this point, the sphere might still be outside
            # of the box (e.g. if it is bigger than the box and a
            # box corner is close to the sphere and points towards it),
            # but this is an acceptable approximation for now
            # (since false positives are safe, and this will not affect
            #  most chunks in typical uses where this is a speedup.)
            # [bruce 080331 comment]
            pass

        return True

    def is_lozenge_visible(self, pos1, pos2, radius): # piotr 080402
        """
        Perform a simple frustum culling test against a "lozenge" object
        in absolute model space coordinates. The lozenge is a cylinder
        with two hemispherical caps. Assume that the frustum planes
        are allocated, i.e. glpane._compute_frustum_planes was already called.
        (If it wasn't, the test will always succeed.)

        Currently, this is a loose (but correct) approximation which calls
        glpane.is_sphere_visible on the lozenge's bounding sphere.

        @warning: this will give incorrect results unless the current
                  GL matrices are in the same state as when _compute_frustum_planes
                  was last called (i.e. in absolute model space coordinates).
        """

        if self._frustum_planes_available:
            center = 0.5 * (pos1 + pos2)
            sphere_radius = 0.5 * vlen(pos2 - pos1) + radius
            res = self.is_sphere_visible(center, sphere_radius)
            # Read Bruce's comment in glpane.is_sphere_visible
            # It applies here, as well.
            return res

        return True

    pass

# end

