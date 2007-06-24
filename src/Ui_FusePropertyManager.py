# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_FusePropertyManager.py
@author: Ninad
@version: $Id$
@copyright:2004-2007 Nanorex, Inc.  All rights reserved.
"""

__author__ = "Ninad"

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.Qt import *
from Utility import geticon, getpixmap
from Ui_MovePropertyManager import Ui_MovePropertyManager
from PropertyManagerMixin import pmVBoxLayout, pmAddHeader, pmAddSponsorButton, \
     pmAddTopRowButtons, pmMessageGroupBox, pmAddBottomSpacer
from PropMgr_Constants import *

class Ui_FusePropertyManager(Ui_MovePropertyManager):
    def setupUi(self, FusePropertyManager):
        
        self.w = FusePropertyManager.w
        FusePropertyManager.setObjectName("FusePropertyManager")
	
	pmVBoxLayout(FusePropertyManager)
        pmAddHeader(FusePropertyManager)
	pmAddSponsorButton(FusePropertyManager)
        
        pmAddTopRowButtons(FusePropertyManager, 
			   showFlags = pmDoneButton | pmWhatsThisButton)
	
	self.MessageGroupBox = pmMessageGroupBox(self, title="Message")
	self.pmVBoxLayout.addWidget(self.MessageGroupBox)
	pmAddBottomSpacer(self.MessageGroupBox, self.pmVBoxLayout)
	
        self.ui_fuseOptions_groupBox(FusePropertyManager)
	pmAddBottomSpacer(self.fuseOptions_groupBox, self.pmVBoxLayout)
	
        self.ui_translate_groupBox(FusePropertyManager)
	pmAddBottomSpacer(self.translate_groupBox, self.pmVBoxLayout)
	
        self.ui_rotate_groupBox(FusePropertyManager)
	pmAddBottomSpacer(self.rotate_groupBox, self.pmVBoxLayout, last=True)
            
    def ui_fuseOptions_groupBox(self, FusePropertyManager):
        #Start Rotate Options        
        self.fuseOptions_groupBox = QtGui.QGroupBox(FusePropertyManager)
        self.fuseOptions_groupBox.setObjectName("fuseOptions_groupBox")    
        
        self.fuseOptions_groupBox.setAutoFillBackground(True)
        palette = FusePropertyManager.getGroupBoxPalette()
        self.fuseOptions_groupBox.setPalette(palette)
        
        styleSheet = FusePropertyManager.getGroupBoxStyleSheet()        
        self.fuseOptions_groupBox.setStyleSheet(styleSheet)
        
        vlo_fuseOptions_groupBox = QtGui.QVBoxLayout(self.fuseOptions_groupBox)
        vlo_fuseOptions_groupBox.setMargin(0)
        vlo_fuseOptions_groupBox.setSpacing(6)
              
        self.fuseOptions_groupBoxButton = FusePropertyManager.getGroupBoxTitleButton(
            "Fuse Options", self.fuseOptions_groupBox)        
        vlo_fuseOptions_groupBox.addWidget(self.fuseOptions_groupBoxButton)
        
        self.fuseOptions_widgetHolder = QtGui.QWidget(self.fuseOptions_groupBox)
                
        vlo_widgetHolder = QtGui.QVBoxLayout(self.fuseOptions_widgetHolder)
        vlo_widgetHolder.setMargin(2)
        vlo_widgetHolder.setSpacing(6)    
        
        self.fuse_mode_combox = QComboBox(self.fuseOptions_widgetHolder)
        self.fuse_mode_combox.insertItem(0,'Make Bonds Between Chunks') 
        self.fuse_mode_combox.insertItem(1,'Fuse Overlapping Atoms')
        vlo_widgetHolder.addWidget(self.fuse_mode_combox)
        
        self.goPB = QPushButton("Make Bonds",self.fuseOptions_widgetHolder)
	self.goPB.setAutoDefault(False)
        vlo_widgetHolder.addWidget(self.goPB)
        
        self.mergeCB = QCheckBox("Merge chunks", self.fuseOptions_widgetHolder)
        self.mergeCB.setChecked(True)
        vlo_widgetHolder.addWidget(self.mergeCB)
        
        self.tolLB = QLabel()
        self.tolLB.setText(" Tolerance:")
        vlo_widgetHolder.addWidget(self.tolLB)
    
        self.toleranceSL = QSlider(Qt.Horizontal)
        ##self.toleranceSL.setMaximumWidth(150)
        self.toleranceSL.setValue(100)
        self.toleranceSL.setRange(0, 300)
        vlo_widgetHolder.addWidget(self.toleranceSL)
        
        self.toleranceLB = QLabel()
        self.toleranceLB.setText("100% => 0 bondable pairs")
        vlo_widgetHolder.addWidget(self.toleranceLB)
        
        vlo_fuseOptions_groupBox.addWidget(self.fuseOptions_widgetHolder)
        self.pmVBoxLayout.addWidget(self.fuseOptions_groupBox)
        
        spacer_fuseops_grpbx = QtGui.QSpacerItem(
            10,10,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        
        self.pmVBoxLayout.addItem(spacer_fuseops_grpbx)