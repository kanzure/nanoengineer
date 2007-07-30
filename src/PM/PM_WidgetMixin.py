# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_WidgetMixin.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-23: Split PropMgrWidgetMixin out of PropMgrBaseClass.py into this file
and renamed it PM_WidgetMixin.
mark 2007-07-29: Deprecated. No longer used in the PM module.
"""

from PyQt4.Qt import QLabel
from PyQt4.Qt import QPalette
from PyQt4.Qt import QWidget

from PM_Constants import pmLeftAlignment
from PM_Constants import pmRightAlignment

class PM_WidgetMixin:
    """
    Property Manager widget mixin class.
    """ 
    
    # Set to True to always hide the widget, even when group box is expanded.
    hidden = False
    # The QLabel containing this widget's label.
    labelWidget = None
    # Set setAsDefault to False if "Restore Defaults" should not 
    # reset this widget's value to val.
    setAsDefault = True
    
    def getWidgetGridLayoutParams( self, label, row, spanWidth ):
        """
        PropMgr widget GridLayout helper function. 
        Given <label>, <row> and <spanWitdth>, this function returns
        all the parameters needed to place the widget (and its label)
        in the caller's group box grid layout.
        """
        
        if not spanWidth: 
            # This widget and its label are on the same row
            labelRow = row
            labelColumn = 0
            labelSpanCols = 1
            labelAlignment = pmRightAlignment
                
            widgetRow = row
            widgetColumn = 1
            widgetSpanCols = 1
            rowIncrement = 1
            
        else: # This widget spans the full width of the groupbox
            if label: # The label and widget are on separate rows.
                    
                # Set the label's row, column and alignment.
                labelRow = row
                labelColumn = 0
                labelSpanCols = 2
                labelAlignment = pmLeftAlignment
                    
                # Set this widget's row and column attrs.
                widgetRow = row + 1 # Widget is below the label.
                widgetColumn = 0
                widgetSpanCols = 2
                rowIncrement = 2
            else:  # No label. Just the widget.
                labelRow = labelColumn = labelSpanCols = labelAlignment = 0
                # Set this widget's row and column attrs.
                widgetRow = row
                widgetColumn = 0
                widgetSpanCols = 2
                rowIncrement = 1
                
        return widgetRow, widgetColumn, widgetSpanCols, rowIncrement, \
               labelRow, labelColumn, labelSpanCols, labelAlignment

    def addWidgetAndLabelToParent( self, parentWidget, label, spanWidth ):
        """
        Add this PM widget and its label to a group box.
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: the text for this widget's label. If <label> is
                      empty, no label will be added.
        @type  label: str
        
        @param spanWidth: if True, the widget and its label will span the width
                    of its group box. Its label will appear directly above
                    the widget (unless the label is empty) left justified.
        @type  spanWidth: bool
        """
        
        # A function that returns all the widget and label layout params.
        widgetRow, widgetColumn, widgetSpanCols, rowIncrement, \
        labelRow, labelColumn, labelSpanCols, labelAlignment = \
        self.getWidgetGridLayoutParams(label, parentWidget._rowCount, spanWidth)
        
        if label:
            # Create QLabel widget.
            self.labelWidget = QLabel()
            self.labelWidget.setAlignment(labelAlignment)
            self.labelWidget.setText(label)
            parentWidget.GridLayout.addWidget( self.labelWidget,
                                               labelRow, 0,
                                               1, labelSpanCols)
        else:
            self.labelWidget = None
        
        parentWidget.GridLayout.addWidget(self,
                                    widgetRow, widgetColumn,
                                    1, widgetSpanCols)
        parentWidget._widgetList.append(self)
        
        parentWidget._rowCount += rowIncrement
        
        self.setName()
        
    def setName( self , name = "" ):
        """
        Automatically assigns an object name for this PM widget in the form:
        
        'parentWidget / classname / widgetlabel'
        
        This name is useful for debugging purposes by calling self.objectName().
        """
            
        if self.labelWidget:
            label = "/'" + str(self.labelWidget.text()) + "'"
        else:
            label = ''
            
        if name:
            label = name
        
        groupBoxNumber = ''
        from PM_GroupBox import PM_GroupBox
        if isinstance(self, PM_GroupBox):
            groupBoxNumber = str(self.parentWidget._groupBoxCount)
            
        self.setObjectName(self.parentWidget.objectName() + 
                           "/" + str(self.__class__.__name__) + 
                           groupBoxNumber +
                           label)
        
    def getPalette( self, palette, colorRole, color ):
        """
        Assigns a color (based on color role) to palette and returns it.
        The color/color role is assigned to all color groups.
            
        @param palette: A palette. If palette is None, we create and return a new palette.
        @type  palette: QPalette
        
        @param colorRole: the Qt ColorRole
        @type  colorRole: Qt.ColorRole
        
        @param color: color
        @type  color: QColor
        
        @return: Returns the updated palette, or a new palette if none was supplied.
        @rtype : QPalette
        
        @see: QPalette.setColor()
        """
        if palette:
            pass # Make sure palette is QPalette.
        else:
            palette = QPalette()
                
        palette.setColor(colorRole, color)
        
        return palette
                    
    def hide( self ):
        """
        Hide this widget and its label. If hidden, the widget
        will not be displayed when its groupbox is expanded.
        Call show() to unhide this widget (and its label).
        """
        self.hidden = True
        QWidget.hide(self) # Hide self.
        if self.labelWidget: # Hide self's label if it has text.
            self.labelWidget.hide() 
        
        from PM_GroupBox import PM_GroupBox
        if isinstance(self, PM_GroupBox):
            # Change the spacer height to zero to "hide" it unless
            # self is the last GroupBox in the Property Manager.
            if self.VSpacerWidget:
                self.VSpacerWidget.changeSize(10, 0)
            
    def show( self ):
        """
        Show this widget and its label.
        """
        self.hidden = False
        QWidget.show(self) # Show self.
        if self.labelWidget: # Show self's label if it has text.
            self.labelWidget.show() 
            
        from PM_GroupBox import PM_GroupBox
        if isinstance(self, PM_GroupBox):
            # Reset the height of the VSpacerWidget, if this groupbox has one.
            if self.VSpacerWidget:
                self.VSpacerWidget.changeSize(10, self.VSpacerWidget.defaultHeight)
        
    def collapse( self ):
        """
        Hides this widget (and its label) when the groupbox is collapsed.
        """
        QWidget.hide(self) # Hide self.
        if self.labelWidget :# Hide self's label if it has one.
            self.labelWidget.hide()
        
    def expand( self ):
        """
        Shows this widget (and its label) when the groupbox is expanded,
        unless this widget is hidden (via its hidden attr).
        """
        if self.hidden: return
        QWidget.show(self) # Show self.
        if self.labelWidget: # Show self's label if it has text.
            self.labelWidget.show()