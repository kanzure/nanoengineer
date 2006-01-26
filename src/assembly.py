# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.

"""
assembly.py -- provides class assembly, for everything stored in one file,
including one main part and zero or more clipboard items; see also part.py.

$Id$

==

About the assembly and Part classes, and their relationship:

[###@@@ warning, 050309: docstring not reviewed recently]

Each assembly has a set of Parts, of which one is always "current"; the current part
is what is displayed in the glpane and operated on by most operations,
and (for now, as of 050222) the assy attributes selmols, selatoms, and molecules
always refer to the same-named attrs of the current Part. (In fact, many other
assy methods and attrs are either delegated to the current Part or have directly
become Part methods or been split into assy and Part methods.)

All selected objects (even atoms) must be in the current part;
the current part is changed by using the model tree to select something
in some other part. The main model is one part, and each clipboard item is another part.
It is not yet possible to form Groups of separate parts in the Clipboard,
but this might be added somehow in the future. For now, any Group in the clipboard
is necessarily a single Part (or inside one); each toplevel member of the clipboard
is exactly one separate Part.

Once several known bugs (like 371) are fixed, then bonds between parts will not be allowed
(since they would be bonds between atoms or jigs in different physical spaces),
and bonds that become "interspace bonds" (due to move or copy operations)
will be automatically broken, or will cause things to be placed into the same space
in order not to break them.

Note that all info in the assy relates either to its named file or to something
about the current mode (in the general sense of that term, not just the current assy.o.mode object);
but the assy's info relating to its named file is not all stored directly in that file --
some of it is stored in other files (such as movie files), and in the future, some of it
might be stored in files referred to from some object within one of its Parts.

==

Both Part and assembly might well be renamed. We don't yet know the best terms
with which to refer to these concepts, or even the exact ideal boundary between them in the code.

==

History: the Part/assembly distinction was introduced by bruce 050222
(though some of its functionality was anticipated by the "current selection group"
introduced earlier, just before Alpha-1). [I also rewrote this entire docstring then.]

The Part/assembly distinction is unfinished, particularly in how it relates to some modes and to movie files.

Prior history unclear; almost certainly originated by Josh.

bruce 050513-16 replaced some == with 'is' and != with 'is not', to avoid __getattr__
on __xxx__ attrs in python objects.

bruce 050913 used env.history in some places.
"""

###@@@ Note: lots of old code below has been commented out for the initial
# assy/part commit, to help clarify what changed in viewcvs,
# but will be removed shortly thereafter.
# Also, several functions will be moved between files after that first commit
# but have been kept in the same place before then for the benefit of viewcvs diff.

from Numeric import *
from VQT import *
from string import *
import re
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from struct import unpack

from chem import *
from movie import *
from jigs import *
from jig_Gamess import *
from Utility import *
from HistoryWidget import greenmsg, redmsg
from platform import fix_plurals
import platform
import env
from undo_mixin import GenericDiffTracker_API_Mixin #bruce 051013
from debug import print_compact_stack


debug_assy_changes = 0 #bruce 050429

if 1: #bruce 060124 debug code; safe but dispensable ######@@@@@@
    import undo_archive
    debug_assy_changes = debug_assy_changes or undo_archive.debug_undo2

from part import Part # (this must come after the SELWHAT constants, in constants.py)

assy_number = 0 # count assembly objects [bruce 050429]

_assy_owning_win = None #bruce 060122; assumes there's only one main window; probably needs cleanup

