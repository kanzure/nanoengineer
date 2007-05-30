# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
MoviePropertyManager.py
@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  All rights reserved.

History:
ninad20070507 : Converted movie dashboard into movie Property manager


"""
__author__  = "Ninad"

import sys
from PyQt4 import QtCore, QtGui
from Ui_MoviePropertyManager import Ui_MoviePropertyManager
from PropertyManagerMixin import PropertyManagerMixin
from PyQt4.Qt import Qt, SIGNAL, QWhatsThis
from Utility import geticon



class MoviePropertyManager(QtGui.QWidget, 
                          PropertyManagerMixin, 
                          Ui_MoviePropertyManager):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.setupUi(self)
        self.retranslateUi(self)   
        
        self.lastCheckedRotateAction = None 
        self.lastCheckedMoveAction = None
                
        #connect slots
        self.connect(self.sponsor_btn,SIGNAL("clicked()"),self.sponsor_btn_clicked)
        self.connect(self.done_btn,SIGNAL("clicked()"),self.w.toolsDone)
        self.connect(self.abort_btn,SIGNAL("clicked()"),self.w.toolsCancel)
        self.connect(self.whatsthis_btn,
                     SIGNAL("clicked()"),
                     QWhatsThis.enterWhatsThisMode)
        
        self.connect(self.movieOptions_groupBoxButton, SIGNAL("clicked()"),
                     self.toggle_movieOptionsGroupBox)
        
        self.connect(self.movieControls_groupBoxButton, SIGNAL("clicked()"),
                     self.toggle_movieControlsGroupBox)  
        
        self.connect(self.movieFiles_groupBoxButton, SIGNAL("clicked()"),
                     self.toggle_movieFilesGroupBox)  
        
        
        
        
    def toggle_movieOptionsGroupBox(self):
        """ Toggles the item display in the parent groupbox of the button and 
       hides the other groupbox also disconnecting the actions in the other 
       groupbox
       Example: If user clicks on Movie groupbox button, it will toggle the 
       display of the groupbox """
        
        self.toggle_groupbox(self.movieOptions_groupBoxButton, 
                             self.movieOptionsGroupBox_widgetHolder) 
        
    def toggle_movieControlsGroupBox(self):
        """ Toggles the item display in the parent groupbox of the button and 
       hides the other groupbox also disconnecting the actions in the other 
       groupbox
       Example: If user clicks on Movie groupbox button, it will toggle the 
       display of the groupbox """
                
        self.toggle_groupbox(self.movieControls_groupBoxButton, 
                             self.movieControlsGroupBox_widgetHolder) 
        
    def toggle_movieFilesGroupBox(self):
        """ Toggles the item display in the parent groupbox of the button and 
       hides the other groupbox also disconnecting the actions in the other 
       groupbox
       Example: If user clicks on Movie groupbox button, it will toggle the 
       display of the groupbox """
        
        self.toggle_groupbox(self.movieFiles_groupBoxButton, 
                             self.movieFilesGroupBox_widgetHolder) 
