# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

from PyQt4 import QtGui

def setupUi(win):
    """
    Populates the "Edit" menu which appears in the main window menu bar.

    @param win: NE1's main window object.
    @type  win: Ui_MainWindow
    """

    # Populate the "Edit" menu.
    win.editMenu.addAction(win.editMakeCheckpointAction) # hidden by default.
    win.editMenu.addAction(win.editUndoAction)
    win.editMenu.addAction(win.editRedoAction)
    win.editMenu.addAction(win.editAutoCheckpointingAction)
    win.editMenu.addAction(win.editClearUndoStackAction)
    win.editMenu.addSeparator()
    win.editMenu.addAction(win.editCutAction)
    win.editMenu.addAction(win.editCopyAction)
    win.editMenu.addAction(win.editPasteAction)
    win.editMenu.addAction(win.pasteFromClipboardAction)
    win.editMenu.addAction(win.editDeleteAction)
    win.editMenu.addSeparator()
    win.editMenu.addAction(win.editDnaDisplayStyleAction)
    win.editMenu.addAction(win.editProteinDisplayStyleAction)
    win.editMenu.addSeparator()
    win.editMenu.addAction(win.dispObjectColorAction)
    win.editMenu.addAction(win.dispObjectColorAction)
    win.editMenu.addSeparator()
    win.editMenu.addAction(win.dispObjectColorAction)
    win.editMenu.addAction(win.resetChunkColorAction)
    win.editMenu.addAction(win.colorSchemeAction)
    win.editMenu.addAction(win.lightingSchemeAction)
    win.editMenu.addSeparator()
    win.editMenu.addAction(win.editRenameSelectionAction)
    win.editMenu.addAction(win.editAddSuffixAction)

def retranslateUi(win):
    """
    Sets text related attributes for the "Edit" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.editMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&Edit",
            None, QtGui.QApplication.UnicodeUTF8))