#!/usr/bin/python

"""This script examines the structure in an MMP file to enumerate all
the bond length terms and bond angle terms for the structure. If an
XYZ file is given, use the position information from the XYZ file,
otherwise use position information from the MMP file. Bond lengths are
in angstroms, bond angles are in degrees.

Usage:
    findterms.py input.mmp > output.txt
    findterms.py input1.mmp input2.xyz > output.txt

Example output:
LENGTH 0 1 1.53077692692
LENGTH 0 3 1.09477166569
....
ANGLE 0 1 2 112.961986081
ANGLE 0 1 6 109.491950915
....

$Id$
"""

__author__ = "Will"

import sys
from MmpFile import MmpFile
from XyzFile import XyzFile

sys.path.append("../../../../cad/src")
import VQT

bondLengthTerms = { }
bondAngleTerms = { }

def addBondLength(atm1, atm2):
    assert atm1 != atm2
    if atm2 < atm1:
        atm1, atm2 = atm2, atm1
    if bondLengthTerms.has_key(atm1):
        if atm2 not in bondLengthTerms[atm1]:
            bondLengthTerms[atm1].append(atm2)
    else:
        bondLengthTerms[atm1] = [ atm2 ]

def getBonds(atm1):
    lst = [ ]
    if bondLengthTerms.has_key(atm1):
        for x in bondLengthTerms[atm1]:
            lst.append(x)
    for key in bondLengthTerms.keys():
        if atm1 in bondLengthTerms[key]:
            if key not in lst:
                lst.append(key)
    lst.sort()
    return lst

def addBondAngle(atm1, atm2, atm3):
    if atm3 < atm1:
        atm1, atm3 = atm3, atm1
    value = (atm2, atm3)
    if bondAngleTerms.has_key(atm1):
        if value not in bondAngleTerms[atm1]:
            bondAngleTerms[atm1].append(value)
    else:
        bondAngleTerms[atm1] = [ value ]

def measureLength(xyz, first, second):
    '''Returns the angle between two atoms (nuclei)'''
    p0 = apply(VQT.V, xyz[first])
    p1 = apply(VQT.V, xyz[second])
    return VQT.vlen(p0 - p1)

def measureAngle(xyz, first, second, third):
    '''Returns the angle between two atoms (nuclei)'''
    p0 = apply(VQT.V, xyz[first])
    p1 = apply(VQT.V, xyz[second])
    p2 = apply(VQT.V, xyz[third])
    v01, v21 = p0 - p1, p2 - p1
    return VQT.angleBetween(v01, v21)


def main(argv):
    mmpInputFile = argv[0]
    mmp = MmpFile()
    mmp.read(mmpInputFile)

    xyz = XyzFile()
    if len(argv) > 1:
        xyzInputFile = argv[1]
        xyz.read(xyzInputFile)
    else:
        # copy xyz file from mmp file
        import Atom
        for i in range(len(mmp)):
            ma = mmp.atoms[i]
            element = Atom._PeriodicTable[ma.elem]
            x, y, z = ma.x, ma.y, ma.z
            a = Atom.Atom()
            a.fromXyz(element, x, y, z)
            xyz.atoms.append(a)

    assert len(xyz) != 0
    assert len(xyz) == len(mmp)

    # store all the bonds in bondLengthTerms
    for i in range(len(mmp)):
        a = mmp.atoms[i]
        for b in a.bonds:
            addBondLength(i, b - 1)

    # generate angles from chains of two bonds
    for first in range(len(mmp)):
        for second in getBonds(first):
            for third in getBonds(second):
                if first != third:
                    addBondAngle(first, second, third)

    for first in bondLengthTerms.keys():
        for second in bondLengthTerms[first]:
            print "LENGTH", first, second,
            print measureLength(xyz, first, second)

    for first in bondAngleTerms.keys():
        for second, third in bondAngleTerms[first]:
            print "ANGLE", first, second, third,
            print measureAngle(xyz, first, second, third)





if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception, e:
        if e:
            sys.stderr.write(sys.argv[0] + ": " + repr(e.args[0]) + "\n")
            import traceback
            traceback.print_tb(sys.exc_traceback, sys.stderr)
            sys.stderr.write("\n")
        sys.stderr.write(__doc__)
        sys.exit(1)
