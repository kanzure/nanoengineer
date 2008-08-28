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

# imports for testing
from PM_ComboBox import PM_ComboBox
from PM_ColorComboBox import PM_ColorComboBox

if 0: # This will be used later
    from PM.PM_Constants import PM_MAINVBOXLAYOUT_MARGIN
    from PM.PM_Constants import PM_MAINVBOXLAYOUT_SPACING
    from PM.PM_Constants import PM_HEADER_FRAME_MARGIN
    from PM.PM_Constants import PM_HEADER_FRAME_SPACING
    from PM.PM_Constants import PM_HEADER_FONT
    from PM.PM_Constants import PM_HEADER_FONT_POINT_SIZE
    from PM.PM_Constants import PM_HEADER_FONT_BOLD
    from PM.PM_Constants import PM_SPONSOR_FRAME_MARGIN
    from PM.PM_Constants import PM_SPONSOR_FRAME_SPACING
    from PM.PM_Constants import PM_TOPROWBUTTONS_MARGIN
    from PM.PM_Constants import PM_TOPROWBUTTONS_SPACING
    from PM.PM_Constants import PM_LABEL_LEFT_ALIGNMENT, PM_LABEL_RIGHT_ALIGNMENT
    
    from PM.PM_Constants import PM_ALL_BUTTONS
    from PM.PM_Constants import PM_DONE_BUTTON
    from PM.PM_Constants import PM_CANCEL_BUTTON
    from PM.PM_Constants import PM_RESTORE_DEFAULTS_BUTTON
    from PM.PM_Constants import PM_PREVIEW_BUTTON
    from PM.PM_Constants import PM_WHATS_THIS_BUTTON

if 1: # This is for building
    from PM_Constants import PM_MAINVBOXLAYOUT_MARGIN
    from PM_Constants import PM_MAINVBOXLAYOUT_SPACING
    from PM_Constants import PM_HEADER_FRAME_MARGIN
    from PM_Constants import PM_HEADER_FRAME_SPACING
    from PM_Constants import PM_HEADER_FONT
    from PM_Constants import PM_HEADER_FONT_POINT_SIZE
    from PM_Constants import PM_HEADER_FONT_BOLD
    from PM_Constants import PM_SPONSOR_FRAME_MARGIN
    from PM_Constants import PM_SPONSOR_FRAME_SPACING
    from PM_Constants import PM_TOPROWBUTTONS_MARGIN
    from PM_Constants import PM_TOPROWBUTTONS_SPACING
    from PM_Constants import PM_LABEL_LEFT_ALIGNMENT, PM_LABEL_RIGHT_ALIGNMENT
    
    from PM_Constants import PM_ALL_BUTTONS
    from PM_Constants import PM_DONE_BUTTON
    from PM_Constants import PM_CANCEL_BUTTON
    from PM_Constants import PM_RESTORE_DEFAULTS_BUTTON
    from PM_Constants import PM_PREVIEW_BUTTON
    from PM_Constants import PM_WHATS_THIS_BUTTON

DEBUG = True

