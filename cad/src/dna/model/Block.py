# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Block.py - ... DEPRECATED CLASS (as of shortly before 080331)

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

Note: this is likely to not always be Dna-specific, and accordingly
might be moved into a more general package. (Except now that it's
deprecated, there is no point in that.)
"""

from foundation.Group import Group

from utilities.debug_prefs import debug_pref, Choice_boolean_False

class Block(Group):
    """
    DEPRECATED CLASS (as of shortly before 080331). DO NOT USE IN NEW CODE.
    
    Model object which represents a user-visible grouping of nodes inside a
    DnaGroup (or similar object, if we have any).

    Most child nodes of a DnaGroup are not visible in the MT, but its Blocks
    are visible there (though their contents are not, except for their
    sub-Blocks). [this statement is partly obsolete]

    @see: DnaGroup, which [used to] inherit Block.
    """

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    #
    #update: bruce 080331 removed this (to affect writemmp),
    # since Block is deprecated. Should not matter, since there is
    # now no known way to create a Block (not counting subclasses).
    # (And the only known way before now was to hand-edit an mmp file.)
    #
    ## _mmp_group_classifications = ('Block',)

    def is_block(self):
        """
        [overrides Node API method]
        """
        return True

    def permits_ungrouping(self): #bruce 080207 overriding this in Block
        """
        Should the user interface permit users to dissolve this Group
        using self.ungroup?
        [overridden from Group]
        """
        return self._show_all_kids_for_debug()

    def apply_to_groups(self, fn): #bruce 080207 overriding this in Block
        """
        Like apply2all, but only applies fn to all Group nodes (at or under self)
        (not including Blocks).
        [overridden from Group implem]
        """
        pass # even if self._show_all_kids_for_debug()

# removing this [ninad 080315]
##    def MT_kids(self, display_prefs = {}): #bruce 080108 revised semantics
##        return self._raw_MT_kids()

    def _raw_MT_kids(self):
        if self._show_all_kids_for_debug():
            return self.members
        return filter( lambda member: member.is_block(), self.members )

    def _show_all_kids_for_debug(self):
        classname_short = self.__class__.__name__.split('.')[-1]
        debug_pref_name = "Model Tree: show content of %s?" % classname_short
            # typical examples (for text searches to find them here):
            # Model Tree: show content of DnaGroup?
            # Model Tree: show content of Block?
        return debug_pref( debug_pref_name, Choice_boolean_False )
        
    def openable(self):
        return not not self._raw_MT_kids()
        # REVIEW: if we are open and lose our _raw_MT_kids, we become open but
        # not openable. Does this cause any bugs or debug prints?
        # Should it cause our open state to be set to false (as a new feature)?
        # [bruce 080107 Q]

    # TODO: need more attrs or methods to specify more properties
    # (note: there might be existing Node API methods already good enough for these):
    # is DND into self permitted?
    # is DND of self permitted?
    # is DND of visible members (subblocks) of self permitted?
    # and maybe more...
    
    pass

# end
