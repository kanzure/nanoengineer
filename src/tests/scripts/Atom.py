#!/usr/bin/python

"""A common Atom definition to be shared by the classes for various
molecule file formats including MMP and XYZ. This will make it easy to
move information back and forth between formats.

$Id$
"""

__author__ = "Will"

import re
import os
import sys
import string
import random

_PeriodicTable = [
    "X",  # our singlet has element number zero
    "H",                                                "He",
    "Li", "Be",             "B",  "C",  "N", "O", "F",  "Ne",
    "Na", "Mg",             "Al", "Si", "P", "S", "Cl", "Ar",
    "K",  "Ca" #Sc,Ti,V,Cr,Mn,Fe....
    ]

_MmpAtomPattern = re.compile("^atom (\d+) \((\d+)\) " +
                             "\((\-?\d+), (\-?\d+), (\-?\d+)\)")

class NotAtomException(Exception):
    pass

class Atom:
    def fromMmp(self, line):
        m = _MmpAtomPattern.match(line)
        if m == None:
            raise NotAtomException
        groups = m.groups()
        self.elem = elem = string.atoi(groups[1])
        str = "atom %s" % groups[0]
        str += " (%s)" % groups[1]
        str += " (%d, %d, %d)"
        str += line[m.span()[1]:]  # anything after position
        self._mmpstr = str
        self.x = 0.001 * string.atoi(groups[2])
        self.y = 0.001 * string.atoi(groups[3])
        self.z = 0.001 * string.atoi(groups[4])
    def clone(self):
        "permit deep cloning of structure files"
        a = Atom()
        for key in self.__dict__.keys():
            setattr(a, key, getattr(self, key))
        return a
    def fromXyz(self, element, x, y, z):
        self.elem = _PeriodicTable.index(element)
        self.x = x
        self.y = y
        self.z = z
    def toMmpString(self):
        return self._mmpstr % (int(self.x * 1000),
                               int(self.y * 1000),
                               int(self.z * 1000))
    def toXyzString(self):
        element = _PeriodicTable[self.elem]
        return "%s %f %f %f" % (element, self.x, self.y, self.z)
    def __repr__(self):
        return "<" + self.toXyzString() + ">"
