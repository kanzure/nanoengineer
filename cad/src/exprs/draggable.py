# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
draggable.py

@author: bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.


070203 status: DraggableObject works, except:
- move/flush untested, and if it works, will require objs already with posn state
- moved/rotated coordsys untested

See also the future usage comments in DraggableObject's docstring.

070203 Design discussion (scratch):

Draggable( thing):
- have own state which is drag pos
- have a command which pushes that state into the object by calling a move method on it
- run that command on mouseup, for now, so highlighting can work inside the object
- temporary solution, since external bonds would need abs coords even during the drag
- better soln is for inner thing to be drawable in more than one coordsys! its own, or abs.
  and for points in it to reveal coords in more than one.
  coordsys to draw in is passed how:
  - parameter in dynenv in glpane? problem is, changetracking of drawing effects.
    they can change in one coordsys indeply of changing in another one!!! ###
    that is, there is a coordsys of least change, and this varies by part and by time!
    but if ever nonconstant, it's "none" (not counting objects with symmetries for it,
      like spheres, dots, infinite lines).
    so for a given object that changed, either it changed in all coordsystems,
    or in all but a specific one... but that one is not a fixed property of that object.
    But our code should always be able to produce a good guess about what system that is.
    BTW it might really be more than one system, since they can equal each other for awhile
    and then not! This happens for the above Draggable idea, between an object's native system
    (used in its own displist) and the one maintained by Draggable during a drag.

