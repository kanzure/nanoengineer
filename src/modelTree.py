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
from selectMode import selectMode
import sys, os

CHANGE_FROM_TREE = True
CHANGE_FROM_GL = True

class modelTree(QListView):
    def __init__(self, parent, win):
        QListView.__init__(self,parent,"modelTreeView")
        self.addColumn("Model Tree")
        self.win = win
        self.assy = win.assy

        self.header().setClickEnabled(0, self.header().count() - 1)
        self.setGeometry(QRect(0, 0, 200, 560))
        self.setSizePolicy(QSizePolicy(0,7,0,244,False))
        self.setResizePolicy(QScrollView.Manual)
        self.setShowSortIndicator(0)
        self.setAcceptDrops(True)

        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.molDefaultIcon = QPixmap(filePath + "/../images/moldefault.png")
        self.molInvisibleIcon = QPixmap(filePath + "/../images/molinvisible.png")
        self.molVDWIcon = QPixmap(filePath + "/../images/molvdw.png")
        self.molLinesIcon = QPixmap(filePath + "/../images/mollines.png")
        self.molCPKIcon = QPixmap(filePath + "/../images/molcpk.png")
        self.molTubesIcon = QPixmap(filePath + "/../images/moltubes.png")
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
        self.clipboardGrayIcon = QPixmap(filePath + "/../images/clipboard-gray.png")
        self.statIcon = QPixmap(filePath + "/../images/stat.png")
        
        self.setSorting(-1)
        self.setRootIsDecorated(1)
        self.setSelectionMode(QListView.Extended)
        self.selectedItem = None
        self.modifier = None

        # Model Tree Menu
        self.menu = self.makemenu([
            ["Group", self.group],
            ["Ungroup", self.ungroup],
            None,
            ["Hide", self.hide],
            ["Show", self.unhide],
            None,
            ["Copy", self.copy],
            ["Cut", self.cut],
            ["Delete", self.kill],
            None,
            ["Properties", self.modprop],
            ])
        
        self.update()
        
        # Mark and Huaicai - commented this out -
        # causing a bug for context menu display on windows
        # Fixed with the signal to "rightButtonPressed"
        if sys.platform != 'win32':
            self.connect(self, SIGNAL("contextMenuRequested(QListViewItem*, const QPoint&,int)"),
                         self.menuReq)
        else:             
            self.connect(self, SIGNAL("rightButtonPressed(QListViewItem*,const QPoint&,int)"),
                         self.menuReq)
            
        self.connect(self, SIGNAL("clicked(QListViewItem *)"), self.select)
        self.connect(self, SIGNAL("expanded(QListViewItem *)"), self.treeItemExpanded)
        self.connect(self, SIGNAL("collapsed(QListViewItem *)"), self.treeItemCollapsed)
        self.connect(self, SIGNAL("itemRenamed(QListViewItem*, int, const QString&)"),
                self.changename)
        self.connect(self, SIGNAL("doubleClicked(QListViewItem*, const QPoint&, int)"),
                self.beginrename)

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
            if listItem not in [self.tree, self.shelf]:
                listItem.setPixmap(0, self.groupOpenIcon)


    def treeItemCollapsed(self, listItem):
        itemObj = listItem.object
        if isinstance(itemObj, Group):
            itemObj.open = False
            if listItem not in [self.tree, self.shelf]:
                listItem.setPixmap(0, self.groupCloseIcon)


    def select(self, item):
        self.win.assy.unpickatoms()
        
        if isinstance(self.win.glpane.mode, selectMode): 
                self.win.toolsSelectMolecules()
        else:        
                self.win.assy.selwhat = 2
        
        if not self.modifier: self.win.assy.unpickparts()
        
        if item: 
            if self.modifier == 'Cntl':
                item.object.unpick()
                self.selectedItem = None
            else:
                item.object.pick()
                self.selectedItem = item.object
            
        self.win.update()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Control:
            self.modifier = 'Cntl'
        if e.key() == Qt.Key_Shift:
            self.modifier = 'Shift'
        
    def keyReleaseEvent(self, key):
        self.modifier = None

    def menuReq(self, listItem, pos, col):
        """ Context menu items function handler for the Model Tree View """
        if listItem: self.selectedItem = listItem.object
        else: self.selectedItem = None
        self.menu.popup(pos, 1)
        self.update()

    def changename(self, listItem, col, text):
        if col != 0: return
        self.assy.modified = 1
        listItem.object.name = str(text)
        
    def beginrename(self, item, pos, col):
        istr = str(item.text(0))
#        print "MT.py: beginrename: selected item: ",istr
        if col != 0: return
        if istr in [self.assy.name, "Clipboard"]: return
        item.startRename(0)

    def startDrag(self):
        if self.selectedItem:
            foo = QDragObject(self)
            foo.drag()

    def dropEvent(self, event):
        pnt = event.pos() - QPoint(0,24)
        item = self.itemAt(self.contentsToViewport(pnt))
        if item:
            #print "Moving", self.selectedItem, "to", item.object
            self.selectedItem.moveto(item.object)
            self.update()
            #self.win.assy.root.dumptree()

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
        mitem.setRenameEnabled(0,True)
        return mitem
    
    def update(self):
        """ Build the tree structure of the current model
        """
        self.assy = self.win.assy
        self.clear()
        
        if self.assy.shelf.members: 
            self.assy.shelf.icon = self.clipboardFullIcon
            self.win.editPasteAction.setIconSet(QIconSet( self.clipboardFullIcon))
        else: 
            self.assy.shelf.icon = self.clipboardEmptyIcon
            self.win.editPasteAction.setIconSet(QIconSet( self.clipboardGrayIcon))
        
        self.shelf = self.assy.shelf.upMT(self, self)
        self.assy.shelf.setProp(self)
        
        self.assy.tree.name = self.assy.name
        
        self.tree = self.assy.tree.upMT(self, self)
        for m in self.assy.data.members[::-1]:
            m.upMT(self, self.tree)
        self.assy.tree.setProp(self)
 
## Context menu handler functions

    def group(self):
        node = self.assy.tree.hindmost()
        if node.picked: return
        new = Group(gensym("Node"), self.assy, node)
        self.tree.object.apply2picked(lambda(x): x.moveto(new))
        self.update()
    
    def ungroup(self):
        self.tree.object.apply2picked(lambda(x): x.ungroup())
        self.update()

    def hide(self):
        self.assy.Hide()
        
    def unhide(self):
        self.assy.Unhide()
    
    def copy(self):
        self.assy.copy()
        self.update()
    
    def cut(self):
        self.assy.cut()
        self.update()
    
    def kill(self):
        self.assy.kill()
        self.update()
    
    def modprop(self):
        if self.selectedItem: 
            self.selectedItem.edit()
            self.update()

    def expand(self):
        self.tree.object.apply2tree(lambda(x): x.setopen())
        self.update()