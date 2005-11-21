# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

""" generate the bond data tables for the simulator
"""
__author__ = "Josh"

import sys
sys.path.append("../../cad/src")

from VQT import *
from LinearAlgebra import *


class elem:
    def __init__(self, no, sym, n, m, rv, bn, rc):
        """called from a table in the source
        no = element number
        sym = (e.g.) "H"
        n = (e.g.) "Hydrogen"
        m = atomic mass in e-27 kg
        rv = van der Waals radius
        bn = number of bonds
        rc = covalent radius
        """
        self.eltnum = no
        self.symbol = sym
        self.name = n
        self.mass = m
        self.rvdw = rv
        self.rcovalent = rc
        self.bonds = bn

    def __repr__(self):
        return "<Element: " + self.symbol + "(" + self.name + ")>"

    def prec(self):
        # /* mass  rvdw   evdw nbonds symbol */
        # {0.100,  0.5,  0.130, 1, "X"},   /*  0 Singlet */
        evd = evdw.get(self.symbol, 0.3+self.eltnum**2/190.0)
        lis = self.mass, self.rvdw, evd, self.bonds, self.rcovalent, self.symbol,
        rec = '   {%7.3f, %5.2f, %6.3f, %d, %6.3f, "%s"},  ' % lis
        print rec+' //', self.name
        

#      sym   name          mass    rVdW  bonds  Rcov
# note mass is in e-27 kg, not amu

Mendeleev=[ \
 elem(0, "X", "Singlet",      17.000,  1.1, 1, 0),
 elem(1, "H",  "Hydrogen",    1.6737, 0.77, 1, 30),
 elem(2, "He", "Helium",      6.646,  1.4, 0, 0),
 
 elem(3, "Li", "Lithium",    11.525,  0.97, 1, 152),
 elem(4, "Be", "Beryllium",  14.964,  1.10, 2, 114),
 elem(5, "B",  "Boron",      17.949,  1.46, 3, 83),
 elem(6, "C",  "Carbon",     19.925,  1.43, 4, 77),
 elem(7, "N",  "Nitrogen",   23.257,  1.39, 3, 70),
 elem(8, "O",  "Oxygen",     26.565,  1.35, 2, 66),
 elem(9, "F",  "Fluorine",   31.545,  1.29, 1, 64),
 elem(10, "Ne", "Neon",       33.49,  1.82, 0, 0),
 
 elem(11, "Na", "Sodium",     38.1726, 1.29, 1, 186),
 elem(12, "Mg", "Magnesium",  40.356,  1.15, 2, 160),
 elem(13, "Al", "Aluminum",   44.7997, 2.0, 3, 125),
 elem(14, "Si", "Silicon",    46.6245, 1.82, 4, 116),
 elem(15, "P",  "Phosphorus", 51.429,  1.78, 3, 110),
 elem(16, "S",  "Sulfur",     53.233,  1.74, 2, 104),
 elem(17, "Cl", "Chlorine",   58.867,  1.69, 1, 99),
 elem(18, "Ar", "Argon",      62.33,   1.88, 0, 0),

 elem(19, "K",  "Potassium",  64.9256, 1.59, 1, 231),
 elem(20, "Ca", "Calcium",    66.5495, 1.27, 2, 197),
 elem(21, "Sc", "Scandium",   74.646,  2.0, 0, 60),
 elem(22, "Ti", "Titanium",   79.534,  2.0, 0, 147),
 elem(23, "V",  "Vanadium",   84.584,  2.0, 0, 132),
 elem(24, "Cr", "Chromium",   86.335,  2.0, 0, 125),
 elem(25, "Mn", "Manganese",  91.22,   2.0, 0, 112),
 elem(26, "Fe", "Iron",       92.729,  2.0, 0, 124),
 elem(27, "Co", "Cobalt",     97.854,  2.0, 0, 125),
 elem(28, "Ni", "Nickel",     97.483,  2.3, 0, 125),
 elem(29, "Cu", "Copper",    105.513,  2.3, 0, 128),
 elem(30, "Zn", "Zinc",      108.541,  2.3, 0, 133),
 elem(31, "Ga", "Gallium",   115.764,  2.3, 0, 135),
 elem(32, "Ge", "Germanium", 120.53,   2.0, 4, 122),
 elem(33, "As", "Arsenic",   124.401,  2.0, 3, 120),
 elem(34, "Se", "Selenium",  131.106,  1.88, 2, 119),
 elem(35, "Br", "Bromine",   132.674,  1.83, 1, 119),
 elem(36, "Kr", "Krypton",   134.429,  1.9, 0,  0),

 elem(51, "Sb", "Antimony",  124.401,  2.2, 3, 144),
 elem(52, "Te", "Tellurium", 131.106,  2.1, 2, 142),
 elem(53, "I", "Iodine",     132.674,  2.0, 1, 141),
 elem(54, "Xe", "Xenon",     134.429,  1.9, 0, 0)

]

