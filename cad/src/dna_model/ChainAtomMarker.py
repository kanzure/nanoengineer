# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
ChainAtomMarker.py - a marked atom in a chain, with help for moving it
to a new atom if its old atom is killed; has state for undo/copy/save

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

### REVIEW -- is the following true?
Note: in principle, this is not specific to DNA, so it probably doesn't
need to be inside the dna_model package, though it was written to support that.

This module has no dna-specific knowledge (except in a few comments about
intended uses), and that should remain true.

See also: class DnaAtomMarker, which inherits this.

"""

from jigs import Jig

# ==

class ChainAtomMarker(Jig):
    """
    A marked atom in an AtomChainOrRing, with help for moving it
    to a new atom if its old atom is killed; has state for undo/copy/save
    """

    # default values of instance variables:
    
    # Jig API variables
    
    sym = "ChainAtomMarker" # probably never visible, since this is an abstract class

    ## copyable_attrs = Jig.copyable_attrs + () # more are only needed in subclasses
    
    # other variables
    
    _old_atom = None # (not undoable or copyable)
    _chain = None # (not undoable or copyable)
    
    # == Jig API methods

    def __init__(self, assy, atomlist, chain = None):
        # [can chain be None after we get copied? I think so...]
        # (chain arg is not needed in _um_initargs since copying it can/should make it None. REVIEW, is that right? ###]
        """
        @param chain: the atom chain or ring which we reside on when created (can it be None??)
        @type chain: AtomChainOrRing instance
        """
        assert len(atomlist) == 1
        Jig.__init__(self, assy, atomlist)
        if chain is not None:
            self.set_chain(chain)
        return
        
    def needs_atoms_to_survive(self):
        # False, so that if our atom is removed, we don't die.
        # Problem: if we're selected and copied, but our atom isn't, this would copy us.
        # But this can't happen if we're at toplevel in a DNA Group, and hidden from user,
        # and thus only selected if entire DNA Group is. REVIEW if this code is ever used
        # in a non-DnaGroup context.
        return False
    
    def confers_properties_on(self, atom):
        """
        [overrides Node method]
        Should this jig be partly copied (even if not selected)
        when this atom is individually selected and copied?
        (It's ok to assume without checking that atom is one of this jig's atoms.)
        """
        return True
    
    def remove_atom(self, atom):
        """
        [subclasses might need to extend this]
        """
        assert atom in self.atoms and len(self.atoms) == 1
        self._old_atom = atom
        Jig.remove_atom(self, atom)
        return
    
    # == other methods

    def is_homeless(self):
        """
        Has our atom been killed?
        """
        res = (not self.atoms) and (self._old_atom is not None)
        if res:
            assert self._old_atom.killed()
        return res

    def _set_marker_atom(self, atom):
        ## assert not self.atoms #k needed? true for current callers, but not required in principle
        assert self.is_homeless()
            # this assumes we initially have an atom when we're made
        assert not atom.killed()
        self._old_atom = None
        self.setAtoms([atom])
        #e other updates?
        return

    def _get_marker_atom(self):
        if self.atoms:
            return self.atoms[0]
        else:
            assert self.is_homeless()
            return self._old_atom
        pass
    
    def set_chain(self, chain):
        """
        A new atom chain or ring is taking us over (but we'll stay on the same atom).

        @param chain: the atom chain or ring which we reside on when created (can it be None??)
        @type chain: AtomChainOrRing instance

        @note: some subclasses should extend this method to add invalidations.
        """
        assert not self.is_homeless()
        #e assert chain contains self._get_marker_atom()?
        assert chain is not None # or should None be allowed, as a way of unsetting it??
        self._chain = chain
        return

    pass # end of class ChainAtomMarker
