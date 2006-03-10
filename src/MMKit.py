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
import os, sys
import env

# PageId constants for mmkit_tab
AtomsPage=0
ClipboardPage=1
LibraryPage=2

class MMKit(MMKitDialog):
    bond_id2name =['sp3', 'sp2', 'sp', 'sp2(graphitic)']
    
    def __init__(self, win):
        MMKitDialog.__init__(self, win, fl=Qt.WType_Dialog)# Qt.WStyle_Customize | Qt.WStyle_Tool | Qt.WStyle_Title | Qt.WStyle_NoBorder)
        self.w = win
        self.elemTable = PeriodicTable
        self.displayMode = diTUBES
        self.elm = None
        
        self.newModel = None  ## used to save the selected lib part
        
        self.flayout = None
        
        if sys.platform == 'darwin': 
            # Work around for bug 1659. Sometimes the program crashes on MacOS when
            # setting tab icons in the MMKit's tabwidget. mark 060310.
            self.mmkit_tab.setMargin ( 0 ) 
            self.mmkit_tab.setTabLabel (self.atomsPage, 'Atoms')
            self.mmkit_tab.setTabLabel (self.clipboardPage, 'Clipbd')
            self.mmkit_tab.setTabLabel (self.libraryPage, 'Lib')
        else:
            # Add icons to MMKit's tabs. mark 060223.
            atoms_pm = imagename_to_pixmap("atom.png")
            self.mmkit_tab.setTabIconSet ( self.atomsPage, QIconSet(atoms_pm))
        
            clipboard_pm = imagename_to_pixmap("clipboard-empty.png")
            self.mmkit_tab.setTabIconSet ( self.clipboardPage, QIconSet(clipboard_pm))
        
            library_pm = imagename_to_pixmap("library.png")
            self.mmkit_tab.setTabIconSet ( self.libraryPage, QIconSet(library_pm))
        
        self._setNewView('MMKitView')
        
        # Set current element in element button group.
        self.elementButtonGroup.setButton(self.w.Element) 
        
        self.connect(self, PYSIGNAL("chunkSelectionChanged"), self.w.pasteComboBox, SIGNAL("activated(int)"))
        self.connect(self.w.hybridComboBox, SIGNAL("activated(int)"), self.hybridChangedOutside)
        
        self.connect(self.w.hybridComboBox, SIGNAL("activated(const QString&)"), self.change2AtomsPage)
        self.connect(self.w.elemChangeComboBox, SIGNAL("activated(const QString&)"), self.change2AtomsPage)
        self.connect(self.w.pasteComboBox, SIGNAL("activated(const QString&)"), self.change2ClipboardPage)
        
        #self.connect(self.w.depositAtomDashboard.pasteBtn, SIGNAL("pressed()"), self.change2ClipboardPage) 
        self.connect(self.w.depositAtomDashboard.pasteBtn, SIGNAL("stateChanged(int)"), self.pasteBtnStateChanged) 
        self.connect(self.w.depositAtomDashboard.depositBtn, SIGNAL("stateChanged(int)"), self.depositBtnStateChanged)
        
        self.connect(self.dirView, SIGNAL("selectionChanged(QListViewItem *)"), self.partChanged)
        
    
    def pasteBtnStateChanged(self, state):
        '''Slot method. Called when the state of the Paste button of deposit dashboard has been changed. '''
        if state == QButton.On:
            self.change2ClipboardPage()


    def depositBtnStateChanged(self, state):
        '''Slot method. Called when the state of the Deposit button of deposit dashboard has been changed. ''' 
        if state == QButton.On:
           self.change2AtomsPage() 


    def hybridChangedOutside(self, newId):
        '''Slot method. Called when user changes element hybridization from the dashboard. 
         This method achieves the same effect as user clicked one of the hybridization buttons.'''
        self.hybrid_btngrp.setButton(newId)
        self.set_hybrid_type(newId)
        
        ## fix bug 868
        self.w.depositAtomDashboard.depositBtn.setOn(True)
       

    def change2AtomsPage(self):
        '''Slot method called when user changes element/hybrid combobox or 
        presses Deposit button from Build mode dashboard.
        '''
        if self.mmkit_tab.currentPageIndex() == AtomsPage: return
        self.mmkit_tab.setCurrentPage(AtomsPage) # Generates signal
            

    def change2ClipboardPage(self):
        '''Slot method called when user changes pastable item combobox or 
        presses the Paste button from the Build mode dashboard. '''
        #if not (self.mmkit_tab.currentPageIndex() == ClipboardPage):
        self.mmkit_tab.setCurrentPage(ClipboardPage) # Generates signal
            

    def setElementInfo(self,value):
        '''Slot method called when an element button is pressed in the element ButtonGroup.
        '''
        self.w.setElement(value)


    def update_dialog(self, elemNum):
        """Called when the current element has been changed.
           Update non user interactive controls display for current selected 
           element: element label info and element graphics info """

        elm = self.elemTable.getElement(elemNum)
        if elm == self.elm and self.currentPageOpen(AtomsPage): return
        
        ## The following statements are redundant in some situations.
        self.elementButtonGroup.setButton(elemNum)

        self.color = self.elemTable.getElemColor(elemNum)
        self.elm = self.elemTable.getElement(elemNum)
        
        self.update_hybrid_btngrp()
        
        self.elemGLPane.resetView()
        self.elemGLPane.refreshDisplay(self.elm, self.displayMode)
        
        # Fix for bug 353, to allow the dialog to be updated with the correct page.  For example,
        # when the user selects Paste from the Edit toolbar/menu, the MMKit should show
        # the Clipboard page and not the Atoms page. Mark 050808
        if self.w.depositState == 'Clipboard':
            self.change2ClipboardPage()
        else:
            self.change2AtomsPage()
        
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
        
    
    def setup_current_page(self, page):
        '''Slot method that is called whenever a user clicks on the 
        'Atoms', 'Clipboard' or 'Library' tab to change to that page.
        '''
        
        #print "setup_current_page: pagename=", pagename
        
        if page == self.atomsPage:  # Atoms page
            self.w.depositState = 'Atoms'
            self.w.update_depositState_buttons()
            self.elemGLPane.resetView()
            self.elemGLPane.refreshDisplay(self.elm, self.displayMode)
            self.browseButton.hide()
        
        elif page == self.clipboardPage: # Clipboard page
            self.w.depositState = 'Clipboard'
            self.w.update_depositState_buttons()
            self.elemGLPane.setDisplay(self.displayMode)
            self._clipboardPageView()
            self.browseButton.hide()
            
        elif page == self.libraryPage: # Library page
            if self.rootDir:
                self.elemGLPane.setDisplay(self.displayMode)
                self._libPageView()
            self.browseButton.show()
            
            #Turn off both paste and deposit buttons, so when in library page and user choose 'set hotspot and copy'
            #it will change to paste page, also, when no chunk selected, a history message shows instead of depositing an atom.
            self.w.depositState = 'Library'
            self.w.update_depositState_buttons()
        else:
            print 'Error: MMKit page unknown: ', page
            
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
        #& self.w.pasteComboBox.setCurrentItem(itemId)
            # Resolves index out of range error. Shouldn't impact behavior. mark 060307.
        self.emit(PYSIGNAL('chunkSelectionChanged'), (itemId,))
        
        self.elemGLPane.updateModel(newChunk)
        
    
    def update_clipboard_items(self):
        '''Updates the items in the clipboard's listview. '''
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
        if self.currentPageOpen(LibraryPage):
            return self.newModel, self.elemGLPane.hotspotAtom
        return None, None

    def currentPageOpen(self, page_id):
        '''Returns True if <page_id> is the current page open in the tab widget, where:
            0 = Atoms page
            1 = Clipboard page
            2 = Library page
        '''
        pageIndex = self.mmkit_tab.currentPageIndex()

        if page_id == pageIndex:
            return True
        else:
            return False
           
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
        '''Updates the clipboard page. '''
        self.pastableItems = self.w.assy.shelf.get_pastable_chunks()
        
        list = QStringList()
        for item in self.pastableItems:
            list.append(item.name)
        
        self.chunkListBox.clear()
        self.chunkListBox.insertStringList(list)
        if len(list): 
            #i = self.w.pasteComboBox.currentItem()
            i = self.chunkListBox.count() - 1 # last item in the listbox.
            if self.currentPageOpen(ClipboardPage):
                # setSelected() causes the clipboard page to be displayed when we don't want it to
                # be displayed (i.e. pressing Control+C to copy something to the clipboard).
                self.chunkListBox.setSelected(i, True)
        else:
            self.elemGLPane.updateModel(None)
        self.update_clipboard_page_icon()
        
    
    def update_clipboard_page_icon(self):
        '''Updates the Clipboard page (tab) icon with a full or empty clipboard icon.
        '''
        if sys.platform == 'darwin': 
            # Work around for bug 1659. mark 060310
            return
            
        if self.w.assy.shelf.get_pastable_chunks():
            clipboard_pm = imagename_to_pixmap("clipboard-full.png")
        else:
            clipboard_pm = imagename_to_pixmap("clipboard-empty.png")
        
        self.mmkit_tab.setTabIconSet (self.clipboardPage, QIconSet(clipboard_pm))

    
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
        libraryPageLayout = QVBoxLayout(self.libraryPage,4,2,"libraryPageLayout")
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

    def closeEvent(self, e):
        """This event handler receives all MMKit close events.  In other words,
        when this dialog's close() slot gets called, this gets called with event 'e'.
        """
        self.hide()
        
        # If the 'Library' page is open, change it to 'Atoms'.  Mark 051212.
        if self.currentPageOpen(LibraryPage):
            self.setup_current_page(self.atomsPage)
                       
    pass # end of class MMKit

# end