class PageWidget(QWidget):
    """
    The page widget base class.
    """

    _rowCount = 0
    _widgetList = []

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
    
    def getPmWidgetPlacementParameters(self, pmWidget):
        """
        Returns all the layout parameters needed to place 
        a PM_Widget in the group box grid layout.
        
        @param pmWidget: The PM widget.
        @type  pmWidget: PM_Widget
        """
        
        row = self._rowCount
        
        #PM_CheckBox doesn't have a label. So do the following to decide the 
        #placement of the checkbox. (can be placed either in column 0 or 1 , 
        #This also needs to be implemented for PM_RadioButton, but at present 
        #the following code doesn't support PM_RadioButton. 
        #if isinstance(pmWidget, PM_CheckBox):
            #spanWidth = pmWidget.spanWidth
            
            #if not spanWidth:
                ## Set the widget's row and column parameters.
                #widgetRow      = row
                #widgetColumn   = pmWidget.widgetColumn
                #widgetSpanCols = 1
                #widgetAlignment = PM_LABEL_LEFT_ALIGNMENT
                #rowIncrement   = 1
                ##set a virtual label
                #labelRow       = row
                #labelSpanCols  = 1
                #labelAlignment = PM_LABEL_RIGHT_ALIGNMENT
                            
                #if widgetColumn == 0:
                    #labelColumn   = 1                              
                #elif widgetColumn == 1:
                    #labelColumn   = 0
            #else:                
                ## Set the widget's row and column parameters.
                #widgetRow      = row
                #widgetColumn   = pmWidget.widgetColumn
                #widgetSpanCols = 2
                #widgetAlignment = PM_LABEL_LEFT_ALIGNMENT
                #rowIncrement   = 1
                ##no label 
                #labelRow       = 0
                #labelColumn    = 0
                #labelSpanCols  = 0
                #labelAlignment = PM_LABEL_RIGHT_ALIGNMENT
                
            
            #return widgetRow, \
               #widgetColumn, \
               #widgetSpanCols, \
               #widgetAlignment, \
               #rowIncrement, \
               #labelRow, \
               #labelColumn, \
               #labelSpanCols, \
               #labelAlignment
        
       
        label       = pmWidget.label            
        labelColumn = pmWidget.labelColumn
        spanWidth   = pmWidget.spanWidth
        
        if not spanWidth: 
            # This widget and its label are on the same row
            labelRow       = row
            labelSpanCols  = 1
            labelAlignment = PM_LABEL_RIGHT_ALIGNMENT
            # Set the widget's row and column parameters.
            widgetRow      = row
            widgetColumn   = 1
            widgetSpanCols = 1
            widgetAlignment = PM_LABEL_LEFT_ALIGNMENT
            rowIncrement   = 1
            
            if labelColumn == 1:
                widgetColumn   = 0
                labelAlignment = PM_LABEL_LEFT_ALIGNMENT
                widgetAlignment = PM_LABEL_RIGHT_ALIGNMENT
                        
        else: 
                      
            # This widget spans the full width of the groupbox           
            if label: 
                # The label and widget are on separate rows.
                # Set the label's row, column and alignment.
                labelRow       = row
                labelColumn    = 0
                labelSpanCols  = 2
                    
                # Set this widget's row and column parameters.
                widgetRow      = row + 1 # Widget is below the label.
                widgetColumn   = 0
                widgetSpanCols = 2
                
                rowIncrement   = 2
            else:  # No label. Just the widget.
                labelRow       = 0
                labelColumn    = 0
                labelSpanCols  = 0

                # Set the widget's row and column parameters.
                widgetRow      = row
                widgetColumn   = 0
                widgetSpanCols = 2
                rowIncrement   = 1
                
            labelAlignment = PM_LABEL_LEFT_ALIGNMENT
            widgetAlignment = PM_LABEL_LEFT_ALIGNMENT
                
        return widgetRow, \
               widgetColumn, \
               widgetSpanCols, \
               widgetAlignment, \
               rowIncrement, \
               labelRow, \
               labelColumn, \
               labelSpanCols, \
               labelAlignment

    def addPmWidget(self, pmWidget):
        """
        This is a reminder to Derrick and Mark to review the PM_Group class
        and its addPmWidget() method, since we want to support PM widget 
        classes.
        """
        """
        Add a PM widget and its label to this group box.

        @param pmWidget: The PM widget to add.
        @type  pmWidget: PM_Widget
        """

        # Get all the widget and label layout parameters.
        widgetRow, \
                 widgetColumn, \
                 widgetSpanCols, \
                 widgetAlignment, \
                 rowIncrement, \
                 labelRow, \
                 labelColumn, \
                 labelSpanCols, \
                 labelAlignment = \
                 self.getPmWidgetPlacementParameters(pmWidget)

        if pmWidget.labelWidget: 
            #Create Label as a pixmap (instead of text) if a valid icon path 
            #is provided
            labelPath = str(pmWidget.label)
            if labelPath and labelPath.startswith("ui/"): #bruce 080325 revised
                labelPixmap = getpixmap(labelPath)
                if not labelPixmap.isNull():
                    pmWidget.labelWidget.setPixmap(labelPixmap)
                    pmWidget.labelWidget.setText('')

            self.gridLayout.addWidget( pmWidget.labelWidget,
                                       labelRow, 
                                       labelColumn,
                                       1, 
                                       labelSpanCols,
                                       labelAlignment )


        # The following is a workaround for a Qt bug. If addWidth()'s 
        # <alignment> argument is not supplied, the widget spans the full 
        # column width of the grid cell containing it. If <alignment> 
        # is supplied, this desired behavior is lost and there is no 
        # value that can be supplied to maintain the behavior (0 doesn't 
        # work). The workaround is to call addWidget() without the <alignment>
        # argument. Mark 2007-07-27.

        if widgetAlignment == PM_LABEL_LEFT_ALIGNMENT:
            self.gridLayout.addWidget( pmWidget,
                                       widgetRow, 
                                       widgetColumn,
                                       1, 
                                       widgetSpanCols) 
                                        # aligment = 0 doesn't work.
        else:
            self.gridLayout.addWidget( pmWidget,
                                       widgetRow, 
                                       widgetColumn,
                                       1, 
                                       widgetSpanCols,
                                       widgetAlignment
                                       )

        self._widgetList.append(pmWidget)

        self._rowCount += rowIncrement
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
        _choices = ['a', 'b' ]
        _pref_ComboBox = PM_ComboBox( page_widget, label =  "choices:", 
                                      choices = _choices, setAsDefault = True)
        _prec_color = PM_ColorComboBox(page_widget)
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