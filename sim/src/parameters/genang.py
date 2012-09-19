#! /usr/bin/python

import os
import sys
import re
from string import *
from math import sqrt

leftpat=re.compile('([A-Z][a-z]?)([=+#@-])\.moi$')
rightpat=re.compile('([=+#@-])([A-Z][a-z]?)\.moi$')
centerpat=re.compile('([=+#@-])([A-Z][a-z]?)([=+#@-])\.moi$')

thetapat=re.compile(" *theta *= *([\d\.]+)")

parmpat = re.compile("([A-Z][a-z]?)([\+=\-@#])([A-Z][a-z]?) +Ks= *([\d\.]+) +R0= *([\d\.]+) +De= *([\d\.]+)")
commpat = re.compile("#")

pref="""! Gamess control file
 $CONTRL SCFTYP=UHF MAXIT=200 RUNTYP=energy MULT=1 ICHARG=0
ICUT=9 ITOL=20 INTTYP=best COORD=zmt nprint=-5 $END
 $SCF NCONV=5 dirscf=.t. DAMP=.t. SHIFT=.t. DIIS=.T. npunch=0 $END
 $STATPT NSTEP=50 OPTTOL=0.0001 IFREEZ(1)=1,2,3 $END
 $FORCE VIBANL=.f. PRTIFC=.f. $END
 $SYSTEM TIMLIM=10000 MWORDS=250 $END
! $BASIS GBASIS=AM1 $END
 $BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 NPFUNC=1 DIFFSP=.t. $END
 $DFT DFTTYP=B3LYP $END
 $DATA
 *** bending for %s
C1
"""

angs=[('.1',-30),('.2',-20),('.3',-15),('.4',-7),('.5',0),
      ('.6',7),('.7',15),('.8',20),('.9',30)]

bontyp = {'-':'1', '=':'2', '+':'3','@':'a', '#':'g'}

Rzeros={}
f=open('stretch.parms')
for lin in f.readlines():
    if commpat.match(lin): continue
    m = parmpat.match(lin)
    l,b,r = m.group(1),m.group(2),m.group(3)

    ks,r0,de = map(lambda p: float(m.group(p)),[4,5,6])

    Rzeros[l+b+r]=r0
    Rzeros[r+b+l]=r0

lefts = []
rights = []
centers = []

for fn in os.listdir('moieties'):
    if leftpat.match(fn): lefts += [fn]
    if rightpat.match(fn): rights += [fn]
    if centerpat.match(fn): centers += [fn]

### hack
rights = ['-B.moi']

for c in centers:
    m=centerpat.match(c)
    ce=m.group(2)
    clb=m.group(1)
    crb=m.group(3)
    # print c
    for l in lefts:
        m=leftpat.match(l)
        le=m.group(1)
        lb=m.group(2)
        if lb != clb: continue
        # print l
        for r in rights:
            m=rightpat.match(r)
            re=m.group(2)
            rb=m.group(1)
            if rb != crb: continue
            # print r
            name = le+lb+ce+rb+re
            print name
            for nmx,dth in angs:
                of = open(name+nmx+'.inp','w')
                of.write(pref % name)
                cf = open('moieties/'+c)
                thetlin=cf.readline()
                theta = float(thetapat.match(thetlin).group(1)) + dth
                for ln in cf.readlines(): of.write(ln)
                for ln in open('moieties/'+l).readlines(): of.write(ln)
                for ln in open('moieties/'+r).readlines(): of.write(ln)
                of.write('\n')
                of.write(' theta = %f\n' % theta)
                of.write(' dxl = %f\n' % Rzeros[le+lb+ce])
                of.write(' dxr = %f\n' % Rzeros[ce+rb+re])
                of.write(' $END\n')
                of.close()

