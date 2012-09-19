# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
demo_drag.py

@author: bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.


demo not only some drag actions, but some ways of setting up new model types
and their edit tools and behaviors. [Eventually.]

[for current status see comments just before GraphDrawDemo_FixedToolOnArg1]

070105 moved the pseudocode for Command & DragCommand class etc into new file Command_scratch_1.py --
see it for ideas about Command, DragCommand, _PERMIT_SETS_INSIDE_, DragANode, ClickDragCommand, MakeANode.
(But some comments below still discuss Command and MakeANode in important ways.)

Notable bug (really in check_target_depth in GLPane, not this file): highlighted-object-finder
can be fooled by nearby depths due to check_target_depth_fudge_factor of 0.0001. This caused
a bug here, which is so far only worked around (by increasing DZFUZZ), not really fixed. [070115 comment]

==

See also:
* demo_drag_2_scratch.py
* dna_ribbon_view.py
* world.py
* rules.py

"""

from OpenGL.GL import GL_LINE_LOOP
from OpenGL.GL import glBegin
from OpenGL.GL import GL_LINE_STRIP
from OpenGL.GL import glVertex3fv
from OpenGL.GL import glEnd

from exprs.Overlay import Overlay

from exprs.transforms import Translate

from exprs.Rect import Rect ##, Sphere

from exprs.Center import Center

from exprs.Highlightable import Highlightable, BackgroundObject ##, Button, print_Expr

from exprs.controls import checkbox_pref, ActionButton

from exprs.Column import SimpleColumn ##, SimpleRow

from exprs.DisplayListChunk import DisplayListChunk

from exprs.world import World

from utilities.constants import black, noop
from utilities.constants import red
from utilities.constants import blue
from utilities.constants import green
from utilities.constants import white
from utilities.constants import yellow

from exprs.Exprs import list_Expr, eval_Expr, call_Expr
from exprs.Exprs import mod_Expr
from exprs.Exprs import tuple_Expr
from exprs.Exprs import getattr_Expr
from exprs.If_expr import If
from exprs.If_expr import If_kluge
from exprs.widget2d import Stub, Widget2D
from exprs.instance_helpers import ModelObject, InstanceOrExpr, DelegatingInstanceOrExpr, InstanceMacro, _this
from exprs.attr_decl_macros import Arg, State, ArgOrOption, Option
from exprs.ExprsConstants import PIXELS, Position, Color, StubType, ORIGIN, DZ
from exprs.py_utils import printfyi
from exprs.__Symbols__ import Anything, _self

# ==

## _viewer_for_object, etc, moved to rules.py on 070123

DZFUZZ = PIXELS * 3.0 # replacing 1, 2, 2.5 in different places, to work around bug reported in BUGS as:
    # 070115 "highlightable-finder can be fooled due to check_target_depth_fudge_factor of 0.0001"
    # (see also the assignment of check_target_depth_fudge_factor in testmode.py, and the discussion in BUGS.txt of better fixes ###e)
    # WARNING: It's possible that the value of DZFUZZ needed to work around this bug depends
    # on the GLPane size, or on user prefs settings, or on Ortho vs Perspective! (all speculations)

## DZFUZZ = PIXELS * 0.5 # this also works, given the change in testmode.py to check_target_depth_fudge_factor = 0.00001 [070116],
# reducing it by 10x, but I will leave it this way (>10x margin of safety) to make it unlikely the bug will show up with
# other GLPane sizes, zoom factors, etc. Sometime it needs one of the better fixes discussed in BUGS.txt.


class Vertex(ModelObject): # renamed Node -> Vertex, to avoid confusion (tho it added some too, since localvars not all changed,
      # and since the world ought to contain model objs anyway, in general, of which Vertex is only one type, and current implem
      # also has its own graphics code)...
    # see below about better ways to rename it...
    """It has a position, initializable from arg1 but also settable as state under name pos, and an arb appearance.
    Position is relative to whatever coords it's drawn in.
    When you drag it, it chooses depth just nearer than hitpoint -- which means if you wiggle it over itself,
    it gets nearer and nearer (design flaw). [see comment for possible fix]
    """
    # 070223 possible fix to seeing depth of self: during a drag, tell glpane not to draw dragobj into depth or during glselect
    # mode... so it finds some other selobj besides dragobj. means it should draw dragobj last i guess... maybe transparent
    # so you can see selobj behind it, or diff color when there is a selobj...

    ###e about what to rename it... Hmm, is it a general "Draggable"? .lookslike arg2 -> .islike or .thing arg1?

    # BTW, the highlightability is not yet specified here ###nim; it relates to the fact that we can bind commands to it
    # (as opposed to things it contains or is contained in, tho that should be permitted at the same time,
    #  tho implem requires nested glnames to sometimes ignore inner ones, when those are inactive);
    # but we might add it in a wrapper which makes it into a view of it that lets commands be bound to it,
    # except that World.draw assumes we draw the actual model objs, not wraps of them - also an issue if env says they
    # look different -- so maybe World needs to wrap all it draws with glue to add looks and behavior to it, in fact.
    # [update much later 070201: or maybe ModelObject knows about this and asks env whether to override default drawing code.]

    # but for now, can we do this here?

    pos0 = Arg(Position)
    pos = State(Position, pos0) ###BUG -- does this work -- is pos0 set in time for this? not sure it's working... 061205 1009p
    #e we probably want to combine pos0/pos into one StateArg so it's obvious how they relate,
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

    cmenu_maker = State(Anything, None) # meant to be set from outside; let's hope None is a legal value [070223 HACK]
    ## delegate = _self.lookslike #k
    delegate = Highlightable( Translate( lookslike, pos ),
                              ## eval_Expr( call_Expr(lookslike.copy,)( color = yellow) ),  #####?? weird exc don't know why - reload?
                              ## AssertionError: _this failed to find referent for '_this_Vertex'
                              on_drag = _self.on_drag, # 070103 kluge experiment, works (eg in _19d)
                              cmenu_maker = cmenu_maker #070223 HACK [#e rename cmenu_maker to cmenu_obj as I guessed it was named??]
                              )
                #e actions? or do this in a per-tool wrapper which knows the actions?
                # or, do this here and make the actions delegate to the current tool for the current parent? guess: the latter.

        ##e digr: will we want to rename delegate so it's only for appearance? *is it*? does it sim like this too?
        # Guess: it's for everything -- looks, sim qualities, etc -- except what we override or grab from special members.
        # [if so, no need to rename, except to clarify, leaving it general.]
    #e might need something for how to save it in a file, Undo policy, etc

    def on_drag(self): # 070103 kluge experiment, copied/modified from on_drag_bg in bigger class below

        # Note: this bug reported in BUGS breaks dragging of these nodes; worked around by increasing DZFUZZ:
        # 070115 "highlightable-finder can be fooled due to check_target_depth_fudge_factor of 0.0001"

        # where i am 070103 447p (one of two places with that comment)
        # - sort of sometimes works, but posns are sometimes same as bg, not sure why that DZ would be needed,
        # oh i guess the mousepos comes from the gray bg rect not the self unless we drag very slow...

        point = self.current_event_mousepoint() ### MIGHT BE WRONG COORDS? guess: no
         #k guess: will have snap-to-fixed-point bug for generic drag code
        newpos = point + DZ * DZFUZZ # used for different things, depending #### DZ needed but might cause trouble too
        self.pos = newpos
        ## print "in-node action set %r.pos = %r" % (self, newpos) # sometimes works
        self.KLUGE_gl_update() #k needed?
        return

    pass # end of class Vertex

# ==

# Summary of this and Vertex_new -- make use_VertexView work --
# [long comment added 070111; devel on this code has been inactive for a few days]
#
# it's an example of dynamically mapping selobj thru toolstate to get looks & behavior,
# so the model object itself can be split out and needs no graphics/interaction code of its own.
# My general sense in hindsight is that it's too low-level -- I need to figure out how all this could/should look as toplevel exprs.
#
# See a new file rules.py for more on that.

class Vertex_new(ModelObject): #070105 ###e maybe it also needs an official type or typename for use in rules and files?
    pos0 = Arg(Position)
    pos = State(Position, pos0)
    color = Option(Color, black)
    pass

class Viewer(InstanceOrExpr):
    "superclass for viewers of model objs given as arg1"
    modelobj = Arg(ModelObject) #k can subclass refer to this??
    pass

class VertexViewer(DelegatingInstanceOrExpr, Viewer): ###k ok supers?

    delegate = Rect(1, color = _self.modelobj.color) ###WRONG details, also assumes _self.modelobj has a color, but some don't.
        ###e do we wrap it in a provider of new default options??
    ###e also needs behaviors...

## viewerfunc = identity # stub - might better be that hardcoded helper func above ####e
def viewerfunc(x):
    printfyi("viewerfunc is being used but is a stub")
    return x

WithViewerFunc = Stub # see rules.py, to which I moved the more expansive stub of this, 070123

# ===

# 070223 new hack

##class polyline_handle(DelegatingInstanceOrExpr):
##    delegate = Draggable(Rect(0.3,green))

class polyline(InstanceOrExpr): # WARNING [070319]: duplicated code, demo_drag.py and demo_draw_on_surface.py [modified a bit]
    """A graphical object with an extendable (or resettable from outside I guess) list of points,
    and a kid (end1) (supplied, but optional (leaving it out is ###UNTESTED)) that can serve as a drag handle by default.
    (And which also picks up a cmenu from self. (kluge!))
    Also some Options, see the code.
    """
    # Note [070307]: this class will be superceded by class Polyline in demo_polyline.py,
    # and the code that uses it below (eg the add_point call) will be superseded by other code in that file.
    #
    ###BUGS: doesn't set color, depends on luck. end1 is not fully part of it so putting cmenu on it will be hard.
    # could use cmenu to set the options.
    # end1 might be in MT directly and also be our kid (not necessarily wrong, caller needn't add it to MT).
    # when drawing on sphere, long line segs can go inside it and not be seen.
    points = State(list_Expr, []) ###k probably wrong way to say the value should be a list
##    end1arg = Arg(StubType,None)
##    end1 = Instance(eval_Expr( call_Expr(end1arg.copy,)( color = green) ))###HACK - works except color is ignored and orig obscures copy
    end1 = Arg(StubType, None, doc = "KLUGE arg: optional externally supplied drag-handle, also is given our cmenu by direct mod")
    closed = Option(bool, False, doc = "whether to draw it as a closed loop")
    _closed_state = State(bool, closed) ####KLUGE, needs OptionState
    relative = Option(bool, True, doc = "whether to position it relative to the center of self.end1 (if it has one)")
    def _init_instance(self):
        end1 = self.end1
        if end1:
            end1.cmenu_maker = self
    def _C__use_relative(self):
        "compute self._use_relative (whether to use the relative option)"
        if self.relative:
            try:
                center = self.end1.center
                return True
            except:
                #e print?
                return False
        return False
    def _C_origin(self): #070307 renamed this to origin from center
        if self._use_relative:
            return self.end1.center # this can vary!
        return ORIGIN
##    center = _self.origin #k might not be needed -- guessing it's not, 070307
    def add_point(self, pos):
        "add a point at the given 3d position"
        pos = pos - self.origin
        self.points = self.points + [pos] ### INEFFICIENT, but need to use '+' for now to make sure it's change-tracked
    def draw(self):
        ###k is it wrong to draw both a kid and some opengl stuff?? not really, just suboptimal if opengl stuff takes long (re rendering.py)
        self.drawkid(self.end1) # end1 node
        if self._closed_state:
            glBegin(GL_LINE_LOOP) # note: nothing sets color. see drawline for how.
                # in practice it's thin and dark gray - just by luck.
        else:
            glBegin(GL_LINE_STRIP)
        if self._use_relative:
            # general case - but also include origin (end1.center) as first point!
            origin = self.origin
            glVertex3fv(origin)
            for pos in self.points:
                glVertex3fv(pos + origin)
        else:
            # optim - but not equivalent since don't include origin!
            for pos in self.points:
                glVertex3fv(pos)
        glEnd()
        #e option to also draw dots on the points [useful if we're made differently, one click per point; and they might be draggable #e]
        return
    def make_selobj_cmenu_items(self, menu_spec, highlightable):
        """Add self-specific context menu items to <menu_spec> list when self is the selobj (or its delegate(?)... ###doc better).
        Only works if this obj (self) gets passed to Highlightable's cmenu_maker option (which DraggableObject(self) will do).
        [For more examples, see this method as implemented in chem.py, jigs*.py in cad/src.]
        """
        menu_spec.extend([
            ("polyline", noop, 'disabled'), # or 'checked' or 'unchecked'; item = None for separator; submenu possible
        ])

    pass

# ===

## class World(ModelObject) -- moved to world.py, 070201

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

class GraphDrawDemo_FixedToolOnArg1(InstanceMacro): # see also class World_dna_holder -- need to unify them as a ui-provider framework
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
    highlight_color = Option(Color, None) # suggest: ave_colors(0.9,gray,white)) # use this only if background takes a color option
    use_VertexView = Option(bool, False) # 070105 so I can try out new code w/o breaking old code #### TRYIT
    world = Option(World, World(), doc = "the set of model objects") # revised 070228 for use in _19j
    test_background_object = Option(bool, False, doc = "test the new testmode._background_object feature") #070322
    hide_background_object = Option(bool, False)
    # internals
    highlightable_background = \
        Highlightable( background, #######   WAIT A MINUTE,   how can we do that -- background is already an instance?!? ######@@@@@@
                       ## background(color=green),####KLUGE, causes various bugs or weirdnesses... not yet fully understood,
                       ## e.g. AssertionError: compute method asked for on non-Instance <Rect#10415(a)>
                       ## [GLPane_overrider.py:455] [Highlightable.py:275] [Rect.py:52]
                       ##Rect(5,5,green),###KLUGE2 - works now that highlightable is not broken by projection=True [also works 061213]
                       ## background.copy(color=green), # oops i mean:
                       ## call_Expr(background.copy,)( color=green), # oops, i have to include eval_Expr:
                       If( highlight_color,
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
                       on_drag = _self.on_drag_bg,
                       on_release = _self.on_release_bg,
                       sbar_text = "gray bg"
                       )
    use_highlightable_background = If( test_background_object,
                                       BackgroundObject( highlightable_background, hide = hide_background_object),
                                       DisplayListChunk( # new feature as of 070103; works, and seems to be faster (hard to be sure)
                                           highlightable_background
                                        )
                                    )
    ## world = Instance( World() ) # maintains the set of objects in the model
    _value = Overlay(
        use_highlightable_background,
        If( _self.use_VertexView,
            DisplayListChunk( WithViewerFunc(world, viewerfunc) ),
            # try DisplayListChunk, 070103 later -- works, doesn't break dragging of contained old nodes.
            DisplayListChunk( world) ##, debug_prints = "World")
            ## world # zap DisplayListChunk to see if it fixes new 070115 bug about dragging old nodes -- nope
        )
    )

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

        newpos = point + DZ * DZFUZZ # kluge: move it slightly closer so we can see it in spite of bg
            ###e needs more principled fix -- not yet sure what that should be -- is it to *draw* closer? (in a perp dir from surface)
            #e or just to create spheres (or anything else with thickness in Z) instead? (that should not always be required)

            ###BUG: DZ is not always the right direction! [more comment on that in demo_draw_on_surface.py]

        if not self.use_VertexView:
            # old code
            ## print "make node in old way (not using VertexView)" # still running as of 070115 at least in testexpr_19f
            node_expr = Vertex(newpos, Center(Rect(0.2,0.2,
                                             ## 'green', -- now we cycle through several colors: (colors,...)[counter % 6]
                                             ## tuple_Expr(green,yellow,red,blue,white,black)[mod_Expr(_this(Vertex).ipath[0],6)]
                                             red # the above worked ok until tested 070121 morn -- ipath now starts with string.
                                                   # it was a kluge anyway, so disable it until we can rework it to be sensible.
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
            # It can map the inner ones somehow... not sure how. This will relate a lot to DisplayListChunk when we have that.
            # Mere nested Highlightables might push two names but both would be unique. Outer name might just defer to inner one then.

        if 0:
            ## MAKE THIS WORK:
            draggable_node_expr = 'define this'
            newnode = self.world.make_and_add( draggable_node_expr, type = "Vertex")
        else:
            newnode = self.world.make_and_add( node_expr, type = "Vertex") #070206 added type = "Vertex"

        self.newnode = newnode ###KLUGE that we store it directly in self; might work tho; we store it only for use by on_drag_bg
        return # from on_press_bg

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
        ## print "on_drag_bg"
        newpos = point + DZ * DZFUZZ # used for different things, depending

        what = kluge_dragtool_state() ###IMPLEM better
        if what == 'draw':
            # make a blue dot showing the drag path, without moving the main new node (from the click)
            node_expr = Vertex(newpos, Center(Rect(0.1,0.1,blue)))
            self.world.make_and_add(node_expr, type = "dot") #070206 added type = "dot" -- note, not deducible from the expr!!
        elif what == 'polyline':
            if not lastnode:
                print "bug: no self.newnode!!!"
            else:
                if not isinstance(lastnode, polyline):
                    lastnode = self.newnode = self.world.make_and_add( polyline(lastnode), type = "polyline" )
                lastnode.add_point(newpos)
        elif what == 'drag':
            # drag the new node made by the click
            if not lastnode:
                print "bug: no self.newnode!!!"
            else:
                lastnode.pos = newpos
            pass
        return

    def on_release_bg(self):#070223 new hack
        import foundation.env as env #FIX
        if isinstance(self.newnode, polyline) and env.prefs.get(kluge_dragtool_state_prefs_key + "bla2", False):
            self.newnode._closed_state = True ####KLUGE, I'd rather say .closed but that won't work until I have OptionState
        return
    # == methods make, make_and_add have been moved from here into class World [070202]

    pass # end of class GraphDrawDemo_FixedToolOnArg1

kluge_dragtool_state_prefs_key = "A9 devel/kluge_dragtool_state_bool"
kluge_dragtool_state_prefs_default = False ## False = 'draw', True = 'drag' (since our only prefs control yet is a boolean checkbox)

def kluge_dragtool_state():
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
    import foundation.env as env
    polyline = env.prefs.get(kluge_dragtool_state_prefs_key + "bla", False)#070223 new hack
    if polyline:
        return "polyline"
    # for this kluge, let the stored value be False or True for whether it's drag
    drag = env.prefs.get(kluge_dragtool_state_prefs_key, kluge_dragtool_state_prefs_default)
    return drag and 'drag' or 'draw'

kluge_dragtool_state() # set the default val

kluge_dragtool_state_checkbox_expr = SimpleColumn( # note, on 061215 late, checkbox_pref was replaced with a better version, same name
    checkbox_pref(kluge_dragtool_state_prefs_key,         "drag new nodes?", dflt = kluge_dragtool_state_prefs_default),
    checkbox_pref(kluge_dragtool_state_prefs_key + "bla", "some other pref"),
 )

def demo_drag_toolcorner_expr_maker(world): #070106 improving the above
    # given an instance of World, return an expr for the "toolcorner" for use along with GraphDrawDemo_FixedToolOnArg1 (on the same World)
    expr = SimpleColumn(
        checkbox_pref(kluge_dragtool_state_prefs_key,         "drag new nodes?", dflt = kluge_dragtool_state_prefs_default),
        checkbox_pref(kluge_dragtool_state_prefs_key + "bla", "make polyline?", dflt = False),
        checkbox_pref(kluge_dragtool_state_prefs_key + "bla2", "(make it closed?)", dflt = False),
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
