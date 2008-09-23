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
from PM.PM_ComboBox              import PM_ComboBox
from PM.PM_ColorComboBox         import PM_ColorComboBox
from PM.PM_CheckBox              import PM_CheckBox
from PM.PM_GroupBox              import PM_GroupBox
from PM.PM_CoordinateSpinBoxes   import PM_CoordinateSpinBoxes
from PM.PM_LineEdit              import PM_LineEdit
from PM.PM_PushButton            import PM_PushButton
from PM.PM_RadioButton           import PM_RadioButton
from PM.PM_RadioButtonList       import PM_RadioButtonList
from PM.PM_Slider                import PM_Slider
from PM.PM_TableWidget           import PM_TableWidget
from PM.PM_TextEdit              import PM_TextEdit
from PM.PM_ToolButton            import PM_ToolButton
from PM.PM_DoubleSpinBox         import PM_DoubleSpinBox
from PM.PM_Dial                  import PM_Dial
from PM.PM_SpinBox               import PM_SpinBox
from PM.PM_FileChooser           import PM_FileChooser
from PM.PM_WidgetRow             import PM_WidgetRow
from PM.PM_DockWidget            import PM_DockWidget
from PM.PM_PushButton            import PM_PushButton
from PM.PM_LabelRow              import PM_LabelRow
from PM.PM_FontComboBox          import PM_FontComboBox
from PM.PM_WidgetGrid            import PM_WidgetGrid

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
from utilities.icon_utilities import geticon

DEBUG = True

class ContainerWidget(QFrame):
    """
    The container widget class for use in PageWidget.
    """

    _rowCount = 0
    _widgetList = []
    _groupBoxCount = 0
    _lastGroupBox = None
    
    def __init__(self, name):
        """
        Creates a container widget within the page widget
        """
        QFrame.__init__(self)
        self.name = name
        self.setObjectName(name)
        if DEBUG:
            self.setFrameShape(QFrame.Box)

        # Create vertical box layout
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setMargin(0)
        self.vBoxLayout.setSpacing(0)

        # Create grid layout
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setMargin(2)
        self.gridLayout.setSpacing(2)

        # Insert grid layout in its own vBoxLayout
        self.vBoxLayout.addLayout(self.gridLayout)

        # Vertical spacer
        #vSpacer = QtGui.QSpacerItem(1, 1, 
                                    #QSizePolicy.Preferred, 
                                    #QSizePolicy.Expanding)
        #self.vBoxLayout.addItem(vSpacer)
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

# End of ContainerWidget class

    
class PageWidget(QWidget):
    """
    The page widget base class.
    """

    def __init__(self, name):
        """
        Creates a page widget named name.

        param name: The page name. It will be used as the tree item
        """
        QWidget.__init__(self)
        self.name = name
        self.setObjectName(name)
        self.containerList = []

        # Horizontal spacer
        hSpacer = QtGui.QSpacerItem(1, 1, 
                                    QSizePolicy.Expanding, 
                                    QSizePolicy.Preferred)

        self.hBoxLayout = QtGui.QHBoxLayout(self)
        self.hBoxLayout.setMargin(0)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.addItem(hSpacer)
        # add the base container widget
        container = self.addContainer(name + "_1")
#        print container
#        scrollArea = QScrollArea()
#        scrollArea.setWidget(container)
#        container.scrollarea = scrollArea

        return

    def insertContainer(self, containerName = None, indx = -1):
        """
        inserts a container class named containerName in the place specified 
        by indx
        """
        # set indx to append to the end of the list if indx is not passed
        if indx < 0:
            indx = len(self.containerList)
        # create some theoretically unique name if None is given
        if containerName == None:
            containerName = self.name + "_" + str((len(self.containerList) + 1))
        # create the container and name it
        _containerWidget = ContainerWidget(containerName)
        _containerWidget.setObjectName(containerName)
        # add the container into the page
        self.containerList.insert(indx, _containerWidget)
        self.hBoxLayout.insertWidget(indx,_containerWidget)
        return _containerWidget
    
    def addContainer(self, containerName = None):
        """
        Adds a container to the end of the list and returns the 
        container's handle
        """
        _groupBoxCount = 0
        _containerWidget = self.insertContainer(containerName)
        return _containerWidget
            
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

# End of PageWidget class

