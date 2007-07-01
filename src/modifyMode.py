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

from selectMode import selectMode
from selectMolsMode import selectMolsMode
from selectAtomsMode import selectAtomsMode
from widgets import FloatSpinBox
from HistoryWidget import redmsg
import env
from MovePropertyManager import MovePropertyManager
from chem import Atom
from bonds import Bond
from jigs import Jig
from modes import basicMode
from Utility import geticon

from debug import print_compact_traceback

from constants import START_NEW_SELECTION
from constants import DELETE_SELECTION
from constants import SUBTRACT_FROM_SELECTION
from constants import ADD_TO_SELECTION

from VQT import V, Q, A, norm, vlen

def do_what_MainWindowUI_should_do(w):
    'Populate the Move Chunks dashboard'
    
    w.moveChunksDashboard.clear()
    
    w.moveChunksDashboard.addWidget(w.textLabel1)

    w.moveChunksDashboard.addAction(w.moveFreeAction)
    
    w.moveChunksDashboard.addSeparator()
    
    w.moveChunksDashboard.addAction(w.transXAction)
    w.moveChunksDashboard.addAction(w.transYAction)
    w.moveChunksDashboard.addAction(w.transZAction)
    
    w.moveChunksDashboard.addSeparator()
    
    w.movetype_combox = QComboBox()
    w.moveChunksDashboard.addWidget(w.movetype_combox)
    w.movetype_combox.insertItem(0,'Translate')
    w.movetype_combox.insertItem(1,'Rotate X')
    w.movetype_combox.insertItem(2,'Rotate Y')
    w.movetype_combox.insertItem(3,'Rotate Z')
    
    w.moveXLabel = QLabel()
    w.moveXLabel.setText(" X ")
    w.moveChunksDashboard.addWidget(w.moveXLabel)
    w.moveXSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveXSpinBox")
    w.moveXSpinBox.setSuffix(" A")
    w.moveXSpinBox.setToolTip('Delta X (Angstroms)')
    w.moveChunksDashboard.addWidget(w.moveXSpinBox)
    w.moveYLabel = QLabel()
    w.moveYLabel.setText(" Y ")
    w.moveChunksDashboard.addWidget(w.moveYLabel)
    w.moveYSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveYSpinBox")
    w.moveYSpinBox.setSuffix(" A")
    w.moveYSpinBox.setToolTip('Delta Y (Angstroms)')
    w.moveChunksDashboard.addWidget(w.moveYSpinBox)
    w.moveZLabel = QLabel()
    w.moveZLabel.setText(" Z ")
    w.moveChunksDashboard.addWidget(w.moveZLabel)
    w.moveZSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveZSpinBox")
    w.moveZSpinBox.setSuffix(" A")
    w.moveZSpinBox.setToolTip('Delta Z (Angstroms)')
    w.moveChunksDashboard.addWidget(w.moveZSpinBox)
    w.moveThetaLabel = QLabel()
    w.moveThetaLabel.setText(" Theta ")
    w.moveChunksDashboard.addWidget(w.moveThetaLabel)
    w.moveThetaSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveThetaSpinBox")
    w.moveThetaSpinBox.setToolTip('Rotation (Degrees)')
    w.moveThetaSpinBox.setRange(-36000,36000) # Actually -360 to 360
    w.moveChunksDashboard.addWidget(w.moveThetaSpinBox)
    
    w.moveChunksDashboard.addAction(w.moveDeltaPlusAction)
    w.moveChunksDashboard.addAction(w.moveDeltaMinusAction)
    w.moveChunksDashboard.addAction(w.moveAbsoluteAction)
    w.moveChunksDashboard.addAction(w.rotateThetaPlusAction)
    w.moveChunksDashboard.addAction(w.rotateThetaMinusAction)
    
    w.moveChunksDashboard.addSeparator()
    
    # I needed this for nanocar animation. Mark 060524.
    w.moveChunksDashboard.rotateAsUnitCB = QCheckBox("Rotate as unit", w.moveChunksDashboard)
    w.moveChunksDashboard.rotateAsUnitCB.setChecked(1)
    w.moveChunksDashboard.rotateAsUnitCB.setToolTip('Rotate selection as a unit')
    w.moveChunksDashboard.addWidget(w.moveChunksDashboard.rotateAsUnitCB)
    
    w.moveChunksDashboard.addSeparator()
    
    w.moveChunksDashboard.addAction(w.toolsDoneAction)

