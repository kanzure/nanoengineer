# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from wiki_help import QToolBar_WikiHelp
from icon_utilities import geticon

def setupUi(win):
    """
    Creates and populates the "Standard" toolbar.
    """
    MainWindow = win

    # Create the "Standard" toolbar.
    win.standardToolBar = QToolBar_WikiHelp(MainWindow)
    win.standardToolBar.setEnabled(True)
    win.standardToolBar.setObjectName("standardToolBar") 
    MainWindow.addToolBar(Qt.TopToolBarArea , win.standardToolBar)
    
    # Action items from the File Menu
    win.standardToolBar.addAction(win.fileOpenAction)
    win.standardToolBar.addAction(win.fileSaveAction)
    win.standardToolBar.addSeparator()
    
    # Action items from the Edit Menu
    win.standardToolBar.addAction(win.editMakeCheckpointAction)
    win.standardToolBar.addAction(win.editUndoAction)
    win.standardToolBar.addAction(win.editRedoAction)
    win.standardToolBar.addAction(win.editCutAction)
    win.standardToolBar.addAction(win.editCopyAction)
    win.standardToolBar.addAction(win.pasteFromClipboardAction)
    win.standardToolBar.addAction(win.editDeleteAction)
    win.standardToolBar.addSeparator()
    
    # Action items from the Tools menu  @@@ninad061110
    # Not decided whether select chunks and move chunks options
    # will be a part of Tools Menu
    
    win.toolsSelectMoleculesAction = QtGui.QAction(MainWindow)
    win.toolsSelectMoleculesAction.setCheckable(1) # make the select chunks button checkable
    win.toolsSelectMoleculesAction.setIcon(geticon("ui/actions/Toolbars/Standard/Select_Chunks"))
    
    # Define an action grop for move molecules (translate and rotate components)
    # actions ...to make them mutually exclusive. 
    # -- ninad 070309
    win.toolsMoveRotateActionGroup = QtGui.QActionGroup(MainWindow)
    win.toolsMoveRotateActionGroup.setExclusive(True)
    
    win.toolsMoveMoleculeAction = QtGui.QWidgetAction(win.toolsMoveRotateActionGroup)
    win.toolsMoveMoleculeAction.setCheckable(1) # make the Move mode button checkable
    win.toolsMoveMoleculeAction.setIcon(geticon("ui/actions/Toolbars/Standard/Move_Chunks"))
       
    win.rotateComponentsAction = QtGui.QWidgetAction(win.toolsMoveRotateActionGroup)
    win.rotateComponentsAction.setCheckable(1) # make the Move mode button checkable
    win.rotateComponentsAction.setIcon(geticon("ui/actions/Toolbars/Standard/Rotate_Components"))
    
    win.standardToolBar.addAction(MainWindow.toolsSelectMoleculesAction)
    win.standardToolBar.addAction(MainWindow.toolsMoveMoleculeAction)
    win.standardToolBar.addAction(MainWindow.rotateComponentsAction)
        
    # Action items from the Tools Menu 
    win.standardToolBar.addAction(win.modifyAdjustSelAction)
    win.standardToolBar.addAction(win.modifyAdjustAllAction)
        
    # Action items from the Simulation Menu
    win.standardToolBar.addAction(win.simMinimizeEnergyAction)
    win.standardToolBar.addSeparator()
    
    # Action items from the Edit Menu or View Menu 
    # (not decided yet where to put it in the menu)
    win.standardToolBar.addAction(win.dispObjectColorAction)
        
    # Action items from the Tools menu
    win.standardToolBar.addAction(win.editPrefsAction)
    win.editPrefsAction.setIcon(geticon("ui/actions/Tools/Options"))
    win.standardToolBar.addSeparator()  
    
    # Action items from the Help Menu 
    win.standardToolBar.addAction(win.helpWhatsThisAction)
    
    
def retranslateUi(win):
    """
    Assigns the I{window title} property of the "Standard" toolbar and other
    widgets.
    
    The window title of the "Standard" toolbar will be displayed in the popup 
    menu under "View > Toolbars".
    """
    win.standardToolBar.setWindowTitle(
        QtGui.QApplication.translate("MainWindow", "Standard", 
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.toolsSelectMoleculesAction.setText(
        QtGui.QApplication.translate("MainWindow", "Select Chunks",
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.toolsSelectMoleculesAction.setToolTip(
        QtGui.QApplication.translate("MainWindow", "Select Chunks", 
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.toolsMoveMoleculeAction.setText(
        QtGui.QApplication.translate("MainWindow", "Translate",
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.toolsMoveMoleculeAction.setToolTip(
        QtGui.QApplication.translate("MainWindow", "Translate",
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.rotateComponentsAction.setText(
        QtGui.QApplication.translate("MainWindow", "Rotate",
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.rotateComponentsAction.setToolTip(
        QtGui.QApplication.translate("MainWindow", "Rotate",
                                    None, QtGui.QApplication.UnicodeUTF8))
