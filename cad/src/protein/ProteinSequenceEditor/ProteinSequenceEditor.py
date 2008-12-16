# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ProteinSequenceEditor.py

@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$
@author: Urmi

History:
Urmi copied this from DnaSequenceEditor.py and modified it to suit the 
requirements of a protein sequence editor.
"""

import foundation.env as env
import os
import re
import string
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QTextCursor
from PyQt4.Qt import QString
from PyQt4.Qt import QFileDialog
from PyQt4.Qt import QMessageBox
from PyQt4.Qt import QRegExp
from PyQt4.Qt import QTextDocument
from utilities.prefs_constants import workingDirectory_prefs_key
from protein.ProteinSequenceEditor.Ui_ProteinSequenceEditor import Ui_ProteinSequenceEditor
from utilities import debug_flags
from utilities.debug import print_compact_stack

class ProteinSequenceEditor(Ui_ProteinSequenceEditor):
    """
    Creates a dockable protein sequence editor. 
    """
    validSymbols  =  QString(' <>~!@#%&_+`=$*()[]{}|^\'"\\.;:,/?')
    sequenceFileName = None
    
    def __init__(self, win):
        """
        Creates a dockable protein sequence editor
        """                 
        Ui_ProteinSequenceEditor.__init__(self, win)   
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False
        self._suppress_textChanged_signal = False
        self.connect_or_disconnect_signals(True)
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
                if widget.__class__.__name__ != 'QAbstractButton':
                    widget.setEnabled(bool_enable)
    
    def sequenceChanged( self ):
        """
        Slot for the Protein Sequence textedit widget.
        Assumes the sequence changed directly by user's keystroke in the 
        textedit.  Other methods...
        """ 
        if self._suppress_textChanged_signal:
            return
        self._suppress_textChanged_signal = True
        cursorPosition  =  self.getCursorPosition()
        theSequence     =  self.getPlainSequence()
        # How has the text changed?
        if theSequence.length() != 0 and theSequence.length() == self.maxSeqLength:  
            self._updateSequence(theSequence)
        else:
            #pop up a message saying that you are not allowed to change the length
            #of the sequence
            msg = "Cannot change the length of the sequence."\
                "You need to have exactly" + str(self.maxSeqLength) + " amino acids."
            QMessageBox.warning(self.win, "Warning!", msg)
            self._suppress_textChanged_signal = False
            return
        #Urmi 20080725: Some time later we need to have a method here which 
        #would allow us to set the sequence of the protein chunk. We will also
        #update the secondary structure sequence or will it be the same as the
        #original one? 
        self._suppress_textChanged_signal = False
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

    def _updateSequence(self, 
                                       inSequence, 
                                       inRestoreCursor  =  True):
        """
        Update the main strand sequence (private method)
        
        Note that the callers outside the class call self.setSequence 
        but never call this method. 
        
        @see: self.setsequence() 
        """
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
        inSequence1 = self._convertProteinSequenceToColoredSequence(seq)
        inSequence1 = self._fixedPitchSequence(inSequence1)
        self.sequenceTextEdit.setHtml( inSequence1 )
        
        #adjust the cursor so that they match for all three text edits
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

        return
    
    def clear( self ):
        """
        Clears the sequence editor.
        """
        self.setSequenceAndStructure("", "")
        return
    
    def setSequenceAndStructure(self, inSequence, inStructure):
        """
        """
        self.setSequence(inSequence)
        self.setSecondaryStructure(inStructure)
        self.setRuler(len(inSequence))
        return
    
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
        
        """
        
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
        inSequence1 = self._convertProteinSequenceToColoredSequence(seq)
        if inStylize:
            inSequence1 = self._fixedPitchSequence(inSequence1)           
    
        #Urmi 20080714: Convert inSequence to colored text, each amino acid is 
        # shown by its own color
        self.sequenceTextEdit.setHtml( inSequence1)
        
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
    
    def _getFormattedSequence(self, inSequence):
        """
        Create formatted sequence to be used by secondary structure text edit
        
        @param inSequence: The new sequence.
        @type  inSequence: QString
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
     
    
    def setSecondaryStructure(self, inStructure, inRestoreCursor  =  True):
        """
        Set the secondary structure of the protein
        
        @param inStructure: The structure string.
        @type  inStructure: QString
        
        @param inRestoreCursor: restore cursor position
        @type  inRestoreCursor: bool
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
        
        fixedPitchSequence = self._getFormattedSequence(inStructure)
        self.secStrucTextEdit.setHtml(fixedPitchSequence)
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
        Set the sequence ruler for up to three digits
        
        @param lengthOfSeq: length of the sequence.
        @type  lengthOfSeq: int
        
        @param inRestoreCursor: restore cursor position
        @type  inRestoreCursor: bool
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
        self.aaRulerTextEdit.setHtml(fixedPitchSequence)
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
    
    def _convertProteinSequenceToColoredSequence(self, inSequence):
        """
        Create formatted sequence to be used by the sequence editor
        
        @param inSequence: The new sequence.
        @type  inSequence: QString
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
        
        @param sequence: The new sequence.
        @type  sequence: QString
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
            curPos = 1
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
        env.history.statusbar_msg("")
        current_command = self.win.commandSequencer.currentCommand.commandName
        commandSet = ('EDIT_ROTAMERS', \
                      'EDIT_RESIDUES', \
                      'BUILD_PROTEIN', \
                      'MODEL_PROTEIN', \
                      'SIMULATE_PROTEIN')
        if current_command not in commandSet:
            return
        
        position = cursor.position()
        if position == 0:
            # piotr 080912: fixed an exception when user clicked on position 0
            position = 1
        proteinExists = False
        if current_command in commandSet:
            current_protein = self.win.commandSequencer.currentCommand.propMgr.current_protein
            for mol in self.win.assy.molecules:
                if mol.isProteinChunk() and mol.name == current_protein:
                    proteinChunk = mol
                    self._display_and_recenter(current_protein, position - 1)
                    proteinExists = True
                    break
        
        if proteinExists:
            toolTipText = proteinChunk.protein.get_amino_acid_id(position - 1)
            self.sequenceTextEdit.setToolTip(str(toolTipText)) 
            env.history.statusbar_msg(toolTipText)
        
            if self.win.commandSequencer.currentCommand.commandName == 'EDIT_ROTAMERS':
                self.win.commandSequencer.currentCommand.propMgr.aminoAcidsComboBox.setCurrentIndex(position - 1)
            if self.win.commandSequencer.currentCommand.commandName == 'EDIT_RESIDUES':
                self.win.commandSequencer.currentCommand.propMgr._sequenceTableCellChanged(position - 1, 0)    
                self.win.commandSequencer.currentCommand.propMgr.sequenceTable.setCurrentCell(position - 1, 3) 
        return
            
            
    def _display_and_recenter(self, current_protein, index):
        """
        Display and recenter the view on the current amino acid under the cursor
        in the text edit
        
        @param current_protein: currently selected protein in the protein combo 
                                box in Build_Protein PM
        @type current_protein: string
        
        @param index: index of amino acid under cursor in sequence text edit
        @type index: int 
        """
        #@@@ Change current_protein from string to Chunk. Mark 2008-12-13
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
        self._updateSequence(sequence)
        
    
    def _writeStrandSequenceFile(self, fileName, strandSequence):
        """
        Writes out the strand sequence (in the Strand Sequence editor) into 
        a file.
        
        @param fileName: file to which the strand sequence is written to
        @type fileName: str
        
        @param strandSequence: strand sequence that is written
        @type strandSequence: str
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
        
        @param searchString: string that is searched for
        @type searchString: str
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
         
        cursor.setPosition((selectionEnd -1), QTextCursor.MoveAnchor)        
        self.sequenceTextEdit.setTextCursor(cursor)   
        
        #Set the sequence in the text edit. 
        self._updateSequence(sequence)
        
        #Find the next occurance of the 'seqrchString' in the sequence.
        self.findNext()
        
    