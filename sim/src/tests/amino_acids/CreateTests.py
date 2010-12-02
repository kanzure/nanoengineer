#!/usr/bin/python

import os
import sys
import MmpFile
import XyzFile

damianFiles = ("ala_l_aminoacid.mmp",
               "arg_l_aminoacid.mmp",
               "asn_l_aminoacid.mmp",
               "asp_l_aminoacid.mmp",
               "cys_l_aminoacid.mmp",
               "gln_l_aminoacid.mmp",
               "glu_l_aminoacid.mmp",
               "gly_l_aminoacid.mmp",
               "his_l_aminoacid.mmp",
               "ile_l_aminoacid.mmp",
               "leu_l_aminoacid.mmp",
               "lys_l_aminoacid.mmp",
               "met_l_aminoacid.mmp",
               "phe_l_aminoacid.mmp",
               "pro_l_aminoacid.mmp",
               "ser_l_aminoacid.mmp",
               "thr_l_aminoacid.mmp",
               "tyr_l_aminoacid.mmp",
               "val_l_aminoacid.mmp")

for df in damianFiles:
    prefix = df[:df.index(".")]
    testPrefix = "test_" + prefix
    damianMmp = MmpFile.MmpFile()
    damianMmp.read(df)

    # Generate the xyzcmp file
    xyzcmpFilename = testPrefix + ".xyzcmp"
    outf = open(xyzcmpFilename, "w")
    xyzcmp = damianMmp.convertToXyz()
    xyzcmp.write(df, outf)
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
