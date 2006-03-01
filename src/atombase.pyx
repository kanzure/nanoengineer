"""
$Id$
"""

__author__ = "Will"

import types
import Numeric
from inval import InvalMixin

DEBUG = 0

#cdef extern from "atombasehelp.c":
#    cdef struct atom:
#        int _eltnum, _atomtype
#        double x, y, z
#        linked_list sets

class Holder:
    """\
    At some point this will become a C struct, one for each usage.
    So AtomBase's C struct will have sets, _eltnum, _atomtype,
    x, y, and z.
    """
    pass

cdef class _AtomBase:

    def __init__(self):
        self.data = Holder()
        self.data.key = 0
        self.data._eltnum = 0
        self.data._atomtype = 0
        self.data.x = 0.0
        self.data.y = 0.0
        self.data.z = 0.0
        self.data.sets = [ ]

    def diffableAttributes(self):
        return ("_eltnum", "_atomtype",
                "x", "y", "z", "sets")

    def __getattr__(self, name):
        if name == "key":
            return self.data.key
        elif name == "_eltnum":
            return self.data._eltnum
        elif name == "_atomtype":
            return self.data._atomtype
        elif name == "x":
            return self.data.x
        elif name == "y":
            return self.data.y
        elif name == "z":
            return self.data.z
        elif name == "sets":
            b = [ ]
            for x in self.data.sets:
                b.append(x.key)
            b.sort()
            return b
        else:
            raise AttributeError, name

    def __setattr__(self, name, value):
        if name == "key":
            if DEBUG > 0: print "SET KEY", value
            self.data.key = value
        elif name == "_eltnum":
            self.data._eltnum = value
        elif name == "_atomtype":
            self.data._atomtype = value
        elif name == "x":
            self.data.x = value
        elif name == "y":
            self.data.y = value
        elif name == "z":
            self.data.z = value
        else:
            self.__dict__[name] = value

    def addSet(self, other):
        self.data.sets.append(other)
    def removeSet(self, set):
        b = [ ]
        for x in self.data.sets:
            if x != set:
                b.append(x)
        self.data.sets = b

class AtomBase(_AtomBase):
    pass

cdef class _AtomSetBase:
    def __init__(self, atoms=[ ]):
        self._dct = { }
        for a in atoms:
            self.add(a)
    def __setitem__(self, key, atom):
        if key != atom.key:
            raise KeyError
        self._dct[key] = atom
        atom.addSet(self)
    def __getitem__(self, key):
        return self._dct[key]
    def __delitem__(self, key):
        self._dct[key].removeSet(self)
        del self._dct[key]
    def __len__(self):
        return len(self._dct.keys())
    def keys(self):
        return self._dct.keys()
    def add(self, atom):
        self[atom.key] = atom
    def remove(self, atom):
        del self[atom.key]
    def update(self, other):
        for k in other.keys():
            self[k] = other[k]
    def values(self):
        lst = [ ]
        for k in self.keys():
            lst.append(self[k])
        return lst
    def items(self):
        lst = [ ]
        for k in self.keys():
            lst.append((k, self[k]))
        return lst
    def atomInfo(self):
        ar = Numeric.zeros((len(self.keys()), 5), 'd')
        i = 0
        for k in self.keys():
            atm = self[k]
            ar[i][0] = atm._eltnum
            ar[i][1] = atm._atomtype
            ar[i][2] = atm.x
            ar[i][3] = atm.y
            ar[i][4] = atm.z
            i = i + 1
        return ar

class AtomSetBase(_AtomSetBase):
    pass

cdef class _DiffObjectBase:
    def __init__(self, attributes, objlist, previous, current):
        for attr in attributes:
            keylist = [ ]
            oldlist = [ ]
            newlist = [ ]
            for x in objlist:
                if attr in x.diffableAttributes():
                    value = current[(attr, x.key)]
                    oldvalue = previous[(attr, x.key)]
                    if value != oldvalue:
                        keylist.append(x.key)
                        oldlist.append(oldvalue)
                        newlist.append(value)
            if len(newlist) > 0 and \
               type(newlist[0]) in (types.IntType, types.FloatType):
                # we can pack these guys efficiently
                setattr(self, attr, (Numeric.array(keylist),
                                     Numeric.array(oldlist),
                                     Numeric.array(newlist)))
            else:
                # these guys can't be packed efficiently
                setattr(self, attr, (Numeric.array(keylist),
                                     oldlist,
                                     newlist))

class DiffObjectBase(_DiffObjectBase):
    pass

cdef class _DiffFactoryBase:
    def __init__(self, objList):
        self.attrs = [ ]
        for x in objList:
            for attr in x.diffableAttributes():
                if attr not in self.attrs:
                    self.attrs.append(attr)
        self.lst = objList
        self.current = None
        self.snapshot()
    def _getCurrentAttributes(self, x):
        for attr in x.diffableAttributes():
            self.current[(attr, x.key)] = getattr(x, attr)
    def addObject(self, x):
        self.lst.append(x)
        self._getCurrentAttributes(x)
    def snapshot(self):
        previous = self.current
        self.current = { }
        for x in self.lst:
            self._getCurrentAttributes(x)
        if previous != None:
            return DiffObjectBase(self.attrs, self.lst,
                                  previous, self.current)

class DiffFactoryBase(_DiffFactoryBase):
    pass
