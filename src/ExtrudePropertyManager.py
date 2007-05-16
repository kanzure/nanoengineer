# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""
import sys
from PyQt4 import QtCore, QtGui
from Ui_ExtrudePropertyManager import Ui_ExtrudePropertyManager
from PropertyManagerMixin import PropertyManagerMixin
from PyQt4.Qt import Qt, SIGNAL

class ExtrudePropertyManager(QtGui.QWidget, PropertyManagerMixin, Ui_ExtrudePropertyManager):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.retranslateUi(self)
        
        self.extrudeSpinBox_circle_n = None ##@@@ This was earlier set in do_what_Mainwindow_.should_do
        ##we are not calling that function anymore so setting it here
        
        #connect slots
        self.connect(self.productSpec_groupBoxButton, SIGNAL("clicked()"),self.toggle_productSpec_groupBox)
        self.connect(self.sponsor_btn,SIGNAL("clicked()"),self.sponsor_btn_clicked)
        self.connect(self.extrudeDirection_groupBoxButton, SIGNAL("clicked()"),self.toggle_extrudeDirection_groupBox)
        self.connect(self.advancedOptions_groupBoxButton, SIGNAL("clicked()"),self.toggle_advancedOptions_groupBox)      
        self.connect(self.done_btn,SIGNAL("clicked()"),self.w.toolsDone)
        self.connect(self.abort_btn,SIGNAL("clicked()"),self.w.toolsCancel)
        
    def toggle_productSpec_groupBox(self):
        self.toggle_groupbox(self.productSpec_groupBoxButton,
                             self.productSpec_groupBoxWidget)
                        
    def toggle_extrudeDirection_groupBox(self):
        self.toggle_groupbox(self.extrudeDirection_groupBoxButton)
    

    def toggle_advancedOptions_groupBox(self):
        self.toggle_groupbox(self.advancedOptions_groupBoxButton, 
                             self.advancedOptions_groupBoxWidget)
        
        
        
        
    