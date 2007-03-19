"""
test_statearray.py

$Id$

also contains test code for constrained dragging.
"""

from basic import *
from basic import _self

import Column
reload_once(Column)
from Column import SimpleColumn, SimpleRow

import Rect
reload_once(Rect)
from Rect import Rect

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable, SavedCoordsys

import Boxed
reload_once(Boxed)
from Boxed import Boxed

import Set
reload_once(Set)
from Set import Set ##e move to basic?

import draggable
reload_once(draggable)
from draggable import DraggableObject, DragBehavior

import images
reload_once(images)
from images import Image, IconImage, NativeImage, PixelGrabber

import controls
reload_once(controls)
from controls import ActionButton, PrintAction

import geometry_exprs
reload_once(geometry_exprs)
from geometry_exprs import Ray

import transforms
reload_once(transforms)
from transforms import Translate

def StateArrayRefs_getitem_as_stateref(statearrayrefs, index): #070313 renamed getitem_stateref to StateArrayRefs_getitem_as_stateref
    "#doc; args are values not exprs in the present form, but maybe can also be exprs someday, returning an expr..."
    if 'arg1 is a StateArrayRefs, not a StateArray':
        return statearrayrefs[index] # WARNING:
            # this only works due to a bug in the initial stub implem for StateArray --
            # now declared a feature due to its being renamed to StateArrayRefs -- in which self.attr
            # is valued as a dict of LvalForState objects rather than of settable/gettable item values,
            # and *also* because I changed LvalForState to conform to the new StateRefInterface so it actually
            # has a settable/gettable .value attribute.
            ##### When that bug in StateArray is fixed, this code would be WRONG if applied to a real StateArray.
            # What we need is to ask for an lval or stateref for that StateArray at that index!
            # Can we do that using getitem_Expr (re semantics, reasonableness, and efficiency)? ##k
    else:
        return StateRef_from_lvalue( getitem_Expr(statearrayrefs, index))
            ###IMPLEM this getitem_Expr behavior (proposed, not yet decided for sure; easy, see getattr_Expr for how)
            ###IMPLEM StateRef_from_lvalue if I can think of a decent name for it, and if I really want it around
    pass

# == example 1

class _color_toggler(DelegatingInstanceOrExpr):
    ###WRONGnesses:
    # - Q: shouldn't we be toggling a flag or enum or int, and separately mapping that to a color to show?
    #   A: Yes, unless we're for general raw color images -- but as a StateArray test this doesn't matter.
    # args
    color_ref = Arg(StateRef, doc = "stateref to a color variable") ###e can we tell StateRef what the value type should be?
    # appearance/behavior
    delegate = Boxed(
        Highlightable(
            Rect(1, 1, color_ref.value),
            on_press = Set( color_ref.value, call_Expr( _self.toggle_color, color_ref.value) ),
            sbar_text = "click to change color" #e give index in StateArray, let that be an arg? (if so, is it a fancy stateref option?)
         ),
        pixelgap = 0, #e rename -- but to what? bordergap? just gap? (change all gap options to being in pixels?)
        borderwidth = 1, ###BUG: some of these border edges are 2 pixels, depending on pixel alignment with actual screen
        bordercolor = black
     )
    def toggle_color(self, color):
        r,g,b = color
        return (b,r,g) # this permits toggling through the cyclic color sequence red, green, blue in that order
            #e or we could rotate that color-cube on the same diagonal axis but less than 1/3 turn,
            # to get more colors, if we didn't mind renormalizing them etc...
    pass

