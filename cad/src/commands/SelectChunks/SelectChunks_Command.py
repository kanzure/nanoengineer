# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
SelectChunks_Command.py 

The 'Command' part of the Select Chunks Mode (SelectChunks_basicCommand and 
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
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.


TODO:
- Items mentioned in Select_GraphicsMode.py 
- Other items listed in Select_Command.py

History:
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from 
                          the old class selectMolsMode and moved the 
                          Command related methods into this class from 
                          selectMolsMode.py

"""
from commands.Select.Select_Command import Select_basicCommand
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from command_support.GraphicsMode_API import GraphicsMode_API

from model.chem import Atom
from model.chunk import Chunk
from model.bonds import Bond

class SelectChunks_basicCommand(Select_basicCommand):
    """
    The 'Command' part of the Select Chunks Mode (SelectChunks_basicCommand and 
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
    commandName = 'SELECTMOLS'
        # i.e. DEFAULT_COMMAND, but don't use that constant to define it here
    featurename = "Select Chunks Mode"
    from utilities.constants import CL_DEFAULT_MODE
    command_level = CL_DEFAULT_MODE # error if command subclass fails to override this

    
    def init_gui(self):
        """
        """
        self.w.toolsSelectMoleculesAction.setChecked(True)
        #Fixes bugs like 2682 where command toolbar (the flyout toolbar 
        #portion) doesn't get updated even when in the default mode. 
        self.win.commandToolbar.resetToDefaultState()
                
 
    def restore_gui(self):
        """
        """
        self.w.toolsSelectMoleculesAction.setChecked(False)
        
    #START: New Command API methods. ==========================================
        
    def command_enter_flyout(self):
        #Fixes bugs like 2682 where command toolbar (the flyout toolbar 
        #portion) doesn't get updated even when in the default mode. 
        self.win.commandToolbar.resetToDefaultState()
        
    def command_enter_misc_actions(self):
        self.w.toolsSelectMoleculesAction.setChecked(True)
    
    def command_exit_misc_actions(self):
        self.w.toolsSelectMoleculesAction.setChecked(False)
        
    #END: New Command API methods. ==========================================
           
    
    call_makeMenus_for_each_event = True
    #bruce 050914 enable dynamic context menus
    # [fixes an unreported bug analogous to 971]
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
            highlightedChunk.make_glpane_context_menu_items(self.Menu_spec,
                                                     command = self)
            return

        _numberOfSelectedChunks = self.o.assy.getNumberOfSelectedChunks()
                    
                
        if _numberOfSelectedChunks == 0:
            self.addStandardMenuItems()
        
        elif _numberOfSelectedChunks == 1:
            selectedChunk = self.o.assy.selmols[0]
            selectedChunk.make_glpane_context_menu_items(self.Menu_spec,
                                                 command = self)            
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

class SelectChunks_Command(SelectChunks_basicCommand):
    """
    @see: B{SelectChunks_basicCommand}
    @see: cad/doc/splitting_a_mode.py
    """
    GraphicsMode_class = SelectChunks_GraphicsMode
    
    def __init__(self, commandSequencer):
        SelectChunks_basicCommand.__init__(self, commandSequencer)
        self._create_GraphicsMode()
        return
        
    def _create_GraphicsMode(self):
        GM_class = self.GraphicsMode_class
        assert issubclass(GM_class, GraphicsMode_API)
        args = [self] 
        kws = {} 
        self.graphicsMode = GM_class(*args, **kws)
