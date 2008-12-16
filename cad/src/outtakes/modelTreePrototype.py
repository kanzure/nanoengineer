# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
modelTreePrototype.py

$Id$

This is a prototype for a Qt 4 compatible Model Tree. It is a standalone test program, not part of NE1 proper.

Usage: on some sysems, this can be run from the command line using

  % pythonw `pwd`/modelTreePrototype.py

Goals/plans:

Develop a clear simple API for the model tree, then work on the model tree in isolation using simple
test data, and then plug the working model tree into the rest of NE-1. This amounts to a refactoring
of the code currently spread between TreeView.py, TreeWidget.py, and modelTree.py.

The API needs to accomplish three things. First it must work in just this file with a very
restricted set of data, and in this context I need to bang on issues of selection, display, and
other GUI stuff. Second it needs to work with the uiPrototype.py stuff for the new user interface.
Third it needs to migrate into the NE-1 code cleanly, ideally with just a change of the filename.
"""

import sys

from PyQt4.Qt import QTreeView
from PyQt4.Qt import QItemDelegate
from PyQt4.Qt import QAbstractItemModel
from PyQt4.Qt import QGroupBox
from PyQt4.Qt import QMainWindow
from PyQt4.Qt import QIcon
from PyQt4.Qt import QTextEdit
from PyQt4.Qt import QVariant
from PyQt4.Qt import Qt
from PyQt4.Qt import QModelIndex
from PyQt4.Qt import QItemSelectionModel
from PyQt4.Qt import QFontMetrics
from PyQt4.Qt import QLineEdit
from PyQt4.Qt import QDrag
from PyQt4.Qt import QMimeData
from PyQt4.Qt import QPoint
from PyQt4.Qt import QMouseEvent
from PyQt4.Qt import QMenu
from PyQt4.Qt import QAction
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QPixmap
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import QHBoxLayout
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QApplication

_ICONSIZE = (22, 22) #bruce 070507 copied this over, not used enough


def todo(x):
    print 'TODO:', x

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

"""
Bruce suggests the following. Make a list of all the methods in TreeView/TreeWidget/modelTree, and
classify all those methods as follows. Here I will use the word 'model' to refer to NE-1's concept
of a tree of Nodes, rather than the Qt4 concept of a model as a tree of items.

(1) Methods that are internal to the view, which should be limited to TreeView and TreeWidget.
(2) Methods that are internal to the model, which should be limited to modelTree.
(3) Methods which the view exposes to the model: their definitions appear in TreeView or
    TreeWidget, but they are used in modelTree.
(4) Methods which the model exposes to the view: their definitions appear in modelTree, but they
    are used in TreeView or TreeWidget.

The (3) methods define the view API as seen by the model. The (4) methods define the model API as
seen by the view. One thing we will find in (4) is a callback to create a context menu spec, and the
model doesn't know when the view will need that so it does have to be a callback.

The model includes, but is not limited to, the tree of Nodes that I've been thinking about thusfar.

So my API is the (3) and (4) methods, and I can ignore the (1) and (2) methods.

Generally, what will happen is that the NE-1 'model' will be translated to a Qt4 'model' by
something like make_new_subtree_for_node. So the use of the words 'view' and 'model' here are from
NE-1's perspective, not the way Qt4 thinks of them.


-----------------------------------------------

The API that the view exposes to the model is these (3) methods:

pick(self, item, group_select_kids=True)
unpick(self, item, group_select_kids=True)
topmost_selected_nodes(self)
mt_update(self, nodetree=None)
toggle_open(self, item, openflag=None)

The API that the model exposes to the view is these (4) methods:

get_topnodes(self)
post_update_topitems(self)
QListViewItem_subclass_for_node(self, node, parent, display_prefs, after)
make_cmenuspec_for_set(self, nodeset, optflag)

=============================

How does renaming work in Qt 3?

