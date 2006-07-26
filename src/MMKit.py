# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
MMKit.py

$Id$

History:

Created by Huaicai.

bruce 050913 used env.history in some places.

bruce has fixed some bugs in it.

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
import platform

# PageId constants for mmkit_tab
AtomsPage=0
ClipboardPage=1
LibraryPage=2

# debugging flags -- do not commit with True
debug_mmkit_events = False

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

        # It looks like we now have correct fixes for bugs 1659 and bug 1824. If so, it would be safe to simply
        # hardware self.icon_tabs to True and simplify code accordingly. But we're not 100% certain, so by leaving
        # it as a debug pref, we can help any users who see those bugs come up again.
        # wware 060420
        from debug_prefs import debug_pref, Choice_boolean_True
        self.icon_tabs = debug_pref("use icons in MMKit tabs?", Choice_boolean_True, prefs_key = "A7/mmkit tab icons")
            #e Changes to this only take effect in the next session.
            # Ideally we'd add a history message about that, when this is changed.
            # (It's not yet easy to do that in a supported way in debug_pref.) [bruce 060313]

        if not self.icon_tabs:
            self.mmkit_tab.setMargin ( 0 ) 
            self.mmkit_tab.setTabLabel (self.atomsPage, 'Atoms')
            self.mmkit_tab.setTabLabel (self.clipboardPage, 'Clipbd')
            self.mmkit_tab.setTabLabel (self.libraryPage, 'Lib')
        else:
            # Add icons to MMKit's tabs. mark 060223.
            atoms_pm = imagename_to_pixmap("atoms.png")
            self.mmkit_tab.setTabIconSet ( self.atomsPage, QIconSet(atoms_pm))
        
            clipboard_pm = imagename_to_pixmap("clipboard-empty.png")
            self.mmkit_tab.setTabIconSet ( self.clipboardPage, QIconSet(clipboard_pm)) # (modified in another method below)
        
            library_pm = imagename_to_pixmap("library.png")
            self.mmkit_tab.setTabIconSet ( self.libraryPage, QIconSet(library_pm))
        
        # Tab tooltips. mark 060326
        self.mmkit_tab.setTabToolTip (self.atomsPage, 'Atoms')
        self.mmkit_tab.setTabToolTip (self.clipboardPage, 'Clipboard')
        self.mmkit_tab.setTabToolTip (self.libraryPage, 'Part Library')
        
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

        return # from __init__

    # ==
    
    #bruce 060412 added everything related to __needs_update_xxx, to fix bugs 1726, 1629 and mitigate bug 1677;
    # for more info see the comments where update_clipboard_items is called (in depositMode.py).
        
    __needs_update_clipboard_items = False
        # (there could be other flags like this for other kinds of updates we might need)

    def update_clipboard_items(self):
        self.__needs_update_clipboard_items = True
        self.update() # this makes sure self.event will get called; it might be better to test the flag only in self.repaint, not sure
        return
    
    def event(self, event): #bruce 060412 debug code, but also checks all self.__needs_update_xxx flags (an essential bugfix)
        if debug_mmkit_events:
            print "debug: MMKit.event got %r, type %r" % (event, event.type())
                # Qt doc for QEvent lists 'enum type' codes; the subclass is also printed by %r
        
        if self.__needs_update_clipboard_items:
            self.__really_update_clipboard_items()
            self.__needs_update_clipboard_items = False
        
        res = MMKitDialog.event(self, event)
        if debug_mmkit_events:
            if res is not None:
                print "debug: MMKit.event returns %r" % (res,) # usually True, sometimes False
        # if we return None we get TypeError: invalid result type from MMKit.event()
        return res

    # ==
    
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
        self.w.pasteComboBox.setCurrentItem(itemId) # Fixes bug 1754. mark 060325
        self.emit(PYSIGNAL('chunkSelectionChanged'), (itemId,))
        
        self.elemGLPane.updateModel(newChunk)
        
    
    def __really_update_clipboard_items(self): #bruce 060412 renamed this from update_clipboard_items to __really_update_clipboard_items
        '''Updates the items in the clipboard's listview, if the clipboard is currently shown. '''
        if self.currentPageOpen(ClipboardPage): #bruce 060313 added this condition to fix bugs 1631, 1669, and MMKit part of 1627
            self._clipboardPageView() # includes self.update_clipboard_page_icon()
        else:
            self.update_clipboard_page_icon() # do this part of it, even if page not shown
        return
        
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

        # The following is absolute nonsense, and is part of what's breaking the fix of bug 2028,
        # so it needs to be revised, to give this assy a standard structure.
        # We'll have to find some other way to draw the hotspot singlet
        # (e.g. a reasonable, straightforward way). So we did -- MMKitView.always_draw_hotspot is True.
        # [bruce 060627]
        
