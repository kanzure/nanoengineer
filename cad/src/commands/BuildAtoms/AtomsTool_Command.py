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
"""

from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from commands.BuildAtoms.BondTool_GraphicsMode import DeleteBondTool_GraphicsMode
from commands.BuildAtoms.BondTool_GraphicsMode import BondTool_GraphicsMode
from model.bond_constants import V_SINGLE, V_DOUBLE, V_TRIPLE, V_AROMATIC, V_CARBOMERIC, V_GRAPHITE
from utilities.constants import CL_SUBCOMMAND

class AtomsTool_Command(BuildAtoms_Command):
    
    GraphicsMode_class = BondTool_GraphicsMode
    commandName = 'ATOMS_TOOL'
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True
    command_has_its_own_gui = False
    
    currentActiveTool = 'ATOMS_TOOL'
    
    
    #class constants for the NEW COMMAND API -- 2008-07-30
    command_level = CL_SUBCOMMAND
    command_parent = 'DEPOSIT'
    
    
    def init_gui(self):
        pass
    
    def restore_gui(self):
        pass