class assembly(GenericDiffTracker_API_Mixin):
    """#doc
    """

    # default values of some instance variables
    _change_counter = 0 #bruce 060121-23; sometimes altered by self.changed() (even if self._modified already set)
    
    def __init__(self, win, name = None):
        # ignore changes to this assembly during __init__, and after it,
        # until the client code first calls our reset_changed method.
        # [bruce 050429 revised that behavior and this comment, re bug 413]
        self._modified = 1 
        
        # the MWsemantics displaying this assembly (or None, when called from ThumbView)
        self.w = win
        # self.mt = win.modelTreeView
        # self.o = win.glpane
        #  ... done in MWsemantics to avoid a circularity
        
        # the name if any
        self.name = name or gensym("Assembly")

        #bruce 050429
        global assy_number
        assy_number += 1
        self._debug_name = self.name + "-%d" % assy_number

        if self.w: # i.e. not when called from ThumbView to make its "dummy assembly"
            global _assy_owning_win
            if _assy_owning_win is not None:
                _assy_owning_win.deinit() # make sure assys don't fight over control of main menus, etc [bruce 060122]
            _assy_owning_win = self
            
            #bruce 051005: create object for tracking changes in our model, before creating any
            # model objects (ie nodes for tree and shelf). Since this is not initially used except
            # to record changes as these objects are created, the fact that self is still incomplete 
            # (e.g. lacks important attributes like tree and root and part) should not matter. [#k I hope]
            import undo_manager
            menus = (win.editMenu,) # list of menus containing editUndo/editRedo actions (for aboutToShow signal) [060122]
            self.undo_manager = undo_manager.AssyUndoManager(self, menus) # be sure to call init1() on this within self.__init__!
                # fyi: this sets self._u_archive for use by our model objects when they report changes
                # (but its name and value are private to AssyUndoManager's API for our model objects,
                #  which is why we don't set it here)
        
        # the Clipboard... this is replaced by another one later (of a different class),
        # once or twice each time a file is opened. ####@@@@ should clean up
        self.shelf = Group("Clipboard", self, None, [])
        self.shelf.open = False

        # the model tree for this assembly
        self.tree = Group(self.name, self, None)

        # a node containing both tree and shelf (also replaced when a file is opened)
        ####@@@@ is this still needed, after assy/part split? not sure why it would be. ###k
        self.root = Group("ROOT", self, None, [self.tree, self.shelf])

        # bruce 050131 for Alpha:
        # For each assembly, maintain one Node or Group which is the
        # "current selection group" (the PartGroup or one of the
        # clipboard items), in which all selection is required to reside.
        #    It might sometimes be an out-of-date node, either a
        # former shelf item or a node from a previously loaded file --
        # not sure if these can happen, but "user beware".
        #    [As of 030510, we store it privately and check it in all uses.]
        #    Sometime after Alpha, we'll show this group in the glpane
        # and let operations (which now look at self.tree or self.molecules)
        # affect it instead of affecting the main model
        # (or having bugs whenever clipboard items are selected, as they
        # often do now).
        # bruce 050228 update: this is still used after assy/part split,
        # but some of the above comment has been done differently,
        # and this needs to be kept in sync with self.part. #doc sometime.
        self.init_current_selgroup() # must be re-called when self.tree is replaced

        # filename if this entire assembly (all parts) was read from a file
        self.filename = ""
        # what to select: 0=atoms, 2 = molecules
        # [bruce 050308 change: new code should use SELWHAT_ATOMS and SELWHAT_CHUNKS
        #  instead of hardcoded constants, and never do boolean tests of selwhat]
        #bruce 050517: as of now, self.selwhat should only be set (other than by this init)
        # via self.set_selwhat(). [BTW, when we make a new assy and init this, are we sure it
        # always corresponds to the mode? Probably it does now only since we change to that mode
        # when opening files. #k]
        self.selwhat = SELWHAT_CHUNKS # initial value for new assy
        self._last_set_selwhat = self.selwhat
        
        #bruce 050131 for Alpha:
        from Utility import kluge_patch_assy_toplevel_groups
        kluge_patch_assy_toplevel_groups( self)
        self.update_parts() #bruce 050309 for assy/part split

        #bruce 050429 as part of fixing bug 413, no longer resetting self._modified here --
        # client code should call reset_changed instead, when appropriate.
        
        # the current version of the MMP file format
        # this is set in files_mmp.writemmpfile_assy. Mark 050130
        # [bruce 050325 comments: the code that sets it might be moved or renamed now;
        #  it's not clear to me what this means
        #  (eg if you read an old file does this indicate that old file's format?)
        #  or why it needs to be set here at all.]
        self.mmpformat = ''

        self.temperature = 300 # bruce 050325 have to put this back here for now

        # bruce 050325 revising Movie code for assy/part split and other reasons.
        # Now it works like this: there can be several active Movie objects,
        # but if one is playing or is the one to be played by default (e.g. the last one made),
        # then it's stored here in assy.current_movie; otherwise that's None. However, unlike before,
        # each movie object knows the alist which is correct for it (or, thinks it knows,
        #  since with old .dpb format it could easily be wrong unless we made it in this session),
        # and in principle old movies can be replayed (but only in the same session)
        # as long as their alist atoms still exist,
        # even if they've been reordered or new ones made, etc
        # (though we might enforce their being all in one Part, and later, add more conditions).
        # For movies made in prior sessions (actually it's worse -- made from prior opened files),
        # we still depend on our guess that the atom order is the same as in the current Part
        # when the moviefile is loaded, checked only by number of atoms. When we have new .dpb format
        # we can improve that.
        self.current_movie = None
            # before 050325 this was called self.m and was always the same Movie object (per assy)

        if debug_assy_changes:
            print "debug_assy_changes: creating", self
        
        # make sure these exist [bruce 050418]:
        assert self.tree
        assert self.tree.part
        assert self.tree.part.homeCsys
        assert self.tree.part.lastCsys

        if self.w:
            self.undo_manager.init1()
        
        return # from assembly.__init__

    def deinit(self): # make sure assys don't fight over control of main menus, etc [bruce 060122]
        ###e should this be extended into a full destroy method, and renamed? guess: yes. [bruce 060126]
        assert self.w # true for now, but not a fundamental requirement
        if self.w:
            self.undo_manager.deinit()
            #e more? forget self.w?? maybe someday, in case someone uses it now who should be using env.mainwindow()
        return
    
    #bruce 051031: keep counter of selection commands in assy (the model object), not Part,
    # to avoid any chance of confusion when atoms (which will record this as their selection time)
    # move between Parts (though in theory, they should be deselected then, so this might not matter).
    _select_cmd_counter = 0
    def begin_select_cmd(self):
        # Warning: same named method exists in assembly, GLPane, and ops_select, with different implems.
        # The best place to save this state is not clear, but probably it's a place that won't explicitly exist
        # until we restructure the code, since it's part of the "current selection" state, which in principle
        # should be maintained as its own object, either per-window or per-widget or per-model.
        # [bruce 051031]
        self._select_cmd_counter += 1
        return
    
    def set_selwhat(self, selwhat): #bruce 050517
        ## print_compact_stack( "set_selwhat to %r: " % (selwhat,))
        assert selwhat in (0,2) # i.e. (SELWHAT_ATOMS, SELWHAT_CHUNKS)
        if not self._last_set_selwhat == self.selwhat: # compare last officially set one to last actual one
            if platform.atom_debug: # condition is because cookiemode will do this, for now
                print_compact_stack( "atom_debug: bug: this failed to call set_selwhat, but set it directly, to %r:\n " \
                                     % (self.selwhat,) )
        self.selwhat = selwhat
        self._last_set_selwhat = self.selwhat
        return

    def construct_viewdata(self): #bruce 050418; this replaces old assy.data attribute for writing mmp files
        #bruce 050421: extend this for saving per-part views (bug 555)
        grpl1 = self.tree.part.viewdata_members(0)
        # Now grab these from the other parts too,
        # but store them in some other way which won't mess up old code which reads the file we'll write these into
        # (namely, as some new mmp record type which the old code would ignore)...
        # or just as a Csys with a name the old code will not store!
        # (This name comes from the argument we pass in.)
        partnodes = self.shelf.members # would not be correct to use self.topnodes_with_own_parts() here
        grpl1 = list(grpl1) # precaution, not needed for current implem as of 050421
        for i,node in zip(range(len(partnodes)),partnodes):
            ll = node.part.viewdata_members(i+1)
            grpl1.extend(ll)
        #bruce 050429 part of fix for bug 413: insulate self from misguided self.changed()
        # done when this Group is made.
        oldmod = self.begin_suspend_noticing_changes()
        res = Group("View Data", self, None, grpl1)
        self.end_suspend_noticing_changes(oldmod)
        return res

    def init_current_selgroup(self):
        self._last_current_selgroup = self.tree
        return

    next_clipboard_item_number = 1 # initial value of instance variable
    def name_autogrouped_nodes_for_clipboard(self, nodes, howmade = ""):
        """Make up a default initial name for an automatically made Group
        whose purpose is to keep some nodes in one clipboard item.
           The nodes in question might be passed, but this is optional
        (but you have to pass None or [] if you don't want to pass them),
        and they might not yet be in the clipboard, might not be the complete set,
        and should not be disturbed by this method in any way.
           A word or phrase describing how the nodes needing this group were made
        can also optionally be passed.
           Someday we might use these args (or anything else, e.g. self.filename)
        to help make up the name.
        """
        # original version: return "<Clipboard item>"
        # bruce 050418: to improve this and avoid the unfixed bug of '<' in names
        # (which mess up history widget's html),
        # I'll use "Clipboard item <n>" where n grows forever, per-file,
        # except that rather than storing it, I'll just look at the nodes now in the file,
        # and remember the highest one used while the file was loaded in the session.
        # (So saving and reloading the file will start over based on the numbers used in the file,
        #  which is basically good.)
        #e (Should I use a modtime instead (easier to implement, perhaps more useful)? No;
        #   instead, someday make that info available for *all* nodes in a 2nd MT column.)
        prefix = "Clipboard item" # permit space, or not, between this and a number, to recognize a number
        for node in self.shelf.members:
            name = node.name
            number = None
            if name.startswith(prefix):
                rest = name[len(prefix):].strip()
                if rest and rest.isdigit():
                    try:
                        number = int(rest)
                    except:
                        # can this happen (someday) for weird unicode digits permitted by isdigit? who knows...
                        print "ignoring clipboard item name containing weird digits: %r" % (name,)
                        number = None
            if number is not None and self.next_clipboard_item_number <= number:
                # don't use any number <= one already in use
                self.next_clipboard_item_number = number + 1
        res = "%s %d" % (prefix, self.next_clipboard_item_number)
        self.next_clipboard_item_number += 1 # also don't reuse this number in this session
        return res
    
    # == Parts

    prefs_node = None #bruce 050602; default value of instance variable; experimental
    
    def topnode_partmaker_pairs(self): #bruce 050602
        """Return a list of (node, partclass) pairs,
        for each node (in the tree of our nodes we'd display in a model tree)
        which should be at the top of its own Part of the specified Part subclass.
           The partclass might actually be any Part constructor with similar API
        to a Part subclass, though as of 050602 it's always a Part subclass.
           Return value is a mutable list owned by the caller (nothing will modify it
        unless caller does (more precisely, except via caller's reference to it)).
           Implem note: we don't ask the nodes themselves for the partclass,
        since it might depend on their position in the MT rather than on the nodetype.
        """
        from part import MainPart, ClipboardItemPart
        res = [(self.tree, MainPart)]
        for node in self.shelf.members:
            res.append(( node, ClipboardItemPart ))
        if self.prefs_node is not None:
            from prefsTree import MainPrefsGroupPart # this file might not be committed if this case doesn't run
            res.append(( self.prefs_node, MainPrefsGroupPart ))
        return res

    def topnodes_with_own_parts(self): #bruce 050602; should match topnode_partmaker_pairs
        res = [self.tree] + self.shelf.members
        if self.prefs_node is not None:
            res.append( self.prefs_node)
        return res
    
    def update_parts(self):
        """For every node in this assy, make sure it's in the correct Part (of the correct kind),
        creating new parts if necessary. [See also checkparts method.] 
        For now [050308], also break inter-Part bonds; later this might be done separately.
        """
        ###@@@ revise the following comment, it's just notes during development:
        # this is a simple brute-force scan, which might be good enough, and if so might be the simplest method that could work.
        # so if it works and seems ok to use whenever nodes change parts, then take care of entirely new nodes somehow (mol init),
        # and then just call this whenever needed... and it should be ok to add nodes to parts in addmember, when they're new
        # (and when dad has a part); and to do this to kids when groups with no parts are added to nodes with parts.
        # So only for a node-move must we worry and do it later... or so it seems, 050308 806pm.

        #bruce 050602 revised the following:
        for (node, part_constructor) in self.topnode_partmaker_pairs():
            self.ensure_one_part( node, part_constructor)
        
        # now all nodes have correct parts, so it's safe to break inter-part bonds.
        # in the future we're likely to do this separately for efficiency (only on nodes that might need it).
        partnodes = self.topnodes_with_own_parts() # do this again in case the nodes changed (though I doubt that can happen)
        for node in partnodes:
            # do this for all parts, even though the experimental prefsnode doesn't need it (as such)
            # (as a kluge, it might use it for smth else; if so, could #e rename the method and then say this is no longer a kluge)
            node.part.break_interpart_bonds()
            # note: this is not needed when shelf has no members, unless there are bugs its assertions catch.
            # but rather than not do it then, I'll just make it fast, since it should be able to be fast
            # (except for needing to recompute externs, but probably something else would need to do that anyway).
            # [bruce 050513] [####@@@@ review this decision later]
        # now make sure current_selgroup() runs without errors, and also make sure
        # its side effects (from fixing an out of date selgroup, notifying observers
        # of any changes (e.g. glpane)) happen now rather than later.
        sg = self.current_selgroup()
        # and make sure selgroup_part finds a part from it, too
        assert self.selgroup_part(sg)
        # 050519 new feature: since bonds might have been broken above (by break_interpart_bonds), do this too:
        ## self.update_bonds() #e overkill -- might need to be optimized
        env.post_event_updates() #bruce 050627 this replaces update_bonds
        return
    
    def ensure_one_part(self, node, part_constructor): #bruce 050420 revised this to help with bug 556; revised again 050527
        """Ensure node is the top node of its own Part, and all its kids are in that Part,
        either by verifying this situation, or creating a new Part just for node and its kids.
        Specifically:
           If node's part is None or not owned by node (ie node is not its own part's topnode),
        give node its own new Part using the given constructor (permitting the new part to copy some
        info from node's old part, like view attrs, if it wants to).
        (Class is not used if node already owns its Part.)
           If node's kids (recursively) are not in node's (old or new) part, add them.
        [But don't try to break inter-Part bonds, since when this is run,
         some nodes might still be in the wrong Part, e.g. when several nodes
         will be moved from one part to another.]
           We have no way to be sure node's old part doesn't have other nodes besides
        our node's recursive kids; caller can assure this by covering all nodes with some call
        of this method.
        """
        #bruce 050420: don't remove node from its old wrong part. Old code [revised 050516] was:
