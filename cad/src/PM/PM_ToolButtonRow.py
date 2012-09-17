# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_ToolButtonRow.py

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:

ninad 2007-08-07: Created.
ninad 2007-08-14: Changes due to the new superclass of PM_ToolButtonGrid.
"""

from PM.PM_ToolButtonGrid import PM_ToolButtonGrid


class PM_ToolButtonRow( PM_ToolButtonGrid ):
    """
    The PM_ToolButtonRow widget provides a row of tool buttons that function
    as an I{exclusive button group}.

    @see: B{Ui_MovePropertyManager} for an example of how this is used.

    """
    def __init__(self,
                 parentWidget,
                 title        = '',
                 buttonList   = [],
                 alignment    = None,
                 label        = '',
                 labelColumn  = 0,
                 spanWidth    = False,
                 checkedId    = -1,
                 setAsDefault = False,
                 isAutoRaise  = True,
                 isCheckable  = True
                 ):
        """
        Appends a PM_ToolButtonRow widget to the bottom of I{parentWidget},
        the Property Manager dialog or group box.

        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox

        @param title: The group box title.
        @type  title: str

        @param buttonList: A list of I{button info lists}. There is one button
                           info list for each button in the grid. The button
                           info list contains the following items:
                           (notice that this list doesn't contain the 'row'
                           which is seen in B{PM_ToolButtonGrid}.)
                            1. Button Type - in this case its 'ToolButton'(str),
                            2. Button Id (int),
                            3. Button text (str),
                            4. Button icon path (str),
                            5. Button tool tip (str),
                            6. Column (int).
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

        PM_ToolButtonGrid.__init__(self,
                                   parentWidget,
                                   title,
                                   buttonList,
                                   alignment,
                                   label,
                                   labelColumn,
                                   spanWidth,
                                   checkedId,
                                   setAsDefault,
                                   isAutoRaise,
                                   isCheckable)



    def getWidgetInfoList(self, buttonInfo):
        """
        Returns the button information provided by the user.
        Overrides the L{PM_WidgetGrid.getWidgetInfoList}
        This is used to set custom information (e.g. a fixed value for row)
        for the button.

        @param  buttonInfo: list containing the button information
        @type   buttonInfo: list

        @return: A list containing the button information.
                This can be same as I{buttonInfo} or can be modified further.
        @rtype:  list

        @see:   L{PM_WidgetGrid.getWidgetInfoList} (overrides this method)

        """

        buttonInfoList = []
        buttonType     = buttonInfo[0]
        buttonId       = buttonInfo[1]
        buttonText     = buttonInfo[2]
        buttonIconPath = buttonInfo[3]
        buttonToolTip  = buttonInfo[4]
        buttonShortcut = buttonInfo[5]
        column         = buttonInfo[6]
        row            = 0

        buttonInfoList = [
            buttonType,
            buttonId,
            buttonText,
            buttonIconPath,
            buttonToolTip,
            buttonShortcut,
            column,
            row]

        return buttonInfoList

    def _getStyleSheet(self):
        """
        Return the style sheet for the toolbutton row. This sets the following
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)

        @see: L{PM_GroupBox._getStyleSheet} (overrides this method)
        """
        #For a toolbutton row, we don't (usually) need  a borders . So set
        #the style sheet accordingly
        styleSheet = \
                   "QGroupBox {border-style:hidden; \
                    border-width: 0px; \
                    border-color: ""; \
                    border-radius: 0px; \
                    min-width: 10em; }"

        return styleSheet
