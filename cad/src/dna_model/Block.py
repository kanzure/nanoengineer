# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Block.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

Note: this is likely to not always be Dna-specific, and accordingly
might be moved into a more general package.
"""

from Group import Group

class Block(Group):
    """
    Model object which represents a user-visible grouping of nodes inside a
    DnaGroup (or similar object, if we have any).

    Most child nodes of a DnaGroup are not visible in the MT, but its Blocks
    are visible there (though their contents are not, except for their
    sub-Blocks).

    See also: DnaGroup, which inherits Block.
    """
    
    def is_block(self):
        """
        [overrides Node API method]
        """
        return True
    
    def MT_kids(self, display_prefs): #bruce 080108 revised semantics
        return self._raw_MT_kids()

    def _raw_MT_kids(self):
        return filter( lambda member: member.is_block(), self.members )
    
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
