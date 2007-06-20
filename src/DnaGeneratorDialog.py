# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$

@author: Will Ware
@copyright: Copyright (c) 2007 Nanorex, Inc.  All rights reserved.

Ninad (Nov2006 and later): Ported it to Property manager 
with further enhancements

Mark 2007-05-14:
Organized code, added docstrings and renamed variables to make code more 
readable and understandable.

Jeff 2007-06-13:
- Major code cleanup (removed most abbreviations, standardized method names); 
- Added helper function getDuplexRise.
- Added Duplex Length spinbox and handler methods (duplexLengthChange, 
update duplex length)
- Revamped approach to sequence checking and editing.

Jeff 2007-06-19:
- Renamed class DnaPropMgr to DnaPropertyManager

To do:
- Provide better indication of where the Sequence textedit's insertion 
point is, even when the textedit is not targeted for keyboard input.

"""

import sys
from PyQt4.Qt          import *
from Utility           import geticon, getpixmap
from PropMgrBaseClass  import *
from PropMgr_Constants import *
from Dna               import *
from HistoryWidget     import *

# DNA model type variables
#  (indices for model... and conformation... combo boxes).
REDUCED_MODEL    =  0
ATOMISTIC_MODEL  =  1
BDNA             =  0
ZDNA             =  1

class DnaPropertyManager( object, PropMgrBaseClass, DebugMenuMixin ):
    
    # <title> - the title that appears in the property manager header.
    title = "DNA"

    # <propmgr_name> - the name of this property manager. This will be set 
    # to the name of the PropMgr (this) object via setObjectName().
    propmgr_name = "pm" + title

    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Structures/DNA.png"

    # <valid_base_letters > - Reduced model letters (default)
    valid_base_letters = "NATCG"
    
    # <DGDdebug> - enables history messages within methods for dubugging. :Jeff 2007-06-18
    DGDdebug  =  False

    def __init__( self ):
        """Construct the DNA Generator property manager.
        """
        PropMgrBaseClass.__init__( self, self.propmgr_name )
        DebugMenuMixin._init1( self )

        self.setPropMgrIcon( self.iconPath )
        self.setPropMgrTitle( self.title )
        self.addGroupBoxes()
        self.add_whats_this_text()
        
        msg = "Edit the DNA parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert it into \
        the model."
        
        # This causes the "Message" box to be displayed as well.
        # setAsDefault=True causes this message to be reset whenever
        # this PropMgr is (re)displayed via show(). Mark 2007-06-01.
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  True )

    
    def addGroupBoxes( self ):
        """Add the 3 groupboxes for the DNA Property Manager.
        """
        self.pmGroupBox1 = PropMgrGroupBox( self, 
                                            title       = "Strand Sequence",
                                            titleButton = True)
        self.loadGroupBox1( self.pmGroupBox1 )
        
        self.pmGroupBox2 = PropMgrGroupBox( self, 
                                            title       = "Representation",
                                            titleButton = True)
        self.loadGroupBox2( self.pmGroupBox2 )
        
        self.pmGroupBox3 = PropMgrGroupBox( self, 
                                            title       = "DNA Form",
                                            titleButton = True)
        self.loadGroupBox3( self.pmGroupBox3 )
        
    def loadGroupBox1(self, pmGroupBox):
        """Load widgets in groubox 1.
        """
        self.duplexLengthSpinBox  =  \
            PropMgrDoubleSpinBox( pmGroupBox,
                                  label         =  "Duplex Length: ",
                                  val           =  0,
                                  setAsDefault  =  False,
                                  min           =  0,
                                  max           =  34000,
                                  singleStep    =  self.getDuplexRise("B-DNA"),
                                  decimals      =  3,
                                  suffix        =  ' Angstroms')

        self.connect( self.duplexLengthSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.duplexLengthChanged )

        self.strandLengthSpinBox = \
            PropMgrSpinBox( pmGroupBox, 
                            label         =  "Strand Length :", 
                            val           =  0,
                            setAsDefault  =  False,
                            min           =  0,
                            max           =  10000,
                            suffix        =  ' bases' )
        
        self.connect( self.strandLengthSpinBox,
                      SIGNAL("valueChanged(int)"),
                      self.strandLengthChanged )    # :jbirac 20070613:
                    
        newBaseChoices  =  ["N (undefined)", "A", "T", "C", "G"]

        self.newBaseChoiceComboBox  = \
            PropMgrComboBox( pmGroupBox,
                             label         =  "New Bases Are :", 
                             choices       =  newBaseChoices, 
                             idx           =  0,
                             setAsDefault  =  True,
                             spanWidth     =  False )
        
        self.strandSeqTextEdit = \
            PropMgrTextEdit( pmGroupBox, 
                             label      =  "", 
                             spanWidth  =  True )
        
        self.connect( self.strandSeqTextEdit,
                      SIGNAL("textChanged()"),
                      self.sequenceChanged )
        
        self.connect( self.strandSeqTextEdit,
                      SIGNAL("cursorPositionChanged()"),
                      self.cursorposChanged ) 
        
        self.complementPushButton  = \
            PropMgrPushButton( pmGroupBox,
                               label  =  "",
                               text   =  "Complement" )
        
        self.connect( self.complementPushButton,
                      SIGNAL("clicked()"),
                      self.complementPushButton_clicked )
        
        self.reversePushButton  = \
            PropMgrPushButton( pmGroupBox,
                               label  =  "",
                               text   =  "Reverse" )
        
        self.connect( self.reversePushButton,
                      SIGNAL("clicked()"),
                      self.reversePushButton_clicked )
        
    def loadGroupBox2( self, pmGroupBox ):
        """Load widgets in groubox 2.
        """
        
        modelChoices        =  ["Reduced",\
                                "Atomistic"]
        self.modelComboBox  = \
            PropMgrComboBox( pmGroupBox,
                             label         =  "Model :", 
                             choices       =  modelChoices, 
                             idx           =  0,
                             setAsDefault  =  True,
                             spanWidth     =  False )
        
        self.connect( self.modelComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.modelComboBox_changed )
        
        createChoices        =  ["Single chunk",\
                                 "Strand chunks",\
                                 "Base-pair chunks"]
        self.createComboBox  = \
            PropMgrComboBox( pmGroupBox,
                             label         =  "Create :", 
                             choices       =  createChoices, 
                             idx           =  0,
                             setAsDefault  =  True,
                             spanWidth     =  False )
    
    def loadGroupBox3( self, pmGroupBox ):
        """Load widgets in groubox 3.
        """
        
        self.conformationComboBox  = \
            PropMgrComboBox( pmGroupBox,
                             label         =  "Conformation :", 
                             choices       =  ["B-DNA"],
                             setAsDefault  =  True)
        
        self.connect( self.conformationComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.conformationComboBox_changed )
        
        self.strandTypeComboBox  = \
            PropMgrComboBox( pmGroupBox,
                             label         =  "Strand Type :", 
                             choices       =  ["Double"],
                             setAsDefault  =  True)
        
        self.basesPerTurnComboBox= \
            PropMgrComboBox( pmGroupBox,
                             label         =  "Bases Per Turn :", 
                             choices       =  ["10.0", "10.5", "10.67"],
                             setAsDefault  =  True)
    
    def add_whats_this_text( self ):
        """What's This text for some of the widgets in the 
        DNA Property Manager.  Many are still missing.
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
        
    def conformationComboBox_changed( self, inIndex ):
        """Slot for the Conformation combobox.
        """
        if DGDdebug: env.history.message( greenmsg(  "conformationComboBox_changed: Begin" ) )

        self.basesPerTurnComboBox.clear()
        conformation  =  self.conformationComboBox.currentText()
        
        #if inIndex == BDNA:
        if conformation == "B-DNA":
            self.basesPerTurnComboBox.insertItem(0, "10.0")
            self.basesPerTurnComboBox.insertItem(1, "10.5")
            self.basesPerTurnComboBox.insertItem(2, "10.67")
        
            #10.5 is the default value for Bases per turn. 
            #So set the current index to 1
            self.basesPerTurnComboBox.setCurrentIndex(1)
            
        #if inIndex == ZDNA:
        elif conformation == "Z-DNA":
            self.basesPerTurnComboBox.insertItem(0, "12.0")
        
        elif inIndex == -1: 
            # Caused by clear(). This is tolerable for now. Mark 2007-05-24.
            pass
        
        else:
            if DGDdebug: env.history.message( redmsg(  ("conformationComboBox_changed():    Error - unknown DNA conformation. Index = "+ idx) ))
            #return

        self.duplexLengthSpinBox.setSingleStep(
                self.getDuplexRise(conformation) )

        if DGDdebug: env.history.message( greenmsg( "conformationComboBox_changed: End" ) )

    # GroupBox2 slots (and other methods) supporting the Representation groupbox.
        
    def modelComboBox_changed( self, inIndex ):
        """Slot for the Model combobox.
        """
        if DGDdebug: env.history.message( greenmsg( "modelComboBox_changed: Begin" ))

        conformation  =  modelChoices[ inIndex ]
        
        if DGDdebug: env.history.message( greenmsg( "modelComboBox_changed:    Disconnect conformationComboBox" ))
        self.disconnect( self.conformationComboBox,
                         SIGNAL("currentIndexChanged(int)"),
                         self.conformationComboBox_changed )
        
        self.newBaseChoiceComboBox.clear() # Generates signal!
        self.conformationComboBox.clear() # Generates signal!
        self.strandTypeComboBox.clear() # Generates signal!
        
        #if idx == REDUCED_MODEL:
        if conformation == "Reduced":
            self.newBaseChoiceComboBox.addItem("N (undefined)")
            self.newBaseChoiceComboBox.addItem("A")
            self.newBaseChoiceComboBox.addItem("T")  
            self.newBaseChoiceComboBox.addItem("C")
            self.newBaseChoiceComboBox.addItem("G") 
            
            self.valid_base_letters = "NATCG"
            
            self.conformationComboBox.addItem("B-DNA")
            
            self.strandTypeComboBox.addItem("Double")
            
        #elif idx == ATOMISTIC_MODEL:
        elif conformation == "Atomistic":
            self.newBaseChoiceComboBox.addItem("N (random)")
            self.newBaseChoiceComboBox.addItem("A")
            self.newBaseChoiceComboBox.addItem("T")  
            self.newBaseChoiceComboBox.addItem("C")
            self.newBaseChoiceComboBox.addItem("G")
            
            self.valid_base_letters = "NATCG"
                #bruce 070518 added N, meaning a randomly chosen base.
                # This makes several comments/docstrings in other places 
                # incorrect (because they were not modular), but I didn't 
                # fix them.
            
            self.conformationComboBox.addItem("B-DNA")
            self.conformationComboBox.addItem("Z-DNA")
            
            self.strandTypeComboBox.addItem("Double")
            self.strandTypeComboBox.addItem("Single")
        
        elif inIndex == -1: 
            # Caused by clear(). This is tolerable for now. Mark 2007-05-24.
            pass
        
        else:
            if DGDdebug: env.history.message( redmsg( ("modelComboBox_changed():    Error - unknown model representation. Index = "+ idx)))
        
        if DGDdebug: env.history.message( greenmsg( "modelComboBox_changed:    Reconnect conformationComboBox" ))
        self.connect( self.conformationComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.conformationComboBox_changed)

        if DGDdebug: env.history.message( greenmsg( "modelComboBox_changed: End"))
    
    # GroupBox3 slots (and other methods) supporting the Strand Sequence groupbox.
    
    def getDuplexRise( self, inConformation ):
        if inConformation == 'A-DNA':
            theDna  =  A_Dna()
        elif inConformation == 'B-DNA':
            theDna  =  B_Dna()
        elif inConformation == 'Z-DNA':
            theDna  =  Z_Dna()
            
        return theDna.getBaseSpacing()

    def synchronizeLengths( self ):
        if self.DGDdebug: env.history.message( greenmsg( "synchronizeLengths: Begin"))
        self.updateDuplexLength()
        self.updateStrandLength()
        if self.DGDdebug: env.history.message( greenmsg( "synchronizeLengths: End"))
        return
    
        # Added :jbirac 20070613:     
    def duplexLengthChanged( self, inDuplexLength ):
        """Slot for the duplex length spinbox, 
        called whenever the value of the Duplex Length spinbox changes.
        """
        if self.DGDdebug: env.history.message( greenmsg( "duplexLengthChanged: Begin"))

        conformation     =  self.conformationComboBox.currentText()
        duplexRise       =  self.getDuplexRise( conformation )
        newStrandLength  =  int( inDuplexLength / duplexRise )

        if self.DGDdebug: env.history.message( greenmsg( "duplexLengthChanged:    Change strand length ("+str(newStrandLength)+')'))

        self.strandLengthChanged( newStrandLength )

        if self.DGDdebug: env.history.message( greenmsg( "duplexLengthChanged: End"))


    def updateDuplexLength( self ):    # Added :jbirac 20070615:
        """Update the Duplex Length spinbox; always the length of the 
        strand sequence multiplied by the 'rise' of the duplex.  This
        method is called by slots of other controls (i.e., this itself
        is not a slot.)
        """
        if self.DGDdebug: env.history.message( greenmsg( "updateDuplexLength: Begin"))

        conformation     =  self.conformationComboBox.currentText()
        newDuplexLength  =  self.getDuplexRise( conformation ) \
                          * self.getSequenceLength()
    
        if self.DGDdebug: env.history.message( greenmsg( "updateDuplexLength:    newDuplexLength="+str(newDuplexLength)))

        if self.DGDdebug: env.history.message( greenmsg( "updateDuplexLength:    Disconnect duplexLengthSpinBox"))

        self.disconnect( self.duplexLengthSpinBox,
                         SIGNAL("valueChanged(double)"),
                         self.duplexLengthChanged)

        self.duplexLengthSpinBox.setValue( newDuplexLength )
 
        if self.DGDdebug: env.history.message( greenmsg( "updateDuplexLength:    Reconnect duplexLengthSpinBox"))
        self.connect( self.duplexLengthSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.duplexLengthChanged)

        if self.DGDdebug: env.history.message( greenmsg( "updateDuplexLength: End"))

    # Renamed from length_changed :jbirac 20070613:
    def strandLengthChanged( self, inStrandLength ):
        """Slot for the Strand Length spinbox, 
        called whenever the value of the Strand Length spinbox changes.
        """
        if self.DGDdebug: env.history.message( greenmsg( ("strandLengthChanged: Begin (inStrandLength="+str(inStrandLength)+')')))

        lengthChange  =  inStrandLength - self.getSequenceLength()

        if inStrandLength < 0: 
            if DGDdebug: env.history.message( orangemsg( ("strandLengthChanged:    Illegal strandlength="+str(inStrandLength))))
            env.history.message( orangemsg( "strandLengthChanged: End"))
            return # Should never happen.
        
        if lengthChange < 0:
            if self.DGDdebug: env.history.message( greenmsg( ("strandLengthChanged:    Shorten("+str(lengthChange)+')')))
            # If length is less than the previous length, 
            # simply truncate (to left of cursor) the 
            # current sequence to "length".

            # Select the range of text to be removed
            cursor          =  self.strandSeqTextEdit.textCursor()
            cursorPosition  =  cursor.position()

            # Restrict the removed section of sequence 
            # to beginning of the sequence.
            if cursorPosition < -lengthChange:
                if self.DGDdebug: env.history.message( orangemsg( ("strandLengthChanged:    Restricted shortening ("+str(cursorPosition)+')')))
                cursorPosition  =  0
            else:
                cursorPosition  =  cursorPosition + lengthChange
    
            cursor.setPosition( cursorPosition, QTextCursor.KeepAnchor )
            self.strandSeqTextEdit.setTextCursor( cursor )

            # Remove the selected text by inserting an empty string.
            self.strandSeqTextEdit.insertPlainText("")

        elif lengthChange > 0:
            # If length has increased, add the correct number of base 
            # letters to the current strand sequence.
            numNewBases  =  lengthChange
            if self.DGDdebug: env.history.message( greenmsg( ("strandLengthChanged:    Lengthen ("+str(lengthChange)+')')))

            # Get current base selected in combobox.
            chosenBase  =  str(self.newBaseChoiceComboBox.currentText())[0]

            basesToAdd  =  chosenBase * numNewBases
            self.strandSeqTextEdit.insertPlainText( basesToAdd )

        else:  # :jbirac 20070613:
            if self.DGDdebug: env.history.message( orangemsg( "strandLengthChanged:   Length has not changed; ignore signal." ))

        if self.DGDdebug: env.history.message( greenmsg( "strandLengthChanged: End"))
        return

    # Renamed from updateLength :jbirac 20070613:
    def updateStrandLength( self ):
        """Update the Strand Length spinbox; 
        always the length of the strand sequence.
        """

        if self.DGDdebug: env.history.message( greenmsg( "updateStrandLength: Begin"))

        if self.DGDdebug: env.history.message( greenmsg( ("updateStrandLength:    Disconnect strandLengthSpinBox")))
        self.disconnect( self.strandLengthSpinBox,
                         SIGNAL("valueChanged(int)"),
                         self.strandLengthChanged )  

        self.strandLengthSpinBox.setValue( self.getSequenceLength() )

        if self.DGDdebug: env.history.message( greenmsg( ("updateStrandLength:    Reconnect strandLengthSpinBox")))
        self.connect( self.strandLengthSpinBox,
                      SIGNAL("valueChanged(int)"),
                      self.strandLengthChanged )
        
        if self.DGDdebug: env.history.message( greenmsg( "updateStrandLength: End"))
        return
    
    def sequenceChanged( self ):
        """Slot for the Strand Sequence textedit widget.
        Make sure only A, T, C or G (and N for reduced model) are allowed.  
        Assumes the sequence changed directly by user's keystroke in the 
        textedit.  Other methods...
        """        
        if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged: Begin") )
        
        cursorPosition  =  self.getCursorPosition()
        
        # How has the text changed?
        if cursorPosition == 0:
            # User deleted all text in sequence widget.
            if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged:    User deleted all text.") )
            self.updateStrandLength()
            self.updateDuplexLength()
        else:
            # Disconnect while we edit the sequence.
            if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged:    Disconnect strandSeqTextEdit") )
            self.disconnect( self.strandSeqTextEdit,
                             SIGNAL("textChanged()"),
                             self.sequenceChanged )
        
            # Verify that all characters in the (new) sequence are uppercase.
            theSequence  =  \
                    str( self.strandSeqTextEdit.toPlainText() ).upper()
            
            # Verify that all characters (bases) in the sequence are "valid".
            for basePosition in range( len(theSequence) ):
                if theSequence[basePosition] not in self.valid_base_letters:
                    invalidSequence  =  True
                    if self.DGDdebug: 
                        env.history.message( 
                                redmsg( "sequenceChanged:   Illegal Sequence character ("\
                                        +theSequence[theBasePosition] \
                                        +" at "+str(theBasePosition)+')'))
            
            # Insert verified sequence and restore cursor position.
            if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged:    Inserting refined sequence") )
            self.strandSeqTextEdit.setText( theSequence )
            cursor  =  self.strandSeqTextEdit.textCursor()
            cursor.setPosition( cursorPosition )
            self.strandSeqTextEdit.setTextCursor( cursor )
            
            # Reconnect to respond when the sequence is changed.
            if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged:    Reconnect strandSeqTextEdit") )
            self.connect( self.strandSeqTextEdit,
                          SIGNAL("textChanged()"),
                          self.sequenceChanged )

        self.synchronizeLengths()
        if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged: End" ) )
        return

    def getSequenceLength( self ):
        """Returns the number of characters in 
        the strand sequence textedit widget.
        """
        return len( self.strandSeqTextEdit.toPlainText() )
        
    def getCursorPosition( self ):
        """Returns the cursor position in the 
        strand sequence textedit widget.
        """
        cursor  =  self.strandSeqTextEdit.textCursor()
        return cursor.position()

    def cursorposChanged(self):
        """Slot called when the cursor position changes.
        """
        cursor  =  self.strandSeqTextEdit.textCursor()

        if self.DGDdebug: 
            env.history.message( greenmsg( "cursorposChanged: Selection ("
                                           + str(cursor.selectionStart())
                                           + " to "
                                           + str(cursor.selectionEnd())+')' ) )
        return
            
    def complementPushButton_clicked(self):
        """Slot for the Complement button.
        """
        def thunk():
            (seq, allKnown) = self._get_sequence( complement  =  True,
                                                  reverse     =  True )
                #bruce 070518 added reverse=True, since complementing a 
                # sequence is usually understood to include reversing the 
                # base order, due to the strands in B-DNA being antiparallel.
            self.strandSeqTextEdit.setPlainText(seq)
        self.handlePluginExceptions(thunk)

    def reversePushButton_clicked(self):
        """Slot for the Reverse button.
        """
        def thunk():
            (seq, allKnown) = self._get_sequence( reverse  =  True )
            self.strandSeqTextEdit.setPlainText( seq )
        self.handlePluginExceptions( thunk )
