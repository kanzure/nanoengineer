# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui

def setupUi(win):
    """
    Populates the "File" menu which appears in the main window menu bar.

    @param win: NE1's main window object.
    @type  win: Ui_MainWindow
    """

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
    
    # Create and add the "Open Recent Files" submenu.
    win.createOpenRecentFilesMenu()

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
    win.openRecentFilesMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Open Recent Files", 
            None, QtGui.QApplication.UnicodeUTF8))