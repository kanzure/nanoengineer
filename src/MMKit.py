# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
MMKit.py

$Id$
'''

from MMKitDialog import *
from ThumbView import ElementHybridView, ChunkView
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
        
        self.flayout = None
        
        self._setNewView('ElementHybridView')
        
        #self.tabWidget2.setCurrentPage(1)
        # Set current element in element button group.
        #self.elementButtonGroup.setButton(self.w.Element) 

    def setElementInfo(self,value):
        '''Called as a slot from button push of the element Button Group'''
        self.w.setElement(value)

    def update_dialog(self, elemNum):
        """Called when the current element has been changed.
           Update non user interactive controls display for current selected 
           element: element label info and element graphics info """
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
        '''Slot method. Called when any of the hybrid type buttons was clicked. '''
        self.w.hybridComboBox.setCurrentItem( type_id )

        b_name = self.bond_id2name[type_id]
        print "Hybrid name: ", b_name
        self.elemGLPane.changeHybridType(b_name)
        self.elemGLPane.refreshDisplay(self.elm, self.displayMode)
    
    def tabpageChanged(self, wg):
        '''Slot method. Called when user clicked to change the tab page'''
        pageId = self.tabWidget2.indexOf(wg)
        
        if pageId == 1: ##Clipboard page
            self.w.pasteP = True
            self.w.depositAtomDashboard.pasteRB.setOn(True)
            self.elemGLPane.setDisplay(self.displayMode)
            self._clipboardPageView()
        else:
            #self._setNewView('ElementHybridView')
            self.w.pasteP = False
            self.w.depositAtomDashboard.atomRB.setOn(True)
            self.elemGLPane.changeHybridType(None)
            self.elemGLPane.refreshDisplay(self.elm, self.displayMode)
            

    def chunkChanged(self, item):
        '''Slot method. Called when user changed the selected chunk. '''
        itemId = self.chunkListBox.index(item)
        newChunk = self.pastableItems[itemId]
        
        self.w.pasteComboBox.setCurrentItem(itemId)
        
        self.elemGLPane.updateModel(newChunk)
        
    
    def _clipboardPageView(self):
        '''Construct clipboard page view. '''
        self.pastableItems = self._getPastableClipboardItems(self.w.assy)
        
        list = QStringList()
        for item in self.pastableItems:
            list.append(item.name)
        
        self.chunkListBox.clear()
        self.chunkListBox.insertStringList(list)
        if len(list): self.chunkListBox.setCurrentItem(0)
        
        #self._setNewView('ChunkView')
        
        
            
    def _getPastableClipboardItems(self, assy):
        '''Find all current pastable chunks. '''
        itemGroup = assy.shelf
        
        pastableItems = []
        for item in itemGroup.members:
            if isinstance(item, molecule):
                pastableItems += [item]
        
        return pastableItems

    
    def _setNewView(self, viewClassName):
        # Put the GL widget inside the frame
        if not self.flayout:
            self.flayout = QVBoxLayout(self.elementFrame,1,1,'flayout')
        else:
            if self.elemGLPane: 
                self.flayout.removeChild(self.elemGLPane)
                self.elemGLPane = None
        
        if viewClassName == 'ChunkView':
            self.elemGLPane = ChunkView(self.elementFrame, "chunk glPane", self.w.glpane)
        elif viewClassName == 'ElementHybridView':
            self.elemGLPane = ElementHybridView(self.elementFrame, "element Hybrid glPane", self.w.glpane)
        
        self.flayout.addWidget(self.elemGLPane,1)
        
     
        