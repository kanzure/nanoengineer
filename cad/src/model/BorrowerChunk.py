# Copyright 2006-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
BorrowerChunk.py -- a chunk which temporarily borrows the atoms
from another one, for an experimental optimization of display lists
when moving subsets of the atoms of a chunk.

Not used by default. Deprecated, since some more principled and
more general loosening of the chunk <-> display list correspondence
would be much better.

@author: Bruce
@version: $Id$
@copyright: 2006-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce wrote this inside chunk.py

Bruce 080314 split this into its own file.
"""

# note: this may not have been tested since it was split out of chunk.py.

from utilities.debug import register_debug_menu_command

from model.chunk import Chunk

from model.global_model_changedicts import _changed_parent_Atoms

import foundation.env as env

from utilities.Log import orangemsg, redmsg, quote_html

from utilities.debug import safe_repr

# ==

# Some notes about BorrowerChunk [bruce 060411]
##    If an undo checkpoint occurs while the atoms are stolen,
##    it won't contain them (it will be as if they were deleted, I think).
##    This might be tolerable for A7 (if tested for safety), since cp's during drag
##    are rare -- or it might not, if problems are caused by bonds from existing to dead atoms!
##
##    When we want to fix it, here are some possible ways:
#     - make the missing-atoms scheme work, by making the bonds from existing to dead atoms also seem to be missing, somehow.
##    - let this chunk be scanned by Undo (ie make it a child of the assy, in a special place
##    so not in the MT), and let it have an _undo_update method
##    (or the like) which merges its atoms back into their homes. (It might turn out this is required
##    anyway, if having it missing during a cp causes unforseen problems.)
##    - disable cp's during drag.
##    - merge undo diffs from the drag.

# ==

class BorrowerChunk(Chunk):
    """
    A temporary Chunk (mostly transparent to users and Undo, when not added to MT) whose atoms belong in other chunks.
    Useful for optimizing redraws, since it has one perhaps-small display list, and the other chunks' display lists
    won't be modified when our atoms change (except once when we first steal their atoms, and when we add them back).

    @warning: removing atoms from, or adding atoms to, this pseudo-chunk is not supported.
    Except for debugging purposes, it should never be added to the MT, or permitted to exist when arbitrary user-ops are possible.
    Its only known safe usage pattern is to be created, used, and destroyed, during one extended operation such as a mouse-drag.
    [If more uses are thought of, these limitations could all be removed. #e]

    update 060412: trying to make it fully safe for Undo cp, and in case it's accidently left alive (in GLPane or MT).
    But not trying to make results perfectly transparent or "correct" in those cases, since we'll try to prevent them.
    E.g. for mmp save, it'll save as a normal Chunk would.
    """
    def __init__(self, assy, atomset = None, name = None): # revised 060413
        """
        #doc; for doc of atomset, see take_atomset
        """
        Chunk.__init__(self, assy, self._name_when_empty(assy))
        if atomset is not None:
            self.take_atomset(atomset, name = name)
        return

    def _name_when_empty(self, assy = None):
        if assy is None:
            assy = self.assy
        del assy # not yet used; might use id or repr someday
        return "(empty borrower id %#x)" % id(self)

    def take_atomset(self, atomset, name = None):
        """
        #doc; atomset maps atom.key -> atom for some atoms we'll temporarily own
        @warning: if all of another chunk's atoms are in atomset, creating us will kill that chunk.
        @warning: it's up to the caller to make sure all singlet neighbors of atoms in atomset
                  are also in atomset! Likely bugs if it doesn't.
        If you want to call this again on new atoms, call self.demolish first.
        """
        if not name:
            name = "(borrower of %d atoms, id %#x)" % (len(atomset), id(self)) #e __repr__ also incls this info
        self.name = name # no use for prior value of self.name #k is there a set_name we should be using??
        atoms = atomset.values() #e could optim this -- only use is to let us pick one arbitrary atom
        egatom = atoms[0]
        egmol = egatom.molecule # do this now, since we're going to change it in the loop
        del atoms, egatom
        assy = egmol.assy
        assert assy is self.assy
        # now steal the atoms, but remember their homes and don't add ourselves to assy.tree.
        # WARNING: if we steal *all* atoms from another chunk, that will cause trouble,
        # but preventing this is up to the caller! [#e put this into another method, so it can be called again later??]
        # We optimize this by lots of inlining, since we need it to be fast for lots of atoms.
        harmedmols = {} # id(mol) -> mol for all mols whose atoms we steal from
        origmols = {} # atom.key - original atom.molecule
        self.origmols = origmols
        self.harmedmols = harmedmols
        # self.atoms was initialized to {} in Chunk.__init__, or restored to that in self.demolish()
        for key, atom in atomset.iteritems():
            mol = atom.molecule
            assert mol is not self
            if isinstance(mol, self.__class__):
                print "%r: borrowing %r from another borrowerchunk %r is not supported" % (self, atom, mol)
                    # whether it might work, I have no idea
            harmedmols[id(mol)] = mol
            # inline part of mol.delatom(atom):
            #e do this later: mol.invalidate_atom_lists()
            _changed_parent_Atoms[key] = atom
            del mol.atoms[key] # callers can check for KeyError, always an error
            # don't do this (but i don't think it prevents all harm from stealing all mol's atoms):
            ## if not mol.atoms:
            ##     mol.kill()
            # inline part of self.addatom(atom):
            atom.molecule = self
            atom.index = -1 # illegal value
            self.atoms[key] = atom
            #e do this later: self.invalidate_atom_lists()
            # remember where atom came from:
            origmols[key] = mol
        # do what we saved for later in the inlined delatom and addatom calls:
        for mol in harmedmols.itervalues():
            natoms = len(mol.atoms)
            if not natoms:
                print "bug: BorrowerChunk stole all atoms from %r; potential for harm is not yet known" % mol
            mol.invalidate_atom_lists()
        self.invalidate_atom_lists()

        try:
            part = egmol.part
            part.add(self) ###e not 100% sure this is ok; need to call part.remove too (and we do)
            assert part is self.part # Part.add should do this (if it was not already done)
        except:
            print "data from following exception: egmol = %r, its part = %r, self.part = %r" % \
                  ( egmol, part, self.part )
            raise

        return # from take_atomset
    
    # instead of overriding _draw_for_main_display_list
    # (now in ChunkDrawer rather than in our superclass Chunk,
    #  so overriding it would require defining a custom _drawer_class),
    # it's enough to define _colorfunc and _dispfunc to help it:
    
    def _colorfunc(self, atm):
        """
        Define this to use atm's home mol's color instead of self.color, and also so that self._dispfunc gets called
        [overrides self._colorfunc = None; this scheme will get messed up if self ever gets copied,
         since the copy code (two methods in Chunk) will set an instance attribute pointing to the bound method of the original]
        """
        #e this has bugs if we removed atoms from self -- that's not supported (#e could override delatom to support it)
        return self.origmols[atm.key].drawing_color()

    def _dispfunc(self, atm):
        origmol = self.origmols[atm.key]
        glpane = origmol.glpane # set shortly before this call, in origmol.draw (kluge)
        disp = origmol.get_dispdef(glpane)
        return disp

    def restore_atoms_to_their_homes(self):
        """
        put your atoms back where they belong
        (calling this multiple times should be ok)
        """
        #e this has bugs if we added atoms to self -- that's not supported (#e could override addatom to support it)
        origmols = self.origmols
        for key, atom in self.atoms.iteritems():
            _changed_parent_Atoms[key] = atom
            origmol = origmols[key]
            atom.molecule = origmol
            atom.index = -1 # illegal value
            origmol.atoms[key] = atom
        for mol in self.harmedmols.itervalues():
            mol.invalidate_atom_lists()
        self.atoms = {}
        self.origmols = {}
        self.harmedmols = {}
        ## self.part = None
        self.invalidate_atom_lists() # might not matter anymore; hope it's ok when we have no atoms
        if self.part is not None:
            self.part.remove(self)
        return
    
    def demolish(self):
        """
        Restore atoms, and make self reusable
        (but up to caller to remove self from any .dad it might have)
        """
        self.restore_atoms_to_their_homes()
        self.name = self._name_when_empty()
        return
    
    def take_atoms_from_list(self, atomlist):
        """
        We must be empty (ready for reuse).
        Divide atoms in atomlist by chunk; take the atoms we can (without taking all atoms from any chunk);
        return a pair of lists (other_chunks, other_atoms), where other_chunks are chunks whose atoms were all in atomlist,
        and other_atoms is a list of atoms we did not take for some other reason
        (presently always [] since there is no other reason we can't take an atom).
        """
        # note: some recent selectMode code for setting up dragatoms is similar enough (in finding other_chunks)
        # that it might make sense to pull out a common helper routine
        other_chunks = []
        other_atoms = [] # never changed
        our_atoms = []
        chunks_and_atoms = divide_atomlist_by_chunk(atomlist) # list of pairs (chunk, atoms in it)
        for chunk, atlist in chunks_and_atoms:
            if len(chunk.atoms) == len(atlist):
                other_chunks.append(chunk)
            else:
                our_atoms.extend(atlist)
        atomset = dict([(a.key, a) for a in our_atoms])
        self.take_atomset( atomset)
        return other_chunks, other_atoms
    
    def kill(self):
        self.restore_atoms_to_their_homes() # or should we delete them instead?? (this should never matter in our planned uses)
            # this includes self.part = None
        Chunk.kill(self)
    
    def destroy(self):
        self.kill()
        self.name = "(destroyed borrowerchunk)"
    
    # for testing, we might let one of these show up in the MT, and then we need these cmenu methods for it:
    
    def __CM_Restore_Atoms_To_Their_Homes(self):
        self.restore_atoms_to_their_homes()
        assy = self.assy
        self.kill()
        assy.w.win_update() # at least mt_update is needed
    
    #e we might need destroy and/or kill methods which call restore_atoms_to_their_homes
    
    pass # end of class BorrowerChunk

# ==

def divide_atomlist_by_chunk(atomlist): # only used in this file as of 080314, but might be more generally useful
    # note: similar to some recent code for setting up dragatoms in selectMode, but not identical
    """
    Given a list of atoms, return a list of pairs
    (chunk, atoms in that chunk from that list).
    Assume no atom appears twice.
    """
    resdict = {} # id(chunk) -> list of one or more atoms from it
    for at in atomlist:
        chunk = at.molecule
        resdict.setdefault(id(chunk), []).append(at)
    return [(atlist[0].molecule, atlist) for atlist in resdict.itervalues()]

def debug_make_BorrowerChunk(target):
    """
    (for debugging only)
    """
    debug_make_BorrowerChunk_raw(True)

def debug_make_BorrowerChunk_no_addmol(target):
    """
    (for debugging only)
    """
    debug_make_BorrowerChunk_raw(False)

def debug_make_BorrowerChunk_raw(do_addmol = True):
    win = env.mainwindow()
    atomset = win.assy.selatoms
    if not atomset:
        env.history.message(redmsg("Need selected atoms to make a BorrowerChunk (for debugging only)"))
    else:
        atomset = dict(atomset) # copy it, since we shouldn't really add singlets to assy.selatoms...
        for atom in atomset.values(): # not itervalues, we're changing it in the loop!
            # BTW Python is nicer about this than I expected:
            # exceptions.RuntimeError: dictionary changed size during iteration
            for bp in atom.singNeighbors(): # likely bugs if these are not added into the set!
                atomset[bp.key] = bp
            assy = atom.molecule.assy # these are all the same, and we do this at least once
        chunk = BorrowerChunk(assy, atomset)
        if do_addmol:
            win.assy.addmol(chunk)
        import __main__
        __main__._bc = chunk
        env.history.message(orangemsg("__main__._bc = %s (for debugging only)" % quote_html(safe_repr(chunk))))
    win.win_update() #k is this done by caller?
    return

# ==

register_debug_menu_command("make BorrowerChunk", debug_make_BorrowerChunk)
register_debug_menu_command("make BorrowerChunk (no addmol)", debug_make_BorrowerChunk_no_addmol)

# end

