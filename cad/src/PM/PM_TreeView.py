#Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_TreeView.py

The PM_TreeView class provides a partlib object (as a 'treeview' of any user
specified directory) to the client code.
The parts from the partlib can be pasted in the 3D  Workspace.

@author: Bruce, Huaicai, Mark, Ninad
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

ninad 2007-09-06: Created.
"""

from PyQt4.Qt import QTreeView
from PyQt4.Qt import QDir
from PyQt4.Qt import QDirModel
from PyQt4.Qt import Qt

import os
import foundation.env as env
import sys

from utilities.Log import redmsg

class PM_TreeView(QTreeView):
    """
    The PM_TreeView class provides a partlib object (as a 'treeview' of any user
    specified directory) to the client code. The parts from the partlib can be
    pasted in the 3D  Workspace.
    """
    def __init__(self, parent):
        """
        The constructor of PM_TreeView class that provides provides a partlib
        object (as a 'treeview' of any user specified directory) to the
        client code. The parts from the partlib can be pasted in the 3D
        Workspace.
        """
        QTreeView.__init__(self, parent)
        self.parent = parent
        self.setEnabled(True)

        self.model = QDirModel(
            ['*.mmp', '*.MMP'], # name filters
            QDir.AllEntries|QDir.AllDirs|QDir.NoDotAndDotDot, # filters
            QDir.Name # sort order
            )

        # explanation of filters (from Qt 4.2 doc for QDirModel):
        # - QDir.AllEntries = list files, dirs, drives, symlinks.
        # - QDir.AllDirs = include dirs regardless of other filters
        #   [guess: needed to ignore the name filters for dirs]
        # - QDir.NoDotAndDotDot = don't include '.' and '..' dirs
        #
        # about dirnames of "CVS":
        # The docs don't mention any way to filter the dirnames using a
        # callback, or any choices besides "filter them same as filenames" or
        # "don't filter them". So there is no documented way to filter out the
        # "CVS" subdirectories like we did in Qt3
        # (short of subclassing this and overriding some methods,
        #  but the docs don't make it obvious how to do that correctly).
        # Fortunately, autoBuild.py removes them from the partlib copy in built
        # releases.
        #
        # Other QDirModel methods we might want to use:
        # QDirModel.refresh, to update its state from the filesystem
        # (but see the docs --
        #  they imply we might have to pass the model's root pathname to that
        #  method,
        #  even if it hasn't changed, but they're not entirely clear on that).
        #
        # [bruce 070502 comments]

        self.path = None
        self.setModel(self.model)
        self.setWindowTitle(self.tr("Tree View"))

        self.setItemsExpandable(True)
        self.setAlternatingRowColors(True)
        self.setColumnWidth(0, 150)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setMinimumHeight(300)

        for i in range(2, 4):
            self.setColumnWidth(i, 4)

        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        libDir = os.path.normpath(filePath + '/../partlib')

        self.libPathKey = '/nanorex/nE-1/libraryPath'
        libDir = env.prefs.get(self.libPathKey, libDir)

        if os.path.isdir(libDir):
            self.rootDir = libDir
            self.setRootPath(libDir)
        else:
            self.rootDir = None
            env.history.message(redmsg("The part library directory: %s doesn't"\
                                       " exist." %libDir))

        self.show()

    #Ninad 070326 reimplementing mouseReleaseEvent and resizeEvent
    #for PM_TreeView Class (which is a subclass of QTreeView)
    #The old code reimplemented 'event' class which handles *all* events.
    #There was a bad bug which didn't send an event when the widget is resized
    # and then the seletcion is changed. In NE1Qt3 this wasn't a problem because
    #it only had one column. Now that we have multiple columns
    #(which are needed to show the horizontal scrollbar.
    # While using Library page only resize event or mouse release events
    #by the user should update the thumbview.
    #The Qt documentation also suggests reimplementing subevents instead of the
    #main event handler method (event())
    def mouseReleaseEvent(self, evt):
        """
        Reimplementation of mouseReleaseEvent method of QTreeView
        """
        if self.selectedItem() is not None:
            self.parent.partChanged(self.selectedItem())
        return QTreeView.mouseReleaseEvent(self, evt)

    def resizeEvent(self, evt):
        """
        Reimplementation of resizeEvent method of QTreeView
        """
        if self.selectedItem() is not None:
            self.parent.partChanged(self.selectedItem())
        return QTreeView.resizeEvent(self, evt)

    def setRootPath(self, path):
        """
        Set the root path for the tree view.
        @param path: The directory path to be set as a root path
        """
        self.path = path
        self.setRootIndex(self.model.index(path))

    def selectedItem(self):
        """
        Returns the Item selected in the QTreeview as a L{self.FileItem}
        @return: The Item selected in the QTreeview converted to a
                 L{self.FileItem} object
        @rtype: L{self.FileItem}
        """
        indexes = self.selectedIndexes()
        if not indexes:
            return None
        index = indexes[0]
        if not index.isValid():
            return None

        return self.FileItem(str(self.model.filePath(index)))

    class FileItem:
        """
        Class FileItem provides the filename object for class PM_TreeView
        """
        def __init__(self, path):
            """
            Constructor for the class
            """
            self.path = path
            dummy, self.fileName = os.path.split(path)
        def name(self):
            """
            Returns the file name
            @return: self.fileName
            """
            return self.fileName

        def getFileObj(self):
            """
            Returns file path (self.path)
            @return: L{self.path}
            """
            return self.path
