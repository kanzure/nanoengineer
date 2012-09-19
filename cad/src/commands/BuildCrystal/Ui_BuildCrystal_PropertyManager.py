# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Ui_BuildCrystal_PropertyManager.py

@author: Ninad
@version:$Id$

UI file for Crystal Property Manager. e.g. UI for groupboxes
(and its contents), button rows etc.

History:

- These options appeared in formerly 'cookie cutter dashboard' till Alpha8
- Post Alpha8 (sometime after 12/2006), the options were included
in the BuildCrystal_PropertyManager (formerly Cookie Property Manager. )
- In Alpha 9 , 'Cookie Cutter' was renamed to 'Build Crystal'

ninad 2007-09-10: Rewrote this class to make it use PM module classes.
Ninad 2008-08-23: Renamed Ui_CookiePropertyManager to
                  Ui_BuildCrystal_PropertyManager
"""
from PyQt4.Qt import Qt
from PyQt4.Qt import QSize


from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_PushButton    import PM_PushButton
from PM.PM_ToolButtonRow import PM_ToolButtonRow
from PM.PM_LineEdit      import PM_LineEdit
from PM.PM_WidgetRow     import PM_WidgetRow

from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON

from utilities.icon_utilities import geticon

from command_support.Command_PropertyManager import Command_PropertyManager

_superclass = Command_PropertyManager
class Ui_BuildCrystal_PropertyManager(Command_PropertyManager):
    """
    The Ui_BuildCrystal_PropertyManager class defines UI elements for the Property
    Manager of the B{Crystal mode}.

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    # <title> - the title that appears in the property manager header.
    title = "Build Crystal"
    # <iconPath> - full path to PNG file that appears in the header.
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    iconPath = "ui/actions/Tools/Build Structures/Build Crystal.png"

    def __init__(self, command):
        """
        Constructor for the B{Crystal} property manager class that defines
        its UI.

        @param command: The parent mode where this Property Manager is used
        @type  command: L{BuildCrystal_Command}
        """


        _superclass.__init__(self, command)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_WHATS_THIS_BUTTON)


    def _addGroupBoxes(self):
        """
        Add various group boxes to the Property manager.
        """
        self._addCrystalSpecsGroupbox()
        self._addLayerPropertiesGroupBox()
        self._addDisplayOptionsGroupBox()
        self._addAdvancedOptionsGroupBox()

    def _addCrystalSpecsGroupbox(self):
        """
        Add 'Crystal groupbox' to the PM
        """
        self.crystalSpecsGroupBox = \
            PM_GroupBox(self, title = "Crystal Specifications")
        self._loadCrystalSpecsGroupBox(self.crystalSpecsGroupBox)

    def _addLayerPropertiesGroupBox(self):
        """
        Add 'Layer Properties' groupbox to the PM
        """
        self.layerPropertiesGroupBox = \
            PM_GroupBox(self, title = "Layer Properties")
        self._loadLayerPropertiesGroupBox(self.layerPropertiesGroupBox)


    def _addAdvancedOptionsGroupBox(self):
        """
        Add 'Advanced Options' groupbox
        """
        self.advancedOptionsGroupBox = \
            PM_GroupBox( self, title = "Advanced Options" )
        self._loadAdvancedOptionsGroupBox(self.advancedOptionsGroupBox)

    def _addDisplayOptionsGroupBox(self):
        """
        Add 'Display Options' groupbox
        """
        self.displayOptionsGroupBox = PM_GroupBox(self,
                                                  title = 'Display Options')
        self._loadDisplayOptionsGroupBox(self.displayOptionsGroupBox)

    def _loadCrystalSpecsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Crystal Specifications group box.
        @param inPmGroupBox: The Crystal Specifications groupbox in the PM
        @type  inPmGroupBox: L{PM_GroupBox}
        """
        latticeChoices = ["Diamond", "Lonsdaleite"]

        self.latticeCBox = \
            PM_ComboBox( inPmGroupBox,
                         label        = 'Lattice:',
                         labelColumn  = 0,
                         choices      = latticeChoices,
                         index        = 0,
                         setAsDefault = True,
                         spanWidth    = False )

        # Button list to create a toolbutton row.
        # Format:
        # - buttonType,
        # - buttonId,
        # - buttonText ,
        # - iconPath
        # - tooltip
        # - shortcut
        # - column
        BUTTON_LIST = [
            ( "QToolButton", 0,  "Surface 100",
              "ui/actions/Properties Manager/Surface100.png",
              "Surface 100", "", 0),

            ( "QToolButton", 1,  "Surface 110",
              "ui/actions/Properties Manager/Surface110.png",
              "Surface 110", "", 1),

            ( "QToolButton", 2,  "Surface 111",
              "ui/actions/Properties Manager/Surface111.png",
              "Surface 110", "", 2)
            ]
        self.gridOrientationButtonRow = \
            PM_ToolButtonRow(inPmGroupBox,
                               title        = "",
                               label        = "Orientation:",
                               buttonList   = BUTTON_LIST,
                               checkedId    = 0,
                               setAsDefault = True,
                               spanWidth   = False
                               )

        self.orientButtonGroup = self.gridOrientationButtonRow.buttonGroup
        self.surface100_btn = self.gridOrientationButtonRow.getButtonById(0)
        self.surface110_btn = self.gridOrientationButtonRow.getButtonById(1)
        self.surface111_btn = self.gridOrientationButtonRow.getButtonById(2)

        self.rotateGridByAngleSpinBox = \
            PM_SpinBox( inPmGroupBox,
                        label         =  "Rotate by: ",
                        labelColumn   =  0,
                        value         =  45,
                        minimum       =  0,
                        maximum       =  360,
                        singleStep    =  5,
                        suffix        = " degrees")

        GRID_ANGLE_BUTTONS = [
                        ("QToolButton", 0,  "Anticlockwise",
                         "ui/actions/Properties Manager/rotate_minus.png",
                         "", "+", 0 ),

                        ( "QToolButton", 1,  "Clockwise",
                          "ui/actions/Properties Manager/rotate_plus.png",
                          "", "-", 1 )
                        ]

        self.gridRotateButtonRow = \
            PM_ToolButtonRow( inPmGroupBox,
                              title        = "",
                              buttonList   = GRID_ANGLE_BUTTONS,
                              label        = 'Rotate grid:',
                              isAutoRaise  =  False,
                              isCheckable  =  False
                            )
        self.rotGridAntiClockwiseButton = \
            self.gridRotateButtonRow.getButtonById(0)
        self.rotGridClockwiseButton = \
            self.gridRotateButtonRow.getButtonById(1)

    def _loadLayerPropertiesGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Layer Properties group box.
        @param inPmGroupBox: The Layer Properties groupbox in the PM
        @type  inPmGroupBox: L{PM_GroupBox}
        """

        self.currentLayerComboBox = \
            PM_ComboBox( inPmGroupBox,
                         index     = 0,
                         spanWidth = True
                        )

        self.addLayerButton = PM_PushButton(inPmGroupBox)
        self.addLayerButton.setIcon(
            geticon('ui/actions/Properties Manager/addlayer.png'))
        self.addLayerButton.setFixedSize(QSize(26, 26))
        self.addLayerButton.setIconSize(QSize(22, 22))

        # A widget list to create a widget row.
        # Format:
        # - Widget type,
        # - widget object,
        # - column

        firstRowWidgetList = [('PM_ComboBox', self.currentLayerComboBox, 1),
                              ('PM_PushButton', self.addLayerButton, 2)
                              ]

        widgetRow = PM_WidgetRow(inPmGroupBox,
                                 title     = '',
                                 widgetList = firstRowWidgetList,
                                 label = "Layer:",
                                 labelColumn  = 0,
                                 )

        self.layerCellsSpinBox = \
             PM_SpinBox( inPmGroupBox,
                        label         =  "Lattice cells:",
                        labelColumn   =  0,
                        value         =  2,
                        minimum       =  1,
                        maximum       =  25
                      )

        self.layerThicknessLineEdit = PM_LineEdit(inPmGroupBox,
                                         label        = "Thickness:",
                                         text         = "",
                                         setAsDefault = False,
                                         spanWidth    = False )

        #self.layerThicknessLineEdit.setReadOnly(True)
        self.layerThicknessLineEdit.setDisabled(True)
        tooltip = "Thickness of layer in Angstroms"
        self.layerThicknessLineEdit.setToolTip(tooltip)


    def _loadAdvancedOptionsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Advanced Options group box.
        @param inPmGroupBox: The Advanced Options box in the PM
        @type  inPmGroupBox: L{PM_GroupBox}
        """
        self.snapGridCheckBox = \
            PM_CheckBox(inPmGroupBox,
                        text = "Snap to grid",
                        state = Qt.Checked
                        )
        tooltip = "Snap selection point to a nearest cell grid point."
        self.snapGridCheckBox.setToolTip(tooltip)

        self.freeViewCheckBox = \
            PM_CheckBox(inPmGroupBox,
                        text = "Enable free view",
                        state = Qt.Unchecked
                    )

    def _loadDisplayOptionsGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Display Options groupbox.
        @param inPmGroupBox: The Display Options groupbox
        @type  inPmGroupBox: L{PM_GroupBox}
        """

        displayChoices = ['Tubes', 'Spheres']

        self.dispModeComboBox = \
            PM_ComboBox( inPmGroupBox,
                         label        = 'Display style:',
                         choices      = displayChoices,
                         index        = 0,
                         setAsDefault = False,
                         spanWidth    = False )


        self.gridLineCheckBox = PM_CheckBox(inPmGroupBox,
                                            text = "Show grid lines",
                                            widgetColumn = 0,
                                            state        = Qt.Checked)


        self.fullModelCheckBox = PM_CheckBox(inPmGroupBox,
                                            text = "Show model",
                                            widgetColumn = 0,
                                            state        = Qt.Unchecked)

    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.

        @note: Many PM widgets are still missing their "What's This" text.
        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_CookiePropertyManager
        whatsThis_CookiePropertyManager(self)

    def _addToolTipText(self):
        """
        What's Tool Tip text for widgets in this Property Manager.
        """
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_CookiePropertyManager
        ToolTip_CookiePropertyManager(self)

