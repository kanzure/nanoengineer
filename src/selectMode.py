# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
selectMode.py -- the default mode for Atom's main model view.

$Id$
"""

from modes import *
from chem import molecule

class selectMode(basicMode):
    "the default mode of GLPane"
    
    # class constants
    backgroundColor = 190/256.0, 229/256.0, 239/256.0
    gridColor = (0.0, 0.0, 0.6)

    # default initial values
    savedOrtho = 0
    
    # init_gui handles all the GUI display when entering a mode    
    def init_gui(self):
        pass # let the subclass handle everything for the GUI - Mark [2004-10-11]

    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        pass # let the subclass handle everything for the GUI - Mark [2004-10-11]
   
    def leftDown(self, event):
        self.StartPick(event, 2) # new selection (replace)
    
    def leftCntlDown(self, event):
        self.StartPick(event, 0) # subtract from selection

    def leftShiftDown(self, event):
        self.StartPick(event, 1) # add to selection


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
        self.ContinPick(event, 2)
    
    def leftCntlDrag(self, event):
        self.ContinPick(event, 0)
    
    def leftShiftDrag(self, event):
        self.ContinPick(event, 1)

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
        self.EndPick(event, 2)
    
    def leftCntlUp(self, event):
        self.EndPick(event, 0)
    
    def leftShiftUp(self, event):
        self.EndPick(event, 1)

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
            self.w.update()
            return

        self.sellist += [p1]
        self.sellist += [self.sellist[0]]
        self.o.backlist += [p2]
        self.o.backlist += [self.o.backlist[0]]
        self.o.shape=shape(self.o.right, self.o.up, self.o.lineOfSight)
        eyeball = (-self.o.quat).rot(V(0,0,6*self.o.scale)) - self.o.pov
        
        if self.selLassRect:
            self.o.shape.pickrect(self.o.backlist[0], p2, -self.o.pov, selSense,
                             eye=(not self.o.ortho) and eyeball)
        else:
            self.o.shape.pickline(self.o.backlist, -self.o.pov, selSense,
                             eye=(not self.o.ortho) and eyeball)
        
        self.o.shape.select(self.o.assy)
        self.o.shape = None

        self.sellist = []

        self.w.update()

    def leftDouble(self, event):
        """Select the part containing the atom the cursor is on.
        """
        self.move() # go into move mode # bruce 040923: we use to inline the same code as is in this method
        

    def elemSet(self,elem):
        # elem is an element number
        self.w.setElement(elem) # bruce comment 040922 -- this line is an inlined version of the superclass method.
        # change selected atoms to the element selected
        if self.o.assy.selatoms:
            for a in self.o.assy.selatoms.values():
                a.mvElement(PeriodicTable[elem])
            self.o.paintGL()
       

    def Draw(self):
        # bruce comment 040922: code is almost identical with modifyMode.Draw;
        # the difference (no check for self.o.assy existing) might be a bug in this version, or might have no effect.
        basicMode.Draw(self)   
        #self.griddraw()
        if self.sellist: self.pickdraw()
        self.o.assy.draw(self.o)

    def makeMenus(self):
        
        self.Menu_spec = [
            ('All', self.o.assy.selectAll),
            ('None', self.o.assy.selectNone),
            ('Invert', self.o.assy.selectInvert),
            None,
            ('Connected', self.o.assy.selectConnected),
            ('Doubly', self.o.assy.selectDoubly),
            None,
            ('Atoms', self.w.toolsSelectAtoms),
            ('Chunks', self.w.toolsSelectMolecules) ]
        
        self.Menu_spec_shift = [
            ('Delete', self.o.assy.kill),
            ('Move', self.move),
            None,
            ('Hide', self.o.assy.Hide),
            None,
            ('Separate', self.o.assy.modifySeparate),
            ('Stretch', self.o.assy.Stretch) ]
        
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

    def move(self):
        # we must set OldCursor to the MoveSelectCursor before going into move mode.
        # go into move mode [bruce 040923: now also called from leftDouble]
        self.o.setMode('MODIFY') # [bruce 040923: i think how we do this doesn't need to be changed]

    pass # end of class selectMode
    
class selectMolsMode(selectMode):
        modename = 'SELECTMOLS'
        default_mode_status_text = "Mode: Select Chunks"
    
        def Enter(self): 
            basicMode.Enter(self)
            self.o.assy.pickParts() # josh 10/7 to avoid race in assy init
        
    
        def init_gui(self):
            selectMode.init_gui(self)
#            print "selectMode.py: init_gui(): Cursor set to SelectMolsCursor"
            self.o.setCursor(self.w.SelectMolsCursor)
            self.w.OldCursor = QCursor(self.o.cursor())
            self.w.toolsSelectMoleculesAction.setOn(1) # toggle on the "Select Chunks" tools icon
            self.w.selectMolDashboard.show() 
            
        def restore_gui(self):
            self.w.selectMolDashboard.hide()
        
        def keyPress(self,key):
            basicMode.keyPress(self, key)
            if key == Qt.Key_Shift:
#                print "selectMode.py: keyPress(): Cursor set to SelectMolsAddCursor"
                self.o.setCursor(self.w.SelectMolsAddCursor)
            if key == Qt.Key_Control:
#                print "selectMode.py: keyPress(): Cursor set to SelectMolsSubtractCursor"
                self.o.setCursor(self.w.SelectMolsSubtractCursor)
                
        def keyRelease(self,key):
            basicMode.keyRelease(self, key)
            if key == Qt.Key_Shift or key == Qt.Key_Control:
#                print "selectMode.py: keyRelease(): Cursor set to SelectMolsCursor"
                self.o.setCursor(self.w.SelectMolsCursor)
                
        def rightShiftDown(self, event):
            basicMode.rightShiftDown(self, event)
            self.o.setCursor(self.w.SelectMolsCursor)
           
        def rightCntlDown(self, event):          
            basicMode.rightCntlDown(self, event)
            self.o.setCursor(self.w.SelectMolsCursor)

class selectAtomsMode(selectMode):
        modename = 'SELECTATOMS'
        default_mode_status_text = "Mode: Select Atoms"
        
        def Enter(self): 
            basicMode.Enter(self)
            self.o.assy.selectAtoms() 
            
        def init_gui(self):
            selectMode.init_gui(self)
            self.o.setCursor(self.w.SelectAtomsCursor)
            self.w.toolsSelectAtomsAction.setOn(1) # toggle on the "Select Atoms" tools icon
            self.w.selectAtomsDashboard.show() 
            
        def restore_gui(self):
            self.w.selectAtomsDashboard.hide()
            
        def keyPress(self,key):
            basicMode.keyPress(self, key)
            if key == Qt.Key_Shift:
                self.o.setCursor(self.w.SelectAtomsAddCursor)
            if key == Qt.Key_Control:
                self.o.setCursor(self.w.SelectAtomsSubtractCursor)
                                
        def keyRelease(self,key):
            basicMode.keyRelease(self, key)
            if key == Qt.Key_Shift or key == Qt.Key_Control:
                self.o.setCursor(self.w.SelectAtomsCursor)
       
       
        def rightShiftDown(self, event):
            basicMode.rightShiftDown(self, event)
            self.o.setCursor(self.w.SelectAtomsCursor)
           
        def rightCntlDown(self, event):          
            basicMode.rightCntlDown(self, event)
            self.o.setCursor(self.w.SelectAtomsCursor)         