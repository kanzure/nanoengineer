# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
scratch6.py

$Id$
"""

# [061025; exploring a graph-editing eg, gets into interesting comments about
# exprs for behaviors, actions, events, potential & actual, command offers,
# and pattern syntax and semantics.]

# you can DND a new edge from one node to another
# using the following behavior, which we might add to some editmodes and not others...

# let's see, what does it say:
# - appearance of the during-drag graphic:
#   (a rubberband edge from an existing node to an object showing what would happen if you dropped at that point)
# - dragging thingy, which looks under it to see what it might drop on, looking for:
#   - something that edges (of its kind) from nodes (of its kind) can be attached to
#   - empty space into which new edges (of its kind) can be drawn (creating new nodes to attach to)
# specifically, in either case (existing or new droptarget), it somehow highlights & has translucent stuff to show what it'd do.
# we're likely to like to do that by:
# - creating a first class feature or object, which is what we'd make real if we dropped
# - but until we drop, "show it as a potential feature or object"
#   - for which standard behavior can be used:
#     - potential object is shown translucent
#     - potential feature (attachment to target) is shown by highlighting target...
#   but in reality, the highlighting of the target is more like a special case for DND.
#   OTOH, when target is space, we highlight the drop point, not the target, based on what we'll do there.

# so it sounds like these potential actions (putting action and appearance when potential into one thing) do exist,
# but might be specialized for this DND-like use.
# That's ok, they're useful even if always custom --
# they can have statustext, help info, history info, name & accel key, cmdline equivalent, etc, too.
# They are pretty much like a command with some standard type & args (some args symbolic or from env).

# potential actions for use while DNDing an edge, relative to the edge itself:
AttachTo(target)
AttachToNew(space, position, what)

edge.AttachTo(target)
    # action is about an edge, thus it's "edge.something"
    # capital A is standard for command names, which are special case of type names (command == type of action)
    # - the above is still something like a widget expr, since we can instantiate it as a way of actually doing the action!
    # - but there is a related expr, maybe a param of that one(??) (or of an instance of it, even if it isn't done yet)
    #   which shows the potential of doing it, and has the mentioned metainfo about that.

# Q: do we instantiate the action as soon as it's a specific potential action, or only when we do it?
# A: when it's a specific potential action.
#   Proof 1: if history mentions the potential action (eg it's shown like this at this time),
#    and then we do it, and history mentions that, they need tying together;
#    both being same instance (at different lifecycle stages) is the simplest way.
#   Proof 2: if each action instance has a random color or whatever,
#    we might want to show this in the appearance of the potential action.

# That means we instantiate all the potential actions we show (e.g. as menu items, or translucent alternatives for deposit).
# Note that if we do something, unrelated potential actions now have new starting conditions and might look different;
# sometimes they'd need to become new instances (if the process of making them used something that just changed).

# does that mean that edge.AttachTo(target) is already instantiated? Hmm... edge is, and target is... OTOH,
# I could imagine passing it into something which decides whether to instantiate it... so I guess it's not.
# e.g.

action1 = If(cond, edge.AttachTo(target1), edge.AttachTo(target2))

# note: the thing doing the action could be symbolic:
_thing.AttachTo(target)

# Q: is that the same as this??
AttachTo(target)
# I don't know. [Guess: yes, if we wanted it (or something like it) to be the same as this, when we designed AttachTo.] ####
# Related Q: do some exprheads autocurry, so that Sym(x1) is the same as Sym(x1, _somespecificsymbol), or perhaps more analogously,
# the same as lambda x: Sym(x1,x)?? ####
# (Digr: the latter need not be expanded on each use -- it can be expanded on a symbol, and the resulting expr lexreplaced on each use.
#  And the arg/kw signature (len args, keys of kws) to use can be determined at runtime, the first time each signature is used.
#  These ideas are mostly mentioned previously in recent notesfiles or papers.)

# Now how might we use some of these potential-action exprs?

# - instantiate some of them, bound to possible user actions (like drop under certain conds (eg on what, in where) with certain modkeys),
#   these are still potential since the user actions (events) are possible rather than actual.
# - these have looks -- draw some of them, maybe all the ones in some set that we also "bind to reality", ie to a source of a real event.
# - the fact that they're bound to that event-source which has a present potential existence (the drag before the drop,
#   or the menu before the menuitem selection) does two things at once, which we like to have tied together:
#   - display the appearance of the potential action (which can now depend on which potential events it's tied to -- it's a bound action)
#   - enable this action as the real one to happen, if that possible event happens.
# Note: binding the potential action to a possible event constitutes offering the action. This is visible, and it's a real offer.
# So "real offers should be visible" -- this is why those two things should be tied together.

# so we have: potential action, as expr or instance, bound to possible event (ortho to whether it's expr or instance afterwards, i think ###),
# which if bound to an instance of a possible event is offered to whatever might do that event.

# a possible event expr:
ControlDropOn(Node) # how do we say Node is the type of _target?? (do we??)
# a potential action expr:
AttachTo # edge. ?  (target)?

# map from possible events to their actions
# (the word "potential" is often implicit; that's ok since it's really a matter of how the action relates to other things)
{ ControlDropOn(Node) : edge.AttachTo } # this assumes Node is the type of "the arg" and edge.AttachTo is a method to apply to "the arg"

edge.AttachTo # a reasonable "bound method"

ControlDropOn(Node) # a bit weird, since ControlDropOn(thing) (for thing perhaps being of type Node) might be an instance of this type,
# so it's as if we had a pattern language in which any term in an expr can be replaced by a type for that term...
# but this leaves a lot of things implicit unless types and ordinary terms are always distinguishable,
# which seems unlikely if types are firstclass.

# So don't we want to say
ControlDropOn(_:Node) # or the like?
# (digr: i bet that syntax could actually work, if we can use Slice as a pattern-forming operator.
#  Whether it *should* work is another matter... no idea. ###)

# hmm -- we might rather say AnythingOfType(Node) rather than <thing that looks like a lexvar of a specific name, even _> of type Node.
# Then we can say that AnythingOfType is a special kind of pattern-forming exprhead, one of a few things treated specially in patterns.

# OTOH maybe ControlDropOn is able, when used as a pattern, to coerce its arg1 into a type?? Which Node already is...
# or even easier, detect that it's a type (of things you can drop on)? After all, a type is an individual, but it isn't
# an individual in the class "things you can drop on" which is what ControlDropOn(arg1) wants in arg1 to be an event.
# So maybe Exrphead(arg1, arg2) with full typedecls for the args has no problem detecting typelike args, re those types,
# and treating them as patterns? I guess there could be problems created by finding recursive types of themselves in lambda calc...
# surely we needn't worry about that in making a heuristic be ANAP? (As Nice As Possible) ####

# Conclusion: I think ControlDropOn(Node) can work if I want it to, when designing ControlDropOn.

