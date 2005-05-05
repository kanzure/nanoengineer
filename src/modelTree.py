# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
modelTree.py -- The model tree display widget. Inherits from TreeWidget.py.

[mostly owned by Bruce]

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
from jigs import Jig
import platform # for atom_debug
from HistoryWidget import redmsg, greenmsg, orangemsg # not all used, that's ok


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

# custom QListViewItem

class mt_QListViewItem( QListViewItem):
    "used for nodes with specialize drawing for various purposes (maybe more than one purpose at once)"
    dotcolor = Qt.red # also available: Qt.blue, Qt.green, Qt.black, QColor(128,0,128), QColor(200,100,0)...
    def setText(self, col, text): # this is called...
        ## print "setText called in custom item",col,text
        ##     # this happens for all nodes after the first in each set of node-kids
        super = QListViewItem
        return super.setText(self, col, text)
    def paintCell(self, p, cg, col, width, align):
                  # QPainter * p, const QColorGroup & cg, int column, int width, int align )
                  # for align see "Qt::AlignmentFlags"... not sure if they'd help; this doesn't cover the area I want to paint
        ## print "paintCell",p, cg, col, width, align # might happen a lot
        ## # paintCell <constants.qt.QPainter object at 0xcf51330> <constants.qt.QColorGroup object at 0xce97120> 0 132 1
        # 0. grab useful values; if this fails use super method
        super = QListViewItem
        try:
            node = self.object
            assy = node.assy
            sg = assy.current_selgroup_iff_valid()
        except:
            print "bug"
            print_compact_traceback("exception in mt_QListViewItem.paintCell: ")
            return super.paintCell(self, p, cg, col, width, align)
        # 1. modify painter before superclass paintcell runs
        p.save()
        if node.is_disabled():
            if 1: #bruce 050423 try to fix bug 562 by erasing to the right of our italic text...
                ## use p.clipRegion? p.eraseRect? Ask QLV for the rect?
                ## print "width is",self.width() -- width needs args for font and column and maybe more! (could find them if necessary)
                ## print "height is",self.height()
                p.eraseRect(0,0,500,self.height())
                    # the 500 is just an obviously-too-large width... will it mess up scrollbar? not on mac.
            # italic name indicates a disabled node (e.g. a jig whose atoms are not in same part, which won't affect the sim)
            p.shear(0, -0.5)
            # WARNING: this shear might have no effect on some platforms, because Qt doc for QListViewItem.paintCell says
            # it should assume painter p state is undefined (I think). Of course p's translation matters, so maybe that's why
            # shear matters, I don't know; or it might just be a Qt bug that it works on the Mac. I also tried setting its
            # pen color and thickness [ p.setPen(QPen(Qt.red, 3)) ], and this had no effect, as predicted by that Qt doc.
            # [bruce 050421]
            #e We should also perhaps alter color for some nodes, e.g. the chunks "touched" by selected jigs (or chunks?)
            # or vice versa... above comment implies that to do this in their text, we'd pass paintCell a modified cg;
            # or we could draw more stuff on top of them (like the red dot below). [bruce 050421]
        res = super.paintCell(self, p, cg, col, width, align)
        p.restore() # without this, shear also affects the red dot drawn below,
            # and text in the drag-graphic (but not other QLVitems) [bruce 050421]
        # 2. red dot indicates currently shown clipboard item, if any
        try:
            if sg == node and node != assy.tree:
                ## before 050421 this class was only used when node.is_top_of_selection_group(), and that if condition was: 
                ## if node != assy.tree and (node.part == assy.part or node == assy.part.topnode.dad): # needs deklugification
                # 
                ## print "super.paintCell returned",res # always None
                ## Python insists self must be right class, so this fails: TreeView.drawbluething( "self arg not used", p)
                p.save()
                p.setPen(QPen(self.dotcolor, 3)) # 3 is pen thickness; btw, this also sets color of the "moving 1 item" at bottom of DND graphic!
                w,h = 100,9 # bbox rect size of what we draw (i think)
                x,y = -21,8 # topleft of what we draw; 0,0 is topleft corner of icon; neg coords work, not sure how far or how safe
                p.drawEllipse(x,y,h,h) # gets onto topleft of the icon (pixmap) region. Useful for something but not for what I want.
                p.restore() # without this, changed color affects text in the drag-graphic [bruce 050421]
        except:
            print "bug"
            print_compact_traceback("exception in mt_QListViewItem.paintCell: ")
        return res
    pass # end of class mt_QListViewItem

