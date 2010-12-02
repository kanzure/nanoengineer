#!/usr/bin/python

"""This script translates an MMP file to an XYZ file.

Usage:
    mmp2xyz.py input.mmp > output.xyz

$Id$
"""

__author__ = "Will"

import sys
from MmpFile import MmpFile
from XyzFile import XyzFile
import Atom

try:
    mmpInputFile = sys.argv[1]

    xyz = XyzFile()
    mmp = MmpFile()
    mmp.read(mmpInputFile)

    for i in range(len(mmp)):
        ma = mmp.atoms[i]
        element = Atom._PeriodicTable[ma.elem]
        x, y, z = ma.x, ma.y, ma.z
        a = Atom.Atom()
        a.fromXyz(element, x, y, z)
        xyz.atoms.append(a)

    xyz.write(mmpInputFile)

except Exception, e:
    if e:
        sys.stderr.write(sys.argv[0] + ": " + e.args[0] + "\n")
        import traceback
        traceback.print_tb(sys.exc_traceback, sys.stderr)
        sys.stderr.write("\n")
    sys.stderr.write(__doc__)
    sys.exit(1)
