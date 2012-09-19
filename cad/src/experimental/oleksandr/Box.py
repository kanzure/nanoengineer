# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.

__author__ = 'oleksandr'

from Interval import *
from Triple import *

"""box representation"""

class Box:

    def __init__(self, *args):
        """box constructor"""
        self.x = Interval()
        self.y = Interval()
        self.z = Interval()
        if len(args) == 0:
            pass
        if len(args) == 3:
            self.x, self.y, self.z = args

    def __str__(self):
        """returns the box in a textual form"""
        s = ""
        s += "%s " % self.x
        s += "%s " % self.y
        s += "%s " % self.z
        return s

    def Empty(self):
        """clear box"""
        self.x.Empty()
        self.y.Empty()
        self.z.Empty()

    def Center(self):
        """calculate center"""
        return Triple(self.x.Center(),self.y.Center(),self.z.Center())

    def Min(self):
        """calculate min"""
        return Triple(self.x.min,self.y.min,self.z.min)

    def Max(self):
        """calculate max"""
        return Triple(self.x.max,self.y.max,self.z.max)

    def Extent(self):
        """calculate extent"""
        return Triple(self.x.Extent(),self.y.Extent(),self.z.Extent())

    def Contains(self, p):
        """box contains point"""
        return self.x.Contains(p.x) and self.y.Contains(p.y) and self.z.Contains(p.z)

    def Enclose(self, p):
        """adjust box"""
        self.x.Enclose(p.x)
        self.y.Enclose(p.y)
        self.z.Enclose(p.z)