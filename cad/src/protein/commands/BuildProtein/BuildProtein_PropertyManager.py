# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildProtein_PropertyManager.py

@author: Urmi
@version: $Id$: 
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

"""
from utilities import debug_flags
from utilities.debug import print_compact_stack

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QString

from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_PushButton    import PM_PushButton
from PM.PM_SelectionListWidget import PM_SelectionListWidget
from PM.PM_LineEdit import PM_LineEdit
from PM.PM_SpinBox import PM_SpinBox
from widgets.DebugMenuMixin import DebugMenuMixin
from command_support.EditCommand_PM import EditCommand_PM

from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON
from PM.PM_Colors        import pmReferencesListWidgetColor
from utilities.Comparison import same_vals

_superclass = EditCommand_PM
class BuildProtein_PropertyManager( EditCommand_PM, DebugMenuMixin ):
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

    title         =  "Build Protein"
    pmName        =  title
    #change this ico path later
    iconPath      =  "ui/actions/Tools/Build Structures/Peptide.png"

    def __init__( self, win, editCommand ):
        """
        Constructor for the Build DNA property manager.
        """
        
        #For model changed signal
        self.previousSelectionParams = None
         
        #Urmi 20080713: set the protein chunk name and its length
        #for the first available chunk and not the selected one, that's
        #not implemented as yet
        
        #self.showProteinParametersAndSequenceEditorForInit(win)
        
        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False           
        
        EditCommand_PM.__init__( self, 
                                    win,
                                    editCommand)


        DebugMenuMixin._init1( self )

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        
        
    def show(self):
        self.showProteinParametersAndSequenceEditor(self.win)
        EditCommand_PM.show(self)        
        
        return
    
    def close(self):
        self.sequenceEditor.hide() 
        EditCommand_PM.close(self)
        return
    
    
    
    def showProteinParametersAndSequenceEditor(self, win):
        part = win.assy.part
        from simulation.ROSETTA.rosetta_commandruns import checkIfProteinChunkInPart
        proteinExists, proteinChunk = checkIfProteinChunkInPart(part)
        print proteinExists
        if proteinExists:
            self._proteinChunkName = proteinChunk.protein.get_pdb_id() + proteinChunk.protein.get_chain_id()
            self._numberOfAA = len(proteinChunk.protein.get_sequence_string())
        else:
            self._proteinChunkName = ''
            self._numberOfAA = 0
            
        self.nameLineEdit.setText(self._proteinChunkName)
        self.numberOfAASpinBox.setValue(self._numberOfAA)
        if proteinExists:
            self.nameLineEdit.setEnabled(True)
        else:
            self.nameLineEdit.setEnabled(False)
            
        self.sequenceEditor = win.createProteinSequenceEditorIfNeeded() 
        #get the sequence for this protein chunk
        if proteinExists:
            sequence = proteinChunk.protein.get_sequence_string()
            self.sequenceEditor.setSequence(sequence)
            secStructure = proteinChunk.protein.get_secondary_structure_string()
            self.sequenceEditor.setSecondaryStructure(secStructure)
            self.sequenceEditor.show()    
        else:
            self.sequenceEditor.hide()   
            
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
            self.editCommand.flyoutToolbar.exitProteinAction.setEnabled(not bool_enable)
        
      
                      
    
    
  
    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """   
        
        self.win.toolsDone()
    
    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """
                  
        self.win.toolsCancel()
    
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

    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """
        """
        Add the DNA Property Manager group boxes.
        """        
                
        self._pmGroupBox1 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox1( self._pmGroupBox1 )
        
        pass
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 4.
        """
        
        self.nameLineEdit = PM_LineEdit( pmGroupBox,
                         label         =  "Protein chunk name:",
                         text          =  "",
                         setAsDefault  =  False)
        
        #Urmi 20080713: May be useful to set the minimum value to not zero
        self.numberOfAASpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Number of amino acids:", 
                        value         =  0,
                        setAsDefault  =  False,
                        minimum       =  0,
                        maximum       =  10000 )
        self.numberOfAASpinBox.setEnabled(False)