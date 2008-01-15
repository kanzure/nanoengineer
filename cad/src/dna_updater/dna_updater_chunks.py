# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_chunks.py - enforce rules on chunks containing changed PAM atoms

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from state_utils import transclose

from dna_updater_globals import ignore_new_changes

from dna_updater_constants import DEBUG_DNA_UPDATER

from dna_model.DnaMarker import _f_get_homeless_dna_markers

from dna_updater_find_chains import find_axis_and_strand_chains_or_rings

from dna_updater_ladders import dissolve_or_fragment_invalid_ladders
from dna_updater_ladders import make_new_ladders, merge_ladders


# ==

def update_PAM_chunks( changed_atoms):
    """
    Update chunks containing changed PAM atoms, ensuring that
    PAM atoms remain divided into AxisChunks and StrandChunks
    in the right way. Also update DnaMarkers as needed.

    @param changed_atoms: an atom.key -> atom dict of all changed atoms
                          that this update function needs to consider,
                          which includes no killed atoms. WE ASSUME
                          OWNERSHIP OF THIS DICT and modify it in
                          arbitrary ways.
                          Note: in present calling code [071127]
                          this dict might include atoms from closed files.

    @return: list of all newly made DnaLadderRailChunks (or modified ones,
             if that's ever possible)
    """

    # see scratch file for comments to revise and bring back here...

    ignore_new_changes("as update_PAM_chunks starts", changes_ok = False )

    # Move the chain markers whose atoms got killed, onto atoms which remain
    # alive in the same old wholechains. (Their old wholechain objects still
    # exist within the markers, and can be used to scan their atoms even though
    # some are dead or their bonding has changed. The markers use them to help
    # decide where and how to move.)
    # (The markers can't yet also correlate their old chain to new chain
    #  direction, since the new chain is not yet constructed, but they record
    #  private info to help them do that later.)

    homeless_markers = _f_get_homeless_dna_markers() #e rename; pull in the ones touched by changed_atoms @@@
    
    live_markers = []
    for marker in homeless_markers:
        still_alive = marker._f_move_to_live_atom_step1() #e rename, doc - it moves, later steps update direction & wholechain
            # move (if possible), and record info (old neighbor atoms?)
            # for later use in determining new baseindex direction advice
            # for new wholechain
        if DEBUG_DNA_UPDATER:
            print "dna updater: moved_step1 marker %r, still_alive = %r" % (marker, still_alive)
        if still_alive:
            live_markers.append(marker)
    del homeless_markers

    ignore_new_changes("from updating DnaMarkers, step1")
        # ignore changes caused by adding/removing marker jigs
        # to their atoms, when the jigs die/move/areborn

##    # warning: all marker-related comments below here need revision, as of 071203 @@@
    
    # make sure invalid DnaLadders are recognized as such in the next step,
    # and dissolved [possible optim: also recorded for later destroy??].
    # also (#e future optim) break long ones at damage points so the undamaged
    # parts needn't be rescanned in the next step.
    #
    # Also make sure that atoms that are no longer in valid ladders
    # (due to dissolved or fragmented ladders) are included below,
    # or that the chains they are in are covered. This is necessary so that
    # the found chains below cover all atoms in every "base pair" (Ss-Ax-Ss)
    # they cover any atom in.
    # This might be done by adding some of their atoms into changed_atoms
    # in the following method.
    
    dissolve_or_fragment_invalid_ladders( changed_atoms)
        # note: this adds atoms (live atoms only) to changed_atoms;
        # see its comments and above comment for details.
    
    # Find the current axis and strand chains (perceived from current bonding)
    # on which any changed atoms reside, but only scanning along atoms
    # not still part of valid DnaLadders. (I.e. leave existing undamaged
    # DnaLadders alone.) (The found chains or rings will be used below to
    # make new DnaChain and DnaLadder objects, and (perhaps combined with
    # preexisting untouched chains) to make new WholeChains and tell the
    # small chains about them.)

    ignore_new_changes("from dissolve_or_fragment_invalid_ladders", changes_ok = False)
    
    axis_chains, strand_chains = find_axis_and_strand_chains_or_rings( changed_atoms)

    ignore_new_changes("from find_axis_and_strand_chains_or_rings", changes_ok = False )

