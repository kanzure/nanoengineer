# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
modifyMode.py

$Id$
"""

from modes import *

class modifyMode(basicMode):
    "[bruce comment 040923:] a transient mode entered from selectMode in response to certain mouse events"

    # class constants
    backgroundColor = 254/255.0, 173/255.0, 246/255.0
    gridColor = 52/255.0, 128/255.0, 26/255.0
    modename = 'MODIFY'
    default_mode_status_text = "Mode: Move Chunks"
    
    # no __init__ method needed

    def Enter(self): # bruce 040922 renamed setMode to Enter (and split out init_gui)
        basicMode.Enter(self)
        self.o.assy.selectParts()
        self.dragdist = 0.0

    # (see basicMode.Done.__doc__ for the ones we don't override here [bruce 040923])

    # init_gui handles all the GUI display when entering this mode [mark 041004]
    def init_gui(self):
        self.o.setCursor(self.w.MoveSelectCursor) # load default cursor for MODIFY mode
        self.w.toolsMoveMoleculeAction.setOn(1) # toggle on the Move Chunks icon
        self.w.moveMolDashboard.show() # show the Move Molecules dashboard
    
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.w.moveMolDashboard.hide()
        
    def keyPress(self,key):
        basicMode.keyPress(self, key)
        if key == Qt.Key_Shift:
            self.o.setCursor(self.w.MoveAddCursor)
        if key == Qt.Key_Control:
            self.o.setCursor(self.w.MoveSubtractCursor)
                                
    def keyRelease(self,key):
        basicMode.keyRelease(self, key)
        if key == Qt.Key_Shift or key == Qt.Key_Control:
            self.o.setCursor(self.w.MoveSelectCursor)

    def rightShiftDown(self, event):
            basicMode.rightShiftDown(self, event)
            self.o.setCursor(self.w.MoveSelectCursor)
           
    def rightCntlDown(self, event):          
            basicMode.rightCntlDown(self, event)
            self.o.setCursor(self.w.MoveSelectCursor)
           
    def leftDown(self, event):
        """Move the selected object(s) in the plane of the screen following
        the mouse.
        """
        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0

    def leftDrag(self, event):
        """Move the selected object(s) in the plane of the screen following
        the mouse.
        """
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        self.dragdist += vlen(deltaMouse)
        move = self.o.quat.unrot(self.o.scale * deltaMouse/(h*0.5))
        self.o.assy.movesel(move)
        self.o.paintGL()
        self.o.SaveMouse(event)

    def leftUp(self, event):
        self.EndPick(event, 2)
        
    def EndPick(self, event, selSense):
        """Pick if click
        """
        if not self.picking: return
        self.picking = False

        if self.dragdist<7:
            # didn't move much, call it a click
            # Pick a part
            if selSense == 0: self.o.assy.unpick_at_event(event)
            if selSense == 1: self.o.assy.pick_at_event(event)
            if selSense == 2: self.o.assy.onlypick_at_event(event)
            
            self.w.update()
     
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
        self.o.paintGL()

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
        self.o.paintGL()

    
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

## bruce 040922 zapped this since it seems obsolete:
##    def griddraw(self):
##        """ draws point-of-view axes
##        """
##        drawer.drawaxes(5,-self.o.pov)

    def makeMenus(self): # menus modified by bruce 041103, 041217
        
        self.Menu_spec = [
            ('Separate', self.o.assy.modifySeparate),
            ('Stretch', self.o.assy.Stretch),
            ('Delete     Del', self.o.assy.kill),
            ('Hide', self.o.assy.Hide),
            None,
            # bruce 041217 added the following (rather than just Done)
            ('Select Atoms', self.w.toolsSelectAtoms), 
            ('Select Chunks', self.w.toolsSelectMolecules),
            ('(Move Chunks)', self.w.toolsMoveMolecule),
                # The parens are an experiment. A checkmark would be better.
                # We should merge this with fixit() in selectMode.py by making
                # that an accessible utility in basicMode. #e
            ('Build Atoms', self.w.toolsAtomStart),
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
        
    def skip(self):
        pass

    pass # end of class modifyMode