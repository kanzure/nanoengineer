# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
modelTree.py -- The model tree display widget. Inherits from TreeWidget.py.

[temporarily owned by Bruce, circa 050107, until further notice]

$Id$

History: modelTree.py was originally written by some combination of
Huaicai, Josh, and Mark. Bruce (Jan 2005) reorganized its interface with
Node and Group and their subclasses (Utility.py and other modules)
and rewrote a lot of the model-tree code (mainly to fix bugs),
and split it into three modules:
- TreeView.py (display and update),
- TreeWidget.py (event handling, and some conventions suitable for
  all our tree widgets, if we define other ones), and
- modelTree.py (customized for showing a "model tree" per se).
"""

from TreeWidget import * # including class TreeWidget itself, and Node, Group
from chunk import molecule
from gadgets import Jig


# helpers for making context menu commands

class statsclass:
    "class for holding and totalling counts of whatever you want, in named attributes"
    def __getattr__(self, attr):
        if not attr.startswith('_'):
            return 0 # no need to set it
        raise AttributeError, attr
    def __iadd__(self, other):
        """this is self += other"""
        for attr in other.__dict__.keys():
            setattr( self, attr, getattr( self, attr) + getattr( other, attr) )
        return self ###k why would this retval be needed??
            # what could it mean in general for += to return something else?
            # i don't know, but without it,
            # the effect of allstats += somestats is apparently to set allstats to None!
            # I need to check out the python doc for __iadd__. [bruce 050125]
    def __str__(self): # mainly for debugging
        res1 = ""
        keys = self.__dict__.keys()
        keys.sort()
        for attr in keys:
            if res1:
                res1 += ", "
            ###k why was there a global here called res?? or was there? maybe exception got discarded.
            res1 += "%s = %d" % (attr, getattr(self, attr))
        return "<stats (%d attrs): %s>" % (len(keys), res1)
    __repr__ = __str__ #k needed?
    pass

def accumulate_stats(node, stats):
    """When making a context menu from a nodeset (of "topselected nodes"),
    this is run once on every topselected node (note: they are all picked)
    and once on every node under those (whether or not they are picked).
    """
    stats.n += 1

    stats.ngroups += int(isinstance(node,Group))
    stats.nchunks += int(isinstance(node,molecule))
    stats.njigs += int(isinstance(node,Jig))
    #e later, classify(node1, Node) into a list of classes, and get counts for all...

    stats.npicked += int(node.picked)
    stats.nhidden += int(node.hidden)
    stats.nopen += int(node.open)
    return

# main widget class

class modelTree(TreeWidget):
    def __init__(self, parent, win, name = "modelTreeView"):
        """#doc"""
        ###@@@ review all init args & instvars, here vs subclasses
        TreeWidget.__init__(self, parent, win, name, columns = ["Model Tree"]) # stores self.win

        # debug menu and reload command - inited in superclass ###k ok?

        self.assy = win.assy #k needed? btw does any superclass depend on this?? ###@@@

        self.initialized = 1 ###@@@ review where this is done
        self.mt_update() ###@@@ review where done, and name (split it?)
        return
    
