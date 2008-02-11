# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODOs: 
Many changes planned in JoinStrands_GraphicsMode . 
"""


from BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
from BuildAtoms_Command    import BuildAtoms_Command
# == GraphicsMode part

_superclass_for_GM = BuildAtoms_GraphicsMode

class JoinStrands_GraphicsMode( BuildAtoms_GraphicsMode ):
    """
    Graphics mode for Join strands command
    
    """  
    
    pass  
    
  
# == Command part

class JoinStrands_Command(BuildAtoms_Command): 
    """
    Command part for joining two strands. 
    
    """
    # class constants
    
    commandName = 'JOIN_STRANDS'
    default_mode_status_text = ""
    featurename = "Join Strands"
         
    hover_highlighting_enabled = True
    GraphicsMode_class = JoinStrands_GraphicsMode
   
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_gui = False
    
    flyoutToolbar = None

    
    def init_gui(self):
        """
        Initialize GUI for this mode 
        """
        previousCommand = self.commandSequencer.prevMode 
        if previousCommand.commandName == 'BUILD_DNA':
            try:
                self.flyoutToolbar = previousCommand.flyoutToolbar
            except AttributeError:
                self.flyoutToolbar = None
            
        pass 
        
    def restore_gui(self):
        """
        Restore the GUI 
        """
        if self.flyoutToolbar:
            self.flyoutToolbar.dnaDuplexAction.setChecked(False)
        pass
    
   