class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    """
    The Preferences dialog class.

    This is experimental.
    
    pagenameList[0] always has to be a singular item, it cannot be a list.
    All sub-lists are interpreted as being children of the item preceding it.
    """
    #pagenameList = ["General", 
                    #"Graphics Area", 
                    #["Zoom, Pan and Rotate", "Rulers"],
                    #"Atoms",
                    #"Bonds",
                    #"DNA",
                    #["Minor groove error indicator", 
                     #"Base orientation indicator"],
                    #"Adjust",
                    #"Lighting",
                    #"Plug-ins",
                    #"Undo",
                    #"Window",
                    #"Reports",
                    #"Tooltips"]
    
    #NOTE: when creating the function names for populating the pages with 
    # widgets...  Create the function name by replacing all spaces with 
    # underscores and removing all characters that are not ascii 
    # letters or numbers, and appending the result to "populate_"
    # ex. "Zoom, Pan and Rotate" has the function:
    #     populate_Zoom_Pan_and_Rotate()
    
    pagenameDict = {}

    def __init__(self):
        """
        Constructor for the prefs dialog.
        """
        self.pagenameList = ["General", 
                    "Graphics Area", 
                    ["Zoom, Pan and Rotate", "Rulers"],
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
        QDialog.__init__(self)
        self.setupUi()
        self._setupDialog_TopLevelWidgets()
        self._addPages(self.pagenameList)
        self.populatePages()
        return

    def setupUi(self):
        self.setObjectName("PreferencesDialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,594,574).size()).expandedTo(self.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(self)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setMargin(2)
        self.vboxlayout.setObjectName("vboxlayout")

        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

#        self.hboxlayout = QtGui.QHBoxLayout(self.tab)
        self.pref_splitter = QtGui.QSplitter(self.tab)
#        self.hboxlayout.setSpacing(4)
#        self.hboxlayout.setMargin(2)
#        self.hboxlayout.setObjectName("hboxlayout")
        self.pref_splitter.setObjectName("pref_splitter")

        self.categoriesTreeWidget = QtGui.QTreeWidget(self.pref_splitter)
        self.categoriesTreeWidget.setMinimumWidth(100)
#        self.categoriesTreeWidget.setMaximumWidth(250)
        self.categoriesTreeWidget.setObjectName("categoriesTreeWidget")
#        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
#        sizePolicy.setHorizontalStretch(0)
#        sizePolicy.setVerticalStretch(0)
#        self.categoriesTreeWidget.setSizePolicy(sizePolicy)
#        self.hboxlayout.addWidget(self.categoriesTreeWidget)
        self.pref_splitter.addWidget(self.categoriesTreeWidget)

        self.prefsStackedWidget = QtGui.QStackedWidget(self.pref_splitter)
#        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
#        self.prefsStackedWidget.setSizePolicy(sizePolicy)
        self.prefsStackedWidget.setObjectName("prefsStackedWidget")

#        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
#        self.pref_splitter.setSizePolicy(sizePolicy)

        self.pref_splitter.addWidget(self.prefsStackedWidget)
        self.tabWidget.addTab(self.tab,"")
        self.vboxlayout.addWidget(self.tabWidget)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.whatsThisToolButton = QtGui.QToolButton(self)
        self.whatsThisToolButton.setObjectName("whatsThisToolButton")
        self.hboxlayout1.addWidget(self.whatsThisToolButton)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)

        self.okButton = QtGui.QPushButton(self)
        self.okButton.setObjectName("okButton")
        self.hboxlayout1.addWidget(self.okButton)
        self.vboxlayout.addLayout(self.hboxlayout1)

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        self.prefsStackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("PreferencesDialog", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.categoriesTreeWidget.headerItem().setText(0,QtGui.QApplication.translate("PreferencesDialog", "Categories", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("PreferencesDialog", "System Options", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("PreferencesDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))

    def _setupDialog_TopLevelWidgets(self):
        """
        Setup all the main dialog widgets and their signal-slot connection(s).
        """
#        self.setWindowIcon(geticon("ui/actions/Tools/Options.png"))

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
            if DEBUG:
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
        _pmGroupBox1 = PM_GroupBox( page_widget, title = "Test of GB",
                                    connectTitleButton = False)
#N        _endPoint1SpinBoxes = PM_CoordinateSpinBoxes(_pmGroupBox1)
#        duplexLengthLineEdit  =  \
#            PM_LineEdit(page_widget, label =  "something\non the next line",
#                         text          =  "default text",
#                         setAsDefault  =  False)
        pushbtn = PM_PushButton(page_widget, label = "Click here",
                                 text = "here")
        radio1 = PM_RadioButton(page_widget, text = "self button1")
        radio2 = PM_RadioButton(page_widget, text = "self button2")
        radiobtns = PM_RadioButtonList (_pmGroupBox1, title = "junk", 
                                        label = "junk2", 
                                        buttonList = [[ 1, "btn1", "btn1"],
                                                      [ 2, "btn2", "btn2"]])
        slider1 = PM_Slider(page_widget, label = "slider 1:")
#        table1 = PM_TableWidget(page_widget, label = "table:")
#        TE1 = PM_TextEdit(page_widget, label = "QMX")
#N        TB1 = PM_ToolButton(_pmGroupBox1, label = "tb1", text = "text1")
        radio3 = PM_RadioButton(page_widget, text = "self button3")
#        SB = PM_SpinBox(page_widget, label = "SB", suffix = "x2")
#        DBS = PM_DoubleSpinBox(page_widget, label = "test", suffix = "x3", singleStep = .1)
#        Dial = PM_Dial( page_widget, label = "Direction", suffix = "degrees")

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
    
    def populatePages(self):
        import string
        for name in self.pagenameDict:
            # create the function name by replacing spaces with "_" and 
            # removing everything that is not an _, ascii letter, or number
            # and appending that to populate_
            fname = "populate_%s" % "".join([ x for x in name.replace(" ","_") \
                                              if (x in string.ascii_letters or\
                                                  x in string.digits \
                                                  or x == "_") ])
            # Make sure the class has that object defined before calling it.
            if hasattr(self, fname):
                fcall = getattr(self, fname)
                if callable(fcall):
                    if DEBUG:
                        print "method defined: %s" % fname
                    fcall(name)
                else:
                    print "Attribute %s exists, but is not a callable method."
            else:
                if DEBUG:
                    print "method missing: %s" % fname
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
        #containers = self.getPage(pagename).getPageContainers()
        #print containers
        return

    def populate_General(self, pagename):
        """
        Populate the General page
        """
        print "populate_General: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        logosGroupBox = PM_GroupBox( _pageContainer, 
                                     title = "Sponsor logos download permission",
                                     connectTitleButton = False)
        self.logo_download_RadioButtonList = \
            PM_RadioButtonList (logosGroupBox,
                                buttonList = [[ 0, 
                                                "Always ask before downloading", 
                                                ""],
                                              [ 1, 
                                                "Never ask before downloading", 
                                                ""],
                                              [ 2, 
                                                "Never download", 
                                                ""] ])
        
        buildChunksGroupBox = PM_GroupBox( _pageContainer, 
                                     title = "Build Chunks Settings",
                                     connectTitleButton = False)
        self.autobondCheckBox = PM_CheckBox(buildChunksGroupBox, text ="Autobond")
        self.hoverHighlightCheckBox = PM_CheckBox(buildChunksGroupBox, text ="Hover highlighting")
        self.waterCheckBox = PM_CheckBox(buildChunksGroupBox, text ="Water")
        self.autoSelectAtomsCheckBox = PM_CheckBox(buildChunksGroupBox, text ="Auto select atoms of deposited objects")

        offsetFactorPastingGroupBox = PM_GroupBox( _pageContainer, 
                                     title = "Offset factor for pasting objects",
                                     connectTitleButton = False)
        self.pasteOffsetForChunks_doublespinbox = PM_DoubleSpinBox(offsetFactorPastingGroupBox, label = "Chunk Objects", singleStep = 1)
        self.pasteOffsetForDNA_doublespinbox = PM_DoubleSpinBox(offsetFactorPastingGroupBox, label = "DNA Objects", singleStep = 1)
      
        return

    def populate_Tooltips(self, pagename):
        print "populate_Tooltips: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        atom_tooltip_options_GroupBox = PM_GroupBox(_pageContainer,
                                                    title = "Atom tooltip options",
                                                    connectTitleButton = False)
        self.atom_chunk_information_CheckBox = PM_CheckBox(atom_tooltip_options_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Chunk Information")
        self.atom_mass_information_CheckBox = PM_CheckBox(atom_tooltip_options_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Mass information")
        self.atom_XYZ_coordinates_CheckBox = PM_CheckBox(atom_tooltip_options_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="XYZ coordinates")
        self.atom_XYZ_distance_CheckBox = PM_CheckBox(atom_tooltip_options_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="XYZ distance deltas")
        self.atom_include_vdw_CheckBox = PM_CheckBox(atom_tooltip_options_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="include Vdw radii in atom distance tooltip")
        self.atom_distance_precision_SpinBox = PM_SpinBox(atom_tooltip_options_GroupBox,
                                                         label = "Distance precision: ", 
                                                         suffix = " decimal places", 
                                                         singleStep = 1)
        self.atom_angle_precision_SpinBox = PM_SpinBox(atom_tooltip_options_GroupBox,
                                                         label = "Angle precision:", 
                                                         suffix = " decimal places", 
                                                         singleStep = 1)
        bond_tooltip_options_GroupBox = PM_GroupBox(_pageContainer,
                                                    title = "Bond tooltip options",
                                                    connectTitleButton = False)
        self.bond_distance_between_atoms_CheckBox = PM_CheckBox(bond_tooltip_options_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Bond distance between atoms")
        self.bond_chunk_information_CheckBox = PM_CheckBox(bond_tooltip_options_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Chunk information")
        return
    
    def populate_Reports(self, pagename):
        print "populate_Reports: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        history_preferences = PM_GroupBox(_pageContainer,
                                          title = "History preferences",
                                          connectTitleButton = False)
        self.history_include_message_serial_CheckBox = PM_CheckBox(history_preferences,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Include message serial number")
        self.history_include_message_timestamp_CheckBox = PM_CheckBox(history_preferences,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Include message timestamp")                                                              
        return
    
    def populate_DNA(self, pagename):
        print "populate_DNA: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        DNA_default_values_GroupBox = PM_GroupBox(_pageContainer,
                                                  title = "DNA default values",
                                                  connectTitleButton = False)
        _choices = ["B-DNA"]
        self.conformation_ComboBox = PM_ComboBox(DNA_default_values_GroupBox, 
                                      label =  "Conformation:", labelColumn = 0,
                                      choices = _choices, 
                                      setAsDefault = False)
        self.bases_per_turn_DoubleSpinBox = PM_DoubleSpinBox(DNA_default_values_GroupBox,
                                                         label = "Bases per turn:", 
                                                         suffix = "", 
                                                         singleStep = 1)
        self.rise_DoubleSpinBox = PM_DoubleSpinBox(DNA_default_values_GroupBox,
                                                         label = "Rise:", 
                                                         suffix = "Angstroms", 
                                                         singleStep = 10)
        self.strand1_ColorComboBox = PM_ColorComboBox(DNA_default_values_GroupBox,
                                                           label = "Strand 1:")
        self.strand2_ColorComboBox = PM_ColorComboBox(DNA_default_values_GroupBox,
                                                           label = "Strand 2:")
        self.segment_ColorComboBox = PM_ColorComboBox(DNA_default_values_GroupBox,
                                                           label = "Segment:")
        self.restore_DNA_colors_PushButton = PM_PushButton(DNA_default_values_GroupBox,
                                                      text = "Restore Default Colors",
                                                      spanWidth = False)
        strand_arrowhead_display_options_GroupBox = PM_GroupBox(_pageContainer,
                                                  title = "Strand arrowhead display options",
                                                  connectTitleButton = False)
        self.show_arrows_on_backbones_CheckBox = PM_CheckBox(strand_arrowhead_display_options_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Show arrows on backbones")
        self.show_arrows_on_3prime_ends_CheckBox = PM_CheckBox(strand_arrowhead_display_options_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Show arrows on 3' ends")
        self.show_arrows_on_5prime_ends_CheckBox = PM_CheckBox(strand_arrowhead_display_options_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Show arrows on 5' ends")
        self.three_prime_end_custom_ColorComboBox = PM_ColorComboBox(strand_arrowhead_display_options_GroupBox,
                                                           label = "3' end custom color:")
        self.five_prime_end_custom_ColorComboBox = PM_ColorComboBox(strand_arrowhead_display_options_GroupBox,
                                                           label = "5' end custom color:")        
        return
    
    def populate_Bonds(self, pagename):
        print "populate_Bonds: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        bond_colors_GroupBox = PM_GroupBox(_pageContainer,
                                           title = "Colors",
                                           connectTitleButton = False)
        self.bond_highlighting_ColorComboBox = PM_ColorComboBox(bond_colors_GroupBox,
                                                           label = "Bond highlighting:")
        self.ball_and_stick_cylinder_ColorComboBox = PM_ColorComboBox(bond_colors_GroupBox,
                                                           label = "Ball and stick cylinder:")
        self.bond_stretch_ColorComboBox = PM_ColorComboBox(bond_colors_GroupBox,
                                                           label = "Bond stretch:")
        self.Vane_Ribbon_ColorComboBox = PM_ColorComboBox(bond_colors_GroupBox,
                                                           label = "Vane/Ribbon:")
        self.restore_bond_colors_PushButton = PM_PushButton(bond_colors_GroupBox,
                                                      text = "Restore Default Colors",
                                                      spanWidth = False)
       
        misc_bond_settings_GroupBox = PM_GroupBox(_pageContainer,
                                                  title = "Miscellaneous bond settings",
                                                  connectTitleButton = False)
        self.ball_and_stick_bond_scale_SpinBox = PM_SpinBox(misc_bond_settings_GroupBox,
                                                       label = "Ball and stick bond scale:",
                                                       suffix = "%")
        self.bond_line_thickness_SpinBox = PM_SpinBox(misc_bond_settings_GroupBox,
                                                       label = "Bond line thickness:",
                                                       suffix = "pixels")
        high_order_bonds_GroupBox = PM_GroupBox(misc_bond_settings_GroupBox,
                                                title = "High order bonds",
                                                connectTitleButton = False)
        self.high_order_bonds_RadioButtonList = PM_RadioButtonList(high_order_bonds_GroupBox,
                                        buttonList = [[ 1, "Multiple cylinders", "cylinders"],
                                                      [ 2, "Vanes", "vanes"],
                                                      [ 3, "Ribbons", "ribbons"] ])
        self.show_bond_type_letters_CheckBox = PM_CheckBox(misc_bond_settings_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Show bond type letters")
        self.show_valence_errors_CheckBox = PM_CheckBox(misc_bond_settings_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Show valence errors")
        self.show_bond_stretch_indicators_CheckBox = PM_CheckBox(misc_bond_settings_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Show bond stretch indicators")
        return
    
    def populate_Rulers(self, pagename):
        print "populate_Rules: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]

        rulers_GroupBox = PM_GroupBox(_pageContainer,
                                      title = "Rulers",
                                      connectTitleButton = False)
        _choices = ["Both rulers", "Verticle ruler only", "Horizontal ruler only"]
        self.display_rulers_ComboBox = PM_ComboBox(rulers_GroupBox, 
                                      label =  "Display:", labelColumn = 0,
                                      choices = _choices, 
                                      setAsDefault = False)
        _choices = ["Lower left", "Upper left", "Lower right", "Upper right"]
        self.origin_rulers_ComboBox = PM_ComboBox(rulers_GroupBox, 
                                      label =  "Origin:", labelColumn = 0,
                                      choices = _choices, 
                                      setAsDefault = False)
        self.rulor_color_ColorComboBox = PM_ColorComboBox(rulers_GroupBox,
                                                      label = "Color:")
        self.ruler_opacity_SpinBox = PM_SpinBox(rulers_GroupBox,
                                           label = "Opacity",
                                           suffix = "%")
        self.show_rulers_in_perspective_view_CheckBox = PM_CheckBox(rulers_GroupBox,
                                                               text ="Show rulers in perspective view",
                                                               spanWidth = True,
                                                               widgetColumn = 0)
        return
    
    def populate_Plugins(self, pagename):
        print "populate_Plugins: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        pluginList = [ "QuteMolX", 
                       "POV-Ray", 
                       "MegaPOV", 
                       "POV include dir",
                       "GROMACS",
                       "cpp",
                       "Rosetta",
                       "Rosetta DB"]
        #if DEBUG:
            #self._addPageTestWidgets(_pageContainer)
        executablesGroupBox = PM_GroupBox( _pageContainer, 
                                           title = "Location of Executables",
                                           connectTitleButton = False)
        self.checkboxes = {}
        self.choosers = {}
        aWidgetList = []
        _rowNumber = 0
        for name in pluginList:
            self.checkboxes[name] = PM_CheckBox(executablesGroupBox, text = name+':  ')
            self.choosers[name] = PM_FileChooser(executablesGroupBox,
                                label     = '',
                                text      = '' ,
                                filter    = "All Files (*.*)",
                                spanWidth = True,
                                labelColumn = 0)
            aWidgetList.append( ("PM_CheckBox", self.checkboxes[name], 0, _rowNumber) )
            aWidgetList.append( ("PM_FileChooser", self.choosers[name], 1, _rowNumber) )
            _rowNumber = _rowNumber + 1
                 
        _widgetGrid = PM_WidgetGrid(executablesGroupBox,
                             widgetList = aWidgetList,
                             labelColumn  = 0)
        if DEBUG:
            print self.checkboxes
            print self.choosers
        return
    
    def populate_Adjust(self, pagename):
        print "populate_Adjust: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        adjust_physics_engine_GroupBox = PM_GroupBox(_pageContainer,
                                           title = "Adjust physics engine",
                                           connectTitleButton = False)
        _choices = ["NanoDynamics-1 (Default)", "GROMACS with ND1 Force Field",
                    "Background GROMACS with ND1 Force Field"]
        self.detail_level_ComboBox = PM_ComboBox(adjust_physics_engine_GroupBox, 
                                      label =  "", labelColumn = 0,
                                      choices = _choices, 
                                      setAsDefault = False)
        self.enable_electrostatics_CheckBox = PM_CheckBox(adjust_physics_engine_GroupBox,
                                                     spanWidth = True,
                                                     widgetColumn = 0,
                                                     text ="Enable electrostatics for DNA reduced model")
        physics_engine_animation_GroupBox = PM_GroupBox(_pageContainer,
                                                        title = "Pysics engine animation options",
                                                        connectTitleButton = False)
        self.constant_animation_update_RadioButton = PM_RadioButton(physics_engine_animation_GroupBox,
                                                               text = "Update as often as possible")
        self.update_every_RadioButton = PM_RadioButton(physics_engine_animation_GroupBox,
                                                               text = "Update Every")
        self.update_rate_SpinBox = PM_SpinBox(physics_engine_animation_GroupBox,
                                           label = "")
        _choices = ["frames", "seconds", "minutes", "hours"]
        self.detail_level_ComboBox = PM_ComboBox(physics_engine_animation_GroupBox, 
                                      label =  "",
                                      choices = _choices, 
                                      setAsDefault = False)
        aWidgetList = [ ("PM_RadioButton", self.update_every_RadioButton, 0),
                        ("PM_SpinBox", self.update_rate_SpinBox, 1),
                        ("PM_ComboBox", self.detail_level_ComboBox, 3) ]
        self.detail_level_row = PM_WidgetRow(physics_engine_animation_GroupBox,
                                        widgetList = aWidgetList,
                                        spanWidth = False)
        convergence_criteria_GroupBox = PM_GroupBox(_pageContainer,
                                                    title = "Convergence criteria",
                                                    connectTitleButton = False)
        self.endRMS_DoubelSpinBox = PM_DoubleSpinBox(convergence_criteria_GroupBox,
                                           label = "EndRMS:",
                                           suffix = " pN")
        self.endmax_SpinBox = PM_SpinBox(convergence_criteria_GroupBox,
                                           label = "EndMax:",
                                           suffix = " pN")
        self.cutoverRMS_SpinBox = PM_SpinBox(convergence_criteria_GroupBox,
                                           label = "CutoverRMS:",
                                           suffix = " pN")
        self.cutoverMax_SpinBox = PM_SpinBox(convergence_criteria_GroupBox,
                                           label = "CutoverMax:",
                                           suffix = " pN")
        return
    
    def populate_Atoms(self, pagename):
        print "populate_Atoms: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        atom_colors_GroupBox = PM_GroupBox(_pageContainer,
                                           title = "Colors",
                                           connectTitleButton = False)
        self.change_element_colors_PushButton = PM_PushButton(atom_colors_GroupBox,
                                                      text = "Change Element Colors...",
                                                      spanWidth = False)
        atom_colors_sub_GroupBox = PM_GroupBox(atom_colors_GroupBox,
                                               connectTitleButton = False)
        self.atom_highlighting_ColorComboBox = PM_ColorComboBox(atom_colors_sub_GroupBox,
                                                      label = "Atom Highlighting:")
        self.bondpoint_highlighting_ColorComboBox = PM_ColorComboBox(atom_colors_sub_GroupBox,
                                                      label = "Bondpoint Highlighting:")
        self.bondpoint_hotspots_ColorComboBox = PM_ColorComboBox(atom_colors_sub_GroupBox,
                                                      label = "Bondpoint hotspots:")
        self.restore_element_colors_PushButton = PM_PushButton(atom_colors_sub_GroupBox,
                                                      text = "Restore Default Colors",
                                                      spanWidth = False)
        misc_atom_settings_GroupBox = PM_GroupBox(_pageContainer,
                                                  title = "Miscellaneous atom options",
                                                  connectTitleButton = False)
        _choices = ["Low", "Medium", "High", "Variable"]
        self.detail_level_ComboBox = PM_ComboBox(misc_atom_settings_GroupBox, 
                                      label =  "Level of detail:", labelColumn = 0,
                                      choices = _choices, 
                                      setAsDefault = False)
        self.ball_and_stick_atom_scale_SpinBox = PM_SpinBox(misc_atom_settings_GroupBox,
                                                       label = "Ball and stick atom scale",
                                                       suffix = "%")
        self.CPK_atom_scale_SpinBox = PM_SpinBox(misc_atom_settings_GroupBox,
                                            label = "CPK atom scale",
                                            suffix = "%")
        self.overlapping_atom_indicators_CheckBox = PM_CheckBox(misc_atom_settings_GroupBox,
                                                           spanWidth = True,
                                                           widgetColumn = 0,
                                                           text ="Overlapping atom indicators")
        self.force_to_keep_bonds_during_transmute_CheckBox = PM_CheckBox(misc_atom_settings_GroupBox,
                                                                    spanWidth = True,
                                                                    widgetColumn = 0,
                                                                    text ="Force to keep bonds during transmute:")
        return
    
    def populate_Window(self, pagename):
        print "populate_Window: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        window_position_and_size_GroupBox = PM_GroupBox(_pageContainer,
                                                  title = "Window Postion and Size",
                                                  connectTitleButton = False)
        self.current_size_x_SpinBox = PM_SpinBox(window_position_and_size_GroupBox,
                                                         label = "", 
                                                         suffix = "pixels",
                                                         labelColumn = 0,
                                                         singleStep = 1,
                                                         )
        self.current_size_y_SpinBox = PM_SpinBox(window_position_and_size_GroupBox,
                                                         label = "",
                                                         labelColumn = 0,
                                                         suffix = "pixels", 
                                                         singleStep = 1,
                                                         )
        self.current_size_save_Button = PM_PushButton(window_position_and_size_GroupBox, 
                                                 text = "Save Current")
        aWidgetList = [ ("QLabel", "Current size:", 0),
                        ("PM_SpinBox", self.current_size_x_SpinBox, 1),
                        ("QLabel", " x ", 2),
                        ("PM_SpinBox", self.current_size_y_SpinBox, 3),
                        ("PM_PushButton", self.current_size_save_Button, 4) ]
        widgetRow = PM_WidgetRow(window_position_and_size_GroupBox,
                         title     = '',
                         spanWidth = False,
                         widgetList = aWidgetList)        

        self.saved_size_x_LineEdit = PM_LineEdit(window_position_and_size_GroupBox,
                                                         label = "")
        self.saved_size_y_LineEdit = PM_LineEdit(window_position_and_size_GroupBox,
                                                         label = "")
        self.saved_size_save_Button = PM_PushButton(window_position_and_size_GroupBox, 
                                                 text = "Restore saved")
        aWidgetList = [ ("QLabel", "Saved size:", 0),
                        ("PM_SpinBox", self.saved_size_x_LineEdit, 1),
                        ("QLabel", " x ", 2),
                        ("PM_SpinBox", self.saved_size_y_LineEdit, 3),
                        ("PM_PushButton", self.saved_size_save_Button, 4) ]
        #widgetRow = PM_WidgetRow(window_position_and_size_GroupBox,
                         #title     = '',
                         #spanWidth = False,
                         #widgetList = aWidgetList)
        self.save_size_on_quit = PM_CheckBox(window_position_and_size_GroupBox,
                                        text = "Always save current position and size when quitting",
                                        widgetColumn = 0,
                                        spanWidth = True)
        window_caption_format_GroupBox = PM_GroupBox(_pageContainer,
                                                  title = "Window caption format",
                                                  connectTitleButton = False)
        self.caption_prefix_LineEdit = PM_LineEdit(window_caption_format_GroupBox,
                                              spanWidth = True,
                                              label = "Window caption prefix for modified file: ")
        self.caption_suffix_LineEdit = PM_LineEdit(window_caption_format_GroupBox,
                                              spanWidth = True,
                                              label = "Window caption suffix for modified file: ")
        self.display_full_path_CheckBox = PM_CheckBox(window_caption_format_GroupBox,
                                                 text = "Display full path of part",
                                                 widgetColumn = 0,
                                                 spanWidth = True)
        custom_font_GroupBox = PM_GroupBox(_pageContainer,
                                           title = "Custom Font",
                                           connectTitleButton = False)
        self.use_custom_font_CheckBox = PM_CheckBox(custom_font_GroupBox,
                                               text = "Use custom font",
                                               spanWidth = True,
                                               widgetColumn = 0)
        self.custom_fontComboBox = PM_FontComboBox(custom_font_GroupBox, 
                                      label =  "Font:", labelColumn = 0,
                                      setAsDefault = False,
                                      spanWidth = False)
        self.custom_font_size_SpinBox = PM_SpinBox(custom_font_GroupBox,
                                            label = "Size: ")
        self.make_default_font_PushButton = PM_PushButton(custom_font_GroupBox, 
                                                     spanWidth = True,
                                                     text = "Make selected font the default font")
        return
    
    def populate_Graphics_Area(self, pagename):
        print "populate_Graphics_Area: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        _choices = ["Lines", "Tubes", "Ball and Stick", "CPK", "DNA Cylinder"]
        globalDisplayStyleStartupComboBox = PM_ComboBox(_pageContainer, 
                                      label =  "Global display style at start-up:", 
                                      choices = _choices, setAsDefault = False)
        compassGroupBox = PM_GroupBox(_pageContainer, 
                                       title = "Compass display settings",
                                       connectTitleButton = False)
        self.display_compass_CheckBox = PM_CheckBox(compassGroupBox, 
                                               text = "Display compass: ",
                                               widgetColumn = 0)
        _choices = ["Upper right", "Upper left", "Lower left", "Lower right"]
        self.globalDisplayStyleStartupComboBox = PM_ComboBox(compassGroupBox, 
                                      label =  "Compass Location:", labelColumn = 0,
                                      choices = _choices, 
                                      setAsDefault = False)
        self.display_compass_labels_checkbox = PM_CheckBox(compassGroupBox, 
                                               text = "Display compass labels ",
                                               spanWidth = True,
                                               widgetColumn = 0)
        axesGroupBox = PM_GroupBox(_pageContainer, 
                                   title = "Axes",
                                   connectTitleButton = False)
        self.display_origin_axix_checkbox = PM_CheckBox(axesGroupBox, 
                                               text = "Display origin axis",
                                               widgetColumn = 0)
        self.display_pov_axis_checkbox = PM_CheckBox(axesGroupBox, 
                                               text = "Display point of view (POV) axis ",
                                               spanWidth = True,
                                               widgetColumn = 0)
        cursor_text_GroupBox = PM_GroupBox(_pageContainer, 
                                       title = "Cursor text settings",
                                       connectTitleButton = False)
        self.cursor_text_CheckBox = PM_CheckBox(cursor_text_GroupBox, 
                                           text = "Cursor text",
                                           widgetColumn = 0)
        self.cursor_text_font_size_SpinBox = PM_DoubleSpinBox(cursor_text_GroupBox,
                                                         label = "", 
                                                         suffix = "pt", 
                                                         singleStep = 1,
                                                         )
        self.cursor_text_reset_Button = PM_PushButton(cursor_text_GroupBox, 
                                                 text = "reset")
        aWidgetList = [ ("QLabel", "Font size: ", 0),
                        ("PM_DoubleSpinBox", self.cursor_text_font_size_SpinBox, 1),
                        ("QLabel", "     ", 2),
                        ("PM_PushButton", self.cursor_text_reset_Button, 3),
                        ("QSpacerItem", 0, 0, 3)]
                            
        widgetRow = PM_WidgetRow(cursor_text_GroupBox,
                         title     = '',
                         spanWidth = True,
                         widgetList = aWidgetList)

        self.cursor_text_color_ComboBox = PM_ColorComboBox(cursor_text_GroupBox,
                                                      label = "Cursor Text color:",
                                                      spanWidth = False)
        misc_graphics_GroupBox = PM_GroupBox(_pageContainer, 
                                       title = "Other graphics options",
                                       connectTitleButton = False)
        self.display_confirmation_corner_CheckBox = PM_CheckBox(misc_graphics_GroupBox, 
                                           text = "Display confirmation corner",
                                           widgetColumn = 0)
        self.anti_aliasing_CheckBox = PM_CheckBox(misc_graphics_GroupBox, 
                                           text = "Enable anti-aliasing (next session)",
                                           widgetColumn = 0)
        
        return
    
    def populate_Base_orientation_indicator(self, pagename):
        print "populate_Base_orientation_indicator: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        self.base_orientation_indicatiors_CheckBox = PM_CheckBox(_pageContainer, 
                                             text = "Display base orientation indicators",
                                             spanWidth = True,
                                             widgetColumn = 0)
        base_orientation_GroupBox = PM_GroupBox(_pageContainer, 
                                                      title = "Base orientation indicator parameters",
                                                      connectTitleButton = False)
        self.indicators_color_ColorComboBox = PM_ColorComboBox(base_orientation_GroupBox,
                                                      label = "Indicators color:",
                                                      spanWidth = False)
        self.inverse_indicators_color_ColorComboBox = PM_ColorComboBox(base_orientation_GroupBox,
                                                      label = "Color:",
                                                      spanWidth = False)
        self.enable_inverse_indicatiors_CheckBox = PM_CheckBox(base_orientation_GroupBox, 
                                             text = "Display base orientation indicators",
                                             spanWidth = True,
                                             widgetColumn = 0)
        self.angle_threshold_DoubleSpinBox = PM_DoubleSpinBox(base_orientation_GroupBox,
                                                         label = "Angle threshold:", 
                                                         suffix = "",
                                                         spanWidth = False,
                                                         singleStep = .1)
        self.terminal_base_distance_SpinBox = PM_SpinBox(base_orientation_GroupBox,
                                                         label = "Terminal base distance:", 
                                                         suffix = "",
                                                         spanWidth = False,
                                                         singleStep = 1)
        return
    
    def populate_Undo(self, pagename):
        print "populate_Undo: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        self.undo_restore_view_CheckBox = PM_CheckBox(_pageContainer,
                                                 text = "Restore view when undoing structural changes",
                                                 widgetColumn = 0,
                                                 spanWidth = True)
        self.undo_automatic_checkpoints_CheckBox = PM_CheckBox(_pageContainer,
                                                 text = "Automatic Checkpoints",
                                                 widgetColumn = 0,
                                                 spanWidth = True)
        self.undo_stack_memory_limit_SpinBox = PM_SpinBox(_pageContainer,
                                                     label = "Undo stack memory limit: ",
                                                     suffix = "MB",
                                                     spanWidth = False,
                                                     singleStep = 1)
        vSpacer = QtGui.QSpacerItem(1, 1, 
                                    QSizePolicy.Preferred, 
                                    QSizePolicy.Expanding)
        _pageContainer.vBoxLayout.addItem(vSpacer)
        return
    
    def populate_Zoom_Pan_and_Rotate(self, pagename):
        print "populate_Zoom_Pan_and_Rotate: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        view_rotation_settings_GroupBox = PM_GroupBox(_pageContainer, 
                                                      title = "View rotation settings",
                                                      connectTitleButton = False)
        self.animate_views_CheckBox = PM_CheckBox(view_rotation_settings_GroupBox, 
                                             text = "Animate between views",
                                             widgetColumn = 0)
        self.view_animation_speed_Slider = PM_Slider(view_rotation_settings_GroupBox,
                                                label = "View animation speed: ",
                                                spanWidth = True)
        labelList = [["QLabel", "slow", 0], ["QSpacerItem", 0, 0, 1], ["QLabel", "fast", 2]]
        self.SF1_Label = PM_WidgetRow(view_rotation_settings_GroupBox,
                                 spanWidth = True,
                                 widgetList = labelList)
        self.mouse_rotation_speed_Slider = PM_Slider(view_rotation_settings_GroupBox,
                                                label = "Mouse rotation speed: ",
                                                spanWidth = True)
        self.SF2_Label = PM_WidgetRow(view_rotation_settings_GroupBox,
                                 spanWidth = True,
                                 widgetList = labelList)
        mouse_zoom_settings_GroupBox = PM_GroupBox(_pageContainer,
                                                   title = "Mouse wheel zoom settings",
                                                   connectTitleButton = False)
        
        _choices = ["Pull/push wheel to zoom in/out", "Push/pull wheel to zoom in/out"]
        self.zoom_directon_ComboBox = PM_ComboBox(mouse_zoom_settings_GroupBox, 
                                      label =  "Direction:", labelColumn = 0,
                                      choices = _choices, 
                                      setAsDefault = False)
        _choices = ["Center about cursor postion", "Center about screen"]
        self.zoom_in_center_ComboBox = PM_ComboBox(mouse_zoom_settings_GroupBox, 
                                      label =  "Zoom in:", labelColumn = 0,
                                      choices = _choices, 
                                      setAsDefault = False)
        _choices = ["Pull/push wheel to zoom in/out", "Push/pull wheel to zoom in/out"]
        self.zoom_out_center_ComboBox = PM_ComboBox(mouse_zoom_settings_GroupBox, 
                                      label =  "Zoom out:", labelColumn = 0,
                                      choices = _choices, 
                                      setAsDefault = False)
        self.hover_highlighting_timeout_SpinBox = PM_DoubleSpinBox(mouse_zoom_settings_GroupBox,
                                                         label = "Hover highlighting\ntimeout interval", 
                                                         suffix = "seconds",
#                                                         spanWidth = True,
                                                         singleStep = .1)
        return
    
    def populate_Lighting(self, pagename):
        print "populate_Lighting: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        self.lighting_defaults_PushButton = PM_PushButton( _pageContainer,
                                                      text = "Restore Defaults")
        directional_lighting_GroupBox = PM_GroupBox(_pageContainer, 
                                        title = "Directional light properties",
                                        connectTitleButton = False)
        _choices = ["1 (off)", "2 (off)", "3 (off)"]
        self.light_ComboBox = PM_ComboBox(directional_lighting_GroupBox, 
                                      label =  "", labelColumn = 0,
                                      choices = _choices, 
                                      setAsDefault = False)
        self.light_on_CheckBox = PM_CheckBox(directional_lighting_GroupBox, 
                                             text = ": On",
                                             widgetColumn = 0)
        aWidgetList = [ ("QLabel", "Light: ", 0),
                        ("PM_ComboBox", self.light_ComboBox, 1),
                        ("QLabel", " ", 2),
                        ("PM_CheckBox", self.light_on_CheckBox, 3)]
        _sliderline = PM_WidgetRow(directional_lighting_GroupBox,
                                 spanWidth = True,
                                 widgetList = aWidgetList)
        self.light_color_ColorComboBox = PM_ColorComboBox(directional_lighting_GroupBox,
                                                      label = "Color:",
                                                      spanWidth = False)
        self.ambient_light_LineEdit = PM_LineEdit(directional_lighting_GroupBox,
                                             label = "",
                                             text = ".1")
        self.ambient_light_Slider = PM_Slider(directional_lighting_GroupBox)
        aWidgetList = [["QLabel", "Ambient:", 0], 
                       ["PM_LineEdit", self.ambient_light_LineEdit, 1], 
                       ["PM_Slider", self.ambient_light_Slider, 2]]
        _sliderline = PM_WidgetRow(directional_lighting_GroupBox,
                                 spanWidth = True,
                                 widgetList = aWidgetList)

        self.difuse_light_LineEdit = PM_LineEdit(directional_lighting_GroupBox,
                                             label = "",
                                             text = ".1")
        self.difuse_light_Slider = PM_Slider(directional_lighting_GroupBox)
        aWidgetList = [["QLabel", "Difuse:", 0], 
                       ["PM_LineEdit", self.difuse_light_LineEdit, 1], 
                       ["PM_Slider", self.difuse_light_Slider, 2]]
        _sliderline = PM_WidgetRow(directional_lighting_GroupBox,
                                 spanWidth = True,
                                 widgetList = aWidgetList)

        self.specular_light_LineEdit = PM_LineEdit(directional_lighting_GroupBox,
                                             label = "",
                                             text = ".1")
        self.specular_light_Slider = PM_Slider(directional_lighting_GroupBox)
        aWidgetList = [["QLabel", "Specular:", 0], 
                       ["PM_LineEdit", self.specular_light_LineEdit, 1], 
                       ["PM_Slider", self.specular_light_Slider, 2]]
        _sliderline = PM_WidgetRow(directional_lighting_GroupBox,
                                 spanWidth = True,
                                 widgetList = aWidgetList)
        self.X_light_LineEdit = PM_LineEdit(directional_lighting_GroupBox,
                                             label = "X:",
                                             text = ".1")
        self.Y_light_LineEdit = PM_LineEdit(directional_lighting_GroupBox,
                                             label = "Y:",
                                             text = ".1")
        self.Z_light_LineEdit = PM_LineEdit(directional_lighting_GroupBox,
                                             label = "Z:",
                                             text = ".1")
        material_specular_properties_GroupBox = PM_GroupBox(_pageContainer, 
                                        title = "Material specular properties",
                                        connectTitleButton = False)        
        self.material_specular_properties_on_CheckBox = PM_CheckBox(material_specular_properties_GroupBox, 
                                             text = ": On",
                                             widgetColumn = 0)
        self.material_specular_properties_finish_LineEdit = PM_LineEdit(material_specular_properties_GroupBox,
                                             label = "Finish: ",
                                             text = ".1")
        self.material_specular_properties_finish_Slider = PM_Slider(material_specular_properties_GroupBox)
#        aWidgetList = [["QLabel", "Finish:", 0], 
#                       ["PM_LineEdit", material_specular_properties_finish_LineEdit, 1], 
#                       ["PM_Slider", material_specular_properties_finish_Slider, 2]]
#        _sliderline = PM_WidgetRow(material_specular_properties_GroupBox,
#                                 spanWidth = True,
#                                 widgetList = aWidgetList)
        labelList = [["QLabel", "Metal", 0], ["QSpacerItem", 0, 0, 1], ["QLabel", "Plastic", 2]]
        SF1_Label = PM_WidgetRow(material_specular_properties_GroupBox,
                                 spanWidth = True,
                                 widgetList = labelList)

        self.material_specular_properties_shininess_LineEdit = PM_LineEdit(material_specular_properties_GroupBox,
                                             label = "Shininess: ",
                                             text = ".1")
        self.material_specular_properties_shininess_Slider = PM_Slider(material_specular_properties_GroupBox)
#        aWidgetList = [["QLabel", "Shininess:", 0], 
#                       ["PM_LineEdit", material_specular_properties_shininess_LineEdit, 1], 
#                       ["PM_Slider", material_specular_properties_shininess_Slider, 2]]
#        _sliderline = PM_WidgetRow(material_specular_properties_GroupBox,
#                                 spanWidth = True,
#                                 widgetList = aWidgetList)
        labelList = [["QLabel", "Flat", 0], ["QSpacerItem", 0, 0, 1], ["QLabel", "Glossy", 2]]
        SF2_Label = PM_WidgetRow(material_specular_properties_GroupBox,
                                 spanWidth = True,
                                 widgetList = labelList)

        self.material_specular_properties_brightness_LineEdit = PM_LineEdit(material_specular_properties_GroupBox,
                                             label = "Brightness: ",
                                             text = ".1")
        self.material_specular_properties_brightness_Slider = PM_Slider(material_specular_properties_GroupBox)
#        aWidgetList = [["QLabel", "Brightness:", 0], 
#                       ["PM_LineEdit", material_specular_properties_brightness_LineEdit, 1], 
#                       ["PM_Slider", material_specular_properties_brightness_Slider, 2]]
#        _sliderline = PM_WidgetRow(material_specular_properties_GroupBox,
#                                 spanWidth = True,
#                                 widgetList = aWidgetList)
        labelList = [["QLabel", "Low", 0], ["QSpacerItem", 0, 0, 1], ["QLabel", "High", 2]]
        SF3_Label = PM_WidgetRow(material_specular_properties_GroupBox,
                                 spanWidth = True,
                                 widgetList = labelList)
        return
    
    def populate_Minor_groove_error_indicator(self, pagename):
        print "populate_Minor_groove_error_indicator: %s" % pagename
        page_widget = self.getPage(pagename)
        _pageContainer = page_widget.getPageContainers()
        _pageContainer = _pageContainer[0]
        self.minor_groove_error_indicatiors_CheckBox = PM_CheckBox(_pageContainer, 
                                             text = "Display minor groove error indicators",
                                             spanWidth = True,
                                             widgetColumn = 0)
        minor_groove_error_parameters_GroupBox = PM_GroupBox(_pageContainer, 
                                                      title = "Error indicator parameters",
                                                      connectTitleButton = False)
        self.minor_groove_error_minimum_angle_SpinBox = PM_SpinBox(minor_groove_error_parameters_GroupBox,
                                                         label = "Minimum angle:", 
                                                         suffix = " degrees",
                                                         spanWidth = False,
                                                         singleStep = 1)
        self.minor_groove_error_maximum_angle_SpinBox = PM_SpinBox(minor_groove_error_parameters_GroupBox,
                                                         label = "Maximum angle:", 
                                                         suffix = " degrees",
                                                         spanWidth = False,
                                                         singleStep = 1)
        self.minor_groove_error_color_ColorComboBox = PM_ColorComboBox(minor_groove_error_parameters_GroupBox,
                                                      label = "Color:",
                                                      spanWidth = False)
        self.minor_groove_error_reset_PushButton = PM_PushButton(minor_groove_error_parameters_GroupBox,
                                                      text = "Reset factory defaults",
                                                      spanWidth = False)
        return
    

# End of PreferencesDialog class

#if __name__ == "__main__":
    #app = QtGui.QApplication(sys.argv)
    #pd = PreferencesDialog()
    #pd.show()
    #sys.exit(app.exec_())