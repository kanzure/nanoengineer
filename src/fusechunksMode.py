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

offset = V(0,0,0)

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
    bondable_pairs_atoms = [] # List of atom pairs that have been bonded.
    tol = 1.0 # tol is the distance (in Angstroms) between two bondable singlets.
    rfactor = .75 # TO BE DOCUMENTED
    
    def init_gui(self):
        self.o.setCursor(self.w.MoveSelectCursor) # load default cursor for MODIFY mode
        self.w.toolsFuseChunksAction.setOn(1) # toggle on the Fuse Chunks icon
        self.w.fuseChunksDashboard.show() # show the Fuse Chunks dashboard
        self.w.connect(self.w.makeBondsPB,SIGNAL("clicked()"),self.make_bonds)
        self.w.connect(self.w.toleranceSL,SIGNAL("valueChanged(int)"),self.tolerance_changed)
        
        # If only one chunk is selected when coming in, make it the selected_chunk.
        # If more than one chunk is selected, unselect them all.
        if len(self.o.assy.selmols) == 1: 
            self.setup_selected_chunk()
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
        '''Undo any bonds made between chunks.
        '''
        # This undoes only the last fused chunks.  Will work on supporting
        # multiple undos when we get a single undo working.   Mark 050326

        # Bust bonds between last pair/set of fused chunks.
        if self.bondable_pairs_atoms:
            for a1, a2 in self.bondable_pairs_atoms:
                b = a1.get_neighbor_bond(a2)
                if b: b.bust()
                
            # Separate and restore the merged chunks' name(s).
            # This isn't implemented yet - need help from Bruce here.
            # I'm thinking: 
            #   1. select any atom from the a1 list. This would be an atom from selected_chunk.
            #   2. call part.marksingle or bring in code from part.conncomp . This would
            #       select all atoms in selected_chunk.
            #   3. bring in code from modifySeparate to separate all chunks.  We need to rename them
            #       differently than modifySeparate().
            # This should get us our original chunks.  Now we need to 
            # figure out how to rename each restored chunk back to it's original name.
           
            # Here are the original names...
            for chunk in self.merged_chunks:
                print "Restore chunk: ", chunk.name
            
            self.find_bondable_pairs() # Find bondable pairs of singlets
            self.o.gl_update()
                        
        else:
            msg = "Fuse Chunks: No bonds have been made yet.  Undo ignored."
            self.w.history.message(redmsg(msg))
        
    def leftDrag(self, event):
        """Move the selected chunk in the plane of the screen following
        the mouse.
        """
        if not self.o.assy.selmols: return
        
        # Need to look at moving all this back into modifyMode.leftDrag
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        self.dragdist += vlen(deltaMouse)
        
        p1, p2 = self.o.mousepoints(event)
        point = planeXline(self.movingPoint, self.o.out, p1, norm(p2-p1))
        if point == None: 
                point = ptonline(self.movingPoint, p1, norm(p2-p1))
        
        self.o.assy.movesel(point - self.movingPoint)
        
        # This is the only line that is different from modifyMode.leftDrag.
        self.find_bondable_pairs() # Find bondable pairs of singlets

        self.o.gl_update()
        self.movingPoint = point
        self.o.SaveMouse(event)        

    def leftShiftDrag(self, event):
        """move chunk along its axis (mouse goes up or down)
           rotate around its axis (left-right)
        """
        if not self.o.assy.selmols: return
            
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
        
        # This is the only line that is different from modifyMode.leftShiftDrag.    
        self.find_bondable_pairs() # Find bondable pairs of singlets

        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()

    def leftCntlDrag(self, event):
        """Do an incremental trackball action on each selected part.
        """
        if not self.o.assy.selmols: return
        
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

        # This is the only line that is different from modifyMode.leftCntlDrag.
        self.find_bondable_pairs() # Find bondable pairs of singlets
        
        self.o.gl_update()
        
    def leftDouble(self, event):
        # This keeps us from ending Fuse Chunks, as is the case with Move Chunks.
        pass
                
    def EndPick(self, event, selSense):
        """Pick or unpick if click.  Only one chunk can be selected.
        """
        if not self.picking: return
        self.picking = False

        if self.dragdist<7: # didn't move much, call it a click
            
            # This will clear bonds when unselecting the current chunk,
            # regardless of whether it is done with the control key pressed.
            # (i.e. clicking in an empty area of the GLPane)
            self.bondable_pairs = [] 
            self.ways_of_bonding = {}
                
            # Unpick the selected chunk.
            if selSense == 0:  # 0 = Control key pressed, so unpick
                self.o.assy.unpick_at_event(event)
                self.selected_chunk = None

            else:  # Pick a new chunk
                self.o.assy.onlypick_at_event(event)
                if self.o.assy.selmols: 
                    self.setup_selected_chunk()
             
            self.w.win_update()

    def setup_selected_chunk(self):
        '''Sets up the selected chunk for finding bondable pairs of singlets.
        '''
        self.selected_chunk = self.o.assy.selmols[0]
        self.selected_chunk_rad = self.selected_chunk.bbox.scale() * self.rfactor
        self.find_bondable_pairs() # Find bondable pairs of singlets
        
    def Draw(self):
        
        modifyMode.Draw(self)
        
        # Color the bondable pairs or singlets and bond lines between them
        if self.bondable_pairs:
            for s1,s2 in self.bondable_pairs:
                
                # Color bondable pair singlets. Singlets with multiple pairs are colored purple.
                # Singlets with one way of bonding are colored blue (selected_chunk) or green (other chunks).
                color = (self.ways_of_bonding[s1.key] > 1) and purple or blue
                s1.overdraw_with_special_color(color)
                color = (self.ways_of_bonding[s2.key] > 1) and purple or green
                s2.overdraw_with_special_color(color)
     
                # Draw bond lines between singlets.
                # Color should be set from user preferences.
                drawline(self.bondcolor, s1.posn(), s2.posn()) 

    def find_bondable_pairs(self):
        '''Checks the open bonds of the selected chunk to see if they are close enough
        to bond with any other open bonds in the part.  Hidden chunks are skipped.
        '''
        self.bondable_pairs = []
        self.ways_of_bonding = {}
        
        # Get center of the selected chunk.
        self.selected_chunk_ctr = self.selected_chunk.bbox.center()
        
        # Loop through all the chunks in the part to search for bondable pairs of singlets.
        for mol in self.o.assy.molecules:
            if self.selected_chunk == mol: continue # Skip itself
            if mol.hidden: continue # Skip hidden chunks

            # Skip this chunk if it's bounding box does not overlap the selected chunk's bbox.
            mol_ctr = mol.bbox.center()
            mol_rad = mol.bbox.scale()* self.rfactor
            if vlen (mol_ctr - self.selected_chunk_ctr) > mol_rad + self.selected_chunk_rad:
                # Skip this chunk.
                # print "Skipped ", mol.name
                continue
            else:

                # Loop through all the singlets in the selected chunk.
                for s1 in self.selected_chunk.singlets:
                    # Loop through all the singlets in this chunk.
                    for s2 in mol.singlets:
                        
                        # I substituted the line below in place of mergeable_singlets_Q_and_offset,
                        # which compares the distance between s1 and s2.  If the distance
                        # is <= tol, then we have a bondable pair of singlets.  I know this isn't 
                        # a proper use of tol, but it work for now.   Mark 050327
                        if vlen (s1.posn() - s2.posn()) <= self.tol:
                            
                        # ok, ideal, err = mergeable_singlets_Q_and_offset(s1, s2, offset, self.tol)
                        # if ok:
                        # we can ignore ideal and err, we know s1, s2 can bond at this tol
                                    
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