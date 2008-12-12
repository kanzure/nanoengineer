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
from protein.commands.ProteinDisplayStyle.ProteinDisplayStyle_PropertyManager import ProteinDisplayStyle_PropertyManager

# == GraphicsMode part

_superclass_for_GM = SelectChunks_GraphicsMode

class ProteinDisplayStyle_GraphicsMode(SelectChunks_GraphicsMode ):
    """
    Graphics mode for (Protein) Display Style command. 
    """
    pass
    
# == Command part

_superclass = EditCommand
class ProteinDisplayStyle_Command(EditCommand): 
#class ProteinDisplayStyle_Command(ModelAndSimulateProtein_Command): 
    """
    
    """
   
    # class constants
    
    GraphicsMode_class = ProteinDisplayStyle_GraphicsMode
    
    PM_class = ProteinDisplayStyle_PropertyManager
    
    
    commandName = 'EDIT_PROTEIN_DISPLAY_STYLE'
    featurename = "Protein Display Style"
    from utilities.constants import CL_GLOBAL_PROPERTIES
    command_level = CL_GLOBAL_PROPERTIES
    
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True
    
    flyoutToolbar = None
    
    def _getFlyoutToolBarActionAndParentCommand(self):
        """
        See superclass for documentation.
        @see: self.command_update_flyout()
        """
        flyoutActionToCheck = 'displayProteinStyleAction'
        parentCommandName = 'MODEL_AND_SIMULATE_PROTEIN'  
        return flyoutActionToCheck, parentCommandName
    
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
