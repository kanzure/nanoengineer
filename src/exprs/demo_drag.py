"""
demo_drag.py

$Id$

demo not only some drag actions, but some ways of setting up new model types
and their edit tools and behaviors. [Eventually.]

[for current status see comments just before GraphDrawDemo_FixedToolOnArg1]

070105 moved the pseudocode for Command & DragCommand class etc into new file Command_scratch_1.py --
see it for ideas about Command, DragCommand, _PERMIT_SETS_INSIDE_, DragANode, ClickDragCommand, MakeANode.
(But some comments below still discuss Command and MakeANode in important ways.)
"""

from basic import *
from basic import _self, _this, _my


import Overlay
reload_once(Overlay)
from Overlay import Overlay

import transforms
reload_once(transforms)
from transforms import Translate

import Rect
reload_once(Rect)
from Rect import Rect ##, Sphere

import Center
reload_once(Center)
from Center import Center, CenterY

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable ##, Button, print_Expr

import draw_utils
reload_once(draw_utils)
from draw_utils import DZ ##e move DZ etc to basic?? not yet, they might need rethought.

import TextRect
reload_once(TextRect)
from TextRect import TextRect

import controls
reload_once(controls)
from controls import checkbox_pref, ActionButton

import Column
reload_once(Column)
from Column import Column, SimpleColumn, SimpleRow # only using SimpleRow

import DisplistChunk # works 070103, with important caveats re Highlightable
reload_once(DisplistChunk)
from DisplistChunk import DisplistChunk

import lvals
reload_once(lvals)
from lvals import Lval, LvalDict2, call_but_discard_tracked_usage

# == trivial prototype of central cache of viewers for objects -- copied/modified from demo_MT.py, 070105, not yet used, stub

def _make_viewer_for_object(obj, essential_data):
    ###stub
    assert obj.__class__.__name__.endswith("Vertex")
    return VertexView(obj)

    # semiobs cmt (del or refile a bit below #e):
    # args are (object, essential-data) where data diffs should prevent sharing of an existing viewer
    # (this scheme means we'd find an existing but not now drawn viewer... but we only have one place to draw one at a time,
    #  so that won't come up as a problem for now.)
    # (this is reminiscent of the Qt3MT node -> TreeItem map...
    #  will it have similar problems? I doubt it, except a memory leak at first, solvable someday by a weak-key node,
    #  and a two-level dict, key1 = weak node, key2 = essentialdata.)

def _make_viewer_for_object_using_key(key):
    """[private, for use in a MemoDict or LvalDict2]
    #doc
    key is whatever should determine how to make the viewer and be used as the key for the dict of cached viewers
    so it includes whatever matters in picking which obj to make/cache/return
    but *not* things that determine current viewer
    but in which changes should invalidate and replace cached viewers.
    """
    obj, essential_data, reload_counter = key ###k assume key has this form
    print "make viewer for obj %r, reload_counter = %r" % (obj, reload_counter) ###
    # obj is any model object
    viewer = _make_viewer_for_object(obj)
    return viewer

_viewer_lvaldict = LvalDict2( _make_viewer_for_object_using_key )

def _viewer_for_object(obj, essential_data = None): #####@@@@@ CALL ME
    "Find or make a viewer for the given model object. Essential data is hashable data which should alter which viewer to find. ###k??"
    from testdraw import vv
    reload_counter = vv.reload_counter # this is so we clear this cache on reload (even if this module is not reloaded)
    # assume essential_data is already hashable (eg not dict but sorted items of one)
    key = (obj, essential_data, reload_counter)
    lval = _viewer_lvaldict[ key ]
    viewer = lval.get_value() ###k?
    return viewer

# ==

class ModelObject(InstanceOrExpr,DelegatingMixin): # stub ##e will we need Widget2D for some reason?
    """#doc
    """
    pass

