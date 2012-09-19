# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

from PyQt4 import QtGui

def setupUi(win):
    """
    Populates the "Selection" menu, a submenu of the "Tools" menu.

    @param win: NE1's main window object.
    @type  win: Ui_MainWindow
    """

    # Populate the "Select" menu.
    win.selectionMenu.addAction(win.selectLockAction)
    win.selectionMenu.addAction(win.selectAllAction)
    win.selectionMenu.addAction(win.selectNoneAction)
    win.selectionMenu.addAction(win.selectInvertAction)
    win.selectionMenu.addAction(win.selectConnectedAction)
    win.selectionMenu.addAction(win.selectDoublyAction)
    win.selectionMenu.addAction(win.selectExpandAction)
    win.selectionMenu.addAction(win.selectContractAction)
    win.selectionMenu.addAction(win.selectByNameAction)

def retranslateUi(win):
    """
    Sets text related attributes for the "Select" submenu,
    which is a submenu of the "Tools" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.selectionMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&Selection",
            None, QtGui.QApplication.UnicodeUTF8))

