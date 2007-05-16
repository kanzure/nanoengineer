# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from qt4transition import *
from wiki_help import QToolBar_WikiHelp
from Utility import geticon

def setupUi(win):
            
            MainWindow = win
            
            win.viewToolBar = QToolBar_WikiHelp(MainWindow)
            win.viewToolBar.setEnabled(True)
            win.viewToolBar.setObjectName("viewToolBar")
            MainWindow.addToolBar(Qt.TopToolBarArea, win.viewToolBar)       
            
                        
            win.viewToolBar.addAction(win.setViewHomeAction)
            win.viewToolBar.addAction(win.setViewFitToWindowAction)
            win.viewToolBar.addAction(win.setViewRecenterAction)
            win.viewToolBar.addAction(win.setViewZoomtoSelectionAction)
            win.viewToolBar.addAction(win.zoomToolAction)
            win.viewToolBar.addAction(win.panToolAction)
            win.viewToolBar.addAction(win.rotateToolAction)
            
            win.viewToolBar.addSeparator()
            
            #Create Standard Views dropdown menu in the View Tool bar ---
            
            #win.standardViewsAction = QtGui.QAction(MainWindow)
            win.standardViewsAction = QtGui.QWidgetAction(MainWindow)
            win.standardViewsAction.setEnabled(True)
            win.standardViewsAction.setIcon(geticon("ui/actions/View/Standard_Views"))
            win.standardViewsAction.setObjectName("standardViews")
            
            win.standardViewsMenu = QtGui.QMenu("Standard Views")
            
            win.standardViewsMenu .addAction(win.viewFrontAction)
            win.standardViewsMenu .addAction(win.viewBackAction)
            win.standardViewsMenu .addAction(win.viewLeftAction)
            win.standardViewsMenu .addAction(win.viewRightAction)
            win.standardViewsMenu .addAction(win.viewTopAction)
            win.standardViewsMenu .addAction(win.viewBottomAction)
            win.standardViewsMenu .addAction(win.viewIsometricAction)
                                   
            win.standardViews_btn = QtGui.QToolButton()
            win.standardViews_btn.setMenu(win.standardViewsMenu)
            win.standardViews_btn.setPopupMode(QToolButton.MenuButtonPopup)
            win.standardViews_btn.setIcon(geticon("ui/actions/View/Standard_Views"))
            win.standardViewsAction.setDefaultWidget(win.standardViews_btn)
            
            win.standardViewsAction.setMenu(win.standardViewsMenu)
                        
            win.viewToolBar.addAction(win.standardViewsAction)
                        
            win.viewToolBar .addAction(win.viewRotate180Action)
            win.viewToolBar .addAction(win.viewRotatePlus90Action)
            win.viewToolBar.addAction(win.viewRotateMinus90Action)
            
            win.viewToolBar.addSeparator()
            win.viewToolBar.addAction(win.viewOrientationAction)
            win.viewToolBar.addAction(win.saveNamedViewAction)
            win.viewToolBar.addAction(win.viewNormalToAction)
            win.viewToolBar.addAction(win.viewParallelToAction)
            
            win.viewToolBar.addSeparator()
                      
            win.viewToolBar.addAction(win.dispDefaultAction)
            win.viewToolBar.addAction(win.dispInvisAction)
            win.viewToolBar.addAction(win.dispLinesAction)
            win.viewToolBar.addAction(win.dispTubesAction)
            win.viewToolBar.addAction(win.dispBallAction)
            win.viewToolBar.addAction(win.dispCPKAction)
            win.viewToolBar.addAction(win.dispCylinderAction)
            win.viewToolBar.addAction(win.dispSurfaceAction)
            win.viewToolBar.addAction(win.viewRaytraceSceneAction) 
            

def retranslateUi(win):
            win.viewToolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "View", None, QtGui.QApplication.UnicodeUTF8))
