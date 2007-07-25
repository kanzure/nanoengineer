# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_LineEdit.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrLineEdit out of PropMgrBaseClass.py into this file
                 and renamed it PM_LineEdit.
"""

from PyQt4.Qt import QLineEdit

from PM_WidgetMixin import PM_WidgetMixin

class PM_LineEdit( QLineEdit, PM_WidgetMixin ):
    """
    The PM_LineEdit widget provides a QLineEdit with a QLabel for a 
    Property Manager group box.
    """
    
    defaultText = "" # Default value of lineedit
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  text         = '', 
                  setAsDefault = True,
                  spanWidth    = False ):
        """
        Appends a QLineEdit widget to <parentWidget>, a property manager group box.
        
        Arguments:
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: label that appears to the left of (or above) the widget.
        @type  label: str
        
        @param text: initial value of LineEdit widget.
        @type  text: str
        
        @param setAsDefault: if True, will restore <val> when the
                    "Restore Defaults" button is clicked.
        @type  spanWidth: bool
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool
        """
        
        if 0: # Debugging code
            print "PM_LineEdit.__init__():"
            print "  label = ", label
            print "  text = ", text
            print "  setAsDefault = ", setAsDefaultfix
            print "  spanWidth = ", spanWidth
                
        QLineEdit.__init__(self)
        
        self.parentWidget = parentWidget
                
        # Set QLineEdit text
        self.setText(text)
        
        # Set default value
        self.defaultText=text
        self.setAsDefault = setAsDefault
            
        self.addWidgetAndLabelToParent(parentWidget, label, spanWidth)
        
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setText(self.defaultText)

# End of PM_LineEdit ############################