class Vertex(ModelObject): # renamed Node -> Vertex, to avoid confusion (tho it added some too, since localvars not all changed,
      # and since the world ought to contain model objs anyway, in general, of which Vertex is only one type, and current implem
      # also has its own graphics code)...
    # see below about better ways to rename it...
    """It has a position, initializable from arg1 but also settable as state under name pos, and an arb appearance.
    Position is relative to whatever coords it's drawn in.
    """
    ###e about what to rename it... Hmm, is it a general "Draggable"? .lookslike arg2 -> .islike or .thing arg1?
    
    # BTW, the highlightability is not yet specified here ###nim; it relates to the fact that we can bind commands to it
    # (as opposed to things it contains or is contained in, tho that should be permitted at the same time,
    #  tho implem requires nested glnames to sometimes ignore inner ones, when those are inactive);
    # but we might add it in a wrapper which makes it into a view of it that lets commands be bound to it,
    # except that World.draw assumes we draw the actual model objs, not wraps of them - also an issue if env says they
    # look different -- so maybe World needs to wrap all it draws with glue to add looks and behavior to it, in fact.

    # but for now, can we do this here?
    
    pos0 = Arg(Position)
    pos = State(Position, pos0) ###BUG -- does this work -- is pos0 set in time for this? not sure it's working... 061205 1009p
    #e we probably want to combine pos0/pos into one ArgState or StateArg so it's obvious how they relate,
    # and only one gets saved in file, and only one self.attr name is used up and accessible

    # the rest of this class is for drawing it and interacting with it.
    # Can we move that code into e.g. VertexDrawable or VertexView
    # and have Vertex itself just delegate (for sake of draw, lbox, etc) to some rule in the env for getting a Drawable for it,
    # probably looking it up in a dynamic memoizing mapping in the env? ####e [070105]
    # I think YES.
    # - a main difference between a model & view object -- a view obj knows how to draw itself, a model obj asks the env.
    #   (and the answer is quite different in different envs, e.g. 3d area vs MT. but what if we mix those?)
    # related notes:
    # - it might want a different delegate for drawing purposes (draw, lbox) and sim purposes (or others).
    # - does it also have an attr corresponding to its index/address/id in the model world?
    # - and maybe some for relations to other model objs, eg MT-parent, tags, name, etc?
    # - and maybe some graphics prefs like color or whatever, even if it's up to the drawing rule whether/how to use these?
    # - and for that matter some arbitrary other data (named attrs), as we'll let any model object have?
    # simplest thing that could work --
    # - make some sort of MemoDict for model-view and put it into the env, even if we kluge how to set it up for now.
    #   how does demo_MT do it? With a hardcoded helper function using a MemoDict in a simple way -- no involvement of env.
    #   So see above for copied code from that... ###e

    #e so now what we want is for this (in super modelobject) to delegate to a computed viewer from the helper func above

    #e but also to have more args that can be used to set the color [do this only in Vertex_new, below]
    ## color = Option(Color, color)
    
##    pass

## class VertexView(xx): -- SOMETHING LIKE THIS IS THE INTENT ####

    #e and then we want this new class to have the hardcoded appearance & behavior which the code below now passes in lookslike arg
    
    lookslike = ArgOrOption(Anything) # OrOption is so it's customizable
        ###BAD for lookslike to be an attr of the Vertex, at least if this should be a good example of editing a sketch. [070105]
        # (a fancy sketch might have custom point types, but they'd have tags or typenames, with rules to control what they look like)
        
    ## delegate = _self.lookslike #k
    delegate = Highlightable( Translate( lookslike, pos ),
                              ## eval_Expr( call_Expr(lookslike.copy,)( color = yellow) ),  #####?? weird exc don't know why - reload?
                              ## AssertionError: _this failed to find referent for '_this_Vertex'
                              on_drag = _self.on_drag # 070103 kluge experiment, works (eg in _19d)

                              )
                #e actions? or do this in a per-tool wrapper which knows the actions?
                # or, do this here and make the actions delegate to the current tool for the current parent? guess: the latter.
                
        ##e digr: will we want to rename delegate so it's only for appearance? *is it*? does it sim like this too?
        # Guess: it's for everything -- looks, sim qualities, etc -- except what we override or grab from special members.
        # [if so, no need to rename, except to clarify, leaving it general.]
    #e might need something for how to save it in a file, Undo policy, etc

    def on_drag(self): # 070103 kluge experiment, copied/modified from on_drag_bg in bigger class below

        # where i am 070103 447p (one of two places with that comment)
        # - sort of sometimes works, but posns are sometimes same as bg, not sure why that DZ would be needed,
        # oh i guess the mousepos comes from the gray bg rect not the self unless we drag very slow...
        
        point = self.current_event_mousepoint() ### MIGHT BE WRONG COORDS? guess: no
         #k guess: will have snap-to-fixed-point bug for generic drag code
        newpos = point + DZ * PIXELS * 2 # used for different things, depending #### DZ needed but might cause trouble too
        self.pos = newpos
        ## print "in-node action set %r.pos = %r" % (self, newpos) # sometimes works
        self.env.glpane.gl_update() #k needed?
        return

    pass # end of class Vertex

# ==

class ModelObject_new(DelegatingInstanceOrExpr):
    ###e delegate = something from env.viewer_for_model_object(self) or so
    pass
    
class Vertex_new(ModelObject_new): #070105 ###e maybe it also needs an official type or typename for use in rules and files?
    pos0 = Arg(Position)
    pos = State(Position, pos0)
    color = Option(Color, black)
    pass

