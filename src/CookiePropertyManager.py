# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""
import sys
from PyQt4 import QtCore, QtGui
from Ui_CookiePropertyManager import Ui_CookiePropertyManager
from PropertyManagerMixin import PropertyManagerMixin
from PyQt4.Qt import Qt, SIGNAL

class CookiePropertyManager(QtGui.QWidget, PropertyManagerMixin, Ui_CookiePropertyManager):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.setupUi(self)
        self.retranslateUi(self)
        
        #connect slots
        self.connect(self.sponsor_btn,
                     SIGNAL("clicked()"),
                     self.sponsor_btn_clicked)
        self.connect(self.cookieSpec_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_cookieSpec_groupBox)      
        self.connect(self.layerProperties_groupBoxButton, 
                     SIGNAL("clicked()"), 
                     self.toggle_layerProperties_groupBox)        
        self.connect(self.displayOptions_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_displayOptions_groupBox)      
        self.connect(self.advancedOptions_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_advancedOptions_groupBox)    
        
    def toggle_cookieSpec_groupBox(self):
        self.toggle_groupbox(self.cookieSpec_groupBoxButton, self.latticeCBox, self.latticeLabel, self.surface100_btn,
                         self.surface110_btn, self.surface111_btn, self.gridOrientation_label,
                         self.rotateGrid_label, self.gridRotateAngle, self.antiRotateButton, self.rotateButton)
        
    def toggle_advancedOptions_groupBox(self):
        self.toggle_groupbox(self.advancedOptions_groupBoxButton, self.snapGridCheckBox, self.freeViewCheckBox)
        
    def toggle_displayOptions_groupBox(self):
        self.toggle_groupbox(self.displayOptions_groupBoxButton, self.dispTextLabel, self.dispModeCBox, 
                             self.fullModelCheckBox, self.gridLineCheckBox)
        
    def toggle_layerProperties_groupBox(self):
        self.toggle_groupbox(self.layerProperties_groupBoxButton, self.currentLayer_label, self.currentLayerCBox, 
                             self.addLayerButton,
                             self.latticeCells_label,  self.layerCellsSpinBox,
                             self.layerThickness_label, self.layerThicknessLineEdit)   