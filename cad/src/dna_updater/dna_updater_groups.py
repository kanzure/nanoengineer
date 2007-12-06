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
    
    ignore_new_changes("as update_DNA_groups starts", changes_ok = False )

    chains = {}
    
    for chunk in new_chunks:
        # does it have a desired home, or need a new one?
        # A desired one is found via its marker, on a chain passing through the chunk.

        # MAYBE TODO: We might do part of this when creating the chunk
        # and only do it now if no home existed.
        chain = chunk.chain # this wants the higher-level WholeChain ##### DOIT
        chains[id(chain)] = chain
        marker = chain.find_controlling_marker() # IMPLEM
        strand_or_segment = marker.owning_strand_or_segment()
            # IMPLEM; might just be an attr, .owner; or just .dad??
            # but note we have new methods like it for more external use, that call get_parentnode....
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
            strand_or_segment = dnaGroup.makeStrandOrSegmentForMarker(marker) # IMPLEM; marker might be new, or newly controlling
        # move the chunk there
        strand_or_segment._move_into_your_members(chunk) # IMPLEM for chunks (or make variant method for each arg class)

    for chain in chains.itervalues():
        for marker in chain.all_markers(): # IMPLEM
            strand_or_segment = marker.owning_strand_or_segment()
            assert strand_or_segment # not sure this will be true... note it can't rely on .dad etc to find it!!! #####DOIT
            strand_or_segment._move_into_your_members(marker) # IMPLEM for markers

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

