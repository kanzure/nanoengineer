from modes import *

class modifyMode(basicMode):
    def __init__(self, glpane):
        basicMode.__init__(self, glpane, 'MODIFY')
        self.backgroundColor = 255/256.0, 174/256.0, 247/256.0
        self.gridColor = 52/256.0, 129/256.0, 26/256.0
        self.makeMenus()
	self.picking = False
        self.dragdist = 0.0

    def Done(self):
        self.o.setMode('SELECT')

    def leftDown(self, event):
        """Move the selected object(s) in the plane of the screen following
        the mouse.
        """
        self.o.SaveMouse(event)
        self.picking = True
        p1, p2 = self.o.mousepoints(event)
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
        move = self.o.scale * deltaMouse/(h*0.5)
        move = dot(move, self.o.quat.matrix3)
        self.o.assy.movesel(move)
        self.o.assy.updateDisplays()
        self.o.SaveMouse(event)

    def leftUp(self, event):
        self.EndPick(event, 1)
        
    def EndPick(self, event, selSense):
        """Pick if click
        """
        if not self.picking: return
        self.picking = False

        p1, p2 = self.o.mousepoints(event)

        if self.dragdist<7:
            # didn't move much, call it a click
            # Pick a part
            if selSense == 0: self.o.assy.unpick(p1,norm(p2-p1))
            if selSense == 1: self.o.assy.pick(p1,norm(p2-p1))
            if selSense == 2: self.o.assy.onlypick(p1,norm(p2-p1))
            
            self.o.assy.updateDisplays()
     
    def leftShiftDown(self, event):
        """Setup a trackball action on each selected part.
        """
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        self.picking = True
        self.dragdist = 0.0

   
    def leftShiftDrag(self, event):
        """Do an incremental trackball action on each selected part.
        """
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1],
                                    self.o.quat)
        self.o.assy.rotsel(q)
        self.o.assy.updateDisplays()

    def leftShiftUp(self, event):
        self.EndPick(event, 0)
    
    
    def leftCntlDown(self, event):
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

    
    def leftCntlDrag(self, event):
        """move part along its axis (mouse goes up or down)
           rotate around its axis (left-right)

        """
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
        self.o.assy.updateDisplays()

    
    def leftCntlUp(self, event):
        self.EndPick(event, 2)

    def leftDouble(self, event):
        self.Done()
        
    def Draw(self):
        self.griddraw()
        if self.sellist: self.pickdraw()
        if self.o.assy: self.o.assy.draw(self.o)

    def griddraw(self):
        """ draws point-of-view axes
        """
        drawer.drawaxes(5,-self.o.pov)

    def makeMenus(self):
        
        self.Menu1 = self.makemenu([('Cancel', self.Flush),
                                    ('Restart', self.Restart),
                                    ('Backup', self.Backup),
                                    None,
                                    ('Copy', self.o.assy.copy),
                                    ('CopyBond', self.o.assy.copy),
                                    ('Bond', self.o.assy.Bond),
                                    ('Unbond', self.o.assy.Unbond),
                                    ('Stretch', self.o.assy.Stretch),
                                    None,
                                    ('Kill', self.o.assy.kill)])

        self.Menu2 = self.makemenu([('Ground', self.o.assy.makeground),
                                    ('Handle', self.skip),
                                    ('motor', self.o.assy.makemotor),
                                    ('Linearmotor', self.o.assy.makeLinearMotor),
                                    ('Spring', self.skip),
                                    ('Bearing', self.skip),
                                    ('Dynamometer', self.skip),
                                    ('Heatsink', self.skip)])
        
        self.Menu3 = self.makemenu([('Passivate', self.o.assy.modifyPassivate),
                                    ('Hydrogenate', self.o.assy.modifyHydrogenate),
                                    ('Separate', self.o.assy.modifySeparate)])
                                    
    def skip(self):
        pass
