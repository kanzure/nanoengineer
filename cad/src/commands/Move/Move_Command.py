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
from PyQt4 import QtGui
from PyQt4.Qt import SIGNAL
from commands.Move.MovePropertyManager import MovePropertyManager
from utilities.icon_utilities import geticon
from commands.SelectChunks.SelectChunks_Command import SelectChunks_basicCommand
from command_support.GraphicsMode_API import GraphicsMode_API
from geometry.BoundingBox import BBox
from utilities.Log import redmsg
from geometry.VQT import V, Q, cross, norm
from utilities.debug import print_compact_traceback
from utilities.constants import black
from commands.Translate.TranslateChunks_GraphicsMode import TranslateChunks_GraphicsMode
from commands.Rotate.RotateChunks_GraphicsMode import RotateChunks_GraphicsMode
from model.chem import Atom #for instance check only as of 2008-04-17
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction

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

##    def NEWER_acceptParamsFromTemporaryMode(self, temporaryModeName, params):
##        """
##        NOTE: see selectMolsMode.acceptParamsFromTemporaryMode for detailed
##        comment. This needs to be a API method. This is a temporary
##        implementation
##        """
##
##        if len(params) == 2:
##            mouseClickPoints, pivotAtom = params
##
##            #Mouseclick points should contain 2 points. But if user abruptly
##            #terminates  the temporary mode, this might not be true. So rotate
##            #only when the it has 2 points!
##
##            if len(mouseClickPoints) < 2:
##                self.propMgr.rotateAboutPointButton.setChecked(False)
##                return
##
##
##            startPoint = mouseClickPoints[0]
##            endPoint = mouseClickPoints[1]
##            #initial assignment of reference_vec. The selected movables will be
##            #rotated by the angle between this vector and the lineVector
##            reference_vec = self.glpane.right
##            if isinstance(pivotAtom, Atom) and not pivotAtom.molecule.isNullChunk() :
##                reference_vec, node_junk = pivotAtom.molecule.getAxis_of_self_or_eligible_parent_node()
##                del node_junk
##            else:
##                reference_vec = self.glpane.right
##
##            lineVector = endPoint - startPoint
##
##            quat1 = Q(lineVector, reference_vec)
##
##            print "***angle =", (quat1.angle)*180/math.pi
##            print "***dot(lineVector, reference_vec)=", dot(lineVector, reference_vec)
##
##            if dot(lineVector, reference_vec) < 0:
##                theta = math.pi - quat1.angle
##            else:
##                theta = quat1.angle
##
##            print "*** new angle =", theta*180/math.pi
##
##
##            rot_axis = cross(lineVector, reference_vec)
##
##            cross_prod_1 = norm(cross(reference_vec, rot_axis))
##            cross_prod_2 = norm(cross(lineVector, rot_axis))
##
##            print "***dot(cross_prod_1, cross_prod_2) =", dot(cross_prod_1, cross_prod_2)
##
##            if dot(cross_prod_1, cross_prod_2) < 0:
##                quat2 = Q(rot_axis,  theta)
##            else:
##                quat2 = Q(rot_axis,  - theta)
##
##            movables = self.graphicsMode.getMovablesForLeftDragging()
##            self.assy.rotateSpecifiedMovables(
##                quat2,
##                movables = movables,
##                commonCenter = startPoint)
##
##            self.o.gl_update()
##
##        self.propMgr.rotateAboutPointButton.setChecked(False)
##
##    def EXPERIMENTAL_acceptParamsFromTemporaryMode(self, temporaryModeName, params):
##        """
##        NOTE: see electMolsMode.acceptParamsFromTemporaryMode for detail
##        comment. This needs to be a API method. This is a temporary
##        implementation
##        """
##        DEBUG_ROTATE_ABOUT_POINT = False
##
##        if DEBUG_ROTATE_ABOUT_POINT:
##            if len(params) == 2:
##                mouseClickPoints, pivotAtom = params
##
##                #Mouseclick points should contain 2 points. But if user abruptly
##                #terminates  the temporary mode, this might not be true. So rotate
##                #only when the it has 2 points!
##
##                if len(mouseClickPoints) < 2:
##                    self.propMgr.rotateAboutPointButton.setChecked(False)
##                    return
##
##
##                startPoint = mouseClickPoints[0]
##                endPoint = mouseClickPoints[1]
##                #initial assignment of reference_vec. The selected movables will be
##                #rotated by the angle between this vector and the lineVector
##                reference_vec = self.glpane.right
##                if isinstance(pivotAtom, Atom) and not pivotAtom.molecule.isNullChunk():
##                    mol = pivotAtom.molecule
##                    reference_vec, node_junk = mol.getAxis_of_self_or_eligible_parent_node(
##                        atomAtVectorOrigin = pivotAtom)
##                    del node_junk
##                else:
##                    reference_vec = self.glpane.right
##
##                lineVector = endPoint - startPoint
##
##                quat1 = Q(lineVector, reference_vec)
##
##                #DEBUG Disabled temporarily . will not be used
##                ##if dot(lineVector, reference_vec) < 0:
##                    ##theta = math.pi - quat1.angle
##                ##else:
##                    ##theta = quat1.angle
##
##                #TEST_DEBUG-- Works fine
##                theta = quat1.angle
##
##                rot_axis = cross(lineVector, reference_vec)
##
##                if dot(lineVector, reference_vec) < 0:
##                    rot_axis = - rot_axis
##
##                cross_prod_1 = norm(cross(reference_vec, rot_axis))
##                cross_prod_2 = norm(cross(lineVector, rot_axis))
##
##                if dot(cross_prod_1, cross_prod_2) < 0:
##                    quat2 = Q(rot_axis,  theta)
##                else:
##                    quat2 = Q(rot_axis,  - theta)
##
##
##                movables = self.graphicsMode.getMovablesForLeftDragging()
##                self.assy.rotateSpecifiedMovables(
##                    quat2,
##                    movables = movables,
##                    commonCenter = startPoint)
##
##                self.o.gl_update()
##
##        self.propMgr.rotateAboutPointButton.setChecked(False)

