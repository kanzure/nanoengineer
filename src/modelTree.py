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
        self.setAcceptDrops(True)

        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.moleculeIcon = QPixmap(filePath + "/../images/molecule.png")
        self.csysIcon = QPixmap(filePath + "/../images/csys.png")
        self.datumIcon = QPixmap(filePath + "/../images/datumplane.png")
        self.partIcon = QPixmap(filePath + "/../images/part.png")
        self.rmotorIcon = QPixmap(filePath + "/../images/rotarymotor.png")
        self.lmotorIcon = QPixmap(filePath + "/../images/linearmotor.png")
        self.insertHereIcon = QPixmap(filePath + "/../images/inserthere.png")
        self.groundIcon = QPixmap(filePath + "/../images/ground.png")
        self.groupOpenIcon = QPixmap(filePath + "/../images/group-expanded.png")
        self.groupCloseIcon = QPixmap(filePath + "/../images/group-collapsed.png")

        self.setSorting(-1)
        self.setRootIsDecorated(1)
        self.setSelectionMode(QListView.Extended)
        self.selectedItem = None

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
        self.update()

        self.connect(self, SIGNAL("contextMenuRequested(QListViewItem*, const QPoint&,int)"),
                     self.menuReq)
        self.connect(self, SIGNAL("clicked(QListViewItem *)"),
                     self.select)
        self.connect(self, SIGNAL("expanded(QListViewItem *)"),
                     self.treeItemExpanded)
        self.connect(self, SIGNAL("collapsed(QListViewItem *)"),
                     self.treeItemCollapsed)
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
            listItem.setPixmap(0, self.groupOpenIcon)


    def treeItemCollapsed(self, listItem):
        itemObj = listItem.object
        if isinstance(itemObj, Group):
            itemObj.open = False
            listItem.setPixmap(0, self.groupCloseIcon)

    def select(self, item):
        if not item: return
        self.win.assy.unpickatoms()
        self.win.assy.unpickparts()
        self.win.assy.selwhat = 2
        item.object.pick()
        self.selectedItem = item.object
        self.win.update()

    def menuReq(self, listItem, pos, col):
        """ Context menu items function handler for the Model Tree View """
        if listItem: self.selectedItem = listItem.object
        else: self.selectedItem = None
        self.menu.popup(pos, 1)
        self.update

    def rename(self, listItem, col, text):
        if col != 0: return
        listItem.object.name = str(text)

    def startDrag(self):
        if self.selectedItem:
            foo = QDragObject(self)
            foo.drag()

    def dropEvent(self, event):
        pnt = event.pos() - QPoint(0,24)
        item = self.itemAt(self.contentsToViewport(pnt))
        if item:
            print "Moving", self.selectedItem, "to", item.object
            self.selectedItem.moveto(item.object)
            self.update()
            self.win.assy.root.dumptree()

    def dragMoveEvent(self, event):
        event.accept()

    def buildNode(self, obj, parent, icon, dnd=True):
        """ build a display node in the tree widget
        corresponding to obj (and return it)
        """
        mitem = QListViewItem(parent, obj.name)
        mitem.object = obj
        mitem.setPixmap(0, icon)
        mitem.setDragEnabled(dnd)
        mitem.setDropEnabled(dnd)
        mitem.setRenameEnabled(0, True)
        return mitem

    def update(self):
        """ Build the tree structure of the current model """
        self.clear()
        self.root = self.win.assy.tree.upMT(self, self)
        self.win.assy.tree.setProp(self)
        self.shelf = self.win.assy.shelf.upMT(self, self)
        self.win.assy.shelf.setProp(self)
        self.data = self.win.assy.data.upMT(self, self, False)
        self.win.assy.data.setProp(self)
        return


## menu functions

    def group(self):
        node = self.root.object.hindmost()
        if node.picked: return
        new = Group(gensym("Node"), self.win.assy, node)
        self.root.object.apply2picked(lambda(x): x.moveto(new))
        self.update()
    
    def ungroup(self):
        self.root.object.apply2picked(lambda(x): x.ungroup())
        self.update()
    
    def copy(self):
        self.win.assy.copy()
    
    def cut(self):
        self.win.assy.cut()
    
    def kill(self):
        self.win.assy.kill()
        self.update()
    
    def modprop(self):
        if self.selectedItem: self.selectedItem.edit()            

    def expand(self):
        self.root.object.apply2tree(lambda(x): x.setopen())
        self.update()

    
