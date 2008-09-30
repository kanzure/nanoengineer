# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
RotateChunks_Command.py

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
Created while splitting class modifyMode into Command and GraphicsMode. 

NOTE:
As of 2008-01-25, this command is not yet used, however its graphics mode class
(RotateChunks_GraphicsMode) is used as an alternative graphics mode in 
Move_Command.
"""
from commands.Move.Move_Command import Move_Command
from commands.Rotate.RotateChunks_GraphicsMode import RotateChunks_GraphicsMode

_superclass = Move_Command
class RotateChunks_Command(Move_Command):
         
    commandName = 'ROTATE_CHUNKS'
    featurename = "Rotate Chunks"
    from utilities.constants import CL_EDIT_GENERIC
    command_level = CL_EDIT_GENERIC
    
    command_should_resume_prevMode = True 
    command_has_its_own_PM = False
    
    GraphicsMode_class = RotateChunks_GraphicsMode
    
        
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        As of 2008-01-25, this method does nothing.
        """
        pass
        
    
    
