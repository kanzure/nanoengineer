# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaStrandOrSegment.py - abstract superclass for DnaStrand and DnaSegment

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from foundation.LeafLikeGroup import LeafLikeGroup

_superclass = LeafLikeGroup

class DnaStrandOrSegment(LeafLikeGroup):
    """
    Abstract superclass for DnaStrand and DnaSegment,
    which represent a Dna Strand or Dna Segment inside a Dna Group.

    Internally, this is just a specialized Group containing various
    subobjects:

    - as Group members (not visible in MT, but for convenience of
    reusing preexisting copy/undo/mmp code):

      - one or more DnaMarkers, one of which determines this
        strand's or segment's base indexing, and whether/how it survives if its
        chains of PAM atoms are broken or merged with other strands or segments

      - this DnaStrands's DnaStrandChunks, or this DnaSegment's
        DnaAxisChunks (see docstrings of DnaStrand/DnaSegment for details)

    - As other attributes:

      - (probably) a WholeChain, which has a chain of DnaAtomChainOrRings (sp?)
        which together comprise all the PAM atoms in this strand, or all
        the PAM atoms in the axis of this segment. From these,
        related objects like DnaLadders and connected DnaSegments/DnaStrands
        can be found. This is used to help the dna updater reconstruct
        the PAM atom chunks after a change by old code which didn't do that itself.
    
      - whatever other properties the user needs to assign, which are not
        covered by the member nodes or superclass attributes. However,
        some of these might be stored on the controlling DnaMarker,
        so that if we are merged with another strand or segment, and later separated
        again, that marker can again control the properties of a new strand
        or segment (as it will in any case control its base indexing).
    """
    
    def permit_as_member(self, node, pre_updaters = True, **opts): # in DnaStrandOrSegment
        """
        [friend method for enforce_permitted_members_in_groups and subroutines]

        Does self permit node as a direct member,
        when called from enforce_permitted_members_in_groups with
        the same options as we are passed?

        @rtype: boolean

        [extends superclass method]
        """
        #bruce 080319
        if not LeafLikeGroup.permit_as_member(self, node, pre_updaters, **opts):
            # reject if superclass would reject [bruce 081217]
            return False
        del opts
        assy = self.assy
        res = isinstance( node, assy.DnaMarker) or \
              isinstance( node, assy.DnaLadderRailChunk) or \
              pre_updaters and isinstance( node, assy.Chunk)
        return res
    
    def getDnaGroup(self):
        """
        Return the DnaGroup we are contained in, or None if we're not
        inside one.
        
        @note: Returning None should never happen
               if we have survived a run of the dna updater.
        """
        return self.parent_node_of_class( self.assy.DnaGroup)

    def move_into_your_members(self, node):
        """
        Move node into self's members, and if node was not
        already there but left some other existing Group,
        return that Group.
        
        @param node: a node of a suitable type for being our direct child
        @type node: a DnaLadderRailChunk or DnaMarker (see: permit_as_member)

        @return: Node's oldgroup (if we moved it out of a Group other than self)
                 or None
        @rtype: Group or None
        """
        # note: this is not yet needed in our superclass LeafLikeGroup,
        # but if it someday is, nothing in it is dna-specific except
        # the docstring.
        oldgroup = node.dad # might be None
        self.addchild(node)
        newgroup = node.dad
        assert newgroup is self
        if oldgroup and oldgroup is not newgroup:
            if oldgroup.part is newgroup.part: #k guess
                return oldgroup
        return None
        
    pass # end of class DnaStrandOrSegment

# end
