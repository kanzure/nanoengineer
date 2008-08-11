# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Ui_ExtrudePropertyManager.py - UI elements for the B{Extrude Mode} Property
Manager.

@version: $Id$
@copyight: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

ninad 2007-01-10: Split the ui code out of extrudeMode while converting
extrude dashboard to extrude property manager.
ninad 2007-09-10: Code clean up to use PM module classes
"""

from PyQt4.Qt import Qt

from PM.PM_Dialog        import PM_Dialog
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_Slider        import PM_Slider
from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_SpinBox       import PM_SpinBox

from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON


class Ui_ExtrudePropertyManager(PM_Dialog):
    """
    The Ui_ExtrudePropertyManager class defines UI elements for the Property
    Manager of the B{Extrude mode}.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    # The title that appears in the Property Manager header
    title = "Extrude"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Properties Manager/Extrude.png"

    def __init__(self, command):
        """
        Constructor for the B{Extrude} property manager class that defines
        its UI.

        @param command: The parent mode where this Property Manager is used
        @type  command: L{extrudeMode}
        """
        self.command = command
        self.w = self.command.w
        self.win = self.command.w
        self.pw = self.command.pw
        self.o = self.win.glpane

        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_WHATS_THIS_BUTTON)


        msg = ''
        self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)

    def _addGroupBoxes(self):
        """
        Add various group boxes to the Extrude Property manager.
        """

        self._addProductSpecsGroupBox()
        self._addAdvancedOptionsGroupBox()

    def _addProductSpecsGroupBox(self):
        """
        """
        self.productSpecsGroupBox = \
            PM_GroupBox( self, title = "Product Specifications" )
        self._loadProductSpecsGroupBox(self.productSpecsGroupBox)

    def _addAdvancedOptionsGroupBox(self):
        """
        Add 'Advanced Options' groupbox
        """
        self.advancedOptionsGroupBox = \
            PM_GroupBox( self, title = "Advanced Options" )
        self._loadAdvancedOptionsGroupBox(self.advancedOptionsGroupBox)

    def _loadProductSpecsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Product specifications group box.
        @param inPmGroupBox: The roduct specifications box in the PM
        @type  inPmGroupBox: L{PM_GroupBox}
        """

        productChoices = ['Rod', 'Ring']

        self.extrude_productTypeComboBox = \
            PM_ComboBox( inPmGroupBox,
                         label        = 'Final product:',
                         labelColumn  = 0,
                         choices      = productChoices,
                         index        = 0,
                         setAsDefault = True,
                         spanWidth    = False )

        # names used in the code, same order
        #if you comment out items from combobox, you also have to remove them
        # from this list unless they are at the end!!!
        self.extrude_productTypeComboBox_ptypes = ["straight rod", \
                                                   "closed ring", \
                                                   "corkscrew"]

        self.extrudeSpinBox_n = \
            PM_SpinBox( inPmGroupBox,
                        label         =  "Number of copies:",
                        labelColumn   =  0,
                        value         =  3,
                        minimum       =  1,
                        maximum       =  99
                    )
        #@WARNING: This method initializes some instance varaiables for various
        #checkboxes. (Example: self.mergeCopiesCheckBox.default = False).
        #These values are needed in extrudemode.py. This
        #won't be needed once extrudeMode.py is cleaned up. -- ninad 2007-09-10

        self.extrudeBondCriterionSlider =  \
            PM_Slider( inPmGroupBox,
                       currentValue = 100,
                       minimum      = 0,
                       maximum      = 300,
                       label        = 'Tolerence'
                   )
        self.extrudeBondCriterionLabel = \
            self.extrudeBondCriterionSlider.labelWidget

        self.extrudeBondCriterionSlider_dflt = 100
        self.extrudeBondCriterionSlider.setPageStep(5)

        self.makeBondsCheckBox = \
            PM_CheckBox(inPmGroupBox,
                        text         = 'Make bonds' ,
                        widgetColumn = 0,
                        state        = Qt.Checked
                    )
        self.makeBondsCheckBox.default = True
        self.makeBondsCheckBox.attr = 'whendone_make_bonds'
        self.makeBondsCheckBox.repaintQ = False


    def _loadAdvancedOptionsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Advanced Options group box.
        @param inPmGroupBox: The Advanced Options box in the PM
        @type  inPmGroupBox: L{PM_GroupBox}

        """
        self.offsetSpecsGroupBox = PM_GroupBox(inPmGroupBox,
                                               title = 'Offset Between Copies:'
                                           )
        self._loadOffsetSpecsGroupBox(self.offsetSpecsGroupBox)

        self.mergeOptionsGroupBox = PM_GroupBox(inPmGroupBox,
                                                title = 'Merge Options:' )
        self._loadMergeOptionsGroupBox(self.mergeOptionsGroupBox)

        self.displayOptionsGroupBox = PM_GroupBox(inPmGroupBox,
                                                  title = 'Display Options:')
        self._loadDisplayOptionsGroupBox(self.displayOptionsGroupBox)
        return
    
    def _loadDisplayOptionsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Display Options groupbox (which is a groupbox within
        the B{Advanced Options group box} ) .
        @param inPmGroupBox: The Display Options groupbox
        @type  inPmGroupBox: L{PM_GroupBox}
        @WARNING: This method initializes some instance varaiables for various
        checkboxes. (Example: self.mergeCopiesCheckBox.default = False). This
        won't be needed once extrudeMode.py is cleaned up.
        """
        self.showEntireModelCheckBox = \
            PM_CheckBox(inPmGroupBox,
                        text         = 'Show entire model' ,
                        widgetColumn = 1,
                        state        = Qt.Unchecked
                    )
        self.showEntireModelCheckBox.default = False
        self.showEntireModelCheckBox.attr = 'show_entire_model'
        self.showEntireModelCheckBox.repaintQ = True

        self.showBondOffsetCheckBox = \
            PM_CheckBox(inPmGroupBox,
                        text         = 'Show bond-offset spheres' ,
                        widgetColumn = 1,
                        state        = Qt.Unchecked
                    )
        self.showBondOffsetCheckBox.default = False
        self.showBondOffsetCheckBox.attr = 'show_bond_offsets'
        self.showBondOffsetCheckBox.repaintQ = True

    def _loadMergeOptionsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Merge Options groupbox (which is a groupbox within
        the B{Advanced Options group box}).
        @param inPmGroupBox: The Merge Options groupbox
        @type  inPmGroupBox: L{PM_GroupBox}
        @WARNING: This method initializes some instance varaiables for various
        checkboxes. (Example: self.mergeCopiesCheckBox.default = False). This
        won't be needed once extrudeMode.py is cleaned up.
        """
        self.mergeCopiesCheckBox = \
            PM_CheckBox(inPmGroupBox,
                        text         = 'Merge copies' ,
                        widgetColumn = 1,
                        state        = Qt.Unchecked
                    )
        self.mergeCopiesCheckBox.default = False
        self.mergeCopiesCheckBox.attr = 'whendone_all_one_part'
        self.mergeCopiesCheckBox.repaintQ = False


        self.extrudePrefMergeSelection = \
            PM_CheckBox(inPmGroupBox,
                        text         = 'Merge selection' ,
                        widgetColumn = 1,
                        state        = Qt.Unchecked
                    )
        self.extrudePrefMergeSelection.default = False
        self.extrudePrefMergeSelection.attr = 'whendone_merge_selection'
        self.extrudePrefMergeSelection.repaintQ = False

    def _loadOffsetSpecsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Offset specs groupbox (which is a groupbox within
        the B{Advanced Options group box}).
        @param inPmGroupBox: The Offset Specs gropbox box
        @type  inPmGroupBox: L{PM_GroupBox}
        """
        self.extrudeSpinBox_length = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  "Total offset",
                              value         =  7.0,
                              setAsDefault  =  True,
                              minimum       =  0.1,
                              maximum       =  2000.0,
                              singleStep    =  1,
                              decimals      =  3,
                              suffix        =  ' Angstroms'
                          )

        self.extrudeSpinBox_x = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  "X offset",
                              value         =  0,
                              minimum       =  -1000.0,
                              maximum       =  1000.0,
                              singleStep    =  1,
                              decimals      =  3,
                              suffix        =  ' Angstroms'
                          )

        self.extrudeSpinBox_y = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  "Y offset",
                              value         =  0,
                              minimum       =  -1000.0,
                              maximum       =  1000.0,
                              singleStep    =  1,
                              decimals      =  3,
                              suffix        =  ' Angstroms'
                          )
        self.extrudeSpinBox_z = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  "Z offset",
                              value         =  0,
                              minimum       =  -1000.0,
                              maximum       =  1000.0,
                              singleStep    =  1,
                              decimals      =  3,
                              suffix        =  ' Angstroms'
                          )

    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.

        @note: Many PM widgets are still missing their "What's This" text.
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_ExtrudePropertyManager
        whatsThis_ExtrudePropertyManager(self)

        return
