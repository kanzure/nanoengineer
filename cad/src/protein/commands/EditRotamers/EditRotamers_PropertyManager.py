# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
EditRotamers_PropertyManager.py

The EditRotamers_PropertyManager class provides a Property Manager 
for the B{Edit Rotamers} command on the flyout toolbar in the 
Build > Protein mode. 

@author: Piotr
@version: $Id$ 
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

"""
import os, time, fnmatch, string
import foundation.env as env

from widgets.DebugMenuMixin import DebugMenuMixin
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

from utilities.prefs_constants import getDefaultWorkingDirectory
from utilities.prefs_constants import workingDirectory_prefs_key

from utilities.Log import greenmsg
from utilities.constants import yellow, orange, red, magenta 
from utilities.constants import cyan, blue, white, black, gray

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4 import QtGui

from PyQt4.Qt import QFileDialog, QString, QMessageBox, QSlider
from PM.PM_PushButton   import PM_PushButton
from PM.PM_Dialog   import PM_Dialog
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

#debug flag to keep signals always connected
from utilities.GlobalPreferences import KEEP_SIGNALS_ALWAYS_CONNECTED

class EditRotamers_PropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The ProteinDisplayStyle_PropertyManager class provides a Property Manager 
    for the B{Display Style} command on the flyout toolbar in the 
    Build > Protein mode. 

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
    iconPath      =  "ui/actions/Edit/EditProteinDisplayStyle.png"

    
    def __init__( self, command ):
        """
        Constructor for the property manager.
        """
        
        self.command = command
        self.w = self.command.w
        self.win = self.command.w

        self.pw = self.command.pw        
        self.o = self.win.glpane                 
        self.currentWorkingDirectory = env.prefs[workingDirectory_prefs_key]
        
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)

        DebugMenuMixin._init1( self )
        self.sequenceEditor = self.win.createProteinSequenceEditorIfNeeded()
        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        msg = "Edit protein rotamers."
        self.updateMessage(msg)
        
        if KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)

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
        
        self.connect( self.aminoAcidsComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self._aminoAcidChanged)
        change_connect(self.showSequencePushButton, 
                       SIGNAL("clicked()"),
                       self._showSeqEditor)
        
    
    #Protein Display methods         

    def _showSeqEditor(self):
        """
        Show sequence editor
        """
        if self.showSequencePushButton.isEnabled():
            self.sequenceEditor.show()
        return
    
    
    def update_residue_combobox(self):
        """
        Update the residue combo box with residues belonging to the same protein
        """
        #Urmi 20080728: Update the residue combo box with amino acids for the
        #currently selected protein in build protein mode
        self.current_protein = ""
        from utilities.GlobalPreferences import MODEL_AND_SIMULATE_PROTEINS
        if MODEL_AND_SIMULATE_PROTEINS:
            previousCommand = self.command.find_parent_command_named('MODEL_AND_SIMULATE_PROTEIN')
        else:    
            previousCommand = self.command.find_parent_command_named('BUILD_PROTEIN')
        if previousCommand:
            self.current_protein = previousCommand.propMgr.get_current_protein_chunk_name()
        else:
            #Urmi 20080728: if the previous command was zoom or something, just set this to the
            # first available protein chunk, since there's no way we can access
            # the current protein in Build protein mode
            for mol in self.win.assy.molecules:
                if mol.isProteinChunk():
                    self.current_protein = mol.name
                    sequence = mol.protein.get_sequence_string()
                    self.sequenceEditor.setSequence(sequence)
                    secStructure = mol.protein.get_secondary_structure_string()
                    self.sequenceEditor.setSecondaryStructure(secStructure)
                    self.sequenceEditor.setRuler(len(secStructure))
                    break
        # Urmi 20080728: if the current protein has changed, need to update the residue combo box
        # as well between two entries into this mode
        
        if self.current_protein != self.previous_protein:
            self.previous_protein = self.current_protein
            count = self.aminoAcidsComboBox.count() 
            #remove all the old residues
            for i in range(count):
                self.aminoAcidsComboBox.removeItem(0)
            #add all the new residues
            aa_list = []
            for mol in self.win.assy.molecules:
                if mol.isProteinChunk() and mol.name == self.current_protein:
                    aa_list = mol.protein.get_amino_acid_id_list()
                    break
            
            for j in range(len(aa_list)):
                self.aminoAcidsComboBox.addItem(aa_list[j])
        return
        
    def show(self):
        """
        Shows the Property Manager. Overrides PM_Dialog.show.
        """  
        env.history.statusbar_msg("")
        self.update_residue_combobox()        
        if self.current_protein != "":  
            self.showSequencePushButton.setEnabled(True)
        else:
            self.showSequencePushButton.setEnabled(False)
        self.sequenceEditor.hide()    
        PM_Dialog.show(self)
        
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)

        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                self.aminoAcidsComboBox.setCurrentIndex(chunk.protein.get_current_amino_acid_index())
                break
            
    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(False)
            
        PM_Dialog.close(self)

    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self,
                                         title = "Position")
        self._loadGroupBox1( self._pmGroupBox1 )

        self._pmGroupBox2 = PM_GroupBox( self,
                                         title = "Rotamer")
        self._loadGroupBox2( self._pmGroupBox2 )


    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        self.current_protein = ""
        #Urmi 20080728: fill up the combo box with amino acids belonging to the
        # current protein in build protein mode
        from utilities.GlobalPreferences import MODEL_AND_SIMULATE_PROTEINS
        if MODEL_AND_SIMULATE_PROTEINS:
            previousCommand = self.command.find_parent_command_named('MODEL_AND_SIMULATE_PROTEIN')
        else:    
            previousCommand = self.command.find_parent_command_named('BUILD_PROTEIN')
        if previousCommand:
            self.current_protein = previousCommand.propMgr.get_current_protein_chunk_name()
        else:
            for mol in self.win.assy.molecules:
                if mol.isProteinChunk():
                    self.current_protein = mol.name
                    break
        self.previous_protein = self.current_protein            
        aa_list = []
        for mol in self.win.assy.molecules:
            if mol.isProteinChunk() and mol.name == self.current_protein:
                aa_list = mol.protein.get_amino_acid_id_list()
                break
            
        self.aminoAcidsComboBox = PM_ComboBox( pmGroupBox,
                                 label         =  "Residue:",
                                 choices       =  aa_list,
                                 setAsDefault  =  False)

        
        self.previousAAPushButton  = \
            PM_PushButton( pmGroupBox,
                         text         =  "Previous AA",
                         setAsDefault  =  True)
        
        self.nextAAPushButton  = \
            PM_PushButton( pmGroupBox,
                         text         =  "Next AA",
                         setAsDefault  =  True)
        
        self.recenterViewCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Re-center view",
                         setAsDefault  =  True,
                         state         = Qt.Unchecked)
        
        self.lockEditedCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Lock edited rotamers",
                         setAsDefault  =  True,
                         state         = Qt.Checked)
        
        self.expandAllPushButton  = \
            PM_PushButton( pmGroupBox,
                         text         =  "Expand All",
                         setAsDefault  =  True)
        
        self.collapseAllPushButton  = \
            PM_PushButton( pmGroupBox,
                         text         =  "Collapse All",
                         setAsDefault  =  True)
        
        self.showSequencePushButton = PM_PushButton( pmGroupBox,
            text       =  "Show Sequence",
            setAsDefault  =  True
            )
        
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
        
    def _addWhatsThisText( self ):
        
        pass
    
    def _addToolTipText(self):
        
        pass
    
    def _expandNextRotamer(self):
        """
        """
        for chunk in self.win.assy.molecules:
            #Urmi 20080728: slot method for the current protein from build protein mode
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                chunk.protein.traverse_forward()
                self._display_and_recenter()
                self._updateAminoAcidInfo(
                    chunk.protein.get_current_amino_acid_index())
                return

    def _expandPreviousRotamer(self):
        """
        """
        for chunk in self.win.assy.molecules:
            #Urmi 20080728: slot method for the current protein from build protein mode
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                chunk.protein.traverse_backward()
                self._display_and_recenter()
                self._updateAminoAcidInfo(
                    chunk.protein.get_current_amino_acid_index())
                return
        
    def _collapseAllRotamers(self):
        """
        """
        for chunk in self.win.assy.molecules:
            #Urmi 20080728: slot method for the current protein from build protein mode
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                chunk.protein.collapse_all_rotamers()
                self.win.glpane.gl_update()
                return
        
    def _expandAllRotamers(self):
        """
        """
        for chunk in self.win.assy.molecules:
            #Urmi 20080728: slot method for the current protein from build protein mode
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                chunk.protein.expand_all_rotamers()
                self.win.glpane.gl_update()
                return
        
    def _display_and_recenter(self):
        """
        """
        for chunk in self.win.assy.molecules:
            #Urmi 20080728: display and recenter for the current protein 
            #from build protein mode
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                chunk.protein.collapse_all_rotamers()
                current_aa = chunk.protein.get_current_amino_acid()
                if current_aa:
                    chunk.protein.expand_rotamer(current_aa)
                    self._update_chi_angles(current_aa)
                    if self.recenterViewCheckBox.isChecked():
                        ca_atom = current_aa.get_c_alpha_atom()
                        if ca_atom:
                            self.win.glpane.pov = -ca_atom.posn()                            
                    
                    self.win.glpane.gl_update()
        
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
        
    def _updateAminoAcidInfo(self, index):
        """
        Update position of Amino Acid combo box.
        """
        self.aminoAcidsComboBox.setCurrentIndex(index)
        
    def _aminoAcidChanged(self, index):
        """
        """
        for chunk in self.win.assy.molecules:
            #Urmi 20080728: slot method for the current protein from build protein mode
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                chunk.protein.set_current_amino_acid_index(index)

                self._display_and_recenter()
        
        #Urmi 20080728: change the cursor position in the sequence editor 
        # when current amino acid in the amino acid combo box is changed
        cursor = self.sequenceEditor.sequenceTextEdit.textCursor()
        if index == -1:
            index = 0
        cursor.setPosition(index, QTextCursor.MoveAnchor)       
        cursor.setPosition(index + 1, QTextCursor.KeepAnchor) 
        self.sequenceEditor.sequenceTextEdit.setTextCursor( cursor )
       
                
    def _rotateChiAngle(self, chi, angle):
        """
        Rotate around chi1 angle.
        """
        for chunk in self.win.assy.molecules:
            #Urmi 20080728: slot method for the current protein from build protein mode
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                current_aa = chunk.protein.get_current_amino_acid()
                if current_aa:
                    chunk.protein.expand_rotamer(current_aa)
                    current_aa.set_chi_angle(chi, angle)
                    self.win.glpane.gl_update()
                    return
                
    def _rotateChi1(self, angle):
        """
        
        """
        self._rotateChiAngle(0, angle)
        self.chi1Dial.updateValueLabel()
        
    def _rotateChi2(self, angle):
        """
        """
        self._rotateChiAngle(1, angle)
        self.chi2Dial.updateValueLabel()
                
    def _rotateChi3(self, angle):
        """
        """
        self._rotateChiAngle(2, angle)
        self.chi3Dial.updateValueLabel()
                
    def _rotateChi4(self, angle):
        """
        """
        self._rotateChiAngle(3, angle)
                
   
