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
from HistoryWidget import redmsg

def fusechunks_lambda_tol_nbonds(tol, nbonds, mbonds):
    if nbonds < 0:
        nbonds_str = "?"
    else:
        nbonds_str = "%d" % (nbonds,)
        
    if mbonds < 0:
        mbonds_str = "?"
    else:
        mbonds_str = "%d" % (mbonds,)
        
    tol_str = ("      %d" % int(tol*100.0))[-3:]
    # fixed-width (3 digits) but using initial spaces
    # (doesn't have all of desired effect, due to non-fixed-width font)
    tol_str = tol_str + "%"
    
    return "%s => %s/%s bonds" % (tol_str,nbonds_str,mbonds_str)
    
class fusechunksMode(modifyMode):
    "Allows user to move one chunk and fuse it to other chunks in the part"

    # class constants
    backgroundColor = 200/255.0, 200/255.0, 200/255.0
    modename = 'FUSECHUNKS'
    default_mode_status_text = "Mode: Fuse Chunks"
    
    # something_was_picked is a special boolean flag needed by Draw() to determine when 
    # the state has changed from something selected to nothing selected.  It is used to 
    # properly update the tolerance label on the dashboard when all chunks are unselected.
    something_was_picked = False 
    bondcolor = white # Color of bond lines
    bondable_pairs = [] # List of bondable singlets
    ways_of_bonding = {} # Number of bonds each singlet found
    bondable_pairs_atoms = [] # List of atom pairs that have been bonded.
    tol = 1.0 # tol is the distance between two bondable singlets.
    rfactor = .75 # 
    
    def init_gui(self):
        self.o.setCursor(self.w.MoveSelectCursor) # load default cursor for MODIFY mode
        self.w.toolsFuseChunksAction.setOn(1) # toggle on the Fuse Chunks icon
        self.w.fuseChunksDashboard.show() # show the Fuse Chunks dashboard
        self.w.connect(self.w.makeBondsPB,SIGNAL("clicked()"),self.make_bonds)
        self.w.connect(self.w.toleranceSL,SIGNAL("valueChanged(int)"),self.tolerance_changed)
        # This is so we can use the X, Y, Z modifier keys from modifyMode.
        self.w.connect(self.w.MoveOptionsGroup, SIGNAL("selected(QAction *)"), self.changeMoveOption)
        if self.o.assy.selmols:
            self.something_was_picked = True

    def restore_gui(self):
        self.w.fuseChunksDashboard.hide()
        self.w.disconnect(self.w.makeBondsPB,SIGNAL("clicked()"),self.make_bonds)
        self.w.disconnect(self.w.toleranceSL,SIGNAL("valueChanged(int)"),self.tolerance_changed)
        self.w.disconnect(self.w.MoveOptionsGroup, SIGNAL("selected(QAction *)"), self.changeMoveOption)

    def tolerance_changed(self, val):
        self.tol = val * .01
        
        if self.o.assy.selmols:
            self.find_bondable_pairs() # This will update the slider tolerance label
            self.o.gl_update()
        else:
            # Since no chunk is select, there are no bonds, but the slider tolerance label still needs updating.  
            # This fixed bug 502-14.  Mark 050407
            tol_str = fusechunks_lambda_tol_nbonds(self.tol, 0, self.multibonds()) # 0 bonds
            self.w.toleranceLB.setText(tol_str) 

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
        
    def leftDouble(self, event):
        # This keeps us from leaving Fuse Chunks mode, as is the case in Move Chunks mode.
        pass

    def Draw(self):

        # This is important and needed in case there is nothing selected.  I mention this because
        # it looks redundant since is the first thing done in find_bondable_pairs(). 
        self.bondable_pairs = []
        self.ways_of_bonding = {}
        
        if self.o.assy.selmols: 
            self.find_bondable_pairs() # Find bondable pairs of singlets
            if not self.something_was_picked: 
                self.something_was_picked = True
        else:
            # Nothing is selected, so there are no bondable pairs.
            # Check if we need to update the slider tolerance label.
            # This fixed bug 502-14.  Mark 050407
            if self.something_was_picked:
                tol_str = fusechunks_lambda_tol_nbonds(self.tol, 0, 0) # 0 bonds
                self.w.toleranceLB.setText(tol_str)
                self.something_was_picked = False # Reset flag

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
        
        for chunk in self.o.assy.selmols:
        
            # Get center and sphere of the selected chunk.
            chunk_ctr = chunk.bbox.center()
            chunk_rad = chunk.bbox.scale() * self.rfactor
        
            # Loop through all the mols in the part to search for bondable pairs of singlets.
            for mol in self.o.assy.molecules:
                if chunk == mol: continue # Skip itself
                if mol.hidden: continue # Skip hidden chunks
                if mol in self.o.assy.selmols: continue # Skip other selected chunks
                
                # Skip this chunk if it's bounding box does not overlap the selected chunk's bbox.
                mol_ctr = mol.bbox.center()
                mol_rad = mol.bbox.scale()* self.rfactor
                
                # I add self.tol twice - tol is a radius, and extreme situations require a diameter
                # to catch all possible bonds.  Extreme situations happen in bonds b/w long, skinny rods.
                # Remember: chunk = a selected chunk, mol = a non-selected chunk.
                if vlen (mol_ctr - chunk_ctr) > mol_rad + chunk_rad + self.tol + self.tol:
                    # Skip this chunk.
                    # print "Skipped ", mol.name
                    continue
                else:

                    # Loop through all the singlets in the selected chunk.
                    for s1 in chunk.singlets:
                        # Loop through all the singlets in this chunk.
                        for s2 in mol.singlets:
                        
                            # I substituted the line below in place of mergeable_singlets_Q_and_offset,
                            # which compares the distance between s1 and s2.  If the distance
                            # is <= tol, then we have a bondable pair of singlets.  I know this isn't 
                            # a proper use of tol, but it works for now.   Mark 050327
                            if vlen (s1.posn() - s2.posn()) <= self.tol:
                            
                            # ok, ideal, err = mergeable_singlets_Q_and_offset(s1, s2, offset2 = V(0,0,0), self.tol)
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
        tol_str = fusechunks_lambda_tol_nbonds(self.tol, nbonds,self.multibonds())
        self.w.toleranceLB.setText(tol_str)

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
            singlets_not_bonded = self.multibonds()
            if singlets_not_bonded == 1:
                msg = "%d open bond had multiple bonds. It was not bonded." % (singlets_not_bonded,)
            else:
                msg = "%d open bonds had multiple bonds. They were not bonded." % (singlets_not_bonded,)
            self.w.history.message(redmsg(msg))
                        
        # Merge the chunks if the "merge chunks" checkbox is checked
        if self.w.mergeCB.isChecked() and self.bondable_pairs_atoms:
            for a1, a2 in self.bondable_pairs_atoms:
                # Ignore a1, they are atoms from the selected chunk(s)
                # It is possible that a2 is an atom from a selected chunk, so check it
                if a2.molecule != a1.molecule:
                    if a2.molecule not in self.merged_chunks:
                        self.merged_chunks.append(a2.molecule)
                        a1.molecule.merge(a2.molecule)

        # This must be done before gl_update, or it will try to draw the 
        # bondable singlets again, which generates errors.
        if self.bondable_pairs_atoms:
            self.bondable_pairs = []
            self.ways_of_bonding = {}
        
        # Update the slider tolerance label.  This fixed bug 502-14.  Mark 050407
        tol_str = fusechunks_lambda_tol_nbonds(self.tol, 0, 0)
        self.w.toleranceLB.setText(tol_str)        
                
        self.w.win_update()

    def multibonds(self):
        '''Returns the number of open bonds (singlets) with multiple bonds.
        '''
        mbonds = 0
        singlets = []
        
        for s1, s2 in self.bondable_pairs:
            if self.ways_of_bonding[s1.key] > 1:
                if s1 not in singlets:
                    singlets.append(s1)
            if self.ways_of_bonding[s2.key] > 1:
                if s2 not in singlets:
                    singlets.append(s2)
                
        return len(singlets)
        
# end of class fusechunksMode