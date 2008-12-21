# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
EditRotamers_PropertyManager.py

The EditRotamers_PropertyManager class provides a Property Manager 
for the B{Edit Rotamers} command on the flyout toolbar in the 
Build > Protein mode. 

@author: Piotr, Mark
@version: $Id$ 
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

TODO:
- Show residue label in GA of current residue, including AA and # (i.e. SER[14]).
- Better messages, especially when selecting different peptides.
- Include "Show entire model" checkbox in PM (checked by default).
- Add wait (hourglass) cursor when changing the display style of proteins.
- Allow user to rename current protein in the Name field.
- Need to implement a validator for the Name line edit field.
- Dim everything in the current protein except the atoms in the current aa.

REFACTORING:
Things to discuss with Bruce include an asterisk:
- Should current_struct be renamed to command.struct everywhere? *
- Add current_aa attr (will eliminate redundant calls to 
  self.current_protein.protein.get_current_amino_acid())
- Moving some methods to EditRotamers_Command or EditCommand class. *
  - add setStructureName(name) in EditRotamers_Command or in superclass EditCommand?
  - other methods that edit the current protein.
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
        
        change_connect(self.nameLineEdit,
                       SIGNAL("editingFinished()"),
                       self._nameChanged)
        
        change_connect(self.currentResidueComboBox,
                       SIGNAL("activated(int)"),
                       self._currentResidueChanged)
        
        change_connect(self.prevButton, 
                       SIGNAL("clicked()"), 
                       self._expandPreviousRotamer)
        
        change_connect(self.nextButton, 
                       SIGNAL("clicked()"), 
                       self._expandNextRotamer)
        
        change_connect(self.recenterViewCheckBox,
                       SIGNAL("toggled(bool)"),
                       self._centerViewToggled)
        
        change_connect(self.showAllResiduesCheckBox,
                       SIGNAL("toggled(bool)"),
                       self._showAllResidues)
        
        # Rotamer control widgets.
        
        change_connect(self.chi1Dial,
                       SIGNAL("valueChanged(int)"),
                       self._rotateChi1)
        
                
        change_connect(self.chi2Dial,
                       SIGNAL("valueChanged(int)"),
                       self._rotateChi2)
        
        change_connect(self.chi3Dial,
                       SIGNAL("valueChanged(int)"),
                       self._rotateChi3)
        
        # Chi4 dial is hidden.
        change_connect(self.chi4Dial,
                       SIGNAL("valueChanged(double)"),
                       self._rotateChi4)
        return
    
    #==
    
    def _nameChanged(self):
        """
        Slot for "Name" field.
        
        @TODO: Include a validator for the name field.
        """
        if not self.current_protein:
            return
        
        _name = str(self.nameLineEdit.text())
        
        if not _name: # Minimal test. Need to implement a validator.
            if self.current_protein:
                self.nameLineEdit.setText(self.current_protein.name)
            return
        
        self.current_protein.name = _name
        msg = "Editing structure <b>%s</b>." % _name
        self.updateMessage(msg)
        
        return
    
    def update_name_field(self):
        """
        Update the name field showing the name of the currently selected protein.
        clear the combobox list.
        """
        if not self.current_protein:
            self.nameLineEdit.setText("")
        else:
            self.nameLineEdit.setText(self.current_protein.name)
        return
    
    def update_length_field(self):
        """
        Update the name field showing the name of the currently selected protein.
        clear the combobox list.
        """
        if not self.current_protein:
            self.lengthLineEdit.setText("")
        else:
            length_str = "%d residues" % self.current_protein.protein.count_amino_acids()
            self.lengthLineEdit.setText(length_str)
        return
    
    def update_residue_combobox(self):
        """
        Update the residue combobox with the amino acid sequence of the
        currently selected protein. If there is no currently selected protein,
        clear the combobox list.
        """
        
        self.currentResidueComboBox.clear()
        
        if not self.current_protein:
            return
        
        aa_list = self.current_protein.protein.get_amino_acid_id_list()
        for j in range(len(aa_list)):
            self.currentResidueComboBox.addItem(aa_list[j])
        
        # This doesn't generate a signal (only 'activate' is connected to 
        # slot _currentResidueChanged).
        self.currentResidueComboBox.setCurrentIndex(
            self.current_protein.protein.get_current_amino_acid_index())
        
        # Call the slot explicitly. This is needed to draw the rotamer
        # on top of the reduced model of the current protein.
        # Also see the comments in _update_UI_do_updates().
        self._currentResidueChanged(
            self.current_protein.protein.get_current_amino_acid_index())
        
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
            
            # Update name in case the it was changed by the user.
            self.current_protein.name = str(self.nameLineEdit.text())
            
        _superclass.close(self)
        return
    
    def show(self):
        """
        Show the PM. Extends superclass method.
        @note: _update_UI_do_updates() gets called immediately after this and
               updates PM widgets with their correct values/settings.
        """
        _superclass.show(self)
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
        
        self.nameLineEdit = PM_LineEdit( pmGroupBox,
                                                label = "Name:")
        
        self.lengthLineEdit = PM_LineEdit( pmGroupBox,
                                           label = "Length:")
        self.lengthLineEdit.setEnabled(False)
        
        self.currentResidueComboBox = PM_ComboBox( pmGroupBox,
                                 label         =  "Current residue:",
                                 setAsDefault  =  False)
        
        BUTTON_LIST = [
            ("QToolButton", 1, "Previous residue", 
             "ui/actions/Properties Manager/Previous.png", 
             "", "Previous residue", 0 ),

            ( "QToolButton", 2, "Next residue",  
              "ui/actions/Properties Manager/Next.png", 
              "", "Next residue", 1 )
            ]
        
        self.prevNextButtonRow = \
            PM_ToolButtonRow( pmGroupBox, 
                              title        =  "",
                              buttonList   =  BUTTON_LIST,
                              label        =  'Previous / Next:',
                              isAutoRaise  =  True,
                              isCheckable  =  False
                            )
        self.prevButton = self.prevNextButtonRow.getButtonById(1)
        self.nextButton = self.prevNextButtonRow.getButtonById(2)
        
        self.recenterViewCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Center view on current residue",
                         setAsDefault  =  True,
                         state         =  Qt.Unchecked,
                         widgetColumn  =  0,
                         spanWidth     =  True)
        
        self.lockEditedCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Lock edited rotamers",
                         setAsDefault  =  True,
                         state         =  Qt.Checked,
                         widgetColumn  =  0,
                         spanWidth     =  True)
        
        self.showAllResiduesCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Show all residues",
                         setAsDefault  =  False,
                         state         =  Qt.Unchecked,
                         widgetColumn  =  0,
                         spanWidth     =  True)
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
        self._updateResidueInfo()
        return
    
    def _expandPreviousRotamer(self):
        """
        Displays the previous rotamer in the chain.
        
        @attention: this only works when the GDS is a reduced display style.
        """
        if not self.current_protein:
            return
        
        self.current_protein.protein.traverse_backward()
        self._updateResidueInfo()
        return
    
    def _centerViewToggled(self, checked):
        """
        Slot for "Center view on current residue" checkbox.
        """
        if checked:
            self.display_and_recenter()
        return
    
    def _showAllResidues(self, show):
        """
        Slot for "Show all residues" checkbox.
        """
        if not self.current_protein:
            return
        
        print "Show =",show
        if show:
            self._expandAllRotamers()
        else:
            self._collapseAllRotamers()
        return
    
    def _collapseAllRotamers(self):
        """
        Hides all the rotamers (except the current rotamer).
        """
        self.display_and_recenter()
        return
    
    def _expandAllRotamers(self):
        """
        Displays all the rotamers.
        """
        if not self.current_protein:
            return
        
        self.current_protein.protein.expand_all_rotamers()
        self.win.glpane.gl_update()
        return
        
    def display_and_recenter(self):
        """
        Recenter the view on the current amino acid selected in the 
        residue combobox (or the sequence editor). All rotamers 
        except the current rotamer are collapsed (hidden).
        """
        if not self.current_protein:
            return
        
        # Uncheck the "Show all residues" checkbox since they are being collapsed.
        # Disconnect signals so that showAllResiduesCheckBox won't general a signal.
        self.connect_or_disconnect_signals(isConnect = False)
        self.showAllResiduesCheckBox.setChecked(False)
        self.connect_or_disconnect_signals(isConnect = True)
        
        self.current_protein.protein.collapse_all_rotamers()
        current_aa = self.current_protein.protein.get_current_amino_acid()
        
        # Display the current amino acid and center it in the view if the
        # "Center view on current residue" is checked.
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
    
    def _updateResidueInfo(self):
        """
        Update the "Current residue" combobox and the cursor position of the
        sequence editor based on the current protein's amino acid index.
        """
        aa_index = self.current_protein.protein.get_current_amino_acid_index()
        self.currentResidueComboBox.setCurrentIndex(aa_index)
        self.sequenceEditor.setCursorPosition(aa_index)
        self.display_and_recenter()
        return
        
    def _currentResidueChanged(self, index):
        """
        Slot for the "Current residue" combobox.
        """
        if not self.current_protein:
            return
        
        print"_currentResidueChanged(): index=", index
        self.current_protein.protein.set_current_amino_acid_index(index)
        self.display_and_recenter()
        self.sequenceEditor.setCursorPosition(index)
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
        Slot for Chi1 dial.
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
        
        if self.current_protein is self.previous_protein:
            print "_update_UI_do_updates(): DO NOTHING."
            return
        
        # It is common that the user will unselect the current protein.
        # If so, set current_protein to previous_protein so that it 
        # (the previously selected protein) remains the current protein 
        # in the PM and sequence editor.
        if not self.current_protein:
            self.current_protein = self.previous_protein
            return
        
        # Update all PM widgets that need to be since something has changed.
        print "_update_UI_do_updates(): UPDATING the PMGR."
        self.update_name_field()
        self.update_length_field()
        self.sequenceEditor.updateSequence(proteinChunk = self.current_protein)
        self.update_residue_combobox()
        
        # NOTE: Changing the display style of the protein chunks can take some
        # time. We should put up the wait (hourglass) cursor and restore 
        # before returning.
        if self.previous_protein:
            self.previous_protein.setDisplayStyle(self.previous_protein_display_style)
            
        self.previous_protein = self.current_protein
        
        if self.current_protein:
            self.previous_protein_display_style = self.current_protein.getDisplayStyle()
            self.current_protein.setDisplayStyle(diPROTEIN)
            
        if self.current_protein:
            msg = "Editing structure <b>%s</b>." % self.current_protein.name
        else:
            msg = "Select a single structure to edit."
        self.updateMessage(msg)
        
        return
