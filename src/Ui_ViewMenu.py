# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt

from Utility import geticon

#Hybrid display is an experimental work. Its action and others need to be 
#removed. For now, I am just removing it using the following flag as I have 
#unrelated modifications in other files that need to be changed in order to remove
#this option completely. I will do it after commiting those changes. For now
#this flag is good enough -- ninad 20070612

SHOW_HYBRID_DISPLAY_MENU = 0

def setupUi(win):    
    

    MainWindow = win    
        
    win.viewMenu = QtGui.QMenu(win.MenuBar)
    win.viewMenu.setObjectName("viewMenu")
  
    ###Submenus of View Menu Start###
    win.displayMenu = win.viewMenu.addMenu("Display")      
    win.Modify = win.viewMenu.addMenu("Modify")
    
    ###Submenus of View Menu End###
        
    ##### View Menu Start #####
        
    #View > Modify Menu Start
    
    win.viewOrientationAction = QtGui.QAction(MainWindow)
    win.viewOrientationAction.setCheckable(True)
    win.viewOrientationAction.setIcon(geticon("ui/actions/View/Modify/Orientation"))
    win.viewOrientationAction.setObjectName("viewOrientationAction")
    
    win.setViewFitToWindowAction = QtGui.QAction(MainWindow)
    win.setViewFitToWindowAction.setIcon(geticon("ui/actions/View/Modify/Zoom_To_Fit"))
    win.setViewFitToWindowAction.setObjectName("setViewFitToWindowAction")
    
    win.setViewZoomtoSelectionAction = QtGui.QAction(MainWindow)
    win.setViewZoomtoSelectionAction.setIcon(geticon("ui/actions/View/Modify/Zoom_To_Selection"))
    win.setViewZoomtoSelectionAction.setObjectName("setViewZoomtoSelectionAction")
    
    win.zoomToolAction = QtGui.QAction(MainWindow)
    win.zoomToolAction.setCheckable(True)
    win.zoomToolAction.setIcon(geticon("ui/actions/View/Modify/Zoom"))
    win.zoomToolAction.setObjectName("zoomToolAction")
    
    win.viewZoomAboutScreenCenterAction = QtGui.QAction(MainWindow)
    win.viewZoomAboutScreenCenterAction.setCheckable(True)
    win.viewZoomAboutScreenCenterAction.setObjectName("zoom about screen center")
    
    
    win.setViewRecenterAction = QtGui.QAction(MainWindow)
    win.setViewRecenterAction.setEnabled(True)
    win.setViewRecenterAction.setIcon(geticon("ui/actions/View/Modify/Recenter"))
    win.setViewRecenterAction.setObjectName("setViewRecenterAction")
    
    win.panToolAction = QtGui.QAction(MainWindow)
    win.panToolAction.setCheckable(True)
    win.panToolAction.setIcon(geticon("ui/actions/View/Modify/Pan"))
    win.panToolAction.setObjectName("panToolAction")

    win.rotateToolAction = QtGui.QAction(MainWindow)
    win.rotateToolAction.setCheckable(True)
    win.rotateToolAction.setIcon(geticon("ui/actions/View/Modify/Rotate"))
    win.rotateToolAction.setObjectName("rotateToolAction")
    
    win.setViewHomeAction = QtGui.QAction(MainWindow)
    win.setViewHomeAction.setIcon(geticon("ui/actions/View/Modify/Home"))
    win.setViewHomeAction.setObjectName("setViewHomeAction")
    
    win.setViewHomeToCurrentAction = QtGui.QAction(MainWindow)
    win.setViewHomeToCurrentAction.setObjectName("setViewHomeToCurrentAction")
    # View > Modify Menu End
                    
    win.viewNormalToAction = QtGui.QAction(MainWindow)
    win.viewNormalToAction.setIcon(geticon("ui/actions/View/Set_View_Normal_To"))
    #win.viewNormalToAction.setObjectName("viewNormalToAction")
    win.viewNormalToAction.setObjectName("NormalTo")

    win.viewParallelToAction = QtGui.QAction(MainWindow)
    win.viewParallelToAction.setIcon(geticon("ui/actions/View/Set_View_Parallel_To"))
    #win.viewParallelToAction.setObjectName("viewParallelToAction")
    win.viewParallelToAction.setObjectName("ParallelTo")
    
    win.saveNamedViewAction = QtGui.QAction(MainWindow)
    win.saveNamedViewAction.setIcon(geticon("ui/actions/View/Modify/Save_Named_View"))
    win.saveNamedViewAction.setObjectName("saveNamedViewAction")
    
    win.viewFrontAction = QtGui.QAction(MainWindow)
    win.viewFrontAction.setEnabled(True)
    win.viewFrontAction.setIcon(geticon("ui/actions/View/Front"))
    #win.viewFrontAction.setObjectName("viewFrontAction")
    win.viewFrontAction.setObjectName("Front")

    win.viewBackAction = QtGui.QAction(MainWindow)
    win.viewBackAction.setIcon(geticon("ui/actions/View/Back"))
    #win.viewBackAction.setObjectName("viewBackAction")
    win.viewBackAction.setObjectName("Back")
    
    win.viewRightAction = QtGui.QAction(MainWindow)
    win.viewRightAction.setIcon(geticon("ui/actions/View/Right"))
    win.viewRightAction.setObjectName("Right")

    win.viewLeftAction = QtGui.QAction(MainWindow)
    win.viewLeftAction.setIcon(geticon("ui/actions/View/Left"))
    win.viewLeftAction.setObjectName("Left")
    
    win.viewTopAction = QtGui.QAction(MainWindow)
    win.viewTopAction.setIcon(geticon("ui/actions/View/Top"))
    win.viewTopAction.setObjectName("Top")

    win.viewBottomAction = QtGui.QAction(MainWindow)
    win.viewBottomAction.setEnabled(True)
    win.viewBottomAction.setIcon(geticon("ui/actions/View/Bottom"))
    win.viewBottomAction.setObjectName("Bottom")

    win.viewIsometricAction = QtGui.QAction(MainWindow)
    win.viewIsometricAction.setIcon(geticon("ui/actions/View/Isometric"))
    win.viewIsometricAction.setObjectName("Isometric")
    
    win.viewRotate180Action = QtGui.QAction(MainWindow)
    win.viewRotate180Action.setIcon(geticon("ui/actions/View/Rotate_View_180"))
    win.viewRotate180Action.setObjectName("Rotate180")
    
    win.viewRotatePlus90Action = QtGui.QAction(MainWindow)
    win.viewRotatePlus90Action.setIcon(geticon("ui/actions/View/Rotate_View_+90"))
    win.viewRotatePlus90Action.setObjectName("RotatePlus90")

    win.viewRotateMinus90Action = QtGui.QAction(MainWindow)
    win.viewRotateMinus90Action.setIcon(geticon("ui/actions/View/Rotate_View_-90"))
    win.viewRotateMinus90Action.setObjectName("RotateMinus90")
                  
    win.viewDefviewAction = QtGui.QAction(MainWindow)
    win.viewDefviewAction.setObjectName("viewDefviewAction")
    
    
    ##### View Menu End #####
    
    ##### Display Menu Start #####
    
    win.dispDefaultAction = QtGui.QAction(MainWindow)
    win.dispDefaultAction.setIcon(geticon("ui/actions/View/Display/Default"))
    win.dispDefaultAction.setObjectName("dispDefaultAction")

    win.dispInvisAction = QtGui.QAction(MainWindow)
    win.dispInvisAction.setIcon(geticon("ui/actions/View/Display/Invisible"))
    win.dispInvisAction.setObjectName("dispInvisAction")

    win.dispLinesAction = QtGui.QAction(MainWindow)
    win.dispLinesAction.setIcon(geticon("ui/actions/View/Display/Lines"))
    win.dispLinesAction.setObjectName("dispLinesAction")

    win.dispTubesAction = QtGui.QAction(MainWindow)
    win.dispTubesAction.setEnabled(True)
    win.dispTubesAction.setIcon(geticon("ui/actions/View/Display/Tubes"))
    win.dispTubesAction.setObjectName("dispTubesAction")

    win.dispCPKAction = QtGui.QAction(MainWindow)
    win.dispCPKAction.setIcon(geticon("ui/actions/View/Display/CPK"))
    win.dispCPKAction.setObjectName("dispCPKAction")

    win.dispBallAction = QtGui.QAction(MainWindow)
    win.dispBallAction.setIcon(geticon("ui/actions/View/Display/Ball_and_Stick"))
    win.dispBallAction.setObjectName("dispBallAction")
    
    
    win.dispHybridAction = QtGui.QAction(MainWindow)
    win.dispHybridAction.setIcon(geticon("ui/actions/View/Display/Hybrid"))
    win.dispHybridAction.setCheckable(True)
    win.dispHybridAction.setObjectName("dispHybridAction")
    
    win.dispCylinderAction = QtGui.QAction(MainWindow)
    win.dispCylinderAction.setIcon(geticon("ui/actions/View/Display/Cylinder"))
    win.dispCylinderAction.setObjectName("dispCylinderAction")
    
    win.dispSurfaceAction = QtGui.QAction(MainWindow)
    win.dispSurfaceAction.setIcon(geticon("ui/actions/View/Display/Surface"))
    win.dispSurfaceAction.setObjectName("dispSurfaceAction")
    
    win.viewQuteMolAction = QtGui.QAction(MainWindow)
    win.viewQuteMolAction.setIcon(geticon("ui/actions/View/Display/QuteMol"))
    win.viewQuteMolAction.setObjectName("viewQuteMolAction")
    
    win.viewRaytraceSceneAction = QtGui.QAction(MainWindow)
    win.viewRaytraceSceneAction.setIcon(geticon("ui/actions/View/Display/Raytrace_Scene"))
    win.viewRaytraceSceneAction.setObjectName("viewRaytraceSceneAction")
    
    win.dispResetChunkColorAction = QtGui.QAction(MainWindow)
    win.dispResetChunkColorAction.setObjectName("dispResetChunkColorAction")
    
     
    win.dispSetEltable1Action = QtGui.QAction(MainWindow)
    win.dispSetEltable1Action.setObjectName("dispSetEltable1Action")

    win.dispSetEltable2Action = QtGui.QAction(MainWindow)
    win.dispSetEltable2Action.setObjectName("dispSetEltable2Action")
    
    win.dispResetAtomsDisplayAction = QtGui.QAction(MainWindow)
    win.dispResetAtomsDisplayAction.setObjectName("dispResetAtomsDisplayAction")
    
    win.dispShowInvisAtomsAction = QtGui.QAction(MainWindow)
    win.dispShowInvisAtomsAction.setObjectName("dispShowInvisAtomsAction")
    
    win.dispBGColorAction = QtGui.QAction(MainWindow)
    win.dispBGColorAction.setIcon(geticon("ui/actions/View/Display/Background_Color"))
    win.dispBGColorAction.setObjectName("dispBGColorAction")
    
    win.dispElementColorSettingsAction = QtGui.QAction(MainWindow)
    win.dispElementColorSettingsAction.setObjectName("dispElementColorSettingsAction")
    win.dispElementColorSettingsAction.setIcon(geticon("ui/actions/View/Display/Element_Color_Settings"))
    
    win.dispLightingAction = QtGui.QAction(MainWindow)
    win.dispLightingAction.setObjectName("dispLightingAction")
    
    ##### Display Menu End #####
    
    #View > Orientation Dockwidget
    #Ui_ViewOrientation.setupUi(win)
    
    win.Modify.addAction(win.viewOrientationAction)
    win.Modify.addAction(win.setViewFitToWindowAction)
    win.Modify.addAction(win.setViewZoomtoSelectionAction)
    win.Modify.addAction(win.viewZoomAboutScreenCenterAction)
    win.Modify.addAction(win.zoomToolAction)        
    win.Modify.addAction(win.setViewRecenterAction)
    
    win.Modify.addSeparator() # ----
    
    win.Modify.addAction(win.rotateToolAction)    
    win.Modify.addAction(win.panToolAction) 
    
    win.Modify.addSeparator() # ----
    
    win.Modify.addAction(win.setViewHomeAction)
    win.Modify.addAction(win.setViewHomeToCurrentAction)
    win.Modify.addAction(win.saveNamedViewAction)
        
    win.displayMenu.addAction(win.dispDefaultAction)
    win.displayMenu.addAction(win.dispInvisAction)
    win.displayMenu.addAction(win.dispLinesAction)
    win.displayMenu.addAction(win.dispTubesAction)
    win.displayMenu.addAction(win.dispBallAction)
    win.displayMenu.addAction(win.dispCPKAction)
    if SHOW_HYBRID_DISPLAY_MENU:
        win.displayMenu.addAction(win.dispHybridAction)
    
    win.displayMenu.addAction(win.dispCylinderAction)
    win.displayMenu.addAction(win.dispSurfaceAction)
    
    win.displayMenu.addSeparator() # ----
    
    win.displayMenu.addAction(MainWindow.setViewPerspecAction)
    win.displayMenu.addAction(MainWindow.setViewOrthoAction)
    
    win.displayMenu.addSeparator() # ----
    
    win.displayMenu.addAction(win.viewQuteMolAction)
    win.displayMenu.addAction(win.viewRaytraceSceneAction)
    
        
