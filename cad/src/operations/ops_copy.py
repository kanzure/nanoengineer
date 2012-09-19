# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
ops_copy.py -- general cut/copy/delete operations on selections
containing all kinds of model tree nodes.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 050507 made this by collecting appropriate methods from class Part.

bruce extended it at various later times.
"""

from utilities import debug_flags
import foundation.env as env
from utilities.Comparison import same_vals
from utilities.debug import print_compact_stack
from utilities.Log import greenmsg, redmsg, orangemsg
from platform_dependent.PlatformDependent import fix_plurals
from foundation.Group import Group
from model.chunk import Chunk
from model.chunk import mol_copy_name
from model.chem import Atom_prekill_prep
from operations.ops_select import Selection
from model.bonds import bond_copied_atoms
from utilities.constants import gensym
from operations.ops_select import selection_from_part
from utilities.constants import noop
from geometry.VQT import V
from geometry.BoundingBox import BBox
from model.jigs import Jig

#General  page prefs - paste offset scale for chunk and dna pasting prefs key
from utilities.prefs_constants import pasteOffsetScaleFactorForChunks_prefs_key
from utilities.prefs_constants import pasteOffsetScaleFactorForDnaObjects_prefs_key

DEBUG_COPY = False # do not leave this as True in the release [bruce 080414]

class ops_copy_Mixin:
    """
    Mixin class for providing these methods to class Part
    """

    # == ###@@@ cut/copy/paste/kill will all be revised to handle bonds better (copy or break them as appropriate)
    # incl jig-atom connections too [bruce, ca. time of assy/part split]
    # [renamings, bruce 050419: kill -> delete_sel, cut -> cut_sel, copy -> copy_sel; does paste also need renaming? to what?]

    # bruce 050131/050201 revised these Cut and Copy methods to fix some Alpha bugs;
    # they need further review after Alpha, and probably could use some merging. ###@@@
    # See also assy.delete_sel (Delete operation).


    #@see: self._getInitialPasteOffsetForPastableNodes() to see how these are
    #attrs are used
    _initial_paste_offset_for_chunks = V(0, 0, 0)
    _initial_paste_offset_for_other_pastables = V(0, 0, 0)
    _previously_pasted_node_list = None

    def cut(self): # we should remove this obsolete alias shortly after the release. [bruce 080414 comment]
        print "bug (worked around): assy.cut called, should use its new name cut_sel" #bruce 050927
        if debug_flags.atom_debug:
            print_compact_stack( "atom_debug: assy.cut called, should use its new name cut_sel: ")
        return self.cut_sel()

    def cut_sel(self, use_selatoms = True):
        #bruce 050505 added use_selatoms = True option, so MT ops can pass False (bugfix)
        #bruce 050419 renamed this from cut to avoid confusion with Node method
        # and follow new _sel convention
        #
        ###BUG: this does not yet work properly for DNA. No time to fix for .rc1.
        # [bruce 080414 late]
        #
        # Note [bruce 080415]:
        # one correct implem for DNA would just be "copy, then delete".
        # (Each of those two ops operates on a differently extended set of chunks
        #  based on the selected chunks.) This would also make it work for
        # selected atoms, and make it "autogroup multiple items for clipboard".
        #
        # The issues of that implementation would be:
        # - delete doesn't yet work for DNA either (needs to extend the selection
        #   as specified elsewhere).
        # - need to make sure copy doesn't change selection, or if it does,
        #   record it first and restore it before delete, or pass the set
        #   of objects to use as the selection to delete_sel.
        # - copied jigs referring to noncopied atoms lose those references,
        #   whereas current code (which moves the jigs) preserves them
        #   (the jigs become disabled, but keep all their atoms).
        # - the history messages would say Copy rather than Cut.
        # - there may be other benefits of moving nodes rather than copying
        #   them, which I am not thinking of now.
        # Some of those could be addressed by adding a flag to Copier to
        # tell it it was "copying as part of Cut". Maybe we could even get
        # it to move rather than copy for nodes in a specified set.

        mc = env.begin_op("Cut") #bruce 050908 for Undo
        try:
            cmd = greenmsg("Cut: ")
            if use_selatoms and self.selatoms:
                # condition should not use selwhat, since jigs can be selected even in Select Atoms mode
                msg = redmsg("Cutting selected atoms is not yet supported.")
                    # REVIEW: could we fix that by calling Separate here,
                    # selecting the chunks it made from selected atoms,
                    # then continuing with Cut on them? [bruce 080415 Q]
                    # WARNING [bruce 060307, clarified 080415]: when this is
                    # implemented, the code below needs to check self.topnode
                    # for becoming None as a side effect of removing all atoms
                    # from a clipboard item whose topnode is a single chunk.
                    # See similar code in delete_sel, added by Mark to fix
                    # bug 1466, and the 'mark 060307' comment there.
                env.history.message(cmd + msg)
                # don't return yet, in case some jigs were selected too.
                # note: we will check selatoms again, below, to know whether we emitted this message
            new = Group(gensym("Copy", self.assy), self.assy, None) # (in cut_sel)
                # bruce 050201 comment: this group is usually, but not always, used only for its members list
            if self.immortal() and self.topnode.picked:
                ###@@@ design note: this is an issue for the partgroup but not for clips... what's the story?
                ### Answer: some parts can be deleted by being entirely cut (top node too) or killed, others can't.
                ### This is not a property of the node, so much as of the Part, I think.... not clear since 1-1 corr.
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
                new = Group(gensym("Copy", self.assy), self.assy, None) # (in cut_sel)
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
                        #bruce 080415 comment: it seems wrong that this doesn't
                        # put them all into a single new Group on the clipboard,
                        # when there is more than one item. That would fix the
                        # bond-breaking issue mentioned above.
                nshelf_after = len(self.shelf.members) #bruce 050201
                msg = fix_plurals("Cut %d item(s)." % (nshelf_after - nshelf_before))
                env.history.message(cmd + msg) #bruce 050201
            else:
                if not (use_selatoms and self.selatoms):
                    #bruce 050201-bug370: we don't need this if the message for selatoms already went out
                    env.history.message(cmd + redmsg("Nothing to cut.")) #bruce 050201
        finally:
            self.assy.update_parts()
            self.w.win_update()
            env.end_op(mc)
        return

##    def copy(self): # we should remove this obsolete alias shortly after the release. [bruce 080414 comment]
##        print "bug (worked around): assy.copy called, should use its new name copy_sel" #bruce 050927
##        if debug_flags.atom_debug:
##            print_compact_stack( "atom_debug: assy.copy called, should use its new name copy_sel: ")
##        return self.copy_sel()

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

        from dna.model.DnaLadderRailChunk import DnaAxisChunk, DnaStrandChunk
            # must be runtime import; after release, clean up by doing it in class Assembly
            # and referring to these as self.assy.DnaAxisChunk etc

        def chunks_to_copy_along_with(chunk):
            """
            Return a list (or other sequence) of chunks that we should copy along with chunk.
            """
            # after release, refactor by adding methods to these chunk classes.
            if isinstance(chunk, DnaAxisChunk):
                ladder = chunk.ladder
                if ladder and ladder.valid: # don't worry about ladder.error
                    return ladder.strand_chunks() #k
            elif isinstance(chunk, DnaStrandChunk):
                ladder = chunk.ladder
                if ladder and ladder.valid:
                    return ladder.axis_chunks() #k
            else:
                pass
            return ()

        part = self
        sel = selection_from_part(part,
                                  use_selatoms = use_selatoms,
                                  expand_chunkset_func = chunks_to_copy_along_with
                                  )

        # 2. prep this for copy by including other required objects, context, etc...
        # (eg a new group to include it all, new chunks for bare atoms)
        # and emit message about what we're about to do

        if debug_flags.atom_debug: #bruce 050811 fixed this for A6 (it was a non-debug reload)
            print "atom_debug: fyi: importing or reloading ops_copy from itself"
            import operations.ops_copy as hmm
            reload(hmm)
        from operations.ops_copy import Copier # use latest code for that class, even if not for this mixin method!
        copier = Copier(sel) #e sel.copier()?
        copier.prep_for_copy_to_shelf()
        if copier.objectsCopied == 0:  # wware 20051128, bug 1118, no error msg if already given
            return
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

    def copy_sel_in_same_part(self, use_selatoms = True):
        """
        Copies the selected object in the same part.

        @param  use_selatoms: If true, it uses the selected atoms in the GLPane
                for copying.

        @type   use_selatoms: boolean

        @return copiedObject: Object copied and added to the same part
                (e.g. Group, chunk, jig)

        @note: Uses: Used in mirror operation.
        """
        #NOTE: This uses most of the code in copy_sel.

        # 1. what objects is user asking to copy?
        part = self
        sel = selection_from_part(part, use_selatoms = use_selatoms)
        # 2. prep this for copy by including other required objects, context, etc...
        # (eg a new group to include it all, new chunks for bare atoms)
        # and emit message about what we're about to do
        if debug_flags.atom_debug: #bruce 050811 fixed this for A6 (it was a non-debug reload)
            print "atom_debug: fyi: importing or reloading ops_copy from itself"
            import operations.ops_copy as hmm
            reload(hmm)
        from operations.ops_copy import Copier # use latest code for that class, even if not for this mixin method!
        copier = Copier(sel) #e sel.copier()?
        copier.prep_for_copy_to_shelf()
        if copier.objectsCopied == 0:  # wware 20051128, bug 1118, no error msg if already given
            return
        if copier.ok():
            desc = copier.describe_objects_for_history() # e.g. "5 items" ### not sure this is worth it if we have a results msg
            if desc:
                text = "Mirror %s" % desc
            else:
                text = "Mirror"
            env.history.message(text)
        else:
            whynot = copier.whynot()
            cmd = 'Copy: ' # WRONG, but before this, it was undefined, according to pylint;
              # I guess it should be passed in from caller? needs REVIEW. [bruce 071107]
            env.history.message(cmd + redmsg(whynot))
            return
        # 3. do it
        copiedObject = copier.copy_as_node_for_shelf()
        self.assy.addnode(copiedObject)
        # 4. clean up
        self.assy.update_parts()
            # overkill! should just apply to the new shelf items. [050308] ###@@@
            # (It might not be that simple -- at one point we needed to scan anything they were jig-connected to as well.
            #  Probably that's no longer true, but it needs to be checked before this is changed. [050526])
        self.w.win_update()

        return copiedObject

    def part_for_save_selection(self):
        #bruce 050925; this helper method is defined here since it's very related to copy_sel ###k does it need self?
        """
        [private helper method for Save Selection]

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
        if debug_flags.atom_debug:
            print "atom_debug: fyi: importing or reloading ops_copy from itself"
            import operations.ops_copy as hmm
            reload(hmm)
        from operations.ops_copy import Copier # use latest code for that class, even if not for this mixin method!
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
            # make a new part, copy pov from original one (##k I think that
            # pov copy happens automatically in Part.__init__)
