# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
# 10/3 currently being owned by Josh

"""Classes for elements, atoms, bonds, molecules
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
 elem("Cl", "Chlorine",   58.867,  2.03, [0.34, 0.68, 0.0],
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
 elem("Br", "Bromine",   132.674,  2.0,  [0.0, 0.5, 0.0],
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

class atom:
    def __init__(self, sym, where, mol):
        """create an atom of element sym (e.g. 'C')
        at location where (e.g. V(36, 24, 36))
        belonging to molecule mol, which is part of assembly assy
        """
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
        and its (possibly inherited) display mode
        An atom's display mode overrides the inherited one from
        the molecule, but a molecule's color overrides the atom's
        element-dependent one
        """

        color = col or self.element.color
        disp, rad = self.howdraw(dispdef)
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
        """remove bond b from the atom.
        called from atom.kill of the other atom.
        """
        # the caller needs to do a shakedown
        self.bonds.remove(b)
        if self.element == Singlet: return
        # normally replace an atom with a singlet,
        # but don't replace a singlet with a singlet
        if b.other(self).element == Singlet: return
        x = atom('X', b.ubp(self), self.molecule)
        self.molecule.bond(self, x)

    def hopmol(self, numol):
        """move this atom to molecule numol
        """
        if self.molecule == numol: return
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

    def kill(self):
        """kill an atom: remove it from molecule.atoms,
        and remove bonds to it from its neighbors
        caller is responsible for shakedown
        """
        try: del self.molecule.atoms[self.key]
        except KeyError: pass
        for b in self.bonds:
            n = b.other(self)
            n.unbond(b)
            if n.element == Singlet: n.kill()

    def Hydrogenate(self):
        """ if this is a singlet, change it to a hydrogen
        """
        if not self.element == Singlet: return
        o = self.bonds[0].other(self)
        self.mvElement(Hydrogen)
        self.molecule.basepos[self.index] += Hydrogen.rcovalent * norm(self.molecule.basepos[self.index] - o.molecule.basepos[o.index])

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
    
    def __init__(self, at1, at2):
        """create a bond from atom at1 to atom at2.
        the key created will be the same whichever order the atoms are
        given, and is used to compare bonds.
        """
        self.atom1 = at1
        self.atom2 = at2
        self.picked = 0
        self.key = 65536*min(at1.key,at2.key)+max(at1.key,at2.key)

    def setup(self):
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
        return self.atom1
    
    def ubp(self, atom):
        """ unbond point """
        if self.atom1.molecule != self.atom2.molecule:
            off = V(0,0,0)
        else: off = atom.molecule.center
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
        self.__init__(self.atom1, self.atom2)
        

    def __eq__(self, ob):
        return ob.key == self.key

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


# I use "molecule" and "part" interchangeably throughout the program.
# this is the class intended to represent rigid collections of
# atoms bonded together, but it's quite possible to make a molecule
# object with unbonded atoms, and with bonds to atoms in other
# molecules

