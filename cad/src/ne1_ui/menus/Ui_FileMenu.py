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
    
    # Populate the "Import" submenu.
    win.importMenu.addAction(win.fileInsertMmpAction)
    win.importMenu.addAction(win.fileInsertPdbAction)
    win.importMenu.addAction(win.fileInsertInAction)
    win.importMenu.addSeparator()
    win.importMenu.addAction(win.fileImportOpenBabelAction)
    win.importMenu.addAction(win.fileImportIOSAction)
    
    #Populate the Fetch submenu
    win.fetchMenu.addAction(win.fileFetchPdbAction)
    
    # Populate the "Export" submenu.
    win.exportMenu.addAction(win.fileExportPdbAction)
    win.exportMenu.addAction(win.fileExportQuteMolXPdbAction)
    win.exportMenu.addSeparator()
    win.exportMenu.addAction(win.fileExportJpgAction)
    win.exportMenu.addAction(win.fileExportPngAction)
    win.exportMenu.addAction(win.fileExportPovAction)
    win.exportMenu.addAction(win.fileExportAmdlAction)
    win.exportMenu.addSeparator()
    win.exportMenu.addAction(win.fileExportOpenBabelAction)
    win.exportMenu.addAction(win.fileExportIOSAction)
    
    # Populate the "File" menu.
    win.fileMenu.addAction(win.fileOpenAction)
    win.fileMenu.addAction(win.fileCloseAction)
    win.fileMenu.addSeparator()
    win.fileMenu.addAction(win.fileSaveAction)
    win.fileMenu.addAction(win.fileSaveAsAction)
    win.fileMenu.addSeparator()
    win.fileMenu.addMenu(win.importMenu)
    win.fileMenu.addMenu(win.exportMenu)
    
    from utilities.GlobalPreferences import ENABLE_PROTEINS
    if ENABLE_PROTEINS:
        win.fileMenu.addMenu(win.fetchMenu)
        
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
    win.importMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Import", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.exportMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Export", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fetchMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Fetch", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.openRecentFilesMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Open Recent Files", 
            None, QtGui.QApplication.UnicodeUTF8))
