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

To do (Jeff):
 1) <DONE> Replace "Complement" and "Reverse" buttons with an "Actions" combobox.
    - Items are "Actions", separator, "Complement" and "Reverse".
    - Always revert to "Actions" after user makes any choice.
    - Choosing "Actions" does NOT send a signal.
    - Maybe an "Apply" button if 
 2) <TABLED> Cursor/insertion point visibility:
    - changes to the interior (not end) of the sequence/strand length must 
      be changed manually via direct selection and editing.
    - try using a blinking vertical bar via HTML to represent the cursor
 3) <DONE> Spinboxes should change the length from the end only of the strand, 
    regardless of the current cursor position or selection.
"""

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QRegExp
from PyQt4.Qt import QString
from PyQt4.Qt import QTextCursor
from PyQt4.Qt import QTextOption

import env
from Dna import Dna
from Dna import A_Dna
from Dna import B_Dna
from Dna import Z_Dna
from HistoryWidget import redmsg
from HistoryWidget import greenmsg
from HistoryWidget import orangemsg

from Utility import geticon, getpixmap
from PropMgrBaseClass import PropMgrBaseClass
from PropMgrBaseClass import PropMgrGroupBox
from PropMgrBaseClass import PropMgrTextEdit
from PropMgrBaseClass import PropMgrSpinBox
from PropMgrBaseClass import PropMgrComboBox
from PropMgrBaseClass import PropMgrPushButton
from PropMgrBaseClass import PropMgrDoubleSpinBox
from debug import DebugMenuMixin

# DNA model type variables
#  (indices for model... and conformation... combo boxes).
REDUCED_MODEL    =  0
ATOMISTIC_MODEL  =  1
BDNA             =  0
ZDNA             =  1

class DnaPropertyManager( object, PropMgrBaseClass, DebugMenuMixin ):
    
    # <title> - the title that appears in the property manager header.
    title  =  "DNA"

    # <propmgr_name> - the name of this property manager. This will be set 
    # to the name of the PropMgr (this) object via setObjectName().
    propmgr_name  = title

    # <iconPath> - full path to PNG file that appears in the header.
    iconPath  =  "ui/actions/Tools/Build Structures/DNA.png"
    
    # <validSymbols> - Miscellaneous symbols that may appear in sequence 
    # (but are ignored). The hyphen '-' is a special case that must be
    # dealt with individually; it is not included because it can confuse 
    # regular expressions.
    validSymbols  =  QString(' <>~!@#%&_+`=$*()[]{}|^\'"\\.;:,/?')

    # <DGDdebug> - enables history messages within methods for dubugging. :Jeff 2007-06-18
    DGDdebug  =  True

    # The following class variables guarantee the UI's menu items
    # are synchronized with their action code.  The arrays should
    # not be changed, unless an item is removed or inserted.
    # Changes should be made via only the _action... variables.
    # e.g., Change _action_Complement from "Complement" 
    #       to "Complement Sequences". The menu item will
    #       change and its related code will need no update.
    _action_Complement           =  "Complement"
    _action_Reverse              =  "Reverse"
    _action_RemoveUnrecognized   =  'Remove unrecognized letters'
    _action_ConvertUnrecognized  =  'Convert unrecognized letters to "N"'

    actionChoices       =  [ "Action",
                             "---",
                             _action_Complement,
                             _action_Reverse,
                             _action_RemoveUnrecognized,
                             _action_ConvertUnrecognized ]

    _modeltype_Reduced    =  "Reduced"
    _modeltype_Atomistic  =  "Atomistic"
    modelChoices          =  [ _modeltype_Reduced,\
                               _modeltype_Atomistic ]

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
        # Duplex Length
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

        # Strand Length
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
                    
        # New Base choices
        newBaseChoices  =  []
        for theBase in Dna.basesDict.keys():
            newBaseChoices  =  newBaseChoices \
                             + [ theBase + ' (' \
                                + Dna.basesDict[theBase]['Name'] + ')' ]
            
        try:
            defaultBaseChoice = Dna.basesDict.keys().index('N')
        except:
            defaultBaseChoice = 0

        self.newBaseChoiceComboBox  = \
            PropMgrComboBox( pmGroupBox,
                             label         =  "New Bases Are :", 
                             choices       =  newBaseChoices, 
                             idx           =  defaultBaseChoice,
                             setAsDefault  =  True,
                             spanWidth     =  False )

        # Strand Sequence
        self.strandSeqTextEdit = \
            PropMgrTextEdit( pmGroupBox, 
                             label      =  "", 
                             spanWidth  =  True )
        
        self.strandSeqTextEdit.setCursorWidth(2)
        self.strandSeqTextEdit.setWordWrapMode( QTextOption.WrapAnywhere )
        
        self.connect( self.strandSeqTextEdit,
                      SIGNAL("textChanged()"),
                      self.sequenceChanged )
        
        self.connect( self.strandSeqTextEdit,
                      SIGNAL("cursorPositionChanged()"),
                      self.cursorPosChanged ) 
        
        # Actions
        self.actionsComboBox  = \
            PropMgrComboBox( pmGroupBox,
                             label         =  '', 
                             choices       =  self.actionChoices, 
                             idx           =  0,
                             setAsDefault  =  True,
                             spanWidth     =  True )

        self.connect( self.actionsComboBox,
                      SIGNAL("activated(QString)"),
                      self.actionsComboBox_changed )

    def loadGroupBox2( self, pmGroupBox ):
        """Load widgets in groubox 2.
        """
        
        self.modelComboBox  = \
            PropMgrComboBox( pmGroupBox,
                             label         =  "Model :", 
                             choices       =  self.modelChoices, 
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
        
        self.actionsComboBox.setWhatsThis("""<b>Action</b>
        <p>Select an action to perform on the sequence.</p>""")
        
        self.modelComboBox.setWhatsThis("""<b>Model</b>
        <p>Determines the type of DNA model that is generated.</p> """)    
        
    def conformationComboBox_changed( self, inIndex ):
        """Slot for the Conformation combobox.
        """
        if self.DGDdebug: env.history.message( greenmsg(  "conformationComboBox_changed: Begin" ) )

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
            if self.DGDdebug: env.history.message( redmsg(  ("conformationComboBox_changed():    Error - unknown DNA conformation. Index = "+ inIndex) ))
            #return

        self.duplexLengthSpinBox.setSingleStep(
                self.getDuplexRise(conformation) )

        if self.DGDdebug: env.history.message( greenmsg( "conformationComboBox_changed: End" ) )

    # GroupBox2 slots (and other methods) supporting the Representation groupbox.
        
    def modelComboBox_changed( self, inIndex ):
        """Slot for the Model combobox.
        """
        if self.DGDdebug: env.history.message( greenmsg( "modelComboBox_changed: Begin" ))

        conformation  =  self.modelChoices[ inIndex ]
        
        if self.DGDdebug: env.history.message( greenmsg( "modelComboBox_changed:    Disconnect conformationComboBox" ))
        self.disconnect( self.conformationComboBox,
                         SIGNAL("currentIndexChanged(int)"),
                         self.conformationComboBox_changed )
        
        self.newBaseChoiceComboBox.clear() # Generates signal!
        self.conformationComboBox.clear() # Generates signal!
        self.strandTypeComboBox.clear() # Generates signal!
        
        if conformation == self._modeltype_Reduced:
            self.newBaseChoiceComboBox.addItem("N (undefined)")
            self.newBaseChoiceComboBox.addItem("A")
            self.newBaseChoiceComboBox.addItem("T")  
            self.newBaseChoiceComboBox.addItem("C")
            self.newBaseChoiceComboBox.addItem("G") 
            
            #self.valid_base_letters = "NATCG"
            
            self.conformationComboBox.addItem("B-DNA")
            
            self.strandTypeComboBox.addItem("Double")
            
        elif conformation == self._modeltype_Atomistic:
            self.newBaseChoiceComboBox.addItem("N (random)")
            self.newBaseChoiceComboBox.addItem("A")
            self.newBaseChoiceComboBox.addItem("T")  
            self.newBaseChoiceComboBox.addItem("C")
            self.newBaseChoiceComboBox.addItem("G")
            
        # Removed. :jbirac: 20070630
            #self.valid_base_letters = "NATCG"
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
            if self.DGDdebug: env.history.message( redmsg( ("modelComboBox_changed():    Error - unknown model representation. Index = "+ inIndex)))
        
        if self.DGDdebug: env.history.message( greenmsg( "modelComboBox_changed:    Reconnect conformationComboBox" ))
        self.connect( self.conformationComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.conformationComboBox_changed)

        if self.DGDdebug: env.history.message( greenmsg( "modelComboBox_changed: End"))
    
    # GroupBox3 slots (and other methods) supporting the Strand Sequence groupbox.
    
    def getDuplexRise( self, inConformation ):
        """Return the 'rise' between base pairs of the 
        specified DNA type (conformation).
        """
        
        if inConformation == 'A-DNA':
            theDna  =  A_Dna()
        elif inConformation == 'B-DNA':
            theDna  =  B_Dna()
        elif inConformation == 'Z-DNA':
            theDna  =  Z_Dna()
            
        return theDna.getBaseSpacing()

    def synchronizeLengths( self ):
        """Guarantees the values of the duplex length and strand length 
        spinboxes agree with the strand sequence (textedit).
        """
        if self.DGDdebug: env.history.message( greenmsg( "synchronizeLengths: Begin"))
        self.updateStrandLength()
        self.updateDuplexLength()
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
        newStrandLength  =  inDuplexLength / duplexRise + 0.5
        newStrandLength  =  int( newStrandLength )

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

        theSequence   =  self.getPlainSequence()
        sequenceLen   =  len( theSequence )
        lengthChange  =  inStrandLength - self.getSequenceLength()

        # Preserve the cursor's position/selection 
        cursor          =  self.strandSeqTextEdit.textCursor()
        #cursorPosition  =  cursor.position()
        selectionStart  =  cursor.selectionStart()
        selectionEnd    =  cursor.selectionEnd()

        if inStrandLength < 0: 
            if self.DGDdebug: env.history.message( orangemsg( ("strandLengthChanged:    Illegal strandlength="+str(inStrandLength))))
            env.history.message( orangemsg( "strandLengthChanged: End"))
            return # Should never happen.
        
        if lengthChange < 0:
            if self.DGDdebug: env.history.message( greenmsg( ("strandLengthChanged:    Shorten("+str(lengthChange)+')')))
            # If length is less than the previous length, 
            # simply truncate the current sequence.

            theSequence.chop( -lengthChange )

        elif lengthChange > 0:
            # If length has increased, add the correct number of base 
            # letters to the current strand sequence.
            numNewBases  =  lengthChange
            if self.DGDdebug: env.history.message( greenmsg( ("strandLengthChanged:    Lengthen ("+str(lengthChange)+')')))

            # Get current base selected in combobox.
            chosenBase  =  str(self.newBaseChoiceComboBox.currentText())[0]

            basesToAdd  =  chosenBase * numNewBases
            #self.strandSeqTextEdit.insertPlainText( basesToAdd )
            theSequence.append( basesToAdd )

        else:  # :jbirac 20070613:
            if self.DGDdebug: env.history.message( orangemsg( "strandLengthChanged:   Length has not changed; ignore signal." ))

        self.setSequence( theSequence )

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
        Assumes the sequence changed directly by user's keystroke in the 
        textedit.  Other methods...
        """        
        if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged: Begin") )
        
        cursorPosition  =  self.getCursorPosition()
        theSequence     =  self.getPlainSequence()
        
        # Disconnect while we edit the sequence.
        if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged:    Disconnect strandSeqTextEdit") )
        self.disconnect( self.strandSeqTextEdit,
                         SIGNAL("textChanged()"),
                         self.sequenceChanged )
    
        # How has the text changed?
        if theSequence.length() == 0:  # There is no sequence.
            if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged: User deleted all text.") )
            self.updateStrandLength()
            self.updateDuplexLength()
        else:
            # Insert the sequence; it will be "stylized" by setSequence().
            if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged:    Inserting refined sequence") )
            self.setSequence( theSequence )
        
        # Reconnect to respond when the sequence is changed.
        if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged:    Reconnect strandSeqTextEdit") )
        self.connect( self.strandSeqTextEdit,
                      SIGNAL("textChanged()"),
                      self.sequenceChanged )

        self.synchronizeLengths()

        if self.DGDdebug: env.history.message( greenmsg( "sequenceChanged: End" ) )
        return

    def removeUnrecognized( self ):
        """Removes any unrecognized/invalid characters (alphanumeric or
        symbolic) from the sequence.
        """
        outSequence  =  self.strandSeqTextEdit.toPlainText()
        theString = ''
        for theBase in Dna.basesDict:
            theString  =  theString + theBase
        theString  =  '[^' + str( QRegExp.escape(theString) ) + ']'
        outSequence.remove(QRegExp( theString ))
        self.setSequence( outSequence )
        return outSequence

    def convertUnrecognized( self,
                             inSequence   =  None, 
                             inSelection  =  None ):
        """Substitutes an 'N' for any unrecognized/invalid characters 
        (alphanumeric or symbolic) in the sequence
        """
        if inSequence == None:
            outSequence  =  self.strandSeqTextEdit.toPlainText()
        else:
            outSequence  =  QString( inSequence )

        theString = ''
        for theBase in Dna.basesDict:
            theString  =  theString + theBase
        theString  =  '[^' + str( QRegExp.escape(theString) ) + ']'
        outSequence.replace( QRegExp(theString), 'N' )
        return outSequence

    def getPlainSequence( self, inOmitSymbols = False ):
        """Returns a plain text QString (without HTML stylization)
        of the current sequence.  All characters are preserved (unless
        specified explicitly), including valid base letters, punctuation 
        symbols, whitespace and invalid letters.
        """
        outSequence  =  self.strandSeqTextEdit.toPlainText()

        if inOmitSymbols:
            # This may look like a sloppy piece of code, but Qt's QRegExp
            # class makes it pretty tricky to remove all punctuation.
            theString  =  '[<>' \
                           + str( QRegExp.escape(self.validSymbols) ) \
                           + ']|-'

            outSequence.remove(QRegExp( theString ))
            
        return outSequence

    def stylizeSequence( self, inSequence ):
        """Converts a plain text string of a sequence (including optional 
        symbols) to an HTML rich text string.
        Returns: QString
        """
        outSequence  =  str(inSequence)
        # Verify that all characters (bases) in the sequence are "valid".
        invalidSequence   =  False
        basePosition      =  0
        sequencePosition  =  0
        invalidStartTag   =  "<b><font color=black>"
        invalidEndTag     =  "</b>"
        previousChar      =  chr(1)  # Null character; may be revised.

        # Some characters must be substituted to preserve 
        # whitespace and tags in HTML code.
        substituteDict    =  { ' ':'&#032;', '<':'&lt;', '>':'&gt;' }
        baseColorsDict    =  { 'A':'darkorange', 
                               'C':'cyan', 
                               'G':'green', 
                               'T':'teal', 
                               'N':'orchid' }

        while basePosition < len(outSequence):

            theSeqChar  =  outSequence[basePosition]

            if ( theSeqChar in Dna.basesDict
                 or theSeqChar in self.validSymbols ):

                # Close any preceding invalid sequence segment.
                if invalidSequence == True:
                    outSequence      =  outSequence[:basePosition] \
                                      + invalidEndTag \
                                      + outSequence[basePosition:]
                    basePosition    +=  len(invalidEndTag)
                    invalidSequence  =  False

                # Color the valid characters.
                if theSeqChar != previousChar:
                    # We only need to insert 'color' tags in places where
                    # the adjacent characters are different.
                    if theSeqChar in baseColorsDict:
                        theTag  =  '<font color=' \
                                + baseColorsDict[ theSeqChar ] \
                                + '>'
                    elif not previousChar in self.validSymbols:
                        # The character is a 'valid' symbol to be greyed
                        # out.  Only one 'color' tag is needed for a 
                        # group of adjacent symbols.
                        theTag  =  '<font color=dimgrey>'
                    else:
                        theTag  =  ''

                    outSequence   =  outSequence[:basePosition] \
                                   + theTag + outSequence[basePosition:]
                        
                    basePosition +=  len(theTag)

                    # Any <space> character must be substituted with an 
                    # ASCII code tag because the HTML engine will collapse 
                    # whitespace to a single <space> character; whitespace 
                    # is truncated from the end of HTML by default.
                    # Also, many symbol characters must be substituted
                    # because they confuse the HTML syntax.
                    #if str( outSequence[basePosition] ) in substituteDict:
                    if outSequence[basePosition] in substituteDict:
                        #theTag = substituteDict[theSeqChar]
                        theTag = substituteDict[ outSequence[basePosition] ]
                        outSequence   =  outSequence[:basePosition] \
                                       + theTag \
                                       + outSequence[basePosition + 1:]
                        basePosition +=  len(theTag) - 1
                        
 
            else:
                # The sequence character is invalid (but permissible).
                # Tags (e.g., <b> and </b>) must be inserted at both the
                # beginning and end of a segment of invalid characters.
                if invalidSequence == False:
                    outSequence      =  outSequence[:basePosition] \
                                      + invalidStartTag \
                                      + outSequence[basePosition:]
                    basePosition    +=  len(invalidStartTag)
                    invalidSequence  =  True

            basePosition +=  1
            previousChar  =  theSeqChar
            #basePosition +=  1

        # Specify that theSequence is definitely HTML format, because 
        # Qt can get confused between HTML and Plain Text.
        outSequence  =  "<html>" + outSequence
        outSequence +=  "</html>"

        return outSequence
    
    def setSequence( self,
                     inSequence,
                     inStylize        =  True,
                     inRestoreCursor  =  True ):
        """ Replace the current strand sequence with the new sequence text.
        NOTE: Signals/slots must be managed before calling this method.  
        The textChanged() signal will be sent to any connected widgets.
        """
        cursor          =  self.strandSeqTextEdit.textCursor()
        selectionStart  =  cursor.selectionStart()
        selectionEnd    =  cursor.selectionEnd()
        
        if inStylize:
            inSequence  =  self.stylizeSequence( inSequence )

        self.strandSeqTextEdit.insertHtml( inSequence )

        cursor.setPosition( selectionStart, 
                            QTextCursor.MoveAnchor )
        cursor.setPosition( selectionEnd, 
                             QTextCursor.KeepAnchor )
        self.strandSeqTextEdit.setTextCursor( cursor )
        return
    
    def getSequenceLength( self ):
        """Returns the number of characters in 
        the strand sequence textedit widget.
        """
        theSequence  =  self.getPlainSequence( inOmitSymbols = True )
        outLength    =  theSequence.length()

        return outLength
        
    def getCursorPosition( self ):
        """Returns the cursor position in the 
        strand sequence textedit widget.
        """
        cursor  =  self.strandSeqTextEdit.textCursor()
        return cursor.position()

    def cursorPosChanged(self):
        """Slot called when the cursor position changes.
        """
        cursor  =  self.strandSeqTextEdit.textCursor()

        if self.DGDdebug: 
            env.history.message( greenmsg( "cursorPosChanged: Selection ("
                                           + str(cursor.selectionStart())
                                           + " thru "
                                           + str(cursor.selectionEnd())+')' ) )
        return
            
    def actionsComboBox_changed( self, inMenuEntry ):
        """Handles user's selection of Actions combobox.
        """
        self.actionsComboBox.setCurrentIndex( 0 )
        return self.invokeAction( inMenuEntry )

    def invokeAction( self, inActionName ):
        """Invokes the action inActionName
        """
        outResult  =  None

        if inActionName == self._action_Complement:
            outResult  =  self.complementSequence()
        elif inActionName == self._action_Reverse:
            outResult  =  self.reverseSequence()
        elif inActionName == self._action_ConvertUnrecognized:
            outResult  =  self.convertUnrecognized()
            self.setSequence( outResult )
        elif inActionName == self._action_RemoveUnrecognized:
            outResult  =  self.removeUnrecognized()

        return outResult
        
    def complementSequence(self):
        """Complements the current sequence.
        """
        def thunk():
            (seq, allKnown) = self._get_sequence( complement  =  True,
                                                  reverse     =  True )
                #bruce 070518 added reverse=True, since complementing a 
                # sequence is usually understood to include reversing the 
                # base order, due to the strands in B-DNA being antiparallel.
            self.setSequence( seq ) #, inStylize  =  False )
            #self.sequenceChanged()
        self.handlePluginExceptions( thunk )

    def reverseSequence(self):
        """Reverse the current sequence.
        """
        def thunk():
            (seq, allKnown) = self._get_sequence( reverse  =  True )
            self.setSequence( seq ) #, inStylize  =  False )
            #self.sequenceChanged()
        self.handlePluginExceptions( thunk )
