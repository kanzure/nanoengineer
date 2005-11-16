#!/usr/bin/python

import os
import sys
import MmpFile
import XyzFile

damianFiles = filter(lambda x: x,
                     os.popen("ls C*.mmp").read().split("\n"))

for df in damianFiles:
    prefix = df[:df.index(".")]
    testPrefix = "test_" + prefix
    damianMmp = MmpFile.MmpFile()
    damianMmp.read(df)

    # Generate the xyzcmp file
    xyzcmpFilename = testPrefix + ".xyzcmp"
    outf = open(xyzcmpFilename, "w")
    xyzcmp = damianMmp.convertToXyz()
    xyzcmp.write("Converted from " + df, outf)
    outf.close()

    # Make a perturbed copy of the MMP, use it for test_{foo}.mmp
    dmClone = damianMmp.clone()
    dmClone.perturb()
    testMmpFilename = testPrefix + ".mmp"
    outf = open(testMmpFilename, "w")
    dmClone.write(outf)
    outf.close()

    # Create test_{foo}.test
    testTestFilename = testPrefix + ".test"
    outf = open(testTestFilename, "w")
    outf.write("TYPE struct\n")
    outf.close()

    print "Test input files generated for " + testPrefix
