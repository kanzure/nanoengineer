# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ops_copy.py -- general cut/copy/delete operations on selections
containing all kinds of model tree nodes.

$Id$

History:

bruce 050507 made this by collecting appropriate methods from class Part.

bruce 050901 used env.history in some places.
"""

from HistoryWidget import greenmsg, redmsg
from platform import fix_plurals
from Utility import Group
from chunk import molecule
from bonds import bond_copied_atoms
import platform # for atom_debug
from debug import print_compact_stack
from jigs import gensym # [I think this code, when in part.py, was using jigs.gensym rather than chem.gensym [bruce 050507]]
from ops_select import selection_from_part
import env #bruce 050901
from constants import noop

class ops_copy_Mixin:
    "Mixin class for providing these methods to class Part"

    # == ###@@@ cut/copy/paste/kill will all be revised to handle bonds better (copy or break them as appropriate)
    # incl jig-atom connections too [bruce, ca. time of assy/part split]
    # [renamings, bruce 050419: kill -> delete_sel, cut -> cut_sel, copy -> copy_sel; does paste also need renaming? to what?]
    
    # bruce 050131/050201 revised these Cut and Copy methods to fix some Alpha bugs;
    # they need further review after Alpha, and probably could use some merging. ###@@@
    # See also assy.delete_sel (Delete operation).

    def cut(self):
        print "bug (worked around): assy.cut called, should use its new name cut_sel" #bruce 050927
        if platform.atom_debug:
            print_compact_stack( "atom_debug: assy.cut called, should use its new name cut_sel: ")
        return self.cut_sel()
    
    def cut_sel(self, use_selatoms = True): #bruce 050505 added use_selatoms = True option, so MT ops can pass False (bugfix)
        #bruce 050419 renamed this from cut to avoid confusion with Node method and follow new _sel convention
        mc = env.begin_op("Cut") #bruce 050908 for Undo
        try:
            cmd = greenmsg("Cut: ")
            if use_selatoms and self.selatoms:
                # condition should not use selwhat, since jigs can be selected even in Select Atoms mode
                msg = redmsg("Cutting selected atoms is not yet supported.")
                env.history.message(cmd + msg)
                # don't return yet, in case some jigs were selected too.
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
                ## env.history.message(redmsg("Can't cut the entire Part -- cutting its members instead.")) #bruce 050201
                ###@@@ following should use description_for_history, but so far there's only one such Part so it doesn't matter yet
                msg = "Can't cut the entire Part; copying its toplevel Group, cutting its members."
                env.history.message(cmd + msg)
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
            
            #e some of the following might someday be done automatically by something like end_event_handler (obs)
            # and/or by methods in a Cut command object [bruce 050908 revised comment]
            
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
                nshelf_after = len(self.shelf.members) #bruce 050201
                msg = fix_plurals("Cut %d item(s)" % (nshelf_after - nshelf_before)) + "." 
                env.history.message(cmd + msg) #bruce 050201
                    ###e fix_plurals can't yet handle "(s)." directly. It needs improvement after Alpha.
            else:
                if not (use_selatoms and self.selatoms):
                    #bruce 050201-bug370: we don't need this if the message for selatoms already went out
                    env.history.message(cmd + redmsg("Nothing to cut.")) #bruce 050201
        finally:
            self.assy.update_parts()
            self.w.win_update()
            env.end_op(mc)
        return

    def copy(self):
        print "bug (worked around): assy.copy called, should use its new name copy_sel" #bruce 050927
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

    #e bruce 050523: should revise this to use selection_from_MT object...
    
    def copy_sel(self, use_selatoms = True): #bruce 050505 added use_selatoms = True option, so MT ops can pass False (bugfix)
        #bruce 050419 renamed this from copy
        #bruce 050523 new code
        # 1. what objects is user asking to copy?
        
        cmd = greenmsg ("Copy: ")
        
        part = self
        sel = selection_from_part(part, use_selatoms = use_selatoms)
        # 2. prep this for copy by including other required objects, context, etc...
        # (eg a new group to include it all, new chunks for bare atoms)
        # and emit message about what we're about to do
        if platform.atom_debug: #bruce 050811 fixed this for A6 (it was a non-debug reload)
            print "atom_debug: fyi: importing or reloading ops_copy from itself"
            import ops_copy as hmm
            reload(hmm)
        from ops_copy import Copier # use latest code for that class, even if not for this mixin method!
        copier = Copier(sel) #e sel.copier()?
        copier.prep_for_copy_to_shelf()
        if copier.ok():
            desc = copier.describe_objects_for_history() # e.g. "5 items" ### not sure this is worth it if we have a results msg
            if desc:
                text = "Copy %s" % desc
            else:
                text = "Copy"
            env.history.message(cmd + text)
        else:
            whynot = copier.whynot()
            env.history.message(cmd + redmsg(whynot))
            return
        # 3. do it
        new = copier.copy_as_node_for_shelf()
        self.shelf.addchild(new)
        # 4. clean up
        self.assy.update_parts()
            # overkill! should just apply to the new shelf items. [050308] ###@@@
            # (It might not be that simple -- at one point we needed to scan anything they were jig-connected to as well.
            #  Probably that's no longer true, but it needs to be checked before this is changed. [050526])
        self.w.win_update()
        return

    def part_for_save_selection(self):
        #bruce 050925; this helper method is defined here since it's very related to copy_sel ###k does it need self?
        """[private helper method for Save Selection]
        Return the tuple (part, killfunc, desc),
        where part is an existing or new Part which can be saved (in any format the caller supports)
        in order to save the current selection, or is None if it can't be saved (with desc being the reason why not),
        killfunc should be called when the caller is done using part,
        and desc is "" or a text string describing the selection contents
        (or an error message when part is None, as mentioned above), for use in history messages.
        """
        self.assy.o.saveLastView() # make sure glpane's cached info gets updated in its current Part, before we might use it
        entire_part = self
        sel = selection_from_part(entire_part, use_selatoms = True) #k use_selatoms is a guess
        if platform.atom_debug:
            print "atom_debug: fyi: importing or reloading ops_copy from itself"
            import ops_copy as hmm
            reload(hmm)
        from ops_copy import Copier # use latest code for that class, even if not for this mixin method!
        copier = Copier(sel) #e sel.copier()?
        copier.prep_for_copy_to_shelf() ###k guess: same prep method should be ok
        if copier.ok():
            desc = copier.describe_objects_for_history() # e.g. "5 items"
            desc = desc or "" #k might be a noop
            # desc is returned below
        else:
            whynot = copier.whynot()
            desc = whynot
            if not sel.nonempty():
                # override message, which refers to "copy" [##e do in that subr??]
                desc = "Nothing to save" # I'm not sure this always means nothing is selected!
            return None, noop, desc
        # copy the selection (unless it's an entire part)
        ####@@@@ logic bug: if it's entire part, copy might still be needed if jigs ref atoms outside it! Hmm... ####@@@@
        copiedQ, node = copier.copy_as_node_for_saving()
        if node is None:
            desc = "Can't save this selection." #e can this happen? needs better explanation. Does it happen for no sel?
            return None, noop, desc
        # now we know we can save it; find or create part to save        
        if not copiedQ:
            # node is top of an existing Part, which we should save in its entirety. Its existing pov is fine.
            savepart = node.part
            assert savepart is not None
            killfunc = noop
        else:
            # make a new part, copy pov from original one (##k I think that happens automatically in Part.__init__)
            from part import Part
            savepart = Part(self.assy, node)
            killfunc = savepart.destroy_with_topnode
        self.w.win_update() # precaution in case of bugs (like side effects on selection) -- if no bugs, should not be needed
        return (savepart, killfunc, desc)

    def paste(self, node):
        pass # to be implemented

    def kill(self):
        print "bug (worked around): assy.kill called, should use its new name delete_sel" #bruce 050927
        if platform.atom_debug:
            print_compact_stack( "atom_debug: assy.kill called, should use its new name delete_sel: ")
        self.delete_sel()

    def delete_sel(self, use_selatoms = True): #bruce 050505 added use_selatoms = True option, so MT ops can pass False (bugfix)
        "delete all selected nodes or atoms in this Part [except the top node, if we're an immortal Part]"
        #bruce 050419 renamed this from kill, to distinguish it
        # from standard meaning of obj.kill() == kill that obj
        #bruce 050201 for Alpha: revised this to fix bug 370
        ## "delete whatever is selected from this assembly " #e use this in the assy version of this method, if we need one
        
        cmd = greenmsg("Delete: ")
        info = ''
            
        ###@@@ #e this also needs a results-message, below.
        if use_selatoms and self.selatoms:
            self.changed()
            nsa = len(self.selatoms) # Get the number of selected atoms before it changes
            for a in self.selatoms.values():
                a.kill()
            self.selatoms = {} # should be redundant
            
            info = fix_plurals( "Deleted %d atom(s)" % nsa)
        
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
        
        env.history.message( cmd + info) # Mark 050715
        
        self.w.win_update()
        return

    pass # end of class ops_copy_Mixin

# ==

def copied_nodes_for_DND( nodes, autogroup_at_top = False): #bruce 050527
    from ops_select import Selection
    if not nodes:
        return None
    part = nodes[0].part # kluge
    copier = Copier(Selection(part, nodes = nodes))
    copier.prep_for_copy_to_shelf()
    if not copier.ok():
        #e histmsg?
        return None
    nodes = copier.copy_as_list_for_DND() # might be None (after histmsg) or a list
    if nodes and autogroup_at_top:
        nodes = copier.autogroup_if_several(nodes)
    return nodes

# ==

class Copier: #bruce 050523-050526; might need revision for merging with DND copy
    "Controller for copying selected nodes and/or atoms."
    def __init__(self, sel):
        self.sel = sel # a Selection object
        self.assy = sel.part.assy
    def prep_for_copy_to_shelf(self):
        """Figure out whether to make a new toplevel Group,
        whether to copy any nonselected Groups or Chunks with selected innards, etc.
        """
        # Rules: partly copy (just enough to provide a context or container for other copied things):
        # - any chunk with copied atoms (since atoms can't live outside of chunks),
        # - certain jigs with copied atoms (those which confer properties on the atoms),
        # - any Group with some but not all copied things (not counting partly copied jigs?) inside it
        #   (since it's a useful separator),
        # - (in future; maybe) any Group which confers properties (eg display modes) being used on copied
        #   things inside it (but probably just copy the properties actually being used).
        # Then at the end (these last things might not be done until a later method, not sure):
        # - if more than topnode is being copied, make a wrapping group around
        #   everything that gets copied (this is not really a copy of the PartGroup, e.g. its name is unrelated).
        # - perhaps modify the name of the top node copied (or of the wrapping group) to say it's a copy.
        # Algorithm: 
        # we'll make dicts of leafnodes to partly copy, but save most of the work
        # (including all decisions about groups) for a scan during the actual copy.
        fullcopy = self.fullcopy = {}
        atom_chunks = self.atom_chunks = {} # id(chunk) -> chunk, for chunks containing selected atoms
        atom_chunk_atoms = self.atom_chunk_atoms = {} # id(chunk) -> list of its atoms to copy (if it's not fullcopied) (arb order)
        atom_jigs = self.atom_jigs = {}
        sel = self.sel
        for node in sel.topnodes: # no need to scan selmols too, it's redundant (and in general a subset)
            # chunks, jigs, Groups -- for efficiency and in case it's a feature,
            # don't scan jigs of a chunk's atoms like we do for individual atoms;
            # this decision might be revised, and if so, we'd scan that here when node is a chunk.
            if node.will_copy_if_selected(sel):
                # Will this node agree to be copied, if it's selected, given what else is selected?
                # (Can be false for Jigs whose atoms won't be copied, if they can't exist with no atoms or too few atoms.)
                # For Groups, no need to recurse here and call this on members,
                # since we assume the groups themselves always say yes -- #e if that changes,
                # we might need to recurse on their members here if the groups say no,
                # unless that 'no' applies to copying the members too.
                fullcopy[id(node)] = node
        for atom in sel.selatoms.itervalues():
            chunk = atom.molecule
            #e for now we assume that all these chunks will always be partly copied;
            # if that changes, we'd need to figure out which ones are not copied, but not right here
            # since this can run many times per chunk.
            idchunk = id(chunk)
            atom_chunks[idchunk] = chunk #k might not be needed since redundant with atom_chunk_atoms except for knowing the chunk
                # some of these might be redundant with fullcopied chunks (at toplevel or lower levels); that's ok
                # (note: I think none are, for now)
            atoms = atom_chunk_atoms.setdefault(idchunk, [])
            atoms.append(atom)
            for jig in atom.jigs:
                if jig.confers_properties_on(atom):
                    # Note: it's intentional that we don't check this for all jigs on all atoms
                    # copied inside of selected chunks. The real reason is efficiency; the excuse
                    # is that when selecting chunks, user could do this in MT and choose which jigs
                    # to select, whereas when selecting atoms, they can't, so we have to do it
                    # for them (by "when in doubt, copy the jig" and letting them delete the ones
                    # they didn't want copied).
                    #  It's also intentional that whether the jig is disabled makes no difference here.
                    atom_jigs[id(jig)] = jig # ditto (about redundancy)
                    #e save filtering of jigtypes for later, for efficiency?
                    # I tried coding that and it seemed less efficient
                    # (since I'm assuming it can depend on the atom, in general, tho for now, none do).
        # Now we need to know which atom_jigs will actually agree to be partly copied,
        # just due to the selatoms inside them. Assume most of them will agree to be copied
        # (since they said they confer properties that should be copied) (so just delete the other ones).
        for jig in atom_jigs.values():
            if not jig.will_partly_copy_due_to_selatoms(sel):
                del atom_jigs[id(jig)]
                # This might delete some which should be copied since selected -- that's ok,
                # they remain in fullcopy then. We're just deleting *this reason* to copy them.
        # (At this point we assume that all jigs we still know about will agree to be copied,
        # except perhaps the ones inside fullcopied groups, for which we don't need to know in advance.)
        self.verytopnode = sel.part.topnode
        return # from prep_for_copy_to_shelf
    
    # the following methods should be called only after some operation has been prepped for
    # (and usually before it's been done, but that's not required)
    def ok(self):
        if self.sel.nonempty():
            return True
        self._whynot = "Nothing to copy"
        return False
    def describe_objects_for_history(self):
        return self.sel.describe_objects_for_history()
    _whynot = ""
    def whynot(self):
        return self._whynot or "can't copy those items"

    # this makes the actual copy (into a known destination) using the info computed above; there are three variants.

    def copy_as_list_for_DND(self): #bruce 050527 added this variant and split out the other one
        "Return a list of nodes, or None"
        return self.copy_as_list( make_partial_groups = False)
        
    def copy_as_node_for_shelf(self):
        """Create and return a new single node (not yet placed in any Group)
        which is a copy of our selected objects meant for the Clipboard;
        or return None (after history message -- would it be better to let caller do that??)
        if all selected objects refuse to be copied.
        """
        newstuff = self.copy_as_list( make_partial_groups = True) # might be None
        if newstuff is None:
            return None
        return self.wrap_or_rename( newstuff)

    def copy_as_node_for_saving(self): #bruce 050925 for "save selection"
        """Copy the selection into a single new node, suitable for saving into a new file;
        in some cases, return the original selection if a copy would not be needed;
        return value is a pair (copiedQ, node) where copiedq says whether node is a copy or not.
        If nothing was selected or none of the selection could be copied, return value is (False, None).
           Specifically:
        If the selection consists of one entire Part, return it unmodified (with no wrapping group).
        (This is the only use of the optimization of not actually copying; other uses of that
         would require an ability to copy or create a Group but let its children be shared with an
         existing different Group, which the Node class doesn't yet support.)
        Otherwise, return a new Group (suitable for transformation into a PartGroup by the caller)
        containing copies of the top selected nodes (perhaps partially grouped if they were in the original),
        even if there is only one top selected node.
        """
        if [self.sel.part.topnode] == self.sel.topnodes:
            return (False, self.sel.part.topnode)
        newstuff = self.copy_as_list( make_partial_groups = True) # might be None
        if newstuff is None:
            return (False, None)
        name = "Copied Selection" #k ?? add unique int?
        res = Group(name, self.assy, None, newstuff)
        return (True, res)

    def copy_as_list(self, make_partial_groups = True):
        """[private helper method]
        Create and return a list of one or more new nodes (not yet placed in any Group)
        which is a copy of our selected objects,
        or return None (after history message -- would it be better to let caller do that??)
        if all objects refuse to be copied.
           It's up to caller whether to group these nodes if there is more than one,
        whether to rename the top node, whether to recenter them,
        and whether to place them in the same or in a different Part as the one they started in.
           Assuming no bugs, the returned nodes might have internode bonds, but they have no
        bonds or jig-atom references (in either direction) between them as a set, and anything else.
        So, even if we copy a jig and caller intends to place it in the same Part,
        this method (unless extended! ###e) won't let that jig refer to anything except copied
        atoms (copied as part of the same set of nodes). [So to implement a "Duplicate" function
        for jigs, letting duplicates refer to the same atoms, this method would need to be extended.
        Or maybe copy for jigs with none of their atoms copied should have a different meaning?? #e]
        """
        self.make_partial_groups = make_partial_groups # used by self.recurse
        # Copy everything we need to (except for extern bonds, and finishing up of jig refs to atoms).
        self.origid_to_copy = {} # various obj copy methods use/extend this, to map id(orig-obj) to copy-obj for all levels of obj
        self.extern_atoms_bonds = []
            # this will get extended when chunks or isolated atoms are copied,
            # with (orig-atom, orig-bond) pairs for which bond copies are not made
            # (but atom copies will be made, and recorded in origid_to_copy)
        self.do_these_at_end = [] #e might change to a dict so it can handle half-copied bonds too, get popped when they pair up
        self.newstuff = []
        self.tentative_new_groups = {}
        self.recurse( self.verytopnode) #e this doesn't need the kluge of verytop always being a group, i think

        # Now handle the bonds that were not made when atoms were copied.
        # (Someday we might merge this into the "finishing up" (for jigs) that happens
        #  later. The order of this vs. that vs. group cleanup should not matter.)
        halfbonds = {}
        actualbonds = {}
        origid_to_copy = self.origid_to_copy
        for atom2, bond in self.extern_atoms_bonds:
            atom1 = halfbonds.pop(id(bond), None)
            if atom1 is not None:
                na1 = origid_to_copy[id(atom1)]
                na2 = origid_to_copy[id(atom2)]
                bond_copied_atoms(na1, na2, bond)
            else:
                halfbonds[id(bond)] = atom2
                actualbonds[id(bond)] = bond
                    #e would it be faster to just use bonds as keys? Probably not! (bond.__getattr__)
        # Now "break" (in the copied atoms) the still uncopied bonds (those for which only one atom was copied)
        # (This does not affect original atoms or break any existing bond object, but it acts like
        #  we copied a bond and then broke that copied bond.)
        for bondid, atom in halfbonds.items():
            bond = actualbonds[bondid]
            nuat = origid_to_copy[id(atom)]
            nuat.break_unmade_bond(bond, atom)
                # i.e. add singlets (or do equivalent invals) as if bond was copied onto atom, then broken;
                # uses original atom so it can find other atom and know bond direction
                # (it assumes nuat might be translated but not rotated, for now)

        # Do other finishing-up steps as requested by copied items
        # (e.g. jigs change their atom refs from orig to copied atoms)
        # (warning: res is still not in any Group, and still has no Part,
        #  and toplevel group structure might still be revised)
        # In case this can ever delete nodes or add siblings (though it doesn't do that for now) [now it can, as of bruce 050704],
        # we should do it before cleaning up the Group structure.
        for func in self.do_these_at_end[:]:
            func() # these should not add further such funcs! #e could check for that, or even handle them if added.
            # [these funcs now sometimes delete just-copied nodes, as of bruce 050704 fixing bug 743.]
        del self.do_these_at_end

        # Now clean up the toplevel Group structure of the copy, and return it.
        newstuff = self.newstuff
        del self.newstuff
        assert (not self.make_partial_groups) or (not newstuff or len(newstuff) == 1)
            # since either verytopnode is a leaf and refused or got copied,
            # or it's a group and copied as one (or all contents refused -- not sure if it copies then #k)
            # (this assert is not required by following code, it's just here as a sanity check)
        # strip off unneeded groups at the top, and return None if nothing got copied
        while len(newstuff) == 1 and id(newstuff[0]) in self.tentative_new_groups:
            newstuff = newstuff[0].steal_members()
        if not newstuff:
            # everything refused to be copied. Can happen (e.g. for a single selected jig at the top).
            env.history.message( redmsg( "That selection can't be copied by itself." )) ###e improve message
            return None

        # further processing depends on the caller (a public method of this class)
        return newstuff

    def autogroup_if_several(self, newstuff): #bruce 050527
        #e should probably refile this into self.assy or so,
        # or even into Node or Group (for target node which asks for the grouping to do),
        # and merge with similar code
        if newstuff and len(newstuff) > 1:
            # add wrapping group
            name = self.assy.name_autogrouped_nodes_for_clipboard( newstuff) #k argument
            res = Group(name, self.assy, None, newstuff)
                ###e we ought to also store this name as the name of the new part
                # (which does not yet exist), like is done in create_new_toplevel_group;
                # not sure when to do that or how to trigger it; probably could create a
                # fake old part here just to hold the name...
                # addendum, 050527: new prior_part feature might be doing this now; find out sometime #k
            newstuff = [res]
        return newstuff
        
    def wrap_or_rename(self, newstuff):
        # wrap or rename result
        if len(newstuff) > 1: #revised 050527
            newstuff = self.autogroup_if_several(newstuff)
            (res,) = newstuff
        else:
            res = newstuff[0]
            # now rename it, like old code would do (in mol.copy), though whether
            # this is a good idea seems very dubious to me [bruce 050524]
            try:
                #bruce 050627 new feature, only used experimentally so far (demo_trans is not yet committed)
                from demo_trans import special_node_name_q
            except:
                pass
            else:
                if special_node_name_q(res.name):
                    return res
            if res.name.endswith('-frag'):
                # kluge - in -frag case it's definitely bad to rename the copy, if this op added that suffix;
                # we can't tell, but since it's likely and since this is dubious anyway, don't do it in this case.
                pass
            else:
                from chunk import mol_copy_name
                res.name = mol_copy_name(res.name)
        #e in future we might also need to store a ref to the top original node, top_orig;
        # this is problematic when it was made up as a wrapping group,
        # but if we think of verytopnode as the one, in that case (always a group in that case), then it's probably ok...
        # for now we don't attempt this, since when we removed useless outer groups we didn't keep track of the original node.

        ##e this is where we'd like to recenter the view (rather than the object, as the old code did for single chunks),
        # but I'm not sure exactly how, so I'll save this for later. ###@@@
        
        return res
        
        ##e ideally we'd implem atoms & bonds differently than now, and copy using Numeric, but not for now.
        
    def recurse(self, orig): #e rename 
        "copy whatever is needed from orig and below, but don't fix refs immediately; append new copies to self.newstuff"
        idorig = id(orig)
        res = None
        if idorig in self.fullcopy:
            res = orig.copy_full_in_mapping(self)
                # recurses into groups, does atoms, bonds, jigs...
                # copies jigs leaving refs to orig things but with an at_end fixup method (??)
                # if refuses, puts None in the mapping as the copy
        elif idorig in self.atom_chunks:
            # orig contains some selected atoms (for now, that means it's a chunk)
            # but is not in fullcopy at any level. (Proof: if it's in fullcopy at toplevel, we handled it
            # in the 'if' case; if it's in fullcopy at a lower level, this method never recurses into it at all,
            # instead letting copy_full_in_mapping on the top fullcopied group handle it.)
            #    Ask it to make a partial copy with only the required atoms (which it should also copy).
            # It should properly copy those atoms (handling bonds, adding them to mapping if necessary).
            atoms = self.atom_chunk_atoms.pop(idorig)
                # the pop is just a space-optim (imperfect since not done for fullcopied chunks)
            res = orig.copy_in_mapping_with_specified_atoms(self, atoms)
        elif idorig in self.atom_jigs:
            # orig is something which confers properties on some selected atoms (but does not contain them);
            # copy it partially, arrange to fix refs later (since not all those atoms might be copied yet).
            # Since this only happens for Anchor jigs, and the semantics are same as copying them fully,
            # for now I'll just use the same method... later we can introduce a distinct 'copy_partial_in_mapping'
            # if there's some reason to do so.
            res = orig.copy_full_in_mapping(self)
        elif orig.is_group():
            if self.make_partial_groups: #bruce 050527 made this optional so DND copy can not do it
                save = self.newstuff
                self.newstuff = []
            map( self.recurse, orig.members)
            if self.make_partial_groups: #050527
                newstuff = self.newstuff
                self.newstuff = save
            else:
                newstuff = None
            if newstuff:
                # we'll make some sort of Group from it, as a partial copy of orig
                # (note that orig is a group which was not selected, so is only needed
                #  to hold copies of selected things inside it, perhaps at lower levels
                #  than its actual members)
                if len(newstuff) == 1 and id(newstuff[0]) in self.tentative_new_groups:
                    # merge names (and someday, pref settings) of orig and newstuff[0]
                    innergroup = newstuff[0]
                    name = orig.name + '/' + innergroup.name
                    newstuff = innergroup.steal_members()
                        # no need to recurse, since innergroup
                        # would have merged with its own member if possible
                else:
                    name = orig.name
                res = Group(name, self.assy, None, newstuff) # note, this pulls those members out of innergroup, if still there (slow?)
                self.tentative_new_groups[id(res)] = res
                    # mark it as tentative so enclosing-group copies are free to discard it and more directly wrap its contents
                ## record_copy is probably not needed, but do it anyway just for its assertions, for now:
                self.record_copy(orig, res)
            #e else need to record None as result?
        # else ditto?
        # now res is the result of that (if anything)
        if res is not None:
            self.newstuff.append(res)
        return # from recurse

    def mapper(self, orig): #k needed?
        # note: None result is ambiguous -- never copied, or refused?
        return self.origid_to_copy.get(id(orig))

    def record_copy(self, orig, copy): #k called by some but not all copiers; probably not needed except for certain atoms
        """Subclass-specific copy methods should call this to record the fact that orig
        (a node or a component of one, e.g. an atom or perhaps even a bond #k)
        is being copied as 'copy' in this mapping.
        (When this is called, copy must of course exist, but need not be "ready for use" --
         e.g. it's ok if orig's components are not yet copied into copy.)
        Also asserts orig was not already copied.
        """
        assert not self.origid_to_copy.has_key(id(orig))
        self.origid_to_copy[id(orig)] = copy

    def do_at_end(self, func): #e might change to dict
        """Node-specific copy methods can call this
        to request that func be run once when the entire copy operation is finished.
        Warning: it is run before ###doc.
        """
        self.do_these_at_end.append(func)
    
    pass # end of class Copier

# end