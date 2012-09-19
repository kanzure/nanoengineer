# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
dna_updater_groups.py - enforce rules on chunks containing changed PAM atoms

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.updater.dna_updater_globals import ignore_new_changes

_DEBUG_GROUPS = False

# ==

def update_DNA_groups( new_chunks, new_wholechains ):
    """
    @param new_chunks: list of all newly made DnaLadderRailChunks (or modified
                       ones, if that's ever possible)

    @param new_wholechains: list of all newly made WholeChains (or modified
                       ones, if that's ever possible) @@@ doc what we do to them @@@ use this arg

    Make sure that PAM chunks and jigs are inside the correct
    Groups of the correct structure and classes, according to
    the DNA Data Model. These Groups include Groups (which someday
    might be called Blocks in this context), DnaSegments,
    DnaStrands, and DnaGroups. Move nodes or create new groups
    of these kinds, as needed.

    Since the user can't directly modify the insides of a DnaGroup,
    and the maintaining code can be assumed to follow the rules,
    the main focus here is on newly created objects, made by
    old code or by reading old mmp files which don't already
    have them inside the right groups.

    For reading mmp files (old or new) to work smoothly, we may [###decide this! it may already sort of work for chunks...]
    also ask the lower-level code that runs before this point
    to add new chunks into the model next to some older chunk
    that contained one of its atoms (if there was one),
    so that if the old chunk was already in the right place,
    the new one will be too.

    We may also convert existing plain Groups into DnaGroups
    under some circumstances, but this is NIM to start with,
    and may never be worth doing, since some touchups of
    converted old files will always be required. But at least,
    if converted files contain useless singleton Groups
    around newly made DnaGroups, we might discard them except
    for copying their name down (which is essentially the same
    thing).

    @return: None (??)
    """

    # Note: this is not (yet? ever?) enough to fully sanitize newly read
    # mmp files re Group structure. It might be enough for the results of
    # user operations, though. So it's probably better to process mmp files
    # in a separate step, after reading them and before (or after?) running
    # this updater. @@@

    # Note:
    # - before we're called, markers have moved to the right place, died, been made,
    #   so that every wholechain has one controlling marker. But nothing has moved
    #   into new groups in the internal model tree. Markers that need new DnaSegments
    #   or DnaStrands don't yet have them, and might be inside the wrong ones.

    # revise comment:
    # - for segments: [this] tells you which existing or new DnaSegment owns each marker and DnaSegmentChunk. Move nodes.
    # - for strands: ditto; move markers into DnaStrand, and chunks into that or DnaSegment (decide this soon).

    ignore_new_changes("as update_DNA_groups starts", changes_ok = False,
                       debug_print_even_if_none = _DEBUG_GROUPS)

    old_groups = {}

    # find or make a DnaStrand or DnaSegment for each controlling marker
    # (via its wholechain), and move markers in the model tree as needed
    for wholechain in new_wholechains:
        strand_or_segment = wholechain.find_or_make_strand_or_segment()
        for marker in wholechain.all_markers():
##            print "dna updater: debug fyi: subloop on ", marker
            old_group = strand_or_segment.move_into_your_members(marker)
            if old_group:
                old_groups[id(old_group)] = old_group

    ignore_new_changes("from find_or_make_strand_or_segment",
                       changes_ok = False,
                       debug_print_even_if_none = _DEBUG_GROUPS )
        # should not change atoms in the ways we track

    # move chunks if needed
    for chunk in new_chunks:
        wholechain = chunk.wholechain # defined for DnaLadderRailChunks
        assert wholechain # set by update_PAM_chunks
        # could assert wholechain is in new_wholechains
        strand_or_segment = wholechain.find_strand_or_segment()
        assert strand_or_segment
        old_group = strand_or_segment.move_into_your_members(chunk)
            # (For a StrandChunk will we place it into a DnaStrand (as in this code)
            #  or based on the attached DnaSegment?
            #  Not yet sure; the latter has some advantages and is compatible with current external code [080111].
            #  If we do it that way, then do that first for the new segment chunks, then another pass for the strand chunks.
            #  Above code assumes it goes into its own DnaStrand object; needs review/revision.)
            #
            # MAYBE TODO: We might do part of this when creating the chunk
            # and only do it now if no home existed.
        if old_group:
            old_groups[id(old_group)] = old_group

    ignore_new_changes("from moving chunks and markers into proper Groups",
                       changes_ok = False,
                       debug_print_even_if_none = _DEBUG_GROUPS )

    # Clean up old_groups:
    #
    # [update 080331: comment needs revision, since Block has been deprecated]
    #
    # For any group we moved anything out of (or are about to delete something
    # from now), we assume it is either a DnaSegment or DnaStrand that we moved
    # a chunk or marker out of, or a Block that we delete all the contents of,
    # or a DnaGroup that we deleted everything from (might happen if we mark it
    # all as having new per-atom errors), or an ordinary group that contained
    # ordinary chunks of PAM DNA, or an ordinary group that contained a DnaGroup
    # we'll delete here.
    #
    # In some of these cases, if the group has become
    # completely empty we should delete it. In theory we should ask the group
    # whether to do this. Right now I think it's correct for all the kinds listed
    # so I'll always do it.
    #
    # If the group now has exactly one member, should we dissolve it
    # (using ungroup)? Not for a 1-member DnaSomething, probably not
    # for a Block, probably not for an ordinary group, so for now,
    # never do this. (Before 080222 we might do this even for a
    # DnaSegment or DnaStrand, I think -- probably a bug.)
    #
    # Note, we need to do the innermost (deepest) ones first.
    # We also need to accumulate new groups that we delete things from,
    # or more simply, just transclose to include all dads from the start.
    # (Note: only correct since we avoid dissolving groups that are equal to
    #  or outside the top of a selection group. Also assumes we never dissolve
    #  singletons; otherwise we'd need to record which groups not in our
    #  original list we delete things from below, and only consider those
    #  (and groups originally in our list) for dissolution.)

    from foundation.state_utils import transclose # todo: make toplevel import
    def collector(group, dict1):
        # group can't be None, but an optim to earlier code might change that,
        # so permit it here
        if group and group.dad:
            dict1[id(group.dad)] = group.dad
    transclose( old_groups, collector)

    depth_group_pairs = [ (group.node_depth(), group)
                          for group in old_groups.itervalues() ]
    depth_group_pairs.sort()
    depth_group_pairs.reverse() # deepest first

    for depth_junk, old_group in depth_group_pairs:
        if old_group.is_top_of_selection_group() or \
           old_group.is_higher_than_selection_group():
            # too high to dissolve
            continue
        if len(old_group.members) == 0:
            # todo: ask old_group whether to do this:
            old_group.kill()
            # note: affects number of members of less deep groups
        # no need for this code when that len is 1:
        ## old_group.ungroup()
        ##     # dissolves the group; could use in length 0 case too
        continue

    ignore_new_changes("from trimming groups we removed things from",
                       changes_ok = False,
                       debug_print_even_if_none = _DEBUG_GROUPS )

    ignore_new_changes("as update_DNA_groups returns", changes_ok = False )

    return # from update_DNA_groups


# end

