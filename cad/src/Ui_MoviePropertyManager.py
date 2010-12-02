# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""


import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QLayout
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QSize
from PyQt4.Qt import QSlider
from PyQt4.Qt import Qt

from Utility import geticon, imagename_to_pixmap, getpixmap
from NE1ToolBar import NE1ToolBar

from PropertyManagerMixin import pmVBoxLayout
from PropertyManagerMixin import pmAddHeader
from PropertyManagerMixin import pmAddSponsorButton
from PropertyManagerMixin import pmAddTopRowButtons
from PropertyManagerMixin import pmMessageGroupBox
from PropertyManagerMixin import pmAddBottomSpacer

from PropMgr_Constants import getHeaderFont
from PropMgr_Constants import pmLabelLeftAlignment
from PropMgr_Constants import pmTopRowBtnsMargin
from PropMgr_Constants import pmTopRowBtnsSpacing
from PropMgr_Constants import pmCancelButton
from PropMgr_Constants import pmDoneButton
from PropMgr_Constants import pmWhatsThisButton

#Note: Ui_MoviePlayerManager uses some Mainwindow widgets and actions 
#(This is because Movie PM uses most methods originally created for movie 
#dashboard and Movie dashboard defined them this way -- ninad 070507


class Ui_MoviePropertyManager(object):
    def setupUi(self, MoviePropertyManager):
        
        self.w = MoviePropertyManager.w
        
        MoviePropertyManager.setObjectName("MoviePropertyManager")
        
        pmVBoxLayout(MoviePropertyManager)
        pmAddHeader(MoviePropertyManager)
	pmAddSponsorButton(MoviePropertyManager)
	
        pmAddTopRowButtons(MoviePropertyManager, 
			   showFlags = 
			   pmDoneButton | 
			   pmCancelButton | 
			   pmWhatsThisButton)
        
	self.message_groupBox = pmMessageGroupBox(self, title="Message")
	self.pmVBoxLayout.addWidget(self.message_groupBox)
	pmAddBottomSpacer(self.message_groupBox, self.pmVBoxLayout)
        
        self.ui_movieControls_groupBox(MoviePropertyManager)
	pmAddBottomSpacer(self.movieControls_groupBox, self.pmVBoxLayout)
        
        self.ui_movieOptions_groupBox(MoviePropertyManager)
	pmAddBottomSpacer(self.movieOptions_groupBox, self.pmVBoxLayout)
        
        self.ui_movieFiles_groupBox(MoviePropertyManager)
	pmAddBottomSpacer(self.movieFiles_groupBox, self.pmVBoxLayout, last=True)
    
    def ui_movieControls_groupBox(self, MoviePropertyManager):
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
        
        self.pmVBoxLayout.addWidget(self.movieControls_groupBox)
        
    def ui_movieFiles_groupBox(self, MoviePropertyManager):
        
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
        self.pmVBoxLayout.addWidget(self.movieFiles_groupBox)
        
        pass
    
    
    def ui_movieOptions_groupBox(self, MoviePropertyManager):
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
        self.pmVBoxLayout.addWidget(self.movieOptions_groupBox)     
