# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Block.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

Note: this is likely to not always be Dna-specific, and accordingly
to be moved into a more general package.
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
    def is_block(self): # IMPLEM in Node API
        """
        [overrides Node API method]
        """
        return True
    # the following methods might be the same for Block and DnaGroup...
    # maybe they should be on a mixin to "hide kids except for blocks"
    def kids(self): ### used? need to rename... MT_members? MT_children? MT_kids?
        return filter( lambda member: member.is_block(), self.members )
    def openable(self): #k args
        return not not self.kids()
    # need more attrs or methods to specify more properties
    # (note: there might be existing Node API methods already good enough for these):
    # is DND into self permitted?
    # is DND of self permitted?
    # is DND of visible members (subblocks) of self permitted?
    # and maybe more...
    pass

# end
