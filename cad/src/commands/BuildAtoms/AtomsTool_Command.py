# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-07-30: Created to refactor Build Chunks command (currently called
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
    
    
    commandName = 'ATOMS_TOOL'
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True
    command_has_its_own_gui = False
    
    currentActiveTool = 'ATOMS_TOOL'
    
    
    #class constants for the NEW COMMAND API -- 2008-07-30
    command_level = CL_SUBCOMMAND
    command_parent = 'DEPOSIT'
    
    def Enter(self):
        _superclass.Enter(self)
        #NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
        self._reusePropMgr_of_parentCommand()
        
    def _reusePropMgr_of_parentCommand(self):
        """
        #NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
        """
        commandSequencer = self.win.commandSequencer
        previousCommand = commandSequencer.prevMode
        if  previousCommand and  previousCommand.commandName == self.command_parent:
            self.propMgr = previousCommand.propMgr
        
    
    
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
    
    