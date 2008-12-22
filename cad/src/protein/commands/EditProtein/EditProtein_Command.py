# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Piotr
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

import foundation.changes as changes
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from command_support.EditCommand import EditCommand
from utilities.constants import red
from protein.commands.EditProtein.EditProtein_PropertyManager import EditProtein_PropertyManager
# == GraphicsMode part

_superclass_for_GM = SelectChunks_GraphicsMode

class EditProtein_GraphicsMode(SelectChunks_GraphicsMode ):
    """
    Graphics mode for Edit Protein command. 
    """
    pass
    
# == Command part


class EditProtein_Command(EditCommand): 
    """
    
    """
    # class constants
    GraphicsMode_class = EditProtein_GraphicsMode
    
    PM_class = EditProtein_PropertyManager
           
    commandName = 'EDIT_PROTEIN'
    featurename = "Edit Protein"
    from utilities.constants import CL_SUBCOMMAND
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_PROTEIN'
            
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True
    
    flyoutToolbar = None
    
    def _getFlyoutToolBarActionAndParentCommand(self):
        """
        See superclass for documentation.
        @see: self.command_update_flyout()
        """
        flyoutActionToCheck = 'editProteinAction'
        parentCommandName = 'BUILD_PROTEIN'    
        
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
