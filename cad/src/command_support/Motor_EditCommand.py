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

from utilities.GlobalPreferences import USE_COMMAND_STACK

_superclass = EditCommand
class Motor_EditCommand(EditCommand):
    """
    Superclass for various Motor edit commands
    """
    __abstract_command_class = True 
    
    #GraphicsMode
    GraphicsMode_class = SelectAtoms_GraphicsMode
    
    #Temporary attr 'command_porting_status. See baseCommand for details.
    command_porting_status = None #fully ported. But need cleanup in PMs of subclasses to move update_widgets_in_PM_* method to perhaps _update_UI_* method. 
    
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
     
    #Old command API methods (in if not USE_COMMAND_STACK condition block)
    if not USE_COMMAND_STACK:   
        def Enter(self):
            """
            Enter this command. 
            @see: EditCommand.Enter
            """
            #See EditCommand.Enter for a detailed comment on why self.struct is 
            #set to None while entering this command.
            #May not be needed for RotaryMotor and Linear motor edit commands, 
            # but safe to do it for now -- Ninad 2008-01-14
            if self.struct:
                self.struct = None        
            EditCommand.Enter(self)
            self.o.assy.permit_pick_atoms()
    
        def init_gui(self):
            """
            NOT IMPLEMENTED YET.
            TODO: Move calls that create/ show PM  in EditCommand.createStructure
                  out of that method. (That code was written before converting the 
                  editCommands into 'Commands'. After this conversion, a better 
                  implementation is necessary, in which PM creation and 
                  display will be handled  in init_gui method.
            """
            #Note: This method overrides EditCommand.init_gui. This is just to 
            #prevent the call of self.create_and_or_show_PM_if_wanted. , As that 
            # method is called in self.createStructure. (to be cleaned up)
            pass 
    
        def restore_gui(self):
            """
            """
            if self.propMgr:
                self.propMgr.close()

