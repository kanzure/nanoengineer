"""
demo_dna.py
$Id$
"""


from basic import *
from basic import _self

import Rect
reload_once(Rect)
from Rect import Rect, RectFrame

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import transforms
reload_once(transforms)
from transforms import Translate

import Center
reload_once(Center)
from Center import Center

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable


# let's start with a resizable rectangular raster of dna turns.
# it's really a resizable guide shape on which we can draw regions of dna to fill in,
# and they in turn act as guide shapes for placing actual strands, cyls, etc, or paths or seams.

# but to start with, let's just be able to draw it... and have it draw some little objs on which to click to fill it or make crossovers.

# so something much simpler is a resizable table of little rects.

# it has the rects, and a resize handle.

# do we bother at this stage to split it into its data and its appearance? Not yet, since that's hard....

Grid = Resizer = Stub

class xxx(DelegatingInstanceOrExpr):
    nrows = State(int, 5) # each row is actually two helices
    ncols = State(int, 10)
    delegate = Overlay(
        Grid( Rect(1), nrows, ncols ),
        Resizer() # resizer of what? and, displayed where? aligned with a grid corner? how?
            # is a Box resizer (one per corner) any simpler?
    )
    pass

# ok, I've still never made a resizable box, resizable at each corner.

class newerBoxed(DelegatingInstanceOrExpr):
    # args
    thing = Arg(Widget2D)
    # options
    borderthickness = Option(Width, 4 * PIXELS)
    gap = Option(Width, 4 * PIXELS)
    bordercolor = Option(Color, white)
    # internal formulas
    extra1 = gap + borderthickness
    ww = thing.width  + 2 * extra1 #k I'm not sure that all Widget2Ds have width -- if not, make it so ##e [061114]
    hh = thing.height + 2 * extra1
    # value
    delegate = Overlay( Translate( RectFrame( ww, hh, thickness = borderthickness, color = bordercolor),
                                 - V_expr( thing.bleft + extra1, thing.bbottom + extra1) ), #e can't we clarify this somehow?
                      thing)
    pass

##class ResizableBox(DelegatingWidgetExpr): # compare to Boxed
##    Overlay(RectFrame(),
##            


class resizablyBoxed(DelegatingInstanceOrExpr):
    # args
    thing = Arg(Widget2D) # display thing (arg1) in the box, but don't use it for the size except to initialize it
    # options
    borderthickness = Option(Width, 4 * PIXELS)
    gap = Option(Width, 4 * PIXELS)
    bordercolor = Option(Color, white)
    # state - initialize from formulas based on args and instance sizes, is that ok??
    thing_width = State(float, thing.width) #k I'm not sure that all Widget2Ds have width -- if not, make it so ##e [061114]
    thing_height = State(float, thing.height)
    # internal formulas, revised to use state
    extra1 = gap + borderthickness
    ww = thing_width  + 2 * extra1
    hh = thing_height + 2 * extra1
    # not yet any way to change the state... to test, add on_press which adds 1 to it or so #e
    # value
    delegate = Overlay( Translate( RectFrame( ww, hh, thickness = borderthickness, color = bordercolor),
                                 - V_expr( thing.bleft + extra1, thing.bbottom + extra1) ),
                                    #e can't we clarify this somehow? yes -- RectFrame should take origin, dx, & dy args.
                        Highlightable(thing, on_press = _self.on_press_thing))
    #e now we need to say that at each corner there's a resizer.
    # Resizer -- of what? looks like what? shown where?
    # really it's a kind of draggable -- a draggable corner, used to drag two intersecting lines (perp in this case).
    # We have to express an aspect of our state as "the posns of these two lines" --
    #
    #                   /
    # if corner is ____/,  then each line can be moved along the other one, so each line gives a vector of motion for a control point
    # on the other -- in fact, the vertex itself can be the control point for both (provided we can express the line that way on demand).
    # So a resizer of intersecting edges needs the edges as args, then it gets the point how?
    # But a polygon is natively more like a bunch of points... and variants of moving cmds of those are discussed elsewhere...
    # one is to move a set of points, controlling some edges fully (if both ends in the set) and some partly (keeping them parallel
    # or keeping other end fixed, depending on the tool). So we first turn selection into controlled & fixed aspects, then into
    # drag action on controlled aspects, which is basically a command to take a delta or new point and apply it to the state.
    # So how do we express a drag command of that kind?
    #    Drag( what? a set of points... with info about how other things respond -- which depends on where you got the point-lvals.)
    #          polygon.draggable_edges( vertex_set) -> ...
    #          polygon.draggable_vertices( vertex_set) -> ...
    # Those can be args to whatever wants to know what to drag! The result is equivalent to a single draggable point, I guess...
    # anything that can accept a drag_from_p1_to_p2 command. So an object with some looks, and some drag commands in certain places,
    # can take draggables as args. Resizer() has a certain look, and places itself at the drag point: Resizer(draggable).
    # Note that it needs the draggable to have a center or corner or so, not just an ability to move from p1 to p2.
    # (The center is not usually equal to p1, but slightly offset from it.)
    #   A CornerResizer would be specialized (in look) for a draggable corner. Also EdgeResizer. They'd still need binding to some
    # givable event (mouse button and mod key combo) (or to have a cmenu or so). And options to affect the look (like whether to have one).
    def on_press_thing(self):
        self.thing_width += 1
        self.thing_height += 2
    pass