# Huaicai: It's completely possible to create a molecule without any atoms,
# so don't assume it always has atoms.   09/30/04
class molecule(Node):
    def __init__(self, assembly, nam=None, dad=None):
        Node.__init__(self, assembly, dad, nam or gensym("Mol"))
        # atoms in a dictionary, indexed by atom.key
        self.atoms = {}
        # motors, grounds
        self.gadgets = []
        # center and bounding box of the molecule
        self.center=V(0,0,0)
        # this overrides global display (GLPane.display)
        # but is overriden by atom value if not default
        self.display = diDEFAULT
        # this set and the molecule in assembly.selmols
        # must remain consistent
        self.picked=0
        # this specifies the molecule's attitude in space
        self.quat = Q(1, 0, 0, 0)
        # this overrides atom colors if set
        self.color = None
        # for caching the display as a GL call list
        self.displist = glGenLists(1)
        self.havelist = 0
        # default place to bond this molecule -- should be a singlet
        self.hotspot = None
        
          
    def bond(self, at1, at2):
        """Cause atom at1 to be bonded to at2
        """
        b=bond(at1,at2)
        if not b in at2.bonds:
            at1.bonds += [b]
            at2.bonds += [b]
        # may have changed appearance of the molecule
        self.havelist = 0

    def shakedown(self):
        """Find center and bounding box for atoms, and set each one's
        xyz to be relative to the center and find principal axes
        """
        if not self.atoms:
            self.bbox = BBox()
            self.center = V(0,0,0)
            self.quat = Q(1,0,0,0)
            self.axis = V(1,0,0)
            self.basepos = self.curpos = []
            return
        atpos = []
        atlist = []
        singlets = []
        singlpos = []
        for a,i in zip(self.atoms.values(),range(len(self.atoms))):
            pos = a.posn()
            atpos += [pos]
            atlist += [a]
            a.index = i
            a.xyz = 'no'
            if a.element == Singlet:
                 singlets += [a]
                 singlpos += [pos]
        atpos = A(atpos)
        

        self.bbox = BBox(atpos)
        self.center = add.reduce(atpos)/len(self.atoms)
        self.quat = Q(1,0,0,0)  # since all atoms are in place 

        # make the positions relative to the center
        self.basepos = atpos-self.center
        self.curpos = atpos
        self.atlist = array(atlist, PyObject)
        self.singlets = array(singlets, PyObject)
        if self.singlets:
            self.singlpos = array(singlpos)
            self.singlbase = self.singlpos - self.center

        # find extrema in many directions
        xtab = dot(self.basepos, polyXmat)
        mins = minimum.reduce(xtab) - 1.8
        maxs = maximum.reduce(xtab) + 1.8

        self.polyhedron = makePolyList(cat(maxs,mins))

        # and compute inertia tensor
        tensor = zeros((3,3),Float)
        for p in self.basepos:
            rsq = dot(p, p)
            m= - multiply.outer(p, p)
            m[0,0] += rsq
            m[1,1] += rsq
            m[2,2] += rsq
            tensor += m
        self.eval, self.evec = eigenvectors(tensor)
    
        # Pick a principal axis: if square or circular, the axle;
        # otherwise the long axis (this is a heuristic)
        if len(atpos)<=1:
            self.axis = V(1,0,0)
        elif len(atpos) == 2:
            self.axis = norm(subtract.reduce(atpos))
        else:
            ug = argsort(self.eval)
            if self.eval[ug[0]]/self.eval[ug[1]] >0.95:
                self.axis = self.evec[ug[2]]
            else: self.axis = self.evec[ug[0]]
            
        # may have changed appearance of the molecule

        drawn = {}

        self.externs = []

        for atm in self.atoms.itervalues():
            for bon in atm.bonds:
                if bon.key not in drawn:
                    if bon.other(atm).molecule != self:
                        self.externs += [bon]
                    else:
                        drawn[bon.key] = bon
                    bon.setup()

        self.havelist = 0

    def freeze(self):
        """ set the molecule up for minimization or simulation"""
        self.center = V(0,0,0)
        self.quat = Q(1,0,0,0)  
        self.basepos = self.curpos # reference == same object
        if self.singlets:
            self.singlbase = self.singlpos # ditto

    def unfreeze(self):
        """ to be done at the end of minimization or simulation"""
        self.shakedown()


    def draw(self, o, dispdef):
        """draw all the atoms, using the atom's, molecule's,
        or GLPane's display mode in that order of preference
        Use the hash table drawn to draw each bond only once,
        as each one will be referenced from two atoms
        If the molecule itself is selected, draw its
        bounding box as a wireframe
        o is a GLPane
        """
        
        self.glpane = o # this is needed for the edit method - Mark [2004-10-13]
        
        #Tried to fix some bugs by Huaicai 09/30/04
        if len(self.atoms) == 0:
            return
            # do nothing for a molecule without any atoms

        # put it in its place
        glPushMatrix()

        glTranslatef(self.center[0], self.center[1], self.center[2])
        
        q = self.quat
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)

        if self.picked:
            drawlinelist(PickedColor,self.polyhedron)

        if self.display != diDEFAULT: disp = self.display
        else: disp = o.display

        # cache molecule display as GL list
        if self.havelist:
            glCallList(self.displist)

        else:
            glNewList(self.displist, GL_COMPILE_AND_EXECUTE)

            drawn = {}

            self.externs = []

            for atm in self.atoms.itervalues():
                # bruce 041014 hack for extrude -- use colorfunc if present
                try:
                    color = self.colorfunc(atm)
                except: # no such attr, or it's None, or it has a bug
                    color = self.color
                # end bruce hack, except for use of color rather than self.color in atm.draw
                atm.draw(o, disp, color, self.assy.drawLevel)
                for bon in atm.bonds:
                    if bon.key not in drawn:
                        if bon.other(atm).molecule != self:
                            self.externs += [bon]
                        else:
                            drawn[bon.key] = bon
                            bon.draw(o, disp, self.color, self.assy.drawLevel)
            glEndList()
            self.havelist = 1
        glPopMatrix()

        for bon in self.externs:
            bon.draw(o, disp, self.color, self.assy.drawLevel)

    def writemmp(self, atnums, alist, f):
        disp = dispNames[self.display]
        f.write("mol (" + self.name + ") " + disp + "\n")
        for a in self.atoms.itervalues():
            a.writemmp(atnums, alist, f)

    # write to a povray file:  draw the atoms and bonds inside a molecule
    def povwrite(self, file, disp):
