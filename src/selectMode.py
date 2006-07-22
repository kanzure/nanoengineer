# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
selectMode.py -- Select Chunks and Select Atoms modes, also used as superclasses for some other modes

$Id$

Some things that need cleanup in this code [bruce 060721 comment]: ####@@@@

- redundant use of glRenderMode (see comment where that is used)

- division between selectMode and selectAtomsMode

- drag algorithms for various object types and modifier keys are split over lots of methods
with lots of common but not identical code. For example, a set of atoms and jigs can be dragged
in the same way, by two different pieces of code depending on whether an atom or jig in the set
was clicked on. If this was cleaned up, so that objects clicked on would answer questions about
how to drag them, and if a drag_handler object was created to handle the drag (or the object itself
can act as one, if only it is dragged and if it knows how), the code would be clearer, some bugs
would be easier to fix, and some NFRs easier to implement.

"""

from modes import *
from HistoryWidget import orangemsg
from chunk import molecule
import env
from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice

_count = 0

#bruce 060315 revised DRAG_STICKINESS_LIMIT to be in pixels

##DRAG_STICKINESS_LIMIT = 0.03 # in Angstroms with respect to the front clipping plane.
##    #& To do: Change to pixel units and make it a user pref.  Also consider a different var/pref
##    #& for singlet vs. atom drag stickiness limits. Mark 060213.

DRAG_STICKINESS_LIMIT = 4 # in pixels; reset in each leftDown via a debug_pref
    #& To do: Make it a user pref in the Prefs Dialog.  Also consider a different var/pref
    #& for singlet vs. atom drag stickiness limits. Mark 060213.

_ds_Choice = Choice([0,1,2,3,4,5,6,7,8,9,10], default_value = DRAG_STICKINESS_LIMIT)

DRAG_STICKINESS_LIMIT_prefs_key = "A7/Drag Stickiness Limit"

def set_DRAG_STICKINESS_LIMIT_from_pref(): #bruce 060315
    global DRAG_STICKINESS_LIMIT
    DRAG_STICKINESS_LIMIT = debug_pref("DRAG_STICKINESS_LIMIT (pixels)",
                                       _ds_Choice,
                                       non_debug = True,
                                       prefs_key = DRAG_STICKINESS_LIMIT_prefs_key)
    return

set_DRAG_STICKINESS_LIMIT_from_pref() # also called in selectAtomsMode.leftDown
    # (ideally, clean up this pref code a lot by not passing DRAG_STICKINESS_LIMIT as an arg to the subr that uses it)
    # we do this early so the debug_pref is visible in the debug menu before entering selectAtomsMode.

## TEST_PYREX_OPENGL = 0 # bruce 060209 moved this to where it's used (below), and changed it to a debug_pref

def do_what_MainWindowUI_should_do(w):
    """This creates the Select Atoms (not the Select Chunks) dashboard."""
     
    w.selectAtomsDashboard.clear()

    w.depositAtomLabel = QLabel(w.selectAtomsDashboard,"Select Atoms")
    w.depositAtomLabel.setText(" Select Atoms ")
    w.selectAtomsDashboard.addSeparator()

    selectLabel = QLabel(w.selectAtomsDashboard, "Select:")
    selectLabel.setText("Select: ")
    
    w.elemFilterComboBox = QComboBox(0,w.selectAtomsDashboard, "elemFilterComboBox")
    
    #w.selectConnectedAction.addTo(w.selectAtomsDashboard)
    #w.selectDoublyAction.addTo(w.selectAtomsDashboard)
        # Removed these now that select connected works on double-click. mark 060220.
    
    w.selectAtomsDashboard.addSeparator()

    transmute2Label = QLabel(w.selectAtomsDashboard, "Transmute_to:")
    transmute2Label.setText("Transmute to: ")
    w.transmute2ComboBox = QComboBox(0,w.selectAtomsDashboard, "transmute2ComboBox")
    w.connect(w.transmute2ComboBox, SIGNAL("activated(int)"), w.transmuteElementChanged)

    w.atomSelect_hybridComboBox = QComboBox(0, w.selectAtomsDashboard, "hybridComboBox") 
    # Set the width of the hybrid drop box.  Mark 050810.
    width = w.hybridComboBox.fontMetrics().width(" sp2(graphitic) ")
    w.atomSelect_hybridComboBox.setMinimumSize ( QSize (width, 0) )

    w.transmuteButton = QPushButton("Transmute", w.selectAtomsDashboard)
                 
    w.transmuteCheckBox = QCheckBox(" Force to Keep Bonds", w.selectAtomsDashboard)
    
    w.selectAtomsDashboard.addSeparator()
    w.selectAtomsDashboard.highlightingCB = QCheckBox("Highlighting", w.selectAtomsDashboard)

    w.selectAtomsDashboard.addSeparator()
    w.toolsDoneAction.addTo(w.selectAtomsDashboard)
    w.selectAtomsDashboard.setLabel("Select Atoms")

    w.elemFilterComboBox.clear()
    # WARNING:
    # these are identified by *position*, not by their text, using corresponding entries in eCCBtab1;
    # this is done by win.elemChange even though nothing but depositMode calls that;
    # the current element is stored in win.Element (as an atomic number ###k).
    # All this needs cleanup so it's safer to modify this and so atomtype can sometimes be included.
    # Both eCCBtab1 and eCCBtab2 are set up and used in MWsemantics but should be moved here,
    # or perhaps with some part moved into elements.py if it ought to share code with elementSelector.py
    # and elementColors.py (though it doesn't now).
    w.elemFilterComboBox.insertItem("All Elements")
    w.elemFilterComboBox.insertItem("Hydrogen")
    w.elemFilterComboBox.insertItem("Helium")
    w.elemFilterComboBox.insertItem("Boron")
    w.elemFilterComboBox.insertItem("Carbon") # will change to two entries, Carbon(sp3) and Carbon(sp2) -- no, use separate combobox
    w.elemFilterComboBox.insertItem("Nitrogen")
    w.elemFilterComboBox.insertItem("Oxygen")
    w.elemFilterComboBox.insertItem("Fluorine")
    w.elemFilterComboBox.insertItem("Neon")
    w.elemFilterComboBox.insertItem("Aluminum")
    w.elemFilterComboBox.insertItem("Silicon")
    w.elemFilterComboBox.insertItem("Phosphorus")
    w.elemFilterComboBox.insertItem("Sulfur")
    w.elemFilterComboBox.insertItem("Chlorine")
    w.elemFilterComboBox.insertItem("Argon")
    w.elemFilterComboBox.insertItem("Germanium")
    w.elemFilterComboBox.insertItem("Arsenic")
    w.elemFilterComboBox.insertItem("Selenium")
    w.elemFilterComboBox.insertItem("Bromine")
    w.elemFilterComboBox.insertItem("Krypton")
    #w.elemFilterComboBox.insertItem("Antimony")
    #w.elemFilterComboBox.insertItem("Tellurium")
    #w.elemFilterComboBox.insertItem("Iodine")
    #w.elemFilterComboBox.insertItem("Xenon")
    
    w.transmute2ComboBox.clear()
    w.transmute2ComboBox.insertItem("Hydrogen")
    w.transmute2ComboBox.insertItem("Helium")
    w.transmute2ComboBox.insertItem("Boron")
    w.transmute2ComboBox.insertItem("Carbon") # will change to two entries, Carbon(sp3) and Carbon(sp2) -- no, use separate combobox
    w.transmute2ComboBox.insertItem("Nitrogen")
    w.transmute2ComboBox.insertItem("Oxygen")
    w.transmute2ComboBox.insertItem("Fluorine")
    w.transmute2ComboBox.insertItem("Neon")
    w.transmute2ComboBox.insertItem("Aluminum")
    w.transmute2ComboBox.insertItem("Silicon")
    w.transmute2ComboBox.insertItem("Phosphorus")
    w.transmute2ComboBox.insertItem("Sulfur")
    w.transmute2ComboBox.insertItem("Chlorine")
    w.transmute2ComboBox.insertItem("Argon")
    w.transmute2ComboBox.insertItem("Germanium")
    w.transmute2ComboBox.insertItem("Arsenic")
    w.transmute2ComboBox.insertItem("Selenium")
    w.transmute2ComboBox.insertItem("Bromine")
    w.transmute2ComboBox.insertItem("Krypton")
    
    from whatsthis import create_whats_this_descriptions_for_selectAtomsMode
    create_whats_this_descriptions_for_selectAtomsMode(w)

    return

# ==

class selectMode(basicMode):
    "Superclass for Select Chunks, Select Atoms, Build, and other modes."
    # Warning: some of the code in this superclass is probably only used in selectAtomsMode and its subclasses,
    # but it's not clear exactly which code this applies to. [bruce 060721 comment]
    
    # class constants
    backgroundColor = 189/255.0, 228/255.0, 238/255.0
    gridColor = (0.0, 0.0, 0.6)

    # default initial values
    savedOrtho = 0

    selCurve_length = 0.0
        # <selCurve_length> is the current length (sum) of all the selection curve segments.
    
    selCurve_List = []
        # <selCurve_List> contains a list of points used to draw the selection curve.  The points lay in the 
        # plane parallel to the screen, just beyond the front clipping plane, so that they are always
        #  inside the clipping volume.
    selArea_List = []
        # <selArea_List> contains a list of points that define the selection area.  The points lay in 
        # the plane parallel to the screen and pass through the center of the view.  The list
        # is used by pickrect() and pickline() to make the selection.
    selShape = SELSHAPE_RECT
        # <selShape> the current selection shape.
    hover_highlighting_enabled = True
        # Set this to False if you want to disable hover highlighting.

    # init_gui handles all the GUI display when entering a mode    
    def init_gui(self):
        pass # let the subclass handle everything for the GUI - Mark [2004-10-11]

    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        pass # let the subclass handle everything for the GUI - Mark [2004-10-11]
    
# == LMB event handling methods ====================================

# Important Terms: [mark 060205]
#
# "selection curve": the collection of line segments drawn by the cursor when defining
# the selection area.  These line segments become the selection lasso when (and if) 
# the selection rectangle disappears. When the selection rectangle is still displayed,
# the selection curve consists of those line segment that are drawn between opposite 
# corners of the selection rectangle. The line segments that define/draw the 
# rectangle itself are not part of the selection curve, however.
# Also, it is worth noting that the line segments of the selection curve are also drawn 
# just beyond the front clipping plane. The variable <selCurve_List> contains the list
# of points that draw the line segments of the selection curve.
#
# "selection area": determined by the selection curve, it is the area that defines what
# is picked (or unpicked).  The variable <selArea_List> contains the list of points that
# define the selection area used to pick/unpick objects. The points in <selArea_List> 
# lay in the plane parallel to the screen and pass through the center of the view.
#
# "selection rectangle": the rectangular selection determined by the first and last points 
# of a selection curve.  These two points define the opposite corners of the rectangle.
#
# "selection lasso": the lasso selection defined by all the points (and line segements)
# in the selection curve.

# == LMB down-click (button press) methods
   
    def leftShiftDown(self, event):
        self.leftDown(event)

    def leftCntlDown(self, event):
        self.leftDown(event)
        
    def leftDown(self, event):
        self.select_2d_region(event)

# == LMB drag methods

    def leftShiftDrag(self, event):
        self.leftDrag(event)
            
    def leftCntlDrag(self, event):
        self.leftDrag(event)
        
    def leftDrag(self, event):
        self.continue_selection_curve(event)

# == LMB up-click (button release) methods

    def leftShiftUp(self, event):
        self.leftUp(event)

    def leftCntlUp(self, event):
        self.leftUp(event)
                
    def leftUp(self, event):
        self.end_selection_curve(event)
        
# == LMB double click method

    def leftDouble(self, event):
        pass
        
# == end of LMB event handlers.

#== Selection Curve helper methods

    def select_2d_region(self, event):
        '''Start 2D selection of a region.
        '''
        if self.o.modkeys is None:
            self.start_selection_curve(event, START_NEW_SELECTION)
        if self.o.modkeys == 'Shift':
            self.start_selection_curve(event, ADD_TO_SELECTION)
        if self.o.modkeys == 'Control':
            self.start_selection_curve(event, SUBTRACT_FROM_SELECTION)
        if self.o.modkeys == 'Shift+Control':
             self.start_selection_curve(event, DELETE_SELECTION)
        return
        
    def start_selection_curve(self, event, sense):
        """Start a new selection rectangle/lasso.
        """
        self.selSense = sense
            # <selSense> is the type of selection.
        self.picking = True
            # <picking> is used to let continue_selection_curve() and end_selection_curve() know 
            # if we are in the process of defining/drawing a selection curve or not, where:
            # True = in the process of defining selection curve
            # False = finished/not defining selection curve
        selCurve_pt, selCurve_AreaPt = self.o.mousepoints(event, just_beyond = 0.01)
            # mousepoints() returns a pair (tuple) of points (Numeric arrays of x,y,z)
            # that lie under the mouse pointer, just beyond the near clipping plane
            # <selCurve_pt> and in the plane of the center of view <selCurve_AreaPt>.
        self.selCurve_List = [selCurve_pt]
            # <selCurve_List> contains the list of points used to draw the selection curve.  The points lay in the 
            # plane parallel to the screen, just beyond the front clipping plane, so that they are always
            #  inside the clipping volume.
        self.o.selArea_List = [selCurve_AreaPt]
            # <selArea_List> contains the list of points that define the selection area.  The points lay in 
            # the plane parallel to the screen and pass through the center of the view.  The list
            # is used by pickrect() and pickline() to make the selection.
        self.selCurve_StartPt = self.selCurve_PrevPt = selCurve_pt
            # <selCurve_StartPt> is the first point of the selection curve.  It is used by 
            # continue_selection_curve() to compute the net distance between it and the current 
            # mouse position.
            # <selCurve_PrevPt> is the previous point of the selection curve.  It is used by 
            # continue_selection_curve() to compute the distance between the current mouse 
            # position and the previous one.
            # Both <selCurve_StartPt> and <selCurve_PrevPt> are used by 
            # basicMode.drawpick().
        self.selCurve_length = 0.0
            # <selCurve_length> is the current length (sum) of all the selection curve segments.

    def continue_selection_curve(self, event):
        """Add another line segment to the current selection curve.
        """
        if not self.picking: return
        
        selCurve_pt, selCurve_AreaPt = self.o.mousepoints(event, 0.01)
            # The next point of the selection curve, where <selCurve_pt> is the point just beyond
            # the near clipping plane and <selCurve_AreaPt> is in the plane of the center of view.
        self.selCurve_List += [selCurve_pt]
        self.o.selArea_List += [selCurve_AreaPt]
        
        self.selCurve_length += vlen(selCurve_pt - self.selCurve_PrevPt)
            # add length of new line segment to <selCurve_length>.
            
        chord_length = vlen(selCurve_pt - self.selCurve_StartPt)
            # <chord_length> is the distance between the (first and last/current) endpoints of the 
            # selection curve.
        
        if self.selCurve_length < 2*chord_length:
            # Update the shape of the selection_curve.
            # The value of <selShape> can change back and forth between lasso and rectangle
            # as the user continues defining the selection curve.
            self.selShape = SELSHAPE_RECT
        else:
            self.selShape = SELSHAPE_LASSO
            
        self.selCurve_PrevPt = selCurve_pt
        
        self.o.gl_update()
        
    def end_selection_curve(self, event):
        """Close the selection curve and do the selection.
        """
        if not self.picking: return
        self.picking = False

        selCurve_pt, selCurve_AreaPt = self.o.mousepoints(event, 0.01)

        if self.selCurve_length/self.o.scale < 0.03:
            # didn't move much, call it a click
            #bruce 060331 comment: the behavior here is related to what it is when we actually just click,
            # but it's implemented by different code -- for example, delete_at_event in this case
            # as opposed to delete_atom_and_baggage in the other circumstance (which both have similar
            # implementations of atom filtering and history messages, but are in different files).
            # It's not clear to me (reviewing this code) whether the behavior should be (or is) identical;
            # whether or not it's identical, it would be better if common code was used, to the extent
            # that the behavior in these two circumstances is supposed to be related.
            has_jig_selected = False 
            
            if self.o.jigSelectionEnabled and self.jigGLSelect(event, self.selSense):
                has_jig_selected = True
            
            if not has_jig_selected:
                if self.selSense == SUBTRACT_FROM_SELECTION: 
                    self.o.assy.unpick_at_event(event)
                elif self.selSense == ADD_TO_SELECTION: 
                    self.o.assy.pick_at_event(event)
                elif self.selSense == START_NEW_SELECTION: 
                    self.o.assy.onlypick_at_event(event)
                elif self.selSense == DELETE_SELECTION: 
                    self.o.assy.delete_at_event(event)
                else:
                    print 'Error in end_selection_curve(): Invalid selSense=', self.selSense
            
            # Huaicai 1/29/05: to fix zoom messing up selection bug
            # In window zoom mode, even for a big selection window, the 
            # selCurve_length/scale could still be < 0.03, so we need clean 
            # selCurve_List[] to release the rubber band selection window. One 
            # problem is its a single pick not as user expect as area pick 
        
        else:
            
            self.selCurve_List += [selCurve_pt] # Add the last point.
            self.selCurve_List += [self.selCurve_List[0]] # Close the selection curve.
            self.o.selArea_List += [selCurve_AreaPt] # Add the last point.
            self.o.selArea_List += [self.o.selArea_List[0]] # Close the selection area.
            
            self.o.shape=SelectionShape(self.o.right, self.o.up, self.o.lineOfSight)
                # Create the selection shape object.
                
            eyeball = (-self.o.quat).rot(V(0,0,6*self.o.scale)) - self.o.pov
            
            if self.selShape == SELSHAPE_RECT : # prepare a rectangle selection
                self.o.shape.pickrect(self.o.selArea_List[0], selCurve_AreaPt, -self.o.pov, self.selSense, \
                            eye=(not self.o.ortho) and eyeball)
            else: # prepare a lasso selection
                self.o.shape.pickline(self.o.selArea_List, -self.o.pov, self.selSense, \
                            eye=(not self.o.ortho) and eyeball)
        
            self.o.shape.select(self.o.assy) # do the actual selection.
                
            self.o.shape = None
                
        self.selCurve_List = []
            # (for debugging purposes, it's sometimes useful to not reset selCurve_List here,
            #  so you can see it at the same time as the selection it caused.)

        self.w.win_update()
        
#== End of Selection Curve helper methods

#== Empty Space helper methods

#& The Empty Space, Atom, Bond and Singlet helper methods should probably be moved to
#& selectAtomsMode.  I put them here because I think there is a good chance that we'll 
#& allow intermixing of atoms, chunks and jigs (and other stuff) in any mode.
#& Mark 060220.

    def emptySpaceLeftDown(self, event):
        self.objectSetup(None)
        self.cursor_over_when_LMB_pressed = 'Empty Space'
        self.select_2d_region(event)
        return
        
    def emptySpaceLeftDrag(self, event):
        self.continue_selection_curve(event)
        return
        
    def emptySpaceLeftUp(self, event):
        self.end_selection_curve(event)
        return

#== Atom selection and dragging helper methods

    def atomLeftDown(self, a, event):
        if not a.picked and self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane() # was unpickatoms and unpickparts [bruce 060721]
                # Note: a comment said that this was intended to unpick (among other things) jigs.
                # It will, since they are selectable in GLPane.
            a.pick()
        if not a.picked and self.o.modkeys == 'Shift':
            a.pick()
            
        if a.picked:
            self.cursor_over_when_LMB_pressed = 'Picked Atom'
        else:
            self.cursor_over_when_LMB_pressed = 'Unpicked Atom'
        self.atomSetup(a, event)

    def objectSetup(self, obj):
        self.current_obj = obj
        self.obj_doubleclicked = obj
        if obj is None:
            self.current_obj_clicked = False
        else:
            self.current_obj_clicked = True

            # we need to store something unique about this event;
            # we'd use serno or time if it had one... instead this _count will do.
            global _count
            _count = _count + 1
            self.current_obj_start = _count

    drag_offset = V(0,0,0) # avoid tracebacks from lack of leftDown
    
    def atomSetup(self, a, event): #bruce 060316 added <event> argument, for bug 1474
        '''Setup for a click, double-click or drag event for real atom <a>.
        '''
        #bruce 060316 set self.drag_offset to help fix bug 1474 (this should be moved into a method so singlets can call it too):
        farQ, dragpoint = self.dragstart_using_GL_DEPTH( event)
        apos0 = a.posn()
        if farQ or vlen( dragpoint - apos0 ) > a.selatom_radius() + 0.2:
            # dragpoint is not realistic -- find a better one (using code similar to innards of dragstart_using_GL_DEPTH)
            ###@@@ Note: + 0.2 is purely a guess (probably too big) -- what it should be is a new method a.max_drawn_radius(),
            # which gives max distance from center of a drawn pixel, including selatom, highlighting, wirespheres,
            # and maybe even the depth offset added by GLPane when it draws in highlighted form (not sure, it might not draw
            # into depth buffer then...) Need to fix this sometime. Not high priority, since it seems to work with 0.2,
            # and since higher than needed values would be basically ok anyway. [bruce 060316]
            if env.debug(): # leave this in until we see it printed sometime
                print "debug: fyi: atomSetup dragpoint try1 was bad, %r for %r, reverting to ptonline" % (dragpoint, apos0)
            p1, p2 = self.o.mousepoints(event)
            dragpoint = ptonline(apos0, p1, norm(p2-p1))
            del p1,p2
        del farQ, event
        self.drag_offset = dragpoint - apos0 # some subclass drag methods can use this with self.dragto_with_offset()
##        if env.debug():
##            print "set event-%d drag_offset" % _count, self.drag_offset

        self.objectSetup(a)
        
        if len(self.o.assy.selatoms_list()) == 1:
            #bruce 060316 question: does it matter, in this case, whether <a> is the single selected atom? is it always??
            self.baggage, self.nonbaggage = a.baggage_and_other_neighbors()
            self.drag_multiple_atoms = False
        else:
            self.dragatoms, self.baggage, self.dragchunks = self.get_dragatoms_and_baggage()
                # if no atoms in alist, dragatoms and baggage are empty lists, which is good.
            self.drag_multiple_atoms = True
            self.maybe_use_bc = debug_pref("use bc to drag mult?", Choice_boolean_False) #bruce 060414
            
        # dragjigs contains all the selected jigs.
        self.dragjigs = self.o.assy.getSelectedJigs()

    def get_dragatoms_and_baggage(self): # by mark. later optimized and extended by bruce, 060410.
        
        #bruce 060410 optimized this; it had a quadratic algorithm (part of the cause of bugs 1828 / 1438), and other slownesses.
        # The old code is commented out for comparison.
        #
        # Note: as of 060410, it looks like callers only care about the total set of atoms in the two returned lists,
        # not about which atom is in which list, so the usefulness of having two lists is questionable.
        # But I preserved the behavior regarding how atoms are distributed between the two lists.
        # (I didn't preserve the order of the lists, since I'm sure this shouldn't matter.)
        
        dragatoms = []
        baggage = []
        ## nonbaggage = []
        
        selatoms = self.o.assy.selatoms
##        selatoms = self.o.assy.selatoms_list()
        
        # Accumulate all the baggage from the selected atoms, which can include
        # selected atoms if a selected atom is another selected atom's baggage.
        # BTW, it is not possible for an atom to end up in self.baggage twice.
        
        for at in selatoms.itervalues():
            bag, nbag = at.baggage_and_other_neighbors()
            baggage.extend(bag) # the baggage we'll keep.
            #all_nonbaggage += nonbaggage
##        for at in selatoms[:]:
##            bag, nbag = at.baggage_and_other_neighbors()
##            baggage += bag # the baggage we'll keep.
##            #all_nonbaggage += nonbaggage

        bagdict = dict([(at.key, None) for at in baggage]) # bruce 060410 added bagdict
                
        # dragatoms should contain all the selected atoms minus atoms that are also baggage.
        # It is critical that dragatoms does not contain any baggage atoms or they 
        # will be moved twice in drag_selected_atoms(), so we remove them here.
        for key, at in selatoms.iteritems():
            if key not in bagdict: # no baggage atoms in dragatoms.
                dragatoms.append(at)
##        for at in selatoms[:]:
##            if not at in baggage: # no baggage atoms in dragatoms.
##                dragatoms.append(at)
                
        # Accumulate all the nonbaggage bonded to the selected atoms.
        # We also need to keep a record of which selected atom belongs to
        # each nonbaggage atom.  This is not implemented yet, but will be needed
        # to get drag_selected_atoms() to work properly.  I'm commenting it out for now.
        # mark 060202.
        #for at in all_nonbaggage[:]:
        #    if not at in dragatoms:
        #        nonbaggage.append(at)
        
        # Debugging print statements.  mark 060202.
        #print "dragatoms = ", dragatoms
        #print "baggage = ", baggage    
        #print "nonbaggage = ", nonbaggage

        #bruce 060410 new code: optimize when all atoms in existing chunks are being dragged.
        # (##e Soon we hope to extend this to all cases, by making new temporary chunks to contain dragged atoms,
        #  invisibly to the user, taking steps to not mess up existing chunks re their hotspot, display mode, etc.)
##        mols = {} # id(mol) -> mol for all involved mols
##        molcounts = {} # id(mol) -> number of atoms we're dragging in that mol
##        atoms = {} # atom.key -> atom for all dragged atoms
##        def doit(at):
##            mol = at.molecule
##            c = molcounts.setdefault(id(mol), 0)
##            molcounts[id(mol)] = c + 1
##            if not c:
##                mols[id(mol)] = mol
##            return # from doit
        atomsets = {} # id(mol) -> (dict from atom.key -> atom) for dragged atoms in that mol
        def doit(at):
            mol = at.molecule
            atoms = atomsets.setdefault(id(mol), {}) # dragged atoms which are in this mol, so far, as atom.key -> atom
            atoms[at.key] = at # atoms serves later to count them, to let us make fragments, and to identify the source mol
        for at in dragatoms:
            doit(at)
        for at in baggage:
            doit(at)
        dragatoms = []
        baggage = [] # no longer used
        dragchunks = []
        for atomset in atomsets.itervalues():
            assert atomset
            mol = None # to detect bugs
            for key, at in atomset.iteritems():
                mol = at.molecule
                break # i.e. pick an arbitrary item... is there an easier way? is this way efficient?
            if len(mol.atoms) == len(atomset):
                # all mol's atoms are being dragged
                dragchunks.append(mol)
            else:
                # some but not all of mol's atoms are being dragged
                ##e soon we can optimize this case too by separating those atoms into a temporary chunk,
                # but for now, just drag them individually as before:
                dragatoms.extend(atomset.itervalues())
                    #k itervalues ok here? Should be, and seems to work ok. Faster than .values? Might be, in theory; not tested.
            continue
        
        return dragatoms, baggage, dragchunks
        
    def delete_atom_and_baggage(self, event):
        '''If the object under the cursor is an atom, delete it and any baggage.  
        Return the result of what happened.
        '''
        a = self.get_real_atom_under_cursor(event)

        if a is None:
            return None
            
        if a.filtered(): # mark 060304.
            # note: bruce 060331 thinks refusing to delete filtered atoms, as this does, is a bad UI design;
            # fo details, see longer comment on similar code in delete_at_event (ops_select.py).
            # (Though when highlighting is disabled, it's arguable that this is more desirable than bad -- conceivably.)
            #bruce 060331 adding orangemsg, since we should warn user we didn't do what they asked.
            env.history.message(orangemsg("Cannot delete " + str(a) + " since it is being filtered. "\
                                "Hit Escape to clear the selection filter."))
            return None
        
        a.deleteBaggage()
        result = "deleted %r" % a
        self.neighbors_of_last_deleted_atom = a.realNeighbors()
        a.kill()
        self.o.selatom = None #bruce 041130 precaution
        self.o.assy.changed()
        self.w.win_update()
        return result
        
    def atomDrag(self, a, event):
        """Drag real atom <a> and any other selected atoms and/or jigs.  <event> is a drag event.
        """
        apos0 = a.posn()
        apos1 = self.dragto_with_offset(apos0, event, self.drag_offset ) #bruce 060316 fixing bug 1474
        delta = apos1 - apos0 # xyz delta between new and current position of <a>.
        
        
        if self.drag_multiple_atoms:
            self.drag_selected_atoms(delta)
        else:
            self.drag_selected_atom(a, delta) #bruce 060316 revised API [##k could this case be handled by the multiatom case??]
        
        self.drag_selected_jigs(delta)
        
        self.atomDragUpdate(a, apos0)
        return
        
    def drag_selected_atom(self, a, delta): #bruce 060316 revised API for uniformity and no redundant dragto, re bug 1474
        """Drag real atom <a> by the xyz offset <delta>, adjusting its baggage atoms accordingly
        (how that's done depends on its other neighbor atoms).
        """
        apo = a.posn()
        ## delta = px - apo
        px = apo + delta
        
        n = self.nonbaggage
            # n = real atoms bonded to <a> that are not singlets or monovalent atoms.
            # they need to have their own baggage adjusted below.
        
        old = V(0,0,0)
        new = V(0,0,0)
            # old and new are used to compute the delta quat for the average 
            # non-baggage bond [in a not-very-principled way, which doesn't work well -- bruce 060629]
            # and apply it to <a>'s baggage
        
        for at in n:
            # Since adjBaggage() doesn't change at.posn(), I switched the order for readability.
            # It is now more obvious that <old> and <new> have no impact on at.adjBaggage(). 
            # mark 060202.
            at.adjBaggage(a, px) # Adjust the baggage of nonbaggage atoms.
            old += at.posn()-apo
            new += at.posn()-px
        
        # Handle baggage differently if <a> has nonbaggage atoms.
        if n: # If <a> has nonbaggage atoms, move and rotate its baggage atoms.
            # slight safety tweaks to old code, though we're about to add new code to second-guess it [bruce 060629]
            old = norm(old) #k not sure if these norms make any difference
            new = norm(new)
            if old and new:
                q = Q(old,new)
                for at in self.baggage:
                    at.setposn(q.rot(at.posn()-apo)+px) # similar to adjBaggage, but also has a translation
            else:
                for at in self.baggage:
                    at.setposn(at.posn()+delta)
            #bruce 060629 for "bondpoint problem": treat that as an initial guess --
            # now fix them better (below, after we've also moved <a> itself.)
        else: # If <a> has no nonbaggage atoms, just move each baggage atom (no rotation).
            for at in self.baggage:
                at.setposn(at.posn()+delta)
        a.setposn(px)
        # [bruce 041108 writes:]
        # This a.setposn(px) can't be done before the at.adjBaggage(a, px)
        # in the loop before it, or adjBaggage (which compares a.posn() to
        # px) would think atom <a> was not moving.

        if n:
            #bruce 060629 for bondpoint problem
            a.reposition_baggage(self.baggage)
        return

    #bruce 060414 move selatoms optimization (won't be enabled by default in A7)
    # (very important for dragging atomsets that are part of big chunks but not all of them)
    # UNFINISHED -- still needs:
    # - failsafe for demolishing bc if drag doesn't end properly
    # - disable undo cp's when bc exists (or maybe during any drag of any kind in any mode)
    # - fix checkparts assertfail (or disable checkparts) when bc exists and atom_debug set
    # - not a debug pref anymore
    # - work for single atom too (with its baggage, implying all bps for real atoms in case chunk rule for that matters)
    # - (not directly related:)
    #   review why reset_drag_vars is only called in selectAtomsMode but the vars are used in the superclass selectMode
    # 
    bc_in_use = None # None, or a BorrowerChunk in use for the current drag,
            # which should be drawn while in use, and demolished when the drag is done (without fail!) #####@@@@@ need failsafe
    _reusable_borrowerchunks = [] # a freelist of empty BorrowerChunks not now being used (a class variable, not instance variable)

    def allocate_empty_borrowerchunk(self):
        "Someone wants a BorrowerChunk; allocate one from our freelist or a new one"
        while self._reusable_borrowerchunks:
            # try to use one from this list
            bc = self._reusable_borrowerchunks.pop()
            if bc.assy is self.o.assy:
                # bc is still suitable for reuse
                return bc
            else:
                # it's not
                bc.destroy()
                continue
            pass
        # list is empty, just return a new one
        from chunk import BorrowerChunk
        return BorrowerChunk(self.o.assy)

    def deallocate_borrowerchunk(self, bc):
        bc.demolish() # so it stores nothing now, but can be reused later; repeated calls must be ok
        self._reusable_borrowerchunks.append(bc)

    maybe_use_bc = False # precaution
    
    def drag_selected_atoms(self, offset):

        if self.maybe_use_bc and self.dragatoms and self.bc_in_use is None:
            #bruce 060414 move selatoms optimization (unfinished); as of 060414 this never happens unless you set a debug_pref.
            # See long comment above for more info.
            bc = self.allocate_empty_borrowerchunk()
            self.bc_in_use = bc
            other_chunks, other_atoms = bc.take_atoms_from_list( self.dragatoms )
            self.dragatoms = other_atoms # usually []
            self.dragchunks.extend(other_chunks) # usually []
            self.dragchunks.append(bc)
        
        # Move dragatoms.
        for at in self.dragatoms: #bruce 060315 optimization: remove unneeded [:] from both loops
            at.setposn(at.posn()+offset)
        
        # Move baggage.
        for at in self.baggage:
            at.setposn(at.posn()+offset)

        # Move chunks. [bruce 060410 new feature, for optimizing moving of selected atoms, re bugs 1828 / 1438]
        # Note, these might be chunks containing selected atoms (and no unselected atoms, except baggage), not selected chunks.
        # All that matters is that we want to move them as a whole (as an optimization of moving their atoms individually).
        # Note, as of 060414 one of them might be a BorrowerChunk.
        for ch in self.dragchunks:
            ch.move(offset)
        
        return

    def deallocate_bc_in_use(self):
        """If self.bc_in_use is not None, it's a BorrowerChunk and we need to deallocate it --
         this must be called at the end of any drag which might have allocated it.
         """
        if self.bc_in_use is not None:
            self.deallocate_borrowerchunk( self.bc_in_use )
            self.bc_in_use = None
        return
        
    def atomDragUpdate(self, a, apos0):
        '''Updates the GLPane and status bar message when dragging atom <a> around.
        <apos0> is the previous x,y,z position of <a>.
        '''
        apos1 = a.posn()
        if apos1 - apos0:
            from debug_prefs import debug_pref, Choice_boolean_True
            if debug_pref("show drag coords continuously", #bruce 060316 made this optional, to see if it causes lagging drags of C
                          Choice_boolean_True, non_debug = True, # non_debug needed for testing, for now
                          prefs_key = "A7/Show Continuous Drag Coordinates"):
                msg = "dragged atom %r to %s" % (a, self.posn_str(a))
                this_drag_id = (self.current_obj_start, self.__class__.leftDrag)
                env.history.message(msg, transient_id = this_drag_id)
            self.current_obj_clicked = False # atom was dragged. mark 060125.
            self.o.gl_update()

    #bruce 060316 moved dragto from here (selectMode) into class basicMode
    
    def atomLeftUp(self, a, event): # Was atomClicked(). mark 060220.
        '''Real atom <a> was clicked, so select, unselect or delete it based on the current modkey.
        - If no modkey is pressed, clear the selection and pick atom <a>.
        - If Shift is pressed, pick <a>, adding it to the current selection.
        - If Ctrl is pressed,  unpick <a>, removing it from the current selection.
        - If Shift+Control (Delete) is pressed, delete atom <a>.
        '''

        self.deallocate_bc_in_use()
        
        if not self.current_obj_clicked:
            # Atom was dragged.  Nothing to do but return.
            if self.drag_multiple_atoms:
                self.set_cmdname('Move Atoms') #bruce 060412 added plural variant
            else:
                self.set_cmdname('Move Atom')
            ##e note about command names: if jigs were moved too, "Move Selected Objects" might be better... [bruce 060412 comment]
            self.o.assy.changed() # mark 060227
            return
            
        nochange = False
        
        if self.o.modkeys is None:
            # isn't this redundant with the side effects in atomLeftDown?? [bruce 060721 question]
            self.o.assy.unpickall_in_GLPane() # was unpickatoms only; I think unpickall makes more sense [bruce 060721]
            if a.picked:
                nochange = True
                #bruce 060331 comment: nochange = True is wrong, since the unpick might have changed something.
                # For some reason the gl_update occurs anyway, so I don't know if this causes a real bug, so I didn't change it.
            else:
                a.pick()
                self.set_cmdname('Select Atom')
            env.history.message(a.getinfo())

        elif self.o.modkeys == 'Shift':
            if a.picked: 
                nochange = True
            else:
                a.pick()
                self.set_cmdname('Select Atom')
            env.history.message(a.getinfo())
                
        elif self.o.modkeys == 'Control':
            if a.picked:
                a.unpick()
                self.set_cmdname('Unselect Atom') #bruce 060331 comment: I think a better term (in general) would be "Deselect".
                #bruce 060331 bugfix: if filtering prevents the unpick, don't print the message saying we unpicked it.
                # I also fixed the message to not use the internal jargon 'unpicked'.
                # I also added an orangemsg when filtering prevented the unpick, as we have when it prevents a delete.
                if not a.picked:
                    # the unpick worked (was not filtered)
                    env.history.message("Deselected atom %r" % a)
                else:
                    env.history.message(orangemsg("Can't deselect atom %r due to selection filter. Hit Escape to clear the filter." % a))
            else: # Already unpicked.
                nochange = True
            
        elif self.o.modkeys == 'Shift+Control':
            result = self.delete_atom_and_baggage(event)
            env.history.message_no_html(result)
            self.set_cmdname('Delete Atom')
            return # delete_atom_and_baggage() calls win_update.
                
        else:
            print_compact_stack('Invalid modkey = "' + str(self.o.modkeys) + '" ')
            return
            
        if nochange: return
        self.o.gl_update()
        
    def atomLeftDouble(self): # mark 060308
        '''Atom double click event handler for the left mouse button.
        '''
        if self.o.modkeys == 'Control':
            self.o.assy.unselectConnected( [ self.obj_doubleclicked ] )
        elif self.o.modkeys == 'Shift+Control':
            self.o.assy.deleteConnected( self.neighbors_of_last_deleted_atom )
        else:
            self.o.assy.selectConnected( [ self.obj_doubleclicked ] )
        # the assy.xxxConnected routines do their own win_update or gl_update as needed. [bruce 060412 comment]
        ##e set_cmdname would be useful here, conditioned on whether they did anything [bruce 060412 comment]
        return
    
#== End of Atom selection and dragging helper methods

#== Bond selection helper methods

    def bondLeftDown(self, b, event):
        # Bonds cannot be picked when highlighting is turned off.
        self.cursor_over_when_LMB_pressed = 'Bond'
        self.bondSetup(b)

    def bondSetup(self, b):
        '''Setup for a click or double-click event for bond <b>. Bond dragging is not supported.
        '''
        self.objectSetup(b)

    def bondLeftUp(self, b, event):
        '''Bond <b> was clicked, so select or unselect its atoms or delete bond <b> 
        based on the current modkey.
        - If no modkey is pressed, clear the selection and pick <b>'s two atoms.
        - If Shift is pressed, pick <b>'s two atoms, adding them to the current selection.
        - If Ctrl is pressed,  unpick <b>'s two atoms, removing them from the current selection.
        - If Shift+Control (Delete) is pressed, delete bond <b>.
        <event> is a LMB release event.
        '''
            
        #& To do: check if anything changed (picked/unpicked) before calling gl_update(). 
        #& mark 060210.
        if self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane() # was unpickatoms() [bruce 060721]
            b.atom1.pick()
            b.atom2.pick()
            self.set_cmdname('Select Atoms')
                
        elif self.o.modkeys == 'Shift':
            b.atom1.pick()
            b.atom2.pick()
            self.set_cmdname('Select Atoms')
            #& Bond class needs a getinfo() method to be called here. mark 060209.
            
        elif self.o.modkeys == 'Control':
            b.atom1.unpick()
            b.atom2.unpick()
            self.set_cmdname('Unselect Atoms')
            #env.history.message("unpicked %r and %r" % (self.bond_clicked.atom1, self.bond_clicked.atom2))
            #& Not necessary to print history msg.  mark 060210.
            # [It's also wrong to print one, or at least the one above, if selection filter affected both atoms. bruce 060331]
                
        elif self.o.modkeys == 'Shift+Control':
            self.bond_delete(event) 
                # <b> is the bond the cursor was over when the LMB was pressed.
                # use <event> to delete bond <b> to ensure that the cursor is still over it.
            
        else:
            print_compact_stack('Invalid modkey = "' + str(self.o.modkeys) + '" ')
            return
            
        self.o.gl_update()
        
    def bond_delete(self, event):
        '''If the object under the cursor is a bond, delete it.
        '''
        self.update_selatom(event) #bruce 041130 in case no update_selatom happened yet
            # see warnings about update_selatom's delayed effect, in its docstring or in leftDown. [bruce 050705 comment]
        selobj = self.o.selobj # only used if selatom is None
        if isinstance( selobj, Bond) and not selobj.is_open_bond(): #bruce 050727 new feature
            env.history.message_no_html("breaking bond %s" % selobj)
                ###e %r doesn't show bond type, but %s doesn't work in history since it contains "<-->" which looks like HTML.
                ###e Should fix with a utility to quote HTML-active chars, to call here on the message.
            self.o.selobj = None # without this, the bond remains highlighted even after it's broken (visible if it's toolong)
            selobj.bust() # this fails to preserve the bond type on the open bonds -- not sure if that's bad, but probably it is
            self.set_cmdname('Delete Bond')
            self.o.assy.changed() #k needed?
            
            self.w.win_update()
            
    def bondDrag(self, event):
        # If a LMB+Drag event has happened after selecting a bond in left*Down(),
        # do a 2D region selection as if the bond were absent. This takes care of 
        # both Shift and Control mod key cases.
        self.cursor_over_when_LMB_pressed = 'Empty Space'
        self.select_2d_region(self.LMB_press_event)
        self.current_obj_clicked = False
        self.current_obj = None
        return
        
    def bondLeftDouble(self): # mark 060308.
        '''Bond double click event handler for the left mouse button. 
        '''
        if self.o.modkeys == 'Control':
            self.o.assy.unselectConnected( [ self.obj_doubleclicked.atom1 ] )
        elif self.o.modkeys == 'Shift+Control':
            self.o.assy.deleteConnected( [ self.obj_doubleclicked.atom1, self.obj_doubleclicked.atom2 ] )
        else:
            self.o.assy.selectConnected( [ self.obj_doubleclicked.atom1 ] )
        # the assy.xxxConnected routines do their own win_update or gl_update as needed. [bruce 060412 comment]
        return
        
#== End of bond selection helper methods

#== Singlet helper methods

    def singletLeftDown(self, s, event):
        self.cursor_over_when_LMB_pressed = 'Empty Space'
        self.select_2d_region(event)
        self.o.gl_update()
        return
    
    def singletSetup(self, s):
        pass
        
    def singletDrag(self, event):
        pass
        
    def singletLeftUp(self, s, event):
        pass
        
    def singletLeftDouble(self):
        '''Singlet double click event handler for the left mouse button.
        '''
        pass
        
#== Jig event handler helper methods

    def jigLeftDown(self, j, event):
        
        if not j.picked and self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane() # was unpickatoms, unpickparts [bruce 060721]
            j.pick()
        if not j.picked and self.o.modkeys == 'Shift':
            j.pick()
        if j.picked:
            self.cursor_over_when_LMB_pressed = 'Picked Jig'
        else:
            self.cursor_over_when_LMB_pressed = 'Unpicked Jig'
            
        # Move section
        farQ_junk, self.jig_MovePt = self.dragstart_using_GL_DEPTH( event)
            #bruce 060316 replaced equivalent old code with this new method

        self.jig_StartPt = self.jig_MovePt # Used in leftDrag() to compute move offset during drag op.
        
        self.jigSetup(j)
        
        
    def jigSetup(self, j):
        '''Setup for a click, double-click or drag event for jig <j>.
        '''
        self.objectSetup(j)
        
        self.dragatoms, self.baggage, self.dragchunks = self.get_dragatoms_and_baggage()
            # if no atoms are selected, dragatoms and baggage are empty lists, which is good.
            
        # dragjigs contains all the selected jigs.
        self.dragjigs = self.o.assy.getSelectedJigs()
        
    def jigDrag(self, j, event):
        """Drag jig <j> and any other selected jigs or atoms.  <event> is a drag event.
        """
        #bruce 060316 commented out deltaMouse since it's not used in this routine
##        deltaMouse = V(event.pos().x() - self.o.MousePos[0], self.o.MousePos[1] - event.pos().y(), 0.0)

        jig_NewPt = self.dragto( self.jig_MovePt, event) #bruce 060316 replaced old code with dragto (equivalent)
        
        # Print status bar msg indicating the current move offset.
        if 1:
            self.moveOffset = jig_NewPt - self.jig_StartPt
            msg = "Offset: [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.moveOffset[0], self.moveOffset[1], self.moveOffset[2])
            env.history.statusbar_msg(msg)

        offset = jig_NewPt - self.jig_MovePt
        
        self.drag_selected_atoms(offset)
        self.drag_selected_jigs(offset)
        
        self.jig_MovePt = jig_NewPt
        
        self.current_obj_clicked = False # jig was dragged.
        self.o.gl_update()
        
    def drag_selected_jigs(self, offset):
        for j in self.dragjigs: #bruce 060315 removed unnecessary [:]
            j.move(offset)

    def jigLeftUp(self, j, event):
        '''Jig <j> was clicked, so select, unselect or delete it based on the current modkey.
        - If no modkey is pressed, clear the selection and pick jig <j>.
        - If Shift is pressed, pick <j>, adding it to the current selection.
        - If Ctrl is pressed,  unpick <j>, removing it from the current selection.
        - If Shift+Control (Delete) is pressed, delete jig <j>.
        '''

        self.deallocate_bc_in_use()
        
        if not self.current_obj_clicked:
            # Jig was dragged.  Nothing to do but return.
            self.set_cmdname('Move Jig')
            self.o.assy.changed()
            return
            
        nochange = False
        
        if self.o.modkeys is None:
            # isn't this redundant with jigLeftDown? [bruce 060721 question; btw this method is very similar to atomLeftUp]
            self.o.assy.unpickall_in_GLPane() # was unpickatoms only (but I think unpickall makes more sense) [bruce 060721]
            if j.picked:
                # bruce 060412 fix unreported bug: remove nochange = True, in case atoms were just unpicked
                pass ## nochange = True
            else:
                j.pick()
                self.set_cmdname('Select Jig')

        elif self.o.modkeys == 'Shift':
            if j.picked: 
                nochange = True
            else:
                j.pick()
                self.set_cmdname('Select Jig')
                
        elif self.o.modkeys == 'Control':
            if j.picked:
                j.unpick()
                self.set_cmdname('Unselect Jig')
                env.history.message("Unselected %r" % j.name) #bruce 060412 capitalized text, replaced j -> j.name
                     #bruce 060412 comment: I think a better term (in general) would be "Deselect".
            else: # Already unpicked.
                nochange = True
            
        elif self.o.modkeys == 'Shift+Control':
            env.history.message("Deleted %r" % j.name) #fixed bug 1641. mark 060314. #bruce 060412 revised text
            # Build list of deleted jig's atoms before they are lost.
            self.atoms_of_last_deleted_jig.extend(j.atoms) #bruce 060412 optimized this
##            for a in j.atoms[:]:
##                self.atoms_of_last_deleted_jig.append(a)
            j.kill()
                #bruce 060412 wonders how j.kill() affects the idea of double-clicking this same jig to delete its atoms too,
                # since the jig is gone by the time of the 2nd click. See comments in jigLeftDouble for more info.
            self.set_cmdname('Delete Jig')
            self.w.win_update()
            return
                
        else:
            print_compact_stack('Invalid modkey = "' + str(self.o.modkeys) + '" ')
            return
            
        if nochange: return
        self.o.gl_update()
        
    def jigLeftDouble(self):
        '''Jig <j> was double clicked, so select, unselect or delete its atoms based on the current modkey.
        - If no modkey is pressed, pick the jig's atoms.
        - If Shift is pressed, pick the jig's atoms, adding them to the current selection.
        - If Ctrl is pressed,  unpick the jig's atoms, removing them from the current selection.
        - If Shift+Control (Delete) is pressed, delete the jig's atoms.
        '''
        #bruce 060412 thinks that the jig transdelete feature (delete the jig's atoms on shift-control-dblclick)
        # might be more dangerous than useful:
        # - it might happen on a wireframe jig, like an Anchor, if user intended to transdelete on an atom instead;
        # - it might happen if user intended to delete jig and then delete an atom behind it (epecially since the jig
        #   becomes invisible after the first click), if two intended single clicks were interpreted as a double click;
        # - it seems rarely needed, so it could just as well be in the jig's context menu instead.
        # To mitigate this problem, I'll add a history message saying that it happened.
        # I'll also optimize some loops (by removing [:]) and fix bug 1816 (missing update).
        if self.o.modkeys == 'Control':
            for a in self.obj_doubleclicked.atoms:
                a.unpick()
        elif self.o.modkeys == 'Shift+Control':
            #bruce 060418 rewrote this, to fix bug 1816 and do other improvements
            # (though I think it should be removed, as explained above)
            atoms = self.atoms_of_last_deleted_jig # a list of atoms
            self.atoms_of_last_deleted_jig = [] # for safety
            if atoms:
                self.set_cmdname("Delete Jig's Atoms")
                    #bruce 060412. Should it be something else? 'Delete Atoms', 'Delete Atoms of Jig', "Delete Jig's Atoms"
                    # Note, this presently ends up as a separate operation in the
                    # Undo stack from the first click deleting the jig, but in the future these ops might be merged in the Undo stack,
                    # and if they are, this command name should be changed to cover deleting both the jig and its atoms.
                env.history.message("Deleted jig's %d atoms" % len(atoms))
                    # needed since this could be done by accident, and in some cases could go unnoticed
                    # (count could be wrong if jig.kill() already killed some of the atoms for some reason; probably never happens)
                self.w.win_update() # fix bug 1816
                for a in atoms:
                    a.kill() ##e could be optimized using prekill
        else:
            for a in self.obj_doubleclicked.atoms:
                a.pick()
        self.o.gl_update() #bruce 060412 fix some possible unreported bugs
        return
        
#== End of singlet helper methods

    def mouse_within_stickiness_limit(self, event, drag_stickiness_limit_pixels): #bruce 060315 reimplemented this
        """Check if mouse has never been dragged beyond <drag_stickiness_limit_pixels>
        while holding down the LMB (left mouse button) during the present drag.
        Return True if it's never exceeded this distance from its starting point, False if it has.
        Distance is measured in pixels.
           Successive calls need not pass the same value of the limit.
        """
        try:
            xy_orig = self.LMB_press_pt_xy
        except:
            # This can happen when leftDown was never called before leftDrag (there's a reported traceback bug about it,
            #  an AttributeError about LMB_press_pt, which this attr replaces).
            # In that case pretend the mouse never moves outside the limit during this drag.
            return True
        # this would be an incorrect optimization:
        ## if self.max_dragdist_pixels > drag_stickiness_limit_pixels:
        ##     return False # optimization -- but incorrect, in case future callers plan to pass a larger limit!!
        xy_now = (event.pos().x(), event.pos().y()) # must be in same coordinates as self.LMB_press_pt_xy in leftDown
        dist = vlen(A(xy_orig) - A(xy_now)) #e could be optimized (e.g. store square of dist), probably doesn't matter
        self.max_dragdist_pixels = max( self.max_dragdist_pixels, dist)
        return self.max_dragdist_pixels <= drag_stickiness_limit_pixels
            
    def set_hoverHighlighting(self, on):
        '''Turn hover highlighting on/off.
        if <on> is True, atoms and bonds are highlighted as the cursor passes over them.
        if <on> is False, atoms are not highlighted until they are selected (with LMB click).
        Bonds are not highlighted either, but they cannot be selected when highlighting is turned off.
        '''
        self.hover_highlighting_enabled = on
        if on:
            msg = "Highlighting turned on."
        else:
            msg = "Highlighting turned off."
        env.history.message(msg)
    
    def get_jig_under_cursor(self, event):
        """Use the OpenGL picking/selection to select any jigs. Restore the projection and modelview
           matrices before returning.
        """
        ####@@@@ WARNING: The original code for this, in GLPane, has been duplicated and slightly modified
        # in at least three other places (search for glRenderMode to find them). This is bad; common code
        # should be used. Furthermore, I suspect it's sometimes needlessly called more than once per frame;
        # that should be fixed too. [bruce 060721 comment]
        
        if not self.o.jigSelectionEnabled:
            return None
        
        from constants import GL_FAR_Z
        
        wX = event.pos().x()
        wY = self.o.height - event.pos().y()
        
        aspect = float(self.o.width)/self.o.height
                
        gz = self._calibrateZ(wX, wY)
        if gz >= GL_FAR_Z:  # Empty space was clicked--This may not be true for translucent face [Huaicai 10/5/05]
            return None  
        
        pxyz = A(gluUnProject(wX, wY, gz))
        pn = self.o.out
        pxyz -= 0.0002*pn
        dp = - dot(pxyz, pn)
        
        # Save project matrix before it's changed
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        
        current_glselect = (wX,wY,3,3) 
        self.o._setup_projection( aspect, self.o.vdist, glselect = current_glselect) 
        
        glSelectBuffer(self.o.glselectBufferSize)
        glRenderMode(GL_SELECT)
        glInitNames()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()  ## Save model/view matrix before it's changed
        try:
            glClipPlane(GL_CLIP_PLANE0, (pn[0], pn[1], pn[2], dp))
            glEnable(GL_CLIP_PLANE0)
            self.o.assy.draw(self.o)
            self.Draw_after_highlighting(pickCheckOnly=True)
            glDisable(GL_CLIP_PLANE0)
        except:
            # Restore Model view matrix, select mode to render mode 
            glPopMatrix()
            glRenderMode(GL_RENDER)
            print_compact_traceback("exception in mode.Draw() during GL_SELECT; ignored; restoring modelview matrix: ")
        else: 
            # Restore Model view matrix
            glPopMatrix() 
    
        #Restore project matrix and set matrix mode to Model/View
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glFlush()
        
        hit_records = list(glRenderMode(GL_RENDER))
        if platform.atom_debug and 0:
            print "%d hits" % len(hit_records)
        for (near,far,names) in hit_records: # see example code, renderpass.py
            if platform.atom_debug and 0:
                print "hit record: near,far,names:",near,far,names
                # e.g. hit record: near,far,names: 1439181696 1453030144 (1638426L,)
                # which proves that near/far are too far apart to give actual depth,
                # in spite of the 1-pixel drawing window (presumably they're vertices
                # taken from unclipped primitives, not clipped ones).
            if 1:
                # partial workaround for bug 1527. This can be removed once that bug (in drawer.py)
                # is properly fixed. This exists in two places -- GLPane.py and modes.py. [bruce 060217]
                if names and names[-1] == 0:
                    print "%d(m) partial workaround for bug 1527: removing 0 from end of namestack:" % env.redraw_counter, names
                    names = names[:-1]
##                    if names:
##                        print " new last element maps to %r" % env.obj_with_glselect_name.get(names[-1])
            if names:
                obj = env.obj_with_glselect_name.get(names[-1]) #k should always return an obj
                #self.glselect_dict[id(obj)] = obj # now these can be rerendered specially, at the end of mode.Draw
                if isinstance(obj, Jig):
                    return obj
        return None # from get_jig_under_cursor
                
    def Draw(self):
        if 1:
            # wware 060124  Embed Pyrex/OpenGL unit tests into the cad code
            # grantham 060207:
            # Set to 1 to see a small array of eight spheres.
            # Set to 2 to see the Large-Bearing model, but this is most effective if
            #  the Large-Bearing has already been loaded normally into rotate mode
            #bruce 060209 set this from a debug_pref menu item, not a hardcoded flag
            from debug_prefs import debug_pref, Choice
            TEST_PYREX_OPENGL = debug_pref("TEST_PYREX_OPENGL", Choice([0,1,2]))
            # uncomment this line to set it in the old way:
            ## TEST_PYREX_OPENGL = 1
        if TEST_PYREX_OPENGL:
            try:
                #self.w.win_update()
                sys.path.append("./experimental/pyrex-opengl")
                binPath = os.path.normpath(os.path.dirname(os.path.abspath(sys.argv[0])) + '/../bin')
                if binPath not in sys.path:
                    sys.path.append(binPath)
                import quux
                if "experimental" in dirname(sys.modules['quux'].__file__):
                    print "WARNING: Using experimental version of quux module"
                # quux.test()
                quux.shapeRendererInit()
                quux.shapeRendererSetUseDynamicLOD(0)
                quux.shapeRendererStartDrawing()
                if TEST_PYREX_OPENGL == 1:
                    center = Numeric.array((Numeric.array((0, 0, 0), 'f'),
                                            Numeric.array((0, 0, 1), 'f'),
                                            Numeric.array((0, 1, 0), 'f'),
                                            Numeric.array((0, 1, 1), 'f'),
                                            Numeric.array((1, 0, 0), 'f'),
                                            Numeric.array((1, 0, 1), 'f'),
                                            Numeric.array((1, 1, 0), 'f'),
                                            Numeric.array((1, 1, 1), 'f')), 'f')
                    radius = Numeric.array((0.2, 0.4, 0.6, 0.8,
                                            1.2, 1.4, 1.6, 1.8), 'f')
                    color = Numeric.array((Numeric.array((0, 0, 0, 0.5), 'f'),
                                           Numeric.array((0, 0, 1, 0.5), 'f'),
                                           Numeric.array((0, 1, 0, 0.5), 'f'),
                                           Numeric.array((0, 1, 1, 0.5), 'f'),
                                           Numeric.array((1, 0, 0, 0.5), 'f'),
                                           Numeric.array((1, 0, 1, 0.5), 'f'),
                                           Numeric.array((1, 1, 0, 0.5), 'f'),
                                           Numeric.array((1, 1, 1, 0.5), 'f')), 'f')
                    result = quux.shapeRendererDrawSpheres(8, center, radius, color)
                elif TEST_PYREX_OPENGL == 2:
                    # grantham - I'm pretty sure the actual compilation, init, etc happens once
                    from bearing_data import sphereCenters, sphereRadii
                    from bearing_data import sphereColors, cylinderPos1
                    from bearing_data import cylinderPos2, cylinderRadii
                    from bearing_data import cylinderCapped, cylinderColors
                    glPushMatrix()
                    glTranslate(-0.001500, -0.000501, 151.873627)
                    result = quux.shapeRendererDrawSpheres(1848, sphereCenters, sphereRadii, sphereColors)
                    result = quux.shapeRendererDrawCylinders(5290, cylinderPos1, cylinderPos2, cylinderRadii, cylinderCapped, cylinderColors)
                    glPopMatrix()
                quux.shapeRendererFinishDrawing()

            except ImportError:
                env.history.message(redmsg("Can't import Pyrex OpenGL or maybe bearing_data.py, rebuild it"))
        else:
            if self.bc_in_use is not None: #bruce 060414
                self.bc_in_use.draw(self.o, 'fake dispdef kluge')
            # bruce comment 040922: code is almost identical with modifyMode.Draw;
            # the difference (no check for self.o.assy existing) might be a bug in this version, or might have no effect.
            basicMode.Draw(self)   
            #self.griddraw()
            if self.selCurve_List: self.draw_selection_curve()
            self.o.assy.draw(self.o)

    # update_selatom_and_selobj() moved here from depositMode.py  mark 060312.
    def update_selatom_and_selobj(self, event = None): #bruce 050705
        """update_selatom (or cause this to happen with next paintGL);
        return consistent pair (selatom, selobj);
        atom_debug warning if inconsistent
        """
        #e should either use this more widely, or do it in selatom itself, or convert entirely to using only selobj.
        self.update_selatom( event) # bruce 050612 added this -- not needed before since bareMotion did it (I guess).
            ##e It might be better to let set_selobj callback (NIM, but needed for sbar messages) keep it updated.
            #
            # See warnings about update_selatom's delayed effect, in its docstring or in leftDown. [bruce 050705 comment]
        selatom = self.o.selatom
        selobj = self.o.selobj #bruce 050705 -- #e it might be better to use selobj alone (selatom should be derived from it)
        if selatom is not None:
            if selobj is not selatom:
                if platform.atom_debug:
                    print "atom_debug: selobj %r not consistent with selatom %r -- using selobj = selatom" % (selobj, selatom)
                selobj = selatom # just for our return value, not changed in GLPane (self.o)
        else:
            pass #e could check that selobj is reflected in selatom if an atom, but might as well let update_selatom do that,
                # esp. since it behaves differently for singlets
        return selatom, selobj
        
    call_makeMenus_for_each_event = True #mark 060312

    def makeMenus(self): # menu item names modified by bruce 041217
    
        selatom, selobj = self.update_selatom_and_selobj( None)
        
        self.Menu_spec = []
        
        # Local minimize [now called Adjust Atoms in history/Undo, Adjust <what> here and in selectMode -- mark & bruce 060705]
        # WARNING: This code is duplicated in depositMode.makeMenus(). mark 060314.
        if selatom is not None and not selatom.is_singlet() and self.w.simSetupAction.isEnabled():
            # see comments in depositMode version
            self.Menu_spec.append(( 'Adjust atom %s' % selatom, lambda e1=None,a=selatom: self.localmin(a,0) ))
            self.Menu_spec.append(( 'Adjust 1 layer', lambda e1=None,a=selatom: self.localmin(a,1) ))
            self.Menu_spec.append(( 'Adjust 2 layers', lambda e1=None,a=selatom: self.localmin(a,2) ))
            
        # selobj-specific menu items. [revised by bruce 060405; for more info see the same code in depositMode]
        if selobj is not None and hasattr(selobj, 'make_selobj_cmenu_items'):
            try:
                selobj.make_selobj_cmenu_items(self.Menu_spec)
            except:
                print_compact_traceback("bug: exception (ignored) in make_selobj_cmenu_items for %r: " % selobj)
        
        # separator and other mode menu items.
        if self.Menu_spec:
            self.Menu_spec.append(None)
        
        # Enable/Disable Jig Selection.
        # This is duplicated in depositMode.makeMenus() and selectMolsMode.makeMenus().
        if self.o.jigSelectionEnabled:
            self.Menu_spec.extend( [('Enable Jig Selection',  self.toggleJigSelection, 'checked')])
        else:
            self.Menu_spec.extend( [('Enable Jig Selection',  self.toggleJigSelection, 'unchecked')])
            
        self.Menu_spec.extend( [
            # mark 060303. added the following:
            None,
            ('Change Background Color...', self.w.dispBGColor),
            ])
            
        return # from makeMenus
        
    def toggleJigSelection(self):
        self.o.jigSelectionEnabled = not self.o.jigSelectionEnabled
    
    # localmin moved here from depositMode. mark 060314.
    # Local minimize [now called Adjust Atoms in history/Undo, Adjust <what> in menu commands -- mark & bruce 060705]
    def localmin(self, atom, nlayers): #bruce 051207 #e might generalize to take a list or pair of atoms, other options
        if platform.atom_debug:
            print "debug: reloading runSim on each use, for development [localmin %s, %d]" % (atom, nlayers)
            import runSim, debug
            debug.reload_once_per_event(runSim) #bruce 060705 revised this
        if 1:
            # this does not work, I don't know why, should fix sometime: [bruce 060705]
            self.set_cmdname("Adjust Atoms") # for Undo (should we be more specific, like the menu text was? why didn't that get used?)
        from runSim import LocalMinimize_function
        LocalMinimize_function( [atom], nlayers )
        return

    pass # end of class selectMode

# ==

class selectMolsMode(selectMode):
    "Select Chunks mode"
    modename = 'SELECTMOLS'
    default_mode_status_text = "Mode: Select Chunks"
    
    def Enter(self): 
        basicMode.Enter(self)
        self.o.assy.selectChunksWithSelAtoms_noupdate() # josh 10/7 to avoid race in assy init
            
    def init_gui(self):
        selectMode.init_gui(self)
        self.w.toolsSelectMoleculesAction.setOn(1) # toggle on the "Select Chunks" tools icon
        self.w.selectMolDashboard.show()
            
    def restore_gui(self):
        self.w.selectMolDashboard.hide()
        
    def leftDouble(self, event):
        '''Switch to Move Chunks Mode.  This will go away in A8. mark 060303.
        '''
        # Current plans are to merge Select Chunks and Move Chunks modes in A8.
        self.o.setMode('MODIFY')
        return
        
    def keyPress(self,key):
        '''keypress event handler for selectMolsMode.
        '''
        basicMode.keyPress(self, key)
                
    def keyRelease(self,key):
        '''keyrelease event handler for selectMolsMode.
        '''
        basicMode.keyRelease(self, key)
        
    def update_cursor_for_no_MB(self):
        '''Update the cursor for 'Select Chunks' mode (selectMolsMode).
        '''
        
        #print "selectMolsMode.update_cursor_for_no_MB(): button=",self.o.button
        
        if self.o.modkeys is None:
            self.o.setCursor(self.w.SelectMolsCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.SelectMolsAddCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.SelectMolsSubtractCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB(): Invalid modkey=", self.o.modkeys
        return
                
    def rightShiftDown(self, event):
        basicMode.rightShiftDown(self, event)
           
    def rightCntlDown(self, event):          
        basicMode.rightCntlDown(self, event)
    
    # moved here from modifyMode.  mark 060303.
    call_makeMenus_for_each_event = True #bruce 050914 enable dynamic context menus [fixes an unreported bug analogous to 971]
    
    # moved here from modifyMode.  mark 060303.
    def makeMenus(self): # mark 060303.
    
        self.Menu_spec = []
        
        if self.o.assy.selmols:
            # Menu items added when there are selected chunks.
            self.Menu_spec = [
                ('Change Color of Selected Chunks...', self.w.dispObjectColor),
                ('Reset Color of Selected Chunks', self.w.dispResetChunkColor),
                ('Reset Atoms Display of Selected Chunks', self.w.dispResetAtomsDisplay),
                ('Show Invisible Atoms of Selected Chunks', self.w.dispShowInvisAtoms),
                ('Hide Selected Chunks', self.o.assy.Hide),
            ]
        
        # Enable/Disable Jig Selection.
        # This is duplicated in selectMode.makeMenus() and depositMode.makeMenus().
        if self.o.jigSelectionEnabled:
            self.Menu_spec.extend( [('Enable Jig Selection',  self.toggleJigSelection, 'checked')])
        else:
            self.Menu_spec.extend( [('Enable Jig Selection',  self.toggleJigSelection, 'unchecked')])
            
        self.Menu_spec.extend( [
            # mark 060303. added the following:
            None,
            ('Change Background Color...', self.w.dispBGColor),
            ])

        self.debug_Menu_spec = [
            ('debug: invalidate selection', self.invalidate_selection),
            ('debug: update selection', self.update_selection),
         ]
    
    # moved here from modifyMode.  mark 060303.
    def invalidate_selection(self): #bruce 041115 (debugging method)
        "[debugging method] invalidate all aspects of selected atoms or mols"
        for mol in self.o.assy.selmols:
            print "already valid in mol %r: %r" % (mol, mol.invalid_attrs())
            mol.invalidate_everything()
        for atm in self.o.assy.selatoms.values():
            atm.invalidate_everything()
    
    # moved here from modifyMode.  mark 060303.
    def update_selection(self): #bruce 041115 (debugging method)
        """[debugging method] update all aspects of selected atoms or mols;
        no effect expected unless you invalidate them first
        """
        for atm in self.o.assy.selatoms.values():
            atm.update_everything()
        for mol in self.o.assy.selmols:
            mol.update_everything()
        return

    pass # end of class selectMolsMode

# ==

class selectAtomsMode(selectMode):
    modename = 'SELECTATOMS'
    default_mode_status_text = "Mode: Select Atoms"
    highlight_singlets = False 
        # Don't highlight singlets in selectAtomsMode. Fixes bug 1540. mark 060220.
    water_enabled = False # Fixes bug 1583. mark 060301.
        
    eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]
        
    def __init__(self, glpane):
        selectMode.__init__(self, glpane)
            
    def Enter(self): 
        basicMode.Enter(self)
        
        self.o.assy.permit_pick_atoms()
        self.w.win_update() #k needed? I doubt it, I bet caller of Enter does it [bruce comment 050517, moved here 060721]
        
        self.set_selection_filter(0) # disable selection filter (sets current item to "All Elements").  mark 060301.
        # Reinitialize previously picked atoms (ppas).
        self.o.assy.ppa2 = self.o.assy.ppa3 = None
        
        self.o.selatom = None
        self.reset_drag_vars()
        self.dont_update_gui = True # until changed in init_gui
        self.ignore_next_leftUp_event = False
            # Set to True in leftDouble() and checked by the left*Up() event handlers
            # to determine whether they should ignore the (second) left*Up event
            # generated by the second LMB up/release event in a double click.
            
    def reset_drag_vars(self):
        #bruce 041124 split this out of Enter; as of 041130,
        # required bits of it are inlined into Down methods as bugfixes
        set_DRAG_STICKINESS_LIMIT_from_pref()
        self.cursor_over_when_LMB_pressed = None
            # <cursor_over_when_LMB_pressed> keeps track of what the cursor was over 
            # when the LMB was pressed, which can be one of:
            #   'Empty Space'
            #   'Picked Atom'
            #   'Unpicked Atom'
            #   'Singlet'
            #   'Bond'
            # [later note: it is only used to compare to 'Empty Space';
            #  self.current_obj and other state variables are used instead of
            #  checking for the other values; I don't know if the other values
            #  are always correct. bruce 060721 comment]
        self.drag_multiple_atoms = False
            # set to True when we are dragging a movable unit of 2 or more atoms.
        self.maybe_use_bc = False # whether to use the BorrowerChunk optimization for the current drag (experimental) [bruce 060414]
        self.current_obj = None
            # current_obj is the object under the cursor when the LMB was pressed.
        self.dragatoms = []
            # dragatoms is constructed in get_dragatoms_and_baggage() and contains all 
            # the selected atoms (except selected baggage atoms) that are dragged around
            # as part of the current selection in drag_selected_atoms().
            # Selected atoms that are baggage are placed in self.baggage
            # along with non-selected baggage atoms connected to dragatoms.
            # See atomSetup() for more information.
            #bruce 060410 note: self.dragatoms is only set along with self.baggage,
            # and the atoms in these lists are only moved together (in all cases involving self.dragatoms,
            #  though not in all cases involving self.baggage),
            # so it doesn't matter which atoms are in which lists (in those cases),
            # and probably the code should be revised to use only the self.dragatoms list (in those cases).
            #bruce 060410 optimization and change: when all atoms in existing chunks are being dragged
            # (or if new chunks could be temporarily and transparently made for which all their atoms were being dragged),
            # then we can take advantage of chunk display lists to get a big speedup in dragging the atoms.
            # We do this by listing such chunks in self.dragchunks and excluding their atoms from self.dragatoms
            # and self.baggage.
        self.dragchunks = []
        self.dragjigs = []
            # dragjigs is constructed in jigSetup() and contains all the selected jigs that 
            # are dragged around as part of the current selection in jigDrag().
            # See jigSetup() for more information.
        self.baggage = []
            # baggage contains singlets and/or monovalent atoms (i.e. H, O(sp2), F, Cl, Br)
            # which are connected to a dragged atom and get dragged around with it.
            # Also, no atom which has baggage can also be baggage.
        self.nonbaggage = []
            # nonbaggage contains atoms which are bonded to a dragged atom but 
            # are not dragged around with it. Their own baggage atoms are moved when a 
            # single atom is dragged in atomDrag().
        self.current_obj_clicked = False 
            # current_obj_clicked is used to determine if a lit up atom, singlet or bond was picked (clicked)
            # or not picked (dragged). It must be set to False here so that a newly 
            # deposited atom doesn't pick itself right away (although now this is the default behavior).
            # current_obj_clicked is set to True in *LeftDown() before it gets dragged (if it does at all).
            # If it is dragged, it is set to False in *LeftDrag().
            # *LeftUp() checks it to determine whether the object gets picked or not. mark 060125.
        self.obj_doubleclicked = None
            # used by leftDouble() to determine the object that was double clicked.
        #bruce 060315 replaced drag_stickiness_limit_exceeded with max_dragdist_pixels
        self.max_dragdist_pixels = 0
            # used in mouse_within_stickiness_limit
        self.drag_offset = V(0,0,0) #bruce 060316
            # default value of offset from object reference point (e.g. atom center) to dragpoint (used by some drag methods)
        self.only_highlight_singlets = False
            # when set to True, only singlets get highlighted when dragging a singlet.
            # depositMode.singletSetup() sets this to True when dragging a singlet around.
        self.neighbors_of_last_deleted_atom = []
            # list of the real atom neighbors connected to a deleted atom.  Used by atomLeftDouble()
            # to find the connected atoms to a recently deleted atom when double clicking with 'Shift+Control'
            # modifier keys pressed together.
        self.atoms_of_last_deleted_jig = []
            # list of the real atoms connected to a deleted jig.  Used by jigLeftDouble()
            # to retreive the atoms of a recently deleted jig when double clicking with 'Shift+Control'
            # modifier keys pressed together.
            
    def init_gui(self):
        selectMode.init_gui(self)
        self.w.toolsSelectAtomsAction.setOn(1) # toggle on the "Select Atoms" tools icon
        # Do this before connecting signals or we'll get a history msg.  Part of fix for bug 1620. mark 060322
        self.w.selectAtomsDashboard.highlightingCB.setChecked(self.hover_highlighting_enabled)
        self.connect_or_disconnect_signals(True)
        self.update_hybridComboBox(self.w)
        self.w.selectAtomsDashboard.show()
        
    def connect_or_disconnect_signals(self, connect):
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
        
        change_connect(self.w.selectAtomsDashboard.highlightingCB,
                        SIGNAL("toggled(bool)"),self.set_hoverHighlighting)
        change_connect(self.w.transmuteButton,
                        SIGNAL("clicked()"),self.transmutePressed)
        change_connect(self.w.elemFilterComboBox,
                        SIGNAL("activated(int)"), self.set_selection_filter)

    def restore_gui(self):
        # disconnect signals which were connected in init_gui [bruce 050728]
        self.connect_or_disconnect_signals(False)
        #self.w.disconnect(self.w.transmuteButton, SIGNAL("clicked()"), self.transmutePressed)
        self.w.selectAtomsDashboard.hide()
            
    def bareMotion(self, event): #bruce 050610 revised this
        """called for motion with no button down
        [should not be called otherwise -- call update_selatom or update_selobj directly instead]
        """
        self.update_selobj(event)
        # note: this routine no longer updates glpane.selatom. For that see self.update_selatom().

    def get_obj_under_cursor(self, event):
        '''Return the object under the cursor.  Only atoms, singlets and bonds are returned.
        Returns None for all other cases, including when a bond, jig or nothing is under the cursor.
        ''' #bruce 060331 comment: this docstring appears wrong, since the code looks like it can return jigs.
        
        if self.hover_highlighting_enabled:
            self.update_selatom(event) #bruce 041130 in case no update_selatom happened yet
            # update_selatom() updates self.o.selatom and self.o.selobj.
            # self.o.selatom is either a real atom or a singlet [or None].
            # self.o.selobj can be a bond, and is used in leftUp() to determine if a bond was selected.
            
        # Warning: if there was no GLPane repaint event (i.e. paintGL call) since the last bareMotion,
        # update_selatom can't make selobj/selatom correct until the next time paintGL runs.
        # Therefore, the present value might be out of date -- but it does correspond to whatever
        # highlighting is on the screen, so whatever it is should not be a surprise to the user,
        # so this is not too bad -- the user should wait for the highlighting to catch up to the mouse
        # motion before pressing the mouse. [bruce 050705 comment]
        
            obj = self.o.selatom # a "highlighted" atom or singlet
            
            if obj is None and self.o.selobj:
                obj = self.o.selobj # a "highlighted" bond
                if not isinstance(obj, Bond) and env.debug():
                    print "debug fyi: not isinstance(obj, Bond) in get_obj_under_cursor, for %r" % (obj,)
                        # I suspect some jigs can occur here
                        # (and if not, we should put them here -- I know of no excuse for jig highlighting
                        #  to work differently than for anything else) [bruce 060721] 
            
            if obj is None: # a "highlighted" jig
                obj = self.get_jig_under_cursor(event)
                if env.debug():
                    print "debug fyi: get_jig_under_cursor returns %r" % (obj,) # [bruce 060721] 
            pass
            
        else: # No hover highlighting
            obj = self.o.assy.findAtomUnderMouse(event, self.water_enabled, singlet_ok = True)
            # Note: findAtomUnderMouse() only returns atoms and singlets, not bonds or jigs.
            # This means that bonds can never be selected when highlighting is turned off.
            # [What about jigs? bruce question 060721]
        return obj
            
    def get_real_atom_under_cursor(self, event):
        '''If the object under the cursor is a real atom, return it.  Otherwise, return None.
        '''
        obj = self.get_obj_under_cursor(event)
        if isinstance(obj, Atom):
            if not obj.is_singlet():
                return obj
        return None

    def bond_type_changer_is_active(self): #bruce 060702
        "[subclasses can override this; see depositMode implem for docstring]"
        return False
        
    def selobj_highlight_color(self, selobj): #bruce 050612 added this to mode API
        """[mode API method]
        If we'd like this selobj to be highlighted on mouseover
        (whenever it's stored in glpane.selobj), return the desired highlight color.
        If we'd prefer it not be highlighted (though it will still be stored
        in glpane.selobj and prevent any other objs it obscures from being stored there
        or highlighted), return None. (Warning: exceptions are ignored and cause the
        default highlight color to be used. #e should clean that up sometime)
        """
        if not self.hover_highlighting_enabled:
            return None
        
        if isinstance(selobj, Atom):
            if selobj.is_singlet():
                if self.highlight_singlets: # added highlight_singlets to fix bug 1540. mark 060220.
                    likebond = self.bond_type_changer_is_active() #bruce 060702 part of fixing bug 833 item 1
                    if likebond:
                        # clicks in this tool-state modify the bond, not the bondpoint, so let the color hint at that
                        return env.prefs[bondHighlightColor_prefs_key]
                    else:
                        return env.prefs[bondpointHighlightColor_prefs_key]
                else:
                    return None
            else:
                if self.only_highlight_singlets: # True only when dragging a bondpoint (in Build mode).
                    # Highlight this atom if it has bondpoints.
                    if selobj.singNeighbors():
                        if self.current_obj in selobj.singNeighbors(): 
                            # Do not highlight the atom that the current singlet belongs to.
                            # Fixes bug 1522. mark 060301.
                            return None
                        return env.prefs[atomHighlightColor_prefs_key]
                    else:
                        return None
                if self.o.modkeys == 'Shift+Control':
                    return darkred  
                        # Highlight the atom in darkred if the control key is pressed and it is not picked.
                        # The delete_mode color should be a user pref.  Wait until A8, though.  mark 060129.
                else:
                    return env.prefs[atomHighlightColor_prefs_key] ## was HICOLOR_real_atom before bruce 050805
        elif isinstance(selobj, Bond):
            #bruce 050822 experiment: debug_pref to control whether to highlight bonds
            # (when False they'll still obscure other things -- need to see if this works for Mark ####@@@@)
            # ###@@@ PROBLEM with this implem: they still have a cmenu and can be deleted by cmd-del (since still in selobj);
            # how would we *completely* turn this off? Need to see how GLPane decides whether a drawn thing is highlightable --
            # maybe just by whether it can draw_with_abs_coords? Maybe by whether it has a glname (not toggleable instantly)?
            # ... now i've modified GLPane to probably fix that...
            from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
            highlight_bonds = debug_pref("highlight bonds", Choice_boolean_True)
            if not highlight_bonds:
                return None
            ###@@@ use checkbox to control this; when false, return None
            if selobj.atom1.is_singlet() or selobj.atom2.is_singlet():
                # note: HICOLOR_singlet_bond is no longer used, since singlet-bond is part of singlet for selobj purposes [bruce 050708]
                print "Error: HICOLOR_singlet_bond no longer used"  # This can be removed soon. mark 060215.
                return None # precaution.  
            else:
                if self.only_highlight_singlets:
                    return None
                if self.o.modkeys == 'Shift+Control': 
                    return darkred
                else:
                    return env.prefs[bondHighlightColor_prefs_key] ## was HICOLOR_real_bond before bruce 050805
        elif isinstance(selobj, Jig): #bruce 050729 bugfix (for some bugs caused by Huaicai's jig-selection code)
            if not self.o.jigSelectionEnabled: #mark 060312.
                # jigSelectionEnabled set from GLPane context menu.
                return None
            if self.o.modkeys == 'Shift+Control': 
                return darkred
            else:
                return env.prefs[bondHighlightColor_prefs_key]
        else:
            print "unexpected selobj class in depmode.selobj_highlight_color:", selobj
            return blue
            
    def update_selobj(self, event): #bruce 050610
        """Keep glpane.selobj up-to-date, as object under mouse, or None
        (whether or not that kind of object should get highlighted).
           Return True if selobj is already updated when we return, or False if that will not happen until the next paintGL.
           Warning: if selobj needs to change, this routine does not change it (or even reset it to None);
        it only sets flags and does gl_update, so that paintGL will run soon and will update it properly,
        and will highlight it if desired ###@@@ how is that controlled? probably by some statevar in self, passed to gl flag?
           This means that old code which depends on selatom being up-to-date must do one of two things:
        - compute selatom from selobj, whenever it's needed;
        - hope that paintGL runs some callback in this mode when it changes selobj, which updates selatom
          and outputs whatever statusbar message is appropriate. ####@@@@ doit... this is not yet fully ok.
        """
        #e see also the options on update_selatom;
        # probably update_selatom should still exist, and call this, and provide those opts, and set selatom from this,
        # but see the docstring issues before doing this ####@@@@

        # bruce 050610 new comments for intended code (#e clean them up and make a docstring):
        # selobj might be None, or might be in stencil buffer.
        # Use that and depthbuffer to decide whether redraw is needed to look for a new one.
        # Details: if selobj none, depth far or under water is fine, any other depth means look for new selobj (set flag, glupdate).
        # if selobj not none, stencil 1 means still same selobj (if no stencil buffer, have to guess it's 0);
        # else depth far or underwater means it's now None (repaint needed to make that look right, but no hittest needed)
        # and another depth means set flag and do repaint (might get same selobj (if no stencil buffer or things moved)
        #   or none or new one, won't know yet, doesn't matter a lot, not sure we even need to reset it to none here first).
        # Only goals of this method: maybe glupdate, if so maybe first set flag, and maybe set selobj none, but prob not
        # (repaint sets new selobj, maybe highlights it).
        # [some code copied from modifyMode]
        glpane = self.o
        
        if self.o.is_animating:
            # If animating, do not select anything. For more info, see GLPane.animateToView(). mark 060404.
            # <is_animating> should be renamed to something more generic (i.e. <select_enabled>). mark 060701.
            return
        
        wX = event.pos().x()
        wY = glpane.height - event.pos().y()
        selobj = orig_selobj = glpane.selobj
        if selobj is not None:
            if glpane.stencilbits >= 1:
                # optimization: fast way to tell if we're still over the same object as last time
                # (warning: for now glpane.stencilbits is 1 even when true number of bits is higher; easy to fix when needed)
                stencilbit = glReadPixelsi(wX, wY, 1, 1, GL_STENCIL_INDEX)[0][0]
                    # Note: if there's no stencil buffer in this OpenGL context, this gets an invalid operation exception from OpenGL.
                    # And by default there isn't one -- it has to be asked for when the QGLWidget is initialized.
                # stencilbit tells whether the highlighted drawing of selobj got drawn at this point on the screen
                # (due to both the shape of selobj, and to the depth buffer contents when it was drawn)
            else:
                stencilbit = 0 # the correct value is "don't know"; 0 is conservative
                #e might collapse this code if stencilbit not used below;
                #e and/or might need to record whether we used this conservative value
            if stencilbit:
                return True # same selobj, no need for gl_update to change highlighting
        # We get here for no prior selobj,
        # or for a prior selobj that the mouse has moved off of the visible/highlighted part of,
        # or for a prior selobj when we don't know whether the mouse moved off of it or not
        # (due to lack of a stencil buffer, i.e. very limited graphics card or OpenGL implementation).
        #
        # We have to figure out selobj afresh from the mouse position (using depth buffer and/or GL_SELECT hit-testing).
        # It might be the same as before (if we have no stencil buffer, or if it got bigger or moved)
        # so don't set it to None for now (unless we're sure from the depth that it should end up being None) --
        # let it remain the old value until the new one (perhaps None) is computed during paintGL.
        #
        # Specifically, if this method can figure out the correct new setting of glpane.selobj (None or some object),
        # it should set it (###@@@ or call a setter? neither -- let end-code do this) and set new_selobj to that
        # (so code at method-end can repaint if new_selobj is different than orig_selobj);
        # and if not, it should set new_selobj to instructions for paintGL to find selobj (also handled by code at method-end).
        ###@@@ if we set it to None, and it wasn't before, we still have to redraw!
        ###@@@ ###e will need to fix bugs by resetting selobj when it moves or view changes etc (find same code as for selatom).
            
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)[0][0]
            # depth (range 0 to 1, 0 is nearest) of most recent drawing at this mouse position
        new_selobj_unknown = False
            # following code should either set this True or set new_selobj to correct new value (None or an object)
        if wZ >= GL_FAR_Z: ## Huaicai 8/17/05 for blue sky plane z value
            # far depth (this happens when no object is touched)
            new_selobj = None
        else:
            # compare to water surface depth
            cov = - glpane.pov # center_of_view (kluge: we happen to know this is where the water surface is drawn)
            try:
                junk, junk, cov_depth = gluProject( cov[0], cov[1], cov[2] )
            except:
                print_compact_traceback( "gluProject( cov[0], cov[1], cov[2] ) exception ignored, for cov == %r: " % (cov,) )
                cov_depth = 2 # too deep to matter (depths range from 0 to 1, 0 is nearest to screen)
            water_depth = cov_depth
            if self.water_enabled and wZ >= water_depth:
                #print "behind water: %r >= %r" % (wZ , water_depth)
                new_selobj = None
                    # btw, in constrast to this condition for a new selobj, an existing one will
                    # remain selected even when you mouseover the underwater part (that's intentional)
            else:
                # depth is in front of water
                new_selobj_unknown = True
                
        if new_selobj_unknown:
            # Only the next paintGL call can figure out the selobj (in general),
            # so set glpane.glselect_wanted to the command to do that and the necessary info for doing it.
            # Note: it might have been set before and not yet used;
            # if so, it's good to discard that old info, as we do.
            glpane.glselect_wanted = (wX, wY, wZ) # mouse pos, depth
                ###e and soon, instructions about whether to highlight selobj based on its type (as predicate on selobj)
                ###e should also include current count of number of times
                # glupdate was ever called because model looks different,
                # and inval these instrs if that happens again before they are used
                # (since in that case wZ is no longer correct)
            # don't change glpane.selobj (since it might not even need to change) (ok??#k) -- the next paintGL will do that
            glpane.gl_update()
        else:
            # it's known (to be a specific object or None)
            if new_selobj is not orig_selobj:
                # this is the right test even if one or both of those is None.
                # (Note that we never figure out a specific new_selobj, above,
                #  except when it's None, but that might change someday
                #  and this code can already handle that.)
                glpane.set_selobj( new_selobj, "depmode")
                    #e use setter func, if anything needs to observe changes to this?
                    # or let paintGL notice the change (whether it or elseone does it) and report that?
                    # Probably it's better for paintGL to report it, so it doesn't happen too often or too soon!
                    # And in the glselect_wanted case, that's the only choice, so we needed code for that anyway.
                    # Conclusion: no external setter func is required; maybe glpane has an internal one and tracks prior value.
                glpane.gl_update() # this might or might not highlight that selobj ###e need to tell it how to decide??
        #####@@@@@ we'll need to do this in a callback when selobj is set:
        ## self.update_selatom(event, msg_about_click = True)
        return not new_selobj_unknown # from update_selobj

    def update_selatom(self, event, singOnly = False, msg_about_click = False, resort_to_prior = True): 
        #bruce 050610 rewrote this
        '''Keep selatom up-to-date, as atom under mouse based on <event>; 
        When <singOnly> is True, only keep singlets up-to-date.
        When <msg_about_click> is True, print a message on the statusbar about the LMB press.
        <resort_to_prior> is disabled.
        ###@@@ correctness after rewrite not yet proven, due to delay until paintGL
        '''
        # bruce 050124 split this out of bareMotion so options can vary
        glpane = self.o
        if event is None:
            # event (and thus its x,y position) is not known [bruce 050612 added this possibility]
            known = False
        else:
            known = self.update_selobj(event) # this might do gl_update (but the paintGL triggered by that only happens later!),
                # and (when it does) might not know the correct obj...
                # so it returns True iff it did know the correct obj (or None) to store into glpane.selobj, False if not.
        assert known in [False,True]
        # If not known, use None or use the prior one? This is up to the caller
        # since the best policy varies. Default is resort_to_prior = True since some callers need this
        # and I did not yet scan them all and fix them. ####@@@@ do that
        
        selobj = glpane.selobj
        ## print "known %r, selobj %r" % (known, selobj) 
            
        if not known:
            if resort_to_prior: 
                pass # stored one is what this says to use, and is what we'll use
                ## print "resort_to_prior using",glpane.selobj
                    # [this is rare, I guess since paintGL usually has time to run after bareMotion before clicks]
            else:
                selobj = None
        oldselatom = glpane.selatom
        atm = selobj
        if not isinstance(atm, Atom):
            atm = None
        if atm is not None and (atm.element is Singlet or not singOnly):
            pass # we'll use this atm as the new selatom
        else:
            atm = None # otherwise we'll use None
        glpane.selatom = atm
        if msg_about_click: # [always do this, since many things can change what it should say]
            # come up with a status bar message about what we would paste now.
            # [bruce 050124 new feature, to mitigate current lack of model tree highlighting of pastable]
            msg = self.describe_leftDown_action( glpane.selatom)
            env.history.statusbar_msg( msg)
        if glpane.selatom is not oldselatom:
            # update display (probably redundant with side effect of update_selobj; ok if it is, and I'm not sure it always is #k)
            glpane.gl_update() # draws selatom too, since its chunk is not hidden [comment might be obs, as of 050610]
        
        return
        
# == LMB event handling methods ====================================
#
# The following sections include all the LMB event handling methods for selectAtomsMode
# The section is organized in the following order and includes the following methods:
#
#   - LMB down-click (button press) methods
#       leftShiftDown()
#       leftCntlDown()
#       leftDown()
#
#   - LMB drag methods
#       leftShiftDrag()
#       leftDrag()
# 
#   - LMB up-click (button release) methods
#       leftShiftUp()
#       leftCntlUp()
#       leftUp()
#
#   - LMB double-click method (only one)
#       leftDouble()
#
# For more information about the LMB event handling scheme, go to 
# http://www.nanoengineer-1.net/ and click on the "Build Mode UI Specification" link.
        
# == LMB down-click (button press) methods

    def leftShiftDown(self, event):
        '''Event handler for Shift+LMB press.'''
        self.leftDown(event)
    
    def leftCntlDown(self, event):
        '''Event handler for Control+LMB press.'''
        self.leftDown(event)
    
    def leftDown(self, event):
        '''Event handler for all LMB press events.'''

        self.set_cmdname('BuildClick') #e (this should be set again later (during the same drag) to a more specific command name)
        
        self.o.assy.permit_pick_atoms() # Fixes bug 1413, 1477, 1478 and 1479.  Mark 060218.
        self.reset_drag_vars()
        env.history.statusbar_msg(" ") # get rid of obsolete msg from bareMotion [bruce 050124; imperfect #e]
            
        self.LMB_press_event = QMouseEvent(event) # Make a copy of this event and save it. 
            # We will need it later if we change our mind and start selecting a 2D region in leftDrag().
            # Copying the event in this way is necessary because Qt will overwrite <event> later (in 
            # leftDrag) if we simply set self.LMB_press_event = event.  mark 060220.

        #bruce 060315 replacing LMB_press_pt with LMB_press_pt_xy
        self.LMB_press_pt_xy = (event.pos().x(), event.pos().y())
            # <LMB_press_pt_xy> is the position of the mouse in window coordinates when the LMB was pressed.
            # Used in mouse_within_stickiness_limit (called by leftDrag() and other methods).
            # We don't bother to vertically flip y using self.height (as mousepoints does),
            # since this is only used for drag distance within single drags.
            
        obj = self.get_obj_under_cursor(event)
            # If highlighting is turned on, get_obj_under_cursor() returns atoms, singlets and bonds (not jigs).
            # If highlighting is turned off, get_obj_under_cursor() returns atoms and singlets (not bonds or jigs).
        
        #print '-'*20
        #print "leftDown(): obj=",obj
        
        if obj is None: # Cursor over empty space.
            self.emptySpaceLeftDown(event)
            return
        
        if isinstance(obj, Atom) and obj.is_singlet(): # Cursor over a singlet
            self.singletLeftDown(obj, event)
                # no win_update() needed. It's the responsibility of singletLeftDown to do it if needed.
            return
            
        if isinstance(obj, Atom) and not obj.is_singlet(): # Cursor over a real atom
            self.atomLeftDown(obj, event)
        
        elif isinstance(obj, Bond) and not obj.is_open_bond(): # Cursor over a bond.
            self.bondLeftDown(obj, event)
        
        elif isinstance(obj, Jig): # Cursor over a jig.
            self.jigLeftDown(obj, event)

        else: # Cursor is over something else other than an atom, singlet or bond. 
            # The program never executes lines in this else statement since
            # get_obj_under_cursor() only returns atoms, singlets or bonds.
            pass

        self.w.win_update()
        return

# == LMB drag methods

    def leftShiftDrag(self, event):
        '''Event handler for Shift+LMB+Drag.'''
        self.leftDrag(event)
        
    def leftCntlDrag(self, event):
        '''Event handler for Control+LMB+Drag.'''
        self.leftDrag(event)
        
    def leftDrag(self, event):
        '''Event handler for all LMB+Drag events.'''
        
        # Do not change the order of the following conditionals unless you know
        # what you're doing.  mark 060208.
        
        if self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            return
            
        obj = self.current_obj
        
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.emptySpaceLeftDrag(event)
            return
            
        if self.o.modkeys is not None:
            # If a drag event has happened after the cursor was over an atom and a modkey is pressed,
            # do a 2D region selection as if the atom were absent.
            self.emptySpaceLeftDown(self.LMB_press_event)
            #bruce 060721 question: why don't we also do emptySpaceLeftDrag at this point?
            return
            
        if obj is None: # Nothing dragged (or clicked); return.
            return
        
        if isinstance(obj, Atom):
            if obj.is_singlet(): # Bondpoint
                self.singletDrag(obj, event)
            else: # Real atom
                self.atomDrag(obj, event)
        
        elif isinstance(obj, Bond): # Bond
            self.bondDrag(event)
        
        elif isinstance(obj, Jig): # Jig
            self.jigDrag(obj, event)
        
        else: # Something else
            pass
            
        # No gl_update() needed. Already taken care of.
        
    def posn_str(self, atm): #bruce 041123
        """return the position of an atom
        as a string for use in our status messages
        (also works if given an atom's position vector itself -- kluge, sorry)
        """
        try:
            x,y,z = atm.posn()
        except AttributeError:
            x,y,z = atm # kluge to accept either arg type
        return "(%.2f, %.2f, %.2f)" % (x,y,z)
        
# == LMB up-click (button release) methods

    def leftShiftUp(self, event):
        '''Event handler for Shift+LMB release.'''
        self.leftUp(event)
    
    def leftCntlUp(self, event):
        '''Event handler for Control+LMB release.'''
        self.leftUp(event)
    
    def leftUp(self, event):
        '''Event handler for all LMB release events.'''
        env.history.flush_saved_transients() # flush any transient message it saved up
        
        if self.ignore_next_leftUp_event: # This event is the second leftUp of a double click, so ignore it.
            self.ignore_next_leftUp_event = False
            self.update_selobj(event) # Fixes bug 1467. mark 060307.
            return
        
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.emptySpaceLeftUp(event)
            return
        
        obj = self.current_obj
            
        if obj is None: # Nothing dragged (or clicked); return.
            return
        
        if self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            event = self.LMB_press_event
            
        if isinstance(obj, Atom):
            if obj.is_singlet(): # Bondpoint
                self.singletLeftUp(obj, event)
            else: # Real atom
                self.atomLeftUp(obj, event)
            
        elif isinstance(obj, Bond): # Bond
            self.bondLeftUp(obj, event)
            
        elif isinstance(obj, Jig): # Jig
            self.jigLeftUp(obj, event)
        
        else:
            pass
        
        self.baggage = []
        self.current_obj = None #bruce 041130 fix bug 230 [later: i guess this attr had a different name then -- bruce 060721]
        self.o.selatom = None #bruce 041208 for safety in case it's killed
        #bruce 041130 comment: it forgets selatom, but doesn't repaint,
        # so selatom is still visible; then the next event will probably
        # set it again; all this seems ok for now, so I'll leave it alone.
        #bruce 041206: I changed my mind, since it seems dangerous to leave
        # it visible (seemingly active) but not active. So I'll repaint here.
        # In future we can consider first simulating a update_selatom at the
        # current location (to set selatom again, if appropriate), but it's
        # not clear this would be good, so *this* is what I won't do for now.
        #self.o.gl_update() #& Now handled in modkey*() methods. mark 060210.
        
# == LMB double-click method

    def leftDouble(self, event): # mark 060126.
        '''Double click event handler for the left mouse button. 
        '''
            
        self.ignore_next_leftUp_event = True
        
        if isinstance(self.obj_doubleclicked, Atom):
            if self.obj_doubleclicked.is_singlet():
                self.singletLeftDouble()
                return
            else:
                self.atomLeftDouble()
            
        if isinstance(self.obj_doubleclicked, Bond):
            self.bondLeftDouble()
            
        if isinstance(self.obj_doubleclicked, Jig):
            self.jigLeftDouble()

# == end of LMB event handler methods
        
    def getDstElement(self):
        '''Return the destination element user wants to transmute to. '''
        return self.eCCBtab1[self.w.transmute2ComboBox.currentItem()] 
            
            
    def getAtomtype(self, elmNo): 
        '''<Param> elm: the current transmuted to element 'atom number'.
        return the current pastable atomtype'''
        elm = PeriodicTable.getElement(elmNo)
        atomtype = None
        if len(elm.atomtypes) > 1: 
            try: 
                hybname = self.w.atomSelect_hybridComboBox.currentText()
                atype = elm.find_atomtype(hybname)
                if atype is not None:
                    atomtype = atype
            except:
                print_compact_traceback("exception (ignored): ") # error, but continue
            pass
        if atomtype is not None and atomtype.element is elm:
            return atomtype
            
        # For element that doesn't support hybridization
        return elm.atomtypes[0]
            
    def transmutePressed(self):
        '''Slot method, called when transmute button was pressed. '''
        force = self.w.transmuteCheckBox.isChecked()
            
        dstElem = self.getDstElement()
        atomType = self.getAtomtype(dstElem)
        self.w.assy.modifyTransmute(dstElem, force = force, atomType=atomType)
                
    def keyPress(self,key):
        '''keypress event handler for selectAtomsMode.
        '''
        from MWsemantics import eCCBtab2
        
        if self.o.mode.modename in ['SELECTATOMS']: 
            # Add mode names above to support atom filtering in subclasses.
            # Pressing Escape clears the selection filter.
            if key == Qt.Key_Escape and self.w.elemFilterComboBox.currentItem():
                # Clear the selection filter, but not the current selection. Fixes bug 1623. mark 060326
                self.set_selection_filter(0) # disable selection filter (sets current item to "All Elements").
                return
            
        basicMode.keyPress(self, key)

        if self.o.mode.modename in ['SELECTATOMS']: 
            # Add mode names above to support atom filtering in subclasses.
            # Pressing a valid key activates the selection filter and sets the element type.
            for sym, code, num in elemKeyTab:
                if key == code:
                    line = eCCBtab2[num] + 1
                    self.set_selection_filter(line)
                
    def keyRelease(self,key):
        '''keyrelease event handler for selectAtomsMode.
        '''
        basicMode.keyRelease(self, key)
    
    def set_selection_filter(self, indx):
        '''Slot for Selection Filter combobox. It can also be called to set the index of the current 
        item in the combobox to <indx>.  Prints history message when selection filter is 
        enabled/disabled and updates the cursor.  When <indx> = 0, the selection filter is disabled
        and the current item is set to "All Elements".
        '''
        self.w.elemFilterComboBox.setCurrentItem(indx) # Doesn't generate signal (good).
            # Updates the combobox to the new element to be filtered.
        
        if indx:
            selection_filter_enabled=True
        else:
            selection_filter_enabled=False
        
        if selection_filter_enabled != self.w.selection_filter_enabled:
            if selection_filter_enabled:
                env.history.message("Atom Selection Filter enabled.")
            else:
                env.history.message("Atom Selection Filter disabled.")
        
        if selection_filter_enabled: 
            self.w.selection_filter_enabled = True
            eltname = str(self.w.elemFilterComboBox.currentText())
            self.w.filtered_elements = []
            self.w.filtered_elements.append(PeriodicTable.getElement(eltname))
        else:
            self.w.selection_filter_enabled = False
            self.w.filtered_elements = []
        self.update_cursor()
            
    def update_cursor_for_no_MB(self):
        '''Update the cursor for 'Select Atoms' mode (selectAtomsMode)
        '''
        #print "selectAtomsMode.update_cursor_for_no_MB(): button=",self.o.button, ", modkeys=", self.o.modkeys
        
        if self.w.selection_filter_enabled:
            self.update_cursor_for_no_MB_selection_filter_enabled()
        else:
            self.update_cursor_for_no_MB_selection_filter_disabled()
            
    def update_cursor_for_no_MB_selection_filter_disabled(self):
        '''Update the cursor for when the Selection Filter is disabled (default).
        '''
        if self.o.modkeys is None:
            self.o.setCursor(self.w.SelectAtomsCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.SelectAtomsAddCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.SelectAtomsSubtractCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB(): Invalid modkey=", self.o.modkeys
        return
        
    def update_cursor_for_no_MB_selection_filter_enabled(self):
        '''Update the cursor for when the Selection Filter is enabled.
        '''
        if self.o.modkeys is None:
            self.o.setCursor(self.w.SelectAtomsFilterCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.SelectAtomsAddFilterCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.SelectAtomsSubtractFilterCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteFilterCursor) # Fixes bug 1604. mark 060303.
        else:
            print "Error in update_cursor_for_no_MB(): Invalid modkey=", self.o.modkeys
        return
            
    def rightShiftDown(self, event):
        basicMode.rightShiftDown(self, event)
        self.o.setCursor(self.w.SelectAtomsCursor)
           
    def rightCntlDown(self, event):          
        basicMode.rightCntlDown(self, event)
        self.o.setCursor(self.w.SelectAtomsCursor)
        
    def update_hybridComboBox(self, win, text = None): 
        '''Based on the same named function in depositMode.py.
        Put the names of the current element's hybridization types into win.hybridComboBox; select the specified one if provided'''
        # I'm not preserving current setting, since when user changes C(sp2) to N, they might not want N(sp2).
        # It might be best to "intelligently modify it", or at least to preserve it when element doesn't change,
        # but even the latter is not obvious how to do in this code (right here, we don't know the prior element).
        #e Actually it'd be easy if I stored the element right here, since this is the only place I set the items --
        # provided this runs often enough (whenever anything changes the current element), which remains to be seen.
            
        elem = PeriodicTable.getElement(self.getDstElement()) 
        if text is None: 
            # Preserve current setting (by name) when possible, and when element is unchanged (not sure if that ever happens).
            # I'm not preserving it when element changes, since when user changes C(sp2) to N, they might not want N(sp2).
            # [It might be best to "intelligently modify it" (to the most similar type of the new element) in some sense,
            #  or it might not (too unpredictable); I won't try this for now.]
            text = str(win.atomSelect_hybridComboBox.currentText() )
        win.atomSelect_hybridComboBox.clear()
        atypes = elem.atomtypes
        if len(atypes) > 1:
            for atype in atypes:
                win.atomSelect_hybridComboBox.insertItem( atype.name)
                if atype.name == text:
                    win.atomSelect_hybridComboBox.setCurrentItem( win.atomSelect_hybridComboBox.count() - 1 ) #k sticky as more added?
            win.atomSelect_hybridComboBox.show()
        else:
            win.atomSelect_hybridComboBox.hide()
        return

    def _highlightAtoms(self, grp):
        """Highlight atoms or chunks inside ESPImage jigs."""
        from jigs_planes import ESPImage
            
        if isinstance(grp, ESPImage): 
            grp.highlightAtomChunks()
        elif isinstance(grp, Group):    
            for m in grp.members:
                if isinstance(m, ESPImage):
                    m.highlightAtomChunks()
                elif isinstance(m, Group):
                    self._highlightAtoms(m)
        return
                        
    def Draw(self):
        """Draw the model for Select Atoms mode."""
        selectMode.Draw(self)
        self._highlightAtoms(self.o.assy.part.topnode)
        return

    pass # end of class selectAtomsMode

# end