##    def _init_menus(self):
##        # Single Item Selected Menu
##        self.singlemenu_spec = ([
##            
##            ["Hide",   self.cm_hide],
##            ["Unhide", self.cm_unhide],
##            None,
##            ["Copy",   self.cm_copy],
##            ["Cut",    self.cm_cut],
##            ["Delete", self.cm_kill],
##            None,
##            ["Properties", self.cm_properties],
##            ])
##
##        # Multiselected Menu
##        self.multimenu_spec = ([
##            
##            ["Group",   self.cm_group],
##            ["Ungroup", self.cm_ungroup],
##            None,
##            ["Hide",   self.cm_hide],
##            ["Unhide", self.cm_unhide],
##            None,
##            ["Copy",   self.cm_copy],
##            ["Cut",    self.cm_cut],
##            ["Delete", self.cm_kill],
##            None,
##            ["Properties", self.cm_properties],
##            ])
##            
##        # Part Node Menu
##        self.partmenu_spec = ([
##            
##            ["Properties", self.cm_properties],
##            ])
##            
##        # Clipboard Menu
##        self.clipboardmenu_spec = ([
##            
##            ["Delete",     self.cm_kill],
##            None,
##            ["Properties", self.cm_properties],
##            ])
##
##        return # from _init_menus

    # callbacks from superclass to help it update the display
    
    def get_topnodes(self):
        self.assy = self.win.assy #k need to save it like this?
        self.assy.tree.name = self.assy.name
            #k is this still desirable, now that we have PartGroup
            # so it's no longer needed for safety?
        kluge_patch_assy_toplevel_groups( self.assy)
            # fixes Group subclasses of assy.shelf and assy.tree,
            # and inserts assy.data.members into assy.tree
        self.tree_node, self.shelf_node = self.assy.tree, self.assy.shelf
        return [self.assy.tree, self.assy.shelf]

    def post_update_topitems(self):
        self.tree_item, self.shelf_item = self.topitems ###k needed??
            # the actual items are different each time this is called

    # special calls from external code
    
    def open_clipboard(self): #bruce 050108, probably temporary
        ## self._open_listitem(self.shelf_item)
        self.toggle_open( self.shelf_item, openflag = True)
    
    # context menus
    
    def make_cmenuspec_for_set(self, nodeset): # [see also the term Menu_spec]
        "#doc... see superclass docstring"

        #e some advice [bruce]: put "display changes" (eg Hide) before "structural changes" (such as Group/Ungroup)...
        #e a context-menu command "duplicate" which produces
        ##a copy of them, with related names and a "sibling" position.
        ##Whereas the menu command called "copy" produces a copy of the selected
        ##things in the system-wide "clipboard" shared by all apps.)

        # I think we might as well remake this every time, for most kinds of menus,
        # so it's easy for it to depend on current state.
        # I really doubt this will be too slow. [bruce 050113]
        
        if not nodeset:
            #e later we'll add useful menu commands for no nodes,
            # i.e. for a "context menu of the background".
            # In fact, we'll probably remove this special case
            # and instead let each menu command decide whether it applies
            # in this case.
            return [('Model Tree (nothing selected)',noop,'disabled')] #e more later

        res = []

        from platform import fix_plurals

        # first put in a Hide item, checked or unchecked. But what if the hidden-state is mixed?
        # then there is a need for two menu commands! Or, use the command twice, fully hide then fully unhide -- not so good.
        # Hmm... let's put in Hide (with checkmark meaning "all hidden"), then iff that's not enough, Unhide.
        # So how do we know if a node is hidden -- this is only defined for leaf nodes now!
        # I guess we figure it out... I guess we might as well classify nodeset and its kids.
        
        allstats = statsclass()
        
        for node in nodeset:
            node.__stats = statsclass() # we expect python name-mangling to make this _modelTree__stats (or something like that)
            node.apply2all( lambda n1: accumulate_stats( n1, node.__stats) )
            allstats += node.__stats # totals to allstats

        # Hide command (and sometimes Unhide)
        
        # now can we figure out how much is/could be hidden, etc
        #e (later, modularize this, make assertfails only affect certain menu commands, etc)
        nleafs = allstats.n - allstats.ngroups
        assert nleafs >= 0
        nhidden = allstats.nhidden
        nunhidden = nleafs - nhidden # since only leafs can be hidden
        assert nunhidden >= 0

        # We'll always define a Hide item. Checked means all is hidden (and the command will be unhide);
        # unchecked means not all is hidden (and the command will be hide).
        # First handle degenerate case where there are no leafs selected.
        if nleafs == 0:
            res.append(( 'Hide', noop, 'disabled')) # nothing that can be hidden
        elif nunhidden == 0:
            # all is hidden -- show that, and offer to unhide it all
            ## res.append(( 'Hidden', self.cm_unhide, 'checked'))
            res.append(( 'Unhide', self.cm_unhide)) # will this be better?
            ##e do we want special cases saying "Unhide All", here and below,
            # when all hidden items would be unhidden, or vice versa?
            # (on PartGroup, or in other cases, so detect by comparing counts for sel and tree_node.)
        elif nhidden > 0:
            # some is not hidden, some is hidden -- make this clear & offer both extremes
            ## res.append(( 'Hide (' + fix_plurals('%d item(s)' % nunhidden) + ')', self.cm_hide )) #e fix_plurals bug, worked around
            res.append(( fix_plurals('Unhide %d item(s)' % nhidden), self.cm_unhide ))
            res.append(( fix_plurals('Hide %d item(s)' % nunhidden), self.cm_hide ))
        else:
            # all is unhidden -- just offer to hide it
            res.append(( 'Hide', self.cm_hide ))

        res.append(None) # separator
        
        # Edit Properties command -- only provide this when there's exactly one thing to apply it to,
        # and it says it can handle it.
        ###e Command name should depend on what the thing is, e.g. "Part Properties", "Chunk Properties".
        # Need to add methods to return that "user-visible class name".
        if len(nodeset) == 1 and nodeset[0].edit_props_enabled():
            res.append(( 'Properties', self.cm_properties ))
        else:
            res.append(( 'Properties', noop, 'disabled' )) # nim for multiple items

        res.append(None) # separator

        # Group command -- only when more than one thing is picked, and they're all in the same "assembly-node" --
        # kluging this for now as "PartGroup or a Shelf member", but it ought to be determined more rationally.
        # In fact, to save time, for now I'll just only do it in the first topnode, self.assy.tree (node, the partgroup)
        # or self.tree_item (the QListViewItem). I'll disable it when anything else is selected (i.e. in the shelf).
        # Then when we fix up the clipboard semantics I'll make it more general. ###e ###@@@

        if len(nodeset) < 2 or self.tree_node.picked or self.shelf_node.haspicked():
            res.append(( 'Group', noop, 'disabled' ))
        else:
            # 2 or more subtrees of the PartGroup -- should always be ok to group them
            res.append(( 'Group', self.cm_group ))

        # Ungroup command -- only when exactly one picked Group is what we have, of a suitable kind.
        # (As for Group, later this can become more general, tho in this case it might be general
        #  enough already -- it's more "self-contained" than the Group command can be.)

        if len(nodeset) == 1 and nodeset[0].permits_ungrouping():
            # (this implies it's a group, or enough like one)
            res.append(( 'Ungroup', self.cm_ungroup ))
        else:
            res.append(( 'Ungroup', noop, 'disabled' ))
         
        ###e more to follow... e.g. copy, cut, delete, maybe duplicate...

        # add basic info on what's selected at the end (later might turn into commands related to subclasses of nodes)

        if allstats.nchunks + allstats.njigs: # otherwise, nothing we can yet print stats on... (e.g. clipboard)

            res.append(None) # separator

            res.append(( "selection:", noop, 'disabled' ))
            
