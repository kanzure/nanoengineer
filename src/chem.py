# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

""" chem.py -- classes for elements, atoms, bonds.

Temporarily owned by bruce 041104 for shakedown inval/update code.

[class molecule, for chunks, was moved into chunk.py circa 041118.]

$Id$
"""
__author__ = "Josh"

from VQT import *
from LinearAlgebra import *
import string
import re
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from drawer import *
from shape import *

from constants import *
from qt import *
from Utility import *
from MoleculeProp import *
from debug import print_compact_stack, print_compact_traceback

INVALID_EXTERNS = 333 #bruce 041029 -- an illegal value for mol.externs;
# used to detect (or someday prevent) accidental use of mol.externs,
# and (someday) to signal other code that a shakedown is needed.

CPKvdW = 0.25

Elno = 0

Gno = 0
def gensym(string):
    """return string appended with a unique number"""
    global Gno
    Gno += 1
    return string + str(Gno)

def genKey():
    """ produces generators that count indefinitely """
    i=0
    while 1:
        i += 1
        yield i

atKey=genKey()


def povpoint(p):
    # note z reversal -- povray is left-handed
    return "<" + str(p[0]) + "," + str(p[1]) + "," + str(-p[2]) + ">"


class elem:
    """one of these for each element type --
    warning, order of creation matters, since it sets eltnum member!"""
    def __init__(self, sym, n, m, rv, col, bn):
        """called from a table in the source
        
        sym = (e.g.) "H"
        n = (e.g.) "Hydrogen"
        m = atomic mass in e-27 kg
        rv = van der Waals radius
        col = color (RGB, 0-1)
        bn = bonding info: list of triples:
             # of bonds in this form
             covalent radius
             angle between bonds in degrees
        """
        global Elno
        self.eltnum = Elno
        Elno += 1
        self.symbol = sym
        self.name = n
        self.color = col
        self.mass = m
        self.rvdw = rv
        self.rcovalent = bn and bn[0][1]/100.0
        self.bonds = bn
        self.numbonds = bn and bn[0][0]
        self.base = None
        self.quats = []
        if bn and bn[0][2]:
            s = bn[0][2][0]
            self.base = s
            for v in bn[0][2][1:]:
                self.quats += [Q(s,v)]

    def __repr__(self):
        return "<Element: " + self.symbol + "(" + self.name + ")>"

# the formations of bonds -- standard offsets
uvec = norm(V(1,1,1))
tetra4 = uvec * A([[1,1,1], [-1,1,-1], [-1,-1,1], [1,-1,-1]])
tetra3 = uvec * A([[-1,1,-1], [-1,-1,1], [1,-1,-1]])
oxy2 = A([[-1,0,0], [0.2588, -0.9659, 0]])
tetra2 = A([[-1,0,0], [0.342, -0.9396, 0]])
straight = A([[-1,0,0], [1,0,0]])
flat = A([[-0.5,0.866,0], [-0.5,-0.866,0], [1,0,0]])


