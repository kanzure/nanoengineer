# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *


class TreeListViewItem(QListViewItem):
        def __init__(self, parent, label):
                QListViewItem.__init__(self, parent, label)
                
        def startRename(self, col):
                self.setRenameEnabled(col, True)
                QListViewItem.startRename(self, col)
                
                name = self.text(col)
                if name == "":
                        QListViewItem.startRename(self, col)
                        
        def okRename(self, col):
                oldText = self.text(col)
                QListViewItem.okRename(self, col)
                
                if self.text(col).isEmpty():
                        self.setText(col, oldText)
                        self.startRename(col)
                        
        def cancelRename(self, col):
                QListViewItem.cancelRename(self, col)        