class test_StateArrayRefs(DelegatingInstanceOrExpr): ### has some WRONGnesses
    indices = range(10)
    colors = StateArrayRefs(Color, pink)
        #e i want an arg for the index set... maybe even the initial set, or total set, so i can iter over it...
        # NOTE: at least one dictlike class has that feature - review the ones in py_utils, see what _CK_ uses
    def _color_toggler_for_index(self, index):#e should we use _CV_ for this?? if not, it must be too hard to use!!!
            #k or is it that it defines a dict rather than a func, but we need a func in MapListToExpr?
        stateref = StateArrayRefs_getitem_as_stateref( self.colors, index )
        newindex = ('_color_toggler_for_index', index)
        return self.Instance( _color_toggler( stateref), newindex ) 
    delegate = MapListToExpr( _self._color_toggler_for_index, ###k _self needed??
                              indices,
                              KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleRow) )
    pass

# == example 2 -- full of kluges, but may finally work now; abandoned 070318 in favor of example 3

# maybe-partly-obs cmt:
###UNFINISHED in 3 ways (besides the same kluges as in example 1):
# - stores vectors not heights
# - constrain_delta nim, so they'll be dragged in all directions
# + [works now] delta_stateref nim,
#   so dragging these won't actually affect the elements of the StateArray yet, which pretty much bypasses the point.
#   ... done, works, and printit verifies that the statearray values actually change.
# even so, it runs (testexpr_35a).

# UNFINISHED aspects of xxx_drag_behavior:
# - its name
# + implem posn_from_params [done now]
# - the logic bug about self.motion -- ignoring for initial kluge test
# + closest_pt_params_to_ray [coded now]
# - how it fits into anything else -- not using DraggableObject is going to be best in the end,
#   but as initial kluge, just pass it in (wrapping DO as a delegator), and it might work.
# Now [cvs rev 1.15 & 1.16, sometime before 070318] it is supposedly coded enough to work using initial kluge test, but it doesn't work,
# but is making 2 highlightables and showing one and trying to drag the other (and failing). No idea why. [fixed now, see below]
# evidence is "saved modelview_matrix is None, not using it" and the reprs in that debug print and in the cmenu. Hmm. #BUG
# [note, an earlier version (not preserved except in earlier cvs revs of these same classes)
#  did partly work, which stored vectors and had no working constraint on the dragging.]
# Now I fixed that bug by passing _delegate not delegate to drag_handler; see code comment.

class xxx_drag_behavior(DragBehavior): # revised 070316; on 070318 removed comments that were copied into version _3
    """a drag behavior which moves the original hitpoint along a line,
    storing only its 1d-position-offset along the line's direction
    [noting that the hitpoint is not necessarily equal to the moved object's origin]
    [#doc better]
    """
    # args
    highlightable = Arg(DraggableObject) # kluge; revised 070316, delegate -> highlightable [works no worse than before [same bug as before]]
        # [but it's misnamed -- it has to be a DraggableObject since we modify its .motion] 
    posn_parameter_ref = Arg(StateRef, doc = "where the variable height is stored")
    constrain_to_line = Arg(Ray, Ray(ORIGIN, DY), doc = "the line/ray on which the height is interpreted as a position")
        # dflt_expr is just for testing #e remove it
    
    def current_event_mouseray(self):
        p0 = self.highlightable.current_event_mousepoint(depth = 0.0) # nearest depth ###k
        p1 = self.highlightable.current_event_mousepoint(depth = 1.0) # farthest depth ###k
        return Ray(p0, p1 - p0) #e passing just p1 should be ok too, but both forms can't work unless p0,p1 are typed objects...
    def on_press(self):
        self.startpoint = self.highlightable.current_event_mousepoint() # the touched point on the visible object (hitpoint)
        self.offset = self.startpoint - (ORIGIN + self.highlightable.motion) #k maybe ok for now, but check whether sensible in long run
        self.line = self.constrain_to_line + self.offset # the line the hitpoint is on (assuming self.motion already obeyed the constraint)
    def on_drag(self):
        # Note: we can assume this is a "real drag" (not one which is too short to count), due to how we are called.
        mouseray = self.current_event_mouseray()
