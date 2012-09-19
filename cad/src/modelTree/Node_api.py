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

class Node_api(Api):
    # REVIEW: maybe refile this into model/Node_API and inherit from Node??
    # [bruce 080107 comment]
    # Or, rename it to reflect its specific purpose (for ModelTreeGUI),
    # then inherit from it (not sure in which package to put it in that case).
    # [bruce 081217 update]
    """
    The client of ModelTreeGUI must provide a node type that meets this API.
    Note that this is not the Node API for use by most of NE1, or even
    by TreeModel -- just for
    use specifically by ModelTreeGUI for nodes returned by its treemodel.

    Providing a node type can be done by extending this class, or implementing
    it yourself.

    @see: class Node in Utility.py, used as the superclass for NE1 model tree
          nodes, which defines an API which is (we hope) a superset of this one.
          It could in principle inherit from this class, and at least ought to
          define all its methods.

    @note: this class is not used (so far, 081216) except as documentation
           and in test code.
    """

    # Questions & comments about this API [bruce 070503, 070508] [updated 081217]:
    #
    # - it ought to include (and the code herein make use of) node.try_rename or so.
    #
    # - is Node.__init__ part of the API, or just a convenience place for a
    #   docstring about required instance variables?
    # - in Qt3 there *is* a Node API call to support renaming ("try_rename"
    #   or so). Why isn't it used or listed here?


    # New proposed policy relating open, openable, MT_kids, members
    # (see also their docstrings herein, revised when this comment was added):
    #
    # - if node.openable(), then regardless of node.open,
    #   node.MT_kids() value is meaningful, and doesn't depend on node.open.
    #   It's the sequence of child nodes to display under node when node is
    #   open. It will also be used to find picked nodes under node, even when
    #   node is not open, for the purpose of making MT operations safe when
    #   some picked nodes only occur inside non-openable unpicked nodes.
    #
    # - if not node.openable(), then regardless of node.open, node.MT_kids()
    #   should never be called (but see new docstring re what it should do
    #   if it's called then anyway).
    #
    # - some MT operations (defined in TreeMember.py) still use node.members
    #   (e.g. Group and Ungroup). This needs review whenever MT_kids can be
    #   anything other than .members for an openable node.
    #
    # Status: need to review defs of MT_kids and openable for this.
    # Then need to implement this policy throughout modelTree and Node classes.
    # Short term motivation is fixing bug 2948.
    #
    # [bruce 081217]


    # see MT_kids and __init__ docstrings for documentation of open and members
    open = False
    members = ()

    def __init__(self):
        """
        self.name MUST be a string instance variable.

        self.hidden MUST be a boolean instance variable.

        self.open MUST be a boolean instance variable.

        self.members is not part of this API since ModelTreeGUI doesn't
        care about it; however, current implem of TreeModel (its client)
        *does* care about it.

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
        # old comment, not recently reviewed as of 081217:
        # display_prefs is used in Group.node_icon to indicate whether a group is open or closed. It
        # is not used anywhere else. It is a dictionary and the only relevant key for it is "open".
        # [Addendum, bruce 070504: it also has a key 'openable'. I don't know if anything looks at
        #  its value at that key, but "not open but openable" vs "not open and not even openable"
        #  is a meaningful difference. The value of 'openable' is usually (so far, always)
        #  implicit in the Node's concrete subclass, so typical methods won't need to look at it.]
        raise Exception("overload me")

    def MT_kids(self, item_prefs = {}):
        """
        When self is openable, return a list of Nodes that the model tree
        should show as children of self, whenever self is openable and open.
        (The return value should not depend on whether self is open.)

        When self is not openable, it doesn't matter what this returns,
        but it should either be safe to call then, or should assert
        that self is openable (so as to raise an understandable exception).

        @note: self is open whenever self.open is true, and is openable
               whenever self.openable() is true.

        @see: self.members
        """
        #bruce 080108 renamed kids -> MT_kids, revised semantics;
        # note that so far this is not yet used in all necessary places
        #bruce 081217 revised semantics again
        raise Exception("overload me")

    def openable(self): #bruce 070508
        """
        Return True if tree widgets should display an openclose icon
        for self, False otherwise.

        When this returns true, the openclose icon must always be usable
        to indicate and change self.open, and when self.open, self's .MT_kids()
        must be displayed under self.

        When this returns false, no children should be displayed under self,
        regardless of self.open and of the return value of self.MT_kids().

        @note: specific nodes are permitted to change this method's return
               value over time, e.g. depending on user preference settings.
               They must ensure that, at any given time, all required
               constraints on its value vs. the use of self.MT_kids() are
               followed. For such changes to take effect, modelTree.mt_update()
               will generally need to be called; the modelTree code must
               ensure that mt_update is sufficient for that purpose.

        @note: even when openable returns false, self.open is permitted
               to be true, but self is still considered to be closed then.
        """
        raise Exception("overload me")
    pass

# end
