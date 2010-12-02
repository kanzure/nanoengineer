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
import Atom

class MmpFile:
    """This is meant to be a Python class representing a MMP file. It
    is not intended to represent ALL the information in a MMP file,
    although it might do that in some distant-future version. Right
    now, its biggest strength is that it allows us to easily modify
    the positions of the atoms in an MMP file, and write out the
    resulting modified MMP file."""
    class _Line:
        def fromMmp(self, line):
            self._str = line
        def str(self):
            return self._str
        def clone(self, owner):
            ln = MmpFile._Line()
            ln._str = self._str
            return ln
    class _AtomHolder:
        """Atom holders are indices into the MmpFile.atoms list,
        and that's done so that an entry in MmpFile.lines can be
        a pointer into the MmpFile.atoms list. When a file is
        cloned, we clone the atoms but keep the same lines.
        """
        def __init__(self, owner):
            self._owner = owner
        def fromMmp(self, line):
            atoms = self._owner.atoms
            self._index = len(atoms)
            a = Atom.Atom()
            a.fromMmp(line)
            atoms.append(a)
        def str(self):
            a = self._owner.atoms[self._index]
            return a.toMmpString()
        def clone(self, newowner):
            other = MmpFile._AtomHolder(newowner)
            other._index = self._index
            return other
    def __init__(self):
        self.atoms = [ ]
        self.lines = [ ]
    def clone(self):
        other = MmpFile()
        for x in self.lines:
            other.lines.append(x.clone(other))
        for a in self.atoms:
            other.atoms.append(a.clone())
        return other
    def getAtom(self, i):
        return self.atoms[i]
    def __getitem__(self, i):
        a = self.atoms[i]
        return (a.x, a.y, a.z)
    def __setitem__(self, i, xyz):
        a = self.atoms[i]
        a.x, a.y, a.z = xyz
    def __len__(self):
        return len(self.atoms)
    def read(self, filename):
        inf = open(filename)
        self.readstring(inf.read())
        inf.close()
    def readstring(self, lines):
        for line in lines.split("\n"):
            try:
                atm = MmpFile._AtomHolder(self)
                atm.fromMmp(line)
            except Atom.NotAtomException:
                atm = MmpFile._Line()
                atm.fromMmp(line)
            self.lines.append(atm)
    def write(self, outf=None):
        if outf == None:
            outf = sys.stdout
        for ln in self.lines:
            outf.write(ln.str() + "\n")
    def convertToXyz(self):
        import XyzFile
        xyz = XyzFile.XyzFile()
        for a in self.atoms:
            xyz.atoms.append(a)
        return xyz
    def perturb(self):
        import random
        A = 0.5   # some small number of angstroms
        A = A / (3 ** .5)   # amount in one dimension
        for i in range(len(self)):
            x, y, z = self[i]
            x += random.normalvariate(0.0, A)
            y += random.normalvariate(0.0, A)
            z += random.normalvariate(0.0, A)
            self[i] = (x, y, z)

if __name__ == "__main__":
    """What follows is a specific usage of the MmpFile class. It's not
    the only way it could be used, but it demonstrates something we're
    going to want to do very soon as we generate test cases from
    Damian's MMP files."""
    m = MmpFile()
    #input = "C14H20.mmp"
    input = "C3H8.mmp"
    m.read(input)
    m.perturb()
    #outf = os.popen("diff -u - %s | less" % input, "w")
    outf = os.popen("diff -u - %s" % input, "w")
    m.write(outf)
    outf.close()
