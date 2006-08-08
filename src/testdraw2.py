'''testdraw2.py - testdraw.py was getting too big to edit conveniently
'''

#e needs cvs add, file header

from testdraw import *


# nim things here: ###@@@
# If, Slanted, Identity, Spacer, Centered
# Centered(None) needs to work; None is sort of like a Spacer(0,0), which is like a Rect but doesn't draw anything
# node.openable, open, disabled, kids
# Row(dict, ...) (and in Column; do it in WE.__init__)
# Row option wrap, wrap each element

# questions:
# - does node.openable work normally, or is node a symbol?
# - do we filter all nodes through a view that gives them our own attrs for them (like filtered kids, our own open state)?
# - will this "python class" style keep working, even as we add DND behavior, or anything else?
#   - guess: yes, since it can find some way to pick up cached state, and anyway it needs that, for code to be reloadable.
#   - digr: Column might like a way of displaying an extra thing over a gap, to help us indicate DND-points.
# - how would display lists work?
#   - guess: as cached state, mainly used by draw methods, which first see if their valid for reuse.
# So it seems like we scan all that we'll draw, every frame, and decide what to reuse, at least in this formulation.
# That is, if we wanted a display list for a node, to reuse when nothing changes inside it,
# we'd have to modify this very code (self.display_node) to know about that,
# and say how to set it up and decide whether it could reuse it.
# (This would help with DND too, where we'd make display lists for all indeply-moving parts, like the moving and not-moving MT,
#  and maybe even the parts we cross over if we let the drop-gap get wider dynamically.)

stubrect = Rect(1,1,black)

# This style of Widget Expr (a python class, with per-frame display methods) lets us use Python subclasses
# as our way of extending it by overriding certain methods.
#
# It will only work if it's ok to remake the specific widget exprs each time.
#
# That means it also lets us use python execution to do some of the per-frame logic, e.g. map over node.kids.

class MT: ###e super?
    def display_node(self, node):
        #e self = self.withmods(mods), if we add **mods to arglist above
        return Column(
            self.display_node_wo_kids(node),
            If( node.openable and node.open,
                self.display_kids(node)
            )
        )
    def display_node_wo_kids(self, node):
        maybe_slanted = If( node.disabled, Slanted, Identity)
        return Row(
            dict(gap = 0.1, wrap = Centered), #####@@@@@ is this a good feature for including options at the start?
            self.display_openclose(node), # even if not openable (this leaves room for one)
            maybe_slanted(
                self.display_type_icon(node),
                self.display_text(node)
            )
        )
    def display_openclose(self, node):
        if not node.openable:
            want = None
        elif node.open:
            want = Button()#e actions: lambdas or helpers on node; state: node.xxx
        else:
            want = Button()#e
        spacer = Spacer(1,1) # make sure it has the right width
        return Overlay(spacer, Centered(want) )
    def display_type_icon(self, node):
        return stubrect
    def display_text(self, node):
        return stubrect
    
    def display_kids(self, node):
        kids = node.kids #e filter them by type
        return Column( dict(gap = 0.1), *map( self.display_kid, kids)) #k syntax?
    def display_kid(self, kid):
        indent = stubrect # actually, either a gap, or an hline attached to the vline from the parent openclose icon
        ###e is kid already a node of the right kind? if we make it the right type on purpose, where do we do that? in display_node?
        # or in node.kids itself?
        return Row( dict(gap = 0.1), indent, self.display_node(kid))
    pass

