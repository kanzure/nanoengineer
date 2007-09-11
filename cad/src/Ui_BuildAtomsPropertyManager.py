# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_BuildAtomsPropertyManager.py

The Ui_BuildAtomsPropertyManager class defines UI elements for the Property 
Manager of the B{Build Atoms mode}.
    
@author: Ninad
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Before Alpha9, (code that used Qt3 framework) Build Atoms mode had a 
'Molecular Modeling Kit' (MMKit) and a dashboard. Starting Alpha 9,
this functionality was integrated into a Property Manager. Since then 
several changes have been made. 
ninad 2007-08-29: Created: Rewrote all UI to make it use the 'PM' module 
                  classes. This deprecates class MMKitDialog.
                  Split out old 'clipboard' functionality into new L{PasteMode}

"""

from PyQt4.Qt import Qt

from PM.PM_Dialog          import PM_Dialog
from PM.PM_GroupBox        import PM_GroupBox
from PM.PM_CheckBox        import PM_CheckBox
from PM.PM_ToolButtonRow   import PM_ToolButtonRow
from PM.PM_ElementChooser  import PM_ElementChooser
from PM.PM_PreviewGroupBox import PM_PreviewGroupBox
from PM.PM_LineEdit        import PM_LineEdit

from PM.PM_Constants       import pmDoneButton
from PM.PM_Constants       import pmWhatsThisButton


class Ui_BuildAtomsPropertyManager(PM_Dialog):
    """
    The Ui_BuildAtomsPropertyManager class defines UI elements for the Property 
    Manager of the B{Build Atoms mode}.
    
    @ivar title: The title that appears in the property manager header.
    @type title: str
    
    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str
    
    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """
       
    # The title that appears in the Property Manager header        
    title = "Build Atoms"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Tools/Build Structures/Build Atoms.png"
    
    def __init__(self, parentMode):
        """
        Constructor for the B{Build Atoms} property manager class that defines 
        its UI.
        
        @param parentMode: The parent mode where this Property Manager is used
        @type  parentMode: L{depositMode}        
        """
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)
        
        self.showTopRowButtons(pmDoneButton | pmWhatsThisButton)
        
        self.parentMode = parentMode
        self.o = self.parentMode.w.glpane 
        msg = ''
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
        
        self.previewGroupBox = None
        self.elementChooser = None
        self.advancedOptionsGroupBox = None
        self.bondToolsGroupBox = None
        
        self.selectionFilterCheckBox = None
        self.filterlistLE = None
        
    def _addGroupBoxes(self):
        """
        Add various group boxes to the Build Atoms Property manager. 
        """
        self._addPreviewGroupBox()        
        self._addElementChooserGroupBox()            
        self._addBondToolsGroupBox()        
        self._addAdvancedOptionsGroupBox()       
       
    def _addPreviewGroupBox(self):
        """
        Adde the preview groupbox that shows the element selected in the 
        element chooser. 
        """
        self.previewGroupBox = PM_PreviewGroupBox( self, glpane = self.o )
        
    def _addElementChooserGroupBox(self):
        """
        Add the 'Element Chooser' groupbox. 
        """
        if not self.previewGroupBox:
            return
        
        elementViewer = self.previewGroupBox.elementViewer
        self.elementChooser = \
            PM_ElementChooser( self,  elementViewer = elementViewer)
    
    def _addBondToolsGroupBox(self):
        """
        Add the 'Bond Tools' groupbox.
        """
        self.bondToolsGroupBox = \
            PM_GroupBox( self, title = "Bond Tools")
        
        self._loadBondToolsGroupBox(self.bondToolsGroupBox)
     
    def _addAdvancedOptionsGroupBox(self):
        """
        Add 'Advanced Options' groupbox
        """
        self.advancedOptionsGroupBox = \
            PM_GroupBox( self, title = "Advanced Options" )  
        
        self._loadAdvancedOptionsGroupBox(self.advancedOptionsGroupBox)
 
    def _loadAdvancedOptionsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Advanced Options group box.
        @param inPmGroupBox: The Advanced Options box in the PM
        @type  inPmGroupBox: L{PM_GroupBox} 
        """
        
        self.selectionFilterCheckBox = \
            PM_CheckBox( inPmGroupBox,
                         text  = "Enable selection filter",
                         widgetColumn = 0,
                         state        = Qt.Unchecked  )
        self.selectionFilterCheckBox.setDefaultValue(False)
        
        self.filterlistLE = PM_LineEdit( inPmGroupBox, 
                                         label        = "",
                                         text         = "",
                                         setAsDefault = False,
                                         spanWidth    = True )
        self.filterlistLE.setReadOnly(True)            
        
        if self.selectionFilterCheckBox.isChecked():
            self.filterlistLE.setEnabled(True)
        else:
            self.filterlistLE.setEnabled(False)
                    
        self.autoBondCheckBox = PM_CheckBox( inPmGroupBox,
                                              text         = 'Auto Bond',
                                              widgetColumn = 0,
                                              state        = Qt.Checked  )
        
        self.waterCheckBox = PM_CheckBox( inPmGroupBox,
                                          text         = "Water",
                                          widgetColumn = 0,
                                          state        = Qt.Unchecked  )
        
        self.highlightingCheckBox = PM_CheckBox( inPmGroupBox,
                                                 text         = "Highlighting",
                                                 widgetColumn = 0,
                                                 state        = Qt.Checked )
        
    def _loadBondToolsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Bond Tools group box.
        @param inPmGroupBox: The Bond Tools box in the PM
        @type  inPmGroupBox: L{PM_GroupBox}        
        """
        # Button list to create a toolbutton row.
        # Format: 
        # - buttonId, 
        # - buttonText , 
        # - iconPath
        # - tooltip
        # - shortcut
        # - column
        BOND_TOOL_BUTTONS = \
                          [ ( "QToolButton", 0,  "SINGLE",    "", "", None, 0),
                            ( "QToolButton", 1,  "DOUBLE",    "", "", None, 1),
                            ( "QToolButton", 2,  "TRIPLE",    "", "", None, 2),
                            ( "QToolButton", 3,  "AROMATIC",  "", "", None, 3),
                            ( "QToolButton", 4,  "GRAPHITIC", "", "", None, 4),
                            ( "QToolButton", 5,  "CUTBONDS",  "", "", None, 5)
                          ]
                        
            
        self.bondToolButtonRow = \
            PM_ToolButtonRow( 
                inPmGroupBox, 
                title        = "",
                buttonList   = BOND_TOOL_BUTTONS,
                checkedId    = 0,
                setAsDefault = True )