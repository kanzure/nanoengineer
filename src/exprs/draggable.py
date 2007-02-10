"""
draggable.py

$Id$

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

from basic import *
from basic import _self

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import Rect
reload_once(Rect)
from Rect import Rect

import Boxed
reload_once(Boxed)
from Boxed import Boxed

import transforms
reload_once(transforms)
from transforms import Translate

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable, Button, print_Expr, _setup_UNKNOWN_SELOBJ

debug070209 = False # turn on debug prints related to drags and clicks, and "click to permanently set selected" test-kluge

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
      visibles = DisplistChunk(fixed_stuff) + distortedly_moving_stuff +
        DraggableObject(DisplistChunk(dragging_as_a_unit_stuff)).
    The distortedly_moving_stuff includes things like external bonds between fixed and being-dragged atoms,
    which have to stretch in individual ways during the drag.
    """
    # args
    obj = Arg(ModelObject)
    
    # state
    selected = State(bool, False) ###KLUGE test stub, only set when debug070209
    motion = State(Vector, V(0,0,0)) # publicly visible, probably not publicly changeable, but not sure -- why not let it be?
        # in case it is or in case of bugs, never modify it in place (using +=) -- assume it might be a shared Numeric array.
        # Note: this needs to be change/usage tracked so that our drawing effects are invalidated when it changes.
        #k is it? It must be, since State has to be by default.

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
    center = obj.center + motion
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
    delegate = Highlightable(
        Translate(
            If( selected,
                Overlay( obj, Rect(1,1,blue)), ##### WRONG LOOK for selected, but should work [070209]
                          #BUG: Rect(1,lightblue) is gray, not light blue -- oh, it's that failure to use type to guess which arg it is!
                obj
             ),
            motion
         ),
        ## sbar_text = format_Expr( "Draggable %r", obj ),
            ##e should use %s on obj.name or obj.name_for_sbar, and add those attrs to ModelObject interface
            # (they would delegate through viewing wrappers on obj, if any, and get to the MT-visible name of the model object itself)
            ##e [Can we implem something like try_Expr( try1, try2, try3) which evals to the first one evalling without an exception??
            # But that doesn't seem safe unless you have to list the permissible exceptions (like in Python try/except).
            # The use of this here (temporary) would be to look for obj.name, then try a different format_Expr if that fails.
            # getattr(obj, 'name', dflt) would get us by, but would not as easily permit alternate format_Exprs in the two cases.]
        If( debug070209, ###e need option or variant of If to turn off warning that cond is a constant: warn_if_constant = False??
                # also make the printed warning give a clue who we are -- even if we have to pass an option with the text of the clue??
            Translate( Boxed(obj), motion),
                #######070209 TEST THIS KLUGE -- note it does not include selected appearance
                    # (but HL might incl it anyway? sometimes yes sometimes no, not sure why that would be -- ah, it depends on whether
                    # mouse is over the moved object (which is silly but i recall it as happening in regular ne1 too -- ###BUG)
                #e not good highlight form
                ####BUG: the layout attrs (lbox attrs, eg bleft) are apparently not delegated, so the box is small and mostly obscured
            Translate( obj, motion)
         ),
        sbar_text = format_Expr( "Draggable %s", getattr_Expr( obj, 'name', format_Expr("%r", obj))),
        on_press = _self.on_press,
        on_drag = _self.on_drag,
        on_release = _self.on_release,
        cmenu_maker = obj ###e 070204 experimental, API very likely to be revised; makes Highlightable look for obj.make_selobj_cmenu_items
    )
        ### DESIGN Q: do we also include the actual event binding (on_press and on_drag) -- for now, we do --
        # or just supply the Draggable interface for moving self.obj
        # and let the caller supply the binding to our internal "cmd" drag_from_to?? ###e

    # has Draggable interface (see demo_polygon.py for explan) for changing self.motion
    
##    def _init_instance(self):
##        self.motion = V(0,0,0) # we own this and modify it in place
##            ###BUG: this implem would lose the dragpos whenever main inst is remade. Need to use State.
##        return
    
    def _cmd_drag_from_to( self, p1, p2):
##        self.motion += (p2 - p1)
        self.motion = self.motion + (p2 - p1)
        return
    
    ##e something to start & end the drag? that could include flush if desired...

    ##e something to highlight the obj, and say it can be moved in sbar or tooltip?
    # Guess: no -- in future, it can also be selected... so probably best to leave
    # highlighting/sbar entirely to caller, who combines Draggable with other features.

    # can push changes into the object
    
    def flush(self, newmotion = V(0,0,0)):
        self.delegate.move(self.motion + newmotion) ###k ASSUMES ModelObject always supports move (even if it's a noop) ###IMPLEM
            # note, nothing wrong with modelobjects usually having one coordsys state which this affects
            # and storing the rest of their data relative to that, if they want to -- but only some do.
        self.motion = V(0,0,0)

    # if told to move, flush at the same time
    
    def move(self, motion):
        self.flush(motion)
        return

    # modified from demo_polygon.py class typical_DragCommand
    def on_press(self):
        point = self.current_event_mousepoint() # the touched point on the visible object (hitpoint)
            # (this method is defined in the Highlightable which is self.delegate)
        self.oldpoint = self.startpoint = point
        if debug070209:
            self.ndrags = 0
        return
    def on_drag(self):
        # Note: we can assume this is a "real drag", since the caller (ultimately a selectMode method in testmode, as of 070209)
        # is tracking mouse motion and not calling this until it becomes large enough, as the debug070209 prints show.
        oldpoint = self.oldpoint # was saved by prior on_drag and by on_press
        point = self.current_event_mousepoint(plane = self.startpoint)
        if debug070209:
            self.ndrags += 1
            if (self.ndrags == 1) or 1:
                print "drag event %d, model distance = %r, pixel dist not computed" % (self.ndrags, vlen(oldpoint - point),)
        self._cmd_drag_from_to( oldpoint, point) # use Draggable interface cmd
        self.oldpoint = point
        self.env.glpane.gl_update() ###k needed? i hope not, but i'm not sure; guess: NO (provided self.motion is change/usage tracked)
        return
    def on_release(self):
        #e here is where we'd decide if this was really just a "click", and if so, do something like select the object,
        # if we are generalized to become the wrapper which handles that too.
        if debug070209:
            if not self.ndrags:
                print "release (no drags)" # ie a click
                self.selected = True ###KLUGE test stub
            else:
                print "release after %d drags" % self.ndrags
            self.ndrags = 0
        pass
    pass # end of class DraggableObject

# examples

## testexpr_31 = DraggableObject(Rect())

# end
