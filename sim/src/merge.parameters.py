#!/usr/bin/python
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.

# usage:
#
# merge.parameters.py existingParameterFile newParameterFiles...
#
# creates existingParameterFile.new
#

import sys
import re

leadingWhitespacePattern = re.compile(r"^\s*")
trailingWhitespacePattern = re.compile(r"\s*$")
idPattern = re.compile(r"(\$Id\:.*\$)")
commentPattern = re.compile("#")
firstField = re.compile(r"^(\S+)\s+(.*)")
parameterPattern = re.compile(r"^([^=]+)\s*\=\s*(\S+)\s*(.*)")

existing = sys.argv[1]
allfiles = sys.argv[1:]

print "existing parameter file: " + existing
newfile = open(existing + ".new", 'w')

# accumulates canonicalized lines for each unique "bond hybridization" pair
results = {}

for f in allfiles:
    print "processing " + f
    lines = open(f).readlines();
    for l in lines:
        # remove leading and trailing whitespace
        l = leadingWhitespacePattern.sub('', l)
        l = trailingWhitespacePattern.sub('', l)

        # find RCSID
        if f == existing and idPattern.search(l):
            newfile.write("#\n" + l + "\n#\n\n")
            continue

        # ignore comments and blank lines
        if commentPattern.match(l): continue
        if len(l) == 0: continue

        m = firstField.match(l)
        if m:
            bond = m.group(1)
            rest = m.group(2)
            canonical = bond + " "
            hybrid = "sp3"
            m = parameterPattern.match(rest)
            while m:
                key = m.group(1)
                value = m.group(2)
                rest = m.group(3)
                if key == "CenterHybridization":
                    hybrid = value
                canonical += key + "=" + value + " "
                m = parameterPattern.match(rest)
            sortfield = bond + " " + hybrid
            results[sortfield] = canonical

bondkeys = results.keys()
bondkeys.sort()
for key in bondkeys:
    newfile.write(results[key] + "\n")

