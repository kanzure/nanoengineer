# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
GraphicsMode_API.py -- API class for whatever is used as a GraphicsMode

@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 071028 split this out of GraphicsMode.py, in which it was
called anyGraphicsMode. All external refs to anyGraphicsMode
are now refs to GraphicsMode_API.

TODO:

Add all the attributes and methods in the true GraphicsMode API
to this class (to fully document the API). Use null methods and
values (legal to use, which do nothing) unless no real GraphicsMode
can be correct without overriding them (like for Command.commandName).

See also the TODO comment in module GraphicsMode.
"""

class GraphicsMode_API(object):
    """
    API class (incomplete) and abstract superclass for all GraphicsMode objects,
    including nullGraphicsMode; used for isinstance tests
    """
    # history:
    # bruce 071008 added object superclass, 071009 split anyMode -> anyGraphicsMode
    # bruce 071028 renamed anyGraphicsMode -> GraphicsMode_API and gave it its own file

    
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
        # affects GLPane's algorithm for finding objectUnderMouse (selobj)

    picking = False # used as instance variable in some mouse methods

    
    # default methods for both nullGraphicsMode and basicGraphicsMode
    
    def selobj_highlight_color(self, selobj): #bruce 050612 added this to GraphicsMode API; see BuildAtoms_Graphicsmode version for docstring
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

    pass # end of class GraphicsMode_API

# end