##        if node.part and node is not node.part.topnode: #revised 050513
##            # this happens, e.g., when moving a Group to the clipboard, and it becomes a new clipboard item
##            node.part.remove(node) # node's kids will be removed below
##            assert node.part is None
##        if node.part is None:
        if node.part is None or node.part.topnode is not node: # if node has no part or does not own its part (as its topnode)
            part1 = part_constructor(self, node) # make a new part with node on top -- uses node's old part (if any) for initial view
            assert node.part is part1 # since making the new part should have added node to it, and set node.part to it
            assert node is node.part.topnode
        # now make sure all node's kids (recursively) are in node.part
        addmethod = node.part.add
        node.apply2all( addmethod ) # noop for nodes already in part;
            # also auto-removes nodes from their old part, if any;
            # also destroys emptied parts.
        return

    # == Part-related debugging functions

    def checkparts(self):
        "make sure each selgroup has its own Part, and all is correct about them"
        # presumably this is only called when platform.atom_debug, but that's up to the caller
        for node in self.topnodes_with_own_parts():
            ## print "checking part-related stuff about node:" ,node
            #e print the above in an except clause, so on asfail we'd see it...
            try:
                assert node.is_top_of_selection_group() ##e rename node.is_selection_group()??
                assert node.part.topnode is node # this also verifies each node has a different part
                kids = []
                node.apply2all( kids.append ) # includes node itself
                for kid in kids:
                    assert kid.part is node.part
                assert node.part.nodecount == len(kids), "node.part.nodecount %d != len(kids) %d" % (node.part.nodecount, len(kids))
            except:
                print "exception while checking part-related stuff about node:", node, "in assy", self
                raise
        return

    # ==

    def draw(self, glpane): #bruce 050617 renamed win arg to glpane, and made submethod use it for the first time
        if platform.atom_debug:
            try:
                self.checkparts()
            except: #bruce 051227 catch exception in order to act more like non-atom_debug version
                print_compact_traceback("atom_debug: exception in checkparts; drawing anyway though this might not work: ")
                print_compact_stack("atom_debug: more info about that exception: self %r, glpane %r: " % (self, glpane))
        if glpane.special_topnode is not None:
            #bruce 050627 new feature, only used experimentally so far (mainly a kluge for old-mode-API compatibility)
            glpane.special_topnode.draw(glpane, glpane.display) #k 2nd arg might not be needed someday, but is needed for now
        elif self.part is not None: #k not None condition needed??
            self.part.draw(glpane)
        return
    
    # == current selection group (see it and/or change it)

    def current_selgroup_iff_valid(self):
        """If the current selection group, as stored (with no fixing!),
        is valid in all ways we can think of checking
        (except any ways related to Parts, which are not examined here),
        return it, otherwise return None (not an error).
        Never has side effects.
        """
        sg = self._last_current_selgroup
        if not self.valid_selgroup( sg):
            return None
        return sg

    def valid_selgroup(self, sg):
        """If the GIVEN (not current) selection group (with no fixing!)
        is valid in all ways we can think of checking
        (except ways related to its .part, which is not examined -- see selgroup_part for that)
        as a candidate for being or becoming our current selection group,
        then return True, otherwise False (not an error).
        Never has side effects.
        """
        if sg is None: return False
        if sg.assy is not self: return False
        if not sg.is_top_of_selection_group():
            return False
        if not (self.root.is_ascendant(sg) or self.prefs_node is sg): #bruce 050602 kluge: added prefs_node
            return False # can this ever happen??
        # I think we won't check the Part, even though it could, in theory,
        # be present but wrong (in the sense that sg.part.topnode is not sg),
        # since that way, this method can be independent of Parts,
        # and since is_top_of_selection_group should have been enough
        # for what this method is used for. Logically, we use this to see
        # the selgroup structure, but consider it lower-level than where we
        # know that each selgroup wants its own Part (and maintain that).
        return True

    def current_selgroup(self):
        """If the current selection group is valid as stored, return it.
        If not, try to fix it, choosing a new one which includes the stored one if possible
        (this situation might be normal after a DND move of a whole clipboard item
         into the inside of some other Part),
        or the main part (self.tree) if not (this might happen if some code deletes nodes
        without changing the selection group).
           Like current_selgroup_iff_valid(), ignore its Part; see selgroup_part for that.
        Also, new Parts are never made (or old Parts revised) in this method.
           If the current selgroup is changed, the new one is both returned and stored.
        """
        sg = self.current_selgroup_iff_valid()
        if sg is not None:
            return sg
        # now we're a bit redundant with that method (this seems necessary);
        # also, at this point we're almost certain to debug print and/or
        # to change self._last_current_selgroup (via self.set_current_selgroup ###k).
        sg = self._last_current_selgroup
        # since that guy was invalid, we'll definitely forget about it now
        # except for its use below as 'sg' (in this run of this method).
        self._last_current_selgroup = None # hopefully to be revised below
        if sg is not None and sg.assy is self and self.root.is_ascendant(sg):
            assert not sg.is_top_of_selection_group() # the only remaining way it could have been wrong
            # this is the one case where we use the invalid _last_current_selgroup in deciding on the new one.
            newsg = sg.find_selection_group() # might be None
            if newsg is None:
                newsg = self.tree
        else:
            newsg = self.tree
        # now newsg is the one we'll *try* to change to and return, if *it* is valid.
        # (if it is not None but not valid, that's probably a bug, and we won't change to it;
        #  ideally we'd change to self.tree then, but since it's probably a bug we won't bother.)
        if newsg is None:
            #k probably can't happen unless self.tree is None, which I hope never happens here
            if platform.atom_debug:
                print_compact_stack("atom_debug: cur selgroup None, no tree(?), should never happen: ")
            # we already stored None, and it's not good to call current_selgroup_changed now (I think) ##k
            return None
        # Note: set_current_selgroup looks at prior self._last_current_selgroup,
        # so the fact that we set that to None (above) is important.
        # Also, what if newsg is sg (should never happen here)?
        # Then it won't be valid (else we'd have returned at top of this method)
        # and we'll see debug prints in set_current_selgroup.
        self.set_current_selgroup( newsg) # this stores it and notifies observers if any (eg updates glpane)
        return self._last_current_selgroup # (this will be same as newsg, or debug prints already occurred)

    def selgroup_part(self, sg):
        """Given a valid selgroup sg (or None), check that it's its .part's topnode,
        and if so return its .part, and if not return None after emitting debug prints
        (which always indicates a bug, I'm 90% sure as I write it -- except maybe during init ###k #doc).
        """
        if sg is None or sg.part is None or sg.part.topnode is not sg:
            #doc: ... assy.tree.part being None.
            # (which might happen during init, and trying to make a part for it might infrecur or otherwise be bad.)
            # so if following debug print gets printed, we might extend it to check whether that "good excuse" is the case.
            if 0 and platform.atom_debug:
                print_compact_stack("atom_debug: fyi: selgroup.part problem during: ")
            if 1:
                # for now, always raise an exception #####@@@@@
                assert sg is not None
                assert sg.part is not None
                assert sg.part.topnode is not None
                assert sg.part.topnode is sg, "part %r topnode is %r should be %r" % (sg.part, sg.part.topnode, sg)
            return None
        return sg.part

    # ==
    
    def current_selgroup_index(self): #bruce 060125 so Undo can store "current part" w/o doing update_parts [guess; wisdom unreviewed]
        """Return the index of the current selgroup, where 0 means self.tree and 1, 2, etc refer to
        the clipboard items in their current positional order. [Note that this won't be useful for out-of-order redo.]
        """
        sg = self.current_selgroup()
        if sg is self.tree:
            return 0
        try:
            return self.shelf.members.index(sg) + 1
        except:
            print_compact_traceback("bug in current_selgroup_index, returning 0: ")
            return 0
        pass

    def selgroup_at_index(self, i): #bruce 060125 for Undo
        "Return the selection group at index i (0 means self.tree), suitable for passing to set_current_selgroup."
        if i == 0:
            return self.tree
        try:
            return self.shelf.members[i-1]
        except:
            print_compact_traceback("bug in selgroup_at_index(%d), returning self.tree: " % (i,) )
            return self.tree
        pass
    
    # == changing the current selection group

    ##e move this lower down?
    def fyi_part_topnode_changed(self, old_top, new_top):
        """[private method for a single caller in Part]
        Some Part tells us that its topnode changed from old_top to new_top.
        If our current selgroup happened to be old_top, make it now be new_top,
        but don't emit a history message about this change.
        [#e: not sure if we should do any unpicking or updating, in general;
         current caller doesn't need or want any.]
        """
        if self._last_current_selgroup is old_top:
            self._last_current_selgroup = new_top
            # no need (in fact, it would be bad) to call current_selgroup_changed, AFAIK
            # (does this suggest that "current part" concept ought to be more
            #  primitive than "current selgroup" concept??)
        # now the Part situation should be ok, no need for assy.update_parts
        return

    def set_current_part(self, part):
        self.set_current_selgroup( part.topnode)
    
    def set_current_selgroup(self, node): #bruce 050131 for Alpha; heavily revised 050315; might need options wrt history msg, etc
        "Set our current selection group to node, which should be a valid one. [public method; no retval]"
        assert node
        prior = self.current_selgroup_iff_valid() # don't call current_selgroup itself here --
            # it might try to "fix an out of date current selgroup"
            # and end up unpicking the node being passed to us.
        if node is prior:
            return # might be redundant with some callers, that's ok [#e simplify them?]
        if prior is None and self._last_current_selgroup:
            prior = 0 # tell submethod that we don't know the true prior one
        if not self.valid_selgroup(node):
            # probably a bug in the caller. Complain, and don't change current selgroup.
            if platform.atom_debug:
                print_compact_stack("atom_debug: bug: invalid selgroup %r not being used" % (node,))
            #e if this never happens, change it to raise an exception (ie just be an assert) ###@@@
            return
        #####@@@@@ now inline the rest
        # ok to set it and report that it changed.
        self._last_current_selgroup = node
        self.current_selgroup_changed(prior = prior) # as of 050315 this is the only call of that method
        return
    
    def current_selgroup_changed(self, prior = 0): #bruce 050131 for Alpha
        "#doc; caller has already stored new valid one; prior == 0 means unknown -- caller might pass None"
        #e in future (post-Alpha) this might revise self.molecules, what to show in glpane, etc
        # for now, make sure nothing outside it is picked!
        # This is the only place where that unpicking from changing selgroup is implemented. ###@@@ verify that claim

        sg = self._last_current_selgroup

        # unpick everything in a different selgroup (but save the message about this for last)
        didany = self.root.unpick_all_except( sg )

        # notify observers of changes to our current selgroup (after the side effect of the unpick!)
        self.o.set_part( self.part)
        ## done by that: self.o.gl_update()
        
        # print a history message about a new current Part, if possible #####@@@@@ not when initing to self.tree!
        try:
            # during init, perhaps lots of things could go wrong with this, so catch them all
            msg = "showing %r (%s)" % (sg.part.topnode.name, sg.part.location_name())
                # AttributeError: 'NoneType' object has no attribute 'topnode' ######@@@@@@
            ## this was too frequent to leave them all in, when clicking around the clipboard:
            ## env.history.message( greenmsg( msg)) ###e need option for this?
            env.history.message( msg, transient_id = "current_selgroup_changed")
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: bug?? or just init?: can't print changed-part msg: ")
            pass

        # emit a message about what we unpicked, if anything
        if didany:
            try: # precaution against new bugs in this alpha-bug-mitigation code
                # what did we deselect?
                # [note, prior might be None or 0, so boolean test is needed [bruce guess/comment 050516]]
                if prior and not isinstance(prior, Group):
                    what = node_name(prior)
                elif prior:
                    what = "some items in " + node_name(prior)
                else:
                    what = "some items"
                ## why = "since selection should not involve more than one clipboard item or part at a time" #e wording??
                why = "to limit selection to one clipboard item or the part" #e wording??
                    #e could make this more specific depending on which selection groups were involved
                msg = "Warning: deselected %s, %s" % (what, why)
            except:
                if platform.atom_debug:
                    raise 
                msg = "Warning: deselected some previously selected items"
            try:
                env.history.message( redmsg( msg))
            except:
                pass # too early? (can this happen?)

        return # from current_selgroup_changed

    # == general attribute code
    
    # attrnames to delegate to the current part
    # (ideally for writing as well as reading, until all using-code is upgraded) ###@@@ use __setattr__ ?? etc??
    part_attrs = ['molecules','selmols','selatoms','homeCsys','lastCsys']
    ##part_methods = ['selectAll','selectNone','selectInvert']###etc... the callable attrs of part class??
    part_methods = filter( lambda attr:
                             not attr.startswith('_')
                             and callable(getattr(Part,attr)), # note: this tries to get self.part before it's ready...
                          dir(Part) ) #approximation!
    #####@@@@@ for both of the following:
    part_attrs_temporary = ['bbox','center','drawLevel'] # temp because caller should say assy.part or be inside self.part
    part_attrs_review = ['ppa2','ppa3','ppm']
        ###@@@ bruce 050325 removed 'alist', now all legit uses of that are directly on Part or Movie
        ### similarly removed 'temperature' (now on assy like it was),'waals' (never used)
        #e in future, we'll split out our own methods for some of these, incl .changed
        #e and for others we'll edit our own methods' code to not call them on self but on self.assy (incl selwhat)
    part_attrs_all = part_attrs + part_attrs_temporary + part_attrs_review
    
    def __getattr__(self, attr):
        if attr.startswith('_'): # common case, be fast
            raise AttributeError, attr
        elif attr == 'part':
            sg = self.current_selgroup() # this fixes it if possible; should always be a node but maybe with no Part during init
            ## return self.parts[node_id(sg)]