class Viewer(InstanceOrExpr):
    "superclass for viewers of model objs given as arg1"
    modelobj = Arg(ModelObject_new) #k can subclass refer to this??
    pass

class VertexViewer(DelegatingInstanceOrExpr, Viewer): ###k ok supers?
    
    delegate = Rect(1, color = _self.modelobj.color) ###WRONG details, also assumes _self.modelobj has a color, but some don't.
        ###e do we wrap it in a provider of new default options??
    ###e also needs behaviors...
        
# ==

viewerfunc = identity # stub - might better be that hardcoded helper func above ####e

class WithViewerFunc(DelegatingInstanceOrExpr):#070105 stub experiment for use with use_VertexView option ### NOT YET USED non-stubbily
    world = Arg(Anything)
    viewerfunc = Arg(Anything) ### NOT YET USED in this stub
    delegate = _self.world # stub
    #e what we actually want is to supply a different env to delegate == arg1, which contains a change from parent env,
    # which depends on viewerfunc. We want a standard way to ask env for viewers, and the change should override that way.
    # But we don't yet have a good way to tell this macro to override env for some arg.
    # We probably have some way to do that by overriding some method to find the env to use for an arg...
    # but we didn't, so i made one.
    def env_for_arg(self, index): # 070105 experiment -- for now, it only exists so we can override it in some subclasses
        env = self.env_for_args #e or could use super of this method [better #e]
        if index == 0: #KLUGE that we know index for that arg (world, delegate, arg1)
            env = env.with_lexmods({}) #### something to use viewerfunc
        return env
    pass

# let's try a more primitive, more general version:

class WithEnvMods(DelegatingInstanceOrExpr):#070105 stub experiment -- refile into instance_helpers.py if accepted ### NOT YET USED
    """WithEnvMods(something, var1 = val1, var2 = val2) delegates to something, but with something instantiated
    in a modified dynamic environment compared to self, in which env.var1 is defined by the formula val1, etc,
    with the formulae interpreted as usual in the lexical environment of self (e.g. they can directly contain
    Symbol objects which have bindings in env, or they can reference any symbol biding in env using _env.symbolname ###IMPLEM
    or maybe other notations not yet defined such as _the(classname) ###MAYBE IMPLEM).
    """
    # The goal is to just say things like WithEnvMods(model, viewer_for_object = bla)
    # in order to change env.viewer_for_object, with bla able to refer to the old one by _env.viewer_for_object, I guess.
    # This assumes env.viewer_for_object is by convention a function used by ModelObjects to get their views. (Why "viewer" not "view"?)
    delegate = Arg(Anything)
    var1 = Option(Anything) ###WRONG, but shows the idea for now...
    def env_for_arg(self, index):
        env = self.env # note: not self.env_for_args, since we'd rather not lexically bind _my.
            # But by convention that means we need a new lowercase name... ####e
        if index == 0: #KLUGE that we know index for that arg (delegate, arg1)
            mods = {} ###stub, WRONG
                #### how do we make these mods? _e_kws tells which, but what env/ipath for the formulae?
                # for that matter do we eval them all now, or (somehow) wait and see if env clients use them?
                # ... would it be easier if this was an OpExpr rather than an InstanceOrExpr?
            env = env.with_lexmods(mods)
        return env
    pass


# ==

# for a quick implem, how does making a new node actually work? Let's assume the instance gets made normally,
# and then a side effect adds it to a list (leaving it the same instance). Ignore issues of "whether it knows its MT-parent" for now.
# We know it won't get modified after made, since the thing that modifies it (the command) is not active and not reused.
# (It might still exist enough to be revivable if we Undoed to the point where it was active, if it was a wizard... that's good!
#  I think that should work fine even if one command makes it, some later ones modify it, etc...)

# so we need a world object whose state contains a list of Vertex objects. And a non-stub Vertex object (see above I hope).