#      sym   name          mass    rVdW  color
#      [[Nbonds, radius, angle] ...]
Mendeleev=[ \
 elem("X", "Singlet",      0.001,  1.1,  [0.8, 0.0, 0.0],
      [[1, 0, None]]),
 elem("H",  "Hydrogen",    1.6737, 1.2,  [0.0, 0.6, 0.6],
      [[1, 30, None]]),
 elem("He", "Helium",      6.646,  1.4,  [1.0, 0.27, 0.67],
      None),
 elem("Li", "Lithium",    11.525,  4.0,  [0.0, 0.5, 0.5],
      [[1, 152, None]]),
 elem("Be", "Beryllium",  14.964,  3.0,  [0.98, 0.67, 1.0],
      [[2, 114, None]]),
 elem("B",  "Boron",      17.949,  2.0,  [0.3, 0.3, 1.0],
      [[3, 90, flat]]),
 elem("C",  "Carbon",     19.925,  1.84, [0.3, 0.5, 0.0],
      [[4, 77, tetra4], [3, 71, flat], [2, 66, straight], [1, 59, None]]),
 elem("N",  "Nitrogen",   23.257,  1.55, [0.84, 0.37, 1.0],
      [[3, 70, tetra3], [2, 62, tetra2], [1, 54.5, None] ]),
 elem("O",  "Oxygen",     26.565,  1.74, [0.6, 0.2, 0.2],
      [[2, 66, oxy2], [1, 55, None]]),
 elem("F",  "Fluorine",   31.545,  1.65, [0.0, 0.8, 0.34],
      [[1, 64, None]]),
 elem("Ne", "Neon",       33.49,   1.82, [0.92, 0.25, 0.62],
      None),
 elem("Na", "Sodium",     38.1726, 4.0,  [0.0, 0.4, 0.4],
      [[1, 186, None]]),
 elem("Mg", "Magnesium",  40.356,  3.0,  [0.88, 0.6, 0.9],
      [[2, 160, None]]),
 elem("Al", "Aluminum",   44.7997, 2.5,  [0.5, 0.5, 0.9],
      [[3, 143, flat]]),
 elem("Si", "Silicon",    46.6245, 2.25, [0.3, 0.3, 0.3],
      [[4, 117, tetra4]]),
 elem("P",  "Phosphorus", 51.429,  2.11, [0.73, 0.32, 0.87],
      [[3, 110, tetra3]]),
 elem("S",  "Sulfur",     53.233,  2.11, [1.0, 0.65, 0.0],
      [[2, 104, tetra2]]),
 elem("Cl", "Chlorine",   58.867,  2.03, [0.25, 0.35, 0.0],
      [[1, 99, None]]),
 elem("Ar", "Argon",      66.33,   1.88, [0.85, 0.24, 0.57],
      None),
 # not used after this
 elem("K",  "Potassium",  64.9256, 5.0,  [0.0, 0.3, 0.3],
      [[1, 231, None]]),
 elem("Ca", "Calcium",    66.5495, 4.0,  [0.79, 0.55, 0.8],
      [[2, 197, tetra2]]),
 elem("Sc", "Scandium",   74.646,  3.7,  [0.417, 0.417, 0.511],
      [[3, 160, tetra3]]),
 elem("Ti", "Titanium",   79.534,  3.5,  [0.417, 0.417, 0.511],
      [[4, 147, tetra4]]),
 elem("V",  "Vanadium",   84.584,  3.3,  [0.417, 0.417, 0.511],
      [[5, 132, None]]),
 elem("Cr", "Chromium",   86.335,  3.1,  [0.417, 0.417, 0.511],
      [[6, 125, None]]),
 elem("Mn", "Manganese",  91.22,   3.0,  [0.417, 0.417, 0.511],
      [[7, 112, None]]),
 elem("Fe", "Iron",       92.729,  3.0,  [0.417, 0.417, 0.511],
      [[3, 124, None]]),
 elem("Co", "Cobalt",     97.854,  3.0,  [0.417, 0.417, 0.511],
      [[3, 125, None]]),
 elem("Ni", "Nickel",     97.483,  3.0,  [0.417, 0.417, 0.511],
      [[3, 125, None]]),
 elem("Cu", "Copper",    105.513,  3.0,  [0.417, 0.417, 0.511],
      [[2, 128, None]]),
 elem("Zn", "Zinc",      108.541,  2.9,  [0.417, 0.417, 0.511],
      [[2, 133, None]]),
 elem("Ga", "Gallium",   115.764,  2.7,  [0.6, 0.6, 0.8],
      [[3, 135, None]]),
 elem("Ge", "Germanium", 120.53,   2.5,  [0.447, 0.49, 0.416],
      [[4, 122, tetra4]]),
 elem("As", "Arsenic",   124.401,  2.2,  [0.6, 0.26, 0.7],
      [[5, 119, tetra3]]),
 elem("Se", "Selenium",  131.106,  2.1,  [0.9, 0.35, 0.0],
      [[6, 120, tetra2]]),
 elem("Br", "Bromine",   132.674,  2.0,  [0.0, 0.4, 0.3],
      [[1, 119, None]]),
 elem("Kr", "Krypton",   134.429,  1.9,  [0.78, 0.21, 0.53],
      None)]

