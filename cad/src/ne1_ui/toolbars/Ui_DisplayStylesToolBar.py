# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

from PyQt4 import QtGui
from PyQt4.Qt import Qt
from foundation.wiki_help import QToolBar_WikiHelp

def setupUi(win, toolbarArea):
    """
    Create and populate the "Display Styles" toolbar.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}

    @param toolbarArea: The ToolBarArea of the main window where this toolbar
                        will live (i.e. top, right, left, bottom).
    @type  toolbarArea: U{B{Qt.ToolBarArea enum}<http://doc.trolltech.com/4.2/qt.html#ToolBarArea-enum>}
    """

    # Create the "Display Styles" toolbar.
    win.displayStylesToolBar = QToolBar_WikiHelp(win)
    win.displayStylesToolBar.setEnabled(True)
    win.displayStylesToolBar.setObjectName("displayStylesToolBar")
    win.addToolBar(toolbarArea, win.displayStylesToolBar)

    # Populate the "Display Styles" toolbar.
    win.displayStylesToolBar.addAction(win.dispDefaultAction)
    win.displayStylesToolBar.addAction(win.dispLinesAction)
    win.displayStylesToolBar.addAction(win.dispTubesAction)
    win.displayStylesToolBar.addAction(win.dispBallAction)
    win.displayStylesToolBar.addAction(win.dispCPKAction)
    win.displayStylesToolBar.addAction(win.dispDnaCylinderAction)
    win.displayStylesToolBar.addSeparator()
    win.displayStylesToolBar.addAction(win.dispHideAction)
    win.displayStylesToolBar.addAction(win.dispUnhideAction)

def retranslateUi(win):
    """
    Assigns the I{window title} property of the "Display Styles" toolbar.

    The window title of these toolbars will be displayed in the popup menu
    under "View > Toolbars".
    """
    win.displayStylesToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Display Styles",
            None, QtGui.QApplication.UnicodeUTF8))
    win.displayStylesToolBar.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Display Styles Toolbar",
            None, QtGui.QApplication.UnicodeUTF8))
