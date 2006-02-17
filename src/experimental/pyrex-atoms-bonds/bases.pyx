# Pyrex file for base classes

cdef extern from "Numeric/arrayobject.h":
    object PyArray_FromDims(int nd, int *d, int type)

cdef extern from "basehelp.c":
    #checkForErrors()
    cdef struct atomset:
        pass
    cdef struct chunkbase:
        pass
    cdef struct atombase:
        int positionIndex
    atomset *atomset_init()
    atomset_size(atomset*)
    void atomset_del(atomset*)
    atomset_contains(atomset*, int)
    atomset_remove(atomset*, int)
    atomset_set(atomset*, int, PyObject)
    atomset_get(atomset*, int)
    atomset_asarray(atomset*)
    void atomset_quickfill(atomset*, int, int, int)
    double atomset_contains_performance(atomset*, int)
    double atomset_set_performance(atomset*, int)
    double atomset_asarray_performance(atomset*, int)
    chunkbase *chunkbase_init()
    chunkbase_addatom(chunkbase*, atombase*, int, double, double, double)
    void chunkbase_del(chunkbase*)
    atombase *atombase_init()
    void atombase_del(atombase*)

cdef class __AtomSet:
    cdef atomset *x
    def __init__(self):
        self.x = atomset_init()
        #checkForErrors()
    def __del__(self):
        atomset_del(self.x)
    def __len__(self):
        return atomset_size(self.x)
    def __setitem__(self, n, obj):
        atomset_set(self.x, n, obj)
    def __getitem__(self, n):
        return atomset_get(self.x, n)
    def __delitem__(self, n):
        atomset_remove(self.x, n)
    def asArray(self):
        return atomset_asarray(self.x)
    def contains(self, n):
        return atomset_contains(self.x, n)
    def contains_performance(self, n):
        return atomset_contains_performance(self.x, n)
    def set_performance(self, n):
        return atomset_set_performance(self.x, n)
    def asarray_performance(self, n):
        return atomset_asarray_performance(self.x, n)
    def quickFill(self, n, div=1):
        atomset_quickfill(self.x, n, div, 0)

class AtomSet(__AtomSet):
    # __del__ doesn't get used until you derive a non-cdef class
    pass

cdef class __AtomBase:
    cdef atombase *x
    def __init__(self):
        self.x = atombase_init()
        #checkForErrors()
    def __del__(self):
        atombase_del(self.x)

class AtomBase(__AtomBase):
    pass

cdef class BondBase:
    pass

cdef class __ChunkBase:
    cdef chunkbase *x
    def __init__(self):
        self.x = chunkbase_init()
        #checkForErrors()
    def __del__(self):
        chunkbase_del(self.x)
    def addatom(self, __AtomBase atm, tp, x, y, z):
        chunkbase_addatom(self.x, atm.x, tp, x, y, z)

class ChunkBase(__ChunkBase):
    # Maintain a normal Python list of atoms so that the
    # atoms don't get GCed while the chunk is still alive
    def __init__(self):
        __ChunkBase.__init__(self)
        self.atomlist = [ ]
    def addatom(self, ab, tp, x, y, z):
        __ChunkBase.addatom(self, ab, tp, x, y, z)
        self.atomlist.append(ab)
