# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Node_api.py - API of Nodes, as assumed by modelTree code

Note: not used (so far, 081216) except as documentation and in test code;
probably not complete

@author: Will, Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from modelTree.Api import Api

class Node_api(Api): # REVIEW: maybe refile this into model/Node_API and inherit from Node?? [bruce 080107 comment]
    """
    The customer must provide a node type that meets this API. This can be done by extending this
    class, or implementing it yourself. [See also class Node in Utility.py, used as the superclass
    for NE1 model tree nodes, which defines an API which is (we hope) a superset of this one.
    This could in principle inherit from this class, and at least ought to define all its methods.]

    In addition to what appears here, a node that has child nodes must maintain them in a list
    called 'self.members'. [that might be WRONG as of 080306, since we now use MT_kids]

    @note: this class is not used (so far, 081216) except as documentation and in test code.
    """
    # There still needs to be an API call to support renaming, where the model tree is allowed to
    # change the Node's name.

    # Questions & comments about this API [bruce 070503, 070508]:
    #
    # - why doesn't it mention node.open or node.openable()?
    #   That omission might be related to some ###BUGS (inability to collapse group nodes).
    #   [I added them to the API but not yet fully to the code. bruce 070508]
    #
    # - how exactly must node.members and node.MT_kids() be related?
    #   Right now this code may assume that they're always equal, and it may also assume that
    #   when they're nonempty the node is openable.
    #   What I think *should* be made true is that node.members is private, or at least read-only...
    #   OTOH MT_kids is not yet different, and not yet used by other NE1 code [bruce 080108 updated this comment]
    #   [this may have been fixed today in favor of only using MT_kids -- bruce 080306]
    #
    # - it ought to include (and the code herein make use of) node.try_rename or so.
    #
    # - is Node.__init__ part of the API, or just a convenience place for a docstring
    #   about required instance variables?
    # - in Qt3 there *is* a Node API call to support renaming ("try_rename" or so).
    #   Why isn't it used or listed here?
    #
    # See also my comments in class ModelTree.__init__.
        
    def __init__(self):
        """
        self.name MUST be a string instance variable.
        self.hidden MUST be a boolean instance variable.
        self.open MUST be a boolean instance variable.
        There is no API requirement about arguments for __init__.
        """
        raise Exception("overload me")

    def pick(self):
        """
        select the object
        [extended in many subclasses, notably in Group]
        [Note: only Node methods should directly alter self.picked,
         since in the future these methods will sometimes invalidate other state
         which needs to depend on which Nodes are picked.]
        """
        raise Exception("overload me")

    def ModelTree_plain_left_click(self): #bruce 080213 addition to Node API
        """
        Do desired extra side effects (if any) from a plain, direct left click
        in a model tree widget (after the usual effect of self.pick, which can
        also happen in several other ways).
        """
        pass
    
    def unpick(self):
        """
        unselect the object, and all its ancestor nodes.
        [extended in many subclasses, notably in Group]
        [Note: only Node methods should directly alter self.picked,
         since in the future these methods will sometimes invalidate other state
         which needs to depend on which Nodes are picked.]
        """
        raise Exception("overload me")

    def apply2picked(self, func):
        """
        Apply fn to the topmost picked nodes under (or equal to) self,
        but don't scan below picked nodes. See Group.apply2picked docstring for details.
        """
        raise Exception("overload me")

    def is_disabled(self):
        """
        MUST return a boolean
        """
        raise Exception("overload me")

    def node_icon(self, display_prefs):
        """
        MUST return either a QPixmap or None
        """
        # display_prefs is used in Group.node_icon to indicate whether a group is open or closed. It
        # is not used anywhere else. It is a dictionary and the only relevant key for it is "open".
        # [Addendum, bruce 070504: it also has a key 'openable'. I don't know if anything looks at
        #  its value at that key, but "not open but openable" vs "not open and not even openable"
        #  is a meaningful difference. The value of 'openable' is usually (so far, always)
        #  implicit in the Node's concrete subclass, so typical methods won't need to look at it.]
        raise Exception("overload me")

##    def drop_on_ok(self, drag_type, nodes):
##        """
##        Say whether 'drag and drop' can drop the given set of nodes onto this node, when they are
##        dragged in the given way, and if not, why not.
##        @rtype: ( boolean, string )
##        """
##        raise Exception("overload me")
##
##    def drop_on(self, drag_type, nodes):
##        """
##        After a 'drag and drop' of type 'move' or 'copy' (according to drag_type), perform the
##        drop of the given list of nodes onto this node. Return any new nodes this creates (toplevel
##        nodes only, for copied groups).
##        """
##        raise Exception("overload me")

    def MT_kids(self, item_prefs = {}): #bruce 080108 renamed kids -> MT_kids; only used in some of the places it needs to be
        """
        Return a list of Nodes that the model tree should show
        as a child of this Node, if it's openable and open.
        (It doesn't matter what this returns in other cases.)
        """
        raise Exception("overload me")

    def openable(self): #bruce 070508
        """
        Return True if tree widgets should display an openclose icon
        for this node, False otherwise.
        """
        raise Exception("overload me")        
    pass

# end