class World(ModelObject):
    nodelist = State(list_Expr, []) # self.nodelist is public for set (self.nodelist = newval), but not for append or other mods
        # since not changetracked -- can it be?###@@@
    def draw(self):
        # draw all the nodes
        # [optim idea 070103 late: have caller put this in a DisplistChunk; will it actually work?
        #  the hope is, yes for animating rotation, with proper inval when nodelist changes. It ought to work! Try it. It works!]
        for node in self.nodelist:
            # print "%r is drawing %r at %r" % (self, node, node.pos) # suspicious: all have same pos ... didn't stay true, nevermind
            node.draw() # this assumes the items in the list track their own posns, which might not make perfect sense;
                # otoh if they didn't we'd probably replace them with container objs for our view of them, which did track their pos;
                # so it doesn't make much difference in our code. we can always have a type "Vertex for us" to coerce them to
                # which if necessary adds the pos which only we see -- we'd want this if one Vertex could be in two Worlds at diff posns.
                # (Which is likely, due to Configuration Management.)
            if 0 and node is self.nodelist[-1]:
                print "drew last node in list, %r, ipath[0] %r, pos %r" % (node, node.ipath[0], node.pos)
        ###e see comment above: "maybe World needs to wrap all it draws with glue to add looks and behavior to it"
        return
    def _cmd_Clear(self): #070106 experimental naming convention for a "cmd method" -- a command on this object (requiring no args/opts, by default)
        if self.nodelist:
            # avoid gratuitous change-track by only doing it if it does something (see also _cmd_Clear_nontrivial)
            # NOTE: this cond is probably not needed, since (IIRC) LvalForState only invalidates if a same_vals comparison fails. ###k
            self.nodelist = []
        return
    # related formulae for that command
    # (names are related by convention, only used in this file, so far; prototype for wider convention, but not yet well thought through)
    _cmd_Clear_nontrivial = not_Expr( not_Expr( nodelist)) #KLUGE: need a more direct boolean coercion (not that it's really needed at all)
        # can be used to enable (vs disable) a button or menu item for this command on this object
    _cmd_Clear_legal = True # whether giving the command to this object from a script would be an error
    _cmd_Clear_tooltip = "clear the dots" # a command button or menu item could use this as its tooltip
    pass

# ok, now how do we bind a click on empty space to class MakeANode ?

# note, someday we might just as easily bind a click on some guide surface
# (onto which we've applied an active tool to interpret clicks)
# to that command, as binding a click on empty space to it. The point is, we have tools, with cmds in them,
# and we bind tools to objects or to pieces of space (see scratch6 and recent notesfiles).
#
# so we can separate this: #####IMPLEM all these
# - put this command and others (for other modkeys) into a tool, and
# - make a button for a pallette which can (when run on a selected space or surface, or on the current space)
#   - bind that tool to empty space or to a guide surface.
# - make a pallette with that button
# - show this pallette.
# - make a space object... is it that World object above, or only sometimes, or only temporarily?
#   well, the tool can change for the same world, the world concerns itself only with what kind of data it can hold
#   (and it may offer a set of tools, or have a default one, or have implems of std-named ones...)

# but for an initial test, we can always be in this kind of world, have one tool implicitly, on entire space --
# but this does require changing the click-action. OR we could create a big image as a guide shape, and put click action on that.
# Hmm, I think that's easier, I'll try that first.

# Let's do it with a DNA origami image... but first, just a rect. So, we want a modifier for a thing (the rect)
# which gives it the event bindings implied by this tool. I.e. a macro based on Highlightable.


# status 061205 1022p: works (in this initial klugy form, not using Command classes above) except for recording points in abs coords
# (wrong) but drawing them in arb rel coords (wrong), when both need to be in a specified coord sys, namely that of the bg rect object.

# status 061207 ~9am: coords were fixed last night, and drag now works as of thismorning. simple demo draws blue nodes along the drag.
# In theory it's using depth found at each point, so it could draw on a 3d curved surface -- but that's not tested. [later, it is.]

# 061213 bug report, trivial: draws just in front, but in model coords, not screen coords. For trackball and then draw on back or
# other side, screen coords would work better -- or maybe object-surface-coords (as some comment suggests) would be better still,
# but for non-enclosed objs like planes, note that that depends on screen coords to know which face is facing the user.

