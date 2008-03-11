# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad, Mark
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

TODO: as of 2008-01-18
See CntSegment_EditCommand for details. 
"""
from PyQt4.Qt import SIGNAL
from PM.PM_GroupBox      import PM_GroupBox

from DebugMenuMixin import DebugMenuMixin
from command_support.EditCommand_PM import EditCommand_PM

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_Constants     import pmCancelButton
from PM.PM_Constants     import pmPreviewButton

from PM.PM_SpinBox import PM_SpinBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_LineEdit import PM_LineEdit
from cnt.model.Cnt_Constants import getNumberOfCellsFromCntLength, getCntLength

from geometry.VQT import V, vlen

class CntSegment_PropertyManager( EditCommand_PM, DebugMenuMixin ):
    """
    The CntSegmenta_PropertyManager class provides a Property Manager 
    for the CntSegment_EditCommand. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Cnt Segment Properties"
    pmName        =  title
    iconPath      =  "ui/actions/Tools/Build Structures/Nanotube.png"

    def __init__( self, win, editCommand ):
        """
        Constructor for the Cnt Segment Properties property manager.
        """
        
        #For model changed signal
        self.previousSelectionParams = None
        
        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False
        
        self.endPoint1 = V(0, 0, 0)
        self.endPoint2 = V(0, 0, 0)
                
        self._numberOfCells = 0 
        self._type = 'Carbon'
        self.cntRise = 2.00
        self.cellsPerTurn = 0
        
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
         
                
        change_connect( self.numberOfCellsSpinBox,
                      SIGNAL("valueChanged(int)"),
                      self.numberOfCellsChanged )
        
        change_connect( self.cntRiseDoubleSpinBox,
                      SIGNAL("valueChanged(double)"),
                      self.cntRiseChanged )
    
    def show(self):
        """
        Show this property manager. Overrides EditCommand_PM.show()
        This method also retrives the name information from the 
        editCommand's structure for its name line edit field. 
        @see: CntSegment_EditCommand.getStructureName()
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
        @see: CntSegment_EditCommand.setStructureName
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
        #Set the cnt rise and cells per turn spinbox values. 
        cntRise, cellsPerTurn = params 
        if cntRise:
            self.cntRiseDoubleSpinBox.setValue(cntRise)
        #if cellsPerTurn:
        #    self.cellsPerTurnDoubleSpinBox.setValue(cellsPerTurn)
        
        
    def getParameters(self):
        """
        """
        numberOfCells = self.numberOfCellsSpinBox.value()
        dnaForm  = 'B-DNA'
        cellsPerTurn = self.cellsPerTurn
        cntRise = self.cntRise
        dnaModel = 'PAM-3'
      
        return (numberOfCells, 
                dnaForm,
                dnaModel,
                cellsPerTurn,
                cntRise,
                self.endPoint1, 
                self.endPoint2)
    
    def _update_widgets_in_PM_before_show(self):
        """
        This is called only when user is editing an existing structure. 
        Its different than self.update_widgets_in_pm_before_show. (that method 
        is called just before showing the property manager) 
        @see: CntSegment_EditCommand.editStructure()
        
        """
        if self.editCommand is not None and self.editCommand.hasValidStructure():
        
            self.endPoint1, self.endPoint2 = self.editCommand.struct.getAxisEndPoints()
                           
            cntLength = vlen(self.endPoint1 - self.endPoint2)
        
            numberOfCells = getNumberOfCellsFromCntLength(cntLength) 
            
            self.numberOfCellsSpinBox.setValue(numberOfCells) 
            #Set the number of cells field. Note that 
            #_update_widgets_in_PM_before_show is called in self.show, before
            #you connect the signals. So, for the 'first show' we will need to 
            #manually set the value of the cnt length in that field. 
            #But later, whan a different CntSegment is clicked, (while still in 
            #CntSegment_EditCommand, the propMgr will already be connected 
            #so the call below in that case is redundant (but harmless)
            self.numberOfCellsChanged(numberOfCells)
    
    def numberOfCellsChanged( self, numberOfCells ):
        """
        Slot for the B{Number of Cells} spinbox.
        """
        # Update the Cnt Length lineEdit widget.
        text = str(getCntLength(self._type, numberOfCells)) \
             + " Angstroms"
        self.cntLengthLineEdit.setText(text)
        return
    
    def cellsPerTurnChanged( self, cellsPerTurn ):
        """
        Slot for the B{Cells per turn} spinbox.
        """
        self.cellsPerTurn = cellsPerTurn
        
    def cntRiseChanged( self, rise ):
        """
        Slot for the B{Rise} spinbox.
        """
        self.cntRise = rise
        
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
                                                   
        # Number of cells
        self.numberOfCellsSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Number of Cells:", 
                        value         =  self._numberOfCells,
                        setAsDefault  =  False,
                        minimum       =  0,
                        maximum       =  10000 )
        
        self.cntRiseDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Rise:",
                              value         =  self.cntRise,
                              setAsDefault  =  True,
                              minimum       =  2.0,
                              maximum       =  4.0,
                              decimals      =  3,
                              singleStep    =  0.01 )

        # Cnt Length
        self.cntLengthLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Length: ",
                         text          =  "0.0 Angstroms",
                         setAsDefault  =  False)

        self.cntLengthLineEdit.setDisabled(True)  
    
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
    
        