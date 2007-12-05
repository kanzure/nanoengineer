# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from icon_utilities import geticon

def setupUi(win):
    """
    Creates and populates the "File" menu in the main menubar.
    
    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    #Note: here 'win' is just a mainwindow object. 

    MainWindow = win

    # Create the File menu and action items that will become menu items.
    win.fileMenu = QtGui.QMenu(win.MenuBar)
    win.fileMenu.setObjectName("fileMenu")

    win.fileOpenAction = QtGui.QAction(MainWindow)
    win.fileOpenAction.setIcon(geticon("ui/actions/File/Open"))
    win.fileOpenAction.setObjectName("fileOpenAction")

    win.fileCloseAction = QtGui.QAction(MainWindow)
    win.fileCloseAction.setObjectName("fileCloseAction")

    win.fileSaveAction = QtGui.QAction(MainWindow)
    win.fileSaveAction.setIcon(geticon("ui/actions/File/Save"))
    win.fileSaveAction.setObjectName("fileSaveAction")

    win.fileSaveAsAction = QtGui.QAction(MainWindow)
    win.fileSaveAsAction.setObjectName("fileSaveAsAction")

    win.fileImportAction = QtGui.QAction(MainWindow)
    win.fileImportAction.setObjectName("fileImportAction")

    win.fileExportAction = QtGui.QAction(MainWindow)
    win.fileExportAction.setObjectName("fileExportAction")

    win.fileSetWorkDirAction = QtGui.QAction(MainWindow)
    win.fileSetWorkDirAction.setObjectName("fileSetWorkDirAction")

    win.fileExitAction = QtGui.QAction(MainWindow)
    win.fileExitAction.setObjectName("fileExitAction")

    # Add action (menu) items to the file menu.
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
    Sets text related attributes for the File menu items.
    
    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    
    # Menu and SubMenu Titles
    win.fileMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&File", None, QtGui.QApplication.UnicodeUTF8))

    # Menu Item (Action items) text and icons
    # FILE MENU ITEMS
    win.fileOpenAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Open...", None, QtGui.QApplication.UnicodeUTF8))
    win.fileOpenAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
    win.fileOpenAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
    win.fileCloseAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Close", None, QtGui.QApplication.UnicodeUTF8))
    win.fileCloseAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Close", None, QtGui.QApplication.UnicodeUTF8))
    win.fileSaveAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Save", None, QtGui.QApplication.UnicodeUTF8))
    win.fileSaveAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
    win.fileSaveAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
    win.fileSaveAsAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Save &As...", None, QtGui.QApplication.UnicodeUTF8))
    win.fileSaveAsAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Save As", None, QtGui.QApplication.UnicodeUTF8))
    win.fileImportAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Import File...", None, QtGui.QApplication.UnicodeUTF8))
    win.fileImportAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Import File...", None, QtGui.QApplication.UnicodeUTF8))
    win.fileImportAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Import File", None, QtGui.QApplication.UnicodeUTF8))
    win.fileExportAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Export File...", None, QtGui.QApplication.UnicodeUTF8))
    win.fileExportAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Export File...", None, QtGui.QApplication.UnicodeUTF8))
    win.fileExportAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Export File", None, QtGui.QApplication.UnicodeUTF8))        
    win.fileExitAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "E&xit", None, QtGui.QApplication.UnicodeUTF8))
    win.fileExitAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))