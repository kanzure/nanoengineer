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

from PyQt4.Qt import QSpinBox

from PM_WidgetMixin import PM_WidgetMixin

class PM_SpinBox( QSpinBox, PM_WidgetMixin ):
    """
    The PM_SpinBox widget provides a QSpinBox with a QLabel for a 
    Property Manager group box.
    """

    defaultValue = 0 # Default value of spinbox.
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  value        = 0, 
                  setAsDefault = True,
                  minimum      = 0, 
                  maximum      = 99,
                  suffix       = '',
                  spanWidth    = False ):
        """
        Appends a QSpinBox widget to <parentWidget>, a property manager group box.
        
        Arguments:
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: the label of this widget.
        @type  label: str
        
        @param value: the initial value of the spin box.
        @type  value: int
        
        @param setAsDefault: if True, will restore <value> as the spin box 
                         value when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param minimum: the minimum value of the spin box. The default value is 0.
        @type  minimum: int
        
        @param maximum: the maximum value of the spin box. The default value is 99.
        @type  maximum: int
        
        @param suffix: the suffix of the spin box.
        @type  suffix: string
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool
        """
        
        if 0: # Debugging code
            print "PM_SpinBox.__init__():"
            print "  label= ", label
            print "  value = ", value
            print "  setAsDefault = ", setAsDefault
            print "  minimum = ", minimum
            print "  maximum = ", maximum
            print "  suffix = ", suffix
            print "  spanWidth = ", spanWidth
        
        QSpinBox.__init__(self)
        
        self.parentWidget = parentWidget
                
        # Set QSpinBox minimum, maximum and initial value
        self.setRange(minimum, maximum)
        self.setValue(value)
        
        # Set default value
        self.defaultValue = value
        self.setAsDefault = setAsDefault
        
        # Add suffix if supplied.
        if suffix:
            self.setSuffix(suffix)
            
        self.addWidgetAndLabelToParent(parentWidget, label, spanWidth)
    
    def setValue(self, value, setAsDefault=True):
        """
        Set value of widget to <value>. If <setAsDefault> is True, 
        <value> becomes the default value for this widget so that
        "Restore Defaults" will reset this widget to <value>.
        """
        if setAsDefault:
            self.setAsDefault = True
            self.defaultValue = value
        QSpinBox.setValue(self, value)
        
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setValue(self.defaultValue)
        
# End of PM_SpinBox ############################