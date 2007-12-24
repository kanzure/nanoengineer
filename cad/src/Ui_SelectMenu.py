# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui

def setupUi(win):
    """
    Populates the "Select" menu, a submenu of the "Tools" menu.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    
    # Create and add the "Select" to the Tool menu.
    win.selectMenu = win.toolsMenu.addMenu("Select")
    
    # Populate the "Select" menu.
    win.selectMenu.addAction(win.selectAllAction)
    win.selectMenu.addAction(win.selectNoneAction)
    win.selectMenu.addAction(win.selectInvertAction)
    win.selectMenu.addAction(win.selectConnectedAction)
    win.selectMenu.addAction(win.selectDoublyAction)
    win.selectMenu.addAction(win.selectExpandAction)
    win.selectMenu.addAction(win.selectContractAction)
    
def retranslateUi(win):
    """
    Sets text related attributes for the "Select" submenu, 
    which is a submenu of the "Tools" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.selectMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&Selection", 
            None, QtGui.QApplication.UnicodeUTF8))
    
    