# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.

__author__ = 'oleksandr'

import types, operator, math

"""3D vector representation"""

class Triple:

    def __init__(self, *args):
        """vector constructor"""
        self.x = 0
        self.y = 0
        self.z = 0
        if len(args) == 0:
            pass
        if len(args) == 1:
            if isinstance(args[0], types.InstanceType):
                self.x = args[0].x
                self.y = args[0].y
                self.z = args[0].z
            elif isinstance(args[0], types.ListType):
                self.x = args[0][0]
                self.y = args[0][1]
                self.z = args[0][2]
            else:
                self.x = args[0]
                self.y = args[0]
                self.z = args[0]
        if len(args) == 2:
            self.x = args[1][0] - args[0][0]
            self.y = args[1][1] - args[0][1]
            self.z = args[1][2] - args[0][2]
        if len(args) == 3:
            self.x, self.y, self.z = args

    def __str__(self):
        """returns the triple in a textual form"""
        s = ""
        s += "%s " % self.x
        s += "%s " % self.y
        s += "%s " % self.z
        return s

    def Len2(self):
        """square of vector length"""
        return self.x * self.x + self.y * self.y + self.z * self.z

    def Len(self):
        """vector length"""
        return math.sqrt(self.Len2())

    def Normalize(self):
        """normalizes vector to unit length"""
        length = self.Len();
        self.x /= length
        self.y /= length
        self.z /= length
        return self

    def Greatest(self):
        """calculate greatest value"""
        if self.x > self.y:
            if self.x > self.z:
                return self.x
            else:
                return self.z
        else:
            if self.y > self.z:
                return self.y
            else:
                return self.z

    def __add__( self, rhs ):
        """operator a + b"""
        t = Triple(rhs)
        return Triple(self.x + t.x, self.y + t.y, self.z + t.z)

    def __radd__( self, lhs ):
        """operator b + a"""
        t = Triple(lhs)
        t.x += self.x
        t.y += self.y
        t.z += self.z
        return t

    def __sub__( self, rhs ):
        """operator a - b"""
        t = Triple(rhs)
        return Triple(self.x - t.x, self.y - t.y, self.z - t.z)

    def __rsub__( self, lhs ):
        """operator b - a"""
        t = Triple(lhs)
        t.x -= self.x
        t.y -= self.y
        t.z -= self.z
        return t

    def __mul__( self, rhs ):
        """operator a * b"""
        t = Triple(rhs)
        return Triple(self.x * t.x, self.y * t.y, self.z * t.z)

    def __rmul__( self, lhs ):
        """operator b * a"""
        t = Triple(lhs)
        t.x *= self.x
        t.y *= self.y
        t.z *= self.z
        return t

    def __div__( self, rhs ):
        """operator a / b"""
        t = Triple(rhs)
        return Triple(self.x / t.x, self.y / t.y, self.z / t.z)

    def __rdiv__( self, lhs ):
        """operator b / a"""
        t = Triple(lhs)
        t.x /= self.x
        t.y /= self.y
        t.z /= self.z
        return t

    def __mod__( self, rhs ):
        """operator a % b (scalar product)"""
        r = self.x * rhs.x + self.y * rhs.y + self.z * rhs.z
        return r

    def __neg__( self):
        """operator -a"""
        return Triple(-self.x, -self.y, -self.z)

def Dot(lhs, rhs ):
    """function dot(a, b) (scalar product)"""
    r = lhs.x * rhs.x + lhs.y * rhs.y + lhs.z * rhs.z
    return r