# redundant:
##    # @@@ LOGIC ISSUE for moving markers: ....
##    # ... we need an old complete-chain object...
##    # or we need to move it more incrly, but even then we'd need the object at that time, so now is as a good a time
##    # as any if we have that object. So, these chains in the markers need to be complete chains!
##    # we need to make lists of chain fragments into complete chains and keep those in the markers.
##    # of course we really should keep a single one in a strand or segment object shared by that obj and all markers. ### DOIT
##    #
##    # And when the markers move onto new ladders, the advice (which?) below is needed,
##    # but what if they move onto old ladders,
##    # Q do we need to update the marker situation of those too? ###figureout
##    # A i guess those old ladder rails get
##    # into new whole-chains in that case... so YES. ### DOIT [so in the end we process all changed strands & segs,
##    # we just optim by incorporating unchanged ladder-rungs and ladders into them. We have higher-level chains
##    # whose components are these rungs, which are chains of atoms.]

    #@@@ not sure if still needed: [080114]
    # [@@@ pre-ladder comment:] To help the moving markers know how to advise their new chains about
    # internal baseindex direction coming from their old chains, we first
    # make a dict from atom.key to (new chain id, atom's baseindex in new chain).
    # (We might use it later as well, not sure.)
    # (We keep axis and strand info in one dict for convenience, since both kinds
    #  of markers are in one list we iterate over.)

    #@@@ not sure if still an issue: [080114]
    ### WORRY ABOUT RING WRAPAROUND in this marker code,
    # where it's a current bug -- see scratch file for more info ###FIX @@@

    print "i bet this marker code step2 should now be done after new ladders are made, not before" #### @@@@
