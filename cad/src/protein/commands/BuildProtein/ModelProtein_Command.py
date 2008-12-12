# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Urmi
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

"""
from utilities.debug import print_compact_stack, print_compact_traceback
from protein.commands.BuildProtein.BuildProtein_Command import BuildProtein_Command

_superclass = BuildProtein_Command
class ModelProtein_Command(BuildProtein_Command):
    """
    Class for modeling proteins
    """
    
    FlyoutToolbar_class = None
    
    featurename = 'Model and Simulate Protein Mode/Model Protein'
    commandName = 'MODEL_PROTEIN'
    
    command_should_resume_prevMode = True
    #Urmi 20080806: We may want it to have its own PM
    command_has_its_own_PM = False
    
    _currentActiveTool = 'MODEL_PROTEIN'
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
        msg = "Select <b>Insert Peptide</b> to create a peptide chain or "\
            "select another modeling tool to modify an existing "\
            "peptide/protein sequence."
        self.propMgr.updateMessage(msg)
