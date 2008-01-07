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
    
    def kids(self): ### used? need to rename... MT_members? MT_children? MT_kids?
        return filter( lambda member: member.is_block(), self.members )
    
    def openable(self): #k args
        return not not self.kids()

    # TODO: need more attrs or methods to specify more properties
    # (note: there might be existing Node API methods already good enough for these):
    # is DND into self permitted?
    # is DND of self permitted?
    # is DND of visible members (subblocks) of self permitted?
    # and maybe more...
    
    pass

# end