def set_move_xyz(obj,x,y,z):
    '''Set values of X, Y and Z in the dashboard.
    '''
    self = obj
    self.moveXSpinBox.setValue(x)
    self.moveYSpinBox.setValue(y)
    self.moveZSpinBox.setValue(z)

def get_move_xyz(obj):
    '''Returns X, Y and Z values in the dashboard based on Plus.
    If Plus is True, returns x, y, z
    If Plus is False, returns -x, -y, -z
    '''
    self = obj

    x = self.moveXSpinBox.value()
    y = self.moveYSpinBox.value()
    z = self.moveZSpinBox.value()
    
    return (x,y,z)   
    
def set_move_delta_xyz(obj, delX, delY, delZ):
    """sets the values for 'move by distance delta' spinboxes """
    self = obj
    self.moveDeltaXSpinBox.setValue(delX)
    self.moveDeltaYSpinBox.setValue(delY)
    self.moveDeltaZSpinBox.setValue(delZ)

def get_move_delta_xyz(obj, Plus =True):
    """Returns the values for 'move by distance delta' spinboxes """
    
    self = obj
    delX = self.moveDeltaXSpinBox.value()
    delY = self.moveDeltaYSpinBox.value()
    delZ = self.moveDeltaZSpinBox.value()
    
    if Plus: return (delX,delY,delZ) # Plus
    else: return (-delX, -delY, -delZ) # Minus
    
    
