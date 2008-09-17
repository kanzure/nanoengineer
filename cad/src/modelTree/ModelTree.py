# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
modelTree.py -- The NE1 model tree display widget, including
its context menu commands.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

modelTree.py was originally written by some combination of
Huaicai, Josh, and Mark. Bruce (Jan 2005) reorganized its interface with
Node and Group and their subclasses (Utility.py and other modules)
and rewrote a lot of the model-tree code (mainly to fix bugs),
and split it into three modules:

- TreeView.py (display and update),

- TreeWidget.py (event handling, and some conventions suitable for
  all our tree widgets, if we define other ones), and

- modelTree.py (customized for showing "the NE1 model tree" per se).

After that, Will ported it to Qt4, and since the Q3 compatibility
classes were unsupported by PyQt4, rewrote much of it, in the process
replacing TreeView.py and TreeWidget.py by a new file, modelTreeGui.py,
and adding a standalone prototype file modelTreePrototype.py (functional
as a separate test program, but not used by NE1). The current organization
might therefore be:

- modelTreeGui.py (display and update, event handling, and some
  conventions suitable for all our tree widgets, if we define other ones), and
  
- modelTree.py (customized for showing "the NE1 model tree" per se).

Bruce later rewrote much of modelTreeGui.py, and has added lots
of context menu commands to modelTree.py at various times.
"""

from PyQt4 import QtCore

import foundation.env as env
from utilities import debug_flags
from platform_dependent.PlatformDependent import fix_plurals
import modelTree.modelTreeGui as modelTreeGui # defines ModelTreeGui (note case difference), Ne1Model_api

from model.chunk import Chunk
from model.jigs import Jig
from utilities.Log import orangemsg
from foundation.Group import Group
from utilities.debug import print_compact_traceback

from utilities.GlobalPreferences import permit_atom_chunk_coselection
from utilities.GlobalPreferences import pref_show_highlighting_in_MT

from utilities.constants import gensym
from utilities.constants import SELWHAT_ATOMS
from utilities.constants import SELWHAT_CHUNKS
from utilities.constants import SELWHAT_NAMES
from utilities.constants import noop

from utilities.qt4transition import qt4here

_debug_preftree = False # bruce 050602 experiment; do not commit with True

# helpers for making context menu commands

class statsclass: # todo: rename, and  move to its own utility module?
    """
    class for holding and totalling counts of whatever you want, in named attributes
    """
    def __getattr__(self, attr): # in class statsclass
        if not attr.startswith('_'):
            return 0 # no need to set it
        raise AttributeError, attr
    def __iadd__(self, other):
        """
        this implements self += other
        """
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

def _accumulate_stats(node, stats):
    """
    When making a context menu from a nodeset (of "topselected nodes"),
    this is run once on every topselected node (note: they are all picked)
    and once on every node under those (whether or not they are picked).
    """
    # todo (refactoring): could be a method on our own subclass of statsclass
    stats.n += 1

    stats.ngroups += int(isinstance(node, Group))
    if (isinstance(node, Chunk)):
        stats.nchunks += 1
        if (node.chunkHasOverlayText and not node.showOverlayText):
            stats.canShowOverlayText += 1
        if (node.chunkHasOverlayText and node.showOverlayText):
            stats.canHideOverlayText += 1
    stats.njigs += int(isinstance(node, Jig))
    #e later, classify(node1, Node) into a list of classes, and get counts for all...

    stats.npicked += int(node.picked)
    stats.nhidden += int(node.hidden)
    stats.nopen += int(node.open)
    return


############################################################

# main widget class

class modelTree(modelTreeGui.Ne1Model_api):
    def __init__(self, parent, win, name = "modelTreeView", size = (200, 560)):
        """
        #doc
        """
        ###@@@ review all init args & instvars, here vs subclasses
        self.modelTreeGui = modelTreeGui.ModelTreeGui(win, name, self, parent)
            # WARNING: self.modelTreeGui is a PUBLIC MEMBER which is accessed by MWsemantics (at least)
            # for use in building the Qt widget layout. For public access purposes it can be considered
            # "the Qt widget containing the model tree" and it ought to have a special name (or get-method)
            # just for that purpose, so this attr could be made private.
            #    Worse, the code before late on 070509 sometimes stored self.modelTreeGui rather than self
            # in win.mt (maybe) and assy.mt (definitely), but other times stored self!
            # And lots of files call various methods on assy.mt and/or win.mt, namely:
            # - update_select_mode
            # - resetAssy_and_clear
            # - mt_update
            # - open_clipboard
            # and in mwsem:
            # - self.mt.setMinimumSize(0, 0)
            # - self.mt.setColumnWidth(0,225)
            # So for now, I made sure all those can be called on self (it was already true),
            # and in future, they need to be documented in the api, or the external calls should
            # call them explicitly on the widget member (accessing it in a valid public way).
            # [bruce 070509 comment]
        self.win = win

        # debug menu and reload command - inited in superclass ###k ok?

        self.assy = win.assy #k needed? btw does any superclass depend on this?? ###@@@

        self.mt_update()
        return

    def statusbar_message(self, text): #bruce 070531 # note: not presently used; untested
        self.modelTreeGui.statusbar_message(text)
        return

    def update_select_mode(self): #bruce 050124; should generalize and refile; should be used for more or for all events ###@@@
        #bruce 060403 revised this but didn't update docstring; now it can change from *Chunk modes to Build, only, I think
        """
        This should be called at the end of event handlers which might have
        changed the current internal selection mode (atoms vs chunks),
        to resolve disagreements between that and the visible selection mode
        iff it's one of the Select modes [or more generally, i assume as of 060403,
        if the current mode wants to be ditched if selwhat has to have certain values it dislikes].
           If the current mode is not one of Select Atoms or Select Chunks, this routine has no effect.
        (In particular, if selwhat changed but could be changed back to what it was,
        it does nothing to correct that [obs? see end of docstring], and indeed it doesn't know the old value of
        selwhat unless the current mode (being a selectMode) implies that.)
           [We should generalize this so that other modes could constrain the selection
        mode to just one of atoms vs chunks if they wanted to. However, the details of this
        need design, since for those modes we'd change the selection whereas for the
        select modes we change which mode we're in and don't change the selection. ###@@@]
           If possible, we leave the visible mode the same (even changing assy.selwhat
        to fit, if nothing is actually selected [that part was NIM until 050519]).
        But if forced to, by what is currently selected, then we change the visible
        selection mode to fit what is actually selected. (We always assert that selwhat
        permitted whatever was selected to be selected.)
        """
        if permit_atom_chunk_coselection(): #bruce 060721
            return
        from commands.SelectChunks.SelectChunks_Command import SelectChunks_Command
        
        #bruce 050519 revised docstring and totally rewrote code.
        assy = self.assy
        win = self.win
        commandSequencer = self.win.commandSequencer #bruce 071008
        mode = commandSequencer.currentCommand
            #bruce 071008; note, I'm not sure it's right to ask the currentCommand
            # for selwhat_from_mode, as opposed to the current graphicsMode!
            # This whole thing needs total revamping (along with everything
            # related to what can be selected at a given time), so I'm not going
            # to worry about it for now.
        del self
        part = assy.part
        # 0. Appraise the situation.
        # 0a: assy.selwhat is what internal code thinks selection restriction is, currently.
        selwhat = assy.selwhat
        assert selwhat in (SELWHAT_CHUNKS, SELWHAT_ATOMS) # any more choices, or change in rules, requires rewriting this method
        # 0b. What does current mode think it needs to be?
        # (Someday we might distinguish modes that constrain this,
        #  vs modes that change to fit it or to fit the actual selection.
        #  For now we only handle modes that change to fit the actual selection.) 
        selwhat_from_mode = None # most modes don't care
        if isinstance( mode, SelectChunks_Command):
            # TODO: replace this by a method call or getattr on mode
            selwhat_from_mode = SELWHAT_CHUNKS
        #bruce 060403 commenting out the following, in advance of proposed removal of Select Atoms mode entirely:
##        elif isinstance( mode, SelectAtoms_Command) and mode.commandName == SelectAtoms_Command.commandName:
##            #bruce 060210 added commandName condition to fix bug when current mode is Build (now a subclass of Select Atoms)
##            selwhat_from_mode = SELWHAT_ATOMS
        change_mode_to_fit = (selwhat_from_mode is not None) # used later; someday some modes won't follow this
        # 0c. What does current selection itself think it needs to be?
        # (If its desires are inconsistent, complain and fix them.)
        if assy.selatoms and assy.selmols:
            if debug_flags.atom_debug:
                #bruce 060210 made this debug-only, since what it reports is not too bad, and it happens routinely now in Build mode
                # if atoms are selected and you then select a chunk in MT
                print "atom_debug: bug, fyi: there are both atoms and chunks selected. Deselecting some of them to fit current mode or internal code."
            new_selwhat_influences = ( selwhat_from_mode, selwhat) # old mode has first say in this case, if it wants it
            #e (We could rewrite this (equivalently) to just use the other case with selwhat_from_sel = None.)
        else:
            # figure out what to do, in this priority order: actual selection, old mode, internal code.
            if assy.selatoms:
                selwhat_from_sel = SELWHAT_ATOMS
            elif assy.selmols:
                selwhat_from_sel = SELWHAT_CHUNKS
            else:
                selwhat_from_sel = None
            new_selwhat_influences = ( selwhat_from_sel, selwhat_from_mode, selwhat)
            if selwhat_from_sel is not None and selwhat_from_sel != selwhat:
                # following code will fix this with no harm, so let's not consider it a big deal,
                # but it does indicate a bug -- so just print a debug-only message.
                # (As of 050519 740pm, we get this from the jig cmenu command "select this jig's atoms"
                #  when the current mode is more compatible with selecting chunks. But I think this causes
                #  no harm, so I might as well wait until we further revise selection code to fix it.)
                if debug_flags.atom_debug:
                    print "atom_debug: bug, fyi: actual selection (%s) inconsistent " \
                          "with internal variable for that (%s); will fix internal variable" % \
                          (SELWHAT_NAMES[selwhat_from_sel], SELWHAT_NAMES[selwhat])
        # Let the strongest (first listed) influence, of those with an opinion,
        # decide what selmode we'll be in now, and make everything consistent with that.
        for opinion in new_selwhat_influences:
            if opinion is not None:
                # We have our decision. Carry it out (on mode, selection, and assy.selwhat) and return.
                selwhat = opinion
                if change_mode_to_fit and selwhat_from_mode != selwhat:
                    #bruce 050520 fix bug 644 by only doing this if needed (i.e. if selwhat_from_mode != selwhat).
                    # Without this fix, redundantly changing the mode using these tool buttons
                    # immediately cancels (or completes?) any node-renaming-by-dblclick
                    # right after it gets initiated (almost too fast to see).
                    if selwhat == SELWHAT_CHUNKS:
                        win.toolsSelectMolecules()
                        print "fyi: forced mode to Select Chunks" # should no longer ever happen as of 060403 
                    elif selwhat == SELWHAT_ATOMS:
                        win.toolsBuildAtoms() #bruce 060403 change: toolsSelectAtoms -> toolsBuildAtoms
                        ## win.toolsSelectAtoms() #bruce 050504 making use of this case for the first time; seems to work
                # that might have fixed the following too, but never mind, we'll just always do it -- sometimes it's needed.
                if selwhat == SELWHAT_CHUNKS:
                    part.unpickatoms()
                    assy.set_selwhat(SELWHAT_CHUNKS)
                elif selwhat == SELWHAT_ATOMS:
                    if assy.selmols: # only if needed (due to a bug), since this also desels Groups and Jigs
                        # (never happens if no bug, since then the actual selection has the strongest say -- as of 050519 anyway)
                        part.unpickparts()
                    assy.set_selwhat(SELWHAT_ATOMS) # (this by itself does not deselect anything, as of 050519)
                return
        assert 0, "new_selwhat_influences should not have ended in None: %r" % (new_selwhat_influences,)
        # scratch comments:
        # if we had been fixing selwhat in the past, it would have fixed bug 500 in spite of permit_pick_parts in cm_hide/cm_unhide.
        # So why aren't we? let's find out with some debug code... (now part of the above, in theory)
        return

    def resetAssy_and_clear(self): #bruce 050201 for Alpha, part of Huaicai's bug 369 fix
        """
        This method should be called from the end of MWsemantics._make_and_init_assy
        to prevent a crash on (at least) Windows during File->Close when the mtree is
        editing an item's text, using a fix developed by Huaicai 050201,
        which is to run the QListView method self.clear().
           Neither Huaicai nor Bruce yet understands why this fix is needed or why
        it works, so the details of what this method does (and when it's called,
        and what's it's named) might change. Bruce notes that without this fix,
        MWsemantics._make_and_init_assy would change win.assy (but not tell the mt (self) to change
        its own .assy) and call mt_update(), which in old code would immediately do
        self.clear() but in new code doesn't do it until later, so this might relate
        to the problem. Perhaps in the future, mt_update itself can compare self.assy
        to self.win.assy and do this immediate clear() if they differ, so no change
        would be needed to MWsemantics._make_and_init_assy(), but for now, we'll just do it
        like this.
        """
        self.modelTreeGui.update_item_tree( unpickEverybody = True )
        # prevents Windows crash if an item's text is being edited in-place
        # [huaicai & bruce 050201 for Alpha to fix bug 369; not sure how it works]
        return

    def mt_update(self):
        # note: bruce 070509 changed a lot of calls of self.modelTreeGui.mt_update to call self.mt_update.
        # note: bruce 070511 removed all direct sets here of mt_update_needed, since mt_update now sets it.
        return self.modelTreeGui.mt_update()

    def repaint_some_nodes(self, nodes): #bruce 080507, for cross-highlighting
        self.modelTreeGui.repaint_some_nodes(nodes)
        return
    
    def setMinimumSize(self, h, w):
        return self.modelTreeGui.setMinimumSize(h, w)
    
    def setMaximumWidth(self, w): #k might not be needed
        return self.modelTreeGui.setMaximumWidth(w)
    
    def setColumnWidth(self, column, w):
        return self.modelTreeGui.setColumnWidth(column, w)
    
    def setGeometry(self, w, h): #k might not be needed
        return self.modelTreeGui.setGeometry(QtCore.QRect(0,0,w,h))

    # callbacks from self.modelTreeGui to help it update the display
    
    def get_topnodes(self):
        self.assy = self.win.assy #k need to save it like this?
        self.assy.tree.name = self.assy.name
            #k is this still desirable, now that we have PartGroup
            # so it's no longer needed for safety?
        self.assy.kluge_patch_toplevel_groups( assert_this_was_not_needed = True)
            # fixes Group subclasses of assy.shelf and assy.tree, and
            # [not anymore, as of some time before 050417] inserts assy.viewdata.members into assy.tree
        self.tree_node, self.shelf_node = self.assy.tree, self.assy.shelf
        topnodes = [self.assy.tree, self.assy.shelf]
        if _debug_preftree: #bruce 050602
            try:
                from foundation.Utility import Node
                ## print "reloading prefsTree"
                import model.prefsTree as _X
                reload(_X)
                from model.prefsTree import prefsTree # constructor for an object which has a tree of nodes and controls them
                self.pt = prefsTree(self.assy) # guess; guessing it's ok to remake it each time
                ptnode = self.pt.topnode
                assert ptnode is not None
                assert isinstance(ptnode, Node)
                topnodes.append(ptnode)
            except:
                print_compact_traceback("error importing prefsTree or making one: ")
        return topnodes

    def get_nodes_to_highlight(self): #bruce 080507
        """
        Return a dictionary of nodes which should be drawn as highlighted right now.
        (The keys are those nodes, and the values are arbitrary.)
        """
        if not pref_show_highlighting_in_MT():
            return {}
        glpane = self.win.glpane
        nodes_containing_selobj = glpane.get_nodes_containing_selobj()
            # note: can contain duplicate nodes
        topnodes = self.get_topnodes()
            # these happen to be the nodes we consider to be
            # too high in the tree to show highlighted
            # (at least when the highlighting comes from
            #  them containing glpane.selobj -- for mouseover
            #  of these nodes in MT iself, we'd still show them
            #  as highlighted, once that's implemented)
        res = {}
        for node in nodes_containing_selobj:
            if not node in topnodes:
                res[node] = True
        return res
    
    def get_current_part_topnode(self): #bruce 070509 added this to the API
        return self.win.assy.part.topnode
    
##    def node_to_item(self, node):
##        return self.modelTreeGui.item_to_node_dict.get(node, None)
##            #bruce 070503 comment: likely ###BUG, should use node_to_item_dict -- but this is not called anywhere!
##            # (Where was it called in Qt3?)

    def open_clipboard(self): #bruce 050108, probably temporary
        ###REVIEW: do we need the effect that's disabled here?
        if 0:
            # self.toggle_open( self.shelf_item, openflag = True)  # what we did in Qt 3
            # shelf_item should be the item for the self.assy.shelf node
            shelf_item = self.modelTreeGui.item_to_node_dict[self.assy.shelf]
                #bruce 070503 comment: likely ###BUG, should use node_to_item_dict -- that explains the KeyError...
                # update, bruce 070531: node_to_item_dict and/or node_to_item are not part of modelTreeGui API
                # (or at least are no longer part of it if they were) and are not present in the new implem.
                # They could be added back, but "items" are internal to the MT so that would probably be misguided.
            # typically that gives a KeyError
            self.toggle_open(shelf_item, openflag = True)
            # toggle_open is defined in TreeView.py in the Qt 3 code
        if False:
            qt4here(show_traceback = True)
            def grep_dash_il(str, substr):
                str = str.upper()
                substr = substr.upper()
                try:
                    str.index(substr)
                    return True
                except ValueError:
                    return False
            print filter(lambda x: grep_dash_il(x, "mmkit"), dir(self.win))
        return

    def post_update_topitems(self): ###REVIEW: is this still needed?
        self.tree_item, self.shelf_item = self.topitems[0:2] # ignore 3rd element (prefsTree when that's enabled)
            # the actual items are different each time this is called
            ###@@@ as of 050602 the only uses of these are:
            # tree_item, in some debug code in TreeView;
            # shelf_item, in our open_clipboard method.
            ##e so I should replace those with something else and remove these.

    ############################################################
    # Everything else in this class is context menu stuff
    
    def make_cmenuspec_for_set(self, nodeset, optflag): # [see also the term Menu_spec]
        """
        #doc... see superclass docstring
        """
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
            res = [('Model Tree (nothing selected)',noop,'disabled')]
            #bruce 050505 adding some commands here (cm_delete_clipboard is a just-reported NFR from Mark)
            res.append(( 'Create new empty clipboard item', self.cm_new_clipboard_item ))
            lenshelf = len(self.assy.shelf.members) # FIX - use MT_kids?
            if lenshelf:
                if lenshelf > 2:
                    text = 'Delete all %d clipboard items' % lenshelf
                else:
                    text = 'Delete all clipboard items'
                res.append(( text, self.cm_delete_clipboard ))
            return res

        res = []

        # first put in a Hide item, checked or unchecked. But what if the hidden-state is mixed?
        # then there is a need for two menu commands! Or, use the command twice, fully hide then fully unhide -- not so good.
        # Hmm... let's put in Hide (with checkmark meaning "all hidden"), then iff that's not enough, Unhide.
        # So how do we know if a node is hidden -- this is only defined for leaf nodes now!
        # I guess we figure it out... I guess we might as well classify nodeset and its kids.
        # [update, bruce 080108/080306: does "and its kids" refer to members, or MT_kids?
        #  It might be some of each -- we would want to include members present but not shown
        #  in the MT (like the members of DnaGroup or DnaStrand), which are in members but not in
        #  MT_kids, but we might also want to cover "shared members", like DnaStrandChunks,
        #  which *might* be included in both strands and segments for this purpose (in the future;
        #  shared members are NIM now).]
        
        allstats = statsclass()
        
        for node in nodeset:
            node_stats = statsclass()
            node.apply2all( lambda node1: _accumulate_stats( node1, node_stats) )
            allstats += node_stats # totals to allstats

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
                
                from model.jigs_planes import RectGadget    # Try to remove this menu item. [Huaicai 10/11/05]
                if not isinstance(jig, RectGadget): #raise  
                
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
        
        #Make some model tree context menus that are specific to group
        #Note that this context menu will appear only when there is exactly one 
        #group selected. This whole method needs to be refactored. 
        #One approach is to let a method on the node define its context menu. 
        #The common things such as hide/unhiding can still be done here. 
        #The method on the object class can then return the menu it needs. 
        #the only problem is order of the menu items. For now, a method
        #on group class is defined that is called below. ('res' simply extends
        #the list returned by this method) -- Ninad 2008-03-14
        if len(nodeset) == 1 and nodeset[0].is_group():
            group_specific_context_menu = nodeset[0].make_modeltree_context_menu()
            if group_specific_context_menu:
                res.extend(group_specific_context_menu)
            
        # Group command -- only ok for 2 or more subtrees of any Part,
        # or for exactly one clipboard item topnode itself if it's not already a Group.
        # [rules loosened by bruce 050419-050421]
        
        if optflag or len(nodeset) >= 2:
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

        offered_ungroup = False # modified below; used by other menu items farther below
        
        if len(nodeset) == 1 and nodeset[0].permits_ungrouping():
            # (this implies it's a group, or enough like one)
            node = nodeset[0]
            if node.is_block(): #bruce 080207; NEEDS REVIEW due to recent Block changes, 080318
                # then we probably should not be here... but in case we are:
                text = "Ungroup %s (unsupported)" % (node.__class__.__name__.split('.')[-1],)
                    # todo: put that into Node.classname_for_ModelTree()
            elif not node.members: #bruce 080207
                # [REVIEW: use MT_kids? same issue in many places in this file, as of 080306]
                text = "Remove empty Group"
            elif node.dad == self.shelf_node and len(node.members) > 1:
                # todo: "Ungroup into %d separate clipboard item(s)"
                text = "Ungroup into separate clipboard items" #bruce 050419 new feature (distinct text in this case)
            else:
                # todo: "Ungroup %d item(s)"
                text = "Ungroup"
            res.append(( text, self.cm_ungroup ))
            offered_ungroup = True
        else:
            res.append(( 'Ungroup', noop, 'disabled' ))

        # Remove all %d empty Groups (which permit ungrouping) [bruce 080207]
        count_holder = [0]
        def func(group, count_holder = count_holder):
            if not group.members and group.permits_ungrouping():
                count_holder[0] += 1 # UnboundLocalError when this was count += 1
        for node in nodeset:
            node.apply_to_groups(func) # note: this treats Blocks as leaves ### NEEDS REVIEW after Block changes circa 080318
        count = count_holder[0]
        if count == 1 and len(nodeset) == 1 and not nodeset[0].members:
            # this is about the single top selected node,
            # so it's redundant with the Ungroup command above
            # (and if that was not offered, this should not be either)
            pass
        elif count:
            res.append(( 'Remove all %d empty Groups' % count, self.cm_remove_empty_groups ))
                # lack of fix_plurals seems best here; review when seen
        else:
            pass

        ## res.append(None) # separator - from now on, add these at start of optional sets, not at end

        # Edit Properties command -- only provide this when there's exactly one thing to apply it to,
        # and it says it can handle it.
        ###e Command name should depend on what the thing is, e.g. "Part Properties", "Chunk Properties".
        # Need to add methods to return that "user-visible class name".
        res.append(None) # separator

        if debug_flags.atom_debug:
            if len(nodeset) == 1:
                res.append(( "debug._node =", self.cm_set_node ))
            else:
                res.append(( "debug._nodeset =", self.cm_set_node ))
        
        if len(nodeset) == 1 and nodeset[0].edit_props_enabled():
            res.append(( 'Edit Properties...', self.cm_properties ))
        else:
            res.append(( 'Edit Properties...', noop, 'disabled' )) # nim for multiple items
        
        #ninad 070320 - context menu option to edit color of multiple chunks
        if allstats.nchunks:
            res.append(("Edit Chunk Color...", self.cmEditChunkColor))
        if allstats.canShowOverlayText:
            res.append(("Show Overlay Text", self.cmShowOverlayText))
        if allstats.canHideOverlayText:
            res.append(("Hide Overlay Text", self.cmHideOverlayText))

        #bruce 070531 - rename node -- temporary workaround for inability to do this in MT, or, maybe we'll like it to stay
        if len(nodeset) == 1:
            node = nodeset[0]
            if node.rename_enabled():
                res.append(("Rename node...", self.cmRenameNode)) ##k should it be called node or item in this menu text?

        # subsection of menu (not a submenu unless they specify one)
        # for node-class-specific menu items, when exactly one node
        # (old way, based on methodnames that start with __CM;
        #  and new better way, using Node method ModelTree_context_menu_section)
        if len(nodeset) == 1:
            node = nodeset[0]
            submenu = []
            attrs = filter( lambda attr: "__CM_" in attr, dir( node.__class__ )) #e should do in order of superclasses
            attrs.sort() # ok if empty list
            #bruce 050708 -- provide a way for these custom menu items to specify a list of menu_spec options (e.g. 'disabled') --
            # they should define a method with the same name + "__options" and have it return a list of options, e.g. ['disabled'],
            # or [] if it doesn't want to provide any options. It will be called again every time the context menu is shown.
            # If it wants to remove the menu item entirely, it can return the special value (not a list) 'remove'.
            opts = {}
            for attr in attrs: # pass 1 - record menu options for certain commands
                if attr.endswith("__options"):
                    boundmethod = getattr( node, attr)
                    try:
                        lis = boundmethod()
                        assert type(lis) == type([]) or lis == 'remove'
                        opts[attr] = lis # for use in pass 2
                    except:
                        print_compact_traceback("exception ignored in %r.%s(): " % (node, attr))
                        pass
            for attr in attrs: # pass 2
                if attr.endswith("__options"):
                    continue
                classname, menutext = attr.split("__CM_",1)
                boundmethod = getattr( node, attr)
                if callable(boundmethod):
                    lis = opts.get(attr + "__options") or []
                    if lis != 'remove':
                        mitem = tuple([menutext.replace('_',' '), boundmethod] + lis)
                        submenu.append(mitem)
                elif boundmethod is None:
                    # kluge: None means remove any existing menu items (before the submenu) with this menutext!
                    res = filter( lambda text_cmd: text_cmd and text_cmd[0] != menutext, res ) # text_cmd might be None
                    while res and res[0] == None:
                        res = res[1:]
                    #e should also remove adjacent Nones inside res
                else:
                    assert 0, "not a callable or None: %r" % boundmethod
            if submenu:
                ## res.append(( 'other', submenu )) #e improve submenu name, ordering, location
                res.extend(submenu) # changed append to extend -- Mark and Bruce at Retreat 050621
            
            # new system, used in addition to __CM above (preferred in new code):
            # [bruce 080225]
            try:
                submenu = node.ModelTree_context_menu_section()
                assert submenu is not None # catch a likely possible error specifically
                assert type(submenu) is type([]) # it should be a menu_spec list
            except:
                print_compact_traceback("exception ignored in %r.%s() " \
                                        "or in checking its result: " % \
                                        (node, 'ModelTree_context_menu_section'))
                submenu = []
            if submenu:
                res.extend(submenu)
            pass

        # Customize command [bruce 050602 experiment -- unfinished and commented out ###@@@]
        # [later comment, bruce 050704: I think this was intended to suggest PrefsNodes applicable to the selected item or items,
        #  and to make them and group them with it. Or (later) to put up a dialog whose end result might be to do that.]
        # Provide this when all items are in the same group? no, any items could be grouped...
        # so for initial experiments, always provide it. If it's a submenu, the selected items might affect
        # what's in it, and some things in it might be already checkmarked if PrefsNodes are above them ... 
        # for very initial experiment let's provide it only for single items.
        # Do we ask them what can be customized about them? I guess so.
##unfinished...
##        if _debug_preftree and len(nodeset) == 1:
##            mspec = nodeset[0].customize_menuspec()
##            submenu = []
            

        # copy, cut, delete, maybe duplicate...
        # bruce 050704 revisions:
        # - these are probably ok for clipboard items; I'll enable them there and let them be tested there.
        # - I'll remove Copy when the selection only contains jigs that won't copy themselves
        #   unless some of their atoms are copied (which for now is true of all jigs).
        #   More generally (in principle -- the implem is not general), Copy should be removed
        #   when the selection contains nothing which makes sense to copy on its own,
        #   only things which make sense to copy only in conjunction with other things.
        #   I think this is equivalent to whether all the selected things would fail to get copied,
        #   when the copy command was run.
        # - I'll add Duplicate for single selected jigs which provide an appropriate method,
        #   and show it dimmed for those that don't.
        
        res.append(None) # separator

        # figure out whether Copy would actually copy anything.
        part = nodeset[0].part # the same for all nodes in nodeset
        from operations.ops_select import selection_from_part
        sel = selection_from_part(part, use_selatoms = False) #k should this be the first code to use selection_from_MT() instead?
        doit = False
        for node in nodeset:
            if node.will_copy_if_selected(sel, False):
                #wware 060329 added realCopy arg, False here (this is not a real copy, so do not issue a warning).
                #bruce 060329 points out about realCopy being False vs True that at this point in the code we don't
                # yet know whether the real copy will be made, and when we do, will_copy_if_selected
                # might like to be re-called with True, but that's presently nim. ###@@@
                # 
                # if this test is too slow, could inline it by knowing about Jigs here; but better to speed it up instead!
                doit = True
                break
        if doit:
            res.append(( 'Copy', self.cm_copy ))
        # For single items, add a Duplicate command and enable it if they support the method. [bruce 050704 new feature]
        # For now, hardly anything offers this command, so I'm changing the plan, and removing it (not disabling it)
        # when not available. This should be reconsidered if more things offer it.
        if len(nodeset) == 1:
            node = nodeset[0]
            try:
                method = node.cm_duplicate
                    # Warning 1: different API than self.cm_xxx methods (arg differs)
                    # or __CM_ methods (disabled rather than missing, if not defined).
                    # Warning 2: if a class provides it, no way for a subclass to stop
                    # providing it. This aspect of the API is bad, should be revised.
                assert callable(method)
            except:
                dupok = False
            else:
                dupok = True
            if dupok:
                res.append(( 'Duplicate', method ))
            else:
                pass ## res.append(( 'Duplicate', noop, 'disabled' ))
        # Cut (unlike Copy), and Delete, should always be ok.
        res.append(( 'Cut', self.cm_cut ))
        res.append(( 'Delete', self.cm_delete ))
        
        #ninad060816 added option to select all atoms of the selected chunks. 
        #I don't know how to handle a case when a whole grop is selected. So putting a condition allstats.nchunks == allstats.n
        #perhaps, I should unpick the groups while picking atoms? 
        if allstats.nchunks == allstats.n and allstats.nchunks : 
            res.append((fix_plurals("Select all atoms of %d chunk(s)" % allstats.nchunks), self.cmSelectAllAtomsInChunk))
        
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
                # (text searches for this code might like to find "Select this jig's" or "Select these jigs'")
                want_select_item = True #bruce 051208
                if allstats.njigs == 1:
                    jig = nodeset[0]
                
                    from model.jigs_planes import RectGadget    # Try to remove this menu item. [Huaicai 10/11/05]
                    if isinstance(jig, RectGadget):
                        ## return res  -- this 'return' was causing bug 1189 by skipping the rest of the menu, not just this item.
                        # Try to do something less drastic. [bruce 051208]
                        want_select_item = False
                    else:
                        natoms = len(nodeset[0].atoms)
                        myatoms = fix_plurals( "this jig's %d atom(s)" % natoms )
                else:
                    myatoms = "these jigs' atoms"
                if want_select_item:
                    res.append(('Select ' + myatoms, self.cm_select_jigs_atoms ))

##        ##e following msg is not true, since nodeset doesn't include selection under selected groups!
##        # need to replace it with a better breakdown of what's selected,
##        # incl how much under selected groups is selected. Maybe we'll add a list of major types
##        # of selected things, as submenus, lower down (with commands like "select only these", "deselect these").
##        
##        res.append(( fix_plurals("(%d selected item(s))" % len(nodeset)), noop, 'disabled' ))

        # for single items that have a featurename, add wiki-help command [bruce 051201]
        if len(nodeset) == 1:
            node = nodeset[0]
            from foundation.wiki_help import wiki_help_menuspec_for_object #e (will this func ever need to know which widget is asking?)
            ms = wiki_help_menuspec_for_object(node) # will be [] if this node should have no wiki help menu items
            if ms:
                res.append(None) # separator
                res.extend(ms)

        return res # from make_cmenuspec_for_set

    # Context menu handler functions [bruce 050112 renamed them; e.g. old name "hide" overrode a method of QWidget!]
    #
    # Note: these must do their own updates (win_update, gl_update, mt_update) as needed.
    
    def cm_hide(self):
        env.history.message("Hide: %d selected items or groups" % len(self.modelTreeGui.topmost_selected_nodes()))
        #####@@@@@ bruce 050517 comment: the following line (of unknown reason or date, but by me) causes bug 500;
        # that method was added 050125 and used in chunk.pick on same date, so adding it here must be then or later.
        # Let's see what happens if I remove it?
        ## self.assy.permit_pick_parts() #e should not be needed here, but see if it fixes my bugs ###@@@ #k still needed? if so, why?
        self.assy.Hide() # includes win_update
        
    def cm_unhide(self):
        env.history.message("Unhide: %d selected items or groups" % len(self.modelTreeGui.topmost_selected_nodes()))
        ## self.assy.permit_pick_parts() #e should not be needed here [see same comment above]
        self.assy.Unhide() # includes win_update

    def cm_set_node(self): #bruce 050604, for debugging
        import utilities.debug as debug
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        if len(nodeset) == 1:
            debug._node = nodeset[0]
            print "set debug._node to", debug._node
        else:
            debug._nodeset = nodeset
            print "set debug._nodeset to list of %d items" % len(debug._nodeset)
        return
    
    def cm_properties(self):
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        if len(nodeset) != 1:
            env.history.message("error: cm_properties called on no or multiple items")
                # (internal error, not user error)
        else:
            node = nodeset[0]
            #UM 20080730: if its a protein chunk, enter build protein mode
            if hasattr(node, 'isProteinChunk') and node.isProteinChunk():
                res = node.protein.edit(self.win)
            else:
                res = node.edit() #e rename method!
            if res:
                env.history.message(res) # added by bruce 050121 for error messages
            else:
                self.win.win_update()
        return

    def cm_group(self): # bruce 050126 adding comments and changing behavior; 050420 permitting exactly one subtree
        """
        put the selected subtrees (one or more than one) into a new Group (and update)
        """
        ##e I wonder if option/alt/middleButton should be like a "force" or "power" flag
        # for cmenus; in this case, it would let this work even for a single element,
        # making a 1-item group. That idea can wait. [bruce 050126]
        #bruce 050420 making this work inside clipboard items too
        # TEST if assy.part updated in time ####@@@@ -- no, change to selgroup!
        sg = self.assy.current_selgroup()
        node = sg.hindmost() # smallest nodetree containing all picked nodes 
        if not node:
            env.history.message("nothing selected to Group") # should never happen
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
                env.history.message("made new group %s" % newtop.name) ###k see if this looks ok with autogenerated name
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
        new = Group(gensym("Group", node.assy), node.assy, node) # was self.assy
        assert not new.picked

        # put it where we want it -- before the first node member-tree with anything picked in it
        for m in node.members:
            if m.haspicked():
                assert m != new
                ## node.delmember(new) #e (addsibling ought to do this for us...) [now it does]
                m.addsibling(new, before = True)
                break # (this always happens, since something was picked under node)
        node.apply2picked(lambda(x): x.moveto(new))
            # this will have skipped new before moving anything picked into it!
            # even so, I'd feel better if it unpicked them before moving them...
            # but I guess it doesn't. for now, just see if it works this way... seems to work.
            # ... later [050316], it evidently does unpick them, or maybe delmember does.
        msg = fix_plurals("grouped %d item(s) into " % len(new.members)) + "%s" % new.name
        env.history.message( msg)

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
        self.win.glpane.gl_update() #k needed? (e.g. for selection change? not sure.)
        self.mt_update()
        return
    
    def cm_ungroup(self):
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        assert len(nodeset) == 1 # caller guarantees this
        node = nodeset[0]
        assert node.permits_ungrouping() # ditto
        need_update_parts = []
        pickme = None
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
            #bruce 050528 addendum: it's not handled well enough, so try this: hmm, it's not enough! try adding pickme too... ###@@@
            if len(node.members) == 1 and node.part.topnode is node:
                node.part.topnode = pickme = node.members[0]
        if node.is_top_of_selection_group() and len(node.members) > 1:
            msg = "splitting %r into %d new clipboard items" % (node.name, len(node.members))
        else:
            msg = fix_plurals("ungrouping %d item(s) from " % len(node.members)) + "%s" % node.name
        env.history.message( msg)
        node.ungroup()
        # this also unpicks the nodes... is that good? Not really, it'd be nice to see who they were,
        # and to be consistent with Group command, and to avoid a glpane redraw.
        # But it's some work to make it pick them now, so for now I'll leave it like that.
        # BTW, if this group is a clipboard item and has >1 member, we couldn't pick all the members anyway!
        #bruce 050528 addendum: we can do it in this case, temporarily, just to get selgroup changed:
        if pickme is not None:
            pickme.pick() # just to change selgroup (too lazy to look up the official way to only do that)
            pickme.unpick() # then make it look the same as for all other "ungroup" ops
        #e history.message?
        for assy in need_update_parts:
            assy.update_parts() # this should break new inter-part bonds
        self.win.glpane.gl_update() #k needed? (e.g. for selection change? not sure. Needed if inter-part bonds break!)
        self.mt_update()
        return

    def cm_remove_empty_groups(self): #bruce 080207
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        empties = []
        def func(group):
            if not group.members and group.permits_ungrouping():
                empties.append(group)
        for node in nodeset:
            node.apply_to_groups(func) # note: this treats Blocks as leaves ### NEEDS REVIEW after Block changes circa 080318
        for group in empties:
            group.kill()
        msg = fix_plurals("removed %d empty Group(s)" % len(empties))
        env.history.message( msg)
        self.mt_update()
        return
    
    # copy and cut and delete are doable by tool buttons
    # so they might as well be available from here as well;
    # anyway I tried to fix or mitigate their bugs [bruce 050131]:
    
    def cm_copy(self):
        self.assy.copy_sel(use_selatoms = False) # does win_update
    
    def cm_cut(self):
        self.assy.cut_sel(use_selatoms = False) # does win_update
    
    def cm_delete(self): # renamed from cm_kill which was renamed from kill
        # note: this is now the same code as MWsemantics.killDo. [bruce 050131]
        self.assy.delete_sel(use_selatoms = False) #bruce 050505 don't touch atoms, to fix bug (reported yesterday in checkin mail)
        ##bruce 050427 moved win_update into delete_sel as part of fixing bug 566
        ##self.win.win_update()
        
    def cmSelectAllAtomsInChunk(self): #Ninad060816
        """
        Selects all the atoms preseent in the selected chunk(s)
        """
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        self.assy.part.permit_pick_atoms()
        for m in nodeset:
            for a in m.atoms.itervalues():
                a.pick()
        self.win.win_update()
    
    def cmEditChunkColor(self): #Ninad 070321
        """
        Edit the color of the selected chunks using the Model Tree context menu
        """         
        from widgets.widget_helpers import RGBf_to_QColor
        
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        chunkList = []
        #Find the chunks in the selection and store them temporarily
        for m in nodeset:
            if isinstance(m, Chunk):
                chunkList.append(m)
        #Following selects the current color of the chunk 
        #in the QColor dialog. If multiple chunks are selected, 
        #it simply sets the selected color in the dialog as 'white'
        if len(chunkList) == 1:
            m = chunkList[0]            
            if m.color:
                m_QColor =  RGBf_to_QColor(m.color)
            else:
                m_QColor = None
               
            self.win.dispObjectColor(initialColor = m_QColor)
        else:         
            self.win.dispObjectColor()

    def cmShowOverlayText(self):
        """
        Context menu entry for chunks.  Turns on the showOverlayText
        flag in each chunk which has overlayText in some of its atoms.
        """
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        for m in nodeset:
            if isinstance(m, Chunk):
                m.showOverlayText = True

    def cmHideOverlayText(self):
        """
        Context menu entry for chunks.  Turns off the showOverlayText
        flag in each chunk which has overlayText in some of its atoms.
        """
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        for m in nodeset:
            if isinstance(m, Chunk):
                m.showOverlayText = False
        

    def cmRenameNode(self): #bruce 070531
        """
        Put up a dialog to let the user rename the selected node. (Only one node for now.)
        """
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        assert len(nodeset) == 1 # caller guarantees this
        node = nodeset[0]
        self.modelTreeGui.rename_node_using_dialog( node) # note: this checks node.rename_enabled() first
        return
    
    def cm_disable(self): #bruce 050421
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        assert len(nodeset) == 1 # caller guarantees this
        node = nodeset[0]
        jig = node # caller guarantees this is a jig; if not, this silently has no effect
        jig.set_disabled_by_user_choice( True) # use Node method as part of fixing bug 593 [bruce 050505]
        self.win.win_update()

    def cm_enable(self): #bruce 050421
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        assert len(nodeset) == 1, "len nodeset should be 1, but nodeset is %r" % nodeset
        node = nodeset[0]
        jig = node
        jig.set_disabled_by_user_choice( False)
        self.win.win_update()

    def cm_select_jigs_atoms(self): #bruce 050504
        nodeset = self.modelTreeGui.topmost_selected_nodes()
        otherpart = {} #bruce 050505 to fix bug 589
        did_these = {}
        nprior = len(self.assy.selatoms)
        for jig in nodeset:
            assert isinstance( jig, Jig) # caller guarantees they are all jigs
            # If we didn't want to desel the jig, I'd have to say:
                # note: this does not deselect the jig (good); and permit_pick_atoms would deselect it (bad);
                # so to keep things straight (not sure this is actually needed except to avoid a debug message),
                # just set SELWHAT_ATOMS here; this is legal because no chunks are selected. Actually, bugs might occur
                # in which that's not true... I forget whether I fixed those recently or only analyzed them (due to delays
                # in update event posting vs processing)... but even if they can occur, it's not high-priority to fix them,
                # esp since selection rules might get revised soon.
                ## self.assy.set_selwhat(SELWHAT_ATOMS)
            # but (I forgot when I wrote that) we *do* desel the jig,
            # so instead I can just say:
            self.assy.part.permit_pick_atoms() # changes selwhat and deselects all chunks, jigs, and groups
            # [bruce 050519 8pm]
            for atm in jig.atoms:
                if atm.molecule.part == jig.part:
                    atm.pick()
                    did_these[atm.key] = atm
                else:
                    otherpart[atm.key] = atm
            ## jig.unpick() # not done by picking atoms [no longer needed since done by permit_pick_atoms]
        msg = fix_plurals("Selected %d atom(s)" % len(did_these)) # might be 0, that's ok
        if nprior: #bruce 050519
            #e msg should distinguish between atoms already selected and also selected again just now,
            # vs already and not now; for now, instead, we just try to be ambiguous about that
            msg += fix_plurals(" (%d atom(s) remain selected from before)" % nprior)
        if otherpart:
            msg += fix_plurals(" (skipped %d atom(s) which were not in this Part)" % len(otherpart))
            msg = orangemsg(msg) # the whole thing, I guess
        env.history.message(msg)
        self.win.win_update()
        # note: caller (which puts up context menu) does self.update_select_mode(); we depend on that.
        return

    def cm_new_clipboard_item(self): #bruce 050505
        name = self.assy.name_autogrouped_nodes_for_clipboard( [] ) # will this end up being the part name too? not sure... ###k
        self.assy.shelf.addchild( Group(name, self.assy, None) )
        self.assy.update_parts()
        self.mt_update()

    def cm_delete_clipboard(self): #bruce 050505; docstring added 050602
        """
        Delete all clipboard items
        """
        ###e get confirmation from user?
        for node in self.assy.shelf.members[:]:
            node.kill() # will this be safe even if one of these is presently displayed? ###k
        self.mt_update()
    
    pass # end of class modelTree

# end