# Antimony is element 51
appendix = [
 elem("Sb", "Antimony",   124.401,  2.2,  [0.6, 0.26, 0.7],
      [[3, 119, tetra3]]),
 elem("Te", "Tellurium",  131.106,  2.1,  [0.9, 0.35, 0.0],
      [[2, 120, tetra2]]),
 elem("I", "Iodine",   132.674,  2.0,  [0.0, 0.5, 0.0],
      [[1, 119, None]]),
 elem("Xe", "Xenon",   134.429,  1.9,  [0.78, 0.21, 0.53],
      None)]

# note mass is in e-27 kg, not amu

# the elements, indexed by symbol (H, C, O ...)
PeriodicTable={}
EltNum2Sym={}
EltName2Num={}
EltSym2Num={}
for el in Mendeleev:
    PeriodicTable[el.eltnum] = el
    EltNum2Sym[el.eltnum] = el.symbol
    EltName2Num[el.name] = el.eltnum
    EltSym2Num[el.symbol] = el.eltnum

Elno = 51
for el in appendix:
    PeriodicTable[el.eltnum] = el
    EltNum2Sym[el.eltnum] = el.symbol
    EltName2Num[el.name] = el.eltnum
    EltSym2Num[el.symbol] = el.eltnum
    

Hydrogen = PeriodicTable[1]
Carbon = PeriodicTable[6]
Nitrogen = PeriodicTable[7]
Oxygen = PeriodicTable[8]

Singlet = PeriodicTable[0]

# reversed right ends of top 4 lines for passivating
PTsenil = [[PeriodicTable[2], PeriodicTable[1]],
           [PeriodicTable[10], PeriodicTable[9], PeriodicTable[8],
            PeriodicTable[7], PeriodicTable[6]],
           [PeriodicTable[18], PeriodicTable[17], PeriodicTable[16],
            PeriodicTable[15], PeriodicTable[14]],
           [PeriodicTable[36], PeriodicTable[35], PeriodicTable[34],
            PeriodicTable[33], PeriodicTable[32]]]

