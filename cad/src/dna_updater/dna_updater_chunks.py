# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_chunks.py - enforce rules on chunks containing changed PAM atoms

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_updater_globals import ignore_new_changes

from dna_updater_constants import DEBUG_DNA_UPDATER

from dna_model.DnaAtomMarker import _f_get_homeless_dna_markers

from dna_updater_find_chains import find_axis_and_strand_chains_or_rings

from dna_updater_ladders import dissolve_or_fragment_invalid_ladders
from dna_updater_ladders import make_new_ladders, merge_ladders


# ==

def update_PAM_chunks( changed_atoms):
    """
    Update chunks containing changed PAM atoms, ensuring that
    PAM atoms remain divided into AxisChunks and StrandSegmentChunks
    in the right way.

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

    # Move the chain markers whose atoms got killed, onto atoms which remain alive
    # but were in the same old chains. (Their old chain objects still exist, in
    # the markers, to help the markers decide where and how to move.)
    # (They can't also correlate their old chain to new chain direction,
    #  since the new chain is not yet known, but they record info to help
    #  them do that later.)

    homeless_markers = _f_get_homeless_dna_markers()
    
    live_markers = []
    for marker in homeless_markers:
        still_alive = marker._f_move_to_live_atom_step1() #e rename, doc
            # move, and record old neighbor atoms for later use
            # in determining new baseindex direction advice for new chain
        if DEBUG_DNA_UPDATER:
            print "dna updater: moved_step1 marker %r, still_alive = %r" % (marker, still_alive)
        if still_alive:
            live_markers.append(marker)
    del homeless_markers

    ignore_new_changes("from updating DnaAtomMarkers, step1")
        # ignore changes caused by adding/removing marker jigs
        # to their atoms, when the jigs die/move/areborn

    # warning: all marker-related comments below here need revision, as of 071203 @@@
    
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
    # make new DnaChain and DnaLadder objects.)

    ignore_new_changes("from dissolve_or_fragment_invalid_ladders", changes_ok = False)
    
    axis_chains, strand_chains = find_axis_and_strand_chains_or_rings( changed_atoms)

    ignore_new_changes("from find_axis_and_strand_chains_or_rings", changes_ok = False )


    # @@@ LOGIC ISSUE for moving markers: ....
    # ... we need an old complete-chain object...
    # or we need to move it more incrly, but even then we'd need the object at that time, so now is as a good a time
    # as any if we have that object. So, these chains in the markers need to be complete chains!
    # we need to make lists of chain fragments into complete chains and keep those in the markers.
    # of course we really should keep a single one in a strand or segment object shared by that obj and all markers. ### DOIT
    # And when the markers move onto new ladders, the advice (which?) below is needed,
    # but what if they move onto old ladders,
    # Q do we need to update the marker situation of those too? ###figureout
    # A i guess those old ladder rails get
    # into new whole-chains in that case... so YES. ### DOIT [so in the end we process all changed strands & segs,
    # we just optim by incorporating unchanged ladder-rungs and ladders into them. We have higher-level chains
    # whose components are these rungs, which are chains of atoms.]

    # [@@@ pre-ladder comment:] To help the moving markers know how to advise their new chains about
    # internal baseindex direction coming from their old chains, we first
    # make a dict from atom.key to (new chain id, atom's baseindex in new chain).
    # (We might use it later as well, not sure.)
    # (We keep axis and strand info in one dict for convenience, since both kinds
    #  of markers are in one list we iterate over.)

    ### WORRY ABOUT RING WRAPAROUND in this marker code,
    # where it's a current bug -- see scratch file for more info ###FIX @@@
    
    new_chain_info = {} 

    for chain in axis_chains + strand_chains:
        for atom, index in chain.baseatom_index_pairs(): # skips non-base atoms like Pl
            info = (chain.chain_id(), index)
            new_chain_info[atom.key] = info

    for marker in live_markers:
        still_alive = marker._f_move_to_live_atom_step2(new_chain_info)
            # Note: this also comes up with direction advice for the new chain,
            # stored in the marker and based on the direction of its new atoms
            # in its old chain (if enough of them remain adjacent, currently 2);
            # but the new chain will later take that advice from at most one marker.
        if DEBUG_DNA_UPDATER:
            print "dna updater: moved_step2 marker %r, still_alive = %r" % (marker, still_alive)
        # Note: we needn't record the markers whose atoms are still alive,
        # since we'll find them all later on a new chain. Any marker
        # that moves either finds new atoms whose chain has a change
        # somewhere that leads us to find it (otherwise that chain would
        # be unchanged and could have no new connection to whatever other
        # chain lost atoms which the marker was on), or finds none, and
        # can't move, and either dies or is of no concern to us.
    del live_markers #k if not, update it with new liveness

    ignore_new_changes("from updating DnaAtomMarkers, step2", changes_ok = False)

    # @@@ LOGIC ISSUE: is the following about new chain fragments, or new/modified whole chains? do it before or after ladders?
    #
    # Tell all new chains to take over their atoms and any markers on them,
    # deciding between competing markers for influencing base indexing
    # and other settings, and creating new markers as needed.
    #
    # (Maybe also save markers for use in later steps, like making or updating
    #  Segment & Strand objects, and storing all these in DNA Groups.)
    #
    # Do axis chains first, so strand chains which need new markers or
    # direction decisions (etc) can be influenced by their base numbering, order, etc.
    #
    # (Future: we might have a concept of "main" and "secondary" strands
    # (e.g. scaffold vs staples in origami), and if so, we might want to do
    # all main strands before all secondary ones for the same reason.)
    
    # [Possible optim: reuse old chains if nothing has changed.
    # Not done at present; I'm not sure how rare the opportunity will be,
    # but I suspect it's rare, in which case, it's not worth the bug risk.]
    
    for chain in axis_chains:
        chain._f_own_atoms()

    for chain in strand_chains:
        chain._f_own_atoms()# IMPLEM - now these are stubs which always remake markers @@@

    ignore_new_changes("from updating DnaAtomMarkers, own_atoms")
        # changes are ok since it can add new marker jigs to atoms
    
    # That figured out which markers control each chain (and stored the answers in the chains). ###IMPLEM
    # It also means we no longer need to care about chain.index_direction,
    # which frees us to permit merging of new and old chains, whose
    # index_directions might be incompatible at the merge points.
    # (I think they'll be compatible for new/new merges, but it doesn't matter.)

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

    # Now.... @@@ [below here might be obs]


    # replace old chain info with new chain info on all live atoms
    # (Q: is this chain info undoable state? guess: yes) (do we need it? could find it via chunks... more efficient.... ###)

    
    #e use them (or make new) to determine id & index for each chain

    # revise indices & chunking

    # markers are really on base-pairs... even though on certain atoms too. indices are for base pairs...
    # so we need to find sections of axis whose strands have no nicks, and number these, and assign these to larger things.
    # one alg: assign new id & indices to every changed chain, effectively a jiglike thing on that chain just to index it...
    # maybe the returned objects above could even be these things. a quick check lets you see if the atom already has one;
    # only reuse it if every atom has same one and atom count matches (ie if its membership needn't change).
    # the atom class can have a field & method for this thing, even if it's also in jigs list... it's a chain id & index...
    # so it can be identical for both axis and strand chains. those atoms can be ChainAtoms.
    # (What about PAM5? i think we'd index only Ss and reuse same index on Pl...)

    # optim: sort bonds in atom classes, and sort atoms in bond classes, in special ways.
    
    return all_new_chunks # from update_PAM_chunks

# end

