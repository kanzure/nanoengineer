# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
MMKit.py

$Id$
'''

from MMKitDialog import *
from ThumbView import ElementView
from elements import PeriodicTable
from constants import diTUBES
from chem import atom
from chunk import molecule
from Utility import imagename_to_pixmap

class MMKit(MMKitDialog):
    bond_id2name =['sp3', 'sp2', 'sp', 'sp2(graphitic)']
    
    def __init__(self, win):
        MMKitDialog.__init__(self, win)
        self.w = win
        self.elemTable = PeriodicTable
        self.displayMode = diTUBES
        
        self.elemGLPane = ElementHybridView(self.elementFrame, "element glPane", self.w.glpane)
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
        #print "MMKit.update_dialog called"
        self.color = self.elemTable.getElemColor(elemNum)
        self.elm = self.elemTable.getElement(elemNum)
        
        self.elemGLPane.changeHybridType(None)
        
        self.elemGLPane.refreshDisplay(self.elm, self.displayMode)
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
        self.w.hybridComboBox.setCurrentItem( type_id )

        b_name = self.bond_id2name[type_id]
        print "Hybrid name: ", b_name
        self.elemGLPane.changeHybridType(b_name)
        self.elemGLPane.refreshDisplay(self.elm, self.displayMode)


class ElementHybridView(ElementView):
    hybrid_type_name = None


    def changeHybridType(self, name):
        self.hybrid_type_name = name
    
    
    def constructModel(self, elm, pos, dispMode):
        """This is to try to repeat what 'oneUnbonded()' function does,
        but hope to remove some stuff not needed here.
        The main purpose is to build the geometry model for element display. 
        <Param> elm: An object of class Elem
        <Param> dispMode: the display mode of the atom--(int)
        <Return>: the molecule which contains the geometry model.
        """
        class DummyAssy:
            """dummy assemby class"""
            drawLevel = 2
            
        if 0:#1:
            assy = DummyAssy()
        else:
            from assembly import assembly 
            assy = assembly(None)
            assy.o = self
                
        mol = molecule(assy, 'dummy') 
        atm = atom(elm.symbol, pos, mol)
        atm.display = dispMode
        ## bruce 050510 comment: this is approximately how you should change the atom type (e.g. to sp2) for this new atom: ####@@@@
        if self.hybrid_type_name:
            atm.set_atomtype_but_dont_revise_singlets(self.hybrid_type_name)
        ## see also atm.element.atomtypes -> a list of available atomtype objects for that element
        ## (which can be passed to set_atomtype_but_dont_revise_singlets)
        atm.make_singlets_when_no_bonds()
        return mol
        