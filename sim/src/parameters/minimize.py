#! /usr/bin/python

from Numeric import *
from VQT import *
from LinearAlgebra import *
from string import *
import re
import os
import sys
from struct import pack
from stat import *

datapat = re.compile("\ \$DATA")
gradpat = re.compile("\ \$GRAD")
hesspat = re.compile(" \$HESS")
vecpat = re.compile(" \$VEC")
endpat = re.compile("\ \$END")
failpat = re.compile("-ABNORMALLY-")
blankpat = re.compile("\s*$")
equilpat = re.compile("1     \*\*\*\*\* EQUILIBRIUM GEOMETRY LOCATED \*\*\*\*\*")
coordpat = re.compile(" COORDINATES")
erecpat = re.compile("E\=\ +([\d\.-]+)\ +GMAX\=\ +([\d\.-]+)\ +GRMS\=\ +([\d\.-]+)")
frecpat = re.compile(".+\ +\d+\.\ +([\d\.E+-]+)\ +([\d\.E+-]+)\ +([\d\.E+-]+)")
irecpat = re.compile(" (\w+) +\d+\.\d* +([\d\.E+-]+) +([\d\.E+-]+) +([\d\.E+-]+)")
xyzpat = re.compile("(\w+) +([\d\.E+-]+) +([\d\.E+-]+) +([\d\.E+-]+)")
pdbname= re.compile("([^\.]+)\.pdb")
xyzname= re.compile("([^\.]+)\.xyz")
inpname= re.compile("([^\.]+)\.inp")

am1p = re.compile("GBASIS=AM1")

preface=["""! Gamess control file
 $CONTRL SCFTYP=RHF MAXIT=200 RUNTYP=optimize MULT=1 ICHARG=0
ICUT=9 ITOL=20 INTTYP=best NPRINT=-5 $END
 $SCF NCONV=8 dirscf=.t. DAMP=.t. SHIFT=.t. DIIS=.T. SOSCF=.T. npunch=0 $END
 $STATPT NSTEP=50 OPTTOL=0.0001 $END
 $FORCE VIBANL=.f. PRTIFC=.f. METHOD=analytic $END
 $SYSTEM TIMLIM=10000 MWORDS=250 $END
""",
        """! Gamess control file
 $CONTRL SCFTYP=RHF MAXIT=500 RUNTYP=energy MULT=1 ICHARG=0
ICUT=9 ITOL=20 INTTYP=best NPRINT=-5 $END
 $SCF NCONV=8 dirscf=.t. DAMP=.t. SHIFT=.t. DIIS=.T. SOSCF=.T. npunch=0 $END
 $FORCE VIBANL=.f. PRTIFC=.f. METHOD=analytic $END
 $SYSTEM TIMLIM=10000 MWORDS=250 $END
""",
        """! Gamess control file
 $CONTRL SCFTYP=RHF MAXIT=500 RUNTYP=optimize MULT=1 ICHARG=0
ICUT=9 ITOL=20 INTTYP=best NPRINT=-5 $END
 $SCF NCONV=8 dirscf=.t. DAMP=.t. SHIFT=.t. DIIS=.T. SOSCF=.T. npunch=0 $END
 $STATPT NSTEP=50 OPTTOL=0.0001 HSSEND=.true. $END
 $FORCE VIBANL=.f. PRTIFC=.f. METHOD=seminum $END
 $SYSTEM TIMLIM=10000 MWORDS=250 $END
"""]
preface2=" $DATA\nGamess theory ladder: "
preface3="\nC1\n"
postface=""" $END
"""
dftface=""" $DFT DFTTYP=B3LYP $END
"""
levels=[" $BASIS GBASIS=AM1 $END\n",
        " $BASIS GBASIS=N21 NGAUSS=3 $END\n",
        " $BASIS GBASIS=N31 NGAUSS=6 $END\n",
        " $BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 NPFUNC=1 $END\n",
        " $BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 NPFUNC=1 DIFFSP=.t. $END\n",
        " $BASIS GBASIS=N311 NGAUSS=6 NDFUNC=2 NPFUNC=2 DIFFSP=.t. $END\n"
        ]
schedule=[#[0, 0, 0, " am1, no dft"],
          [2, 0, 0, " am1, hessian"],
          [0, 1, 1, " 3-21G, b3lyp"]]
##           [0, 2, 1, " 6-31G, b3lyp"],
##           [0, 3, 1, " 6-31G(d,p), b3lyp"],
##           [0, 3, 1, " 6-31G(d,p), b3lyp"],
##           [0, 4, 1, " 6-31+G(d,p), b3lyp"],
##           [1, 5, 1, " 6-31+G(2d,2p), b3lyp, single point energy"]]


# distances are in angstroms, and delta T is 1e-16 seconds

# gradients from Gamess are given in Hartrees/Bohr. To convert to N:
gradU = 82.38729477e-9

# given in 1e-27 kg
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
num2mass=[0]
for (sym, num, mass) in elmnts:
    sym2num[sym] = num
    num2mass += [mass]

