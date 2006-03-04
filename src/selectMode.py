# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
selectMode.py -- the default mode for Atom's main model view.

$Id$
"""

from modes import *
from chunk import molecule
import env

_count = 0

DRAG_STICKINESS_LIMIT = 0.03 # in Angstroms with respect to the front clipping plane.
    #& To do: Change to pixel units and make it a user pref.  Also consider a different var/pref
    #& for singlet vs. atom drag stickiness limits. Mark 060213.

## TEST_PYREX_OPENGL = 0 # bruce 060209 moved this to where it's used (below), and changed it to a debug_pref

def do_what_MainWindowUI_should_do(w):
    '''This creates the Select Atoms (not the Select Chunks) dashboard .
    '''
     
    w.selectAtomsDashboard.clear()

    w.depositAtomLabel = QLabel(w.selectAtomsDashboard,"Select Atoms")
    w.depositAtomLabel.setText(" Select Atoms ")
    w.selectAtomsDashboard.addSeparator()

    ## Kludge to make it work, it's really not good, may need to rework it later. Huaicai 8/10/05
    #w.filterCheckBox = QCheckBox(" Select Only : ", w.selectAtomsDashboard)
    #w.filterCheckBox.hide()
    #QToolTip.add(w.filterCheckBox, qApp.translate("MainWindow","Selection Filter", None))
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
    QToolTip.add(w.transmuteButton, qApp.translate("MainWindow","Transmute Selected Atoms", None))
                 
    w.transmuteCheckBox = QCheckBox(" Force to Keep Bonds", w.selectAtomsDashboard)
    QToolTip.add(w.transmuteCheckBox, qApp.translate("MainWindow","Check to keep bonds when transmute.", None))
    w.modifySetElementAction.setEnabled(False) #addTo(w.selectAtomsDashboard)
    
    w.selectAtomsDashboard.addSeparator()
    w.selectAtomsDashboard.highlightingCB = QCheckBox("Highlighting", w.selectAtomsDashboard)
    w.selectAtomsDashboard.highlightingCB.setChecked(env.prefs[selectAtomsModeHighlightingEnabled_prefs_key])

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


    
class selectMode(basicMode):
    "the default mode of GLPane"
    
    # class constants
    backgroundColor = 189/255.0, 228/255.0, 238/255.0
    gridColor = (0.0, 0.0, 0.6)

    # default initial values
    savedOrtho = 0

    jigSelectionEnabled = True
    
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


    #def __init__(self, glpane):
    #    """The initial function is called only once for the whole program """
    #    basicMode.__init__(self, glpane)
    #    self.jigSelectionEnabled = True
    
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
            has_jig_selected = False
            
            if self.jigSelectionEnabled and self.jigGLSelect(event, self.selSense):
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
            self.o.assy.unpickatoms()
            a.pick()
        if not a.picked and self.o.modkeys == 'Shift':
            a.pick()
        if a.picked and len(self.o.assy.selatoms_list()) > 1:
            # now called when two or more atoms are selected.  mark 060202.
            self.cursor_over_when_LMB_pressed = 'Picked Atom'
            self.drag_multiple_atoms = True
            self.atomsSetup(a)
        else:
            if a.picked:
                self.cursor_over_when_LMB_pressed = 'Picked Atom'
            else:
                self.cursor_over_when_LMB_pressed = 'Unpicked Atom'
            self.drag_multiple_atoms = False
            self.atomSetup(a)

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

    def atomSetup(self, a):
        '''Setup for a click, double-click or drag event for real atom <a>.
        '''
        self.objectSetup(a)
        self.baggage = []
        self.nonbaggage = []
        self.baggage, self.nonbaggage = a.baggage_and_other_neighbors()
        
    def atomsSetup(self, a):
        '''Setup for a click or double-click of real atom <a>, but also handles setup of dragging of 
        real atom <a> and all other currently selected atoms.
        '''
        self.objectSetup(a)
        self.baggage = []
        self.nonbaggage = []
        #all_nonbaggage = [] # NIY. mark 060202.
        
        selatoms = self.o.assy.selatoms_list()
        
        # Accumulate all the baggage from the selected atoms, which can include
        # selected atoms if a selected atom is another selected atom's baggage.
        # BTW, it is not possible for an atom to end up in self.baggage twice.
        for at in selatoms[:]:
            baggage, nonbaggage = at.baggage_and_other_neighbors()
            self.baggage += baggage # the baggage we'll keep.
            #all_nonbaggage += nonbaggage
        
        # dragobjs contains all the selected atoms minus atoms that are also 
        # baggage. It is critical that dragobjs does not contain any baggage 
        # atoms or they will be moved twice in atomsDrag(), so we removed them here.
        for at in selatoms[:]:
            if not at in self.baggage: # no baggage atoms in dragobjs.
                self.dragobjs.append(at)
        
        # Accumulate all the nonbaggage bonded to the selected atoms.
        # We also need to keep a record of which selected atom belongs to
        # each nonbaggage atom.  This is not implemented yet, but will be needed
        # to get atomsDrag() to work properly.  I'm commenting it out for now.
        # mark 060202.
        #for at in all_nonbaggage[:]:
        #    if not at in self.dragobjs:
        #        self.nonbaggage.append(at)
        
        # Debugging print statements.  mark 060202.
        #print "dragobjs = ", self.dragobjs
        #print "baggage = ", self.baggage    
        #print "nonbaggage = ", self.nonbaggage
        
    def delete_atom_and_baggage(self, event):
        '''If the object under the cursor is an atom, delete it and any baggage.  
        Return the result of what happened.
        '''
        a = self.get_real_atom_under_cursor(event)

        if a is None:
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
        """Drag real atom <a>.  <event> is a drag event.
        """
        
        if self.drag_multiple_atoms:
            self.atomsDrag(a, event)
            return
                
        apos0 = a.posn()
        
        px = self.dragto(a.posn(), event)
        apo = a.posn()
        delta = px - apo # xyz delta between new and current position of <a>.
        
        n = self.nonbaggage
            # n = real atoms bonded to <a> that are not singlets or monovalent atoms.
            # they need to have their own baggage adjusted below.
        
        old = V(0,0,0)
        new = V(0,0,0)
            # old and new are used to compute the delta quat for the average 
            # non-baggage bond and apply it to <a>'s baggage
        
        for at in n:
            # Since adjBaggage() doesn't change at.posn(), I switched the order for readability.
            # It is now more obvious that <old> and <new> have no impact on at.adjBaggage(). 
            # mark 060202.
            at.adjBaggage(a, px) # Adjust the baggage of nonbaggage atoms.
            old += at.posn()-apo
            new += at.posn()-px
        
        # Handle baggage differently if <a> has nonbaggage atoms.
        if n: # If <a> has nonbaggage atoms, move and rotate its baggage atoms.
            q=Q(old,new)
            for at in self.baggage:
                at.setposn(q.rot(at.posn()-apo)+px)
        else: # If <a> has no nonbaggage atoms, just move each baggage atom (no rotation).
            for at in self.baggage:
                at.setposn(at.posn()+delta)
        # [Josh wrote, about the following "a.setposn(px)":]
        # there's some weirdness I don't understand
        # this doesn't work if done before the loop above
        a.setposn(px)
        # [bruce 041108 writes:]
        # This a.setposn(px) can't be done before the at.adjBaggage(a, px)
        # in the loop before it, or adjBaggage (which compares a.posn() to
        # px) would think atom <a> was not moving.
        
        self.atomDragUpdate(a, apos0)
        
    def atomsDrag(self, a, event):
        """Drag real atom <a> and all picked atoms.  <event> is a drag event.
        """
        # atomsDrag() behaves differently than atomDrag() in that nonbaggage atoms 
        # and their own baggage are not used or moved in any way. I used to think this 
        # was a feature and not a bug, but I'm pretty sure I was wrong about that since
        # other programs behave like atomDrag() when dragging two or more atoms.
        # The current implementation is still better than nothing and might be OK for A7.
        # I'm guessing we'll want to change it, though.  If so, I have a good idea how to 
        # code it, but it will take a day to get it working properly. mark 060201.
        
        # Note: <a> gets moved in one of the two 'for' loops below.  
        # If <a> is a baggage atom, it will be in the baggage list.  
        # Otherwise, it will be in dragobjs. mark 060201.
        
        apos0 = a.posn()
        
        px = self.dragto(a.posn(), event)
        apo = a.posn()
        delta = px - apo # xyz delta between new and current position of <a>.

        # Move dragobjs.
        for at in self.dragobjs[:]:
            at.setposn(at.posn()+delta)
        
        # Move baggage.
        for at in self.baggage[:]:
            at.setposn(at.posn()+delta)
            
        self.atomDragUpdate(a, apos0)
        
    def atomDragUpdate(self, a, apos0):
        '''Updates the GLPane and status bar message when dragging atom <a> around.
        <apos0> is the previous x,y,z position of <a>.
        '''
        apos1 = a.posn()
        if apos1 - apos0:
            msg = "dragged atom %r to %s" % (a, self.posn_str(a))
            this_drag_id = (self.current_obj_start, self.__class__.leftDrag)
            env.history.message(msg, transient_id = this_drag_id)
            self.current_obj_clicked = False # atom was dragged. mark 060125.
            self.o.gl_update()
            
    def dragto(self, point, event, perp = None):
        """Return the point to which we should drag the given point,
        if event is the drag-motion event and we want to drag the point
        parallel to the screen (or perpendicular to the given direction "perp"
        if one is passed in). (Only correct for points, not extended objects,
        unless you use the point which was clicked on (not e.g. the center)
        as the dragged point.)
        """
        #bruce 041123 split this from two methods, and bugfixed to make dragging
        # parallel to screen. (I don't know if there was a bug report for that.)
        # Should be moved into modes.py and used in modifyMode too. ###e
        p1, p2 = self.o.mousepoints(event)
        if perp is None:
            perp = self.o.out
        point2 = planeXline(point, perp, p1, norm(p2-p1)) # args are (ppt, pv, lpt, lv)
        if point2 is None:
            # should never happen, but use old code as a last resort:
            point2 = ptonline(point, p1, norm(p2-p1))
        return point2
        
    def atomLeftUp(self, a, event): # Was atomClicked(). mark 060220.
        '''Real atom <a> was clicked, so select, unselect or delete it based on the current modkey.
        - If no modkey is pressed, clear the selection and pick atom <a>.
        - If Shift is pressed, pick <a>, adding it to the current selection.
        - If Ctrl is pressed,  unpick <a>, removing it from the current selection.
        - If Shift+Control (Delete) is pressed, delete atom <a>.
        '''
        
        if not self.current_obj_clicked:
            # Atom was dragged.  Nothing to do but return.
            self.set_cmdname('Move Atom') #& Not taking. mark 060220.
            self.o.assy.changed() # mark 060227
            return
            
        nochange = False
        
        if self.o.modkeys is None:
            self.o.assy.unpickatoms()
            if a.picked:
                nochange = True
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
                self.set_cmdname('Unselect Atom')
                env.history.message("unpicked %r" % a)
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
            self.o.assy.unpickatoms()
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
            
    def bondLeftDrag(self, event):
        # If a LMB+Drag event has happened after selecting a bond in left*Down(),
        # do a 2D region selection as if the bond were absent. This takes care of 
        # both Shift and Control mod key cases.
        self.cursor_over_when_LMB_pressed = 'Empty Space'
        self.select_2d_region(self.LMB_press_event)
        self.current_obj_clicked = False
        self.current_obj = None
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
        
#== End of singlet helper methods
        
    def mouse_within_stickiness_limit(self, event, drag_stickiness_limit):
        '''Check if mouse has been dragged beyond <drag_stickiness_limit> while holding down the LMB.
        Returns True if the mouse has not exceeded <drag_stickiness_limit>.
        Returns False if the mouse has exceeded <drag_stickiness_limit>.
        <drag_stickiness_limit> is measured in Angstroms. #& will be changed to pixels. mark 060213
        '''
        #& Intend to add arg for pixels
        if self.drag_stickiness_limit_exceeded:
            return False
        
        LMB_drag_pt, junk = self.o.mousepoints(event, 0.01)
        self.drag_distance = vlen(LMB_drag_pt - self.LMB_press_pt)
        if self.drag_distance/self.o.scale < drag_stickiness_limit:
            return True
        else:
            self.drag_stickiness_limit_exceeded = True
            return False

    def pickit(self):
        '''Returns True or False based on the current modkey state.  
        If modkey is None (no modkey is pressed), it will unpick all atoms.
        '''
        if self.o.modkeys is None:
            self.o.assy.unpickatoms()
            return True
        if self.o.modkeys == 'Shift':
            return True
        if self.o.modkeys == 'Control':
            return False
        else: # Delete
            return False
            
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
    
    def setJigSelectionEnabled(self):
        self.jigSelectionEnabled = not self.jigSelectionEnabled
                 
        id = self.Menu1.idAt(3)
        self.Menu1.setItemChecked(id, self.jigSelectionEnabled)
        
                
    def Draw(self):
        if 1:
            # wware 060124  Embed Pyrex/OpenGL unit tests into the cad code
            # grantham 060207:
            # Set to 1 to see a small array of eight spheres.
            # Set to 2 to see the Large-Bearing model, but this is most effective if
            #  the Large-Bearing has already been loaded normally into rotate mode
            #bruce 060209 set this from a debug_pref menu item, not a hardcoded flag
            from debug_prefs import debug_pref, Choice
            TEST_PYREX_OPENGL = debug_pref("TEST_PYREX_OPENGL", Choice([0,1,2]), non_debug = True)
                #e should remove non_debug = True before release!
            # uncomment this line to set it in the old way:
            ## TEST_PYREX_OPENGL = 1
        if TEST_PYREX_OPENGL:
            try:
                #self.w.win_update()
                sys.path.append("./experimental/pyrex-opengl")
                import quux
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
            # bruce comment 040922: code is almost identical with modifyMode.Draw;
            # the difference (no check for self.o.assy existing) might be a bug in this version, or might have no effect.
            basicMode.Draw(self)   
            #self.griddraw()
            if self.selCurve_List: self.draw_selection_curve()
            self.o.assy.draw(self.o)

    def makeMenus(self): # menu item names modified by bruce 041217

        def fixit3(text, func): 
            # Not called anymore since switching modes using context menus is no longer supported. mark 060303.
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
            # mark 060303. added the following:
            ('Enable Jig Selection',  self.setJigSelectionEnabled, 'checked'),
            None,
            ('Change Background Color...', self.w.dispBGColor),
            ]
        
        #& Marked for removal. mark 060303.
        #self.Menu_spec_shift = [
        #    ('Delete        Del', self.o.assy.delete_sel),
        #    ('Hide', self.o.assy.Hide)]
        
        #& Marked for removal. mark 060303.
        #self.Menu_spec_control = [
        #    ('Invisible', self.w.dispInvis),
        #    None,
        #    ('Default', self.w.dispDefault),
        #    ('Lines', self.w.dispLines),
        #    ('CPK', self.w.dispCPK),
        #    ('Tubes', self.w.dispTubes),
        #    ('VdW', self.w.dispVdW),
        #    None,
        #    ('Chunk Color...', self.w.dispObjectColor),
        #    ('Reset Chunk Color', self.w.dispResetChunkColor),
        #    ('Reset Atoms Display', self.w.dispResetAtomsDisplay),
        #    ('Show Invisible Atoms', self.w.dispShowInvisAtoms),
        #    ]

    pass # end of class selectMode
    
class selectMolsMode(selectMode):
    modename = 'SELECTMOLS'
    default_mode_status_text = "Mode: Select Chunks"
    
    def Enter(self): 
        basicMode.Enter(self)
        self.o.assy.pickParts() # josh 10/7 to avoid race in assy init
            
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
        
        self.Menu_spec = [
            ('Change Chunk Color...', self.w.dispObjectColor),
            ('Reset Chunk Color', self.w.dispResetChunkColor),
            ('Reset Atoms Display', self.w.dispResetAtomsDisplay),
            ('Show Invisible Atoms', self.w.dispShowInvisAtoms),
            ('Hide Chunk', self.o.assy.Hide),
            None,
            ('Change Background Color...', self.w.dispBGColor),
         ]

        self.debug_Menu_spec = [
            ('debug: invalidate selection', self.invalidate_selection),
            ('debug: update selection', self.update_selection),
         ]
        
        # Find this redundancy unnecessary; toolbar with these options is available.  mark 060303.
        #self.Menu_spec_control = [
        #    ('Invisible', self.w.dispInvis),
        #    None,
        #    ('Default', self.w.dispDefault),
        #    ('Lines', self.w.dispLines),
        #    ('CPK', self.w.dispCPK),
        #    ('Tubes', self.w.dispTubes),
        #    ('VdW', self.w.dispVdW)]
    
    
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


class selectAtomsMode(selectMode):
    modename = 'SELECTATOMS'
    default_mode_status_text = "Mode: Select Atoms"
    highlight_singlets = False 
        # Don't highlight singlets in selectAtomsMode. Fixes bug 1540. mark 060220.
    hover_highlighting_enabled = env.prefs[selectAtomsModeHighlightingEnabled_prefs_key]
        # Fixes bug 1541.  mark 060220.
    water_enabled = False # Fixes bug 1583. mark 060301.
    selection_filter_enabled = False # mark 060301.
        
    eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]
        
    #def __init__(self, glpane):
    #    selectMode.__init__(self, glpane)
    #    self.w.filterCheckBox.setChecked(0)
            
    def Enter(self): 
        basicMode.Enter(self)
        
        self.o.assy.selectAtoms()
        self.set_selection_filter(0) # disable selection filter (sets current item to "All Elements").  mark 060301.
        # Reinitialize previously picked atoms (ppas).
        self.o.assy.ppa2 = self.o.assy.ppa3 = None
        
        #self.o.assy.permit_pick_atoms() #bruce 050517 revised API of this call
            # permit_pick_atoms() already done in self.o.assy.selectAtoms().  mark 060219.
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
        self.cursor_over_when_LMB_pressed = None
            # <cursor_over_when_LMB_pressed> keeps track of what the cursor was over 
            # when the LMB was pressed, which can be one of:
            #   'Empty Space'
            #   'Picked Atom'
            #   'Unpicked Atom'
            #   'Singlet'
            #   'Bond'
        self.drag_multiple_atoms = False
            # set to True when we are dragging a movable unit of 2 or more atoms.
        self.current_obj = None
            # current_obj is the object under the cursor when the LMB was pressed.
        self.dragobjs = []
            # dragobjs is constructed in atomsSetup() and contains all 
            # the selected atoms (except selected baggage atoms) 
            # that are dragged around as a group in atomsDrag().
            # Selected atoms that are baggage are placed in self.baggage
            # along with non-selected baggage atoms connected to dragobjs.
            # See atomsSetup() for more information.
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
        self.drag_stickiness_limit_exceeded = False
            # used in leftDrag() to determine if the drag stickiness limit was exceeded.
        self.only_highlight_singlets = False
            # when set to Tru, only singlets get highlighted when dragging a singlet.
            # depositMode.singletSetup() sets this to True when dragging a singlet around.
            
    def init_gui(self):
        selectMode.init_gui(self)
        self.w.toolsSelectAtomsAction.setOn(1) # toggle on the "Select Atoms" tools icon
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
        '''
        if self.hover_highlighting_enabled:
            self.update_selatom(event) #bruce 041130 in case no update_selatom happened yet
            # update_selatom() updates self.o.selatom and self.o.selobj.
            # self.o.selatom is either a real atom or a singlet.
            # self.o.selobj can be a bond, and is used in leftUp() to determine if a bond was selected.
            
        # Warning: if there was no GLPane repaint event (i.e. paintGL call) since the last bareMotion,
        # update_selatom can't make selobj/selatom correct until the next time paintGL runs.
        # Therefore, the present value might be out of date -- but it does correspond to whatever
        # highlighting is on the screen, so whatever it is should not be a surprise to the user,
        # so this is not too bad -- the user should wait for the highlighting to catch up to the mouse
        # motion before pressing the mouse. [bruce 050705 comment]
        
            a = self.o.selatom # a "highlighted" atom or singlet
            
            if a is None and self.o.selobj:
                a = self.o.selobj # a "highlighted" bond
            
        else: # No hover highlighting
            a = self.o.assy.findAtomUnderMouse(event, self.water_enabled, singlet_ok = True)
            # Note: findAtomUnderMouse() only returns atoms and singlets, not bonds or jigs.
            # This means that bonds can never be selected when highlighting is turned off.
        return a
            
    def get_real_atom_under_cursor(self, event):
        '''If the object under the cursor is a real atom, return it.  Otherwise, return None.
        '''
        a = self.get_obj_under_cursor(event)
        if isinstance(a, Atom):
            if not a.is_singlet():
                return a
        return None
        
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
                    return env.prefs[bondpointHighlightColor_prefs_key]
            else:
                if self.only_highlight_singlets:
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
                #return HICOLOR_singlet_bond
                print "Error: HICOLOR_singlet_bond no longer used"  # This can be removed soon. mark 060215.
                return None # precaution.  
            else:
                if self.only_highlight_singlets:
                    return None
                if self.o.modkeys == 'Shift+Control': 
                    return darkred # Highlight the bond in darkred if the control key is pressed.
                else:
                    return env.prefs[bondHighlightColor_prefs_key] ## was HICOLOR_real_bond before bruce 050805
        elif isinstance(selobj, Jig): #bruce 050729 bugfix (for some bugs caused by Huaicai's jig-selection code)
            return None # (jigs aren't yet able to draw themselves with a highlight-color)
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

        self.set_cmdname('BuildClick')
        
        self.o.assy.permit_pick_atoms() # Fixes bug 1413, 1477, 1478 and 1479.  Mark 060218.
        self.reset_drag_vars()
        env.history.statusbar_msg(" ") # get rid of obsolete msg from bareMotion [bruce 050124; imperfect #e]
            
        self.LMB_press_event = QMouseEvent(event) # Make a copy of this event and save it. 
            # We will need it later if we change our mind and start selecting a 2D region in leftDrag().
            # Copying the event in this way is necessary because Qt will overwrite <event> later (in 
            # leftDrag) if we simply set self.LMB_press_event = event.  mark 060220.
            
        self.LMB_press_pt, junk = self.o.mousepoints(event, just_beyond = 0.01)
            # <LMB_press_pt> is the position of the mouse when the LMB was pressed. Used in leftDrag().
            
        obj = self.get_obj_under_cursor(event)
            # If highlighting is turned on, get_obj_under_cursor() returns atoms, singlets and bonds (not jigs).
            # If highlighting is turned off, get_obj_under_cursor() returns atoms and singlets (not bonds or jigs).
        
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
            return
            
        if obj is None: # Nothing dragged (or clicked); return.
            return
            
        if isinstance(obj, Bond): # Cursor was over a bond during LMB press event.
            self.bondLeftDrag(event)
            return
            
        if isinstance(obj, Atom) and obj.is_singlet(): # Cursor was over a singlet during LMB press event.
            self.singletDrag(obj, event)
            
        if isinstance(obj, Atom) and not obj.is_singlet(): # Cursor was over a real atom during LMB press event.
            self.atomDrag(obj, event)
        
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
            return
        
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.emptySpaceLeftUp(event)
            return
        
        obj = self.current_obj
            
        if obj is None: # Nothing dragged (or clicked); return.
            return
        
        if self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            event = self.LMB_press_event
            
        if isinstance(obj, Atom) and obj.is_singlet(): # Cursor over a singlet
            self.singletLeftUp(obj, event)
            
        if isinstance(obj, Atom) and not obj.is_singlet(): # Cursor over a real atom
            self.atomLeftUp(obj, event)
            
        if isinstance(obj, Bond):
            self.bondLeftUp(obj, event)
        
        self.baggage = []
        self.current_obj = None #bruce 041130 fix bug 230
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
                # Double-clicking on a singlet should do nothing.
                return
                
            else: # real atom
                if self.o.modkeys == 'Control':
                    self.o.assy.unselectConnected( [ self.obj_doubleclicked ] )
                elif self.o.modkeys == 'Shift+Control':
                    self.o.assy.deleteConnected( self.neighbors_of_last_deleted_atom )
                else:
                    self.o.assy.selectConnected( [ self.obj_doubleclicked ] )
            
        if isinstance(self.obj_doubleclicked, Bond):
            if self.o.modkeys == 'Control':
                self.o.assy.unselectConnected( [ self.obj_doubleclicked.atom1 ] )
            elif self.o.modkeys == 'Shift+Control':
                self.o.assy.deleteConnected( [ self.obj_doubleclicked.atom1, self.obj_doubleclicked.atom2 ] )
            else:
                self.o.assy.selectConnected( [ self.obj_doubleclicked.atom1 ] )

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
            
        basicMode.keyPress(self, key)

        if self.o.mode.modename in ['SELECTATOMS']: 
            # Add the mode name to this list to support filtering using keypresses to select element type.
            if key == Qt.Key_Escape: # Disable the selection filter.  mark 060301.
                self.set_selection_filter(0) # disable selection filter (sets current item to "All Elements").  mark 060301.
                return
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
        #print "set_selection_filter val=",val
        self.w.elemFilterComboBox.setCurrentItem(indx)
        old_filter_enabled = self.selection_filter_enabled
        self.selection_filter_enabled = indx
        if indx:
            if not old_filter_enabled:
                env.history.message("Atoms Selection Filter enabled.")
        else:
            if old_filter_enabled:
                env.history.message("Atoms Selection Filter disabled.")
        self.update_cursor()
            
    def update_cursor_for_no_MB(self):
        '''Update the cursor for 'Select Atoms' mode (selectAtomsMode)
        '''
        #print "selectAtomsMode.update_cursor_for_no_MB(): button=",self.o.button, ", modkeys=", self.o.modkeys
        
        if self.selection_filter_enabled:
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
        
    def makeMenus(self): # added by mark 060303.
        
        self.Menu_spec = [
            ###e these accelerators should be changed to be Qt-official
            # by extending widgets.makemenu_helper to use Qt's setAccel...
            # [bruce 050112]
            # mark 060303. added the following:
            ('Enable Jig Selection',  self.setJigSelectionEnabled, 'checked'), # Always stays checked; bug.  mark 060303.
            None,
            ('Change Background Color...', self.w.dispBGColor),
            ]
        
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
        '''High light atoms or chunks inside ESPImage jigs. '''
        from jigs_planes import ESPImage
            
        if isinstance(grp, ESPImage): 
            grp.highlightAtomChunks()
        elif isinstance(grp, Group):    
            for m in grp.members:
                if isinstance(m, ESPImage):
                    m.highlightAtomChunks()
                elif isinstance(m, Group):
                    self._highlightAtoms(m)
        
                        
    def Draw(self):
        '''Draw model for the select Atom mode'''
        selectMode.Draw(self)
        self._highlightAtoms(self.o.assy.part.topnode)