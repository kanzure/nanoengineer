# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
fix_bond_directions.py - dna updater helper functions

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from model.elements import Singlet

import foundation.env as env
from utilities.Log import orangemsg
from platform_dependent.PlatformDependent import fix_plurals

from dna.updater.dna_updater_prefs import pref_print_bond_direction_errors

from model.elements import Pl5

# ==

_DEBUG_PRINT_BOND_DIRECTION_ERRORS = False # set later to match a debug_pref

try:
    _global_direct_error_atoms
except:
    _global_direct_error_atoms = {}
    # maps atom.key -> atom, for all atoms that have direct dna updater errors
    # (as opposed to error codes propogated from other atoms in their basepair)
    # at the end of a dna updater run. Coming into a run, we'll ignore this info
    # for any changed_atom but believe it for all other atoms. We'll then update it,
    # and use it to update all atom's error codes (direct or propogated).
    #
    # note: we optimize for this being empty, since that should be the usual case.

try:
    _all_error_atoms_after_propogation
except:
    _all_error_atoms_after_propogation = {}

# ==

def fix_local_bond_directions( changed_atoms):
    """
    Fix local directional bond issues, namely:
    - directional bond chain branches (illegal)
    - missing bond directions (when fixable locally -- most are not)
    - inconsistent bond directions
    But for most of these, "fix" just means "mark them as an error".
    We will only change bond direction on open bonds;
    we'll never break any bonds or change bond direction
    on any real bonds (unless it's illegal given the bonded atomtypes).
    """

    global _DEBUG_PRINT_BOND_DIRECTION_ERRORS
    _DEBUG_PRINT_BOND_DIRECTION_ERRORS = pref_print_bond_direction_errors()

    new_error_atoms = {} # note: only used for its length in a warning message

    # Find new errors (or the lack of them) on changed_atoms,
    # updating _global_direct_error_atoms to be current for all atoms.
    # Then propogate errors within basepairs, and make sure all atoms
    # have correct error data, and call changeapp as needed when we
    # change this. This scheme is chosen mainly to optimize the case
    # when the number of atoms with errors is small or zero.

    for atom in changed_atoms.itervalues():
        # look for new errors
        error_info = None # might be changed below
        if atom.element is Singlet:
            pass # handle these as part of their base atom
        elif not atom.element.bonds_can_be_directional:
            # note: we needn't worry here about nondirectional bonds
            # with a direction set. Those can't hurt us except on directional
            # elements, dealt with below. @@@DOIT
            pass # optimization
        elif atom.killed():
            pass # not sure this ever happens
        else:
            # note: at this stage we might have Ss or Pl;
            # valence has not been checked (in code as of 080123)

            # catch specially labelled AssertionErrors from
            # _fix_atom_or_return_error_info;
            # turn them into errors, history summaries
            # (needed here? or done more generally for them all, elsewhere?),
            # and console prints
            try:
                error_info = _fix_atom_or_return_error_info(atom)
            except AssertionError, e:
                e_string = "%s" % (e,)
                if not e_string.startswith("__ERROR:"):
                    raise
                # it's a specially labelled exception meant to become
                # an updater error string
                print "%s: %r (neighbors: %r)" % (e_string, atom, atom.neighbors())
                # TODO: history summary needed? better error_data string?
                prefix = "" # STUB
                error_data = prefix + e_string[len("__ERROR:"):].strip()
                error_info = _ATOM_HAS_ERROR, error_data
                pass

        if error_info:
            error_type, error_data = error_info
            assert error_type == _ATOM_HAS_ERROR
            assert error_data and type(error_data) == type("")
            if _DEBUG_PRINT_BOND_DIRECTION_ERRORS:
                print "bond direction error for %r: %s" % (atom, error_data)
                print
            _atom_set_dna_updater_error( atom, error_data)
            atom.molecule.changeapp(0) #k probably not needed
            new_error_atoms[atom.key] = atom
            _global_direct_error_atoms[atom.key] = atom
        else:
            _atom_clear_dna_updater_error( atom)
            _global_direct_error_atoms.pop(atom.key, None)
        continue

    if new_error_atoms: #e if we print more below, this might be only interesting for debugging, not sure
        # maybe: move later since we will be expanding this set; or report number of base pairs
        msg = "Warning: dna updater noticed %d pseudoatom(s) with bond direction errors" % len(new_error_atoms)
        msg = fix_plurals(msg)
        env.history.orangemsg(msg)

    global _all_error_atoms_after_propogation
    old_all_error_atoms_after_propogation = _all_error_atoms_after_propogation

    new_all_error_atoms_after_propogation = {}

    for atom in _global_direct_error_atoms.itervalues():
        for atom2 in _same_base_pair_atoms(atom):
            new_all_error_atoms_after_propogation[atom2.key] = atom2

    _all_error_atoms_after_propogation = new_all_error_atoms_after_propogation

    for atom in old_all_error_atoms_after_propogation.itervalues():
        if atom.key not in new_all_error_atoms_after_propogation:
            if atom._dna_updater__error: # should always be true
                del atom._dna_updater__error
                if not atom.killed():
                    atom.molecule.changeapp(0) #k needed?

    for atom in new_all_error_atoms_after_propogation.itervalues():
        if atom.key not in _global_direct_error_atoms:
            _atom_set_dna_updater_error( atom, PROPOGATED_DNA_UPDATER_ERROR)
                # note: the propogated error is deterministic,
                # since only the fact of error is propogated,
                # not the error string itself, which could differ
                # on different sources of propogated error.
            atom.molecule.changeapp(0)

    return # from fix_local_bond_directions