def datread(fname):
    f=open(fname,"r")

    grads=zeros((0,3),Float)

    while 1:
        card = f.readline()
        if gradpat.match(card): break

    f.readline() # R= ...

    while 1:
        card = f.readline()
        if endpat.match(card): break
        m=frecpat.match(card)
        v=A([map(float,(m.group(1),m.group(2), m.group(3)))])
        grads = concatenate((grads,v),axis=0)

    f.close()
    return grads

def inpread(fname):

    f=open(fname+'.inp',"r")

    atoms = zeros((0,3),Float)
    elem = []
    preface=" $DATA\n"
    postface=""

    while 1:
        card = f.readline()
        if datapat.match(card): break

    preface += f.readline() # the comment line
    preface += f.readline() # the symmetry line

    while 1:
        card = f.readline()
        if blankpat.match(card):
            preface += card # if non-C1 sym
            continue
        if endpat.match(card): break
        m=irecpat.match(card)
        elem += [m.group(1)]

        v=A([map(float,(m.group(2),m.group(3), m.group(4)))])
        atoms = concatenate((atoms,v),axis=0)

    postface = card
    f.close()
    return elem, atoms, preface

def inpwrite(fname, elem, pos, pref=" $DATA\ncomment\nC1\n"):
    f=open(fname+'.inp',"w")
    f.write(pref)

    for i in range(len(elem)):
        f.write(" %-10s %2d." % (elem[i], sym2num[elem[i]]) +
                " %12.7f %12.7f %12.7f" % tuple(pos[i]) + "\n")

    f.write(" $END\n")
    f.close()

def xyzread(f):
    n=int(f.readline())
    elems=[]
    atoms = zeros((n,3),Float)
    f.readline() # skip comment line
    for i in range(n):
        m=xyzpat.match(f.readline())
        elems += [capitalize(m.group(1))]
        atoms[i]=A(map(float,(m.group(2),m.group(3), m.group(4))))
    return elems, atoms

def xyzwrite(f, elem, pos):
    f.write(str(len(elem))+"\n--comment line--\n")
    for i in range(len(elem)):
        f.write(elem[i] + " %12.7f %12.7f %12.7f" % tuple(pos[i]) + "\n")

def logread(name):
    f=open(name+'.log',"r")
    while 1:
        card = f.readline()
        if failpat.search(card):
            print 'GAMESS bombs in',name
            return None, None
        if card == "1     ***** EQUILIBRIUM GEOMETRY LOCATED *****\n": break
        if card == " **** THE GEOMETRY SEARCH IS NOT CONVERGED! ****":
            print 'GAMESS bombs in',name
            return None, None

    f.readline() # COORDINATES ...
    f.readline() #    ATOM   CHARGE       X              Y              Z
    f.readline() #  ------------------------------------------------------------

    atoms = zeros((0,3),Float)
    elem = []

    while 1:
        card = f.readline()
        if len(card)<10: break
        if coordpat.match(card): break
        m=irecpat.match(card)
        elem += [capitalize(m.group(1))]

        v=A([map(float,(m.group(2),m.group(3), m.group(4)))])
        atoms = concatenate((atoms,v),axis=0)

    return elem, atoms


def dpbwrite(f, pos):
    global ipos
    npos=floor(pos*100)
    delta=npos-ipos
    ipos = npos
    for line in delta:
        f.write(pack("bbb",int(line[0]),int(line[1]),int(line[2])))

def rungms(name, elem, pos, pref):
    print "*****  running",name,"   *****"
    inpwrite(name, elem, pos, pref)
    if am1p.search(pref):
        os.system("rungms "+name+" 1 > "+name+".log")
    else:
        os.system("rcp "+name+".inp cluster:/home/josh/working.inp")
        os.system("rsh cluster /home/gamess32/rungms working Nov222004R1 4 >"+name+".log")
    return name

def makexyz():
    print "making xyz files:"
    xyzs = {}
    files = os.listdir('level0')
    for file in files:
        x = xyzname.match(file)
        if x: xyzs[x.group(1)] = True
    for file in files:
        x = pdbname.match(file)
        if x and not x.group(1) in xyzs:
            print 'Making',x.group(1)+'.xyz'
            os.system("pdb2xyz " + 'level0/'+x.group(1))

def fexist(fname):
    try: os.stat(fname)
    except OSError: return False
    return True


def dirsetup():
    print "making input files:"
    files = os.listdir('level0')
    for file in files:
        x = xyzname.match(file)
        if x:
            name = x.group(1)
            if fexist('level0/'+name+'.inp'): continue
            elems, atoms = xyzread(open('level0/'+name+'.xyz'))
            inpwrite('level0/'+name, elems, atoms)

def dorunrun(n):
    print "\nrunning Gamess at level",n
    fd = 'level'+str(n-1)
    td = 'level'+str(n)
    header = open(td+'/theory').read()
    files = os.listdir(fd)
    for file in files:
        x = inpname.match(file)
        if not x: continue
        name = x.group(1)
        fname = fd+'/'+name
        tname = td+'/'+name
        if fexist(tname+'.log'): continue
        elem, atoms, pref = inpread(fname)
        if fexist(fname+'.log'): elem, atoms = logread(fname)
        if elem: rungms(tname, elem, atoms, header+pref)



if __name__ == "__main__":
    makexyz()
    dirsetup()
    n=1
    while 1:
        dorunrun(n)
        n += 1
        if not fexist('level'+str(n)): break

