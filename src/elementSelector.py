# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
elementSelector.py

$Id$
'''

from ElementSelectorDialog import *
from elementColors import ElementView
from elements import PeriodicTable
from constants import diVDW, diCPK, diTUBES

#########################################################################
# Declaring tuples
elementAMU = { 1 : "1.008", 2 : "4.003", 
                        5 : "10.811", 6 : "12.011" , 7 : "14.007", 8 : "15.999", 9 : "18.998", 10: "20.178",
                        13 : "26.982", 14 : "28.086", 15 : "30.974", 16 : "32.066", 17 : "35.453", 18 : "39.948",
                        32 : "72.610", 33 : "74.922", 34 : "78.960", 35 : "79.904", 36 : "83.800",
                        51 : "121.760", 52 : "127.600", 53 : "126.904", 54 : "131.290" }

############################################################

class elementSelector(ElementSelectorDialog):
    _displayList = (diTUBES, diCPK, diVDW)
    def __init__(self, win):
        ElementSelectorDialog.__init__(self, win)
        self.w = win
        self.elemTable = PeriodicTable
        self.displayMode = self._displayList[0]
        
        self.elemGLPane = ElementView(self.elementFrame, "element glPane", self.w.glpane)
        # Put the GL widget inside the frame
        flayout = QVBoxLayout(self.elementFrame,1,1,'flayout')
        flayout.addWidget(self.elemGLPane,1)

    # called as a slot from button push
    def setElementInfo(self,value):
        self.w.setElement(value)

    def setDisplay(self, value):
        self.elemNum = value
        eInfoText =   str(value) + "<br>"#"</p> "
        elemSymbol = self.elemTable.getElemSymbol(value)
        elemName = self.elemTable.getElemName(value)
        elemRvdw = str(self.elemTable.getElemRvdw(value))
        elemBonds = str(self.elemTable.getElemBondCount(value))
        if not elemSymbol: return
        eInfoText +=   "<font size=18> <b>" + elemSymbol + "</b> </font> <br>"#</p>"
        eInfoText +=  elemName + "<br>"#"</p>"
        eInfoText += "Amu: " + elementAMU[value] + "<br>"#"</p>"
        eInfoText += "Rvdw: " + elemRvdw + "<br>"#"</p>"
        eInfoText += "Open Bonds: " + elemBonds #</p>"
        self.elemInfoLabel.setText(eInfoText)
        
        self._updateElemGraphDisplay(value)
    
    def changeDisplayMode(self, value):
        """Called when any of the display mode radioButton clicked. """
        assert value in [0, 1, 2]
        newMode = self._displayList[value]
        if newMode != self.displayMode:
            self.displayMode = newMode
            elm = self.elemTable.getElement(self.elemNum)
            self.elemGLPane.refreshDisplay(elm, self.displayMode)    
 
    def _updateElemGraphDisplay(self, elemNum):
        """Update non user interactive controls display for current selected element: element label info and element graphics info """
        self.color = self.elemTable.getElemColor(elemNum)
        elm = self.elemTable.getElement(elemNum)
        
        self.elemGLPane.refreshDisplay(elm, self.displayMode)
         
        r =  int(self.color[0]*255 + 0.5)
        g = int(self.color[1]*255 + 0.5)
        b = int(self.color[2]*255 + 0.5)
        self.elemColorLabel.setPaletteBackgroundColor(QColor(r, g, b)) 
        
    def transmutePressed(self):
        force = self.transmuteCheckBox.isChecked()
        self.w.glpane.mode.modifyTransmute(self.w.Element, force = force)
        # bruce 041216: renamed elemSet to modifyTransmute, added force option