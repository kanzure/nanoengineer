# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

from PyQt4 import QtGui
from foundation.wiki_help import QToolBar_WikiHelp

def setupUi(win, toolbarArea):
    """
    Creates and populates the "Build Tools" toolbar in the main window.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}

    @param toolbarArea: The ToolBarArea of the main window where this toolbar
                        will live (i.e. top, right, left, bottom).
    @type  toolbarArea: U{B{Qt.ToolBarArea enum}<http://doc.trolltech.com/4.2/qt.html#ToolBarArea-enum>}
    """

    # Create the "Build Tools" toolbar.
    win.buildToolsToolBar = QToolBar_WikiHelp(win)
    win.buildToolsToolBar.setEnabled(True)
    win.buildToolsToolBar.setObjectName("buildToolsToolBar")
    win.addToolBar(toolbarArea, win.buildToolsToolBar)

    # Populate the "Build Tools" toolbar.
    win.buildToolsToolBar.addAction(win.toolsFuseChunksAction)
    win.buildToolsToolBar.addAction(win.modifyDeleteBondsAction)
    win.buildToolsToolBar.addAction(win.modifyHydrogenateAction)
    win.buildToolsToolBar.addAction(win.modifyDehydrogenateAction)
    win.buildToolsToolBar.addAction(win.modifyPassivateAction)
    win.buildToolsToolBar.addAction(win.modifyStretchAction)
    win.buildToolsToolBar.addAction(win.modifyMergeAction)
    win.buildToolsToolBar.addAction(win.modifyMirrorAction)
    win.buildToolsToolBar.addAction(win.modifyInvertAction)
    win.buildToolsToolBar.addAction(win.modifyAlignCommonAxisAction)
    #win.buildToolsToolBar.addAction(win.modifyCenterCommonAxisAction)

def retranslateUi(win):
    """
    Assigns the I{window title} property of the "Build Tools" toolbar.

    The window title of the "Build Tools" toolbar will be displayed in the popup
    menu under "View > Toolbars".
    """
    win.buildToolsToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Build Tools",
            None, QtGui.QApplication.UnicodeUTF8))
    win.buildToolsToolBar.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Build Tools Toolbar",
            None, QtGui.QApplication.UnicodeUTF8))
