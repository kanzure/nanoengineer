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

class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    """
    The Preferences dialog class.
    
    This is experimental.
    """
    pagenameList = []
    containerWidgetList = []
    
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
        Adds all pages to the Preferences dialog.
        """
        _pageWidget = self.addPage("General")
        _pageWidget = self.addPage("Color")
        _pageWidget = self.addPage("Graphics Area")
        _pageWidget = self.addPage("Zoom, Pan and Rotate")
        return
    
    def addPage(self, pagename):
        """
        Appends a new page to the bottom of the list.
        """
        return self.insertPage(pagename)
    
    def insertPage(self, pagename, index = -1):
        """
        Inserts page into this preferences dialog at position index.
        If index is negative, the page is added at the end. 
        
        param pagename: Page name.
        type  pagename: string
        param index: Page index
        type  index: int
        
        @note: This implem in temporary. Derrick and I like passing in a 
        page widget that gets added to the stacked widget. The page
        widget will contain the name attr needed in this method.
        """
        # 0. Check that the page widget's "name" is a unique name/string
        
        # 1. Create the page widget and add it to the stack widget.
        _page = QtGui.QWidget()
        _page.setObjectName(pagename)
        self.prefsStackedWidget.addWidget(_page)
        
        # 2. Add page widget and pagename to a list.
        
        # _widget is the container widget.
        _widget = QtGui.QFrame(_page)
        _widget.setObjectName(pagename)
        _widget.setFrameShape(QFrame.Box)
        
        # Set the size policy for the container widget. 
        # Note to Derrick: This is really important to get right early in the
        # project. --Mark
        #_widget.setMinimumSize(QtCore.QSize(100,100))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(_widget.sizePolicy().hasHeightForWidth())
        _widget.setSizePolicy(sizePolicy)
        
        if index < 0:
            self.pagenameList.append(pagename)
            self.containerWidgetList.append(_widget)
        else:
            self.pagenameList.insert(index, pagename)
            self.containerWidgetList.append(index, _page)
            
        # Label for debugging
        if 1:
            _label = QtGui.QLabel(_widget)
            _label.setText(pagename+" this is an extension to the label so that it will grow")

        
        if 1:
            # Horizontal spacer
            horizontalSpacer = QtGui.QSpacerItem(1, 1, 
                                    QSizePolicy.Preferred, 
                                    QSizePolicy.Minimum)
            
            self.hBoxLayout = QtGui.QHBoxLayout(_page)
            self.hBoxLayout.addWidget(_widget)
            self.hBoxLayout.addItem(horizontalSpacer)
        
        # 3. Add the QTreeWidgetItem
        _item = QtGui.QTreeWidgetItem(self.categoriesTreeWidget)
        _item.setText(0, 
                      QtGui.QApplication.translate("PreferencesDialog", 
                                                   pagename, 
                                                   None, 
                                                   QtGui.QApplication.UnicodeUTF8))
        
        return _widget
    
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