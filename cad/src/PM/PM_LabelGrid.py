# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_LabelGrid.py

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:

ninad 2007-08-14: Created.
"""

from PyQt4.Qt import QFont

from PM.PM_WidgetGrid import PM_WidgetGrid


class PM_LabelGrid( PM_WidgetGrid ):
    """
    The PM_LabelGrid widget (a groupbox) provides a grid of labels arranged in
    the  grid layout of the PM_LabelGrid

    @see: B{Ui_MovePropertyManager} for an example of how this is used.

    """

    def __init__(self,
                 parentWidget,
                 title     = '',
                 labelList = [],
                 alignment = None,
                 isBold    = False
                 ):
        """
        Appends a PM_LabelGrid widget ( a groupbox) to the bottom of I{parentWidget},
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
                           4. Row (int).
        @type  labelList: list
        """

        self.isBold = isBold

        #Empty list that will contain all the labels in this widget.
        self.labels = []

        PM_WidgetGrid.__init__(self,
                               parentWidget ,
                               title,
                               labelList,
                               alignment)

    def _createWidgetUsingParameters(self, widgetParams):
        """
        Returns a label created using the parameters specified by the user

        @param widgetParams: A list of label parameters. This is a modified
                             using the original list returned
                             by L{self.getWidgetInfoList}. The modified list
                             doesn't contain the row and column information.
        @type  widgetParams: list
        @see:  L{PM_WidgetGrid._createWidgetUsingParameters} (overrided in this
               method)
        @see:  L{PM_WidgetGrid.loadWidgets} which calls this method.

        """
        labelParams  = list(widgetParams)
        label = self._createLabel(labelParams)
        labelFont = self.getLabelFont(self.isBold)
        label.setFont(labelFont)
        label.setUpdatesEnabled(True)
        self.labels.append(label)
        return label


    def getLabelFont(self, isBold = False):
        """
        Returns the font for the labels in the grid
        """
        # Font for labels.
        labelFont = QFont(self.font())
        labelFont.setBold(False)
        return labelFont

    def setBold(self, isBold = True):
        """
        Sets or unsets font of all labels in this widget to bold
        @param isBold: If true, sets the font of all labels in the widget to
                       bold.
        @type  isBold: bool
        @see:  B{MovePropertyManager.updateRotationDeltaLabels} for an example
               on how this function is used.
        """

        for label in self.labels:
            font = QFont(label.font())
            font.setBold(isBold)
            label.setFont(font)
