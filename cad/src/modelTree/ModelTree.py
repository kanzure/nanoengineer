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
    
    def resetAssy_and_clear(self):
        """
        This method should be called from the end of MWsemantics._make_and_init_assy.
        """
        # REVIEW: not sure if this method is still needed at all.
        # An old comment about an old version of this method:
        # #bruce 050201 for Alpha, part of Huaicai's bug 369 fix;
        # called to prevent a crash on (at least) Windows during File->Close
        # when the model tree is editing an item's text in-place, using a fix
        # developed by Huaicai 050201, which is to run the (Qt3) QListView
        # method self.clear().
        # Sometime during or after the port to Q4, it became equivalent to just
        # mt_update, albeit inside a couple calls of an old ModelTreeGUI_api
        # method update_item_tree. [bruce 081216 comment]
        self.mt_update()
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
