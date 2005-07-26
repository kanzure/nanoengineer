# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
MMKit.py

$Id$
'''

from MMKitDialog import *
from elementColors import ElementView
from elements import PeriodicTable
from constants import diTUBES

class MMKit(MMKitDialog):
    def __init__(self, win):
        MMKitDialog.__init__(self, win)
        self.w = win
        self.elemTable = PeriodicTable
        self.displayMode = diTUBES
        
        self.elemGLPane = ElementView(self.elementFrame, "element glPane", self.w.glpane)
        # Put the GL widget inside the frame
        flayout = QVBoxLayout(self.elementFrame,1,1,'flayout')
        flayout.addWidget(self.elemGLPane,1)

    # called as a slot from button push
    def setElementInfo(self,value):
        self.w.setElement(value)

    def update_dialog(self, elemNum):
        """Update non user interactive controls display for current selected element: element label info and element graphics info """
        print "MMKit.update_dialog called"
        self.color = self.elemTable.getElemColor(elemNum)
        elm = self.elemTable.getElement(elemNum)
        
        self.elemGLPane.refreshDisplay(elm, self.displayMode)
        self.update_hybrid_btngrp()
        
    def update_hybrid_btngrp(self):
        '''Update the buttons of the current element's hybridization types into hybrid_btngrp; 
        select the specified one if provided'''
        elem = PeriodicTable.getElement(self.w.Element) # self.w.Element is atomic number
        
        atypes = elem.atomtypes

#        print "MMKit.update_hybrid_btngrp called. elem =", elem.name
#        print "atypes=",atypes
        
        if elem.name == 'Carbon':
            self.setup_C_hybrid_buttons()
        elif elem.name == 'Nitrogen':
            self.setup_N_hybrid_buttons()
        elif elem.name == 'Oxygen':
            self.setup_O_hybrid_buttons()
        elif elem.name == 'Sulfur':
            self.setup_S_hybrid_buttons()
        else:
            self.hybrid_btngrp.hide()
            return
        
        self.hybrid_btngrp.show()

    def setup_C_hybrid_buttons(self):
        '''Displays the Carbon hybrid buttons.
        '''
        self.sp3_btn.show()
        self.sp2_btn.show()
        self.sp_btn.show()
        self.aromatic_btn.hide()
        
    def setup_N_hybrid_buttons(self):
        '''Displays the Nitrogen hybrid buttons.
        '''
        self.sp3_btn.show()
        self.sp2_btn.show()
        self.sp_btn.show()
        self.aromatic_btn.show()
        
    def setup_O_hybrid_buttons(self):
        '''Displays the Oxygen hybrid buttons.
        '''
        self.sp3_btn.show()
        self.sp2_btn.show()
        self.sp_btn.hide()
        self.aromatic_btn.hide()
        
    def setup_S_hybrid_buttons(self):
        '''Displays the Sulfur hybrid buttons.
        '''
        self.sp3_btn.show()
        self.sp2_btn.show()
        self.sp_btn.hide()
        self.aromatic_btn.hide()