"""
ks = 2*De*beta^2
beta = 0.4+125/(r0*De)
evdw = 0.3+n^2/100
"""
 
evdw = {
 "H":0.382,
 "C":0.357,
 "N":0.447,
 "O":0.406,
 "F":0.634,
 "Si":1.137,
 "P":1.365,
 "S":1.641,
 "Cl":1.950,
}


print """
// Copyright (c) 2005 Nanorex, Inc. All Rights Reserved.
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "simulator.h"


struct atomtype element[]={
    /* mass  rvdw   evdw nbonds symbol */

"""
pertab ={}
for el in Mendeleev:
    pertab[el.eltnum] = el
    el.prec()

print """
};

const int NUMELTS = sizeof(element)/sizeof(struct atomtype);

struct bsdata bstab[]={
    // order,atom1,atom2  
    //              Ks    r0     de   beta*0.01
    //             N/m    pm     aJ

"""

Detab = {'HN': 0.75, 'NO': 0.383, 'NF': 0.422,
         'FS': 0.166, 'OF': 0.302, 'CI': 0.373,
         'OCl': 0.397, 'OI': 0.354, 'SCl': 0.489}

bontab = {}
for el in Mendeleev:
    if el.bonds<1: continue
    for el2 in Mendeleev:
        if el2.bonds<1: continue
        if not el2.symbol+el.symbol in bontab:
            r0 = el.rcovalent+el2.rcovalent
            if r0==0: continue
            de=Detab.get(el.symbol+el2.symbol,0.58)
            b=0.4+125/(r0*de)
            ks = min(200*de*b**2, 1000)
            rec = (el.eltnum, el2.eltnum, ks, r0, de, b)
            bontab[el.symbol+el2.symbol] = rec

def bondrec(n1,n2, ks, r0, de, b):
    #print r0, pertab[n1].rcovalent+pertab[n2].rcovalent
    #print ks, 200*de*b**2
    #print r0,de, b,0.4+125/(r0*de)
    #print r0, de, 1-r0*0.0025
    bontab[pertab[n1].symbol+pertab[n2].symbol] = (n1,n2, ks, r0, de, b)
    
#//              Ks    r0     de   beta*0.01
#//             N/m    pm     aJ

bondrec(1,6,  460.0, 111.3, 0.671, 1.851) # H-C
bondrec(1,8,  460.0,  94.2, 0.753, 1.747) # H-O
bondrec(1,14, 359.4, 125.6, 0.627, 1.693) # H-Si
bondrec(1,16, 360.0, 125.2, 0.606, 1.769) # H-S
bondrec(1,17, 380.0, 134.6, 0.716, 1.628) # H-Cl
bondrec(6,6,  440.0, 152.3, 0.556, 1.989) # C-C
bondrec(6,7,  510.0, 143.8, 0.509, 2.238) # C-N
bondrec(6,8,  536.0, 140.2, 0.575, 2.159) # C-O
bondrec(6,9,  510.0, 139.2, 0.887, 1.695) # C-F
bondrec(6,14, 297.0, 188.0, 0.624, 1.543) # C-Si
bondrec(6,15, 291.0, 185.4, 0.852, 1.306) # C-P
bondrec(6,16, 321.3, 181.5, 0.539, 1.726) # C-S
bondrec(6,17, 323.0, 179.5, 0.591, 1.653) # C-Cl
bondrec(6,35, 230.0, 194.9, 0.488, 1.536) # C-Br
bondrec(7,7,  560.0, 138.1, 0.417, 2.592) # N-N

bondrec(8,8,  781.0, 147.0, 0.272, 3.789) # O-O
bondrec(8,14, 550.0, 162.0, 0.89, 1.757) # O-Si
bondrec(8,15, 290.0, 161.5, 0.994, 1.207) # O-P

bondrec(14,14,185.0, 233.2, 0.559, 1.286) # Si-Si
bondrec(14,16, 219.37, 213.0, 0.58, 1.375) # Si-S
bondrec(16,16, 310.0, 202, 0.706, 1.481) # S-S

for el in Mendeleev:
    for el2 in Mendeleev:
        if el.symbol+el2.symbol in bontab:
            rec = bontab[el.symbol+el2.symbol]
            a="bondrec(%2d, %2d, %6.2f, %5.1f, %6.4f, %5.3f), " % rec
            print a, '//',el.symbol+'-'+el2.symbol

