# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
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
from FusePropertyManager import FusePropertyManager

MAKEBONDS = 'Make Bonds Between Chunks'
FUSEATOMS = 'Fuse Overlapping Atoms'

def do_what_MainWindowUI_should_do(w):
    'Populate the Fuse Chunks dashboard'
    
    w.fuseChunksDashboard.clear()

    #w.textLabel1_3.setText(" Fuse Chunks ")
    w.fuseChunksDashboard.addWidget(w.textLabel1_3)
    
    w.fuseChunksDashboard.addSeparator()

    # moveFreeAction, transXAction, transYAction, and transZAction are shared with modifyMode.
    w.fuseChunksDashboard.addAction(w.moveFreeAction)
    
    w.fuseChunksDashboard.addSeparator()
    
    w.fuseChunksDashboard.addAction(w.transXAction)
    w.fuseChunksDashboard.addAction(w.transYAction)
    w.fuseChunksDashboard.addAction(w.transZAction)
    
    w.fuseChunksDashboard.addSeparator()
    
    w.fuseActionLabel = QLabel()
    w.fuseActionLabel.setText(" Fuse Mode : ")
    w.fuseChunksDashboard.addWidget(w.fuseActionLabel)
    
    w.fuse_mode_combox = QComboBox()
    w.fuseChunksDashboard.addWidget(w.fuse_mode_combox)
    
    w.goPB = QPushButton("Make Bonds", w.fuseChunksDashboard)
    w.fuseChunksDashboard.addWidget(w.goPB)
    
    w.mergeCB = QCheckBox("Merge chunks", w.fuseChunksDashboard)
    w.mergeCB.setChecked(True)
    w.fuseChunksDashboard.addWidget(w.mergeCB)
    
    w.fuseChunksDashboard.addSeparator()
    
    w.tolLB = QLabel()
    w.tolLB.setText(" Tolerance: ")
    w.fuseChunksDashboard.addWidget(w.tolLB)
    #w.toleranceSL = QSlider(0,300,5,100,Qt.Horizontal,w.fuseChunksDashboard)
    w.toleranceSL = QSlider(Qt.Horizontal)
    w.toleranceSL.setMaximumWidth(100)
    w.toleranceSL.setValue(100)
    w.toleranceSL.setRange(0, 300)
    w.fuseChunksDashboard.addWidget(w.toleranceSL)
    w.toleranceLB = QLabel()
    w.toleranceLB.setText("100% => 0 bondable pairs")
    w.fuseChunksDashboard.addWidget(w.toleranceLB)
    
    w.fuseChunksDashboard.addSeparator()
    
    w.fuseChunksDashboard.addAction(w.toolsBackUpAction)
    w.fuseChunksDashboard.addAction(w.toolsDoneAction)
    
    w.fuseChunksDashboard.setWindowTitle("Fuse Chunks") #Toolbar tooltip label - no good for Qt 4
    w.fuse_mode_combox.clear()
    # these are identified by both their *position* and not their text
    w.fuse_mode_combox.insertItem(0,MAKEBONDS) 
    w.fuse_mode_combox.insertItem(1,FUSEATOMS) 
    

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
    


