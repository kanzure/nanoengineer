#!/usr/bin/python

import sys, string
from math import *
from VQT import A, vlen

class AtomType:
    def __init__(self, symbol, number, rcovalent):
        self.symbol = symbol
        self.number = number
        self.rcovalent = rcovalent
    def __repr__(self):
        return '<' + self.symbol + '>'

periodicTable = [
    AtomType('X', 0, 0.3),
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
        mmpline = mmpline.rstrip()
        self.mmpline = mmpline
        fields = mmpline.split()
        self.key = string.atoi(fields[1])
        self.style = fields[6]
        self.hybridization = None
        self.group = None
        self.atomtype = lookupAtomType(string.atoi(fields[2][1:-1]))
        self.x = 0.001 * string.atoi(fields[3][1:-1])
        self.y = 0.001 * string.atoi(fields[4][:-1])
        self.z = 0.001 * string.atoi(fields[5][:-1])
        self.bonds = [ ]

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
        return A((self.x, self.y, self.z))
    def __repr__(self):
        r = "<%s %d (%g, %g, %g)" % \
               (self.atomtype.symbol, self.key, self.x, self.y, self.z)
        r += " %s" % self.style
        if self.hybridization != None:
            r += " %s" % self.hybridization
        if self.group != None:
            r += " (group %d)" % self.group
        if self.bonds:
            r += " ["
            for b in self.bonds:
                r += " " + repr(b)
            r += " ]"
        return r + ">"

class Group:
    def __init__(self):
        self.atoms = { }
        self.nextKey = 1

    def addAtom(self, a):
        a.key = key = self.nextKey
        self.nextKey += 1
        self.atoms[key] = a

    def transform(self, t):
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

    def assignSubgroups(self):
        self.inferBonds()
        remainingKeys = self.atoms.keys()
        while len(remainingKeys) > 0:
            groupKey = remainingKeys[0]
            print "Group", groupKey
            group = [ groupKey ]
            remainingKeys = remainingKeys[1:]
            style = self.atoms[groupKey].style
            self.atoms[groupKey].group = groupKey
            while True:
                growth = [ ]
                for key in group:
                    a = self.atoms[key]
                    for k2 in a.bonds:
                        if a.style == self.atoms[k2].style and k2 not in group and k2 not in growth:
                            growth.append(k2)
                            remainingKeys.remove(k2)
                            self.atoms[k2].group = groupKey
                if len(growth) == 0:
                    break
                group += growth

    def filter(self, filt):
        atomlist = filter(filt, self.atoms.values())
        # Renumber their keys, and recompute bonds with new keys
        self.atoms = { }
        self.nextKey = 1
        for i in range(len(atomlist)):
            self.addAtom(atomlist[i])
        self.inferBonds()

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
        atomlist.sort(lambda a1, a2: cmp(a1.group, a2.group))
        # Renumber their keys, and recompute bonds with new keys
        self.atoms = { }
        self.nextKey = 1
        for i in range(len(atomlist)):
            self.addAtom(atomlist[i])
        self.inferBonds()
        # write the file
        s = ""
        thisgroup = None
        for a in self.atoms.values():
            if groupname == None:
                if thisgroup != a.group:
                    s += "mol (Group %d) def\n" % a.group
                    thisgroup = a.group
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

def writeMmp(filename='groups.mmp', groupname=None, selectedGroup=None, theta=0.0, zdiff=0.0):

    g = Group()
    for L in open('strund1.mmp').readlines():
        if L.startswith("atom"):
            g.addAtom(Atom(L))
    g.assignSubgroups()

    """To include just one group in the MMP file, use selectedGroup to choose
    the groupKey. Otherwise you'll get the whole strand, with groups
    imported as distinct chunks.
    """
    if selectedGroup != None:
        g.filter(lambda atm,n=selectedGroup: atm.group == n)

    """To rotate these guys all into the same orientation, use these
    values...

    Group 1 -> crank = 0 -> theta = 0, zdiff = -20.2
    Group 9 -> crank = 1 -> theta = 30, zdiff = -20.2 + 1.67
    Group 41 -> crank = 2 -> theta = 60, zdiff = -20.2 + 1.67 + 5.76
    Group 74 -> crank = 3 -> theta = 90, zdiff = -20.2 + 2*1.67 + 5.76
    Group 104 -> crank = 3 -> theta = 90, zdiff = -20.2 + 2*1.67 + 2*5.76
    Group 136 -> crank = 3 -> theta = 90, zdiff = -20.2 + 3*1.67 + 2*5.76
    etc...
    """
    def tfm(x, y, z, c=cos(theta), s=sin(theta), zdiff=zdiff):
        return c * x + s * y, -s * x + c * y, z + zdiff
    g.transform(tfm)

    g.writeMmp(filename, groupname)

if True:
    theta = 0.0
    zdiff = -20.2
    for (i, groupkey, groupname, filename) in (
        (0, 1, 'cytosine', 'cytosine-inner.mmp'),
        (1, 9, 'guanine', 'guanine-outer.mmp'),
        #(2, 41, 'cytosine', 'cytosine-inner.mmp'),
        (3, 74, 'adenine', 'adenine-outer.mmp'),
        (4, 104, 'adenine', 'adenine-inner.mmp'),
        #(5, 136, 'adenine', 'adenine-outer.mmp'),
        (6, 168, 'thymine', 'thymine-inner.mmp'),
        (7, 200, 'thymine', 'thymine-outer.mmp'),
        #(8, 232, 'thymine', 'thymine-inner.mmp'),
        (9, 264, 'cytosine', 'cytosine-outer.mmp'),
        (10, 296, 'guanine', 'guanine-inner.mmp'),
        #(11, 326, 'cytosine', 'cytosine-outer.mmp')
        ):
        filename = 'experimental/zdna-bases/' + filename
        theta = i * (pi / 6)
        zdiff = -20.2 + int((i+1)/2) * 1.67 + int(i/2) * 5.76
        writeMmp(filename, groupname, groupkey, theta, zdiff)
else:
    writeMmp('groups.mmp')
