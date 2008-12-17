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
           is a public member, accessed by MWsemantics (or a subobject)
           for use in building the Qt widget layout. For public access
           purposes it can be considered "the Qt widget containing the model
           tree".
    """
    def __init__(self, parent, win, name = "modelTreeView", size = (200, 560)):
        """
        #doc
        """
        self._treemodel = TreeModel(self, win)
        
        self.modelTreeGui = ModelTreeGui(win, name, self._treemodel, parent)
            # public member; review: maybe it ought to have a special name
            # (or get-method) just for its public purpose, so this attr could
            # be made private for internal use

        self.mt_update()
        return
    
    def mt_update(self):
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
