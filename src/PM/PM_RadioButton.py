# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_RadioButton.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrRadioButton out of PropMgrBaseClass.py into this file
                 and renamed it PM_RadioButton.
"""

from PyQt4.Qt import QRadioButton

from PM_WidgetMixin import PM_WidgetMixin

class PM_RadioButton( QRadioButton, PM_WidgetMixin ):
    """
    The PM_RadioButton widget provides a QRadioButton with a QLabel for a 
    Property Manager group box.
    """
    
    # Default text when "Restore Default" is clicked
    defaultText = ""
    
    def __init__( self, 
                  parentWidget, 
                  text         = '', 
                  setAsDefault = True,
                  spanWidth    = True ):
        """
        Appends a QRadioButton widget to <parentWidget>, a property manager groupbox.
        
        Arguments:
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param text: text displayed on the RadioButton.
        @type  text: str
        
        @param setAsDefault: if True, will restore <text> as the RadioButton's text
                             when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param spanWidth: if True, the widget will span the width
                          of the group box. 
        @type  spanWidth: bool
        
        """
        
        QRadioButton.__init__(self)
        
        self.parentWidget = parentWidget
        
        label = ''
        
        self.setText(text)
        # Set default text
        self.defaultText=text
        self.setAsDefault = setAsDefault
        
        self.setCheckable(True)
        
        self.addWidgetAndLabelToParent(parentWidget, label, spanWidth)
        
    def restoreDefault( self ):
        """
        Restores the default value.
        
        @warning: not implemented yet
        """
        print "PM_RadioButton.restoreDefault(): Not implemented yet."

# End of PM_RadioButton ############################