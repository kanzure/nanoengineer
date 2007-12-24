# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id:$
"""

from PyQt4 import QtGui
from PyQt4.Qt import Qt
from wiki_help import QToolBar_WikiHelp

def setupUi(win):
    """
    Create and populate the "Standard Views" toolbar.
    
    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    
    # Create the "Standard Views" toolbar. 
    win.standardViewsToolBar = QToolBar_WikiHelp(win)
    win.standardViewsToolBar.setEnabled(True)
    win.standardViewsToolBar.setObjectName("standardViewsToolBar")
    win.addToolBar(Qt.TopToolBarArea, win.standardViewsToolBar)  
    
    # Populate the "Standard Views" toolbar.
    win.standardViewsToolBar.addAction(win.viewFrontAction)
    win.standardViewsToolBar.addAction(win.viewBackAction)
    win.standardViewsToolBar.addAction(win.viewLeftAction)
    win.standardViewsToolBar.addAction(win.viewRightAction)
    win.standardViewsToolBar.addAction(win.viewTopAction)
    win.standardViewsToolBar.addAction(win.viewBottomAction)
    win.standardViewsToolBar.addAction(win.viewIsometricAction)

def retranslateUi(win):
    """
    Assigns the I{window title} property of the "View", "Standard Views" and 
    "Display Styles" toolbars.
    
    The window title of these toolbars will be displayed in the popup menu 
    under "View > Toolbars".
    """
    win.standardViewsToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Standard Views", 
            None, QtGui.QApplication.UnicodeUTF8))
