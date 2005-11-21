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
import string
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

LENGTH_TOLERANCE = 0.2
ANGLE_TOLERANCE = 10

def main(argv):
    import getopt

    mmpInputFile = None
    xyzInputFile = None
    outputFile = None
    referenceInputFile = None
    generateFlag = False

    try:
        opts, args = getopt.getopt(argv, "m:x:o:r:g")
    except getopt.error, msg:
        errprint(msg)
        return
    for o, a in opts:
        if o == '-m':
            mmpInputFile = a
        elif o == '-x':
            xyzInputFile = a
        elif o == '-o':
            outputFile = a
        elif o == '-r':
            referenceInputFile = a
        elif o == '-g':
            generateFlag = True

    if mmpInputFile == None:
        mmpInputFile = args.pop(0)
    mmp = MmpFile()
    mmp.read(mmpInputFile)

    xyz = XyzFile()
    if xyzInputFile == None and len(args) > 1:
        xyzInputFile = args.pop(0)

    if xyzInputFile != None:
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

    lengthList = [ ]
    for first in bondLengthTerms.keys():
        for second in bondLengthTerms[first]:
            lengthList.append((first, second,
                               measureLength(xyz, first, second)))
    angleList = [ ]
    for first in bondAngleTerms.keys():
        for second, third in bondAngleTerms[first]:
            angleList.append((first, second, third,
                              measureAngle(xyz, first, second, third)))

    ######### Ready to output stuff, redirect if needed
    if outputFile != None:
        ss, sys.stdout = sys.stdout, open(outputFile, "w")

    if generateFlag:
        for a1, a2, L in lengthList:
            print "LENGTH", a1, a2, L
        for a1, a2, a3, A in angleList:
            print "ANGLE", a1, a2, a3, A

    if referenceInputFile != None:
        badness = False
        # read in LENGTH lines, compare them to this guy
        inf = open(referenceInputFile)
        lp = ap = 0
        for line in inf.readlines():
            if line.startswith("LENGTH "):
                fields = line[7:].split()
                a1, a2, L = (string.atoi(fields[0]),
                             string.atoi(fields[1]),
                             string.atof(fields[2]))
                a11, a22, LL = lengthList[lp]
                lp += 1
                if a1 != a11 or a2 != a22:
                    print ("Wrong length term (%d, %d), should be (%d, %d)"
                           % (a11, a22, a1, a2))
                    badness = True
                    break
                if abs(L - LL) > LENGTH_TOLERANCE:
                    print ("Wrong bond length at (%d, %d), it's %f, should be %f"
                           % (a1, a2, LL, L))
                    badness = True
                    break
            elif line.startswith("ANGLE "):
                fields = line[6:].split()
                a1, a2, a3, A = (string.atoi(fields[0]),
                                 string.atoi(fields[1]),
                                 string.atoi(fields[2]),
                                 string.atof(fields[3]))
                a11, a22, a33, AA = angleList[ap]
                ap += 1
                if a1 != a11 or a2 != a22 or a3 != a33:
                    print ("Wrong angle term (%d, %d, %d), should be (%d, %d, %d)"
                           % (a11, a22, a33, a1, a2, a3))
                    badness = True
                    break
                if abs(L - LL) > ANGLE_TOLERANCE:
                    print ("Wrong bond angle at (%d, %d, %d), it's %f, should be %f"
                           % (a1, a2, a3, AA, A))
                    badness = True
                    break
            else:
                print "Unknown line in reference file:", line
                badness = True
                break
        if not badness:
            print "OK"

    ############ undo redirection if needed ############
    if outputFile != None:
        sys.stdout.close()
        sys.stdout = ss

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
