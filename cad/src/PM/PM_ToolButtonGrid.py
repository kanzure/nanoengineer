# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_ToolButtonGrid.py

@author: Mark Sims
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-08-02: Created.
ninad 2007-08-14: New superclass PM_WidgetGrid. Related refactoring and cleanup.
"""

import sys

from PyQt4.Qt import QButtonGroup
from PyQt4.Qt import QFont
from PyQt4.Qt import QSize

from PM.PM_WidgetGrid import PM_WidgetGrid

BUTTON_FONT = "Arial"
BUTTON_FONT_BOLD = True

if sys.platform == "darwin":
    BUTTON_FONT_POINT_SIZE = 18
else: # Windows and Linux
    BUTTON_FONT_POINT_SIZE = 10

class PM_ToolButtonGrid( PM_WidgetGrid ):
    """
    The PM_ToolButtonGrid widget provides a grid of tool buttons that function
    as an I{exclusive button group}.

    @see: B{PM_ElementChooser} for an example of how this is used.

    @todo: Fix button size issue (e.g. all buttons are sized 32 x 32).
    """

    buttonList       = []
    defaultCheckedId = -1    # -1 means no checked Id
    setAsDefault     = True


    def __init__(self,
                 parentWidget,
                 title        = '',
                 buttonList   = [],
                 alignment    = None,
                 label        = '',
                 labelColumn = 0,
                 spanWidth   = True,
                 checkedId    = -1,
                 setAsDefault = False,
                 isAutoRaise  = False,
                 isCheckable  = True
                 ):
        """
        Appends a PM_ToolButtonGrid widget to the bottom of I{parentWidget},
        the Property Manager Group box.

        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox

        @param title: The group box title.
        @type  title: str

        @param buttonList: A list of I{button info lists}. There is one button
                           info list for each button in the grid. The button
                           info list contains the following items:
                           1. Button Type - in this case its 'ToolButton'(str),
                           2. Button Id (int),
                           3. Button text (str),
                           4. Button icon path (str),
                           5. Button tool tip (str),
                           6. Column (int),
                           7. Row (int).
        @type  buttonList: list

        @param alignment:  The alignment of the toolbutton row in the parent
                           groupbox. Based on its value,spacer items is added
                           to the grid layout of the parent groupbox.
        @type  alignment:  str

        @param label:      The label for the toolbutton row. If present, it is
                           added to the same grid layout as the rest of the
                           toolbuttons, in column number E{0}.
        @type  label:      str

        @param labelColumn: The column in the parentWidget's grid layout to which
                            this widget's label will be added. The labelColum
                            can only be E{0} or E{1}
        @type  labelColumn: int

        @param spanWidth: If True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool (default False)

        @param checkedId:  Checked button id in the button group. Default value
                           is -1 that implies no button is checked.
        @type  checkedId:  int

        @param setAsDefault: If True, sets the I{checkedId} specified by the
                            user as the  default checked
        @type  setAsDefault: boolean
        """

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(True)

        self.isAutoRaise = isAutoRaise
        self.isCheckable = isCheckable
        self.buttonsById   = {}
        self.buttonsByText = {}

        if setAsDefault:
            self.setDefaultCheckedId(checkedId)


        PM_WidgetGrid.__init__(self,
                               parentWidget ,
                               title,
                               buttonList,
                               alignment,
                               label,
                               labelColumn,
                               spanWidth
                              )


    def _createWidgetUsingParameters(self, widgetParams):
        """
        Returns a tool button created using the parameters specified by the user

        @param widgetParams: A list of label parameters. This is a modified
                             using the original list returned
                             by L{self.getWidgetInfoList}. The modified list
                             doesn't contain the row and column information.
        @type  widgetParams: list
        @see:  L{PM_WidgetGrid._createWidgetUsingParameters} (overrided in this
               method)
        @see:  L{PM_WidgetGrid.loadWidgets} which calls this method.

        """
        buttonFont = self.getButtonFont()
        buttonParams = list(widgetParams)

        button = self._createToolButton(buttonParams)

        buttonId = buttonParams[1]

        if self.defaultCheckedId == buttonId:
            button.setChecked(True)
        button.setFont(buttonFont)
        button.setAutoRaise(self.isAutoRaise)
        button.setCheckable(self.isCheckable)
        self.buttonGroup.addButton(button, buttonId)

        self.buttonsById[buttonId]    = button
        self.buttonsByText[str(button.text())] = button

        return button


    def getButtonFont(self):
        """
        Returns the font for the tool buttons in the grid.

        @return: Button font.
        @rtype:  U{B{QFont}<http://doc.trolltech.com/4/qfont.html>}
        """
        # Font for tool buttons.
        buttonFont = QFont(self.font())
        buttonFont.setFamily(BUTTON_FONT)
        buttonFont.setPointSize(BUTTON_FONT_POINT_SIZE)
        buttonFont.setBold(BUTTON_FONT_BOLD)
        return buttonFont

    def restoreDefault(self):
        """
        Restores the default checkedId.
        """
        if self.setAsDefault:
            for buttonInfo in self.buttonList:
                buttonId = buttonInfo[0]
                if buttonId == self.defaultCheckedId:
                    button = self.getButtonById(buttonId)
                    button.setChecked(True)
        return

    def setDefaultCheckedId(self, checkedId):
        """
        Sets the default checked id (button) to I{checkedId}. The current checked
        button is unchanged.

        @param checkedId: The new default id for the tool button group.
        @type  checkedId: int
        """
        self.setAsDefault = True
        self.defaultCheckedId = checkedId

    def checkedButton(self):
        """
        Returns the tool button group's checked button, or E{0} if no button is
        checked.
        @return: Checked tool button or E{0}
        @rtype:  instance of QToolButton  or int
        """
        return self.buttonGroup.checkedButton()

    def checkedId(self):
        """
        Returns the id of the checkedButton(), or -1 if no button is checked.

        @return: The checked button Id
        @rtype:  int
        """
        return self.buttonGroup.checkedId()

    def getButtonByText(self, text):
        """
        Returns the button with its current text set to I{text}.

        @return: The button, or B{None} if no button was found.
        @rtype:  U{B{QToolButton}<http://doc.trolltech.com/4/qtoolbutton.html>}

        @note: If multiple buttons have the same text, only the last one is returned.
        """
        if self.buttonsByText.has_key(text):
            return self.buttonsByText[text]
        else:
            return None

    def getButtonById(self, buttonId):
        """
        Returns the button with the button id of I{buttonId}.

        return: The button, or B{None} if no button was found.
        rtype:  U{B{QToolButton}<http://doc.trolltech.com/4/qtoolbutton.html>}
        """
        if self.buttonsById.has_key(buttonId):
            return self.buttonsById[buttonId]
        else:
            return None

    def setButtonSize(self, width = 32, height = 32):
        """
        """
        for btn in self.buttonGroup.buttons():
            btn.setFixedSize(QSize(width, height))


# End of PM_ToolButtonGrid ############################

