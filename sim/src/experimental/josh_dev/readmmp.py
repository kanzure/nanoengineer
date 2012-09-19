# Copyright 2005 Nanorex, Inc.  See LICENSE file for details.
from Numeric import *
from VQT import *
from string import *
import re

keypat = re.compile("(\S+)")
molpat = re.compile("mol \(.*\) (\S\S\S)")
atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")


def readmmp(fname):
    pos = []
    elt = []
    atnum = -1
    atnos = {}
    bonds = []
    for card in open(fname).readlines():
        key = keypat.match(card).group(1)
        if key == 'atom':
            atnum += 1
            m = atompat.match(card)
            atnos[int(m.group(1))] = atnum
            elt += [int(m.group(2))]
            pos += [map(float, [m.group(3),m.group(4),m.group(5)])]
        if key[:4] == 'bond':
            order = ['1','2','3','a','g'].index(key[4])
            bonds += [(atnum,atnos[int(x)],order)
                      for x in re.findall("\d+",card[5:])]
    pos = array(pos)/1000.0
    return elt, pos, array(bonds)
