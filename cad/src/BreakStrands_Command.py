# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODOs: [ as of 2008-01-04]
- To be revised heavily . Still a stub, needs documentation.
- bondLeftup deletes any bonds -- it should only break strands. 

"""


from BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
from BuildAtoms_Command    import BuildAtoms_Command
# == GraphicsMode part

_superclass_for_GM = BuildAtoms_GraphicsMode

class BreakStrands_GraphicsMode( BuildAtoms_GraphicsMode ):
    """
    
    """    
    def bondLeftUp(self, b, event): 
       
        """
        Delete the bond upon left up.
        """
        
        self.bondDelete(event)
        
  
    def update_cursor_for_no_MB(self): 
        """
        Update the cursor for this mode.
        """               
        self.glpane.setCursor(self.win.DeleteCursor)
    
  
# == Command part

class BreakStrands_Command(BuildAtoms_Command): 
    """
    
    """
    # class constants
    
    commandName = 'BREAK_STRANDS'
    default_mode_status_text = ""
    featurename = "Break Strands"
         
    hover_highlighting_enabled = True
    GraphicsMode_class = BreakStrands_GraphicsMode
   
    
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
    
   