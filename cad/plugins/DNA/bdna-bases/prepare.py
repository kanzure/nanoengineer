#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
import sys
import string

sys.path.append("../../../src")

from VQT import A, V, vlen

class AtomType:
    def __init__(self, symbol, number, rcovalent):
        self.symbol = symbol
        self.number = number
        self.rcovalent = rcovalent
    def __repr__(self):
        return '<' + self.symbol + '>'

periodicTable = [
    AtomType('X', 0, 0.0),
    AtomType('H', 1, 0.31),
    AtomType('C', 6, 0.77),
    AtomType('N', 7, 0.73),
    AtomType('O', 8, 0.69),
    AtomType('P', 15, 1.08),
    ]

def lookupAtomType(num):
    for at in periodicTable:
        if at.number == num:
            return at
    raise Exception("AtomType not found, num=" + repr(num))

class Atom:
    def __init__(self, mmpline):
        if mmpline != None:
            mmpline = mmpline.rstrip()
            self.mmpline = mmpline
            fields = mmpline.split()
            self.key = string.atoi(fields[1])
            self.style = fields[6]
            self.hybridization = None
            self.base = None
            self.atomtype = lookupAtomType(string.atoi(fields[2][1:-1]))
            self.x = 0.001 * string.atoi(fields[3][1:-1])
            self.y = 0.001 * string.atoi(fields[4][:-1])
            self.z = 0.001 * string.atoi(fields[5][:-1])
        else:
            self.mmpline = None
            self.key = 0
            self.style = None
            self.hybridization = None
            self.base = None
            self.atomtype = lookupAtomType(0)
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
        self.bonds = [ ]

    def is_singlet(self):
        return self.atomtype.symbol == 'X'

    def clone(self):
        a = Atom(self.mmpline)
        for attr in ('key', 'style', 'hybridization', 'base', 'atomtype',
                     'x', 'y', 'z', 'bonds'):
            setattr(a, attr, getattr(self, attr))
        return a

    def hybridize(self, hybrids={
        'C': { 4: 'sp3',
               3: 'sp2',
               2: 'sp',
               },

        'O': { 2: 'sp3',
               1: 'sp2',
               },

        'N': { 3: 'sp3',
               2: 'sp2',
               1: 'sp',
               }
        }):
        try:
            self.hybridization = hybrids[self.atomtype.symbol][len(self.bonds)]
        except KeyError:
            self.hybridization = None
    def posn(self):
        return V(self.x, self.y, self.z)
    def __repr__(self):
        r = "<%s %d (%g, %g, %g)" % \
               (self.atomtype.symbol, self.key, self.x, self.y, self.z)
        r += " %s" % self.style
        if self.hybridization != None:
            r += " %s" % self.hybridization
        if self.base != None:
            r += " (base %d)" % self.base
        if self.bonds:
            r += " ["
            for b in self.bonds:
                r += " " + repr(b)
            r += " ]"
        return r + ">"

class Bondpoint(Atom):
    def __init__(self, owner, v):
        Atom.__init__(self, mmpline=None)
        self.style = owner.style
        self.base = owner.base
        self.x = v[0]
        self.y = v[1]
        self.z = v[2]
        self.bonds = [ owner.key ]
    def __repr__(self):
        r = "<%s %d (%g, %g, %g)" % \
               (self.atomtype.symbol, self.key, self.x, self.y, self.z)
        r += " %s" % self.style
        if self.base != None:
            r += " (base %d)" % self.base
        if self.bonds:
            r += " ["
            for b in self.bonds:
                r += " " + repr(b)
            r += " ]"
        return r + ">"

class MakeBondpoint(Exception):
    pass

