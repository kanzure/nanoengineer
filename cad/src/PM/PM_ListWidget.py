# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_ListWidget.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrListWidget out of PropMgrBaseClass.py into this 
file and renamed it PM_ListWidget.
"""

from PyQt4.Qt import QLabel
from PyQt4.Qt import QListWidget
from PyQt4.Qt import QWidget
from PyQt4.Qt import Qt
from PyQt4.Qt import QAbstractItemView

from utilities.debug import print_compact_traceback

class PM_ListWidget( QListWidget ):
    """
    The PM_ListWidget widget provides a QListWidget with a 
    QLabel for a Property Manager group box.
    
    @cvar defaultItems: The default list of items in the list widget.
    @type defaultItems: list
                          
    @cvar defaultRow: The default row of the list widget.
    @type defaultRow: int
    
    @cvar setAsDefault: Determines whether to reset the choices to 
                        I{defaultItems} and current row to I{defaultRow}
                        when the user clicks the "Restore Defaults" button.
    @type setAsDefault: bool
    
    @cvar labelWidget: The Qt label widget of this list widget.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """
    
    defaultRow   = 0
    defaultItems = []
    setAsDefault = True
    labelWidget  = None
    
    def __init__(self, 
                 parentWidget, 
                 label        = '', 
                 labelColumn  = 0,
                 items        = [], 
                 defaultRow   = 0, 
                 setAsDefault = True,
                 heightByRows = 6, 
                 spanWidth    = False
                 ):
        """     
        Appends a QListWidget (Qt) widget to the bottom of I{parentWidget}, 
        a Property Manager group box.
        
        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: The label that appears to the left or right of the 
                      checkbox. 
                      
                      If spanWidth is True, the label will be displayed on
                      its own row directly above the list widget.
                      
                      To suppress the label, set I{label} to an 
                      empty string.
        @type  label: str
        
        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left 
                            column) and 1 (right column). The default is 0 
                            (left column).
        @type  labelColumn: int
        
        @param items: list of items (strings) to be inserted in the widget.
        @type  items: list
        
        @param defaultRow: The default row (item) selected, where 0 is the first 
                           row.
        @type  defaultRow: int
        
        @param setAsDefault: If True, will restore <idx> as the current index
                         when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param heightByRows: The height of the list widget.
        @type  heightByRows: int
        
        @param spanWidth: If True, the widget and its label will span the width
                          of the group box. Its label will appear directly above
                          the widget (unless the label is empty) and is left 
                          justified.
        @type  spanWidth: bool
        
        @see: U{B{QListWidget}<http://doc.trolltech.com/4/qlistwidget.html>}
        """
        
        if 0: # Debugging code
            print "PM_ListWidget.__init__():"
            print "  label        = ", label
            print "  labelColumn  = ", labelColumn
            print "  items        = ", items
            print "  defaultRow   = ", defaultRow
            print "  setAsDefault = ", setAsDefault
            print "  heightByRows = ", heightByRows
            print "  spanWidth    = ", spanWidth
                
        QListWidget.__init__(self)
        
        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth
        
        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)
               
        # Load QComboBox widget choice items and set initial choice (index).           
        self.insertItems(0, items, setAsDefault)
        self.setCurrentRow(defaultRow, setAsDefault)
                
        # Set height of list widget.
        margin = self.fontMetrics().leading() * 2 # Mark 2007-05-28
        height = heightByRows * self.fontMetrics().lineSpacing() + margin
        self.setMaximumHeight(height)
                     
        
        #As of 2008-04-16, the items in any list widgets won't be sorted 
        #automatically. It can be changes by simply uncommentting the lines
        #below -- Ninad
        ##self.setSortingEnabled(True)
        ##self.sortItems() 
        
        self.setAlternatingRowColors(True)                        
        parentWidget.addPmWidget(self)
        
    def insertItems(self, row, items, setAsDefault = True):
        """
        Insert items of widget starting at <row>. 
        If <setAsDefault> is True, <items> become the default list of
        items for this widget. "Restore Defaults" will reset 
        the list of items to <items>.
        
        Note: <items> will always replace the list of current items
        in the widget. <row> is ignored. This is considered a bug.
        -- Mark 2007-06-04
        """
        if row <> 0:
            msg = "PM_ListWidget.insertItems(): <row> must be zero."\
                "See docstring for details:"
            print_compact_traceback(msg)
            return
            
        if setAsDefault:
            self.setAsDefault = setAsDefault
            self.defaultItems = items
        
        self.clear()
        QListWidget.insertItems(self, row, items)
        
    def setCurrentRow(self, row, setAsDefault = False ):
        """
        Select new row. 
        
        @param row: The new row to select.
        @type  row: int
        
        @param setAsDefault: If True, I{row} becomes the default row when
                             "Restore Defaults" is clicked.
        """
        if setAsDefault:
            self.setAsDefault = setAsDefault
            self.defaultRow   = row
        QListWidget.setCurrentRow(self, row)
        
    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.insertItems(0, self.defaultItems)
            self.setCurrentRow(self.defaultRow)
            ## self.clear()
            ## for choice in self.defaultChoices:
            ##     self.addItem(choice)
            ## self.setCurrentRow(self.defaultRow)
        
    def hide(self):
        """
        Hides the list widget and its label (if it has one).
        
        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget: 
            self.labelWidget.hide()
            
    def show(self):
        """
        Unhides the list widget and its label (if it has one).
        
        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget: 
            self.labelWidget.show()

# End of PM_ListWidget ############################