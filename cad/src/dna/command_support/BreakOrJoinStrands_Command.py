# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
2008-08-06: refactored Break and Join Strands commands to create this new class

TODO:
"""


import foundation.env as env
from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from utilities.exception_classes import AbstractMethod
from utilities.constants import CL_SUBCOMMAND

_superclass = BuildAtoms_Command

class BreakOrJoinStrands_Command(BuildAtoms_Command):
    """
    A superclass for Break Strands and Join Strands commands
    """   
    
    #Property Manager class (overridden in subclasses)
    PM_class = None
    
    #Flyout toolbar class
    FlyoutToolbar_class = None
    
    command_level = CL_SUBCOMMAND
    command_parent = 'BUILD_DNA'
    __abstract_command_class = True #bruce 080905
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True
    
    
    
    flyoutToolbar = None   
    
    
    def _getFlyoutToolBarActionAndParentCommand(self):
        """
        See superclass for documentation.
        @see: self.command_update_flyout()
        """
        flyoutActionToCheck = self._get_init_gui_flyout_action_string()
        parentCommandName = None        
        return flyoutActionToCheck, parentCommandName
             
    
    def _get_init_gui_flyout_action_string(self):
        raise AbstractMethod
                  
            
    def command_enter_misc_actions(self):
        """
        Overrides superclass method. See superclass for documentation.
        """
        pass
    
    def command_exit_misc_action(self):
        """
        Overrides superclass method. See superclass for documentation.
        """
        pass      
    
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

        bool_keep = _superclass.keep_empty_group(self, group)

        if not bool_keep:
            #Lets just not delete *ANY* DnaGroup while in BreakStrands_Command
            #Although BreakStrands command can only be accessed through
            #BuildDna_EditCommand, it could happen (due to a bug) that the
            #previous command is not BuildDna_Editcommand. So bool_keep
            #in that case will return False propmting dna updater to even delete
            #the empty DnaGroup (if it becomes empty for some reasons) of the
            #BuildDna command. To avoid this ,this method will instruct
            # to keep all instances of DnaGroup even when they might be empty.
            if isinstance(group, self.assy.DnaGroup):
                bool_keep = True
            
        return bool_keep
    
