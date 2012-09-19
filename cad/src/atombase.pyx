# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$

make atombase.so ; valgrind python atombasetests.py >& OUCH; less OUCH

"""

__author__ = "Will"

import types
import numpy.oldnumeric
from foundation.inval import InvalMixin

cdef extern from "atombasehelp.c":

    cdef struct key_thing:
        int key
        void *self

    cdef struct pointerlist:
        int size
        int arraysize
        void **lst

    cdef struct xyz:
        double x, y, z

    cdef struct atomstruct:
        int key
        void *self
        int _eltnum, _atomtype
        xyz _posn
        pointerlist *sets

    cdef struct bondstruct:
        int key
        void *self
        int v6
        pointerlist *sets

    cdef struct setstruct:
        int key
        void *self
        pointerlist *members

    pointerlist *new_pointerlist()
    pointerlist *has_key(pointerlist *n, unsigned int key)
    add_to_pointerlist(pointerlist *head, key_thing *other)
    remove_from_pointerlist(pointerlist *head, unsigned int otherkey)
    extract_list(pointerlist *root, int values)
    free_list(pointerlist *root)
    pointerlist_lookup(pointerlist *root, unsigned int key)
    int _init_bitmap_font()

cdef extern from "Numeric/arrayobject.h":
    struct PyArray_Descr:
        int type_um, elsize
        char type
    ctypedef class Numeric.ArrayType [object PyArrayObject]:
        cdef char *data
        cdef int nd
        cdef int *dimensions, *strides
        cdef object base
        cdef PyArray_Descr *descr
        cdef int flags

cdef extern from "string.h":
    int strcmp(char *s1, char *s2)

# this is a handy diagnostic for printing addresses of things
cdef addr(void *p):
    pl = long(<int> p)
    if pl < 0:
        return '%x' % (pl + (long(1) << 32))
    else:
        return '%x' % pl

##############################################################
##############################################################
##############################################################
##############################################################

cdef class _BaseItem:
    # this is polymorphic to _AtomBase and _BondBase
    cdef key_thing data

##############################################################
##############################################################
##############################################################
##############################################################

cdef class _BaseDictClass:

    cdef setstruct data

    # Define __setitem__ and __delitem__ for the kind of item in the set

    def __init__(self):
        self.data.key = 0
        self.data.self = <void*> self
        self.data.members = new_pointerlist()
    def __setattr__(self, name, value):
        if name == "key":
            self.data.key = value
        else:
            self.__dict__[name] = value
    def __getattr__(self, char *name):
        if strcmp(name, "key") == 0:
            return self.data.key
        else:
            raise AttributeError, name
    def __getitem__(self, key):
        return pointerlist_lookup(self.data.members, key)
    def __len__(self):
        return len(self.values())
    def __contains__(self, unsigned int key):
        try:
            pointerlist_lookup(self.data.members, key)
            return 1
        except KeyError:
            return 0
    def has_key(self, unsigned int key):
        return self.__contains__(key)
    def clear(self):
        for k in self.keys():
            self.remove(self[k])
    def keys(self):
        return extract_list(self.data.members, 0)
    def add(self, guy):
        assert guy.key != 0
        self[guy.key] = guy
    def remove(self, guy):
        del self[guy.key]
    def update(self, other):
        for k in other.keys():
            self[k] = other[k]
    def values(self):
        return extract_list(self.data.members, 1)
    def items(self):
        lst = [ ]
        for k in self.keys():
            lst.append((k, self[k]))
        return lst

##############################################################
##############################################################
##############################################################
##############################################################

cdef class _AtomBase:

    cdef atomstruct data

    def __init__(self):
        self.data.key = 0
        self.data.self = <void*> self
        self.data._eltnum = 0
        self.data._posn.x = 0.0
        self.data._posn.y = 0.0
        self.data._posn.z = 0.0
        self.data._atomtype = 0
        self.data.sets = new_pointerlist()

    def diffableAttributes(self):
        return ("_eltnum", "_atomtype",
                "_posn", "sets")

    def __getattr__(self, char *name):
        if strcmp(name, "key") == 0:
            return self.data.key
        elif strcmp(name, "_eltnum") == 0:
            return self.data._eltnum
        elif strcmp(name, "_atomtype") == 0:
            return self.data._atomtype
        elif strcmp(name, "_posn") == 0:
            return Numeric.array((self.data._posn.x,
                                  self.data._posn.y,
                                  self.data._posn.z))
        elif strcmp(name, "x") == 0:
            return self.data._posn.x
        elif strcmp(name, "y") == 0:
            return self.data._posn.y
        elif strcmp(name, "z") == 0:
            return self.data._posn.z
        elif strcmp(name, "sets") == 0:
            return extract_list(self.data.sets, 0)
        else:
            raise AttributeError, name

    def _setposn(self, ArrayType ary):
        if chr(ary.descr.type) != "d" or ary.nd != 1 or ary.dimensions[0] != 3:
            raise TypeError("Array of three doubles required")
        self.data._posn.x = (<double *> ary.data)[0]
        self.data._posn.y = (<double *> ary.data)[1]
        self.data._posn.z = (<double *> ary.data)[2]

    def __setattr__(self, char *name, value):
        if strcmp(name, "key") == 0:
            self.data.key = value
        elif strcmp(name, "_eltnum") == 0:
            self.data._eltnum = value
        elif strcmp(name, "_atomtype") == 0:
            self.data._atomtype = value
        elif strcmp(name, "_posn") == 0:
            self._setposn(value)
        else:
            self.__dict__[name] = value

    def addDict(self, _BaseDictClass other):
        add_to_pointerlist(self.data.sets, <key_thing*> &other.data)

    def removeDict(self, _BaseDictClass other):
        remove_from_pointerlist(self.data.sets, other.data.key)

class AtomBase(_AtomBase):
    pass

##############################################################
##############################################################
##############################################################
##############################################################

cdef class _AtomDictBase(_BaseDictClass):

    def __setitem__(self, unsigned int key, atom):
        cdef atomstruct *adata
        adata = &(<_AtomBase> atom).data
        # Warn if key mismatches
        if key != adata.key:
            raise KeyError, (key, adata.key)
        add_to_pointerlist(self.data.members, <key_thing*> adata)
        assert (<long>adata.sets) != 0
        add_to_pointerlist(adata.sets, <key_thing *>&self.data)
    def __delitem__(self, unsigned int key):
        cdef atomstruct *adata
        x = self[key]
        adata = &(<_AtomBase> x).data
        assert adata.key == key  # remove this eventually
        remove_from_pointerlist(self.data.members, key)
        remove_from_pointerlist(adata.sets, self.data.key)
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

class AtomDictBase(_AtomDictBase):
    pass

##############################################################
##############################################################
##############################################################
##############################################################

cdef class _BondBase:

    cdef bondstruct data

    def __init__(self):
        self.data.key = 0
        self.data.self = <void*> self
        self.data.v6 = 0
        self.data.sets = new_pointerlist()

    def diffableAttributes(self):
        return ("v6",)

    def __getattr__(self, char *name):
        # ord('_') => 95. If the first char of the attribute name is
        # an underscore, give up immediately.
        if name[0] == 95:
            raise AttributeError, name
        if strcmp(name, "bond_key") == 0:
            return self.data.key
        elif strcmp(name, "v6") == 0:
            return self.data.v6
        elif strcmp(name, "sets") == 0:
            return extract_list(self.data.sets, 0)
        else:
            raise AttributeError, name

    def __setattr__(self, name, value):
        if name == "bond_key":
            self.data.key = value
        elif name == "v6":
            self.data.v6 = value
        else:
            self.__dict__[name] = value

    def addDict(self, _BaseDictClass other):
        add_to_pointerlist(self.data.sets, <key_thing*> &other.data)

    def removeDict(self, _BaseDictClass other):
        remove_from_pointerlist(self.data.sets, other.data.key)

class BondBase(_BondBase):
    pass

##############################################################
##############################################################
##############################################################
##############################################################

cdef class _BondDictBase(_BaseDictClass):

    def __setitem__(self, key, _BondBase bond):
        if key != bond.key:
            raise KeyError
        add_to_pointerlist(self.data.members, <key_thing *>&bond.data)
        add_to_pointerlist(bond.data.sets, <key_thing *>&self.data)
    def __delitem__(self, key):
        cdef bondstruct adata
        x = self[key]
        adata = (<_BondBase> x).data
        remove_from_pointerlist(self.data.members, adata.key)
        remove_from_pointerlist(adata.sets, self.data.key)
    def __contains__(self, unsigned int key):
        try:
            pointerlist_lookup(self.data.members, key)
            return 1
        except KeyError:
            return 0
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

class BondDictBase(_BondDictBase):
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

##############################################################
##############################################################
##############################################################
##############################################################

def init_bitmap_font():
    return _init_bitmap_font()