#bruce 050528 removing this since it prevents clipboard from opening in MT once it's closed, when displaying a clipboard item!
##            if 1:
##                # open all containing nodes below assy.root (i.e. the clipboard, if we're a clipboard item)
##                containing_node = sg.dad
##                while containing_node is not None and containing_node is not self.root:
##                    containing_node.open = True
##                    containing_node = containing_node.dad
            part = self.selgroup_part(sg)
            if part is None:
                #e [this IS REDUNDANT with debug prints inside selgroup_part] [which for debugging are now asserts #####@@@@@]
                # no point in trying to fix it -- if that was possible, current_selgroup() did it.
                # if it has no bugs, the only problem it couldn't fix would be assy.tree.part being None.
                # (which might happen during init, and trying to make a part for it might infrecur or otherwise be bad.)
                # so if following debug print gets printed, we might extend it to check whether that "good excuse" is the case.
                if platform.atom_debug:
                    print_compact_stack("atom_debug: fyi: assy.part getattr finds selgroup problem: ")
                return None
            return part
        elif attr in self.part_attrs_all:
            # delegate to self.part
            try:
                part = self.part
            except:
                print "fyi: following exception getting self.part happened just before we looked for its attr %r" % (attr,)
                raise
            try:
                return getattr(part, attr) ###@@@ detect error of infrecur, since part getattr delegates to here??
            except:
                print "fyi: following exception in assy.part.attr was for attr = %r" % (attr,)
                raise
        elif attr in self.part_methods:
            # attr is a method-name for a method we should delegate to our current part.
            # it's not enough to return the current self.part's bound method...
            # we need to create and return a fake bound method of our own
            # which, when called in the future, will delegate to our .part *at that time* --
            # in case it is not called immediately, but stored away (e.g. as a menu item's callable)
            # and used later when our current part might have changed.
            def deleg(*args,**kws):
                meth = getattr(self.part, attr)
                return meth(*args,**kws)
            return deleg
        raise AttributeError, attr

    # == change-tracking [needs to be extended to be per-part or per-node, and for Undo]
    
    def has_changed(self):
        """Report whether this assembly (or something it contains)
        has been changed since it was last saved or loaded from a file.
        See self.changed() docstring and comments for more info.
        Don't use or set self._modified directly!
           #e We might also make this method query the current mode
        to see if it has changes which ought to be put into this assembly
        before it's saved.
        """
        return self._modified
    
    def changed(self):
        """Record the fact that this assembly (or something it contains)
        has been changed, in the sense that saving it into a file would
        produce meaningfully different file contents than if that had been
        done before the change.
           Note that some state changes (such as selecting chunks or atoms)
        affect some observers (like the glpane or model tree), but not what
        would be saved into a file; such changes should *not* cause calls to
        this method (though in the future there might be other methods for
        them to call, e.g. perhaps self.changed_selection() #e).
           [Note: as of 050107, it's unlikely that this is called everywhere
        it needs to be. It's called in exactly the same places where the
        prior code set self.modified = 1. In the future, this will be called
        from lower-level methods than it is now, making complete coverage
        easier. #e]
        """
        # bruce 050107 added this method; as of now, all method names (in all
        # classes) of the form 'changed' or 'changed_xxx' (for any xxx) are
        # hereby reserved for this purpose! [For beta, I plan to put in a
        # uniform system for efficiently recording and propogating change-
        # notices of that kind, as part of implementing Undo (among other uses).]

        if self._suspend_noticing_changes:
            return #bruce 060121 -- this changes effective implem of begin/end_suspend_noticing_changes; should be ok
        
        newc = env.change_counter_for_changed_objects() #bruce 060123
        
        if debug_assy_changes:
            oldc = self._change_counter
            print
            self.modflag_asserts()
            if oldc == newc:
                print "debug_assy_changes: self._change_counter remains", oldc
            else:
                print_compact_stack("debug_assy_changes: self._change_counter %d -> %d: " % (oldc, newc) )
            pass
        
        self._change_counter = newc
            ###e should optimize by feeding new value from changed children (mainly Nodes) only when needed
            ##e will also change this in some other routine which is run for changes that are undoable but won't set _modified flag

        if not self._modified:
            self._modified = 1
            # Feel free to add more side effects here, inside this 'if'
            # statement, even if they are slow! They will only run the first
            # time you modify this assembly since it was last saved, opened, or closed
            # (i.e. since the last call of reset_changed).

            # A long time ago, this is where we'd emit a history message about unsaved changes.
            # Now we denote a file change by adding an asterisk (or whatever the user prefers)
            # to the end of the filename in the window caption.
            self.w.update_mainwindow_caption_properly()
            if debug_assy_changes:
                import time
                print time.asctime(), self, self.name
                print_compact_stack("atom_debug: part now has unsaved changes")
            pass
        
        # If you think you need to add a side-effect *here* (which runs every
        # time this method is called, not just the first time after each save),
        # that would probably be too slow -- we'll need to figure out a different
        # way to get the same effect (like recording a "modtime" or "event counter").
        
        self.modflag_asserts() #e should speed-optimize this eventually
        
        return # from assembly.changed()

    def modflag_asserts(self): #bruce 060123; revised 060125
        "check invariants related to self._modified"
        if 1: ###@@@ maybe should be: if platform.atom_debug:
            hopetrue = ( (not self._modified) == (self._change_counter == self._change_counter_when_reset_changed) )
            if not hopetrue:
                print_compact_stack(
                    "bug? (%r.modflag_asserts() failed; %r %r %r): " % \
                      (self, self._modified, self._change_counter, self._change_counter_when_reset_changed)
                )
        return

    # Methods to toggle change-noticing during specific sections of code.
    # (These depend on assy._modified working as it did on 050109 - 050429;
    #  they'll need review when we add per-Part _modified flag, Undo, etc.)
    # [written by bruce 050110 as helper functions in Utility.py;
    #  renamed and moved here by bruce 050429, re bug 413]

    _suspend_noticing_changes = False
        #bruce 060121 for Undo; depends on proper matching and lack of nesting of following methods,
        # which looks true at the moment; see also use of this in self.changed(), which changes
        # effective implem of following methods.
    
    def begin_suspend_noticing_changes(self): #bruce 060121 revised implem, see comment above and in self.changed()
        """See docstring of end_suspend_noticing_changes."""
        assert not self._suspend_noticing_changes
        self._suspend_noticing_changes = True # this prevents self.changed() from doing much
        oldmod = self._modified
        self._modified = 1 # probably no longer needed as of 060121
        return oldmod # this must be passed to the 'end' function
        # also, if this is True, caller can safely not worry about
        # calling "end" of this, i suppose; best not to depend on that

    def end_suspend_noticing_changes(self, oldmod):
        """Call this sometime after every call of begin_suspend_noticing_changes.
        These begin/end pairs can be nested, but see the caveat below about the oldmod argument in that case.
           The argument should be the begin method's return value, unless you know you want the new situation
        to look "not modified", in which case the argument should be False.
        Note that even calls of self.reset_changed() (between the begin and end methods)
        are not noticed, so if one occurred and should have been noticed,
        this can only be fixed by passing False to this method.
           Caveat: with nested begin/end pairs, if an inner end's oldmod was False
        (instead of the "correct" value returned by its matching begin method),
        then changes after that inner end method *will* (incorrectly) be noticed.
        This is a bug in the present implementation which needs to be worked around.
        It might be inherent in the present API, I don't know; the present API has no
        protection for mismatch-bugs and needs revision anyway.
           It's probably safe even if the assembly object these methods are being called on
        is not the same for the begin and end methods!
        """ # docstring by bruce 050429 ; might be wrong due to changes of 060121
        assert self._suspend_noticing_changes
        self._suspend_noticing_changes = False
        self._modified = oldmod
        return

    _change_counter_when_reset_changed = -1 #bruce 060123 for Undo; as of 060125 it should no longer matter whether the value is even
    
    def reset_changed(self): # bruce 050107
        """[private method] #doc this... see self.changed() docstring...
        """
        #bruce 060123 assuming all calls are like File->Save call...
        # actual calls are from MWsem.__init__, File->Open,
        # File->Save (actually saved_main_file; does its own update_mainwindow_caption), File->Close
        if self._suspend_noticing_changes:
            print "warning, possible bug: self._suspend_noticing_changes is True during reset_changed" #bruce guess 060121
        if debug_assy_changes:
            print_compact_stack( "debug_assy_changes: %r: reset_changed: " % self )
        self._modified = 0
        #e should this call self.w.update_mainwindow_caption(Changed = False),
        # or fulfill a subs to do that?? [bruce question 060123]

        self._change_counter_when_reset_changed = self._change_counter #bruce 060125 (eve) revised this; related to bugs 1387, 1388??
            ## = env.change_counter_checkpoint() #bruce 060123 for Undo
            ##k not sure it's right to call change_counter_checkpoint and not subsequently call change_counter_for_changed_objects,
            # but i bet it's ok... more problematic is calling change_counter_checkpoint at all! #######@@@@@@@
            # the issue is, this is not actually a change to our data, so why are we changing self._change_counter??
            # OTOH, if just before saving we always changed our data just for fun, the effect would be the same, right?
            # Well, not sure -- what about when we Undo before... if we use this as a vers, maybe no diffs will link at it...
            # but why would they not? this is not running inside undo, but from an op that does changes like anything else does
            # (namely file save) (open or close is yet another issue since assy is replaced during the cmd ###@@@).
            # so i'm guessing it's ok. let's leave it in and find out. hmm, it might make it *look* like file->save did a change
            # and should be undoable -- but undoing it will have no effect. Really in order to make sure we know that diff
            # is empty, it would be better not to do this, or somehow to know there was no real change.
            # plan: zap the final '= env...' and revise modflag_asserts accordingly. worry about real changes for sure
            # changing counter even if they wouldn't... call checkpoint here even if not using value?!?!?!? #####@@@@@ 060124 230pm
        return

    def reset_changed_for_undo(self, change_counter ): #bruce 060123 guess; needs cleanup
        """External code (doing an Undo or Redo) has made our state like it was when self._change_counter was as given.
        Set self._change_counter to that value and update self._modified to match (using self._change_counter_when_reset_changed
        without changing it).
        """
        # in other words, treat self._change_counter as a varid_vers for our current state... ###@@@
        modflag = (self._change_counter_when_reset_changed != change_counter)
            #### ignores issue of undoable changes that are not saved (selection) or don't trigger save (view/part??)
        if debug_assy_changes:
            print_compact_stack( "debug_assy_changes for %r: reset_changed_for_undo(%r), modflag %r: " % (self,change_counter,modflag) )
        self._modified = modflag
        self._change_counter = change_counter
        self.modflag_asserts()
        #####@@@@@ need any other side effects of assy.changed()??
        if self.w:
            self.w.update_mainwindow_caption_properly()
        return
    
    # ==
    
    ## bruce 050308 disabling checkpicked for assy/part split; they should be per-part
    ## and they fix errors in the wrong direction (.picked is more fundamental)
    def checkpicked(self, always_print = 0):
        if always_print: print "fyi: checkpicked() is disabled until assy/part split is completed"
        return

    # ==

    def apply2movies(self, func): #bruce 050428
        "apply func to all possibly-ever-playable Movie objects we know about. (Not to mere sim-param-holders for minimize, etc.)"
        if self.current_movie:
            # for now, this is the only one! (even if it's a "mere param-holder".)
            # at some point there'll also be movie nodes in the MT...
            ##e when there can be more than one, perhaps catch exceptions here and/or "or" the retvals together...
            func( self.current_movie)
        return
    
    # ==

    def __str__(self):
        if platform.atom_debug:
            return "<Assembly of file %r" % self.filename + " (id = %r, _debug_name = %r)>" % (id(self), self._debug_name) #bruce 050429
        return "<Assembly of " + self.filename + ">"

    def writemmpfile(self, filename):
        from files_mmp import writemmpfile_assy
        writemmpfile_assy( self, filename, addshelf = True)
        
    def get_cwd(self):
        '''Returns the current working directory for assy.
        '''
        if self.filename: 
            cwd, file = os.path.split(self.filename)
        else: 
            cwd = globalParms['WorkingDirectory']
        return cwd

    # ==

    def become_state(self, state): #bruce 060117 kluge 
        from undo_archive import assy_become_state
        return assy_become_state(self, state) # this subroutine will probably become a method of class assembly

    def clear(self): #bruce 060117 kluge
        from undo_archive import assy_clear
        return assy_clear(self) # this subroutine will probably become a method of class assembly

    def editUndo(self):
        self.undo_manager.editUndo()

    def editRedo(self):
        self.undo_manager.editRedo()

    def undo_checkpoint_before_command(self, *args, **kws):
        return self.undo_manager.undo_checkpoint_before_command(*args, **kws)

    def undo_checkpoint_after_command(self, *args, **kws):
        return self.undo_manager.undo_checkpoint_after_command(*args, **kws)

    def current_command_info(self, *args, **kws):
        #e (will this always go into undo system, or go into some more general current command object in env, instead?)
        return self.undo_manager.current_command_info(*args, **kws)
    
    pass # end of class assembly

# end
