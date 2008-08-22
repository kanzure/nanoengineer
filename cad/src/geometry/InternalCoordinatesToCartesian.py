# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

"""
InternalCoordinatesToCartesian.py

@author: EricM from code by Piotr
@version:$Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""

from geometry.VQT import V

from Numeric import zeros, Float, cos, sin, sqrt, pi

DEG2RAD = (pi/180.0)

class InternalCoordinatesToCartesian(object):
    """
    Translator to convert internal coordinates (such as those in AMBER
    .in files, as described by http://amber.scripps.edu/doc/prep.html)
    into cartesian coordinates.  Internal coordinates represent the
    location of each point relative to three other already defined
    points.  Indicies for those three points are given, along with
    distances, angles, and torsion angles among the given points.
    Each point in either cartesian or internal coordinates has three
    degrees of freedom, but they are specified differently between the
    two systems.

    To use:

    Create the translator object.  If you wish to add the resulting
    structure onto a particular location on an existing structure, you
    should pass in suitable cartesian coordinates for the
    initialCoordinates, which define the position and orientation of
    the coordinate system used to translate the points.  If you leave
    this as None, the results will begin at the origin in a standard
    orientation.

    For each set of internal coordinates represenging one point, call
    addInternal() passing in the internal coordinates.

    For each point so defined, you can retrieve the cartesian
    equivalent coordinates with a call to getCartesian().
    """

    def __init__(self, length, initialCoordinates):
        """
        @param length: How many points will be converted, including
                       the 3 dummy points.

        @param initialCoordinates: Either None, or an array of three
                                   sets of x, y, z cartesian
                                   coordinates.  These are the
                                   coordinates of the three dummy
                                   points, indices 1, 2, and 3, which
                                   are defined before any actual data
                                   points are added.
        """
        self._coords = zeros([length+1, 3], Float)
        if (initialCoordinates):
            self._coords[1][0] = initialCoordinates[0][0]
            self._coords[1][1] = initialCoordinates[0][1]
            self._coords[1][2] = initialCoordinates[0][2]

            self._coords[2][0] = initialCoordinates[1][0]
            self._coords[2][1] = initialCoordinates[1][1]
            self._coords[2][2] = initialCoordinates[1][2]

            self._coords[3][0] = initialCoordinates[2][0]
            self._coords[3][1] = initialCoordinates[2][1]
            self._coords[3][2] = initialCoordinates[2][2]
        else:
            self._coords[1][0] = -1.0
            self._coords[1][1] = -1.0
            self._coords[1][2] =  0.0

            self._coords[2][0] = -1.0
            self._coords[2][1] =  0.0
            self._coords[2][2] =  0.0

            self._coords[3][0] =  0.0
            self._coords[3][1] =  0.0
            self._coords[3][2] =  0.0

        self._nextIndex = 4

    def addInternal(self, i, na, nb, nc, r, theta, phi):
        """
        Add another point, given its internal coordinates.  Once added
        via this routine, the cartesian coordinates for the point can
        be retrieved with getCartesian().

        @param i: Index of the point being added.  After this call, a
                  call to getCartesian with this index value will
                  succeed.  Index values less than 4 are ignored.
                  Index values should be presented here in sequence
                  beginning with 4.

        @param na: Index value for point A.  Point 'i' will be 'r'
                   distance units from point A.

        @param nb: Index value for point B.  Point 'i' will be located
                   such that the angle i-A-B is 'theta' degrees.

        @param nc: Index value for point C.  Point 'i' will be located
                      such that the torsion angle i-A-B-C is 'torsion'
                      degrees.

        @param r: Radial distance (in same units as resulting
                  cartesian coordinates) between A and i.

        @param theta: Angle in degrees of i-A-B.

        @param phi: Torsion angle in degrees of i-A-B-C
        """

        if (i < 4):
            return

        if (i != self._nextIndex):
            raise IndexError, "next index is %d not %r" % (self._nextIndex, i)

        cos_theta = cos(DEG2RAD * theta)
        xb = self._coords[nb][0] - self._coords[na][0]
        yb = self._coords[nb][1] - self._coords[na][1]
        zb = self._coords[nb][2] - self._coords[na][2]
        rba = 1.0 / sqrt(xb*xb + yb*yb + zb*zb)

        if abs(cos_theta) >= 0.999:
            # Linear case
            # Skip angles, just extend along A-B.
            rba = r * rba * cos_theta
            xqd = xb * rba
            yqd = yb * rba
            zqd = zb * rba
        else:
            xc = self._coords[nc][0] - self._coords[na][0]
            yc = self._coords[nc][1] - self._coords[na][1]
            zc = self._coords[nc][2] - self._coords[na][2]

            xyb = sqrt(xb*xb + yb*yb)

            inv = False
            if xyb < 0.001:
                # A-B points along the z axis.
                tmp = zc
                zc = -xc
                xc = tmp
                tmp = zb
                zb = -xb
                xb = tmp
                xyb = sqrt(xb*xb + yb*yb)
                inv = True

            costh = xb / xyb
            sinth = yb / xyb
            xpc = xc * costh + yc * sinth
            ypc = yc * costh - xc * sinth
            sinph = zb * rba
            cosph = sqrt(abs(1.0- sinph * sinph))
            xqa = xpc * cosph + zc * sinph
            zqa = zc * cosph - xpc * sinph
            yzc = sqrt(ypc * ypc + zqa * zqa)
            if yzc < 1e-8:
                coskh = 1.0
                sinkh = 0.0
            else:
                coskh = ypc / yzc
                sinkh = zqa / yzc

            sin_theta = sin(DEG2RAD * theta)
            sin_phi = -sin(DEG2RAD * phi)
            cos_phi = cos(DEG2RAD * phi)

            # Apply the bond length.
            xd = r * cos_theta
            yd = r * sin_theta * cos_phi
            zd = r * sin_theta * sin_phi

            # Compute the atom position using bond and torsional angles.
            ypd = yd * coskh - zd * sinkh
            zpd = zd * coskh + yd * sinkh
            xpd = xd * cosph - zpd * sinph
            zqd = zpd * cosph + xd * sinph
            xqd = xpd * costh - ypd * sinth
            yqd = ypd * costh + xpd * sinth

            if inv:
                tmp = -zqd
                zqd = xqd
                xqd = tmp

        self._coords[i][0] = xqd + self._coords[na][0]
        self._coords[i][1] = yqd + self._coords[na][1]
        self._coords[i][2] = zqd + self._coords[na][2]
        self._nextIndex = self._nextIndex + 1

    def getCartesian(self, index):
        """
        Return the cartesian coordinates for a point added via
        addInternal().  Units are the same as for the 'r' parameter of
        addInternal().
        """
        if (index < self._nextIndex and index > 0):
            return V(self._coords[index][0],
                     self._coords[index][1],
                     self._coords[index][2])
        raise IndexError, "%r not defined" % index
