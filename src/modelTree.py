# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from RotaryMotorProp import RotaryMotorProp
from LinearMotorProp import LinearMotorProp
from MoleculeProp import MoleculeProp
from GroundProp import GroundProp
from TreeListViewItem import TreeListViewItem
from constants import *
from chem import *
from gadgets import *
from Utility import *
import sys, os


class modelTree(QListView):
    def __init__(self, parent, win):
        QListView.__init__(self,parent,"modelTreeView")
        self.addColumn("Model Tree")
        self.win = win        

        self.header().setClickEnabled(0, self.header().count() - 1)
        self.setGeometry(QRect(0, 0, 131, 560))
        self.setSizePolicy(QSizePolicy(0,7,0,244,False))
        self.setResizePolicy(QScrollView.Manual)
        self.setShowSortIndicator(0)
        self.viewport().setAcceptDrops(True)
         
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
    	self.moleculeIcon = QPixmap(filePath + "/../images/molecule.png")
        self.csysIcon = QPixmap(filePath + "/../images/csys.png")
        self.datumPlaneIcon = QPixmap(filePath + "/../images/datumplane.png") 
        self.partIcon = QPixmap(filePath + "/../images/part.png")
        self.rmotorIcon = QPixmap(filePath + "/../images/rotarymotor.png")
        self.lmotorIcon = QPixmap(filePath + "/../images/linearmotor.png")
       	self.insertHereIcon = QPixmap(filePath + "/../images/inserthere.png")
       	self.groundIcon = QPixmap(filePath + "/../images/ground.png")
       	self.groupOpenIcon = QPixmap(filePath + "/../images/group-expanded.png")
        self.groupCloseIcon = QPixmap(filePath + "/../images/group-collapsed.png")
        
        #self.dropItem = 0
        self.descendants = None
        self.oldCurrent = None
        self.presspos = None
        self.mousePressed = 0
        
        self.COPY = 0
        self.CUT = 1
        self.itemToPaste = None
        self.pasteMode = self.COPY

	# Dictionary stores the pair of (tree item, real model object)
        self.treeItems = {}
        self.objectToTreeItems = {} # Dictionary for pair of (real model object, tree item)
        self.hiddenItems =[]
    	self.selectedTreeItem = None
        self.lastSelectedItem = None
        
        self.setSorting(-1)
        self.setRootIsDecorated(1)
        #self.setSelectionMode(QListView.Extended)
        self.connect(self, 
                SIGNAL("rightButtonPressed(QListViewItem*,const QPoint&,int)"), 
                                                     self.processRightButton)
        self.connect(self, SIGNAL("selectionChanged(QListViewItem *)"), self.treeItemChanged)
        self.connect(self, SIGNAL("expanded(QListViewItem *)"), self.treeItemExpanded)
        self.connect(self, SIGNAL("collapsed(QListViewItem *)"), self.treeItemCollapsed) 
  
        self.updateModelTree()        
        self.setPopupMenus() 
        

