# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_WidgetGrid.py

@author: Ninad
@version: $Id:  $
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:

ninad 2007-08-14: Created. 
"""
import os

from PyQt4.Qt import QWidget
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QSpacerItem
from PyQt4.Qt import QSize
from PyQt4.Qt import QLabel
from PyQt4.Qt import QToolButton

from debug    import print_compact_traceback
from Utility  import geticon

from PM.PM_GroupBox import PM_GroupBox


class PM_WidgetGrid( PM_GroupBox ):
    """
    The B{PM_Widgetgrid} provides a convenient way to create different 
    types of widgets (such as ToolButtons, Labels, PushButtons etc) and 
    arrange them in the grid layout of a B{PM_Groupbox} 
    
    @see: B{Ui_MovePropertyManager} that uses B{PM_ToolButtonRow}, to create 
    custom widgets (toolbuttons) arranged in a grid layout. 
    """
       
    def __init__(self, 
                 parentWidget,
                 title     = '',
                 widgetList = [],
                 alignment = None,
                 label = '',
                 ):
        
        
        """
        Appends a PM_WidgetGrid (a group box widget) to the bottom of 
        I{parentWidget},the Property Manager Group box.
        
        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox 
        
        @param title: The group box title.
        @type  title: str
        
        @param widgetList: A list of I{widget info lists}. There is one widget
                           info list for each widget in the grid. The widget
                           info list contains custom information about the 
                           widget but the following items are always present:
                           - First Item       : Widget Type (str),
                           - Second Last Item : Column (int), 
                           - Last Item        : Row (int).
        @type  widgetList: list
        
        @param alignment:  The alignment of the widget row in the parent 
                           groupbox. Based on its value,spacer items is added 
                           to the grid layout of the parent groupbox. 
        @type  alignment:  str
        
        @param label:      The label for the widget row. If present, it is 
                           added to the same grid layout as the rest of the 
                           widgets on that row, in column number E{0}.
        @type  label:      str
        
       
        """
         
        
        self.label = label
        
        PM_GroupBox.__init__(self, parentWidget, title)
        
        # These are needed to properly maintain the height of the grid if 
        # all labels in a row are hidden via hide().
        self.vBoxLayout.setMargin(0)
        self.vBoxLayout.setSpacing(0)
        
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
                     
        self.parentWidget = parentWidget
        self.widgetList   = widgetList
                    
        self.alignment = alignment
        
        self.loadWidgets()
                 
    
    def loadWidgets(self):
        """
        Creates the widgets (or spacers) in a grid layout of a B{PM_GroupBox} 
        Then adds this group box to the grid layout of the I{parentWidget}, 
        which is again a B{PM_GroupBox} object.        
        """
        
        priviousRow = 0.0999 #initialize with some junk value. 
                            
        for widgetInfo in self.widgetList: 
            widgetInfoList = self.getWidgetInfoList(widgetInfo) 
            widgetParams = list(widgetInfoList[0:-2])
                        
            widgetOrSpacer = self._createWidgetUsingParameters(widgetParams) 
            
            column  = widgetInfoList[-2]
            row     = widgetInfoList[-1]
                                            
            #Following adds a label to the current row, in the same grid layout
            #as the rest of the widgets. If the label is specified, it is added 
            # to the column 0 of the current row. -- Ninad 20070814
                        
            if priviousRow != row and self.label:                
                label = QLabel(self.parentWidget)
                label.setText(self.label)                
                self.gridLayout.addWidget(label, row, 0, 1, 1)
                previousRow = row                  
            
            #Increment the column number by 1 if a label is specified 
            #@see: B{Ui_MovePropertyManager.rotateAroundAxisButtonRow} as an 
            #example. In this example, client code specifies the
            #tool buttons with column number starting at 0 as usual and then 
            #just specify the label argument. 
            
            if self.label:
                column += 1
        
            if widgetOrSpacer.__class__.__name__  ==  QSpacerItem.__name__:
                self.gridLayout.addItem( widgetOrSpacer,
                                       row,
                                       column,
                                       1,
                                       1 )
            else: 
                self.gridLayout.addWidget( widgetOrSpacer,
                                           row,
                                           column,
                                           1,
                                           1 )
                
        #Add the widget i.e., the PM_GroupBox, that contains all the widgets 
        # the client needs, to the grid layout of the parent groupbox
        self.addWidgetToParentGridLayout()
        
    def getWidgetInfoList(self, widgetInfo):
        """
        Returns the widget information provided by the user. 
        Subclasses should override this method if they need to provide 
        custom information (e.g. a fixed value for row) .
        @param  widgetInfo: A list containing the widget information
        @type   widgetInfo: list
        
        @return: A list containing custom widget information. 
                This can be same as I{widgetInfo} or can be modified further.
        @rtype: list
        @see:   B{PM_ToolButtonRow.getWidgetInfoList}
        
        """
        
        widgetInfoList = list(widgetInfo)
        return widgetInfoList
    
             
    def _createWidgetUsingParameters(self, widgetParams):
        """
        Returns a widget based on the I{widgetType} 
        
        Subclasses can override this method.
        
        @param widgetParams: A list containing widget's parameters. 
        @type  widgetParams: list
        
        @see: L{PM_ToolButtonGrid._createWidgetUsingParameters} which overrides
              this method.
        
        """        
        widgetParams = list(widgetParams)  
        
        widgetType = widgetParams[0]
        
        if widgetType == "ToolButton":
            widget = self._createToolButton(params)
        elif widgetType == "PushButton":
            widget = self._createPushButton(params)
        elif widgetType == "Label":
            widget = self._createLabel(params)
        elif widgetType == "Spacer":
            widget = self._createSpacer(params)
        else:
            msg1 = "Error, unknown/unsupported widget type. "
            msg2 = "Widget Grid can not be created"
            print_compact_traceback(msg1 + msg2)
            widget = None     
  
        return widget
    
    def _createToolButton(self, widgetParams):
        """
        Returns a tool button created using the custom parameters. 
                
        @param widgetParams: A list containing tool button parameters. 
        @type  widgetParams: list
        
        @see: L{self._createWidgetUsingParameters} where this method is called.
        """
        
        buttonSize = QSize(32, 32) #@ FOR TEST ONLY
        
        buttonParams = list(widgetParams)
        buttonId       = buttonParams[1]
        buttonText     = buttonParams[2]
        buttonIconPath = buttonParams[3]
        buttonToolTip  = buttonParams[4] 
                
        button = QToolButton(self)
        button.setText(buttonText)
        if os.path.exists(buttonIconPath):
            button.setIcon(geticon(buttonIconPath))
            button.setIconSize(QSize(22,22))
        button.setToolTip(buttonToolTip)
        button.setFixedSize(buttonSize) #@ Currently fixed to 32 x 32.
        button.setCheckable(True)
        return button
    
    
    def _createLabel(self, widgetParams):
        """
        Returns a label created using the custom parameters. 
                
        @param widgetParams: A list containing label parameters. 
        @type  widgetParams: list
        
        @see: L{self._createWidgetUsingParameters} where this method is called.
        """
        
        labelParams = list(widgetParams)        
        labelText        = labelParams[1]        
        label = QLabel(self)
        label.setText(labelText)
        return label
    
    
    
    # ==== Helper methods to add widgets/ spacers to the Grid Layout =====
    
    def addWidgetToParentGridLayout(self):
        """
        Adds this widget (groupbox) to the parent widget's grid layout. 
        ( The parent widget should be a groupbox)
        Example: If user specifies this widget's alignment as 'Center' then 
        it adds Left spacer, this widget and the right spacer to the 
        parentWidget's grid layout, in the current row. 
        This method also increments the row number of the parentWidget's grid 
        layout. 
        @see: L{self.loadWidgets} which calls this method
        
        """
        
        row = self.parentWidget._rowCount
        column = 0
               
        #Add Left spacer to the parentWidget's layout
        if self.alignment and self.alignment != 'Left':
            self._addAlignmentSpacer(row, column)
            column += 1

        #Add the widget to the parentWidget's layout
        self.parentWidget.gridLayout.addWidget(self, row, column, 1, 1)
                   
        #Add Right spacer to the parentWidget's layout
        if self.alignment and self.alignment != 'Right':
            self._addAlignmentSpacer(row, column + 1)
                    
        #Increment the paren widget's row count 
        self.parentWidget._rowCount += 1
                    
    def _addAlignmentSpacer(self, rowNumber, columnNumber):
        """
        Adds a alignment spacer to the parent widget's grid layout which also 
        contain this classes widget.
        @see: L{self.addWidgetToParentGridLayout} for an example on how it is 
              used.
        """
        row = rowNumber
        column = columnNumber
        spacer = QSpacerItem(10, 5, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        self.parentWidget.gridLayout.addItem( spacer, row, column, 1, 1 )
    