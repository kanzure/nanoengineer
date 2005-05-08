# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ops_copy.py -- general cut/copy/delete operations on selections
containing all kinds of model tree nodes.

$Id$

History:

bruce 050507 made this by collecting appropriate methods from class Part.
"""

from changes import begin_event_handler, end_event_handler
from HistoryWidget import greenmsg, redmsg
from platform import fix_plurals
from Utility import Group
from chunk import molecule
import platform # for atom_debug
from debug import print_compact_stack
from jigs import gensym # [I think this code, when in part.py, was using jigs.gensym rather than chem.gensym [bruce 050507]] 

class ops_copy_Mixin:
    "Mixin class for providing these methods to class Part"

    # == ###@@@ cut/copy/paste/kill will all be revised to handle bonds better (copy or break them as appropriate)
    # incl jig-atom connections too [bruce, ca. time of assy/part split]
    # [renamings, bruce 050419: kill -> delete_sel, cut -> cut_sel, copy -> copy_sel; does paste also need renaming? to what?]
    
    # bruce 050131/050201 revised these Cut and Copy methods to fix some Alpha bugs;
    # they need further review after Alpha, and probably could use some merging. ###@@@
    # See also assy.delete_sel (Delete operation).

    def cut(self):
        if platform.atom_debug:
            print_compact_stack( "atom_debug: assy.cut called, should use its new name cut_sel: ")
        return self.cut_sel()
    
    def cut_sel(self, use_selatoms = True): #bruce 050505 added use_selatoms = True option, so MT ops can pass False (bugfix)
        #bruce 050419 renamed this from cut to avoid confusion with Node method and follow new _sel convention
        eh = begin_event_handler("Cut") # bruce ca. 050307; stub for future undo work; experimental
        center_these = []
        try:
            self.w.history.message(greenmsg("Cut:"))
            if use_selatoms and self.selatoms:
                #bruce 050201-bug370 (2nd commit here, similar issue to bug 370):
                # changed condition to not use selwhat, since jigs can be selected even in Select Atoms mode
                self.w.history.message(redmsg("Cutting selected atoms is not yet supported.")) #bruce 050201
                ## return #bruce 050201-bug370: don't return yet, in case some jigs were selected too.
                # note: we will check selatoms again, below, to know whether we emitted this message
            new = Group(gensym("Copy"), self.assy, None)
                # bruce 050201 comment: this group is usually, but not always, used only for its members list
            if self.immortal() and self.topnode.picked:
                ###@@@ design note: this is an issue for the partgroup but not for clips... what's the story?
                ### Answer: some parts can be deleted by being entirely cut (top node too) or killed, others can't.
                ### This is not a properly of the node, so much as of the Part, I think.... not clear since 1-1 corr.
                ### but i'll go with that guess. immortal parts are the ones that can't be killed in the UI.
                
                #bruce 050201 to fix catchall bug 360's "Additional Comments From ninad@nanorex.com  2005-02-02 00:36":
                # don't let assy.tree itself be cut; if that's requested, just cut all its members instead.
                # (No such restriction will be required for assy.copy_sel, even when it copies entire groups.)
                self.topnode.unpick_top()
                ## self.w.history.message(redmsg("Can't cut the entire Part -- cutting its members instead.")) #bruce 050201
                ###@@@ following should use description_for_history, but so far there's only one such Part so it doesn't matter yet
                self.w.history.message("Can't cut the entire Part; copying its toplevel Group, cutting its members.") #bruce 050201
                # new code to handle this case [bruce 050201]
                self.topnode.apply2picked(lambda(x): x.moveto(new))
                use = new
                use.name = self.topnode.name # not copying any other properties of the Group (if it has any)
                new = Group(gensym("Copy"), self.assy, None)
                new.addchild(use)
            else:
                self.topnode.apply2picked(lambda(x): x.moveto(new))
                # bruce 050131 inference from recalled bug report:
                # this must fail in some way that addchild handles, or tolerate jigs/groups but shouldn't;
                # one difference is that for chunks it would leave them in assy.molecules whereas copy_sel would not;
                # guess: that last effect (and the .pick we used to do) might be the most likely cause of some bugs --
                # like bug 278! Because findpick (etc) uses assy.molecules. So I fixed this with sanitize_for_clipboard, below.
                # [later, 050307: replaced that with update_parts.]

            # Now we know what nodes to cut (i.e. move to the clipboard) -- the members of new.
            # And they are no longer in their original location,
            # but neither they nor the group "new" is in its final location.
            # (But they still belong to their original Part, until this is changed later.)
            
            #e much of the following might someday be done automatically by end_event_handler and by methods in a Cut command object
            
            if new.members:
                # move them to the clipboard (individually for now, though this
                # is wrong if they are bonded; also, this should be made common code
                # with DND move to clipboard, though that's more complex since
                # it might move nodes inside an existing item. [bruce 050307 comment])
                self.changed() # bruce 050201 doing this earlier; 050223 made it conditional on new.members
                nshelf_before = len(self.shelf.members) #bruce 050201
                for ob in new.members[:]:
                    # [bruce 050302 copying that members list, to fix bug 360 item 8, like I fixed
                    #  bug 360 item 5 in "copy_sel" 2 weeks ago. It's silly that I didn't look for the same
                    #  bug in this method too, when I fixed it in copy_sel.]
                    # bruce 050131 try fixing bug 278 in a limited, conservative way
                    # (which won't help the underlying problem in other cases like drag & drop, sorry),
                    # based on the theory that chunks remaining in assy.molecules is the problem:
                    ## self.sanitize_for_clipboard(ob) ## zapped 050307 since obs
                    self.shelf.addchild(ob) # add new member(s) to the clipboard [incl. Groups, jigs -- won't be pastable]
                    # If the new member is a molecule, move it to the center of its space --
                    # but not yet, since it messes up break_interpart_bonds which we'll do later!
                    # This caused bug 452 item 18.
                    # Doing the centering later is a temporary fix, should not be necessary,
                    # since the better fix is for breaking a bond to not care if its endpoint coords make sense.
                    # (That is, to reposition the singlets from scratch, not based on the existing bond.)
                    # [bruce 050321]
                    if isinstance(ob, molecule):
                        center_these.append(ob) ## was: ob.move(-ob.center)
                ## ob.pick() # bruce 050131 removed this
                nshelf_after = len(self.shelf.members) #bruce 050201
                self.w.history.message( fix_plurals("Cut %d item(s)" % (nshelf_after - nshelf_before)) + "." ) #bruce 050201
                    ###e fix_plurals can't yet handle "(s)." directly. It needs improvement after Alpha.
            else:
                if not (use_selatoms and self.selatoms):
                    #bruce 050201-bug370: we don't need this if the message for selatoms already went out
                    self.w.history.message(redmsg("Nothing to cut.")) #bruce 050201
        finally:
            end_event_handler(eh) # this should fix Part membership of moved nodes, break inter-Part bonds #####@@@@@ doit
            # ... but it doesn't, so instead, do this: ######@@@@@@ and review this situation and clean it up:
            self.assy.update_parts()
            for ob in center_these: #bruce 050321
                if ob.is_top_of_selection_group(): # should be always True, but check to be safe
                    ob.move(-ob.center)
                elif platform.atom_debug:
                    print "atom_debug: bug? mol we should center no longer is_top_of_selection_group", ob
            self.w.win_update() ###stub of how this relates to ending the handler
        return

    def copy(self):
        if platform.atom_debug:
            print_compact_stack( "atom_debug: assy.copy called, should use its new name copy_sel: ")
        return self.copy_sel()
    
    # copy any selected parts (molecules) [making a new clipboard item... #doc #k]
    #  Revised by Mark to fix bug 213; Mark's code added by bruce 041129.
    #  Bruce's comments (based on reading the code, not all verified by test): [###obs comments]
    #    0. If groups are not allowed in the clipboard (bug 213 doesn't say,
    #  but why else would it have been a bug to have added a group there?),
    #  then this is only a partial fix, since if a group is one of the
    #  selected items, apply2picked will run its lambda on it directly.
    #    1. The group 'new' is now seemingly used only to hold
    #  a list; it's never made a real group (I think). So I wonder if this
    #  is now deviating from Josh's intention, since he presumably had some
    #  reason to make a group (rather than just a list).
    #    2. Is it intentional to select only the last item added to the
    #  clipboard? (This will be the topmost selected item, since (at least
    #  for now) the group members are in bottom-to-top order.)
    
    def copy_sel(self, use_selatoms = True): #bruce 050505 added use_selatoms = True option, so MT ops can pass False (bugfix)
        #bruce 050419 renamed this from copy
        self.w.history.message(greenmsg("Copy:"))
        if use_selatoms and self.selatoms:
            #bruce 050201-bug370: revised this in same way as for assy.cut_sel (above)
            self.w.history.message(redmsg("Copying selected atoms is not yet supported.")) #bruce 050131
            ## return
        new = Group(gensym("Copy"), self.assy, None)
            # bruce 050201 comment: this group is always (so far) used only for its members list
        # x is each node in the tree that is picked. [bruce 050201 comment: it's ok if self.topnode is picked.]
        # [bruce 050131 comments (not changing it in spite of bugs):
        #  the x's might be chunks, jigs, groups... but maybe not all are supported for copy.
        #  In fact, Group.copy returns 0 and Jig.copy returns None, and addchild tolerates that
        #  and does nothing!!
        #  About chunk.copy: it sets numol.assy but doesn't add it to assy,
        #  and it sets numol.dad but doesn't add it to dad's members -- so we do that immediately
        #  in addchild. So we end up with a members list of copied chunks from assy.tree.]
        self.topnode.apply2picked(lambda(x): new.addchild(x.copy(None))) #bruce 050215 changed mol.copy arg from new to None

        # unlike for cut_sel, no self.changed() should be needed
        
        if new.members:
            nshelf_before = len(self.shelf.members) #bruce 050201
            for ob in new.members[:]:
                # [bruce 050215 copying that members list, to fix bug 360 comment #6 (item 5),
                # which I introduced in Alpha-2 by making addchild remove ob from its prior home,
                # thus modifying new.members during this loop]
                ## no longer needed, 050309:
                ## self.sanitize_for_clipboard(ob) # not needed on 050131 but might be needed soon, and harmless
                self.shelf.addchild(ob) # add new member(s) to the clipboard
                # if the new member is a molecule, move it to the center of its space
                if isinstance(ob, molecule): ob.move(-ob.center)
            ## ob.pick() # bruce 050131 removed this
            nshelf_after = len(self.shelf.members) #bruce 050201
            self.w.history.message( fix_plurals("Copied %d item(s)" % (nshelf_after - nshelf_before)) + "." ) #bruce 050201
                ###e fix_plurals can't yet handle "(s)." directly. It needs improvement after Alpha.
        else:
            if not (use_selatoms and self.selatoms):
                #bruce 050201-bug370: we don't need this if the message for selatoms already went out
                self.w.history.message(redmsg("Nothing to Copy.")) #bruce 050201
        self.assy.update_parts() # stub, 050308; overkill! should just apply to the new shelf items. ####@@@@ 
        self.w.win_update()
        return
    
    def paste(self, node):
        pass # to be implemented

    def kill(self):
        if platform.atom_debug:
            print_compact_stack( "atom_debug: assy.kill called, should use its new name delete_sel: ")
        self.delete_sel()

    def delete_sel(self, use_selatoms = True): #bruce 050505 added use_selatoms = True option, so MT ops can pass False (bugfix)
        "delete all selected nodes or atoms in this Part [except the top node, if we're an immortal Part]"
        #bruce 050419 renamed this from kill, to distinguish it
        # from standard meaning of obj.kill() == kill that obj
        #bruce 050201 for Alpha: revised this to fix bug 370
        ## "delete whatever is selected from this assembly " #e use this in the assy version of this method, if we need one
        self.w.history.message(greenmsg("Delete:"))
        ###@@@ #e this also needs a results-message, below.
        if use_selatoms and self.selatoms:
            self.changed()
            for a in self.selatoms.values():
                a.kill()
            self.selatoms = {} # should be redundant
        
        ## bruce 050201 removed the condition "self.selwhat == 2 or self.selmols"
        # (previously used to decide whether to kill all picked nodes in self.topnode)
        # since selected jigs no longer force selwhat to be 2.
        # (Maybe they never did, but my guess is they did; anyway I think they shouldn't.)
        # self.changed() is not needed since removing Group members should do it (I think),
        # and would be wrong here if nothing was selected.
        if self.immortal():
            self.topnode.unpick_top() #bruce 050201: prevent deletion of entire part (no msg needed)
        self.topnode.apply2picked(lambda o: o.kill())
        self.invalidate_attr('natoms') #####@@@@@ actually this is needed in the atom and molecule kill methods, and add/remove methods
        #bruce 050427 moved win_update into delete_sel as part of fixing bug 566
        self.w.win_update()
        return

    pass # end of class ops_copy_Mixin

# end
