# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
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

- Ninad 070216 moved selectAtomsMode and selectMolsMode out of selectMode.py 
"""
import sys
import os
import Numeric
from Numeric import dot

from PyQt4.Qt import QLabel
from PyQt4.Qt import QComboBox
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QSize
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QCheckBox

from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glSelectBuffer
from OpenGL.GL import GL_SELECT
from OpenGL.GL import glRenderMode
from OpenGL.GL import glInitNames
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_CLIP_PLANE0
from OpenGL.GL import glClipPlane
from OpenGL.GL import glEnable
from OpenGL.GL import glDisable
from OpenGL.GL import GL_RENDER
from OpenGL.GL import glFlush
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslate
from OpenGL.GL import glPopMatrix

from OpenGL.GLU import gluUnProject

from modes import basicMode
from utilities.Log import orangemsg
from chunk import molecule
import env
from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice
from Plane import Handle
from constants import average_value
from constants import SELSHAPE_RECT

from VQT import V, Q, A, norm, planeXline, ptonline, vlen

from constants import SELSHAPE_LASSO
from constants import SUBTRACT_FROM_SELECTION
from constants import ADD_TO_SELECTION
from constants import START_NEW_SELECTION
from constants import DELETE_SELECTION
from shape import SelectionShape
from bonds import Bond
from debug import print_compact_traceback
from debug import print_compact_stack

from jigs import Jig
from utilities.Log import redmsg
import platform


debug_update_selobj_calls = False # do not commit with true

_count = 0

#bruce 060315 revised DRAG_STICKINESS_LIMIT to be in pixels

##DRAG_STICKINESS_LIMIT = 0.03 # in Angstroms with respect to the front clipping plane.
##    #& To do: Change to pixel units and make it a user pref.  Also consider a different var/pref
##    #& for singlet vs. atom drag stickiness limits. Mark 060213.

DRAG_STICKINESS_LIMIT = 4 # in pixels; reset in each leftDown via a debug_pref
    #& To do: Make it a user pref in the Prefs Dialog.  Also consider a different var/pref
    #& for singlet vs. atom drag stickiness limits. Mark 060213.

_ds_Choice = Choice([0,1,2,3,4,5,6,7,8,9,10], defaultValue = DRAG_STICKINESS_LIMIT)

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

    def __init__(self, glpane): #bruce 070412
        basicMode.__init__(self, glpane)
        self.get_smooth_reshaping_drag() # exercise debug_pref to make sure it's always in the menu.
        self.get_use_old_safe_drag_code() # ditto
        return

    # init_gui handles all the GUI display when entering a mode    
    def init_gui(self):
        pass # let the subclass handle everything for the GUI - Mark [2004-10-11]

    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        pass # let the subclass handle everything for the GUI - Mark [2004-10-11]
    
    def reset_drag_vars(self):
        """This resets (or initializes) per-drag instance variables, and is called in Enter and at beginning of leftDown.
        [Subclasses can override this to add variables, but those methods should call this version too.]
        """
        #WARNING: This method has been duplicated 
        #in the subclass (selectAtomsMode.py) This needs cleanup . 
        #Note that this duplication is NOT exact 
        #See selectAtomsMode.reset_drag_vars for further details. 
          
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
            # [it is set to that obj by objectSetup, and set back to None by some, but not all,
            #  mousedrag and mouseup methods. It's used by leftDrag and leftUp to decide what to do,
            #  to what object. When a drag_handler is in use, I think [bruce 060728] this will be the
            #  drag_handler (not the selobj that it is for), but I'll still have a separate self.drag_handler
            #  attr to also record that. One of these is redundant, but this will most clearly separate old and new code,
            #  while ensuring that if old code tests current_obj it won't see a class it thinks it knows how to handle
            #  (even if I sometimes use drag_handlers to drag old specialcase object classes), and won't see None.
            #  (Other possibilities would be to not have self.drag_handler at all, and/or to let this be the selobj
            #   that a drag_handler was made for; these seem worse now, but I mention them in case I need to switch to them.)
            #  Maybe we'll need some uses of current_obj to filter it though a self method which converts drag_handlers
            #  back to their underlying objects (i.e. the selobj that they were made from or made for). (Or have a .selobj attr.)
            #  #####@@@@@ [bruce 060728 comment]]
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
            # [bruce 060727 comments: it seems to mean "was self.current_obj clicked, but not (yet) dragged",
            #  and its basic point seems to be to let leftUp decide whether to select the object,
            #  i.e. to not require all drags of objects to select them.
            #    Note: it is set back to False only by class-specific drag methods, not by leftDrag itself;
            #  similarly, it is used only in class-specific mouseup methods, not by leftUp itself.
            #    For drag_handlers, it looks like we should treat all drag_handler uses as another object type,
            #  so we should set this in the same way in the drag_handler-specific methods.
            #  Hmm, maybe we want separate submethods like dragHandlerLeft*, just as for Atom/Bond/Jig. #####@@@@@
            # ]
        self.obj_doubleclicked = None
            # used by leftDouble() to determine the object that was double clicked.
            # [bruce 060727 comments: This is the same object found by the first click's leftDown -- mouse motion
            #  is not checked for! That might be a bug -- if the mouse slipped off this object, it might be better
            #  to discard the entire drag (and a stencil buffer test could check for this, without needing glSelect).
            #  At least, this is always the correct object if anything is.
            #    It is used in obj-class-specific leftDown methods, and assumed to be an object of the right class
            #  (which seems ok, since leftDouble uses isinstance on it to call one of those methods).
            #    If a drag_handler is in use, this should probably be the drag_handler itself
            #  (no current code compares it to any selobj -- it only isinstances it to decide what drag code to run),
            #  but if some Atoms/Bonds/Jigs ever use self as a drag_handler, our isinstance tests on this
            #  will be problematic; we may need an "are you acting as a drag_handler" method instead. #####@@@@@
            # ]
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
        self.drag_handler = None #bruce 060725
        return
    
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
            # REVIEW (possible optim): can gl_update_highlight be extended to cover this? [bruce 070626]
        return
        
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
            # REVIEW (possible optim): can we make gl_update_highlight (or something like it) cover this?
            # Note that both the curve itself, and what's selected, are changing. [bruce 070626]
        
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
        if farQ or vlen( dragpoint - apos0 ) > a.max_pixel_radius():
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
            self.smooth_reshaping_drag = self.get_smooth_reshaping_drag() #bruce 070412
            self.dragatoms, self.baggage, self.dragchunks = self.get_dragatoms_and_baggage()
                # if no atoms in alist, dragatoms and baggage are empty lists, which is good.
            self.drag_multiple_atoms = True
            self.maybe_use_bc = debug_pref("use bc to drag mult?", Choice_boolean_False) #bruce 060414
            
        # dragjigs contains all the selected jigs.
        self.dragjigs = self.o.assy.getSelectedJigs()

    def OLD_get_dragatoms_and_baggage(self): # by mark. later optimized and extended by bruce, 060410. Still used, 070413.
        """#doc... return dragatoms, baggage, dragchunks; look at self.smooth_reshaping_drag [nim];
        how atoms are divided between dragatoms & baggage is arbitrary and is not defined.
        [A rewrite of callers would either change them to treat those differently and change
        this to care how they're divided up (requiring a decision about selected baggage atoms),
        or remove self.baggage entirely.]
        """
        #bruce 060410 optimized this; it had a quadratic algorithm (part of the cause of bugs 1828 / 1438), and other slownesses.
        # The old code was commented out for comparison [and later, 070412, was removed].
        #
        # Note: as of 060410, it looks like callers only care about the total set of atoms in the two returned lists,
        # not about which atom is in which list, so the usefulness of having two lists is questionable.
        # The old behavior was (by accident) that selected baggage atoms end up only in the baggage list, not in dragatoms.
        # This was probably not intended but did not matter at the time.
        # The dragchunks optimization at the end [060410] changes this by returning all atoms in dragatoms or dragchunks,
        # none in baggage. The new smooth reshaping feature [070412] may change this again.
        # WARNING: THIS IS NOT USED for smooth reshaping; see (non-OLD) get_dragatoms_and_baggage for that.
        
        dragatoms = []
        baggage = []
        
        selatoms = self.o.assy.selatoms
        
        # Accumulate all the baggage from the selected atoms, which can include
        # selected atoms if a selected atom is another selected atom's baggage.
        # BTW, it is not possible for an atom to end up in self.baggage twice.
        
        for at in selatoms.itervalues():
            bag, nbag_junk = at.baggage_and_other_neighbors()
            baggage.extend(bag) # the baggage we'll keep.

        bagdict = dict([(at.key, None) for at in baggage])
                
        # dragatoms should contain all the selected atoms minus atoms that are also baggage.
        # It is critical that dragatoms does not contain any baggage atoms or they 
        # will be moved twice in drag_selected_atoms(), so we remove them here.
        for key, at in selatoms.iteritems():
            if key not in bagdict: # no baggage atoms in dragatoms.
                dragatoms.append(at)
                
        # Accumulate all the nonbaggage bonded to the selected atoms.
        # We also need to keep a record of which selected atom belongs to
        # each nonbaggage atom.  This is not implemented yet, but will be needed
        # to get drag_selected_atoms() to work properly.  I'm commenting it out for now.
        # mark 060202.
        ## [code removed, 070412]
        

        #bruce 060410 new code: optimize when all atoms in existing chunks are being dragged.
        # (##e Soon we hope to extend this to all cases, by making new temporary chunks to contain dragged atoms,
        #  invisibly to the user, taking steps to not mess up existing chunks re their hotspot, display mode, etc.)
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
        
        return dragatoms, baggage, dragchunks  # return from OLD_get_dragatoms_and_baggage; this routine will be removed later
        
    def get_dragatoms_and_baggage(self):
        """#doc... return dragatoms, baggage, dragchunks; look at self.smooth_reshaping_drag [nim];
        how atoms are divided between dragatoms & baggage is arbitrary and is not defined.
        [A rewrite of callers would either change them to treat those differently and change
        this to care how they're divided up (requiring a decision about selected baggage atoms),
        or remove self.baggage entirely.]
        """
        #bruce 060410 optimized this; it had a quadratic algorithm (part of the cause of bugs 1828 / 1438), and other slownesses.
        # The old code was commented out for comparison [and later, 070412, was removed].
        # [Since then, it was totally rewritten by bruce 070412.]
        #
        # Note: as of 060410, it looks like callers only care about the total set of atoms in the two returned lists,
        # not about which atom is in which list, so the usefulness of having two lists is questionable.
        # The old behavior was (by accident) that selected baggage atoms end up only in the baggage list, not in dragatoms.
        # This was probably not intended but did not matter at the time.
        # The dragchunks optimization at the end [060410] changes this by returning all atoms in dragatoms or dragchunks,
        # none in baggage. The new smooth reshaping feature [070412] may change this again.

        if not self.smooth_reshaping_drag and self.get_use_old_safe_drag_code():
            # by default, for now: for safety, use the old drag code, if we're not doing a smooth_reshaping_drag.
            # After FNANO I'll change the default for use_old_safe_drag_code to False. [bruce 070413]
            return self.OLD_get_dragatoms_and_baggage()

        print "fyi: using experimental code for get_dragatoms_and_baggage; smooth_reshaping_drag = %r" % self.smooth_reshaping_drag
            # Remove this print after FNANO when this code becomes standard, at least for non-smooth_reshaping_drag case.
            # But consider changing the Undo cmdname, drag -> smooth drag or reshaping drag. #e

        # rewrite, bruce 070412, for smooth reshaping and also for general simplification:
        # [this comment and the partly redundant ones in the code will be merged later]
        # - treat general case as smooth reshaping with different (trivial) motion-function
        #   (though we'll optimize for that) -- gather the same setup data either way.
        #   That will reduce bug-differences between smooth reshaping and plain drags,
        #   and it might help with other features in the future, like handling baggage better
        #   when there are multiple selected atoms.
        # - any baggage atom B has exactly one neighbor S, and if that neighbor is selected
        #   (which is the only time we might think of B as baggage here), we want B to move
        #   with S, regardless of smooth reshaping which might otherwise move them differently.
        #   This is true even if B itself is selected. So, for baggage atoms (even if selected)
        #   make a dict which points them to other selected atoms. If we find cycles in that,
        #   those atoms must be closed for selection (ie not indirectly bonded to unselected atoms,
        #   which is what matters for smooth reshaping alg) or can be treated that way,
        #   so move those atoms into a third dict for moving atoms which are not connected to
        #   unmoving atoms. (These never participate in smooth reshaping -- they always move
        #   with the drag.)
        # - the other atoms which move with the drag are the ones we find later with N == N_max,
        #   and the other ones not bonded to unselected nonbaggage atoms, and all of them if
        #   we're not doing reshaping drag.
        # - then for all atoms which move with the drag (including some of the baggage,
        #   so rescan it to find those), we do the dragchunk optim;
        #   for the ones which move, but not with the drag, we store their motion-offset-ratio
        #   in a dict to be used during the drag (or maybe return it and let caller store it #k).
        #
        # - I think all the above can be simplified to the following:
        #   - expand selatoms to include baggage (then no need to remember which was which,
        #     since "monovalent" is good enough to mean "drag with neighbor", even for non-baggage)
        #   - point monovalent atoms in that set, whose neighbors are in it, to those neighbors
        #     (removing them from that set) (permitting cycles, which are always length 2)
        #     (during the drag, we'll move them with neighbors, then in future correct
        #      their posn for the motion of other atoms around those neighbors, as is now only done
        #      in single-atom dragging)
        #   - analyze remaining atoms in set for closeness (across bonds) to unselected atoms
        #     (permitting infinite dist == no connection to them)
        #   - then sort all the atoms into groups that move with the same offset, and find whole chunks
        #     in those groups (or at least in the group that moves precisely with the drag). (In future
        #     we'd use the whole-chunk and borrowerchunk optims (or equiv) for the slower-moving groups too.
        #     Even now, it'd be easy to use whole-chunk optim then, but only very rarely useful, so don't bother.)
        #
        # - finally, maybe done in another routine, selected movable jigs move in a way that depends on how
        #   their atoms move -- maybe their offset-ratio is the average of that of their atoms.
        
        # Ok, here we go:
        #   - expand selatoms to include baggage (then no need to remember which was which,
        #     since "monovalent" is good enough to mean "drag with neighbor", even for non-baggage)

        selatoms = self.o.assy.selatoms # maps atom.key -> atom
            # note: after this, we care only which atoms are in selatoms, not whether they're selected --
            # in other words, you could pass some other dict in place of selatoms if we modified the API for that,
            # and no code after this point would need to change.
        atoms_todo = dict(selatoms) # a copy which we'll modify in the following loop,and later;
            # in general it contains all moving atoms we didn't yet decide how to handle.
        monovalents = {} # maps a monvalent atom -> its neighbor, starting with baggage atoms we find
        boundary = {} # maps boundary atoms (selected, with unselected nonbaggage neighbor) to themselves
        ## unselected = {} # maps an unselected nonbaggage atom (next to one or more selected ones) to an arbitrary selected one
        for atom in selatoms.itervalues():
            baggage, nonbaggage = atom.baggage_and_other_neighbors()
            for b in baggage:
                monovalents[b] = atom # note: b (I mean b.key) might also be in atoms_todo
            for n in nonbaggage:
                if n.key not in selatoms:
                    ## unselected[n] = atom
                    boundary[atom] = atom
                    break
            continue
        del selatoms
        # note: monovalents might overlap atoms_todo; we'll fix that later.
        # also it is not yet complete, we'll extend it later.

        #   - point monovalent atoms in that set (atoms_todo), whose neighbors are in it, to those neighbors
        #     (removing them from that set) (permitting cycles, which are always length 2 -- handled later ###DOIT)
        for atom in atoms_todo.itervalues():
            if len(atom.bonds) == 1:
                bond = atom.bonds[0]
                if bond.atom1.key in atoms_todo and bond.atom2.key in atoms_todo:
                    monovalents[atom] = bond.other(atom)
        for b in monovalents:
            atoms_todo.pop(b.key, None) # make sure b is not in atoms_todo, if it ever was

        len_total = len(monovalents) + len(atoms_todo) # total number of atoms considered, used in assertions
        
        #   - analyze remaining atoms in set (atoms_todo) for closeness (across bonds) to unselected atoms
        #     (permitting infinite dist == no connection to them)
        # Do this by transclosing boundary across bonds to atoms in atoms_todo.
        layers = {} # will map N to set-of-atoms-with-N (using terminology of smooth-reshaping drag proposal)
        from state_utils import transclose
        def collector( atom, dict1):
            """add neighbors of atom which are in atoms_todo (which maps atom keys to atoms)
            to dict1 (which maps atoms to atoms)."""
            for n in atom.neighbors():
                if n.key in atoms_todo:
                    dict1[n] = n
            return
        def layer_collector( counter, set):
            layers[counter] = set
            ## max_counter = counter # calling order is guaranteed by transclose
                # no good namespace to store this in -- grab it later
            return
        layers_union = transclose( boundary, collector, layer_collector)
        max_counter = len(layers)

        # Now layers_union is a subset of atoms_todo, and is the union of all the layers;
        # the other atoms in atoms_todo are the ones not connected to unselected nonbaggage atoms.
        # And that's all moving atoms except the ones in monovalents.

        for atom in layers_union:
            atoms_todo.pop(atom.key) # this has KeyError if atom is not there, which is a good check of the above alg.

        unconnected = {} # this will map atoms to themselves, which are not connected to unselected atoms.
            # note that we can't say "it's atoms_todo", since that maps atom keys to atoms.
            # (perhaps a mistake.)
        for atom in atoms_todo.itervalues():
            unconnected[atom] = atom
        ## del atoms_todo
            ## SyntaxError: can not delete variable 'atoms_todo' referenced in nested scope
            # not even if I promise I'll never use one of those references again? (they're only in the local function defs above)
        atoms_todo = -1111 # error if used as a dict; recognizable/searchable value in a debugger

        assert len(monovalents) + len(layers_union) + len(unconnected) == len_total
        assert len(layers_union) == sum(map(len, layers.values()))

        # Warning: most sets at this point map atoms to themselves, but monovalents maps them to their neighbors
        # (which may or may not be monovalents).

        # Now sort all the atoms into groups that move with the same offset, and find whole chunks
        # in those groups (or at least in the group that moves precisely with the drag).
        # First, sort monovalents into unconnected ones (2-cycles, moved into unconnected)
        # and others (left in monovalents).

        cycs = {}
        for m in monovalents:
            if monovalents[m] in monovalents:
                assert monovalents[monovalents[m]] is m
                cycs[m] = m
                unconnected[m] = m
        for m in cycs:
            monovalents.pop(m)
        del cycs
        assert len(monovalents) + len(layers_union) + len(unconnected) == len_total # again, now that we moved them around

        # Now handle the non-smooth_reshaping_drag case by expressing our results from above
        # in terms of the smooth_reshaping_drag case.

        if not self.smooth_reshaping_drag:
            # throw away all the work we did above! (but help to catch bugs in the above code, even so)
            unconnected.update(layers_union)
            for atom in monovalents:
                unconnected[atom] = atom
            assert len(unconnected) == len_total
            layers_union = {}
            layers = {}
            monovalents = {}
            max_counter = 0

        # Now we'll move unconnected and the highest layer (or layers?) with the drag,
        # move the other layers lesser amounts, and move monovalents with their neighbors.
        # Let's label all the atoms with their N, then pull that back onto the monovalents,
        # and add them to a layer or unconnected as we do that, also adding a layer to unconnected
        # if it moves the same. But the code is simpler if we move unconnected into the highest layer
        # instead of the other way around (noting that maybe max_counter == 0 and layers is empty).
        # (unconnected can be empty too, but that is not hard to handle.)

        labels = {}
        self.smooth_Max_N = max_counter # for use during the drag
        self.smooth_N_dict = labels # ditto (though we'll modify it below)

        if not max_counter:
            assert not layers
            layers[max_counter] = {}
        layers[max_counter].update(unconnected)
        del unconnected

        assert max_counter in layers
        for N, layer in layers.iteritems():
            assert N <= max_counter
            for atom in layer:
                labels[atom] = N
        N = layer = None
        del N, layer

        for m, n in monovalents.iteritems():
            where = labels[n]
            labels[m] = where
            layers[where][m] = m
        del monovalents

        # Now every atom is labelled and in a layer. Move the fast ones out, keep the slower ones in layers.
        # (Note that labels itself is a dict of all the atoms, with their N -- probably it could be our sole output
        #  except for the dragchunks optim. But we'll try to remain compatible with the old API. Hmm, why not return
        #  the slow atoms in baggage and the fast ones in dragatoms/dragchunks?)

        fastatoms = layers.pop(max_counter)

        slowatoms = {}
        for layer in layers.itervalues():
            slowatoms.update(layer)
        layer = None
        del layer
        layers = -1112
        # slowatoms is not further used here, just returned

        assert len_total == len(fastatoms) + len(slowatoms)
        
        # Now find whole chunks in the group that moves precisely with the drag (fastatoms).
        # This is a slightly modified version of:
        #bruce 060410 new code: optimize when all atoms in existing chunks are being dragged.
        # (##e Soon we hope to extend this to all cases, by making new temporary chunks to contain dragged atoms,
        #  invisibly to the user, taking steps to not mess up existing chunks re their hotspot, display mode, etc.)
        atomsets = {} # id(mol) -> (dict from atom.key -> atom) for dragged atoms in that mol
        def doit(at):
            mol = at.molecule
            atoms = atomsets.setdefault(id(mol), {}) # dragged atoms which are in this mol, so far, as atom.key -> atom
            atoms[at.key] = at # atoms serves later to count them, to let us make fragments, and to identify the source mol
        for at in fastatoms:
            doit(at)
        dragatoms = []
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

        assert len(fastatoms) == len(dragatoms) + sum([len(chunk.atoms) for chunk in dragchunks])
        
        res = (dragatoms, slowatoms.values(), dragchunks) # these are all lists

        return res # from (NEW) get_dragatoms_and_baggage
        
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
    #   [later 070412: maybe because the methods calling it are themselves only called from selectAtomsMode? it looks that way anyway]
    #   [later 070412: ###WARNING: in Qt3, reset_drag_vars is defined in selectAtomsMode, but in Qt4, it's defined in selectMode.]
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
        # WARNING: this (and quite a few other methods) is probably only called (ultimately) from event handlers
        # in selectAtomsMode, and probably uses some attrs of self that only exist in that mode. [bruce 070412 comment]

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
        for at in self.dragatoms:
            at.setposn(at.posn()+offset)
        
        # Move baggage (or slow atoms, in smooth-reshaping drag case)
        if not self.smooth_reshaping_drag:
            for at in self.baggage:
                at.setposn(at.posn() + offset)
        else:
            # kluge: in this case, the slow-moving atoms are the ones in self.baggage.
            # We should probably rename self.baggage or not use the same attribute for those.
            for at in self.baggage:
                f = self.offset_ratio(at, assert_slow = True)
                at.setposn(at.posn() + f * offset)
            pass

        # Move chunks. [bruce 060410 new feature, for optimizing moving of selected atoms, re bugs 1828 / 1438]
        # Note, these might be chunks containing selected atoms (and no unselected atoms, except baggage), not selected chunks.
        # All that matters is that we want to move them as a whole (as an optimization of moving their atoms individually).
        # Note, as of 060414 one of them might be a BorrowerChunk.
        for ch in self.dragchunks:
            ch.move(offset)
        
        return

    def offset_ratio(self, atom, assert_slow = False): #bruce 070412
        "When self.smooth_reshaping_drag, return the drag_offset_ratio for any atom (0 if we're not dragging it)."
        N = float(self.smooth_N_dict.get(atom, 0))
            # If found: from 1 to Max_N
        Max_N = self.smooth_Max_N # 0 or more (integer)
        if Max_N == 0:
            R = 0; f = 1
        else:
            R = (Max_N - N)/Max_N # ranges from just above 0 to just below 1, in slow case, or can be exact 0 or 1 in general
            f = (1-R**2)**2 # could be precomputed for each N, but that's probably not a big optim
        if assert_slow:
            assert 1 <= N < Max_N
            assert 0 < R < 1, "why is R == %r not strictly between 0 and 1? N = %r, Max_N = %r, atom = %r" % \
                   (R, N, Max_N, atom)
            assert 0 < f < 1
        else:
            assert 0 <= N <= Max_N
            assert 0 <= R <= 1
            assert 0 <= f <= 1
        return f

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
        self.o.gl_update() # REVIEW (possible optim): can gl_update_highlight be extended to cover this? [bruce 070626]
        return
    
    def singletSetup(self, s):
        pass
        
    def singletDrag(self, s, event):
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
                # REVIEW (possible optim): can we (or some client code) make gl_update_highlight cover this? [bruce 070626]
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
                    # REVIEW (possible optim): can we make gl_update_highlight cover this? [bruce 070626]
                # lots of other stuff done by other leftUp methods here? #####@@@@@
            pass
        except:
            print_compact_traceback("bug: exception in dragHandlerLeftUp ignored: ")
        pass
        
    def dragHandlerLeftDouble(self, drag_handler, event): # never called as of 070324; see also testmode.leftDouble
        if env.debug():
            print "debug fyi: dragHandlerLeftDouble is nim"
        return

    #Reference Geometry handler helper methods
    #@@ This and jig helper methods need to be combined. -- ninad 20070516
    def geometryLeftDown(self, geom, event):    
        self.jigLeftDown(geom, event)
    
    def geometryLeftUp(self, geom, event):
        self.jigLeftUp(geom, event)
    
    def geometryLeftDrag(self, geom, event):
        geometry_NewPt = self.dragto( self.jig_MovePt, event)
        # Print status bar msg indicating the current move offset.
        if 1:
            self.moveOffset = geometry_NewPt - self.jig_StartPt
            msg = "Offset: [X: %.2f] [Y: %.2f] [Z: %.2f]" % (self.moveOffset[0], self.moveOffset[1], self.moveOffset[2])
            env.history.statusbar_msg(msg)
            
        offset = geometry_NewPt - self.jig_MovePt         
        geom.move(offset)                  
        self.jig_MovePt = geometry_NewPt        
        self.current_obj_clicked = False 
        self.o.gl_update()
        pass
                
    
    def handleLeftDown(self, hdl, event): 
        self.handle_MovePt = hdl.parent.getHandlePoint(hdl, event)
        self.handleSetUp(hdl)
    
    def handleLeftDrag(self, hdl, event):        
        hdl.parent.resizeGeometry(hdl, event)
        handle_NewPt = hdl.parent.getHandlePoint(hdl, event)
        self.handle_MovePt = handle_NewPt
        self.current_obj_clicked = False
        self.o.gl_update()
                           
    def handleLeftUp(self, hdl, event):
        pass
    
    def handleSetUp(self, hdl):
        self.objectSetup(hdl)
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

        self.smooth_reshaping_drag = self.get_smooth_reshaping_drag() #bruce 070412
        
        self.dragatoms, self.baggage, self.dragchunks = self.get_dragatoms_and_baggage()
            # if no atoms are selected, dragatoms and baggage are empty lists, which is good.
            
        # dragjigs contains all the selected jigs.
        self.dragjigs = self.o.assy.getSelectedJigs()

    def get_smooth_reshaping_drag(self): #bruce 070412; implement "smooth-reshaping drag" feature
        res = debug_pref("Drag reshapes selected atoms?", #bruce 070525 shortened text (it made entire menu too wide)
                         Choice_boolean_False,
                         prefs_key = '_debug_pref_key:Drag reshapes selected atoms when bonded to unselected atoms?',
                         non_debug = True )
        return res

    def get_use_old_safe_drag_code(self): #bruce 070413
        res = debug_pref("use old safe drag code, when not reshaping?",
                         Choice_boolean_True, ###e change this default to False (and change the prefs key) after FNANO
                         prefs_key = True, non_debug = True )
        return res
        
        
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
        for j in self.dragjigs:
            if self.smooth_reshaping_drag:
                # figure out a modified offset by averaging the offset-ratio for this jig's atoms
                ratio = average_value(map(self.offset_ratio, j.atoms), default = 1.0)
                offset = offset * ratio # not *=, since it's a mutable Numeric array!
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
##            for a in j.atoms:
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
        self.o._setup_projection( glselect = current_glselect) 
        
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
            TEST_PYREX_OPENGL = debug_pref("TEST_PYREX_OPENGL", Choice([0,1,2]))
            # uncomment this line to set it in the old way:
            ## TEST_PYREX_OPENGL = 1
        if TEST_PYREX_OPENGL:
            try:
                print_compact_stack("selectMode Draw: " )###
                ### BUG: if import quux fails, we get into some sort of infinite loop of Draw calls. [bruce 070917 comment]
                
                #self.w.win_update()
##                sys.path.append("./experimental/pyrex-opengl") # no longer needed here -- always done in drawer.py
                binPath = os.path.normpath(os.path.dirname(os.path.abspath(sys.argv[0])) + '/../bin')
                if binPath not in sys.path:
                    sys.path.append(binPath)
                import quux
                if "experimental" in os.path.dirname(sys.modules['quux'].__file__):
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
