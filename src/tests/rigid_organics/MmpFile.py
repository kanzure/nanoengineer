#!/usr/bin/python

"""Grab one of Damian's minimized MMP files, perturb each atom's
position by some fraction of an angstrom, write out the result as
another MMP file, which becomes an input file for the test.

$Id$
"""

__author__ = "Will"

import re
import os
import sys
import string
import random

class NotAtomException(Exception):
    pass

class Line:
    def __init__(self, line):
        self._str = line
    def str(self):
        return self._str

class AtomLine(Line):
    pattern = re.compile("^atom (\d+) \((\d+)\) " +
                         "\((\-?\d+), (\-?\d+), (\-?\d+)\)")
    def __init__(self, line):
        m = self.pattern.match(line)
        if m == None:
            raise NotAtomException
        groups = m.groups()
        newline = "atom %s" % groups[0]
        self.elem = elem = string.atoi(groups[1])
        newline += " (%s)" % groups[1]
        newline += " (%d, %d, %d)"
        newline += line[m.span()[1]:]  # anything after position
        self._str = newline
        self.x = 0.001 * string.atoi(groups[2])
        self.y = 0.001 * string.atoi(groups[3])
        self.z = 0.001 * string.atoi(groups[4])
    def __iadd__(self, incr):
        self.x += incr[0]
        self.y += incr[1]
        self.z += incr[2]
    def str(self):
        return self._str % (int(self.x * 1000),
                            int(self.y * 1000),
                            int(self.z * 1000))

class MmpFile:
    """This is meant to be a Python class representing a MMP file. It
    is not intended to represent ALL the information in a MMP file,
    although it might do that in some distant-future version. Right
    now, its biggest strength is that it allows us to easily modify
    the positions of the atoms in an MMP file, and write out the
    resulting modified MMP file."""
    def __init__(self):
        self.atoms = [ ]
        self.lines = [ ]
    def __setitem__(self, i, value):
        self.atoms[i] = value
    def __getitem__(self, i):
        return self.atoms[i]
    def __len__(self):
        return len(self.atoms)
    def read(self, filename):
        inf = open(filename)
        self.readstring(inf.read())
        inf.close()
    def readstring(self, lines):
        for line in lines.split("\n"):
            try:
                atm = AtomLine(line)
                self.atoms.append(atm)
                self.lines.append(atm)
            except NotAtomException:
                ln = Line(line)
                self.lines.append(ln)
    def write(self, outf=None):
        needToClose = True
        if outf == None:
            outf = sys.stdout
            needToClose = False
        for ln in self.lines:
            outf.write(ln.str() + "\n")
        if needToClose:
            outf.close()

if __name__ == "__main__":
    """What follows is a specific usage of the MmpFile class. It's not
    the only way it could be used, but it demonstrates something we're
    going to want to do very soon as we generate test cases from
    Damian's MMP files."""
    m = MmpFile()
    #input = "C14H20.mmp"
    input = "C3H8.mmp"
    m.read(input)
    for i in range(len(m)):
        A = 0.5   # some small number of angstroms
        A = A / (3 ** .5)   # amount in one dimension
        xdiff = random.normalvariate(0.0, A)
        ydiff = random.normalvariate(0.0, A)
        zdiff = random.normalvariate(0.0, A)
        m[i] += (xdiff, ydiff, zdiff)
    outf = os.popen("diff -u - %s | less" % input, "w")
    m.write(outf)