class atom:
    def __init__(self, sym, where, mol):
        """create an atom of element sym (e.g. 'C')
        at location where (e.g. V(36, 24, 36))
        belonging to molecule mol, which is part of assembly assy
        """
        self.__killed = 0
        # unique key for hashing
        self.key = atKey.next()
        # element-type object
        self.element=PeriodicTable[EltSym2Num[sym]]
        # location, which will be set relative to its molecule's center
        self.xyz=where
        # list of bond objects
        self.bonds=[]
        # whether the atom is selected, see also assembly.selatoms
        self.picked = 0
        # can be set to override molecule or global value
        self.display = diDEFAULT
        # pointer to molecule containing this atom
        self.molecule=mol
        self.molecule.atoms[self.key] = self

        # josh 10/26 to fix bug 85
        self.jigs = []

        # note that the assembly is not explicitly stored

    def posn(self):
        """return the absolute position of the atom in space,
        by calculating rotation and translation offset from molecule
        """
        if self.xyz != 'no':
            return self.xyz
        else:
            return self.molecule.curpos[self.index]

    def setposn(self, pos):
        """set the atom's position. after doing this you have to get the
        atom positions back in to the molecule's basepos somehow
        assume this won't be called during molecule setup (no xyz check)
        """
        self.molecule.curpos[self.index] = pos
        pos = self.molecule.quat.unrot(pos - self.molecule.center)
        self.molecule.basepos[self.index] = pos
        for b in self.bonds: b.setup()
        self.molecule.changeapp()

    def adjSinglets(self, atom, nupos):
        """We're going to move atom, a neighbor of yours, to nupos,
        so adjust the positions of your singlets to match.
        """
        apo = self.posn()
        # find the delta quat for the average real bond and apply
        # it to the singlets
        n = self.realNeighbors()
        old = V(0,0,0)
        new = V(0,0,0)
        for at in n:
            old += at.posn()-apo
            if at == atom: new += nupos-apo
            else: new += at.posn()-apo
        if n:
            q=Q(old,new)
            for at in self.singNeighbors():
                at.setposn(q.rot(at.posn()-apo)+apo)

    def __repr__(self):
        return self.element.symbol + str(self.key)

    def __str__(self):
        return self.element.symbol + str(self.key)

    def prin(self):
        """for debugging
        """
        lis = map((lambda b: b.other(self).element.symbol), self.bonds)
        print self.element.name, lis

    def draw(self, win, dispdef, col, level):
        """draw the atom depending on whether it is picked
        and its (possibly inherited) display mode.
        An atom's display mode overrides the inherited one from
        the molecule, but a molecule's color overrides the atom's
        element-dependent one
        """
        color = col or self.element.color
        disp, rad = self.howdraw(dispdef)
        if self == win.selatom: # bruce 041104 bugfix for bug#45
            if self.element == Singlet:
                color = LEDon
            else:
                color = orange
            if disp not in [diVDW, diCPK, diTUBES]:
                disp = diTUBES # Make sure selatom always gets drawn.
                # This is correct even if the atom is invisible, since if
                # depositMode stored it into win.selatom, then it will act
                # on it when you click, so we should light it up to indicate
                # that. If depositMode wants to not light up invisible atoms,
                # or wants the choice of visible display mode to influence that,
                # all it needs to do is not store them in win.selatom (which
                # it also needs to do to avoid acting on them). [bruce 041104]
        # note use of basepos since it's being drawn under
        # rotation/translation of molecule
        pos = self.molecule.basepos[self.index]
        if disp in [diVDW, diCPK]:
            drawsphere(color, pos, rad, level)
        rad *= 1.1
        if disp == diTUBES:
            if self == win.selatom:
                if self.element == Singlet:
                    drawsphere(LEDon, pos, rad, level)
                else:
                    drawsphere(orange, pos, rad*1.7, level)
                    
            else: drawsphere(color, pos, rad, level)
            rad *= 1.8
        if self.picked:
            drawwiresphere(PickedColor, pos, rad)

    def setDisplay(self, disp):
        self.display = disp
        self.molecule.changeapp()
        

    def howdraw(self, dispdef):
        """ tell how to draw the atom depending
        its (possibly inherited) display mode
        An atom's display mode overrides the inherited one from
        the molecule, but a molecule's color overrides the atom's
        element-dependent one
        return that and radius to use in a tuple
        """
        if self.element == Singlet:
            disp,rad = self.bonds[0].other(self).howdraw(dispdef)
        else:
            if self.display == diDEFAULT: disp=dispdef
            else: disp=self.display
        rad = self.element.rvdw
        if disp != diVDW: rad=rad*CPKvdW
        if disp == diTUBES: rad = TubeRadius
        return (disp, rad)

    def writemmp(self, atnums, alist, f):
        atnums['NUM'] += 1
        num = atnums['NUM']
        alist += [self]
        atnums[self.key] = num
        disp = dispNames[self.display]
        xyz=self.posn()*1000
        n=(num, self.element.eltnum,
           int(xyz[0]), int(xyz[1]), int(xyz[2]), disp)
        f.write("atom %d (%d) (%d, %d, %d) %s\n" % n)
        bl=[]
        for b in self.bonds:
            oa = b.other(self)
            if oa.key in atnums: bl += [atnums[oa.key]]
        if len(bl) > 0:
            f.write("bond1 " + " ".join(map(str,bl)) + "\n")

    # write to a povray file:  draw a single atom
    def povwrite(self, file, dispdef, col):
        color = col or self.element.color
        color = color * V(1,1,-1)
        disp, rad = self.howdraw(dispdef)
        if disp in [diVDW, diCPK]:
            file.write("atom(" + povpoint(self.posn()) +
                       "," + str(rad) + "," +
                       povpoint(color) + ")\n")
        if disp == diTUBES:
            file.write("atom(" + povpoint(self.posn()) +
                       "," + str(TubeRadius) + "," +
                       povpoint(color) + ")\n")


    def checkpick(self, p1, v1, disp, r=None, iPic=None):
        """check if the line through point p1 in direction v1
        goes through the atom (defined as a sphere 70% its vdW radius)
        This is a royal kludge, needs to be replaced by something
        that uses the screen representation
        """
        if self.element == Singlet: return None
        if not r:
            disp, r = self.howdraw(disp)
        if self.picked and not iPic: return None
        dist, wid = orthodist(p1, v1, self.posn())
        if wid > r: return None
        if dist<0: return None
        return dist

    def getinfo(self):
        # Return information about the selected atom for the msgbar
        # [mark 2004-10-14]
        xyzstr = self.posn()
        ainfo = ("Atom #" + str (self.key ) + " [" + self.element.name +
                 "] [X = " + str(xyzstr[0]) + "] [Y = " + str(xyzstr[1]) +
                 "] [Z = " + str(xyzstr[2]) + "]")
        return ainfo

    def pick(self):
        """make the atom selected
        """
        if self.element == Singlet: return
        if not self.picked:
            self.picked = 1
            self.molecule.assy.selatoms[self.key] = self
            self.molecule.changeapp()
            # Print information about the selected atom in the msgbar
            # [mark 2004-10-14]
            self.molecule.assy.w.msgbarLabel.setText(self.getinfo())
                
    def unpick(self):
        """make the atom unselected
        """
        if self.element == Singlet: return
        if self.picked:
            self.picked = 0
            del self.molecule.assy.selatoms[self.key]
            self.molecule.changeapp()
            #self.molecule.assy.w.msgbarLabel.setText(" ")

    def copy(self, numol):
        """create a copy of the atom
        (to go in numol, a copy of its molecule)
        """
        nuat = atom(self.element.symbol, 'no', numol)
        nuat.index = self.index
        return nuat

    def unbond(self, b):
        """Remove bond b from the atom (error if b not in atom.bonds).
        Replace it with a new bond to a new singlet,
        unless self or the old neighbor atom is a singlet.
        Private method, called from atom.kill of the other atom,
        and from bond.bust. Caller is responsible for shakedown
        or kill (after clearing externs) of affected molecules.
        We invalidate externs of both molecules if they are different,
        and we always invalidate appearance of both molecules.
        [code and docstring revised by bruce 041029]
        """
        at2 = b.other(self)
        if self.molecule != at2.molecule:
            self.molecule.externs = at2.molecule.externs = INVALID_EXTERNS
        self.molecule.havelist = at2.molecule.havelist = 0 # changeapp()
        # the caller needs to do a shakedown or kill of both molecules
        try:
            self.bonds.remove(b)
        except ValueError: # list.remove(x): x not in list
            # this is always a bug in the caller, but we catch it here to
            # prevent turning it into a worse bug [bruce 041028]
            msg = "fyi: atom.unbond: bond %r should be in bonds %r\n of atom %r, " \
                  "but is not:\n " % (b, self.bonds, self)
            print_compact_traceback(msg)
        if self.element == Singlet: return
        # normally replace an atom with a singlet,
        # but don't replace a singlet with a singlet
        if b.other(self).element == Singlet: return
        x = atom('X', b.ubp(self), self.molecule)
        self.molecule.bond(self, x)

    def hopmol(self, numol):
        """move this atom to molecule numol.  Caller is responsible for
        shakedown or kill (of both involved molecules).
        We invalidate the externs of both involved molecules
        so that their erroneous use will be detected.
        """
        if self.molecule == numol: return
        self.molecule.externs = numol.externs = INVALID_EXTERNS # [bruce 041029]
        nxyz = self.posn()
        del self.molecule.atoms[self.key]
        self.unpick()
        self.xyz = nxyz
        self.molecule = numol
        numol.atoms[self.key] = self
        for a in self.neighbors():
            if a.element == Singlet:
                a.hopmol(numol)
        # both molecules change!
        self.molecule.changeapp()
        numol.changeapp()

    def neighbors(self):
        """return a list of the atoms bonded to this one
        """
        return map((lambda b: b.other(self)), self.bonds)

    def realNeighbors(self):
        """return a list of the atoms not singlets bonded to this one
        """
        return filter(lambda a: a.element != Singlet, self.neighbors())
              
    def singNeighbors(self):
        """return a list of the singlets bonded to this atom
        """
        return filter(lambda a: a.element == Singlet, self.neighbors())
              

    def mvElement(self, elt):
        """Change the element type of this atom to element elt
        (an element object)
        """
        self.element = elt
        for b in self.bonds: b.setup()            
        self.molecule.changeapp()

    def killed(self): #bruce 041029
        """For an ordinary atom, return False.
        For an atom which has been properly killed, return True.
        For an atom which has something clearly wrong with it,
        print an error message, try to fix the problem,
        effectively kill it, and return True.
        Don't call this on an atom still being initialized.
        """
        try:
            killed = not (self.key in self.molecule.atoms)
            if killed:
                assert self.__killed == 1
                assert not self.picked
                assert not self.key in self.molecule.assy.selatoms
                assert not self.bonds
                assert not self.jigs
            else:
                assert self.__killed == 0
            return killed
        except:
            print_compact_traceback("fyi: atom.killed detects some problem" \
                " in atom %r, trying to work around it:\n " % self )
            try:
                self.__killed = 0 # make sure kill tries to do something
                self.kill()
            except:
                print_compact_traceback("fyi: atom.killed: ignoring" \
                    " exception when killing atom %r:\n " % self )
            return True
        pass # end of atom.killed()
        
    def kill(self):
        """kill an atom: remove it from molecule.atoms,
        and remove bonds to it from its neighbors.
        caller is responsible for shakedown or kill of all affected molecules.
        """
        if self.__killed:
            if not self.element == Singlet:
                print_compact_stack("fyi: atom %r killed twice; ignoring:\n" % self)
            else:
                ###e killing a selected mol, using Delete key, kills a lot of
                # singlets twice; I don't know why but it's not clear it's a
                # bug, so I'll disable this debug-print in that case until I
                # understand the cause. [bruce 041029]
                pass
            return
        self.__killed = 1 # do this now, to reduce repeated exceptions (works??)
        try:
            self.unpick() #bruce 041029
        except:
            print_compact_traceback("fyi: atom.kill: ignoring error in unpick: ")
            pass
        try:
            del self.molecule.atoms[self.key]
        except KeyError:
            print "fyi: atom.kill: atom %r not in its molecule (killed twice?)" % self
            pass
        for b in self.bonds:
            n = b.other(self)
            n.unbond(b) # this can create a new singlet on n
            # note: as of 041029 unbond also invalidates externs if necessary
            if n.element == Singlet: n.kill()
        self.bonds = [] #bruce 041029 mitigate repeated kills
        # josh 10/26 to fix bug 85
        for j in self.jigs: j.rematom(self)
            # bruce comment 041018: it looks like killing singlets
            # might mess up other molecules, if singlets are in other
            # molecules and caller doesn't know about those in order
            # to do a shakedown on them as well. ###e needs bugfix
        self.jigs = [] #bruce 041029 mitigate repeated kills
        
        return # from atom.kill

    def Hydrogenate(self):
        """ if this is a singlet, change it to a hydrogen
        """
        if not self.element == Singlet: return
        o = self.bonds[0].other(self)
        self.mvElement(Hydrogen)
        self.molecule.basepos[self.index] += Hydrogen.rcovalent * norm(self.molecule.basepos[self.index] - o.molecule.basepos[o.index])
        # bruce comment 041018: does this need to also change curpos, or does
        # caller make sure that's fixed somehow, or neither (a bug)??
        ###e needs review

    def Dehydrogenate(self):
        """If this is a hydrogen atom (and if it was not already killed),
        kill it and return 1 (int, not boolean), otherwise return 0.
        [bruce comment 041018: I think caller MUST do a shakedown on all
         affected molecules (those of self and its neighbor), or remove them
         if they are left with no atoms.
         But I think it would be wrong to do any of that here.]
        """
        # [fyi: some new features were added by bruce, 041018 and 041029]
        if self.element == Hydrogen and not self.killed():
            #bruce 041029 added self.killed() check to fix bug 152
            self.kill()
            return 1
        else:
            return 0
        pass

    def snuggle(self):
        """self is a singlet and the simulator has moved it out to the
        radius of an H. move it back. the molecule is still in frozen
        mode.
        """
        o = self.bonds[0].other(self)
        op = o.posn()
        np = norm(self.posn()-op)*o.element.rcovalent + op
        self.molecule.curpos[self.index] = np


    def passivate(self):

        """change the element type of the atom to match the number of
        bonds with other real atoms, and delete singlets"""
        el = self.element
        line = len(PTsenil)
        for i in range(line):
            if el in PTsenil[i]:
                line = i
                break
        if line == len(PTsenil): return #not in table
        nrn = len(self.realNeighbors())
        for a in self.singNeighbors():
            a.kill()
        try: self.mvElement(PTsenil[line][nrn])
        except IndexError: pass
        # note that if an atom has too many bonds we'll delete the
        # singlets anyway -- which is fine
                            
        
