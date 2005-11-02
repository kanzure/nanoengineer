# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
NanotubeGenerator.py

$Id$

See http://www.nanoengineer-1.net/mediawiki/index.php?title=Nanotube_generator_dialog
for notes about what's going on here.
"""

__author__ = "Will"

from qt import *
from NanotubeGeneratorDialog import *

sqrt3 = 3 ** 0.5

class Chirality:

    # Nanotube bond length according to Dresselhaus, M. S.,
    # Dresselhaus, G., Eklund, P. C. "Science of Fullerenes and Carbon
    # Nanotubes" Academic Press: San Diego, CA, 1995; pp. 760.
    BONDLENGTH = 1.421  # angstroms

    def __init__(self, n, m):
        self.n, self.m = n, m
        x = (n + 0.5 * m) * sqrt3
        y = 1.5 * m
        angle = atan2(y, x)
        twoPiRoverA = (x**2 + y**2) ** .5
        AoverR = (2 * pi) / twoPiRoverA
        self.__cos = cos(angle)
        self.__sin = sin(angle)
        # time to get the constants
        s, t = self.x1y1(0,0)
        u, v = self.x1y1(1./3, 1./3)
        w, x = self.x1y1(0,1)
        F = (t - v)**2
        G = 2 * (1 - cos(AoverR * (s - u)))
        H = (v - x)**2
        J = 2 * (1 - cos(AoverR * (u - w)))
        L = self.BONDLENGTH
        denom = F * J - G * H
        self.R = (L**2 * (F - H) / denom) ** .5
        self.B = (L**2 * (J - G) / denom) ** .5
        self.A = self.R * AoverR

    class ConstError(TypeError): pass
    def __setattr__(self,name,value):
        # Don't touch my precious constants
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't reassign " + name
        self.__dict__[name] = value

    def x1y1(self, n, m):
        c, s = self.__cos, self.__sin
        x = (n + .5*m) * sqrt3
        y = 1.5 * m
        x1 = x * c + y * s
        y1 = -x * s + y * c
        return (x1, y1)

    def mlimits(self, y3min, y3max, n):
        if y3max < y3min:
            y3min, y3max = y3max, y3min
        B, c, s = self.B, self.__cos, self.__sin
        P = sqrt3 * B * s
        Q = 1.5 * B * (c - s / sqrt3)
        m1, m2 = (y3min + P * n) / Q, (y3max + P * n) / Q
        return int(m1-1.5), int(m2+1.5)

    def xyz(self, n, m):
        x1, y1 = self.x1y1(n, m)
        x2, y2 = self.A * x1, self.B * y1
        R = self.R
        x3 = R * sin(x2/R)
        z3 = R * cos(x2/R)
        return (x3, y2, z3)

    def populate(self, mol, length):
        for n in range(self.n):
            mmin, mmax = chirality.mlimits(-.5 * length, .5 * length, n)
            for m in range(mmin-1, mmax+1):
                x, y, z = chirality.xyz(n, m)
                if -.5 * length <= y <= .5 * length:
                    mol.add("C", x, y, z)
                x, y, z = chirality.xyz(n+1./3, m+1./3)
                if -.5 * length <= y <= .5 * length:
                    mol.add("C", x, y, z)
        mol.makeBonds(self.BONDLENGTH * 1.2)

class Molecule:
    def __init__(self):
        self.atoms = [ ]
    def add(self, elt, x, y, z):
        class Atom:
            pass
        a = Atom()
        a.element = elt
        a.hybridization = "sp2"
        a.x, a.y, a.z = x, y, z
        self.atoms.append(a)
    def bondsForAtom(self, atomIndex):
        # atomIndex goes from 1..N, not 0..N-1
        lst = [ ]
        for k in range(len(self.bonds)):
            i, j = self.bonds[k]
            if i == atomIndex or j == atomIndex:
                lst.append(k)
        return lst
    def passivate(self):
        for k in range(len(self.atoms)):
            lst = self.bondsForAtom(k + 1)
            if len(lst) == 2:
                self.atoms[k].element = "O"
                self.atoms[k].hybridization = "sp3"
            elif len(lst) == 1:
                self.atoms[k].element = "H"
                self.atoms[k].hybridization = "sp3"
        # If a carbon is bonded to two oxygens, make it sp3.
        for k in range(len(self.atoms)):
            a = self.atoms[k]
            if a.element == "C":
                numox = 0
                for j in self.bondsForAtom(k + 1):
                    b = self.bonds[j]
                    if b[0] == k+1 and self.atoms[b[1]-1].element == "O":
                        numox += 1
                    elif b[1] == k+1 and self.atoms[b[0]-1].element == "O":
                        numox += 1
                if numox == 2:
                    a.hybridization = "sp3"
    def makeBonds(self, maxlen):
        self.bonds = [ ]
        n = len(self.atoms)
        for i in range(n):
            a = self.atoms[i]
            ax, ay, az = a.x, a.y, a.z
            for j in range(i+1,n):
                b = self.atoms[j]
                dist = ((ax - b.x) ** 2 +
                        (ay - b.y) ** 2 +
                        (az - b.z) ** 2) ** .5
                if dist <= maxlen:
                    self.bonds.append((i+1, j+1))
    def mmp(self, filename=None):
        if filename != None:
            outf = open(filename, "w")
        else:
            outf = sys.stdout
        outf.write("""mmpformat 050920 required