class modifyMode(selectMolsMode, MovePropertyManager): # changed superclass from basicMode to selectMolsMode.  mark 060301.
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
    
    # no __init__ method needed

    def Enter(self):
        
        #Initialize the flag for Constrained translation and rotation
        #along the axis of the chunk to False. This flag is set 
        #to True whenever keyboard key 'A' is pressed 
        #while in Translate/Rotate mode. See methods keyPress, keyRelease, 
        #leftDown, Drag and leftADown, Drag for details. 
        self.isConstrainedDragAlongAxis = False

        #ninad 070212. modifyMode is a subclass of selMols mode. 
        #Using the following instead of basicMode.Enter(self)
        #It is also useful in setting a proper flag when move mode is 
        #used as a 'pseudo mode' in Select chunks mode.          
        selectMolsMode.Enter(self) 
        self.o.assy.selectChunksWithSelAtoms()
        self.dragdist = 0.0
        self.setGoBackToMode(False, 'MODIFY')
        self.clear_leftA_variables() #bruce 070605 precaution
        return
    
    # (see basicMode.Done.__doc__ for the ones we don't override here [bruce 040923])

    def init_gui(self):
        
        MovePropertyManager.__init__(self)
                
        self.openPropertyManager(self) # ninad 061227 see PropertymanagerMixin
	
	self.updateCommandManager(bool_entering = True)
    
        # connect signals (these all need to be disconnected in restore_gui)
                
        self.connect_or_disconnect_signals(True)
        
        self.w.dashboardHolder.setWidget(self.w.moveChunksDashboard)
        
        self.w.moveChunksDashboard.show() # show the Move Molecules dashboard
        
        set_move_xyz(self, 0, 0, 0) # Init X, Y, and Z to zero
        set_move_delta_xyz(self, 0,0,0) # Init DelX,DelY, DelZ to zero
        self.w.moveThetaSpinBox.setValue(0) # Init Theta spinbox to zero
        self.setup_movetype(self.w.movetype_combox.currentText())

        # Always reset the dashboard icon to "Move Free" when entering MODIFY mode.
        # Mark 050410
        #self.w.moveFreeAction.setChecked(1) # toggle on the Move Free action on the dashboard
        self.moveOption = 'MOVEDEFAULT'
        self.rotateOption = 'ROTATEDEFAULT'
    
    def connect_or_disconnect_signals(self, connect): # mark 060304.
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
        #change_connect(self.w.MoveOptionsGroup, SIGNAL("selected(QAction *)"), self.changeMoveOption)
        change_connect(self.w.MoveOptionsGroup, SIGNAL("triggered(QAction *)"), self.changeMoveOption)
        change_connect(self.w.rotateOptionsGroup, SIGNAL("triggered(QAction *)"), self.changeRotateOption)
        
        change_connect(self.w.moveDeltaPlusAction, SIGNAL("activated()"), self.moveDeltaPlus)
        change_connect(self.w.moveDeltaMinusAction, SIGNAL("activated()"), self.moveDeltaMinus)
        change_connect(self.w.moveAbsoluteAction, SIGNAL("activated()"), self.moveAbsolute)
        change_connect(self.w.rotateThetaPlusAction, SIGNAL("activated()"), self.moveThetaPlus)
        change_connect(self.w.rotateThetaMinusAction, SIGNAL("activated()"), self.moveThetaMinus)
        change_connect(self.w.movetype_combox, SIGNAL("activated(const QString&)"), self.setup_movetype)
	change_connect(self.exitMoveAction, SIGNAL("triggered()"), 	 
	                        self.w.toolsDone)
        
    def restore_gui(self):
        # disconnect signals which were connected in init_gui [bruce 050728]
	self.updateCommandManager(bool_entering = False)
        self.closePropertyManager()	
        self.w.toolsMoveMoleculeAction.setChecked(False) # toggle on the Move Chunks icon
        self.w.rotateComponentsAction.setChecked(False)
        self.connect_or_disconnect_signals(False)
        self.w.moveChunksDashboard.hide()

    
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
						   entering =bool_entering)
    
        
    def keyPress(self,key):           
        basicMode.keyPress(self, key)
        
        # For these key presses, we toggle the Action item, which will send 
        # an event to changeMoveMode, where the business is done.
        # Mark 050410
        if self.w.toolsMoveMoleculeAction.isChecked():  
            if key == Qt.Key_X:
                self.w.transXAction.setChecked(1) # toggle on the Translate X action item
                self.changeMoveOption(self.w.transXAction)
            elif key == Qt.Key_Y:
                self.w.transYAction.setChecked(1) # toggle on the Translate Y action item
                self.changeMoveOption(self.w.transYAction)
            elif key == Qt.Key_Z:
                self.w.transZAction.setChecked(1) # toggle on the Translate Z action item
                self.changeMoveOption(self.w.transZAction)
        elif self.w.rotateComponentsAction.isChecked():
            if key == Qt.Key_X:
                self.w.rotXAction.setChecked(1) # toggle on the Rotate X action item
                self.changeRotateOption(self.w.rotXAction)
            elif key == Qt.Key_Y:
                self.w.rotYAction.setChecked(1) # toggle on the Rotate Y action item
                self.changeRotateOption(self.w.rotYAction)
            elif key == Qt.Key_Z:
                self.w.rotZAction.setChecked(1) # toggle on the Rotate Z action item
                self.changeRotateOption(self.w.rotZAction)
        
        #If Key 'A' is pressed, set the flag for Constrained trasnlation and rotation
        #along the axis of the chunk to True
        if key == Qt.Key_A:
            self.isConstrainedDragAlongAxis = True 
            
        else:
            self.isConstrainedDragAlongAxis = False 
        
        self.update_cursor()
            
                
    def keyRelease(self,key):
        basicMode.keyRelease(self, key)
        
    
        if key == Qt.Key_X or key == Qt.Key_Y or key == Qt.Key_Z:
            self.w.moveFreeAction.setChecked(1) # toggle on the Move Chunks icon
            self.changeMoveOption(self.w.moveFreeAction)
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
        if self.o.modkeys is None:
            if self.isConstrainedDragAlongAxis:
                self.o.setCursor(self.w.MolSelAxisRotTransCursor)
            else:
                if self.w.toolsMoveMoleculeAction.isChecked():
                    self.o.setCursor(self.w.MolSelTransCursor)
                else:
                    self.o.setCursor(self.w.MolSelRotCursor)
        elif self.o.modkeys == 'Shift':
            if self.w.toolsMoveMoleculeAction.isChecked():
                self.o.setCursor(self.w.MolSelTransAddCursor)
            else:
                self.o.setCursor(self.w.MolSelRotAddCursor)
        elif self.o.modkeys == 'Control':
            if self.w.toolsMoveMoleculeAction.isChecked():
                self.o.setCursor(self.w.MolSelTransSubCursor)
            else:
                self.o.setCursor(self.w.MolSelRotSubCursor)  
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB(): Invalid modkey=", self.o.modkeys
        
        return
           
    def leftDown(self, event):
        """Move the selected object(s).
        """
        self.clear_leftA_variables() #bruce 070605 added this (guess at what's needed)
        env.history.statusbar_msg("")

        # If keyboard key 'A' is pressed, set it up for constrained translation
        #and rotation along the axis and return. 
        if not self.isGoBackToMode():  
            if self.isConstrainedDragAlongAxis:
                self.leftADown(event)
                return
        
        #If its pseudo move mode only permit free move(translate) drag
        if self.isGoBackToMode():
            self.w.toolsMoveMoleculeAction.setChecked(True)
            self.w.moveFreeAction.setChecked(True)            
        else:
            #Ninad 070308 for 'rotate components mode, left down = old ctrl + left down
            #@@@ this will be revised. I am planning to write methods such as 'rotateFree drag setup, 
            #move free drag setup etc and call them here and in leftDrag.
            if self.w.rotateFreeAction.isChecked():
                self.leftCntlDown(event)
		    
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
       