class bondtype:
    """not implemented
    """
    pass
    # int at1, at2;    /* types of the elements */
    # num r0,ks;           /* bond length and stiffness */
    # num ediss;           /* dissociation (breaking) energy */
    # int order;            /* 1 single, 2 double, 3 triple */
    # num length;          // bond length from nucleus to nucleus
    # num angrad1, aks1;        // angular radius and stiffness for at1
    # num angrad2, aks2;        // angular radius and stiffness for at2

class bond:
    """essentially a record pointing to two atoms
    """
    
    def __init__(self, at1, at2): # also called from self.rebond()
        """create a bond from atom at1 to atom at2.
        the key created will be the same whichever order the atoms are
        given, and is used to compare bonds.
        [further comments by bruce 041029:]
        Private method (that is, creating of bond objects is private, for
        affected molecules and/or atoms). Note: the bond is not actually added
        to the atoms' molecules! Caller must do that, and must do any necessary
        invalidation or shakedown of those molecules.
        """
        self.atom1 = at1
        self.atom2 = at2
        ## self.picked = 0 # bruce 041029 removed this since it seems unused
        self.key = 65536*min(at1.key,at2.key)+max(at1.key,at2.key)
        if self.setup_ok():
            self.setup()
        # [bruce 041029] We call self.setup() to fix a bug in Bond menu item,
        # and on the general principle of keeping things safe. Probably ok,
        # but needs testing, in case bonds are made on atoms which have not
        # yet been properly initialized. The exception when not self.setup_ok()
        # is needed for making certain molecules (no basepos before shakedown)
        # but should not prevent this from helping with bonds made later,
        # like in molecule.bond().

    def setup_ok(self):
        "check whether it's ok (or too early) to call self.setup" #bruce 041029
        try:
            self.a1pos = self.atom1.molecule.basepos[self.atom1.index]
            self.a2pos = self.atom2.molecule.basepos[self.atom2.index]
            return 1
        except:
            return 0
        pass
    
    def setup(self):
        """Call this whenever the position or element of either bonded atom is
        changed. Also called from bond.__init__ when self.setup_ok().
        """
        self.a1pos = self.atom1.molecule.basepos[self.atom1.index]
        self.a2pos = self.atom2.molecule.basepos[self.atom2.index]
        if self.atom1.molecule != self.atom2.molecule:
            self.a1pos = self.atom1.posn()
            self.a2pos = self.atom2.posn()

        vec = self.a2pos - self.a1pos
        len = 0.98 * vlen(vec)
        vec = norm(vec)
        self.c1 = self.a1pos + vec*self.atom1.element.rcovalent
        self.c2 = self.a2pos - vec*self.atom2.element.rcovalent
        if len > self.atom1.element.rcovalent + self.atom2.element.rcovalent:
            self.center = None
        else:
            self.center = (self.c1 + self.c2) /2.0

    def other(self, at):
        """Given one atom the bond is connected to, return the other one
        """
        if self.atom1 == at: return self.atom2
        assert self.atom2 == at #bruce 041029
        return self.atom1
    
    def ubp(self, atom):
        """ unbond point """
        if self.atom1.molecule != self.atom2.molecule:
            off = V(0,0,0)
        else: off = atom.molecule.center