class GraphDrawDemo_FixedToolOnArg1(InstanceMacro):
    # args
    background = Arg(Widget2D, Rect(10) )
        # testexpr_19a, 061207 morn -- see if arb objects work here, and try drawing on a curved surface --
        # works! (when the surface was the default here -- now also tested/works when it's the arg supplied by that testexpr)
        #
        # ... except for desirable improvements:
        # - we should replace DZ with "local perp to surface" to make the drawn things more visible.
        # - And we *might* want to replace depth with "computed true depth", since for a sphere, as we rotate the view
        #   the drawn radius slightly changes due to where the triangle faces are located, and this can bury the drawing of marks
        #   if they are really close to the sphere --
        # - either that, or record their posns relative to the sphere surface,
        #   which might be most correct anyway -- and especially useful if we change the radius of the sphere! (making it balloon-like)
        # - Also those things are oriented in global coords rather than coords based on the clicked surface.
        #   Fixing that would also make them "look oriented" and help you perceive their depth when they're over a curved surface.
        #
        # Note that all these ideas would require asking the object for the surface orientation, and for how to store coords (relative
        # to what), and in the given eg, getting quite different answers (incl about how to transform coords for storage, re scaling)
        # depending on whether the rect or sphere was clicked --
        # which the current code does not even detect, since it gives them the same glname. ###e
    # options
    highlight_color = Option(Color, None)#UNTESTED ## suggest: ave_colors(0.9,gray,white)) # use this only if background takes a color option
    use_VertexView = Option(bool, False) # 070105 so I can try out new code w/o breaking old code #### TRYIT
    # internals
    world = Instance( World() ) # has .nodelist I'm allowed to extend
    _value = Overlay(
      DisplistChunk( # new feature as of 070103; works, and seems to be faster (hard to be sure)
        Highlightable( background, #######   WAIT A MINUTE,   how can we do that -- background is already an instance?!? ######@@@@@@
                       ## background(color=green),####KLUGE, causes various bugs or weirdnesses... not yet fully understood,
                       ## e.g. AssertionError: compute method asked for on non-Instance <Rect#10415(a)>
                       ## [GLPane_overrider.py:455] [Highlightable.py:275] [Rect.py:52]
                       ##Rect(5,5,green),###KLUGE2 - works now that highlightable is not broken by projection=True [also works 061213]
                       ## background.copy(color=green), # oops i mean:
                       ## call_Expr(background.copy,)( color=green), # oops, i have to include eval_Expr:
                       If( highlight_color,#UNTESTED
                          eval_Expr( call_Expr(background.copy,)( color = highlight_color) ),
                               # can't work unless background is simple like a Rect,
                               # but does work then! (edit _19d to include _19 not _19b)
                          background ## None -- I hoped None would be equivalent, noticed in HL and replaced, but that would be hard,
                           # would require it to notice each time whether the opt was suppied or not, do default each time
                           # rather than per-time, also require supplying None to be same as not supplying the arg (not true now)
                           # (maybe passing some other symbol should be same as that?? and permitted each time? But If->None is so
                           #  easy, by leaving out the arg... ###e decide)
                        ),
                       #e want this to work too: call_Expr(background.copy, color=green),
                           # -- just let copy take **kws and pass them on, or let it call a customize helper
                       # review of the kluges:
                       # - the explicit call_Expr remains annoying but the lack of simple fix still seems true; not sure;
                       #   could we experiment by turning off that check within certain classes? not sure if that's possible
                       #   since it happens during expr-building. ##k
                       # - the need for eval_Expr seems wrong somehow, in fact i'm not sure I understand why we need it.
                       #   Will it go away in new planned eval/instantiation scheme? not sure. I think so.
                       # - copy needs **kws.
                       # - does the .copy itself need to be explicit? that is, could supplying args/opts to an instance copy it implicitly??
                       #   this might fit with other instances doing other stuff when those were supplied.... ###e
                       # - should Overlay take color option and pass it on into leaves (subexprs)? what if some leaves won't take it?
                       #   that has been discussed elsewhere... i forget if dynenv or _optional_options = dict() seemed best.
                       on_press = _self.on_press_bg,
                       on_drag = _self.on_drag_bg )), # end of Highlightable and DisplistChunk
      If( _self.use_VertexView,
          DisplistChunk( WithViewerFunc(world, viewerfunc) ),
          DisplistChunk( world) ##, debug_prints = "World")
          # try DisplistChunk, 070103 later -- works, doesn't break dragging of contained old nodes.
      )
    )
    _index_counter = State(int, 1000) # we have to use this for indexes of created thing, or they overlap state!

    newnode = None # note: name conflict(?) with one of those not yet used Command classes
    
    def on_press_bg(self):
        if 0:
            print "compare:"
            print self, self.delegate, self.delegate.delegate, self.delegate.delegate.plain # the background
            print self.background
            print "hl.highlighted =",self.delegate.delegate.highlighted
                # self.background is the same as the .plain printed above, which means, as of 061208 941pm anyway,
                # instantiating an instance gives exactly that instance. (Reasonable for now...)
            
        point = self.current_event_mousepoint()
            #e note: current_event_mousepoint is defined only on Highlightable, for now (see comments there for how we need to fix that),
            # but works here because we delegate ultimately to a Highlightable, without changing local coords as we do.
            # note: lots of devel scratch & debug comments removed 061207; see cvs rev 1.5 for them.

        # for initial test, don't use those Command classes above, just do a side effect right here ###kluge

        newpos = point + DZ * PIXELS # kluge: move it slightly closer so we can see it in spite of bg
            ###e needs more principled fix -- not yet sure what that should be -- is it to *draw* closer? (in a perp dir from surface)
            #e or just to create spheres (or anything else with thickness in Z) instead? (that should not always be required)

        if not self.use_VertexView:
            # old code
            node_expr = Vertex(newpos, Center(Rect(0.2,0.2,
                                             ## 'green', -- now we cycle through several colors: (colors,...)[counter % 6]
                                             tuple_Expr(green,yellow,red,blue,white,black)[mod_Expr(_this(Vertex).ipath[0],6)]
                                             )))
        else:
            # new code, being written 070105, just getting started -- mostly nim
            node_expr = Vertex_new(newpos,
                               # cycle through several colors: (colors,...)[counter % 6]
                               color = tuple_Expr(green,yellow,red,blue,white,black)[mod_Expr(_this(Vertex).ipath[0],6)]
                            )
            pass
        
        ## draggable_node_expr = Highlightable(node_expr, on_drag = _self.on_drag_node, sbar_text = "dne")
            ###BUG: this breaks dragging of the new node; it fails to print the call message from on_drag_node;
            # if you try to drag an old node made this way, it doesn't work but says
            # debug fyi: len(names) == 2 (names = (268L, 269L))
            # Guess: limitation in current rendering code makes it not work for any nested glnames, but just print this instead...
            # (note: even after reload, the node objects in the world have their old Vertex class, and the old expr used to make them)
            #
            # [later 061213:] IIRC the status was: I made GLPane_overrider so I could fix that 2-glname issue in it,
            # but never got to that yet. Meanwhile I commented out the use of this expr, and thus on_drag_node is never used...
            # and Vertexes dragged directly do nothing -- they're highlightable but with no actions.
            # And World could probably draw them highlightable even if they weren't, but it doesn't.
            # BTW the disabled nonworking draggable_node_expr is not well-designed -- it does not add a Vertex to World, it adds a
            # draggable one -- but even World is not perfect, since it contains Vertexes (not just their data)
            # and they inherently have (a lack of) action bindings since they are Highlightable.
            # Probably better would be if World contained data-nodes and had access to (or had its own) display rules for them
            # which added commands/actions based on the currently active tools. That would help with tool-code-reloading too.
            # Probably some other comments here say this too.
            #
            # So does a World need a formula or function arg for how to map its data objects to display objects, at the moment?
            # Or is there some scheme of a global map for that, to be applied when "drawing" any data object?
            # And do some data objs have their own positions, or is that always supplied by the world or other data obj they're in?
            # In theory, we might display atoms at posns unrelated to atom.pos, e.g. as a row in a table which includes their coords.
            # So it's more like we have ways of "drawing a set of things" which can say "at posns given by func(thing)"
            # or "at successive posns in a column", corresponding to two display forms with different exprs,
            # with the map from thing to individual display form also needing to be specified.
            # So a World is more like a set of things, and it can have a display mode (or more than one), given a thing-display-function.
            # We can ask it or anything else how it recommends displaying itself given display style options,
            # but we can choose to use that display function (from it to a more directly displayable object) or use another one.
            # Or we can probably just "draw it" and have it pick up the current display style from the env (including the
            # currently active tools). Is there any reason not to permit both? (draw using current style, draw using given style,
            # give me function from you to drawables using given style, use specific function and draw the results -- all possible.)
            # 
            # If a thing in a world has standard mouse actions of its own, can it also have "grabbable areas" for use in dragging it
            # when it has a posn as displayed in some world? Or did that world have to explicitly turn it into a draggable thing?
            # Answer: both. The world turns it into that by adding a drag binding for those "overall handles" the thing has.
            # It might draw them with glnames in some set it knows... ie as named subobjs of itself. The overall thing might also
            # have a single name. Then we have a sequence of two glnames meaning obj/subobj which we want to use to determine the action.
            # For some subobjs that's within the object and supplied by it (perhaps depending on tool); for others,
            # it's supplied by the World it's in (also dep on a tool) and handled by it (eg move the obj, select the obj).
            #
            # For the simple things we have there, there are no subobjects, and no actions except drag or later select the whole thing.
            # A simple model is "one thing was hit, but some things are specified by a specific series of two or more glnames".
            # In general the outer name decides how to interpret (or whether to ignore) the inner names.
            # It can map the inner ones somehow... not sure how. This will relate a lot to DisplistChunk when we have that.
            # Mere nested Highlightables might push two names but both would be unique. Outer name might just defer to inner one then.
            
        if 0:
            ## MAKE THIS WORK:
            newnode = self.make_and_add( draggable_node_expr)
        else:
            newnode = self.make_and_add( node_expr)
            
        self.newnode = newnode ###KLUGE that we store it directly in self; might work tho; we store it only for use by on_drag_bg
        return # from on_press_bg
    
    def make_and_add(self, node_expr):
        node = self.make(node_expr)
            ### NOTE: index should really be determined by where we add it in world, or changed when we do that;
            # for now, that picks a unique index (using a counter in transient_state)
        
        ## self.world.nodelist.append(node)
        self.world.nodelist = self.world.nodelist + [node] # kluge: make sure it gets change-tracked. Inefficient when long!
        
        ##e let new node be dragged, and use Command classes above for newmaking and dragging
        return node
    
