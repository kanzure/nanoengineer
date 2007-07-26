# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_DoubleSpinBox.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrDoubleSpinBox out of PropMgrBaseClass.py into this file
and renamed it PM_DoubleSpinBox.
"""

from PyQt4.Qt import QDoubleSpinBox
from PyQt4.Qt import QWidget

from PM_WidgetMixin import PM_WidgetMixin

class PM_DoubleSpinBox( QDoubleSpinBox, PM_WidgetMixin ):
    """
    The PM_DoubleSpinBox widget provides a QDoubleSpinBox (with an 
    optional label) for a Property Manager group box.
    
    Detailed Description
    ====================
    The PM_DoubleSpinBox class provides a spin box widget (with an
    optional label) for a 
    U{B{Property Manager dialog}<http://www.nanoengineer-1.net/mediawiki/
    index.php?title=Property_Manager>} 
    that takes floats.

    PM_DoubleSpinBox allows the user to choose a value by clicking the up and 
    down buttons or by pressing Up or Down on the keyboard to increase or 
    decrease the value currently displayed. The user can also type the value 
    in manually. The spin box supports float values but can be extended to 
    use different strings with validate(), textFromValue() and valueFromText().
    
    Every time the value changes PM_DoubleSpinBox emits the valueChanged() signal.
    The current value can be fetched with value() and set with setValue().
    
    Note: PM_DoubleSpinBox will round numbers so they can be displayed with the 
    current precision. In a PM_DoubleSpinBox with decimals set to 2, calling 
    setValue(2.555) will cause value() to return 2.56.
    
    Clicking the up and down buttons or using the keyboard accelerator's 
    Up and Down arrows will increase or decrease the current value in steps 
    of size singleStep(). If you want to change this behavior you can 
    reimplement the virtual function stepBy(). The minimum and maximum 
    value and the step size can be set using one of the constructors, 
    and can be changed later with setMinimum(), setMaximum() and 
    setSingleStep(). The spin box has a default precision of 2 decimal 
    places but this can be changed using setDecimals().
    
    Most spin boxes are directional, but PM_DoubleSpinBox can also operate 
    as a circular spin box, i.e. if the range is 0.0-99.9 and the current 
    value is 99.9, clicking "up" will give 0 if wrapping() is set to true. 
    Use setWrapping() if you want circular behavior.
    
    The displayed value can be prepended and appended with arbitrary strings 
    indicating, for example, currency or the unit of measurement. 
    See setPrefix() and setSuffix(). The text in the spin box is retrieved 
    with text() (which includes any prefix() and suffix()), or with 
    cleanText() (which has no prefix(), no suffix() and no leading or 
    trailing whitespace).
    
    It is often desirable to give the user a special (often default) choice
    in addition to the range of numeric values. See setSpecialValueText() 
    for how to do this with PM_DoubleSpinBox.
    
    @see: U{B{QDoubleSpinBox}<http://doc.trolltech.com/4/qdoublespinbox.html>}
    """
    
    defaultValue = 0.0 # Default value of the spin box.
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  value        = 0.0, 
                  setAsDefault = True,
                  minimum      = 0.0, 
                  maximum      = 99.0,
                  singleStep   = 1.0, 
                  decimals     = 1, 
                  suffix       = '',
                  spanWidth    = False ):
        """
        Appends a QDoubleSpinBox (Qt) widget to the bottom of I{parentWidget}, 
        a Property Manager group box.
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: The label that appears to the left of (or above) the 
                      spin box. To suppress the label, set I{label} to an 
                      empty string.
        @type  label: str
        
        @param value: The initial value of the spin box.
        @type  value: float
        
        @param setAsDefault: If True, will restore I{value} when the 
                             "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param minimum: The minimum value of the spin box.
        @type  minimum: float
        
        @param maximum: The maximum value of the spin box.
        @type  maximum: float
        
        @param decimals: The precision of the spin box.
        @type  decimals: int
        
        @param singleStep: When the user uses the arrows to change the 
                           spin box's value the value will be 
                           incremented/decremented by the amount of the 
                           singleStep. The default value is 1.0. 
                           Setting a singleStep value of less than 0 does 
                           nothing.
        @type  singleStep: int
        
        @param suffix: The suffix is appended to the end of the displayed value. 
                       Typical use is to display a unit of measurement. 
                       The default is no suffix. The suffix is not displayed for the minimum 
                       value if specialValueText() is set.
        @type  suffix: str
        
        @param spanWidth: If True, the spin box and its label will span the width
                          of the group box. The label will appear directly above
                          the spin box and is left justified. 
        @type  spanWidth: bool
        
        @see: U{B{QDoubleSpinBox}<http://doc.trolltech.com/4/qdoublespinbox.html>}
        """
        
        if 0: # Debugging code
            print "PropMgrSpinBox.__init__():"
            print "  label        = ", label
            print "  value        = ", value
            print "  setAsDefault = ", setAsDefault
            print "  minimum      = ", minimum
            print "  maximum      = ", maximum
            print "  singleStep   = ", singleStep
            print "  decimals     = ", decimals
            print "  suffix       = ", suffix
            print "  spanWidth    = ", spanWidth
        
        if not parentWidget:
            return
        
        QDoubleSpinBox.__init__(self)
        
        self.parentWidget = parentWidget
                        
        # Set QDoubleSpinBox minimum, maximum, singleStep, decimals, then value
        self.setRange(minimum, maximum)
        self.setSingleStep(singleStep)
        self.setDecimals(decimals)
        
        self.setValue(value) # This must come after setDecimals().
        
        if setAsDefault:
            self.setDefaultValue(value)
        
        # Add suffix if supplied.
        if suffix:
            self.setSuffix(suffix)
        
        self.addWidgetAndLabelToParent(parentWidget, label, spanWidth)
        
    def collapse( self ):
        """
        Hides the spin box (and its label) when its group box is collapsed.
        """
        QWidget.hide(self) # Hide self.
        if self.labelWidget :# Hide self's label if it has one.
            self.labelWidget.hide()
        
    def expand( self ):
        """
        Shows the spin box (and its label) when its group box is expanded,
        unless the spin box was hidden via L{hide()}.
        """
        if self.hidden: return
        QWidget.show(self) # Show self.
        if self.labelWidget: # Show self's label if it has text.
            self.labelWidget.show()
        
    def hide( self ):
        """
        Hide the spin box (and its label). If hidden, the spin box
        will not be displayed when its group box is expanded.
        Call L{show()} to unhide the spin box (and its label).
        
        @see: L{show()}
        """
        self.hidden = True
        QWidget.hide(self) # Hide the spin box.
        if self.labelWidget: 
            # Hide the spin box's label.
            self.labelWidget.hide() 
                    
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setValue(self.defaultValue)
    
    def setDefaultValue( self, value ):
        """
        Sets the default value of the spin box to I{value}. The current spin box
        value is unchanged.
                      
        @param value: The new default value of the spin box.
        @type  value: float
        
        @see: L{setValue}
        """
        self.setAsDefault = True
        self.defaultValue = value
            
    def setValue( self, value, setAsDefault = True ):
        """
        Sets the value of the spin box to I{value}. 
        
        setValue() will emit valueChanged() if the new value is different from the old one.
        
        Note: The value will be rounded so it can be displayed with the current setting of decimals.          
        
        @param value: The new spin box value.
        @type  value: float
        
        @param setAsDefault: Determines if the spin box value is reset when 
                             the "Restore Defaults" button is clicked. If True,
                             (the default) I{value} will be used as the reset 
                             value.
        @type  setAsDefault: bool
        
        @see: L{setDefaultValue}
        """
        if setAsDefault:
            self.setDefaultValue(value)
        QDoubleSpinBox.setValue(self, value)
        
    def show( self ):
        """
        Show the spin box (and its label if it has text).
        
        @see: L{hide()}
        """
        self.hidden = False
        QWidget.show(self) # Show the spin box.
        if self.labelWidget: 
            # Show the spin box's label if it has text.
            self.labelWidget.show()
        
    # End of PM_DoubleSpinBox ########################################