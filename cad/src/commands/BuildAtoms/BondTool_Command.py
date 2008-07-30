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
from commands.BuildAtoms.BondTool_GraphicsMode import DeleteBondTool_GraphicsMode
from commands.BuildAtoms.BondTool_GraphicsMode import BondTool_GraphicsMode
from model.bond_constants import V_SINGLE, V_DOUBLE, V_TRIPLE, V_AROMATIC, V_CARBOMERIC, V_GRAPHITE
from utilities.constants import CL_SUBCOMMAND

class BondTool_Command(BuildAtoms_Command):
    """
    Each of the subclass of this class represent a temporary command that 
    will act like 'activating a tool'. Example: when user clicks on single Bonds 
    tool, it will enter Single Bond Tool command. , suspending the Build Chunks
    default command.
    """
    GraphicsMode_class = BondTool_GraphicsMode
    commandName = 'BOND_TOOL'
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True
    command_has_its_own_gui = False
    
    currentActiveTool = 'BONDS_TOOL'
    
    
    #class constants for the NEW COMMAND API -- 2008-07-30
    command_level = CL_SUBCOMMAND
    command_parent = 'DEPOSIT'
    
    def Enter(self):
        BuildAtoms_Command.Enter(self)
        #REVIEW: NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
        self._reusePropMgr_of_parentCommand()
        
    def _reusePropMgr_of_parentCommand(self):
        """
        #REVIEW: NEW COMMAND API SHOULD REVISE THIS METHOD -- 2008-07-30
        """
        commandSequencer = self.win.commandSequencer
        previousCommand = commandSequencer.prevMode
        if  previousCommand and  previousCommand.commandName == self.command_parent:
            self.propMgr = previousCommand.propMgr
    
    def init_gui(self):
        pass
    
    def restore_gui(self):
        pass
    
    def getBondType(self):
        return V_SINGLE
    
    #TEMPORARILY override the is*ToolActive methods in BuildAtoms_Command. 
    #These methods will go away when BuildAtoms command starts treating 
    #each tool as a subcommand. 
    def isAtomsToolActive(self):
        """
        Tells whether the Atoms Tool is active (boolean)          
        """        
        return False
    
    def isBondsToolActive(self):
        """
        Tells whether the Bonds Tool is active (boolean)          
        """        
        return True
    
    def isDeletBondsToolActive(self):
        """
        Tells whether the Delete Bonds Tool is active (boolean)          
        """        
        return False
    
#####################

#classes need to be in their own module
class SingleBondTool(BondTool_Command):
    commandName = 'SINGLE_BOND_TOOL'            
    def getBondType(self):
        return V_SINGLE

class DoubleBondTool(BondTool_Command):
    commandName = 'DOUBLE_BOND_TOOL'
    def getBondType(self):
        return V_DOUBLE

class TripleBondTool(BondTool_Command):
    commandName = 'TRIPLE_BOND_TOOL'
    def getBondType(self):
        return V_TRIPLE
    
class AromaticBondTool(BondTool_Command):
    commandName = 'AROMATIC_BOND_TOOL'
    
    def getBondType(self):
        return V_AROMATIC

class GraphiticBondTool(BondTool_Command):
    commandName = 'GRAPHITIC_BOND_TOOL'
    
    def getBondType(self):
        return V_GRAPHITE

class DeleteBondTool(BondTool_Command):
    GraphicsMode_class = DeleteBondTool_GraphicsMode
    commandName = 'DELETE_BOND_TOOL'
    
