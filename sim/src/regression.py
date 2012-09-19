#!/usr/bin/python
# Copyright 2005-2006 Nanorex, Inc.  See LICENSE file for details.

"""run regression tests

how to make a regression test:

Inside one of the directories listed below, you need to create three files.
I'm going to call them test_000X.* here.  Just number them sequentially
although that doesn't really matter.

The first file is the input data file for the test run.  It will
usually be called test_000X.mmp.  If it's called something else, or
there are more than one of them (or zero of them), you can specify
that using the INPUT directive in the .test file.

The second file is the test description file: test_000X.test.
This file describes the inputs, outputs, and program arguments
for the test.  The default values should be fine for minimizer tests.
For dynamics runs you'll need to specify the program arguments:

PROGRAM simulator -f900 -x test_000X.mmp

See runtest.sh for a complete description.

The third file is the expected output.  Generate this using
runtest.sh like this (in the test directory):

../../runtest.sh test_000X.test > test_000X.out

You can change the list of output files to be included
using the OUTPUT directive in the .test file.

Check this file to make sure the output looks reasonable, then
rerun regression.sh before checking in the test_000X.* files.
"""

import os
import sys
import filecmp
from shutil import copy
from os.path import join, basename, exists
from glob import glob
import runtest

testDirs = ["tests/minimize", "tests/dynamics", "tests/rigid_organics"]

exitStatus = 0
generate = False

try:
    if sys.argv[1] == "--generate":
        generate = True
except IndexError:
    pass

if exists("/tmp/testsimulator"):
    os.remove("/tmp/testsimulator")
# Windows doesn't have symbolic links, so copy the file.
copy("simulator", "/tmp/testsimulator")

for dir in testDirs:
    for testFile in glob(join(dir, "*.test")):
        print "Running " + testFile
        base = basename(testFile[:-5])
        out = join(dir, base + ".out")
        # Why do we not pass "--generate" to runtest???
        outf = open(out + ".new", "w")
        #runtest.main((testFile,), myStdout=outf, generate=generate)
        runtest.main((testFile,), myStdout=outf)
        outf.close()

        if generate and not exists(out):
            copy(out + ".new", out)
            print "Generated new " + out

        if filecmp.cmp(out, out + ".new"):
            os.remove(out + ".new")
        else:
            print >> sys.__stderr__, "Test failed: " + testFile
            os.system("diff %s %s.new > %s.diff" % (out, out, out))
            exitStatus = 1

os.remove("/tmp/testsimulator")
