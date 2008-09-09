# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_WidgetsDemoPropertyManager.py - Displays all the PM module widgets in a PM.

$Id$
"""

from PyQt4.Qt import Qt, SIGNAL

from PM.PM_Dialog          import PM_Dialog
from PM.PM_GroupBox        import PM_GroupBox

from PM.PM_CheckBox        import PM_CheckBox
from PM.PM_ComboBox        import PM_ComboBox
from PM.PM_DoubleSpinBox   import PM_DoubleSpinBox
from PM.PM_ElementChooser  import PM_ElementChooser
from PM.PM_LineEdit        import PM_LineEdit
from PM.PM_ListWidget      import PM_ListWidget
from PM.PM_PushButton      import PM_PushButton
from PM.PM_RadioButton     import PM_RadioButton
from PM.PM_RadioButtonList import PM_RadioButtonList
from PM.PM_SpinBox         import PM_SpinBox
from PM.PM_TextEdit        import PM_TextEdit
from PM.PM_ToolButton      import PM_ToolButton
from PM.PM_ToolButtonGrid  import PM_ToolButtonGrid

from command_support.GeneratorBaseClass import GeneratorBaseClass

# Options for radio button list to create a PM_RadioButtonList widget.
# Format: buttonId, buttonText, tooltip
OPTIONS_BUTTON_LIST = [ \
    ( 0, "Option 1", "Tooltip text for option 1"),
    ( 1, "Option 2", "Tooltip text for option 2"),
    ( 2, "Option 3", "Tooltip text for option 3"),
    ( 3, "Option 4", "Tooltip text for option 4")
]

# Tool button list to create a PM_ToolButtonGrid.
# Format: 
# - buttonId, buttonText, iconPath, column, row, tooltipText
TOOL_BUTTON_LIST = [ \
    ( 5,  "B", "", 0, 1, "Boron"      ),
    ( 6,  "C", "", 1, 1, "Carbon"     ),
    ( 7,  "N", "", 2, 1, "Nitrogen"   ),
    ( 8,  "O", "", 3, 1, "Oxygen"     ),
    ( 9,  "F", "", 4, 1, "Fluorine"   ),
    (10, "Ne", "", 5, 1, "Neon"       ),
    (13, "Al", "", 0, 2, "Aluminum"   ),
    (14, "Si", "", 1, 2, "Silicon"    ),
    (15,  "P", "", 2, 2, "Phosphorus" ),
    (16,  "S", "", 3, 2, "Sulfur"     ),
    (17, "Cl", "", 4, 2, "Chlorine"   ),
    (18, "Ar", "", 5, 2, "Argon"      )
]

class PM_WidgetsDemoPropertyManager(PM_Dialog, GeneratorBaseClass):
    """
    This is a special command for testing new widgets in the PM module
    in their own Property Manager. It does nothing except display PM group boxes
    and their widgets.
    """
    
    title = "PM Widget Demo"
    pmName = title
    iconPath = "ui/actions/Properties Manager/info.png"

    def __init__(self, win, command = None):
       
        self.win = win
                
        PM_Dialog.__init__( self, self.pmName, self.iconPath, self.title )
        GeneratorBaseClass.__init__( self, win)    
                
        msg = "This Property Manager (PM) is used to display and/or test new \
               PM widgets avaiable in NanoEngineer-1's PM module."
        
        # This causes the "Message" box to be displayed as well.
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault = False )
        return

    def _addGroupBoxes(self):
        """
        Add group boxes to the Property Manager.
        """
                        
        self.widgetSelectorGroupBox = PM_GroupBox(self, title = "PM Widget Selector" )
        self._loadWidgetSelectorGroupBox(self.widgetSelectorGroupBox)
        
        self.groupBoxes = []
        
        pmGroupBox = PM_GroupBox(self, title = "PM_CheckBox")
        self._loadPM_CheckBox(pmGroupBox)
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_GroupBox(self, title = "PM_ComboBox")
        self._loadPM_ComboBox(pmGroupBox)
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_GroupBox(self, title = "PM_DoubleSpinBox")
        self._loadPM_DoubleSpinBox(pmGroupBox)
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox =  PM_ElementChooser(self, title = "PM_ElementChooser")
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_GroupBox(self, title = "PM_LineEdit")
        self._loadPM_LineEdit(pmGroupBox)
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_GroupBox(self, title = "PM_ListWidget")
        self._loadPM_ListWidget(pmGroupBox)
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_GroupBox(self, title = "PM_PushButton")
        self._loadPM_PushButton(pmGroupBox)
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_GroupBox(self, title = "PM_RadioButton")
        self._loadPM_TextEdit(pmGroupBox)
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_RadioButtonList( self,
                                         title      = "PM_RadioButtonList", 
                                         buttonList = OPTIONS_BUTTON_LIST,
                                         checkedId  = 2 )
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_GroupBox(self, title = "PM_SpinBox")
        self._loadPM_SpinBox(pmGroupBox)
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_GroupBox(self, title = "PM_TextEdit")
        self._loadPM_TextEdit(pmGroupBox)
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_GroupBox(self, title = "PM_ToolButton")
        self._loadPM_ToolButton(pmGroupBox)
        self.groupBoxes.append(pmGroupBox)
        
        pmGroupBox = PM_ToolButtonGrid( self, 
                                        title        = "PM_ToolButtonGrid",
                                        buttonList   = TOOL_BUTTON_LIST,
                                        checkedId    = 6,
                                        setAsDefault = True )
        self.groupBoxes.append(pmGroupBox)
        
        self.widgetSelectorComboBox.clear()
        titles = self._getGroupBoxTitles()
        self.widgetSelectorComboBox.addItems(titles)
        
        self._updateGroupBoxes(0)
        
    def _loadWidgetSelectorGroupBox(self, inPmGroupBox):
        """
        Widget selector group box.
        """
        
        # The widget choices are set via self._getGroupBoxTitles() later.
        widgetTypeChoices = [ "PM_CheckBox" ]
        
        self.widgetSelectorComboBox = \
            PM_ComboBox( inPmGroupBox,
                         label        = "Select a PM widget:", 
                         choices      = widgetTypeChoices, 
                         index        = 0, 
                         setAsDefault = False,
                         spanWidth    = True )
        
        self.connect(self.widgetSelectorComboBox, 
                     SIGNAL("currentIndexChanged(int)"), 
                     self._updateGroupBoxes)
    
    def _loadPM_CheckBox(self, inPmGroupBox):
        """
        PM_CheckBox.
        """
        self.checkBoxGroupBox = \
            PM_GroupBox( inPmGroupBox, 
                         title          = "<b> PM_CheckBox examples</b>" )
        
        self.checkBox1 = \
            PM_CheckBox( self.checkBoxGroupBox,
                         text         = "Label on left:",
                         widgetColumn = 1,
                         state        = Qt.Checked,
                         setAsDefault = True,
                        )
        
        self.checkBox2 = \
            PM_CheckBox( self.checkBoxGroupBox,
                         text          = ": Label on right",
                         widgetColumn  = 1,
                         state         = Qt.Checked,
                         setAsDefault  = True,
                        )
        
        self.checkBox3 = \
            PM_CheckBox( self.checkBoxGroupBox,
                         text         = "CheckBox (spanWidth = True):",
                         state        = Qt.Unchecked,
                         setAsDefault = False,
                       )
        
    def _loadPM_ComboBox(self, inPmGroupBox):
        """
        PM_ComboBox widgets.
        """
        
        choices = [ "First", "Second", "Third (Default)", "Forth" ]
        
        self.comboBox1= \
            PM_ComboBox( inPmGroupBox,
                         label        = 'Choices: ', 
                         choices      = choices, 
                         index        = 2, 
                         setAsDefault = True,
                         spanWidth    = False )
        
        self.comboBox2= \
            PM_ComboBox( inPmGroupBox,
                         label        = ' :Choices', 
                         labelColumn  = 1,
                         choices      = choices, 
                         index        = 2, 
                         setAsDefault = True,
                         spanWidth    = False )
        
        self.comboBox3= \
            PM_ComboBox( inPmGroupBox,
                         label        = ' Choices (SpanWidth = True):', 
                         labelColumn  = 1,
                         choices      = choices, 
                         index        = 2, 
                         setAsDefault = True,
                         spanWidth    = True )      
        
        self.nestedGroupBox1 = \
            PM_GroupBox( inPmGroupBox, 
                         title          = "Group Box Title" )
            
        self.comboBox4= \
            PM_ComboBox( self.nestedGroupBox1,
                         label        = "Choices:", 
                         choices      = choices, 
                         index        = 2, 
                         setAsDefault = True,
                         spanWidth    = False )
        
        self.nestedGroupBox2 = \
            PM_GroupBox( inPmGroupBox, 
                         title          = "Group Box Title" )
            
        self.comboBox6= \
            PM_ComboBox( self.nestedGroupBox2,
                         label        = "Choices:", 
                         choices      = choices, 
                         index        = 2, 
                         setAsDefault = True,
                         spanWidth    = True )
    
    def _loadPM_DoubleSpinBox(self, inPmGroupBox):
        """
        PM_DoubleSpinBox widgets.
        """
        
        self.doubleSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox, 
                              #label="Spanning DoubleSpinBox :",
                              label        = "", # No label
                              value        = 5.0, 
                              setAsDefault = True,
                              minimum      = 1.0, 
                              maximum      = 10.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = ' Suffix',
                              spanWidth    = True )
            
        # Add a prefix example.
        self.doubleSpinBox.setPrefix("Prefix ")
        
    def _loadPM_LineEdit(self, inPmGroupBox):
        """
        PM_LineEdit widgets.
        """
        
        self.lineEdit1 = \
            PM_LineEdit( inPmGroupBox, 
                         label        = "Name:",
                         text         = "RotaryMotor-1",
                         setAsDefault = True,
                         spanWidth    = False)
        
        self.lineEdit2 = \
            PM_LineEdit( inPmGroupBox, 
                         label        = ":Name",
                         labelColumn  = 1,
                         text         = "RotaryMotor-1",
                         setAsDefault = True,
                         spanWidth    = False)
        
        self.lineEdit3 = \
            PM_LineEdit( inPmGroupBox, 
                         label        = "LineEdit (spanWidth = True):",
                         text         = "RotaryMotor-1",
                         setAsDefault = False,
                         spanWidth    = True)
    
    def _loadPM_ListWidget(self, inPmGroupBox):
        """
        PM_ListWidget.
        """
        
        items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6"]
        
        self.listWidget1 = \
            PM_ListWidget( inPmGroupBox, 
                         label        = "Items to select (label on top):",
                         items        = items, 
                         defaultRow   = 0, 
                         setAsDefault = False,
                         heightByRows = 4, 
                         spanWidth    = True )
        
        self.listWidget2 = \
            PM_ListWidget( inPmGroupBox, 
                         label        = "Items:",
                         items        = items, 
                         defaultRow   = 0, 
                         setAsDefault = False,
                         heightByRows = 4, 
                         spanWidth    = False )
        
    def _loadPM_PushButton(self, inPmGroupBox):
        """
        PM_PushButton widgets.
        """
        
        self.pushButton1 = \
            PM_PushButton( inPmGroupBox,
                           label = "",
                           text  = "PushButton 1" )
        
        self.pushButton2 = \
            PM_PushButton( inPmGroupBox,
                           label     = "",
                           text      = "PushButton 2",
                           spanWidth = True )
        
    def _loadPM_RadioButton(self, inPmGroupBox):
        """
        PM_RadioButton.
        """
        
        self.radioButton1 = \
            PM_RadioButton( inPmGroupBox, 
                            text = "Display PM_CheckBox group box")
        
    def _loadPM_SpinBox(self, inPmGroupBox):
        """
        PM_SpinBox widgets.
        """
        
        self.spinBox = \
            PM_SpinBox( inPmGroupBox, 
                        label        = "Spinbox:", 
                        value        = 5, 
                        setAsDefault = True,
                        minimum      = 2, 
                        maximum      = 10, 
                        suffix       = ' things',
                        spanWidth    = True )
            
    def _loadPM_TextEdit(self, inPmGroupBox):
        """
        PM_TextEdit widgets.
        """
        
        self.textEdit = \
            PM_TextEdit( inPmGroupBox, 
                         label     = "TextEdit:", 
                         spanWidth = False )
        
        self.spanTextEdit = \
            PM_TextEdit( inPmGroupBox, 
                         label     = "PM_TextEdit with label on top:", 
                         spanWidth = True )
    
    def _loadPM_ToolButton(self, inPmGroupBox):
        """
        PM_ToolButton widgets.
        """
        
        self.toolButton1 = \
            PM_ToolButton( inPmGroupBox,
                           label = "",
                           text  = "ToolButton 1" )
        
        self.toolButton2 = \
            PM_ToolButton( inPmGroupBox,
                           label     = "",
                           text      = "ToolButton 2",
                           spanWidth = True )
        
    def _getGroupBoxTitles(self):
        """
        Returns all the group box titles in a list.
        """
        titles = []
        for groupBox in self.groupBoxes:
            titles.append(groupBox.getTitle())
        return titles
    
    def _updateGroupBoxes(self, index):
        """
        Update the group boxes displayed based index.
        """
        
        count = 0
        for groupBox in self.groupBoxes:
            if index == count:
                groupBox.show()
            else:
                groupBox.hide()
            count += 1
