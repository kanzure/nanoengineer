# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import QToolButton

from wiki_help import QToolBar_WikiHelp
from icon_utilities import geticon

def setupUi(win):

    MainWindow = win

    # View toolbar: Create and populate 
    
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

    # Create Standard Views dropdown menu in the View Tool bar ---

    win.standardViewsMenu = QtGui.QMenu("Standard Views")

    win.standardViewsMenu.addAction(win.viewFrontAction)
    win.standardViewsMenu.addAction(win.viewBackAction)
    win.standardViewsMenu.addAction(win.viewLeftAction)
    win.standardViewsMenu.addAction(win.viewRightAction)
    win.standardViewsMenu.addAction(win.viewTopAction)
    win.standardViewsMenu.addAction(win.viewBottomAction)
    win.standardViewsMenu.addAction(win.viewIsometricAction)

    win.standardViewsAction = QtGui.QWidgetAction(MainWindow)
    win.standardViewsAction.setEnabled(True)
    win.standardViewsAction.setIcon(geticon("ui/actions/View/Standard_Views"))
    win.standardViewsAction.setObjectName("standardViews")
    win.standardViewsAction.setText("Standard Views")
    win.standardViewsAction.setMenu(win.standardViewsMenu)

    win.standardViews_btn = QtGui.QToolButton()            
    win.standardViews_btn.setPopupMode(QToolButton.MenuButtonPopup)
    win.standardViewsAction.setDefaultWidget(win.standardViews_btn)
    win.standardViews_btn.setDefaultAction(win.standardViewsAction)

    win.viewToolBar.addAction(win.standardViewsAction)

    win.viewToolBar.addAction(win.viewRotate180Action)
    win.viewToolBar.addAction(win.viewRotatePlus90Action)
    win.viewToolBar.addAction(win.viewRotateMinus90Action)

    win.viewToolBar.addSeparator() # ----

    win.viewToolBar.addAction(win.viewOrientationAction)
    win.viewToolBar.addAction(win.saveNamedViewAction)
    win.viewToolBar.addAction(win.viewNormalToAction)
    win.viewToolBar.addAction(win.viewParallelToAction)
    
    win.viewToolBar.addSeparator() # ----

    win.viewToolBar.addAction(win.viewQuteMolAction)
    win.viewToolBar.addAction(win.viewRaytraceSceneAction) 
    
    # Standard Views toolbar: Create and populate 
    
    # Having all the standard views available on their own toolbar is nice
    # if the screen is wide enough. Mark 2007-12-02
    win.standardViewsToolBar = QToolBar_WikiHelp(MainWindow)
    win.standardViewsToolBar.setEnabled(True)
    win.standardViewsToolBar.setObjectName("standardViewsToolBar")
    MainWindow.addToolBar(Qt.TopToolBarArea, win.standardViewsToolBar)  
    
    win.standardViewsToolBar.addAction(win.viewFrontAction)
    win.standardViewsToolBar.addAction(win.viewBackAction)
    win.standardViewsToolBar.addAction(win.viewLeftAction)
    win.standardViewsToolBar.addAction(win.viewRightAction)
    win.standardViewsToolBar.addAction(win.viewTopAction)
    win.standardViewsToolBar.addAction(win.viewBottomAction)
    win.standardViewsToolBar.addAction(win.viewIsometricAction)
    
    # Display Style toolbar: Create and populate 
    
    win.displayStylesToolBar = QToolBar_WikiHelp(MainWindow)
    win.displayStylesToolBar.setEnabled(True)
    win.displayStylesToolBar.setObjectName("displayStylesToolBar")
    MainWindow.addToolBar(Qt.TopToolBarArea, win.displayStylesToolBar)    

    win.displayStylesToolBar.addAction(win.dispDefaultAction)
    win.displayStylesToolBar.addAction(win.dispInvisAction)
    win.displayStylesToolBar.addAction(win.dispLinesAction)
    win.displayStylesToolBar.addAction(win.dispTubesAction)
    win.displayStylesToolBar.addAction(win.dispBallAction)
    win.displayStylesToolBar.addAction(win.dispCPKAction)
    win.displayStylesToolBar.addAction(win.dispCylinderAction)
    win.displayStylesToolBar.addAction(win.dispSurfaceAction)

def retranslateUi(win):
    win.viewToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "View", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.standardViewsToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Standard Views", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.displayStylesToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Display Styles", 
            None, QtGui.QApplication.UnicodeUTF8))