# HOW TO UPDATE THIS CODE:
# just do what has to be done before making new ladders (reversing, merging chains, maybe rotating rings)
# to help markers do their later direction-xfer or fixing...
#
# WE MIGHT KEEP THIS
# but i comment it out to mark it as needing revising and maybe deleting. 080114
#
##    new_chain_info = {} #k needed? @@
##
##    for chain in axis_chains + strand_chains:
##        for atom, index in chain.baseatom_index_pairs(): # skips non-base atoms like Pl
##            info = (chain.chain_id(), index)
##            new_chain_info[atom.key] = info
##
##    for marker in live_markers:
##        still_alive = marker._f_move_to_live_atom_step2(new_chain_info)
##            # Note: this also comes up with direction advice for the new chain,
##            # stored in the marker and based on the direction of its new atoms
##            # in its old chain (if enough of them remain adjacent, currently 2);
##            # but the new chain will later take that advice from at most one marker.
##        if DEBUG_DNA_UPDATER:
##            print "dna updater: moved_step2 marker %r, still_alive = %r" % (marker, still_alive)
##        # Note: we needn't record the markers whose atoms are still alive,
##        # since we'll find them all later on a new chain. Any marker
##        # that moves either finds new atoms whose chain has a change
##        # somewhere that leads us to find it (otherwise that chain would
##        # be unchanged and could have no new connection to whatever other
##        # chain lost atoms which the marker was on), or finds none, and
##        # can't move, and either dies or is of no concern to us.
##    del live_markers #k if not, update it with new liveness
##
##    ignore_new_changes("from updating DnaMarkers, step2", changes_ok = False)
##
##    # @@@ LOGIC ISSUE: is the following about new chain fragments, or new/modified whole chains? do it before or after ladders?
##    #
##    # Tell all new chains to take over their atoms and any markers on them,
##    # deciding between competing markers for influencing base indexing
##    # and other settings, and creating new markers as needed.
##    #
##    # (Maybe also save markers for use in later steps, like making or updating
##    #  Segment & Strand objects, and storing all these in DNA Groups.)
##    #
##    # Do axis chains first, so strand chains which need new markers or
##    # direction decisions (etc) can be influenced by their base numbering, order, etc.
##    #
##    # (Future: we might have a concept of "main" and "secondary" strands
##    # (e.g. scaffold vs staples in origami), and if so, we might want to do
##    # all main strands before all secondary ones for the same reason.)
##    
##    # [Possible optim: reuse old chains if nothing has changed.
##    # Not done at present; I'm not sure how rare the opportunity will be,
##    # but I suspect it's rare, in which case, it's not worth the bug risk.]
##    
##    for chain in axis_chains:
##        chain._f_own_atoms()
##
##    for chain in strand_chains:
##        chain._f_own_atoms()# IMPLEM - now these are stubs which always remake markers @@@
##
##    ignore_new_changes("from updating DnaMarkers, own_atoms")
##        # changes are ok since it can add new marker jigs to atoms
##    
##    # That figured out which markers control each chain (and stored the answers in the chains). ###IMPLEM
##    # It also means we no longer need to care about chain.index_direction,
##    # which frees us to permit merging of new and old chains, whose
##    # index_directions might be incompatible at the merge points.
##    # (I think they'll be compatible for new/new merges, but it doesn't matter.)

    # Now use the above-computed info to make new DnaLadders out of the chains
    # we just made (which contain all PAM atoms no longer in valid old ladders),
    # and to merge end-to-end-connected ladders (new/new or new/old) into larger
    # ones, when that doesn't make them too long. We'll reverse chains
    # as needed to make the ones in one ladder correspond in direction, and to
    # standardize their strand bond directions. (There is no longer any need to
    # keep track of index_direction -- it might be useful for new/new ladder
    # merging, but that probably doesn't help us since we also need to handle
    # new/old merging. For now, the lower-level code maintains it for individual
    # chains, and when fragmenting chains above, but discards it for merged
    # chains.)

    # @@@ do we need to rotate smallchains that are rings?

    new_ladders = make_new_ladders(axis_chains, strand_chains)

    ignore_new_changes("from make_new_ladders", changes_ok = False)

    modified_valid_ladders = merge_ladders(new_ladders)
        # note: each returned ladder is either entirely new (perhaps merged),
        # or the result of merging new and old ladders.

    ignore_new_changes("from merge_ladders", changes_ok = False)

    # Now make or remake chunks as needed, so that each ladder-rail is a chunk.
    # This must be done to all newly made or merged ladders (even if parts are old).

    all_new_chunks = []
    
    for ladder in modified_valid_ladders:
        new_chunks = ladder.remake_chunks()
        all_new_chunks.extend(new_chunks)

    ignore_new_changes("from remake_chunks", changes_ok = True)#k changes_ok?

    # Now make new wholechains on modified_valid_ladders,
    # let them own their atoms and markers,
    # and choose their controlling markers.
    # These may have existing DnaSegmentOrStrand objects,
    # or need new ones (made later), and in a later step (not in this function)
    # those objects take over their chunks.
    
    # Note that due to the prior step, any atom in a ladder (new or old)
    # can find its smallchain via its chunk.

    # We'll do axis chains first, in case we want them finalized
    # in figuring out anything about strand markers (not the case for now).
    # For any length-1 axis chains, we'll pick a direction arbitrarily (?),
    # so we can store, for all chains, a pointer to the ladder-index of the
    # chain it connects to (if any).

    # For each kind of chain, the algorithm is handled by this function:
    def algorithm( ladder_to_rails_function ):
        """
        [local helper function]
        Given ladder_to_rails_function to tell us the rails of interest for any
        ladder, for each such rail in modified_valid_ladders,
        find the set of rails to be used in making its WholeChain,
        and a return a list of all such sets found.
        
        To find the neighbor chains, we just use atom.molecule.ladder
        and then look for atom in the rail ends of the same type of rail
        (i.e. the ones found by ladder_to_rails_function).
        """
        toscan_all = {} # maps id(rail) -> rail, for initial set of rails to scan
        for ladder in modified_valid_ladders:
            for rail in ladder_to_rails_function(ladder):
                toscan_all[id(rail)] = rail
        def collector(rail, dict1):
            """
            function for transclose on a single initial rail:
            remove each rail seen from toscan_all if present;
            store neighbor atom pointers in rail,
            and store neighbor rails themselves into dict1
            """
            toscan_all.pop(rail, None)
            rail._f_compute_neighbor_atoms() # called exactly once per rail,
                # per dna updater run which encounters it (whether as a new
                # or preexisting rail); IMPLEM, differs for axis or strand
            for neighbor_atom in rail.neighbor_atoms: # IMPLEM, as len 2 list (??)
                rail1 = _find_rail_of_atom( neighbor_atom, ladder_to_rails_function ) # IMPLEM
                dict1[id(rail1)] = rail1
            return # from collector
        res = [] # elements are data args for WholeChain constructors (or helpers)
        for rail in toscan_all.values(): # not itervalues (modified during loop)
            if id(rail) in toscan_all:
                # (we haven't popped rail yet, in collector)
                rails_for_wholechain = transclose(toscan, collector)
                res.append(rails_for_wholechain)
        return res

    new_wholechains = (
        map( Axis_WholeChain, 
             algorithm( lambda ladder: [ladder.axis_rail] ) ) +
        map( Strand_WholeChain,
             algorithm( lambda ladder: ladder.strand_rails ) )
     )
    ### @@@ DOC and IMPLEM whatever side effects those should have, besides construction:
    #
    # this includes "let them own their atoms and markers,
    # and choose their controlling markers."
    #
    # (REVIEW: maybe use helper funcs so constructors are clean)


    # TODO: use wholechains and markers to revise base indices if needed (if this info is cached outside of wholechains)

    return all_new_chunks, new_wholechains # from update_PAM_chunks

# end

