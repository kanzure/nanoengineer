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

# ==

def Pl_pos_from_neighbor_PAM3plus5_data(
        bond_directions_to_neighbors,
        remove_data_from_neighbors = False
    ): #bruce 080402
    """

    @see: related method (stores data in the other direction),
          _f_Pl_store_position_into_Ss3plus5_data
    """
    proposed_posns = []
    
    for dirto, ss in bond_directions_to_neighbors:
        if ss.element.role == 'strand':
            # (avoid bondpoints or (erroneous) non-PAM or axis atoms)
            pos = ss._f_recommend_PAM3plus5_Pl_abs_position(
                    - direction,
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