class fusechunksMode(modifyMode, fusechunksBase, FusePropertyManager):
    '''Allows user to move chunks and fuse them to other chunks in the part.
    Two fuse methods are supported:
        1. Make Bonds - bondpoints between chunks will form bonds when they are near each other.
        2. Fuse Atoms - atoms between chunks will be fused when they overlap each other.
    '''

    # class constants
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
        ##self.change_fuse_mode(self.w.fuse_mode_combox.currentText()) 
            # This maintains state of fuse mode when leaving/reentering mode, and
            # syncs the dashboard and glpane (and does a gl_update).
            
    def init_gui(self):
                
        FusePropertyManager.__init__(self) 
        self.openPropertyManager(self)
        
        self.change_fuse_mode(self.fuse_mode_combox.currentText()) 
            # This maintains state of fuse mode when leaving/reentering mode, and
            # syncs the dashboard and glpane (and does a gl_update).
        
        self.w.toolsFuseChunksAction.setChecked(1) # toggle on the Fuse Chunks icon
        
        self.updateCommandManager(bool_entering = True)
                
        # connect signals (these all need to be disconnected in restore_gui) [mark 050901]
        self.connect_or_disconnect_signals(True)
        
        if self.o.assy.selmols:
            self.something_was_picked = True
       
        if self.isMoveGroupBoxActive:
            self.w.moveFreeAction.setChecked(True) # toggle on the Move Free action on the dashboard
            self.moveOption = 'MOVEDEFAULT'
        else:
            self.w.rotateFreeAction.setChecked(True)
            self.rotateOption = 'ROTATEDEFAULT'

    def restore_gui(self):
	self.updateCommandManager(bool_entering = False)
        self.closePropertyManager()
        self.connect_or_disconnect_signals(False)
        self.w.toolsFuseChunksAction.setChecked(False)
        
    def connect_or_disconnect_signals(self, connect): #copied from depositMode.py. mark 050901
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
            
        change_connect(self.goPB,SIGNAL("clicked()"),self.fuse_something)
        change_connect(self.toleranceSL,SIGNAL("valueChanged(int)"),
                       self.tolerance_changed)
        
        
        change_connect(self.w.MoveOptionsGroup, 
                       SIGNAL("triggered(QAction *)"), self.changeMoveOption)
        change_connect(self.w.rotateOptionsGroup, 
                       SIGNAL("triggered(QAction *)"), self.changeRotateOption)
        
        change_connect(self.fuse_mode_combox, 
                       SIGNAL("activated(const QString&)"), 
                       self.change_fuse_mode)
        
        change_connect(self.w.moveDeltaPlusAction, SIGNAL("activated()"), 
                       self.moveDeltaPlus)
        change_connect(self.w.moveDeltaMinusAction, SIGNAL("activated()"), 
                       self.moveDeltaMinus)
        change_connect(self.w.moveAbsoluteAction, SIGNAL("activated()"), 
                       self.moveAbsolute)
        change_connect(self.w.rotateThetaPlusAction, SIGNAL("activated()"),
                       self.moveThetaPlus)        
        change_connect(self.w.rotateThetaMinusAction, SIGNAL("activated()"),                        
                       self.moveThetaMinus)
        change_connect(self.w.movetype_combox, 
                       SIGNAL("activated(const QString&)"), 
                       self.setup_movetype)
	
	change_connect(self.exitFuseAction, SIGNAL("triggered()"), 
		       self.w.toolsDone)
        
        return
    
    def getFlyoutActionList(self): #Ninad 20070618
	""" Returns a tuple that contains mode spcific actionlists in the 
	added in the flyout toolbar of the mode. 
	CommandManager._createFlyoutToolBar method calls this 
	@return: params: A tuple that contains 3 lists: 
	(subControlAreaActionList, commandActionLists, allActionsList)"""	
		
	#'allActionsList' returns all actions in the flyout toolbar 
	#including the subcontrolArea actions
	allActionsList = []
	
	#Action List for  subcontrol Area buttons. 
	#In this mode, there is really no subcontrol area. 
	#We will treat subcontrol area same as 'command area' 
	#(subcontrol area buttons will have an empty list as their command area 
	#list). We will set  the Comamnd Area palette background color to the
	#subcontrol area.
	
	subControlAreaActionList =[] 
		
	self.exitFuseAction = QtGui.QWidgetAction(self.w)
	self.exitFuseAction.setText("Exit Fuse")
	self.exitFuseAction.setCheckable(True)
	self.exitFuseAction.setChecked(True)
	self.exitFuseAction.setIcon(geticon("ui/actions/Toolbars/Smart/Exit"))
	subControlAreaActionList.append(self.exitFuseAction)
	
	separator = QtGui.QAction(self.w)
	separator.setSeparator(True)
	subControlAreaActionList.append(separator) 
			
	allActionsList.extend(subControlAreaActionList)
	
	#Empty actionlist for the 'Command Area'
	commandActionLists = [] 
	
	#Append empty 'lists' in 'commandActionLists equal to the 
	#number of actions in subControlArea 
	for i in range(len(subControlAreaActionList)):
	    lst = []
	    commandActionLists.append(lst)
	    	
	params = (subControlAreaActionList, commandActionLists, allActionsList)
	
	return params
    
    def updateCommandManager(self, bool_entering = True):#Ninad 20070618
	''' Update the command manager '''	
	# object that needs its own flyout toolbar. In this case it is just 
	#the mode itself. 
	
	action = self.w.toolsFuseChunksAction
	obj = self  	    	    
	self.w.commandManager.updateCommandManager(action,
						   obj, 
						   entering =bool_entering)
        
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
        self.toleranceLB.setText(tol_str) 
    
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
        if fuse_mode == str(MAKEBONDS): self.goPB.setText('Make Bonds')
        else: self.goPB.setText('Fuse Atoms') 
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
    

    def leftDown(self, event):        
        """Move the selected object(s).
        Overrides modifymode.LeftDown
        """
        self.clear_leftA_variables() #bruce 070605 added this (guess at what's needed)
        env.history.statusbar_msg("") #bruce 070605

        if self.isConstrainedDragAlongAxis:
            self.leftADown(event)
            return
       
        if self.w.rotateFreeAction.isChecked():
            self.leftCntlDown(event)
        
        self.reset_drag_vars()
        
        self.LMB_press_event = QMouseEvent(event) # Make a copy of this event and save it. 
        # We will need it later if we change our mind and start selecting a 2D region in leftDrag().
        # Copying the event in this way is necessary because Qt will overwrite <event> later (in 
        # leftDrag) if we simply set self.LMB_press_event = event.  mark 060220
        
        self.LMB_press_pt_xy = (event.pos().x(), event.pos().y())
            # <LMB_press_pt_xy> is the position of the mouse in window coordinates when the LMB was pressed.
            # Used in mouse_within_stickiness_limit (called by leftDrag() and other methods).
            # We don't bother to vertically flip y using self.height (as mousepoints does),
            # since this is only used for drag distance within single drags.
       
