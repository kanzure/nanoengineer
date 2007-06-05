# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
modelTreeGui.py - provide a Qt4-compatible Model Tree widget,
inherited by modelTree.py to provide NE1's Model Tree of Nodes.

$Id$

Goals:

There is now a clear simple API for the model tree, which amounts to a refactoring of the code
previously appearing in TreeView.py, TreeWidget.py, and modelTree.py. [For history, see the
modelTree.py docstring.]

The API needs to accomplish three things. First it must work in just this file with a very
restricted set of data, and in this context I [Will] need to bang on issues of selection, display, and
other GUI stuff. Second it needs to work with the uiPrototype.py stuff for the new user interface.
Third it needs to migrate into the NE-1 code cleanly, ideally with just a change of the filename.

Recent history:

Those goals were partly achieved, and in particular the API superclasses add a lot of clarity,
but in the implementation there were serious missing features and logic bugs... I have solved
some of these by bringing back some of the old code, and abandoning use of Qt's concept of selected
items, and rewriting the node-selection-related behaviors. In doing this, I added a few methods
to the APIs (not all of which are documented there -- see ##doc comments to find those that aren't).

There remain some serious cosmetic and performance bugs, relative to the Qt3 version, which I'm
still working on. [bruce 070508]

"""

import sys
from PyQt4 import *
from PyQt4.Qt import *
from assembly import assembly
from Utility import Group, Node
from debug import print_compact_traceback, print_compact_stack
from platform import fix_plurals
from HistoryWidget import quote_html
from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice
from widgets import makemenu_helper
import env

DEBUG0 = False # debug api compliance
DEBUG = False # debug selection stuff
DEBUG2 = False # mouse press event details
DEBUG3 = False # stack, begin, end, for event processing

# These base classes are JUST the API. Functionality is implemented by extending these base classes.

# Context menu events can rearrange the structure in various ways. Items in the model tree can be
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

#####################################
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

###################################################################
# Yet another experiment with testing API compliance in Python

def _inheritance_chains(klas, endpoint):
    if klas is endpoint:
        return [ (endpoint,) ]
    lst = [ ]
    for base in klas.__bases__:
        for seq in _inheritance_chains(base, endpoint):
            lst.append((klas,) + seq)
    return lst

# This little hack is a way to ensure that a class implementing an API does so completely. API
# compliance also requires that the caller not call any methods _not_ defined by the API, but
# that's a harder problem that we'll ignore for the moment.

class Api:
    def _verify_api_compliance(self):
        from types import MethodType
        myclass = self.__class__
        mystuff = myclass.__dict__
        ouch = False
        for legacy in _inheritance_chains(myclass, Api):
            assert len(legacy) >= 3
            api = legacy[-2]
            print api, api.__dict__
            for method in api.__dict__:
                if not method.startswith("__"):
                    assert type(getattr(api, method)) is MethodType
                    assert type(getattr(self, method)) is MethodType
                    this_method_ok = False
                    for ancestor in legacy[:-2]:
                        if method in ancestor.__dict__:
                            this_method_ok = True
                    if not this_method_ok:
                        print myclass, 'does not implement', method, 'from', api
                        ouch = True
        if ouch:
            raise Exception('Class does not comply with its API')

#############################################

class Ne1Model_api(Api):
    """API (and some default method implementations) for a Model Tree object."""
    
    def get_topnodes(self):
        """Return a list of the top-level nodes, typically assy.tree and assy.shelf for an assembly.
        """
        raise Exception('overload me')

    def make_cmenuspec_for_set(self, nodeset, optflag):
        """Return a Menu_spec list (of a format suitable for makemenu_helper)
        for a context menu suitable for nodeset, a list of 0 or more selected nodes
        (which includes only the topmost selected nodes, i.e. it includes no
        children of selected nodes even if they are selected).
           <optflag> can be 'Option' or None, in case menus want to include
        additional items when it's 'Option'.
           Subclasses should override this to provide an actual menu spec.
        The subclass implementation can directly examine the selection status of nodes
        below those in nodeset, if desired, and can assume every node in nodeset is picked,
        and every node not in it or under something in it is not picked.
        [all subclasses should override this]
        """
        raise Exception('overload me')

    def get_current_part_topnode(self): #bruce 070509 added this to API ##e rename?
        """Return a node guaranteed to contain all selected nodes, and be fast.
        """
        raise Exception('overload me')

    # helper methods -- strictly speaking these are now part of the API, but they have default implems
    # based on more primitive methods (which need never be overridden, and maybe should never be overridden).
    # [moved them into this class from modelTreeGui, bruce 070529]
    
    def recurseOnNodes(self, func, topnode = None, fake_nodes_to_mark_groups = False, visible_only = False ):
        """
        """
        #bruce 070509 new features: fake_nodes_to_mark_groups, visible_only
        if topnode is None:
            for topnode in self.get_topnodes():
                self.recurseOnNodes(func, topnode,
                                    fake_nodes_to_mark_groups = fake_nodes_to_mark_groups,
                                    visible_only = visible_only)
                continue
        else:
            func(topnode)
            if hasattr(topnode, 'members'):
                if not visible_only or topnode.open:                    
                    if fake_nodes_to_mark_groups:
                        func(0)
                    for child in topnode.members:
                        self.recurseOnNodes(func, child,
                                            fake_nodes_to_mark_groups = fake_nodes_to_mark_groups,
                                            visible_only = visible_only)
                        continue
                    if fake_nodes_to_mark_groups:
                        func(1)
            pass
        return
    
    def topmost_selected_nodes(self):
        """Return a list of nodes whose corresponding items are currently selected.
        [But not including any children of selected nodes. --bruce]
        """
        nodes = [self.get_current_part_topnode()]
        from ops_select import topmost_selected_nodes
        return topmost_selected_nodes(nodes)

    pass # end of class Ne1Model_api

class Node_api(Api):
    """The customer must provide a node type that meets this API. This can be done by extending this
    class, or implementing it yourself. [See also class Node in Utility.py, used as the superclass
    for NE1 model tree nodes, which defines an API which is (we hope) a superset of this one.
    This could in principle inherit from this class, and at least ought to define all its methods.]

    In addition to what appears here, a node that has child nodes must maintain them in a list
    called 'self.members'.
    """
    # There still needs to be an API call to support renaming, where the model tree is allowed to
    # change the Node's name.

    # Questions & comments about this API [bruce 070503, 070508]:
    #
    # - why doesn't it mention node.open or node.openable()?
    #   That omission might be related to some ###BUGS (inability to collapse group nodes).
    #   [I added them to the API but not yet fully to the code. bruce 070508]
    #
    # - how exactly must node.members and node.kids() be related?
    #   Right now this code may assume that they're always equal, and it may also assume that
    #   when they're nonempty the node is openable.
    #   What I think *should* be made true is that node.members is private, or at least read-only...
    #   OTOH kids is not yet different, not yet used much by other NE1 code, and a bad choice of attr name
    #   since it's too common a word for text search to work well.
    #
    # - it ought to include (and the code herein make use of) node.try_rename or so.
    #
    # - is Node.__init__ part of the API, or just a convenience place for a docstring
    #   about required instance variables?
    # - in Qt3 there *is* a Node API call to support renaming ("try_rename" or so).
    #   Why isn't it used or listed here?
    #
    # See also my comments in modelTree.__init__.
        
    def __init__(self):
        """self.name MUST be a string instance variable.
        self.hidden MUST be a boolean instance variable.
        self.open MUST be a boolean instance variable.
        There is no API requirement about arguments for __init__.
        """
        raise Exception('overload me')

    def pick(self):
        """select the object
        [extended in many subclasses, notably in Group]
        [Note: only Node methods should directly alter self.picked,
         since in the future these methods will sometimes invalidate other state
         which needs to depend on which Nodes are picked.]
        """
        raise Exception('overload me')

    def unpick(self):
        """unselect the object, and all its ancestor nodes.
        [extended in many subclasses, notably in Group]
        [Note: only Node methods should directly alter self.picked,
         since in the future these methods will sometimes invalidate other state
         which needs to depend on which Nodes are picked.]
        """
        raise Exception('overload me')

    def apply2picked(self, func):
        """Apply fn to the topmost picked nodes under (or equal to) self,
        but don't scan below picked nodes. See Group.apply2picked docstring for details.
        """
        raise Exception('overload me')

    def is_disabled(self):
        """MUST return a boolean"""
        raise Exception('overload me')

    def node_icon(self, display_prefs):
        """MUST return either a QPixmap or None"""
        # display_prefs is used in Group.node_icon to indicate whether a group is open or closed. It
        # is not used anywhere else. It is a dictionary and the only relevant key for it is "open".
        # [Addendum, bruce 070504: it also has a key 'openable'. I don't know if anything looks at
        #  its value at that key, but "not open but openable" vs "not open and not even openable"
        #  is a meaningful difference. The value of 'openable' is usually (so far, always)
        #  implicit in the Node's concrete subclass, so typical methods won't need to look at it.]
        raise Exception('overload me')

    def drop_on_ok(self, drag_type, nodes):
        """Say whether 'drag and drop' can drop the given set of nodes onto this node, when they are
        dragged in the given way
        """
        raise Exception('overload me')

    def drop_on(self, drag_type, nodes):
        """After a 'drag and drop' of type 'move' or 'copy' (according to drag_type), perform the
        drop of the given list of nodes onto this node. Return any new nodes this creates (toplevel
        nodes only, for copied groups).
        """
        raise Exception('overload me')

    def kids(self, item_prefs):
        """Return a list of Nodes that are a child of this Node.
        """
        raise Exception('overload me')

    def openable(self): #bruce 070508
        """Return True if tree widgets should display an openclose icon for this node, False otherwise.
        """
        raise Exception('overload me')        
    pass

class ModelTreeGui_api(Api):
    """This should be a Qt4 widget that can be put into a layout.
    """
    def update_item_tree(self, unpickEverybody = False): # in ModelTreeGui_api
        """Removes and deletes all the items in this list view and triggers an update. Previously
        this was the 'clear' method in Q3ListView. 
        """
        ###REVIEW: in the implementation below, this also creates a new tree of items given a root node.
        # I guess this means the meaning of this method in this API was changed since the above was written.
        # (So has the name -- it was called 'clear' until bruce 070509. Also the option was not listed in this API.)
        raise Exception('overload me')

    def topmost_selected_nodes(self): # in ModelTreeGui_api
        "return a list of all selected nodes as seen by apply2picked, i.e. without looking inside selected Groups"
        # this should really be called topmost_PICKED_nodes: nodes are picked, items are selected
        raise Exception('overload me')

    def mt_update(self, nodetree = None): # in ModelTreeGui_api
        """External code (or event bindings in a subclass, if they don't do enough repainting themselves)
        should call this when it might have changed any state that should
        affect what's shown in the tree. (Specifically: the ordering or grouping of nodes,
        or the icons or text they should display, or their open or selected state.) (BTW external
        code probably has no business changing node.open since it is slated to become a tree-
        widget-specific state in the near future.)
           If these changes are known to be confined to a single node and its children,
        that node can be passed as a second argument as a possible optimization
        (though as of 050113 the current implem does not take advantage of this).
        """
        raise Exception('overload me')
    pass

####################### End of the API #############################
####################################################################
####################################################################


####################################################################
####################################################################
#################### Implementation ################################

_ICONSIZE = (22, 22)

ITEM_HEIGHT = _ICONSIZE[1] # in theory, these need not be the same, but other values are untested [bruce 070529 guess]


class _our_QItemDelegate(QItemDelegate):
    #bruce 070525 renamed this from _QtTreeItem and split away all tree-item functionality,
    # leaving it only in _our_TreeItem

    # Extending QItemDelegate allows you to customize the paint() method. We need to do this because
    # we have a combination of requirements that weren't anticipated in Qt 4.1; more might be
    # available in Qt 4.2.
    #
    # QTreeWidget can give you icons and a tree structure, but you don't get much ability to
    # customize things like shear, and you can't force a repaint of the model tree when you want it.
    # QTreeView provides a forced repaint with the setModel() method (so that's the one we use).

    # update, bruce 070523:
    # WARNING: the Qt docs suggest that we only need one QItemDelegate (our rootItem), not a tree of them.
    # We were constructing an entire tree of items of this class, but the docs and some other evidence
    # hinted that most methods of it are only called on the rootItem. So to test this, I split it into
    # this class for the rootItem alone, and a much simpler _nonRootItem class (defined just below this one)
    # [later renamed to _our_TreeItem and used for root item too]
    # for all other items, and this seems to work fine. So, this class is really mashing together two
    # roles or functions that don't belong together -- an item for our own use, and a QItemDelegate.
    # These roles are still mixed together and confused for the rootItem itself, but not anymore (as of now)
    # for the other items (whose class is probably not really needed at all).
    # (Note: I'm using the term "roles" here generically -- no relation to Qt's color(?) roles,
    #  also mentioned in some of this code.)
    #
    # WARNING: It's not yet clear which attribute names are ours vs. Qts (eg childItems, parentItem).
    # Guess: they're all ours.
    
    def __init__(self, modeltreegui): ## was: self, node, parent = None):
        QItemDelegate.__init__(self, modeltreegui)
        self.view = modeltreegui #bruce 070525: do this here, not in caller

    def sizeHint(self, styleOption, index): ###REVIEW: why is this correct (or is it), since it only returns an icon size?
        return QSize(_ICONSIZE[0], ITEM_HEIGHT)

    def paint(self, painter, option, index, pos = None): #k is this our methodname & API, or Qt's?
        """
        """
        # figure out drawing position
        if pos is not None:#bruce 070511 new feature
            x, y = pos
        else:
            x, y = option.rect.x(), option.rect.y() ##k what is option? it seems we use it to determine the position of drawing...
##        if DEBUG3:
##            print "option is %r in _our_QItemDelegate.paint" % (option,)###
            ##option is <PyQt4.QtGui.QStyleOptionViewItem object at 0x4cf0228> in _our_QItemDelegate.paint

        # Note: I don't know what coordinate system x, y are in --
        # relative to self, or to item; and, in scrolled tree coords or its viewports coords. [bruce comment]

        # figure out what item to draw, and its node
        item = index.internalPointer()
        
        node = item.node
        
        _paintnode(node, painter, x, y, self.view) # self.view is a widget used for its palette

        return # from paint

    # Methods to support renaming on double click; index tells which item is being renamed
    # (See also the uses of QLineEdit in the QScrollArea version, below.
    #  WARNING: they duplicate some of this code.)

    def createEditor(self, parent, option, index):
        qle = QLineEdit(parent)
        self.setEditorData(qle, index)
        return qle

    def setEditorData(self, lineEdit, index):
        value = str(index.model().data(index, Qt.DisplayRole).toString())
        lineEdit.setText(value)

    def setModelData(self, lineEdit, model, index):
        model.setData(index, QVariant(lineEdit.text()))

    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        rect.setX(rect.x() + _ICONSIZE[0])
        qfm = QFontMetrics(editor.font())
        width = qfm.width(editor.text()) + 10
        width = min(width, rect.width() - _ICONSIZE[0])
        width = min(width, self.parent().width() - 50 - rect.x())
        rect.setWidth(width)
        editor.setGeometry(rect)

    pass # end of class _our_QItemDelegate

_cached_icons = {} #bruce 070529 presumed optimization

def _paintnode(node, painter, x, y, widget): #bruce 070529 split this out
    """Draw node in painter.
    x,y are coords for topleft of type-icon.
    widget (the modelTreeGui) is used for palette.
    """
    ## print "_paintnode",node, painter, x, y, widget
        # x is 20, 40, etc (indent level)
        # y is 0 for the top item, incrs by 22 for other items -- but this varies as we scroll.
    
    # find state of node which determines how we draw it
    selected = node.picked
    disabled = node.is_disabled() ### might be slow!
    display_prefs = display_prefs_for_node(node)
        # someday these might also depend on parent node and/or on ModelTreeGui (i.e. widget)
    
    node_icon = node.node_icon(display_prefs) # a QPixmap object
    try:
        pixmap = _cached_icons[node_icon]
    except KeyError:
        # print "making pixmap for node_icon", node_icon # should occur once per unique icon per session
        pixmap = QIcon(node_icon).pixmap(_ICONSIZE[0], _ICONSIZE[1]) # vary the size
        _cached_icons[node_icon] = pixmap
        pass
    
    # draw it (icon and label), possibly transforming the painter before and during this.
    
    # Note about save/restore: Qt 4.1 doc says:
    #  After painting, you should ensure that the painter is returned to the state it was supplied in
    #  when this function was called. For example, it may be useful to call QPainter::save()
    #  before painting and QPainter::restore() afterwards.

    need_save = disabled or selected #bruce 070529 presumed optimization

    if need_save:
        painter.save()

    if disabled: # before
        # draw icon and label in slanted form
        painter.shear(0, -0.5)
        painter.translate(0.5 * y + 4, 0.0)
            
    painter.drawPixmap(x, y, pixmap)

    if selected: # before
        # draw a selection color as text bg color
        ###BUG: should use color role so it depends on app being in bg or fg (like it does for native QTreeView selectedness)
        # (note: this used to be done before drawing the icon, but even then it did not affect the icon.
        #  so it would be ok in either place.)
##        background = painter.background()
##        backgroundMode = painter.backgroundMode()
        painter.setBackground(widget.palette().highlight())
        painter.setBackgroundMode(Qt.OpaqueMode)

    yoffset = _ICONSIZE[1] / 2 + 4
    painter.drawText(x + _ICONSIZE[0] + 4, y + yoffset, node.name)

    if need_save:
        painter.restore()

    # About fixing bug 2372 by drawing the "red donut" to show the current Part:
    # the following code works, and would be correct if we ported the sg and condition code,
    # but it looks too ugly to consider using, IMHO (on my iMac G5).
    # Maybe we should draw some sort of icon for this? [bruce 070514]
    #
    ##    ## sg = assy.current_selgroup_iff_valid()
    ##    dotcolor = Qt.red
    ##    if 1: ### sg == node and node != assy.tree:
    ##        painter.save()
    ##        painter.setPen(QPen(dotcolor, 3)) # 3 is pen thickness; btw, this also sets color of the "moving 1 item" at bottom of DND graphic!
    ##        h = 9
    ##        dx,dy = -38,8 # topleft of what we draw; 0,0 is topleft corner of icon; neg coords work, not sure how far or how safe
    ##        painter.drawEllipse(x + dx, y + dy, h, h)
    ##        painter.restore()
    return

# ==

class _our_TreeItem: #bruce 070523 experiment; works; now used for root items too, 070525
    "use this for all tree items (root or not), to test theory that Qt never sees them directly or cares about them -- seems true"
    def __init__(self, node, parent):
        # parent is either an item of this class, or a modelTreeGui object
        self.node = node
        self.childItems = []
        assert parent is not None
        if hasattr(parent, 'childItems'): #k not sure if this is true for a modelTreeGui object
            parent.childItems.append(self)
        self.parentItem = parent

    def __repr__(self):
        return '<%s \"%s\">' % (self.__class__.__name__, self.node.name)

    def height(self): #bruce 070511 for use by other methods here
        return ITEM_HEIGHT
    
    pass # end of class _our_TreeItem

class _our_TreeItem_NEW(object): #bruce 070525 incremental (lazy) version of that.
    # Note: doesn't memoize, since node structure can change.
    def __init__(self, node, modeltreegui):
        self.node = node
        self._modeltreegui = modeltreegui
        self._modeltreegui.item_to_node_dict[self] = node
        self._modeltreegui.node_to_item_dict[node] = self

    def _get_parentItem(self):
        # assume item tree structure corresponds exactly to node tree, at least for parent/dad
        return self._modeltreegui.node_to_item( self.node.dad ) # note: has special case for dad of toplevel nodes
    
    parentItem = property( _get_parentItem)

    def _get_childItems(self):
        node = self.node
        try:
            ###k what if node is collapsed? old code stores childItems then anyway...
            # not sure if new code can safely optim by not yet returning them
            children = node.members
        except AttributeError:
            return []
        return map( self._modeltreegui.node_to_item, children )

    childItems = property( _get_childItems)

    def __repr__(self):
        return '<%s \"%s\">' % (self.__class__.__name__, self.node.name)

    def height(self): #bruce 070511 for use by other methods here
        return ITEM_HEIGHT
    
    pass # end of class _our_TreeItem_NEW


# What attrs does the current code use in that class? [as of 070525]
# Text search for item.xxx or Item.xxx (covers various localvars) to find:
# - item.node -- used all the time; maybe the items always come from index.internalPointer (not sure)
# - item.height() (constant)
# - item.childItems -- used in _QtTreeModel .__init__, .index, .parent, .rowCount, and in modelTreeGui.recurseOnItems
# - item.parentItem -- used in _QtTreeModel.parent
# To make it more incremental, we'd want to compute childItems and parentItem as needed. Should be easy using node to item dict.
# But we also need to create indices as needed. Not sure how easy that is. We'd need to update the treemodel's index_for_item dict.
# Also worth knowing -- how long do these item objects last? Where are they grabbed from for use?
#
# false alarms from that text search:
# - not item.setText(col,newname) -- it's only in a comment about Qt3 code)
# - not item.width(fontmetrics, self, 0) -- only used in some Qt3 code for DND drag graphic, not yet ported to Qt4

####################################################################

# Here is a potentially confusing point. There are two levels of model. Because of
# Qt's model/view paradigm, we need a "Qt model" separate from the view of the data
# in the model. But all that stuff is packaged into something that looks like a
# view, from NE-1's perspective.

class _QtTreeModel(QAbstractItemModel): # see also _QtTreeModel_NEW variant, which overrides two of our methods
    def __init__(self, root_Item): # note: different in _QtTreeModel_NEW
        """Create a _QtTreeModel containing the tree of items
        (which must already exist and be complete) starting at root_Item.
        Assign indices to the non-root items and store them in self.index_for_item[item].
        """
        QAbstractItemModel.__init__(self)
        self.root_Item = root_Item
        self.index_for_item = { }   # maps items to indexes [bruce 070525 renamed this from indexdict]
        def helper(item): ##, depth):
            row = 0
            for item in item.childItems:
                self.index_for_item[item] = self.createIndex(row, 0, item)
                    # Qt method; args are: row, column, internalPointer == item
                row += 1
                helper(item) ##, depth+1)
        helper(root_Item) ##, 0)

    # We don't need indexToItem because we can use index.internalPointer()...
    # unless index might be invalid, in which case, use this:

    def indexToItem(self, index): #bruce 070525
        if not index.isValid():
            item = self.root_Item
        else:
            item = index.internalPointer()
        return item

    def itemToIndex(self, item): # note: different in _QtTreeModel_NEW
        try:
            return self.index_for_item[item]
        except KeyError:
            return QModelIndex()

    # The following methods are the official API required by QTreeView's idea of how
    # QAbstractItemModel should work.

    ###REVIEW:
    # - would these Qt methods be useful?
    #   Qt doc: http://doc.trolltech.com/4.2/qabstractitemmodel.html
    #   [i forget if these are methods on this class or some related one,
    #    or whether it was using them or overriding them that I thought might be useful #k]
    #   - reset
    #   - modelReset
    #   - supportedDropActions (only copy, by default)
    # - for hasChildren and rowCount, some mailing list web pages have advice and Qt bug reports
    #   [ref is probably elsewhere in the code].
    
    def columnCount(self, parent):
        return 1
    
    def data(self, index, role): # usually this is the node.name
        if not index.isValid():
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()
        item = index.internalPointer()
        return QVariant(item.node.name)

    def flags(self, index):
        assert index.isValid()
        r = Qt.ItemIsEnabled ## | Qt.ItemIsSelectable
            ###REVIEW: is ItemIsSelectable ok given that we want to stop using Qt idea of selection?
                # probably ok, but turn it off to see if that helps with anything, eg the two-clipboard bug. [bruce 070525]
            ###REVIEW: do we want to use other flags here, eg to control whether node can be DND source and/or target?
        if index.internalPointer().node.rename_enabled():
            r |= Qt.ItemIsEditable
        return r

    def setData(self, index, qvar):
        item = index.internalPointer()
        item.node.name = str(qvar.toString()) ###BUG: this needs to go through node.try_rename. (Like this, it'll fail on unicode.)
            # But when it does, the caller may also need revision, since a modified name might be stored here.

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.root_Item.node.name)
        return QVariant()

    def index(self, row, column, parent): ### needs review, not yet fully understood by bruce
        # parent is an index; guess: come up with a requested child index
        parentItem = self.indexToItem(parent)
        childItem = parentItem.childItems[row]
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            print "childItem false in _QtTreeModel.index -- i thought this would not happen"
            return QModelIndex()

    def parent(self, index): ### needs review, not yet fully understood by bruce
        if not index.isValid():
            return QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parentItem
        if parentItem == self.root_Item:
            return QModelIndex()
        if parentItem.parentItem is None:
            parentRow = 0
        else:
            parentRow = parentItem.parentItem.childItems.index(parentItem)
        return self.createIndex(parentRow, 0, parentItem)

    def rowCount(self, parent):
        # in QStandardItem doc: "Returns the number of rows in the model that contain items with the given parent"
        parentItem = self.indexToItem(parent)
        return len(parentItem.childItems)

    def hasChildren(self, parent): #bruce 070504 guess; Qt seems to use this to decide whether to display the openclose decoration
        # see also, in Qt dos: fetchmore, canfetchmore (sp?)
        parentItem = self.indexToItem(parent)
        if parentItem is self.root_Item:
            return True
        else:
            node = parentItem.node
            return node.openable() ###REVIEW: is it better to return False for some or all Groups with no children, e.g. Clipboard??
        pass
    
    pass # end of class _QtTreeModel

# ==

# experimental new version of that, works totally differently (lazily, incrementally, keeps items more private)
# [bruce 070523-25; unfinished, not yet usable, tho a live debug_pref tries to use it; ABANDONED as of 070530 and will be removed]

class _QtTreeModel_NEW( _QtTreeModel):
    def __init__(self, root_Item):
        #e might be better to pass rootnode, create root_Item here
        """... incrementally follow changes in its data or node subtree
        """
        QAbstractItemModel.__init__(self)
        self.root_Item = root_Item ### RENAME back to rootItem I think
        self.index_for_item = { }   # maps items to indexes; lazily filled, so semi-private [bruce 070525 renamed this from indexdict]
        return

##    def _scan_node(self, node): # ???
##        "scan a node to find out all data inside it that might make us want to send a dataChanged signal for it (not recursive)"
##        return (node.name, )####STUB, needs picked, icon, members, open (or members iff open?), etc... note, alg not really designed

    def itemToIndex(self, item):
        try:
            return self.index_for_item[item]
        except KeyError:
            if item is self.root_Item:
                return QModelIndex() ###k can't we just store this one? review all uses of the dict, to see
            # generate new indexes for all siblings at once
            parentItem = item.parentItem
            row = 0
            for item1 in parentItem.childItems:
                self.index_for_item[item1] = self.createIndex(row, 0, item1)
                    # Qt method; args are: row, column, internalPointer == item1
                row += 1
            return self.index_for_item[item] # KeyError if still not set (indicates bug in node tree structure)
        pass

    pass # end of class _QtTreeModel_NEW

####################################################################

_debug_mt_update_counter = 0

_buttons = dict(left = Qt.LeftButton,
                mid = Qt.MidButton,
                right = Qt.RightButton )

_modifiers = dict(shift = Qt.ShiftModifier,
                  control = Qt.ControlModifier,
                  alt = Qt.AltModifier,
                  meta = Qt.MetaModifier,
                  keypad = Qt.KeypadModifier,
                  X11_Mode_switch = Qt.GroupSwitchModifier )
    # http://www.riverbankcomputing.com/Docs/PyQt4/html/qt.html says:
    #   Note: On Mac OS X, the ControlModifier value corresponds to the Command keys on the Macintosh keyboard,
    #   and the MetaModifier value corresponds to the Control keys. The KeypadModifier value will also be set
    #   when an arrow key is pressed as the arrow keys are considered part of the keypad.
    # Thus, on any platform we can use ControlModifier for de-select, but context menu requests on the Mac
    # may involve either RightButton or MetaModifier. (Also, Qt seems to mess them up in a complicated way,
    # splitting them into an event with inconsistent button/buttons flags (LMB and RMB respectively), followed
    # by a contextMenuEvent call, at least if we don't use setContextMenuPolicy.
    
def describe_buttons(buttons):
    return _describe( int(buttons), _buttons)
    
def describe_modifiers(modifiers):
    return _describe( int(modifiers), _modifiers)

def _describe( flags, name_val_dict):
    origflags = flags
    flags = int(flags)
    res = []
    items = name_val_dict.items()
    items.sort() #e suboptimal order
    for name, val in items:
        val = int(val)
        if val & flags:
            res.append(name)
            flags = flags &~ val
    if flags:
        res.append("unknown flags %#x" % flags)
    desc = ", ".join(res) # might be empty
    return "%#x (%s)" % (int(origflags), desc)

def describe_index(index):
    return "(%r, %r, %r)" % (index.row(), index.column(), index.internalPointer()) ##k

# ==

# Things can be simpler if we admit that display_prefs don't yet depend on the ModelTreeGui object.
# So for now I'm pulling this out of that object, so _our_QItemDelegate.paint can access it without having a pointer to that object.
# I'm also optimizing it, since it'll be called a lot more often now.
# (Even better would be to optimize the node_icon API so we can pass .open directly.
#  We don't want to let the node use its own .open, in case in future we show one node in different MTs.)
# [bruce 070511]

def display_prefs_for_node(node):
    """Return a dict of the *incremental* display prefs for the node,
    relative to whatever its parent passes as display prefs for its own kids.
    Any prefs that it should inherit from its parent's env should be left out of this dict.
    The complete set of display prefs can be used by node_icon to decide what icon the treeview
    should display for this node. (It can also use the node class or state.)
       In current code, the only thing this needs to include is whether this node
    is openable, and if so, whether it's open.
    [Subclasses can override this.]
    [Using this cumbersomeness just to say whether the item is open
     is not worthwhile in hindsight. Fix it sometime. #e]
    """
    if node.openable():
        if node.open:
            return _DISPLAY_PREFS_OPEN
        else:
            return _DISPLAY_PREFS_CLOSED
    else:
        return _DISPLAY_PREFS_LEAF
    pass

_DISPLAY_PREFS_OPEN   = dict(openable = True, open = True)
_DISPLAY_PREFS_CLOSED = dict(openable = True, open = False)
_DISPLAY_PREFS_LEAF   = {}

# ==

class DoNotDrop(Exception): pass

class ModelTreeGui_common(ModelTreeGui_api): #bruce 070529 split this out of class ModelTreeGui
    """The part of our model tree implementation which is the same
    for either type of Qt widget used to show it.
    """
    def __init__(self, win, ne1model):
        self.win = win
        self.ne1model = ne1model
        ne1model.view = self #e should rename this attr of ne1model
        self._mousepress_info_for_move = None
            # set by any mousePress that supports mouseMove not being a noop, to info about what that move should do #bruce 070509
        self._ongoing_DND_info = None # set to a tuple of a private format, during a DND drag (not used during a selection-drag #k)
        self.setAcceptDrops(True)
        if DEBUG0:
            self._verify_api_compliance()

        # Make sure certain debug_prefs are visible from the start, in the debug_prefs menu --
        # but only the ones that matter for the MT implem we're using in this session.
        # WARNING (kluge): the defaults and other options are duplicated code, but are only honored in these calls
        # (since these calls happen first).

        # these are used in both MT implems:
        self.debug_pref_use_fancy_DND_graphic()
        self.MT_debug_prints()

        if debug_pref_use_old_MT_code():
            # these are only used in ModelTreeGui_QTreeView -- in a cleanup we could do this in its init method, not here:
            debug_pref("MT debug: setDirtyRegion", Choice(["large","small","none"]), non_debug = True, prefs_key = True)
            debug_pref("MT debug: updateGeometry", Choice_boolean_True, non_debug = True, prefs_key = True)
            debug_pref("MT debug: scrollToBottom", Choice_boolean_True, non_debug = True, prefs_key = True)
            debug_pref("MT debug: set_scrollpos",  Choice_boolean_True, non_debug = True, prefs_key = True)
            debug_pref("MT debug: show after replace", Choice_boolean_True, non_debug = True, prefs_key = True)
            debug_pref("MT debug: disable replace_items",      Choice_boolean_False, non_debug = True, prefs_key = True)
            debug_pref("MT debug: disable _remake_contents_0", Choice_boolean_False, non_debug = True, prefs_key = True)
            debug_pref("MT debug: disable scrollBar.valueChanged()", Choice_boolean_False, non_debug = True, prefs_key = True)
            debug_pref("MT debug: incremental update_item_tree?",    Choice_boolean_False, non_debug = True, prefs_key = True)
        return
    
    def topmost_selected_nodes(self): #bruce 070529 moved method body into self.ne1model
        """Return a list of nodes whose corresponding items are currently selected,
        but not including any children of selected nodes.
        """
        return self.ne1model.topmost_selected_nodes()

    def MT_debug_prints(self):
        return debug_pref("MT debug: debug prints", Choice_boolean_False, prefs_key = True)
    
    def display_prefs_for_node(self, node):
        """For doc, see the global function of the same name."""
        return display_prefs_for_node(node) #bruce 070511 revised this to make it a global function

    # == DND start methods

    def _start_DND(self, item, option_modifier):
        thisnode = item.node
        drag_type = option_modifier and 'copy' or 'move'
            #bruce 070509 kluge condition, not sure fully correct (Qt3 code used fix_event then looked for MidButton)
            ###REVIEW: what sets the drag cursor -- does it redundantly compute this? Or does the cursor think it's *always* copy?
        nodes = self._dnd_nodes
            # set in mousepress, using info we no longer have
            # (due to its having already altered the selection)
        
        # now filter these nodes for the ones ok to drag, in the same way the Qt3 code did --
        # and not in every drag move event method [bruce 070509]
        nodes = self.filter_drag_nodes( drag_type, nodes ) # might be None
        if not nodes: # whether None or []
            return # message already emitted (if one is desired)

        # work around visual bug due to unwanted deselection of some of these nodes (during mousePressEvent)
        for node in self.topmost_selected_nodes():
            node.unpick()
        for node in nodes:
            node.pick()
        self.mt_update()
        # if that doesn't work, try self.repaint()

        self._ongoing_DND_info = (nodes, drag_type)

        # as a temporary workaround for the DND graphic being inadequate,
        # at least print a decent sbar message about it.

        # make up some text to be dragged in case the custom pixmap doesn't work or is nim
        dragobj_text = "%s %d item(s)" % (drag_type, len(nodes)) # e.g. "copy 5 item(s)"
        dragobj_text = fix_plurals(dragobj_text) # e.g. "copy 5 items" or "move 1 item" -- no "ing" to keep it as short as possible

        # make the dragobj [move sbar code above this? #e]
##        dragsource = self
##        dragobj = QTextDrag( dragobj_text, dragsource)
##            # \n and \r were each turned to \n, \n\r gave two \ns - even in "od -c"; as processed through Terminal
        dragobj = QDrag(self)
        mimedata = QMimeData()
        mimedata.setText("need a string here for a valid mimetype")
        dragobj.setMimeData(mimedata)

        pixmap = self.get_pixmap_for_dragging_nodes(drag_type, nodes)
        if pixmap:
            dragobj.setPixmap(pixmap)

        sbar_text = self.get_whatting_n_items_text( drag_type, nodes)
        self.statusbar_msg( sbar_text)

        dragobj.setHotSpot(QPoint(-18, 8)) #bruce 070514 tweak hotspot
        requested_action = {'copy':Qt.CopyAction, 'move':Qt.MoveAction}[drag_type]
            #bruce 070514 fix bug in DND cursor copy/move indication
        dragobj.start( requested_action)
        
        return # nodes

    def filter_drag_nodes(self, drag_type, nodes): #bruce 070509 copied this from Qt3 TreeWidget.py [#k same as in Qt4 TreeWidget??]
        """See which of the given nodes can be dragged (as a group) in the given way.
        Return a subset of them to be actually dragged
        (having emitted a warning, if desired, if this is not all of them),
        or someday perhaps a processed version of them (e.g. you could pre-make copies for a 'copy' drag),
        or None (*not* just a list [] of 0 nodes to drag! that might be possible to drag!)
        if you want to refuse this drag (also after emitting a suitable warning).
        """
        if drag_type == 'move':
            nodes_ok = filter( lambda n: n.drag_move_ok(), nodes)
        else:
            nodes_ok = filter( lambda n: n.drag_copy_ok(), nodes)
        oops = len(nodes) - len(nodes_ok)
        if oops:
            ## msg = "some selected nodes can't be dragged that way -- try again" ###e improve msg
##            msg = "The Part can't be moved" # kluge: this is the only known case! (that I can remember...) #e generalize this
##            self.redmsg(msg)
            #bruce 070509 commented that out, since I think it will often happen by accident for "small move onto self"
            # note: self.redmsg is probably not yet defined
            return None
        return nodes_ok # same as nodes for now, but we might change above code so it's not

    def debug_pref_use_fancy_DND_graphic(self):
        return debug_pref("Model Tree: use fancy DND graphic?", Choice_boolean_True, non_debug = True, prefs_key = True)
    
    def get_pixmap_for_dragging_nodes(self, drag_type, nodes):
        if self.debug_pref_use_fancy_DND_graphic():
            pixmap = self.get_pixmap_for_dragging_nodes_Qt3(drag_type, nodes)
        else:
            # stub version, just the icon from the first node
            display_prefs = self.display_prefs_for_node(nodes[0]) #bruce 070504 bugfix (partial fix only)
            pixmap = nodes[0].node_icon(display_prefs)
        return pixmap

    def get_whatting_n_items_text(self, drag_type, nodes):
        "return something like 'moving 1 item' or 'copying 5 items'"
        ing_dict = { "move":"moving", "copy":"copying" }
        whatting = ing_dict[ drag_type] # moving or copying?
        return fix_plurals( "%s %d item(s)" % (whatting, len(nodes)) )
            # not quite the same as the shorter text for the QDragObject itself;
            #e might become more different in the future if we include the class
            # when they're all nodes of the same subclass...

    def statusbar_msg(self, msg):
        #e should store the current one for this widget, to share sbar with other widgets;
        # or better, the method we're calling should do that for all widgets (or their parts) in a uniform way
        env.history.statusbar_msg( msg)

    statusbar_message = statusbar_msg #bruce 070531; we should rename all methods of that name like this, after A9 goes out
    
    # == Qt3 code for drag graphic, not yet ported, used only if debug_pref set [copied from Qt3/TreeWidget.py, bruce 070511]

    def get_pixmap_for_dragging_nodes_Qt3(self, drag_type, nodes):        
        #e [also put the drag-text-making code in another method near here? or even the dragobj maker?
        # or even the decision of what to do when the motion is large enough (ie let drag_handler role be only to notice that,
        # not to do whatever should be done at that point? as if its role was to filter our events into higher level ones
        # where one of them would be enoughMotionToStartADragEvent?] ###e yes, lots of cleanup is possible here...
        """Our current drag_handler can call this to ask us for a nice-looking pixmap
        representing this drag_type of these nodes,
        to put into its QDragObject as a custom pixmap.
        If we're not yet sure how to make one, we can just return None.
        """
        listview = self
        ##pixmap = QPixmap("/Nanorex/Working/cad/src/butterfly.png") # this works
        ##print pixmap,pixmap.width(),pixmap.height(),pixmap.size(),pixmap.depth()
        w,h = 160,130
        
        if 1:
            # but that's not good if len(nodes) is large, so use the following;
            # note that it depends on the details of hardcoded stuff in other functions
            # and those don't even have comments warning about that! ###
            # [bruce 050202 10:20am]:
            item = self.nodeItem(nodes[0]) # Grab a node to find out it's height
            ih = item.height()
            h = max(1,min(3,len(nodes))) * ih + ih # the last 24 is a guess for the text at the bottom
            w = self.get_drag_pixmap_width(nodes)

            if len(nodes)>3:
                h += 10 # for the "..."
            pass
        
        pixmap = QPixmap(w,h) # should have size w,h, depth of video mode, dflt optimization
        
        ##print pixmap,pixmap.width(),pixmap.height(),pixmap.size(),pixmap.depth()
        ## pixmap.fill(Qt.red) # makes it red; what's dragged is a pretty transparent version of this, but red... (looks nice)

        # CAREFUL: calling pixmap.fill() with no arguments creates problems
        # on Windows and Linux.  Text will not be drawn.  Be sure to include
        # a QColor argument so that the QPainter's setPen color can work 
        # as expected.  Mark 050205
        #
        #pixmap.fill() # makes pixmap white, but text can't be drawn

        ## pixmap.fill(listview,0,0)
        ## following would fill with this widget's bgcolor...
        ## but it actually looks worse: very faint stripes, all faintly visible
        
        p = QPainter(pixmap)

        # Determine the pixmap's background and text color
        if 1: ## sys.platform == 'darwin': # Mac
            hicolor = Qt.white
            textcolor = Qt.black
# Note: I disabled the following special case, since it's not yet ported to Qt4 (it caused bug 2395) -- bruce 070514
##        else: # Window and Linux
##            colorgroup = listview.palette().active()
##            hicolor = QColor (colorgroup.highlight())
##            textcolor = QColor (colorgroup.highlightedText())
        
        pixmap.fill(hicolor) # Pixmap backgroup color
        p.setPen(textcolor) # Pixmap text draw color

        try:
            self.paint_nodes(p, drag_type, nodes)
            return pixmap
        except:
            p.end() # this is needed to avoid segfaults here
            print_compact_traceback("error making drag-pixmap: ")
            return None
        pass
    
    def paint_node(self, p, drag_type, node):
        "paint one node's item into QPainter p, and translate it down by the item's height"
        #e someday also paint the little openclose triangles if they are groups?
        #e unselect items first, at least for copy?
        item = self.nodeItem(node)
        width = self.paint_item( p, item) # was 99 for one example -- note, font used was a bit too wide
        height = item.height() # was 24
        p.translate(0,height)
        return width, height
            #btw exception in above (when two subr levels up and different named vars) caused a segfault!
            # [before we caught exception, and did p.end(), in routine creating painter p]
            ##Qt: QPaintDevice: Cannot destroy paint device that is being painted.  Be sure to QPainter::end() painters!
            ##NameError: global name 'item' is not defined
            ##Segmentation fault
            ##Exit 139
            # This means I need to catch exceptions inside the functions that make painters!
            # And keep the painters inside so they refdecr on the way out.
            # (Or actually "end" them... in fact that turns out to be needed too.)
        
    def paint_nodes(self, p, drag_type, nodes):
        "paint a dragobject picture of these nodes into the QPainter p; if you give up, raise an exception; return w,h used??"
        nn = len(nodes)
        if not nn:
            print nodes,"no nodes??" # when i try to drag the clipboard?? because unselected.
            # need to filter it somehow... should be done now, so this should no longer happen.
            # also the history warning is annoying... otoh i am not *supposed* to drag it so nevermind.
            return
        if nn >= 1:
            self.paint_node( p, drag_type, nodes[0])
        if nn >= 2:
            self.paint_node( p, drag_type, nodes[1])
        if nn >= 4: # yes, i know 4 and 3 appear in reversed order in this code...
            # put in "..."
            p.drawText(0,6," ...") # y=6 is baseline. It works! Only required 5 or 6 steps of directed evolution to get it right.
            p.translate(0,10) # room for a "..." we plan to put in above # 8 is a guess
        if nn >= 3:
            self.paint_node( p, drag_type, nodes[-1])
        #e also put in the same text we'd put into the statusbar
        text = self.get_whatting_n_items_text(drag_type, nodes)
        item = self.nodeItem(nodes[0]) # Grab a node to find out it's height
        h = item.height()
        w = self.get_drag_pixmap_width(nodes)
        flags = 0 # guess
        p.drawText(4,4,w,h,flags,text) # in this drawText version, we're supplying bounding rect, not baseline.
            #e want smaller font, italic, colored...
        return

    def get_drag_pixmap_width(self, nodes):
        return 168 ###STUB
    
        ## pt = QPainter(self, True) # Qt3 version
        #print "before QP"
        pt = QPainter(self) # this prints:
            ## QPainter::begin: Widget painting can only begin as a result of a paintEvent
            # then later we get
            ## QPainter::end: Painter not active, aborted
        #print "after QP"
        try:
            fontmetrics = pt.fontMetrics()
            w = pt.fontMetrics().width("Copying 99 items") ## AttributeError: width
            maxw = w * 1.5
            for node in nodes:
                item = self.nodeItem(node)
                cw = item.width(fontmetrics, self, 0)
                if  cw > w: w = cw
        except:
            w = 160
            print_compact_traceback( "Exception in get_drag_pixmap_width: w = %r: " % (w,) )
        pt.end()
            # guess: this line is what prints
            ## QPainter::end: Painter not active, aborted
            # and that must raise an exception which prevents the NameError from maxw.
            # But why don't I see that exception? Maybe it's something weirder than an exception?!?
        return min(maxw, w + 8)
    
    # == DND event methods ###SLATED FOR REVIEW and likely eventual rewrite or replacement
    
    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        try:
            self._do_drop_or_raise_DoNotDrop(event)
        except DoNotDrop:
            event.ignore()
            self.mt_update()
        self._ongoing_DND_info = None # nodes
        return
    
    def _do_drop_or_raise_DoNotDrop(self, event): #bruce 070511 split this out
        "[private] Do a drop, or raise a DoNotDrop exception. Print a message, but do appropriate updates only if we succeed."
        #bruce 070511 brought in several error messages from Qt3/TreeWidget.py,
        # modified some of them, made them use statusbar_msg rather than history redmsg ###UNTESTED
        item, rectjunk = self.item_and_rect_at_event_pos(event)
        if item is None:
            self.statusbar_msg( "drop into empty space ignored (drops under groups not supported; drop onto them instead)")
            raise DoNotDrop()
        nodes, drag_type = self._ongoing_DND_info
        targetnode = item.node
        if targetnode in nodes:
            # don't print a message, it's probably common for small mouse motions
            if DEBUG2:
                print "debug warning: MT DND: targetnode in nodes, refusing drop" # new behavior, bruce 070509
            #e should generalize based on what Qt3 code does
            #k should find out why this is not redundant with drop_on_ok check below
            raise DoNotDrop()
        if not targetnode.drop_on_ok(drag_type, nodes):
            self.statusbar_msg( "drop refused by %s" % quote_html(targetnode.name) )
            raise DoNotDrop()
        
        event.acceptProposedAction() # this should come after any DoNotDrop we might raise

        #bruce 070511 fixing some bugs by bringing in copiednodes & oldpart & unpick/pick code from Qt3/TreeWidget.py

        oldpart = nodes[0].part #bruce 060203
        oldassy = nodes[0].assy # not needed (assy can't be different yet) but ok for now [bruce 070511 comment]

        if drag_type == 'move':
            #bruce 060203 see if this helps implement NFR/bug 932 (which says, don't pick moved nodes or open their drop target);
            # do this first to make sure they're not picked when we move them... which might change current part [unverified claim].
            for node1 in nodes:
                node1.unpick()

        copiednodes = targetnode.drop_on(drag_type, nodes)
            #bruce 050203: copiednodes is a list of copied nodes made by drop_on
            # (toplevel only, when groups are copied).
            # For a move, it's []. We use it to select the copies, below.

        #bruce 050203 cause moved nodes to remain picked;
        # for copied nodes, we want the copies not originals to be picked.
        #bruce 060203 no longer pick moved nodes if moved into a different part, but still pick copies,
        # or nodes moved into the same part (or entire parts moved as a whole, only possible w/in clipboard).
        if drag_type == 'move':
            # this case rewritten by bruce 060203 re bug/NFR 932 (whose full fix also involved other files)
            self.unpick_all() # probably redundant now
            # pick the moved nodes, iff they are still in the same part.
            # run update_parts to help us; this covers case of moving an entire part w/in the clipboard,
            # in which it should remain picked.
            # (Someday it might be useful to look at nodes[0].find_selection_group() instead...)
            self.win.assy.update_parts()
                # FYI: drop_on sometimes does update_parts, but not always, so do it here to be safe. Optim this later.
                # Note: knowing anything about parts, and maybe even knowing self.win.assy, violates modularity
                # (re supposed generality of TreeWidget as opposed to modelTree); fix this later.
                # (I guess just about this entire method violates modularity, and probably so does much else in this file.
                #  As an older comment said:
                #  Note that this behavior should be subclass-specific, as should any knowledge of "the clipboard" at all!
                #  This needs review and cleanup -- maybe all this selection behavior needs to ask nodes what to do.)
            newpart = nodes[0].part
            if oldpart is newpart:
                for node1 in nodes:
                    node1.pick()
            pass
        else:
            self.unpick_all()
            # Pre-060203 code: we pick the copies iff they remain in the main part.
            # The reason we don't pick them otherwise is:
            # - NFR 932 thinks we shouldn't, in some cases (tho it probably doesn't think that
            #   if they are and remain in one clipboard part)
            # - there's a bug in drop_on which can put them in more than one clipboard item,
            #   but the selection is confined to one clipboard item.
            # With a little work we could improve this (in the cases not affected by that bug).
            # [comment revised, bruce 060203]
##            if not targetnode.in_clipboard():
##                for node1 in copiednodes:
##                    node1.pick()
            #bruce 060203 revising this to use similar scheme to move case (but not when copies get split up):
            # pick the copies if they're in the same part as the originals.
            # (I believe this will either pick all copies or none of them.)
            self.win.assy.update_parts()
            for node1 in copiednodes:
                if node1.part is oldpart:
                    node1.pick()
            pass
            
        # ... too common for a history message, i guess...
        msg = "dropped %d item(s) onto %s" % (len(nodes), quote_html(targetnode.name))
            #e should be more specific about what happened to them... ask the target node itself??
        msg = fix_plurals(msg)
        self.statusbar_msg( msg)
        #bruce 050203: mt_update is not enough, in case selection changed
        # (which can happen as a side effect of nodes moving under new dads in the tree)
        self.win.win_update()
        return
    
    def unpick_all(self):
        for node in self.topmost_selected_nodes():
            node.unpick()

    # == mouse click and selection drag events, and DND start code
    
    def mouseMoveEvent(self, event):
        if DEBUG3:
            print "begin mouseMoveEvent"

        try:
            if self._mousepress_info_for_move is None:
                return

            (item, eventInRect, option_modifier) = self._mousepress_info_for_move

            # might we be a DND, or a dragged-out selection [nim]?
            # for DND we need item and eventInRect (and if true, we only start one if one is not ongoing);
            # for selection we need not eventInRect (and perhaps item).
            
            if item and eventInRect:
                # possibly start a DND (if not already doing one)
                if self._ongoing_DND_info is not None:
                    return
                ### old LOGIC BUGS, hopefully fixed as of bruce 070509
                # - should not do this unless we decided the press event was in a place that would permit it
                # - the dragged object should depend on that press, not on the cursor position now (unlike how index is computed below)
                dragLength = (event.globalPos() - self.mouse_press_qpoint).manhattanLength()
                if dragLength < 10: ## QApplication.startDragDistance(): ###REVIEW: is this the best distance threshhold to use?
                    # the mouse hasn't moved far enough yet
                    return
                self._start_DND( item, option_modifier)
                return

            #e dragging out a selection is nim; the hard parts include:
            # - need to know what items were in between the ones hit
            # - need to recompute selected items based on original ones,
            #   altered ones by drag, and selection inference rules
            #   for both picking (into kids) and unpicking (into parents)
            # - need faster update of state and display than we have
            # [bruce 070609 comments]
            return
        finally:
            if DEBUG3:
                print "end mouseMoveEvent"
        pass

    # ==

    _mousepress_info_for_doubleclick = None, None # always a pair; always set; but only matters in QScrollArea implem
    
    def mousePressEvent(self, event, _doubleclick = False):
        "called by Qt on mousePress, or by our own method with private option _doubleclick = True"

        ## self.mouse_press_scrollpos = self.get_scrollpos("start of mousePressEvent")
        ###BUG: messes up manual scroll + click elsewhere (causing mt_update) -- this pos rules, discarding the manual scroll.
        # partial workaround for now -- do this only for a cmenu click... still causes that bug right after it, i think...
        # unless we del the attr then? no, we don't know *when* to del it -- "after updates caused by event X"???
            # This is more often correct than the one we get during a later paintEvent after a cmenu command,
            # for unknown reasons, so save it and use it (to preserve scroll position) instead of whatever we get then.
            # Note: this is unlikely to cure the scroll-jump-to-top that sometimes happens (on Mac) when the app is
            # brought to the foreground (also for unknown reasons, but the mouseclick that does that can even be on
            #  the dock area, presumably unseen by this object). Maybe we can intercept an "app now in foreground event"
            # and change its behavior? Should I browse the Qt source code for stray scrollToTops etc?
                                        
        self._mousepress_info_for_move = None
        
        _prior_mousepress_info_for_doubleclick = self._mousepress_info_for_doubleclick
        self._mousepress_info_for_doubleclick = None, None
            # Note: set below; used only when called later with _doubleclick, which is only done
            # by the QScrollArea implem subclass, not the QTreeView one.

        qp = event.globalPos()  # clone the point to keep it constant
        self.mouse_press_button = button = event.button() #bruce 070509
        self.mouse_press_buttons = buttons = event.buttons()
        self.mouse_press_modifiers = modifiers = event.modifiers()

        # simulate effect of fix_buttons / fix_event in the type-of-event analysis
        # [bruce 070509; later should ###REVIEW for consistency, or use one of those functions]
        option_modifier = (button == Qt.MidButton) or (modifiers & Qt.AltModifier) ###TODO: other conds like this should use this flag
        contextMenu = (button == Qt.RightButton) or (modifiers & Qt.MetaModifier)

        if contextMenu and hasattr(self, 'get_scrollpos'): # hasattr is kluge, varies by subclass [bruce 070529]
            # do this asap in case its value changes for mysterious reasons (as seems plausible from experience)
            self.mouse_press_scrollpos = self.get_scrollpos("start of mousePressEvent for cmenu")
            ###BUG: see comment for same thing at start of method
        else:
            self.mouse_press_scrollpos = None
            del self.mouse_press_scrollpos
        
        if DEBUG2:
            print "\nMT mousePressEvent: button %r, buttons %s, modifiers %s, globalPos %r, pos %r" % \
                  (button,
                   describe_buttons(buttons), # str and repr only show the class, which is PyQt4.QtCore.MouseButtons; int works
                   describe_modifiers(modifiers),
                   (qp.x(), qp.y()),
                   (event.pos().x(), event.pos().y())
                  )

        self.mouse_press_qpoint = QPoint(qp.x(), qp.y()) # used in mouseMoveEvent to see if drag length is long enough
        
        item, rect = self.item_and_rect_at_event_pos(event)
            # note about coordinates:
            # in QTreeView implem, I am not sure which coords event and this rect are in, contents or viewport.
            # in QScrollArea implem, they should be in viewport (once item_and_rect_at_event_pos is bugfixed).

        eventInRect = False # might be changed below; says whether event hits rect including icon(??) and name/label
        if item is not None:
            self.statusbar_msg( quote_html( item.node.name)) #bruce 070511 -- no other way to see long node names!
                # (at least for now -- tooltips are off for some reason, MT can't be widened, and it has no horizontal scrollbar,
                #  though it did a few days ago -- don't know why.)
            alreadySelected = item.node.picked #bruce 070509
            if DEBUG2:
                print "visualRect coords",rect.left(), rect.right(), rect.top(), rect.bottom()
            qfm = QFontMetrics(QLineEdit(self).font())
            rect.setWidth(qfm.width(item.node.name) + _ICONSIZE[0] + 4)
            if DEBUG2:
                print "visualRect coords, modified:",rect.left(), rect.right(), rect.top(), rect.bottom()
                # looks like icon and text, a bit taller than text (guesses)
            eventInRect = rect.contains(event.pos())
            if DEBUG2:
                print "real item: eventInRect = %r, item = %r, alreadySelected = %r" % \
                      (eventInRect, item, alreadySelected)
        else:
            alreadySelected = False # bruce 070509
            if DEBUG2:
                print "no item"
            pass

        if _doubleclick:
            # Either handle a double click (if all is ok for that), or do nothing for this event (return early).
            # (Question: will there be a mouseRelease event for this??)
            if eventInRect and not contextMenu \
               and not (modifiers & Qt.ShiftModifier) and not (modifiers & Qt.ControlModifier):
                olditem, oldrect_junk = _prior_mousepress_info_for_doubleclick
                if olditem and (olditem.node is item.node):
                    self.handle_doubleclick( event, item, rect) # this should do all needed updates
            return
                    
        if eventInRect and not contextMenu \
           and not (modifiers & Qt.ShiftModifier) and not (modifiers & Qt.ControlModifier):
            assert item
            self._mousepress_info_for_doubleclick = (item, rect) # use this only if next call has _doubleclick true
            
        # if not eventInRect, should also figure out if we are to left or right (maybe; nim),
        # or on openclose decoration (certainly; done now)
        if not eventInRect and item and item.node.openable():
            # we're on item's row, and item has an openclose decoration (or should have one anyway) -- are we on it?
            left_delta = rect.left() - event.pos().x()
            if DEBUG2:
                print "left_delta is %r" % left_delta
            if 0 < left_delta < 20:
                # guess; precise value doesn't matter for correctness, only for "feel" of the UI
                # (see also OPENCLOSE_AREA_WIDTH, but that's defined only for one of our two implems)
                # we presume they're toggling the openclose decoration
                node = item.node
                node.open = not node.open
                self.mt_update()
##                self.win.glpane.gl_update()
                if DEBUG3:
                    print "returning from mousePressEvent (openclose case)"
                return
            pass

        ###LOGIC BUG: if this press starts a DND, we don't want the same selection effects as if it doesn't.
        # What did the Qt3 code do? ###REVIEW that....
        # for now, save some info for mouseMoveEvent to use. (Might be clearer if saved in separate attrs? #e)
        if not contextMenu:
            self._mousepress_info_for_move = (item, eventInRect, option_modifier)
                # value determines whether a mouse move after this press might drag nodes, drag out a selection (nim), or do nothing
            if item:
                # figure out nodes to drag by DND, since we might change them below but wish we hadn't (kluge until better fix is found)
                if alreadySelected:
                    self._dnd_nodes = self.topmost_selected_nodes()
                else:
                    self._dnd_nodes = [item.node]
        
        # Flags indicating the actions we might take [mostly, modifying the selection]
        # Note: it looks to me like we maintain parallel selection state in a QSelectionModel and in the nodes themselves.
        # Furthermore, there are lots of bugs in the way we maintain selection state here,
        # since we try to duplicate the rules for Group/member interaction of selected state, but do it incorrectly.
        # (E.g. selecting all members of a Group selects it (bug),
        #  and clicking in empty space in that Group node's row then fails to unselect it (bug).)
        # What we ought to do is maintain selection state only in the nodes, and update it here from whatever nodes it changes in.
        # [bruce 070507 comment; now we're doing that, 070509]
        unselectOthers = False # if you set this, you must also set selectThis or unselectThis, unless there's no item
            # i.e. not eventInRect ###k I think [bruce 070509]; see if we do
        selectThis = False
        unselectThis = False
        toggleThis = False # toggle selection state

        # See "Feature:Model Tree" in the public wiki for model tree mouse controls
        ###REVIEW: is it right to look at event.buttons() but ignore event.button(), here?
        # Evidently not (at least for cmenu on Mac)... Revising it [bruce 070509]
        
        if 1:
            if modifiers & Qt.ShiftModifier:
                if modifiers & Qt.ControlModifier:
                    # shift control left click
                    unselectOthers = False
                    toggleThis = eventInRect
                else:
                    # shift left click
                    unselectOthers = False
                    selectThis = eventInRect
                    unselectThis = False #bruce 070509 revised, was unselectThis = not eventInRect
            else:
                if modifiers & Qt.ControlModifier:
                    # control left click
                    ## pass
                    unselectThis = eventInRect #bruce 070509 revised, was a noop
                    selectThis = False
                else:
                    # left click
                    selectThis = eventInRect
                    unselectThis = False #bruce 070509 revised, was unselectThis = not eventInRect
                    if not (alreadySelected and contextMenu):
                        # this cond is bruce 070509 bugfix; this would make it wrong for DND,
                        # but to avoid that we saved the selected nodes earlier (see comments there for caveats).
                        unselectOthers = True

        if DEBUG:
            print 
            print "unselectOthers", unselectOthers
            print "selectThis", selectThis
            print "unselectThis", unselectThis
            print "toggleThis", toggleThis
            print "contextMenu", contextMenu
            print "SELECTED BEFORE <<<"
            print self.topmost_selected_nodes()
            print ">>>"
        
        assert not (selectThis and toggleThis)   # confusing case to be avoided
        assert not (selectThis and unselectThis)   # confusing case to be avoided
        assert not eventInRect or not unselectOthers or (selectThis or unselectThis) #bruce 070509 added this

        # take whatever actions are required (one or more of the following, in order -- selection and maybe cmenu)
        
        updateGui = False # whether we need to update MT and/or GLPane at the end

        ###TODO: optimize by only setting updateGui if something changes
        if unselectOthers:
            ###REVIEW: this actually unselects all (this too), not just others -- is that ok? Even if it's inside a picked group?
            # I think it's ok provided we reselect it due to selectThis (or specifically unselect it too).
            for node in self.topmost_selected_nodes():#bruce 070509 optimization
                node.unpick() # for a group, this unpicks the children too (could use unpick_all_except if necessary)
            updateGui = True
        if selectThis and item is not None:
            item.node.pick()
            updateGui = True
        if unselectThis and item is not None:
            item.node.unpick()
            updateGui = True
        if toggleThis and item is not None:
            assert not unselectOthers
            if item.node.picked:
                item.node.unpick()
            else:
                item.node.pick()
            updateGui = True
        
        if contextMenu:
            # Note: some of the above selection actions may have also been done.
            # In the QScrollArea implem, we need to redraw the MT to show them;
            # in the QTreeView implem, we apparently didn't need to, but it shouldn't hurt.
            if updateGui:
                self.mt_update()
            self._renamed_contextMenuEvent(event)
            # Why no updateGui = True here? Because the cmenu commands are supposed to do their own updates as needed.
            # But it probably has little effect now to not do it, because we probably do it anyway
            # during the selection phase above.

        if DEBUG:
            print "SELECTED AFTER <<<"
            print self.topmost_selected_nodes()
            print ">>>"

        if updateGui: # this is often overkill, needs optim
            if DEBUG3:
                print "doing updateGui at end of mousePressEvent"
            self.mt_update()
            self.win.glpane.gl_update()

        if DEBUG3:
            print "end mousePressEvent"
        
        return # from mousePressEvent
    
    def mouseReleaseEvent(self, event):
        if DEBUG3:
            print "begin/end mouseReleaseEvent (almost-noop method)"
        self._ongoing_DND_info = None

    def contentsMousePressEvent(self, event): #bruce 070508 debug code; doesn't seem to be called (in QTreeView implem anyway)
        if DEBUG3:
            print "calling QTreeView.contentsMousePressEvent"
        res = QTreeView.contentsMousePressEvent(self, event)
        if DEBUG3:
            print "returned from QTreeView.contentsMousePressEvent"
        return res

    def contentsMouseMoveEvent(self, event): #bruce 070508 debug code; doesn't seem to be called
        if DEBUG3:
            print "calling QTreeView.contentsMouseMoveEvent"
        res = QTreeView.contentsMouseMoveEvent(self, event)
        if DEBUG3:
            print "returned from QTreeView.contentsMouseMoveEvent"
        return res

    def contentsMouseReleaseEvent(self, event): #bruce 070508 debug code; doesn't seem to be called
        if DEBUG3:
            print "calling QTreeView.contentsMouseReleaseEvent"
        res = QTreeView.contentsMouseReleaseEvent(self, event)
        if DEBUG3:
            print "returned from QTreeView.contentsMouseReleaseEvent"
        return res
    # ==
    
    def contextMenuEvent(self, event): ###bruce hack, temporary, just to make sure it's no longer called directly
        if 1:
            print "\n *** fyi: MT: something called self.contextMenuEvent directly -- likely bug ***\n"
            print_compact_stack("hmm, who called it?: ")
                # Note: this can be called directly by app.exec_() in main.py,
                # and is, if we use microsoft mouse right click on iMac G5 in Qt 4.2.2, *or* control-left-click;
                # if that can't be changed (by finding an interceptable caller in common with mousePressEvent),
                # we might need to revise this to also do selection click actions,
                # but OTOH, for reasons unknown, mousePressedEvent is running *first* as if it was a left click
                # (but with an unknown modifier flag, the same one for either right-click or control-left-click),
                # which might remove the need for that if we can be sure it will always happen.
                #    We also need to know whether all this happens the same way for control-left-click on Mac (I guess yes),
                # and/or for other mice, and/or on Windows, and/or in later versions of Qt.
                #    Need to ###REVIEW:
                # - Qt docs for this (both about modifiers, and buttons/button, and sequence of event calls for contextMenuEvent)
                # - comments in fix_buttons (which we're not using but maybe should be)
                # - is it related to buttons not always including button?
                #   What's happening in that first event is buttons = 1 (left), button = 2 (right).
                #   This still leaves unexplained (1) who calls contextMenuEvent, (2) why two events occur at all.
                #   (Could it have anything to do with the tab control?? ###REVIEW)
                #   What about for a plain left click? Then we get button 1, buttons 0x1 (left) (inconsistent).
        return self._renamed_contextMenuEvent(event)
    
    def _renamed_contextMenuEvent(self, event):
        if DEBUG3:
            print "begin _renamed_contextMenuEvent"
            # See TreeWidget.selection_click() call from TreeWidget.menuReq(), in the Qt 3 code...
            # but that's done by our caller, not us. We're no longer called directly from Qt, only from other methods here.
            # [bruce 070509]

        if hasattr(self, 'get_scrollpos'): #kluge, varies by subclass [bruce 070529]
            self.get_scrollpos("start of _renamed_contextMenuEvent")###k see if this is more correct than the one we get later...
                # not sure, since querying it may have had the effect of fixing the bug of it changing later! not sure yet...
        
        event.accept() ##k #bruce 070511, see if this fixes scroll to top for these events --
            # note, event is probably a mouse press, not a cmenu event per se
        nodeset = self.topmost_selected_nodes()
        ###TODO: we should consolidate the several checks for the optflag condition into one place, maybe mousePressEvent.
        optflag = (((self.mouse_press_buttons & Qt.MidButton) or
                    (self.mouse_press_modifiers & Qt.AltModifier)) and 'Option' or None)
        cmenu_spec = self.ne1model.make_cmenuspec_for_set(nodeset, optflag)
        menu = makemenu_helper(self, cmenu_spec) #bruce 070514 fix bug 2374 and probably others by using makemenu_helper
        menu.exec_(event.globalPos())
        if DEBUG3:
            print "end _renamed_contextMenuEvent"
        return

    # ==

    # Note: if we ever want our own keyPressEvent or keyReleaseEvent bindings, see the code and comments
    # in TreeWidget.keyPressEvent about doing this correctly, and for how Qt3 did the arrow key actions.
    # We will need the filter_key call it does (or an equivalent use of wrap_key_event as done in GLPane)
    # or NE1 will have a Mac-specific delete key bug whenever the MT has the focus. This does not happen now
    # since MWsemantics handles our key presses, and it passes them to GLPane, which has the bugfix for that.
    # See also the comments in filter_key(). [bruce 070517 comment]

    # ==
    
    def get_scrollpos(self, msg = ""):
        "Return the current scrollposition (as x,y, in scrollbar units), and if DEBUG3 also print it using msg."
        ## res = ( self.horizontalOffset(), self.verticalOffset() )
            # This is in pixels, and it apparently works, but it's not useful
            # because setting it (using QWidget.scroll) doesn't work properly and has bad side effects.
            # So, get it in "scrollbar units" instead, and set it by talking directly to the scrollbars.
        hsb = self.horizontalScrollBar()
        x = hsb and hsb.value() or 0
        vsb = self.verticalScrollBar()
        y = vsb and vsb.value() or 0
        res = x,y
        if DEBUG3:
            if msg:
                msg = " (%s)" % (msg,)
            print "get_scrollpos%s returns %r" % (msg, res,)
        return res

    def set_scrollpos(self, pos): # used only in QTreeView implem, but should be correct in QScrollArea implem too
        "Set the scrollposition (as x,y, in scrollbar units), and if DEBUG3 print various warnings if anything looks funny."
        x, y = pos # this is in scrollbar units, not necessarily pixels
        hsb = self.horizontalScrollBar()
        if hsb:
            hsb.setValue(x) # even if x is 0, since we don't know if the current value is 0
        else:
            if x and DEBUG3:
                print "warning: can't set scrollpos x = %r since no horizontalScrollBar" % (x,)
        vsb = self.verticalScrollBar()
        if vsb:
            vsb.setValue(y)
        else:
            if y and DEBUG3:
                print "warning: can't set scrollpos y = %r since no verticalScrollBar" % (y,)
        pos1 = self.get_scrollpos("verifying set_scrollpos")
        if pos != pos1:
            if DEBUG3:
                print "warning: tried to set scrollpos to %r, but it's now %r" % (pos,pos1)
        return

    def rename_node_using_dialog(self, node): #bruce 070531
        """[newly in public API -- ###doc that. Used by callers in more than one file.]
        Put up a dialog to let the user rename the given node. (Only one node for now.)
        Emit an appropriate statusbar message, and do necessary updates if successful.
        """
        # Note: see similar code in setModelData in another class.
        ##e Question: why is renaming the toplevel node not permitted? Because we'll lose the name when opening the file?
        oldname = node.name
        ok = node.rename_enabled()
        # Various things below can set ok to False (if it's not already)
        # and set text to the reason renaming is not ok (for use in error messages).
        # Or they can put the new name in text, leave ok True, and do the renaming.
        if not ok:
            text = "Renaming this node is not permitted."
                #e someday we might want to call try_rename on fake text
                # to get a more specific error message... for now it doesn't have one.
        else:
            ok, text = grab_text_line_using_dialog( title = "Rename",
                                            label = "new name for node [%s]:" % oldname,
                                            default = oldname )
        if ok:
            ok, text = node.try_rename(text)
        if ok:
            msg = "Renamed node [%s] to [%s]" % (oldname, text) ##e need quote_html??
            self.statusbar_message(msg)
            self.mt_update() #e might be redundant with caller; if so, might be a speed hit
        else:
            msg = "Can't rename node [%s]: %s" % (oldname, text) # text is reason why not
            self.statusbar_message(msg)
        return

    pass # end of class ModelTreeGui_common

# ==

def grab_text_line_using_dialog( default = "", title = "title", label = "label" ): #bruce 070531 ##e refile this
    """Use a dialog to get one line of text from the user, with given default (initial) value,
    dialog window title, and label text inside the dialog. If successful, return (True, text);
    if not, return (False, "Reason why not"). Returned text is a python string (not unicode).
    """
    # WARNING: several routines contain very similar code.
    # We should combine them into one and refile it into widgets.py or the like.
    # This one was modified from grab_text_line_using_dialog() (in exprs module)
    # which was modified from _set_test_from_dialog(),
    # which was modified from debug_runpycode_from_a_dialog(),
    # which does the "run py code" debug menu command.
    from PyQt4.Qt import QInputDialog, QLineEdit
    parent = None
    text, ok = QInputDialog.getText(parent, title, label, QLineEdit.Normal, default) # parent arg needed only in Qt4
    if not ok:
        reason = "Cancelled"
    if ok:
        try:
            # fyi: type(text) == <class '__main__.qt.QString'>
            text = str(text) ###BUG: won't work for unicode
        except:
            ok = False
            reason = "Unicode is not yet supported"
        ## text = text.replace("@@@",'\n')
    if ok:
        return True, text
    else:
        return False, reason
    pass

# ==

class ModelTreeGui_QTreeView(QTreeView, ModelTreeGui_common):
    """The old version of our model tree GUI based on QTreeView.
    As of 070529, used by default, but has various unfixable bugs.
    Will be removed when the newer one (not based on QTreeView) works well enough.
    """
    # Relevant Qt docs (QTreeView) [scattered among several places in this file]:
    # We use Qt 4.2 now, but some methods introduced in Qt 4.3 might be useful:
    # [see http://doc.trolltech.com/4.3/qtreeview.html]
    # - QTreeView::indexRowHeight
    # and in 4.2:
    # - QModelIndexList QItemSelectionModel::selectedRows
    #   http://lists.trolltech.com/qt-interest/2006-08/thread00791-0.html
    def __init__(self, win, name, ne1model, parent=None):
        QTreeView.__init__(self, parent)
        ModelTreeGui_common.__init__(self, win, ne1model)
        del name
        
        # What's different between MultiSelection and ExtendedSelection?
        #
        # MultiSelection: When the user selects an item in the usual way, the selection status of
        # that item is toggled and the other items are left alone.
        #
        # Extended Selection: When the user selects an item in the usual way, the selection is
        # cleared and the new item selected. However, if the user presses the Ctrl key when clicking
        # on an item, the clicked item gets toggled and all other items are left untouched. If the
        # user presses the Shift key while clicking on an item, all items between the current item
        # and the clicked item are selected or unselected, depending on the state of the clicked
        # item. Multiple items can be selected by dragging the mouse over them.
        #
        # So it looks like I [Will] have manually implemented [something related to part of]
        # Extended Selection in the mousePressEvent method, but that's not such a wasteful thing,
        # because it's defined in a way that we can easily redefine it if we want to change the behavior.
        #
        # [Unfortunately it has serious bugs and probably needs replacement. However, we'll continue
        #  to implement selection behavior ourselves, not depending on setSelectionMode, and perhaps
        #  we'll even stop using Qt's idea of selected nodes at all (since it paints too much of their bg,
        #  and we don't really need another copy of the selection state, whose definitive values are stored
        #  in node.picked). [bruce 070508]]
        #
##        self.setSelectionMode(self.MultiSelection)
##        self.setSelectionMode(self.ExtendedSelection)
        self.setSelectionMode(self.NoSelection) #bruce 070507 change -- doesn't make a noticeable difference.
        self.setContextMenuPolicy(Qt.PreventContextMenu) #bruce 070509 change; I hope it will prevent direct calls of contextMenuEvent
        
        self.setUniformRowHeights(True)
            #bruce 070507 optimization; known to be true due to our _our_QItemDelegate.sizeHint method;
            # said to be significant in some of these related web pages:
            # - http://lists.trolltech.com/qt-interest/2006-08/thread00736-0.html
            # - http://wiki.kde.org/tiki-index.php?page=ItemView+Tips
            # (doc: http://doc.trolltech.com/4.2/qtreeview.html#uniformRowHeights-prop )

        self.qttreemodel = None

        #k the following might be removed... they're only used in mt_update to compare to current values and decide if update needed.
        self.lastAllNodes = [ ]
        self.lastPickedNodes = [ ]

        return

    def nodeItem(self, node):
        return self.node_to_item_dict[node]

    def recurseOnItems(self, func, topitem = None): ###REVIEW: could/should this method be defined in _QtTreeModel?
        if topitem is None:
            if self.qttreemodel is None:
                return
            topitem = self.qttreemodel.root_Item
        func(topitem)
        for child in topitem.childItems:
            self.recurseOnItems(func, child)

    def paint_item(self, p, item):
        option = None # not used when pos is provided
        index = self.qttreemodel.itemToIndex(item) #bruce 070511 (first use of itemToIndex)
        assert index.isValid()
        self.itemDelegate.paint(p, option, index, pos = (0,0))
        width = 160 ###k guess; should compute in paint and return, or in an aux subr if Qt would not like that
        return width

    def item_and_rect_at_event_pos(self, event):#bruce 070529 split out of callers
        """Given a mouse event, return the item under it (or None if no item),
        and a QRect encompassing certain(?) parts of it (or None if no item).
        ### which parts?
        ### what coords?
        """
        pos = event.pos()
        index = self.indexAt(pos)
        if index.isValid():
            item = index.internalPointer()
            rect = self.visualRect(index)
            return item, rect ###k might change API to only return rect left and right bounds; right now, full QRect is needed
        else:
            return None, None
        pass

    def update_item_tree(self, unpickEverybody = False): ###SLATED FOR REWRITE OR REPLACEMENT [partly done?]
        """Discard old item tree and replace it with a new one (made of all new items),
        updating item state as needed, including open/closed state.
        OR, if a debug_pref says to, keep using the same item tree if possible, but send signals to tell the TreeView it changed.
           Also unpick all nodes (and in that case always remake the model), if requested by the option.
        """
        # [bruce 070509 renamed clear -> replace_item_tree and changed default value of unpickEverybody to False,
        #  revising calls as needed to keep them equivalent. Then, bruce 070525 renamed it again, to update_item_tree.]

        newcode = debug_pref("MT debug: incremental update_item_tree?", Choice_boolean_False, non_debug = True, prefs_key = True)

        if newcode:
            self.update_item_tree_NEW(unpickEverybody = unpickEverybody)
                # let it redundantly get the disabled debug_pref,
                # since it will eventually replace this method entirely (if it works)
            return

        disabled = debug_pref("MT debug: disable replace_items", Choice_boolean_False, non_debug = True, prefs_key = True)
        
        if disabled and unpickEverybody:
            print "ignoring \"MT debug: disable replace_items\" for initializing new assy"
            disabled = False

        if disabled and not isinstance(self.qttreemodel, _QtTreeModel):
            print "ignoring \"MT debug: disable replace_items\" since qttreemodel not there or wrong class"
            disabled = False

        if disabled:
            print "update_item_tree: skipped (disabled)"
            return

        # OLD CODE (but still used by default as of 070525 3pm)
        
        # throw away all references to existing list items
        if unpickEverybody and hasattr(self, 'node_to_item_dict'):
            if self.MT_debug_prints():
                print "MT debug: FYI: unpickEverybody"
            for node in self.node_to_item_dict.keys():
                node.unpick() #e optim: this descends into Groups, so we're doing extra work in this loop
        self.item_to_node_dict = { }
        self.node_to_item_dict = { }
        # Make a "fake" root node and give it the list of top nodes as children. Convert the tree of
        # Nodes to a whole new tree of items, thereby populating the two dictionaries.
        class FakeTopNode(Node):
            def __init__(self, name, members=[ ]):
                self.name = name
                self.members = members
                self.picked = False
            def rename_enabled(self):
                return False
            def pick(self):
                pass
            def unpick(self):
                pass
        rootNode = FakeTopNode("Model tree", self.ne1model.get_topnodes())
        root_Item = self.make_new_subtree_for_node(rootNode)
        self.qttreemodel = model = _QtTreeModel(root_Item) # creates item indices in model.index_for_item[item]

        self.itemDelegate = _our_QItemDelegate(self)
            # note: we'll store this here, not in the qttreemodel [bruce 070525, splitting it from root_Item]
        
        self.setModel(model)  # undoes all Qt-native item selections (no effect on node selections)
        self.setItemDelegate( self.itemDelegate)
            #k I don't know whether this delegate needs to be an item (like it is),
            # or just any object with a certain API for handling items, like def paint.
            # [bruce 070511 comment]

##        ### kluge: should do following in its init method:
##        itemDelegate.view = self  # needed for paint()
            ###REVIEW: is .view our own made-up name, or something known to Qt?
            # guess: our own, and too generic to search for, and used in two different objects for different-class values,
            # so they ought to be renamed to different attrnames. [bruce 070511 comment]

        if DEBUG3:
            print "\nMT update_item_tree (%d)" % _debug_mt_update_counter ### when is this happening? [bruce 070507]
        #bruce 070507 use setExpanded (we'll probably move this into another method to call separately, as in the Qt3 code)
        def expand_if_open(item):
            if item is root_Item:
                return
            node = item.node
            open = node.openable() and node.open
            index = self.qttreemodel.index_for_item[item]
            self.setExpanded( index, open )
        self.recurseOnItems(expand_if_open)

        if debug_pref("MT debug: show after replace", Choice_boolean_True, non_debug = True, prefs_key = True):
            self.show()
        return # from update_item_tree (old version)

    # ==

    qttreemodel = None
    
    def update_item_tree_NEW(self, unpickEverybody = False): #bruce 070525
        """
        """
        
        disabled = debug_pref("MT debug: disable replace_items", Choice_boolean_False, non_debug = True, prefs_key = True)
        
        if disabled and unpickEverybody:
            print "ignoring \"MT debug: disable replace_items\" for initializing new assy"
            disabled = False

        correct_class = isinstance(self.qttreemodel, _QtTreeModel_NEW)
        
        if disabled and not correct_class:
            print "ignoring \"MT debug: disable replace_items\" since qttreemodel not there or wrong class"
            disabled = False

        if disabled:
            print "update_item_tree_NEW: skipped (disabled)"
            return

        print "update_item_tree_NEW" ####

        # NEW CODE: use the new incremental algorithm, but remember that we might be clearing state or not have created it yet.

        # The attrs which hold the state we need to incrementally update or initialize are:
        # - self.qttreemodel -- an old-code _QtTreeModel or a new-code _QtTreeModel_NEW
        #   which includes:
        #   - self.qttreemodel.index_for_item
        # - self.item_to_node_dict
        # - self.node_to_item_dict

        # Some methods we need to call here to set state in other objects are:
        # - self.setModel
        # - self.setItemDelegate
        # - self.setExpanded( index, open)

        remake = False
        try:
            # decide whether to remake from scratch -- any exception here means we want to
            # (we probably ought to do this in a more principled way, e.g. comparing assy to the prior one we saw --
            #  right now we're probably relying on being called with unpickEverybody true, whenever assy changes)
            assert correct_class, "remake if qttreemodel is not there or not correct class"
            assert not unpickEverybody, "remake if a new assy is being initialized"
            # see if all necessary attrs have been initialized
##            self.qttreemodel
            self.qttreemodel.index_for_item
            self.item_to_node_dict
            self.node_to_item_dict
            ### not sure we want this last condition -- "and they are nonempty"
##            assert self.qttreemodel.index_for_item
##            assert self.item_to_node_dict
##            assert self.node_to_item_dict
            print "update will be incremental"####
        except:
            DEBUG_070525 = True
            if DEBUG_070525:
                print_compact_traceback("not a bug: remaking item tree, for this reason: ")####
            remake = True

        if remake:
            if unpickEverybody and hasattr(self, 'node_to_item_dict'):
                if self.MT_debug_prints():
                    print "MT debug: FYI: unpickEverybody"
                for node in self.node_to_item_dict.keys():
                    node.unpick() #e optim: this descends into Groups, so we're doing extra work in this loop

            # throw away all references to existing list items
            self.item_to_node_dict = { }
            self.node_to_item_dict = { }
            # Make a "fake" root node and give it the list of top nodes as children. Convert the tree of
            # Nodes to a whole new tree of items, thereby populating the two dictionaries.
            class FakeTopNode(Node):
                def __init__(self, name, members=[ ]):
                    self.name = name
                    self.members = members
                    self.picked = False
                def rename_enabled(self):
                    return False
                def pick(self):
                    pass
                def unpick(self):
                    pass
            rootNode = FakeTopNode("Model tree", self.ne1model.get_topnodes())
            root_Item = self.make_new_subtree_for_node_NEW(rootNode)
                # note: this remains available as self.qttreemodel.root_Item
            self.qttreemodel = model = _QtTreeModel_NEW(root_Item) # creates item indices in model.index_for_item[item] (lazily)

            self.itemDelegate = _our_QItemDelegate(self)
            # note: we'll store this here, not in the qttreemodel [bruce 070525, splitting it from root_Item]
            
            self.setModel(model)  # undoes all Qt-native item selections (no effect on node selections)
            self.setItemDelegate(self.itemDelegate)
##            self.itemDelegate.view = self  # needed for paint()
                ###REVIEW: is .view our own made-up name, or something known to Qt?
                # guess: our own, and too generic to search for, and used in two different objects for different-class values,
                # so they ought to be renamed to different attrnames. [bruce 070511 comment]
        else:
            pass # handle incremental updates lower down

        #bruce 070507 use setExpanded (we'll probably move this into another method to call separately, as in the Qt3 code)
        def expand_if_open(item):
            if item is self.qttreemodel.root_Item:
                return
            node = item.node
            open = node.openable() and node.open
            index = self.qttreemodel.itemToIndex(item)
            self.setExpanded( index, open )
        self.recurseOnItems(expand_if_open)

        if debug_pref("MT debug: show after replace", Choice_boolean_True, non_debug = True, prefs_key = True):
            self.show()

        if not remake:
            # incremental updates
            rootIndex = self.qttreemodel.itemToIndex( self.qttreemodel.root_Item)
            print "rootIndex.isValid() is", rootIndex.isValid()
            self.dataChanged( rootIndex, rootIndex ) ###k will this index be there? will this have desired update effect?
                # do we need to do this in mt_update rather than here inside paintEvent? #### GUESS: YES
        
        return # from update_item_tree_NEW

    def node_to_item(self, node): #bruce 070525, only used when _NEW routines are used ###k
        "For node being some known node's dad or child, return the corresponding tree item (creating it if necessary)"
        try:
            return self.node_to_item_dict[node] # note: never contains root_Item (#k not sure if we can safely change that)
        except KeyError:
            assert node is not None ###BUG: this fails, don't yet know why [070529 1130am]
            assert isinstance(node, Node) # I don't think FakeTopNode gets here, but it's a Node even if it does
            if node.__class__.__name__ == 'RootGroup':
                ###KLUGE -- better to compare to toplevel nodes, or at least, assy.root
                ###Doc -- this exception to .parent and .dad correspondence should be mentioned, in a comment that says they corr.
                return self.qttreemodel.root_Item
            assert node is not self.qttreemodel.root_Item.node # i.e. assert no other way for us to need to return root_Item
            item = _our_TreeItem_NEW(node, self)
                # that constructor saves it in self.node_to_item_dict and the other one
            return item
        pass
            
    # ==

    _inside_paintEvent = False
    
    def mt_update(self):
        """
        """
        if self._inside_paintEvent:
            print "likely bug: mt_update when self._inside_paintEvent"
            
        #bruce 070510 rewrote this to be an invalidation method, not an update method,
        # just as it was in the Qt3 code. This improves efficiency and helps fix some bugs.
        self._mt_update_needed = True #bruce 070511 revised this (attr is now private and in self, not in self.ne1model)
        regiontype = debug_pref("MT debug: setDirtyRegion", Choice(["large","small","none"]), non_debug = True, prefs_key = True)
        if regiontype == "large":
            x,y = 0,0
            w,h = 10000,10000 # hopefully that should be enough -- but (1) not if Mt is very long! (not sure what coords it's in)
                # and (2) i don't know if it matters what it covers, as long as it covers something visible -- the only need for this
                # is that update alone is not enough to cause paintEvent to be called.
            region = QRegion(x,y,w,h)
            self.setDirtyRegion(region) # needs region arg - can we get the whole thing? in what coords?
        elif regiontype == "small":
            # might not work if scrolled, even if it works normally; but might affect scrollbar recursion bug 2399 (conceivably)
            x,y = 0,0
            w,h = 1,1
            region = QRegion(x,y,w,h)
            self.setDirtyRegion(region)
        
        self.update() ##k is this enough to call our paintEvent? NO. (And if it does: with enough of a dirty region?)

    # ==
    
    def paintEvent(self, event): #bruce 070510
        # note: when this had the wrong param list, the exception for that was printed
        # without any line number or traceback, but apparently by Qt itself. Can we fix that?
        if DEBUG3:
            print "begin paintEvent"
        if self._inside_paintEvent:
            print "likely bug: recursive MT.paintEvent"
        old = self._inside_paintEvent
        try:
            if self._mt_update_needed:
                self._update_if_data_changed()
                self._mt_update_needed = False
            self._inside_paintEvent = True
            QTreeView.paintEvent(self, event) # this indirectly calls the item paint methods
        except:
            print_compact_traceback()
        self._inside_paintEvent = old
        if DEBUG3:
            print "end paintEvent"
        return
        
    # ==
    
    def _update_if_data_changed(self): #bruce 070510 split this out and changed caller (now paintEvent); revised 070511

        # We need to update if either the list of selected
        # items or picked nodes has changed since last time. We also need to update if the
        # set of all nodes has changed.
        # [###BUG: those are not enough to detect all differences. This might miss things like
        #  node renames from EditProps dialogs, or icon changes due to hide or display mode, or disabledness changes.
        #  ###OPTIM: this might have false positives when changes occur inside closed groups.
        #  (that might be fixed now by visible_only = True)
        #  -- bruce 070509 comment]

        # bruce 070509 changes (not enough to make it correct):
        # - only look at visible nodes (optim, and might be incorrect (see comment))
        # - ignore Qt idea of selection (we'll stop using that entirely)
        # - fake_nodes_to_mark_groups = True (fix bugs if set and order of nodes unchanged, but depth changes)
        # To make it correct, we'd also need to know about node name/icon/disabled/hidden/open changes by other code. ###BUG
        # (No need to know if picked changes, since we check that here; not open either, if we retain visible_only = True.)

# put this back when it's correct; for now just always update at this point [070511, maybe was true 070510 too]
##        update_needed = False
##        pickedNodes = []
##        allNodes = []
##        def addIfPicked(node):
##            allNodes.append(node)
##            if node not in (0,1) and node.picked: # 0,1 are fake nodes passed due to fake_nodes_to_mark_groups = True
##                pickedNodes.append(node)
##        self.ne1model.recurseOnNodes(addIfPicked,
##                              #bruce 070509 added options as an optim (might be important)
##                            visible_only = True, ###REVIEW: this is only correct if opening a closed Group calls mt_update.
##                            fake_nodes_to_mark_groups = True
##                           )
##        if allNodes != self.lastAllNodes:
##            self.lastAllNodes = allNodes
##            update_needed = True
##        if pickedNodes != self.lastPickedNodes:
##            self.lastPickedNodes = pickedNodes
##            update_needed = True
        update_needed = True
        if update_needed:
            self._remake_contents_0()
        elif DEBUG3:
            pass ## print "\nmt_update: update not needed (%d)" % _debug_mt_update_counter ## add back the incr of this
        return # from _update_if_data_changed

    def _remake_contents_0(self): #bruce 070510 split this out of mt_update
        """
        """
        # note: this corresponds to update_state_0 in Qt3 code

        if debug_pref("MT debug: disable _remake_contents_0", Choice_boolean_False, non_debug = True, prefs_key = True):
            return

        # use the record of the scroll position from the mousePress, so it can be set to something similar below
        pos1 = self.get_scrollpos("initial") # the current value has already been messed up in some cases! (e.g. after cmenu commands)
        try:
            scrollpos = self.mouse_press_scrollpos # note: as of 070522 (and earlier) we're setting this iff this is a cmenu event.
                # but then the assert 0 below ignores it.
            assert 0 ### DISABLE THIS FOR NOW, too weird in effects on scrollbar... sometimes it jumps when you click scrollthumb itself
            
            ###BUG: probably wrong if user scrolled manually! or if we're called in another way...
            # e.g. during it!
            # not sure how to fix -- erasing it during mouseRelease won't work if that event is missed!!
            # Hmm, try this:
            ## del self.mouse_press_scrollpos # theory: >1 event -> 1 update, only one should do this... dubious in practice,
            # tho it might cure the bug we now have where manual scroll (no click inside) + glpane click resets scrollpos.###TEST
            # does not fully work, or causes other worse effects. would it work to do this only after a real mt that does stuff?
            # or in caller? no, that's unlikely. next best guess: don't do this del, do capture manual scroll changes. BUT HOW??#####
            # Another poss -- don't do this for mouseclicks, unless they are for cmenu events...
        except: # makes it work to start, but doesn't cure manual-scroll bug (predicted, verified (w/o del))
            scrollpos = pos1
        
        self.update_item_tree()

        # set the scroll position to what it ought to be [bruce circa 050113. Fixes bug 177.] [ported to Qt4, bruce 070511]
        # (the frequent get_scrollpos calls are for debugging, but it's conceivable they are needed due to undocumented side effects.)
        self.get_scrollpos("after remake alone")

        if debug_pref("MT debug: updateGeometry", Choice_boolean_True, non_debug = True, prefs_key = True):
            self.updateGeometry() #k don't know if this is needed
            self.get_scrollpos("after updateGeometry")

        disable_valueChanged = debug_pref("MT debug: disable scrollBar.valueChanged()",
                                          Choice_boolean_False, non_debug = True, prefs_key = True)
        if disable_valueChanged:
            self.set_scrollbar_valueChanged_enabled( False) #bruce 070524 experiment

        if debug_pref("MT debug: scrollToBottom", Choice_boolean_True, non_debug = True, prefs_key = True):
            self.scrollToBottom() # this is needed -- it prevents temporary removal of scrollbar.
                # Maybe that's related to the updates it does internally, unlike scrollToTop?
                # The source code, in gui/itemviews/qabstractitemview.cpp (Qt 4.2.2), says:
                    ##    void QAbstractItemView::scrollToBottom()
                    ##    {
                    ##        Q_D(QAbstractItemView);
                    ##        if (d->delayedLayout.isActive()) {
                    ##            d->executePostedLayout();
                    ##            updateGeometries();
                    ##        }
                    ##        verticalScrollBar()->setValue(verticalScrollBar()->maximum());
                    ##    }
            self.get_scrollpos("after scrollToBottom")

        if debug_pref("MT debug: set_scrollpos", Choice_boolean_True, non_debug = True, prefs_key = True):
            self.set_scrollpos( scrollpos)

        if disable_valueChanged:
            self.set_scrollbar_valueChanged_enabled( True) #bruce 070524 experiment

        # Qt3 comment, not sure if still an issue in Qt4:
        ### not yet perfect, since we need to correct height
        # to be larger than needed for all items, when collapsing a group
        # which went below the visible area, so the group doesn't move on
        # screen due to QListView not liking empty space below the items.

        ## a note about why ensureItemVisible is not useful [bruce circa 050109, Qt3 code]: 
        ##self.ensureItemVisible(self.last_selected_node.tritem)
        ## this "works", but it looks pretty bad:
        ## - there's a lot of flickering, incl of the scrollbar (disabling updates might fix that)
        ## - it always puts this item at the very bottom, for the ones that would otherwise be off the bottom
        ## - even if this item is already visible near the top, it moves stuff, perhaps as if trying to center it.

        #ninad 061201: Update the orientation window's items, if it's visible. 
        if self.win.orientationWindow:
            self.win.orientationWindow.updateOrientationViewList()
        
        return # from _remake_contents_0

    def set_scrollbar_valueChanged_enabled( self, enabled): #bruce 070524 experiment; has bad side effects (drawing in wrong coords)
        """Enable or disable the sending of the valueChanged signal (or, of all signals)
        from whichever scrollbars we have (horizontal and/or vertical)
        """
        # relevant Qt 4.2.2 docs:
        # bool QObject::signalsBlocked() -- Returns true if signals are blocked; otherwise returns false.
        # bool QObject::blockSignals ( bool block ) -- If block is true, signals emitted by this object is blocked
        # (i.e., emitted signals disappear into hyperspace). If block is false, no such blocking will occur.
        # The return value is the previous value of signalsBlocked().
        hsb = self.horizontalScrollBar()
        if hsb:
            resh = hsb.blockSignals( not enabled)
        vsb = self.verticalScrollBar()
        if vsb:
            resv = vsb.blockSignals( not enabled)
        # print "set_scrollbar_valueChanged_enabled(%r), prior enabled states were" % enabled, not resh, not resv 
        return resh, resv # retval not yet used or documented
    
    def make_new_subtree_for_node(self, node, parent = None):
        "make a new item tree for the node tree; return the root item; parent should be None or a parent item" #bruce 070525 docstring
        if parent is None:
            parent = self # kluge, i think [bruce 070525 comment]: parent has some of the same attrs as _our_TreeItem
        item = _our_TreeItem(node, parent) #bruce 070523 experiment; works; bruce 070525 update: now using it for the root too
        ## item_prefs = self.display_prefs_for_node(node)
            # [bruce 070504 comment: item_prefs was not yet used; in principle, should be passed to make_new_subtree_for_node]
        self.item_to_node_dict[item] = node
        self.node_to_item_dict[node] = item
        if hasattr(node, 'members'):
            for child in node.members:
                self.make_new_subtree_for_node(child, item)
        #bruce 070507 use setExpanded -- can't do it here, since index is not yet set; done by caller
        return item

    def make_new_subtree_for_node_NEW(self, node): #bruce 070525
        mtgui = self # kluge, i think [bruce 070525 comment]: self has some of the same attrs as _our_TreeItem_NEW ###k see if true
        item = _our_TreeItem_NEW(node, mtgui) #bruce 070523 experiment; works; bruce 070525 update: now using it for the root too
        ## item_prefs = self.display_prefs_for_node(node)
            # [bruce 070504 comment: item_prefs was not yet used; in principle, should be passed to make_new_subtree_for_node]
##        self.item_to_node_dict[item] = node # now done in _our_TreeItem_NEW
##        self.node_to_item_dict[node] = item
##        if hasattr(node, 'members'):
##            for child in node.members:
##                self.make_new_subtree_for_node(child, item)
##        #bruce 070507 use setExpanded -- can't do it here, since index is not yet set; done by caller
        return item

    pass # end of class ModelTreeGui_QTreeView

# ==

# newer version of model tree gui which doesn't use QTreeView [bruce 070529]

MT_CONTENT_WIDTH = 500 # fixed content width for now

OPENCLOSE_AREA_WIDTH = 20
INDENT_OFFSET = 20
INDENT_0 = 20

MT_CONTENT_TOP_Y = 0

def x_for_indent(n):
    return INDENT_0 + INDENT_OFFSET * n

class MT_View(QtGui.QWidget):
    "mt contents view"
    def __init__(self, parent, palette_widget, modeltreegui):
        QtGui.QWidget.__init__(self, parent)
        self.palette_widget = palette_widget #e rename?
        self.modeltreegui = modeltreegui
        self.ne1model = self.modeltreegui.ne1model ###KLUGE? not sure. consider passing this directly?        
        self.get_icons()
        return

    def get_icons(self):
        from Utility import geticon, getpixmap
        # note: geticon calls QIcon, but painter has no drawIcon, and drawPixmap doesn't accept them,
        # so here we use getpixmap which calls QPixmap. We could also try QImage and painter.drawImage
        # (known to work for crate.bmp and other test images, but presumably slower).
        ## painter.drawImage(QtCore.QPoint(0, 0), self.image)

        if 0:
            # these are the pixmaps meant for groupbox buttons on the Mac; they're workable here:        
            self.mac_collapsed = getpixmap("ui/modeltree/mac_collapsed_icon.png") # 16 x 15, centering looks best
            self.mac_expanded = getpixmap("ui/modeltree/mac_expanded_icon.png") # 16 x 8 (.width() x .height()), centering looks best
            # (The Windows groupbox icons, win_expand_icon.png and win_collapse_icon.png, are not useful in an MT.)
##            print "size:", self.mac_expanded.width(), self.mac_expanded.height(), # size 16 8
        
        # As of 070530 9pm the following are renamed copies of the Mac groupbox icons above,
        # and are the same on Mac and Windows, but we should replace them with imitations of
        # the standard ones for those platforms.
        # We load them all here, since a debug_pref can switch between Mac and Win styles at runtime.
        # The comments describe their conventional appearance (NIM for Win style) and its interpretation.
        self.mac_collapsed = getpixmap("ui/modeltree/mac_collapsed_mtnode.png") # triangle pointing right (indicates "collapsed")
        self.mac_expanded =  getpixmap("ui/modeltree/mac_expanded_mtnode.png") # triangle pointing down (indicates "expanded")
        self.win_collapsed = getpixmap("ui/modeltree/win_collapsed_mtnode.png") # plus in a box (indicates "expand action")
        self.win_expanded =  getpixmap("ui/modeltree/win_expanded_mtnode.png") # minus in a box (indicates "collapse action")
        # Default MT style depends on platform, but user can change it at runtime
        # to the same set of possibilities on all platforms. For now this uses debug_prefs.
        if sys.platform == 'darwin':
            # Macintosh
            self._icon_style_choice = Choice(['mac', 'win'])
            self._openclose_lines_choice = Choice_boolean_False
        else:
            # Windows or Linux
            self._icon_style_choice = Choice(['win', 'mac'])
            self._openclose_lines_choice = Choice_boolean_True
        return

    def _setup_openclose_style(self):
        "[private] As an optimization, choose the openclose icons (etc) just once before drawing."
        
        style = debug_pref("Model Tree: openclose icon style", self._icon_style_choice,
                           non_debug = True, prefs_key = "A9/MT openclose icon style")
        if style == 'mac':
            self.collapsed_mtnode_icon = self.mac_collapsed
            self.expanded_mtnode_icon = self.mac_expanded
        else:
            self.collapsed_mtnode_icon = self.win_collapsed
            self.expanded_mtnode_icon = self.win_expanded

        self.draw_openclose_lines = debug_pref("Model Tree: openclose lines", self._openclose_lines_choice,
                           non_debug = True, prefs_key = "A9/MT openclose lines")
        return
    
    def sizeHint(self):
        # Note: this probably has no effect, since it's overridden by a resize in every mt_update.
        return QtCore.QSize(MT_CONTENT_WIDTH, 700)
    
    def paintEvent(self, event):
        # Note: if this paintEvent was in QAbstractScrollArea, Qt doc for that warns:
        #   Note: If you open a painter, make sure to open it on the viewport().
        # But, it's not in that (or its subclass QScrollArea), it's in the widget we're setting in that.
        # Note: we're painting using contents coords, not viewport coords (and this is working, as expected).
        # Question: would this change cliprect?
        ## painter.setViewport(0, 0, self.width(), self.height())
        if self.modeltreegui.MT_debug_prints():
            print 'paint' # note: this worked once we called update (it didn't require sizeHint to be defined)
        self._setup_openclose_style()
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            topnodes = self.ne1model.get_topnodes()
            x, y = x_for_indent(0), MT_CONTENT_TOP_Y
            for node in topnodes:
                y = self.paint_subtree(node, painter, x, y)
            pass
        finally:
            painter.end()
        return
    
    def paint_subtree(self, node, painter, x, y, line_to_pos = None, last_child = True):
        """Paint node and its visible subtree (at x,y in painter);
        return the y value to use for the next lower node.
           If this is a child node, the y position to which an "openclose line"
        (in case we're drawing them) needs to be drawn up to (from the center
         of our openclose icon) is passed in line_to_pos as an int; otherwise
        line_to_pos is None. Also, if last_child is False, we draw the openclose
        line (if we're drawing them) a bit lower down as well, so we can draw it
        before our openclose icon so as not to obscure it. Warning: those optional
        args are sometimes passed positionally.
        """
        openable = node.openable()
        open = node.open and openable
        if open:
            members = node.members
        else:
            members = ()
        # openclose line
        draw_openclose_lines = self.draw_openclose_lines
        next_line_to_pos = y + ITEM_HEIGHT # easiest to do this all the time
        if draw_openclose_lines:
            # draw them first (including the start of one going down, if needed), so they won't obscure icons.
            # In this section we draw the ones that go through (under) the center of our own openclose icon.
            doanything = (line_to_pos is not None) or members
            if doanything:
                # compute openclose area center:
                lx1 = x - OPENCLOSE_AREA_WIDTH / 2
                ly1 = y + ITEM_HEIGHT / 2
                painter.save() # otherwise we mess up the node text color -- I guess _paintnode is not self-contained re that
                painter.setPen(QColor(Qt.gray)) # width 0, solid line
            if line_to_pos is not None:
                # vertical line
                if last_child:
                    painter.drawLine(lx1, line_to_pos, lx1, ly1 )
                else:
                    painter.drawLine(lx1, line_to_pos, lx1, y + ITEM_HEIGHT ) # this goes a bit lower down;
                        # the knowledge of how much lower down is also known to the caller
                        # (i.e. this recursive function, in members loop below)
                # horizontal line
                painter.drawLine(lx1, ly1, x + _ICONSIZE[0]/2, ly1)
            if members:
                painter.drawLine(lx1 + INDENT_OFFSET, ly1,
                                 lx1 + INDENT_OFFSET, next_line_to_pos)
            if doanything:
                painter.restore()
        # node type icon and node name text (possibly looking selected and/or disabled)
        _paintnode(node, painter, x, y, self.palette_widget)
        # openclose decoration -- uses style set up by _setup_openclose_style for Mac or Win
        if openable:
            if open:
                pixmap = self.expanded_mtnode_icon
            else:
                pixmap = self.collapsed_mtnode_icon
            w = pixmap.width()
            h = pixmap.height()
            painter.drawPixmap(x - (OPENCLOSE_AREA_WIDTH + w)/2, y + (ITEM_HEIGHT - h)/2, pixmap)
                # this adjusts posn for pixmap size, to center the pixmap
            pass
        y += ITEM_HEIGHT
        if open:
            x += INDENT_OFFSET
            for child in members:
                its_last_child = (child is members[-1]) # wrong if children can occur twice in members
                y0 = y
                y = self.paint_subtree(child, painter, x, y, next_line_to_pos, its_last_child)
                # following only matters if not its_last_child
                next_line_to_pos = y0 + ITEM_HEIGHT
        return y

    def look_for_y(self, y):
        """Given y (in contents coordinates), find the node drawn under it,
        and return (node, its depth, its y0).
        If no node is under it, return None, None, None.
        """
        y0 = MT_CONTENT_TOP_Y
        d = 0 # indent level
        if y < y0:
            return None, None, None
        for child in self.ne1model.get_topnodes():
            resnode, resdepth, resy0, y0 = self.look_for_y_recursive( child, y0, d, y)
            if resnode:
                return resnode, resdepth, resy0
        return None, None, None
        
    def look_for_y_recursive(self, node, y0, d, y):
        """assuming node is drawn at vertical position y0 (in contents coordinates)
        and indent level d, find the node in its visible subtree (perhaps node itself)
        which is drawn over position y; return (that node, its depth, its y0, None), or (None, None, None, next_y0),
        where next_y0 is the y coordinate for the next node below the given node and its visible subtree.
        Assume without checking that y >= y0.
        """
        y0 += ITEM_HEIGHT
        if y < y0:
            return node, d, y0 - ITEM_HEIGHT, None
        if node.open:
            d += 1
            for child in node.members:
                resnode, resdepth, resy0, y0 = self.look_for_y_recursive( child, y0, d, y)
                if resnode:
                    return resnode, resdepth, resy0, y0
        return (None, None, None, y0)

    # WARNING: the following methods duplicate some of the code in _our_QItemDelegate in the other MT implem, far above.
    
    def createEditor(self, node):
        "Create and return a QLineEdit child widget to serve as an editor for the given node; initialize its text."
        parent = self
        qle = QLineEdit(parent)
        self.setEditorData(qle, node)
        return qle

    def setEditorData(self, lineEdit, node):
        "copy the editable data from node to lineEdit"
        value = node.name
        lineEdit.setText(value)
        return

    def setModelData(self, lineEdit, node):
        "copy the editable data from lineEdit to node (if permitted); display a statusbar message about the result"
        # Note: try_rename checks node.rename_enabled()
        # BUG: try_rename doesn't handle unicode (though it seems to handle some non-ascii chars somehow)
        # Note: see similar code in a method in another class in this file.
        oldname = node.name
        ok, text = node.try_rename( lineEdit.text() )
        # if ok, text is the new text, perhaps modified;
        # if not ok, text is an error message
        if ok:
            msg = "Renamed node [%s] to [%s]" % (oldname, text) ##e need quote_html??
            self.statusbar_message(msg)
            ## self.modeltreegui.mt_update() #e might be redundant with caller; if so, might be a speed hit
        else:
            msg = "Can't rename node [%s]: %s" % (oldname, text) # text is reason why not
            self.statusbar_message(msg)
        return

    def statusbar_message(self, text): #bruce 070531
        self.modeltreegui.statusbar_message(text)
        return
    
    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        rect.setX(rect.x() + _ICONSIZE[0])
        qfm = QFontMetrics(editor.font())
        width = qfm.width(editor.text()) + 10
        width = min(width, rect.width() - _ICONSIZE[0])
##        parent = self.parent()
        parent = self
        width = min(width, parent.width() - 50 - rect.x())
        rect.setWidth(width)
        editor.setGeometry(rect)
        return
        
    pass # end of class MT_View

import time

class FakeItem:
    def __init__(self, node):
        self.node = node
    def height(self):
        return ITEM_HEIGHT ##k
    pass

class ModelTreeGui(QScrollArea, ModelTreeGui_common):#bruce 070529-30 rewrite of some of class ModelTreeGui_QTreeView
    
    def __init__(self, win, name, ne1model, parent = None):
        ## print "what are these args?", win, name, ne1model, parent
        # win = <MWsemantics.MWsemantics object at 0x4ce8a08>
        # name = modelTreeView
        # ne1model = <modelTree.modelTree instance at 0x4cfb3a0>
        # parent = <PyQt4.QtGui.QWidget object at 0x4cff468>
        del name
        QScrollArea.__init__(self, parent)
        ###e  setWidgetResizable ? (default False - honors size of widget - done when fitToWindow checked, in the imageviewer example)
        # adjustSize? (called when *not* fitToWindow -- more like our case... i don't fully understand it from docs)
        # updateGeometry? (call when sizeHint changed)
##        self.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)

        self.setContextMenuPolicy(Qt.PreventContextMenu) #bruce 070509 change; I hope it will prevent direct calls of contextMenuEvent

        # this has to be done after QScrollArea.__init__, since it assumes QWidget init has occurred
        ModelTreeGui_common.__init__(self, win, ne1model) ## mouse and DND methods -- better off in view widget or here??
            # will this intercept events meant for the scrollbars themselves??? need to use the contents event methods?
        
        self.view = MT_View( self, self, self) # args are: parent, palette_widget, modeltreegui
        self.setWidget(self.view)
        
        # Model Tree background color. Mark 2007-06-04
        from prefs_constants import mtColor_prefs_key # In case we want to make it a user pref.
        from widgets import RGBf_to_QColor
        mtColor = RGBf_to_QColor(env.prefs[mtColor_prefs_key]) 
        from PropMgrBaseClass import getPalette
        self.setPalette(getPalette(None, QPalette.Window, mtColor))

        #e not sure if mt_update would be safe at this point (were cooperating objects fully initialized?)

##        self._debug_scrollbars("init") # they have arbitrary-looking values at this point, later corrected, evidently

        return
    
    def _scrollbars(self):
        hsb = self.horizontalScrollBar()
        vsb = self.verticalScrollBar()
        return hsb, vsb
    
    def _debug_scrollbars(self, when): # not normally called except when debugging
        print "debug_scrollbars (%s)" % when
        hsb, vsb = self._scrollbars() # they are always there, even when not shown, it seems
##        if hsb:
##            print "hsb pageStep = %r, singleStep = %r, minimum = %r, maximum = %r" % \
##                  (hsb.pageStep(), hsb.singleStep(), hsb.minimum(), hsb.maximum())
        if vsb:
            print "vsb pageStep = %r, singleStep = %r, minimum = %r, maximum = %r" % \
                  (vsb.pageStep(), vsb.singleStep(), vsb.minimum(), vsb.maximum())
        return

    def nodeItem(self, node):
        return FakeItem(node)
    
    def mt_update(self):
        "part of the public API"

        if self.MT_debug_prints():
            print 'mt_update',time.asctime()

        # probably we need to scan the nodes and decide what needs remaking (on next paintevent) and how tall it is;
        # should we do this in MT_View? yes.
        self.__count = 0
        def func(node):
            self.__count += 1 # using a local var doesn't work, due to Python scoping
        self.ne1model.recurseOnNodes(func, visible_only = True)
        height = self.__count * ITEM_HEIGHT
        if self.MT_debug_prints():
            print "mt_update: total height", height

##        self._debug_scrollbars("mt_update pre-resize")

        self.view.resize(MT_CONTENT_WIDTH, height)
        #e updateGeometry? guess: this does that itself. I don't know for sure, but the scrollbars do seem to adjust properly.

##        self._debug_scrollbars("mt_update post-resize")

        hsb, vsb = self._scrollbars()
        if vsb:
            vsb.setSingleStep( ITEM_HEIGHT )
            vsb.setPageStep( vsb.pageStep() / ITEM_HEIGHT * ITEM_HEIGHT )
                #k Note: It might be enough to do setSingleStep once during init, since the value seems to stick --
                # but the page step is being quantized, so that has to be redone every time.
                # NFR: I don't know how to set a "motion quantum" which affects user-set positions too.
        
##        self._debug_scrollbars("mt_update post-correct")
        
        self.view.update() # this works
        self.update() # this alone doesn't update the contents, but do it anyway to be sure we get the scrollbars (will it be enough?)

##        self._debug_scrollbars("mt_update post-update")
        return
    
    def update_item_tree(self, unpickEverybody = False):
        "part of the public API"
        self.mt_update()

    def paint_item(self, painter, item):
        x,y = 0,0
        node = item.node
        _paintnode(node, painter, x, y, self.view) # self.view is a widget used for its palette

        width = 160 ###k guess; should compute in paint and return, or in an aux subr if Qt would not like that
        return width

    def item_and_rect_at_event_pos(self, event):
        """Given a mouse event, return the item under it (or None if no item),
        and a QRect encompassing certain(?) parts of it (or None if no item).
        ### which parts?
        ### what coords?
        """
        pos = event.pos()
        x, y = pos.x(), pos.y()
##        print "viewport pos x = %r, y = %r" % (x,y)
        
        dx, dy = self.get_scrollpos("item_and_rect_at_event_pos") # in pixels (will that remain true if we scroll by items?)

        cx = x + dx
        cy = y + dy

        # do item hit test in contents (inner) coords cx, cy, but return item's rect in viewport (outer) coords x, y.
        # Note: in variable names for x or y coords, we use 'c' to mean "contents coords" (otherwise viewport),
        # and suffix '0' to mean "coordinate of item reference point (top left of type icon)" (otherwise of mouse event).

        node, depth, cy0 = self.view.look_for_y( cy)
        if node:
            item = self.nodeItem(node)
            if 1:
                cx0 = x_for_indent(depth)
                    # Note: this is correct if the rect is supposed to be including the type icon -- is it? I think so.
                    # (This affects whether clicks on type icon can select the node. I think it's good if they can.)
                x0 = cx0 - dx
                y0 = cy0 - dy
                w = MT_CONTENT_WIDTH #STUB, but good enough for now --
                    # maybe better than being correct re clicks to right of text?? not sure.
                    # To make it correct, could use the code that makes a temporary QLineEdit, if slow is ok (I think it is)...
                    # Wait, that code is being used on exactly this value in our caller, so what we set here doesn't matter!
                h = ITEM_HEIGHT
                rect = QRect( x0, y0, w, h) # viewport coords
            return item, rect
        else:
            return None, None
        pass

    def set_scrollpos(self, pos): 
        assert 0, "don't use set_scrollpos in this QScrollArea-using subclass, without thinking twice!"

    def mouseDoubleClickEvent(self, event):
        self.mousePressEvent(event, _doubleclick = True) # this calls the following method in self (sometimes)

    def handle_doubleclick(self, event, item, rect):
        # print "handle_doubleclick" # this gets called when expected
        # temporary kluge, 070531, to be released for A9: use a dialog.
        # (Later we'll try using an in-place QLineEdit; some stub code for that is elsewhere in this file.)
        node = item.node
        self.rename_node_using_dialog( node) # note: this checks node.rename_enabled() first
        return
    
    pass # end of class ModelTreeGui

def debug_pref_use_old_MT_code(): #bruce 070531 split out, removed non_debug = True, changed name/sense/key/default
    return debug_pref("MT: use old QTreeView code (next session)?", Choice_boolean_False, prefs_key = True)

if debug_pref_use_old_MT_code():
    ModelTreeGui = ModelTreeGui_QTreeView

# bugs in new class ModelTreeGui based on QScrollArea [070531 2pm PT]:
#
# - mouse events:
#   openclose - works now
#   selection - some works, rest not tested
#   cmenus - some work, except bug [fixed now] in selection update when menu is shown, i.e.
#    it fails to do click select behavior in visible way, when putting up menu, tho it probably does it internally
#    [fixed, tho update is too slow -- incremental redrawing of changed items (when only selection changes) would be better]
#   DND - seems to work; not fully tested
#   renaming - in place is NIM; using dialog works now
#   key events: arrow keys should move the selectedness up and down in the nodes, but now they move the scrollbar.
#
# - drawing:
#   - decoration icons need improvement
#   - bg color is wrong (or, need transparent icons)
#   - it's missing the header that says "model tree" -- we decided that's a feature, not a bug
#   - too slow
#     - set painter state less often? (esp for text)
#     - profile it?
#     - see if text or icons are taking the time
#     - is icon caching helping?
#     - make an image to keep it in, so it scrolls faster?
#     Maybe enough to just draw only in inval rect.
#
# - other:
#   - hsb always there, fixed content width
#   - rename_enabled ignored -- probably fixed
#   - maybe so are some properties about DND being permitted (not sure)
#
# - highly desired NFRs for A10:
#   - cross-highlighting with GLPane
#   - DND:
#     - autoscrolling during DND
#     - drop on group puts node before other members
#     - drop-point highlighting, between nodes



################ End of implementation #############################
####################################################################
####################################################################


####################################################################
####################################################################
##################### Test code ####################################

class TestNode(Node_api):
    def __init__(self, name, parent = None, icon = None, icon_hidden = None):
        self.open = False #bruce 070508 added this for api compliance; it's not otherwise used by test code
        self.hidden = False
        self._disabled = False
        self.name = name
        self.icon = icon
        self.icon_hidden = icon_hidden
        class FakeAssembly:
            def update_parts(self):
                pass
        self.assy = FakeAssembly() #bruce 070511 comment: this appears to never be used
        self.parentNode = parent
        if parent is not None:
            parent.members.append(self)
        self.members = [ ]
        self.picked = False
        if DEBUG0: self._verify_api_compliance()
    def showTree(self, indent = 0):
        "handy diagnostic"
        s = (indent * '\t') + repr(self)
        if self.picked: s += ' PICKED'
        print s
        for ch in self.members:
            ch.showTree(indent + 1)
    # beginning of official API
    def pick(self):
        self.picked = True
    def unpick(self):
        self.picked = False
    def apply2picked(self, func):
        if self.picked: func(self)
        for x in self.members:
            x.apply2picked(func)
    def drop_on_ok(self, drag_type, nodes):
        import sys, traceback
        for node in nodes:
            # don't drop stuff that's already here
            if node in self.members:
                traceback.print_stack(file = sys.stdout)
                print self, nodes, node, self.members
                print 'node is in children already'
                return False
        # We can't drop things on chunks or jigs
        if self.name.startswith("Chunk"):
            traceback.print_stack(file = sys.stdout)
            print self, node, self.members
            print 'cannot drop on a chunk'
            return False
        if self.name.startswith("Jig"):
            traceback.print_stack(file = sys.stdout)
            print self, node, self.members
            print 'cannot drop on a jig'
            return False
        return True
    def drop_on(self, drag_type, nodes):
        previous_parents = { }
        for node in nodes:
            if drag_type == 'copy':
                node = node.clone()
            previous_parents[node] = node.parentNode
            self.members.append(node)
            node.parentNode = self
            node.unpick()
        if drag_type == 'move':
            for node in nodes:
                previous_parents[node].members.remove(node)
        return [ ]
    def node_icon(self, display_prefs):
        # read up on display_prefs?
        if self.hidden:
            return self.icon_hidden
        else:
            return self.icon
    def is_disabled(self):
        return self._disabled
    # end of official API
    def clone(self):
        newguy = self.__class__(self.name + "-copy", None, self.icon, self.icon_hidden)
        newguy.hidden = self.hidden
        newguy._disabled = self._disabled
        newguy.members = self.members[:]
        return newguy
    def kids(self, item_prefs):
        return self.members
    def __repr__(self):
        return "<Node \"%s\">" % self.name

class TestClipboardNode(TestNode):
    def __init__(self, name):
        TestNode.__init__(self, name)
        self.iconEmpty = QPixmap("../images/clipboard-empty.png")
        self.iconFull = QPixmap("../images/clipboard-full.png")
        self.iconGray = QPixmap("../images/clipboard-gray.png")
        if DEBUG0: self._verify_api_compliance()

    def node_icon(self, display_prefs):
        if self.hidden:  # is the clipboard ever hidden??
            return self.iconGray
        elif self.members:
            return self.iconFull
        else:
            return self.iconEmpty

class TestNe1Model(Ne1Model_api):
    def __init__(self):
        self.untitledNode = TestNode("Untitled", None,
                                     QPixmap("../images/part.png"))
        self.clipboardNode = TestClipboardNode("Clipboard")
        if DEBUG0: self._verify_api_compliance()

    def get_topnodes(self):
        return [self.untitledNode, self.clipboardNode]

    def make_cmenuspec_for_set(self, nodeset, optflag):
        for node in nodeset:
            def thunk(str):
                def _thunk(str=str):
                    print str
                return _thunk
            if isinstance(node, TestNode):
                disableTuple = ('Disable', lambda node=node: self.cm_disable(node))
                if node.name.startswith("Chunk"):
                    disableTuple += ('disabled',)

                return [('Copy', lambda node=node: self.cm_copy(node)),
                        ('Cut', lambda node=node: self.cm_cut(node)),
                        ('Hide', lambda node=node: self.cm_hide(node)),
                        disableTuple,
                        None,
                        ('Delete', lambda node=node: self.cm_delete(node))]
            else:
                return [('A', thunk('A')),
                        ('B', thunk('B')),
                        None,
                        ('C', thunk('C'), 'disabled'),
                        ('D', thunk('D'))]
        return [ ]

    def complete_context_menu_action(self):
        # unpick all nodes
        for x in self.get_topnodes():
            x.apply2picked(lambda node: node.unpick())
        self.view.mt_update()

    def cm_copy(self, node):
        nodelst = self.view.topmost_selected_nodes()
        if node not in nodelst:
            nodelst.append(node)
        self.clipboardNode.drop_on('copy', nodelst)
        self.complete_context_menu_action()

    def cm_cut(self, node):
        nodelst = self.view.topmost_selected_nodes()
        if node not in nodelst:
            nodelst.append(node)
        self.clipboardNode.drop_on('move', nodelst)
        self.complete_context_menu_action()

    def cm_disable(self, node):
        node._disabled = not node._disabled
        self.complete_context_menu_action()

    def cm_hide(self, node):
        node.hidden = not node.hidden
        self.complete_context_menu_action()

    def cm_delete(self, node):
        node.parentNode.members.remove(node)
        self.complete_context_menu_action()

class TestGLPane:
    def gl_update(self):
        print 'GL Pane update'
class TestMainWindow:
    def __init__(self):
        self.glpane = TestGLPane()
        self.orientationWindow = None

class TestWrapper(QGroupBox):

    def __init__(self):
        QGroupBox.__init__(self)

        self.ne1model = ne1model = TestNe1Model()

        self.view = view = ModelTreeGui(TestMainWindow(), "Model tree", ne1model, self)
        view.mt_update()
        self.chunkNum = 2
        self.gbox = QGroupBox()
        vl = QVBoxLayout(self)
        vl.setSpacing(0)
        vl.setMargin(0)
        vl.addWidget(self.view)
        self.buttonLayout = hl = QHBoxLayout()
        hl.setSpacing(0)
        hl.setMargin(0)
        vl.addLayout(hl)
        self.buttonNum = 1
        for func in (self.addmol, self.addjig, self.selected):
            self.addButton(func)

    def addButton(self, func):
        button = QPushButton(func.__doc__)
        setattr(self, "button%d" % self.buttonNum, button)
        self.buttonNum += 1
        self.buttonLayout.addWidget(button)
        self.connect(button, SIGNAL('clicked()'), func)

    def addIconButton(self, icon, func):
        button = QPushButton()
        button.setIcon(icon)
        setattr(self, "button%d" % self.buttonNum, button)
        self.buttonNum += 1
        self.buttonLayout.addWidget(button)
        self.connect(button, SIGNAL('clicked()'), func)

    def addsomething(self, what):
        if what == "Chunk":
            icon = QPixmap('../images/moldefault.png')
            icon_h = QPixmap('../images/moldefault-hide.png')
        else:
            icon = QPixmap('../images/measuredistance.png')
            icon_h = QPixmap('../images/measuredistance-hide.png')
        chunk = TestNode("%s-%d" % (what, self.chunkNum),
                         self.ne1model.untitledNode, icon, icon_h)

        self.chunkNum += 1
        self.view.mt_update()

    def addmol(self):
        "Chunk"
        # This is equivalent to Part.addmol() in part.py
        self.addsomething("Chunk")

    def addjig(self):
        "Jig"
        self.addsomething("Jig")

    def selected(self):
        "Selected"
        print self.view.topmost_selected_nodes()

####################################################################

def test_api():
    # Test API compliance. If we remove all the functionality, pushing buttons shouldn't raise any
    # exceptions.
    global ModelTreeGui, _our_QItemDelegate, _QtTreeModel
    ModelTreeGui = ModelTreeGui_api
    del _QtTreeModel
    del _our_QItemDelegate

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.wrapper = TestWrapper()
        self.setCentralWidget(self.wrapper)
        self.resize(200, 300)
        self.wrapper.show()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        test_api()
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
