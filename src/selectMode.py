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
    backgroundColor = 189/255.0, 228/255.0, 238/255.0
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

        p1, p2 = self.o.mousepoints(event, 0.01)
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
        p1, p2 = self.o.mousepoints(event, 0.01)

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

        p1, p2 = self.o.mousepoints(event, 0.01)

        if self.pickLineLength/self.o.scale < 0.03:
            # didn't move much, call it a click
            if selSense == 0: self.o.assy.unpick_at_event(event)
            if selSense == 1: self.o.assy.pick_at_event(event)
            if selSense == 2: self.o.assy.onlypick_at_event(event)
            self.w.win_update()
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
            # (for debug, it's sometimes useful to not reset sellist here,
            #  so you can see it at the same time as the selection it caused.)

        self.w.win_update()

    def leftDouble(self, event):
        """Select the part containing the atom the cursor is on.
        """
        self.move() # go into move mode
        # bruce 040923: we use to inline the same code as is in this method
        # bruce 041217: I am guessing we still intend to leave this in,
        # here and in Move mode (to get back).

    
    # bruce 041216: renamed elemSet to modifyTransmute, added force option,
    # made it work on selected chunks as well as selected atoms
    # [that last part is undiscussed, we might remove it]
    def modifyTransmute(self, elem, force = False): 
        # elem is an element number
        # make it current in the element selector dialog
        self.w.setElement(elem) # bruce comment 040922 -- this line is an inlined version of the superclass method.
        # now change selected atoms to the specified element
        # [bruce 041215: this should probably be made available for any modes
        #  in which "selected atoms" are permitted, not just Select modes. #e]
        if self.o.assy.selatoms:
            for atm in self.o.assy.selatoms.values():
                atm.Transmute(PeriodicTable[elem], force = force)
                # bruce 041215 fix bug 131 by replacing low-level mvElement call
                # with new higher-level method Transmute. Note that singlets
                # can't be selected, so the fact that Transmute does nothing to
                # them is not (presently) relevant.
            #e status message?
            # (Presently a.Transmute makes one per "error or refusal".)
            self.o.paintGL()
        elif self.o.assy.selmols:
            for mol in self.o.assy.selmols[:]:
                for atm in mol.atoms.values():
                    atm.Transmute(PeriodicTable[elem], force = force)
                        # this might run on some killed singlets; should be ok
            self.o.paintGL()
        return
       

    def Draw(self):
        # bruce comment 040922: code is almost identical with modifyMode.Draw;
        # the difference (no check for self.o.assy existing) might be a bug in this version, or might have no effect.
        basicMode.Draw(self)   
        #self.griddraw()
        if self.sellist: self.pickdraw()
        self.o.assy.draw(self.o)

    def makeMenus(self): # menu item names modified by bruce 041217

        def fixit3(text, func):
            if self.default_mode_status_text == "Mode: " + text:
                # this menu item indicates the current mode --
                # add a checkmark and disable it [bruce 050112]
                return text, func, 'checked'
            else:
                return text, func
        
        self.Menu_spec = [
            ###e these accelerators should be changed to be Qt-official
            # by extending widgets.makemenu_helper to use Qt's setAccel...
            # [bruce 050112]
            ('Select All                     Ctrl+A', self.o.assy.selectAll),
            ('Select None                Ctrl+D', self.o.assy.selectNone),
            ('Invert Selection   Ctrl+Shift+I', self.o.assy.selectInvert),
            None,
            ('Connected', self.o.assy.selectConnected),
            ('Doubly', self.o.assy.selectDoubly),
            None,
            # bruce 041217 renamed Atoms and Chunks to the full names of the
            # modes they enter, and added Move Chunks too. (It was already
            # present but in a different menu. I left it there, too, for the
            # sake of existing users. But it would be better to remove it.)
            #bruce 051213 reordered these to conform with toolbar.
            fixit3(('Select Chunks'), self.w.toolsSelectMolecules),
            fixit3(('Select Atoms'), self.w.toolsSelectAtoms),
            ('Move Chunks', self.w.toolsMoveMolecule), 
            ('Build Atoms', self.w.toolsAtomStart),
            ]
        
        self.Menu_spec_shift = [
            ('Delete        Del', self.o.assy.kill),
            ('Move', self.move), # redundant but intentionally left in for now
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
            ('Color', self.w.dispObjectColor),
            ]

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
