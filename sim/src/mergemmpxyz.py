#!/usr/bin/python
# Copyright 2006 Nanorex, Inc.  See LICENSE file for details.

# usage:
#
# mergemmpxyz.py file.mmp file.xyz > merged.mmp
#

import sys
import re

if len(sys.argv) != 3:
    print >>sys.stderr, "usage: mergemmpxyz.py file.mmp file.xyz > merged.mmp"
    sys.exit(1)

atomLinePattern = re.compile(r"^(atom.*\(.*\).*\().*(\).*)$")
xyzLinePattern = re.compile(r"^\S+\s+([-.0-9]+)\s+([-.0-9]+)\s+([-.0-9]+)\s*$")

mmpInputFileName = sys.argv[1]
xyzInputFileName = sys.argv[2]

mmpInputFile = file(mmpInputFileName, "r")
xyzInputFile = file(xyzInputFileName, "r")
# skip the first two lines of xyz file
xyzInput = xyzInputFile.readline() # number of atoms
xyzInput = xyzInputFile.readline() # RMS=0.12345

mmpInput = mmpInputFile.readline()
while mmpInput:
    mmpInput = mmpInput[:-1] # strip trailing newline
    m = atomLinePattern.match(mmpInput)
    if m:
        xyzInput = xyzInputFile.readline()
        if xyzInput:
            m2 = xyzLinePattern.match(xyzInput)
            if m2:
                x = int(float(m2.group(1)) * 1000.0)
                y = int(float(m2.group(2)) * 1000.0)
                z = int(float(m2.group(3)) * 1000.0)
                mmpInput = "%s%d, %d, %d%s" % (m.group(1), x, y, z, m.group(2))
            else:
                print >>stderr, "xyz format error: " + xyzInput,
                sys.exit(1)
        else:
            print >>stderr, "not enough lines in xyz file"
            sys.exit(1)
    print mmpInput
    mmpInput = mmpInputFile.readline()
mmpInputFile.close()
xyzInputFile.close()
