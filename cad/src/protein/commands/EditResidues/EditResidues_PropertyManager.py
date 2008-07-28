# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
EditResidues_PropertyManager.py

The EditResidues_PropertyManager class provides a Property Manager 
for the B{Edit Residues} command on the flyout toolbar in the 
Build > Protein mode. 

@author: Piotr
@version: $Id$ 
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

"""
import os, sys, time, fnmatch, string, re
import foundation.env as env

from widgets.DebugMenuMixin import DebugMenuMixin
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

from utilities.prefs_constants import getDefaultWorkingDirectory
from utilities.prefs_constants import workingDirectory_prefs_key
from utilities.prefs_constants import proteinCustomDescriptors_prefs_key

from utilities.Log import greenmsg
from utilities.constants import yellow, orange, red, magenta 
from utilities.constants import cyan, blue, white, black, gray

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4.Qt import QCheckBox
from PyQt4.Qt import QLabel
from PyQt4.Qt import QFont
from PyQt4.Qt import QComboBox
from PyQt4.Qt import QTableWidgetItem
from PyQt4.Qt import QSize
        

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
from PM.PM_TableWidget import PM_TableWidget
from PM.PM_WidgetGrid import PM_WidgetGrid

class EditResidues_PropertyManager( PM_Dialog, DebugMenuMixin ):
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

    title         =  "Edit Residues"
    pmName        =  title
    iconPath      =  "ui/actions/Edit/EditProteinDisplayStyle.png"

    rosetta_all_set =    "PGAVILMFWYCSTNQDEHKR"
    rosetta_polar_set =  "___________STNQDEHKR"
    rosetta_apolar_set = "PGAVILMFWYC_________"

        
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

        msg = "Edit residues."
        
        self.editingItem = False
        
        self.updateMessage(msg)

    def connect_or_disconnect_signals(self, isConnect = True):
        
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
        
        change_connect(self.applyAnyPushButton,
                         SIGNAL("clicked()"),
                         self._applyAny)

        change_connect(self.applySamePushButton,
                         SIGNAL("clicked()"),
                         self._applySame)

        change_connect(self.applyLockedPushButton,
                         SIGNAL("clicked()"),
                         self._applyLocked)

        change_connect(self.applyPolarPushButton,
                         SIGNAL("clicked()"),
                         self._applyPolar)

        change_connect(self.applyApolarPushButton,
                         SIGNAL("clicked()"),
                         self._applyApolar)

        change_connect(self.selectAllPushButton,
                         SIGNAL("clicked()"),
                         self._selectAll)
        
        change_connect(self.selectNonePushButton,
                         SIGNAL("clicked()"),
                         self._selectNone)
        
        change_connect(self.selectInvertPushButton,
                         SIGNAL("clicked()"),
                         self._invertSelection)

        change_connect(self.applyDescriptorPushButton,
                         SIGNAL("clicked()"),
                         self._applyDescriptor)
        
        change_connect(self.removeDescriptorPushButton,
                         SIGNAL("clicked()"),
                         self._removeDescriptor)
        
        change_connect(self.sequenceTable,
                         SIGNAL("cellClicked(int, int)"),
                         self._sequenceTableCellChanged)
        
        change_connect(self.sequenceTable, 
                         SIGNAL("itemChanged(QTableWidgetItem*)"),
                         self._sequenceTableItemChanged)
        
        change_connect(self.descriptorsTable, 
                         SIGNAL("itemChanged(QTableWidgetItem*)"),
                         self._descriptorsTableItemChanged)
        
        #change_connect(self.descriptorsTable, 
        #                 SIGNAL("currentItemChanged(QTableWidgetItem*, QTableWidgetItem*)"),
        #                 self._descriptorsTableCurrentItemChanged)
        
        #change_connect(self.descriptorsTable, 
        #                 SIGNAL("itemDoubleClicked(QTableWidgetItem*)"),
        #                 self._descriptorsTableItemDoubleClicked)
        
        change_connect(self.newDescriptorPushButton,
                         SIGNAL("clicked()"),
                         self._addNewDescriptor)
        
        
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
        #Urmi 20080728: Set the current protein and this will be used for accessing
        #various properties of this protein
        self.set_current_protein()
        if self.current_protein != "":    
            self.sequenceEditor.show()
        PM_Dialog.show(self)
        self.connect_or_disconnect_signals(isConnect = True)
        self._fillSequenceTable()
        
    def set_current_protein(self):
        """
        Set the current protein for which all the properties are displayed to the
        one chosen in the build protein combo box
        """
        #Urmi 20080728: created this method to update accessing properties of
        #"current protein" in this mode.
        self.current_protein = ""
        previousCommand = self.win.commandSequencer.prevMode # set_current_protein: previousCommand.propMgr.get_current_protein_chunk_name
        #Urmi 20080728: get the protein currently selected in the combo box
        if previousCommand is not None and previousCommand.commandName == 'BUILD_PROTEIN':
            self.current_protein = previousCommand.propMgr.get_current_protein_chunk_name()
        else:
            #if the previous command was zoom or something, just set this to the
            # first available protein chunk, since there's no way we can access
            # the current protein in Build protein mode
            for mol in self.win.assy.molecules:
                if mol.isProteinChunk():
                    #Urmi 20080728: set the current protein to first available
                    #protein in NE-1 part
                    self.current_protein = mol.name
                    sequence = mol.protein.get_sequence_string()
                    self.sequenceEditor.setSequence(sequence)
                    secStructure = mol.protein.get_secondary_structure_string()
                    self.sequenceEditor.setSecondaryStructure(secStructure)
                    self.sequenceEditor.setRuler(len(secStructure))
                    break
        return
        
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
        
        if sys.platform == "darwin":
            # Workaround for table font size difference between Mac/Win
            self.labelfont = QFont("Helvetica", 12)
            self.descriptorfont = QFont("Courier New", 12)        
        else:
            self.labelfont = QFont("Helvetica", 9)
            self.descriptorfont = QFont("Courier New", 9)        
            
        self._pmGroupBox1 = PM_GroupBox( self,
                                         title = "Descriptors")
        self._loadGroupBox1( self._pmGroupBox1 )

        self._pmGroupBox2 = PM_GroupBox( self,
                                         title = "Sequence")
        self._loadGroupBox2( self._pmGroupBox2 )


    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
            
        self.headerdata_desc = ['Name', 'Descriptor']
        
        self.set_names = ["Any", "Same", "Locked", "Apolar", "Polar"]
        self.rosetta_set_names = ["ALLAA", "NATAA", "NATRO", "APOLA", "POLAR"]
        self.descriptor_list = ["PGAVILMFWYCSTNQDEHKR", 
                                "____________________", 
                                "____________________", 
                                "PGAVILMFWYC_________",
                                "___________STNQDEHKR"]
        
        self.applyAnyPushButton = PM_PushButton( pmGroupBox,
            text       =  "ALLAA",
            setAsDefault  =  True)
        
        self.applySamePushButton = PM_PushButton( pmGroupBox,
            text       =  "NATAA",
            setAsDefault  =  True)
        
        self.applyLockedPushButton = PM_PushButton( pmGroupBox,
            text       =  "NATRO",
            setAsDefault  =  True)
        
        self.applyPolarPushButton = PM_PushButton( pmGroupBox,
            text       =  "APOLA",
            setAsDefault  =  True)
        
        self.applyApolarPushButton = PM_PushButton( pmGroupBox,
            text       =  "POLAR",
            setAsDefault  =  True)
        
        self.applyAnyPushButton.setFixedHeight(25)
        self.applyAnyPushButton.setFixedWidth(60)
        
        self.applySamePushButton.setFixedHeight(25)
        self.applySamePushButton.setFixedWidth(60)

        self.applyLockedPushButton.setFixedHeight(25)
        self.applyLockedPushButton.setFixedWidth(60)

        self.applyPolarPushButton.setFixedHeight(25)
        self.applyPolarPushButton.setFixedWidth(60)

        self.applyApolarPushButton.setFixedHeight(25)
        self.applyApolarPushButton.setFixedWidth(60)
        
        applyButtonList = [('PM_PushButton', self.applyAnyPushButton, 0, 0),
            ('PM_PushButton', self.applySamePushButton, 1, 0),
            ('PM_PushButton', self.applyLockedPushButton, 2, 0),
            ('PM_PushButton', self.applyPolarPushButton, 3, 0),
            ('PM_PushButton', self.applyApolarPushButton, 4, 0) ]

        self.applyButtonGrid = PM_WidgetGrid( pmGroupBox, 
                                              label = "Apply standard set",
                                              widgetList = applyButtonList)

        self.descriptorsTable = PM_TableWidget( pmGroupBox,
                                                label = "Custom descriptors")
        
        self.descriptorsTable.setFixedHeight(100)
        self.descriptorsTable.setRowCount(0)
        self.descriptorsTable.setColumnCount(2)
        self.descriptorsTable.verticalHeader().setVisible(False)
        self.descriptorsTable.horizontalHeader().setVisible(True)
        self.descriptorsTable.setGridStyle(Qt.NoPen)
        self.descriptorsTable.setHorizontalHeaderLabels(self.headerdata_desc) 

        self._updateSetLists()
        
        self._fillDescriptorsTable()
        
        #dstr = env.prefs[proteinCustomDescriptors_prefs_key].split(":")
        #for i in range(len(dstr) / 2):
        #    self.set_names.append(dstr[2*i])
        #    self.descriptor_list.append(dstr[2*i+1])
        #    self.rosetta_set_names.append("PIKAA")
        #    self._addNewDescriptorTableRow(dstr[2*i], dstr[2*i+1])
                    
        self.descriptorsTable.resizeColumnsToContents()

        self.newDescriptorPushButton = PM_PushButton( pmGroupBox,
            text         =  "New",
            setAsDefault  =  True)

        self.newDescriptorPushButton.setFixedHeight(25)

        self.removeDescriptorPushButton = PM_PushButton( pmGroupBox,
            text         =  "Remove",
            setAsDefault  =  True)

        self.removeDescriptorPushButton.setFixedHeight(25)

        self.applyDescriptorPushButton = PM_PushButton( pmGroupBox,
            text         =  "Apply",
            setAsDefault  =  True)

        self.applyDescriptorPushButton.setFixedHeight(25)

        addDescriptorButtonList = [('PM_PushButton', self.newDescriptorPushButton, 0, 0),
            ('PM_PushButton', self.removeDescriptorPushButton, 1, 0),
            ('PM_PushButton', self.applyDescriptorPushButton, 2, 0) ]

        self.addDescriptorGrid = PM_WidgetGrid( pmGroupBox, 
                                              alignment = "Center", 
                                              widgetList = addDescriptorButtonList)
                
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in second group box.
        """
            
        self.headerdata_seq = ['', 'ID', 'Set', 'Descriptor']

        self.recenterViewCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Re-center view on selected residue",
                         setAsDefault  =  True,
                         widgetColumn  = 0, 
                         state         = Qt.Unchecked)
        
        self.selectAllPushButton = PM_PushButton( pmGroupBox,
            text         =  "All",
            setAsDefault  =  True)

        self.selectAllPushButton.setFixedHeight(25)
        
        self.selectNonePushButton = PM_PushButton( pmGroupBox,
            text       =  "None",
            setAsDefault  =  True)

        self.selectNonePushButton.setFixedHeight(25)

        self.selectInvertPushButton = PM_PushButton( pmGroupBox,
            text       =  "Invert",
            setAsDefault  =  True)

        self.selectInvertPushButton.setFixedHeight(25)

        buttonList = [ ('PM_PushButton', self.selectAllPushButton, 0, 0),
                       ('PM_PushButton', self.selectNonePushButton, 1, 0),
                       ('PM_PushButton', self.selectInvertPushButton, 2, 0)]

        self.buttonGrid = PM_WidgetGrid( pmGroupBox, 
                                         widgetList = buttonList)
                                         
        
        self.sequenceTable = PM_TableWidget( pmGroupBox)
        #self.sequenceTable.setModel(self.tableModel)
        self.sequenceTable.resizeColumnsToContents()
        self.sequenceTable.verticalHeader().setVisible(False)
        #self.sequenceTable.setRowCount(0)
        self.sequenceTable.setColumnCount(4)
        
        self.checkbox = QCheckBox()
        
        
        self.sequenceTable.setFixedHeight(345)
        
        self.sequenceTable.setGridStyle(Qt.NoPen)
        
        self.sequenceTable.setHorizontalHeaderLabels(self.headerdata_seq) 
        ###self._fillSequenceTable()
        

    def _fillSequenceTable(self):
        """
        """        
        
        ###self.setComboBox = QComboBox()
        
        self.editingItem = True
        
        for chunk in self.win.assy.molecules:
            #Urmi 20080728: slot connection for current protein in build protein mode
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                aa_list = chunk.protein.get_amino_acids()
                aa_list_len = len(aa_list)
                self.sequenceTable.setRowCount(aa_list_len)
                for index in range(aa_list_len):                    
                    item_widget = QTableWidgetItem("")
                    item_widget.setFont(self.labelfont)
                    item_widget.setCheckState(Qt.Checked)
                    item_widget.setTextAlignment(Qt.AlignLeft)
                    item_widget.setSizeHint(QSize(20,12))
                    item_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
                    self.sequenceTable.setItem(index, 0, item_widget)
                
                    item_widget = QTableWidgetItem(str(index+1))
                    item_widget.setFont(self.labelfont)
                    item_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)            
                    item_widget.setTextAlignment(Qt.AlignCenter)
                    self.sequenceTable.setItem(index, 1, item_widget)
                    
                    aa = self._get_aa_for_index(index)
                    item_widget = QTableWidgetItem(self._get_descriptor_name(aa))
                    item_widget.setFont(self.labelfont)
                    item_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item_widget.setTextAlignment(Qt.AlignCenter)
                    self.sequenceTable.setItem(index, 2, item_widget)
                    
                    aa_string = self._get_mutation_descriptor(aa)

                    item_widget = QTableWidgetItem(aa_string)
                    item_widget.setFont(self.descriptorfont)
                    self.sequenceTable.setItem(index, 3, item_widget)
        
                    self.sequenceTable.setRowHeight(index, 16)
                    
        self.editingItem = False
        
        self.sequenceTable.resizeColumnsToContents()
        
        self.sequenceTable.setColumnWidth(0, 35)
        self.sequenceTable.setColumnWidth(2, 80)
        
    def _get_descriptor_name(self, aa):
        """
        """
        range_name = aa.get_mutation_range()
        for i in range(len(self.rosetta_set_names)):
            if range_name == self.rosetta_set_names[i]:
                if range_name == "PIKAA":
                    # Find a descriptor with a list of
                    # custom descriptors.
                    dstr = self._makeProperAAString(aa.get_mutation_descriptor())
                    for i in range(5, len(self.descriptor_list)):
                        if dstr == self.descriptor_list[i]:
                            return self.set_names[i]
                else:
                    return self.set_names[i]
        return "Custom"
    
    def _selectAll(self):
        for row in range(self.sequenceTable.rowCount()):
            self.sequenceTable.item(row, 0).setCheckState(Qt.Checked)
            
    def _selectNone(self):
        for row in range(self.sequenceTable.rowCount()):
            self.sequenceTable.item(row, 0).setCheckState(Qt.Unchecked)
            
    def _invertSelection(self):
        for row in range(self.sequenceTable.rowCount()):
            item_widget = self.sequenceTable.item(row, 0)
            if item_widget.checkState() == Qt.Checked:
                item_widget.setCheckState(Qt.Unchecked)
            else:
                item_widget.setCheckState(Qt.Checked)
                
    def _get_mutation_descriptor(self, aa):
        """
        """
        aa_string = self.rosetta_all_set
        
        range = aa.get_mutation_range()                    
        aa_string = self.rosetta_all_set
        
        if range == "NATRO" or \
           range == "NATAA":
            code = aa.get_one_letter_code()                    
            aa_string = re.sub("[^"+code+"]",'_', aa_string)
        elif range == "POLAR":
            aa_string = self.rosetta_polar_set
        elif range == "APOLA":
            aa_string = self.rosetta_apolar_set
        elif range == "PIKAA":
            aa_string = aa.get_mutation_descriptor()
        
        return aa_string
    
    def _get_aa_for_index(self, index, expand=False):
        """
        """
        # Center on a selected amino acid.
        for chunk in self.win.assy.molecules:
            #Urmi 20080728: slot connection for current protein in build protein mode
            if chunk.isProteinChunk() and chunk.name == self.current_protein:
                chunk.protein.set_current_amino_acid_index(index)
                current_aa = chunk.protein.get_current_amino_acid()
                if expand:
                    chunk.protein.collapse_all_rotamers()
                    chunk.protein.expand_rotamer(current_aa)
                return current_aa 

        return None
    
    def _sequenceTableCellChanged(self, crow, ccol):
        item = self.sequenceTable.item(crow, ccol)
        for row in range(self.sequenceTable.rowCount()):
            self.sequenceTable.removeCellWidget(row, 2)
            self.sequenceTable.setRowHeight(row, 16)
        if ccol == 2:
            # Make the row a little bit wider.
            self.sequenceTable.setRowHeight(crow, 22)
            # Create and insert a Combo Box into a current cell. 
            self.setComboBox = QComboBox()
            self.setComboBox.addItems(self.set_names)
            
            self.win.connect(self.setComboBox,
                             SIGNAL("activated(int)"),
                             self._setComboBoxIndexChanged)
            
            self.sequenceTable.setCellWidget(crow, 2, self.setComboBox)
        
        current_aa = self._get_aa_for_index(crow, expand=True)
        if current_aa:
            # Center on the selected amino acid.
            if self.recenterViewCheckBox.isChecked():
                ca_atom = current_aa.get_c_alpha_atom()
                if ca_atom:
                    self.win.glpane.pov = -ca_atom.posn()                            
            self.win.glpane.gl_update()
        
        from PyQt4.Qt import QTextCursor   
        cursor = self.sequenceEditor.sequenceTextEdit.textCursor()
        #boundary condition
        if crow == -1:
            crow = 0
        cursor.setPosition(crow, QTextCursor.MoveAnchor)       
        cursor.setPosition(crow + 1, QTextCursor.KeepAnchor) 
        self.sequenceEditor.sequenceTextEdit.setTextCursor( cursor )
        
            
    def _applyDescriptor(self):
        """        
        """
        cdes = self.descriptorsTable.currentRow()
        for row in range(self.sequenceTable.rowCount()):
            self._setComboBoxIndexChanged(cdes + 5, tablerow = row, selectedOnly = True)
            
    def _setComboBoxIndexChanged( self, index, tablerow = None, selectedOnly = False):
        """
        """
        if tablerow is None: 
            crow = self.sequenceTable.currentRow()
        else:
            crow = tablerow
        item = self.sequenceTable.item(crow, 2)
        if item:
            self.editingItem = True
            
            cbox = self.sequenceTable.item(crow, 0)
            if not selectedOnly or \
               cbox.checkState() == Qt.Checked:
                item.setText(self.set_names[index])
                item = self.sequenceTable.item(crow, 3)
                aa = self._get_aa_for_index(crow)
                set_name = self.rosetta_set_names[index]
                aa.set_mutation_range(set_name)
                if set_name == "PIKAA":                    
                    aa.set_mutation_descriptor(self.descriptor_list[index])
                item.setText(self._get_mutation_descriptor(aa))        
                for row in range(self.sequenceTable.rowCount()):
                    self.sequenceTable.removeCellWidget(row, 2)
                    self.sequenceTable.setRowHeight(row, 16)
            
            self.editingItem = False
        
    def _addWhatsThisText( self ):
        
        #from ne1_ui.WhatsThisText_for_PropertyManagers import WhatsThis_EditResidues_PropertyManager
        #WhatsThis_EditResidues_PropertyManager(self)
        pass
    
    def _addToolTipText(self):
        #from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_EditProteinDisplayStyle_PropertyManager 
        #ToolTip_EditProteinDisplayStyle_PropertyManager(self)
        pass
        
    def scrollToPosition(self, index):
        """
        Scrolls the Sequence Table to a given sequence position.
        """
        item = self.sequenceTable.item(index, 0)
        if item:
            self.sequenceTable.scrollToItem(item)
        
    def _applyAny(self):
        """
        """
        for row in range(self.sequenceTable.rowCount()):
            self._setComboBoxIndexChanged(0, tablerow = row, selectedOnly = True)

    def _applySame(self):
        """
        """
        for row in range(self.sequenceTable.rowCount()):
            self._setComboBoxIndexChanged(1, tablerow = row, selectedOnly = True)

    def _applyLocked(self):
        """
        """
        for row in range(self.sequenceTable.rowCount()):
            self._setComboBoxIndexChanged(2, tablerow = row, selectedOnly = True)

    def _applyPolar(self):
        """
        """
        for row in range(self.sequenceTable.rowCount()):
            self._setComboBoxIndexChanged(3, tablerow = row, selectedOnly = True)

    def _applyApolar(self):
        """
        """
        for row in range(self.sequenceTable.rowCount()):
            self._setComboBoxIndexChanged(4, tablerow = row, selectedOnly = True)
    
    def resizeEvent(self, event):
        """
        """
        #width = event.size().width()
        w = int(self.applyButtonGrid.width() / 5)
        #self.applyAnyPushButton.setFixedWidth(w)
        #self.applySamePushButton.setFixedWidth(w)
        #self.applyLockedPushButton.setFixedWidth(w)
        #self.applyPolarPushButton.setFixedWidth(w)
        #self.applyApolarPushButton.setFixedWidth(w)
        
        #return
        
        self.descriptorsTable.setColumnWidth(1, 
            self.descriptorsTable.width()-self.descriptorsTable.columnWidth(0)-20)

        self.sequenceTable.setColumnWidth(3, 
            self.sequenceTable.width()-
            (self.sequenceTable.columnWidth(0) +
             self.sequenceTable.columnWidth(1) +
            self.sequenceTable.columnWidth(2))-20)

        
    def _addNewDescriptorTableRow(self, name, descriptor):
        """
        """
        row = self.descriptorsTable.rowCount()
        self.descriptorsTable.insertRow(row)
        
        item_widget = QTableWidgetItem(name)
        item_widget.setFont(self.labelfont)
        item_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
        item_widget.setTextAlignment(Qt.AlignLeft)
        self.descriptorsTable.setItem(row, 0, item_widget)
        self.descriptorsTable.resizeColumnToContents(0)
        
        s = self._makeProperAAString(descriptor)
        item_widget = QTableWidgetItem(s)
        item_widget.setFont(self.descriptorfont)
        item_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
        item_widget.setTextAlignment(Qt.AlignLeft)
        self.descriptorsTable.setItem(row, 1, item_widget)
        self.descriptorsTable.setColumnWidth(1, 
            self.descriptorsTable.width()-self.descriptorsTable.columnWidth(0)-20)
        
        self.descriptorsTable.setRowHeight(row, 16)
        
    def _addNewDescriptor(self):
        """
        """
        self._addNewDescriptorTableRow("New Set", "PGAVILMFWYCSTNQDEHKR")
        self._makeDescriptorUserPref()
        self._updateSetLists()
        
    def _removeDescriptor(self):
        """
        """
        crow = self.descriptorsTable.currentRow()
        if crow >= 0:
            self.descriptorsTable.removeRow(crow)
            self._makeDescriptorUserPref()
            self._updateSetLists()
            
    def _makeDescriptorUserPref(self):
        # Construct a custom descriptors string.
        """
        """
        dstr = ""
        for row in range(self.descriptorsTable.rowCount()):
            item0 = self.descriptorsTable.item(row, 0)
            item1 = self.descriptorsTable.item(row, 1)
            if item0 and \
               item1:
                dstr += item0.text() + \
                     ":" + \
                     item1.text() + \
                     ":"
        env.prefs[proteinCustomDescriptors_prefs_key] = dstr        
            
    def _makeProperAAString(self, string):
        """
        """
        aa_string = str(string).upper()
        new_aa_string = ""
        for i in range(len(self.rosetta_all_set)):
            if aa_string.find(self.rosetta_all_set[i]) == -1:
                new_aa_string += "_"
            else:
                new_aa_string += self.rosetta_all_set[i]
        return new_aa_string
        
    def _sequenceTableItemChanged(self, item):
        """
        """
        if self.editingItem:
            return
        if self.sequenceTable.column(item) == 3:
            self.editingItem = True
            crow = self.sequenceTable.currentRow()
            dstr = self._makeProperAAString(str(item.text()).upper())
            item.setText(dstr)
            aa = self._get_aa_for_index(crow)
            if aa:                
                aa.set_mutation_range("PIKAA")
                aa.set_mutation_descriptor(dstr.replace("_",""))
            item = self.sequenceTable.item(crow, 2)
            if item:
                item.setText("Custom")
            self.editingItem = False
    
    def _descriptorsTableItemChanged(self, item):
        """
        """
        if self.editingItem:
            return
        if self.descriptorsTable.column(item) == 1:
            self.editingItem = True
            item.setText(self._makeProperAAString(str(item.text()).upper()))
            self.editingItem = False

        self._makeDescriptorUserPref()
        self._updateSetLists()

    def _updateSetLists(self):
        """
        """
        self.set_names = self.set_names[:5]
        self.descriptor_list = self.descriptor_list[:5]
        self.rosetta_set_names = self.rosetta_set_names[:5]
        
        dstr = env.prefs[proteinCustomDescriptors_prefs_key].split(":")
        for i in range(len(dstr) / 2):
            self.set_names.append(dstr[2*i])
            self.descriptor_list.append(dstr[2*i+1])
            self.rosetta_set_names.append("PIKAA")
            #self._addNewDescriptorTableRow(dstr[2*i], dstr[2*i+1])

    def _fillDescriptorsTable(self):
        """
        """
        dstr = env.prefs[proteinCustomDescriptors_prefs_key].split(":")
        for i in range(len(dstr) / 2):
            self._addNewDescriptorTableRow(dstr[2*i], dstr[2*i+1])

