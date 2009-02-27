# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPane_csdl_collector.py -- classes for use as a GLPane's csdl_collector

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 090218 wrote this as part of Part_drawing_frame,
then realized it belonged elsewhere and split it into
a separate object on 090219
"""

from utilities.debug import print_compact_stack

from graphics.drawing.ColorSortedDisplayList import ColorSortedDisplayList
from graphics.drawing.ColorSorter import ColorSorter

# ==

class _GLPane_csdl_collector_superclass:
    """
    """
    use_drawingsets = False # whether to draw CSDLs using DrawingSets
    bare_primitives = None # None, or a CSDL for collecting bare primitives
    
    pass

# ==

class GLPane_csdl_collector(_GLPane_csdl_collector_superclass):
    """
    One of these is created whenever drawing a model,
    provided GLPane.before_drawing_csdls is called.

    It holds attributes needed for GLPane.draw_csdl to work
    (and helper methods for that as well).

    See superclass code comments for documentation of attributes.

    For more info, see docstring of GLPane.before_drawing_csdls.
    """
    def __init__(self, glpane):
        ## print "\ninit GLPane_csdl_collector", glpane, glpane.drawing_phase
        self._glpane = glpane
            # note: this won't be a ref cycle once we're done with,
            # since glpane won't refer to us anymore then
        return
    
    def setup_for_drawingsets(self):
        # review: needed in fake_GLPane_csdl_collector too??
        """
        """
        self.use_drawingsets = True
        self._drawingset_contents = {}

    def setup_for_bare_primitives(self): #bruce 090220
        """
        """
        self.bare_primitives = ColorSortedDisplayList(reentrant = True)
        ColorSorter.start(self._glpane, self.bare_primitives)
        return
    
    def collect_csdl(self, csdl, intent):
        """
        When self.use_drawingsets is set, model component drawing code which
        wants to draw a CSDL should pass it to this method rather than
        drawing it directly.

        This method just collects it into a dict based on intent.

        At the end of the current drawing frame, all csdls passed to this method
        will be added to (or maintained in) an appropriate DrawingSet,
        and all DrawingSets will be drawn, by external code which calls
        grab_intent_to_csdls_dict.

        @param csdl: a CSDL to draw later
        @type csdl: ColorSortedDisplayList

        @param intent: specifies how the DrawingSet which csdl ends up in
                       should be drawn (transform, other GL state, draw options)
        @type intent: not defined here, but must be useable as a dict key

        @return: None

        This API requires that every csdl to be drawn must be passed here in
        every frame (though the DrawingSets themselves can be persistent
        and incrementally updated, depending on how the data accumulated here
        is used). A more incremental API would probably perform better
        but would be much more complex, having to deal with chunks which
        move in and out of self, get killed, or don't get drawn for any other
        reason, and also requiring chunks to "diff" their own drawing intents
        and do incremental update themselves.
        """
        try:
            csdl_dict = self._drawingset_contents[intent]
        except KeyError:
            csdl_dict = self._drawingset_contents[intent] = {}
        csdl_dict[csdl.csdl_id] = csdl
        return

    def finish_bare_primitives(self):
        assert self.bare_primitives
        csdl = self.bare_primitives
        self.bare_primitives = None # precaution
        assert ColorSorter._parent_csdl is csdl
        ColorSorter.finish( draw_now = False)
        return csdl
    
    def grab_intent_to_csdls_dict(self):
        """
        Return (with ownership) to the caller (and reset in self)
        a dict from intent (about how a csdl's drawingset should be drawn)
        to a set of csdls (as a dict from their csdl_id's),
        which includes exactly the CSDLs which should be drawn in this
        frame (whether or not they were drawn in the last frame).

        The intent and csdl pairs in what we return are just the ones
        which were passed to collect_csdl during this frame.
        """
        res = self._drawingset_contents
        self._drawingset_contents = {}
        return res

    pass

# ==

class fake_GLPane_csdl_collector(_GLPane_csdl_collector_superclass):
    """
    Use one of these "between draws" to avoid or mitigate bugs.
    """
    def __init__(self, glpane):
        print_compact_stack(
            "warning: fake_GLPane_csdl_collector is being instantiated: " )
        return
    
    pass
        
# end
