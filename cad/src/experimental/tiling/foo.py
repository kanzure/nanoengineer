#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""Arbitrary 2D surfaces in 3D space can be represented as:

    f(v) = 0

where f takes a 3D vector v and returns a scalar. For a
sphere, where f(x,y,z) = x**2 + y**2 + z**2 - R**2.

We would like to take these arbitrary surfaces and tile them with
graphene structures. The inputs to this process will be the function f
that defines the surface, and a starting point x0.
"""

import os
import random
import types

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def tuple(self):
        return (self.x, self.y, self.z)
    def __repr__(self):
        return ("<" +
                repr(self.x) + "," +
                repr(self.y) + "," +
                repr(self.z) + ">")
    def __abs__(self):
        return self.magsq() ** 0.5
    def magsq(self):
        return self.x**2 + self.y**2 + self.z**2
    def scale(self, k):
        return Vector(k * self.x, k * self.y, k * self.z)
    def normalize(self):
        return self.scale(1.0 / abs(self))
    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y, self.z + v.z)
    def __sub__(self, v):
        return self + (-v)
    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)
    def int(self):
        return Vector(int(self.x), int(self.y), int(self.z))
    def cross(self, v):
        return Vector(self.y * v.z - self.z * v.y,
                      self.z * v.x - self.x * v.z,
                      self.x * v.y - self.y * v.x)
    def gradient(self, f):
        h = 1.0e-10
        e = f(self)
        return Vector((f(self + Vector(h, 0, 0)) - e) / h,
                      (f(self + Vector(0, h, 0)) - e) / h,
                      (f(self + Vector(0, 0, h)) - e) / h)




def randvec():
    # return a random vector of length one
    while True:
        vec = Vector(2 * random.random() - 1,
                     2 * random.random() - 1,
                     2 * random.random() - 1)
        if vec.magsq() > 0.001:
            return vec.normalize()

def minimize(f, v, g=None, debug=False):
    """If g is not None, then it represents a direction, starting at v,
    along which we seek a minimum value for f.

    If g is None, then we are starting at v and trying to find a local
    minimum for f, regardless of direction.

    Some of the instances where we're using this, we should maybe use
    Newton's method instead."""
    localMin = (g == None)
    if localMin:
        if debug: print "finding local minimum"
        g = -v.gradient(f)
    else:
        if debug: print "1D minimize"
    x = f(v)
    p = 3.0
    s = 0.0
    evals = 1
    while p > 1.0e-15:
        for j in range(-10,10):
            ds = p * j
            if s + ds >= 0.0:
                v1 = v + g.scale(s + ds)
                y = f(v1)
                evals += 1
                if y < x:
                    s += ds
                    if debug: print "new good s", s, y
                    x = y
                    if localMin:
                        v = v + g.scale(s)
                        g = -v.gradient(f)
        p *= 0.7
    if debug: print evals, "evals"
    if localMin:
        return v
    else:
        return v + g.scale(s)

def newtonsMethodStep(f, v):
    x = f(v)
    g = v.gradient(f)
    return v - g.scale(x / g.magsq())

def nearbyPoint(f, v):
    """Given a point xi which is pretty close to the surface defined
    by f, find a nearby point which lies right on the surface (within
    the limits of floating-point imprecision) where f is zero
    """
    #def f2(x):
    #    return f(x) ** 2
    #return minimize(f2, v, -v.gradient(f))
    for i in range(10):
        v = newtonsMethodStep(f, v)
    return v

######################

def makeRing(f, x0, side=1.42):
    def distances(ptlst, v):
        flst = [ f ]
        for pt, dist in ptlst:
            def dist(v, pt=pt, distsq=dist**2):
                return (v - pt).magsq() - distsq
            flst.append(dist)
        for i in range(1000):
            for f1 in flst:
                v = newtonsMethodStep(f1, v)
        return v
    def extendRing(p1, p2, p3=None):
        lst = [ (p1, side), (p2, (3**.5) * side) ]
        if p3 != None:
            lst.append((p3, 2 * side))
        px = p1 + randvec()
        px = distances(lst, px)
        return px
    x0 = nearbyPoint(f, x0)
    x1 = x0 + randvec()
    x1 = distances([ (x0, side) ], x1)
    x2 = extendRing(x0, x1)
    x3 = extendRing(x1, x0, x2)
    print f(x1), abs(x0 - x1)
    print f(x2), abs(x2 - x0), abs(x2 - x1)
    print f(x3), abs(x3 - x0), abs(x3 - x1)
    x4 = extendRing(x2, x0, x1)
    x5 = extendRing(x3, x1, x0)
    print f(x4), abs(x4 - x0), abs(x4 - x3)
    print f(x5), abs(x5 - x1), abs(x5 - x2)
    print abs(x5 - x4) / side

######################

