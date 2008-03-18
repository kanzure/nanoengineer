# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaStrandOrSegment.py - abstract superclass for DnaStrand and DnaSegment

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from foundation.Group import Group

from utilities.debug_prefs import debug_pref, Choice_boolean_False

class DnaStrandOrSegment(Group):
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

      - (maybe) this DnaStrands's DnaStrandChunks, or this DnaSegment's
        DnaAxisChunks (see docstrings of DnaStrand/DnaSegment for details)

    - As other attributes:

      - (probably) a chain of DnaAtomChainOrRings
        which together comprise all the PAM atoms in this strand, or all
        the PAM atoms in the axis of this segment. From these,
        related objects like DnaLadders and connected DnaSegments/DnaStrands
        can be found. (But we may instead have, or also have and mainly use,
        a chain of the chunks that normally contain these same atoms.
        The reason we might need both is that the atom-based chain,
        independent of chunks, can help the dna updater reconstruct
        the chunks after a change by old code which didn't do that itself.
    
      - whatever other properties the user needs to assign, which are not
        covered by the member nodes or superclass attributes. However,
        some of these might be stored on the controlling DnaMarker,
        so that if we are merged with another strand or segment, and later separated
        again, that marker can again control the properties of a new strand
        or segment (as it
        will in any case control its base indexing).
    """

    def permits_ungrouping(self): #bruce 080207 in Block, copied to DnaStrandOrSegment 080318
        """
        Should the user interface permit users to dissolve this Group
        using self.ungroup?
        [overridden from Group]
        """
        return self._show_all_kids_for_debug() # normally False
            # note: modelTree should modify menu text for Ungroup to say "(unsupported)",
            # but this is broken as of before 080318 since it uses a self.is_block() test.

    def _show_all_kids_for_debug(self): #bruce 080207 in Block, copied to DnaStrandOrSegment 080318
        classname_short = self.__class__.__name__.split('.')[-1]
        debug_pref_name = "Model Tree: show content of %s?" % classname_short
            # typical examples (for text searches to find them here):
            # Model Tree: show content of DnaGroup?
            # Model Tree: show content of Block?
        return debug_pref( debug_pref_name, Choice_boolean_False )

    def MT_DND_can_drop_inside(self): #bruce 080317, revised 080318
        """
        Are ModelTree Drag and Drop operations permitted to drop nodes
        inside self?

        [overrides Node/Group method]
        """
        return self._show_all_kids_for_debug() # normally False

    def _raw_MT_kids(self, display_prefs = {}):
        """
        DnaStrand or DnaSegment groups (subclasses of this class) should not 
        show any MT kids.
        @see: Group._raw__MT_kids()
        @see: Group.MT_kids()
        """
        if self._show_all_kids_for_debug(): # normally False
            # bruce 080318
            return self.members
        return ()

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
        Move node into self's Group members, and if node was not
        already there but left some other existing Group,
        return that Group.
        
        @param node: a node of a suitable type for being our direct child
        @type node: a DnaLadderRailChunk or DnaMarker

        @return: Node's oldgroup (if we moved it out of a Group other than self)
                 or None
        @rtype: Group or None
        """
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
