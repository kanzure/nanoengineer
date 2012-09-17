# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_RadioButtonList.py

@author: Mark Sims
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-08-05: Created.
"""

from PyQt4.Qt import QButtonGroup
from PyQt4.Qt import QRadioButton

from PM.PM_GroupBox import PM_GroupBox
from PyQt4.Qt import QLabel

class PM_RadioButtonList( PM_GroupBox ):
    """
    The PM_RadioButtonList widget provides a list of radio buttons that function
    as an I{exclusive button group}.
    """

    buttonList       = []
    defaultCheckedId = -1    # -1 means no checked Id
    setAsDefault     = True
    labelWidget      = None

    def __init__(self,
                 parentWidget,
                 title        = '',
                 label = '',
                 labelColumn = 0,
                 buttonList   = [],
                 checkedId    = -1,
                 setAsDefault = False,
                 spanWidth   = True,
                 borders = True
                 ):
        """
        Appends a PM_RadioButtonList widget to the bottom of I{parentWidget},
        the Property Manager dialog or group box.

        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox or PM_Dialog

        @param title: The group box title.
        @type  title: str

        @param label:      The label for the coordinate spinbox.
        @type  label:      str

        @param labelColumn: The column in the parentWidget's grid layout to
                            which this widget's label will be added.
                            The labelColum can only be E{0} or E{1}
        @type  labelColumn: int


        @param buttonList: A list of I{button info lists}. There is one button
                           info list for each radio button in the list. The
                           button info list contains the following three items:
                           1). Button Id (int),
                           2). Button text (str),
                           3). Button tool tip (str).
        @type  buttonList: list

        @param spanWidth: If True, the widget and its label will span the width
                         of the group box. Its label will appear directly above
                         the widget (unless the label is empty) and is left
                         justified.
        @type  spanWidth: bool (default False)


        @param borders: If true (default), this widget will have borders displayed.
                        otherwise the won't be any outside borders around the
                        set of radio buttons this class provides
        @type borders: boolean
        """

        # Intializing label, labelColumn etc is needed before doing
        # PM_GroupBox.__init__. This is done so that
        # self.parentWidget.addPmWidget(self) done at the end of __init__
        # works properly.
        # 'self.parentWidget.addPmWidget(self)' is done to avoid a bug where a
        # groupbox is always appended as the 'last widget' when its
        # parentWidget is also a groupbox. This is due to other PM widgets
        #(e.g. PM_PushButton)add themselves to their parent widget in their
        #__init__ using self.parentWidget.addPmWidget(self). So doing the
        #same thing here. More general fix is needed in PM_GroupBox code
        # --Ninad 2007-11-14 (comment copied from PM_coordinateSpinBoxes)
        self.label = label
        self.labelColumn = labelColumn
        self.spanWidth = spanWidth

        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)


        PM_GroupBox.__init__(self, parentWidget, title)

        # These are needed to properly maintain the height of the grid if
        # all buttons in a row are hidden via hide().
        self.vBoxLayout.setMargin(0)
        self.vBoxLayout.setSpacing(0)

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(True)

        self.parentWidget = parentWidget
        self.buttonList   = buttonList

        if setAsDefault:
            self.setDefaultCheckedId(checkedId)

        self.buttonsById   = {}
        self.buttonsByText = {}

        # Create radio button list from button info.
        for buttonInfo in buttonList:
            buttonId       = buttonInfo[0]
            buttonText     = buttonInfo[1]
            buttonToolTip  = buttonInfo[2]

            button = QRadioButton(self)

            button.setText(buttonText)
            button.setToolTip(buttonToolTip) # Not working.
            button.setCheckable(True)
            if checkedId == buttonId:
                button.setChecked(True)
            self.buttonGroup.addButton(button, buttonId)
            self.vBoxLayout.addWidget(button)

            self.buttonsById[buttonId]    = button
            self.buttonsByText[buttonText] = button

        if isinstance(self.parentWidget, PM_GroupBox):
            self.parentWidget.addPmWidget(self)
        else:
            #@@ Should self be added to self.parentWidget's widgetList?
            #don't know. Retaining old code -- Ninad 2008-06-23
            self._widgetList.append(self)
            self._rowCount += 1

        if not borders:
            #reset the style sheet so that there are no borders around the
            #radio button set this class provides.
            self.setStyleSheet(self._getAlternateStyleSheet())

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
        Returns the tool button group's checked button, or 0 if no buttons are
        checked.
        """
        return self.buttonGroup.checkedButton()

    def checkedId(self):
        """
        Returns the id of the checkedButton(), or -1 if no button is checked.
        """
        return self.buttonGroup.checkedId()

    def getButtonByText(self, text):
        """
        Returns the button with its current text set to I{text}.
        """
        if self.buttonsByText.has_key(text):
            return self.buttonsByText[text]
        else:
            return None

    def getButtonById(self, buttonId):
        """
        Returns the button with the button id of I{buttonId}.
        """
        if self.buttonsById.has_key(buttonId):
            return self.buttonsById[buttonId]
        else:
            return None


    def _getAlternateStyleSheet(self):
        """
        Return the style sheet for the groupbox. This sets the following
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)
        @see: L{PM_GroupBox._getStyleSheet} (overrided here)
        """

        styleSheet = "QGroupBox {border-style:hidden;\
        border-width: 0px;\
        border-color: "";\
        border-radius: 0px;\
        min-width: 10em; }"

        return styleSheet

# End of PM_RadioButtonList ############################