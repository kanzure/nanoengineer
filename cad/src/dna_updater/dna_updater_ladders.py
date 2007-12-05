# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_ladders.py - ladder-related helpers for dna_updater_chunks

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

See also: DnaLadder
"""

from dna_updater_constants import DEBUG_DNA_UPDATER

from dna_updater_follow_strand import dna_updater_follow_strand

from dna_model.DnaLadder import DnaLadder

from dna_model.DnaLadderRailChunk import DnaLadderRailChunk # import not needed?

# ==

def dissolve_or_fragment_invalid_ladders( changed_atoms):
    """
    """
    # assume ladder rails are DnaLadderRailChunk instances.
    
    changed_chunks = {}

    for atom in changed_atoms.itervalues():
        chunk = atom.molecule
        changed_chunks[id(chunk)] = chunk
    
    for chunk in changed_chunks.values():
        # todo: assert not killed, not nullMol, is a Chunk
        chunk.invalidate_ladder() # noop except in DnaLadderRailChunk
            # this just dissolves chunk.ladder;
            # a future optim could fragment it instead,
            # if we also recorded which basepair positions
            # were invalid.

    # BUGS: [from deleting one duplex strand bond]
    # - ladder rails are not yet DnaLadderRailChunk instances.
    # - ladder rails whose whole chains stay untouched (no atoms in changed_atoms)
    #   need inclusion in the strand and axis chain lists (in current code, 071204)
    #   but are not included in them.
    
    return

# == helper for make_new_ladders

class chains_to_break:
    """
    Helper class for breaking chains all at once
    after incrementally recording all desired breakpoints.
    """
    def __init__( self, chains):
        self.chains = chains # a list
        self._set_of_breakpoints_for_chain = {}
    def break_chain_later( self, chain, index, whichside):
        """
        Record info about where to later break chain --
        on whichside of index.

        @param chain: a chain that's assumed to be in self.chains
        @type chain: DnaChain
        
        @param index: an atom index in chain; WARNING: would become invalid
                      if we reversed the chain
                      
        @param whichside: which side of the indexed atom the break should be on,
            represented as 1 or -1 -- the desired break is
            between index and index + whichsidetobreak        
        """
        ## key = (chain, index, whichside)
        # no, we don't need to record the distinction between break point and direction,
        # just enough to know where the break is; and we might as well collect
        # it up per chain:
        if whichside == -1:
            # break_indices = index - 1, index
            break_after = index - 1
        else:
            assert whichside == 1
            # break_indices = index, index + 1
            break_after = index
        self._set_of_breakpoints_for_chain .setdefault(chain, {})[break_after] = None
        return
    def breakit(self, chain):
        """
        Return a sequence of (start_index, length, direction) triples,
        suitable for passing to chain.virtual_fragment
        for the fragments of chain into which are recorded breaks
        should break it.
        Direction will always be 1.

        @param chain: a chain that's assumed to be in self.chains
        @type chain: DnaChain

        @return: sequence of (start_index, length, direction) triples
        """
        print "breakit nim, stub never breaks",chain ####
        return [ (chain.start_baseindex(), chain.baselength()) ]
    pass

# ==

def make_new_ladders(axis_chains, strand_chains):
    """
    Make new DnaLadders out of the given (partial) atom chains
    (which should contain only PAM atoms no longer in valid old ladders,
     and which are able to form complete new ladders, since they contain
     all or no PAM atoms from each "base pair" (Ss-Ax-Ss unit) or "single
     strand base" (Ss-Ax- with no other Ss on that Ax),
    fragmenting, reversing, and shifting the chains as needed.

    The newly made ladders might be more fragmented than required
    (i.e. new/new ladder merges might be possible), and they might be
    mergeable with old ladders. Their length can be as short as 1.
    They might be rings (or moebius rings), or some of their rails
    might be rings, but this is not detected or encoded explicitly.

    The new ladders will have rails in the same direction
    and with proper bond directions. (If necessary, we fix
    inconsistent bond directions.) @@@doit

    @return: list of newly made DnaLadders
    """
    # Basic algorithm: scan each axis chain (or ring), and follow along its two
    # bound strands to see when one or both of them leave it or stop (i.e. when
    # the next atom along the strand is not bound to the next atom along the
    # axis). This should classify all strand atoms as well (since bare ones were
    # deleted earlier -- if they weren't, remaining strand fragments can also
    # be found).

    # possible simplification: should we just make lots of length-1 ladders
    # (one per axis atom), then merge them all? In theory, this should work,
    # and it might even be faster -- that depends on how often this step
    # manages to return ladders much longer than 1. It would eliminate
    # most code in this function. (Try it if this function is hard to debug? @@@)
    
    strand_axis_info = {}
    
    for axis in axis_chains:
        for atom, index in axis.baseatom_index_pairs():
            # assume no termination atoms here
            
            new_strand_atoms = atom.strand_neighbors() # IMPLEM
                # todo: make an AxisAtom method from this new Atom method

            # For efficiency, at this stage we just store info about these strand atoms' axis locations;
            # later we scan strands all at once and look at that info. This avoids trying both pairings
            # of prior and current strand atoms, and checking for bonding (perhaps thru Pl) or adjacency
            # (worrying about ring index wraparound).


            for s_atom in new_strand_atoms:
                strand_axis_info[s_atom.key] = (axis, index)
                    # store axis object (not id) so it can help with ring indices

    # Make helper objects to record the strand and axis breaks we'll need to do
    # (in terms of putting their pieces into separate ladders/rails).
    #
    # Note: we don't actually do the breaks until we've scanned everything.
    # (We might even do some re-merging of unnecessary breaks before doing
    #  any real breaks of axes.)
    #
    # Note that matched axis and strand indices might be in reversed relative
    # order. We won't reverse any chains until the scan is done and the
    # ladders are made (or being made, since merging ladders requires it).


    axis_breaker = chains_to_break(axis_chains)
    strand_breaker = chains_to_break(strand_chains)

    # helper functions; args are chain, index, whichside:
    break_axis = axis_breaker.break_chain_later
    break_strand = strand_breaker.break_chain_later

    for strand in strand_chains:
        # Loop over strand's base atoms, watching the strand join and leave
        # axis chains and move along them; virtually break both axis and strand
        # whenever it joins, leaves, or moves discontinuously
        # along axis (for details, see the helper function).
        # (The break_ functions store the virtual breaks for later use
        #  in fragmenting the chains.)
        dna_updater_follow_strand(strand, strand_axis_info, break_axis, break_strand)

    # Now use the recorded axis breaks to decide what new ladder fragments
    # to make, and the recorded strand breaks to make strand fragments to
    # assign to ladder fragments. (Note that matching index directions may
    # be reversed, and current indices are offset from those of the
    # fragments.)
    #
    # All fragments in the same ladder will now have the same length
    # (which can be as low as 1). Every ladder will have one or two
    # strands, assuming prior updater stage rules were not violated.
    # (The maximum of two strands comes from a maximum of two strand atoms
    #  bonded to one axis atom. The minimum of 1 comes from deleting bare
    #  axis atoms. The coverage of all strand atoms in this matching
    #  process comes from the lack of bare strand atoms. All of this
    #  is only true since a change to any old ladder atom makes us
    #  process all its atoms in this updater cycle, or at least,
    #  either all or no atoms from the 3 atoms in each of its rungs.)
    #
    # Maybe: do everything virtually at first, in case we can merge some
    # ladders before actually breaking chains. (I'm not sure if this is
    # likely if there were no non-physical situations, though, nor if it's
    # worth the trouble then, since we need code to merge real ladder
    # fragments too, in case new ones should merge with old unchanged ones.)

    ladder_locator = {} # atom.key -> ladder, for end axis atoms of each ladder we're making

    def end_atoms(rail):
        return rail.end_baseatoms()
        ## return (rail.atom_list[0], rail.atom_list[-1])

    ladders = []
    
    for axis in axis_chains:
        frags = axis_breaker.breakit(axis)
        for frag in frags:
            start_index, length = frag
            axis_rail = axis.virtual_fragment(start_index, length)
            ladder = DnaLadder(axis_rail)
            for atom in end_atoms(axis_rail):
                ladder_locator[atom.key] = ladder
            ladders.append(ladder)

    for strand in strand_chains:
        frags = strand_breaker.breakit(strand)
        for frag in frags:
            start_index, length = frag
            strand_rail = strand.virtual_fragment(start_index, length)
            # find ladder to put it in
            atom = end_atoms(strand_rail)[0].axis_neighbor()
            ladder = ladder_locator[atom.key]
            ladder.add_strand_rail(strand_rail)

    for ladder in ladders:
        ladder.finished()
            # this ensures ladder has one or two strands, antiparallel in standard bond directions, aligned with axis rungs
            # (it reverses chains as needed, for rung alignment and strand bond direction)

    return ladders

# ==

def merge_ladders(new_ladders):
    """
    Merge end-to-end-connected ladders (new/new or new/old) into larger
    ones, when that doesn't make the resulting ladders too long.

    @return: list of modified_valid_ladders [nim]

    @note: each returned ladder is either entirely new (perhaps merged),
           or the result of merging new and old ladders.
    """
    # Initial implem - might be too slow (quadratic in atomcount) if repeated
    # merges from small to large chain sizes occur.
    # Note, these ladders' rails might be real chunks (merge is slower)
    # or some sort of real or virtual atom chains (merge is faster).
    res = []
    while new_ladders:
        next = []
        for ladder in new_ladders:
            if ladder.can_merge(): # at either end! only if ladder is valid; ladder can't merge with self!
                assert ladder.valid
                merged_ladder = ladder.do_merge()
                    # kluge: does either end's merge, if both ends could be done
                    # note: invals the old ladders
                    # Q: what if the rails (also merged) are contained in some sort of chains?
                    # Should we just make sure the chains can easily be found, and only find them later? guess: yes.
                assert not ladder.valid
                assert merged_ladder.valid
                next.append(merged_ladder)
            else:
                res.append(ladder)
        new_ladders = next
    return res

# end
