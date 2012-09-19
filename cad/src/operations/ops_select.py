# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
ops_select.py -- operations and internal methods for changing what's selected
and maintaining other selection-related state. (Not well-organized.)

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 050507 made this by collecting appropriate methods from class Part.

Various improvements since then, by various developers.

TODO: probably needs some refactoring, judging by the imports
as of 080414.
"""

from utilities.constants import SELWHAT_CHUNKS, SELWHAT_ATOMS
from utilities.constants import diINVISIBLE, diDEFAULT
from model.global_model_changedicts import _changed_picked_Atoms
from model.chunk import Chunk
from model.elements import Singlet
from geometry.VQT import V, A, norm, cross
from Numeric import dot, transpose
import foundation.env as env
from utilities.Log import redmsg, greenmsg, orangemsg
from utilities.debug import print_compact_traceback
from utilities import debug_flags
from platform_dependent.PlatformDependent import fix_plurals
from utilities.GlobalPreferences import permit_atom_chunk_coselection
from utilities.icon_utilities import geticon

from dna.model.DnaGroup import DnaGroup
from dna.model.DnaStrand import DnaStrand

from foundation.Group import Group
from dna.model.DnaLadderRailChunk import DnaAxisChunk
from dna.model.DnaLadderRailChunk import DnaStrandChunk
from dna.model.DnaMarker import DnaMarker
from dna.model.DnaSegment import DnaSegment
from cnt.model.NanotubeSegment import NanotubeSegment

# Object flags, used by objectSelected() and its callers.
ATOMS = 1
CHUNKS = 2
JIGS = 4
DNASTRANDS = 8
DNASEGMENTS = 16
DNAGROUPS = 32
ALLOBJECTS = ATOMS | CHUNKS | JIGS | DNASTRANDS | DNASEGMENTS | DNAGROUPS

def objectSelected(part, objectFlags = ALLOBJECTS): # Mark 2007-06-24
    """
    Returns True if anything is selected (i.e. atoms, chunks, jigs, etc.).
    Returns False if nothing is selected.

    <objectFlags> is an enum used to test for specific object types, where:

        ATOMS = 1
        CHUNKS = 2
        JIGS = 4
        DNASTRANDS = 8
        DNASEGMENTS = 16
        DNAGROUPS = 32
        ATOMS | CHUNKS | JIGS | DNASTRANDS | DNASEGMENTS | DNAGROUPS
    """

    if objectFlags & ATOMS:
        if part.selatoms_list():
            return True

    if objectFlags & CHUNKS:
        if part.selmols:
            return True

    if objectFlags & JIGS:
        if part.getSelectedJigs():
            return True

    if objectFlags & DNASTRANDS:
        if part.getSelectedDnaStrands():
            return True

    if objectFlags & DNASEGMENTS:
        if part.getSelectedDnaSegments():
            return True

    if objectFlags & DNAGROUPS:
        if part.getSelectedDnaGroups():
            return True

    return False

def renameableLeafNode(obj, groups_renameable = False): # probably by Mark
    """
    Returns True if obj is a visible, renameable leaf node in the model tree.
    Otherwise, returns False.

    If obj is a Group or DnaGroup and groups_renameable is True,
    return True.
    """
    # TODO: refactor this so that it doesn't hardcode a lot of classes.
    # (The result is probably deducible from existing class attrs;
    #  if not, we should add one. There might already be a method on
    #  class Node related to this -- see try_rename or its calls to find out.)
    # [bruce 081124 comment]

    _nodeList = [[DnaAxisChunk,    False], # Chunk subclass
                 [DnaStrandChunk,  False], # Chunk subclass
                 [DnaMarker,       False], # Jig subclass
                 [DnaSegment,      True], # Group subclass
                 [DnaStrand,       True], # Group subclass
                 [NanotubeSegment, True], # Group subclass
                 [DnaGroup,        groups_renameable], # Group subclass
                 [Group,           groups_renameable]] # Group must be last in list.

    if not obj.rename_enabled():
        return False

    for _class, _renameable in _nodeList:
        if isinstance(obj, _class):
            return _renameable

    return True

class ops_select_Mixin:
    """
    Mixin class for providing selection methods to class L{Part}.
    """

    # functions from the "Select" menu
    # [these are called to change the set of selected things in this part,
    #  when it's the current part; these are event handlers which should
    #  do necessary updates at the end, e.g. win_update, and should print
    #  history messages, etc]

    def selectionContainsAtomsWithOverriddenDisplay(self):
        """
        Checks if the current selection contains any atoms that have
        its display mode not set to B{diDEFAULT}.

        @return: True if there is one or more selected atoms with its
                 display mode not set to B{diDEFAULT}.
        @rtype:  bool

        @note: It doesn't consider atoms in a chunk or of a jig if they
               (the atoms) are not explicitely selected.
        """
        for a in self.getOnlyAtomsSelectedByUser():
            if a.display != diDEFAULT:
                return True
        return False

    def selectionContainsInvisibleAtoms(self):
        """
        Checks if the current selection contains any atoms that have
        its display mode set to B{diINVISIBLE}.

        @return: True if there is one or more selected atoms with its display
                 mode set to B{diINVISIBLE}.
        @rtype:  bool

        @note: It doesn't consider atoms in a chunk or of a jig if they
               (the atoms) are not explicitely selected.
        """
        for a in self.getOnlyAtomsSelectedByUser():
            if a.display == diINVISIBLE:
                return True
        return False

    def getSelectedAtoms(self): #mark 060122
        """
        Returns a list of all the selected atoms, including those of selected
        chunks and jigs.

        @return: List of selected atoms.
        @rtype:  list
        """
        atoms = []

        for chunk in self.assy.selmols[:]:
            atoms += chunk.atoms.values()

        for jig in self.assy.getSelectedJigs():
            atoms += jig.atoms

        atoms += self.assy.selatoms_list()

        return atoms

    def getOnlyAtomsSelectedByUser(self): #ninad 0600818
        """
        Returns a list of atoms selected by the user. It doesn't consider atoms
        in a chunk or of a jig if they (the atoms) are not explicitely selected.
        """
        #ninad060818 is using this function to get distance and other info in the DynamiceTooltip class.
        atoms = []
        atoms += self.assy.selatoms_list()
        return atoms


    def getSelectedJigs(self):
        """
        Returns a list of all the currently selected jigs.
        @see: MWsemantics.activateDnaTool
        """
        selJigs = []
        def addSelectedJig(obj, jigs=selJigs):
            if obj.picked and isinstance(obj, self.win.assy.Jig):
                jigs += [obj]

        self.topnode.apply2all(addSelectedJig)
        return selJigs

    def getSelectedPlanes(self):
        """
        Returns a list of selected planes.
        @see: self.getSelectedJigs()
        """
        selectedJigs = self.getSelectedJigs()

        selectedPlanes = filter(lambda p:
                                isinstance(p, self.win.assy.Plane),
                                selectedJigs)
        return selectedPlanes

    def getSelectedDnaGroups(self):
        """
        Returns a list of the currently selected DnaGroup(s).

        """

        selDnaGroupList = []
        def addSelectedDnaGroup(obj, dnaList = selDnaGroupList):
            if obj.picked and isinstance(obj, DnaGroup):
                dnaList += [obj]

        self.topnode.apply2all(addSelectedDnaGroup)
        return selDnaGroupList

    def getSelectedDnaStrands(self):
        """
        Returns a list of the currently selected DnaStrand(s).

        """

        selDnaStrandList = []
        def addSelectedDnaStrand(obj, dnaList = selDnaStrandList):
            if obj.picked and isinstance(obj, DnaStrand):
                dnaList += [obj]

        self.topnode.apply2all(addSelectedDnaStrand)
        return selDnaStrandList

    def getSelectedDnaSegments(self):
        """
        Returns a list of the currently selected DnaSegment(s).

        """

        selDnaSegmentList = []
        def addSelectedDnaSegment(obj, dnaList = selDnaSegmentList):
            if obj.picked and isinstance(obj, self.win.assy.DnaSegment):
                dnaList += [obj]

        self.topnode.apply2all(addSelectedDnaSegment)
        return selDnaSegmentList

    def getSelectedNanotubeSegments(self):
        """
        @return: a list of the currently selected NanotubeSegments
        """
        selNanotubeSegmentList = []
        def addSelectedNanotubeSegment(obj, ntSegmentList = selNanotubeSegmentList):
            if obj.picked and isinstance(obj, self.win.assy.NanotubeSegment):
                ntSegmentList += [obj]
            return
        self.topnode.apply2all(addSelectedNanotubeSegment)
        return selNanotubeSegmentList

    def getSelectedNanotubeSegment(self):
        """
        Returns only the currently selected nanotubeSegment, if any.
        @return: the currently selected nanotubeSegment or None if no
                 nanotubeSegments are selected. Also returns None if more
                 than one nanotubeSegment is select.
        @rtype: L{Chunk}
        @note: use L{getSelectedNanotubeSegments()} to get the list of all
               selected nanotubeSegments.
        """
        selectedNanotubeSegmentList = self.getSelectedNanotubeSegments()
        if len(selectedNanotubeSegmentList) == 1:
            return selectedNanotubeSegmentList[0]
        else:
            return None
        return

    def getSelectedProteinChunks(self):
        """
        @return: a list of the currently selected Protein chunks
        """
        selProteinList = []
        def addSelectedProteinChunk(obj, proteinList = selProteinList):
            if obj.picked and \
               isinstance(obj, self.win.assy.Chunk) and \
               obj.isProteinChunk():
                proteinList += [obj]
            return
        self.topnode.apply2all(addSelectedProteinChunk)
        return selProteinList

    def getSelectedProteinChunk(self):
        """
        Returns only the currently selected protein chunk, if any.
        @return: the currently selected protein chunk or None if no peptide
                 chunks are selected. Also returns None if more than one
                 peptide chunk is select.
        @rtype: L{Chunk}
        @note: use L{getSelectedProteinChunks()} to get the list of all
               selected proteins.
        """
        selectedProteinList = self.getSelectedProteinChunks()
        if len(selectedProteinList) == 1:
            return selectedProteinList[0]
        else:
            return None
        return

    def getNumberOfSelectedChunks(self):
        """
        Returns the number of selected chunks.

        @note:Atoms and jigs are not counted.
        """
        return len(self.assy.selmols)

    def getNumberOfSelectedJigs(self):
        """
        Returns the number of selected jigs.

        @note:Atoms and chunks are not counted.
        """
        return len(self.assy.getSelectedJigs())

    def getSelectedMovables(self): # Renamed from getMovables().  mark 060124.
        """
        Returns the list of all selected nodes that are movable.
        """
        selected_movables = []
        def addMovableNode(obj, nodes=selected_movables):
            if obj.picked and obj.is_movable:
                nodes += [obj]
        self.topnode.apply2all(addMovableNode)
        return selected_movables

    def getSelectedRenameables(self):
        """
        Returns the list of all selected nodes that can be renamed.
        """
        selected_renameables = []
        def addRenameableNode(obj, nodes=selected_renameables):
            if obj.picked and obj.rename_enabled():
                nodes += [obj]
        self.topnode.apply2all(addRenameableNode)
        return selected_renameables

    def getSelectedNodes(self):
        """
        Return a list of all selected nodes in the MT.
        """
        selected_nodes = []
        def func(obj):
            if obj.picked:
                selected_nodes.append(obj)
        self.topnode.apply2all(func)
        return selected_nodes


    def selectAll(self):
        """
        Select all atoms or all chunks, depending on the select mode.

        @note: The selection filter is applied if it is enabled.
        """
        self.begin_select_cmd() #bruce 051031
        if self.selwhat == SELWHAT_CHUNKS:
            for m in self.molecules:
                m.pick()
            #Call Graphics mode API method to do any additinal selection
            #(example select an entire DnaGroup if all its contents are selected
            #@see: basicGraphicsMode.end_selection_from_GLPane()
            currentCommand = self.w.commandSequencer.currentCommand
            currentCommand.graphicsMode.end_selection_from_GLPane()
        else:
            assert self.selwhat == SELWHAT_ATOMS
            for m in self.molecules:
                for a in m.atoms.itervalues():
                    a.pick()
        self.w.win_update()

    def selectNone(self):
        self.begin_select_cmd() #bruce 051031
        self.unpickall_in_win()
        self.w.win_update()

    def selectInvert(self):
        """
        If some parts are selected, select the other parts instead.
        If some atoms are selected, select the other atoms instead
        (even in chunks with no atoms selected, which end up with
        all atoms selected). (And unselect all currently selected
        parts or atoms.)

        @note: when atoms are selected, only affects atoms as permitted by the
        selection filter.
        """ #bruce 060331 revised docstring
        #bruce 060721 comments: this is problematic #####@@@@@ as we move to more general selection semantics.
        # E.g. -- can it select atoms inside a CylinderChunk? It probably shouldn't, but now it can.
        # (If some in it are already selected, then maybe, but not if they are not, and maybe that should
        #  never be permitted to occur.)
        # E.g. -- what if there are atoms selected inside chunks that are selected?
        # (Even if not, how do you decide whether unselected stuff gets selected as atoms or chunks?
        #  Now, this depends on the mode (Build -> atoms, Extrude -> Chunks); maybe that makes sense --
        #  select things in the smallest units that could be done by clicking (for CylChunks this will mean chunks).)
        self.begin_select_cmd() #bruce 051031
        cmd = "Invert Selection: "
        env.history.message(greenmsg(cmd))

        # revised by bruce 041217 after discussion with Josh;
        # previous version inverted selatoms only in chunks with
        # some selected atoms.
        if self.selwhat == SELWHAT_CHUNKS:
            newpicked = filter( lambda m: not m.picked, self.molecules )
            self.unpickparts()
            for m in newpicked:
                m.pick()
            #Call Graphics mode API method to do any additinal selection
            #(example select an entire DnaGroup if all its contents are selected
            #@see: basicGraphicsMode.end_selection_from_GLPane()
            currentCommand = self.w.commandSequencer.currentCommand
            currentCommand.graphicsMode.end_selection_from_GLPane()
        else:
            assert self.selwhat == SELWHAT_ATOMS
            for m in self.molecules:
                for a in m.atoms.itervalues():
                    if a.picked: a.unpick()
                    else: a.pick()

        # Print summary msg to history widget.  Always do this before win/gl_update.
        env.history.message("Selection Inverted")

        self.w.win_update()

    def expandDnaComponentSelection(self, dnaStrandOrSegment):
        """
        Expand the DnaComponent selection. DnaComponent can be a strand or a
        segment.
        For DnaSegment -- it selects that dna segment and the adjacent segments
        reachable through crossovers.
        For DnaStrand it selects that strand and all the complementary strands.
        @see: self._expandDnaSegmentSelection()
        @see: SelectChunks_GraphicsMode.chunkLeftDouble()
        @see: DnaStrand.get_DnaStrandChunks_sharing_basepairs()
        @see: DnaSegment.get_DnaSegments_reachable_thru_crossovers()
        @see: NFR bug 2749 for details.
        """
        if isinstance(dnaStrandOrSegment, self.win.assy.DnaStrand):
            self._expandDnaStrandSelection(dnaStrandOrSegment)
        elif isinstance(dnaStrandOrSegment, self.win.assy.DnaSegment):
            self._expandDnaSegmentSelection(dnaStrandOrSegment)

        currentCommand = self.w.commandSequencer.currentCommand
        currentCommand.graphicsMode.end_selection_from_GLPane()
        self.win.win_update()


    def _expandDnaSegmentSelection(self, dnaSegment):
        """
        Expand the selection of such that the segment <dnaSegment> and all its
        adjacent DnaSegments reachable through the crossovers, are selected.
        @see:self.expandDnaComponentSelection()
        """
        assert isinstance(dnaSegment, self.win.assy.DnaSegment)
        segmentList = [dnaSegment]
        segmentList.extend(dnaSegment.get_DnaSegments_reachable_thru_crossovers())
        for segment in segmentList:
            if not segment.picked:
                segment.pick()

    def _expandDnaStrandSelection(self, dnaStrand):
        """
        Expand the selection such that the <dnaStrand> and all its complementary
        strand chunks are selected.
        """
        assert isinstance(dnaStrand, self.win.assy.DnaStrand)
        lst = dnaStrand.getStrandChunks()
        lst.extend(dnaStrand.get_DnaStrandChunks_sharing_basepairs())

        for c in lst:
            if not c.picked:
                c.pick()

    def contractDnaComponentSelection(self, dnaStrandOrSegment):
        """
        Contract the selection such that:

        If is a DnaStrand, then that strand and all its complementary
        strand chunks are deselected.

        If its a DnaSegment, then that segment and its adjacent segments reachable
        through cross overs are deselected.

        @see:self._contractDnaStrandSelection()
        @see: self._contractDnaSegmentSelection()
        @see: SelectChunks_GraphicsMode.chunkLeftDouble()
        @see: DnaStrand.get_DnaStrandChunks_sharing_basepairs()
        @see: DnaSegment.get_DnaSegments_reachable_thru_crossovers()
        @see: NFR bug 2749 for details.
        """
        if isinstance(dnaStrandOrSegment, self.win.assy.DnaStrand):
            self._contractDnaStrandSelection(dnaStrandOrSegment)
        elif isinstance(dnaStrandOrSegment, self.win.assy.DnaSegment):
            self._contractDnaSegmentSelection(dnaStrandOrSegment)

    def _contractDnaStrandSelection(self, dnaStrand):
        assert isinstance(dnaStrand, self.win.assy.DnaStrand)
        assert isinstance(dnaStrand, self.win.assy.DnaStrand)
        lst = dnaStrand.getStrandChunks()
        lst.extend(dnaStrand.get_DnaStrandChunks_sharing_basepairs())

        for c in lst:
            if c.picked:
                c.unpick()

    def _contractDnaSegmentSelection(self, dnaSegment):
        """
        Contract the selection of the picked DnaSegments such that the segment
        <dnaSegment> and all its adjacent DnaSegments reachable through the
        crossovers, are deselected.
        """
        assert isinstance(dnaSegment, self.win.assy.DnaSegment)
        segmentList = [dnaSegment]
        segmentList.extend(dnaSegment.get_DnaSegments_reachable_thru_crossovers())
        for segment in segmentList:
            if segment.picked:
                segment.unpick()


    def selectExpand(self):
        """
        Select any atom that is bonded to any currently selected atom,
        and whose selection is permitted by the selection filter.
        """ #bruce 060331 revised docstring
        # Eric really needed this.  Added by Mark 050923.
        # (See also Selection.expand_atomset method. [bruce 051129])

        self.begin_select_cmd() #bruce 051031
        cmd = "Expand Selection: "
        env.history.message(greenmsg(cmd))
            #bruce 051129 comment: redundancy of greenmsg is bad, but self.selatoms can take time to compute,
            # so I decided against fixing the redundancy by moving this below the "No atoms selected" test.

        if not self.selatoms:
            env.history.message(greenmsg(cmd) + redmsg("No atoms selected."))
            return

        num_picked = 0 # Number of atoms picked in the expand selection.

        for a in self.selatoms.values():
            if a.picked: #bruce 051129 comment: this is presumably always true
                for n in a.neighbors():
                    if not n.picked:
                        n.pick()
                        if n.picked:
                            #bruce 051129 added condition to fix two predicted miscount bugs (don't know if reported):
                            # - open bonds can't be picked (.pick is always a noop for them)
                            # - some elements can't be picked when selection filter is on (.pick is a noop for them, too)
                            # Note that these bugs might have caused those unselected atoms to be counted more than once,
                            # not merely once (corrected code counts them 0 times).
                            num_picked += 1

        # Print summary msg to history widget.  Always do this before win/gl_update.
        msg = fix_plurals(str(num_picked) + " atom(s) selected.")
        env.history.message(msg)

        self.w.win_update()

    def selectContract(self):
        """
        Unselects any atom which has a bond to an unselected atom, or which has any open bonds,
        and whose unselection is permitted by the selection filter.
        """ #bruce 060331 revised docstring
        # Added by Mark 050923.

        self.begin_select_cmd() #bruce 051031
        cmd = "Contract Selection: "
        env.history.message(greenmsg(cmd))

        if not self.selatoms:
            env.history.message(greenmsg(cmd) + redmsg("No atoms selected."))
            return

        contract_list = [] # Contains list of atoms to be unselected.

        assert self.selwhat == SELWHAT_ATOMS
        for a in self.selatoms.values():
            if a.picked:
                # If a selected atom has an unpicked neighbor, it gets added to the contract_list
                # Bruce mentions: you can just scan realNeighbors if you want to only scan
                # the non-singlet atoms. Users may desire this behavior - we can switch it on/off
                # via a dashboard checkbox or user pref if we want.  Mark 050923.
                for n in a.neighbors():
                    if not n.picked:
                        contract_list.append(a)
                        break

        # Unselect the atom in the contract_list
        #bruce 051129 comment: this appears to contain only unique picked atoms (based on above code),
        # and any atom can be unpicked (regardless of selection filter) [this later became WRONG; see below],
        # so using its len as a count of changed atoms, below, is probably correct.
        #bruce 060331 comment & bugfix: sometime since the above comment, unpick started using selection filter.
        # So I'll fix the atom count for the history message.
        natoms = 0
        for a in contract_list:
            if not a.picked:
                continue #bruce 060331 precaution, for correct count (not needed for current code above)
            a.unpick()
            if not a.picked: # condition is due to selection filter
                natoms += 1

        # Print summary msg to history widget.
        msg = fix_plurals(str(natoms) + " atom(s) unselected.")
        env.history.message(msg)

        self.w.win_update() # Needed? Mark 2008-02-14

    def lockSelection(self, lockState):
        """
        Enable/disable the mouse "selection lock". When enabled, selection
        operations using the mouse (i.e. clicks and drags) are disabled in the
        3D graphics area (glpane). All other selection commands via the
        toolbar, menus, model tree and keyboard shortcuts are not affected by
        the selection lock state.

        @param lockState: The selection lock state, where:
                        - True  = selection locked
                        - False = selection unlocked
        @type  lockState: boolean
        """
        if lockState:
            self.w.selectLockAction.setIcon(
                geticon("ui/actions/Tools/Select/Selection_Locked.png"))
        else:
            self.w.selectLockAction.setIcon(
                geticon("ui/actions/Tools/Select/Selection_Unlocked.png"))

        self.o.mouse_selection_lock_enabled = lockState
        # Update the cursor and statusbar.
        self.o.setCursor()

        if 0:
            print "mouse_selection_lock_enabled=", \
                  self.o.mouse_selection_lock_enabled

    def hideSelection(self):
        """
        Hides the current selection. Selected atoms are made invisible.
        Selected chunks and/or any other object (i.e. jigs, planes, etc.)
        are hidden.
        """
        # Added by Mark 2008-02-14. [slight revisions, bruce 080305]

        cmd = "Hide: "
        env.history.message(greenmsg(cmd))

        # Hide selected objects.
        self.assy.Hide()

        if self.selatoms:
            # Hide selected atoms by changing their display style to invisible.
            for a in self.selatoms.itervalues():
                a.setDisplayStyle(diINVISIBLE)
        return

    def unhideSelection(self):
        """
        Unhides the current selection.

        If the current selection mode is "Select Chunks", the selected nodes
        (i.e. chunks, jigs, planes, etc.) are unhidden. If all the nodes
        were already visible (unhidden), then we unhide any invisble atoms
        inside chunks by changing their display style to default (even if
        their display style before they were hidden was something different).

        If the current selection mode is "Select Atoms (i.e. Build Atoms), then
        the selected atoms are made visible by changing their display style
        to default (even if their display style before they were hidden
        was something different).
        """
        # Added by Mark 2008-02-25. [slight revisions, bruce 080305]
        # [subsequently modified and/or bugfixed by Ninad]

        # TODO: fix possible speed issue: this looks like it might be slow for
        #  deep nesting in model tree, since it may unhide selected groups
        #  as a whole, as well as each node they contain. [bruce 081124 comment]

        cmd = "Unhide: "
        env.history.message(greenmsg(cmd))

        _node_was_unhidden = False

        selectedNodes = self.getSelectedNodes()

        # Unhide any movables. This includes chunks, jigs, etc. (but not atoms).
        for node in selectedNodes:
            if node.hidden:
                _node_was_unhidden = True
                node.unhide()

        if _node_was_unhidden:
            self.w.win_update()
            return

        if not self.selatoms:
            # Unhide any invisible atoms in the selected chunks.
            for chunk in self.assy.selmols[:]:
                for a in chunk.atoms.itervalues():
                    a.setDisplayStyle(diDEFAULT)
        else:
            # Unhide selected atoms by changing their display style to default.
            for a in self.selatoms.itervalues():
                a.setDisplayStyle(diDEFAULT)
        self.w.win_update()
        return

    # ==

    def selectChunksWithSelAtoms(self): #bruce 060721 renamed from selectParts; see also permit_pick_parts
        """
        Change this Part's assy to permit selected chunks, not atoms,
        but select all chunks which contained selected atoms;
        then win_update
        [warning: not for general use -- doesn't change which select mode is in use]
        """
        # This is called by Move_GraphicsMode.Enter_GraphicsMode.
        # (Why not selectChunksMode? because SelectChunks_GraphicsMode calls it w/o update, instead:
        #   self.o.assy.selectChunksWithSelAtoms_noupdate() # josh 10/7 to avoid race in assy init
        # )
        # BTW, MainWindowUI.{py,ui} has an unused slot with the same name this method used to have [selectParts]
        # [bruce 050517/060721 comment and docstring]
        self.selectChunksWithSelAtoms_noupdate()
        self.w.win_update()

    def selectChunksWithSelAtoms_noupdate(self): #bruce 060721 renamed from pickParts; see also permit_pick_parts
        """
        Change this Part's assy to permit selected chunks, not atoms,
        but select all chunks which contained selected atoms; do no updates
        [warning: not for general use -- doesn't change which select mode is in use]
        """
        #bruce 050517 added docstring
        lis = self.selatoms.values()
        self.unpickatoms() # (not sure whether this is still always good, but probably it's ok -- bruce 060721)
        for atm in lis:
            atm.molecule.pick()
        self.assy.set_selwhat(SELWHAT_CHUNKS) #bruce 050517 revised API of this call
            #bruce 050517: do this at the end, to avoid worry about whether
            # it is later given the side effect of unpickatoms.
            # It's redundant only if lis has any atoms.
        return

    def permit_pick_parts(self): #bruce 050125; see also selectChunksWithSelAtoms_noupdate, but that can leave some chunks initially selected
        """
        Ensure it's legal to pick chunks using mouse selection, and deselect
        any selected atoms (if picking chunks does so).
        """
        #bruce 060414 revised this to try to fix bug 1819
        # (and perhaps related bugs like 1106, where atoms & chunks are both selected)
        if permit_atom_chunk_coselection(): #bruce 060721
            return

        if self.selatoms and self.assy.selwhat == SELWHAT_CHUNKS and env.debug():
            print "debug: bug: permit_pick_parts sees self.selatoms even though self.assy.selwhat == SELWHAT_CHUNKS; unpicking them"
                # Note: this happens during bug 1819, and indicates a bug in the code that led up to here,
                # probably something about selatoms being per-part, but selwhat (and MT part-switch conventions re selection)
                # being for the assy -- maybe we need to deselect atoms, not only chunks, when switching parts (not yet done).
                # In the meantime, warn only the developer, and try to fix the situation
                # by doing the following anyway (which the pre-060414 code did not).
        if self.selatoms:
            self.unpickatoms()
        self.assy.set_selwhat(SELWHAT_CHUNKS) # not super-fast (could optim using our own test), but that's ok here
        return

    def permit_pick_atoms(self): #bruce 050517 added this for use in some mode Enter methods -- but not sure they need it!
        """
        Ensure it's legal to pick atoms using mouse selection, and deselect any
        selected chunks (if picking atoms does so).
        """
        if permit_atom_chunk_coselection(): #bruce 060721
            return
        ## if self.assy.selwhat != SELWHAT_ATOMS:
        if 1: # this matters, to callers who might have jigs selected
            self.unpickchunks() # only unpick chunks, not jigs. mark 060309.
            self.assy.set_selwhat(SELWHAT_ATOMS) #bruce 050517 revised API of this call
        return

    # == selection functions using a mouse position

    # REVIEW: we should probably move some of these, especially findAtomUnderMouse,
    # to GraphicsMode instead (once it's split from basicMode), since they depend
    # on model-specific graphical properties. [bruce 071008]

    # (Note: some of these are not toplevel event handlers)

    # dumb hack: find which atom the cursor is pointing at by
    # checking every atom...
    # [bruce 041214 comment: findpick is now mostly replaced by findAtomUnderMouse;
    #  its only remaining call is in depositMode.getcoords, which uses a constant
    #  radius other than the atoms' radii, and doesn't use iPic or iInv,
    #  but that too might be replaced in the near future, once bug 269 response
    #  is fully decided upon.
    #  Meanwhile, I'll make this one only notice visible atoms, and clean it up.
    #  BTW it's now the only caller of atom.checkpick().]

    def findpick(self, p1, v1, r=None):
        distance = 1000000
        atom = None
        for mol in self.molecules:
            if mol.hidden:
                continue
            disp = mol.get_dispdef()
            for a in mol.atoms.itervalues():
                if not a.visible(disp):
                    continue
                dist = a.checkpick(p1, v1, disp, r, None)
                if dist:
                    if dist < distance:
                        distance = dist
                        atom = a
        return atom

    def _decide_water_cutoff(self): #bruce 071008 split this out
        """
        Decide what value of water_cutoff to pass to self.findAtomUnderMouse.
        """
        # I'm not sure if this is really an aspect of the currentCommand
        # or of the graphics mode -- maybe the currentCommand
        # since that does or doesn't offer UI control of water,
        # or maybe the graphicsMode since that does or doesn't display it.
        # Someone should figure this out and clean it up.
        # Best guess at the right cleanup: graphicsModes should all have
        # common boolean water_enabled and float water_depth attributes,
        # used for both drawing and picking in a uniform way.
        # But I won't do it that way here, since I'm imitating the prior code.
        # (BTW note that self.findAtomUnderMouse is not private, and has
        #  external callers which pass their own water_enabled flag to it.
        #  So we can't just inline this into it.)
        # [bruce 071008]
        #UPDATE 2008-08-01: Water surface is currently an aspect of the
        #command class rather than graphicsMode class. The graphicsmode checks
        #it by calling self.command.isWaterSurfaceEnabled() --[ Ninad comment]
        commandSequencer = self.win.commandSequencer
        if commandSequencer.currentCommand.commandName == 'DEPOSIT':
            return True
        else:
            return False
        pass

    # bruce 041214, for fixing bug 235 and some unreported ones:
    def findAtomUnderMouse(self, event, water_cutoff = False, singlet_ok = False):
        """
        Return the atom (if any) whose front surface should be visible at the
        position of the given mouse event, or None if no atom is drawn there.
        This takes into account all known effects that affect drawing, except
        bonds and other non-atom things, which are treated as invisible.
        (Someday we'll fix this by switching to OpenGL-based hit-detection. #e)

        @note: if several atoms are drawn there, the correct one to return is
        the one that obscures the others at that exact point, which is not always
        the one whose center is closest to the screen!
           When water_cutoff is true, also return None if the atom you would
        otherwise return (more precisely, if the place its surface is touched by
        the mouse) is under the "water surface".
           Normally never return a singlet (though it does prevent returning
        whatever is behind it). Optional arg singlet_ok permits returning one.
        """
        p1, p2 = self.o.mousepoints(event, 0.0)
        z = norm(p1-p2)
        if 1:
            # This computation of matrix is now doable (roughly) by geometry.matrix_putting_axis_at_z().
            # Once that's tested, these could probably be replaced by a call to it.
            # But this is not confirmed -- the question is whether we cared about this use of self.o.up
            # except as a convenient known perpendicular to z. If it matters, we can't use matrix_putting_axis_at_z here.
            # [bruce 060608 comment]
            x = cross(self.o.up,z)
            y = cross(z,x)
            matrix = transpose(V(x,y,z))
        point = p2
        cutoffs = dot( A([p1,p2]) - point, matrix)[:,2]
        near_cutoff = cutoffs[0]
        if water_cutoff:
            far_cutoff = cutoffs[1]
            # note: this can be 0.0, which is false, so an expression like
            # (water_cutoff and cutoffs[1] or None) doesn't work!
        else:
            far_cutoff = None
        z_atom_pairs = []
        for mol in self.molecules:
            if mol.hidden:
                continue
            pairs = mol.findAtomUnderMouse(point, matrix, \
                                           far_cutoff = far_cutoff, near_cutoff = near_cutoff )
            z_atom_pairs.extend( pairs)
        if not z_atom_pairs:
            return None
        z_atom_pairs.sort() # smallest z == farthest first; we want nearest
        res = z_atom_pairs[-1][1] # nearest hit atom
        if res.element == Singlet and not singlet_ok:
            return None
        return res

    #bruce 041214 renamed and rewrote the following pick_event methods, as part of
    # fixing bug 235 (and perhaps some unreported bugs).
    # I renamed them to distinguish them from the many other "pick" (etc) methods
    # for Node subclasses, with common semantics different than these have.
    # I removed some no-longer-used related methods.

    # All these methods should be rewritten to be more general;
    # for more info, see comment about findAtomUnderMouse and jigGLSelect
    # in def end_selection_curve in Select_GraphicsMode.py.
    # [bruce 080917 comment]

    def pick_at_event(self, event): #renamed from pick; modified
        """
        Pick whatever visible atom or chunk (depending on
        self.selwhat) is under the mouse, adding it to the current selection.
        You are not allowed to select a singlet.
        Print a message about what you just selected (if it was an atom).
        """
        # [bruce 041227 moved the getinfo status messages here, from the Atom
        # and Chunk pick methods, since doing them there was too verbose
        # when many items were selected at the same time. Original message
        # code was by [mark 2004-10-14].]
        self.begin_select_cmd() #bruce 051031
        atm = self.findAtomUnderMouse(event, water_cutoff = self._decide_water_cutoff())
        if atm:
            if self.selwhat == SELWHAT_CHUNKS:
                if not self.selmols:
                    self.selmols = []
                    # bruce 041214 added that, since pickpart used to do it and
                    # calls of that now come here; in theory it's never needed.
                atm.molecule.pick()
                env.history.message(atm.molecule.getinfo())
            else:
                assert self.selwhat == SELWHAT_ATOMS
                atm.pick()
                env.history.message(atm.getinfo())

        return

    def delete_at_event(self, event):
        """
        Delete whatever visible atom or chunk (depending on self.selwhat)
        is under the mouse. You are not allowed to delete a singlet.
        This leaves the selection unchanged for any atoms/chunks in the current
        selection not deleted. Print a message about what you just deleted.
        """
        self.begin_select_cmd()
        atm = self.findAtomUnderMouse(event, water_cutoff = self._decide_water_cutoff())
        if atm:
            if self.selwhat == SELWHAT_CHUNKS:
                if not self.selmols:
                    self.selmols = []
                    # bruce 041214 added that, since pickpart used to do it and
                    # calls of that now come here; in theory it's never needed.
                env.history.message("Deleted " + atm.molecule.name)
                atm.molecule.kill()
            else:
                assert self.selwhat == SELWHAT_ATOMS
                if atm.filtered():
                    # note: bruce 060331 thinks refusing to delete filtered atoms, as this does, is a bad UI design,
                    # since if the user clicked on a specific atom they probably knew what they were doing,
                    # and if (at most) we just printed a warning and deleted it anyway, they could always Undo the delete
                    # if they had hit the wrong atom. See also similar code and message in delete_atom_and_baggage (selectMode.py).
                    #bruce 060331 adding orangemsg, since we should warn user we didn't do what they asked.
                    env.history.message(orangemsg("Cannot delete " + str(atm) + " since it is being filtered. "\
                                                  "Hit Escape to clear the selection filter."))
                else:
                    env.history.message("Deleted " + str(atm) )
                    atm.kill()
        return

    def onlypick_at_event(self, event): #renamed from onlypick; modified
        """
        Unselect everything in the glpane; then select whatever visible atom
        or chunk (depending on self.selwhat) is under the mouse at event.
        If no atom or chunk is under the mouse, nothing in glpane is selected.
        """
        self.begin_select_cmd() #bruce 051031
        self.unpickall_in_GLPane() #bruce 060721, replacing the following selwhat-dependent unpickers:
##        if self.selwhat == SELWHAT_CHUNKS:
##            self.unpickparts()
##        else:
##            assert self.selwhat == SELWHAT_ATOMS
##            self.unpickparts() # Fixed bug 606, partial fix for bug 365.  Mark 050713.
##            self.unpickatoms()
        self.pick_at_event(event)

    def unpick_at_event(self, event): #renamed from unpick; modified
        """
        Make whatever visible atom or chunk (depending on self.selwhat)
        is under the mouse at event get un-selected (subject to selection filter),
        but don't change whatever else is selected.
        """ #bruce 060331 revised docstring
        self.begin_select_cmd() #bruce 051031
        atm = self.findAtomUnderMouse(event, water_cutoff = self._decide_water_cutoff())
        if atm:
            if self.selwhat == SELWHAT_CHUNKS:
                atm.molecule.unpick()
            else:
                assert self.selwhat == SELWHAT_ATOMS
                atm.unpick() # this is subject to selection filter -- is that ok?? [bruce 060331 question]
        return

    # == internal selection-related routines

    def unpickatoms(self): #e [should this be private?] [bruce 060721]
        """
        Deselect any selected atoms (but don't change selwhat or do any
        updates).
        """ #bruce 050517 added docstring
        if self.selatoms:
            ## for a in self.selatoms.itervalues():
                #bruce 060405 comment/precaution: that use of self.selatoms.itervalues might have been safe
                # (since actual .unpick (which would modify it) is not called in the loop),
                # but it looks troublesome enough that we ought to make it safer, so I will:
            selatoms = self.selatoms
            self.selatoms = {}
            mols = {}
            for a in selatoms.itervalues():
                # this inlines and optims Atom.unpick
                a.picked = False
                _changed_picked_Atoms[a.key] = a #bruce 060321 for Undo (or future general uses)
                m = a.molecule
                mols[m] = m
            for m in mols: #bruce 090119 optimized, revised call
                m.changed_selected_atoms()
            self.selatoms = {}
        return

    def unpickparts(self): ##e this is misnamed -- should be unpicknodes #e [should this be private?] [bruce 060721]
        """
        Deselect any selected nodes (e.g. chunks, Jigs, Groups) in this part
        (but don't change selwhat or do any updates).
        See also unpickchunks.
        """ #bruce 050517 added docstring; 060721 split out unpickchunks
        self.topnode.unpick()
        return

    def unpickchunks(self): #bruce 060721 made this to replace the misnamed unpick_jigs = False option of unpickparts
        """
        Deselect any selected chunks in this part
        (but don't change selwhat or do any updates).
        See also unpickparts.
        """
        # [bruce 060721 comment: unpick_jigs option to unpickparts was misnamed,
        #  since there are selectable nodes other than jigs and chunks.
        #  BTW Only one call uses this option, which will be obsolete soon
        #  (when atoms & chunks can be coselected).]
        for c in self.molecules:
            if c.picked:
                c.unpick()
        return

    def unpickall_in_GLPane(self): #bruce 060721
        """
        Unselect all things that ought to be unselected by a click in empty
        space in the GLPane.
        As of 060721 this means "everything", but we might decide that MT nodes
        that are never drawn in GLPane should remain selected in a case like
        this. ###@@@
        """
        self.unpickatoms()
        self.unpickparts()
        return

    def unpickall_in_MT(self): #bruce 060721
        """
        Unselect all things that ought to be unselected by a click in empty
        space in the Model Tree. As of 060721 this means "all nodes", but we
        might decide that it should deselect atoms too. ###@@@
        """
        self.unpickparts()
        return

    def unpickall_in_win(self): #bruce 060721
        """
        Unselect all things that a general "unselect all" tool button or menu
        command ought to. This should unselect all selectable things, and
        should be equivalent to doing both L{unpickall_in_GLPane()} and
        L{unpickall_in_MT()}.
        """
        self.unpickatoms()
        self.unpickparts()
        return

    def begin_select_cmd(self):
        # Warning: same named method exists in assembly, GLPane, and ops_select, with different implems.
        # More info in comments in assembly version. [bruce 051031]
        self.assy.begin_select_cmd() # count selection commands, for use in pick-time records
        return

    # ==

    def selection_from_glpane(self): #bruce 050404 experimental feature for initial use in Minimize Selection; renamed 050523
        """
        Return an object which represents the contents of the current selection,
        independently of part attrs... how long valid?? Include the data
        generally used when doing an op on selection from glpane (atoms and
        chunks); see also selection_from_MT().
        """
        # the idea is that this is a snapshot of selection even if it changes
        # but it's not clear how valid it is after the part contents itself starts changing...
        # so don't worry about this yet, consider it part of the experiment...
        part = self
        return selection_from_glpane( part)

    def selection_for_all(self): #bruce 050419 for use in Minimize All; revised 050523
        """
        Return a selection object referring to all our atoms (regardless of
        the current selection, and not changing it).
        """
        part = self
        return selection_for_entire_part( part)

    def selection_from_MT(self): #bruce 050523; not used as of 080414, but might be someday
        """
        [#doc]
        """
        part = self
        return selection_from_MT( part)

    def selection_from_part(self, *args, **kws): #bruce 051005
        part = self
        return selection_from_part(part, *args, **kws)

    pass # end of class ops_select_Mixin (used in class Part)

# ==

def topmost_selected_nodes(nodes):
    """
    @param nodes: a list of nodes, to be examined for selected nodes or subnodes
    @type nodes: python sequence of Nodes

    @return: a list of all selected nodes in or under the given list of nodes,
             not including any node which is inside any selected Group
             in or under the given list

    @see: same-named method in class ModelTreeGui_api and class TreeModel_api
    """
    #bruce 050523 split this out from the same-named TreeWidget method,
    # and optimized it
    res = []
    func = res.append
    for node in nodes:
        node.apply2picked( func)
    return res

# ==

def selection_from_glpane( part): #bruce 050523 split this out as intermediate helper function; revised 050523
    # note: as of 080414 this is used only in sim_commandruns.py and MinimizeEnergyProp.py
    return Selection( part, atoms = part.selatoms, chunks = part.selmols )

def selection_from_MT( part): #bruce 050523; not used as of 080414, but might be someday
    return Selection( part, atoms = {}, nodes = topmost_selected_nodes([part.topnode]) )

def selection_from_part( part, use_selatoms = True, expand_chunkset_func = None): #bruce 050523
    # note: as of 080414 all ultimate uses of this are in ModelTree.py or ops_copy.py
    if use_selatoms:
        atoms = part.selatoms
    else:
        atoms = {}
    res = Selection( part, atoms = atoms, nodes = topmost_selected_nodes([part.topnode]) )
    if expand_chunkset_func:
        res.expand_chunkset(expand_chunkset_func)
    return res

def selection_for_entire_part( part): #bruce 050523 split this out, revised it
    return Selection( part, atoms = {}, chunks = part.molecules )

def selection_from_atomlist( part, atomlist): #bruce 051129, for initial use in Local Minimize
    return Selection( part, atoms = atomdict_from_atomlist(atomlist) )

def atomdict_from_atomlist(atomlist): #bruce 051129 [#e should refile -- if I didn't already implement it somewhere else]
    """
    Given a list of atoms, return a dict mapping atom keys to those atoms.
    """
    return dict( [(a.key, a) for a in atomlist] )

class Selection: #bruce 050404 experimental feature for initial use in Minimize Selection; revised 050523
    """
    Represent a "snapshot-by-reference" of the contents of the current selection,
    or any similar set of objects passed to the constructor.

    @warning: this remains valid (and unchanged in meaning) if the
    selection-state changes, but might become invalid if the Part contents
    themselves change in any way! (Or at least if the objects passed to the
    constructor (like chunks or Groups) change in contents (atoms or child
    nodes).)
    """ #bruce 051129 revised docstring
    def __init__(self, part, atoms = {}, chunks = [], nodes = []):
        """
        Create a snapshot-by-reference of whatever sets or lists of objects
        are passed in the args atoms, chunks, and/or nodes (see details and
        limitations below).

        Objects should not be passed redundantly -- i.e. they should not
        contain atoms or nodes twice, where we define chunks as containing
        their atoms and Group nodes as containing their child nodes.

        Objects must be of the appropriate types (if passed):
        atoms must be a dict mapping atom keys to atoms;
        chunks must be a list of chunks;
        nodes must be a list of nodes, thought of as disjoint node-subtrees
        (e.g. "topmost selected nodes").

        The current implem also prohibits passing both chunks and nodes lists,
        but this limitation is just for its convenience and can be removed
        when needed.

        The object-containing arguments are shallow-copied immediately, but the
        objects they contain are never copied, and in particular, the effect
        of changes to the set of child nodes of Group nodes passed in the nodes
        argument is undefined. (In initial implem, the effect depends on when
        self.selmols is first evaluated.)

        Some methods assume only certain kinds of object arguments were
        passed (see their docstrings for details).
        """
        #bruce 051129 revised docstring -- need to review code to verify its accuracy. ###k
        # note: topnodes might not always be provided;
        # when provided it should be a list of nodes in the part compatible with selmols
        # but containing groups and jigs as well as chunks, and not containing members of groups it contains
        # (those are implicit)
        self.part = part
        ## I don't think self.topnode is used or needed [bruce 050523]
        ## self.topnode = part.topnode # might change...
        self.selatoms = dict(atoms) # copy the dict; it's ok that this does not store atoms inside chunks or nodes
        # For now, we permit passing chunks or nodes list but not both.
        if nodes:
            # nodes were passed -- store them, but let selmols be computed lazily
            assert not chunks, "don't pass both chunks and nodes arguments to Selection"
            self.topnodes = list(nodes)
            # selmols will be computed lazily if needed
            # (to avoid needlessly computing it, we don't assert not (self.selatoms and self.selmols))
        else:
            # chunks (or no chunks and no nodes) were passed -- store as both selmols and topnodes
            self.selmols = list(chunks) # copy the list
            self.topnodes = self.selmols # use the same copy we just made
            if (self.selatoms and self.selmols) and debug_flags.atom_debug: #e could this change? try not to depend on it
                print_compact_traceback( "atom_debug: self.selatoms and self.selmols: " ) #bruce 051129, replacing an assert
        return
    def nonempty(self): #e make this the object's boolean value too?
        # assume that each selmol has some real atoms, not just singlets! Should always be true.
        return self.selatoms or self.topnodes #revised 050523
    def atomslist(self):
        """
        Return a list of all selected real atoms, whether selected as atoms or
        in selected chunks; no singlets or jigs.
        """
        #e memoize this!
        # [bruce 050419 comment: memoizing it might matter for correctness
        #  if mol contents change, not only for speed. But it's not yet needed,
        #  since in the only current use of this, the atomslist is grabbed once
        #  and stored elsewhere.]
        if self.selmols:
            res = dict(self.selatoms) # dict from atom keys to atoms
            for mol in self.selmols:
                # we'll add real atoms and singlets, then remove singlets
                # (probably faster than only adding real atoms, since .update is one bytecode
                #  and (for large mols) most atoms are not singlets)
                res.update(mol.atoms)
                for s in mol.singlets:
                    del res[s.key]
        else:
            res = self.selatoms
        items = res.items()
        items.sort() # sort by atom key; might not be needed
        return [atom for key, atom in items]
    def __getattr__(self, attr): # in class Selection
        if attr == 'selmols':
            # compute from self.topnodes -- can't assume selection state of self.part
            # is same as during our init, or even know whether it was relevant then.
            res = []
            def func(node):
                if isinstance(node, Chunk):
                    res.append(node)
                return # from func
            for node in self.topnodes:
                node.apply2all(func)
            self.selmols = res
            return res
        elif attr == 'selmols_dict': #bruce 050526
            res = {}
            for mol in self.selmols:
                res[id(mol)] = mol
            self.selmols_dict = res
            return res
        raise AttributeError, attr

    def picks_atom(self, atom): #bruce 050526
        """
        Does this selection include atom, either directly or via its chunk?
        """
        return atom.key in self.selatoms or id(atom.molecule) in self.selmols_dict

    def picks_chunk(self, chunk): #bruce 080414
        """
        Does this selection include chunk, either directly or via a containing
        Group in topnodes?
        """
        return id(chunk) in self.selmols_dict

    def add_chunk(self, chunk): #bruce 080414
        """
        If not self.picks_chunk(chunk), add chunk to this selection
        (no effect on external selection state i.e. chunk.picked).
        Otherwise do nothing.
        """
        if not self.picks_chunk(chunk):
            self.selmols_dict[id(chunk)] = chunk
            self.selmols.append(chunk)
            # sometimes self.selmols is the same mutable list as self.topnodes.
            # if so, preserve this, otherwise also add to self.topnodes
            if self.topnodes and self.topnodes[-1] is chunk:
                pass
            else:
                self.topnodes.append(chunk)
            # (note: modifying those attrs is only permissible because
            #  __init__ shallow-copies those lists)
            pass
        return

    def describe_objects_for_history(self):
        """
        Return a string like "5 items" but more explicit if possible, for use
        in history messages.
        """
        if self.topnodes:
            res = fix_plurals( "%d item(s)" % len(self.topnodes) )
            #e could figure out their common class if any (esp. useful for Jig and below); for Groups say what they contain; etc
        elif self.selmols:
            res = fix_plurals( "%d chunk(s)" % len(self.selmols) )
        else:
            res = ""
        if self.selatoms:
            if res:
                res += " and "
            res += fix_plurals( "%d atom(s)" % len(self.selatoms) )
            #e could say "other atoms" if the selected nodes contain any atoms
        return res

    def expand_atomset(self, ntimes = 1): #bruce 051129 for use in Local Minimize; compare to selectExpand
        """
        Expand self's set of atoms (to include all their real-atom neighbors)
        (repeating this ntimes), much like "Expand Selection" but using no
        element filter, and of course having no influence by or effect on
        "current selection state" (atom.picked attribute).

        Ignore issue of self having selected chunks (as opposed to the atoms
        in them); if this ever becomes possible we can decide how to generalize
        this method for that case (ignore them, turn them to atoms, etc).

        @warning: Current implem [051129] is not optimized for lots of atoms
        and ntimes > 1 (which doesn't matter for its initial use).
        """
        assert not self.selmols and not self.topnodes # (since current implem would be incorrect otherwise)
        atoms = self.selatoms # mutable dict, modified in following loop
            # [name 'selatoms' is historical, but also warns that it doesn't include atoms in selmols --
            #  present implem is only correct on selection objects made only from atoms.]
        for i in range(ntimes):
            for a1 in atoms.values(): # this list remains fixed as atoms dict is modified by this loop
                for a2 in a1.realNeighbors():
                    atoms[a2.key] = a2 # analogous to a2.pick()
        return

    def expand_chunkset(self, func): #bruce 080414
        """
        func can be called on one chunk to return a list of chunks.
        Expand the set of chunks in self (once, not recursively)
        by including all chunks in func(orig) for orig being any chunk
        originally in self (when this is called). Independently protect
        from exceptions in each call of func, and also from the bug
        of func returning None.
        """
        for chunk in list(self.selmols):
            try:
                more_chunks = func(chunk)
                assert more_chunks is not None
            except:
                print_compact_traceback("ignoring exception in, or returning of None by, %r(%r): " % (func, chunk))
                more_chunks = ()
            if more_chunks:
                for chunk2 in more_chunks:
                    self.add_chunk(chunk2)
            continue
        return

    pass # end of class Selection

# end
