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

from debug import print_compact_stack, print_compact_traceback, compact_stack

import platform # for atom_debug, but uses of atom_debug should all grab it
  # from platform.atom_debug since it can be changed at runtime

# from chunk import * -- done at end of file,
# until other code that now imports its symbols from this module
# has been updated to do that directly.
# [-- bruce 041110, upon moving class molecule from this file into chunk.py]


# ==

## removed, 041112: INVALID_EXTERNS = 333 #bruce 041029 -- an illegal value for mol.externs;
# used to detect (or someday prevent) accidental use of mol.externs,
# and (someday) to signal other code that a shakedown is needed.

CPKvdW = 0.25

Elno = 0

Gno = 0
def gensym(string):
    # warning, there is also a function like this in gadgets.py
    # but with its own global counter!
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


# == Elements, and periodic table

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

onebond = A([[1,0,0]]) # for use with valence-1 elements
# [bruce 041119-23; Josh has reviewed "onebond", and approves it in principle]
#e [note that this one-bond-direction is in model space; it might be better to
#   change the code that deposits "onebond" atoms to always use screen-right]


#      sym   name          mass    rVdW  color
#      [[Nbonds, radius, angle] ...]
Mendeleev=[ \
 elem("X", "Singlet",      0.001,  1.1,  [0.8, 0.0, 0.0],
      [[1, 0, None]]),
 elem("H",  "Hydrogen",    1.6737, 1.2,  [0.0, 0.6, 0.6],
      [[1, 30, onebond]]),
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
      [[1, 64, onebond]]),
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
      [[1, 99, onebond]]),
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
      [[1, 119, onebond]]),
 elem("Kr", "Krypton",   134.429,  1.9,  [0.78, 0.21, 0.53],
      None)]

