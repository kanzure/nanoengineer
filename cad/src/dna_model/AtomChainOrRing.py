# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
AtomChainOrRing.py - 

Used internally for base indexing in strands and segments; perhaps used in the
future to mark subsequence endpoints for relations or display styles.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

# ==

class AtomChainOrRing(object):
    """
    Abstract class, superclass of AtomChain and AtomRing.

    Used internally to cache information about atom chains or rings.
    Contains no undoable state; never appears in internal model tree or mmp file

    The atom and bond lists are not modifiable after init.

    Some of all of the atoms and bonds might be killed.
    """
    ringQ = None # subclasses set this to True or False
    index_direction = 1 # might be set to 1 or -1 in instances -- OR we might replace this with a .reverse() method ### REVIEW/IMPLEM
        # note: not the same as bond direction for strands (which is not even defined for axis bonds).
    def __init__(self, listb, lista):
        assert self.ringQ in (False, True) # i.e. we're in a concrete subclass
        self.bond_list = listb
        self.atom_list = lista
        if self.ringQ:
            assert len(listb) == len(lista)
            #e and more conditions about how they relate [see calling code asserts]
            # (which also make sure caller didn't reverse the arg order)
        else:
            assert len(listb) + 1 == len(lista)
            #e ditto
        return
    def iteratoms(self): # REVIEW: different if self.index_direction < 0?
        """
        # get doc from calling method
        """
        return self.atom_list
    def _f_own_atoms(self):
        """
        Own our atoms, for chain purposes.
        This does not presently store anything on the atoms, even indirectly,
        but we do take over the markers and decide between competing ones and tell them their status.
        """
        print "%r._f_own_atoms() is nim" % self #####IMPLEM
    pass

class AtomChain(AtomChainOrRing):
    ringQ = False
    pass

class AtomRing(AtomChainOrRing):
    ringQ = True
    pass

# end
