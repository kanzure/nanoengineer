"""
TrivalentGraphModel.py

$Id$

bug: rubber edges stopped working...
"""

from demoapp.geometry.vectors import V, dot, vlen, unitVector, rotate2d_90

import pyglet

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
    def destroy(self):
        for e in self.edges[:]:
            e.destroy()
        self.edges = []
        del self.model.nodes[self]
    def new_edge_ok(self):
        return len(self.edges) < 3
    def new_edge_ok_to(self, node):
        return self.new_edge_ok() and not self.connected_to(node)
    def connected_to(self, node):
        for edge in self.edges:
            if node in edge.nodes:
                return True
        return False
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
    def hit_test(self, x, y): # modified from soundspace.py; made 2d; could improve using vectors.py functions
        dx, dy  = [a - b for a, b in zip(self.pos, (x, y))]
        if dx * dx + dy * dy  < self.radius * self.radius:
            return -dx, -dy,  # return relative position within object
    pass

class Edge(ModelComponent):
    def __init__(self, model, n1, n2):
        assert isinstance(n1, Node)
        assert isinstance(n2, Node)
        assert n1 is not n2
        assert not n1.connected_to(n2)
        assert not n2.connected_to(n1)
        self.model = model
        self.nodes = (n1, n2) # sequence or set of our nodes
        for n in self.nodes:
            n.edges.append(self)
    def destroy(self): # (what about undo?)
        del self.model.edges[self]
        for n in self.nodes:
            n.edges.remove(self)
        self.nodes = ()
    def draw(self):
        drawline2d(black, self.n1.pos, self.n2.pos) # refactor, use in rubber_edge: draw_Edge
    @property
    def n1(self):
        return self.nodes[0]
    @property
    def n2(self):
        return self.nodes[1]
    def other(self, node):
        if self.nodes[0] is node:
            return self.nodes[1]
        else:
            assert self.nodes[1] is node
            return self.nodes[0]
        pass
    def hit_test(self, x, y):
        HALO_RADIUS = 2 # or maybe 1?
        p1 = self.nodes[0].pos
        p2 = self.nodes[1].pos
        direction_along_edge = unitVector(p2 - p1)
        unit_normal_to_edge = rotate2d_90(direction_along_edge)
        vec = V(x,y) - p1
        distance_from_edge_line = abs(dot(vec, unit_normal_to_edge))
        if distance_from_edge_line > HALO_RADIUS:
            return False
        distance_along_edge_line = dot(vec, direction_along_edge)
        if HALO_RADIUS <= distance_along_edge_line <= vlen(p2 - p1) - HALO_RADIUS:
            # For our purposes, exclude points too near the endpoints --
            # matches to a rectangle centered on the edge and not within
            # halo radius (along the edge) of the endpoints. (If node radius
            # is larger, near-endpoint behavior won't matter anyway, since we
            # treat nodes as being in front of edges.)
            return True
        return False
    pass

class TrivalentGraphModel(object):
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

    def cmd_addNodeOnEdge(self, x, y, edge):
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

    def cmd_MergeNodes(self, node1, node2):
        "merge node1 with node2 (retaining properties of node2, e.g. .pos)"
        node1_neighbors = [e.other(node1) for e in node1.edges] # might include node2
        node1.destroy()
        for n in node1_neighbors:
            if n is not node2 and not n.connected_to(node2):
                self.cmd_addEdge(n, node2)
        return True

    def hit_test_objects(self): # front to back
        for node in self.nodes.itervalues():
            yield node
        for edge in self.edges.itervalues():
            yield edge

    def drawn_objects(self):
        return self.hit_test_objects() #stub

    def draw(self):
        for obj in self.drawn_objects():
            obj.draw()

    pass
