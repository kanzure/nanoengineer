#!/usr/bin/env python

# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

"""
SplitDotInFile.py

Splits an AMBER .in file containing residues with internal coordinates
into multiple .in_frag files, one for each residue.
"""

import sys

def parseInFile(fileName):
    file = open(fileName)
    lines = file.readlines()
    file.close()
    inFile = False
    nextIndex = -1
    line1 = line2 = line3 = line4 = line5 = line6 = ''
    for line in lines:

        line6 = line5
        line5 = line4
        line4 = line3
        line3 = line2
        line2 = line1
        line1 = line

        columns = line.strip().split()
        if (len(columns) < 10):
            if (inFile):
                # After the last line in a residue, there's a blank
                # line, which will get us here.
                nextIndex = -1
                inFile = False
                out.close()
            continue
        if (columns[0] == '1' and columns[1] == 'DUMM' and columns[2] == 'DU'):
            # This is the start of a new residue (dummy atoms for
            # defining the internal coordinate system).  Earlier lines
            # (saved in lineX) contain various info about the residue.
            # We extract short and long names to build the filename.
            fullName = line6.strip()
            fullName = fullName.replace(' ', '_')
            fullName = fullName.replace('*', '_x_')
            fullName = fullName.replace('/', '_s_')
            fullName = fullName.replace("'", '_p_')
            fullName = fullName.replace('[', '_os_')
            fullName = fullName.replace(']', '_cs_')
            fullName = fullName.replace('(', '_op_')
            fullName = fullName.replace(')', '_cp_')
            cols4 = line4.strip().split()
            shortName = cols4[0]
            newFileName = "%s_%s.in_frag" % (shortName, fullName)
            out = open(newFileName, 'w')
            nextIndex = 1
            inFile = True
        
        if (inFile):
            # Within the residue itself, column 0 is an index number
            # which usually increments sequentially.
            if (columns[0] != "%d" % nextIndex):
                print "%s %s index not sequential" % (fileName, newFileName)
            print >>out, line.rstrip()
            nextIndex = int(columns[0]) + 1


if (__name__ == '__main__'):
    parseInFile(sys.argv[1])
