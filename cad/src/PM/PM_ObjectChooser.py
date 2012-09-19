# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO
- remove all self.command calls.
"""
from PM.PM_SelectionListWidget import PM_SelectionListWidget
from utilities.constants import lightred_1, lightgreen_2
from PyQt4.Qt import Qt, SIGNAL
from PM.PM_ToolButton    import PM_ToolButton
from PM.PM_WidgetRow     import PM_WidgetRow

from PM.PM_GroupBox import PM_GroupBox
from utilities import debug_flags
from utilities.debug import print_compact_stack

_superclass = PM_GroupBox

class PM_ObjectChooser(PM_GroupBox):

    def __init__(self,
                 parentWidget,
                 command,
                 modelObjectType,
                 title = '' ,
                 addIcon = "ui/actions/Properties Manager"\
                        "/AddSegment_To_ResizeSegmentList.png",
                 removeIcon = "ui/actions/Properties Manager"\
                        "/RemoveSegment_From_ResizeSegmentList.png"):
        """
        """
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False

        _superclass.__init__(self,
                             parentWidget,
                             title = title)

        self.command = command
        self.win = self.command.win
        self._modelObjectType = modelObjectType

        self._addIcon = addIcon
        self._removeIcon = removeIcon

        self._loadWidgets()

    def getModelObjectType(self):
        return self._modelObjectType

    def setModelObjectType(self, modelObjtype):
        self._modelObjectType = modelObjtype

    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot
                          method.
        @type  isConnect: boolean
        """
        #TODO: This is a temporary fix for a bug. When you invoke a temporary mode
        # entering such a temporary mode keeps the signals of
        #PM from the previous mode connected (
        #but while exiting that temporary mode and reentering the
        #previous mode, it atucally reconnects the signal! This gives rise to
        #lots  of bugs. This needs more general fix in Temporary mode API.
        # -- Ninad 2008-01-09 (similar comment exists in MovePropertyManager.py

        if isConnect and self.isAlreadyConnected:
            if debug_flags.atom_debug:
                print_compact_stack("warning: attempt to connect widgets"\
                                    "in this PM that are already connected." )
            return

        if not isConnect and self.isAlreadyDisconnected:
            if debug_flags.atom_debug:
                print_compact_stack("warning: attempt to disconnect widgets"\
                                    "in this PM that are already disconnected.")
            return

        self.isAlreadyConnected = isConnect
        self.isAlreadyDisconnected = not isConnect

        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect


        self._listWidget.connect_or_disconnect_signals(isConnect)

        change_connect(self._addToolButton,
                       SIGNAL("toggled(bool)"),
                       self.activateAddTool)
        change_connect(self._removeToolButton,
                       SIGNAL("toggled(bool)"),
                       self.activateRemoveTool)


    def _loadWidgets(self):
        """
        """
        self._loadSelectionListWidget()
        self._loadAddRemoveButtons()

    def _loadSelectionListWidget(self):
        """
        """
        self._listWidget = PM_SelectionListWidget(
            self,
            self.win,
            label = "",
            heightByRows = 12)

        self._listWidget.setFocusPolicy(Qt.StrongFocus)
        self._listWidget.setFocus()
        self.setFocusPolicy(Qt.StrongFocus)

    def _loadAddRemoveButtons(self):
        """
        """
        self._addToolButton = PM_ToolButton(
                        self,
                        text = "Add items to the list",
                        iconPath  = self._addIcon,
                        spanWidth = True  )
        self._addToolButton.setCheckable(True)
        self._addToolButton.setAutoRaise(True)

        self._removeToolButton = PM_ToolButton(
                        self,
                        text = "Remove items from the list",
                        iconPath  = self._removeIcon,
                        spanWidth = True  )
        self._removeToolButton.setCheckable(True)
        self._removeToolButton.setAutoRaise(True)

        #Widgets to include in the widget row.
        widgetList = [
            ('QLabel', "  Add/Remove Items:", 0),
            ('QSpacerItem', 5, 5, 1),
            ('PM_ToolButton', self._addToolButton, 2),
             ('QSpacerItem', 5, 5, 3),
            ('PM_ToolButton', self._removeToolButton, 4),
            ('QSpacerItem', 5, 5, 5) ]

        widgetRow = PM_WidgetRow(self,
                                 title     = '',
                                 widgetList = widgetList,
                                 label = "",
                                 spanWidth = True )

    def isAddToolActive(self):
        """
        Returns True if the add objects tool is active.
        """

        if self._addToolButton.isChecked():
            #For safety
            if not self._removeToolButton.isChecked():
                return True

        return False

    def isRemoveToolActive(self):
        """
        Returns True if the remove segments tool (which removes the segments
        from the list of segments ) is active
        """
        if self._removeToolButton.isChecked():
            if not self._addToolButton.isChecked():
                #For safety
                return True
        return False

    def hasFocus(self):
        """
        Checks if the list widget that lists dnasegments (that will undergo
        special operations such as 'resizing them at once or making
        crossovers between the segments etc) has the
        Qt focus. This is used to just remove items from the list widget
        (without actually 'deleting' the corresponding Dnasegment in the GLPane)
        @see: MultipleDnaSegment_GraphicsMode.keyPressEvent() where it is called
        """
        if self._listWidget.hasFocus():
            return True
        return False


    def activateAddTool(self,enable):
        """
        Change the appearance of the list widget (that lists the dna segments
        ) so as to indicate that the add dna segments tool is
        active
        @param enable: If True, changes the appearance of list widget to
                       indicate that the add segments tool is active.
        @type  enable: bool
        """
        if enable:
            if not self._addToolButton.isChecked():
                self._addToolButton.setChecked(True)
            if self._removeToolButton.isChecked():
                self._removeToolButton.setChecked(False)
            self._listWidget.setAlternatingRowColors(False)
            self._listWidget.setColor(lightgreen_2)
            ##objectType = self._modelObjectType
            ##objectChooserType = 'ADD'
            ##self.command.activateObjectChooser((objectType, objectChooserType))
            ##self.command.logMessage('ADD_SEGMENTS_ACTIVATED')
        else:
            if self._addToolButton.isChecked():
                self._addToolButton.setChecked(False)
            self._listWidget.setAlternatingRowColors(True)
            self._listWidget.resetColor()

    def activateRemoveTool(self,enable):
        """
        Change the appearance of the list widget (that lists the dna segments
        ) so as to indicate that the REMOVE dna segments tool is
        active
        @param enable: If True, changes the appearance of list widget to
                       indicate that the REMOVE segments tool is active.
        @type  enable: bool
        """
        if enable:
            if not self._removeToolButton.isChecked():
                self._removeToolButton.setChecked(True)
            if self._addToolButton.isChecked():
                self._addToolButton.setChecked(False)
            self._listWidget.setAlternatingRowColors(False)
            ##self.command.logMessage('REMOVE_SEGMENTS_ACTIVATED')
            self._listWidget.setColor(lightred_1)
        else:
            if self._removeToolButton.isChecked():
                self._removeToolButton.setChecked(False)
            self._listWidget.setAlternatingRowColors(True)
            self._listWidget.resetColor()


    def _deactivateAddRemoveTools(self):
        """
        Deactivate tools that allow adding or removing the segments to the
        segment list in the Property manager. This can be simply done by
        resetting the state of toolbuttons to False.
        Example: toolbuttons that add or remove
        segments to the segment list in the Property manager. When self.show
        is called these need to be unchecked.
        @see: self.isAddSegmentsToolActive()
        @see:self.isRemoveSegmentsToolActive()
        @see: self.show()
        """
        self._addToolButton.setChecked(False)
        self._removeToolButton.setChecked(False)

    def removeItems(self):
        """
        Removes selected itoms from the dna segment list widget
        Example: User selects a bunch of items in the list widget and hits
        delete key  to remove the selected items from the list
        IMPORTANT NOTE: This method does NOT delete the correspoinging model
        item in the GLPane (i.e. corresponding dnasegment). It just 'removes'
        the item from the list widget
        This is intentional.
        """
        self._listWidget.deleteSelection()
        itemDict = self._listWidget.getItemDictonary()
        self.command.setSegmentList(itemDict.values())
        self.updateListWidget()
        self.win.win_update()


    def updateListWidget(self, objectList = []):
        """
        Update the list of segments shown in the segments list widget
        @see: self.updateListWidgets, self.updateStrandListWidget
        """

        self._listWidget.insertItems(
            row = 0,
            items = objectList)

