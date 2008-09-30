# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-09-09: Moved common code from Rotarymotor and 
LinearMotor_EditCommand to here. 

TODO:
"""

from command_support.EditCommand import EditCommand
from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_GraphicsMode

_superclass = EditCommand
class Motor_EditCommand(EditCommand):
    """
    Superclass for various Motor edit commands
    """
    __abstract_command_class = True 
    
    #GraphicsMode
    GraphicsMode_class = SelectAtoms_GraphicsMode
    
    prefix = '' # Not used by jigs.
    # All jigs like rotary and linear motors already created their
    # name, so do not (re)create it from the prefix.
    create_name_from_prefix = False 
    propMgr = None

    #See Command.anyCommand for details about the following flags
    command_should_resume_prevMode = True
    command_has_its_own_PM = True
    
    from utilities.constants import CL_EDIT_GENERIC
    command_level = CL_EDIT_GENERIC
    
    
    
        
    def command_entered(self):
        """
        Overrides superclass method. 
        @see: baseCommand.command_entered()
        """
        self.struct = None 
        _superclass.command_entered(self)
        self.o.assy.permit_pick_atoms()        
     