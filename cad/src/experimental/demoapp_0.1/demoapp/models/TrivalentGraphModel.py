"""
TrivalentGraphModel.py

$Id$
"""

from demoapp.geometry.vectors import V

import pyglet

# from pyglet.gl import * - not sure if needed - try it

from demoapp.graphics.colors import black

from demoapp.graphics.drawing import drawline2d

from demoapp.models.TrivalentGraph_Graphics import NODE_RADIUS, draw_Node

# ==

class ModelComponent(object): #refile
    def hit_test(self, x, y):
        return False

class Node(ModelComponent):
    radius = NODE_RADIUS
    def __init__(self, model, x, y):
        self.model = model
        self.x = x
        self.y = y
        self.edges = [] # sequence or set of our edges
    def new_edge_ok(self):
        return len(self.edges) < 3
    def draw(self, highlight_color = None):
        draw_Node( self.pos,
                   self.radius,
                   numedges = len(self.edges),
                   highlight_color = highlight_color)
    def get_pos(self):
        return V(self.x, self.y)
    def set_pos(self, pos):
        self.x, self.y = pos
    pos = property(get_pos, set_pos)
    def hit_test(self, x, y): # modified from soundspace.py; made 2d
        dx, dy  = [a - b for a, b in zip(self.pos, (x, y))]
        if dx * dx + dy * dy  < self.radius * self.radius:
            return -dx, -dy,  # return relative position within object
    pass

class Edge(ModelComponent):
    def __init__(self, model, n1, n2):
        self.model = model
        self.nodes = (n1, n2) # sequence or set of our nodes
        for n in self.nodes:
            n.edges.append(self)
    def destroy(self): # CALL ME (and what about undo?)
        del self.model.edges[self]
        for n in self.nodes:
            n.edges.remove(self)
        self.nodes = []
    def draw(self):
        drawline2d(black, self.n1.pos, self.n2.pos) # refactor, use in rubber_edge: draw_Edge
    @property
    def n1(self):
        return self.nodes[0]
    @property
    def n2(self):
        return self.nodes[1]
    # todo: def hit_test
    pass
    
class TrivalentGraphModel(object): ## was: (pyglet.event.EventDispatcher)
    # REVISE: rename, then split out superclass Model
    """
    model for a partial or complete trivalent graph
    """
    Node = Node
    Edge = Edge
    
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        
    def cmd_addNode(self, x, y):
        n = self.Node(self, x, y)
        self.nodes[n] = n
        #print "added", n
        return n

    def cmd_deleteNode(self, n):
        for e in list(n.edges):
            e.destroy()
        del self.nodes[n]
        return True # only needed due to an assert that is wrong in general
    
    def cmd_addEdge(self, n1, n2):
        e = self.Edge(self, n1, n2)
        self.edges[e] = e
        #print "added", e
        return e

    def cmd_addNodeAndConnectFrom(self, x, y, node):
        # 'From' in cmdname is because node order within edge
        # might matter someday, for a directed graph
        node2 = self.cmd_addNode(x, y)
        self.cmd_addEdge(node, node2)
        return node2

    def cmd_addNodeOnEdge(self, x, y, edge): #note: never called until edge hit_test is implemented ###
        node2 = self.cmd_addNode(x, y) # todo: position it exactly on edge? if so, worry if mouse still over it re KLUGE elsewhere
        n1, n3 = list(edge.nodes) # seq or set; in order, if that matters
        edge.destroy()
        self.cmd_addEdge(n1, node2)
        self.cmd_addEdge(node2, n3)
        return node2

    def cmd_addNodeOnEdgeAndConnectFrom(self, x, y, edge, node):
        node2 = self.cmd_addNodeOnEdge(x, y, edge)
        self.cmd_addEdge(node, node2)
        return node2
    
    def draw(self):
        for obj in self.drawn_objects():
            obj.draw()
    def hit_test_objects(self): # front to back
        for node in self.nodes.itervalues():
            yield node
        for edge in self.edges.itervalues():
            yield edge
    def drawn_objects(self):
        return self.hit_test_objects() #stub
    pass

##TrivalentGraphModel.register_event_type('cmd_addNode')
##TrivalentGraphModel.register_event_type('cmd_addEdge')
##TrivalentGraphModel.register_event_type('cmd_addNodeAndConnectFrom')
##TrivalentGraphModel.register_event_type('cmd_addNodeOnEdge')
##TrivalentGraphModel.register_event_type('cmd_addNodeOnEdgeAndConnectFrom') # todo: autoregister based on prefix; or pass 'cmd_*' to this method
