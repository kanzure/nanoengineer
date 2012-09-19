# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
Command_scratch_1.py

$Id$

[061212 is the date of some small mods to make this parse -- probably it was mostly written
then or a few days before, within demo_drag.py]


070105 moved the pseudocode for Command & DragCommand class etc from demo_drag.py
into this new file Command_scratch_1.py --
see this file for ideas about Command, DragCommand, _PERMIT_SETS_INSIDE_, DragANode, ClickDragCommand, MakeANode.
(But some comments in demo_drag.py still discuss Command and MakeANode in important ways. ####e)
"""

from basic import *
from basic import _self, _this, _my


Alias = mousepos = Vertex = Stub


class Command(InstanceMacro): #k super is prob wrong
    """#doc
    a subclass can make exprs that are specific available commands:
    - when they get args they know their param-formulas relative to event sources they're bound to
    - when instantiated, they are a potential real command, all decisions made, offerable (eg in a context menu)
    - some further protocol (not yet designed, but controlled by the event source)
      decides to start doing them, binding them to a real event (perhaps a long-running one like drag,
        or an even longer one if they are wizard-like commands that take over a window for awhile, with lots of mode like variables,
        lots of controls, etc -- in that case the "event" is just "all user events to this subwindow while this wizard is active"
        or "all user events controlled by this wizard" -- they're like a mode, in the old NE1)
      and letting them control what's shown (graphics area, in their own optional separate panes, etc),
      and what is left (as their side effect, changed or created stuff) at the end.
    """
    pass

class DragCommand(Command):
    """Commands that are bound to (give behavior/action to) a single drag-event
    (starting when the user-event-processing-system decides it's a real drag (not just a click),
    ending when the mouse goes up and the resulting intended effect (if any) can be done by this command).
    """
    pass

_PERMIT_SETS_INSIDE_ = attrholder # temporary kluge

class DragANode(DragCommand):
    """this runs on a new Vertex made by the click which started this drag (assumed made before this drag starts)
    [whether we can or should really separate click and drag actions like that, in this example, is not clear ###k]
    [but if we can, then this *same* command can also drag an *old* node, which would be nice, if we rename it. #e]
    [I think we can sep them, by noticing that the node-maker on click can then decide what to do with "the rest of its drag". #k
     In fact, I bet it will continue to exist as an ongoing command, delegating its remaining user-event stream to the subcommand
     it selects for handling that "rest". #k]
    """
    # the new Vertex is an Arg, I guess. How does caller know its name? or is it always arg1?
    node = Arg(Vertex)
    # it has a position which we will drag.
    # This is really its posn in a specific space... for now assume it (or our view of it, anyway)
    # owns that pos and knows that space.
    pos = Alias( node.pos) # Alias is so we can set or change pos as a way of changing node.pos [#nim, & not even fully decided on]

        # [later 070111: note that in real life, pos should be a *translated* form of node.pos, but still be settable as an lval.
        #  in general we'll want to transform the settable for drag parts of node, to those of a drag-target with a uniform
        #  interface, then let the mouse drag events modify the drag-target in a standard way. See '070111 settable coordinate vars'
        #  [not in cvs] for related discussion.]

    # Q: if system decides it's a drag only after it moves a little bit, does the object then jump, or start smoothly,
    # as it starts to move?
    # A: what does NE1 do? what do I prefer? should it be a user pref? If so, can this code not even know about it somehow?
    # What would make this code simplest?
    # Does this code need a dragpoint on the new object (perhaps with a depth)? Does it need a drag-delta instead? (At what depth?)
    # Can this code work w/o change if someone hooks up a 3d drag device? (Meaning, it accepts a 3d drag path, for now always planar.)

    # ok, now it's time to specify our effect, which is basically, set node pos to mouse pos. How simple can it be, in that case?

    ## pos = mousepos # won't work, since erases above other set of pos in the class namespace.

    node.pos = mousepos # won't work -- syntax error [predicted] .. wait, turns out it's not one!!!
        # But what does it do? It ought to be doing setattr on an expr returned by Arg(Vertex) -- which does what?
        # Oh, just sets the attr in there, silently! Can we capture it? If the attrname is arbitrary (seems likely, not certain),
        # then only with expensive code (on all symbolic exprs?) to notice all sets of attrs not starting with _e_ etc...
        # (hmm, maybe we don't need to notice them except later? that is, it's just a formula sitting inside the value of node,
        #  created by Arg just for us after all, which we can notice from dir(node) since the attrname doesn't start _e_??
        # As experiment just try printing them all. But first keep deciding if we want this syntax, since it's kind of weird.
        # E.g. it implies we do this continuously, *all the time* that this instance exists [wrong, see below] --
        # which might be what we want... hmm.
        # It also naturally only lets us assign a specific thing as one formula... at least at the whole-class level. Hmm.

        # actually it doesn't have to mean we do the action continuously. The formulas could get grabbed and stored,
        # for whole class or per-symbol or per-symbol.attr.attr (or all of those), and then done by a specific method call,
        # either once at the end or continuosly, and in various "modes of doing them" like accept or offer or reject/cancel...
        # this would let us set up the side effects, then do them tentatively during the command, do them fully after it,
        # or reject/cancel them in an automatic way using a single call (doing right thing re history, undo, etc).
        # If the command-end method didn't exist, the standard super one could just accept the changes
        # (and same with setting up to tentatively accept them during the command, showing that in std ways).
        #
        # BTW the way tentativeness can be shown is to store metainfo with the attr-set side effects
        # (eg obj._tentativeness_of_attr = True # (paraphrased)), then for display styles to notice that and let it affect them,
        # maybe noticing it automatically for all attrs they use -- i.e. "or" some caveat-flags (incl warnings, uncertainties...)
        # as you usage-track so you'll know what caveats apply to some value you compute. (Or actually use them, in case they change.
        # I guess only use them for a parallel computation of your own caveats.)

    print_node_mod_demo = False # 061212
    # print_node_mod_demo = True # 070130 - works, disabling again for now

    if print_node_mod_demo:
        print "our node symexpr has:",node._e_dir_added()
##    for attr in dir(node):
##        if attr.startswith('_e_') or attr.startswith('__'):
##            pass
##        else:
##            print attr, # _init_e_serno_ [fixed?], pos
##        continue
##    print

    node.pos.subattr = 1
    node.pos2 = _PERMIT_SETS_INSIDE_()
    node.pos2.subattr2 = 1

    if print_node_mod_demo:
        print "now it has:",node._e_dir_added() ###BUG [before i had _PERMIT_SETS_INSIDE_() above] - where is pos2?
    #print "dir is",dir(node) # it's not in here either! OH, I never made it, I only asked for it (for val of node.pos2)
     # and I got a getattr_Expr of node and pos2! Can that be fixed? As it is I can't even see that getattr_Expr,
     # it was discarded. Can/should I capture the setattr of attr in symbolic getattr_Expr? Guess: probably I can. ###k
     # (Alternatively I could capture the making of the getattr_Expr on a symbolic expr,
     #  and do something equiv to the set to _PERMIT_SETS_INSIDE_() above -- this might make basic sense...
     #  but it would only work if I didn't return the getattr_Expr itself, but whatever object I stored for it!
     #  But wait, why not just store that same getattr_Expr, so it's memoized (might save mem or help in other ways)? Hmm..
     #  note that the exact cond for doing this being ok is not _e_is_symbolic but something inherited from arg1 of some OpExprs...
     #  ###k
     #
     #  [digr: it might even have other uses, like a convenient record of how we use each symbol,
     #   which can be checked against its type later on,
     #   or checked against specific values passed in, or used in other ways....])
     #
     # [Then I could also warn if i thought it might be discarded -- if the set fails to know it "tells something it was done".]
     ####e First decide if i want to. My tentative guess is yes, but the idea is too new to be sure.
     # But I could test the idea without that, just by requiring kluge workaround of a set of node.pos2 to a special value; try above.

    node.blorg = node.blorg + 1 # hopefully this will set it to a OpExpr of a getattr_Expr, equiv to the expr node.blorg + 1

    if print_node_mod_demo:
        print "and now it has:",node._e_dir_added()
        print "node.blorg is now",node.blorg # it does!
    ####
    pass # end of class DragANode

ClickDragCommand = DragCommand # STUB
    #e the idea is, ClickDragCommand includes initial click, whereas DragCommand only starts when real drag is recognized
    # (later: we might decide to drop the type-distinction between ClickDragCommand and DragCommand,
    #  for economy in set of concepts, trading it off for making the common DragCommand more complex or ambiguous
    #  since it may or may not include the initial click -- but it has to be given enough info as if it did.)

class MakeANode(ClickDragCommand): #k super?
    #e will be bound to empty space, or guide surfaces/objects you can make nodes on
    # (but might want them as arg, to attach to -- hmm, not only the surface, but the space!
    #  same arg? -- what it's a feature of or on? or, feature of and feature on might both be space, or might be space and obj??
    #  related: what its saved pos is relative to. ####e decide that...)
    """
    """
    # hmm, they clicked, at some pos, and we know a kind of node to make... let's make it
    newnodepos = V_expr(0,0,0) #stub
    newnodepos = _self.pos # what other kind of pos can we have? well, we could have the continuously updated mousepos...
    newnodepos = _self.clickpos #e rename; note we have dragstart_posn or so in other files

    newnode = Vertex(newnodepos, 'some params')
        ###PROBLEM: is that just an Expr (pure expr, not instance, not more symbolic than IorE) assigned to an attr?
        # is it symbolic enough to let us do newnode.pos = whatever later if we want?
        # see cmt below about how to list it as "_what_we_make".

    # (typically some params would be formulas)

        # - do those params say where in space, relative to mousepos? yes, they must, since it can vary for other commands,
        #   eg if it's built on top of something that exists (see above comment about attaching to an obj, too).

    # now we want to say:

    # - where to put it -- i mean, what collection to assign it to

    # - now permit it to be dragged (or in other kinds of commands, permit some aspect of it to be dragged)
    #   - maybe with some params of the node -- or of this command (temporary params not in the node itself) --
    #     being controlled during the drag
    #   by letting this event be taken over (after its side effects, maybe before its own wrapups) by another command

    #   but binding that other command to the event that a real drag starts -- HOW? ###e

    ## _value_if_a_real_drag_starts___is_made_from_this_expr = DragANode # ___is_made_from_this_expr should be implicit

        #e DragANode with what args? self? self.newnode? might need self if it needs to change the look based on self...
        # otoh it has access to the drag event, so maybe that would be rare...
        # except that self is probably controlling "tentativity". hmm.... ###k

        #e revise to look like a bunch of subevents bound to actions/behaviors (commands), when we know what that looks like
        # tho this special case might be common enough to have its own name, shorter than this one, e.g. _continue_drag

    _value_if_a_real_drag_starts = DragANode( newnode)

        # defect: this requires us to define DragANode first in the file; if a problem, replace it with _forward.DragANode or so

    if 0:
        # I disabled this 061212 to avoid the warning which in real life would be suppressed for this special case:
        ## warning: formula <Vertex#8661(a)> already in replacements -- error?? its rhs is
        ## <getattr_Expr#8669: (S._self, <constant_Expr#8668: '_what_we_make'>)>; new rhs would be for attr 'newnode'
        _what_we_make = newnode # maybe we'll just name newnode so this is obvious...
            # btw this can be an exception to not allowing two attrs = one expr, since _what_we_make is a special name... so ignore this:
                ## warning: formula <Widget2D#12737(a)> already in replacements -- error??
                ## its rhs is <getattr_Expr#12741: (S._self, <constant_Expr#12740: '_what_we_make'>)>;
                ## new rhs would be for attr 'newnode'
            # should we make its specialness obvious (for it and _value and _continue_drag and all other special names)??
            # I mean by a common prefix or so. BTW are they all different kinds of "values" or "results"? Could use _V_ or _v_ or _r_...
            # ####e decide

    # an alternate way to say what we make, and to say where: some sort of side effect formula... maybe worse re POLS.
    if 0:
        _something.make(newnode)
        _something.add(newnode)
        _self.something.make(newnode)
        make(newnode)
        # etc

    pass # end of class MakeANode
