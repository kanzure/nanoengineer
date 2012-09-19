 #!/usr/bin/python

# Copyright 2005, 2007 Nanorex, Inc.  See LICENSE file for details.
"""Nanotube generation tool for nanoENGINEER-1
Usage:
    nanotube.py <n> <m> <length>
where (n,m) is the chirality of the nanotube, and the length is in
nanometers. The resulting MMP file is written to standard output.
According to Dresselhaus et al, the bond lengths in the nanotube are
all 1.421 angstroms. The nanotube is passivated with oxygens and
hydrogens at the ends.
"""

# Some nice references on nanotube geometry and properties:
# http://physicsweb.org/articles/world/11/1/9
# http://physicsweb.org/articles/world/11/1/9/1/world-11-1-9-1

import sys
import string
import math

sqrt3 = 3 ** 0.5

def prettyClose(u,v):
    # floats are never perfectly equal
    return (u-v)**2 < 1.0e-10

def prettyClose3(x1,y1,z1,x2,y2,z2):
    return (prettyClose(x1, x2) and
            prettyClose(y1, y2) and
            prettyClose(z1, z2))

class Chirality:

    # Nanotube bond length according to Dresselhaus, M. S.,
    # Dresselhaus, G., Eklund, P. C. "Science of Fullerenes and Carbon
    # Nanotubes" Academic Press: San Diego, CA, 1995; pp. 760.
    BONDLENGTH = 1.421  # angstroms

    def __init__(self, n, m):
        self.n, self.m = n, m
        x = (n + 0.5 * m) * sqrt3
        y = 1.5 * m
        angle = math.atan2(y, x)
        twoPiRoverA = (x**2 + y**2) ** .5
        AoverR = (2 * math.pi) / twoPiRoverA
        self.__cos = math.cos(angle)
        self.__sin = math.sin(angle)
        # time to get the constants
        s, t = self.x1y1(0,0)
        u, v = self.x1y1(1./3, 1./3)
        w, x = self.x1y1(0,1)
        F = (t - v)**2
        G = 2 * (1 - math.cos(AoverR * (s - u)))
        H = (v - x)**2
        J = 2 * (1 - math.cos(AoverR * (u - w)))
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
        x3 = R * math.sin(x2/R)
        z3 = R * math.cos(x2/R)
        return (x3, y2, z3)

class Molecule:
    def __init__(self):
        self.atoms = [ ]
    def add(self, elt, x, y, z):
        for a2 in self.atoms:
            assert not prettyClose3(x, y, z,
                                    a2.x, a2.y, a2.z)
        class Atom:
            pass
        a = Atom()
        a.element = elt
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
            elif len(lst) == 1:
                self.atoms[k].element = "H"
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
    def mmp(self):
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
            if a.element == "C":
                outf.write("info atom atomtype = sp2\n")
                r = "bonda"
            elif a.element in ("O", "H"):
                outf.write("info atom atomtype = sp3\n")
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
    def rasmol(self):
        import os
        filename = "/tmp/foo.xyz"
        outf = open(filename, "w")
        r = repr(len(self.atoms)) + "\n"
        r += "glop\n"
        for a in self.atoms:
            r += a.element + (" %g %g %g\n" % (a.x, a.y, a.z))
        outf.write(r)
        outf.close()
        os.system("rasmol -xyz " + filename)
    def test(self):
        mindist = None
        maxdist = None
        for a, b in self.bonds:
            a, b = self.atoms[a-1], self.atoms[b-1]
            dist = ((a.x - b.x) ** 2 +
                    (a.y - b.y) ** 2 +
                    (a.z - b.z) ** 2) ** .5
            if mindist == None or dist < mindist:
                mindist = dist
            if maxdist == None or dist > maxdist:
                maxdist = dist
        return (mindist, maxdist)


if (__name__ == '__main__'):
    if len(sys.argv) < 4:
        sys.stderr.write(__doc__)
        sys.exit(1)

    n = string.atoi(sys.argv[1])
    m = string.atoi(sys.argv[2])
    length = string.atof(sys.argv[3])

    chirality = Chirality(n,m)

    M = Molecule()

    for n in range(chirality.n):
        mmin, mmax = chirality.mlimits(-.5 * length, .5 * length, n)
        for m in range(mmin-1, mmax+1):
            x, y, z = chirality.xyz(n, m)
            if -.5 * length <= y <= .5 * length:
                M.add("C", x, y, z)
            x, y, z = chirality.xyz(n+1./3, m+1./3)
            if -.5 * length <= y <= .5 * length:
                M.add("C", x, y, z)
    M.makeBonds(Chirality.BONDLENGTH * 1.2)
    M.passivate()

    M.mmp()