##########------ Context menu processing functions-----#############
    def processCsysMenu(self, id):
          if id == 0: #Rename
              self.selectedTreeItem.startRename(0)
          else: # Set current view as default view
              assy = self.win.assy
              assy.csys.quat = Q(self.win.glpane.quat)

    def processTreeMenu(self, id):
        if id == 0: #Collapse
            self.collapseTree() 
        elif id ==1: # Expand
            self.expandTree()
        elif id == 2: # Hide
            pass    
        elif id == 3: # Unhide All"
            self.unhideTree()
        elif id == 4: # Filter
            pass
               
    def processMolMenu(self, id):
            if id == 0: #Copy
                 self.itemToPaste = self.selectedTreeItem
                 self.pasteMode = self.COPY
            elif id == 1: #Cut
                 self.itemToPaste = self.selectedTreeItem
                 self.pasteMode = self.CUT
            elif id == 2: #Delete
                 parentItem = self.selectedTreeItem.parent()
                 parentItem.takeItem(self.selectedTreeItem)
            elif id == 3: #Rename
                 self.selectedTreeItem.startRename(0)
            elif id == 4: #Hide/Unhide
                 self.hiddenItems += [self.selectedTreeItem]
                 self.selectedTreeItem.setVisible(False)
            elif id == 5: # Properties
                 molDialog = MoleculeProp(self.treeItems[self.selectedTreeItem])
                 if molDialog.exec_loop() == QDialog.Accepted:
                         self.updateModelTree()
                  
    def processJigMenu(self, id):
            if id == 0: #Delete
                  parentItem = self.selectedTreeItem.parent()
                  parentItem.takeItem(self.selectedTreeItem)
            elif id == 1: #Rename
                  self.selectedTreeItem.startRename(0)
            elif id == 2: #Hide/Unhide
                 self.hiddenItems += [self.selectedTreeItem]
                 self.selectedTreeItem.setVisible(False)            
            elif id == 3: # Properties
                jig = self.treeItems[self.selectedTreeItem]
                if isinstance(jig, motor):
                        rMotorDialog = RotaryMotorProp(jig, self.win.glpane)
                        if rMotorDialog.exec_loop() == QDialog.Accepted:
                                self.updateModelTree()
                elif isinstance(jig, LinearMotor):
                        lMotorDialog = LinearMotorProp(jig, self.win.glpane)
                        if lMotorDialog.exec_loop() == QDialog.Accepted:
                                self.updateModelTree()
                elif isinstance(jig, ground):
                        groundDialog = GroundProp(jig, self.win.glpane)
                        if groundDialog.exec_loop() == QDialog.Accepted:
                                self.updateModelTree()

    def processInsertHereMenu(self, id):
            if id == 0: #Paste
                  hereItem = self.objectToTreeItems[self.insertHereIcon]
                  tItem = hereItem.itemAbove()
                  if tItem.nextSibling() != hereItem:
                       tItem = tItem.parent()
                  self.pasteItem(tItem)
                  
            elif id == 1: #New Group
                  group = Group("New Group")
                  item = TreeListViewItem(self.rootItem, group.name)
                  item.setItemObject(group)
                  item.setPixmap(0, self.groupCloseIcon)
                  item.setDragEnabled(True)
                  item.setDropEnabled(True)
                  self.objectToTreeItems[group] = item
                  self.treeItems[item] = group
                  
                  hereItem = self.objectToTreeItems[self.insertHereIcon]
                  tItem = hereItem.itemAbove()
                  if tItem.nextSibling() != hereItem:
                       tItem = tItem.parent()
                  item.moveItem(tItem)
                  item.startRename(0)
                                                  
                  
    def setPopupMenus(self):
        self.treePopupMenu = QPopupMenu()
        self.treePopupMenu.insertItem("Collapse", 0)
        self.treePopupMenu.insertItem("Expand", 1)
        #self.treePopupMenu.insertItem("Hide", 2)
        self.treePopupMenu.insertItem("Unhide All", 3)
        #self.treePopupMenu.insertItem("Filter...", 4)
        self.connect(self.treePopupMenu, SIGNAL("activated(int)"), self.processTreeMenu)
        
        self.csysPopupMenu = QPopupMenu()
        self.csysPopupMenu.insertItem("Rename", 0)
        self.csysPopupMenu.insertItem("Set Home View", 1)
        self.connect(self.csysPopupMenu, SIGNAL("activated(int)"), self.processCsysMenu)
        
        self.molPopupMenu = QPopupMenu()
        self.molPopupMenu.insertItem("Copy", 0)
        self.molPopupMenu.insertItem("Cut", 1)
        self.molPopupMenu.insertItem("Delete", 2)
        self.molPopupMenu.insertItem("Rename", 3)
        self.molPopupMenu.insertItem("Hide/Unhide", 4)
        self.molPopupMenu.insertItem("Properties...", 5)
        self.connect(self.molPopupMenu, SIGNAL("activated(int)"), self.processMolMenu)
        
        self.jigPopupMenu = QPopupMenu()
        self.jigPopupMenu.insertItem("Delete", 0)
        self.jigPopupMenu.insertItem("Rename", 1)
        self.jigPopupMenu.insertItem("Hide/Unhide", 2)
        self.jigPopupMenu.insertItem("Properites...", 3)
        self.connect(self.jigPopupMenu, SIGNAL("activated(int)"), self.processJigMenu)

        
        self.insertHerePopupMenu = QPopupMenu()
        self.insertHerePopupMenu.insertItem("Paste", 0)
        self.insertHerePopupMenu.insertItem("New Group", 1)
        self.connect(self.insertHerePopupMenu, SIGNAL("activated(int)"), self.processInsertHereMenu)


