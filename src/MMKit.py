# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
MMKit.py

$Id$
'''

from MMKitDialog import *
from elementColors import ElementView
from elements import PeriodicTable
from constants import diTUBES
from Utility import imagename_to_pixmap

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
        
        # Set current element in element button group.
        self.elementButtonGroup.setButton(self.w.Element) 

    # called as a slot from button push
    def setElementInfo(self,value):
        self.w.setElement(value)

    def update_dialog(self, elemNum):
        """Update non user interactive controls display for current selected element: element label info and element graphics info """
#        print "MMKit.update_dialog called"
        elm = self.elemTable.getElement(elemNum)
        self.elemGLPane.refreshDisplay(elm, self.displayMode)
        self.update_hybrid_btngrp()
        
    def update_hybrid_btngrp(self):
        '''Update the buttons of the current element's hybridization types into hybrid_btngrp; 
        select the specified one if provided'''
        elem = PeriodicTable.getElement(self.w.Element) # self.w.Element is atomic number
        
        atypes = elem.atomtypes

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
        
        self.hybrid_btngrp.setButton(0)
        self.hybrid_btngrp.show()

    def setup_C_hybrid_buttons(self):
        '''Displays the Carbon hybrid buttons.
        '''
        self.elementButtonGroup.setButton(self.w.Element)
        self.sp3_btn.setPixmap(imagename_to_pixmap('C_sp3.png'))
        self.sp3_btn.show()
        self.sp2_btn.setPixmap(imagename_to_pixmap('C_sp2.png'))
        self.sp2_btn.show()
        self.sp_btn.setPixmap(imagename_to_pixmap('C_sp.png'))
        self.sp_btn.show()
        self.aromatic_btn.hide()
        
    def setup_N_hybrid_buttons(self):
        '''Displays the Nitrogen hybrid buttons.
        '''
        self.sp3_btn.setPixmap(imagename_to_pixmap('N_sp3.png'))
        self.sp3_btn.show()
        self.sp2_btn.setPixmap(imagename_to_pixmap('N_sp2.png'))
        self.sp2_btn.show()
        self.sp_btn.setPixmap(imagename_to_pixmap('N_sp.png'))
        self.sp_btn.show()
        self.aromatic_btn.setPixmap(imagename_to_pixmap('N_aromatic.png'))
        self.aromatic_btn.show()
        
    def setup_O_hybrid_buttons(self):
        '''Displays the Oxygen hybrid buttons.
        '''
        self.sp3_btn.setPixmap(imagename_to_pixmap('O_sp3.png'))
        self.sp3_btn.show()
        self.sp2_btn.setPixmap(imagename_to_pixmap('O_sp2.png'))
        self.sp2_btn.show()
        self.sp_btn.hide()
        self.aromatic_btn.hide()
        
    def setup_S_hybrid_buttons(self):
        '''Displays the Sulfur hybrid buttons.
        '''
        self.sp3_btn.setPixmap(imagename_to_pixmap('O_sp3.png')) # S and O are the same.
        self.sp3_btn.show()
        self.sp3_btn.setPixmap(imagename_to_pixmap('O_sp3.png'))
        self.sp2_btn.show()
        self.sp_btn.hide()
        self.aromatic_btn.hide()
        
    def set_hybrid_type(self, type_id):
        print "MMKit.set_hybrid_type: type_id=", type_id
        self.w.hybridComboBox.setCurrentItem( type_id )