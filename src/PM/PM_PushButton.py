# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_PushButton.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrPushButton out of PropMgrBaseClass.py into this file
                 and renamed it PM_PushButton.
"""

from PyQt4.Qt import QPushButton

from PM_WidgetMixin import PM_WidgetMixin

class PM_PushButton( QPushButton, PM_WidgetMixin ):
    """
    The PM_PushButton widget provides a QPushButton with a QLabel for a 
    Property Manager group box.
    """

    # The default text when "Restore Default" is clicked.
    defaultText = ""
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  text         = '', 
                  setAsDefault = True,
                  spanWidth    = False ):
        """
        Appends a QPushButton widget to <parentWidget>, a property manager groupbox.
        
        Arguments:
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: label that appears to the left of (or above) the widget.
        @type  label: str
        
        @param text: text displayed on the button.
        @type  text: str
        
        @param setAsDefault: if True, will restore <text> as the button's text
                         when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool
        
        """
        
        if 0: # Debugging code
            print "PM_PushButton.__init__():"
            print "  label = ",label
            print "  text = ", text
            print "  setAsDefault = ", setAsDefault
            print "  spanWidth = ", spanWidth
        
        QPushButton.__init__(self)
        
        self.parentWidget = parentWidget
        
        # Set text
        self.setText(text)
        
        # Set default text
        self.defaultText=text
        self.setAsDefault = setAsDefault
        
        self.addWidgetAndLabelToParent(parentWidget, label, spanWidth)
        
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setText(self.defaultText)

# End of PM_PushButton ############################