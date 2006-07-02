# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
modifyMode.py

$Id$

bruce 050913 used env.history in some places.
"""

from selectMode import *
from widgets import FloatSpinBox
from HistoryWidget import redmsg
import env

def do_what_MainWindowUI_should_do(w):
    'Populate the Move Chunks dashboard'
    
    w.moveChunksDashboard.clear()
    
    w.moveChunksLabel = QLabel(w.moveChunksDashboard,"Move Chunks")
    w.moveChunksLabel.setText(" Move Chunks ")
    w.moveChunksDashboard.addSeparator()

    w.moveFreeAction.addTo(w.moveChunksDashboard)
    
    w.moveChunksDashboard.addSeparator()
    
    w.transXAction.addTo(w.moveChunksDashboard)
    w.transYAction.addTo(w.moveChunksDashboard)
    w.transZAction.addTo(w.moveChunksDashboard)
    
    w.moveChunksDashboard.addSeparator()
    
    movetype_qvbox = QVBox(w.moveChunksDashboard)
    w.movetype_combox = QComboBox(0,movetype_qvbox,"movetype_combox")
    w.movetype_combox.insertItem('Translate')
    w.movetype_combox.insertItem('Rotate X')
    w.movetype_combox.insertItem('Rotate Y')
    w.movetype_combox.insertItem('Rotate Z')
    
    w.moveXLabel = QLabel(" X ", w.moveChunksDashboard)
    w.moveXSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveXSpinBox")
    w.moveXSpinBox.setSuffix(" A")
    QToolTip.add(w.moveXSpinBox,'Delta X (Angstroms)')
    w.moveYLabel = QLabel(" Y ", w.moveChunksDashboard)
    w.moveYSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveYSpinBox")
    w.moveYSpinBox.setSuffix(" A")
    QToolTip.add(w.moveYSpinBox,'Delta Y (Angstroms)')
    w.moveZLabel = QLabel(" Z ", w.moveChunksDashboard)
    w.moveZSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveZSpinBox")
    w.moveZSpinBox.setSuffix(" A")
    QToolTip.add(w.moveZSpinBox,'Delta Z (Angstroms)')
    w.moveThetaLabel = QLabel(" Theta ", w.moveChunksDashboard)
    w.moveThetaSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveThetaSpinBox")
    QToolTip.add(w.moveThetaSpinBox,'Rotation (Degrees)')
    w.moveThetaSpinBox.setMaxValue(36000) # Actually 360
    w.moveThetaSpinBox.setMinValue(-36000) # Actually -360
    
    w.moveDeltaPlusAction.addTo(w.moveChunksDashboard)
    w.moveDeltaMinusAction.addTo(w.moveChunksDashboard)
    w.moveAbsoluteAction.addTo(w.moveChunksDashboard)
    w.moveThetaPlusAction.addTo(w.moveChunksDashboard)
    w.moveThetaMinusAction.addTo(w.moveChunksDashboard)
    
    w.moveChunksDashboard.addSeparator()
    
    # I needed this for nanocar animation. Mark 060524.
    w.moveChunksDashboard.rotateAsUnitCB = QCheckBox("Rotate as unit", w.moveChunksDashboard)
    w.moveChunksDashboard.rotateAsUnitCB.setChecked(1)
    QToolTip.add(w.moveChunksDashboard.rotateAsUnitCB,'Rotate selection as a unit')
    
    w.moveChunksDashboard.addSeparator()
    
    w.toolsDoneAction.addTo(w.moveChunksDashboard)

def set_move_xyz(win,x,y,z):
    '''Set values of X, Y and Z in the dashboard.
    '''
    self = win
    self.moveXSpinBox.setFloatValue(x)
    self.moveYSpinBox.setFloatValue(y)
    self.moveZSpinBox.setFloatValue(z)

def get_move_xyz(win, Plus = True):
    '''Returns X, Y and Z values in the dashboard based on Plus.
    If Plus is True, returns x, y, z
    If Plus is False, returns -x, -y, -z
    '''
    self = win
    x = self.moveXSpinBox.floatValue()
    y = self.moveYSpinBox.floatValue()
    z = self.moveZSpinBox.floatValue()
    if Plus: return (x,y,z) # Plus
    else: return (-x, -y, -z) # Minus
    
class modifyMode(selectMolsMode): # changed superclass from basicMode to selectMolsMode.  mark 060301.
    "[bruce comment 040923:] a transient mode entered from selectMode in response to certain mouse events"

    # class constants
    backgroundColor = 254/255.0, 173/255.0, 246/255.0
    gridColor = 52/255.0, 128/255.0, 26/255.0
    modename = 'MODIFY'
    default_mode_status_text = "Mode: Move Chunks"
    
    MOVEOPTS = [ 'MOVEDEFAULT', 'TRANSX', 'TRANSY', 'TRANSZ' ]
    
    # class variables
    moveOption = 'MOVEDEFAULT'
    axis = 'X'
    RotationOnly = False
    TranslationOnly = False
    
    # no __init__ method needed

    def Enter(self):
        basicMode.Enter(self)
        self.o.assy.selectParts()
        self.dragdist = 0.0
        
    # (see basicMode.Done.__doc__ for the ones we don't override here [bruce 040923])

    def init_gui(self):
        self.w.toolsMoveMoleculeAction.setOn(1) # toggle on the Move Chunks icon
        # connect signals (these all need to be disconnected in restore_gui)
        self.connect_or_disconnect_signals(True)
        self.w.moveChunksDashboard.show() # show the Move Molecules dashboard
        
        set_move_xyz(self.w, 0, 0, 0) # Init X, Y, and Z to zero
        self.w.moveThetaSpinBox.setFloatValue(0) # Init Theta spinbox to zero
        self.setup_movetype(self.w.movetype_combox.currentText())

        # Always reset the dashboard icon to "Move Free" when entering MODIFY mode.
        # Mark 050410
        self.w.moveFreeAction.setOn(1) # toggle on the Move Free action on the dashboard
        self.moveOption = 'MOVEDEFAULT'
        
    def connect_or_disconnect_signals(self, connect): # mark 060304.
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
        change_connect(self.w.MoveOptionsGroup, SIGNAL("selected(QAction *)"), self.changeMoveOption)
        change_connect(self.w.moveDeltaPlusAction, SIGNAL("activated()"), self.moveDeltaPlus)
        change_connect(self.w.moveDeltaMinusAction, SIGNAL("activated()"), self.moveDeltaMinus)
        change_connect(self.w.moveAbsoluteAction, SIGNAL("activated()"), self.moveAbsolute)
        change_connect(self.w.moveThetaPlusAction, SIGNAL("activated()"), self.moveThetaPlus)
        change_connect(self.w.moveThetaMinusAction, SIGNAL("activated()"), self.moveThetaMinus)
        change_connect(self.w.movetype_combox, SIGNAL("activated(const QString&)"), self.setup_movetype)
        
    def restore_gui(self):
        # disconnect signals which were connected in init_gui [bruce 050728]
        self.connect_or_disconnect_signals(False)
        self.w.moveChunksDashboard.hide()
        
    def keyPress(self,key):
        basicMode.keyPress(self, key)

        # For these key presses, we toggle the Action item, which will send 
        # an event to changeMoveMode, where the business is done.
        # Mark 050410
        if key == Qt.Key_X:
            self.w.transXAction.setOn(1) # toggle on the Translate X action item
        elif key == Qt.Key_Y:
            self.w.transYAction.setOn(1) # toggle on the Translate Y action item
        elif key == Qt.Key_Z:
            self.w.transZAction.setOn(1) # toggle on the Translate Z action item
            
        # R and T keys constrain movement to rotation or translation only while they are pressed.
        elif key == Qt.Key_R:
            self.RotationOnly = True # Rotation only.
        elif key == Qt.Key_T:
            self.TranslationOnly = True # Translation only.
                
    def keyRelease(self,key):
        basicMode.keyRelease(self, key)

        if key == Qt.Key_X or key == Qt.Key_Y or key == Qt.Key_Z: 
            self.w.moveFreeAction.setOn(1) # toggle on the Move Chunks icon
            self.movingPoint = None # Fixes bugs 583 and 674 along with change in leftDrag().  Mark 050623
        elif key == Qt.Key_R:
            self.RotationOnly = False # Unconstrain translation.
        elif key == Qt.Key_T:
            self.TranslationOnly = False # Unconstrain rotation.
            
    def update_cursor_for_no_MB(self):
        '''Update the cursor for 'Move Chunks' mode.
        '''
        if self.o.modkeys is None:
            self.o.setCursor(self.w.MoveSelectCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.MoveAxisRotateMolCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.MoveFreeRotateMolCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB(): Invalid modkey=", self.o.modkeys
        return
           
    def leftDown(self, event):
        """Move the selected object(s).
        """
##        from constants import GL_FAR_Z
        
        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0
        self.transDelta = 0 # X, Y or Z deltas for translate.
        self.rotDelta = 0 # delta for constrained rotations.
        self.moveOffset = [0.0, 0.0, 0.0] # X, Y and Z offset for move.
        
        if not self.o.assy.getSelectedMovables(): return
        
        # This needs to be refactored further into move and translate methods. mark 060301.
        
        # Move section
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
            #bruce 060316 replaced equivalent old code with this new method
        self.startpt = self.movingPoint # Used in leftDrag() to compute move offset during drag op.
        
        # end of Move section

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
            else: print "modifyMode: Error - unknown moveOption value =", self.moveOption
        
            ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
            # When in the front view, right = 1,0,0 and up = 0,1,0, so ma will be computed as 0,0.
            # This creates a special case problem when the user wants to constrain rotation around
            # the Z axis because Zmat will be zero.  So we have to test for this case (ma = 0,0) and
            # fix ma to -1,0.  This was needed to fix bug 537.  Mark 050420
            if ma[0] == 0.0 and ma[1] == 0.0: ma = [-1.0, 0.0] 
            self.Zmat = A([ma,[-ma[1],ma[0]]])

        # end of Translate section
        
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
        if not self.picking: return
        
        if not self.o.assy.getSelectedMovables(): return
        
        # Fixes bugs 583 and 674 along with change in keyRelease.  Mark 050623
        if self.movingPoint is None: self.leftDown(event) # Fix per Bruce's email.  Mark 050704

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
        
        # Translate/Rotate section
        else: 
        
            w=self.o.width+0.0
            h=self.o.height+0.0
            deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())
            a =  dot(self.Zmat, deltaMouse)
            dx,dy =  a * V(self.o.scale/(h*0.5), 2*pi/w)
            
            if self.RotationOnly: dx = 0.0
            if self.TranslationOnly: dy = 0.0

            if self.moveOption == 'TRANSX': ma = V(1,0,0) # X Axis
            elif self.moveOption == 'TRANSY': ma = V(0,1,0) # Y Axis
            elif self.moveOption == 'TRANSZ': ma = V(0,0,1) # Z Axis
            else: 
                print "modifyMode.leftDrag: Error - unknown moveOption value =", self.moveOption
                return

            self.transDelta += dx # Increment translation delta
            qrot = Q(ma,-dy) # Quat for rotation delta.
            self.rotDelta += qrot.angle *180.0/pi * sign(dy) # Increment rotation delta (and convert to degrees)
            
            self.o.assy.movesel(dx*ma) # [Huaicai 8/30/05: call this method instead]
            self.o.assy.rotsel(qrot) # [Huaicai 8/30/05: call this method instead]
            
            # Print status bar msg indicating the current translation and rotation delta.
            if self.o.assy.selmols:
                msg = "%s delta: [%.2f Angstroms] [%.2f Degrees]" % (self.axis, self.transDelta, self.rotDelta)
                env.history.statusbar_msg(msg)
            
        # end of Translate section

        # common finished code
        
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()
        
    # end of leftDrag

    def leftUp(self, event):
        self.EndPick(event, START_NEW_SELECTION)
        
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
        
        if self.w.moveChunksDashboard.rotateAsUnitCB.isChecked():
            self.o.assy.rotsel(q) # Rotate the selection as a unit.
        else:
            for mol in self.o.assy.selmols: # Rotate each chunk individually.
                mol.rot(q)

        self.o.gl_update()

    def leftCntlUp(self, event):
        self.EndPick(event, SUBTRACT_FROM_SELECTION)
    
    def leftShiftDown(self, event):
        """ Set up for sliding and/or rotating the selected chunk(s) along/around its own axis.
        """
        if self.o.modkeys == 'Shift+Control':
            self.start_selection_curve(event, DELETE_SELECTION)
            return
            
        movables = self.o.assy.getSelectedMovables()
        if not movables: return
        
        self.o.SaveMouse(event)
        ma = V(0,0,0)
        for mol in movables:
            ma += mol.getaxis()
        ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
        self.Zmat = A([ma,[-ma[1],ma[0]]])
        self.picking = True
        self.dragdist = 0.0

        
    def leftShiftDrag(self, event):
        """Move selected chunk(s) along its axis (mouse goes up or down)
           and rotate around its axis (left-right)
        """
            
        ##See comments of leftDrag()--Huaicai 3/23/05
        if not self.picking: return
        
        if self.o.modkeys == 'Shift+Control':
            self.continue_selection_curve(event)
            return

        movables = self.o.assy.getSelectedMovables()
        if not movables: return
        
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())
        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*pi/w)
        for mol in movables:
            ma = mol.getaxis()
            mol.move(dx*ma)
            mol.rot(Q(ma,-dy))
        
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()
    
    
    def leftShiftUp(self, event):
                
        if self.o.modkeys == 'Shift+Control':
            self.end_selection_curve(event)
            return
            
        self.EndPick(event, ADD_TO_SELECTION)


    def leftDouble(self, event):
        '''Switch to Select Chunks mode.  This will go away in A8. mark 060303.
        '''
        # Current plans are to merge Select Chunks and Move Chunks modes in A8.
        self.o.setMode('SELECTMOLS') # Fixes bug 1182. mark 060301.
        return

    def setup_movetype(self, movetype):
        
        if movetype == 'Translate':
            
            self.w.moveXLabel.show()
            self.w.moveXSpinBox.show()
            self.w.moveYLabel.show()
            self.w.moveYSpinBox.show()
            self.w.moveZLabel.show()
            self.w.moveZSpinBox.show()
            self.w.moveThetaLabel.hide()
            self.w.moveThetaSpinBox.hide()
            
            self.w.moveDeltaPlusAction.setVisible(1)
            self.w.moveDeltaMinusAction.setVisible(1)
            self.w.moveAbsoluteAction.setVisible(1)
            self.w.moveThetaPlusAction.setVisible(0)
            self.w.moveThetaMinusAction.setVisible(0)
            
        else: # Rotate
            
            self.w.moveXLabel.hide()
            self.w.moveXSpinBox.hide()
            self.w.moveYLabel.hide()
            self.w.moveYSpinBox.hide()
            self.w.moveZLabel.hide()
            self.w.moveZSpinBox.hide()
            self.w.moveThetaLabel.show()
            self.w.moveThetaSpinBox.show()
            
            self.w.moveDeltaPlusAction.setVisible(0)
            self.w.moveDeltaMinusAction.setVisible(0)
            self.w.moveAbsoluteAction.setVisible(0)
            self.w.moveThetaPlusAction.setVisible(1)
            self.w.moveThetaMinusAction.setVisible(1)

    def moveThetaPlus(self):
        "Rotate the selected chunk(s) by theta (plus)"
        rotype = self.w.movetype_combox.currentText()
        theta = self.w.moveThetaSpinBox.floatValue()
        self.moveTheta( rotype, theta)
        
    def moveThetaMinus(self):
        "Rotate the selected chunk(s) by theta (minus)"
        rotype = self.w.movetype_combox.currentText()
        theta = self.w.moveThetaSpinBox.floatValue() * -1.0
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

        dy = theta / 180.0 * pi # Convert to radians
        qrot = Q(ma,dy) # Quat for rotation delta.
        
        if self.w.moveChunksDashboard.rotateAsUnitCB.isChecked():
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
        
        offset = get_move_xyz(self.w)
        self.o.assy.movesel(offset)
        self.o.gl_update()


    def moveDeltaMinus(self):
        "Subtract X, Y, and Z from the selected chunk(s) current position"
        if not self.o.assy.getSelectedMovables(): 
            env.history.message(redmsg("No chunks or movable jigs selected."))
            return
        
        offset = get_move_xyz(self.w, Plus=False)
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
       
        pt2 = get_move_xyz(self.w) # pt2 = X, Y, Z values from dashboard.
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
        '''Slot for Move Chunks dashboard's Move Options
        '''
        if action == self.w.transXAction:
            self.moveOption = 'TRANSX'
        elif action == self.w.transYAction:
            self.moveOption = 'TRANSY'
        elif action == self.w.transZAction:
            self.moveOption = 'TRANSZ'
        else:
            self.moveOption = 'MOVEDEFAULT'

    def skip(self):
        pass

    pass # end of class modifyMode