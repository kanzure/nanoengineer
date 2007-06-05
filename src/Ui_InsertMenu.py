# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from qt4transition import *
from Utility import geticon
from debug_prefs import debug_pref, Choice_boolean_False


def setupUi(win):
    
    MainWindow = win
      
    win.Insert = QtGui.QMenu(win.MenuBar)
    win.Insert.setObjectName("Insert")
    
    win.jigsAtomSetAction = QtGui.QWidgetAction(MainWindow)
    win.jigsAtomSetAction.setIcon(geticon("ui/actions/Tools/Atom_Set"))
    win.jigsAtomSetAction.setObjectName("jigsAtomSetAction")
    
    win.fileInsertAction = QtGui.QAction(MainWindow)
    win.fileInsertAction.setObjectName("fileInsertAction")
    
    win.insertCommentAction = QtGui.QAction(MainWindow)
    win.insertCommentAction.setIcon(geticon("ui/actions/Insert/Comment"))
    win.insertCommentAction.setObjectName("insertCommentAction")
    
    win.insertPovraySceneAction = QtGui.QAction(MainWindow)
    win.insertPovraySceneAction.setIcon(geticon("ui/actions/Insert/POV-Ray_Scene"))
    win.insertPovraySceneAction.setObjectName("insertPovraySceneAction")
    
    
    win.jigsGridPlaneAction = QtGui.QAction(MainWindow)
    win.jigsGridPlaneAction.setIcon(geticon("ui/actions/Insert/Reference Geometry/Grid_Plane"))
    win.jigsGridPlaneAction.setObjectName("jigsGridPlaneAction")
    
    win.referencePlaneAction = QtGui.QAction(MainWindow)
    win.referencePlaneAction.setIcon(geticon(
        "ui/actions/Insert/Reference Geometry/Plane"))
    win.referencePlaneAction.setObjectName("referencePlaneAction")
    
        
    win.referenceGeometryMenu = win.Insert.addMenu("Reference Geometry")
    
    #Add Actions
    ##if debug_pref("Show new Insert > Reference Plane option", 
                      ##Choice_boolean_False,
                      ##prefs_key=True):
    win.referenceGeometryMenu.addAction(win.referencePlaneAction)        
    win.referenceGeometryMenu.addAction(win.jigsGridPlaneAction)
    win.Insert.addAction(win.jigsAtomSetAction)
    win.Insert.addSeparator()
    win.Insert.addAction(win.fileInsertAction)
    win.Insert.addSeparator()    
    win.Insert.addAction(win.insertCommentAction)
    win.Insert.addSeparator()
    win.Insert.addAction(win.insertPovraySceneAction) 
    
    
def retranslateUi(win):
    
    win.Insert.setTitle(QtGui.QApplication.translate(
        "MainWindow", "&Insert", 
        None, QtGui.QApplication.UnicodeUTF8))
    
    win.jigsAtomSetAction.setIconText(QtGui.QApplication.translate(
        "MainWindow",  "Atom Set",  None, QtGui.QApplication.UnicodeUTF8))
        
    win.fileInsertAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Part...", 
        None, QtGui.QApplication.UnicodeUTF8))
    
    win.fileInsertAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Insert Part...", 
        None, QtGui.QApplication.UnicodeUTF8))
    
    win.fileInsertAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Insert Part", 
        None, QtGui.QApplication.UnicodeUTF8))
    
    win.insertCommentAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Comment", 
        None,  QtGui.QApplication.UnicodeUTF8))
    
    win.insertPovraySceneAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "POV-Ray Scene", 
        None, QtGui.QApplication.UnicodeUTF8))
    
    win.insertPovraySceneAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Insert POV-Ray Scene file", 
        None, QtGui.QApplication.UnicodeUTF8))
    
    win.jigsGridPlaneAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Grid Plane...", 
        None, QtGui.QApplication.UnicodeUTF8))
    
    win.referencePlaneAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Plane...", 
        None, QtGui.QApplication.UnicodeUTF8))
               