#    def povwrite(self, file, win):

        if self.display != diDEFAULT: disp = self.display
#        else: disp = win.display
#        disp = self.display
        
        drawn = {}
        for atm in self.atoms.itervalues():
            atm.povwrite(file, disp, self.color)
            for bon in atm.bonds:
                if bon.key not in drawn:
                    drawn[bon.key] = bon
                    bon.povwrite(file, disp, self.color)

    def move(self, offs):
        self.center += offs
        self.curpos = self.center + self.quat.rot(self.basepos)
        if self.singlets:
            self.singlpos = self.center + self.quat.rot(self.singlbase)
        for bon in self.externs: bon.setup()

    def rot(self, q):
        self.quat += q
        self.curpos = self.center + self.quat.rot(self.basepos)
        if self.singlets:
            self.singlpos = self.center + self.quat.rot(self.singlbase)
        for bon in self.externs: bon.setup()

    def pivot(self, point, q):
        """pivot the molecule around point by quaternion q
        """
        r = point - self.center
        self.center += r - q.rot(r)
        self.quat += q
        self.curpos = self.center + self.quat.rot(self.basepos)
        if self.singlets:
            self.singlpos = self.center + self.quat.rot(self.singlbase)
        for bon in self.externs: bon.setup()


    def stretch(self, factor):
        self.basepos *= 1.1
        self.curpos = self.center + self.quat.rot(self.basepos)
        if self.singlets:
            self.singlpos = self.center + self.quat.rot(self.singlbase)
        for bon in self.externs: bon.setup()
        self.changeapp()


    def getaxis(self):
        return self.quat.rot(self.axis)

    def setcolor(self, color):
        """change the molecule's color
        """
        self.color = color
        self.havelist = 0

    def setDisplay(self, disp):
        self.display = disp
        self.havelist = 0
        
    def changeapp(self):
        """call when you've changed appearance of the molecule
        """ 
        self.havelist = 0

    def seticon(self, treewidget):
        self.icon = treewidget.moleculeIcon
        
    def getinfo(self):
        # Return information about the selected moledule for the msgbar [mark 2004-10-14]
        minfo =  "Molecule Name: [" + str (self.name) + "]     Total Atoms: " + str(len(self.atoms)) + " "
        ele2Num = {}
        # Calculating the number of element types in this molecule.
        for a in self.atoms.itervalues():
            if not ele2Num.has_key(a.element.symbol): ele2Num[a.element.symbol] = 1 # New element found
            else: ele2Num[a.element.symbol] += 1 # Increment element
        # String construction for each element to be displayed.
        for item in ele2Num.iteritems():
            eleStr = "[" + item[0] + ": " + str(item[1]) + "] "
            minfo += eleStr            
        return minfo


    def pick(self):
        """select the molecule.
        """
        if not self.picked:
            Node.pick(self)
            self.assy.selmols.append(self)
            # may have changed appearance of the molecule
            self.havelist = 0

            # print molecule info on the msgbar. - Mark [2004-10-14]
            self.assy.w.msgbarLabel.setText(self.getinfo())

    def unpick(self):
        """unselect the molecule.
        """
        if self.picked:
            Node.unpick(self)
            self.assy.selmols.remove(self)
            # may have changed appearance of the molecule
            self.havelist = 0
            # self.assy.w.msgbarLabel.setText(" ")

    def kill(self):
        self.unpick()
        Node.kill(self)
        try:
            self.assy.molecules.remove(self)
            self.assy.modified = 1
        except ValueError: pass
        for b in self.externs:
            b.bust(self)

    # point is some point on the line of sight
    # matrix is a rotation matrix with z along the line of sight,
    # positive z out of the plane
    # return positive points only, sorted by distance
    def findatoms(self, point, matrix, radius, cutoff):
        v = dot(self.curpos-point,matrix)
        r = sqrt(v[:,0]**2 + v[:,1]**2)
        i = argmax(v[:,2] - 100000.0*(r>radius))
        if r[i]>radius: return None
        if v[i,2]<cutoff: return None
        return self.atlist[i]


    # point is some point on the line of sight
    # matrix is a rotation matrix with z along the line of sight,
    # positive z out of the plane
    # return positive points only, sorted by distance
    def findSinglets(self, point, matrix, radius, cutoff):
        if not self.singlets: return None
        v = dot(self.singlpos-point,matrix)
        r = sqrt(v[:,0]**2 + v[:,1]**2)
        i = argmax(v[:,2] - 100000.0*(r>radius))
        if r[i]>radius: return None
        if v[i,2]<cutoff: return None
        return self.singlets[i]

    # Same, but return all that match
    def findAllSinglets(self, point, matrix, radius, cutoff):
        if not self.singlets: return []
        v = dot(self.singlpos-point,matrix)
        r = sqrt(v[:,0]**2 + v[:,1]**2)
        lis = []
        for i in range(len(self.singlets)):
            if r[i]<=radius and v[i,2]>=cutoff: lis += [self.singlets[i]]
        return lis

    # return the singlets in the given sphere
    # sorted by increasing distance from the center
    def nearSinglets(self, point, radius):
        if not self.singlets: return []
        v = self.singlpos-point
        r = sqrt(v[:,0]**2 + v[:,1]**2 + v[:,2]**2)
        p= r<=radius
        i=argsort(compress(p,r))
        return take(compress(p,self.singlets),i)

    def copy(self, dad=None, offset=V(0,0,0)):
        """Copy the molecule to a new molecule.
        offset tells where it will go relative to the original.
        """
        pairlis = []
        ndix = {}
        numol = molecule(self.assy, gensym(self.name))
        for a in self.atoms.itervalues():
            na = a.copy(numol)
            pairlis += [(a, na)]
            ndix[a.key] = na
        for (a, na) in pairlis:
            for b in a.bonds:
                if b.other(a).key in ndix:
                    numol.bond(na,ndix[b.other(a).key])
                    
        numol.hotspot = ndix[self.hotspot.key]
        numol.curpos = self.curpos+offset
        numol.shakedown()
        numol.setDisplay(self.display)
        numol.dad = dad
        return numol

    def passivate(self):
        """kludgey hack: change carbons with 3 neighbors to nitrogen,
        with 2 neighbors to oxygen, with 1 to hydrogen, and
        delete unbonded ones.
        """
        for a in self.atoms.values():
            if a.element == Carbon:
                valence = len(a.bonds)
                if valence == 0: a.kill()
                elif valence == 1: a.element = Hydrogen
                elif valence == 2: a.element = Oxygen
                elif valence == 3: a.element = Nitrogen
        # will have changed appearance of the molecule
        self.havelist = 0

    def Hydrogenate(self):
        """Add hydrogen to all unfilled bond sites on carbon
        atoms assuming they are in a diamond lattice.
        For hilariously incorrect results, use on graphite.
        This ought to be an atom method.
        """
        # will change appearance of the molecule
        self.havelist = 0
        for a in self.atoms.values():
            a.Hydrogenate()

    def edit(self):
        cntl = MoleculeProp(self)    
        cntl.exec_loop()
        self.assy.mt.update()


    def __str__(self):
        return "<Molecule of " + self.name + ">"

    def dump(self):
        print self, len(self.atoms), 'atoms,', len(self.singlets), 'singlets'
        for a in self.atlist:
            print a
            for b in a.bonds:
                print b

    def merge(self, mol):
        """merge the given molecule into this one.
        assume they are in the same assy.
        """
        pairlis = []
        ndix = {}
        for a in mol.atoms.values():
            a.hopmol(self)
        self.shakedown()
        mol.externs = []
        mol.kill()

