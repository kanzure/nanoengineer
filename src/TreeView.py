# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
TreeView.py -- display and update, for a tree widget based on QListView,
and meant to display Nodes (with interface and semantics as in Utility.py).

Assumes each node is shown in at most one place in the widget.
This could in theory be changed (see code for details).

[temporarily owned by Bruce, circa 050107, until further notice]

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

###@@@ some of these imports are only needed by subclasses
from qt import *
from constants import *
from chem import *
from gadgets import *
from Utility import *
from selectMode import selectMode
import sys, os, time

from platform import fix_buttons_helper
from widgets import makemenu_helper
from debug import DebugMenuMixin

# from somewhere import noop
def noop(*args,**kws): pass

class TreeView(QListView):
    needs_update_state = 0
    initialized = 0 ####@@@@ review use of this here vs in subclasses
    def __init__(self, parent, win, name = None, columns = ["node tree"]): ###@@@ review all init args & instvars, here vs subclasses
        """Create a TreeView (superclasses include QListView, QScrollView, QWidget).
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
        self.win = win
        self._node_items = {}
        QListView.__init__(self,parent,name) ###@@@ would any wflags be appropriate?

        # try doing these first, but if that fails, do them after columns are made [as before]:
        self.setSorting(-1)
        self.setRootIsDecorated(1)
        self.setShowSortIndicator(0) # [this used to be done after setResizePolicy]

        self.columns = columns
        for column in columns:
            assert type(column) == type("")
            self.addColumn(column)
        
        ## self.addColumn("col2") # experiment - worked, but resulted in unwanted
        ## # sort indicator in col2 (with redraw bugs) [see QHeader in Qt docs?]
        ## ... might work better if done after we've turned off sorting.
        
        self.header().setClickEnabled(0, self.header().count() - 1) #k what's this?
          # Qt doc says it's turning off the clicked signal for clicks in a certain
          # section header (which one? I don't know if count() is 1 or 2 for our one column.)

        # [some of the following might belong in a subclass or need to be influenced by one:]
        self.setGeometry(QRect(0, 0, 200, 560))
        self.setSizePolicy(QSizePolicy(0,7,0,244,False)) #k what's this?
        self.setResizePolicy(QScrollView.Manual) #k what's this? The Qt doc is pretty obscure.
            # I tried removing it, and noticed no change; in particular, the bug of a resize
            # which makes top toolbar dock taller hiding the mtree label remains.
            # So I put it back for now. [bruce 050110] [see also updateGeometry below]
            # [note - that bug was fixed later; see comments near QPainter.]
            # [see also self.setSelectionMode, below -- unrelated, but I once saw this and
            #  thought it was that, but with the wrong comment.]

        # Selection mode -- what rules should the QListView enforce?
        # (This is retained in the display-only superclass since it seems to affect
        #  what set of items can be shown selected at one time.)
        self.setSelectionMode(QListView.Multi)
        
        # The doc for QListViewItem claims that item.setSelected bypasses those
        # rules -- but tests seem to show it's lying, so we still have to choose
        # rules consistent with what we want to do. The pre-050109 code set this
        # to QListView.Extended; changing it to QListView.Multi seemed to make it
        # better (less interference by Qt with our own sel rules), whereas
        # QListView.NoSelection didn't work at all (no sel shown on items even
        # after item.setSelected and repaint). But to make it
        # fully ok required intercepting all mouse events before QListView sees
        # them, so it would never second-guess us about selection (or anything
        # else). [bruce 050112]
        #older bruce devel-scratch comments:
        ####@@@@ find out whether it's being updated but not drawn, or what or what.... since our code knows...
        ####@@@@ note that select (click handler) is not updating, so what *is* it doing, in all?
        ## self.setSelectionMode(QListView.Extended)
        ###@@@ note that Qt defines semantics for this different from ours....

        self.setShowToolTips(True)
            # bruce 050109 added this; but it doesn't seem to work

        ###@@@ where is item.setExpandable? implicit??

        # this is not safe to do here -- subclasses need to do it themselves!
        # if they forget, the symptom might be that no updates seem to happen.
        ## self.initialized = 1
        ## self.mt_update()

        return # from TreeView.__init__

    # invalidation function for use by external code
    # (and by some internal code in subclasses)
    
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
        self.needs_update_state = 1 # we'll respond to this in our custom method during the next paintEvent
        if not self.isUpdatesEnabled():
            if platform.atom_debug:
                print_compact_stack("atom_debug: stack in mt_update when not isUpdatesEnabled: ")
        ###k I don't know if triggerUpdate is needed [050113]
        self.triggerUpdate() # this is a QListView method... does it also call update? not sure, so call that too:
        self.update()

    # debugging functions
    
    def bruce_print_node(self, node, indent=""): ###@@@ debugging
        print indent + "a node %r:" % node, node.name, node.__class__.__name__,"dad =",node.dad
        if not self.nodeItem(node): ## node.tritem
            print indent + "... has no tree item"
        else:
            print indent + "its tree item:"
            self.bruce_print_item(self.nodeItem(node), "  "+indent)
        return
    
    def bruce_print_item(self, item, indent=""): ###@@@ debugging
        print indent + "an item %r for:" % item, item.object.name, item.object.__class__.__name__
        if item == self.shelf: print indent + " (mt.shelf)"
        if item == self.tree: print indent + " (mt.tree)"
        if item.object.name == self.assy.name:
            print indent + " (part item, i guess: item.object.name == self.assy.name)"
        dad = item.object.dad
        if dad:
            dadlen = len(dad.members)
            ind = dad.members.index(item.object)
            print indent + " its dad node (member index %d out of index range 0 to %d-1):" % (ind, dadlen)
            self.bruce_print_node(dad, "| "+indent)
        else:
            print indent + " (dad is %r)" % (dad,)
        return

    _last_dprinttime_stamp = None
    def dprinttime(self):
        "call this to print a timestamp before every debug line for which the same time was never before printed"
        if not platform.atom_debug: return
        import time
        stamp = time.asctime() #e improve
        if stamp != self._last_dprinttime_stamp:
            print
            print stamp
        self._last_dprinttime_stamp = stamp
        return

    def dprint(self, msg):
        if platform.atom_debug:
            self.dprinttime()
            print msg
        return

    # update-related functions, and related event-processing
    # (not user input events -- those should be defined in subclasses)
    # (###@@@ #e though we might want to override them here to mask QListView from seeing them -- but maybe no need)
    
    def update(self):
        if platform.atom_debug:
            self.dprinttime()
            ##print "fyi: modelTree.update() called (by Qt, or by a bug in our own code, which should call mt.mt_update; or by our new code)"
            print_compact_stack("stack in update(): ")
            ## this happens twice early, not from exec_loop:
            # stack in update(): [atom.py:75] [MWsemantics.py:119] [modelTree.py:115] [modelTree.py:125] [modelTree.py:349]
            ## and once after history file started but before first paintEvent:
            # stack in update(): [atom.py:75] [MWsemantics.py:175] [MWsemantics.py:260] [modelTree.py:125] [modelTree.py:349]
            # The funcs are: 349 = this method, 125 = mt_update, 115 = end of our __init__, atom75 = "foo = MWsemantics()",
            #  and in 2nd time, MWsem's mt_update inside win_update. All reasonable. Does it happen more after that? It better! ###@@@
        return QListView.update(self)

    def updateContents(self):
        if platform.atom_debug:
            self.dprinttime()
            print "fyi: modelTree.updateContents() called (by Qt, maybe by triggerUpdate)"
            print_compact_stack("stack in updateContents(): ")
        return QListView.updateContents(self)

    def resize(self): #k does this get called? no.
        if platform.atom_debug:
            self.dprinttime()
            print "fyi: modelTree.resize() called (by Qt, presumably)"
            print_compact_stack("stack in resize(): ")
        return QListView.resize(self)

    def resizeEvent(self, event): #k does this get called? yes.
        # maybe it needs to do updateContents to avoid a bug
        # when window's top toolbar dock gets taller, covering the top of mtree...
        # or is there some other func to call then? and will this one even get called then?
        if platform.atom_debug:
            self.dprinttime()
            ## print "fyi: modelTree.resizeEvent() called (by Qt, presumably)"
            print_compact_stack("stack in resizeEvent(e): ")
        self.updateGeometry() #k does this help with bug of grown tooldock hiding mtree label? no, no effect.
        self.update() #k, ok, does this help? no. it looks like it only redraws where (and if) it think's it's needed. and is wrong.
        # ok let's really bludgeon it, see if this helps even tho i't more than i want to change:
        self.setContentsPos(0,0)# no, this too did not fix it.
        self.repaint() # this is doc'd to actually erase and repaint whole thing ... wait, before i try, do i need to
        # first let the listview see this event? in theory, no... so try w/o that, then with it and with less done.
        # resultS: no effect. things to try: give a rect, change wflags for scrollview, do it after native resize event.
        ## self.repaint(0,0,100,100) - typeerror, oh that was my own custom method's bug, fixed now, anyway nevermind
        ##self.repaint(0,0,100,100,True) # True is erase flag

        self.dprint("QListView.resizeEvent being called")
        res = QListView.resizeEvent(self, event)
        self.dprint("QListView.resizeEvent(self, event) res is %r" % res)

        ###@@@@ so maybe one of these things, done after as well as before, will help...
        self.updateGeometry()
        self.update()
        self.setContentsPos(0,0)
        self.repaint()
        ##self.repaint(0,0,100,100,True)
        self.triggerUpdate() #k
        # well, if i do all that (starting with the specific rect repaint above),
        # then it makes a difference: the mtree content area gets repainted - but not the mtree label at the top.
        # let's try seeing if the paintevent below contains region info... ####@@@@
        return res

    def repaint(self, *args):
        if platform.atom_debug:
            self.dprinttime()
            print "fyi: modelTree.repaint() called (by Qt, presumably)"
            print_compact_stack("stack in repaint(): ")
        return QListView.repaint(self, *args)

    ###@@@ move this? for eventual use, into a subclass, but for debug use, keep a copy here...
    def drawbluething(self, painter, pos = (0,0), color = Qt.blue): # bruce 050110 taken from my local canvas_b2.py
        return ########@@@@@@@@@@
        p = painter # caller should have called begin on the widget, assuming that works
        p.setPen(QPen(color, 3)) # 3 is pen thickness
        w,h = 100,9
        x,y = pos
        p.drawEllipse(x,y,h,h)
        fudge_up = 1 # 1 for h = 9, 2 for h = 10
        p.drawLine(x+h, y+h/2 - fudge_up, x+w, y+h/2 - fudge_up)
        
    def viewportPaintEvent(self, event):
        # making this do nothing does prevent most of mtree from being drawn, but:
        # - doesn't prevent its top column label from being drawn
        # - doesn't prevent regular PaintEvent from happening.
        # so let's try some drawing in here... then try to decode that warning from QPainter about begin().
        # and look up how to get the real painter... also look up the clipper... and find out what draws that mtree label...
        # or consider postponing all this, since i do have access to mtree content drawing now, and that's more important for now.
        # and maybe i could just turn off the label and draw my own!
        self.dprint("viewportPaintEvent, maybe this one needs to call update_state, if called first?") ####@@@@ this might fix it all
        if platform.atom_debug:
            print_compact_stack("stack in viewportPaintEvent(e): ")

        self.update_state_iff_needed(event) ####@@@@ this might fix the update bug after the menuitem to make a group!

        if 1:
            res = QListView.viewportPaintEvent(self, event)
        painter = QPainter(self, True)#True=unclipped, works, it shows up over the mtree label...
            ####@@@@ if this is what fixes the redraw bugs, should i do it before the super call not after?
        self.dprint("viewportPaintEvent super done, and QPainter after it done")
##        self.drawbluething(painter, (0,0), color = Qt.red)
##        self.drawbluething(painter, (80,130), color = Qt.green)
        return res
    
    ## def viewportResizeEvent(self, event):pass
        
    def paintEvent(self, event):
        # this is the only one that gets called, out of update, repaint, paintEvent, contentsPaintEvent
        if platform.atom_debug:
            self.dprinttime()
            ##print "fyi: modelTree.paintEvent() called (by Qt, presumably), event = %r" % event
            print_compact_stack("stack in PaintEvent(e): ") # just shows app.exec_loop and this method
##            print "event.rect(), event.erased():",event.rect().coords(), event.erased()
            # this shows a rect starting at 0,0... but where is that?
            # let's paint there and see what happens... 
            # besides that will be useful to know how to do later, for D&D into the gaps.
            # DO THIS BELOW so it's after the main painting we do.
            
            # also: find the clipper and its coords right now. ####@@@@

        ## self.update_state_iff_needed(event)
        
        ##res = QListView.paintEvent(self, event) -- removing this doesn't prevent mtree from being drawn!!!! * * * * 
        res=None
        # now draw our own thing on top...
        # so: find the viewport and painter, ... ####@@@@
##        self.dprint("super paintEv done, now blue")
        ####@@@@ i don't know *which* painter is fixing the update bugs, btw, this one or the viewportPaintEvent one.
        painter = QPainter(self, True) # this works (so does one from viewportPaintEvent, it's random which is left on screen)
            # but: it's obscured by model tree label (i only see the part in the highlight border area)
            # , and, it's clipped so i don't see it in mtree area either. Hmm, try no clipping, True arg2 to QPainter. works.
##        self.drawbluething(painter, (0,0)) # draws nothing, but says "QPainter::setPen: Will be reset by begin()"
##        self.drawbluething(painter, (100,120))
        return res

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
            pass

    def contentsPaintEvent(self, event): #k don't know if this exists; but viewportPaintEvent does, i think
        if platform.atom_debug:
            self.dprinttime()
            print "fyi: modelTree.contentsPaintEvent(e) called (by Qt, presumably), event = %r" % event
            print_compact_stack("stack in contentsPaintEvent(e): ")
        return QListView.contentsPaintEvent(self, event)

    ###@@@ move this comment down below:
    # main tree-remaking function (runs more often than it would need to in a more incremental implem)

    # bruce 050107 renamed this 'update' -> 'mt_update';
    # then bruce 050110 renamed it 'update_state' and made it
    # no longer public, but called inside paintEvent(?)
    # when mt_update records the need for this

    def update_state(self, paintevent):
        """[private]
        Rebuild the tree of QListViewItems. Details in update_state_0 docstring.
        [no longer named update, since that conflicts with QWidget.update]
        """
        # Qt doc makes it clear (well, at least deducible)
        # that disabling updates is not redundant here,
        # and it says other things which lead me to guess
        # that it might avoid infrecur from repaint by QListView,
        # and even if not, might reduce screen flicker or other problems.
        old_UpdatesEnabled = self.isUpdatesEnabled()
        if not old_UpdatesEnabled:
            self.dprint( "atom_debug: not old_UpdatesEnabled") # error?
        self.setUpdatesEnabled( False)
        try:
            self.update_state_0( paintevent)
        finally:
            self.setUpdatesEnabled( old_UpdatesEnabled)
            self.update() #####@@@@@ might cause infrepeat... try it anyway
        #e should be no need to do an update right here, since we're only
        # called when a repaint is about to happen! But an updateContents
        # might be good, here or in the sole caller or grandcaller. ###@@@
        return

    def update_state_0( self, paintevent):
        """[private]
        Build or rebuild a new tree of QListViewItems in this widget
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
        self.scrollpos = self.viewportToContents(0,0)

        self.clear() # this destroys all our QListViewItems!
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

        lastitem = None ####@@@@ got to about here
        for node in self.topnodes:
            item = self.make_new_subtree_for_node( node, listview, after = lastitem)
            lastitem = item
            self.topitems.append(item)
        
