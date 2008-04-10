# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
pam3plus5_ops.py - PAM3+5 conversion helpers that modify model objects
(but that are not writemmp-specific -- those have their own module)

@author: Bruce (based on algorithms proposed by Eric D)
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

Reference and explanation for PAM3+5 conversion process and formulas:

http://www.nanoengineer-1.net/privatewiki/index.php?title=PAM-3plus5plus_coordinates
"""

# WARNING: this list of imports must be kept fairly clean,
# especially of anything from dna module. For explanation
# see import comment near top of PAM_Atom_methods.py.
# [bruce 080409]

from utilities.constants import average_value
from utilities.constants import Pl_STICKY_BOND_DIRECTION

from model.elements import Pl5, Singlet

from utilities import debug_flags
##from utilities.constants import MODEL_PAM5

##from dna.updater.dna_updater_prefs import pref_dna_updater_convert_to_PAM3plus5

import foundation.env as env
from utilities.Log import redmsg, graymsg

from model.bond_constants import find_bond, find_Pl_bonds

# ==

def Pl_pos_from_neighbor_PAM3plus5_data(
        bond_directions_to_neighbors,
        remove_data_from_neighbors = False
    ): #bruce 080402
    """
    Figure out where a new Pl atom should be located
    based on the PAM3plus5_data (related to its position)
    in its neighbor Ss3 or Ss5 atoms (whose positions are assumed correct).
    (If the neighbors are Ss5 it's because they got converted from Ss3
     recently, since this info is normally only present on Ss3 atoms.)

    Assume the neighbors are in DnaLadders with up to date baseframe info
    already computed and stored. This may not be checked, and out of date
    info would cause hard-to-notice bugs.

    @return: new absolute position, or None if we can't compute one (error).

    @see: related method (stores data in the other direction),
          _f_Pl_store_position_into_Ss3plus5_data

    @see: analogous function for Gv: Gv_pos_from_neighbor_PAM3plus5_data
    """
    proposed_posns = []
    
    for direction_to, ss in bond_directions_to_neighbors:
        if ss.element.role == 'strand':
            # (avoid bondpoints or (erroneous) non-PAM or axis atoms)
            pos = ss._f_recommend_PAM3plus5_Pl_abs_position(
                    - direction_to,
                    remove_data = remove_data_from_neighbors,
                    make_up_position_if_necessary = True
             )
            if pos is None:
                # can happen in theory, in spite of
                # make_up_position_if_necessary = True,
                # if ss is not a valid atom for this;
                # but the loop above tries not to call it then,
                # so this should not happen unless there are bugs.
                print "fyi: _f_recommend_PAM3plus5_Pl_abs_position returned None for %r" % ss
                    # remove when works if routine; leave in if never seen, to notice bugs
            else:
                proposed_posns.append(pos)
        continue

    if not proposed_posns:
        # neither neighbor was able to make up a position -- error.
        # caller might have ways of handling this, but we don't...
        print "bug: Pl_pos_from_neighbor_PAM3plus5_data can't compute pos for %r" % self
        return None

    if len(proposed_posns) == 1:
        # optimization
        return proposed_posns[0]

    return average_value( proposed_posns)

# ==

def kill_Pl_and_rebond_neighbors(atom):
    # note: modified and moved here [bruce 080408] from function
    # _convert_Pl5 in obsolete file convert_from_PAM5.py
    # [written/debugged/tested there, bruce 080327 or earlier]
    """
    Assume atom is a live and correctly structured Pl5 atom
    (but also check this for safety, at least for now).
    
    If atom's neighbors have the necessary structure
    (Ss-Pl-Ss or X-Pl-Ss, with fully set and consistent bond_directions),
    then kill atom, replacing its bonds with a direct bond
    between its neighbors (same bond_direction).

    Summarize results (ok or error) to history. ### REVIEW
    """
    assert atom.element is Pl5 # remove when works
    assert not atom.killed()
    
    # could also assert no dna updater error

    # Note: we optimize for the common case (nothing wrong, conversion happens)

    ### NOTE: many of the following checks have probably also been done by
    # calling code before we get here. Optimize this sometime. [bruce 080408]
    
    bonds = atom.bonds
    
    # change these during the loop
    bad = False
    saw_plus = saw_minus = False
    num_bondpoints = 0
    neighbors = []
    direction = None # KLUGE: set this during loop, but use it afterwards too

    for bond in bonds:
        other = bond.other(atom)
        neighbors += [other]
        element = other.element
        direction = bond.bond_direction_from(atom)
        
        if direction == 1:
            saw_plus = True
        elif direction == -1:
            saw_minus = True
        
        if element is Singlet:
            num_bondpoints += 1
        elif element.symbol in ('Ss3',): ## 'Ss5'): # [in the 080408 copy, will always be Ss3 AFAIK]
            pass
        else:
            bad = True
        continue

    if not (len(bonds) == 2 and saw_minus and saw_plus and num_bondpoints < 2):
        bad = True

    if bad:
        summary_format = \
            "Warning: dna updater left [N] Pl5 pseudoatom(s) unconverted"
        env.history.deferred_summary_message( redmsg(summary_format) ) # orange -> red [080408]
        return

    del saw_plus, saw_minus, num_bondpoints, bad    

    # Now we know it is either Ss-Pl-Ss or X-Pl-Ss,
    # with fully set and consistent bond_directions.
    
    # But we'd better make sure the neighbors are not already bonded!
    #
    # (This is weird enough to get its own summary message, which is red.
    #  Mild bug: we're not also counting it in the above message.)
    #
    # (Note: there is potentially slow debug code in rebond which is
    #  redundant with this. It does a few other things too that we don't
    #  need, so if it shows up in a profile, just write a custom version
    #  for this use. ### OPTIM)

    n0, n1 = neighbors
    del neighbors

    b0, b1 = bonds
    del bonds # it might be mutable and we're changing it below,
        # so be sure not to use it again
    
    if find_bond(n0, n1):
        summary_format = \
            "Error: dna updater noticed [N] Pl5 pseudoatom(s) whose neighbors are directly bonded"
        env.history.deferred_summary_message( redmsg(summary_format) )
        return
        
    # Pull out the Pl5 and directly bond its neighbors,
    # reusing one of the bonds for efficiency.
    # (This doesn't preserve its bond_direction, so set that again.)

    # Kluge: the following code only works for n1 not a bondpoint
    # (since bond.bust on an open bond kills the bondpoint),
    # and fixing that would require inlining and modifying a
    # few Atom methods,
    # so to avoid this case, reverse everything if needed.    
    if n1.element is Singlet:
        direction = - direction
        n0, n1 = n1, n0
        b0, b1 = b1, b0
        # Note: bonds.reverse() might modify atom.bonds itself,
        # so we shouldn't do it even if we didn't del bonds above.
        # (Even though no known harm comes from changing an atom's
        #  order of its bonds. It's not reviewed as a problematic
        #  change for an undo snapshot, though. Which is moot here
        #  since we're about to remove them all. But it still seems
        #  safer not to do it.)
        pass

##    # save atom_posn before modifying atom (not known to be needed), and
    # set atom.atomtype to avoid bugs in reguess_atomtype during atom.kill
    # (need to do that when it still has the right number of bonds, I think)
##    atom_posn = atom.posn()
    atom.atomtype # side effect: set atomtype

    old_nbonds_neighbor1 = len(n1.bonds) # for assert
    old_nbonds_neighbor0 = len(n0.bonds) # for assert
    
    b1.bust(make_bondpoints = False) # n1 is now missing one bond; so is atom
    b0.rebond(atom, n1) # now n1 has enough bonds again; atom is missing both bonds

    assert len(atom.bonds) == 0, "Pl %r should have no bonds but has %r" % (atom, atom.bonds)
    assert not atom.killed()

    assert len(n1.bonds) == old_nbonds_neighbor1
    assert len(n0.bonds) == old_nbonds_neighbor0

##    # KLUGE: we know direction is still set to the direction of b1 from atom
##    # (since b1 was processed last by the for loop above),
##    # which is the overall direction from n0 thru b0 to atom thru b1 to n1,
##    # so use this to optimize recording the Pl info below.
##    # (Of course we really ought to just rewrite this whole conversion in Pyrex.)
##    
##    ## assert direction == b1.bond_direction_from(atom) # too slow to enable by default
##
##    # not needed, rebond preserves it:
##    ## b0.set_bond_direction_from(n0, direction)
##    ## assert b0.bond_direction_from(n0) == direction # too slow to enable by default
##        
##    # now save the info we'll need later (this uses direction left over from for-loop)
##
##    if n0.element is not Singlet:
##        _save_Pl_info( n0, direction, atom_posn)
##    
##    if n1.element is not Singlet:
##        _save_Pl_info( n1, - direction, atom_posn) # note the sign on direction

    # get the Pl atom out of the way

    atom.kill()
##        # (let's hope this happened before an Undo checkpoint ever saw it --
##        #  sometime verify that, and optimize if it's not true)
    
    # summarize our success -- we'll remove this when it becomes the default,
    # or condition it on a DEBUG_DNA_UPDATER flag ###

    debug_flags.DEBUG_DNA_UPDATER # for use later
    
    summary_format = \
        "Note: dna updater removed [N] Pl5 pseudoatom(s) while converting to PAM3+5"
    env.history.deferred_summary_message( graymsg(summary_format) )
    
    return

# ==

def insert_Pl_between(s1, s2): #bruce 080409/080410
    """
    Assume s1 and s2 are directly bonded atoms, which can each
    be Ss3 or Ss5 (PAM strand sugar atoms) or bondpoints
    (but not both bondpoints -- impossible since such can never be
     directly bonded).
    
    Insert a Pl5 between them (bonded to each of them, replacing
    their direct bond), set it to have non-definitive position,
    and return it.

    @note: inserting Pl5 between Ss5-X is only correct at one end
           of a PAM5 strand, but we depend on the caller to check this
           and only call us if it's correct (since we just insert it
           without checking).

    @return: the Pl5 atom we made. (Never returns None. Errors are either
             not detected or cause exceptions.)
    """
    direct_bond = find_bond(s1, s2)
    assert direct_bond
    direction = direct_bond.bond_direction_from(s1) # from s1 to s2

    # Figure out which atom the Pl sticks to (joins the chunk of).
    # Note: the following works even if s1 or s2 is a bondpoint,
    # which is needed for putting a Pl at the end of a newly-PAM5 strand.
    # But whether to actually put one there is up to the caller --
    # it's only correct at one end, but this function will always do it.
    if direction == Pl_STICKY_BOND_DIRECTION:
        Pl_prefers = [s2, s1]
    else:
        Pl_prefers = [s1, s2]
    # The Pl sticks to the first thing in Pl_prefers which is not a bondpoint
    # (which always exists, since two bondpoints can't be bonded):
    # (see also the related method Pl_preferred_Ss_neighbor())
    Pl_sticks_to = None # for pylint
    for s in Pl_prefers:
        if not s.is_singlet():
            Pl_sticks_to = s
            break
        continue

    # break the old bond
    direct_bond.bust(make_bondpoints = False)

    # make the new Pl atom
    Atom = s1.__class__
        # kluge to avoid import of chem.py, for now
        # (though that would probably be ok (at least as a runtime import)
        #  even though it might expand the import cycle graph)
        # needs revision if we introduce Atom subclasses
        # TODO: check if this works when Atom is an extension object
        # (from pyrex atoms)
    chunk = Pl_sticks_to.molecule
    pos = (s1.posn() + s2.posn()) / 2.0
        # position will be corrected by caller before user sees it
    Pl = Atom('Pl5', pos, chunk)
    Pl._f_Pl_posn_is_definitive = False
        # tell caller it needs to, and is allowed to, correct pos

    # bond it to s1 and s2
    from model.bonds import bond_atoms_faster
    from model.bond_constants import V_SINGLE
        # runtime imports, since we're imported indirectly by chem.py
    b1 = bond_atoms_faster(Pl, s1, V_SINGLE)
    b2 = bond_atoms_faster(Pl, s2, V_SINGLE)
    
    # set bond directions: s1->Pl->s2 same as s1->s2 was before
    b1.set_bond_direction_from(s1, direction)
    b2.set_bond_direction_from(Pl, direction)
    
    return Pl # or None if error? caller assumes not possible, so do we

def find_Pl_between(s1, s2): #bruce 080409
    """
    Assume s1 and s2 are Ss3 and/or Ss5 atoms which
    might be directly bonded or might have a Pl5 between them.
    If they are directly bonded, return None.
    If they have a Pl between them, return it.
    If neither is true, raise an exception.
    """
    # optimize for the Pl being found
    bond1, bond2 = find_Pl_bonds(s1, s2)
    if bond1:
        return bond1.other(s1)
    else:
        assert find_bond(s1, s2)
        return None
    pass
    
# ==

def Gv_pos_from_neighbor_PAM3plus5_data(
        neighbors,
        remove_data_from_neighbors = False
     ):
    #bruce 080409, modified from Pl_pos_from_neighbor_PAM3plus5_data
    """
    Figure out where a new Gv atom should be located
    based on the PAM3plus5_data (related to its position)
    in its neighbor Ss3 or Ss5 atoms (whose positions are assumed correct).
    (If the neighbors are Ss5 it's because they got converted from Ss3
     recently, since this info is normally only present on Ss3 atoms.)

    Assume the neighbors are in the same basepair in a DnaLadder
    with up to date baseframe info already computed and stored.
    This may not be checked, and out of date
    info would cause hard-to-notice bugs.

    @return: new absolute position, or None if we can't compute one (error).
    
    @see: related method (stores data in the other direction),
          _f_Gv_store_position_into_Ss3plus5_data

    @see: analogous function for Pl: Pl_pos_from_neighbor_PAM3plus5_data
    """
    proposed_posns = []
    
    for ss in neighbors:
        assert ss.element.role == 'strand'
            # (avoid bondpoints or (erroneous) non-PAM or axis atoms)
        pos = ss._f_recommend_PAM3plus5_Gv_abs_position(
                remove_data = remove_data_from_neighbors,
                make_up_position_if_necessary = True
         )
        if pos is None:
            # can happen in theory, in spite of
            # make_up_position_if_necessary = True,
            # if ss is not a valid atom for this;
            # but the loop above tries not to call it then,
            # so this should not happen unless there are bugs.
            print "fyi: _f_recommend_PAM3plus5_Gv_abs_position returned None for %r" % ss
                # remove when works if routine; leave in if never seen, to notice bugs
        else:
            proposed_posns.append(pos)
        continue

    if not proposed_posns:
        # neither neighbor was able to make up a position -- error.
        # caller might have ways of handling this, but we don't...
        print "bug: Gv_pos_from_neighbor_PAM3plus5_data can't compute pos for %r" % self
        return None

    if len(proposed_posns) == 1:
        # optimization
        return proposed_posns[0]

    return average_value( proposed_posns)

# ==

# TODO: fix a dna updater bug in which (I am guessing) reading an mmp file with Ss3-Pl5-Ss3
# makes a DnaChain containing only the Pl5, which has no baseatoms,
# and assertfails about that. I have an example input file, Untitled-bug-Ss3-Pl5-Ss3.mmp,
# for which I guess this is the issue (not verified).
# Low priority, since no such files (or lone Pl5 atoms in that sense) will normally exist.
# OTOH, this bug seems to ruin the session, by making a DnaLadder with no strand rails
# which never goes away even when we read more than one new file afterwards.
# Correct fix is to kill that Pl and (even lower pri) put its position data onto its neighbors.
# Or, leave it there but don't make it into a chain.
# [bruce 080402 comment]

# end
