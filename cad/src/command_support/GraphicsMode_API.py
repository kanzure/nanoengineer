# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
GraphicsMode_API.py -- API class for whatever is used as a GraphicsMode

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 071028 split this out of GraphicsMode.py, in which it was
called anyGraphicsMode. All external refs to anyGraphicsMode
are now refs to GraphicsMode_API.

Bruce 081002 added all GraphicsMode API methods to this class, AFAIK
(to fully document the API). Used null methods and
values (legal to use, which do nothing) unless no real GraphicsMode
can be correct without overriding them (like for Command.commandName).

Note that this API consists mainly of methods/attrs expected by GLPane,
rather than by self.command, since when a Command expects certain
methods in its GraphicsMode, it's enough for those to be defined in
that command's own GraphicsMode_class (assuming subclasses of that
command use graphicsmode classes which are subclasses of that GM class,
as should generally be true).

TODO:

See the TODO comment in module GraphicsMode.
"""

class GraphicsMode_interface(object): #bruce 090307
    """
    This can be used in isinstance/issubclass assertions,
    and inherited by classes which intend to delegate to an actual GraphicsMode
    (such as Delegating_GraphicsMode) and which therefore don't want
    to inherit the default method implementations in GraphicsMode_API.
    """
    pass

# ==

class Delegating_GraphicsMode(GraphicsMode_interface): #bruce 090307
    """
    Abstract class for GraphicsModes which delegate almost everything
    to their parentGraphicsMode.

    @see: related class Overdrawing_GraphicsMode_preMixin,
        used in TemporaryCommand_Overdrawing
    """
    # implem note: We can't use idlelib.Delegator to help implement this class,
    # since the delegate needs to be dynamic.
    
    def __init__(self, command):
        self.command = command
        return

    def __get_parentGraphicsMode(self): #bruce 081223 [copied from GraphicsMode]
        # review: does it need to check whether the following exists?
        return self.command.parentCommand.graphicsMode

    parentGraphicsMode = property(__get_parentGraphicsMode)
        # use this when you need to wrap a method, then delegate explicitly
        # (but rely on __getattr__ instead, when you can delegate directly)

    def __getattr__(self, attr):
        if self.command.parentCommand:
            if self.command.parentCommand.graphicsMode: # aka parentGraphicsMode
                return getattr(self.command.parentCommand.graphicsMode, attr)
                # may raise AttributeError
            else:
                # parentCommand has no graphicsMode [never yet seen]
                print "%r has no graphicsMode!" % self.command.parentCommand
                raise AttributeError, attr
            pass
        else:
            # self.command has no parentCommand [never yet seen]
            print "%r has no parentCommand!" % self.command
            raise AttributeError, attr
        pass
    pass

# ==

class GraphicsMode_API(GraphicsMode_interface):
    """
    API class and abstract superclass for most GraphicsMode objects,
    including nullGraphicsMode.

    @note: for isinstance/issubclass tests, and fully-delegating GraphicsModes,
        use GraphicsMode_interface instead.
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

    check_target_depth_fudge_factor = 0.0001
        # affects GLPane's algorithm for finding selobj (aka objectUnderMouse)


    # default methods of various kinds:

    # selobj-related
    
    def selobj_highlight_color(self, selobj):
        """
        @see: Select_GraphicsMode version, for docstring
        """
        return None

    def selobj_still_ok(self, selobj):
        """
        @see: GraphicsMode version, for docstring
        """
        return True

    # also: glpane asks for self.command.isHighlightingEnabled()
    # (as part of a kluge used for updates during event processing);
    # review: should we define that in this API, and delegate it to command
    # in basicGraphicsMode? Or, better, refactor the sole call in GLPane_*.py
    # to call selobj_highlight_color instead (which is None whenever
    # the selobj should not be highlighted). [bruce 081002 comment]

    # drawing stages

    def gm_start_of_paintGL(self, glpane):
        return

    def Draw(self):
        # this should never happen as of bruce 090311
        print "bug: old code is calling %r.Draw(): " % self
        return

    def Draw_preparation(self):
        return

    def Draw_axes(self):
        return

    def Draw_other_before_model(self):
        return

    def Draw_model(self):
        return

    def Draw_other(self):
        return

    def Draw_after_highlighting(self, pickCheckOnly = False):
        return

    def draw_overlay(self): # misnamed
        return

    def Draw_highlighted_selobj(self, glpane, selobj, hicolor):
        """
        @see: GraphicsMode version, for docstring
        """
        return

    def gm_end_of_paintGL(self, glpane):
        return
    
    # cursor

    def update_cursor(self):
        return

    # key events
    
    def keyPressEvent(self, event):
        return

    def keyReleaseEvent(self, event):
        return

    # mouse wheel event

    def Wheel(self, event):
        return
    
    # mouse events
    # (todo: refactor to have fewer methods, let GraphicsMode
    #  split them up if desired, since some GMs don't want to)
    
    def mouse_event_handler_for_event_position(self, wX, wY):
        return None
    
    def bareMotion(self, event):
        """
        Mouse motion with no buttons pressed.

        @return: whether this event was "discarded" due to the last mouse wheel
                 event occurring too recently
        @rtype: boolean

        @note: GLPane sometimes generates a fake bareMotion event with
               no actual mouse motion

        @see: Select_GraphicsMode_MouseHelpers_preMixin.bareMotion
        @see: SelectChunks_GraphicsMode.bareMotion for 'return True'
        """
        return False # russ 080527 added return value to API


    def leftDouble(self, event): pass

    def leftDown(self, event): pass
    def leftDrag(self, event): pass
    def leftUp(self, event): pass

    def leftShiftDown(self, event): pass
    def leftShiftDrag(self, event): pass
    def leftShiftUp(self, event): pass

    def leftCntlDown(self, event): pass
    def leftCntlDrag(self, event): pass
    def leftCntlUp(self, event): pass
    

    def middleDouble(self, event): pass

    def middleDown(self, event): pass
    def middleDrag(self, event): pass
    def middleUp(self, event): pass
        
    def middleShiftDown(self, event): pass
    def middleShiftDrag(self, event): pass
    def middleShiftUp(self, event): pass
    
    def middleCntlDown(self, event): pass
    def middleCntlDrag(self, event): pass
    def middleCntlUp(self, event): pass
    
    def middleShiftCntlDown(self, event): pass
    def middleShiftCntlDrag(self, event): pass
    def middleShiftCntlUp(self, event): pass


    def rightDouble(self, event): pass

    def rightDown(self, event): pass
    def rightDrag(self, event): pass
    def rightUp(self, event): pass

    def rightShiftDown(self, event): pass
    def rightShiftDrag(self, event): pass
    def rightShiftUp(self, event): pass

    def rightCntlDown(self, event): pass
    def rightCntlDrag(self, event): pass
    def rightCntlUp(self, event): pass


    ### REVIEW:
    # other methods/attrs that may be part of the GraphicsMode API,
    # even though they are not called from GLPane itself
    # (some of them are called on "current GraphicsMode"):
    # - end_selection_from_GLPane
    # - isCurrentGraphicsMode
    # - get_prefs_value
    # - UNKNOWN_SELOBJ attr
    # - command attr
    # See also TODO comment in DynamicTip.py, suggesting a new API method
    # to ask what to display in the tooltip.

    pass # end of class GraphicsMode_API

# end
