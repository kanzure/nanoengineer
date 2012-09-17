# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
dna_updater_ladders.py - ladder-related helpers for dna_updater_chunks

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

See also: DnaLadder
"""

from utilities import debug_flags

from dna.updater.dna_updater_follow_strand import dna_updater_follow_strand

from dna.model.DnaLadder import DnaLadder, DnaSingleStrandDomain

from dna.updater.dna_updater_globals import _f_get_invalid_dna_ladders
from dna.updater.dna_updater_globals import DNALADDER_INVAL_IS_OK
from dna.updater.dna_updater_globals import temporarily_set_dnaladder_inval_policy
from dna.updater.dna_updater_globals import DNALADDER_INVAL_IS_ERROR

from dna.model.dna_model_constants import MAX_LADDER_LENGTH

from model.elements import Pl5

# ==

def dissolve_or_fragment_invalid_ladders( changed_atoms):
    """
    #doc... [some is in a caller comment]

    Also make sure that live atoms that are no longer in valid ladders
    (due to dissolved or fragmented ladders) are included in the caller's
    subsequent step of finding changed chains,
    or that the chains they are in are covered. This is necessary so that
    the found chains (by the caller, after this call)
    cover all atoms in every "base pair" (Ss-Ax-Ss) they cover any atom in.
    This might be done by adding some of their atoms into changed_atoms
    in this method (but only live atoms).
    """
    # assume ladder rails are DnaLadderRailChunk instances,
    # or were such until atoms got removed (calling their delatom methods).

    changed_chunks = {}

    for atom in changed_atoms.itervalues():
        chunk = atom.molecule
        ## print "DEBUG: changed atom %r -> chunk %r" % (atom, chunk)
        changed_chunks[id(chunk)] = chunk
        if atom.element is Pl5:
            #bruce 080529 fix bug 2887 (except for the lone Pl atom part,
            #  really a separate bug)
            # Only needed for Pl5 whose structure actually changed
            # (so no need to do it recursively for the ones we add to
            #  changed_atoms lower down). Needed because, without it,
            # breaking a Pl-Ss bond can leave a Pl whose only real bond
            # goes to a valid ladder, resulting in finding a strand chain
            # with only that Pl atom (thus no baseatoms), which assertfails,
            # and would probably cause other problems if it didn't.
            for Ss in atom.strand_neighbors():
                chunk = Ss.molecule
                changed_chunks[id(chunk)] = chunk
                # no need to put Ss into changed_atoms,
                # that will happen lower down when chunk ladder becomes invalid
                # (and if somehow it doesn't, probably not needed anyway,
                #  though that ought to be reviewed)
                continue
            pass
        continue

    for chunk in changed_chunks.itervalues():
        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE: # was useful for bug 080120 9pm
            print "dna updater: fyi: tell changed chunk %r -> inval its ladder %r" % \
                  (chunk, getattr(chunk, 'ladder', "<has none>"))
            pass
        # todo: assert not killed, not nullMol, is a Chunk
        ## chunk.invalidate_ladder()
        chunk.invalidate_ladder_and_assert_permitted()
            # fyi: noop except in DnaLadderRailChunk
            # this just invals chunk.ladder (and below code will dissolve it);
            # a future optim could fragment it instead,
            # if we also recorded which basepair positions
            # were invalid, and made sure their atoms were covered
            # below so their chains will get scanned by caller,
            # e.g. due to changed_atoms.

    # Changed atoms that got removed from their ladders invalidated them
    # at the time (in DnaLadderRailChunk.delatom). Those that didn't get
    # removed from them are still in them, and invalidated them just above.
    # So the following will now give us a complete list of invalid ladders,
    # all of whose atoms we want to scan here.

    invalid_ladders = _f_get_invalid_dna_ladders()

    # now that we grabbed invalid ladders, and callers will make new valid
    # ones soon, any uncontrolled/unexpected inval of ladders is a bug --
    # so make it an error except for specific times when we temporarily
    # permit it and make it a noop (using DNALADDER_INVAL_IS_NOOP_BUT_OK).
    # [bruce 080413]
    _old = temporarily_set_dnaladder_inval_policy( DNALADDER_INVAL_IS_ERROR )
        # note: the restore happens elsewhere, which is why we assert what the
        # old policy was, rather than bothering to later pass it to the
        # restore function (not called before we return), restore_dnaladder_inval_policy.
    assert _old == DNALADDER_INVAL_IS_OK

    for ladder in invalid_ladders:
        # WARNING: the following is only reviewed for the case of the above code
        # dissolving (invalidating, not fragmenting) chunk's ladder.
        #e Could optim if we know some rails were untouched, by
        # "including them whole" rather than rescanning them, in caller.

        # Note: what is meant by "dissolving the ladder" (done above)
        # vs "fragmenting it" (not implemented) is the difference between
        # what happens to the atoms no longer in a valid ladder --
        # are they (until updater runs on them) in no valid ladder,
        # or in some newly made smaller one? The former, for now.
        # The comments and docstrings here are unclear about *when*
        # the dissolving or fragmenting is done. The dissolving can
        # be considered done right when the ladder is invalidated,
        # since we don't intend to make fragments from the untouched
        # parts of it. But this function name claims to do the dissolving
        # itself (even on already invalidated ladders). # todo: clarify.

        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE: # was useful for bug 080120 9pm
            print "dna updater: fyi: adding all atoms from dissolved ladder %r" % ladder
        for rail in ladder.all_rails():
            for atom in rail.baseatoms: # probably overkill, maybe just one atom is enough -- not sure
                # note: atom is in a ladder that was valid a moment ago,
                # but even so, it might be killed now, e.g. if you select
                # and delete one strand atom in a duplex.
                if not atom.killed():
                    changed_atoms[atom.key] = atom
        continue

    return

# == helper for make_new_ladders

class chains_to_break:
    """
    Helper class for breaking chains all at once
    after incrementally recording all desired breakpoints.
    """
    def __init__( self, chains):
        self.chains = chains # a list
        self._set_of_breakpoints_for_chain = d = {}
        for chain in chains:
            d[chain] = {} # avoid later setdefault
        return
    def break_chain_later( self, chain, index, whichside):
        """
        Record info about where to later break chain --
        on whichside of index.

        @param chain: a chain that must be in self.chains
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
            break_before = index
        else:
            assert whichside == 1
            # break_indices = index, index + 1
            break_before = index + 1
        # not needed: assert chain in self.chains
        ## self._set_of_breakpoints_for_chain.setdefault(chain, {})[break_before] = None
        self._set_of_breakpoints_for_chain[chain][break_before] = None # arb value
        return
    def break_between_Q( self, chain, index1, index2):
        """
        Is there a break between the given two adjacent indices in chain?
        @note: adjacent indices can be passed in either order.
        """
        breaks = self._set_of_breakpoints_for_chain[chain]
        assert abs(index1 - index2) == 1
        break_before = max(index1, index2)
        return breaks.has_key(break_before)
    def breakit(self, chain):
        """
        Return a sequence of (start_index, length) pairs,
        suitable for passing to chain.virtual_fragment,
        which describes the fragments of chain into which our
        recorded breaks should break it.

        @param chain: a chain that must be in self.chains
        @type chain: DnaChain

        @return: sequence of (start_index, length) pairs
        """
        breaks = self._set_of_breakpoints_for_chain[chain].keys() # might be empty
        breaks.sort()
        start_index = chain.start_baseindex() # modified during loop
        limit_index = chain.baselength() + start_index
        breaks.append(limit_index)
        res = []
        num_bases = 0 # for asserts only
        for break_before in breaks:
            length = break_before - start_index
            num_bases += length # for asserts only
            # length can be 0 here, due to explicit breaks at the ends
            if length:
                res.append( (start_index, length) )
            start_index = break_before
            continue
        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE: # made verbose on 080201
            print "will break %r -> %d pieces == %r" % (chain, len(res), res)
        assert num_bases == chain.baselength()
        return res
    pass

