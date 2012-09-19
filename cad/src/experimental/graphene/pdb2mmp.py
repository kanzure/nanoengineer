# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""Convert CoNTub's PDB output to an MMP file

Typical usage:
    python pdb2mmp.py < hetero.pdb > hetero.mmp
"""

import sys, string

class Atom:
    def __init__(self, index, elem, xyz):
        self.index = index
        self.elem = elem
        self.xyz = xyz
        self.bonds = [ ]
    def __repr__(self):
        def s(x):
            # convert distances to int picometers
            return int(1000.0 * x)
        r = ('atom %d (%d) (%d, %d, %d) def' %
             (self.index, self.elem,
              s(self.xyz[0]), s(self.xyz[1]), s(self.xyz[2])))
        if self.bonds:
            r += '\nbondg'
            for y in self.bonds:
                r += ' %d' % y
        return r

atoms = { }
bonds = [ ]

for L in sys.stdin.readlines():
    L = L.rstrip().upper()
    #print L
    fields = L.split()
    if fields[0] == 'HETATM':
        index = string.atoi(fields[1])
        elem = {'C': 6, 'H': 1, 'N': 7}[fields[2]]
        xyz = map(string.atof, fields[-3:])
        atoms[index] = Atom(index, elem, xyz)
    elif fields[0] == 'CONECT':
        fields = map(string.atoi, fields[1:])
        x = fields[0]
        for y in fields[1:]:
            if y < x:
                bonds.append((x, y))

for x, y in bonds:
    atoms[x].bonds.append(y)

r = '''mmpformat 050920 required; 051103 preferred
kelvin 300
group (View Data)
info opengroup open = True
csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)
csys (LastView) (1.000000, 0.000000, 0.000000, 0.000000) (10.943023) (0.000000, 0.000000, 0.000000) (1.000000)
egroup (View Data)
group (Heterojunction)
info opengroup open = True
mol (Heterojunction-1) def
'''

for index in atoms:
    r += repr(atoms[index]) + '\n'

r += '''egroup (Heterojunction)
end1
group (Clipboard)
info opengroup open = False
egroup (Clipboard)
end molecular machine part 1881'''

print r
