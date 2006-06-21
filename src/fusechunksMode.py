# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
fusechunksMode.py

$Id$

bruce 050913 used env.history in some places.
"""

__author__ = "Mark"

from modifyMode import *
from extrudeMode import mergeable_singlets_Q_and_offset
from bonds import bond_at_singlets
from HistoryWidget import redmsg, orangemsg
from platform import fix_plurals
import env

MAKEBONDS = 'Make Bonds'
FUSEATOMS = 'Fuse Atoms'

def do_what_MainWindowUI_should_do(w):
    'Populate the Fuse Chunks dashboard'
    
    w.fuseChunksDashboard.clear()
    
    w.fuseChunksLabel = QLabel(w.fuseChunksDashboard)
    w.fuseChunksLabel.setText(" Fuse Chunks ")
    
    w.fuseChunksDashboard.addSeparator()

    # moveFreeAction, transXAction, transYAction, and transZAction are shared with modifyMode.
    w.moveFreeAction.addTo(w.fuseChunksDashboard)
    
    w.fuseChunksDashboard.addSeparator()
    
    w.transXAction.addTo(w.fuseChunksDashboard)
    w.transYAction.addTo(w.fuseChunksDashboard)
    w.transZAction.addTo(w.fuseChunksDashboard)
    
    w.fuseChunksDashboard.addSeparator()
    
    w.fuseActionLabel = QLabel(w.fuseChunksDashboard)
    w.fuseActionLabel.setText(" Fuse Mode : ")
    
    w.fuse_mode_combox = QComboBox(0, w.fuseChunksDashboard, "fuse_mode_combox")
    
    w.goPB = QPushButton("Make Bonds", w.fuseChunksDashboard)
    
    w.mergeCB = QCheckBox("Merge chunks", w.fuseChunksDashboard)
    w.mergeCB.setChecked(True)
    
    w.fuseChunksDashboard.addSeparator()
    
    w.tolLB = QLabel(w.fuseChunksDashboard)
    w.tolLB.setText(" Tolerance: ")
    w.toleranceSL = QSlider(0,300,5,100,Qt.Horizontal,w.fuseChunksDashboard)
    w.toleranceLB = QLabel(w.fuseChunksDashboard)
    w.toleranceLB.setText("100% => 0 bondable pairs")
    
    w.fuseChunksDashboard.addSeparator()
    
    w.toolsBackUpAction.addTo(w.fuseChunksDashboard)
    w.toolsDoneAction.addTo(w.fuseChunksDashboard)
    
    w.fuseChunksDashboard.setLabel("Fuse Chunks") #Toolbar tooltip label
    w.fuse_mode_combox.clear()
    # these are identified by both their *position* and not their text
    w.fuse_mode_combox.insertItem(MAKEBONDS) 
    w.fuse_mode_combox.insertItem(FUSEATOMS) 
    

    
def fusechunks_lambda_tol_nbonds(tol, nbonds, mbonds, bondable_pairs):
    '''Returns the bondable pairs tolerance string for the tolerance slider.
    '''
    if nbonds < 0:
        nbonds_str = "?"
    else:
        nbonds_str = "%d" % (nbonds,)
        
    if mbonds < 0:
        mbonds_str = "?"
    elif mbonds == 0:
        mbonds_str = " "
    else:
        mbonds_str = "(%d  non-bondable) " % (mbonds,)
        
    tol_str = ("      %d" % int(tol*100.0))[-3:]
    # fixed-width (3 digits) but using initial spaces
    # (doesn't have all of desired effect, due to non-fixed-width font)
    tol_str = tol_str + "%"
    
#    return "%s => %s/%s bonds" % (tol_str,nbonds_str,mbonds_str)
#    return "%s => [%s bondable pairs] [%s bonds / %s multibonds] " % (tol_str,bondable_pairs,nbonds_str,mbonds_str)
    return "%s => %s bondable pairs %s" % (tol_str,bondable_pairs,mbonds_str)

def fusechunks_lambda_tol_natoms(tol, natoms):
    '''Returns the overlapping atoms tolerance string for the tolerance slider.
    '''
    if natoms < 0:
        natoms_str = "?"
    else:
        natoms_str = "%d" % (natoms,)

    tol_str = ("      %d" % int(tol*100.0))[-3:]
    # fixed-width (3 digits) but using initial spaces
    # (doesn't have all of desired effect, due to non-fixed-width font)
    tol_str = tol_str + "%"
    
    return "%s => %s overlapping atoms" % (tol_str, natoms_str)


class fusechunksBase:
    '''Allows user to move chunks and fuse them to other chunks in the part.
    Two fuse methods are supported:
        1. Make Bonds - bondpoints between chunks will form bonds when they are near each other.
        2. Fuse Atoms - atoms between chunks will be fused when they overlap each other.
    '''
    bondable_pairs = [] # List of bondable singlets
    ways_of_bonding = {} # Number of bonds each singlet found
    bondable_pairs_atoms = [] # List of atom pairs that can be bonded
    overlapping_atoms = [] # List of overlapping atoms
    
    tol = 1.0 # in Angstroms
        # For "Make Bonds", tol is the distance between two bondable singlets
        # For "Fuse Atoms", tol is the distance between two atoms to be considered overlapping
    
    recompute_fusables = True
        # 'recompute_fusables' is used to optimize redraws by skipping the recomputing of fusables
        # (bondable pairs or overlapping atoms). When set to False, Draw() will not recompute fusables 
        # before repainting the GLPane. When False, 'recompute_fusables' is reset to True in Draw(), 
        # so it is the responsibility of the caller to Draw() (i.e. win_update() or gl_update()) to reset it to 
        # False before each redraw if desired. For more info, see comments in Draw().

    def find_bondable_pairs(self, chunk_list = None, selmols_list = None):
        '''Checks the bondpoints of the selected chunk to see if they are close enough
        to bond with any other bondpoints in a list of chunks.  Hidden chunks are skipped.
        '''
        self.bondable_pairs = []
        self.ways_of_bonding = {}
        
        if not chunk_list:
            chunk_list = self.o.assy.molecules
        if not selmols_list:
            selmols_list = self.o.assy.selmols

        for chunk in selmols_list:
            if chunk.hidden or chunk.display == diINVISIBLE: 
                # Skip selected chunk if hidden or invisible. Fixes bug 970. mark 060404
                continue
        
            # Loop through all the mols in the part to search for bondable pairs of singlets.
            # for mol in self.o.assy.molecules:
            for mol in chunk_list:
                if chunk is mol: continue # Skip itself
                if mol.hidden or mol.display == diINVISIBLE: continue # Skip hidden and invisible chunks.
                if mol.picked: continue # Skip selected chunks
                
                # Skip this mol if it's bounding box does not overlap the selected chunk's bbox.
                # Remember: chunk = a selected chunk, mol = a non-selected chunk.
                if not chunk.overlapping_chunk(mol, self.tol):
                    # print "Skipping ", mol.name
                    continue
                else:

                    # Loop through all the singlets in the selected chunk.
                    for s1 in chunk.singlets:
                        # We can skip mol if the singlet lies outside it's bbox.
                        if not mol.overlapping_atom(s1, self.tol):
                            continue
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
        mbonds, singlets_not_bonded, singlet_pairs = self.multibonds()
        tol_str = fusechunks_lambda_tol_nbonds(self.tol, nbonds, mbonds, singlet_pairs)
        return tol_str

    def make_bonds(self, assy=None):
        "Make bonds between all bondable pairs of singlets"
        self._make_bonds_1(assy)
        self._make_bonds_3()
        
    def _make_bonds_1(self, assy=None):
        "Make bonds between all bondable pairs of singlets"
        if assy == None:
            assy = self.o.assy
        self.bondable_pairs_atoms = []
        self.merged_chunks = []
        singlet_found_with_multiple_bonds = False # True when there are singlets with multiple bonds.
        self.total_bonds_made = 0 # The total number of bondpoint pairs that formed bonds.
        singlets_not_bonded = 0 # Number of bondpoints not bonded.
        
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
                assy.changed() # The assy has changed.
            else:
                singlet_found_with_multiple_bonds = True
        self.singlet_found_with_multiple_bonds = singlet_found_with_multiple_bonds

    def _make_bonds_3(self):
        # Print history msgs to inform the user what happened.                         
        if self.singlet_found_with_multiple_bonds:
            mbonds, singlets_not_bonded, bp = self.multibonds()

            self.total_bonds_made = len(self.bondable_pairs_atoms)
            
            if singlets_not_bonded == 1:
                msg = "%d bondpoint had more than one option to form bonds with. It was not bonded." % (singlets_not_bonded,)
            else:
                msg = "%d bondpoints had more than one option to form bonds with. They were not bonded." % (singlets_not_bonded,)
            env.history.message(orangemsg(msg))
            
        else:  # All bond pairs had only one way to bond.
            self.total_bonds_made = len(self.bondable_pairs_atoms)
            
    def multibonds(self):
        '''Returns the following information about bondable pairs:
            - the number of multiple bonds
            - number of bondpoints (singlets) with multiple bonds
            - number of bondpoint pairs that will bond
        '''
        mbonds = 0 # number of multiple bonds
        mbond_singlets = [] # list of singlets with multiple bonds (these will not bond)
        sbond_singlets = 0 # number of singlets with single bonds (these will bond)
        
        for s1, s2 in self.bondable_pairs:
            
            if self.ways_of_bonding[s1.key] == 1 and self.ways_of_bonding[s2.key] == 1:
                sbond_singlets += 1
                continue
                
            if self.ways_of_bonding[s1.key] > 1:
                if s1 not in mbond_singlets:
                    mbond_singlets.append(s1)
                    mbonds += self.ways_of_bonding[s1.key] - 1 # The first one doesn't count.
                
            if self.ways_of_bonding[s2.key] > 1:
                if s2 not in mbond_singlets:
                    mbond_singlets.append(s2)
                    mbonds += self.ways_of_bonding[s2.key] - 1 # The first one doesn't count.

        return mbonds, len(mbond_singlets), sbond_singlets
    


class fusechunksMode(modifyMode, fusechunksBase):
    '''Allows user to move chunks and fuse them to other chunks in the part.
    Two fuse methods are supported:
        1. Make Bonds - bondpoints between chunks will form bonds when they are near each other.
        2. Fuse Atoms - atoms between chunks will be fused when they overlap each other.
    '''

    # class constants
    backgroundColor = 210/255.0, 210/255.0, 210/255.0
    modename = 'FUSECHUNKS'
    default_mode_status_text = "Mode: Fuse Chunks"
    
    something_was_picked = False
        # 'something_was_picked' is a special boolean flag needed by Draw() to determine when 
        # the state has changed from something selected to nothing selected.  It is used to 
        # properly update the tolerance label on the dashboard when all chunks are unselected.
    
    bondable_pairs = [] # List of bondable singlets
    ways_of_bonding = {} # Number of bonds each singlet found
    bondable_pairs_atoms = [] # List of atom pairs that can be bonded
    overlapping_atoms = [] # List of overlapping atoms
    
    tol = 1.0 # in Angstroms
        # For "Make Bonds", tol is the distance between two bondable singlets
        # For "Fuse Atoms", tol is the distance between two atoms to be considered overlapping
    
    fuse_mode = ''
        # The Fuse mode, either 'Make Bonds' or 'Fuse Atoms'.
        
    recompute_fusables = True
        # 'recompute_fusables' is used to optimize redraws by skipping the recomputing of fusables
        # (bondable pairs or overlapping atoms). When set to False, Draw() will not recompute fusables 
        # before repainting the GLPane. When False, 'recompute_fusables' is reset to True in Draw(), 
        # so it is the responsibility of the caller to Draw() (i.e. win_update() or gl_update()) to reset it to 
        # False before each redraw if desired. For more info, see comments in Draw().

    def Enter(self):
        modifyMode.Enter(self)
        self.recompute_fusables = True
        self.change_fuse_mode(self.w.fuse_mode_combox.currentText()) 
            # This maintains state of fuse mode when leaving/reentering mode, and
            # syncs the dashboard and glpane (and does a gl_update).
            
    def init_gui(self):
        self.w.toolsFuseChunksAction.setOn(1) # toggle on the Fuse Chunks icon
        self.w.fuseChunksDashboard.show() # show the Fuse Chunks dashboard
        
        # connect signals (these all need to be disconnected in restore_gui) [mark 050901]
        self.connect_or_disconnect_signals(True)
        
        if self.o.assy.selmols:
            self.something_was_picked = True
            
        # Always reset the dashboard icon to "Move Free" when entering FUSE CHUNKS mode.
        # Mark 050428
        self.w.moveFreeAction.setOn(1) # toggle on the Move Free action on the dashboard
        self.moveOption = 'MOVEDEFAULT'

    def restore_gui(self):
        self.w.fuseChunksDashboard.hide()
        self.connect_or_disconnect_signals(False)
        
    def connect_or_disconnect_signals(self, connect): #copied from depositMode.py. mark 050901
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
            
        change_connect(self.w.goPB,SIGNAL("clicked()"),self.fuse_something)
        change_connect(self.w.toleranceSL,SIGNAL("valueChanged(int)"),self.tolerance_changed)
        # This is so we can use the X, Y, Z modifier keys from modifyMode.
        change_connect(self.w.MoveOptionsGroup, SIGNAL("selected(QAction *)"), self.changeMoveOption)
        change_connect(self.w.fuse_mode_combox, SIGNAL("activated(const QString&)"), self.change_fuse_mode)
        
        return
        
    def tolerance_changed(self, val):
        '''Slot for tolerance slider.
        '''
        self.tol = val * .01
        
        if self.o.assy.selmols:
            self.o.gl_update()
        else:
            # Since no chunks are selected, there are no bonds, but the slider tolerance label still needs 
            # updating.  This fixed bug 502-14.  Mark 050407
            self.reset_tolerance_label()

    def reset_tolerance_label(self):
        'Reset the tolerance label to 0 bonds or 0 overlapping atoms'
        if self.fuse_mode == MAKEBONDS:
            tol_str = fusechunks_lambda_tol_nbonds(self.tol, 0, 0, 0) # 0 bonds
        else:
            tol_str = fusechunks_lambda_tol_natoms(self.tol, 0) # 0 overlapping atoms
        self.w.toleranceLB.setText(tol_str) 
    
    def find_fusables(self):
        'Finds bondable pairs or overlapping atoms, based on the Fuse Action combo box'
        if self.fuse_mode == MAKEBONDS:
            self.find_bondable_pairs()
        else:
            self.find_overlapping_atoms()
                
    def change_fuse_mode(self, fuse_mode):
        'Sets the Fuse mode'
        if self.fuse_mode == fuse_mode:
            return # The mode did not change.  Don't do anything.
        self.fuse_mode = str(fuse_mode) # Must cast here.
        self.w.goPB.setText(fuse_mode) # Update the button text.
        self.o.gl_update() # the Draw() method will update based on the current combo box item.

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
            
            # This is the best we can do for Alpha 5.  This will be handled properly when Undo
            # gets implemented (probably Alpha 7 or 8).  For now, let's just let the user know what 
            # happened and give them an idea of how to restore the orginal chunks (if they were 
            # merged).
            # Mark 050428.
            
            if self.merged_chunks:
                nchunks_str = "%d" % (len(self.merged_chunks) + 1,)   
                msg = "Fuse Chunks: Bonds broken between %s chunks." % (nchunks_str)
                env.history.message(msg)
                msg = "Warning: Cannot separate the original chunks. You can do this yourself using <b>Modify > Separate</b>."
                env.history.message(orangemsg(msg))
            
                cnames = "Their names were: "
                # Here are the original names...
                for chunk in self.merged_chunks:
                    cnames += '[' + chunk.name + '] '
                env.history.message(cnames)
            
            self.o.gl_update()
                        
        else:
            msg = "Fuse Chunks: No bonds have been made yet.  Undo ignored."
            env.history.message(redmsg(msg))
        
    def leftDouble(self, event):
        # This keeps us from leaving Fuse Chunks mode, as is the case in Move Chunks mode.
        pass
        
    def Wheel(self, event):
        '''Mouse wheel event handler.  This overrides basicMode.Wheel() to optimize
        redraws by setting 'recompute_fusables' to False so that Draw()
        will not recompute fusables while zooming in/out.
        '''
        basicMode.Wheel(self, event)
        self.recompute_fusables = False

    def Draw(self):
        '''Draw bondable pairs or overlapping atoms.
        '''
        
        if self.o.is_animating or self.o.button == 'MMB':
            # Don't need to recompute fusables if we are animating between views or 
            # zooming, panning or rotating with the MMB.
            self.recompute_fusables = False
        
        # 'recompute_fusables' is set to False when the bondable pairs or overlapping atoms don't
        # need to be recomputed.  Scenerios when 'recompute_fusables' is set to False:
        #   1. animating between views. Done above, boolean attr 'self.o.is_animating' is checked.
        #   2. zooming, panning and rotating with MMB. Done above, check if self.o.button == 'MMB'
        #   3. Zooming with mouse wheel, done in fusechunksMode.Wheel().
        # If 'recompute_fusables' is False here, it is immediately reset to True below. mark 060405
        if self.recompute_fusables:
            
            # This is important and needed in case there is nothing selected.  I mention this because
            # it looks redundant since is the first thing done in find_bondable_pairs(). 
            self.bondable_pairs = []
            self.ways_of_bonding = {}
            self.overlapping_atoms = []
        
            if self.o.assy.selmols: 
                # Recompute fusables. This can be very expensive, especially with large parts.
                self.find_fusables() 
                if not self.something_was_picked: 
                    self.something_was_picked = True
            else:
                # Nothing is selected, so there can be no fusables.
                # Check if we need to update the slider tolerance label.
                # This fixed bug 502-14.  Mark 050407
                if self.something_was_picked:
                    self.reset_tolerance_label()
                    self.something_was_picked = False # Reset flag
        else:
            self.recompute_fusables = True

        modifyMode.Draw(self)
        
        if self.bondable_pairs:
            self.draw_bondable_pairs()
        
        elif self.overlapping_atoms:
            self.draw_overlapping_atoms()

    def draw_bondable_pairs(self):
        '''Draws bondable pairs of singlets and the bond lines between them. 
        Singlets in the selected chunk(s) are colored green.
        Singlets in the unselected chunk(s) are colored blue.
        Singlets with more than one way to bond are colored magenta.
        '''
        bondline_color = get_selCurve_color(0,self.backgroundColor) # Color of bond lines
        for s1,s2 in self.bondable_pairs:
            color = (self.ways_of_bonding[s1.key] > 1) and magenta or green
            s1.overdraw_with_special_color(color)
            color = (self.ways_of_bonding[s2.key] > 1) and magenta or blue
            s2.overdraw_with_special_color(color)
            drawline(bondline_color, s1.posn(), s2.posn()) # Draw bond lines between singlets.
    
    def draw_overlapping_atoms(self):
        '''Draws overlapping atoms. 
        Atoms in the selected chunk(s) are colored green.
        Atoms in the unselected chunk(s) that will be deleted are colored darkred.
        '''
        for a1,a2 in self.overlapping_atoms:
            # a1 atoms are the selected chunk atoms
            a1.overdraw_with_special_color(green) # NFR/bug 945. Mark 051029.
            # a2 atoms are the unselected chunk(s) atoms
            a2.overdraw_with_special_color(darkred)

    def find_bondable_pairs(self, chunk_list = None):
        '''Checks the bondpoints of the selected chunk to see if they are close enough
        to bond with any other bondpoints in a list of chunks.  Hidden chunks are skipped.
        '''
        tol_str = fusechunksBase.find_bondable_pairs(self, chunk_list, None)
        self.w.toleranceLB.setText(tol_str)

    def fuse_something(self):
        '''Slot for 'Make Bonds/Fuse Atoms' button.
        '''
        if self.fuse_mode == MAKEBONDS:
            self.make_bonds()
        else:
            self.fuse_atoms()
            
    def make_bonds(self):
        "Make bonds between all bondable pairs of singlets"
        self._make_bonds_1()
        self._make_bonds_2()
        self._make_bonds_3()
        self._make_bonds_4()
        
    def _make_bonds_2(self):
        # Merge the chunks if the "merge chunks" checkbox is checked
        if self.w.mergeCB.isChecked() and self.bondable_pairs_atoms:
            for a1, a2 in self.bondable_pairs_atoms:
                # Ignore a1, they are atoms from the selected chunk(s)
                # It is possible that a2 is an atom from a selected chunk, so check it
                if a2.molecule != a1.molecule:
                    if a2.molecule not in self.merged_chunks:
                        self.merged_chunks.append(a2.molecule)
                        a1.molecule.merge(a2.molecule)
                        
    def _make_bonds_4(self):
        msg = fix_plurals( "%d bond(s) made" % self.total_bonds_made)
        env.history.message(msg)

        # Update the slider tolerance label.  This fixed bug 502-14.  Mark 050407
        self.reset_tolerance_label()
        
        if self.bondable_pairs_atoms:
            # This must be done before gl_update, or it will try to draw the 
            # bondable singlets again, which generates errors.
            self.bondable_pairs = []
            self.ways_of_bonding = {}
        
        self.w.win_update()

    ######### Overlapping Atoms methods #############
    
    def find_overlapping_atoms(self):
        '''Checks atoms of the selected chunk to see if they overlap atoms
        in other chunks of the same type (element).  Hidden chunks are skipped.
        '''
        # Future versions should allow more flexible rules for overlapping atoms,
        # but this needs to be discussed with others before implementing anything.
        # For now, only atoms of the same type qualify as overlapping atoms.
        # As is, it is extremely useful for fusing chunks of diamond, lonsdaleite or SiC,
        # which is done quite a lot with casings.  This will save me hours of 
        # modeling work.
        # Mark 050902
        
        self.overlapping_atoms = []
        
        for chunk in self.o.assy.selmols:
            
            if chunk.hidden or chunk.display == diINVISIBLE: 
                # Skip selected chunk if hidden or invisible. Fixes bug 970. mark 060404
                continue
        
            # Loop through all the mols in the part to search for bondable pairs of singlets.
            for mol in self.o.assy.molecules:
                if chunk is mol: continue # Skip itself
                if mol.hidden or mol.display == diINVISIBLE: continue # Skip hidden or invisible chunks
                if mol in self.o.assy.selmols: continue # Skip other selected chunks
                
                # Skip this mol if it's bounding box does not overlap the selected chunk's bbox.
                # Remember: chunk = a selected chunk, mol = a non-selected chunk.
                if not chunk.overlapping_chunk(mol, self.tol):
                    # print "Skipping ", mol.name
                    continue
                else:

                    # Loop through all the atoms in the selected chunk.
                    for a1 in chunk.atoms.itervalues(): # Use values() if the loop ever modifies chunk or mol
                        if a1.element is Singlet: # Singlets can't be overlapping atoms.
                            continue
                        # We can skip mol if the atom lies outside it's bbox.
                        if not mol.overlapping_atom(a1, self.tol):
                            continue

                        # Loop through all the atoms in this chunk.
                        for a2 in mol.atoms.itervalues():
                            # Only atoms of the same type can be overlapping.
                            # This also screens singlets, since a1 can't be a singlet.
                            if a1.element is not a2.element: 
                                continue

                            # Compares the distance between a1 and a2.  If the distance
                            # is <= tol, then we have an overlapping atom.  I know this isn't 
                            # a proper use of tol, but it works for now.   Mark 050901
                            if vlen (a1.posn() - a2.posn()) <= self.tol:
                                self.overlapping_atoms.append( (a1,a2) ) # Add this pair to the list
                                break # No need to check other atoms in this chunk.
                                    
        # Update tolerance label and status bar msgs.
        natoms = len(self.overlapping_atoms)
        tol_str = fusechunks_lambda_tol_natoms(self.tol, natoms)
        self.w.toleranceLB.setText(tol_str)
        

    def fuse_atoms(self):
        '''Deletes overlapping atoms found with the selected chunk(s).  Only the overlapping
        atoms from the unselected chunk(s) are deleted. If the "Merge Chunks" checkbox
        is checked, then find_bondable_pairs() and make_bonds() is called, resulting
        in the merging of chunks.
        '''
        
        total_atoms_fused = 0 # The total number of atoms fused.
       
        # fused_chunks stores the list of chunks that contain overlapping atoms 
        # (but no selected chunks, though)
        fused_chunks = []
        
        # Delete overlapping atoms.
        for a1, a2 in self.overlapping_atoms:
            if a2.molecule not in fused_chunks:
                fused_chunks.append(a2.molecule)
            a2.kill()
        
#        print "Fused chunks list:", fused_chunks
        
        # Merge the chunks if the "merge chunks" checkbox is checked
        if self.w.mergeCB.isChecked() and self.overlapping_atoms:
            # This will bond and merge the selected chunks only with
            # chunks that had overlapping atoms.
            #& This has bugs when the bonds don't line up nicely between overlapping atoms in the selected chunk
            #& and the bondpoints of the deleted atoms' neighbors.  Needs a bug report. mark 060406.
            self.find_bondable_pairs(fused_chunks)
            self.make_bonds()
                        
        # Print history msgs to inform the user what happened.                         
        total_atoms_fused = len(self.overlapping_atoms)
        msg = fix_plurals( "%d atom(s) fused with %d chunk(s)" % (total_atoms_fused, len(fused_chunks)))
        env.history.message(msg)
        #"%s => %s overlapping atoms" % (tol_str, natoms_str)
        
        # Update the slider tolerance label.
        self.reset_tolerance_label()
        
        self.overlapping_atoms = [] 
            # This must be done before win_update(), or it will try to draw the 
            # overlapping atoms again, which generates errors.
        
        self.w.win_update()

# end of class fusechunksMode
