# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
FusePropertyManager.py
@author: Ninad
@version: $Id$
@copyright:2004-2007 Nanorex, Inc.  All rights reserved.

History: 
ninad070425 :1) Moved Fuse dashboard to Property manager 
             2) Implemented Translate/ Rotate enhancements
	     
ninad20070723: code cleanup to define a fusePropMgr object. This was a 
prerequisite for 'command sequencer' and also needed to resolve potential 
multiple inheritance issues.

TODO: ninad20070723--
See if the signals can be connected in the 
fuseMde.connect_disconnect_signals OR better to call 
propMgr.connect_disconnect_signals in the fuseMde.connect_disconnect_signals?  
I think the latter will help decoupling ui elements from fuseMode. Same thing 
applies to other modes and Propert Managers (e.g. Move mode, Build Atoms mode)
"""
__author__  = "Ninad"

from PyQt4.Qt import SIGNAL

from PropertyManagerMixin   import  PropertyManagerMixin
from PropertyManagerMixin   import  pmSetPropMgrIcon, pmSetPropMgrTitle
from Ui_FusePropertyManager import  Ui_FusePropertyManager
from MovePropertyManager    import  MovePropertyManager

from ops_select             import  objectSelected


class FusePropertyManager(MovePropertyManager):
    
    # <title> - the title that appears in the property manager header.
    title = "Fuse Chunks"
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Tools/Fuse_Chunks.png"
    
    def __init__(self, parentMode):
	
	self.parentMode = parentMode
        MovePropertyManager.__init__(self, self.parentMode)
        # setupUi() did not add the icon or title. We do that here.
	pmSetPropMgrIcon( self, self.iconPath )
        pmSetPropMgrTitle( self, self.title )
        
        #At startup Move groupbox is active by default 
        #the following variable sets this flag (used in fusechunksMode.leftDrag)
        self.isMoveGroupBoxActive = True
        self.o.setCursor(self.w.MolSelTransCursor)
        
        
        self.showGroupBox(self.translate_groupBoxButton, 
                          self.translateGroupBox_widgetHolder)        
        self.hideGroupBox(self.rotate_groupBoxButton, 
                          self.rotateGroupBox_widgetHolder) 
    
    def connect_or_disconnect_signals(self, connect):
	"""
	Connect the slots in Fuse Property Manager. 
	@see: fusechunksMode.connect_or_disconnect_signals.
	"""
	if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
	
	#connect slots
	
	change_connect(self.goPB,
		       SIGNAL("clicked()"),
		       self.parentMode.fuse_something)
	
        change_connect(self.toleranceSL,
		       SIGNAL("valueChanged(int)"),
                       self.parentMode.tolerance_changed)        
        
        change_connect(self.fuse_mode_combox, 
                       SIGNAL("activated(const QString&)"), 
                       self.parentMode.change_fuse_mode)
        
        change_connect(self.w.moveDeltaPlusAction, 
		       SIGNAL("activated()"), 
                       self.parentMode.moveDeltaPlus)
	
        change_connect(self.w.moveDeltaMinusAction, 
		       SIGNAL("activated()"), 
                       self.parentMode.moveDeltaMinus)
	
        change_connect(self.w.moveAbsoluteAction, 
		       SIGNAL("activated()"), 
                       self.parentMode.moveAbsolute)
	
        change_connect(self.w.rotateThetaPlusAction, 
		       SIGNAL("activated()"),
                       self.parentMode.moveThetaPlus)        
	
        change_connect(self.w.rotateThetaMinusAction, 
		       SIGNAL("activated()"),                        
                       self.parentMode.moveThetaMinus)
        
	change_connect(self.w.MoveOptionsGroup, 
                       SIGNAL("triggered(QAction *)"), 
		       self.changeMoveOption)
	
        change_connect(self.w.rotateOptionsGroup, 
                       SIGNAL("triggered(QAction *)"), 
		       self.changeRotateOption)
	
        change_connect(self.sponsor_btn,
                     SIGNAL("clicked()"),
                     self.sponsor_btn_clicked)
        
        change_connect(self.translate_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.activate_translateGroupBox_in_fuse_PM)   
	
        change_connect(self.rotate_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.activate_rotateGroupBox_in_fuse_PM)
	
	change_connect(self.fuseOptions_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_fuseOptionsGroupBox)
        
        
	change_connect(self.movetype_combox, 
		     SIGNAL("currentIndexChanged(int)"), 
		     self.updateMoveGroupBoxItems)
	
	change_connect(self.rotatetype_combox, 
		     SIGNAL("currentIndexChanged(int)"), 
		     self.updateRotateGroupBoxItems)
	
    
        
    def activate_translateGroupBox_in_fuse_PM(self):
        """Show contents of translate groupbox, deactivae the rotate groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable). This method is called only when move groupbox button 
        is clicked. See also activate_translateGroupBox_in_fuse_PM method . 
        """
                      
	self.toggle_translateGroupBox()
	self.o.setCursor(self.w.MolSelTransCursor)
	self.deactivate_rotateGroupBox()
       
        actionToCheck = self.getTranslateActionToCheck()
                     
        if actionToCheck:
            actionToCheck.setChecked(True) 
        else:
            actionToCheck = self.w.moveFreeAction
            actionToCheck.setChecked(True)
	
	self.changeMoveOption(actionToCheck)
        
        self.isMoveGroupBoxActive = True
    
    def activate_rotateGroupBox_in_fuse_PM(self):
        """Show contents of rotate groupbox (in fuse PM), deactivae the 
        #translate groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable). This method is called only when rotate groupbox button 
        is clicked. See also activate_rotateGroupBox_in_fuse_PM method. 
        """
     
	self.toggle_rotateGroupBox()
	self.o.setCursor(self.w.MolSelRotCursor)
	self.deactivate_translateGroupBox()
                
        actionToCheck = self.getRotateActionToCheck()
                  
        if actionToCheck:
            actionToCheck.setChecked(True) 
        else:
            actionToCheck = self.w.rotateFreeAction
            actionToCheck.setChecked(True)
	    
	self.changeRotateOption(actionToCheck)
        
        self.isMoveGroupBoxActive = False
	
        
    def toggle_fuseOptionsGroupBox(self):
        '''Toggles the item display in the parent groupbox of the button'''
        
        self.toggle_groupbox(self.fuseOptions_groupBoxButton,
                             self.fuseOptions_widgetHolder)  
    
    def show_propMgr(self):
	"""
	Show the Fuse Property Manager.
	"""
	self.openPropertyManager(self)
	
    
    def setupUi(self, fusePropMgrObject):
	"""
	Overrides MovePropertyManager.setupUi
	@param fusePropMgrObject : fuse PM object is passed to the 
	                           Ui_FusePropertyManager class method which 
				   defines the necessary ui elements for 
				   Fuse Property Manager
	@see : MovePropertyManager.setupUI
	"""
	fusePropMgr = fusePropMgrObject
	fuseUi = Ui_FusePropertyManager()
	fuseUi.setupUi(fusePropMgr)
    
    def updateMessage(self): 
        """
	Updates the message box with an informative message.
	Overrides the MovePropertyManager.updateMessage method
	@see: MovePropertyManager.updateMessage
        """
	
	#@bug: BUG: The message box height is fixed. The verticle scrollbar appears 
	#as the following message is long. It however tries to make the cursor 
	#visible within the message box . This results in scrolling the msg box
	#to the last line and thus doesn't look good. I think once we migrate to
	#PropertyManagerBaseClass, this will go away -- ninad 20070723
	
	if self.fuse_mode_combox.currentIndex() == 0:
	    #i.e. 'Make Bonds Between Chunks'
	    msg = "To <b> make bonds</b> between two or more chunks, \
	    drag the selected chunk(s) such that their one or more bondpoints \
	    overlap with the other chunk(s). Then hit <b> Make Bonds </b> to \
	    create bond(s) between them. "
	else:	
	    msg = "To <b>fuse overlapping atoms</b> in two or more chunks,\
	    drag the selected chunk(s) such that their one or more atoms overlap \
	    with the atoms in the other chunk(s). Then hit <b> Fuse Atoms </b>\
	    to remove the overlapping atoms of unselected chunk. "
	
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  True )
	