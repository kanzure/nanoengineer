#!/usr/bin/env python

"""

For now, I'll make this capable of parsing fineMotion970116.pdb and no
more general than that. Later we'll want to parse general PDB files.

The FMC file only has three kinds of lines in it: HETATM, CONECT, and
END. The PDB spec has many more, but think about those later.

"""

import sys, string

lines = map(lambda x: x.strip(), sys.stdin.readlines())

atoms = { }   # permit out-of-order definition of atoms by index

atomicNumbers = {
    "H": 1,
    "C": 6,
    "N": 7,
    "O": 8,
    "F": 9,
    "S": 16,
    "SI": 14,
    "Si": 14
    }

class Atom:
    def __init__(self, index, sym, x, y, z):
        atoms[index] = self
        self.index = index
        self.sym = sym
        self.x = x
        self.y = y
        self.z = z
        self.brethren = [ ]
    def bond(self, other):
        self.brethren.append(other.index)
    def __repr__(self):
        r = "<%d %g %g %g [" % (self.sym, self.x, self.y, self.z)
        for b in self.brethren:
            r += "%d," % b
        return r[:-1] + "]>"
    def mmpAtom(self):
        # convert angstroms to 1e-13 m
        r = ("atom %d (%d) (%g,%g,%g)" %
             (self.index, atomicNumbers[self.sym],
              1000*self.x, 1000*self.y, 1000*self.z))
        bonds = 0
        r2 = "\nbond1"
        for b in self.brethren:
            if b < self.index:
                r2 += " %d" % b
                bonds = 1
        if bonds:
            r += r2
        return r

for x in lines:
    # print "<<<" + x + ">>>"
    if x.startswith("HETATM"):
        # handle an atom
        # fields: 0=HETATM, 1=index, 2=symbol,
        #    4=xpos, 5=ypos, 6=zpos, (3,7,8) useless
        (a,index,sym,b,xpos,ypos,zpos,c,d) = x.split()
        index = string.atoi(index)
        xpos = string.atof(xpos)
        ypos = string.atof(ypos)
        zpos = string.atof(zpos)
        Atom(index, sym, xpos, ypos, zpos)
    elif x.startswith("CONECT"):
        # handle a set of bonds
        connections = map(string.atoi, x.split()[1:])
        thisguy, connections = connections[0], connections[1:]
        thisguy = atoms[thisguy]
        for x in connections:
            thisguy.bond(atoms[x])

print "part bns foobar"
for k in atoms.keys():
    print atoms[k].mmpAtom()
print "end"
