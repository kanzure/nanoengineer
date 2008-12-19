# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaSequenceEditor.py

@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 2007-11-20: Created.

NOTE: Methods such as _sequenceChanged, _stylizeSequence are copied from the old
      DnaGeneratorPropertyManager where they were originally defined.
      This old PM used to implement a 'DnaSequenceEditor text editor'.
      That file hasn't been deprecated yet -- 2007-11-20
      
TODO:  Ninad 2007-11-28 (reviewed and updated by Mark 2008-12-17)
- File open-save strand sequence needs more work.
- The old method '_setSequence' that inserts a sequence into the text edit 
  is slow. Apparently it replaces the whole sequence each time. This 
  needs to be cleaned up.
- Should the Find and Replace widgets and methods be defined in their own class
  and then called here?
- Implement synchronizeLengths(). It doesn't do anything for now.
- Create superclass that both the DNA and Protein sequence editors can use.
  
Implementation Notes as of 2007-11-20 (reviewed and updated by Mark 2008-12-17):  
The Sequence Editor is shown when you edit a DnaStrand (if visible, the 
'Reports' dockwidget is hidden at the same time). The editor is a docked at 
the bottom of the mainwindow. It has two text edits -- 'Strand' and 'Mate'. 
The 'Mate' (which might be renamed in future) is a readonly widget. It shows 
the complement of the sequence you enter in the 'Sequence' field. The user 
can Open or Save the strand sequence using the options in the sequence editor.