##    def on_drag_node(self):
##        print "on_drag_node called -- how can we know *which* node it was called on??"
##        # 070103 status guess: this is not called; old cmts above seem to say that the only problem with it working is nested glnames. 
##        return
    
    def on_drag_bg(self):
        # note: so far, anyway, called only for drag after click on empty space, not from drag after click on existing node
        point = self.current_event_mousepoint()
        lastnode = self.newnode # btw nothing clears this on mouseup, so in theory it could be left from a prior drag
##        try:
##            lastipath = lastnode.ipath[0]
##        except:
##            lastipath = -1
##        # print "on_drag_bg %d" % lastipath, point###  # this shows no error in retaining correct lastnode -- that's not the bug
        newpos = point + DZ * PIXELS * 2 # used for different things, depending
        
        what = kluge_dragtool_state() ###IMPLEM better
        if what == 'draw':
            # make a blue dot showing the drag path, without moving the main new node (from the click)
            node_expr = Vertex(newpos, Center(Rect(0.1,0.1,blue)))
            self.make_and_add(node_expr)
        elif what == 'drag':
            # drag the new node made by the click
            if not lastnode:
                print "bug: no self.newnode!!!"
            else:
                lastnode.pos = newpos # this is always triggering the "standard inval twice" message; don't yet know why;
                    # see g4 file '061207 debug std inval twice' for two stacktraces for once and twice (not confirmed from same
                    # source), one with longer inval path. That file asks:
                    #  could it be a normal consequence of two paths of usage/dependency from one thing (node.pos) to another (glpane),
                    #  with the ends of the two paths entering glpane at different invalidation subs from it??
                    #  I doubt it... but should review. Or what if they enter at the same subs? Also doubt it, also should review. ##k

                # print "set %r.pos = %r" % (lastnode,newpos)### this shows i set them, then draw them to a different pos! Why?[where i am]
                self.env.glpane.gl_update() ###KLUGE [attempted bugfix, didn't work, see comment for guess at why]
                    # without this gl_update, during drag of a new node,
                    # if mouse gets too far ahead, we lose the updates until we mouse over some node,
                    # perhaps since only a change of what's highlighted triggers an update. Why doesn't change-tracking of the setattr
                    # solve that???? HMM, ADDING THIS gl_update DOESN'T FIX THE BUG!   ###BUG
                    #
                    # Under what conds does gl_update not redraw?!?
                    #   GUESS [wrong, see below] - mouse motion, detecting no change of selobj in selectMode, perhaps immediately does nothing
                    # (not calling this routine via drag_handler at all)... but then how do we drag atoms? Review this. #k
                    #   NO, that can't be it -- our debug print above is indeed printing that it gets called.
                    #
                    # Can it just be that Qt has no time to redraw since it's processing repeated drag events?
                    # Wouldn't it merge them? (Maybe not.) But I observed that stopping and waiting didn't seem to solve the problem.
                    #
                    # SOLVED: It was the Numeric array == bug, in lvals.py optim for setting to same value.
                    # If any coord was the same, it didn't inval or change the stored pos. Fixed using same_vals.
                    # Checked for other such bugs in that file, BUT NOT IN OTHER FILES. ###DOIT [061207 10p] 
            pass
        return
    
    def make(self, expr):
        index = None
        #e rename? #e move to some superclass 
        #e worry about lexenv, eg _self in the expr, _this or _my in it... is expr hardcoded or from an arg?
        #e revise implem in other ways eg eval vs instantiate
        #e default unique index?? (unique in the saved stateplace, not just here)
        # (in fact, is reuse of index going to occur from a Command and be a problem? note *we* are acting as command...
        #e use in other recent commits that inlined it
        if index is None:
            # usual case I hope (due to issues mentioned above): allocate one
            if 0:
                index = getattr(self, '_index_counter', 100)
                index = index + 1
                setattr(self, '_index_counter', index)
            else:
                # try to fix bug
                index = self._index_counter
                index = index + 1
                self._index_counter = index
                ###e LOGIC ISSUE: should assert the resulting ipath has never been used,
                # or have a more fundamental mechanism to guarantee that
        env = self.env # maybe wrong, esp re _self
        ipath = (index, self.ipath)
        return expr._e_eval(self.env, ipath)
    pass # end of class GraphDrawDemo_FixedToolOnArg1

