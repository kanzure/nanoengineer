# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
PM_Dial.py

@author: Mark
@version: $Id$
@copyright: 2008 Nanorex, Inc.  All rights reserved.

History:

piotr 2008-07-29: Created this file.

"""

from PyQt4.Qt import QDial
from PyQt4.Qt import QLabel
from PyQt4.Qt import QWidget

from widgets.prefs_widgets import widget_connectWithState
from widgets.prefs_widgets import set_metainfo_from_stateref

class PM_Dial( QDial ):
    """
    The PM_Dial widget provides a QDial (with an
    optional label) for a Property Manager group box.
    """

    defaultValue = 0.0
    setAsDefault = True
    labelWidget  = None

    def __init__(self,
                 parentWidget,
                 label        = '',
                 suffix       = '',
                 labelColumn  = 1,
                 value        = 0.0,
                 setAsDefault = True,
                 minimum      = 0.0,
                 maximum      = 360.0,
                 notchSize    = 1,
                 notchTarget  = 10.0,
                 notchesVisible = True,
                 wrapping     = True,
                 spanWidth    = True
                 ):
        """
        Appends a QDial (Qt) widget to the bottom of I{parentWidget},
        a Property Manager group box.

        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox

        @see: U{B{QDial}<http://doc.trolltech.com/4/qdial.html>}
        """

        if not parentWidget:
            return

        QDial.__init__(self)

        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth
        self.suffix = suffix

        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.updateValueLabel()
            self.labelWidget.setText(self.value_label)

        # Set QDial minimum, maximum, then value
        self.setRange(minimum, maximum)

        self.setValue(value) # This must come after setDecimals().

        if setAsDefault:
            self.setDefaultValue(value)

        self.notchSize = notchSize
        self.setNotchTarget(notchTarget)
        self.setNotchesVisible(notchesVisible)
        self.setWrapping(wrapping)

        parentWidget.addPmWidget(self)

    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setValue(self.defaultValue)

    def setDefaultValue(self, value):
        """
        Sets the default value of the dial to I{value}. The current dial
        value is unchanged.

        @param value: The new default value of the dial.
        @type  value: float

        @see: L{setValue}
        """
        self.setAsDefault = True
        self.defaultValue = value

    def setValue(self, value, setAsDefault = True):
        """
        Sets the value of the dial to I{value}.

        setValue() will emit valueChanged() if the new value is different from
        the old one.

        @param value: The new dial value.
        @type  value: float

##        @param setAsDefault: Determines if the dial value is reset when
##                             the "Restore Defaults" button is clicked. If True,
##                             (the default) I{value} will be used as the reset
##                             value.
##        @type  setAsDefault: bool

        @note: The value will be rounded so it can be displayed with the current
        setting of decimals.

        @see: L{setDefaultValue}
        """

        QDial.setValue(self, value)
        self.updateValueLabel()

    def updateValueLabel(self):
        """
        Updates a widget's label with a value.
        """
        if self.label:
            self.value_label = "   " + self.label + " " + \
                "%-4d" % int(self.value()) + " " + self.suffix
            self.labelWidget.setText(self.value_label)

    def connectWithState(self, stateref,
                         set_metainfo = True,
                         debug_metainfo = False):
        """
        Connect self to the state referred to by stateref,
        so changes to self's value change that state's value
        and vice versa. By default, also set self's metainfo
        to correspond to what the stateref provides.

        @param stateref: a reference to state of type double,
                         which meets the state-reference interface StateRef_API.
        @type stateref: StateRef_API

        @param set_metainfo: whether to also set defaultValue, minimum,
        and/or maximum, if these are provided by the stateref. (This
        list of metainfo attributes will probably be extended.)

        @type set_metainfo: bool

        @param debug_metainfo: whether to print debug messages
        about the actions taken by set_metainfo, when it's true.

        @type debug_metainfo: bool
        """
        if set_metainfo:
            # Do this first, so old min/max don't prevent setting the
            # correct current value when we connect new state.
            #
            # REVIEW: the conventions for expressing a lack of
            # minimum, maximum, or defaultValue, either on self
            # or on the stateref, may need revision, so it's not
            # ambiguous whether the stateref knows the minimum (etc)
            # should be unset on self or doesn't care what it's set to.
            # Ideally, some explicit value of stateref.minimum
            # would correspond to "no minimum" (i.e. a minimum of
            # negative infinity), etc.
            # [bruce 070926]
            set_metainfo_from_stateref( self.setMinimum, stateref, 'minimum',
                                        debug_metainfo)
            set_metainfo_from_stateref( self.setMaximum, stateref, 'maximum',
                                        debug_metainfo)
            set_metainfo_from_stateref( self.setDefaultValue,
                                        stateref,
                                        'defaultValue',
                                        debug_metainfo)
        ###widget_connectWithState( self, stateref,
        ###                        QDoubleSpinBox_ConnectionWithState)
        print "PM_Dial.connectWithState: not yet implemented" #bruce 080811 added this line
        return

    def hide( self ):
        """
        Hides the dial and its label (if it has one).
        Call L{show()} to unhide the dial.

        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget:
            self.labelWidget.hide()

    def show( self ):
        """
        Unhides the dial and its label (if it has one).

        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()

    # End of PM_Dial ########################################
