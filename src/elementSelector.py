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

elementSymbol = { 1 : "H", 2 : "He", 
                            5 : "B", 6 : "C" , 7 : "N", 8 : "O", 9 : "F", 10 : "Ne",
                            13 : "Al", 14 : "Si", 15 : "P", 16 : "S", 17 : "Cl" , 18 : "Ar",
                            32 : "Ge", 33 : "As", 34 : "Se", 35 : "Br", 36 : "Kr",
                           51 : "Sb", 52 : "Te", 53 : "I", 54 : "Xe" }
                        
elementAMU = { 1 : "1.008", 2 : "4.003", 
                        5 : "10.811", 6 : "12.011" , 7 : "14.007", 8 : "15.999", 9 : "18.998", 10: "20.178",
                        13 : "26.982", 14 : "28.086", 15 : "30.974", 16 : "32.066", 17 : "35.453", 18 : "39.948",
                        32 : "72.610", 33 : "74.922", 34 : "78.960", 35 : "79.904", 36 : "83.800",
                        51 : "121.760", 52 : "127.600", 53 : "126.904", 54 : "131.290" }

r = { 1: 60, 2 : 210, 
        5 : 80, 6 : 35, 7 : 255, 8 : 190, 9 : 85, 10 : 210, 
        13 : 170, 14 : 155, 15 : 170, 16 : 255, 17 : 150, 18 : 210,
        32 : 206, 33 : 229, 34 : 230, 35 : 77, 36 : 210,
        51 : 170, 52 : 238, 53 : 0, 54 : 210 }
g = { 1: 215, 2 : 210, 
        5 : 135, 6 : 165, 7 : 170, 8 : 0, 9 : 255, 10 : 210, 
        13 : 170, 14 : 155, 15 : 85, 16 : 215, 17 : 225, 18 : 210,
        32 : 206, 33 : 62, 34 : 144, 35 : 202, 36 : 210,
        51 : 0, 52 : 183, 53 : 180, 54 : 210 }
b = { 1: 205, 2 : 255, 
        5 : 255, 6 : 75, 7 : 255, 8 : 0, 9 : 125, 10 : 255, 
        13 : 255, 14 : 155, 15 : 200, 16 : 75, 17 : 0, 18 : 255,
        32 : 0, 33 : 255, 34 : 23, 35 : 156, 36 : 255,
        51 : 255, 52 : 53, 53 : 135, 54 : 255 }

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
