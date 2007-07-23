# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_FusePropertyManager.py
@author: Ninad
@version: $Id$
@copyright:2004-2007 Nanorex, Inc.  All rights reserved.
"""

__author__ = "Ninad"

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QLayout
from PyQt4.Qt import QComboBox
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QCheckBox
from PyQt4.Qt import QLabel
from PyQt4.Qt import QSlider
from PyQt4.Qt import Qt

from Utility import geticon, getpixmap

from PropertyManagerMixin import pmVBoxLayout
from PropertyManagerMixin import pmAddHeader
from PropertyManagerMixin import pmAddSponsorButton
from PropertyManagerMixin import pmAddTopRowButtons
from PropertyManagerMixin import pmMessageGroupBox
from PropertyManagerMixin import pmAddBottomSpacer

from PropMgr_Constants import getHeaderFont
from PropMgr_Constants import pmLabelLeftAlignment
from PropMgr_Constants import pmDoneButton
from PropMgr_Constants import pmWhatsThisButton

class Ui_FusePropertyManager(object):
    def setupUi(self, fusePropMgrObject):
        fusePropMgr = fusePropMgrObject
        fusePropMgr.setObjectName("fusePropMgr")
	pmVBoxLayout(fusePropMgr)	
        pmAddHeader(fusePropMgr)
	pmAddSponsorButton(fusePropMgr)        
        pmAddTopRowButtons(fusePropMgr, 
			   showFlags = pmDoneButton | pmWhatsThisButton)
	
	fusePropMgr.MessageGroupBox = pmMessageGroupBox(fusePropMgr,
							title = "Message",
							)
	fusePropMgr.pmVBoxLayout.addWidget(fusePropMgr.MessageGroupBox)
	pmAddBottomSpacer(fusePropMgr.MessageGroupBox, fusePropMgr.pmVBoxLayout)
	
        self.ui_fuseOptions_groupBox(fusePropMgr)
	pmAddBottomSpacer(fusePropMgr.fuseOptions_groupBox, 
			  fusePropMgr.pmVBoxLayout)
	
        fusePropMgr.ui_translate_groupBox(fusePropMgr)
	pmAddBottomSpacer(fusePropMgr.translate_groupBox, 
			  fusePropMgr.pmVBoxLayout)
	
        fusePropMgr.ui_rotate_groupBox(fusePropMgr)
	pmAddBottomSpacer(fusePropMgr.rotate_groupBox, 
			  fusePropMgr.pmVBoxLayout, 
			  last=True)
            
    def ui_fuseOptions_groupBox(self, fusePropMgrObject):
	
	#Start Fuse Options  
	fusePropMgr = fusePropMgrObject              
        fusePropMgr.fuseOptions_groupBox = QtGui.QGroupBox(fusePropMgr)
        fusePropMgr.fuseOptions_groupBox.setObjectName("fuseOptions_groupBox")    
        
        fusePropMgr.fuseOptions_groupBox.setAutoFillBackground(True)
        palette = fusePropMgr.getGroupBoxPalette()
        fusePropMgr.fuseOptions_groupBox.setPalette(palette)
        
        styleSheet = fusePropMgr.getGroupBoxStyleSheet()        
        fusePropMgr.fuseOptions_groupBox.setStyleSheet(styleSheet)
        
        vlo_fuseOptions_groupBox = QtGui.QVBoxLayout(
	    fusePropMgr.fuseOptions_groupBox)
        vlo_fuseOptions_groupBox.setMargin(0)
        vlo_fuseOptions_groupBox.setSpacing(6)
              
        fusePropMgr.fuseOptions_groupBoxButton = \
		   fusePropMgr.getGroupBoxTitleButton(
		       "Fuse Options", 
		       fusePropMgr.fuseOptions_groupBox)  
	
        vlo_fuseOptions_groupBox.addWidget(
	    fusePropMgr.fuseOptions_groupBoxButton)
        
        fusePropMgr.fuseOptions_widgetHolder = QtGui.QWidget(
	    fusePropMgr.fuseOptions_groupBox)
                
        vlo_widgetHolder = QtGui.QVBoxLayout(
	    fusePropMgr.fuseOptions_widgetHolder)
        vlo_widgetHolder.setMargin(2)
        vlo_widgetHolder.setSpacing(6)    
        
        fusePropMgr.fuse_mode_combox = QComboBox(
	    fusePropMgr.fuseOptions_widgetHolder)
        fusePropMgr.fuse_mode_combox.insertItem(0,'Make Bonds Between Chunks') 
        fusePropMgr.fuse_mode_combox.insertItem(1,'Fuse Overlapping Atoms')
        vlo_widgetHolder.addWidget(fusePropMgr.fuse_mode_combox)
        
        fusePropMgr.goPB = QPushButton("Make Bonds",
				       fusePropMgr.fuseOptions_widgetHolder)
	fusePropMgr.goPB.setAutoDefault(False)
        vlo_widgetHolder.addWidget(fusePropMgr.goPB)
        
        fusePropMgr.mergeCB = QCheckBox("Merge chunks", 
					fusePropMgr.fuseOptions_widgetHolder)
        fusePropMgr.mergeCB.setChecked(True)
        vlo_widgetHolder.addWidget(fusePropMgr.mergeCB)
        
        fusePropMgr.tolLB = QLabel()
        fusePropMgr.tolLB.setText(" Tolerance:")
        vlo_widgetHolder.addWidget(fusePropMgr.tolLB)
    
        fusePropMgr.toleranceSL = QSlider(Qt.Horizontal)
        ##fusePropMgr.toleranceSL.setMaximumWidth(150)
        fusePropMgr.toleranceSL.setValue(100)
        fusePropMgr.toleranceSL.setRange(0, 300)
        vlo_widgetHolder.addWidget(fusePropMgr.toleranceSL)
        
        fusePropMgr.toleranceLB = QLabel()
        fusePropMgr.toleranceLB.setText("100% => 0 bondable pairs")
        vlo_widgetHolder.addWidget(fusePropMgr.toleranceLB)
        
        vlo_fuseOptions_groupBox.addWidget(fusePropMgr.fuseOptions_widgetHolder)
        fusePropMgr.pmVBoxLayout.addWidget(fusePropMgr.fuseOptions_groupBox)
        