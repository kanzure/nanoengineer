# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_ToolButtonRow.py

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:

ninad 2007-08-07: Created.
"""

import os


from PM.PM_ToolButtonGrid import PM_ToolButtonGrid


class PM_ToolButtonRow( PM_ToolButtonGrid ):
    """
    The PM_ToolButtonRow widget provides a row of tool buttons that function
    as an I{exclusive button group}.
    
    @see: B{Ui_MovePropertyManager} for an example of how this is used.
    
    @todo: support for adding spacers to the tool button row
    """
    
    def __init__(self, 
                 parentWidget, 
                 title        = '', 
                 buttonList   = [],
                 checkedId    = -1, 
                 setAsDefault = False
                 ):
        """
        Appends a PM_ToolButtonRow widget to the bottom of I{parentWidget}, 
        the Property Manager dialog or group box.
        
        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox or PM_Dialog
        
        @param title: The group box title.
        @type  title: str
        
        @param buttonList: A list of I{button info lists}. There is one button
                           info list for each button in the grid. The button
                           info list contains the following five items:
                           (notice that this list doesn't contain the 'row' as an
                           item like in PM_ToolButtonGrid. 
                           1). Button Id (int), 
                           2). Button text (str),
                           3). Button icon path (str),
                           4). Column (int)
                           5). Button tool tip (str).
        @type  buttonList: list
        """
        
        PM_ToolButtonGrid.__init__(self, 
                                   parentWidget, 
                                   title,
                                   buttonList,
                                   checkedId,
                                   setAsDefault
                               )
                
    def getButtonInfoList(self, buttonInfo):
        """
        Returns the button information provided by the user. 
        Overrides the PM_ToolButtonRow.getButtonInfoList
        custom information (e.g. a fixed value for row) .
        @param  buttonInfo: list containing the button information
        @type   buttonInfo: list
        @return buttonInfoList: list containing the button information. 
                This can be same as I{buttonInfo} or can be modified further.
        @rtype  buttonInfoList: list
        @see:   PM_ToolButtonGrid.getButtonInfoList (overrides this method)
        
        """
                
        buttonId       = buttonInfo[0]
        buttonText     = buttonInfo[1]
        buttonIconPath = buttonInfo[2]
        column         = buttonInfo[3]
        row            = 0
        buttonToolTip  = buttonInfo[4] 
        
        buttonInfoList = [buttonId, buttonText, buttonIconPath,
                          column, row, buttonToolTip]
                          
        return buttonInfoList            
        
    def _getStyleSheet(self):
        """
        Return the style sheet for the groupbox. This sets the following 
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)
        @see: PM_GroupBox._getStyleSheet (overrided here)
        """
        
        styleSheet = "QGroupBox {border-style:hidden;\
        border-width: 0px;\
        border-color: "";\
        border-radius: 0px;\
        min-width: 10em; }" 
   
        return styleSheet