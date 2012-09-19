#! /usr/bin/python

# Copyright 2005 Nanorex, Inc.  See LICENSE file for details.
from Numeric import *
from VQT import *
from string import *
import re
import os
import sys

keypat = re.compile("(\S+)")
molpat = re.compile("mol \(.*\) (\S\S\S)")
atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")


def readmmp(fname):
    global atnum, elt, poshape
    pos = []
    elt = []
    atnum = -1
    atnos = {}
    bonds = [(0,0,0)]
    for card in open(fname).readlines():
        key = keypat.match(card).group(1)
        if key == 'atom':
            atnum += 1
            m = atompat.match(card)
            atnos[int(m.group(1))] = atnum
            elt += [int(m.group(2))]
            pos += [[float(m.group(n)) for n in [3,4,5]]]
        if key[:4] == 'bond':
            order = ['1','2','3','a','g'].index(key[4])
            bonds += [(atnum,atnos[int(x)],order)
                      for x in re.findall("\d+",card[5:])]
    pos = transpose(array(pos)/1000.0) # gives angstroms
    poshape = shape(pos)
    return elt, pos, array(bonds)



parmpat = re.compile("([A-Z][a-z]?)([\+=\-@#])([A-Z][a-z]?) +Ks= *([\d\.]+) +R0= *([\d\.]+) +De= *([\d\.]+)")
commpat = re.compile("#")

bendpat = re.compile("([A-Z][a-z]?)([\+=\-@#])([A-Z][a-z]?)([\+=\-@#])([A-Z][a-z]?) +theta0= *([\d\.]+) +Ktheta= *([\d\.]+)")


# masses in 1e-27kg
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

elmass=array([0.0]+[1e-27*x[2] for x in elmnts])

enames=['X']+[x[0] for x in elmnts]

btypes = ['-', '=', '+','@', '#']

def bondstr(elts,triple):
    return enames[elts[triple[0]]]+btypes[triple[2]]+enames[elts[triple[1]]]

def bendstr(elts,quint):
    return (enames[elts[quint[0]]]+btypes[quint[1]]+enames[elts[quint[2]]]
            +btypes[quint[1]]+enames[elts[quint[2]]])
# ks -- N/m
# R0 -- 1e-10 m
# De -- aJ

stretchtable={}
f=open("stretch.parms")
for lin in f.readlines():
    if commpat.match(lin): continue
    m = parmpat.match(lin)
    which = m.group(1)+m.group(2)+m.group(3)
    which1 = m.group(3)+m.group(2)+m.group(1)

    ks,r0,de = [float(m.group(p)) for p in [4,5,6]]

    bt=sqrt(ks/(2.0*de))/10.0
    stretchtable[which] = (ks,r0,de, bt)
    stretchtable[which1] = (ks,r0,de, bt)

# Theta - radians
# Ktheta - aJ/radian^2

bendtable={}
f=open("bending.parms")
for lin in f.readlines():
    if commpat.match(lin): continue
    m = bendpat.match(lin)
    which = m.group(1)+m.group(2)+m.group(3)+m.group(4)+m.group(5)
    which1 = m.group(5)+m.group(4)+m.group(3)+m.group(2)+m.group(1)

    th0, kth = [float(m.group(p)) for p in [6,7]]
    kth *= 100.0
    bendtable[which] = (th0, kth)
    bendtable[which1] = (th0, kth)

