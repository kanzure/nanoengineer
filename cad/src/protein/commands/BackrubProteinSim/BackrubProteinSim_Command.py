# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Urmi
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

import foundation.changes as changes
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from command_support.EditCommand import EditCommand
from utilities.constants import red
from protein.commands.BackrubProteinSim.BackrubProteinSim_PropertyManager import BackrubProteinSim_PropertyManager

# == GraphicsMode part

_superclass_for_GM = SelectChunks_GraphicsMode

class BackrubProteinSim_GraphicsMode(SelectChunks_GraphicsMode ):
    """
    Graphics mode for Backrub Proteins sequence design command. 
    """
    pass
    
# == Command part


class BackrubProteinSim_Command(EditCommand): 
    """
    
    """
    # class constants
    
    commandName = 'BACKRUB_PROTEIN_SEQUENCE_DESIGN'
    featurename = "Backrub Protein Sequence Design"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'SIMULATE_PROTEIN'
      
    GraphicsMode_class = BackrubProteinSim_GraphicsMode
   
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True
    
    flyoutToolbar = None

    def init_gui(self):
        """
        Initialize GUI for this mode 
        """

        self._init_gui_flyout_action( 'rosetta_backrub_Action', 'MODEL_AND_SIMULATE_PROTEIN' )
        
        if self.propMgr is None:
            self.propMgr = BackrubProteinSim_PropertyManager(self)
            #@bug BUG: following is a workaround for bug 2494.
            #This bug is mitigated as propMgr object no longer gets recreated
            #for modes -- niand 2007-08-29
            changes.keep_forever(self.propMgr)  
            
        self.propMgr.show()
        
    def restore_gui(self):
        """
        Restore the GUI 
        """
        EditCommand.restore_gui(self)
        if self.flyoutToolbar:
            self.flyoutToolbar.rosetta_backrub_Action.setChecked(False)    
        
    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted. 
        otherwise returns False. The default implementation always returns 
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True. 
        (and as of 2008-03-06, it is proposed that dna_updater calls this method
        when needed. 
        @see: Command.keep_empty_group() which is overridden here. 
        """
        
        bool_keep = EditCommand.keep_empty_group(self, group)
        
        return bool_keep
