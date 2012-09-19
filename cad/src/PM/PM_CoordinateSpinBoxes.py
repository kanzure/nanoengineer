# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_CoordinateSpinBoxes.py

The PM_CoordinateSpinBoxes class provides a groupbox containing the three
coordinate spinboxes.

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

@TODO: Need to implement connectWidgetWithState when that API is formalized.

"""

from PyQt4.Qt            import QLabel
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox


class PM_CoordinateSpinBoxes(PM_GroupBox):
    """
    The PM_CoordinateSpinBoxes class provides a groupbox containing the three
    coordinate spinboxes.
    @see: L{Ui_BuildAtomsPropertyManager._loadSelectedAtomPosGroupBox} for
          an example.
    """
    def __init__(self,
                 parentWidget,
                 title = "",
                 label = '',
                 labelColumn = 0,
                 spanWidth   = True
                 ):
        """
        Appends a PM_CoordinateSpinBoxes groupbox widget to I{parentWidget},
        a L{PM_Groupbox} or a L{PM_Dialog}

        @param parentWidget: The parent groupbox or dialog (Property manager)
                             containing this  widget.
        @type  parentWidget: L{PM_GroupBox} or L{PM_Dialog}

        @param title: The title (button) text.
        @type  title: str

        @param label:      The label for the coordinate spinbox.
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
        # --Ninad 2007-11-14
        self.label = label
        self.labelColumn = labelColumn
        self.spanWidth = spanWidth

        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)

        PM_GroupBox.__init__(self, parentWidget, title)

        #Initialize attributes
        self.xSpinBox = None
        self.ySpinBox = None
        self.zSpinBox = None

        self._loadCoordinateSpinBoxes()

        self.parentWidget.addPmWidget(self)

    def _loadCoordinateSpinBoxes(self):
        """
        Load the coordinateSpinboxes groupbox with the x, y, z spinboxes
        """
         # User input to specify x-coordinate
        self.xSpinBox  =  \
            PM_DoubleSpinBox( self,
                              label         =  \
                              "ui/actions/Properties Manager/X_Coordinate.png",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  - 9999999,
                              maximum       =  9999999,
                              singleStep    =  1,
                              decimals      =  3,
                              suffix        =  " A")


        # User input to specify y-coordinate
        self.ySpinBox  =  \
            PM_DoubleSpinBox( self,
                              label         =  \
                              "ui/actions/Properties Manager/Y_Coordinate.png",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  - 9999999,
                              maximum       =  9999999,
                              singleStep    =  1,
                              decimals      =  3,
                              suffix        =  " A")

        # User input to specify z-coordinate
        self.zSpinBox  =  \
            PM_DoubleSpinBox( self,
                              label         =  \
                              "ui/actions/Properties Manager/Z_Coordinate.png",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  - 9999999,
                              maximum       =  9999999,
                              singleStep    =  1,
                              decimals      =  3,
                              suffix        =  " A")

    def _zgetStyleSheet(self):
        """
        Return the style sheet for the groupbox. This sets the following
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)
        For PM_CoordinateSpinBoxes groupbox, we typically don't want the border
        around the groupbox. If client needs a border, it should be explicitly
        defined and set there.
        @see: L{PM_GroupBox._getStyleSheet} (overrided here)
        """

        styleSheet = "QGroupBox {border-style:hidden;\
        border-width: 0px;\
        border-color: "";\
        border-radius: 0px;\
        min-width: 10em; }"

        return styleSheet


