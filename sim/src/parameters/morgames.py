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
termpat = re.compile(" EXECUTION OF GAMESS TERMINATED")
failpat = re.compile("-ABNORMALLY-")
blankpat = re.compile("\s*$")
potpat = re.compile("     POTENTIAL SURFACE MAP INPUT")
hevpat = re.compile(" HAS ENERGY VALUE +([\d\.-]+)")
smgpat = re.compile(" ---- SURFACE MAPPING GEOMETRY ----")
alphpat = re.compile(" *ALPH *[\d\.-]+ *[\d\.-]+ *([\d\.-]+)")
betapat = re.compile(" +\d+ +BETA +([\d\.]+)")
c1pat = re.compile("  \d  C    +([\d\.]+)")
b3pat = re.compile(" FINAL U-B3LYP ENERGY IS +([\d\.-]+)")
equilpat = re.compile("1     \*\*\*\*\* EQUILIBRIUM GEOMETRY LOCATED \*\*\*\*\*")
erecpat = re.compile("E\=\ +([\d\.-]+)\ +GMAX\=\ +([\d\.-]+)\ +GRMS\=\ +([\d\.-]+)")
frecpat = re.compile(".+\ +\d+\.\ +([\d\.E+-]+)\ +([\d\.E+-]+)\ +([\d\.E+-]+)")
irecpat = re.compile(" (\w+) +\d+\.\d* +([\d\.E+-]+) +([\d\.E+-]+) +([\d\.E+-]+)")
grecpat = re.compile("\w+ +\d+\.\d* +([\d\.E+-]+) +([\d\.E+-]+) +([\d\.E+-]+)")
xyzpat = re.compile("(\w+) +([\d\.E+-]+) +([\d\.E+-]+) +([\d\.E+-]+)")
pdbname= re.compile("([^\.]+)\.pdb")
xyzname= re.compile("([^\.]+)\.xyz")
inpname= re.compile("([^\.]+)\.inp")
moiname= re.compile("(\w+)([=\-\+])\.moi$")


am1p = re.compile("GBASIS=AM1")

preface="""! Gamess control file
 $CONTRL SCFTYP=UHF MAXIT=200 RUNTYP=surface MULT=1 ICHARG=0
ICUT=9 ITOL=20 INTTYP=best NPRINT=-5 $END
 $SCF NCONV=8 dirscf=.t. DAMP=.t. SHIFT=.t. DIIS=.T. SOSCF=.T. npunch=0 $END
 $STATPT NSTEP=50 OPTTOL=0.0001 $END
 $FORCE VIBANL=.f. PRTIFC=.f. $END
 $SYSTEM TIMLIM=10000 MWORDS=250 $END
 $BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 NPFUNC=1 DIFFSP=.t. $END
 $DFT DFTTYP=B3LYP $END
"""

triplet="""! Gamess control file
 $CONTRL SCFTYP=UHF MAXIT=200 RUNTYP=energy MULT=3 ICHARG=0
ICUT=9 ITOL=20 INTTYP=best NPRINT=-5 $END
 $SCF NCONV=5 dirscf=.t. DAMP=.t. SHIFT=.t. DIIS=.T. SOSCF=.T. npunch=0 $END
 $STATPT NSTEP=50 OPTTOL=0.0001 $END
 $FORCE VIBANL=.f. PRTIFC=.f. $END
 $SYSTEM TIMLIM=10000 MWORDS=250 $END
 $BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 NPFUNC=1 DIFFSP=.t. $END
 $DFT DFTTYP=B3LYP $END
"""

# distances are in angstroms, and delta T is 1e-16 seconds

# gradients from Gamess are given in Hartrees/Bohr. To convert to N:
gradU = 82.38729477e-9

Hartree = 4.3597482 # attoJoules
Bohr = 0.5291772083 # Angstroms


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

def findnext(f,pat):
    while 1:
        card = f.readline()
        if not card: return None
        m = pat.match(card)
        if m: return m

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

# read a moiety, consisting of a chunk of a $data section only
def moiread(fname):

    f=open(fname+'.moi',"r")

    atoms = zeros((0,3),Float)
    elem = []

    while 1:
        card = f.readline()
        if blankpat.match(card): break
        m=irecpat.match(card)
        elem += [capitalize(m.group(1))]

        v=A([map(float,(m.group(2),m.group(3), m.group(4)))])
        atoms = concatenate((atoms,v),axis=0)

    f.close()
    return elem, atoms

