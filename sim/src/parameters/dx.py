#! /usr/bin/python

from Numeric import *
import sys
import re


recpat = re.compile(" *([\d\.E+-]+) +([\d\.E+-]+) +([\d\.E+-]+)")

f=open(sys.argv[1])
card = f.readline()
m=recpat.match(card)
v=array(map(float,(m.group(1),m.group(2), m.group(3))))
while 1:
    card = f.readline()
    if len(card)<3: break
    m=recpat.match(card)
    w=array(map(float,(m.group(1),m.group(2), m.group(3))))
    print (w-v)[0], (w-v)[1], (w-v)[2]
    v=w