##        self.tree = self.make_new_subtree_for_node( self.assy.tree, listview)
##        self.shelf = self.make_new_subtree_for_node( self.assy.shelf, listview, after = self.tree)

        # Update open/highlighted state of all tree items [text, icon already done above]
        ###@@@ code copied below - merge?

        for item in self.topitems:
            self.update_open_selected_in_itemtree( item)

##        ###obs, handle by scanning items not nodes (store kidlist on items??):
##        ###@@@ following might be unsafe -- so instead, fix above func to use all kids:
##        ## self.update_items_from_nodes_open_selected( self.assy.data)

        self.post_update_topitems() # let subclass know about new self.topitems
        
        # set the scroll position to what it ought to be
        # [bruce circa 050113. Fixes bug 177.]
        x, y = self.scrollpos
        self.setContentsPos( x, y)
            ###@@@ not yet perfect, since we need to correct height
            # to be larger than needed for all items, when collapsing a group
            # which went below the visible area, so the group doesn't move on
            # screen due to QListView not liking empty space below the items.
        
        ## a note about why ensureItemVisible is not useful [bruce circa 050109]: 
        ##self.ensureItemVisible(self.last_selected_node.tritem)
        ## this "works", but it looks pretty bad:
        ## - there's a lot of flickering, incl of the scrollbar (disabling updates might fix that)
        ## - it always puts this item at the very bottom, for the ones that would otherwise be off the bottom
        ## - even if this item is already visible near the top, it moves stuff, perhaps as if trying to center it.

        return # from update_state_0

    def get_topnodes(self):
        "[subclasses must override this to tell us what nodes to actually show]"
        return [] ###e a better stub/testing value might be a comment node, if there is such a node class
    
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
        if node.openable():
            res['openable'] = True ###@@@??? see setExpandable; and discussion in QListViewItem docs, esp about setup() function
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
        """Return the QListViewItem currently representing Node (in self)
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
        terms of real QListViewItems, then we might end up needing to use
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

    # update helpers; will want some revision but this is not urgent I think #e
    
    def make_new_subtree_for_node(self, node, parent, display_prefs = {}, after = None):
        """Make one or more new treeitems (QListViewItems) in this treewidget (a QListView),
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
        item = self.make_new_item_for_node(node, parent, item_prefs, after)
        self.set_nodeItem(node, item) ## node.tritem = item
        kids = node.kids(item_prefs)
        lastkid = None
        for kid in kids: ###@@@ also gaps for dnd -- but only later when we translate this to a canvas
            kiditem = self.make_new_subtree_for_node( kid, item, kid_prefs, after = lastkid)
            lastkid = kiditem
            del kiditem
            ###@@@ what about dnd here?? was it grabbed from each node or passed from toplevel upMT call?
            ## kid.upMT(item, dnd)
        return item

    ###@@@ I think existing code would not rebuild tree except when expand/collapse;
    # eg would not do it just when sel changed. notsure. at least that must be why it has separate setProp.

    # bruce 050108 moved this back into mtree (from the Node.buildNode methods)
    ###@@@ qt doc explains why it comes in wrong order, and tells how to fix it
    def make_new_item_for_node(self, node, parent, display_prefs = {}, after = None):
        """build and return a single new tree item in this tree widget
        (as part of building the entire tree from scratch, or maybe an entire subtree)
        corresponding to node; the args are:
        self, this tree widget; not sure if this was avail to the orig buildnode -- maybe as one of the other args?
        node, the node
        parent, can be another tree item (QListViewItem) or the tree widget itself (a QListView)
        icon - the icon to use for this node
        dnd - whether to enable drag and drop (not sure which part of it this is about)
        rename - whether to enable in-place editing of the name
        some of these args might be replaced by computations we do here or in sole caller ###@@@ do it all
        ####@@@redoc below
        .. .must add to nodes: options to specify dnd, rename, icon(openness).
        NOTE: it does not add in the kids! that must be done by upMT. and only if the item should be open.
        """
        if after: # this 'if' is required!
            try:
                item = QListViewItem(parent, after) # comes first... unless after is passed
                item.setText(0, node.name) # 0 is column number; there is no initializer with both after and text
            except:
                # only happens on a bug we can't handle, so always print something
                print "fyi: bug in after option, this is its value:",after ###@@@
                raise
        else:
            item = QListViewItem(parent, node.name)
            ###@@@ revise interface, pass the node, do this function in that init method, don't need this func at all, perhaps.
        item.object = node ###@@@ probably still ok to store it like this
        ###@@@ store node.tritem = item here, but in a new way? no, do it in caller.
        ## open = node.open ###@@@temporary [wrong, too -- not defined on leaf nodes]
        ## done in subr: open = display_prefs.get('open',False) ###e better this way, or direct from self.display_prefs_for_node??
        item.display_prefs = display_prefs # needed when we update the icon
        item.setPixmap(0, node.node_icon( display_prefs)) ###@@@ and/or, update the icon directly when we open/close?
        item.setDragEnabled(node.drag_enabled()) ###@@@ does this need to inherit from higher in nodetree?
            # if so, add that later (decision might be revised anyway, vs old code)
            # (but do figure out what old code did!)
            # do it via dad if in nodes, or via display prefs here if in tree, or both (anding them).
            # if we update items later then we also need to store their item parent here, or rely on this matching node.dad
            # which is questionable esp at top of tree.
        item.setDropEnabled(node.drop_enabled())
        item.setRenameEnabled(0, node.rename_enabled()) ###k what is the 0 arg?
        ###@@@ also setProp even if that is also done separately; ###@@@ should that also do the icon? and even the other props here?
        # e.g. (someday) drop property might vary depending on open or not...
        return item

    def toggle_open(self, item, openflag = None):
        """Toggle the open/closed state of this item, or set it to openflag
        if that's supplied. Do all necessary invals or repaints, including
        creation of new child items if needed.
        (Error if item is not openable; this may or may not be checked here.)
        """
        node = item.object
        try:
            open = node.open #e self.isOpen(node)?
        except AttributeError:
            open = False # or could mean node is not openable! nevermind for now
        if openflag == None:
            # toggle open/closed state
            open = not open
            # fall thru
        else:
            # set to specified state (and update, whether or not state was same before)
            ### canonicalize boolean values before comparing them
            ##openflag = not not openflag 
            ##open = not not open
            ##if open == openflag: return
            open = openflag
        # open (local var) is now what we want, maybe not what we have.
        node.open = open # self.setNodeOpen(node, open)? would that do inval/repaint itself?
        
        #e after this, needs review or cleanup:
        # fix the icon before calling the general updater func (which does not call the needed setPixmap)
        # ... the old code (or my mods to it?) was assuming that we only needed this
        # on the very same nodes we clicked on (no .open chgs of hidden ones by code):
        # ####@@@@ i am not yet doing in to the kids, just see if it works at this level
        self.update_item_icon(item)
        # 0. open the tree item (setOpen, setSelected, and repaint that item -- HMM this also repaints newly opened kids...####@@@@
        self.update_open_selected_in_itemtree( item, do_invisible_nodes = False) ###k flag correct?? ###@@@
        # 1. call update - even though the above repainted the indiv node and i guess the newly opened kids -
        # since that repaint was not enough to shift down the guys that come after our kids!
        # note we did not set the state-inval flag so the eventual full repaint will not call update_state.
        self.update()
        # 2. review what my current code does when it happens... looks ok unless the update_state (not used here) is too late.
        return

    def update_item_icon(self, item): ###@@@ should also use this in some other methods, i think
        node = item.object
        display_prefs = dict(item.display_prefs) # make a copy to hold local changes
        display_prefs.update( self.display_prefs_for_node(node) ) # patches in current 'open' pref
        icon = node.node_icon( display_prefs)
        item.setPixmap(0, icon) # 0 is the column the pixmap is in
            # Qt doc doesn't say whether this repaints or updates or neither,
            # but something seems to make it look right after this

