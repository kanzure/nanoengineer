# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from RotMotorProp import RotMotorProp
from LinearMotorProp import LinearMotorProp
from constants import *

class modelTree(QListView):
    def __init__(self, parent, win):
        QListView.__init__(self,parent,"modelTreeView")
        self.addColumn("Model Tree")
	self.win = win        

        self.header().setClickEnabled(0,self.header().count() - 1)
        self.setGeometry(QRect(0,0,131,560))
        self.setSizePolicy(QSizePolicy(0,7,0,244,False))
        self.setResizePolicy(QScrollView.Manual)
        self.setShowSortIndicator(0)

	# Dictionary stores the pair of (tree item, real model object)
        self.treeItems = {} 
	self.selectedTreeItem = None
        
        self.setSorting(-1)
	self.setRootIsDecorated(1)
        self.connect(self, 
                SIGNAL("rightButtonPressed(QListViewItem*,const QPoint&,int)"), 
                                                     self.processRightButton)

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
            rootItem.setPixmap(0,self.win.image1)
            self.treeItems[rootItem] = None

            item = QListViewItem(rootItem, "Tri-hedron")
	    item.setPixmap(0, self.win.image42)
            self.treeItems[item] = None
            item = QListViewItem(rootItem, "Datum plane")
            item.setPixmap(0, self.win.image2) 
            self.treeItems[item] = None
        
            for mol in assy.molecules:
                mitem = QListViewItem(rootItem, mol.name)
                mitem.setPixmap(0, self.win.image19)
                self.treeItems[mitem] = mol
                item = QListViewItem(mitem, "Total %d atoms" % len(mol.atoms))
                self.treeItems[item] = None

                gIndex = 1
                for g in mol.gadgets:
                   item = QListViewItem(mitem, g.__class__.__name__ + str(gIndex))
                   self.treeItems[item] = g
                   gIndex += 1
