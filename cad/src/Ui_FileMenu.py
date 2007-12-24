# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui

def setupUi(win):
    """
    Creates and populates the "File" menu in the main menubar.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """

    # Create the "File" menu.
    win.fileMenu = QtGui.QMenu(win.MenuBar)
    win.fileMenu.setObjectName("fileMenu")

    # Populate the "File" menu.
    win.fileMenu.addAction(win.fileOpenAction)
    win.fileMenu.addAction(win.fileCloseAction)
    win.fileMenu.addSeparator()
    win.fileMenu.addAction(win.fileSaveAction)
    win.fileMenu.addAction(win.fileSaveAsAction)
    win.fileMenu.addSeparator()
    win.fileMenu.addAction(win.fileImportAction)
    win.fileMenu.addAction(win.fileExportAction)
    win.fileMenu.addSeparator()
    win.fileMenu.addAction(win.fileExitAction)

def retranslateUi(win):
    """
    Sets text related attributes for the "File" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.fileMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&File", 
            None, QtGui.QApplication.UnicodeUTF8))