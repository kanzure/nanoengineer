# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
fusechunksMode.py

$Id$
"""

__author__ = "Mark"

#from modes import *
from modifyMode import *
from extrudeMode import mergeable_singlets_Q_and_offset, lambda_tol_nbonds
from chunk import bond_at_singlets
from HistoryWidget import redmsg

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
        self.o.setCursor(self.w.MoveSelectCursor) # load default cursor for MODIFY mode
        self.w.toolsFuseChunksAction.setOn(1) # toggle on the Fuse Chunks icon
        self.w.fuseChunksDashboard.show() # show the Fuse Chunks dashboard
        self.w.connect(self.w.makeBondsPB,SIGNAL("clicked()"),self.make_bonds)
        self.w.connect(self.w.toleranceSL,SIGNAL("valueChanged(int)"),self.tolerance_changed)
        
        # If only one chunk is selected when coming in, make it the selected_chunk.
        # If more than one chunk is selected, unselect them all.
        if len(self.o.assy.selmols) == 1: 
            self.selected_chunk = self.o.assy.selmols[0]
            self.find_bondable_pairs() # Find bondable pairs of singlets
        else:
            self.o.assy.unpickparts()
            self.selected_chunk = None
    
    def restore_gui(self):
        self.w.fuseChunksDashboard.hide()
        self.w.disconnect(self.w.makeBondsPB,SIGNAL("clicked()"),self.make_bonds)
        self.w.disconnect(self.w.toleranceSL,SIGNAL("valueChanged(int)"),self.tolerance_changed)

    def tolerance_changed(self, val):
        self.tol = val * .01
        if not self.selected_chunk: return
        self.find_bondable_pairs() # Find bondable pairs of singlets
        self.o.gl_update()

    def Backup(self):
        if self.bondable_pairs_atoms:
            for a1, a2 in self.bondable_pairs_atoms:
                b = self.get_neighbor_bond(a1, a2)
                if b: b.bust()
            # Then I need to separate and rename the new chunk back to it's original name.
            for chunk in self.merged_chunks:
                print "Restore chunk: ", chunk.name
                
        self.find_bondable_pairs() # Find bondable pairs of singlets
        self.o.gl_update()

    def get_neighbor_bond(self, a1, a2):
        '''Return the bond between atoms a1 and a2, or None if none exist.
        '''
        for b in a1.bonds[:]:
            if b.other(a1) == a2:
               return b
        return None
        
    def leftDrag(self, event):
        """Move the selected chunk in the plane of the screen following
        the mouse.
        """
        if not self.selected_chunk: return
        
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
        if not self.selected_chunk: return
            
        self.o.setCursor(self.w.MoveRotateMolCursor)
        
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())
        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*pi/w)

        # This is always be only one chunk.
        for mol in self.o.assy.selmols:
            ma = mol.getaxis()
            mol.move(dx*ma)
            mol.rot(Q(ma,-dy))
            
        self.find_bondable_pairs() # Find bondable pairs of singlets

        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()

    def leftCntlDrag(self, event):
        """Do an incremental trackball action on each selected part.
        """
        if not self.selected_chunk: return
        
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
        
    def leftDouble(self, event):
        # This keeps us from ending Fuse Chunks, as is the case with Move Chunks.
        pass
                
    def EndPick(self, event, selSense):
        """Pick if click.  Only one chunk can be selected .
        """
        if not self.picking: return
        self.picking = False

        if self.dragdist<7: # didn't move much, call it a click
            
            # Pick a chunk and only one chunk
            if selSense == 0:  # Control key pressed, so unpick
                self.o.assy.unpick_at_event(event)
                self.selected_chunk = None
                self.bondable_pairs = [] 
                self.ways_of_bonding = {}

            else:  # Pick a new chunk
                self.o.assy.onlypick_at_event(event)
                if self.o.assy.selmols: 
                    self.selected_chunk = self.o.assy.selmols[0]
                    self.find_bondable_pairs() # Find bondable pairs of singlets
             
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
        
        # Update tolerance label and status bar msgs.
        nbonds = len(self.bondable_pairs)
        tol_str = lambda_tol_nbonds(self.tol, nbonds)
        self.w.toleranceLB.setText(tol_str)
        
        if nbonds:
            self.w.history.transient_msg("")
        else:
            self.w.history.transient_msg("Drag chunk with open bonds near another chunk with open bonds to create new bonds.")

    def make_bonds(self):
        "Make bonds between all bondable pairs of singlets"
        
        self.bondable_pairs_atoms = []
        self.merged_chunks = []
        not_bonded = 0 # Bondable pairs not bonded counter
        
#        print self.bondable_pairs
        
        # This first section of code bonds each bondable pair of singlets.
        for s1, s2 in self.bondable_pairs:
            # Make sure each singlet of the pair has only one way of bonding.
            # If either singlet has more than one ways to bond, we aren't going to bond them.
            if self.ways_of_bonding[s1.key] == 1 and self.ways_of_bonding[s2.key] == 1:
                # Record the real atoms in case I want to undo the bond later (before general Undo exists)
                # Current, this undo feature is not implemented here. Mark 050325
                a1 = s1.singlet_neighbor()
                a2 = s2.singlet_neighbor()
                self.bondable_pairs_atoms.append( (a1,a2) ) # Add this pair to the list
                bond_at_singlets(s1, s2, move = False) # Bond the singlets.
                self.o.assy.changed() # The assy has changed.
            else:
                not_bonded += 1
                # One of the two singlets had more than one way to bond.
                # We keep track of it so we can print a msg to the user
                # that we aren't bonding this pair (and other previous pairs).
        if not_bonded:
            if not_bonded == 1:
                msg = "%d open bond had multiple bonds. It was not bonded." % (not_bonded,)
            else:
                msg = "%d open bonds had multiple bonds. They were not bonded." % (not_bonded,)
            self.w.history.message(redmsg(msg))
                        
        # Merge the chunks if the "merge chunks" checkbox is checked
        if self.w.mergeCB.isChecked() and self.bondable_pairs_atoms:
            for a1, a2 in self.bondable_pairs_atoms:
                # Ignore a1, they are atoms from selected_chunk
                # It is possible that a2 is an atom from selected_chunk, so check it
                if a2.molecule != self.selected_chunk:
                    if a2.molecule not in self.merged_chunks:
                        self.merged_chunks.append(a2.molecule)
                        self.selected_chunk.merge(a2.molecule)

        # This must be done before gl_update, or it will try to draw the 
        # bondable singlets again, which generates errors.
        if self.bondable_pairs_atoms:
            self.bondable_pairs = []
            self.ways_of_bonding = {}
                
        self.w.win_update()

# end of class fusechunksMode