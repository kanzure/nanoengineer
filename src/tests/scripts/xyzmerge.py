#!/usr/bin/python

"""This script merges an MMP file with an XYZ file, by replacing the
MMP file's atom positions with the positions from the XYZ file,
producing a new MMP file with the XYZ positions. The merged MMP file
is written to standard output.

Usage:
    xyzmerge.py input1.mmp input2.xyz > output.mmp

$Id$
"""

__author__ = "Will"

import sys
from MmpFile import MmpFile
from XyzFile import XyzFile

try:
    mmpInputFile = sys.argv[1]
    xyzInputFile = sys.argv[2]

    xyz = XyzFile()
    xyz.read(xyzInputFile)
    mmp = MmpFile()
    mmp.read(mmpInputFile)

    assert len(xyz) != 0
    assert len(xyz) == len(mmp)

    for i in range(len(xyz)):
        xa = xyz.atoms[i]
        ma = mmp.atoms[i]
        assert xa.elem == ma.elem
        ma.x, ma.y, ma.z = xa.x, xa.y, xa.z

    mmp.write()

except Exception, e:
    if e:
        sys.stderr.write(sys.argv[0] + ": " + e.args[0] + "\n\n")
    sys.stderr.write(__doc__)
    sys.exit(1)
