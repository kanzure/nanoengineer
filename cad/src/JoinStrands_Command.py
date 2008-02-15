# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODOs: 
Many changes planned in JoinStrands_GraphicsMode . 
"""
import changes

from BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
from BuildAtoms_Command    import BuildAtoms_Command
from JoinStrands_PropertyManager import JoinStrands_PropertyManager
from TemporaryCommand import ESC_to_exit_GraphicsMode_preMixin
# == GraphicsMode part

_superclass_for_GM = BuildAtoms_GraphicsMode

class JoinStrands_GraphicsMode( ESC_to_exit_GraphicsMode_preMixin,
                                BuildAtoms_GraphicsMode ):
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
    command_has_its_own_gui = True
    
    flyoutToolbar = None

    
    def init_gui(self):
        """
        Initialize GUI for this mode 
        """
        previousCommand = self.commandSequencer.prevMode 
        if previousCommand.commandName == 'BUILD_DNA':
            try:
                self.flyoutToolbar = previousCommand.flyoutToolbar
                #Need a better way to deal with changing state of the 
                #corresponding action in the flyout toolbar. To be revised 
                #during command toolbar cleanup 
                self.flyoutToolbar.joinStrandsAction.setChecked(True)
            except AttributeError:
                self.flyoutToolbar = None
        if self.propMgr is None:
            self.propMgr = JoinStrands_PropertyManager(self)
            #@bug BUG: following is a workaround for bug 2494.
            #This bug is mitigated as propMgr object no longer gets recreated
            #for modes -- niand 2007-08-29
            changes.keep_forever(self.propMgr)  
            
        self.propMgr.show()    
       
        
    def restore_gui(self):
        """
        Restore the GUI 
        """
                    
        if self.propMgr is not None:
            self.propMgr.close()
    
   