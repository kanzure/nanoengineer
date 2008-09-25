# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Mark
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

import foundation.changes as changes
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from command_support.EditCommand import EditCommand
from utilities.constants import red
from dna.commands.OrderDna.OrderDna_PropertyManager import OrderDna_PropertyManager

from graphics.drawing.drawDnaLabels import draw_dnaBaseNumberLabels

# == GraphicsMode part

_superclass_for_GM = SelectChunks_GraphicsMode

class OrderDna_GraphicsMode( SelectChunks_GraphicsMode ):
    """
    Graphics mode for "Order DNA" command. 
    """
    def _drawLabels(self):
        """
        Overrides suoerclass method.
        @see: GraphicsMode._drawLabels()
        """
        _superclass_for_GM._drawLabels(self)
        draw_dnaBaseNumberLabels(self.glpane)
    
# == Command part

class OrderDna_Command(EditCommand): 
    """
    
    """
   
    # class constants
    
    commandName = 'ORDER_DNA'
    featurename = "Order DNA"
    from utilities.constants import CL_EXTERNAL_ACTION
    command_level = CL_EXTERNAL_ACTION
         
    GraphicsMode_class = OrderDna_GraphicsMode
    
    PM_class = OrderDna_PropertyManager
   
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True
    
    flyoutToolbar = None
    
    def _getFlyoutToolBarActionAndParentCommand(self):
        """
        Overides superclass method. 
        @see: self.command_update_flyout()
        """
        flyoutActionToCheck = 'orderDnaAction'
        parentCommandName = 'BUILD_DNA'    
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
        
        if not bool_keep:
            #Lets just not delete *ANY* DnaGroup while in OrderDna_Command
            #Although OrderDna command can only be accessed through
            #BuildDna_EditCommand, it could happen (due to a bug) that the 
            #previous command is not BuildDna_Editcommand. So bool_keep 
            #in that case will return False propmting dna updater to even delete
            #the empty DnaGroup (if it becomes empty for some reasons) of the 
            #BuildDna command. To avoid this ,this method will instruct 
            # to keep all instances of DnaGroup even when they might be empty.            
            if isinstance(group, self.assy.DnaGroup):
                bool_keep = True
            #Commented out code that shows what I was planning to implement 
            #earlier. 
            ##previousCommand = self.commandSequencer.prevMode # keep_empty_group: .struct
            ##if previousCommand.commandName == 'BUILD_DNA':
                ##if group is previousCommand.struct:
                    ##bool_keep = True                                
        
        return bool_keep
