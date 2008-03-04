# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

This is a Property Manager dialog of the Peptide Generator.

@author: Piotr
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:

Piotr 2008-01-11: Implemented Peptide Generator dialog using PropMgrBaseClass 
                  (just copied most stuff from NanotubeGeneratorPropertyManager).

Piotr 2008-03-02: Re-written the Property Manager dialogs to allow it working in 
                  the interactive mode.

"""

import math

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import SIGNAL

from PM.PM_Dialog         import PM_Dialog
from PM.PM_GroupBox       import PM_GroupBox
from PM.PM_ComboBox       import PM_ComboBox
from PM.PM_DoubleSpinBox  import PM_DoubleSpinBox
from PM.PM_SpinBox        import PM_SpinBox
from PM.PM_PushButton     import PM_PushButton
from PM.PM_ToolButtonGrid import PM_ToolButtonGrid
from PM.PM_TextEdit       import PM_TextEdit

from debug import print_compact_traceback

from utilities.Log import orangemsg, greenmsg, redmsg
import env

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

class PeptideGeneratorPropertyManager(PM_Dialog):
    """
    The PeptideGeneratorPropertyManager class provides a Property Manager 
    for the "Build > Peptide" command.
    """
    # The title that appears in the property manager header.
    title = "Peptide"
    # The name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    pmName = title
    # The relative path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Structures/Peptide.png"
    
    def __init__(self):
        """Construct the Peptide Property Manager.
        """
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)

        # phi psi angles will define the secondary structure of the peptide chain
        self.phi = -57.0
        self.psi = -47.0 
        self.ss_idx = 0
        self.peptide_cache = []
            
        self.updateMessageGroupBox()
                
    def updateMessageGroupBox(self):
        msg = ""

        msg = msg + "Click on <b>Amino Acid</b> buttons to add a new residuum to the \
        polypeptide chain. Click <b>Done</b> to insert it into the model."
        
        # This causes the "Message" box to be displayed as well.
        # setAsDefault=True causes this message to be reset whenever
        # this PropMgr is (re)displayed via show(). Mark 2007-06-01.
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=True)
        
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
        
        memberChoices = ["Alpha helix", "Pi helix", "3_10 helix", "Beta strand"]
        self.aaTypeComboBox= \
            PM_ComboBox( inPmGroupBox,
                         label        = "Conformation :", 
                         choices      = memberChoices, 
                         index        = 0, 
                         setAsDefault = True,
                         spanWidth    = False )

        self.connect( self.aaTypeComboBox,
                      SIGNAL("currentIndexChanged(int)"),
                      self._aaTypeChanged)
 
        self.aaTypesButtonGroup = \
            PM_ToolButtonGrid( inPmGroupBox, 
                               buttonList = AA_BUTTON_LIST,
                               label      = "Amino acids :",
                               checkedId  = 0,
                               setAsDefault = True )

        self.connect( self.aaTypesButtonGroup.buttonGroup,
                      SIGNAL("buttonClicked(int)"),
                      self._setAminoAcidType)
        
        self.sequenceEditor = \
            PM_TextEdit( inPmGroupBox, 
                         label      = "",
                         spanWidth = True )
                         
        self.sequenceEditor.insertHtml("Sequence:<br>", False, 4, 10, True)

        self.startOverButton = \
            PM_PushButton( inPmGroupBox,
                           label     = "",
                           text      = "Start Over",
                           spanWidth = True,
                           setAsDefault = True )

        self.connect( self.startOverButton,
                      SIGNAL("clicked()"),
                      self._startOverClicked)

    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        from gui.WhatsThisText_for_PropertyManagers import whatsThis_PeptideGeneratorPropertyManager
        whatsThis_PeptideGeneratorPropertyManager(self)
        
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        from gui.ToolTipText_for_PropertyManagers import ToolTip_PeptideGeneratorPropertyManager
        ToolTip_PeptideGeneratorPropertyManager(self)
        
    def _aaTypeChanged(self, idx):
        """
        Slot for Peptide Structure Type combobox.
        Changes phi/psi angles for secondary structure.
        """
        self.ss_idx = idx
        if idx==0: # alpha helix
            self.phi = -57.0
            self.psi = -47.0
        elif idx==1: # pi helix
            self.phi = -55.0
            self.psi = -70.0
        elif idx==2: # 3-10 helix
            self.phi = -49.0
            self.psi = -26.0
        else: # beta strand
            self.phi = 180.0
            self.psi = 170.0
 
    def _setAminoAcidType(self, aaTypeIndex):
        """
        Adds a new amino acid to the peptide molecule.
        """
        button, idx, short_name, dum, name, symbol, x, y = AA_BUTTON_LIST[aaTypeIndex]
        self.sequenceEditor.insertHtml(symbol, False, 4, 10, False)
        self.addAminoAcid(aaTypeIndex)
        
    def _startOverClicked(self):
        """
        Resets a sequence in the sequence editor window.
        """
        self.sequenceEditor.insertHtml("Sequence:<br>", False, 4, 10, True)
        self.peptide_cache = []