def oneUnbonded(elem, assy, pos):
    """[bruce comment 040928:] create one unbonded atom, of element elem,
    at position pos, in its own new molecule."""
    mol = molecule(assy, gensym('Molecule.'))
    a = atom(elem.symbol, pos, mol)
    r = elem.rcovalent
    if elem.bonds and elem.bonds[0][2]:
        for dp in elem.bonds[0][2]:
            x = atom('X', pos+r*dp, mol)
            mol.bond(a,x)
    assy.addmol(mol)

    return a

def makeBonded(s1, s2):
    """s1 and s2 are singlets; make a bond between their real atoms in
    their stead. If they are in different molecules, move s1's to
    match the bond. Set its center to the bond point and its axis to
    the line of the bond.
    """
    b1 = s1.bonds[0]
    b2 = s2.bonds[0]
    a1 = b1.other(s1)
    a2 = b2.other(s2)
    m1 = s1.molecule
    m2 = s2.molecule
    if m1 != m2: # move the molecule
        m1.rot(Q(a1.posn()-s1.posn(), s2.posn()-a2.posn()))
        m1.move(s2.posn()-s1.posn())
    s1.kill()
    s2.kill()
    m1.bond(a1,a2)
    m1.shakedown()
    m2.shakedown()

    # caller must take care of redisplay
    
