#! /usr/bin/python
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.

from string import *
import re
import os
import sys
from math import sqrt

findBondNamePattern = re.compile(r"^(\S+)\s+(.*)$")
bondNamePattern = re.compile(r"(.*)([-=+@#])(.*)([-=+@#])(.*)$")
parameterPattern = re.compile(r"^([^=]+)\s*\=\s*(\S+)\s*(.*)")
idPattern = re.compile(r"(\$Id\:.*\$)")
commentPattern = re.compile("#")
leadingWhitespacePattern = re.compile(r"^\s*")
trailingWhitespacePattern = re.compile(r"\s*$")


elmnts=[("H",   1,   1.6737),
        ("He",  2,   6.646),
        ("Li",  3,  11.525),
        ("Be",  4,  14.964),
        ("B",   5,  17.949),
        ("C",   6,  19.925),
        ("N",   7,  23.257),
        ("O",   8,  26.565),
        ("F",   9,  31.545),
        ("Ne", 10,  33.49),

        ("Na", 11,  38.1726),
        ("Mg", 12,  40.356),
        ("Al", 13,  44.7997),
        ("Si", 14,  46.6245),
        ("P",  15,  51.429),
        ("S",  16,  53.233),
        ("Cl", 17,  58.867),
        ("Ar", 18,  66.33),

        ("K",  19,  64.9256),
        ("Ca", 20,  66.5495),
        ("Sc", 21,  74.646),
        ("Ti", 22,  79.534),
        ("V",  23,  84.584),
        ("Cr", 24,  86.335),
        ("Mn", 25,  91.22),
        ("Fe", 26,  92.729),
        ("Co", 27,  97.854),
        ("Ni", 28,  97.483),
        ("Cu", 29, 105.513),
        ("Zn", 30, 108.541),
        ("Ga", 31, 115.764),
        ("Ge", 32, 120.53),
        ("As", 33, 124.401),
        ("Se", 34, 131.106),
        ("Br", 35, 132.674),
        ("Kr", 36, 134.429),

        ("Ax", 200, 0.000),
        ("Ss", 201, 0.000),
        ("Sp", 202, 0.000),
        ]

sym2num={}
bends={}

for (sym, num, mass) in elmnts:
    sym2num[sym] = num

bontyp = {'-':'1', '=':'2', '+':'3','@':'a', '#':'g'}

def printBond(a1, bond1, ac, bond2, a2, parameters):
    ktheta = parameters['Ktheta']
    theta0 = parameters['theta0']
    centerHybridization = parameters['CenterHybridization']
    quality = int(parameters['Quality'])
    b1 = bontyp[bond1]
    b2 = bontyp[bond2]
    if sym2num[a1] > sym2num[a2] or (a1 == a2 and b1 > b2):
        a1, b1, b2, a2 = a2, b2, b1, a1
    bendName = '%s-%s-%s.%s-%s-%s' % (a1, b1, ac, centerHybridization, b2, a2)
    bendLine = 'addInitialBendData(%-14s, %-13s, %2d, "%s");' % (ktheta, theta0, quality, bendName)
    if (bendName in bends):
        print '//' + bendLine
    else:
        print '  ' + bendLine
    bends[bendName] = 1

if __name__ == "__main__":
    f=open(sys.argv[1])
    headerPrinted = False
    for lin in f.readlines():
        # remove leading and trailing whitespace
        lin = leadingWhitespacePattern.sub('', lin)
        lin = trailingWhitespacePattern.sub('', lin)

        # find RCSID
        m = idPattern.search(lin)
        if m:
            print '#define RCSID_BENDS_H "Generated from: ' + m.group(1) + '"'
            continue

        # ignore comments and blank lines
        if commentPattern.match(lin): continue
        if len(lin) == 0: continue

        m = findBondNamePattern.match(lin)
        if (m):
            bond = m.group(1)
            rest = m.group(2)
            parameters = {}
            parameters['bond'] = bond
            # default values for particular parameters:
            parameters['Quality'] = 9
            parameters['CenterHybridization'] = "sp3"
            # extract parameters from rest of line into dictionary
            m = parameterPattern.match(rest)
            while m:
                key = m.group(1)
                value = m.group(2)
                rest = m.group(3)
                parameters[key] = value
                m = parameterPattern.match(rest)
            m = bondNamePattern.match(bond)
            if m:
                if not headerPrinted:
                    headerPrinted = True
                    print '//                     ktheta          theta0  quality bondName'
                printBond(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), parameters)
            else:
                print >> sys.stderr, 'malformed bond: ' + bond
            continue
        else:
            print >> sys.stderr, 'unrecognized line: "' + lin + '"'
