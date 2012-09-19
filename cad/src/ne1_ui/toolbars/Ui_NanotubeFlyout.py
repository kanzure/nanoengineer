# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$

TODO: (list copied and kept from Ui_DnaFlyout.py --Mark)
- Does the parentWidget for the NanotubeFlyout always needs to be a propertyManager
  The parentWidget is the propertyManager object of the currentCommand on the
  commandSequencer. What if the currentCommand doesn't have a PM but it wants
  its own commandToolbar?  Use the mainWindow as its parentWidget?
- The implementation may change after Command Manager (Command toolbar) code
  cleanup. The implementation as of 2007-12-20 is an attempt to define
  flyouttoolbar object in the 'Command.

History:
- Mark 2008-03-8: This file created from a copy of Ui_DnaFlyout.py and edited.
"""


from PyQt4 import QtGui
from PyQt4.Qt import SIGNAL
from utilities.icon_utilities import geticon

from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction



from ne1_ui.toolbars.Ui_AbstractFlyout import Ui_AbstractFlyout


_superclass = Ui_AbstractFlyout
class NanotubeFlyout(Ui_AbstractFlyout):

    def _action_in_controlArea_to_show_this_flyout(self):
        """
        Required action in the 'Control Area' as a reference for this
        flyout toolbar. See superclass method for documentation and todo note.
        """
        return self.win.buildNanotubeAction

    def _getExitActionText(self):
        """
        Overrides superclass method.
        @see: self._createActions()
        """
        return "Exit NT"


    def getFlyoutActionList(self):
        """
        Returns a tuple that contains lists of actions used to create
        the flyout toolbar.
        Called by CommandToolbar._createFlyoutToolBar().
        @return: params: A tuple that contains 3 lists:
        (subControlAreaActionList, commandActionLists, allActionsList)
        """
        #'allActionsList' returns all actions in the flyout toolbar
        #including the subcontrolArea actions.
        allActionsList = []


        #Action List for  subcontrol Area buttons.
        subControlAreaActionList = []
        subControlAreaActionList.append(self.exitModeAction)
        separator = QtGui.QAction(self.parentWidget)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator)
        subControlAreaActionList.append(self.insertNanotubeAction)

        allActionsList.extend(subControlAreaActionList)

        commandActionLists = []
        #Append empty 'lists' in 'commandActionLists equal to the
        #number of actions in subControlArea
        for i in range(len(subControlAreaActionList)):
            lst = []
            commandActionLists.append(lst)

        params = (subControlAreaActionList, commandActionLists, allActionsList)

        return params

    def _createActions(self, parentWidget):

        _superclass._createActions(self, parentWidget)

        self.subControlActionGroup = QtGui.QActionGroup(self.parentWidget)
        self.subControlActionGroup.setExclusive(False)

        self.insertNanotubeAction = \
            NE1_QWidgetAction(self.subControlActionGroup,
                              win = self.win)
        self.insertNanotubeAction.setText("Insert NT")
        self.insertNanotubeAction.setCheckable(True)
        self.insertNanotubeAction.setIcon(
            geticon("ui/actions/Tools/Build Structures/InsertNanotube.png"))

        self.subControlActionGroup.addAction(self.insertNanotubeAction)

    def _addWhatsThisText(self):
        """
        Add 'What's This' help text for all actions on toolbar.
        """
        from ne1_ui.WhatsThisText_for_CommandToolbars import whatsThisTextForNanotubeCommandToolbar
        whatsThisTextForNanotubeCommandToolbar(self)
        return

    def _addToolTipText(self):
        """
        Add 'Tool tip' help text for all actions on toolbar.
        """
        from ne1_ui.ToolTipText_for_CommandToolbars import toolTipTextForNanotubeCommandToolbar
        toolTipTextForNanotubeCommandToolbar(self)
        return

    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot
                          method.
        @type  isConnect: boolean

        @see: self.activateFlyoutToolbar, self.deActivateFlyoutToolbar
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect

        _superclass.connect_or_disconnect_signals(self, isConnect)

        change_connect(self.insertNanotubeAction,
                             SIGNAL("triggered(bool)"),
                             self.activateInsertNanotubeLine_EditCommand)


    def resetStateOfActions(self):
        """
        Resets the state of actions in the flyout toolbar.
        Uncheck most of the actions. Basically it
        unchecks all the actions EXCEPT the ExitCntAction
        @see: self.deActivateFlyoutToolbar()
        @see: baseCommand.command_update_flyout()
        """

        #Uncheck all the actions in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action.isChecked():
                action.setChecked(False)


    def activateInsertNanotubeLine_EditCommand(self, isChecked):
        """
        Slot for (Insert) B{Nanotube} action.
        """

        self.win.insertNanotube(isChecked)

        #IMPORTANT:
        #For a QAction, the method
        #setChecked does NOT emmit the 'triggered' SIGNAL. So
        #we can call self.capCntAction.setChecked without invoking its
        #slot method!
        #Otherwise we would have needed to block the signal when action is
        #emitted ..example we would have called something like :
        #'if self._block_insertNanotubeAction_event: return' at the beginning of
        #this method. Why we didn't use QAction group -- We need these actions
        #to be
        # a) exclusive as well as
        #(b) 'toggle-able' (e.g. if you click on a checked action , it should
        #uncheck)
        #QActionGroup achieves (a) but can't do (b)

        #Uncheck all the actions except the dna duplex action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroup.actions():
            if action is not self.insertNanotubeAction and action.isChecked():
                action.setChecked(False)