##        self._cmd_drag_from_to( oldpoint, point) # use Draggable interface cmd on self
            # ie self.delta_stateref.value = self.delta_stateref.value + (p2 - p1)
        ## def drag_mouseray_from_to(self, oldray, newray): # sort of like _cmd_from_to (sp?) in other eg code
        ## "[part of an interface XXX related to drag behaviors]"
        k = self.line.closest_pt_params_to_ray(mouseray)
        if k is not None:
            # store k
            self.posn_parameter_ref.value = k ####e by analogy with DraggableObject, should we perhaps save this side effect until the end?
            # compute new posn from k
            self.highlightable.motion = self.constrain_to_line.posn_from_params(k) #e review renaming, since we are asking it for a 3-tuple
                ####### LOGIC BUG: what causes self.motion to initially come from this formula, not from our own state?
                # maybe don't use DraggableObject at all? [or as initial kluge, just let initial motion and initial height both be 0]
        return
    def on_release(self):
        pass
    pass # end of class xxx_drag_behavior

class _height_dragger(DelegatingInstanceOrExpr):
    # args
    #e coordsystem? for now let x/y be the way it spreads, z be the height
    height_ref = Arg(StateRef, doc = "stateref to a height variable")
    # appearance/behavior
    #e should draw some "walls" too, and maybe limit the height
    # note: the following sets up a cyclic inter-Instance ref ( drag_handler -> delegate -> drag_handler);
    # it works since the actual refs are symbolic (getattr_Expr(_self, 'attr'), not evalled except when used).
    drag_handler = Instance( xxx_drag_behavior( _self._delegate, height_ref, Ray(ORIGIN, DX) )) ### DX for initial test, then DZ
        # note: passing _self._delegate (not _self.delegate) fixed my "undiagnosed bug".
    delegate = DraggableObject(
        Image("blueflake.jpg"), ###e needs an option to be visible from both sides (default True, probably)
##        constrain_delta = _self.constrain_delta, ###IMPLEM constrain_delta in DraggableObject
##        delta_stateref = height_ref ###IMPLEM delta_stateref [done] (and rename it); and change this to make height_ref a number not vector;
            ##e and maybe include the constraint in that transform, since it seems implicit in it anyway. ####HOW in semantics?
            # ... = PropertyRef(DZ * height_ref.value, Set( height_ref.value, project_onto_unit_vector( _something, DZ ))
            # ... = TransformStateRef( height_ref, ... ) # funcs? or formula in terms of 1 or 2 vars? with a chance at solving it?? ##e
        _kluge_drag_handler = drag_handler
     )
##    def constrain_delta(self, delta):
##        not yet - called
##        return project_onto_unit_vector( delta, DZ)
    pass

class test_StateArrayRefs_2(DelegatingInstanceOrExpr): # testexpr_35a
    indices = range(4)
    ## heights = StateArrayRefs(Width, ORIGIN) ###KLUGE for now: this contains heights * DZ as Vectors, not just heights
    heights = StateArrayRefs(Width, 0.0)
    def _height_dragger_for_index(self, index):
        stateref = StateArrayRefs_getitem_as_stateref( self.heights, index )
            #e change to self.heights.getitem_as_stateref(index)? self.heights._staterefs[index]?? self.heights[index]???
        newindex = ('_height_dragger_for_index', index) 
        return self.Instance( _height_dragger( stateref), newindex )
    delegate = SimpleRow(
        MapListToExpr( _self._height_dragger_for_index, ###k _self needed??
                       indices,
                       KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleColumn) ),
                           #e SimpleGrid? 2d form of MapListToExpr?
        ActionButton( _self.printit, "button: print state") ###e idea: define on special attr, let UI assemble debug info viewer
     )
    def printit(self): #e can PrintAction do this for us?
        print [h.value for i,h in sorted_items(self.heights)] ###KLUGE, assumes they're StateRefs -- maybe just rename StateArray -> StateArrayRefs
    pass

# == example 3 

