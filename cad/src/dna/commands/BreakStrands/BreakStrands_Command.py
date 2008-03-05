# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

TODOs: [ as of 2008-01-04]
- To be revised heavily . Still a stub, needs documentation.
- bondLeftup deletes any bonds -- it should only break strands. 
- Move BreakStrands_GraphicsMode into its own module when need arises. 
"""

import changes
from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from constants             import red
from dna.commands.BreakStrands.BreakStrands_PropertyManager import BreakStrands_PropertyManager

from TemporaryCommand import ESC_to_exit_GraphicsMode_preMixin
# == GraphicsMode part

_superclass_for_GM = BuildAtoms_GraphicsMode

class BreakStrands_GraphicsMode( ESC_to_exit_GraphicsMode_preMixin,
                                 BuildAtoms_GraphicsMode ):
    """
    Graphics mode for Break Strands command. 
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
        
    def _getBondHighlightColor(self, selobj):
        """
	Return the Bond highlight color . Since its a BreakStrands graphics
        mode, the color is 'red' by default. 
	@return: Highlight color of the object (Bond)
	
	""" 
        return red
        
    
  
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
                self.flyoutToolbar.breakStrandAction.setChecked(True)
            except AttributeError:
                self.flyoutToolbar = None
        
        if self.propMgr is None:
            self.propMgr = BreakStrands_PropertyManager(self)
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
    
   