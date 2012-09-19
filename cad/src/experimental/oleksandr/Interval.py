# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.

__author__ = 'oleksandr'

"""interval representation"""

class Interval:

    def __init__(self, *args):
        """interval constructor"""
        self.min = 0
        self.max = 0
        if len(args) == 0:
            pass
        if len(args) == 2:
            self.min, self.max = args
    def __str__(self):
        """returns the interval in a textual form"""
        s = ""
        s += "%s " % self.min
        s += "%s " % self.max
        return s

    def Empty(self):
        """clear interval"""
        self.min = 1000000
        self.max = -1000000

    def Center(self):
        """calculate center"""
        return (self.max + self.min) / 2

    def Extent(self):
        """calculate extent"""
        return (self.max - self.min) / 2

    def Point(self, u):
        """calculate point"""
        return (1 - u) * self.min + u * self.max

    def Normalize(self, u):
        """normalization"""
        return (u - self.min) / (self.max - self.min)

    def Contains(self, p):
        """interval contains point"""
        return p >= self.min and p <= self.max

    def Enclose(self, p):
        """adjust interval"""
        if (p < self.min):
            self.min = p;
        if (p > self.max):
            self.max = p;

