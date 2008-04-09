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

from utilities.constants import average_value

from model.elements import Pl5, Singlet

from utilities import debug_flags
##from utilities.constants import MODEL_PAM5

##from dna.updater.dna_updater_prefs import pref_dna_updater_convert_to_PAM3plus5

import foundation.env as env
from utilities.Log import redmsg, graymsg

from model.bond_constants import find_bond

# ==

def Pl_pos_from_neighbor_PAM3plus5_data(
        bond_directions_to_neighbors,
        remove_data_from_neighbors = False,
        ladders_dict = None
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
    
    @see: related method (stores data in the other direction),
          _f_Pl_store_position_into_Ss3plus5_data

    @see: a similar function for Gv [nim]
    """
    proposed_posns = []
    
    for dirto, ss in bond_directions_to_neighbors:
        if ss.element.role == 'strand':
            # (avoid bondpoints or (erroneous) non-PAM or axis atoms)
            pos = ss._f_recommend_PAM3plus5_Pl_abs_position(
                    - direction,
                    remove_data = remove_data_from_neighbors,
                    make_up_position_if_necessary = True,
                    ladders_dict = ladders_dict
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
