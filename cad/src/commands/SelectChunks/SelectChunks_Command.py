# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
SelectChunks_Command.py

The 'Command' part of the Select Chunks Mode (SelectChunks_Command and
SelectChunks_basicGraphicsMode are the two split classes of the old
selectMolsMode)  It provides the command object for its GraphicsMode class.
The Command class defines anything related to the 'command half' of the mode --
For example:
- Anything related to its current Property Manager, its settings or state
- The model operations the command does (unless those are so simple
  that the mouse event bindings in the _GM half can do them directly
  and the code is still clean, *and* no command-half subclass needs
  to override them).

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.


TODO:
- Items mentioned in Select_GraphicsMode.py
- Other items listed in Select_Command.py

History:
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from
                          the old class selectMolsMode and moved the
                          Command related methods into this class from
                          selectMolsMode.py

"""
from commands.Select.Select_Command import Select_Command
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from utilities.Comparison import same_vals

from model.chem import Atom
from model.chunk import Chunk
from model.bonds import Bond

_superclass = Select_Command
class SelectChunks_Command(Select_Command):
    """
    The 'Command' part of the Select Chunks Mode (SelectChunks_Command and
    SelectChunks_basicGraphicsMode are the two split classes of the old
    selectMolsMode)  It provides the command object for its GraphicsMode class.
    The Command class defines anything related to the 'command half' of the
    mode --
    For example:
    - Anything related to its current Property Manager, its settings or state
    - The model operations the command does (unless those are so simple
      that the mouse event bindings in the _GM half can do them directly
      and the code is still clean, *and* no command-half subclass needs
      to override them).
    """

    #GraphicsMode
    GraphicsMode_class = SelectChunks_GraphicsMode

    commandName = 'SELECTMOLS'
        # i.e. DEFAULT_COMMAND, but don't use that constant to define it here
    featurename = "Select Chunks Mode"
    from utilities.constants import CL_DEFAULT_MODE
    command_level = CL_DEFAULT_MODE # error if command subclass fails to override this

    #This attr is used for comparison purpose in self.command_update_UI()
    #Note the extra '_' at the beginning of this attr name.This is because
    #two classes use _previous_command_stack_change_indicator attr. If one of the
    #class is superclass of the other, then it could create a potential bug
    #(because we call _superclass.command_update_UI' in def command_update_UI)
    #But this is only a fix to a potential bug. As of 2008-11-24, SelectChunks_Command
    #is not a superclass of EditCommand.
    __previous_command_stack_change_indicator = None

    def command_enter_misc_actions(self):
        self.w.toolsSelectMoleculesAction.setChecked(True)

    def command_exit_misc_actions(self):
        self.w.toolsSelectMoleculesAction.setChecked(False)


    def command_update_UI(self):
        """
        Extends superclass method.
        """
        _superclass.command_update_UI(self)
        #Ths following code fixes a bug reported by Mark on 2008-11-10
        #the bug is:
            #1. Insert DNA
            #2. Enter Break Strands command. Exit command.
            #3. Do a region selection to select the middle of the DNA duplex.
            #Notice that atoms are selected, not the strands/segment chunks.
        #The problem is the selection state is not changed back to the Select Chunks
        #the code that does this is in Enter_GraphicsMode.
        #(See SelectChunks_GraphicsMode) but when a command is 'resumed', that
        #method is not called. The fix for this is to check if the command stack
        #indicator changed in the command_update_state method, if it is changed
        #and if currentCommand is BuildDna_EditCommand, call the code that
        #ensures that chunks will be selected when you draw a selection lasso.
        #-- Ninad 2008-11-10
        indicator = self.assy.command_stack_change_indicator()
        if same_vals(self.__previous_command_stack_change_indicator,
                     indicator):
            return

        self.__previous_command_stack_change_indicator = indicator
        self.assy.selectChunksWithSelAtoms_noupdate()
        return

    call_makeMenus_for_each_event = True

    def makeMenus(self): # mark 060303.
        """
        Make the GLPane context menu for Select Chunks.
        """

        self.Menu_spec = []

        selobj = self.glpane.selobj
        highlightedChunk = None
        if isinstance(selobj, Chunk):
            highlightedChunk = selobj
        if isinstance(selobj, Atom):
            highlightedChunk = selobj.molecule
        elif isinstance(selobj, Bond):
            chunk1 = selobj.atom1.molecule
            chunk2 = selobj.atom2.molecule
            if chunk1 is chunk2 and chunk1 is not None:
                highlightedChunk = chunk1

        self.debug_Menu_spec = [
            ('debug: invalidate selection', self.invalidate_selection),
            ('debug: update selection', self.update_selection),
        ]

        if highlightedChunk is not None:
            highlightedChunk.make_glpane_cmenu_items(self.Menu_spec, self)
            return

        _numberOfSelectedChunks = self.o.assy.getNumberOfSelectedChunks()


        if _numberOfSelectedChunks == 0:
            self.addStandardMenuItems()

        elif _numberOfSelectedChunks == 1:
            selectedChunk = self.o.assy.selmols[0]
            selectedChunk.make_glpane_cmenu_items(self.Menu_spec, self)
        elif _numberOfSelectedChunks > 1:
            self._makeEditContextMenus()
            self.Menu_spec.extend([None]) # inserts separator
            contextMenuList = [
                ('Hide', self.o.assy.Hide),
                ('Reset atoms display of selected chunks',
                 self.w.dispResetAtomsDisplay),
                ('Show invisible atoms of selected chunks',
                 self.w.dispShowInvisAtoms),
                ]
            self.Menu_spec.extend(contextMenuList)

        else:
            self.addStandardMenuItems()
        return

    def addStandardMenuItems(self):
        """
        Insert the 'standard' menu items for the GLPane context menu.
        """
        self.Menu_spec.extend(
            [('Edit Color Scheme...', self.w.colorSchemeCommand)])

        # Enable/Disable Jig Selection.
        # This is duplicated in depositMode.makeMenus().
        if self.o.jigSelectionEnabled:
            self.Menu_spec.extend(
                [None,
                 ('Enable jig selection',
                  self.graphicsMode.toggleJigSelection,
                  'checked')])
        else:
            self.Menu_spec.extend(
                [None,
                 ('Enable jig selection',
                  self.graphicsMode.toggleJigSelection,
                  'unchecked')])
        return

    def invalidate_selection(self): #bruce 041115 (debugging method)
        """
        [debugging method] invalidate all aspects of selected atoms or mols
        """
        for mol in self.o.assy.selmols:
            print "already valid in mol %r: %r" % (mol, mol.invalid_attrs())
            mol.invalidate_everything()
        for atm in self.o.assy.selatoms.values():
            atm.invalidate_everything()
        return

    def update_selection(self): #bruce 041115 (debugging method)
        """
        [debugging method] update all aspects of selected atoms or mols;
        no effect expected unless you invalidate them first
        """
        for atm in self.o.assy.selatoms.values():
            atm.update_everything()
        for mol in self.o.assy.selmols:
            mol.update_everything()
        return

