# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from RotaryMotorProp import RotaryMotorProp
from LinearMotorProp import LinearMotorProp
from TreeListViewItem import TreeListViewItem
from constants import *
from chem import *
from gadgets import *
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

        self.dropItem = 0
        self.oldCurrent = None
        self.presspos = None
        self.mousePressed = 0

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
     
    	self.updateModelTree()        
        self.setPopupMenus() 

                
    def processCsysMenu(self, id):
          if id == 0: #Rename
              self.selectedTreeItem.startRename(0)
          else: # Properties
              pass

    def processTreeMenu(self, id):
          if id == 0: #Collapse 
             child = self.firstChild()
             while child != None:
                      self.setOpen(child, False)
                      child = child.itemBelow()        
                       
          elif id ==1: # Expand
             child = self.firstChild()
             while child != None:
                      self.setOpen(child, True)
                      child = child.itemBelow()        
          
          elif id == 2: # Hide
               pass    
          elif id == 3: # Unhide All"
               for item in self.hiddenItems:
                    item.setVisible(True)
                    
               self.hiddenItems = []
                     
          elif id == 4: # Filter                    
               pass
               
    def processMolMenu(self, id):
            if id == 0: #Copy
                 pass
            elif id == 1: #Cut
                 pass
            elif id == 2: #Delete
                 pass#self.selectedTreeItem.takeItem(self.selectedTreeItem)
            elif id == 3: #Rename
                 self.selectedTreeItem.startRename(0)
            elif id == 4: #Hide/Unhide
                 self.hiddenItems += [self.selectedTreeItem]
                 self.selectedTreeItem.setVisible(False)
            elif id == 5: # Properties
                 pass
                  
    def processJigMenu(self, id):
            if id == 0: #Delete
                  pass#self.selectedTreeItem.takeItem(self.selectedTreeItem)
            elif id == 1: #Rename
                  self.selectedTreeItem.startRename(0)
            elif id == 2: #Hide/Unhide
                 self.hiddenItems += [self.selectedTreeItem]
                 self.selectedTreeItem.setVisible(False)            
            elif id == 3: # Properties
                jig = self.treeItems[self.selectedTreeItem]
                if isinstance(jig, motor):
                        rMotorDialog = RotaryMotorProp(jig)
                        rMotorDialog.show()
                        rMotorDialog.exec_loop()
                elif isinstance(jig, LinearMotor):
                        lMotorDialog = LinearMotorProp(jig)
                        lMotorDialog.show()
                        lMotorDialog.exec_loop()
                elif isinstance(jig, ground):
                        pass

                  
    def processInsertHereMenu(self, id):
            if id == 0: #Paste
                  pass
            elif id == 1: #New Group
                  pass                            
                  
    def setPopupMenus(self):
        self.treePopupMenu = QPopupMenu()
        self.treePopupMenu.insertItem("Collapse", 0)
        self.treePopupMenu.insertItem("Expand", 1)
        #self.treePopupMenu.insertItem("Hide", 2)
        self.treePopupMenu.insertItem("Unhide All", 3)
        self.treePopupMenu.insertItem("Filter...", 4)
        self.connect(self.treePopupMenu, SIGNAL("activated(int)"), self.processTreeMenu)
        
        self.csysPopupMenu = QPopupMenu()
        self.csysPopupMenu.insertItem("Rename", 0)
        self.csysPopupMenu.insertItem("Properties...", 1)
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


    def editLinearMotor(self):
        linearMotor = self.treeItems[self.selectedTreeItem]
        lMotorDialog = LinearMotorProp(linearMotor)
        lMotorDialog.show()
        lMotorDialog.exec_loop()    

    def editRotMotor(self):
        rotaryMotor = self.treeItems[self.selectedTreeItem]
        rMotorDialog = RotMotorProp(rotaryMotor)
        rMotorDialog.show()
        rMotorDialog.exec_loop()    


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
                        self.insertHerePopupMenu.exec_loop(pos)
                elif listItem == self.objectToTreeItems[self.csysIcon]:
                        self.csysPopupMenu.exec_loop(pos)  


    def updateModelTree(self):
        """ Build the tree structure of the current model """
        self.clear()
        #global assyList

        #for assy in assyList:
        assy = self.win.assy
        rootItem = QListViewItem(self, assy.name)
        rootItem.setPixmap(0, self.partIcon)
        self.treeItems[rootItem] = assy
        self.objectToTreeItems[assy] = rootItem
            
        item = QListViewItem(rootItem, "Insert Here")
        item.setPixmap(0, self.insertHereIcon)
        item.setDragEnabled(True)
        item.setDropEnabled(False)
        self.objectToTreeItems[self.insertHereIcon] = item
        self.treeItems[item] = None


        for mol in assy.molecules:
                mitem = TreeListViewItem(rootItem, mol.name)
                mitem.setItemObject(mol)
                mitem.setPixmap(0, self.moleculeIcon)
                mitem.setDragEnabled(False)
                mitem.setDropEnabled(True)
                mitem.setRenameEnabled(0, True)
                self.treeItems[mitem] = mol
                self.objectToTreeItems[mol] = mitem

                #item = QListViewItem(mitem, "Total %d atoms" % len(mol.atoms))
                #self.treeItems[item] = None

                gIndex = 1
                for g in mol.gadgets:
                   item = TreeListViewItem(mitem, g.__class__.__name__ + str(gIndex))
                   item.setItemObject(g)
                   if isinstance(g, ground):
                      item.setPixmap(0, self.groundIcon)
                   elif isinstance(g, motor):
                      item.setPixmap(0, self.rmotorIcon)
                   elif isinstance(g, LinearMotor):
                      item.setPixmap(0, self.lmotorIcon)
                         
                   item.setDragEnabled(False)
                   item.setDropEnabled(False)
                   item.setRenameEnabled(0, True)
                   self.treeItems[item] = g
                   self.objectToTreeItems[g] = item
                   gIndex += 1
            
        item = QListViewItem(rootItem, "RIGHT")
        item.setPixmap(0, self.datumPlaneIcon) 
        item.setDragEnabled(False)
        item.setDropEnabled(True)
        self.treeItems[item] = None
        
        item = QListViewItem(rootItem, "TOP")
        item.setPixmap(0, self.datumPlaneIcon) 
        item.setDragEnabled(False)
        item.setDropEnabled(False)
        self.treeItems[item] = None
        
        item = QListViewItem(rootItem, "FRONT")
        item.setPixmap(0, self.datumPlaneIcon) 
        item.setDragEnabled(False)
        item.setDropEnabled(False)
        self.treeItems[item] = None
        
        item = TreeListViewItem(rootItem, "Csys")
        
        item.setPixmap(0, self.csysIcon)
        item.setDragEnabled(False)
        item.setDropEnabled(False)
        item.setRenameEnabled(0, True)
        self.treeItems[item] = None
        self.objectToTreeItems[self.csysIcon] = item


             

    def contentsDragEnterEvent(self, e):
    #     e.accept(True)
        self.oldCurrent = self.currentItem()
        
        i = self.itemAt(self.contentsToViewport(e.pos()))
        if i:
            self.dropItem = i
        

    def contentsDragMoveEvent(self, e):
        vp = self.contentsToViewport(e.pos())
        i = self.itemAt( vp )

        if  i and i.dropEnabled():
            self.setSelected( i, True )
            e.accept()
            e.acceptAction()
        else:
           e.ignore()


    def contentsDragLeaveEvent(self, e):
        #autoopen_timer->stop();
        self.dropItem = 0          
        
        self.setCurrentItem( self.oldCurrent )
        self.setSelected( self.oldCurrent, True )



    def contentsDropEvent(self, e ):
          item = self.itemAt(self.contentsToViewport(e.pos()))
          if not item or not item.parent() or not item.dropEnabled():
             return

          self.oldCurrent.moveItem(item)


    def contentsMousePressEvent(self, e ):
        QListView.contentsMousePressEvent(self, e)
        p = QPoint(self.contentsToViewport(e.pos()))
        item = self.itemAt( p )
        if item and self.objectToTreeItems[self.insertHereIcon] == item:
            if self.rootIsDecorated(): i = 1
            else: i = 0

        # if the user clicked into the root decoration of the item, don't try to start a drag!
            if ( p.x() > self.header().sectionPos(self.header().mapToIndex(0)) +
                   self.treeStepSize() * ( item.depth() + i) + self.itemMargin() or
                   p.x() < self.header().sectionPos(self.header().mapToIndex(0))):
              self.presspos = e.pos()
              self.mousePressed = True
              self.oldCurrent = item



    def contentsMouseMoveEvent(self, e ):
       if (self.mousePressed):# and
                #(self.presspos - e.pos()).manhattanLength() > QApplication. startDragDistance()) :
            self.mousePressed = False
            item = self.itemAt( self.contentsToViewport(self.presspos) )
            if item:
                ud = QDragObject(self.viewport())
                ud.drag()
                

    def contentsMouseReleaseEvent(self, e ):
        self.mousePressed = False