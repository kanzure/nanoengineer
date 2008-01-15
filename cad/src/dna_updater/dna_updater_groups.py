# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_groups.py - enforce rules on chunks containing changed PAM atoms

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_updater_globals import ignore_new_changes

from dna_updater_constants import DEBUG_DNA_UPDATER

from dna_model.DnaGroup import DnaGroup

from dna_model.DnaStrandOrSegment import DnaStrandOrSegment

# ==

def update_DNA_groups( new_chunks, new_wholechains ):
    """
    @param new_chunks: list of all newly made DnaLadderRailChunks (or modified
                       ones, if that's ever possible)

    @param new_wholechains: list of all newly made WholeChains (or modified
                       ones, if that's ever possible) @@@ doc what we do to them @@@ use this arg

    Make sure that PAM chunks and jigs are inside the correct
    Groups of the correct structure and classes, according to
    the DNA Data Model. These Groups include Blocks, DnaSegments,
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

    # basic algorithm: [080111 comment]
    # - markers have moved, or if not, finish that... and pick controlling one on each wholechain (new or modified)
    #   (they are immutable so modified == new, but the point is, some new ones are made in part of untouched smaller chains).
    # - for segments: this tells you which existing or new DnaSegment owns each marker and DnaSegmentChunk. Move nodes.
    # - for strands: ditto; move markers into DnaStrand, and chunks into that or DnaSegment (decide this soon).

    ignore_new_changes("as update_DNA_groups starts", changes_ok = False )

    old_groups = {}

    # make missing strand_or_segment, and move markers into it if needed
    for wholechain in new_wholechains:
        strand_or_segment = wholechain.find_or_make_strand_or_segment() # IMPLEM,
            # using code in outtakes, chunk from any atom in wholechain
        for marker in whole_chain.all_markers(): # IMPLEM
            oldgroup = strand_or_segment._move_into_your_members(marker) # IMPLEM for markers
            if old_group:
                old_groups[id(old_group)] = old_group

    # move chunks if needed
    for chunk in new_chunks:
        whole_chain = chunk.whole_chain # IMPLEM
        # could assert this is in new_wholechains
        strand_or_segment = wholechain.find_strand_or_segment() # IMPLEM
        assert strand_or_segment
        # move the chunk there
        ### REFILE: oldgroup is a group we moved chunk out of (only if we actually moved it to a different one), if any, else None
        oldgroup = strand_or_segment._move_into_your_members(chunk) # IMPLEM for chunks (or make variant method for each arg class)
            # (For a StrandChunk will we place it into a DnaStrand or based on the attached DnaSegment?
            #  Not yet sure; the latter has some advantages and is compatible with current external code [080111].
            #  If we do it that way, then do that first for the new segment chunks, then another pass for the strand chunks.
            #  Above code assumes it goes into its own DnaStrand object; needs review/revision.)
            #
            # MAYBE TODO: We might do part of this when creating the chunk
            # and only do it now if no home existed.
        if old_group:
            old_groups[id(old_group)] = old_group

    # Clean up old_groups:
    # for any group we moved anything out of, perhaps delete it if it is now empty
    # or (especially) dissolve it if it now has only one member and we made that member.
    # This is important when updating an old mmp file with existing groups
    # containing ordinary dna-containing chunks, since otherwise we'll bury the new DnaGroup
    # inside one of those and leave the others empty.
    #
    # Note, we need to do the innermost (deepest) ones first.

    depth_group_pairs = [ (group.group_depth(), group) # IMPLEM group_depth
                          for group in old_groups.values() ]
    depth_group_pairs.sort()
    depth_group_pairs.reverse() # deepest first
    
    for depth_junk, old_group in depth_group_pairs:
        if old_group.is_top_of_selection_group():
            ###k really, if it's too high to dissolve... should be equiv since we modified members...
            # provided parts had toplevel groups before we started here, MAYBE NOT TRUE...
            # but by now they do since there is a DnaGroup somewhere (made above if nec.)... review sometime.
            continue
        if len(old_group.members) == 0:
            old_group.kill() ###k is this always ok?? desirable?
            # might affect members of less deep groups
        elif len(old_group.members) == 1:
            old_group.dissolve() ###k always ok? desirable? IMPLEM dissolve; could use it in len 0 case too...

    ignore_new_changes("as update_DNA_groups returns", changes_ok = False )

    return # from update_DNA_groups

# ==

def new_DnaGroup_around_chunk(chunk):
    return new_Group_around_Node(chunk, DnaGroup)

def new_Group_around_Node(node, group_class): #e refile
    node.part.ensure_toplevel_group() # might not be needed
    name = "(internal Group)" # stub
    assy = node.assy
    dad = None #k legal?? arg needed?
    group = group_class(name, assy, dad) # same args as for Group.__init__(self, name, assy, dad) [review: reorder those anytime soon??]
    node.addsibling(group)
    group.addchild(node)
    return group

# end

