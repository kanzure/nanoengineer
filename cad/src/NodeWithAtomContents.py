# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
NodeWithAtomContents.py -- abstract class for Node subclasses which
can contain Atoms.

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 080305 added some abstract classes between Node and Group
in the inheritance hierarchy, of which is this one.
"""

from Utility import NodeWith3DContents

class NodeWithAtomContents(NodeWith3DContents):
    # REVIEW: which methods can safely assert that subclass must implement?
    """
    Abstract class for Node subclasses which can contain Atoms.

    Notable subclasses include Chunk and Group.
    """
    def pickatoms(self):
        """
        [overrides Node method; subclasses must override this method]
        """
        pass ### assert 0, "subclass must implement"

    def contains_atom(self, atom):
        """
        [overrides Node method; subclasses must override this method]
        """
        assert 0, "subclass must implement"

    pass

# end
