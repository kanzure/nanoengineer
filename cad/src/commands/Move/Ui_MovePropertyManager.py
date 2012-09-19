# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Ui_MovePropertyManager.py
@author: Ninad
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.
$Id$

History:

ninad 2007-08-20: code cleanup to use new PM module classes.
"""

from PyQt4.Qt import Qt

from PM.PM_GroupBox        import PM_GroupBox
from PM.PM_DoubleSpinBox   import PM_DoubleSpinBox
from PM.PM_ComboBox        import PM_ComboBox
from PM.PM_PushButton      import PM_PushButton
from PM.PM_CheckBox        import PM_CheckBox
from PM.PM_ToolButtonRow   import PM_ToolButtonRow
from PM.PM_ToolButton      import PM_ToolButton
from PM.PM_LineEdit        import PM_LineEdit
from PM.PM_LabelRow        import PM_LabelRow
from PM.PM_CoordinateSpinBoxes import PM_CoordinateSpinBoxes

from PM.PM_Constants       import PM_DONE_BUTTON
from PM.PM_Constants       import PM_WHATS_THIS_BUTTON


from command_support.Command_PropertyManager import Command_PropertyManager

_superclass = Command_PropertyManager
class Ui_MovePropertyManager(Command_PropertyManager):


    # The title that appears in the Property Manager header
    title = "Move"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Properties Manager/Translate_Components.png"

    # The title(s) that appear in the property manager header.
    # (these are changed depending on the active group box)
    translateTitle = "Translate"
    rotateTitle = "Rotate"

    # The full path to PNG file(s) that appears in the header.
    translateIconPath = "ui/actions/Properties Manager/Translate_Components.png"
    rotateIconPath = "ui/actions/Properties Manager/Rotate_Components.png"

    def __init__(self, command):
        _superclass.__init__(self, command)
        self.showTopRowButtons(PM_DONE_BUTTON | PM_WHATS_THIS_BUTTON)

    def _addGroupBoxes(self):
        """
        Add groupboxes to the Property Manager dialog.
        """

        self.translateGroupBox = PM_GroupBox( self,
                                              title = "Translate",
                                              connectTitleButton = False)
        self.translateGroupBox.titleButton.setShortcut('T')
        self._loadTranslateGroupBox(self.translateGroupBox)

        self.rotateGroupBox = PM_GroupBox( self,
                                           title = "Rotate",
                                           connectTitleButton = False)
        self.rotateGroupBox.titleButton.setShortcut('R')
        self._loadRotateGroupBox(self.rotateGroupBox)

        self.translateGroupBox.collapse()
        self.rotateGroupBox.collapse()

    # == Begin Translate Group Box =====================

    def _loadTranslateGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Translate group box.
        @param inPmGroupBox: The Translate group box in the PM
        @type  inPmGroupBox: L{PM_GroupBox}
        """

        translateChoices = [ "Free Drag",
                             "By Delta XYZ",
                             "To XYZ Position" ]

        self.translateComboBox = \
            PM_ComboBox( inPmGroupBox,
                         label        = '',
                         choices      = translateChoices,
                         index        = 0,
                         setAsDefault = False,
                         spanWidth    = True )

        self.freeDragTranslateGroupBox = PM_GroupBox( inPmGroupBox )
        self._loadFreeDragTranslateGroupBox(self.freeDragTranslateGroupBox)

        self.byDeltaGroupBox = PM_GroupBox( inPmGroupBox )
        self._loadByDeltaGroupBox(self.byDeltaGroupBox)

        self.toPositionGroupBox = PM_GroupBox( inPmGroupBox )
        self._loadToPositionGroupBox(self.toPositionGroupBox)

        self.updateTranslateGroupBoxes(0)

    def _loadFreeDragTranslateGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Free Drag Translate group box, which is present
        within the Translate groupbox.
        @param inPmGroupBox: The Free Drag Translate group box in the Translate
                             group box.
        @type  inPmGroupBox: L{PM_GroupBox}
        """
        # Button list to create a toolbutton row.
        # Format:
        # - buttonId,
        # - buttonText ,
        # - iconPath
        # - tooltip
        # - shortcut
        # - column


        BUTTON_LIST = [
            ( "QToolButton", 1,  "MOVEDEFAULT",
              "ui/actions/Properties Manager/Move_Free.png", "", "F", 0),
            ( "QToolButton", 2,  "TRANSX",
              "ui/actions/Properties Manager/TranslateX.png", "", "X", 1),
            ( "QToolButton", 3,  "TRANSY",
              "ui/actions/Properties Manager/TranslateY.png", "", "Y", 2),
            ( "QToolButton", 4,  "TRANSZ",
              "ui/actions/Properties Manager/TranslateZ.png", "", "Z", 3),
            ( "QToolButton", 5,  "ROT_TRANS_ALONG_AXIS",
              "ui/actions/Properties Manager/translate+rotate-A.png", "", \
              "A", 4)

            ]

        self.freeDragTranslateButtonGroup = \
            PM_ToolButtonRow( inPmGroupBox,
                               title        = "",
                               buttonList   = BUTTON_LIST,
                               checkedId    = 1,
                               setAsDefault = True,
                               )
        self.transFreeButton =self.freeDragTranslateButtonGroup.getButtonById(1)
        self.transXButton = self.freeDragTranslateButtonGroup.getButtonById(2)
        self.transYButton = self.freeDragTranslateButtonGroup.getButtonById(3)
        self.transZButton = self.freeDragTranslateButtonGroup.getButtonById(4)
        self.transAlongAxisButton = \
            self.freeDragTranslateButtonGroup.getButtonById(5)

        self.moveFromToButton = PM_ToolButton(
                    inPmGroupBox,
                    text = "Translate from/to",
                    iconPath  = "ui/actions/Properties Manager"\
                    "/Translate_Components.png",
                    spanWidth = True

                    )
        self.moveFromToButton.setCheckable(True)
        self.moveFromToButton.setAutoRaise(True)
        self.moveFromToButton.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon)


        self.startCoordLineEdit = PM_LineEdit(
            inPmGroupBox,
            label        = "ui/actions/Properties Manager"\
                    "/Move_Start_Point.png",
            text         = "Define 'from' and 'to' points",
            setAsDefault = False,
            )
        self.startCoordLineEdit.setReadOnly(True)
        self.startCoordLineEdit.setEnabled(False)

    def _loadByDeltaGroupBox(self, inPmGroupBox):
        """
        Load widgets in the translate By Delta group box, which is present
        within the Translate groupbox.
        @param inPmGroupBox: The Translate By Delta group box in the translate
                             group box.
        @type  inPmGroupBox: L{PM_GroupBox}
        """

        self.moveDeltaXSpinBox = \
            PM_DoubleSpinBox(
                inPmGroupBox,
                label        = "ui/actions/Properties Manager/Delta_X.png",
                value        = 0.0,
                setAsDefault = True,
                minimum      = -100.0,
                maximum      =  100.0,
                singleStep   = 1.0,
                decimals     = 3,
                suffix       = ' Angstroms',
                spanWidth    = False )

        self.moveDeltaYSpinBox = \
            PM_DoubleSpinBox(
                inPmGroupBox,
                label        = "ui/actions/Properties Manager/Delta_Y.png",
                value        = 0.0,
                setAsDefault = True,
                minimum      = -100.0,
                maximum      =  100.0,
                singleStep   = 1.0,
                decimals     = 3,
                suffix       = ' Angstroms',
                spanWidth    = False )

        self.moveDeltaZSpinBox = \
            PM_DoubleSpinBox(
                inPmGroupBox,
                label        = "ui/actions/Properties Manager/Delta_Z.png",
                value        = 0.0,
                setAsDefault = True,
                minimum      = -100.0,
                maximum      =  100.0,
                singleStep   = 1.0,
                decimals     = 3,
                suffix       = ' Angstroms',
                spanWidth    = False )

        DELTA_BUTTONS = [
                        ("QToolButton",1,  "Delta Plus",
                         "ui/actions/Properties Manager/Move_Delta_Plus.png",
                         "", "+", 0 ),

                        ( "QToolButton", 2,  "Delta Minus",
                          "ui/actions/Properties Manager/Move_Delta_Minus.png",
                          "", "-", 1 )
                        ]

        self.translateDeltaButtonRow = \
            PM_ToolButtonRow( inPmGroupBox,
                              title        = "",
                              buttonList   = DELTA_BUTTONS,
                              label        = 'Translate:',
                              isAutoRaise  =  True,
                              isCheckable  =  False
                            )
        self.transDeltaPlusButton = \
            self.translateDeltaButtonRow.getButtonById(1)
        self.transDeltaMinusButton = \
            self.translateDeltaButtonRow.getButtonById(2)


    def _loadToPositionGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Translate To a given Position group box, which is
        present within the Translate groupbox.
        @param inPmGroupBox: Translate To Position group box in the Translate
                             group box.
        @type  inPmGroupBox: L{PM_GroupBox}
        """

        self.toPositionspinboxes = PM_CoordinateSpinBoxes(inPmGroupBox)

        self.moveXSpinBox = self.toPositionspinboxes.xSpinBox
        self.moveYSpinBox = self.toPositionspinboxes.ySpinBox
        self.moveZSpinBox = self.toPositionspinboxes.zSpinBox


        self.moveAbsoluteButton = \
            PM_PushButton( inPmGroupBox,
                           label     = "",
                           text      = "Move Selection",
                           spanWidth = True )

    # == Begin Rotate Group Box =====================
    def _loadRotateGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Rotate group box,
        @param inPmGroupBox: The Rotate GroupBox in the PM
        @type  inPmGroupBox: L{PM_GroupBox}
        """

        rotateChoices = [ "Free Drag", "By Specified Angle"]

        self.rotateComboBox = \
            PM_ComboBox( inPmGroupBox,
                         label        = '',
                         choices      = rotateChoices,
                         index        = 0,
                         setAsDefault = False,
                         spanWidth    = True )

        self.rotateAsUnitCB = \
            PM_CheckBox( inPmGroupBox,
                         text         = 'Rotate as a unit' ,
                         widgetColumn = 0,
                         state        = Qt.Checked )


        self.freeDragRotateGroupBox = PM_GroupBox( inPmGroupBox )
        self._loadFreeDragRotateGroupBox(self.freeDragRotateGroupBox)

        self.bySpecifiedAngleGroupBox = PM_GroupBox( inPmGroupBox )
        self._loadBySpecifiedAngleGroupBox(self.bySpecifiedAngleGroupBox)

        self.updateRotateGroupBoxes(0)

    def _loadFreeDragRotateGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Free Drag Rotate group box, which is
        present within the Rotate groupbox.
        @param inPmGroupBox: The Free Drag Rotate group box in the Rotate
                             group box.
        @type  inPmGroupBox: L{PM_GroupBox}
        """
        # Button list to create a toolbutton row.
        # Format:
        # - buttonId,
        # - buttonText ,
        # - iconPath
        # - tooltip
        # - shortcut
        # - column

        BUTTON_LIST = [
            ( "QToolButton", 1,  "ROTATEDEFAULT",
              "ui/actions/Properties Manager/Rotate_Free.png", "", "F", 0 ),

            ( "QToolButton", 2,  "ROTATEX",
              "ui/actions/Properties Manager/RotateX.png", "", "X", 1 ),

            ( "QToolButton", 3,  "ROTATEY",
              "ui/actions/Properties Manager/RotateY.png", "", "Y", 2 ),

            ( "QToolButton", 4,  "ROTATEZ",
              "ui/actions/Properties Manager/RotateZ.png", "", "Z", 3 ),

            ( "QToolButton", 5,  "ROT_TRANS_ALONG_AXIS",
              "ui/actions/Properties Manager/translate+rotate-A.png", "", \
              "A", 4 )

            ]

        self.freeDragRotateButtonGroup = \
            PM_ToolButtonRow( inPmGroupBox,
                               title        = "",
                               buttonList   = BUTTON_LIST,
                               spanWidth = True,
                               checkedId    = 1,
                               setAsDefault = True,
                            )

        self.rotateFreeButton = self.freeDragRotateButtonGroup.getButtonById(1)
        self.rotateXButton    = self.freeDragRotateButtonGroup.getButtonById(2)
        self.rotateYButton    = self.freeDragRotateButtonGroup.getButtonById(3)
        self.rotateZButton    = self.freeDragRotateButtonGroup.getButtonById(4)
        self.rotAlongAxisButton = \
            self.freeDragRotateButtonGroup.getButtonById(5)

        inPmGroupBox.setStyleSheet(
            self.freeDragRotateButtonGroup._getStyleSheet())

        X_ROW_LABELS = [("QLabel", "Delta Theta X:", 0),
                        ("QLabel", "", 1),
                        ("QLabel", "0.00", 2),
                        ("QLabel", "Degrees", 3)]

        Y_ROW_LABELS = [("QLabel", "Delta Theta Y:", 0),
                        ("QLabel", "", 1),
                        ("QLabel", "0.00", 2),
                        ("QLabel", "Degrees", 3)]

        Z_ROW_LABELS = [("QLabel", "Delta Theta Z:", 0),
                        ("QLabel", "", 1),
                        ("QLabel", "0.00", 2),
                        ("QLabel", "Degrees", 3)]

        self.rotateXLabelRow = PM_LabelRow( inPmGroupBox,
                                            title = "",
                                            labelList = X_ROW_LABELS )
        self.deltaThetaX_lbl = self.rotateXLabelRow.labels[2]

        self.rotateYLabelRow = PM_LabelRow( inPmGroupBox,
                                            title = "",
                                            labelList = Y_ROW_LABELS )
        self.deltaThetaY_lbl = self.rotateYLabelRow.labels[2]

        self.rotateZLabelRow = PM_LabelRow( inPmGroupBox,
                                            title = "",
                                            labelList = Z_ROW_LABELS )
        self.deltaThetaZ_lbl = self.rotateZLabelRow.labels[2]

        self.rotateAboutPointButton = PM_ToolButton(
                    inPmGroupBox,
                    text = "Rotate selection about a point",
                    iconPath  = "ui/actions/Properties Manager"\
                    "/Rotate_Components.png",
                    spanWidth = True
                    )
        self.rotateAboutPointButton.setCheckable(True)
        self.rotateAboutPointButton.setAutoRaise(True)
        self.rotateAboutPointButton.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon)


        self.rotateStartCoordLineEdit = PM_LineEdit(
            inPmGroupBox,
            label        = "ui/actions/Properties Manager"\
                    "/Move_Start_Point.png",
            text         = "Define 3 points",
            setAsDefault = False,
            )
        self.rotateStartCoordLineEdit.setReadOnly(True)
        self.rotateStartCoordLineEdit.setEnabled(False)


    def _loadBySpecifiedAngleGroupBox(self, inPmGroupBox):
        """
        Load widgets in the Rotate By Specified Angle group box, which is
        present within the Rotate groupbox.
        @param inPmGroupBox: Rotate By Specified Angle group box in the Rotate
                             group box.
        @type  inPmGroupBox: L{PM_GroupBox}
        """
        # Button list to create a toolbutton row.
        # Format:
        # - buttonId,
        # - buttonText ,
        # - iconPath
        # - tooltip
        # - shortcut
        # - column

        BUTTON_LIST = [
            ( "QToolButton", 1,  "ROTATEX",
              "ui/actions/Properties Manager/RotateX.png",
              "Rotate about X axis", "X", 0 ),

            ( "QToolButton", 2,  "ROTATEY",
              "ui/actions/Properties Manager/RotateY.png",
              "Rotate about Y axis", "Y", 1 ),

            ( "QToolButton", 3,  "ROTATEZ",
              "ui/actions/Properties Manager/RotateZ.png",
              "Rotate about Z axis","Z", 2 ),
            ]



        self.rotateAroundAxisButtonRow = \
            PM_ToolButtonRow( inPmGroupBox,
                              title        = "",
                              buttonList   = BUTTON_LIST,
                              alignment    = 'Right',
                              label        = 'Rotate Around:'
                            )
        self.rotXaxisButton = \
            self.rotateAroundAxisButtonRow.getButtonById(1)

        self.rotYaxisButton = \
            self.rotateAroundAxisButtonRow.getButtonById(2)

        self.rotZaxisButton = \
            self.rotateAroundAxisButtonRow.getButtonById(3)



        self.rotateThetaSpinBox = \
            PM_DoubleSpinBox(inPmGroupBox,
                             label        = "Rotate By:",
                             value        = 0.0,
                             setAsDefault = True,
                             minimum      = 0,
                             maximum      = 360.0,
                             singleStep   = 1.0,
                             decimals     = 2,
                             suffix       = ' Degrees')


        THETA_BUTTONS = [
            ( "QToolButton", 1,  "Theta Plus",
              "ui/actions/Properties Manager/Move_Theta_Plus.png", "", "+", 0 ),

            ( "QToolButton", 2,  "Theta Minus",
              "ui/actions/Properties Manager/Move_Theta_Minus.png", "", "-", 1 )
            ]

        self.rotateThetaButtonRow = \
            PM_ToolButtonRow( inPmGroupBox,
                              title        = "",
                              buttonList   = THETA_BUTTONS,
                              label        = 'Direction:',
                              isAutoRaise  =  True,
                              isCheckable  =  False
                            )
        self.rotateThetaPlusButton =  self.rotateThetaButtonRow.getButtonById(1)
        self.rotateThetaMinusButton = self.rotateThetaButtonRow.getButtonById(2)

    # == End Rotate Group Box =====================

    # == Slots for Translate group box
    def _hideAllTranslateGroupBoxes(self):
        """
        Hides all Translate group boxes.
        """
        self.toPositionGroupBox.hide()
        self.byDeltaGroupBox.hide()
        self.freeDragTranslateGroupBox.hide()

    def updateTranslateGroupBoxes(self, id):
        """
        Update the translate group boxes displayed based on the translate
        option selected.
        @param id: Integer value corresponding to the combobox item in the
                   Translate group box.
        @type  id: int
        """
        self._hideAllTranslateGroupBoxes()

        if id is 0:
            self.freeDragTranslateGroupBox.show()

        if id is 1:
            self.byDeltaGroupBox.show()
        if id is 2:
            self.toPositionGroupBox.show()

        self.updateMessage()

    def changeMoveOption(self, button):
        """
        Subclasses should reimplement this method.

        @param button: QToolButton that decides the type of translate operation
        to be set.
        @type  button: QToolButton
                       L{http://doc.trolltech.com/4.2/qtoolbutton.html}
        @see: B{MovePropertyManager.changeMoveOption} which overrides this
              method
        """
        pass

    # == Slots for Rotate group box
    def updateRotateGroupBoxes(self, id):
        """
        Update the translate group boxes displayed based on the translate
        option selected.
        @param id: Integer value corresponding to the combobox item in the
                   Rotate group box.
        @type  id: int
        """
        if id is 0:
            self.bySpecifiedAngleGroupBox.hide()
            self.freeDragRotateGroupBox.show()
        if id is 1:
            self.freeDragRotateGroupBox.hide()
            self.bySpecifiedAngleGroupBox.show()

        self.updateMessage()

    def changeRotateOption(self, button):
        """
        Subclasses should reimplement this method.

        @param button: QToolButton that decides the type of rotate operation
        to be set.
        @type  button: QToolButton
                       L{http://doc.trolltech.com/4.2/qtoolbutton.html}
        @see: B{MovePropertyManage.changeRotateOption} which overrides this
             method
        """
        pass

    def _addWhatsThisText(self):
        """
        What's This text for some of the widgets in this Property Manager.

        """
        from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_MovePropertyManager
        whatsThis_MovePropertyManager(self)

    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.
        """
        from ne1_ui.ToolTipText_for_PropertyManagers import ToolTip_MovePropertyManager
        ToolTip_MovePropertyManager(self)