kelvin 300
group (View Data)
info opengroup open = False
egroup (View Data)
group (Untitled)
info opengroup open = True
mol (Nanotube.1) def
""")
        for i in range(len(self.atoms)):
            a = self.atoms[i]
            enum = {"C": 6, "O": 8, "H": 1}[a.element]
            outf.write("atom %d (%d) (%d, %d, %d) vdw\n" %
                       (i+1, enum,
                        int(1000*a.x), int(1000*a.y), int(1000*a.z)))
            outf.write("info atom atomtype = %s\n" % a.hybridization)
            if a.element == "C":
                r = "bonda"
            elif a.element in ("O", "H"):
                r = "bond1"
            else:
                raise Exception, "unknown element"
            bondlist = self.bondsForAtom(i+1)
            for k in bondlist:
                a1, a2 = self.bonds[k]
                if a2 < i+1:
                    r += " " + repr(a2)
                elif a1 < i+1:
                    r += " " + repr(a1)
            outf.write(r + "\n")
        outf.write("""egroup (Untitled)
end1
group (Clipboard)
info opengroup open = False
egroup (Clipboard)
end molecular machine part Untitled
""")
        outf.close()


class NanotubeGenerator(NanotubeGeneratorDialog):
    def __init__(self, chunk):
        NanotubeGeneratorDialog.__init__(self)

    def generateTube(self):
        if hasattr(self, "n") and hasattr(self, "m") and hasattr(self, "length"):
            chirality = Chirality(self.n, self.m)
            M = Molecule()
            chirality.populate(M, self.length)
            M.passivate()
            # BIG KLUDGE, JUST FOR TESTING! I don't yet know how to create
            # this as a chunk, so for now, just write an MMP file somewhere
            # harmless.
            M.mmp("/tmp/foo.mmp")

    def setN(self):
        self.n = string.atoi(self.textEdit1.getText())

    def setM(self):
        self.m = string.atoi(self.textEdit2.getText())

    def setLength(self):
        self.length = string.atof(self.textEdit3.getText())


"""
Damian's notes on cleaning up passivation:

Where there's one C, make it C-H, which will make its carbon atom
type (for now) aromatic. The rules for aromaticity (Huckel's 4n+2,
that is) break down in large pi-systems, so we don't need to worry
about counting rings to make the pi-electrons work out right.

Where there are two carbons (where you've got -O-O- now), make each
of those C-H, which will also make their atom types aromatic (those
same C-C units are the dimers the DC10c tip is designed to build
with).  There'll be no complaints from the nanotube community who,
like I said, don't typically think about any other atom types but C
and H (and H only when necessary).

"""
