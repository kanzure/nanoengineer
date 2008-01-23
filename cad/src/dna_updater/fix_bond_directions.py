# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
fix_bond_directions.py - dna updater helper functions

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from elements import Singlet

# ==

# comments from caller, perhaps for docstrings here: ###

    #
    # The changes caused by these fixes include:
    # - setting or perhaps clearing bond direction (changes from this could be ignored here)
    # - breaking bonds in some cases (### REVIEW how to handle changes from this -- grab/fix new bondpoints?)
    # Tentative conclusion: no need to do anything to new changed atoms except scan them later. ### REVIEW
    
    # Non-local bond direction issues (e.g. choosing a bond direction
    # for a long portion of a chain on which it's unset) are fixed elsewhere,
    # once WholeChains are available or while forming them. # @@@@ NIM as of 08012 morning

def fix_local_bond_directions( changed_atoms): # mostly a stub; debug print if anything needs fixing [untested]
    """
    Fix local directional bond issues, namely:
    - directional bond chain branches (illegal)
    - missing bond directions (when fixable locally -- most are not)
    - inconsistent bond directions
    """
    # Q. Which changes from this are needed in subsequent dna updater steps?
    # A. I think the answer is identical to that for delete_bare_atoms [bruce 080122]:
    # The changed neighbor atoms are needed, in case they're the only
    # indicator of a change to the chain they're on (especially if the killed
    # atom was in a different dna ladder). But their classes needn't be changed,
    # and their deletion can't cause any more atoms to become bare (due to
    # the current meaning of bare), so no earlier steps need to be repeated.

    # Algorithm: just look at every atom, counting directional real & open bonds
    # of each direction. Build a set of problems to fix at the end... ####
    #
    # worry: what if a bond looks ok from one side but then gets broken from other side?
    # this might require rescanning first side... need to analyze situations like this...
    # - first look at all atoms with >2 directional bonds (error if >2 are real)
    #   - decide whether to bust all bonds (to be fair if all have dirs set) or only some...
    #
    # maybe:
    # - first delete some atoms or all their bonds -- too much there, or inconsistent directions
    #   (make sure that won't trigger delete_bare_atoms on them in the next round!) @@@
    #   possible kluge to detect which bond is new/wrong: look at chunks of the atoms, guess new is interchunk if only one is
    # - then look at all bonds for missing dirs we can fill in (or could save this for later steps)

    # see also:
    
##    print "fix_local_bond_directions is a stub" # stub @@@@
    
    break_these_bonds = [] ## change to a dict?
    unset_direction_on_these_bonds = {} ###
    
    for atom in changed_atoms.itervalues():
        if atom.element is Singlet:
            continue # handle these as part of their base atom
        if not atom.element.bonds_can_be_directional:
            # note: we needn't worry here about nondirectional bonds
            # with a direction set. Those can't hurt us except on directional
            # elements, dealt with below. @@@DOIT
            continue # optimization
        # note: at this stage we might have Ss or Pl;
        # valence has not been checked (in code as of 080123)
        _fix_atom(atom) ### side effect args?
        
        pass ###

    for bond in break_these_bonds:
        bond.bust()

    return # from fix_local_bond_directions

def _fix_atom(atom):
    """
    [private helper for fix_local_bond_directions]
    @param atom: a real atom which permits directional bonds.
    """
    # note: the following code is related to these Atom methods
    # (but can't be fully handled by them):
    # - Atom.bond_directions_are_set_and_consistent
    #   (not sufficient to say it's ok -- misses new real directional bonds
    #    w/ no direction set)
    # - Atom.directional_bond_chain_status (only looks at bonds being
    #    directional or not, not what directions are set)

    # TODO: once we're sure this is right, speed up the usual case
    # (no changes needed) by making a separate loop just to find
    # atoms that require any changes. Also consider coding that in C/Pyrex. @@@
    # But don't optimize it that way right now, since the details of what
    # the fast initial check should do might change.

    # count kinds of directional bonds on atom
    num_plus_real = 0
    num_minus_real = 0
    num_unset_real = 0
    
    num_plus_open = 0
    num_minus_open = 0
    num_unset_open = 0
        
    for bond in atom.bonds:
        direction = bond.bond_direction_from(atom)
        neighbor = bond.other(atom)
            # we'll use this to inline & optimize both
            # bond.is_directional and bond.is_open_bond,
            # since we know enough about atom that only neighbor
            # can affect them
        is_directional = neighbor.element.bonds_can_be_directional
        is_open_bond = (neighbor.element is Singlet)

        if direction == 1:
            if not is_directional:
                assert not is_open_bond
                _clear_illegal_direction(bond)                
            elif is_open_bond:
                num_plus_open += 1
            else:
                num_plus_real += 1
        elif direction == -1:
            if not is_directional:
                assert not is_open_bond
                _clear_illegal_direction(bond)                
            elif is_open_bond:
                num_minus_open += 1
            else:
                num_minus_real += 1
        else:
            if is_open_bond:
                num_unset_open += 1
            elif is_directional:
                num_unset_real += 1
            pass
        continue # next bond of atom

    # what to look for, for all to be already ok: ### REVIEW -- correct and complete? I think so, but re-check it...
    # (might optim the above to only check for that first -- usual case)
    # - real bonds must number <= 2, be zero or one of each nonzero direction, none unset
    # - open bonds must bring that to exactly one of each nonzero direction
    # equiv to: exactly one in all, of each nonzero direction; no reals are unset.

    num_plus = num_plus_real + num_plus_open
    num_minus = num_minus_real + num_minus_open
    
    if num_unset_real or num_plus != 1 or num_minus != 1:
        # have to fix something about this atom;
        # print info that tells me what cases need handling ASAP, @@@
        # vs cases that can wait
        print "\n*** dna updater: fix_local_bond_directions ought to fix %r but is NIM" % (atom,)
        print " data about that atom:"
        print "  num_plus_real =", num_plus_real
        print "  num_minus_real =", num_minus_real
        print "  num_unset_real =", num_unset_real
        print "  num_plus_open =", num_plus_open
        print "  num_minus_open =", num_minus_open
        print "  num_unset_open =", num_unset_open
        print
    
    return # from _fix_atom

def _clear_illegal_direction(bond):
    """
    [private helper for _fix_atom]

    bond has a direction but is not directional
    (since one of its atoms does not permit directional bonds,
     e.g. it might be an Ss-Ax bond).
    Report and immediately fix this error.

    @type bond: Bond
    """
    print "\n*** _clear_illegal_direction(%r)" % (bond,)
    bond._clear_bond_direction()
    return

# ==

#e todo: nonlocal helper functions

# end