print """};

const int BSTABSIZE = sizeof(bstab) / sizeof(struct bsdata);

struct angben bendata[]={
    
    // atom,order,atom,order,atom, 
    //             zJ/rad^2,  radians
"""
bentab = {}
for el in Mendeleev:
    if el.bonds<2: continue
    for el1 in Mendeleev:
        if el1.bonds<1: continue
        for el2 in Mendeleev:
            if el2.bonds<1: continue
            if el2.symbol+el.symbol+el1.symbol in bentab: continue
            len = el.rcovalent+el1.rcovalent+el2.rcovalent
            kb = min(45e6/len**2+len*1.3-475, 2000)
            th0 = 1.9106
            rec = (el1.eltnum, el.eltnum, el2.eltnum, kb, th0)
            bentab[el1.symbol+el.symbol+el2.symbol] = rec

def benrec(n1,nc,n2,kb,th0):
    name = pertab[n1].symbol+pertab[nc].symbol+pertab[n2].symbol
    
    rec = (n1,nc,n2,kb,th0)
    
    bentab[name]=rec

#// atom,order,atom,order,atom, 
#//             zJ/rad^2,  radians

benrec(6,6,6, 450, 1.911)#	/* C-C-C */
benrec(6,6,1, 360, 1.909)#	/* C-C-H */
benrec(1,6,1, 320, 1.909)#	/* H-C-H */
benrec(6,6,9, 650, 1.911)#	/* C-C-F */
benrec(9,6,9, 1070, 1.869)#	/* F-C-F */
benrec(8,6,8, 460, 1.727)#  O-C-O
benrec(16,6,16, 420, 2.024)#  S-C-S
benrec(6,8,8, 635, 1.722)#  C-O-O
benrec(6,8,15, 770, 2.024)#  C-O-P
benrec(6,8,7, 500, 2.094)#  C-O-N
benrec(6,8,14, 400, 2.000)#  C-O-Si
benrec(14,8,14, 150, 2.44)#  Si-O-Si
benrec(7,8,7, 200, 2.286)#  N-O-N
benrec(15,8,15, 200, 2.826)#  

benrec(6,8,1, 770, 1.864)#	/* C-O-H */
benrec(6,8,6, 770, 1.864)#	/* C-O-C */
benrec(6,7,6, 630, 1.880)#	/* C-N-C */
benrec(6,7,7, 740, 1.841)#  C-N-N

benrec(6,6,8, 700, 1.876)#	/* C-C-O */
benrec(7,6,8, 630, 1.900)#	/* N-C-O */
benrec(6,6,7, 570, 1.911)#	/* C-C-N */
benrec(14,14,14, 350, 1.943)#	/* Si-Si-Si */
benrec(14,16,14, 350, 1.726)#	/* Si-S-Si */
benrec(16,14,16, 350, 1.815)#	/* S-Si-S */
benrec(6,14,8, 350, 1.893)#  C-Si-O
benrec(6,14,14, 750, 1.919)#  C-Si-Si
benrec(8,14,8, 450, 1.980)#  O-Si-O
benrec(14,8,15, 450, 1.726)#  Si-O-P xxx

benrec(14,6,14, 400, 2.016)#	/* Si-C-Si */
benrec(6,14,6, 480, 1.934)#	/* C-Si-C */
benrec(17,6,17, 1080, 1.950)#	/* Cl-C-Cl */
benrec(6,6,16, 550, 1.902)#	/* C-C-S */
benrec(6,16,6, 720, 1.902)#	/* C-S-C */
benrec(6,16,16, 1168, 1.795)#  C-S-S
benrec(6,15,6, 576, 1.675)#  C-P-C
benrec(8,15,8, 450, 1.736)#  O-P-O
benrec(8,15,14, 450, 1.736)#  O-P-Si xxx



for el in Mendeleev:
    if el.bonds<2: continue
    for el1 in Mendeleev:
        if el1.bonds<1: continue
        for el2 in Mendeleev:
            if el2.bonds<1: continue
            if not el1.symbol+el.symbol+el2.symbol in bentab: continue
            lis = bentab[el1.symbol+el.symbol+el2.symbol]
            rec = "    benrec(%2d, %2d, %2d, %4d, %6.4f),	//" % lis
            print rec, el1.symbol+'-'+el.symbol+'-'+el2.symbol
            


print """};

const int BENDATASIZE = sizeof(bendata) / sizeof(struct angben);

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
"""
