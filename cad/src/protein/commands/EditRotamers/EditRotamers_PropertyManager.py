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
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_ToolButtonRow import PM_ToolButtonRow
from PM.PM_Slider import PM_Slider
from PM.PM_Constants import PM_DONE_BUTTON
from PM.PM_Constants import PM_WHATS_THIS_BUTTON
from PM.PM_ColorComboBox import PM_ColorComboBox
from PyQt4.Qt import QTextCursor        

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

    
    def __init__( self, parentCommand ):
        """
        Constructor for the property manager.
        """
        
        self.parentMode = parentCommand
        self.w = self.parentMode.w
        self.win = self.parentMode.w

        self.pw = self.parentMode.pw        
        self.o = self.win.glpane                 
        self.currentWorkingDirectory = env.prefs[workingDirectory_prefs_key]
        
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)

        DebugMenuMixin._init1( self )
        self.sequenceEditor = self.win.createProteinSequenceEditorIfNeeded()
        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        msg = "Edit protein rotamers."
        self.updateMessage(msg)

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
        
    #Protein Display methods         

    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """
        self.win.toolsDone()

    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """
        #TODO: Cancel button needs to be removed. See comment at the top
        self.win.toolsDone()

    def update_residue_combobox(self):
        self.current_protein = ""
        previousCommand = self.win.commandSequencer.prevMode
        if previousCommand is not None and previousCommand.commandName == 'BUILD_PROTEIN':
            self.current_protein = previousCommand.propMgr.get_current_protein_chunk_name()
        else:
            #if the previous command was zoom or something, just set this to the
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
        #if the current protein has changed, need to update the residue combo box
        # as well
        
        if self.current_protein != self.previous_protein:
            self.previous_protein = self.current_protein
            count = self.aminoAcidsComboBox.count()    
            for i in range(count):
                self.aminoAcidsComboBox.removeItem(0)
          
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
        
        self.update_residue_combobox()        
        if self.current_protein != "":  
            self.sequenceEditor.show()
        PM_Dialog.show(self)

        # Update all PM widgets, then establish their signal-slot connections.
        # note: It is important to update the widgets *first* since doing
        # it in the reverse order will generate signals when updating
        # the PM widgets (via updateDnaDisplayStyleWidgets()), causing
        # unneccessary repaints of the model view.
        self.connect_or_disconnect_signals(isConnect = True)

        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                self.aminoAcidsComboBox.setCurrentIndex(chunk.protein.get_current_amino_acid_index())
                break
            
    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """
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
        
        previousCommand = self.win.commandSequencer.prevMode
        if previousCommand.commandName == 'BUILD_PROTEIN':
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
        
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        self.discreteStepsCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Use discrete steps",
                         setAsDefault  =  True,
                         state         = Qt.Unchecked)
        
        self.chi1SpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Chi1 angle:",
                              value         =  0.000,
                              setAsDefault  =  True,
                              minimum       =  -180.0,
                              maximum       =  180.0,
                              decimals      =  1,
                              singleStep    =  30.0, 
                              spanWidth = False)
        
        self.chi1SpinBox.setEnabled(False)
        
        self.win.connect(self.chi1SpinBox,
                         SIGNAL("valueChanged(double)"),
                         self._rotateChi1)
        
        self.chi2SpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Chi2 angle:",
                              value         =  0.000,
                              setAsDefault  =  True,
                              minimum       =  -180.0,
                              maximum       =  180.0,
                              decimals      =  1,
                              singleStep    =  30.0, 
                              spanWidth = False)
        
        self.chi2SpinBox.setEnabled(False)
        
        self.win.connect(self.chi2SpinBox,
                         SIGNAL("valueChanged(double)"),
                         self._rotateChi2)
        
        self.chi3SpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Chi3 angle:",
                              value         =  0.000,
                              setAsDefault  =  True,
                              minimum       =  -180.0,
                              maximum       =  180.0,
                              decimals      =  1,
                              singleStep    =  60.0, 
                              spanWidth = False)
        
        self.chi3SpinBox.setEnabled(False)

        self.win.connect(self.chi3SpinBox,
                         SIGNAL("valueChanged(double)"),
                         self._rotateChi3)
        
        self.chi4SpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Chi4 angle:",
                              value         =  0.000,
                              setAsDefault  =  True,
                              minimum       =  -180.0,
                              maximum       =  180.0,
                              decimals      =  1,
                              singleStep    =  60.0, 
                              spanWidth = False)
        
        self.chi4SpinBox.setEnabled(False)
        
        self.chi4SpinBox.hide()
        
        self.win.connect(self.chi4SpinBox,
                         SIGNAL("valueChanged(double)"),
                         self._rotateChi4)
        
    def _addWhatsThisText( self ):
        
        #from ne1_ui.WhatsThisText_for_PropertyManagers import WhatsThis_EditRotamers_PropertyManager
        #WhatsThis_EditRotamers_PropertyManager(self)
        pass
    
    def _addToolTipText(self):
        #from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_EditProteinDisplayStyle_PropertyManager 
        #ToolTip_EditProteinDisplayStyle_PropertyManager(self)
        pass
    
    def _expandNextRotamer(self):
        """
        """
        for chunk in self.win.assy.molecules:
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
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                chunk.protein.collapse_all_rotamers()
                self.win.glpane.gl_update()
                return
        
    def _expandAllRotamers(self):
        """
        """
        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                chunk.protein.expand_all_rotamers()
                self.win.glpane.gl_update()
                return
        
    def _display_and_recenter(self):
        """
        """
        for chunk in self.win.assy.molecules:
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
                    #self.win.glpane.gl_update()
                    self.win.glpane.gl_update()
        
    def _update_chi_angles(self, aa):
        """
        """
        angle = aa.get_chi_angle(0)
        if angle:
            self.chi1SpinBox.setEnabled(True)
            self.chi1SpinBox.setValue(angle)
        else:
            self.chi1SpinBox.setEnabled(False)
            self.chi1SpinBox.setValue(0.0)
        
        angle = aa.get_chi_angle(1)
        if angle:
            self.chi2SpinBox.setEnabled(True)
            self.chi2SpinBox.setValue(angle)
        else:
            self.chi2SpinBox.setEnabled(False)
            self.chi2SpinBox.setValue(0.0)
        
        angle = aa.get_chi_angle(2)
        if angle:
            self.chi3SpinBox.setEnabled(True)
            self.chi3SpinBox.setValue(angle)
        else:
            self.chi3SpinBox.setEnabled(False)
            self.chi3SpinBox.setValue(0.0)
        
        angle = aa.get_chi_angle(3)
        if angle:
            self.chi4SpinBox.setEnabled(True)
            self.chi4SpinBox.setValue(angle)
        else:
            self.chi4SpinBox.setEnabled(False)
            self.chi4SpinBox.setValue(0.0)
        
    def _updateAminoAcidInfo(self, index):
        """
        """
        self.aminoAcidsComboBox.setCurrentIndex(index)
        
    def _aminoAcidChanged(self, index):
        """
        """
        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                chunk.protein.set_current_amino_acid_index(index)

                self._display_and_recenter()
        
        cursor = self.sequenceEditor.sequenceTextEdit.textCursor()
        if index == -1:
            index = 0
        cursor.setPosition(index, QTextCursor.MoveAnchor)       
        cursor.setPosition(index + 1, QTextCursor.KeepAnchor) 
        self.sequenceEditor.sequenceTextEdit.setTextCursor( cursor )
       
                
    def _rotateChiAngle(self, chi, angle):
        """
        """
        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                current_aa = chunk.protein.get_current_amino_acid()
                if current_aa:
                    chunk.protein.expand_rotamer(current_aa)
                    ###print "LOCK = ", self.lockEditedCheckBox.isChecked()
                    current_aa.set_chi_angle(chi, angle, lock=self.lockEditedCheckBox.isChecked())
                    self.win.glpane.gl_update()
                    return
                
    def _rotateChi1(self, angle):
        """
        """
        
        self._rotateChiAngle(0, angle)
                
    def _rotateChi2(self, angle):
        """
        """
        self._rotateChiAngle(1, angle)
                
    def _rotateChi3(self, angle):
        """
        """
        self._rotateChiAngle(2, angle)
                
    def _rotateChi4(self, angle):
        """
        """
        self._rotateChiAngle(3, angle)
                
   