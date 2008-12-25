# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildNanotube_PropertyManager.py

@author: Ninad, Mark
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:
2008-01-11 Ninad: Created
"""
import foundation.env as env
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QString
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_PushButton    import PM_PushButton
from PM.PM_SelectionListWidget import PM_SelectionListWidget
from command_support.EditCommand_PM import EditCommand_PM
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON
from utilities.Comparison import same_vals
from cnt.model.NanotubeSegment import getAllNanotubeSegmentsInPart

_superclass = EditCommand_PM
class BuildNanotube_PropertyManager(EditCommand_PM):
    """
    The BuildNanotube_PropertyManager class provides a Property Manager 
    for the B{Build > CNT } command.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Build Nanotube"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/BuildNanotube/BuildNanotube.png"

    def __init__( self, command ):
        """
        Constructor for the Build Nanotube property manager.
        """
        
        #Attributes for self._update_UI_do_updates() to keep track of changes
        #in these , since the last call of that method. These are used to 
        #determine whether certain UI updates are needed. 
        self._previousSelectionParams = None        
        self._previousStructureParams = None
        self._previousCommandStackParams = None

        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False
        
        EditCommand_PM.__init__( self, command)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
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
        #mode, entering such a temporary mode keeps the signals of PM from the 
        #previous mode connected (but while exiting that temporary mode and 
        #reentering the previous mode, it actually reconnects the signal! 
        #This gives rise to lots of bugs. This needs a more general fix in 
        #the Temporary mode API. 
        # -- Ninad 2008-01-09 (similar comment exists in MovePropertyManager.py
        
        if isConnect and self.isAlreadyConnected:
            return 
        
        if not isConnect and self.isAlreadyDisconnected:
            return
        
        self.isAlreadyConnected = isConnect
        self.isAlreadyDisconnected = not isConnect
        
        if isConnect:
            change_connect = self.win.connect     
        else:
            change_connect = self.win.disconnect 
        
        self.nanotubeListWidget.connect_or_disconnect_signals(isConnect)
        
        change_connect(self.editNanotubePropertiesButton,
                      SIGNAL("clicked()"),
                      self._editNanotube)
        return
    
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
        pass
    
    def _update_UI_do_updates(self):
        """
        Overrides superclass method. 
        
        @see: Command_PropertyManager._update_UI_do_updates()
        """
        
        newSelectionParams = self._currentSelectionParams()
        current_struct_params = self._currentStructureParams()
        
        selection_params_unchanged = same_vals(newSelectionParams,
                                               self._previousSelectionParams)
        
        #introducing self._previousStructureParams and 
        #adding structure_params_unchanged check to the 'if' condition below 
        #fixes bug 2910. 
        structure_params_unchanged = same_vals(self._previousStructureParams, 
                                                current_struct_params)
        
        current_command_stack_params = self._currentCommandStackParams()
        
        #Check if command stack params changed since last call of this 
        #PM update method. This is used to fix bugs like 2940
        command_stack_params_unchanged = same_vals(
            self._previousCommandStackParams, current_command_stack_params)
              
        #No need to proceed if any of the selection/ structure and commandstack 
        #parameters remained unchanged since last call. --- [CONDITION A]
        if selection_params_unchanged and \
           structure_params_unchanged and \
           command_stack_params_unchanged:
            return
        
        self._previousStructureParams = current_struct_params
        self._previousSelectionParams =  newSelectionParams         
        self._previousCommandStackParams  = current_command_stack_params
        
        if structure_params_unchanged: 
            #NOTE: We checked if either of the selection struct or command stack
            #parameters or both changed. (this was referred as '[CONDITION A]' 
            #above). So, this condition (structure_params_unchanged)also means 
            #either selection or command stack or both parameters were changed.    
            
            if not command_stack_params_unchanged:
                #update the nanotube list widget *before* updating the selection if 
                #the command stack changed. This ensures that the selection box
                #appears around the list widget items that are selected.
                self.updateNanotubeListWidget()
                
            selectedNanotubeSegments = newSelectionParams    
            
            self.nanotubeListWidget.updateSelection(selectedNanotubeSegments) 
            
            # Enable/disable "Edit Sequence" button.
            if len(selectedNanotubeSegments) == 1:
                self.editNanotubePropertiesButton.setEnabled(True)
            else:
                self.editNanotubePropertiesButton.setEnabled(False)
            return
        
        self.updateNanotubeListWidget()
        return
    
    def _currentCommandStackParams(self):
        """
        The return value is supposed to be used by BUILD_NANOTUBE command PM ONLY
        and NOT by any subclasses.         
        
        Returns a tuple containing current command stack change indicator and 
        the name of the command 'BUILD_NANOTUBE'. These 
        parameters are then used to decide whether updating widgets
        in this property manager is needed, when self._update_UI_do_updates()
        is called. 
        
        @NOTE: 
        - Command_PropertyManager.update_UI() already does a check to see if 
          any of the global change indicators in assembly (command_stack_change, 
          model_change, selection_change) changed since last call and then only
          calls self._update_UI_do_updates(). 
        - But this method is just used to keep track of the 
          local command stack change counter in order to update the list 
          widgets.      
        - This is used to fix bug 2940
        
        @see: self._update_UI_do_updates()
        """
        commandStackCounter = self.command.assy.command_stack_change_indicator()
        #Append 'BUILD_NANOTUBE to the tuple to be returned. This is just to remind 
        #us that this method is meant for BUILD_NANOTUBE command PM only. (and not 
        #by any subclasses) Should we assert this? I think it will slow things 
        #down so this comment is enough -- Ninad 2008-09-30
        return (commandStackCounter, 'BUILD_NANOTUBE')
        
    def _currentSelectionParams(self):
        """
        Returns a tuple containing current selection parameters. These 
        parameters are then used to decide whether updating widgets
        in this property manager is needed when L{self.model_changed}
        method is called.
        
        @return: A tuple that contains total number of selected nanotubes.
        @rtype:  tuple
        
        @NOTE: This method may be renamed in future. 
        It's possible that there are other groupboxes in the PM that need to be 
        updated when something changes in the glpane.        
        """
        selectedNanotubeSegments = []
        if self.command is not None: # and self.command.hasValidStructure():
            selectedNanotubeSegments = self.win.assy.getSelectedNanotubeSegments()          
        return (selectedNanotubeSegments)
    
    def _currentStructureParams(self):
        """
        Return current structure parameters of interest to self.model_changed. 
        Right now it only returns the number of nanotubes within the structure
        (or None). This is a good enough check (and no need to compare 
        each and every nanotube within the structure with a previously stored 
        set of strands).
        """
        params = None
        
        if self.command: # and self.command.hasValidStructure():
            nanotubeSegmentList = []
            nanotubeSegmentList = getAllNanotubeSegmentsInPart(self.win.assy)
            params = len(nanotubeSegmentList)
        
        return params
    
    def close(self):
        """
        Closes the Property Manager. Overrides EditCommand_PM.close()
        """
        #Clear tags, if any, due to the selection in the self.strandListWidget.
        #self.nanotubeListWidget.clear()
        env.history.statusbar_msg("")
        EditCommand_PM.close(self)
        return
    
    def show(self):
        """
        Show the PM. Extends superclass method.
        @note: _update_UI_do_updates() gets called immediately after this and
               updates PM widgets with their correct values/settings. 
        """
        
        env.history.statusbar_msg("")
        EditCommand_PM.show(self)
        
        # NOTE: Think about moving this msg to _update_UI_do_updates() where
        # custom msgs can be created based on the current selection, etc.
        # Mark 2008-12-14
        msg = "Select <b>Insert Nanotube</b> to create a nanotube or "\
            "select an existing nantube to modify it."
        self.updateMessage(msg)
        return
    
    def _editNanotube(self):
        """
        Slot for the "Edit Properties" button. 
        """
        
        #if not self.command.hasValidStructure():
        #    return
        
        nanotubeSegment = self.win.assy.getSelectedNanotubeSegment()
        
        if nanotubeSegment:
            nanotubeSegment.edit()
        return
    
    def _addWhatsThisText( self ):
        """
        What's This text for widgets in the CNT Property Manager.  
        """
        pass
                
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the CNT Property Manager.  
        """
        pass
    
    def _addGroupBoxes( self ):
        """
        Add the Nanotube Property Manager group boxes.
        """        
        self._pmGroupBox1 = PM_GroupBox( self, title = "Nanotubes" )
        self._loadGroupBox1( self._pmGroupBox1 )
        return
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        load widgets in groupbox1
        """
        
        self.nanotubeListWidget = PM_SelectionListWidget(pmGroupBox,
                                                         self.win,
                                                         label = "",
                                                         heightByRows = 12)
        self.nanotubeListWidget.setObjectName('nanotubeListWidget')
        self.nanotubeListWidget.setTagInstruction('PICK_ITEM_IN_GLPANE')
        
        self.editNanotubePropertiesButton = PM_PushButton(pmGroupBox,
                                                          label = "",
                                                          text  = "Edit Properties..." )
        self.editNanotubePropertiesButton.setEnabled(False)
        return
    
    def updateNanotubeListWidget(self):   
        """
        Update the nanotube list widget. It shows all nanotubes in the part.
        """
        nanotubeSegmentList = getAllNanotubeSegmentsInPart(self.win.assy)
        
        if nanotubeSegmentList:
            self.nanotubeListWidget.insertItems(
                row = 0,
                items = nanotubeSegmentList)
        else:           
            self.nanotubeListWidget.clear()
        return
