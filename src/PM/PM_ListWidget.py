# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_ListWidget.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrListWidget out of PropMgrBaseClass.py into this file
                 and renamed it PM_ListWidget.
"""

from PyQt4.Qt import QListWidget

from PM_WidgetMixin import PM_WidgetMixin

class PM_ListWidget( QListWidget, PM_WidgetMixin ):
    """
    PropMgr ListWidget class, for groupboxes (PropMgrGroupBox) only.
    """
    
    # The default row when "Restore Defaults" is clicked
    defaultRow = 0
    # The list of items when "Restore Defaults" is clicked.
    defaultItems = []
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  items        = [], 
                  row          = 0, 
                  setAsDefault = True,
                  numRows      = 6, 
                  spanWidth    = False ):
        """
        Appends a QListWidget widget to <parentWidget>, a property manager groupbox.
        
        Arguments:
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: the label of this widget.
        @type  label: str
        
        @param items: list of items (strings) to be inserted in the widget.
        @type  items: list
        
        @param row: current row. (0=first item)
        @type  row: int
        
        @param setAsDefault: if True, will restore <idx> as the current index
                         when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param numRows: the number of rows to display. If <items> is 
                 greater than <numRows>, a scrollbar will be displayed.
        @type  numRows: int
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool
        
        """
        
        if 0: # Debugging code
            print "PM_ListWidget.__init__():"
            print "  label = ",label
            print "  items = ", items
            print "  row = ",row
            print "  setAsDefault = ", setAsDefault
            print "  numRows = ",numRows
            print "  spanWidth = ", spanWidth
                
        QListWidget.__init__(self)
        
        self.parentWidget = parentWidget
               
        # Load QComboBox widget choices and set initial choice (index).
        #for choice in choices:
        #    self.addItem(choice)
            
        self.insertItems(0, items, setAsDefault)
        self.setCurrentRow(row, setAsDefault)
        
        # Need setChoices() method 
        #self.defaultChoices=choices
        
        # Set height
        margin = self.fontMetrics().leading() * 2 # Mark 2007-05-28
        height = numRows * self.fontMetrics().lineSpacing() + margin
        self.setMaximumHeight(height)
        
        self.addWidgetAndLabelToParent(parentWidget, label, spanWidth)
        
    def insertItems( self, row, items, setAsDefault = True ):
        """
        Insert items of widget starting at <row>. 
        If <setAsDefault> is True, <items> become the default list of
        items for this widget. "Restore Defaults" will reset 
        the list of items to <items>.
        
        Note: <items> will always replace the list of current items
        in the widget. <row> is ignored. This is considered a bug. Mark 2007-06-04
        """
        
        if row <> 0:
            msg = "PM_ListWidget.insertItems(): <row> must be zero. See docstring for details:"
            print_compact_traceback(msg)
            return
            
        if setAsDefault:
            self.setAsDefault = setAsDefault
            self.defaultItems=items
        
        self.clear()
        QListWidget.insertItems(self, row, items)
        
    def setCurrentRow( self, row, setAsDefault = True ):
        """
        Set current row of widget to <row>. If <setAsDefault> is True, 
        <row> becomes the default row for this widget so that
        "Restore Defaults" will reset this widget to <row>.
        """
        if setAsDefault:
            self.setAsDefault = setAsDefault
            self.defaultRow=row
        QListWidget.setCurrentRow(self, row)
        
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.insertItems(0, self.defaultItems)
            self.setCurrentRow(self.defaultRow)
            '''
            self.clear()
            for choice in self.defaultChoices:
                self.addItem(choice)
            self.setCurrentRow(self.defaultRow)
            '''

# End of PM_ListWidget ############################