def inpread(fname):

    f=open(fname+'.inp',"r")

    atoms = zeros((0,3),Float)
    elem = []
    preface=""
    postface=""

    while 1:
        card = f.readline()
        preface += card
        if datapat.match(card): break

    preface += f.readline() # the comment line
    preface += f.readline() # the C1 line

    while 1:
        card = f.readline()
        if endpat.match(card): break
        m=irecpat.match(card)
        elem += [capitalize(m.group(1))]

        v=A([map(float,(m.group(2),m.group(3), m.group(4)))])
        atoms = concatenate((atoms,v),axis=0)

    postface = card
    f.close()
    return elem, atoms

def absetup(e1, e2):
     sym2num['ALPH']= sym2num[e1[0]]
     sym2num['BETA']= sym2num[e2[0]]
     e1[0] = 'ALPH'
     e2[0] = 'BETA'
     return e1, e2

def inpwrite(fname, elem, pos, pref=" $DATA\nComment\nC1\n"):
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


def xeread(name):
    f=open(name+'.log',"r")
    x = []
    e= []
    t = False
    findnext(f, potpat)

    while 1:
        m = findnext(f, betapat)
        m1 = findnext(f,hevpat)
        if not (m and m1): break
        x += [float(m.group(1))]
        e += [float(m1.group(1))*Hartree]

    f.close()
    return x,e


def logread(name):
    f=open(name+'.log',"r")
    while 1:
        card = f.readline()
        if failpat.search(card):
            print card
            sys.exit(1)
        if card == "1     ***** EQUILIBRIUM GEOMETRY LOCATED *****\n": break
        if card == " **** THE GEOMETRY SEARCH IS NOT CONVERGED! ****":
            print card
            sys.exit(1)
    f.readline() # COORDINATES OF ALL ATOMS ARE (ANGS)
    f.readline() #    ATOM   CHARGE       X              Y              Z
    f.readline() #  ------------------------------------------------------------

    atoms = zeros((0,3),Float)
    elem = []

    while 1:
        card = f.readline()
        if len(card)<10: break
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
    files = os.listdir('.')
    for file in files:
        x = xyzname.match(file)
        if x: xyzs[x.group(1)] = True
    for file in files:
        x = pdbname.match(file)
        if x and not x.group(1) in xyzs:
            print 'Making',x.group(1)+'.xyz'
            os.system("pdb2xyz " + x.group(1))

def fexist(fname):
    try: os.stat(fname)
    except OSError: return False
    return True


def dirsetup():
    print "making input files:"
    files = os.listdir('.')
    for file in files:
        x = xyzname.match(file)
        if x:
            name = x.group(1)
            if fexist('level0/'+name+'.inp'): continue
            elems, atoms = xyzread(open(name+'.xyz'))
            inpwrite('level0/'+name, elems, atoms)

def dorunrun(n):
    print "running Gamess at level",n
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
        if fexist(tname+'.inp'): continue
        if fexist(fname+'.log'): elem, atoms = logread(fname)
        else: elem, atoms = inpread(fname)
        rungms(tname, elem, atoms, header)

De=0.556
# R0=1.523
Beta=1.989
def morse(r,de,beta, R0):
    return de*(1-exp(-beta*(r-R0)))**2

def diff(de, e, x, ix, Ks, R0):
    sum = 0.0
    beta = sqrt(Ks/(2.0*de)) /10.0
    for i in range(ix):
        sum += (e[i]-morse(x[i],de,beta, R0))**2
    return sum

def quadmin(a,fa,b,fb,c,fc):
    num =  (b-a)**2 * (fb-fc) - (b-c)**2 * (fb-fa)
    den =  (b-a)    * (fb-fc) - (b-c)    * (fb-fa)
    if den == 0.0: return b
    return b - num / (2*den)

def golden(f,a,fa,b,fb,c,fc, tol=1e-2):

##     print 'Searching:',a,b,c
##     print '[',fa, fb, fc,']'

    if c-a<tol: return quadmin(a,fa,b,fb,c,fc)
    if c-b > b-a:
        new = b+0.38197*(c-b)
        fnew = f(new)
        if fnew < fb: return golden(f, b,fb, new,fnew, c,fc)
        else: return golden(f, a,fa, b,fb, new, fnew)
    else:
        new = a+0.61803*(b-a)
        fnew = f(new)
        if fnew < fb: return golden(f, a, fa, new,fnew, b,fb)
        else: return golden(f, new, fnew, b,fb, c,fc)

def texvec(v):
    if len(v)>1: return str(v[0])+','+texvec(v[1:])
    if v: return str(v[0])
    return ''

