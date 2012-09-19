# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
'''
buckyball.py -- Buckyball generator, for putting endcaps on nanotubes

The order of a buckyball is how many hexagons go between the
pentagons. This code fails for order 6 and higher, something in the
edges() method.

Orders 3 and 4 look like this:
http://www.geocities.com/geodesicsnz/3viy.jpg
http://www.geocities.com/geodesicsnz/4viy-01.jpg

Diameters for different orders:
1 - 3.9 Angstroms
2 - 8.0 A
3 - 12.8 A
4 - 17.7 A
5 - 23.5 A

The geometry for a buckyball works like this. Each carbon lies in the
center of a triangle. Vectors of unit length are used to represent
the vertices of the triangles. Edges are the connections between
adjacent vectors; three contiguous edges define a triangle. The
positions of carbon atoms are taken by getting a vector for the center
of the triangle, and scaling it to make the bond lengths work. Once
you have vectors for all the carbons, you can get bonds. Each bond
crosses an edge, so edges are given two atom indices for the bond
crossing them.

There is a sequence of data structures with interdependencies, so an
invalidation idiom is used to decide when any one of them should be
recomputed. The dependencies (as of this writing) are: _edges ->
_triangles -> _carbons -> _bonds.

$Id$
'''
__author__ = "Will"

from math import sin, cos, pi, floor
from geometry.VQT import V, vlen
from geometry.NeighborhoodGenerator import NeighborhoodGenerator
from model.bonds import bond_atoms, CC_GRAPHITIC_BONDLENGTH
from model.bond_constants import V_GRAPHITE
from model.chem import Atom

