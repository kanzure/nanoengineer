# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
# 10/11 currently being owned by Huaicai
"""
The model tree display widget
$Id$
"""

from qt import *
from constants import *
from chem import *
from gadgets import *
from Utility import *
import sys, os

CHANGE_FROM_TREE = True
CHANGE_FROM_GL = True

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
        #self.setAcceptDrops(True)

        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.moleculeIcon = QPixmap(filePath + "/../images/molecule.png")
        self.csysIcon = QPixmap(filePath + "/../images/csys.png")
        self.datumIcon = QPixmap(filePath + "/../images/datumplane.png")
        self.partIcon = QPixmap(filePath + "/../images/part.png")
        self.rmotorIcon = QPixmap(filePath + "/../images/rotarymotor.png")
        self.lmotorIcon = QPixmap(filePath + "/../images/linearmotor.png")
        self.insertHereIcon = QPixmap(filePath + "/../images/inserthere.png")
        self.groundIcon = QPixmap(filePath + "/../images/ground.png")
        self.statIcon = QPixmap(filePath + "/../images/stat.png")
        self.groupOpenIcon = QPixmap(filePath + "/../images/group-expanded.png")
        self.groupCloseIcon = QPixmap(filePath + "/../images/group-collapsed.png")
        self.clipboardFullIcon = QPixmap(filePath + "/../images/clipboard-full.png")
        self.clipboardEmptyIcon = QPixmap(filePath + "/../images/clipboard-empty.png")
        self.statIcon = QPixmap(filePath + "/../images/stat.png")
        
        self.setFocusPolicy(QWidget.StrongFocus)

        self.setSorting(-1)
        self.setRootIsDecorated(1)
        self.setSelectionMode(QListView.Extended)
        self.selectedItem = None
        self.currentItem = None

        self.menu = self.makemenu([["Group", self.group],
                                   ["Ungroup", self.ungroup],
                                   None,
                                   ["Copy", self.copy],
                                   ["Cut", self.cut],
                                   ["Kill", self.kill],
                                   None,
                                   ["Properties", self.modprop],
                                   None,
                                   ["Expand all", self.expand],
                                   ["Hide Tree", self.hide]])
        
        self._update()
        
        # Mark and Huaicai - commented this out - causing a bug for context menu display
        # Fixed with the signal to "rightButtonPressed"
        if sys.platform != 'win32':
                self.connect(self, SIGNAL("contextMenuRequested(QListViewItem*, const QPoint&,int)"),
                     self.menuReq)
        else:             
                self.connect(self, SIGNAL("rightButtonPressed(QListViewItem*,const QPoint&,int)"),
                     self.menuReq)
        self.connect(self, SIGNAL("selectionChanged()"), self.select)
        self.connect(self, SIGNAL("expanded(QListViewItem *)"), self.treeItemExpanded)
        self.connect(self, SIGNAL("collapsed(QListViewItem *)"), self.treeItemCollapsed)
        self.connect(self, SIGNAL("itemRenamed(QListViewItem*, int, const QString&)"),
                     self.rename)
        


    def makemenu(self, lis): 
        """make and return a reusable popup menu from lis,
        which gives pairs of command names and callables"""
        win = self
        menu = QPopupMenu(win)
        for m in lis:
            if m:
                act = QAction(win,m[0]+'Action')
                act.setText(win.trUtf8(m[0]))
                act.setMenuText(win.trUtf8(m[0]))
                act.addTo(menu)
                win.connect(act, SIGNAL("activated()"), m[1])
            else:
                menu.insertSeparator()
        return menu


