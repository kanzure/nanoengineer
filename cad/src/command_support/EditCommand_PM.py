# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

This is a superclass for the property managers of various objects that use
EditCommand for generating the object. e.g. PlanePropertyManager inherits
from this class to use common methods such as ok_btn_cliked.

"""
import foundation.env as env
from command_support.Command_PropertyManager import Command_PropertyManager

_superclass = Command_PropertyManager

class EditCommand_PM(Command_PropertyManager):
    """
    This is a superclass for the property managers of various objects that use
    EditCommand for generating the object. e.g. PlanePropertyManager
    inherits from this class to use common methods
    """ 
        
    def show(self):
        """
        Shows the Property Manager. Extends superclass method.
        """
        self._update_widgets_in_PM_before_show()
        _superclass.show(self)                  

    def _update_widgets_in_PM_before_show(self):
        """
        Update various widgets  in this Property manager. The default
        implementation does nothing. Overridden in subclasses. The various
        widgets , (e.g. spinboxes) will get values from the structure for which
        this propMgr is constructed for (seelf.command.struct)

        @see: RotaryMotorPropertyManager._update_widgets_in_PM_before_show
        @see: self.show where it is called.
        """
        pass

    def update_props_if_needed_before_closing(self):
        """
        This updates some cosmetic properties of the Rotary motor (e.g. opacity)
        before closing the Property Manager.
        This is the default implemetation. Subclasses may override this method
        @see: L{PlanePropertManager.update_props_if_needed_before_closing}
              where this method is overridden.
        """
        #API method. See Plane.update_props_if_needed_before_closing for another
        #example.
        # Example: The Rotary Motor Property Manager is open and the user is
        # 'previewing' the motor. Now the user clicks on "Build > Atoms"
        # to invoke the next command (without clicking "Done").
        # This calls self.open() which replaces the current PM
        # with the Build Atoms PM.  Thus, it creates and inserts the motor
        # that was being previewed. Before the motor is permanently inserted
        # into the part, it needs to change some of its cosmetic properties
        # (e.g. opacity) which distinguishes it as
        # a previewed motor in the part. This function changes those properties.
        # [ninad 2007-10-09 comment]

        #called from updatePropertyManager in Ui_PartWindow.py (Partwindowclass)
        if self.command.struct and hasattr(self.command.struct, 'updateCosmeticProps'):
            self.command.struct.updateCosmeticProps()
        self.enable_or_disable_gui_actions(bool_enable = True)

    def preview_btn_clicked(self):
        """
        Implements Preview button.
        """
        self.command.preview_or_finalize_structure(previewing = True)
        env.history.message(self.command.logMessage)

    def restore_defaults_btn_clicked(self):
        """
        Implements Restore defaults button
        """
        pass
    