TreeWidget.slot_itemRenamed() is connected to Q3ListView.itemRenamed(). It accepts an item, a column
number, and the new text. If everything is OK, it calls item.setText(col,newname). What I am not
seeing is how the name gets from the Q3ListViewItem back to the Node. So renaming is a big mystery to
me, and I'll ask Bruce about it later.
"""

class Ne1Model_api:
    def get_topnodes(self):
        """Return a list of the top-level nodes, typically assy.tree and assy.shelf for an Assembly.
        """
        raise Exception('overload me')
        return []
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
        return [ ]
    #
    # These other two methods, I think I maybe don't need.
    #
    def post_update_topitems(self):
        "#doc"
        # The Qt 3 code provides no useful documentation on this method. What it actually does is
        # just <<< self.tree_item, self.shelf_item = self.topitems[0:2] >>>. self.tree_item is used
        # in viewportPaintEvent (described as 'the main redrawing event for a QListView').
        # self.shelf_item is some kind of pointer to the clipboard, and is used as an argument to
        # toggle_open(). self.tree_item and self.shelf_item are subclasses of QListViewItem.

        # I will need to think about the behavior for opening groups and clipboards.

        # The NE-1 model should NEVER EVER thinks about Qt items. I will consider this method to be
        # internal to the view and not a part of the formal API.
        raise Exception('overload me')

    def QtItem_subclass_for_node(self, node, parent, display_prefs, after):
        """Return an appropriate subclass of QItemDelegate for this node.
           This subclass's __init__ must work for either of these two forms of arglist,
        by testing the type of the second argument:
        self, parent, after (after = another QListView item)
        or self, parent, text.
           Furthermore, its setText method must work for (self, 0, text)
        in the same way as its __init__ method (or by letting QListViewItem handle it).
           [Subclasses of TreeView can override this method, perhaps by letting their
        tree's nodes influence the chosen subclass, or perhaps having a custom subclass
        for the entire tree.]
        """
        # I don't want to use this. Bruce's original intent was that this code should be useful for
        # other trees besides the model tree. To do that, you should subclass ModelTree below and
        # redefine make_new_subtree_for_node() to refer to a new class that inherits _QtTreeItem.
        #
        # The NE-1 model should NEVER EVER thinks about Qt items. Let the customer code define
        # subclasses of ModelTree and _QtTreeItem, and confine any magical paint() code to those.
        raise Exception('overload me')

class Node_api:
    """The customer must provide a node type that meets this API. This can be done by extending this
    class, or implementing it yourself.
    """

    # There still needs to be an API call to support renaming, where the model tree is allowed to
    # change the Node's name.

    def __init__(self):
        """self.name MUST be a string instance variable. self.hidden MUST be a boolean instance
        variable. There is no API requirement about arguments for __init__.
        """
        raise Exception('overload me')

    def is_disabled(self):
        """MUST return a boolean"""
        raise Exception('overload me')

    def node_icon(self, display_prefs):
        """MUST return either a QPixmap or None"""
        # display_prefs is used in Group.node_icon to indicate whether a group is open or closed. It
        # is not used anywhere else. It is a dictionary and the only relevant key for it is"open".
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

class ModelTree_api(QTreeView):
    """This should be a Qt4 widget that can be put into a layout.
    """
    def pick(self, item, group_select_kids=True):
        "select the given item (actually the node or group it shows)"
        raise Exception('overload me')

    def unpick(self, item, group_select_kids=True):
        "deselect the given item (actually the node or group it shows)"
        raise Exception('overload me')

    def topmost_selected_nodes(self): #e might be needed by some context menus... how should the makers ask for it?
        "return a list of all selected nodes as seen by apply2picked, i.e. without looking inside selected Groups"
        raise Exception('overload me')

    def mt_update(self, nodetree=None):
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

    def toggle_open(self, item, openflag=None):
        """Toggle the open/closed state of this item, or set it to openflag
        if that's supplied. Do all necessary invals or repaints, including
        creation of new child items if needed.
        (Error if item is not openable; this may or may not be checked here.)
        """
        raise Exception('overload me')


####################### End of the API #############################
####################################################################
####################################################################
####################################################################
####################################################################
####################################################################
#################### Implementation ################################

class _QtTreeItem(QItemDelegate):
    # Extending QItemDelegate allows you to customize the paint() method. We need to do this because
    # we have a combination of requirements that weren't anticipated in Qt 4.1, more might be
    # available in Qt 4.2.
    #
    # QTreeWidget can give you icons and a tree structure, but you don't get much ability to
    # customize things like shear, and you can't force a repaint of the model tree when you want it.
    #
    # QTreeView provides a forced repaint with the setModel() method (see notes below about
    # veryShallowClone). The hassle of doing this is needing to learn the intricacies of Qt's
    # model/view programming model.
    #
    def __init__(self, node, parent=None):
        QItemDelegate.__init__(self, parent)
        self.node = node
        self.childItems = []
        self.cmenu = [ ]
        self.editing = False
        if parent is not None:
            parent.childItems.append(self)
        self.parentItem = parent

    def __repr__(self):
        return '<%s \"%s\">' % (self.__class__.__name__, self.node.name)

    def paint(self, painter, option, index):
        item = index.internalPointer()
        x, y = option.rect.x(), option.rect.y()
##        selected = (index in self.view.selectedIndexes())
        selected = item.node.picked
        disabled = item.node.is_disabled()
        hidden = item.node.hidden

        if selected: # before
            background = painter.background()
            backgroundMode = painter.backgroundMode()
            painter.setBackground(self.view.palette().highlight())
            painter.setBackgroundMode(Qt.OpaqueMode)

        if disabled: # before
            painter.shear(0, -0.5)
            painter.translate(0.5 * y + 4, 0.0)

        display_prefs = { } # ? ? ? ?
        pixmap = QIcon(item.node.node_icon(display_prefs)).pixmap(16, 16)
        painter.drawPixmap(x, y, pixmap)
        painter.drawText(x + 20, y + 12, item.node.name)

        if disabled: # after
            painter.translate(-0.5 * y - 4, 0.0)
            painter.shear(0, 0.5)

        if selected: # after
            painter.setBackground(background)
            painter.setBackgroundMode(backgroundMode)

    #def sizeHint(self, styleOptions, index):
    #    return QSize(16, 16)

    # This stuff is supposed to help with renaming, but it's not working yet.
    #

    def createEditor(self, parent, option, index):
        editor = QTextEdit(parent)
        editor.setMinimumHeight(24)
        return editor

    def setEditorData(self, textEdit, index):
        value = str(index.model().data(index, Qt.DisplayRole).toString())
        textEdit.setPlainText(value)

    def setModelData(self, textEdit, model, index):
        value = textEdit.toPlainText()
        model.setData(index, QVariant(value))

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)



####################################################################

# Here is a potentially confusing point. There are two levels of model. Because of
# Qt's model/view paradigm, we need a "Qt model" separate from the view of the data
# in the model. But all that stuff is packaged into something that looks like a
# view, from NE-1's perspective.

class _QtTreeModel(QAbstractItemModel):
    def __init__(self, rootItem=None):
        QAbstractItemModel.__init__(self)
        self.rootItem = rootItem
        self.indexdict = { }   # maps Nodes to indexes?
        def helper(item, self=self):
            row = 0
            for x in item.childItems:
                self.indexdict[x] = self.createIndex(row, 0, x)
                row += 1
                helper(x)
        helper(rootItem)

    def veryShallowClone(self):
        # This is part of the magic to UPDATING the model tree. We clone the model, and call
        # setModel on the new guy. We can use a very shallow clone for this, the QTreeView only
        # needs to see the pointer change.
        #
        return _QtTreeModel(self.rootItem)

    # We don't need indexToItem because we can use index.internalPointer().

    def itemToIndex(self, item):
        try:
            return self.indexdict[item]
        except KeyError:
            return QModelIndex()

    # The following methods are the the official API required by QTreeView's idea of how
    # QAbstractItemModel should work.

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()
        item = index.internalPointer()
        return QVariant(item.node.name)

    def setData(self, index, qvar):
        item = index.internalPointer()
        item.node.name = str(qvar.toString())

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsEditable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.rootItem.node.name)
        return QVariant()

    def index(self, row, column, parent):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem.childItems[row]
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parentItem
        if parentItem == self.rootItem:
            return QModelIndex()
        if parentItem.parentItem is None:
            parentRow = 0
        else:
            parentRow = parentItem.parentItem.childItems.index(parentItem)
        return self.createIndex(parentRow, 0, parentItem)

    def rowCount(self, parent):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        return len(parentItem.childItems)

####################################################################

class ModelTree(ModelTree_api):
    def __init__(self, name, ne1model, parent=None):
        QTreeView.__init__(self, parent)
        self.ne1model = ne1model
        ne1model.view = self
        self.setSelectionMode(self.ExtendedSelection) #bruce 070507 MultiSelection -> ExtendedSelection
        self.qtmodel = None
        self.drag = None
        self.setAcceptDrops(True)

    def selectedList(self):
        return map(lambda x: x.internalPointer().node,
                   self.selectedIndexes())

    def selectNodes(self, nodes, but_not=[ ]):
        selmodel = QItemSelectionModel(self.qtmodel, self)
        self.setSelectionModel(selmodel)
        for x in nodes:
            if x not in but_not:
                item = self.node_to_item_dict.get(x, None)
                if item is not None:
                    index = self.qtmodel.itemToIndex(item)
                    if index.isValid():
                        selmodel.select(index, selmodel.Select)

    def mt_update(self):
        ###REVIEW: this is an update method, but ideally it would be an invalidation method
        # (like I think it was in Qt3, though I'm not sure). Certainly it might be pretty slow this way
        # since it might do more updates than needed. [bruce 070504 comment]
        
        # save the list of which nodes are selected, we need them later
        selectedList = self.selectedList()
        # throw away all references to existing list items
        self.item_to_node_dict = { }
        self.node_to_item_dict = { }

        # Make a "fake" root node and give it the list of top nodes as children. Then convert the
        # tree of Nodes to a whole new tree of _QtTreeItems, populating the two dicts as we go.
        class FakeTopNode:
            def __init__(self, name, kidlist):
                self.name = name
                self.hidden = False
                self.kidlist = kidlist
            def kids(self, item_prefs):
                return self.kidlist
            def is_disabled(self):
                return False
            def node_icon(self, display_prefs):
                return None

        rootNode = FakeTopNode("Model tree", self.ne1model.get_topnodes())
        rootItem = self.make_new_subtree_for_node(rootNode)
        self.qtmodel = model = _QtTreeModel(rootItem)
        self.setModel(model)
        self.setItemDelegate(rootItem)
        rootItem.view = self  # needed for paint()

        # When we did setModel(), we lost the old selection information, so reselect
        self.selectNodes(selectedList)
        self.expandAll() ###BUG
        self.show()

    def make_new_subtree_for_node(self, node, parent=None):
        item = _QtTreeItem(node, parent)
        display_prefs = item_prefs = { }  # ? ? ?
        # item.icon = QIcon(node.node_icon(display_prefs))
        self.item_to_node_dict[item] = node
        self.node_to_item_dict[node] = item
        for kid in node.kids(item_prefs):
            self.make_new_subtree_for_node(kid, item)
        return item

    def expandAll(self):
        # With Qt 4.2, QTreeView will have its own expandAll method.
        # [bruce 070504 comment: we don't need this method anyway -- its only call is a bug.]
        for index in self.qtmodel.indexdict.values():
            self.expand(index)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        index = self.indexAt(event.pos())
        sellst = self.selectedList()
        if index.isValid():
            target_node = index.internalPointer().node
            dragged_nodes, drag_type, qdrag = self.drag
            # I don't think we need qdrag for anything, but it can't hurt.
            if target_node.drop_on_ok(drag_type, dragged_nodes):
                self.selectNodes(sellst, but_not=dragged_nodes)
                target_node.drop_on(drag_type, dragged_nodes)
                event.acceptProposedAction()
                self.mt_update()
                self.drag = None
                return
        event.ignore()
        self.mt_update()
        self.drag = None

    def mouseMoveEvent(self, event):
        if self.drag is not None:
            QTreeView.mouseMoveEvent(self, event)
            return
        if ((event.globalPos() - self.mouse_press_qpoint).manhattanLength()
            < QApplication.startDragDistance()):
            return
        #
        # starting a drag
        # [logic bug, after bruce change 070507: should not do this
        #  if we already started dragging out a selection. How can we tell?
        #  Only by whether the initial press had eventInRect, I think
        #  (not yet recorded), or at least, the initial move (#e could record here).]
        #
        index = self.indexAt(event.pos())

        sellst = self.selectedList() # bruce 070507 move earlier

        DEBUG2 = True

        if index.isValid():
            thisnode = index.internalPointer().node

            #bruce 070507 bring in some code from modelTreeGui.py
            alreadySelected = (thisnode in sellst)
            
            item = index.internalPointer()
            rect = self.visualRect(index)
            if DEBUG2:
                print "visualRect coords",rect.left(), rect.right(), rect.top(), rect.bottom()
            qfm = QFontMetrics(QLineEdit(self).font())
            rect.setWidth(qfm.width(item.node.name) + _ICONSIZE[0] + 4)
            if DEBUG2:
                print "visualRect coords, modified:",rect.left(), rect.right(), rect.top(), rect.bottom()
                # looks like icon and text, a bit taller than text (guesses)
            eventInRect = rect.contains(event.pos())
            if DEBUG2:
                print "valid index: eventInRect = %r, item = %r, index = %r, alreadySelected = %r" % \
                      (eventInRect, item, index, alreadySelected)#######
        else:
            thisnode = item = None
            alreadySelected = eventInRect = False
        
        if not eventInRect:
            # nothing to drag, but [bruce 070507] let super handle it (for dragging over nodes to select)
            self.drag_is_not_DND = True ### not yet used
            QTreeView.mouseMoveEvent(self, event)
            return

        if thisnode in sellst:
            # if dragging something selected, drag along all other selected ones
            dragged_nodes = sellst
        else:
            # if dragging something unselected, ignore any selected ones
            dragged_nodes = [ thisnode ]
        qdrag = QDrag(self)
        drag_type = 'move'  # how do I decide between 'move' and 'copy'?
        self.drag = (dragged_nodes, drag_type, qdrag)
        mimedata = QMimeData()
        mimedata.setText("need a string here for a valid mimetype")
        qdrag.setMimeData(mimedata)
        display_prefs = { }
        pixmap = dragged_nodes[0].node_icon(display_prefs)
        qdrag.setPixmap(pixmap)
        qdrag.setHotSpot(QPoint(-8, 8))
        qdrag.start()

    def mousePressEvent(self, event):
        self.drag_is_not_DND = False # don't know yet
        qp = event.globalPos()  # clone the point to keep it constant
        self.mouse_press_qpoint = QPoint(qp.x(), qp.y())
        self.mouse_press_event = QMouseEvent(event.type(),
                                             QPoint(event.x(), event.y()),
                                             event.button(), event.buttons(),
                                             event.modifiers())

    def mouseReleaseEvent(self, event):
        self.drag_is_not_DND = False
        if self.drag is None:
            QTreeView.mousePressEvent(self, self.mouse_press_event)
        self.drag = None
        QTreeView.mouseReleaseEvent(self, event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        pos = event.pos()
        index = self.indexAt(pos)
        if index.isValid():
            item = self.indexAt(pos).internalPointer()
            node = self.item_to_node_dict[item]
            nodeset = [ node ] # ? ? ? ?
            optflag = False  # ? ? ? ?
            cmenu_spec = self.ne1model.make_cmenuspec_for_set(nodeset, optflag)
            for x in cmenu_spec:
                if x is not None:
                    str, thunk = x[:2]
                    act = QAction(str, self)
                    act.setEnabled("disabled" not in x[2:])
                    self.connect(act, SIGNAL("triggered()"), thunk)
                    menu.addAction(act)
                else:
                    menu.addSeparator()
            menu.exec_(event.globalPos())



################ End of implementation #############################
####################################################################
####################################################################
####################################################################
####################################################################
##################### Test code ####################################

class TestNode(Node_api):
    def __init__(self, name, parent=None, icon=None, icon_hidden=None):
        self.hidden = False
        self._disabled = False
        self.name = name
        self.picked = True #bruce 070509 added this
        self.icon = icon
        self.icon_hidden = icon_hidden
        # We need to implement a tree structure with Nodes, which
        # is then duplicated in the _QtTreeItems.
        self.parentNode = parent
        if parent is not None:
            parent.childNodes.append(self)
        self.childNodes = [ ]
    # beginning of official API
    def drop_on_ok(self, drag_type, nodes):
        import traceback
        # We can't drop things on chunks or jigs
        for node in nodes:
            # don't drop stuff that's already here
            if node in self.childNodes:
                traceback.print_stack()
                print self, nodes, node, self.childNodes
                print 'node is in children already'
                return False
        if self.name.startswith("Chunk"):
            traceback.print_stack()
            print self, node, self.childNodes
            print 'cannot drop on a chunk'
            return False
        if self.name.startswith("Jig"):
            traceback.print_stack()
            print self, node, self.childNodes
            print 'cannot drop on a jig'
            return False
        return True
    def drop_on(self, drag_type, nodes):
        previous_parents = { }
        for node in nodes:
            if drag_type == 'copy':
                node = node.clone()
            previous_parents[node] = node.parentNode
            self.childNodes.append(node)
            node.parentNode = self
        if drag_type == 'move':
            for node in nodes:
                if previous_parents.has_key(node):
                    previous_parents[node].childNodes.remove(node)
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
        newguy.childNodes = self.childNodes[:]
        return newguy
    def kids(self, item_prefs):
        return self.childNodes
    def __repr__(self):
        return "<Node \"%s\">" % self.name

class TestClipboardNode(TestNode):
    def __init__(self, name):
        TestNode.__init__(self, name)
        self.iconEmpty = QPixmap("../images/clipboard-empty.png")
        self.iconFull = QPixmap("../images/clipboard-full.png")
        self.iconGray = QPixmap("../images/clipboard-gray.png")
    def node_icon(self, display_prefs):
        if self.hidden:  # is the clipboard ever hidden??
            return self.iconGray
        elif self.childNodes:
            return self.iconFull
        else:
            return self.iconEmpty

class TestNe1Model(Ne1Model_api):
    def __init__(self):
        self.untitledNode = TestNode("Untitled", None,
                                     QPixmap("../images/part.png"))
        self.clipboardNode = TestClipboardNode("Clipboard")

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

    def cm_copy(self, node):
        nodelist = self.view.selectedList()
        if node not in nodelist:
            nodelist.append(node)
        self.clipboardNode.drop_on('copy', nodelist)
        self.view.mt_update()

    def cm_cut(self, node):
        nodelist = self.view.selectedList()
        if node not in nodelist:
            nodelist.append(node)
        self.clipboardNode.drop_on('move', nodelist)
        self.view.mt_update()

    def cm_disable(self, node):
        node._disabled = not node._disabled
        self.view.mt_update()

    def cm_hide(self, node):
        node.hidden = not node.hidden
        self.view.mt_update()

    def cm_delete(self, node):
        self.untitledNode.childNodes.remove(node)
        self.view.mt_update()


class TestWrapper(QGroupBox):

    def __init__(self):
        QGroupBox.__init__(self)

        self.ne1model = ne1model = TestNe1Model()

        self.view = view = ModelTree("Model tree", ne1model, self)
        view.mt_update()

        def thunk(str):
            def _thunk(str=str):
                print str
            return _thunk

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
        print self.view.selectedList()

####################################################################

def test_api():
    # Test API compliance. If we remove all the functionality, pushing buttons shouldn't raise any
    # exceptions.
    global ModelTree, _QtTreeItem, _QtTreeModel
    ModelTree = ModelTree_api
    del _QtTreeModel
    del _QtTreeItem

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
