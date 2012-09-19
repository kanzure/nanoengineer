# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Ui_RenderingToolBar.py - Toolbar for Rendering plug-ins like QuteMolX and
POV-Ray.

@author: Mark
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""

from PyQt4 import QtGui
from foundation.wiki_help import QToolBar_WikiHelp

def setupUi(win, toolbarArea):
    """
    Create and populate the "Rendering" toolbar.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}

    @param toolbarArea: The ToolBarArea of the main window where this toolbar
                        will live (i.e. top, right, left, bottom).
    @type  toolbarArea: U{B{Qt.ToolBarArea enum}<http://doc.trolltech.com/4.2/qt.html#ToolBarArea-enum>}
    """

    # Create the "Rendering" toolbar.
    win.renderingToolBar = QToolBar_WikiHelp(win)
    win.renderingToolBar.setEnabled(True)
    win.renderingToolBar.setObjectName("renderingToolBar")
    win.addToolBar(toolbarArea, win.renderingToolBar)

    # Populate the "Rendering" toolbar.
    win.renderingToolBar.addAction(win.viewQuteMolAction)
    win.renderingToolBar.addAction(win.viewRaytraceSceneAction)
    win.renderingToolBar.addSeparator()
    win.renderingToolBar.addAction(win.setStereoViewAction) # piotr 080516

def retranslateUi(win):
    """
    Assigns the I{window title} property of the "Rendering" toolbar.

    The window title of these toolbars will be displayed in the popup menu
    under "View > Toolbars".
    """
    win.renderingToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Rendering",
            None, QtGui.QApplication.UnicodeUTF8))
    win.renderingToolBar.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Rendering Toolbar",
            None, QtGui.QApplication.UnicodeUTF8))