# ==

def make_new_ladders(axis_chains, strand_chains):
    """
    Make new DnaLadders and/or DnaSingleStrandDomains out of the given (partial) atom chains
    (which should contain only PAM atoms no longer in valid old ladders,
     and which are able to form complete new ladders, since they contain
     all or no PAM atoms from each "base pair" (Ss-Ax-Ss unit) or "single
     strand base" (either Ss-Ax- with no other Ss on that Ax, or Ss with
     no Ax (possibly with 'unpaired-base' atoms which we mostly ignore),
    fragmenting, reversing, and shifting the chains as needed.

    The newly made ladders might be more fragmented than required
    (i.e. new/new ladder merges might be possible), and they might be
    mergeable with old ladders. Their length can be as short as 1.
    They might be rings (or moebius rings), or some of their rails
    might be rings, but this is not detected or encoded explicitly.

    The new ladders will have rails in the same direction
    and with proper bond directions. (If necessary, we fix
    inconsistent bond directions.) [### partly nim; see ladder.error flag --
    also it would be better to not change them but to break bonds. @@@]

    @return: tuple of two lists: newly made DnaLadders, newly made DnaSingleStrandDomains
    """
    # Basic algorithm: scan each axis chain (or ring), and follow along its two
    # bound strands to see when one or both of them leave it or stop (i.e. when
    # the next atom along the strand is not bound to the next atom along the
    # axis). This should classify all strand atoms as well (since bare ones were
    # deleted earlier -- if they weren't, remaining strand fragments can also
    # be found).

    # possible simplification: should we just make lots of length==1 ladders
    # (one per axis atom), then merge them all? In theory, this should work,
    # and it might even be faster -- that depends on how often this step
    # manages to return ladders much longer than 1. It would eliminate
    # most code in this function. (Try it if this function is hard to debug? @@@)

    strand_axis_info = {}

    for axis in axis_chains:
        for atom, index in axis.baseatom_index_pairs():
            # assume no termination atoms here

            new_strand_atoms = atom.strand_neighbors()
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
        # along axis (treating lack of Ax as moving continuously on an
        # imaginary Ax chain different from all real ones)
        # (for details, see the helper function).
        # (The break_ functions store the virtual breaks for later use
        #  in fragmenting the chains.)
        dna_updater_follow_strand(1, strand, strand_axis_info, break_axis, break_strand)

    for strand in strand_chains:
        # Now copy any axis breaks that strand moves over
        # onto strand breaks, in case they originated from the
        # other strand at that point on the axis.
        dna_updater_follow_strand(2, strand, strand_axis_info, None, break_strand, axis_breaker.break_between_Q )

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

    def end_baseatoms(rail):
        return rail.end_baseatoms()

    ladders = []
    singlestrands = []

    for axis in axis_chains:
        frags = axis_breaker.breakit(axis)
        for frag in frags:
            start_index, length = frag
            axis_rail = axis.virtual_fragment(start_index, length)
            ladder = DnaLadder(axis_rail)
            for atom in axis_rail.end_baseatoms():
                ladder_locator[atom.key] = ladder
            ladders.append(ladder)

    for strand in strand_chains:
        frags = strand_breaker.breakit(strand)
        for frag in frags:
            start_index, length = frag
            strand_rail = strand.virtual_fragment(start_index, length)
            # find ladder to put it in (Ax attached to arbitrary strand atom)
            atom = strand_rail.end_baseatoms()[0].axis_neighbor()
            if atom is None:
                # single strand with no Ax (will be true of every Ss in chain)
