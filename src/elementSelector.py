# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
elementSelector.py

$Id$
'''

from ElementSelectorDialog import *
#from elementpixmaps import *
from elementColors import ElementView

#########################################################################
# Declaring tuples
elementAMU = { 1 : "1.008", 2 : "4.003", 
                        5 : "10.811", 6 : "12.011" , 7 : "14.007", 8 : "15.999", 9 : "18.998", 10: "20.178",
                        13 : "26.982", 14 : "28.086", 15 : "30.974", 16 : "32.066", 17 : "35.453", 18 : "39.948",
                        32 : "72.610", 33 : "74.922", 34 : "78.960", 35 : "79.904", 36 : "83.800",
                        51 : "121.760", 52 : "127.600", 53 : "126.904", 54 : "131.290" }

############################################################

class elementSelector(ElementSelectorDialog):
    def __init__(self, win):
        ElementSelectorDialog.__init__(self, win)
        self.w = win
        self.elemTable = self.w.periodicTable
        
        self.elemGLPane = ElementView(self.elementFrame, "element glPane", self.w.glpane)
        # Put the GL widget inside the frame
        flayout = QVBoxLayout(self.elementFrame,1,1,'flayout')
        flayout.addWidget(self.elemGLPane,1)

    # called as a slot from button push
    def setElementInfo(self,value):
        self.w.setElement(value)

    def setDisplay(self, value):
        eInfoText = "<p>" + str(value) + "</p> "
        elemSymbol = self.elemTable.getElemSymbol(value)
        if not elemSymbol: return
        eInfoText += "<p> " + "<font size=26> <b>" + elemSymbol + "</b> </font> </p>"
        eInfoText += "<p>" + elementAMU[value] + "</p>"
        self.elemInfoLabel.setText(eInfoText)
        
        self._updateElemGraphDisplay(value)
        
 
    def _updateElemGraphDisplay(self, elemNum):
        """Update non user interactive controls display for current selected element: element label info and element graphics info """
        self.color = self.elemTable.getElemColor(elemNum)
        self.rad = self.elemTable.getElemRvdw(elemNum)
        
        self.elemGLPane.refreshDisplay(self.color, self.rad)
         
        r =  int(self.color[0]*255 + 0.5)
        g = int(self.color[1]*255 + 0.5)
        b = int(self.color[2]*255 + 0.5)
        self.elemColorLabel.setPaletteBackgroundColor(QColor(r, g, b)) 
        
    def transmutePressed(self):
        force = self.transmuteCheckBox.isChecked()
        self.w.glpane.mode.modifyTransmute(self.w.Element, force = force)
        # bruce 041216: renamed elemSet to modifyTransmute, added force option