Note, that's for a Draggable wrapper,
but there is also a Draggable interface (in comments and stub code),
which is for any object that can accept standard drag events,
regardless of what it uses them for
(which could be anything that varies with mousepos while it's down).

In theory wrapper and interface are implementationally independent namespaces (AFAIK so far)
so this overloading would be tolerable. But would it be misleading? Would all methods of
the wrapper be assumed to be part of the interface? Quite possibly. So one of them should be renamed.

Note that Draggability of a visible object will tend to go along with selectability...

For now, just use a temp name, fix it later.
Avoid overloading -- call it DraggableObject.
It assumes its arg has move method, etc.
"""

from math import pi

from exprs.Overlay import Overlay

from exprs.Rect import Rect

from exprs.transforms import Translate, RotateTranslate

from exprs.Highlightable import Highlightable

from exprs.DisplayListChunk import DisplayListChunk

from exprs.demo_MT import node_name #e really this belongs in a file which defines ModelTreeNodeInterface

from geometry.VQT import V, Q
from geometry.VQT import norm
from geometry.VQT import cross
from geometry.VQT import vlen
from utilities.constants import blue, white, ave_colors

from exprs.Exprs import call_Expr, LvalueFromObjAndAttr, format_Expr, V_expr, neg_Expr
from exprs.Boxed import Boxed
from exprs.If_expr import If
from exprs.Center import TopLeft, Center
from exprs.clipping_planes import Clipped, clip_to_right_of_x0, clip_below_y0
from exprs.ExprsConstants import StubType, StateRef, Vector, Quat, ORIGIN
from exprs.widget2d import Widget
from exprs.instance_helpers import DelegatingInstanceOrExpr, ModelObject
from exprs.attr_decl_macros import Arg, Option, State, Instance
from exprs.__Symbols__ import Anything, _self, _my

from exprs.DragBehavior import SimpleDragBehavior

debug070209 = True # turn on debug prints related to drags and clicks, and "click to toggle self.selected" test-kluge

# ==

###e refile WarpColors etc

ColorFunction = StubType

class WarpColors(DelegatingInstanceOrExpr):
    """#doc"""
    delegate = Arg(Widget) #e really Drawable or so
    warpfunc = Arg(ColorFunction) #e also might need hashable data specifying what it does, as an attr of it or another arg
    def draw(self):
        #e temporarily push warpfunc onto the front of a sequence of functions in a composition
        # which forms the glpane's overall color-warping function
        # (front means first run by fix_color, when it turns specified colors into drawn colors)
        #
        # (this assumes there are no GL state variables that do good-enough color-warping --
        #  if there are, it would be much better & more efficient to use them --
        #  but other things will end up needing this scheme)
        glpane = self.env.glpane
        old_warpfuncs = getattr(glpane, '_exprs__warpfuncs', None) # note: attr also used in DisplayListChunk and fix_color method
        glpane._exprs__warpfuncs = (self.warpfunc, old_warpfuncs) # temporary
            #e also modify a similar sequence of hashable func-effect data -- unless presence of any funcs turns off all displists
            # (we'll do that to start with, since simplest)
        try:
            self.drawkid( self.delegate)
        finally:
            glpane._exprs__warpfuncs = old_warpfuncs
        return
    pass

# ==

# [old cmt:]
### TODO: DraggableObject should ask the obj when it prefers to be moved (eg so other objs know its abs location) --
# never; only at file save or some other kind of update; at end of drag; continuously.
# ('m not sure things in that scheme are divided up quite right -- its model coords may need to update continuously regardless...
# or at least that may be a different Q than whether a graphical delegate inside DraggableObj wants that.)

#### NOTE [070318]: DraggableObject will be refactored soon. Its drag event handling methods (on_*) need to be moved into
# separate DragBehaviors, one for translate (i.e. SimpleDragBehavior) and one for rotate,
# or maybe into a fancier DragBehavior which delegates to one or the other of those,
# and also lets us know whether any on_drags occurred so we can do selection behavior in on_release if not.
# See also: other uses of any DragBehavior.

class DraggableObject(DelegatingInstanceOrExpr):
    """DraggableObject(obj) is a wrapper which makes any model object draggable (###doc the details),
    and also helps provides a context menu specific to obj.
    [##e It may be extended to make obj click-selectable or even region-selectable, at the proper times, too.]
       WARNING: Experimental -- API/organization will surely change,
    integrating not only rotation, but click to select, etc.
    The resulting wrapper will typically be applied by model->view macros.
       In fact, it's more complicated than that: the selection-click controller will wrap single objects,
    but the draggability wrapper is more likely to be organized something like this,
    where the named localvars refer to sets whose membership depends on selection:
      visibles = DisplayListChunk(fixed_stuff) + distortedly_moving_stuff +
        DraggableObject(DisplayListChunk(dragging_as_a_unit_stuff)).
    The distortedly_moving_stuff includes things like external bonds between fixed and being-dragged atoms,
    which have to stretch in individual ways during the drag.
    """
    # args
    obj = Arg(ModelObject)

    # options
    #e selectable = Option(bool, True, doc = "whether to let this object be click-selectable in the standard way") [see selected]
    rotatable = Option(bool, True, doc = "whether to let this object rotate about its center using MMB/Alt/Option drags")
        # This is intended to implement an initial subset of the "New motion UI" [070225 new feature]
        # [###e default will change to False after testing]
        # WARNING: as an optim, we might require that this be True initially, or even always (i.e. be a constant),
        # if it will ever be True during the Instance's lifetime -- not sure. If so, this requirement must at least be documented,
        # and preferably error-detected. ###FIX (if we do require that)
    # experimental kluge 070314
    _kluge_drag_handler = Option(Anything, _self, doc = "object to receive our on_press/on_drag/on_release events, in place of _self")

    # state
    selected = State(bool, False) ###KLUGE test stub, only set when debug070209
    translation = Option(Vector, V(0,0,0), #070404
                      doc = "initial translation [WARNING: might merge with misnamed self.motion (a State attr) to make a StateOption]")
    motion = State(Vector, _self.translation) # publicly visible and settable (but only with =, not +=).
        ##e rename to translation? (by making it a StateOption)
        ##e (or deprecate the concept of StateOption but make any State settable initially by a special option not just with same name?
        ##   eg either initial_attr or initial_data = [something with dict or attr access to the data] ??)
        ##e NOTE [070404]: I miscoded translation as Arg rather than Option, and said StateArg rather than StateOption in docstring,
        # though intending only named uses of it -- is this evidence that Arg / Option / Parameter should be the same,
        # that Option should be the default meaning, and positional arglists should be handled differently and as an extra thing
        # (eg like the old _args feature -- which leads to clearer code when subclassing)?? Guess: quite possibly, but needs more thought.
        # WARNING: use of += has two distinct bugs, neither error directly detectable:
        # - changes due to += (or the like) would not be change tracked.
        #   (But all changes to this need to be tracked, so our drawing effects are invalidated when it changes.)
        # - value might be a shared Numeric array -- right now use of = to set this doesn't copy the array to make us own it.
    rotation = State(Quat, Q(1,0,0,0)) #070225 new feature -- applied around object center

    # experiment 070312: works (see test_StateArrayRefs_2) ###doc ##e clean up ##k is it making the usual case slow in a significant way??
    delta_stateref = Option(StateRef, call_Expr( LvalueFromObjAndAttr, _self, 'motion'), doc = "#doc")
    use_motion = delta_stateref.value

    # geometric attrs should delegate to obj, but be translated by motion as appropriate.
    ##e Someday we need to say that in two ways:
    # - the attrs in the "geometric object interface" delegate as a group (rather than listing each one of them here)
    # - but when they do, they get passed through a change-of-coords boundary, and they know their own coordsystems,
    #   so the right thing happens.
    # But for now we have no way to say either thing, so we'll add specific formulas for specific attrs as needed. [070208]
    ##e Note that before the obj types know how to translate due to type, the interface (which knows the attrs indivly)
    # could know it. So, delegation of all attrs in an interface can be done by special glue code which also knows
    # how to transform them in useful ways, by knowing about those attrs and what transforms are useful.
    # This is useful enough to keep, even once its default transforms can come from declared attr types &
    # values knowing their coordsys. It adds value to that since interfaces can always know special cases about specific attrs.

    if 0:
      # update 070209 late: try doing this in Translate below, with the other involved exprs delegating as usual... ####k
      center = obj.center + motion
      # following comments are from when the above was 'if 1' a day or two ago -- still relevant since general [##e refile??]:

        # Problem: won't work for objs with no center! Solution for now: don't try to eval the self attr then.
        # Not perfect, since what ought to be AttributeError will turn into some other exception.
        ##e One better solution would involve declared interfaces for obj, and delegation of all attrs in interfaces
        # of a certain kind (geometric), so if obj met more interfaces and had more attrs, those would be included,
        # but if not, we would not have them either.
        ##e Or alternatively, we could provide an easy way to modify the above formula
        # to specify a condition under which center should seem to exist here, with that cond being whether it exists on obj.
        ### A potential problem with both solutions: misleasing AttributeError messages, referring to self rather than obj,
        # would hurt debugging. So we probably want to reraise the original AttributeError in cases like that, whatever
        # the way in which we ask for that behavior. That means one construct for "passing along attr missingness",
        # but *not* a composition of one construct for saying when this attr is there, and one for asking whether another is.

        # Note: can't we delegate center (& other geometry) through the display delegate below, if Highlightable passes it through
        # and Translate does the coordinate transformation? ###e

    # appearance

    obj_name = call_Expr( node_name, obj) #070216
        # Note: node_name is used in MT_try2; it's better than using _e_model_type_you_make (for our use in sbar_text, below).
        # BTW, node_name is a helper function associated with ModelTreeNodeInterface (informal so far).
        #
        # If you want to wrap an object with extra info which specifies its node_name, use ... what? ###k hmm, I forget if there
        # is a way partway through being implemented...
        # maybe WithAttributes( Center(Rect(0.4, 0.4, green)), mt_name = "green rect #n" )... i guess yes, ### TRY IT
        # should clean this situation up, use Adaptor term for that pattern
        # of interface conversion, etc... [070404 updated comment]

        # (Note [070216]: I had a bug when I had a comma after the above def. This made obj_name, included directly in another expr,
        #  turn into a singleton tuple of the call_Expr value, but when included as _self.obj_name (normally equivalent to obj_name),
        #  turn into something else (since eval of a tuple must not descend inside it -- guess, might have been a tuple_Expr).
        #  I'm not sure how to detect this error except to stop permitting tuple(expr) to be allowed as abbrev for a tuple_Expr --
        #  which seems too inconvenient -- or to figure out a way for the formula scanner to detect it (and make it illegal as the
        #  rhs of an assignment into a class namespace -- probably ok to make illegal). ##DOIT sometime)

    obj_drawn = If( selected,
                    Overlay( obj, Rect(1,1,blue)), ##### WRONG LOOK for selected, but should work [070209]
                          #BUG: Rect(1,lightblue) is gray, not light blue -- oh, it's that failure to use type to guess which arg it is!
                    obj
                 )

    sbar_text_for_maybe_selected = If( selected, " (selected)", "")

    delegate = Highlightable(
        # Note 070317: since Highlightable is outside of RotateTranslate, its coordsys doesn't change during a drag,
        # thus avoiding, here in DraggableObject, the bug that came up in the first implem of DraggablyBoxed,
        # whose highlightable rectframe was moving during the drag, but was also being used to supply the coordsys
        # for the drag events. This bug is actually in SimpleDragBehavior above, and the fix will be confined to that class.
        #
        # plain appearance
        RotateTranslate( obj_drawn, rotation, use_motion),
        # hover-highlighted appearance (also used when dragging, below)
        highlighted = RotateTranslate(
            DisplayListChunk(
                # This inner DisplayListChunk, in theory, might help make up for current implem of disabling them inside WarpColors...
                # in my tests, it didn't make a noticeable difference (probably since obj is fast to draw). [070216 2pm]
                #
                # Note: if obj has its own DisplayListChunk, does that notice the value of whatever dynenv var is altered by WarpColors??
                # We'll have to make it do so somehow -- perhaps by altering the displist name by that, or turning off displists due to it.
                # For this initial implem [070215 4pm], we did the latter.

                ## WarpColors( obj_drawn, lambda color: ave_colors( 0.3, white, color ) ), # whiten the color -- ugly
                ## WarpColors( obj_drawn, lambda color: yellow ), # "ignore color, use yellow" -- even uglier
                ## WarpColors( obj_drawn, lambda color: ave_colors( 0.2, white, color ) ), # whiten, but not as much -- less ugly
                WarpColors( obj_drawn, lambda color: ave_colors( 0.1, white, color ) ), # whiten, even less -- even less ugly [best so far]
                ## WarpColors( obj_drawn, lambda color: ave_colors( 0.2, gray, color ) ), # gray-end instead of whiten -- not quite as good
                ## WarpColors( obj_drawn, lambda color: (color[1],color[2],color[0]) ), # permute the hues...
            ),
            rotation, use_motion
         ),
        pressed = _my.highlighted, # pressed_in and pressed_out appearance
            ###BUG (when we gave pressed_in and pressed_out separately -- ###UNTESTED since then):
            # this pressed_out appearance seems to work for DNA cyls but not for draggable PalletteWell items! [070215 4pm]
        ## sbar_text = format_Expr( "Draggable %r", obj ),
            ##e should use %s on obj.name or obj.name_for_sbar, and add those attrs to ModelObject interface
            # (they would delegate through viewing wrappers on obj, if any, and get to the MT-visible name of the model object itself)
            ##e [Can we implem something like try_Expr( try1, try2, try3) which evals to the first one evalling without an exception??
            # But that doesn't seem safe unless you have to list the permissible exceptions (like in Python try/except).
            # The use of this here (temporary) would be to look for obj.name, then try a different format_Expr if that fails.
            # getattr(obj, 'name', dflt) would get us by, but would not as easily permit alternate format_Exprs in the two cases.]
##        # older highlighted or pressed_in appearance (not sure which it was before I inserted the args above this) -- zapping it 070216 late
##        If( eval_Expr(constant_Expr(constant_Expr(debug070209))),
##                ###e need option or variant of If to turn off warning that cond is a constant: warn_if_constant = False??
##                # also make the printed warning give a clue who we are -- even if we have to pass an option with the text of the clue??
##            Translate( Boxed(obj), motion),
##                #######070209 TEST THIS KLUGE -- note it does not include selected appearance
##                    # (but HL might incl it anyway? sometimes yes sometimes no, not sure why that would be -- ah, it depends on whether
##                    # mouse is over the moved object (which is silly but i recall it as happening in regular ne1 too -- ###BUG)
##                #e not good highlight form
##                ####BUG: the layout attrs (lbox attrs, eg bleft) are apparently not delegated, so the box is small and mostly obscured
##            Translate( obj, motion)
##         ),
        ## _obj_name = call_Expr(node_name, obj), #070216
            # that can't work yet -- it tries to define a new attr in an object (this Highlightable) from outside,
            # accessible in other option formulae as _this(Highlightable)._obj_name...
            # instead, I moved this def into _self (far above) for now.
        sbar_text = format_Expr( "%s%s (can be dragged)", obj_name, sbar_text_for_maybe_selected ), # revised 070216
            # This adds some info to sbar_text about what we can do with obj (drag, select, etc)...
            #e someday, maybe the dynenv wants to control how info of several kinds turns into actual sbar_text.
##        on_press = _self.on_press,
##        on_drag = _self.on_drag,
##        on_release = _self.on_release,
        on_press = _kluge_drag_handler.on_press,
        on_drag = _kluge_drag_handler.on_drag,
        on_release = _kluge_drag_handler.on_release,
        cmenu_maker = obj ###e 070204 experimental, API very likely to be revised; makes Highlightable look for obj.make_selobj_cmenu_items
    )
        ### DESIGN Q: do we also include the actual event binding (on_press and on_drag) -- for now, we do --
        # or just supply the Draggable interface for moving self.obj
        # and let the caller supply the binding to our internal "cmd" drag_from_to?? ###e

    # has Draggable interface (see demo_polygon.py for explan) for changing self.motion

    def _cmd_drag_from_to( self, p1, p2): #e rename drag_hitpoint_from_to? (in the Draggable Interface)
        """[part of the Draggable Interface; but this interface
        is not general enough if it only has this method -- some objects need more info eg a moving mouseray, screenrect, etc.
        Either this gets passed more info (eg a dragevent obj),
        or we keep the kluge of separate self dynenv queries (like for mousepoint and screenrect),
        or we provide glue code to look for this method but use more general ones if it's not there. ###e
        BTW, that interface is a myth at present; all actual dragging so far is done using on_press/on_drag/on_release,
        with this method at best used internally on some objs, like this one. [as of 070313]]
        """
        if self._delegate.altkey:
            assert 0, "should no longer be called"
##            ###KLUGE, just a hack for testing Highlightable.altkey [070224]; later, do rotation instead (per "New motion UI")
##            # (Is it also a ###KLUGE to detect altkey within this method, rather than caller detecting it and passing a flag
##            #  or calling a different method? YES.)
##            ## self.motion = self.motion + (p2 - p1) * -1
##            # change self.rotation... by a quat which depends on p2 - p1 projected onto the screen... or the similar mouse x,y delta...
##            ###KLUGE: assume DZ is toward screen and scale is standard....
##            # wait, ###BUG, we don't even have enough info to do this right, or not simply, starting from p1, rather than startpoint...
##            dx,dy,dz = p2 - p1
##            rotby = Q(p1,p2) ###WRONG but ought to be legal and visible and might even pretend to be a trackball in some cases and ways
##            self.rotation = self.rotation + rotby
##            # print "%r motion = %r rotation = %r" % (self, self.motion, self.rotation)
        else:
            ## self.motion = self.motion + (p2 - p1)
            self.delta_stateref.value = self.delta_stateref.value + (p2 - p1)
        return

    ##e something to start & end the drag? that could include flush if desired...

    # can push changes into the object

    def flush(self, newmotion = V(0,0,0)):
        self.delegate.move(self.use_motion + newmotion) ###k ASSUMES ModelObject always supports move (even if it's a noop) ###IMPLEM
            # note, nothing wrong with modelobjects usually having one coordsys state which this affects
            # and storing the rest of their data relative to that, if they want to -- but only some do.
        ## self.motion = V(0,0,0)
        self.delta_stateref.value = V(0,0,0)

    # if told to move, flush at the same time

    def move(self, motion):
        self.flush(motion)
        return

    # on_press etc methods are modified from demo_polygon.py class typical_DragCommand

    #e note: it may happen that we add an option to pass something other than self to supply these methods.
    # then these methods would be just the default for when that was not passed
    # (or we might move them into a helper class, one of which can be made to delegate to self and be the default obj). [070313]

    def on_press(self):
        point = self.current_event_mousepoint() # the touched point on the visible object (hitpoint)
            # (this method is defined in the Highlightable which is self.delegate)
        self.oldpoint = self.startpoint = point
        # decide type of drag now, so it's clearly constant during drag, and so decision code is only in one place.
        # (but note that some modkey meanings might require that changes to them during the same drag are detected [nim].)
        if self._delegate.altkey:
            self._this_drag = 'free x-y rotate'
                #e more options later, and/or more flags like this (maybe some should be booleans)
                ###e or better, set up a function or object which turns later points into their effects... hmm, a DragCommand instance!
                ##e or should that be renamed DragOperation??
            self._screenrect = (ll, lr, ur, ul) = self.screenrect( self.startpoint)
                # these points should be valid in our delegate's coords == self's coords
            self._dx = _dx = norm(lr - ll)
            self._dy = _dy = norm(ur - lr)
            self._dz = cross(_dx, _dy) # towards the eye (if view is ortho) (but alg is correct whether or not it is, i think)
                ###k check cross direction sign
            self._scale = min(vlen(lr - ll), vlen(ur - lr)) * 0.4
                # New motion UI suggests that 40% of that distance means 180 degrees of rotation.
                # We'll draw an axis whose length is chosen so that dragging on a sphere of that size
                # would have the same effect. (Maybe.)
            self._objcenter = self._delegate.center
            self.startrot = + self.rotation
        else:
            self._this_drag = 'free x-y translate'
        if debug070209:
            self.ndrags = 0
        return
    def on_drag(self):
        # Note: we can assume this is a "real drag", since the caller (ultimately a selectMode method in testmode, as of 070209)
        # is tracking mouse motion and not calling this until it becomes large enough, as the debug070209 prints show.
        oldpoint = self.oldpoint # was saved by prior on_drag or by on_press
        point = self.current_event_mousepoint(plane = self.startpoint)
        if debug070209:
            self.ndrags += 1
##            if (self.ndrags == 1) or 1:
##                print "drag event %d, model distance = %r, pixel dist not computed" % (self.ndrags, vlen(oldpoint - point),)
        if self._this_drag == 'free x-y rotate':
            # rotate using New motion UI
            #  [probably works for this specific kind of rotation, one of 4 that UI proposes;
            #   doesn't yet have fancy cursors or during-rotation graphics; add those only after it's a DragCommand]
            # two implem choices:
            # 1. know the eye direction and the screen dims in plane of startpoint, in model coords; compute in model coords
            # 2. get the mouse positions (startpoint and point) and screen dims in window x,y coords, compute rotation in eye coords,
            #   but remember to reorient it to correspond with model if model coords are rotated already.
            # Not sure which one is better.
            #   In general, placing user into model coords (or more precisely, into object local coords) seems more general --
            # for example, what if there were several interacting users, each visible to the others?
            # We'd want each user's eye & screen to be visible! (Maybe even an image of their face & screen, properly scaled and aligned?)
            # And we'd want their posns to be used in the computations here, all in model coords.
            # (Even if zoom had occurred, which means, even the user's *size* is quite variable!)
            #   I need "user in model coords" for other reasons too, so ok, I'll do it that way.
            #
            # [Hey, I might as well fix the bug in current_event_mousepoint which fakes the center of view, at the same time.
            # (I can't remember its details right now, but I think it assumed the local origin was the cov, which is obviously wrong.)
            # (But I didn't look at that code or fix that bug now.)]
            vec = point - self.startpoint
            uvec = norm(vec) #k needed??
            axisvec = cross(self._dz, uvec) # unit length (suitable for glRotate -- but we need to use it to make a quat!)
            axisvec = norm(axisvec) # just to be sure (or to reduce numerical errors)
            scale = self._scale
            draw_axisvec = axisvec * scale #e times some other length constant too?
            center = self._objcenter
            self.axisends = (center - axisvec, center + axisvec) # draw a rotation axis here ###e
            self.degrees = degrees = vlen(vec) / scale * 180.0 # draw a textual indicator with degrees (and axisvec angle too) ###e
                ###e or print that info into sbar? or somewhere fixed in glpane? or in glpane near mouse?
            # now set self.rotation to a quat made from axisvec and degrees
            theta = degrees / 360.0 * 2 * pi
            # print "axisvec %r, degrees %r, theta %r" % (axisvec ,degrees,theta)
            rot = Q(axisvec, theta)
            self.rotation = self.startrot + rot # note use of self.startrot rather than self.rotation on rhs
                # avoid += to make sure it gets changed-tracked -- and since it would be the wrong op!

        elif self._this_drag == 'free x-y translate':
            self._cmd_drag_from_to( oldpoint, point) # use Draggable interface cmd on self
        else:
            assert 0
        self.oldpoint = point
        return
    def on_release(self):
        #e here is where we'd decide if this was really just a "click", and if so, do something like select the object,
        # if we are generalized to become the wrapper which handles that too.
        if debug070209:
            if not self.ndrags:
                # print "release (no drags)" # ie a click
                self.selected = not self.selected ###KLUGE test stub
            else:
                pass # print "release after %d drags" % self.ndrags
            self.ndrags = 0
        pass

    pass # end of class DraggableObject

class DraggablyBoxed(Boxed): # 070316; works 070317 [testexpr_36] before ww,hh State or resizable, and again (_36b) after them
    # inherit args, options, formulae from Boxed
    thing = _self.thing ###k WONT WORK unless we kluge ExprsMeta to remove this assignment from the namespace -- which we did.
        ###e not sure this is best syntax though. attr = _super.attr implies it'd work inside larger formulae, but it can't;
        # attr = Boxed.attr might be ok, whether it can work is not reviewed; it too might imply what _super does, falsely I think.
    extra1 = _self.extra1
    borderthickness = _self.borderthickness
    rectframe = _self.rectframe # a pure expr
    # new options
    resizable = Option(bool, False, doc = "whether to make it resizable at lower right")
        # works 070317 10pm (testexpr_36b) except for a few ###BUGS [updated info 070318 7pm]:
        # + [fixed] the wrong corner resizes (top right) (logic bug)
        # + [fixed] resizer doesn't move (understood -- wrong expr for its posn; commented below)
        # - negative sizes allowed (missing feature - limit the drag - need new DragBehavior feature)
        # - no clipping to interior of rectframe (missing feature - draw something clipped)
        # - perspective view ought to work, but entirely ###UNTESTED.
        # also, cosmetic bugs:
        # - resizer doesn't follow mouse in rotated coordsys, even in ortho view (though it's still useable).
        #   (This is not surprising -- we're using the wrong kind of DragBehavior as a simple kluge.)
        # - the resizer is ugly, in shape & color.
    clipped = Option(bool, False, doc = "###doc") #070322 new feature ### make True default after testing?
    # state
        # WARNING: due to ipath persistence, if you revise dflt_expr you apparently need to restart ne1 to see the change.
##    ww = State(Width, thing.width  + 2 * extra1) # replaces non-state formula in superclass -- seems to work
##    hh = State(Width, thing.height + 2 * extra1)
##        # now we just need a way to get a stateref to, effectively, the 3-tuple (ww,hh,set-value-discarder) ... instead, use whj:
    whj = State(Vector, V_expr(thing.width  + 2 * extra1, - thing.height - 2 * extra1, 0)) #e not sure this is sound in rotated coordsys
    translation = State(Vector, ORIGIN)
    # override super formulae
    ww = whj[0] # seems to work
    hh = neg_Expr(whj[1]) # negative is needed since drag down (negative Y direction) needs to increase height
        # (guess: neg_Expr wouldn't be needed if we used an appropriate new DragBehavior in resizer,
        #  rather than our current klugy use of SimpleDragBehavior)
    # appearance
    rectframe_h = Instance( Highlightable(
        ## rectframe(bordercolor=green),####### cust is just to see if it works -- it doesn't, i guess i sort of know why
        ##bug: __call__ of <getattr_Expr#8243: (S._self, <constant_Expr#8242: 'rectframe'>)> with: () {'bordercolor': (0.0, 1.0, 0.0)}
        ##AssertionError: getattr exprs are not callable
        TopLeft(rectframe),
        #e different colored hover-highlighted version?? for now, just use sbar_text to know you're there.
        sbar_text = "draggable box frame", # this disappears on press -- is that intended? ###k
        behavior = SimpleDragBehavior(
            # arg1: the highlightable
            _self.rectframe_h,
            # arg2: a write-capable reference to _self.translation
            ## fails - evalled at compile time, not an expr: LvalueFromObjAndAttr( _self, 'translation'),
                ###BUG: why didn't anything complain when that bug caused the state value to be an add_Expr, not a number-array?
            call_Expr( LvalueFromObjAndAttr, _self, 'translation'),
                #e alternate forms for this that we might want to make work:
                #  - getattr_StateRef(_self, 'translation') # simple def of the above
                #  - StateRef_for( _self.translation ) # turns any lvalue into a stateref! Name is not good enough, though.
         )
     ))
    resizer = Instance( Highlightable(
        Center(Rect(extra1, extra1)), #e also try BottomRight
        highlighted = Center(Rect(extra1, extra1, white)),
        pressed = _my.highlighted,
        sbar_text = "resize the box frame",
        behavior = SimpleDragBehavior( _self.resizer, call_Expr( LvalueFromObjAndAttr, _self, 'whj') )
     ))
    ###BUG: in Boxed, rectframe comes first, so lbox attrs are delegated to it. We should do that too --
    # but right now we draw it later in order to obscure the thing if they overlap. With clipping we won't need that --
    # but without clipping we will. If the latter still matters, we need a version of Overlay with delegation != drawing order,
    # or, to delegate appearance and layout to different instances ourselves. (Or just to define new formulae for lbox -- easiest.) #e
    drawme = Instance( Overlay(
        If( clipped,
            Clipped(thing, planes = [call_Expr(clip_to_right_of_x0, - thing.bleft - extra1 + ww - borderthickness ),
                                         # note: the (- borderthickness) term makes the clipping reach exactly
                                         # to the inner rectframe edge. Without it, clipping would reach to the outer edge,
                                         # which for 3d objects inside the frame can cause them to obscure it.
                                         # (Other interesting values are (- extra1) and (- borderthickness/2.0),
                                         #  but they both look worse, IMHO.)
                                     call_Expr(clip_below_y0, thing.btop + extra1 - hh + borderthickness )
                                    ]),
            thing,
         ),
        Translate( rectframe_h, V_expr( - thing.bleft - extra1, thing.btop + extra1) ),
        If( resizable,
            ## Translate( resizer, V_expr( thing.bright + extra1, - thing.bbottom - extra1))
                ###WRONG - this posn is fixed by thing's lbox dims, not affected by ww, hh;
                # will the fix be clearer if we use a TopLeft alignment expr?
                # It'd be hard to use it while maintaining thing's origin for use by external alignment --
                # but maybe there's no point in doing that.
            Translate( resizer, V_expr( - thing.bleft - extra1 + ww, thing.btop + extra1 - hh))
         )
     ))
    _value = Translate( drawme, ## DisplayListChunk( drawme), ###k this DisplayListChunk might break the Highlightable in rectframe_h #####
                        translation
                       )
    pass # end of class DraggablyBoxed

# examples

## testexpr_31 = DraggableObject(Rect())

# end
