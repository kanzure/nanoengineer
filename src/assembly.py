from Numeric import *
from VQT import *
from string import *
import re
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from struct import unpack

from drawer import drawsphere, drawcylinder, drawline, drawaxes
from drawer import segstart, drawsegment, segend, drawwirecube
from shape import *
from chem import *
from gadgets import *

# number of atoms for detail level 0
HUGE_MODEL = 20000
# number of atoms for detail level 1
LARGE_MODEL = 5000

# the class for groups of parts (molecules)
# currently only one level, but should be recursive
class assembly:
    def __init__(self, nm=None):
        # nothing is done with this now, but should have a
        # control for browsing/managing the list
        global assyList
        assyList += [self]
        # the Form1's displaying this assembly. 
        # breaks currently if there is more than 1!
        self.windows = []
        # list of chem.molecule's
        self.molecules=[]
        # list of the atoms, only valid just after read or write
        self.alist = [] #None
        # filename if this was read from a file
        self.filename= None
        # the name if any
        self.name = nm or gensym("Assembly")
        # to be shrunk, see addmol
        self.bboxhi=V(-1000,-1000,-1000)
        self.bboxlo=V(1000,1000,1000)
        self.center=V(0,0,0)
        # dictionary of selected atoms (indexed by atom.key)
        self.selatoms={}
        # list of selected molecules
        self.selmols=[]
        # level of detail to draw
        self.drawLevel = 2
        # currently unimplemented
        self.selmotors=[]
        self.undolist=[]

    # convert absolute atom positions to relative, find
    # bounding boxes, do some housekeeping

    def addmol(self,mol):
        mol.shakedown()
        self.bboxhi = maximum(self.bboxhi, mol.bboxhi+mol.center)
        self.bboxlo = minimum(self.bboxlo, mol.bboxlo+mol.center)
        self.center = (self.bboxhi+self.bboxlo)/2
        self.molecules += [mol]

        self.setDrawLevel()
        
    ## Calculate the number of atoms in an assembly, which is used to
    ## control the detail level of sphere subdivision
    def setDrawLevel(self):

        num = 0
        for mol in self.molecules:
	    num += len(mol.atoms)
        self.drawLevel = 2
	if num > LARGE_MODEL: self.drawLevel = 1
	if num > HUGE_MODEL: self.drawLevel = 0


    # to draw, just draw everything inside
    ## get the number of atoms to decide what detail level of subdivison we'll use
    def draw(self, win):

        for mol in self.molecules:
            mol.draw(win, self.drawLevel)

    # update all the displays we're connected to
    def updateDisplays(self):
        mollist = []
        for m in self.molecules:
            if m.havelist == 0: mollist += [m]
        for win in self.windows:
            for m in mollist: m.changeapp()
            win.glpane.paintGL()
           
    # write a povray file: just draw everything inside
    def povwrite(self,file,win):
        for mol in self.molecules:
            mol.povwrite(file,win)

    # make a new molecule using a cookie-cut shape
    def molmake(self,shap):
        mol = molecule(self, gensym("handrawn"))
        ndx={}
        sp=1.7586
        sp2 = sp * 0.5
        lo = floor(shap.bboxlo / sp)
        ilo = map(int, lo)
        ioff = (sum(ilo)+1) % 2
        lo = sp * lo
        ihi = map(int, ceil(shap.bboxhi / sp))
        for i in range(ilo[0], ihi[0]+1):
            for j in range(ilo[1], ihi[1]+1):
                for k in range(ilo[2], ihi[2]+1):
                    if (i+j+k+ioff)%2:
                        abc=V(i,j,k)*sp
                        a1=None
                        if shap.isin(abc):
                            a1 = atom("C", abc, mol)
                            ndx[(i,j,k)]=a1
                            try: q = ndx[(i+1,j,k)]
                            except KeyError: pass
                            else: mol.bond(a1,q)
                            try: q = ndx[(i,j+1,k)]
                            except KeyError: pass
                            else: mol.bond(a1,q)
                            try: q = ndx[(i,j,k+1)]
                            except KeyError: pass
                            else: mol.bond(a1,q)
                        if shap.isin(abc+sp2):
                            a2 = atom("C", abc+sp2, mol)
                            ndx[(i+1,j+1,k+1)]=a2
                            if a1: mol.bond(a1,a2)
        self.addmol(mol)
        mol.pick()

    # read a Protein DataBank-format file into a single molecule
    def readpdb(self,filename):
        l=open(filename,"r").readlines()
        self.filename=filename
        alist=[]
        ndix={}
        mol=molecule(self, filename)
        for card in l:
            key=card[:6].lower().replace(" ", "")
            if key in ["atom", "hetatm"]:
                sym = capitalize(card[12:14].replace(" ", "").replace("_", ""))
                try: PeriodicTable[sym]
                except KeyError: print 'unknown element "',sym,'" in: ',card
                else:
                    xyz = map(float, [card[30:38],card[38:46],card[46:54]])
                    n=int(card[6:11])
                    a=atom(sym, A(xyz), mol)
                    ndix[n]=a
            elif key == "conect":
                a1=ndix[int(card[6:11])]
                for i in range(11, 70, 5):
                    try: a2=ndix[int(card[i:i+5])]
                    except ValueError: break
                    mol.bond(a1, a2)
        self.addmol(mol)

    # read a Molecular Machine Part-format file into maybe multiple molecules
    def readmmp(self,filnam):
        l=open(filnam,"r").readlines()
        self.filename=filnam
        mol = None
        ndix={}
        self.alist = []

        for card in l:
            key=card[:4]
            if key=="part":
                if mol: self.addmol(mol)
                m=re.search("(\(\s+\))", card[8:])
                mol=molecule(self, m and m.group(1))
                mol.display = ["def", 'nil', "lin", 'bns', 'vdw'].index(card[5:8]) - 1
            elif key == "atom":
                m=re.match("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)"
                           ,card)
                n=int(m.group(1))
                sym=Mendeleev[int(m.group(2))].symbol
                xyz=A(map(float, [m.group(3),m.group(4),m.group(5)]))/1000.0
                a=atom(sym, xyz, mol)
                self.alist += [a]
                ndix[n]=a
                prevatom=a
                prevcard = card
            elif key == "bond":
                list=map(int, re.findall("\d+",card[5:]))
                try:
                    for a in map((lambda n: ndix[n]), list):
                        mol.bond(prevatom, a)
                except KeyError:
                    print "error in MMP file: atom ", prevcard
                    print card
            elif key[:3] == "end":
                if mol: self.addmol(mol)
            elif key == "moto":
                if mol:
                    self.addmol(mol)
                    mol = None
                m=re.match("motor (-?\d+\.\d+), (-?\d+\.\d+), \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)", card)
                torq=float(m.group(1))
                sped=float(m.group(2))
                cxyz=A(map(float, [m.group(3),m.group(4),m.group(5)]))/1000.0
                axyz=A(map(float, [m.group(6),m.group(7),m.group(8)]))/1000.0
                prevmotor=motor(self)
                prevmotor.setcenter(torq, sped, cxyz, axyz)
            elif key == "shaf":
                list = map(int, re.findall("\d+",card[6:]))
                list = map((lambda n: ndix[n]), list)
                prevmotor.setshaft(list)
            elif key == "grou":
                if mol:
                    self.addmol(mol)
                    mol = None
                list = map(int, re.findall("\d+",card[7:]))
                list = map((lambda n: ndix[n]), list)
                ground(self, list)

    # write all molecules, motors, grounds into an MMP file
    def writemmp(self,filename):
        f=open(filename,"w")
        atnums = {}
        atnum = 1
        self.alist = []
        for mol in self.molecules:
            carrydisp = ("nil", "lin", "bns", "vdw")[mol.display]
            f.write("part " + carrydisp + " (" + mol.name + ")\n")
            for a in mol.atoms.itervalues():
                self.alist += [a]
                atnums[a.key] = atnum
                if a.display >= 0:
                    disp = ("nil", "lin", "bns", "vdw")[a.display]
                else: disp = ("nil", "lin", "bns", "vdw")[mol.display]
                if disp != carrydisp:
                    f.write("show " + disp + "\n")
                    carrydisp = disp
                xyz=a.posn()*1000
                n=(atnum, a.element.atnum,
                   int(xyz[0]), int(xyz[1]), int(xyz[2]))
                f.write("atom %d (%d) (%d, %d, %d)\n" % n)
                atnum += 1
                bl=[]
                for b in a.bonds:
                    oa = b.other(a)
                    if oa.key in atnums: bl += [atnums[oa.key]]
                if len(bl) > 0:
                    f.write("bond1 " + " ".join(map(str,bl)) + "\n")
            for g in mol.gadgets:
                f.write(g.__repr__(atnums) + "\n")
        f.write("end molecular machine part " + self.name + "\n")
        f.close()

    # move the atoms one frame as for movie or minization
    # .dpb file is in units of 16 pm
    # units here are angstroms
    def movatoms(self, file):
        if not self.alist: return
        for a in self.alist:
            #print unpack('bbb',file.read(3))
            a.xyz += A(unpack('bbb',file.read(3)))*0.01
        for m in self.molecules:
            m.changeapp()
        

    # dumb hack: find which atom the cursor is pointing at by
    # checking every atom...
    def findpick(self, p1, v1):
        distance=1000000
        atom=None
        for mol in self.molecules:
            if mol.display == diINVISIBLE: continue
            for a in mol.atoms.itervalues():
                if a.display == diINVISIBLE: continue
                dist = a.checkpick(p1, v1)
                if dist:
                    if dist<distance:
                        distance=dist
                        atom=a
        return atom

    # make an atom selected: deselects all parts
    def pickatom(self, p1, v1):
        self.unpickparts()
        if not self.selatoms: self.selatoms = {}
        a = self.findpick(p1, v1)
        if a: a.pick()

    # make a part selected: deselects all atoms
    def pickpart(self, p1, v1):
        self.unpickatoms()
        if not self.selmols: self.selmols = []
        a = self.findpick(p1, v1)
        if a: a.molecule.pick()

    # deselect any selected atoms
    def unpickatoms(self):
        if self.selatoms:
            for a in self.selatoms.itervalues():
                a.picked = 0
                a.molecule.changeapp()
            self.selatoms = {}

    # deselect any selected molecules
    def unpickparts(self):
        if self.selmols:
            for mol in self.selmols:
                mol.picked = 0
                mol.changeapp()
            self.selmols = []

    # for debugging
    def prin(self):
        for a in self.selatoms.itervalues():
            a.prin()

    # copy any selected parts (molecules)
    def copy(self):
        if self.selmols:
            offset = self.bboxhi-self.bboxlo
            nulist=[]
            for mol in self.selmols[:]:
                numol=mol.copy(offset)
                nulist += [numol]
                self.molecules += [numol]
                self.bboxhi = maximum(self.bboxhi, numol.bboxhi+numol.center)
                self.bboxlo = minimum(self.bboxlo, numol.bboxlo+numol.center)
            self.center = (self.bboxhi+self.bboxlo)/2

    # move any selected parts in space ("move" is an offset vector)
    def movesel(self, move):
        for mol in self.selmols:
            mol.move(move)

    # rotate any selected parts in space ("rot" is a quaternion)
    def rotsel(self, rot):
        for mol in self.selmols:
            mol.rot(rot)

    # delete whatever is selected
    def kill(self):
        if self.selatoms:
            for a in self.selatoms.values():
                a.kill()
            self.selatoms={}
        if self.selmols:
            for m in self.selmols:
                self.killmol(m)
            self.selmols=[]

        self.setDrawLevel()


    # actually remove a given molecule from the list
    def killmol(self, mol):
        try: self.molecules.remove(mol)
        except ValueError: pass

        self.setDrawLevel()


    def __str__(self):
        return "<Assembly of " + self.filename + ">"
    
    # makes a motor connected to the selected atoms
    # note I don't check for a limit of 25 atoms, but any more
    # will choke the file parser in the simulator
    def makemotor(self, sightline):
        if not self.selatoms: return
        m=motor(self)
        m.findcenter(self.selatoms.values(), sightline)
        self.unpickatoms()

    # makes a Linear Motor connected to the selected atoms
    # note I don't check for a limit of 25 atoms, but any more
    # will choke the file parser in the simulator
    def makeLinearMotor(self, sightline):
        if not self.selatoms: return
        m = LinearMotor(self)
        m.findCenter(self.selatoms.values(), sightline)
        self.unpickatoms()

    # makes all the selected atoms grounded
    # same note as above
    def makeground(self):
        if not self.selatoms: return
        m=ground(self, self.selatoms.values())
        self.unpickatoms()

    # select all atoms connected by a sequence of bonds to
    # an already selected one
    def marksingle(self):
        for a in self.selatoms.values():
            self.conncomp(a, 1)

    # connected components. DFS is elegant!
    # This is called with go=1 from eached already picked atom
    # its only problem is relatively limited stack in Python
    def conncomp(self, atom, go=0):
        if go or not atom.picked:
            atom.pick()
            for a in atom.neighbors(): self.conncomp(a)

    # select all atoms connected by two disjoint sequences of bonds to
    # an already selected one. This picks stiff components but doesn't
    # cross single-bond or single-atom bearings or hinges
    # does select e.g. hydrogens connected to the component and nothing else
    def markdouble(self):
        self.father= {}
        self.stack = []
        self.out = []
        self.dfi={}
        self.p={}
        self.i=0
        for a in self.selatoms.values():
            if a not in self.dfi:
                self.father[a]=None
                self.blocks(a)
        for (a1,a2) in self.out[-1]:
            a1.pick()
            a2.pick()
        for mol in self.molecules:
            for a in mol.atoms.values():
                if len(a.bonds) == 1 and a.neighbors()[0].picked:
                    a.pick()

    # compared to that, the doubly-connected components algo is hairy.
    # cf Gibbons: Algorithmic Graph Theory, Cambridge 1985
    def blocks(self, atom):
        self.dfi[atom]=self.i
        self.p[atom] = self.i
        self.i += 1
        for a2 in atom.neighbors():
            if atom.key < a2.key: pair = (atom, a2)
            else: pair = (a2, atom)
            if not pair in self.stack: self.stack += [pair]
            if a2 in self.dfi:
                if a2 != self.father[atom]:
                    self.p[atom] = min(self.p[atom], self.dfi[a2])
            else:
                self.father[a2] = atom
                self.blocks(a2)
                if self.p[a2] >= self.dfi[atom]:
                    pop = self.stack.index(pair)
                    self.out += [self.stack[pop:]]
                    self.stack = self.stack[:pop]
                self.p[atom] = min(self.p[atom], self.p[a2])

    # separate selected atoms into a new molecule
    # do not break bonds
    def separate(self):
        for mol in self.molecules:
            numol = molecule(self, mol.name + gensym("-frag"))
            for a in mol.atoms.values():
                if a.picked:
                    a.hopmol(numol)
                    a.unpick()
            if numol.atoms:
                self.addmol(numol)
                numol.shakedown()
                numol.pick()
                # need to redo the old one too
                mol.shakedown()

          
