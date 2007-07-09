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
        
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.setupUi(self)
	
	# Update the title and icon for "Translate" (the default move mode).
	pmSetPropMgrIcon( self, self.translateIconPath )
	pmSetPropMgrTitle( self, self.translateTitle )
        
        self.lastCheckedRotateAction = None 
        self.lastCheckedTranslateAction = None
               
        self.connect(self.translate_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.activate_translateGroupBox_using_groupButton)            
        self.connect(self.rotate_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.activate_rotateGroupBox_using_groupButton)
        
        self.connect(self.movetype_combox, 
                     SIGNAL("currentIndexChanged(int)"), 
                     self.updateMoveGroupBoxItems)
        self.connect(self.rotatetype_combox, 
                     SIGNAL("currentIndexChanged(int)"), 
                     self.updateRotateGroupBoxItems)
        
        
        self.updateMessage()
        
        self.add_whats_this_text()
    
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
	    #@@ the following method is in modifyMode. Needs cleanup
	    #each mode should make its propMgr object (cleanup proces)
	    #In that case , the following will become, for example, 
	    #self.parent.changeMoveOption Or the changeMoveOption methode 
	    #itself can be moved in this class (at present a bit of work 
	    #because of other things that depend on it. -- ninad 20070605
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
	    #@@ the following method is in movodifyMode. Needs cleanup
	    #each mode should make its propMgr object (cleanup proces)
	    #In that case , the follwing will become, for example, 
	    #self.parent.changeRotateOption Or the changeRotateOption methode 
	    #itself can be moved in this class (at present a bit of work 
	    #because of other things that depend on it. -- ninad 20070605
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
	    
	#@@ the following method is in modifyMode. Needs cleanup
	#each mode should make its propMgr object (cleanup proces)
	#In that case , the following will become, for example, 
	#self.parent.changeMoveOption Or the changeMoveOption methode 
	#itself can be moved in this class (at present a bit of work 
	#because of other things that depend on it. -- ninad 20070605
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
	
	#@@ the following method is in movodifyMode. Needs cleanup
	#each mode should make its propMgr object (cleanup proces)
	#In that case , the follwing will become, for example, 
	#self.parent.changeRotateOption Or the changeRotateOption methode 
	#itself can be moved in this class (at present a bit of work 
	#because of other things that depend on it. -- ninad 20070605
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
        
    def updateMessage(self): # Mark 2007-06-23
        """Updates the message box with an informative message.
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
	    