# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
modifyMode.py

$Id$

bruce 050913 used env.history in some places.

"""

import math
from Numeric import dot, sign

from PyQt4 import QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import QComboBox
from PyQt4.Qt import QLabel
from PyQt4.Qt import QCheckBox
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QMouseEvent

import changes
import platform
import env

from selectMode import selectMode
from selectMolsMode import selectMolsMode
from selectAtomsMode import selectAtomsMode
from widgets import FloatSpinBox
from utilities.Log import redmsg

from MovePropertyManager import MovePropertyManager
from chem import Atom
from bonds import Bond
from jigs import Jig
from modes import basicMode
from icon_utilities import geticon

from debug import print_compact_traceback

from constants import START_NEW_SELECTION
from constants import DELETE_SELECTION
from constants import SUBTRACT_FROM_SELECTION
from constants import ADD_TO_SELECTION

from VQT import V, Q, A, norm, vlen


class modifyMode(selectMolsMode): # changed superclass from basicMode to selectMolsMode.  mark 060301.
    "[bruce comment 040923:] a transient mode entered from selectMode in response to certain mouse events"

    # class constants
    gridColor = 52/255.0, 128/255.0, 26/255.0
    modename = 'MODIFY'
    default_mode_status_text = "Mode: Move Chunks"
    
    MOVEOPTS = [ 'MOVEDEFAULT', 'TRANSX', 'TRANSY', 'TRANSZ' ]
    
    # class variables
    moveOption = 'MOVEDEFAULT'
    rotateOption = 'ROTATEDEFAULT'
    axis = 'X'
    RotationOnly = False
    TranslationOnly = False
    
    propMgr = None
    pw = None
    
    # no __init__ method needed

    def Enter(self):
	
        #Initialize the flag for Constrained translation and rotation
        #along the axis of the chunk to False. This flag is set 
        #to True whenever keyboard key 'A' is pressed 
        #while in Translate/Rotate mode. See methods keyPress, keyRelease, 
        #leftDown, Drag and leftADown, Drag for details. 
        self.isConstrainedDragAlongAxis = False
	
        selectMolsMode.Enter(self) 
        self.o.assy.selectChunksWithSelAtoms()
        self.dragdist = 0.0
	self.clear_leftA_variables() #bruce 070605 precaution
        return
    
    # (see basicMode.Done.__doc__ for the ones we don't override here [bruce 040923])

    def init_gui(self):	
	
	if not self.propMgr:
	    self.propMgr = MovePropertyManager(self)
	    #@bug BUG: following is a workaround for bug 2494
	    changes.keep_forever(self.propMgr)
		
	self.propMgr.show()                	
	self.updateCommandManager(bool_entering = True)
    
        # connect signals (these all need to be disconnected in restore_gui)                
        self.connect_or_disconnect_signals(True)
                        
        self.propMgr.set_move_xyz(0, 0, 0) # Init X, Y, and Z to zero
        self.propMgr.set_move_delta_xyz(0,0,0) # Init DelX,DelY, DelZ to zero

       
        self.moveOption = 'MOVEDEFAULT'
        self.rotateOption = 'ROTATEDEFAULT'
    
    def connect_or_disconnect_signals(self, connect): # mark 060304.
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
        
	change_connect(self.exitMoveAction, SIGNAL("triggered()"), 	 
	                        self.w.toolsDone)
	
	self.propMgr.connect_or_disconnect_signals(connect)
        
    def restore_gui(self):
        # disconnect signals which were connected in init_gui [bruce 050728]
	self.updateCommandManager(bool_entering = False)
        self.w.toolsMoveMoleculeAction.setChecked(False) # toggle on the Move Chunks icon
        self.w.rotateComponentsAction.setChecked(False)
        self.connect_or_disconnect_signals(False)        
	if self.propMgr:	    
	    self.propMgr.close()
    
    def moveFromToTemporaryMode_NOT_IMPLEMENTED(self):
	"""
	Temporary code not implemented yet
	"""
	if 0:	
	    print "currentCommand.modename ="
	    commandSequencer = self.commandSequencer
	    currentCommand = commandSequencer.currentCommand
	    
	    if currentCommand.modename != "MouseClickPointAcceptor_TempMode":
		    commandSequencer.userEnterTemporaryCommand(
			'MouseClickPointAcceptor_TempMode')
		    return
	    else:
		print "currentCommand.modename == "\
		      "MouseClickPointAcceptor_TempMode"
	
    
    def getFlyoutActionList(self): #Ninad 20070618
	""" Returns a tuple that contains mode spcific actionlists in the 
	added in the flyout toolbar of the mode. 
	CommandManager._createFlyoutToolBar method calls this 
	@return: params: A tuple that contains 3 lists: 
	(subControlAreaActionList, commandActionLists, allActionsList)"""	
		
	#'allActionsList' returns all actions in the flyout toolbar 
	#including the subcontrolArea actions
	allActionsList = []
	
	#Action List for  subcontrol Area buttons. 
	#In this mode, there is really no subcontrol area. 
	#We will treat subcontrol area same as 'command area' 
	#(subcontrol area buttons will have an empty list as their command area 
	#list). We will set  the Comamnd Area palette background color to the
	#subcontrol area.
	
	subControlAreaActionList =[] 
		
	self.exitMoveAction = QtGui.QWidgetAction(self.w)
	self.exitMoveAction.setText("Exit Move")
	self.exitMoveAction.setCheckable(True)
	self.exitMoveAction.setChecked(True)
	self.exitMoveAction.setIcon(geticon("ui/actions/Toolbars/Smart/Exit"))
	subControlAreaActionList.append(self.exitMoveAction)
	
	separator = QtGui.QAction(self.w)
	separator.setSeparator(True)
	subControlAreaActionList.append(separator) 
	
	subControlAreaActionList.append(self.w.toolsMoveMoleculeAction)
	subControlAreaActionList.append(self.w.rotateComponentsAction)
	subControlAreaActionList.append(self.w.modifyAlignCommonAxisAction)
		
	allActionsList.extend(subControlAreaActionList)
	
	#Empty actionlist for the 'Command Area'
	commandActionLists = [] 
	
	#Append empty 'lists' in 'commandActionLists equal to the 
	#number of actions in subControlArea 
	for i in range(len(subControlAreaActionList)):
	    lst = []
	    commandActionLists.append(lst)
	    	
	params = (subControlAreaActionList, commandActionLists, allActionsList)
	
	return params
	
    
    def updateCommandManager(self, bool_entering = True):#Ninad 20070618
	''' Update the command manager '''
	if bool_entering:
	    try:
		action = self.w.toolsMoveRotateActionGroup.checkedAction()
	    except:
		print_compact_traceback("bug: no move action checked?")
		action = None
	else: 
	    action = None
	
	# object that needs its own flyout toolbar. In this case it is just 
	#the mode itself. 
	obj = self  
	    	    
	self.w.commandManager.updateCommandManager(action,
						   obj, 
						   entering = bool_entering)
    
        
    def keyPress(self,key):           
        basicMode.keyPress(self, key)        
        # For these key presses, we toggle the Action item, which will send 
        # an event to changeMoveMode, where the business is done.
        # Mark 050410

        # If Key 'A' is pressed, set the flag for Constrained translation and rotation
        # along the axis of the chunk; otherwise reset that flag
        # [REVIEW: is that resetting good, for any key at all?? If so, document why. bruce comment 071012]
        if key == Qt.Key_A:
            self.isConstrainedDragAlongAxis = True 
        else:
            self.isConstrainedDragAlongAxis = False 
        
        self.update_cursor()
            
                
    def keyRelease(self,key):
        basicMode.keyRelease(self, key)        
    
        if key in [Qt.Key_X, Qt.Key_Y, Qt.Key_Z, Qt.Key_A]:
            self.movingPoint = None # Fixes bugs 583 and 674 along with change in leftDrag().  Mark 050623
        elif key == Qt.Key_R:
            self.RotationOnly = False # Unconstrain translation.
        elif key == Qt.Key_T:
            self.TranslationOnly = False # Unconstrain rotation.
        
        #Set the flag for Constrained translation and rotation
        #along the axis of the chunk to False
        self.isConstrainedDragAlongAxis = False 
        self.update_cursor()
            
    def update_cursor_for_no_MB(self):
        '''Update the cursor for 'Move Chunks' mode.
        '''
	
	#No need to proceed further if the propMgr is not initialized. 
	#The cursor to set will be decided by the active groupbox in the
	#property manager. 
	
	if self.propMgr is None:
	    return

        if self.o.modkeys is None:
            if self.isConstrainedDragAlongAxis:
                self.o.setCursor(self.w.MolSelAxisRotTransCursor)
            else:
		if self.propMgr.isTranslateGroupBoxActive:
		    self.o.setCursor(self.w.MolSelTransCursor)
		else:
		    self.o.setCursor(self.w.MolSelRotCursor)		    
        elif self.o.modkeys == 'Shift':
            if self.propMgr.isTranslateGroupBoxActive:
                self.o.setCursor(self.w.MolSelTransAddCursor)
            else:
                self.o.setCursor(self.w.MolSelRotAddCursor)
        elif self.o.modkeys == 'Control':
            if self.propMgr.isTranslateGroupBoxActive:
                self.o.setCursor(self.w.MolSelTransSubCursor)
            else:
                self.o.setCursor(self.w.MolSelRotSubCursor)  
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB(): Invalid modkey=", self.o.modkeys
        
        return
           
    def leftDown(self, event):
        """
	Handle left down event. Preparation for dragging and/or selection
	@param event: The mouse left down event.
	@type  event: QMouseEvent instance
	@see: self.leftDownForTranslatation
	@see: self.leftDownForRotation
        """
	#The following variable stores a string. It is used in leftDrag related 
	#methods to handle cases where the user may do a keypress *while* left 
	#dragging, which would change the move type. This variable is assigned a 
	#string value.See self.leftDownForTranslatation for an example. 
	self.leftDownType = None
	
        self.clear_leftA_variables() #bruce 070605 added this (guess at what's needed)
        env.history.statusbar_msg("")

        # If keyboard key 'A' is pressed, set it up for constrained translation
        #and rotation along the axis and return. 
	if self.isConstrainedDragAlongAxis:
	    self.leftADown(event)
	    return
        		    		    
        self.reset_drag_vars()
	        
        self.LMB_press_event = QMouseEvent(event) # Make a copy of this event and save it. 
        # We will need it later if we change our mind and start selecting a 2D region in leftDrag().
        # Copying the event in this way is necessary because Qt will overwrite <event> later (in 
        # leftDrag) if we simply set self.LMB_press_event = event.  mark 060220
        
        self.LMB_press_pt_xy = (event.pos().x(), event.pos().y())
	# <LMB_press_pt_xy> is the position of the mouse in window coordinates when the LMB was pressed.
	# Used in mouse_within_stickiness_limit (called by leftDrag() and other methods).
	# We don't bother to vertically flip y using self.height (as mousepoints does),
	# since this is only used for drag distance within single drags.
	    	
	if self.propMgr.isTranslateGroupBoxActive:
	    self.leftDownForTranslation(event)	    
	else:
	    self.leftDownForRotation(event)
	
	# Permit movable object picking upon left down.             
	
	obj = self.get_obj_under_cursor(event)
	# If highlighting is turned on, get_obj_under_cursor() returns atoms, 
	# singlets, bonds, jigs,
	# or anything that can be highlighted and end up in glpane.selobj. 
	# [bruce revised this comment, 060725]If highlighting is turned off, 
	# get_obj_under_cursor() returns atoms and singlets (not bonds or jigs).
	# [not sure if that's still true -- probably not. bruce 060725 addendum]
	if obj is None: # Cursor over empty space.
	    self.emptySpaceLeftDown(event)
	    return	
	
	self.doObjectSpecificLeftDown(obj, event)
	
	self.w.win_update()
	return
	
	        
    def leftDownForRotation(self, event):	
	""" 
	Handle left down event. Preparation for rotation and/or selection
	@param event: The mouse left down event.
	@type  event: QMouseEvent instance
	@see: self.leftDown
	@see: self.leftDragRotation
	
	"""
	
	self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0	
	# delta for constrained rotations.
	self.rotDelta = 0 
		
	if self.rotateOption == 'ROTATEDEFAULT':
	    self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
	else:
	    if self.rotateOption == 'ROTATEX': 
		ma = V(1,0,0) # X Axis
		self.axis = 'X'
	    elif self.rotateOption == 'ROTATEY': 
		ma = V(0,1,0) # Y Axis
		self.axis = 'Y'
	    elif self.rotateOption == 'ROTATEZ': 
		ma = V(0,0,1) # Z Axis
		self.axis = 'Z'
	    elif self.rotateOption == 'ROT_TRANS_ALONG_AXIS':
		self.leftADown(event)
		return
		
	    else: 
		print "modifyMode: Error - unknown rotateOption value =", \
		      self.rotateOption
		return
	    
	    ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
	    # When in the front view, right = 1,0,0 and up = 0,1,0, so ma will 
	    # be computed as 0,0.This creates a special case problem when the 
	    # user wants to constrain rotation around the Z axis because Zmat 
	    # will be zero.  So we have to test for this case (ma = 0,0) and
	    # fix ma to -1,0.  This was needed to fix bug 537.  Mark 050420
	    if ma[0] == 0.0 and ma[1] == 0.0: 
		ma = [-1.0, 0.0] 
	    self.Zmat = A([ma,[-ma[1],ma[0]]])
			
	self.leftDownType = 'ROTATE'
	
	return
    
    def leftDownForTranslation(self, event):
	""" 
	Handle left down event. Preparation for translation and/or selection
	@param event: The mouse left down event.
	@type  event: QMouseEvent instance
	@see: self.leftDown
	@see: self.leftDragTranslation
	
	"""
	self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0
        self.transDelta = 0 # X, Y or Z deltas for translate.        
        self.moveOffset = [0.0, 0.0, 0.0] # X, Y and Z offset for move.        
       
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)	
	# Following is in leftDrag() to compute move offset during drag op.
        self.startpt = self.movingPoint 
                
        # Translate section     
                    
	if self.moveOption != 'MOVEDEFAULT':
	    if self.moveOption == 'TRANSX': 
		ma = V(1,0,0) # X Axis
		self.axis = 'X'
	    elif self.moveOption == 'TRANSY': 
		ma = V(0,1,0) # Y Axis
		self.axis = 'Y'
	    elif self.moveOption == 'TRANSZ': 
		ma = V(0,0,1) # Z Axis
		self.axis = 'Z'
	    elif self.moveOption == 'ROT_TRANS_ALONG_AXIS':
		self.leftADown(event)
		return
	    else: print "modifyMode: Error - unknown moveOption value =", self.moveOption
	    
	    ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
	    # When in the front view, right = 1,0,0 and up = 0,1,0, so ma will be computed as 0,0.
	    # This creates a special case problem when the user wants to constrain rotation around
	    # the Z axis because Zmat will be zero.  So we have to test for this case (ma = 0,0) and
	    # fix ma to -1,0.  This was needed to fix bug 537.  Mark 050420
	    if ma[0] == 0.0 and ma[1] == 0.0: ma = [-1.0, 0.0] 
	    self.Zmat = A([ma,[-ma[1],ma[0]]])
	    
	    # end of Translate section
                               	
	self.leftDownType = 'TRANSLATE'
	
	return
    
            
    def leftDrag(self, event):
        """
	Translate or Rotate the selected object(s):
        - in the plane of the screen following the mouse, 
        - or slide and rotate along the an axis
	
	@param event: The mouse left drag event. 
	@type  event: QMouseEvent instance
	@see : self.leftDragTranslation
	@see : self.leftDragRotation
        """
		            
 
	if self.cursor_over_when_LMB_pressed == 'Empty Space':            
	    ##self.continue_selection_curve(event)             
	    self.emptySpaceLeftDrag(event)
	    return
	
	if self.o.modkeys is not None:
            #@see : comment related to this condition in selectMolsMode.leftDrag
            self.emptySpaceLeftDown(self.LMB_press_event)
            return
	
	if not self.picking:
	    return
	
	if not self.o.assy.getSelectedMovables():
	    return
	
	if self.isConstrainedDragAlongAxis:
	    try:
		self.leftADrag(event)
		return
	    except:
		# this might be obsolete, since leftADrag now tries to handle 
		#this (untested) [bruce 070605 comment]
		print "Key A pressed after Left Down. controlled translation will not be performed"
		pass
	
	if self.propMgr.isTranslateGroupBoxActive:
	    if self.leftDownType in ['TRANSLATE', 'A_TRANSLATE']:
		try:
		    self.leftDragTranslation(event)
		    return
		except:	   
		    msg1 = "Controlled translation not allowed. "
		    msg2 = "Key must be pressed before starting the drag"
		    env.history.statusbar_msg(msg1 + msg2)
		    if platform.atom_debug:
			msg3 = "Error occured in modifyMode.leftDragTranslation."
			msg4 = "Possibly due to a key press that activated. "
			msg5 = "Rotate groupbox. Aborting drag operation"
			print_compact_traceback(msg3 + msg4 + msg5)
		    pass
		    		
	else:
	    if self.leftDownType in ['ROTATE', 'A_ROTATE']:
		try:
		    self.leftDragRotation(event)  
		    return
		except:
		    msg1 = "Controlled rotation not allowed. "
		    msg2 = "Key must be pressed before starting the drag"
		    env.history.statusbar_msg(msg1 + msg2)
		    if platform.atom_debug:
			msg3 = "Error occured in modifyMode.leftDragRotation."
			msg4 = "Possibly due to a key press that activated. "
			msg5 = "Translate groupbox. Aborting drag operation"
			print_compact_traceback(msg3 + msg4 + msg5)
		    pass 
                               
    # end of leftDrag    
    
    def leftDragTranslation(self, event):
	"""
	Translate the selected object(s):
        - in the plane of the screen following the mouse, 
        - or slide and rotate along the an axis
	
	@param event: The mouse left drag event. 
	@note : This method is partially duplicated (free drag translate code)
	in selectMolsMode.pseudoMoveModeLeftDrag 
	@see : self.leftDrag
	"""
	#TODO: Further cleanup of this method and also for
	# selectMolsMode.pseudoMoveModeLeftDrag. Need to move some common code
	#in this method to self.leftDrag. Lower priority -- ninad 20070727
	
	if self.propMgr.translateComboBox.currentText() != "Free Drag":
	    return
	     
	# Fixes bugs 583 and 674 along with change in keyRelease.  Mark 050623
	# Fix per Bruce's email.  Mark 050704
        if self.movingPoint is None: self.leftDown(event) 
                       
	
	if self.moveOption == 'ROT_TRANS_ALONG_AXIS':
	    try:
		self.leftADrag(event)
	    except:
		print_compact_traceback(" error doing leftADrag")		
	    return	
	# Move section
	if self.moveOption == 'MOVEDEFAULT':	    
	    deltaMouse = V(event.pos().x() - self.o.MousePos[0],
		       self.o.MousePos[1] - event.pos().y(), 0.0)
	    
	    #bruce 060316 replaced old code with dragto (equivalent)
	    point = self.dragto( self.movingPoint, event) 
	    # Print status bar msg indicating the current move delta.
	    self.moveOffset = point - self.startpt # Fixed bug 929.  mark 060111
	    msg = "Offset: [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.moveOffset[0], 
							     self.moveOffset[1], 
							     self.moveOffset[2])
	    
	    env.history.statusbar_msg(msg)
	    self.o.assy.movesel(point - self.movingPoint)
	    self.movingPoint = point    
	    # end of Move section
	
	# Translate section
	else:
	    w=self.o.width+0.0
	    h=self.o.height+0.0
	    deltaMouse = V(event.pos().x() - self.o.MousePos[0],
		       self.o.MousePos[1] - event.pos().y())
	    a =  dot(self.Zmat, deltaMouse)
	    dx,dy =  a * V(self.o.scale/(h*0.5), 2*math.pi/w)
	    if self.moveOption == 'TRANSX':
		ma = V(1,0,0) # X Axis
	    elif self.moveOption == 'TRANSY':
		ma = V(0,1,0) # Y Axis
	    elif self.moveOption == 'TRANSZ':
		ma = V(0,0,1) # Z Axis
	    else: 
		print "modifyMode.leftDrag Error: unknown moveOption value:", \
		self.moveOption                
		return
   
	    self.transDelta += dx # Increment translation delta  
	    self.o.assy.movesel(dx*ma)
	    
	# Print status bar msg indicating the current translation delta
        if self.o.assy.selmols:
	    msg = "%s delta: [%.2f Angstroms] [0 Degrees]" % (self.axis, 
							      self.transDelta)
            env.history.statusbar_msg(msg)

	# common finished code
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()
	
	return
    
    def leftDragRotation(self, event):
	"""
	Rotate the selected object(s) or slide and rotate along the an axis
	
	@param event: The mouse left drag event.
	@type  event: QMouseEvent object
	@see : self.leftDrag
	"""
	
	if self.propMgr.rotateComboBox.currentText() != "Free Drag":
	    return
	
	if self.rotateOption == 'ROTATEDEFAULT':
	    ##self.leftCntlDrag(event)
	    self.leftDragFreeRotation(event)
	    return 
	
	if self.rotateOption == 'ROT_TRANS_ALONG_AXIS':
	    try:
		self.leftADrag(event)
	    except:
		print_compact_traceback(" error doing leftADrag")
	    
	    return
	
	#Rotate section      
	w=self.o.width+0.0
	h=self.o.height+0.0
	
	deltaMouse = V(event.pos().x() - self.o.MousePos[0],
		   self.o.MousePos[1] - event.pos().y())
	
	a =  dot(self.Zmat, deltaMouse)
	dx,dy =  a * V(self.o.scale/(h*0.5), 2*math.pi/w) 
	
	if self.rotateOption == 'ROTATEX':
	    ma = V(1,0,0) # X Axis
	elif self.rotateOption == 'ROTATEY':
	    ma = V(0,1,0) # Y Axis
	elif self.rotateOption == 'ROTATEZ':
	    ma = V(0,0,1) # Z Axis
	else: 
	    print "modifyMode.leftDrag Error: unknown rotateOption value:",\
		  self.rotateOption   
	    return             
	
	qrot = Q(ma,-dy) # Quat for rotation delta.
	# Increment rotation delta (and convert to degrees)
	self.rotDelta += qrot.angle *180.0/math.pi * sign(dy) 
	
	self.propMgr.updateRotationDeltaLabels(self.rotateOption, 
					       self.rotDelta)
	self.o.assy.rotsel(qrot) 
	
	# Print status bar msg indicating the current rotation delta.
        if self.o.assy.selmols:
            msg = "%s delta: [0 Angstroms] [%.2f Degrees]" % (self.axis, 
							      self.rotDelta)
            env.history.statusbar_msg(msg)
	
	# common finished code
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()
	
	#End of Rotate Section
	
	return    
    
    def leftDragFreeRotation(self, event):
        """
	Does an incremental trackball action (free drag rotation)on all selected 
	movables. 
		
	@param event: The mouse left drag event. 
	@type  event: QMouseEvent instance
	@see : self.leftDragRotation
		
        """
        #Note: In Alpha 9.1 and before, this operation was done by leftCntlDrag
	#Now, leftCntlDrag is used for 'subtract from selection' which is 
	#consistent with the default mode (selectMols mode)- ninad 20070802
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1],
                                    self.o.quat)
    
        if self.propMgr.rotateAsUnitCB.isChecked():
            self.o.assy.rotsel(q) # Rotate the selection as a unit.
        else:
            for mol in self.o.assy.selmols: # Rotate each chunk individually.
                mol.rot(q)

        self.o.gl_update()
      
    def leftUp(self, event):  
        '''Overrides leftdrag method of selectMolsMode'''        
        
	if self.cursor_over_when_LMB_pressed == 'Empty Space': #@@ needed?
	    self.emptySpaceLeftUp(event)
	elif self.dragdist < 2:
	    selectMolsMode.leftUp(self,event)
                  
    def EndPick(self, event, selSense):
        """
        Pick if click
        """
        if not self.picking:
            return
        
        self.picking = False

        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        self.dragdist += vlen(deltaMouse)
        
        if self.dragdist<7:
            # didn't move much, call it a click
            has_jig_selected = False
            if self.o.jigSelectionEnabled and self.jigGLSelect(event, selSense):
                has_jig_selected = True
            if not has_jig_selected:
                if selSense == SUBTRACT_FROM_SELECTION: 
                    self.o.assy.unpick_at_event(event)
                if selSense == ADD_TO_SELECTION: 
                    self.o.assy.pick_at_event(event)
                if selSense == START_NEW_SELECTION: 
                    self.o.assy.onlypick_at_event(event)
                if selSense == DELETE_SELECTION: 
                    self.o.assy.delete_at_event(event)
                
            self.w.win_update()

    
    def clear_leftA_variables(self): # bruce 070605 #####@@@@CALL ME  #k should it clear sbar too?
        # Clear variables that only leftADown can set. This needs to be done for every mousedown and mouseup ###DOIT.
        # (more precisely for any call of Down that if A is then pressed might start calling leftADrag ####)
        # Then, if they're not properly set during leftADrag, it will show a statusbar error and do nothing.
        # This should fix bugs caused by 'A' keypress during drag or 'A' keypress not noticed by NE1 (in wrong widget or app).
        # [bruce 070605 bugfix; also added all these variables]
        self._leftADown = False # whether we're doing a leftA-style drag at all
        self._leftADown_rotateAsUnit = None
        self._leftADown_movables = None # list of movables for leftADrag
            # WARNING: some code (rotsel calls) assumes this is also the movable selected objects
        self._leftADown_indiv_axes = None
        self._leftADown_averaged_axis = None
        self._leftADown_error = False # whether an error should cause subsequent leftADrags to be noops
        self._leftADown_dragcounter = 0
        self._leftADown_total_dx_dy = V(0.0, 0.0)
        return

    def leftAError(self, msg):
        env.history.statusbar_msg( msg) #bruce 070605
        self._leftADown_error = True # prevent more from happening in leftADrag
        return

    def leftADown(self, event):
        """ Set up for sliding and/or rotating the selected chunk(s) 
        along/around its own axis when left mouse and key 'A' is pressed.
        """

        self._leftADown = True
        self._leftADown_rotateAsUnit = self.propMgr.rotateAsUnitCB.isChecked()
        
        
        obj = self.get_obj_under_cursor(event)
        
        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            return
        
	self.doObjectSpecificLeftDown(obj, event)
	
	movables = self.o.assy.getSelectedMovables()
        self._leftADown_movables = movables
	        
        if not movables:
            self.leftAError("(nothing movable is selected)")
            return
                    
        self.o.SaveMouse(event)

        #bruce 070605 questions (about code that was here before I did anything to it today):
        # - how are self.Zmat, self.picking, self.dragdist used during leftADrag?
        # - Why is the axis recomputed in each leftADrag? I think that's a bug, for "rotate as a unit", since it varies!
        #   And it's slow, either way, since it should not vary (once bugs are fixed) but .getaxis will always have to recompute it.
        #   So I'll change this to compute the axes or axis only once, here in leftADown, and use it in each leftADrag.
        # - Why is the "averaged axis" computed here at all, when not "rotate as a unit"?
        
        ma = V(0,0,0) # accumulate "average axis" (only works well if all axes similar in direction, except perhaps for sign)
        self._leftADown_indiv_axes = [] #bruce 070605 optim
        for mol in movables:
            axis = mol.getaxis()
            if dot(ma, axis) < 0.0: #bruce 070605 bugfix, in case axis happens to point the opposite way as ma
                axis = - axis
            self._leftADown_indiv_axes.append(axis) # not sure it's best to put sign-corrected axes here, but I'm guessing it is
            ma += axis

        self._leftADown_averaged_axis = norm(ma) #bruce 070605 optim/bugfix
        
               
        if vlen(self._leftADown_averaged_axis) < 0.5: # ma was too small
            # The pathological case of zero ma is probably possible, but should be rare;
            # consequences not reviewed; so statusbar message and refusal seems safest:
            self.leftAError("(axes can't be averaged, doing nothing)")
            return
            
        ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
        self.Zmat = A([ma,[-ma[1],ma[0]]])
        self.picking = True
        self.dragdist = 0.0

        self._leftADown_total_dx_dy = V(0.0, 0.0)

        if 0: # looks ok; axis for 3-strand n=10 DNA is reasonably close to axis of Axis strand [bruce 070605]
            print "\nleftADown gets",self._leftADown_averaged_axis
            print self._leftADown_indiv_axes
            print movables
            print self.Zmat
        
        if self.propMgr.isTranslateGroupBoxActive:
	    self.leftDownType = 'A_TRANSLATE'
	else:
	    self.leftDownType = 'A_ROTATE'
        return # from leftADown
    
    def leftADrag(self, event):
        """Move selected chunk(s) along its axis (mouse goes up or down)
           and rotate around its axis (left-right) while left dragging
           the selection with keyboard key 'A' pressed
        """
	            
        ##See comments of leftDrag()--Huaicai 3/23/05
        if not self.picking:
            return

        if self._leftADown_error:
            return

        if not self._leftADown:
            self.leftAError("(doing nothing -- 'A' pressed after drag already started)")
            return
        
        movables = self._leftADown_movables
        assert movables # otherwise error flag was set during leftADown [bruce 070605]

        self._leftADown_dragcounter += 1
        counter = self._leftADown_dragcounter # mainly useful for debugging
        
        w = self.o.width + 0.0
        h = self.o.height + 0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())
	
        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*math.pi/w)
        
        self._leftADown_total_dx_dy += V(dx,dy)
        tot_dx, tot_dy = self._leftADown_total_dx_dy

        ## env.history.statusbar_msg("(%d) incremental motion: %f; rotation: %f" % (counter, dx, dy)) # counter useful for debug
        
        env.history.statusbar_msg("this 'A'-drag: translation: %f; rotation: %f" % (tot_dx, tot_dy))
            #bruce 070605; format might need cleanup
        
        if not self._leftADown_rotateAsUnit:
            # move/rotate individually ###UNTESTED since rewrite [bruce 070605]
            for mol, ma in zip(movables, self._leftADown_indiv_axes):
                mol.move(dx*ma)
                mol.rot(Q(ma,-dy))            
        else:
            # move/rotate selection as a unit
            
            #find out resultant axis, translate and rotate the selected
            #movables along this axis (for rotate use rotsel)-- ninad 20070605
            # (modified/optimized by bruce 070605)
            resAxis = self._leftADown_averaged_axis
            for mol in movables:
                mol.move(dx*resAxis)
                
            self.o.assy.rotsel(Q(resAxis,-dy)) # this assumes movables are exactly the selected movable objects (as they are)
                # [could this be slow, or could something in here have a memory leak?? (maybe redrawing selected chunks?)
                #  interaction is way too slow, and uneven, and I hear swapping in the bg.
                #  Aha, I bet it's all those Undo checkpoints, which we should not be collecting during drags at all!!
                #  --bruce 070605 Q]
        
        self.dragdist += vlen(deltaMouse) #k needed?? [bruce 070605 comment]
        self.o.SaveMouse(event)
        self.o.assy.changed() #ninad060924 fixed bug 2278
        self.o.gl_update()
        return
    
    def leftShiftUp(self, event):
	if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.emptySpaceLeftUp(event)
            return
        if self.o.modkeys == 'Shift+Control':
            self.end_selection_curve(event)
            return
        self.EndPick(event, ADD_TO_SELECTION)

    def leftDouble(self, event):
        """
        Do nothing upon double click , while in move mode (pre Alpha9 - experimental)
        """
	#@@ninad070329  Till Alpha8, it used to Switch to Select Chunks Mode. 
        #for Alpha9, (pr pre Alpha9), it won't do anything. 
	#this implementation might change in future. 
	
        ## Current plans are to merge Select Chunks and Move Chunks modes in A8.
        ##self.commandSequencer.userEnterCommand('SELECTMOLS') # Fixes bug 1182. mark 060301.
        return


    def rotateThetaPlus(self):
        "Rotate the selected chunk(s) by theta (plus)"
	
        button = self.propMgr.rotateAroundAxisButtonRow.checkedButton()
        if button:
            rotype = str(button.text())
        else:
            env.history.message(redmsg("Rotate By Specified Angle: Please press the button \
            corresponding to the axis of rotation"))
            return
        theta = self.propMgr.rotateThetaSpinBox.value()
        self.rotateTheta( rotype, theta)
        
    def rotateThetaMinus(self):
        "Rotate the selected chunk(s) by theta (minus)"
        button = self.propMgr.rotateAroundAxisButtonRow.checkedButton()
        if button:
            rotype = str(button.text())
        else:
            env.history.message(redmsg("Rotate By Specified Angle: Please press the button \
            corresponding to the axis of rotation"))
            return
        theta = self.propMgr.rotateThetaSpinBox.value() * -1.0
        self.rotateTheta( rotype, theta)
        
    def rotateTheta(self, rotype, theta):
        "Rotate the selected chunk(s) /jig(s) around the specified axis by theta (degrees)"
	
	selectedMovables = self.o.assy.getSelectedMovables()
        if not selectedMovables: 
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return
        
        if rotype == 'ROTATEX':
            ma = V(1,0,0) # X Axis
        elif rotype == 'ROTATEY':
            ma = V(0,1,0) # Y Axis
        elif rotype == 'ROTATEZ':
            ma = V(0,0,1) # Z Axis
        else:
            print 'modifyMody.rotateTheta: Error.  rotype = ', rotype, ', which is undefined.'
            return

        # wware 20061214: I don't know where the need arose for this factor of 100,
        # but it's necessary to get correct angles.        
        #ninad 070322:
        #Will's above comment was for "dy = 100.0 * (pi / 180.0) * theta  # Convert to radians" 
        #I agree with this. In fact if I enter angle of  1 degree, it multiplies it by 100!
        #May be it was necessary in Qt3 branch. I am modifying this formula 
        #to remove this  multiplication factor of 100 as its giving wrong results
        dy =  (math.pi / 180.0) * theta  # Convert to radians
        qrot = Q(ma,dy) # Quat for rotation delta.
        
        if self.propMgr.rotateAsUnitCB.isChecked():
            self.o.assy.rotsel(qrot) # Rotate the selection as a unit.
        else:
	    for item in selectedMovables:
		try:
		    item.rot(qrot)
		except AssertionError:
		    print_compact_traceback("Selected movable doesn't have"\
					    "rot method?")
                
        self.o.gl_update()
        
    def transDeltaPlus(self):
        "Add X, Y, and Z to the selected chunk(s) current position"
        if not self.o.assy.getSelectedMovables(): 
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return
        offset = self.propMgr.get_move_delta_xyz()
        self.o.assy.movesel(offset)
        self.o.gl_update()

    def transDeltaMinus(self):
        "Subtract X, Y, and Z from the selected chunk(s) current position"
        if not self.o.assy.getSelectedMovables(): 
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return
        
        offset = self.propMgr.get_move_delta_xyz(Plus=False)
        self.o.assy.movesel(offset)
        self.o.gl_update()

    def moveAbsolute(self):
        '''Move selected chunk(s), jig(s) to absolute X, Y, and Z by computing the bbox center
        of everything as if they were one big chunk, then move everything as a unit.
        '''
        movables = self.o.assy.getSelectedMovables()
        if not movables: 
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return
        
        ## Compute bbox for selected chunk(s).
        from shape import BBox
        bbox = BBox()
        for m in movables:
            if hasattr(m, "bbox"): # Fixes bug 1990. Mark 060702.
                bbox.merge(m.bbox)
        pt1 = bbox.center() # pt1 = center point for bbox of selected chunk(s).
       
        pt2 = self.propMgr.get_move_xyz() # pt2 = X, Y, Z values from PM
        offset = pt2 - pt1 # Compute offset for movesel.
        
        self.o.assy.movesel(offset) # Move the selected chunk(s)/jig(s).
    
        # Print history message about what happened.
        if len(movables) == 1:
            msg = "[%s] moved to [X: %.2f] [Y: %.2f] [Z: %.2f]" % (movables[0].name, pt2[0], pt2[1], pt2[2])
        else:
            msg = "Selected chunks/jigs moved by offset [X: %.2f] [Y: %.2f] [Z: %.2f]" % (offset[0], offset[1], offset[2])
        env.history.message(msg)
        self.o.gl_update()
        return
    
    def skip(self):
        pass

    def drawHighlightedChunk(self, glpane, selobj, hicolor):
        """
        [overrides selectMolsMode method]
        """
        # bruce 071008 (intending to be equivalent to prior code)
        return False
    
    pass # end of class modifyMode
