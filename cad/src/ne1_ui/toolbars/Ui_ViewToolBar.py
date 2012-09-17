# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

from PyQt4 import QtGui
from foundation.wiki_help import QToolBar_WikiHelp

def setupUi(win, toolbarArea):
    """
    Create and populate the "View" toolbar.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}

    @param toolbarArea: The ToolBarArea of the main window where this toolbar
                        will live (i.e. top, right, left, bottom).
    @type  toolbarArea: U{B{Qt.ToolBarArea enum}<http://doc.trolltech.com/4.2/qt.html#ToolBarArea-enum>}
    """

    # Create the "View" toolbar.
    win.viewToolBar = QToolBar_WikiHelp(win)
    win.viewToolBar.setEnabled(True)
    win.viewToolBar.setObjectName("viewToolBar")
    win.addToolBar(toolbarArea, win.viewToolBar)

    # Populate the "View" toolbar.
    win.viewToolBar.addAction(win.setViewHomeAction)
    win.viewToolBar.addAction(win.setViewFitToWindowAction)
    win.viewToolBar.addAction(win.setViewRecenterAction)
    win.viewToolBar.addAction(win.setViewZoomtoSelectionAction)
    win.viewToolBar.addAction(win.zoomToAreaAction)
    win.viewToolBar.addAction(win.zoomInOutAction)
    win.viewToolBar.addAction(win.panToolAction)
    win.viewToolBar.addAction(win.rotateToolAction)
    win.viewToolBar.addSeparator()
    win.viewToolBar.addAction(win.standardViewsAction) # A menu with views.
    win.viewToolBar.addAction(win.viewFlipViewVertAction)
    win.viewToolBar.addAction(win.viewFlipViewHorzAction)
    win.viewToolBar.addAction(win.viewRotatePlus90Action)
    win.viewToolBar.addAction(win.viewRotateMinus90Action)
    win.viewToolBar.addSeparator()
    win.viewToolBar.addAction(win.viewOrientationAction)
    win.viewToolBar.addAction(win.saveNamedViewAction)
    win.viewToolBar.addAction(win.viewNormalToAction)
    win.viewToolBar.addAction(win.viewParallelToAction)

def retranslateUi(win):
    """
    Assigns the I{window title} property of the "View", "Standard Views" and
    "Display Styles" toolbars.

    The window title of these toolbars will be displayed in the popup menu
    under "View > Toolbars".
    """
    win.viewToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "View",
            None, QtGui.QApplication.UnicodeUTF8))
    win.viewToolBar.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "View Toolbar",
            None, QtGui.QApplication.UnicodeUTF8))
