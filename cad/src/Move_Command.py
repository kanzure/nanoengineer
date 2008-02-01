# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Move_Command.py 

The 'Command' part of the Move Mode (Move_Command and 
Move_GraphicsMode are the two split classes of the old 
modifyMode)  It provides the command object for its GraphicsMode class. 
The Command class defines anything related to the 'command half' of the mode -- 
For example: 
- Anything related to its current Property Manager, its settings or state
- The model operations the command does (unless those are so simple
  that the mouse event bindings in the _GM half can do them directly
  and the code is still clean, *and* no command-half subclass needs
  to override them).

@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.


History:
See Move_GraphicsMode.py

"""
import env
import math
import changes
from PyQt4 import QtGui
from PyQt4.Qt import SIGNAL
from MovePropertyManager import MovePropertyManager
from icon_utilities import geticon
from SelectChunks_Command import SelectChunks_basicCommand
from Move_GraphicsMode  import Move_GraphicsMode
from GraphicsMode_API import GraphicsMode_API
from geometry.BoundingBox import BBox
from utilities.Log import redmsg
from geometry.VQT import V, Q, A, norm, vlen
from debug import print_compact_traceback

from TranslateChunks_GraphicsMode import TranslateChunks_GraphicsMode
from RotateChunks_GraphicsMode import RotateChunks_GraphicsMode

class Move_basicCommand(SelectChunks_basicCommand):
    """
    """    
    commandName = 'MODIFY'
    default_mode_status_text = "Mode: Move Chunks"
    featurename = "Move Chunks Mode"
    propMgr = None
    pw = None
    
    command_can_be_suspended = True
    command_should_resume_prevMode = False 
    command_has_its_own_gui = True
        
    def init_gui(self):	
        if not self.propMgr:
            self.propMgr = MovePropertyManager(self)
            #@bug BUG: following is a workaround for bug 2494
            changes.keep_forever(self.propMgr)

        self.propMgr.show()                	
        self.updateCommandToolbar(bool_entering = True)

        # connect signals (these all need to be disconnected in restore_gui)                
        self.connect_or_disconnect_signals(True)

        self.propMgr.set_move_xyz(0, 0, 0) # Init X, Y, and Z to zero
        self.propMgr.set_move_delta_xyz(0,0,0) # Init DelX,DelY, DelZ to zero
    
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
        self.updateCommandToolbar(bool_entering = False)
        self.w.toolsMoveMoleculeAction.setChecked(False) # toggle on the Move Chunks icon
        self.w.rotateComponentsAction.setChecked(False)
        self.connect_or_disconnect_signals(False)        
        if self.propMgr:	    
            self.propMgr.close()
    
    def acceptParamsFromTemporaryMode(self, temporaryModeName, params):
        """
	NOTE: see electMolsMode.acceptParamsFromTemporaryMode for detail 
	comment. This needs to be a API method. This is a temporary
	implementation	
        """
        #Usually params will contain 2 items. But if user abruptly terminates  
        #the temporary mode, this might not be true. So move the chunk by offset
        #only when you have got 2 points!  Ninad 2007-10-16
        if len(params) == 2:
            startPoint = params[0]
            endPoint = params[1]
            offset = endPoint - startPoint	
            self.o.assy.movesel(offset)
            self.o.gl_update()

        self.propMgr.moveFromToButton.setChecked(False)		
    
    def provideParamsForTemporaryMode(self, temporaryModeName):
        """
	NOTE: See selectMolsMode.provideParamsForTemporaryMode 
	for detail comment. This needs to be a API method. This is a temporary
	implementation
        """

        if temporaryModeName == "LineMode":
            #This is the number of mouse clicks that the temporary mode accepts
            mouseClickLimit = 2
            return (mouseClickLimit)
    
    def moveFromToTemporaryMode(self, isChecked = False):
        """
	Move the selected entities by the offset vector specified by the 
	endpoints of a line. To use this feature, click on 'Move From/To button'
	in the PM and specify the two endpoints from GLPane. The program enters
	a temporary mode while you do that and then uses the data collected 
	while in temporary mode (i.e. two endpoints) to move the selection. 

	TODO: Note that the endpoints always assume GLPane depth. As of today, 
	the temporary mode API knows nothing about the highlighting. Once it 
	is implemented,  we can then specify atom centers etc as reference 
	points. See comments in LineMode for further details. 
	"""
        if isChecked:	    
            self.propMgr.startCoordLineEdit.setEnabled(isChecked)
            msg = "Click inside the 3D workspace to define two endpoints" \
                "of a line. The selection will be moved by the offset "\
                "vector defined by these line endpoints."

            self.propMgr.updateMessage(msg)

            commandSequencer = self.commandSequencer
            currentCommand = commandSequencer.currentCommand
            
            if currentCommand.commandName != "LineMode":
                commandSequencer.userEnterTemporaryCommand(
                    'LineMode')
                return
        else:
            self.propMgr.startCoordLineEdit.setEnabled(False)
            self.propMgr.updateMessage()
    
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
    
    #Command Toolbar related methods to be revised==============================
    def updateCommandToolbar(self, bool_entering = True):#Ninad 20070618
        """
        Update the command toolbar.
        """
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

        self.w.commandToolbar.updateCommandToolbar(action,
                                                   obj, 
                                                   entering = bool_entering)
    
    def getFlyoutActionList(self): #Ninad 20070618
        """ Returns a tuple that contains mode spcific actionlists in the 
	added in the flyout toolbar of the mode. 
	CommandToolbar._createFlyoutToolBar method calls this 
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

    
class Move_Command(Move_basicCommand):
    """
    @see: B{Move_basicCommand}
    @see: splitting_a_mode.py
    """
    GraphicsMode_class = TranslateChunks_GraphicsMode
    
    def __init__(self, commandSequencer):
        Move_basicCommand.__init__(self, commandSequencer)
        self._create_GraphicsMode()
        self._post_init_modify_GraphicsMode()
        return
        
    def _create_GraphicsMode(self):
        GM_class = self.GraphicsMode_class
        assert issubclass(GM_class, GraphicsMode_API)
        args = [self] 
        kws = {} 
        self.graphicsMode = GM_class(*args, **kws)
        
        self.translate_graphicsMode = TranslateChunks_GraphicsMode(*args, **kws)
        self.rotate_graphicsMode  = RotateChunks_GraphicsMode(*args, **kws)
  
    def _post_init_modify_GraphicsMode(self):
        pass
    
    def switchGraphicsModeTo(self, newGraphicsMode = 'TRANSLATE_CHUNKS'):
        """
        Switch graphics mode of self to the one specified 
        by the client. 
        Changing graphics mode while remaining in the same command has certain 
        advantages and it also bypasses some code related to entering a new 
        command. 
        @param newGraphicsMode: specifies the new graphics mode to switch to
        @type  newGraphicsMode: string
        @see: B{MovePropertyManager.activate_translateGroupBox} 
        """
        #TODO: Make this a general API method if need arises - Ninad 2008-01-25
        assert newGraphicsMode in ['TRANSLATE_CHUNKS', 'ROTATE_CHUNKS']
        
        if newGraphicsMode == 'TRANSLATE_CHUNKS':
            if self.graphicsMode is self.translate_graphicsMode:
                return
            self.graphicsMode = self.translate_graphicsMode
            self.graphicsMode.Enter_GraphicsMode()
            self.glpane.update_after_new_graphicsMode()
        elif newGraphicsMode == 'ROTATE_CHUNKS':
            if self.graphicsMode is self.rotate_graphicsMode:
                return 
            self.graphicsMode = self.rotate_graphicsMode
            self.graphicsMode.Enter_GraphicsMode()
            self.glpane.update_after_new_graphicsMode()
            
    
    

