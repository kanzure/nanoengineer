# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui
from PyQt4.Qt import Qt
from wiki_help import QToolBar_WikiHelp

def setupUi(win):
    """
    Create and populate the "Display Styles" toolbar.
    
    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    
    # Create the "Display Styles" toolbar.
    win.displayStylesToolBar = QToolBar_WikiHelp(win)
    win.displayStylesToolBar.setEnabled(True)
    win.displayStylesToolBar.setObjectName("displayStylesToolBar")
    win.addToolBar(Qt.TopToolBarArea, win.displayStylesToolBar)    

    # Populate the "Display Styles" toolbar.
    win.displayStylesToolBar.addAction(win.dispDefaultAction)
    win.displayStylesToolBar.addAction(win.dispInvisAction)
    win.displayStylesToolBar.addAction(win.dispLinesAction)
    win.displayStylesToolBar.addAction(win.dispTubesAction)
    win.displayStylesToolBar.addAction(win.dispBallAction)
    win.displayStylesToolBar.addAction(win.dispCPKAction)
    win.displayStylesToolBar.addAction(win.dispDnaCylinderAction)
    win.displayStylesToolBar.addAction(win.dispCylinderAction)
    win.displayStylesToolBar.addAction(win.dispSurfaceAction)

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
