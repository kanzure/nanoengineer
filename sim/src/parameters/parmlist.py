#! /usr/bin/python

from string import *
import re
import os
import sys
from math import sqrt

parmpat = re.compile("([A-Z][a-z]?)([\+=\-@#])([A-Z][a-z]?) +Ks= *([\d\.]+) +R0= *([\d\.]+) +De= *([\d\.]+)")
commpat = re.compile("#")


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
        ("Kr", 36, 134.429)]


sym2num={}

for (sym, num, mass) in elmnts:
    sym2num[sym] = num

bontyp = {'-':'1', '=':'2', '+':'3','@':'a', '#':'g'}


if __name__ == "__main__":
    f=open(sys.argv[1])
    for lin in f.readlines():
        if commpat.match(lin): continue
        m = parmpat.match(lin)
        which = m.group(1),m.group(2),m.group(3)

        ks,r0,de = map(lambda p: float(m.group(p)),[4,5,6])

        bt=sqrt(ks/(2.0*de))/10.0
        r0=r0*100.0

        print '  addInitialBondStretch(',
        print '%2d,'%sym2num[which[0]],
        print '%2d,'%sym2num[which[2]],
        print "'%s',"%bontyp[which[1]],

        print '%6.1f,%6.1f,%7.4f,%7.4f); //'%(ks,r0,de,bt),
        print which[0]+which[1]+which[2]
