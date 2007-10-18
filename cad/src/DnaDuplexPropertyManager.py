# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaDuplexPropertyManager.py

$Id:$

@author: Mark Sims
@copyright: Copyright (c) 2007 Nanorex, Inc.  All rights reserved.

Mark 2007-10-18: 
- Created. Major rewrite of DnaGeneratorPropertyManager.py.
"""

__author__ = "Mark"

import env

from Dna_Constants import getDuplexRise, getDuplexLength
from Dna_Constants import getComplementSequence
from Dna_Constants import getReverseSequence
from Dna_Constants import replaceUnrecognized

from utilities.Log import redmsg, greenmsg, orangemsg

from icon_utilities import geticon, getpixmap

from PyQt4.Qt import SIGNAL

from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_LineEdit      import PM_LineEdit

from PM.PM_Dialog import PM_Dialog
from DebugMenuMixin import DebugMenuMixin

class DnaDuplexPropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The DnaDuplexPropertyManager class provides a Property Manager 
    for the B{Build > DNA > Duplex} command.
    
    @ivar title: The title that appears in the property manager header.
    @type title: str
    
    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str
    
    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """
    
    title         =  "DNA"
    pmName        =  title
    iconPath      =  "ui/actions/Tools/Build Structures/DNA.png"
    
    _conformation  = "B-DNA"
    _numberOfBases = 0
    _basesPerTurn  = 10.0
    _duplexRise    = getDuplexRise(_conformation)
    _duplexLength  = getDuplexLength(_conformation, _numberOfBases)

    def __init__( self ):
        """
        Constructor for the DNA Duplex property manager.
        """
        PM_Dialog.__init__( self, self.pmName, self.iconPath, self.title )
        DebugMenuMixin._init1( self )

        self._addGroupBoxes()
        self._addWhatsThisText()
        
        msg = "Edit the DNA parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert it into \
        the model."
        
        # This causes the "Message" box to be displayed as well.
        # setAsDefault=True causes this message to be reset whenever
        # this PM is (re)displayed via show(). Mark 2007-06-01.
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  True )
    
    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox1( self._pmGroupBox1 )
        
        self._pmGroupBox2 = PM_GroupBox( self, title = "Endpoints" )
        self._loadGroupBox2( self._pmGroupBox2 )
        
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 1.
        """
        
        self.conformationComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Conformation :", 
                         choices       =  ["B-DNA"],
                         setAsDefault  =  True)
        
        self.connect( self.conformationComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self.conformationComboBoxChanged )
        
        # Strand Length (i.e. the number of bases)
        self.numberOfBasesSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Number of bases :", 
                        value         =  self._numberOfBases,
                        setAsDefault  =  False,
                        minimum       =  0,
                        maximum       =  10000 )
        
        self.connect( self.numberOfBasesSpinBox,
                      SIGNAL("valueChanged(int)"),
                      self.numberOfBasesChanged )
        
        self.basesPerTurnDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Bases Per Turn :",
                              value         =  self._basesPerTurn,
                              setAsDefault  =  True,
                              minimum       =  8.0,
                              maximum       =  20.0,
                              decimals      =  2,
                              singleStep    =  0.1 )
        
        # Duplex Length
        self.duplexLengthLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Duplex Length: ",
                         text          =  "0.0 Angstroms",
                         setAsDefault  =  False)
        
        self.duplexLengthLineEdit.setDisabled(True)

    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in group box 3.
        """
        
        self._endPoint1GroupBox = PM_GroupBox( pmGroupBox, title = "Endpoint1" )
        self._endPoint2GroupBox = PM_GroupBox( pmGroupBox, title = "Endpoint2" )
        
        # Point 1
        self.x1SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint1GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/X_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
        self.y1SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint1GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Y_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
        self.z1SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint1GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Z_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
        # Point 2
        self.x2SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint2GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/X_Coordinate.png",
                              value         =  10.0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
        self.y2SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint2GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Y_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
        self.z2SpinBox  =  \
            PM_DoubleSpinBox( self._endPoint2GroupBox,
                              label         =  \
                              "ui/actions/Properties Manager/Z_Coordinate.png",
                              value         =  0,
                              setAsDefault  =  True,
                              minimum       =  -100.0,
                              maximum       =   100.0,
                              decimals      =  3,
                              suffix        =  ' Angstroms')
        
    def _addWhatsThisText( self ):
        """
        What's This text for some of the widgets in the 
        DNA Property Manager.  
        
        @note: Many PM widgets are still missing their "What's This" text.
        """
        
        self.conformationComboBox.setWhatsThis("""<b>Conformation</b>
        <p>DNA exists in several possible conformations, with A-DNA, B-DNA,
        and Z-DNA being the most common. 
        <br>
        Only B-DNA is currently supported in NanoEngineer-1.</p>""")
        
    def conformationComboBoxChanged( self, inIndex ):
        """
        Slot for the Conformation combobox. It is called whenever the
        Conformation choice is changed.
        
        @param inIndex: The new index.
        @type  inIndex: int
        """
        conformation  =  self.conformationComboBox.currentText()
        
        if conformation == "B-DNA":
            self.basesPerTurnDoubleSpinBox.setValue("10.0")
            
        elif conformation == "Z-DNA":
            self.basesPerTurnDoubleSpinBox.setValue("12.0")
        
        else:
            msg = redmsg("conformationComboBoxChanged(): \
            Error - unknown DNA conformation. Index = "+ inIndex)
            env.history.message(msg)

        self.duplexLengthSpinBox.setSingleStep(getDuplexRise(conformation))

    def numberOfBasesChanged( self, numberOfBases ):
        """
        Slot for the B{Number of Bases" spinbox.
        """
        # Update the Duplex Length lineEdit widget.
        text = str(getDuplexLength(self._conformation, numberOfBases)) \
                   + " Angstroms"
        self.duplexLengthLineEdit.setText(text)
        return
