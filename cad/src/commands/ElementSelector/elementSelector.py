# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
elementSelector.py

$Id$
"""

from PyQt4.Qt import QDialog
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QVBoxLayout

from commands.ElementSelector.ElementSelectorDialog import Ui_ElementSelectorDialog
from graphics.widgets.ThumbView import ElementView
from model.elements import PeriodicTable
from utilities.constants import diTUBES

class elementSelector(QDialog, Ui_ElementSelectorDialog):
    def __init__(self, win):
        QDialog.__init__(self, win)
        self.setupUi(self)
        self.connect(self.closePTableButton,SIGNAL("clicked()"),self.close)
        self.connect(self.TransmuteButton,SIGNAL("clicked()"),self.transmutePressed)
        self.connect(self.elementButtonGroup,SIGNAL("clicked(int)"),self.setElementInfo)
        self.w = win
        self.elemTable = PeriodicTable
        self.displayMode = diTUBES
        
        self.elemGLPane = ElementView(self.elementFrame, "element glPane", self.w.glpane)
        # Put the GL widget inside the frame
        flayout = QVBoxLayout(self.elementFrame,1,1,'flayout')
        flayout.addWidget(self.elemGLPane,1)
        self.elementFrame.setWhatsThis("""3D view of current atom type""")
        self.TransmuteButton.setWhatsThis("""Transmutes selected atoms in the 3D workspace to current atom
        above.""")
        self.transmuteCheckBox.setWhatsThis("""Check if transmuted atoms should keep all existing bonds,  even
        if chemistry is wrong.""")

    def setElementInfo(self,value):
        """
        Called as a slot from button push of the element Button Group
        """
        self.w.setElement(value)

    def update_dialog(self, elemNum):
        """
        Update non user interactive controls display for current 
        selected element: element label info and element graphics info
        """
        self.color = self.elemTable.getElemColor(elemNum)
        elm = self.elemTable.getElement(elemNum)
        
        self.elemGLPane.resetView()
        self.elemGLPane.refreshDisplay(elm, self.displayMode)
        
    def transmutePressed(self):
        force = self.transmuteCheckBox.isChecked()
        self.w.assy.modifyTransmute(self.w.Element, force = force)
        # bruce 041216: renamed elemSet to modifyTransmute, added force option
