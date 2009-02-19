# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
GraphicsMode.py -- base class for "graphics modes" (display and GLPane event handling)

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 071009 split modes.py into Command.py and GraphicsMode.py,
leaving only temporary compatibility mixins in modes.py.
For prior history see modes.py docstring before the split.

TODO:

A lot of methods in class GraphicsMode are private helper methods,
available to subclasses and/or to default implems of public methods,
but are not yet named as private or otherwise distinguished
from API methods. We should turn anyGraphicsMode into GraphicsMode_API
[done as of 071028],
add all the API methods to it, and rename the other methods
in class GraphicsMode to look private.
"""

import math # just for pi
from Numeric import exp

from PyQt4.Qt import Qt
from PyQt4.Qt import QMenu

from geometry.VQT import V, Q, vlen, norm, planeXline, ptonline
from graphics.drawing.CS_draw_primitives import drawline
from graphics.drawing.CS_draw_primitives import drawTag
from graphics.drawing.drawers import drawOriginAsSmallAxis
from graphics.drawing.drawers import drawaxes, drawPointOfViewAxes
from graphics.drawing.drawers import drawrectangle

from utilities.debug import print_compact_traceback

from utilities import debug_flags
import foundation.env as env
from graphics.behaviors.shape import get_selCurve_color
from utilities.constants import SELSHAPE_RECT
from utilities.constants import yellow
from utilities.prefs_constants import zoomInAboutScreenCenter_prefs_key
from utilities.prefs_constants import zoomOutAboutScreenCenter_prefs_key
from utilities.prefs_constants import displayOriginAxis_prefs_key
from utilities.prefs_constants import displayOriginAsSmallAxis_prefs_key
from utilities.prefs_constants import displayPOVAxis_prefs_key
from utilities.prefs_constants import displayConfirmationCorner_prefs_key
from utilities.prefs_constants import panArrowKeysDirection_prefs_key

from model.chem import Atom
from model.bonds import Bond
from foundation.Utility import Node


import time

from command_support.GraphicsMode_API import GraphicsMode_API

# ==

class nullGraphicsMode(GraphicsMode_API):
    """
    do-nothing GraphicsMode (for internal use only) to avoid crashes
    in case of certain bugs during transition between GraphicsModes
    """

    # needs no __init__ method; constructor takes no arguments

    # WARNING: the next two methods are similar in all "null objects", of which
    # we have nullCommand and nullGraphicsMode so far. They ought to be moved
    # into a common nullObjectMixin for all kinds of "null objects". [bruce 071009]

    def noop_method(self, *args, **kws):
        if debug_flags.atom_debug:
            print "fyi: atom_debug: nullGraphicsMode noop method called -- probably ok; ignored"
        return None #e print a warning?
    def __getattr__(self, attr): # in class nullGraphicsMode
        # note: this is not inherited by other GraphicsMode classes,
        # since we are not their superclass
        if not attr.startswith('_'):
            if debug_flags.atom_debug:
                print "fyi: atom_debug: nullGraphicsMode.__getattr__(%r) -- probably ok; returned noop method" % attr
            return self.noop_method
        else:
            raise AttributeError, attr #e args?

    # GraphicsMode-specific null methods

    def setDrawTags(self, *args, **kws):
        # This would not be needed here if calls were fixed,
        # as commented on them; thus, not part of GraphicsMode_API
        # [bruce 081002 comment]
        pass

    pass # end of class nullGraphicsMode

# ==

class basicGraphicsMode(GraphicsMode_API):
    """
    Common code between class GraphicsMode (see its docstring)
    and old-code-compatibility class basicMode.
    Will be merged with class GraphicsMode (keeping that one's name)
    when basicMode is no longer needed.
    """

    # Initialize timeAtLastWheelEvent to None. It is assigned
    # in self.wheelEvent and used in SelectChunks_GraphicsMode.bareMotion
    # to disable highlighting briefly after any mouse wheel event.
    # Motivation: when user is scrolling the wheel to zoom in or out,
    # and at the same time the mouse moves slightly, we want to make sure
    # that the object under the cursor is not highlighted (mainly for
    # performance reasons).
    timeAtLastWheelEvent = None

    # NOTE: subclasses will have to make self.command point to the command
    # object (a running command which owns the graphics mode object).
    # This is done differently in different subclasses, since in some of
    # them, those are the same object.

    # Draw tags on entities in the 3D workspace if wanted. See self._drawTags
    # for details.
    _tagPositions = ()
    _tagColor = yellow
    
    picking = False # used as instance variable in some mouse methods
    
    def __init__(self, glpane):
        """
        """
        # guessing self.pw is only needed in class Command (or not at all):
        ## self.pw = None # pw = part window

        # initialize attributes used by methods to refer to
        # important objects in their runtime environment

        # make sure we didn't get passed the commandSequencer by accident
        glpane.gl_update # not a call, just make sure it has this method

        self.glpane = glpane
        self.win = glpane.win

        ## self.commandSequencer = self.win.commandSequencer #bruce 070108
        # that doesn't work, since when self is first created during GLPane creation,
        # self.win doesn't yet have this attribute:
        # (btw the exception from this is not very understandable.)
        # So instead, we define a property that does this alias, below.

        # Note: the attributes self.o and self.w are deprecated, but often used.
        # New code should use some other attribute, such as self.glpane or
        # self.commandSequencer or self.win, as appropriate. [bruce 070613, 071008]
        self.o = self.glpane # (deprecated)
        self.w = self.win # (deprecated)

        # set up context menus
        self._setup_menus_in_init()

        return # from basicGraphicsMode.__init__

    def Enter_GraphicsMode(self):
        """
        Perform side effects in self (a GraphicsMode) when entering it
        or reentering it. Typically this involves resetting or initializing
        state variables.
        
        @note: Called in self.command.command_entered.
        
        @see: B{baseCommand.command_entered}
        """
        #NOTE: See a comment in basicCommand.Enter for things still needed
        # to be done

        self.picking = False
        
    def isCurrentGraphicsMode(self): #bruce 071010, for GraphicsMode API
        """
        Return a boolean to indicate whether self is the currently active GraphicsMode.

        See also Command.isCurrentCommand.
        """
        # see WARNING in CommandSequencer about this needing revision if .graphicsMode
        # might have been wrapped with an API-enforcement (or any other) proxy.
        return self.glpane.graphicsMode is self

    def __get_parentGraphicsMode(self): #bruce 081223
        # review: does it need to check whether the following exists?
        return self.command.parentCommand.graphicsMode

    parentGraphicsMode = property(__get_parentGraphicsMode)
    
    def _setup_menus_in_init(self):
        if not self.command.call_makeMenus_for_each_event:
            self._setup_menus( )

    def _setup_menus_in_each_cmenu_event(self):
        if self.command.call_makeMenus_for_each_event:
            self._setup_menus( )

    def _setup_menus(self):
        """
        Call self.command.setup_graphics_menu_specs(),
        assume it sets all the menu_spec attrs on self.command,

        Menu_spec,
        Menu_spec_shift,
        Menu_spec_control,

        and turn them into self._Menu1 etc, which are QMenus,
        one of which will be posted by the caller
        depending on the modkeys of an event.
        (TODO: when we know we're called for each event, optim by producing
         only one of those QMenus, and tell setup_graphics_menu_specs
         to optim in a similar way.)
        """
        # Note: this was split between Command.setup_graphics_menu_specs and
        # GraphicsMode._setup_menus, bruce 071009

        command = self.command

        command.setup_graphics_menu_specs()

        self._Menu1 = QMenu()
        self.makemenu(command.Menu_spec, self._Menu1)

        self._Menu2 = QMenu()
        self.makemenu(command.Menu_spec_shift, self._Menu2)

        self._Menu3 = QMenu()
        self.makemenu(command.Menu_spec_control, self._Menu3)

        return

    # ==

    # confirmation corner methods [bruce 070405-070409, 070627]

    _ccinstance = None

    def draw_overlay(self): #bruce 070405, revised 070627
        """
        called from GLPane with same drawing coordsys as for model
        [part of GLPane's drawing interface to modes]
        """
        # conf corner is enabled by default for A9.1 (070627);
        # requires exprs module and Python Imaging Library
        if not env.prefs[displayConfirmationCorner_prefs_key]:
            return
        
        # which command should control the confirmation corner?
        command = self.command #bruce 071015 to fix bug 2565
            # (originally done inside find_or_make_confcorner_instance)
            # Note: we cache this on the Command, not on the GraphicsMode.
            # I'm not sure that's best, though since the whole thing seems to assume
            # they have a 1-1 correspondence, it may not matter much.
            # But in the future if weird GraphicsModes needed their own
            # conf. corner styles or implems, it might need revision.
       
        #bruce 080905 fix bug 2933 
        command = command.command_that_supplies_PM()
        
        # figure out what kind of confirmation corner command wants, and draw it
        import graphics.behaviors.confirmation_corner as confirmation_corner
        cctype = command.want_confirmation_corner_type()
        self._ccinstance = confirmation_corner.find_or_make_confcorner_instance(cctype, command)
            # Notes:
            # - we might use an instance cached in command (in an attr private to that helper function);
            # - this might be as specific as both args passed above, or as shared as one instance
            #   for the entire app -- that's up to it;
            # - if one instance is shared for multiple values of (cctype, command),
            #   it might store those values in that instance as a side effect of
            #   find_or_make_confcorner_instance;
            # - self._ccinstance might be None.
        if self._ccinstance is not None:
            # it's an instance we want to draw, and to keep around for mouse event handling
            # (even though it's not necessarily still valid the next time we draw;
            #  fortunately we'll rerun this method then and recompute cctype and command, etc)
            self._ccinstance.draw()
        return

    def mouse_event_handler_for_event_position(self, wX, wY): #bruce 070405
        """
        Some mouse events should be handled by special "overlay" widgets
        (e.g. confirmation corner buttons) rather than by the GLPane & mode's
        usual event handling functions. This mode API method is called by the
        GLPane to determine whether a given mouse position (in OpenGL-style
        window coordinates, 0,0 at bottom left) lies over such an overlay widget.

        Its return value is saved in glpane.mouse_event_handler -- a public
        fact, which can be depended on by mode methods such as update_cursor --
        and should be None or an object that obeys the MouseEventHandler interface.
        (Note that modes themselves don't (currently) provide that interface --
        they get their mouse events from GLPane in a more-digested way than that
        interface supplies.)

        Note that this method is not called for all mouse events -- whether
        it's called depends on the event type (and perhaps modkeys). The caller's
        policy as of 070405 (fyi) is that the mouse event handler is not changed
        during a drag, even if the drag goes off the overlay widget, but it is
        changed during bareMotion if the mouse goes on or off of one. But that
        policy is the caller's business, not self's.

        [Subclasses should override this if they show extra or nonstandard
        overlay widgets, but as of the initial implem (070405), that's not likely
        to be needed.]
        """
        if self._ccinstance is not None:
            method = getattr(self._ccinstance, 'want_event_position', None)
            if method:
                if method(wX, wY):
                    return self._ccinstance
            elif debug_flags.atom_debug:
                print "atom_debug: fyi: ccinstance %r with no want_event_position method" % (self._ccinstance,)
        return None


    # ==

    def Draw(self):
        """
        Generic Draw method, with drawing code common to all modes.
        Specific modes should call this somewhere within their own Draw method,
        unless they have a good reason not to.

        @note: it doesn't draw the model,
               since not all modes want to always draw it.

        @note: this default implementation calls private methods such as
               _drawTags, _drawSpecialIndicators, and _drawLabels,
               but these are not part of the GraphicsMode API
               and need never be called directly. They can still
               be overridden in any subclasses of GraphicsMode
               (the base class of all actual GraphicsModes)
               and this will work as expected, provided either the
               superclass or parentGraphicsMode Draw method is being
               called, as it usually should be.
        """
        # Review: it might be cleaner to revise _drawTags,
        # _drawSpecialIndicators, and _drawLabels, to be public methods
        # of GraphicsMode_API. Presently they are not part of it at all;
        # they are only part of the subclass-extending API of this base
        # class GraphicsMode. [bruce 081223 comment]

        # Draw the Origin axes.
        # WARNING: this code is duplicated, or almost duplicated,
        # in GraphicsMode.py and GLPane.py.
        # It should be moved into a common method in drawers.py.
        # [bruce 080710 comment]
        if env.prefs[displayOriginAxis_prefs_key]:
            if env.prefs[displayOriginAsSmallAxis_prefs_key]: #ninad060920
                drawOriginAsSmallAxis(self.o.scale, (0.0, 0.0, 0.0))
                #ninad060921: note: we are also drawing a dotted origin displayed only when
                #the solid origin is hidden. See def standard_repaint_0 in GLPane.py
                #ninad060922 passing self.o.scale makes sure that the origin / pov axes are not zoomable
            else:
                drawaxes(self.o.scale, (0.0, 0.0, 0.0), coloraxes = True)

        if env.prefs[displayPOVAxis_prefs_key]:
            drawPointOfViewAxes(self.o.scale, -self.o.pov)

        # Draw the Point of View axis unless it is at the origin (0, 0, 0) AND draw origin as cross wire is true ninad060920
        if env.prefs[displayPOVAxis_prefs_key]:
            if not env.prefs[displayOriginAsSmallAxis_prefs_key]:
                if vlen(self.o.pov):
                    drawPointOfViewAxes(self.o.scale, -self.o.pov)
                else:
                    # POV is at the origin (0, 0, 0).  Draw it if the Origin axis is not drawn. Fixes bug 735.
                    if not env.prefs[displayOriginAxis_prefs_key]:
                        drawPointOfViewAxes(self.o.scale, -self.o.pov)
            else:
                drawPointOfViewAxes(self.o.scale, -self.o.pov)

        #Draw tags if any
        self._drawTags()

        #Draw Special indicators if any (subclasses can draw custom indicators)
        self._drawSpecialIndicators()
        
        #Draw labels if any 
        self._drawLabels()


        # bruce 040929/041103 debug code -- for developers who enable this
        # feature, check for bugs in atom.picked and mol.picked for everything
        # in the assembly; print and fix violations. (This might be slow, which
        # is why we don't turn it on by default for regular users.)
        if debug_flags.atom_debug:
            self.o.assy.checkpicked(always_print = 0)
        return

    def setDrawTags(self, tagPositions = (), tagColor = yellow): # by Ninad
        """
        Public method that accepts requests to draw tags at the given
        tagPositions.

        @note: this saves its arguments as private state in self, but does
        not actually draw them -- that is done later by self._drawTags().
        Thus, this method is safe to call outside of self.Draw() and without
        ensuring that self.glpane is the current OpenGL context.
        
        @param tagPositions: The client can provide a list or tuple of tag
                            base positions. The default value for this parameter
                            is an empty tuple. Thus, if no tag position is
                            specified, it won't draw any tags and will also
                            clear the previously drawn tags.
        @type tagPositions: list or tuple
        
        @param tagColor: The color of the tags
        @type tagColor:  B{A}
        
        @see: self._drawTags
        @see: InsertDna_PropertyManager.clearTags for an example
        """
        #bruce 081002 renamed from drawTags -> setDrawTags, to avoid confusion,
        # since it sets state but doesn't do any drawing
        self._tagPositions = list(tagPositions)
        self._tagColor = tagColor

    def _drawTags(self):
        """
        Private method, called in self.Draw that actually draws the tags
        saved in self._tagPositions by self.setDrawTags.
        """

        if self._tagPositions:
            for basePoint in self._tagPositions:
                if self.glpane.scale < 5:
                    lineScale = 5
                else:
                    lineScale = self.glpane.scale

                endPoint = basePoint + self.glpane.up*0.2*lineScale

                pointSize = round(self.glpane.scale*0.5)

                drawTag(self._tagColor,
                        basePoint,
                        endPoint,
                        pointSize = pointSize)


    def _drawSpecialIndicators(self):
        """
        Subclasses should override this method. Default implementation does
        nothing. Many times, the graphics mode needs to draw some things to
        emphasis some entities in the 3D workspace.

        Example: In MultiplednaSegmentResize_GraphicsMode, it draws
        transparent cylinders around the DnaSegments being resized at once.
        This visually distinguishes them from the rest of the segments.

        @see: MultipleDnaSegmentResize_GraphicsMode._drawSpecialIndicators()
        @TODO: cleanup self._drawTags() that method and this method look
        similar but the actual implementation is different.
        """
        pass
    
    def _drawLabels(self):
        """
        Subclasses should override this method. Default implementation does
        nothing. Many times, the graphics mode needs to draw some labels on the
        top of everything. Called in self.Draw()
        
        Example: For a DNA, user may want to turn on the labels next to the 
        atoms indicating the base numbers. 
        
        @see: BreakOrJoinStrands_GraphicsMode._drawLabels() for an example.   
        
        @see: self._drawSpecialIndicators()
        @see: self.Draw()
        """
        pass

    def Draw_after_highlighting(self, pickCheckOnly = False): #bruce 050610
        """
        Do more drawing, after the main drawing code has completed its
        highlighting/stenciling for selobj.
        Caller will leave glstate in standard form for Draw.
        Implems are free to turn off depth buffer read or write
        (but must restore standard glstate when done, just as for
        GraphicsMode Draw() method).

        Warning: anything implems do to depth or stencil buffers will affect
        the standard selobj-check in bareMotion
        (which as of 050610 was only used in BuildAtoms_Graphicsmode).

        [New method in mode API as of bruce 050610.
         General form not yet defined -- just a hack for Build mode's
         water surface. Could be used for transparent drawing in general.

        UPDATE 2008-06-20: Another example use of this method:
        Used for selecting a Reference Plane when user clicks inside the
        filled plane (i.e. not along the edges).
        See new API method Node.draw_after_highlighthing
        which is called here. It fixes bug 2900--  Ninad ]

        @see: Plane.draw_after_highlighthing()
        @see: Node.draw_after_highlighitng()
        """
        return self.o.assy.part.topnode.draw_after_highlighting(
            self.glpane,
            self.glpane.displayMode,
            pickCheckOnly = pickCheckOnly )

    def selobj_still_ok(self, selobj):
        """
        [overrides GraphicsMode_API method]
        
        Say whether a highlighted mouseover object from a prior draw
        (done by the same GraphicsMode) is still ok.
        
        In this implementation: if our special cases of various classes
        of selobj don't hold, we ask selobj (using a method of the same name
        in the selobj API, though it's not defined in Selobj_API for now);
        if that doesn't work, we assume selobj defines .killed, and answer yes
        unless it's been killed.
        """
        try:
            # This sequence of conditionals fix bugs 1648 and 1676. mark 060315.
            # [revised by bruce 060724 -- merged in selobj.killed() condition, dated 050702,
            #  which was part of fix 1 of 2 redundant fixes for bug 716 (both fixes are desirable)]
            if isinstance(selobj, Atom):
                return not selobj.killed() and selobj.molecule.part is self.o.part
            elif isinstance(selobj, Bond):
                return not selobj.killed() and selobj.atom1.molecule.part is self.o.part
            elif isinstance(selobj, Node): # e.g. Jig
                return not selobj.killed() and selobj.part is self.o.part
            else:
                try:
                    method = selobj.selobj_still_ok
                        # REVIEW: this method is not defined in Selobj_API; can it be?
                except AttributeError:
                    pass
                else:
                    res = method(self.o) # this method would need to compare glpane.part to something in selobj
                        ##e it might be better to require selobj's to return a part, compare that here,
                        # then call this for further conditions
                    if res is None:
                        print "likely bug: %r.selobj_still_ok(glpane) returned None, "\
                              "should return boolean (missing return statement?)" % (selobj,)
                    return res
            if debug_flags.atom_debug:
                print "debug: selobj_still_ok doesn't recognize %r, assuming ok" % (selobj,)
            return True
        except:
            if debug_flags.atom_debug:
                print_compact_traceback("atom_debug: ignoring exception: ")
            return True # let the selobj remain
        pass

    def drawHighlightedObjectUnderMouse(self, glpane, selobj, hicolor):
        """
        [overrides GraphicsMode_API method]

        Subclasses should override this as needed, though most don't need to:

        Draw selobj in highlighted form for being the object under the mouse,
        as appropriate to this graphics mode.
        [TODO: document this properly: Use hicolor as its color
        if you return sensible colors from method XXX.]

        Note: selobj is typically glpane.selobj, but don't assume this.
        """
        selobj.draw_in_abs_coords(glpane, hicolor)

    def draw_glpane_label(self, glpane):
        """
        #doc [see doc in the glpane method we call] [#doc coord sys when called]
        
        @note: called from GLPane.paintGL shortly after graphicsMode.Draw()
        """
        #bruce 090219 moved this here from part.py, renamed from draw_text_label
        # (after refactoring it the prior day, 090218)
        
        # (note: caller catches exceptions, so we don't have to bother)

        text = self.glpane.part.glpane_label_text()
        if text:
            glpane.draw_glpane_label_text(text)
        return

    # ==
    
    def end_selection_from_GLPane(self):
        """
        GraphicsMode API method that decides whether to do some additional
        selection/ deselection (delegates this to a node API method)

        Example: If all content od a Dna group is selected (such as
        direct members, other logical contents), then pick the whole DnaGroup

        @see: Node.pick_if_all_glpane_content_is_picked()
        @see: Select_GraphicsMode.end_selection_curve() for an example use
        """
        part = self.win.assy.part

        class_list = (self.win.assy.DnaStrandOrSegment,
                      self.win.assy.DnaGroup,
                      self.win.assy.NanotubeSegment
                  )

        topnode = part.topnode
        topnode.call_on_topmost_unpicked_nodes_of_certain_classes(
            lambda node: node.pick_if_all_glpane_content_is_picked(),
            class_list )
        return

    def dragstart_using_GL_DEPTH(self, event, **kws):
        """
        Use the OpenGL depth buffer pixel at the coordinates of event
        (which works correctly only if the proper GL context, self.o, is current -- caller is responsible for this)
        to guess the 3D point that was visually clicked on. See GLPane version's docstring for details.

        [Note: this is public for event handlers using this object
         (whether in subclasses or external objects),
         but it's not part of the GraphicsMode interface from the GLPane.]
        """
        res = self.o.dragstart_using_GL_DEPTH(event, **kws) # note: res is a tuple whose length depends on **kws
        return res

    def dragstart_using_plane_depth(self, 
                                    event, 
                                    plane= None,
                                    planeAxis = None, 
                                    planePoint = None, 
                                    ):
        
        res = self.o.dragstart_using_plane_depth(event, 
                                                 plane= plane,
                                                 planeAxis = planeAxis, 
                                                 planePoint = planePoint, 
                                                 ) # note: res is a tuple whose length depends on **kws
        return res

    def dragto(self, point, event, perp = None):
        """
        Return the point to which we should drag the given point,
        if event is the drag-motion event and we want to drag the point
        parallel to the screen (or perpendicular to the given direction "perp"
        if one is passed in), keeping the point visibly touching the mouse cursor hotspot.

        (This is only correct for extended objects if 'point' (as passed in, and as retval is used)
        is the point on the object surface which was clicked on (not e.g. the center).
        For example, dragto(a.posn(),...) is incorrect code, unless the user happened to
        start the drag with a mousedown right over the center of atom <a>. See jigDrag
        in some subclasses for an example of correct usage.)
        """
        #bruce 041123 split this from two methods, and bugfixed to make dragging
        # parallel to screen. (I don't know if there was a bug report for that.)
        # Should be moved into modes.py and used in Move_Command too. 
        #[doing that, 060316]
        p1, p2 = self.o.mousepoints(event)
        if perp is None:
            perp = self.o.out
        point2 = planeXline(point, perp, p1, norm(p2-p1)) # args are (ppt, pv, lpt, lv)
        if point2 is None:
            # should never happen (unless a bad choice of perp is passed in),
            # but use old code as a last resort (it makes sense, and might even be equivalent for default perp)
            if env.debug(): #bruce 060316 added debug print; it should remain indefinitely if we rarely see it
                print "debug: fyi: dragto planeXline failed, fallback to ptonline", point, perp, p1, p2
            point2 = ptonline(point, p1, norm(p2-p1))
        return point2

    def dragto_with_offset(self, point, event, offset): #bruce 060316 for bug 1474
        """
        Convenience wrapper for dragto:

        Use this to drag objects by points other than their centers,
        when the calling code prefers to think only about the center positions
        (or some other reference position for the object).

        Arguments:
        - <point> should be the current center (or other reference) point of the object.
        - The return value will be a new position for the same reference point as <point> comes from
          (which the caller should move the object to match, perhaps subject to drag-constraints).
        - <event> should be an event whose .pos().x() and .pos.y() supply window coordinates for the mouse
        - <offset> should be a vector (fixed throughout the drag) from the center of the object
          to the actual dragpoint (i.e. to the point in 3d space which should appear to be gripped by the mouse,
          usually the 3d position of a pixel which was drawn when drawing the object
          and which was under the mousedown which started the drag).

        By convention, modes can store self.drag_offset in leftDown and pass it as <offset>.

        Note: we're not designed for objects which rotate while being dragged, as in e.g. dragSinglets,
        though using this routine for them might work better than nothing (untested ##k). In such cases
        it might be better to pass a different <offset> each time (not sure), but the only perfect
        solution is likely to involve custom code which is fully aware of how the object's
        center and its dragpoint differ, and of how the offset between them rotates as the object does.
        """
        return self.dragto(point + offset, event) - offset

    # middle mouse button actions -- these support a trackball, and
    # are the same for all GraphicsModes (with a few exceptions)
    
    def middleDown(self, event):
        """
        Set up for rotating the view with MMB+Drag.
        """
        self.update_cursor()
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0], self.o.MousePos[1])
        self.picking = True

        # Turn off hover highlighting while rotating the view with middle mouse button. Fixes bug 1657. Mark 060805.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.

    def middleDrag(self, event):
        """
        Rotate the view with MMB+Drag.
        """
        # Huaicai 4/12/05: Originally 'self.picking = False in both middle*Down
        # and middle*Drag methods. Change it as it is now is to prevent
        # possible similar bug that happened in the Move_Command where
        # a *Drag method is called before a *Down() method. This
        # comment applies to all three *Down/*Drag/*Up methods.
        if not self.picking:
            return

        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0], self.o.MousePos[1])
        self.o.quat += q
        self.o.gl_update()

    def middleUp(self, event):
        self.picking = False
        self.update_cursor()

    def middleShiftDown(self, event):
        """
        Set up for panning the view with MMB+Shift+Drag.
        """
        self.update_cursor()
        # Setup pan operation
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
        self.startpt = self.movingPoint # Used in leftDrag() to compute move offset during drag op.
            # REVIEW: needed? the subclasses that use it also set it, so probably not.
            # TODO: confirm that guess, then remove this set. (In fact, this makes me wonder
            # if some or all of the other things in this method are redundant now.) [bruce 071012 comment]

        self.o.SaveMouse(event) #k still needed?? probably yes; might even be useful to help dragto for atoms #e [bruce 060316 comment]
        self.picking = True

        # Turn off hover highlighting while panning the view with middle mouse button. Fixes bug 1657. Mark 060808.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.


    def middleShiftDrag(self, event):
        """
        Pan view with MMB+Shift+Drag.
        Move point of view so that the model appears to follow the cursor on the screen.
        """
        point = self.dragto( self.movingPoint, event)
        self.o.pov += point - self.movingPoint
        self.o.gl_update()

    def middleShiftUp(self, event):
        self.picking = False
        self.update_cursor()

    def middleCntlDown(self, event):
        """
        Set up for rotating view around POV axis with MMB+Cntl+Drag.
        """
        self.update_cursor()
        self.o.SaveMouse(event)
        self.Zorg = self.o.MousePos
        self.Zq = Q(self.o.quat)
        self.Zpov = self.o.pov
        self.picking = True

        # Turn off hover highlighting while rotating the view with middle mouse button. Mark 060808.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.

    def middleCntlDrag(self, event):
        """
        Rotate around the point of view (POV) axis
        """
        if not self.picking:
            return

        self.o.SaveMouse(event)
        dx, dy = (self.o.MousePos - self.Zorg) * V(1,-1)

        self.o.pov = self.Zpov

        w = self.o.width+0.0
        self.o.quat = self.Zq + Q(V(0,0,1), 2*math.pi*dx/w)

        self.o.gl_update()

    def middleCntlUp(self, event):
        self.picking = False
        self.update_cursor()

    def middleShiftCntlDown(self, event): # mark 060228.
        """
        Set up zooming POV in/out
        """
        self.middleCntlDown(event)

    def middleShiftCntlDrag(self, event):
        """
        Zoom (push/pull) point of view (POV) away/nearer
        """
        if not self.picking:
            return

        self.o.SaveMouse(event)
        dx, dy = (self.o.MousePos - self.Zorg) * V(1,-1)
        self.o.quat = Q(self.Zq)
        h = self.o.height+0.0
        self.o.pov = self.Zpov-self.o.out*(2.0*dy/h)*self.o.scale

        self.o.gl_update()

    def middleShiftCntlUp(self, event):
        self.picking = False
        self.update_cursor()

    # right button actions... #doc

    def rightDown(self, event):
        self._setup_menus_in_each_cmenu_event()
        self._Menu1.exec_(event.globalPos())
        #ninad061009: Qpopupmenu in qt3 is  QMenu in Qt4
        #apparently QMenu._exec does not take option int indexAtPoint.
        # [bruce 041104 comment:] Huaicai says that menu.popup and menu.exec_
        # differ in that menu.popup returns immediately, whereas menu.exec_
        # returns after the menu is dismissed. What matters most for us is whether
        # the callable in the menu item is called (and returns) just before
        # menu.exec_ returns, or just after (outside of all event processing).
        # I would guess "just before", in which case we have to worry about order
        # of side effects for any code we run after calling exec_, since in
        # general, our Qt event processing functions assume they are called purely
        # sequentially. I also don't know for sure whether the rightUp() method
        # would be called by Qt during or after the exec_ call. If any of this
        # ever matters, we need to test it. Meanwhile, exec_ is probably best
        # for context menus, provided we run no code in the same method after it
        # returns, nor in the corresponding mouseUp() method, whose order we don't
        # yet know. (Or at least I don't yet know.)
        #  With either method (popup or exec_), the menu stays up if you just
        # click rather than drag (which I don't like); this might be fixable in
        # the corresponding mouseup methods, but that requires worrying about the
        # above-described issues.

    def rightShiftDown(self, event):
        self._setup_menus_in_each_cmenu_event()
        # Previously we did this:
        # self._Menu2.exec_(event.globalPos(),3)
        # where 3 specified the 4th? action in the list. The exec_ method now
        # needs a pointer to the action itself, not a numerical index. The only
        # ways I can see to do that is with lots of bookkeeping, or if the menu
        # had a listOfActions method. This isn't important enough for the former
        # and Qt does not give us the latter. So forget about the 3.
        self._Menu2.exec_(event.globalPos())

    def rightCntlDown(self, event):
        self._setup_menus_in_each_cmenu_event()
        # see note above
        self._Menu3.exec_(event.globalPos())

    # other events

    def Wheel(self, event):
        mod = event.modifiers()
            ### REVIEW: this might need a fix_buttons call to work the same
            # on the Mac [bruce 041220]
        dScale = 1.0/1200.0
        if mod & Qt.ShiftModifier and mod & Qt.ControlModifier:
            # Shift + Control + Wheel zooms at same rate as without a modkey.
            pass
        elif mod & Qt.ShiftModifier:
            # Shift + Wheel zooms in quickly (2x),
            dScale *= 2.0
        elif mod & Qt.ControlModifier:
            # Control + Wheel zooms in slowly (.25x).
            dScale *= 0.25
        farQ_junk, point = self.dragstart_using_GL_DEPTH( event)
            # russ 080116 Limit mouse acceleration on the Mac.
        delta = max( -360, min(event.delta(), 360)) * self.w.mouseWheelDirection
        factor = exp(dScale * delta)
        #print "Wheel factor=", factor, " delta=", delta

            #bruce 070402 bugfix: original formula, factor = 1.0 + dScale * delta, was not reversible by inverting delta,
            # so zooming in and then out (or vice versa) would fail to restore original scale precisely,
            # especially for large delta. (Measured deltas: -360 or +360.)
            # Fixed by using an exponential instead.
        self.rescale_around_point_re_user_prefs( factor , point )
            # note: depending on factor < 1.0 and user prefs, point is not always used.

        # Turn off hover highlighting while zooming with mouse wheel. Fixes bug 1657. Mark 060805.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.

        # Following fixes bug 2536. See also SelectChunks_GraphicsMode.bareMotion
        # and the comment where this is initialized as a class variable.
        # [probably by Ninad 2007-09-19]
        #
        # update, bruce 080130: change time.clock -> time.time to fix one cause
        # of bug 2606. See comments where this is used for more info.
        self.timeAtLastWheelEvent = time.time()

        self.o.gl_update()
        return

    def rescale_around_point_re_user_prefs(self, factor, point = None): #bruce 060829; revised/renamed/moved from GLPane, 070402
        """
        Rescale by factor around point or center of view, depending on zoom direction and user prefs.
        (Factor < 1.0 means zooming in.)

        If point is not supplied, the center of view remains unchanged after the rescaling,
        and user prefs have no effect.

        Note that point need not be in the plane of the center of view, and if it's not, the depth
        of the center of view will change. If callers wish to avoid this, they can project point onto
        the plane of the center of view.
        """
        if point is not None:
            # decide whether to recenter around point (or do nothing, i.e. stay centered on center of view).
            if factor < 1.0:
                # zooming in
                recenter = not env.prefs[zoomInAboutScreenCenter_prefs_key]
            else:
                # zooming out
                recenter = not env.prefs[zoomOutAboutScreenCenter_prefs_key]
            if not recenter:
                point = None
        glpane = self.o
        glpane.rescale_around_point(factor, point) # note: point might have been modified above
        return

    # Key event handling revised by bruce 041220 to fix some bugs;
    # see comments in the GLPane methods, which now contain Mac-specific Delete
    # key fixes that used to be done here. For the future: The keyPressEvent and
    # keyReleaseEvent methods must be overridden by any mode which needs to know
    # more about key events than event.key() (which is the same for 'A' and 'a',
    # for example). As of 041220 no existing mode needs to do this.

    def keyPressEvent(self, event):
        """
        [some modes will need to override this in the future]
        """
        # Holding down X, Y or Z "modifier keys" in MODIFY and TRANSLATE modes generates
        # autorepeating keyPress and keyRelease events.  For now, ignore autorepeating key events.
        # Later, we may add a flag to determine if we should ignore autorepeating key events.
        # If a mode needs these events, simply override keyPressEvent and keyReleaseEvent.
        # Mark 050412
        #bruce 060516 extending this by adding keyPressAutoRepeating and keyReleaseAutoRepeating,
        # usually but not always ignored.
        if event.isAutoRepeat():
            self.keyPressAutoRepeating(event.key())
        else:
            self.keyPress(event.key())
        return

    def keyReleaseEvent(self, event):
        """
        """
        # Ignore autorepeating key events.  Read comments in keyPressEvent above for more detail.
        # Mark 050412
        #bruce 060516 extending this; see same comment.
        if event.isAutoRepeat():
            self.keyReleaseAutoRepeating(event.key())
        else:
            self.keyRelease(event.key())
        return

    # the old key event API (for modes which don't override keyPressEvent etc)

    def keyPress(self, key): # several modes extend this method, some might replace it

        def zoom(dScale):
            self.o.scale *= dScale
            self.o.gl_update()

        def pan(offsetVector, panIncrement):
            planePoint = V(0.0, 0.0, 0.0)
            offsetPoint = offsetVector * self.o.scale * panIncrement
            povOffset = planeXline(planePoint, self.o.out, offsetPoint, self.o.out)
            self.glpane.pov += povOffset
            self.glpane.gl_update()

        if key == Qt.Key_Delete:
            self.w.killDo()
        
        # Zoom in & out for Eric and Paul:
        # - Eric D. requested Period/Comma keys for zoom in/out.
        # - Paul R. requested Minus/Equal keys for zoom in/out.
        # Both sets of keys work with Ctrl/Cmd pressed for less zoom.
        # I took the liberty of implementing Plus and Less keys for zoom out
        # a lot, and Underscore and Greater keys for zoom in a lot. If this
        # conflicts with other uses of these keys, it can be easily changed.
        # Mark 2008-02-28.
        elif key in (Qt.Key_Minus, Qt.Key_Period):  # Zoom in.
            dScale = 0.95
            if self.o.modkeys == 'Control': # Zoom in a little.
                dScale = 0.995
            zoom(dScale)
        elif key in (Qt.Key_Underscore, Qt.Key_Greater):  # Zoom in a lot.
            dScale = 0.8
            zoom(dScale)
        elif key in (Qt.Key_Equal, Qt.Key_Comma): # Zoom out.
            dScale = 1.05
            if self.o.modkeys == 'Control':
                dScale = 1.005
            zoom(dScale)
        elif key in (Qt.Key_Plus, Qt.Key_Less):  # Zoom out a lot.
            dScale = 1.2
            zoom(dScale)

        # Pan left, right, up and down using arrow keys, requested by Paul.
        # Mark 2008-04-13
        elif key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            panIncrement = 0.1 * env.prefs[panArrowKeysDirection_prefs_key]
            if self.o.modkeys == 'Control':
                panIncrement *= 0.25
            elif self.o.modkeys == 'Shift':
                panIncrement *= 4.0
            if key == Qt.Key_Left:
                pan(-self.o.right, panIncrement)
            elif key == Qt.Key_Right:
                pan(self.o.right, panIncrement)
            elif key == Qt.Key_Up:
                pan(self.o.up, panIncrement)
            elif key == Qt.Key_Down:
                pan(-self.o.up, panIncrement)

        # comment out wiki help feature until further notice, wware 051101
        # [bruce 051130 revived/revised it, elsewhere in file]
        #if key == Qt.Key_F1:
        #    import webbrowser
        #    # [will 051010 added wiki help feature]
        #    webbrowser.open(self.__WikiHelpPrefix + self.__class__.__name__)
        #bruce 051201: let's see if I can bring this F1 binding back.
        # It works for Mac (only if you hold down "fn" key as well as F1);
        # but I don't know whether it's appropriate for Mac.
        # F1 for help (opening separate window, not usually an external website)
        # is conventional for Windows (I'm told).
        # See bug 1171 for more info about different platforms -- this should be revised to match.
        # Also the menu item should mention this accel key, but doesn't.
        elif key == Qt.Key_F1:
            featurename = self.command.get_featurename()
            if featurename:
                from foundation.wiki_help import open_wiki_help_dialog
                open_wiki_help_dialog( featurename)
            pass
        elif 0 and debug_flags.atom_debug:#bruce 051201 -- might be wrong depending on how subclasses call this, so disabled for now
            print "atom_debug: fyi: glpane keyPress ignored:", key
        return

    def keyPressAutoRepeating(self, key): #bruce 060416
        if key in (Qt.Key_Period, Qt.Key_Comma):
            self.keyPress(key)
        return

    def keyRelease(self, key): # mark 2004-10-11
        #e bruce comment 041220: lots of modes change cursors on this, but they
        # have bugs when more than one modifier is pressed and then one is
        # released, and perhaps when the focus changes. To fix those, we need to
        # track the set of modifiers and use some sort of inval/update system.
        # (Someday. These are low-priority bugs.)
        pass

    def keyReleaseAutoRepeating(self, key): #bruce 060416
        if key in (Qt.Key_Period, Qt.Key_Comma):
            self.keyRelease(key)
        return

    def update_cursor(self): # mark 060227
        """
        Update the cursor based on the current mouse button and mod keys pressed.
        """
        # print "basicMode.update_cursor(): button = %s, modkeys = %s, mode = %r, handler = %r" % \
        #     ( self.o.button, self.o.modkeys, self, self.o.mouse_event_handler )

        handler = self.o.mouse_event_handler # [bruce 070405]
            # Note: use of this attr here is a sign that this method really belongs in class GLPane,
            # and the glpane should decide whether to pass this update call to that attr's value or to the mode.
            # Or, better, maybe the mouse_event_handler should be temporarily on top of the command stack
            # in the command sequencer, overriding the mode below it for some purposes.
            # [bruce 070628 comment]

        if handler is not None:
            wX, wY = self.o._last_event_wXwY #bruce 070626
            handler.update_cursor(self, (wX, wY))
            return

        if self.o.button is None:
            self.update_cursor_for_no_MB()
        elif self.o.button == 'LMB':
            self.update_cursor_for_LMB()
        elif self.o.button == 'MMB':
            self.update_cursor_for_MMB()
        elif self.o.button == 'RMB':
            self.update_cursor_for_RMB()
        else:
            print "basicMode.update_cursor() button ignored:", self.o.button
        return

    def update_cursor_for_no_MB(self): # mark 060228
        """
        Update the cursor for operations when no mouse button is pressed.
        The default implementation just sets it to a simple arrow cursor
        """
        self.o.setCursor(self.w.SelectArrowCursor)

    def update_cursor_for_LMB(self): # mark 060228
        """
        Update the cursor for operations when the left mouse button (LMB) is pressed
        """
        pass

    def update_cursor_for_MMB(self): # mark 060228
        """
        Update the cursor for operations when the middle mouse button (MMB) is pressed
        """
        #print "basicMode.update_cursor_for_MMB(): button=",self.o.button

        if self.o.modkeys is None:
            self.o.setCursor(self.w.RotateViewCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.PanViewCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.RotateZCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.ZoomPovCursor)
        else:
            print "Error in update_cursor_for_MMB(): Invalid modkey=", self.o.modkeys
        return

    def update_cursor_for_RMB(self): # mark 060228
        """
        Update the cursor for operations when the right mouse button (RMB) is pressed
        """
        pass

    def makemenu(self, menu_spec, menu = None):
        glpane = self.o
        return glpane.makemenu(menu_spec, menu)

    def draw_selection_curve(self): # REVIEW: move to a subclass?
        """
        Draw the (possibly unfinished) freehand selection curve.
        """
        color = get_selCurve_color(self.selSense, self.o.backgroundColor)

        pl = zip(self.selCurve_List[:-1], self.selCurve_List[1:])
        for pp in pl: # Draw the selection curve (lasso).
            drawline(color, pp[0], pp[1])

        if self.selShape == SELSHAPE_RECT:  # Draw the selection rectangle.
            drawrectangle(self.selCurve_StartPt, self.selCurve_PrevPt,
                          self.o.up, self.o.right, color)

        if debug_flags.atom_debug and 0: # (keep awhile, might be useful)
            # debug code bruce 041214: also draw back of selection curve
            pl = zip(self.o.selArea_List[:-1], self.o.selArea_List[1:])
            for pp in pl:
                drawline(color, pp[0], pp[1])

    def get_prefs_value(self, prefs_key): #bruce 080605
        """
        Get the prefs_value to use for the given prefs_key in this graphicsMode.
        This is env.prefs[prefs_key] by default, but is sometimes overridden
        for specific combinations of graphicsMode and prefs_key,
        e.g. to return the value of a "command-specific pref" instead
        of the global one.

        @note: callers can continue to call env.prefs[prefs_key] directly
               except for specific prefs_keys for which some graphicsModes
               locally override them. (This is not yet declared as a property
               of a prefs_key, so there is not yet any way to detect the error
               of not calling this when needed for a specific prefs_key.)

        @note: the present implementation usage tracks env.prefs[whatever key
               or keys it accesses], but ideally, whenever the result depends
               on the specific graphicsMode, it would also track a variable
               corresponding to the current graphicsMode (so that changes
               to the graphicsMode would invalidate whatever was derived
               from the return value). Until that's implemented, callers
               must use other methods to invalidate the values they derived
               from this when our actual return value changes, if that might
               have been due to a change in current graphicsMode.

        [some subclasses should override this for specific prefs_keys,
         but use the passed prefs_key otherwise; ideally they should call
         their superclass version of this method for whatever prefs lookups
         they end up doing, rather than using env.prefs directly.]
        """
        return env.prefs[prefs_key]

    pass # end of class basicGraphicsMode

# ==

class GraphicsMode(basicGraphicsMode):
    """
    Subclass this class to provide a new mode of interaction for the GLPane.
    """
    def __init__(self, command):
        self.command = command
        glpane = self.command.glpane ### REVIEW: do commands continue to have this directly??
        basicGraphicsMode.__init__(self, glpane)
        return

    # Note: the remaining methods etc are not needed in basicGraphicsMode
    # since it is always mixed in after basicCommand
    # (since it is only for use in basicMode)
    # and they are provided by basicCommand or basicMode.

    def _get_commandSequencer(self):
        return self.command.commandSequencer

    commandSequencer = property(_get_commandSequencer) ### REVIEW: needed in this class?

    def set_cmdname(self, name): ### REVIEW: needed in this class? # Note: used directly, not in a property.
        """
        Helper method for setting the cmdname to be used by Undo/Redo.
        Called by undoable user operations which run within the context
        of this Graphics Mode's Command.
        """
        self.command.set_cmdname(name)
        return

    pass

commonGraphicsMode = basicGraphicsMode # use this for mixin classes that need to work in both basicGraphicsMode and GraphicsMode

# end
