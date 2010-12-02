# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_CookiePropertyManager.py

$Id$


UI file for Cookie Property Manager. e.g. UI for groupboxes 
(and its contents), button rows etc. 

History:

- These options appeared in cookie cutter dashboard till Alpha8

- Post Alpha8 (sometime after 12/2006), the options were included 
in the Cookie Property Manager. 

- In Alpha 9 , 'Cookie Cutter' was renamed to 'Build Crystal'


"""
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QSize
from PyQt4.Qt import QButtonGroup
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QSpinBox
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QLineEdit
from PyQt4.Qt import QLayout
from PyQt4.Qt import QLabel
from PyQt4.Qt import QComboBox
from PyQt4.Qt import QCheckBox

from Utility import geticon, getpixmap

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

__author__ = "Ninad"

class Ui_CookiePropertyManager(object):
    def setupUi(self, CookiePropertyManager):
        CookiePropertyManager.setObjectName("CookiePropertyManager")
	
	pmVBoxLayout(CookiePropertyManager)
        pmAddHeader(CookiePropertyManager)
	pmAddSponsorButton(CookiePropertyManager)
        
	pmAddTopRowButtons(CookiePropertyManager, 
			   showFlags = 
			   pmDoneButton | 
			   pmCancelButton | 
			   pmWhatsThisButton)
	
	self.MessageGroupBox = pmMessageGroupBox(self, title="Message")
	self.pmVBoxLayout.addWidget(self.MessageGroupBox)
	pmAddBottomSpacer(self.MessageGroupBox, self.pmVBoxLayout)
        
        self.ui_cookieSpec_groupBox(CookiePropertyManager)
	pmAddBottomSpacer(self.cookieSpec_groupBox, self.pmVBoxLayout)
        
        self.ui_layerProperties_groupBox(CookiePropertyManager)
        pmAddBottomSpacer(self.layerProperties_groupBox, self.pmVBoxLayout)
	
        self.ui_displayOptions_groupBox(CookiePropertyManager)
        pmAddBottomSpacer(self.displayOptions_groupBox, self.pmVBoxLayout)
	
        self.ui_advancedOptions_groupBox(CookiePropertyManager)
	pmAddBottomSpacer(self.advancedOptions_groupBox, self.pmVBoxLayout, last=True)
        
        self.retranslateUi(CookiePropertyManager)
        QtCore.QMetaObject.connectSlotsByName(CookiePropertyManager)
    
    def ui_cookieSpec_groupBox(self, CookiePropertyManager):
        
        # Start Cookie Specifications Groupbox
        self.cookieSpec_groupBox = QtGui.QGroupBox(CookiePropertyManager)
        self.cookieSpec_groupBox.setObjectName("cookieSpec_groupBox")
        
        self.cookieSpec_groupBox.setAutoFillBackground(True) 
        palette =  CookiePropertyManager.getGroupBoxPalette()
        self.cookieSpec_groupBox.setPalette(palette)
        
        styleSheet = CookiePropertyManager.getGroupBoxStyleSheet()        
        self.cookieSpec_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_grpbox1 = QtGui.QVBoxLayout(self.cookieSpec_groupBox)
        self.vboxlayout_grpbox1.setMargin(0)
        self.vboxlayout_grpbox1.setSpacing(6)
        self.vboxlayout_grpbox1.setObjectName("vboxlayout_grpbox1")
        
        
        self.cookieSpec_groupBoxButton = CookiePropertyManager.getGroupBoxTitleButton(
            "Crystal Specifications", self.cookieSpec_groupBox)
        
        self.vboxlayout_grpbox1.addWidget(self.cookieSpec_groupBoxButton)

        
        self.hboxlayout2_grpbox1 = QtGui.QHBoxLayout()
        self.hboxlayout2_grpbox1.setMargin(0)
        self.hboxlayout2_grpbox1.setSpacing(6)
        self.hboxlayout2_grpbox1.setObjectName("hboxlayout2_grpbox1")
        
        self.latticeLabel = QLabel("Lattice Type")
        
        self.hboxlayout2_grpbox1.addWidget(self.latticeLabel)
        
        self.latticeCBox = QComboBox(self.cookieSpec_groupBox)
        self.latticeCBox.insertItem(1, "Diamond")
        self.latticeCBox.insertItem(2, "Lonsdaleite")
        
        self.hboxlayout2_grpbox1.addWidget(self.latticeCBox)
        
        self.vboxlayout_grpbox1.addLayout(self.hboxlayout2_grpbox1)
        
        self.hboxlayout3_grpbox1 = QtGui.QHBoxLayout()
        self.hboxlayout3_grpbox1.setMargin(0)
        self.hboxlayout3_grpbox1.setSpacing(6)
        self.hboxlayout3_grpbox1.setObjectName("hboxlayout3_grpbox1")
        
            
        self.gridOrientation_label = QLabel(self.cookieSpec_groupBox)
        self.gridOrientation_label.setObjectName("self.gridOrientation_label")
        self.hboxlayout3_grpbox1.addWidget(self.gridOrientation_label)
        
        self.orientButtonGroup = QButtonGroup()
        
        self.surface100_btn = QToolButton(self.cookieSpec_groupBox)
        
        self.orientButtonGroup.addButton(self.surface100_btn, 0)    
        self.surface100_btn.setCheckable(1)
        self.surface100_btn.setChecked(0)
        self.surface100_btn.setAutoExclusive(1)
        self.surface100_btn.setAutoRaise(1)
        self.surface100_btn.setMinimumSize(QtCore.QSize(26,26))
        self.surface100_btn.index = 0
        self.surface100_btn.setIcon(geticon('ui/actions/Properties Manager/Surface100.png'))       
        self.surface100_btn.setIconSize(QtCore.QSize(22,22))       
        self.surface100_btn.setToolTip("Surface 100")
        self.hboxlayout3_grpbox1.addWidget(self.surface100_btn)
        
        self.surface110_btn = QToolButton(self.cookieSpec_groupBox)

        self.orientButtonGroup.addButton(self.surface110_btn, 1)
    
        self.surface110_btn.setCheckable(1)
        self.surface110_btn.setChecked(0)
        self.surface110_btn.setAutoExclusive(1)
        self.surface110_btn.setAutoRaise(1)
        self.surface110_btn.setMinimumSize(QtCore.QSize(26,26))
        self.surface110_btn.index = 1
        self.surface110_btn.setIcon(geticon('ui/actions/Properties Manager/Surface110.png'))
        self.surface110_btn.setIconSize(QtCore.QSize(22,22))       
        self.surface110_btn.setToolTip("Surface 110")
        self.hboxlayout3_grpbox1.addWidget(self.surface110_btn)
                        
        self.surface111_btn = QToolButton(self.cookieSpec_groupBox)
        
        self.orientButtonGroup.addButton(self.surface111_btn,2)        
        self.surface111_btn.setCheckable(1)
        self.surface111_btn.setChecked(0)
        self.surface111_btn.setAutoExclusive(1)
        self.surface111_btn.setAutoRaise(1)
        self.surface111_btn.setMinimumSize(QtCore.QSize(26,26))
        self.surface111_btn.setIconSize(QtCore.QSize(22,22))       
        self.surface111_btn.index = 2
        self.surface111_btn.setIcon(geticon('ui/actions/Properties Manager/Surface111.png'))
        self.surface111_btn.setToolTip("Surface 111")
        self.hboxlayout3_grpbox1.addWidget(self.surface111_btn)
        
        self.vboxlayout_grpbox1.addLayout(self.hboxlayout3_grpbox1)
        
        self.hboxlayout4_grpbox1 = QtGui.QHBoxLayout()
        self.hboxlayout4_grpbox1.setMargin(0)
        self.hboxlayout4_grpbox1.setSpacing(6)
        self.hboxlayout4_grpbox1.setObjectName("hboxlayout4_grpbox1")
        
        self.rotateGrid_label = QLabel(self.cookieSpec_groupBox)
        self.rotateGrid_label.setObjectName("self.rotateGrid_label")
        self.hboxlayout4_grpbox1.addWidget(self.rotateGrid_label)
        
        self.gridRotateAngle = QSpinBox(self.cookieSpec_groupBox)
        self.gridRotateAngle.setRange(0, 360)
        self.gridRotateAngle.setSingleStep(5)
        self.gridRotateAngle.setToolTip("Degrees to rotate")
        self.hboxlayout4_grpbox1.addWidget(self.gridRotateAngle)
        
        self.antiRotateButton = QToolButton(self.cookieSpec_groupBox)
        self.antiRotateButton.setIcon(geticon('ui/actions/Properties Manager/rotate_minus'))
        self.antiRotateButton.setIconSize(QtCore.QSize(22,22))       
        self.antiRotateButton.setToolTip("Rotate Anti-Clockwise")
        self.hboxlayout4_grpbox1.addWidget(self.antiRotateButton)
        
        self.rotateButton = QToolButton(self.cookieSpec_groupBox)
        self.rotateButton.setIcon(geticon('ui/actions/Properties Manager/rotate_plus'))
        self.rotateButton.setIconSize(QtCore.QSize(22,22))       
        self.rotateButton.setToolTip("Rotate Clockwise")
        self.hboxlayout4_grpbox1.addWidget(self.rotateButton)
        
        self.vboxlayout_grpbox1.addLayout(self.hboxlayout4_grpbox1)
        
        # End Cookie Specifications Groupbox
        self.pmVBoxLayout.addWidget(self.cookieSpec_groupBox)
    
    def ui_layerProperties_groupBox(self, CookiePropertyManager):
        
        #Start Layer Properties Groupbox
        self.layerProperties_groupBox = QtGui.QGroupBox(CookiePropertyManager)
        self.layerProperties_groupBox .setObjectName("layerProperties_groupBox")
        
        self.layerProperties_groupBox.setAutoFillBackground(True) 
        palette =  CookiePropertyManager.getGroupBoxPalette()
        self.layerProperties_groupBox.setPalette(palette)
        
        styleSheet = CookiePropertyManager.getGroupBoxStyleSheet()        
        self.layerProperties_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_layergrpbox = QtGui.QVBoxLayout(self.layerProperties_groupBox)
        self.vboxlayout_layergrpbox.setMargin(0)
        self.vboxlayout_layergrpbox.setSpacing(6)
        self.vboxlayout_layergrpbox.setSizeConstraint(QLayout.SetMinimumSize)
        self.vboxlayout_layergrpbox.setObjectName("vboxlayout_layergrpbox")

        self.layerProperties_groupBoxButton = CookiePropertyManager.getGroupBoxTitleButton(
            "Layer Properties",self.layerProperties_groupBox)
        self.vboxlayout_layergrpbox.addWidget(self.layerProperties_groupBoxButton)
  
        self.hboxlayout2_layergrpbox = QtGui.QHBoxLayout()
        self.hboxlayout2_layergrpbox.setMargin(0)
        self.hboxlayout2_layergrpbox.setSpacing(6)
        self.hboxlayout2_layergrpbox.setObjectName("hboxlayout2_layergrpbox")
        
        self.currentLayer_label = QtGui.QLabel(self.layerProperties_groupBox)
        self.currentLayer_label.setObjectName("currentLayer_label")
        self.hboxlayout2_layergrpbox.addWidget(self.currentLayer_label)
        
        self.currentLayerCBox = QComboBox(self.layerProperties_groupBox)
        self.hboxlayout2_layergrpbox.addWidget(self.currentLayerCBox)
                
        self.addLayerButton = QPushButton(self.layerProperties_groupBox)
        self.addLayerButton.setIcon(geticon('ui/actions/Properties Manager/addlayer'))
        self.addLayerButton.setFixedSize(QtCore.QSize(26,26))
        self.addLayerButton.setIconSize(QtCore.QSize(22,22))
        self.hboxlayout2_layergrpbox.addWidget(self.addLayerButton)
        self.vboxlayout_layergrpbox.addLayout(self.hboxlayout2_layergrpbox)
        
        
        self.hboxlayout3_layergrpbox = QtGui.QHBoxLayout()
        self.hboxlayout3_layergrpbox.setMargin(0)
        self.hboxlayout3_layergrpbox.setSpacing(6)
        self.hboxlayout3_layergrpbox.setObjectName("hboxlayout3_layergrpbox")
        
        self.latticeCells_label = QLabel("Lattice Cells")
        self.hboxlayout3_layergrpbox.addWidget(self.latticeCells_label)
        
        #spacerItem = QtGui.QSpacerItem(35,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        #self.hboxlayout3_layergrpbox.addItem(spacerItem)
        
        self.layerCellsSpinBox = QSpinBox(self.layerProperties_groupBox)
        self.layerCellsSpinBox.setRange(1, 25)
        self.layerCellsSpinBox.setValue(2)
        self.layerCellsSpinBox.setToolTip("Number of lattice cells")
        self.hboxlayout3_layergrpbox.addWidget(self.layerCellsSpinBox)
        self.vboxlayout_layergrpbox.addLayout(self.hboxlayout3_layergrpbox)
        
        self.hboxlayout4_layergrpbox = QtGui.QHBoxLayout()
        self.hboxlayout4_layergrpbox.setMargin(0)
        self.hboxlayout4_layergrpbox.setSpacing(6)
        self.hboxlayout4_layergrpbox.setObjectName("hboxlayout4_layergrpbox")
        
        self.layerThickness_label = QLabel(self.layerProperties_groupBox)
        self.hboxlayout4_layergrpbox.addWidget(self.layerThickness_label)
        
        #spacerItem = QtGui.QSpacerItem(65,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        #self.hboxlayout4_layergrpbox.addItem(spacerItem)
        
        self.layerThicknessLineEdit = QLineEdit("layerThicknessLineEdit")
        self.layerThicknessLineEdit.setReadOnly(1)
        self.layerThicknessLineEdit.setText("")
        self.layerThicknessLineEdit.setToolTip("Thickness of layer in Angstroms")
        self.hboxlayout4_layergrpbox.addWidget(self.layerThicknessLineEdit)
        self.vboxlayout_layergrpbox.addLayout(self.hboxlayout4_layergrpbox) 
        
        #End Layer Properties Groupbox
        self.pmVBoxLayout.addWidget(self.layerProperties_groupBox)
        
    def ui_displayOptions_groupBox(self, CookiePropertyManager):
        #Start Display Options Groupbox
        
        self.displayOptions_groupBox = QtGui.QGroupBox(CookiePropertyManager)
        self.displayOptions_groupBox .setObjectName("displayOptions_groupBox")
        
        self.displayOptions_groupBox.setAutoFillBackground(True) 
        palette =  CookiePropertyManager.getGroupBoxPalette()
        self.displayOptions_groupBox.setPalette(palette)
        
        styleSheet = CookiePropertyManager.getGroupBoxStyleSheet()        
        self.displayOptions_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_grpbox2 = QtGui.QVBoxLayout(self.displayOptions_groupBox)
        self.vboxlayout_grpbox2.setMargin(0)
        self.vboxlayout_grpbox2.setSpacing(6)
        self.vboxlayout_grpbox2.setSizeConstraint(QLayout.SetMinimumSize)
        self.vboxlayout_grpbox2.setObjectName("vboxlayout_grpbox2")

    
        self.displayOptions_groupBoxButton =  CookiePropertyManager.getGroupBoxTitleButton(
            "Display Options", self.displayOptions_groupBox)
        self.vboxlayout_grpbox2.addWidget(self.displayOptions_groupBoxButton)
               
        self.hboxlayout2_grpbox2 = QtGui.QHBoxLayout()
        self.hboxlayout2_grpbox2.setMargin(0)
        self.hboxlayout2_grpbox2.setSpacing(3)
        self.hboxlayout2_grpbox2.setObjectName("hboxlayout2_grpbox2")
        
        self.dispTextLabel = QLabel("Cookie Display Format:", self.displayOptions_groupBox)   
        self.hboxlayout2_grpbox2.addWidget(self.dispTextLabel)
        
        self.dispModeCBox = QComboBox(self.displayOptions_groupBox)
        self.dispModeCBox.insertItem(1,"Tubes")
        self.dispModeCBox.insertItem(2,"Spheres")
        self.hboxlayout2_grpbox2.addWidget(self.dispModeCBox)
        
        self.vboxlayout_grpbox2.addLayout(self.hboxlayout2_grpbox2)
        
        self.gridLineCheckBox = QCheckBox("Show Grid Lines", self.displayOptions_groupBox)
        self.gridLineCheckBox.setChecked(1)
        self.gridLineCheckBox.setToolTip("Show or hide the grid lines")
        self.vboxlayout_grpbox2.addWidget(self.gridLineCheckBox )
        
        self.fullModelCheckBox = QCheckBox("Show Existing Model", self.displayOptions_groupBox)
        self.fullModelCheckBox.setToolTip("Show or hide existing model.")
        self.vboxlayout_grpbox2.addWidget(self.fullModelCheckBox)                 
        
        #End Display Options Groupbox
        self.pmVBoxLayout.addWidget(self.displayOptions_groupBox)
        
    def ui_advancedOptions_groupBox(self, CookiePropertyManager):
        #Start AdvancedOptions Groupbox
        self.advancedOptions_groupBox = QtGui.QGroupBox(CookiePropertyManager)
        self.advancedOptions_groupBox .setObjectName("advancedOptions_groupBox")
        
        self.advancedOptions_groupBox.setAutoFillBackground(True) 
        palette =  CookiePropertyManager.getGroupBoxPalette()
        self.advancedOptions_groupBox.setPalette(palette)
        
        styleSheet = CookiePropertyManager.getGroupBoxStyleSheet()        
        self.advancedOptions_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_grpbox3 = QtGui.QVBoxLayout(self.advancedOptions_groupBox)
        self.vboxlayout_grpbox3.setMargin(0)
        self.vboxlayout_grpbox3.setSpacing(6)
        self.vboxlayout_grpbox3.setObjectName("vboxlayout_grpbox3")

        self.advancedOptions_groupBoxButton = CookiePropertyManager.getGroupBoxTitleButton(
            "Advanced Options", self.advancedOptions_groupBox)
        self.vboxlayout_grpbox3.addWidget(self.advancedOptions_groupBoxButton)
        
        self.snapGridCheckBox = QCheckBox("Snap To Grid", self.advancedOptions_groupBox)
        self.snapGridCheckBox.setChecked(1)
        self.snapGridCheckBox.setToolTip("Snap selection point to a nearest cell grid point.")
        self.vboxlayout_grpbox3.addWidget(self.snapGridCheckBox) 
        
        self.freeViewCheckBox = QCheckBox("Enable Free View", self.advancedOptions_groupBox)
        self.freeViewCheckBox.setToolTip("Sets the current view to the one resulting after rotating the workspace ")
        self.vboxlayout_grpbox3.addWidget(self.freeViewCheckBox)
    
        #End Advanced Options
        self.pmVBoxLayout.addWidget(self.advancedOptions_groupBox)
        

    def retranslateUi(self, CookiePropertyManager):
        CookiePropertyManager.setWindowTitle(QtGui.QApplication.translate(
            "CookiePropertyManager", 
            "CookiePropertyManager", 
            None,
            QtGui.QApplication.UnicodeUTF8))
    
        self.gridOrientation_label.setText(QtGui.QApplication.translate(
            "CookiePropertyManager", 
            "Grid Orientation", 
             None, 
            QtGui.QApplication.UnicodeUTF8))
        
        self.rotateGrid_label.setText(QtGui.QApplication.translate(
            "CookiePropertyManager", 
             "Rotate Grid", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
        
        self.currentLayer_label.setText(QtGui.QApplication.translate(
            "CookiePropertyManager", 
            "Current Layer:", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
        
        self.addLayerButton.setToolTip("Adds a new layer to draw the cookie shape on")
        
        self.currentLayerCBox.setToolTip("Shows the current cookie layer")
        self.layerThickness_label.setText(QtGui.QApplication.translate(
            "CookiePropertyManager", 
            "Lattice Thickness:", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