##            if len(nodeset) > 1:
##                res.append(( "%d selections:" % len(nodeset), noop, 'disabled' ))
##            else:
##                res.append(( "selection:", noop, 'disabled' ))
            
            if allstats.nchunks:
                res.append(( fix_plurals("%d chunk(s)" % allstats.nchunks), noop, 'disabled' ))
            
            if allstats.njigs:
                res.append(( fix_plurals("%d jig(s)" % allstats.njigs), noop, 'disabled' ))
            
            if allstats.nhidden:
                res.append(( fix_plurals("(%d of these are hidden)" % allstats.nhidden), noop, 'disabled' ))

##        ##e following msg is not true, since nodeset doesn't include selection under selected groups!
##        # need to replace it with a better breakdown of what's selected,
##        # incl how much under selected groups is selected. Maybe we'll add a list of major types
##        # of selected things, as submenus, lower down (with commands like "select only these", "deselect these").
##        
##        res.append(( fix_plurals("(%d selected item(s))" % len(nodeset)), noop, 'disabled' ))

        # pre-alpha warning [050126] (hope to be able to remove this for alpha):
        shelf_npicked = self.shelf_node.nodespicked() - int(self.shelf_node.picked)
            # clipboard itself, picked alone, probably has no bad bugs to warn about
        if shelf_npicked:
            res.append(None) # separator
            res.append(( fix_plurals("(%d selected item(s) in clipboard)" % shelf_npicked), noop, 'disabled' ))
            res.append(( "WARNING (pre-alpha): clipboard selections have bugs", noop ))

        return res # from make_cmenuspec_for_set

    ## Context menu handler functions [bruce 050112 renamed them; "hide" hid a QWidget method!]

    # these ones are good enough for now [050125]
    # (but they'll need revision when we fix clipboard bugs)
    
    def cm_hide(self):
        self.win.history.message("Hide: %d selected items or groups" % len(self.topmost_selected_nodes()))
        self.assy.permit_pick_parts() #e should not be needed here, but see if it fixes my bugs ###@@@ #k still needed? if so, why?
        self.assy.Hide() # operates only on assy.tree, using apply2picked; includes win_update
        
    def cm_unhide(self):
        self.win.history.message("Unhide: %d selected items or groups" % len(self.topmost_selected_nodes()))
        self.assy.permit_pick_parts() #e should not be needed here [see same comment above]
        self.assy.Unhide() # operates only on assy.tree, using apply2picked; includes win_update
    
    def cm_properties(self):
        nodeset = self.topmost_selected_nodes()
        if len(nodeset) != 1:
            self.win.history.message("error: cm_properties called on no or multiple items")
        else:
            node = nodeset[0]
            res = node.edit() #e rename method!
            if res:
                self.win.history.message(res) # added by bruce 050121 for error messages
            else:
                self.win.win_update()
        return
    
    def cm_group(self): # bruce 050126 adding comments and changing behavior
        "put the selected subtrees (if more than one) into a new Group"
        ##e I wonder if option/alt/midButton should be like a "force" or "power" flag
        # for cmenus; in this case, it would let this work even for a single element,
        # making a 1-item group. That idea can wait. [bruce 050126]
        ###@@@ the use of assy.tree to find what to operate on is wrong
        # (and will prevent this from working inside the clipboard);
        # this is tolerable for the moment. [bruce 050126]
        node = self.assy.tree.hindmost() # smallest nodetree containing all picked nodes 
        if not node:
            self.win.history.message("nothing selected to Group") # should never happen
            return # hindmost can return "None", with no "picked" attribute. Mark 401210.
        if node.picked:
            # prevent 1-item Groups from being formed
            # (should never occur, if caller constructs menu properly, unless it wants
            #  to permit 1-item groups, which would require a new special case here to do
            #  correctly, I think -- bruce 050126)
            self.win.history.message("single item, not making a new Group")
            return
        # node is an unpicked Group; more than one of its children are either picked
        # or contain something picked (but maybe none of them are directly picked).
        # we'll make a new Group inside node, just before the first child containing
        # anything picked, and move all picked subtrees into it (preserving their order;
        # but losing their structure in terms of unpicked groups that contain some of them).
        ###e what do we do with the picked state of things we move? worry about the invariant! ####@@@@

        # make a new Group (inside node, same assy)
        ###e future: require all assys the same, or, do this once per topnode or assy-node.
        # for now: this will have bugs when done across topnodes!
        # so the caller doesn't let that happen, for now. [050126]
        new = Group(gensym("Group"), node.assy, node) # was self.assy
        assert not new.picked

        # put it where we want it -- before the first node member-tree with anything picked in it
        for m in node.members:
            if m.haspicked():
                assert m != new
                node.delmember(new) #e (addsibling ought to do this for us...)
                m.addsibling(new, before = True)
                break # (this always happens, since something was picked under node)
        node.apply2picked(lambda(x): x.moveto(new)) # was self.tree_item.object.apply2picked
            # this will have skipped new before moving anything picked into it!
            # even so, I'd feel better if it unpicked them before moving them...
            # but I guess it doesn't. for now, just see if it works this way... seems to work.
        msg = "grouped %d items into %s" % (len(new.members), new.name)
        self.win.history.message( msg)
        
        # we have not changed picked state of anything in glpane, so in theory only the mtree
        # needs updating... [050126, untested]
        self.mt_update() # bruce 050110 this does not seem to be always working ###@@@ still??
    
    def cm_ungroup(self):
        nodeset = self.topmost_selected_nodes()
        assert len(nodeset) == 1
        node = nodeset[0]
        assert node.permits_ungrouping()
        node.ungroup()
        # for now, this does not change the picked state, so no glpane update is needed... [050126, untested]
        #e history.message?
        self.mt_update()

    # not yet reviewed: [050126] ###@@@
    
    def cm_copy(self):
        self.assy.copy()
        self.mt_update()
    
    def cm_cut(self):
        self.assy.cut()
        self.mt_update()
    
    def cm_kill(self):
        # note: this is essentially the same as MWsemantics.killDo. [bruce 041220 comment]
        self.assy.kill()
        self.win.win_update() # Changed from self.mt_update for deleting from MT menu. Mark [04-12-03]

    pass # end of class modelTree

# end