# this code knows where to place missing bonds in carbon
# sure to be used later

        
##         # length of Carbon-Hydrogen bond
##         lCHb = (Carbon.bonds[0][1] + Hydrogen.bonds[0][1]) / 100.0
##         for a in self.atoms.values():
##             if a.element == Carbon:
##                 valence = len(a.bonds)
##                 # lone atom, pick 4 directions arbitrarily
##                 if valence == 0:
##                     b=atom("H", a.xyz+lCHb*norm(V(-1,-1,-1)), self)
##                     c=atom("H", a.xyz+lCHb*norm(V(1,-1,1)), self)
##                     d=atom("H", a.xyz+lCHb*norm(V(1,1,-1)), self)
##                     e=atom("H", a.xyz+lCHb*norm(V(-1,1,1)), self)
##                     self.bond(a,b)
##                     self.bond(a,c)
##                     self.bond(a,d)
##                     self.bond(a,e)

##                 # pick an arbitrary tripod, and rotate it to
##                 # center away from the one bond
##                 elif valence == 1:
##                     bpos = lCHb*norm(V(-1,-1,-1))
##                     cpos = lCHb*norm(V(1,-1,1))
##                     dpos = lCHb*norm(V(1,1,-1))
##                     epos = V(-1,1,1)
##                     q1 = Q(epos, a.bonds[0].other(a).xyz - a.xyz)
##                     b=atom("H", a.xyz+q1.rot(bpos), self)
##                     c=atom("H", a.xyz+q1.rot(cpos), self)
##                     d=atom("H", a.xyz+q1.rot(dpos), self)
##                     self.bond(a,b)
##                     self.bond(a,c)
##                     self.bond(a,d)

##                 # for two bonds, the new ones can be constructed
##                 # as linear combinations of their sum and cross product
##                 elif valence == 2:
##                     b=a.bonds[0].other(a).xyz - a.xyz
##                     c=a.bonds[1].other(a).xyz - a.xyz
##                     v1 = - norm(b+c)
##                     v2 = norm(cross(b,c))
##                     bpos = lCHb*(v1 + sqrt(2)*v2)/sqrt(3)
##                     cpos = lCHb*(v1 - sqrt(2)*v2)/sqrt(3)
##                     b=atom("H", a.xyz+bpos, self)
##                     c=atom("H", a.xyz+cpos, self)
##                     self.bond(a,b)
##                     self.bond(a,c)

##                 # given 3, the last one is opposite their average
##                 elif valence == 3:
##                     b=a.bonds[0].other(a).xyz - a.xyz
##                     c=a.bonds[1].other(a).xyz - a.xyz
##                     d=a.bonds[2].other(a).xyz - a.xyz
##                     v = - norm(b+c+d)
##                     b=atom("H", a.xyz+lCHb*v, self)
##                     self.bond(a,b)
