# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created on 2008-07-15 . The main purpose of this class was a workaround to
new Qt4.3.2 BUG 2916 in the QToolbar extension popup indicator. 

TODO:
"""

from PyQt4.Qt import QWidgetAction

from PyQt4.Qt import QToolButton
from PyQt4.Qt import Qt

import foundation.env as env


def truncateText(text, length = 12, truncateSymbol = '...'):
    """
    Truncates the tooltip text with the given truncation symbol
    (three dots) in the case 
    """
        
    #ninad 070201 This is a temporary fix. Ideally it should show the whole
    #text in the  toolbutton. But there are some layout / size policy 
    #problems because of which the toolbar height increases after you print
    #tooltip text on two or more lines. (undesirable effect) 
        
    if not text:
        print "no text to truncate. Returning"
        return 
    
    truncatedLength  = length - len(truncateSymbol)
    
    if len(text) > length:
        return text[:truncatedLength] + truncateSymbol
    else:
        return text
    
    
def wrapToolButtonText(text):
        """
        Add a newline character at the end of each word in the toolbutton text
        """
        #ninad 070126 QToolButton lacks this method. This is not really a 
        #'word wrap' but OK for now. 
        
        #@@@ ninad 070126. Not calling this method as it is creating an annoying
        #resizing problem in the Command toolbar layout. Possible solution is 
        #to add a spacer item in a vbox layout to the command toolbar layout
        
        stringlist = text.split(" ", QString.SkipEmptyParts)
        text2 = QString()
        if len(stringlist) > 1:
            for l in stringlist:
                text2.append(l)
                text2.append("\n")
            return text2
                
        return None
    
    

_superclass = QWidgetAction

class NE1_QWidgetAction(_superclass):
    def __init__(self, parent, win = None):        
        _superclass.__init__(self, parent)
        self.win = win
        self._toolButtonPalette = None
            
    def createWidget(self, parent):
        
        cmdToolbar = self.win.commandToolbar
        
        btn = None
        if cmdToolbar:
            flyoutToolBar = cmdToolbar.flyoutToolBar  
            if flyoutToolBar:
                if 0:
                    print "***self.text() =%s, parent = %s"%(self.text(), 
                                                             parent)
        
            if parent is flyoutToolBar:   
                btn = self._createToolButtonWidget(parent)                

        return btn
    
    def _createToolButtonWidget(self, parent):
        """
        @see: self.createWidget()
        """
        btn = QToolButton(parent)
        btn.setAutoFillBackground(True)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)      
        btn.setMinimumWidth(75)
        btn.setMaximumWidth(75)
        btn.setMinimumHeight(62) 
        btn.setAutoRaise(True)
        
        btn.setCheckable(True)   
        btn.setDefaultAction(self)
        
        text = truncateText(self.text())
        btn.setText(text)
        
        if self._toolButtonPalette:
            btn.setPalette(self._toolButtonPalette)
            
        #@@@ ninad070125 The following function 
        #adds a newline character after each word in toolbutton text. 
        #but the changes are reflected only on 'mode' toolbuttons 
        #on the flyout toolbar (i.e.only Checkable buttons..don't know 
        #why. Disabling its use for now. 
        debug_wrapText = False

        if debug_wrapText:
            text = wrapToolButtonText(action.text())
            if text:    
                action.setText(text) 
                
        return btn
                

    def setToolButtonPalette(self, palette):
        """
        @see: CommandToolbar._createFlyoutToolbar()
        """
        self._toolButtonPalette = palette
        
    
    
    
        
    