##            from part import Part as Part_class
            Part_class = self.__class__ #bruce 071103 to fix import cycle
                # (this code is untested since that Part_class change, since
                #  this feature is not accessible from the UI)
            assert Part_class.__name__ == 'Part' # remove when works
            savepart = Part_class(self.assy, node)
                # obs comment, if the above import cycle fix works:
                ### TODO: get the appropriate subclass of Part from self.assy
                # or node, and/or use a superclass with fewer methods,
                # to break an import cycle between part and ops_copy.
                #   Note that this method is only needed for "save selection",
                # which is not in the UI and probably not fully implemented
                # (though I can't see in what way it's not done in the code,
                #  except the logic bug comment above; otoh I might be missing
                #  something), but which appears to be "almost fully implemented",
                # so this code should be preserved (and made accessible from a
                # debug menu command).
                # [bruce 071029 comment]
            killfunc = savepart.destroy_with_topnode
        self.w.win_update() # precaution in case of bugs (like side effects on selection) -- if no bugs, should not be needed
        return (savepart, killfunc, desc)

    def paste(self, pastableNode, mousePosition = None):
        """
        Paste the given item in the 3D workspace.

        A. Implementation notes for the single shot paste operation:
           - The object (chunk or group) is pasted with a slight offset.
             Example:
             Create a graphene sheet, select it , do Ctrl + C and then Ctrl + V.
             The pasted object is offset to original one.
           - It deselects others, selects the pasted item and then does a zoom
             to selection so that the selected item is in the center of the
             screen.
           - Bugs/ Unsupported feature: If you paste multiple copies of an
             object they are pasted at the same location.
             (i.e. the offset is constant)

        B. Implemetation notes for 'Paste from clipboard' operation:
           - Enter L{PasteFromClipboard_Command}, select a pastable from the PM and then
             double click inside the 3D workspace to paste that object.
             This function uses the mouse coordinates during double click for
             pasting.

        @param pastableNode: The item to be pasted in the 3D workspace
        @type  pastableNode: L{Node}

        @param mousePosition: These are the coordinates during mouse
                              double click while in Paste Mode.
                              If the node has a center it will be moved by the
                              moveOffset, which is L{[mousePosition} -
                              node.center. This parameter is not used if its a
                              single shot paste operation (Ctrl + V)
        @type mousePosition:  Array containing the x, y, z position on the
                              screen, or None
        @see:L{self._pasteChunk}, L{self._pasteGroup}, L{self._pasteJig}
        @see:L{MWsemantics.editPaste}, L{MWsemantics.editPasteFromClipboard}

        @return: (itemPasted, errorMsg)
        @rtype: tuple of (node or None, string)
        """
        ###REVIEW: this has not been reviewed for DNA data model. No time to fix for .rc1. [bruce 080414 late]

        pastable = pastableNode
        pos = mousePosition
        moveOffset = V( 0, 0, 0)
        itemPasted = None

        # TODO: refactor this so that the type-specific paste methods
        # can all be replaced by a single method that works for any kind
        # of node, includind kinds other than Chunk, Group, or Jig.
        # This would probably involve adding new methods to the Node API
        # for things like bounding box for 3d objects.
        # Also there is a design Q of what Paste should do for selections
        # which include non-3d objects like comment nodes; I think it should
        # "just work", copying them into a new location in the model tree.
        # And it ought to work for selected non-nodes like atoms, too, IMHO.
        # [bruce 071011 comment]

        if isinstance(pastable, Chunk):
            itemPasted, errorMsg = self._pasteChunk(pastable, pos)
        elif isinstance(pastable, Group):
            itemPasted, errorMsg = self._pasteGroup(pastable, pos)
        elif isinstance(pastable, Jig):
            #NOTE: it never gets in here because an independent jig on the
            #clipboard is not considered 'pastable' . This needs to change
            # so that Planes etc , which are internally 'jigs' can be pasted
            # when they exist as a single node -- ninad 2007-08-31
            itemPasted, errorMsg = self._pasteJig(pastable, pos)
        else:
            errorMsg = redmsg("Internal error pasting clipboard item [%s]") % \
                pastable.name


        if pos is None:
            self.assy.unpickall_in_GLPane()
            itemPasted.pick()
            #Do not "zoom to selection" (based on a discussion with Russ) as
            #its confusing -- ninad 2008-06-06 (just before v1.1.0 code freeze)
            ##self.assy.o.setViewZoomToSelection(fast = True)

        self.assy.w.win_update()

        if errorMsg:
            msg = errorMsg
        else:
            msg = greenmsg("Pasted copy of clipboard item: [%s] ") % \
                pastable.name

        env.history.message(msg)

        return itemPasted, "copy of %r" % pastable.name

    def _pasteChunk(self, chunkToPaste, mousePosition = None):
        """
        Paste the given chunk in the 3D workspace.
        @param chunkToPaste: The chunk to be pasted in the 3D workspace
        @type  chunkToPaste: L{Chunk}

        @param mousePosition: These are the coordinates during mouse double
                              click.
        @type mousePosition:  Array containing the x, y, z position on the
                              screen, or None
        @see: L{self.paste} for implementation notes.

        @return: (itemPasted, errorMsg)
        @rtype: tuple of (node or None, string)
        """
        assert isinstance(chunkToPaste, Chunk)

        pastable = chunkToPaste
        pos = mousePosition
        newChunk = None
        errorMsg = None
        moveOffset = V(0, 0, 0)

        newChunk = pastable.copy_single_chunk(None)
        chunkCenter  = newChunk.center


        #@see: self._getInitialPasteOffsetForPastableNodes()
        original_copied_nodes = [chunkToPaste]
        if chunkToPaste:
            initial_offset_for_chunks, initial_offset_for_other_pastables = \
                                     self._getInitialPasteOffsetForPastableNodes(original_copied_nodes)
        else:
            initial_offset_for_chunks = V(0, 0, 0)
            initial_offset_for_other_pastables = V(0, 0, 0)


        if pos:
            #Paste from clipboard (by Double clicking)
            moveOffset = pos - chunkCenter
        else:
            #Single Shot paste (Ctrl + V)
            boundingBox = BBox()
            boundingBox.merge(newChunk.bbox)
            scale = float(boundingBox.scale() * 0.06)
            if scale < 0.001:
                scale = 0.1
            moveOffset = scale * self.assy.o.right
            moveOffset += scale * self.assy.o.down
            moveOffset += initial_offset_for_chunks

        #@see: self._getInitialPasteOffsetForPastableNodes()
        self._initial_paste_offset_for_chunks = moveOffset

        newChunk.move(moveOffset)
        self.assy.addmol(newChunk)

        return newChunk, errorMsg

    def _pasteGroup(self, groupToPaste, mousePosition = None):
        """
        Paste the given group (and all its members) in the 3D workspace.

        @param groupToPaste: The group to be pasted in the 3D workspace
        @type  groupToPaste: L{Group}

        @param mousePosition: These are the coordinates during mouse
                              double click.
        @type mousePosition:  Array containing the x, y, z
                              position on the screen, or None
        @see: L{self.paste} for implementation notes.
        @see: self. _getInitialPasteOffsetForPastableNodes()

        @return: (itemPasted, errorMsg)
        @rtype: tuple of (node or None, string)
        """
        #@TODO: REFACTOR and REVIEW this.
        #Many changes made just before v1.1.0 codefreeze for a new must have
        #bug fix -- Ninad 2008-06-06

        #Note about new implementation as of 2008-06-06:
        #When pasting a selection which may contain various groups as
        #well as independent chunks, this method does the following --
        #a) checks if the items to be pasted have at least one Dna object
        #   such as a DnaGroup or DnaStrandOrSegment or a DnaStrandOrAxisChunk
        #If it finds the above, the scale for computing the move offset
        #for pasting all the selection is the one for pasting dna objects
        #(see scale_when_dna_in_newNodeList).
        #- If there are no dna objects AND all pastable items are pure chunks
        # then uses a scale computed using bounding box of the chunks.. if thats
        #too low, then uses 'scale_when_dna_in_newNodeList'
        #for all non 'pure chunk' pastable items, it always uses
        #'scale_when_dna_in_newNodeList'. soon, these scale values will become a
        #user preference. -- Ninad 2008-06-06

        assert isinstance(groupToPaste, Group)

        pastable = groupToPaste
        pos = mousePosition
        newGroup = None
        errorMsg = None
        moveOffset = V(0, 0, 0)

        assy = self.assy

        nodes = list(pastable.members) # used in several places below ### TODO: rename

        newstuff = copied_nodes_for_DND( [pastable],
                                         autogroup_at_top = True, ###k
                                         assy = assy )
        if len(newstuff) == 1:
            # new code (to fix bug 2919) worked, keep using it
            use_new_code = True # to fix bug 2919, but fall back to old code on error [bruce 080718]
            newGroup = newstuff[0]
            newNodeList = list(newGroup.members)
                # copying this is a precaution, probably not needed
        else:
            # new code failed, fall back to old code
            print "bug in fix for bug 2919, falling back to older code " \
                  "(len is %d, should be 1)" % len(newstuff)
            use_new_code = False
            newGroup = Group(pastable.name, assy, None)
                # Review: should this use Group or groupToPaste.__class__,
                # e.g. re a DnaGroup or DnaSegment? [bruce 080314 question]
                # (Yes, to fix bug 2919; or better, just copy the whole node
                #  using the copy function now used on its members
                #  [bruce 080717 reply]. This is now attempted above.)
            newNodeList = copied_nodes_for_DND( nodes,
                                                autogroup_at_top = False,
                                                assy = assy )
            if not newNodeList:
                errorMsg = orangemsg("Clipboard item is probably an empty group. "\
                                     "Paste cancelled")
                    # review: is this claim about the cause always correct?
                    # review: is there any good reason to cancel the paste then?
                    # probably not; not only that, it appears that we *don't* cancel it,
                    # but return something that means we'll go ahead with it,
                    # i.e. the message is wrong. [bruce 080717 guess]
                return newGroup, errorMsg
            pass

        # note: at this point, if use_new_code is false,
        # newGroup is still empty (newNodeList not yet added to it);
        # in that case they are added just before returning.

        selection_has_dna_objects = self._pasteGroup_nodeList_contains_Dna_objects(newNodeList)

        scale_when_dna_in_newNodeList =  env.prefs[pasteOffsetScaleFactorForDnaObjects_prefs_key]
        scale_when_no_dna_in_newNodeList = env.prefs[pasteOffsetScaleFactorForChunks_prefs_key]

        def filterChunks(node):
            """
            Returns True if the given node is a chunk AND its NOT a DnaStrand
            chunk or DnaAxis chunk. Otherwise returns False.
            See also sub-'def filterOtherPastables', which does exactly opposite
            It filters out pastables that are not 'pure chunks'
            """
            if isinstance(node, self.assy.Chunk):
                if not node.isAxisChunk() or node.isStrandChunk():
                    return True
            return False

        def filterOtherPastables(node):
            """
            Returns FALSE if the given node is a chunk AND its NOT a DnaStrand
            chunk or DnaAxis chunk. Otherwise returns TRUE. (does exactly opposite
            of def filterChunks
            @see: sub method filterChunks.
            _getInitialPasteOffsetForPastableNodesc
            """
            if isinstance(node, self.assy.Chunk):
                if not node.isAxisChunk() or node.isStrandChunk():
                    return False
            return True

        chunkList = []
        other_pastable_items = []

        chunkList = filter(lambda newNode: filterChunks(newNode), newNodeList)

        if len(chunkList) < len(newNodeList):
            other_pastable_items = filter(lambda newNode:
                                          filterOtherPastables(newNode),
                                          newNodeList)

        #@see: self._getInitialPasteOffsetForPastableNodes()
        original_copied_nodes = nodes
        if nodes:
            initial_offset_for_chunks, initial_offset_for_other_pastables = \
                                     self._getInitialPasteOffsetForPastableNodes(original_copied_nodes)
        else:
            initial_offset_for_chunks = V(0, 0, 0)
            initial_offset_for_other_pastables = V(0, 0, 0)

        if chunkList:
            boundingBox = BBox()
            for m in chunkList:
                boundingBox.merge(m.bbox)
            approxCenter = boundingBox.center()
            if selection_has_dna_objects:
                scale = scale_when_dna_in_newNodeList
            else:
                #scale that determines moveOffset
                scale = float(boundingBox.scale() * 0.06)
                if scale < 0.001:
                    scale = scale_when_no_dna_in_newNodeList

            if pos:
                moveOffset = pos - approxCenter
            else:
                moveOffset  = scale * self.assy.o.right
                moveOffset += scale * self.assy.o.down
                moveOffset += initial_offset_for_chunks

            #@see: self._getInitialPasteOffsetForPastableNodes()
            self._initial_paste_offset_for_chunks = moveOffset
            #Move the chunks (these will be later added to the newGroup)
            for m in chunkList:
                m.move(moveOffset)

        if other_pastable_items:
            approxCenter = V(0.01, 0.01, 0.01)
            scale = scale_when_dna_in_newNodeList
            if pos:
                moveOffset = pos - approxCenter
            else:
                moveOffset = initial_offset_for_other_pastables
                moveOffset += scale * self.assy.o.right
                moveOffset += scale * self.assy.o.down

            #@see: self._getInitialPasteOffsetForPastableNodes()
            self._initial_paste_offset_for_other_pastables = moveOffset


            for m in other_pastable_items:
                m.move(moveOffset)
            pass

        #Now add all the nodes in the newNodeList to the Group, if needed
        if not use_new_code:
            for newNode in newNodeList:
                newGroup.addmember(newNode)

        assy.addnode(newGroup)
            # review: is this the best place to add it?
            # probably there is no other choice, since it comes from the clipboard
            # (unless we introduce a "model tree cursor" or "current group").
            # [bruce 080717 comment]

        return newGroup, errorMsg

    #Determine if the selection
    def _pasteGroup_nodeList_contains_Dna_objects(self, nodeList): # by Ninad
        """
        Private method, that tells if the given list has at least one dna object
        in it. e.g. a dnagroup or DnaSegment etc.
        Used in self._pasteGroup as of 2008-06-06.

        @TODO: May even be moved to a general utility class
        in dna pkg. (but needs self.assy for isinstance checks)
        """
        # BUG: doesn't look inside Groups. Ignorable,
        # since this method will be removed when paste method is refactored.
        # [bruce 080717 comment]
        for node in nodeList:
            if isinstance(node, self.assy.DnaGroup) or \
               isinstance(node, self.assy.DnaStrandOrSegment):
                return True
            if isinstance(node, Chunk):
                if node.isStrandChunk() or node.isAxisChunk():
                    return True
        return False

    def _getInitialPasteOffsetForPastableNodes(self, original_copied_nodes): # by Ninad
        """
        @see: self._pasteGroup(), self._pasteChunk()
        What it supports:
        1. User selects some objects
        2. Hits Ctrl + C
        3. Hits Ctrl + V
          - first ctrl V  pastes object at an offset, (doesn't recenter the view)
            to the original one
          - 2nd paste offsets it further and like that....

        This fixes bug 2890
        """
        #@TODO: Review this method. It was added just before v1.1.0 to fix a
        #copy-paste-pasteagain-pasteagain bug -- Ninad 2008-06-06

        if same_vals(original_copied_nodes, self._previously_pasted_node_list):
            initial_offset_for_chunks = self._initial_paste_offset_for_chunks
            initial_offset_for_other_pastables = self._initial_paste_offset_for_other_pastables
        else:
            initial_offset_for_chunks = V(0, 0, 0)
            initial_offset_for_other_pastables = V(0, 0, 0)

        self._previously_pasted_node_list = original_copied_nodes

        return initial_offset_for_chunks, initial_offset_for_other_pastables


    def _pasteJig(self, jigToPaste, mousePosition = None):
        """
        Paste the given Jig in the 3D workspace.
        @param jigToPaste: The chunk to be pasted in the 3D workspace
        @type  jigToPaste: L{Jig}

        @param mousePosition: These are the coordinates during mouse double
                              click.
        @type mousePosition:  Array containing the x, y, z position on the
                              screen, or None
        @see: L{self.paste} for implementation notes.

        @return: (itemPasted, errorMsg)
        @rtype: tuple of (node or None, string)
        """

        assert isinstance(jigToPaste, Jig)

        pastable = jigToPaste
        pos = mousePosition
        errorMsg = None
        moveOffset = V(0, 0, 0)

        ## newJig = pastable.copy(None) # BUG: never works (see comment below);
        # inlining it so I can remove that method from Node: [bruce 090113]
        pastable.redmsg("This cannot yet be copied")
        newJig = None # will cause bugs below
            # Note: there is no def copy on Jig or any subclass of Jig,
            # so this would run Node.copy, which prints a redmsg to history
            # and returns None. What we need is new paste code which uses
            # something like the existing code to "copy a list of nodes".
            # Or perhaps a new implem of Node.copy which uses the existing
            # general copy code properly (if pastables are always single nodes).
            # [bruce 080314 comment]

        jigCenter  = newJig.center

        if pos:
            moveOffset = pos - jigCenter
        else:
            moveOffset = 0.2 * self.assy.o.right
            moveOffset += 0.2 * self.assy.o.down

        newJig.move(moveOffset)
        self.assy.addnode(newJig)

        return newJig, errorMsg

    def kill(self):
        print "bug (worked around): assy.kill called, should use its new name delete_sel" #bruce 050927
        if debug_flags.atom_debug:
            print_compact_stack( "atom_debug: assy.kill called, should use its new name delete_sel: ")
        self.delete_sel()

    def delete_sel(self, use_selatoms = True): #bruce 050505 added use_selatoms = True option, so MT ops can pass False (bugfix)
        """
        delete all selected nodes or atoms in this Part
        [except the top node, if we're an immortal Part]
        """
        ###REVIEW: this may not yet work properly for DNA. No time to review or fix for .rc1. [bruce 080414 late]

        #bruce 050419 renamed this from kill, to distinguish it
        # from standard meaning of obj.kill() == kill that obj
        #bruce 050201 for Alpha: revised this to fix bug 370
        ## "delete whatever is selected from this assembly " #e use this in the assy version of this method, if we need one

        cmd = greenmsg("Delete: ")
        info = ""

        ###@@@ #e this also needs a results-message, below.
        if use_selatoms and self.selatoms:
            self.changed()
            nsa = len(self.selatoms) # Get the number of selected atoms before it changes
            if 1:
                #bruce 060328 optimization: avoid creating transient new bondpoints as you delete bonds between these atoms
                # WARNING: the rules for doing this properly are tricky and are not yet documented.
                # The basic rule is to do things in this order, for atoms only, for a lot of them at once:
                # prekill_prep, prekill all the atoms, kill the same atoms.
                val = Atom_prekill_prep()
                for a in self.selatoms.itervalues():
                    a._f_will_kill = val # inlined a._f_prekill(val), for speed
            for a in self.selatoms.values(): # the above can be itervalues, but this can't be!
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
        if self.topnode:
            # This condition is needed because the code above that calls
            # a.kill() may have already deleted the Chunk/Node the atom(s)
            # belonged to. If the current node is a clipboard item part,
            # self no longer has a topnode.  Fixes bug 1466.  mark 060307.
            # [bruce 060307 adds: this only happens if all atoms in the Part
            #  were deleted, and it has no nodes except Chunks. By "the current
            #  node" (which is not a concept we have) I think Mark meant the
            #  former value of self.topnode, when that was a chunk which lost
            #  all its atoms.) See also my comment in cut_sel, which will
            #  someday need this fix [when it can cut atoms].]
            self.topnode.apply2picked(lambda o: o.kill())
        self.invalidate_attr('natoms') #####@@@@@ actually this is needed in the Atom and Chunk kill methods, and add/remove methods
        #bruce 050427 moved win_update into delete_sel as part of fixing bug 566

        env.history.message( cmd + info) # Mark 050715

        self.w.win_update()
        return

    pass # end of class ops_copy_Mixin