kluge_dragtool_state_prefs_key = "A9 devel/kluge_dragtool_state_bool"
kluge_dragtool_state_prefs_default = False ## False = 'draw', True = 'drag' (since our only prefs control yet is a boolean checkbox)

def kluge_dragtool_state():
    # can edit by hand, then reload; should make it a checkbox or tool-choice setting (tho 'drag' is useless)...
    # it's like a user pref or transient state for the *toolset* of which the tools choosable here are a part.
    # (typically you have one instance of each toolset in your app, not one per editable thing for each kind of toolset,
    #  though if you ask, there might be a way to customize those settings for what you edit -- but by default they're general.)
    # so for now we can approximate this using either transient state or prefs state for the toolset object,
    # or a prefs key if we don't have that kind of state. (Note: currently no stateplace is stored in prefs, but one could be.)
    #
    # related digr: if code uses prefs, those prefs might as well be readily available when that code's in use,
    # so automatically we can get code-specific control panels just to control display & behavior that affects what's now on screen,
    # organized in std hierarchy but filtered for whether they are "in use". For now do this by hand, but later we'll want some way
    # to find out what's in use in that sense, and usage-tracking might be enough unless prefs get bundled into single tracked objs
    # of which then only some parts get used. We can probably avoid that well enough by convention.
    if 0:
        if 1:
            return 'draw' # usual case
        else:
            return 'drag'
    else:
        import env
        # for this kluge, let the stored value be False or True for whether it's drag
        return env.prefs.get(kluge_dragtool_state_prefs_key, kluge_dragtool_state_prefs_default) and 'drag' or 'draw'
    pass

