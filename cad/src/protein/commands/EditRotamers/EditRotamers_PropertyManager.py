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

    def show(self):
        """
        Shows the Property Manager. Overrides PM_Dialog.show.
        """
        PM_Dialog.show(self)

        # Update all PM widgets, then establish their signal-slot connections.
        # note: It is important to update the widgets *first* since doing
        # it in the reverse order will generate signals when updating
        # the PM widgets (via updateDnaDisplayStyleWidgets()), causing
        # unneccessary repaints of the model view.
        self.connect_or_disconnect_signals(isConnect = True)

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
                                         title = "Rotamers")
        self._loadGroupBox1( self._pmGroupBox1 )


    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        self.currentAANameLineEdit = PM_LineEdit( pmGroupBox,
                                 label         =  "Rotamer:",
                                 text          =  "",
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
                         state         = Qt.Checked)
        
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
            if chunk.isProteinChunk():
                chunk.protein.collapse_all_rotamers()
                chunk.protein.traverse_forward()
                current_aa = chunk.protein.get_current_amino_acid()
                if current_aa:
                    chunk.protein.expand_rotamer(current_aa)
                    if self.recenterViewCheckBox.isChecked():
                        ca_atom = current_aa.get_c_alpha_atom()
                        if ca_atom:
                            self.win.glpane.pov = -ca_atom.posn()
                        self.win.glpane.gl_update()
                        self._updateAminoAcidInfo()
                        return

    def _expandPreviousRotamer(self):
        """
        """
        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk():
                chunk.protein.collapse_all_rotamers()
                chunk.protein.traverse_backward()
                current_aa = chunk.protein.get_current_amino_acid()
                if current_aa:
                    chunk.protein.expand_rotamer(current_aa)
                    if self.recenterViewCheckBox.isChecked():
                        ca_atom = current_aa.get_c_alpha_atom()
                        if ca_atom:
                            self.win.glpane.pov = -ca_atom.posn()                            
                    self.win.glpane.gl_update()
                    self._updateAminoAcidInfo()
                    return
            
    def _updateAminoAcidInfo(self):
        """
        """
        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk():
                current_aa = chunk.protein.get_current_amino_acid()
                if current_aa:
                    self.currentAANameLineEdit.setText(
                        chunk.protein.get_pdb_id() + 
                        chunk.protein.get_chain_id() + 
                        "[" + 
                        repr(chunk.protein.get_current_amino_acid_index()+1) +
                        "] : " +
                        current_aa.get_three_letter_code() + 
                        "[" +  
                        repr(int(current_aa.get_id())) + 
                        "]")
                    return
            