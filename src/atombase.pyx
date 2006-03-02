"""
$Id$

make atombase.so ; valgrind python atombasetests.py >& OUCH; less OUCH

"""

__author__ = "Will"

import types
import Numeric
from inval import InvalMixin

DEBUG = 0

cdef extern from "atombasehelp.c":

    cdef struct key_thing:
        int key
        void *self

    cdef struct link:
        link *next
        key_thing *other

    cdef struct atomstruct:
        int _eltnum, _atomtype
        double x, y, z
        link *sets

    cdef struct bondstruct:
        int v6
        link *sets

    cdef struct atomsetstruct:
        link *atoms

    cdef struct bondsetstruct:
        link *atoms

    link *has_link(link *n, unsigned int key)
    add_to_linked_list(link **head, key_thing *other)
    remove_from_linked_list(link **head, key_thing *other)
    extract_list(link *root, int values)
    linked_list_lookup(link *root, unsigned int key)

cdef class _BaseClass:
    cdef key_thing data0
    def __init__(self):
        self.data0.self = <void*> self

##############################################################
##############################################################
##############################################################
##############################################################

cdef class _AtomBase(_BaseClass):

    cdef atomstruct data

    def __init__(self):
        _BaseClass.__init__(self)
        self.data0.key = 0
        self.data._eltnum = 0
        self.data._atomtype = 0
        self.data.x = 0.0
        self.data.y = 0.0
        self.data.z = 0.0
        self.data.sets = NULL

    def diffableAttributes(self):
        return ("_eltnum", "_atomtype",
                "x", "y", "z", "sets")

    def __getattr__(self, name):
        if name == "key":
            return self.data0.key
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
            return extract_list(self.data.sets, 0)
        else:
            raise AttributeError, name

    def __setattr__(self, name, value):
        if name == "key":
            if DEBUG > 0: print "SET KEY", value
            self.data0.key = value
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

    def addSet(self, _BaseClass other):
        add_to_linked_list(&self.data.sets, &other.data0)

    def removeSet(self, _BaseClass other):
        remove_from_linked_list(&self.data.sets, &other.data0)

class AtomBase(_AtomBase):
    pass

##############################################################
##############################################################
##############################################################
##############################################################

cdef class _AtomSetBaseRefImpl(_BaseClass):

    cdef atomsetstruct data

    def __init__(self, atoms=[ ]):
        _BaseClass.__init__(self)
        self._dct = { }
        for a in atoms:
            self.add(a)
    def __setattr__(self, name, value):
        if name == "key":
            self.data0.key = value
        else:
            self.__dict__[name] = value
    def __getattr__(self, name):
        if name == "key":
            return self.data0.key
        elif name in ("_dct"):
            return self.__dict__[name]
        else:
            raise AttributeError, name
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

cdef class _AtomSetBase(_BaseClass):

    cdef atomsetstruct data

    def __init__(self, atomlst=[ ]):
        _BaseClass.__init__(self)
        self.data.atoms = NULL
        for a in atomlst:
            self.add(a)
    def __setattr__(self, name, value):
        if name == "key":
            self.data0.key = value
        else:
            self.__dict__[name] = value
    def __getattr__(self, name):
        if name == "key":
            return self.data0.key
        else:
            raise AttributeError, name
    def __setitem__(self, key, _AtomBase atom):
        if key != atom.key:
            raise KeyError
        add_to_linked_list(&self.data.atoms, &atom.data0)
        add_to_linked_list(&atom.data.sets, &self.data0)
    def __getitem__(self, key):
        return linked_list_lookup(self.data.atoms, key)
    def __delitem__(self, key):
        cdef key_thing adata0
        cdef atomstruct adata
        x = self[key]
        adata0 = (<_AtomBase> x).data0
        adata = (<_AtomBase> x).data
        remove_from_linked_list(&self.data.atoms, &adata0)
        remove_from_linked_list(&adata.sets, &self.data0)
    def __len__(self):
        return len(self.values())
    def keys(self):
        return extract_list(self.data.atoms, 0)
    def add(self, atom):
        self[atom.key] = atom
    def remove(self, atom):
        del self[atom.key]
    def update(self, other):
        for k in other.keys():
            self[k] = other[k]
    def values(self):
        return extract_list(self.data.atoms, 1)
    def items(self):
        lst = [ ]
        for k in self.keys():
            lst.append((k, self[k]))
        return lst
    def atomInfo(self):
        ar = Numeric.zeros((len(self), 5), 'd')
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

class AtomSetBase(_AtomSetBaseRefImpl):
    pass
#class AtomSetBase(_AtomSetBase):
#    pass

##############################################################
##############################################################
##############################################################
##############################################################

cdef class _BondBase(_BaseClass):

    cdef bondstruct data

    def __init__(self):
        _BaseClass.__init__(self)
        self.data0.key = 0
        self.data.v6 = 0
        self.data.sets = NULL

    def diffableAttributes(self):
        return ("v6",)

    def __getattr__(self, name):
        if name == "key":
            return self.data0.key
        elif name == "v6":
            return self.data.v6
        elif name == "sets":
            return extract_list(self.data.sets, 0)
        else:
            raise AttributeError, name

    def __setattr__(self, name, value):
        if name == "key":
            if DEBUG > 0: print "SET KEY", value
            self.data0.key = value
        elif name == "v6":
            self.data.v6 = value
        else:
            self.__dict__[name] = value

    def addSet(self, _BaseClass other):
        add_to_linked_list(&self.data.sets, &other.data0)

    def removeSet(self, _BaseClass other):
        remove_from_linked_list(&self.data.sets, &other.data0)

class BondBase(_BondBase):
    pass

##############################################################
##############################################################
##############################################################
##############################################################

cdef class _BondSetBase(_BaseClass):

    cdef bondsetstruct data

    def __init__(self, bonds=[ ]):
        _BaseClass.__init__(self)
        self._dct = { }
        for a in bonds:
            self.add(a)
    def __setattr__(self, name, value):
        if name == "key":
            self.data0.key = value
        else:
            self.__dict__[name] = value
    def __getattr__(self, name):
        if name == "key":
            return self.data0.key
        elif name in ("_dct"):
            return self.__dict__[name]
        else:
            raise AttributeError, name
    def __setitem__(self, key, bond):
        if key != bond.key:
            raise KeyError
        self._dct[key] = bond
        bond.addSet(self)
    def __getitem__(self, key):
        return self._dct[key]

    def __delitem__(self, key):
        self._dct[key].removeSet(self)
        del self._dct[key]
    def __len__(self):
        return len(self._dct.keys())
    def keys(self):
        return self._dct.keys()
    def add(self, bond):
        self[bond.key] = bond
    def remove(self, bond):
        del self[bond.key]
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
    def bondInfo(self):
        ary = Numeric.zeros((len(self.keys()), 3), 'i')
        i = 0
        for k in self.keys():
            bnd = self[k]
            ary[i][0] = bnd.atomkey1
            ary[i][1] = bnd.atomkey2
            ary[i][2] = bnd.v6
            i = i + 1
        return ary

class BondSetBase(_BondSetBase):
    pass

##############################################################
##############################################################
##############################################################
##############################################################

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
                    if type(value) == Numeric.arraytype: veq = value.tolist()
                    else: veq = value
                    if type(oldvalue) == Numeric.arraytype: oveq = oldvalue.tolist()
                    else: oveq = oldvalue
                    if veq != oveq:
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

##############################################################
##############################################################
##############################################################
##############################################################

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
