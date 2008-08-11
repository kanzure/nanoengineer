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
                  Split out old 'clipboard' functionality into new L{PasteFromClipboard_Command}

"""

from PyQt4.Qt import Qt

from PM.PM_Dialog          import PM_Dialog
from PM.PM_GroupBox        import PM_GroupBox
from PM.PM_CheckBox        import PM_CheckBox
from PM.PM_ComboBox        import PM_ComboBox
from PM.PM_LineEdit        import PM_LineEdit
from PM.PM_DoubleSpinBox   import PM_DoubleSpinBox

from PM.PM_CoordinateSpinBoxes import PM_CoordinateSpinBoxes
from PM.PM_ToolButtonRow       import PM_ToolButtonRow

from PM.PM_ElementChooser      import PM_ElementChooser
from PM.PM_PAM5_AtomChooser    import PM_PAM5_AtomChooser
from PM.PM_PAM3_AtomChooser    import PM_PAM3_AtomChooser
from PM.PM_PreviewGroupBox     import PM_PreviewGroupBox

from PM.PM_Constants       import PM_DONE_BUTTON
from PM.PM_Constants       import PM_WHATS_THIS_BUTTON

from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

import foundation.env as env
from utilities.prefs_constants import reshapeAtomsSelection_prefs_key


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
    iconPath = "ui/actions/Tools/Build Structures/Build Chunks.png"
    
    def __init__(self, command):
        """
        Constructor for the B{Build Atoms} property manager class that defines 
        its UI.
        
        @param command: The parent mode where this Property Manager is used
        @type  command: L{depositMode}        
        """
        self.command = command
        self.w = self.command.w
        self.win = self.command.w
        self.pw = self.command.pw        
        self.o = self.win.glpane 
        
        
        self.previewGroupBox = None
        self.regularElementChooser = None
        self.PAM5Chooser = None
        self.PAM3Chooser = None
        self.elementChooser = None
        self.advancedOptionsGroupBox = None
        self.bondToolsGroupBox = None
        
        self.selectionFilterCheckBox = None
        self.filterlistLE = None
        self.selectedAtomInfoLabel = None
        
        #Initialize the following to None. (subclasses may not define this)
        #Make sure you initialize it before adding groupboxes!
        self.selectedAtomPosGroupBox = None
        self.showSelectedAtomInfoCheckBox = None
        
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)
        
        self.showTopRowButtons(PM_DONE_BUTTON | PM_WHATS_THIS_BUTTON)        
        msg = ''
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)

    def _addGroupBoxes(self):
        """
        Add various group boxes to the Build Atoms Property manager. 
        """
        self._addPreviewGroupBox()  
        self._addAtomChooserGroupBox()
        self._addBondToolsGroupBox() 
        
        #@@@TODO HIDE the bonds tool groupbox initially as the 
        #by default, the atoms tool is active when BuildAtoms command is 
        #finist invoked. 
        self.bondToolsGroupBox.hide()        
        
        self._addSelectionOptionsGroupBox()        
        self._addAdvancedOptionsGroupBox()       
       
    def _addPreviewGroupBox(self):
        """
        Adde the preview groupbox that shows the element selected in the 
        element chooser. 
        """
        self.previewGroupBox = PM_PreviewGroupBox( self, glpane = self.o )
    
    def _addAtomChooserGroupBox(self):
        """
        Add the Atom Chooser groupbox. This groupbox displays one of the 
        following three groupboxes depending on the choice selected in the 
        combobox:
          a) Periodic Table Elements L{self.regularElementChooser}
          b) PAM5 Atoms  L{self.PAM5Chooser}
          c) PAM3 Atoms  L{self.PAM3Chooser}
        @see: L{self.__updateAtomChooserGroupBoxes}
        """
        self.atomChooserGroupBox = \
            PM_GroupBox(self, title = "Atom Chooser")
        self._loadAtomChooserGroupBox(self.atomChooserGroupBox)
        
        self._updateAtomChooserGroupBoxes(currentIndex = 0)

    def _addElementChooserGroupBox(self, inPmGroupBox):
        """
        Add the 'Element Chooser' groupbox. (present within the 
        Atom Chooser Groupbox) 
        """
        if not self.previewGroupBox:
            return
        
        elementViewer = self.previewGroupBox.elementViewer
        self.regularElementChooser = \
            PM_ElementChooser( inPmGroupBox,  
                               parentPropMgr = self,
                               elementViewer = elementViewer)
        
    
    def _add_PAM5_AtomChooserGroupBox(self, inPmGroupBox):
        """
        Add the 'PAM5 Atom Chooser' groupbox (present within the 
        Atom Chooser Groupbox) 
        """
        if not self.previewGroupBox:
            return
        
        elementViewer = self.previewGroupBox.elementViewer
        self.PAM5Chooser = \
            PM_PAM5_AtomChooser( inPmGroupBox,
                                 parentPropMgr = self,
                                 elementViewer = elementViewer)
    
    def _add_PAM3_AtomChooserGroupBox(self, inPmGroupBox):
        """
        Add the 'PAM3 Atom Chooser' groupbox (present within the 
        Atom Chooser Groupbox)
        """
        if not self.previewGroupBox:
            return
        
        elementViewer = self.previewGroupBox.elementViewer
        self.PAM3Chooser = \
            PM_PAM3_AtomChooser( inPmGroupBox, 
                                 parentPropMgr = self,
                                 elementViewer = elementViewer)
        
    def _hideAllAtomChooserGroupBoxes(self):        
        """
        Hides all Atom Chooser group boxes.
        """
        if self.regularElementChooser:
            self.regularElementChooser.hide()
        if self.PAM5Chooser:
            self.PAM5Chooser.hide()
        if self.PAM3Chooser:
            self.PAM3Chooser.hide()
        
    def _addBondToolsGroupBox(self):
        """
        Add the 'Bond Tools' groupbox.
        """
        self.bondToolsGroupBox = \
            PM_GroupBox( self, title = "Bond Tools")
        
        self._loadBondToolsGroupBox(self.bondToolsGroupBox)
    
    def _addSelectionOptionsGroupBox(self):
        """
        Add 'Selection Options' groupbox
        """
        self.selectionOptionsGroupBox = \
            PM_GroupBox( self, title = "Selection Options" )  
        
        self._loadSelectionOptionsGroupBox(self.selectionOptionsGroupBox)
    
    def _loadAtomChooserGroupBox(self, inPmGroupBox):
        """
        Load the widgets inside the Atom Chooser groupbox.
        @param inPmGroupBox: The Atom Chooser box in the PM
        @type  inPmGroupBox: L{PM_GroupBox} 
        """
        atomChooserChoices = [ "Periodic Table Elements", 
                             "PAM5 Atoms", 
                             "PAM3 Atoms" ]
        
        self.atomChooserComboBox = \
            PM_ComboBox( inPmGroupBox,
                         label        = '', 
                         choices      = atomChooserChoices, 
                         index        = 0, 
                         setAsDefault = False,
                         spanWidth    = True )
        
        #Following fixes bug 2550  
        self.atomChooserComboBox.setFocusPolicy(Qt.NoFocus)
        
        self._addElementChooserGroupBox(inPmGroupBox) 
        self._add_PAM5_AtomChooserGroupBox(inPmGroupBox)
        self._add_PAM3_AtomChooserGroupBox(inPmGroupBox)
        
    def _loadSelectionOptionsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Selection Options group box.
        @param inPmGroupBox: The Selection Options box in the PM
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
        
        self.showSelectedAtomInfoCheckBox = \
            PM_CheckBox( 
                inPmGroupBox,
                text  = "Show Selected Atom Info",
                widgetColumn = 0,
                state        = Qt.Unchecked)
        
        self.selectedAtomPosGroupBox = \
            PM_GroupBox( inPmGroupBox, title = "")
        self._loadSelectedAtomPosGroupBox(self.selectedAtomPosGroupBox)
        
        self.toggle_selectedAtomPosGroupBox(show = 0)
        self.enable_or_disable_selectedAtomPosGroupBox( bool_enable = False)
        
        self.reshapeSelectionCheckBox = \
            PM_CheckBox( inPmGroupBox,
                         text         = 'Dragging reshapes selection',
                         widgetColumn = 0,
                         state        = Qt.Unchecked  )
        
        connect_checkbox_with_boolean_pref( self.reshapeSelectionCheckBox, 
                                            reshapeAtomsSelection_prefs_key )
        
        env.prefs[reshapeAtomsSelection_prefs_key] = False
        
        self.waterCheckBox = \
            PM_CheckBox( inPmGroupBox,
                         text         = "Z depth filter (water surface)",
                         widgetColumn = 0,
                         state        = Qt.Unchecked  )

    def _loadSelectedAtomPosGroupBox(self, inPmGroupBox):
        """
        Load the selected Atoms position groupbox It is a sub-gropbox of 
        L{self.selectionOptionsGroupBox)
        @param inPmGroupBox: 'The Selected Atom Position Groupbox'
        @type  inPmGroupBox: L{PM_GroupBox} 
        """
        
        self.selectedAtomLineEdit = PM_LineEdit( inPmGroupBox, 
                                         label        = "Selected Atom:",
                                         text         = "",
                                         setAsDefault = False,
                                         spanWidth    = False )
        
        self.selectedAtomLineEdit.setReadOnly(True) 
        self.selectedAtomLineEdit.setEnabled(False)
        
        self.coordinateSpinboxes = PM_CoordinateSpinBoxes(inPmGroupBox)
    
        # User input to specify x-coordinate 
        self.xCoordOfSelectedAtom  =  self.coordinateSpinboxes.xSpinBox
        # User input to specify y-coordinate 
        self.yCoordOfSelectedAtom  =  self.coordinateSpinboxes.ySpinBox
        # User input to specify z-coordinate 
        self.zCoordOfSelectedAtom  =  self.coordinateSpinboxes.zSpinBox

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
        
        self.autoBondCheckBox = \
            PM_CheckBox( inPmGroupBox,
                         text         = 'Auto bond',
                         widgetColumn = 0,
                         state        = Qt.Checked  )
        
        self.highlightingCheckBox = \
            PM_CheckBox( inPmGroupBox,
                         text         = "Hover highlighting",
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
                checkedId    = None,
                setAsDefault = True )
    
    def _addWhatsThisText(self):
        """
        "What's This" text for widgets in this Property Manager.
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_BuildAtomsPropertyManager
        whatsThis_BuildAtomsPropertyManager(self)
        
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_BuildAtomsPropertyManager
        ToolTip_BuildAtomsPropertyManager(self)
        
    def toggle_selectedAtomPosGroupBox(self, show = 0):
        """
        Show or hide L{self.selectedAtomPosGroupBox} depending on the state of
        the checkbox (L{self.showSelectedAtomInfoCheckBox}) 
        @param show: Flag that shows or hides the groupbox (can have values 
                     0 or 1
        @type  show: int
        """
        if show:
            self.selectedAtomPosGroupBox.show()
        else:
            self.selectedAtomPosGroupBox.hide()
    
    def enable_or_disable_selectedAtomPosGroupBox(self, bool_enable = False):
        """
        Enable or disable Selected AtomPosGroupBox present within 
        'selection options' and also the checkbox that shows or hide this 
        groupbox. These two widgets are enabled when only a single atom is 
        selected from the 3D workspace. 
        @param bool_enable: Flag that enables or disables widgets
        @type  bool_enable: boolean
        """
        if self.showSelectedAtomInfoCheckBox:
            self.showSelectedAtomInfoCheckBox.setEnabled(bool_enable)
        if self.selectedAtomPosGroupBox:
            self.selectedAtomPosGroupBox.setEnabled(bool_enable)
    
    def _updateAtomChooserGroupBoxes(self, currentIndex):
        """
        Updates the Atom Chooser Groupbox. It displays one of the 
        following three groupboxes depending on the choice selected in the 
        combobox:
          a) Periodic Table Elements L{self.regularElementChooser}
          b) PAM5 Atoms  L{self.PAM5Chooser}
          c) PAM3 Atoms  L{self.PAM3Chooser}
        It also sets self.elementChooser to the current active Atom chooser 
        and updates the display accordingly in the Preview groupbox.
        """
        self._hideAllAtomChooserGroupBoxes()
        
        if currentIndex is 0:
            self.elementChooser = self.regularElementChooser
            self.regularElementChooser.show()
        if currentIndex is 1:
            self.elementChooser = self.PAM5Chooser
            self.PAM5Chooser.show()
        if currentIndex is 2:
            self.elementChooser = self.PAM3Chooser
            self.PAM3Chooser.show()
        
        if self.elementChooser:
            self.elementChooser.updateElementViewer()
        
        self.updateMessage()
        
        
    def updateMessage(self):
        """
        Update the Message groupbox with informative message. 
        Subclasses should override this.
        """
        pass
  