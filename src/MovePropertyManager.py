# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$

History:

ninad 070207 : created this file to manage 
Move and Rotate Property managers

"""
__author__  = "Ninad"

import sys
from PyQt4 import QtCore, QtGui
from Ui_MovePropertyManager import Ui_MovePropertyManager
from PropertyManagerMixin import PropertyManagerMixin
from PyQt4.Qt import Qt, SIGNAL, QWhatsThis
from Utility import geticon, getpixmap

class MovePropertyManager(QtGui.QWidget, PropertyManagerMixin, Ui_MovePropertyManager):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.setupUi(self)
        self.retranslateUi(self)   
        
        self.lastCheckedRotateAction = None 
        self.lastCheckedMoveAction = None
                
        #connect slots
        self.connect(self.sponsor_btn,SIGNAL("clicked()"),self.sponsor_btn_clicked)
        self.connect(self.done_btn,SIGNAL("clicked()"),self.w.toolsDone)
        self.connect(self.whatsthis_btn,
                     SIGNAL("clicked()"),
                     QWhatsThis.enterWhatsThisMode)
       
        self.connect(self.move_groupBoxButton, SIGNAL("clicked()"),self.activate_moveGroupBox_using_groupButton)            
        self.connect(self.rotate_groupBoxButton, SIGNAL("clicked()"),self.activate_rotateGroupBox_using_groupButton)
        
        self.connect(self.movetype_combox, SIGNAL("currentIndexChanged(int)"), self.updateMoveGroupBoxItems)
        self.connect(self.rotatetype_combox, SIGNAL("currentIndexChanged(int)"), self.updateRotateGroupBoxItems)
    
    def activate_moveGroupBox_using_groupButton(self):
        """Show contents of this groupbox, deactivae the other groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable). This method is called only when move groupbox button 
        is clicked. See also activate_moveGroupBox method. 
        """
        
        self.toggle_moveGroupBox()
        
        if not self.w.toolsMoveMoleculeAction.isChecked():
            self.w.toolsMoveMoleculeAction.setChecked(True)
            self.o.setCursor(self.w.MolSelTransCursor)
            
            self.heading_pixmap.setPixmap(getpixmap('ui/actions/Properties Manager/Translate_Components.png'))
            self.heading_label.setText(QtGui.QApplication.translate("MovePropertyManager", 
                                                                "<font color=\"#FFFFFF\">Translate</font>", 
                                                                None, QtGui.QApplication.UnicodeUTF8))  
            
            self.deactivate_rotateGroupBox()
            
            #This is the action that was checked the last time when this 
            #groupbox was active. 
            actionToCheck = self.getLastCheckedMoveAction()             
              
            if actionToCheck:
                actionToCheck.setChecked(True) 
            else:
                actionToCheck = self.w.moveFreeAction
                actionToCheck.setChecked(True)
            
    
    def activate_rotateGroupBox_using_groupButton(self):
        """Show contents of this groupbox, deactivae the other groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable). This method is called only when rotate groupbox button 
        is clicked. See also activate_rotateGroupBox method. 
        """
        
        self.toggle_rotateGroupBox()
        
        if not self.w.rotateComponentsAction.isChecked():            
            self.w.rotateComponentsAction.setChecked(True)           
            self.o.setCursor(self.w.MolSelRotCursor)
            self.heading_pixmap.setPixmap(getpixmap('ui/actions/Properties Manager/Rotate_Components.png'))
            self.heading_label.setText(QtGui.QApplication.translate("MovePropertyManager", 
                                                                "<font color=\"#FFFFFF\">Rotate</font>", 
                                                                None, QtGui.QApplication.UnicodeUTF8))        
            
            self.deactivate_moveGroupBox()
        
            #This is the action that was checked the last time when this 
            #groupbox was active. 
            actionToCheck = self.getLastCheckedRotateAction()
                      
            if actionToCheck:
                actionToCheck.setChecked(True) 
            else:
                actionToCheck = self.w.rotateFreeAction
                actionToCheck.setChecked(True)
                    
    def activate_moveGroupBox(self):
        """Show contents of this groupbox, deactivae the other groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable) This action is called when toolsMoveMoleculeAction
        is checked from the toolbar or command manager. 
        see also: activate_moveGroupBox_using_groupButton
        """
        self.toggle_moveGroupBox()
        self.o.setCursor(self.w.MolSelTransCursor)
        
        self.heading_pixmap.setPixmap(getpixmap('ui/actions/Properties Manager/Translate_Components.png'))        
        self.heading_label.setText(QtGui.QApplication.translate("MovePropertyManager", 
                                                                "<font color=\"#FFFFFF\">Translate</font>", 
                                                                None, QtGui.QApplication.UnicodeUTF8))  
            
        self.deactivate_rotateGroupBox()    
        
        #This is the action that was checked the last time when this 
        #groupbox was active. 
        actionToCheck = self.getLastCheckedMoveAction()             
          
        if actionToCheck:
            actionToCheck.setChecked(True) 
        else:
            actionToCheck = self.w.moveFreeAction
            actionToCheck.setChecked(True)
            
    def activate_rotateGroupBox(self):
        """Show contents of this groupbox, deactivae the other groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable). This action is called when rotateComponentsAction
        is checked from the toolbar or command manager. 
        see also: activate_rotateGroupBox_using_groupButton
        """
        
        self.toggle_rotateGroupBox()
        self.o.setCursor(self.w.MolSelRotCursor)
        
        self.heading_pixmap.setPixmap(getpixmap('ui/actions/Properties Manager/Rotate_Components.png'))        
        self.heading_label.setText(QtGui.QApplication.translate("MovePropertyManager", 
                                                                "<font color=\"#FFFFFF\">Rotate</font>", 
                                                                None, QtGui.QApplication.UnicodeUTF8))    
        
        self.deactivate_moveGroupBox()           
    
        #This is the action that was checked the last time when this 
        #groupbox was active. 
        actionToCheck = self.getLastCheckedRotateAction()
                  
        if actionToCheck:
            actionToCheck.setChecked(True) 
        else:
            actionToCheck = self.w.rotateFreeAction
            actionToCheck.setChecked(True)
        
                               
    def deactivate_rotateGroupBox(self):
        """ Hide the items in the groupbox, Also 
        store the current checked action which will be checked again 
        when user activates this groupbox again. After storing 
        the checked action, uncheck it (so that other active groupbox 
        action can operate easily). """
        
        self.hideGroupBox(self.rotate_groupBoxButton, self.rotateGroupBox_widgetHolder)
        
        #Store the last checked action of the groupbox you are about to close
        #(in this case Rotate Groupbox is the groupbox that will be deactivated and 
        #'Move groupbox will be activated (opened) ) 
        lastCheckedRotateAction = self.w.rotateOptionsGroup.checkedAction()        
        self.setLastCheckedRotateAction(lastCheckedRotateAction)     
        
        #Disconnect checked action in Rotate Components groupbox
        if self.w.rotateOptionsGroup.checkedAction(): #bruce 070613 added condition
            self.w.rotateOptionsGroup.checkedAction().setChecked(False)
        
    def deactivate_moveGroupBox(self):
        """ Hide the items in the groupbox, Also 
        store the current checked action which will be checked again 
        when user activates this groupbox again. After storing 
        the checked action, uncheck it (so that other active groupbox 
        action can operate easily). """
        
        self.hideGroupBox(self.move_groupBoxButton, self.moveGroupBox_widgetHolder) 
        
        #Store the last checked action of the groupbox you are about to close
        #(in this case Move Groupbox is the groupbox that will be deactivated and 
        #'Rotate groupbox will be activated (opened) ) 
        lastCheckedMoveAction = self.w.MoveOptionsGroup.checkedAction()        
        self.setLastCheckedMoveAction(lastCheckedMoveAction)        
        
        #Disconnect checked action in Move groupbox
        self.w.MoveOptionsGroup.checkedAction().setChecked(False)        
 
    def toggle_moveGroupBox(self):
        """ Toggles the item display in the parent groupbox of the button and 
       hides the other groupbox also disconnecting the actions in the other groupbox
       Example: If user clicks on Move groupbox button, it will toggle the display of the groupbox, 
       connect its actions and Hide the other groupbox i.e. Rotate Compomnents groupbox and also 
       disconnect actions inside it"""
        
        self.toggle_groupbox(self.move_groupBoxButton, self.moveGroupBox_widgetHolder)              
        
    def updateMoveGroupBoxItems(self, id):
        """Update the items displayed in the move groupbox based on 
        the combobox item selected"""
        if id is 0:
            self.toXYZPositionWidget.hide()
            self.byDeltaXYZWidget.hide()
            self.freeDragWidget.show()
                               
        if id is 1:
            self.freeDragWidget.hide()
            self.toXYZPositionWidget.hide()
            self.byDeltaXYZWidget.show()
                    
        if id is 2:
            self.freeDragWidget.hide()
            self.byDeltaXYZWidget.hide()
            self.toXYZPositionWidget.show()
            
    def updateRotateGroupBoxItems(self, id):
        """Update the items displayed in the rotate groupbox based on 
        the combobox item selected"""
        if id is 0:            
            self.rotateBySpecifiedAngleWidget.hide()
            self.freeDragRotateWidget.show()     
            
        if id is 1:
            self.freeDragRotateWidget.hide()
            self.rotateBySpecifiedAngleWidget.show()
            
    def toggle_rotateGroupBox(self):
        """ Toggles the item display in the parent groupbox of the button and 
       hides the other groupbox also disconnecting the actions in the other groupbox
       Example: If user clicks on Move groupbox button, it will toggle the display of the groupbox, 
       connect its actions and Hide the other groupbox i.e. Rotate Compomnents groupbox and also 
       disconnect actions inside it"""
        
        self.toggle_groupbox(self.rotate_groupBoxButton, self.rotateGroupBox_widgetHolder)
                
        
    def setLastCheckedRotateAction(self, lastCheckedAction):
        """" Sets the  'last checked action value' Program remembers the last checked action 
        in a groupbox (either Translate or rotate (components)) . When that groupbox 
        is displayed, it checkes this last action again (see get method)"""
        self.lastCheckedRotateAction = lastCheckedAction
        
    def setLastCheckedMoveAction(self, lastCheckedAction):
        """" Sets the  'last checked action value' Program remembers the last checked action 
        in a groupbox (either Translate components or rotate components) . When that groupbox 
        is displayed, it checkes this last action again (see get method)"""
        self.lastCheckedMoveAction = lastCheckedAction
    
    def getLastCheckedRotateAction(self):
        """returns the last checked action in a groupbox."""
        if self.lastCheckedRotateAction:
            return self.lastCheckedRotateAction
        else:
            return None
        
    def getLastCheckedMoveAction(self):
        """returns the last checked action in a groupbox."""
        if self.lastCheckedMoveAction:
            return self.lastCheckedMoveAction
        else:
            return None
        
               
        
