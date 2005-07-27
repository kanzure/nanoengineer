# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
elementSelector.py

$Id$
'''

from ElementSelectorDialog import *
from elementColors import ElementView
from elements import PeriodicTable
from constants import diTUBES

class elementSelector(ElementSelectorDialog):
    def __init__(self, win):
        ElementSelectorDialog.__init__(self, win)
        self.w = win
        self.elemTable = PeriodicTable
        self.displayMode = diTUBES
        
        self.elemGLPane = ElementView(self.elementFrame, "element glPane", self.w.glpane)
        # Put the GL widget inside the frame
        flayout = QVBoxLayout(self.elementFrame,1,1,'flayout')
        flayout.addWidget(self.elemGLPane,1)

    def setElementInfo(self,value):
        '''Called as a slot from button push of the element Button Group'''
        self.w.setElement(value)

    def update_dialog(self, elemNum):
        """Update non user interactive controls display for current selected element: element label info and element graphics info """
        print "elementSelector.update_dialog called"
        self.color = self.elemTable.getElemColor(elemNum)
        elm = self.elemTable.getElement(elemNum)
        
        self.elemGLPane.refreshDisplay(elm, self.displayMode)
        
    def transmutePressed(self):
        force = self.transmuteCheckBox.isChecked()
        self.w.glpane.mode.modifyTransmute(self.w.Element, force = force)
        # bruce 041216: renamed elemSet to modifyTransmute, added force option