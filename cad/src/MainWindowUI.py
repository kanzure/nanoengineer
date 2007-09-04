# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

# -*- coding: utf-8 -*-



from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt

import Ui_FileMenu
import Ui_EditMenu
import Ui_ViewMenu
import Ui_InsertMenu
import Ui_ToolsMenu
import Ui_SimulationMenu
import Ui_HelpMenu

import Ui_StandardToolBar
import Ui_ViewToolBar
import Ui_SelectToolBar
import Ui_SimulationToolBar
import Ui_BuildToolsToolBar
import Ui_BuildStructuresToolBar
from Utility import geticon

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        #MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,1014,688).size()).expandedTo(MainWindow.minimumSizeHint()))

        from debug_prefs import debug_pref, Choice_boolean_False
        if debug_pref("Multipane GUI", Choice_boolean_False):
            self.widget = self.centralWidget()
        else:
            self.widget = QtGui.QWidget(MainWindow)
            self.widget.setGeometry(QtCore.QRect(0,95,1014,593))
            self.widget.setObjectName("widget")
            MainWindow.setCentralWidget(self.widget)
                
     
        
        ###########################
               #### DASHBOARDS  ####
        ###########################
        

        self.cookieCutterDashboard = QtGui.QToolBar(MainWindow)
        self.cookieCutterDashboard.setEnabled(True)
        #self.cookieCutterDashboard.setGeometry(QtCore.QRect(667,0,94,20))
        self.cookieCutterDashboard.setObjectName("cookieCutterDashboard")

        self.ccLabel = QtGui.QLabel(self.cookieCutterDashboard)
        self.ccLabel.setObjectName("ccLabel")
        #MainWindow.addDockWidget(self.cookieCutterDashboard)

        self.moveChunksDashboard = QtGui.QToolBar(MainWindow)
        
        self.moveChunksDashboard.setEnabled(True)
        self.moveChunksDashboard.setObjectName("moveChunksDashboard")

        self.textLabel1 = QtGui.QLabel(self.moveChunksDashboard)
        self.textLabel1.setObjectName("textLabel1")

        self.moviePlayerDashboard = QtGui.QToolBar(MainWindow)
        self.moviePlayerDashboard.setEnabled(True)
        self.moviePlayerDashboard.setGeometry(QtCore.QRect(0,20,864,27))
        self.moviePlayerDashboard.setObjectName("moviePlayerDashboard")
        
        self.selectMolDashboard = QtGui.QToolBar(MainWindow)
        
        self.selectMolDashboard.setEnabled(True)
        self.selectMolDashboard.setObjectName("selectMolDashboard")

        self.textLabel1_2 = QtGui.QLabel(self.selectMolDashboard)
        self.textLabel1_2.setObjectName("textLabel1_2")

        self.zoomDashboard = QtGui.QToolBar(MainWindow)
        self.zoomDashboard.setEnabled(True)
        self.zoomDashboard.setGeometry(QtCore.QRect(0,47,91,20))
        self.zoomDashboard.setObjectName("zoomDashboard")

        self.zoomTextLabel = QtGui.QLabel(self.zoomDashboard)
        self.zoomTextLabel.setObjectName("zoomTextLabel")
        MainWindow.addToolBar(Qt.BottomToolBarArea, self.zoomDashboard)

        self.panDashboard = QtGui.QToolBar(MainWindow)
        self.panDashboard.setEnabled(True)
        self.panDashboard.setGeometry(QtCore.QRect(91,47,79,20))
        self.panDashboard.setObjectName("panDashboard")

        self.panTextLabel = QtGui.QLabel(self.panDashboard)
        self.panTextLabel.setObjectName("panTextLabel")
        MainWindow.addToolBar(Qt.BottomToolBarArea,  self.panDashboard)

        self.rotateDashboard = QtGui.QToolBar(MainWindow)
        self.rotateDashboard.setEnabled(True)
        self.rotateDashboard.setGeometry(QtCore.QRect(170,47,94,20))
        self.rotateDashboard.setObjectName("rotateDashboard")

        self.rotateTextLabel = QtGui.QLabel(self.rotateDashboard)
        self.rotateTextLabel.setObjectName("rotateTextLabel")
        MainWindow.addToolBar(Qt.BottomToolBarArea,  self.rotateDashboard)

        self.fuseChunksDashboard = QtGui.QToolBar(MainWindow)
        self.fuseChunksDashboard.setEnabled(True)
        self.fuseChunksDashboard.setObjectName("fuseChunksDashboard")

        self.textLabel1_3 = QtGui.QLabel(self.fuseChunksDashboard)
        self.textLabel1_3.setObjectName("textLabel1_3")

        self.dashboardHolder = QtGui.QDockWidget(MainWindow)
        self.dashboardHolder.setObjectName('dashboardholder')
        self.dashboardHolder.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dashboardHolder)
       

        self.cookieSelectDashboard = QtGui.QToolBar(MainWindow)
        self.cookieSelectDashboard.setEnabled(True)
        self.cookieSelectDashboard.setGeometry(QtCore.QRect(373,47,109,20))
        self.cookieSelectDashboard.setObjectName("cookieSelectDashboard")
        MainWindow.addToolBar(Qt.BottomToolBarArea, self.cookieSelectDashboard)
        
        
        

        self.MenuBar = QtGui.QMenuBar(MainWindow)
        self.MenuBar.setEnabled(True)
        self.MenuBar.setGeometry(QtCore.QRect(0,0,1014,28))
        self.MenuBar.setObjectName("MenuBar")
        
        ###########################
               #### MAIN MENUS  ####
        ###########################
        
        Ui_FileMenu.setupUi(self)
        Ui_EditMenu.setupUi(self)
        Ui_ViewMenu.setupUi(self)
        Ui_InsertMenu.setupUi(self)
        Ui_ToolsMenu.setupUi(self)
        Ui_SimulationMenu.setupUi(self)
        Ui_HelpMenu.setupUi(self)
        
        #########################
        ######TOOLBARS#########
        #########################
        
        Ui_StandardToolBar.setupUi(self)       
        Ui_ViewToolBar.setupUi(self)       
        
        Ui_BuildToolsToolBar.setupUi(self)
        Ui_BuildStructuresToolBar.setupUi(self)
        Ui_SelectToolBar.setupUi(self)
        Ui_SimulationToolBar.setupUi(self)
                    
        self.animatorMenu = QtGui.QMenu(self.MenuBar)
        self.animatorMenu.setObjectName("Animator")
        
        self.windowMenu = QtGui.QMenu(self.MenuBar)
        self.windowMenu.setObjectName("Window")   

        
              
        ###Following will become outdated for Alpha9 Start#####

        self.Modes = QtGui.QMenu(self.MenuBar)
        self.Modes.setObjectName("Modes")

        self.jigsMenu = QtGui.QMenu(self.MenuBar)
        self.jigsMenu.setObjectName("jigsMenu")
        
        ###Following will become outdated for Alpha9 Start#####
       
        MainWindow.setMenuBar(self.MenuBar)
        
        ###########################
               #### SUB-MENU ITEMS  ####
        ########################### 
     
        ##### OTHERS Start #####
        
        self.nullAction = QtGui.QAction(MainWindow)
        self.nullAction.setEnabled(False)
        self.nullAction.setIcon(geticon("ui/actions/MainWindowUI_image79"))
        self.nullAction.setVisible(True)
        self.nullAction.setObjectName("nullAction")
        
        self.ccAddLayerAction = QtGui.QAction(MainWindow)
        self.ccAddLayerAction.setEnabled(False)
        self.ccAddLayerAction.setIcon(geticon("ui/actions/"))
        self.ccAddLayerAction.setObjectName("ccAddLayerAction")

        self.toolsDoneAction = QtGui.QAction(MainWindow)
        self.toolsDoneAction.setIcon(geticon(
            "ui/actions/Properties Manager/Done"))
        self.toolsDoneAction.setObjectName("toolsDoneAction")

        self.toolsCancelAction = QtGui.QAction(MainWindow)
        self.toolsCancelAction.setIcon(geticon(
            "ui/actions/Properties Manager/Cancel"))
        self.toolsCancelAction.setObjectName("toolsCancelAction")
        
        
        # Toggle ToolBars 
        self.toggleStandardToolBarAction = QtGui.QAction(MainWindow)
        self.toggleStandardToolBarAction.setCheckable(True)
        self.toggleStandardToolBarAction.setChecked(True)
        self.toggleStandardToolBarAction.setObjectName("toggleStandardToolBarAction")
    
        self.toggleViewToolBarAction = QtGui.QAction(MainWindow)
        self.toggleViewToolBarAction.setCheckable(True)
        self.toggleViewToolBarAction.setChecked(True)
        self.toggleViewToolBarAction.setObjectName("toggleViewToolBarAction")
       
        ##### OTHERS End #####

        ##### UNUSED Menu Start #####
        
        self.fileImageAction = QtGui.QAction(MainWindow)
        self.fileImageAction.setIcon(geticon("ui/actions/MainWindowUI_image3"))
        self.fileImageAction.setObjectName("fileImageAction")
        
        self.editFindAction = QtGui.QAction(MainWindow)
        self.editFindAction.setIcon(geticon("ui/actions/MainWindowUI_image9"))
        self.editFindAction.setObjectName("editFindAction")
        
        self.jigsBearingAction = QtGui.QAction(MainWindow)
        self.jigsBearingAction.setIcon(geticon("ui/actions/MainWindowUI_image26"))
        self.jigsBearingAction.setObjectName("jigsBearingAction")

        self.jigsSpringAction = QtGui.QAction(MainWindow)
        self.jigsSpringAction.setIcon(geticon("ui/actions/MainWindowUI_image27"))
        self.jigsSpringAction.setObjectName("jigsSpringAction")

        self.jigsDynoAction = QtGui.QAction(MainWindow)
        self.jigsDynoAction.setIcon(geticon("ui/actions/MainWindowUI_image28"))
        self.jigsDynoAction.setObjectName("jigsDynoAction")

        self.jigsHeatsinkAction = QtGui.QAction(MainWindow)
        self.jigsHeatsinkAction.setIcon(geticon("ui/actions/MainWindowUI_image29"))
        self.jigsHeatsinkAction.setObjectName("jigsHeatsinkAction")

        self.jigsHandleAction = QtGui.QAction(MainWindow)
        self.jigsHandleAction.setIcon(geticon("ui/actions/MainWindowUI_image31"))
        self.jigsHandleAction.setObjectName("jigsHandleAction")
        
        self.fileClearAction = QtGui.QAction(MainWindow)
        self.fileClearAction.setObjectName("fileClearAction")
        
        self.simNanoHiveAction = QtGui.QAction(MainWindow)
        self.simNanoHiveAction.setIcon(geticon("ui/actions/MainWindowUI_image124"))
        self.simNanoHiveAction.setVisible(False)
        self.simNanoHiveAction.setObjectName("simNanoHiveAction")

        self.fileSaveSelectionAction = QtGui.QAction(MainWindow)
        self.fileSaveSelectionAction.setObjectName("fileSaveSelectionAction")
        
        self.movieNextFrameAction = QtGui.QAction(MainWindow)
        self.movieNextFrameAction.setIcon(geticon("ui/actions/Properties Manager/MainWindowUI_image89"))
        self.movieNextFrameAction.setObjectName("movieNextFrameAction")

        self.moviePrevFrameAction = QtGui.QAction(MainWindow)
        self.moviePrevFrameAction.setIcon(geticon("ui/actions/Properties Manager/MainWindowUI_image90"))
        self.moviePrevFrameAction.setObjectName("moviePrevFrameAction")
        
        self.rotateWindowAction = QtGui.QAction(MainWindow)
        self.rotateWindowAction.setIcon(geticon("ui/actions/MainWindowUI_image95"))
        self.rotateWindowAction.setObjectName("rotateWindowAction")
        
        self.helpContentsAction = QtGui.QAction(MainWindow)
        self.helpContentsAction.setObjectName("helpContentsAction")
    
        
         ##### UNUSED Menu End #####
         
        self.orient100Action = QtGui.QAction(MainWindow)
        self.orient100Action.setCheckable(True)
        self.orient100Action.setIcon(geticon("ui/actions/Properties Manager/Surface100"))
        self.orient100Action.setObjectName("orient100Action")

        self.orient110Action = QtGui.QAction(MainWindow)
        self.orient110Action.setCheckable(True)
        self.orient110Action.setIcon(geticon("ui/actions/Properties Manager/Surface110"))
        self.orient110Action.setObjectName("orient110Action")

        self.orient111Action = QtGui.QAction(MainWindow)
        self.orient111Action.setCheckable(True)
        self.orient111Action.setIcon(geticon("ui/actions/Properties Manager/Surface111"))
        self.orient111Action.setObjectName("orient111Action")

        self.toolsStartOverAction = QtGui.QAction(MainWindow)
        self.toolsStartOverAction.setIcon(geticon("ui/actions/Properties Manager/Startover"))
        self.toolsStartOverAction.setObjectName("toolsStartOverAction")

        self.toolsBackUpAction = QtGui.QAction(MainWindow)
        self.toolsBackUpAction.setIcon(geticon("ui/actions/Properties Manager/Backup"))
        self.toolsBackUpAction.setObjectName("toolsBackUpAction")

        self.toggleDatumDispTbarAction = QtGui.QAction(MainWindow)
        self.toggleDatumDispTbarAction.setCheckable(True)
        self.toggleDatumDispTbarAction.setChecked(False)
        self.toggleDatumDispTbarAction.setObjectName("toggleDatumDispTbarAction")

        self.toggleGridsTbarAction = QtGui.QAction(MainWindow)
        self.toggleGridsTbarAction.setCheckable(True)
        self.toggleGridsTbarAction.setChecked(True)
        self.toggleGridsTbarAction.setObjectName("toggleGridsTbarAction")

        #######Dashboard Actions Start ############
        
        self.movieResetAction = QtGui.QAction(MainWindow)
        self.movieResetAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Reset"))
        self.movieResetAction.setObjectName("movieResetAction")

        self.movieMoveToEndAction = QtGui.QAction(MainWindow)
        self.movieMoveToEndAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Move_To_End"))
        self.movieMoveToEndAction.setObjectName("movieMoveToEndAction")

        self.moviePauseAction = QtGui.QAction(MainWindow)
        self.moviePauseAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Pause"))
        self.moviePauseAction.setObjectName("moviePauseAction")

        self.moviePlayAction = QtGui.QAction(MainWindow)
        self.moviePlayAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Play_Forward"))
        self.moviePlayAction.setVisible(True)
        self.moviePlayAction.setObjectName("moviePlayAction")
        
        self.moviePlayActiveAction = QtGui.QAction(MainWindow)
        self.moviePlayActiveAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Play_Forward_Active"))
        self.moviePlayActiveAction.setObjectName("moviePlayActiveAction")

        self.movieDoneAction = QtGui.QAction(MainWindow)
        self.movieDoneAction.setIcon(geticon("ui/actions/Properties Manager/Properties Manager/Done"))
        self.movieDoneAction.setObjectName("movieDoneAction")

        self.fileSaveMovieAction = QtGui.QAction(MainWindow)
        self.fileSaveMovieAction.setIcon(geticon("ui/actions/Properties Manager/Save"))
        self.fileSaveMovieAction.setObjectName("fileSaveMovieAction")

        self.moviePlayRevAction = QtGui.QAction(MainWindow)
        self.moviePlayRevAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Play_Reverse"))
        self.moviePlayRevAction.setObjectName("moviePlayRevAction")
        
        self.moviePlayRevActiveAction = QtGui.QAction(MainWindow)
        self.moviePlayRevActiveAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Play_Reverse_Active"))
        self.moviePlayRevActiveAction.setObjectName("moviePlayRevActiveAction")

        self.fileOpenMovieAction = QtGui.QAction(MainWindow)
        self.fileOpenMovieAction.setIcon(geticon("ui/actions/Properties Manager/Open"))
        self.fileOpenMovieAction.setObjectName("fileOpenMovieAction")

        self.movieInfoAction = QtGui.QAction(MainWindow)
        self.movieInfoAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Info"))
        self.movieInfoAction.setObjectName("movieInfoAction")

        
        self.panDoneAction = QtGui.QAction(MainWindow)
        self.panDoneAction.setIcon(geticon("ui/actions/Properties Manager/Done"))
        self.panDoneAction.setObjectName("panDoneAction")
        
        self.moveDeltaPlusAction = QtGui.QAction(MainWindow)
        self.moveDeltaPlusAction.setIcon(geticon("ui/actions/Properties Manager/Move_Delta_Plus"))
        self.moveDeltaPlusAction.setObjectName("moveDeltaPlusAction")

        self.moveAbsoluteAction = QtGui.QAction(MainWindow)
        self.moveAbsoluteAction.setIcon(geticon("ui/actions/Properties Manager/Move_Absolute"))
        self.moveAbsoluteAction.setObjectName("moveAbsoluteAction")

        self.moveDeltaMinusAction = QtGui.QAction(MainWindow)
        self.moveDeltaMinusAction.setIcon(geticon("ui/actions/Properties Manager/Move_Delta_Minus"))
        self.moveDeltaMinusAction.setObjectName("moveDeltaMinusAction")

        self.rotateClockwiseAction = QtGui.QAction(MainWindow)
        self.rotateClockwiseAction.setCheckable(False)
        self.rotateClockwiseAction.setIcon(geticon("ui/actions/Properties Manager/Rotate_Clockwise"))
        self.rotateClockwiseAction.setObjectName("rotateClockwiseAction")

        self.rotateCounterClockwiseAction = QtGui.QAction(MainWindow)
        self.rotateCounterClockwiseAction.setCheckable(False)
        self.rotateCounterClockwiseAction.setIcon(geticon("ui/actions/Properties Manager/Rotate_Counter_Clockwise"))
        self.rotateCounterClockwiseAction.setObjectName("rotateCounterClockwiseAction")
               
        self.simJobManagerAction = QtGui.QAction(MainWindow)
        self.simJobManagerAction.setIcon(geticon("ui/actions/MainWindowUI_image118"))
        self.simJobManagerAction.setObjectName("simJobManagerAction")

        self.serverManagerAction = QtGui.QAction(MainWindow)
        self.serverManagerAction.setIcon(geticon("ui/actions/MainWindowUI_image119"))
        self.serverManagerAction.setObjectName("serverManagerAction")

        self.rotateThetaMinusAction = QtGui.QAction(MainWindow)
        self.rotateThetaMinusAction.setIcon(geticon("ui/actions/Properties Manager/Move_Theta_Minus"))
        self.rotateThetaMinusAction.setObjectName("rotateThetaMinusAction")

        self.rotateThetaPlusAction = QtGui.QAction(MainWindow)
        self.rotateThetaPlusAction.setIcon(geticon("ui/actions/Properties Manager/Move_Theta_Plus"))
        self.rotateThetaPlusAction.setObjectName("rotateThetaPlusAction")

        self.modifyMMKitAction = QtGui.QAction(MainWindow)
        self.modifyMMKitAction.setIcon(geticon("ui/actions/Properties Manager/MMKit"))
        self.modifyMMKitAction.setObjectName("modifyMMKitAction")
        
        #######Dashboard Actions End ############
             
        # All the stuff below should be moved out of the MainWindowUI.ui/py world, and out
        # into Nanorex-defined source files.
               
                 
        self.zoomDashboard.addAction(self.toolsDoneAction)
        self.panDashboard.addAction(self.toolsDoneAction)
        self.rotateDashboard.addAction(self.toolsDoneAction)
        
        self.cookieSelectDashboard.addAction(MainWindow.DefaultSelAction)
        self.cookieSelectDashboard.addAction(MainWindow.LassoSelAction)
        self.cookieSelectDashboard.addAction(MainWindow.RectCornerSelAction)
        self.cookieSelectDashboard.addAction(MainWindow.RectCtrSelAction)
        self.cookieSelectDashboard.addAction(MainWindow.SquareSelAction)
        self.cookieSelectDashboard.addAction(MainWindow.TriangleSelAction)
        self.cookieSelectDashboard.addAction(MainWindow.DiamondSelAction)
        self.cookieSelectDashboard.addAction(MainWindow.CircleSelAction)
        self.cookieSelectDashboard.addAction(MainWindow.HexagonSelAction)    
        
        
              
        """ A8 Display menu items Disabled temporarily 061030
        self.displayMenu.addSeparator()
        self.displayMenu.addAction(self.dispObjectColorAction)
        self.displayMenu.addAction(self.dispResetChunkColorAction)
        self.displayMenu.addAction(self.dispResetAtomsDisplayAction)
        self.displayMenu.addAction(self.dispShowInvisAtomsAction)
        self.displayMenu.addSeparator()
        self.displayMenu.addAction(self.dispBGColorAction)
        self.displayMenu.addSeparator()
        self.displayMenu.addAction(self.dispElementColorSettingsAction)
        self.displayMenu.addAction(self.dispLightingAction)
        """
                               
        self.jigsMenu.addAction(self.jigsESPImageAction)
        self.jigsMenu.addAction(self.jigsGamessAction)
        self.jigsMenu.addAction(self.jigsGridPlaneAction)
        self.jigsMenu.addAction(self.jigsAtomSetAction)        
        self.simulationMenu.addAction(self.simNanoHiveAction)      
        
       
        
        #ADD MAIN MENUS TO THE MENUBAR
        self.MenuBar.addAction(self.fileMenu.menuAction())
        self.MenuBar.addAction(self.editMenu.menuAction())
        self.MenuBar.addAction(self.viewMenu.menuAction())
        self.MenuBar.addAction(self.Insert.menuAction())
        self.MenuBar.addAction(self.toolsMenu.menuAction())
        #Main menu 'Animator' disabled for A9 
        ##self.MenuBar.addAction(self.animatorMenu.menuAction())
        self.MenuBar.addAction(self.simulationMenu.menuAction())
        #Main menu 'Window' disabled for A9 
        ##self.MenuBar.addAction(self.windowMenu.menuAction())
        self.MenuBar.addAction(self.helpMenu.menuAction())

        self.retranslateUi(MainWindow)
        
        QtCore.QObject.connect(self.fileExitAction,QtCore.SIGNAL("activated()"),MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "NanoEngineer-1", None, QtGui.QApplication.UnicodeUTF8))
        
        self.cookieCutterDashboard.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Cookie Cutter", None, QtGui.QApplication.UnicodeUTF8))
        self.ccLabel.setText(QtGui.QApplication.translate("MainWindow", "Cookie Cutter", None, QtGui.QApplication.UnicodeUTF8))
        self.moveChunksDashboard.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Move Chunks", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("MainWindow", "Move Chunks", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayerDashboard.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Movie Player Dashboard", None, QtGui.QApplication.UnicodeUTF8))
        self.selectMolDashboard.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Select Molecule", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2.setText(QtGui.QApplication.translate("MainWindow", "Select Chunks", None, QtGui.QApplication.UnicodeUTF8))
        self.zoomDashboard.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Zoom Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.zoomTextLabel.setText(QtGui.QApplication.translate("MainWindow", "Zoom Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.panDashboard.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Pan Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.panTextLabel.setText(QtGui.QApplication.translate("MainWindow", "Pan Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.rotateDashboard.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Rotate Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.rotateTextLabel.setText(QtGui.QApplication.translate("MainWindow", "Rotate Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.fuseChunksDashboard.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Fuse Chunks", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3.setText(QtGui.QApplication.translate("MainWindow", "Fuse Chunks", None, QtGui.QApplication.UnicodeUTF8))
        self.cookieSelectDashboard.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Toolbar", None, QtGui.QApplication.UnicodeUTF8))
               
        
        #Menus and SubMenus
        
        Ui_FileMenu.retranslateUi(self)
        Ui_EditMenu.retranslateUi(self)
        Ui_ViewMenu.retranslateUi(self)     
        Ui_InsertMenu.retranslateUi(self)
        Ui_ToolsMenu.retranslateUi(self)
        Ui_SimulationMenu.retranslateUi(self)
        Ui_HelpMenu.retranslateUi(self)
        
        #Toolbars
        
        Ui_StandardToolBar.retranslateUi(self)
        Ui_ViewToolBar.retranslateUi(self)
        Ui_BuildStructuresToolBar.retranslateUi(self)
        Ui_BuildToolsToolBar.retranslateUi(self)
        Ui_SelectToolBar.retranslateUi(self)
        Ui_SimulationToolBar.retranslateUi(self)
        
        self.animatorMenu.setTitle(QtGui.QApplication.translate("MainWindow", "&Animator", None, QtGui.QApplication.UnicodeUTF8))
        self.windowMenu.setTitle(QtGui.QApplication.translate("MainWindow", "&Window", None, QtGui.QApplication.UnicodeUTF8))
                                
        #Menu Item (Action items) text and icons
                       
        #UNUSED MENU ITEMS 
        self.viewDefviewAction.setText(QtGui.QApplication.translate("MainWindow", "Orientations", None, QtGui.QApplication.UnicodeUTF8))
        self.viewDefviewAction.setIconText(QtGui.QApplication.translate("MainWindow", "Orientations", None, QtGui.QApplication.UnicodeUTF8))
        self.viewDefviewAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Default Views", None, QtGui.QApplication.UnicodeUTF8))
        self.dispBGColorAction.setText(QtGui.QApplication.translate("MainWindow", "&Background Color...", None, QtGui.QApplication.UnicodeUTF8))
        self.dispBGColorAction.setIconText(QtGui.QApplication.translate("MainWindow", "Background Color...", None, QtGui.QApplication.UnicodeUTF8))
        self.editFindAction.setText(QtGui.QApplication.translate("MainWindow", "&Find...", None, QtGui.QApplication.UnicodeUTF8))
        self.editFindAction.setIconText(QtGui.QApplication.translate("MainWindow", "Find", None, QtGui.QApplication.UnicodeUTF8))
       
        self.fileClearAction.setText(QtGui.QApplication.translate("MainWindow", "C&lear", None, QtGui.QApplication.UnicodeUTF8))
        self.fileClearAction.setIconText(QtGui.QApplication.translate("MainWindow", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        
        self.ccAddLayerAction.setText(QtGui.QApplication.translate("MainWindow", "Add Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.ccAddLayerAction.setIconText(QtGui.QApplication.translate("MainWindow", "Add Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.ccAddLayerAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Add a new layer.(Maximum is 6 layer)", None, QtGui.QApplication.UnicodeUTF8))
        self.toolsDoneAction.setText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
        self.toolsDoneAction.setIconText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
        self.toolsCancelAction.setText(QtGui.QApplication.translate("MainWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.toolsCancelAction.setIconText(QtGui.QApplication.translate("MainWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        
 
        self.toggleStandardToolBarAction.setText(QtGui.QApplication.translate("MainWindow", "Standard", None, QtGui.QApplication.UnicodeUTF8))
        self.toggleStandardToolBarAction.setIconText(QtGui.QApplication.translate("MainWindow", "Standard", None, QtGui.QApplication.UnicodeUTF8))
        
        self.toggleViewToolBarAction.setText(QtGui.QApplication.translate("MainWindow", "View", None, QtGui.QApplication.UnicodeUTF8))
        self.toggleViewToolBarAction.setIconText(QtGui.QApplication.translate("MainWindow", "View", None, QtGui.QApplication.UnicodeUTF8))
      
        #self.fileSetWorkDirAction.setText(QtGui.QApplication.translate("MainWindow", "Set &Working Directory...", None, QtGui.QApplication.UnicodeUTF8))
        #self.fileSetWorkDirAction.setIconText(QtGui.QApplication.translate("MainWindow", "Set Working Directory...", None, QtGui.QApplication.UnicodeUTF8))
               
        self.jigsBearingAction.setText(QtGui.QApplication.translate("MainWindow", "&Bearing", None, QtGui.QApplication.UnicodeUTF8))
        self.jigsBearingAction.setIconText(QtGui.QApplication.translate("MainWindow", "Bearing", None, QtGui.QApplication.UnicodeUTF8))
        self.jigsSpringAction.setText(QtGui.QApplication.translate("MainWindow", "&Spring", None, QtGui.QApplication.UnicodeUTF8))
        self.jigsSpringAction.setIconText(QtGui.QApplication.translate("MainWindow", "Spring", None, QtGui.QApplication.UnicodeUTF8))
        self.jigsDynoAction.setText(QtGui.QApplication.translate("MainWindow", "&Dyno", None, QtGui.QApplication.UnicodeUTF8))
        self.jigsDynoAction.setIconText(QtGui.QApplication.translate("MainWindow", "Dyno", None, QtGui.QApplication.UnicodeUTF8))
        self.jigsHeatsinkAction.setText(QtGui.QApplication.translate("MainWindow", "Heatsin&k", None, QtGui.QApplication.UnicodeUTF8))
        self.jigsHeatsinkAction.setIconText(QtGui.QApplication.translate("MainWindow", "Heatsin&k", None, QtGui.QApplication.UnicodeUTF8))
        self.jigsHandleAction.setText(QtGui.QApplication.translate("MainWindow", "&Handle", None, QtGui.QApplication.UnicodeUTF8))
        self.jigsHandleAction.setIconText(QtGui.QApplication.translate("MainWindow", "Handle", None, QtGui.QApplication.UnicodeUTF8))
        
        self.orient100Action.setText(QtGui.QApplication.translate("MainWindow", "Surface 100", None, QtGui.QApplication.UnicodeUTF8))
        self.orient100Action.setIconText(QtGui.QApplication.translate("MainWindow", "Surface 100", None, QtGui.QApplication.UnicodeUTF8))
        self.orient110Action.setText(QtGui.QApplication.translate("MainWindow", "Surface 110", None, QtGui.QApplication.UnicodeUTF8))
        self.orient110Action.setIconText(QtGui.QApplication.translate("MainWindow", "Surface 110", None, QtGui.QApplication.UnicodeUTF8))
        self.orient111Action.setText(QtGui.QApplication.translate("MainWindow", "Surface 111", None, QtGui.QApplication.UnicodeUTF8))
        self.orient111Action.setIconText(QtGui.QApplication.translate("MainWindow", "Surface 111", None, QtGui.QApplication.UnicodeUTF8))
                
        self.toolsStartOverAction.setText(QtGui.QApplication.translate("MainWindow", "Start Over", None, QtGui.QApplication.UnicodeUTF8))
        self.toolsStartOverAction.setIconText(QtGui.QApplication.translate("MainWindow", "Start Over", None, QtGui.QApplication.UnicodeUTF8))
        self.toolsBackUpAction.setText(QtGui.QApplication.translate("MainWindow", "Back Up", None, QtGui.QApplication.UnicodeUTF8))
        self.toolsBackUpAction.setIconText(QtGui.QApplication.translate("MainWindow", "Back Up", None, QtGui.QApplication.UnicodeUTF8))
                
        self.modifyStretchAction.setText(QtGui.QApplication.translate("MainWindow", "S&tretch", None, QtGui.QApplication.UnicodeUTF8))
        self.modifyStretchAction.setIconText(QtGui.QApplication.translate("MainWindow", "Stretch", None, QtGui.QApplication.UnicodeUTF8))      
                
        self.movieResetAction.setText(QtGui.QApplication.translate("MainWindow", "Reset Movie", None, QtGui.QApplication.UnicodeUTF8))
        self.movieResetAction.setIconText(QtGui.QApplication.translate("MainWindow", "Reset Movie", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayRevActiveAction.setText(QtGui.QApplication.translate("MainWindow", "Play Reverse", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayRevActiveAction.setIconText(QtGui.QApplication.translate("MainWindow", "Play Reverse", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayActiveAction.setText(QtGui.QApplication.translate("MainWindow", "Play Forward", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayActiveAction.setIconText(QtGui.QApplication.translate("MainWindow", "Play Forward", None, QtGui.QApplication.UnicodeUTF8))
        self.movieMoveToEndAction.setText(QtGui.QApplication.translate("MainWindow", "Advance To End", None, QtGui.QApplication.UnicodeUTF8))
        self.movieMoveToEndAction.setIconText(QtGui.QApplication.translate("MainWindow", "Advance To End", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePauseAction.setText(QtGui.QApplication.translate("MainWindow", "Pause", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePauseAction.setIconText(QtGui.QApplication.translate("MainWindow", "Pause", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayAction.setText(QtGui.QApplication.translate("MainWindow", "Play Forward", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayAction.setIconText(QtGui.QApplication.translate("MainWindow", "Play Forward", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Play Forward", None, QtGui.QApplication.UnicodeUTF8))
        
        
        self.dispSetEltable1Action.setText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Default", None, QtGui.QApplication.UnicodeUTF8))
        self.dispSetEltable1Action.setIconText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Default", None, QtGui.QApplication.UnicodeUTF8))
        self.dispSetEltable2Action.setText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Alternate", None, QtGui.QApplication.UnicodeUTF8))
        self.dispSetEltable2Action.setIconText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Alternate", None, QtGui.QApplication.UnicodeUTF8))
        self.movieDoneAction.setText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
        self.movieDoneAction.setIconText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
        self.movieNextFrameAction.setText(QtGui.QApplication.translate("MainWindow", "Next", None, QtGui.QApplication.UnicodeUTF8))
        self.movieNextFrameAction.setIconText(QtGui.QApplication.translate("MainWindow", "Next", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePrevFrameAction.setText(QtGui.QApplication.translate("MainWindow", "Prev", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePrevFrameAction.setIconText(QtGui.QApplication.translate("MainWindow", "Prev", None, QtGui.QApplication.UnicodeUTF8))
        self.fileSaveMovieAction.setText(QtGui.QApplication.translate("MainWindow", "Save Movie File...", None, QtGui.QApplication.UnicodeUTF8))
        self.fileSaveMovieAction.setIconText(QtGui.QApplication.translate("MainWindow", "Save Movie File...", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayRevAction.setText(QtGui.QApplication.translate("MainWindow", "Play Reverse", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayRevAction.setIconText(QtGui.QApplication.translate("MainWindow", "Play Reverse", None, QtGui.QApplication.UnicodeUTF8))
        self.fileOpenMovieAction.setText(QtGui.QApplication.translate("MainWindow", "Open Movie File...", None, QtGui.QApplication.UnicodeUTF8))
        self.fileOpenMovieAction.setIconText(QtGui.QApplication.translate("MainWindow", "Open Movie File...", None, QtGui.QApplication.UnicodeUTF8))
        self.movieInfoAction.setText(QtGui.QApplication.translate("MainWindow", "Movie Information", None, QtGui.QApplication.UnicodeUTF8))
        self.movieInfoAction.setIconText(QtGui.QApplication.translate("MainWindow", "Movie Information", None, QtGui.QApplication.UnicodeUTF8))
        
        self.rotateWindowAction.setText(QtGui.QApplication.translate("MainWindow", "Action", None, QtGui.QApplication.UnicodeUTF8))
        self.rotateWindowAction.setIconText(QtGui.QApplication.translate("MainWindow", "Action", None, QtGui.QApplication.UnicodeUTF8))
       
        self.panDoneAction.setText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
        self.panDoneAction.setIconText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
        
        self.dispElementColorSettingsAction.setText(QtGui.QApplication.translate("MainWindow", "Element Color Settings...", None, QtGui.QApplication.UnicodeUTF8))
        self.dispElementColorSettingsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Element Color Settings...", None, QtGui.QApplication.UnicodeUTF8))
        
        self.dispLightingAction.setText(QtGui.QApplication.translate("MainWindow", "Lighting...", None, QtGui.QApplication.UnicodeUTF8))
        self.dispLightingAction.setIconText(QtGui.QApplication.translate("MainWindow", "Lighting", None, QtGui.QApplication.UnicodeUTF8))
        self.dispResetAtomsDisplayAction.setText(QtGui.QApplication.translate("MainWindow", "Reset Atoms Display", None, QtGui.QApplication.UnicodeUTF8))
        self.dispResetAtomsDisplayAction.setIconText(QtGui.QApplication.translate("MainWindow", "Reset Atoms Display", None, QtGui.QApplication.UnicodeUTF8))
        self.dispShowInvisAtomsAction.setText(QtGui.QApplication.translate("MainWindow", "Show Invisible Atoms", None, QtGui.QApplication.UnicodeUTF8))
        self.dispShowInvisAtomsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Show Invisible Atoms", None, QtGui.QApplication.UnicodeUTF8))
        
        self.moveDeltaPlusAction.setText(QtGui.QApplication.translate("MainWindow", "Move Delta (+)", None, QtGui.QApplication.UnicodeUTF8))
        self.moveDeltaPlusAction.setIconText(QtGui.QApplication.translate("MainWindow", "Move Delta (+)", None, QtGui.QApplication.UnicodeUTF8))
        self.moveAbsoluteAction.setText(QtGui.QApplication.translate("MainWindow", "Move Absolute", None, QtGui.QApplication.UnicodeUTF8))
        self.moveAbsoluteAction.setIconText(QtGui.QApplication.translate("MainWindow", "Move Absolute", None, QtGui.QApplication.UnicodeUTF8))
        
        self.moveDeltaMinusAction.setText(QtGui.QApplication.translate("MainWindow", "Move Delta (-)", None, QtGui.QApplication.UnicodeUTF8))
        self.moveDeltaMinusAction.setIconText(QtGui.QApplication.translate("MainWindow", "Move Delta (-)", None, QtGui.QApplication.UnicodeUTF8))
        
        self.rotateClockwiseAction.setText(QtGui.QApplication.translate("MainWindow", "Rotate Clockwise", None, QtGui.QApplication.UnicodeUTF8))
        self.rotateClockwiseAction.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate Clockwise", None, QtGui.QApplication.UnicodeUTF8))
        self.rotateCounterClockwiseAction.setText(QtGui.QApplication.translate("MainWindow", "Rotate Counter Clockwise", None, QtGui.QApplication.UnicodeUTF8))
        self.rotateCounterClockwiseAction.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate Counter Clockwise", None, QtGui.QApplication.UnicodeUTF8))
        
        self.simJobManagerAction.setText(QtGui.QApplication.translate("MainWindow", "Job Manager...", None, QtGui.QApplication.UnicodeUTF8))
        self.simJobManagerAction.setIconText(QtGui.QApplication.translate("MainWindow", "Job Manager...", None, QtGui.QApplication.UnicodeUTF8))
        self.serverManagerAction.setText(QtGui.QApplication.translate("MainWindow", "Server Manager...", None, QtGui.QApplication.UnicodeUTF8))
        self.serverManagerAction.setIconText(QtGui.QApplication.translate("MainWindow", "Server Manager...", None, QtGui.QApplication.UnicodeUTF8))
        self.rotateThetaMinusAction.setText(QtGui.QApplication.translate("MainWindow", "Rotate Theta (-)", None, QtGui.QApplication.UnicodeUTF8))
        self.rotateThetaMinusAction.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate Theta (-)", None, QtGui.QApplication.UnicodeUTF8))
        self.rotateThetaPlusAction.setText(QtGui.QApplication.translate("MainWindow", "Rotate Theta (+)", None, QtGui.QApplication.UnicodeUTF8))
        self.rotateThetaPlusAction.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate Theta (+)", None, QtGui.QApplication.UnicodeUTF8))
        
        self.modifyMMKitAction.setIconText(QtGui.QApplication.translate("MainWindow", "Molecular Modeling Kit", None, QtGui.QApplication.UnicodeUTF8))
        self.modifyMMKitAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Modeling Kit", None, QtGui.QApplication.UnicodeUTF8))
        
        
        self.simNanoHiveAction.setText(QtGui.QApplication.translate("MainWindow", "Nano-Hive...", None, QtGui.QApplication.UnicodeUTF8))
        self.simNanoHiveAction.setIconText(QtGui.QApplication.translate("MainWindow", "Nano-Hive", None, QtGui.QApplication.UnicodeUTF8))
        
        
        
        self.fileSaveSelectionAction.setIconText(QtGui.QApplication.translate("MainWindow", "Save Selection...", None, QtGui.QApplication.UnicodeUTF8))
        self.viewRotatePlus90Action.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate View +90", None, QtGui.QApplication.UnicodeUTF8))
        self.viewRotateMinus90Action.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate View -90", None, QtGui.QApplication.UnicodeUTF8))
                
        self.viewNormalToAction.setIconText(QtGui.QApplication.translate("MainWindow", "Set View Normal To", None, QtGui.QApplication.UnicodeUTF8))
        self.viewNormalToAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Set View Normal To", None, QtGui.QApplication.UnicodeUTF8))
        self.viewParallelToAction.setIconText(QtGui.QApplication.translate("MainWindow", "Set View Parallel To", None, QtGui.QApplication.UnicodeUTF8))
        self.viewParallelToAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Set View Parallel To", None, QtGui.QApplication.UnicodeUTF8))
        
        self.viewQuteMolAction.setIconText(QtGui.QApplication.translate("MainWindow", "QuteMol", None, QtGui.QApplication.UnicodeUTF8))
        self.viewRaytraceSceneAction.setIconText(QtGui.QApplication.translate("MainWindow", "POV-Ray", None, QtGui.QApplication.UnicodeUTF8))
        
