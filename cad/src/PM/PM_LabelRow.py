# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_LabelRow.py

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:

ninad 2007-08-14: Created.
"""

from PM.PM_LabelGrid import PM_LabelGrid

class PM_LabelRow( PM_LabelGrid ):
    """
    The PM_LabelRow widget (a groupbox) provides a grid of labels arranged on the
    same row of the grid layout of the PM_LabelRow

    @see: B{Ui_MovePropertyManager} for an example of how this is used.

    """

    def __init__(self,
                 parentWidget,
                 title     = '',
                 labelList = [],
                 alignment = None,
                 isBold = False
                 ):
        """
        Appends a PM_LabelRow widget ( a groupbox) to the bottom of I{parentWidget},
        the Property Manager Group box.

        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox

        @param title: The group box title.
        @type  title: str

        @param labelList: A list of I{label info lists}. There is one label
                           info list for each label in the grid. The label
                           info list contains the following items:
                           1. Widget Type - in this case its 'Label'(str),
                           2. Label text (str),
                           3. Column (int),
        @type  labelList: list
        """

        PM_LabelGrid.__init__(self,
                              parentWidget ,
                              title,
                              labelList,
                              alignment,
                              isBold)



    def getWidgetInfoList(self, labelInfo):
        """
        Returns the label information provided by the user.
        Overrides PM_LabelGrid.getLabelInfoList if they need to provide
        custom information (e.g. a fixed value for row) .
        @param  labelInfo: list containing the label information
        @type   labelInfo: list
        @return : A list containing the label information.
                This can be same as I{labelInfo} or can be modified further.
        @rtype  : list
        @see:   L{PM_WidgetGrid.getWidgetInfoList (this method is overridden
        here)

        """
        widgetType       = labelInfo[0]
        labelText        = labelInfo[1]
        column           = labelInfo[2]
        row              = 0

        labelInfoList = [widgetType, labelText, column, row]

        return labelInfoList

    def _getStyleSheet(self):
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
