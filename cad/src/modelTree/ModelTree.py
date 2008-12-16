# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ModelTree.py -- owner and external interface to the NE1 model tree
(which is implemented as several objects by the modules in this
modelTree package)

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

modelTree.py was originally written by some combination of
Huaicai, Josh, and Mark. Bruce (Jan 2005) reorganized its interface with
Node and Group and their subclasses (Utility.py and other modules)
and rewrote a lot of the model-tree code (mainly to fix bugs),
and split it into three modules:

- TreeView.py (display and update),

- TreeWidget.py (event handling, and some conventions suitable for
  all our tree widgets, if we define other ones), and

- modelTree.py (customized for showing "the NE1 model tree" per se).

After that, Will ported it to Qt4, and since the Q3 compatibility
classes were unsupported by PyQt4, rewrote much of it, in the process
replacing TreeView.py and TreeWidget.py by a new file, modelTreeGui.py,
and adding a standalone prototype file modelTreePrototype.py (functional
as a separate test program, but not used by NE1). The current organization
might therefore be:

- modelTreeGui.py (display and update, event handling, and some
  conventions suitable for all our tree widgets, if we define other ones), and
  
- modelTree.py (customized for showing "the NE1 model tree" per se).

Bruce later rewrote much of modelTreeGui.py, and has added lots
of context menu commands to modelTree.py at various times.

Bruce 081216 is doing some cleanup and refactoring, including splitting
ModelTree and TreeModel into separate objects with separate classes and
_api classes, and splitting some code into separate files.
"""

from PyQt4 import QtCore

from modelTree.modelTreeGui import ModelTreeGui
from modelTree.TreeModel import TreeModel

# ===

class ModelTree(object):
    """
    NE1's main model tree, serving as public owner of the model tree widget
    (self.modelTreeGui, class ModelTreeGui) and private owner of the tree
    model shown by that (class TreeModel).

    @note: ModelTree is a public class name, and self.modelTreeGui
           is a public member.
    """
    #bruce 081216 renamed modelTree -> ModelTree, then split it into two objects
    # (ModelTree and TreeModel); removed _api class since incomplete and not
    # very useful, since all our methods are API methods and they are all small.
    def __init__(self, parent, win, name = "modelTreeView", size = (200, 560)):
        """
        #doc
        """
        self._treemodel = TreeModel(self, win) #bruce 081216
        
        ###@@@ review all init args & instvars, here vs subclasses
        self.modelTreeGui = ModelTreeGui(win, name, self._treemodel, parent)
            # WARNING: self.modelTreeGui is a PUBLIC MEMBER which is accessed by MWsemantics (at least)
            # for use in building the Qt widget layout. For public access purposes it can be considered
            # "the Qt widget containing the model tree" and it ought to have a special name (or get-method)
            # just for that purpose, so this attr could be made private.
            #    Worse, the code before late on 070509 sometimes stored self.modelTreeGui rather than self
            # in win.mt (maybe) and assy.mt (definitely), but other times stored self!
            # And lots of files call various methods on assy.mt and/or win.mt, namely:
            # - resetAssy_and_clear
            # - mt_update
            # and in mwsem:
            # - self.mt.setMinimumSize(0, 0)
            # - self.mt.setColumnWidth(0,225)
            # So for now, I made sure all those can be called on self (it was already true),
            # and in future, they need to be documented in the api, or the external calls should
            # call them explicitly on the widget member (accessing it in a valid public way).
            # [bruce 070509 comment]
            #update 081216: the above has probably all been taken care of, except for adding a
            # few methods to the api class, so that should be done and this comment removed.

##        # these attributes are probably not needed [bruce 081216 comment after refactoring]
##        self.win = win
##        self.assy = win.assy
        
        # note: there used to be self.view = self.modelTreeGui stored externally,
        # but this was never accessed, so I removed it along with the refactoring
        # [bruce 081216]

        self.mt_update()
        return
    
    def resetAssy_and_clear(self): #bruce 050201 for Alpha, part of Huaicai's bug 369 fix
        """
        This method should be called from the end of MWsemantics._make_and_init_assy
        to prevent a crash on (at least) Windows during File->Close when the mtree is
        editing an item's text, using a fix developed by Huaicai 050201,
        which is to run the QListView method self.clear().
           Neither Huaicai nor Bruce yet understands why this fix is needed or why
        it works, so the details of what this method does (and when it's called,
        and what's it's named) might change. Bruce notes that without this fix,
        MWsemantics._make_and_init_assy would change win.assy (but not tell the mt (self) to change
        its own .assy) and call mt_update(), which in old code would immediately do
        self.clear() but in new code doesn't do it until later, so this might relate
        to the problem. Perhaps in the future, mt_update itself can compare self.assy
        to self.win.assy and do this immediate clear() if they differ, so no change
        would be needed to MWsemantics._make_and_init_assy(), but for now, we'll just do it
        like this.
        """
        self.modelTreeGui.update_item_tree( unpickEverybody = True )
        # prevents Windows crash if an item's text is being edited in-place
        # [huaicai & bruce 050201 for Alpha to fix bug 369; not sure how it works]
        return

    def mt_update(self):
        # note: bruce 070509 changed a lot of calls of self.modelTreeGui.mt_update to call self.mt_update.
        # note: bruce 070511 removed all direct sets here of mt_update_needed, since mt_update now sets it.
        return self.modelTreeGui.mt_update()

    def repaint_some_nodes(self, nodes): #bruce 080507, for cross-highlighting
        """
        For each node in nodes, repaint that node, if it was painted the last
        time we repainted self as a whole. (Not an error if it wasn't.)
        """
        self.modelTreeGui.repaint_some_nodes(nodes)
        return
    
    def setMinimumSize(self, h, w):
        return self.modelTreeGui.setMinimumSize(h, w)
    
    def setMaximumWidth(self, w): #k might not be needed
        return self.modelTreeGui.setMaximumWidth(w)
    
    def setColumnWidth(self, column, w):
        return self.modelTreeGui.setColumnWidth(column, w)
    
    def setGeometry(self, w, h): #k might not be needed
        return self.modelTreeGui.setGeometry(QtCore.QRect(0,0,w,h))

    pass # end of class ModelTree

# end
