# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

TODO: as of 2008-01-18
See DnaSegment_EditCommand for details. 
"""
from PyQt4.Qt import SIGNAL
from PM.PM_GroupBox      import PM_GroupBox

from widgets.DebugMenuMixin import DebugMenuMixin
from command_support.EditCommand_PM import EditCommand_PM

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_Constants     import pmCancelButton
from PM.PM_Constants     import pmPreviewButton

from PM.PM_SpinBox import PM_SpinBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_LineEdit import PM_LineEdit
from dna.model.Dna_Constants import getNumberOfBasePairsFromDuplexLength, getDuplexLength

from geometry.VQT import V, vlen

class DnaSegment_PropertyManager( EditCommand_PM, DebugMenuMixin ):
    """
    The DnaSegmenta_PropertyManager class provides a Property Manager 
    for the DnaSegment_EditCommand. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Dna Segment Properties"
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
        
        self.endPoint1 = V(0, 0, 0)
        self.endPoint2 = V(0, 0, 0)
                
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
                                pmCancelButton | \
                                pmPreviewButton | \
                                pmWhatsThisButton)
    
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
         
                
        change_connect( self.numberOfBasePairsSpinBox,
                      SIGNAL("valueChanged(int)"),
                      self.numberOfBasesChanged )
        
        change_connect( self.basesPerTurnDoubleSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.basesPerTurnChanged )
        
        change_connect( self.duplexRiseDoubleSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.duplexRiseChanged )
    
    def show(self):
        """
        Show this property manager. Overrides EditCommand_PM.show()
        This method also retrives the name information from the 
        editCommand's structure for its name line edit field. 
        @see: DnaSegment_EditCommand.getStructureName()
        @see: self.close()
        """
        EditCommand_PM.show(self)
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
        EditCommand_PM.close(self)
        
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
                             duplexRise, \
                             endPoint1, \
                             endPoint2   = params 
        
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
        if endPoint1 is not None:
            self.endPoint1 = endPoint1
        if endPoint2 is not None:
            self.endPoint2 = endPoint2
        
    
        
    def getParameters(self):
        """
        """
        #See bug 2802 for details about the parameter 
        #'number_of_basePairs_from_struct'. Basically it is used to check
        #if the structure got modified (e.g. because of undo) 
        #The numberOfBases parameter obtained from the propMgr is given as a 
        #separate parameter for the reasons mentioned in bug 2802
        #-- Ninad 2008-04-12
        number_of_basePairs_from_struct = None
        if self.editCommand.hasValidStructure():
            number_of_basePairs_from_struct = self.editCommand.struct.getNumberOfBasePairs()
        numberOfBases = self.numberOfBasePairsSpinBox.value()
        dnaForm  = self._conformation
        dnaModel = self.dnaModel
        basesPerTurn = self.basesPerTurn
        duplexRise = self.duplexRise
              
        return (
            number_of_basePairs_from_struct,
            numberOfBases, 
            dnaForm,
            dnaModel,
            basesPerTurn,
            duplexRise,
            self.endPoint1, 
            self.endPoint2)
    
    def _update_widgets_in_PM_before_show(self):
        """
        This is called only when user is editing an existing structure. 
        Its different than self.update_widgets_in_pm_before_show. (that method 
        is called just before showing the property manager) 
        @see: DnaSegment_EditCommand.editStructure()
        
        """
        if self.editCommand is not None and self.editCommand.hasValidStructure():
        
            self.endPoint1, self.endPoint2 = self.editCommand.struct.getAxisEndPoints()
                           
            duplexLength = vlen(self.endPoint1 - self.endPoint2)
        
            numberOfBasePairs = getNumberOfBasePairsFromDuplexLength('B-DNA', 
                                                                 duplexLength) 
            
            self.numberOfBasePairsSpinBox.setValue(numberOfBasePairs) 
            #Set the legth of duplex field. Note that 
            #_update_widgets_in_PM_before_show is called in self.show, before
            #you connect the signals. So, for the 'first show' we will need to 
            #manually set the value of the duplex length in that field. 
            #But later, whan a different DnaSegment is clicked, (while still in 
            #DnaSegment_EditCommand, the propMgr will already be connected 
            #so the call below in that case is redundant (but harmless)
            self.numberOfBasesChanged(numberOfBasePairs)
    
    def numberOfBasesChanged( self, numberOfBases ):
        """
        Slot for the B{Number of Bases" spinbox.
        """
        # Update the Duplex Length lineEdit widget.
        text = str(getDuplexLength(self._conformation, numberOfBases)) \
             + " Angstroms"
        self.duplexLengthLineEdit.setText(text)
        return
    
    def basesPerTurnChanged( self, basesPerTurn ):
        """
        Slot for the B{Bases per turn} spinbox.
        """
        self.basesPerTurn = basesPerTurn
        
    
    def duplexRiseChanged( self, rise ):
        """
        Slot for the B{Rise} spinbox.
        """
        self.duplexRise = rise
        
                          
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
                         label         =  "Segment name:",
                         text          =  "",
                         setAsDefault  =  False)
                                                   
        # Strand Length (i.e. the number of bases)
        self.numberOfBasePairsSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Base pairs:", 
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


        # Duplex Length
        self.duplexLengthLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Duplex length: ",
                         text          =  "0.0 Angstroms",
                         setAsDefault  =  False)

        self.duplexLengthLineEdit.setDisabled(True)  
        
        
    
    def _addWhatsThisText(self):
        """
        Add what's this text. 
        """
        pass
    
    def _addToolTipText(self):
        """
        Add Tooltip text
        """
        pass
    
        
