# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_WidgetRow.py

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:

ninad 2007-08-09: Created.

@attention: This file is subject to heavy modifications. 
"""

from PM.PM_WidgetGrid import PM_WidgetGrid
from widgets.widget_helpers import QColor_to_Hex
from PM.PM_Colors import pmGrpBoxColor

class PM_WidgetRow( PM_WidgetGrid ):
    """
    The B{PM_WidgetRow} provides a convenient way to create different 
    types of widgets (such as ToolButtons, Labels, PushButtons etc) in a single
    row and add them to a groupbox. 
    
    #Example of how a caller creates a PM_WidgetRow object:
    
    # Format of the widget list that is passed to the widget row --        
        # - Widget type,
        # - Middle portion of any tuple in the list is either a widget object 
        #   or some other parameters if the widget object of 
        #   given type needs to be created by the PM_WidgetRow. For example--
        #   If widget type  is 'QLabel' , then it will be created by 
        #   PM_WidgetRow class and user just need to provide the text for the 
        #   QLabel. 
        # - column number (the last item in a tuple)
        
    aWidgetList = [('PM_ComboBox', self.latticeTypeComboBox, 0),
                   ('PM_PushButton', self.addLayerButton, 1),
                   ('QLabel', "Some Label", 2)  ]
        
    widgetRow = PM_WidgetRow(parentWidget,
                             title     = '',
                             widgetList = aWidgetList,
                             label = "Layer:",
                             labelColumn  = 0,
                             )
    @see: B{PM_WidgetGrid._createWidgetUsingParameters }
    @see: B{Ui_CookiePropertyManager._loadLayerPropertiesGroupBox} that uses 
          a B{PM_WidgetRow}
    
    """
    titleButtonRequested = False
            
    def __init__(self, 
                 parentWidget,
                 title     = '',
                 widgetList = [],  
                 alignment  = None,
                 label = '',
                 labelColumn = 0,
                 spanWidth   = False
                 ):
        
        """
        Appends a PM_WidgetRow (a group box widget) to the bottom of 
        I{parentWidget},the Property Manager Group box.
        
        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: L{PM_GroupBox}
        
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
        
        @param label:      The label for the widget row. .
        @type  label:      str
        
        @param labelColumn: The column in the parentWidget's grid layout to which
                            this widget's label will be added. The labelColum
                            can only be E{0} or E{1}
        @type  labelColumn: int
        
        @param spanWidth: If True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool (default False)
        
        """
                
        PM_WidgetGrid.__init__(self, 
                               parentWidget , 
                               title, 
                               widgetList,
                               alignment ,
                               label,
                               labelColumn,
                               spanWidth 
                              )
              
                         
    def getWidgetInfoList(self, widgetInfo):
        """
        Returns the label information provided by the user. 
        Overrides PM_LabelGrid.getLabelInfoList if they need to provide 
        custom information (e.g. a fixed value for row) .
        @param  labelInfo: list containing the label information
        @type   labelInfo: list
        @return : A list containing the label information. 
                This can be same as I{labelInfo} or can be modified further.
        @rtype  : list
        @see:   L{PM_WidgetGrid.getWidgetInfoList (this method is overridden 
        here)
        
        """        
        
        row    = 0        
        widgetInfoList = list(widgetInfo)
        widgetInfoList.append(row)
                          
        return widgetInfoList
    
    def _getStyleSheet(self):
        """
        Return the style sheet for the groupbox. This sets the following 
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)
         - background color
        @see: L{PM_GroupBox._getStyleSheet} (overrided here)
        """
        
        styleSheet = "QGroupBox {border-style:hidden; "\
        "border-width: 0px; "\
        "border-color: ""; "\
        "border-radius: 0px;"\
        "min-width: 10em; "\
        "background-color: #%s;"\
        "}" % ( QColor_to_Hex(pmGrpBoxColor))
                           
   
        return styleSheet
 