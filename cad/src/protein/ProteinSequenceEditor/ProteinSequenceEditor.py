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
from PyQt4.Qt import QPalette

from PM.PM_Colors import getPalette
from PM.PM_Colors import sequenceEditorNormalColor
from PM.PM_Colors import sequenceEditorChangedColor

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
    
    current_protein   = None   # The current protein chunk.
    _sequence_changed = False  # Set to True when the sequence has been changed by the user.
    _previousSequence = ""     # The previous sequence, just before the user changed it.
    
    def __init__(self, win):
        """
        Creates a dockable protein sequence editor
        """                 
        Ui_ProteinSequenceEditor.__init__(self, win)   
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False
        self._suppress_textChanged_signal = False
        self._suppress_cursorPosChanged_signal = False
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
                     self._open_FASTA_File)
        
        change_connect(self.saveSequenceButton, 
                     SIGNAL("clicked()"), 
                     self._savePeptideSequence)
        
        change_connect( self.sequenceTextEdit,
                      SIGNAL("textChanged()"),
                      self._sequenceChanged )
        
        change_connect( self.sequenceTextEdit,
                      SIGNAL("editingFinished()"),
                      self._assignPeptideSequence )
        
        change_connect( self.sequenceTextEdit,
                      SIGNAL("cursorPositionChanged()"),
                      self._cursorPosChanged) 
        
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
        return
    
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
        return
    
    def _sequenceChanged( self ):
        """
        Slot for the Protein Sequence textedit widget. (private method)
        Assumes the sequence changed directly by user's keystroke in the 
        textedit.  Other methods...
        """ 
        if self._suppress_textChanged_signal:
            return
        
        self._suppress_textChanged_signal = True
        cursorPos   =  self.getCursorPosition()
        theSequence =  self.getPlainSequence()
        
        if len(theSequence) == len(self._previousSequence):
            # Replace space characters with the same character.
            aa = self._previousSequence[cursorPos - 1]
            theSequence.replace(" ", aa) 
            print "The last character was replaced with: ", aa
        
        # Insert the sequence; it will be "stylized" by _setSequence().
        self._setSequence(theSequence, inCursorPos = cursorPos)
        
        if False: # Set to True for debugging statements.
            if theSequence == self._previousSequence:
                print "The sequence did not change (YOU SHOULD NEVER SEE THIS)."
            elif len(theSequence) < len(self._previousSequence):
                print "Character(s) were deleted from the sequence."
            elif len(theSequence) == len(self._previousSequence):
                print "A character was replaced. The sequence length is the same."
            else:
                print "Character(s) where added to the sequence."
            pass
        
        # If the sequence in the text edit (field) is different from the current
        # sequence, change the sequence field bg color to pink to 
        # indicate that the sequence is different. If they are the same,
        # change the sequence field background (back) to white.
        if theSequence != self.current_protein.protein.get_sequence_string():
            self._sequence_changed = True
        else:
            self._sequence_changed = False
        self._previousSequence = theSequence
        self._updateSequenceBgColor()
        
        #Urmi 20080725: Some time later we need to have a method here which 
        #would allow us to set the sequence of the protein chunk. We will also
        #update the secondary structure sequence or will it be the same as the
        #original one? 
        self._suppress_textChanged_signal = False
        return
    
    def _assignPeptideSequence(self):
        """
        (private)
        Slot for the "editingFinished()" signal generated by the PM_TextEdit 
        whenever the user presses the Enter key in the sequence text edit field.
        
        Assigns the amino acid sequence in the sequence editor text field to 
        the current protein. 
        
        @attention: this method is not implemented yet. If called, it will
        display a messagebox warning the user that this is not implement yet.
        """
        if not self.current_protein: 
            return
        
        sequenceString = self.getPlainSequence()
        sequenceString = str(sequenceString)     
        
        #assign sequence only if it not the same as the current sequence
        seq = self.current_protein.protein.get_sequence_string()
        
        if seq != sequenceString:
            #self.current_protein.setSequence(sequenceString)
            #self.updateSequence(cursorPos = self.getCursorPosition())
            msg = "We are sorry. You cannot change the sequence since "\
                "this feature is not yet supported."
            QMessageBox.warning(self.win, "Warning!", msg)
            self._suppress_textChanged_signal = False
            
        self.updateSequence(self.current_protein)
        return
    
    def _updateSequenceBgColor(self):
        """
        Updates the sequence field background color 
        (pink = changed, white = unchanged).
        """
        if self._sequence_changed:
            bgColor = sequenceEditorChangedColor
        else:
            bgColor = sequenceEditorNormalColor
            
        palette = getPalette(None, 
                             QPalette.Base, 
                             bgColor)
        self.sequenceTextEdit.setPalette(palette)
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
    
    def clear( self ):
        """
        Clears the sequence editor.
        """
        self.current_protein = None
        self._setSequenceAndStructure("", "")
        return
    
    def _setSequenceAndStructure(self, 
                                 inSequence, 
                                 inStructure, 
                                 inCursorPos = -1):
        """
        Sets the sequence, structure and ruler fields in the sequence editor.
        @param inSequence: The sequence string.
        @type  inSequence: QString
        @param inStructure: The secondary structure string.
        @type  inStructure: QString
        @param inCursorPos: the position in the sequence in which to place the
                          cursor. If cursorPos is negative, the cursor position
                          is placed at first residue of the sequence (default).
        @type  inCursorPos: int
        """
        #NOTE: It is important that sequence is set last so that setCursorPos()
        #doesn't complain (i.e. the structure and ruler strings must be
        #equal to the length of the sequence string before setting the cursor
        # position). --Mark 2008-12-20
        self._setSecondaryStructure(inStructure)
        self._setRuler(len(inSequence))
        self._setSequence(inSequence, inCursorPos = inCursorPos)
        return
    
    def _setSequence( self,
                      inSequence,
                      inStylize        =  True,
                      inCursorPos      = -1
                      ):
        """ 
        Replace the current amino acid sequence with the new sequence text.
        (private method)
        
        Callers outside this class wishing to update the amino acid sequence  
        field should call updateSequence().
        
        @param inSequence: The sequence string.
        @type  inSequence: QString
        
        @param inStylize: If True, inSequence will be converted from a plain
                          text string (including optional symbols) to an HTML 
                          rich text string.
        @type  inStylize: bool
        
        @param inCursorPos: the position in the sequence in which to place the
                          cursor. If cursorPos is negative, the cursor position
                          is placed at first residue of the sequence (default).
        @type  inCursorPos: int
        
        @see: updateSequence()
        """
        
        seq = str(inSequence)
        seq = seq.upper()
        htmlSequence = self._convertProteinSequenceToColoredSequence(seq)
        if inStylize:
            htmlSequence = self._fixedPitchSequence(htmlSequence)
        self._suppress_textChanged_signal = True
        self._suppress_cursorPosChanged_signal = True
        self.sequenceTextEdit.setHtml(htmlSequence) # Generates cursorPosChanged signal!
        self.setCursorPosition(inCursorPos = inCursorPos)
        self._suppress_textChanged_signal = False
        self._suppress_cursorPosChanged_signal = False
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
     
    
    def _setSecondaryStructure(self, inStructure):
        """
        Set the secondary structure of the protein. (private method)
        
        Callers outside this class wishing to update the secondary structure 
        field should call updateSequence().
        
        @param inStructure: The structure string.
        @type  inStructure: QString
        
        @see: updateSequence()
        """
        fixedPitchSequence = self._getFormattedSequence(inStructure)
        self.secStrucTextEdit.setHtml(fixedPitchSequence)
        return 
    
    def getRulerText(self, lengthOfSeq):
        """
        Return the ruler text given I{lengthOfSeq} (i.e. the length of the 
        current sequence).
        """
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
        return rulerText
        
    def _setRuler(self, lengthOfSeq):
        """
        Set the sequence ruler with a length of I{lengthOfSeq}.
        
        Callers outside this class wishing to update the ruler 
        should call updateSequence().
        
        @param lengthOfSeq: length of the sequence.
        @type  lengthOfSeq: int
        
        @note: supports up to 3 digits (i.e. max length of 999).
        """
        rulerText = self.getRulerText(lengthOfSeq)
        fixedPitchSequence  =  "<html><bold><font size=3 face=Courier New color=green>"  + rulerText
        fixedPitchSequence +=  "</font></bold></html>"    
        self.aaRulerTextEdit.setHtml(fixedPitchSequence)
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
    
    def _colorExtraSequenceCharacters(self, inSequence):
        """
        Returns I{inSequence} with html tags that color any extra overhang 
        characters gray.
        @param inSequence: The sequence.
        @type  inSequence: QString
        @return: inSequence with the html tags to color any overhang characters.
        @rtype:  string
        """
        aaLength = self.current_protein.protein.count_amino_acids()
        if len(inSequence) <= aaLength:
            return inSequence
        
        sequence = inSequence[:aaLength]
        overhang = inSequence[aaLength:]
        
        return sequence + "<font color=gray>" + overhang + "</font>"
    
    def _fixedPitchSequence(self, sequence):
        """
        Make the sequence 'fixed-pitched'  i.e. width of all characters 
        should be constance
        
        @param sequence: The new sequence.
        @type  sequence: QString
        """
        fixedPitchSequence  =  "<html><bold><font size=3 face=Courier New >"  + sequence
        fixedPitchSequence +=  "</bold></font></html>"
        return fixedPitchSequence
    
    def getSequenceLength( self ):
        """
        Returns the number of characters in the sequence textedit widget.
        """
        theSequence  =  self.getPlainSequence( inOmitSymbols = True )
        outLength    =  theSequence.length()
        return outLength
    
    def updateSequence(self, proteinChunk = None, inCursorPos = -1):
        """
        Updates the sequence editor with the sequence of I{proteinChunk}. 
        
        @param proteinChunk: the protein chunk. If proteinChunk is None 
                            (default), the sequence editor is cleared.
        @type  proteinChunk: protein Chunk
        
        @param inCursorPos: the position in the sequence in which to place the
                          cursor. If cursorPos is negative, the cursor position
                          is placed at first residue of the sequence (default).
        @type  inCursorPos: int
        """
        
        if proteinChunk:
            assert isinstance(proteinChunk, self.win.assy.Chunk) and \
                   proteinChunk.isProteinChunk()
            self.current_protein = proteinChunk
        else:
            # Use self.current_protein. Make sure it's not None.
            #assert isinstance(self.current_protein, self.win.assy.Chunk) and \
                   #proteinChunk.isProteinChunk()
            self.clear()
            return
        
        # We have a protein chunk. Update the editor with its sequence.
        sequence = self.current_protein.protein.get_sequence_string()
        structure = self.current_protein.protein.get_secondary_structure_string()
        self._setSequenceAndStructure(sequence, structure, inCursorPos = inCursorPos)
        
        # Update the bg color to white.
        self._sequence_changed = False
        self._previousSequence = sequence
        self._updateSequenceBgColor()
        
        # Update window title with name of current protein.
        titleString = 'Sequence Editor for ' + self.current_protein.name
        self.setWindowTitle(titleString)
        
        if not self.isVisible():
            #Show the sequence editor if it isn't visible.
            #ATTENTION: the sequence editor will (temporarily) close the
            #Reports dockwidget (if it is visible). The Reports dockwidget
            #is restored when the sequence Editor is closed.
            self.show()
            
        return
    
    def setCursorPosition(self, inCursorPos = -1):
        """
        Set the cursor position to I{cursorPos} in the sequence textedit widget.
        
        @param inCursorPos: the position in the sequence in which to place the
                          cursor. If cursorPos is negative, the cursor position
                          is placed at the beginning of the sequence (default).
        @type  inCursorPos: int
        """
        
        # Make sure cursorPos is in the valid range.
        if inCursorPos < 0:
            cursorPos = 0
            anchorPos = 1
        elif inCursorPos >= self.getSequenceLength():
            cursorPos = self.getSequenceLength() - 1
            anchorPos = self.getSequenceLength()
        else:
            cursorPos = inCursorPos
            anchorPos = inCursorPos + 1
        
        # Useful print statements for debugging.
        print "setCursorPosition(): Sequence=", self.getPlainSequence()
        print "setCursorPosition(): Final inCursorPos=%d\ncursorPos=%d, anchorPos=%d" % (inCursorPos, cursorPos, anchorPos)

        self._suppress_cursorPosChanged_signal = True
        
        # Finally, set the cursor position in the sequence.
        cursor = self.sequenceTextEdit.textCursor()
        cursor.setPosition(anchorPos, QTextCursor.MoveAnchor)
        cursor.setPosition(cursorPos, QTextCursor.KeepAnchor)
        self.sequenceTextEdit.setTextCursor( cursor )
        
        cursorMate = self.secStrucTextEdit.textCursor()
        cursorMate.setPosition(anchorPos, QTextCursor.MoveAnchor)  
        cursorMate.setPosition(cursorPos, QTextCursor.KeepAnchor) 
        self.secStrucTextEdit.setTextCursor( cursorMate )
        
        cursorMate2 = self.aaRulerTextEdit.textCursor()
        cursorMate2.setPosition(anchorPos, QTextCursor.MoveAnchor)  
        cursorMate2.setPosition(cursorPos, QTextCursor.KeepAnchor) 
        self.aaRulerTextEdit.setTextCursor( cursorMate2 )
        
        self._updateToolTip()
        
        self._suppress_cursorPosChanged_signal = False
            
        return
        
    def getCursorPosition( self ):
        """
        Returns the cursor position in the sequence textedit widget.
        """
        cursor  =  self.sequenceTextEdit.textCursor()
        return cursor.position()

    def _cursorPosChanged( self ):
        """
        Slot called when the cursor position of the sequence textEdit changes. 
        When this happens, this method also changes the cursor position 
        of the 'Mate' text edit. Because of this, both the text edit widgets 
        in the Sequence Editor scroll 'in sync'.
        """  
        if self._suppress_cursorPosChanged_signal:
            return
        
        cursor  =  self.sequenceTextEdit.textCursor()
        cursorPos = cursor.position()
        print "_cursorPosChanged(): Here! cursorPos=", cursorPos
        
        self.setCursorPosition(inCursorPos = cursorPos) # sets all three.
        
        # Provide amino acid info as cursor position changes    
        env.history.statusbar_msg("")
        current_command = self.win.commandSequencer.currentCommand
        commandSet = ('EDIT_PROTEIN', 'EDIT_RESIDUES')
        
        if current_command.commandName not in commandSet:
            return
        
        aa_index = min(cursorPos, self.getSequenceLength() - 1)
    
        if current_command.commandName == 'EDIT_PROTEIN':
            current_command.propMgr.setCurrentAminoAcid(aa_index)
        if current_command.commandName == 'EDIT_RESIDUES':
            current_command.propMgr._sequenceTableCellChanged(aa_index, 0)    
            current_command.propMgr.sequenceTable.setCurrentCell(aa_index, 3) 
            
        self._updateToolTip()
        
        return
    
    def _updateToolTip(self):
        """
        Update the tooltip text (and status bar) with the current residue id.
        """
        aa_index = self.current_protein.protein.get_current_amino_acid_index()
        aa_info = self.current_protein.protein.get_amino_acid_id(aa_index)
        aa_id, residue_id = aa_info.strip().split(":")
        toolTipText = residue_id
        self.sequenceTextEdit.setToolTip(str(toolTipText)) 
        env.history.statusbar_msg(toolTipText)
        return
        
    def _display_and_recenter(self, index):
        """
        Display and recenter the view on the current amino acid under the cursor
        in the text edit
        
        @param index: index of amino acid under cursor in sequence text edit
        @type index: int 
        
        @note: this method has no callers. It will likely be moved to 
               EditResidues_PM soon.  -Mark 2008-12-20 
        """
        chunk = self.current_protein
        chunk.protein.collapse_all_rotamers()
        current_aa = chunk.protein.get_amino_acid_at_index(index)
        if current_aa:
            if self.win.commandSequencer.currentCommand.commandName == 'EDIT_RESIDUES':
                checked = self.win.commandSequencer.currentCommand.propMgr.recenterViewCheckBox.isChecked()
                if checked:
                    ca_atom = current_aa.get_c_alpha_atom()
                    if ca_atom:
                        self.win.glpane.pov = -ca_atom.posn()              
            self.win.glpane.gl_update()
        return
    
    def _open_FASTA_File(self):
        """
        Open (read) the user specified FASTA sequence file and load it into
        the sequence field.
        
        @TODO: It only reads in the first line of the file. Also, it doesn't
               handle any special cases. (Once the special cases are clearly 
               defined, that functionality will be added. 
               
        @attention: This is not implemented yet.
        """
        #Urmi 20080714: should not this be only fasta file, for both load and save
        if self.parentWidget.assy.filename: 
            odir = os.path.dirname(self.parentWidget.assy.filename)
        else: 
            odir = env.prefs[workingDirectory_prefs_key]
        self.sequenceFileName = \
            str(QFileDialog.getOpenFileName( 
                self,
                "Load FASTA sequence for " + self.current_protein.name,
                odir,
                "FASTA file (*.txt);;All Files (*.*);;"))  
        lines = self.sequenceFileName
        try:
            lines = open(self.sequenceFileName, "rU").readlines()         
        except:
            print "Exception occurred to open file: ", self.sequenceFileName
            return 
        
        sequence = lines[0]
        sequence = QString(sequence) 
        sequence = sequence.toUpper()
        self._setSequence(sequence)
        return
    
    def _write_FASTA_File(self, fileName, sequence):
        """
        Writes I{sequence} in FASTA format to I{filename}.
        
        @param fileName: full path of the file.
        @type  fileName: str
        
        @param sequence: AA sequence to be saved in FASTA format.
        @type  sequence: str
        
        @attention: The sequence is not written in FASTA format yet.
        
        @TODO: Write sequence in FASTA format.
        """                
        try:
            f = open(fileName, "w")
        except:
            print "Exception occurred to open file %s to write: " % fileName
            return None
       
        f.write(str(sequence))  
        f.close()
        return
    
    def _savePeptideSequence(self):
        """
        Save the current sequence (displayed in the sequence field) in FASTA 
        format in the specified file. 
        """
        if not self.sequenceFileName:  
            sdir = env.prefs[workingDirectory_prefs_key]
        else:
            sdir = self.sequenceFileName
           
        fileName = QFileDialog.getSaveFileName(
                     self,              
                     "Save Sequence As ...",
                     sdir,
                    "FASTA File (*.txt)"
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
                    "Save Sequence...", 
                    "The file \"" + fileName + "\" already exists.\n"\
                    "Do you want to overwrite the existing file or cancel?",
                    "&Overwrite", "&Cancel", "",
                    0, # Enter == button 0
                    1 ) # Escape == button 1

                if ret == 1:
                    # The user cancelled
                    return 
                    
            # write the current set of element colors into a file    
            self._write_FASTA_File(
                fileName,
                str(self.sequenceTextEdit.toPlainText()))
        return
   
    # ==== Methods to support find and replace. 
    # Should this (find and replace) be in its own class? -- Ninad 2007-11-28
    
    def findNext(self):
        """
        Find the next occurence of the search string in the sequence
        """
        self._findNextOrPrevious()
        return
        
    def findPrevious(self):
        """
        Find the previous occurence of the search string in the sequence
        """
        self._findNextOrPrevious(findPrevious = True)
        return
        
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
        return
        
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
        return
        
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
        return
    
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
        self._setSequence(sequence)
        
        #Find the next occurance of the 'seqrchString' in the sequence.
        self.findNext()
        return
        
    