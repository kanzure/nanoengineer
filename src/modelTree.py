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
        self.groupOpenIcon = QPixmap(filePath + "/../images/group-expanded.png")
        self.groupCloseIcon = QPixmap(filePath + "/../images/group-collapsed.png")
        self.clipboardFullIcon = QPixmap(filePath + "/../images/clipboard-full.png")
        self.clipboardEmptyIcon = QPixmap(filePath + "/../images/clipboard-empty.png")
        self.clipboardGrayIcon = QPixmap(filePath + "/../images/clipboard-gray.png")
        
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
            ["Unhide", self.unhide],
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
        # Check if there is text for the listitem's name.  If not, we must force an MT update.
        # Otherwise, the name will remain blank until the next MT update.
        # Mark [04-12-07]
        if text: listItem.object.name = str(text)
        else: self.update() # Force MT update.

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
            #print "Moving", self.selectedItem, " to ", item.object
            self.selectedItem.moveto(item.object)
            # We only need to update the GLpane in the following 2 cases:
            #   1. The selected item is moved from the MT to the Clipboard
            #   2. The selected item is moved from the Clipboard to the MT
            # Since I don't know how to check for #2, I'm always updating the GLpane
            # after a dropEvent (Yuk).  I'll bother Bruce later - he's busy now.
            # Here is a start:
            #if item.object.name == "Clipboard": self.win.update # Case 1
            #elif ???: self.win.update Case 2
            #else: self.update() # Only update the MT (this is called 95% of the time)
            # 
            # Mark [04-12-08]
            self.win.update() # This will do for now.

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
        # A kludge.  Will fix for beta by implementing a "rename" method for Node class (and all sub-classes)
        # This works for now.  Mark [04-12-07]
        if obj.name != "Clipboard": mitem.setRenameEnabled(0,True) # kludge for Clipboard.
        return mitem
    
    def update(self):
        """ Build the tree structure of the current model
        """
        self.assy = self.win.assy
        self.clear()
        
        # Note: This model tree (MT) is draw bottom to top. - Mark [04-12-08]
        # Create the clipboard
        if self.assy.shelf.members: 
            self.assy.shelf.icon = self.clipboardFullIcon
            self.win.editPasteAction.setIconSet(QIconSet( self.clipboardFullIcon))
        else: 
            self.assy.shelf.icon = self.clipboardEmptyIcon
            self.win.editPasteAction.setIconSet(QIconSet( self.clipboardGrayIcon))
        
        # Add clipboard members
        self.shelf = self.assy.shelf.upMT(self, self)
        self.assy.shelf.setProp(self) # Update selected items in clipboard
        
        # Add part group members
        self.assy.tree.name = self.assy.name
        self.tree = self.assy.tree.upMT(self, self)
        
        # Add data members (Csys and datum planes)
        for m in self.assy.data.members[::-1]:
            m.upMT(self, self.tree)
            
        # Update any selected items in tree.
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
        self.win.update() # Changed from self.update for deleting from MT menu. Mark [04-12-03]
    
    def modprop(self):
        if self.selectedItem: 
            self.selectedItem.edit()
            self.update()

    def expand(self):
        self.tree.object.apply2tree(lambda(x): x.setopen())
        self.update()