# given a set of stretch bonds, return the bend quintuples
def bondsetup(bonds):
    global bond0, bond1, KS, R0
    global sort0,mash0,spred0, sort1,mash1,spred1
    global bends, Theta0, Ktheta, bba, bbb, bbc
    global bbsorta, bbmasha, bbputa
    global bbsortb, bbmashb, bbputb
    global bbsortc, bbmashc, bbputc

    n = atnum+1

    bond0 = bonds[:,0]
    bond1 = bonds[:,1]

    sort0 = argsort(bond0)
    x0=take(bond0,sort0)
    x=x0[1:]!=x0[:-1]
    x[0]=1
    x=compress(x,arange(len(x)))
    mash0=concatenate((array([0]),x+1))
    spred0=zeros(n)
    x=take(x0,mash0[1:])
    put(spred0,x,1+arange(len(x)))

    sort1 = argsort(bond1)
    x1=take(bond1,sort1)
    x=x1[1:]!=x1[:-1]
    x[0]=1
    x=compress(x,arange(len(x)))
    mash1=concatenate((array([0]),x+1))
    spred1=zeros(n)
    x=take(x1,mash1[1:])
    put(spred1,x,1+arange(len(x)))

    btlis = [bondstr(elt,x) for x in bonds]
    KS = array([stretchtable[x][0] for x in btlis])
    KS[0]=0.0
    R0 = array([stretchtable[x][1] for x in btlis])
    R0[0]=0.0

    bondict = {}
    bends = []
    for (a,b,o) in bonds[1:]:
        bondict[a] = bondict.get(a,[]) + [(o,b)]
        bondict[b] = bondict.get(b,[]) + [(o,a)]
    for (a,lis) in bondict.iteritems():
        for i in range(len(lis)-1):
            (ob,b) = lis[i]
            for (oc,c) in lis[i+1:]:
                bends += [(b,ob,a,oc,c)]
    bends = array(bends)
    bba = bends[:,0]
    bbb = bends[:,4]
    bbc = bends[:,2]
    bnlis = [bendstr(elt,x) for x in bends]
    Theta0 = array([bendtable[b][0] for b in bnlis])
    Ktheta = array([bendtable[b][1] for b in bnlis])

    n=len(elt)

    bbsorta = argsort(bba)
    x1=take(bba,bbsorta)
    x2=x1[1:]!=x1[:-1]
    x=compress(x2,arange(len(x2)))
    bbmasha=concatenate((array([0]),x+1))
    bbputa = compress(concatenate((array([1]),x2)),x1)
    bbputa = concatenate((bbputa, n+bbputa, 2*n+bbputa))

    bbsortb = argsort(bbb)
    x1=take(bbb,bbsortb)
    x2=x1[1:]!=x1[:-1]
    x=compress(x2,arange(len(x2)))
    bbmashb=concatenate((array([0]),x+1))
    bbputb = compress(concatenate((array([1]),x2)),x1)
    bbputb = concatenate((bbputb, n+bbputb, 2*n+bbputb))

    bbsortc = argsort(bbc)
    x1=take(bbc,bbsortc)
    x2=x1[1:]!=x1[:-1]
    x=compress(x2,arange(len(x2)))
    bbmashc=concatenate((array([0]),x+1))
    bbputc = compress(concatenate((array([1]),x2)),x1)
    bbputc = concatenate((bbputc, n+bbputc, 2*n+bbputc))

    return bends


# aa means stretch bond (atom-atom)
# bb means bend (bond-bond)
# bba, bbb, bbc are the three atoms in a bend, bbc the center
#
#globals: bond0, bond1: atom #'s; R0s; KSs
def force(pos):
    aavx = take(pos,bond0,1) - take(pos,bond1,1)
    aax = sqrt(add.reduce(aavx*aavx))
    aax[0]=1.0

    aavu = aavx/aax
    aavf = aavu * KS * (R0 - aax)

    avf0 = add.reduceat(take(aavf,sort0,1),mash0)
    avf1 = add.reduceat(take(aavf,sort1,1),mash1)
    f = take(avf0,spred0,1) - take(avf1,spred1,1)

    bbva = take(pos,bba,1) - take(pos,bbc,1)
    bbvb = take(pos,bbb,1) - take(pos,bbc,1)
    bbla = sqrt(add.reduce(bbva*bbva))
    bblb = sqrt(add.reduce(bbvb*bbvb))
    bbau = bbva/bbla
    bbbu = bbvb/bblb
    bbadb = add.reduce(bbau*bbbu)
    angle = arccos(bbadb)
    torq = Ktheta*(angle-Theta0)

    bbaf = bbbu-bbadb*bbau
    bbaf = bbaf/sqrt(add.reduce(bbaf*bbaf))
    bbaf = bbaf*torq/bbla
    bbbf = bbau-bbadb*bbbu
    bbbf = bbbf/sqrt(add.reduce(bbbf*bbbf))
    bbbf = bbbf*torq/bblb

    fa = zeros(poshape,Float)
    put(fa,bbputa,add.reduceat(take(bbaf,bbsorta,1),bbmasha))
    fc1 = zeros(poshape,Float)
    put(fc1,bbputc,add.reduceat(take(bbaf,bbsortc,1),bbmashc))

    fb = zeros(poshape,Float)
    put(fb,bbputb,add.reduceat(take(bbbf,bbsortb,1),bbmashb))
    fc2 = zeros(poshape,Float)
    put(fc2,bbputc,add.reduceat(take(bbbf,bbsortc,1),bbmashc))

    return f+fa+fb-fc1-fc2


