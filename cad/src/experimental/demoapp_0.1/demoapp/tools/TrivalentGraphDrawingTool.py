"""
TrivalentGraphDrawingTool.py - tool for drawing new nodes and edges into a trivalent graph

$Id$

bugs, fri eve 080613:
- sometimes app seemingly can get stuck; not seen recently
- might be fixed:
  can't drag an existing node i click in when no edge will be drawn by that click
  - not sure i like the lack of drag of node i connect edge to, either;
    but at least, if i click and it doesn't connect and has no rubberedge, i should be able to drag.
- lack of tip when it starts or just does an action is inconsistent;
  otoh the tip we want then might be better in a fixed bottom place
  than next to the cursor. plus we need prefs to turn off "empty space tips" and/or other tips.
  need to classify tips, then have pref for each kind, off or bottom or cursor.
  - mitigated by removing emoty space tips since rubber objs are sufficient
- should prohibit recconnecting two nodes that are already directly connected
  (ie making new edge identical to old one)
- since latest chg, has visual glitches (briefly seen tips that are now mostly gone)

sat aft:
- mouse leave doesn't stop showing the gray rubber node -- i guess we need to bind that event directly
- "drag this node" is wrong, you can also add an edge to it, or both... so fix tip,
  also fix behavior so if you do drag it, you're done, i.e. "drag it *or* add edge to it". tip: "drag or add edge".
- yellow *around* dragnode is distracting, should change it to *be* yellow.
- should make all these lines thickness 2


nfr:
- drag one node over another -> merge nodes (if let go)
- node cmenu command to dissolve node, merging edges, when node has exactly 2 edges
- want other tools, e.g. one for only making nodes, only dragging, only making edges, etc

"""

from pyglet.event import EVENT_HANDLED

from demoapp.foundation.MouseBehavior import Tool, CMD_RETVAL, ToolStateBehavior, Transition ##, SAME_STATE

from demoapp.tools.HuntForClickAction_ToolStateBehavior import HuntForClickAction_ToolStateBehavior
from demoapp.tools.HuntForReleaseAction_ToolStateBehavior import HuntForReleaseAction_ToolStateBehavior

from demoapp.geometry.vectors import A, V

from demoapp.models.TrivalentGraph_Graphics import TrivalentGraph_HighlightGraphics

# ==

class HuntForNode(HuntForClickAction_ToolStateBehavior): # rename: HuntForNodeFromNode?
    """
    Mouse motion draws out a new edge from a given node (if that's not None),
    and looks for places where clicks could create new nodes (almost anywhere).
    """
    # instance variables
    # (in superclass: _tip_and_highlight_info)
    node = None
    _ever_moved_off_self_node = False

    def __init__(self, tool, node):
        super(HuntForNode, self).__init__(tool)
        if node and not node.new_edge_ok():
            node = None
        self.node = node # last-clicked node, start of rubber edge to a new node

    def on_mouse_press_would_do(self, x, y, button, modifiers):
        """
        Click makes new node or finds existing one,
        and makes an edge to it from the last-clicked or last-made node if any.
        """
        model = self.model
        obj = self.pane.find_object(x, y) # might be None
        if self.node and obj is not self.node:
            self._ever_moved_off_self_node = True
        hh = self.tool._f_HighlightGraphics_descriptions
        if self.node and obj is self.node:
            if self._ever_moved_off_self_node:
                return Transition(
                    indicators = [hh.tip_text("click to stop drawing edges", obj), #e clarify text
                                  hh.highlight_refusal(obj)
                                  ],
                    command = None,
                    next_state = (HuntForNode, None)
                 )
            else:
                return Transition(
                    indicators = None,
                    command = None,
                    next_state = (HuntForNode, None)
                 )
        elif isinstance(obj, model.Node):
            # click on another node: connect our node to it, if both nodes permit
            if self.node and obj.new_edge_ok_to(self.node):
                return Transition(
                    indicators = [hh.tip_text("click to connect to this node", obj),
                                  hh.highlight_connect_to(obj),
                                  hh.rubber_edge(self.node, obj)
                                  ],
                    command = ("cmd_addEdge", obj, self.node),
                    next_state = (HuntForNode, obj)
                        ### TODO: sometimes, pass to HuntForNode None instead of obj,
                        # in order to "stop drawing edges" after making this connection,
                        # e.g. if it "closed a loop".
                 )
            elif self.node and obj.connected_to(self.node):
                return Transition(
                    indicators = [hh.tip_text("(already connected to this node)", obj),
                                  hh.highlight_refusal(obj)
                                  ],
                    command = None,
                    next_state = (DragNode, obj, (x,y))
                 )
            elif self.node:
                return Transition(
                    indicators = [hh.tip_text("(can't connect to this node)", obj),
                                  hh.highlight_refusal(obj)
                                  ],
                    command = None,
                    next_state = (DragNode, obj, (x,y))
                 )
            elif obj.new_edge_ok():
                return Transition(
                    indicators = [hh.tip_text("drag this node, or click to connect it to other nodes", obj),
                                  hh.highlight_drag(obj)
                                  ],
                    command = None,
                    next_state = (DragNode, obj, (x,y))
                 )
            else:
                return Transition(
                    indicators = [hh.tip_text("drag this node", obj),
                                  hh.highlight_drag(obj)
                                  ],
                    command = None,
                    next_state = (DragNode, obj, (x,y))
                 )
        elif obj is None:
            # click in empty space [todo: make sure not too near an existing node];
            # create a new node here [todo: depends on type of background object]
            # and maybe connect to it.
            if self.node: # todo: and not too close to any existing node
                return Transition(
                    indicators = [ # tip_text is not needed due to rubber objects:
                                   ## hh.tip_text("click to create new node and connect to it", (x,y)),
                                   hh.rubber_edge(self.node, (x,y)),
                                   hh.rubber_node((x,y))
                                   ],
                    command = ("cmd_addNodeAndConnectFrom", x, y, self.node), # todo: model coords
                    next_state = (DragNode, CMD_RETVAL, (x,y))
                 )
            else:
                return Transition(
                    indicators = [ # tip_text is not needed due to rubber objects:
                                   ## hh.tip_text("click to create new node (and start drawing edges)", (x,y)),
                                   hh.rubber_node((x,y))
                                   ],
                    command = ("cmd_addNode", x, y),
                    next_state = (DragNode, CMD_RETVAL, (x,y))
                 )
        elif isinstance(obj, model.Edge):
            # click on edge: make a node there, then act as if we clicked on it
            if self.node and self.node not in obj.nodes:
                return Transition(
                    indicators = [hh.tip_text("click to insert new node into this edge, and connect to it", (x,y)),
                                  hh.highlight_insert_into(obj),
                                  hh.rubber_node((x,y)),
                                  hh.rubber_edge(self.node, (x,y)),
                                      # fix: not quite correct position
                                      # (we want same corrected pos for tip and both highlights),
                                      # and doesn't indicate change to old edge
                                  ],
                    command = ("cmd_addNodeOnEdgeAndConnectFrom", x, y, obj, self.node),
                    next_state = (DragNode, CMD_RETVAL, (x,y))
                 )
            elif not self.node:
                return Transition(
                    indicators = [hh.tip_text("click to insert new node into this edge", (x,y)),
                                  hh.highlight_insert_into(obj),
                                  hh.rubber_node((x,y))
                                      # fix: not quite correct position (same as in above case)
                                  ],
                    command = ("cmd_addNodeOnEdge", x, y, obj),
                    next_state = (DragNode, CMD_RETVAL, (x,y))
                 )
            else:
                # self.node is one of the endpoints of this edge (obj)
                return None
        return None # for anything we don't understand, do nothing and use the handler below us...
            # (e.g. this lets us highlight and click buttons even if they are "behind" us,
            #  in the general case -- but not in current code, since even empty space has an action
            #  for us. For this state's code the buttons had better be in front or in another pane.)
    pass

