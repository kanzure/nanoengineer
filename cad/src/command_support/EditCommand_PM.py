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

from PM.PM_Dialog import PM_Dialog
from PyQt4.Qt import SIGNAL

from utilities.exception_classes import AbstractMethod
from utilities.icon_utilities import geticon
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction

#debug flag to keep signals always connected
from utilities.GlobalPreferences import KEEP_SIGNALS_ALWAYS_CONNECTED
from utilities.GlobalPreferences import USE_COMMAND_STACK

class EditCommand_PM(PM_Dialog):
    """
    This is a superclass for the property managers of various objects that use
    EditCommand for generating the object. e.g. PlanePropertyManager
    inherits from this class to use common methods
    """
    # The title that appears in the Property Manager header.
    title = "Property Manager"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = ""

    def __init__(self, command):
        """
        Constructor for the EditCommand_PM
        """
        # pw = part window.
        # Its subclasses will create their partwindow objects
        # (and destroy them after Done) -- @@ not be a good idea if we have
        # multiple partwindow support? (i.e. when win object is replaced(?) by
        # partwindow object for each partwindow).  But this works fine.
        # ..same guess -- because opening multiple windows is not supported
        # When we begin supporting that, lots of things will change and this
        # might be one of them .--- ninad 20070613

        self.command = command

        self.win =  self.command.win
        self.w = self.command.win
        self.pw       =  None
        
        PM_Dialog.__init__(self,
                           self.pmName,
                           self.iconPath,
                           self.title
                       )       
        
        if KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)

    def setEditCommand(self, command):
        """
        """
        assert command
        self.command = command
        
        
    def show(self):
        """
        Shows the Property Manager. Overrides PM_Dialog.show)
        """
        self._update_widgets_in_PM_before_show()
        PM_Dialog.show(self)
        
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)
            
        self.enable_or_disable_gui_actions(bool_enable = False)
        

    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """
        
        if not USE_COMMAND_STACK:
            #First exit temporary modes (e.g. Pan mode) if any.
            currentCommand = self.win.commandSequencer.currentCommand
            if not currentCommand.command_has_its_own_PM:
                currentCommand.Done()
            
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(False)
            
        self.enable_or_disable_gui_actions(bool_enable = True)
        PM_Dialog.close(self)

    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot
                          method.
        @type  isConnect: boolean
        """
        pass
    

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

    def enable_or_disable_gui_actions(self, bool_enable = False):
        """
        Enable or disable some gui actions when this property manager is
        opened or closed, depending on the bool_enable.
        Subclasses can override this method.
        """
        pass


    def _addGroupBoxes(self):
        """
        Add various group boxes to this PM.
        Abstract method.
        """
        raise AbstractMethod()

    def _addWhatsThisText(self):
        """
        Add what's this text.
        Abstract method.
        """
        raise AbstractMethod()

    def ok_btn_clicked(self):
        """
        Implements Done button

        [extends superclass method]
        """
        if not USE_COMMAND_STACK:
            self.command.preview_or_finalize_structure(previewing = False)
            #This should be cleaned up in a refactoring. There should be a central
            #updater which should ask when to print a message etc. There could be
            #mab=ny subclasses without a logMessage. Also, I am not removing 
            #the call that prints history message as some subclasses might be 
            #using it. For now, just do a hasattr test -- Ninad 2008-07-23
            if hasattr(self.command, 'logMessage'):
                env.history.message(self.command.logMessage)
                
        PM_Dialog.ok_btn_clicked(self)

    def cancel_btn_clicked(self):
        """
        Implements Cancel button

        [extends superclass method]
        """
        if self.command:
            self.command.cancelStructure()
        ## self.win.toolsCancel() #bruce 080815 replaced this with superclass call
        PM_Dialog.cancel_btn_clicked(self)

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
    