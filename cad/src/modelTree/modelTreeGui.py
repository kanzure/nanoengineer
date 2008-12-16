# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
modelTreeGui.py - provide a Qt4-compatible Model Tree widget,
inherited by modelTree.py to provide NE1's Model Tree of Nodes.

@author: Will, Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

Goals (of Will's refactoring, as part of the Qt3 -> Qt4 port):

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

Update 070612: I [bruce] did a major rewrite to fix scrollbar bugs (circa May 07), mentioned in
comments below, before A9 release, using QScrollArea instead of QTreeView. Now I am removing the
obsolete code which used QTreeView, but some comments still refer to its classes. What's being
removed includes the classes:

  class _our_QItemDelegate(QItemDelegate): # removed
  class _our_TreeItem: # removed
  class _QtTreeModel(QAbstractItemModel): # removed
  class ModelTreeGui_QTreeView(QTreeView, ModelTreeGui_common): # removed

late 2007 and/or early 2008: Mark and Bruce implemented atom content indicators,
though some bugs remain

080507: Bruce partly implemented GLPane -> MT cross-highlighting

TODO:

This module is too long, and includes api classes for other modules,
so it needs to be split into several files.
"""

import sys
import time

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.Qt import Qt
from PyQt4.Qt import QTreeView
from PyQt4.Qt import QScrollArea
from PyQt4.Qt import QIcon
from PyQt4.Qt import QDrag
from PyQt4.Qt import QMimeData
from PyQt4.Qt import QPoint
from PyQt4.Qt import QPixmap
from PyQt4.Qt import QPainter
from PyQt4.Qt import QFontMetrics
from PyQt4.Qt import QLineEdit
from PyQt4.Qt import QColor
from PyQt4.Qt import QRect
from PyQt4.Qt import QPalette

from utilities.debug import print_compact_traceback, print_compact_stack
from platform_dependent.PlatformDependent import fix_plurals
from utilities.Log import quote_html
from utilities.debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice
from widgets.menu_helpers import makemenu_helper
import foundation.env as env

from widgets.simple_dialogs import grab_text_line_using_dialog
from utilities.icon_utilities import imagename_to_pixmap

from modelTree.Node_as_MT_DND_Target import Node_as_MT_DND_Target #bruce 071025

from utilities.constants import AC_INVISIBLE, AC_HAS_INDIVIDUAL_DISPLAY_STYLE

from utilities.GlobalPreferences import pref_show_node_color_in_MT

from widgets.widget_helpers import RGBf_to_QColor

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
    """
    API (and some default method implementations) for a Model Tree object.
    """
    def get_topnodes(self):
        """
        Return a list of the top-level nodes, typically assy.tree and assy.shelf for an assembly.
        """
        raise Exception("overload me")

    def get_nodes_to_highlight(self): #bruce 080507
        """
        Return a dictionary of nodes which should be drawn as highlighted right now.
        (The keys are those nodes, and the values are arbitrary.)
        """
        return {}
    
    def make_cmenuspec_for_set(self, nodeset, optflag):
        """
        Return a Menu_spec list (of a format suitable for makemenu_helper)
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
        raise Exception("overload me")

    def get_current_part_topnode(self): #bruce 070509 added this to API ##e rename?
        """
        Return a node guaranteed to contain all selected nodes, and be fast.
        """
        raise Exception("overload me")

    # helper methods -- strictly speaking these are now part of the API, but they have default implems
    # based on more primitive methods (which need never be overridden, and maybe should never be overridden).
    # [moved them into this class from modelTreeGui, bruce 070529]
    
    def recurseOnNodes(self, func, topnode = None,
                       fake_nodes_to_mark_groups = False,
                       visible_only = False ):
        """
        """
        #bruce 070509 new features:
        # - fake_nodes_to_mark_groups [not used as of 080306],
        # - visible_only [always true as of 080306]
        assert visible_only # see above comment
        if topnode is None:
            for topnode in self.get_topnodes():
                self.recurseOnNodes(func, topnode,
                                    fake_nodes_to_mark_groups = fake_nodes_to_mark_groups,
                                    visible_only = visible_only)
                continue
        else:
            func(topnode)
            
            #bruce 080306 use MT_kids, not .members, to fix some bugs
            # (at least the one about lots of extra scroll height when
            #  a large DnaGroup is in the MT). Note, MT_kids is always
            # defined; it's a length 0 sequence on leaf nodes.
            if visible_only:
                if topnode.open and topnode.openable():
                    members = topnode.MT_kids()
                        # note: we're required to not care what MT_kids returns
                        # unless topnode.open and topnode.openable() are true.
                else:
                    members = ()
            else:
                assert 0 # not well defined what this means, due to MT_kids vs members issue [bruce 080306]
            
            if members:
                if fake_nodes_to_mark_groups:
                    func(0)
                for child in members:
                    self.recurseOnNodes(func, child,
                                        fake_nodes_to_mark_groups = fake_nodes_to_mark_groups,
                                        visible_only = visible_only)
                    continue
                if fake_nodes_to_mark_groups:
                    func(1)
            pass
        return
    
    def topmost_selected_nodes(self): # in class Ne1Model_api
        """
        @return: a list of all selected nodes which are not inside selected Groups
        """
        nodes = [self.get_current_part_topnode()]
        from operations.ops_select import topmost_selected_nodes
        return topmost_selected_nodes(nodes)

    def repaint_some_nodes(self, nodes): #bruce 080507, for cross-highlighting
        """
        For each node in nodes, repaint that node, if it was painted the last
        time we repainted self as a whole. (Not an error if it wasn't.)
        """
        raise Exception("overload me")

    pass # end of class Ne1Model_api

class Node_api(Api): # REVIEW: maybe refile this into model/Node_API and inherit from Node?? [bruce 080107 comment]
    """
    The customer must provide a node type that meets this API. This can be done by extending this
    class, or implementing it yourself. [See also class Node in Utility.py, used as the superclass
    for NE1 model tree nodes, which defines an API which is (we hope) a superset of this one.
    This could in principle inherit from this class, and at least ought to define all its methods.]

    In addition to what appears here, a node that has child nodes must maintain them in a list
    called 'self.members'. [that might be WRONG as of 080306, since we now use MT_kids]

    @note: this class is only used (so far, 081212) as documentation and in test code.
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
    # See also my comments in modelTree.__init__.
        
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

class ModelTreeGui_api(Api): 
    """
    This should be a Qt4 widget that can be put into a layout.
    """
    # not private, but only used in this file so far [bruce 080306 comment]
    def update_item_tree(self, unpickEverybody = False): # in ModelTreeGui_api
        """
        Removes and deletes all the items in this list view and triggers an update. Previously
        this was the 'clear' method in Q3ListView. 
        """
        ###REVIEW: in the implementation below, this also creates a new tree of items given a root node.
        # I guess this means the meaning of this method in this API was changed since the above was written.
        # (So has the name -- it was called 'clear' until bruce 070509. Also the option was not listed in this API.)
        raise Exception("overload me")

    def topmost_selected_nodes(self): # in ModelTreeGui_api
        """
        @return: a list of all selected nodes which are not inside selected Groups
        """
        raise Exception("overload me")

    def mt_update(self, nodetree = None): # in ModelTreeGui_api
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

####################### End of the API #############################

#################### Implementation ################################

_ICONSIZE = (22, 22)

ITEM_HEIGHT = _ICONSIZE[1] # in theory, these need not be the same,
    # but other values are untested [bruce 070529 guess]

_cached_icons = {} #bruce 070529 presumed optimization

def _paintnode(node, painter, x, y, widget, option_holder = None):
    """
    Draw node in painter.
    x,y are coords for topleft of type-icon.
    widget (the modelTreeGui) is used for palette.
    @param option_holder: the MT_View, used for dictionary attribute
                          _f_nodes_to_highlight and (in future)
                          for some prefs flags.
    """
    #bruce 070529 split this out
    #bruce 080507 added option_holder
    ### todo: revise appearance of highlighted nodes
    
    ## print "_paintnode",node, painter, x, y, widget
        # x is 20, 40, etc (indent level)
        # y is 0 for the top item, incrs by 22 for other items -- but this varies as we scroll.
    
    # find state of node which determines how we draw it
    selected = node.picked
    disabled = node.is_disabled() ### might be slow!
    display_prefs = display_prefs_for_node(node)
        # someday these might also depend on parent node and/or on ModelTreeGui (i.e. widget)

    text_color = None
    if pref_show_node_color_in_MT():
        # [bruce 080507 new feature, mainly for testing]
        # review: should the modelTree itself (ne1model) test this pref
        # and tell us the text_color for each node?
        ### is this debug_pref test too slow? if it is, so is the debug_pref lower down...
        # could fix using option_holder to know the pref values
        
        # note: this should work for all nodes with a .color attribute,
        # not just chunks, but to work with Groups (including DnaStrand etc)
        # it would need some revisions, e.g. call a new Node method
        # get_node_color_for_MT (which would be a good refactoring anyway)
        text_color = getattr(node, 'color', None) # node.color

    highlighted = option_holder and node in option_holder._f_nodes_to_highlight
        # fyi: for now, this means "highlighted in glpane",
        # but in the future we'll also use it for MT mouseover highlighting
    
    # draw it
    
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

    need_save = disabled or selected or (text_color is not None) or highlighted
        #bruce 070529 presumed optimization (not usually set for most nodes)

    if need_save:
        painter.save()

    if disabled: # before
        # draw icon and label in slanted form
        painter.shear(0, -0.5)
        painter.translate(0.5 * y + 4, 0.0)
            
    painter.drawPixmap(x, y, pixmap)
    
    # Draw a special symbol in the upper right corner of the node icon if one 
    # of the following conditions is true:
    # - draw a small yellow dot if the node contains atoms that have their 
    #   display style set to something other than diDEFAULT.
    # - draw a small white ghost if the node contains invisible or hidden 
    #   chunks and/or atoms.
    # - draw a small yellow ghost if the node contains invisible or hidden
    #   chunks and/or atoms _and_ the node also contains atoms that have their
    #   display style set to something other than diDEFAULT.
    # Mark 2008-03-04
    #
    # revised by bruce 080306, but not yet in final form, or in final place in this file. ###
    # What remains to do (assuming this works so far):
    # - some optimizations in the code for maintaining the node flags this accesses
    # - MT needs to subscribe to changes in this data for nodes it draws (and get mt_update when that changes)
    # - MT needs to include this data in what it compares about a node when deciding if redraw is needed.
    #   Until it does, even an MT click often won't update the MT as needed.
    #   (So to test this as it is so far, modify the model, then save and reopen the file.)
    #
    # Also need to revise behavior. See Qs below. Here are notes about the answers: [080314]
    ##yellow ghost: chunks in groups count (for both indicators)
    ##but hidden whole can coexist with ghost if the ghost is about hidden atoms 
    ## (since unhide of them requires another step)
    ## (and the latter is nim, we'll make bug report)
    
    node_symbols = debug_pref("Model Tree: add content symbols to node icons?",
                                  #bruce 080416 renamed this, special -> content,
                                  # for clarity
                              Choice_boolean_True, #bruce 080307 False -> True
                              non_debug = True, 
                              prefs_key = True #bruce 080307 (safe now)
                            )
    if node_symbols:

        flags = node.get_atom_content(AC_INVISIBLE | AC_HAS_INDIVIDUAL_DISPLAY_STYLE)

        # Hidden nodes get ghosts. [hmm, probably not right ### FIX]
        node_has_invisible_contents = node.hidden

        # NIM: so do nodes with hidden sub-nodes. ##### IMPLEM
        
        # So do nodes which contain invisible (aka hidden) atoms:
        if flags & AC_INVISIBLE:
            node_has_invisible_contents = True

        # Nodes which contain atoms with non-default display styles get yellow dots
        # (or yellow ghosts if they already would have ghosts).
        node_has_special_display_contents = False
        if flags & AC_HAS_INDIVIDUAL_DISPLAY_STYLE:
            node_has_special_display_contents = True

        # What about non-default display styles on chunks? ### DECIDE, FIX

        # Now draw all this.
        if node_has_invisible_contents and node_has_special_display_contents:
            painter.drawPixmap(x, y, 
                               imagename_to_pixmap("modeltree/yellow_ghost.png"))
        elif node_has_invisible_contents:
            painter.drawPixmap(x, y, 
                               imagename_to_pixmap("modeltree/white_ghost.png"))
        elif node_has_special_display_contents:
            painter.drawPixmap(x, y, 
                               imagename_to_pixmap("modeltree/yellow_dot.png"))

    if highlighted:
        background = Qt.yellow # initial test, NOT IDEAL since obscures selectedness ######
    elif selected:
        background = widget.palette().highlight() #k what type is this? QColor or something else?
    else:
        background = None
    
    if background is not None:
        # draw a selection or highlight color as text bg color
        ###BUG: should use color role so it depends on app being in bg or fg
        ###     (like it does for native QTreeView selectedness)
        # (note: this used to be done before drawing the icon, but even then it did not affect the icon.
        #  so it would be ok in either place.)
##        background = painter.background()
##        backgroundMode = painter.backgroundMode()
        painter.setBackground(background)
        painter.setBackgroundMode(Qt.OpaqueMode)

    if text_color is not None:
        painter.setPen(RGBf_to_QColor(text_color))

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
    ##        painter.setPen(QPen(dotcolor, 3)) # 3 is pen thickness;
    ##            # btw, this also sets color of the "moving 1 item"
    ##            # at bottom of DND graphic!
    ##        h = 9
    ##        dx,dy = -38,8 # topleft of what we draw;
    ##            # 0,0 is topleft corner of icon; neg coords work, not sure how far or how safe
    ##        painter.drawEllipse(x + dx, y + dy, h, h)
    ##        painter.restore()
    return

# ==

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

# ==

# Things can be simpler if we admit that display_prefs don't yet depend on the ModelTreeGui object.
# So for now I'm pulling this out of that object, so _our_QItemDelegate.paint can access it without having a pointer to that object.
# I'm also optimizing it, since it'll be called a lot more often now.
# (Even better would be to optimize the node_icon API so we can pass .open directly.
#  We don't want to let the node use its own .open, in case in future we show one node in different MTs.)
# [bruce 070511]

def display_prefs_for_node(node):
    """
    Return a dict of the *incremental* display prefs for the node,
    relative to whatever its parent passes as display prefs for its own MT_kids.
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

class ModelTreeGui_common(ModelTreeGui_api):
    """
    The part of our model tree implementation which is the same
    for either type of Qt widget used to show it.
    """
    # not private, but only used in this file so far [bruce 080306 comment]
    #bruce 070529 split this out of class ModelTreeGui
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
        return
    
    def topmost_selected_nodes(self): # in class ModelTreeGui_common, subclass of ModelTreeGui_api
        """
        @return: a list of all selected nodes which are not inside selected Groups
        """
        #bruce 070529 moved method body into self.ne1model
        #REVIEW: should this be removed from ModelTreeGui_api,
        # always accessed via self.ne1model? Pro: many accesses come
        # from methods in self.ne1model anyway, which also defines it.
        # Con: there are a lot of accesses from methods of self, too.
        # Note that we could make accesses from self.ne1model not
        # depend on this class, without preventing this class from
        # having its own def; in that case, review whether this class's
        # def belongs in its api class or is just a convenience of
        # this implementation. [bruce 081212 comment]
        
        return self.ne1model.topmost_selected_nodes()

    def MT_debug_prints(self):
        return debug_pref("MT debug: debug prints", Choice_boolean_False, prefs_key = True)
    
    def display_prefs_for_node(self, node):
        """
        For doc, see the global function of the same name.
        """
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

    def filter_drag_nodes(self, drag_type, nodes):
        #bruce 070509 copied this from Qt3 TreeWidget.py [#k same as in Qt4 TreeWidget??]
        """
        See which of the given nodes can be dragged (as a group) in the given way.
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
##            msg = "The Part can't be moved"
##                # kluge: this is the only known case! (that I can remember...) #e generalize this
##            self.redmsg(msg)
            #bruce 070509 commented that out, since I think it will often
            # happen by accident for "small move onto self"
            # note: self.redmsg is probably not yet defined
            return None
        return nodes_ok # same as nodes for now, but we might change above code so it's not

    def debug_pref_use_fancy_DND_graphic(self):
        return debug_pref("Model Tree: use fancy DND graphic?",
                          Choice_boolean_True,
                          non_debug = True,
                          prefs_key = True)
    
    def get_pixmap_for_dragging_nodes(self, drag_type, nodes):
        if self.debug_pref_use_fancy_DND_graphic():
            pixmap = self.get_pixmap_for_dragging_nodes_Qt3(drag_type, nodes)
        else:
            # stub version, just the icon from the first node
            display_prefs = self.display_prefs_for_node(nodes[0])
                #bruce 070504 bugfix (partial fix only)
            pixmap = nodes[0].node_icon(display_prefs)
        return pixmap

    def get_whatting_n_items_text(self, drag_type, nodes):
        """
        return something like 'moving 1 item' or 'copying 5 items'
        """
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
    # == [update: I think this is now fully ported and used by default, long before 080507]

    def get_pixmap_for_dragging_nodes_Qt3(self, drag_type, nodes):        
        #e [also put the drag-text-making code in another method near here? or even the dragobj maker?
        # or even the decision of what to do when the motion is large enough (ie let drag_handler role be only to notice that,
        # not to do whatever should be done at that point? as if its role was to filter our events into higher level ones
        # where one of them would be enoughMotionToStartADragEvent?] ###e yes, lots of cleanup is possible here...
        """
        Our current drag_handler can call this to ask us for a nice-looking pixmap
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
        """
        paint one node's item into QPainter p, and translate it down by the item's height
        """
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
        """
        paint a dragobject picture of these nodes into the QPainter p; if you give up, raise an exception; return w,h used??
        """
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
        """
        [private] Do a drop, or raise a DoNotDrop exception.
        Print a message, but do appropriate updates only if we succeed.
        """
        #bruce 070511 brought in several error messages from Qt3/TreeWidget.py,
        # modified some of them, made them use statusbar_msg rather than history
        # redmsg
        item, rectjunk = self.item_and_rect_at_event_pos(event)
        if item is None:
            msg = "drop into empty space ignored (drops under groups " \
                  "not supported; drop onto them instead)"
            self.statusbar_msg( msg)
            raise DoNotDrop()
        nodes, drag_type = self._ongoing_DND_info
        targetnode = item.node
        if targetnode in nodes:
            # don't print a message -- probably common for small mouse motions
            # (thus, don't leave this for drop_on_ok to find)
            # (not verified by test that it *will* find it, though it ought to)
            if DEBUG2:
                print "debug warning: MT DND: targetnode in nodes, refusing drop" # new behavior, bruce 070509
            #e should generalize based on what Qt3 code does [obs cmt?]
            raise DoNotDrop()
        ok, whynot = Node_as_MT_DND_Target(targetnode).drop_on_ok(drag_type, nodes)
        if not ok:
            msg = "drop refused by %s" % quote_html(targetnode.name)
            if whynot:
                msg += ": %s" % (whynot,) #bruce 080303
            self.statusbar_msg( msg )
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

        copiednodes = Node_as_MT_DND_Target(targetnode).drop_on(drag_type, nodes)
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
        msg = "dropped %d item(s) onto %s" % \
              (len(nodes), quote_html(targetnode.name))
            #e should be more specific about what happened to them...
            # ask the target node itself? have drop_on return this info?
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
        """
        called by Qt on mousePress, or by our own method with private option _doubleclick = True
        """

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

        if eventInRect and not contextMenu \
           and not (modifiers & Qt.ShiftModifier) and not (modifiers & Qt.ControlModifier):
            # plain left click --
            # also do direct left click effects for nodes that have any
            # [new feature, bruce 080213]
            assert item.node
            try:
                item.node.ModelTree_plain_left_click
            except AttributeError:
                pass # soon, this should never happen
            else:
                self.mt_update()
                    # kluge (not sure it'll work) -- try to update the MT
                    # at the start, not end, of long-running side effects
                    # in the following method, like animating a view change.
                    # (But we will still do it again below, in case something
                    #  changed during a long op here (this is ok since it
                    #  should be fast if nothing changed).
                item.node.ModelTree_plain_left_click()
            pass
            
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
        menu = makemenu_helper(self, cmenu_spec)
            #bruce 070514 fix bug 2374 and probably others by using makemenu_helper
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
        """
        Return the current scrollposition (as x,y, in scrollbar units), and if DEBUG3 also print it using msg.
        """
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
        """
        Set the scrollposition (as x,y, in scrollbar units), and if DEBUG3 print various warnings if anything looks funny.
        """
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
        """
        [newly in public API -- ###doc that. Used by callers in more than one file.]
        Put up a dialog to let the user rename the given node. (Only one node for now.)
        Emit an appropriate statusbar message, and do necessary updates if successful.
        @see: Node.rename_using_dialog()
        """
        node.rename_using_dialog()
        return

    pass # end of class ModelTreeGui_common

# ==

# newer version of model tree gui which doesn't use QTreeView [bruce 070529] (older one is removed now)

MT_CONTENT_WIDTH = 500 # fixed content width for now

OPENCLOSE_AREA_WIDTH = 20
INDENT_OFFSET = 20
INDENT_0 = 20

MT_CONTENT_TOP_Y = 0

def x_for_indent(n):
    return INDENT_0 + INDENT_OFFSET * n

class MT_View(QtGui.QWidget):
    """
    ModelTree contents view
    """
    def __init__(self, parent, palette_widget, modeltreegui):
        QtGui.QWidget.__init__(self, parent)
        self.palette_widget = palette_widget #e rename?
        self.modeltreegui = modeltreegui
        self.ne1model = self.modeltreegui.ne1model ###KLUGE? not sure. consider passing this directly?        
        self.get_icons()
        return

    def mt_update(self):
        self.modeltreegui.mt_update()
    
    def get_icons(self):
        from utilities.icon_utilities import getpixmap
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

        ### TODO: also get content indicator icons here, ie yellow ghost @@@@
        
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
        """
        [private]
        As an optimization, choose the openclose icons (etc) just once before drawing.
        """
        style = debug_pref("Model Tree: openclose icon style", self._icon_style_choice,
                           non_debug = True, prefs_key = "A9/MT openclose icon style",
                           call_with_new_value = (lambda val: self.mt_update()) )
        if style == 'mac':
            self.collapsed_mtnode_icon = self.mac_collapsed
            self.expanded_mtnode_icon = self.mac_expanded
        else:
            self.collapsed_mtnode_icon = self.win_collapsed
            self.expanded_mtnode_icon = self.win_expanded

        self.draw_openclose_lines = debug_pref("Model Tree: openclose lines", self._openclose_lines_choice,
                           non_debug = True, prefs_key = "A9/MT openclose lines",
                           call_with_new_value = (lambda val: self.mt_update()) )
        return
    
    def sizeHint(self):
        # Note: this probably has no effect, since it's overridden by a resize in every mt_update.
        return QtCore.QSize(MT_CONTENT_WIDTH, 700)

    _painted = None # not {}, so not mutable; after first paintEvent will be a
        # dictionary, which maps node to (x, y) for whatever nodes were painted
        # during the last full repaint [bruce 080507]
    
    def paintEvent(self, event):
        # Note: if this paintEvent was in QAbstractScrollArea, Qt doc for that warns:
        #   Note: If you open a painter, make sure to open it on the viewport().
        # But, it's not in that (or its subclass QScrollArea), it's in the widget we're setting in that.
        # Note: we're painting using contents coords, not viewport coords (and this is working, as expected).
        # Question: would this change cliprect?
        ## painter.setViewport(0, 0, self.width(), self.height())
        if self.modeltreegui.MT_debug_prints():
            print 'paint' # note: this worked once we called update (it didn't require sizeHint to be defined)
        self._setup_full_repaint_variables()
            # needed before _paintnode can use us as its option_holder,
            # and for other reasons
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

    def _setup_full_repaint_variables(self): #bruce 080507 split this out, extended it
        self._setup_openclose_style()
        # todo: optim: implem this: self._setup_prefs(),
        # so _paintnode needn't repeatedly test the same debug_prefs for each node
        self._f_nodes_to_highlight = self.ne1model.get_nodes_to_highlight()
            # a dictionary from node to an arbitrary value;
            # in future, could store highlight color, etc
        self._painted = {} # modified in paint_subtree when we call _paintnode
        return
        
    def paint_subtree(self, node, painter, x, y, line_to_pos = None, last_child = True):
        """
        Paint node and its visible subtree (at x,y in painter);
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
            ## members = node.members
            members = node.MT_kids() #bruce 080306 fix
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
        _paintnode(node, painter, x, y, self.palette_widget, option_holder = self)
        self._painted[node] = (x, y)
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

    def repaint_some_nodes_NOT_YET_USED(self, nodes): #bruce 080507 experimental, for cross-highlighting; maybe not used; rename?
        """
        For each node in nodes, repaint that node, if it was painted the last
        time we repainted self as a whole. (If it wasn't, it might not be an
        error, if it was due to that node being inside a closed group, or to
        a future optim for nodes not visible due to scrolling, or if we're being
        called on a new node before it got painted here the first time; so we
        print no warning unless debug flags are set.)

        Optimization for non-visible nodes (outside scrollarea viewport) is
        permitted, but not implemented as of 080507.

        @warning: this can only legally be called during a paintEvent on self.
                  Otherwise it doesn't paint (but causes no harm, I think)
                  and Qt prints errors to the console. THE INITIAL IMPLEM IN
                  THE CALLERS IGNORES THIS ISSUE AND THEREFORE DOESN'T YET WORK.
                  See code comments for likely fix.
        """
        # See docstring comment about the caller implem not yet working.
        # The fix will probably be for the outer-class methods to queue up the
        # nodes to repaint incrementally, and do the necessary update calls
        # so that a paintEvent can occur, and set enough new flags to make it
        # incremental, so its main effect will just be to call this method.
        # The danger is that other update calls (not via our modelTreeGui's mt_update method)
        # are coming from Qt and need to be non-incremental. (Don't know, should find out.)
        # So an initial fix might just ignore the "incremental" issue
        # except for deferring the mt_update effects themselves
        # (but I'm not sure if those effects are legal inside paintEvent!).
        
        if not self._painted:
            # called too early; not an error
            return
        # (Possible optim: it will often happen that none of the passed nodes
        #  have stored positions. We could check for this first and not bother
        #  to set up the painter in that case. I'm guessing this is not needed.)
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            for node in nodes:
                where = self._painted.get(node) # (x, y) or None
                if where:
                    print "mt debug fyi: repainting %r" % (node,) #### remove when works
                    x, y = where
                    _paintnode(node, painter, x, y, self.palette_widget,
                               option_holder = self)
                else:
                    print "mt debug fyi: NOT repainting %r" % (node,) #### remove when works
                continue
        finally:
            painter.end()
        return

    def any_of_these_nodes_are_painted(self, nodes): #bruce 080507, for cross-highlighting
        """
        @return: whether any of the given nodes were painted during the last
        full repaint of self.

        @rtype: boolean
        """
        if not self._painted:
            # called too early; not an error
            return False
        for node in nodes:
            where = self._painted.get(node) # (x, y) or None
            if where is not None:
                return True
            continue
        return False
    
    def look_for_y(self, y):
        """
        Given y (in contents coordinates), find the node drawn under it,
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
        """
        assuming node is drawn at vertical position y0 (in contents coordinates)
        and indent level d, find the node in its visible subtree (perhaps node itself)
        which is drawn over position y; return (that node, its depth, its y0, None), or (None, None, None, next_y0),
        where next_y0 is the y coordinate for the next node below the given node and its visible subtree.
        Assume without checking that y >= y0.
        """
        y0 += ITEM_HEIGHT
        if y < y0:
            return node, d, y0 - ITEM_HEIGHT, None
        if node.open and node.openable(): #bruce 080108 bugfix for Block: add .openable() check
            d += 1
            for child in node.MT_kids(): #bruce 080108 change for Block: use MT_kids
                     # (but BUG elsewhere, since this is not yet done in drawing code for MT)
                     # [update, bruce 080306 -- so how does e.g. DnaStrand hide its kids?
                     #  I guess it does this by returning False for node.openable(),
                     #  which I guess we do check in enough places, e.g. display_prefs_for_node.
                     #  This means we can effectively notice an MT_kids being empty
                     #  but not one being partial. As of now I think that happens to cover
                     #  the ways we're using it, but clearly this is fragile.]
                resnode, resdepth, resy0, y0 = self.look_for_y_recursive( child, y0, d, y)
                if resnode:
                    return resnode, resdepth, resy0, y0
        return (None, None, None, y0)

    # WARNING: the following methods duplicate some of the code in
    # _our_QItemDelegate in the other MT implem, far above [now removed].
    # Also, they are mostly not yet used (still true, 070612). They might be
    # used to help make in-place node-label-edit work again.
    
    def createEditor(self, node):
        """
        Create and return a QLineEdit child widget to serve as an editor for the given node; initialize its text.
        """
        parent = self
        qle = QLineEdit(parent)
        self.setEditorData(qle, node)
        return qle

    def setEditorData(self, lineEdit, node):
        """
        copy the editable data from node to lineEdit
        """
        value = node.name
        lineEdit.setText(value)
        return

    def setModelData(self, lineEdit, node):
        """
        copy the editable data from lineEdit to node (if permitted); display a statusbar message about the result
        """
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

# ===

class FakeItem:
    def __init__(self, node):
        self.node = node
    def height(self):
        return ITEM_HEIGHT
    pass

class ModelTreeGui(QScrollArea, ModelTreeGui_common):
    """
    The GUI part of the NE1 model tree widget.
    """
    #bruce 070529-30 rewrite of some of [now-removed] class ModelTreeGui_QTreeView
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
        from utilities.prefs_constants import mtColor_prefs_key # In case we want to make it a user pref.
        mtColor = RGBf_to_QColor(env.prefs[mtColor_prefs_key]) 
        from PM.PM_Colors  import getPalette
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
        """
        part of the public API:
        - recompute desired size for scroll area based on visible nodes
        - resize scroll area if needed
        - _do_widget_updates to make sure we get redrawn soon
        """
        if self.MT_debug_prints():
            print "mt_update", time.asctime()

        # probably we need to scan the nodes and decide what needs remaking
        # (on next paintevent) and how tall it is; should we do this in MT_View? yes.
        self.__count = 0
        def func(node):
            self.__count += 1 # using a local var doesn't work, due to Python scoping
        self.ne1model.recurseOnNodes(func, visible_only = True)
        NUMBER_OF_BLANK_ITEMS_AT_BOTTOM = 1
            # not 0, to let user be certain they are at the end
            # [bruce 080306 new feature]
        self.__count += NUMBER_OF_BLANK_ITEMS_AT_BOTTOM
        height = self.__count * ITEM_HEIGHT
        if self.MT_debug_prints():
            print "mt_update: total height", height

##        self._debug_scrollbars("mt_update pre-resize")

        self.view.resize(MT_CONTENT_WIDTH, height)
        #e updateGeometry? guess: this does that itself. I don't know for sure,
        # but the scrollbars do seem to adjust properly.

##        self._debug_scrollbars("mt_update post-resize")

        hsb, vsb = self._scrollbars()
        if vsb:
            vsb.setSingleStep( ITEM_HEIGHT )
            vsb.setPageStep( vsb.pageStep() / ITEM_HEIGHT * ITEM_HEIGHT )
                #k Note: It might be enough to do setSingleStep once during init, since the value seems to stick --
                # but the page step is being quantized, so that has to be redone every time.
                # NFR: I don't know how to set a "motion quantum" which affects user-set positions too.
        
##        self._debug_scrollbars("mt_update post-correct")

        self._do_widget_updates()
        
##        self._debug_scrollbars("mt_update post-update")
        return
    
    def _do_widget_updates(self): #bruce 080507 split this out
        """
        [private]

        Call QWidget.update on our widgets, so that Qt will redraw us soon.
        """
        self.view.update() # this works
        self.update() # this alone doesn't update the contents, but do it anyway
            # to be sure we get the scrollbars (will it be enough?)
        return
    
    def update_item_tree(self, unpickEverybody = False):
        """
        part of the public API
        """
        self.mt_update()

    def paint_item(self, painter, item): # probably only used for DND drag graphic (in superclass)
        x,y = 0,0
        node = item.node
        _paintnode(node, painter, x, y,
                   self.view, # self.view is a widget used for its palette
                   option_holder = None # could be self.view,
                       # but only if we told it to _setup_full_repaint_variables
                  )
        width = 160 ###k guess; should compute in paint and return, or in an aux subr if Qt would not like that
        return width

    def repaint_some_nodes(self, nodes): #bruce 080507, for cross-highlighting
        """
        For each node in nodes, repaint that node, if it was painted the last
        time we repainted self as a whole. (Not an error if it wasn't.)
        """
        # we can't do it this way, since we're not inside paintEvent:
        ## self.view.repaint_some_nodes(nodes)
        if self.view.any_of_these_nodes_are_painted(nodes):
            self._do_widget_updates() # also called by mt_update
        return
    
    def item_and_rect_at_event_pos(self, event):
        """
        Given a mouse event, return the item under it (or None if no item),
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

##def debug_pref_use_old_MT_code(): #bruce 070531 split out, removed non_debug = True, changed name/sense/key/default
##    return debug_pref("MT: use old QTreeView code (next session)?", Choice_boolean_False, prefs_key = True)
##
##if debug_pref_use_old_MT_code():
##    ModelTreeGui = ModelTreeGui_QTreeView


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
#     - drop on group puts node before other members [done, in another file, for NE1 v1.0.0, bruce 080414]
#     - drop-point highlighting, between nodes

# end
