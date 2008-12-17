# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaStrand_PropertyManager.py

@author: Ninad
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

Special notes:
- Sequence editor is also created in BuildDna_PropertyManager (of course 
its a child of that PM) . See if that creates any issues. 
- Copies some methods from BuildDna_PropertyManager. 

Bugs to fix:

Bug 2952: 
- Typing in new sequence will not take if you select another strand,
  (even if you hit Enter after typing in the new sequence).

Bug 2953:
- Getting the following error msg (see bug report for details):
  "QTextCursor::setPosition: Position '#' out of range"

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
    iconPath      =  "ui/actions/Properties Manager/Strand.png"

    def __init__( self, command ):
        """
        Constructor for the Build DNA property manager.
        """
                
        self.sequenceEditor = None      
        
        self._numberOfBases = 0 
        self._conformation = 'B-DNA'
        self.dnaModel = 'PAM3'
        
        _superclass.__init__( self, command)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        return
    
    def _addGroupBoxes( self ):
        """
        Add group boxes to this PM.
        """        
                
        self._pmGroupBox1 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox1( self._pmGroupBox1 )
        self._displayOptionsGroupBox = PM_GroupBox( self, 
                                                    title = "Display Options" )
        self._loadDisplayOptionsGroupBox( self._displayOptionsGroupBox )
        
        #Sequence Editor. This is NOT a groupbox, needs cleanup. Doing it here 
        #so that the sequence editor gets connected! Perhaps 
        #superclass should define _loadAdditionalWidgets. -- Ninad2008-10-03
        self._loadSequenceEditor()
        return
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 1.
        """
        
        self.nameLineEdit = PM_LineEdit( pmGroupBox,
                         label         =  "Name:",
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
        #editable only by using the resize handles.
        self.numberOfBasesSpinBox.setEnabled(False)        
        return
            
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
        return
        
    def _loadDisplayOptionsGroupBox(self, pmGroupBox):
        """
        Overrides superclass method. 
        Also loads the color chooser widget. 
        """
        self._loadColorChooser(pmGroupBox)
        _superclass._loadDisplayOptionsGroupBox(self, pmGroupBox)
        return
         
    def _connect_showCursorTextCheckBox(self):
        """
        Connect the show cursor text checkbox with user prefs_key.
        Overrides 
        DnaOrCnt_PropertyManager._connect_showCursorTextCheckBox
        """
        connect_checkbox_with_boolean_pref(
            self.showCursorTextCheckBox , 
            dnaStrandEditCommand_showCursorTextCheckBox_prefs_key)
        return


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
        name = self.nameLineEdit.text()
        numberOfBases = self.numberOfBasesSpinBox.value()
        dnaForm  = self._conformation
        dnaModel = self.dnaModel
        color = self._colorChooser.getColor()
              
        return (numberOfBases, 
                dnaForm,
                dnaModel,
                color,
                name
                )
    
    def setParameters(self, params):
        """
        This is usually called when you are editing an existing structure. 
        It also gets called when selecting a new strand (within this command).
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
            color, \
            name = params 
        
        if numberOfBases is not None:
            self.numberOfBasesSpinBox.setValue(numberOfBases)
        if dnaForm is not None:
            self._conformation = dnaForm
        if dnaModel is not None:
            self.dnaModel = dnaModel
         
        if color is not None:
            self._colorChooser.setColor(color)
            
        if name:  # Minimal test. Should add a validator. --Mark 2008-12-16
            self.nameLineEdit.setText(name)
        
        # This gets called when we enter the command *or* when selecting a new
        # strand. In either case, we must update the sequence in the sequenece
        # editor. Fixes bug 2951. --Mark 2008-12-16
        if self.command and self.command.hasValidStructure():
            self.updateSequence(strand = self.command.struct)
        return
    
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
        
        change_connect(self.nameLineEdit,
                       SIGNAL("editingFinished()"),
                       self._nameChanged)
        return
        
    def _update_UI_do_updates(self):
        """
        @see: Command_PropertyManager. _update_UI_do_updates()
        @see: DnaStrand_EditCommand.command_update_UI()
        @see: DnaStrand_EditCommand.hasResizableStructure()
        """
        isStructResizable, why_not = self.command.hasResizableStructure()
        if not isStructResizable:
            #disable all widgets
            if self._pmGroupBox1.isEnabled():
                self._pmGroupBox1.setEnabled(False)
                msg1 = ("Attention: ") % (self.command.struct.name) 
                msg2 = redmsg("DnaStrand <b>%s</b> is not resizable. Reason: %s" % \
                              (self.command.struct.name, why_not))
                self.updateMessage(msg1 + msg2)
        else:
            if not self._pmGroupBox1.isEnabled():
                self._pmGroupBox1.setEnabled(True)
            msg1 = ("Editing <b>%s</b>. ") % (self.command.struct.name) 
            msg2 = "Use resize handles to resize the strand. Use sequence editor"\
                "to assign a new sequence or the current one to a file."
            self.updateMessage(msg1 + msg2)
        return
        
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
        return
    
    def updateSequence(self, strand = None):
        """
        Public method provided for convenience. If any callers outside of this 
        command need to update the sequence in the sequence editor, they can simply 
        do DnaStrand_ProprtyManager.updateSequence() rather than 
        DnaStrand_ProprtyManager.sequenceEditor.updateSequence()
        @see: Ui_DnaSequenceEditor.updateSequence()
        """
        if self.sequenceEditor:
            self.sequenceEditor.updateSequence(strand = strand)
        return
        
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
        return

    def _addWhatsThisText(self):
        """
        Add what's this text. 
        Abstract method.
        """
        pass
    
    def _nameChanged(self): # Added by Mark. 2008-12-16
        """
        Slot for "Name" field. Changes the name of the strand if the user types
        in a new name.
        
        @warning: this lacks a validator. User can type in a name with invalid
                  characters.
        """
        if not self.command.hasValidStructure():
            return
        
        name = str(self.nameLineEdit.text())
        
        if not name: # Minimal test. Should add a validator. Ask Bruce for example validator code somewhere. --Mark 2008-12-16
            if self.command.hasValidStructure():
                self.nameLineEdit.setText(self.command.getStructureName())
                
            return
        
        self.command.setStructureName(name)
        
        self._update_UI_do_updates() # Updates the message box.
        
        return
    
