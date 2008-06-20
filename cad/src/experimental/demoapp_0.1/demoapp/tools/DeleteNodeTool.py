"""
DeleteNodeTool.py - tool for deleting nodes

$Id$
"""

from demoapp.foundation.MouseBehavior import Tool, Transition

from demoapp.tools.HuntForClickAction_ToolStateBehavior import HuntForClickAction_ToolStateBehavior

from demoapp.models.TrivalentGraph_Graphics import TrivalentGraph_HighlightGraphics

# ==


class _HuntForNode(HuntForClickAction_ToolStateBehavior): # rename?
    """
    Clicking on nodes deletes them.
    """
    def on_mouse_press_would_do(self, x, y, button, modifiers):
        """
        """
        model = self.model
        obj = self.pane.find_object(x, y) # might be None
        hh = self.tool._f_HighlightGraphics_descriptions
        if isinstance(obj, model.Node):
            # click on any node: delete it
            return Transition(
                indicators = [hh.tip_text("click to DELETE this node", obj),
                              hh.highlight_delete(obj),
                              ],
                command = ("cmd_deleteNode", obj,),
                next_state = (_HuntForNode,) # todo: use SAME_STATE here
             )
        return None # for anything we don't understand, use handler below us
    pass

# ==

class DeleteNodeTool(Tool):
    _default_state = (_HuntForNode,)
    HighlightGraphics_class = TrivalentGraph_HighlightGraphics
        # instance ends up in self._f_HighlightGraphics_instance,
        # but this code mostly uses self._f_HighlightGraphics_descriptions instead.
    pass

# end