kluge_dragtool_state() # set the default val

##def _kluge_clear_the_world(): OBS, will remove after commit
##    # find the World
##    from test import _kluge_current_testexpr_instance, enable_testbed
##    #e now how do we find the instance of testexpr if enable_testbed is true? ...
##    # conclusion: this approach is ###WRONG, instead the checkbox thingy below needs an arg...
##    testexpr_instance = ...
##    # assume that's a GraphDrawDemo_FixedToolOnArg1 with .world
##    world = testexpr_instance.world
##    world._cmd_Clear()
##    return
    
kluge_dragtool_state_checkbox_expr = SimpleColumn( # note, on 061215 late, checkbox_pref was replaced with a better version, same name
    checkbox_pref(kluge_dragtool_state_prefs_key,         "drag new nodes?", dflt = kluge_dragtool_state_prefs_default),
    checkbox_pref(kluge_dragtool_state_prefs_key + "bla", "some other pref"),
##    checkbox_pref(kluge_dragtool_state_prefs_key + "cb ", "button: clear (buggy)"), #e use ActionButton somehow, but what action? see below...
##    ActionButton( _kluge_clear_the_world, "button: clear (untested)")
 )    

def demo_drag_toolcorner_expr_maker(world): #070106 improving the above ### USE ME
    # given an instance of World, return an expr for the "toolcorner" for use along with GraphDrawDemo_FixedToolOnArg1 (on the same World)
    expr = SimpleColumn(
        checkbox_pref(kluge_dragtool_state_prefs_key,         "drag new nodes?", dflt = kluge_dragtool_state_prefs_default),
        checkbox_pref(kluge_dragtool_state_prefs_key + "bla", "some other pref"),
        ## ActionButton( world._cmd_Clear, "button: clear") # works
        # 070108: try this variant which uses _cmd_Clear_nontrivial: will the If work as an Expr?? If_kluge should tell us #####k
        ####k also will the type tests inside ActionButton work with an If? Probably not -- that's a ###BUG but I'll put it off.
        ## 1. make this work later: ActionButton( world._cmd_Clear, If_kluge( world._cmd_Clear_nontrivial, "button: clear", "button (disabled): clear"))
##          2. this too: If_kluge( world._cmd_Clear_nontrivial,
##                  ActionButton( world._cmd_Clear, "button: clear"),
##                  ActionButton( world._cmd_Clear, "button (disabled): clear")
##         )
        If_kluge( getattr_Expr( world, '_cmd_Clear_nontrivial'),
                  ActionButton( world._cmd_Clear, "button: clear"),
                  ActionButton( world._cmd_Clear, "button (disabled): clear", enabled = False)
         ) # works, though text change is so slow I suspect there's actually a highlighting or update bug making it appear even slower...
          # update 070109: the bug seems to be that as long as the mouse stays on the button, it remains highlighted with the old highlight form.
     )
    return expr

# end
