# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
fix_bond_directions.py - dna updater helper functions

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from elements import Singlet

from debug_prefs import debug_pref, Choice_boolean_False

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

_DEBUG_PRINT_BOND_DIRECTION_ERRORS = False # set as global inside functions here

def fix_local_bond_directions( changed_atoms): # mostly a stub; debug print if anything needs fixing
    """
    Fix local directional bond issues, namely:
    - directional bond chain branches (illegal)
    - missing bond directions (when fixable locally -- most are not)
    - inconsistent bond directions
    """
    # Q. Which changes recorded by our side effects are needed in subsequent
    # dna updater steps?
    # A. Same as for delete_bare_atoms, I think [bruce 080122]:
    # The changed neighbor atoms are needed, in case they're the only
    # indicator of a change to the chain they're on (especially if the killed
    # atom was in a different dna ladder). But their classes needn't be changed,
    # and their deletion can't cause any more atoms to become bare (due to
    # the current meaning of bare), so no earlier updater steps need to be
    # repeated.

    # Algorithm: just look at every atom, counting directional real & open bonds
    # of each direction (plus == out, minus == in). Build a set of problems to
    # fix at the end, as well as fixing some at the time, or marking atoms or
    # bonds as having errors.
    #
    # REVIEW comments below here:
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


    global _DEBUG_PRINT_BOND_DIRECTION_ERRORS
    _DEBUG_PRINT_BOND_DIRECTION_ERRORS = \
        debug_pref( "DNA updater: print bond direction errors",
                    Choice_boolean_False
                   )
    
##    break_these_bonds = [] ## change to a dict?
##    unset_direction_on_these_bonds = {} ###

    new_error_atoms = {}

    # We need to look for new errors on changed_atoms,
    # or old errors on all other atoms in the same base pair
    # as any changed atom (whether or not it has an error).
    # (Would it be more efficient to save all old errors somewhere global?
    #  YES, since in the usual case, there are none!) # @@@@ DOIT

    for atom in changed_atoms.itervalues():
        # look for new errors
        if atom.element is Singlet:
            continue # handle these as part of their base atom
        if not atom.element.bonds_can_be_directional:
            # note: we needn't worry here about nondirectional bonds
            # with a direction set. Those can't hurt us except on directional
            # elements, dealt with below. @@@DOIT
            continue # optimization
        # note: at this stage we might have Ss or Pl;
        # valence has not been checked (in code as of 080123)
        res = _fix_atom(atom) ### side effect args? or return bonds to break?
        if res:
            error_type, error_data = res
            assert error_type == _ATOM_HAS_ERROR
            assert error_data and type(error_data) == type("")
            if _DEBUG_PRINT_BOND_DIRECTION_ERRORS:
                print "bond direction error for %r: %s" % (atom, error_data)
                print
            atom._dna_updater__error = error_data ##### @@@ make this affect later updater stages, graphics, tooltips
            new_error_atoms[atom.key] = atom
        else:
            if atom._dna_updater__error:
                del atom._dna_updater__error
        continue

    for atom in error_atoms.itervalues():
        # propogate errors within base pair
        # (but don't override existing errors)
        # (deterministic since only the fact of error
        #  is propogated, not error string itself,
        #  which could differ if different sources of it
        #  got propogated first)
        # REVIEW: does "lack of error" also effectively get propogated
        # once the user fixes the error? Only if changed_atoms is already
        # "closed" across rung bonds! I BET IT'S NOT. We'll see. @@@
        # RELATED: if changed_atoms was not closed that way,
        # then atoms that looked ok above might need errors propogated
        # from other (unchanged) atoms with errors. SERIOUS BUG IF NOT, need to fix.
        # [this is where i am, tue night 080129, plus above cmt about "save all old errors somewhere global". @@@@]

        for atom2 in _same_base_pair_atoms(atom): # IMPLEM @@@
            if not 
##    for bond in break_these_bonds:
##        bond.bust()

    return # from fix_local_bond_directions

# error type codes (may be revised)
_ATOM_HAS_ERROR = 1

