# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_WidgetGrid.py

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:

ninad 2007-08-14: Created.
"""


from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QSpacerItem
from PyQt4.Qt import QSize
from PyQt4.Qt import QLabel
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QPushButton

from utilities.debug import print_compact_traceback
from utilities.icon_utilities import geticon

from PM.PM_GroupBox import PM_GroupBox

from mock import Mock

class PM_WidgetGrid( PM_GroupBox ):
    """
    The B{PM_WidgetGrid} provides a convenient way to create different
    types of widgets (such as ToolButtons, Labels, PushButtons etc) and
    arrange them in the grid layout of a B{PM_Groupbox}

    @see: B{Ui_MovePropertyManager} that uses B{PM_ToolButtonRow}, to create
    custom widgets (toolbuttons) arranged in a grid layout.

    """
    __metaclass__ = Mock()

    def __init__(self,
                 parentWidget,
                 title     = '',
                 widgetList = [],
                 alignment = None,
                 label = '',
                 labelColumn = 0,
                 spanWidth   = True
                 ):


        """
        Appends a PM_WidgetGrid (a group box widget) to the bottom of
        I{parentWidget},the Property Manager Group box.

        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox

        @param title: The group box title.
        @type  title: str

        @param widgetList: A list of I{widget info lists}. There is one widget
                           info list for each widget in the grid. The widget
                           info list contains custom information about the
                           widget but the following items are always present:
                           - First Item       : Widget Type (str),
                           - Second Last Item : Column (int),
                           - Last Item        : Row (int).
        @type  widgetList: list

        @param alignment:  The alignment of the widget row in the parent
                           groupbox. Based on its value,spacer items is added
                           to the grid layout of the parent groupbox.
        @type  alignment:  str

        @param label:      The label for the widget row. .
        @type  label:      str

        @param labelColumn: The column in the parentWidget's grid layout to
                            which this widget's label will be added.
                            The labelColum can only be E{0} or E{1}
        @type  labelColumn: int

        @param spanWidth: If True, the widget and its label will span the width
                         of the group box. Its label will appear directly above
                         the widget (unless the label is empty) and is left
                         justified.
        @type  spanWidth: bool (default False)


        """


        self.label = label
        self.labelColumn = labelColumn
        self.spanWidth = spanWidth

        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)

        PM_GroupBox.__init__(self, parentWidget, title)

        # These are needed to properly maintain the height of the grid if
        # all labels in a row are hidden via hide().
        self.vBoxLayout.setMargin(0)
        self.vBoxLayout.setSpacing(0)

        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)

        self.parentWidget = parentWidget
        self.widgetList   = widgetList

        self.alignment = alignment

        self.loadWidgets()

    def loadWidgets(self):
        """
        Creates the widgets (or spacers) in a grid layout of a B{PM_GroupBox}
        Then adds this group box to the grid layout of the I{parentWidget},
        which is again a B{PM_GroupBox} object.
        """

        for widgetInfo in self.widgetList:
            widgetInfoList = self.getWidgetInfoList(widgetInfo)
            widgetParams = list(widgetInfoList[0:-2])

            widgetOrSpacer = self._createWidgetUsingParameters(widgetParams)

            column  = widgetInfoList[-2]
            row     = widgetInfoList[-1]


            if widgetOrSpacer.__class__.__name__  ==  QSpacerItem.__name__:
                self.gridLayout.addItem( widgetOrSpacer,
                                       row,
                                       column,
                                       1,
                                       1 )
            else:
                self.gridLayout.addWidget( widgetOrSpacer,
                                           row,
                                           column,
                                           1,
                                           1 )


        self.parentWidget.addPmWidget(self)

    def getWidgetInfoList(self, widgetInfo):
        """
        Returns the widget information provided by the user.
        Subclasses should override this method if they need to provide
        custom information (e.g. a fixed value for row) .
        @param  widgetInfo: A list containing the widget information
        @type   widgetInfo: list

        @return: A list containing custom widget information.
                This can be same as I{widgetInfo} or can be modified further.
        @rtype: list
        @see:   B{PM_ToolButtonRow.getWidgetInfoList}

        """

        widgetInfoList = list(widgetInfo)
        return widgetInfoList


    def _createWidgetUsingParameters(self, widgetParams):
        """
        Returns a widget based on the I{widgetType}

        Subclasses can override this method.

        @param widgetParams: A list containing widget's parameters.
        @type  widgetParams: list

        @see: L{PM_ToolButtonGrid._createWidgetUsingParameters} which overrides
              this method.

        """
        widgetParams = list(widgetParams)

        widgetType = str(widgetParams[0])


        if widgetType[0:3] == "PM_":
            #The given widget is already defined using a class in PM_Module
            #so simply use the specified object
            #@see:Ui_BuildCrystal_PropertyManager._loadLayerPropertiesGroupBox
            #      for an example on how it is used.
            widget = widgetParams[1]
            return widget

        if widgetType == QToolButton.__name__:
            widget = self._createToolButton(widgetParams)
        elif widgetType == QPushButton.__name__:
            widget = self._createPushButton(widgetParams)
        elif widgetType == QLabel.__name__:
            widget = self._createLabel(widgetParams)
        elif widgetType == QSpacerItem.__name__:
            widget = self._createSpacer(widgetParams)
        else:
            msg1 = "Error, unknown/unsupported widget type. "
            msg2 = "Widget Grid can not be created"
            print_compact_traceback(msg1 + msg2)
            widget = None

        return widget

    def _createToolButton(self, widgetParams):
        """
        Returns a tool button created using the custom parameters.

        @param widgetParams: A list containing tool button parameters.
        @type  widgetParams: list

        @see: L{self._createWidgetUsingParameters} where this method is called.
        """

        buttonSize = QSize(32, 32) #@ FOR TEST ONLY

        buttonParams = list(widgetParams)
        buttonId       = buttonParams[1]
        buttonText     = buttonParams[2]
        buttonIconPath = buttonParams[3]
        buttonToolTip  = buttonParams[4]
        buttonShortcut = buttonParams[5]

        button = QToolButton(self)
        button.setText(buttonText)
        if buttonIconPath:
            buttonIcon = geticon(buttonIconPath)
            if not buttonIcon.isNull():
                button.setIcon(buttonIcon)
                button.setIconSize(QSize(22, 22))
        button.setToolTip(buttonToolTip)
        if buttonShortcut:
            button.setShortcut(buttonShortcut)

        button.setFixedSize(buttonSize) #@ Currently fixed to 32 x 32.
        button.setCheckable(True)
        return button


    def _createLabel(self, widgetParams):
        """
        Returns a label created using the custom parameters.

        @param widgetParams: A list containing label parameters.
        @type  widgetParams: list

        @see: L{self._createWidgetUsingParameters} where this method is called.
        """

        labelParams = list(widgetParams)
        labelText   = labelParams[1]
        label = QLabel(self)
        label.setText(labelText)
        return label

    def _createSpacer(self, widgetParams):
        """
        Returns a QSpacerItem created using the custom parameters.

        @param widgetParams: A list containing spacer parameters.
        @type  widgetParams: list

        @see: L{self._createWidgetUsingParameters} where this method is called.
        """
        spacerParams = list(widgetParams)
        spacerWidth = spacerParams[1]
        spacerHeight = spacerParams[2]

        spacer = QSpacerItem(spacerWidth,
                             spacerHeight,
                             QSizePolicy.MinimumExpanding,
                             QSizePolicy.Minimum
                         )
        return spacer




    # ==== Helper methods to add widgets/ spacers to the Grid Layout =====
    # NOTE:  Following helper methods ARE NOT used as of 2007-08-16. These will
    # be deleted or modified when a new HBoxLayout is introduced to the Groupbox
    #-- Ninad 2007-08-16

    def addWidgetToParentGridLayout(self):
        """
        Adds this widget (groupbox) to the parent widget's grid layout.
        ( The parent widget should be a groupbox)
        Example: If user specifies this widget's alignment as 'Center' then
        it adds Left spacer, this widget and the right spacer to the
        parentWidget's grid layout, in the current row.
        This method also increments the row number of the parentWidget's grid
        layout.
        @see: L{self.loadWidgets} which calls this method

        """

        row = self.parentWidget.getRowCount()
        column = 0

        #Add Left spacer to the parentWidget's layout
        if self.alignment and self.alignment != 'Left':
            self._addAlignmentSpacer(row, column)
            column += 1

        #Add the widget to the parentWidget's layout
        self.parentWidget.gridLayout.addWidget(self, row, column, 1, 1)

        #Add Right spacer to the parentWidget's layout
        if self.alignment and self.alignment != 'Right':
            self._addAlignmentSpacer(row, column + 1)

        #Increment the parent widget's row count
        self.parentWidget.incrementRowCount()

    def _addAlignmentSpacer(self, rowNumber, columnNumber):
        """
        Adds a alignment spacer to the parent widget's grid layout which also
        contain this classes widget.
        @see: L{self.addWidgetToParentGridLayout} for an example on how it is
              used.
        """
        row = rowNumber
        column = columnNumber
        spacer = QSpacerItem(10, 5, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.parentWidget.gridLayout.addItem( spacer, row, column, 1, 1 )

