# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
The model tree display widget.

[temporarily owned by Bruce, circa 050107, until further notice]

$Id$
"""

from qt import *
from constants import *
from chem import *
from gadgets import *
from Utility import *
from selectMode import selectMode
import sys, os

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

        # Single Item Selected Menu
        self.singlemenu = self.makemenu([
            ["Hide", self.hide],
            ["Unhide", self.unhide],
            None,
            ["Copy", self.copy],
            ["Cut", self.cut],
            ["Delete", self.kill],
            None,
            ["Properties", self.modprop],
            ])

        # Multiselected Menu
        self.multimenu = self.makemenu([
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
            
        # Part Node Menu
        self.partmenu = self.makemenu([
            ["Properties", self.modprop],
            ])
            
        # Clipboard Menu
        self.clipboardmenu = self.makemenu([
            ["Delete", self.kill],
            None,
            ["Properties", self.modprop],
            ])
        
        self.mt_update()
        
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
        # bruce comment 041220: this is called when widget signals that
        # user clicked on an item, or on blank part of model tree (confirmed by
        # experiment). Event (with mod keys flags) would be useful,
        # but is evidently not available (maybe it could be, in some other way?)
        # [addendum, 041227: it might be sufficient to wrap this with a subclass
        #  which defines an "event" method to process all events, making a note
        #  of their flags, then handing it off to the superclass event method. ###@@@]
        if item:
            if item.object.name == self.assy.name:
                return
        
        self.win.assy.unpickatoms()
        
        if isinstance(self.win.glpane.mode, selectMode): 
            self.win.toolsSelectMolecules()
                #e should optim:
                # this calls repaintGL redundantly with win.win_update() [bruce 041220]
        else:        
            self.win.assy.selwhat = 2
        
        if not self.modifier:
            # bruce comment 041220: some bugs are caused by this being wrong,
            # e.g. bug 263 (my comment #3 in there explains the likely cause).
            self.win.assy.unpickparts()
        
        if item: 
            if self.modifier == 'Cntl':
                item.object.unpick()
                self.selectedItem = None
            else:
                item.object.pick()
                self.selectedItem = item.object
                ###@@@ why only the one item? [bruce question 041220]
            
        self.win.win_update()

    def keyPressEvent(self, e):
        key = e.key()
        import platform
        key = platform.filter_key(key) #bruce 041220 (needed for bug 93)
        if key == Qt.Key_Delete:
            # bruce 041220: this fixes bug 93 (Delete on Mac) when the model
            # tree has the focus; the fix for other cases is in separate code.
            # Note that the Del key (and the Delete key on non-Mac platforms)
            # never makes it to this keyPressEvent method, but is handled at
            # some earlier stage by the widget, and in a different way;
            # probably this happens because it's a menu item accelerator.
            # The Del key (or the Delete menu item) always directly runs
            # MWsemantics.killDo, regardless of focus.
            self.win.killDo()
            ## part of killDo: self.win.win_update()
        elif key == Qt.Key_Control:
            self.modifier = 'Cntl'
        elif key == Qt.Key_Shift:
            self.modifier = 'Shift'
        # bruce 041220: I tried passing other key events to the superclass,
        # QListView.keyPressEvent, but I didn't find any that had any effect
        # (e.g. arrow keys, letters) so I took that out.
        return
        
    def keyReleaseEvent(self, key):
        self.modifier = None
                        
    def menuReq(self, listItem, pos, col):
        """ Context menu items function handler for the Model Tree View """
        if listItem:
            self.selectedItem = listItem.object
            sdaddy = self.selectedItem.whosurdaddy()
            if sdaddy in ["ROOT","Data"]: 
                # This conditional should change.  There has to be a better check.
                # We get the partmenu if another object has the same name as the assy.
                # Mark 041225 (Merry Xmas!)
                if self.selectedItem.name == self.assy.name: 
                    self.partmenu.popup(pos, 1)
                return
        else:
            self.selectedItem = None
            return
        
        # Figure out which menu to display 
        # (This is kludgy - meant to be a quick fix for Alpha) - Mark
        treepicked = self.assy.tree.nodespicked() #Number of nodes picked in the MT
        clippicked = self.assy.shelf.nodespicked() #Number of nodes picked in the clipboard
#        print "MT.menuReq: selectedItem = ",self.selectedItem
#        print "treepicked =",treepicked,", clippicked =",clippicked
        if treepicked == 0 and clippicked == 0:
            return
        if clippicked:
             ###@@@ bruce 041227 comment: this test being first could be bad
            # for depositmode's current use of clipboard selection; but that use
            # is slated to be changed.
            self.clipboardmenu.popup(pos, 1)
        elif treepicked == 1:
            self.singlemenu.popup(pos, 1)
        elif treepicked > 1:
            self.multimenu.popup(pos, 1)
        self.mt_update()

    def changename(self, listItem, col, text):
        if col != 0: return

        # Huaicai: the following line to make sure file name is not just space
        text = text.stripWhiteSpace()
        
        # Check if there is text for the listitem's name.  If not, we must force an MT update.
        # Otherwise, the name will remain blank until the next MT update.
        # Mark [04-12-07]
        if text: 
            listItem.object.name = str(text)
            self.assy.modified = 1
        else: self.mt_update() # Force MT update.

    def beginrename(self, item, pos, col):
        if not item: return
        istr = str(item.text(0))
#        print "MT.py: beginrename: selected item: ",istr
        if col != 0: return
        if istr in [self.assy.name, "Clipboard"]: return
        item.startRename(0)

    def startDrag(self):
#        print "MT.startDrag: self.selectedItem = [",self.selectedItem,"]"
        if self.selectedItem:
            foo = QDragObject(self)
            foo.drag()

    def dropEvent(self, event):
        above = False
        pnt = event.pos() - QPoint(0,24)
        # mark comments [04-12-10]
        # We need to check where we are dropping the selected item.  We cannot allow it 
        # to be dropped into the Data group.  This is what we are checking for here.
        # mmtop = 5 top nodes * (
        #                treeStepSize (space b/w parent and child nodes = 20 pixels) + 
        #                5 pixels (space b/w nodes ))
        mttop = 5 * (self.treeStepSize() + 5) # Y pos past top 5 nodes of MT (after last datum plane node).
#        print "modelTree.dropEvent: mttop = ",mttop
        if pnt.y() < mttop:
            pnt.setY(mttop) # We dropped above the first chunk (onto datum plane/csys). Mark 041210
            above = True # If we move node, insert it above first node in MT.
        droptarget = self.itemAt(self.contentsToViewport(pnt))
        if droptarget:
            sdaddy = self.selectedItem.whosurdaddy() # Selected item's daddy (source)
            tdaddy = droptarget.object.whosurdaddy() # Drop target item's daddy (target)
#            print "Source selected item:", self.selectedItem,", sdaddy: ", sdaddy
#            print "Target drop item:", droptarget.object,", tdaddy: ", tdaddy
            if sdaddy == "Data": return # selected item is in the Data group.  Do nothing.
            if sdaddy == "ROOT": return # selected item is the part or clipboard. Do nothing.    
            if isinstance(droptarget.object, Group): above = True # If drop target is a Group
            self.selectedItem.moveto(droptarget.object, above)
#            if sdaddy != tdaddy: 
#                if sdaddy == "Clipboard" or droptarget.object.name == "Clipboard": 
#                    self.win.win_update() # Selected item moved to/from clipboard. Update both MT and GLpane.
#                    return
#            self.mt_update() # Update MT only
            self.win.win_update()

    def dragMoveEvent(self, event):
        event.accept()

    def mt_update(self): # bruce 050107 renamed this from 'update'
        """ Build the model tree of the current model
        [no longer named update, since that conflicts with QWidget.update]
        """
        self.assy = self.win.assy
        
        ###e bruce comment 041227: this might be a good place to record the
        # current scroll position so it can later be set to something similar.
        
        self.clear()
        
        # Mark comments [04-12-08]
        # The model tree (MT) is drawn bottom to top. - Mark [04-12-08]
        
        # Create the clipboard
        if self.assy.shelf.members: 
            self.assy.shelf.icon = self.clipboardFullIcon
            self.win.editPasteAction.setIconSet(QIconSet( self.clipboardFullIcon))
        else: 
            self.assy.shelf.icon = self.clipboardEmptyIcon
            self.win.editPasteAction.setIconSet(QIconSet( self.clipboardGrayIcon))
        
        # Add clipboard members
        self.shelf = self.assy.shelf.upMT(self)
        self.assy.shelf.setProp(self) # Update selected items in clipboard
        
        # Add part group members
        self.assy.tree.name = self.assy.name
        self.tree = self.assy.tree.upMT(self)
        
        # Add data members (Csys and datum planes)
        for m in self.assy.data.members[::-1]:
            m.upMT(self.tree)
            
        # Update any selected items in tree.
        self.assy.tree.setProp(self)

        ###e bruce comment 041227: this would be a good place to set the scroll
        # position to what it ought to be (to fix bug 177). ###@@@
 
## Context menu handler functions

    def group(self):
        node = self.assy.tree.hindmost()
        if not node: return # hindmost can return "None", with no "picked" attribute. Mark 401210.
        if node.picked: return
        new = Group(gensym("Group"), self.assy, node)
        self.tree.object.apply2picked(lambda(x): x.moveto(new))
        self.mt_update()
    
    def ungroup(self):
        self.tree.object.apply2picked(lambda(x): x.ungroup())
        self.mt_update()

    def hide(self):
        self.assy.Hide()
        
    def unhide(self):
        self.assy.Unhide()
    
    def copy(self):
        self.assy.copy()
        self.mt_update()
    
    def cut(self):
        self.assy.cut()
        self.mt_update()
    
    def kill(self):
        # note: this is essentially the same as MWsemantics.killDo. [bruce 041220 comment]
        self.assy.kill()
        self.win.win_update() # Changed from self.mt_update for deleting from MT menu. Mark [04-12-03]
    
    def modprop(self):
        if self.selectedItem: 
            self.selectedItem.edit()
            self.mt_update()

    def expand(self):
        self.tree.object.apply2tree(lambda(x): x.setopen())
        self.mt_update()

    # end of class modelTree