##        from constants import GL_FAR_Z

        self.o.SaveMouse(event)
        self.picking = True
        self.dragdist = 0.0
        self.transDelta = 0 # X, Y or Z deltas for translate.
        self.rotDelta = 0 # delta for constrained rotations.
        self.moveOffset = [0.0, 0.0, 0.0] # X, Y and Z offset for move.
        
        # This needs to be refactored further into move and translate methods. mark 060301.
        
        # Move section
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
            #bruce 060316 replaced equivalent old code with this new method
        self.startpt = self.movingPoint # Used in leftDrag() to compute move offset during drag op.
        
        # end of Move section
           
        # Translate section     
        if self.isMoveGroupBoxActive:            
            if self.moveOption != 'MOVEDEFAULT':
                if self.moveOption == 'TRANSX': 
                    ma = V(1,0,0) # X Axis
                    self.axis = 'X'
                elif self.moveOption == 'TRANSY': 
                    ma = V(0,1,0) # Y Axis
                    self.axis = 'Y'
                elif self.moveOption == 'TRANSZ': 
                    ma = V(0,0,1) # Z Axis
                    self.axis = 'Z'
                else: print "modifyMode: Error - unknown moveOption value =", self.moveOption
                
                ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
                # When in the front view, right = 1,0,0 and up = 0,1,0, so ma will be computed as 0,0.
                # This creates a special case problem when the user wants to constrain rotation around
                # the Z axis because Zmat will be zero.  So we have to test for this case (ma = 0,0) and
                # fix ma to -1,0.  This was needed to fix bug 537.  Mark 050420
                if ma[0] == 0.0 and ma[1] == 0.0: ma = [-1.0, 0.0] 
                self.Zmat = A([ma,[-ma[1],ma[0]]])                
                # end of Translate section                
        else:
            if self.rotateOption != 'ROTATEDEFAULT':
                if self.rotateOption == 'ROTATEX': 
                    ma = V(1,0,0) # X Axis
                    self.axis = 'X'
                elif self.rotateOption == 'ROTATEY': 
                    ma = V(0,1,0) # Y Axis
                    self.axis = 'Y'
                elif self.rotateOption == 'ROTATEZ': 
                    ma = V(0,0,1) # Z Axis
                    self.axis = 'Z'
                else: print "modifyMode: Error - unknown rotateOption value =", self.rotateOption

                ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
                # When in the front view, right = 1,0,0 and up = 0,1,0, so ma will be computed as 0,0.
                # This creates a special case problem when the user wants to constrain rotation around
                # the Z axis because Zmat will be zero.  So we have to test for this case (ma = 0,0) and
                # fix ma to -1,0.  This was needed to fix bug 537.  Mark 050420
                if ma[0] == 0.0 and ma[1] == 0.0: ma = [-1.0, 0.0] 
                self.Zmat = A([ma,[-ma[1],ma[0]]])
                       
                                    
        #Permit movable object picking upon left down.             
        obj = self.get_obj_under_cursor(event)
        # If highlighting is turned on, get_obj_under_cursor() returns atoms, singlets, bonds, jigs,
        # or anything that can be highlighted and end up in glpane.selobj. [bruce revised this comment, 060725]
            # If highlighting is turned off, get_obj_under_cursor() returns atoms and singlets (not bonds or jigs).
            # [not sure if that's still true -- probably not. bruce 060725 addendum]
        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            return
        
        if isinstance(obj, Atom) and obj.is_singlet(): # Cursor over a singlet
            self.singletLeftDown(obj, event)
                # no win_update() needed. It's the responsibility of singletLeftDown to do it if needed.
            return                
        elif isinstance(obj, Atom) and not obj.is_singlet(): # Cursor over a real atom
            self.atomLeftDown(obj, event)
        elif isinstance(obj, Bond) and not obj.is_open_bond(): # Cursor over a bond.
            self.bondLeftDown(obj, event)
        elif isinstance(obj, Jig): # Cursor over a jig.
            self.jigLeftDown(obj, event)
        else: # Cursor is over something else other than an atom, singlet or bond. 
            # The program never executes lines in this else statement since
            # get_obj_under_cursor() only returns atoms, singlets or bonds.
            # [perhaps no longer true, if it ever was -- bruce 060725]
            pass
        
        self.w.win_update()
            
       
    def leftDrag(self, event):
        """Move the selected object(s):
        - in the plane of the screen following the mouse, 
        - or slide and rotate along the an axis
        Overrides modifyMode.leftDrag
        """
        
        if not self.picking: return
        
        if not self.o.assy.getSelectedMovables(): return
        
        if self.isConstrainedDragAlongAxis:
            try:
                self.leftADrag(event)
                    ### WARNING: this call has not been reviewed in detail since I rewrote that method
                    # and leftADown in modifyMode thismorning. I did try to adapt self.leftDown to this
                    # but it's untested. [bruce 070605]
                return
            except:
                print "Key A pressed after Left Down. controlled translation will not be performed"
                pass
        
        if self.w.rotateFreeAction.isChecked():
            self.leftCntlDrag(event)
            return
        
        # Fixes bugs 583 and 674 along with change in keyRelease.  Mark 050623
        if self.movingPoint is None: self.leftDown(event) # Fix per Bruce's email.  Mark 050704
        
        if self.isMoveGroupBoxActive:
            # Move section
            if self.moveOption == 'MOVEDEFAULT':
                deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                           self.o.MousePos[1] - event.pos().y(), 0.0)
    
                point = self.dragto( self.movingPoint, event) #bruce 060316 replaced old code with dragto (equivalent)
            
                # Print status bar msg indicating the current move delta.
                if 1:
                    self.moveOffset = point - self.startpt # Fixed bug 929.  mark 060111
                    msg = "Offset: [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.moveOffset[0], self.moveOffset[1], self.moveOffset[2])
                    env.history.statusbar_msg(msg)
    
                self.o.assy.movesel(point - self.movingPoint)
                self.movingPoint = point    
                # end of Move section
            
            # Translate section
            else:
                w=self.o.width+0.0
                h=self.o.height+0.0
                deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                           self.o.MousePos[1] - event.pos().y())
                a =  dot(self.Zmat, deltaMouse)
                dx,dy =  a * V(self.o.scale/(h*0.5), 2*pi/w)
                if self.moveOption == 'TRANSX' :     ma = V(1,0,0) # X Axis
                elif self.moveOption == 'TRANSY' :  ma = V(0,1,0) # Y Axis
                elif self.moveOption == 'TRANSZ' :  ma = V(0,0,1) # Z Axis
                else: 
                    print "modifyMode.leftDrag: Error - unknown moveOption value =",
                    self.moveOption                
                    return       
                self.transDelta += dx # Increment translation delta                   
                self.o.assy.movesel(dx*ma) 
                
        else:
            #Rotate section      
            w=self.o.width+0.0
            h=self.o.height+0.0
            deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())
            a =  dot(self.Zmat, deltaMouse)
            dx,dy =  a * V(self.o.scale/(h*0.5), 2*pi/w)

            if self.rotateOption == 'ROTATEX' :     ma = V(1,0,0) # X Axis
            elif self.rotateOption == 'ROTATEY' :  ma = V(0,1,0) # Y Axis
            elif self.rotateOption == 'ROTATEZ' :  ma = V(0,0,1) # Z Axis
            else: 
                print "modifyMode.leftDrag: Error - unknown rotateOption value =", self.rotateOption                
                return                
            qrot = Q(ma,-dy) # Quat for rotation delta.
            self.rotDelta += qrot.angle *180.0/pi * sign(dy) # Increment rotation delta (and convert to degrees)
            
            self.updateRotationDeltaLabels(self.rotateOption, self.rotDelta)
            self.o.assy.rotsel(qrot) 
            
            #End of Rotate Section
            
        # Print status bar msg indicating the current translation and rotation delta.
        if self.o.assy.selmols:
            msg = "%s delta: [%.2f Angstroms] [%.2f Degrees]" % (self.axis, self.transDelta, self.rotDelta)
            env.history.statusbar_msg(msg)
            
                                
        # Print status bar msg indicating the current translation and rotation delta.
        if self.o.assy.selmols:
            msg = "%s delta: [%.2f Angstroms] [%.2f Degrees]" % (self.axis, self.transDelta, self.rotDelta)
            env.history.statusbar_msg(msg)
            
        # common finished code
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()        
        # end of leftDrag
    
    def leftUp(self, event):  
        '''Overrides leftup method of modifyMode'''        
        if self.dragdist < 2:
            selectMolsMode.leftUp(self,event)
        # end of leftUp
    
           
    def leftCntlDown(self, event):
        """Setup a trackball action on the selected chunk(s).
        """
        if not self.o.assy.getSelectedMovables(): return
        
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        self.picking = True
        self.dragdist = 0.0



    def leftCntlUp(self, event):
        ''' Overrides modifyMode.leftCntlUp'''  
        
        self.EndPick(event, SUBTRACT_FROM_SELECTION)
        

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
        bondline_color = get_selCurve_color(0,self.o.backgroundColor) # Color of bond lines
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
        self.toleranceLB.setText(tol_str)

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
        if self.mergeCB.isChecked() and self.bondable_pairs_atoms:
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
        self.toleranceLB.setText(tol_str)
        

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
        if self.mergeCB.isChecked() and self.overlapping_atoms:
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
