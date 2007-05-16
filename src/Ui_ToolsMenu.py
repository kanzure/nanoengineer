# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from qt4transition import *

import Ui_BuildStructuresMenu
import Ui_BuildToolsMenu
import Ui_SelectMenu
import Ui_DimensionsMenu
from Utility import geticon


def setupUi(win):
    
    MainWindow = win
    
    win.toolsMenu = QtGui.QMenu(win.MenuBar)
    win.toolsMenu.setObjectName("Tools")
    
    
    ####Tools Menu Start####
    win.editPrefsAction = QtGui.QWidgetAction(MainWindow)
    win.editPrefsAction.setIcon(geticon("ui/actions/Tools/Options"))
    win.editPrefsAction.setObjectName("editPrefsAction")    
    
    win.modifyAdjustSelAction = QtGui.QWidgetAction(MainWindow)
    win.modifyAdjustSelAction.setEnabled(True)
    win.modifyAdjustSelAction.setIcon(geticon("ui/actions/Tools/Adjust_Selection"))
    win.modifyAdjustSelAction.setObjectName("modifyAdjustSelAction")

    win.modifyAdjustAllAction = QtGui.QWidgetAction(MainWindow)
    win.modifyAdjustAllAction.setIcon(geticon("ui/actions/Tools/Adjust_All"))
    win.modifyAdjustAllAction.setObjectName("modifyAdjustAllAction")
    
    win.simMinimizeEnergyAction = QtGui.QWidgetAction(MainWindow)
    win.simMinimizeEnergyAction.setIcon(geticon("ui/actions/Simulation/Minimize_Energy"))
    win.simMinimizeEnergyAction.setObjectName("simMinimizeEnergyAction")
        
    win.toolsExtrudeAction = QtGui.QWidgetAction(MainWindow)
    win.toolsExtrudeAction.setCheckable(True)
    win.toolsExtrudeAction.setIcon(geticon("ui/actions/Insert/Features/Extrude"))
    
    win.toolsFuseChunksAction = QtGui.QWidgetAction(MainWindow)
    win.toolsFuseChunksAction.setCheckable(1) # make the Fuse Mode button checkable
    win.toolsFuseChunksAction.setIcon(geticon("ui/actions/Tools/Build Tools/Fuse_Chunks"))
       
    win.modifyMirrorAction = QtGui.QWidgetAction(MainWindow)
    win.modifyMirrorAction.setIcon(geticon("ui/actions/Tools/Build Tools/Mirror"))
    win.modifyMirrorAction.setObjectName("modifyMirrorAction")
    
    win.modifyInvertAction = QtGui.QWidgetAction(MainWindow)
    win.modifyInvertAction.setIcon(geticon("ui/actions/Tools/Build Tools/Invert"))
    win.modifyInvertAction.setObjectName("modifyInvertAction")
    
    win.modifyStretchAction = QtGui.QWidgetAction(MainWindow)
    win.modifyStretchAction.setIcon(geticon("ui/actions/Tools/Build Tools/Stretch"))
    win.modifyStretchAction.setObjectName("modifyStretchAction")
    
    #Add Menu items to the Tools menu
    win.toolsMenu.addAction(win.modifyAdjustSelAction)
    win.toolsMenu.addAction(win.modifyAdjustAllAction)
    win.toolsMenu.addAction(win.simMinimizeEnergyAction)
    win.toolsMenu.addSeparator()
    
    #Tools Sub Menus
    win.buildStructuresMenu = win.toolsMenu.addMenu("Build Structures")
    win.buildToolsMenu = win.toolsMenu.addMenu("Build Tools")
    
    win.toolsMenu.addSeparator()
    #Tools Menu items again 
    win.toolsMenu.addAction(win.toolsExtrudeAction)
    win.toolsMenu.addAction(win.toolsFuseChunksAction)
    win.toolsMenu.addSeparator()
    win.toolsMenu.addAction(win.modifyMirrorAction)
    win.toolsMenu.addAction(win.modifyInvertAction)
    win.toolsMenu.addAction(win.modifyStretchAction)    
    win.toolsMenu.addSeparator()
    win.dimensionsMenu = win.toolsMenu.addMenu("Dimensions")
    win.Select = win.toolsMenu.addMenu("Select")
    
    win.toolsMenu.addSeparator()
    
    #Tools > Preferences Menu Item
    win.toolsMenu.addAction(win.editPrefsAction)
        
    ####Tools Menu End####
    
    #TOOLS > SUB-MENUS
    Ui_BuildStructuresMenu.setupUi(win)
    Ui_BuildToolsMenu.setupUi(win)
    Ui_SelectMenu.setupUi(win)
    Ui_DimensionsMenu.setupUi(win)    
        
    
def retranslateUi(win):
        
    win.toolsMenu.setTitle(QtGui.QApplication.translate(
        "MainWindow", 
        "&Tools",
        None, 
        QtGui.QApplication.UnicodeUTF8))
        
    # TOOLS  > SUB-MENUS
    Ui_BuildStructuresMenu.retranslateUi(win)
    Ui_BuildToolsMenu.retranslateUi(win)
    Ui_SelectMenu.retranslateUi(win)
    Ui_DimensionsMenu.retranslateUi(win)
        
    #TOOLS > MENU ITEMS
    win.modifyAdjustSelAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Adjust Selection",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.modifyAdjustSelAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Adjust Selection",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.modifyAdjustSelAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Adjust Selection",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.modifyAdjustAllAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Adjust All",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.modifyAdjustAllAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Adjust All", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.simMinimizeEnergyAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Minimize Energy", 
        None, 
        QtGui.QApplication.UnicodeUTF8))    
    
    win.toolsExtrudeAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Extrude",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.toolsFuseChunksAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Fuse Chunks",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.toolsFuseChunksAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Fuse Chunks", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.toolsExtrudeAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Extrude", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
        
    win.editPrefsAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Preferences...", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.modifyMirrorAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Mirror", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.modifyMirrorAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Mirror Chunks",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.modifyInvertAction.setText(QtGui.QApplication.translate(
        "MainWindow", "&Invert", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.modifyInvertAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Invert",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.editPrefsAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Preferences...", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    win.editPrefsAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Preferences", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    
    