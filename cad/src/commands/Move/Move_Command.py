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
import foundation.env as env
import math
from Numeric import dot
import foundation.changes as changes
from commands.Move.MovePropertyManager import MovePropertyManager
from commands.SelectChunks.SelectChunks_Command import SelectChunks_basicCommand
from command_support.GraphicsMode_API import GraphicsMode_API
from geometry.BoundingBox import BBox
from utilities.Log import redmsg
from geometry.VQT import V, Q
from utilities.debug import print_compact_traceback
from commands.Translate.TranslateChunks_GraphicsMode import TranslateChunks_GraphicsMode
from commands.Rotate.RotateChunks_GraphicsMode import RotateChunks_GraphicsMode
from ne1_ui.toolbars.Ui_MoveFlyout import MoveFlyout

class Move_basicCommand(SelectChunks_basicCommand):
    """
    """
    commandName = 'MODIFY'
    featurename = "Move Chunks Mode"
    from utilities.constants import CL_EDIT_GENERIC
    command_level = CL_EDIT_GENERIC

    propMgr = None
    pw = None

    command_can_be_suspended = True
    command_should_resume_prevMode = False
    command_has_its_own_PM = True
    
    flyoutToolbar = None
    
    #START new command API methods =============================================
    #currently [2008-08-01 ] also called in by self,init_gui and 
    #self.restore_gui.
    
    def command_enter_PM(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_PM()  for documentation
        """
        #important to check for old propMgr object. Reusing propMgr object 
        #significantly improves the performance.
        if not self.propMgr:
            self.propMgr = self._createPropMgrObject()
            #@bug BUG: following is a workaround for bug 2494.
            #This bug is mitigated as propMgr object no longer gets recreated
            #for modes -- ninad 2007-08-29
            changes.keep_forever(self.propMgr)  
            
        self.propMgr.show()        
        self.propMgr.set_move_xyz(0, 0, 0) # Init X, Y, and Z to zero
        self.propMgr.set_move_delta_xyz(0,0,0) # Init DelX,DelY, DelZ to zero
        
    
    def command_exit_PM(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_PM() for documentation
        """
        
        if self.propMgr:
            self.propMgr.close()
            
    def command_enter_flyout(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_flyout()  for documentation
        """
        if self.flyoutToolbar is None:
            self.flyoutToolbar = self._createFlyoutToolBarObject() 
        self.flyoutToolbar.activateFlyoutToolbar()  
        
    def _createFlyoutToolBarObject(self):
        """
        Create a flyout toolbar to be shown when this command is active. 
        Overridden in subclasses. 
        @see: PasteFromClipboard_Command._createFlyouttoolBar()
        @see: self.command_enter_flyout()
        """
        flyoutToolbar = MoveFlyout(self) 
        return flyoutToolbar
    
    def _createPropMgrObject(self):
        propMgr = MovePropertyManager(self)
        return propMgr
        
            
    def command_exit_flyout(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_flyout()  for documentation
        """
        if self.flyoutToolbar:
            self.flyoutToolbar.deActivateFlyoutToolbar()
            
    def command_enter_misc_actions(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_misc_actions()  for documentation
        """
        pass
                
            
    def command_exit_misc_actions(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_misc_actions()  for documentation
        """
        self.w.toolsMoveMoleculeAction.setChecked(False) 
        self.w.rotateComponentsAction.setChecked(False)       
    
    #END new command API methods ==============================================

    def init_gui(self):
        """
        Do changes to the GUI while entering this mode. This includes opening 
        the property manager, updating the command toolbar, connecting widget 
        slots etc. 
        
        Called once each time the mode is entered; should be called only by code 
        in modes.py
        
        @see: L{self.restore_gui}
        """        
        self.command_enter_misc_actions()
        self.command_enter_PM() 
        self.command_enter_flyout()

    def restore_gui(self):
        """
        Do changes to the GUI while exiting this mode. This includes closing 
        this mode's property manager, updating the command toolbar, 
        disconnecting widget slots etc. 
        @see: L{self.init_gui}
        """
        self.command_exit_misc_actions()
        self.command_exit_flyout()
        self.command_exit_PM()

    def _acceptLineModePoints(self, params): #bruce 080801, revises acceptParamsFromTemporaryMode
        """
        Accept returned points from the LineMode request command.
        """
        ### REVIEW: can this be called with params == None
        # if LineMode is terminated early?
        
        (points,) = params
        del params
        
        #Usually points will contain 2 items. But if user abruptly terminates
        #the temporary mode, this might not be true. So move the chunk by offset
        #only when you have got 2 points!  Ninad 2007-10-16
        if len(points) == 2:
            startPoint = points[0]
            endPoint = points[1]
            offset = endPoint - startPoint
            movables = self.graphicsMode.getMovablesForLeftDragging()
            self.assy.translateSpecifiedMovables(offset, movables = movables)
            self.o.gl_update()

        self.propMgr.moveFromToButton.setChecked(False)

        #For Rotate about point tool. Maybe we should do the following
        #only when the graphics mode is Rotate graphics mode? Okay for now.
        #feature implemented just before FNANO 08 cleanup.
        # -- Ninad 2008-04-20
        # [note: this is no longer called for RotateAboutPoint;
        #  see _acceptRotateAboutPointResults for that -- bruce 080801]
        self.propMgr.rotateAboutPointButton.setChecked(False) #k needed?
        return

    def _acceptRotateAboutPointResults(self, params): #bruce 080801, revises acceptParamsFromTemporaryMode
        """
        Accept results (empty tuple) from the RotateAboutPoint request command.
        (This exists in order to perform a side effect, and since
         callRequestCommand requires a results callback.)
        """
        ### REVIEW: can this be called with params == None
        # if RotateAboutPoint is terminated early?
        del params
        self.propMgr.moveFromToButton.setChecked(False)  # above needed? 
        self.propMgr.rotateAboutPointButton.setChecked(False)
        return


    def rotateAboutPointTemporaryCommand(self, isChecked = False):
        """
        @see: self.moveFromToTemporaryMode
        """
        #@TODO: clean this up. This was written just after Rattlesnake rc2
        #for FNANO presentation -- Ninad 2008-04-17

        if isChecked:
            self.propMgr.rotateStartCoordLineEdit.setEnabled(isChecked)
            msg = "Click inside the 3D workspace to define two points" \
                "of a line. The selection will be rotated about the first point"\
                " in the direction specified by that line"

            self.propMgr.updateMessage(msg)
            
            # following was revised by bruce 080801
            self.commandSequencer.callRequestCommand( 'RotateAboutPoint',
                 ## provide_arguments = self.provideParamsForTemporaryMode,
                 arguments = (2,), # number of mouse click points to accept
                 accept_results = self._acceptRotateAboutPointResults
             )
        else:
            currentCommand = self.commandSequencer.currentCommand
            if currentCommand.commandName == "RotateAboutPoint":
                currentCommand.Done(exit_using_done_or_cancel_button = False)
            self.propMgr.rotateStartCoordLineEdit.setEnabled(False)
            self.propMgr.updateMessage()

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
            msg = "Click inside the 3D workspace to define two endpoints " \
                "of a line. The selection will be moved by the offset "\
                "vector defined by these line endpoints."

            self.propMgr.updateMessage(msg)
            # following was revised by bruce 080801
            self.commandSequencer.callRequestCommand( 'LineMode',
                 ## provide_arguments = self.provideParamsForTemporaryMode,
                 arguments = (2,), # number of mouse click points to accept
                 accept_results = self._acceptLineModePoints
             )
        else:
            self.propMgr.startCoordLineEdit.setEnabled(False)
            self.propMgr.updateMessage()

    def rotateThetaPlus(self):
        """
        Rotate the selected chunk(s) by theta (plus)
        """
        button = self.propMgr.rotateAroundAxisButtonRow.checkedButton()
        if button:
            rotype = str(button.text())
        else:
            env.history.message(redmsg("Rotate By Specified Angle:" 
                                       "Please press the button "\
                                       "corresponding to the axis of rotation"))
            return
        theta = self.propMgr.rotateThetaSpinBox.value()
        self.rotateTheta( rotype, theta)

    def rotateThetaMinus(self):
        """
        Rotate the selected chunk(s) by theta (minus)
        """
        button = self.propMgr.rotateAroundAxisButtonRow.checkedButton()
        if button:
            rotype = str(button.text())
        else:
            env.history.message(redmsg("Rotate By Specified Angle:"\
                                       " Please press the button "\
                                       "corresponding to the axis of rotation"))
            return
        theta = self.propMgr.rotateThetaSpinBox.value() * -1.0
        self.rotateTheta( rotype, theta)

    def rotateTheta(self, rotype, theta):
        """
        Rotate the selected chunk(s) /jig(s) around the specified axis
        by theta (degrees)
        """
        movables = self.graphicsMode.getMovablesForLeftDragging()
        if not movables:
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
            # Rotate the selection as a unit.
            self.assy.rotateSpecifiedMovables(qrot,
                                              movables)
        else:
            for item in movables:
                try:
                    item.rot(qrot)
                except AssertionError:
                    print_compact_traceback("Selected movable doesn't have"\
                                            "rot method?")

        self.o.gl_update()

    def transDeltaPlus(self):
        """
        Add X, Y, and Z to the selected chunk(s) current position
        """
        movables = self.graphicsMode.getMovablesForLeftDragging()
        if not movables:
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return
        offset = self.propMgr.get_move_delta_xyz()
        self.assy.translateSpecifiedMovables(offset,
                                             movables = movables)
        self.o.gl_update()

    def transDeltaMinus(self):
        """
        Subtract X, Y, and Z from the selected chunk(s) current position
        """
        movables = self.graphicsMode.getMovablesForLeftDragging()
        if not movables:
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return

        offset = self.propMgr.get_move_delta_xyz(Plus=False)
        self.assy.translateSpecifiedMovables(offset,
                                             movables = movables)
        self.o.gl_update()

    def moveAbsolute(self):
        """
        Move selected chunk(s), jig(s) to absolute X, Y, and Z by computing
        the bbox center of everything as if they were one big chunk, then move
        everything as a unit.
        """
        movables = self.graphicsMode.getMovablesForLeftDragging()
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
        offset = pt2 - pt1 # Compute offset for translating the selection

        self.assy.translateSpecifiedMovables(offset,
                                             movables = movables)

        # Print history message about what happened.
        if len(movables) == 1:
            msg = "[%s] moved to [X: %.2f] [Y: %.2f] [Z: %.2f]" % (movables[0].name, pt2[0], pt2[1], pt2[2])
        else:
            msg = "Selected chunks/jigs moved by offset [X: %.2f] [Y: %.2f] [Z: %.2f]" % (offset[0], offset[1], offset[2])
        env.history.message(msg)
        self.o.gl_update()
        return

class Move_Command(Move_basicCommand):
    """
    @see: B{Move_basicCommand}
    @see: cad/doc/splitting_a_mode.py
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