# ==

### TODO: after the release, should split this into two files at this point. [bruce 080414 comment]

DEBUG_ORDER = False #bruce 070525, can remove soon

def copied_nodes_for_DND( nodes, autogroup_at_top = False, assy = None, _sort = False):
    """
    Given a list of nodes (which must live in the same Part, though this may go unchecked),
    copy them (into their existing assy, or into a new one if given), as if they were being DND-copied
    from their existing Part, but don't place the copies under any Group (caller must do that).
    Honor the autogroup_at_top option (see class Copier for details).

    @warning: this ignores their order in the list of input nodes, using only their
    MT order (native order within their Part's topnode) to determine the order
    of the returned list of copied nodes. If the input order matters, use
    copy_nodes_in_order instead.

    @note: _sort is a private option for use by copy_nodes_in_order.

    @note: this method is used for several kinds of copying, not only for DND.
    """
    if not nodes:
        return None
    if DEBUG_ORDER:
        print "copied_nodes_for_DND: got nodes",nodes
        print "their ids are",map(id,nodes)
    part = nodes[0].part # kluge
    originals = nodes[:] #k not sure if this list-copy is needed
    copier = Copier(Selection(part, nodes = nodes), assy = assy)
        ### WARNING: this loses all info about the order of nodes! At least, it does once copier copies them.
        # That was indirectly the cause of bug 2403 (copied nodes reversed in DND) -- the caller reversed them
        # to try to compensate, but that had no effect. It might risk bugs in our use for Extrude, as well [fixed now].
        # But for most copy applications (including DND for a general selected set), it does make sense to use MT order
        # rather than the order in which a list of nodes was provided (which in some cases might be selection order
        # or an arbitrary dict-value order). So -- I fixed the DND order bug by reversing the copies
        # (not the originals) in the caller; and I added copy_nodes_in_order for copying a list of nodes
        # in the same order as in the list, and used it in Extrude as a precaution.
        # [bruce 070525]
    copier.prep_for_copy_to_shelf()
    if not copier.ok():
        #e histmsg?
        return None
    nodes = copier.copy_as_list_for_DND() # might be None (after histmsg) or a list
    if _sort:
        # sort the copies to correspond with the originals -- or, more precisely,
        # only include in the output the copies of the originals
        # (whether or not originals are duplicated, or new wrapping nodes were created when copying).
        # If some original was not copied, print a warning (for now only -- later this will be legitimized)
        # and use None in its place -- thus preserving orig-copy correspondence at same positions in
        # input and output lists. [bruce 070525]
        def lookup(orig):
            "return the copy corresponding to orig"
            res = copier.origid_to_copy.get(id(orig), None)
            if res is None:
                print "debug note: copy of %r is None" % (orig,) # remove this if it happens legitimately
            return res
        nodes = map(lookup, originals)
    if nodes and autogroup_at_top:
        if _sort:
            nodes = filter( lambda node: node is not None , nodes)
        nodes = copier.autogroup_if_several(nodes)
    if DEBUG_ORDER:
        print "copied_nodes_for_DND: return nodes",nodes
        print "their ids are",map(id,nodes)
        print "copier.origid_to_copy is",copier.origid_to_copy
        print "... looking at that with id",[(k,id(v)) for (k,v) in copier.origid_to_copy.items()]
    return nodes

