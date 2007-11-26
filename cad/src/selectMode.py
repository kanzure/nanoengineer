# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
selectMode.py -- Select Chunks and Select Atoms modes,
also used as superclasses for some other modes

$Id$

Some things that need cleanup in this code [bruce 060721 comment]: ####@@@@

- redundant use of glRenderMode (see comment where that is used)

- division between selectMode and selectAtomsMode

- drag algorithms for various object types and modifier keys are split over
lots of methods with lots of common but not identical code. For example, a
set of atoms and jigs can be dragged in the same way, by two different
pieces of code depending on whether an atom or jig in the set was clicked
on. If this was cleaned up, so that objects clicked on would answer
questions about how to drag them, and if a drag_handler object was created
to handle the drag (or the object itself can act as one, if only it is
dragged and if it knows how), the code would be clearer, some bugs would be
easier to fix, and some NFRs easier to implement. [bruce 060728 -- I'm
adding drag_handlers for use by new kinds of draggable or buttonlike things
(only in selectAtoms mode and subclasses), but not changing how old dragging
code works.]

- Ninad 070216 moved selectAtomsMode and selectMolsMode out of selectMode.py 

"""
import sys
import os
import Numeric
from Numeric import dot

from OpenGL.GL import GL_CLIP_PLANE0
from OpenGL.GL import GL_DEPTH_COMPONENT
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import GL_RENDER
from OpenGL.GL import GL_SELECT
from OpenGL.GL import GL_STENCIL_INDEX
from OpenGL.GL import GL_TRUE
from OpenGL.GL import glClipPlane
from OpenGL.GL import glColorMask
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import glFlush
from OpenGL.GL import glInitNames
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glReadPixelsf
from OpenGL.GL import glReadPixelsi
from OpenGL.GL import glRenderMode
from OpenGL.GL import glSelectBuffer
from OpenGL.GL import glTranslate

from OpenGL.GLU import gluProject
from OpenGL.GLU import gluUnProject

from constants import GL_FAR_Z
from constants import SELSHAPE_RECT
from constants import SELSHAPE_LASSO
from constants import SUBTRACT_FROM_SELECTION
from constants import ADD_TO_SELECTION
from constants import START_NEW_SELECTION
from constants import DELETE_SELECTION

from constants import black

from modes import basicMode

from utilities.Log import redmsg

import env
from debug_prefs import debug_pref
from debug_prefs import Choice

from VQT import V, A, vlen

from shape import SelectionShape
from bonds import Bond
from chem  import Atom 
from jigs  import Jig

from debug import print_compact_traceback
from debug import print_compact_stack

from prefs_constants import bondHighlightColor_prefs_key
from prefs_constants import deleteBondHighlightColor_prefs_key

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
    # (ideally, clean up this pref code a lot by not passing DRAG_STICKINESS_LIMIT
    # as an arg to the subr that uses it)
    # we do this early so the debug_pref is visible in the debug menu before
    # entering selectAtomsMode.

# ==

class selectMode(basicMode):
    """
    Superclass for Select Chunks, Select Atoms, Build, and other modes.
    """
    # Warning: some of the code in this superclass is probably only used in
    # selectAtomsMode and its subclasses, but it's not clear exactly which
    # code this applies to. [bruce 060721 comment]

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

    water_enabled  = None # see self.update_selobj for a detailed comment

    def __init__(self, glpane): #bruce 070412
        basicMode.__init__(self, glpane)        
        return

    # init_gui handles all the GUI display when entering a mode    
    def init_gui(self):
        pass # let the subclass handle everything for the GUI - Mark [2004-10-11]

    def connect_or_disconnect_signals(self, connect):
        """
	Subclasses should override this method
	"""
        pass

    # restore_gui handles all the GUI display when leaving this mode [mark 041004]
    def restore_gui(self):
        pass # let the subclass handle everything for the GUI - Mark [2004-10-11]


    def reset_drag_vars(self):
        """
        This resets (or initializes) per-drag instance variables, and is called 
        in Enter and at beginning of leftDown. Subclasses can override this 
        to add variables, but those methods should call this version too.
        @see L{selectAtomsMode.reset_drag_vars}
        """        
        #IDEALLY(what we should impelment in future) -- 
        #in each class it would reset only that class's drag vars 
        #(the ones used by methods of that class, whether or not 
        #those methods are only called in a subclass, but not the 
        #ones reset by the superclass version of reset_drag_vars), 
        #and in  the subclass it would call the superclass version
        #rather than  resetting all or mostly the same vars. 

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
        self.maybe_use_bc = False
            # whether to use the BorrowerChunk optimization for the current
            # drag (experimental) [bruce 060414]
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
            # [update bruce 071121: this is only used in selectAtomsMode, so it
            #  should be moved there. Maybe the same is true for other variables
            #  here?]
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

    def bareMotion(self, event): #bruce 050610 revised this
        """
        called for motion with no button down
        [should not be called otherwise -- call update_selatom
         or update_selobj directly instead]
        """
        # The mouse_exceeded_distance() conditional below is a "hover highlighting" optimization. 
        # It works by returning before calling update_selobj() if the mouse is moving fast. 
        # This reduces unnecessary highlighting of objects whenever the user moves the cursor 
        # quickly across the GLPane. In many cases, this unnecessary highlighting degrades 
        # interactive responsiveness and can also cause the user to select the wrong objects (i.e. atoms), 
        # especially in large models.
        #
        # One problem with this approach (pointed out by Bruce) happens when the user moves the
        # cursor quickly from one object and suddenly stops on another object, expecting it (the 2nd 
        # object) to be highlighted. Since bareMotion() is only called when the mouse is moving, and the
        # distance between the last two mouse move events is far, mouse_exceed_distance() will 
        # return True. In that case, update_selobj() will not get called and the object under the cursor 
        # will never get highlighted unless the user jiggles the mouse slightly. To address this issue, 
        # a GLpane timer was implemented. The timer calls bareMotion() whenever it expires and the 
        # cursor hasn't moved since the previous timer event. For more details, read the docstring for 
        # GLPane.timerEvent().
        if self.mouse_exceeded_distance(event, 1):
            return

        self.update_selobj(event)
        # note: this routine no longer updates glpane.selatom. For that see
        # self.update_selatom().
        ###e someday, if new or prior selobj asks for it (by defining certain
        # methods), we'd tell it about this bareMotion and about changes in
        # selobj. [bruce 060726]
        return

    # == Selection Curve helper methods

    def select_2d_region(self, event):
        """
        Start 2D selection of a region.
        """
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
        """
        Start a new selection rectangle/lasso.
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
        """
        Add another line segment to the current selection curve.
        """
        if not self.picking:
            return

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
            # REVIEW (possible optim): can gl_update_highlight be extended to
            # cover this? [bruce 070626]
        return

    def end_selection_curve(self, event):
        """
        Close the selection curve and do the selection.
        """
        if not self.picking:
            return
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
            # (for debugging purposes, it's sometimes useful to not reset 
            #  selCurve_List here,
            #  so you can see it at the same time as the selection it caused.)

        self.w.win_update()
            # REVIEW (possible optim): can we make gl_update_highlight
            # (or something like it) cover this?
            # Note that both the curve itself, and what's selected,
            # are changing. [bruce 070626]

    # == End of Selection Curve helper methods

    # == Empty Space helper methods

    #& The Empty Space, Atom, Bond and Singlet helper methods should probably be
    #& moved to selectAtomsMode.  I put them here because I think there is a 
    #& good chance that we'll allow intermixing of atoms, chunks and jigs 
    #&(and other stuff) in any mode. Mark 060220.

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

    def doObjectSpecificLeftDown(self, obj, event):
        """
	Call objectLeftDown methods depending on the object instance. 
	@param obj: object under consideration
	@type  obj: instance 
	@param event: Left down mouse event 
	@type  event: QMouseEvent instance
	"""
                
        if isinstance(obj, Atom) and obj.is_singlet(): 
            self.singletLeftDown(obj, event)# Cursor over a singlet               
        elif isinstance(obj, Atom) and not obj.is_singlet(): 
            self.atomLeftDown(obj, event)   # Cursor over a real atom
        elif isinstance(obj, Bond) and not obj.is_open_bond(): 
            self.bondLeftDown(obj, event)   #Cursor over a bond.
        elif isinstance(obj, Jig): 
            self.jigLeftDown(obj, event)    #Cursor over a jig.
        else: 
            # Cursor is over something else other than an atom, singlet or bond. 
            # (should be handled in caller)
            pass

    def doObjectSpecificLeftUp(self, obj, event):
        """
	Call objectLeftUp methods depending on the object instance. 
	@param obj: object under consideration
	@type  obj: instance 
	@param event: Left Up mouse event 
	@type  event: QMouseEvent instance
	"""
                
        #This flag initially gets set in selectMode.objectSetup. Then, 
        #if the object is being dragged, the value is reset to False in 
        #the object specific drag method  . FYI: The comment in 
        #selectMode.objectSetup suggests the this flag should not be set in 
        #class.leftDrag method. (but instead object specific left drag) 
        #So lets set that flag up in the method 
        #selectMode.doObjectSpecificLeftDrag. Note that this method is 
        #overridden in subclasses, so make sure to either set that flag in 
        #those methods or always call the superclass method at the beginning. 
        # In case of selectMolsMode, the 'objects' are 
        # really the  selectedMovable. so it makes sense to set it in 
        #selectMolsMode.pseudoMoveModeLeftDrag or call doObjectSpecificLeftDrag 
        #somewhere -- Ninad 2007-11-15
        
        #UPDATE 2007-11-15:
        #The self.current_obj_clicked is not valid for  Singlets (bond 
        #points) because singlet dragging and then doing left up actually forms 
        #a bond. So It is important to continue down this method for that
        #condition even if self.current_obj_clicked is False. Otherwise bonds 
        # won't be formed....Then should this check be done in each of the 
        #objectLeftUp methods? But that would be too many methods in various 
        #subclasses and it may cause bugs if someone forgets to add this check.
                
        if not self.current_obj_clicked:
            if isinstance(obj, Atom) and obj.is_singlet():
                pass
            else:
                return
          
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

    def doObjectSpecificLeftDrag(self, obj, event):
        """
	Call objectLeftDrag methods depending on the object instance.
	Default implementation only sets flag self.current_obj_clicked to False.
        Subclasses should make sure to either set that flag in 
        #those methods or always call the superclass method at the beginning. 
        
	@param obj: object under consideration. 
	@type  obj: instance 
	@param event: Left drag mouse event 
	@type  event: QMouseEvent instance
	@see: selectAtomsMode.doObjectSpecificLeftDrag
        @see: self.doObjectSpecificLeftUp, self.objectSetup for comments
	"""
        #current object is not clicked but is dragged. Important to set this 
        #flag. See self.doObjectSpecificLeftUp for more comments
        self.current_obj_clicked = False
        

    def objectSetup(self, obj): 
        ###e [should move this up, below generic left* methods -- 
        ##it's not just about atoms]
        # [this seems to be called (sometimes indirectly) by every leftDown 
        # method, and by some methods in depmode that create objects and can 
        # immediately drag them. Purpose is more general than just for a 
        # literal "drag" --
        # I guess it's for many things that immediately-subsequent leftDrag or 
        # leftUp or leftDouble might need to know obj to decide on. I think I'll
        #call it for all new drag_handlers too. [bruce 060728 comment]]
        self.current_obj = obj # [used by leftDrag and leftUp to decide what 
                               #to do [bruce 060727 comment]]
        self.obj_doubleclicked = obj # [used by leftDouble and class-specific 
                                     #leftDouble methods [bruce 060727 comment]]
        if obj is None:
            self.current_obj_clicked = False
        else:
            self.current_obj_clicked = True
                # [will be set back to False if obj is dragged, but only by 
                # class-specific drag methods, not by leftDrag itself -- make 
                # sure to consider doing that in drag_handler case too  ##@@@@@
                #  [bruce 060727 comment]]
                
            # we need to store something unique about this event;
            # we'd use serno or time if it had one..instead this _count will do.
            global _count
            _count = _count + 1
            self.current_obj_start = _count # used in transient_id argument 
                                            #to env.history.message
           
    
    #bruce 060414 move selatoms optimization (won't be enabled by default in A7)
    # (very important for dragging atomsets that are part of big chunks but not 
    # all of them)
    # UNFINISHED -- still needs:
    # - failsafe for demolishing bc if drag doesn't end properly
    # - disable undo cp's when bc exists (or maybe during any drag of any kind
    #   in any mode)
    # - fix checkparts assertfail (or disable checkparts) when bc exists and 
    #   atom_debug set
    # - not a debug pref anymore
    # - work for single atom too (with its baggage, implying all bps for real 
    #   atoms in case chunk rule for that matters)
    # - (not directly related:)
    #   review why reset_drag_vars is only called in selectAtomsMode but the 
    #    vars are used in the superclass selectMode
    #   [later 070412: maybe because the methods calling it are themselves only 
    #    called from selectAtomsMode? it looks that way anyway]
    #   [later 070412: ###WARNING: in Qt3, reset_drag_vars is defined in 
    #   selectAtomsMode, but in Qt4, it's defined in selectMode.]
    # 
    bc_in_use = None # None, or a BorrowerChunk in use for the current drag,
            # which should be drawn while in use, and demolished when the drag 
            #is done (without fail!) #####@@@@@ need failsafe
    _reusable_borrowerchunks = [] # a freelist of empty BorrowerChunks not now
                                  # being used (a class variable, not instance 
                                  # variable)

    def allocate_empty_borrowerchunk(self):
        """
        Someone wants a BorrowerChunk; allocate one from our freelist or a new 
        one
        """
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
        bc.demolish() # so it stores nothing now, but can be reused later; 
                     #repeated calls must be ok
        self._reusable_borrowerchunks.append(bc)

    
    

    def deallocate_bc_in_use(self):
        """
        If self.bc_in_use is not None, it's a BorrowerChunk and we need to 
        deallocate it -- this must be called at the end of any drag which might 
        have allocated it.
        """
        if self.bc_in_use is not None:
            self.deallocate_borrowerchunk( self.bc_in_use )
            self.bc_in_use = None
        return

    #bruce 060316 moved dragto from here (selectMode) into class basicMode        
    def atomSetup(self, a, event):
        """
        Subclasses should override this method
        Setup for a click, double-click or drag event for real atom <a>.
        @see: selectatomsMode.atomSetup where this method is overridden.
        """
        self.objectSetup(a) 
    
    def atomLeftDown(self, a, event):
        """
        Subclasses should override this method.
        @param a: Instance of class Atom 
        @type a: B{Atom}
        @param event: the QMouseEvent. 
        @see: selectAtomsMode.atomLeftDown
        """
        self.atomSetup(a, event)

    def atomLeftUp(self, a, event):
        """
        Subclasses should override this method. The default implementation does
        nothing. 
        @param a: Instance of class Atom 
        @type a: B{Atom}
        @param event: the QMouseEvent. 
        @see: selectAtomsMode.atomLeftUp
        """
        pass
    
    def atomLeftDouble(self): # mark 060308
        """
        Subclasses should override this method. The default implementation 
        does nothing. 
        
        Atom double click event handler for the left mouse button.
        """
        pass

    # == End of Atom selection and dragging helper methods

    # == Bond selection helper methods

    def bondLeftDown(self, b, event):
        # Bonds cannot be picked when highlighting is turned off.
        self.cursor_over_when_LMB_pressed = 'Bond'
        self.bondSetup(b)

    def bondSetup(self, b):
        """
        Setup for a click or double-click event for bond <b>. Bond dragging is not supported.
        """
        self.objectSetup(b)

    def bondLeftUp(self, b, event):
        """
        Subclasses should override this method. The default implementation does 
        nothing. 
        
        Bond <b> was clicked, so select or unselect its atoms or delete bond <b>
        based on the current modkey.
        - If no modkey is pressed, clear the selection and pick <b>'s two atoms.
        - If Shift is pressed, pick <b>'s two atoms, adding them to the current 
          selection.
        - If Ctrl is pressed,  unpick <b>'s two atoms, removing them from 
          the current selection.
        - If Shift+Control (Delete) is pressed, delete bond <b>.
        <event> is a LMB release event.
        """
        pass
    
        
    def bondDelete(self, event):
        """
                
        If the object under the cursor is a bond, delete it. Subclasses should 
        override this method. The default implementation does nothing. 
        
        @param event: A left mouse up event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        pass
    
    def bondDrag(self, obj, event):
        """
        Subclasses should override this method
        @see: selectAtomsMode.bondDrag
        """
        pass
    
    def bondLeftDouble(self):
        """
        Subclasses should override this method
        @see: selectAtomsMode.bondLeftDouble
        """
        pass
        
    # == End of bond selection helper methods

    # == Singlet helper methods

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
        """
        Singlet double click event handler for the left mouse button.
        """
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
                    # REVIEW (possible optim): can we make gl_update_highlight
                    # cover this? [bruce 070626]
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
        
    # == Jig event handler helper methods   

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
        """
        Setup for a click, double-click or drag event for jig <j>.
        """
        self.objectSetup(j)

    def jigLeftUp(self, j, event):
        """
        Jig <j> was clicked, so select, unselect or delete it based on the current modkey.
        - If no modkey is pressed, clear the selection and pick jig <j>.
        - If Shift is pressed, pick <j>, adding it to the current selection.
        - If Ctrl is pressed,  unpick <j>, removing it from the current selection.
        - If Shift+Control (Delete) is pressed, delete jig <j>.
        """

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
        """
        Jig <j> was double clicked, so select, unselect or delete its atoms based on the current modkey.
        - If no modkey is pressed, pick the jig's atoms.
        - If Shift is pressed, pick the jig's atoms, adding them to the current selection.
        - If Ctrl is pressed,  unpick the jig's atoms, removing them from the current selection.
        - If Shift+Control (Delete) is pressed, delete the jig's atoms.
        """
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

    # == End of (most) Jig helper methods

    def mouse_within_stickiness_limit(self, event, drag_stickiness_limit_pixels): #bruce 060315 reimplemented this
        """
        Check if mouse has never been dragged beyond <drag_stickiness_limit_pixels>
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
        """
        Check if mouse has been moved beyond <pixel_distance> since the last mouse 'move event'.
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
        """
        Turn hover highlighting (in our graphicsMode) on/off.
        if <on> is True, atoms and bonds are highlighted as the cursor passes over them.
        if <on> is False, atoms are not highlighted until they are selected (with LMB click).
        Bonds are not highlighted either, but they cannot be selected when highlighting is turned off.
        """
        self.hover_highlighting_enabled = on
        if on:
            msg = "Highlighting turned on."
        else:
            msg = "Highlighting turned off."
        env.history.message(msg)

    def get_jig_under_cursor(self, event): ###e should move this up with the other Jig helper methods
        """
        Use the OpenGL picking/selection to select any jigs. Restore the projection and modelview
        matrices before returning.
        """
        ####@@@@ WARNING: The original code for this, in GLPane, has been duplicated and slightly modified
        # in at least three other places (search for glRenderMode to find them). TWO OF THEM ARE METHODS
        # IN THIS CLASS! This is bad; common code
        # should be used. Furthermore, I suspect it's sometimes needlessly called more than once per frame;
        # that should be fixed too. [bruce 060721 comment]

        if not self.o.jigSelectionEnabled:
            return None

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

        # Restore project matrix and set matrix mode to Model/View
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

    def _calibrateZ(self, wX, wY): # by huaicai; bruce 071013 moved this here from GraphicsMode
        """
        Because translucent plane drawing or other special drawing,
        the depth value may not be accurate. We need to
        redraw them so we'll have correct Z values. 
        """
        glMatrixMode(GL_MODELVIEW)
        glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE) 

        if self.Draw_after_highlighting(pickCheckOnly = True): # Only when we have translucent planes drawn
            self.o.assy.draw(self.o)

        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)

        return wZ[0][0]

    def jigGLSelect(self, event, selSense): # by huaicai; bruce 071013 moved this here from GraphicsMode
        """
        Use the OpenGL picking/selection to select any jigs.
        Restore the projection and modelview matrices before returning.
        """
        ## [Huaicai 9/22/05]: Moved it from selectMode class, so it can be called in move mode, which
        ## is asked for by Mark, but it's not intended for any other mode.
        # [since then I moved it back here, since move == modify is a subclass of this -- bruce 071013]
        #
        ### WARNING: The original code for this, in GLPane, has been duplicated and slightly modified
        # in at least three other places (search for glRenderMode to find them).  TWO OF THEM ARE METHODS
        # IN THIS CLASS! This is bad; common code
        # should be used. Furthermore, I suspect it's sometimes needlessly called more than once per frame;
        # that should be fixed too. [bruce 060721 comment]

        wX = event.pos().x()
        wY = self.o.height - event.pos().y()

        gz = self._calibrateZ(wX, wY) 
        if gz >= GL_FAR_Z:  # Empty space was clicked--This may not be true for translucent face [Huaicai 10/5/05]
            return False  

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

        # Restore project matrix and set matrix mode to Model/View
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
                    if selSense == SUBTRACT_FROM_SELECTION: #Ctrl key, unpick picked
                        if obj.picked:  
                            obj.unpick()
                    elif selSense == ADD_TO_SELECTION: #Shift key, Add pick
                        if not obj.picked: 
                            obj.pick()
                    else:               #Without key press, exclusive pick
                        self.o.assy.unpickall_in_GLPane() # was: unpickparts, unpickatoms [bruce 060721]
                        if not obj.picked:
                            obj.pick()
                    return True
        return False # from jigGLSelect

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

    def selobj_highlight_color(self, selobj): 
        """
        [mode API method]

        If we'd like this selobj to be highlighted on mouseover
        (whenever it's stored in glpane.selobj), return the desired highlight 
	color.
        If we'd prefer it not be highlighted (though it will still be stored
        in glpane.selobj and prevent any other objs it obscures from being 
	stored there or highlighted), return None.

	@param selobj: The object in the GLPane to be highlighted 
	@TODO: exceptions are ignored and cause the default highlight color 
	to be used ..should clean that up sometime
        """
        # Mode API method originally by bruce 050612. 
        # This has been refactored further and moved to the superclass 
        # from selectAtomsMode. -- Ninad 2007-10-14

        if not self.hover_highlighting_enabled:
            return None

        #####@@@@@ if self.drag_handler, we should probably let it 
        # override all this
        # (so it can highlight just the things it might let you 
        # DND its selobj to, for example),
        # even for Atom/Bondpoint/Bond/Jig, maybe even when not 
        # self.hover_highlighting_enabled. [bruce 060726 comment]

        if isinstance(selobj, Atom):
            return self._getAtomHighlightColor(selobj)
        elif isinstance(selobj, Bond):
            return self._getBondHighlightColor(selobj)
        elif isinstance(selobj, Jig): 
            return self._getJigHighlightColor(selobj)
        else:
            return self._getObjectDefinedHighlightColor(selobj)

    def _getAtomHighlightColor(self, selobj):
        """
	Return the Atom highlight color 
	@return: Highlight color of the object (Atom or Singlet)
	The default implementation returns 'None' . Subclasses should override
	this method if they need atom highlight color.
	""" 
        return None

    def _getBondHighlightColor(self, selobj):
        """
	Return the Bond highlight color 
	@return: Highlight color of the object (Bond)
	The default implementation returns 'None' . Subclasses should override
	this method if they need bond highlight color.
	""" 
        return None

    def _getJigHighlightColor(self, selobj):
        """
	Return the Jig highlight color. Subclasses can override this method.
	@return: Highlight color of the Jig
	"""
        assert isinstance(selobj, Jig)

        if not self.o.jigSelectionEnabled: #mark 060312.
            # jigSelectionEnabled set from GLPane context menu.
            return None
        if self.o.modkeys == 'Shift+Control': 
            return env.prefs[deleteBondHighlightColor_prefs_key]
        else:
            return env.prefs[bondHighlightColor_prefs_key]

    def _getObjectDefinedHighlightColor(self, selobj):
        """
	Return the highlight color defined by the object itself. 
	"""

        # Let the object tell us its highlight color, if it's not one we have 
        # a special case for here (and if no drag_handler told us instead 
        # (nim, above)).
        # Note: this color will be passed to selobj.draw_in_abs_coords when 
        # selobj is asked to draw its highlight; but even if that method plans 
        # to ignore that color arg,
        # this method better return a real color (or at least not None or 
        # (maybe) anything false),
        # otherwise GLPane will decide it's not a valid selobj and not 
        # highlight it at all.
        # (And in that case, will a context menu work on it 
        # (if it wasn't nim for that kind of selobj)?  I don't know.)
        # [bruce 060722 new feature; revised comment 060726]
        method = getattr(selobj, 'highlight_color_for_modkeys', None)
        if method:
            return method(self.o.modkeys)
            # Note: this API might be revised; it only really makes sense 
            # if the mode created the selobj to fit its
            # current way of using modkeys, perhaps including not only its 
            # code but its active-tool state.
            #e Does it make sense to pass the drag_handler, even if we let it 
            # override this?
            # Yes, since it might like to ask the object (so it needs an API 
            # to do that), or let the obj decide,
            # based on properties of the drag_handler.
            #e Does it make sense to pass the obj being dragged without a 
            # drag_handler?
            # Yes, even more so. Not sure if that's always called the same 
            #thing, depending on its type.
            # If not, we can probably just kluge it by self.this or self.that, 
            # if they all get reset each drag. ###@@@
        print "unexpected selobj class in mode.selobj_highlight_color:", selobj
        # Return black color so that an error becomes more obvious 
        #(bruce comments)
        return black

    def get_obj_under_cursor(self, event): # docstring appears wrong
        """
        Return the object under the cursor.  Only atoms, singlets and bonds 
	are returned.
        Returns None for all other cases, including when a bond, jig or nothing 
	is under the cursor. [warning: this docstring appears wrong.]

        @attention: This method was originally from class selectAtomsMode. See
	            code comment for details
        """

        #@ATTENTION: This method was originally from class selectAtomsMode. 
        # It was mostly duplicated (with some changes) in selectMolsMode 
        # when that mode started permitting highlighting. 
        # The has been modified and moved to selectMode class so that both 
        # selectAtomsMode and selectMolsMode can use it -Ninad 2007-10-15


        #bruce 060331 comment: this docstring appears wrong, since the code looks like it can return jigs.
        #bruce 070322 note: this will be overridden (extended) in testmode, which will sometimes return a "background object"
        # rather than None, in order that leftDown can be handled by background_object.leftClick in the same way as for
        # other drag_handler-returning objects.
        #
        ### WARNING: this is slow, and redundant with highlighting -- only call it on mousedown or mouseup, never in move or drag.
        # [true as of 060726 and before; bruce 060726 comment]
        # It may be that it's not called when highlighting is on, and it has no excuse to be, but I suspect it is anyway.
        # [bruce 060726 comment]
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
            # motion before pressing the mouse. [bruce 050705 comment] [might be out of context, copied from other code]

            obj = self.o.selatom # a "highlighted" atom or singlet

            if obj is None and self.o.selobj:
                obj = self.o.selobj # a "highlighted" bond
                    # [or anything else, except Atom or Jig -- i.e. a general/drag_handler/Drawable selobj [bruce 060728]]
                if env.debug():
                    # I want to know if either of these things occur -- I doubt they do, but I'm not sure about Jigs [bruce 060728]
                    # (this does happen for Jigs, see below)
                    if isinstance(obj, Atom):
                        print "debug fyi: likely bug: selobj is Atom but not in selatom: %r" % (obj,)
                    elif isinstance(obj, Jig):
                        print "debug fyi: selobj is a Jig in get_obj_under_cursor (comment is wrong), for %r" % (obj,)
                        # I suspect some jigs can occur here
                        # (and if not, we should put them here -- I know of no excuse for jig highlighting
                        #  to work differently than for anything else) [bruce 060721]
                        # update 070413: yes, this happens (e.g. select some atoms and an rmotor jig, then drag the jig).
                    pass

            if obj is None: # a "highlighted" jig [i think this comment is misleading, it might really be nothing -- bruce 060726]
                obj = self.get_jig_under_cursor(event) # [this can be slow -- bruce comment 070322]
                if 0 and env.debug():
                    print "debug fyi: get_jig_under_cursor returns %r" % (obj,) # [bruce 060721] 
            pass

        else: # No hover highlighting
            obj = self.o.assy.findAtomUnderMouse(event, 
                                                 self.water_enabled, 
                                                 singlet_ok = True)
            # Note: findAtomUnderMouse() only returns atoms and singlets, not 
            # bonds or jigs.
            # This means that bonds can never be selected when highlighting 
            # is turned off.
            # [What about jigs? bruce question 060721]
        return obj

    def update_selobj(self, event): #bruce 050610
        """
	Keep glpane.selobj up-to-date, as object under mouse, or None
        (whether or not that kind of object should get highlighted).

	Return True if selobj is already updated when we return, or False 
	if that will not happen until the next paintGL.

	Warning: if selobj needs to change, this routine does not change it 
	(or even reset it to None); it only sets flags and does gl_update, 
	so that paintGL will run soon and will update it properly, and will 
	highlight it if desired ###@@@ how is that controlled? probably by 
	some statevar in self, passed to gl flag?

	This means that old code which depends on selatom being  up-to-date must
	do one of two things:
	    - compute selatom from selobj, whenever it's needed;
	    - hope that paintGL runs some callback in this mode when it changes
	      selobj, which updates selatom and outputs whatever statusbar 
	      message is appropriate. ####@@@@ doit... this is not yet fully ok.

	@attention: This method was originally from class selectAtomsMode. See
	            code comment for details
        """

        #@ATTENTION: This method was originally from class selectAtomsMode. 
        # It was mostly duplicated (with some changes) in selectMolsMode 
        # when that mode started permitting highlighting. 
        # The has been modified and moved to selectMode class so that both 
        # selectAtomsMode and selectMolsMode can use it -Ninad 2007-10-12



        #e see also the options on update_selatom;
        # probably update_selatom should still exist, and call this, and 
        #provide those opts, and set selatom from this,
        # but see the docstring issues before doing this ####@@@@

        # bruce 050610 new comments for intended code (#e clean them up and
        # make a docstring):
        # selobj might be None, or might be in stencil buffer.
        # Use that and depthbuffer to decide whether redraw is needed to look 
        # for a new one.
        # Details: if selobj none, depth far or under water is fine, any other 
        # depth means look for new selobj (set flag, glupdate). if selobj not
        # none, stencil 1 means still same selobj (if no stencil buffer, have to
        # guess it's 0); else depth far or underwater means it's now None 
        #(repaint needed to make that look right, but no hittest needed)
        # and another depth means set flag and do repaint (might get same selobj
        #(if no stencil buffer or things moved)or none or new one, won't know 
        # yet, doesn't matter a lot, not sure we even need to reset it to none 
        # here first).
        # Only goals of this method: maybe glupdate, if so maybe first set flag,
        # and maybe set selobj none, but prob not(repaint sets new selobj, maybe
        # highlights it).[some code copied from modifyMode]

        if debug_update_selobj_calls:
            print_compact_stack("debug_update_selobj_calls: ")

        glpane = self.o

        # If animating or ZPRing (zooming/panning/rotating) with the MMB, 
        # do not hover highlight anything. For more info about <is_animating>, 
        #see GLPane.animateToView(). mark 060404.
        if self.o.is_animating or \
           (self.o.button == "MMB" and not getattr(self, '_defeat_update_selobj_MMB_specialcase', False)):
            return
                # note, returning None violates this method's API (acc'd to docstring), but this apparently never mattered until now,
                # and it's not obvious how to fix it (probably to be correct requires imitating the conditional set_selobj below),
                # so instead I'll just disable it in the new case that triggers it, using _defeat_update_selobj_MMB_specialcase.
                # [bruce 070224]

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
            #For selectMolsMode, 'water' is not defined. So self.water_enabled
            # is initialized to None in this class. This is one of the things 
            # needed to do for moving selectAtomsMode.update_selobj to here 
            # and getting rid of mostly duplicated code in selectMolsMode and
            # selectAtomsMode -- Ninad 2007-10-12. 	    
            if self.water_enabled:
                # compare to water surface depth
                cov = - glpane.pov # center_of_view (kluge: we happen to know this is where the water surface is drawn)
                try:
                    junk, junk, cov_depth = gluProject( cov[0], cov[1], cov[2] )
                except:
                    print_compact_traceback( "gluProject( cov[0], cov[1], cov[2] ) exception ignored, for cov == %r: " % (cov,) )
                    cov_depth = 2 # too deep to matter (depths range from 0 to 1, 0 is nearest to screen)
                water_depth = cov_depth
                if wZ >= water_depth:
                    #print "behind water: %r >= %r" % (wZ , water_depth)
                    new_selobj = None
                        # btw, in contrast to this condition for a new selobj, an existing one will
                        # remain selected even when you mouseover the underwater part (that's intentional)
                else:
                    # depth is in front of water
                    new_selobj_unknown = True
            else:
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
            # don't change glpane.selobj (since it might not even need to change) (ok??#k) -- the next paintGL will do that --
            # UNLESS the current mode wants us to change it [new feature, bruce 061218, perhaps a temporary kluge, but helps
            #  avoid a logic bug in this code, experienced often in testmode due to its slow redraw]
            #
            # Note: I'm mostly guessing that this should be found in (and unique to) graphicsMode
            # rather than currentCommand, in spite of being set only in testmode by current code.
            # That does make this code simpler, since graphicsMode is self. So replacing glpane.mode with self.
            # [bruce 071010, same comment and change done in both duplications of this code, and in other places]
            if hasattr(self, 'UNKNOWN_SELOBJ'):
                glpane.selobj = getattr(self, 'UNKNOWN_SELOBJ')
            glpane.gl_update_for_glselect()
        else:
            # it's known (to be a specific object or None)
            if new_selobj is not orig_selobj:
                # this is the right test even if one or both of those is None.
                # (Note that we never figure out a specific new_selobj, above,
                #  except when it's None, but that might change someday
                #  and this code can already handle that.)
                glpane.set_selobj( new_selobj, "Select mode")
                #e use setter func, if anything needs to observe changes to 
                # this? or let paintGL notice the change (whether it or elseone 
                # does it) and  report that?
                # Probably it's better for paintGL to report it, so it doesn't 
                # happen too often or too soon!
                # And in the glselect_wanted case, that's the only choice, 
                # so we needed code for that anyway.
                # Conclusion: no external setter func is required; maybe glpane
                # has an internal one and tracks prior value.
                glpane.gl_update_highlight() # this might or might not highlight that selobj ###e need to tell it how to decide??
        # someday -- we'll need to do this in a callback when selobj is set:
        ## self.update_selatom(event, msg_about_click = True)
        # but for now, I removed the msg_about_click option, since it's no longer used,
        # and can't yet be implemented correctly (due to callback issue when selobj
        # is not yet known), and it tried to call a method defined only in depositMode,
        # describe_leftDown_action, which I'll also remove or comment out. [bruce 071025]
        return not new_selobj_unknown # from update_selobj

    def update_selatom(self, 
                       event, 
                       singOnly = False, 
                       resort_to_prior = True):
        """
	THE DEFAULT IMPLEMENTATION OF THIS METHOD DOES NOTHING. Subclasses 
	should override this method as needed.
	
	@see: selectAtomsMode.update_selatom for documentation.
        #see; selectMode.get_obj_under_cursor
        """
        # REVIEW: are any of the calls to this in selectMode methods,
        # which do nothing except in subclasses of selectAtomsMode,
        # indications that the code they're in doesn't make sense except
        # in such subclasses? [bruce 071025 question]
        
        #I am not sure what you mean above. Assuming you meant: Is there a 
        #method in this class selectMode, that calls this method
        # (i.e. calls selectMode.update_selatom)
        #Yes, there is a method self.selectMode.get_obj_under_cursor that calls 
        #this method and thats why I kept a default implemetation that does 
        #nothing -- Ninad 2007-11-16
        pass

    def makeMenus(self):
        """
        Overrided in subclasses. Default implementation does nothing
        @see: selectAtomsMode.makeMenus
        @see: selectMolsMode.makeMenus         
        """
        pass    

    def toggleJigSelection(self):
        self.o.jigSelectionEnabled = not self.o.jigSelectionEnabled

    
    pass # end of class selectMode

# end
