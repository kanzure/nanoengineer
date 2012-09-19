# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
CompareProteins_PropertyManager.py

The CompareProteins_PropertyManager class provides a Property Manager
for the B{Compare Proteins} command on the flyout toolbar in the
Build > Protein mode.

@author: Piotr
@version: $Id$
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

TODO:
- Switch display styles of selected proteins to diPROTEIN (instead of the GDS).
- PM color comboboxes to choose the "difference colors".

BUGS:
- Previously compared proteins still show differences after comparing a new set of proteins.
- "Hide differences" button should be disabled (or hidden) when there are no differences.

"""

import foundation.env as env

from command_support.Command_PropertyManager import Command_PropertyManager
from utilities.prefs_constants import workingDirectory_prefs_key
from utilities.constants import yellow

from PyQt4.Qt import SIGNAL
from PM.PM_PushButton   import PM_PushButton
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_LineEdit import PM_LineEdit
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_Constants import PM_DONE_BUTTON
from PM.PM_Constants import PM_WHATS_THIS_BUTTON
from protein.model.Protein import getAllProteinChunksInPart
from utilities.constants import diPROTEIN
from utilities.Log import redmsg

_superclass = Command_PropertyManager
class CompareProteins_PropertyManager(Command_PropertyManager):
    """
    The CompareProteins_PropertyManager class provides a Property Manager
    for the B{Compare Proteins} command on the Build Protein flyout toolbar.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str

    @ivar proteinChunk1: The first currently selected protein to be compared.
    @type proteinChunk1: protein chunk

    @ivar proteinChunk2: The second currently selected protein to be compared.
    @type proteinChunk2: protein chunk
    """

    title          =  "Compare Proteins"
    pmName         =  title
    iconPath       =  "ui/actions/Command Toolbar/BuildProtein/Compare.png"
    proteinChunk1  =  None
    proteinChunk2  =  None

    def __init__( self, command ):
        """
        Constructor for the property manager.
        """
        self.threshold = 10.0

        _superclass.__init__(self, command)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        return

    def connect_or_disconnect_signals(self, isConnect = True):

        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect

        change_connect(self.comparePushButton,
                       SIGNAL("clicked()"),
                       self._compareProteins)

        change_connect(self.thresholdDoubleSpinBox,
                       SIGNAL("valueChanged(double)"),
                       self._thresholdChanged)

        change_connect(self.hidePushButton,
                       SIGNAL("clicked()"),
                       self._hideDifferences)
        return

    def close(self):
        """
        Closes the Property Manager. Overrides EditCommand_PM.close()
        """

        env.history.statusbar_msg("")
        self._resetAminoAcids()
        _superclass.close(self)

        # Restore the original global display style.
        self.o.setGlobalDisplayStyle(self.originalDisplayStyle)
        return

    def show(self):
        """
        Show the PM. Extends superclass method.

        @note: _update_UI_do_updates() gets called immediately after this and
               updates PM widgets with their correct values/settings.
        """
        _superclass.show(self)
        env.history.statusbar_msg("")

        # Force the Global Display Style to "Protein" since this is the only way
        # to see comparisons. The global display style will be restored when leaving
        # this command (via self.close()).
        self.originalDisplayStyle = self.o.displayMode
        self.o.setGlobalDisplayStyle(diPROTEIN)
        return

    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self,
                                         title = "Compare")
        self._loadGroupBox1( self._pmGroupBox1 )
        return

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

    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """

        self.structure1LineEdit = \
            PM_LineEdit( pmGroupBox,
                         label         =  "First structure:",
                         setAsDefault  =  False)
        self.structure1LineEdit.setEnabled(False)

        self.structure2LineEdit = \
            PM_LineEdit( pmGroupBox,
                         label         =  "Second structure:",
                         setAsDefault  =  False)
        self.structure2LineEdit.setEnabled(False)

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

        self.comparePushButton  = \
            PM_PushButton( pmGroupBox,
                         text         =  "Compare",
                         setAsDefault  =  True)

        self.hidePushButton  = \
            PM_PushButton( pmGroupBox,
                         text         =  "Hide differences",
                         setAsDefault  =  True)
        return

    def _compareProteins(self):
        """
        Slot for Compare button.

        Compares two selected proteins of the same length.
        Amino acids that differ greater than the "threshold"
        value are displayed in two colors (red for the first protein
        and yellow for the second protein) and are only visible when
        the two proteins are displayed in the
        reduced display style.
        """
        from utilities.constants import red, orange, green, cyan

        if not self.proteinChunk1 or \
           not self.proteinChunk2:
            return

        protein_1 = self.proteinChunk1.protein
        protein_2 = self.proteinChunk2.protein

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
                msg = "The lengths of compared proteins are not equal."
                self.updateMessage(msg)
                env.history.redmsg(msg)
        return

    def _hideDifferences(self):
        """
        Slot for the "Hide differences" button.

        Hides amino acids that differ greater than the "threshold" value.

        @warning: Untested. Code looks suspicious.
        """
        if not self.proteinChunk1 or \
           not self.proteinChunk2:
            return

        protein_1 = self.proteinChunk1.protein
        protein_2 = self.proteinChunk2.protein

        if protein_1 and \
           protein_2:
            aa_list_1 = protein_1.get_amino_acids()
            aa_list_2 = protein_2.get_amino_acids()
            if len(aa_list_1) == len(aa_list_2):
                protein_1.collapse_all_rotamers() #@@@
                protein_2.collapse_all_rotamers() #@@@
                for aa1, aa2 in zip (aa_list_1, aa_list_2):
                    aa1.color = None
                    aa2.color = None
                    aa1.collapse()
                    aa2.collapse()
            self.win.glpane.gl_update()
        return

    def _thresholdChanged(self, value):
        """
        Slot for Threshold spinbox.
        """
        self.threshold = value
        self._compareProteins()
        return

    def _resetAminoAcids(self):
        """
        Resets the color and collapse all amino acids of all proteins.
        """

        proteinChunkList = getAllProteinChunksInPart(self.win.assy)

        for proteinChunk in proteinChunkList:
            proteinChunk.protein.collapse_all_rotamers()
            aa_list = proteinChunk.protein.get_amino_acids()
            for aa in aa_list:
                aa.color = None
                aa.collapse()

        self.win.glpane.gl_update()
        return

    def _update_UI_do_updates(self):
        """
        Overrides superclass method.

        @see: Command_PropertyManager._update_UI_do_updates()
        """

        self.proteinChunk1 = None
        self.proteinChunk2 = None
        self.comparePushButton.setEnabled(False)
        self.hidePushButton.setEnabled(False)

        selectedProteinList = self.win.assy.getSelectedProteinChunks()

        if len(selectedProteinList) == 0:
            self.structure1LineEdit.setText("")
            self.structure2LineEdit.setText("")
            msg = "Select two structures of the same length in the graphics area, "\
                "then click the <b>Compare</b> button to compare them."

        elif len(selectedProteinList) == 1:
            self.proteinChunk1 = selectedProteinList[0]
            aa1_count = " (%d)" % self.proteinChunk1.protein.count_amino_acids()
            self.structure1LineEdit.setText(self.proteinChunk1.name + aa1_count)
            self.structure2LineEdit.setText("")
            msg = "Select one more structure in the graphics area that is the same "\
                "length as <b>" + self.proteinChunk1.name + "</b>. "\
                "Then click the <b>Compare</b> button to compare them."

        elif len(selectedProteinList) == 2:
            self.proteinChunk1 = selectedProteinList[0]
            aa1_count = " (%d)" % self.proteinChunk1.protein.count_amino_acids()
            self.structure1LineEdit.setText(self.proteinChunk1.name + aa1_count)

            self.proteinChunk2 = selectedProteinList[1]
            aa2_count = " (%d)" % self.proteinChunk2.protein.count_amino_acids()
            self.structure2LineEdit.setText(self.proteinChunk2.name + aa2_count)

            if aa1_count == aa2_count:
                self.comparePushButton.setEnabled(True)
                self.hidePushButton.setEnabled(True)
                msg = "Click the <b>Compare</b> button to compare the two selected structures."
            else:
                msg = "<b>%s</b> and <b>%s</b> are not the same length." % \
                    (self.proteinChunk1.name, self.proteinChunk2.name)
                msg = redmsg(msg)

        else:
            self.structure1LineEdit.setText("")
            self.structure2LineEdit.setText("")
            msg = redmsg("Too many proteins selected.")

        self.updateMessage(msg)
        env.history.redmsg(msg)
        return