def _same_base_pair_atoms(atom):
    """
    Defining a base pair as whatever portion of Ss-Ax-Ss exists,
    return a list of atoms in the same base pair as atom.
    At minimum this is atom itself. Pl atoms are not considered
    to be part of the base pair. (This is used only for propogating
    detected dna updater errors; for that use it's important to propogate
    across rung bonds, so that strand and axis chains cover the same set of
    base pairs.)

    @note: since we are used to report errors, we have to work even
    if there are arbitrary errors, including errors in how many atoms of
    what elements are bonded to a given atom. But, we don't want to consider
    too many atoms to be part of one base pair... or do we? For now, we will
    propogate errors across any number of "rung bonds", regardless
    of how many atoms this reaches.
    """
    # POSSIBLE OPTIM: in current calling code, atom itself needs to be part of
    # our return value. This could be revised, permitting this to return
    # a constant value of () in some cases.

    # implem note: for speed, we don't use the utility function transclose,
    # and we use special case optimizations based on the kind of atoms and
    # bonds we are looking for. [implem rewritten, bruce 080304]
    look_at_these = {atom.key : atom} # atoms we still need to explore
    found = {} # atoms found in prior steps
    have_role = atom.element.role # role of all atoms in look_at_these
        # (where strand implies not Pl, in this loop but not in general;
        #  we take no steps to exclude it explicitly, since it will not
        #  be included in correct structures due to only crossing
        #  strand-axis bonds)
    # look for neighbor atoms of alternating roles
    while look_at_these:
        found.update(look_at_these)
        next = {}
        next_role = (have_role == 'axis' and 'strand' or 'axis')
        for atom1 in look_at_these.itervalues():
            assert have_role == atom1.element.role # remove when works
            for atom2 in atom1.neighbors():
                # maybe add atom2 to next, if suitable and not in found
                if atom2.element.role == next_role and not found.has_key(atom2.key):
                    next[atom2.key] = atom2
                continue
            continue
        look_at_these = next
        have_role = next_role
        continue
    return found.values()
##    if atom.element.role == 'strand':
##        axis_atom = atom.axis_neighbor() # might be None (for Pl or single-stranded)
##        if not axis_atom:
##            return (atom,)
##    elif atom.element.role == 'axis':
##        axis_atom = atom
##    else:
##        return (atom,)
##    return [axis_atom] + axis_atom.strand_neighbors()

# ==

# error type codes (may be revised)
_ATOM_HAS_ERROR = 1

