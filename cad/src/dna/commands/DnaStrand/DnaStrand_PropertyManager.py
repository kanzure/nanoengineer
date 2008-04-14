# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaStrand_PropertyManager.py

@author: Ninad
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

TODO: as of 2008-02-14
- Sequence editor is also created in BuildDna_PropertyManager (of course 
its a child of that PM) . See if that creates any issues. 
- Copies some methods from BuildDna_PropertyManager. 
"""
from utilities import debug_flags
from utilities.debug import print_compact_stack
from utilities.Comparison import same_vals
from utilities.Log import redmsg

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QString
from PyQt4.Qt import Qt

from widgets.DebugMenuMixin import DebugMenuMixin
from command_support.EditCommand_PM import EditCommand_PM

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_LineEdit      import PM_LineEdit
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox


class DnaStrand_PropertyManager( EditCommand_PM, DebugMenuMixin ):
    """
    The DnaStrand_PropertyManager class provides a Property Manager 
    for the DnaStrand_EditCommand.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Strand Properties"
    pmName        =  title
    iconPath      =  "ui/actions/Properties Manager/Strand.png"

    def __init__( self, win, editCommand ):
        """
        Constructor for the Build DNA property manager.
        """
        
        #For model changed signal
        self.previousSelectionParams = None
        
        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False
        
        self.sequenceEditor = None      
        
        self._numberOfBases = 0 
        self._conformation = 'B-DNA'
        self.duplexRise = 3.18
        self.basesPerTurn = 10
        self.dnaModel = 'PAM3'
        
        
        EditCommand_PM.__init__( self, 
                                    win,
                                    editCommand)


        DebugMenuMixin._init1( self )

        self.showTopRowButtons( pmDoneButton | \
                                pmWhatsThisButton)
        
        self._loadSequenceEditor()
        
        if self.editCommand.hasValidStructure():
            msg1 = ("Viewing properties of %s <br>") %(self.editCommand.struct.name)                        
            msg2 = "Use resize handles to resize the strand. Use sequence editor"\
                       "to assign a new sequence or the current one to a file."
            self.updateMessage(msg1 + msg2)
       
    
    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """        
                
        self._pmGroupBox1 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox1( self._pmGroupBox1 )
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 4.
        """
        
        self.nameLineEdit = PM_LineEdit( pmGroupBox,
                         label         =  "Strand name:",
                         text          =  "",
                         setAsDefault  =  False)
        
        self.numberOfBasesSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Number of bases:", 
                        value         =  self._numberOfBases,
                        setAsDefault  =  False,
                        minimum       =  2,
                        maximum       =  10000 )
        
        self.basesPerTurnDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Bases per turn:",
                              value         =  self.basesPerTurn,
                              setAsDefault  =  True,
                              minimum       =  8.0,
                              maximum       =  20.0,
                              decimals      =  2,
                              singleStep    =  0.1 )
        
        self.duplexRiseDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Rise:",
                              value         =  self.duplexRise,
                              setAsDefault  =  True,
                              minimum       =  2.0,
                              maximum       =  4.0,
                              decimals      =  3,
                              singleStep    =  0.01 )
        
        self.disableStructHighlightingCheckbox = \
            PM_CheckBox( pmGroupBox,
                         text         = "Don't highlight while editing DNA",
                         widgetColumn  = 0,
                         state        = Qt.Unchecked,
                         setAsDefault = True,
                         spanWidth = True
                         )
        
        #As of 2008-03-31, the properties such as number of bases will be 
        #editable only by using the resize handles. post FNANO we will support 
        #the 
        self.numberOfBasesSpinBox.setEnabled(False)
        self.basesPerTurnDoubleSpinBox.setEnabled(False)
        self.duplexRiseDoubleSpinBox.setEnabled(False)
        
    
            
    def _loadSequenceEditor(self):
        """
        Temporary code  that shows the Sequence editor ..a doc widget docked
        at the bottom of the mainwindow. The implementation is going to change
        before 'rattleSnake' product release.
        As of 2007-11-20: This feature (sequence editor) is waiting 
        for the ongoing dna model work to complete.
        """
        self.sequenceEditor = self.win.createDnaSequenceEditorIfNeeded() 
        self.sequenceEditor.hide()
        
    def getParameters(self):
        numberOfBases = self.numberOfBasesSpinBox.value()
        dnaForm  = self._conformation
        dnaModel = self.dnaModel
        basesPerTurn = self.basesPerTurn
        duplexRise = self.duplexRise
              
        return (numberOfBases, 
                dnaForm,
                dnaModel,
                basesPerTurn,
                duplexRise)
    
    def setParameters(self, params):
        """
        This is usually called when you are editing an existing structure. 
        Some property manager ui elements then display the information 
        obtained from the object being edited. 
        TODO:
        - Make this a EditCommand_PM API method? 
        - See also the routines GraphicsMode.setParams or object.setProps
        ..better to name them all in one style?  
        """
        #Set the duplex rise and bases per turn spinbox values. 
        
        numberOfBasePairs, \
                         dnaForm, \
                             dnaModel,\
                             basesPerTurn, \
                             duplexRise = params 
        
        if numberOfBasePairs is not None:
            self.numberOfBasePairsSpinBox.setValue(numberOfBasePairs)
        if dnaForm is not None:
            self._conformation = dnaForm
        if dnaModel is not None:
            self.dnaModel = dnaModel
        if duplexRise is not None:
            self.duplexRiseDoubleSpinBox.setValue(duplexRise)
        if basesPerTurn is not None:
            self.basesPerTurnDoubleSpinBox.setValue(basesPerTurn)    
    
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        #TODO: This is a temporary fix for a bug. When you invoke a temporary
        # mode Entering such a temporary mode keeps the signals of 
        #PM from the previous mode connected (
        #but while exiting that temporary mode and reentering the 
        #previous mode, it atucally reconnects the signal! This gives rise to 
        #lots  of bugs. This needs more general fix in Temporary mode API. 
        # -- Ninad 2008-01-09 (similar comment exists in MovePropertyManager.py
                
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
          
                
        if self.sequenceEditor:
            self.sequenceEditor.connect_or_disconnect_signals(isConnect)
            
        
        change_connect(self.disableStructHighlightingCheckbox, 
                       SIGNAL('stateChanged(int)'), 
                       self.change_struct_highlightPolicy)
        
    def model_changed(self): 
        """
        @see: DnaStrand_EditCommand.model_changed()
        @see: DnaStrand_EditCommand.hasResizableStructure()
        """
        if not self.editCommand.hasResizableStructure():
            #disable all widgets
            if self._pmGroupBox1.isEnabled():
                self._pmGroupBox1.setEnabled(False)
                msg1 = ("Viewing properties of %s <br>") %(self.editCommand.struct.name) 
                msg2 = redmsg("To resize the strand, first convert it to a PAM3"\
                   " model")                    
                self.updateMessage(msg1 + msg2)
        else:
            if not self._pmGroupBox1.isEnabled():
                self._pmGroupBox1.setEnabled(True)
                msg1 = ("Viewing properties of %s <br>") %(self.editCommand.struct.name) 
                msg2 = "Use resize handles to resize the strand. Use sequence editor"\
                    "to assign a new sequence or the current one to a file."
                self.updateMessage(msg1 + msg2)
        
    def show(self):
        """
        Show this PM 
        As of 2007-11-20, it also shows the Sequence Editor widget and hides 
        the history widget. This implementation may change in the near future
        This method also retrives the name information from the 
        editCommand's structure for its name line edit field. 
        @see: DnaStrand_EditCommand.getStructureName()
        @see: self.close()
        """
        EditCommand_PM.show(self) 
        self._showSequenceEditor()
    
        if self.editCommand is not None:
            name = self.editCommand.getStructureName()
            if name is not None:
                self.nameLineEdit.setText(name)
                
    
    def close(self):
        """
        Close this property manager. 
        Also sets the name of the self.editCommand's structure to the one 
        displayed in the line edit field.
        @see self.show()
        @see: DnaSegment_EditCommand.setStructureName
        """
        if self.editCommand is not None:
            name = str(self.nameLineEdit.text())
            self.editCommand.setStructureName(name)
            
        if self.sequenceEditor:
            self.sequenceEditor.close()
            if self.win.viewFullScreenAction.isChecked() or \
               self.win.viewSemiFullScreenAction.isChecked():
                pass
            else:
                self.win.reportsDockWidget.show()
                
        EditCommand_PM.close(self)
            
    def _showSequenceEditor(self):
        if self.sequenceEditor:
            #hide the history widget first
            #(It will be shown back during self.close)
            #The history widget is hidden or shown only when both 
            # 'View > Full Screen' and View > Semi Full Screen actions 
            # are *unchecked*
            #Thus show or close methods won't do anything to history widget
            # if either of the above mentioned actions is checked.
            if self.win.viewFullScreenAction.isChecked() or \
               self.win.viewSemiFullScreenAction.isChecked():
                pass
            else:
                self.win.reportsDockWidget.hide()
            
            if not self.sequenceEditor.isVisible():
                #Show the sequence editor
                self.sequenceEditor.show()     
                                              
            self.updateSequence()

        
    def updateSequence(self):
        """
        Update the sequence string in the sequence editor
        @see: DnaSequenceEditor.setSequence()
        @see DnaSequenceEditor._determine_complementSequence()
        @see: DnaSequenceEditor.setComplementSequence()
        @see: DnaStrand.getStrandSequenceAndItsComplement()
        """
        #Read in the strand sequence of the selected strand and 
        #show it in the text edit in the sequence editor.
        ##strand = self.strandListWidget.getPickedItem()
        
        if not self.editCommand.hasValidStructure():
            return
        
        strand = self.editCommand.struct
        
        titleString = 'Sequence Editor for ' + strand.name
                           
        self.sequenceEditor.setWindowTitle(titleString)
        sequenceString, complementSequenceString = strand.getStrandSequenceAndItsComplement()
        if sequenceString:
            sequenceString = QString(sequenceString) 
            sequenceString = sequenceString.toUpper()
            #Set the initial sequence (read in from the file)
            self.sequenceEditor.setSequence(sequenceString)
            
            #Set the initial complement sequence for DnaSequence editor. 
            #do this independently because 'complementSequenceString' may have
            #some characters (such as * ) that denote a missing base on the 
            #complementary strand. this information is used by the sequence
            #editor. See DnaSequenceEditor._determine_complementSequence() 
            #for more details. See also bug 2787
            self.sequenceEditor.setComplementSequence(complementSequenceString)
            
    def change_struct_highlightPolicy(self,checkedState = False):
        """
        Change the 'highlight policy' of the structure being edited 
        (i.e. self.editCommand.struct) . 
        @param checkedState: The checked state of the checkbox that says 
                             'Don't highlight while editing DNA'. So, it 
                             its True, the structure being edited won't get
                             highlighted. 
        @see: DnaStrand.setHighlightPolicy for more comments        
        """        
        if self.editCommand and self.editCommand.hasValidStructure():
            highlight = not checkedState
            self.editCommand.struct.setHighlightPolicy(highlight = highlight)

    def _addWhatsThisText(self):
        """
        Add what's this text. 
        Abstract method.
        """
        pass
    
