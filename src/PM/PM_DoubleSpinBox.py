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

from PM_WidgetMixin import PM_WidgetMixin

class PM_DoubleSpinBox( QDoubleSpinBox, PM_WidgetMixin ):
    """
    The PM_DoubleSpinBox widget provides a QDoubleSpinBox with a 
    QLabel for a Property Manager group box.
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
        Appends a QDoubleSpinBox (Qt) widget to I{parentWidget}, 
        a Property Manager group box.
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: The label that appears to the left of (or above) the 
                      spin box. To suppress the label, set I{label} to an 
                      empty string.
        @type  label: str
        
        @param value: initial value of the spin box.
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
        
        # Add suffix if supplied.
        if suffix:
            self.setSuffix(suffix)
        
        self.addWidgetAndLabelToParent(parentWidget, label, spanWidth)
        
    def setValue( self, value, setAsDefault = True ):
        """
        Sets the value of the spin box to I{value}. 
        
        setValue() will emit valueChanged() if the new value is different from the old one.
        
        Note: The value will be rounded so it can be displayed with the current setting of decimals.          
        
        @param value: The new spin box value.
        @type  value: float
        
        @param setAsDefault: If True, will restore I{value} when the 
                             "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        """
        if setAsDefault:
            self.setAsDefault = True
            self.defaultValue = value
        QDoubleSpinBox.setValue(self, value)
        
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setValue(self.defaultValue)
        
    # End of PM_DoubleSpinBox ########################################