############------ Slot functions-------------################
    def treeItemExpanded(self, listItem):
        itemObj = listItem.object
        if isinstance(itemObj, Group):
            itemObj.open = True
            if listItem not in [self.root, self.shelf]:
                listItem.setPixmap(0, self.groupOpenIcon)


    def treeItemCollapsed(self, listItem):
        itemObj = listItem.object
        if isinstance(itemObj, Group):
            itemObj.open = False
            if listItem not in [self.root, self.shelf]:
                listItem.setPixmap(0, self.groupCloseIcon)


    def select(self):
                items = self.selectedItems()    
        
                self.disconnect(self, SIGNAL("selectionChanged()"), self.select)    

                self.win.assy.unpickatoms()
                self.win.assy.unpickparts()
                self.win.assy.selwhat = 2
        
                for item in items:
                        item.object.pick()
                
                self.win.glpane.paintGL()
                #self._update()
       
                self.connect(self, SIGNAL("selectionChanged()"), self.select)


    def menuReq(self, listItem, pos, col):
        """ Context menu items function handler for the Model Tree View """
        if listItem: 
             try:
                self.selectedItem = listItem.object
                self.menu.popup(pos, 1)
             except: 
                       print "What's the listItm? no object attribute?", listItem   
                       return
        else: 
                self.selectedItem = None
        

    def rename(self, listItem, col, text):
        if col != 0: return
        self.win.assy.modified = 1
        listItem.object.name = str(text)

    #def startDrag(self):
    #    if self.selectedItem:
    #        foo = QDragObject(self)
    #       foo.drag()

    #def dropEvent(self, event):
    #    pnt = event.pos() - QPoint(0,24)
    #    item = self.itemAt(self.contentsToViewport(pnt))
    #    if item:
    #        print "Moving", self.selectedItem, "to", item.object
    #        self.selectedItem.moveto(item.object)
    #        self.update()
    #        self.win.assy.model.dumptree()

    #def dragMoveEvent(self, event):
    #    event.accept()

    def buildNode(self, obj, parent, icon, dnd=True):
        """ build a display node in the tree widget
        corresponding to obj (and return it)
        """
        mitem = QListViewItem(parent, obj.name)
        mitem.object = obj
        mitem.setPixmap(0, icon)
        #mitem.setDragEnabled(dnd)
        #mitem.setDropEnabled(dnd)
        mitem.setRenameEnabled(0, True)
        return mitem
    
    
    def selectedItems(self):
        """ Find all selected tree items """
        items = []
        
        child = self.firstChild()
        while child:
                if child.isSelected():
                        items += [child]
                child = child.itemBelow()
        
        return items
        
        
    def _update(self):
        """ Build the tree structure of the current model, internal function """
        self.clear()
        
        if self.win.assy.shelf.members:
                self.win.assy.shelf.icon = self.clipboardFullIcon
        else:
                self.win.assy.shelf.icon = self.clipboardEmptyIcon
        self.shelf = self.win.assy.shelf.upMT(self, self)
        self.win.assy.shelf.setProp(self)
                
        
        rootGroup = Group(self.win.assy.name, self.win.assy, None)
        rootGroup.icon = self.partIcon
        
        for m in self.win.assy.tree.members[::-1]:
                oldDad = m.dad
                rootGroup.addmember(m)
                m.dad = oldDad
                 
        for m in self.win.assy.data.members[::-1]:
                rootGroup.addmember(m)
                 
        self.root = rootGroup.upMT(self, self)
        rootGroup.setProp(self)           

 
    def update(self):
        """ Build the tree structure of the current model, public interface """
        self.disconnect(self, SIGNAL("selectionChanged()"), self.select)
        self._update()
        self.connect(self, SIGNAL("selectionChanged()"), self.select)


## Context menu handler functions

    def group(self):
        node = self.root.object.hindmost()
        if node.picked: return
        new = Group(gensym("Node"), self.win.assy, node)
        self.root.object.apply2picked(lambda(x): x.moveto(new))
        self._update()
    
    def ungroup(self):
        self.root.object.apply2picked(lambda(x): x.ungroup())
        self._update()
    
    def copy(self):
        self.win.assy.copy()
        self._update()
    
    def cut(self):
        self.win.assy.cut()
        self._update()
    
    def kill(self):
        self.win.assy.kill()
        self._update()
    
    def modprop(self):
        if self.selectedItem: 
                self.selectedItem.edit()
                self._update()
            

    def expand(self):
        self.root.object.apply2tree(lambda(x): x.setopen())
        self._update()
