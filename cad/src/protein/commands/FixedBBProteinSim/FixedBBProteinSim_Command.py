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
from protein.commands.FixedBBProteinSim.FixedBBProteinSim_PropertyManager import FixedBBProteinSim_PropertyManager
from utilities.GlobalPreferences import MODEL_AND_SIMULATE_PROTEINS
# == GraphicsMode part

_superclass_for_GM = SelectChunks_GraphicsMode

class FixedBBProteinSim_GraphicsMode(SelectChunks_GraphicsMode ):
    """
    Graphics mode for Fixed Backbone Protein Sequence Design command. 
    """
    pass
    
# == Command part


class FixedBBProteinSim_Command(EditCommand): 
    """
    Class for fixed backbone rosetta sequence design
    """    
    # class constants
    
    GraphicsMode_class = FixedBBProteinSim_GraphicsMode
    
    PM_class = FixedBBProteinSim_PropertyManager
    
    commandName = 'FIXED_BACKBONE_PROTEIN_SEQUENCE_DESIGN'
    featurename = "Fixed Backbone Sequence Design"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'SIMULATE_PROTEIN'
      
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True
    
    flyoutToolbar = None
    
    def _getFlyoutToolBarActionAndParentCommand(self):
        """
        See superclass for documentation.
        @see: self.command_update_flyout()
        """
        flyoutActionToCheck = 'rosetta_fixedbb_design_Action'
        if MODEL_AND_SIMULATE_PROTEINS:
            parentCommandName = 'MODEL_AND_SIMULATE_PROTEIN'    
        else:
            parentCommandName = None
            
        return flyoutActionToCheck, parentCommandName
    
    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted. 
        otherwise returns False. The default implementation always returns 
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True. 
        @see: Command.keep_empty_group() which is overridden here. 
        """
        
        bool_keep = EditCommand.keep_empty_group(self, group)
        
        return bool_keep
