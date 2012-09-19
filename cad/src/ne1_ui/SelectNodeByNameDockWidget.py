# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created on 2008-11-06
TODO:
Created as a part of a NFR by Mark on Nov 6, 2008. This is a quick implementation
subjected to a number of changes / revisions.
"""
import foundation.env as env

from PyQt4.Qt import QToolButton
from PyQt4.Qt import QPalette
from PyQt4.Qt import QTextOption
from PyQt4.Qt import QLabel
from PyQt4.Qt import QAction, QMenu
from PyQt4.Qt import Qt, SIGNAL

from PM.PM_Colors    import getPalette
from PM.PM_Colors    import sequenceEditStrandMateBaseColor

from PM.PM_DockWidget import PM_DockWidget
from PM.PM_WidgetRow  import PM_WidgetRow
from PM.PM_ToolButton import PM_ToolButton
from PM.PM_ComboBox   import PM_ComboBox
from PM.PM_TextEdit   import PM_TextEdit
from PM.PM_LineEdit   import PM_LineEdit
from PM.PM_PushButton import PM_PushButton
from PM.PM_SpinBox    import PM_SpinBox
from PM.PM_SelectionListWidget import PM_SelectionListWidget
from PM.PM_DnaSearchResultTable import PM_DnaSearchResultTable

from utilities.icon_utilities import geticon, getpixmap
from utilities.prefs_constants import dnaSearchTypeLabelChoice_prefs_key
from widgets.prefs_widgets import connect_comboBox_with_pref

_superclass = PM_DockWidget
class SelectNodeByNameDockWidget(PM_DockWidget):
    """
    The Ui_DnaSequenceEditor class defines UI elements for the Sequence Editor
    object. The sequence editor is usually visible while in DNA edit mode.
    It is a DockWidget that is doced at the bottom of the MainWindow
    """
    _title         =  "Select Node by Name"
    _groupBoxCount = 0
    _lastGroupBox = None

    def __init__(self, win):
        """
        Constructor for the Ui_DnaSequenceEditor
        @param win: The parentWidget (MainWindow) for the sequence editor
        """

        self.win = win
        parentWidget = win

        _superclass.__init__(self, parentWidget, title = self._title)

        win.addDockWidget(Qt.BottomDockWidgetArea, self)
        self.setFixedHeight(120)
        ##self.setFixedWidth(90)
        self.connect_or_disconnect_signals(True)

        if not self.win.selectByNameAction.isChecked():
            self.close()

    def show(self):
        """
        Overrides superclass method.
        """
        _superclass.show(self)
        val = env.prefs[dnaSearchTypeLabelChoice_prefs_key]
        self.searchTypeComboBox_indexChanged(val)


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

        self._listWidget.connect_or_disconnect_signals(isConnect)

        change_connect( self.searchToolButton,
                      SIGNAL("clicked()"),
                      self.searchNodes)

        prefs_key = dnaSearchTypeLabelChoice_prefs_key
        connect_comboBox_with_pref(self.searchTypeComboBox,
                                   prefs_key )

        change_connect( self.searchTypeComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.searchTypeComboBox_indexChanged)

    def searchTypeComboBox_indexChanged(self, val):
        if val == 0:
            ##self._widgetRow1.show()
            ##self._widgetRow2.hide()
            self._widgetRow1.setEnabled(True)
            self._widgetRow2.setEnabled(False)
        else:
            ##self._widgetRow2.show()
            ##self._widgetRow1.hide()
            self._widgetRow2.setEnabled(True)
            self._widgetRow1.setEnabled(False)

    def searchNodes(self):
        """
        ONLY implemented for DnaStrand or DnaSegments.
        """

        assy = self.win.assy

        topnode = assy.part.topnode
        lst = []
        def func(node):
            if isinstance(node, assy.DnaStrandOrSegment):
                lst.append(node)

        topnode.apply2all(func)

        choice = env.prefs[dnaSearchTypeLabelChoice_prefs_key]

        if choice == 0:
            nodes = self._searchNodesByName(lst)
        elif choice == 1:
            nodes = self._searchNodesByNucleotides(lst)

        self._listWidget.insertItems(
                row = 0,
                items = nodes)

    def _searchNodesByNucleotides(self, nodeList):
        lst = nodeList
        min_val = self._nucleotidesSpinBox_1.value()
        max_val = self._nucleotidesSpinBox_2.value()
        if min_val > max_val:
            print "Lower value for number of nucleotides exceeds max search value"
            return ()

        def func2(node):
            n = node.getNumberOfNucleotides()

            return (n >= min_val and n <= max_val)

        return filter(lambda m:func2(m), lst)


    def _searchNodesByName(self, nodeList):
        nodeNameString = self.findLineEdit.text()
        nodeNameString = str(nodeNameString)

        lst = nodeList
        def func2(node):
            n = len(nodeNameString)
            if len(node.name)< n:
                return False

            nameString = str(node.name[:n])

            if  nameString.lower() == nodeNameString.lower():
                return True

            return False

        return filter(lambda m:func2(m), lst)




    def closeEvent(self, event):
        self.win.selectByNameAction.setChecked(False)
        _superclass.closeEvent(self, event)


    def _loadWidgets(self):
        """
        Overrides PM.PM_DockWidget._loadWidgets. Loads the widget in this
        dockwidget.
        """
        self._loadMenuWidgets()
        self._loadTableWidget()

    def _loadTableWidget(self):
        self._listWidget = PM_DnaSearchResultTable(self, self.win)

    def _loadMenuWidgets(self):
        """
        Load the various menu widgets (e.g. Open, save sequence options,
        Find and replace widgets etc.
        """
        #Note: Find and replace widgets might be moved to their own class.

        self.searchTypeComboBox  = \
            PM_ComboBox( self,
                         label         =  "Search options:",
                         choices       =  ["By node name", "By # of bases (DNA only)"],
                         setAsDefault  =  True)


        #Find  widgets --
        self._nucleotidesSpinBox_1 = PM_SpinBox(self,
                        label         =  "",
                        value         =  10,
                        setAsDefault  =  False,
                        singleStep = 10,
                        minimum       =  1,
                        maximum       =  50000)

        self._nucleotidesSpinBox_2 = PM_SpinBox(self,
                        label         =  "",
                        value         =  50,
                        setAsDefault  =  False,
                        singleStep = 10,
                        minimum       =  1,
                        maximum       =  50000)


        self.findLineEdit = \
            PM_LineEdit( self,
                         label        = "",
                         spanWidth    = False)

        self.findLineEdit.setMaximumWidth(80)

        self.findOptionsToolButton = PM_ToolButton(self)
        self.findOptionsToolButton.setMaximumWidth(12)
        self.findOptionsToolButton.setAutoRaise(True)

        ##self.findOptionsToolButton.setPopupMode(QToolButton.MenuButtonPopup)

        ##self._setFindOptionsToolButtonMenu()

        self.searchToolButton = PM_ToolButton(
            self,
            iconPath = "ui/actions/Properties Manager/Find_Next.png")
        self.searchToolButton.setAutoRaise(False)


        self.warningSign = QLabel(self)
        self.warningSign.setPixmap(
            getpixmap('ui/actions/Properties Manager/Warning.png'))
        self.warningSign.hide()

        self.phraseNotFoundLabel = QLabel(self)
        self.phraseNotFoundLabel.setText("Not Found")
        self.phraseNotFoundLabel.hide()

        # NOTE: Following needs cleanup in the PM_WidgetRow/ PM_WidgetGrid
        # but this explanation is sufficient  until thats done --

        # When the widget type starts with the word 'PM_' , the
        # PM_WidgetRow treats it as a well defined widget and thus doesn't try
        # to create a QWidget object (or its subclasses)
        # This is the reason why qLabels such as self.warningSign and
        # self.phraseNotFoundLabel  are defined as PM_Labels and not 'QLabels'
        # If they were defined as 'QLabel'(s) then PM_WidgetRow would have
        # recreated the label. Since we want to show/hide the above mentioned
        # labels (and if they were recreated as mentioned above),
        # we would have needed to define  those something like this:
        # self.phraseNotFoundLabel = widgetRow._widgetList[-2]
        #Cleanup in PM_widgetGrid could be to check if the widget starts with
        #'Q'  instead of 'PM_'


        #Widgets to include in the widget row.


        widgetList1 = [
                      ('QLabel', "     Search for name:", 1),
                      ('PM_LineEdit', self.findLineEdit, 2),
                      ('PM_ToolButton', self.findOptionsToolButton, 3),
                      ('PM_ToolButton', self.searchToolButton, 4),
                      ('PM_Label', self.warningSign, 5),
                      ('PM_Label', self.phraseNotFoundLabel, 6),
                      ('QSpacerItem', 5, 5, 7) ]

        widgetList2 = [
                      ('QLabel', "     Number of bases: >=", 1),
                      ('PM_SpinBox', self._nucleotidesSpinBox_1, 2),
                      ('QLabel', "     <=", 3),
                      ('PM_SpinBox', self._nucleotidesSpinBox_2, 4),
                      ('QSpacerItem', 5, 5, 5)]

        widgetList3 = [
                      ('QSpacerItem', 5, 5, 1),
                      ('PM_ToolButton', self.searchToolButton, 2),
                      ('PM_Label', self.warningSign, 3),
                      ('PM_Label', self.phraseNotFoundLabel, 4),
                      ('QSpacerItem', 5, 5, 5) ]


        self._widgetRow1 = PM_WidgetRow(self,
                                 title     = '',
                                 widgetList = widgetList1,
                                 label = "",
                                 spanWidth = True )

        self._widgetRow2 = PM_WidgetRow(self,
                                 title     = '',
                                 widgetList = widgetList2,
                                 label = "",
                                 spanWidth = True )

        self._widgetRow3 = PM_WidgetRow(self,
                                 title     = '',
                                 widgetList = widgetList3,
                                 label = "",
                                 spanWidth = True )