Data = Stub # Type? Interface?

class DraggableCorner(Data): ### a description of a data type (an interface to data -- can be state-like, readable/settable)
    "an interface which has a draggable center point, and a corner on it (an ordered pair of vectors coming from it)"
    # attrs -- Attr?? Data?? State? Arg? Option? Are they used for construction? Implication of orthogonality for Set?
    point = Attr(Point) # Point? Position? it's supposed to be Draggable -- where do we say that? just say DraggablePoint here?
    vnext = Attr(Vector) # vector to next corner point (in ccw order) (e.g. to the right and up, if we're a bottom corner)
    vprev = Attr(Vector) # vector to previous corner point (e.g. to left and up, if we're a bottom corner)
        ###k these make sense as 2d vectors -- what about 3d? can still make perfect sense if we assume the thing is planar.
    draggable_commands = point.draggable_commands ###k ok to say it that way??
    pass

class Resizer(DelegatingInstanceOrExpr):
    "anything that has a delegate for looks, and puts a drag-binding on it which drags self.what" # looks like this, drags that
##    def _cmd_drag_from_to(self, p1, p2):
##        self.what._cmd_drag_from_to(p1,p2) ###k? or all the draggable_commands??
    draggable_commands = _self.what.draggable_commands
        #e do we ask for this interface by name, when giving any of these commands?? ####k
        #e as if IorE had a rule, _cmd_drag_from_to = _self.draggable_commands._cmd_drag_from_to ?
        # overridable of course by a specific def of _cmd_drag_from_to.
        #  (But if we override _cmd_drag_from_to, has that overridden something else asking us for self.draggable_commands?
        #   Only if the specific methodname is effectively an alias (even for redef and inheritance, at least by deleg) for the
        #   one in self.draggable_commands. That can be done somehow, *if* we can figure out the exact desired rules.)
        # Do we have a naming convention for assignable interfaces? _I_draggable = _self.what._I_draggable
    pass


class CornerResizer(Resizer):
    what = Arg(DraggableCorner)
    mylen = 2 #stub; ideally we'd ask the edges if they have a thickness, and assign them one if not (for our sib corners to see)
    delegate = Rect(origin = what.point,
                    dx = UnitVector(what.vnext) * mylen,
                    dy = UnitVector(what.vprev) * mylen,
                    color = white) # parallelogram
    pass

