# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
QuteMol_Command.py

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
2008-07-24 : Created

TODO:
"""
import foundation.changes as changes
from commands.SelectChunks.SelectChunks_Command import SelectChunks_Command
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from commands.QuteMol.QuteMolPropertyManager import QuteMolPropertyManager

_superclass = SelectChunks_Command
class QuteMol_Command(SelectChunks_Command):
    commandName = 'QUTEMOL'
    featurename = "QuteMol"
    from utilities.constants import CL_EXTERNAL_ACTION
    command_level = CL_EXTERNAL_ACTION
    
    GraphicsMode_class = SelectChunks_GraphicsMode
    
    PM_class = QuteMolPropertyManager

    command_should_resume_prevMode = True 
    command_has_its_own_PM = True

    flyoutToolbar = None
    
  