# main widget class

class modelTree(TreeWidget):
    def __init__(self, parent, win, name = "modelTreeView", size = (200, 560)):
        """#doc"""
        ###@@@ review all init args & instvars, here vs subclasses
        TreeWidget.__init__(self, parent, win, name, columns = ["Model Tree"], size = size) # stores self.win

        # debug menu and reload command - inited in superclass ###k ok?

        self.assy = win.assy #k needed? btw does any superclass depend on this?? ###@@@

        self.initialized = 1 ###@@@ review where this is done
        self.mt_update() ###@@@ review where done, and name (split it?)
        return

    def resetAssy_and_clear(self): #bruce 050201 for Alpha, part of Huaicai's bug 369 fix
        """This method should be called from the end of MWsemantics.__clear
        to prevent a crash on (at least) Windows during File->Close when the mtree is
        editing an item's text, using a fix developed by Huaicai 050201,
        which is to run the QListView method self.clear().
           Neither Huaicai nor Bruce yet understands why this fix is needed or why
        it works, so the details of what this method does (and when it's called,
        and what's it's named) might change. Bruce notes that without this fix,
        MWsemantics.__clear would change win.assy (but not tell the mt (self) to change
        its own .assy) and call mt_update(), which in old code would immediately do
        self.clear() but in new code doesn't do it until later, so this might relate
        to the problem. Perhaps in the future, mt_update itself can compare self.assy
        to self.win.assy and do this immediate clear() if they differ, so no change
        would be needed to MWsemantics.__clear(), but for now, we'll just do it
        like this.
        """
        self.clear()
        # prevents Windows crash if an item's text is being edited in-place
        # [huaicai & bruce 050201 for Alpha to fix bug 369; not sure how it works]
        return

    # callbacks from superclass to help it update the display
    
    def get_topnodes(self):
        self.assy = self.win.assy #k need to save it like this?
        self.assy.tree.name = self.assy.name
            #k is this still desirable, now that we have PartGroup
            # so it's no longer needed for safety?
        kluge_patch_assy_toplevel_groups( self.assy, assert_this_was_not_needed = True)
            # fixes Group subclasses of assy.shelf and assy.tree, and
            # [not anymore, as of some time before 050417] inserts assy.viewdata.members into assy.tree
        self.tree_node, self.shelf_node = self.assy.tree, self.assy.shelf
        return [self.assy.tree, self.assy.shelf]

    def post_update_topitems(self):
        self.tree_item, self.shelf_item = self.topitems ###k needed??
            # the actual items are different each time this is called

    def QListViewItem_subclass_for_node( self, node, parent, display_prefs, after):
        if node.is_top_of_selection_group() or node.is_disabled():
                ## can't do this -- it's causing a bug where clipboard won't reopen with red dot: or node == node.assy.shelf:
            return mt_QListViewItem
        return QListViewItem

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

        try:
            njigs = allstats.njigs
            if njigs == 1 and allstats.n == 1:
                # exactly one jig selected. Show its disabled state, with option to change this if permitted.
                # warning: depends on details of Jig.is_disabled() implem. Ideally we should ask Jig to contribute
                # this part of the menu-spec itself #e. [bruce 050421]
                jig = nodeset[0]
                disabled_must = jig.disabled_by_atoms() # (by its atoms being in the wrong part)
                disabled_choice = jig.disabled_by_user_choice
                disabled_menu_item = disabled_must # menu item is disabled iff jig disabled state can't be changed, ie is "stuck on"
                checked = disabled_must or disabled_choice # menu item is checked if it's disabled for whatever reason (also affects text)
                if checked:
                    command = self.cm_enable
                    if disabled_must:
                        text = "Disabled (atoms in other Part)"
                    else:
                        text = "Disabled"
                else:
                    command = self.cm_disable
                    text = "Disable"
                res.append(( text, command, checked and 'checked' or None, disabled_menu_item and 'disabled' or None ))
        except:
            print "bug in MT njigs == 1, ignored"
            ## raise # just during devel
            pass

        res.append(None) # separator

        # Group command -- only ok for 2 or more subtrees of any Part,
        # or for exactly one clipboard item topnode itself if it's not already a Group.
        # [rules loosened by bruce 050419-050421]
        
        if len(nodeset) >= 2:
            # note that these nodes are always in the same Part and can't include its topnode
            ok = True
        else:
            # exactly one node - better be a clipboard item and not a group
            node = nodeset[0]
            ok = (node.dad == self.shelf_node and not node.is_group())
        if not ok:
            res.append(( 'Group', noop, 'disabled' ))
        else:
            res.append(( 'Group', self.cm_group ))

        # Ungroup command -- only when exactly one picked Group is what we have, of a suitable kind.
        # (As for Group, later this can become more general, tho in this case it might be general
        #  enough already -- it's more "self-contained" than the Group command can be.)

        if len(nodeset) == 1 and nodeset[0].permits_ungrouping():
            # (this implies it's a group, or enough like one)
            node = nodeset[0]
            if node.dad == self.shelf_node and len(node.members) > 1:
                text = "Ungroup into separate clipboard items" #bruce 050419 new feature (distinct text in this case)
            else:
                text = "Ungroup"
            res.append(( text, self.cm_ungroup ))
        else:
            res.append(( 'Ungroup', noop, 'disabled' ))

        ## res.append(None) # separator - from now on, add these at start of optional sets, not at end

        # Edit Properties command -- only provide this when there's exactly one thing to apply it to,
        # and it says it can handle it.
        ###e Command name should depend on what the thing is, e.g. "Part Properties", "Chunk Properties".
        # Need to add methods to return that "user-visible class name".
        res.append(None) # separator
        if len(nodeset) == 1 and nodeset[0].edit_props_enabled():
            res.append(( 'Properties', self.cm_properties ))
        else:
            res.append(( 'Properties', noop, 'disabled' )) # nim for multiple items
         
        # copy, cut, delete, maybe duplicate...
        # some of them are not-for-use-in-clipboard [bruce 050131]
        res.append(None) # separator
        if len(nodeset) >= 1 and nodeset[0].find_selection_group() == self.tree_node:
            # selection is in the main part
            res.append(( 'Copy', self.cm_copy )) ###@@@ review or fix for being ok in clipboard?
            res.append(( 'Cut', self.cm_cut )) ###@@@ ditto
        res.append(('Delete', self.cm_delete )) # ok for part or clipboard
        #e duplicate?

        # add basic info on what's selected at the end (later might turn into commands related to subclasses of nodes)

        if allstats.nchunks + allstats.njigs: # otherwise, nothing we can yet print stats on... (e.g. clipboard)

            res.append(None) # separator

            res.append(( "selection:", noop, 'disabled' ))
                        
            if allstats.nchunks:
                res.append(( fix_plurals("%d chunk(s)" % allstats.nchunks), noop, 'disabled' ))
            
            if allstats.njigs:
                res.append(( fix_plurals("%d jig(s)" % allstats.njigs), noop, 'disabled' ))
            
            if allstats.nhidden:
                res.append(( "(%d of these are hidden)" % allstats.nhidden, noop, 'disabled' ))

            if allstats.njigs == allstats.n and allstats.njigs:
                # only jigs are selected -- offer to select their atoms [bruce 050504]
                if allstats.njigs == 1:
                    natoms = len(nodeset[0].atoms)
                    myatoms = fix_plurals( "this jig's %d atom(s)" % natoms )
                else:
                    myatoms = "these jigs' atoms"
                res.append(('Select ' + myatoms, self.cm_select_jigs_atoms ))

