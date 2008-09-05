# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

This is a Property Manager dialog of the Peptide Generator.

@author: Piotr, Urmi
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:

Piotr 2008-01-11: Implemented Peptide Generator dialog using PropMgrBaseClass 
                  (just copied most stuff from NanotubeGeneratorPropertyManager).

Piotr 2008-03-02: Re-written the Property Manager dialogs to allow it working in 
                  the interactive mode.

Piotr 080407: Fixed minor bugs in sequence text editor window.

Urmi 20080731: Property Manager updated to support drawing proteins by
               clicking on two point

"""

import math

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt

from command_support.EditCommand_PM import EditCommand_PM

from PM.PM_GroupBox       import PM_GroupBox
from PM.PM_CheckBox       import PM_CheckBox
from PM.PM_ComboBox       import PM_ComboBox
from PM.PM_DoubleSpinBox  import PM_DoubleSpinBox
from PM.PM_SpinBox        import PM_SpinBox
from PM.PM_PushButton     import PM_PushButton
from PM.PM_ToolButtonGrid import PM_ToolButtonGrid
from PM.PM_TextEdit       import PM_TextEdit

from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON
from PM.PM_Constants     import PM_PREVIEW_BUTTON

from utilities.debug import print_compact_traceback

from utilities.Log import orangemsg, greenmsg, redmsg
import foundation.env as env

from protein.model.Residue import Residue
from protein.model.Residue import SS_HELIX, SS_COIL, SS_STRAND

# list of button descriptors for PM_ToolButtonGrid

AA_BUTTON_LIST = [
    ( "QToolButton", 0,  "Ala", "", "Alanine",       "A", 0, 0   ),
    ( "QToolButton", 1,  "Arg", "", "Arginine",      "R", 1, 0   ),
    ( "QToolButton", 2,  "Asn", "", "Asparagine",    "N", 2, 0   ),
    ( "QToolButton", 3,  "Asp", "", "Aspartic Acid", "D", 3, 0   ),
    ( "QToolButton", 4,  "Cys", "", "Cysteine",      "C", 4, 0   ),
    ( "QToolButton", 5,  "Glu", "", "Glutamic Acid", "E", 0, 1   ),
    ( "QToolButton", 6,  "Gln", "", "Glutamine",     "Q", 1, 1   ),
    ( "QToolButton", 7,  "Gly", "", "Glycine",       "G", 2, 1   ),
    ( "QToolButton", 8,  "His", "", "Histidine",     "H", 3, 1   ),
    ( "QToolButton", 9,  "Ile", "", "Isoleucine",    "I", 4, 1   ),
    ( "QToolButton", 10, "Leu", "", "Leucine",       "L", 0, 2   ),
    ( "QToolButton", 11, "Lys", "", "Lysine",        "K", 1, 2   ),
    ( "QToolButton", 12, "Met", "", "Methionine",    "M", 2, 2   ),
    ( "QToolButton", 13, "Phe", "", "Phenylalanine", "F", 3, 2   ),
    ( "QToolButton", 14, "Pro", "", "Proline",       "P", 4, 2   ),
    ( "QToolButton", 15, "Ser", "", "Serine",        "S", 0, 3   ),
    ( "QToolButton", 16, "Thr", "", "Threonine",     "T", 1, 3   ),
    ( "QToolButton", 17, "Trp", "", "Tryptophan" ,   "W", 2, 3   ),
    ( "QToolButton", 18, "Tyr", "", "Tyrosine",      "Y", 3, 3   ),
    ( "QToolButton", 19, "Val", "", "Valine",        "V", 4, 3   )
]
_superclass = EditCommand_PM
class PeptideGeneratorPropertyManager(EditCommand_PM):
    """
    The PeptideGeneratorPropertyManager class provides a Property Manager 
    for the "Build > Peptide" command.
    """
    # The title that appears in the property manager header.
    title = "Peptide Generator"
    # The name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    pmName = title
    # The relative path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Structures/Peptide.png"

    def __init__( self, command ):
        """
        Construct the "Build Graphene" Property Manager.
        """
        _superclass.__init__( self, command )
               
               
        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_PREVIEW_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        # phi psi angles will define the secondary structure of the peptide chain
        self.phi = -57.0
        self.psi = -47.0
        self.chirality = 1
        self.secondary = SS_COIL
        self.current_amino_acid = 0
        #self.peptide_cache = []
        #self.peptide_cache.append((0, 0, 0))
        self.updateMessageGroupBox()
                
    def updateMessageGroupBox(self):
       
        msg = "Click on the Amino Acid buttons to add a new residue to " \
            "the polypeptide chain. Click <b>Done</b> to insert it into the project."

        # This causes the "Message" box to be displayed as well.
        # setAsDefault=True causes this message to be reset whenever
        # this PropMgr is (re)displayed via show(). Mark 2007-06-01.
        self.updateMessage(msg)
        
    def getParameters(self):
        """
        Return the parameters from this property manager
        to be used to create the  peptide.
        @return: A tuple containing the parameters
        @rtype: tuple
        @see: L{Peptide_EditCommand._gatherParameters()} where this is used
        
        """
        #return (self.a1, self.a2, self.a3, self.a4, self.a5, self.a6)
    
        return (self.secondary, self.phi, self.psi, self.current_amino_acid)

    def _addGroupBoxes(self):
        """
        Add the group boxe to the Peptide Property Manager dialog.
        """
        self.pmGroupBox1 = \
            PM_GroupBox( self, 
                         title          = "Peptide Parameters" )

        # Add group box widgets.
        self._loadGroupBox1(self.pmGroupBox1)

    def _loadGroupBox1(self, inPmGroupBox):
        """
        Load widgets in the group box.
        """

        memberChoices = ["Custom", 
                         "Alpha helix", 
                         "Beta strand",
                         "Pi helix", 
                         "3_10 helix", 
                         "Polyproline-II helix",
                         "Fully extended"]

        self.aaTypeComboBox= \
            PM_ComboBox( inPmGroupBox,
                         label        = "Conformation :", 
                         choices      = memberChoices, 
                         index        = 1, 
                         setAsDefault = True,
                         spanWidth    = False )

        self.connect( self.aaTypeComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self._aaTypeChanged)

        self.phiAngleField = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "Phi angle :", 
                              value        = -57.0, 
                              setAsDefault = True,
                              minimum      = -180.0, 
                              maximum      = 180.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = " degrees")

        self.connect( self.phiAngleField,
                      SIGNAL("valueChanged(double)"),
                      self._aaPhiAngleChanged)

        self.phiAngleField.setEnabled(False)

        self.psiAngleField = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label        = "Psi angle :", 
                              value        = -47.0, 
                              setAsDefault = True,
                              minimum      = -180.0, 
                              maximum      = 180.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = " degrees" )

        self.connect( self.psiAngleField,
                      SIGNAL("valueChanged(double)"),
                      self._aaPsiAngleChanged)

        self.psiAngleField.setEnabled(False)        


        #self.invertChiralityPushButton = \
        #    PM_PushButton( inPmGroupBox,
        #                   text         = 'Invert chirality' ,
        #                   spanWidth    = False
        #               )

        #self.connect(self.invertChiralityPushButton,
        #             SIGNAL("clicked()"),
        #             self._aaChiralityChanged)

        self.aaTypesButtonGroup = \
            PM_ToolButtonGrid( inPmGroupBox, 
                               buttonList = AA_BUTTON_LIST,
                               label      = "Amino acids :",
                               checkedId  = 0,
                               setAsDefault = True )

        self.connect( self.aaTypesButtonGroup.buttonGroup,
                      SIGNAL("buttonClicked(int)"),
                      self._setAminoAcidType)

        #self.addAminoAcid(0)
    
    def addAminoAcid(self, index):
        """
        Adds a new amino acid to the peptide molecule.
        This is going to be displayed after user accepts or previews the structure.
        """

        # add a new amino acid and chain conformation to the peptide cache
        #self.peptide_cache.append((index,self.phi,self.psi))
        #self.peptide_cache[0] = (index,self.phi,self.psi)
        
        self.current_amino_acid = index
        return

    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        #from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_PeptideGeneratorPropertyManager
        #whatsThis_PeptideGeneratorPropertyManager(self)
        pass

    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        #from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_PeptideGeneratorPropertyManager
        #ToolTip_PeptideGeneratorPropertyManager(self)
        pass

    def _aaChiralityChanged(self):
        """
        Set chirality of the peptide chain.
        """
        self.psi *= -1
        self.phi *= -1

        self.phiAngleField.setValue(self.phi)
        self.psiAngleField.setValue(self.psi)

    def _aaTypeChanged(self, idx):
        """
        Slot for Peptide Structure Type combobox.
        Changes phi/psi angles for secondary structure.
        """
        print "edit_command = ", self.command
        
        self.ss_idx = idx

        if idx == 0:
            self.phiAngleField.setEnabled(True)
            self.psiAngleField.setEnabled(True)
        else:
            self.phiAngleField.setEnabled(False)
            self.psiAngleField.setEnabled(False)

        if idx == 1: # alpha helix
            self.phi = -57.0
            self.psi = -47.0
            self.secondary = SS_HELIX
        elif idx == 2: # beta strand
            self.phi = -135.0
            self.psi = 135.0
            self.secondary = SS_STRAND
        elif idx == 3: # 3-10 helix
            self.phi = -55.0
            self.psi = -70.0
            self.secondary = SS_HELIX
        elif idx == 4: # pi helix
            self.phi = -49.0
            self.psi = -26.0
            self.secondary = SS_HELIX
        elif idx == 5: # polyprolin-II
            self.phi = -75.0
            self.psi = 150.0
            self.secondary = SS_COIL
        elif idx == 6: # fully extended
            self.phi = -180.0
            self.psi = 180.0
            self.secondary = SS_STRAND
        else:
            self.phi = self.phiAngleField.value()
            self.psi = self.psiAngleField.value()
            self.secondary = SS_COIL
            
        self.phi *= self.chirality
        self.psi *= self.chirality

        self.phiAngleField.setValue(self.phi)
        self.psiAngleField.setValue(self.psi)
        pass

    def _aaPhiAngleChanged(self, phi):
        self.phi = self.phiAngleField.value()
        pass


    def _aaPsiAngleChanged(self, psi):
        self.psi = self.psiAngleField.value()
        pass        

    def _setAminoAcidType(self, aaTypeIndex):
        """
        Adds a new amino acid to the peptide molecule.
        """
        """
        button, idx, short_name, dum, name, symbol, x, y = AA_BUTTON_LIST[aaTypeIndex]
        if self.ss_idx==1:
            aa_txt = "<font color=red>"
        elif self.ss_idx==2:
            aa_txt = "<font color=blue>"
        elif self.ss_idx==3:
            aa_txt = "<font color=green>"
        elif self.ss_idx==4:
            aa_txt = "<font color=orange>"
        elif self.ss_idx==5:
            aa_txt = "<font color=magenta>"
        elif self.ss_idx==6:
            aa_txt = "<font color=darkblue>"
        else:
            aa_txt = "<font color=black>"

        aa_txt += symbol+"</font>"
        #self.sequenceEditor.insertHtml(aa_txt, False, 4, 10, False)
        """
        self.current_amino_acid = aaTypeIndex
        #self.addAminoAcid(aaTypeIndex)
        return

    
    #def _startOverClicked(self):
    #    """
    #    Resets a sequence in the sequence editor window.
    #    """
    #    self.sequenceEditor.clear()
    #    self.peptide_cache = []
    #    pass
     