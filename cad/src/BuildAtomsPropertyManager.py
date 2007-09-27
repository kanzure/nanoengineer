# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildAtomsPropertyManager.py

The BuildAtomsPropertyManager class provides the Property Manager for the
B{Build Atoms mode}.  The UI is defined in L{Ui_BuildAtomsPropertyManager}
    
@author: Bruce, Huaicai, Mark, Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:
Before Alpha9, (code that used Qt3 framework) Build Atoms mode had a 
'Molecular Modeling Kit' (MMKit) and a dashboard. Starting Alpha 9,
this functionality was integrated into a Property Manager. Since then 
several changes have been made. 
ninad 2007-08-29: Created to use PM module classes, thus deprecating old 
                  Property Manager class MMKit. Split out old 'clipboard' 
                  functionality into new L{PasteMode} 
"""


import env

from PyQt4.Qt import SIGNAL
from Ui_BuildAtomsPropertyManager import Ui_BuildAtomsPropertyManager
from bond_constants               import btype_from_v6
from VQT import V
from state_utils import same_vals

NOBLEGASES = ["He", "Ne", "Ar", "Kr"]

class BuildAtomsPropertyManager(Ui_BuildAtomsPropertyManager):
    """
    The BuildAtomsPropertyManager class provides the Property Manager for the
    B{Build Atoms mode}.  The UI is defined in L{Ui_BuildAtomsPropertyManager}
    """
    
    def __init__(self, parentMode):
        """
        Constructor for the B{Build Atoms} property manager.
        
        @param parentMode: The parent mode where this Property Manager is used
        @type  parentMode: L{depositMode} 
        """
        Ui_BuildAtomsPropertyManager.__init__(self, parentMode)
        
        self.w = self.parentMode.w
        self.win = self.parentMode.w
        self.pw = self.parentMode.pw
        
        self._addGroupBoxes()
        self.updateMessage()
        
        self.previousSelectionParams = None
        
    def ok_btn_clicked(self):
        """
        Calls MainWindow.toolsDone to exit the current mode. 
        @attention: this method needs to be renamed. (this should be done in 
        PM_Dialog)
        """
        self.w.toolsDone()
    
    def connect_or_disconnect_signals(self, isConnect): 
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        @see: L{depositMode.connect_or_disconnect_signals} where this is called
        """
        
        if isConnect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
            
        change_connect(self.waterCheckBox,
                        SIGNAL("toggled(bool)"),
                        self.parentMode.setWater)
        
        change_connect(self.highlightingCheckBox,
                        SIGNAL("toggled(bool)"),
                        self.parentMode.set_hoverHighlighting)
        
        change_connect(self.selectionFilterCheckBox,
                       SIGNAL("stateChanged(int)"),
                       self.set_selection_filter)
        
        change_connect(self.xCoordOfSelectedAtom,
                     SIGNAL("valueChanged(double)"), 
                     self._moveSelectedAtom)
        
        change_connect(self.yCoordOfSelectedAtom,
                     SIGNAL("valueChanged(double)"), 
                     self._moveSelectedAtom)
        
        change_connect(self.zCoordOfSelectedAtom,
                     SIGNAL("valueChanged(double)"), 
                     self._moveSelectedAtom)
            
    
    def model_changed(self):
        """
        Overrides basicMode.model_changed. 
        @WARNING: Ideally this property manager should implement both
               model_changed and selection_changed methods in the mode API. 
               model_changed method will be used here when the selected atom is 
               dragged, transmuted etc. The selection_changed method will be 
               used when the selection (picking/ unpicking) changes. 
               At present, selection_changed and model_changed methods are 
               called too frequently that it doesn't matter which one you use. 
               Its better to use only a single method for preformance reasons 
               (at the moment). This should change when the original 
               methods in the API are revised to be called at appropiraite 
               time. 
        """  
        newSelectionParams = self._currentSelectionParams()
        
        if same_vals(newSelectionParams, self.previousSelectionParams):
            return
        
        self.previousSelectionParams = newSelectionParams   
        #subclasses of BuildAtomsPM may not define self.selectedAtomPosGroupBox
        #so do the following check.
        if self.selectedAtomPosGroupBox:            
            self._updateSelectedAtomPosGroupBox(newSelectionParams) 
            
    
    def _currentSelectionParams(self):
        """
        Returns a tuple containing current selection parameters. These 
        parameters are then used to decide whether updating widgets
        in this property manager is needed when L{self.model_changed} or 
        L{self.selection_changed} methods are called. In this case, the 
        Seletion Options groupbox is updated when atom selection changes 
        or when the selected atom is moved. 
        @return: A tuple that contains following selection parameters
                   - Total number of selected atoms (int)
                   - Selected Atom if a single atom is selected, else None
                   - Position vector of the single selected atom or None
        @rtype:  tuple
        @NOTE: The method name may be renamed in future. 
        Its possible that there are other groupboxes in the PM that need to be 
        updated when something changes in the glpane.        
        """
        selectedAtomsList = self.win.assy.getOnlyAtomsSelectedByUser()
        if len(selectedAtomsList) == 1: 
            selectedAtom = selectedAtomsList[0]
            posn = selectedAtom.posn()
            return (len(selectedAtomsList), selectedAtom, posn)
        elif len(selectedAtomsList) > 1:
            return (len(selectedAtomsList), None, None)
        else: 
            return (None, None, None)
        

    def set_selection_filter(self, enabled):
        """
        Slot for Atom Selection Filter checkbox that enables or diables the 
        selection filter and updates the cursor.
        @param enabled: Checked state of L{self.selectionFilterStateBox}
                        If checked, the selection filter will be enabled
        @type  enabled: bool
        @see: L{self.update_selection_filter_list}      
        """
        
        if enabled != self.w.selection_filter_enabled:
            if enabled:
                env.history.message("Atom Selection Filter enabled.")
            else:
                env.history.message("Atom Selection Filter disabled.")
        
        self.w.selection_filter_enabled = enabled
        
        self.filterlistLE.setEnabled(enabled)   
        self.update_selection_filter_list()     
        self.parentMode.update_cursor()
        
    def update_selection_filter_list(self):
        """
        Adds/removes the element selected in the Element Chooser to/from Atom 
        Selection Filter based on what modifier key is pressed (if any).
        @see: L{self.set_selection_filter}
        @see: L{self.update_selection_filter_list_widget}
        """
        #Don't update the filter list if selection filter checkbox is not active
        if not self.filterlistLE.isEnabled():
            self.w.filtered_elements = []
            self.update_selection_filter_list_widget()
            return
        
        element = self.elementChooser.element        
        if self.o.modkeys is None:
            self.w.filtered_elements = []
            self.w.filtered_elements.append(element)
        if self.o.modkeys == 'Shift':
            if not element in self.w.filtered_elements[:]:
                self.w.filtered_elements.append(element)
        elif self.o.modkeys == 'Control':
            if element in self.w.filtered_elements[:]:
                self.w.filtered_elements.remove(element)
                
        self.update_selection_filter_list_widget()
        
    def update_selection_filter_list_widget(self):
        """
        Updates the list of elements displayed in the Atom Selection Filter 
        List. 
        
        @see: L{self.update_selection_filter_list}. (Should only be called 
              from this method)
        """
        
        filtered_syms = ''
        for e in self.w.filtered_elements[:]:
            if filtered_syms: 
                filtered_syms += ", "
            
            filtered_syms += e.symbol
            
        self.filterlistLE.setText(filtered_syms)
                
    def updateMessage(self):
        """
        Updates the message box with an informative message based on the 
        current page and current selected atom type.
        """
        msg = ""
        element = self.elementChooser.element
        
        if self.elementChooser.isVisible():
            msg = "Double click in empty space to insert a single " \
                + element.name + " atom. "
            if not element.symbol in NOBLEGASES:
                msg += "Click on an atom's <i>red bondpoint</i> to attach a " \
                    + element.name + " atom to it."       
        else: # Bonds Tool is selected
            if self.parentMode.cutBondsAction.isChecked():
                msg = "<b> Cut Bonds </b> tool is active. \
                Click on bonds in order to delete them."
                self.MessageGroupBox.insertHtmlMessage(msg)
                return          
            if not hasattr(self.parentMode, 'bondclick_v6'): 
                return
            if self.parentMode.bondclick_v6:
                name = btype_from_v6(self.parentMode.bondclick_v6)
                msg = "Click bonds or bondpoints to make them %s bonds." % name 
            
        # Post message.
        self.MessageGroupBox.insertHtmlMessage(msg)
    
    def update_clipboard_items(self):
        """
        Do nothing. Subclasses should override this method. 
        @see: L{PasteMode.update_clipboard_items} for an example. 
        """
        #TODO: Need further clean up of depositMode.py that will make this 
        #unnecessary
        pass   
    
    
    def _updateSelectedAtomPosGroupBox(self, selectionParams):
        """
        Update the Selected Atoms Position groupbox present withn the 
        B{Selection GroupBox" of this PM. This groupbox shows the 
        X, Y, Z coordinates of the selected atom (if any). 
        This groupbox is updated whenever selection in the glpane changes 
        or a single atom is moved. This groupbox is enabled only when exactly
        one atom in the glpane is selected. 
        @param selectionParams: A tuple that provides following selection 
                               parameters
                                 - Total number of selected atoms (int)
                                 - Selected Atom if a single atom is selected, 
                                   else None
                                 - Position vector of the single selected atom 
                                   or None
        @type: tuple 
        @see: L{self._currentSelectionParams}
        @see: L{self.model_changed}
        
        """
        totalAtoms, selectedAtom, atomPosn = selectionParams
        
        text = ""
        if totalAtoms == 1:
            self.selectedAtomPosGroupBox.setEnabled(True)
            text = str(selectedAtom.getInformationString())
            text += " (" + str(selectedAtom.element.name) + ")"
            self._updateAtomPosSpinBoxes(atomPosn)                       
        elif totalAtoms > 1:
            self.selectedAtomPosGroupBox.setEnabled(False)
            text = "Multiple atoms selected"
        else:
            self.selectedAtomPosGroupBox.setEnabled(False)
            text = "No Atom selected"
        
        if self.selectedAtomLineEdit:
            self.selectedAtomLineEdit.setText(text)
    
    def _moveSelectedAtom(self):
        """
        Move the selected atom position based on the value in the X, Y, Z 
        coordinate spinboxes in the Selection GroupBox. 
        """
        
        selectedAtomsList = self.win.assy.getOnlyAtomsSelectedByUser()
        
        if not len(selectedAtomsList) == 1:
            return

        selectedAtom = selectedAtomsList[0]
        xPos= self.xCoordOfSelectedAtom.value()
        yPos = self.yCoordOfSelectedAtom.value()
        zPos = self.zCoordOfSelectedAtom.value()        
        newPosition = V(xPos, yPos, zPos)
        selectedAtom.setposn(newPosition)
        self.o.gl_update()
        
    def _updateAtomPosSpinBoxes(self, atomCoords):
        """
        Updates the X, Y, Z values in the Selection Options Groupbox. This
        method is called whenever the selected atom in the glpane is dragged.
        @param atomCoords: X, Y, Z coordinate position vector
        @type  atomCoords: Vector
        """
        self.xCoordOfSelectedAtom.setValue(atomCoords[0])
        self.yCoordOfSelectedAtom.setValue(atomCoords[1])
        self.zCoordOfSelectedAtom.setValue(atomCoords[2])     
        
 
        