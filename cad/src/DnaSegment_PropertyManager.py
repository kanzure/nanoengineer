# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

TODO: as of 2008-01-18
See DnaSegment_EditCommand for details. 
"""

from PM.PM_GroupBox      import PM_GroupBox

from DebugMenuMixin import DebugMenuMixin
from EditCommand_PM import EditCommand_PM

from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_Constants     import pmCancelButton
from PM.PM_SpinBox import PM_SpinBox
from PM.PM_LineEdit import PM_LineEdit


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
        
        
        self._numberOfBases = 0       
        
        EditCommand_PM.__init__( self, 
                                    win,
                                    editCommand)


        DebugMenuMixin._init1( self )

        self.showTopRowButtons( pmDoneButton | \
                                pmCancelButton | \
                                pmWhatsThisButton)
        
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
    
        