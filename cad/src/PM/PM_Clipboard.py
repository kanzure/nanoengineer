# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_Clipboard.py

The PM_Clipboard class provides a groupbox containing a list of clipboard
items that can be pasted in the 3D Workspace. The selected item in this
list is shown by its elementViewer (an instance of L{PM_PreviewGroupBox})
The object being previewed can then be deposited into the 3D workspace.

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:
ninad 2007-08-29: Created. (Initially to support the clipboard in L{PasteFromClipboard_Command})

"""

from PyQt4.Qt import QListWidget
from PyQt4.Qt import SIGNAL
from graphics.widgets.ThumbView import MMKitView
from PM.PM_GroupBox import PM_GroupBox
from utilities.constants import diTUBES

class PM_Clipboard(PM_GroupBox):
    """
    The PM_Clipboard class provides a groupbox containing a list of clipboard
    items that can be pasted in the 3D Workspace. The selected item in this
    list is shown by its elementViewer (an instance of L{PM_PreviewGroupBox})
    The object being previewed can then be deposited into the 3D workspace.
    """
    def __init__(self,
                parentWidget,
                title = 'Clipboard',
                win   = None,
                elementViewer = None
                ):

        """
        Appends a PM_Clipboard groupbox widget to I{parentWidget},a L{PM_Dialog}

        @param parentWidget: The parent dialog (Property manager) containing
                             this  widget.
        @type  parentWidget: L{PM_Dialog}

        @param title: The title (button) text.
        @type  title: str

        @param win: MainWindow object
        @type  win: L{MWsemantics} or None

        @param elementViewer: The associated preview pane groupbox. If provided,
                              The selected item in L{self.clipboardListWidget}
                              is shown (previewed) by L{elementViewer}.
                              The object being previewed can then be deposited
                              into the 3D workspace.
        @type  elementViewer: L{PM_PreviewGroupBox} or None

        """

        self.w = win
        self.elementViewer = elementViewer
        self.elementViewer.setDisplay(diTUBES)
        self.pastableItems = None

        PM_GroupBox.__init__(self, parentWidget, title)

        self._loadClipboardGroupbox()


    def _loadClipboardGroupbox(self):
        """
        Load the L{self.clipboardListWidget} widget used to display a list of
        clipboard items inside this  clipboard  groupbox.
        """
        self.clipboardListWidget = QListWidget(self)

        self.gridLayout.addWidget(self.clipboardListWidget)
        #Append to the widget list. This is important for expand -collapse
        #functions (of the groupbox) to work properly.
        self._widgetList.append(self.clipboardListWidget)

    def _updateElementViewer(self, newModel = None):
        """
        Update the view of L{self.elementViewer}
        @param newModel: The model correseponding to the item selected
                         in L{self.clipboardListWidget}.
        @type  newModel: L{molecule} or L{Group}
        """
        if not self.elementViewer:
            return

        assert isinstance(self.elementViewer, MMKitView)
        self.elementViewer.resetView()
        if newModel:
            self.elementViewer.updateModel(newModel)

    def update(self):
        """
        Updates the clipboard items in the L{PM_Clipboard} groupbox. Also
        updates its element viewer.
        """
        PM_GroupBox.update(self)
        self.pastableItems = self.w.assy.shelf.getPastables()
        i = self.clipboardListWidget.currentRow()
        self.clipboardListWidget.clear()
        newModel = None

        if len(self.pastableItems):
            for item in self.pastableItems:
                self.clipboardListWidget.addItem(item.name)

            if i >= self.clipboardListWidget.count():
                i = self.clipboardListWidget.count() - 1

            if i < 0:
                i = 0

            self.clipboardListWidget.setCurrentItem(
                    self.clipboardListWidget.item(i))


            newModel = self.pastableItems[i]

        self._updateElementViewer(newModel)

    def clipboardListItemChanged(self, currentItem = None, previousItem = None):
        """
        Slot method. Called when user clicks on a different pastable item
        displayed in this groupbox
        @param currentItem: Current item in the L{self.clipboardListWidget}
                            that is selected
        @type  currentItem: U{B{QListWidgetItem}
                            <http://doc.trolltech.com/4.2/qlistwidgetitem.html>}
        @param previousItem: Previously selected item in the
                            L{self.clipboardListWidget}
        @type  previousItem: U{B{QListWidgetItem}
                            <http://doc.trolltech.com/4.2/qlistwidgetitem.html>}
        """

        if not (currentItem or previousItem):
            return

        itemId = self.clipboardListWidget.row(currentItem)

        if itemId != -1:

            newChunk = self.pastableItems[itemId]
            self.clipboardListWidget.setCurrentRow(itemId)
            self._updateElementViewer(newChunk)


    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot
                          method.
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect

        change_connect(
            self.clipboardListWidget,
            SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"),
            self.clipboardListItemChanged )

    def currentRow(self):
        """
        Return the current row of the selected item in this groupbox's
        listwidget ( L{self.clipboardListWidget} )
        @return: Current Row of the selected pastable item in the
                 clipboard groupbox.
        @rtype: int
        """
        currentRow = self.clipboardListWidget.currentRow()
        return currentRow


