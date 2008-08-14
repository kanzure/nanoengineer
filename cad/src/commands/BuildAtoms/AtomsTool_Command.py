# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
2008-07-30: Created to refactor Build Atoms command (currently called
BuildAtoms_Command).  

TODO:

- Classes created to refactor BuildAtoms_Command (rather 'BuildChunks' command)
to be revised further. 
- document
- REVIEW: _reusePropMgr_of_parentCommand -- this is an experimental method 
that will fit in the NEW command API (2008-07-30) . to be revised/ renamed. 
e.g. command_reuse_PM etc.
"""

from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from model.bond_constants import V_SINGLE, V_DOUBLE, V_TRIPLE, V_AROMATIC, V_CARBOMERIC, V_GRAPHITE
from utilities.constants import CL_SUBCOMMAND

_superclass = BuildAtoms_Command
class AtomsTool_Command(BuildAtoms_Command):
    
    featurename = 'Build Atoms Mode/AtomsTool'
    commandName = 'ATOMS_TOOL'
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True
    command_has_its_own_PM = False
    
    currentActiveTool = 'ATOMS_TOOL'
    
    
    #class constants for the NEW COMMAND API -- 2008-07-30
    command_level = CL_SUBCOMMAND
    command_parent = 'DEPOSIT'
    
    def Enter(self):
        _superclass.Enter(self)
        #NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
        self.command_enter_PM()
        
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
        
      
    def init_gui(self):
        pass
    
    def restore_gui(self):
        pass
    
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
    
    
