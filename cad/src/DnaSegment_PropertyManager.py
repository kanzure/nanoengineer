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

from DebugMenuMixin import DebugMenuMixin
from EditCommand_PM import EditCommand_PM

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_Constants     import pmCancelButton
from PM.PM_Constants     import pmPreviewButton

from PM.PM_SpinBox import PM_SpinBox
from PM.PM_LineEdit import PM_LineEdit
from Dna_Constants import getNumberOfBasePairsFromDuplexLength, getDuplexLength

from VQT import V, vlen

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
        

    def getParameters(self):
        """
        """
        numberOfBases = self.numberOfBasePairsSpinBox.value()
        dnaForm  = 'B-DNA'
        basesPerTurn = 10        
        dnaModel = 'PAM-3'
      
        return (numberOfBases, 
                dnaForm,
                dnaModel,
                basesPerTurn,
                self.endPoint1, 
                self.endPoint2)
    
    def _update_widgets_in_PM_before_show(self):
        """
        This is called only when user is editing an existing structure. 
        Its different than self.update_widgets_in_pm_before_show. (that method 
        is called just before showing the property manager) 
        @see: DnaSegment_EditCommand.editStructure()
        
        """
        if self.struct:
        
            self.endPoint1, self.endPoint2 = self.struct.getAxisEndPoints()
                           
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

                                            
        # Strand Length (i.e. the number of bases)
        self.numberOfBasePairsSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Base Pairs :", 
                        value         =  self._numberOfBases,
                        setAsDefault  =  False,
                        minimum       =  0,
                        maximum       =  10000 )


        # Duplex Length
        self.duplexLengthLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Duplex Length: ",
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
    
        