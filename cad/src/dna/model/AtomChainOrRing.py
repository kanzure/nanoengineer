# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
AtomChainOrRing.py - cache info about atom/bond chains or rings of various types

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

Note: this is not specific to DNA, so it probably doesn't belong inside the
dna_model package, though it was written to support that.

This module has no dna-specific knowledge, and that should remain true.

See also: class DnaChain, which inherits this.
"""

class AtomChainOrRing(object):
    """
    Abstract class, superclass of AtomChain and AtomRing.

    Used internally to cache information about atom chains or rings.
    Contains no undoable state; never appears in internal model tree or mmp file

    The atom and bond lists are not modifiable after init.

    Some of all of the atoms and bonds might be killed.
    """
    # subclass constant
    ringQ = None # subclasses set this to True or False

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
    pass

class AtomChain(AtomChainOrRing):
    ringQ = False
    pass

class AtomRing(AtomChainOrRing):
    ringQ = True
    pass

# end
