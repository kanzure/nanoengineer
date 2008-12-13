# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildProtein_PropertyManager.py

@author: Urmi, Mark
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

Mark 20081212: Heavily rewritten, modeled after BuildDna_PropertyManager.py.

To do list:
- Include name and length of the current Peptide in the title of the Sequence Editor.
- Make sure PM and SeqEditor are updated correctly after selecting/editing 
  a peptide via the model tree.
- Add "Edit Properties" menu item to GA context menu when highlighting Peptide.
- Bug: Cannot edit a peptide loaded from an MMP file.
- Create a new PM for "Peptide Properties".
- Rename MODEL_AND_SIMULATE_PROTEIN to BUILD_PROTEIN (if it is safe).
- FASTA file support in sequence editor.
- Debug_pref for debug print statements.
- Special peptide icons for MT and PM list widget.
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
    
    current_protein = "" # name of the single selected peptide.

    def __init__( self, command):
        """
        Constructor for the Build Protein property manager.
        """
        
        self.sequenceEditor = command.win.createProteinSequenceEditorIfNeeded() 
        
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
        
        self.peptideListWidget.connect_or_disconnect_signals(isConnect)
        
        change_connect(self.editPeptidePropertiesButton, 
                       SIGNAL("clicked()"),
                       self._editPeptide)
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
            print "_update_UI_do_updates(): RETURNING 1"
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
                #update the peptide list widget *before* updating the selection if 
                #the command stack changed. This ensures that the selection box
                #appears around the list widget items that are selected.
                self.updatePeptideListWidget()
                
            selectedProteins = newSelectionParams    
            
            self.peptideListWidget.updateSelection(selectedProteins) 
            
            if len(selectedProteins) == 1:
                self.set_current_protein_chunk_name(selectedProteins[0].name)
                print "current_protein=", self.get_current_protein_chunk_name()
                self.editPeptidePropertiesButton.setEnabled(True)
            else:
                self.set_current_protein_chunk_name("")
                self.editPeptidePropertiesButton.setEnabled(False)
                self.sequenceEditor.hide()
                
            return
        
        self.updatePeptideListWidget()
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
         
        selectedPeptides = []
        if self.command is not None: # and self.command.hasValidStructure():
            selectedPeptides = self.win.assy.getSelectedProteinChunks()          
        
        print "_currentSelectionParams(): Number of selected peptides:", len(selectedPeptides)
        return (selectedPeptides)
    
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
            peptideList = []
            peptideList = self.getPeptideChunks()
            params = len(peptideList)
        
        print "_currentStructureParams(): params:", params
        return params
    
    def close(self):
        """
        Closes the Property Manager. Overrides EditCommand_PM.close()
        """
        #Clear tags, if any, due to the selection in the self.strandListWidget.
        self.peptideListWidget.clear()
        self.sequenceEditor.hide()
        env.history.statusbar_msg("")
        EditCommand_PM.close(self)
        return
    
    def show(self):
        """
        Show this PM. It also shows the Sequence Editor widget and hides 
        the history widget.
        """
        
        env.history.statusbar_msg("")
        self._showPeptideSequenceEditor()
        
        EditCommand_PM.show(self)
        
        msg = "Select <b>Insert Peptide</b> to create a peptide chain or "\
            "select another modeling tool to modify an existing protein."
        self.updateMessage(msg)
        return
    
    def _editPeptide(self):  
        """
        Opens the sequence editor for the selected peptide.
        """
        
        selectedPeptideList = self.win.assy.getSelectedProteinChunks()
        
        if len(selectedPeptideList) == 1:     
            peptideChunk = selectedPeptideList[0]
            sequence = peptideChunk.protein.get_sequence_string()
            self.sequenceEditor.setSequence(sequence)
            secStructure = peptideChunk.protein.get_secondary_structure_string()
            self.sequenceEditor.setSecondaryStructure(secStructure)
            self.sequenceEditor.setRuler(len(secStructure)) 
            self.sequenceEditor.show()
        return
    
    # getPeptideChunks() should eventually be moved to assy or some other class.
    # This should wait until we have a data model implemented for 
    # peptides/proteins.
    # Ask Bruce. Mark 2008-12-12
    def getPeptideChunks(self):
        """
        Returns a list of all the peptides in the current assy.
        """
        peptideList = []
        for mol in self.win.assy.molecules:
            if mol.isProteinChunk():
                peptideList.append(mol)
        return peptideList
    
    def _showPeptideSequenceEditor(self):
        """
        Show/hide sequence editor. It is only displayed if there is
        a single peptide selected. Otherwise it is hidden.
        """
        if self.get_current_protein_chunk_name():
            self.sequenceEditor.show()
        else:
            self.sequenceEditor.hide()
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
        
        self.peptideListWidget = PM_SelectionListWidget(pmGroupBox,
                                                       self.win,
                                                       label = "",
                                                       heightByRows = 6 )
        self.peptideListWidget.setObjectName('Peptide_list_widget')
        self.peptideListWidget.setTagInstruction('PICK_ITEM_IN_GLPANE')
        
        self.editPeptidePropertiesButton = PM_PushButton(pmGroupBox,
                                                         label = "",
                                                         text  = "Edit Sequence" )
        self.editPeptidePropertiesButton.setEnabled(False)
        return
    
    def updatePeptideListWidget(self):   
        """
        Update the peptide list widget. It shows all peptides in the part.
        """
        peptideChunkList = self.getPeptideChunks()
        
        if peptideChunkList:
            self.peptideListWidget.insertItems(
                row = 0,
                items = peptideChunkList)
        else:           
            self.peptideListWidget.clear()
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
    
    
    # --------------------------------------------------------------------
    # Deprecated methods to keep until we're certain this is working.
    # --Mark 2008-12-12.
    
    def _updateProteinParameters_DEPRECATED(self, index):
        """
        Update number of amino acids and sequence editor, as well as set the
        current protein pdb id which will be used in the child commands and for
        rosetta simulation from inside the build protein mode.
        @param index: index of the protein combo box
        @type index: int
        """
        for mol in self.protein_chunk_list:
            if  mol.name == self.peptideListComboBox.currentText():
                self._numberOfAA = len(mol.protein.get_sequence_string())
                self.numberOfAASpinBox.setValue(self._numberOfAA)
                sequence = mol.protein.get_sequence_string()
                self.sequenceEditor.setSequence(sequence)
                secStructure = mol.protein.get_secondary_structure_string()
                self.sequenceEditor.setSecondaryStructure(secStructure)
                self.sequenceEditor.setRuler(len(secStructure))
                break
        self.set_current_protein_chunk_name(mol.name) 
        env.history.statusbar_msg("")
        
        self._editPeptideSequence() #@@@
        
        return
    
    def _updateProteinList_DEPRECATED(self):
        """
        Update the list of proteins so that the protein name combo box in this 
        PM can be populated.
        """
        self.protein_chunk_list = []
        self.protein_name_list = []
        for mol in self.win.assy.molecules:
            if mol.isProteinChunk():
                self.protein_chunk_list.append(mol)
                self.protein_name_list.append(mol.name)
        return
    
    
    def _showProteinParametersAndSequenceEditor_DEPRECATED(self):
        """
        Show/ Hide protein parameters and sequence editor based on if there's
        any protein in NE-1 part.
        """
        part = self.win.assy.part  
        proteinExists, proteinChunk = checkIfProteinChunkInPart(part)
        if proteinExists:
            #check to see if current_protein is still in part, otherwise set 
            # this to first available protein
            try:
                index = self.peptideListComboBox.findText(self.current_protein)
                index1 = self.protein_name_list.index(self.current_protein)
            except ValueError:
                index = 0
                index1 = 0
                self.set_current_protein_chunk_name(self.protein_name_list[index1])
                
            self.peptideListComboBox.setCurrentIndex(index)
            proteinChunk = self.protein_chunk_list[index1]            
            self._numberOfAA = len(proteinChunk.protein.get_sequence_string())
        else:  
            #remove all items from the combo box
            count = self.peptideListComboBox.count()
            for i in range(count):
                self.peptideListComboBox.removeItem(0)
            self._numberOfAA = 0
            self.set_current_protein_chunk_name("")
        self.numberOfAASpinBox.setValue(self._numberOfAA)
        
        
        #get the sequence for this protein chunk
        if proteinExists:
            sequence = proteinChunk.protein.get_sequence_string()
            self.sequenceEditor.setSequence(sequence)
            secStructure = proteinChunk.protein.get_secondary_structure_string()
            self.sequenceEditor.setSecondaryStructure(secStructure)
            self.sequenceEditor.setRuler(len(secStructure)) 
            self.editPropertiesPushButton.setEnabled(True)
        else:
            self.editPropertiesPushButton.setEnabled(False)
        self.sequenceEditor.hide()  
        return
    
    def _updateProteinListForShow_DEPRECATED(self):
        """
        Update the list of proteins in the combo box in the PM.
        """
        #first remove from combo box all the proteins that do not exist in NE-1
        #part anymore
        currentProteinNameList = []
        for mol in self.win.assy.molecules:
            currentProteinNameList.append(mol.name)
         
        for name in self.protein_name_list:   
            try:
                index = currentProteinNameList.index(name) 
            except ValueError:    
                #protein does not exist any more, need to remove it
                i = self.protein_name_list.index(name)
                self.protein_chunk_list.pop(i)
                self.protein_name_list.pop(i)
                j = self.peptideListComboBox.findText(name)
                self.peptideListComboBox.removeItem(j)
        
        for mol in self.win.assy.molecules:
            #if molecules does not already exist in combo box list, need to add 
            #them
            if mol.isProteinChunk(): 
                try:
                    self.protein_name_list.index(mol.name)
                except ValueError:    
                    self.protein_chunk_list.append(mol)
                    self.protein_name_list.append(mol.name)
                    self.peptideListComboBox.addItem(mol.name)
        return
    