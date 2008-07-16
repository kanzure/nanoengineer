# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

This is a superclass for the property managers of various objects that use
EditCommand for generating the object. e.g. PlanePropertyManager inherits
from this class to use common methods such as ok_btn_cliked.

"""

import foundation.env as env

from PM.PM_Dialog import PM_Dialog
from PyQt4.Qt import SIGNAL

from command_support.GeneratorBaseClass import AbstractMethod
from utilities.icon_utilities import geticon
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction

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

    def __init__(self, win, editCommand = None):
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

        self.editCommand = editCommand
        if editCommand:
            self.struct = self.editCommand.struct
        else:
            self.struct = None

        self.win      =  win
        self.w = win
        self.pw       =  None
        self.modePropertyManager = None


        PM_Dialog.__init__(self,
                           self.pmName,
                           self.iconPath,
                           self.title
                       )

        self._createFlyoutActions()

    def setEditCommand(self, editCommand):
        """
        """
        assert editCommand
        self.editCommand = editCommand
        self.struct = self.editCommand.struct

    def show(self):
        """
        Shows the Property Manager. Overrides PM_Dialog.show)
        """
        self._update_widgets_in_PM_before_show()
        PM_Dialog.show(self)
        self.connect_or_disconnect_signals(isConnect = True)
        self.enable_or_disable_gui_actions(bool_enable = False)
        self.updateCommandToolbar(bool_entering = True)

    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """
        #First exit temporary modes (e.g. Pan mode) if any.
        currentCommand = self.win.commandSequencer.currentCommand
        if not currentCommand.command_has_its_own_gui:
            currentCommand.Done()
        self.connect_or_disconnect_signals(False)
        self.enable_or_disable_gui_actions(bool_enable = True)
        self.updateCommandToolbar(bool_entering = False)
        PM_Dialog.close(self)

    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot
                          method.
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect

        if self.exitEditCommandAction:
            change_connect(self.exitEditCommandAction,
                           SIGNAL("triggered()"),
                           self.close)

    def _update_widgets_in_PM_before_show(self):
        """
        Update various widgets  in this Property manager. The default
        implementation does nothing. Overridden in subclasses. The various
        widgets , (e.g. spinboxes) will get values from the structure for which
        this propMgr is constructed for (seelf.editCommand.struct)

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
        if hasattr(self.struct, 'updateCosmeticProps'):
            self.struct.updateCosmeticProps()
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
        Slot for the OK button
        """
        if self.editCommand:
            self.editCommand.preview_or_finalize_structure(previewing = False)
            env.history.message(self.editCommand.logMessage)
        self.win.toolsDone()

    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """
        if self.editCommand:
            self.editCommand.cancelStructure()
        self.win.toolsCancel()

    def preview_btn_clicked(self):
        """
        Slot for the Preview button.
        """
        self.editCommand.preview_or_finalize_structure(previewing = True)
        env.history.message(self.editCommand.logMessage)

    def abort_btn_clicked(self):
        """
        Slot for Abort button
        """
        self.cancel_btn_clicked()

    def restore_defaults_btn_clicked(self):
        """
        Slot for Restore defaults button
        """
        pass

    def enter_WhatsThisMode(self):
        """
        Show what's this text
        """
        pass

    def _createFlyoutActions(self):
        self.exitEditCommandAction = NE1_QWidgetAction(self.win, win = self.win)
        if self.editCommand:
            text = "Exit " + self.editCommand.cmdname
        else:
            text = "Exit"
        self.exitEditCommandAction.setText(text)
        self.exitEditCommandAction.setIcon(
            geticon("ui/actions/Toolbars/Smart/Exit.png"))
        self.exitEditCommandAction.setCheckable(True)

    def getFlyoutActionList(self):
        """
        returns custom actionlist that will be used in a specific mode
        or editing a feature etc Example: while in movie mode,
        the _createFlyoutToolBar method calls
        this
        Subclasses must override this method if they need their own flyout
        toolbar
        """

        #'allActionsList' returns all actions in the flyout toolbar
        #including the subcontrolArea actions
        allActionsList = []

        #Action List for  subcontrol Area buttons.
        #In this mode there is really no subcontrol area.
        #We will treat subcontrol area same as 'command area'
        #(subcontrol area buttons will have an empty list as their command area
        #list). We will set  the Comamnd Area palette background color to the
        #subcontrol area.

        subControlAreaActionList =[]

        #Action list for the command area button (the actions meant for the
        commandActionLists = []

        params = (subControlAreaActionList, commandActionLists, allActionsList)

        return params

    def updateCommandToolbar(self, bool_entering = True):
        """
        Update the command toolbar
        Subclasses should override this method if they need their flyout toolbar
        """

        #Note to Eric M:
        # This needs cleanup. This is a temporary implementation --ninad20071025
        pass


