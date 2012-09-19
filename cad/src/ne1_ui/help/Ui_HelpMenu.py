# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

from PyQt4 import QtGui

def setupUi(win):
    """
    Populates the "Help" menu which appears in the main window menu bar.

    @param win: NE1's main window object.
    @type  win: Ui_MainWindow
    """

    # Populate the "Help" menu.
    win.helpMenu.addAction(win.helpTutorialsAction)
    win.helpMenu.addAction(win.helpKeyboardShortcutsAction)
    win.helpMenu.addAction(win.helpMouseControlsAction)
    win.helpMenu.addAction(win.helpSelectionShortcutsAction)
    win.helpMenu.addAction(win.helpWhatsThisAction)
    win.helpMenu.addSeparator()
    win.helpMenu.addAction(win.helpGraphicsCardAction)
    win.helpMenu.addSeparator()
    win.helpMenu.addAction(win.helpAboutAction)

def retranslateUi(win):
    """
    Sets text related attributes for the "Help" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.helpMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&Help",
            None, QtGui.QApplication.UnicodeUTF8))