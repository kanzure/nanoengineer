# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ModelTreeGUI_api.py - API class for ModelTreeGui

@author: Will, Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from modelTree.Api import Api

# old comments by Will from his refactoring circa 2006:

# These base classes [various _api classes in this modelTree package]
# are JUST the API [external, and inter-object internal].

# Functionality is implemented by extending these base classes.

# Context menu events can rearrange the tree structure in various ways. Items in the model tree can be
# hidden or disabled or deleted. An item can be moved or copied from one place in the tree to
# another. These things are done by the customer, OUTSIDE the model tree, and then the customer
# gives the model tree a new structure. Aside from the context menus, the model tree does not make
# callbacks to the customer code.

# Customer code should depend ONLY on the API as presented, and treat it as a contract. Then any
# bugs are either API bugs and implementation bugs, and the implementation bugs become relatively
# isolated and easier to fix.

# http://en.wikipedia.org/wiki/Duck_typing describes how API compliance works in Python. In Java or
# C++, the only way to guarantee that class B complies with class A's API is for B to subclass A. In
# Python, there is no such compile-time check, Python just raises an exception if we try to use a
# method that isn't implemented.

# =============================
# Bruce's original intent was that this code should be useful for other trees besides the model tree.
# To do that, you should subclass ModelTreeGui below and redefine make_new_subtree_for_node() to refer to
# a new class that inherits _QtTreeItem. Perhaps the subclass of QItemDelegate could be a parameter of
# ModelTreeGui. [This comment is no longer correct now that _QtTreeItem's two roles, which never belonged
# together, are split into _our_QItemDelegate and (misnamed) _our_TreeItem. bruce 070525]
#
# How this was done previously was that the NE-1 model would define a method for creating the item for
# a Node.
#
# =============================
#
# How does renaming work in Qt 3?
#
# TreeWidget.slot_itemRenamed() is connected to Q3ListView.itemRenamed(). It accepts an item, a column
# number, and the new text. If everything is OK, it calls item.setText(col,newname). What I am not
# seeing is how the name gets from the Q3ListViewItem back to the Node. So renaming is a big mystery to
# me, and I'll ask Bruce about it later.

# ===

class ModelTreeGUI_api(Api): 
    """
    This should be a Qt4 widget that can be put into a layout.
    """
    # note: this classname and modulename contains "GUI" not "Gui",
    # like class ModelTreeGui someday ought to, but doesn't now.
    # [bruce 081216]

    def mt_update(self, nodetree = None): # in ModelTreeGUI_api
        """
        External code (or event bindings in a subclass, if they don't do enough repainting themselves)
        should call this when it might have changed any state that should
        affect what's shown in the tree. (Specifically: the ordering or grouping of nodes,
        or the icons or text they should display, or their open or selected state.) (BTW external
        code probably has no business changing node.open since it is slated to become a tree-
        widget-specific state in the near future.)
           If these changes are known to be confined to a single node and its children,
        that node can be passed as a second argument as a possible optimization
        (though as of 050113 the current implem does not take advantage of this).

        @warning: as of 080306 the implementations of this don't conform to the
                  argspec, since they don't even accept (let alone pay attention
                  to) the nodetree optional argument.
        """
        raise Exception("overload me")

    def repaint_some_nodes(self, nodes): #bruce 080507, for cross-highlighting
        """
        For each node in nodes, repaint that node, if it was painted the last
        time we repainted self as a whole. (Not an error if it wasn't.)
        """
        raise Exception("overload me")

    pass

# end