class Atom:
    def __init__(self, pos):
        self.index = -1
        self.pos = pos
        self.bonds = [ ]
    def __repr__(self):
        return "<Atom %d %f %f %f>" % \
               (self.index, self.pos.x, self.pos.y, self.pos.z)
    def mmp(self):
        r = "atom %d (6) (%d, %d, %d) def\n" % \
            (self.index + 1,
             int(1000 * self.pos.x),
             int(1000 * self.pos.y),
             int(1000 * self.pos.z))
        numBonds = 0
        bonds = "bondg"
        for atm2 in self.bonds:
            if atm2.index < self.index:
                bonds += " " + repr(atm2.index+1)
                numBonds += 1
        bonds += "\n"
        if numBonds > 3:
            return ""
        elif numBonds > 0:
            r += bonds
        return r

BONDLEN = 1.42
TOOCLOSE = 0.8 * BONDLEN
TOODISTANT = 1.1 * BONDLEN

def bucketKey(pos):
    return (int(pos.x / BONDLEN),
            int(pos.y / BONDLEN),
            int(pos.z / BONDLEN))

class Buckets:
    def __init__(self, alst=[ ]):
        self.buckets = { }
        for a in alst:
            self.add(a)
    def add(self, atm):
        key = bucketKey(atm.pos)
        try:
            self.buckets[key].append(atm)
        except KeyError:
            self.buckets[key] = [ atm ]
    def remove(self, atm):
        key = bucketKey(atm.pos)
        try:
            self.buckets[key].remove(atm)
        except KeyError:
            pass
    def neighborhood(self, pos):
        ipos = pos.scale(1. / BONDLEN).int()
        lst = [ ]
        for xdiff in range(-1, 2):
            for ydiff in range(-1, 2):
                for zdiff in range(-1, 2):
                    diff = Vector(xdiff, ydiff, zdiff)
                    key = (ipos + diff).tuple()
                    if self.buckets.has_key(key):
                        lst2 = self.buckets[key]
                        for atm2 in lst2:
                            lst.append(atm2)
        return lst
    def findClosestAtom(self, pos, ignoreIdentical=True):
        closest = None
        smallestDistance = 1.0e20
        for atm in self.neighborhood(pos):
            dist = abs(atm.pos - pos)
            if dist < smallestDistance:
                if not ignoreIdentical or dist > 0.00001:
                    smallestDistance = dist
                    closest = atm
        return closest

class Tiling:
    def __init__(self):
        self.atoms = [ ]
        self.buckets = Buckets()
    def start(self, f, x0, x1=None):
        x0 = nearbyPoint(f, x0)
        if x1 == None:
            x1 = x0 + randvec()
        def dist(v, pt=x0, distsq=BONDLEN**2):
            return (v - pt).magsq() - distsq
        for i in range(10):
            x1 = newtonsMethodStep(f, x1)
            x1 = newtonsMethodStep(dist, x1)
        tiling.add(Atom(x0))
        tiling.add(Atom(x1))
        self.inferBonds()
    def moveAtom(self, atm, newpos):
        print "moveAtom"
        key1 = bucketKey(atm.pos)
        key2 = bucketKey(newpos)
        self.buckets.remove(atm)
        atm.pos = newpos
        self.buckets.add(atm)
    def __neighborhood(self, pos):
        ipos = apply(Vector, bucketKey(pos))
        lst = [ ]
        for xdiff in range(-1, 2):
            for ydiff in range(-1, 2):
                for zdiff in range(-1, 2):
                    diff = Vector(xdiff, ydiff, zdiff)
                    key = (ipos + diff).tuple()
                    if self.buckets.has_key(key):
                        lst2 = self.buckets[key]
                        for atm2 in lst2:
                            lst.append(atm2)
        return lst
    def grow(self, f):
        while self.growLayer(f) > 0:
            print "layer"
        #for i in range(9):
        #    self.growLayer(f)
        #    print "layer"
    def growLayer(self, f):
        self.inferBonds()
        def growAtom(f, atm):
            def dist(v, pt=atm.pos, distsq=BONDLEN**2):
                return (v - pt).magsq() - distsq
            if len(atm.bonds) == 0:
                print "no bonds " + repr(a)
                return [ ]
            elif len(atm.bonds) == 1:
                g = atm.pos.gradient(f)
                u = (atm.pos - atm.bonds[0].pos).normalize()
                v = u.cross(g.normalize())
                A = BONDLEN * (3**.5)/2
                B = BONDLEN * 0.5
                x2 = atm.pos + v.scale(A) + u.scale(B)
                x3 = atm.pos - v.scale(A) + u.scale(B)
                for i in range(10):
                    x2 = newtonsMethodStep(f, x2)
                    x2 = newtonsMethodStep(dist, x2)
                    x3 = newtonsMethodStep(f, x3)
                    x3 = newtonsMethodStep(dist, x3)
                x2, x3 = Atom(x2), Atom(x3)
                return [ x2, x3 ]
            elif len(atm.bonds) == 2:
                u = atm.pos - atm.bonds[0].pos
                v = atm.pos - atm.bonds[1].pos
                x2 = u + v
                for i in range(10):
                    x2 = newtonsMethodStep(f, x2)
                    x2 = newtonsMethodStep(dist, x2)
                x2 = Atom(x2)
                return [ x2 ]
            else:
                return [ ]
        oldsize = len(self.atoms)
        newatoms = [ ]
        for a in self.atoms:
            newatoms += growAtom(f, a)
        # first eliminate redundancies in the new layer itself
        i = 0
        while i < len(newatoms):
            b = Buckets(newatoms)
            atm = newatoms[i]
            atm2 = b.findClosestAtom(atm.pos)
            if atm2 != None and abs(atm.pos - atm2.pos) < TOOCLOSE:
                newpos = (atm.pos + atm2.pos).scale(0.5)
                newatoms.remove(atm)
                atm2.pos = newpos
            else:
                i = i + 1
        # next eliminate any redundancies with atoms already in the structure
        for atm in newatoms:
            atm2 = self.buckets.findClosestAtom(atm.pos)
            if abs(atm.pos - atm2.pos) < TOOCLOSE:
                newatoms.remove(atm)
                self.moveAtom(atm2, (atm.pos + atm2.pos).scale(0.5))
        for a in newatoms:
            self.add(a)
        return len(self.atoms) - oldsize
    def add(self, atm):
        print 'add', atm
        self.atoms.append(atm)
        self.buckets.add(atm)
    def remove(self, atm):
        print 'remove', atm
        self.atoms.remove(atm)
        self.buckets.remove(atm)
    def closestAtom(self, pos):
        return self.buckets.findClosestAtom(pos)
    def inferBondsForAtom(self, atm):
        def closeEnough(atm1, atm2):
            return abs(atm1.pos - atm2.pos) < 2
        nbhd = self.buckets.neighborhood(atm.pos)
        for atm2 in nbhd:
            if atm2 != atm and atm2 not in atm.bonds and \
               0.8 * BONDLEN < abs(atm.pos - atm2.pos) < 1.2 * BONDLEN:
                atm.bonds.append(atm2)
    def inferBonds(self):
        for atm in self.atoms:
            self.inferBondsForAtom(atm)
    def writeMmp(self, filename):
        self.inferBonds()
        for i in range(len(self.atoms)):
            self.atoms[i].index = i
        mmpfile = """mmpformat 050920 required; 051103 preferred
kelvin 300
group (View Data)
info opengroup open = True
csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)
csys (LastView) (1.000000, 0.000000, 0.000000, 0.000000) (10.943023) (0.000000, 0.000000, 0.000000) (1.000000)
egroup (View Data)
group (Nanotube)
info opengroup open = True
mol (Nanotube-1) def
"""
        for a in self.atoms:
            mmpfile += a.mmp()
        mmpfile += """egroup (Nanotube)
group (Clipboard)
info opengroup open = False
egroup (Clipboard)
end molecular machine part 1
"""
        open(filename, "w").write(mmpfile)