# hmm, all we need for that is details and biggies:
# - UnitVector
# - Rect(origin = , dx = , dy =, color =)
# - unstub mylen
# - Data, and interface concept in general
#   - assign draggable_commands separately [could be done as outlined above]
#   - declare Attr/Data/State/Arg or whatever within a data type
# - a lot of the ways we want to extend this are assuming we have a good way to bring extra info along for free
#   (like edge thickness to affect resizer size, tooltip text to come with a drag-command, etc)
#   - part of the point of a declared interface is to help the system know what goes with what, by default (conjecture)
#   - a more important part is for auto-glue-code (like type coercion)
#   - it means we have to declare the interfaces things have... superclasses count...
#     and it needs to be easy to define the glue in the original class (show how to make it fit some interface) or separately
#   - the interface bundling a set of attrs that can also be accessed directly seems common -- in fact, maybe they preexisted it

class Corner(Interface):
            # why call it Interface, even if it is one? 
            # It's many things: a constructor for a thing which follows that interface,
            # a data type we could use in other things and save...
            # nothing prevents other things from acting like this, and saying they can act like it, and how...
            # not least, an expr written as Corner(formulas).
            # In fact that's the usual way something would say how to coerce itself to a Corner -- describe one which is the result of that.
            # It can do that on an attr whose name is the interface name, or formed from that: thing._as_Corner.
            # There is some way to supply everything with a formula like that (default and/or overriding?) -- lexically for use
            # when your code asks to convert things to Corners? Or dynamically, when things you call do that?? In the "drawing env"
            # (the env used to produce certain outputs or to run methods in a certain interface)?
            #
            # digr: BTW, a Widget is just a thing which might have state and which follows a certain small set of interfaces,
            # e.g. for looks, size, ui responses, etc.
    point = Arg(Point)
    vprev = Arg(Vector)
    vnext = Arg(Vector)
    pass

c1 = Corner(p, v0, v1)

# using up words is risky ... what about a 3D corner? \ | /
#                                                      \|/
# it has more stuff, a point and a circularly-ordered set of vectors giving it 3 2d corners, but is just as deserving of the name Corner.
#
# specific point: I might call them Corner2D and Corner3D.
# general point: we'll need namespaces.

# I've also called Interfaces Situations... the connotations are different -- is there any formal difference? ##k

# What are the interfaces I know I need so far?
# - every data type I've used in type coercion:
#   Point Vector Position Type StateRef Width Color Widget Widget2D
# - implicit interfaces, not yet named:
#   - draw method
#     - variants for highlighting, transparency
#   - lbox attrs
# - others
#   - command
#   - action, event binding, tool
#   - ... every complex data type seems to also be an interface

# a data type can say how to coerce it to an interface; an interface can say how it coerces data.
# What if they both say that? Then the data type wins, since if it says this, it's not distinguishable from it *already* being
# in that interface. A program, OTOH, can see the true datatype and do whatever it likes with it...
# but if what it does is ask it to coerce itself to an interface, that's what happens, acc'd to datatype.
# Would it matter which one it asked first, data or interface? Not sure, seems bad.

# What interfaces do my classes, so far, belong to?
# - all their superclasses
# - that's just about all, except for a few basic interfaces that should be known to the supers.
#
# A super needs to be able to say how a sub coerces, using things to be defined in the sub.
# It does this by giving a formula for the coerced version and/or pieces of it.
# I think the fundamental defs of what class is in what types has to be runtime --
# that means, my existing classes should be defining defaults for this, by ExprsMeta or by a general rule that it defaults to the supers.
# (Or at least the ones that say they can be used as types.)

# So is an Interface just a Type?

# For a long time, we don't need nontrivial coercers! They can just look up formulas and fail if they don't find them.
# We do however need the option to define one thing in a variety of ways,
# so if certain things are given and others not, we can say in general how to compute the rest, w/o being ambiguous or circular.
# Q: does the following way work: let caller specify some formulas, then whichever ones are not there, use defaults,
# and detect circularity as an error, "not enough specified"? I doubt that's enough. We need to pick correct formula for X
# based on whether Y or Z was defined. It's almost more like executing a program that says "if these are defined and those not, do this"...
# This means, we need to know if a super, defining an attr, is defining it in a way that counts for this, or only as a default.
