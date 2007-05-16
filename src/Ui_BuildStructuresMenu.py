# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from qt4transition import *
from Utility import geticon


def setupUi(win):
    
    MainWindow = win

    ###Build Structures Menu start###
    #win.toolsDepositAtomAction = QtGui.QAction(MainWindow)
    win.toolsDepositAtomAction = QtGui.QWidgetAction(MainWindow)
    win.toolsDepositAtomAction.setCheckable(1) # make the build button checkable
    win.toolsDepositAtomAction.setIcon(geticon("ui/actions/Tools/Build Structures/Atoms"))
    
    win.toolsCookieCutAction = QtGui.QWidgetAction(MainWindow)
    win.toolsCookieCutAction.setCheckable(1) # make the cookie cutter button checkable
    win.toolsCookieCutAction.setIcon(geticon("ui/actions/Tools/Build Structures/Cookie_Cutter"))
        
    win.insertGrapheneAction = QtGui.QWidgetAction(MainWindow)
    win.insertGrapheneAction.setIcon(geticon("ui/actions/Tools/Build Structures/Graphene"))
    win.insertGrapheneAction.setObjectName("insertGrapheneAction")
    
    win.insertNanotubeAction = QtGui.QWidgetAction(MainWindow)
    win.insertNanotubeAction.setIcon(geticon("ui/actions/Tools/Build Structures/Nanotube"))
    win.insertNanotubeAction.setObjectName("insertNanotubeAction")

    win.buildDnaAction = QtGui.QWidgetAction(MainWindow)
    win.buildDnaAction.setIcon(geticon("ui/actions/Tools/Build Structures/DNA"))
    win.buildDnaAction.setObjectName("buildDnaAction")
    
    win.buildDnaOrigamiAction = QtGui.QWidgetAction(MainWindow)
    win.buildDnaOrigamiAction.setIcon(geticon(
        "ui/actions/Tools/Build Structures/DNA_Origami"))
    win.buildDnaOrigamiAction.setObjectName("buildDnaOrigamiAction")
    
       
    win.buildStructuresMenu.addAction(MainWindow.toolsDepositAtomAction)
    win.buildStructuresMenu.addAction(win.buildDnaAction)
    win.buildStructuresMenu.addAction(win.buildDnaOrigamiAction)    
    win.buildStructuresMenu.addAction(win.insertNanotubeAction)
    win.buildStructuresMenu.addAction(win.insertGrapheneAction)
    win.buildStructuresMenu.addAction(MainWindow.toolsCookieCutAction)
    
       
    ###Build Structures Menu end###
    
def retranslateUi(win):
    
     win.buildStructuresMenu.setTitle(QtGui.QApplication.translate(
         "MainWindow", 
         "Build Structures", 
         None, 
         QtGui.QApplication.UnicodeUTF8))
    
     # TOOLS > BUILD STRUCTURES MENU ITEMS
     win.toolsDepositAtomAction.setText(QtGui.QApplication.translate(
         "MainWindow", 
         "Atoms", 
         None, 
         QtGui.QApplication.UnicodeUTF8))
     win.toolsDepositAtomAction.setToolTip(QtGui.QApplication.translate(
         "MainWindow", 
         "Build Atoms", 
         None, 
         QtGui.QApplication.UnicodeUTF8))
     win.buildDnaOrigamiAction.setText(QtGui.QApplication.translate(
         "MainWindow", 
         "Origami",
         None,
         QtGui.QApplication.UnicodeUTF8))
     win.buildDnaOrigamiAction.setToolTip(QtGui.QApplication.translate(
         "MainWindow",
         "Build DNA Origami", 
         None, 
         QtGui.QApplication.UnicodeUTF8))
     
     win.toolsCookieCutAction.setText(QtGui.QApplication.translate(
         "MainWindow", 
         "Crystal",
         None, 
         QtGui.QApplication.UnicodeUTF8))
     win.toolsCookieCutAction.setToolTip(QtGui.QApplication.translate(
         "MainWindow", 
         "Build Crystal",
         None, 
         QtGui.QApplication.UnicodeUTF8))
     win.insertNanotubeAction.setIconText(QtGui.QApplication.translate(
         "MainWindow",
         "Nanotube",
         None, 
         QtGui.QApplication.UnicodeUTF8))
     win.insertNanotubeAction.setToolTip(QtGui.QApplication.translate(
         "MainWindow", 
         "Nanotube Generator", 
         None,
         QtGui.QApplication.UnicodeUTF8))
     win.insertGrapheneAction.setIconText(QtGui.QApplication.translate(
         "MainWindow", 
         "Graphene", 
         None, 
         QtGui.QApplication.UnicodeUTF8))
     win.insertGrapheneAction.setToolTip(QtGui.QApplication.translate(
         "MainWindow", 
         "Graphene Generator", 
         None, 
         QtGui.QApplication.UnicodeUTF8))
     win.buildDnaAction.setText(QtGui.QApplication.translate(
         "MainWindow", 
         "DNA", 
         None, 
         QtGui.QApplication.UnicodeUTF8))
     win.buildDnaAction.setIconText(QtGui.QApplication.translate(
         "MainWindow", 
         "DNA",
         None,
         QtGui.QApplication.UnicodeUTF8))
     win.buildDnaAction.setToolTip(QtGui.QApplication.translate(
         "MainWindow",
         "DNA Generator", 
         None, 
         QtGui.QApplication.UnicodeUTF8))