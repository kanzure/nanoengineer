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

from commands.LightingScheme.LightingScheme_PropertyManager import LightingScheme_PropertyManager

# == GraphicsMode part

_superclass_for_GM = SelectChunks_GraphicsMode

class LightingScheme_GraphicsMode( SelectChunks_GraphicsMode ):
    """
    Graphics mode for (DNA) Display Style command. 
    """
    pass
    
# == Command part


class LightingScheme_Command(EditCommand): 
    """
    
    """
    # class constants    
       
    #@TODO: may be it should inherit Select_Command. Check. 
    
    commandName = 'LIGHTING_SCHEME'
    featurename = "Lighting Scheme"
    from utilities.constants import CL_GLOBAL_PROPERTIES
    command_level = CL_GLOBAL_PROPERTIES
         
    GraphicsMode_class = LightingScheme_GraphicsMode
    
    PM_class = LightingScheme_PropertyManager
   
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True    
