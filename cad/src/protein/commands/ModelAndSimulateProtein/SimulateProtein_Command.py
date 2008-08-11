# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Urmi
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

"""
from utilities.debug import print_compact_stack, print_compact_traceback
from protein.commands.ModelAndSimulateProtein.ModelAndSimulateProtein_Command import ModelAndSimulateProtein_Command
class SimulateProtein_Command(ModelAndSimulateProtein_Command):
    
    featurename = 'Model and Simulate Protein Mode/Simulate Protein'
    commandName = 'SIMULATE_PROTEIN'
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True
    #Urmi 20080806: We may want it to have its own PM
    command_has_its_own_gui = False
    
    currentActiveTool = 'SIMULATE_PROTEIN'
    
    #class constants for the NEW COMMAND API -- 2008-07-30
    from utilities.constants import CL_SUBCOMMAND

    command_level = CL_SUBCOMMAND
    command_parent = 'MODEL_AND_SIMULATE_PROTEIN'
    
    def Enter(self):
        
        ModelAndSimulateProtein_Command.Enter(self)
        #REVIEW: NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
        self.command_enter_PM()     
        
        msg = "Select a simulation tool to either design or score "\
                "a protein sequence."
        self.propMgr.updateMessage(msg)
        self.command_enter_flyout()
        
    def command_enter_flyout(self):
        """
        REUSE the flyout toolbar from the parent_command (BuildAtoms_command 
        in this case)
        @TODO: 
        - may need cleanup in command stack refactoring. But the method name is 
        such that it fits the new method names in command API.         
        """
        self._reuse_attr_of_parentCommand('flyoutToolbar')
    
    def _reuse_attr_of_parentCommand(self, attr_name = ''): 
        """
        Reuse the given attr of the parent command. 
        Example: reuse 'flyoutToolbar' or 'propMgr' attrs in self. 
        @see: self.command_enter_flyout()
        """
        # WARNING: this code is duplicated in other places.
        # For comments about it, see one of them.
        
        if not attr_name:
            print_compact_stack("bug: trying to set an attr with no name "
                                "in this command: ")
            return
        
        previousCommand = self.find_parent_command_named( self.command_parent)
        
        if previousCommand:
            try:
                parent_attr = getattr(previousCommand, attr_name)
            except:
                msg = "bug: parent command %s doesn't have an " \
                      "attr named %r" % (previousCommand, attr_name)
                print_compact_traceback( msg + ": " )
                return                
                
            setattr(self, attr_name, parent_attr)

        else:
            msg = "bug: parent command %s not found" % self.command_parent
            print_compact_stack( msg + ": " )
        return

    def command_enter_PM(self):
        """
        #REVIEW: NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
        """
        self._reuse_attr_of_parentCommand('propMgr')
        
    
        
    def init_gui(self):
        
        pass
    
    def restore_gui(self):
          
        pass    