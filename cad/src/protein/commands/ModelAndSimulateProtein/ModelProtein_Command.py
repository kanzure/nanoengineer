# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Urmi
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

"""
from utilities.debug import print_compact_stack, print_compact_traceback
from protein.commands.ModelAndSimulateProtein.ModelAndSimulateProtein_Command import ModelAndSimulateProtein_Command
from utilities.GlobalPreferences import USE_COMMAND_STACK

_superclass = ModelAndSimulateProtein_Command
class ModelProtein_Command(ModelAndSimulateProtein_Command):
    """
    Class for modeling proteins
    """
    #Temporary attr 'command_porting_status. See baseCommand for details.
    command_porting_status = None #fully ported
    
    FlyoutToolbar_class = None
    
    featurename = 'Model and Simulate Protein Mode/Model Protein'
    commandName = 'MODEL_PROTEIN'
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True
    #Urmi 20080806: We may want it to have its own PM
    command_has_its_own_PM = False
    
    currentActiveTool = 'MODEL_PROTEIN'
    from utilities.constants import CL_SUBCOMMAND

    #class constants for the NEW COMMAND API -- 2008-07-30
    command_level = CL_SUBCOMMAND
    command_parent = 'MODEL_AND_SIMULATE_PROTEIN'
    
    def command_entered(self):
        """
        Extends superclass method. 
        @see: baseCommand.command_entered() for documentation
        """
        _superclass.command_entered(self)
        msg = "Select a modeling tool to either modify an existing protein "\
                    "or create a new peptide chain."
        self.propMgr.updateMessage(msg)
        

    if not USE_COMMAND_STACK:
    
        def Enter(self):
            """
            Enter modeling protein command
            """
            ModelAndSimulateProtein_Command.Enter(self)
            #REVIEW: NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
            self.command_enter_PM()     
            
            msg = "Select a modeling tool to either modify an existing protein "\
                    "or create a new peptide chain."
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