def _fix_atom_or_return_error_info(atom):
    """
    [private helper for fix_local_bond_directions]

    note: at this stage we might have Ss or Pl;
    valence has not been checked (in code as of 080123)

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

    neighbors = []

    for bond in atom.bonds:
        direction = bond.bond_direction_from(atom)
        neighbor = bond.other(atom)
            # we'll use this to inline & optimize both
            # bond.is_directional and bond.is_open_bond,
            # since we know enough about atom that only neighbor
            # can affect their values.
        neighbors += [neighbor]
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

    # first check for a legal set of neighbors [new feature, bruce 080304];
    # for simpler code, we'll report errors as exceptions with unvarying text
    # and a standard prefix recognized by caller, and let caller convert those
    # to error strings (and also print them with name of specific atom). #### @@@@@ DOIT
    #
    # (note, someday this might be done more generally by an earlier
    #  updater stage)
    # (note, this is not complete, just enough to catch some errors
    #  noticed in test files on 080304)

    if atom.element is Pl5:
        # permit only strand atoms (not Pl) and bondpoints as neighbors, valence 2
        assert len(atom.bonds) == 2, "__ERROR: Pl valence must be 2"
        for neighbor in neighbors:
            element = neighbor.element
            assert element is Singlet or \
                   (element.role == 'strand' and
                    not element is Pl5), \
                    "__ERROR: Pl has non-permitted neighbor element %s" % element.symbol
    elif atom.element.role == 'strand':
        # other strand atoms (Ss or equivalent) must have 2 bonds to other strand atoms (Pl or not) or bondpoints,
        # and 1 bond to an axis atom or a bondpoint or (doesn't yet happen) 1 or 2 unpaired base atoms.
        num_bondpoint = 0
        num_strand = 0
        num_axis = 0
        num_unpaired_base = 0
        for neighbor in neighbors:
            element = neighbor.element
            role = element.role
            if element is Singlet:
                num_bondpoint += 1
            elif role == 'strand':
                num_strand += 1
            elif role == 'axis':
                num_axis += 1
            elif role == 'unpaired-base':
                num_unpaired_base += 1
            else:
                assert 0, \
                       "__ERROR: strand sugar has non-permitted " \
                       "neighbor element %s" % element.symbol
            continue
        assert num_strand <= 2, \
               "__ERROR: strand sugar has more than 2 strand bonds"
        assert num_axis <= 1, \
               "__ERROR: strand sugar has more than one axis bond"
        assert num_unpaired_base <= 2, \
               "__ERROR: strand sugar has more than two unpaired base neighbors"
        assert num_bondpoint + num_strand + num_axis + \
               (not not num_unpaired_base) == 3, \
               "__ERROR: strand sugar has wrong number of bonds"
    else:
        # should never happen, so no valence or neighbor checks are
        # implemented here, but print a nim warning
        print "BUG: fix_bond_directions got %r of unexpected element %s" % (atom, element.symbol)
        msg = "BUG: fix_bond_directions got [N] atom(s) of unexpected element %s" % element.symbol
        summary_format = redmsg( msg )
        env.history.deferred_summary_message(summary_format)
        pass

    # now look at actual bond directions.
    #
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

    def _dir(bond): # for assertions (could be done as a lambda)
        return bond.bond_direction_from(atom)

    assert num_plus == _number_of_bonds_with_direction(atom, +1), "%r" % (num_plus, atom, atom.bonds, map( _dir, atom.bonds))
    assert num_minus == _number_of_bonds_with_direction(atom, -1), "%r" % (num_minus, atom, atom.bonds, map( _dir, atom.bonds))

    if num_plus > 1 or num_minus > 1 or num_plus + num_minus + num_unset_real > 2:
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
            _unset_some_open_bond_direction(atom, +1)
            num_plus_open -= 1
            num_plus -= 1
            assert num_plus == _number_of_bonds_with_direction(atom, +1), "%r" % (num_plus, atom, atom.bonds, map( _dir, atom.bonds))
            assert num_minus == _number_of_bonds_with_direction(atom, -1), "%r" % (num_minus, atom, atom.bonds, map( _dir, atom.bonds))

        while num_minus_open and num_minus > 1:
            _unset_some_open_bond_direction(atom, -1)
            num_minus_open -= 1
            num_minus -= 1
            assert num_plus == _number_of_bonds_with_direction(atom, +1), "%r" % (num_plus, atom, atom.bonds, map( _dir, atom.bonds))
            assert num_minus == _number_of_bonds_with_direction(atom, -1), "%r" % (num_minus, atom, atom.bonds, map( _dir, atom.bonds))

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
    assert num_minus <= 1, \
           "num_minus = %r, num_minus_open = %r, num_minus_real = %r, atom = %r, bonds = %r, dirs = %r" % \
           (num_minus, num_minus_open, num_minus_real, atom, atom.bonds, map( _dir, atom.bonds) )

    if (1 - num_plus) + (1 - num_minus) <= num_unset_open:
        # fully fixable case (given that we're willing to pick an open bond arbitrarily)
        while num_plus < 1:
            # note: runs at most once, but 'while' is logically most correct
            _set_some_open_bond_direction(atom, +1)
            num_plus += 1
            num_plus_open += 1
            num_unset_open -= 1
        while num_minus < 1:
            # note: runs at most once
            _set_some_open_bond_direction(atom, -1)
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

    return res # from _fix_atom_or_return_error_info

# ==

def _set_some_open_bond_direction(atom, direction):
    """
    Find a directional open bond on atom with no bond direction set
    (error if you can't), and set its bond direction to the specified one.
    """
    assert direction in (-1, 1)

    didit = False
    for bond in atom.bonds:
        if bond.is_open_bond() and \
           bond.is_directional() and \
           not bond.bond_direction_from(atom):
            bond.set_bond_direction_from(atom, direction)
            didit = True
            break
        continue
    assert didit

    summary_format = "Warning: dna updater set bond direction on [N] open bond(s)"
    env.history.deferred_summary_message( orangemsg(summary_format) )
        # todo: refactor so orangemsg is replaced with a warning option
        # review: should we say in how many cases we picked one of several open bonds arbitrarily?
    return

def _unset_some_open_bond_direction(atom, direction):
    """
    Find an open bond on atom with the specified bond direction set
    (error if you can't), and unset its bond direction.
    """
    assert direction in (-1, 1)

    didit = False
    for bond in atom.bonds:
        if bond.is_open_bond() and \
           bond.bond_direction_from(atom) == direction: # bugfix 080201, care which direction is set, not just that some dir was set
            bond.clear_bond_direction()
            didit = True
            break
        continue
    assert didit

    summary_format = "Warning: dna updater unset bond direction on [N] open bond(s)"
    env.history.deferred_summary_message( orangemsg(summary_format) )
    return

def _number_of_bonds_with_direction(atom, direction): # for asserts
    count = 0
    for bond in atom.bonds:
        if bond.bond_direction_from(atom) == direction:
            count += 1
    return count

def _clear_illegal_direction(bond):
    """
    [private helper for _fix_atom_or_return_error_info]

    bond has a direction but is not directional
    (since one of its atoms does not permit directional bonds,
     e.g. it might be an Ss-Ax bond).
    Report and immediately fix this error.

    @type bond: Bond
    """
    bond.clear_bond_direction()

    summary_format = "Warning: dna updater cleared [N] bond direction(s) on pseudoelements that don't permit one"
    env.history.deferred_summary_message( orangemsg(summary_format) )
    return

# ==

# the following will probably be moved into a separate file in dna_model,
# both on general principles (it might become a file for an Atom subclass,
# for a common superclass of StrandAtom and AxisAtom),
# or if an import cycle exists from chem.py import of these.
# [bruce 080204]

PROPOGATED_DNA_UPDATER_ERROR = 'error elsewhere in basepair'

def _atom_set_dna_updater_error(atom, error_string): # turn into method on an Atom subclass
    """
    [private helper, will turn into friend method]
    Low-level setter for atom._dna_updater__error.
    Caller is responsible for atom.molecule.changeapp(0) if this is needed.
    (It is needed due to effect on atom color, unless caller knows
     it is done by other code.)
    """
    atom._dna_updater__error = error_string
    if not error_string:
        del atom._dna_updater__error # optimization
    return

def _atom_clear_dna_updater_error( atom):
    """
    [private helper, will turn into friend method]
    Low-level clear for atom._dna_updater__error.
    Caller is responsible for atom.molecule.changeapp(0) if this is needed.
    (It is needed due to effect on atom color, unless caller knows
     it is done by other code.)
    """
    if atom._dna_updater__error:
        del atom._dna_updater__error
    assert not atom._dna_updater__error # verify class default value is ok
    # otherwise it's ok to assume it's not set (doesn't matter much anyway)
    return

def _f_detailed_dna_updater_error_string( atom):
    """
    [friend function for use by Atom.dna_updater_error_string,
     which might be moved onto the same Atom subclass as
     _atom_set_dna_updater_error should be moved to]

    Assuming atom._dna_updater__error == PROPOGATED_DNA_UPDATER_ERROR,
    return a more complete error string for atom
    (perhaps containing internal newlines)
    which lists the errors directly assigned to other atoms
    in the same basepair.
    """

    ### REVIEW: should we be documented to work even before propogation
    # actually occurs?

    assert atom._dna_updater__error == PROPOGATED_DNA_UPDATER_ERROR

    # find the sources of direct error
    direct_errors = {} # maps atom2 -> value of _dna_updater__error
    for atom2 in _same_base_pair_atoms(atom):
        error = atom2._dna_updater__error
        assert error # otherwise propogation did not finish or had a bug
        if error != PROPOGATED_DNA_UPDATER_ERROR:
            direct_errors[atom2] = error
    assert atom not in direct_errors
    assert direct_errors # otherwise where did the error come from?
        # (could happen if unsetting obs error strings has a bug)
    error_reports = [ "%s: %s" % (str(atom2), error)
                      for atom2, error in direct_errors.items() ]
    if len(error_reports) <= 1:
        header = "error elsewhere in basepair:"
    else:
        error_reports.sort() # todo - should probably use atom key numbers as sort order
        header = "errors elsewhere in basepair:"
    error_reports.insert(0, header)
    res = "\n".join( error_reports)
    # todo: indicate visual direction? highlight error-source atoms?
    return res

# end
