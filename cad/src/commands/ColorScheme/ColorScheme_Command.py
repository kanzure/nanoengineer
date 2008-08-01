# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Urmi
@version:   $Id: ColorScheme_Command.py 12835 2008-05-19 18:58:51Z urmim $
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

import foundation.changes as changes
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from command_support.EditCommand import EditCommand
from utilities.constants import red

from commands.ColorScheme.ColorScheme_PropertyManager import ColorScheme_PropertyManager

# == GraphicsMode part

_superclass_for_GM = SelectChunks_GraphicsMode

class ColorScheme_GraphicsMode( SelectChunks_GraphicsMode ):
    """
    Graphics mode for (DNA) Display Style command. 
    """
    pass
    
# == Command part


class ColorScheme_Command(EditCommand): 
    """
    
    """
    # class constants
    
    # not sure which class should it inherit
    
    commandName = 'COLOR_SCHEME'
    featurename = "Color Scheme"
    from utilities.constants import CL_GLOBAL_PROPERTIES
    command_level = CL_GLOBAL_PROPERTIES
         
    GraphicsMode_class = ColorScheme_GraphicsMode
   
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_gui = True
    
    flyoutToolbar = None

    def init_gui(self):
        """
        Initialize GUI for this mode 
        """
        
        
        if self.propMgr is None:
            self.propMgr = ColorScheme_PropertyManager(self)
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
    
   
    