class Base:
    def __init__(self, strand, key):
        self.key = key
        self.atomlist = [ ]
        self.phosphorusZcoord = 0.
        self.strand = strand
        atm0 = strand.atoms[key]
        self.style = atm0.style
        self.addAtom(atm0)

    def __cmp__(self, other):
        return -cmp(self.phosphorusZcoord, other.phosphorusZcoord)

    def keys(self):
        return map(lambda a: a.key, self.atomlist)

    def __len__(self):
        return len(self.atomlist)

    def addAtom(self, a):
        k = a.key
        if a not in self.atomlist:
            if a.style == self.style:
                a.base = self.key
                self.atomlist.append(a)
                if a.atomtype.symbol == 'P':
                    self.phosphorusZcoord = a.z
            else:
                raise MakeBondpoint

    def addLayer(self):
        atoms = self.strand.atoms
        newguys = [ ]
        for a in self.atomlist:
            for k in a.bonds:
                if k not in newguys and k not in self.keys():
                    newguys.append(k)
                    atoms[k].buddy = a
        newAtoms = 0
        for k in newguys:
            a2 = atoms[k]
            a = a2.buddy
            try:
                self.addAtom(a2)
                newAtoms += 1
            except MakeBondpoint:
                # don't make this bondpoint if it's already been made
                if not hasattr(a, 'gotBondpoint'):
                    p1, p2 = a.posn(), a2.posn()
                    r1, r2 = a.atomtype.rcovalent, a2.atomtype.rcovalent
                    p = (r2 * p1 + r1 * p2) / (r1 + r2)
                    bpt = Bondpoint(a, p)
                    # pick up a new key
                    self.strand.addAtom(bpt)
                    self.addAtom(bpt)
                    a.gotBondpoint = True
        return newAtoms

    def grow(self):
        while True:
            if self.addLayer() == 0:
                return

