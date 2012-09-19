# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_SpinBox.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrSpinBox out of PropMgrBaseClass.py into this file
and renamed it PM_SpinBox.
"""

from PyQt4.Qt import QLabel
from PyQt4.Qt import QSpinBox
from PyQt4.Qt import QWidget

class PM_SpinBox( QSpinBox ):
    """
    The PM_SpinBox widget provides a QSpinBox (with an
    optional label) for a Property Manager group box.

    Detailed Description
    ====================
    The PM_SpinBox class provides a spin box widget (with an
    optional label) for a
    U{B{Property Manager dialog}<http://www.nanoengineer-1.net/mediawiki/
    index.php?title=Property_Manager>}.

    PM_SpinBox is designed to handle integers and discrete sets of values
    (e.g., month names); use PM_DoubleSpinBox for floating point values.

    PM_SpinBox allows the user to choose a value by clicking the up/down buttons
    or pressing up/down on the keyboard to increase/decrease the value currently
    displayed. The user can also type the value in manually. The spin box
    supports integer values but can be extended to use different strings with
    validate(), textFromValue() and valueFromText().

    Every time the value changes PM_SpinBox emits the valueChanged() signals.
    The current value can be fetched with value() and set with setValue().

    Clicking the up/down buttons or using the keyboard accelerator's up and down
    arrows will increase or decrease the current value in steps of size
    singleStep(). If you want to change this behaviour you can reimplement the
    virtual function stepBy(). The minimum and maximum value and the step size
    can be set using one of the constructors, and can be changed later with
    setMinimum(), setMaximum() and setSingleStep().

    Most spin boxes are directional, but PM_SpinBox can also operate as a circular
    spin box, i.e. if the range is 0-99 and the current value is 99, clicking
    "up" will give 0 if wrapping() is set to true. Use setWrapping() if you want
    circular behavior.

    The displayed value can be prepended and appended with arbitrary strings
    indicating, for example, currency or the unit of measurement. See
    setPrefix() and setSuffix(). The text in the spin box is retrieved with
    text() (which includes any prefix() and suffix()), or with cleanText()
    (which has no prefix(), no suffix() and no leading or trailing whitespace).

    It is often desirable to give the user a special (often default) choice
    in addition to the range of numeric values. See setSpecialValueText() for
    how to do this with QSpinBox.

    @see: U{B{QSpinBox}<http://doc.trolltech.com/4/qspinbox.html>}

    @cvar defaultValue: The default value of the spin box.
    @type defaultValue: int

    @cvar setAsDefault: Determines whether to reset the value of the
                        spin box to I{defaultValue} when the user clicks
                        the "Restore Defaults" button.
    @type setAsDefault: bool

    @cvar labelWidget: The Qt label widget of this spin box.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """

    defaultValue = 0
    setAsDefault = True
    labelWidget  = None

    def __init__(self,
                 parentWidget,
                 label        = '',
                 labelColumn  = 0,
                 value        = 0,
                 setAsDefault = True,
                 minimum      = 0,
                 maximum      = 99,
                 singleStep   = 1,
                 suffix       = '',
                 spanWidth    = False
                 ):
        """
        Appends a QSpinBox (Qt) widget to the bottom of I{parentWidget},
        a Property Manager group box.

        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox

        @param label: The label that appears to the left of (or above) the
                      spin box. If label contains the relative path to an
                      icon (.png) file, that icon image will be used for the
                      label.

                      If spanWidth is True, the label will be displayed on
                      its own row directly above the spin box.

                      To suppress the label, set I{label} to an empty string.
        @type  label: str

        @param value: The initial value of the spin box.
        @type  value: int

        @param setAsDefault: Determines if the spin box value is reset when
                             the "Restore Defaults" button is clicked. If True,
                             (the default) I{value} will be used as the reset
                             value.
        @type  setAsDefault: bool

        @param minimum: The minimum value of the spin box.
        @type  minimum: int

        @param maximum: The maximum value of the spin box.
        @type  maximum: int

        @param singleStep: When the user uses the arrows to change the
                           spin box's value the value will be
                           incremented/decremented by the amount of the
                           singleStep. The default value is 1.
                           Setting a singleStep value of less than 0 does
                           nothing.
        @type  singleStep: int

        @param suffix: The suffix is appended to the end of the displayed value.
                       Typical use is to display a unit of measurement.
                       The default is no suffix. The suffix is not displayed
                       for the minimum value if specialValueText() is set.
        @type  suffix: str

        @param spanWidth: If True, the spin box and its label will span the
                          width of the group box. The label will appear
                          directly above the spin box and is left justified.
        @type  spanWidth: bool

        @see: U{B{QSpinBox}<http://doc.trolltech.com/4/qspinbox.html>}
        """

        if 0: # Debugging code
            print "PM_SpinBox.__init__():"
            print "  label        = ", label
            print "  labelColumn  = ", labelColumn
            print "  value        = ", value
            print "  setAsDefault = ", setAsDefault
            print "  minimum      = ", minimum
            print "  maximum      = ", maximum
            print "  singleStep   = ", singleStep
            print "  suffix       = ", suffix
            print "  spanWidth    = ", spanWidth

        QSpinBox.__init__(self)

        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth

        self._suppress_valueChanged_signal = False

        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)

        # Set QSpinBox minimum, maximum and initial value
        self.setRange(minimum, maximum)
        self.setSingleStep(singleStep)
        self.setValue(value)

        # Set default value
        self.defaultValue = value
        self.setAsDefault = setAsDefault

        # Add suffix if supplied.
        if suffix:
            self.setSuffix(suffix)

        parentWidget.addPmWidget(self)

    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setValue(self.defaultValue)

    def setDefaultValue(self, value):
        """
        Sets the default value of the spin box to I{value}. The current spin box
        value is unchanged.

        @param value: The new default value of the spin box.
        @type  value: int

        @see: L{setValue}
        """
        self.setAsDefault = True
        self.defaultValue = value

    def setValue(self, value,
                 setAsDefault = True,
                 blockSignals = False):
        """
        Sets the value of the spin box to I{value}.

        setValue() will emit valueChanged() if the new value is different from
        the old one.  (and if blockSignals flag is False)

        @param value: The new spin box value.
        @type  value: int

        @param setAsDefault: Determines if the spin box value is reset when
                             the "Restore Defaults" button is clicked. If True,
                             (the default) I{value} will be used as the reset
                             value.
        @type  setAsDefault: bool

        @param blockSignals: Many times, the caller just wants to setValue
                             and don't want to send valueChanged signal.
                             If this flag is set to True, the valueChanged
                             signal won't be emitted.  The default value is
                             False.
        @type  blockSignals: bool

        @see: L{setDefaultValue}
        @see: QObject.blockSignals(bool block)

        @see: B{InsertNanotube_PropertyManager._chiralityFixup()} for an example
              use of blockSignals flag

        """
        #If blockSignals flag is True, the valueChanged signal won't be emitted
        #This is done by self.blockSignals method below.  -- Ninad 2008-08-13
        self.blockSignals(blockSignals)

        if setAsDefault:
            self.setDefaultValue(value)
        QSpinBox.setValue(self, value)

        #Make sure to always 'unblock' signals that might have been temporarily
        #blocked before calling superclass.setValue.
        self.blockSignals(False)


    def hide(self):
        """
        Hides the spin box and its label (if it has one).

        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget:
            self.labelWidget.hide()

    def show(self):
        """
        Unhides the spin box and its label (if it has one).

        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()



# End of PM_SpinBox ############################