# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
GraphicsMode.py -- 

$Id$

History:

bruce 071009 split modes.py into Command.py and GraphicsMode.py,
leaving only temporary compatibility mixins in modes.py.
For prior history see modes.py docstring before the split.

TODO:

A lot of methods in class GraphicsMode are private helper methods,
available to subclasses and/or to default implems of public methods,
but are not yet named as private or otherwise distinguished
from API methods. We should turn anyGraphicsMode into GraphicsMode_API,
add all the API methods to it, and rename the other methods
in class GraphicsMode to look private.
"""

import math # just for pi
from Numeric import exp
from Numeric import dot

from PyQt4.Qt import Qt
from PyQt4.Qt import QMenu, QCursor

from OpenGL.GL import GL_FALSE
from OpenGL.GL import glColorMask
from OpenGL.GL import GL_DEPTH_COMPONENT
from OpenGL.GL import glReadPixelsf
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glSelectBuffer
from OpenGL.GL import GL_SELECT
from OpenGL.GL import glRenderMode
from OpenGL.GL import glInitNames
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_CLIP_PLANE0
from OpenGL.GL import glClipPlane
from OpenGL.GL import glEnable
from OpenGL.GL import glDisable
from OpenGL.GL import glPopMatrix
from OpenGL.GL import GL_RENDER
from OpenGL.GL import glFlush

from OpenGL.GLU import gluUnProject

from VQT import V, Q, A, vlen, norm, planeXline, ptonline
import drawer

from debug import print_compact_traceback

import platform

import env
from shape import get_selCurve_color

from constants import SELSHAPE_RECT
from constants import SUBTRACT_FROM_SELECTION
from constants import ADD_TO_SELECTION

from prefs_constants import zoomAboutScreenCenter_prefs_key
from prefs_constants import displayOriginAxis_prefs_key
from prefs_constants import displayOriginAsSmallAxis_prefs_key
from prefs_constants import displayPOVAxis_prefs_key

from Utility import Group
from chem import Atom
from bonds import Bond
from Utility import Node
from jigs import Jig

import time

# ==

class anyGraphicsMode(object): #bruce 071008 added object superclass, 071009 split anyMode -> anyGraphicsMode
    """
    abstract superclass for all GraphicsMode objects, including nullGraphicsMode
    """

    # GraphicsMode-specific attribute null values
    
    compass_moved_in_from_corner = False
        # when set, tells GLPane to render compass in a different place [bruce 070406]

    render_scene = None # optional scene-rendering method [bruce 070406]
        # When this is None, it tells GLPane to use its default method.
        # (TODO, maybe: move that default method into basicGraphicsMode's implem
        #  of this, and put a null implem in this class.)
        # Note: to use this, override it with a method (or set it to a
        # callable) which is compatible with GLPane.render_scene()
        # but which receives a single argument which will be the GLPane.
    
    hover_highlighting_enabled = False
        # note: hover_highlighting_enabled is a settable instance variable in both
        # the Command and GraphicsMode APIs; a separate GraphicsMode delegates it
        # as state to its Command [bruce 071011]

    check_target_depth_fudge_factor = 0.0001
        # affects GLPane's algorithm for finding objectUnderMouse (selobj)

    
    # default methods for both nullGraphicsMode and basicGraphicsMode
    
    def selobj_highlight_color(self, selobj): #bruce 050612 added this to GraphicsMode API; see depositMode version for docstring
        return None

    def selobj_still_ok(self, selobj): #bruce 050702 added this to GraphicsMode API; overridden in GraphicsMode, and docstring is there
        return True

    def draw_overlay(self): #bruce 070405
        return

    def mouse_event_handler_for_event_position(self, wX, wY): #bruce 070405
        return None

    def update_cursor(self): #bruce 070410
        return

    def drawHighlightedObjectUnderMouse(self, glpane, selobj, hicolor): #bruce 071008
        pass

    pass # end of class anyGraphicsMode


class nullGraphicsMode(anyGraphicsMode):
    """
    do-nothing GraphicsMode (for internal use only) to avoid crashes
    in case of certain bugs during transition between GraphicsModes
    """
    
    # needs no __init__ method; constructor takes no arguments
    
    # WARNING: the next two methods are similar in all "null objects", of which
    # we have nullCommand and nullGraphicsMode so far. They ought to be moved
    # into a common nullObjectMixin for all kinds of "null objects". [bruce 071009]
    
    def noop_method(self, *args, **kws):
        if platform.atom_debug:
            print "fyi: atom_debug: nullGraphicsMode noop method called -- probably ok; ignored"
        return None #e print a warning?
    def __getattr__(self, attr): # in class nullGraphicsMode
        # note: this is not inherited by other GraphicsMode classes,
        # since we are not their superclass
        if not attr.startswith('_'):
            if platform.atom_debug:
                print "fyi: atom_debug: nullGraphicsMode.__getattr__(%r) -- probably ok; returned noop method" % attr
            return self.noop_method
        else:
            raise AttributeError, attr #e args?

    # GraphicsMode-specific null methods
    
    def Draw(self):
        # Note: this does happen... maybe due to how soon we call
        # .start_using_mode( '$DEFAULT_MODE')".
        # If so, it's ok that it happens and good
        # that we make it a noop. [bruce 040924]
        pass
    def Draw_after_highlighting(self):
        pass
    def keyPressEvent(self, e):
        pass
    def keyReleaseEvent(self, e):
        pass
    def bareMotion(self, e):
        pass
    
    pass # end of class nullGraphicsMode


class basicGraphicsMode(anyGraphicsMode):
    """
    Common code between class GraphicsMode (see its docstring)
    and old-code-compatibility class basicMode.
    Will be merged with class GraphicsMode (keeping that one's name)
    when basicMode is no longer needed.
    """
    
    #Initialize clock time during a wheel event to None. Its value is assigned 
    #in self.wheelEvent. This time is used to decide whether to highlight 
    #object under cursor. I.e. when user is scrolling the wheel to zoom in or
    #out, and at the same time the mouse moves slightly, we want to make sure 
    #that the object is not highlighted.See selectMolsMode.bareMotion for an 
    #example. 
    timeAtLastWheelEvent = None

    # NOTE: subclasses will have to make self.command point to the command
    # object (a running command which owns the graphics mode object).
    # This is done differently in different subclasses, since in some of
    # them, those are the same object.
    
    def __init__(self, glpane):
        """
        """
        # guessing self.pw is only needed in class Command (or not at all):
        ## self.pw = None # pw = part window

        # initialize attributes used by methods to refer to
        # important objects in their runtime environment
        
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

    def isCurrentGraphicsMode(self): #bruce 071010, for GraphicsMode API
        """
        Return a boolean to indicate whether self is the currently active GraphicsMode.
        
        See also Command.isCurrentCommand.
        """
        # see WARNING in modeMixin about this needing revision if .graphicsMode
        # might have been wrapped with an API-enforcement (or any other) proxy.
        return self.glpane.graphicsMode is self

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
        # conf corner is enabled by default for A9.1 (070627); requires exprs module and Python Imaging Library
        from debug_prefs import debug_pref, Choice_boolean_True
        if not debug_pref("Enable confirmation corner?", Choice_boolean_True, prefs_key = True):
            return 
        # figure out what kind of confirmation corner we want, and draw it
        import confirmation_corner
        cctype = self.command.want_confirmation_corner_type()
        self._ccinstance = confirmation_corner.find_or_make(cctype, self)
            # Notes:
            # - we might use an instance cached in self (in an attr private to that helper function);
            # - this might be as specific as both args passed above, or as shared as one instance
            #   for the entire app -- that's up to it;
            # - if one instance is shared for multiple cctypes, it might store the cctype passed above
            #   as a side effect of find_or_make;
            # - self._ccinstance might be None.
        if self._ccinstance is not None:
            # it's an instance we want to draw, and to keep around for mouse event handling
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
            elif platform.atom_debug:
                print "atom_debug: fyi: ccinstance %r with no want_event_position method" % (self._ccinstance,)
        return None

    # ==

    def restore_patches_by_GraphicsMode(self):
        """
        subclasses should restore anything they temporarily modified in
        their environment (such as temporary objects stored in major objects
        like win or glpane or assy, or settings changes in them)

        @see: Command.restore_patches_by_Command
        """
        pass

    # ==

    def Draw(self):
        """
        Generic Draw method, with drawing code common to all modes.
        Specific modes should call this somewhere within their own Draw method,
        unless they have a good reason not to. Note: it doesn't draw the model,
        since not all modes want to always draw it.
        """
        
        # Draw the Origin axis.
        if env.prefs[displayOriginAxis_prefs_key]:
            if env.prefs[displayOriginAsSmallAxis_prefs_key]: #ninad060920
                drawer.drawOriginAsSmallAxis(self.o.scale, (0.0,0.0,0.0))
                #ninad060921: note: we are also drawing a dotted origin displayed only when 
                #the solid origin is hidden. See def standard_repaint_0 in GLPane.py
                #ninad060922 passing self.o.scale makes sure that the origin / pov axes are not zoomable
            else:
                drawer.drawaxes(self.o.scale, (0.0,0.0,0.0), coloraxes=True)
            
        if env.prefs[displayPOVAxis_prefs_key]:
            drawer.drawaxes(self.o.scale, -self.o.pov)
        
        # Draw the Point of View axis unless it is at the origin (0,0,0) AND draw origin as cross wire is true ninad060920
        if env.prefs[displayPOVAxis_prefs_key]:
            if not env.prefs[displayOriginAsSmallAxis_prefs_key]:
                if vlen(self.o.pov):
                    drawer.drawaxes(self.o.scale, -self.o.pov)
                else:
                    # POV is at the origin (0,0,0).  Draw it if the Origin axis is not drawn. Fixes bug 735.
                    if not env.prefs[displayOriginAxis_prefs_key]:
                        drawer.drawaxes(self.o.scale, -self.o.pov)
            else:
                drawer.drawaxes(self.o.scale, -self.o.pov)
	
        # bruce 040929/041103 debug code -- for developers who enable this
        # feature, check for bugs in atom.picked and mol.picked for everything
        # in the assembly; print and fix violations. (This might be slow, which
        # is why we don't turn it on by default for regular users.)
        if platform.atom_debug:
            self.o.assy.checkpicked(always_print = 0)
        return

    def _drawESPImage(self, grp, pickCheckOnly): # huaicai
        """
        Draw any member in the Group <grp> if it is an ESP Image.
        Not consider the order of ESP Image objects
        """
        from jigs_planes import ESPImage
       
        anythingDrawn = False
    
        try:
            if isinstance(grp, ESPImage):
                anythingDrawn = True
                grp.pickCheckOnly = pickCheckOnly
                grp.draw(self.o, self.o.displayMode)
            elif isinstance(grp, Group):    
                for ob in grp.members[:]:
                    if isinstance(ob, ESPImage):
                        anythingDrawn = True
                        ob.pickCheckOnly = pickCheckOnly
                        ob.draw(self.o, self.o.displayMode)
                    elif isinstance(ob, Group):
                        self._drawESPImage(ob, pickCheckOnly)
                #k Do they actually use dispdef? I know some of them sometimes circumvent it (i.e. look directly at outermost one).
                #e I might like to get them to honor it, and generalize dispdef into "drawing preferences".
                # Or it might be easier for drawing prefs to be separately pushed and popped in the glpane itself...
                # we have to worry about things which are drawn before or after main drawing loop --
                # they might need to figure out their dispdef (and coords) specially, or store them during first pass
                # (like renderpass.py egcode does when it stores modelview matrix for transparent objects).
                # [bruce 050615 comments]
            return anythingDrawn
        except:
            print_compact_traceback("exception in drawing some Group member; skipping to end: ")
            ###k return value?
        pass
    
    def Draw_after_highlighting(self, pickCheckOnly = False): #bruce 050610
        """
        Do more drawing, after the main drawing code has completed its highlighting/stenciling for selobj.
        Caller will leave glstate in standard form for Draw. Implems are free to turn off depth buffer read or write
        (but must restore standard glstate when done, as for mode.Draw() method).

        Warning: anything implems do to depth or stencil buffers will affect the standard selobj-check in bareMotion
        (presently only used in depositMode).
        
        [New method in mode API as of bruce 050610. General form not yet defined -- just a hack for Build mode's
         water surface. Could be used for transparent drawing in general.]
        """
        return self._drawESPImage(self.o.assy.part.topnode, pickCheckOnly)
    
    def selobj_still_ok(self, selobj): #bruce 050702 added this to mode API; revised 060724
        """
        Say whether a highlighted mouseover object from a prior draw (in the same mode) is still ok.
        If the mode's special cases don't hold, we ask the selobj; if that doesn't work, we assume it
        defines .killed (and answer yes unless it's been killed).

        [overrides anyMode method; subclasses might want to override this one]
        """
        try:
            # This sequence of conditionals fix bugs 1648 and 1676. mark 060315.
            # [revised by bruce 060724 -- merged in selobj.killed() condition, dated 050702,
            #  which was part of fix 1 of 2 redundant fixes for bug 716 (both fixes are desirable)]
            if isinstance(selobj, Atom):
                return not selobj.killed() and selobj.molecule.part is self.o.part
            elif isinstance(selobj, Bond):
                return not selobj.killed() and selobj.atom1.molecule.part is self.o.part
            elif isinstance(selobj, Node): # Jig
                return not selobj.killed() and selobj.part is self.o.part
            else:
                #bruce 060724 new feature, related to Drawable API
                try:
                    method = selobj.selobj_still_ok
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
            if platform.atom_debug:
                print "debug: selobj_still_ok doesn't recognize %r, assuming ok" % (selobj,)
            return True
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: ignoring exception: ")
            return True # let the selobj remain
        pass

    def drawHighlightedObjectUnderMouse(self, glpane, selobj, hicolor): #bruce 071008 for graphics mode API
        """
        Subclasses should override this as needed, though most don't need to:
        
        Draw selobj in highlighted form for being the object under the mouse,
        as appropriate to this graphics mode.
        [TODO: document this properly: Use hicolor as its color
        if you return sensible colors from method XXX.]

        Note: selobj is typically glpane.selobj, but don't assume this.
        """
        selobj.draw_in_abs_coords(glpane, hicolor)
    
    # left mouse button actions -- overridden in modes that respond to them
    def leftDown(self, event):
        pass
    
    def leftDrag(self, event):
        pass
    
    def leftUp(self, event):
        pass
    
    def leftShiftDown(self, event):
        pass
    
    def leftShiftDrag(self, event):
        pass
    
    def leftShiftUp(self, event):
        pass
    
    def leftCntlDown(self, event):
        pass
    
    def leftCntlDrag(self, event):
        pass
    
    def leftCntlUp(self, event):
        pass
    
    def leftDouble(self, event):
        pass

    # middle mouse button actions -- these support a trackball, and
    # are the same for all modes (with a few exceptions)
    def middleDown(self, event):
        """
        Set up for rotating the view with MMB+Drag.
        """
        self.update_cursor()
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        self.picking = True
        
        # Turn off hover highlighting while rotating the view with middle mouse button. Fixes bug 1657. Mark 060805.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.

    def middleDrag(self, event):
        """
        Rotate the view with MMB+Drag.
        """
        # Huaicai 4/12/05: Originally 'self.picking=0 in both middle*Down
        # and middle*Drag methods. Change it as it is now is to prevent 
        # possible similar bug that happened in the modifyMode where 
        # a *Drag method is called before a *Down() method. This 
        # comment applies to all three *Down/*Drag/*Up methods.
        if not self.picking: return
        
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1])
        self.o.quat += q
        self.o.gl_update()
 
    def middleUp(self, event):
        self.picking = False
        self.update_cursor()

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
        
    def middleShiftDown_OBS(self, event):
        self.w.OldCursor = QCursor(self.o.cursor())
        # save copy of current cursor in OldCursor
        self.o.setCursor(self.w.MoveCursor) # load MoveCursor in glpane
        
        self.o.SaveMouse(event)
        self.picking = False

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
        # Should be moved into modes.py and used in modifyMode too. [doing that, 060316]
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
    
    def middleShiftDrag(self, event):
        """
        Pan view with MMB+Shift+Drag. 
        Move point of view so that the model appears to follow the cursor on the screen.
        """
        point = self.dragto( self.movingPoint, event) #bruce 060316 replaced old code with dragto (equivalent)
        self.o.pov += point - self.movingPoint
        self.o.gl_update()
        
    def middleShiftDrag_OBS(self, event):
        """
        Move point of view so that objects appear to follow
        the mouse on the screen.
        """
        if not self.picking:
            return
        
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        #move = self.o.quat.unrot(self.o.scale * deltaMouse/(h*0.5))
        
        # bruce comment 040908, about josh code: 'move' is mouse
        # motion in model coords. We want center of view, -self.pov,
        # to move in opposite direction as mouse, so that after
        # recentering view on that point, objects have moved with
        # mouse.
        
        ### Huaicai 1/26/05: delta Xe, delta Ye  depend on Ze, here
        ### Ze is just an estimate, so Xe and Ye are estimates too, but
        ### they seems more accurate than before. To accurately 
        ### calculate it, we need to find a depth value for a point on 
        ### the model.
        Ze = 2.0*self.o.near*self.o.far*self.o.scale/(self.o.near+self.o.far)
        tY = (self.o.zoomFactor*Ze)*2.0/h
        
        move = self.o.quat.unrot(deltaMouse*tY)
        self.o.pov += move
        self.o.gl_update()
        self.o.SaveMouse(event)
        
    
    def middleShiftUp(self, event):
        self.picking = 0
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
        self.picking = 1
        
        # Turn off hover highlighting while rotating the view with middle mouse button. Mark 060808.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.
    
    def middleCntlDrag(self, event):
        """
        Rotate around the point of view (POV) axis
        """
        if not self.picking:
            return
        
        self.o.SaveMouse(event)
        dx,dy = (self.o.MousePos - self.Zorg) * V(1,-1)

        self.o.pov = self.Zpov

        w=self.o.width+0.0
        self.o.quat = self.Zq + Q(V(0,0,1),2*math.pi*dx/w)
 
        self.o.gl_update()
        
    def middleCntlUp(self, event):
        self.picking = 0
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
        dx,dy = (self.o.MousePos - self.Zorg) * V(1,-1)
        self.o.quat = Q(self.Zq)
        h=self.o.height+0.0
        self.o.pov = self.Zpov-self.o.out*(2.0*dy/h)*self.o.scale
 
        self.o.gl_update()
        
    def middleShiftCntlUp(self, event):
        self.picking = 0
        self.update_cursor()

    def middleCntlDrag_OBS(self, event):
        """
        push scene away (mouse goes up) or pull (down);
        and/or rotate around vertical axis (left-right)
        """
        if not self.picking:
            return
        
        self.o.SaveMouse(event)
        dx,dy = (self.o.MousePos - self.Zorg) * V(1,-1)
        ax,ay = abs(V(dx,dy))
        if self.Zunlocked:
            self.Zunlocked = ax<10 and ay<10
            if ax>ay:
                # rotating
                self.o.setCursor(self.w.RotateZCursor)
                # load RotateZCursor in glpane
                self.o.pov = self.Zpov
                self.ZRot = 1
            else:
                # zooming
                self.o.setCursor(self.w.ZoomCursor)
                # load ZoomCursor in glpane
                self.o.quat = Q(self.Zq)
                self.ZRot = 0
        if self.ZRot:
            w=self.o.width+0.0
            self.o.quat = self.Zq + Q(V(0,0,1),2*math.pi*dx/w)
        else:
            h=self.o.height+0.0
            self.o.pov = self.Zpov-self.o.out*(2.0*dy/h)*self.o.scale
 
        self.o.gl_update()

    def middleDouble(self, event):
        pass

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
    
    def rightDrag(self, event):
        pass
    
    def rightUp(self, event):
        pass
    
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

                
    def rightShiftDrag(self, event):
        pass
    
    def rightShiftUp(self, event):
        pass
    
    def rightCntlDown(self, event):
        self._setup_menus_in_each_cmenu_event()
        # see note above
        self._Menu3.exec_(event.globalPos())
        
    def rightCntlDrag(self, event):
        pass
    
    def rightCntlUp(self, event):
        pass
    
    def rightDouble(self, event):
        pass

    # other events
    
    def bareMotion(self, event):
        pass

    def Wheel(self, event):
        #e sometime we need to give this a modifier key binding too;
        # see some email from Josh with a suggested set of them [bruce 041220]
        mod = event.modifiers()
            ### REVIEW: this might need a fix_buttons call to work the same
            # on the Mac [bruce 041220]
        dScale = 1.0/1200.0
        if mod & Qt.ShiftModifier: dScale *= 2.0
        if mod & Qt.ControlModifier: dScale *= 0.25
            # Switched Shift and Control zoom factors to be more intuitive.
            # Shift + Wheel zooms in quickly (2x), Control + Wheel zooms in slowly (.25x). 
            # mark 060321
        farQ_junk, point = self.dragstart_using_GL_DEPTH( event)
        delta = event.delta()
##        factor = 1.0 + dScale * delta
        factor = exp(dScale * delta)
            #bruce 070402 bugfix: original formula, factor = 1.0 + dScale * delta, was not reversible by inverting delta,
            # so zooming in and then out (or vice versa) would fail to restore original scale precisely,
            # especially for large delta. (Measured deltas: -360 or +360.)
            # Fixed by using an exponential instead.
        self.rescale_around_point_re_user_prefs( factor , point )
            # note: depending on factor < 1.0 and user prefs, point is not always used.
        
        # Turn off hover highlighting while zooming with mouse wheel. Fixes bug 1657. Mark 060805.
        self.o.selobj = None # <selobj> is the object highlighted under the cursor.
        
        #Following fixes bug 2536 See also selectMolsMode.bareMotion
        self.timeAtLastWheelEvent = time.clock()
        
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
                recenter = not env.prefs[zoomAboutScreenCenter_prefs_key]
                    # ninad 060924 Zoom about screen center is disabled by default (so recenter is True by default)
            else:
                # zooming out -- behavior changed for A9 by bruce 070402 on Mark request to not recenter on point.
                # (Old behavior was to use the same pref as for zooming in.)
                #e [Should this be a separate user pref? For now it's a debug pref, just for testing.
                #   We might replace these two prefs with a 3-choice pref which controls them both.]
                from debug_prefs import debug_pref, Choice_boolean_False
                if debug_pref("GLPane: zoom out acts the same as zoom in?", Choice_boolean_False,
                              prefs_key = "A9 devel/GLPane: zoom out same as zoom in?"
                             ):
                    recenter = not env.prefs[zoomAboutScreenCenter_prefs_key]
                else:
                    recenter = False # the new documented behavior
            if not recenter:
                point = None
        glpane = self.o
        glpane.rescale_around_point(factor, point) # note: point might have been modified above
        return
    
    # [remaining methods not yet analyzed by bruce 040922]

    
    # Key event handling revised by bruce 041220 to fix some bugs;
    # see comments in the GLPane methods, which now contain Mac-specific Delete
    # key fixes that used to be done here. For the future: The keyPressEvent and
    # keyReleaseEvent methods must be overridden by any mode which needs to know
    # more about key events than e.key() (which is the same for 'A' and 'a',
    # for example). As of 041220 no existing mode needs to do this.
    
    def keyPressEvent(self, e):
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
        if e.isAutoRepeat():
            self.keyPressAutoRepeating(e.key())
        else:
            self.keyPress(e.key())
        return
        
    def keyReleaseEvent(self, e):
        
        # Ignore autorepeating key events.  Read comments in keyPressEvent above for more detail.
        # Mark 050412
        #bruce 060516 extending this; see same comment.
        if e.isAutoRepeat():
            self.keyReleaseAutoRepeating(e.key())
        else:
            self.keyRelease(e.key())
        return

    # the old key event API (for modes which don't override keyPressEvent etc)
    
    def keyPress(self,key): # several modes extend this method, some might replace it
        if key == Qt.Key_Delete:
            self.w.killDo()
        elif key == Qt.Key_Escape: # Select None. mark 060129.
            self.o.assy.selectNone()
        # Zoom in (Ctrl/Cmd+.) & out (Ctrl/Cmd+,) for Eric.  Right now, this will work with or without
        # the Ctrl/Cmd key pressed.  We'll fix this later, at the same time we address the issue of
        # more than one modifier key being pressed (see Bruce's notes below). Mark 050923.
        elif key == Qt.Key_Period:
            self.o.scale *= .95
            self.o.gl_update()
        elif key == Qt.Key_Comma: 
            self.o.scale *= 1.05
            self.o.gl_update()
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
            featurename = self.user_modename()
            if featurename:
                from wiki_help import open_wiki_help_dialog
                open_wiki_help_dialog( featurename)
            pass
        elif 0 and platform.atom_debug:#bruce 051201 -- might be wrong depending on how subclasses call this, so disabled for now
            print "atom_debug: fyi: glpane keyPress ignored:", key
        return

    def keyPressAutoRepeating(self, key): #bruce 060416
        if key in (Qt.Key_Period, Qt.Key_Comma):
            self.keyPress(key)
        return
    
    def keyRelease(self,key): # mark 2004-10-11
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
        Update the cursor for operations when no mouse button is pressed
        """
        pass
    
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
            self.o.setCursor(self.w.RotateCursor)
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.MoveCursor)
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.RotateZCursor)
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.ZoomPOVCursor)
        else:
            print "Error in update_cursor_for_MMB(): Invalid modkey=", self.o.modkeys
        return
        
    def update_cursor_for_RMB(self): # mark 060228
        """
        Update the cursor for operations when the right mouse button (RMB) is pressed
        """
        pass

    def makemenu(self, menu, lis):
        # bruce 040909 moved most of this method into GLPane.
        glpane = self.o
        return glpane.makemenu(menu, lis)

    def draw_selection_curve(self):
        """
        Draw the (possibly unfinished) freehand selection curve.
        """
        color = get_selCurve_color(self.selSense, self.o.backgroundColor)
        
        pl = zip(self.selCurve_List[:-1],self.selCurve_List[1:])
        for pp in pl: # Draw the selection curve (lasso).
            drawer.drawline(color,pp[0],pp[1])
            
        if self.selShape == SELSHAPE_RECT:  # Draw the selection rectangle.
            drawer.drawrectangle(self.selCurve_StartPt, self.selCurve_PrevPt,
                                 self.o.up, self.o.right, color)

        if platform.atom_debug and 0: # (keep awhile, might be useful)
            # debug code bruce 041214: also draw back of selection curve
            pl = zip(self.o.selArea_List[:-1],self.o.selArea_List[1:])
            for pp in pl:
                drawer.drawline(color,pp[0],pp[1])

    def surfset(self, num):
        """
        noop method, meant to be overridden in cookieMode
        for setting diamond surface orientation
        """
        pass


    def _calibrateZ(self, wX, wY):
        """
        Because translucent plane drawing or other special drawing,
        the depth value may not be accurate. We need to
        redraw them so we'll have correct Z values. 
        """
        glMatrixMode(GL_MODELVIEW)
        glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE) 
        
        if self.Draw_after_highlighting(pickCheckOnly=True): # Only when we have translucent planes drawn
            self.o.assy.draw(self.o)
        
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
        
        return wZ[0][0]

    def jigGLSelect(self, event, selSense):
        """
        Use the OpenGL picking/selection to select any jigs.
        Restore the projection and modelview matrices before returning.
        """
        ## [Huaicai 9/22/05]: Moved it from selectMode class, so it can be called in move mode, which
        ## is asked for by Mark, but it's not intended for any other mode.
        #
        ### WARNING: The original code for this, in GLPane, has been duplicated and slightly modified
        # in at least three other places (search for glRenderMode to find them). This is bad; common code
        # should be used. Furthermore, I suspect it's sometimes needlessly called more than once per frame;
        # that should be fixed too. [bruce 060721 comment]
        
        from constants import GL_FAR_Z
        
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
        return  False # from jigGLSelect

    pass # end of class basicGraphicsMode

# ==

class GraphicsMode(basicGraphicsMode):
    """
    Subclass this class to provide a new mode of interaction for the GLPane.
    """
    def __init__(self, command):
        self.command = command
        glpane = self.xxx ### TODO: work this out... #}
        basicGraphicsMode.__init__(glpane)
        return

    # Note: the remaining methods etc are not needed in basicGraphicsMode
    # since it is always mixed in after basicCommand
    # (sinc it is only for use in basicMode)
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

    def _get_hover_highlighting_enabled(self):
        return self.command.hover_highlighting_enabled
    
    def _set_hover_highlighting_enabled(self, val):
        self.command.hover_highlighting_enabled = val

    hover_highlighting_enabled = property(_get_hover_highlighting_enabled, _set_hover_highlighting_enabled)
    
    pass

# end
