# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ChainAtomMarker.py - a marked atom and direction in a chain of atoms,
with help for moving it to a new atom if its old atom is killed;
has state for undo/copy/save

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

### REVIEW -- is the following true?
Note: in principle, this is not specific to DNA, so it probably doesn't
need to be inside the dna_model package, though it was written to support that.

This module has no dna-specific knowledge (except in a few comments about
intended uses), and that should remain true.

See also: class DnaMarker, which inherits this.

"""

from jigs import Jig

_NUMBER_OF_MARKER_ATOMS = 2

# ==

class ChainAtomMarker(Jig):
    """
    Abstract class.
    
    Marks a single atom in some kind of chain of live atoms
    (which kind and how to move along it is known only to more
    concrete subclasses), and a direction along that chain,
    represented as a reference to the next atom along it
    (and/or by other subclass-specific attrs).

    As a jig, has pointers to both the marked and next atom,
    so it can be invalidated when either one is killed.
    Responding to that occurrence is up to subclasses,
    though this class has some support for the subclass
    "moving self to a new atom along the same chain".

    Contains state for undo/copy/save (namely the two atoms,
    individually distinguished), and perhaps more subclass-
    specific state).

    Note that there are several distinct ways this object can be "invalid"
    and become "valid" (making use of subclass-specific code in both,
    and for that matter with "validity" only meaningful in a subclass-
    specific way):

    - moving to a new atom, since the old marker_atom was killed
      (perhaps moving along an old chain that is no longer valid
       except for that purpose)

    - resetting its next_atom to a new one which records the same
      direction from its marker_atom, if next_atom died or got disconnected

    - becoming owned by the chain its atoms are on, after undo/copy/read.

    For all of these cases, the subclass needs to extend appropriate
    Jig API methods to be notified of and respond to these events,
    and it may record more info when updating self in response to them,
    which may be more definitive as a direction or position indicator
    than next_atom or perhaps even marker_atom. It is up to the subclass
    to keep those atoms up to date (i.e. change them if necessary
    to fit the more definitive info, which is not seen by copy/undo/save).
    """

    # default values of instance variables:
    
    # Jig API variables
    
    sym = "ChainAtomMarker" # probably never visible, since this is an abstract class
    
    # other variables

    marked_atom = None
    next_atom = None

    # declare attributes involved in copy, undo, mmp save
    
    copyable_attrs = Jig.copyable_attrs + ('marked_atom', 'next_atom')
        # that sets them up for copy and undo;
        # no need for mmp write/read code for these, since they're written as part of self.atoms
        # and reinitialized from that when we're constructed,
        # but do REVIEW and assert that they're in the right order when written.
        
        # note: more copyable_attrs are needed in subclasses
    
##    _old_atom = None # (not undoable or copyable) (but see comment on "make _old_atom undoable" below)
    
    # == Jig API methods

    def __init__(self, assy, atomlist):
        """
        """
        Jig.__init__(self, assy, atomlist) # calls self.setAtoms
        return

    def setAtoms(self, atomlist): #bruce 080208 split this out of __init__ so copy is simpler
        Jig.setAtoms(self, atomlist)
        if len(atomlist) == _NUMBER_OF_MARKER_ATOMS:
            marked_atom, next_atom = atomlist
            self.marked_atom = marked_atom
            self.next_atom = next_atom
            self._check_atom_order()
        else:
            # We are probably being called by _copy_fixup_at_end
            # with fewer or no atoms, or by __init__ in first stage of copy
            # (Jig.copy_full_in_mapping) with no atoms.
            # todo: would be better to make those callers tell us for sure.
            # for now: print bug warning if fewer atoms but not none
            # (i don't know if that can happen), and assert not too many atoms.
            assert len(atomlist) <= _NUMBER_OF_MARKER_ATOMS
            if atomlist:
                print "bug? %r.setAtoms(%r), len != _NUMBER_OF_MARKER_ATOMS or 0" % \
                      self, atomlist
            pass
        return
            
    def needs_atoms_to_survive(self):
        # False, so that if both our atoms are removed, we don't die.
        # Problem: if we're selected and copied, but our atoms aren't, this would copy us.
        # But this can't happen if we're at toplevel in a DNA Group, and hidden from user,
        # and thus only selected if entire DNA Group is. REVIEW if this code is ever used
        # in a non-DnaGroup context. [Also REVIEW now that we have two atoms.]
        return False
    
    def confers_properties_on(self, atom): ### REVIEW now that we have two atoms, for copy code
        """
        [overrides Node method]
        Should this jig be partly copied (even if not selected)
        when this atom is individually selected and copied?
        (It's ok to assume without checking that atom is one of this jig's atoms.)
        """
        return True

    def writemmp(self, mapping):
        """
        [extends superclass method]
        """
        # check a few things, then call superclass method
        assert not self.is_homeless() # redundant as of 080111, that's ok
        assert len(self.atoms) == _NUMBER_OF_MARKER_ATOMS
        self._check_atom_order()
        
        return Jig.writemmp(self, mapping)

    def __repr__(self): # 080118
        # find out if this harms Jig.writemmp; if not, i can try fixing __repr__ on all jigs
        classname = self.__class__.__name__.split('.')[-1]
##        try:
##            name = self.name
##        except:
##            name = "?"
        res = "<%s[%r -> %r] at %#x>" % \
              (classname, self.marked_atom, self.next_atom, id(self))
        return res
        
    # == other methods

    def _check_atom_order(self):
        """
        Check assertions about the order of the special atoms we know about
        in the list self.atoms.
        """
        # todo: extend/rename this to fix atom order (not just check it),
        # if it turns out the order can ever get messed up
        # (update 080208: maybe it can by copy or remove_atom, not sure @@@@)
        assert len(self.atoms) <= _NUMBER_OF_MARKER_ATOMS
        if len(self.atoms) == _NUMBER_OF_MARKER_ATOMS:
            assert [self.marked_atom, self.next_atom] == self.atoms
        return
    
    def is_homeless(self): # REVIEW: Maybe rename to needs_update?
        """
        Has either of our atoms been killed?
        [misnamed, since if only next_atom is killed, we're not really
         homeless -- we just need an update.]
        """
        return len(self.atoms) < _NUMBER_OF_MARKER_ATOMS
# old code:
##        res = (not self.atoms) and (self._old_atom is not None)
##        if res:
##            assert self._old_atom.killed()
##            # BUG: can fail in Undo, e.g. if you select and delete all atoms,
##            # then Undo that. (At least it did once after some other atom
##            # deletes in a duplex, just after delete_bare_atoms was implemented.)
##            # REVIEW: make _old_atom undoable, to fix this? Not sure it would help...
##            # [071205]
##        return res

# REVIEW following - needed? correct for two atoms?? (i doubt it) [bruce 080111 comment]
##    def _set_marker_atom(self, atom):
##        ## assert not self.atoms #k needed? true for current callers, but not required in principle
##        assert self.is_homeless()
##            # this assumes we initially have an atom when we're made
##        assert not atom.killed()
##        self._old_atom = None
##        self.setAtoms([atom])
##        #e other updates?
##        return
##
##    def _get_marker_atom(self):
##        if self.atoms:
##            return self.atoms[0]
##        else:
##            assert self.is_homeless()
##            return self._old_atom
##        pass
    
    pass # end of class ChainAtomMarker
