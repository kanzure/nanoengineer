# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
PreferencesDialog.py

This is experimental.

To run, type:

python PreferencesDialog.py
"""

import sys
from PyQt4.Qt import *
from PyQt4 import QtCore, QtGui
from Ui_PreferencesDialog import Ui_PreferencesDialog

DEBUG = True

class PageWidget(QWidget):
    """
    The page widget base class.
    """
    
    _rowCount = 0
    
    def __init__(self, name):
        """
        Creates a page widget named name.
        
        param name: The page name. It will be used as the tree item
        """
        QWidget.__init__(self)
        self.name = name
        self.setObjectName(name)
        
        # _containerWidget is the container widget.
        _containerWidget = QtGui.QFrame(self)
        _containerWidget.setObjectName(name)
        
        if DEBUG:
            _containerWidget.setFrameShape(QFrame.Box)
        
        # Create vertical box layout
        self.vBoxLayout = QVBoxLayout(_containerWidget)
        self.vBoxLayout.setMargin(0)
        self.vBoxLayout.setSpacing(0)
        
        # Create grid layout
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setMargin(2)
        self.gridLayout.setSpacing(2)
        
        # Insert grid layout in its own vBoxLayout
        self.vBoxLayout.addLayout(self.gridLayout)
        
        # Vertical spacer
        vSpacer = QtGui.QSpacerItem(1, 1, 
                                    QSizePolicy.Preferred, 
                                    QSizePolicy.Expanding)
        self.vBoxLayout.addItem(vSpacer)
        
        # Horizontal spacer
        hSpacer = QtGui.QSpacerItem(1, 1, 
                                    QSizePolicy.Expanding, 
                                    QSizePolicy.Preferred)
        
        self.hBoxLayout = QtGui.QHBoxLayout(self)
        self.hBoxLayout.setMargin(0)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.addWidget(_containerWidget)
        self.hBoxLayout.addItem(hSpacer)
            
        return
    
    def addQtWidget(self, qtWidget, column = 0, spanWidth = False):
        """
        Add a Qt widget to this page.
        
        @param qtWidget: The Qt widget to add.
        @type  qtWidget: QWidget
        """
        # Set the widget's row and column parameters.
        widgetRow      = self._rowCount
        widgetColumn   = column
        if spanWidth:
            widgetSpanCols = 2
        else:
            widgetSpanCols = 1
        
        self.gridLayout.addWidget( qtWidget,
                                   widgetRow, 
                                   widgetColumn,
                                   1, 
                                   widgetSpanCols )
        
        self._rowCount += 1
        return
    
    def addPmWidget(self):
        """
        This is a reminder to Derrick and Mark to review the PM_Group class
        and its addPmWidget() method, since we want to support PM widget 
        classes.
        """
        return
    
    pass # End of PageWidget class

class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    """
    The Preferences dialog class.
    
    This is experimental.
    """
    pagenameList = ["General", 
                    "Graphics Area", 
                    "Zoom, Pan and Rotate",
                    "Rules",
                    "Atoms",
                    "Bonds",
                    "DNA",
                    "Minor groove error indicator",
                    "Base orientation indicator",
                    "Adjust",
                    "Lighting",
                    "Plug-ins",
                    "Undo",
                    "Window",
                    "Reports",
                    "Tooltips"]
    
    def __init__(self):
        """
        Constructor for the prefs dialog.
        """
        QDialog.__init__(self)
        self.setupUi(self)
        self._setupDialog_TopLevelWidgets()
        self._addPages()
        return
        
    def _setupDialog_TopLevelWidgets(self):
        """
        Setup all the main dialog widgets and their signal-slot connection(s).
        """

        #self.setWindowIcon(geticon("ui/actions/Tools/Options.png"))

        # This connects the "itemSelectedChanged" signal generated when the
        # user selects an item in the "Category" QTreeWidget on the left
        # side of the Preferences dialog (inside the "Systems Option" tab)
        # to the slot for turning to the correct page in the QStackedWidget
        # on the right side.
        self.connect(self.categoriesTreeWidget, SIGNAL("itemSelectionChanged()"), self.showPage)

        # Connections for OK and What's This buttons at the bottom of the dialog.
        self.connect(self.okButton, SIGNAL("clicked()"), self.accept)
        self.connect(self.whatsThisToolButton, SIGNAL("clicked()"),QWhatsThis.enterWhatsThisMode)

        #self.whatsThisToolButton.setIcon(
        #    geticon("ui/actions/Properties Manager/WhatsThis.png"))
        #self.whatsThisToolButton.setIconSize(QSize(22, 22))
        self.whatsThisToolButton.setToolTip('Enter "What\'s This?" help mode')
        return
    
    def _addPages(self):
        """
        Creates all page widgets in pagenameList and add them 
        to the Preferences dialog.
        """
        for name in self.pagenameList:
            print name
            page_widget = PageWidget(name)
            self.addPage(page_widget)
            
            # Add test widgets for debugging
            if DEBUG:
                self._addPageTestWidgets(page_widget)
                
        return
    
    def _addPageTestWidgets(self, page_widget):
        """
        This creates a set of test widgets for page_widget.
        """
        _label = QtGui.QLabel(page_widget)
        _label.setText(page_widget.name)
        page_widget.addQtWidget(_label)
        _checkbox = QtGui.QCheckBox(page_widget.name, page_widget)
        page_widget.addQtWidget(_checkbox)
        _pushbutton = QtGui.QPushButton(page_widget.name, page_widget)
        page_widget.addQtWidget(_pushbutton)
        _label = QtGui.QLabel(page_widget)
        return
    
    def addPage(self, page):
        """
        Adds page into this preferences dialog at position index.
        If index is negative, the page is added at the end. 
        
        param page: Page widget.
        type  page: L{PageWidget}
        """
        
        # Add page to the stacked widget
        self.prefsStackedWidget.addWidget(page)
        
        # Add a QTreeWidgetItem to the categories QTreeWidget.
        # The label (text) of the item is the page name.
        _item = QtGui.QTreeWidgetItem(self.categoriesTreeWidget)
        _item.setText(0, 
                      QtGui.QApplication.translate("PreferencesDialog", 
                                                   page.name, 
                                                   None, 
                                                   QtGui.QApplication.UnicodeUTF8))
        
        return
    
    def getPage(self, pagename):
        """
        Returns the container widget for pagename.
        """
        return
    
    def showPage(self, pagename = ""):
        """
        Show the current page of the Preferences dialog. If no page is
        selected from the Category tree widget, show the "General" page.

        @param pagename: Name of the Preferences page. Default is "General".
                         Only names found in self.pagenameList are allowed.
        @type  pagename: string

        @note: This is the slot method for the "Categories" QTreeWidget.
        """

        if not pagename:
            selectedItemsList = self.categoriesTreeWidget.selectedItems()
            if selectedItemsList:
                selectedItem = selectedItemsList[0]
                pagename = str(selectedItem.text(0))
            else:
                pagename = 'General'

        if not pagename in self.pagenameList:
            msg = 'Preferences page unknown: pagename =%s\n' \
                'pagename must be one of the following:\n%r\n' \
                % (pagename, self.pagenameList)
            print_compact_traceback(msg)
            
        try:
            # Show page.
            self.prefsStackedWidget.setCurrentIndex(self.pagenameList.index(pagename))
        except:
            print_compact_traceback("Bug in showPage() ignored.")

        self.setWindowTitle("Preferences - %s" % pagename)
        return
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    pd = PreferencesDialog()
    pd.show()
    sys.exit(app.exec_())