# 070318: now that DraggablyBoxed resizer works, I'll revise example 2 in some related ways,
# including using a saved_coordsys as in SimpleDragBehavior. This new example has the same intent
# as example 2, but cleaner code, and could entirely replace it once it works --
# but now they both work (except for different lbox effects) so for now I'll keep them both around.

class xxx_drag_behavior_3(DragBehavior): #070318 (compare to SimpleDragBehavior) ###e rename & refile when it works
    """a drag behavior which moves the original hitpoint along a line,
    storing only its 1d-position-offset along the line's direction
    [noting that the hitpoint is not necessarily equal to the moved object's origin]
    [#doc better]
    """
    # args [#e replace 'height' with 'posn_parameter' or 'posn_param' in these comments & docstrings]
    highlightable = Arg(Anything) ###e is there a way we can require that we're passed an Instance rather than making it ourselves?
        # I suspect that violating that caused the bug in example 2.
        # (A way that would work: a specialcase check in _init_instance.
        #  But I'd rather have an option on Arg to do that. require_already_instance?? Or ArgInstance? that latter invites confusion
        #  since it's not analogous to ArgExpr.)
    posn_parameter_ref = Arg(StateRef, doc = "where the variable height is stored")
    constrain_to_line = Arg(Ray, doc = "the line/ray on which the height is interpreted as a position")
        # note: the position of the height on this line is typically used as the position of the drawn movable object's origin;
        # we shouldn't assume the drag startpoint is on the line, since the drawn movable object might be touched at any of its points.
        ##e rename Ray -> MarkedLine? (a line, with real number markings on it) ParametricLine? (no, suggests they can be distorted/curved)
    range = Option(tuple_Expr, None, doc = "range limit of height")#nim
    ##e drag event object can be passed to us... as a delegate! [In recent code, it seems like the Highlightable is taking this role.]
        
    # (if this delegates or supers to something that knows all about the drag in a lower level way,
    #  then maybe it's not so bad to be getting dragevent info from self rather than a dragevent arg... hmm.
    #  An argument in favor of that: self is storing state related to one drag anyway, so nothing is lost
    #  by assuming some other level of self stores some other level of that state. So maybe we create a standard
    #  DragHandling object, then create a behavior-specific delegate to it, to which *it* delegates on_press etc;
    #  and we also get it to delegate state-modifying calls to some external object -- or maybe that's not needed
    #  if things like this one's stateref are enough. ##k)
    #
    # related: Maybe DraggableObject gets split into the MovableObject and the DragBehavior...

    # same as in SimpleDragBehavior: saved_coordsys & current_event_mousepoint
    
    # state:
    saved_coordsys = Instance( SavedCoordsys() ) # provides transient state for saving a fixed coordsys to use throughout a drag

    def current_event_mousepoint(self, *args, **kws): #e zap this and inline it, for clarity? or move it into DragBehavior superclass??
        return self.saved_coordsys.current_event_mousepoint(*args, **kws)

    def current_event_mouseray(self):
        p0 = self.current_event_mousepoint(depth = 0.0) # nearest depth ###k
        p1 = self.current_event_mousepoint(depth = 1.0) # farthest depth ###k
        return Ray(p0, p1 - p0) #e passing just p1 should be ok too, but both forms can't work unless p0,p1 are typed objects...

    def _C__translation(self): ### WARNING: used externally too -- rename to be not private if we decide that's ok ###e
        "compute self._translation from the externally stored height"
        k = self.posn_parameter_ref.value
        return self.constrain_to_line.posn_from_params(k) #e review renaming, since we are asking it for a 3-tuple
    
    def on_press(self):
        self.saved_coordsys.copy_from( self.highlightable) # needed before using current_event_mousepoint or current_event_mouseray
            # (since self.highlightable's coordsys changes during the drag)
        self.startpoint = self.current_event_mousepoint() # the touched point on the visible object (hitpoint)
        self.offset = self.startpoint - (ORIGIN + self._translation) #k maybe ok for now, but check whether sensible in long run
        self.line = self.constrain_to_line + self.offset # the line the hitpoint is on
    def on_drag(self):
        mouseray = self.current_event_mouseray()
        k = self.line.closest_pt_params_to_ray(mouseray)
        if k is not None:
            # store k, after range-limiting
            range = self.range # don't use the python builtin of the same name, in this method! (#e or rename the option?)
            if range is not None:
                low, high = range
                if low is not None and k < low:
                    k = low
                if high is not None and k > high:
                    k = high
            self.posn_parameter_ref.value = k ##e by analogy with DraggableObject, should we perhaps save this side effect until the end?
        return
    def on_release(self):
        pass
    pass # end of class xxx_drag_behavior_3

