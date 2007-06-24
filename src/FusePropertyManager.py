# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
FusePropertyManager.py
@author: Ninad
@version: $Id$
@copyright:2004-2007 Nanorex, Inc.  All rights reserved.

History: 
ninad070425 :1) Moved Fuse dashboard to Property manager 
             2) Implemented Translate/ Rotate enhancements

"""
__author__  = "Ninad"

import sys
from PyQt4 import QtCore, QtGui
from PropertyManagerMixin import PropertyManagerMixin
from Ui_FusePropertyManager import Ui_FusePropertyManager
from PyQt4.Qt import Qt, SIGNAL
from Utility import geticon

class FusePropertyManager(QtGui.QWidget, 
                          PropertyManagerMixin,
                          Ui_FusePropertyManager):
    def __init__(self):
        QtGui.QWidget.__init__(self)
                                
        self.setupUi(self)
        self.retranslateUi(self)     
        
        #At startup Move groupbox is active by default 
        #the following variable sets this flag (used in fusechunksMode.leftDrag)
        self.isMoveGroupBoxActive = True
        self.o.setCursor(self.w.MolSelTransCursor)
        
        self.showGroupBox(self.translate_groupBoxButton, 
                          self.translateGroupBox_widgetHolder)        
        self.hideGroupBox(self.rotate_groupBoxButton, 
                          self.rotateGroupBox_widgetHolder)
        
        self.lastCheckedRotateAction = None 
        self.lastCheckedMoveAction = None
        
        #connect slots
        self.connect(self.sponsor_btn,
                     SIGNAL("clicked()"),
                     self.sponsor_btn_clicked)
        
        self.connect(self.translate_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.activate_translateGroupBox_in_fuse_PM)            
        self.connect(self.rotate_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.activate_rotateGroupBox_in_fuse_PM)
        
        self.connect(self.fuseOptions_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_fuseOptionsGroupBox)
        
        try:
            self.connect(self.movetype_combox, SIGNAL("currentIndexChanged(int)"), 
                         self.updateMoveGroupBoxItems)
            self.connect(self.rotatetype_combox, SIGNAL("currentIndexChanged(int)"), 
                         self.updateRotateGroupBoxItems)
        except:
            print "Bug: methods defined in Move Property manager methods\
            not accessible in fuse property manager. Likely to cause other bugs\
            Returning"
            return            
        
        
    def activate_translateGroupBox_in_fuse_PM(self):
        """Show contents of translate groupbox, deactivae the rotate groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable). This method is called only when move groupbox button 
        is clicked. See also activate_translateGroupBox_in_fuse_PM method . 
        """
        
        #@@Note: FusePropertyManager doesn't inherit MovePropertyManager. 
        # but Fuse PM is (and should be) *only* called in Fuse Chunks mode. 
        #Fuse Chunks mode is a a subclass of modifyMode (which inherits 
        #MoveProperty manager) So the following should work. 
        #If in future, for some reasons fuseChunk doesn't inherit modifyMode, 
        # the following won't work. The following try-except statement will 
        #partially help identify the problem (if it ever arises) -- ninad070425
        
        try:
            self.toggle_translateGroupBox()
            self.o.setCursor(self.w.MolSelTransCursor)
            self.deactivate_rotateGroupBox()
        except:
            print "Bug: methods defined in Move Property manager methods\
            not accessible in fuse property manager. Likely to cause other bugs\
            Returning"
            return
                
        
        #This is the action that was checked the last time when this 
        #groupbox was active. (note: its defined in MovceProperty Manager)
        
        actionToCheck = self.getLastCheckedMoveAction()             
          
        if actionToCheck:
            actionToCheck.setChecked(True) 
        else:
            actionToCheck = self.w.moveFreeAction
            actionToCheck.setChecked(True)
        
        self.isMoveGroupBoxActive = True
    
    def activate_rotateGroupBox_in_fuse_PM(self):
        """Show contents of rotate groupbox (in fuse PM), deactivae the 
        #translate groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable). This method is called only when rotate groupbox button 
        is clicked. See also activate_rotateGroupBox_in_fuse_PM method. 
        """
        
        #@@Note: FusePropertyManager doesn't inherit MovePropertyManager. 
        # but Fuse PM is (and should be) *only* called in Fuse Chunks mode. 
        #Fuse Chunks mode is a a subclass of modifyMode (which inherits 
        #MoveProperty manager) So the following should work. 
        #If in future, for some reasons fuseChunk doesn't inherit modifyMode, 
        # the following won't work. The following try-except statement will 
        #partially help identify the problem (if it ever arises) -- ninad070425
        
        try:
            self.toggle_rotateGroupBox()
            self.o.setCursor(self.w.MolSelRotCursor)
            self.deactivate_translateGroupBox()
        except:
            print "Bug: methods defined in Move Property manager methods\
            not accessible in fuse property manager. Likely to cause other bugs\
            Returning"
            return
        
        #This is the action that was checked the last time when this 
        #groupbox was active. 
        actionToCheck = self.getLastCheckedRotateAction()
                  
        if actionToCheck:
            actionToCheck.setChecked(True) 
        else:
            actionToCheck = self.w.rotateFreeAction
            actionToCheck.setChecked(True)
        
        self.isMoveGroupBoxActive = False
        
    def toggle_fuseOptionsGroupBox(self):
        '''Toggles the item display in the parent groupbox of the button'''
        
        self.toggle_groupbox(self.fuseOptions_groupBoxButton,
                             self.fuseOptions_widgetHolder)  
    
        