class Strand:
    def __init__(self, filename=None):
        self.atoms = { }
        self.nextKey = 1
        self.bases = [ ]
        if filename != None:
            for L in open(filename).readlines():
                if L.startswith("atom"):
                    self.addAtom(Atom(L))
            self.assignBases()

    def addAtom(self, a):
        a.key = key = self.nextKey
        self.nextKey += 1
        self.atoms[key] = a

    def transform(self, t):
        if t.func_code.co_argcount == 1:
            for a in self.atoms.values():
                v = V(a.x, a.y, a.z)
                a.x, a.y, a.z = tuple(t(v))
        else:
            for a in self.atoms.values():
                a.x, a.y, a.z = t(a.x, a.y, a.z)

    def addAtomFromMmp(self, mmpline):
        self.addAtom(Atom(mmpline))

    def inferBonds(self):
        maxBondLength = 2.5
        def quantize(vec, maxBondLength=maxBondLength):
            return (int(vec[0] / maxBondLength),
                    int(vec[1] / maxBondLength),
                    int(vec[2] / maxBondLength))
        def bond_atoms(a1, a2):
            if a1.key not in a2.bonds:
                a2.bonds.append(a1.key)
            if a2.key not in a1.bonds:
                a1.bonds.append(a2.key)
        buckets = { }
        for atom in self.atoms.values():
            atom.bonds = [ ]  # clear existing bonds
            # put this atom in one of the buckets
            key = quantize(atom.posn())
            try:
                buckets[key].append(atom)
            except KeyError:
                buckets[key] = [ atom ]
        def region(center):
            lst = [ ]
            x0, y0, z0 = quantize(center)
            for x in range(x0 - 1, x0 + 2):
                for y in range(y0 - 1, y0 + 2):
                    for z in range(z0 - 1, z0 + 2):
                        key = (x, y, z)
                        try:
                            lst += buckets[key]
                        except KeyError:
                            pass
            return lst
        for atm1 in self.atoms.values():
            for atm2 in region(atm1.posn()):
                bondLen = vlen(atm1.posn() - atm2.posn())
                idealBondLen = atm1.atomtype.rcovalent + atm2.atomtype.rcovalent
                a = 0.2
                if (1-a) * idealBondLen < bondLen < (1+a) * idealBondLen:
                    bond_atoms(atm1, atm2)
            atm1.hybridize()

    def assignBases(self):
        self.inferBonds()
        remainingKeys = self.atoms.keys()
        while len(remainingKeys) > 0:
            baseKey = remainingKeys[0]
            print "Base", baseKey
            base = Base(self, baseKey)
            self.bases.append(base)
            remainingKeys = remainingKeys[1:]
            base.grow()
            for key in base.keys():
                if key in remainingKeys:
                    remainingKeys.remove(key)

    def renumberAtoms(self):
        # Renumber their keys, and recompute bonds with new keys
        atomlist = self.atoms.values()
        self.atoms = { }
        self.nextKey = 1
        for i in range(len(atomlist)):
            self.addAtom(atomlist[i])
        self.inferBonds()

    def filter(self, filt):
        s = Strand()
        for a in self.atoms.values():
            if filt(a):
                s.addAtom(a.clone())
        s.inferBonds()
        return s

    def writeManyMmps(self, specs, tfm0, tfm):
        # discard tiny "bases" and any atoms in them
        tinybases = filter(lambda b: len(b) < 6, self.bases)
        for b in tinybases:
            for a in b.atomlist:
                del self.atoms[a.key]
        self.bases.remove(b)
        self.renumberAtoms()
        # sort bases in order of decreasing phosphorus z coord
        self.bases.sort()
        for index, groupname, filename in specs:
            basekey = self.bases[index].key
            base = self.filter(lambda a: a.base == basekey)
            def tfm2(x, y, z, tfm0=tfm0, tfm=tfm, index=index):
                v = V(x,y,z)
                v = tfm0(v)
                while index:
                    v = tfm(v)
                    index -= 1
                return tuple(v)
            base.transform(tfm2)
            base.writeMmp(filename, groupname)


    mmptext = """mmpformat 050920 required; 060421 preferred
kelvin 300
group (View Data)
info opengroup open = True
csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)
csys (LastView) (1.000000, 0.000000, 0.000000, 0.000000) (8.153929) (0.000000, 0.000000, 0.000000) (1.000000)
egroup (View Data)
group (%(groupname)s)
info opengroup open = True
%(text)s
egroup (%(groupname)s)
end1
group (Clipboard)
info opengroup open = False
egroup (Clipboard)
end molecular machine part %(groupname)s
"""

    def writeMmp(self, filename, groupname=None):
        # Sort the atoms by what group they are in
        atomlist = self.atoms.values()
        atomlist.sort(lambda a1, a2: cmp(a1.base, a2.base))
        self.renumberAtoms()
        # write the file
        s = ""
        thisgroup = None
        for a in self.atoms.values():
            if groupname == None:
                if thisgroup != a.base:
                    s += "mol (Strand %d) def\n" % a.base
                    thisgroup = a.base
            s += ("atom %d (%d) (%d, %d, %d) def\n" %
                  (a.key, a.atomtype.number,
                   int(1000 * a.x), int(1000 * a.y), int(1000 * a.z)))
            if a.hybridization != None:
                s += "info atom atomtype = " + a.hybridization + "\n"
            bstr = ""
            for b in a.bonds:
                if b < a.key:
                    bstr += " " + repr(b)
            if bstr:
                s += "bond1" + bstr + "\n"
        if groupname != None:
            s = "mol (" + groupname + ") def\n" + s
        outf = open(filename, "w")
        outf.write(self.mmptext % {"groupname": groupname, "text": s[:-1]})
        outf.close()

########################################

if (__name__ == '__main__'):
    g = Strand('strund1.mmp')
    specs = [
        (0, 'guanine', 'guanine.mmp'),
        (1, 'cytosine', 'cytosine.mmp'),
        (3, 'adenine', 'adenine.mmp'),
        (6, 'thymine', 'thymine.mmp')
        ]
    def tfm0(v):
        return v + V(0, 0, -18.7)
    def tfm(v):
        angle = -36 * pi / 180
        x, y, z = tuple(v)
        c, s = cos(angle), sin(angle)
        x, y = c * x + s * y, -s * x + c * y
        return V(x, y, z + 3.391)
    g.writeManyMmps(specs, tfm0, tfm)
