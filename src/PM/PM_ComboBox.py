# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_ComboBox.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrComboBox out of PropMgrBaseClass.py into this file
                 and renamed it PM_ComboBox.
"""

from PyQt4.Qt import QComboBox
from PM_WidgetMixin import PM_WidgetMixin

class PM_ComboBox( QComboBox, PM_WidgetMixin ):
    """
    The PM_ComboBox widget provides a QComboBox with a 
    QLabel for a Property Manager groupbox.
    """
    
    # The default index when "Restore Defaults" is clicked
    defaultIndex = 0
    # The default choices when "Restore Defaults" is clicked.
    defaultChoices = []
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  choices      = [],
                  index        = 0, 
                  setAsDefault = True,
                  spanWidth    = False ):
        """
        Appends a QComboBox widget (with a QLabel widget) to <parentWidget>, 
        a property manager group box.
        
        Arguments:
        
        @param parentWidget: the group box containing this PM widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: label that appears to the left of (or above) this PM widget.
        @type  label: str
        
        @param choices: list of combo box choices (strings).
        @type  choices: list
        
        @param index: initial index (choice) of combobox. (0=first item)
        @type  index: int (default 0)
        
        @param setAsDefault: if True, will restore <index> as the current index
                         when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool (default True)
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool (default False)
        """
        
        if 0: # Debugging code
            print "PM_ComboBox.__init__():"
            print "  label=",label
            print "  choices =", choices
            print "  index =", index
            print "  setAsDefault =", setAsDefault
            print "  spanWidth =", spanWidth
        
        QComboBox.__init__(self)
        
        self.parentWidget = parentWidget
                       
        # Load QComboBox widget choices and set initial choice (index).
        for choice in choices:
            self.addItem(choice)
        self.setCurrentIndex(index)
        
        # Set default index
        self.defaultIndex=index
        self.defaultChoices=choices
        self.setAsDefault = setAsDefault
        
        self.addWidgetAndLabelToParent(parentWidget, label, spanWidth)
            
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.clear() # Generates signals!
            for choice in self.defaultChoices:
                self.addItem(choice)
            self.setCurrentIndex(self.defaultIndex)

# End of PM_ComboBox ############################