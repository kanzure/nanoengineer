# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""
from PyQt4 import QtGui
from foundation.wiki_help import QToolBar_WikiHelp

def setupUi(win, toolbarArea):
    """
    Creates and populates the "Standard" toolbar in the main window.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    
    @param toolbarArea: The ToolBarArea of the main window where this toolbar
                        will live (i.e. top, right, left, bottom).
    @type  toolbarArea: U{B{Qt.ToolBarArea enum}<http://doc.trolltech.com/4.2/qt.html#ToolBarArea-enum>}
    """

    # Create the "Standard" toolbar.
    win.standardToolBar = QToolBar_WikiHelp(win)
    win.standardToolBar.setEnabled(True)
    win.standardToolBar.setObjectName("standardToolBar") 
    win.addToolBar(toolbarArea , win.standardToolBar)

    # Populate the "Standard" toolbar.
    win.standardToolBar.addAction(win.fileOpenAction)
    win.standardToolBar.addAction(win.fileSaveAction)
    win.standardToolBar.addSeparator()
    win.standardToolBar.addAction(win.editMakeCheckpointAction) # hidden.
    win.standardToolBar.addAction(win.editUndoAction)
    win.standardToolBar.addAction(win.editRedoAction)
    win.standardToolBar.addAction(win.editCutAction)
    win.standardToolBar.addAction(win.editCopyAction)
    win.standardToolBar.addAction(win.pasteFromClipboardAction)
    win.standardToolBar.addAction(win.editDeleteAction)
    win.standardToolBar.addSeparator()
    win.standardToolBar.addAction(win.toolsSelectMoleculesAction)
    win.standardToolBar.addAction(win.toolsMoveMoleculeAction)
    win.standardToolBar.addAction(win.rotateComponentsAction)
    win.standardToolBar.addAction(win.modifyAdjustSelAction)
    win.standardToolBar.addAction(win.modifyAdjustAllAction)
    win.standardToolBar.addAction(win.simMinimizeEnergyAction)
    win.standardToolBar.addSeparator()
    win.standardToolBar.addAction(win.dispObjectColorAction)
    win.standardToolBar.addAction(win.resetChunkColorAction)
    win.standardToolBar.addSeparator()
    win.standardToolBar.addAction(win.colorSchemeAction)
    win.standardToolBar.addAction(win.lightingSchemeAction)
    win.standardToolBar.addSeparator()
    win.standardToolBar.addAction(win.editRenameSelectionAction)
    win.standardToolBar.addAction(win.editAddSuffixAction)
    win.standardToolBar.addSeparator()
    win.standardToolBar.addAction(win.editPrefsAction)    
    
    win.standardToolBar.addSeparator()  
    win.standardToolBar.addAction(win.helpWhatsThisAction)

def retranslateUi(win):
    """
    Assigns the I{window title} property of the "Standard" toolbar.

    The window title of the "Standard" toolbar will be displayed in the popup 
    menu under "View > Toolbars".
    """
    win.standardToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Standard", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.standardToolBar.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Standard Toolbar", 
            None, QtGui.QApplication.UnicodeUTF8))
