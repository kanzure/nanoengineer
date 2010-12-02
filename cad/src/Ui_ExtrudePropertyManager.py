# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

"""
$Id$
"""
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QLayout
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QSize
from PyQt4.Qt import QGridLayout
from PyQt4.Qt import QLabel
from PyQt4.Qt import QSlider
from PyQt4.Qt import Qt
from PyQt4.Qt import QDoubleSpinBox

from Utility import geticon, getpixmap
from widgets import FloatSpinBox, TogglePrefCheckBox
from qt4transition import qt4todo

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
from PropMgr_Constants import pmGridLayoutMargin
from PropMgr_Constants import pmGridLayoutSpacing
from PropMgr_Constants import pmLabelRightAlignment
from PropMgr_Constants import pmGroupBoxSpacing
from PropMgr_Constants import pmGrpBoxVboxLayoutMargin
from PropMgr_Constants import pmGrpBoxVboxLayoutSpacing
from PropMgr_Constants import pmCancelButton
from PropMgr_Constants import pmDoneButton
from PropMgr_Constants import pmWhatsThisButton

class Ui_ExtrudePropertyManager(object):
    def setupUi(self, ExtrudePropertyManager):
        ExtrudePropertyManager.setObjectName("ExtrudePropertyManager")
        
        pmVBoxLayout(ExtrudePropertyManager)
        pmAddHeader(ExtrudePropertyManager)
	pmAddSponsorButton(ExtrudePropertyManager)
	
        pmAddTopRowButtons(ExtrudePropertyManager, 
			   showFlags = 
			   pmDoneButton | 
			   pmCancelButton | 
			   pmWhatsThisButton)
	
	self.MessageGroupBox = pmMessageGroupBox(self, title="Message")
	self.pmVBoxLayout.addWidget(self.MessageGroupBox)
	pmAddBottomSpacer(self.MessageGroupBox, self.pmVBoxLayout)
        
        self.ui_productSpec_groupBox(ExtrudePropertyManager)
	pmAddBottomSpacer(self.productSpec_groupBox, self.pmVBoxLayout)
        
        self.ui_extrudeDirection_groupBox(ExtrudePropertyManager)
	# Don't add the spacer since the extrude direction groupbox is
	# currently hidden (but we still need to create it above).
	# pmAddBottomSpacer(self.extrudeDirection_groupBox, self.pmVBoxLayout)
        
        self.ui_advancedOptions_groupBox(ExtrudePropertyManager)
	pmAddBottomSpacer(self.advancedOptions_groupBox, self.pmVBoxLayout, last=True)
        
        self.retranslateUi(ExtrudePropertyManager)
        QtCore.QMetaObject.connectSlotsByName(ExtrudePropertyManager)
    
    def ui_productSpec_groupBox(self, ExtrudePropertyManager):
	"""Creates the "Product Specifications" groupbox.
	"""
        self.productSpec_groupBox = QtGui.QGroupBox(ExtrudePropertyManager)
        self.productSpec_groupBox.setObjectName("productSpec_groupBox")
        
        self.productSpec_groupBox.setAutoFillBackground(True) 
        palette =  ExtrudePropertyManager.getGroupBoxPalette()
        self.productSpec_groupBox.setPalette(palette)
            
        styleSheet = ExtrudePropertyManager.getGroupBoxStyleSheet()        
        self.productSpec_groupBox.setStyleSheet(styleSheet)
    
        self.vboxlayout_grpbox1 = QtGui.QVBoxLayout(self.productSpec_groupBox)
	self.vboxlayout_grpbox1.setMargin(pmGrpBoxVboxLayoutMargin)
        self.vboxlayout_grpbox1.setSpacing(pmGrpBoxVboxLayoutSpacing)

        self.productSpec_groupBoxButton = ExtrudePropertyManager.getGroupBoxTitleButton(
            "Product Specifications", self.productSpec_groupBox)
        self.vboxlayout_grpbox1.addWidget(self.productSpec_groupBoxButton)
        
        self.productSpec_groupBoxWidget = QtGui.QWidget(
            self.productSpec_groupBox)
                
        vlo_grpbx_widget = QtGui.QVBoxLayout(
            self.productSpec_groupBoxWidget)
        vlo_grpbx_widget.setMargin(4)
        vlo_grpbx_widget.setSpacing(2)
              
        # Start Product Type Combobox 
	
	# Create grid layout
        self.GridLayout = QGridLayout()
        self.GridLayout.setMargin(pmGridLayoutMargin)
        self.GridLayout.setSpacing(pmGridLayoutSpacing)
        
        # Insert grid layout
	vlo_grpbx_widget.addLayout(self.GridLayout) 
	
        self.extrude_productType_label = QtGui.QLabel(
            self.productSpec_groupBoxWidget)
	self.extrude_productType_label.setAlignment(pmLabelRightAlignment)
        self.GridLayout.addWidget(self.extrude_productType_label,
				  0, 0,
				  1, 1)
          
        self.extrude_productTypeComboBox= QtGui.QComboBox(
            self.productSpec_groupBoxWidget)
        
        self.extrude_productTypeComboBox.insertItem(0,"rod") # these names are seen by user but not by our code        
        self.extrude_productTypeComboBox.insertItem(1,"ring")        
        self.extrude_productTypeComboBox_ptypes = ["straight rod", "closed ring", "corkscrew"] # names used in the code, same order
        # # # # if you comment out items from combobox, you also have to remove them from this list unless they are at the end!!!
	
	self.GridLayout.addWidget(self.extrude_productTypeComboBox,
				  0, 1,
				  1, 1)        
        
        # End ProductType Combobox 

        # Start Total Number of copies Spinbox (Including Base Unit)

        self.extrudeSpinBox_n_label = QtGui.QLabel(
            self.productSpec_groupBoxWidget)
	self.extrudeSpinBox_n_label.setAlignment(pmLabelRightAlignment)
	self.GridLayout.addWidget(self.extrudeSpinBox_n_label,
				  1, 0,
				  1, 1)
                        
        self.extrudeSpinBox_n = QtGui.QSpinBox(self.productSpec_groupBoxWidget)
        self.extrudeSpinBox_n.setObjectName("extrudeSpinBox_n")
        
        self.GridLayout.addWidget(self.extrudeSpinBox_n,
				  1, 1,
				  1, 1)   
	    
        # End Total Number of copies Spinbox (Including Base Unit)
        
        self.vboxlayout_grpbox1.addWidget(self.productSpec_groupBoxWidget)
        
        # End Product Specifications Groupbox        
        self.pmVBoxLayout.addWidget(self.productSpec_groupBox)
        
        
    def ui_extrudeDirection_groupBox(self, ExtrudePropertyManager):
	"""Creates the "Extrude Direction" groupbox. This is not shown.
	It is created, but hidden (below).
	"""
        #Start extrudeDirection groupbox
        self.extrudeDirection_groupBox = QtGui.QGroupBox(ExtrudePropertyManager)
        self.extrudeDirection_groupBox.setObjectName("extrudeDirection_groupBox")
        
        self.extrudeDirection_groupBox.setAutoFillBackground(True) 
        palette =  ExtrudePropertyManager.getGroupBoxPalette()
        self.extrudeDirection_groupBox.setPalette(palette)
               
        styleSheet = ExtrudePropertyManager.getGroupBoxStyleSheet()        
        self.extrudeDirection_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_grpbox2 = QtGui.QVBoxLayout(self.extrudeDirection_groupBox)
	self.vboxlayout_grpbox2.setMargin(pmGrpBoxVboxLayoutMargin)
        self.vboxlayout_grpbox2.setSpacing(pmGrpBoxVboxLayoutSpacing)
        
        self.extrudeDirection_groupBoxButton = ExtrudePropertyManager.getGroupBoxTitleButton(
            "Extrude Direction", self.extrudeDirection_groupBox)
        self.vboxlayout_grpbox2.addWidget(self.extrudeDirection_groupBoxButton)
    
        # End extrudeDirection  Groupbox         
        self.pmVBoxLayout.addWidget(self.extrudeDirection_groupBox)
	
	# Commenting out this spacer since the groupbox isn't implemented. Mark 2007-05-29.
        #spacer_extrudedirection_grpbx = QtGui.QSpacerItem(10,10,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        #self.pmVBoxLayout.addItem(spacer_extrudedirection_grpbx)
        
        #Hide extrude direction group box until it is implemented - ninad070411
        self.extrudeDirection_groupBox.hide()

        
    def ui_advancedOptions_groupBox(self, ExtrudePropertyManager):
	"""Creates the "Advanced Options" groupbox.
	"""
        self.advancedOptions_groupBox = QtGui.QGroupBox(ExtrudePropertyManager)
        self.advancedOptions_groupBox .setObjectName("advancedOptions_groupBox")
        
        self.advancedOptions_groupBox.setAutoFillBackground(True) 
        palette =  ExtrudePropertyManager.getGroupBoxPalette()
        self.advancedOptions_groupBox.setPalette(palette)
        
        styleSheet = ExtrudePropertyManager.getGroupBoxStyleSheet()        
        self.advancedOptions_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_grpbox3 = QtGui.QVBoxLayout(self.advancedOptions_groupBox)
	self.vboxlayout_grpbox3.setMargin(pmGrpBoxVboxLayoutMargin)
        self.vboxlayout_grpbox3.setSpacing(pmGrpBoxVboxLayoutSpacing)

        self.advancedOptions_groupBoxButton = ExtrudePropertyManager.getGroupBoxTitleButton(
            "Advanced Options", self.advancedOptions_groupBox)        
           
        self.vboxlayout_grpbox3.addWidget(self.advancedOptions_groupBoxButton)
        
        self.advancedOptions_groupBoxWidget = QtGui.QWidget(
            self.advancedOptions_groupBox)
        
        vlo_grpbx_widget = QtGui.QVBoxLayout(
            self.advancedOptions_groupBoxWidget)
        vlo_grpbx_widget.setMargin(4)
        vlo_grpbx_widget.setSpacing(4)
        
        self.extrudePref1 = TogglePrefCheckBox(
            "Show Entire Model", 
            self.advancedOptions_groupBoxWidget,
            "extrudePref1", 
            default = False,
            attr = 'show_entire_model',
            repaintQ = True )
        
        vlo_grpbx_widget.addWidget(self.extrudePref1)        
       
        self.extrudePref3 = TogglePrefCheckBox(
            "Make Bonds", 
            self.advancedOptions_groupBoxWidget,
            "extrudePref3", 
            attr = 'whendone_make_bonds')
        
        vlo_grpbx_widget.addWidget(self.extrudePref3)
        
        self.extrudePref2 = TogglePrefCheckBox(
            "Show Bond-offset Spheres", 
            self.advancedOptions_groupBoxWidget,
            "extrudePref2", default = False,  
            attr = 'show_bond_offsets', 
            repaintQ = True )
	
        vlo_grpbx_widget.addWidget(self.extrudePref2)
        
        self.extrudeBondCriterionLabel = QLabel("")
        #self.extrudeBondCriterionLabel_lambda_tol_nbonds = lambda_tol_nbonds
        self.extrudeBondCriterionSlider_dflt = dflt = 100
        vlo_grpbx_widget.addWidget(self.extrudeBondCriterionLabel)
        
        
        self.extrudeBondCriterionSlider = QSlider(
            Qt.Horizontal,
            self.advancedOptions_groupBoxWidget)
        
        self.extrudeBondCriterionSlider.setMinimum(0)
        self.extrudeBondCriterionSlider.setMaximum(300)
        self.extrudeBondCriterionSlider.setPageStep(5)
        self.extrudeBondCriterionSlider.setValue(dflt)
        vlo_grpbx_widget.addWidget(self.extrudeBondCriterionSlider)
        
        #ninad070410: Bruce should hook-up the following preference       
        self.extrudePrefMergeSelection = TogglePrefCheckBox(
            "Merge Selection", 
            self.advancedOptions_groupBoxWidget, 
            "extrudePrefMergeSelection",
            attr = 'whendone_merge_selection',
            default= False)
        
        vlo_grpbx_widget.addWidget(self.extrudePrefMergeSelection)
        
        self.extrudePref4 = TogglePrefCheckBox(
            "Merge Copies", 
            self.advancedOptions_groupBoxWidget, 
            "extrudePref4",
            attr = 'whendone_all_one_part',
            default= False)    
        
        vlo_grpbx_widget.addWidget(self.extrudePref4)
        
        
        #@@@ extrudeSpinBox_x/y/z and length are temporarily placed in Advanced option gruopbox
        
        qt4todo('#@@@ extrudeSpinBox_x/y/z and length are \
        temporarily placed in Advanced option gruopbox')
        
        #vbox layout for X, Y, Z and length spinboxes
        spinboxes_vlayout = QtGui.QVBoxLayout()
        
        spacerItem_spinbox_x= QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        spacerItem_spinbox_y= QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        spacerItem_spinbox_z= QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        spacerItem_spinbox_length= QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        
        spinbox_length_hlayout = QtGui.QHBoxLayout()       
        spinbox_length_hlayout.setSpacing(4)
        spinbox_length_hlayout.setMargin(4)
        
        self.length_label = QtGui.QLabel(self.advancedOptions_groupBoxWidget)       
        spinbox_length_hlayout.addWidget(self.length_label)  
        
        self.extrudeSpinBox_length = QDoubleSpinBox(
            self.advancedOptions_groupBoxWidget)
        self.extrudeSpinBox_length.setDecimals(2)
        self.extrudeSpinBox_length.setRange(0.1, 2000)
        spinbox_length_hlayout.addWidget(self.extrudeSpinBox_length)
        
                
        spinbox_length_hlayout.addItem(spacerItem_spinbox_length)
        spinboxes_vlayout.addLayout(spinbox_length_hlayout)
        
        spinbox_x_hlayout = QtGui.QHBoxLayout()   
        spinbox_x_hlayout.setSpacing(4)
        spinbox_x_hlayout.setMargin(4)
        
        self.x_label = QtGui.QLabel(self.advancedOptions_groupBoxWidget)
        spinbox_x_hlayout.addWidget(self.x_label)
        
        self.extrudeSpinBox_x = QDoubleSpinBox(
            self.advancedOptions_groupBoxWidget)
        self.extrudeSpinBox_x.setDecimals(2)
        self.extrudeSpinBox_x.setRange(-1000.0, 1000.0)        
        spinbox_x_hlayout.addWidget(self.extrudeSpinBox_x)
        
        spinbox_x_hlayout.addItem(spacerItem_spinbox_x)
        
        spinboxes_vlayout.addLayout(spinbox_x_hlayout)
        
        spinbox_y_hlayout = QtGui.QHBoxLayout()  
        spinbox_y_hlayout.setSpacing(4)
        spinbox_y_hlayout.setMargin(4)
        
              
        self.y_label = QtGui.QLabel(self.advancedOptions_groupBoxWidget)       
        spinbox_y_hlayout.addWidget(self.y_label)        
        
        self.extrudeSpinBox_y = QDoubleSpinBox(
            self.advancedOptions_groupBoxWidget)
        self.extrudeSpinBox_y.setDecimals(2)
        self.extrudeSpinBox_y.setRange(-1000.0, 1000.0)
        spinbox_y_hlayout.addWidget(self.extrudeSpinBox_y)
        
        spinbox_y_hlayout.addItem(spacerItem_spinbox_y)
        
        spinboxes_vlayout.addLayout(spinbox_y_hlayout)
        
        spinbox_z_hlayout = QtGui.QHBoxLayout()
        spinbox_z_hlayout.setSpacing(4)
        spinbox_z_hlayout.setMargin(4)
               
        
        self.z_label = QtGui.QLabel(self.advancedOptions_groupBoxWidget)       
        spinbox_z_hlayout.addWidget(self.z_label)  
                
        self.extrudeSpinBox_z = QDoubleSpinBox(
            self.advancedOptions_groupBoxWidget)
        self.extrudeSpinBox_z.setDecimals(2)
        self.extrudeSpinBox_z.setRange(-1000.0, 1000.0)
        spinbox_z_hlayout.addWidget(self.extrudeSpinBox_z)
        
        spinbox_z_hlayout.addItem(spacerItem_spinbox_z)
        
        spinboxes_vlayout.addLayout(spinbox_z_hlayout) 
        spinboxes_vlayout.setSpacing(2)
        spinboxes_vlayout.setMargin(2)
        
        vlo_grpbx_widget.addLayout(spinboxes_vlayout)
        
        ##Start bondOptionsWidget
        #self.bondOptionsWidget = QtGui.QWidget(
        #          self.advancedOptions_groupBoxWidget )
               
        ##End  bondOptionsWidget
        
        ##Start displayOptionsWidget
        #self.displayOptionsWidget = QtGui.QWidget(
        #                  self.advancedOptions_groupBoxWidget)
        
        ## End displayOptionsWidget        
        self.vboxlayout_grpbox3.addWidget(self.advancedOptions_groupBoxWidget)
        
        #End Advanced Options
        self.pmVBoxLayout.addWidget(self.advancedOptions_groupBox)
        

    def retranslateUi(self, ExtrudePropertyManager):
        ExtrudePropertyManager.setWindowTitle(
	    QtGui.QApplication.translate("ExtrudePropertyManager", 
					"ExtrudePropertyManager", 
					None, 
					QtGui.QApplication.UnicodeUTF8))
        self.extrude_productType_label.setText(
	    QtGui.QApplication.translate("ExtrudePropertyManager", 
					"Final product :",
					None, 
					QtGui.QApplication.UnicodeUTF8))
        self.extrudeSpinBox_n_label.setText(
	    QtGui.QApplication.translate("ExtrudePropertyManager", 
					"Number of copies :", 
					None, 
					QtGui.QApplication.UnicodeUTF8))
        self.x_label.setText(
	    QtGui.QApplication.translate("ExtrudePropertyManager", 
					"X Offset :", 
					None, 
					QtGui.QApplication.UnicodeUTF8))
        self.y_label.setText(
	    QtGui.QApplication.translate("ExtrudePropertyManager", 
					"Y Offset :", 
					None, 
					QtGui.QApplication.UnicodeUTF8))
        self.z_label.setText(
	    QtGui.QApplication.translate("ExtrudePropertyManager", 
					"Z Offset :", 
					None, 
					QtGui.QApplication.UnicodeUTF8))
        self.length_label.setText(
	    QtGui.QApplication.translate("ExtrudePropertyManager", 
					"Total Offset :", 
					None, 
					QtGui.QApplication.UnicodeUTF8))
