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
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_ColorComboBox import PM_ColorComboBox
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_CoordinateSpinBoxes import PM_CoordinateSpinBoxes
from PM.PM_LineEdit      import PM_LineEdit
from PM.PM_PushButton import PM_PushButton
from PM.PM_RadioButton import PM_RadioButton
from PM.PM_RadioButtonList import PM_RadioButtonList
from PM.PM_Slider import PM_Slider
from PM.PM_TableWidget import PM_TableWidget
from PM.PM_TextEdit import PM_TextEdit
from PM.PM_ToolButton import PM_ToolButton
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_Dial import PM_Dial
from PM.PM_SpinBox import PM_SpinBox

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
        self.containerList = []

        # _containerWidget is the container widget.
        _containerWidget = QtGui.QFrame(self)
        _containerWidget.setObjectName(name)
        # This next line fills the list with improper data.  But, later when a
        # container class is built, this will store the object where the 
        # getPageContainers method can get to it.  One container will be 
        # created with each page, and the programmer can ask for more by calling
        # self.newContainer (not yet implemented).
        self.containerList.append(_containerWidget)

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
    
    def getPageContainers(self, containerKey = None):
        """
        Returns a list of containers which the page owns.
        Always returns a list for consistancy.  The list can be restricted to
        only those that have containerKey in the name.  If there's only one, the 
        programmer can do list = list[0]
        """

        # See if we are asking for a specific container
        if containerKey == None:
            # return the whole list
            containers = self.containerList
        else:
            # return only the container(s) where containerKey is in the name.
            # this is a list comprehension search.
            # Also, the condition can be modified with a startswith depending
            # on the implementation of naming the containers.
            containers = [ x for x in self.containerList \
                           if x.objectName().find(containerKey) >= 0 ]
        return containers

    
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
        if isinstance(pmWidget, PM_CheckBox):
            spanWidth = pmWidget.spanWidth
            
            if not spanWidth:
                # Set the widget's row and column parameters.
                widgetRow      = row
                widgetColumn   = pmWidget.widgetColumn
                widgetSpanCols = 1
                widgetAlignment = PM_LABEL_LEFT_ALIGNMENT
                rowIncrement   = 1
                #set a virtual label
                labelRow       = row
                labelSpanCols  = 1
                labelAlignment = PM_LABEL_RIGHT_ALIGNMENT
                            
                if widgetColumn == 0:
                    labelColumn   = 1                              
                elif widgetColumn == 1:
                    labelColumn   = 0
            else:                
                # Set the widget's row and column parameters.
                widgetRow      = row
                widgetColumn   = pmWidget.widgetColumn
                widgetSpanCols = 2
                widgetAlignment = PM_LABEL_LEFT_ALIGNMENT
                rowIncrement   = 1
                #no label 
                labelRow       = 0
                labelColumn    = 0
                labelSpanCols  = 0
                labelAlignment = PM_LABEL_RIGHT_ALIGNMENT
                
            
            return widgetRow, \
               widgetColumn, \
               widgetSpanCols, \
               widgetAlignment, \
               rowIncrement, \
               labelRow, \
               labelColumn, \
               labelSpanCols, \
               labelAlignment
        
       
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
    
    pagenameList[0] always has to be a singular item, it cannot be a list.
    All sub-lists are interpreted as being children of the item preceding it.
    """
    pagenameList = ["General", 
                    "Graphics Area", 
                    ["Zoom, Pan and Rotate", "Rules"],
                    "Atoms",
                    "Bonds",
                    "DNA",
                    ["Minor groove error indicator", 
                     "Base orientation indicator"],
                    "Adjust",
                    "Lighting",
                    "Plug-ins",
                    "Undo",
                    "Window",
                    "Reports",
                    "Tooltips"]
    
    pagenameDict = {}

    def __init__(self):
        """
        Constructor for the prefs dialog.
        """
        QDialog.__init__(self)
        self.setupUi(self)
        self._setupDialog_TopLevelWidgets()
        self._addPages(self.pagenameList)
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

    #def addScrollArea(self):
        #self.propertyManagerScrollArea = QScrollArea(self.categoriesTreeWidget)
        #self.propertyManagerScrollArea.setObjectName("propertyManagerScrollArea")
        #self.propertyManagerScrollArea.setWidget(self.categoriesTreeWidget)
        #self.propertyManagerScrollArea.setWidgetResizable(True)
    
    def _addPages(self, pagenameList, myparent = None):
        """
        Creates all page widgets in pagenameList and add them 
        to the Preferences dialog.
        """

        if (type(pagenameList[0]) == list or \
            type(pagenameList[0]) == tuple):
            print "Invalid tree structure with no root page."
            return
        # Run through the list and add the pages into the tree.
        # This is recursive so that it interpretes nested sublists based on
        # the structure of the list.
        x=-1
        while x < len(pagenameList) - 1:
            x = x + 1
            name = pagenameList[x]
            print name
            page_widget = PageWidget(name)
            # Create a dictionary entry for the page name and it's index
            self.pagenameDict[name] = len(self.pagenameDict)
            page_tree_slot = self.addPage(page_widget, myparent)
            # Check if the next level is a sub-list
            if x + 1 <= len(pagenameList) - 1 and \
               (type(pagenameList[x+1]) == list or \
               type(pagenameList[x+1]) == tuple):
                # If so, call addPages again using the sublist and the current
                # item as the parent
                self._addPages(pagenameList[x+1], page_tree_slot)
                x = x + 1

            # Add test widgets for debugging
            if DEBUG:
                self._addPageTestWidgets(page_widget)

        return

    def addPage(self, page, myparent = None):
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
        if not myparent:
            _item = QtGui.QTreeWidgetItem(self.categoriesTreeWidget)
        else:
            _item = QtGui.QTreeWidgetItem(myparent)
        _item.setText(0, 
                      QtGui.QApplication.translate("PreferencesDialog", 
                                                   page.name, 
                                                   None, 
                                                   QtGui.QApplication.UnicodeUTF8))

        return _item

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
        _choices = ['choice a', 'choice b' ]
        _pref_ComboBox = PM_ComboBox( page_widget, label =  "choices:", 
                                      choices = _choices, setAsDefault = True)
        _pref_color = PM_ColorComboBox(page_widget, spanWidth = True)
        _pref_CheckBox = PM_CheckBox(page_widget, text ="nothing interesting", \
                                     widgetColumn = 1)
        #N means this PM widget currently does not work.
#N        _pmGroupBox1 = PM_GroupBox( self, title = "Endpoints" )
#N        _endPoint1SpinBoxes = PM_CoordinateSpinBoxes(self._pmGroupBox1,
#                                                          label = "test 1")
        duplexLengthLineEdit  =  \
            PM_LineEdit(page_widget, label =  "something\non the next line",
                         text          =  "default text",
                         setAsDefault  =  False)
        pushbtn = PM_PushButton(page_widget, label = "Click here",
                                 text = "here")
        radio1 = PM_RadioButton(page_widget, text = "self button1")
        radio2 = PM_RadioButton(page_widget, text = "self button2")
#N        radiobtns = PM_RadioButtonList (page_widget, title = "junk", 
#                                        label = "junk2", 
#                                        buttonList = ["btn1", "btn2"])
        slider1 = PM_Slider(page_widget, label = "slider 1:")
        table1 = PM_TableWidget(page_widget, label = "table:")
        TE1 = PM_TextEdit(page_widget, label = "QMX")
#N        TB1 = PM_ToolButton(page_widget, label = "tb1", text = "text1")
        radio3 = PM_RadioButton(page_widget, text = "self button3")
        SB = PM_SpinBox(page_widget, label = "SB", suffix = "x2")
        DBS = PM_DoubleSpinBox(page_widget, label = "test", suffix = "x3", singleStep = .1)
        Dial = PM_Dial( page_widget, label = "Direction", suffix = "degrees")

        return
        
    def getPage(self, pagename):
        """
        Returns the page widget for pagename.
        """
        if not pagename in self.pagenameDict:
            msg = 'Preferences page unknown: pagename =%s\n' \
                'pagename must be one of the following:\n%r\n' \
                % (pagename, self.pagenameList)
            print_compact_traceback(msg)
            return
        return self.prefsStackedWidget.widget(self.pagenameDict[pagename])
    
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

        if not pagename in self.pagenameDict:
            msg = 'Preferences page unknown: pagename =%s\n' \
                'pagename must be one of the following:\n%r\n' \
                % (pagename, self.pagenameList)
            print_compact_traceback(msg)

        try:
            # Show page.  Use the dictionary to get the index.
            self.prefsStackedWidget.setCurrentIndex(self.pagenameDict[pagename])
        except:
            print_compact_traceback("Bug in showPage() ignored.")

        self.setWindowTitle("Preferences - %s" % pagename)
        containers = self.getPage(pagename).getPageContainers()
        print containers
        return

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    pd = PreferencesDialog()
    pd.show()
    sys.exit(app.exec_())