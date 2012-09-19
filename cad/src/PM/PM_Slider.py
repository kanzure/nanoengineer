# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_Slider.py

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:

ninad 2007-08-21: Created.

"""
from PyQt4.Qt import Qt
from PyQt4.Qt import QSlider
from PyQt4.Qt import QLabel
from PyQt4.Qt import QWidget


class PM_Slider(QSlider):

    labelWidget = None

    def __init__( self,
                  parentWidget,
                  orientation  = None, ##Qt.Horizontal,
                  currentValue = 0,
                  minimum      = 0,
                  maximum      = 100,
                  label        = '',
                  labelColumn  = 0,
                  setAsDefault = True,
                  spanWidth    = True):
        """

        Appends a Qslider widget (with a QLabel widget) to <parentWidget>
        a property manager group box.

        Arguments:

        @param parentWidget: the group box containing this PM widget.
        @type  parentWidget: PM_GroupBox

        @param currentValue:
        @type  currentValue: int

        @param minimum: minimum value the slider can get.
              (used to set its 'range')
        @type  minimum: int

        @param maximum: maximum value the slider can get.
              (used to set its 'range')
        @type  maximum: int

        @param label: label that appears to the left of (or above) this widget.
        @type  label: str

        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left
                            column) and 1 (right column). The default is 0
                            (left column).
        @type  labelColumn: int


        @param setAsDefault: if True, will restore value when the
               "Restore Defaults" button is clicked.
        @type  setAsDefault: bool (default True)

        @param spanWidth: If True, the widget and its label will span the width
                    of the group box. Its label will appear directly above
                    the widget (unless the label is empty)and is left justified.
        @type  spanWidth: bool (default True)

        @see: U{B{QSlider}<http://doc.trolltech.com/4/qslider.html>}

        """

        ##QSlider.__init__(self, orientation, parentWidget)
        QSlider.__init__(self, parentWidget)

        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth

        #Ideally, this should be simply self.setOrientation(orientation)  with the
        #default orientation = Qt.Horizontal in the init argument itself. But,
        #apparently pylint chokes up when init argument is a Qt enum.
        #This problem happened while running pylint 0.23 on the SEMBOT server
        #so comitting this temporary workaround. The pylint on my machine is
        #0.25 and it runs fine even before this workaround. Similar changes made
        #in PM_CheckBox. -- Ninad 2008-06-30
        if orientation is None:
            self.setOrientation(Qt.Horizontal)
        else:
            self.setOrientation(orientation)

        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)

        self.setValue(currentValue)
        self.setRange(minimum, maximum)

        self.setAsDefault   = setAsDefault

        if self.setAsDefault:
            self.setDefaultValue(currentValue)

        parentWidget.addPmWidget(self)



    def hide(self):
        """
        Hides the slider and its label (if it has one).

        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget:
            self.labelWidget.hide()

    def show(self):
        """
        Unhides the slider and its label (if it has one).

        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()

    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setValue(self.defaultValue)


    def setDefaultValue(self, value):
        """
        Sets the Default value for the slider. This value will be set if
        user hits Restore Defaults button in the Property Manager.
        """
        self.defaultValue = value
        self.setAsDefault = True
