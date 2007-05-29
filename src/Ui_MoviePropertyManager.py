# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""


import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from Utility import geticon, imagename_to_pixmap, getpixmap

from NE1ToolBar import NE1ToolBar


#Note: Ui_MoviePlayerManager uses some Mainwindow widgets and actions 
#(This is because Movie PM uses most methods originally created for movie 
#dashboard and Movie dashboard defined them this way -- ninad 070507


class Ui_MoviePropertyManager(object):
    def setupUi(self, MoviePropertyManager):
        
        self.w = MoviePropertyManager.w
        
        MoviePropertyManager.setObjectName("MoviePropertyManager")
        MoviePropertyManager.resize(QtCore.QSize(QtCore.QRect(0,0,200,320).size()).expandedTo(
            MoviePropertyManager.minimumSizeHint()))    
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(3))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MoviePropertyManager.sizePolicy().hasHeightForWidth())
        MoviePropertyManager.setSizePolicy(sizePolicy)
        
        palette = MoviePropertyManager.getPropertyManagerPalette()
        MoviePropertyManager.setPalette(palette)
        
        self.vboxlayout = QtGui.QVBoxLayout(MoviePropertyManager)
        self.vboxlayout.setMargin(0) # was 1. Mark 2007-05-24.
        self.vboxlayout.setSpacing(0) # was 1. Mark 2007-05-24.
        self.vboxlayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.vboxlayout.setObjectName("vboxlayout")
        
        self.heading_frame = QtGui.QFrame(MoviePropertyManager)
        self.heading_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.heading_frame.setObjectName("heading_frame")
        
        palette2 = QtGui.QPalette()
        palette2.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(10),
                          QtGui.QColor(120,120,120)) #bgrole(10) is 'Windows'
        palette2.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(10),
                          QtGui.QColor(120,120,120)) #bgrole(10) is 'Windows'
        palette2.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(10),
                          QtGui.QColor(120,120,120)) #bgrole(10) is 'Windows'
        self.heading_frame.setAutoFillBackground(True)
        self.heading_frame.setPalette(palette2)

        self.hboxlayout_heading = QtGui.QHBoxLayout(self.heading_frame)
        self.hboxlayout_heading .setMargin(2)
        self.hboxlayout_heading .setSpacing(5)
        self.hboxlayout_heading .setObjectName("hboxlayout")


        self.heading_pixmap = QtGui.QLabel(self.heading_frame)
        self.heading_pixmap.setPixmap(getpixmap('ui/actions/Simulation/Play_Movie.png'))
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.heading_pixmap.sizePolicy().hasHeightForWidth())
        self.heading_pixmap.setSizePolicy(sizePolicy)
        #self.heading_pixmap.setScaledContents(True)
        self.heading_pixmap.setObjectName("heading_pixmap")
        
        self.hboxlayout_heading .addWidget(self.heading_pixmap)
        
        self.heading_label = QtGui.QLabel(self.heading_frame)

        font = QtGui.QFont(self.heading_label.font())
        font.setFamily("Sans Serif")
        font.setPointSize(12)
        font.setWeight(100)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(True)
        self.heading_label.setFont(font)
        self.heading_label.setObjectName("heading_label")
        
        
        self.hboxlayout_heading .addWidget(self.heading_label)
        
        self.vboxlayout.addWidget(self.heading_frame)

        self.sponsor_frame = QtGui.QFrame(MoviePropertyManager)
        self.sponsor_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.sponsor_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.sponsor_frame.setObjectName("sponsor_frame")

        self.gridlayout_sponsor = QtGui.QGridLayout(self.sponsor_frame)
        self.gridlayout_sponsor.setMargin(0)
        self.gridlayout_sponsor.setSpacing(0)
        self.gridlayout_sponsor.setObjectName("gridlayout")

        self.sponsor_btn = QtGui.QPushButton(self.sponsor_frame)
        self.sponsor_btn.setAutoDefault(False)
        self.sponsor_btn.setFlat(True)
        self.sponsor_btn.setObjectName("sponsor_btn")
        self.gridlayout_sponsor.addWidget(self.sponsor_btn,0,0,1,1)
        
        self.vboxlayout.addWidget(self.sponsor_frame)
        
        self.ui_doneCancelButtonRow(MoviePropertyManager)
        self.ui_movieControlsGroupBox(MoviePropertyManager) 
        self.ui_movieOptionsGroupBox(MoviePropertyManager)    
	self.ui_movieFilesGroupBox(MoviePropertyManager) 
            
                
        #ninad 0700202 its  important to add this spacerItem in the main vboxlayout to prevent the size adjustments in 
        #the property manager when the group items are hidden 
        spacerItem4 = QtGui.QSpacerItem(20,1,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem4)
        
        # This should be called last since it only works if all the widgets
	# for this Property Manager are added first. Mark 2007-05-29
        from PropMgrBaseClass import fitPropMgrToContents
	fitPropMgrToContents(MoviePropertyManager)
	
    def ui_doneCancelButtonRow(self, MoviePropertyManager):
        #Start Done , Abort, button row        
        hboxlayout_buttonrow = QtGui.QHBoxLayout()
        
        leftSpacer = QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Expanding, QSizePolicy.Minimum)
        hboxlayout_buttonrow.addItem(leftSpacer)        
                        
        self.button_frame = QtGui.QFrame(MoviePropertyManager)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_frame.sizePolicy().hasHeightForWidth())
        self.button_frame.setSizePolicy(sizePolicy)
        self.button_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.button_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.button_frame.setObjectName("button_frame")
        
        self.hboxlayout_buttonframe = QtGui.QHBoxLayout(self.button_frame)
        self.hboxlayout_buttonframe.setMargin(2)
        self.hboxlayout_buttonframe.setSpacing(2)
        self.hboxlayout_buttonframe.setObjectName("hboxlayout_buttonframe")
                
        self.done_btn = QtGui.QPushButton(self.button_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.done_btn.sizePolicy().hasHeightForWidth())
        self.done_btn.setSizePolicy(sizePolicy)

        self.done_btn.setIcon(geticon("ui/actions/Properties Manager/Done.png"))
        self.done_btn.setObjectName("done_btn")        
        
        self.hboxlayout_buttonframe.addWidget(self.done_btn)        
        
        self.abort_btn = QtGui.QPushButton(self.button_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.abort_btn.sizePolicy().hasHeightForWidth())
        self.abort_btn.setSizePolicy(sizePolicy)
        self.abort_btn.setIcon(geticon("ui/actions/Properties Manager/Abort.png"))
        self.abort_btn.setObjectName("abort_btn")
        self.hboxlayout_buttonframe.addWidget(self.abort_btn)
        
        self.whatthis_btn = QtGui.QPushButton(self.button_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),
                                       QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.whatthis_btn.sizePolicy().hasHeightForWidth())
        self.whatthis_btn.setSizePolicy(sizePolicy)
        self.whatthis_btn.setIcon(geticon("ui/actions/Properties Manager/WhatsThis.png"))
        self.whatthis_btn.setObjectName("whatthis_btn")
        self.hboxlayout_buttonframe.addWidget(self.whatthis_btn)
        
        hboxlayout_buttonrow.addWidget(self.button_frame)
        
        rightSpacer = QtGui.QSpacerItem(40, 10, QtGui.QSizePolicy.Expanding, 
                                        QSizePolicy.Minimum)
        hboxlayout_buttonrow.addItem(rightSpacer)
    
        self.vboxlayout.addLayout(hboxlayout_buttonrow)        
        #End Done , Abort button row
    
    def ui_movieControlsGroupBox(self, MoviePropertyManager):
	#Start movieControls Groupbox
        self.movieControls_groupBox = QtGui.QGroupBox(MoviePropertyManager)
        self.movieControls_groupBox .setObjectName("movieControls_groupBox")
               
        self.movieControls_groupBox.setAutoFillBackground(True)
        palette = MoviePropertyManager.getGroupBoxPalette()
        self.movieControls_groupBox.setPalette(palette)
        
        styleSheet = MoviePropertyManager.getGroupBoxStyleSheet()        
        self.movieControls_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_movieControls_grpbox = QtGui.QVBoxLayout(self.movieControls_groupBox)
        self.vboxlayout_movieControls_grpbox.setMargin(0)
        self.vboxlayout_movieControls_grpbox.setSpacing(6)
        self.vboxlayout_movieControls_grpbox.setObjectName(
            "vboxlayout_movieControls_grpbox") 

        self.movieControls_groupBoxButton=MoviePropertyManager.getGroupBoxTitleButton(
            "Movie Controls", 
            self.movieControls_groupBox)
        
        self.vboxlayout_movieControls_grpbox.addWidget(self.movieControls_groupBoxButton) 
        
        
        self.movieControlsGroupBox_widgetHolder = QtGui.QWidget(
            self.movieControls_groupBox)
        self.vboxlayout_movieControls_grpbox.addWidget(
            self.movieControlsGroupBox_widgetHolder)
        
        
        vlo_widgetholder = QtGui.QVBoxLayout(
            self.movieControlsGroupBox_widgetHolder)
        vlo_widgetholder.setMargin(4)
        vlo_widgetholder.setSpacing(6)
	
	#Movie Slider
	self.w.frameNumberSL = QSlider()
	self.w.frameNumberSL.setMaximum(999999)
	self.w.frameNumberSL.setOrientation(QtCore.Qt.Horizontal)
	
	vlo_widgetholder.addWidget(self.w.frameNumberSL)
	
	#Movie Frame Update Label
	
	hlo_movieFrameUpdate = QtGui.QHBoxLayout()
	
	spacer1_movieUpdateLabelRow = QtGui.QSpacerItem(
            5,
            10,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
	hlo_movieFrameUpdate.addItem(spacer1_movieUpdateLabelRow)
	
	self.w.movieFrameUpdateLabel = QtGui.QLabel("")
	
	hlo_movieFrameUpdate.addWidget(self.w.movieFrameUpdateLabel)
	spacer2_movieUpdateLabelRow = QtGui.QSpacerItem(
            5,
            10,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
	hlo_movieFrameUpdate.addItem(spacer2_movieUpdateLabelRow)
	
	vlo_widgetholder.addLayout(hlo_movieFrameUpdate)
	
        #Movie Controls
       	
        self.movieButtonsToolBar = NE1ToolBar(
            self.movieControlsGroupBox_widgetHolder)
	     
	
        movieActionList = [self.w.movieResetAction,
                           self.w.moviePlayRevActiveAction,
                           self.w.moviePlayRevAction,
                           self.w.moviePauseAction,
                           self.w.moviePlayAction,
                           self.w.moviePlayActiveAction,
                           self.w.movieMoveToEndAction
                           ]
        
        for action in movieActionList:
	    self.movieButtonsToolBar.addAction(action)
        	
	self.w.moviePlayActiveAction.setVisible(0)
        self.w.moviePlayRevActiveAction.setVisible(0)
		
    
        vlo_widgetholder.addWidget(self.movieButtonsToolBar)
	
	self.vboxlayout.addWidget(self.movieControls_groupBox)
	
	spacer_movieControls_grpbx = QtGui.QSpacerItem(
            10,
            10,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        
        self.vboxlayout.addItem(spacer_movieControls_grpbx) 
	
    def ui_movieFilesGroupBox(self, MoviePropertyManager):
	
	#Start movieFiles Groupbox
        self.movieFiles_groupBox = QtGui.QGroupBox(MoviePropertyManager)
        self.movieFiles_groupBox .setObjectName("movieFiles_groupBox")
               
        self.movieFiles_groupBox.setAutoFillBackground(True)
        palette = MoviePropertyManager.getGroupBoxPalette()
        self.movieFiles_groupBox.setPalette(palette)
        
        styleSheet = MoviePropertyManager.getGroupBoxStyleSheet()        
        self.movieFiles_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_movieFiles_grpbox = QtGui.QVBoxLayout(self.movieFiles_groupBox)
        self.vboxlayout_movieFiles_grpbox.setMargin(0)
        self.vboxlayout_movieFiles_grpbox.setSpacing(6)
        self.vboxlayout_movieFiles_grpbox.setObjectName(
            "vboxlayout_movieFiles_grpbox") 

        self.movieFiles_groupBoxButton=MoviePropertyManager.getGroupBoxTitleButton(
            "Open/Save Movie Options", 
            self.movieFiles_groupBox)
        
        self.vboxlayout_movieFiles_grpbox.addWidget(self.movieFiles_groupBoxButton) 
        
        
        self.movieFilesGroupBox_widgetHolder = QtGui.QWidget(
            self.movieFiles_groupBox)
        self.vboxlayout_movieFiles_grpbox.addWidget(
            self.movieFilesGroupBox_widgetHolder)
        
        
        vlo_widgetholder = QtGui.QVBoxLayout(
            self.movieFilesGroupBox_widgetHolder)
        vlo_widgetholder.setMargin(10)
        vlo_widgetholder.setSpacing(6)
	

	
	for action in self.w.fileOpenMovieAction, self.w.fileSaveMovieAction:
	    btn = QtGui.QToolButton()
	    btn.setDefaultAction(action)
	    btn.setAutoRaise(True)
	    btn.setText(action.text())
	    btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
	    vlo_widgetholder.addWidget(btn)	
		        
        #End movieFiles Options
        self.vboxlayout.addWidget(self.movieFiles_groupBox)
        spacer_movieFiles_grpbx = QtGui.QSpacerItem(
            10,
            10,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        
        self.vboxlayout.addItem(spacer_movieFiles_grpbx)  
	
	pass
    
    
    def ui_movieOptionsGroupBox(self, MoviePropertyManager):
        #Start movieOptions Groupbox
        self.movieOptions_groupBox = QtGui.QGroupBox(MoviePropertyManager)
        self.movieOptions_groupBox .setObjectName("movieOptions_groupBox")
               
        self.movieOptions_groupBox.setAutoFillBackground(True)
        palette = MoviePropertyManager.getGroupBoxPalette()
        self.movieOptions_groupBox.setPalette(palette)
        
        styleSheet = MoviePropertyManager.getGroupBoxStyleSheet()        
        self.movieOptions_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_movieOptions_grpbox = QtGui.QVBoxLayout(self.movieOptions_groupBox)
        self.vboxlayout_movieOptions_grpbox.setMargin(0)
        self.vboxlayout_movieOptions_grpbox.setSpacing(6)
        self.vboxlayout_movieOptions_grpbox.setObjectName(
            "vboxlayout_movieOptions_grpbox") 

        self.movieOptions_groupBoxButton=MoviePropertyManager.getGroupBoxTitleButton(
            "Movie Options", 
            self.movieOptions_groupBox)
        
        self.vboxlayout_movieOptions_grpbox.addWidget(self.movieOptions_groupBoxButton) 
        
        
        self.movieOptionsGroupBox_widgetHolder = QtGui.QWidget(
            self.movieOptions_groupBox)
        self.vboxlayout_movieOptions_grpbox.addWidget(
            self.movieOptionsGroupBox_widgetHolder)
        
        
        vlo_widgetholder = QtGui.QVBoxLayout(
            self.movieOptionsGroupBox_widgetHolder)
        vlo_widgetholder.setMargin(4)
        vlo_widgetholder.setSpacing(6)
	
	self.w.movieLoop_checkbox = QtGui.QCheckBox("Loop")    
        self.w.movieLoop_checkbox.setObjectName("movieLoop_checkbox")
	vlo_widgetholder.addWidget(self.w.movieLoop_checkbox)
	
	
	hlo_frameNumber = QtGui.QHBoxLayout()
	
	#@@@ninad20070507 self.w.frameLabel was used by old movie dashboard. 
	#it's references need to be  removed . Just define it here 
	#for now to get rid of those errors. Its not used in ui anywhere
	
	self.w.frameLabel = QtGui.QLabel()
        
	
	self.frameLabel = QtGui.QLabel("Go to:")
	self.frameLabel.setAlignment(Qt.AlignRight|Qt.AlignCenter)
	self.frameLabel.setObjectName("frameLabel")
	hlo_frameNumber.addWidget(self.frameLabel)
    
	self.w.frameNumberSB = QtGui.QSpinBox()
	

	font = QtGui.QFont(self.w.frameNumberSB.font())
	font.setFamily("Sans Serif")
	font.setPointSize(9)
	font.setWeight(75)
	font.setItalic(False)
	font.setUnderline(False)
	font.setStrikeOut(False)
	font.setBold(True)
	self.w.frameNumberSB.setFont(font)
	self.w.frameNumberSB.setMaximum(999999)
	self.w.frameNumberSB.setObjectName("frameNumberSB")
	
	hlo_frameNumber.addWidget(self.w.frameNumberSB)
	
	spacer_frameNumber = QtGui.QSpacerItem(
            10,
            10,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
	
	hlo_frameNumber.addItem(spacer_frameNumber)
	
	vlo_widgetholder.addLayout(hlo_frameNumber)
	
	
	hlo_skip = QtGui.QHBoxLayout()
	self.w.skipTL = QtGui.QLabel("Skip: ")
	self.w.skipTL.setAlignment(Qt.AlignRight)
	self.w.skipTL.setObjectName("skipTL")
	hlo_skip.addWidget(self.w.skipTL)
	
	self.w.skipSB = QtGui.QSpinBox()
	self.w.skipSB.setObjectName("skipSB")
	self.w.skipSB.setRange(1,9999)
	self.w.skipSB.setMaximum(999999)
	
	font = QtGui.QFont(self.w.skipSB.font())
	font.setFamily("Sans Serif")
	font.setPointSize(9)
	font.setWeight(75)
	font.setItalic(False)
	font.setUnderline(False)
	font.setStrikeOut(False)
	font.setBold(True)
	self.w.skipSB.setFont(font)
		
	hlo_skip.addWidget(self.w.skipSB)
	
	spacer_skip = QtGui.QSpacerItem(
            10,
            10,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
	
	hlo_skip.addItem(spacer_skip)
	
	vlo_widgetholder.addLayout(hlo_skip)

		        
        #End movieOptions Options
        self.vboxlayout.addWidget(self.movieOptions_groupBox)
        spacer_movieOptions_grpbx = QtGui.QSpacerItem(
            10,
            10,
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)
        
        self.vboxlayout.addItem(spacer_movieOptions_grpbx)       
    
        
    def retranslateUi(self, MoviePropertyManager):
        MoviePropertyManager.setWindowTitle(QtGui.QApplication.translate("MoviePropertyManager", 
                                                                        "MoviePropertyManager",
                                                                        None, QtGui.QApplication.UnicodeUTF8))
        self.heading_label.setText(QtGui.QApplication.translate("MoviePropertyManager", 
                                                                "<font color=\"#FFFFFF\">Movie</font>", 
                                                                None, QtGui.QApplication.UnicodeUTF8))
        