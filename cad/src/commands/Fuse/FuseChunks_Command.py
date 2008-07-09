# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
FuseChunks_Command.py

@author: Mark
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:
Originally by Mark as class 'fuseChunksMode'.
Ninad 2008-01-25: Split Command and GraphicsMode classes
                 out of class fuseChunksMode. The graphicsMode class can be
                 found in FuseChunks_GraphicsMode.py
"""


from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QWidgetAction
from PyQt4.Qt import QAction

import foundation.env as env
import foundation.changes as changes
from geometry.VQT import vlen

from model.elements import Singlet
from utilities.Log import redmsg, orangemsg
from platform_dependent.PlatformDependent import fix_plurals
from commands.Fuse.FusePropertyManager import FusePropertyManager
from utilities.icon_utilities import geticon
from utilities.constants import diINVISIBLE

from commands.Move.Move_Command import Move_Command
from commands.Fuse.fusechunksMode import fusechunksBase

from commands.Fuse.fusechunksMode import fusechunks_lambda_tol_natoms, fusechunks_lambda_tol_nbonds

MAKEBONDS = 'Make Bonds Between Chunks'
FUSEATOMS = 'Fuse Overlapping Atoms'

from commands.Fuse.FuseChunks_GraphicsMode import FuseChunks_GraphicsMode
from commands.Fuse.FuseChunks_GraphicsMode import Translate_in_FuseChunks_GraphicsMode
from commands.Fuse.FuseChunks_GraphicsMode import Rotate_in_FuseChunks_GraphicsMode
from command_support.GraphicsMode_API import GraphicsMode_API

class FuseChunks_Command(Move_Command, fusechunksBase):
    """
    Allows user to move chunks and fuse them to other chunks in the part.
    Two fuse methods are supported:
    1. Make Bonds - bondpoints between chunks will form bonds when they are
       near each other.
    2. Fuse Atoms - atoms between chunks will be fused when they overlap each
       other.
    """
    # class constants
    commandName = 'FUSECHUNKS'
    default_mode_status_text = "Mode: Fuse Chunks"
    featurename = "Fuse Chunks Mode"
    bondable_pairs = [] # List of bondable singlets
    ways_of_bonding = {} # Number of bonds each singlet found
    bondable_pairs_atoms = [] # List of atom pairs that can be bonded
    overlapping_atoms = [] # List of overlapping atoms

    tol = 1.0 # in Angstroms
        # For "Make Bonds", tol is the distance between two bondable singlets
        # For "Fuse Atoms", tol is the distance between two atoms to be
        # considered overlapping

    fuse_mode = '' # The Fuse mode, either 'Make Bonds' or 'Fuse Atoms'.
    propMgr = None

    GraphicsMode_class = FuseChunks_GraphicsMode

    def _create_GraphicsMode(self):
        GM_class = self.GraphicsMode_class
        assert issubclass(GM_class, GraphicsMode_API)
        args = [self]
        kws = {}
        self.graphicsMode = GM_class(*args, **kws)

        self.translate_graphicsMode = Translate_in_FuseChunks_GraphicsMode(*args, **kws)
        self.rotate_graphicsMode  = Rotate_in_FuseChunks_GraphicsMode(*args, **kws)


    def init_gui(self):
        if self.propMgr is None:
            self.propMgr = FusePropertyManager(self)
            #@bug BUG: following is a workaround for bug 2494
            changes.keep_forever(self.propMgr)

        self.propMgr.show()

        self.change_fuse_mode(self.propMgr.fuseComboBox.currentText())
            # This maintains state of fuse mode when leaving/reentering mode,
            # and syncs the PM and glpane (and does a gl_update).


        self.w.toolsFuseChunksAction.setChecked(1)

        self.updateCommandToolbar(bool_entering = True)

        # connect signals
        #(these all need to be disconnected in restore_gui) [mark 050901]
        self.connect_or_disconnect_signals(True)

        if self.o.assy.selmols:
            self.graphicsMode.something_was_picked = True

        #if self.propMgr.isTranslateGroupBoxActive:
            ## toggle on the Move Free action in the Property Manager
            #self.propMgr.transFreeButton.setChecked(True)
            #self.graphicsMode.moveOption = 'MOVEDEFAULT'
        #else:
            #self.propMgr.rotateFreeButton.setChecked(True)
            #self.graphicsrotateOption = 'ROTATEDEFAULT'

    def restore_gui(self):
        self.updateCommandToolbar(bool_entering = False)
        self.connect_or_disconnect_signals(False)
        self.w.toolsFuseChunksAction.setChecked(False)
        self.propMgr.close()

    def connect_or_disconnect_signals(self, connect):
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect

        change_connect(self.exitFuseAction, SIGNAL("triggered()"),
                       self.w.toolsDone)

        #Connect or disconnect signals in property manager
        self.propMgr.connect_or_disconnect_signals(connect)

        return

    def Backup(self):
        """
        Undo any bonds made between chunks.
        """
        # This undoes only the last fused chunks.  Will work on supporting
        # multiple undos when we get a single undo working.   Mark 050326

        # Bust bonds between last pair/set of fused chunks.
        if self.bondable_pairs_atoms:
            for a1, a2 in self.bondable_pairs_atoms:
                b = a1.get_neighbor_bond(a2)
                if b: b.bust()


            if self.merged_chunks:
                nchunks_str = "%d" % (len(self.merged_chunks) + 1,)
                msg = "Fuse Chunks: Bonds broken between %s chunks." % (nchunks_str)
                env.history.message(msg)
                msg = "Warning: Cannot separate the original chunks. You can " \
                "do this yourself using <b>Modify > Separate</b>."
                env.history.message(orangemsg(msg))

                cnames = "Their names were: "
                # Here are the original names...
                for chunk in self.merged_chunks:
                    cnames += '[' + chunk.name + '] '
                env.history.message(cnames)

            self.o.gl_update()

        else:
            msg = "Fuse Chunks: No bonds have been made yet.  Undo ignored."
            env.history.message(redmsg(msg))



    def tolerance_changed(self, val):
        """
        Slot for tolerance slider.
        """
        self.tol = val * .01

        if self.o.assy.selmols:
            self.o.gl_update()
        else:
            # Since no chunks are selected, there are no bonds, but the slider
            # tolerance label still needs
            # updating.  This fixed bug 502-14.  Mark 050407
            self.reset_tolerance_label()

    def reset_tolerance_label(self):
        """
        Reset the tolerance label to 0 bonds or 0 overlapping atoms
        """
        if self.fuse_mode == MAKEBONDS:
            tol_str = fusechunks_lambda_tol_nbonds(self.tol, 0, 0, 0) # 0 bonds
        else:
            # 0 overlapping atoms
            tol_str = fusechunks_lambda_tol_natoms(self.tol, 0)

        tolerenceLabel = tol_str
        self.propMgr.toleranceSlider.labelWidget.setText(tolerenceLabel)

    def change_fuse_mode(self, fuse_mode):
        """
        Sets the Fuse mode
        """
        if self.fuse_mode == fuse_mode:
            return # The mode did not change.  Don't do anything.
        self.fuse_mode = str(fuse_mode) # Must cast here.

        if self.fuse_mode == str(MAKEBONDS):
            self.propMgr.fusePushButton.setText('Make Bonds')
        else:
            self.propMgr.fusePushButton.setText('Fuse Atoms')

        self.o.gl_update() # the Draw() method will update based on the current
                           #combo box item.

    def find_fusables(self):
        """
        Finds bondable pairs or overlapping atoms, based on the
        Fuse Action combo box
        """
        if self.fuse_mode == MAKEBONDS:
            self.find_bondable_pairs()
        else:
            self.find_overlapping_atoms()

    def find_bondable_pairs(self, chunk_list = None):
        """
        Checks the bondpoints of the selected chunk to see if they are close
        enough to bond with any other bondpoints in a list of chunks.
        Hidden chunks are skipped.
        """
        tol_str = fusechunksBase.find_bondable_pairs(self, chunk_list, None)
        tolerenceLabel = tol_str
        self.propMgr.toleranceSlider.labelWidget.setText(tolerenceLabel)

    def fuse_something(self):
        """
        Slot for 'Make Bonds/Fuse Atoms' button.
        """
        if self.fuse_mode == MAKEBONDS:
            self.make_bonds()
        else:
            self.fuse_atoms()

    def make_bonds(self):
        """
        Make bonds between all bondable pairs of singlets
        """
        self._make_bonds_1()
        self._make_bonds_2()
        self._make_bonds_3()
        self._make_bonds_4()

    def _make_bonds_2(self):
        # Merge the chunks if the "merge chunks" checkbox is checked
        if self.propMgr.mergeChunksCheckBox.isChecked() and self.bondable_pairs_atoms:
            for a1, a2 in self.bondable_pairs_atoms:
                # Ignore a1, they are atoms from the selected chunk(s)
                # It is possible that a2 is an atom from a selected chunk,
                # so check it
                if a2.molecule != a1.molecule:
                    if a2.molecule not in self.merged_chunks:
                        self.merged_chunks.append(a2.molecule)
                        a1.molecule.merge(a2.molecule)

    def _make_bonds_4(self):
        msg = fix_plurals( "%d bond(s) made" % self.total_bonds_made)
        env.history.message(msg)

        # Update the slider tolerance label.  This fixed bug 502-14. Mark 050407
        self.reset_tolerance_label()

        if self.bondable_pairs_atoms:
            # This must be done before gl_update, or it will try to draw the
            # bondable singlets again, which generates errors.
            self.bondable_pairs = []
            self.ways_of_bonding = {}

        self.w.win_update()

        ######### Overlapping Atoms methods #############

    def find_overlapping_atoms(self):
        """
        Checks atoms of the selected chunk to see if they overlap atoms
        in other chunks of the same type (element).  Hidden chunks are skipped.
        """
        # Future versions should allow more flexible rules for overlapping
        # atoms, but this needs to be discussed with others before implementing
        # anything.
        # For now, only atoms of the same type qualify as overlapping atoms.
        # As is, it is extremely useful for fusing chunks of diamond,
        # lonsdaleite or SiC,
        # which is done quite a lot with casings.  This will save me hours of
        # modeling work.
        # Mark 050902

        self.overlapping_atoms = []

        for chunk in self.o.assy.selmols:

            if chunk.hidden or chunk.display == diINVISIBLE:
                # Skip selected chunk if hidden or invisible.
                # Fixes bug 970. mark 060404
                continue

            # Loop through all the mols in the part to search for bondable
            # pairs of singlets.
            for mol in self.o.assy.molecules:
                if chunk is mol:
                    continue # Skip itself
                if mol.hidden or mol.display == diINVISIBLE:
                    continue # Skip hidden or invisible chunks
                if mol in self.o.assy.selmols:
                    continue # Skip other selected chunks

                # Skip this mol if its bounding box does not overlap the
                # selected chunk's bbox.
                # Remember: chunk = a selected chunk, mol = a non-selected
                # chunk.
                if not chunk.overlapping_chunk(mol, self.tol):
                    # print "Skipping ", mol.name
                    continue
                else:

                    # Loop through all the atoms in the selected chunk.
                    # Use values() if the loop ever modifies chunk or mol--
                    for a1 in chunk.atoms.itervalues():
                        # Singlets can't be overlapping atoms --
                        if a1.element is Singlet:
                            continue
                        # We can skip mol if the atom lies outside its bbox.
                        if not mol.overlapping_atom(a1, self.tol):
                            continue

                        # Loop through all the atoms in this chunk.
                        for a2 in mol.atoms.itervalues():
                            # Only atoms of the same type can be overlapping.
                            # This also screens singlets, since a1 can't be a
                            # singlet.
                            if a1.element is not a2.element:
                                continue

                            # Compares the distance between a1 and a2.
                            # If the distance
                            # is <= tol, then we have an overlapping atom.
                            # I know this isn't a proper use of tol,
                            # but it works for now.   Mark 050901
                            if vlen (a1.posn() - a2.posn()) <= self.tol:
                                # Add this pair to the list--
                                self.overlapping_atoms.append( (a1,a2) )
                                # No need to check other atoms in this chunk--
                                break

        # Update tolerance label and status bar msgs.
        natoms = len(self.overlapping_atoms)
        tol_str = fusechunks_lambda_tol_natoms(self.tol, natoms)
        tolerenceLabel = tol_str
        self.propMgr.toleranceSlider.labelWidget.setText(tolerenceLabel)


    def fuse_atoms(self):
        """
        Deletes overlapping atoms found with the selected chunk(s).
        Only the overlapping atoms from the unselected chunk(s) are deleted.
        If the "Merge Chunks" checkbox
        is checked, then find_bondable_pairs() and make_bonds() is called,
        resulting in the merging of chunks.
        """
        total_atoms_fused = 0 # The total number of atoms fused.

        # fused_chunks stores the list of chunks that contain overlapping atoms
        # (but no selected chunks, though)
        fused_chunks = []

        # Delete overlapping atoms.
        for a1, a2 in self.overlapping_atoms:
            if a2.molecule not in fused_chunks:
                fused_chunks.append(a2.molecule)
            a2.kill()

#        print "Fused chunks list:", fused_chunks

        # Merge the chunks if the "merge chunks" checkbox is checked
        if self.propMgr.mergeChunksCheckBox.isChecked() and self.overlapping_atoms:
            # This will bond and merge the selected chunks only with
            # chunks that had overlapping atoms.
            #& This has bugs when the bonds don't line up nicely between
            # overlapping atoms in the selected chunk
            #& and the bondpoints of the deleted atoms' neighbors.
            # Needs a bug report. mark 060406.
            self.find_bondable_pairs(fused_chunks)
            self.make_bonds()

        # Print history msgs to inform the user what happened.
        total_atoms_fused = len(self.overlapping_atoms)
        msg = fix_plurals( "%d atom(s) fused with %d chunk(s)" % (total_atoms_fused, len(fused_chunks)))
        env.history.message(msg)
        #"%s => %s overlapping atoms" % (tol_str, natoms_str)

        # Update the slider tolerance label.
        self.reset_tolerance_label()

        self.overlapping_atoms = []
            # This must be done before win_update(), or it will try to draw the
            # overlapping atoms again, which generates errors.

        self.w.win_update()


    #Command Toolbar to be revised ============================================

    def getFlyoutActionList(self): #Ninad 20070618
        """
        Returns a tuple that contains mode spcific actionlists in the
        added in the flyout toolbar of the mode.
        CommandToolbar._createFlyoutToolBar method calls this
        @return: params: A tuple that contains 3 lists:
        (subControlAreaActionList, commandActionLists, allActionsList)
        """

        #'allActionsList' returns all actions in the flyout toolbar
        #including the subcontrolArea actions
        allActionsList = []

        #Action List for  subcontrol Area buttons.
        #In this mode, there is really no subcontrol area.
        #We will treat subcontrol area same as 'command area'
        #(subcontrol area buttons will have an empty list as their command area
        #list). We will set  the Comamnd Area palette background color to the
        #subcontrol area.

        subControlAreaActionList =[]

        self.exitFuseAction = QWidgetAction(self.w)
        self.exitFuseAction.setText("Exit Fuse")
        self.exitFuseAction.setCheckable(True)
        self.exitFuseAction.setChecked(True)
        self.exitFuseAction.setIcon(
            geticon("ui/actions/Toolbars/Smart/Exit.png"))
        subControlAreaActionList.append(self.exitFuseAction)

        separator = QAction(self.w)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator)

        allActionsList.extend(subControlAreaActionList)

        #Empty actionlist for the 'Command Area'
        commandActionLists = []

        #Append empty 'lists' in 'commandActionLists equal to the
        #number of actions in subControlArea
        for i in range(len(subControlAreaActionList)):
            lst = []
            commandActionLists.append(lst)

        params = (subControlAreaActionList, commandActionLists, allActionsList)

        return params

    def updateCommandToolbar(self, bool_entering = True):#Ninad 20070618
        """
        Update the command toolbar
        """
        # object that needs its own flyout toolbar. In this case it is just
        #the mode itself.

        action = self.w.toolsFuseChunksAction
        obj = self
        self.w.commandToolbar.updateCommandToolbar(action,
                                                   obj,
                                                   entering =bool_entering)