def retranslateUi(win):
        
    win.viewMenu.setTitle(QtGui.QApplication.translate("MainWindow", "&View", None, QtGui.QApplication.UnicodeUTF8))
    win.displayMenu.setTitle(QtGui.QApplication.translate("MainWindow", "&Display", None, QtGui.QApplication.UnicodeUTF8))
    win.Modify.setTitle(QtGui.QApplication.translate("MainWindow", "M&odify", None, QtGui.QApplication.UnicodeUTF8))
    
    #VIEW > MODIFY MENU ITEMS
    win.viewOrientationAction.setText(QtGui.QApplication.translate("MainWindow", "Orientation...", None, QtGui.QApplication.UnicodeUTF8))
    win.viewOrientationAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Space", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewFitToWindowAction.setText(QtGui.QApplication.translate("MainWindow", "&Zoom to Fit", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewFitToWindowAction.setIconText(QtGui.QApplication.translate("MainWindow", "Zoom to Fit", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewFitToWindowAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Zoom to Fit (Ctrl+F)", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewFitToWindowAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+F", None, QtGui.QApplication.UnicodeUTF8))
    win.zoomToolAction.setText(QtGui.QApplication.translate("MainWindow", "&Zoom Tool", None, QtGui.QApplication.UnicodeUTF8))
    win.zoomToolAction.setIconText(QtGui.QApplication.translate("MainWindow", "Zoom Tool", None, QtGui.QApplication.UnicodeUTF8))
    
    win.viewZoomAboutScreenCenterAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Zoom About Screen Center", 
        None, QtGui.QApplication.UnicodeUTF8))
    
    win.setViewZoomtoSelectionAction.setText(QtGui.QApplication.translate("MainWindow", "Zoom To Selection", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewZoomtoSelectionAction.setIconText(QtGui.QApplication.translate("MainWindow", "Zoom To Selection", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewZoomtoSelectionAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Zoom to Selection", None, QtGui.QApplication.UnicodeUTF8))
    
    win.panToolAction.setText(QtGui.QApplication.translate("MainWindow", "&Pan", None, QtGui.QApplication.UnicodeUTF8))
    win.panToolAction.setIconText(QtGui.QApplication.translate("MainWindow", "Pan ", None, QtGui.QApplication.UnicodeUTF8))
    win.rotateToolAction.setText(QtGui.QApplication.translate("MainWindow", "Rotate", None, QtGui.QApplication.UnicodeUTF8))
    win.rotateToolAction.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeAction.setText(QtGui.QApplication.translate("MainWindow", "&Home", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeAction.setIconText(QtGui.QApplication.translate("MainWindow", "Home", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Home View (Home)", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Home", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewRecenterAction.setText(QtGui.QApplication.translate("MainWindow", "&Recenter", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewRecenterAction.setIconText(QtGui.QApplication.translate("MainWindow", "Recenter", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewRecenterAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Recenter (Ctrl+R)", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewRecenterAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+R", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeToCurrentAction.setText(QtGui.QApplication.translate("MainWindow", "Set Home View to &Current View", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeToCurrentAction.setIconText(QtGui.QApplication.translate("MainWindow", "Set Home View to Current View", None, QtGui.QApplication.UnicodeUTF8))
    win.saveNamedViewAction.setText(QtGui.QApplication.translate("MainWindow", "Save Named View", None, QtGui.QApplication.UnicodeUTF8))
    win.saveNamedViewAction.setIconText(QtGui.QApplication.translate("MainWindow", "Save Named View", None, QtGui.QApplication.UnicodeUTF8))
        
    #VIEW > DISPLAY MENU ITEMS
    win.dispBallAction.setText(QtGui.QApplication.translate("MainWindow", "Ball and Stick", None, QtGui.QApplication.UnicodeUTF8))
    win.dispBallAction.setIconText(QtGui.QApplication.translate("MainWindow", "Ball and Stick", None, QtGui.QApplication.UnicodeUTF8))
    win.dispDefaultAction.setText(QtGui.QApplication.translate("MainWindow", "Default", None, QtGui.QApplication.UnicodeUTF8))
    win.dispDefaultAction.setIconText(QtGui.QApplication.translate("MainWindow", "Default", None, QtGui.QApplication.UnicodeUTF8))
    
    win.dispInvisAction.setText(QtGui.QApplication.translate("MainWindow", "Invisible", None, QtGui.QApplication.UnicodeUTF8))
    win.dispInvisAction.setIconText(QtGui.QApplication.translate("MainWindow", "Invisible", None, QtGui.QApplication.UnicodeUTF8))
    win.dispLinesAction.setText(QtGui.QApplication.translate("MainWindow", "Lines", None, QtGui.QApplication.UnicodeUTF8))
    win.dispLinesAction.setIconText(QtGui.QApplication.translate("MainWindow", "Lines", None, QtGui.QApplication.UnicodeUTF8))
    win.dispTubesAction.setText(QtGui.QApplication.translate("MainWindow", "Tubes", None, QtGui.QApplication.UnicodeUTF8))
    win.dispTubesAction.setIconText(QtGui.QApplication.translate("MainWindow", "Tubes", None, QtGui.QApplication.UnicodeUTF8))
    win.dispCPKAction.setText(QtGui.QApplication.translate("MainWindow", "CPK", None, QtGui.QApplication.UnicodeUTF8))
    win.dispCPKAction.setIconText(QtGui.QApplication.translate("MainWindow", "CPK", None, QtGui.QApplication.UnicodeUTF8))
    win.dispHybridAction.setText(QtGui.QApplication.translate("MainWindow", "Hybrid Display", None, QtGui.QApplication.UnicodeUTF8))
    win.dispHybridAction.setIconText(QtGui.QApplication.translate("MainWindow", "Hybrid", None, QtGui.QApplication.UnicodeUTF8))
    win.dispSurfaceAction.setIconText(QtGui.QApplication.translate("MainWindow", "Surface", None, QtGui.QApplication.UnicodeUTF8))
    win.dispCylinderAction.setIconText(QtGui.QApplication.translate("MainWindow", "Cylinder", None, QtGui.QApplication.UnicodeUTF8))
    
    #FOLLOWING VIEW MENU ITEMS NEED SORTING
    win.viewFrontAction.setText(QtGui.QApplication.translate("MainWindow", "&Front", None, QtGui.QApplication.UnicodeUTF8))
    win.viewFrontAction.setIconText(QtGui.QApplication.translate("MainWindow", "Front", None, QtGui.QApplication.UnicodeUTF8))
    win.viewFrontAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Front View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBackAction.setText(QtGui.QApplication.translate("MainWindow", "&Back", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBackAction.setIconText(QtGui.QApplication.translate("MainWindow", "Back", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBackAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Back View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewTopAction.setText(QtGui.QApplication.translate("MainWindow", "&Top", None, QtGui.QApplication.UnicodeUTF8))
    win.viewTopAction.setIconText(QtGui.QApplication.translate("MainWindow", "Top", None, QtGui.QApplication.UnicodeUTF8))
    win.viewTopAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Top View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBottomAction.setText(QtGui.QApplication.translate("MainWindow", "Botto&m", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBottomAction.setIconText(QtGui.QApplication.translate("MainWindow", "Bottom", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBottomAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Bottom View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRightAction.setText(QtGui.QApplication.translate("MainWindow", "&Right", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRightAction.setIconText(QtGui.QApplication.translate("MainWindow", "Right", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRightAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Right View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRightAction.setStatusTip(QtGui.QApplication.translate("MainWindow", "Right View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewLeftAction.setText(QtGui.QApplication.translate("MainWindow", "&Left", None, QtGui.QApplication.UnicodeUTF8))
    win.viewLeftAction.setIconText(QtGui.QApplication.translate("MainWindow", "Left", None, QtGui.QApplication.UnicodeUTF8))
    win.viewLeftAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Left View", None, QtGui.QApplication.UnicodeUTF8))
    
    win.viewRotate180Action.setText(QtGui.QApplication.translate("MainWindow", "Rotate View 180", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRotate180Action.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate View 180", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRotate180Action.setToolTip(QtGui.QApplication.translate("MainWindow", "Rotate View 180", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRotate180Action.setStatusTip(QtGui.QApplication.translate("MainWindow", "Rotate View 180", None, QtGui.QApplication.UnicodeUTF8))
    win.viewIsometricAction.setText(QtGui.QApplication.translate("MainWindow", "&Isometric", None, QtGui.QApplication.UnicodeUTF8))
    win.viewIsometricAction.setIconText(QtGui.QApplication.translate("MainWindow", "Isometric", None, QtGui.QApplication.UnicodeUTF8))
    win.dispResetChunkColorAction.setText(QtGui.QApplication.translate("MainWindow", "&Reset Chunk Color", None, QtGui.QApplication.UnicodeUTF8))
    win.dispResetChunkColorAction.setIconText(QtGui.QApplication.translate("MainWindow", "Reset Chunk Color", None, QtGui.QApplication.UnicodeUTF8))
    
