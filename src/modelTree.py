# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from RotMotorProp import RotMotorProp
from LinearMotorProp import LinearMotorProp
from constants import *
# from QUriDrag import *

class modelTree(QListView):
    def __init__(self, parent, win):
        QListView.__init__(self,parent,"modelTreeView")
        self.addColumn("Model Tree")
	    #self.win = win1        

        self.header().setClickEnabled(0, self.header().count() - 1)
        self.setGeometry(QRect(0, 0, 131, 560))
        self.setSizePolicy(QSizePolicy(0,7,0,244,False))
        self.setResizePolicy(QScrollView.Manual)
        self.setShowSortIndicator(0)
        self.viewport().setAcceptDrops(True)

    	self.assemblyIcon = QPixmap("../images/assembly.png")
        self.csysIcon = QPixmap("../images/csys.png")
        self.datumPlaneIcon = QPixmap("../images/datumplane.png") 
        self.partIcon = QPixmap("../images/part.png")
        self.motorIcon = QPixmap("../images/motor.png")
       	self.insertHereIcon = QPixmap("../images/inserthere.png")

        self.dropItem = 0
        self.oldCurrent = None
        self.presspos = None
        self.mousePressed = 0

	    # Dictionary stores the pair of (tree item, real model object)
        self.treeItems = {}
        self.objectToTreeItems = {} # Dictionary for pair of (real model object, tree item) 
    	self.selectedTreeItem = None
        self.lastSelectedItem = None
        
        self.setSorting(-1)
        self.setRootIsDecorated(1)
        self.connect(self, 
                SIGNAL("rightButtonPressed(QListViewItem*,const QPoint&,int)"), 
                                                     self.processRightButton)
        self.connect(self, SIGNAL("selectionChanged(QListViewItem *)"), self.treeItemChanged)


    	self.updateModelTree()        


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
             if modelItem.__class__.__name__ == 'molecule':
                modelItem.setSelectionState(self, modelItem, False)
 
          modelItem = self.treeItems[listItem]
          if modelItem.__class__.__name__ == 'molecule':
                modelItem.setSelectionState(self,  modelItem, True)

          self.lastSelectedItem = listItem          
            
 
    def changeModelSelection(self, trigger, target, state):
          if self == trigger:  #don't respond if it is triggered by itself
               return
          # Find the corresponding tree item for the target and set the state
          if target.__class__.__name__ == 'molecule':
               item = self.objectToTreeItems[target]
               self.setSelected(item, state)
	
    def processRightButton(self, listItem, pos, col):
        """ Context menu items function handler for the Model Tree View """
        if col == -1: return
        if not listItem or not self.isSelected(listItem): return 
        self.selectedTreeItem = listItem
        clickedItem = self.treeItems[listItem]

        if clickedItem.__class__.__name__ == 'LinearMotor':
           _popupMenu = QPopupMenu()
           editAction = QAction(self, 'linearMototEditAction')
           editAction.setText(self.trUtf8("&Edit..."))
           editAction.setMenuText(self.trUtf8("&Edit..."))
           editAction.addTo(_popupMenu)

           self.connect(editAction, SIGNAL("activated()"), self.editLinearMotor)
           _popupMenu.exec_loop(pos)
        
        elif clickedItem.__class__.__name__ == 'motor':
           _popupMenu = QPopupMenu()
           editAction = QAction(self, 'rotMototEditAction')
           editAction.setText(self.trUtf8("&Edit..."))
           editAction.setMenuText(self.trUtf8("&Edit..."))
           editAction.addTo(_popupMenu)

           self.connect(editAction, SIGNAL("activated()"), self.editRotMotor)
           _popupMenu.exec_loop(pos)
        


    def updateModelTree(self):
        """ Build the tree structure of the current model """
        self.clear()
        global assyList

        for assy in assyList:
            rootItem = QListViewItem(self, assy.name)
            rootItem.setPixmap(0, self.assemblyIcon)
            self.treeItems[rootItem] = assy
            self.objectToTreeItems[assy] = rootItem

            item = QListViewItem(rootItem, "Csys")
    	    item.setPixmap(0, self.csysIcon)
            item.setDragEnabled(False)
            item.setDropEnabled(True)
            self.treeItems[item] = None

            item = QListViewItem(rootItem, "Datum Plane")
            item.setPixmap(0, self.datumPlaneIcon) 
            item.setDragEnabled(False)
            item.setDropEnabled(True)
            self.treeItems[item] = None
        
            for mol in assy.molecules:
                mitem = QListViewItem(rootItem, mol.name)
                mitem.setPixmap(0, self.partIcon)
                mitem.setDragEnabled(False)
                mitem.setDropEnabled(True)
                self.treeItems[mitem] = mol
                self.objectToTreeItems[mol] = mitem

                item = QListViewItem(mitem, "Total %d atoms" % len(mol.atoms))
                self.treeItems[item] = None

                gIndex = 1
                for g in mol.gadgets:
                   item = QListViewItem(rootItem, g.__class__.__name__ + str(gIndex))
                   item.setPixmap(0, self.motorIcon)
                   item.setDragEnabled(False)
                   item.setDropEnabled(True)
                   self.treeItems[item] = g
                   self.objectToTreeItems[g] = item
                   gIndex += 1

        item = QListViewItem(self, "Insert Here")
        item.setPixmap(0, self.insertHereIcon)
        item.setDragEnabled(True)
        item.setDropEnabled(False)


    def contentsDragEnterEvent(self, e):
         e.accept(True)
        

    def contentsDragMoveEvent(self, e):
        vp = self.contentsToViewport(e.pos())
        i = self.itemAt( vp )
        if  i:
            self.setSelected( i, True )
            e.accept()
            e.acceptAction()
        else:
           e.ignore()


    def contentsDragLeaveEvent(self, e):
        #autoopen_timer->stop();
        self.dropItem = 0          #if ( not QDragObject.canDecode(e) ):
           #    e.ignore()
           #    return

        #self.oldCurrent = self.currentItem();

        #i = self.itemAt(self.contentsToViewport(e.pos()))
        #if i: 
        #   self.dropItem = i
        #    print "In DragEnterEvent: ", i
        #   #autoopen_timer->start( autoopenTime );

        self.setCurrentItem( self.oldCurrent )
        self.setSelected( self.oldCurrent, True )



    def contentsDropEvent(self, e ):
          item = self.itemAt(self.contentsToViewport(e.pos()))
          if not item:
             return

          if (item == item.parent().firstChild()):
                self.oldCurrent.moveItem(item)
                item.moveItem(self.oldCurrent)
          else:
                item = item.itemAbove() 
                self.oldCurrent.moveItem(item)


    def contentsMousePressEvent(self, e ):
        QListView.contentsMousePressEvent(self, e)
        p = QPoint(self.contentsToViewport(e.pos()))
        item = self.itemAt( p )
        if item:
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