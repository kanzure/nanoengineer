# Pyrex file for base classes

#cdef extern from "basehelp.c":
#    cdef struct intset:
#        pass
#    intset_add(intset, int)
#    intset_contains(intset, int)
#    intset_remove(intset, int)

cdef class AtomBase:
    pass

cdef class BondBase:
    pass

class IntSetReferenceImplementation:
    def __init__(self):
        self._lst = [ ]
    def add(self, n):
        import types
        assert type(n) == types.IntType
        self._lst.append(n)
    def remove(self, n):
        import types
        assert type(n) == types.IntType
        # no complaint if it's not there?
        try: self._lst.remove(n)
        except ValueError: pass
    def contains(self, n):
        import types
        assert type(n) == types.IntType
        return n in self._lst

cdef class IntSet:
    pass
