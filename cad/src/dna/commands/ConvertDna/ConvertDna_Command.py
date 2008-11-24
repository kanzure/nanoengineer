# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities.constants import CL_EXTERNAL_ACTION
from commands.SelectChunks.SelectChunks_Command import SelectChunks_Command
from dna.commands.ConvertDna.ConvertDna_GraphicsMode import ConvertDna_GraphicsMode
from dna.commands.ConvertDna.ConvertDna_PropertyManager import ConvertDna_PropertyManager

_superclass = SelectChunks_Command
    

class ConvertDna_Command(SelectChunks_Command):
    """
    "Convert DNA" command.
    """
    
    # class constants
    
    commandName = 'CONVERT_DNA'
    featurename = "Convert DNA"
    
    command_level = CL_EXTERNAL_ACTION
         
    GraphicsMode_class = ConvertDna_GraphicsMode
    
    PM_class = ConvertDna_PropertyManager
   
    command_should_resume_prevMode = True 
    command_has_its_own_PM = True
    
    flyoutToolbar = None
    
    