##        # Move all stuff under assembly.tree into assy.shelf. This is needed to draw hotspot singlet
##        def addChild(child):
##            self.newModel.shelf.addchild(child)
##        
##        # Remove existing clipboard items from the libary part before adopting childern from 'tree'.
##        self.newModel.shelf.members = []
##        self.newModel.tree.apply2all(addChild)
##        
##        self.newModel.shelf.prior_part = None
##        self.newModel.part = Part(self.newModel, self.newModel.shelf)

        if 1: #bruce 060627
            self.newModel.update_parts() #k not sure if needed after readmmp)
            self.newModel.checkparts()
            if self.newModel.shelf.members:
                if platform.atom_debug:
                    print "debug warning: library part %r contains clipboard items" % mmpfile # we'll see if this is common
                    # happens for e.g. nanokids/nanoKid-C39H42O2.mmp
                for m in self.newModel.shelf.members[:]:
                    m.kill() #k guess about a correct way to handle them
                self.newModel.update_parts() #k probably not needed
                self.newModel.checkparts() #k probably not needed
            pass
            
        self.elemGLPane.updateModel(self.newModel)
                
    
    def _clipboardPageView(self):
        '''Updates the clipboard page. '''
        if not self.currentPageOpen(ClipboardPage):
            # (old code permitted this to be false below in 'if len(list):',
            #  but failed to check for it in the 'else' clause,
            #  thus causing bug 1627 [I think], now fixed in our caller)
            print "bug: _clipboardPageView called when not self.currentPageOpen(ClipboardPage)" #bruce 060313
            return
        
        self.pastableItems = self.w.assy.shelf.get_pastable_chunks()
        
        list = QStringList()
        for item in self.pastableItems:
            list.append(item.name)
        
        self.chunkListBox.clear()
        self.chunkListBox.insertStringList(list)
        if len(list): 
            i = self.w.pasteComboBox.currentItem()
            if self.currentPageOpen(ClipboardPage):
                # Make sure the clipboard page is open before calling selSelected(), because
                # setSelected() causes the clipboard page to be displayed when we don't want it to
                # be displayed (i.e. pressing Control+C to copy something to the clipboard).
                self.chunkListBox.setSelected(i, True)
            #bruce 060313 question: why don't we now have to pass the selected chunk to self.elemGLPane.updateModel? ###@@@
        else:
            self.elemGLPane.updateModel(None)
        self.update_clipboard_page_icon()
        
    
    def update_clipboard_page_icon(self):
        '''Updates the Clipboard page (tab) icon with a full or empty clipboard icon.
        '''
        if not self.icon_tabs:
            # Work around for bug 1659. mark 060310 [revised by bruce 060313]
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
       # Determine what directory to open.
       if self.w.assy.filename: odir = os.path.dirname(self.w.assy.filename)
       else: odir = env.prefs[workingDirectory_prefs_key]
        
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
            
    def get_location_ORIG(self, firstShow):
        '''Returns the best x, y screen coordinate for positioning the MMKit.
        If <firstShow> is True, the Model Tree width is set to 200 pixels.
        Should only be called MMKit has been created.
        '''

        if sys.platform == 'linux2' and firstShow:
            # Qt Notes: On X11 system, widgets do not have a frameGeometry() before show() is called.
            # This is why we have special case code in atom.py, MWsemantics.py and here to work
            # around this issue on Linux.  mark 060311.
            mmk_height = 500
        else:
            mmk_height = self.frameGeometry().height() 
                # <mmk_height> is wrong when firstShow is True.  This is due to a problem with the
                # Library's QListView (DirView) widget.  See DirView.__init__() for more info on this.
                # We compensate for <mmk_height>'s wrong value below. Mark 060222.

        buildmode_dashboard_height = self.w.depositAtomDashboard.frameGeometry().height()
        status_bar_height = self.w.statusBar().frameGeometry().height()
        
        # Compute the y coordinate
        y = self.w.geometry().y() \
            + self.w.geometry().height() \
            - mmk_height \
            - buildmode_dashboard_height \
            - status_bar_height
        
        # Make small adjustments to the y coordinate based on various situations for different platforms.   
        if firstShow:
            # Avoid traceback on Linux, because mmk_geometry isn't defined. wware 060224
            if sys.platform != 'linux2':
                y -= 58
                # This is to compensate for a strange bug related to the Library's QListView widget changing size
                # after the MMKit is created but not yet shown.  This bug causes <mmk_height> of the
                # MMKit be off by 58 pixels on Windows. MacOS and Linux will probably need a different value.
                # See DirView.__init__() for more info on this. mark 060222.
                
            self.w.mt.setGeometry(0,0,200,560) 
                # Set model tree width to 200. mark 060303.
                # Make sure this is really needed. I seem to remember that I tried initializing the MT to a width
                # of 200 pixels, but something wasn't working.  This may be needed, but my guess right now
                # is that it isn't required.  mark 060311.
        else:
            if sys.platform == 'linux2':
                y -= 33
        # Make sure the MMKit stays on the screen.
        y = max(0, y)
        x = max(4,self.w.geometry().x()) # Fixes bug 1636.  Mark 060310.

        #print "x=%d, y =%d" % (x,y)
        return x, y
        
    def get_location(self, firstShow):
        '''Returns the best x, y screen coordinate for positioning the MMKit.
        If <firstShow> is True, the Model Tree width is set to 200 pixels.
        Should only be called MMKit has been created.
        '''

        mmkit_height = self.frameGeometry().height()
        #&print "MMKit.get_location_NEW().MMKit height =", mmkit_height
        buildmode_dashboard_height = self.w.depositAtomDashboard.frameGeometry().height()
        status_bar_height = self.w.statusBar().frameGeometry().height()
        
        # Compute the y coordinate
        y = self.w.geometry().y() \
            + self.w.geometry().height() \
            - mmkit_height \
            - buildmode_dashboard_height \
            - status_bar_height
        
        # Make small adjustments to the y coordinate based on various situations for different platforms.   
        if firstShow:
            self.w.mt.setGeometry(0,0,200,560)
            if sys.platform == 'win32':
                y -= 58
                # This is to compensate for a strange bug related to the Library's QListView widget changing size
                # after the MMKit is created but not yet shown.  This bug causes <mmk_height> of the
                # MMKit be off by 58 pixels on Windows. MacOS and Linux will probably need a different value.
                # See DirView.__init__() for more info on this. mark 060222.
            if sys.platform == 'darwin':
                y -= 39 # Tested and working. mark 060315.
        
        if sys.platform == 'linux2':
            y -= 33 # Tested and working. mark 060315.

        # Make sure the MMKit stays on the screen.
        y = max(0, y)
        x = max(0, self.w.geometry().x()) # Fixes bug 1636.  Mark 060310.

        #&print "MMKit.get_location_NEW().x=%d, y =%d" % (x,y)
        return x, y
    
    num_polish = 0
    
    def polish(self):
        '''This slot is called after a widget has been fully created and before it is shown the very first time.
        Polishing is useful for final initialization which depends on having an instantiated widget. 
        This is something a constructor cannot guarantee since the initialization of the subclasses might not be finished.
        After this function, the widget has a proper font and palette and QApplication.polish() has been called.
        Remember to call QWidget's implementation when reimplementing this function.
        '''
        QWidget.polish(self) # call QWidget's polish() implementation
        self.num_polish += 1
        #&print "num_polish =", self.num_polish
        if self.num_polish < 2:
            # polish() is called twice; not sure why.  
            # Call move_to_best_location() only after the second polish signal since 
            # get_location() can only get self.frameGeometry() after that.
            return
        self.move_to_best_location(True)
        
    def move_to_best_location(self, firstShow):
        x, y = self.get_location(firstShow)
        self.move(x, y)
        #&print "MMKit.move_to_best_location: x=%r, y=%r" % (x,y)
        
    def show(self):
        '''MMKit's show slot.
        '''
        QDialog.show(self)
        #&print "MMKit.move: setting mainwindow to active window"
        self.w.setActiveWindow() # Fixes bug 1503.  mark 060216.
            # Required to give the keyboard input focus back to self (MainWindow).
        
    pass # end of class MMKit

# end
