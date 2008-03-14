# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaGeneratorPropertyManager.py

WARNING: this file has been mostly superseded by DnaDuplexPropertyManager.py.

@author: Will Ware
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

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

Mark 2007-08-07: 
- Now uses new PM module. Also renamed DnaPropertyManager to 
DnaGeneratorPropertyManager.

Mark 2007-10-18: 
- Major rewrite of this module, superseding it --
  DnaDuplexPropertyManager.py.
"""

# To do:
# 1) <TABLED> Cursor/insertion point visibility:
#    - changes to the interior (not end) of the sequence/strand length must 
#      be changed manually via direct selection and editing.
#    - try using a blinking vertical bar via HTML to represent the cursor
# 2) Actions (reverse, complement, etc in _getSequence() should not purge
#    unrecognized characters.

import foundation.env as env

from dna.model.Dna_Constants import basesDict, dnaDict
from dna.model.Dna_Constants import getComplementSequence
from dna.model.Dna_Constants import getReverseSequence
from dna.model.Dna_Constants import replaceUnrecognized

from utilities.Log import redmsg, greenmsg, orangemsg

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QRegExp
from PyQt4.Qt import QString
from PyQt4.Qt import QTextCursor
from PyQt4.Qt import QTextOption

from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_TextEdit      import PM_TextEdit

from PM.PM_Dialog import PM_Dialog
from widgets.DebugMenuMixin import DebugMenuMixin

# DNA model type variables
#  (indices for model... and conformation... comboboxes).
#@REDUCED_MODEL    =  0
#@ATOMISTIC_MODEL  =  1
BDNA             =  0
ZDNA             =  1

# Do not commit with DEBUG set to True. Mark 2007-08-07
DEBUG = False

class DnaGeneratorPropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The DnaGeneratorPropertyManager class provides a Property Manager 
    for the "Build > Atoms" command.
    
    @ivar title: The title that appears in the property manager header.
    @type title: str
    
    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str
    
    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    
    @ivar validSymbols: Miscellaneous symbols that may appear in the sequence 
                        (but are ignored). The hyphen '-' is a special case
                        that must be dealt with individually; it is not 
                        included because it can confuse regular expressions.
    @type validSymbols: QString
    """
    
    title         =  "DNA"
    pmName        =  title
    iconPath      =  "ui/actions/Tools/Build Structures/DNA.png"
    validSymbols  =  QString(' <>~!@#%&_+`=$*()[]{}|^\'"\\.;:,/?')

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

    _actionChoices       =  [ "Action",
                              "---",
                              _action_Complement,
                              _action_Reverse,
                              _action_RemoveUnrecognized,
                              _action_ConvertUnrecognized ]

    _modeltype_PAM3       =  "PAM3"
    _modeltype_PAM5       =  "PAM5"
    _modeltype_Atomistic  =  "Atomistic" # deprecated
    _modelChoices          =  [ _modeltype_PAM3,
                                _modeltype_PAM5 ]

    def __init__( self ):
        """
        Constructor for the DNA Generator property manager.
        """
        PM_Dialog.__init__( self, self.pmName, self.iconPath, self.title )
        DebugMenuMixin._init1( self )

        
        msg = "Edit the DNA parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert it into \
        the model."
        
        # This causes the "Message" box to be displayed as well.
        # setAsDefault=True causes this message to be reset whenever
        # this PM is (re)displayed via show(). Mark 2007-06-01.
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  True )
    
    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self, title = "Strand Sequence" )
        self._loadGroupBox1( self._pmGroupBox1 )
        
        self._pmGroupBox2 = PM_GroupBox( self, title = "DNA Parameters" )
        self._loadGroupBox2( self._pmGroupBox2 )
        
        self._pmGroupBox3 = PM_GroupBox( self, title = "Endpoints" )
        self._loadGroupBox3( self._pmGroupBox3 )
        
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 1.
        """
        # Duplex Length
        self.duplexLengthSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Duplex Length: ",
                              value         =  0,
                              setAsDefault  =  False,
                              minimum       =  0,
                              maximum       =  34000,
                              singleStep    =  self.getDuplexRise("B-DNA"),
                              decimals      =  3,
                              suffix        =  ' Angstroms')

        self.connect( self.duplexLengthSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.duplexLengthChanged )

        # Strand Length
        self.strandLengthSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Strand Length :", 
                        value         =  0,
                        setAsDefault  =  False,
                        minimum       =  0,
                        maximum       =  10000,
                        suffix        =  ' bases' )
        
        self.connect( self.strandLengthSpinBox,
                      SIGNAL("valueChanged(int)"),
                      self.strandLengthChanged )                    
        # New Base choices
        newBaseChoices  =  []
        for theBase in basesDict.keys():
            newBaseChoices  =  newBaseChoices \
                            + [ theBase + ' (' \
                            + basesDict[theBase]['Name'] + ')' ]
            
        try:
            defaultBaseChoice = basesDict.keys().index('N')
        except:
            defaultBaseChoice = 0

        # Strand Sequence
        self.sequenceTextEdit = \
            PM_TextEdit( pmGroupBox, 
                         label      =  "", 
                         spanWidth  =  True )
        
        self.sequenceTextEdit.setCursorWidth(2)
        self.sequenceTextEdit.setWordWrapMode( QTextOption.WrapAnywhere )
        
        self.connect( self.sequenceTextEdit,
                      SIGNAL("textChanged()"),
                      self.sequenceChanged )
        
        self.connect( self.sequenceTextEdit,
                      SIGNAL("cursorPositionChanged()"),
                      self.cursorPosChanged ) 
        
        # Actions
        self.actionsComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  '', 
                         choices       =  self._actionChoices, 
                         index         =  0,
                         setAsDefault  =  True,
                         spanWidth     =  True )

        # If SIGNAL("activate(const QString&)") is used, we get a TypeError.
        # This is a bug that needs Bruce. Using currentIndexChanged(int) as
        # a workaround, but there is still a bug when the "Reverse" action 
        # is selected. Mark 2007-08-15
        self.connect( self.actionsComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.actionsComboBoxChanged )
    
    def _loadGroupBox2( self, pmGroupBox ):
        """
        Load widgets in group box 2.
        """
        
        self.modelComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Model :", 
                         choices       =  self._modelChoices,
                         setAsDefault  =  True)
        
        self.conformationComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Conformation :", 
                         choices       =  ["B-DNA"],
                         setAsDefault  =  True)
    
        self.connect( self.conformationComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.conformationComboBoxChanged )
        
        self.basesPerTurnComboBox= \
            PM_ComboBox( pmGroupBox,
                         label         =  "Bases Per Turn :", 
                         choices       =  ["10.0", "10.5", "10.67"],
                         setAsDefault  =  True)
        
        # I may decide to reintroduce "base-pair chunks" at a later time.
        # Please talk to me if you have a strong feeling about including
        # this. Mark 2007-08-19.
        createChoices        =  ["Strand chunks", \
                                 "Single chunk" ]
                                 #@ "Base-pair chunks"] 
                                 
        self.createComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Create :", 
                         choices       =  createChoices, 
                         index         =  0,
                         setAsDefault  =  True,
                         spanWidth     =  False )
    
    def _loadGroupBox3(self, pmGroupBox):
        """
        Load widgets in group box 3.
        """
        
        self._endPoint1GroupBox = PM_GroupBox( pmGroupBox, title = "Endpoint1" )
        self._endPoint2GroupBox = PM_GroupBox( pmGroupBox, title = "Endpoint2" )
        
        # Point 1
        self.x1SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint1GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/X_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
        self.y1SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint1GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Y_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
        self.z1SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint1GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Z_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
        # Point 2
        self.x2SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint2GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/X_Coordinate.png",
                              value         =  10.0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
        self.y2SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint2GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Y_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
        self.z2SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint2GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Z_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
    def _addWhatsThisText( self ):
        """
        What's This text for some of the widgets in the 
        DNA Property Manager.  
        
        @note: Many PM widgets are still missing their "What's This" text.
        """
        
        self.conformationComboBox.setWhatsThis("""<b>Conformation</b>
        <p>There are three DNA geometries, A-DNA, B-DNA,
        and Z-DNA. Only B-DNA and Z-DNA are currently supported.</p>""")
        
        self.sequenceTextEdit.setWhatsThis("""<b>Strand Sequence</b>
        <p>Type in the strand sequence you want to generate here (5' => 3')<br>
        <br>
        Recognized base letters:<br>
        <br>
        A = Adenosine<br>
        C = Cytosine<br> 
        G = Guanosine<br>
        T = Thymidine<br>
        N = aNy base<br>
        X = Unassigned<br>
        <br>
        Other base letters currently recognized:<br>
        <br>
        B = C,G, or T<br>
        D = A,G, or T<br>
        H = A,C, or T<br>
        V = A,C, or G<br>
        R = A or G (puRine)<br>
        Y = C or T (pYrimidine)<br>
        K = G or T (Keto)<br>
        M = A or C (aMino)<br>
        S = G or C (Strong -3H bonds)<br>
        W = A or T (Weak - 2H bonds)<br>
        </p>""")
        
        self.actionsComboBox.setWhatsThis("""<b>Action</b>
        <p>Select an action to perform on the sequence.</p>""")
        
    def conformationComboBoxChanged( self, inIndex ):
        """
        Slot for the Conformation combobox. It is called whenever the
        Conformation choice is changed.
        
        @param inIndex: The new index.
        @type  inIndex: int
        """
        self.basesPerTurnComboBox.clear()
        conformation  =  self.conformationComboBox.currentText()
        
        if conformation == "B-DNA":
            self.basesPerTurnComboBox.insertItem(0, "10.0")
            self.basesPerTurnComboBox.insertItem(1, "10.5")
            self.basesPerTurnComboBox.insertItem(2, "10.67")
        
            #10.5 is the default value for Bases per turn. 
            #So set the current index to 1
            self.basesPerTurnComboBox.setCurrentIndex(1)
            
        elif conformation == "Z-DNA":
            self.basesPerTurnComboBox.insertItem(0, "12.0")
        
        elif inIndex == -1: 
            # Caused by clear(). This is tolerable for now. Mark 2007-05-24.
            conformation = "B-DNA" # Workaround for "Restore Defaults".
            pass
        
        else:
            msg = redmsg("conformationComboBoxChanged(): \
            Error - unknown DNA conformation. Index = "+ inIndex)
            env.history.message(msg)

        self.duplexLengthSpinBox.setSingleStep(
                self.getDuplexRise(conformation) )
        
    def modelComboBoxChanged( self, inIndex ):
        """
        Slot for the Model combobox. It is called whenever the
        Model choice is changed.
        
        @param inIndex: The new index.
        @type  inIndex: int
        """
        conformation  =  self._modelChoices[ inIndex ]
            
        self.disconnect( self.conformationComboBox,
                         SIGNAL("currentIndexChanged(int)"),
                         self.conformationComboBoxChanged )
        
        self.conformationComboBox.clear() # Generates signal!
        
        if conformation == self._modeltype_PAM3:            
            self.conformationComboBox.addItem("B-DNA")
            
        elif conformation == self._modeltype_PAM5:            
            self.conformationComboBox.addItem("B-DNA")
            
        elif conformation == self._modeltype_Atomistic:            
            self.conformationComboBox.addItem("B-DNA")
            self.conformationComboBox.addItem("Z-DNA")
        
        elif inIndex == -1: 
            # Caused by clear(). This is tolerable for now. Mark 2007-05-24.
            pass
        
        else:
            msg = "Error - unknown model representation. Index = " + inIndex
            env.history.message(redmsg(msg))
            
        self.connect( self.conformationComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.conformationComboBoxChanged)
    
    # GroupBox3 slots (and other methods) supporting the Strand Sequence groupbox.
    
    def getDuplexRise( self, inConformation ):
        """
        Return the 'rise' between base pairs of the 
        specified DNA type (conformation).
        
        @param inConformation: The current conformation.
        @type  inConformation: int
        """
        return dnaDict[str(inConformation)]['DuplexRise']

    def synchronizeLengths( self ):
        """
        Guarantees the values of the duplex length and strand length 
        spinboxes agree with the strand sequence (textedit).
        """
        self.updateStrandLength()
        self.updateDuplexLength()   
        return
    
        # Added :jbirac 20070613:     
    def duplexLengthChanged( self, inDuplexLength ):
        """
        Slot for the duplex length spinbox, called whenever the value of the 
        Duplex Length spinbox changes.
        
        @param inDuplexLength: The duplex length.
        @type  inDuplexLength: float
        """

        conformation     =  self.conformationComboBox.currentText()
        duplexRise       =  self.getDuplexRise( conformation )
        newStrandLength  =  inDuplexLength / duplexRise + 0.5
        newStrandLength  =  int( newStrandLength )
        self.strandLengthChanged( newStrandLength )

    def updateDuplexLength( self ):    # Added :jbirac 20070615:
        """
        Update the Duplex Length spinbox; always the length of the 
        strand sequence multiplied by the 'rise' of the duplex.  This
        method is called by slots of other controls (i.e., this itself
        is not a slot.)
        """
        conformation     =  self.conformationComboBox.currentText()
        newDuplexLength  =  self.getDuplexRise( conformation ) \
                          * self.getSequenceLength()

        self.disconnect( self.duplexLengthSpinBox,
                         SIGNAL("valueChanged(double)"),
                         self.duplexLengthChanged)

        self.duplexLengthSpinBox.setValue( newDuplexLength )
            
        self.connect( self.duplexLengthSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.duplexLengthChanged)

    # Renamed from length_changed :jbirac 20070613:
    def strandLengthChanged( self, inStrandLength ):
        """
        Slot for the Strand Length spin box, called whenever the value of the 
        Strand Length spin box changes.
        
        @param inStrandLength: The number of bases in the strand sequence.
        @type  inStrandLength: int
        """

        theSequence   =  self.getPlainSequence()
        sequenceLen   =  len( theSequence )
        lengthChange  =  inStrandLength - self.getSequenceLength()

        # Preserve the cursor's position/selection 
        cursor          =  self.sequenceTextEdit.textCursor()
        #cursorPosition  =  cursor.position()
        selectionStart  =  cursor.selectionStart()
        selectionEnd    =  cursor.selectionEnd()

        if inStrandLength < 0:
            return # Should never happen.
        
        if lengthChange < 0:
            # If length is less than the previous length, 
            # simply truncate the current sequence.
            theSequence.chop( -lengthChange )

        elif lengthChange > 0:
            # If length has increased, add the correct number of base 
            # letters to the current strand sequence.
            numNewBases  =  lengthChange

            # Get current base selected in combobox.
            chosenBase  =  'X' # Unassigned.

            basesToAdd  =  chosenBase * numNewBases
            theSequence.append( basesToAdd )

        else:
            env.history.message( 
                orangemsg( "strandLengthChanged(): Length has not changed." ))

        self.setSequence( theSequence )

        return

    # Renamed from updateLength :jbirac 20070613:
    def updateStrandLength( self ):
        """
        Update the Strand Length spinbox; always the length of the strand 
        sequence.
        """
            
        self.disconnect( self.strandLengthSpinBox,
                         SIGNAL("valueChanged(int)"),
                         self.strandLengthChanged )  

        self.strandLengthSpinBox.setValue( self.getSequenceLength() )
            
        self.connect( self.strandLengthSpinBox,
                      SIGNAL("valueChanged(int)"),
                      self.strandLengthChanged )
        return

    def sequenceChanged( self ):
        """
        Slot for the Strand Sequence textedit widget.
        Assumes the sequence changed directly by user's keystroke in the 
        textedit.  Other methods...
        """        
        cursorPosition  =  self.getCursorPosition()
        theSequence     =  self.getPlainSequence()
        
        # Disconnect while we edit the sequence.            
        self.disconnect( self.sequenceTextEdit,
                         SIGNAL("textChanged()"),
                         self.sequenceChanged )
    
        # How has the text changed?
        if theSequence.length() == 0:  # There is no sequence.
            self.updateStrandLength()
            self.updateDuplexLength()
        else:
            # Insert the sequence; it will be "stylized" by setSequence().
            self.setSequence( theSequence )
        
        # Reconnect to respond when the sequence is changed.
        self.connect( self.sequenceTextEdit,
                      SIGNAL("textChanged()"),
                      self.sequenceChanged )

        self.synchronizeLengths()
        return

    def getPlainSequence( self, inOmitSymbols = False ):
        """
        Returns a plain text QString (without HTML stylization)
        of the current sequence.  All characters are preserved (unless
        specified explicitly), including valid base letters, punctuation 
        symbols, whitespace and invalid letters.
        
        @param inOmitSymbols: Omits characters listed in self.validSymbols.
        @type  inOmitSymbols: bool
        
        @return: The current DNA sequence in the PM.
        @rtype:  QString
        """
        outSequence  =  self.sequenceTextEdit.toPlainText()

        if inOmitSymbols:
            # This may look like a sloppy piece of code, but Qt's QRegExp
            # class makes it pretty tricky to remove all punctuation.
            theString  =  '[<>' \
                           + str( QRegExp.escape(self.validSymbols) ) \
                           + ']|-'

            outSequence.remove(QRegExp( theString ))
            
        return outSequence

    def stylizeSequence( self, inSequence ):
        """
        Converts a plain text string of a sequence (including optional 
        symbols) to an HTML rich text string.
        
        @param inSequence: A DNA sequence.
        @type  inSequence: QString
        
        @return: The sequence.
        @rtype: QString
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
        
        while basePosition < len(outSequence):

            theSeqChar  =  outSequence[basePosition]

            if ( theSeqChar in basesDict
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
                    if theSeqChar in basesDict:
                        theTag  =  '<font color=' \
                                + basesDict[ theSeqChar ]['Color'] \
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
        """ 
        Replace the current strand sequence with the new sequence text.
        
        @param inSequence: The new sequence.
        @type  inSequence: QString
        
        @param inStylize: If True, inSequence will be converted from a plain
                          text string (including optional symbols) to an HTML 
                          rich text string.
        @type  inStylize: bool
        
        @param inRestoreCursor: Not implemented yet.
        @type  inRestoreCursor: bool
        
        @attention: Signals/slots must be managed before calling this method.  
        The textChanged() signal will be sent to any connected widgets.
        """
        cursor          =  self.sequenceTextEdit.textCursor()
        selectionStart  =  cursor.selectionStart()
        selectionEnd    =  cursor.selectionEnd()
        
        if inStylize:
            inSequence  =  self.stylizeSequence( inSequence )

        self.sequenceTextEdit.insertHtml( inSequence )
        
        if inRestoreCursor:
            cursor.setPosition( min(selectionStart, self.getSequenceLength()), 
                                QTextCursor.MoveAnchor )
            cursor.setPosition( min(selectionEnd, self.getSequenceLength()), 
                                 QTextCursor.KeepAnchor )
            self.sequenceTextEdit.setTextCursor( cursor )
        return
    
    def getSequenceLength( self ):
        """
        Returns the number of characters in 
        the strand sequence textedit widget.
        """
        theSequence  =  self.getPlainSequence( inOmitSymbols = True )
        outLength    =  theSequence.length()

        return outLength
        
    def getCursorPosition( self ):
        """
        Returns the cursor position in the 
        strand sequence textedit widget.
        """
        cursor  =  self.sequenceTextEdit.textCursor()
        return cursor.position()

    def cursorPosChanged( self ):
        """
        Slot called when the cursor position changes.
        """
        cursor  =  self.sequenceTextEdit.textCursor()

        if 0: 
            env.history.message( greenmsg( "cursorPosChanged: Selection ("
                                           + str(cursor.selectionStart())
                                           + " thru "
                                           + str(cursor.selectionEnd())+')' ) )
        return
            
    def actionsComboBoxChanged( self, inIndex ):
        """
        Slot for the Actions combobox. It is called whenever the
        Action choice is changed.
        
        @param inIndex: The index of the selected action choice.
        @type  inIndex: int
        """
        if inIndex == 0: # Very important.
            return
        
        actionName = str(self.actionsComboBox.currentText())
        self.actionsComboBox.setCurrentIndex( 0 ) # Generates signal!
        self.invokeAction( actionName )
        return 

    def invokeAction( self, inActionName ):
        """
        Applies an action on the current sequence displayed in the PM.

        @param inActionName: The action name.
        @type  inActionName: str

        @return: The sequence after the action has been applied.
        @rtype:  str
        """
        sequence, allKnown = self._getSequence()
        outResult  =  ""

        if inActionName == self._action_Complement:
            outResult  =  getComplementSequence(sequence)
        elif inActionName == self._action_Reverse:
            outResult  =  getReverseSequence(sequence)
        elif inActionName == self._action_ConvertUnrecognized:
            outResult  =  replaceUnrecognized(sequence, replaceBase = 'N')
            self.setSequence( outResult )
        elif inActionName == self._action_RemoveUnrecognized:
            outResult  =  replaceUnrecognized(sequence, replaceBase = '')

        self.setSequence( outResult )
        
        return
