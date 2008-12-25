# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildProtein_PropertyManager.py

@author: Urmi, Mark
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

Mark 20081212: Heavily rewritten, modeled after BuildDna_PropertyManager.py.

To do list:
- Add "Edit Properties" menu item to GA context menu when highlighting Peptide.
- Bug: Cannot edit a peptide loaded from an MMP file.
- Read FASTA file via sequence editor (or another way).
- Debug_pref for debug print statements.
- Deprecate set_current_protein_chunk_name() and get_current_protein_chunk_name.
  Use ops_select_Mixin's getSelectedProteinChunk() instead.
- Bug: Returning from Compare command unselects the two selected protein chunks.
  The PM list widget shows them as selected and the compare button is enabled,
  but they are not selected in the graphics area.
"""
import foundation.env as env
from PyQt4.Qt import SIGNAL
from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_SpinBox import PM_SpinBox
from PM.PM_PushButton import PM_PushButton
from PM.PM_SelectionListWidget import PM_SelectionListWidget
from command_support.EditCommand_PM import EditCommand_PM
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON
from utilities.Comparison import same_vals
from protein.model.Protein import getAllProteinChunksInPart

_superclass = EditCommand_PM
class BuildProtein_PropertyManager(EditCommand_PM):
    """
    The BuildProtein_PropertyManager class provides a Property Manager 
    for the B{Build Protein} command.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Build Protein"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/BuildProtein/BuildProtein.png"
    
    current_protein = "" # name of the single selected peptide. To be deprecated soon. --Mark 2008-12-14

    def __init__( self, command):
        """
        Constructor for the Build Protein property manager.
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
                                PM_CANCEL_BUTTON | \
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
        
        self.proteinListWidget.connect_or_disconnect_signals(isConnect)
        
        change_connect(self.editPeptidePropertiesButton, 
                       SIGNAL("clicked()"),
                       self._editPeptide)
        
        change_connect(self.compareProteinsButton, 
                       SIGNAL("clicked()"),
                       self._compareProteins)
        
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
        if selection_params_unchanged and structure_params_unchanged and command_stack_params_unchanged:
            #This second condition above fixes bug 2888
            print "Build Protein: _update_UI_do_updates(): DO NOTHING"
            return
        
        self._previousStructureParams = current_struct_params
        self._previousSelectionParams =  newSelectionParams         
        self._previousCommandStackParams  = current_command_stack_params
        
        ##if not selection_params_unchanged or not command_stack_params_unchanged and structure_params_unchanged: 
        if structure_params_unchanged: 
            #NOTE: We checked if either of the selection struct or command stack
            #parameters or both changed. (this was referred as '[CONDITION A]' 
            #above). So, this condition (structure_params_unchanged)also means 
            #either selection or command stack or both parameters were changed.    
            
            if not command_stack_params_unchanged:
                #update the protein list widget *before* updating the selection if 
                #the command stack changed. This ensures that the selection box
                #appears around the list widget items that are selected.
                self.updateProteinListWidget()
                
            selectedProteins = newSelectionParams    
            
            self.proteinListWidget.updateSelection(selectedProteins) 
            
            # Enable/disable "Edit Sequence" button.
            if len(selectedProteins) == 1:
                self.editPeptidePropertiesButton.setEnabled(True)
            else:
                self.editPeptidePropertiesButton.setEnabled(False)
            
                # Enable/disable "Compare Proteins" button.
            if len(selectedProteins) == 2:
                self.compareProteinsButton.setEnabled(True)
            else:
                self.compareProteinsButton.setEnabled(False)
                
            return
        
        self.updateProteinListWidget()
        return
    
    def _currentCommandStackParams(self):
        """
        The return value is supposed to be used by BUILD_PROTEIN command PM ONLY
        and NOT by any subclasses.         
        
        Returns a tuple containing current command stack change indicator and 
        the name of the command 'BUILD_PROTEIN'. These 
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
        #Append 'BUILD_PROTEIN to the tuple to be returned. This is just to remind 
        #us that this method is meant for BUILD_PROTEIN command PM only. (and not 
        #by any subclasses) Should we assert this? I think it will slow things 
        #down so this comment is enough -- Ninad 2008-09-30
        return (commandStackCounter, 'BUILD_PROTEIN')
                      
    def _currentSelectionParams(self):
        """
        Returns a tuple containing current selection parameters. These 
        parameters are then used to decide whether updating widgets
        in this property manager is needed when L{self.model_changed}
        method is called.
        
        @return: A tuple that contains total number of selected peptides.
        @rtype:  tuple
        
        @NOTE: This method may be renamed in future. 
        It's possible that there are other groupboxes in the PM that need to be 
        updated when something changes in the glpane.        
        """
         
        selectedProteins = []
        if self.command is not None: # and self.command.hasValidStructure():
            selectedProteins = self.win.assy.getSelectedProteinChunks()          
        
        #print "_currentSelectionParams(): Number of selected proteins:", len(selectedProteins)
        return (selectedProteins)
    
    def _currentStructureParams(self):
        """
        Return current structure parameters of interest to self.model_changed. 
        Right now it only returns the number of peptides within the structure
        (or None). This is a good enough check (and no need to compare 
        each and every peptide within the structure with a previously stored 
        set of strands).
        """
        #Can it happen that the total number of peptides remains the same even 
        #after some alterations to the peptides? Unlikely. (Example: a single
        #(future) Break peptide operation will increase the number of peptides
        #by one. Or Join peptides decrease it by 1)
        params = None
        
        if self.command: # and self.command.hasValidStructure():
            proteinList = []
            proteinList = getAllProteinChunksInPart(self.win.assy)
            params = len(proteinList)
        
        print "_currentStructureParams(): params:", params
        return params
    
    def close(self):
        """
        Closes the Property Manager. Overrides EditCommand_PM.close()
        """
        #Clear tags, if any, due to the selection in the self.strandListWidget.
        #self.proteinListWidget.clear()
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
        msg = "Select <b>Insert Peptide</b> to create a peptide chain or "\
            "select another modeling tool to modify an existing protein."
        self.updateMessage(msg)
        return
    
    def _editPeptide(self):  
        """
        Slot for the "Edit Properties" button. 
        """
        
        #if not self.command.hasValidStructure():
        #    return
        
        proteinChunk = self.getSelectedProteinChunk()
        
        if proteinChunk:
            proteinChunk.protein.edit(self.win)
        return
    
    def _compareProteins(self):
        """
        Slot for the "Compare Proteins" button.
        """
        self.win.commandSequencer.userEnterCommand('COMPARE_PROTEINS')
        return
    
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

    def _addGroupBoxes(self):
        """
        Add the Build Protein Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox(self, title = "Peptides")
        self._loadGroupBox1(self._pmGroupBox1)
        return
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in groupbox1.
        """
        
        self.proteinListWidget = PM_SelectionListWidget(pmGroupBox,
                                                       self.win,
                                                       label = "",
                                                       heightByRows = 6 )
        self.proteinListWidget.setObjectName('Peptide_list_widget')
        self.proteinListWidget.setTagInstruction('PICK_ITEM_IN_GLPANE')
        
        self.editPeptidePropertiesButton = PM_PushButton(pmGroupBox,
                                                         label = "",
                                                         text  = "Edit Properties..." )
        self.editPeptidePropertiesButton.setEnabled(False)
        
        self.compareProteinsButton = PM_PushButton(pmGroupBox,
                                                         label = "",
                                                         text  = "Compare Proteins..." )
        self.compareProteinsButton.setEnabled(False)
        
        return
    
    def updateProteinListWidget(self):   
        """
        Update the peptide list widget. It shows all peptides in the part.
        """
        proteinChunkList = getAllProteinChunksInPart(self.win.assy)
        
        if proteinChunkList:
            self.proteinListWidget.insertItems(
                row = 0,
                items = proteinChunkList)
        else:           
            self.proteinListWidget.clear()
        return
    
    def set_current_protein_chunk_name(self, name):
        """
        Sets the name of the currently selected peptide. Set it to an
        empty string if there is no currently selected peptide.
        
        @return: the name of the currently selected peptide.
        @rtype: string
        
        @note: this is used widely by other commands. It will be renamed to 
               setCurrentPeptideName() soon.
        """
        self.current_protein = name
        return
        
    
    def get_current_protein_chunk_name(self):
        """
        Returns the name of the currently selected peptide. Returns an
        empty string if there is no currently selected peptide.
        
        @return: the name of the currently selected peptide.
        @rtype: string
        
        @note: this is used widely by other commands. It will be renamed to 
               getCurrentPeptideName() soon.
        """
        return self.current_protein
    
    def getSelectedProteinChunk(self):
        """
        Returns only the currently selected protein chunk, if any.
        @return: the currently selected protein chunk or None if no peptide 
                 chunks are selected. Also returns None if more than one
                 peptide chunk is select.
        @rtype: L{Chunk}
        @note: use L{getSelectedProteinChunks()} to get the list of all 
               selected proteins.
        @attention: A method of the same name is in the ops_select_Mixin class.
                    It is my intention to use that method and deprecate this one.
                    I cannot do that until I remove all uses of 
                    get_current_protein_chunk_name() and 
                    set_current_protein_chunk_name() -- Mark. 2008-12-13
        """
        selectedPeptideList = self.win.assy.getSelectedProteinChunks()
        if len(selectedPeptideList) == 1:
            self.set_current_protein_chunk_name(selectedPeptideList[0].name)
            return selectedPeptideList[0]
        else:
            self.set_current_protein_chunk_name("")
            return None
        return
    
    