# everything after this: new methods by bruce 050108-050110, many temporary,
# as I tease apart mtree and Utility to have a clean boundary ###@@@
    
    ###@@@@ the following should be rewritten to scan item tree, not node tree...
        # then maybe it would not matter if item.parent ~= node.dad.
        # so it'd work for data nodes even if we don't make that correspondence strict.
        
    def update_open_selected_in_itemtree(self, item, do_setOpen = True, do_invisible_nodes = True):
        ###@@@ change to also update text, icon? anything but structure... rename??
        ###@@@ this implem is temporary and wrong:
        self.update_items_from_nodes_open_selected(self, item.object, do_setOpen = do_setOpen, do_invisible_nodes = do_invisible_nodes)
        
    def update_items_from_nodes_open_selected(self, node, do_setOpen = True, do_invisible_nodes = True):
        # bruce 050110 temporary; deprecated, only call from above method and not for long! ###@@@
        """set the properties in the model tree widget to match
        those in the tree datastructure #redoc
        """
        # bruce 050110 made this from the old Node.setProp and Group.setProp methods,
        # deprecated now (removed asap).
        # this will pull them into this file;
        # later worry about making them item-centric not node-centric...
        # and about fixing them to use methods on items not in tw, so sel works better.
        # btw what about data members (kids but not members, might not be reached here)?
        #  is it moot? ignore for now. or ask node for all members for this use... ie all possible kids, kids_if_open...
        # useful in our treemaker too i guess.
        tw = self # tw means tree widget, i guess [taken from old code]
        item = self.nodeItem(node)
        assert item
        if do_setOpen and node.openable():
            tw.setOpen(item, node.open) ###@@@ use a new method in place of open... if we even need this...
        ## old: tw.setSelected(item, node.picked)
        item.setSelected(node.picked)
        item.repaint()
        if hasattr(node, 'members'): # clean this up... won't be enough for PartGroup! ####@@@@
            if not do_invisible_nodes:
                # if the members are not visible now, don't update them now (optim, I guess)
                if not (node.openable() and getattr(node,'open',False)):
                    return
            for kid in node.members: ###@@@ for data guys, use kids_if_open
                self.update_items_from_nodes_open_selected(kid, do_setOpen = do_setOpen)
        return
    
    pass # end of class TreeView

# end
