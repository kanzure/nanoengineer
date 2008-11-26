# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Urmi
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

"""
from utilities.debug import print_compact_stack, print_compact_traceback
from protein.commands.ModelAndSimulateProtein.ModelAndSimulateProtein_Command import ModelAndSimulateProtein_Command

_superclass = ModelAndSimulateProtein_Command
class SimulateProtein_Command(ModelAndSimulateProtein_Command):
    """
    Class for simulating proteins
    """    
    FlyoutToolbar_class = None
    
    featurename = 'Model and Simulate Protein Mode/Simulate Protein'
    commandName = 'SIMULATE_PROTEIN'
    
    command_should_resume_prevMode = True
    #Urmi 20080806: We may want it to have its own PM
    command_has_its_own_PM = False
    
    currentActiveTool = 'SIMULATE_PROTEIN'
    
    #class constants for the NEW COMMAND API -- 2008-07-30
    from utilities.constants import CL_SUBCOMMAND

    command_level = CL_SUBCOMMAND
    command_parent = 'MODEL_AND_SIMULATE_PROTEIN'
    
    def command_entered(self):
        """
        Extends superclass method. 
        @see: baseCommand.command_entered() for documentation
        """
        _superclass.command_entered(self)
        msg = "Select a Rosetta simulation tool to either design or score "\
            "a peptide/protein sequence."
        self.propMgr.updateMessage(msg)