# Antimony is element 51
appendix = [
 elem("Sb", "Antimony",   124.401,  2.2,  [0.6, 0.26, 0.7],
      [[3, 119, tetra3]]),
 elem("Te", "Tellurium",  131.106,  2.1,  [0.9, 0.35, 0.0],
      [[2, 120, tetra2]]),
 elem("I", "Iodine",   132.674,  2.0,  [0.0, 0.5, 0.0],
      [[1, 119, onebond]]),
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

# == Atom

##e bruce 041109 thinks class atom should be renamed Atom so it's easier to find
# all its uses in the code. To ease the change, I'll wait for my rewrites to
# go in before doing the renaming at all, then define atom() to print a warning
# and call Atom().

class atom:
    """An atom instance represents one real atom, or one "singlet"
    (a place near a real atom where another atom could bond to it).
       At any time, each atom has an element, a position in space,
    a list of bond objects it's part of, a list of jigs it's part of,
    and a reference to exactly one molecule object ("chunk") which
    owns it; all these attributes can change over time.
       It also has a never-changing key used as its key in self.molecule.atoms,
    a selection state, a display mode (which overrides that of its molecule),
    and (usually) some attributes added externally by its molecule, notably
    self.index. The attributes .index and .xyz are essentially for the
    private use of the owning molecule; see the methods posn and baseposn
    for details. Other code might add other attributes to an atom; some of
    those might be copied in the private method atom.copy_for_mol_copy().
    """
    # bruce 041109-16 wrote docstring
    def __init__(self, sym, where, mol):
        """create an atom of element sym (e.g. 'C')
        at location where (e.g. V(36, 24, 36))
        belonging to molecule mol, which is part of assembly assy
        """
        self.__killed = 0
        # unique key for hashing
        self.key = atKey.next()
        # element-type object
        self.element = PeriodicTable[EltSym2Num[sym]]
        # 'where' is atom's absolute location in model space,
        # until replaced with 'no' by shakedown, indicating
        # the location should be found using the formula in self.posn();
        # or it can be passed as 'no' by caller of __init__
        self.xyz = where
        # list of bond objects
        self.bonds = []
        # list of jigs (###e should be treated analogously to self.bonds)
        self.jigs = [] # josh 10/26 to fix bug 85
        # whether the atom is selected; see also assembly.selatoms
        self.picked = 0
        # can be set to override molecule or global value
        self.display = diDEFAULT

        # pointer to molecule containing this atom
        # (note that the assembly is not explicitly stored
        #  and that the index is only set later by methods in the molecule)
        self.molecule = None # checked/replaced by mol.addatom
        if mol:
            mol.addatom(self)
            # bruce 041109 wrote addatom to do following for us and for hopmol:
            ## self.molecule = mol
            ## self.molecule.atoms[self.key] = self
            ## # now do the necessary invals in self.molecule for adding an atom
            ## ...
        else:
            # this now happens in mol.copy as of 041113
            # print "fyi: creating atom with mol == None"
            pass
        # (optional debugging code to show which code creates bad atoms:)
        ## if platform.atom_debug:
        ##     self._source = compact_stack("\n")        
        return # from atom.__init__

    def posn(self):
        """Return the absolute position of the atom in space.
        Public method, should be ok to call for any atom at any time.
        Private implementation note (fyi): this info is sometimes stored
        in the atom, and sometimes in its molecule.
        
        """
        #bruce 041104,041112 revised docstring
        if self.xyz != 'no':
            return self.xyz #bruce 041124: this should return a copy, use '+' ###@@@
        else:
            return self.molecule.curpos[self.index] ###@@@ ditto

    def baseposn(self): #bruce 041107 night
        """Like posn, but return the mol-relative position.
        Semi-private method -- should always be legal, but assumes you have
        some business knowing about the mol-relative coordinate system, which is
        somewhat private since it's semi-arbitrary and is changed by some
        recomputation methods -- including this one, if it recomputes basepos!
        Private implementation note: Recompute mol.basepos if it's not already
        there; this might change mol.basecenter and/or mol.quat.
        """
        # No .xyz check is needed, since recomputing basepos (when it's missing
        # and has to be recomputed by mol.__getattr__) will set self.xyz to 'no'!
        # And basepos will be invalid (and thus missing) whenever some new atom
        # was added, ie whenever any atom still stores its own .xyz.
        basepos = self.molecule.basepos
        # that might have set or changed self.index; it's now definitely valid.
        return basepos[self.index]
    
    def setposn(self, pos):
        """set the atom's absolute position,
        adjusting or invalidating whatever is necessary as a result.
        (public method; ok for atoms in frozen molecules too)
        """
        # fyi: called from depositMode, but not (yet?) from movie-playing. [041110]
        if self.xyz != 'no':
            # bruce 041108 added xyz check, rather than asserting we don't need it;
            # this might never happen
            self.xyz = pos
            # The position being stored in the atom implies it's never been used
            # in the molecule (in curpos or atpos or anything derived from them),
            # so we don't need to invalidate anything in the molecule.
        else:
            # the position is stored in the molecule, so let it figure out the
            # proper way of adjusting it -- this also does the necessary invals.
            self.molecule.setatomposn(self.index, pos, self.element)
        # also invalidate the bonds or jigs which depend on our position.
        #e (should this be a separate method -- does anything else need it?)
        for b in self.bonds:
            b.setup_invalidate()
        if platform.atom_debug and self.jigs:
            print "bug: atom.setposn needs to invalidate jigs, but that's nim"
        return

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

    def draw(self, glpane, dispdef, col, level):
        """draw the atom depending on whether it is picked
        and its display mode (possibly inherited from dispdef).
        An atom's display mode overrides the inherited one from
        the molecule or glpane, but a molecule's color overrides the atom's
        element-dependent one
        """
        assert not self.__killed
        color = col or self.element.color
        disp, rad = self.howdraw(dispdef)
        if self == glpane.selatom: # bruce 041104 bugfix for bug#45
            if self.element == Singlet:
                color = LEDon
            else:
                color = orange
            if disp not in [diVDW, diCPK, diTUBES]:
                disp = diTUBES # Make sure selatom always gets drawn.
                # This is correct even if the atom is invisible, since if
                # depositMode stored it into glpane.selatom, then it will act
                # on it when you click, so we should light it up to indicate
                # that. If depositMode wants to not light up invisible atoms,
                # or wants the choice of visible display mode to influence that,
                # all it needs to do is not store them in glpane.selatom (which
                # it also needs to do to avoid acting on them). [bruce 041104]
                # [bruce 041129: also rad = TubeRadius? I guess not.]
        # note use of basepos (in atom.baseposn) since it's being drawn under
        # rotation/translation of molecule
        pos = self.baseposn()
        if disp in [diVDW, diCPK]:
            drawsphere(color, pos, rad, level)
        rad *= 1.1
        if disp == diTUBES:
            if self == glpane.selatom:
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
        # bruce 041109 comment: this changes appearance of this atom's bonds,
        # so: do we need to invalidate the bonds? No, they don't store display
        # info, and the geometry related to bond.setup_invalidate has not changed.
        # What about the mols on both ends of the bonds? The changeapp() handles
        # that for internal bonds, and external bonds are redrawn every time so
        # no invals are needed if their appearance changes.

    def howdraw(self, dispdef):
        """Tell how to draw the atom depending on its display mode (possibly
        inherited from dispdef). An atom's display mode overrides the inherited
        one from the molecule or glpane, but a molecule's color overrides the
        atom's element-dependent one (color is done in atom.draw, not here).
        Return display mode and radius to use, in a tuple (disp, rad).
        Note that atom.draw further modifies the radius in some cases.
        """
        if dispdef == diDEFAULT: #bruce 041129 permanent debug code, re bug 21
            if platform.atom_debug:
                print "bug warning: dispdef == diDEFAULT in atom.howdraw for %r" % self
            ## this workaround would be possible, but I'm not doing it:
            ## dispdef = default_display_mode
        if self.element == Singlet:
            disp,rad = self.bonds[0].other(self).howdraw(dispdef)
            # note: this rad is going to be replaced, below
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
    def writepov(self, file, dispdef, col):
        color = col or self.element.color
        color = color * V(1,1,-1) # kluge for povpoint(color)
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
        goes through the atom (defined as a sphere 70% its vdW radius).
        This is a royal kludge, needs to be replaced by something
        that uses the screen representation
        [or caller can pass disp, r to indicate that]
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
            # [mark 2004-10-14] [bruce 041104: needs revision, but ok for now]
            self.molecule.assy.w.msgbarLabel.setText(self.getinfo())
                
    def unpick(self):
        """make the atom unselected
        """
        # note: this is inlined into assembly.unpickatoms
        if self.element == Singlet: return
        if self.picked:
            self.picked = 0
            del self.molecule.assy.selatoms[self.key]
            self.molecule.changeapp()
            #self.molecule.assy.w.msgbarLabel.setText(" ")

    def copy_for_mol_copy(self, numol):
        # bruce 041113 changed semantics, and renamed from copy()
        # to ensure only one caller, which is mol.copy()
        """create a copy of the atom (to go in numol, a copy of its molecule),
        with .xyz == 'no' and .index the same as in self;
        caller must also call numol.invalidate_atom_lists() at least once
        [private method, only suitable for use from mol.copy(), since use of
         same .index assumes numol will be given copied curpos/basepos arrays.]
        """
        nuat = atom(self.element.symbol, 'no', None)
        numol.addcopiedatom(nuat)
        ## numol.invalidate_atom_lists() -- done in caller now
        nuat.index = self.index
        nuat.display = self.display #bruce 041109 new feature, seems best
        try:
            nuat.info = self.info
            # bruce 041109, needed by extrude and other future things
        except AttributeError:
            pass
        return nuat

    def copy(self): # bruce 041116, new method
        # (warning: has previous name of copy_for_mol_copy method)
        """Public method: copy an atom, with no special assumptions;
        new atom is not in any mol but could be added to one using mol.addatom.
        """
        nuat = atom(self.element.symbol, self.posn(), None)
        nuat.display = self.display
        try:
            nuat.info = self.info
            # bruce 041109, needed by extrude and other future things
        except AttributeError:
            pass
        return nuat

    def unbond(self, b):
        """Private method (for use mainly by bonds); remove b from self and
        usually replace it with a singlet. Details:
           Remove bond b from self (error if b not in self.bonds).
        Note that bonds are compared with __eq__, not 'is', by 'in' and 'remove'.
        Only call this when b will be destroyed, or "recycled" (by bond.rebond);
        thus no need to invalidate the bond b itself -- caller must do whatever
        inval of bond b is needed (which is nothing, if it will be destroyed).
           Then replace bond b in self.bonds with a new bond to a new singlet,
        unless self or the old neighbor atom is a singlet.
        Do all necessary invalidations of molecules, BUT NOT OF b (see above).
           If self is a singlet, kill it (singlets must always have one bond).
           As of 041109, this is called from atom.kill of the other atom,
        and from bond.bust, and [added by bruce 041109] from bond.rebond.
        """
        # [obsolete comment: Caller is responsible for shakedown
        #  or kill (after clearing externs) of affected molecules.]
        
        # code and docstring revised by bruce 041029, 041105-12
        
        b.invalidate_bonded_mols() #e more efficient if callers did this
        
        try:
            self.bonds.remove(b)
        except ValueError: # list.remove(x): x not in list
            # this is always a bug in the caller, but we catch it here to
            # prevent turning it into a worse bug [bruce 041028]
            msg = "fyi: atom.unbond: bond %r should be in bonds %r\n of atom %r, " \
                  "but is not:\n " % (b, self.bonds, self)
            print_compact_traceback(msg)
        # normally replace an atom (bonded to self) with a singlet,
        # but don't replace a singlet (at2) with a singlet,
        # and don't add a singlet to another singlet (self).
        if self.element == Singlet:
            if not self.bonds:
                self.kill() # bruce 041115 added this and revised all callers
            else:
                print "fyi: bug: unbond on a singlet %r finds unexpected bonds left over in it, %r" % (self,self.bonds)
                # don't kill it, in this case [bruce 041115; I don't know if this ever happens]
            return
        at2 = b.other(self)
        if at2.element == Singlet: return
        x = atom('X', b.ubp(self), self.molecule) # invals mol as needed
        self.molecule.bond(self, x) # invals mol as needed
    
    def hopmol(self, numol): #bruce 041105-041109 extensively revised this
        """If this atom is not already in molecule numol, unpick it and move it
        to molecule numol. (This only changes the owning molecule -- it doesn't
        change this atom's position in space!) Also move its singlet-neighbors.
        Do all necessary invalidations of old and new molecules,
        including for this atom's bonds (both internal and external),
        since some of those bonds might change from internal to external
        or vice versa, which changes how they need to be drawn.
        """
        if self.molecule == numol:
            return
        self.unpick() #e do we still want this? we no longer need it, i think
        # (in fact our only caller as of 041118, modifySeparate, does it redundantly)
        self.molecule.delatom(self) # this also invalidates our bonds
        numol.addatom(self)
        for a in self.singNeighbors():
            assert self.element != Singlet # (only if we have singNeighbors!)
                # (since hopmol would infrecur if two singlets were bonded)
            a.hopmol(numol)
        return
    
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
        """(Public method:)
        Change the element type of this atom to element elt
        (an element object for a real element, not Singlet),
        and do the necessary invalidations.
        Note: this does not change any atom or singlet positions, so callers
        wanting to correct bond lengths need to do that themselves.
        """
        if platform.atom_debug:
            if elt == Singlet: #bruce 041118
                # this is unsupported; if we support it it would require
                # moving this atom to its neighbor atom's chunk, too
                print "fyi, bug?: mvElement changing %r to a singlet" % self
        self.element = elt
        for b in self.bonds:
            b.setup_invalidate()
        self.molecule.changeapp()
        # no need to invalidate shakedown-related things, I think [bruce 041112]

    def invalidate_bonds(self): # also often inlined
        for b in self.bonds:
            b.setup_invalidate()
        
    def killed(self): #bruce 041029
        """(Public method) Report whether an atom has been killed.
        Details: For an ordinary atom, return False.
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
                from chunk import _nullMol
                assert self.molecule == _nullMol or self.molecule == None
                # thus don't do this: assert not self.key in self.molecule.assy.selatoms
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
        """Public method:
        kill an atom: unpick it, remove it from its jigs, remove its bonds,
        then remove it from its molecule. Do all necessary invalidations.
        (Note that molecules left with no atoms, by this or any other op,
        will themselves be killed.)
        """
        if self.__killed:
            if not self.element == Singlet:
                print_compact_stack("fyi: atom %r killed twice; ignoring:\n" % self)
            else:
                # Note: killing a selected mol, using Delete key, kills a lot of
                # singlets twice; I guess it's because we kill every atom
                # and singlet in mol, but also kill singlets of killed atoms.
                # So I'll declare this legal, for singlets only. [bruce 041115]
                pass
            return
        self.__killed = 1 # do this now, to reduce repeated exceptions (works??)
        # unpick
        try:
            self.unpick() #bruce 041029
        except:
            print_compact_traceback("fyi: atom.kill: ignoring error in unpick: ")
            pass
        # bruce 041115 reordered everything that follows, so it's safe to use
        # delatom (now at the end, after things which depend on self.molecule),
        # since delatom resets self.molecule to None.
        
        # josh 10/26 to fix bug 85 - remove from jigs
        for j in self.jigs:
            try:
                j.rematom(self)
            except:
                print_compact_traceback("fyi: atom.kill: ignoring error in rematom %r from jig %r: " % (self,j) )
        self.jigs = [] #bruce 041029 mitigate repeated kills
        
        # remove bonds
        for b in self.bonds:
            n = b.other(self)
            n.unbond(b) # note: this can create a new singlet on n, if n is real,
                        # which requires computing b.ubp which uses self.posn();
                        # or it can kill n if it's a singlet
            # note: as of 041029 unbond also invalidates externs if necessary
            ## if n.element == Singlet: n.kill() -- done in unbond as of 041115
        self.bonds = [] #bruce 041029 mitigate repeated kills

        # only after disconnected from everything else, remove it from its molecule
        try:
            ## del self.molecule.atoms[self.key]
            self.molecule.delatom(self) # bruce 041115
            # delatom also kills the mol if it becomes empty (as of bruce 041116)
        except KeyError:
            print "fyi: atom.kill: atom %r not in its molecule (killed twice?)" % self
            pass
        return # from atom.kill

    def Hydrogenate(self):
        """(Public method; does all needed invalidations)
        If this atom is a singlet, change it to a hydrogen,
        and assuming it was already at the right distance from its neighbor
        when it was a singlet (not checked), move it farther away so this
        is again true now that it's a hydrogen.
        """
        if not self.element == Singlet: return
        o = self.bonds[0].other(self)
        self.mvElement(Hydrogen)
        # bruce 041112 rewrote following code
        singpos = self.posn()
        otherpos = o.posn()
        singvec = norm( singpos - otherpos)
        newsingpos = singpos + Hydrogen.rcovalent * singvec
        self.setposn(newsingpos)
        return

    def Dehydrogenate(self):
        """If this is a hydrogen atom (and if it was not already killed),
        kill it and return 1 (int, not boolean), otherwise return 0.
        (Killing it should produce a singlet unless it was bonded to one.)
        (Public method; does all needed invalidations.)
        """
        # [fyi: some new features were added by bruce, 041018 and 041029;
        #  need for callers to shakedown or kill mols removed, bruce 041116]
        if self.element == Hydrogen and not self.killed():
            #bruce 041029 added self.killed() check above to fix bug 152
            self.kill()
            # note that the new singlet produced by killing self might be in a
            # different mol (since it needs to be in our neighbor atom's mol)
            return 1
        else:
            return 0
        pass

    def snuggle(self):
        """self is a singlet and the simulator has moved it out to the
        radius of an H. move it back. the molecule is still in frozen
        mode. Do all needed invals.
        """
        o = self.bonds[0].other(self)
        op = o.posn()
        np = norm(self.posn()-op)*o.element.rcovalent + op
        # bruce 041112 rewrote last line
        self.setposn(np)
        ## self.molecule.curpos[self.index] = np

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

    def is_singlet(self):
        return self.element == Singlet
    
    def singlet_neighbor(self): #bruce 041109 moved here from extrudeMode.py
        "return the atom self (a known singlet) is bonded to, checking assertions"
        assert self.element == Singlet
        obond = self.bonds[0]
        atom = obond.other(self)
        assert atom.element != Singlet, "bug: a singlet %r is bonded to another singlet %r!!" % (self,atom)
        return atom

    # debugging methods (not yet fully tested; use at your own risk)
    
    def invalidate_everything(self): # for an atom, remove it and then readd it to its mol
        "debugging method"
        if len(self.molecule.atoms) == 1:
            print "warning: invalidate_everything on the only atom in mol %r\n" \
                  " might kill mol as a side effect!" % self.molecule
        # note: delatom invals self.bonds
        self.molecule.delatom(self) # note: this kills the mol if it becomes empty!
        self.molecule.addatom(self)
        return

    def update_everything(self):
        print "atom.update_everything() does nothing"
        return

    pass # end of class atom

def singlet_atom(singlet):
    "return the atom a singlet is bonded to, checking assertions"
    return singlet.singlet_neighbor()

# ==

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

# == Bond

def bonded(at1, at2): #bruce 041119
    "are these atoms (or singlets) already directly bonded?"
    return at2 in at1.neighbors()

def bond_atoms(at1,at2):
    """Make a new bond between atoms at1 and at2 (and add it to their lists of bonds),
    if they are not already bonded; if they are already bonded do nothing. Return None.
    (The new bond object, if one is made, can't be found except by scanning the bonds
    of one of the atoms.)
       If at1 == at2, this is an error; print a warning and do nothing.
       This increases the number of bonds on each atom (when it makes a new bond) --
    it never removes any singlets. Therefore it is mostly for low-level use.
    It could be called directly, but is usually called via the method molecule.bond,
    purely for historical reasons.
    """
    # bruce 041109 split this out of molecule.bond. Since it's the only caller of
    # Bond.__init__, what it does to the atoms could (and probably shoould) be put
    # inside the constructor. However, it should not simply be replaced with calls
    # to the constructor, in case we someday want it to return the bond which it
    # either makes (as the constructor does) or doesn't make (when the atoms are
    # already bonded). The test for a prior bond makes more sense outside of the
    # Bond constructor.
    if at1 == at2: #bruce 041119, partial response to bug #203
        print "BUG: bond_atoms was asked to bond %r to itself." % at1
        print "Doing nothing (but further bugs may be caused by this)."
        print_compact_stack()
        return

    b = Bond(at1,at2) # (this does all necessary invals)
    
    #bruce 041029 precautionary change -- I find in debugging that the bond
    # can be already in one but not the other of at1.bonds and at2.bonds,
    # as a result of prior bugs. To avoid worsening those bugs, we should
    # change this... but for now I'll just print a message about it.
    #bruce 041109: when this happens I'll now also remove the obsolete bond.
    if (b in at1.bonds) != (b in at2.bonds):
        print "fyi: debug: for new bond %r, (b in at1.bonds) != (b in at2.bonds); removing old bond" % b
        try:
            at1.bonds.remove(b)
        except:
            pass
        try:
            at2.bonds.remove(b)
        except:
            pass
    if not b in at2.bonds:
        at1.bonds += [b]
        at2.bonds += [b]
    else:
        # [bruce comment 041115: I don't know if this ever happens,
        #  or if it's a good idea for it to be allowed, but it is allowed.
        #  #e should it inval the old bond? I think so, but didn't add that.
        #  later: it happens a lot when entering Extrude; guess: mol.copy copies
        #  each internal bond twice (sounds right, but I did not verify this).]
        pass
        
    return

#bruce 041109:
# Capitalized name of class Bond, so we can find all uses of it in the code;
# as of now there is only one use, in bond_atoms (used by molecule.bond).
# I also rewrote lots of the code in class Bond.

class Bond:
    """A Bond is essentially a record pointing to two atoms
    (either one of which might be a real atom or a "singlet"),
    representing a bond between them if it also occurs in atom.bonds
    for each atom. It should occur in both or neither of atom.bonds
    of its two atoms, except transiently.
       The two atoms in a bond should always be different objects.
       We don't support more than one bond between the same two
    atoms; trying to add the second one will do nothing, because
    of Bond.__eq__. We don't yet support double or triple bonds.
       Bonds have a private member 'key' so they can be compared equal
    whenever they involve the same pair of atoms (in either order).
       Bonds sometimes store geometric info used to draw them; see
    the method setup_invalidate, which must be called when the atoms
    are changed in certain ways. Bonds don't store any selection
    state or display-mode state, and they record no info about the
    bonded molecules (but each bonded atom knows its molecule).
       Bonds are called "external" if they connect atoms in two
    different molecules, or "internal" if they connect two atoms
    in the same molecule. This affects what kind of info is
    invalidated by the private method invalidate_bonded_mols, which
    should be called by internal code whenever the bond is actually
    added to or removed from its atoms
    (or is probably about to be added or removed).
       Bonds can be removed from their atoms by Bond.bust, and then
    forgotten about (no need to kill or otherwise explicitly destroy
    them after they're not on their atoms).
    """
    
    def __init__(self, at1, at2): # no longer also called from self.rebond()
        """create a bond from atom at1 to atom at2.
        the key created will be the same whichever order the atoms are
        given, and is used to compare bonds.
        [further comments by bruce 041029:]
        Private method (that is, creating of bond objects is private, for
        affected molecules and/or atoms). Note: the bond is not actually added
        to the atoms' molecules! Caller must do that. But [new feature 041109]
        we will do all necessary invalidations, in case the new bond is indeed
        added to those atoms (as I think it always will be in the current code).
        """
        self.atom1 = at1
        self.atom2 = at2
        ## self.picked = 0 # bruce 041029 removed this since it seems unused
        self.changed_atoms()
        self.invalidate_bonded_mols() #bruce 041109 new feature

    def changed_atoms(self):
        """Private method to call when the atoms assigned to this bond are changed.
        WARNING: does not call setup_invalidate(), though that would often also
        be needed, as would invalidate_bonded_mols() both before and after the change.
        """
        at1 = self.atom1
        at2 = self.atom2
        assert at1 != at2
        self.key = 65536*min(at1.key,at2.key)+max(at1.key,at2.key)
        return
    
    def invalidate_bonded_mols(self): #bruce 041109
        """Private method to call when a bond is made or destroyed;
        knows which kinds of bonds are put into a display list by molecule.draw
        (internal bonds) or put into into mol.externs (external bonds),
        though this knowledge should ideally be private to class molecule.
        """
        # assume mols are not None (they might be _nullMol, that's ok)
        mol1 = self.atom1.molecule
        mol2 = self.atom2.molecule
        if mol1 != mol2:
            # external bond
            mol1.invalidate_attr('externs')
            mol2.invalidate_attr('externs')
        else:
            # internal bond
            mol1.havelist = 0
        return

    def setup_invalidate(self):
        """Semi-private method for bonds. Invalidates cached geometric values
        related to drawing the bond.
         This must be called whenever the position or element of either bonded
        atom is changed, or when either atom's molecule changes if this affects
        whether it's an external bond (since the coordinate system used for drawing
        is different in each case).
         (FYI: It need not be called for other changes that might affect bond
        appearance, like disp or color of bonded molecules, though for internal
        bonds, the molecule's .havelist should be reset when those things change.)
          Note that before the "inval/update" revisions [bruce 041104],
        self.setup() (the old name for this method, from point of view of callers)
        did the recomputation now done on demand by __setup_update; now this method
        only does the invalidation which makes sure that recomputation will happen
        when it's needed.
        """
        # just delete all the attrs recomputed by self.__setup_update()
        try:
            del self.c1
        except AttributeError:
            pass # assume other attrs are also not there
        else:
            # assume other attrs are also there
            del self.c2, self.center, self.a1pos, self.a2pos, self.toolong
        # for internal bonds, or bonds that used to be internal
        # (which we can't detect, so this means for *all* bonds),
        # also reset mol.havelist (for each affected mol).
        #e (This might not be needed if all callers remember to do this,
        # as they should have. And it might cause unnecessary redrawing of
        # display lists, if callers know better than we do when to do it.
        # So we should make all callers do it when needed, and not do it here.
        # ###e optimize by doing that... NEW CALLERS: DON'T ASSUME WE INVAL HAVELISTS HERE)

        # (These mols might sometimes be _nullMol but should never be None:)
        self.atom1.molecule.havelist = 0 
        self.atom2.molecule.havelist = 0
        ###e should be removed if we have time; see comment above and all callers;
        # but more likely I'll just decide to not bother invalling bonds at all
        # (but then, certainly, i have to ensure callers do their own havelist=0)
        # ###@@@ bruce 041118
        return

    def __setup_update(self):
        """Private method. Before bruce 041104 this was called self.setup()
        and was called more widely; now the method of that name just invalidates
        the same attrs we recompute, by deleting them.
         Now, this is only called by __getattr__ when we need to recompute one
        or more of those attributes, to set up the bond for drawing.
        Sets a1pos, a2pos using mol-relative positions for internal bonds
        (atoms in same molecule), or absolute positions for external bonds.
        Sets c1, c2, and center to points along the bond useful for drawing it,
        except for too-long bonds whose center is set to None.
        """
        # [docstring revised, and inval/update scheme added, by bruce 041104]
        if self.atom1.molecule != self.atom2.molecule:
            # external bond; use absolute positions
            self.a1pos = self.atom1.posn()
            self.a2pos = self.atom2.posn()
        else:
            # internal bond; use mol-relative positions.
            # Note: this means any change to mol's coordinate system
            # (basecenter and quat) requires calling setup_invalidate
            # in this bond! That's a pain (and inefficient), so I might
            # replace it by a __getattr__ mol-coordsys-version-number check...
            # ##e [bruce 041115]
            basepos = self.atom1.molecule.basepos
            # if basepos is recomputed by __getattr__, that might have altered
            # the atom indices, and they might not have been valid before.
            self.a1pos = basepos[self.atom1.index]
            self.a2pos = basepos[self.atom2.index]
        vec = self.a2pos - self.a1pos
        len = 0.98 * vlen(vec)
        vec = norm(vec)
        self.c1 = self.a1pos + vec*self.atom1.element.rcovalent
        self.c2 = self.a2pos - vec*self.atom2.element.rcovalent
        self.toolong = (len > self.atom1.element.rcovalent + self.atom2.element.rcovalent)
        self.center = (self.c1 + self.c2) /2.0 # before 041112 this was None when self.toolong
        return

    def __getattr__(self, attr): # bond.__getattr__ #bruce 041104
        """Called when one of the attrs computed by self.__setup_update() is
        needed, but was not yet computed or was deleted since last computed
        (as our way of invalidating it). Also might be called for an arbitrary
        missing attr due to a bug in the calling code. Now that this __getattr__
        method exists, no other calls of self.__setup_update() should be needed.
        """
        if not attr in ['a1pos','a2pos','c1','c2','center','toolong']:
            # unfortunately (since it's slow) we can't avoid checking this first,
            # or we risk infinite recursion due to a missing attr needed by setup
            raise AttributeError, "bond has no %r" % attr
        self.__setup_update() # this should add the attribute (or raise an exception
          # if it's called too early while initing the bond or one of its molecules)
        return self.__dict__[attr] # raise exception if attr still missing

    def other(self, atm):
        """Given one atom the bond is connected to, return the other one
        """
        if self.atom1 == atm: return self.atom2
        assert self.atom2 == atm #bruce 041029
        return self.atom1

    def othermol(self, mol): #bruce 041123; not yet used or tested
        """Given the molecule of one atom of this bond, return the mol
        of the other one. Error if mol is not one of the bonded mols.
        Note that this implies that for an internal bond within mol,
        the input must be mol and we always return mol.
        """
        if mol == self.atom1.molecule:
            return self.atom2.molecule
        elif mol == self.atom2.molecule:
            return self.atom1.molecule
        else:
            assert mol in [self.atom1.molecule, self.atom2.molecule]
            # this always fails -- it's just our "understandable error message"
        pass
    
    def ubp(self, atom):
        """ unbond point (atom must be one of the bond's atoms) """
        #bruce 041115 bugfixed this for when mol.quat is not 1,
        # tho i never looked for or saw an effect from the bug in that case
        if atom == self.atom1:
            point = self.c1
        else:
            assert atom == self.atom2
            point = self.c2
        # now figure out what coord system that's in
        if self.atom1.molecule != self.atom2.molecule:
            return point
        else:
            return self.atom1.molecule.base_to_abs(point)
        pass

    # "break" is a python keyword
    def bust(self):
        """Destroy this bond, modifying the bonded atoms as needed
        (by adding singlets in place of this bond -- they might overlap!),
        and invalidating the bonded molecules as needed.
        (This method is named 'bust' since 'break' is a python keyword.)
        If either atom is a singlet, kill that atom.
        (Note: as of 041115 bust is never called with either atom a singlet.)
        """
        # bruce 041115: bust is never called with either atom a singlet,
        # but since atom.unbond now kills singlets lacking any bonds,
        # and since not doing that would be bad, I added a note about that
        # to the docstring.
        self.atom1.unbond(self) # does all needed invals
        self.atom2.unbond(self)
        ###e do we want to also change our atoms and key to None, for safety?
        ###e check all callers and decide
        return
    
    def rebond(self, old, new):
        """Self is a bond between old (typically a singlet) and some atom A;
        replace old with new in this same bond (self),
        so that old no longer bonds to A but new does.
        Unlike some other bonding methods, the number of bonds on new increases
        by 1, since no singlet on new is removed -- new is intended to be
        a just-created atom, not one with the right number of existing bonds.
        If old is a singlet, then kill it since it now has no bonds.
        Do the necessary invalidations in self and all involved molecules.
        """
        # [bruce 041109 added docstring and rewrote Josh's code:]
        # Josh said: intended for use on singlets, other uses may have bugs.
        # bruce 041109: I think that means "old" is intended to be a singlet.
        # I will try to make it safe for any atoms, and do all needed invals.
        if self.atom1 == old:
            old.unbond(self) # also kills old if it's a singlet, as of 041115
            ## if len(old.bonds) == 1: del old.molecule.atoms[old.key] --
            ## the above code removed the singlet, old, without killing it.
            self.atom1 = new
        elif self.atom2 == old:
            old.unbond(self)
            self.atom2 = new
        else:
            print "fyi: bug: rebond: %r doesn't contain atom %r to replace with atom %r" % (self, old, new)
            # no changes in the structure
            return
        # bruce 041109 worries slightly about order of the following:
        # invalidate this bond itself
        self.changed_atoms()
        self.setup_invalidate()
        # add this bond to new
        new.bonds += [self]
            #e put this in some private method on new, new.add_new_bond(self)??
            #  Note that it's intended to increase number of bonds on new,
            #  not to zap a singlet already bonded to new.
        # Invalidate molecules (of both our atoms) as needed, due to our existence
        self.invalidate_bonded_mols()

    def __eq__(self, ob):
        return ob.key == self.key

    def __ne__(self, ob):
        # bruce 041028 -- python doc advises defining __ne__
        # whenever you define __eq__
        return not self.__eq__(ob)

    def draw(self, glpane, dispdef, col, level):
        """Draw the bond. Note that for external bonds, this is called twice,
        once for each bonded molecule (in arbitrary order)
        (and is never cached in either mol's display list);
        each of these calls gets dispdef, col, and level from a different mol.
        [bruce, 041104, thinks that leads to some bugs in bond looks.]
        Bonds are drawn only in certain display modes (CPK, LINES, TUBES).
        The display mode is inherited from the atoms or molecule (as passed in
         via dispdef from the calling molecule -- this might cause bugs if some
         callers change display mode but don't set havelist = 0, but maybe they do).
        Lines or tubes change color from atom to atom, and are red in the middle
        for long bonds. CPK bonds are drawn in the calling molecule's color or
        in the constant bondColor (which is light gray).
        """
        #bruce 041104 revised docstring, added comments about possible bugs.
        # Note that this code depends on finding the attrs toolong, center,
        # a1pos, a2pos, c1, c2, as created by self.__setup_update().
        # As of 041109 this is now handled by bond.__getattr__.
        # The attr toolong is new as of 041112.
        
        color1 = col or self.atom1.element.color
        color2 = col or self.atom2.element.color

        disp=max(self.atom1.display, self.atom2.display)
        if disp == diDEFAULT: disp= dispdef
        if disp == diLINES:
            if not self.toolong:
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
            ###e bruce 041104 suspects v1, v2 wrong for external bonds, needs
            # to look at each mol's .hidden (but this is purely a guess)
            if not self.toolong:
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

    # write to a povray file:  draw a single bond [never reviewed by bruce]
    # [note: this redundantly computes attrs like _setup_update computes for
    #  draw, and instead we should just use those attrs, but I did not make
    #  this change since there is a current bug report which someone might
    #  fix by altering povpoint and the V(1,1,-1) kluges in here,
    #  and I want to avoid a cvs merge conflict. When this is fixed,
    #  note that I have changed self.center and added self.toolong; see
    #  self.draw() for details. -- bruce 041112 ###e]
    def writepov(self, file, dispdef, col):
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

    pass # end of class Bond

# ==

# class molecule used to be defined here, but now it's in chunk.py. [bruce 041118]

# for the sake of other files which still look for class molecule in this file,
# we'll import it here (this might not work if done at the top of this file):

from chunk import *

# end of chem.py
