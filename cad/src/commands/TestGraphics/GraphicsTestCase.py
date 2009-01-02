# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
GraphicsTestCase.py

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details. 

todo: refile some or all of this out of this specific command?
"""

class GraphicsTestCase(object):
    """
    """
    def __init__(self):
        """
        """
        return
    def activate(self):
        """
        Make sure this instance is ready to be used immediately.
        You can assume that this is either called just before self.draw(),
        or that no other test case's .draw method has been called between
        when this was called and when self.draw() is called.
        
        TBD: whether it is necessarily called when test case parameters change. 
        (Guess: should be, but isn't in initial prototype.)

        (Note that that means that the subclass API semantics for this method
        depends on how it's used by the totality of test cases.
        At present, one thing it can be used for is setting up the global environment
        for drawing, e.g. the list of DrawingSets to draw,
        in a way depended on by self.draw.)
        """
        return
    def deactivate(self):
        """
        Optimize for not planning to reuse this instance for awhile.
        """
        self.clear_caches()
        return
    def clear_caches(self):
        """
        Deallocate whatever caches this instance owns
        (which consume nontrivial amounts of CPU or GPU RAM),
        without preventing further uses of this instance.
        """
        return
    # == drawing methods
    def draw_complete(self):
        """
        Do all drawing for self for one frame.
        
        @note; it is not usually sensible for this method on a container
               to call the same method on contained objects.
               For that, see self.draw().
        """
        self.draw()
        self._draw_drawingsets()
        return
    def draw(self): # review: rename? this name is 
        """
        Run whatever immediate-mode OpenGL code is required,
        and maintain the global or env-supplied list of DrawingSets 
        and their CSDL membership, in anticipation of their being drawn
        in the usual way (by _draw_drawingsets, on self or some container self is in)
        later in the drawing of this frame.
        """
        # note: this name 'draw' is for maximum old-code compatibility.
        # it may be clear when seen from the point of view of graphics leaf nodes
        # rather than for rendering loop test cases as this class API is meant for.
        return
    def _draw_drawingsets(self):
        """
        subclass API method, for a complete test container
        (not for individual objects inside it)
        """
        assert 0, "implement in subclass"
        return
    pass

# end