##        ##e following msg is not true, since nodeset doesn't include selection under selected groups!
##        # need to replace it with a better breakdown of what's selected,
##        # incl how much under selected groups is selected. Maybe we'll add a list of major types
##        # of selected things, as submenus, lower down (with commands like "select only these", "deselect these").
##        
##        res.append(( fix_plurals("(%d selected item(s))" % len(nodeset)), noop, 'disabled' ))

        return res # from make_cmenuspec_for_set

    ## Context menu handler functions [bruce 050112 renamed them; "hide" hid a QWidget method!]

    # these ones are good enough for now [050125]
    # (but they'll need revision when we fix clipboard bugs)
    
    def cm_hide(self):
        self.win.history.message("Hide: %d selected items or groups" % len(self.topmost_selected_nodes()))
        self.assy.permit_pick_parts() #e should not be needed here, but see if it fixes my bugs ###@@@ #k still needed? if so, why?
        self.assy.Hide() # includes win_update
        
    def cm_unhide(self):
        self.win.history.message("Unhide: %d selected items or groups" % len(self.topmost_selected_nodes()))
        self.assy.permit_pick_parts() #e should not be needed here [see same comment above]
        self.assy.Unhide() # includes win_update
    
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
    
    def cm_group(self): # bruce 050126 adding comments and changing behavior; 050420 permitting exactly one subtree
        "put the selected subtrees (one or more than one) into a new Group (and update)"
        ##e I wonder if option/alt/midButton should be like a "force" or "power" flag
        # for cmenus; in this case, it would let this work even for a single element,
        # making a 1-item group. That idea can wait. [bruce 050126]
        #bruce 050420 making this work inside clipboard items too
        # TEST if assy.part updated in time ####@@@@ -- no, change to selgroup!
        sg = self.assy.current_selgroup()
        node = sg.hindmost() # smallest nodetree containing all picked nodes 
        if not node:
            self.win.history.message("nothing selected to Group") # should never happen
            return # hindmost can return "None", with no "picked" attribute. Mark 401210.
        if node.picked:
            #bruce 050420: permit this case whenever possible (formation of 1-item group);
            # cmenu constructor should disable or leave out the menu command when desired.
            if node != sg:
                assert node.dad # in fact, it'll be part of the same sg subtree (perhaps equal to sg)
                node = node.dad
                assert not node.picked
                # fall through -- general case below can handle this.
            else:
                # the picked item is the topnode of a selection group.
                # If it's the main part, we could make a new group inside it
                # containing all its children (0 or more). This can't happen yet
                # so I'll be lazy and save it for later.
                assert node != self.assy.tree
                # Otherwise it's a clipboard item. Let the Part take care of it
                # since it needs to patch up its topnode, choose the right name,
                # preserve its view attributes, etc.
                assert node.part.topnode == node
                newtop = node.part.create_new_toplevel_group()
                self.win.history.message("made new group %s" % newtop.name) ###k see if this looks ok with autogenerated name
                self.mt_update()
                return
        # (above 'if' might change node and then fall through to here)
        # node is an unpicked Group inside (or equal to) sg;
        # more than one of its children (or exactly one if we fell through from the node.picked case above)
        # are either picked or contain something picked (but maybe none of them are directly picked).
        # We'll make a new Group inside node, just before the first child containing
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
                ## node.delmember(new) #e (addsibling ought to do this for us...) [now it does]
                m.addsibling(new, before = True)
                break # (this always happens, since something was picked under node)
        node.apply2picked(lambda(x): x.moveto(new)) # was self.tree_item.object.apply2picked
            # this will have skipped new before moving anything picked into it!
            # even so, I'd feel better if it unpicked them before moving them...
            # but I guess it doesn't. for now, just see if it works this way... seems to work.
            # ... later [050316], it evidently does unpick them, or maybe delmember does.
        from platform import fix_plurals
        msg = fix_plurals("grouped %d item(s) into " % len(new.members)) + "%s" % new.name
        self.win.history.message( msg)

        # now, should we pick the new group so that glpane picked state has not changed?
        # or not, and then make sure to redraw as well? hmm...
        # - possibility 1: try picking the group, then see if anyone complains.
        # Caveat: future changes might cause glpane redraw to occur anyway, defeating the speed-purpose of this...
        # and as a UI feature I'm not sure what's better.
        # - possibility 2: don't pick it, do update glpane. This is consistent with Ungroup (for now)
        # and most other commands, so I'll do it.
        #
        # BTW, the prior code didn't pick the group
        # and orginally didn't unpick the members but now does, so it had a bug (failure to update
        # glpane to show new picked state), whose bug number I forget, which this should fix.
        # [bruce 050316]
        ## new.pick() # this will emit an undesirable history message... fix that?
        self.win.glpane.gl_update() #k needed?
        self.mt_update()
        return
    
    def cm_ungroup(self):
        from platform import fix_plurals
        nodeset = self.topmost_selected_nodes()
        assert len(nodeset) == 1 # caller guarantees this
        node = nodeset[0]
        assert node.permits_ungrouping() # ditto
        need_update_parts = []
        if node.is_top_of_selection_group():
            # this case is harder, since dissolving this node causes its members to become
            # new selection groups. Whether there's one or more members, Part structure needs fixing;
            # if more than one, interpart bonds need breaking (or in future might keep some subsets of
            # members together; more likely we'd have a different command for that).
            # simplest fix -- just make sure to update the part structure when you're done.
            # [bruce 050316]
            need_update_parts.append( node.assy)
            #bruce 050419 comment: if exactly one child, might as well retain the same Part... does this matter?
            # Want to retain its name (if group name was automade)? think about this a bit before doing it...
            # maybe fixing bugs for >1 child case will also cover this case. ###e
            #bruce 050420 addendum: I did some things in Part.__init__ which might handle all this well enough. We'll see. ###@@@ #k
        if node.is_top_of_selection_group() and len(node.members) > 1:
            msg = "splitting %r into %d new clipboard items" % (node.name, len(node.members))
        else:
            msg = fix_plurals("ungrouping %d item(s) from " % len(node.members)) + "%s" % node.name
        self.win.history.message( msg)
        node.ungroup()
        # this also unpicks the nodes... is that good? Not really, it'd be nice to see who they were,
        # and to be consistent with Group command, and to avoid a glpane redraw.
        # But it's some work to make it pick them now, so for now I'll leave it like that.
        # BTW, if this group is a clipboard item and has >1 member, we couldn't pick all the members anyway!
        #e history.message?
        for assy in need_update_parts:
            assy.update_parts() # this should break new inter-part bonds
        self.win.glpane.gl_update()
        self.mt_update()
        return

    # copy and cut and delete are doable by tool buttons
    # so they might as well be available from here as well;
    # anyway I tried to fix or mitigate their bugs [bruce 050131]:
    
    def cm_copy(self):
        self.assy.copy_sel()
        ## bruce 050427: removing mt_update since copy_sel does win_update:
        ## self.mt_update()
    
    def cm_cut(self):
        self.assy.cut_sel()
        ## bruce 050427: removing win_update since cut_sel does it:
        ## self.win.win_update() # Changed from self.mt_update [bruce 050421 precaution, seems necessary tho I didn't notice bugs]
    
    def cm_delete(self): # renamed from cm_kill which was renamed from kill
        # note: this is now the same code as MWsemantics.killDo. [bruce 050131]
        self.assy.delete_sel()
        ##bruce 050427 moved win_update into delete_sel as part of fixing bug 566
        ##self.win.win_update()

    def cm_disable(self): #bruce 050421
        nodeset = self.topmost_selected_nodes()
        assert len(nodeset) == 1 # caller guarantees this
        node = nodeset[0]
        jig = node # caller guarantees this is a jig; if not, this silently has no effect
        jig.disabled_by_user_choice = True
        self.win.win_update()

    def cm_enable(self): #bruce 050421
        nodeset = self.topmost_selected_nodes()
        assert len(nodeset) == 1, "len nodeset should be 1, but nodeset is %r" % nodeset
        node = nodeset[0]
        jig = node
        jig.disabled_by_user_choice = False
        self.win.win_update()

    def cm_select_jigs_atoms(self): #bruce 050504
        nodeset = self.topmost_selected_nodes()
        otherpart = {} #bruce 050505 to fix bug 589
        did_these = {}
        for jig in nodeset:
            assert isinstance( jig, Jig) # caller guarantees they are all jigs
            for atm in jig.atoms:
                if atm.molecule.part == jig.part:
                    atm.pick()
                    did_these[atm.key] = atm
                else:
                    otherpart[atm.key] = atm
            jig.unpick() # not done by picking atoms
        msg = fix_plurals("Selected %d atom(s)" % len(did_these)) # might be 0, that's ok
        if otherpart:
            msg += fix_plurals(" (skipped %d atom(s) which were not in this Part)" % len(otherpart))
            msg = orangemsg(msg) # the whole thing, I guess
        self.win.history.message(msg)
        self.win.win_update()
        # note: caller (which puts up context menu) does self.update_select_mode(); we depend on that.
        return
    
    pass # end of class modelTree

# end
