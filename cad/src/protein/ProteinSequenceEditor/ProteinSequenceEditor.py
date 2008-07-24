# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ProteinSequenceEditor.py

@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$
@author: Urmi

History:
Urmi copied this from DnaSequenceEditor.py and modified it to suit the 
requirements of a protein sequence editor

"""

import foundation.env as env
import os
import re
import string
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QTextCursor, QRegExp
from PyQt4.Qt import QString
from PyQt4.Qt import QFileDialog
from PyQt4.Qt import QMessageBox
from PyQt4.Qt import QTextCharFormat, QBrush
from PyQt4.Qt import QRegExp
from PyQt4.Qt import QTextDocument

from dna.model.Dna_Constants import basesDict
from dna.model.Dna_Constants import getComplementSequence
from dna.model.Dna_Constants import getReverseSequence

from PM.PM_Colors import pmMessageBoxColor

from utilities.prefs_constants import workingDirectory_prefs_key

from protein.ProteinSequenceEditor.Ui_ProteinSequenceEditor import Ui_ProteinSequenceEditor

from utilities import debug_flags
from utilities.debug import print_compact_stack

from dna.model.Dna_Constants import MISSING_COMPLEMENTARY_STRAND_ATOM_SYMBOL
from utilities.constants import black, blue, darkblue, aqua, orange, darkorange
from utilities.constants import red, lightred_1, yellow, green, lightgray, olive
from utilities.constants import lightgreen_2, darkgreen, magenta, cyan, gray
from utilities.constants import navy, violet, pink, copper, brass, mustard, banana

class ProteinSequenceEditor(Ui_ProteinSequenceEditor):
    """
    Creates a dockable sequence editor. 
    """
    
    validSymbols  =  QString(' <>~!@#%&_+`=$*()[]{}|^\'"\\.;:,/?')
    sequenceFileName = None
    
    currentPosition = 0
    startPosition = 0
    endPosition = 0
    
    def __init__(self, win):
        """
        Creates a dockable sequence editor
        """
                     
        Ui_ProteinSequenceEditor.__init__(self, win)   
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False
        self._supress_textChanged_signal = False
        self.connect_or_disconnect_signals(isConnect = True)
        self.win = win
        self.maxSeqLength = 0
    
        
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
                
        #@see: BuildDna_PropertyManager.connect_or_disconnect_signals
        #for a comment about these flags.
        if isConnect and self.isAlreadyConnected:
            if debug_flags.atom_debug:
                print_compact_stack("warning: attempt to connect widgets"\
                                    "in this PM that are already connected." )
            return 
        
        if not isConnect and self.isAlreadyDisconnected:
            if debug_flags.atom_debug:
                print_compact_stack("warning: attempt to disconnect widgets"\
                                    "in this PM that are already disconnected.")
            return
        
        self.isAlreadyConnected = isConnect
        self.isAlreadyDisconnected = not isConnect
        
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
        
        change_connect( self.sequenceTextEdit,
                      SIGNAL("editingFinished()"),
                      self.sequenceChanged )
        
        change_connect( self.sequenceTextEdit,
                      SIGNAL("cursorPositionChanged()"),
                      self.cursorPosChanged) 
        
        change_connect( self.findLineEdit,
                      SIGNAL("textEdited(const QString&)"),
                      self.findLineEdit_textEdited) 
        
        change_connect( self.findNextToolButton,
                      SIGNAL("clicked()"),
                      self.findNext) 
        
        change_connect( self.findPreviousToolButton,
                      SIGNAL("clicked()"),
                      self.findPrevious) 
        
        change_connect( self.replacePushButton,
                      SIGNAL("clicked()"),
                      self.replace) 
    
    def update_state(self, bool_enable = True):
        """
        Update the state of this widget by enabling or disabling it depending
        upon the flag bool_enable. 
        @param bool_enable: If True , enables the widgets inside the sequence
                            editor
        @type bool_enable: boolean
        """
        for widget in self.children():
            if hasattr(widget, 'setEnabled'):
                #The following check ensures that even when all widgets in the 
                #Sequence Editor docWidget are disabled, the  'close' ('x')
                #and undock button in the top right corner are still accessible
                #for the user. Using self.setEnabled(False) disables 
                #all the widgets including the corner buttons so that method
                #is not used -- Ninad 2008-01-17
                if widget.__class__.__name__ != 'QAbstractButton':
                    widget.setEnabled(bool_enable)
      
                    
    
             
    def sequenceChanged( self ):
        """
        Slot for the Strand Sequence textedit widget.
        Assumes the sequence changed directly by user's keystroke in the 
        textedit.  Other methods...
        """ 
        
        if self._supress_textChanged_signal:
            return
        
        self._supress_textChanged_signal = True
        
        cursorPosition  =  self.getCursorPosition()
        theSequence     =  self.getPlainSequence()
        
        # How has the text changed?
        if theSequence.length() != 0 and theSequence.length() == self.maxSeqLength:  
            self._updateSequenceAndItsComplement(theSequence)
        else:
            #pop up a message saying that you are not allowed to change the length
            #of the sequence
            msg = "Cannot change the length of the sequence."\
                "You need to have exactly" + str(self.maxSeqLength) + " amino acids."
            QMessageBox.warning(self.win, "Warning!", msg)
            self._supress_textChanged_signal = False
            return
        
        ### Reconnect to respond when the sequence is changed.
        ##self.connect( self.sequenceTextEdit,
                      ##SIGNAL("textChanged()"),
                      ##self.sequenceChanged )

        #Urmi 20080715: need to update the sec structure text edit as well
        secStrucSeq = self.secStrucTextEdit.toPlainText()
        fixedPitchSequence = self.getFormattedSequence(str(secStrucSeq))
        self.secStrucTextEdit.insertHtml(fixedPitchSequence)
        self.synchronizeLengths()
        
        self._supress_textChanged_signal = False
        return
    
    def getPlainSequence( self, inOmitSymbols = False ):
        """
        Returns a plain text QString (without HTML stylization)
        of the current sequence.  All characters are preserved (unless
        specified explicitly), including valid base letters, punctuation 
        symbols, whitespace and invalid letters.
        
        @param inOmitSymbols: Omits characters listed in self.validSymbols.
        @type  inOmitSymbols: bool
        
        @return: The current Protein sequence in the PM.
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

    def _updateSequenceAndItsComplement(self, 
                                       inSequence, 
                                       inRestoreCursor  =  True):
        """
        Update the main strand sequence and its complement.  (pribvate method)
        
        Updating the complement sequence is done as explaned in the method 
        docstring of  self._detemine_complementSequence()
        
        Note that the callers outside the class call self.setSequence and 
        self.setComplementsequence but never call this method. 
        
        @see: self.setsequence() -- most portion (except for calling 
              self._determine_complementSequence() is copied over from
              setSequence. 
        @see: self._updateSequenceAndItsComplement()
        @see: self._determine_complementSequence()
        """
        #@BUG: This method was mostly copied from self.setSequence, which in turn
        #was copied over from old DnaGenerator. (so both methods have similar 
        #issues mentioned below)
        #Apparently PM_TextEdit.insertHtml replaces the the whole 
        #sequence each time. This needs to be cleaned up. - Ninad 2007-04-10
        
        cursor          =  self.sequenceTextEdit.textCursor()
        cursorMate      =  self.secStrucTextEdit.textCursor()   
        cursorMate2      =  self.aaRulerTextEdit.textCursor() 
        if cursor.position() == len(self.sequenceTextEdit.toPlainText()):
            selectionStart  = 0
            selectionEnd    = 0
        elif cursor.position() == -1:
            selectionStart  = 0
            selectionEnd    = 0
        else:
            selectionStart  =  cursor.selectionStart()
            selectionEnd    =  cursor.selectionEnd()
        
        seq = str(inSequence)
        inSequence1 = self.convertProteinSequenceToColoredSequence(seq)
        inSequence1 = self._fixedPitchSequence(inSequence1)
        
        # Specify that theSequence is definitely HTML format, because 
        # Qt can get confused between HTML and Plain Text. 
        
        self.sequenceTextEdit.insertHtml( inSequence1 )
        
        if inRestoreCursor:                      
            cursor.setPosition(selectionStart, QTextCursor.MoveAnchor)       
            cursor.setPosition(selectionEnd, QTextCursor.KeepAnchor)     
            self.sequenceTextEdit.setTextCursor( cursor )
            cursorMate.setPosition( selectionStart, QTextCursor.MoveAnchor )
            cursorMate.setPosition(selectionEnd, QTextCursor.KeepAnchor)     
            self.secStrucTextEdit.setTextCursor( cursorMate )
            cursorMate2.setPosition( selectionStart, QTextCursor.MoveAnchor )
            cursorMate2.setPosition(selectionEnd, QTextCursor.KeepAnchor)     
            self.aaRulerTextEdit.setTextCursor( cursorMate2 )

    def setSequence( self,
                     inSequence,
                     inStylize        =  True,
                     inRestoreCursor  =  True
                     ):
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
        
        @see: self.setsequence()
        @see: self._updateSequenceAndItsComplement()
        @see: self._determine_complementSequence()
        
        """
        #@BUG: This method was mostly copied from old DnaGenerator
        #Apparently PM_TextEdit.insertHtml replaces the the whole 
        #sequence each time. This needs to be cleaned up. - Ninad 2007-11-27
        
        self.maxSeqLength = len(inSequence)
        cursor          =  self.sequenceTextEdit.textCursor()     
        cursorMate      =  self.secStrucTextEdit.textCursor()
        cursorMate2     =  self.aaRulerTextEdit.textCursor()
        if cursor.position() == len(self.sequenceTextEdit.toPlainText()):
            selectionStart  = 0
            selectionEnd    = 0
        elif cursor.position() == -1:
            selectionStart  = 0
            selectionEnd    = 0    
        else:
            selectionStart  =  cursor.selectionStart()
            selectionEnd    =  cursor.selectionEnd()
        
        
        seq = str(inSequence)
        inSequence1 = self.convertProteinSequenceToColoredSequence(seq)
        
        #inSequence = "<font color=red>" + inSequence + "</font>"
        if inStylize:
            inSequence1 = self._fixedPitchSequence(inSequence1)           
    
        #Urmi 20080714: Convert inSequence to colored text, each amino acid is 
        # shown by its own color
        
        # Specify that theSequence is definitely HTML format, because 
        # Qt can get confused between HTML and Plain Text. 
        
        self.sequenceTextEdit.insertHtml( inSequence1)
        
        if inRestoreCursor:                      
            cursor.setPosition(selectionStart, QTextCursor.MoveAnchor)       
            cursor.setPosition(selectionEnd, QTextCursor.KeepAnchor)     
            self.sequenceTextEdit.setTextCursor( cursor )
            cursorMate.setPosition(selectionStart, QTextCursor.MoveAnchor)  
            cursorMate.setPosition(selectionEnd, QTextCursor.KeepAnchor) 
            self.secStrucTextEdit.setTextCursor( cursorMate )
            cursorMate2.setPosition(selectionStart, QTextCursor.MoveAnchor)  
            cursorMate2.setPosition(selectionEnd, QTextCursor.KeepAnchor) 
            self.aaRulerTextEdit.setTextCursor( cursorMate2 )
        return
    
    def getFormattedSequence(self, inSequence):
        """
        Create formatted sequence to be used by secondary structure text edit
        """
        colorList = ['Red','Blue', 'Green']
        secStrucList = ['H','E', '-']
        secStrucDict = dict(zip(secStrucList, colorList))
        outSequence = ""
        for i in range(len(inSequence)):
            currentAA = inSequence[i]
            color = secStrucDict[currentAA]
            outSequence = outSequence + "<font color=" + color + ">" 
            outSequence = outSequence + currentAA + "</font>"
            
        #Now put html tags and make everything bold
        fixedPitchSequence  =  "<html><bold><font size=3 face=Courier New >"  + outSequence
        fixedPitchSequence +=  "</font></bold></html>"
        return fixedPitchSequence 
     
    
    def setSecondaryStructure(self, inSequence, inRestoreCursor  =  True):
        """
        Set the secondary structure of the protein
        """
        cursor          =  self.sequenceTextEdit.textCursor()     
        cursorMate      =  self.secStrucTextEdit.textCursor()
        cursorMate2     =  self.aaRulerTextEdit.textCursor()
        if cursor.position() == len(self.sequenceTextEdit.toPlainText()):
            selectionStart  = 0
            selectionEnd    = 0
        elif cursor.position() == -1:
            selectionStart  = 0
            selectionEnd    = 0    
        else:
            selectionStart  =  cursor.selectionStart()
            selectionEnd    =  cursor.selectionEnd()
        
        fixedPitchSequence = self.getFormattedSequence(inSequence)
        self.secStrucTextEdit.insertHtml(fixedPitchSequence)
        if inRestoreCursor:                      
            cursor.setPosition(selectionStart, QTextCursor.MoveAnchor)       
            cursor.setPosition(selectionEnd, QTextCursor.KeepAnchor)     
            self.sequenceTextEdit.setTextCursor( cursor )
            cursorMate.setPosition(selectionStart, QTextCursor.MoveAnchor)  
            cursorMate.setPosition(selectionEnd, QTextCursor.KeepAnchor) 
            self.secStrucTextEdit.setTextCursor( cursorMate )
            cursorMate2.setPosition(selectionStart, QTextCursor.MoveAnchor)  
            cursorMate2.setPosition(selectionEnd, QTextCursor.KeepAnchor) 
            self.aaRulerTextEdit.setTextCursor( cursorMate2 )
        return 
    
    def setRuler(self, lengthOfSeq, inRestoreCursor  =  True):
        """
        Set the sequence ruler for upto three digits
        """
        cursor          =  self.sequenceTextEdit.textCursor()     
        cursorMate      =  self.secStrucTextEdit.textCursor()
        cursorMate2     =  self.aaRulerTextEdit.textCursor()
        if cursor.position() == len(self.sequenceTextEdit.toPlainText()):
            selectionStart  = 0
            selectionEnd    = 0
        elif cursor.position() == -1:
            selectionStart  = 0
            selectionEnd    = 0    
        else:
            selectionStart  =  cursor.selectionStart()
            selectionEnd    =  cursor.selectionEnd()
        
        rulerText = ""
        i = 0
        while i < lengthOfSeq:
            
            if i == 0:
                rulerText = "1"
                i = i + 1
            elif i % 10 == 0 and i % 5 == 0:
                rulerText = rulerText + str(i+1)
                if len(str(i+1)) == 2:
                    i = i + 2
                    continue
                elif len(str(i+1)) == 3:
                    i = i + 3
                else:
                    i = i + 1
                    continue
            elif i % 5 == 0 and i % 10 != 0:
                rulerText = rulerText + "*"
                i = i + 1
            else:
                rulerText = rulerText + "-"
                i = i + 1
        fixedPitchSequence  =  "<html><bold><font size=3 face=Courier New color=green>"  + rulerText
        fixedPitchSequence +=  "</font></bold></html>"    
        self.aaRulerTextEdit.insertHtml(fixedPitchSequence)
        if inRestoreCursor:                      
            cursor.setPosition(selectionStart, QTextCursor.MoveAnchor)       
            cursor.setPosition(selectionEnd, QTextCursor.KeepAnchor)     
            self.sequenceTextEdit.setTextCursor( cursor )
            cursorMate.setPosition(selectionStart, QTextCursor.MoveAnchor)  
            cursorMate.setPosition(selectionEnd, QTextCursor.KeepAnchor) 
            self.secStrucTextEdit.setTextCursor( cursorMate )
            cursorMate2.setPosition(selectionStart, QTextCursor.MoveAnchor)  
            cursorMate2.setPosition(selectionEnd, QTextCursor.KeepAnchor) 
            self.aaRulerTextEdit.setTextCursor( cursorMate2 )
        return
    
    def convertProteinSequenceToColoredSequence(self, inSequence):
        """
        Create formatted sequence to be used by the sequence editor
        """
        outSequence = ""
        
        colorList = ['Crimson', 'CadetBlue', 'Coral', 'DarkCyan', 'DarkGray', 
                     'DarkGoldenRod', 'DarkOliveGreen', 'BlueViolet', 'Red',
                     'Chocolate', 'DarkKhaki', 'DarkSalmon', 'DarkSeaGreen',
                     'FireBrick', 'HotPink', 'LawnGreen', 'IndianRed', 'Indigo',
                     'LightCoral', 'LightBlue', 'Khaki']
    
        aaList = ['A', 'V', 'X', 'Y', 'W', 'T', 'S', 'P', 'F', 'M', 'K', 'L', 'I'
                  'H', 'G', 'Q', 'E', 'C', 'R', 'N', 'D' ]
        aaDict = dict(zip(aaList, colorList))
        for i in range(len(inSequence)):
            currentAA = inSequence[i]
            try:
                color = aaDict[currentAA]
            except KeyError:
                color = aaDict['X']
            outSequence = outSequence + "<font color=" + color + ">" 
            outSequence = outSequence + currentAA + "</font>"
            
        return outSequence
    
    def _fixedPitchSequence(self, sequence):
        """
        Make the sequence 'fixed-pitched'  i.e. width of all characters 
        should be constance
        """
        #The <pre> tag is important to keep the fonts 'fixed pitch' i.e. 
        #all the characters occupy the same size. This is important because 
        #we have two text edits. (strand and Mate) the 'Mate' edit gets updated
        #as you type in letters in the 'StrandEdit' and these two should
        #appear to user as having equal lengths. 
        fixedPitchSequence  =  "<html><bold><font size=3 face=Courier New >"  + sequence
        fixedPitchSequence +=  "</bold></font></html>"
        
        return fixedPitchSequence
        
        
    
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
        Slot called when the cursor position of the strand textEdit changes. 
        When this happens, this method also changes the cursor position 
        of the 'Mate' text edit. Because of this, both the text edit widgets 
        in the Sequence Editor scroll 'in sync'.
        """  
        strandSequence = self.sequenceTextEdit.toPlainText() 
        cursor  =  self.sequenceTextEdit.textCursor()
        cursor_mate =  self.secStrucTextEdit.textCursor()
        cursor_mate2 =  self.aaRulerTextEdit.textCursor()
        
        if cursor.position() == len(self.sequenceTextEdit.toPlainText()):
            curPos = 0
        else:
            curPos = cursor.position()
            
        if cursor_mate.position() != cursor.position():
            cursor_mate.setPosition( curPos, 
                                    QTextCursor.MoveAnchor )
            cursor_mate2.setPosition( curPos, 
                                    QTextCursor.MoveAnchor )
            #After setting position, it is important to do setTextCursor 
            #otherwise no effect will be observed. 
            self.secStrucTextEdit.setTextCursor(cursor_mate)
            self.aaRulerTextEdit.setTextCursor(cursor_mate2)
        
        #provide amino acid info as cursor position changes    
        part = self.win.assy.part
        
        current_command = self.win.commandSequencer.currentCommand.commandName
        position = cursor.position()
        if current_command == 'EDIT_ROTAMERS' or current_command == 'EDIT_RESIDUES' or current_command == 'BUILD_PROTEIN':
            current_protein = self.win.commandSequencer.currentCommand.propMgr.current_protein
            for mol in self.win.assy.molecules:
                if mol.isProteinChunk and mol.name == current_protein:
                    proteinChunk = mol
                    self._display_and_recenter(current_protein, position - 1)
                    break
        else:
            from simulation.ROSETTA.rosetta_commandruns import checkIfProteinChunkInPart
            proteinExists, proteinChunk = checkIfProteinChunkInPart(part)
        
        
        toolTipText = proteinChunk.protein.get_amino_acid_id(position - 1)
        self.sequenceTextEdit.setToolTip(str(toolTipText)) 
        env.history.statusbar_msg(toolTipText)
        
        if self.win.commandSequencer.currentCommand.commandName == 'EDIT_ROTAMERS':
            self.win.commandSequencer.currentCommand.propMgr.aminoAcidsComboBox.setCurrentIndex(position - 1)
        if self.win.commandSequencer.currentCommand.commandName == 'EDIT_RESIDUES':
            self.win.commandSequencer.currentCommand.propMgr._sequenceTableCellChanged(position - 1, 0)    
            self.win.commandSequencer.currentCommand.propMgr.sequenceTable.setCurrentCell(position - 1, 3) 
            
    def _display_and_recenter(self, current_protein, index):
        """
        """
        for chunk in self.win.assy.molecules:
            if chunk.isProteinChunk() and chunk.name == current_protein:
                chunk.protein.collapse_all_rotamers()
                current_aa = chunk.protein.get_amino_acid_at_index(index)
                if current_aa:
                    chunk.protein.expand_rotamer(current_aa)
                    if self.win.commandSequencer.currentCommand.commandName == 'EDIT_ROTAMERS':
                        checked = self.win.commandSequencer.currentCommand.propMgr.recenterViewCheckBox.isChecked()
                        if checked:
                            ca_atom = current_aa.get_c_alpha_atom()
                            if ca_atom:
                                self.win.glpane.pov = -ca_atom.posn()  
                    if self.win.commandSequencer.currentCommand.commandName == 'EDIT_RESIDUES':
                        checked = self.win.commandSequencer.currentCommand.propMgr.recenterViewCheckBox.isChecked()
                        if checked:
                            ca_atom = current_aa.get_c_alpha_atom()
                            if ca_atom:
                                self.win.glpane.pov = -ca_atom.posn()              
                    self.win.glpane.gl_update()
                    
                    
    def synchronizeLengths( self ):
        """
        Guarantees the values of the duplex length and strand length 
        spinboxes agree with the strand sequence (textedit).
        
        @TODO: synchronizeLengths doesn't do anything for now
        """  
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
        #Urmi 20080714: should not this be only fasta file, for both load and save
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
        self._updateSequenceAndItsComplement(sequence)
        
    
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
    
    
    
    
    # ==== Methods to support find and replace. 
    # Should this (find and replace) be in its own class? -- Ninad 2007-11-28
    
    def findNext(self):
        """
        Find the next occurence of the search string in the sequence
        """
        self._findNextOrPrevious()
        
    def findPrevious(self):
        """
        Find the previous occurence of the search string in the sequence
        """
        self._findNextOrPrevious(findPrevious = True)
        
    def _findNextOrPrevious(self, findPrevious = False):
        """
        Find the next or previous matching string depending on the 
        findPrevious flag. It also considers into account various findFlags 
        user might have set (e.g. case sensitive search)
        @param findPrevious: If true, this method will find the previous 
                             occurance of the search string. 
        @type  findPrevious: boolean
        """
        findFlags = QTextDocument.FindFlags()
    
        if findPrevious:
            findFlags |= QTextDocument.FindBackward
    
        if self.caseSensitiveFindAction.isChecked():
            findFlags |= QTextDocument.FindCaseSensitively    
            
        if not self.sequenceTextEdit.hasFocus():
            self.sequenceTextEdit.setFocus()
    
        searchString = self.findLineEdit.text()        
        cursor  =  self.sequenceTextEdit.textCursor()
    
        found = self.sequenceTextEdit.find(searchString, findFlags)
    
        #May be the cursor reached the end of the document, set it at position 0
        #to redo the search. This makes sure that the search loops over as 
        #user executes findNext multiple times. 
        if not found:
            if findPrevious:
                sequence_QString = self.sequenceTextEdit.toPlainText()
                newCursorStartPosition = sequence_QString.length()
            else:
                newCursorStartPosition = 0
                
            cursor.setPosition( newCursorStartPosition, 
                                QTextCursor.MoveAnchor)  
            self.sequenceTextEdit.setTextCursor(cursor)
            found = self.sequenceTextEdit.find(searchString, findFlags)
    
        #Display or hide the warning widgets (that say 'sequence not found' 
        #based on the boolean 'found' 
        self._toggleWarningWidgets(found)
        
    def _toggleWarningWidgets(self, found):
        """
        If the given searchString is not found in the sequence string, toggle 
        the display of the 'sequence not found' warning widgets. Also enable 
        or disable  the 'Replace' button accordingly
        @param found: Flag that decides whether to sho or hide warning 
        @type  found: boolean
        @see: self.findNext, self.findPrevious
        """
        if not found:
            self.findLineEdit.setStyleSheet(self._getFindLineEditStyleSheet())
            self.phraseNotFoundLabel.show()
            self.warningSign.show()
            self.replacePushButton.setEnabled(False)
        else:
            self.findLineEdit.setStyleSheet("")
            self.phraseNotFoundLabel.hide()
            self.warningSign.hide()
            self.replacePushButton.setEnabled(True)
        
    def findLineEdit_textEdited(self, searchString):
        """
        Slot method called whenever the text in the findLineEdit is edited 
        *by the user*  (and not by the setText calls). This is useful in 
        dynamically searching the string as it gets typed in the findLineedit.
        """
        self.findNext()
        #findNext sets the focus inside the sequenceTextEdit. So set it back to
        #to the findLineEdit to permit entering more characters.
        if not self.findLineEdit.hasFocus():
            self.findLineEdit.setFocus()        
    
    def replace(self):
        """
        Find a string matching the searchString given in the findLineEdit and 
        replace it with the string given in the replaceLineEdit. 
        """        
        searchString = self.findLineEdit.text()                    
        replaceString = self.replaceLineEdit.text()        
        sequence = self.sequenceTextEdit.toPlainText()
        
        #Its important to set focus on the sequenceTextEdit otherwise, 
        #cursor.setPosition and setTextCursor won't have any effect 
        if not self.sequenceTextEdit.hasFocus():
            self.sequenceTextEdit.setFocus()       
        
        cursor  =  self.sequenceTextEdit.textCursor() 
        selectionStart = cursor.selectionStart()
        selectionEnd = cursor.selectionEnd()
                        
        sequence.replace( selectionStart, 
                          (selectionEnd - selectionStart), 
                          replaceString )  
        
        #Move the cursor position one step back. This is important to do.
        #Example: Let the sequence be 'AAZAAA' and assume that the 
        #'replaceString' is empty. Now user hits 'replace' , it deletes first 
        #'A' . Thus the new sequence starts with the second A i.e. 'AZAAA' .
        # Note that the cursor position is still 'selectionEnd' i.e. cursor 
        # position index is 1. 
        #Now you do 'self.findNext' -- so it starts with cursor position 1 
        #onwards, thus missing the 'A' before the character Z. That's why 
        #the following is done.     
        cursor.setPosition((selectionEnd -1), QTextCursor.MoveAnchor)        
        self.sequenceTextEdit.setTextCursor(cursor)   
        
        #Set the sequence in the text edit. This could be slow. See comments
        #in self._updateSequenceAndItsComplement for more info. 
        self._updateSequenceAndItsComplement(sequence)
        
        #Find the next occurance of the 'seqrchString' in the sequence.
        self.findNext()
        
    