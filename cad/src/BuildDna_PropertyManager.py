# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildDna_PropertyManager.py

@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:
Ninad 2008-01-11: Created


TODO: as of 2008-01-11
- Needs more documentation and the file is subjected to heavy revision. 
This is an initial implementation of default Dna edit mode.
- Methods such as callback_addSegments might be renamed.
BUGS:
- Has bugs such as -- Flyout toolbar doesn't get updated when you return to 
  BuildDna_EditCommand from a a temporary command. 
- Just entering and leaving BuilddDna_EditCommand creates an empty DnaGroup
"""
from utilities import debug_flags
from debug import  print_compact_stack

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QString

from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_PushButton    import PM_PushButton
from PM.PM_SelectionListWidget import PM_SelectionListWidget

from DebugMenuMixin import DebugMenuMixin
from EditCommand_PM import EditCommand_PM

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_Constants     import pmCancelButton
from PM.PM_Colors        import pmReferencesListWidgetColor
from utilities.Comparison import same_vals
from dna_model.DnaSegment import DnaSegment

class BuildDna_PropertyManager( EditCommand_PM, DebugMenuMixin ):
    """
    The BuildDna_PropertyManager class provides a Property Manager 
    for the B{Build > DNA } command.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "DNA Properties"
    pmName        =  title
    iconPath      =  "ui/actions/Tools/Build Structures/DNA.png"

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
        
        
        EditCommand_PM.__init__( self, 
                                    win,
                                    editCommand)


        DebugMenuMixin._init1( self )

        self.showTopRowButtons( pmDoneButton | \
                                pmCancelButton | \
                                pmWhatsThisButton)
        
        self._loadSequenceEditor()
                
            
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
    
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        #TODO: This is a temporary fix for a bug. When you invoke a temporary mode 
        # entering such a temporary mode keeps the signals of 
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
          
        self.strandListWidget.connect_or_disconnect_signals(isConnect)        
        self.segmentListWidget.connect_or_disconnect_signals(isConnect)
        
        if self.sequenceEditor:
            self.sequenceEditor.connect_or_disconnect_signals(isConnect)
            
            change_connect( self.sequenceEditor.assignStrandSequencePushButton,
                      SIGNAL("clicked()"),
                      self.assignStrandSequence)
        
                
        change_connect(self.editStrandPropertiesButton,
                      SIGNAL("clicked()"),
                      self._showSequenceEditor)
        
        change_connect(self.editSegmentPropertiesButton,
                      SIGNAL("clicked()"),
                      self._editDnaSegment)

    def assignStrandSequence(self):
        """
        Assigns the sequence typed in the sequence editor text field to 
        the selected strand chunk. The method it invokes also assigns 
        a complimentary sequence to the mate strand.
        @see: Chunk.setStrandSequence
        """
        sequenceString = self.sequenceEditor.getPlainSequence()
        sequenceString = str(sequenceString)
        #@We can do this only if only a single item is selected in the 
        #strand list widget (which is what happens as of 2008-01-11)
        strand = self.strandListWidget.getPickedItem() 
        #Set the strand sequence for the selected strand and also change 
        #the strand sequence of its mate strand!
        strand.setStrandSequence(sequenceString)   
    
    def enable_or_disable_gui_actions(self, bool_enable = False):
        """
        Enable or disable some gui actions when this property manager is 
        opened or closed, depending on the bool_enable. 
        
        """
        #TODO: This is bad. It would have been much better to enable/disable 
        #gui actions using a API method in command/commandSequencer which gets 
        #called when you enter another command exiting or suspending the 
        #previous one. . At present. it doesn't exist (first needs cleanup in 
        #command/command sequencer (Done and other methods._)-- Ninad 2008-01-09
        if hasattr(self.editCommand, 'flyoutToolbar') and \
           self.editCommand.flyoutToolbar:            
            self.editCommand.flyoutToolbar.exitDnaAction.setEnabled(not bool_enable)
            self.editCommand.flyoutToolbar.orderDnaAction.setEnabled(not bool_enable)
        
    def model_changed(self):
        """       
        When the editCommand is treated as a 'command' by the 
        commandSequencer. this method will override basicCommand.model_changed.
        
        @WARNING: Ideally this property manager should implement both
               model_changed and selection_changed methods in the mode/command
               API. 
               model_changed method will be used here when the selected atom is 
               dragged, transmuted etc. The selection_changed method will be 
               used when the selection (picking/ unpicking) changes. 
               At present, selection_changed and model_changed methods are 
               called too frequently that it doesn't matter which one you use. 
               Its better to use only a single method for preformance reasons 
               (at the moment). This should change when the original 
               methods in the API are revised to be called at appropiraite 
               time. 
        """  
        newSelectionParams = self._currentSelectionParams()
        
                
        if same_vals(newSelectionParams, self.previousSelectionParams):
            return
        
        #Update the strand and segmment list widgets. 
        #Ideally it should only update when the structure is modified 
        #example --when structure is deleted. But as of 2008-02-21
        #this feature is not easily available in the API method. 
        #see Command class for some proposed methods such as 'something_changed'
        #etc. The list widgets are updated even when selection changes. 
        if self.editCommand.hasValidStructure():
           self.updateListWidgets()
                
        self.previousSelectionParams = newSelectionParams  
        
        selectedStrands, selectedSegments = newSelectionParams
               
        self.strandListWidget.updateSelection(selectedStrands) 
        self.segmentListWidget.updateSelection(selectedSegments)
        
        if len(selectedStrands) == 1:
            self.editStrandPropertiesButton.setEnabled(True)
            if self.sequenceEditor:
                self.sequenceEditor.update_state(bool_enable = True) 
            if self.sequenceEditor and self.sequenceEditor.isVisible():
                self._updateSequence(selectedStrands[0])                           
        else:
            self.editStrandPropertiesButton.setEnabled(False)
            if self.sequenceEditor:       
                self.sequenceEditor.update_state(bool_enable = False)   
        
        if len(selectedSegments) == 1:
            self.editSegmentPropertiesButton.setEnabled(True)
        else:
            self.editSegmentPropertiesButton.setEnabled(False)
                         
        
    def _currentSelectionParams(self):
        """
        NOT CALLED YET. This needs commandSequencer to treat various 
        edit controllers as commands. Until then, the 'model_changed' method 
        (and thus this method) will  never be called.
        
        Returns a tuple containing current selection parameters. These 
        parameters are then used to decide whether updating widgets
        in this property manager is needed when L{self.model_changed} or 
        L{self.selection_changed} methods are called. 
        @return: A tuple that contains following selection parameters
                   - Total number of selected atoms (int)
                   - Selected Atom if a single atom is selected, else None
                   - Position vector of the single selected atom or None
        @rtype:  tuple
        @NOTE: The method name may be renamed in future. 
        Its possible that there are other groupboxes in the PM that need to be 
        updated when something changes in the glpane.        
        """
         
        selectedStrands = []
        selectedSegments = []
        if self.editCommand is not None and self.editCommand.hasValidStructure():
            selectedStrands = self.editCommand.struct.getSelectedStrands()
            selectedSegments = self.editCommand.struct.getSelectedSegments()
             
                    
        return (selectedStrands, selectedSegments)
                
             
    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """   
        if self.editCommand:
            self.editCommand.preview_or_finalize_structure(previewing = False)
        self.win.toolsDone()
    
    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """
        if self.editCommand:
            self.editCommand.cancelStructure()            
        self.win.toolsCancel()
        
    
    def close(self):
        """
        Closes the Property Manager. Overrides EditCommand_PM.close()
        """
        #Clear tags, if any, due to the selection in the self.strandListWidget.
        if self.strandListWidget:
            self.strandListWidget.clear()
        
        if self.segmentListWidget:
            self.segmentListWidget.clear()
        
        if self.sequenceEditor:
            self.sequenceEditor.hide()
            if self.win.viewFullScreenAction.isChecked() or \
               self.win.viewSemiFullScreenAction.isChecked():
                pass
            else:
                self.win.reportsDockWidget.show()
           
        EditCommand_PM.close(self)
    
    def show(self):
        """
        Show this PM 
        As of 2007-11-20, it also shows the Sequence Editor widget and hides 
        the history widget. This implementation may change in the near future
        """
        EditCommand_PM.show(self) 
        self.updateListWidgets()    
    
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
            
            selectedStrandList = self.editCommand.struct.getSelectedStrands()
            
            if len(selectedStrandList) == 1:                   
                self._updateSequence(selectedStrandList[0])
    
    def _updateSequence(self, pickedStrand):
        """
        Update the sequence string in the sequence editor
        """
        #Read in the strand sequence of the selected strand and 
        #show it in the text edit in the sequence editor.
        ##strand = self.strandListWidget.getPickedItem()
        
        strand = pickedStrand
        
        titleString = 'Sequence Editor for ' + strand.name
        
        if self.struct:
            titleString = titleString +  ' [of ' + self.struct.name + ']'
            
        self.sequenceEditor.setWindowTitle(titleString)
        
        sequenceString = strand.getStrandSequence()
        if sequenceString:
            sequenceString = QString(sequenceString) 
            sequenceString = sequenceString.toUpper()
            self.sequenceEditor.setSequence(sequenceString) 
    
    def _editDnaSegment(self):
        """
        """
        if self.editCommand is not None and self.editCommand.hasValidStructure(): 
            selectedSegments = self.editCommand.struct.getSelectedSegments()
            if len(selectedSegments) == 1:
                selectedSegments[0].edit()
    
        
    def _update_widgets_in_PM_before_show(self):
        """
        Update various widgets  in this Property manager.
        Overrides EditCommand_PM._update_widgets_in_PM_before_show. 
        The various  widgets , (e.g. spinboxes) will get values from the 
        structure for which this propMgr is constructed for 
        (self.editcCommand.struct)
        
        @see: MotorPropertyManager._update_widgets_in_PM_before_show
        @see: self.show  
        """  
        self.updateListWidgets()
        
    
    def updateListWidgets(self):
        """
        Update List Widgets (strand list and segment list)
        in this property manager
        @see: self.updateSegmentListWidgets, self.updateStrandListWidget
        """
        self.updateStrandListWidget() 
        self.updateSegmentListWidget()
          
       
    def updateStrandListWidget(self):   
        """
        Update the list of items inside the strandlist widget 
        Example: Origianally it shows two srands. User now edits an
        existing dna, and deletes some of the strands, hits done. User then 
        again invokes the Edit command for this dna object -- now the strand 
        list widget must be updated so that it shows only the existing strands.
        
        @see: B{Chunk.isStrandChunk}
        @see: self.updateListWidgets, self.updateSegmentListWidget
        """
        #TODO: 
        #Filter out only the chunks inside the dna group. the DnaDuplex.make 
        #doesn't  implement the dan data model yet. Until thats implemented ,we
        #will do an isinstance(node, Chunk) check . Note that it includes both  
        #Strands and Axis chunks -- Ninad 2008-01-09
        
        if self.editCommand and self.editCommand.hasValidStructure():
            strandChunkList = self.editCommand.struct.getStrands()
                        
            self.strandListWidget.insertItems(
                row = 0,
                items = strandChunkList)
        else:
            self.strandListWidget.clear()
    
    def updateSegmentListWidget(self):
        """
        Update the list of segments shown in the segments list widget
        @see: self.updateListWidgets, self.updateStrandListWidget
        """
        segmentList = []
        if self.editCommand and self.editCommand.struct: 
            def func(node):
                if isinstance(node, DnaSegment):
                    segmentList.append(node)    
                    
            self.editCommand.struct.apply2all(func)
            
            self.segmentListWidget.insertItems(
                row = 0,
                items = segmentList)
        else:
            self.segmentListWidget.clear()
             
            
    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """        
        #Unused 'References List Box' to be revided. (just commented out for the
        #time being. 
        ##self._pmGroupBox1 = PM_GroupBox( self, title = "Reference Plane" )
        ##self._loadGroupBox1( self._pmGroupBox1 )
        
        self._pmGroupBox2 = PM_GroupBox( self, title = "Strands" )
        self._loadGroupBox2( self._pmGroupBox2 )
        
        self._pmGroupBox3 = PM_GroupBox( self, title = "Segments" )
        self._loadGroupBox3( self._pmGroupBox3 )
        
        
    def _loadGroupBox1(self, pmGroupBox):
        """
        load widgets in groupbox1
        """
        self.referencePlaneListWidget = PM_SelectionListWidget(
            pmGroupBox,
            self.win,
            label = "",
            color = pmReferencesListWidgetColor,
            heightByRows = 2)
    
    def _loadGroupBox2(self, pmGroupBox):
        """
        load widgets in groupbox2
        """
        
        self.strandListWidget = PM_SelectionListWidget(pmGroupBox,
                                                       self.win,
                                                       label = "",
                                                       heightByRows = 5 )
        self.strandListWidget.setTagInstruction('PICK_ITEM_IN_GLPANE')
    
        self.editStrandPropertiesButton = PM_PushButton( 
            pmGroupBox,
            label = "",
            text  = "Sequence Editor..." )
        self.editStrandPropertiesButton.setEnabled(False)
        
    def _loadGroupBox3(self, pmGroupBox):
        """
        load widgets in groupbox3
        """
        
        self.segmentListWidget = PM_SelectionListWidget(pmGroupBox,
                                                       self.win,
                                                       label = "",
                                                       heightByRows = 4 )
        self.segmentListWidget.setObjectName('Segment_list_widget')
        self.segmentListWidget.setTagInstruction('PICK_ITEM_IN_GLPANE')
        
    
        self.editSegmentPropertiesButton = PM_PushButton( 
            pmGroupBox,
            label = "",
            text  = "Edit Properties..." )
        self.editSegmentPropertiesButton.setEnabled(False)
    
 
    def _addWhatsThisText( self ):
        """
        What's This text for widgets in the DNA Property Manager.  
        """
        pass
                
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the DNA Property Manager.  
        """
        pass
