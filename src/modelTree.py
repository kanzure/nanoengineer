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

# helper function for making context menus

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

class modelTree(TreeWidget):
    def __init__(self, parent, win, name = "modelTreeView"):
        """#doc"""
        ###@@@ review all init args & instvars, here vs subclasses
        TreeWidget.__init__(self, parent, win, name, columns = ["Model Tree"]) # stores self.win

        # debug menu and reload command - inited in superclass ###k ok?

        self.assy = win.assy #k needed? btw does any superclass depend on this?? ###@@@

##        ###@@@ soon to be obs (or moved elsewhere):
##        self._init_menus()

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
        return [self.assy.tree, self.assy.shelf]

    def post_update_topitems(self):
        self.tree, self.shelf = self.topitems ###k needed??
            # the actual items are different each time this is called

    # special calls from external code
    
    def open_clipboard(self): #bruce 050108, probably temporary
        ## self._open_listitem(self.shelf)
        self.toggle_open( self.shelf, openflag = True)
    
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
            ## print "so far: node.__stats = %r, allstats = %r" % (node.__stats, allstats) #####@@@@@
        
        # ...

        # Hide command (and sometimes Unhide)
        
        # now can we figure out how much is/could be hidden, etc
        #e (later, modularize this, make assertfails only affect certain menu commands, etc)
        nleafs = allstats.n - allstats.ngroups
        assert nleafs >= 0
        nhidden = allstats.nhidden
        nunhidden = nleafs - nhidden # since only leafs can be hidden
        assert nunhidden >= 0
##        print nodeset #####@@@@@
##        print "nleafs = %d, nhidden = %d, nunhidden = %d" % (nleafs, nhidden, nunhidden)  #####@@@@@
##        print allstats #####@@@@@

        # We'll always define a Hide item. Checked means all is hidden (and the command will be unhide);
        # unchecked means not all is hidden (and the command will be hide).
        # First handle degenerate case where there are no leafs selected.
        if nleafs == 0:
            res.append(( 'Hide', noop, 'disabled')) # nothing that can be hidden
        elif nunhidden == 0:
            # all is hidden -- show that, and offer to unhide it all
            res.append(( 'Hidden', self.cm_unhide, 'checked'))
        elif nhidden > 0:
            # some is not hidden, some is hidden -- make this clear & offer both extremes
            ## res.append(( 'Hide (' + fix_plurals('%d item(s)' % nunhidden) + ')', self.cm_hide )) #e fix_plurals bug, worked around
            res.append(( fix_plurals('Hide %d item(s)' % nunhidden), self.cm_hide ))
            res.append(( fix_plurals('Unhide %d item(s)' % nhidden), self.cm_unhide ))
        else:
            # all is unhidden -- just offer to hide it
            res.append(( 'Hide', self.cm_hide ))

        # Edit Properties command -- only provide this when there's exactly one thing to apply it to, I guess.
        if len(nodeset) == 1:
            res.append(( 'Properties', self.cm_properties ))
        else:
            res.append(( 'Properties', noop, 'disabled' )) # nim for multiple items
        
        ###e more to follow...

        # add basic info on what's selected at the end (later might turn into commands related to subclasses of nodes)
        
        ##e following msg is not true, since nodeset doesn't include selection under selected groups!
        # need to replace it with a better breakdown of what's selected,
        # incl how much under selected groups is selected. Maybe we'll add a list of major types
        # of selected things, as submenus, lower down (with commands like "select only these", "deselect these").
        
        res.append(( fix_plurals("(%d item(s) selected)" % len(nodeset)), noop, 'disabled' )) #e move to bottom?

        return res # from make_cmenuspec_for_set

    
##        # ok, what does the following do or want to do?
##        # click on data item (csys or datum plane) or directly on part node or clipboard node (maybe unintended? maybe not):
##        #     iff name is assy name (true only for part node i think), then use partmenu
##        # in other words, there is a special menu for the Part node itself, and no menu at all for those other special high up nodes.
##        # (which is not right, but never mind) [btw the finder sel item / cmenu rules don't know about sel group specialness... #think)
##        # [btw i suspect we should contribute menu entries for both the itemness (eg collapse all) and the nodeness...]
##        #
##        # click on any other item: fall thru... or on no item: no menu [wrong, fixed above]
##        if item:
##            self.last_selected_node = item.object
##            sdaddy = self.last_selected_node.whosurdaddy()
##            if sdaddy in ["ROOT","Data"]: 
##                # This conditional should change.  There has to be a better check.
##                # We get the partmenu if another object has the same name as the assy.
##                # Mark 041225 (Merry Xmas!)
##                if self.last_selected_node.name == self.assy.name: 
##                    return self.partmenu_spec
##                return
##            # else fall thru
##        else:
##            self.last_selected_node = None
##            return
##
##        # ok what does this do (for a real and ordinary item - a chunk or group, never the partgroup)?
##        # what it looks like it wanted to do: if any sel in clipboard, use clipboardmenu,
##        # else if any in main model, use right one of singlemenu and multimenu.
##        # and does 0/False wrongness make it do anything different? no, it was ok since called on groups.
##        
##        # Figure out which menu to display 
##        # (This is kludgy - meant to be a quick fix for Alpha) - Mark
##        treepicked = self.assy.tree.nodespicked() #Number of nodes picked in the MT
##        clippicked = self.assy.shelf.nodespicked() #Number of nodes picked in the clipboard
##        if treepicked == 0 and clippicked == 0:
##            return
##        if clippicked:
##             ###@@@ bruce 041227 comment: this test being first could be bad
##            # for depositmode's current use of clipboard selection; but that use
##            # is slated to be changed.
##            return self.clipboardmenu_spec
##        elif treepicked == 1:
##            return self.singlemenu_spec
##        elif treepicked > 1:
##            return self.multimenu_spec


    ## Context menu handler functions [bruce 050112 renamed them; "hide" hid a QWidget method!]

    # good enough for now: [050125]
    
    def cm_hide(self):
        self.win.history.message("Hide: %d selected items or groups" % len(self.topmost_selected_nodes()))
        ## print "assy.selwhat =",self.assy.selwhat
        self.assy.permit_pick_parts() #e should not be needed here, but see if it fixes my bugs #####@@@@@
        self.assy.Hide() # operates only on assy.tree, using apply2picked; includes win_update
        
    def cm_unhide(self):
        self.win.history.message("Unhide: %d selected items or groups" % len(self.topmost_selected_nodes()))
        self.assy.permit_pick_parts() #e should not be needed here, but see if it fixes my bugs #####@@@@@
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

    # not yet reviewed: [050125]
    
    def cm_group(self):
        node = self.assy.tree.hindmost()
        if not node: return # hindmost can return "None", with no "picked" attribute. Mark 401210.
        if node.picked: return
        new = Group(gensym("Group"), self.assy, node)
        self.tree.object.apply2picked(lambda(x): x.moveto(new))
        self.mt_update() # bruce 050110 this does not seem to be always working ####@@@@
    
    def cm_ungroup(self):
        self.tree.object.apply2picked(lambda(x): x.ungroup())
        self.mt_update()
    
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

## zapped by bruce 050108 since unused and uses deprecated node.setopen:
##    def expand(self):
##        self.tree.object.apply2tree(lambda(x): x.setopen())
##        self.mt_update()

    pass # end of class modelTree

# end
