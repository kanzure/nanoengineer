# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
SequenceEditor.py

@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 2007-11-20: Created.

NOTE: Methods such as sequenceChanged, stylizeSequence are copied from the old
      DnaGeneratorPropertyManager where they were originally defined 
      This old PM used to implement a 'SequenceEditor text editor'.
      That file hasn't been deprecated yet -- 2007-11-20
      
TODO: (as of 2007-11-20)
- File open-save strand sequence needs more work 
- Implement 'Find and Replace' feature
- When strand editor cursor scrolls , it should also reflect changes in the 
  mate editor. 
- Many other things listed on rattleSnake sprint backlog, once dna object model
  is ready
  
Implementation Notes as of 2007-11-20:  
The Sequence Editor is shown when you enter DnaDuplex mode. The history widget 
is hidden at the same time)The editor is a docked at the bottom of the 
mainwindow. It has two text edits -- 'Strand' and 'Mate'. The 'Mate' (which 
might be renamed in future) is a readonly and it shows the complement of the 
sequence you enter in the Strand TextEdit field. User can Open or Save the 
strand sequence using the options in the sequrence editor. (other options such 
as Find and replace to be added) 
"""

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QPalette
from PyQt4.Qt import QTextCursor, QRegExp
from PyQt4.Qt import QTextOption
from PyQt4.Qt import QString
from PyQt4.Qt import QFileDialog
from PyQt4.Qt import QMessageBox

from PM.PM_Colors    import getPalette
from PM.PM_Colors    import sequenceEditStrandMateBaseColor


from PM.PM_DockWidget import PM_DockWidget
from PM.PM_WidgetRow  import PM_WidgetRow
from PM.PM_ToolButton import PM_ToolButton
from PM.PM_ComboBox   import PM_ComboBox
from PM.PM_TextEdit   import PM_TextEdit

from Dna_Constants import basesDict
from Dna_Constants import getComplementSequence
from Dna_Constants import getReverseSequence

from prefs_constants import workingDirectory_prefs_key

import env
import os


class SequenceEditor(PM_DockWidget):
    """
    Creates a dockable sequence editor. The sequence editor has two text edit 
    fields -- Strand and Mate and has various options such as 
    load a sequence from file or save the current sequence etc. By default 
    the sequence editor is docked in the bottom area of the mainwindow. 
    The sequence editor shows up in Dna edit mode. 
    """
    _title         =  "Sequence Editor"
    _groupBoxCount = 0
    _lastGroupBox = None
    validSymbols  =  QString(' <>~!@#%&_+`=$*()[]{}|^\'"\\.;:,/?')
    sequenceFileName = None
    
    def __init__(self, win):
        """
        Creates a dockable sequence editor
        """
        self.win = win
        # Should parentWidget for a docwidget always be win? 
        #Not necessary but most likely it will be the case.
        
        parentWidget = win        
        PM_DockWidget.__init__(self, parentWidget, title = self._title)
    
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect
  
        change_connect(self.loadSequenceButton, 
                     SIGNAL("clicked()"), 
                     self.openStrandSequenceFile)
        
        change_connect(self.saveSequenceButton, 
                     SIGNAL("clicked()"), 
                     self.saveStrandSequence)
        
        change_connect(self.baseDirectionChoiceComboBox,
                     SIGNAL('currentIndexChanged(int)'),
                     self._reverseSequence)
        
        change_connect( self.sequenceTextEdit,
                      SIGNAL("textChanged()"),
                      self.sequenceChanged )
        
        change_connect( self.sequenceTextEdit,
                      SIGNAL("cursorPositionChanged()"),
                      self.cursorPosChanged)               
           
    def _loadWidgets(self):
        """
        Overrides PM.PM_dockWidget._loadWidgets. Loads the widget in this
        dockwidget.
        """
        self._loadMenuWidgets()
        self._loadTextEditWidget()
    
    def _loadMenuWidgets(self):
        """
        """
        self.loadSequenceButton = PM_ToolButton(
            self,
            iconPath = "ui/actions/Properties Manager/Open_Strand_Sequence.png")  
        
        self.saveSequenceButton = PM_ToolButton(
            self, 
            iconPath = "ui/actions/Properties Manager/Save_Strand_Sequence.png") 
                                        
        self.loadSequenceButton.setAutoRaise(True)
        self.saveSequenceButton.setAutoRaise(True)
        
        editDirectionChoices = ["5' to 3'", "3' to 5'"]
        self.baseDirectionChoiceComboBox = \
            PM_ComboBox( self,
                         choices = editDirectionChoices,
                         index     = 0, 
                         spanWidth = False )
        
        widgetList = [('PM_ToolButton', self.loadSequenceButton, 0),
                      ('PM_ToolButton', self.saveSequenceButton, 1),
                      ('QLabel', "     Sequence direction:", 2),
                      ('PM_ComboBox',  self.baseDirectionChoiceComboBox , 3),
                      ('QSpacerItem', 5, 5, 4) ]
        
        widgetRow = PM_WidgetRow(self,
                                 title     = '',
                                 widgetList = widgetList,
                                 label = "",
                                 spanWidth = True )
        
       
    def _reverseSequence(self, itemIndex):
        """
        Reverse the strand sequence and update the StrandTextEdit widgets. 
        This is used when the 'strand direction' combobox item changes. 
        Example: If the sequence direction option is 5' to 3' then while
        adding the bases, those get added to extend the 3' end. 
        Changing the direction (3' to 5') reverses the existing sequence in 
        the text edit (which was meant to be for 5' to 3')
        @param itemIndex: currentIndex of combobox
        @type  itemIndex: int
        """
        sequence = self.getPlainSequence()
        reverseSequence = getReverseSequence(str(sequence))
        self.setSequence(reverseSequence)  
           
    def _loadTextEditWidget(self):
        """
        Load the SequenceTexteditWidgets.         
        """        
        self.sequenceTextEdit = \
            PM_TextEdit( self, label = " Strand: ", spanWidth = False )        
        self.sequenceTextEdit.setCursorWidth(2)
        self.sequenceTextEdit.setWordWrapMode( QTextOption.WrapAnywhere )
        self.sequenceTextEdit.setFixedHeight(20)
        
        #The StrandSequence 'Mate' it is a read only etxtedit that shows
        #the complementary strand sequence.         
        self.sequenceTextEdit_mate = \
            PM_TextEdit(self, label = " Mate: ", spanWidth = False )        
        palette = getPalette(None, 
                             QPalette.Base, 
                             sequenceEditStrandMateBaseColor)
        self.sequenceTextEdit_mate.setPalette(palette)        
        self.sequenceTextEdit_mate.setFixedHeight(20)
        self.sequenceTextEdit_mate.setReadOnly(True)
        self.sequenceTextEdit_mate.setWordWrapMode(QTextOption.WrapAnywhere)
     
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
            self.sequenceTextEdit_mate.clear()
            ##self.updateStrandLength()
            ##self.updateDuplexLength()            
        else:
            # Insert the sequence; it will be "stylized" by setSequence().
            self.setSequence( theSequence )
        
        # Reconnect to respond when the sequence is changed.
        self.connect( self.sequenceTextEdit,
                      SIGNAL("textChanged()"),
                      self.sequenceChanged )

        self.synchronizeLengths()
        
    
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
        outSequence = outSequence.toUpper()
        
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
        
        #The <pre> tag is important to keep the fonts 'fixed pitch' i.e. 
        #all the characters occupy the same size. This is important because 
        #we have two text edits. (strand and Mate) the 'Mate' edit gets updated
        #as you type in letters in the 'StrandEdit' and these two should
        #appear to user as having equal lengths. 
        outSequence  =  "<html>" + "<pre>" + outSequence
        outSequence +=  "</pre>" + "</html>"

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
        complementSequence = getComplementSequence(str(inSequence))
                
        if inStylize:
            inSequence  =  self.stylizeSequence( inSequence )            
            complementSequence = self.stylizeSequence(complementSequence)
            
        self.sequenceTextEdit.insertHtml( inSequence )
        self.sequenceTextEdit_mate.insertHtml(complementSequence)
        
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
        @TODO: cursorPosChanged doesn't do anything for now
        """        
        pass
        ##cursor  =  self.sequenceTextEdit.textCursor()
             
    
    def synchronizeLengths( self ):
        """
        Guarantees the values of the duplex length and strand length 
        spinboxes agree with the strand sequence (textedit).
        
        @TODO: synchronizeLengths doesn't do anything for now
        """
        ##self.updateStrandLength()
        ##self.updateDuplexLength()   
        return
    
    def openStrandSequenceFile(self):
        """
        Open (read) the user specified Strand sequence file and enter the 
        sequence in the Strand sequence Text edit. Note that it ONLY reads the 
        FIRST line of the file.
        @TODO: It only reads in the first line of the file. Also, it doesn't
               handle any special cases. (Once the special cases are clearly 
               defined, that functionality will be added. 
        """
        
        if self.parentWidget.assy.filename: 
            odir = os.path.dirname(self.parentWidget.assy.filename)
        else: 
            odir = env.prefs[workingDirectory_prefs_key]
        self.sequenceFileName = \
            str(QFileDialog.getOpenFileName( 
                self,
                "Load Strand Sequence",
                odir,
                "Strand Sequnce file (*.txt);;All Files (*.*);;"))  
        lines = self.sequenceFileName
        try:
            lines = open(self.sequenceFileName, "rU").readlines()         
        except:
            print "Exception occurred to open file: ", self.sequenceFileName
            return 
        
        sequence = lines[0]
        sequence = QString(sequence) 
        sequence = sequence.toUpper()
        self.setSequence(sequence)
        
    
    def _writeStrandSequenceFile(self, fileName, strandSequence):
        """
        Writes out the strand sequence (in the Strand Sequence editor) into 
        a file.
        """                
        try:
            f = open(fileName, "w")
        except:
            print "Exception occurred to open file %s to write: " % fileName
            return None
       
        f.write(str(strandSequence))  
        f.close()
    
    def saveStrandSequence(self):
        """
        Save the strand sequence entered in the Strand text edit in the 
        specified file. 
        """
        if not self.sequenceFileName:  
            sdir = env.prefs[workingDirectory_prefs_key]
        else:
            sdir = self.sequenceFileName
           
        fileName = QFileDialog.getSaveFileName(
                     self,              
                     "Save Strand Sequence As ...",
                     sdir,
                    "Strand Sequence File (*.txt)"
                     )
        
        if fileName:
            fileName = str(fileName)
            if fileName[-4] != '.':
                fileName += '.txt'
               
            if os.path.exists(fileName):
                
                # ...and if the "Save As" file exists...
                # ... confirm overwrite of the existing file.
                
                ret = QMessageBox.warning( 
                    self, 
                    "Save Strand Sequence...", 
                    "The file \"" + fileName + "\" already exists.\n"\
                    "Do you want to overwrite the existing file or cancel?",
                    "&Overwrite", "&Cancel", "",
                    0, # Enter == button 0
                    1 ) # Escape == button 1

                if ret == 1:
                    # The user cancelled
                    return 
                    
            # write the current set of element colors into a file    
            self._writeStrandSequenceFile(
                fileName,
                str(self.sequenceTextEdit.toPlainText()))

    