"""
TrivalentGraph_Graphics.py

$Id$
"""

from pyglet.gl import *

from demoapp.graphics.colors import red, black, green, yellow

from demoapp.graphics.drawing import drawcircle2d, drawline2d

from demoapp.geometry.vectors import get_pos

from demoapp.foundation.tool_graphics import HighlightGraphics

# ==

NODE_RADIUS = 5

def draw_Node(pos, radius, numedges = 0, highlight_color = None, color = None):
    if color is None:
        if numedges < 3:
            color = green
        elif numedges == 3:
            color = black
        else:
            color = red
    x, y = pos
    glColor3f(*color)
    drawcircle2d(radius, x, y)
    if highlight_color:
        glColor3f(*highlight_color)
        drawcircle2d(radius + 1, x, y)
        drawcircle2d(radius + 2, x, y)
    return

class TrivalentGraph_HighlightGraphics( HighlightGraphics):
    def rubber_edge(self, node_or_pos_1, node_or_pos_2):
        drawline2d( self.rubber_object_color,
                    get_pos(node_or_pos_1),
                    get_pos(node_or_pos_2) ) # draw_Edge = drawline2d?
    def rubber_node(self, pos):
        draw_Node(pos, NODE_RADIUS, color = self.rubber_object_color)
        pass
    def highlight_refusal(self, obj):
        obj.draw( highlight_color = red) # bug: only implemented for nodes
        pass
    def highlight_connect_to(self, node):
        node.draw( highlight_color = yellow)
        pass
    def highlight_merge(self, node1, node2):
        node1.draw( highlight_color = yellow)
        node2.draw( highlight_color = yellow)
        pass
    def highlight_insert_into(self, edge):
        #todo
        pass
    def highlight_drag(self, node):
        node.draw( highlight_color = yellow)
        pass
    def highlight_delete(self, obj):
        pos = obj.pos
        draw_Node(pos, NODE_RADIUS, color = red)
        draw_Node(pos, NODE_RADIUS + 1, color = red)
        pass
    pass

# move all imports of the above
