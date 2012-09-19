# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
demo_polygon.py [recently renamed from demo_dna.py]

$Id$

scratch file about Resizer, Draggable, and especially Interface...
and polygon-vertex dragging, for exploring some Draggable/DragCommand structure issues.

The specific code in it is mostly about polygon-vertex dragging.
"""

from basic import *
from basic import _self

from Rect import Rect, RectFrame

from Overlay import Overlay

from transforms import Translate

from Center import Center

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
        #   one in self.draggable_commands. That can be done somehow, *if* we can figure out the exact desired rules. ###e)

        # An alternative way of defining/implementing per-Interface delegation -- just a modification of delegation & inheritance
        # which can look up, for each attr, what interface it's in and therefore how to delegate it & define it.

        # Do we have a naming convention for assignable interfaces? _I_draggable = _self.what._I_draggable
    pass

# which commands are the draggable_commands, aka _I_draggable or _I_Draggable ?
# - _cmd_drag_from_to [#e rename -- more concise?]
# - point or center (?) (also part of some more basic geometric interface)
#   (in fact a Draggable would often have a size & shape -- but it's not required)


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
#     (i.e. the attrs were defined, then we decided later they were all part of an interface)

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

# So is an Interface just a Type?    (note, it might be a distinct concept, but able to be automade (coerced) from a Type.)

# For a long time, we don't need nontrivial coercers! They can just look up formulas and fail if they don't find them.
# We do however need the option to define one thing in a variety of ways,
# so if certain things are given and others not, we can say in general how to compute the rest, w/o being ambiguous or circular.
# Q: does the following way work: let caller specify some formulas, then whichever ones are not there, use defaults,
# and detect circularity as an error, "not enough specified"? I doubt that's enough. We need to pick correct formula for X
# based on whether Y or Z was defined. It's almost more like executing a program that says "if these are defined and those not, do this"...
# This means, we need to know if a super, defining an attr, is defining it in a way that counts for this, or only as a default.

# ==

# back to drag commands: (use some supers from Command_scratch_1.py)

class typical_DragCommand(ClickDragCommand):
        # ??? maybe this is also a declared way of coercing any Draggable to a ClickDragCommand?
        # if so we might rename it in such a way as to indicate that and permit it to be autoregistered for that use.
        # (it has to be registered with either Draggable or ClickDragCommand or TypeCoerce or env... details unknown.)
    delegate = Arg(Draggable) # general delegate?? or change to a delegate just for _cmd_drag_from_to?
        # argument in favor of general: maybe it wants to define extra info to be used for this purpose.
        # I wonder if it can define extra info "only to be visible if i'm coerced to or seen as a DragCommand"... #k
    def on_press(self):
        point = whatever # see example in demo_drag.py; point should be the touched point on the visible object (hitpoint)
        self.oldpoint = point
        return
    def on_drag(self):
        point = whatever # see example in demo_drag.py
        oldpoint = self.oldpoint # was saved by prior on_drag and by on_press
        self._cmd_drag_from_to( oldpoint, point) # use Draggable interface cmd (to delegate)
        self.oldpoint = point
        return
    def on_release(self):
        pass
    pass


# let's assume that a Corner can be dragged because setting its point will work (preserving vectors, or not touching their formulae --
#  so they might change if they are defined in terms of point, and not if they are defined as indep state)
# and by default the implem of _cmd_drag_from_to will work by resetting self.point with the same delta in 3d space.

class _default_Draggable_methods: ###e name, super -- is it just part of Draggable itself??
    def _cmd_drag_from_to( self, p1, p2):
        self.point += (p2 - p1)
        return
    pass

class Draggable(...): ###e super? is it a kind of Command in all these cases? not sure.
    point = Attr(Point) # declare it as something any draggable must have. Do we say State so if not overridden it's defined as state??##k
    def _cmd_drag_from_to( self, p1, p2):
        self.point += (p2 - p1)
        return
    #e some tooltip and disablement cond to go with that cmd
    # (the reason it starts with _cmd_ is so its clients know they can look for these --
    #  it's a kind of interface made of several methodnames parametrized by one methodname-root!)
    pass

# ==

# some specifics about dragging a set of polygon vertices while keeping edge directions unchanged. (as an example DragCommand)

class drag_verts_while_edgedirs_unchanged(DragCommand):
    verts = Arg(ListOf(Vertex)) ###IMPLEM ListOf ##e rename Vertex? they need to be "polygon vertices" for this to work. Do we need the poly itself??
    def _init_instance(self): ###k might be wrong method, if instance only means we're considering the drag -- later method means doing it
        """
        Given: a set of vertices to be dragged together, with edges staying parallel, in a polygon or the like,
        Come up with: an object which accepts drag commands and alters state of them and connected verts.
           Note: we assume each vert has exactly 2 neighbor verts and thus 2 edges. Extending to valence 1 would be easy,
        but for higher valences, it would require some new UI decisions, since we would not know what to do
        when dragging 2 out of 3 neighbors of a vert we're not dragging (which ought to move that vert along, but can't).
        [future implem note: I suppose it could just go ahead and move it (perhaps unless the internal analyzer.ok flag was false),
         but I can't recall if that was the only problem in here with higher valence... maybe it was, so I should generalize this.
         There are other cases too, but if in general we either drag or leave fixed when confused, it'll probably be ok. ###e]
           Note: we may assume the entire graph is in 2D, but I can't think of a specific place where we assume that, so it might work in 3D
        (for a non-planar polygon or graph, and drags of verts in any 3D direction).
           When the graph/polygon is 2D, the user may wish to constrain delta to the same plane, either for a tilted polygon vs the screen,
        or to avoid nonplanarity due to roundoff errors. Our alg does not yet handle this in either case. The caller should constrain delta
        to the polygon's plane, *and* should separately constrain all newly set vert positions to that plane to avoid roundoff error.
        (Or maybe we should have a feature to do those things for it.) ###e
        """
        verts = self.verts # an input list; each v in it has .edges (exactly 2 or fewer)
              # [Q: do we need to identify the net or poly too? yes, if v doesn't imply it... nevermind for now, easy to add later]
              # [maybe we'll just need to specify in there that the polygon for all of them has to be the same one...
              #  but note that it doesn't! They could be in a set of polygons and this alg would work fine -- and that's useful in a UI! hmm...]
        # find the edges touched twice or once -- but for boundary verts, transclose on them if near 180 --
        # in other words, find all verts "affected" (which need to move) by transclose
        dragverts = dict([(dv,dv) for dv in verts]) # a set of those verts [##e maybe the arg should be SetOf(Vertex) so we don't need to do this here??]
        analyzers = {}
        def collect_straightneighbors(dv, dict1):
            nn = dv.neighbors ###IMPLEM .neighbors
            for v in nn:
                if v not in dict1: # (this is just an optim, but it's a big one ###k verify that it works, re transclose semantics; doc in transclose if so)
                    analyzer = corner_analyzer(v, dv, other_of_pair(nn,dv)) # (here's one place where we'd need revision for a general graph)
                    nim ###IMPLEM revised arg order ##e rename -- induced_motion_analyzer? #e should v0 arg be done in the class, e.g. in case >1?
                        # analyzer figures out how it would work to drag dv and thereby induce motion in v
                        # (assuming v's other neighbor is fixed, which is not yet known -- we'll discard this later if it's not, using extra_dragverts)
                    if not analyzer.ok: ###IMPLEM ok
                        dict1[v] = v # make v also a dragvert
                    else:
                        # save analyzer for use when we do the drag (but not all of them will be used)
                        if v in analyzers:
                            analyzers[v] = "invalid" # >1 analyzers were found; this means v will end up in extra_dragverts, so no analyzer for v will be used
                        else:
                            analyzers[v] = analyzer
                        # Note: in principle we should index analyzers by both v and dv, in case v is found from both sides;
                        # but if that happens, we know we'll never use them, since v will end up in extra_verts.
                        #    Another solution (more general since it better supports general graphs)
                        # would be for one analyzer to learn about new neighbors of v becoming dragverts,
                        # so as long as v itself didn't, it always knows how to handle v's motion for whatever neighhors are dragverts
                        # with the others assumed fixed.
                        # (This might also help with the general optim for drag-specific displists, discussed below -- not sure.)
                        #
                        # Come to think of it, that's how we'd handle a much-generalized drag of some dofs, with constraints tying them to others,
                        # some of which we should also drag, others update partially. Each dof would get analyzed, updating that alalysis incrementally in a
                        # transclose, whose units (dict entries) might be influences (effect arrows between dofs or their owning objs, not dofs themselves)
                        # so each unit has binary not gradual inclusion into the transclose set. Even during runtime we might update these analyzers
                        # to bring more stuff into the drag if limits were reached. Then they'd compile the drag-code (e.g. displist membership) for the drag,
                        # helped by knowing enough about the dofs to know which objects were purely translated.
                        nim ###IMPLEM the use
                    pass
                continue
            return
        def collect_allneighbors(v,dict1): ###e this could be removed since they're in analyzers
            for v2 in v.neighbors:
                    dict1[v2] = v2
            return
        dragverts = transclose(dragverts, collect_straightneighbors) # all the verts we have to drag (will later include extra_dragverts)
        allverts = transclose(dragverts, collect_allneighbors) # all the verts affected when we drag those (including those)
        # the formula for vert motion is simple: dragverts move with the drag, and any other verts move because one edge
        # connects them to some dragvert, and needs to stay parallel -- unless they have more than one edge connected to a dragvert,
        # in which case, assume they move entirely with the drag -- and assume they have no other edges (this alg breaks down here
        # for a general graph, which seems harder).
        extra_dragverts = {} # verts effectively dragged since both their neighbors are dragged
        move_verts = [] # verts moved by the motion of one neighbor dragvert, paired with a direction along which to constrain their motion
        for v in allverts: # .keys() but works ok, since these sets are v->v maps
            if v not in dragverts:
                dragneighbors = intersection(v.neighbors, dragverts)###IMPLEM intersection, complement if necessary (does py23 have a sets module?)
                assert len(dragneighbors) > 0 # otherwise v should not be in allverts
                if len(dragneighbors) > 1:
                    extra_dragverts[v] = v # just drag these too
                else:
                    otherneighbors = complement(v.neighbors, dragneighbors)
                    assert len(otherneighbors) == 1 # can't handle general graphs #e not yet not bothering to handle free ends (easy to fix)
                    v0 = otherneighbors[0]
                    direction = UnitVector(v-v0)
                    move_verts.append( (v, direction) )
                pass
            continue
        dragverts.update(extra_dragverts)
        # now all affected verts are in one of dragverts or move_verts.
        self.dragverts = dragverts
        self.move_verts = move_verts
    def motion_func(self, delta): ##e rename -- something in the Draggable or DragCommand interface
        for v,unit in move_verts: # just project delta onto the line from v0 to v (in direction of unit)
            wrong:
                motion = dot(delta,unit) * unit ###WRONG -- we need to divide by dot, or something like that
                    # to be correct:
                    # the actual motion, projected onto unit, should equal delta, projected onto unit. length-of-motion == dot(delta,unit) -- STILL WRONG!
                    #### to correct this, use corner_analyzer below, which we ought to memoize for v/dv during the transclose
            v.pos += motion
        # the dragverts move independently, so it doesn't matter what other verts we moved already, among them or others
        for v in dragverts:
            v.pos += delta
        return
    ###e add something to help the UI visually indicate which verts are moved in different ways -- there are 4 kinds here:
    # original dragged verts, added due to angle 180, added due to both neighbors dragged, induced motion since one neighbor dragged.
    # We want to create a visible object on each, with one of 4 looks (but the first is not needed since they'll probably be the selected verts).
    # All we need is 3 new attrs which define these sets during the motion, and some default looks for them, and our own default look made of those --
    # the look of a drag command is whatever extra stuff you should draw when doing it (or considering it, maybe -- maybe that's a separate look
    #  so it can be turned off by default).
    #
    ###e BTW we might also want to take over defining the look of the stuff we're moving (as an optional feature of the DragCommand interface) --
    # not so much to make it look different (tho that might be useful) as to implem the optim of having the moving and fixed stuff in different
    # display lists! in fact, we want different ones for fixed stuff, moving-with-mouse stuff, and each other indep motion set -- assume each vert
    # in move_verts is indep, so just put all of them into a displist we remake all the time (or not in any displist at all -- probably that's better),
    # but the ones that move together should be in a single displist which moves as a unit, and which won't need to be remade during the drag!
    #   This requires somehow pulling our v's (and all their edges, and any other stuff attached to them) out of the "main displist for v's".
    # (And sorting it into those categories of motion -- surely this requires new general additions to some interface they're all part of ##e).
    # It also requires *not* moving them by v.pos += delta, but by redefining v.pos to be relative, then moving the collection.
    # [later Q: can any .pos implicitly have associated attrs "which coordsystem" and a related one "which displist" or "which displist-variation"?]
    #   One possible trick for part of that -- introduce a temporary state variable "in-drag" in which things with a certain attr are not visible
    # in the normal way -- that'll be things moving due to the drag.
    # And make normal displists have variants for when the app is in that mode and any of their own elements are being dragged.
    # (Details not entirely clear.)
    pass

# for comparison: drag verts while other verts unchanged (should be simpler!)

class drag_verts(DragCommand):
    verts = Arg(ListOf(Vertex))
    def motion_func(self, delta):
        for v in self.verts:
            v.pos += delta
        return
    pass

class _use_ExprsMeta(object): #e refile, if not already there under another name
    __metaclass__ = ExprsMeta
    pass

def other_of_pair(lis, thing):
    a,b = lis # error if wrong length
    if thing == a:
        return b
    assert thing == b
    return a

class corner_analyzer(_use_ExprsMeta):  ###e nim: handle UnitVector(0) ie v == dv or v == v0  ###CALL ME
    """Figure out how to propogate vertex-drag of dv (with all edge directions unchanged)
    into an adjacent vertex v, based on local geometry of v's "corner"
    (i.e. positions of 3 adjacent vertices dv, v, v0).
       Assume without checking that dv will be directly dragged, but v and v0 won't be,
    meaning that v will have induced partial motion and v0 will remain fixed.
    It's up to the caller to determine whether this is actually true
    and ignore our analysis if not (and this happens in practice in our current uses).
    """
    def __init__(self, v0, v, dv):
        """we're the corner from v0 to v to dv (or the same 3 verts in reverse order),
        where dv is a dragvert and v has induced motion and v0 is fixed and all edge-directions are fixed
        """
        self.vars = (v0, v, dv)
    def motion_of_v(self, delta):
        """if dv moves by delta (a vector), how much (as a vector) should v move by?
        [Note: this will be asked for at every drag-step (so it should be fast).]
        """
        return self.unit * dot(self.control, delta)
    # the following compute methods are run at most once per self
    def _C_unit(self):
        "compute self.unit, a unit vector in the direction in which v should move"
        v0, v, dv = self.vars
        return UnitVector(v-v0)
    def _C_control(self):
        "compute self.control, a vector whose dot product with delta determines the desired signed distance of motion, or V(0,0,0) if it's too sensitive to work"
        # this vector should have the direction of unit projected perp to the dir of null motion, but inverted length
        v0, v, dv = self.vars
        unit = self.unit
        nullunit = UnitVector(dv-v) # a direction of no induced motion of v
        control_dir = unit - nullunit * dot(unit, nullunit) # perp to nullunit; shorter if induced motion is more sensitive
        inverse_sensitivity = vlen(control_dir)
        if inverse_sensitivity < 0.01: # guess
            return V(0,0,0) # wrong, but the right answer is an excessively long vector for excessively sensitive motion (infinitely so, if points are colinear)
        control_dir /= inverse_sensitivity # now it's unit length
        return control_dir / inverse_sensitivity # now it's longer when motion should be more sensitive
    pass
