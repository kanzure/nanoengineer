# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

from modes import *
from chem import molecule

class selectMode(basicMode):
    def __init__(self, glpane):
        basicMode.__init__(self, glpane, 'SELECT')
        self.backgroundColor = 190/256.0, 229/256.0, 239/256.0
        self.gridColor = (0.0, 0.0, 0.6)
        self.makeMenus()
        self.picking = 0

    def leftDown(self, event):
        self.StartPick(event, 1)
    
    def leftShiftDown(self, event):
        self.StartPick(event, 0)

    def leftCntlDown(self, event):
        self.StartPick(event, 2)


    def StartPick(self, event, sense):
        """Start a selection curve
        """
        self.selSense = sense
        self.picking = 1
        self.o.SaveMouse(event)
        self.o.prevvec = None

        p1, p2 = self.o.mousepoints(event)
        self.o.normal = self.o.lineOfSight
        self.sellist = [p1]
        self.o.backlist = [p2]
        self.pickLineStart = self.pickLinePrev = p1
        self.pickLineLength = 0.0

    
    def leftDrag(self, event):
        self.ContinPick(event, 1)
    
    def leftShiftDrag(self, event):
        self.ContinPick(event, 0)
    
    def leftCntlDrag(self, event):
        self.ContinPick(event, 2)

    def ContinPick(self, event, sense):
        """Add another segment to a selection curve
        """
        if not self.picking: return
        self.selSense = sense
        p1, p2 = self.o.mousepoints(event)

        self.sellist += [p1]
        self.o.backlist += [p2]
        netdist = vlen(p1-self.pickLineStart)

        self.pickLineLength += vlen(p1-self.pickLinePrev)
        self.selLassRect = self.pickLineLength < 2*netdist

        self.pickLinePrev = p1
        self.o.paintGL()

    def leftUp(self, event):
        self.EndPick(event, 1)
    
    def leftShiftUp(self, event):
        self.EndPick(event, 0)
    
    def leftCntlUp(self, event):
        self.EndPick(event, 2)

    def EndPick(self, event, selSense):
        """Close a selection curve and do the selection
        """
        if not self.picking: return
        self.picking = False

        p1, p2 = self.o.mousepoints(event)

        if self.pickLineLength/self.o.scale < 0.03:
            # didn't move much, call it a click
            if selSense == 0: self.o.assy.unpick(p1,norm(p2-p1))
            if selSense == 1: self.o.assy.pick(p1,norm(p2-p1))
            if selSense == 2: self.o.assy.onlypick(p1,norm(p2-p1))
            self.o.paintGL()
            return

        self.sellist += [p1]
        self.sellist += [self.sellist[0]]
        self.o.backlist += [p2]
        self.o.backlist += [self.o.backlist[0]]
        self.o.shape=shape(self.o.right, self.o.up, self.o.lineOfSight)
        eyeball = (-self.o.quat).rot(V(0,0,6*self.o.scale)) - self.o.pov
        if self.selLassRect:
            self.o.shape.pickrect(self.o.backlist[0], p2, -self.o.pov, selSense,
                             (not self.o.ortho) and eyeball)
        else:
            self.o.shape.pickline(self.o.backlist, -self.o.pov, selSense,
                             (not self.o.ortho) and eyeball)
        self.o.shape.select(self.o.assy)
	self.o.shape = None

        self.sellist = []

        self.o.paintGL()

    def leftDouble(self, event):
        """Select the part containing the atom the cursor is on.
        """
        # go into move mode
        self.o.setMode('MODIFY')


    def elemSet(self,elem):
        # elem is an element number
        self.w.setElement(elem)
        # change selected atoms to the element selected
        if self.o.assy.selatoms:
            for a in self.o.assy.selatoms.itervalues():
                a.mvElement(PeriodicTable[elem])
            self.o.paintGL()
       

    def Draw(self):
        basicMode.Draw(self)   
        #self.griddraw()
        if self.sellist: self.pickdraw()
        self.o.assy.draw(self.o)

    def griddraw(self):
        """ draws point-of-view axes
        """
        drawer.drawaxes(5,-self.o.pov)

    def makeMenus(self):
        self.Menu1 = self.makemenu([('All', self.o.assy.selectAll),
                                    ('None', self.o.assy.selectNone),
                                    ('Invert', self.o.assy.selectInvert),
                                    None,
                                    ('Connected', self.o.assy.selectConnected),
                                    ('Doubly', self.o.assy.selectDoubly),
                                    None,
                                    ('Atoms', self.o.assy.selectAtoms),
                                    ('Parts', self.o.assy.selectParts)])
        
        self.Menu2 = self.makemenu([('Kill', self.o.assy.kill),
                                    ('Copy', self.o.assy.copy),
                                    ('Move', self.move),
                                    None,
                                    ('Bond', self.o.assy.Bond),
                                    ('Unbond', self.o.assy.Unbond),
                                    None,
                                    ('Separate', self.o.assy.modifySeparate),
                                    ('Stretch', self.o.assy.Stretch)])
        
        self.Menu3 = self.makemenu([('Invisible', self.w.dispInvis),
                                    None,
                                    ('Default', self.w.dispDefault),
                                    ('Lines', self.w.dispLines),
                                    ('CPK', self.w.dispCPK),
                                    ('Tubes', self.w.dispTubes),
                                    ('VdW', self.w.dispVdW),
                                    None,
                                    ('Color', self.w.dispObjectColor)])

    def move(self):
        # go into move mode
        self.o.setMode('MODIFY')

    def changeModelSelection(self, trigger, target, state):
          """ slot function to respond to model selection change
          """
          if self == trigger:
               return
          
          if isinstance(target, molecule):
                   if state:
                        target.pick()
                   else:
                        target.unpick()

                   self.o.updateGL()