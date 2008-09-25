# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Piotr
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

import foundation.changes as changes
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from commands.SelectChunks.SelectChunks_Command import SelectChunks_Command
from command_support.Command import Command
from utilities.constants import red
from commands.StereoProperties.StereoProperties_PropertyManager import StereoProperties_PropertyManager

# == GraphicsMode part

class StereoProperties_GraphicsMode(SelectChunks_GraphicsMode ):
    """
    Graphics mode for StereoProperties command. 
    """
    pass

# == Command part

class StereoProperties_Command(SelectChunks_Command): 
    """

    """
       
    # class constants
    GraphicsMode_class = StereoProperties_GraphicsMode
    PM_class = StereoProperties_PropertyManager
    
    commandName = 'STEREO_PROPERTIES'
    featurename = "Stereo View Properties"
    from utilities.constants import CL_GLOBAL_PROPERTIES
    command_level = CL_GLOBAL_PROPERTIES
   

    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True

    flyoutToolbar = None
    