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

from command_support.DnaOrCnt_PropertyManager import DnaOrCnt_PropertyManager


from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_LineEdit      import PM_LineEdit
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox


from widgets.prefs_widgets import connect_checkbox_with_boolean_pref
from utilities.prefs_constants import dnaStrandEditCommand_cursorTextCheckBox_changedBases_prefs_key
from utilities.prefs_constants import dnaStrandEditCommand_cursorTextCheckBox_numberOfBases_prefs_key
from utilities.prefs_constants import dnaStrandEditCommand_showCursorTextCheckBox_prefs_key


_superclass = DnaOrCnt_PropertyManager
class DnaStrand_PropertyManager( DnaOrCnt_PropertyManager):
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

    title         =  "DnaStrand Properties"
    pmName        =  title
    iconPath      =  "ui/actions/Properties Manager/Strand.png"

    def __init__( self, win, command ):
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
        self.dnaModel = 'PAM3'
        
        
        _superclass.__init__( self, 
                                    win,
                                    command)


        
        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        
        self._loadSequenceEditor()
        
        msg = "Use resize handles to resize the strand. Use sequence editor"\
                   "to assign a new sequence or the current one to a file."
        self.updateMessage(msg)
        
               
    
    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """        
                
        self._pmGroupBox1 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox1( self._pmGroupBox1 )
        self._displayOptionsGroupBox = PM_GroupBox( self, 
                                                    title = "Display Options" )
        self._loadDisplayOptionsGroupBox( self._displayOptionsGroupBox )
    
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
        
        
    def _loadDisplayOptionsGroupBox(self, pmGroupBox):
        """
        Overrides superclass method. 
        Also loads the color chooser widget. 
        """
        self._loadColorChooser(pmGroupBox)
        _superclass._loadDisplayOptionsGroupBox(self, pmGroupBox)
        
         
    def _connect_showCursorTextCheckBox(self):
        """
        Connect the show cursor text checkbox with user prefs_key.
        Overrides 
        DnaOrCnt_PropertyManager._connect_showCursorTextCheckBox
        """
        connect_checkbox_with_boolean_pref(
            self.showCursorTextCheckBox , 
            dnaStrandEditCommand_showCursorTextCheckBox_prefs_key)


    def _params_for_creating_cursorTextCheckBoxes(self):
        """
        Returns params needed to create various cursor text checkboxes connected
        to prefs_keys  that allow custom cursor texts. 
        @return: A list containing tuples in the following format:
                ('checkBoxTextString' , preference_key). PM_PrefsCheckBoxes 
                uses this data to create checkboxes with the the given names and
                connects them to the provided preference keys. (Note that 
                PM_PrefsCheckBoxes puts thes within a GroupBox)
        @rtype: list
        @see: PM_PrefsCheckBoxes
        @see: self._loadDisplayOptionsGroupBox where this list is used. 
        @see: Superclass method which is overridden here --
        DnaOrCnt_PropertyManager._params_for_creating_cursorTextCheckBoxes()
        """
        params = \
               [  #Format: (" checkbox text", prefs_key)
                  ("Number of bases", 
                   dnaStrandEditCommand_cursorTextCheckBox_numberOfBases_prefs_key),

                  ("Number of bases to be changed",
                   dnaStrandEditCommand_cursorTextCheckBox_changedBases_prefs_key) 
                 ]

        return params
    
        
    def getParameters(self):
        numberOfBases = self.numberOfBasesSpinBox.value()
        dnaForm  = self._conformation
        dnaModel = self.dnaModel
        color = self._colorChooser.getColor()
              
        return (numberOfBases, 
                dnaForm,
                dnaModel,
                color
                )
    
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
                
        numberOfBases, \
                     dnaForm, \
                     dnaModel, \
                     color  = params 
        
        if numberOfBases is not None:
            self.numberOfBasesSpinBox.setValue(numberOfBases)
        if dnaForm is not None:
            self._conformation = dnaForm
        if dnaModel is not None:
            self.dnaModel = dnaModel
         
        if color is not None:
            self._colorChooser.setColor(color)
    
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
            
        _superclass.connect_or_disconnect_signals(self, isConnect)
            
        
        change_connect(self.disableStructHighlightingCheckbox, 
                       SIGNAL('stateChanged(int)'), 
                       self.change_struct_highlightPolicy)
        
        change_connect(self.showCursorTextCheckBox, 
                       SIGNAL('stateChanged(int)'), 
                       self._update_state_of_cursorTextGroupBox)
        
    def model_changed(self): 
        """
        @see: DnaStrand_EditCommand.model_changed()
        @see: DnaStrand_EditCommand.hasResizableStructure()
        """
        isStructResizable, why_not = self.command.hasResizableStructure()
        if not isStructResizable:
            #disable all widgets
            if self._pmGroupBox1.isEnabled():
                self._pmGroupBox1.setEnabled(False)
                msg1 = ("Viewing properties of %s <br>") %(self.command.struct.name) 
                msg2 = redmsg("DnaStrand is not resizable. Reason: %s"%(why_not))                    
                self.updateMessage(msg1 + msg2)
        else:
            if not self._pmGroupBox1.isEnabled():
                self._pmGroupBox1.setEnabled(True)
                msg1 = ("Viewing properties of %s <br>") %(self.command.struct.name) 
                msg2 = "Use resize handles to resize the strand. Use sequence editor"\
                    "to assign a new sequence or the current one to a file."
                self.updateMessage(msg1 + msg2)
        
    def show(self):
        """
        Show this PM 
        As of 2007-11-20, it also shows the Sequence Editor widget and hides 
        the history widget. This implementation may change in the near future
        This method also retrives the name information from the 
        command's structure for its name line edit field. 
        @see: DnaStrand_EditCommand.getStructureName()
        @see: self.close()
        """
        _superclass.show(self) 
        self._showSequenceEditor()
    
        if self.command is not None:
            name = self.command.getStructureName()
            if name is not None:
                self.nameLineEdit.setText(name)     
           
    def close(self):
        """
        Close this property manager. 
        Also sets the name of the self.command's structure to the one 
        displayed in the line edit field.
        @see self.show()
        @see: DnaSegment_EditCommand.setStructureName
        """
        if self.command is not None:
            name = str(self.nameLineEdit.text())
            self.command.setStructureName(name)
            
        if self.sequenceEditor:
            self.sequenceEditor.close()
                            
        _superclass.close(self)
            
    def _showSequenceEditor(self):
        if self.sequenceEditor:
            if not self.sequenceEditor.isVisible():
                #Show the sequence editor
                #ATTENTION: the sequence editor also closes (temporarily) the
                #reports dockwidget (if visible) Its state is later restored when
                #the sequuence Editor is closed. 
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
        
        if not self.command.hasValidStructure():
            return
        
        strand = self.command.struct
        
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
        (i.e. self.command.struct) . 
        @param checkedState: The checked state of the checkbox that says 
                             'Don't highlight while editing DNA'. So, it 
                             its True, the structure being edited won't get
                             highlighted. 
        @see: DnaStrand.setHighlightPolicy for more comments        
        """        
        if self.command and self.command.hasValidStructure():
            highlight = not checkedState
            self.command.struct.setHighlightPolicy(highlight = highlight)

    def _addWhatsThisText(self):
        """
        Add what's this text. 
        Abstract method.
        """
        pass
    
