# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
fusechunksMode.py

$Id$
"""

__author__ = "Mark"

#from modes import *
from modifyMode import *
from extrudeMode import mergeable_singlets_Q_and_offset
from chunk import bond_at_singlets

class fusechunksMode(modifyMode):
    "Allows user to move one chunk and fuse it to other chunks in the part"

    # class constants
    backgroundColor = 200/255.0, 200/255.0, 200/255.0
    modename = 'FUSECHUNKS'
    default_mode_status_text = "Mode: Fuse Chunks"
    
    selected_chunk = None # The selected chunk we are moving around
    bondcolor = white # Color of bond lines
    bondable_pairs = [] # List of bondable singlets
    ways_of_bonding = {} # Number of bonds each singlet found
    # tol is the tolerance (distance in Angstrom?) between two singlets.  If the singlets are closer
    # than tol, they can form a bond.  This can be adjusted by a slider later.
    tol = 1.0
    
    def init_gui(self):
        self.w.toolsFuseChunksAction.setOn(1) # toggle on the Fuse Chunks icon
        self.w.fuseChunksDashboard.show() # show the Fuse Chunks dashboard
        self.w.toleranceLCD.display((self.w.toleranceSL.value() + 50) * .01)
        self.w.connect(self.w.makeBondsPB,SIGNAL("clicked()"),self.make_bonds)
        self.w.connect(self.w.toleranceSL,SIGNAL("valueChanged(int)"),self.tolerance_changed)
        self.o.assy.unpickparts()
    
    def restore_gui(self):
        self.w.fuseChunksDashboard.hide()
        self.w.disconnect(self.w.makeBondsPB,SIGNAL("clicked()"),self.make_bonds)
        self.w.disconnect(self.w.toleranceSL,SIGNAL("valueChanged(int)"),self.tolerance_changed)

    def tolerance_changed(self, val):
        self.tol = (val + 50) * .01
        self.w.toleranceLCD.display(self.tol)
        self.find_bondable_pairs() # Find bondable pairs of singlets
        self.o.gl_update()
        
    def leftDrag(self, event):
        """Move the selected chunk in the plane of the screen following
        the mouse.
        """
        # Need to look at moving all this back into modifyMode.leftDrag
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        self.dragdist += vlen(deltaMouse)
        
        p1, p2 = self.o.mousepoints(event)
        point = planeXline(self.movingPoint, self.o.out, p1, norm(p2-p1))
        if point == None: 
                point = ptonline(self.movingPoint, p1, norm(p2-p1))
        
        self.o.assy.movesel(point - self.movingPoint)
        
        self.find_bondable_pairs() # Find bondable pairs of singlets

        self.o.gl_update()
        self.movingPoint = point
        self.o.SaveMouse(event)        

    def leftShiftDrag(self, event):
        """move chunk along its axis (mouse goes up or down)
           rotate around its axis (left-right)
        """
        self.o.setCursor(self.w.MoveRotateMolCursor)
        
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())
        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*pi/w)

        ##### This is the only difference b/w fusechunks and modify #####
        
        ma = self.selected_chunk.getaxis()
        self.selected_chunk.move(dx*ma)
        self.selected_chunk.rot(Q(ma,-dy))

        self.find_bondable_pairs() # Find bondable pairs of singlets
        
        ####################################################
        
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()

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

        self.find_bondable_pairs() # Find bondable pairs of singlets
        
        self.o.gl_update()
                
    def EndPick(self, event, selSense):
        """Pick if click.  Only one chunk can be selected .
        """
        if not self.picking: return
        self.picking = False

        if self.dragdist<7:
            # didn't move much, call it a click
            # Pick a chunk and only one chunk
            if selSense == 0:  # Control key pressed, so unpick
                self.o.assy.unpick_at_event(event)
                self.selected_chunk = None
            else:  # Pick this chunk
                self.o.assy.onlypick_at_event(event)
                if self.o.assy.selmols: self.selected_chunk = self.o.assy.selmols[0]

            self.w.win_update()
                    
    def Draw(self):
        
        modifyMode.Draw(self)
        
        # Color the bondable pairs or singlets and bond lines between them
        if self.bondable_pairs:
            for s1,s2 in self.bondable_pairs:
                
                # Color bondable pair singlets. Singlets with multiple pairs are colored purple.
                color = (self.ways_of_bonding[s1.key] > 1) and purple or blue
                s1.overdraw_with_special_color(color)
                color = (self.ways_of_bonding[s2.key] > 1) and purple or green
                s2.overdraw_with_special_color(color)
     
                # Draw bond lines between singlets
                drawline(self.bondcolor, s1.posn(), s2.posn()) # Color should be set from user preferences

    def find_bondable_pairs(self):
        '''Checks the open bonds of the select chunk to see if they are close enough
        to bond with any other open bonds in the part.
        '''
        self.bondable_pairs = []
        self.ways_of_bonding = {}
        
        # Loop through all the molecules in the part to search for bondable pairs of singlets.
        for mol in self.o.assy.molecules:
            if self.selected_chunk != mol: # Not itself
            
                # An opportunity exists right here for a major optimization.
                # Something like this:
                # if vlen (self.selected_chunk.center - mol.center) < self.selected_chunk.slen + mol.slen + tol:
                # where slen is the distance from the chunk's center to its furthest singlet.
                
                # Main loop
                for a1 in self.selected_chunk.atoms.itervalues():
                    if a1.element == Singlet:
                        s1 = a1
                        for a2 in mol.atoms.itervalues():
                            if a2.element == Singlet:
                                s2 = a2

                                # The secret sauce...
                                if vlen (s1.posn() - s2.posn()) <= self.tol:
                                    self.bondable_pairs.append( (s1,s2) ) # Add this pair to the list
            
                                    # Now increment ways_of_bonding for each of the two singlets.
                                    if s1.key in self.ways_of_bonding:
                                        self.ways_of_bonding[s1.key] += 1
                                    else:
                                        self.ways_of_bonding[s1.key] = 1
                                    if s2.key in self.ways_of_bonding:
                                        self.ways_of_bonding[s2.key] += 1
                                    else:
                                        self.ways_of_bonding[s2.key] = 1

    def make_bonds(self):
        "Make bonds between all bondable pairs of singlets"
        
        self.bondable_pairs_atoms = []
        
        for s1, s2 in self.bondable_pairs:
            if self.ways_of_bonding[s1.key] == 1 and self.ways_of_bonding[s2.key] == 1:
                # record the real atoms in case you want to undo the bond later (before general Undo exists)
                a1 = s1.singlet_neighbor()
                a2 = s2.singlet_neighbor()
                self.bondable_pairs_atoms.append( (a1,a2) ) # Add this pair to the list
                # Bond the singlets.
                bond_at_singlets(s1, s2, move = False)
        
        # This must be done before gl_update, or it will attempt to draw the singlets again.
        self.bondable_pairs = [] 
        self.ways_of_bonding = {} 
                
        self.o.gl_update()
        
# end of class fusechunksMode