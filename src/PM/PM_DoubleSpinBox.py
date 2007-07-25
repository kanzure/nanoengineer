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
    QLabel for a Property Manager groupbox.
    """
    
    defaultValue = 0 # Default value of spinbox
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  value        = 0, 
                  setAsDefault = True,
                  minimum      = 0, 
                  maximum      = 99,
                  singleStep   = 1.0, 
                  decimals     = 1, 
                  suffix       = '',
                  spanWidth    = False ):
        """
        Appends a QDoubleSpinBox widget to <parentWidget>, a property manager groupbox.
        
        Arguments:
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: label that appears to the left (or above) of the SpinBox.
        @type  label: str
        
        @param value: initial value of SpinBox.
        @type  value: float
        
        @param setAsDefault: if True, will restore <value>
                         when the "Restore Defaults" button is clicked.
        @type  setAsDefault:
        
        @param minimum: minimum value in the SpinBox.
        @type  minimum: float
        
        @param maximum: maximum value in the SpinBox.
        @type  maximum: float
        
        @param decimals: precision of SpinBox.
        @type  decimals: int
        
        @param singleStep: increment/decrement value when user uses arrows.
        @type  singleStep:
        
        @param suffix: suffix.
        @type  suffix:
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth:
        
        """
        
        if 0: # Debugging code
            print "PropMgrSpinBox.__init__():"
            print "  label = ", label
            print "  value = ", value
            print "  setAsDefault = ", setAsDefault
            print "  minimum = ", minimum
            print "  maximum = ", maximum
            print "  singleStep = ", singleStep
            print "  decimals = ", decimals
            print "  suffix = ", suffix
            print "  spanWidth = ", spanWidth
        
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
        Set value of widget to <value>. If <setAsDefault> is True, 
        <value> becomes the default value for this widget so that
        "Restore Defaults" will reset this widget to <value>.
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
            

# End of PropMgrDoubleSpinBox ############################