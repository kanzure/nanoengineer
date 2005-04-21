# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
modifyMode.py

$Id$
"""

from modes import *
from widgets import FloatSpinBox
from HistoryWidget import redmsg

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
    
    w.moveXLabel = QLabel(" X ", w.moveChunksDashboard)
    w.moveXSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveXSpinBox")
    w.moveXLabel = QLabel(" Y ", w.moveChunksDashboard)
    w.moveYSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveYSpinBox")
    w.moveXLabel = QLabel(" Z ", w.moveChunksDashboard)
    w.moveZSpinBox = FloatSpinBox(w.moveChunksDashboard, "moveZSpinBox")
    
    w.moveDeltaPlusAction.addTo(w.moveChunksDashboard)
    w.moveDeltaMinusAction.addTo(w.moveChunksDashboard)
    w.moveAbsoluteAction.addTo(w.moveChunksDashboard)
    
    w.moveChunksDashboard.addSeparator()
    
    w.toolsDoneAction.addTo(w.moveChunksDashboard)

def set_move_xyz(win,x,y,z):
    self = win
    self.moveXSpinBox.setFloatValue(x)
    self.moveYSpinBox.setFloatValue(y)
    self.moveZSpinBox.setFloatValue(z)

def get_move_xyz(win, Plus = 1):
    self = win
    x = self.moveXSpinBox.floatValue()
    y = self.moveYSpinBox.floatValue()
    z = self.moveZSpinBox.floatValue()
    if Plus: return (x,y,z) # Plus
    else: return (-x, -y, -z) # Minus
    
class modifyMode(basicMode):
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

    # init_gui handles all the GUI display when entering this mode [mark 041004]
    def init_gui(self):
        self.o.setCursor(self.w.MoveSelectCursor) # load default cursor for MODIFY mode
        self.w.toolsMoveMoleculeAction.setOn(1) # toggle on the Move Chunks icon
        self.w.moveChunksDashboard.show() # show the Move Molecules dashboard
        
        self.w.connect(self.w.MoveOptionsGroup, SIGNAL("selected(QAction *)"), self.changeMoveOption)
        self.w.connect(self.w.moveDeltaPlusAction, SIGNAL("activated()"), self.moveDeltaPlus)
        self.w.connect(self.w.moveDeltaMinusAction, SIGNAL("activated()"), self.moveDeltaMinus)
        self.w.connect(self.w.moveAbsoluteAction, SIGNAL("activated()"), self.moveAbsolute)
        
        set_move_xyz(self.w, 0, 0, 0)

        # Always reset the dashboard icon to "Move Free" when entering MODIFY mode.
        # Mark 050410
        self.w.moveFreeAction.setOn(1) # toggle on the Move Free action on the dashboard
        self.moveOption = 'MOVEDEFAULT'
    
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.w.moveChunksDashboard.hide()
        self.w.disconnect(self.w.MoveOptionsGroup, SIGNAL("selected(QAction *)"), self.changeMoveOption)
        self.w.disconnect(self.w.moveDeltaPlusAction, SIGNAL("activated()"), self.moveDeltaPlus)
        self.w.disconnect(self.w.moveDeltaMinusAction, SIGNAL("activated()"), self.moveDeltaMinus)
        self.w.disconnect(self.w.moveAbsoluteAction, SIGNAL("activated()"), self.moveAbsolute)
        
    def keyPress(self,key):
        basicMode.keyPress(self, key)
        if key == Qt.Key_Shift:
            self.o.setCursor(self.w.MoveAddCursor)
        elif key == Qt.Key_Control:
            self.o.setCursor(self.w.MoveSubtractCursor)

        # For these key presses, we toggle the Action item, which will send 
        # an event to changeMoveMode, where the business is done.
        # Mark 050410
        elif key == Qt.Key_X:
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
#        print "modifyMode: keyRelease, key=", key
        if key == Qt.Key_Shift or key == Qt.Key_Control:
            self.o.setCursor(self.w.MoveSelectCursor)
        if key == Qt.Key_X or key == Qt.Key_Y or key == Qt.Key_Z: 
            self.w.moveFreeAction.setOn(1) # toggle on the Move Chunks icon
        if key == Qt.Key_R:
            self.RotationOnly = False # Unconstrain translation.
        if key == Qt.Key_T:
            self.TranslationOnly = False # Unconstrain rotation.
            
    def rightShiftDown(self, event):
            basicMode.rightShiftDown(self, event)
            self.o.setCursor(self.w.MoveSelectCursor)
           
    def rightCntlDown(self, event):          
            basicMode.rightCntlDown(self, event)
            self.o.setCursor(self.w.MoveSelectCursor)
           
    def leftDown(self, event):
        """Move the selected object(s).
        """
        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0
        self.transDelta = 0 # X, Y or Z deltas for translate.
        self.rotDelta = 0 # delta for constrained rotations.
        self.moveOffset = [0.0, 0.0, 0.0] # X, Y and Z offset for move.

        # Move section
        if self.moveOption == 'MOVEDEFAULT':        
            wX = event.pos().x()
            wY = self.o.height - event.pos().y()
            wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
            if wZ[0][0] >= 1.0: 
                junk, self.movingPoint = self.o.mousepoints(event)
            else:
                self.movingPoint = A(gluUnProject(wX, wY, wZ[0][0]))
        # end of Move section

        # Translate section
        else:
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
        # Call. 
        if not self.picking: return

        # Move section
        if self.moveOption == 'MOVEDEFAULT':
            deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        
            p1, p2 = self.o.mousepoints(event)
        
            point = planeXline(self.movingPoint, self.o.out, p1, norm(p2-p1))
            if point == None: 
                point = ptonline(self.movingPoint, p1, norm(p2-p1))
        
            # Print status bar msg indicating the current move delta.
            if self.o.assy.selmols:
                self.moveOffset += norm(point - self.movingPoint) # Increment move offset
                msg = "Offset: [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.moveOffset[0], self.moveOffset[1], self.moveOffset[2])
                self.w.history.transient_msg(msg)

            self.o.assy.movesel(point - self.movingPoint)
            self.movingPoint = point

        # end of Move section
        
        # Translate/Rotate section
        else: 
            #self.o.setCursor(self.w.MoveRotateMolCursor)
        
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
            
            # Move the selected chunks    
            for mol in self.o.assy.selmols:
                mol.move(dx*ma) # Translate
                mol.rot(qrot) # Rotate
        
            # Print status bar msg indicating the current translation and rotation delta.
            if self.o.assy.selmols:
                msg = "%s delta: [%.2f Angstroms] [%.2f Degrees]" % (self.axis, self.transDelta, self.rotDelta)
                self.w.history.transient_msg(msg)
            
        # end of Translate section

        # common finished code
        
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()
        
    # end of leftDrag

    def leftUp(self, event):
        self.EndPick(event, 2)
        
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
            # Pick a part
            if selSense == 0: self.o.assy.unpick_at_event(event)
            if selSense == 1: self.o.assy.pick_at_event(event)
            if selSense == 2: self.o.assy.onlypick_at_event(event)
            
            self.w.win_update()
     
    def leftCntlDown(self, event):
        """Setup a trackball action on each selected part.
        """
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        self.picking = True
        self.dragdist = 0.0

   
    def leftCntlDrag(self, event):
        """Do an incremental trackball action on each selected part.
        """
        ##See comments of leftDrag()--Huaicai 3/23/05
        if not self.picking: return

        self.o.setCursor(self.w.RotateMolCursor)
        
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1],
                                    self.o.quat)
        self.o.assy.rotsel(q)
        self.o.gl_update()

    def leftCntlUp(self, event):
        self.EndPick(event, 0)
    
    def leftShiftDown(self, event):
        """ Set up for sliding or rotating the selected part
        unlike select zoom/rotate, can have combined motion
        """
        self.o.SaveMouse(event)
        ma = V(0,0,0)
        for mol in self.o.assy.selmols:
            ma += mol.getaxis()
        ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
        self.Zmat = A([ma,[-ma[1],ma[0]]])
        self.picking = True
        self.dragdist = 0.0
        
    def leftShiftDrag(self, event):
        """move part along its axis (mouse goes up or down)
           rotate around its axis (left-right)
        """
        ##See comments of leftDrag()--Huaicai 3/23/05
        if not self.picking: return

        self.o.setCursor(self.w.MoveRotateMolCursor)
        
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())
        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*pi/w)
        for mol in self.o.assy.selmols:
            ma = mol.getaxis()
            mol.move(dx*ma)
            mol.rot(Q(ma,-dy))
        
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()
    
    def leftShiftUp(self, event):
        self.EndPick(event, 1)


    def leftDouble(self, event):
        self.Done() # bruce 040923: how to do this need not change
        # (tho josh in bug#15 asks us to change the functionality -- not yet done ###e)
        # (as of now, my understanding is that we want to leave leftDouble in,
        #  for Select and Move mode only -- but I'm not sure. I think we once wanted it
        #  to get back into the same one of Select Atoms or Select Chunks that the
        #  user was last in, but I'm not changing that now. [bruce 041217])
        
    def Draw(self):
        # bruce comment 040922: code is almost identical with selectMode.Draw
        basicMode.Draw(self)
        # self.griddraw()
        if self.sellist: self.pickdraw()
        if self.o.assy: self.o.assy.draw(self.o)


    def makeMenus(self): # menus modified by bruce 041103, 041217
        
        self.Menu_spec = [
            ('Stretch', self.o.assy.Stretch),
            ('Delete     Del', self.o.assy.delete_sel),
            ('Hide', self.o.assy.Hide),
            None,
            # bruce 041217 added the following (rather than just Done)
            #bruce 051213 added 'checked' and reordered these to conform with toolbar.
            ('Select Chunks', self.w.toolsSelectMolecules),
            ('Select Atoms', self.w.toolsSelectAtoms), 
            ('Move Chunks', self.w.toolsMoveMolecule, 'checked'),
            ('Build Atoms', self.w.toolsBuildAtoms),
         ]

        self.debug_Menu_spec = [
            ('debug: invalidate selection', self.invalidate_selection),
            ('debug: update selection', self.update_selection),
         ]
        
        self.Menu_spec_control = [
            ('Invisible', self.w.dispInvis),
            None,
            ('Default', self.w.dispDefault),
            ('Lines', self.w.dispLines),
            ('CPK', self.w.dispCPK),
            ('Tubes', self.w.dispTubes),
            ('VdW', self.w.dispVdW),
            None,
            ('Color', self.w.dispObjectColor) ]

    def invalidate_selection(self): #bruce 041115 (debugging method)
        "[debugging method] invalidate all aspects of selected atoms or mols"
        for mol in self.o.assy.selmols:
            print "already valid in mol %r: %r" % (mol, mol.invalid_attrs())
            mol.invalidate_everything()
        for atm in self.o.assy.selatoms.values():
            atm.invalidate_everything()

    def update_selection(self): #bruce 041115 (debugging method)
        """[debugging method] update all aspects of selected atoms or mols;
        no effect expected unless you invalidate them first
        """
        for atm in self.o.assy.selatoms.values():
            atm.update_everything()
        for mol in self.o.assy.selmols:
            mol.update_everything()

    def moveDeltaPlus(self):
        "Add X, Y, and Z to the selected chunk(s) current position"
        if not self.o.assy.selmols: 
            self.w.history.message(redmsg("No chunks selected."))
            return
        offset = get_move_xyz(self.w, 1)
        self.o.assy.movesel(offset)
        self.o.gl_update()

    def moveDeltaMinus(self):
        "Subtract X, Y, and Z from the selected chunk(s) current position"
        if not self.o.assy.selmols: 
            self.w.history.message(redmsg("No chunks selected."))
            return
        offset = get_move_xyz(self.w, 0)
        self.o.assy.movesel(offset)
        self.o.gl_update()

    def moveAbsolute(self):
        '''Move selected chunk(s) to absolute X, Y, and Z by computing the bbox center
        of everything as if they were one big chunk, then move everything as a unit.
        '''
        if not self.o.assy.selmols: 
            self.w.history.message(redmsg("No chunks selected."))
            return
        # Compute bbox for selected chunk(s).
        from shape import BBox
        bbox = BBox()
        for mol in self.o.assy.selmols:
              bbox.merge(mol.bbox)
        pt1 = bbox.center() # pt1 = center point for bbox of selected chunk(s).
        pt2 = get_move_xyz(self.w, 1) # pt2 = X, Y, Z values from dashboard.
        offset = pt2 - pt1 # Compute offset for movesel.
        self.o.assy.movesel(offset) # Move the selected chunk(s).
        # Print history message about what happened.
        if len(self.o.assy.selmols) == 1:
            msg = "Chunk [%s] moved to [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.o.assy.selmols[0].name, pt2[0], pt2[1], pt2[2])
        else:
            msg = "Selected chunks moved by offset [X: %.2f] [Y: %.2f] [Z: %.2f]" % (offset[0], offset[1], offset[2])
        self.w.history.message(msg)
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