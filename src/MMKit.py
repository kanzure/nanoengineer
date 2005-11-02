# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
MMKit.py

$Id$

History:

Created by Huaicai.

bruce 050913 used env.history in some places.
'''

from MMKitDialog import *
from ThumbView import MMKitView, ChunkView
from elements import PeriodicTable
from constants import diTUBES
from chem import atom
from chunk import molecule
from Utility import imagename_to_pixmap
from DirView import FileItem, Directory, DirView
from assembly import assembly
from files_mmp import readmmp
from part import Part
import os
import sys
import env

class MMKit(MMKitDialog):
    bond_id2name =['sp3', 'sp2', 'sp', 'sp2(graphitic)']
    
    def __init__(self, win):
        MMKitDialog.__init__(self, win, fl=Qt.WType_Dialog)# Qt.WStyle_Customize | Qt.WStyle_Tool | Qt.WStyle_Title | Qt.WStyle_NoBorder)
        self.w = win
        self.elemTable = PeriodicTable
        self.displayMode = diTUBES
        self.elm = None
        
        self.newModel = None  ## used to save the selected lib part
        
        self.pageId = 0 ## Display the first tab page by default
        
        self.flayout = None
        
        self._setNewView('MMKitView')
        
        # Set current element in element button group.
        self.elementButtonGroup.setButton(self.w.Element) 
        
        self.connect(self, PYSIGNAL("chunkSelectionChanged"), self.w.pasteComboBox, SIGNAL("activated(int)"))
        self.connect(self.w.hybridComboBox, SIGNAL("activated(int)"), self.hybridChangedOutside)
        
        self.connect(self.w.hybridComboBox, SIGNAL("activated(const QString&)"), self.change2ElemPage)
        self.connect(self.w.elemChangeComboBox, SIGNAL("activated(const QString&)"), self.change2ElemPage)
        self.connect(self.w.pasteComboBox, SIGNAL("activated(const QString&)"), self.change2PastePage)
        
        #self.connect(self.w.depositAtomDashboard.pasteRB, SIGNAL("pressed()"), self.change2PastePage) 
        self.connect(self.w.depositAtomDashboard.pasteRB, SIGNAL("stateChanged(int)"), self.pasteBtnStateChanged) 
        self.connect(self.w.depositAtomDashboard.atomRB, SIGNAL("stateChanged(int)"), self.atomBtnStateChanged)
        
        self.connect(self.dirView, SIGNAL("selectionChanged(QListViewItem *)"), self.partChanged)
        
    
    def pasteBtnStateChanged(self, state):
        '''Slot method. Called when the state of the paste button of deposit dashboard has been changed. '''
        if state == QButton.On:
            self.change2PastePage()


    def atomBtnStateChanged(self, state):
        '''Slot method. Called when the state of the atom button of deposit dashboard has been changed. ''' 
        if state == QButton.On:
           self.change2ElemPage() 


    def hybridChangedOutside(self, newId):
        '''Slot method. Called when user change element hybridization from the dashboard. 
         This method achieves the same effect as user clicked one of the hybridization buttons.'''
        self.hybrid_btngrp.setButton(newId)
        self.set_hybrid_type(newId)
        
        ## fix bug 868
        self.w.depositAtomDashboard.atomRB.setOn(True)
       

    def change2ElemPage(self):
        '''Slot method. Called when user changed element/hybrid or pressed deposit button from dashboard.
        '''
        if not (self.tabWidget2.currentPageIndex() == 0):
            self.tabWidget2.setCurrentPage(0)
            

    def change2PastePage(self):
        '''Slot method. Called when user changed pastable item or pressed paste button from dashboard. '''
        #if not (self.tabWidget2.currentPageIndex() == 1):
        self.tabWidget2.setCurrentPage(1)
            

    def setElementInfo(self,value):
        '''Called as a slot from button push of the element Button Group'''
        self.w.setElement(value)


    def update_dialog(self, elemNum):
        """Called when the current element has been changed.
           Update non user interactive controls display for current selected 
           element: element label info and element graphics info """

        elm = self.elemTable.getElement(elemNum)
        if elm == self.elm and self.tabWidget2.currentPageIndex() == 0: return
        
        ## The following statements are redundant in some situations.
        self.elementButtonGroup.setButton(elemNum)

        self.color = self.elemTable.getElemColor(elemNum)
        self.elm = self.elemTable.getElement(elemNum)
        
        self.update_hybrid_btngrp()
        
        self.elemGLPane.resetView()
        self.elemGLPane.refreshDisplay(self.elm, self.displayMode)
        
        # Fix for bug 353, to allow the dialog to be updated with the correct page.  For example,
        # when the user selects Copy and Paste from the Edit toolbar/menu, the MMKit should show
        # the Clipboard, not the Atoms page. Mark 050808
        if self.w.pasteP:
            self.change2PastePage()
        else:
            self.change2ElemPage()
            
        
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
            self.elemGLPane.changeHybridType(None)
            return
        
        #if len(atypes) > 1:
        # Prequisite: w.hybridComboBox has been updated at this moment.
        type_id = self.w.hybridComboBox.currentItem()
        b_name = self.bond_id2name[type_id]
        self.elemGLPane.changeHybridType(b_name)
        self.hybrid_btngrp.setButton(type_id)
            
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
        self.graphitic_btn.hide()
    
        
    def setup_N_hybrid_buttons(self):
        '''Displays the Nitrogen hybrid buttons.
        '''
        self.sp3_btn.setPixmap(imagename_to_pixmap('N_sp3.png'))
        self.sp3_btn.show()
        self.sp2_btn.setPixmap(imagename_to_pixmap('N_sp2.png'))
        self.sp2_btn.show()
        self.sp_btn.setPixmap(imagename_to_pixmap('N_sp.png'))
        self.sp_btn.show()
        self.graphitic_btn.setPixmap(imagename_to_pixmap('N_graphitic.png'))
        self.graphitic_btn.show()
        
        
    def setup_O_hybrid_buttons(self):
        '''Displays the Oxygen hybrid buttons.
        '''
        self.sp3_btn.setPixmap(imagename_to_pixmap('O_sp3.png'))
        self.sp3_btn.show()
        self.sp2_btn.setPixmap(imagename_to_pixmap('O_sp2.png'))
        self.sp2_btn.show()
        self.sp_btn.hide()
        self.graphitic_btn.hide()
        
        
    def setup_S_hybrid_buttons(self):
        '''Displays the Sulfur hybrid buttons.
        '''
        self.sp3_btn.setPixmap(imagename_to_pixmap('O_sp3.png')) # S and O are the same.
        self.sp3_btn.show()
        self.sp2_btn.setPixmap(imagename_to_pixmap('O_sp2.png'))
        self.sp2_btn.show()
        self.sp_btn.hide()
        self.graphitic_btn.hide()
    
    
    def set_hybrid_type(self, type_id):
        '''Slot method. Called when any of the hybrid type buttons was clicked. '''
        self.w.hybridComboBox.setCurrentItem( type_id )

        b_name = self.bond_id2name[type_id]
        
        #This condition fixs bug 866, also saves time since no need to draw without MMKIt shown
        if self.isShown():
            self.elemGLPane.changeHybridType(b_name)
            self.elemGLPane.refreshDisplay(self.elm, self.displayMode)
        
    
    def tabpageChanged(self, wg):
        '''Slot method. Called when user clicked to change the tab page'''
        self.pageId = self.tabWidget2.indexOf(wg)
        
        if self.pageId == 1: ## Clipboard page
            self.w.pasteP = True
            self.w.depositAtomDashboard.pasteRB.setOn(True)
            self.elemGLPane.setDisplay(self.displayMode)
            self._clipboardPageView()
            self.browseButton.hide()
            
        elif self.pageId == 0:  ## Element page
            self.w.pasteP = False
            self.w.depositAtomDashboard.atomRB.setOn(True)
            self.elemGLPane.resetView()
            self.elemGLPane.refreshDisplay(self.elm, self.displayMode)
            self.browseButton.hide()
        
        elif self.pageId == 2:
            if self.rootDir:
                self.elemGLPane.setDisplay(self.displayMode)
                self._libPageView()
            self.browseButton.show()
            
            #Turn off both paste and deposit buttons, so when in library page and user choose 'set hotspot and copy'
            #it will change to paste page, also, when no chunk selected, a history message shows instead of depositing an atom.
            self.w.depositAtomDashboard.pasteRB.setOn(False)
            self.w.depositAtomDashboard.atomRB.setOn(False)
            
        self.elemGLPane.setFocus()
        
        
    def chunkChanged(self, item):
        '''Slot method. Called when user changed the selected chunk. '''
        itemId = self.chunkListBox.index(item)
        newChunk = self.pastableItems[itemId]
                
        #self.w.pasteComboBox.setCurrentItem(itemId)
        #buildModeObj = self.w.glpane.modetab['DEPOSIT']
        #assert buildModeObj
        #buildModeObj.setPaste()
        
        ##Compared to the above way, I think this way is better. Modules are more uncoupled.
        self.w.pasteComboBox.setCurrentItem(itemId)
        self.emit(PYSIGNAL('chunkSelectionChanged'), (itemId,))
        
        self.elemGLPane.updateModel(newChunk)
        
    
    def updatePastableItems(self):
        '''Slot method. Called when user clicks the 'Update' button. '''
        self._clipboardPageView()
    
        
    def partChanged(self, item):
        '''Slot method, called when user changed the partlib brower tree'''
        if isinstance(item, FileItem):
           self._libPageView(True)
        else:
           self.newModel = None
           self.elemGLPane.updateModel(self.newModel)
 

    def getPastablePart(self):
        '''Public method. Retrieve pastable part and hotspot if current tab page is in libary, otherwise, return None. '''
        if self.pageId == 2:
            return self.newModel, self.elemGLPane.hotspotAtom
        return None, None
    
           
    def _libPageView(self, isFile=False):
        item = self.dirView.selectedItem()
        if not isFile and not isinstance(item, FileItem):
            self.newModel = None
            self.elemGLPane.updateModel(self.newModel)
            return
        
        mmpfile = str(item.getFileObj())
        self.newModel = assembly(self.w, "assembly 1")
        self.newModel.o = self.elemGLPane ## Make it looks "assembly" used by glpane.
        readmmp(self.newModel, mmpfile)
        
        # Move all stuff under assembly.tree into assy.shelf. This is needed to draw hotspot singlet
        def addChild(child):
            self.newModel.shelf.addchild(child)
        
        # Remove existing clipboard items from the libary part before adopting childern from 'tree'.
        self.newModel.shelf.members = []
        self.newModel.tree.apply2all(addChild)
        
        self.newModel.shelf.prior_part = None
        self.newModel.part = Part(self.newModel, self.newModel.shelf)
            
        self.elemGLPane.updateModel(self.newModel)
                
    
    def _clipboardPageView(self):
        '''Construct clipboard page view. '''
        self.pastableItems = self._getPastableClipboardItems(self.w.assy)
        
        list = QStringList()
        for item in self.pastableItems:
            list.append(item.name)
        
        self.chunkListBox.clear()
        self.chunkListBox.insertStringList(list)
        if len(list): 
            itIndex = self.w.pasteComboBox.currentItem()
            self.chunkListBox.setSelected(itIndex, True)
        else: self.elemGLPane.updateModel(None)
        
        
            
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
        elif viewClassName == 'MMKitView':
            self.elemGLPane = MMKitView(self.elementFrame, "MMKitView glPane", self.w.glpane)
        
        self.flayout.addWidget(self.elemGLPane,1)
        
        self.dirView = DirView(self.libraryPage)
        libraryPageLayout = QVBoxLayout(self.libraryPage,11,6,"libraryPageLayout")
        libraryPageLayout.addWidget(self.dirView)
        
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        libDir = os.path.normpath(filePath + '/../partlib')
        
        self.libPathKey = '/nanorex/nE-1/libraryPath'
        libDir = env.prefs.get(self.libPathKey, libDir)
        
        if os.path.isdir(libDir):
            self.rootDir = Directory(self.dirView, libDir)
            self.rootDir.setOpen(True)
        else:
            self.rootDir = None
            from HistoryWidget import redmsg
            env.history.message(redmsg("The part library directory: %s doesn't exists." %libDir))
        
            
    def browseDirectories(self):
       '''Slot method for the browse button of library page. '''
       from constants import globalParms
       # Determine what directory to open.
       if self.w.assy.filename: odir = os.path.dirname(self.w.assy.filename)
       else: odir = globalParms['WorkingDirectory']
        
       fdir = QFileDialog.getExistingDirectory(odir, self, "Choose directory", "Choose library directory", True)
       libDir = str(fdir)
       #fileDialog = QFileDialog(self, "Choose library directory", True)
       #fileDialog.setCaption("Choose library directory")
       #fileDialog.setMode(QFileDialog.Directory)
       if libDir:#fileDialog.exec_loop() == QDialog.Accepted:
           #libDir = str(fileDialog.selectedFile())
           if os.path.isdir(libDir):
               env.prefs[self.libPathKey] = libDir
               
               #Clear any previous tree items before creating the new one
               self.dirView.clear()
        
               self.rootDir = Directory(self.dirView, libDir)
               self.rootDir.setOpen(True)
            
               #Refresh GL-thumbView display
               self.newModel = None
               self.elemGLPane.updateModel(self.newModel)
            
        
