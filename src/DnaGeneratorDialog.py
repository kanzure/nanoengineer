# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$

Created by Will

Ninad (Nov2006 and later): Ported it to Property manager 
with further enhancements

Mark 2007-05-14: Organized code, added docstrings and renamed variables to make
 code more readable and understandable.

"""

import sys
from PyQt4 import Qt, QtCore, QtGui
from Utility import geticon, getpixmap
from PyQt4.Qt import *
from PropertyManagerMixin import PropMgrBaseClass
from PropMgr_Constants import *

# DNA model type variables.
REDUCED_MODEL=0
ATOMISTIC_MODEL=1
BDNA=0
ZDNA=1

class DnaPropMgr(object, PropMgrBaseClass):
    
    valid_base_letters = "NATCG" # Reduced model letters.
    
    def __init__(self):
        """Construct the DNA Property Manager.
        """
        PropMgrBaseClass.__init__(self)
        self.setPropMgrIcon('ui/actions/Tools/Build Structures/DNA.png')
        self.setPropMgrTitle("DNA")
        self.addGroupBoxes()
        self.addBottomSpacer() 
        self.add_whats_this_text()
        self.connect_or_disconnect_signals(connect=True)
        
        msg = "Edit the DNA parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert it into the model."
        self.insertHtmlMsg(msg)
        
    def addGroupBoxes(self):
        """Add the 3 groupboxes for the DNA Property Manager.
        """
        self.addGroupBox1("DNA Parameters")
        self.addGroupBox2("Representation")
        self.addGroupBox3("Strand Sequence")
              
    def addGroupBox1(self, title):
        """Adds a spacer, then it creates layout and widgets for the 
        "DNA Parameters" groupbox.
        """
        
        self.addGroupBoxSpacer()
                
        self.pmGroupBox1 = QtGui.QGroupBox(self)
        self.pmGroupBox1.setObjectName("pmGroupBox1")
        
        self.pmGroupBox1.setAutoFillBackground(True) 
        palette =  self.getGroupBoxPalette()
        self.pmGroupBox1.setPalette(palette)
        
        styleSheet = self.getGroupBoxStyleSheet()        
        self.pmGroupBox1.setStyleSheet(styleSheet)
        
        # Create vertical box layout
        self.GrpBox1MainVBoxLayout = QtGui.QVBoxLayout(self.pmGroupBox1)
        self.GrpBox1MainVBoxLayout.setMargin(0)
        self.GrpBox1MainVBoxLayout.setSpacing(2)

        # Title button for groupbox1
        
        self.pmGroupBoxBtn1 = self.getGroupBoxTitleButton(
            title, self.pmGroupBox1)
        
        self.GrpBox1MainVBoxLayout.addWidget(self.pmGroupBoxBtn1)
   
        # Create grid layout
        self.GrpBox1GridLayout1 = QtGui.QGridLayout()
        self.GrpBox1GridLayout1.setMargin(2)
        self.GrpBox1GridLayout1.setSpacing(4)
        
        # "Conformation" label.
        self.dnaConformation_lbl = QtGui.QLabel(self.pmGroupBox1)
        self.dnaConformation_lbl.setAlignment(Qt.AlignRight|
                                              Qt.AlignTrailing|
                                              Qt.AlignVCenter)
        self.dnaConformation_lbl.setObjectName("dnaConformation_lbl")
        self.dnaConformation_lbl.setText("Conformation :")
        self.GrpBox1GridLayout1.addWidget(self.dnaConformation_lbl,0,0,1,1)

        # "Conformation" combobox.
        self.dnaConformation_combox = QtGui.QComboBox(self.pmGroupBox1)
        self.dnaConformation_combox.setObjectName("dnaConformation_combox")
        self.dnaConformation_combox.addItem("B-DNA")
        self.GrpBox1GridLayout1.addWidget(self.dnaConformation_combox,0,1,1,1)
        
        # "Strand Type" label.
        self.strandType_lbl = QtGui.QLabel(self.pmGroupBox1)
        self.strandType_lbl.setAlignment(Qt.AlignRight|
                                         Qt.AlignTrailing|
                                         Qt.AlignVCenter)
        self.strandType_lbl.setObjectName("strandType_lbl")
        self.strandType_lbl.setText("Strand Type :")
        self.GrpBox1GridLayout1.addWidget(self.strandType_lbl,1,0,1,1)

        # "Strand Type" combobox.
        self.strandType_combox = QtGui.QComboBox(self.pmGroupBox1)
        self.strandType_combox.setObjectName("strandType_combox")
        self.strandType_combox.addItem("Double")
        self.GrpBox1GridLayout1.addWidget(self.strandType_combox,1,1,1,1)
        
        # "Bases Per Turn" label.
        self.basesPerTurn_lbl = QLabel()
        self.basesPerTurn_lbl.setAlignment(Qt.AlignRight|
                                           Qt.AlignTrailing|
                                           Qt.AlignVCenter)
        
        self.basesPerTurn_lbl.setText("Bases Per Turn :")
        self.GrpBox1GridLayout1.addWidget(self.basesPerTurn_lbl, 2,0,1,1,)
        
        # "Bases Per Turn" combobox.
        self.basesPerTurn_combox = QtGui.QComboBox(self.pmGroupBox1)
        self.basesPerTurn_combox.insertItem(0, "10.0")
        self.basesPerTurn_combox.insertItem(1, "10.5")
        self.basesPerTurn_combox.insertItem(2, "10.67")
        self.GrpBox1GridLayout1.addWidget(self.basesPerTurn_combox, 2,1,1,1,)
        
        #10.5 is the default value for Bases per turn. 
        #So set the current index to 1
        self.basesPerTurn_combox.setCurrentIndex(1) 
        
        self.GrpBox1MainVBoxLayout.addLayout(self.GrpBox1GridLayout1)
        
        self.pmMainVboxLO.addWidget(self.pmGroupBox1) # Add groupbox
        
    
    def addGroupBox2(self, title):
        """Adds a spacer, then it creates layout and widgets for
        the "Representation" groupbox.
        """
        
        self.addGroupBoxSpacer()
        
        self.pmGroupBox2 = QtGui.QGroupBox(self)
        self.pmGroupBox2.setObjectName("pmGroupBox2")
        
        self.pmGroupBox2.setAutoFillBackground(True) 
        palette =  self.getGroupBoxPalette()
        self.pmGroupBox2.setPalette(palette)
        
        styleSheet = self.getGroupBoxStyleSheet()        
        self.pmGroupBox2.setStyleSheet(styleSheet)
        
        # Create vertical box layout
        self.GrpBox2MainVBoxLayout = QtGui.QVBoxLayout(self.pmGroupBox2)
        self.GrpBox2MainVBoxLayout.setMargin(0)
        self.GrpBox2MainVBoxLayout.setSpacing(2)
        
        # "Representation" title button for groupbox3
        
        self.pmGroupBoxBtn2 = self.getGroupBoxTitleButton(
            title, self.pmGroupBox2)
        
        self.GrpBox2MainVBoxLayout.addWidget(self.pmGroupBoxBtn2)
        
        # Create grid layout
        self.GrpBox2GridLayout1 = QtGui.QGridLayout()
        self.GrpBox2GridLayout1.setMargin(2)
        self.GrpBox2GridLayout1.setSpacing(4)
        
        # "Model" label and combobox.
        
        self.model_combox_lbl = QLabel() # "Model :" label, defined in another file. mark 2007-05-09.
        self.model_combox_lbl.setAlignment(Qt.AlignRight|
                                           Qt.AlignTrailing|
                                           Qt.AlignVCenter)
        self.model_combox_lbl.setText("Model :")
        self.GrpBox2GridLayout1.addWidget(self.model_combox_lbl,0,0,1,1)
                
        self.model_combox = QtGui.QComboBox(self.pmGroupBox2)
        self.model_combox.insertItem(1, "Reduced")
        self.model_combox.insertItem(2, "Atomistic")
        
        self.GrpBox2GridLayout1.addWidget(self.model_combox,0,1,1,1)
        
        # "Create" label and combobox.
        
        self.dnaChunkOptions_lbl = QtGui.QLabel(self.pmGroupBox2)
        self.dnaChunkOptions_lbl.setText("Create :")
        self.dnaChunkOptions_lbl.setAlignment(Qt.AlignRight|
                                              Qt.AlignTrailing|
                                              Qt.AlignVCenter)
        self.GrpBox2GridLayout1.addWidget(self.dnaChunkOptions_lbl,1,0,1,1)
        
        self.dnaChunkOptions_combox = QtGui.QComboBox(self.pmGroupBox2)
        self.dnaChunkOptions_combox.addItem("DNA Chunk")
        self.dnaChunkOptions_combox.addItem("Strand Chunks")  
        self.dnaChunkOptions_combox.addItem("Base-Pair Chunks")   
                
        self.GrpBox2GridLayout1.addWidget(self.dnaChunkOptions_combox,1,1,1,1)
        
        self.GrpBox2MainVBoxLayout.addLayout(self.GrpBox2GridLayout1)
        
        self.pmMainVboxLO.addWidget(self.pmGroupBox2) # Add groupbox
                
    
    def addGroupBox3(self, title):
        """Adds a spacer, then it creates layout and widgets for 
        the "Strand Sequence" groupbox.
        """
        
        self.addGroupBoxSpacer()
        
        self.pmGroupBox3 = QtGui.QGroupBox(self)
        self.pmGroupBox3.setObjectName("pmGroupBox3")
        
        self.pmGroupBox3.setAutoFillBackground(True) 
        palette = self.getGroupBoxPalette()
        self.pmGroupBox3.setPalette(palette)
        
        styleSheet = self.getGroupBoxStyleSheet()        
        self.pmGroupBox3.setStyleSheet(styleSheet)
        
        # Create vertical box layout
        self.GrpBox3MainVBoxLayout = QtGui.QVBoxLayout(self.pmGroupBox3)
        self.GrpBox3MainVBoxLayout.setMargin(0)
        self.GrpBox3MainVBoxLayout.setSpacing(2)
        
        # Title button
        self.pmGroupBoxBtn3 = self.getGroupBoxTitleButton(
            title, self.pmGroupBox3)
        
        self.GrpBox3MainVBoxLayout.addWidget(self.pmGroupBoxBtn3)
        
        # Create grid layout
        self.GrpBox3GridLayout1 = QtGui.QGridLayout()
        self.GrpBox3GridLayout1.setMargin(2)
        self.GrpBox3GridLayout1.setSpacing(4)
        
        # "Total Length" Label
        self.length_lbl = QtGui.QLabel(self.pmGroupBox3)
        self.length_lbl.setAlignment(Qt.AlignRight|
                                     Qt.AlignTrailing|
                                     Qt.AlignVCenter)
        self.length_lbl.setText("Total Length :")
        
        self.GrpBox3GridLayout1.addWidget(self.length_lbl,0,0,1,1)
        
        # "Total Length" SpinBox
        self.length_spinbox = QtGui.QSpinBox(self.pmGroupBox3)
        self.length_spinbox.setMinimum(0)
        self.length_spinbox.setMaximum(10000)
        self.length_spinbox.setValue(0)
        self.length_spinbox.setSuffix(" bases")
        self.GrpBox3GridLayout1.addWidget(self.length_spinbox,0,1,1,1)    
        
        # "New Bases Are" label
        self.newBaseOptions_lbl = QtGui.QLabel(self.pmGroupBox3)
        self.newBaseOptions_lbl.setAlignment(Qt.AlignRight|
                                             Qt.AlignTrailing|
                                             Qt.AlignVCenter)
        self.newBaseOptions_lbl.setText("New Bases Are :")
        
        self.GrpBox3GridLayout1.addWidget(self.newBaseOptions_lbl,1,0,1,1)
        
        # "New Bases Are" combobox
        self.newBaseOptions_combox = QtGui.QComboBox(self.pmGroupBox3)
        self.newBaseOptions_combox.addItem("N (undefined)")
        self.newBaseOptions_combox.addItem("A")
        self.newBaseOptions_combox.addItem("T")  
        self.newBaseOptions_combox.addItem("C")
        self.newBaseOptions_combox.addItem("G")
        self.GrpBox3GridLayout1.addWidget(self.newBaseOptions_combox,1,1,1,1)

        # "Complement" button
        self.complement_btn = QtGui.QPushButton(self.pmGroupBox3)
        self.complement_btn.setAutoDefault(False)
        self.complement_btn.setObjectName("complement_btn")
        self.complement_btn.setText("Complement")
        self.GrpBox3GridLayout1.addWidget(self.complement_btn,2,0,1,1)

        # "Reverse" button
        self.reverse_btn = QtGui.QPushButton(self.pmGroupBox3)
        self.reverse_btn.setAutoDefault(False)
        self.reverse_btn.setObjectName("reverse_btn")
        self.reverse_btn.setText("Reverse")
        self.GrpBox3GridLayout1.addWidget(self.reverse_btn,2,1,1,1)
        
        # "Base sequence" TextEdit
        self.base_textedit = QtGui.QTextEdit(self.pmGroupBox3)
        self.base_textedit.setObjectName("base_textedit")
        self.base_textedit.setMinimumSize(200,70)
        self.base_textedit.setSizePolicy(QSizePolicy.MinimumExpanding,
                                         QSizePolicy.Minimum)
        self.GrpBox3GridLayout1.addWidget(self.base_textedit,3,0,1,2)
        
        self.GrpBox3MainVBoxLayout.addLayout(self.GrpBox3GridLayout1)
        
        self.pmMainVboxLO.addWidget(self.pmGroupBox3) # Add groupbox


    def add_whats_this_text(self):
        """What's This text for some of the widgets in the DNA Property Manager.
        Many are still missing.
        """
        
        self.dnaConformation_combox.setWhatsThis("""<b>Conformation</b>
        <p>There are three DNA geometries, A-DNA, B-DNA,
        and Z-DNA. Only B-DNA and Z-DNA are currently supported.</p>""")
        
        self.strandType_combox.setWhatsThis("""<b>Strand Type</b>
        <p>DNA strands can be single or double.</p>""")
        
        self.base_textedit.setWhatsThis("""<b>Strand Sequence</b>
        <p>Type in the strand sequence you want to generate here (5' => 3')
        </p>""")
        
        self.complement_btn.setWhatsThis("""<b>Complement</b>
        <p>Change the current strand sequence to the complement strand 
        sequence.</p>""")
        
        self.reverse_btn.setWhatsThis("""<b>Reverse</b>
        <p>Reverse the strand sequence that has been entered.</p>""")
        
        self.model_combox.setWhatsThis("""<b>Model</b>
        <p>Determines the type of DNA model that is generated.</p> """)
        
    def connect_or_disconnect_signals(self, connect=True):
        """Connect/disconnect this pmgr's widgets signals to/from their slots.
        If <connect> is False, disconnect all slots listed.
        """
        
        if connect:
            contype = self.connect
        else:
            contype = self.disconnect
        
        # Groupbox Toggle Buttons.
        contype(self.pmGroupBoxBtn1,SIGNAL("clicked()"),
                self.toggle_pmGroupBox1)
        contype(self.pmGroupBoxBtn2, SIGNAL("clicked()"), 
                self.toggle_pmGroupBox2) 
        contype(self.pmGroupBoxBtn3,SIGNAL("clicked()"),
                self.toggle_pmGroupBox3)
       
        # Groupbox1.
        contype(self.dnaConformation_combox,
                SIGNAL("currentIndexChanged(int)"),
                self.dnaConformation_combox_changed)
        
        # Groupbox2.
        contype(self.model_combox,SIGNAL("currentIndexChanged(int)"),
                self.model_combox_changed)
        
        # Groupbox3.
        contype(self.length_spinbox,SIGNAL("valueChanged(int)"),
                self.length_changed)
        contype(self.base_textedit,SIGNAL("textChanged()"),
                self.sequence_changed)
        contype(self.base_textedit,SIGNAL("cursorPositionChanged()"),
                self.cursorpos_changed)
        contype(self.complement_btn,SIGNAL("clicked()"),
                self.complement_btn_clicked)
        contype(self.reverse_btn,SIGNAL("clicked()"),
                self.reverse_btn_clicked)
        
    # GroupBox1 slots (and other methods) supporting the DNA Parameters groupbox.
        
    def dnaConformation_combox_changed(self, idx):
        """Slot for the Conformation combobox.
        """
        self.basesPerTurn_combox.clear()
        
        if idx == BDNA:
            self.basesPerTurn_combox.insertItem(0, "10.0")
            self.basesPerTurn_combox.insertItem(1, "10.5")
            self.basesPerTurn_combox.insertItem(2, "10.67")
        
            #10.5 is the default value for Bases per turn. 
            #So set the current index to 1
            self.basesPerTurn_combox.setCurrentIndex(1) 
        
        elif idx == ZDNA:
            self.basesPerTurn_combox.insertItem(0, "12.0")
            
        else:
            print "dnaConformation_combox_changed(): Error - unknown DNA conformation. Index =", idx
            return
        
    # GroupBox2 slots (and other methods) supporting the Representation groupbox.
        
    def model_combox_changed(self, idx):
        """Slot for the Model combobox.
        """
        
        seqlen = self.get_sequence_length()
        self.base_textedit.clear()
        
        self.disconnect(self.dnaConformation_combox,SIGNAL("currentIndexChanged(int)"),
                     self.dnaConformation_combox_changed)
        
        self.newBaseOptions_combox.clear() # Generates signal!
        self.dnaConformation_combox.clear() # Generates signal!
        self.strandType_combox.clear() # Generates signal!
        
        if idx == REDUCED_MODEL:
            self.newBaseOptions_combox.addItem("N (undefined)")
            self.newBaseOptions_combox.addItem("A")
            self.newBaseOptions_combox.addItem("T")  
            self.newBaseOptions_combox.addItem("C")
            self.newBaseOptions_combox.addItem("G") 
            
            seq = "N" * seqlen
            self.base_textedit.insertPlainText(seq)
            self.valid_base_letters = "NATCG"
            
            self.dnaConformation_combox.addItem("B-DNA")
            
            self.strandType_combox.addItem("Double")
            
        elif idx == ATOMISTIC_MODEL:
            self.newBaseOptions_combox.addItem("A")
            self.newBaseOptions_combox.addItem("T")  
            self.newBaseOptions_combox.addItem("C")
            self.newBaseOptions_combox.addItem("G")
            self.valid_base_letters = "ATCG"
            
            self.dnaConformation_combox.addItem("B-DNA")
            self.dnaConformation_combox.addItem("Z-DNA")
            
            self.strandType_combox.addItem("Double")
            self.strandType_combox.addItem("Single")
            
        else:
            print "model_combox_changed(): Error - unknown model representation. Index =", idx
        
        self.connect(self.dnaConformation_combox,SIGNAL("currentIndexChanged(int)"),
                     self.dnaConformation_combox_changed)
    
    # GroupBox3 slots (and other methods) supporting the Strand Sequence groupbox.
    
    def length_changed(self, length):
        """Slot for the length spinbox.
        """
        #print "New length = ", length, ", Current length =", self.get_sequence_length()
        if length < 0: return # Should never happen.
        
        if length < self.get_sequence_length():
            # If length is less than the previous length, simply truncate the current sequence to "length".
            if length < 0: return # Should never happen.
            for p in range(self.get_sequence_length()-length):
                self.base_textedit.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor) # Move the cursor one position to the left. 
            self.base_textedit.cut()
            return
        else:
            # If length has increased, add the correct number of base letters to the current strand sequence.
            numNewBases = length - self.get_sequence_length()
            # print "Number of new bases = ", numNewBases
            bases = ''
            base = str(self.newBaseOptions_combox.currentText()) # Current base selected in combobox.
            bases = base[0] * numNewBases
            self.base_textedit.insertPlainText(bases)
        
    def update_length(self):
        """Update the Length spinbox; always the length of the strand sequence.
        """
        self.disconnect(self.length_spinbox,SIGNAL("valueChanged(int)"),
                     self.length_changed)
        self.length_spinbox.setValue(self.get_sequence_length())
        self.connect(self.length_spinbox,SIGNAL("valueChanged(int)"),
                     self.length_changed)
    
    def sequence_changed(self):       
        """Slot for the strand sequence textedit widget.
        Make sure only A, T, C or G (and N for reduced model) are allowed.
        """
        
        pm_seq = str(self.base_textedit.toPlainText()).upper()
        curpos = self.get_cursorpos()
        
        if curpos == 0:
            # User deleted all text in sequence widget.
            self.update_length()
            return
        
        ch = pm_seq[curpos-1] # This is the character the user typed.
        #print "Cursor pos=", curpos, ", Char typed was: ", ch
        
        # Disconnect while we edit the sequence.
        self.disconnect(self.base_textedit,SIGNAL("textChanged()"),
                     self.sequence_changed)
        
        # Delete the character the user just typed in. We'll replace it in upper case (if legal) or not (if not legal).
        self.base_textedit.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor) # Move the cursor one position to the left. 
        self.base_textedit.cut() # Delete (cut) single character user typed in.

        if ch in self.valid_base_letters: # Remove "N: if atomistic model is selected. (later)
            self.base_textedit.insertPlainText(ch.upper()) # Change to upper case.
        
        self.connect(self.base_textedit,SIGNAL("textChanged()"),
                     self.sequence_changed)
        
        self.update_length() # Update Length spinbox.
    
    def get_sequence_length(self):
        """Returns the number of characters in the strand sequence textedit widget.
        """
        #print "get_sequence_length(): strand length =", len(self.base_textedit.toPlainText())   
        return len(self.base_textedit.toPlainText())
        
    def get_cursorpos(self):
        """Returns the cursor position in the strand sequence textedit widget.
        """
        cursor = self.base_textedit.textCursor()
        return cursor.position()

    def cursorpos_changed(self):
        """Slot called when the cursor position changes.
        """
        # Useful for debugging. mark 2007-05-09.
        # print "cursorpos_changed(): Cursor at position ", self.get_cursorpos()
        return
            
    def complement_btn_clicked(self):
        """Slot for the Complement button.
        """
        def thunk():
            (seq, allKnown) = self._get_sequence(complement=True)
            self.base_textedit.setPlainText(seq)
        self.handlePluginExceptions(thunk)

    def reverse_btn_clicked(self):
        """Slot for the Reverse button.
        """
        def thunk():
            (seq, allKnown) = self._get_sequence(reverse=True)
            self.base_textedit.setPlainText(seq)
        self.handlePluginExceptions(thunk)
        
        
    # Collapse/expand toggle slots for groupbox buttons.
        
    def toggle_pmGroupBox1(self): # DNA Parameters groupbox
        self.toggle_groupbox(self.pmGroupBoxBtn1, 
                             self.dnaConformation_lbl, self.dnaConformation_combox,
                             self.strandType_lbl, self.strandType_combox,
                             self.basesPerTurn_lbl, self.basesPerTurn_combox)

    def toggle_pmGroupBox2(self): # Represenation groupbox
        self.toggle_groupbox(self.pmGroupBoxBtn2, 
                             self.model_combox_lbl, self.model_combox,
                             self.dnaChunkOptions_lbl, self.dnaChunkOptions_combox )
    
    def toggle_pmGroupBox3(self): # Strand Sequence groupbox
        self.toggle_groupbox(self.pmGroupBoxBtn3, 
                             self.length_lbl, self.length_spinbox,
                             self.newBaseOptions_lbl, self.newBaseOptions_combox,
                             self.base_textedit,
                             self.complement_btn, self.reverse_btn)