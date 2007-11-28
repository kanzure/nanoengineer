# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
AtomChainOrRing.py - 

Used internally for base indexing in strands and segments; perhaps used in the
future to mark subsequence endpoints for relations or display styles.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_model.DnaAtomMarker import DnaAtomMarker # needs refactoring, since this is dna-specific

# ==

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

    # default values of instance variables
    # these variables might be DNA-specific:
    index_direction = 1 # might be set to 1 or -1 in instances -- OR we might replace this with a .reverse() method ### REVIEW/IMPLEM
        # note: not the same as bond direction for strands (which is not even defined for axis bonds).
    controlling_marker = None
    
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
        but we do take over the markers and decide between competing ones
        and tell them their status, and record the list of markers (needs update??)
        and the controlling marker for our chain identity (needs update??).
        This info about markers might be DNA-specific ...
        and it might be only valid during the dna updater run, before
        more model changes are made. [#todo: update docstring when known]
        """
        print "%r._f_own_atoms() is a stub - always makes a new marker" % self #####FIX
        # stub -- just make a new marker! we'll need code for this anyway...
        # but it's WRONG to do it when an old one could take over, so this is not a correct stub, just one that might run.
        atom = self.atom_list[0]
        # hmm, this is getting dna specific, but we already have a chain vs ring subclass distinction,
        # which might affect general methods, so ignore that for now...
        assy = atom.molecule.assy
        marker = DnaAtomMarker(assy, [atom], chain = self)
        self.controlling_marker = marker
        marker.set_whether_controlling(True)
        ## and call that with False for the other markers, so they die if needed -- ### IMPLEM
    pass

#e maybe chain vs ring should not be a subclass distinction,
# just an init argument, though letting it determine a mixin might be useful

class AtomChain(AtomChainOrRing):
    ringQ = False
    pass

class AtomRing(AtomChainOrRing):
    ringQ = True
    pass

# end
