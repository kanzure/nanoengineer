# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ModelAndSimulateProtein_PropertyManager.py

@author: Urmi
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""
import foundation.env as env
from PyQt4.Qt import SIGNAL
from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_SpinBox import PM_SpinBox
from PM.PM_PushButton import PM_PushButton
from command_support.EditCommand_PM import EditCommand_PM
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON
from simulation.ROSETTA.rosetta_commandruns import checkIfProteinChunkInPart

_superclass = EditCommand_PM
class ModelAndSimulateProtein_PropertyManager(EditCommand_PM):
    """
    The ModelAndSimulate_PropertyManager class provides a Property Manager 
    for the B{Build > Protein } command.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Model and Simulate Protein"
    pmName        =  title
    #change this ico path later
    iconPath      =  "ui/actions/Tools/Build Structures/Peptide.png"

    def __init__( self, command):
        """
        Constructor for the Build DNA property manager.
        """
        
        self.current_protein = ""
        self.sequenceEditor = command.win.createProteinSequenceEditorIfNeeded() 
        
        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False           
        
        EditCommand_PM.__init__( self, command)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        
    def _updateProteinListForShow(self):
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
                j = self.structureComboBox.findText(name)
                self.structureComboBox.removeItem(j)
        
        for mol in self.win.assy.molecules:
            #if molecules does not already exist in combo box list, need to add 
            #them
            if mol.isProteinChunk(): 
                try:
                    self.protein_name_list.index(mol.name)
                except ValueError:    
                    self.protein_chunk_list.append(mol)
                    self.protein_name_list.append(mol.name)
                    self.structureComboBox.addItem(mol.name)
        return
        
    def show(self):
        """
        Overrides superclass show method
        """
        env.history.statusbar_msg("")
        self._updateProteinListForShow()
        self._showProteinParametersAndSequenceEditor()
        EditCommand_PM.show(self)  
        self.updateMessage()
        return
    
    def close(self):
        """
        Overrides superclass close method
        """
        self.sequenceEditor.hide() 
        env.history.statusbar_msg("")
        EditCommand_PM.close(self)
        return
    
    def _updateProteinList(self):
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
    
    
    def _showProteinParametersAndSequenceEditor(self):
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
                index = self.structureComboBox.findText(self.current_protein)
                index1 = self.protein_name_list.index(self.current_protein)
            except ValueError:
                index = 0
                index1 = 0
                self.set_current_protein_chunk_name(self.protein_name_list[index1])
                
            self.structureComboBox.setCurrentIndex(index)
            proteinChunk = self.protein_chunk_list[index1]            
            self._numberOfAA = len(proteinChunk.protein.get_sequence_string())
        else:  
            #remove all items from the combo box
            count = self.structureComboBox.count()
            for i in range(count):
                self.structureComboBox.removeItem(0)
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
        change_connect(self.structureComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                       self._updateProteinParameters)
        change_connect(self.editPropertiesPushButton, 
                       SIGNAL("clicked()"),
                       self._showSeqEditor)
        
    def _showSeqEditor(self):
        """
        Show sequence editor
        """
        if self.editPropertiesPushButton.isEnabled():
            self.sequenceEditor.show()
        return
        
    def _updateProteinParameters(self, index):
        """
        Update number of amino acids and sequence editor, as well as set the
        current protein pdb id which will be used in the child commands and for
        rosetta simulation from inside the build protein mode.
        @param index: index of the protein combo box
        @type index: int
        """
        for mol in self.protein_chunk_list:
            if  mol.name == self.structureComboBox.currentText():
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
        return
    
    def set_current_protein_chunk_name(self, name):
        """
        Sets the current protein name
        @param name: pdb id of the protein currently selected in the combo box
        @type name: str
        """
        self.current_protein = name
        return
        
    
    def get_current_protein_chunk_name(self):
        """
        gets the current protein name
        @return: pdb id of the protein currently selected in the combo box
        """
        return self.current_protein
        
    
    def enable_or_disable_gui_actions(self, bool_enable = False):
        """
        Enable or disable some gui actions when this property manager is 
        opened or closed, depending on the bool_enable. 
        @param bool_enable: enables/disables some gui action
        @type bool_enable: bool
        
        """
        #if hasattr(self.command, 'flyoutToolbar') and \
           #self.command.flyoutToolbar:            
            #self.command.flyoutToolbar.exitProteinAction.setEnabled(not bool_enable)
    
        
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
        Add the DNA Property Manager group boxes.
        """  
        self._pmGroupBox1 = PM_GroupBox(self, title = "Parameters")
        self._loadGroupBox1(self._pmGroupBox1)
        return
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 1.
        @param pmGroupBox: group box that contains protein name combo box and 
                        number of amino acids spin box
        @see: L{PM_GroupBox}                
        """
        self._updateProteinList()
        if len(self.protein_name_list) >= 1:
            self.set_current_protein_chunk_name(self.protein_name_list[0]) 
        self.structureComboBox = PM_ComboBox( pmGroupBox,
                                 label         =  "Name:",
                                 choices       =  self.protein_name_list,
                                 setAsDefault  =  False)
        
        #Urmi 20080713: May be useful to set the minimum value to not zero
        #Now it does not matter, since its disabled. But zero as the minimum 
        #value in a spinbox does not work otherwise. 
        self.numberOfAASpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Amino Acids:", 
                        value         =  0,
                        setAsDefault  =  False,
                        minimum       =  0,
                        maximum       =  10000 )
        #for now we do not allow changing number of residues
        self.numberOfAASpinBox.setEnabled(False)
        self.editPropertiesPushButton = PM_PushButton( pmGroupBox,
            text       =  "Edit Sequence",
            setAsDefault  =  True
            )
        return
    
