# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Urmi
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

"""
from utilities.debug import print_compact_stack, print_compact_traceback
from protein.commands.ModelAndSimulateProtein.ModelAndSimulateProtein_Command import ModelAndSimulateProtein_Command
class SimulateProtein_Command(ModelAndSimulateProtein_Command):
    """
    Class for simulating proteins
    """
    featurename = 'Model and Simulate Protein Mode/Simulate Protein'
    commandName = 'SIMULATE_PROTEIN'
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True
    #Urmi 20080806: We may want it to have its own PM
    command_has_its_own_PM = False
    
    currentActiveTool = 'SIMULATE_PROTEIN'
    
    #class constants for the NEW COMMAND API -- 2008-07-30
    from utilities.constants import CL_SUBCOMMAND

    command_level = CL_SUBCOMMAND
    command_parent = 'MODEL_AND_SIMULATE_PROTEIN'
    
    def Enter(self):
        """
        Enter the protein simulation command.
        """
        ModelAndSimulateProtein_Command.Enter(self)
        #REVIEW: NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
        self.command_enter_PM()     
        
        msg = "Select a simulation tool to either design or score "\
                "a protein sequence."
        self.propMgr.updateMessage(msg)
        self.command_enter_flyout()
        
    def command_enter_flyout(self):
        """
        REUSE the flyout toolbar from the parent_command         
        """
        self._reuse_attr_of_parentCommand('flyoutToolbar')
    
               
    def init_gui(self):
        
        pass
    
    def restore_gui(self):
          
        pass    