##        from constants import GL_FAR_Z

        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0
        self.transDelta = 0 # X, Y or Z deltas for translate.
        self.rotDelta = 0 # delta for constrained rotations.
        self.moveOffset = [0.0, 0.0, 0.0] # X, Y and Z offset for move.
        
        # This needs to be refactored further into move and translate methods. mark 060301.
        
        # Move section
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
            #bruce 060316 replaced equivalent old code with this new method
        self.startpt = self.movingPoint # Used in leftDrag() to compute move offset during drag op.
        
        # end of Move section
           
        # Translate section     
        if self.w.toolsMoveMoleculeAction.isChecked():            
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
                
        if self.w.rotateComponentsAction.isChecked():
            if self.rotateOption != 'ROTATEDEFAULT':
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
                    
                else: print "modifyMode: Error - unknown rotateOption value =", self.rotateOption

                ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
                # When in the front view, right = 1,0,0 and up = 0,1,0, so ma will be computed as 0,0.
                # This creates a special case problem when the user wants to constrain rotation around
                # the Z axis because Zmat will be zero.  So we have to test for this case (ma = 0,0) and
                # fix ma to -1,0.  This was needed to fix bug 537.  Mark 050420
                if ma[0] == 0.0 and ma[1] == 0.0: ma = [-1.0, 0.0] 
                self.Zmat = A([ma,[-ma[1],ma[0]]])
                
        
        if not self.isGoBackToMode():                            
            #Permit movable object picking upon left down.             
            obj = self.get_obj_under_cursor(event)
            # If highlighting is turned on, get_obj_under_cursor() returns atoms, singlets, bonds, jigs,
            # or anything that can be highlighted and end up in glpane.selobj. [bruce revised this comment, 060725]
                # If highlighting is turned off, get_obj_under_cursor() returns atoms and singlets (not bonds or jigs).
                # [not sure if that's still true -- probably not. bruce 060725 addendum]
            if obj is None: # Cursor over empty space.
                self.emptySpaceLeftDown(event)
                return
            
            if isinstance(obj, Atom) and obj.is_singlet(): # Cursor over a singlet
                self.singletLeftDown(obj, event)
                    # no win_update() needed. It's the responsibility of singletLeftDown to do it if needed.
                return                
            elif isinstance(obj, Atom) and not obj.is_singlet(): # Cursor over a real atom
                self.atomLeftDown(obj, event)
            elif isinstance(obj, Bond) and not obj.is_open_bond(): # Cursor over a bond.
                self.bondLeftDown(obj, event)
            elif isinstance(obj, Jig): # Cursor over a jig.
                self.jigLeftDown(obj, event)
            else: # Cursor is over something else other than an atom, singlet or bond. 
                # The program never executes lines in this else statement since
                # get_obj_under_cursor() only returns atoms, singlets or bonds.
                # [perhaps no longer true, if it ever was -- bruce 060725]
                pass
            
            self.w.win_update()

        # end of Rotate section
        
    def leftDrag(self, event):
        """Move the selected object(s):
        - in the plane of the screen following the mouse, 
        - or slide and rotate along the an axis
        """
        #Huaicai 3/23/05: This following line will fix bugs like 460. But
        #the root of the serials of bugs including a lot of cursor bugs is
        # the mouse event processing function. For bug 460, the 
        # obvious reason is leftDown() is not called before the leftDrag()
        #& Not sure this is true anymore with the new cursor/modkey API.  mark 060301.
        
        #@@@TODO: leftDrag and leftDown methods need code cleanup. 
        #perhaps a new class for 'rotate components' ? that will help reduce
        #lots of if-else checks below. Also, hopefully, the new 
        #DrahHandler_API will be applied to to atoms, jigs, bonds someday. 
        #that will help to get rid of the 'psudoMoveMode conditions. 
        #[--Ninad 20070605 commented]
        
        if not self.picking: return
        
        if not self.isGoBackToMode():  
	    if self.cursor_over_when_LMB_pressed == 'Empty Space':            
                self.continue_selection_curve(event)             
		return
            if self.isConstrainedDragAlongAxis:
                try:
                    self.leftADrag(event)
                    return
                except:
                    # this might be obsolete, since leftADrag now tries to handle this (untested) [bruce 070605 comment]
                    print "Key A pressed after Left Down. controlled translation will not be performed"
                    pass
            if self.w.rotateComponentsAction.isChecked():
                if self.rotateOption == 'ROT_TRANS_ALONG_AXIS':
                    try:
                        self.leftADrag(event)
                        return
                    except:
                        print " error doing leftADrag"
            elif self.w.toolsMoveMoleculeAction.isChecked():
                if self.moveOption == 'ROT_TRANS_ALONG_AXIS':
                    try:
                        self.leftADrag(event)
                        return
                    except:
                        print " error doing leftADrag"
                    
        
        #Ninad 070314: Following ensures that you are in Move mode 
        #(and not pseudo move mode) and returns from left drag if 
        #'free' drag option in the combobox is not set.
        if not self.isGoBackToMode():       
            if self.w.toolsMoveMoleculeAction.isChecked():
                if self.movetype_combox.currentText() != "Free Drag":
                    return
            elif self.w.rotateComponentsAction.isChecked():
                if self.rotatetype_combox.currentText() != "Free Drag":
                    return                
            #Ninad 070308 for 'rotate components mode, left drag = old ctrl + left drag
            if self.w.rotateComponentsAction.isChecked():
                if self.w.rotateFreeAction.isChecked():      
                    self.leftCntlDrag(event)
                    return

        if not self.o.assy.getSelectedMovables(): return
        
        
        # Fixes bugs 583 and 674 along with change in keyRelease.  Mark 050623
        if self.movingPoint is None: self.leftDown(event) # Fix per Bruce's email.  Mark 050704
        
                    
        if self.w.toolsMoveMoleculeAction.isChecked():            
            # Move section
            if self.moveOption == 'MOVEDEFAULT':
                deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                           self.o.MousePos[1] - event.pos().y(), 0.0)
    
                point = self.dragto( self.movingPoint, event) #bruce 060316 replaced old code with dragto (equivalent)
            
                # Print status bar msg indicating the current move delta.
                if 1:
                    self.moveOffset = point - self.startpt # Fixed bug 929.  mark 060111
                    msg = "Offset: [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.moveOffset[0], self.moveOffset[1], self.moveOffset[2])
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
                if self.moveOption == 'TRANSX' :     ma = V(1,0,0) # X Axis
                elif self.moveOption == 'TRANSY' :  ma = V(0,1,0) # Y Axis
                elif self.moveOption == 'TRANSZ' :  ma = V(0,0,1) # Z Axis
                else: 
                    print "modifyMode.leftDrag: Error - unknown moveOption value =", self.moveOption                
                    return
       
                self.transDelta += dx # Increment translation delta                   
                self.o.assy.movesel(dx*ma) 
                
        if self.w.rotateComponentsAction.isChecked():
            #Rotate section      
            w=self.o.width+0.0
            h=self.o.height+0.0
            deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())
            a =  dot(self.Zmat, deltaMouse)
            dx,dy =  a * V(self.o.scale/(h*0.5), 2*math.pi/w)

            if self.rotateOption == 'ROTATEX' :     ma = V(1,0,0) # X Axis
            elif self.rotateOption == 'ROTATEY' :  ma = V(0,1,0) # Y Axis
            elif self.rotateOption == 'ROTATEZ' :  ma = V(0,0,1) # Z Axis
            else: 
                print "modifyMode.leftDrag: Error - unknown rotateOption value =", self.rotateOption                
                return                
            qrot = Q(ma,-dy) # Quat for rotation delta.
            self.rotDelta += qrot.angle *180.0/math.pi * sign(dy) # Increment rotation delta (and convert to degrees)
            
            self.updateRotationDeltaLabels(self.rotateOption, self.rotDelta)
            self.o.assy.rotsel(qrot) 
            
            #End of Rotate Section
            
        # Print status bar msg indicating the current translation and rotation delta.
        if self.o.assy.selmols:
            msg = "%s delta: [%.2f Angstroms] [%.2f Degrees]" % (self.axis, self.transDelta, self.rotDelta)
            env.history.statusbar_msg(msg)
            

        # common finished code
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()
        
    # end of leftDrag    
    
    def updateRotationDeltaLabels(self, rotateOption, rotationDelta):
        """ Updates the Rotation Delta labels in the Rotate combobox  while rotating
        the selection aroung an axis"""
        ##self.rotationAngleDeltas_lbl.show()
        
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
            self.deltaThetaX_lbl.setText(str(round(self.rotDelta, 2)))
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
            self.deltaThetaY_lbl.setText(str(round(self.rotDelta, 2)))
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
            self.deltaThetaZ_lbl.setText(str(round(self.rotDelta, 2)))
            for lbl in listxy:
                font = QtGui.QFont(lbl.font())
                font.setBold(False)
                lbl.setFont(font)   
                lbl.show()
        else:
            print "modifyMode.updateRotationDeltaLabels: Error - unknown rotateOption value =", self.rotateOption
                
          
    #Ninad 070212 : Flags that set which mode to return after left mouse dragging (left down) is finished. 
    #This is used in 'psudo -move mode' which is accessed from the Select chunks mode. 
    def setGoBackToMode(self, bool = False, modeToReturn = 'MODIFY'):
        """ Sets the flag go back to mode. Move mode acts like a pesudo mode while in 
        Select chunks mode. (it is activated only during left drag (leftDown) in select mode and then 
        user returns to the select chunks mode upon mouse release"""
        self.bool_goBackToMode = bool
        self.modeToReturn = modeToReturn
    
    def isGoBackToMode(self):
        """ Returns True if Go back to mode is requested. Move mode acts like a pesudo mode while in 
        Select chunks mode. (it is activated only during left drag in select mode and then 
        user returns to the select chunks mode upon mouse release"""
        return self.bool_goBackToMode
    
    def goBackToMode(self, modeToReturn = 'MODIFY'):
        """ Returns the mode to go back to. The default value is Move mode (i.e. it stays in move mode) 
        Move mode acts like a pesudo mode while in 
        Select chunks mode. (it is activated only during left drag in select mode and then 
        user returns to the select chunks mode upon mouse release"""        
        return self.modeToReturn
    
    def leftUp(self, event):  
        '''Overrides leftdrag method of selectMolsMode'''        
        #Ninad 070212: Flags that set which mode to return after left mouse dragging (left down) is finished.
        # Example: SelectMols Mode's leftDrag event calls modifyMode's leftDown Event and sets proper 
        #flags before so that when the left mouse button is released, program returns to the select mols mode. 
        #Thus  we can make use of the free drag functionality while in select chunks mode.    
        if self.isGoBackToMode():
            modeToReturn = self.goBackToMode()
            self.o.setMode(modeToReturn)            
        else:
	    if self.cursor_over_when_LMB_pressed == 'Empty Space': #@@ needed?
		self.emptySpaceLeftUp(event)
            elif self.dragdist < 2:
                selectMolsMode.leftUp(self,event)
           
        #ninad 070212 This is necessary to make sure that program remains in the Move mode when 
        #user is in that mode 
        self.setGoBackToMode(False, 'MODIFY')
        
       
    def EndPick(self, event, selSense):
        """Pick if click
        """
        if not self.picking: return
        
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
     
    def leftCntlDown(self, event):
        """Setup a trackball action on the selected chunk(s).
        """
        if not self.o.assy.getSelectedMovables(): return
	
	    
        #If its pseudo move mode only permit free move(translate) drag
        if self.isGoBackToMode():
            self.w.rotateComponentsAction.setChecked(True)
            self.w.rotateFreeAction.setChecked(True)

        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        self.picking = True
        self.dragdist = 0.0

   
    def leftCntlDrag(self, event):
        """Do an incremental trackball action on all selected chunks(s).
        """
		
        ##See comments of leftDrag()--Huaicai 3/23/05
        if not self.picking: return
	
		    
        if not self.o.assy.getSelectedMovables(): return
        
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1],
                                    self.o.quat)
    
        if self.rotateAsUnitCB.isChecked():
            self.o.assy.rotsel(q) # Rotate the selection as a unit.
        else:
            for mol in self.o.assy.selmols: # Rotate each chunk individually.
                mol.rot(q)

        self.o.gl_update()

    def leftCntlUp(self, event):
        #Ninad 070322: Flags that set which mode to return after Control left mouse dragging  is finished.
        # Example: SelectMols Mode's leftCntlDrag event calls modifyMode's leftCntlDown Event and sets proper 
        #flags before so that when the left+ cntl  mouse buttons are  released, program returns to the select mols mode. 
        #Thus  we can make use of the 'free rotate drag' functionality while in select chunks mode.    
        if self.isGoBackToMode():
            modeToReturn = self.goBackToMode()
            self.o.setMode(modeToReturn)         
        else:
            self.EndPick(event, SUBTRACT_FROM_SELECTION)
    

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
        self._leftADown_rotateAsUnit = self.rotateAsUnitCB.isChecked()
        movables = self.o.assy.getSelectedMovables()
        self._leftADown_movables = movables
        
        obj = self.get_obj_under_cursor(event)
        
        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            ##return
            
        if isinstance(obj, Atom) and obj.is_singlet(): # Cursor over a singlet
            self.singletLeftDown(obj, event)
                # no win_update() needed. It's the responsibility of singletLeftDown to do it if needed.
            return                
        elif isinstance(obj, Atom) and not obj.is_singlet(): # Cursor over a real atom
            self.atomLeftDown(obj, event)
        elif isinstance(obj, Bond) and not obj.is_open_bond(): # Cursor over a bond.
            self.bondLeftDown(obj, event)
        elif isinstance(obj, Jig): # Cursor over a jig.
            self.jigLeftDown(obj, event)
        else: # Cursor is over something else other than an atom, singlet or bond. 
            # The program never executes lines in this else statement since
            # get_obj_under_cursor() only returns atoms, singlets or bonds.
            # [perhaps no longer true, if it ever was -- bruce 060725]
            pass
        
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
                
        return # from leftADown
    
    def leftADrag(self, event):
        """Move selected chunk(s) along its axis (mouse goes up or down)
           and rotate around its axis (left-right) while left dragging
           the selection with keyboard key 'A' pressed
        """
            
        ##See comments of leftDrag()--Huaicai 3/23/05
        if not self.picking: return

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
        '''Do nothing upon double click , while in move mode (pre Alpha9 - experimental)
        '''
	#@@ninad070329  Till Alpha8, it used to Switch to Select Chunks Mode. 
        #for Alpha9, (pr pre Alpha9), it won't do anything. 
	#this implementation might change in future. 
	
        ## Current plans are to merge Select Chunks and Move Chunks modes in A8.
        ##self.o.setMode('SELECTMOLS') # Fixes bug 1182. mark 060301.
        return

    def setup_movetype(self, movetype):

        # Very mysterious: if movetype (a QString) is "Rotate X" or
        # "Rotate Y" or "Rotate Z", then it takes two tries for the
        # visibility changes to take effect. Why is that??? - wware
        # 20061214
        translate = (movetype == 'Translate')
            
        self.w.moveXLabel.setVisible(translate)
        self.w.moveXSpinBox.setVisible(translate)
        self.w.moveYLabel.setVisible(translate)
        self.w.moveYSpinBox.setVisible(translate)
        self.w.moveZLabel.setVisible(translate)
        self.w.moveZSpinBox.setVisible(translate)
        self.w.moveThetaLabel.setVisible(not translate)
        self.w.moveThetaSpinBox.setVisible(not translate)

        self.w.moveDeltaPlusAction.setVisible(translate)
        self.w.moveDeltaMinusAction.setVisible(translate)
        self.w.moveAbsoluteAction.setVisible(translate)
        self.w.rotateThetaPlusAction.setVisible(not translate)
        self.w.rotateThetaMinusAction.setVisible(not translate)

    def moveThetaPlus(self):
        "Rotate the selected chunk(s) by theta (plus)"
        button= self.rotateAroundAxisButtonGroup.checkedButton()
        if button:
            rotype = button.objectName()
        else:
            env.history.message(redmsg("Rotate By Specified Angle: Please press the button \
            corresponding to the axis of rotation"))
            return
        theta = self.rotateThetaSpinBox.value()
        self.moveTheta( rotype, theta)
        
    def moveThetaMinus(self):
        "Rotate the selected chunk(s) by theta (minus)"
        button= self.rotateAroundAxisButtonGroup.checkedButton()
        if button:
            rotype = button.objectName()
        else:
            env.history.message(redmsg("Rotate By Specified Angle: Please press the button \
            corresponding to the axis of rotation"))
            return
        theta = self.rotateThetaSpinBox.value() * -1.0
        self.moveTheta( rotype, theta)
        
    def moveTheta(self, rotype, theta):
        "Rotate the selected chunk(s) /jig(s) around the specified axis by theta (degrees)"
        if not self.o.assy.getSelectedMovables(): 
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return
        
        if rotype == 'Rotate X':
            ma = V(1,0,0) # X Axis
        elif rotype == 'Rotate Y':
            ma = V(0,1,0) # Y Axis
        elif rotype == 'Rotate Z':
            ma = V(0,0,1) # Z Axis
        else:
            print 'modifyMody.moveThetaPlus: Error.  rotype = ', rotype, ', which is undefined.'
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
        
        if self.rotateAsUnitCB.isChecked():
            self.o.assy.rotsel(qrot) # Rotate the selection as a unit.
        else:
            for mol in self.o.assy.selmols: # Rotate each chunk individually.
                mol.rot(qrot)
    
        self.o.gl_update()
        
    def moveDeltaPlus(self):
        "Add X, Y, and Z to the selected chunk(s) current position"
        if not self.o.assy.getSelectedMovables(): 
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return
        offset = get_move_delta_xyz(self)
        self.o.assy.movesel(offset)
        self.o.gl_update()

    def moveDeltaMinus(self):
        "Subtract X, Y, and Z from the selected chunk(s) current position"
        if not self.o.assy.getSelectedMovables(): 
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return
        
        offset = get_move_delta_xyz(self, Plus=False)
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
       
        pt2 = get_move_xyz(self) # pt2 = X, Y, Z values from dashboard.
        offset = pt2 - pt1 # Compute offset for movesel.
        
        self.o.assy.movesel(offset) # Move the selected chunk(s)/jig(s).
    
        # Print history message about what happened.
        if len(movables) == 1:
            msg = "[%s] moved to [X: %.2f] [Y: %.2f] [Z: %.2f]" % (movables[0].name, pt2[0], pt2[1], pt2[2])
        else:
            msg = "Selected chunks/jigs moved by offset [X: %.2f] [Y: %.2f] [Z: %.2f]" % (offset[0], offset[1], offset[2])
        env.history.message(msg)
        self.o.gl_update()
        
    def changeMoveOption(self, action):
        '''Slot for Move Chunks dashboard\'s Move Options
        '''        
        if action == self.w.transXAction:
            self.moveOption = 'TRANSX'
        elif action == self.w.transYAction:
            self.moveOption = 'TRANSY'
        elif action == self.w.transZAction:
            self.moveOption = 'TRANSZ'
        elif action == self.w.rotTransAlongAxisAction_1:
            self.moveOption = 'ROT_TRANS_ALONG_AXIS' 
        else:
            self.moveOption = 'MOVEDEFAULT'
            
            
    def changeRotateOption(self, action):
        '''Change the rotate action
        '''   
        if action == self.w.rotXAction:
            self.rotateOption = 'ROTATEX'
            self.rotateAsUnitCB.hide()
            self.toggleRotationDeltaLabels(show = True)
        elif action == self.w.rotYAction:
            self.rotateOption = 'ROTATEY'
            self.rotateAsUnitCB.hide()
            self.toggleRotationDeltaLabels(show = True)
        elif action == self.w.rotZAction:
            self.rotateOption = 'ROTATEZ'
            self.rotateAsUnitCB.hide()
            self.toggleRotationDeltaLabels(show = True)
        elif action == self.w.rotTransAlongAxisAction_2:
            #do not use the isConstrainedDrag.. flag. Causing bugs and 
            #am in a rush (need this new option for today's release) 
            #-- ninad20070605
            ##self.isConstrainedDragAlongAxis = True
            self.rotateOption = 'ROT_TRANS_ALONG_AXIS' 
            pass
        else:
            self.rotateOption = 'ROTATEDEFAULT'        
            #Hides all the rotation delta labels when  
            #rotateFreeDragAction is checked
            self.toggleRotationDeltaLabels(show = False)
            self.rotateAsUnitCB.show()
    
    def toggleRotationDeltaLabels(self, show=False):
        """ Hide all the rotation delta labels when  
        rotateFreeDragAction is checked """
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
            
            

    def skip(self):
        pass

    pass # end of class modifyMode
