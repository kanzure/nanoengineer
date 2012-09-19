# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
Select_GraphicsMode.py
The GraphicsMode part of the Select_Command. It provides the graphicsMode
object for its Command class. The GraphicsMode class defines anything
related to the *3D Graphics Area* --
For example:
- Anything related to graphics (Draw method),
- Mouse events
- Cursors,
- Key bindings or context menu

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

TODO:
-  Select_basicGraphicsMode is the main GM class. It is inherited by
    a 'glue-in' class Select_GraphicsMode. See cad/doc/splitting_a_mode.py for
    a detailed explanation on how this is used. Note that the glue-in classes
    will be used until all the selectMode subclasses are split into GM
    and Command part. Once thats done you the class Select_basicGraphicsMode
    needs to be used (and rename that to Select_GraphicsMode)
-  See if context menu related method makeMenus defined in the command class
    needs to be moved to the GraphicsMode class
-  Other items listed in Select_Command.py
-  Redundant use of glRenderMode (see comment where that is used) See Bruce's
  comments in method get_jig_under_cursor

+++
OLD comment -- might be outdated as of 2007-12-13
Some things that need cleanup in this code [bruce 060721 comment]: ####@@@@

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
+++

History:
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from
                          the old class selectMode and moved the GraphicsMode
                          related methods into this class from selectMode.py

