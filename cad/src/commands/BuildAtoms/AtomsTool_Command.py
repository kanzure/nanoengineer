# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
2008-07-30: Created to refactor Build Atoms command (currently called
BuildAtoms_Command).  

TODO:

- Classes created to refactor BuildAtoms_Command 
to be revised further. 
- document
- REVIEW: _reusePropMgr_of_parentCommand -- this is an experimental method 
that will fit in the NEW command API (2008-07-30) . to be revised/ renamed. 
e.g. command_reuse_PM etc.

- Update methods (e.g. self.propMgr.updateMessage() need to be called 
by a central method such as command_update_* or PM._update_UI_*. 

"""

from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from model.bond_constants import V_SINGLE, V_DOUBLE, V_TRIPLE, V_AROMATIC, V_CARBOMERIC, V_GRAPHITE
from utilities.constants import CL_SUBCOMMAND

_superclass = BuildAtoms_Command
class AtomsTool_Command(BuildAtoms_Command):
        
    FlyoutToolbar_class = None
    
    featurename = 'Build Atoms Mode/AtomsTool'
    commandName = 'ATOMS_TOOL'
    
    command_should_resume_prevMode = False
    command_has_its_own_PM = False
    
    currentActiveTool = 'ATOMS_TOOL'
    
    
    #class constants for the NEW COMMAND API -- 2008-07-30
    command_level = CL_SUBCOMMAND
    command_parent = 'DEPOSIT'
        
    #TEMPORARILY override the is*ToolActive methods in BuildAtoms_Command. 
    #These methods will go away when BuildAtoms command starts treating 
    #each tool as a subcommand. 
    
    def isAtomsToolActive(self):
        """
        Tells whether the Atoms Tool is active (boolean)          
        """        
        return True
    
    def isBondsToolActive(self):
        """
        Tells whether the Bonds Tool is active (boolean)          
        """        
        return False
    
    def isDeletBondsToolActive(self):
        """
        Tells whether the Delete Bonds Tool is active (boolean)          
        """        
        return False
    
    
