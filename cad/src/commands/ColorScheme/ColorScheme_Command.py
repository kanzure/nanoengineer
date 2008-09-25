# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Urmi
@version:   $Id$
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
    
    #@TODO: may be it should inherit Select_Command. Check. 
       
    commandName = 'COLOR_SCHEME'
    featurename = "Color Scheme"
    from utilities.constants import CL_GLOBAL_PROPERTIES
    command_level = CL_GLOBAL_PROPERTIES
         
    GraphicsMode_class = ColorScheme_GraphicsMode
    
    PM_class = ColorScheme_PropertyManager
        
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True
    