############------ Slot functions-------------################
    def treeItemExpanded(self, listItem):
            itemObj = self.treeItems[listItem]
            if isinstance(itemObj, Group):
                    listItem.setPixmap(0, self.groupOpenIcon)
    
            
    def treeItemCollapsed(self, listItem):
            itemObj = self.treeItems[listItem]
            if isinstance(itemObj, Group):
                    listItem.setPixmap(0, self.groupCloseIcon)
    
            
    def treeItemChanged(self, listItem):
          if self.lastSelectedItem:
             modelItem = self.treeItems[self.lastSelectedItem]
             if isinstance(modelItem, molecule):
                modelItem.setSelectionState(self, modelItem, False)
 
          modelItem = self.treeItems[listItem]
          if isinstance(modelItem, molecule): 
                modelItem.setSelectionState(self,  modelItem, True)

          self.lastSelectedItem = listItem          
            
 
    def changeModelSelection(self, trigger, target, state):
          if self == trigger:  #don't respond if it is triggered by itself
               return
          # Find the corresponding tree item for the target and set the state
          if isinstance(target, molecule):
               item = self.objectToTreeItems[target]
               self.setSelected(item, state)
	
    def processRightButton(self, listItem, pos, col):
        """ Context menu items function handler for the Model Tree View """
        if col == -1: 
        #if not listItem or not self.isSelected(listItem) or col == -1:
           if not self.hiddenItems:
                   self.treePopupMenu.setItemEnabled(3, False)
           else:
                   self.treePopupMenu.setItemEnabled(3, True)
           self.treePopupMenu.exec_loop(pos)

        if listItem and self.isSelected(listItem):            
                self.selectedTreeItem = listItem
                clickedItem = self.treeItems[listItem]

                if isinstance(clickedItem, (LinearMotor, motor, ground)):
                        self.jigPopupMenu.exec_loop(pos)
                elif isinstance(clickedItem, molecule):
                        self.molPopupMenu.exec_loop(pos)
                elif listItem == self.objectToTreeItems[self.insertHereIcon]:
                        if self.itemToPaste:
                                self.insertHerePopupMenu.setItemEnabled(0, True)
                        else:
                                self.insertHerePopupMenu.setItemEnabled(0, False)
                        self.insertHerePopupMenu.exec_loop(pos)
                elif listItem == self.objectToTreeItems[self.csysIcon]:
                        self.csysPopupMenu.exec_loop(pos)  



###---------- Drag & Drop related functions------------------------###             

   # def contentsDragEnterEvent(self, e):
   #     self.oldCurrent = self.currentItem()
        
   #     i = self.itemAt(self.contentsToViewport(e.pos()))
   #     if i:
   #         self.dropItem = i
        

    def contentsDragMoveEvent(self, e):
        vp = self.contentsToViewport(e.pos())
        i = self.itemAt( vp )
        droppable = True
        
        if  i and i.dropEnabled() and i != self.oldCurrent:
            for child in self.descendants:
                   if child == i:
                        droppable = False
                        break
                    
            if droppable:
                self.setSelected( i, True )
                e.accept()
                e.acceptAction()
            else:
                e.ignore()    
        else:
           e.ignore()


    def contentsDragLeaveEvent(self, e):
        #autoopen_timer->stop();
        #self.dropItem = 0          
        
        self.setCurrentItem( self.oldCurrent )
        self.setSelected( self.oldCurrent, True )



    def contentsDropEvent(self, e ):
          item = self.itemAt(self.contentsToViewport(e.pos()))
          if not item or not item.parent() or not item.dropEnabled():
             return

          curObject = self.treeItems[item]
          oldObject = self.treeItems[self.oldCurrent]
          if isinstance(curObject, Group) and isinstance(oldObject, (molecule, Group)) :
                  parentItem = self.oldCurrent.parent()
                  parentItem.takeItem(self.oldCurrent)
                  item.insertItem(self.oldCurrent)
          else:        
                  self.oldCurrent.moveItem(item)


    def contentsMousePressEvent(self, e ):
        if e.button() == QMouseEvent.LeftButton:    
            p = QPoint(self.contentsToViewport(e.pos()))
            item = self.itemAt( p )
            if item and item.dragEnabled():
                 if self.rootIsDecorated(): i = 1
                 else: i = 0
            
            
        # if the user clicked into the root decoration of the item, don't try to start a drag!
                 if ( p.x() > self.header().sectionPos(self.header().mapToIndex(0)) +
                          self.treeStepSize() * ( item.depth() + i) + self.itemMargin() or
                         p.x() < self.header().sectionPos(self.header().mapToIndex(0))):
                       self.presspos = e.pos()
                       self.mousePressed = True
                       self.oldCurrent = item
        
        QListView.contentsMousePressEvent(self, e)
      


    def contentsMouseMoveEvent(self, e ):
       if self.mousePressed:
        # and (e.pos() - self.presspos).manhattanLength() > QApplication. startDragDistance() :
            self.mousePressed = False 
            #self.setOpen(self.oldCurrent, False)
            self.descendants = self.getDescendants(self.oldCurrent)
            dragObj = QDragObject(self.viewport())
            dragObj.drag()
            
       QListView.contentsMouseMoveEvent(self, e )         

    def contentsMouseReleaseEvent(self, e ):
        self.mousePressed = False
        QListView.contentsMouseReleaseEvent(self, e )
    
        