"""
from numpy.oldnumeric import dot

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


from OpenGL.GLU import gluProject
from OpenGL.GLU import gluUnProject

from utilities.constants import GL_FAR_Z
from utilities.constants import SELSHAPE_RECT
from utilities.constants import SELSHAPE_LASSO
from utilities.constants import SUBTRACT_FROM_SELECTION
from utilities.constants import ADD_TO_SELECTION
from utilities.constants import START_NEW_SELECTION
from utilities.constants import DELETE_SELECTION

from utilities.constants import black

import foundation.env as env

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice

from geometry.VQT import A, vlen

from graphics.behaviors.shape import SelectionShape
from model.bonds import Bond
from model.chem import Atom
from model.jigs import Jig

from utilities.debug import print_compact_traceback
from utilities.debug import print_compact_stack

from utilities.prefs_constants import bondHighlightColor_prefs_key
from utilities.prefs_constants import deleteBondHighlightColor_prefs_key

from utilities import debug_flags


debug_update_selobj_calls = False # do not commit with true


DRAG_STICKINESS_LIMIT = 6 # in pixels; reset in each leftDown via a debug_pref
    #& To do: Make it a user pref in the Prefs Dialog.  Also consider a
    # different var/pref
    #& for singlet vs. atom drag stickiness limits. Mark 060213.

_ds_Choice = Choice([0,1,2,3,4,5,6,7,8,9,10],
                    defaultValue = DRAG_STICKINESS_LIMIT)

DRAG_STICKINESS_LIMIT_prefs_key = "A7/Drag Stickiness Limit"

def set_DRAG_STICKINESS_LIMIT_from_pref(): #bruce 060315
    global DRAG_STICKINESS_LIMIT
    DRAG_STICKINESS_LIMIT = debug_pref(
        "DRAG_STICKINESS_LIMIT (pixels)",
        _ds_Choice,
        non_debug = True,
        prefs_key = DRAG_STICKINESS_LIMIT_prefs_key)
    return

set_DRAG_STICKINESS_LIMIT_from_pref() # also called in SelectAtoms_GraphicsMode.leftDown
    # (ideally, clean up this pref code a lot by not passing
    # DRAG_STICKINESS_LIMIT  as an arg to the subr that uses it)
    # we do this early so the debug_pref is visible in the debug menu before
    # entering SelectAtoms_GraphicsMode.

# ==

from command_support.GraphicsMode import basicGraphicsMode

from commands.Select.Select_GraphicsMode_MouseHelpers_preMixin import Select_GraphicsMode_MouseHelpers_preMixin
from temporary_commands.TemporaryCommand import ESC_to_exit_GraphicsMode_preMixin

_superclass = basicGraphicsMode

class Select_basicGraphicsMode( Select_GraphicsMode_MouseHelpers_preMixin,
                                ESC_to_exit_GraphicsMode_preMixin,
                                basicGraphicsMode ):
    """
    The GraphicsMode part of the Select_Command. It provides the graphicsMode
    object for its Command class. The GraphicsMode class defines anything
    related to the 3D graphics area --
    For example:
    - Anything related to graphics (Draw method),
    - Mouse events, cursors (for use in graphics area),
    - Key bindings or context menu (for use in graphics area).

    @see: cad/doc/splitting_a_mode.py that gives a detailed explanation about
          how this is implemented.
    @see: B{Select_GraphicsMode}
    @see: B{Select_Command}, B{Select_basicCommand}, B{selectMode}
    @see: B{Select_GraphicsMode_MouseHelpers_preMixin}
    @see: B{SelectChunks_basicGraphicsMode}, B{SelectAtoms_basicGraphicsMode}
          which inherits this class
    """

    # class constants
    gridColor = (0.0, 0.0, 0.6)

    # default initial values
    savedOrtho = 0

    selCurve_length = 0.0
        # <selCurve_length> is the current length (sum) of all the selection
        #curve segments.

    selCurve_List = []
        # <selCurve_List> contains a list of points used to draw the selection
        #  curve.  The points lay in the
        #  plane parallel to the screen, just beyond the front clipping plane,
        #  so that they are always
        #  inside the clipping volume.
    selArea_List = []
        # <selArea_List> contains a list of points that define the selection
        #  area.  The points lay in
        # the plane parallel to the screen and pass through the center of the
        # view.  The list is used by pickrect() and pickline() to make the
        #  selection.
    selShape = SELSHAPE_RECT
        # <selShape> the current selection shape.

    ignore_next_leftUp_event = False
        # Set to True in leftDouble() and checked by the left*Up()
        # event handlers to determine whether they should ignore the
        # (second) left*Up event generated by the second LMB up/release
        # event in a double click.
        
    #Boolean flag that is used in combination with 
    #self.command.isHighlightingEnabled(). 
    _suppress_highlighting = False


    def __init__(self, glpane):
        """
        """
        _superclass.__init__(self, glpane)
        # Now do whatever might be needed to init the graphicsMode object,
        # or the graphicsMode-related attrs of the mixed object.
        #
        # (Similar comments apply as for Select_basicCommand.__init__, below,
        #  but note that for GraphicsModes, there is no Enter method.
        #  Probably we will need to add something like an Enter_graphicsMode
        #  method to the GraphicsMode API. In the meantime, the command's Enter
        #  method has to initialize the graphicsMode object's attrs (which are
        #  the graphics-related attrs of self, in the mixed case, but are
        #  referred to as self.graphicsMode.attr so this will work in the split
        #  case as well), which is a kluge.)

        #Initialize the flag often used in leftDrag methods of the subclasses
        #to avoid any attr errors. Note that this flag will often be reset in
        #self.reset_frag_vars()
        self.cursor_over_when_LMB_pressed = None

        #Initialize LMB_press_event
        self.LMB_press_event = None

        return

    def Enter_GraphicsMode(self):
        """
        Things needed while entering the GraphicsMode (e.g. updating cursor,
        setting some attributes etc).
        
        @see: B{baseCommand.command_entered()} which calls this method
        """
        _superclass.Enter_GraphicsMode(self)
        self.reset_drag_vars()
        self.ignore_next_leftUp_event = False
            # Set to True in leftDouble() and checked by the left*Up()
            # event handlers to determine whether they should ignore the
            # (second) left*Up event generated by the second LMB up/release
            # event in a double click.

    # ==

    def _draw_this_test_instead(self):
        """
        [private]
        Decide whether to draw a special test graphic in place of the model,
        and if so, which one.
        """
        # TODO: move this test code into a specific test mode just for it,
        # so it doesn't clutter up or slow down this general-use mode.
        #
        # wware 060124  Embed Pyrex/OpenGL unit tests into the cad code
        # grantham 060207:
        # Set to 1 to see a small array of eight spheres.
        # Set to 2 to see the Large-Bearing model, but this is most effective if
        #  the Large-Bearing has already been loaded normally into rotate mode
        #bruce 060209 set this from a debug_pref menu item, not a hardcoded flag
        TEST_PYREX_OPENGL = debug_pref("GLPane: TEST_PYREX_OPENGL", Choice([0,1,2]))
        # uncomment this line to set it in the old way:
        ## TEST_PYREX_OPENGL = 1

        return TEST_PYREX_OPENGL
        
    def Draw_model(self):
        _superclass.Draw_model(self) # probably a noop -- actual model drawn below
        
        TEST_PYREX_OPENGL = self._draw_this_test_instead()
        if TEST_PYREX_OPENGL:
            # draw this test instead of the usual model
            from graphics.drawing.c_renderer import test_pyrex_opengl
            test_pyrex_opengl(TEST_PYREX_OPENGL)
                #bruce 090303 split this out (untested;
                # it did work long ago when first written, inlined here)
                # (revised again, 090310, still untested)
            pass
        else:
            # draw the usual model
            if self.bc_in_use is not None: #bruce 060414
                self.bc_in_use.draw(self.o, 'fake dispdef kluge')
            self.o.assy.draw(self.o)
        return
    
    def Draw_other(self):
        _superclass.Draw_other(self)
        
        TEST_PYREX_OPENGL = self._draw_this_test_instead()
        if TEST_PYREX_OPENGL:
            pass
        else:
            #self.griddraw()
            if self.selCurve_List:
                self.draw_selection_curve()
        return

    # ==
    
    def getMovablesForLeftDragging(self):
        """
        Returns a list of movables that will be moved during this gaphics mode's
        left drag. In SelectChunks_GraphicsMode it is the selected movables
        in the assembly. However, some subclasses can override this method to
        provide a custom list of objects it wants to move during the left drag
        Example: In buildDna_GraphicsMode, it moving a dnaSegment axis chunk
        will move all the axischunk members of the dna segment and also
        its logical content chunks.
        @see: self._leftDrag_movables #attr
        @see: self._leftDown_preparation_for_dragging()
        @see: self.leftDragTranslation()
        @see:BuildDna_GraphicsMode.getMovablesForLeftDragging()
        """
        movables = []

        movables = self.win.assy.getSelectedMovables()

        contentChunksOfSelectedSegments = []
        contentChunksOfSelectedStrands  = []

        selectedSegments = self.win.assy.getSelectedDnaSegments()
        selectedStrands = self.win.assy.getSelectedDnaStrands()

        for segment in selectedSegments:
            contentChunks = segment.get_all_content_chunks()
            contentChunksOfSelectedSegments.extend(contentChunks)

        for strand in selectedStrands:
            strandContentChunks = strand.get_all_content_chunks()
            contentChunksOfSelectedStrands.extend(strandContentChunks)

        #doing item in list' could be a slow operation. But this method will get
        #called only duting leftdown and not during leftDrag so it should be
        #okay -- Ninad 2008-04-08

        for c in contentChunksOfSelectedSegments:
            if c not in movables:
                movables.append(c)

        #After appending appropriate content chunks of segment, do same thing for
        #strand content chunk list.
        #Remember that the  contentChunksOfSelectedStrandscould contain chunks
        #that are already listed in contentChunksOfSelectedSegments

        for c in contentChunksOfSelectedStrands:
            if c not in movables:
                movables.append(c)

        return movables

    def reset_drag_vars(self):
        """
        This resets (or initializes) per-drag instance variables, and is called
        in Enter and at beginning of leftDown. Subclasses can override this
        to add variables, but those methods should call this version too.
        @see L{SelectAtoms_GraphicsMode.reset_drag_vars}
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

        self.current_obj = None
            # current_obj is the object under the cursor when the LMB was
            # pressed.
            # [it is set to that obj by objectSetup, and set back to None by
            # some, but not all, mousedrag and mouseup methods. It's used by
            # leftDrag and leftUp  to decide what to do, to what object.
            # When a drag_handler is in use, I think [bruce 060728] this will be
            # the  drag_handler (not the selobj that it is for), but I'll still
            # have a separate self.drag_handler attr to also record that. One of
            # these is redundant, but this will most clearly separate old and
            # new code, while ensuring that if old code tests current_obj it
            # won't see a class it thinks it knows how to handle (even if I
            # sometimes use drag_handlers to drag old specialcase object
            # classes), and won't see None.(Other possibilities would be to not
            # have self.drag_handler at all, and/or to let this be the selobj
            # that a drag_handler was made for; these seem worse now, but I
            # mention them in case I need to switch to them.)
            #  Maybe we'll need some uses of current_obj to filter it though a
            # self method which converts drag_handlers back to their underlying
            # objects (i.e. the selobj that they were made from or made for).
            # (Or have a .selobj attr.)  #####@@@@@ [bruce 060728 comment]]

        self.current_obj_clicked = False
            # current_obj_clicked is used to determine if a lit up atom, singlet
            # or bond was picked (clicked)or not picked (dragged). It must be
            # set to False here so that a newly deposited atom doesn't pick
            # itself right away (although now this is the default behavior).
            # current_obj_clicked is set to True in *LeftDown() before it gets
            # dragged (if it does at all).If it is dragged, it is set to False
            # in *LeftDrag().*LeftUp() checks it to determine whether the object
            # gets picked or not. mark 060125. [bruce 060727 comments: it seems
            # to mean "was self.current_obj clicked, but not (yet) dragged",
            #  and its basic point seems to be to let leftUp decide whether to
            #  select the object,i.e. to not require all drags of objects to
            #  select them.Note: it is set back to False only by class-specific
            #  drag methods, not by leftDrag itself;similarly, it is used only
            #  in class-specific mouseup methods, not by leftUp itself.
            #   For drag_handlers, it looks like we should treat all
            # drag_handler uses as another object type,so we should set this in
            # the same way in the drag_handler-specific methods. Hmm, maybe we
            # want separate submethods like dragHandlerLeft*, just as for
            # Atom/Bond/Jig. #####@@@@@
            # ]
        self.obj_doubleclicked = None
            # used by leftDouble() to determine the object that was double
            # clicked.
            # [bruce 060727 comments: This is the same object found by the first
            # click's leftDown -- mouse motion
            #  is not checked for! That might be a bug -- if the mouse slipped
            # off this object, it might be betterto discard the entire drag (and
            # a stencil buffer test could check for this, without needing
            # glSelect). At least, this is always the correct object if anything
            # is.It is used in obj-class-specific leftDown methods, and assumed
            # to be an object of the right class (which seems ok, since
            # leftDouble uses isinstance on it to call one of those methods).
            #    If a drag_handler is in use, this should probably be the
            # drag_handler itself(no current code compares it to any selobj --
            # it only isinstances it to decide what drag code to run), but if
            # some Atoms/Bonds/Jigs ever use self as a drag_handler, our
            # isinstance tests on thiswill be problematic; we may need an "are
            # you acting as a drag_handler" method instead. #####@@@@@
            # ]
        #bruce 060315 replaced drag_stickiness_limit_exceeded with
        # max_dragdist_pixels
        self.max_dragdist_pixels = 0
            # used in mouse_within_stickiness_limit

        self.atoms_of_last_deleted_jig = []
            # list of the real atoms connected to a deleted jig.
            # Used by jigLeftDouble()
            # to retreive the atoms of a recently deleted jig when double
            # clicking with 'Shift+Control'modifier keys pressed together.

        self.drag_handler = None #bruce 060725

        return



    # == drag_handler event handler methods [bruce 060728]======================

    # note: dragHandlerLeftDown() does not exist, since self.drag_handler is
    # only created by some other object's leftDown method

    def dragHandlerSetup(self, drag_handler, event):
        assert drag_handler is self.drag_handler #e clean up sometime? not sure
                                                #how
        self.cursor_over_when_LMB_pressed = 'drag_handler' # not presently used,
                                             #except for not being 'Empty Space'
        self.objectSetup(drag_handler) #bruce 060728
        if not drag_handler.handles_updates():
            self.w.win_update()
                # REVIEW (possible optim): can we (or some client code) make
                # gl_update_highlight cover this? [bruce 070626]
        return

    def dragHandlerDrag(self, drag_handler, event):
        ###e nim: for some kinds of them, we want to pick them in leftDown,
        ###then drag all picked objects, using self.dragto...
        try:
            method = getattr(drag_handler, 'DraggedOn', None) #e rename
            if method:
                old_selobj = self.o.selobj
                ###e args it might need:
                # - mode, for callbacks for things like update_selobj (which
                #   needs a flag to avoid glselect)
                # - event, to pass to update_selobj (and maybe other callbacks
                #   we offer)and ones it can callback for:
                # - offset, for convenient 3d motion of movable dragobjs
                # - maybe the mouseray, as two points?
                retval = method(event, self)
                # assume no update needed unless selobj changed
                #e so detect that... not sure if we need to, maybe set_selobj or
                #(probably) update_selobj does it?
                if old_selobj is not self.o.selobj:
                    if 0 and env.debug():
                        print "debug fyi: selobj change noticed by " \
                              "dragHandlerDrag, %r -> %r" % (old_selobj ,
                                                             self.o.selobj)
                        # WARNING: this is not a good enough detection, if any
                        # outside code also does update_selobj and changes it,
                        # since those changes won't be detected here. Apparently
                        # this happens when the mouse moves back onto a real
                        # selobj. Therefore I'm disabling this test for now. If
                        # we need it, we'll need to store old_selobj in self,
                        # between calls of this method.
                    pass
                pass
            pass
        except:
            print_compact_traceback("bug: exception in dragHandlerDrag ignored:")
        return

    def dragHandlerLeftUp(self, drag_handler, event):
        try:
            method = getattr(drag_handler, 'ReleasedOn', None)#e rename
            if method:
                retval = method(self.o.selobj, event, self)
                    #bruce 061120 changed args from (selobj, self) to
                    #(selobj, event, self) [where self is the mode object]
                self.w.win_update() ##k not always needed, might be redundant,
                                    ##should let the handler decide ####@@@@
                    # REVIEW (possible optim): can we make gl_update_highlight
                    # cover this? [bruce 070626]
                # lots of other stuff done by other leftUp methods here? ###@@@@
        except:
            print_compact_traceback("bug: exception in dragHandlerLeftUp ignored:")
        pass

    def dragHandlerLeftDouble(self, drag_handler, event): # never called as of
                                                          #070324; see also
                                                          #testmode.leftDouble
        if env.debug():
            print "debug fyi: dragHandlerLeftDouble is nim"
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
            # <picking> is used to let continue_selection_curve() and
            # end_selection_curve() know
            # if we are in the process of defining/drawing a selection curve
            # or not, where:
            # True = in the process of defining selection curve
            # False = finished/not defining selection curve
        selCurve_pt, selCurve_AreaPt = \
                     self.o.mousepoints(event, just_beyond = 0.01)
            # mousepoints() returns a pair (tuple) of points (Numeric arrays
            # of x,y,z)
            # that lie under the mouse pointer, just beyond the near
            # clipping plane
            # <selCurve_pt> and in the plane of the center of view <selCurve_AreaPt>.
        self.selCurve_List = [selCurve_pt]
            # <selCurve_List> contains the list of points used to draw the
            # selection curve.  The points lay in the plane parallel to the
            # screen, just beyond the front clipping plane, so that they are
            # alwaysinside the clipping volume.
        self.o.selArea_List = [selCurve_AreaPt]
            # <selArea_List> contains the list of points that define the
            # selection area.  The points lay in the plane parallel to the
            # screen and pass through the center of the view.  The list
            # is used by pickrect() and pickline() to make the selection.
        self.selCurve_StartPt = self.selCurve_PrevPt = selCurve_pt
            # <selCurve_StartPt> is the first point of the selection curve.
            # It is used by continue_selection_curve() to compute the net
            # distance between it and the current mouse position.
            # <selCurve_PrevPt> is the previous point of the selection curve.
            # It is used by  continue_selection_curve() to compute the distance
            # between the current mouse position and the previous one.
            # Both <selCurve_StartPt> and <selCurve_PrevPt> are used by
            # basicMode.drawpick().
        self.selCurve_length = 0.0
            # <selCurve_length> is the current length (sum) of all the selection
            # curve segments.

    def continue_selection_curve(self, event):
        """
        Add another line segment to the current selection curve.
        """
        if not self.picking:
            return

        selCurve_pt, selCurve_AreaPt = self.o.mousepoints(event, 0.01)
            # The next point of the selection curve, where <selCurve_pt> is the
            # point just beyondthe near clipping plane and <selCurve_AreaPt> is
            # in the plane of the center of view.
        self.selCurve_List += [selCurve_pt]
        self.o.selArea_List += [selCurve_AreaPt]

        self.selCurve_length += vlen(selCurve_pt - self.selCurve_PrevPt)
            # add length of new line segment to <selCurve_length>.

        chord_length = vlen(selCurve_pt - self.selCurve_StartPt)
            # <chord_length> is the distance between the (first and
            # last/current) endpoints of the
            # selection curve.

        if self.selCurve_length < 2*chord_length:
            # Update the shape of the selection_curve.
            # The value of <selShape> can change back and forth between lasso
            # and rectangle as the user continues defining the selection curve.
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
        #Don't select anything if the selection is locked.
        #@see: Select_GraphicsMode_MouseHelper_preMixin.selection_locked()
        if self.selection_locked():
            self.selCurve_List = []
            self.glpane.gl_update()
            return

        if not self.picking:
            return
        self.picking = False

        selCurve_pt, selCurve_AreaPt = self.o.mousepoints(event, 0.01)

        if self.selCurve_length / self.o.scale < 0.03:
            # didn't move much, call it a click
            #bruce 060331 comment: the behavior here is related to what it is
            # when we actually just click,
            # but it's implemented by different code -- for example,
            # delete_at_event in this case
            # as opposed to delete_atom_and_baggage in the other circumstance
            # (which both have similar
            # implementations of atom filtering and history messages, but are
            # in different files). It's not clear to me (reviewing this code)
            # whether the behavior should be (or is) identical;
            # whether or not it's identical, it would be better if common code
            # was used, to the extent that the behavior in these two
            # circumstances is supposed to be related.
            has_jig_selected = False

            if self.o.jigSelectionEnabled and self.jigGLSelect(event,
                                                               self.selSense):
                has_jig_selected = True

            if not has_jig_selected:
                # NOTES about bugs in this code, and how to clean it up:
                # the following methods rely on findAtomUnderMouse,
                # even when highlighting is enabled (not sure why -- probably
                # a bad historical reason or oversight); this means they don't
                # work for clicking internal bonds (predicted bug), and they
                # don't work for jigs, which means the above jigGLSelect call
                # (which internally duplicates the GL_SELECT code used to
                # update selobj, and the picking effects of the following
                # depending on selSense) is presently necessary, whether
                # or not highlighting is enabled.
                #
                # TODO: This is a mess, but cleaning it up requires rewriting
                # all of the following at once:
                # - this code, and similar call of jigGLSelect in Move_GraphicsMode
                # - unpick_at_event and the 3 other methods below
                #   - have them use selobj when highlighting is enabled
                #   - if desired, have them update selobj even when highlighting
                #     is disabled, as replacement for findAtomUnderMouse
                #     which would work for jigs (basically equivalent to
                #     existing code calling special jig select methods in those
                #     cases, but without requiring duplicated code)
                # - this would permit completely removing the methods
                #   jigGLSelect and get_jig_under_cursor from this class.
                # [bruce 080917 comment]
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

            self.o.shape = SelectionShape(self.o.right, self.o.up, self.o.lineOfSight)
                # Create the selection shape object.

            ## eyeball = (-self.o.quat).rot(V(0,0,6*self.o.scale)) - self.o.pov
            eyeball = self.o.eyeball() #bruce 080912 change, should be equivalent

            if self.selShape == SELSHAPE_RECT : # prepare a rectangle selection
                self.o.shape.pickrect(self.o.selArea_List[0],
                                      selCurve_AreaPt,
                                      -self.o.pov,
                                      self.selSense, \
                                      eye = (not self.o.ortho) and eyeball)
            else: # prepare a lasso selection
                self.o.shape.pickline(self.o.selArea_List,
                                      -self.o.pov, self.selSense, \
                                      eye = (not self.o.ortho) and eyeball)

            self.o.shape.select(self.o.assy) # do the actual selection.

            self.o.shape = None

        #Call the API method that decides whether to select/deselect anything
        #else (e.g. pick a DnaGroup if all its content is selected)
        self.end_selection_from_GLPane()

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

    def get_obj_under_cursor(self, event): # docstring appears wrong
        """
        Return the object under the cursor.  Only atoms, singlets and bonds
        are returned.
        Returns None for all other cases, including when a bond, jig or nothing
        is under the cursor. [warning: this docstring appears wrong.]

        @attention: This method was originally from class SelectAtoms_GraphicsMode. See
                    code comment for details
        """

        #@ATTENTION: This method was originally from class SelectAtoms_GraphicsMode.
        # It was mostly duplicated (with some changes) in SelectChunks_GraphicsMode
        # when that mode started permitting highlighting.
        # The has been modified and moved to selectMode class so that both
        # SelectAtoms_GraphicsMode and SelectChunks_GraphicsMode can use it -Ninad 2007-10-15


        #bruce 060331 comment: this docstring appears wrong, since the code
        # looks like it can return jigs.
        #bruce 070322 note: this will be overridden (extended) in testmode,
        #which will sometimes return a "background object"
        # rather than None, in order that leftDown can be handled by
        # background_object.leftClick in the same way as for other
        #drag_handler-returning objects.
        #
        ### WARNING: this is slow, and redundant with highlighting --
        ### only call it on mousedown or mouseup, never in move or drag.
        # [true as of 060726 and before; bruce 060726 comment]
        # It may be that it's not called when highlighting is on, and it has no
        # excuse to be, but I suspect it is anyway.
        # [bruce 060726 comment]
        if self.command.isHighlightingEnabled() and not self._suppress_highlighting:
            self.update_selatom(event) #bruce 041130 in case no update_selatom
                                       #happened yet
            # update_selatom() updates self.o.selatom and self.o.selobj.
            # self.o.selatom is either a real atom or a singlet [or None].
            # self.o.selobj can be a bond, and is used in leftUp() to determine
            # if a bond was selected.

            # Warning: if there was no GLPane repaint event (i.e. paintGL call)
            # since the last bareMotion,update_selatom can't make selobj/selatom
            # correct until the next time paintGL runs.
            # Therefore, the present value might be out of date -- but it does
            # correspond to whateverhighlighting is on the screen, so whatever
            # it is should not be a surprise to the user,so this is not too
            # bad -- the user should wait for the highlighting to catch up to
            # the mouse motion before pressing the mouse. [bruce 050705 comment]
            # [might be out of context, copied from other code]

            obj = self.o.selatom # a "highlighted" atom or singlet

            if obj is None and self.o.selobj:
                obj = self.o.selobj # a "highlighted" bond
                    # [or anything else, except Atom or Jig -- i.e. a
                    #general/drag_handler/Drawable selobj [bruce 060728]]
                if env.debug():
                    # I want to know if either of these things occur
                    #-- I doubt they do, but I'm not sure about Jigs [bruce 060728]
                    # (this does happen for Jigs, see below)
                    if isinstance(obj, Atom):
                        print "debug fyi: likely bug: selobj is Atom but not in selatom: %r" % (obj,)
                    elif isinstance(obj, Jig):
                        print "debug fyi: selobj is a Jig in get_obj_under_cursor (comment is wrong), for %r" % (obj,)
                        # I suspect some jigs can occur here
                        # (and if not, we should put them here
                        #-- I know of no excuse for jig highlighting
                        #  to work differently than for anything else) [bruce 060721]
                        # update 070413: yes, this happens (e.g. select some
                        # atoms and an rmotor jig, then drag the jig).
                    pass

            if obj is None: # a "highlighted" jig [i think this comment is
                            #misleading, it might really be nothing -- bruce 060726]
                obj = self.get_jig_under_cursor(event) # [this can be slow -- bruce comment 070322]
                if env.debug(): #######
                    print "debug fyi: get_jig_under_cursor returns %r" % (obj,) # [bruce 060721]
            pass

        else: # No hover highlighting
            obj = self.o.assy.findAtomUnderMouse(event,
                                                 self.command.isWaterSurfaceEnabled(),
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

        @attention: This method was originally from class SelectAtoms_GraphicsMode. See
                    code comment for details
        """

        #@ATTENTION: This method was originally from class SelectAtoms_GraphicsMode.
        # It was mostly duplicated (with some changes) in SelectChunks_GraphicsMode
        # when that mode started permitting highlighting.
        # The has been modified and moved to selectMode class so that both
        # SelectAtoms_GraphicsMode and SelectChunks_GraphicsMode can use it -Ninad 2007-10-12



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

        # If animating or zooming/panning/rotating with the MMB,
        # do not hover highlight anything. For more info about is_animating,
        # see GLPane.animateToView(). [mark 060404]
        if self.o.is_animating or \
           (self.o.button == "MMB" and not
            getattr(self, '_defeat_update_selobj_MMB_specialcase', False)):

            return
                # BUG: returning None violates this method's API (according to
                # docstring), but this apparently never mattered until now,
                # and it's not obvious how to fix it (probably to be correct
                # requires imitating the conditional set_selobj below); so
                # instead I'll just disable it in the new case that triggers it,
                # using _defeat_update_selobj_MMB_specialcase.
                # [bruce 070224]

        wX = event.pos().x()
        wY = glpane.height - event.pos().y()
        selobj = orig_selobj = glpane.selobj
        if selobj is not None:
            if glpane.stencilbits >= 1:
                # optimization: fast way to tell if we're still over the same
                # object as last time. (Warning: for now glpane.stencilbits is 1
                # even when true number of bits is higher; should be easy to fix
                # when needed.)
                #
                # WARNING: a side effect of QGLWidget.renderText is to clear the
                # stencil buffer, which defeats this optimization. This has been
                # true since at least Qt 4.3.5 (which we use as of now), but was
                # undocumented until Qt 4.4. This causes extra redraws whenever
                # renderText is used when drawing a frame and the mouse
                # subsequently moves within one highlighted object,
                # but should not cause an actual bug unless it affects the
                # occurrence of a bug in other code. [bruce 081211 comment]
                #
                # Note: double buffering applies only to the color buffer,
                # not the stencil or depth buffers, which have only one copy.
                # Therefore, this code would not work properly if run during
                # paintGL (even if GL_READ_BUFFER was set to GL_FRONT), since
                # paintGL might be modifying the buffer it reads. The setting
                # of GL_READ_BUFFER should have no effect on this code.
                # [bruce 081211 comment, based on Russ report of OpenGL doc]
                stencilbit = glReadPixelsi(wX, wY, 1, 1, GL_STENCIL_INDEX)[0][0]
                    # Note: if there's no stencil buffer in this OpenGL context,
                    # this gets an invalid operation exception from OpenGL.
                    # And by default there isn't one -- it has to be asked for
                    # when the QGLWidget is initialized.
                # stencilbit tells whether the highlighted drawing of selobj
                # got drawn at this point on the screen (due to both the shape
                # of selobj, and to the depth buffer contents when it was drawn)
                # but might be 0 even if it was drawn (due to the renderText
                # effect mentioned above).
            else:
                stencilbit = 0
                    # the correct value is "don't know"; 0 is conservative
                # maybe todo: collapse this code if stencilbit not used below;
                # and/or we might need to record whether we used this
                # conservative value
            if stencilbit:
                return True
                    # same selobj, no need for gl_update to change highlighting
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
            #For commands like SelectChunks_Command,  the 'water surface' 
            #is not defined.
            if self.command.isWaterSurfaceEnabled():
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
            # so set glpane.glselect_wanted to the command to do that and the 
            # necessary info for doing it.
            # Note: it might have been set before and not yet used;
            # if so, it's good to discard that old info, as we do.
            glpane.glselect_wanted = (wX, wY, wZ) # mouse pos, depth
                ###e and soon, instructions about whether to highlight selobj
                # based on its type (as predicate on selobj)
                ###e should also include current count of number of times
                # glupdate was ever called because model looks different,
                # and inval these instrs if that happens again before they
                # are used (since in that case wZ is no longer correct)
                
                # [addendum, bruce 081230: this is nonmodular -- we should call
                #  a glpane method to set that, and make it private.]
                
            # don't change glpane.selobj (since it might not even need to 
            # change) (ok??#k) -- the next paintGL will do that --
            # UNLESS the current mode wants us to change it 
            # [new feature, bruce 061218, perhaps a temporary kluge, but helps
            #  avoid a logic bug in this code, experienced often in testmode 
            #  due to its slow redraw]
            #
            # Note: I'm mostly guessing that this should be found in 
            # (and unique to) graphicsMode rather than currentCommand, 
            # in spite of being set only in testmode by current code.
            # That does make this code simpler, since graphicsMode is self.
            # [bruce 071010, same comment and change done in both duplications
            #  of this code, and in other places]
            if hasattr(self, 'UNKNOWN_SELOBJ'):
                # for motivation, see comment above, dated 061218
                glpane.selobj = getattr(self, 'UNKNOWN_SELOBJ')
                ## print "\n*** changed glpane.selobj from %r to %r" % (orig_selobj, glpane.selobj)
            
            #bruce 081230 part of fix for bug 2964 -- repaint the status bar
            # now, to work around a Qt or Mac OS bug (of unknown cause) which
            # otherwise might prevent it from being repainted later when
            # we store a message about a new selobj (in set_selobj or at the
            # end of paintGL). We need both lines to make sure this actually
            # repaints it now, even if the prior message was " " or "".
            env.history.statusbar_msg("") 
            env.history.statusbar_msg(" ") 
            
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

        @see: SelectAtoms_GraphicsMode.update_selatom for documentation.
        @see: selectMode.get_obj_under_cursor
        """
        # REVIEW: are any of the calls to this in selectMode methods,
        # which do nothing except in subclasses of SelectAtoms_GraphicsMode,
        # indications that the code they're in doesn't make sense except
        # in such subclasses? [bruce 071025 question]
        
        #I am not sure what you mean above. Assuming you meant: Is there a
        #method in this class selectMode, that calls this method
        # (i.e. calls selectMode.update_selatom)
        #Yes, there is a method self.selectMode.get_obj_under_cursor that calls
        #this method and thats why I kept a default implemetation that does
        #nothing -- Ninad 2007-11-16

        # No, I meant: is the fact that that call (for example) does nothing
        # (when not using a subclass of SelectAtoms_GraphicsMode)
        # a sign that some refactoring is desirable, which would (among
        # other effects) end up moving all calls of update_selatom into
        # subclasses of SelectAtoms* classes? [bruce 080917 reply]
        pass

    def get_jig_under_cursor(self, event):
        """
        Use the OpenGL picking/selection to select any jigs. Restore the projection and modelview
        matrices before returning.
        """
        ####@@@@ WARNING: The original code for this, in GLPane, has been
        ### duplicated and slightly modified
        # in at least three other places (search for glRenderMode to find them).
        # TWO OF THEM ARE METHODS IN THIS CLASS! This is bad; common code
        # should be used. Furthermore, I suspect it's sometimes needlessly
        # called more than once per frame;
        # that should be fixed too. [bruce 060721 comment]

        # BUG: both methods like this in this class are wrong when left/right
        # stereo is enabled. Ideally they should be removed.
        # For more info, see similar comment in jigGLSelect.
        # [bruce 080917 comment]

        if not self.o.jigSelectionEnabled:
            return None

        wX = event.pos().x()
        wY = self.o.height - event.pos().y()

        gz = self._calibrateZ(wX, wY) # note: this redraws the entire model
        if gz >= GL_FAR_Z:  # Empty space was clicked--This may not be true for translucent face [Huaicai 10/5/05]
            return None

        pxyz = A(gluUnProject(wX, wY, gz))
        pn = self.o.out
        pxyz -= 0.0002 * pn
        dp = - dot(pxyz, pn)

        # Save project matrix before it's changed
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()

        current_glselect = (wX, wY, 3, 3)
        self.o._setup_projection( glselect = current_glselect)

        glSelectBuffer(self.o.SIZE_FOR_glSelectBuffer)
        glRenderMode(GL_SELECT)
        glInitNames()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()  # Save modelview matrix before it's changed
        assy = self.o.assy
        try:
            glClipPlane(GL_CLIP_PLANE0, (pn[0], pn[1], pn[2], dp))
            glEnable(GL_CLIP_PLANE0)
            def func():
                assy.draw(self.o)
            self.o._call_func_that_draws_model( func, drawing_phase = 'main')
            self.o.call_Draw_after_highlighting(self, pickCheckOnly = True)
            glDisable(GL_CLIP_PLANE0)
        except:
            # BUG: this except clause looks wrong. It doesn't return,
            # therefore it results in two calls of glRenderMode(GL_RENDER).
            # [bruce 080917 comment]
            
            # Restore Model view matrix, select mode to render mode
            msg = "exception in code around mode.Draw_after_highlighting() " \
                  "during GL_SELECT; ignored; restoring modelview matrix: "
            print_compact_traceback(msg + ": ")
            glPopMatrix()
            glRenderMode(GL_RENDER)
        else:
            # Restore Model view matrix
            glPopMatrix()

        # Restore project matrix and set matrix mode to ModelView
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glFlush()

        hit_records = list(glRenderMode(GL_RENDER))
        for (near,far,names) in hit_records: # see example code, renderpass.py
            if debug_flags.atom_debug and 0:
                print "hit record: near,far,names:",near,far,names
            if 1:
                # partial workaround for bug 1527. This can be removed once that bug (in drawer.py)
                # is properly fixed. This exists in two places -- GLPane.py and modes.py. [bruce 060217]
                if names and names[-1] == 0:
                    print "%d(m) partial workaround for bug 1527: removing 0 from end of namestack:" % env.redraw_counter, names
                    names = names[:-1]
            if names:
                obj = assy.object_for_glselect_name(names[-1])
                #self.glselect_dict[id(obj)] = obj # now these can be rerendered specially, at the end of mode.Draw
                if isinstance(obj, Jig):
                    return obj
        return None # from get_jig_under_cursor

    # ==
    
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
    #   review why reset_drag_vars is only called in SelectAtoms_GraphicsMode but the
    #    vars are used in the superclass selectMode
    #   [later 070412: maybe because the methods calling it are themselves only
    #    called from SelectAtoms_GraphicsMode? it looks that way anyway]
    #   [later 070412: ###WARNING: in Qt3, reset_drag_vars is defined in
    #   SelectAtoms_GraphicsMode, but in Qt4, it's defined in selectMode.]
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
        from model.BorrowerChunk import BorrowerChunk
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

    #==HIGHLIGHTING  ===========================================================

    def selobj_highlight_color(self, selobj):
        """
        [GraphicsMode API method]

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
        # from SelectAtoms_GraphicsMode. -- Ninad 2007-10-14
        if not self.command.isHighlightingEnabled():
            return None

        #####@@@@@ if self.drag_handler, we should probably let it
        # override all this
        # (so it can highlight just the things it might let you
        # DND its selobj to, for example),
        # even for Atom/Bondpoint/Bond/Jig, maybe even when not
        # self.command.isHighlightingEnabled(). [bruce 060726 comment]

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
        Return the Atom highlight color. Default implementation returns 'None'
        Overridden in subclasses.
        @return: Highlight color of the object (Atom or Singlet)
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

    def _calibrateZ(self, wX, wY): # by huaicai; bruce 071013 moved this here from GraphicsMode
        """
        Because of translucent plane drawing or other special drawing,
        the depth value may not be accurate. We need to
        redraw them so we'll have correct Z values.
        """
        # REVIEW: why does this not need to clear the depth buffer?
        # If caller needs to, that needs to be documented.
        # [bruce 080917 comment]
        glMatrixMode(GL_MODELVIEW)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)

        if self.o.call_Draw_after_highlighting(self, pickCheckOnly = True):
            # Only when we have translucent planes drawn
            def func():
                self.o.assy.draw(self.o)
            self.o._call_func_that_draws_model( func, drawing_phase = 'main')
            pass

        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

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

        # BUG: both methods like this in this class are wrong when left/right
        # stereo is enabled. The best fix would be to remove them completely,
        # since they should never have existed at all, since general highlighting
        # code handles jigs. Unfortunately removing them is hard --
        # for how to do it, see comment near the call of this method
        # in this file. [bruce 080917 comment]

        # this method has two calls, one in this file and one in commands/Move/Move_GraphicsMode
        # [bruce 090227 comment]

        wX = event.pos().x()
        wY = self.o.height - event.pos().y()

        gz = self._calibrateZ(wX, wY) # note: this sometimes redraws the entire model
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

        glSelectBuffer(self.o.SIZE_FOR_glSelectBuffer)
        glRenderMode(GL_SELECT)
        glInitNames()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()  ## Save model/view matrix before it's changed
        assy = self.o.assy
        try:
            glClipPlane(GL_CLIP_PLANE0, (pn[0], pn[1], pn[2], dp))
            glEnable(GL_CLIP_PLANE0)
            def func():
                assy.draw(self.o)
            self.o._call_func_that_draws_model( func, drawing_phase = 'main')
            self.o.call_Draw_after_highlighting(self, pickCheckOnly = True)
            glDisable(GL_CLIP_PLANE0)
        except:
            # Restore Model view matrix, select mode to render mode
            glPopMatrix()
            glRenderMode(GL_RENDER)
            msg = "exception in drawing during GL_SELECT, ignored; restoring modelview matrix"
            print_compact_traceback(msg + ": ")
        else:
            # Restore Model view matrix
            glPopMatrix()

        # Restore project matrix and set matrix mode to Model/View
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glFlush()

        hit_records = list(glRenderMode(GL_RENDER))
        if debug_flags.atom_debug and 0:
            print "%d hits" % len(hit_records)
        for (near,far,names) in hit_records: # see example code, renderpass.py
            if 1:
                # partial workaround for bug 1527. This can be removed once that bug (in drawer.py)
                # is properly fixed. This exists in two places -- GLPane.py and modes.py. [bruce 060217]
                if names and names[-1] == 0:
                    print "%d(m) partial workaround for bug 1527: removing 0 from end of namestack:" % env.redraw_counter, names
                    names = names[:-1]
            if names:
                obj = assy.object_for_glselect_name(names[-1])
                #self.glselect_dict[id(obj)] = obj # now these can be rerendered specially, at the end of mode.Draw
                if isinstance(obj, Jig):
                    if selSense == SUBTRACT_FROM_SELECTION: #Ctrl key, unpick picked
                        if obj.picked:
                            obj.unpick()
                    elif selSense == ADD_TO_SELECTION: #Shift key, Add pick
                        if not obj.picked:
                            obj.pick()
                    else:               #Without key press, exclusive pick
                        assy.unpickall_in_GLPane() # was: unpickparts, unpickatoms [bruce 060721]
                        if not obj.picked:
                            obj.pick()
                    return True
        return False # from jigGLSelect

    def toggleJigSelection(self):
        self.o.jigSelectionEnabled = not self.o.jigSelectionEnabled

    pass # end of class Select_basicGraphicsMode

# ==

class Select_GraphicsMode(Select_basicGraphicsMode):
    """
    """
    # Imitate the init and property code in GraphicsMode, but don't inherit it.
    # (Remember to replace all the occurrences of its superclass with our own.)
    # (When this is later merged with its superclass, most of this can go away
    #  since we'll then be inheriting GraphicsMode here.)

    # (Or can we inherit GraphicsMode *after* the main superclass, and not have
    #  to do some of this? I don't know. ### find out! [I think I did this in PanLikeMode.]
    #  At least we'd probably still need this __init__ method.
    #  If this pattern works, then in *our* subclasses we'd instead post-inherit
    #  this class, Select_GraphicsMode.)

    def __init__(self, command):
        self.command = command
        glpane = self.command.glpane
        Select_basicGraphicsMode.__init__(self, glpane)
        return

    # (the rest would come from GraphicsMode if post-inheriting it worked,
    #  or we could split it out of GraphicsMode as a post-mixin to use there
    #  and here)

    def _get_commandSequencer(self):
        return self.command.commandSequencer

    commandSequencer = property(_get_commandSequencer)

    def set_cmdname(self, name):
        self.command.set_cmdname(name)
        return

    pass

# end

    
