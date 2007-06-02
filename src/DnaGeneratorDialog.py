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
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from Utility import geticon, getpixmap
from PropMgrBaseClass import *
from PropMgr_Constants import *

# DNA model type variables.
REDUCED_MODEL=0
ATOMISTIC_MODEL=1
BDNA=0
ZDNA=1

class DnaPropMgr(object, PropMgrBaseClass):
    
    # <title> - the title that appears in the property manager header.
    title = "DNA"
    # <propmgr_name> - the name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    propmgr_name = "pm" + title
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Structures/DNA.png"
    # Reduced model letters (default)
    valid_base_letters = "NATCG"
    
    def __init__(self):
        """Construct the Graphene Property Manager.
        """
        PropMgrBaseClass.__init__(self, self.propmgr_name)
        self.setPropMgrIcon(self.iconPath)
        self.setPropMgrTitle(self.title)
        self.addGroupBoxes()
        self.addBottomSpacer() 
        self.add_whats_this_text()
        
        msg = "Edit the DNA parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert it into the model."
        
        # This causes the "Message" box to be displayed as well.
        # setAsDefault=True causes this message to be reset whenever
        # this PropMgr is (re)displayed via show(). Mark 2007-06-01.
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=True)
        
    def addGroupBoxes(self):
        """Add the 3 groupboxes for the DNA Property Manager.
        """
        self.addGroupBoxSpacer()
        self.pmGroupBox1 = PropMgrGroupBox(self, 
                                           title="Strand Sequence",
                                           titleButton=True)
        self.loadGroupBox1(self.pmGroupBox1)
        
        self.addGroupBoxSpacer()
        self.pmGroupBox2 = PropMgrGroupBox(self, 
                                           title="Representation",
                                           titleButton=True)
        self.loadGroupBox2(self.pmGroupBox2)
        
        self.addGroupBoxSpacer()
        self.pmGroupBox3 = PropMgrGroupBox(self, 
                                           title="DNA Form",
                                           titleButton=True)
        self.loadGroupBox3(self.pmGroupBox3)
        
    def loadGroupBox1(self, pmGroupBox):
        """Load widgets in groubox 1.
        """
        
        self.strandSeqTextEdit = \
            PropMgrTextEdit(pmGroupBox, 
                            label="", 
                            spanWidth=True)
        
        self.connect(self.strandSeqTextEdit,
                     SIGNAL("textChanged()"),
                     self.sequence_changed)
        
        self.connect(self.strandSeqTextEdit,
                     SIGNAL("cursorPositionChanged()"),
                     self.cursorpos_changed) 
        
        self.lengthSpinBox = \
            PropMgrSpinBox(pmGroupBox, 
                            label="Total Length :", 
                            val=0, setAsDefault=False,
                            min=0, max=10000,
                            suffix=' bases')
        
        self.connect(self.lengthSpinBox,
                     SIGNAL("valueChanged(int)"),
                     self.length_changed)
                    
        newBaseChoices = ["N (undefined)", "A", "T", "C", "G"]
        self.newBaseChoiceComboBox= \
            PropMgrComboBox(pmGroupBox,
                            label="New Bases Are :", 
                            choices=newBaseChoices, 
                            idx=0, setAsDefault=True,
                            spanWidth=False)
        
        self.complementPushButton = \
            PropMgrPushButton(pmGroupBox,
                              label="",
                              text="Complement")
        
        self.connect(self.complementPushButton,
                     SIGNAL("clicked()"),
                     self.complementPushButton_clicked)
        
        self.reversePushButton = \
            PropMgrPushButton(pmGroupBox,
                              label="",
                              text="Reverse")
        
        self.connect(self.reversePushButton,
                     SIGNAL("clicked()"),
                     self.reversePushButton_clicked)
        
    def loadGroupBox2(self, pmGroupBox):
        """Load widgets in groubox 2.
        """
        
        modelChoices = ["Reduced", "Atomistic"]
        self.modelComboBox= \
            PropMgrComboBox(pmGroupBox,
                            label="Model :", 
                            choices=modelChoices, 
                            idx=0, setAsDefault=True,
                            spanWidth=False)
        
        self.connect(self.modelComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.modelComboBox_changed)
        
        createChoices = ["Single chunk", "Strand chunks", "Base-pair chunks"]
        self.createComboBox= \
            PropMgrComboBox(pmGroupBox,
                            label="Create :", 
                            choices=createChoices, 
                            idx=0, setAsDefault=True,
                            spanWidth=False)
    
    def loadGroupBox3(self, pmGroupBox):
        """Load widgets in groubox 3.
        """
        
        self.conformationComboBox= \
            PropMgrComboBox(pmGroupBox,
                            label="Conformation :", 
                            choices=["B-DNA"],
                            setAsDefault=True)
        
        self.connect(self.conformationComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.conformationComboBox_changed)
        
        self.strandTypeComboBox= \
            PropMgrComboBox(pmGroupBox,
                            label="Strand Type :", 
                            choices=["Double"],
                            setAsDefault=True)
        
        self.basesPerTurnComboBox= \
            PropMgrComboBox(pmGroupBox,
                            label="Bases Per Turn :", 
                            choices=["10.0", "10.5", "10.67"],
                            setAsDefault=True)
    
    def add_whats_this_text(self):
        """What's This text for some of the widgets in the DNA Property Manager.
        Many are still missing.
        """
        
        self.conformationComboBox.setWhatsThis("""<b>Conformation</b>
        <p>There are three DNA geometries, A-DNA, B-DNA,
        and Z-DNA. Only B-DNA and Z-DNA are currently supported.</p>""")
        
        self.strandTypeComboBox.setWhatsThis("""<b>Strand Type</b>
        <p>DNA strands can be single or double.</p>""")
        
        self.strandSeqTextEdit.setWhatsThis("""<b>Strand Sequence</b>
        <p>Type in the strand sequence you want to generate here (5' => 3')
        </p>""")
        
        self.complementPushButton.setWhatsThis("""<b>Complement</b>
        <p>Change the current strand sequence to the complement strand 
        sequence.</p>""")
        
        self.reversePushButton.setWhatsThis("""<b>Reverse</b>
        <p>Reverse the strand sequence that has been entered.</p>""")
        
        self.modelComboBox.setWhatsThis("""<b>Model</b>
        <p>Determines the type of DNA model that is generated.</p> """)    
        
    def conformationComboBox_changed(self, idx):
        """Slot for the Conformation combobox.
        """
        self.basesPerTurnComboBox.clear()
        
        if idx == BDNA:
            self.basesPerTurnComboBox.insertItem(0, "10.0")
            self.basesPerTurnComboBox.insertItem(1, "10.5")
            self.basesPerTurnComboBox.insertItem(2, "10.67")
        
            #10.5 is the default value for Bases per turn. 
            #So set the current index to 1
            self.basesPerTurnComboBox.setCurrentIndex(1) 
        
        elif idx == ZDNA:
            self.basesPerTurnComboBox.insertItem(0, "12.0")
        
        elif idx == -1: 
            # Cause by clear(). This is tolerable for now. Mark 2007-05-24.
            pass
        
        else:
            print "conformationComboBox_changed(): Error - unknown DNA conformation. Index =", idx
            return
        
    # GroupBox2 slots (and other methods) supporting the Representation groupbox.
        
    def modelComboBox_changed(self, idx):
        """Slot for the Model combobox.
        """
        
        seqlen = self.get_sequence_length()
        
        self.disconnect(self.conformationComboBox,SIGNAL("currentIndexChanged(int)"),
                     self.conformationComboBox_changed)
        
        self.newBaseChoiceComboBox.clear() # Generates signal!
        self.conformationComboBox.clear() # Generates signal!
        self.strandTypeComboBox.clear() # Generates signal!
        
        if idx == REDUCED_MODEL:
            self.newBaseChoiceComboBox.addItem("N (undefined)")
            self.newBaseChoiceComboBox.addItem("A")
            self.newBaseChoiceComboBox.addItem("T")  
            self.newBaseChoiceComboBox.addItem("C")
            self.newBaseChoiceComboBox.addItem("G") 
            
            self.valid_base_letters = "NATCG"
            
            self.conformationComboBox.addItem("B-DNA")
            
            self.strandTypeComboBox.addItem("Double")
            
        elif idx == ATOMISTIC_MODEL:
            self.newBaseChoiceComboBox.addItem("N (random)")
            self.newBaseChoiceComboBox.addItem("A")
            self.newBaseChoiceComboBox.addItem("T")  
            self.newBaseChoiceComboBox.addItem("C")
            self.newBaseChoiceComboBox.addItem("G")
            
            self.valid_base_letters = "NATCG"
                #bruce 070518 added N, meaning a randomly chosen base.
                # This makes several comments/docstrings in other places incorrect
                # (because they were not modular), but I didn't fix them.
            
            self.conformationComboBox.addItem("B-DNA")
            self.conformationComboBox.addItem("Z-DNA")
            
            self.strandTypeComboBox.addItem("Double")
            self.strandTypeComboBox.addItem("Single")
        
        elif idx == -1: 
            # Caused by clear(). This is tolerable for now. Mark 2007-05-24.
            pass
        
        else:
            print "modelComboBox_changed(): Error - unknown model representation. Index =", idx
        
        self.connect(self.conformationComboBox,SIGNAL("currentIndexChanged(int)"),
                     self.conformationComboBox_changed)
    
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
                self.strandSeqTextEdit.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor) # Move the cursor one position to the left. 
            self.strandSeqTextEdit.cut()
            return
        else:
            # If length has increased, add the correct number of base letters to the current strand sequence.
            numNewBases = length - self.get_sequence_length()
            # print "Number of new bases = ", numNewBases
            bases = ''
            base = str(self.newBaseChoiceComboBox.currentText()) # Current base selected in combobox.
            bases = base[0] * numNewBases
            self.strandSeqTextEdit.insertPlainText(bases)
        
    def update_length(self):
        """Update the Length spinbox; always the length of the strand sequence.
        """
        self.disconnect(self.lengthSpinBox,SIGNAL("valueChanged(int)"),
                     self.length_changed)
        self.lengthSpinBox.setValue(self.get_sequence_length())
        self.connect(self.lengthSpinBox,SIGNAL("valueChanged(int)"),
                     self.length_changed)
    
    def sequence_changed(self):       
        """Slot for the strand sequence textedit widget.
        Make sure only A, T, C or G (and N for reduced model) are allowed.
        """
        
        pm_seq = str(self.strandSeqTextEdit.toPlainText()).upper()
        curpos = self.get_cursorpos()
        
        if curpos == 0:
            # User deleted all text in sequence widget.
            self.update_length()
            return
        
        ch = pm_seq[curpos-1] # This is the character the user typed.
        #print "Cursor pos=", curpos, ", Char typed was: ", ch
        
        # Disconnect while we edit the sequence.
        self.disconnect(self.strandSeqTextEdit,SIGNAL("textChanged()"),
                     self.sequence_changed)
        
        # Delete the character the user just typed in. We'll replace it in upper case (if legal) or not (if not legal).
        self.strandSeqTextEdit.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor) # Move the cursor one position to the left. 
        self.strandSeqTextEdit.cut() # Delete (cut) single character user typed in.

        if ch in self.valid_base_letters: # Remove "N: if atomistic model is selected. (later)
            self.strandSeqTextEdit.insertPlainText(ch.upper()) # Change to upper case.
        
        self.connect(self.strandSeqTextEdit,SIGNAL("textChanged()"),
                     self.sequence_changed)
        
        self.update_length() # Update Length spinbox.
    
    def get_sequence_length(self):
        """Returns the number of characters in the strand sequence textedit widget.
        """
        #print "get_sequence_length(): strand length =", len(self.strandSeqTextEdit.toPlainText())   
        return len(self.strandSeqTextEdit.toPlainText())
        
    def get_cursorpos(self):
        """Returns the cursor position in the strand sequence textedit widget.
        """
        cursor = self.strandSeqTextEdit.textCursor()
        return cursor.position()

    def cursorpos_changed(self):
        """Slot called when the cursor position changes.
        """
        # Useful for debugging. mark 2007-05-09.
        # print "cursorpos_changed(): Cursor at position ", self.get_cursorpos()
        return
            
    def complementPushButton_clicked(self):
        """Slot for the Complement button.
        """
        def thunk():
            (seq, allKnown) = self._get_sequence(complement=True, reverse=True)
                #bruce 070518 added reverse=True, since complementing a sequence is usually understood
                # to include reversing the base order, due to the strands in B-DNA being antiparallel.
            self.strandSeqTextEdit.setPlainText(seq)
        self.handlePluginExceptions(thunk)

    def reversePushButton_clicked(self):
        """Slot for the Reverse button.
        """
        def thunk():
            (seq, allKnown) = self._get_sequence(reverse=True)
            self.strandSeqTextEdit.setPlainText(seq)
        self.handlePluginExceptions(thunk)