##        try:
##            self.c1
##        except:
##            #bruce 041029 added this to prevent a bug seen in Bond/Unbond menu items
##            self.setup()
        if atom==self.atom1: return self.c1 + off
        else: return self.c2 + off

    # "break" is a python keyword
    def bust(self, mol = None):
        self.atom1.unbond(self)
        self.atom2.unbond(self)
        # a non-null mol is being thrown away, no need to update it
        if mol != self.atom1.molecule:
            self.atom1.molecule.shakedown()
        if self.atom1.molecule != self.atom2.molecule:
            if mol != self.atom2.molecule:
                self.atom2.molecule.shakedown()

    def rebond(self, old, new):
        # intended for use on singlets, other uses may have bugs
        if len(old.bonds) == 1: del old.molecule.atoms[old.key]
        if self.atom1 == old: self.atom1 = new
        if self.atom2 == old: self.atom2 = new
        new.bonds += [self]
        # bruce 041028 wonders why we don't old.bonds.remove(self)...
        # I suggest adding a comment here explaining that.
        self.__init__(self.atom1, self.atom2)
        

    def __eq__(self, ob):
        return ob.key == self.key

    def __ne__(self, ob):
        # bruce 041028 -- python doc advises defining __ne__
        # whenever you define __eq__
        return not self.__eq__(ob)

    def draw(self, win, dispdef, col, level):
        """bonds are drawn in CPK or line display mode.
        display mode is inherited from the atoms or molecule.
        lines change color from atom to atom.
        CPK bonds are drawn in the molecule's color or bondColor
        (which is light gray)
        """
        
        color1 = col or self.atom1.element.color
        color2 = col or self.atom2.element.color

        disp=max(self.atom1.display, self.atom2.display)
        if disp == diDEFAULT: disp= dispdef
        if disp == diLINES:
            if self.center:
                drawline(color1, self.a1pos, self.center)
                drawline(color2, self.a2pos, self.center)
            else:
                drawline(color1, self.a1pos, self.c1)
                drawline(color2, self.a2pos, self.c2)
                drawline(red, self.c1, self.c2)
        if disp == diCPK:
            drawcylinder(col or bondColor, self.a1pos, self.a2pos, 0.1)
        if disp == diTUBES:
            v1 = self.atom1.display != diINVISIBLE
            v2 = self.atom2.display != diINVISIBLE
            if self.center:
                if v1:
                    drawcylinder(color1, self.a1pos, self.center, TubeRadius)
                if v2:
                    drawcylinder(color2, self.a2pos, self.center, TubeRadius)
                if not (v1 and v2):
                    drawsphere(black, self.center, TubeRadius, level)
            else:
                drawcylinder(red, self.c1, self.c2, TubeRadius)
                if v1:
                    drawcylinder(color1, self.a1pos, self.c1, TubeRadius)
                else:
                    drawsphere(black, self.c1, TubeRadius, level)
                if v2:
                    drawcylinder(color2, self.a2pos, self.c2, TubeRadius)
                else:
                    drawsphere(black, self.c2, TubeRadius, level)

    # write to a povray file:  draw a single bond
    def povwrite(self, file, dispdef, col):
        disp=max(self.atom1.display, self.atom2.display)
        if disp == diDEFAULT: disp= dispdef
        color1 = self.atom1.element.color * V(1,1,-1)
        color2 = self.atom2.element.color * V(1,1,-1)
        a1pos = self.atom1.posn()
        a2pos = self.atom2.posn()
        vec = a2pos - a1pos
        len = 0.98 * vlen(vec)
        c1 = a1pos + vec*self.atom1.element.rcovalent
        c2 = a2pos - vec*self.atom2.element.rcovalent
        if len > self.atom1.element.rcovalent + self.atom2.element.rcovalent:
            center = None
        else:
            center = (c1 + c2) /2.0
        
        if disp<0: disp= dispdef
        if disp == diLINES:
            file.write("line(" + povpoint(a1pos) +
                       "," + povpoint(a2pos) + ")\n")
        if disp == diCPK:
            file.write("bond(" + povpoint(a1pos) +
                       "," + povpoint(a2pos) + ")\n")
        if disp == diTUBES:
            if center:
                file.write("tube2(" + povpoint(a1pos) +
                           "," + povpoint(color1) +
                           "," + povpoint(center) + "," +
                           povpoint(a2pos) + "," +
                           povpoint(color2) + ")\n")
            else:
                file.write("tube1(" + povpoint(a1pos) +
                           "," + povpoint(color1) +
                           "," + povpoint(c1) + "," +
                           povpoint(c2) + "," + 
                           povpoint(a2pos) + "," +
                           povpoint(color2) + ")\n")

    def __str__(self):
        return str(self.atom1) + " <--> " + str(self.atom2)

    def __repr__(self):
        return str(self.atom1) + "::" + str(self.atom2)

    pass # end of class bond

# ==

# class molecule used to be defined here, but now it's in chunk.py. [bruce 041118]

# for the sake of other files which still look for class molecule in this file,
# we'll import it here (this might not work if done at the top of this file):

from chunk import *

# end of chem.py
