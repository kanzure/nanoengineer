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
    
    @cvar hidden: Hide flag.
    @type hidden: bool
    
    @cvar labelWidget: The Qt label widget of this list widget.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """
    
    defaultRow   = 0
    defaultItems = []
    setAsDefault = True
    hidden       = False
    labelWidget  = None
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  labelColumn  = 0,
                  items        = [], 
                  row          = 0, 
                  setAsDefault = True,
                  numRows      = 6, 
                  spanWidth    = False ):
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
        
        @see: U{B{QListWidget}<http://doc.trolltech.com/4/qlistwidget.html>}
        """
        
        if 0: # Debugging code
            print "PM_ListWidget.__init__():"
            print "  label        = ", label
            print "  labelColumn  = ", labelColumn
            print "  items        = ", items
            print "  row          = ", row
            print "  setAsDefault = ", setAsDefault
            print "  numRows      = ", numRows
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
        self.setCurrentRow(row, setAsDefault)
        
        # Need setChoices() method 
        #self.defaultChoices=choices
        
        # Set height of list widget.
        margin = self.fontMetrics().leading() * 2 # Mark 2007-05-28
        height = numRows * self.fontMetrics().lineSpacing() + margin
        self.setMaximumHeight(height)
        
        parentWidget.addPmWidget(self)
        
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
            
    def collapse( self ):
        """
        Hides the list widget and its label (if it has one) when its group box 
        is collapsed.
        """
        QWidget.hide(self) 
        if self.labelWidget :
            self.labelWidget.hide()
        
    def expand( self ):
        """
        Displays the list widget and its label (if it has one) when its group 
        box is expanded, unless the list widget was "permanently" hidden via
        L{hide()}. In that case, the list widget will remain hidden until 
        L{show()} is called.
        """
        if self.hidden: return
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()
        
    def hide( self ):
        """
        Hides the list widget and its label (if it has one). If hidden, the 
        list widget will not be displayed when its group box is expanded.
        Call L{show()} to unhide the list widget.
        
        @see: L{show}
        """
        self.hidden = True
        QWidget.hide(self)
        if self.labelWidget: 
            self.labelWidget.hide()
            
    def show( self ):
        """
        Unhide the list widget and its label (if it has one). The list widget
        will remain (temporarily) hidden if its group box is collapsed, 
        but will be displayed again when the group box is expanded.
        
        @see: L{hide}
        """
        self.hidden = False
        QWidget.show(self)
        if self.labelWidget: 
            self.labelWidget.show()

# End of PM_ListWidget ############################