class _height_dragger_3(DelegatingInstanceOrExpr):
    # args
    height_ref = Arg(StateRef, doc = "stateref to a height variable")
    direction = Arg(Vector)
    sbar_text = Option(str, "_height_dragger_3")
    range = Option(tuple_Expr, None, doc = "range limit of height")
    # appearance/behavior
    #e should draw some "walls" too, and maybe limit the height
    drag_handler = Instance( xxx_drag_behavior_3( _self._delegate, height_ref,
                                                  ## Ray(ORIGIN, DX) # works
                                                  ## Ray(ORIGIN, DZ) # works, but only if you trackball it (as expected)...
                                                  ## Ray(ORIGIN, direction) # fails -- Ray is an ordinary class, not an expr! ###FIX
                                                  call_Expr(Ray, ORIGIN, direction), # this workaround fixes it for now.
                                                      # (in prior commit it didn't, but only because of a typo in the testexpr defs
                                                      #  in tests.py, which meant I passed DZ when I thought I passed DX.)
                                                  range = range
                            ))
        ### NOTE: drag_handler is also being used to compute the translation from the height, even between drags.
    delegate = Highlightable(
        Translate(
            Image("blueflake.jpg"), ###e needs an option to be visible from both sides (default True, probably)
            drag_handler._translation ###k ok?? only if that thing hangs around even in between drags, i guess!
                #e #k not sure if this code-commoning is good, but it's tempting. hmm.
         ),
        sbar_text = sbar_text,
        behavior = drag_handler
     )
    pass

class test_StateArrayRefs_3( DelegatingInstanceOrExpr): # testexpr_35b, _35c
    indices = range(3)
    heights = StateArrayRefs(Width, 0.0)
    direction = Arg(Vector, DX, "direction of permitted motion -- DZ is the goal but DX is easier for testing")
        ### DX for initial test (testexpr_35b), then DZ (testexpr_35c)
    range = Option(tuple_Expr, None, doc = "range limit of height")
    msg = Option(str, "drag along a line")
    def _height_dragger_for_index(self, index):
        stateref = StateArrayRefs_getitem_as_stateref( self.heights, index )
            #e change to self.heights.getitem_as_stateref(index)? self.heights._staterefs[index]?? self.heights[index]???
        newindex = ('_height_dragger_3_for_index', index) 
        return self.Instance( _height_dragger_3( stateref, self.direction,
                                                 sbar_text = "%s (#%r)" % (self.msg, index,),
                                                 range = self.range
                                                ), newindex )
    delegate = SimpleRow(
        MapListToExpr( _self._height_dragger_for_index, ###k _self needed??
                       indices,
                       KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleColumn) ),
                           #e SimpleGrid? 2d form of MapListToExpr?
        ActionButton( _self.printit, "button: print state") ###e idea: define on special attr, let UI assemble debug info viewer
     )
    def printit(self): #e can PrintAction do this for us?
        print [h.value for i,h in sorted_items(self.heights)] ###KLUGE, assumes they're StateRefs -- maybe just rename StateArray -> StateArrayRefs
    pass


# end
