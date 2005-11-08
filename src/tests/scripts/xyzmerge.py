#!/usr/bin/python

"""This will be a script that merges an existing MMP file
with an XYZ file. The idea (I think) is to replace the MMP
file's atom positions with the positions from the XYZ file."""

import sys, re, string
from XyzFile import XyzFile

elementNames = {
    0: "X",
    1: "H",
    6: "C",
    7: "N",
    8: "O",
    14: "Si",
    }

if len(sys.argv) < 3:
    print "Usage: " + sys.argv[0] + " [mmpfile] [xyzfile]"
    print "Merged MMP file is put to standard output"
    sys.exit(0)

mmpInputFile = sys.argv[1]
xyzInputFile = sys.argv[2]

xyz = XyzFile()
xyz.read(xyzInputFile)

mmpLines = open(mmpInputFile).read().split("\n")
atompat = re.compile("^atom (\d+) \((\d+)\) \((\d+), (\d+), (\d+)\)")

xyzIndex = 0
for i in range(len(mmpLines)):
    line = mmpLines[i]
    m = atompat.match(line)
    if m != None:
        atm = xyz[xyzIndex]
        xyzIndex += 1
        groups = m.groups()
        newline = "atom (%s)" % groups[0]
        elem = string.atoi(groups[1])
        if elmentNames[elem] != atm.element:
            print elmentNames[elem], atm.element
            assert False
        newline += " (%s)" % groups[1]
        newline += " (%d, %d, %d)" % (int(atm.x * 1000),
                                      int(atm.y * 1000),
                                      int(atm.z * 1000))
        newline += line[m.span()[1]:]  # anything after position
        mmpLines[i] = newline

for line in mmpLines:
    print line
