# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from icon_utilities import geticon

def setupUi(win):
    MainWindow = win    
    
    win.editMenu = QtGui.QMenu(win.MenuBar)
    win.editMenu.setObjectName("editMenu")
    
    ##### Edit Menu Start #####
    
    win.editUndoAction = QtGui.QAction(MainWindow)
    win.editUndoAction.setIcon(geticon("ui/actions/Edit/Undo"))
    win.editUndoAction.setVisible(True)
    win.editUndoAction.setObjectName("editUndoAction")

    win.editRedoAction = QtGui.QAction(MainWindow)
    win.editRedoAction.setChecked(False)
    win.editRedoAction.setIcon(geticon("ui/actions/Edit/Redo"))
    win.editRedoAction.setVisible(True)
    win.editRedoAction.setObjectName("editRedoAction")
    
    win.editMakeCheckpointAction = QtGui.QAction(MainWindow)
    win.editMakeCheckpointAction.setIcon(geticon("ui/actions/Edit/Make_Checkpoint"))
    win.editMakeCheckpointAction.setObjectName("editMakeCheckpointAction")

    win.editAutoCheckpointingAction = QtGui.QAction(MainWindow)
    win.editAutoCheckpointingAction.setCheckable(True)
    win.editAutoCheckpointingAction.setChecked(True)
    win.editAutoCheckpointingAction.setObjectName("editAutoCheckpointingAction")

    win.editClearUndoStackAction = QtGui.QAction(MainWindow)
    win.editClearUndoStackAction.setObjectName("editClearUndoStackAction")
    
    win.editCutAction = QtGui.QAction(MainWindow)
    win.editCutAction.setEnabled(True)
    win.editCutAction.setIcon(geticon("ui/actions/Edit/Cut"))
    win.editCutAction.setObjectName("editCutAction")

    win.editCopyAction = QtGui.QAction(MainWindow)
    win.editCopyAction.setEnabled(True)
    win.editCopyAction.setIcon(geticon("ui/actions/Edit/Copy"))
    win.editCopyAction.setObjectName("editCopyAction")

    win.editPasteAction = QtGui.QAction(MainWindow)
    win.editPasteAction.setIcon(geticon("ui/actions/Edit/Paste_Off"))
    win.editPasteAction.setObjectName("editPasteAction")
    
    win.pasteFromClipboardAction = QtGui.QAction(MainWindow)
    win.pasteFromClipboardAction.setIcon(geticon(
        "ui/actions/Properties Manager/clipboard-full"))
    
    win.pasteFromClipboardAction.setObjectName("pasteFromClipboardAction")
    win.pasteFromClipboardAction.setText("Paste from clipboard...")
    
    win.editDeleteAction = QtGui.QAction(MainWindow)
    win.editDeleteAction.setIcon(geticon("ui/actions/Edit/Delete"))
    win.editDeleteAction.setObjectName("editDeleteAction")
    
    win.dispObjectColorAction = QtGui.QAction(MainWindow)
    win.dispObjectColorAction.setIcon(geticon("ui/actions/Edit/Edit_Color"))
    win.dispObjectColorAction.setObjectName("dispObjectColorAction")    
    
               
    ##### Edit Menu Ends #####
    
    win.editMenu.addAction(win.editMakeCheckpointAction)
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
    win.editMenu.addAction(win.dispObjectColorAction)
    
    
        
    
def retranslateUi(win):    
    win.editMenu.setTitle(QtGui.QApplication.translate("MainWindow", "&Edit", None, QtGui.QApplication.UnicodeUTF8))
    
    #EDIT MENU ITEMS
    win.editUndoAction.setText(QtGui.QApplication.translate("MainWindow", "&Undo",
                                                            None, QtGui.QApplication.UnicodeUTF8))
    win.editUndoAction.setIconText(QtGui.QApplication.translate("MainWindow", "Undo",
                                                                None, QtGui.QApplication.UnicodeUTF8))
    win.editUndoAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Z", 
                                                                None, QtGui.QApplication.UnicodeUTF8))
    win.editRedoAction.setText(QtGui.QApplication.translate("MainWindow", "&Redo", 
                                                            None, QtGui.QApplication.UnicodeUTF8))
    win.editRedoAction.setIconText(QtGui.QApplication.translate("MainWindow", "Redo", 
                                                                None, QtGui.QApplication.UnicodeUTF8))
    win.editRedoAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Y", 
                                                                None, QtGui.QApplication.UnicodeUTF8))
    win.editCutAction.setText(QtGui.QApplication.translate("MainWindow", "&Cut", 
                                                           None, QtGui.QApplication.UnicodeUTF8))
    win.editCutAction.setIconText(QtGui.QApplication.translate("MainWindow", "Cut", 
                                                               None, QtGui.QApplication.UnicodeUTF8))
    win.editCutAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+X", 
                                                               None, QtGui.QApplication.UnicodeUTF8))
    win.editCopyAction.setText(QtGui.QApplication.translate("MainWindow", "C&opy", 
                                                            None, QtGui.QApplication.UnicodeUTF8))
    win.editCopyAction.setIconText(QtGui.QApplication.translate("MainWindow", "Copy", 
                                                                None, QtGui.QApplication.UnicodeUTF8))
    win.editCopyAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+C", 
                                                                None, QtGui.QApplication.UnicodeUTF8))
    win.editPasteAction.setText(QtGui.QApplication.translate("MainWindow", "&Paste", 
                                                             None, QtGui.QApplication.UnicodeUTF8))
    win.editPasteAction.setIconText(QtGui.QApplication.translate("MainWindow", "Paste", 
                                                                 None, QtGui.QApplication.UnicodeUTF8))
    win.editPasteAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+V", 
                                                                 None, QtGui.QApplication.UnicodeUTF8))
    win.editDeleteAction.setText(QtGui.QApplication.translate("MainWindow", "&Delete",
                                                              None, QtGui.QApplication.UnicodeUTF8))
    win.editDeleteAction.setIconText(QtGui.QApplication.translate("MainWindow", "Delete", 
                                                                  None, QtGui.QApplication.UnicodeUTF8))
    win.editDeleteAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Delete (Del)", 
                                                                 None, QtGui.QApplication.UnicodeUTF8))
    win.editDeleteAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Del", 
                                                                  None, QtGui.QApplication.UnicodeUTF8))
       
    win.editMakeCheckpointAction.setIconText(QtGui.QApplication.translate("MainWindow", "Make Checkpoint", 
                                                                          None, QtGui.QApplication.UnicodeUTF8))
    win.editAutoCheckpointingAction.setIconText(QtGui.QApplication.translate("MainWindow", "Automatic Checkpointing", 
                                                                             None, QtGui.QApplication.UnicodeUTF8))
    win.editClearUndoStackAction.setIconText(QtGui.QApplication.translate("MainWindow", "Clear Undo Stack", 
                                                                          None, QtGui.QApplication.UnicodeUTF8))    
    win.dispObjectColorAction.setText(QtGui.QApplication.translate("MainWindow", "&Chunk Color...", 
                                                                    None, QtGui.QApplication.UnicodeUTF8))
    win.dispObjectColorAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Edit Chunk Color...", 
                                                                        None, QtGui.QApplication.UnicodeUTF8))
    win.dispObjectColorAction.setIconText(QtGui.QApplication.translate("MainWindow", "Chunk Color", 
                                                                       None, QtGui.QApplication.UnicodeUTF8))
              
