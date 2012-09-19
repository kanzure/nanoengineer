# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
demo_drag_2_scratch.py

$Id$

scratch file about how to rewrite demo_drag in a higher level way
"""

Vertex = DataType("Vertex",
                  Arg("pos", Position), # relative to what?
                  Option("guide", ModelObject)
         )
   # this is not a correct set of attrs


DataType(pos = Arg(Position))(guide = Option(ModelObject)) # nah

DataType( lambda pos = Arg(Position), guide = Option(ModelObject): 0 ) # has the data and syntax, but looks too weird and non-POLS --
    # but maybe it wouldn't if we *used* the symbols -- replace 0 with a bunch of further decls about those symbols,
    # like the change-order-policies discussed 1 screen below

DataType("Vertex",
         "pos", Arg(Position),
         "guide", Option(ModelObject),
        ) # surprisingly tolerable. hmm.

# define IntrinsicVertex as extended/subtype of Vertex, with more data and ways to see it as Vertex

IntrinsicVertex = Vertex(pos = RelativePos(_params.lpos, <coordsys>), <other customization>)

# Create command, using a formula-customized subtype of IntrinsicVertex as the type to create

Create(IntrinsicVertex(lpos = <formula>, guide = <formula>, policy = <formula>)(<data args, opts>))

## Move( some_vertex, from = pos1, to = pos2) # typical Move command
  # [unless from or to is py keyword -- rats, 'from' is! Ok, change it:]

Move( some_vertex, _from = pos1, to = pos2)
#or
Move( some_vertex, from_pos = pos1, to_pos = pos2)  # also allow from_lpos, to_lpos




# == simplest that could work:

Vertex = DataType("Vertex",
                  "pos", Arg(Position))

Vertex = DataType(
    "pos", Arg(Position))

IntrinsicVertex = ...
    we want to say that pos is a formula of lpos and some coords
    ( a reversible formula -- lpos can be set by setting pos -- due to coords or the coord-combining-op supporting that)
    and the obj that supplies the coords is an arg
    and a policy option says whether we grab a snapshot of those coords from that obj, or continuously regrab them, as obj moves
    (but even in first case a cmenu item would let us regrab them -- so it still knows the obj)
    (but it does have its own copy of the coords, I guess -- and the precise type of those depends on the nature of the obj)

    note: coords is correct but don't be fooled -- it's a semiarb map from some coords to others -- not an affine map!
    so for a point on a sphere, the intrinsic coords are a surface point on unit sphere and a radius ratio...
    or a radius offset if you prefer -- different types.

    what does the eg look like, for a radius ratio, with a policy option for autoupdate or just update?

    coords = formula(guideshape), update = True or False

    pos = coords(lpos) # reversible -- how do we say so?

    pos = Reversible(coords(lpos)) #??
    pos = Alias(coords(lpos)) #??
    pos = Lvalue(coords(lpos)) #??
    pos = Settable(coords(lpos)) #??

    # or just let it be implied by the expr coords(lpos) due to the lexically declared type of coords? (sounds too hard for now)
    # or have a separate list of things you can set, to change other things, which says you can set pos to change lpos?
    # (a list of different ways to change it, each having a list in priority order of things to keep fixed or set as requested;
    #  in this case the list would say, supply pos, fix coords, derive lpos, I guess...
    # or that you can derive lpos from pos?

    # goal: know what can be specified, to get what -- and how to do this (at least, what to ask to do it, ie coords)

    # does it relate to what data's type needs to know the code to do it? ie it's not just lpos + coords = pos, solved for lpos --
    # the knowledge of how is *in coords*, not in some outer + operation. So it's really that coords gets pos from lpos, reversibly.
    # It's like an optional attr of the formula, or even of the expr coords(lpos).

class GuideShapeVertex(Vertex):
    # (this class form makes it easier to see the symbols and use them in subsequent exprs -- even lambda can't let me use them in
    #  the very next decl -- i'd need nested lambdas for that -- or my own expr syntax parser, of course)
    guide = Option(GuideShape, "the guide shape used to position the vertex") #e digr: ok place for a docstring, in this syntax?
    if 0:
        # problem: depends on knowing that a string is not the default GuideShape! eg this is not good:
        textmsg = Option(str, "message for statusbar") # unless this is then *both* the default and docstring... very silly but possible --
            # has some UI advantages (in a parameter dialog), believe it or not! But too silly to take seriously.
        # fix that:
        textmsg = Option(str, <dflt>, "message for statusbar")
        textmsg = Option(str, doc = "message for statusbar")
        # but seriously, we might permit it if you *do* know that strings can't belong to the type. Not sure.
        # Not great if source code changes meaning if someone adds a way to coerce strings into that type! So nevermind.
    # coords = guide.coords -- Decl about whether snapshotted or updated --
    coords_update = Option(bool, False, "whether to continuously update the lpos coordsys (and thus pos) from motion of the guide shape")
    coords = StateSnapshot(guide.coords, update = coords_update,
                           doc = "intrinsic coordsys for lpos (can map it to abs pos)")
        # or capitalize guide.Coords since it's a type, in a sense? not sure. it's also or more a func...
        # why is this not just a formula? because update might be false. But if it's true? because guide shape might *lose* its coords,
        # e.g. if it disappears entirely (gets deleted from model);
        # then the update fails, but this does not lose the coords! it's just a warning (about the data object -- maybe not even
        # seen except on demand, ie really info not warning), and they are still locally there & useable. So it's State for sure.
        # OTOH it's not settable except by taking a snapshot of the declared formula, I guess... not sure if that's essential.
        # I wonder if we should even declare it like this:
    if 0:
        coords = State(guide.Coords)
        coords.value = ... # no, too confusing, it's coords as a whole that we're setting...
    lpos = StateArg(coords.Position, "intrinsic coords -- i.e. local pos")
        #k and coords.Position is a type which is an aspect of that "func" coords
        # (which is more than just a func, tho "callable" in Expr sense, i.e. coords(x) is an Expr)
    pos = coords(lpos, reversible = True, doc = "absolute position, derived from lpos via coords; can be set to adjust lpos")
    pass

# to summarize and fix that, rename some things for clarity, etc:

class GuideShapeVertex(Vertex):
    "#doc"
    guide = Option(GuideShape, doc = "the guide shape used to position the vertex")
    coordsys_update = Option(bool, False, "whether to continuously update the lpos coordsys (and thus pos) from motion of the guide shape")
    coordsys = Snapshot(guide.coordsys, update = coordsys_update, #e rename update -> continuous? auto? always? #e just Snapshot?
                           doc = "intrinsic coordsys for lpos (used to map it to abs pos)")
    lpos = StateArg(coordsys.Position, "intrinsic coords -- i.e. local pos")
    pos = coordsys(lpos, reversible = True, doc = "absolute position, derived from lpos via coordsys; can be set to adjust lpos")
    pass

# do we need to declare that outsiders can set .pos, not just internal code? Or is not naming it _x or listing it as private enough?

# given the above, what constructors can we use?

GuideShapeVertex(lpos, guide = guide1)

# custom type:
myVert = GuideShapeVertex(coordsys_update = True)
def makeone(): # wrong use of Create as executable function!
    Create( myVert(lpos1) )
    Create( myVert(pos = pos1) ) # dubious -- the idea is, pos is not an option, so using it as one must mean setting it in constructor...

    # btw are we going to let people in general use Args (with known names, as they always have) as Options? at least for customization? #e
    # when that happens, are they removed from the remaining arglist?