##                print "dna updater: fyi: found single strand domain %r" % (strand_rail,)
                for atom2 in strand_rail.baseatoms:
                    assert atom2.axis_neighbor() is None, \
                           "%r.axis_neighbor() should be None, is %r; atom is %r, sr is %r" % \
                           (atom2, atom2.axis_neighbor(), atom, strand_rail)
                        # remove when works?? has failed once, 080325 for tom...
                        # and once for me, after exception in pam conversion, 080413
                singlestrand = DnaSingleStrandDomain(strand_rail)
                singlestrands.append(singlestrand)
            else:
                # Ax is present
                ### REVIEW or BUG: why can we assume this works, for an arb (not just end) strand atom? @@@@
                # but wait, it's not an arb atom, it's a strand_rail end atom. Should be ok -- FIX THE COMMENT ABOVE.
                # but there is a bug where dissolving a ladder failed to put axis atoms into changed_atoms... 080120 327p
                try:
                    ladder = ladder_locator[atom.key]
                except KeyError:
                    # this happens in a bug tom reported thismorning, so try to survive it and print debug info
                    # [bruce 080219]
                    print "\n***BUG: dna updater: ladder_locator lacks %r -- specialcase might cause bugs" % (atom,) # @@@@@
                    # specialcase is variant of single strand code above
                    for atom2 in strand_rail.baseatoms:
                        if not (atom2.axis_neighbor() is None):
                            print " sub-bug: %r has %r with an axis_neighbor, %r" % \
                                  (strand_rail, atom2, atom2.axis_neighbor())
                    singlestrand = DnaSingleStrandDomain(strand_rail)
                    singlestrands.append(singlestrand)
                else:
                    ladder.add_strand_rail(strand_rail)

    for ladder in ladders:
        ladder.finished()
            # this ensures ladder has one or two strands, antiparallel in standard bond directions, aligned with axis rungs
            # (it reverses chains as needed, for rung alignment and strand bond direction)
            # @@@ (does it rotate ring chains?)

    return ladders, singlestrands # from make_new_ladders