class BuckyBall:

    class Edge:
        def __init__(self, i, j):
            assert i != j
            if i > j: i, j = j, i
            self.i, self.j = i, j
            self.atom1 = None
            self.atom2 = None
        def ij(self):  # ascending order
            return (self.i, self.j)
        def ji(self):  # descending order
            return (self.j, self.i)
        def add_atom(self, a):
            # a is an int, an index into the list returned by
            # BuckyBall.carbons()
            if self.atom1 == None:
                self.atom1 = a
            elif self.atom2 == None:
                self.atom2 = a
            else:
                assert False, 'more than two atoms for an edge??'
        def atoms(self):
            a1, a2 = self.atom1, self.atom2
            assert a1 != None and a2 != None
            if a1 > a2: a1, a2 = a2, a1
            # a1 and a2 are ints, indices into the list returned by
            # BuckyBall.carbons()
            return (a1, a2)

    class EdgeList:
        def __init__(self):
            self.lst = [ ]
            self.dct = { }
        def append(self, edge):
            dct = self.dct
            i, j = edge.ij()
            self.lst.append(edge)
            if not dct.has_key(i):
                dct[i] = [ ]
            if not dct.has_key(j):
                dct[j] = [ ]
            dct[i].append((edge, j))
            dct[j].append((edge, i))
        def adjoining(self, i):
            lst = [ ]
            for e, j in self.dct[i]:
                lst.append(j)
            return lst
        def edgeFor(self, i, j):
            for e, j1 in self.dct[i]:
                if j == j1:
                    return e
            assert False, 'edge not found'
        def __iter__(self):
            return self.lst.__iter__()
        def anyOldBond(self):
            return self.lst[0].atoms()
        def bondlist(self):
            lst = [ ]
            for i in self.dct.keys():
                for e, j in self.dct[i]:
                    if j > i:
                        lst.append(e.atoms())
            return lst
        def mmpBonds(self):
            dct = { }
            for i in self.dct.keys():
                for e, j in self.dct[i]:
                    if j > i:
                        a1, a2 = e.atoms()
                        if not dct.has_key(a2):
                            dct[a2] = [ ]
                        if a1+1 not in dct[a2]:
                            dct[a2].append(a1+1)
            return dct

    def __init__(self, bondlength=CC_GRAPHITIC_BONDLENGTH, order=1):
        assert order <= 5, 'edges algorithm fails for order > 5'
        lst = [ ]
        a = 0.8 ** 0.5
        b = 0.2 ** 0.5
        lst.append(V(0.0, 0.0, 1.0))
        lst.append(V(0.0, 0.0, -1.0))
        for i in range(10):
            t = i * pi * 36 / 180
            bb = (i & 1) and -b or b
            lst.append(V(a * cos(t), a * sin(t), bb))
        self.lst = lst
        self.order = 1
        self._invalidate_all()
        if order > 1:
            self._subtriangulate(order)
            self._invalidate_all()
        self.bondlength = bondlength

    def _invalidate_all(self):
        self._edges = None
        self._triangles = None
        self._carbons = None
        self._bonds = None
        self._bondlist = None

    def edges(self):
        if self._edges == None:
            minLength = 1.0e20
            for i in range(len(self.lst)):
                u = self.lst[i]
                for j in range(i+1, len(self.lst)):
                    d = vlen(self.lst[j] - u)
                    if d < minLength:
                        minLength = d
            maxLength = 1.5 * minLength
            _edges = self.EdgeList()
            for i in range(len(self.lst)):
                u = self.lst[i]
                for j in range(i+1, len(self.lst)):
                    d = vlen(self.lst[j] - u)
                    if d < maxLength:
                        _edges.append(self.Edge(i, j))
            self._edges = _edges
            # invalidate _triangles
            self._triangles = None
        return self._edges

    def triangles(self):
        if self._triangles == None:
            edges = self.edges()
            tlst = [ ]
            n = len(self.lst)
            for e in edges:
                i, j = e.ij()
                ei = edges.adjoining(i)
                ej = edges.adjoining(j)
                for x in ei:
                    if x in ej:
                        tri = [i, j, x]
                        tri.sort()
                        tri = tuple(tri)
                        if tri not in tlst:
                            tlst.append(tri)
            self._triangles = tlst
            # invalidate _carbons
            self._carbons = None
        return self._triangles

    def carbons(self):
        if self._carbons == None:
            edges = self.edges()
            lst = [ ]
            carbonIndex = 0
            for tri in self.triangles():
                a, b, c = tri
                ab = edges.edgeFor(a, b)
                ab.add_atom(carbonIndex)
                ac = edges.edgeFor(a, c)
                ac.add_atom(carbonIndex)
                bc = edges.edgeFor(b, c)
                bc.add_atom(carbonIndex)
                v0, v1, v2 = self.lst[a], self.lst[b], self.lst[c]
                v = (v0 + v1 + v2) / 3.0
                lst.append(v)
                carbonIndex += 1
            # get a bond length
            a1, a2 = edges.anyOldBond()
            bondlen = vlen(lst[a1] - lst[a2])
            # scale to get the correct bond length
            factor = self.bondlength / bondlen
            for i in range(len(lst)):
                lst[i] = factor * lst[i]
            self._carbons = lst
            # invalidate _bonds
            self._bonds = None
        return self._carbons

    def radius(self):
        carbons = self.carbons()
        assert len(carbons) > 0
        totaldist = 0.0
        n = 0
        # just averge the first ten (or fewer)
        for c in carbons[:10]:
            totaldist += vlen(c)
            n += 1
        return totaldist / n

    def mmpBonds(self):
        if self._bonds == None:
            # bonds are perpendicular to edges
            self._bonds = self.edges().mmpBonds()
        return self._bonds

    def bondlist(self):
        if self._bondlist == None:
            # bonds are perpendicular to edges
            self._bondlist = self.edges().bondlist()
        return self._bondlist

    def _subtriangulate(self, n):
        # don't put new vectors right on top of old ones
        # this is similar to the neighborhood generator
        gap = 0.001
        occupied = { }
        def quantize(v):
            return (int(floor(v[0] / gap)),
                    int(floor(v[1] / gap)),
                    int(floor(v[2] / gap)))
        def overlap(v):
            x0, y0, z0 = quantize(v)
            for x in range(x0 - 1, x0 + 2):
                for y in range(y0 - 1, y0 + 2):
                    for z in range(z0 - 1, z0 + 2):
                        key = (x, y, z)
                        if occupied.has_key(key):
                            return True
            return False
        def occupy(v):
            key = quantize(v)
            occupied[key] = 1
        def add_if_ok(v):
            if not overlap(v):
                occupy(v)
                self.lst.append(v)
        for v in self.lst:
            occupy(v)
        for tri in self.triangles():
            v0, v1, v2 = self.lst[tri[0]], self.lst[tri[1]], self.lst[tri[2]]
            v10, v21 = v1 - v0, v2 - v1
            for i in range(n + 1):
                for j in range(i + 1):
                    v = v21 * (1. * j / n) + v10 * (1. * i / n) + v0
                    add_if_ok(v / vlen(v))
        self.order *= n

    def add_to_mol(self, mol):
        maxradius = 1.5 * self.bondlength
        positions = self.carbons()
        atoms = [ ]
        for newpos in positions:
            newguy = Atom('C', newpos, mol)
            atoms.append(newguy)
            newguy.set_atomtype('sp2')
        ngen = NeighborhoodGenerator(atoms, maxradius)
        for atm1 in atoms:
            p1 = atm1.posn()
            for atm2 in ngen.region(p1):
                if atm2.key < atm1.key:
                    bond_atoms(atm1, atm2, V_GRAPHITE)
        # clean up singlets
        for atm in atoms:
            for s in atm.singNeighbors():
                s.kill()
            atm.make_enough_bondpoints()

#############################

if __name__ == '__main__':
    mmp_header = '''mmpformat 050920 required; 060421 preferred
kelvin 300
group (View Data)
info opengroup open = True
csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)
csys (LastView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)
egroup (View Data)
group (Buckyball)
info opengroup open = True
mol (Buckyball) def
'''

    mmp_footer = '''egroup (Buckyball)
end1
group (Clipboard)
info opengroup open = False
egroup (Clipboard)
end molecular machine part gp
'''

    def writemmp(bball, filename):
        outf = open(filename, 'w')
        outf.write(mmp_header)
        carbons = bball.carbons()
        mmpbonds = bball.mmpBonds()
        for i in range(len(carbons)):
            x, y, z = carbons[i]
            outf.write('atom %d (6) (%d, %d, %d) def\n' %
                       (i + 1, int(1000 * x), int(1000 * y), int(1000 * z)))
            outf.write('info atom atomtype = sp2\n')
            if mmpbonds.has_key(i) and len(mmpbonds[i]) > 0:
                outf.write('bondg ' + ', '.join(map(str, mmpbonds[i])) + '\n')
        outf.write(mmp_footer)
        outf.close()

    for i in range(1, 6):
        b = BuckyBall(i)
        writemmp(b, 'buckyball-%d.mmp' % i)
