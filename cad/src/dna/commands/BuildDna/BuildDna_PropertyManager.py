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
from utilities.debug import print_compact_stack

from PyQt4.Qt import SIGNAL


from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_PushButton    import PM_PushButton
from PM.PM_SelectionListWidget import PM_SelectionListWidget

from widgets.DebugMenuMixin import DebugMenuMixin
from command_support.EditCommand_PM import EditCommand_PM

from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON
from PM.PM_Colors        import pmReferencesListWidgetColor
from utilities.Comparison import same_vals
from PM.PM_DnaBaseNumberLabelsGroupBox import PM_DnaBaseNumberLabelsGroupBox

from utilities.GlobalPreferences import USE_COMMAND_STACK

DEBUG_CHANGE_COUNTERS =  False
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

    title         =  "Build DNA"
    pmName        =  title
    iconPath      =  "ui/actions/Tools/Build Structures/DNA.png"
    sponsor_keyword = None # Nanorex is the sponsor. Change to 'DNA' to the
                             # the NUPACK logo.

    def __init__( self, command ):
        """
        Constructor for the Build DNA property manager.
        """
        
        #For model changed signal
        self._previousSelectionParams = None
        
        self._previousStructureParams = None
                
        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False           
        
        EditCommand_PM.__init__( self, command)


        DebugMenuMixin._init1( self )

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        

    
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
        
        change_connect(self.editStrandPropertiesButton,
                      SIGNAL("clicked()"),
                      self._editDnaStrand)
        
        change_connect(self.editSegmentPropertiesButton,
                      SIGNAL("clicked()"),
                      self._editDnaSegment)
        
        change_connect(self.searchForCrossoversButton,
                      SIGNAL("clicked()"),
                      self._enterMakeCrossoversCommand)
        
        self._baseNumberLabelGroupBox.connect_or_disconnect_signals(isConnect)
 
    
    def enable_or_disable_gui_actions(self, bool_enable = False):
        """
        Enable or disable some gui actions when this property manager is 
        opened or closed, depending on the bool_enable. 
        
        """
        #For new command API, we will always show the exit button to check 
        #if Exit button really exits the subcommand and the parent command 
        #(earlier there were bugs) . Regaring 'whether this should be the 
        #default behavior', its a UI design issue and we will worry about it 
        #later -- Ninad 2008-08-27 (based on an email exchanged with Bruce)
        if not USE_COMMAND_STACK:
            #TODO: This is bad. It would have been much better to enable/disable 
            #gui actions using a API method in command/commandSequencer which gets 
            #called when you enter another command exiting or suspending the 
            #previous one. . At present. it doesn't exist (first needs cleanup in 
            #command/command sequencer (Done and other methods._)-- Ninad 2008-01-09
            if hasattr(self.command, 'flyoutToolbar') and \
               self.command.flyoutToolbar:            
                self.command.flyoutToolbar.exitModeAction.setEnabled(not bool_enable)
                
                
    #New command API method -- implemented on 2008-08-27
    def _update_UI_do_updates(self):
        """
        This method should replace model_changed() eventually. 
        This is used with USE_COMMAND_STACK debug flag
        """   
        self.model_changed()            
                    
    def model_changed(self):
        """       
        When the command is treated as a 'command' by the 
        commandSequencer, this method will override basicCommand.model_changed.
        For more info, see BuildAtomsPropertyManager.model_changed docstring.
        """         
        
                
                
        newSelectionParams = self._currentSelectionParams()   
        
        selection_params_unchanged = same_vals(newSelectionParams,
                                               self._previousSelectionParams)
        
        #introducing self._previousStructureParams and adding structure_params_unchanged
        #check to the 'if' condition below fixes bug 2910. 
        structure_params_unchanged = same_vals(self._previousStructureParams, 
                                                self._currentStructureParams())
        
        if selection_params_unchanged and \
           structure_params_unchanged:
            #This second condition above fixes bug 2888
            return
        
        self._previousStructureParams = self._currentStructureParams()
        
        if not selection_params_unchanged and structure_params_unchanged:            
            
            self._previousSelectionParams = newSelectionParams  
            
            selectedStrands, selectedSegments = newSelectionParams
                       
            self.strandListWidget.updateSelection(selectedStrands) 
            self.segmentListWidget.updateSelection(selectedSegments)
            
            if len(selectedStrands) == 1:
                self.editStrandPropertiesButton.setEnabled(True)                         
            else:
                self.editStrandPropertiesButton.setEnabled(False)  
            
            if len(selectedSegments) == 1:
                self.editSegmentPropertiesButton.setText("Edit Properties...")
                self.editSegmentPropertiesButton.setEnabled(True)
            elif len(selectedSegments) > 1:
                resizeString = "Resize Selected Segments (%d)..." % len(selectedSegments)
                self.editSegmentPropertiesButton.setText(resizeString)
                self.editSegmentPropertiesButton.setEnabled(True)
                self.searchForCrossoversButton.setEnabled(True)
            else:
                self.editSegmentPropertiesButton.setText("Edit Properties...")
                self.editSegmentPropertiesButton.setEnabled(False)
                self.searchForCrossoversButton.setEnabled(False)
                         
        #Update the strand and segmment list widgets. 
        #Ideally it should only update when the structure is modified
        #example --when structure is deleted. But as of 2008-02-21
        #this feature is not easily available in the API method. 
        #The list widgets are updated even when selection changes.
        # [bruce 080804 addendum: use of change counters could fix that.]
        #
        #NOTE: If this is called before listwidget's 'updateSelection' call, 
        #done above, it 'may give' (as of 2008-02-25, it is unlikely to happen 
        #because of a better implementation)  C/C++ object deleted errors. 
        #So better to do it in the end. Cause -- unknown. 
        #Guess : something to do with clearing the widget list and then reading
        #items (done by self.updateListWidgets).
        #...This probably interferes with the selection
        #within that list. So better to do it after updating the selection.
        if not structure_params_unchanged:  
            self.updateListWidgets()   
                      
    def _currentSelectionParams(self):
        """
        Returns a tuple containing current selection parameters. These 
        parameters are then used to decide whether updating widgets
        in this property manager is needed when L{self.model_changed}
        method is called.
        
        @return: A tuple that contains following selection parameters
                   - Total number of selected atoms (int)
                   - Selected Atom if a single atom is selected, else None
                   - Position vector of the single selected atom or None
        @rtype:  tuple
        
        @NOTE: This method may be renamed in future. 
        It's possible that there are other groupboxes in the PM that need to be 
        updated when something changes in the glpane.        
        """
         
        selectedStrands = []
        selectedSegments = []
        if self.command is not None and self.command.hasValidStructure():
            selectedStrands = self.command.struct.getSelectedStrands()
            selectedSegments = self.command.struct.getSelectedSegments()             
                    
        return (selectedStrands, selectedSegments)
    
    def _currentStructureParams(self):
        """
        Return current structure parameters of interest to self.model_changed. 
        Right now it only returns the number of strands within the structure
        (or None). This is a good enough check (and no need to compare 
        each and every strand within the structure with a previously stored 
        set of strands).
        """
        #Can it happen that the total number of strands remains the same even 
        #after some alterations to the strands? Unlikely. (Example: a single
        #Break strands operation will increase the number of strands by one. 
        #Or Join strands decrease it by 1)
        params = None
        
        if self.command and self.command.hasValidStructure():
            strandList = []
            strandList = self.command.struct.getStrands()
            params = len(strandList)
            
        return params 
           
    
    def close(self):
        """
        Closes the Property Manager. Overrides EditCommand_PM.close()
        """
        #Clear tags, if any, due to the selection in the self.strandListWidget.
        if self.strandListWidget:
            self.strandListWidget.clear()
        
        if self.segmentListWidget:
            self.segmentListWidget.clear()
            
        EditCommand_PM.close(self)
    
    def show(self):
        """
        Show this PM 
        As of 2007-11-20, it also shows the Sequence Editor widget and hides 
        the history widget. This implementation may change in the near future
        """
        EditCommand_PM.show(self) 
        if not USE_COMMAND_STACK:
            self.updateListWidgets()    
        
        self.updateMessage("Use appropriate command in the command "\
                               "toolbar to create or modify a DNA Object"\
                               "<br>" )
        
    def _editDnaStrand(self):  
        """
        Enter the DnaStrand_EditCommand to edit the selected strand. 
        """
        
        if not self.command.hasValidStructure():
            return
        
        selectedStrandList = self.command.struct.getSelectedStrands()
        
        if len(selectedStrandList) == 1:     
            strand = selectedStrandList[0]
            strand.edit()


    def _editDnaSegment(self):
        """
        """
        if self.command is not None and self.command.hasValidStructure(): 
            selectedSegments = self.command.struct.getSelectedSegments()
            if len(selectedSegments) == 1:
                selectedSegments[0].edit()
            elif len(selectedSegments) > 1:
                self.win.resizeSelectedDnaSegments()
    
    def _enterMakeCrossoversCommand(self):
        """
        If more than one segments in the segment list widget 
        are selected, enter make crossovers  command
        
        @BUG: This enters Make Crossover command which searches for *ALL* 
        of the selected DnaSegments in the model and not just the selected 
        segments of the DnaGroup you are editing in the BuildDna command
        This is misleading.
        
        """
        self.win.enterMakeCrossoversCommand()
                       
        
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
        if not USE_COMMAND_STACK:
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
        #doesn't implement the dna data model yet. Until that's implemented, we
        #will do an isinstance(node, Chunk) check. Note that it includes both  
        #Strands and Axis chunks -- Ninad 2008-01-09
        
        if self.command and self.command.hasValidStructure():
            strandChunkList = self.command.struct.getStrands()
                        
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
        if self.command and self.command.hasValidStructure(): 
            def func(node):
                if isinstance(node, self.win.assy.DnaSegment):
                    segmentList.append(node)    
                    
            self.command.struct.apply2all(func)
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
        
        self._loadBaseNumberLabelGroupBox(self)
        
        
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
                                                       heightByRows = 9 )
        self.strandListWidget.setTagInstruction('PICK_ITEM_IN_GLPANE')
    
        self.editStrandPropertiesButton = PM_PushButton( 
            pmGroupBox,
            label = "",
            text  = "Edit Properties..." )
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
        
        self.searchForCrossoversButton = PM_PushButton( 
            pmGroupBox,
            label = "",
            text  = "Search For Crossovers..." )
        self.searchForCrossoversButton.setEnabled(False)
        
        
    def _loadBaseNumberLabelGroupBox(self, pmGroupBox):
        """
        """
        self._baseNumberLabelGroupBox = PM_DnaBaseNumberLabelsGroupBox(pmGroupBox, 
                                                                       self.command)
    
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
