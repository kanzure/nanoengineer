# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODOs: 
Many changes planned in JoinStrands_GraphicsMode . 
"""

from dna.commands.JoinStrands.JoinStrands_PropertyManager import JoinStrands_PropertyManager
from dna.command_support.BreakOrJoinStrands_Command import BreakOrJoinStrands_Command
from dna.commands.JoinStrands.JoinStrands_GraphicsMode import JoinStrands_GraphicsMode

# == Command part

_superclass = BreakOrJoinStrands_Command
class JoinStrands_Command(BreakOrJoinStrands_Command): 
    """
    Command part for joining two strands. 
    @see: superclass B{BreakOrJoinStrands_Command} 
    """
    # class constants
    
    commandName = 'JOIN_STRANDS'
    featurename = "Join Strands"   

    GraphicsMode_class = JoinStrands_GraphicsMode 
    PM_class = JoinStrands_PropertyManager
        
    def _get_init_gui_flyout_action_string(self):
        return 'joinStrandsAction'
    
          
