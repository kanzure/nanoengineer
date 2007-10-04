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
        
        self.previousSelectionParams = None
                
        self._addGroupBoxes()
                
        # It is essential to make the following flag 'True' instead of False. 
        # Program enters self._moveSelectedAtom method first after init, and 
        # there and this flag ensures that it returns from that method 
        # immediately. It is not clear why self.model_changed is not called 
        # before the it enters that method. This flag may not be needed after
        # implementing connectWithState. 
        self.model_changed_from_glpane = True
        
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
        
        change_connect(self.atomChooserComboBox, 
                     SIGNAL("currentIndexChanged(int)"), 
                     self._updateAtomChooserGroupBoxes)
            
        change_connect(self.waterCheckBox,
                        SIGNAL("toggled(bool)"),
                        self.parentMode.setWater)
        
        change_connect(self.highlightingCheckBox,
                        SIGNAL("toggled(bool)"),
                        self.parentMode.set_hoverHighlighting)
        
        change_connect(self.selectionFilterCheckBox,
                       SIGNAL("stateChanged(int)"),
                       self.set_selection_filter)
        
        change_connect(self.showSelectedAtomInfoCheckBox,
                       SIGNAL("stateChanged(int)"),
                       self.toggle_selectedAtomPosGroupBox)
        
        
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
        
        #use selected atom dictionary which is already made by assy. 
        #use this dict for length tests below. Don't create list from this 
        #dict yet as that would be a slow operation to do at this point. 
        selectedAtomsDictionary = self.win.assy.selatoms
        
        if len(selectedAtomsDictionary) == 1: 
            #self.win.assy.selatoms_list() is same as 
            # selectedAtomsDictionary.values() except that it is a sorted list 
            #it doesn't matter in this case, but a useful info if we decide 
            # we need a sorted list for multiple atoms in future. 
            # -- ninad 2007-09-27 (comment based on Bruce's code review)
            selectedAtomList = self.win.assy.selatoms_list()
            selectedAtom = selectedAtomList[0]
            posn = selectedAtom.posn()
            return (len(selectedAtomsDictionary), selectedAtom, posn)
        elif len(selectedAtomsDictionary) > 1:
            #All we are interested in, is to check if multiple atoms are 
            #selected. So just return a number greater than 1. This makes sure
            #that parameter difference test in  self.model_changed doesn't
            # succeed much more often (i.e. whenever user changes the number of 
            # selected atoms, but still keeping that number > 1
            aNumberGreaterThanOne = 2
            return (aNumberGreaterThanOne, None, None)
        else: 
            return (0, None, None)
        
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
        if not self.elementChooser:
            return
        
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
            self.enable_or_disable_selectedAtomPosGroupBox(bool_enable = True)
            text = str(selectedAtom.getInformationString())
            text += " (" + str(selectedAtom.element.name) + ")"
            self._updateAtomPosSpinBoxes(atomPosn)                       
        elif totalAtoms > 1:
            self.enable_or_disable_selectedAtomPosGroupBox(bool_enable = False)
            text = "Multiple atoms selected"
        else:
            self.enable_or_disable_selectedAtomPosGroupBox(bool_enable = False)
            text = "No Atom selected"
        
        if self.selectedAtomLineEdit:
            self.selectedAtomLineEdit.setText(text)
    
    def _moveSelectedAtom(self, spinBoxValueJunk = None):
        """
        Move the selected atom position based on the value in the X, Y, Z 
        coordinate spinboxes in the Selection GroupBox. 
        @param spinBoxValueJunk: This is the Spinbox value from the valueChanged
                                 signal. It is not used. We just want to know
                                 that the spinbox value has changed.
        @type  spinBoxValueJunk: double or None           
        """
                
        if self.model_changed_from_glpane:
            #Model is changed from glpane ,do nothing. Fixes bug 2545
            return
        
        totalAtoms, selectedAtom, atomPosn_junk = self._currentSelectionParams()
    
        if not totalAtoms == 1:
            return
        
        #@NOTE: This is important to determine baggage and nobaggage atoms. 
        #Otherwise the bondpoints won't move! See also:
        # selectMode.atomSetup where this is done. 
        # But that method gets called only when during atom left down. 
        #Its not useful here as user may select that atom using selection lasso
        #or using other means (ctrl + A if only one atom is present) . Also, 
        #the lists parentMode.baggage and parentMode.nonbaggage seem to get 
        #cleared during left up. So that method is not useful. 
        #There needs to be a method in parentmode (selectMode or depositMode) 
        #to do the following (next code cleanup?) -- ninad 2007-09-27
        self.parentMode.baggage, self.parentMode.nonbaggage = \
            selectedAtom.baggage_and_other_neighbors()          
        
        xPos= self.xCoordOfSelectedAtom.value()
        yPos = self.yCoordOfSelectedAtom.value()
        zPos = self.zCoordOfSelectedAtom.value()        
        newPosition = V(xPos, yPos, zPos)
        delta = newPosition - selectedAtom.posn()
        
        #Don't do selectedAtom.setposn()  because it needs to handle 
        #cases where atom has bond points and/or monovalent atoms . It also 
        #needs to modify the neighboring atom baggage. This is already done in
        #the following method in parentMode so use that. 
        self.parentMode.drag_selected_atom(selectedAtom, delta)
        
        self.o.gl_update()
        
    def _updateAtomPosSpinBoxes(self, atomCoords):
        """
        Updates the X, Y, Z values in the Selection Options Groupbox. This
        method is called whenever the selected atom in the glpane is dragged.
        @param atomCoords: X, Y, Z coordinate position vector
        @type  atomCoords: Vector
        """
        self.model_changed_from_glpane = True
        self.xCoordOfSelectedAtom.setValue(atomCoords[0])
        self.yCoordOfSelectedAtom.setValue(atomCoords[1])
        self.zCoordOfSelectedAtom.setValue(atomCoords[2])  
        self.model_changed_from_glpane = False
    
    