"""

import foundation.env as env
import os
import re

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QTextCursor, QRegExp
from PyQt4.Qt import QString
from PyQt4.Qt import QFileDialog
from PyQt4.Qt import QMessageBox
from PyQt4.Qt import QTextCharFormat, QBrush
from PyQt4.Qt import QRegExp
from PyQt4.Qt import QTextDocument
from PyQt4.Qt import QPalette

from dna.model.Dna_Constants import basesDict
from dna.model.Dna_Constants import getComplementSequence
from dna.model.Dna_Constants import getReverseSequence

from PM.PM_Colors import getPalette
from PM.PM_Colors import sequenceEditorNormalColor
from PM.PM_Colors import sequenceEditorChangedColor
from PM.PM_Colors import pmMessageBoxColor

from utilities.prefs_constants import workingDirectory_prefs_key

from dna.DnaSequenceEditor.Ui_DnaSequenceEditor import Ui_DnaSequenceEditor

from utilities import debug_flags
from utilities.debug import print_compact_stack

from dna.model.Dna_Constants import MISSING_COMPLEMENTARY_STRAND_ATOM_SYMBOL

class DnaSequenceEditor(Ui_DnaSequenceEditor):
    """
    Creates a dockable sequence editor. The sequence editor has two text edit 
    fields -- Strand and Mate and has various options such as 
    load a sequence from file or save the current sequence etc. By default 
    the sequence editor is docked in the bottom area of the mainwindow. 
    The sequence editor shows up in Dna edit mode. 
    """
   
    validSymbols  =  QString(' <>~!@#%&_+`=$*()[]{}|^\'"\\.;:,/?')
    sequenceFileName = None
    
    current_strand    = None   # The current strand.
    _sequence_changed = False  # Set to True when the sequence has been changed by the user.
    _previousSequence = ""     # The previous sequence, just before the user changed it.
    
    # Check to see if these 3 attrs are used by any other classes.
    # They are not used here. Mark 2008-12-17
    currentPosition = 0
    startPosition = 0
    endPosition = 0
    
    def __init__(self, win):
        """
        Creates a dockable sequence editor
        """
                       
        Ui_DnaSequenceEditor.__init__(self, win)  
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False
        #Flag used in self._sequenceChanged so that it doesn't get called 
        #recusrively in the text changed signal while changing the sequence
        #in self.textEdit while in that method. 
        self._suppress_textChanged_signal = False
        #Initial complement sequence set while reading in the strand sequence
        #of the strand being edited. 
        #@see: self._setComplementSequence(), self._determine_complementSequence()
        self._initial_complementSequence = ''
        return
    
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
      
        change_connect(self.baseDirectionChoiceComboBox,
                     SIGNAL('currentIndexChanged(int)'),
                     self._reverseSequence)
        
        change_connect( self.sequenceTextEdit,
                      SIGNAL("textChanged()"),
                      self._sequenceChanged )
        
        change_connect( self.sequenceTextEdit,
                      SIGNAL("editingFinished()"),
                      self._assignStrandSequence )
        
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
                #The following check ensures that even when all widgets in the 
                #Sequence Editor docWidget are disabled, the  'close' ('x')
                #and undock button in the top right corner are still accessible
                #for the user. Using self.setEnabled(False) disables 
                #all the widgets including the corner buttons so that method
                #is not used -- Ninad 2008-01-17
                if widget.__class__.__name__ != 'QAbstractButton':
                    widget.setEnabled(bool_enable)
        return
                    
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
        @see self._determine_complementSequence() and bug 2787
        """
        sequence = str(self.getPlainSequence())
        complementSequence = str(self.sequenceTextEdit_mate.toPlainText())
        
        reverseSequence = getReverseSequence(sequence)
        
        #Important to reverse the complement sequence separately 
        #see bug 2787 for implementation notes. 
        #@see self._determine_complementSequence()
        reverseComplementSequence = getReverseSequence(complementSequence)
        
        self._setComplementSequence(reverseComplementSequence)
        self._setSequence(reverseSequence)  
        return
    
    def _sequenceChanged( self ):
        """
        (private)
        Slot for the Strand Sequence textedit widget.
        Assumes the sequence changed directly by user's keystroke in the 
        textedit.  Other methods...
        """ 
        
        if self._suppress_textChanged_signal:
            return
        
        self._suppress_textChanged_signal = True
        
        cursorPosition  =  self.getCursorPosition()
        theSequence     =  self.getPlainSequence()
        
        theSequence.replace(" ", "X") # Space = X (unassigned).
        
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
        
        # Insert the sequence; it will be "stylized" by _setSequence().
        self._updateSequenceAndItsComplement(theSequence)
        
        # If the sequence in the text edit (field) is different from the current
        # strand's sequence, change the sequence field bg color to pink to 
        # indicate that the sequence is different. If they are the same,
        # change the sequence field background (back) to white.
        if theSequence != self.current_strand.getStrandSequence():
            self._sequence_changed = True
        else:
            self._sequence_changed = False
        self._previousSequence = theSequence
        self._updateSequenceBgColor()

        self.synchronizeLengths()
        
        self._suppress_textChanged_signal = False
        return
    
    def _assignStrandSequence(self):
        """
        (private)
        Slot for the "editingFinished()" signal generated by the PM_TextEdit 
        whenever the user presses the Enter key in the sequence text edit field.
        
        Assigns the sequence in the sequence editor text field to 
        the current strand. The method it invokes also assigns 
        complimentary bases to the mate strand(s).
        @see: Chunk.setStrandSequence
        @note: the method was copied from DnaStrand_EditCommand.assignStrandSequence()
        """
        if not self.current_strand: 
            #Fixes bug 2923
            return
        
        sequenceString = self.getPlainSequence()
        sequenceString = str(sequenceString)     
        
        #assign strand sequence only if it not the same as the current sequence
        seq = self.current_strand.getStrandSequence()
        
        if seq != sequenceString:
            self.current_strand.setStrandSequence(sequenceString)
            self.updateSequence(cursorPos = self.getCursorPosition())
        return
    
    def _updateSequenceBgColor(self):
        
        if self._sequence_changed:
            bgColor = sequenceEditorChangedColor
        else:
            bgColor = sequenceEditorNormalColor
            
        palette = getPalette(None, 
                             QPalette.Base, 
                             bgColor)
        self.sequenceTextEdit.setPalette(palette)  
        
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
        outSequence  = self._fixedPitchSequence(outSequence)

        return outSequence
    
    def _updateSequenceAndItsComplement(self, 
                                       inSequence, 
                                       inRestoreCursor  =  True):
        """
        Update the main strand sequence and its complement. (private method)
        
        Updating the complement sequence is done as explaned in the method 
        docstring of self._detemine_complementSequence()
        
        Note that the callers outside the class must call self.updateSequence(),
        but never call this method.
        
        @see: self.setsequence() -- most portion (except for calling 
              self._determine_complementSequence() is copied over from
              _setSequence. 
        @see: self._updateSequenceAndItsComplement()
        @see: self._determine_complementSequence()
        """
        
        #Find out complement sequence
        complementSequence = self._determine_complementSequence(inSequence)
        inSequence = self._fixedPitchSequence(inSequence)
        complementSequence = self._fixedPitchSequence(complementSequence)
        
        # Get current cursor position before inserting inSequence.
        if inRestoreCursor:
            cursorPos = self.getCursorPosition()
        else:
            cursorPos = 0
        
        # Specify that theSequence is definitely HTML format, because 
        # Qt can get confused between HTML and Plain Text.        
        self.sequenceTextEdit.insertHtml( inSequence ) #@@@ Generates signal???
        self.sequenceTextEdit_mate.insertHtml(complementSequence)
        self.setCursorPosition(cursorPos = cursorPos)

        return
        
    def _determine_complementSequence(self, inSequence):
        """
        Determine the complementary sequence based on the main sequence. 
        It does lots of thing than just obtaining the information by using 
        'getComplementSequence'. 
        
        Examples of what it does: 
        
        1. Suppose you have a duplex with 10 basepairs. 
        You are editing strand A and you lengthen it to create a sticky end. 
        Lets assume that it is lengthened by 5 bases. Since there will be no 
        complementary strand baseatoms for these, the sequence editor will show 
        an asterisk('*'), indicating that its missing the strand mate base atom.
        
        Sequence Editor itself doesn't check each time if the strand mate is 
        missing. Rather, it relies on what the caller supplied as the initial 
        complement sequence. (@see: self._setComplementSequence) . The caller 
        determines the sequence of the strand being edited and also its complement.
        If the complement doesn't exist, it replace the complement with a '*' 
        and passes this information to the sequence editor. Everytime sequence
        editor is updating its sequnece, it updates the mate sequence and skips
        the positions marked '*' (by using self._initial_complementSequence), 
        and thus those remain unaltered. 
        
        If user enters a sequence which has more characters than the original
        sequence, then it doesn't update the complement portion of that
        extra portion of the sequence. This gives a visual indication of 
        where the sequence ends. (see NFR bug 2787). 
        
        Reversing the sequence also reverses the complement (including the '*'
        positions)
        
        @see Bug 2787 for details of the implementation. 
        
        @see: self._setComplementSequence()
        @see: self._updateSequenceAndItsComplement()
        @see: self._setSequence()
        @see: DnaStrand_PropertyManager.updateSequence() (the caller)
        @see: Dna_Constants.MISSING_COMPLEMENTARY_STRAND_ATOM_SYMBOL
        @see: DnaStrand.getStrandSequenceAndItsComplement()
        
        """
        if not self._initial_complementSequence:
            #This is unlikely. Do nothing in this case. 
            return ''
        
        complementSequence = ''
        
        #Make sure that the insequence is a string object
        inSequence = str(inSequence)
       
        #Do the following only when the length of sequence (inSequence) is 
        #greater than or equal to length of original complement sequence
        
        #REVIEW This could be SLOW, need to think of a better way to do this.
        if len(inSequence) >= len(self._initial_complementSequence):                
            for i in range(len(self._initial_complementSequence)):
                if self._initial_complementSequence[i] == \
                   MISSING_COMPLEMENTARY_STRAND_ATOM_SYMBOL:
                    complementSequence += self._initial_complementSequence[i]
                else:
                    complementSequence += getComplementSequence(inSequence[i])
                    
        else:
            #Use complementSequence as a list object as we will need to modify 
            #some of the charactes within it. We can't do for example
            #string[i] = 'X' as it is not permitted in python. So we will first 
            #treat the complementSequence as a list, do necessary modifications
            #to it and then convert is back to a string. 
            #TODO: see if re.sub or re.subn can be used directly to replace
            #some characters (the reason re.suib is not used here is that 
            #it does find and repalce for all matching patterns, which we don't
            # want here )
            
            complementSequence = list(self._initial_complementSequence)
            
            for i in range(len(inSequence)):
                if complementSequence[i] != MISSING_COMPLEMENTARY_STRAND_ATOM_SYMBOL:
                    complementSequence[i] = getComplementSequence(inSequence[i])
            
            #Now there is additinal complementary sequence (because lenght of the
            #main sequence provided is less than the 'original complementary
            #sequence' (or the 'original main strand sequence) . In this case, 
            #for the remaining complementary sequence, we will use unassigned
            #base symbol 'X' . 
            #Example: If user starts editing a strand, 
            #the initial strand sequence and its complement are shown in the
            #sequence editor. Now, the user deletes some characters from the 
            #main sequence (using , e.g. backspace in sequence text edit to 
            #delete those), here, we will assume that this deletion of a 
            #character is as good as making it an unassigned base 'X', 
            #so its new complement will be of course 'X' --Ninad 2008-04-10
            extra_length = len(complementSequence) - len(inSequence)
            #do the above mentioned replacement 
            count = extra_length
            while count > 0:
                if complementSequence[-count] != MISSING_COMPLEMENTARY_STRAND_ATOM_SYMBOL:
                    complementSequence[-count] = 'X'
                count -= 1                           
       
            #convert the complement sequence back to a string
            complementSequence = ''.join(complementSequence)
  
        return complementSequence

    def _setComplementSequence(self, complementSequence):
        """
        Set the complement sequence field to I{complementSequence}. (private)
        
        This is typically called immediately before or after calling 
        self._setSequence().
        
        @param complementSequence: the complementary sequence determined by the
               caller. This string may contain characters '*' which indicate
               that there is a missing strand mate atom for the strand you are
               editing. The Sequence Editorkeeps the '*' characters while 
               determining the compelment sequence  (if the main sequence is 
               changed by the user)
        @type complementSequence: str
        
        See method docstring self._detemine_complementSequence() for more 
        information.         
        
        @see: self.updateSequence()
        @see: self._setSequence()
        @see: self._updateSequenceAndItsComplement()
        @see: self._determine_complementSequence()
        @see: DnaStrand_PropertyManager.updateSequence()
        """
        self._initial_complementSequence = complementSequence
        complementSequence = self._fixedPitchSequence(complementSequence)        
        self.sequenceTextEdit_mate.insertHtml(complementSequence)
        return
    
    def _setSequence( self,
                     inSequence,
                     inStylize        =  True,
                     inRestoreCursor  =  True
                     ):
        """ 
        Replace the current strand sequence with the new sequence text.
        (private method)
        
        This is typically called immediately before or after calling 
        self._setComplementSequence().
        
        @param inSequence: The new sequence.
        @type  inSequence: QString
        
        @param inStylize: If True, inSequence will be converted from a plain
                          text string (including optional symbols) to an HTML 
                          rich text string.
        @type  inStylize: bool
        
        @param inRestoreCursor: Restores cursor to previous position.
                                Not implemented yet.
        @type  inRestoreCursor: bool
        
        @attention: Signals/slots must be managed before calling this method.  
        The textChanged() signal will be sent to any connected widgets.
        
        @see: self.updateSequence()
        @see: self._setComplementSequence()
        @see: self._updateSequenceAndItsComplement()
        @see: self._determine_complementSequence()
        
        """
        #@BUG: This method was mostly copied from old DnaGenerator
        #Apparently PM_TextEdit.insertHtml replaces the the whole 
        #sequence each time. This needs to be cleaned up. - Ninad 2007-11-27
        
        #@UPDATE: Rewrote this method to help fix bugs 2953.
        # - Mark 2008-12-17
        
        if inStylize:
            #Temporary fix for bug 2604--
            #Temporarily disabling the code that 'stylizes the sequence' 
            #that code is too slow and takes a long time for a file to load. 
            # Example: NE1 hangs while loading M13 sequence (8kb file) if we 
            #stylize the sequence .-- Ninad 2008-01-22
            ##inSequence  =  self.stylizeSequence( inSequence )            
            
            #Instead only make the sequence 'Fixed pitch' (while bug 2604
            #is still open
            inSequence = self._fixedPitchSequence(inSequence)           
    
        # Specify that theSequence is definitely HTML format, because 
        # Qt can get confused between HTML and Plain Text.
        self._suppress_textChanged_signal = True
        self.sequenceTextEdit.insertHtml( inSequence )
        self._suppress_textChanged_signal = False
        
        self.setCursorPosition(0)
        return
    
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
        fixedPitchSequence  =  "<html>" + "<pre>" + sequence
        fixedPitchSequence +=  "</pre>" + "</html>"
        
        return fixedPitchSequence
        
    def getSequenceLength( self ):
        """
        Returns the number of characters in 
        the strand sequence textedit widget.
        """
        theSequence  =  self.getPlainSequence( inOmitSymbols = True )
        outLength    =  theSequence.length()
        return outLength
    
    def updateSequence(self, strand = None, cursorPos = -1):
        """
        Updates and shows the sequence editor with the sequence of I{strand}. 
        
        This is the main (public) method to call to update the sequence editor.
        
        @param strand: the strand. If strand is None (default), it is assumed
                       that self.current_strand is the sequence.
        @type  strand: DnaStrand
        
        @param cursorPos: the position in the sequence in which to place the
                          cursor. If cursorPos is negative, the cursor position
                          is placed at the end of the sequence (default).
        @type  cursorPos: int
        """
        
        if strand:
            assert isinstance(strand, self.win.assy.DnaStrand)
            self.current_strand = strand
        else: 
            # Use self.current_strand. Make sure it's not None (as a precaution).
            assert isinstance(self.current_strand, self.win.assy.DnaStrand)
        
        sequence, complementSequence = \
                self.current_strand.getStrandSequenceAndItsComplement()
        
        if sequence:
            sequence = QString(sequence) 
            sequence = sequence.toUpper()
            #Set the initial sequence (read in from the file)
            self._setSequence(sequence)
            
            #Set the initial complement sequence for DnaSequence editor. 
            #do this independently because 'complementSequenceString' may have
            #some characters (such as * ) that denote a missing base on the 
            #complementary strand. This information is used by the sequence
            #editor. See DnaSequenceEditor._determine_complementSequence() 
            #for more details. See also bug 2787
            self._setComplementSequence(complementSequence)
        else:
            msg = "DnaStrand '%s' has no sequence." % self.current_strand.name
            print_compact_traceback(msg)
            self._setSequence(msg)
            self._setComplementSequence("")
        
        # Set cursor position.
        self.setCursorPosition(cursorPos = cursorPos)
        
        # Update the bg color to white.
        self._sequence_changed = False
        self._previousSequence = sequence
        self._updateSequenceBgColor()
        
        # Update window title with name of current protein.
        titleString = 'Sequence Editor for ' + self.current_strand.name
        self.setWindowTitle(titleString)
        
        if not self.isVisible():
            #Show the sequence editor if it isn't visible.
            #ATTENTION: the sequence editor will (temporarily) close the
            #Reports dockwidget (if it is visible). The Reports dockwidget
            #is restored when the sequence Editor is closed.  
            self.show()
        return
    
    def setCursorPosition(self, cursorPos = 0):
        """
        Set the cursor position to I{cursorPos} in the strand sequence 
        textedit widget.
        
        @param cursorPos: the position in the sequence in which to place the
                          cursor. If cursorPos is negative, the cursor position
                          is placed at the end of the sequence (default).
        @type  cursorPos: int
        """
        
        
        # Make sure cursorPos is in the valid range.
        if cursorPos < 0:
            startPos = self.getSequenceLength()
            endPos   = self.getSequenceLength()
        elif cursorPos >= self.getSequenceLength():
            startPos = self.getSequenceLength()
            endPos   = self.getSequenceLength()
        else:
            startPos = cursorPos
            endPos   = cursorPos
        
        # Useful print statements for debugging.
        #print "setCursorPosition(): Sequence=", self.getPlainSequence()
        #print "setCursorPosition(): Final cursorPos=%d\nstartPos=%d, endPos=%d" % (cursorPos, startPos, endPos)
        
        # Finally, set the cursor position in the sequence.
        cursor = self.sequenceTextEdit.textCursor()
        cursor.setPosition(endPos,   QTextCursor.MoveAnchor)
        cursor.setPosition(startPos, QTextCursor.KeepAnchor)
        self.sequenceTextEdit.setTextCursor( cursor )
        return
        
    def getCursorPosition( self ):
        """
        Returns the cursor position in the strand sequence textedit widget.
        """
        cursor  =  self.sequenceTextEdit.textCursor()
        return cursor.position()

    def _cursorPosChanged( self ):
        """
        Slot called when the cursor position of the strand textEdit changes. 
        When this happens, this method also changes the cursor position 
        of the 'Mate' text edit. Because of this, both the text edit widgets 
        in the Sequence Editor scroll 'in sync'.
        """  
        strandSequence = self.sequenceTextEdit.toPlainText()
        strandSequence_mate = self.sequenceTextEdit_mate.toPlainText()
        
        #The cursorChanged signal is emitted even before the program enters 
        #_setSequence() (or before the 'textChanged' signal is emitted) 
        #So, simply return if the 'Mate' doesn't have same number of characters
        #as the 'Strand text edit' (otherwise it will print warning message 
        # while setting the cursor_mate position later in the method. 
        if strandSequence.length() != strandSequence_mate.length():
            return        
        
        cursor  =  self.sequenceTextEdit.textCursor()
        cursor_mate =  self.sequenceTextEdit_mate.textCursor()
        
        if cursor_mate.position() != cursor.position():
            cursor_mate.setPosition( cursor.position(), 
                                    QTextCursor.MoveAnchor )
            #After setting position, it is important to do setTextCursor 
            #otherwise no effect will be observed. 
            self.sequenceTextEdit_mate.setTextCursor(cursor_mate)
        return

    def synchronizeLengths( self ):
        """
        Guarantees the values of the duplex length and strand length 
        spinboxes agree with the strand sequence (textedit).
        
        @note: synchronizeLengths doesn't do anything for now
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
        self._updateSequenceAndItsComplement(sequence)
        return
    
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
        return
    
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
            print "_findNextOrPrevious(): setting cursor pos:"
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
        
        #Move the cursor position one step back. This is important to do.
        #Example: Let the sequence be 'AAZAAA' and assume that the 
        #'replaceString' is empty. Now user hits 'replace' , it deletes first 
        #'A' . Thus the new sequence starts with the second A i.e. 'AZAAA' .
        # Note that the cursor position is still 'selectionEnd' i.e. cursor 
        # position index is 1. 
        #Now you do 'self.findNext' -- so it starts with cursor position 1 
        #onwards, thus missing the 'A' before the character Z. That's why 
        #the following is done.     
        cursor.setPosition((selectionEnd - 1), QTextCursor.MoveAnchor) 
        self.sequenceTextEdit.setTextCursor(cursor)   
        
        #Set the sequence in the text edit. This could be slow. See comments
        #in self._updateSequenceAndItsComplement for more info. 
        self._updateSequenceAndItsComplement(sequence)
        
        #Find the next occurance of the 'seqrchString' in the sequence.
        self.findNext()
        return
    
