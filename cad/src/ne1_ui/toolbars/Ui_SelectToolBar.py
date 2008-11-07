# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui
from foundation.wiki_help import QToolBar_WikiHelp

def setupUi(win, toolbarArea):
    """
    Create and populate the "Select" toolbar.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    
    @param toolbarArea: The ToolBarArea of the main window where this toolbar
                        will live (i.e. top, right, left, bottom).
    @type  toolbarArea: U{B{Qt.ToolBarArea enum}<http://doc.trolltech.com/4.2/qt.html#ToolBarArea-enum>}
    """

    # Create the "Select" toolbar.
    win.selectToolBar = QToolBar_WikiHelp(win)
    win.selectToolBar.setEnabled(True)
    win.selectToolBar.setObjectName("selectToolBar")
    win.addToolBar(toolbarArea, win.selectToolBar)

    # Populate the "Select" toolbar.
    win.selectToolBar.addAction(win.selectLockAction)
    win.selectToolBar.addAction(win.selectAllAction)
    win.selectToolBar.addAction(win.selectNoneAction)
    win.selectToolBar.addAction(win.selectInvertAction)
    win.selectToolBar.addAction(win.selectConnectedAction)
    win.selectToolBar.addAction(win.selectDoublyAction)
    win.selectToolBar.addAction(win.selectExpandAction)
    win.selectToolBar.addAction(win.selectContractAction)
    win.selectToolBar.addAction(win.selectByNameAction)

def retranslateUi(win):
    """
    Assigns the I{window title} property of the "Select" toolbar.

    The window title of the "Select" toolbar will be displayed in the popup 
    menu under "View > Toolbars".
    """
    win.selectToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Select", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.selectToolBar.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Select Toolbar", 
            None, QtGui.QApplication.UnicodeUTF8))
