# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
MWsemantics.py provides the main window class, MWsemantics.


$Id$

History: too much to mention, except for breakups of the file.

[maybe some of those are not listed here?]
Huaicai ??? split out cookieMode slots (into separate class)
bruce 050413 split out movieDashboardSlotsMixin
bruce 050907 split out fileSlotsMixin
mark 060120 split out viewSlotsMixin

[Much more splitup of this file is needed. Ideally we would
split up the class MWsemantics (as for cookieMode), not just the file.]

[some of that splitup has been done, now, by Ninad in the Qt4 branch]
"""

from PyQt4.Qt import QMainWindow, QFrame, SIGNAL, QFileDialog
from PyQt4.Qt import QCursor, QBitmap, QLabel, QSplitter, QMessageBox, QString, QColorDialog, QColor
from PyQt4 import QtCore
from GLPane import GLPane 
from assembly import assembly 
from drawer import get_gl_info_string ## grantham 20051201
import os, sys
import help
from math import ceil
from modelTree import modelTree 
import platform
from qt4transition import *
from Utility import geticon

from constants import *
from PropMgr_Constants import pmDefaultWidth, pmMaxWidth, pmMinWidth
from elementColors import elementColors 
from elementSelector import elementSelector 
from MMKit import MMKit
from fileIO import * # this might be needed for some of the many other modules it imports; who knows? [bruce 050418 comment]
from Sponsors import PermissionDialog
from debug_prefs import debug_pref, Choice_boolean_False

from ViewOrientationWindow import ViewOrientationWindow # Ninad 061121

# most of the file format imports are probably no longer needed; I'm removing some of them
# (but we need to check for imports of them from here by other modules) [bruce 050907]
from files_pdb import readpdb, insertpdb, writepdb
from files_gms import readgms, insertgms
from files_mmp import readmmp, insertmmp

from debug import print_compact_traceback

from MainWindowUI import Ui_MainWindow
from HistoryWidget import greenmsg, redmsg

from movieMode import movieDashboardSlotsMixin
from ops_files import fileSlotsMixin
from ops_view import viewSlotsMixin 
from changes import register_postinit_object
import preferences
import env 
import undo 

elementSelectorWin = None
elementColorsWin = None
MMKitWin = None
windowList = []


eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]

eCCBtab2 = {}
for i,elno in zip(range(len(eCCBtab1)), eCCBtab1):
    eCCBtab2[elno] = i

recentfiles_use_QSettings = True #bruce 050919 debug flag (replacing use of __debug__) ###@@@

########################################################################

class PartWindow(QWidget):
    def __init__(self, assy, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.setWindowTitle("My Part Window")
	self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
	
        _layout = QtGui.QHBoxLayout(self)
        layout = QSplitter(Qt.Horizontal)
        layout.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        _layout.addWidget(layout)

        #########################

	# <holder> - the area to the left of the vertical splitter, next to the
	# GLPane. 
        holder = QWidget(parent)
        holder.setMinimumWidth(pmMinWidth) # Mark 2007-05-24
	holder.setMaximumWidth(pmMaxWidth) # Always defaults to this width. (no good).
	self.resize(pmDefaultWidth, holder.sizeHint().height())
        
        sublayout = QVBoxLayout(holder)
        sublayout.setMargin(0)
        sublayout.setSpacing(0)
        
	layout.addWidget(holder)
	
        ###

        self.featureManager = QtGui.QTabWidget()
        self.featureManager.setCurrentIndex(0)
	self.featureManager.setAutoFillBackground(True)	
	
	from widgets import RGBf_to_QColor
		
	palette = QtGui.QPalette()
	#bgrole(10) is 'Window'
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(10),QtGui.QColor(230,231,230))
	##following won't give a gradient background ( we set it for glpane using paintGL.) . Need to make backgrounds of glpane and 
	## feature manager identical. 
	##palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(10), RGBf_to_QColor(self.glpane.backgroundColor))
	self.featureManager.setPalette(palette)
	
	#self.featureManager.setMinimumSize(0,0)
        self.featureManager.setMinimumWidth(pmMinWidth) # Mark 2007-05-24
	self.featureManager.setMaximumWidth(pmMaxWidth) # Mark 2007-05-24
	self.resize(pmDefaultWidth, holder.sizeHint().height())
	#ninad 070102 Setting the size policy as 'Ignored' makes the default MT widget width to 0
	#so commenting out the following for now
	
	#self.featureManager.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
					
        self.modelTreeTab = QtGui.QWidget()
        self.featureManager.addTab(self.modelTreeTab,geticon("ui/modeltree/Model_Tree"), "") 
	
        modelTreeTabLayout = QtGui.QVBoxLayout(self.modelTreeTab)
        modelTreeTabLayout.setMargin(0)
        modelTreeTabLayout.setSpacing(0)
			
        self.propertyManagerTab = QtGui.QWidget()
	
	self.propertyManagerScrollArea = QtGui.QScrollArea(self.featureManager)
	#self.propertyManagerScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
	self.propertyManagerScrollArea.setAlignment(Qt.AlignHCenter)
	self.propertyManagerScrollArea.setWidget(self.propertyManagerTab) 	
		
	self.featureManager.addTab(self.propertyManagerScrollArea, geticon("ui/modeltree/Property_Manager"), "")       
        sublayout.addWidget(self.featureManager)

        ###

        self.modelTree = modelTree(self.modelTreeTab, parent)
        modelTreeTabLayout.addWidget(self.modelTree.modelTreeGui)

	vlayout = QSplitter(Qt.Vertical, layout)
        self.glpane = GLPane(assy, self, 'glpane name', parent)		    	
	qt4warnDestruction(self.glpane, 'GLPane of PartWindow')
        vlayout.addWidget(self.glpane)
	
		
	from HistoryWidget import HistoryWidget
	
        histfile = platform.make_history_filename() #@@@ ninad 061213 This is likely a new bug for multipane concept 
	#as each file in a session will have its own history widget
	qt4todo('histfile = platform.make_history_filename()')
	
        #bruce 050913 renamed self.history to self.history_object, and deprecated direct access
        # to self.history; code should use env.history to emit messages, self.history_widget
        # to see the history widget, or self.history_object to see its owning object per se
        # rather than as a place to emit messages (this is rarely needed).
        self.history_object = HistoryWidget(self, filename = histfile, mkdirs = 1)
            # this is not a Qt widget, but its owner;
            # use self.history_widget for Qt calls that need the widget itself.
        self.history_widget = self.history_object.widget
	self.history_widget.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
	
            #bruce 050913, in case future code splits history widget (as main window subwidget)
            # from history message recipient (the global object env.history).
        
        env.history = self.history_object #bruce 050727, revised 050913
	
	vlayout.addWidget(self.history_widget)
	
	layout.addWidget(vlayout)

    def setRowCol(self, row, col):
        self.row, self.col = row, col
	
    def updatePropertyManagerTab(self, tab): #Ninad 061207
	"Update the Properties Manager tab with 'tab' "
	
	if self.propertyManagerScrollArea.widget():
	    #The following is necessary to get rid of those c object deleted errors (and the resulting bugs)
	    lastwidgetobject = self.propertyManagerScrollArea.takeWidget()  
	    lastwidgetobject.hide() # @ ninad 061212 perhaps hiding the widget is not needed
	       
	self.featureManager.removeTab(self.featureManager.indexOf(self.propertyManagerScrollArea))

	
	#Set the PropertyManager tab scroll area to the appropriate widget .at
	self.propertyManagerScrollArea.setWidget(tab)
		
	self.featureManager.addTab(self.propertyManagerScrollArea, 
				   geticon("ui/modeltree/Property_Manager"), "")
				   
	self.featureManager.setCurrentIndex(self.featureManager.indexOf(self.propertyManagerScrollArea))
	

    def dismiss(self):
        self.parent.removePartWindow(self)

class GridPosition:
    def __init__(self):
        self.row, self.col = 0, 0
        self.availableSlots = [ ]
        self.takenSlots = { }

    def next(self, widget):
        if len(self.availableSlots) > 0:
            row, col = self.availableSlots.pop(0)
        else:
            row, col = self.row, self.col
            if row == col:
                # when on the diagonal, start a new self.column
                self.row = 0
                self.col = col + 1
            elif row < col:
                # continue moving down the right edge until we're about
                # to hit the diagonal, then start a new bottom self.row
                if row == col - 1:
                    self.row = row + 1
                    self.col = 0
                else:
                    self.row = row + 1
            else:
                # move right along the bottom edge til you hit the diagonal
                self.col = col + 1
        self.takenSlots[widget] = (row, col)
        return row, col

    def removeWidget(self, widget):
        rc = self.takenSlots[widget]
        self.availableSlots.append(rc)
        del self.takenSlots[widget]

########################################################################

class MWsemantics(QMainWindow, fileSlotsMixin, viewSlotsMixin, movieDashboardSlotsMixin, Ui_MainWindow):
    "The single Main Window object."

    #bruce 050413 split out movieDashboardSlotsMixin, which needs to come before MainWindow
    # in the list of superclasses, since MainWindow overrides its methods with "NIM stubs".
    #bruce 050906: same for fileSlotsMixin.
    #mark 060120: same for viewSlotsMixin.
    
    initialised = 0 #bruce 041222
    _ok_to_autosave_geometry_changes = False #bruce 051218

    # This determines the location of "Open Recent Files" menu item in the File Menu. Mark 060807.
    RECENT_FILES_MENU_ITEM = None

    def __init__(self, parent = None, name = None):
    
        global windowList
        self._activepw = None
	
        self.orientationWindow = None
		
        undo.just_before_mainwindow_super_init()

        qt4warning('MainWindow.__init__(self, parent, name, Qt.WDestructiveClose) - what is destructive close?')
        QMainWindow.__init__(self, parent)
        self.DefaultSelAction = QAction(self)
        self.LassoSelAction = QAction(self)
        self.RectCornerSelAction = QAction(self)
        self.RectCtrSelAction = QAction(self)
        self.SquareSelAction = QAction(self)
        self.TriangleSelAction = QAction(self)
        self.DiamondSelAction = QAction(self)
        self.CircleSelAction = QAction(self)
        self.HexagonSelAction = QAction(self)

                	
        self.setViewPerspecAction = QAction(self)
	self.setViewPerspecAction.setText(QtGui.QApplication.translate("MainWindow", "Perspective",
                                                  None, QtGui.QApplication.UnicodeUTF8))
	
        self.setViewOrthoAction = QAction(self)
	self.setViewOrthoAction.setText(QtGui.QApplication.translate("MainWindow", "Orthographic",
                                                  None, QtGui.QApplication.UnicodeUTF8))
	

        self.toolsSelectAtomsAction = QAction(self)
        self.simMoviePlayerAction = QAction(self)
        self.setupUi(self)	 
	
	#hide these toolbars by default @@@ ninad070330. 
        #This(display and position of toolbars) needs to be a preference sooner. 
	self.buildStructuresToolBar.hide()
	self.buildToolsToolBar.hide()
	self.selectToolBar.hide()
	self.simulationToolBar.hide()
	
                       

        self.MoveOptionsGroup = QActionGroup(self)
        self.MoveOptionsGroup.setObjectName("MoveOptionsGroup")
	self.MoveOptionsGroup.setExclusive(True)
	
	self.moveFreeAction = QAction(self.MoveOptionsGroup)
        self.moveFreeAction.setObjectName("moveFreeAction")
        self.moveFreeAction.setCheckable(True)
	self.moveFreeAction.setIcon(geticon("ui/actions/Properties Manager/Move_Free"))
	
        self.transXAction = QAction(self.MoveOptionsGroup)
        self.transXAction.setObjectName("transXAction")
        self.transXAction.setCheckable(True)
        self.transXAction.setIcon(geticon("ui/actions/Properties Manager/TranslateX"))
        self.transYAction = QAction(self.MoveOptionsGroup)
        self.transYAction.setObjectName("transYAction")
        self.transYAction.setCheckable(True)
        self.transYAction.setIcon(geticon("ui/actions/Properties Manager/TranslateY"))
        self.transZAction = QAction(self.MoveOptionsGroup)
        self.transZAction.setObjectName("transZAction")
        self.transZAction.setCheckable(True)
        self.transZAction.setIcon(geticon("ui/actions/Properties Manager/TranslateZ"))
	
	#Free Drag rotate action group (rotate components groupbox)
	self.rotateOptionsGroup = QActionGroup(self)
	self.rotateOptionsGroup.setObjectName("RotateOptionsGroup")
	self.rotateOptionsGroup.setExclusive(True)
		
	#Ninad 070308 added rotate free action (free drag rotate) -- See Move/ Rotate Property manager . 
        self.rotateFreeAction = QAction(self.rotateOptionsGroup)
	self.rotateFreeAction.setObjectName("rotateFreeAction")
	self.rotateFreeAction.setCheckable(True)	
        self.rotateFreeAction.setIcon(geticon("ui/actions/Properties Manager/Rotate_Free"))
	
        self.rotXAction = QAction(self.rotateOptionsGroup)
        self.rotXAction.setObjectName("rotXAction")
        self.rotXAction.setCheckable(True)
        self.rotXAction.setIcon(geticon("ui/actions/Properties Manager/RotateX"))
        self.rotYAction = QAction(self.rotateOptionsGroup)
        self.rotYAction.setObjectName("rotYAction")
        self.rotYAction.setCheckable(True)
        self.rotYAction.setIcon(geticon("ui/actions/Properties Manager/RotateY"))
        self.rotZAction = QAction(self.rotateOptionsGroup)
        self.rotZAction.setObjectName("rotZAction")
        self.rotZAction.setCheckable(True)
        self.rotZAction.setIcon(geticon("ui/actions/Properties Manager/RotateZ"))
	        
        	
        self.moveDeltaPlusAction = QAction(self)
        self.moveDeltaPlusAction.setObjectName("moveDeltaPlusAction")
        self.moveDeltaPlusAction.setIcon(geticon("ui/actions/Properties Manager/Move_Delta_Plus"))
        self.moveAbsoluteAction = QAction(self)
        self.moveAbsoluteAction.setObjectName("moveAbsoluteAction")
        self.moveAbsoluteAction.setIcon(geticon("ui/actions/Properties Manager/Move_Absolute"))
        self.moveDeltaMinusAction = QAction(self)
        self.moveDeltaMinusAction.setObjectName("moveDeltaMinusAction")
        self.moveDeltaMinusAction.setIcon(geticon("ui/actions/Properties Manager/Move_Delta_Minus"))
        self.rotateThetaMinusAction = QAction(self)
        self.rotateThetaMinusAction.setObjectName("rotateThetaMinusAction")
        self.rotateThetaMinusAction.setIcon(geticon("ui/actions/Properties Manager/Move_Theta_Minus"))
        self.rotateThetaPlusAction = QAction(self)
        self.rotateThetaPlusAction.setObjectName("rotateThetaPlusAction")
        self.rotateThetaPlusAction.setIcon(geticon("ui/actions/Properties Manager/Move_Theta_Plus"))

        self.connect(self.dispBGColorAction,SIGNAL("triggered()"),self.dispBGColor)
        self.connect(self.dispBallAction,SIGNAL("triggered()"),self.dispBall)
        self.connect(self.dispDefaultAction,SIGNAL("triggered()"),self.dispDefault)
        self.connect(self.dispElementColorSettingsAction,SIGNAL("triggered()"),self.dispElementColorSettings)
        self.connect(self.dispInvisAction,SIGNAL("triggered()"),self.dispInvis)
        self.connect(self.dispLightingAction,SIGNAL("triggered()"),self.dispLighting)
        self.connect(self.dispLinesAction,SIGNAL("triggered()"),self.dispLines)
        self.connect(self.dispObjectColorAction,SIGNAL("triggered()"),self.dispObjectColor)
        self.connect(self.dispResetAtomsDisplayAction,SIGNAL("triggered()"),self.dispResetAtomsDisplay)
        self.connect(self.dispResetChunkColorAction,SIGNAL("triggered()"),self.dispResetChunkColor)
        self.connect(self.dispShowInvisAtomsAction,SIGNAL("triggered()"),self.dispShowInvisAtoms)
        self.connect(self.dispTubesAction,SIGNAL("triggered()"),self.dispTubes)
        self.connect(self.dispCPKAction,SIGNAL("triggered()"),self.dispCPK)
	self.connect(self.dispHybridAction,SIGNAL("triggered()"),self.dispHybrid)
	
        self.connect(self.editAutoCheckpointingAction,SIGNAL("toggled(bool)"),self.editAutoCheckpointing)
        self.connect(self.editClearUndoStackAction,SIGNAL("triggered()"),self.editClearUndoStack)
        self.connect(self.editCopyAction,SIGNAL("triggered()"),self.editCopy)
        self.connect(self.editCutAction,SIGNAL("triggered()"),self.editCut)
        self.connect(self.editDeleteAction,SIGNAL("triggered()"),self.killDo)
        #self.connect(self.editFindAction,SIGNAL("triggered()"),self.editFind)
        self.connect(self.editMakeCheckpointAction,SIGNAL("triggered()"),self.editMakeCheckpoint)
        self.connect(self.editPasteAction,SIGNAL("triggered()"),self.editPaste)
        self.connect(self.editPrefsAction,SIGNAL("triggered()"),self.editPrefs)
        self.connect(self.editRedoAction,SIGNAL("triggered()"),self.editRedo)
        self.connect(self.editUndoAction,SIGNAL("triggered()"),self.editUndo)
        #self.connect(self.fileClearAction,SIGNAL("triggered()"),self.fileClear)
        self.connect(self.fileCloseAction,SIGNAL("triggered()"),self.fileClose)
        self.connect(self.fileExitAction,SIGNAL("triggered()"),self.close)
        #self.connect(self.fileImageAction,SIGNAL("triggered()"),self.fileImage)
        self.connect(self.fileInsertAction,SIGNAL("triggered()"),self.fileInsert)
        self.connect(self.fileOpenAction,SIGNAL("triggered()"),self.fileOpen)
        self.connect(self.fileOpenMovieAction,SIGNAL("triggered()"),self.fileOpenMovie)
        self.connect(self.fileSaveAction,SIGNAL("triggered()"),self.fileSave)
        self.connect(self.fileSaveAsAction,SIGNAL("triggered()"),self.fileSaveAs)
        self.connect(self.fileSaveMovieAction,SIGNAL("triggered()"),self.fileSaveMovie)
        self.connect(self.fileSaveSelectionAction,SIGNAL("triggered()"),self.fileSaveSelection)
        self.connect(self.fileSetWorkDirAction,SIGNAL("triggered()"),self.fileSetWorkDir)
        #self.connect(self.frameNumberSB,SIGNAL("valueChanged(int)"),self.moviePlayFrame)
        #self.connect(self.frameNumberSL,SIGNAL("valueChanged(int)"),self.movieSlider)
        self.connect(self.helpAboutAction,SIGNAL("triggered()"),self.helpAbout)
        #self.connect(self.helpContentsAction,SIGNAL("triggered()"),self.helpContents)
        self.connect(self.helpGraphicsCardAction,SIGNAL("triggered()"),self.helpGraphicsCard)
        self.connect(self.helpKeyboardShortcutsAction,SIGNAL("triggered()"),self.helpKeyboardShortcuts)
        self.connect(self.helpMouseControlsAction,SIGNAL("triggered()"),self.helpMouseControls)
        self.connect(self.helpWhatsThisAction,SIGNAL("triggered()"),self.helpWhatsThis)
        self.connect(self.buildDnaAction,SIGNAL("triggered()"),self.insertDna)
        self.connect(self.insertCommentAction,SIGNAL("triggered()"),self.insertComment)
        self.connect(self.insertNanotubeAction,SIGNAL("triggered()"),self.insertNanotube)
        self.connect(self.insertGrapheneAction,SIGNAL("triggered()"),self.insertGraphene)
        self.connect(self.jigsAnchorAction,SIGNAL("triggered()"),self.makeAnchor)
        self.connect(self.jigsAngleAction,SIGNAL("triggered()"),self.makeMeasureAngle)
        self.connect(self.jigsAtomSetAction,SIGNAL("triggered()"),self.makeAtomSet)
        #self.connect(self.jigsBearingAction,SIGNAL("triggered()"),self.makeBearing)
        self.connect(self.jigsDihedralAction,SIGNAL("triggered()"),self.makeMeasureDihedral)
        self.connect(self.jigsDistanceAction,SIGNAL("triggered()"),self.makeMeasureDistance)
        #self.connect(self.jigsDynoAction,SIGNAL("triggered()"),self.makeDyno)
        self.connect(self.jigsESPImageAction,SIGNAL("triggered()"),self.makeESPImage)
        self.connect(self.jigsGamessAction,SIGNAL("triggered()"),self.makeGamess)
        self.connect(self.jigsGridPlaneAction,SIGNAL("triggered()"),self.makeGridPlane)
	
	self.connect(self.referencePlaneAction,SIGNAL("triggered()"),
		     self.createPlane)
	
        #self.connect(self.jigsHandleAction,SIGNAL("triggered()"),self.makeHandle)
        #self.connect(self.jigsHeatsinkAction,SIGNAL("triggered()"),self.makeHeatsink)
        self.connect(self.jigsLinearMotorAction,SIGNAL("triggered()"),self.makeLinearMotor)
        self.connect(self.jigsMotorAction,SIGNAL("triggered()"),self.makeMotor)
        #self.connect(self.jigsSpringAction,SIGNAL("triggered()"),self.makeSpring)
        self.connect(self.jigsStatAction,SIGNAL("triggered()"),self.makeStat)
        self.connect(self.jigsThermoAction,SIGNAL("triggered()"),self.makeThermo)
        self.connect(self.modifyAlignCommonAxisAction,SIGNAL("triggered()"),self.modifyAlignCommonAxis)
        self.connect(self.modifyCenterCommonAxisAction,SIGNAL("triggered()"),self.modifyCenterCommonAxis)
        self.connect(self.modifyDehydrogenateAction,SIGNAL("triggered()"),self.modifyDehydrogenate)
        self.connect(self.modifyDeleteBondsAction,SIGNAL("triggered()"),self.modifyDeleteBonds)
        self.connect(self.modifyHydrogenateAction,SIGNAL("triggered()"),self.modifyHydrogenate)
        self.connect(self.modifyInvertAction,SIGNAL("triggered()"),self.modifyInvert)
        self.connect(self.modifyMergeAction,SIGNAL("triggered()"),self.modifyMerge)
	self.connect(self.makeChunkFromAtomsAction,
		     SIGNAL("triggered()"),self.makeChunkFromAtom)
	
	
        self.connect(self.modifyAdjustAllAction,SIGNAL("triggered()"),self.modifyAdjustAll)
        self.connect(self.modifyAdjustSelAction,SIGNAL("triggered()"),self.modifyAdjustSel)
        self.connect(self.modifyMMKitAction,SIGNAL("triggered()"),self.modifyMMKit)
        self.connect(self.modifyPassivateAction,SIGNAL("triggered()"),self.modifyPassivate)
        self.connect(self.modifySeparateAction,SIGNAL("triggered()"),self.modifySeparate)
        self.connect(self.modifyStretchAction,SIGNAL("triggered()"),self.modifyStretch)
        #self.connect(self.movieDoneAction,SIGNAL("triggered()"),self.movieDone)
        self.connect(self.movieInfoAction,SIGNAL("triggered()"),self.movieInfo)
        self.connect(self.movieMoveToEndAction,SIGNAL("triggered()"),self.movieMoveToEnd)
        self.connect(self.moviePauseAction,SIGNAL("triggered()"),self.moviePause)
        self.connect(self.moviePlayAction,SIGNAL("triggered()"),self.moviePlay)
        self.connect(self.moviePlayRevAction,SIGNAL("triggered()"),self.moviePlayRev)
        self.connect(self.movieResetAction,SIGNAL("triggered()"),self.movieReset)
        #self.connect(self.orient100Action,SIGNAL("triggered()"),self.orient100)
        #self.connect(self.orient110Action,SIGNAL("triggered()"),self.orient110)
        #self.connect(self.orient111Action,SIGNAL("triggered()"),self.orient111)
        #self.connect(self.panDoneAction,SIGNAL("triggered()"),self.panDone)
        self.connect(self.panToolAction,SIGNAL("toggled(bool)"),self.panTool)
        self.connect(self.rotateToolAction,SIGNAL("toggled(bool)"),self.rotateTool)
        self.connect(self.saveNamedViewAction,SIGNAL("triggered()"),self.saveNamedView)
        self.connect(self.selectAllAction,SIGNAL("triggered()"),self.selectAll)
        self.connect(self.selectConnectedAction,SIGNAL("triggered()"),self.selectConnected)
        self.connect(self.selectContractAction,SIGNAL("triggered()"),self.selectContract)
        self.connect(self.selectDoublyAction,SIGNAL("triggered()"),self.selectDoubly)
        self.connect(self.selectExpandAction,SIGNAL("triggered()"),self.selectExpand)
        self.connect(self.selectInvertAction,SIGNAL("triggered()"),self.selectInvert)
        self.connect(self.selectNoneAction,SIGNAL("triggered()"),self.selectNone)
        self.connect(self.serverManagerAction,SIGNAL("triggered()"),self.serverManager)
        
        self.connect(self.viewOrientationAction,SIGNAL("triggered()"),self.showOrientationWindow) #ninad061114
	
	
	
	##When Standard Views button is clicked, show its QMenu.-- By default, nothing happens if you click on the 
	##toolbutton with submenus. The menus are displayed only when you click on the small downward arrow 
	## of the tool button. Therefore the following slot is added. Also QWidgetAction is used 
	## for it to add this feature (see Ui_ViewToolBar for details) ninad 070109 
	self.connect(self.standardViews_btn,SIGNAL("pressed()"),self.showStandardViewsMenu)
	
	self.connect(self.viewBackAction,SIGNAL("triggered()"),self.viewBack)
        self.connect(self.viewBottomAction,SIGNAL("triggered()"),self.viewBottom)
        self.connect(self.setViewFitToWindowAction,SIGNAL("triggered()"),self.setViewFitToWindow)
        self.connect(self.viewFrontAction,SIGNAL("triggered()"),self.viewFront)
        self.connect(self.setViewHomeAction,SIGNAL("triggered()"),self.setViewHome)
        self.connect(self.setViewHomeToCurrentAction,SIGNAL("triggered()"),self.setViewHomeToCurrent)
        self.connect(self.viewLeftAction,SIGNAL("triggered()"),self.viewLeft)
        self.connect(self.viewRotateMinus90Action,SIGNAL("triggered()"),self.viewRotateMinus90)
        self.connect(self.viewNormalToAction,SIGNAL("triggered()"),self.viewNormalTo)
        self.connect(self.viewRotate180Action,SIGNAL("triggered()"),self.viewRotate180)
        self.connect(self.setViewOrthoAction,SIGNAL("triggered()"),self.setViewOrtho)
        self.connect(self.viewParallelToAction,SIGNAL("triggered()"),self.viewParallelTo)
        self.connect(self.setViewPerspecAction,SIGNAL("triggered()"),self.setViewPerspec)
        self.connect(self.viewRotatePlus90Action,SIGNAL("triggered()"),self.viewRotatePlus90)
        self.connect(self.setViewRecenterAction,SIGNAL("triggered()"),self.setViewRecenter)
        self.connect(self.viewRightAction,SIGNAL("triggered()"),self.viewRight)
        self.connect(self.viewTopAction,SIGNAL("triggered()"),self.viewTop)
        self.connect(self.simJobManagerAction,SIGNAL("triggered()"),self.JobManager)
        self.connect(self.simMoviePlayerAction,SIGNAL("triggered()"),self.simMoviePlayer)
        self.connect(self.simNanoHiveAction,SIGNAL("triggered()"),self.simNanoHive)
        self.connect(self.simPlotToolAction,SIGNAL("triggered()"),self.simPlot)
        self.connect(self.simSetupAction,SIGNAL("triggered()"),self.simSetup)
        #self.connect(self.toggleDatumDispTbarAction,SIGNAL("triggered()"),self.toggleDatumDispTbar)
        #self.connect(self.toggleEditTbarAction,SIGNAL("triggered()"),self.toggleEditTbar)
        #self.connect(self.toggleFileTbarAction,SIGNAL("triggered()"),self.toggleFileTbar)
        #self.connect(self.toggleModelDispTbarAction,SIGNAL("triggered()"),self.toggleModelDispTbar)
        #self.connect(self.toggleModifyTbarAction,SIGNAL("triggered()"),self.toggleModifyTbar)
        #self.connect(self.toggleSelectTbarAction,SIGNAL("triggered()"),self.toggleSelectTbar)
        #self.connect(self.toggleToolsTbarAction,SIGNAL("triggered()"),self.toggleToolsTbar)
        #self.connect(self.toggleViewTbarAction,SIGNAL("triggered()"),self.toggleViewTbar)
        self.connect(self.toolsBackUpAction,SIGNAL("triggered()"),self.toolsBackUp)
        self.connect(self.toolsCancelAction,SIGNAL("triggered()"),self.toolsCancel)
        self.connect(self.toolsCookieCutAction,SIGNAL("triggered()"),self.toolsCookieCut)
	
        self.connect(self.toolsDepositAtomAction,
		     SIGNAL("triggered()"),
		     self.toolsBuildAtoms)
	
	#Slot for DNA Origami
	self.connect(self.buildDnaOrigamiAction,
		     SIGNAL("triggered()"),
		     self.buildDnaOrigami)
	
        self.connect(self.toolsDoneAction,SIGNAL("triggered()"),self.toolsDone)
        self.connect(self.toolsExtrudeAction,SIGNAL("triggered()"),self.toolsExtrude)
        ###self.connect(self.toolsFuseAtomsAction,SIGNAL("triggered()"),self.toolsFuseAtoms)
        self.connect(self.toolsFuseChunksAction,SIGNAL("triggered()"),self.toolsFuseChunks)
        ###self.connect(self.toolsMirrorAction,SIGNAL("triggered()"),self.toolsMirror)
        ###self.connect(self.toolsMirrorCircularBoundaryAction,SIGNAL("triggered()"),self.toolsMirrorCircularBoundary)
	#Move and Rotate Components mode
        self.connect(self.toolsMoveMoleculeAction,SIGNAL("triggered()"),self.toolsMoveMolecule)
	self.connect(self.rotateComponentsAction,SIGNAL("triggered()"),self.toolsRotateComponents)
	
        ###self.connect(self.toolsRevolveAction,SIGNAL("triggered()"),self.toolsRevolve)
        self.connect(self.toolsSelectAtomsAction,SIGNAL("triggered()"),self.toolsSelectAtoms)
        self.connect(self.toolsSelectMoleculesAction,SIGNAL("triggered()"),self.toolsSelectMolecules)
        self.connect(self.toolsStartOverAction,SIGNAL("triggered()"),self.toolsStartOver)
        self.connect(self.zoomToolAction,SIGNAL("toggled(bool)"),self.zoomTool)
	self.connect(self.viewZoomAboutScreenCenterAction,SIGNAL("toggled(bool)"),
		     self.changeZoomBehavior)
        self.connect(self.viewRaytraceSceneAction,SIGNAL("triggered()"),self.viewRaytraceScene)
        self.connect(self.insertPovraySceneAction,SIGNAL("triggered()"),self.insertPovrayScene)
        self.connect(self.dispSurfaceAction,SIGNAL("triggered()"),self.dispSurface)
        self.connect(self.dispCylinderAction,SIGNAL("triggered()"),self.dispCylinder)
        self.connect(self.simMinimizeEnergyAction,SIGNAL("triggered()"),self.simMinimizeEnergy)
        self.connect(self.fileImportAction,SIGNAL("triggered()"),self.fileImport)
        self.connect(self.fileExportAction,SIGNAL("triggered()"),self.fileExport)
        self.connect(self.viewIsometricAction,SIGNAL("triggered()"),self.viewIsometric)
        self.connect(self.modifyMirrorAction,SIGNAL("triggered()"),self.modifyMirror)
        self.connect(self.setViewZoomtoSelectionAction,SIGNAL("triggered()"),self.setViewZoomToSelection)

        # mark 060105 commented out self.make_buttons_not_in_UI_file()
        # Now done below: _StatusBar.do_what_MainWindowUI_should_do(self)
        #self.make_buttons_not_in_UI_file()

        undo.just_after_mainwindow_super_init()

        # bruce 050104 moved this here so it can be used earlier
        # (it might need to be moved into main.py at some point)
        self.tmpFilePath = platform.find_or_make_Nanorex_directory()

        
        import depositMode as _depositMode
        _depositMode.do_what_MainWindowUI_should_do(self)
        
        # mark 050711: Added Select Atoms dashboard.
        import selectMode as _selectMode
        _selectMode.do_what_MainWindowUI_should_do(self)
        
        # mark 050411: Added Move Mode dashboard.
        import modifyMode as _modifyMode
        _modifyMode.do_what_MainWindowUI_should_do(self)
        
        # mark 050428: Added Fuse Chunk dashboard.
        import fusechunksMode as _fusechunksMode
        _fusechunksMode.do_what_MainWindowUI_should_do(self)
        
               
        # Load additional icons to QAction iconsets.
        # self.load_icons_to_iconsets() # Uncomment this line to test if Redo button has custom icon when disabled. mark 060427
        
        # Load all the custom cursors
        from cursors import loadCursors
        loadCursors(self)
        
        # Hide all dashboards
        self.hideDashboards()

        #qt4todo('just a hack'); print self.moviePlayerDashboard; self.moviePlayerDashboard.show()
        
        # Create our 2 status bar widgets - msgbarLabel and modebarLabel
        # (see also env.history.message())
        import StatusBar as _StatusBar
        _StatusBar.do_what_MainWindowUI_should_do(self)
	
        windowList += [self]
        if name == None:
            self.setWindowTitle("NanoEngineer-1") # Mark 11-05-2004

        # start with empty window 
        self.assy = assembly(self, "Untitled", own_window_UI = True) # own_window_UI is required for this assy to support Undo
            #bruce 060127 added own_window_UI flag to help fix bug 1403
        #bruce 050429: as part of fixing bug 413, it's now required to call
        # self.assy.reset_changed() sometime in this method; it's called below.
        
        # Set the caption to the name of the current (default) part - Mark [2004-10-11]
        self.update_mainwindow_caption()
        
        # hsplitter and vsplitter reimplemented. mark 060222.
        # Create the horizontal-splitter between the model tree (left) and the glpane 
        # and history widget (right)
        hsplitter = QSplitter(Qt.Horizontal, self)

        from debug_prefs import this_session_permit_property_pane
        mtree_in_a_vsplitter = this_session_permit_property_pane() or False
            #bruce 060402 experiment; works (except for initial width), but DO NOT COMMIT WITH True
        # only bug known so far is mtree (vsplitter2) width
        if mtree_in_a_vsplitter:
            vsplitter2 = QSplitter(Qt.Vertical, hsplitter)
            self.vsplitter2 = vsplitter2 # use this for property pane parent? doesn't work, don't know why. [060623]
            ## vsplitter2.setBaseSize(QSize(225,150)) #k experiment, guess, height is wrong; has no effect
            mtree_parent = vsplitter2
	    
        else:
            mtree_parent = hsplitter
	    
        if not debug_pref("Multipane GUI", Choice_boolean_False):
            # Create the model tree widget. Width of 225 matches width of MMKit.  Mark 060222.
            self.mt = modelTree(mtree_parent, self)
	    self.mt.setMinimumSize(0, 0)
	    #self.mt.setColumnWidth(0,225)
	    
            if mtree_in_a_vsplitter:
                mtree_view_in_hsplitter = vsplitter2
            else:
                mtree_view_in_hsplitter = self.mt.modelTreeGui  # @@ninad 061205 replaced self.mt with self.mt.modelTreeGui 
		#to get   hsplitter.setStretchFactor working (without errors)
		        
        # Create the vertical-splitter between the glpane (top) and the
        # history widget (bottom) [history is new as of 041223]
        vsplitter = QSplitter(Qt.Vertical, hsplitter)
        
        if not debug_pref("Multipane GUI", Choice_boolean_False):
            if 0: 
                #& This creates a gplane with a black 1 pixel border around it.  Leave it in in case we want to use this.
                #& mark 060222. [bruce 060612 committed with 'if 0', in an updated/tested form]
                glframe = QFrame(vsplitter)
                glframe.setFrameShape ( QFrame.Box ) 
                flayout = QVBoxLayout(glframe,1,1,'flayout')
                self.glpane = GLPane(self.assy, glframe, "glpane", self)
                flayout.addWidget(self.glpane,1)
            else:
                # Create the glpane - where all the action is!
                self.glpane = GLPane(self.assy, vsplitter, "glpane", self)
                    #bruce 050911 revised GLPane.__init__ -- now it leaves glpane's mode as nullmode;
                    # we change it below, since doing so now would be too early for some modes permitted as startup mode
                    # (e.g. Build mode, which when Entered needs self.Element to exist, as of 050911)
         
	if not debug_pref("Multipane GUI", Choice_boolean_False):
	    # Create the history area at the bottom
	    from HistoryWidget import HistoryWidget
	    histfile = platform.make_history_filename()
	    #bruce 050913 renamed self.history to self.history_object, and deprecated direct access
	    # to self.history; code should use env.history to emit messages, self.history_widget
	    # to see the history widget, or self.history_object to see its owning object per se
	    # rather than as a place to emit messages (this is rarely needed).
	    self.history_object = HistoryWidget(vsplitter, filename = histfile, mkdirs = 1)
		# this is not a Qt widget, but its owner;
		# use self.history_widget for Qt calls that need the widget itself.
	    self.history_widget = self.history_object.widget
	    
		#bruce 050913, in case future code splits history widget (as main window subwidget)
		# from history message recipient (the global object env.history).
	    
	    env.history = self.history_object #bruce 050727, revised 050913

        # Some final hsplitter setup...
        hsplitter.setHandleWidth(3) # Default is 5 pixels (too wide).  mark 060222.
        qt4todo('hsplitter.setResizeMode(mtree_view_in_hsplitter, QSplitter.KeepSize)')
	qt4todo('hsplitter.setStretchFactor(hsplitter.indexOf(mtree_view_in_hsplitter), 0)')
	#hsplitter.setStretchFactor(0, 0)
	hsplitter.setOpaqueResize(False)	
	
        	
        # ... and some final vsplitter setup [bruce 041223]
        vsplitter.setHandleWidth(3) # Default is 5 pixels (too wide).  mark 060222.
        qt4todo('vsplitter.setResizeMode(self.history_widget, QSplitter.KeepSize)')
	qt4todo('vsplitter.setStretchFactor(vsplitter.indexOf(self.history_widget), 0)')
        vsplitter.setOpaqueResize(False)
	
        if not debug_pref("Multipane GUI", Choice_boolean_False):
            self.setCentralWidget(hsplitter) # This is required.
            # This makes the hsplitter the central widget, spanning the height of the mainwindow.
            # mark 060222.
	    

        if mtree_in_a_vsplitter:
            hsplitter.setSizes([225,]) #e this works, but 225 is evidently not always the MMKit width (e.g. on bruce's iMac g4)
            vsplitter2.setHandleWidth(3)
            vsplitter2.setOpaqueResize(False)
            # client code adding things to vsplitter2 may want to call something like:
            ## vsplitter2.setResizeMode(newthing-in-vsplitter2, QSplitter.KeepSize)
	    

        if debug_pref("Multipane GUI", Choice_boolean_False):
            # Create the "What's This?" online help system.
            from whatsthis import createWhatsThis
            createWhatsThis(self)

            start_element = 6 # Carbon

            # Start with Carbon as the default element (for Deposit Mode and the Element Selector)
            self.Element = start_element
            self.setElement(start_element)

            # Attr/list for Atom Selection Filter. mark 060401
            self.filtered_elements = [] # Holds list of elements to be selected when the Atom Selection Filter is enabled.
            self.filtered_elements.append(PeriodicTable.getElement(start_element)) # Carbon
            self.selection_filter_enabled = False # Set to True to enable the Atom Selection Filter.

            self.currentWorkingDirectory = ''
            self.hideDashboards()
            self.setWindowTitle("My Main Window")
            MAIN_WINDOW_SIZE = (800, 600)
            self.setMinimumWidth(MAIN_WINDOW_SIZE[0])
            self.setMinimumHeight(MAIN_WINDOW_SIZE[1])

            ##############################################

            centralwidget = QWidget()
            self.setCentralWidget(centralwidget)
            layout = QVBoxLayout(centralwidget)
            layout.setMargin(0)
            layout.setSpacing(0)
            middlewidget = QWidget()
	    
	    
	    from CommandManager import CommandManager
	    
	    self.commandManager = CommandManager(self)
	    self.cmdManager = self.commandManager.cmdManager  
	    layout.addWidget(self.cmdManager)	    
	    
	    
            layout.addWidget(middlewidget)
            self.layout = QGridLayout(middlewidget)
            self.layout.setMargin(0)
            self.layout.setSpacing(0)
            self.gridPosition = GridPosition()
            self.numParts = 0

            self.addPartWindow(self.assy)
        else:
            self.init_part_two()
    
    def createPopupMenu(self):#Ninad 070328
	''' Reimplemented createPopPupMenu method that allows 
	display of custom context menu (toolbars and dockwidgets) 
	when you rightclick on QMainWindow widget. '''
	menu = QMenu(self)
	contextMenuToolBars = [self.standardToolBar, self.viewToolBar,
			   self.simulationToolBar, self.buildToolsToolBar,
			   self.selectToolBar, self.buildStructuresToolBar]
	for toolbar in contextMenuToolBars:
	    menu.addAction(toolbar.toggleViewAction())
	return menu
	
	
    def removePartWindow(self, pw):
        self.layout.removeWidget(pw)
        self.gridPosition.removeWidget(pw)
        self.numParts -= 1
        if self.numParts == 0:
            self.cmdManagerControlArea.hide()
        # [bruce 070503 question: why do we not worry about whether pw == self._activepw?]

    def addPartWindow(self, assy):
        # This should be associated with fileOpen (ops_files.py) or with creating a new structure
        # from scratch.
        # [bruce 070503 question: why do we get passed an assy, and use it for some things and self.assy for others?]
        if self.numParts == 0:
            #self.cmdManagerControlArea.show()
	    self.cmdManager.show()
        self.numParts += 1
        pw = PartWindow(assy, self)
        row, col = self.gridPosition.next(pw)
        self.layout.addWidget(pw, row, col)
        self.assy.o = pw.glpane
        self.assy.mt = pw.modelTree #bruce 070509 revised this, was pw.modelTree.modelTreeGui
        self._activepw = pw
            # Note: nothing in this class can set self._activepw (except to None),
            # which one might guess means that no code yet switches between partwindows,
            # but GLPane.makeCurrent *does* set self._activepw to its .partWindow
            # (initialized to its parent arg when it's created), so that conclusion is not clear.
            # [bruce 070503 comment]
        if not hasattr(self, '_init_part_two_done'):
            # I bet there are pieces of init_part_two that should be done EVERY time we bring up a
            # new partwindow.
            # [I guess that comment is by Will... for now, this code doesn't do those things
            #  more than once, it appears. [bruce 070503 comment]]
            MWsemantics.init_part_two(self)
            self._init_part_two_done = True
                # WARNING: even setting it to False would have the same effect on the hasattr test above. [bruce 070503 comment]

        pw.glpane.start_using_mode('$STARTUP_MODE') #bruce 050911
	

    def __getattr__(self, key):
        #
        # Somebody wants our glpane, but we no longer have just one glpane. We have one
        # glpane for each PartWindow, and only one PartWindow is active.
        #
        def locate(attr):
            try:
                raise Exception
            except:
                import sys
                tb = sys.exc_info()[2]
                f = tb.tb_frame
                f = f.f_back.f_back
                print 'MainWindow.'+attr+' ->', f.f_code.co_filename, f.f_code.co_name, f.f_lineno
        if debug_pref("Multipane GUI", Choice_boolean_False):
            if key == 'glpane':
                # locate('glpane')   # who is asking for this?
                pw = self.activePartWindow()
                assert pw is not None
                return pw.glpane
            if key == 'mt':
                # locate('mt')    # who is asking for this?
                pw = self.activePartWindow()
                assert pw is not None
                return pw.modelTree
        raise AttributeError(key)
        
    def init_part_two(self):
        # Create the Preferences dialog widget.
        # Mark 050628
        if not debug_pref("Multipane GUI", Choice_boolean_False):
            self.assy.o = self.glpane
        from UserPrefs import UserPrefs
        self.uprefs = UserPrefs(self.assy)

        # Enable/disable plugins.  These should be moved to a central method
        # where all plug-ins get added and enabled during invocation.  Mark 050921.
        self.uprefs.enable_nanohive(env.prefs[nanohive_enabled_prefs_key])
        self.uprefs.enable_gamess(env.prefs[gamess_enabled_prefs_key])
        
        #Zoom behavior setting  (View > Zoom About Screen Center)
        self.viewZoomAboutScreenCenterAction.setChecked(
	    env.prefs[zoomAboutScreenCenter_prefs_key])
        
        #Huaicai 9/14/05: Initialization for the 'Recently opened files' feature
        from PyQt4.Qt import QSettings, QWhatsThis
        menuItem = self.RECENT_FILES_MENU_ITEM
        if recentfiles_use_QSettings:
            prefsSetting = QSettings("Nanorex", "NanoEngineer-1")
        else:
            prefsSetting = preferences.prefs_context()
	    
        if recentfiles_use_QSettings:
            # Qt3: fileList = prefsSetting.readListEntry('/Nanorex/nE-1/recentFiles')[0]
            fileList = prefsSetting.value('/Nanorex/nE-1/recentFiles').toStringList()
        else:
            fileList = prefsSetting.get('/Nanorex/nE-1/recentFiles', [])
        if len(fileList):  
            qt4warning('self.fileMenu.setItemEnabled(menuItem, True)')
            if menuItem is not None: menuItem.setEnabled(True)
            self._createRecentFilesList()
        else:
            qt4warning('self.fileMenu.setItemEnabled(menuItem, False)')
            if menuItem is not None: menuItem.setEnabled(False)
        self.helpMouseControlsAction.setWhatsThis('Displays help for mouse controls')
        self.helpKeyboardShortcutsAction.setWhatsThis('Displays help for keyboard shortcuts')
        self.insertCommentAction.setWhatsThis('Inserts a comment in the part.')

        # Create the Help dialog. Mark 050812
        from help import Help
        self.help = Help()

        # Create the Nanotube generator dialog.  Fixes bug 1091. Mark 060112.
        from GrapheneGenerator import GrapheneGenerator
        self.graphenecntl = GrapheneGenerator(self)
        from NanotubeGenerator import NanotubeGenerator
        self.nanotubecntl = NanotubeGenerator(self)
        from DnaGenerator import DnaGenerator
        self.dnacntl = DnaGenerator(self)
        from PovraySceneProp import PovraySceneProp
        self.povrayscenecntl = PovraySceneProp(self)
        from CommentProp import CommentProp
        self.commentcntl = CommentProp(self)
        # Minimize Energy dialog. Mark 060705.
        from MinimizeEnergyProp import MinimizeEnergyProp
        self.minimize_energy = MinimizeEnergyProp(self)
	
        
        if not debug_pref("Multipane GUI", Choice_boolean_False):
            # do here to avoid a circular dependency
            # note: as of long before now, this doesn't normally run [bruce 070503 comment]
            self.assy.o = self.glpane
            self.assy.mt = self.mt

        # We must enable keyboard focus for a widget if it processes
        # keyboard events. [Note added by bruce 041223: I don't know if this is
        # needed for this window; it's needed for some subwidgets, incl. glpane,
        # and done in their own code. This window forwards its own key events to
        # the glpane. This doesn't prevent other subwidgets from having focus.]
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        # Hide the "Make Checkpoint" toolbar button/menu item. mark 060302.
        self.editMakeCheckpointAction.setVisible(False)

        # Create the "What's This?" online help system.
        from whatsthis import createWhatsThis, fix_whatsthis_text_and_links
        if not debug_pref("Multipane GUI", Choice_boolean_False):
            createWhatsThis(self)

        # IMPORTANT: All widget creation (i.e. dashboards, dialogs, etc.) and their 
        # whatthis text should be created before this line. [If this is not possible,
        # we'll need to split out some functions within this one which can be called
        # later on individual QActions and/or QWidgets. bruce 060319]
        fix_whatsthis_text_and_links(self, refix_later = (self.editMenu,)) # (main call) Fixes bug 1136.  Mark 051126.
            # [bruce 060319 added refix_later as part of fixing bug 1421]

        if not debug_pref("Multipane GUI", Choice_boolean_False):
            start_element = 6 # Carbon

            # Attr/list for Atom Selection Filter. mark 060401
            self.filtered_elements = [] # Holds list of elements to be selected when the Atom Selection Filter is enabled.
            self.filtered_elements.append(PeriodicTable.getElement(start_element)) # Carbon
            self.selection_filter_enabled = False # Set to True to enable the Atom Selection Filter.

            # Start with Carbon as the default element (for Deposit Mode and the Element Selector)
            self.Element = start_element
            self.setElement(start_element)

        # 'depositState' is used by depositMode and MMKit to synchonize the 
        # depositMode dashboard (Deposit and Paste toggle buttons) and the MMKit pages (tabs).
        # It is also used to determine what type of object (atom, clipboard chunk or library part)
        # to deposit when pressing the left mouse button in Build mode.
        #
        # depositState can be either:
        #   'Atoms' - deposit an atom based on the current atom type selected in the MMKit 'Atoms'
        #           page or dashboard atom type combobox(es).
        #   'Clipboard' - deposit a chunk from the clipboard based on what is currently selected in
        #           the MMKit 'Clipboard' page or dashboard clipboard/paste combobox.
        #   'Library' - deposit a part from the library based on what is currently selected in the
        #           MMKit 'Library' page.  There is no dashboard option for this.
        self.depositState = 'Atoms'
        
        self.assy.reset_changed() #bruce 050429, part of fixing bug 413
        
        # Movie Player Flag.  Mark 051209.
        # 'movie_is_playing' is a flag that indicates a movie is playing. It is used by other code to
        # speed up rendering times by disabling the (re)building of display lists for each frame
        # of the movie.
        self.movie_is_playing = False
	
	# Current Working Directory (CWD).
	# When NE1 starts, the CWD is set to the Working Directory (WD) pref from the prefs db. 
	# Every time the user opens or inserts a file during a session, the CWD changes to the directory containing
	# that file. When the user closes the current file and then attempts to open a new file, the CWD will still
	# be the directory of the last file opened or inserted. 
	# If the user changes the WD via 'File > Set Working Directory' when a file is open, 
	# the CWD will not be changed to the new WD. (This rule may change. Need to discuss with Ninad).
	# On the other hand, if there is no part open, the CWD will be changed to the new WD.  Mark 060729.
	self.currentWorkingDirectory = ''

	# Before setting the CWD, make sure the WD from the prefs db exists (it might have been deleted). 
	# If not, set the CWD to the default WD.
	if os.path.isdir(env.prefs[workingDirectory_prefs_key]): 
	    self.currentWorkingDirectory = env.prefs[workingDirectory_prefs_key]
	else:
	    self.currentWorkingDirectory = getDefaultWorkingDirectory()

        #bruce 050810 replaced user preference initialization with this, and revised update_mainwindow_caption to match
        from changes import Formula
        self._caption_formula = Formula(
            # this should depend on whatever update_mainwindow_caption_properly depends on;
            # but it can't yet depend on assy.has_changed(),
            # so that calls update_mainwindow_caption_properly (or the equiv) directly.
            lambda: (env.prefs[captionPrefix_prefs_key],
                     env.prefs[captionSuffix_prefs_key],
                     env.prefs[captionFullPath_prefs_key]),
            self.update_mainwindow_caption_properly
        )
        
        #bruce 050810 part of QToolButton Tiger bug workaround
        # [intentionally called on all systems,
        #  though it will only do anything on Macs except during debugging]
        if 1:
            from debug import auto_enable_MacOSX_Tiger_workaround_if_desired
            auto_enable_MacOSX_Tiger_workaround_if_desired( self)

        self.initialised = 1 # enables win_update [should this be moved into _init_after_geometry_is_set?? bruce 060104 question]

        # be told to add new Jigs menu items, now or as they become available [bruce 050504]
        register_postinit_object( "Jigs menu items", self )

        # Anything which depends on this window's geometry (which is not yet set at this point)
        # should be done in the _init_after_geometry_is_set method below, not here. [bruce guess 060104]

        return # from MWsemantics.__init__

    def activePartWindow(self):
        return self._activepw

    def closeEvent(self, ce):
        fileSlotsMixin.closeEvent(self, ce)

    def sponsoredList(self):
        return (self.graphenecntl,
                self.nanotubecntl,
                self.dnacntl,
                self.povrayscenecntl,
                self.minimize_energy)

    def _init_after_geometry_is_set(self): #bruce 060104 renamed this from startRun and replaced its docstring.
        """Do whatever initialization of self needs to wait until its geometry has been set.
        [Should be called only once, after geometry is set; can be called before self is shown.]
        """
        # older docstring:
        # After the main window(its size and location) has been setup, begin to run the program from this method. 
        # [Huaicai 11/1/05: try to fix the initial MMKitWin off screen problem by splitting from the __init__() method]
        
        if not debug_pref("Multipane GUI", Choice_boolean_False):
            self.glpane.start_using_mode( '$STARTUP_MODE') #bruce 050911
            # Note: this might depend on self's geometry in choosing dialog placement, so it shouldn't be done in __init__.

        self.win_update() # bruce 041222
        undo.just_before_mainwindow_init_returns() # (this is now misnamed, now that it's not part of __init__)
        return

    def cleanUpBeforeExiting(self): #bruce 060127 added this re bug 1412 (Python crashes on exit, newly common)
        try:
            env.history.message(greenmsg("Exiting program."))
            if env.prefs[rememberWinPosSize_prefs_key]: # Fixes bug 1249-2. Mark 060518.
                self.uprefs.save_current_win_pos_and_size()
            ## this seems to take too long, and is probably not needed: self.__clear()
            self.deleteMMKit()  # wware 060406 bug 1263 - don't leave MMKit open after exiting program
	    self.deleteOrientationWindow() # ninad 061121- perhaps its unnecessary
            self.assy.deinit()
                # in particular, stop trying to update Undo/Redo actions all the time
                # (which might cause crashes once their associated widgets are deallocated)
        except:
            print_compact_traceback( "exception (ignored) in cleanUpBeforeExiting: " )
        return
    
    def postinit_item(self, item): #bruce 050504
        try:
            item(self)
        except:
            # blame item
            print_compact_traceback( "exception (ignored) in postinit_item(%r): " % item )
        return

    # == start of code which is unused as of 060106 -- might become real soon, don't know yet;
    # please don't remove it without asking me [bruce 060106]
    
##    stack_of_extended_ops = None
##        # owns a stack of nested actions-with-duration that can be aborted or paused (last first). [bruce 060104]
##
##    def make_buttons_not_in_UI_file(self): #bruce 060104
##        """Make whatever buttons, actions, etc, are for some reason (perhaps a temporary reason)
##        not made in our superclass .ui file. [If you move them into there, remove their code from here,
##        but I suggest not removing this method even if it becomes empty.]
##        """
##        # Abort Simulation button and menu item (we will dynamically change its text in methods of self.stack_of_extended_ops)
##        #e (make this adder a little helper routine, or loop over table?)
##        self.simAbortAction = QAction(self,"simAbortAction")
##        self.simAbortAction.setEnabled(True) # disabled by default -- no, enabled for now, so it's visible... ###@@@
##        if 1:
##            from Utility import imagename_to_pixmap
##            pixmap = imagename_to_pixmap("stopsign.png")
##                # icon file stopsign.png (as of bruce 060104) works in menu but not in toolbar (for Mac Panther)
##                # (actually it works when enabled, it's just gray when disabled, in toolbar.)
##        self.simAbortAction.setIcon(QIcon(pixmap))
##        self.simToolbar.addAction(self.simAbortAction)
##        self.simulatorMenu.addAction(self.simAbortAction)
##        self.connect(self.simAbortAction,SIGNAL("triggered()"),self.simAbort)
##        self.simAbortAction.setText("Abort Sim") # removed __tr, could add it back if desired
##        self.simAbortAction.setMenuText("Abort Sim...")
##
##        ###e also need pause and continue, one hidden and one shown; imitate movie player icons etc
##        
##        if 1: # this is needed here even if the self.simAbortAction initializing code gets moved into the .ui file
##          if 0: ###@@@ DISABLED FOR SAFE COMMIT OF UNFINISHED CODE [bruce 060104]
##            from extended_ops import ExtendedOpStack
##            self.stack_of_extended_ops = ExtendedOpStack(self, [self.simAbortAction])
##                #e in present implem this knows a lot about self.simAbortAction; needs cleanup
##            self.stack_of_extended_ops.update_UI()
##        return
##
##    def simAbort_orig(self): #bruce 060104 ###e also need pause and continue
##        "[slot method]"
##        print "MWsemantics.simAbort(): simAbortButton clicked"
##        if self.stack_of_extended_ops:
##            self.stack_of_extended_ops.do_abort()
##        return

    # == end of code which is unused as of 060106
    
    sim_abort_button_pressed = False #bruce 060106
    
    def simAbort(self):
        '''Original slot for Abort button.
        '''
        if platform.atom_debug and self.sim_abort_button_pressed: #bruce 060106
            print "atom_debug: self.sim_abort_button_pressed is already True before we even put up our dialog"
        
        # Added confirmation before aborting as part of fix to bug 915. Mark 050824.
        # Bug 915 had to do with a problem if the user accidently hit the space bar or espace key,
        # which would call this slot and abort the simulation.  This should no longer be an issue here
        # since we aren't using a dialog.  I still like having this confirmation anyway.  
        # IMHO, it should be kept. Mark 060106. 
        ret = QMessageBox.warning( self, "Confirm",
            "Please confirm you want to abort.\n",
            "Confirm",
            "Cancel", 
            "", 
            1,  # The "default" button, when user presses Enter or Return (1 = Cancel)
            1)  # Escape (1= Cancel)
          
        if ret==0: # Confirmed
            self.sim_abort_button_pressed = True
    
    def update_mode_status(self, mode_obj = None):
        """[by bruce 040927]
        
        Update the text shown in self.modebarLabel (if that widget
        exists yet).  Get the text to use from mode_obj if supplied,
        otherwise from the current mode object
        (self.glpane.mode). (The mode object has to be supplied when
        the currently stored one is incorrect, during a mode
        transition.)

        This method needs to be called whenever the mode status text
        might need to change.  See a comment in the method to find out
        what code should call it.
        
        """
        # There are at least 3 general ways we could be sure to call
        # this method often enough; the initial implementation of
        # 040927 uses (approximately) way #1:
        # 
        # (1) Call it after any user-event-handler that might change
        # what the mode status text should be.  This is reasonable,
        # but has the danger that we might forget about some kind of
        # user-event that ought to change it. (As of 040927, we call
        # this method from this file (after tool button actions
        # related to selection), and from the mode code (after mode
        # changes).)
        # 
        # (2) Call it after any user-event at all (except for
        # mouse-move or mouse-drag).  This would probably be best (##e
        # so do it!), since it's simple, won't miss anything, and is
        # probably efficient enough.  (But if we ever support
        # text-editing, we might have to exclude keypress/keyrelease
        # from this, for efficiency.)
        # 
        # (3) Call it after any internal change which might affect the
        # mode-status text. This would have to include, at least, any
        # change to (the id of) self.glpane, self.glpane.mode,
        # self.glpane.assy, or (the value of)
        # self.glpane.assy.selwhat, regardless of the initial cause of
        # that change. The problems with this method are: it's
        # complicated; we might miss a necessary update call; we'd
        # have to be careful for efficiency to avoid too many calls
        # after a single user event (e.g. one for which we iterate
        # over all atoms and "select parts" redundantly for each one);
        # or we'd have to make many calls permissible, by separating
        # this method into an "update-needed" notice (just setting a
        # flag), and a "do-update" function, which does the update
        # only when the flag is set. But if we did the latter, it
        # would be simpler and probably faster to just dispense with
        # the flag and always update, i.e. to use method (2).
        
        try:
            widget = self.modebarLabel
        except AttributeError:
            print "Caught <AttributeError: self.modebarLabel>, normal behavior, not a bug"
            pass # this is normal, before the widget exists
        else:
            mode_obj = mode_obj or self.glpane.mode
            text = mode_obj.get_mode_status_text()
            #widget.setText( text )


    ##################################################
    # The beginnings of an invalidate/update mechanism
    # at the moment it just does update whether needed or not
    ##################################################

    def win_update(self): # bruce 050107 renamed this from 'update'
        """ Update most state which directly affects the GUI display,
        in some cases repainting it directly.
        (Someday this should update all of it, but only what's needed,
        and perhaps also call QWidget.update. #e)
        [no longer named update, since that conflicts with QWidget.update]
        """
        if not self.initialised:
            return #bruce 041222
        if debug_pref("Multipane GUI", Choice_boolean_False):
            pw = self.activePartWindow()
            pw.glpane.gl_update()
            pw.modelTree.mt_update()
	    pw.history_object.h_update()
        else:
            self.glpane.gl_update()
            self.mt.mt_update()	
	    self.history_object.h_update() #bruce 050104
		# this is self.history_object, not env.history,
		# since it's really about this window's widget-owner,
		# not about the place to print history messages [bruce 050913]
        
    ###################################
    # File Toolbar Slots 
    ###################################

    # file toolbar slots are inherited from fileSlotsMixin (in ops_files.py) as of bruce 050907.
    # Notes:
    #   #e closeEvent method (moved to fileSlotsMixin) should be split in two
    # and the outer part moved back into this file.
    #   __clear method was moved to fileSlotsMixin (as it should be), even though
    # its name-mangled name thereby changed, and some comments in other code
    # still refer to it as MWsemantics.__clear. It should be given an ordinary name.

    
    ###################################
    # Edit Toolbar Slots
    ###################################

    def editMakeCheckpoint(self):
        '''Slot for making a checkpoint (only available when Automatic Checkpointing is disabled).
        '''
        import undo_manager, debug
        debug.reload_once_per_event(undo_manager) # only reloads if atom_debug is set
        undo_manager.editMakeCheckpoint()
        ## env.history.message("Make Checkpoint: Not implemented yet.")
        return
        
    def editUndo(self):
        self.assy.editUndo()

    def editRedo(self):
        self.assy.editRedo()
        
    def editAutoCheckpointing(self, enabled):
        '''Slot for enabling/disabling automatic checkpointing.
        '''
        import undo_manager, debug
        debug.reload_once_per_event(undo_manager) # only reloads if atom_debug is set
        undo_manager.editAutoCheckpointing(enabled)
            # that will probably do (among other things): self.editMakeCheckpointAction.setVisible(not enabled)
        return
            
    def editClearUndoStack(self):
        '''Slot for clearing the Undo Stack.  Requires the user to confirm.
        '''
        import undo_manager, debug
        debug.reload_once_per_event(undo_manager) # only reloads if atom_debug is set
        undo_manager.editClearUndoStack()
        return

    # bruce 050131 moved some history messages from the following methods
    # into the assy methods they call, so the menu command versions also have them
    
    def editCut(self):
        self.assy.cut_sel()
        self.win_update()

    def editCopy(self):
        self.assy.copy_sel()
        self.win_update()

    def editPaste(self):
        if self.assy.shelf.members:
            env.history.message(greenmsg("Paste:"))
	    if self.glpane.mode.modename != "DEPOSIT":
		self.glpane.setMode('DEPOSIT')
		
	    self.glpane.mode.change2ClipboardPage() # Fixed bug 1230.  Mark 051219.
            
    # editDelete
    def killDo(self):
        """ Deletes selected atoms, chunks, jigs and groups.
        """
        self.assy.delete_sel()
        ##bruce 050427 moved win_update into delete_sel as part of fixing bug 566
        ##self.win_update()

    def editPrefs(self):
        """ Edit Preferences """
        self.uprefs.showDialog()
        
    ###################################
    # View Toolbar Slots 
    ###################################

    # view toolbar slots are inherited from viewSlotsMixin (in ops_view.py) as of mark 060120.
        
    ###################################
    # Display Toolbar Slots
    ###################################
    
    # set display formats in whatever is selected,
    # or the GLPane global default if nothing is
    def dispDefault(self):
        self.setDisplay(diDEFAULT, True)

    def dispInvis(self):
        self.setDisplay(diINVISIBLE)

    def dispCPK(self): #e this slot method (here and in .ui file) renamed from dispVdW to dispCPK [bruce 060607]
        self.setDisplay(diTrueCPK)
	
    def dispHybrid(self): #@@ Ninad 070308
	print "Hybrid display is  Implemented yet"
	pass

    def dispTubes(self):
        self.setDisplay(diTUBES)

    def dispBall(self): #e this slot method (here and in .ui file) renamed from dispCPK to dispBall [bruce 060607]
        self.setDisplay(diBALL)

    def dispLines(self):
        self.setDisplay(diLINES)
    
    def dispCylinder(self):
        cmd = greenmsg("Set Display Cylinder: ")
        if self.assy and self.assy.selatoms:
            # Fixes bug 2005. Mark 060702.
            env.history.message(cmd + "Selected atoms cannot have their display mode set to Cylinder.")
            return #ninad 061003  fixed bug 2286... Note: Once atoms and chunks are allowed to be sel at the same 
            #time , this fix might need further mods. 
        self.setDisplay(diCYLINDER)
        
    def dispSurface(self):
        cmd = greenmsg("Set Display Surface: ")
        if self.assy and self.assy.selatoms:
            # Fixes bug 2005. Mark 060702.
            env.history.message(cmd + "Selected atoms cannot have their display mode set to Surface.")
            return #ninad 061003 fixed bug 2286
        self.setDisplay(diSURFACE)

    def setDisplay(self, form, default_display=False):
        '''Set the display of the selection to 'form'.  If nothing is selected, then change
        the GLPane's current display to 'form'.
        '''
        if self.assy and self.assy.selatoms:
            for ob in self.assy.selatoms.itervalues():
                ob.setDisplay(form)
        elif self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.setDisplay(form)
        else:
            if self.glpane.displayMode == form:
                pass ## was 'return' # no change needed
                # bruce 041129 removing this optim, tho correct in theory,
                # since it's not expensive to changeapp and repaint if user
                # hits a button, so it's more important to fix any bugs that
                # might be in other code failing to call changeapp when needed.
            self.glpane.setDisplay(form, default_display) # See docstring for info about default_display
        self.win_update() # bruce 041206, needed for model tree display mode icons
        ## was self.glpane.paintGL() [but now would be self.glpane.gl_update]

    # set the color of the selected molecule
    # atom colors cannot be changed singly
    def dispObjectColor(self, currentcolor = None):
        if not self.assy.selmols: 
            env.history.message(redmsg("Set Chunk Color: No chunks selected.")) #bruce 050505 added this message
            return
	if not currentcolor:
	    c = QColorDialog.getColor(Qt.white, self)
	else:
	    c = QColorDialog.getColor(currentcolor, self)
	    
        if c.isValid():
            molcolor = c.red()/255.0, c.green()/255.0, c.blue()/255.0
	    list = []
            for ob in self.assy.selmols:
                ob.setcolor(molcolor)
		list.append(ob)
		
	    #Ninad 070321: Since the chunk is selected as a colored selection, 
	    #it should be unpicked after changing its color. 
	    #The user has most likely selected the chunk to change its color 
	    #and won't like it still shown 'green'(the selection color) 
	    #even after changing the color. so deselect it. 	
	    # The chunk is NOT unpicked IF the color is changed via chunk property
	    #dialog. see ChunkProp.change_chunk_color for details. This is intentional.
	    
	    for ob in list: 		
		ob.unpick()
	    
	    self.win_update()
            #self.glpane.gl_update()
    

    def dispResetChunkColor(self):
        "Resets the selected chunk's atom colors to the current element colors"
        if not self.assy.selmols: 
            env.history.message(redmsg("Reset Chunk Color: No chunks selected."))
            return
        
        for chunk in self.assy.selmols:
            chunk.setcolor(None)
        self.glpane.gl_update()
        
    def dispResetAtomsDisplay(self):
        "Resets the display setting for each atom in the selected chunks or atoms to Default display mode"
        
        cmd = greenmsg("Reset Atoms Display: ")
        msg = "No atoms or chunks selected."
        
        if self.assy.selmols: 
            self.assy.resetAtomsDisplay()
            msg = "Display setting for all atoms in selected chunk(s) reset to Default (i.e. their parent chunk's display mode)."
        
        if self.disp_not_default_in_selected_atoms():
            for a in self.assy.selatoms.itervalues(): #bruce 060707 itervalues
                if a.display != diDEFAULT:
                    a.setDisplay(diDEFAULT)
                    
            msg = "Display setting for all selected atom(s) reset to Default (i.e. their parent chunk's display mode)."
        
        env.history.message(cmd + msg)
        
    def dispShowInvisAtoms(self):
        "Resets the display setting for each invisible atom in the selected chunks or atoms to Default display mode"
        
        cmd = greenmsg("Show Invisible Atoms: ")
        
        if not self.assy.selmols and not self.assy.selatoms:
            msg = "No atoms or chunks selected."
            env.history.message(cmd + msg)
            return

        nia = 0 # nia = Number of Invisible Atoms
        
        if self.assy.selmols:
            nia = self.assy.showInvisibleAtoms()
        
        if self.disp_invis_in_selected_atoms():
            for a in self.assy.selatoms.itervalues(): #bruce 060707 itervalues
                if a.display == diINVISIBLE: 
                    a.setDisplay(diDEFAULT)
                    nia += 1
        
        msg = cmd + str(nia) + " invisible atoms found."
        env.history.message(msg)
    
    # The next two methods should be moved somewhere else (i.e. ops_select.py). Discuss with Bruce.
    def disp_not_default_in_selected_atoms(self): # Mark 060707.
        'Returns True if there is one or more selected atoms with its display mode not set to diDEFAULT.'
        for a in self.assy.selatoms.itervalues(): #bruce 060707 itervalues
                if a.display != diDEFAULT: 
                    return True
        return False
    
    def disp_invis_in_selected_atoms(self): # Mark 060707.
        'Returns True if there is one or more selected atoms with its display mode set to diINVISIBLE.'
        for a in self.assy.selatoms.itervalues(): #bruce 060707 itervalues
                if a.display == diINVISIBLE: 
                    return True
        return False
                    
    def dispBGColor(self):
        "Let user change the current mode's background color"
        # Fixed bug 894.  Mark
        # Changed "Background" to "General". Mark 060815.
        self.uprefs.showDialog(pagename='General')
    
    # pop up Element Color Selector dialog
    def dispElementColorSettings(self):
        "Slot for 'Display > Element Color Settings...' menu item."
        self.showElementColorSettings()
        
    def showElementColorSettings(self, parent=None):
        '''Opens the Element Color Setting dialog, allowing the user to change default 
        colors of elements and bondpoints, and save them to a file.
        '''
        global elementColorsWin
        #Huaicai 2/24/05: Create a new element selector window each time,  
        #so it will be easier to always start from the same states.
        # Make sure only a single element window is shown
        if elementColorsWin and elementColorsWin.isVisible(): 
                    return 
                    
        if not parent: # added parent arg to allow the caller (i.e. Preferences dialog) to make it modal.
            parent = self
        
        elementColorsWin = elementColors(parent)
        elementColorsWin.setDisplay(self.Element)
        # Sync the thumbview bg color with the current mode's bg color.  Mark 051216.
        elementColorsWin.elemGLPane.setBackgroundColor(
            self.glpane.backgroundColor, 
            self.glpane.backgroundGradient
            )
        elementColorsWin.show()

    def dispLighting(self):
        """Allows user to change lighting brightness.
        """
        self.uprefs.showDialog('Lighting') # Show Prefences | Lighting.
        
    ###############################################################
    # Select Toolbar Slots
    ###############################################################

    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        """
        env.history.message(greenmsg("Select All:"))
        self.assy.selectAll()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectNone(self):
        env.history.message(greenmsg("Select None:"))
        self.assy.selectNone()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectInvert(self):
        """If some parts are selected, select the other parts instead.
        If some atoms are selected, select the other atoms instead
        (even in chunks with no atoms selected, which end up with
        all atoms selected). (And unselect all currently selected
        parts or atoms.)
        """
        #env.history.message(greenmsg("Invert Selection:"))
        # assy method revised by bruce 041217 after discussion with Josh
        self.assy.selectInvert()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        Huaicai 1/19/05: This is called when user clicks the tool button,
        but when the user choose from pop up menu, only assy.selectConnected() called.
        I don't think this is good by any means, so I'll try to make them almost the same,
        but still keep this function. 
        """
        self.assy.selectConnected()

    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds. 
        Huaicai 1/19/05, see commets for the above method
        """
        self.assy.selectDoubly()

    def selectExpand(self):
        """Slot for Expand Selection, which selects any atom that is bonded 
        to any currently selected atom.
        """
        self.assy.selectExpand()
        
    def selectContract(self):
        """Slot for Contract Selection, which unselects any atom which has
        a bond to an unselected atom, or which has any open bonds.
        """
        self.assy.selectContract()
        
    ###################################
    # Jig Toolbar Slots
    ###################################

    def makeGamess(self):
        self.assy.makegamess()
        
    def makeAnchor(self): # Changed name from makeGround. Mark 051104.
        self.assy.makeAnchor()
        
    def makeStat(self):
        self.assy.makestat()

    def makeThermo(self):
        self.assy.makethermo()
        
    def makeMotor(self):
        self.assy.makeRotaryMotor(self.glpane.lineOfSight)

    def makeLinearMotor(self):
        self.assy.makeLinearMotor(self.glpane.lineOfSight)
	
    def createPlane(self):
	self.assy.createPlane()	
        
    def makeGridPlane(self):
        self.assy.makeGridPlane()

    def makeESPImage(self):
        self.assy.makeESPImage()
        
    def makeAtomSet(self):
        self.assy.makeAtomSet()
        
    def makeMeasureDistance(self):
        self.assy.makeMeasureDistance()
        
    def makeMeasureAngle(self):
        self.assy.makeMeasureAngle()
        
    def makeMeasureDihedral(self):
        self.assy.makeMeasureDihedral()
	

    ###################################
    # Modify Toolbar Slots
    ###################################
        
    def modifyAdjustSel(self):
        """Adjust the current selection"""
        if platform.atom_debug:
            print "debug: reloading runSim on each use, for development"
            import runSim, debug
            debug.reload_once_per_event(runSim)
        from runSim import Minimize_CommandRun
        cmdrun = Minimize_CommandRun( self, 'Sel', type = 'Adjust')
        cmdrun.run()
        return

    def modifyAdjustAll(self):
        """Adjust the entire (current) Part"""
        if platform.atom_debug:
            print "debug: reloading runSim on each use, for development"
            import runSim, debug
            debug.reload_once_per_event(runSim)
        from runSim import Minimize_CommandRun
        cmdrun = Minimize_CommandRun( self, 'All', type = 'Adjust')
        cmdrun.run()
        return
  
    def modifyHydrogenate(self):
        """ Add hydrogen atoms to each singlet in the selection """
        self.assy.modifyHydrogenate()
        
    # remove hydrogen atoms from selected atoms/molecules
    def modifyDehydrogenate(self):
        """ Remove all hydrogen atoms from the selection """
        self.assy.modifyDehydrogenate()
        
    def modifyPassivate(self):
        """ Passivate the selection by changing surface atoms to eliminate singlets """
        self.assy.modifyPassivate()
    
    def modifyDeleteBonds(self):
        """ Delete all bonds between selected and unselected atoms or chunks"""
        self.assy.modifyDeleteBonds()
            
    def modifyStretch(self):
        """ Stretch/expand the selected chunk(s) """
        self.assy.Stretch()
        
    def modifySeparate(self):
        """ Form a new chunk from the selected atoms """
        self.assy.modifySeparate()

    def modifyMerge(self):
        """ Create a single chunk from two of more selected chunks """
        self.assy.merge()
        self.win_update()
    
    def makeChunkFromAtom(self):
	''' Create a new chunk from the selected atoms'''
	self.assy.makeChunkFromAtoms()
	self.win_update()
	
	

    def modifyInvert(self):
        """ Invert the atoms of the selected chunk(s) """
        self.assy.Invert()
    
    def modifyMirror(self):
        "Mirrors the selected chunk about a jig with 0 atoms (mainly grid plane)"
        self.assy.Mirror()

    def modifyAlignCommonAxis(self):
        """ Align selected chunks to the computed axis of the first chunk by rotating them """
        self.assy.align()
        self.win_update()
        
    def modifyCenterCommonAxis(self):
        '''Same as "Align to Common Axis", except that it moves all the selected chunks to the 
        center of the first selected chunk after aligning/rotating the other chunks
        '''

        # This is still not fully implemented as intended.  Instead of moving all the selected 
        # chunks to the center of the first selected chunk, I want to have them moved to the closest 
        # (perpendicular) point of the first chunk's axis.  I've studied and understand the math involved; 
        # I just need to implement the code.  I plan to ask Bruce for help since the two of us will get it 
        # done much more quickly together than me doing it alone.
        # Mark 050829.

        self.assy.alignmove()
        self.win_update()
        
    ###################################
    # Help Toolbar Slots
    ###################################
    
    def helpMouseControls(self):
        self.help.showDialog(0)
        
    def helpKeyboardShortcuts(self):
        self.help.showDialog(1)
    
    def helpGraphicsCard(self):
        '''Displays details about the system\'s graphics card.
        '''
        ginfo = get_gl_info_string( self.glpane) #bruce 070308 added glpane arg
        
        from widgets import TextMessageBox
        msgbox = TextMessageBox(self)
        msgbox.setWindowTitle("Graphics Card Info")
        msgbox.setText(ginfo)
        msgbox.show()

# I modified a copy of cpuinfo.py from 
# http://cvs.sourceforge.net/viewcvs.py/numpy/Numeric3/scipy/distutils/
# thinking it might help us support users better if we had a built-in utility
# for interrogating the CPU.  I do not plan to commit cpuinfo.py until I speak
# to Bruce about this. Mark 051209.
# 
#    def helpCpuInfo(self):
#        '''Displays this system's CPU information.
#        '''
#        from cpuinfo import get_cpuinfo
#        cpuinfo = get_cpuinfo()
#        
#        from widgets import TextMessageBox
#        msgbox = TextMessageBox(self)
#        msgbox.setCaption("CPU Info")
#        msgbox.setText(cpuinfo)
#        msgbox.show()
              
    def helpAbout(self):
        """Displays information about this version of NanoEngineer-1
        """
        from version import Version
        v = Version()
        product = v.product
        versionString = repr(v) + (" (%s)" % v.releaseType)
        date = "Release Date: " + v.releaseDate
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
	if filePath.endswith('/Contents/Resources'):
            filePath = filePath[:-19]
        installdir = "Running from: " + filePath
        techsupport = "For technical support, send email to support@nanorex.com"
        website = "Website: www.nanoengineer-1.com"
        wiki = "Wiki: www.nanoengineer-1.net"
        aboutstr = product + " " + versionString \
                       + "\n\n" \
                       + date \
                       + "\n\n" \
                       + installdir \
                       + "\n\n" \
                       + v.copyright \
                       + "\n\n" \
                       + techsupport \
                       + "\n" \
                       + website \
                       + "\n" \
                       + wiki
                      
        QMessageBox.about ( self, "About NanoEngineer-1", aboutstr)
             
    def helpWhatsThis(self):
        from PyQt4.Qt import QWhatsThis ##bruce 050408
        QWhatsThis.enterWhatsThisMode ()


    ###################################
    # Modes Toolbar Slots
    ###################################

    # get into Select Atoms mode
    def toolsSelectAtoms(self): # note: this can NO LONGER be called from update_select_mode [as of bruce 060403]
        self.glpane.setMode('SELECTATOMS')

    # get into Select Chunks mode
    def toolsSelectMolecules(self):# note: this can also be called from update_select_mode [bruce 060403 comment]
        self.glpane.setMode('SELECTMOLS')

    # get into Move Chunks (or Translate Components) mode        
    def toolsMoveMolecule(self):
	if self.glpane.mode.modename == 'MODIFY':
	    self.glpane.mode.activate_moveGroupBox()		
	else:
	    self.glpane.setMode('MODIFY')
	
    #Rotate Components mode. 
    def toolsRotateComponents(self):
	if self.glpane.mode.modename == 'MODIFY':
	    self.glpane.mode.activate_rotateGroupBox()
	else:
	    self.glpane.setMode('MODIFY')
	    
	    
	
   
    # get into Build mode        
    def toolsBuildAtoms(self): # note: this can now be called from update_select_mode [as of bruce 060403]
        self.depositState = 'Atoms'
        self.glpane.setMode('DEPOSIT')
	
    #get into Build DNA Origami mode
    def buildDnaOrigami(self):
	''' Enter DNA Origami mode'''
	msg1 = greenmsg("DNA Origami: ")
	msg2 = " Not implemented yet"
	final_msg = msg1 + msg2
	env.history.message(final_msg)

    # get into cookiecutter mode
    def toolsCookieCut(self):
        self.glpane.setMode('COOKIE')

    # get into Extrude mode
    def toolsExtrude(self):
        self.glpane.setMode('EXTRUDE')

    # get into Fuse Chunks mode
    def toolsFuseChunks(self):
        self.glpane.setMode('FUSECHUNKS')
        
    ###################################
    # Simulator Toolbar Slots
    ###################################
    
    def simMinimizeEnergy(self):
        """Opens the Minimize Energy dialog.
        """
        self.minimize_energy.setup()
        
    def simSetup(self):
        """Creates a movie of a molecular dynamics simulation.
        """
        if platform.atom_debug: #bruce 060106 added this (fixing trivial bug 1260)
            print "atom_debug: reloading runSim on each use, for development"
            import runSim
            reload(runSim)
        from runSim import simSetup_CommandRun
        cmdrun = simSetup_CommandRun( self)
        cmdrun.run()
        return

    def simNanoHive(self):
        """Opens the Nano-Hive dialog... for details see subroutine's docstring.
        """
        # This should be probably be modeled after the simSetup_CommandRun class
        # I'll do this if Bruce agrees.  For now, I want to get this working ASAP.
        # Mark 050915.
        self.nanohive.showDialog(self.assy)

    def simPlot(self):
        """Opens the "Make Graphs" dialog if there is a "current" movie file
	(i.e. a movie file has been opened in the Movie Player).
	For details see subroutine's docstring.
        """
        from PlotTool import simPlot
        dialog = simPlot(self.assy) # Returns "None" if there is no current movie file. [mark 2007-05-03]
        if dialog:
            self.plotcntl = dialog #probably useless, but done since old code did it;
                # conceivably, keeping it matters due to its refcount. [bruce 050327]
		# matters now, since dialog can be None. [mark 2007-05-03]
        return
    
    def simMoviePlayer(self):
        """Plays a DPB movie file created by the simulator.
        """
        from movieMode import simMoviePlayer
        simMoviePlayer(self.assy)
        return

    def JobManager(self):
        """Opens the Job Manager dialog... for details see subroutine's docstring.
        """
        from JobManager import JobManager
        dialog = JobManager(self)
        if dialog:
            self.jobmgrcntl = dialog #probably useless, but done since old code did it;
                # conceivably, keeping it matters due to its refcount.  See Bruce's note in simPlot().
        return
    
    def serverManager(self):
        """Opens the server manager dialog. """
        from ServerManager import ServerManager
        ServerManager().showDialog()
        
    ###################################
    # Insert Menu/Toolbar Slots
    ###################################
        
    def insertGraphene(self):
	if self.glpane.mode.modename != 'SELECTMOLS':
	    self.glpane.setMode('SELECTMOLS')
        self.graphenecntl.show()

    def insertNanotube(self):
	if self.glpane.mode.modename != 'SELECTMOLS':
	    self.glpane.setMode('SELECTMOLS')
        self.nanotubecntl.show()

    def insertDna(self):
	if self.glpane.mode.modename != 'SELECTMOLS':
	    self.glpane.setMode('SELECTMOLS')
        self.dnacntl.show()
        
    def insertPovrayScene(self):
        self.povrayscenecntl.setup()
        
    def insertComment(self):
        '''Insert a new comment into the model tree.
        '''
        self.commentcntl.setup()

    #### Movie Player Dashboard Slots ############

    #bruce 050413 moved code for movie player dashboard slots into movieMode.py
    

    ###################################
    # Slots for future tools
    ###################################
    
    # get into Revolve mode [bruce 041015]
    def toolsRevolve(self):
        self.glpane.setMode('REVOLVE')
        
    # Mirror Tool
    def toolsMirror(self):
        env.history.message(redmsg("Mirror Tool: Not implemented yet."))
             
    # Mirror Circular Boundary Tool
    def toolsMirrorCircularBoundary(self):
        env.history.message(redmsg("Mirror Circular Boundary Tool: Not implemented yet."))

    ###################################
    # Slots for Dashboard widgets
    ###################################

    # fill the shape created in the cookiecutter with actual
    # carbon atoms in a diamond lattice (including bonds)
    # this works for all modes, not just add atom
    def toolsDone(self):
        self.glpane.mode.Done()

    def toolsStartOver(self):
        self.glpane.mode.Restart()

    def toolsBackUp(self):
        self.glpane.mode.Backup()

    def toolsCancel(self):
        self.glpane.mode.Flush()

   
    #######################################
    # Element Selector Slots
    #######################################
    def modifySetElement(self):
        '''Creates the Element Selector for Select Atoms mode.
        '''
        global elementSelectorWin
        #Huaicai 2/24/05: Create a new element selector window each time,  
        #so it will be easier to always start from the same states.
        # Make sure only a single element window is shown
        if elementSelectorWin and elementSelectorWin.isVisible():
            return 
        
        elementSelectorWin = elementSelector(self)
        elementSelectorWin.update_dialog(self.Element)
        elementSelectorWin.show()
    
    def update_depositState_buttons(self): #bruce 051230 moved this from depositMode to MWsemantics and removed the argument.
        '''Update the Build dashboard 'depositState' buttons based on self.depositState.
        '''
        depositState = self.depositState
            # (this is the only correct source of this info, so I made it not an argument;
            #  if that changes then we can supply an *optional* argument to get this info
            #  from a nonstandard source [bruce 051230])
        if depositState == 'Atoms':
            self.depositAtomDashboard.depositBtn.setChecked(True)
        elif depositState == 'Clipboard':
            self.depositAtomDashboard.pasteBtn.setChecked(True)
        elif depositState == 'Library':
            self.depositAtomDashboard.depositBtn.setChecked(False)
            self.depositAtomDashboard.pasteBtn.setChecked(False)
        else:
            print "Bug: depositState unknown: ", depositState, ".  depositState buttons unchanged." #bruce 051230 revised text
        return
    
    def modifyMMKit(self):
        '''Open The Molecular Modeling Kit for Build (DEPOSIT) mode.
        '''
        # This should probably be moved elsewhere
        global MMKitWin
        if MMKitWin and not MMKitWin.isHidden():
            return MMKitWin

        # It's very important to add the following condition, so only a single instance
        # of the MMKit has been created and used. This is to fix bug 934, which is kind
        # of hard to find. [Huaicai 9/2/05]
        firstShow = False
        if not MMKitWin:
            firstShow = True
            MMKitWin = MMKit(self)

        self.current_bondtool_button = None
        def bondtool_button_clicked(button, self=self):
            self.current_bondtool_button = button
            self.glpane.mode.update_cursor_for_no_MB_selection_filter_disabled()
	
	#ninad070412 disabled the following action. bondToolButtons attribute doesn't
	#exist in ne1qt4
        ##QObject.connect(MMKitWin.bondToolButtons, SIGNAL("buttonClicked(QAbstractButton *)"), bondtool_button_clicked)
        
        MMKitWin.update_dialog(self.Element)	
        return MMKitWin
        
    def hide_MMKit_during_open_or_save_on_MacOS(self): # added to fix bug 1744. mark 060324
        '''Returns True if the current platform is MacOS and the MMKit is shown.  
        Returns False if the current platform is not MacOS or if the MMKit is not shown.
        If the current platform is MacOS, the MMKit will be hidden if it is open and showing.
        '''
        if sys.platform == 'darwin':
            global MMKitWin
            if MMKitWin and MMKitWin.isVisible():
                MMKitWin.hide()
                return True
        return False

    def deleteMMKit(self):
        '''Deletes the MMKit.
        '''
        global MMKitWin
        if MMKitWin:
            MMKitWin.close()  # wware 060406 bug 1263 - don't leave MMKit open after exiting program
            MMKitWin = None
            self.depositState = 'Atoms' # reset so next time MMKit is created it will open to Atoms page

    def transmuteElementChanged(self, a0):
        '''Slot method, called when user changes the items in the <Transmute to> comboBox of selectAtom Dashboard.
           I put it here instead of the more relevant selectMode.py is because selectMode is not of 
           QObject, so it doesn't support signal/slots. --Huaicai '''
        self.glpane.mode.update_hybridComboBox(self)
            
        
    def elemChange(self, a0):
        '''Slot for Element selector combobox in Build mode's dashboard.
        '''
        self.Element = eCCBtab1[a0]
        
        try: #bruce 050606
            from depositMode import update_hybridComboBox
            update_hybridComboBox(self)
        except:
            if platform.atom_debug:
                print_compact_traceback( "atom_debug: ignoring exception from update_hybridComboBox: ")
            pass # might never fail, not sure...
        
        #[Huaicai 9/6/05: The element selector feature is obsolete.
        #global elementSelectorWin
        #if elementSelectorWin and not elementSelectorWin.isHidden():
        #   elementSelectorWin.update_dialog(self.Element)     
        #   elementSelectorWin.show()
        
        global MMKitWin
        if MMKitWin and not MMKitWin.isHidden():
           self.depositState = 'Atoms'
           MMKitWin.update_dialog(self.Element)     
           MMKitWin.show()


    # this routine sets the displays to reflect elt
    # [bruce 041215: most of this should be made a method in elementSelector.py #e]
    def setElement(self, elt):
        # element specified as element number
        global elementSelectorWin
        global MMKitWin
        
        self.Element = elt
        
        pw = self.activePartWindow()
        if pw is not None and pw.glpane.mode.modename == 'DEPOSIT':
            pw.glpane.mode.update_selection_filter_list() # depositMode.update_selection_filter_list()

        #Huaicai: These are redundant since the elemChange() will do all of them. 8/10/05
        #if elementSelectorWin: elementSelectorWin.update_dialog(elt)
        #if MMKitWin: MMKitWin.update_dialog(elt)
        
        line = eCCBtab2[elt]
        #self.elemChangeComboBox.setCurrentIndex(line) ###k does this send the signal, or not (if not that might cause bug 690)?
        #bruce 050706 fix bug 690 by calling the same slot that elemChangeComboBox.setCurrentIndex should have called
        # (not sure in principle that this is always safe or always a complete fix, but it seems to work)
        
        # Huaicai 8/10/05: remove the synchronization.
        #self.elemFilterComboBox.setCurrentIndex(line)
        
        self.elemChange(line) #k arg is a guess, but seems to work
            # (btw if you use keypress to change to the same element you're in, it *doesn't* reset that element
            #  to its default atomtype (hybridization combobox in build dashboard);
            #  this is due to a special case in update_hybridComboBox;
            #  I'm not sure whether this is good or bad. #k [bruce 050706])

        return
    

    def setCarbon(self):
        self.setElement(6) 

    def setHydrogen(self):
        self.setElement(1)
    
    def setOxygen(self):
        self.setElement(8)

    def setNitrogen(self):
        self.setElement(7)
	
	
    ######################################
    #Show View > Orientation Window     
    #######################################
    
    def showOrientationWindow(self): #Ninad 061121
	
	if not self.orientationWindow:
	    self.orientationWindow  = ViewOrientationWindow(self)
	    #self.orientationWindow.createOrientationViewList(namedViewList)
	    self.orientationWindow.createOrientationViewList()
	    self.viewOrientationAction.setChecked(True)
	    self.orientationWindow.setVisible(True)    	
	else:
	    if not self.orientationWindow.isVisible():
		self.orientationWindow.setVisible(True)
		self.viewOrientationAction.setChecked(True)
		
	return self.orientationWindow
    
    def deleteOrientationWindow(self):
	'''Delete the orientation window when the main window closes'''
	#ninad 061121 - this is probably unnecessary  
	if self.orientationWindow:
	    self.orientationWindow.close()
	    self.orientationWindow = None
	    
	return self.orientationWindow
            
    # key event handling revised by bruce 041220 to fix some bugs;
    # see comments in the GLPane methods.
    
    def keyPressEvent(self, e):
        self.glpane.keyPressEvent(e)
        
    def keyReleaseEvent(self, e):
        self.glpane.keyReleaseEvent(e)

    ##############################################################
    # Some future slot functions for the UI                      #
    ##############################################################

    def dispDatumLines(self):
        """ Toggle on/off datum lines """
        env.history.message(redmsg("Display Datum Lines: Not implemented yet."))

    def dispDatumPlanes(self):
        """ Toggle on/off datum planes """
        env.history.message(redmsg("Display Datum Planes: Not implemented yet."))

    def dispOpenBonds(self):
        """ Toggle on/off open bonds """
        env.history.message(redmsg("Display Open Bonds: Not implemented yet."))
             
    def validateThickness(self, s):
        if self.vd.validate( s, 0 )[0] != 2: self.ccLayerThicknessLineEdit.setText(s[:-1])

    ####### Movie Player slots ######################################

    # This is a temporary home for a single slot. This will need to be moved to
    # movieMode when I decide to create do_what_MainWindowUI_should_do().
    # NFR requested by Damian. Mark 060927.

    def updateSkipSuffix(self, val): # mark 060927 wrote this & bruce split it into two functions.
        """Update the suffix of the skip spinbox on the Movie Player dashboard"""
        from platform import th_st_nd_rd
        suffix = "%s frame" % th_st_nd_rd(val)
        self.skipSB.setSuffix(suffix)

#######  Load IconSets #########################################
    def load_icons_to_iconsets(self):
        '''Load additional icons to QAction icon sets that are used in MainWindow toolbars and menus.
        This is experimental. mark 060427.
        '''
    
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        small_disabled_on_icon_fname = filePath + "/../images/redoAction_small_disabled_off.png"
        
        # Add the small "disabled/off" icon for the Redo QAction, displayed when editRedoAction.setDisabled(1).
        editRedoIconSet = self.editRedoAction.iconSet()
        editRedoIconSet.setPixmap ( small_disabled_on_icon_fname, QIcon.Small, QIcon.Disabled, QIcon.Off )
        self.editRedoAction.setIcon ( editRedoIconSet )
    
    def hideDashboards(self):
        # [bruce 050408 comment: this list should be recoded somehow so that it
        #  lists what to show, not what to hide. ##e]
        self.cookieCutterDashboard.hide()
        #self.extrudeDashboard.hide()
	#self.revolveDashboard.hide()
        self.depositAtomDashboard.hide()
        self.selectMolDashboard.hide()
        self.selectAtomsDashboard.hide()
        self.moveChunksDashboard.hide()
        self.moviePlayerDashboard.hide()
        self.zoomDashboard.hide()
        self.panDashboard.hide()
        self.rotateDashboard.hide()
        self.fuseChunksDashboard.hide()
        self.cookieSelectDashboard.hide()
	
	##Huaicai 12/08/04, remove unnecessary toolbars from context menu
        objList = self.findChildren(QToolBar)
        for obj in objList:
            # [bruce 050408 comment: this is bad style; the default should be setAppropriate False
            #  (to keep most dashboard names out of the context menu in the toolbar area),
            #  and we should list here the few we want to include in that menu (setAppropriate True),
            #  not the many we want to exclude (which is also a list that changes more often). ##e]
	    """
            if obj in [self.moviePlayerDashboard, self.moveChunksDashboard,
                self.cookieCutterDashboard, self.depositAtomDashboard, self.extrudeDashboard,
                self.selectAtomsDashboard, self.selectMolDashboard, self.zoomDashboard,
                self.panDashboard, self.rotateDashboard, self.fuseChunksDashboard,
                self.cookieSelectDashboard]:
                    obj.setHidden(True)"""


            
    def enableViews(self, enableFlag=True):
        '''Disables/enables view actions on toolbar and menu.
        '''
        self.viewNormalToAction.setEnabled(enableFlag)
        self.viewParallelToAction.setEnabled(enableFlag)
        
        self.viewFrontAction.setEnabled(enableFlag)
        self.viewBackAction.setEnabled(enableFlag)
        self.viewTopAction.setEnabled(enableFlag)
        self.viewBottomAction.setEnabled(enableFlag)
        self.viewLeftAction.setEnabled(enableFlag)
        self.viewRightAction.setEnabled(enableFlag)
        self.viewIsometricAction.setEnabled(enableFlag)
        
        self.setViewHomeAction.setEnabled(enableFlag)
        self.setViewFitToWindowAction.setEnabled(enableFlag)
        self.setViewRecenterAction.setEnabled(enableFlag)
        
        self.viewRotate180Action.setEnabled(enableFlag)
        self.viewRotatePlus90Action.setEnabled(enableFlag)
        self.viewRotateMinus90Action.setEnabled(enableFlag)
    
    def disable_QActions_for_extrudeMode(self, disableFlag=True):
        '''Disables action items in the main window for extrudeMode.
        '''
        self.disable_QActions_for_movieMode(disableFlag)
        self.modifyHydrogenateAction.setEnabled(not disableFlag) # Fixes bug 1057. mark 060323
        self.modifyDehydrogenateAction.setEnabled(not disableFlag)
        self.modifyPassivateAction.setEnabled(not disableFlag)
        self.modifyDeleteBondsAction.setEnabled(not disableFlag)
        self.modifyStretchAction.setEnabled(not disableFlag)
        self.modifySeparateAction.setEnabled(not disableFlag)
        self.modifyMergeAction.setEnabled(not disableFlag)
        self.modifyInvertAction.setEnabled(not disableFlag)
	self.modifyMirrorAction.setEnabled(not disableFlag)
        self.modifyAlignCommonAxisAction.setEnabled(not disableFlag)
        # All QActions in the Modify menu/toolbar should be disabled, too. mark 060323
        
        
    def disable_QActions_for_sim(self, disableFlag=True):
        '''Disables actions items in the main window during simulations (and minimize).
        '''
        self.disable_QActions_for_movieMode(disableFlag)
        self.simMoviePlayerAction.setEnabled(not disableFlag)
        
    def disable_QActions_for_movieMode(self, disableFlag=True):
        '''Disables action items in the main window for movieMode.
        '''
        disable = not disableFlag
        self.modifyAdjustSelAction.setEnabled(disable) # "Adjust Selection"
        self.modifyAdjustAllAction.setEnabled(disable) # "Adjust All"
        self.simMinimizeEnergyAction.setEnabled(disable) # Minimize Energy 
        self.simSetupAction.setEnabled(disable) # "Simulator"
        self.fileSaveAction.setEnabled(disable) # "File Save"
        self.fileSaveAsAction.setEnabled(disable) # "File Save As"
        self.fileOpenAction.setEnabled(disable) # "File Open"
        self.fileCloseAction.setEnabled(disable) # "File Close"
        self.fileInsertAction.setEnabled(disable) # "File Insert"
        self.editDeleteAction.setEnabled(disable) # "Delete"
        
        # [bruce 050426 comment: I'm skeptical of disabling the ones marked #k 
        #  and suggest for some others (especially "simulator") that they
        #  auto-exit the mode rather than be disabled,
        #  but I won't revise these for now.]
        self.zoomToolAction.setEnabled(disable) # "Zoom Tool" [#k]
        self.panToolAction.setEnabled(disable) # "Pan Tool" [#k]
        self.rotateToolAction.setEnabled(disable) # "Rotate Tool" [#k]

# == Caption methods

    def update_mainwindow_caption_properly(self, junk = None): #bruce 050810 added this
        self.update_mainwindow_caption(self.assy.has_changed())

    def update_mainwindow_caption(self, Changed=False): #by mark; bruce 050810 revised this in several ways, fixed bug 785
        '''Update the caption at the top of the of the main window. 
        Example:  "NanoEngineer-1 - [partname.mmp]"
        Changed=True will add the prefix and suffix to the caption denoting the part has been changed.
        '''
        caption_prefix = env.prefs[captionPrefix_prefs_key]
        caption_suffix = env.prefs[captionSuffix_prefs_key]
        caption_fullpath = env.prefs[captionFullPath_prefs_key]
        
        if Changed:
            prefix = caption_prefix
            suffix = caption_suffix
        else:
            prefix = ''
            suffix = ''

        # this is not needed here since it's already done in the prefs values themselves when we set them:
        # if prefix and not prefix.endswith(" "):
        #     prefix = prefix + " "
        # if suffix and not suffix.startswith(" "):
        #     suffix = " " + suffix
        
        try:
            junk, basename = os.path.split(self.assy.filename)
            assert basename # it's normal for this to fail, when there is no file yet
            
            if caption_fullpath:
                partname = os.path.normpath(self.assy.filename)#fixed bug 453-1 ninad060721
            else:
                partname = basename
        
        except:
            partname = 'Untitled'

        ##e [bruce 050811 comment:] perhaps we should move prefix to the beginning, rather than just before "[";
        # and in any case the other stuff here, self.name() + " - " + "[" + "]", should also be user-changeable, IMHO.
	#print "****self.accessibleName *****=" , self.accessibleName()
	self.setWindowTitle(self.trUtf8("NanoEngineer-1" + " - " +prefix + "[" + partname + "]" + suffix))
	self.setWindowIcon(geticon("ui/border/MainWindow"))
        return
    
    pass # end of class MWsemantics

# end

