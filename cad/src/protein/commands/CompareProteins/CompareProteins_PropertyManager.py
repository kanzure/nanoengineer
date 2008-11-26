# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
CompareProteins_PropertyManager.py

The CompareProteins_PropertyManager class provides a Property Manager 
for the B{Compare Proteins} command on the flyout toolbar in the 
Build > Protein mode. 

@author: Piotr
@version: $Id$ 
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

"""

import foundation.env as env

from command_support.Command_PropertyManager import Command_PropertyManager
from utilities.prefs_constants import workingDirectory_prefs_key
from utilities.constants import yellow

from PyQt4.Qt import SIGNAL
from PM.PM_PushButton   import PM_PushButton
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_Constants import PM_DONE_BUTTON
from PM.PM_Constants import PM_WHATS_THIS_BUTTON


_superclass = Command_PropertyManager
class CompareProteins_PropertyManager(Command_PropertyManager):
    """
    The ProteinDisplayStyle_PropertyManager class provides a Property Manager 
    for the B{Display Style} command on the flyout toolbar in the 
    Build > Protein mode. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Compare Proteins"
    pmName        =  title
    iconPath      =  "ui/actions/Edit/EditProteinDisplayStyle.png"

    
    def __init__( self, command ):
        """
        Constructor for the property manager.
        """

                     
        self.currentWorkingDirectory = env.prefs[workingDirectory_prefs_key]
        
        self.threshold = 10.0
        
        _superclass.__init__(self, command)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        msg = "Select two protein structures to compare."
        self.updateMessage(msg)

    def connect_or_disconnect_signals(self, isConnect = True):
        
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
        
        #change_connect(self.nextAAPushButton,
        #               SIGNAL("clicked()"),
        #               self._expandNextRotamer)
        
    #Protein Display methods         


    def show(self):
        """
        Shows the Property Manager. Extends superclass method. 
        """
        #@REVIEW: Why does it create sequence editor here? Also, is it
        #required to be done before the superclass.show call? --Ninad 2008-10-02
        self.sequenceEditor = self.win.createProteinSequenceEditorIfNeeded()
        self.sequenceEditor.hide()
        _superclass.show(self)
        
        self._updateProteinList()
        self.structure1ComboBox.clear()
        self.structure1ComboBox.addItems(self.protein_name_list)
        self.structure2ComboBox.clear()
        self.structure2ComboBox.addItems(self.protein_name_list)
        
   
    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self,
                                         title = "Compare")
        self._loadGroupBox1( self._pmGroupBox1 )
        
    def _addWhatsThisText( self ):
        """
        What's This text for widgets in this Property Manager.  
        """
        pass
    
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        pass
    

    def _updateProteinList(self):
        """
        """
        self.protein_chunk_list = []
        self.protein_name_list = []
        for mol in self.win.assy.molecules:
            if mol.isProteinChunk():
                self.protein_chunk_list.append(mol)
                self.protein_name_list.append(mol.name)
        
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        self._updateProteinList()
        
        self.structure1ComboBox = PM_ComboBox( pmGroupBox,
                                 label         =  "First structure:",
                                 choices       =  self.protein_name_list,
                                 setAsDefault  =  False)

        self.structure2ComboBox = PM_ComboBox( pmGroupBox,
                                 label         =  "Second structure:",
                                 choices       =  self.protein_name_list,
                                 setAsDefault  =  False)

        self.thresholdDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Threshold:",
                              value         =  self.threshold,
                              setAsDefault  =  True,
                              minimum       =  0.0,
                              maximum       =  360.0,
                              decimals      =  1,
                              singleStep    =  30.0,
                              suffix        = " deg",
                              spanWidth = False)

        self.win.connect(self.thresholdDoubleSpinBox,
                         SIGNAL("valueChanged(double)"),
                         self._thresholdChanged)
        
        self.comparePushButton  = \
            PM_PushButton( pmGroupBox,
                         text         =  "Compare",
                         setAsDefault  =  True)
        
        self.win.connect(self.comparePushButton,
                         SIGNAL("clicked()"),
                         self._compareProteins)
        
        self.hidePushButton  = \
            PM_PushButton( pmGroupBox,
                         text         =  "Hide differences",
                         setAsDefault  =  True)
        
        self.win.connect(self.hidePushButton,
                         SIGNAL("clicked()"),
                         self._hideDifferences)
        
    def _compareProteins(self):
        """
        """
        from utilities.constants import red, orange, green, cyan
        
        if len(self.protein_chunk_list) == 0 or \
           len(self.protein_chunk_list) == 0:
            return
        
        protein_1 = self.protein_chunk_list[self.structure1ComboBox.currentIndex()].protein
        protein_2 = self.protein_chunk_list[self.structure2ComboBox.currentIndex()].protein
        
        if protein_1 and \
           protein_2:
            aa_list_1 = protein_1.get_amino_acids()
            aa_list_2 = protein_2.get_amino_acids()
            protein_1.collapse_all_rotamers()
            protein_2.collapse_all_rotamers()
            if len(aa_list_1) == len(aa_list_2):
                for aa1, aa2 in zip (aa_list_1, aa_list_2):
                    aa1.color = None
                    aa2.color = None
                    #aa1.collapse()
                    #aa2.collapse()
                    if aa1.get_one_letter_code() != aa2.get_one_letter_code():
                        aa1.set_color(red)
                        aa1.expand()
                        aa2.set_color(yellow)
                        aa2.expand()
                    else:
                        max = 0.0
                        for chi in range(0, 3):
                            angle1 = aa1.get_chi_angle(chi)
                            angle2 = aa2.get_chi_angle(chi)
                            if angle1 and \
                               angle2:
                                if angle1 < 0.0:
                                    angle1 += 360.0
                                if angle2 < 0.0:
                                    angle2 += 360.0
                                diff = abs(angle1 - angle2)
                                if diff > max:
                                    max = diff
                        if max >= self.threshold:
                            # This be a parameter.
                            aa1.set_color(green)
                            aa1.expand()
                            aa2.set_color(cyan)
                            aa2.expand()
                        
                self.win.glpane.gl_update()
            else:
                env.history.redmsg("The lengths of compared proteins are not equal.")

    def _hideDifferences(self):
        """
        """
        if len(self.protein_chunk_list) == 0 or \
           len(self.protein_chunk_list) == 0:
            return
        
        protein_1 = self.protein_chunk_list[self.structure1ComboBox.currentIndex()].protein
        protein_2 = self.protein_chunk_list[self.structure2ComboBox.currentIndex()].protein
        
        if protein_1 and \
           protein_2:
            aa_list_1 = protein_1.get_amino_acids()
            aa_list_2 = protein_2.get_amino_acids()
            if len(aa_list_1) == len(aa_list_2):
                protein_1.collapse_all_rotamers()
                protein_2.collapse_all_rotamers()
                for aa1, aa2 in zip (aa_list_1, aa_list_2):
                    aa1.color = None
                    aa2.color = None
                    aa1.collapse()
                    aa2.collapse()

    def _thresholdChanged(self, value):
        self.threshold = value
        self._compareProteins()
        