def _fix_atom(atom):
    """
    [private helper for fix_local_bond_directions]

    If atom looks fine (re directional bonds), do nothing and return None.

    Otherwise try to fix it and/or return advice to caller about it,
    as a tuple of (error type code, error data).
    
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
            # can affect their values.
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
    # considering directional bonds (dirbonds) only:
    # - real directional bonds must number <= 2,
    #   with 0 or 1 of each nonzero direction, none with direction unset
    # - open directional bonds must bring those totals to exactly one
    #   of each nonzero direction.
    # those conds are equivalent to:
    # - exactly one dirbond of each nonzero direction;
    # - no real directional bonds are unset (in direction).

    num_plus = num_plus_real + num_plus_open
    num_minus = num_minus_real + num_minus_open
        # note: these variables might be modified below
        # but the just-assigned relations are kept correct.

    if not (num_unset_real or num_plus != 1 or num_minus != 1):
        # nothing wrong (note: doesn't check valence)
        return None
    
    # We need to fix something about this atom (assumed Ss or Pl),
    # or record an error. Detect the most serious errors first so they
    # will be the ones recorded.

    if _DEBUG_PRINT_BOND_DIRECTION_ERRORS:
        # (too bad we can't print the return value easily)
        # print info that tells me what cases need handling ASAP, @@@
        # vs cases that can wait
        print "\n*** dna updater: fix_local_bond_directions ought to fix %r but is NIM" % (atom,)
        print " data about that atom:", \
              num_plus_real, num_minus_real, num_unset_real, \
              num_plus_open, num_minus_open, num_unset_open
            # that form is for sorting output text lines;
            # the next form is for readability (make it once only?):
        print "  num_plus_real =", num_plus_real
        print "  num_minus_real =", num_minus_real
        print "  num_unset_real =", num_unset_real
        print "  num_plus_open =", num_plus_open
        print "  num_minus_open =", num_minus_open
        print "  num_unset_open =", num_unset_open
        print
    
    if num_plus_real + num_minus_real + num_unset_real > 2:
        # Too many real directional bonds -- no way to fully fix
        # without breaking one, so let the user choose which one.
        return _ATOM_HAS_ERROR, "too many real directional bonds"

    if num_plus_real > 1 or num_minus_real > 1:
        # contradiction in real bond directions -- we would need to damage
        # something to fix it (break or unset (direction of) real bonds).
        return _ATOM_HAS_ERROR, "inconsistent bond directions"

    if num_unset_real:
        # Just report this error rather than spending development time
        # trying to fix it. Both ends of an unset real bond will get marked
        # as errors (no guarantee it's with *this* error, but that's ok),
        # so there's no danger of this bond making it into a chain later
        # (and thus causing trouble) from either end-atom. No need to mark
        # this error on the bond itself, since it's easy to detect directly
        # when drawing the bond. # @@@ DOIT
        return _ATOM_HAS_ERROR, "unset real bond direction"

    # Note: some of the following code is general enough to handle
    # num_unset_real > 0, so it is left in some expressions.

    if num_plus + num_minus + num_unset_real > 2:
        # too much is set, or *would be* if all real bonds were set
        # (as they should be) -- can we unset some open bonds to fix that?

        # (Note: due to earlier checks (ignoring the check on num_unset_real),
        # we know that num_plus_real and num_minus_real are 0 or 1,
        # and num_unset_real is 0 or 1 or 2.)
        
        # Any open bond that duplicates a real bond direction
        # (or another open bond direction) should be unset.
        # But if num_unset_real, we won't know which open bond direction
        # is bad until we set the real bond direction. We marked that
        # case as an error above, but if that ever changes, we would not
        # fix it here, but leave it for later code to fix when the real
        # bond directions were chosen. (As it is, only the user can choose
        # them, so the "later code" is the next dna updater pass after
        # they do that.)
        while num_plus_open and num_plus > 1:
            _unset_some_open_bond_direction(+1) # IMPLEM; somehow print warning that it acted @@@
            num_plus_open -= 1
            num_plus -= 1
        while num_minus_open and num_minus > 1:
            _unset_some_open_bond_direction(-1)
            num_minus_open -= 1
            num_minus -= 1
        if not (num_unset_real or num_plus != 1 or num_minus != 1):
            # if not still bad, then declare atom as ok
            return None
            
        # (note: if we someday look for chains of unset real bonds to fix,
        #  then we might want to do the above in an initial pass,
        #  or in a subroutine called on any atom we hit then.)

        # at this point, real bonds are not excessive but might be deficient;
        # open bonds might make the total (of one nonzero direction value)
        # excessive but will be fixed at the end.

    # What remains is to add directions to open bonds if this would
    # fully fix things.

    assert num_plus <= 1
    assert num_minus <= 1

    if (1 - num_plus) + (1 - num_minus) <= num_unset_open:
        # fully fixable case
        while num_plus < 1:
            # note: runs at most once, but 'while' is logically most correct
            _set_some_open_bond_direction(+1) # IMPLEM; somehow print warning that it acted @@@
            num_plus += 1
            num_plus_open += 1
            num_unset_open -= 1
        while num_minus < 1:
            # note: runs at most once
            _set_some_open_bond_direction(+1) # IMPLEM; somehow print warning that it acted @@@
            num_minus += 1
            num_minus_open += 1
            num_unset_open -= 1
        assert not (num_unset_real or num_plus != 1 or num_minus != 1)
        # not still bad, so declare atom as ok
        return None

    # otherwise we can't fully fix things.

    assert (num_unset_real or num_plus != 1 or num_minus != 1)
    res = _ATOM_HAS_ERROR, "bond direction error"
        # not sure how best to describe it
        
    return res # from _fix_atom

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