####################

# makeRing(f, x0)

def growAtom(f, atm):
    def dist(v, pt=atm.pos, distsq=BONDLEN**2):
        return (v - pt).magsq() - distsq
    if len(atm.bonds) == 0:
        raise Exception("no bonds")
    elif len(atm.bonds) == 1:
        g = atm.pos.gradient(f)
        u = (atm.pos - atm.bonds[0].pos).normalize()
        v = u.cross(g.normalize())
        A = BONDLEN * (3**.5)/2
        B = BONDLEN * 0.5
        x2 = atm.pos + v.scale(A) + u.scale(B)
        x3 = atm.pos - v.scale(A) + u.scale(B)
        for i in range(10):
            x2 = newtonsMethodStep(f, x2)
            x2 = newtonsMethodStep(dist, x2)
            x3 = newtonsMethodStep(f, x3)
            x3 = newtonsMethodStep(dist, x3)
        x2, x3 = Atom(x2), Atom(x3)
        return [ x2, x3 ]
    elif len(atm.bonds) == 2:
        u = atm.pos - atm.bonds[0].pos
        v = atm.pos - atm.bonds[1].pos
        x2 = u + v
        for i in range(10):
            x2 = newtonsMethodStep(f, x2)
            x2 = newtonsMethodStep(dist, x2)
        x2 = Atom(x2)
        return [ x2 ]
    else:
        return [ ]

# def joinY

def firstTwo(mmpf, f, x0, x1=None):
    x0 = nearbyPoint(f, x0)
    if x1 == None:
        x1 = x0 + randvec()
    def dist(v, pt=x0, distsq=BONDLEN**2):
        return (v - pt).magsq() - distsq
    for i in range(10):
        x1 = newtonsMethodStep(f, x1)
        x1 = newtonsMethodStep(dist, x1)
    x0, x1 = Atom(x0), Atom(x1)
    return [ x0, x1 ]

###################################

def bevelMax(x, y, C=1.0):
    if y - x < -C: return x
    elif y - x > C: return y
    else: return x + (1/(4.*C)) * (y - x + C)**2

def f(v):
    f1 = v.x**2 + v.y**2 + (3 * v.z)**2 - 10.0**2
    f2 = (v.x-50)**2 + v.y**2 + v.z**2 - 50.0**2
    #return bevelMax(f1, f2)
    return max(f1, f2)

tiling = Tiling()
tiling.start(f, randvec())
tiling.grow(f)
tiling.writeMmp('/tmp/nt.mmp')
# os.system("/home/wware/polosims/cad/src/atom.py /tmp/nt.mmp")
