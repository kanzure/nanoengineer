# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$

History:

ninad 070207 : created this file to manage 
Move and Rotate Property managers

"""
__author__  = "Ninad"

from PyQt4 import QtCore, QtGui
from Ui_MovePropertyManager import Ui_MovePropertyManager
from PropertyManagerMixin import PropertyManagerMixin, pmSetPropMgrIcon, pmSetPropMgrTitle
from PyQt4.Qt import Qt, SIGNAL
from Utility import geticon, getpixmap

TRANSLATE=1
ROTATE=2

class MovePropertyManager(QtGui.QWidget, 
                          PropertyManagerMixin, 
                          Ui_MovePropertyManager):
    
    # The title(s) that appears in the property manager header.
    translateTitle = "Translate"
    rotateTitle = "Rotate"

    # The full path to PNG file(s) that appears in the header.
    translateIconPath = "ui/actions/Properties Manager/Translate_Components.png"
    rotateIconPath = "ui/actions/Properties Manager/Rotate_Components.png"

    # The current move mode (either TRANSLATE or ROTATE).
    _currentMoveMode = TRANSLATE 
        
    def __init__(self, parentMode):
        QtGui.QWidget.__init__(self)
     
        self.parentMode = parentMode
	self.w = self.parentMode.w
	self.o = self.parentMode.o
	self.pw = self.parentMode.pw
	
        self.setupUi(self)	
	# Update the title and icon for "Translate" (the default move mode).
	pmSetPropMgrIcon( self, self.translateIconPath )
	pmSetPropMgrTitle( self, self.translateTitle )
        
        self.lastCheckedRotateAction = None 
        self.lastCheckedTranslateAction = None
          
        self.updateMessage()
        
        self.add_whats_this_text()
    
    def connect_or_disconnect_signals(self, connect):
	"""
	Connect the slots in Move Property Manager. 
	@see: modifyMode.connect_or_disconnect_signals.
	"""
	if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
	    
	change_connect(self.translate_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.activate_translateGroupBox_using_groupButton)  
	
        change_connect(self.rotate_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.activate_rotateGroupBox_using_groupButton)
        
        change_connect(self.movetype_combox, 
                     SIGNAL("currentIndexChanged(int)"), 
                     self.updateMoveGroupBoxItems)
	
        change_connect(self.rotatetype_combox, 
                     SIGNAL("currentIndexChanged(int)"), 
                     self.updateRotateGroupBoxItems)
	
        change_connect(self.w.MoveOptionsGroup, 
		       SIGNAL("triggered(QAction *)"), 
		       self.changeMoveOption)
	
        change_connect(self.w.rotateOptionsGroup, 
		       SIGNAL("triggered(QAction *)"), 
		       self.changeRotateOption)
        
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
	
        	
    
    def show_propMgr(self):
	"""
	Show Move Property Manager
	"""
	self.openPropertyManager(self)
    
    def activate_translateGroupBox_using_groupButton(self):
        """Show contents of this groupbox, deactivae the other groupbox. 
        Also check the action that was checked when this groupbox  was active
        last time. (if applicable). This method is called only when move 
        groupbox button is clicked. See also activate_translateGroupBox 
        method.
        """
        self._currentMoveMode = TRANSLATE
        self.updateMessage()
                
        self.toggle_translateGroupBox()
        
        if not self.w.toolsMoveMoleculeAction.isChecked():
            self.w.toolsMoveMoleculeAction.setChecked(True)
            self.o.setCursor(self.w.MolSelTransCursor)
            
            # Update the title and icon.
	    pmSetPropMgrIcon( self, self.translateIconPath )
	    pmSetPropMgrTitle( self, self.translateTitle )
            
            self.deactivate_rotateGroupBox()          
	    
	    actionToCheck = self.getTranslateActionToCheck()
              
            if actionToCheck:
                actionToCheck.setChecked(True) 
            else:
                actionToCheck = self.w.moveFreeAction
                actionToCheck.setChecked(True)
	    
	    self.changeMoveOption(actionToCheck)
	    
    
    def activate_rotateGroupBox_using_groupButton(self):
        """Show contents of this groupbox, deactivae the other groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable). This method is called only when rotate groupbox button 
        is clicked. See also activate_rotateGroupBox method. 
        """
        self._currentMoveMode = ROTATE
        self.updateMessage()
        
        self.toggle_rotateGroupBox()
        
        if not self.w.rotateComponentsAction.isChecked():            
            self.w.rotateComponentsAction.setChecked(True)           
            self.o.setCursor(self.w.MolSelRotCursor)

            # Update the title and icon.
	    pmSetPropMgrIcon( self, self.rotateIconPath )
	    pmSetPropMgrTitle( self, self.rotateTitle )
	    
            self.deactivate_translateGroupBox()
        
	    #Following implements NFR bug 2485.
	    #Earlier, it used to remember the last checked action 
	    #so this wasn't necessary	    
	    actionToCheck = self.getRotateActionToCheck()
	    				    
            if actionToCheck:		
                actionToCheck.setChecked(True) 
            else:
                actionToCheck = self.w.rotateFreeAction
                actionToCheck.setChecked(True)
	    
	    self.changeRotateOption(actionToCheck)
	
                    
    def activate_translateGroupBox(self):
        """Show contents of this groupbox, deactivae the other groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable) This action is called when toolsMoveMoleculeAction
        is checked from the toolbar or command manager. 
        see also: activate_translateGroupBox_using_groupButton
        """
        
        self._currentMoveMode = TRANSLATE
        self.updateMessage()
                
        self.toggle_translateGroupBox()
        self.o.setCursor(self.w.MolSelTransCursor)
        
	# Update the title and icon.
	pmSetPropMgrIcon( self, self.translateIconPath )
	pmSetPropMgrTitle( self, self.translateTitle )
	
        self.deactivate_rotateGroupBox()    
        
        #Following implements NFR bug 2485.
	#Earlier, it used to remember the last checked action 
	#so this wasn't necessary
	actionToCheck = self.getTranslateActionToCheck()
	
        if actionToCheck:
            actionToCheck.setChecked(True) 
        else:
            actionToCheck = self.w.moveFreeAction
            actionToCheck.setChecked(True)
	
	self.changeMoveOption(actionToCheck)
            
    def activate_rotateGroupBox(self):
        """Show contents of this groupbox, deactivae the other groupbox. 
        Also check the action that was checked when this groupbox  was active last
        time. (if applicable). This action is called when rotateComponentsAction
        is checked from the toolbar or command manager. 
        see also: activate_rotateGroupBox_using_groupButton
        """
        
        self._currentMoveMode = ROTATE
        self.updateMessage()
        
        self.toggle_rotateGroupBox()
        self.o.setCursor(self.w.MolSelRotCursor)

        # Update the title and icon.
	pmSetPropMgrIcon( self, self.rotateIconPath )
	pmSetPropMgrTitle( self, self.rotateTitle )
	
        self.deactivate_translateGroupBox()           
    	
        actionToCheck = self.getRotateActionToCheck() 
	
        if actionToCheck:
            actionToCheck.setChecked(True) 
        else:
            actionToCheck = self.w.rotateFreeAction
            actionToCheck.setChecked(True)
	
	self.changeRotateOption(actionToCheck)
        
                               
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
        
    def deactivate_translateGroupBox(self):
        """ Hide the items in the groupbox, Also 
        store the current checked action which will be checked again 
        when user activates this groupbox again. After storing 
        the checked action, uncheck it (so that other active groupbox 
        action can operate easily). """
        
        self.hideGroupBox(self.translate_groupBoxButton, self.translateGroupBox_widgetHolder) 
        
        #Store the last checked action of the groupbox you are about to close
        #(in this case Move Groupbox is the groupbox that will be deactivated and 
        #'Rotate groupbox will be activated (opened) ) 
        lastCheckedTranslateAction = self.w.MoveOptionsGroup.checkedAction()        
        self.setLastCheckedMoveAction(lastCheckedTranslateAction)        
        
        #Disconnect checked action in Move groupbox
        self.w.MoveOptionsGroup.checkedAction().setChecked(False)        
 
    def toggle_translateGroupBox(self):
        """ Toggles the item display in the parent groupbox of the button and 
       hides the other groupbox also disconnecting the actions in the other groupbox
       Example: If user clicks on Move groupbox button, it will toggle the display of the groupbox, 
       connect its actions and Hide the other groupbox i.e. Rotate Compomnents groupbox and also 
       disconnect actions inside it"""
        
        self.toggle_groupbox(self.translate_groupBoxButton, self.translateGroupBox_widgetHolder)              
        
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
        self.lastCheckedTranslateAction = lastCheckedAction
    
    def getLastCheckedRotateAction(self):
        """returns the last checked action in a groupbox."""
        if self.lastCheckedRotateAction:
            return self.lastCheckedRotateAction
        else:
            return None
        
    def getLastCheckedMoveAction(self):
        """returns the last checked action in a groupbox."""
        if self.lastCheckedTranslateAction:
            return self.lastCheckedTranslateAction
        else:
            return None
    
    def getRotateActionToCheck(self):
	''' Decide which rotate group box action to check 
	based on the last action that was checked in *translate* 
	groupbox
	@return <actionToCheck>:rotate action to be checked when rotate groupbox 
	is active (and when free drag rotate is chosen from the combo box)'''
	lastMoveAction =  self.getLastCheckedMoveAction()
	actionToCheck = None
	if lastMoveAction:
	    if lastMoveAction == self.w.transXAction:
		actionToCheck = self.w.rotXAction
	    elif lastMoveAction == self.w.transYAction:
		actionToCheck = self.w.rotYAction
	    elif lastMoveAction == self.w.transZAction:
		actionToCheck = self.w.rotZAction	
	    elif lastMoveAction == self.w.moveFreeAction:
		actionToCheck = self.w.rotateFreeAction
	    elif lastMoveAction == self.w.rotTransAlongAxisAction_1:
		actionToCheck = self.w.rotTransAlongAxisAction_2
	
	return actionToCheck
    
    def getTranslateActionToCheck(self):
	''' Decide which translate group box action to check 
	based on the last action that was checked in *rotate* groupbox.
	@return <actionToCheck>:translate action to be checked when translate 
	grpbx is active (and when free drag translate is chosen from the combo 
	box)'''
	
	lastRotateAction =  self.getLastCheckedRotateAction()
	actionToCheck = None
	if lastRotateAction:
	    if lastRotateAction == self.w.rotXAction:
		actionToCheck = self.w.transXAction
	    elif lastRotateAction == self.w.rotYAction:
		actionToCheck = self.w.transYAction
	    elif lastRotateAction == self.w.rotZAction:
		actionToCheck = self.w.transZAction
	    elif lastRotateAction == self.w.rotateFreeAction:
		actionToCheck = self.w.moveFreeAction
	    elif lastRotateAction == self.w.rotTransAlongAxisAction_2:
		actionToCheck = self.w.rotTransAlongAxisAction_1
	
	return actionToCheck
    
    def updateRotationDeltaLabels(self, rotateOption, rotationDelta):
        """ 
	Updates the Rotation Delta labels in the Rotate combobox  while rotating
        the selection around an axis
	"""
        
        if rotateOption == 'ROTATEX':
            listx = [self.lbl_x, self. deltaThetaX_lbl, 
                     self.degree_lbl_x]
            
            listyz = [self.deltaThetaY_lbl, self.deltaThetaZ_lbl, 
                      self.lbl_y, self.lbl_z, self.degree_lbl_y,
                      self.degree_lbl_z]            
            for lbl in listx:
                lbl.show()
                font = QtGui.QFont(lbl.font())
                font.setBold(True)
                lbl.setFont(font)
            self.deltaThetaX_lbl.setText(str(round(self.parentMode.rotDelta, 2)))
            for lbl in listyz:
                font = QtGui.QFont(lbl.font())
                font.setBold(False)
                lbl.setFont(font)
                lbl.show()
        elif rotateOption == 'ROTATEY':
            listy = [self.lbl_y, self. deltaThetaY_lbl, self.degree_lbl_y]
            listxz =[self.deltaThetaX_lbl, self.deltaThetaZ_lbl, 
                     self.lbl_x, self.lbl_z, self.degree_lbl_x, 
                     self.degree_lbl_z]
            for lbl in listy :
                font = QtGui.QFont(lbl.font())
                font.setBold(True)
                lbl.setFont(font)        
                lbl.show()
            self.deltaThetaY_lbl.setText(str(round(self.parentMode.rotDelta, 2)))
            for lbl in listxz:
                font = QtGui.QFont(lbl.font())
                font.setBold(False)
                lbl.setFont(font)
                lbl.show()
        elif rotateOption == 'ROTATEZ':
            listz = [self.lbl_z, self. deltaThetaZ_lbl, self.degree_lbl_z]
            listxy =  [ self.deltaThetaX_lbl, self.deltaThetaY_lbl, 
                        self.lbl_x, self.lbl_y, self.degree_lbl_x,
                        self.degree_lbl_y]
            for lbl in listz:
                font = QtGui.QFont(lbl.font())
                font.setBold(True)
                lbl.setFont(font)
                lbl.show()
            self.deltaThetaZ_lbl.setText(str(round(self.parentMode.rotDelta, 2)))
            for lbl in listxy:
                font = QtGui.QFont(lbl.font())
                font.setBold(False)
                lbl.setFont(font)   
                lbl.show()
        else:
            print "MovePropertyManager.updateRotationDeltaLabels: Error - unknown rotateOption value =", self.rotateOption
    
    def toggleRotationDeltaLabels(self, show=False):
        """ 
	Hide all the rotation delta labels when  
        rotateFreeDragAction is checked 
	"""
        lst = [self.lbl_y, self.lbl_z, self.lbl_x,
                   self.deltaThetaX_lbl, 
                   self.deltaThetaY_lbl, 
                   self.deltaThetaZ_lbl,
                   self.degree_lbl_x,
                   self.degree_lbl_y,
                   self.degree_lbl_z
                   ]
        if not show:            
            for lbl in lst:
                lbl.hide()    
        else:
            for lbl in lst:
                lbl.show()
		
    def changeMoveOption(self, action):
        """
	Change the translate option. 
	
	@param action: QAction that decides the type of translate operation 
	to be set.
        """
        if action == self.w.transXAction:
            moveOption = 'TRANSX'
        elif action == self.w.transYAction:
            moveOption = 'TRANSY'
        elif action == self.w.transZAction:
            moveOption = 'TRANSZ'
        elif action == self.w.rotTransAlongAxisAction_1:
            moveOption = 'ROT_TRANS_ALONG_AXIS' 
        else:
            moveOption = 'MOVEDEFAULT'
	
	self.parentMode.moveOption = moveOption
            
            
    def changeRotateOption(self, action):
        """
	Change the rotate option. 
	
	@param action: QAction that decides the type of rotate operation 
	to be set.
        """  
        if action == self.w.rotXAction:
            rotateOption = 'ROTATEX'
            self.rotateAsUnitCB.hide()
            self.toggleRotationDeltaLabels(show = True)
        elif action == self.w.rotYAction:
            rotateOption = 'ROTATEY'
            self.rotateAsUnitCB.hide()
            self.toggleRotationDeltaLabels(show = True)
        elif action == self.w.rotZAction:
            rotateOption = 'ROTATEZ'
            self.rotateAsUnitCB.hide()
            self.toggleRotationDeltaLabels(show = True)
        elif action == self.w.rotTransAlongAxisAction_2:
            #do not use the isConstrainedDrag.. flag. Causing bugs and 
            #am in a rush (need this new option for today's release) 
            #-- ninad20070605
            ##self.isConstrainedDragAlongAxis = True
            rotateOption = 'ROT_TRANS_ALONG_AXIS' 
            pass
        else:
            rotateOption = 'ROTATEDEFAULT'        
            #Hides all the rotation delta labels when  
            #rotateFreeDragAction is checked
            self.toggleRotationDeltaLabels(show = False)
            self.rotateAsUnitCB.show() 
	
	self.parentMode.rotateOption = rotateOption
    
    def set_move_xyz(self,x,y,z):
	"""
	Set values of X, Y and Z coordinates in the Move Property Manager.
	@param x: X coordinate of the common center of the selected objects
	@param y: Y coordinate of the common center of the selected objects
	@param z: Z coordinate of the common center of the selected objects
	"""
	self.moveXSpinBox.setValue(x)
	self.moveYSpinBox.setValue(y)
	self.moveZSpinBox.setValue(z)

    def get_move_xyz(self):
	"""
	Returns X, Y and Z values in the Move Property Manager. 
	@return : tuple (x, y, z) 
	"""
    
	x = self.moveXSpinBox.value()
	y = self.moveYSpinBox.value()
	z = self.moveZSpinBox.value()
	
	return (x,y,z)   
	
    def set_move_delta_xyz(self,delX, delY, delZ):
	"""
	Sets the values for 'move by distance delta' spinboxes 
	These are the values by which the selection will be translated 
	along the specified axes.
	@param delX: Delta X value 
	@param delY: Delta Y value
	@param delZ: Delta Z value
	
	"""
	self.moveDeltaXSpinBox.setValue(delX)
	self.moveDeltaYSpinBox.setValue(delY)
	self.moveDeltaZSpinBox.setValue(delZ)
    
    def get_move_delta_xyz(self, Plus = True):
	"""
	Returns the values for 'move by distance delta' spinboxes 
	@param Plus : Boolean that decides the sign of the return values. 
	(True returns positive values)
	@return : A tuple containing delta X, delta Y and delta Z values
	"""
     
	delX = self.moveDeltaXSpinBox.value()
	delY = self.moveDeltaYSpinBox.value()
	delZ = self.moveDeltaZSpinBox.value()
	
	if Plus: return (delX,delY,delZ) # Plus
	else: return (-delX, -delY, -delZ) # Minus
	
        
    def updateMessage(self): # Mark 2007-06-23
        """
	Updates the message box with an informative message.
        """
        
        from ops_select import objectSelected
        if objectSelected(self.o.assy):
            msg = ""
        else:
            msg = "Click on an object to select it."
        
        if self._currentMoveMode == TRANSLATE:
            msg += "Translate the current selection by holding down the \
                left mouse button (<b>LMB</b>) and dragging the cursor. \
                Translation options are availabe below."
        else:
            msg += "Rotate the current selection by holding down the \
                left mouse button (<b>LMB</b>) and dragging the cursor. \
                Rotate options are availabe below."

        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  True )
        
    def add_whats_this_text( self ):
        """What's This text for some of the widgets in the 
        Move Property Manager.
        """
        
        # Translate group box widgets ################################
	
        self.movetype_combox.setWhatsThis(
            """<b>Translation Options</b>
            <p>This menu provides different options for translating the
            current selection where:</p>
            <p>
            <b>Free Drag</b>: translates the selection by dragging the mouse
            while holding down the left mouse button (LMB).</p>
            <p>
	    <b>By Delta XYZ</b>: tranlates the selection by a specified 
	    offset.</p>
            <p>
	    <b>To XYZ Position</b>: moves the selection to an absolute XYZ
            coordinate. The <i>centroid</i> of the selection is used for
            this operation.
            </p>""")
        
        self.moveFreeButton.setWhatsThis(
            """<b>Unconstrained Translation</b>
            <p>Translates the selection freely within the plane of the screen.
            </p>""")
        
        self.transXButton.setWhatsThis(
            """<b>X Translation</b>
            <p>Constrains translation of the selection to the X axis.
            </p>""")
        
        self.transYButton.setWhatsThis(
            """<b>Y Translation</b>
            <p>Constrains translation of the selection to the Y axis.
            </p>""")
        
        self.transZButton.setWhatsThis(
            """<b>Z Translation</b>
            <p>Constrains translation of the selection to the Z axis.
            </p>""")
        
        self.rotTransAlongAxisButton_1.setWhatsThis(
            """<b>Axial Translation/Rotation</b>
            <p>Constrains both translation and rotation of the selection along
            the central axis of the selected object(s). This is especially
            useful for translating and rotating DNA duplexes along their
            own axis.
            </p>""")
	
	# By Delta XYZ widgets
	
        self.moveDeltaXSpinBox.setWhatsThis(
	    """<b>Delta X</b>
            <p>The X offset distance the selection is moved when 
	    clicking the +/- Delta buttons.
            </p>""")
	
	self.moveDeltaYSpinBox.setWhatsThis(
	    """<b>Delta Y</b>
            <p>The Y offset distance the selection is moved when 
	    clicking the +/- Delta buttons.
            </p>""")
	
	self.moveDeltaXSpinBox.setWhatsThis(
	    """<b>Delta Z</b>
            <p>The Z offset distance the selection is moved when 
	    clicking the +/- Delta buttons.
            </p>""")
	
	self.moveDeltaPlusButton.setWhatsThis(
	    """<b>Delta +</b>
            <p>Moves the current selection by an offset
	    specified by the Delta X, Y and Z spinboxes.
            </p>""")
	
	self.moveDeltaPlusButton.setToolTip(
	    "Move selection by + (plus) delta XYZ")
	
	self.moveDeltaMinusButton.setWhatsThis(
	    """<b>Delta -</b>
            <p>Moves the current selection by an offset opposite of that 
	    specified by the Delta X, Y and Z spinboxes.
            </p>""")
	
	self.moveDeltaPlusButton.setToolTip(
	    "Move selection by - (minus) delta XYZ")
	
	# To XYZ Position widgets
	
	self.moveXSpinBox.setWhatsThis(
	    """<b>X</b>
            <p>The X coordinate the selection is moved when 
	    clicking the +/- Delta buttons.
            </p>""")
	
	self.moveYSpinBox.setWhatsThis(
	    """<b>Y</b>
            <p>The Y coordinate the selection is moved when 
	    clicking the +/- Delta buttons.
            </p>""")
	
	self.moveZSpinBox.setWhatsThis(
	    """<b>Z</b>
            <p>The Z coordinate the selection is moved when 
	    clicking the <b>Move to Absolute Position</b> button.
            </p>""")
	
	self.moveAbsoluteButton.setWhatsThis(
	    """<b>Move to Absolute Position</b>
            <p>Moves the current selection to the position
	    specified by the X, Y and Z spinboxes. The selection's centroid
	    is used compute how the selection is moved.
            </p>""")
	
	self.moveAbsoluteButton.setToolTip(
	    "Move selection to absolute XYZ position")
	
	
        # Rotate group box widgets ############################
	
	self.rotatetype_combox.setWhatsThis(
            """<b>Rotate Options</b>
            <p>This menu provides different options for rotating the
            current selection where:</p>
            <p>
            <b>Free Drag</b>: rotates the selection by dragging the mouse
            while holding down the left mouse button (LMB).</p>
            <p>
	    <b>By Specified Angle</b>: rotates the selection by a specified 
	    angle.
            </p>""")
	
	# Free Drag widgets.
        
        self.rotateFreeButton.setWhatsThis(
            """<b>Unconstrained Rotation</b>
            <p>Rotates the selection freely about its centroid.
            </p>""")
        
        self.rotateXButton.setWhatsThis(
            """<b>X Rotation</b>
            <p>Constrains rotation of the selection to the X axis.
            </p>""")
        
        self.rotateYButton.setWhatsThis(
            """<b>Y Rotation</b>
            <p>Constrains rotation of the selection to the Y axis.
            </p>""")
        
        self.rotateZButton.setWhatsThis(
            """<b>Z Rotation</b>
            <p>Constrains rotation of the selection to the Z axis.
            </p>""")
        
        self.rotTransAlongAxisButton_2.setWhatsThis(
            """<b>Axial Translation/Rotation</b>
            <p>Constrains both translation and rotation of the selection along
            the central axis of the selected object(s). This is especially
            useful for translating and rotating DNA duplexes along their
            own axis.
            </p>""")
        
        self.rotateAsUnitCB.setWhatsThis(
            """<b>Rotate as unit</b>
            <p>When <b>checked</b>, the selection is rotated as a unit about its
            collective centroid.<br>
            When <b>unchecked</b>, the selected objects are rotated about their own
            individual centroids.
            </p>""")
	
	# By Specified Angle widgets
	
	self.rotateByThetaXButton.setWhatsThis(
	    """<b>Rotate about X axis</b>
	    <p>Constrains rotation about the X axis.
	    </p>""")
	
	self.rotateByThetaXButton.setToolTip(
	    "Rotate about X axis")
	
	self.rotateByThetaYButton.setWhatsThis(
	    """<b>Rotate about Y axis</b>
	    <p>Constrains rotation about the Y axis.
	    </p>""")
	
	self.rotateByThetaYButton.setToolTip(
	    "Rotate about Y axis")
	
	self.rotateByThetaZButton.setWhatsThis(
	    """<b>Rotate about Z axis</b>
	    <p>Constrains rotation about the Z axis.
	    </p>""")
	
	self.rotateByThetaZButton.setToolTip(
	    "Rotate about Z axis")
	
	self.rotateThetaSpinBox.setWhatsThis(
	    """<b>Rotation angle</b>
	    <p>Specifies the angle of rotation.
	    </p>""")
	
	self.rotateThetaSpinBox.setToolTip(
	    "Angle of rotation")
	
	# These next two aren't working. 
	# I don't understand why not. Mark 2007-06-25.
	self.rotateThetaPlusButton.setWhatsThis(
	    """<b>Rotate</b>
	    <p>Rotates the selection by the specified angle.
	    </p>""")
	
	self.rotateThetaMinusButton.setWhatsThis(
	    """<b>Rotate (minus)</b>
	    <p>Rotates the selection by the specified angle 
	    (in the opposite direction).
	    </p>""")
	    