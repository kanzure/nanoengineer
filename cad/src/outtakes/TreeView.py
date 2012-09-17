# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
TreeView.py -- NO LONGER USED IN Qt4 NE1

 -- display and update, for a tree widget based on QTreeView,
and meant to display Nodes (with interface and semantics as in Utility.py).

Assumes each node is shown in at most one place in the widget.
This could in theory be changed (see code for details).

$Id$

History: modelTree.py was originally written by some combination of
Huaicai, Josh, and Mark. Bruce (Jan 2005) reorganized its interface with
Node and Group and their subclasses (Utility.py and other modules)
and rewrote a lot of the model-tree code (to fix bugs and add features),
and split it into three modules:
- TreeView.py (display and update),
- TreeWidget.py (event handling, and some conventions suitable for
  all our tree widgets, if we define other ones), and
- modelTree.py (customized for showing a "model tree" per se).
"""

assert 0, "TreeView.py is NO LONGER USED IN Qt4 NE1" #bruce 070503 Qt4

debug_painting = 0 ###@@@ DO NOT COMMIT with 1

debug_mt_updates = 0 ###@@@ DO NOT COMMIT with 1

debug_prints = 0 # whether atom_debug enables dprint; ok to commit with 0 or 1

###@@@ some of these imports are only needed by subclasses
from PyQt4.Qt import *
from constants import *
from chem import *
from jigs import *
from Utility import *
from foundation.Group import Group
import sys, os, time
from utilities import debug_flags
from qt4transition import *

class ModelTreeItem(QItemDelegate):
    def __init__(self, name, parent, node):
        QItemDelegate.__init__(self)
        self.parentItem = parent
        self.name = name
        self.object = node
        self.icon = None
        self.childItems = [ ]

    def __repr__(self):
        return "<ModelTreeItem@%x \"%s\">" % (id(self), self.name)

    def text(self, column):
        raise Exception()

    def setIcon(self, icon):
        self.icon = icon

    def row(self):
        try:
            return self.parentItem.childItems.index(self)
        except:
            return 0

    def appendChild(self, x):
        self.childItems.append(x)

    def paint(self, painter, option, index):
        item = index.internalPointer()
        x, y = option.rect.x(), option.rect.y()
        selected = (index in self.view.selectedIndexes())

        if selected: # before
            background = painter.background()
            backgroundMode = painter.backgroundMode()
            painter.setBackground(self.view.palette().highlight())
            painter.setBackgroundMode(Qt.OpaqueMode)

        if item.object.is_disabled(): # before
            painter.shear(0, -0.5)
            painter.translate(0.5 * y + 4, 0.0)

        painter.drawPixmap(x, y, item.icon.pixmap(16, 16))
        painter.drawText(x + 20, y + 12, item.name)

        if item.object.is_disabled(): # after
            painter.translate(-0.5 * y - 4, 0.0)
            painter.shear(0, 0.5)

        if selected: # after
            painter.setBackground(background)
            painter.setBackgroundMode(backgroundMode)


    def _paint(self, painter, option, index):
        item = index.internalPointer()
        x, y = option.rect.x(), option.rect.y()

        # What's failing here is not the display mechanism. Set this flag
        # to True and all distance measurement jigs will be shown as disabled.
        # The problem is with the context menu in modelTree.py, which is not
        # doing the right thing with the cm_disable method somehow. The 'Disable'
        # option appears in the context menu, but when you choose it, cm_disable
        # does not get called, as verified by putting a print statement in it.
        TEST_TO_SEE_IF_DISABLED_DISPLAY_WORKS = False

        if TEST_TO_SEE_IF_DISABLED_DISPLAY_WORKS:
            if item.name.startswith("Distance"):
                def is_disabled():
                    return True
                item.object.is_disabled = is_disabled

        if item.object.is_disabled():
            # Apply shear or other effects for "Hidden" and "Disabled" and "Selected"
            painter.shear(0, -0.5)
            painter.translate(0.5 * y + 4, 0.0)
            if item.icon is not None:
                painter.drawPixmap(x, y, item.icon.pixmap(16, 16))
            painter.drawText(x + 20, y + 12, item.name)
            painter.translate(-0.5 * y - 4, 0.0)
            painter.shear(0, 0.5)
        else:
            if item.icon is not None:
                painter.drawPixmap(x, y, item.icon.pixmap(16, 16))
            painter.drawText(x + 20, y + 12, item.name)

    def pr(self, indent=""):
        print indent, self
        for x in self.childItems:
            x.pr(indent + "    ")

####################################################################

class ModelTreeModel(QAbstractItemModel):
    def __init__(self, rootItem=None):
        QAbstractItemModel.__init__(self)
        if rootItem is None:
            rootItem = ModelTreeItem('Model Tree', None, None)
        self.rootItem = rootItem

    def veryShallowClone(self):
        #
        # This is part of the magic to UPDATING the model tree. We
        # clone the model, and call setModel on the new guy. We can
        # use a very shallow clone for this, the QTreeView only needs
        # to see the pointer change.
        #
        return ModelTreeModel(self.rootItem)

    def pr(self):
        print self
        self.rootItem.pr("  ")

    # The following methods are the the official API required by
    # QTreeView's idea of how QAbstractItemModel should work.

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()
        item = index.internalPointer()
        return QVariant(item.name)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.rootItem.name)
        return QVariant()

    def index(self, row, column, parent):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        if not hasattr(parentItem, 'childItems'):
            return QModelIndex()
        if row >= len(parentItem.childItems):
            return QModelIndex()
        childItem = parentItem.childItems[row]
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()


    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        childItem = index.internalPointer()
        if not hasattr(childItem, 'parentItem'):
            return self.createIndex(0, 0, childItem)
        parentItem = childItem.parentItem
        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        return len(parentItem.childItems)

##################################

class TreeView(QTreeView):
    needs_update_state = 0
    initialized = 0 ####@@@@ review use of this here vs in subclasses
    def __init__(self, parent, win, name = None, columns = ["node tree"], size = (100, 560)): ###@@@ review all init args & instvars, here vs subclasses
        """Create a TreeView (superclasses include QTreeView, QScrollView, QWidget).
        parent is the Qt widget parent.
        win (required) is our main window, stored in self.win
        and used for debug menu (by some subclasses).
        and for history messages (by subclasses -- not sure if also by this class).
        name is used by Qt as the widget name. #k
        columns is a list of column names (error if not at least one, if it's supplied).
        Note: we create all columns requested, but the present implem is only
        known to work for one column; some code in it only bothers trying to
        support one column (e.g. it assumes everything should be done only in column 0).
        """
        assert False   # we shouldn't be using TreeWidget or TreeView any more
        self.win = win
        self._node_items = {}
        QTreeView.__init__(self,parent) ###@@@ would any wflags be appropriate?

        # try doing these first, but if that fails, do them after columns are made [as before]:
        qt4skipit('self.setSorting(-1)')
		
        self.setRootIsDecorated(1)
        qt4skipit('self.setShowSortIndicator(0) # [this used to be done after setResizePolicy]')

        #self.columns = columns
        self.setItemsExpandable(True)

        self.model = model = ModelTreeModel()
        model.rootItem.view = self
        self.setModel(model)
        self.setItemDelegate(model.rootItem)
        self.expandAll()

        self.setSelectionMode(self.MultiSelection)

        ## self.addColumn("col2") # experiment - worked, but resulted in unwanted
        ## # sort indicator in col2 (with redraw bugs) [see QHeader in Qt docs?]
        ## ... might work better if done after we've turned off sorting.

        qt4todo('self.header().setClickEnabled(0, self.header().count() - 1) #k what\'s this?')
          # Qt doc says it's turning off the clicked signal for clicks in a certain
          # section header (which one? I don't know if count() is 1 or 2 for our one column.)

        # [some of the following might belong in a subclass or need to be influenced by one:]
        qt4skipit('self.setGeometry(QRect(0, 0, size[0], size[1]))')
        self.setMaximumWidth(200)

        # make a change needed by Geoff Leach [see his mail to cad 050304],
        # needed (at least back then) on his Linux system and/or Qt/PyQt installation
        # (this relates to some reported bug whose bug number I forget)
        # [bruce 050408]
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding))

        qt4skipit('self.setShowToolTips(True)')
            # bruce 050109 added this; but it doesn't seem to work

        ###@@@ where is item.setExpandable? implicit??

        # this is not safe to do here -- subclasses need to do it themselves!
        # if they forget, the symptom might be that no updates seem to happen.
        ## self.initialized = 1
        ## self.mt_update()

        return # from TreeView.__init__

    # invalidation function for use by external code
    # (and by some internal code in subclasses)

    def expandAll(self):
        #
        # With Qt 4.2, QTreeView will have its own expandAll method.
        #
        modelIndex = QModelIndex()
        while True:
            self.expand(modelIndex)
            modelIndex = self.indexBelow(modelIndex)
            if modelIndex.row() == -1:
                return

    def itemAt(self, qpoint):
        # emulate the equivalent function for QTreeView
        index = self.indexAt(qpoint)
        item = index.internalPointer()
        assert isinstance(item, ModelTreeItem)
        return item

    def visualItemRect(self, item):
        # get the index for this item
        index = self.model.createIndex(0, 0)
        while True:
            if index.internalPointer() == item:
                return self.visualRect(index)
            if index.row() == -1:
                # item wasn't found
                assert False
            index = self.indexBelow(index)

    def mt_update(self, nodetree = None): ###@@@ review name of this function, whether subclasses need to override it
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
        if debug_mt_updates:
            print "debug_mt_updates: mt_update called"
        self.needs_update_state = 1 # we'll respond to this in our custom method during the next paintEvent
        if not self.updatesEnabled():
            if debug_flags.atom_debug:
                print_compact_stack("atom_debug: stack in mt_update when not isUpdatesEnabled: ")
        # Force a repaint by changing the pointer to the model, using a shallow clone.
        self.model = self.model.veryShallowClone()
        self.model.rootItem.view = self
        self.setModel(self.model)
        self.expandAll()

    # debugging functions [might as well keep the commented-out ones around for awhile]

    _last_dprinttime_stamp = None
    def dprinttime(self):
        "call this to print a timestamp before every debug line for which the same time was never before printed"
        if not debug_prints: return
        if not debug_flags.atom_debug: return
        import time
        stamp = time.asctime() #e improve
        if stamp != self._last_dprinttime_stamp:
            print
            print stamp
        self._last_dprinttime_stamp = stamp
        return

    def dprint(self, msg):
        if not debug_prints: return
        if debug_flags.atom_debug:
            self.dprinttime()
            print msg
        return

    # update-related functions, and related event-processing
    # (not user input events -- those should be defined in subclasses)
    # (###@@@ #e though we might want to override them here to mask QTreeView from seeing them -- but maybe no need)

    def updateContents(self):
        if debug_prints:
            self.dprinttime()
            print "fyi: modelTree.updateContents() called (by Qt, maybe by triggerUpdate)"
            print_compact_stack("stack in updateContents(): ")
        self.update()

    def resize(self): #k does this get called? no.
        if debug_prints:
            self.dprinttime()
            print "fyi: modelTree.resize() called (by Qt, presumably)"
            print_compact_stack("stack in resize(): ")
        return QTreeView.resize(self)

    ###@@@ move this? for eventual use, into a subclass, but for debug use, keep a copy here...
    def drawbluething(self, painter, pos = (0,0), color = Qt.blue): # bruce 050110 taken from my local canvas_b2.py
        "[for debugging] draw a recognizable symbol in the given QPainter, at given position, of given color"
        p = painter # caller should have called begin on the widget, assuming that works
        p.setPen(QPen(color, 3)) # 3 is pen thickness
        w,h = 100,9 # bbox rect size of what we draw (i think)
        x,y = pos # topleft of what we draw
        p.drawEllipse(x,y,h,h)
        fudge_up = 1 # 1 for h = 9, 2 for h = 10
        p.drawLine(x+h, y+h/2 - fudge_up, x+w, y+h/2 - fudge_up)

    def paintEvent(self, event):
        """[This (viewportPaintEvent) turns out to be the main redrawing event for a QTreeView (in Qt3) --
        not that you can tell that from the Qt docs for it.
        """
        self.update_state_iff_needed(event)
        return QTreeView.paintEvent(self, event)

    def update_state_iff_needed(self, event):
        if self.needs_update_state and self.initialized:
            # new code 050110, see if it fixes any bugs -- defer state updates
            # (but should we instead do it in updateContents so it happens before that?? and/or do that here??) ###@@@ did neither for now
            try:
                self.needs_update_state = 0 # in case of exception
                self.update_state(event) # used to be mt_update; event is not really needed i think
                self.needs_update_state = 0 # in case of bug that sets this during that call
                    # [not sure this is good, but might avoid "infrepeat"]
                #e also call updateContents now? let's try it, see if it helps Group formation update bug:
                self.updateContents() ####k syntax and doc, for both qlistview and qscrollview ####@@@@
            except:
                self.dprinttime()
                print_compact_traceback("exception in update_state() or updateContents(): ")
        self.repaint()

    ###@@@ move this comment down below:
    # main tree-remaking function (runs more often than it would need to in a more incremental implem)

    # bruce 050107 renamed this 'update' -> 'mt_update';
    # then bruce 050110 renamed it 'update_state' and made it
    # no longer public, but called inside paintEvent(?)
    # when mt_update records the need for this

    def update_state(self, paintevent):
        """[private]
        Rebuild the tree of ModelTreeItems. Details in update_state_0 docstring.
        [no longer named update, since that conflicts with QWidget.update]
        """
        # Qt doc makes it clear (well, at least deducible)
        # that disabling updates is not redundant here,
        # and it says other things which lead me to guess
        # that it might avoid infrecur from repaint by QTreeView,
        # and even if not, might reduce screen flicker or other problems.
        if debug_mt_updates:
            print "debug_mt_updates: update_state called"
        old_UpdatesEnabled = self.updatesEnabled()
        if not old_UpdatesEnabled:
            self.dprint( "atom_debug: not old_UpdatesEnabled") # error?
        self.setUpdatesEnabled( False)
        try:
            self.update_state_0( paintevent)
        finally:
            self.setUpdatesEnabled( old_UpdatesEnabled)
            self.update() # might cause infrepeat... try it anyway [seems to be ok]
        #e should be no need to do an update right here, since we're only
        # called when a repaint is about to happen! But an updateContents
        # might be good, here or in the sole caller or grandcaller. ###@@@
        if debug_mt_updates:
            print "debug_mt_updates: update_state returning normally"
        return

    def update_state_0( self, paintevent):
        """[private]
        Build or rebuild a new tree of ModelTreeItems in this widget
        corresponding to the node tree of the current model; ###@@@ how does subclass tell us where to look for root nodes?
        assume updates are disabled in this widget.
        (#e Someday we might do this incrementally, ie. rebuild only part of the tree
        depending on what has been invalidated or is measured now to be invalid,
        though this is not done as of 050120. Relatedly, someday we might not build
        items for all hidden children (items whose parent items are closed), but
        for now we do.)
        """
        del paintevent

        # heavily revised by bruce circa 050109 [from the version called mt_update]
        # and split into this method and one or more subclass methods, bruce 050120

        # record the current scroll position so it can later be set to something similar
        qt4todo('self.scrollpos = self.viewportToContents(0,0)')

        #self.clear() # this destroys all our ModelTreeItems!
        self.clear_nodeItems() # and this makes sure we don't still try to update them.
            # As of 050113 this is still the only place we delete listview items.
            # We might do this more incrementally in the future,
            # for nodes whose kid order or set of kids changed --
            # though as far as I know, this won't fix bugs, it's just an optimization.
            #    We don't yet take much care to avoid old node.tritem pointing to
            # deleted list items! (Though current code won't experience this except
            # when it has bugs.) If those are ever used it causes a Qt exception.
            # This can be fixed when node.tritem is replaced with a
            # per-treewidget dict from nodes to their tree items...
            # as has now been done [050119], with self.nodeItem().

        listview = self # (would be self.widget if we were a megawidget)

        # subclass supplies one or more root nodes for the tree
        # [should be ok if this list is non-constant, but that's untested as of 050120]
        self.topnodes = self.get_topnodes()

        self.topitems = [] # rebuilt below, to correspond with topnodes

        self.model = model = ModelTreeModel()
        model.rootItem.view = self
        self.setItemDelegate(model.rootItem)
        self.setModel(model)

        lastitem = None ####@@@@ got to about here
        for node in self.topnodes:
            item = self.make_new_subtree_for_node(node, listview, self.model.rootItem, after = lastitem)
            lastitem = item
            self.topitems.append(item)

        self.expandAll()

        # Update open/highlighted state of all tree items [text, icon already done above]
        ###@@@ code copied below - merge?

        for item in self.topitems:
            self.update_open_selected_in_itemtree( item)

        self.post_update_topitems() # let subclass know about new self.topitems

        # set the scroll position to what it ought to be
        # [bruce circa 050113. Fixes bug 177.]
        qt4todo('x, y = self.scrollpos')
        qt4todo('self.setContentsPos( x, y)')
            ###@@@ not yet perfect, since we need to correct height
            # to be larger than needed for all items, when collapsing a group
            # which went below the visible area, so the group doesn't move on
            # screen due to QTreeView not liking empty space below the items.

        ## a note about why ensureItemVisible is not useful [bruce circa 050109]:
        ##self.ensureItemVisible(self.last_selected_node.tritem)
        ## this "works", but it looks pretty bad:
        ## - there's a lot of flickering, incl of the scrollbar (disabling updates might fix that)
        ## - it always puts this item at the very bottom, for the ones that would otherwise be off the bottom
        ## - even if this item is already visible near the top, it moves stuff, perhaps as if trying to center it.

        return # from update_state_0

    def get_topnodes(self):
        "[subclasses must override this to tell us what nodes to actually show]"
        return [] #e a better stub/testing value might be a comment node, if there is such a node class

    def post_update_topitems(self):
        "#doc"
        pass

    def update_selection_highlighting(self): ###@@@ #e let caller pass a subset or list to do it for?
        """The selection state might have changed; for each item whose selection state
        might be different now, set it properly via item.setSelected and repaint the item.
        """
        # [Note: this is presently only called from subclasses, because it's only useful as part of an incremental update
        # (otherwise the items were created with this already correct, or updated en masse right afterwards)
        # and so far only some subclass's own event methods do incremental updates.
        # But someday we'll let ourselves be given incremental inval info (by subclass event methods, or outside code)
        # and call this from our own update function when only certain kinds of incremental invals occurred.]

        ###@@@ this is way more work than needed -- just do it for single items in old xor new members of selitems lists!
        # we'll need to fix this to make the selection behavior look fast enough, else it'll look bad.
        for item in self.topitems:
            self.update_open_selected_in_itemtree(item, do_setOpen=0)
            ###@@@ code copied from above -- but this code will change, anyway. so nevermind.
            # w/o flag do_setOpen=0 it might do illegal changes for a slot function... not sure
        return

    # default implems, subclasses could override (but don't, so far); also,
    # self.isOpen(item) (nim) ought to be separated from display_prefs and not included in them.
    def display_prefs_for_node(self, node):
        """Return a dict of the *incremental* display prefs for the node,
        relative to whatever its parent passes as display prefs for its own kids.
        Any prefs that it should inherit from its parent's env should be left out of this dict.
        The main thing this needs to include (if this is an openable node)
        is whether this node should be open in this view.
        [Subclasses can override this.]
        [Using this cumbersomeness just to say whether the item is open
         is not worthwhile in hindsight. Fix it sometime. #e]
        """
        res = {}
        if node.openable(): ###e should use item_isOpen, but that's for items...
            res['openable'] = True ###@@@??? see setExpandable; and discussion in ModelTreeItem docs, esp about setup() function
            try:
                node.open ###@@@ obs, will be changed
            except:
                print "fyi: bug? openable node has no .open attr: %r" % node ###@@@ soon, none will need this, i think...
                res['open'] = False
            else:
                res['open'] = not not node.open
        return res

    def display_prefs_for_kids_of(self, node):
        """Return a dict of the *incremental* display prefs for this node's kids,
        relative to whatever its parent passes as display prefs for its own kids.
        Any that should inherit from parent's env should be left out of this dict.
        """
        return {}

    # basic data structure -- move this to some earlier position in the class #e

    def set_nodeItem(self, node, item): #050119
        self._node_items[node] = item # does not destroy old item, if any!

    def nodeItem(self, node):
        """Return the ModelTreeItem currently representing Node (in self)
        (this item might be hidden under closed higher nodes), or None.
        (If this item exists, then normally item.object == node.)
           Note that we (usually??) insist on node.dad corresponding to
        item.parent, so (always) one node can be shown in at most one place
        (per treewidget), thus can have at most one item per treewidget.
           [If you want to change this, consider instead using a new layer of
        nodes with these properties, between the tree widget and whatever
        nodes you're actually showing. If you *still* want to change it,
        then we'll still insist, I think, on all structural state being
        derived from display rules (which include the per-item "open" state)
        and node-tree structure, so that changes to the node tree result in
        deterministic but perhaps multiple changes to the item tree.
        But if that item tree, knowing "open", is ever lazily created in,
        terms of real ModelTreeItems, then we might end up needing to use
        permanent ones which end up being that same extra layer of nodes
        or at least permanent-item-position-ids.]
        """
        return self._node_items.get(node)
        # historical note [bruce 050119]:
        # this used to be stored in node.tritem (except that
        # attr was missing when this was None); this had two problems:
        # - no possibility for more than one tree widget showing the same nodes;
        # - there was no clear_nodeItems(), resulting in bugs from accessing
        #   deleted Qt objects when simple incremental update schemes were tried.
        # Unreviewed recent comment by me: "all this seems to be for is
        # setSelected, setOpen, and bookkeeping, and being created".
        # (Presumably, for other needs, we already have the item. If we go to
        # item-centric updating, then conceivably we'll no longer need this at
        # all -- then it would be easy to let it be a one-to-many function!
        # Well, we might still want it (in that form) for invalidation. Though
        # at the moment we survive without any per-node inval, so maybe not.)

    def clear_nodeItems(self):
        self._node_items.clear() # does not destroy old items!

    """Bug 1070 is one of these 'underlying C/C++ object has been
    deleted' bugs. These come up periodically, and they make me wonder
    if there is something we should be doing to detect when underlying
    C objects get deleted, and remove our own references to them. For
    the present, we should try to detect such instances and clean up as
    best we can. Maybe the rearchitecture will resolve this problem in
    a more satisfactory way.  - wware 051206
    """

    # wware 051206 fixing bug 1070
    def tooltip_nodeItems(self, tooltip):
        """Step through the nodes for this tree, and fill in the QToolTip for
        the ModelTreeItems in the viewport of the QlistView for the tree."""
        _node_items = self._node_items
        for node in _node_items.keys():
            name = node.name
            if len(name) > 12:
                item = _node_items[node]
                try:
                    vp = self.viewport()
                    if not isinstance(vp, QWidget):
                        if debug_flags.atom_debug:
                            # See bug 2113 - this does not appear to be very serious. wware 060727
                            sys.stderr.write("QScrollView.viewport() should return a QWidget (bug 1457)\n")
                            sys.stderr.write("Instead it returned " + repr(vp) + "\n")
                        return
                    # qrect = vp.itemRect(item) ? ?
                    qrect = self.itemRect(item)
                    tooltip.add(vp, qrect, node.name)
                except RuntimeError:
                    qrect = None
                    # underlying C/C++ object has been deleted
                    # item is invalid, remove it from _node_items
                    del _node_items[node]

    # update helpers; will want some revision but this is not urgent I think #e

    def make_new_subtree_for_node(self, node, parent, nodeParent, display_prefs = {}, after = None):
        """Make one or more new treeitems (ModelTreeItems) in this treewidget (a QTreeView),
        as needed to display the given node under the given parent
        (which should be a treeitem or this treewidget).
        The display prefs (in our argument) are the ones from the env supplied by the parent --
        they don't include the ones for this node itself (e.g. whether it's open),
        though (someday) they might include policies for whether or not to honor those.
           Return the toplevel treeitem made (the one corresponding to node).
        ###redoc: MAYBE: Include all kids of node (as if the node was open), whether or not it's actually open.
        [###@@@ that might be changed, but that's how it was in the pre-050109 code.]
        """
        # This replaces the pre-050109 Node.upMT and Group.upMT, as well as the buildNode methods they called.
        ## display_prefs = {} ###@@@ get from caller; includes 'open' ###@@@ as temp kluge, set node.open here??
        # modify display_prefs for this node, and for kids (separately!).
        item_prefs = dict(display_prefs)
        item_prefs.update( self.display_prefs_for_node(node) ) # incls. whether node should be open in this view
        item_prefs['open'] = True ###@@@ imitate the old code - include all the kids
        kid_prefs = dict(display_prefs)
        kid_prefs.update( self.display_prefs_for_kids_of(node) ) # as of 050109, does nothing, but that might change soon
        item = self.make_new_item_for_node(node, parent, nodeParent, item_prefs, after)
        self.set_nodeItem(node, item) ## node.tritem = item
        kids = node.kids(item_prefs)
        lastkid = None
        for kid in kids: ###@@@ also gaps for dnd -- but only later when we translate this to a canvas
            kiditem = self.make_new_subtree_for_node( kid, item, item, kid_prefs, after = lastkid)
            # kiditem.setParent(item)
            lastkid = kiditem
            del kiditem
            ###@@@ what about dnd here?? was it grabbed from each node or passed from toplevel upMT call?
            ## kid.upMT(item, dnd)
        return item

    ###@@@ I think existing code would not rebuild tree except when expand/collapse;
    # eg would not do it just when sel changed. notsure. at least that must be why it has separate setProp.

    # bruce 050108 moved this back into mtree (from the Node.buildNode methods)
    ###@@@ qt doc explains why it comes in wrong order, and tells how to fix it
    def make_new_item_for_node(self, node, parent, nodeParent, display_prefs = {}, after = None):
        """build and return a single new tree item in this tree widget
        (as part of building the entire tree from scratch, or maybe an entire subtree)
        corresponding to node; the args are:
        self, this tree widget; not sure if this was avail to the orig buildnode -- maybe as one of the other args?
        node, the node
        parent, can be another tree item (ModelTreeItem) or the tree widget itself (a QTreeView)
        icon - the icon to use for this node
        dnd - whether to enable drag and drop (not sure which part of it this is about)
        rename - whether to enable in-place editing of the name
        some of these args might be replaced by computations we do here or in sole caller ###@@@ do it all
        ####@@@redoc below
        after - None, or another listview item we come after
        .. .must add to nodes: options to specify dnd, rename, icon(openness).
        NOTE: it does not add in the kids! that must be done by upMT. and only if the item should be open.
        """
        item = ModelTreeItem(node.name, nodeParent, node)
        nodeParent.appendChild(item)
        item.display_prefs = display_prefs # needed when we update the icon
        item.setIcon(QIcon(node.node_icon(display_prefs))) ###@@@ and/or, update the icon directly when we open/close?
        qt4todo('item.setRenameEnabled(0, node.rename_enabled()) ###k what is the 0 arg?')
        return item

    def update_item_icon(self, item): ###@@@ should also use this in some other methods, i think
        node = item.object
        display_prefs = dict(item.display_prefs) # make a copy to hold local changes
        display_prefs.update( self.display_prefs_for_node(node) ) # patches in current 'open' pref
        icon = node.node_icon( display_prefs)
        item.setIcon(icon) # 0 is the column the pixmap is in
            # Qt doc doesn't say whether this repaints or updates or neither,
            # but something seems to make it look right after this

# everything after this: new methods by bruce 050108-050110, many temporary,
# as I tease apart mtree and Utility to have a clean boundary ###@@@

    ###@@@@ the following should be rewritten to scan item tree, not node tree...
        # then maybe it would not matter if item.parent ~= node.dad.
        # so it'd work for viewdata nodes even if we don't make that correspondence strict.

    def update_open_selected_in_itemtree(self, item, do_setOpen = True, do_invisible_nodes = True):
        ###@@@ change to also update text, icon? anything but structure... rename??
        ###@@@ this implem is temporary and wrong:
        self.update_items_from_nodes_open_selected(item.object, do_setOpen = do_setOpen, do_invisible_nodes = do_invisible_nodes)

    def update_items_from_nodes_open_selected(self, node, _guard_ = None, do_setOpen = True, do_invisible_nodes = True):
        # bruce 050110 temporary; deprecated, only call from above method and not for long! ###@@@
        """set the properties in the model tree widget to match
        those in the tree datastructure #redoc
        """
        assert _guard_ is None # this makes sure we don't supply too many positional arguments!
        # bruce 050110 made this from the old Node.setProp and Group.setProp methods,
        # deprecated now (removed asap).
        # this will pull them into this file;
        # later worry about making them item-centric not node-centric...
        # and about fixing them to use methods on items not in tw, so sel works better.
        # btw what about viewdata members (kids but not members, might not be reached here)?
        #  is it moot? ignore for now. or ask node for all members for this use... ie all possible kids, kids_if_open...
        # useful in our treemaker too i guess.
        listview = self
        item = self.nodeItem(node)
        #bruce 050512 re bug 620: it can happen that item is None because node is newly made
        # since the last time the MT was fully updated. To fix comment#0 of that bug, check for this.
        # For details of how that can happen, see my comments in that bug report. Roughly, if you click
        # in MT while waiting for a long op to finish which at the end needs to remake MT and does so by
        # calling mt_update, it happens because Qt first processes our click, then the mt update event.
        # [#e One better fix might be to remake the MT at the end of the user event that messed up the nodes it shows.
        # Then this would happen before the click was processed so it'd be up to date... we might still want to
        # detect this and discard that click in case it was on the wrong item. Anyway that's all NIM for now.
        # Another fix would be to scan the item-tree here (as last made from a node-tree), not the new node-tree. #e]
        if not item:
            if debug_flags.atom_debug:
                print "atom_debug: fyi: MT node with no item (still waiting for MT.update Qt event?)"
            return
        # bruce 050512 continues: Worse, it can happen that item is no longer valid -- the first time we call a method on it,
        # we get an exception from PyQt "RuntimeError: underlying C/C++ object has been deleted". My bug 620 comments give
        # details on that as well. Let's check this here with a harmless method and get it over with:
        try:
            item.text(0) # returns text in column 0
        except:
            if debug_flags.atom_debug:
                print "atom_debug: fyi: MT node with invalid item (still waiting for MT.update Qt event?)"
            return
        # Now it should be safe to use item.
        if do_setOpen:
            if node.openable(): ###e needs cleanup: use node_isOpen/isOpenable split from current item_ methods
                self.expandItem(item)
        qt4todo('item.repaint()')
        self.repaint()
        if hasattr(node, 'members'): # clean this up... won't be enough for PartGroup! ###@@@
            if not do_invisible_nodes:
                # if the members are not visible now, don't update them now (optim, I guess)
                if not (node.openable() and getattr(node,'open',False)):
                    return
            for kid in node.members: ###@@@ for viewdata guys, use kids_if_open
                self.update_items_from_nodes_open_selected(kid, do_setOpen = do_setOpen)
        return

    pass # end of class TreeView

# end
