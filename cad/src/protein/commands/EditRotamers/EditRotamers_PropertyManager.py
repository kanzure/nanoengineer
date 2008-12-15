# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
EditRotamers_PropertyManager.py

The EditRotamers_PropertyManager class provides a Property Manager 
for the B{Edit Rotamers} command on the flyout toolbar in the 
Build > Protein mode. 

@author: Piotr, Mark
@version: $Id$ 
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

To do:
- Place "Previous AA" and "Next AA" buttons side-by-side.
- Fix bug: Changing Chi angles doesn't update rotamer position in the GA.
- Show residue label in GA of current residue, including AA and # (i.e. SER[14]).
- Better messages, especially when selecting different peptides.
- Include "Show entire model" checkbox in PM (checked by default).
- Add "Number of AA:" field (disabled).
- Include name of the current peptide in the title of the Sequence Editor.
- Sync Residue combobox and sequence editor (or remove one or the other).
- Add wait (hourglass) cursor when changing the display style of proteins.
"""
import os, time, fnmatch, string
import foundation.env as env

from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

from utilities.prefs_constants import getDefaultWorkingDirectory
from utilities.prefs_constants import workingDirectory_prefs_key

from utilities.Log import greenmsg
from utilities.constants import yellow, orange, red, magenta 
from utilities.constants import cyan, blue, white, black, gray
from utilities.constants import diPROTEIN

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4 import QtGui

from PyQt4.Qt import QFileDialog, QString, QMessageBox, QSlider
from PM.PM_PushButton   import PM_PushButton

from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_LineEdit import PM_LineEdit
from PM.PM_StackedWidget import PM_StackedWidget
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_Dial import PM_Dial
from PM.PM_ToolButtonRow import PM_ToolButtonRow
from PM.PM_Slider import PM_Slider
from PM.PM_Constants import PM_DONE_BUTTON
from PM.PM_Constants import PM_WHATS_THIS_BUTTON
from PM.PM_ColorComboBox import PM_ColorComboBox
from PyQt4.Qt import QTextCursor    

from command_support.Command_PropertyManager import Command_PropertyManager

_superclass = Command_PropertyManager
class EditRotamers_PropertyManager(Command_PropertyManager):
    """
    The ProteinDisplayStyle_PropertyManager class provides a Property Manager 
    for the B{Edit Rotamers} command on the Build Protein command toolbar. 
    
    The selected peptide/protein is displayed in the protein reduced display
    style. The user can select individual rotamers and edit their chi angles.
    This is useful for certain types of protein design protocols using a
    3rd party program like Rosetta.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Edit Rotamers"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/BuildProtein/EditRotamers.png"
    
    current_protein  = None # The currently selected peptide.
    previous_protein = None # The last peptide selected.

    
    def __init__( self, command ):
        """
        Constructor for the property manager.
        """
        self.currentWorkingDirectory = env.prefs[workingDirectory_prefs_key]
        
        _superclass.__init__(self, command)
        
        self.sequenceEditor = self.win.createProteinSequenceEditorIfNeeded()
        
        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        return
        
    def connect_or_disconnect_signals(self, isConnect = True):
        
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
        
        change_connect(self.nextAAPushButton,
                       SIGNAL("clicked()"),
                       self._expandNextRotamer)

        change_connect(self.previousAAPushButton,
                       SIGNAL("clicked()"),
                       self._expandPreviousRotamer)
        
        change_connect(self.expandAllPushButton,
                       SIGNAL("clicked()"),
                       self._expandAllRotamers)
        
        change_connect(self.collapseAllPushButton,
                       SIGNAL("clicked()"),
                       self._collapseAllRotamers)
        
        change_connect(self.aminoAcidsComboBox,
                       SIGNAL("activated(int)"),
                       self._aminoAcidChanged)
        return
    
    #==
    
    def update_name_field(self):
        """
        Update the name field showing the name of the currently selected protein.
        clear the combobox list.
        """
        if not self.current_protein:
            self.proteinNameLineEdit.setText("")
        else:
            self.proteinNameLineEdit.setText(self.current_protein.name)
        return
    
    def update_residue_combobox(self):
        """
        Update the residue combobox with the amino acid sequence of the
        currently selected protein. If there is no currently selected protein,
        clear the combobox list.
        """
        
        self.aminoAcidsComboBox.clear()
        
        if not self.current_protein:
            return
        
        aa_list = self.current_protein.protein.get_amino_acid_id_list()
        for j in range(len(aa_list)):
            self.aminoAcidsComboBox.addItem(aa_list[j])
        
        # This doesn't generate a signal (only 'activate' is connected to 
        # slot _aminoAcidChanged).
        self.aminoAcidsComboBox.setCurrentIndex(
            self.current_protein.protein.get_current_amino_acid_index())
        
        # Call the slot explicitly. This is needed to draw the rotamer
        # on top of the reduced model of the current protein.
        # Also see the comments in _update_UI_do_updates().
        self._aminoAcidChanged(
            self.current_protein.protein.get_current_amino_acid_index())
        
        return
    
    def update_sequence_editor(self):
        """
        Update the sequence editor with the peptide sequence of the
        currently selected protein. If there is no currently selected protein,
        clear the combobox list.
        
        @note: This should become the update() method of the sequence editor.
        """
        if not self.current_protein:
            self.sequenceEditor.clear()
            return
        
        sequence = self.current_protein.protein.get_sequence_string()
        structure = self.current_protein.protein.get_secondary_structure_string()
        self.sequenceEditor.setSequenceAndStructure(sequence, structure)
        return
    
    def close(self):
        """
        Closes the Property Manager. Overrides EditCommand_PM.close()
        """
        self.sequenceEditor.hide()
        env.history.statusbar_msg("")
        if self.current_protein:
            self.current_protein.setDisplayStyle(self.previous_protein_display_style)
            self.previous_protein = None
        _superclass.close(self)
        return
    
    def show(self):
        """
        Show the PM. Extends superclass method.
        @note: _update_UI_do_updates() gets called immediately after this and
               updates PM widgets with their correct values/settings.
        """
        _superclass.show(self)
        
        self.updateMessage("Edit...")
        self.sequenceEditor.show()
        env.history.statusbar_msg("")
        return
    
    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self,
                                         title = "Parameters")
        self._loadGroupBox1( self._pmGroupBox1 )

        self._pmGroupBox2 = PM_GroupBox( self,
                                         title = "Rotamer Controls")
        self._loadGroupBox2( self._pmGroupBox2 )
        return


    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        self.proteinNameLineEdit = PM_LineEdit( pmGroupBox,
                                                label = "Name:")
            
        self.aminoAcidsComboBox = PM_ComboBox( pmGroupBox,
                                 label         =  "Current residue:",
                                 setAsDefault  =  False)
        
        self.previousAAPushButton  = \
            PM_PushButton( pmGroupBox,
                         text          =  "Previous AA",
                         setAsDefault  =  True)
        
        self.nextAAPushButton  = \
            PM_PushButton( pmGroupBox,
                         text          =  "Next AA",
                         setAsDefault  =  True)
        
        self.recenterViewCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Re-center view",
                         setAsDefault  =  True,
                         state         =  Qt.Unchecked)
        
        self.lockEditedCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Lock edited rotamers",
                         setAsDefault  =  True,
                         state         =  Qt.Checked)
        
        self.expandAllPushButton  = \
            PM_PushButton( pmGroupBox,
                         text         =  "Expand All",
                         setAsDefault  =  True)
        
        self.collapseAllPushButton  = \
            PM_PushButton( pmGroupBox,
                         text          =  "Collapse All",
                         setAsDefault  =  True)
        return
        
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        self.discreteStepsCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Use discrete steps",
                         setAsDefault  =  True,
                         state         = Qt.Unchecked)
        
        self.chi1Dial  =  \
            PM_Dial( pmGroupBox,
                              label         =  "Chi1:",
                              value         =  0.000,
                              setAsDefault  =  True,
                              minimum       =  -180.0,
                              maximum       =  180.0,
                              wrapping      =  True,
                              suffix        =  "deg",
                              spanWidth = False)
        
        self.chi1Dial.setEnabled(False)

        self.win.connect(self.chi1Dial,
                         SIGNAL("valueChanged(int)"),
                         self._rotateChi1)
        
        self.chi2Dial  =  \
            PM_Dial( pmGroupBox,
                              label         =  "Chi2:",
                              value         =  0.000,
                              setAsDefault  =  True,
                              minimum       =  -180.0,
                              maximum       =  180.0,
                              suffix        =  "deg",
                              spanWidth = False)
        
        self.chi2Dial.setEnabled(False)
        
        self.win.connect(self.chi2Dial,
                         SIGNAL("valueChanged(int)"),
                         self._rotateChi2)
        
        self.chi3Dial  =  \
            PM_Dial( pmGroupBox,
                              label         =  "Chi3:",
                              value         =  0.000,
                              setAsDefault  =  True,
                              minimum       =  -180.0,
                              maximum       =  180.0,
                              suffix        =  "deg",
                              spanWidth = False)
        
        self.chi3Dial.setEnabled(False)

        self.win.connect(self.chi3Dial,
                         SIGNAL("valueChanged(int)"),
                         self._rotateChi3)
        
        self.chi4Dial  =  \
            PM_Dial( pmGroupBox,
                              label         =  "Chi4:",
                              value         =  0.000,
                              setAsDefault  =  True,
                              minimum       =  -180.0,
                              maximum       =  180.0,
                              suffix        =  "deg",
                              spanWidth = False)
        
        self.chi4Dial.setEnabled(False)
        
        self.chi4Dial.hide()
        
        self.win.connect(self.chi4Dial,
                         SIGNAL("valueChanged(double)"),
                         self._rotateChi4)
        return
        
    def _addWhatsThisText( self ):
        
        pass
    
    def _addToolTipText(self):
        
        pass

    def _expandNextRotamer(self):
        """
        Displays the next rotamer in the chain.
        
        @attention: this only works when the GDS is a reduced display style.
        """
        if not self.current_protein:
            return
        
        self.current_protein.protein.traverse_forward()
        self._display_and_recenter()
        self._updateAminoAcidInfo(
            self.current_protein.protein.get_current_amino_acid_index())
        return
    
    def _expandPreviousRotamer(self):
        """
        Displays the previous rotamer in the chain.
        
        @attention: this only works when the GDS is a reduced display style.
        """
        if not self.current_protein:
            return
        
        self.current_protein.protein.traverse_backward()
        self._display_and_recenter()
        self._updateAminoAcidInfo(
            self.current_protein.protein.get_current_amino_acid_index())
        return
        
    def _collapseAllRotamers(self):
        """
        Hides all the rotamers.
        
        @attention: this only works when the GDS is a reduced display style.
        """
        if not self.current_protein:
            return
        
        self.current_protein.protein.collapse_all_rotamers()
        self.win.glpane.gl_update()
        return
    
    def _expandAllRotamers(self):
        """
        Displays all the rotamers.
        
        @attention: this only works when the GDS is a reduced display style.
        """
        if not self.current_protein:
            return
        
        self.current_protein.protein.expand_all_rotamers()
        self.win.glpane.gl_update()
        return
    
    def _display_and_recenter(self):
        """
        Recenter the view on the current amino acid selected in the 
        residue combobox (or the sequence editor).
        """
        if not self.current_protein:
            return
        
        self.current_protein.protein.collapse_all_rotamers()
        current_aa = self.current_protein.protein.get_current_amino_acid()
        
        if current_aa:
            self.current_protein.protein.expand_rotamer(current_aa)
            self._update_chi_angles(current_aa)
            if self.recenterViewCheckBox.isChecked():
                ca_atom = current_aa.get_c_alpha_atom()
                if ca_atom:
                    self.win.glpane.pov = -ca_atom.posn()                            
            
            self.win.glpane.gl_update()
        return
    
    def _update_chi_angles(self, aa):
        """
        """
        angle = aa.get_chi_angle(0)
        if angle:
            self.chi1Dial.setEnabled(True)
            self.chi1Dial.setValue(angle)
        else:
            self.chi1Dial.setEnabled(False)
            self.chi1Dial.setValue(0.0)
        
        angle = aa.get_chi_angle(1)
        if angle:
            self.chi2Dial.setEnabled(True)
            self.chi2Dial.setValue(angle)
        else:
            self.chi2Dial.setEnabled(False)
            self.chi2Dial.setValue(0.0)
        
        angle = aa.get_chi_angle(2)
        if angle:
            self.chi3Dial.setEnabled(True)
            self.chi3Dial.setValue(angle)
        else:
            self.chi3Dial.setEnabled(False)
            self.chi3Dial.setValue(0.0)
        
        angle = aa.get_chi_angle(3)
        if angle:
            self.chi4Dial.setEnabled(True)
            self.chi4Dial.setValue(angle)
        else:
            self.chi4Dial.setEnabled(False)
            self.chi4Dial.setValue(0.0)
        return
    
    def _updateAminoAcidInfo(self, index):
        """
        Update position of Amino Acid combo box.
        """
        self.aminoAcidsComboBox.setCurrentIndex(index)
        return
        
    def _aminoAcidChanged(self, index):
        """
        Slot for the "Current residue" combobox.
        """
        if not self.current_protein:
            return
        
        self.current_protein.protein.set_current_amino_acid_index(index)
        self._display_and_recenter()
        
        #Urmi 20080728: change the cursor position in the sequence editor 
        # when current amino acid in the amino acid combo box is changed
        cursor = self.sequenceEditor.sequenceTextEdit.textCursor()
        if index == -1:
            index = 0
        cursor.setPosition(index, QTextCursor.MoveAnchor)       
        cursor.setPosition(index + 1, QTextCursor.KeepAnchor) 
        self.sequenceEditor.sequenceTextEdit.setTextCursor( cursor )
        return
    
    def _rotateChiAngle(self, chi, angle):
        """
        Rotate around chi1 angle.
        """
        if not self.current_protein:
            return
        
        current_aa = self.current_protein.protein.get_current_amino_acid()
        if current_aa:
            self.current_protein.protein.expand_rotamer(current_aa)
            current_aa.set_chi_angle(chi, angle)
            self.win.glpane.gl_update()

        return
                
    def _rotateChi1(self, angle):
        """
        
        """
        self._rotateChiAngle(0, angle)
        self.chi1Dial.updateValueLabel()
        return
    
    def _rotateChi2(self, angle):
        """
        """
        self._rotateChiAngle(1, angle)
        self.chi2Dial.updateValueLabel()
        return
        
    def _rotateChi3(self, angle):
        """
        """
        self._rotateChiAngle(2, angle)
        self.chi3Dial.updateValueLabel()
        return
        
    def _rotateChi4(self, angle):
        """
        """
        self._rotateChiAngle(3, angle)
        return
   
    def _update_UI_do_updates(self):
        """
        Overrides superclass method. 
        
        @see: Command_PropertyManager._update_UI_do_updates()
        """
        
        self.current_protein = self.win.assy.getSelectedProteinChunk()
        
        if self.current_protein == self.previous_protein:
            print "_update_UI_do_updates(): DO NOTHING."
            return
        
        # NOTE: Changing the display styles of the protein chunks can take some
        # time. We should put up the wait (hourglass) cursor here and restore 
        # before returning.
        
        # Update all PM widgets that need to be since something has changed.
        print "_update_UI_do_updates(): UPDATING the PMGR."
        self.update_name_field()
        self.update_sequence_editor()
        self.update_residue_combobox()
        
        
        if self.previous_protein:
            self.previous_protein.setDisplayStyle(self.previous_protein_display_style)
            
        self.previous_protein = self.current_protein
        
        if self.current_protein:
            self.previous_protein_display_style = self.current_protein.getDisplayStyle()
            self.current_protein.setDisplayStyle(diPROTEIN)
        
        return