# ==

def merge_ladders(new_ladders):
    """
    Merge end-to-end-connected ladders (new/new or new/old) into larger
    ones, when that doesn't make the resulting ladders too long.

    @return: list of merged (or new and unable to be merged) ladders

    @note: each returned ladder is either entirely new (perhaps merged
           or perhaps one of the ones the caller passed in),
           or the result of merging (one or more) new and (presumably
           just one) old ladders.
    """
    # Initial implem - might be too slow (quadratic in atomcount) if
    # repeated merges from small to large chain sizes occur.
    # Note, these ladders' rails might be real chunks (merge is slower)
    # or some sort of real or virtual atom chains (merge is faster).
    # (As of 080114 I think they are real atom chains, not yet associated
    #  with chunks.)

    res = [] # collects ladders that can't be merged

    while new_ladders: # has ladders untested for can_merge

        # note about invalid ladders during these loops:
        # in the first iteration of this outer loop, the ladders in
        # new_ladders are newly made, all valid (though they might be invalid
        # by the time the inner loop reaches them, if they got merged into a
        # ladder encountered earlier in that loop over new_ladders). In all
        # other iterations they are newly merged ladders, but they might
        # *already* be invalid if they got merged again by a later ladder
        # in the inner loop that merged them. (Or they might become invalid
        # during the loop, just as in the first iteration.)
        # In all cases it means nothing if they are invalid now,
        # and they should just be skipped if they are invalid when encountered.
        # [comment and behavior revised to fix bug from incorrect assertion,
        #  bruce 080222; earlier partial version of skip, bruce 080122]

        next = [] # new_ladders for next iteration

        for ladder in new_ladders:
            if not ladder.valid:
                # just skip it (not an error, as explained above)
                pass
            else:
                can_merge_info = ladder.can_merge() # (at either end)
                if can_merge_info:
                    merged_ladder = ladder.do_merge(can_merge_info)
                        # note: this invals the old ladders, one of which is
                        # ladder; the other might be later in new_ladders, or
                        # already appended to next earlier during this loop,
                        # or not known to this function.
                        # Q: what if the rails (also merged here) are already
                        # contained in wholechains?
                        # A: they're not yet contained in those -- we find those
                        # later from the merged ladders.
                    assert not ladder.valid
                    assert merged_ladder.valid
                    next.append(merged_ladder)
                else:
                    res.append(ladder)
        new_ladders = next
    for ladder in res:
        assert ladder.valid # required by caller, trivially true here
    return res

def split_ladders(ladders): # STUB but should cause no harm @@@@
    res = []
    for ladder in ladders:
        # REVIEW: higher threshhold for split than merge, for "hysteresis"?? maybe not needed...
        if len(ladder) > MAX_LADDER_LENGTH:
            print "NIM: split long ladder %r" % ladder
            res0 = [ladder] # the pieces
                # (real split function should inval original, then validate pieces)
            res.extend(res0)
        else:
            res.append(ladder)
    return res

def merge_and_split_ladders(ladders, debug_msg = ""):
    """
    See docstrings of merge_ladders and split_ladders
    (which this does in succession).

    @param ladders: list of 0 or more new DnaLadders

    @param debug_msg: string for debug prints
    """
    len1 = len(ladders) # only for debug prints

    ladders = merge_ladders(ladders)

    len2 = len(ladders)

    ladders = split_ladders(ladders)

    len3 = len(ladders)

    assert len2 == len3 ### REMOVE WHEN WORKS (says split is a stub) @@@@

    if debug_flags.DEBUG_DNA_UPDATER:
        if debug_flags.DEBUG_DNA_UPDATER_VERBOSE or len2 != len1 or len3 != len1:
            # note: _DEBUG_FINISH_AND_MERGE(sp?) is in another file
            if debug_msg:
                debug_msg = " (%s)" % debug_msg
            print "dna updater: merge_and_split_ladders%s: %d ladders, merged to %d, split to %d" % \
                  (debug_msg, len1, len2, len3)
    return ladders

# end
