# Pyrex file for base classes

cdef extern from "Numeric/arrayobject.h":
    object PyArray_FromDims(int nd, int *d, int type)

cdef extern from "basehelp.c":
    checkForErrors()
    cdef struct intset:
        pass
    cdef struct chunkbase:
        pass
    cdef struct atombase:
        int positionIndex
    intset *intset_init()
    intset_size(intset*)
    intset_add(intset*, int)
    intset_addRange(intset*, int, int)
    intset_asarray(intset*)
    intset_fromList(intset*, PyObject)
    intset_contains(intset*, int)
    intset_remove(intset*, int)
    intset_del(intset*)
    double intset_contains_performance_test(intset*, int)
    double intset_add_performance(intset*, int)
    double intset_asarray_performance_test(intset*, int)
    chunkbase *chunkbase_init()
    chunkbase_addatom(chunkbase*, atombase*, int, double, double, double)
    void chunkbase_del(chunkbase*)
    atombase *atombase_init()
    void atombase_del(atombase*)

cdef class __IntegerSet:
    cdef intset *x
    def __init__(self):
        self.x = intset_init()
        checkForErrors()
    def __del__(self):
        intset_del(self.x)
    def __len__(self):
        return intset_size(self.x)
    def fromList(self, lst):
        intset_fromList(self.x, lst)
    def add(self, n):
        intset_add(self.x, n)
    def asArray(self):
        return intset_asarray(self.x)
    def remove(self, n):
        intset_remove(self.x, n)
    def contains(self, n):
        return intset_contains(self.x, n)
    def addRange(self, m, n):
        intset_addRange(self.x, m, n)
    def contains_performance(self, n):
        return intset_contains_performance_test(self.x, n)
    def add_performance(self, n):
        return intset_add_performance(self.x, n)
    def asarray_performance(self, n):
        return intset_asarray_performance_test(self.x, n)

class IntegerSet(__IntegerSet):
    # __del__ doesn't get used until you derive a non-cdef class
    pass

cdef class __AtomBase:
    cdef atombase *x
    def __init__(self):
        self.x = atombase_init()
        checkForErrors()
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
        checkForErrors()
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
