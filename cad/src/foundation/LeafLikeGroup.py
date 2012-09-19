# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
LeafLikeGroup.py - abstract superclass for groups that appear as leaves
in the MT, e.g. DnaStrandOrSegment, NanotubeSegment, PeptideSegment.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:

most methods written by Bruce as part of DnaStrandOrSegment,
and subsequently copied into NanotubeSegment and PeptideSegment
by Ninad and/or Mark and/or Piotr.

bruce 081217 made this class to contain common code for those
classes which originated in DnaStrandOrSegment (which was
svn copied to initiate this file).

TODO:

notice and pull in other common code subsequently
added to some of our subclasses.

"""

from foundation.Group import Group

from utilities.debug_prefs import debug_pref, Choice_boolean_False

class LeafLikeGroup(Group):
    """
    Abstract superclass for Groups that appear as leaves in the Model Tree.

    Internally, this is just a specialized Group containing subclass-
    specific subobjects and attributes, and overriding some Node or Group API
    methods to change Model Tree behavior (and perhaps other behavior).
    """

    def permit_addnode_inside(self): #bruce 080626
        """
        [overrides superclass method]
        """
        return False

    def permits_ungrouping(self):
        """
        Should the user interface permit users to dissolve this Group
        using self.ungroup?

        [overrides superclass method]
        """
        #bruce 080207 in deprecated class Block, copied to DnaStrandOrSegment 080318
        return self._show_all_kids_for_debug() # normally False

    def _show_all_kids_for_debug(self):
        #bruce 080207 in deprecated class Block, copied to DnaStrandOrSegment 080318
        #bruce 081217: revised to use same debug_pref for all node classes
        debug_pref_name = "Model Tree: show content of leaf-like Groups?"
        return debug_pref( debug_pref_name, Choice_boolean_False )

    def _f_wants_to_be_killed(self, pre_updaters = True, **opts): # in LeafLikeGroup
        """
        [friend method for enforce_permitted_members_in_groups and subroutines]

        Does self want to be killed due to members that got ejected
        by _f_move_nonpermitted_members (or due to completely invalid structure
        from before then, and no value in keeping self even temporarily)?

        @rtype: boolean

        [overrides superclass method]
        """
        #bruce 080319
        del opts, pre_updaters
        return not self.members

    def MT_DND_can_drop_inside(self): #bruce 080317, revised 080318
        """
        Are ModelTree Drag and Drop operations permitted to drop nodes
        inside self?

        [overrides superclass method]
        """
        return self._show_all_kids_for_debug() # normally False

    def openable(self):
        """
        whether tree widgets should permit the user to open/close
        their view of this node

        [overrides superclass method]
        """
        # if we decide this depends on the tree widget or on somet for thing about it,
        # we'll have to pass in some args... don't do that unless/until we need to.

        #If there are no MT_kids (subnodes visible in MT under this group) then
        #don't make this node 'openable'. This makes sure that expand/ collapse
        #pixmap next to the node is not shown for this type of Group with 0
        #MT_kids
        #Examples of such groups include empty groups, DnaStrand Groups,
        #DnaSegments etc -- Ninad 2008-03-15
        return len(self.MT_kids()) != 0

    def MT_kids(self, display_prefs = {}):
        """
        [overrides superclass method]
        """
        if self._show_all_kids_for_debug(): # normally False
            # bruce 080318
            return self.members
        return ()

    def get_all_content_chunks(self): # by Ninad; moved & docstring revised by bruce 081217
        """
        Return all the chunks which should be considered logical contents
        of self.

        The default implementation returns direct members of self
        which are chunks.

        Some subclasses must override this.
        """
        # TODO: refactor this and its callers to use a more general definition
        # of what to return, and to use related submethods such as one to
        # iterate over logical contents (perhaps adding that to API).
        # The different calls might need splitting into different API methods.
        # REVIEW: I suspect there are bugs at present from not including jigs,
        # when this is used for dragging.
        # [bruce 081217 comments]
        all_content_chunk_list = []

        for member in self.members:
            if isinstance(member, self.assy.Chunk):
                all_content_chunk_list.append(member)

        return all_content_chunk_list

    pass # end of class DnaStrandOrSegment

# end
