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
would be easier to fix, and some NFRs easier to implement. [bruce 060728 -- I'm adding drag_handlers
for use by new kinds of draggable or buttonlike things (only in selectAtoms mode and subclasses),
but not changing how old dragging code works.]
"""

from modes import *
from HistoryWidget import orangemsg
from chunk import molecule
import env
from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice

debug_update_selobj_calls = False # do not commit with true

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

    def objectSetup(self, obj): ###e [should move this up, below generic left* methods -- it's not just about atoms]
        # [this seems to be called (sometimes indirectly) by every leftDown method, and by some methods in depmode
        #  that create objects and can immediately drag them. Purpose is more general than just for a literal "drag" --
        #  I guess it's for many things that immediately-subsequent leftDrag or leftUp or leftDouble might need to
        #  know obj to decide on. I think I'll call it for all new drag_handlers too. [bruce 060728 comment]]
        self.current_obj = obj # [used by leftDrag and leftUp to decide what to do [bruce 060727 comment]]
        self.obj_doubleclicked = obj # [used by leftDouble and class-specific leftDouble methods [bruce 060727 comment]]
        if obj is None:
            self.current_obj_clicked = False
        else:
            self.current_obj_clicked = True
                # [will be set back to False if obj is dragged, but only by class-specific drag methods,
                #  not by leftDrag itself -- make sure to consider doing that in drag_handler case too  #####@@@@@
                #  [bruce 060727 comment]]

            # we need to store something unique about this event;
            # we'd use serno or time if it had one... instead this _count will do.
            global _count
            _count = _count + 1
            self.current_obj_start = _count # used in transient_id argument to env.history.message

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
        selobj = self.o.selobj # only used if selatom is None [this comment seems wrong -- bruce 060726]
        if isinstance( selobj, Bond) and not selobj.is_open_bond(): #bruce 050727 new feature
            env.history.message_no_html("breaking bond %s" % selobj)
                # note: %r doesn't show bond type, but %s needs _no_html since it contains "<-->" which looks like HTML.
            self.o.selobj = None # without this, the bond remains highlighted even after it's broken (visible if it's toolong)
                ###e shouldn't we use set_selobj instead?? [bruce 060726 question]
            selobj.bust() # this fails to preserve the bond type on the open bonds -- not sure if that's bad, but probably it is
            self.set_cmdname('Delete Bond')
            self.o.assy.changed() #k needed?
            self.w.win_update() #k wouldn't gl_update be enough? [bruce 060726 question]
            
    def bondDrag(self, obj, event):
        # [bruce 060728 added obj arg, for uniformity; probably needed even more in other Bond methods ##e]
        # If a LMB+Drag event has happened after selecting a bond in left*Down(),
        # do a 2D region selection as if the bond were absent. This takes care of 
        # both Shift and Control mod key cases.
        self.cursor_over_when_LMB_pressed = 'Empty Space'
        self.select_2d_region(self.LMB_press_event) # [i suspect this inlines something in another method -- bruce 060728 comment]
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

# == drag_handler event handler methods [bruce 060728]

    # note: dragHandlerLeftDown() does not exist, since self.drag_handler is only created by some other object's leftDown method

    def dragHandlerSetup(self, drag_handler, event):
        assert drag_handler is self.drag_handler #e clean up sometime? not sure how
        self.cursor_over_when_LMB_pressed = 'drag_handler' # not presently used, except for not being 'Empty Space'
        self.objectSetup(drag_handler) #bruce 060728
        if not drag_handler.handles_updates():
            self.w.win_update()
        return
    
    def dragHandlerDrag(self, drag_handler, event):
        ###e nim: for some kinds of them, we want to pick them in leftDown, then drag all picked objects, using self.dragto...
        try:
            method = getattr(drag_handler, 'DraggedOn', None) #e rename
            if method:
                old_selobj = self.o.selobj
                ###e args it might need:
                # - mode, for callbacks for things like update_selobj (which needs a flag to avoid glselect)
                # - event, to pass to update_selobj (and maybe other callbacks we offer)
                # and ones it can callback for:
                # - offset, for convenient 3d motion of movable dragobjs
                # - maybe the mouseray, as two points?
                retval = method(event, self)
                # assume no update needed unless selobj changed
                #e so detect that... not sure if we need to, maybe set_selobj or (probably) update_selobj does it?
                if old_selobj is not self.o.selobj:
                    if 0 and env.debug():
                        print "debug fyi: selobj change noticed by dragHandlerDrag, %r -> %r" % (old_selobj ,  self.o.selobj)
                        # WARNING: this is not a good enough detection, if any outside code also does update_selobj and changes it,
                        # since those changes won't be detected here. Apparently this happens when the mouse moves back onto a real
                        # selobj. Therefore I'm disabling this test for now. If we need it, we'll need to store old_selobj in self,
                        # between calls of this method. 
                    pass
                pass
            pass
        except:
            print_compact_traceback("bug: exception in dragHandlerDrag ignored: ")
        return
        
    def dragHandlerLeftUp(self, drag_handler, event):
        try:
            method = getattr(drag_handler, 'ReleasedOn', None)#e rename
            if method:
                retval = method(self.o.selobj, event, self)
                    #bruce 061120 changed args from (selobj, self) to (selobj, event, self) [where self is the mode object]
                self.w.win_update() ##k not always needed, might be redundant, should let the handler decide ####@@@@
                # lots of other stuff done by other leftUp methods here? #####@@@@@
            pass
        except:
            print_compact_traceback("bug: exception in dragHandlerLeftUp ignored: ")
        pass
        
    def dragHandlerLeftDouble(self, drag_handler, event): # never called as of 070324; see also testmode.leftDouble
        if env.debug():
            print "debug fyi: dragHandlerLeftDouble is nim"
        return
        
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
        
        if 1:
            #bruce 060611 experiment, harmless, prototype of WidgetExpr-related changes, might help Bauble; committed 060722
            # [see also leftClick, which will eventually supercede this, and probably could already -- bruce 060725]
            method = getattr(j, 'clickedOn', None)
            if method and method(self.jig_MovePt):
                return

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
        
#== End of (most) Jig helper methods

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
    
    def mouse_exceeded_distance(self, event, pixel_distance): 
        """Check if mouse has been moved beyond <pixel_distance> since the last mouse 'move event'.
        Return True if <pixel_distance> is exceeded, False if it hasn't. Distance is measured in pixels.
        """
        try:
            xy_last = self.xy_last
        except:
            self.xy_last = (event.pos().x(), event.pos().y())
            return False
        xy_now = (event.pos().x(), event.pos().y())
        dist = vlen(A(xy_last) - A(xy_now)) #e could be optimized (e.g. store square of dist), probably doesn't matter
        self.xy_last = xy_now
        return dist > pixel_distance
            
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
    
    def get_jig_under_cursor(self, event): ###e should move this up with the other Jig helper methods
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

    # ==
    
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

# end