def copy_nodes_in_order(nodes, assy = None): #bruce 070525
    """
    Given a list of nodes in the same Part, copy them
    (into their existing assy, or into a new one if given)
    and return the list of copied nodes, in the same order
    as their originals (whether or not this agrees with their
    MT order, i.e. their native order in their Part) -- in fact,
    with a precise 1-1 correspondence between originals and copies
    at the same list positions (i.e. no missing copies --
    use None in their place if necessary).

    See also copied_nodes_for_DND, which uses the nodes' native order instead.
    """
    copies = copied_nodes_for_DND(nodes, assy = assy, _sort = True)
        # if we decide we need an autogroup_at_top option, we'll have to modify this code
    if not copies:
        copies = []
    assert len(copies) == len(nodes) # should be true even if some nodes were not copyable
    return copies

# ==

class Copier: #bruce 050523-050526; might need revision for merging with DND copy
    """
    Control one run of an operation which copies selected nodes and/or atoms.

    @note: When this is passed to Node copy routines, it's referred to in their
           argument names as a mapping.
    """
    def __init__(self, sel, assy = None):
        """
        Create a new Copier for a new (upcoming) copy operation,
        where sel is a Selection object which represents the set of things we'll copy
        (or maybe a superset of that?? #k),
        and assy (optional) is the assembly object which should contain the new node copies
        (if not provided, they'll be in the same assembly as before; all nodes in a Selection object
         must be in a single assembly).
        """
        self.sel = sel
        self.assy = assy or sel.part.assy # the assy into which we'll put copies
            # [new feature, bruce 070430: self.assy can differ from assy of originals -- ###UNTESTED; will use for partlib groups]
        self.objectsCopied = 0  # wware 20051128, bug 1118, no error msg if already given
    def prep_for_copy_to_shelf(self):
        """
        Figure out whether to make a new toplevel Group,
        whether to copy any nonselected Groups or Chunks with selected innards, etc.

        @note: in spite of the name, this is also used by copied_nodes_for_DND
               (which is itself used for several kinds of copying, not only for DND).
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
        if debug_flags.atom_debug and not sel.topnodes:
            print "debug warning: prep_for_copy_to_shelf sees no sel.topnodes"
                #bruce 060627; not always a bug (e.g. happens for copying atoms)
        for node in sel.topnodes: # no need to scan selmols too, it's redundant (and in general a subset)
            # chunks, jigs, Groups -- for efficiency and in case it's a feature,
            # don't scan jigs of a chunk's atoms like we do for individual atoms;
            # this decision might be revised, and if so, we'd scan that here when node is a chunk.
            if node.will_copy_if_selected(sel, True): #wware 060329 added realCopy arg, True to cause non-copy warning to be printed
                # Will this node agree to be copied, if it's selected, given what else is selected?
                # (Can be false for Jigs whose atoms won't be copied, if they can't exist with no atoms or too few atoms.)
                # For Groups, no need to recurse here and call this on members,
                # since we assume the groups themselves always say yes -- #e if that changes,
                # we might need to recurse on their members here if the groups say no,
                # unless that 'no' applies to copying the members too.
                fullcopy[id(node)] = node
        for atom in sel.selatoms.itervalues(): # this use of selatoms.itervalues is only safe because .pick/.unpick is not called
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
        for d in (fullcopy, atom_chunks, atom_chunk_atoms, atom_jigs):  # wware 20051128, bug 1118
            self.objectsCopied += len(d)
            # [note: I am not sure there are not overlaps in these dicts, so this number might be wrong,
            #  but whether it's 0 is right, which is all that matters. But I have not reviewed
            #  whether the code related to how it's used is fully correct. bruce 060627 comment]
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

    # this makes the actual copy (into a known destination) using the info computed above; there are several variants.

    def copy_as_list_for_DND(self): #bruce 050527 added this variant and split out the other one
        """
        Return a list of nodes, or None
        """
        return self.copy_as_list( make_partial_groups = False)

    def copy_as_node_for_shelf(self):
        """
        Create and return a new single node (not yet placed in any Group)
        which is a copy of our selected objects meant for the Clipboard;
        or return None (after history message -- would it be better to let caller do that??)
        if all selected objects refuse to be copied.
        """
        newstuff = self.copy_as_list( make_partial_groups = True) # might be None
        if newstuff is None:
            return None
        return self.wrap_or_rename( newstuff)

    def copy_as_node_for_saving(self): #bruce 050925 for "save selection"
        """
        Copy the selection into a single new node, suitable for saving into a new file;
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
        # review: is this used by anything accessible from the UI?
        if [self.sel.part.topnode] == self.sel.topnodes:
            return (False, self.sel.part.topnode)
        newstuff = self.copy_as_list( make_partial_groups = True) # might be None
        if newstuff is None:
            return (False, None)
        name = "Copied Selection" #k ?? add unique int?
        res = Group(name, self.assy, None, newstuff)
            ### REVIEW: some other subclass of Group?
            # use copy_with_provided_copied_partial_contents?
        return (True, res)

    def copy_as_list(self, make_partial_groups = True):
        """
        [private helper method, used in the above copy_as_xxx methods]

        Create and return a list of one or more new nodes (not yet placed in any Group)
        which is a copy of our selected objects
        (with all ordering in the copy coming from the model tree order of the originals),
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
        #  later. The order of this vs. that vs. group cleanup should not matter.
        #  [update 080414: a comment below, dated [bruce 050704], says it might matter now.])
        halfbonds = {}
        actualbonds = {}
        origid_to_copy = self.origid_to_copy
        for atom2, bond in self.extern_atoms_bonds:
            atom1 = halfbonds.pop(id(bond), None)
            if atom1 is not None:
                na1 = origid_to_copy[id(atom1)]
                na2 = origid_to_copy[id(atom2)]
                bond_copied_atoms(na1, na2, bond, atom1)
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
        ## assert (not self.make_partial_groups) or (not newstuff or len(newstuff) == 1)
        if not ((not self.make_partial_groups) or (not newstuff or len(newstuff) == 1)): # weakened to print, just in case, 080414
            print "fyi: old sanity check failed: assert (not self.make_partial_groups) or (not newstuff or len(newstuff) == 1)"
            # since either verytopnode is a leaf and refused or got copied,
            # or it's a group and copied as one (or all contents refused -- not sure if it copies then #k)
            # (this assert is not required by following code, it's just here as a sanity check)
        # strip off unneeded groups at the top, and return None if nothing got copied
        while len(newstuff) == 1 and \
              self._dissolveable_and_in_tentative_new_groups( newstuff[0]):
            newstuff = newstuff[0].steal_members()
        if not newstuff:
            # everything refused to be copied. Can happen (e.g. for a single selected jig at the top).
            env.history.message( redmsg( "That selection can't be copied by itself." )) ###e improve message
            return None

        # further processing depends on the caller (a public method of this class)
        return newstuff

    def _dissolveable_and_in_tentative_new_groups(self, group): #bruce 080414
        # note: this method name is intended to be findable when searching for tentative_new_groups;
        # otherwise I'd call this _dissolveable_tentative_group.
        res = id(group) in self.tentative_new_groups and \
              not self._non_dissolveable_group(group)
        if DEBUG_COPY and res:
            print "debug copy: discarding the outer Group wrapper of: %r" % group
        return res

    def _non_dissolveable_group(self, group): #bruce 080414
        """
        id(group) is in self.tentative_new_groups, and if it's an ordinary
        Group we will dissolve it and use its members directly,
        since we made it but it was not selected initially during this copy.
        But, not all Groups want us to dissolve them then!
        Return True if this is one of the special kinds that doesn't want that.
        """
        DnaStrandOrSegment = self.assy.DnaStrandOrSegment
        DnaGroup = self.assy.DnaGroup
        return isinstance(group, DnaGroup) or isinstance(group, DnaStrandOrSegment)

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
                #update, bruce 080414: does this ever need to make a special class of Group?
                # answer: not due to its members or where they came from -- if they needed that,
                # then we needed to copy some Group around them when copying them
                # in recurse (the kind of Group it stores in tentative_new_groups).
                # but maybe, if the reason is based on where we plan to *put* the result.
                # AFAIK that never matters yet, except that the reason we autogroup at all
                # is that this matters for the clipboard. If in future we know we're
                # pasting inside a special group (e.g. a DnaGroup), it might matter then
                # (not sure) (alternatively the paste could modify our outer layers,
                # perhaps using our internal record of whether they were tentative).
            newstuff = [res]
        return newstuff

    def wrap_or_rename(self, newstuff):
        # wrap or rename result
        if len(newstuff) > 1: #revised 050527
            newstuff = self.autogroup_if_several(newstuff)
            (res,) = newstuff
                # later comment [bruce 080414]:
                # hmm, I think this means:
                #   assert len(newstuff) == 1
                #   res = newstuff[0]
                # and after the upcoming release I should change it to that
                # as a clarification.
        else:
            res = newstuff[0]
            # now rename it, like old code would do (in mol.copy), though whether
            # this is a good idea seems very dubious to me [bruce 050524]
            if res.name.endswith('-frag'):
                # kluge - in -frag case it's definitely bad to rename the copy, if this op added that suffix;
                # we can't tell, but since it's likely and since this is dubious anyway, don't do it in this case.
                pass
            else:
                res.name = mol_copy_name(res.name, self.assy)
                    # REVIEW: is self.assy correct here, even when we're copying
                    # something from one assy to another? [bruce 080407 Q]
        #e in future we might also need to store a ref to the top original node, top_orig;
        # this is problematic when it was made up as a wrapping group,
        # but if we think of verytopnode as the one, in that case (always a group in that case), then it's probably ok...
        # for now we don't attempt this, since when we removed useless outer groups we didn't keep track of the original node.

        ##e this is where we'd like to recenter the view (rather than the object, as the old code did for single chunks),
        # but I'm not sure exactly how, so I'll save this for later. ###@@@

        return res

        ##e ideally we'd implem atoms & bonds differently than now, and copy using Numeric, but not for now.

    def recurse(self, orig): #e rename
        """
        copy whatever is needed from orig and below, but don't fix refs
        immediately; append new copies to self.newstuff.

        @note: this is initially called on self.verytopnode.
        """
        # review: should this method be renamed as private? [bruce 080414 comment]
        idorig = id(orig)
        res = None # default result, changed in many cases below
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
            # [note, update 080414: 'copy_partial_in_mapping' is used in class Node as an alias
            #  for (the Node implem of) copy_full_in_mapping, even though it's never called.]
            res = orig.copy_full_in_mapping(self)
        elif orig.is_group():
            # what this section does depends on self.make_partial_groups, so is described
            # differently below in each clause of the following 'if' statement
            # [bruce 080414 comments]:
            if self.make_partial_groups: #bruce 050527 made this optional so DND copy can not do it
                # copy whatever needs copying from orig into a new self.newstuff
                # that is initially [], and is the local var newstuff in later code,
                # with the initial self.newstuff unchanged
                save = self.newstuff
                self.newstuff = []
            map( self.recurse, orig.members)
            if self.make_partial_groups: #050527
                newstuff = self.newstuff
                self.newstuff = save
            else:
                newstuff = None
                ## print "not self.make_partial_groups" # fyi: this does happen, for DND of copied nodes onto a node
                ###BUG: this does not yet work properly for DNA. No time to fix for .rc1. [bruce 080414 late]
            if newstuff:
                # if self.make_partial_groups, this means: if anything in orig was copied.
                # otherwise, this means: always false (don't run this code).
                # [bruce 080414 comment]

                # we'll make some sort of Group from newstuff, as a partial copy of orig
                # (note that orig is a group which was not selected, so is only needed
                #  to hold copies of selected things inside it, perhaps at lower levels
                #  than its actual members)

                # first, if newstuff has one element which is a Group we made,
                # decide whether to merge it into the group we'll make as a partial copy
                # of orig, or not. As part of fixing copy of Dna bugs [bruce 080414],
                # I'll modify this to never dissolve a DnaStrandOrSegment or a DnaGroup.
                # After the release we can figure out a more principled way of asking
                # the group whether to dissolve it here -- this might be determinable
                # from existing Group API attrs or methods, or require new ones.
                # (Note that debug prefs that open up groups in the MT for seeing into
                #  or ungrouping should *not* thereby affect copy behavior, even if they
                #  affect MT drop-on behavior.)

                # make sure i got these attr names right [remove when works]
                DnaStrandOrSegment = self.assy.DnaStrandOrSegment
                DnaGroup = self.assy.DnaGroup

                if len(newstuff) == 1 and \
                   self._dissolveable_and_in_tentative_new_groups( newstuff[0]):
                    # merge names (and someday, pref settings) of orig and newstuff[0]
                    #update, bruce 080414: use non_dissolveable_group to not merge them
                    # if special classes (i.e. DnaStrandOrSegment, DnaGroup)
                    # unless they are a special case that is mergable in a special way
                    # (hopefully controlled by methods on one or both of the orig objects)
                    # (no such special case is yet needed).
                    innergroup = newstuff[0]
                    name = orig.name + '/' + innergroup.name
                    newstuff = innergroup.steal_members()
                        # no need to recurse, since innergroup
                        # would have merged with its own member if possible
                else:
                    name = orig.name
                ## res = Group(name, self.assy, None, newstuff)
                res = orig.copy_with_provided_copied_partial_contents( name, self.assy, None, newstuff ) #bruce 080414
                    # note: if newstuff elements are still members of innergroup
                    # (not sure if this is true after steal_members! probably not. should review.),
                    # this constructor call pulls them out of innergroup (slow?)
                    #update, bruce 080414: this probably needs to make a special class of Group
                    # (by asking orig what class to use) in some cases... now it does!
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
        """
        Subclass-specific copy methods should call this to record the fact that orig
        (a node or a component of one, e.g. an atom or perhaps even a bond #k)
        is being copied as 'copy' in this mapping.
        (When this is called, copy must of course exist, but need not be "ready for use" --
         e.g. it's ok if orig's components are not yet copied into copy.)
        Also asserts orig was not already copied.
        """
        assert not self.origid_to_copy.has_key(id(orig))
        self.origid_to_copy[id(orig)] = copy

    def do_at_end(self, func): #e might change to dict
        """
        Node-specific copy methods can call this
        to request that func be run once when the entire copy operation is finished.
        Warning: it is run before [###doc -- before what?].
        """
        self.do_these_at_end.append(func)

    pass # end of class Copier

# end
