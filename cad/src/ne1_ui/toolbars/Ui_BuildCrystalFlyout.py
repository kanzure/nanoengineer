# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
This class provides the flyout toolbar for BuildCrystals command

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-08-11: Created during command stack refactoring project

TODO:
"""
from ne1_ui.toolbars.Ui_AbstractFlyout import Ui_AbstractFlyout
from PyQt4.Qt import SIGNAL
from PyQt4 import QtGui
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction
from utilities.icon_utilities import geticon
_superclass = Ui_AbstractFlyout
class BuildCrystalFlyout(Ui_AbstractFlyout):
    """
    This class provides the flyout toolbar for BuildCrystals command
    """
    _subControlAreaActionList = []

    def _action_in_controlArea_to_show_this_flyout(self):
        """
        Required action in the 'Control Area' as a reference for this
        flyout toolbar. See superclass method for documentation and todo note.
        """
        return self.win.buildCrystalAction

    def _getExitActionText(self):
        """
        Overrides superclass method.
        @see: self._createActions()
        """
        return "Exit Crystal"

    def activateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides.
        @see: Ui_AbstractFlyout.activateFlyoutToolbar()
        """
        _superclass.activateFlyoutToolbar(self)
        self._setAutoShapeAcclKeys(True)

    def deActivateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides.
        @see: Ui_AbstractFlyout.deActivateFlyoutToolbar()
        """
        self._setAutoShapeAcclKeys(False)
        _superclass.deActivateFlyoutToolbar(self)

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

        _superclass.connect_or_disconnect_signals(self,
                                                  isConnect)

        change_connect(self.subControlActionGroup,
                       SIGNAL("triggered(QAction *)"),
                       self.parentWidget.changeSelectionShape)


    def _createActions(self, parentWidget):

        _superclass._createActions(self, parentWidget)

        # The subControlActionGroup is the parent of all flyout QActions.
        self.subControlActionGroup = QtGui.QActionGroup(parentWidget)

        self._subControlAreaActionList.append(self.exitModeAction)
        separator = QtGui.QAction(parentWidget)
        separator.setSeparator(True)
        self._subControlAreaActionList.append(separator)

        self.polygonShapeAction = NE1_QWidgetAction(self.subControlActionGroup,
                                                    win = self.win)
        self.polygonShapeAction.setObjectName("DEFAULT")
        self.polygonShapeAction.setText("Polygon")
        self._subControlAreaActionList.append(self.polygonShapeAction)

        self.circleShapeAction = NE1_QWidgetAction(self.subControlActionGroup,
                                                   win = self.win)
        self.circleShapeAction.setObjectName("CIRCLE")
        self.circleShapeAction.setText("Circle")
        self._subControlAreaActionList.append(self.circleShapeAction)

        self.squareShapeAction = NE1_QWidgetAction(self.subControlActionGroup,
                                                   win = self.win)
        self.squareShapeAction.setObjectName("SQUARE")
        self.squareShapeAction.setText("Square")
        self._subControlAreaActionList.append(self.squareShapeAction)

        self.rectCtrShapeAction = NE1_QWidgetAction(self.subControlActionGroup,
                                                    win = self.win)
        self.rectCtrShapeAction.setObjectName("RECTANGLE")
        self.rectCtrShapeAction.setText("RectCenter")
        self._subControlAreaActionList.append(self.rectCtrShapeAction)

        self.rectCornersShapeAction = NE1_QWidgetAction(self.subControlActionGroup,
                                                        win = self.win)
        self.rectCornersShapeAction.setObjectName("RECT_CORNER")
        self.rectCornersShapeAction.setText("RectCorners")
        self._subControlAreaActionList.append(self.rectCornersShapeAction)

        self.triangleShapeAction = NE1_QWidgetAction(self.subControlActionGroup,
                                                     win = self.win)
        self.triangleShapeAction.setObjectName("TRIANGLE")
        self.triangleShapeAction.setText("Triangle")
        self._subControlAreaActionList.append(self.triangleShapeAction)

        self.diamondShapeAction = NE1_QWidgetAction(self.subControlActionGroup,
                                                    win = self.win)
        self.diamondShapeAction.setObjectName("DIAMOND")
        self.diamondShapeAction.setText("Diamond")
        self._subControlAreaActionList.append(self.diamondShapeAction)

        self.hexagonShapeAction = NE1_QWidgetAction(self.subControlActionGroup,
                                                    win = self.win)
        self.hexagonShapeAction.setObjectName("HEXAGON")
        self.hexagonShapeAction.setText("Hexagon")
        self._subControlAreaActionList.append(self.hexagonShapeAction)

        self.lassoShapeAction = NE1_QWidgetAction(self.subControlActionGroup,
                                                  win = self.win)
        self.lassoShapeAction.setObjectName("LASSO")
        self.lassoShapeAction.setText("Lasso")
        self._subControlAreaActionList.append(self.lassoShapeAction)

        for action in self._subControlAreaActionList[1:]:
            if isinstance(action, NE1_QWidgetAction):
                action.setCheckable(True)
                self.subControlActionGroup.addAction(action)
                iconpath = "ui/actions/Command Toolbar/BuildCrystal/" + str(action.text()) + ".png"
                action.setIcon(geticon(iconpath))

        if not self.subControlActionGroup.checkedAction():
                self.polygonShapeAction.setChecked(True)

        return

    def getFlyoutActionList(self):
        """
        Returns a tuple that contains mode spcific actionlists in the
        added in the flyout toolbar of the mode.
        CommandToolbar._createFlyoutToolBar method calls this
        @return: params: A tuple that contains 3 lists:
        (subControlAreaActionList, commandActionLists, allActionsList)
        """
        #'allActionsList' returns all actions in the flyout toolbar
        #including the subcontrolArea actions
        allActionsList = []

        #Action List for  subcontrol Area buttons.
        #In this mode, there is really no subcontrol area.
        #We will treat subcontrol area same as 'command area'
        #(subcontrol area buttons will have an empty list as their command area
        #list). We will set  the Comamnd Area palette background color to the
        #subcontrol area.

        subControlAreaActionList =[]

        subControlAreaActionList.append(self.exitModeAction)
        subControlAreaActionList.extend(self._subControlAreaActionList)

        allActionsList.extend(subControlAreaActionList)

        #Empty actionlist for the 'Command Area'
        commandActionLists = []

        #Append empty 'lists' in 'commandActionLists equal to the
        #number of actions in subControlArea
        for i in range(len(subControlAreaActionList)):
            lst = []
            commandActionLists.append(lst)

        params = (subControlAreaActionList, commandActionLists, allActionsList)

        return params


    def _setAutoShapeAcclKeys(self, on):
        """
        If <on>, then set the acceleration keys for autoshape selection
        in this command; otherwise, like when exit. set it to empty.
        """
        if on:
            self.polygonShapeAction.setShortcut('P')
            self.circleShapeAction.setShortcut('C')
            self.rectCtrShapeAction.setShortcut('R')
            self.hexagonShapeAction.setShortcut('H')
            self.triangleShapeAction.setShortcut('T')
            self.rectCornersShapeAction.setShortcut('SHIFT+R')
            self.lassoShapeAction.setShortcut('L')
            self.diamondShapeAction.setShortcut('D')
            self.squareShapeAction.setShortcut('S')

        else:
            for btn in self.subControlActionGroup.actions():
                btn.setShortcut('')


    def getSelectionShape(self):
        """
        Return the current selection shape that is checked.
        """
        selectionShape = self.subControlActionGroup.checkedAction().objectName()
        return selectionShape

    def _addWhatsThisText(self):
        """
        Add 'What's This' help text for all actions on toolbar.
        """
        from ne1_ui.WhatsThisText_for_CommandToolbars import whatsThisTextForCrystalCommandToolbar
        whatsThisTextForCrystalCommandToolbar(self)
        return

    def _addToolTipText(self):
        """
        Add 'Tool tip' help text for all actions on toolbar.
        """
        from ne1_ui.ToolTipText_for_CommandToolbars import toolTipTextForCrystalCommandToolbar
        toolTipTextForCrystalCommandToolbar(self)
        return