##    def acceptParamsFromTemporaryMode(self, temporaryModeName, params):
##        """
##        NOTE: see selectMolsMode.acceptParamsFromTemporaryMode for detailed
##        comment. This needs to be an API method. This is a temporary
##        implementation.
##        """

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
        self.propMgr.moveFromToButton.setChecked(False) #k needed?
        self.propMgr.rotateAboutPointButton.setChecked(False)
        return

##    def provideParamsForTemporaryMode(self, temporaryModeName = None):
##        """
##        NOTE: See selectMolsMode.provideParamsForTemporaryMode
##        for detailed comment. This is a temporary implementation.
##        @see: LineMode_GM._drawCursorText
##        """
##        temporaryModeNames = ('LineMode', 'RotateAboutPoint', None)
##
##        if temporaryModeName in temporaryModeNames:
##            #This is the number of mouse clicks that the temporary mode accepts
##            mouseClickLimit = 2
##            return (mouseClickLimit,)
##        return ()

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
            ## self.commandSequencer.userEnterTemporaryCommand('RotateAboutPoint')
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
            env.history.message(redmsg("Rotate By Specified Angle: Please press the button \
                                   corresponding to the axis of rotation"))
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
            env.history.message(redmsg("Rotate By Specified Angle: Please press the button \
                                   corresponding to the axis of rotation"))
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
        """
        Returns a tuple that contains mode spcific actionlists in the
        added in the flyout toolbar of the mode.
        CommandToolbar._createFlyoutToolBar method calls this
        @return: params: A tuple that contains 3 lists:
        (subControlAreaActionList, commandActionLists, allActionsList)
        """
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

        self.exitMoveAction = NE1_QWidgetAction(self.w, 
                                                  win = self.w)
        self.exitMoveAction.setText("Exit Move")
        self.exitMoveAction.setWhatsThis("Exits Move Mode")
        self.exitMoveAction.setCheckable(True)
        self.exitMoveAction.setChecked(True)
        self.exitMoveAction.setIcon(
            geticon("ui/actions/Toolbars/Smart/Exit.png"))
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




