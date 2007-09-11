# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from wiki_help import QToolBar_WikiHelp

def setupUi(win):
    MainWindow = win
    
    win.buildToolsToolBar = QToolBar_WikiHelp(MainWindow)
    win.buildToolsToolBar.setEnabled(True)
    win.buildToolsToolBar.setGeometry(QtCore.QRect(458,0,89,20))
    win.buildToolsToolBar.setObjectName("buildToolsToolBar")
    
    win.buildToolsToolBar.addAction(MainWindow.toolsFuseChunksAction) 
    win.buildToolsToolBar.addAction(win.modifyDeleteBondsAction)
    
    win.buildToolsToolBar.addAction(win.modifyHydrogenateAction)
    win.buildToolsToolBar.addAction(win.modifyDehydrogenateAction)
    win.buildToolsToolBar.addAction(win.modifyPassivateAction)
    
    win.buildToolsToolBar.addAction(win.modifyStretchAction)
    win.buildToolsToolBar.addAction(win.modifySeparateAction)
    win.buildToolsToolBar.addAction(win.modifyMergeAction)
    
    win.buildToolsToolBar.addAction(win.modifyMirrorAction)
    win.buildToolsToolBar.addAction(win.modifyInvertAction)
    
    win.buildToolsToolBar.addAction(win.modifyAlignCommonAxisAction)
    #win.buildToolsToolBar.addAction(win.modifyCenterCommonAxisAction)
    
    
    ##MainWindow.addToolBar(Qt.RightToolBarArea, win.buildToolsToolBar)
    MainWindow.addToolBar(Qt.TopToolBarArea, win.buildToolsToolBar)
        
def retranslateUi(win):
    win.buildToolsToolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Build Tools", 
                                                                      None, QtGui.QApplication.UnicodeUTF8))
