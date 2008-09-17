# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
TranslateChunks_Command.py

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:

NOTE:
As of 2008-01-25, this command is not yet used, however its graphics mode class
(TranslateChunks_GraphicsMode) is used as an alternative graphics mode in 
Move_Command.
"""
from commands.Move.Move_Command import Move_Command
from commands.Translate.TranslateChunks_GraphicsMode import TranslateChunks_GraphicsMode
from utilities.GlobalPreferences import USE_COMMAND_STACK

_superclass = Move_Command
class TranslateChunks_Command(Move_Command):
    """
    Translate Chunks command
    """
    #Temporary attr 'command_porting_status. See baseCommand for details.
    command_porting_status = None #fully ported.
    
    commandName = 'TRANSLATE_CHUNKS'
    featurename = "Translate Chunks"
    from utilities.constants import CL_EDIT_GENERIC
    command_level = CL_EDIT_GENERIC
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_PM = False    
    GraphicsMode_class = TranslateChunks_GraphicsMode
        
    if not USE_COMMAND_STACK:  
        def init_gui(self):
            """
            Do changes to the GUI while entering this command.      
            Called once each time the command is entered; should be called only by 
            code  in modes.py
            As of 2008-01-25, this method does nothing.
            
            @see: L{self.restore_gui}
            """
            pass
        
        def restore_gui(self):
            """
            Do changes to the GUI while exiting this command. 
            As of 2008-01-25, this method does nothing.
            @see: L{self.init_gui}
            """
            pass
    
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        As of 2008-01-25, this method does nothing.
        """
        pass
        
    
    
