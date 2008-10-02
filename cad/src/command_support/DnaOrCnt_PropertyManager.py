# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaOrCnt_PropertyManager.py

DnaOrCnt_PropertyManager class provides common functionality (e.g. groupboxes 
etc) to the subclasses that define various Dna and Cnt (Carbon nanotube) 
Property Managers. 

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created on 2008-05-20

TODO:
- Need a better name for this class? 
- The Reference list widget and related code (added on 2008-06-24) supports 
  the feature in insert dna/cnt commands, where you can specify a reference 
   plane on which the structure will be placed. The ui elelment allows adding
   /deleting this plane. Implementing this is not straightforward. 
   It needs specific code in PM, GM and command classes. Need some core internal 
   features that allow easy creation and handling of such ui. (Similar issue 
   can be seen in the MakeCrossOvers or MultipleDnaSegmentResize commands where
   special code is needed to add or remove segments from the list. 
   [-- Ninad 2008-06-24 comment]
"""
from PyQt4.Qt              import Qt, SIGNAL
from PM.PM_CheckBox        import PM_CheckBox
from PM.PM_PrefsCheckBoxes import PM_PrefsCheckBoxes
from PM.PM_SelectionListWidget import PM_SelectionListWidget
from PM.PM_RadioButtonList     import PM_RadioButtonList
from utilities.constants       import lightgreen_2

from command_support.EditCommand_PM import EditCommand_PM

from PM.PM_ColorChooser import PM_ColorChooser
from PM.PM_ColorComboBox import PM_ColorComboBox

_superclass = EditCommand_PM
class DnaOrCnt_PropertyManager(EditCommand_PM):
    """
    DnaOrCnt_PropertyManager class provides common functionality 
    (e.g. groupboxes etc) to the subclasses that define various Dna and Cnt
    (Carbon nanotube) Property Managers. 
    @see: DnaSegment_PropertyManager (subclass)
    @see: DnaDuplexPropertyManager (subclass)
    """

    def __init__( self, command ):
        """
        Constructor for the DNA Duplex property manager.
        """
        
        self._cursorTextGroupBox = None
        self._colorChooser     = None
        self.showCursorTextCheckBox = None
        self.referencePlaneListWidget = None
        
        
        #For model changed signal
        #@see: self.model_changed() and self._current_model_changed_params 
        #for example use
        self._previous_model_changed_params = None


        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False
        

        _superclass.__init__( self, command)

        
    def show(self):
        """
        Show this PM
	"""
        _superclass.show(self)
        
        if isinstance(self.showCursorTextCheckBox, PM_CheckBox):
            self._update_state_of_cursorTextGroupBox(
                    self.showCursorTextCheckBox.isChecked())


    def _loadDisplayOptionsGroupBox(self, pmGroupBox):
        """
        Load widgets in the Display Options GroupBox
        """
        self._loadCursorTextGroupBox(pmGroupBox)
        
    def _loadColorChooser(self, pmGroupBox):
        self._colorChooser = PM_ColorComboBox(pmGroupBox)
        
            
    def _loadCursorTextGroupBox(self, pmGroupBox):
        """
        Load various checkboxes within the cursor text groupbox. 
        @see: self. _loadDisplayOptionsGroupBox()
        @see: self._connect_showCursorTextCheckBox()
        @see: self._params_for_creating_cursorTextCheckBoxes()
        """
        self.showCursorTextCheckBox = \
            PM_CheckBox( 
                pmGroupBox,
                text  = "Show cursor text",
                widgetColumn = 0,
                state        = Qt.Checked)

        self._connect_showCursorTextCheckBox()

        paramsForCheckBoxes = self._params_for_creating_cursorTextCheckBoxes()

        self._cursorTextGroupBox = PM_PrefsCheckBoxes(
            pmGroupBox, 
            paramsForCheckBoxes = paramsForCheckBoxes,            
            title = 'Cursor text options:')
        
    def connect_or_disconnect_signals(self, isConnect):
        
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
        
        if self._colorChooser:
            change_connect(self._colorChooser, 
                           SIGNAL("editingFinished()"), 
                           self._changeStructureColor)

        pass
    

    def _connect_showCursorTextCheckBox(self):
        """
        Connect the show cursor text checkbox with user prefs_key.
        Subclasses should override this method. The default implementation 
        does nothing. 
        """
        pass

    def _params_for_creating_cursorTextCheckBoxes(self):
        """
        Subclasses should override this method. The default implementation 
        returns an empty list.
        Returns params needed to create various cursor text checkboxes connected
        to prefs_keys  that allow custom cursor texts. 
        @return: A list containing tuples in the following format:
                ('checkBoxTextString' , preference_key). PM_PrefsCheckBoxes 
                uses this data to create checkboxes with the the given names and
                connects them to the provided preference keys. (Note that 
                PM_PrefsCheckBoxes puts thes within a GroupBox)
        @rtype: list
        @see: PM_PrefsCheckBoxes
        @see: self._loadDisplayOptionsGroupBox where this list is used. 
        #see: self._loadCursorTextGroupBox()
        @see: subclass method: 
        DnaSegment_PropertyManager._params_for_creating_cursorTextCheckBoxes()
        """
        params = [] #Format: (" checkbox text", prefs_key)

        return params
    
    
    def _update_state_of_cursorTextGroupBox(self, enable):
        """
        """
        if not isinstance(self._cursorTextGroupBox, PM_PrefsCheckBoxes):
            return
        
        if enable:
            self._cursorTextGroupBox.setEnabled(True)
        else:
            self._cursorTextGroupBox.setEnabled(False)
            
            
    def _loadReferencePlaneGroupBox(self, pmGroupBox):
        """
        Load widgets in reference plane groupbox
        @see: DnaDuplexPropertyManager._addGroupBoxes where this groupbox 
        is added. 
        """
        # Placement Options radio button list to create radio button list.
        # Format: buttonId, buttonText, tooltip
        PLACEMENT_OPTIONS_BUTTON_LIST = [ \
            ( 0, "Parallel to screen (default)",     "Parallel to screen"     ),
            ( 1, "On the specified plane:", "On specified plane" )]

        
        self._placementOptions = \
            PM_RadioButtonList( pmGroupBox,
                                ##label      = "Duplex Placement Options:", 
                                buttonList = PLACEMENT_OPTIONS_BUTTON_LIST,
                                checkedId  = 0, 
                                spanWidth = True,
                                borders = False)
        
        self._specifyReferencePlane_radioButton = self._placementOptions.getButtonById(1)
        
        self.referencePlaneListWidget = PM_SelectionListWidget(
            pmGroupBox,
            self.win,
            label = "",
            heightByRows = 2)
        
    def useSpecifiedDrawingPlane(self):
        """
        Tells if the the command (rather the graphicsmode) should use the user 
        specified drawing plane on which the structure (such as dna duplex or 
        CNT) will be created. 
        
        Returns True if a Palne is specified by the user AND 'use specified 
        plane' radio button in the Property manager is checked. 
        
        @see: DnaDuplex_GraphicsMode.getDrawingPlane()
        """
        if self.referencePlaneListWidget is None:
            return False
        
        if self._specifyReferencePlane_radioButton.isChecked():
            itemDict = self.referencePlaneListWidget.getItemDictonary()
            planeList = itemDict.values()            
            if len(planeList) == 1:
                return True
            
        return False
    
    def activateSpecifyReferencePlaneTool(self, index):
        """
        Slot method that changes the appearance of some ui elements, suggesting
        that the Specify reference plane tool is active.
        @see: self.isSpecifyPlaneToolActive()
        """        
        if self.referencePlaneListWidget is None:
            return
        
        if index == 0:
            self.referencePlaneListWidget.resetColor()            
        else:
            itemDict = self.referencePlaneListWidget.getItemDictonary()
            planeList = itemDict.values()            
            if len(planeList) == 0:                
                self.referencePlaneListWidget.setColor(lightgreen_2) 
            else:
                self.referencePlaneListWidget.resetColor()
        
    def isSpecifyPlaneToolActive(self): 
        """
        Returns True if the add segments tool (which adds the segments to the 
        list of segments) is active
        @see: DnaDuplex_EditCommand.isSpecifyPlaneToolActive()
        @see: DnaDuplex_GraphicsMode.isSpecifyPlaneToolActive()
        @see: DnaDuplex_GraphicsMode.jigLeftUp()
        """
        if self.referencePlaneListWidget is None:
            return False
           
        if self._specifyReferencePlane_radioButton.isChecked():
            itemDict = self.referencePlaneListWidget.getItemDictonary()
            planeList = itemDict.values()
            
            if len(planeList) == 1:
                return False            
            else:
                return True
   
        return False
    
    def removeListWidgetItems(self):
        """
        Removes all the items in the list widget 
        @TODO: At the moment the list widget means 'self.referencePlaneListWidget'
         the method name needs renaming if there are some more list widgets 
         in the Property manager.
        """
        if self.referencePlaneListWidget is None:
            return
        
        self.referencePlaneListWidget.insertItems(
            row = 0,
            items = ())
        self.referencePlaneListWidget.setColor(lightgreen_2)
    
    def updateReferencePlaneListWidget(self, plane = None):
        """
        Update the reference plane list widget by replacing the 
        current item (if any) with the specified <plane >. This plane object 
        (if not None) will be used as a referecne plane on which the structure 
        will be constructed. 
        
        @param plane: Plane object to be         
        """   
        if self.referencePlaneListWidget is None:
            return
        
        planeList = [ ]
        
        if plane is not None:
            planeList = [plane]
               
        self.referencePlaneListWidget.insertItems(
            row = 0,
            items = planeList)
        
    def listWidgetHasFocus(self):
        """
        Checkes if the list widget that lists the referecne plane, on which 
        the dna will be created, has the Qt focus. This is used to just remove 
        items from the list widget (without actually 'deleting' the 
        corresponding Plane in the GLPane)
        @see: DnaDuplex_GraphicsMode.keyPressEvent() where this is called
        """
        if self.referencePlaneListWidget and \
           self.referencePlaneListWidget.hasFocus():
            return True  
        
        return False   
    
    
    def _changeStructureColor(self):
        """
        """
        if self._colorChooser is None:
            return
        
        if self.command and self.command.hasValidStructure():
            color = self._colorChooser.getColor()
            if hasattr(self.command.struct, 'setColor'):
                self.command.struct.setColor(color)
                self.win.glpane.gl_update()
            

