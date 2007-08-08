# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_ToolButtonGrid.py

@author: Mark Sims
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-08-02: Created.
"""

import sys
import os

from Utility import geticon

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QButtonGroup
from PyQt4.Qt import QFont
from PyQt4.Qt import QLabel
from PyQt4.Qt import QSize
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QWidget
from PyQt4.Qt import Qt

from PM.PM_GroupBox import PM_GroupBox

BUTTON_HEIGHT = 32
BUTTON_WIDTH = 32
BUTTON_FONT = "Arial"
BUTTON_FONT_BOLD = False

if sys.platform == "darwin":
    BUTTON_FONT_POINT_SIZE = 18
else: # Windows and Linux
    BUTTON_FONT_POINT_SIZE = 10

class PM_ToolButtonGrid( PM_GroupBox ):
    """
    The PM_ToolButtonGrid widget provides a grid of tool buttons that function
    as an I{exclusive button group}.
    
    @see: B{PM_ElementChooser} for an example of how this is used.
    
    @todo: Fix button size issue (e.g. all buttons are sized 32 x 32).
    """
    
    buttonList       = []
    defaultCheckedId = -1    # -1 means no checked Id
    setAsDefault     = True
    labelWidget      = None
    
    def __init__(self, 
                 parentWidget, 
                 title        = '', 
                 buttonList   = [],
                 checkedId    = -1, 
                 setAsDefault = False 
                 ):
        """
        Appends a PM_ToolButtonGrid widget to the bottom of I{parentWidget}, 
        the Property Manager dialog or group box.
        
        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox or PM_Dialog
        
        @param title: The group box title.
        @type  title: str
        
        @param buttonList: A list of I{button info lists}. There is one button
                           info list for each button in the grid. The button
                           info list contains the following six items:
                           1). Button Id (int), 
                           2). Button text (str),
                           3). Button icon path (str),
                           4). Column (int),
                           5). Row (int),
                           6). Button tool tip (str).
        @type  buttonList: list
        """
        
        PM_GroupBox.__init__(self, parentWidget, title)
        
        # These are needed to properly maintain the height of the grid if 
        # all buttons in a row are hidden via hide().
        self.vBoxLayout.setMargin(0)
        self.vBoxLayout.setSpacing(0)
        
        self.gridLayout.setMargin(1)
        self.gridLayout.setSpacing(0)
        
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(True)
        
        self.parentWidget = parentWidget
        self.buttonList   = buttonList
                
        if setAsDefault:
            self.setDefaultCheckedId(checkedId)
    
        
        self.loadToolButtons()
        
        self._widgetList.append(self)
        
        self._rowCount += 1
    
    def loadToolButtons(self):
        """
        Load the grid layout with tool buttons.
        
        """
                       
        self.buttonsById   = {}
        self.buttonsByText = {}
            
        # Load grid layout with tool buttons. (Original)
        for buttonInfo in self.buttonList:  
            buttonFont = self.getButtonFont()            
            buttonSize = QSize(BUTTON_WIDTH, BUTTON_HEIGHT) #@ FOR TEST ONLY
            buttonInfoList = self.getButtonInfoList(buttonInfo)
            
            buttonId       = buttonInfoList[0]
            buttonText     = buttonInfoList[1]
            buttonIconPath = buttonInfoList[2]
            column         = buttonInfoList[3]
            row            = buttonInfoList[4]
            buttonToolTip  = buttonInfoList[5] 
            
            
            button = QToolButton(self)
            button.setText(buttonText)
            if os.path.exists(buttonIconPath):
                button.setIcon(geticon(buttonIconPath))
                button.setIconSize(QSize(22,22))
            button.setToolTip(buttonToolTip)
            button.setFixedSize(buttonSize) #@ Currently fixed to 32 x 32.
            button.setCheckable(True)
            button.setAutoRaise(True)
            if self.checkedId() == buttonId:
                button.setChecked(True)
            button.setFont(buttonFont)
            self.buttonGroup.addButton(button, buttonId)
            
            #add button to the layout
            self.gridLayout.addWidget( button,
                                       row,
                                       column,
                                       1,
                                       1 )
            
            self.buttonsById[buttonId]    = button
            self.buttonsByText[buttonText] = button

    def getButtonFont(self):
        """
        Returns the font for the tool buttons in the grid
        """
        # Font for tool buttons.
        buttonFont = QFont(self.font())
        buttonFont.setFamily(BUTTON_FONT)
        buttonFont.setPointSize(BUTTON_FONT_POINT_SIZE)
        buttonFont.setBold(BUTTON_FONT_BOLD)
        return buttonFont
    
    def getButtonInfoList(self, buttonInfo):
        """
        Returns the button information provided by the user. 
        Subclasses should override this method if they need to provide 
        custom information (e.g. a fixed value for row) .
        @param  buttonInfo: list containing the button information
        @type   buttonInfo: list
        @return buttonInfoList: list containing the button information. 
                This can be same as I{buttonInfo} or can be modified further.
        @rtype  buttonInfoList: list
        @see:   PM_ToolButtonRow.getButtonInfoList
        
        """
        
        buttonInfoList = buttonInfo                
        return buttonInfoList
            
    def restoreDefault(self):
        """
        Restores the default checkedId.
        """
        if self.setAsDefault:
            for buttonInfo in self.buttonList:
                buttonId = buttonInfo[0]
                if buttonId == self.defaultCheckedId:
                    button = self.getButtonById(buttonId)
                    button.setChecked(True)
        return
    
    def setDefaultCheckedId(self, checkedId):
        """
        Sets the default checked id (button) to I{checkedId}. The current checked
        button is unchanged.
                      
        @param checkedId: The new default id for the tool button group.
        @type  checkedId: int
        """
        self.setAsDefault = True
        self.defaultCheckedId = checkedId
        
    def checkedButton(self):
        """
        Returns the tool button group's checked button, or 0 if no buttons are
        checked.
        """
        return self.buttonGroup.checkedButton()
        
    def checkedId(self):
        """
        Returns the id of the checkedButton(), or -1 if no button is checked.
        """
        return self.buttonGroup.checkedId()
    
    def getButtonByText(self, text):
        """
        Returns the button with its current text set to I{text}.
        """
        if self.buttonsByText.has_key(text):
            return self.buttonsByText[text]
        else:
            return None
        
    def getButtonById(self, buttonId):
        """
        Returns the button with the button id of I{buttonId}.
        """
        if self.buttonsById.has_key(buttonId):
            return self.buttonsById[buttonId]
        else:
            return None
        
# End of PM_ToolButtonGrid ############################