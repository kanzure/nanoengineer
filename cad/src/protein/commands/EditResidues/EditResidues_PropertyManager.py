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
import os, time, fnmatch, string, re
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

        msg = "Edit residues."
        
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
        
        change_connect(self.applyDescriptorPushButton,
                         SIGNAL("clicked()"),
                         self._applyDescriptor)
        
        change_connect(self.sequenceTable,
                         SIGNAL("cellClicked(int, int)"),
                         self._sequenceTableCellChanged)
        
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
        self.sequenceEditor = self.win.createProteinSequenceEditorIfNeeded()
        
        self.sequenceEditor.hide()

        PM_Dialog.show(self)

        # Update all PM widgets, then establish their signal-slot connections.
        # note: It is important to update the widgets *first* since doing
        # it in the reverse order will generate signals when updating
        # the PM widgets (via updateDnaDisplayStyleWidgets()), causing
        # unneccessary repaints of the model view.
        
        self.connect_or_disconnect_signals(isConnect = True)

        self._fillSequenceTable()
        

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

        self.labelfont = QFont("Helvetica", 12)
        
        self.descriptorfont = QFont("Courier New", 12)        

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
            
        self.set_names = ["Any", "Same", "Locked", "Polar", "Apolar"]
        self.rosetta_set_names = ["ALLAA", "NATAA", "NATRO", "POLAR", "APOLA"]
        self.descriptor_list = ["PGAVILMFWYCSTNQDEHKR", 
                                "____________________", 
                                "____________________", 
                                "_________YCSTNQDEHKR", 
                                "PGAVILMFW___________"]
        
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
            text       =  "POLAR",
            setAsDefault  =  True)
        
        self.applyApolarPushButton = PM_PushButton( pmGroupBox,
            text       =  "APOLA",
            setAsDefault  =  True)
        
        self.applyAnyPushButton.setFixedHeight(25)
        #self.applyAnyPushButton.setFixedWidth(50)
        
        self.applySamePushButton.setFixedHeight(25)
        #self.applySamePushButton.setFixedWidth(50)

        self.applyLockedPushButton.setFixedHeight(25)
        #self.applyLockedPushButton.setFixedWidth(50)

        self.applyPolarPushButton.setFixedHeight(25)
        #self.applyPolarPushButton.setFixedWidth(50)

        self.applyApolarPushButton.setFixedHeight(25)
        #self.applyApolarPushButton.setFixedWidth(50)
        
        applyButtonList = [('PM_PushButton', self.applyAnyPushButton, 0, 0),
            ('PM_PushButton', self.applySamePushButton, 1, 0),
            ('PM_PushButton', self.applyLockedPushButton, 2, 0),
            ('PM_PushButton', self.applyPolarPushButton, 3, 0),
            ('PM_PushButton', self.applyApolarPushButton, 4, 0) ]

        self.applyButtonGrid = PM_WidgetGrid( pmGroupBox, 
                                              label = "Apply standard set",
                                              alignment = "Center", 
                                              widgetList = applyButtonList)

        self.descriptorsTable = PM_TableWidget( pmGroupBox,
                                                label = "Custom descriptors")
        
        self.descriptorsTable.setFixedHeight(100)
        self.descriptorsTable.setRowCount(len(self.set_names))
        self.descriptorsTable.setColumnCount(2)
        self.descriptorsTable.verticalHeader().setVisible(False)
        self.descriptorsTable.horizontalHeader().setVisible(False)
        self.descriptorsTable.setGridStyle(Qt.NoPen)

        for index in range(len(self.set_names)):
            item_widget = QTableWidgetItem(self.set_names[index])
            item_widget.setFont(self.labelfont)
            item_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            item_widget.setTextAlignment(Qt.AlignCenter)
            self.descriptorsTable.setItem(index, 0, item_widget)
            
            item_widget = QTableWidgetItem(self.descriptor_list[index])
            item_widget.setFont(self.descriptorfont)
            item_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            item_widget.setTextAlignment(Qt.AlignCenter)
            self.descriptorsTable.setItem(index, 1, item_widget)

            self.descriptorsTable.setRowHeight(index, 16)
            pass
        
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
            
        self.headerdata = ['', 'ID', 'Set', 'Descriptor']

        self.recenterViewCheckBox  = \
            PM_CheckBox( pmGroupBox,
                         text          =  "Re-center view on selected residue",
                         setAsDefault  =  True,
                         widgetColumn  = 0, 
                         state         = Qt.Checked)
        
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
        
        self.sequenceTable.setHorizontalHeaderLabels(self.headerdata) 
        ###self._fillSequenceTable()
        

    def _fillSequenceTable(self):
        """
        """        
        
        self.setComboBox = QComboBox()
        
        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk():
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
                    
                    item_widget = QTableWidgetItem("Any")
                    item_widget.setFont(self.labelfont)
                    item_widget.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item_widget.setTextAlignment(Qt.AlignCenter)
                    self.sequenceTable.setItem(index, 2, item_widget)
                    
                    aa_string = self._get_mutation_descriptor(
                        self._get_aa_for_index(index))

                    item_widget = QTableWidgetItem(aa_string)
                    item_widget.setFont(self.descriptorfont)
                    self.sequenceTable.setItem(index, 3, item_widget)
        
                    self.sequenceTable.setRowHeight(index, 16)
                    
        self.sequenceTable.resizeColumnsToContents()
        
        self.sequenceTable.setColumnWidth(0, 35)
        self.sequenceTable.setColumnWidth(2, 80)
        
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
        aa_string = "PGAVILMFWYCSTNQDEHKR"
        
        range = aa.get_mutation_range()                    
        if range == "NATRO" or \
           range == "NATAA":
            code = aa.get_one_letter_code()                    
            aa_string = re.sub("[^"+code+"]",'_', aa_string)
        elif range == "POLAR":
            aa_string = "_________YCSTNQDEHKR"
        elif range == "APOLA":
            aa_string = "PGAVILMFW___________"

        return aa_string
    
    def _get_aa_for_index(self, index, expand=False):
        """
        """
        # Center on a selected amino acid.
        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk():
                chunk.protein.set_current_amino_acid_index(index)
                current_aa = chunk.protein.get_current_amino_acid()
                if expand:
                    chunk.protein.collapse_all_rotamers()
                    chunk.protein.expand_rotamer(current_aa)
                return current_aa 

        return None
    
    def _sequenceTableCellChanged(self, crow, ccol):
        #print "CELL CHANGED: ", (crow, ccol)
        item = self.sequenceTable.item(crow, ccol)
        #print "ITEM = ", item
        
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
                             SIGNAL("currentIndexChanged(int)"),
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
        
    def _applyDescriptor(self):
        """        
        """
        cdes = self.descriptorsTable.currentRow()
        for row in range(self.sequenceTable.rowCount()):
            #print "row = ", row
            self._setComboBoxIndexChanged(cdes, tablerow = row, selectedOnly = True)
            
    def _setComboBoxIndexChanged( self, index, tablerow = None, selectedOnly = False):
        """
        """
        #print "INDEX = ", index
        if tablerow is None: 
            crow = self.sequenceTable.currentRow()
        else:
            crow = tablerow
        #print "current row: ", crow
        item = self.sequenceTable.item(crow, 2)
        if item:
            cbox = self.sequenceTable.item(crow, 0)
            if not selectedOnly or \
               cbox.checkState() == Qt.Checked:
                item.setText(self.set_names[index])
                item = self.sequenceTable.item(crow, 3)
                aa = self._get_aa_for_index(crow)
                aa.set_mutation_range(self.rosetta_set_names[index])
                item.setText(self._get_mutation_descriptor(aa))
        
        ###self._write_resfile()
        
    def _write_resfile(self):
        from protein.model.Protein import write_rosetta_resfile
        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk():
                write_rosetta_resfile("/Users/piotr/test.resfile", chunk)
                return
        
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
    
    def _addNewDescriptor(self):
        """
        """
        ### self.descriptorsTable.insertRow
        