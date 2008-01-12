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

def update_DNA_groups( new_chunks ):
    """
    @param new_chunks: list of all newly made DnaLadderRailChunks (or modified
                       ones, if that's ever possible)

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

    whole_chains = {}
    
    for chunk in new_chunks:
        # does it have a desired home, or need a new one?
        # A desired one is found via the controlling_marker on a whole_chain passing through the chunk.
        # (For a StrandChunk will we place it into a DnaStrand or based on the attached DnaSegment?
        #  Not yet sure; the latter has some advantages and is compatible with current external code [080111].
        #  If we do it that way, then do that first for the new segment chunks, then another pass for the strand chunks.
        #  Following unfinished code assumes it goes into its own DnaStrand object; needs review/revision.)

        # MAYBE TODO: We might do part of this when creating the chunk
        # and only do it now if no home existed.
        whole_chain = chunk.whole_chain # this wants the higher-level WholeChain ##### DOIT
        whole_chains[id(whole_chain)] = whole_chain
        controlling_marker = whole_chain.find_controlling_marker() # IMPLEM
        strand_or_segment = controlling_marker._f_get_owning_strand_or_segment()
            # IMPLEM; might just be an attr, .owner; or just .dad?? [not .dad, we're fixing that now!]
            # but note we have new methods like it for more external use (not valid here), that call get_parentnode....
        if strand_or_segment is None:
            # find the right DnaGroup (or make one if there is none).
            # ASSUME the chunk was created inside the right DnaGroup if there is one. ### VERIFY TRUE
            dnaGroup = chunk.get_parentnode_of_class(DnaGroup)
            if dnaGroup is None:
                # if it was not in a DnaGroup, there's no way it was in
                # a DnaStrand or DnaSegment (since we never make those without
                # immediately putting them into a valid DnaGroup or making them
                # inside one), so there's no need to check for one to make the
                # new group outside of. Just to be sure, we assert this:
                assert chunk.get_parentnode_of_class(DnaStrandOrSegment) is None
                dnaGroup = new_DnaGroup_around_chunk(chunk)
            # now make a strand or segment in that DnaGroup (in a certain Block??)
            strand_or_segment = dnaGroup.makeStrandOrSegmentForMarker(controlling_marker) # IMPLEM; controlling_marker might be new, or newly controlling;
                # doesn't matter for this call whether it moves controlling_marker into self, but i suppose it will
        # move the chunk there
        strand_or_segment._move_into_your_members(chunk) # IMPLEM for chunks (or make variant method for each arg class)

    for whole_chain in whole_chains.itervalues():
        controlling_marker = whole_chain.find_controlling_marker()
        strand_or_segment = controlling_marker._f_get_owning_strand_or_segment()
        for marker in whole_chain.all_markers(): # IMPLEM
##            strand_or_segment = marker._f_get_owning_strand_or_segment()
##            assert strand_or_segment # not sure this will be true... note it can't rely on .dad etc to find it!
##                # hmm, it seems likely (or possible anyway) that this will be false.
##                # what should be possible is to find the controlling marker
##                # on the same whole_chain!
            strand_or_segment._move_into_your_members(marker) # IMPLEM for markers

    # TODO: for any group we moved anything out of, perhaps delete it if it is now empty
    # or (especially) dissolve it if it now has only one member and we made that member.
    # This is important when updating an old mmp file with existing groups
    # containing ordinary dna-containing chunks, since otherwise we'll bury the new DnaGroup
    # inside one of those and leave the others empty.

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