#############--- Utility functions--------#################
    def pasteItem(self, afterItem):
            mol = self.treeItems[self.itemToPaste]
            parentItem = afterItem.parent()
            newMol = None
            
            if self.pasteMode == self.COPY:
                offset = V(10.0, 10.0, 10.0)
                newMol = mol.copy(offset)
                newMol.name = "Copy of " + mol.name
                assy = self.win.assy
                assy.molecules += [newMol]
            
                mitem = TreeListViewItem(parentItem, newMol.name)
            else:
                mitem = TreeListViewItem(parentItem, mol.name)
                       
            if self.pasteMode == self.CUT:
                parentItem = self.itemToPaste.parent()
                parentItem.takeItem(self.itemToPaste)
        
            mitem.moveItem(afterItem)
            mitem.setPixmap(0, self.moleculeIcon)
            mitem.setDragEnabled(True)
            mitem.setDropEnabled(True)
            mitem.setRenameEnabled(0, True)
            
            if self.pasteMode == self.COPY:
                mitem.setItemObject(newMol)
                self.treeItems[mitem] = newMol
                self.objectToTreeItems[newMol] = mitem
            else:   
                mitem.setItemObject(mol)
                self.treeItems[mitem] = mol
                self.objectToTreeItems[mol] = mitem
                
            self.itemToPaste = None   

    def buildMoleculeTree(self, mol, parentItem):
                """ build tree structure for molecule"""
                mitem = TreeListViewItem(parentItem, mol.name)
                mitem.setItemObject(mol)
                mitem.setPixmap(0, self.moleculeIcon)
                mitem.setDragEnabled(True)
                mitem.setDropEnabled(True)
                mitem.setRenameEnabled(0, True)
                self.treeItems[mitem] = mol
                self.objectToTreeItems[mol] = mitem

                gIndex = 1
                mol.gadgets.reverse()
                for g in mol.gadgets:

#                   item = TreeListViewItem(mitem, g.__class__.__name__ + str(gIndex))
                   item = TreeListViewItem(mitem, g.name)
                   item.setItemObject(g)

                   if isinstance(g, ground):
                      item.setPixmap(0, self.groundIcon)
                   elif isinstance(g, motor):
                      item.setPixmap(0, self.rmotorIcon)
                   elif isinstance(g, LinearMotor):
                      item.setPixmap(0, self.lmotorIcon)
                         
                   item.setDragEnabled(False)
                   item.setDropEnabled(False)
                   item.setRenameEnabled(0, False)
                   self.treeItems[item] = g
                   self.objectToTreeItems[g] = item
                   gIndex += 1
                mol.gadgets.reverse()   
                
                   
    def buildGroupTree(self, group, parentItem):
                """ build tree structure for a group """
                item = TreeListViewItem(parentItem, group.name)
                item.setItemObject(group)
                item.setPixmap(0, self.groupCloseIcon)
                item.setDragEnabled(True)
                item.setDropEnabled(True)
                self.objectToTreeItems[group] = item
                self.treeItems[item] = group
                
                group.members.reverse()   
                for g in group.members:
                     if isinstance(g, molecule):
                          self.buildMoleculeTree(g, item)
                     else:
                          self.buildGroupTree(g, item)
                group.members.reverse()             
                                           

    def addTreeItem(self, obj):
        """create new model object, like molecule"""
        atItem =  self.objectToTreeItems[self.insertHereIcon]
        parentItem = atItem.parent()
        if isinstance(obj, molecule):
                mitem = TreeListViewItem(parentItem, obj.name)
                mitem.setItemObject(obj)
                mitem.setPixmap(0, self.moleculeIcon)
                mitem.setDragEnabled(True)
                mitem.setDropEnabled(True)
                mitem.setRenameEnabled(0, True)
                self.treeItems[mitem] =obj
                self.objectToTreeItems[obj] = mitem
     
                aboveItem = atItem.itemAbove()
                if aboveItem != parentItem:
                        sItem = aboveItem.nextSibling()
                        while  sItem!= atItem and aboveItem != self.rootItem:
                                aboveItem = aboveItem.itemAbove()
                                sItem = aboveItem.nextSibling()
                 
                        if aboveItem != self.rootItem:
                                mitem.moveItem(aboveItem)
                 
                   
            
    def updateModelTree(self):        
        """ Build the tree structure of the current model """
        self.clear()
        #global assyList

        #for assy in assyList:
        assy = self.win.assy
        self.rootItem = QListViewItem(self, assy.name)
        self.rootItem.setPixmap(0, self.partIcon)
        self.treeItems[self.rootItem] = assy
        self.objectToTreeItems[assy] = self.rootItem
            
        item = QListViewItem(self.rootItem, "Insert Here")
        item.setPixmap(0, self.insertHereIcon)
        item.setDragEnabled(True)
        item.setDropEnabled(False)
        self.objectToTreeItems[self.insertHereIcon] = item
        self.treeItems[item] = None
 
        assy.orderedItemsList.reverse()
        for m in assy.orderedItemsList:
                if isinstance(m, molecule):
                        self.buildMoleculeTree(m, self.rootItem)
                else:
                        self.buildGroupTree(m, self.rootItem)
        assy.orderedItemsList.reverse()
                   
        item = QListViewItem(self.rootItem, "RIGHT")
        item.setPixmap(0, self.datumPlaneIcon) 
        item.setDragEnabled(False)
        item.setDropEnabled(True)
        self.treeItems[item] = None
        
        item = QListViewItem(self.rootItem, "TOP")
        item.setPixmap(0, self.datumPlaneIcon) 
        item.setDragEnabled(False)
        item.setDropEnabled(False)
        self.treeItems[item] = None
        
        item = QListViewItem(self.rootItem, "FRONT")
        item.setPixmap(0, self.datumPlaneIcon) 
        item.setDragEnabled(False)
        item.setDropEnabled(False)
        self.treeItems[item] = None
        
        item = TreeListViewItem(self.rootItem, "Csys")
        
        item.setPixmap(0, self.csysIcon)
        item.setDragEnabled(False)
        item.setDropEnabled(False)
        item.setRenameEnabled(0, True)
        self.treeItems[item] = None
        self.objectToTreeItems[self.csysIcon] = item

        self.expandTree() # added by mark 9/28/2004
             

# added these basic methods for expanding, collapsing and unhiding the model tree. - mark 9/28/04
        
    def expandTree(self):
        child = self.firstChild()
        while child != None:
            self.setOpen(child, True)
            child = child.itemBelow()

    def collapseTree(self):            
        child = self.firstChild()
        while child != None:
            self.setOpen(child, False)
            child = child.itemBelow()
            
    def unhideTree(self):
        for item in self.hiddenItems:
            item.setVisible(True)
            self.hiddenItems = []

    def saveGroupItems(self, obj, item):
            child = item.firstChild()
            obj.members = []
            
            while child:
                cObj = self.treeItems[child]
                if isinstance(cObj, molecule):
                       obj.members += [cObj]
                elif isinstance(cObj, Group):
                       self.saveGroupItems(cObj, child)
                       obj.members += [cObj]
                            
                child = child.nextSibling()

    def saveModelTree(self):
        """ Update the information  for the model tree operation """
        assy =  self.win.assy
        assy.orderedItemsList = []
        it = self.firstChild().firstChild()
        
        while it:
                obj = self.treeItems[it]
                if isinstance(obj, molecule):
                      assy.orderedItemsList += [obj]
                elif isinstance(obj, Group):
                      self.saveGroupItems(obj, it)
                      assy.orderedItemsList += [obj]
                      
                it = it.nextSibling()
                
    def getDescendants(self, item):
        """ Get all the childern, grandchildren of the item """
        list = []
        nList = []
        
        child = item.firstChild()
        while child :
                list += [child]
                nList += [child]
                child = child.nextSibling()
                
        for m in nList:
              list += self.getDescendants(m)
         
        return list
                           