# ==

class DragNode(HuntForReleaseAction_ToolStateBehavior): # works, except for bugs in merging operation (doesn't delete enough edges)
    def __init__(self, tool, node, dragstart_pos):
        super(DragNode, self).__init__(tool)
        self.node = node
        # todo: assert isinstance(node, Node), "DragNode needs a Node, not %r" % (node,)
        # for now:
        assert node, "DragNode needs a Node, not %r" % (node,) # only checks existence, not class
        ### ISSUE: are node.pos and dragstart_pos in same coords? probably not. need model to pane, vice versa. #####
        self.dragstart_pos = A(dragstart_pos)
        self.node_offset = node.pos - self.dragstart_pos

    def on_mouse_release_would_do(self, x, y, button, modifiers):
        model = self.model
        obj = self.pane.find_object(x, y,
                                    excluding = [self.node] + list(self.node.edges)
                                    ) # might be None
        hh = self.tool._f_HighlightGraphics_descriptions
        if isinstance(obj, model.Node):
            return Transition(
                indicators = [hh.tip_text("merge with existing node", obj),
                              hh.highlight_merge(self.node, obj),
                              ],
                command = ("cmd_MergeNodes", self.node, obj),
                next_state = (HuntForNode, None)
             )
        elif V(x, y) != self.dragstart_pos:
            # it moved; don't draw edges from it during subsequent mouse motion
            # (future: small motions should not count, for this or for dragging;
            #  could be done here, or by caller not sending drag events at first)
            return Transition( None, None, (HuntForNode, None) )
        else:
            # it didn't move; do perhaps draw edges from it during subsequent motion
            return Transition( None, None, (HuntForNode, self.node) )
                #### review: should this state DragNode be "called" and at this point "return",
                # rather than being jumped to and hardcoding what to jump back out to?
                # if so, how to pass None or self.node?

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        "[extends superclass version]"
        self.node.pos = self.node_offset + V(x, y)
        res = super(DragNode, self).on_mouse_drag(x, y, dx, dy, buttons, modifiers)
            # superclass method handles tip & highlighting specific to this potential release-point
        return res

    def on_mouse_release(self, x, y, button, modifiers):
        "[extends superclass version]"
        self.node.pos = self.node_offset + V(x, y)
        res = super(DragNode, self).on_mouse_release(x, y, button, modifiers)
        return res

    ### REVIEW: what about on_draw_handle? (to highlight this node to indicate we're dragging it)
    # different look for could drag or is dragging? text tip "dragging"?

    pass

# ==

class TrivalentGraphDrawingTool(Tool):
    _default_state = (HuntForNode, None)
    HighlightGraphics_class = TrivalentGraph_HighlightGraphics
        # instance ends up in self._f_HighlightGraphics_instance,
        # but this code mostly uses self._f_HighlightGraphics_descriptions instead.
    pass

# end

