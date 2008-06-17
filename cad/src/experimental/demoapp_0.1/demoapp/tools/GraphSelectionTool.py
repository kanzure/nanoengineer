"""
GraphSelectionTool.py

$Id$
"""

from demoapp.geometry.vectors import V

from pyglet.event import EVENT_HANDLED

from demoapp.graphics.drawing import drawline2d

from demoapp.foundation.MouseBehavior import Tool, MouseBehavior, parse_command, NOOP

from demoapp.graphics.colors import thin_rubberband_color

# ==

class GraphSelectionTool(Tool):
    """
    Clicks on nodes select them (in node sel mode)
    or all their edges (in edge sel mode),
    or modify selection using standard modifier key effects.

    Clicks on edges select them or both their nodes,
    depending on node vs edge sel mode. (Or modify selection.)

    Clicks on empty space deselect all
    (if no add-to-sel or toggle-sel modifier keys),
    then initiate region selection for their drags.

    States:
    - bare motion (param: modkeys -- possible?)
    - in region sel drag (substates: not yet a region, rect region, poly region; also the param: original modkeys)
    - during a click on something, not yet a drag
    - click on something and drag from it... not yet big enough, or big enough, and if so, doing what (substates/subhandlers)
    """
    pass

# end