def surfgen(fqbn, x1, x2):
    b = " $SURF ivec1(1)=1,"+str(1+len(x1))
    b += " igrp1(1)="+texvec(map(lambda x: 1+len(x1)+x, range(len(x2))))
    dx = x1[0][2]+x2[0][2]
    b += "\n orig1="+str(-0.33*dx)
    b += " disp1="+str(dx*0.01)+" ndisp1=50 $END\n"
    b += " $DATA\n *** Parm Gen for "+fqbn+"\nC1\n"
    return b

def enggen(fqbn):
    return " $DATA\n *** Separated energy for "+fqbn+"\nC1\n"

def surfread(filnam, zero):
    x,e = xeread('bonds/'+filnam)


    # find lowest point
    lo=e[0]
    ix=0
    for i in range(len(x)):
        if e[i] < lo:
            lo=e[i]
            ix=i
    # take it and its neighbors for parabolic interpolation
    a = x[ix-1]
    fa= e[ix-1]
    b = x[ix]
    fb= e[ix]
    c = x[ix+1]
    fc= e[ix+1]

    # the lowest point on the parabola
    R0 = quadmin(a,fa,b,fb,c,fc)

    # its value via Lagrange's formula
    fR0 = (fa*((R0-b)*(R0-c))/((a-b)*(a-c)) +
           fb*((R0-a)*(R0-c))/((b-a)*(b-c)) +
           fc*((R0-a)*(R0-b))/((c-a)*(c-b)))

    # adjust points to min of 0
    for i in range(len(x)):
        e[i]=e[i]-fR0

    fa= e[ix-1]
    fb= e[ix]
    fc= e[ix+1]

    # stiffness, interpolated between two triples of points
    # this assumes equally spaced abcissas
    num = (b - a)*fc + (a - c)*fb + (c - b)*fa
    den = (b - a)* c**2  + (a**2  - b**2 )*c + a*b**2  - a**2 * b
    Ks1 = 200.0 * num / den

    ob = b
    if R0>b: ix += 1
    else: ix -= 1
    a = x[ix-1]
    fa= e[ix-1]
    b = x[ix]
    fb= e[ix]
    c = x[ix+1]
    fc= e[ix+1]
    num = (b - a)*fc + (a - c)*fb + (c - b)*fa
    den = (b - a)* c**2  + (a**2  - b**2 )*c + a*b**2  - a**2 * b
    Ks2 = 200.0 * num / den

    Ks = Ks1 + (Ks2-Ks1)*(R0-ob)/(b-ob)

    # now search for De by fitting a morse curve to the points

    delo = 0.2
    dehi = 1.7
    demd = delo + 0.61803*(dehi-delo)
    De = golden(lambda d: diff(d, e, x, ix, Ks, R0),
                delo, diff(delo, e, x, ix, Ks, R0),
                demd, diff(demd, e, x, ix, Ks, R0),
                dehi, diff(dehi, e, x, ix, Ks, R0))

    if zero != 0.0: De = zero-fR0
    Beta=sqrt(Ks/(2.0*De))/10.0
    return Ks, R0, De

def deread(nam):
    f=open('bonds/'+nam+'.De.log','r')
    z=0.0
    while 1:
        m=findnext(f, b3pat)
        if not m: break
        q=float(m.group(1))
        if q != 0.0: z=q*Hartree
    return z

## if __name__ == "__main__":
##     files = os.listdir('moieties')
##     for i in range(len(files)):
##         f1 = moiname.match(files[i])
##         if f1:
##             f1el, f1bn = f1.groups()
##             for f2 in files[i:]:
##                 m = moiname.match(f2)
##                 if not m: continue
##                 f2el, f2bn = m.groups()
##                 if f1bn != f2bn: continue
##                 fqbn=f1el+f1bn+f2el
##                 #if fexist('bonds/'+fqbn+'.parms'): continue
##                 print 'Doing',fqbn
##                 el, pos = moiread('moieties/'+f1el+f1bn)
##                 el2, pos2 = moiread('moieties/'+f2el+f2bn)
##                 #el, el2 = absetup(el, el2)
##                 rungms('bonds/'+fqbn+'.De',
##                        el+el2,
##                        concatenate((pos+V(0,0,4), -pos2),axis=0),
##                        triplet+enggen(fqbn))

if __name__ == "__main__":
    files = os.listdir('bonds')
    logfiles = filter(lambda x: x[-4:]=='.log', files)
    defiles = filter(lambda x: x[-7:]=='.De.log', logfiles)
    logfiles = filter(lambda x: x not in defiles, logfiles)
    fn = map(lambda x: x[:-4], logfiles)
    for f in fn:
        if fexist('bonds/'+f+'.De.log'): zero = deread(f)
        else: zero=0.0
        if zero==0.0: print '###',f,'-- no energy zero'
        print f,'Ks=%7.2f R0=%7.4f De=%7.4f' % surfread(f,zero)
