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

import transforms
reload_once(transforms)
from transforms import Translate

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable, Button, print_Expr, _setup_UNKNOWN_SELOBJ


class DraggableObject(DelegatingInstanceOrExpr):
    """DraggableObject(obj) is a wrapper which makes any model object draggable (###doc the details).
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
    
    # options
    motion = State(Vector, V(0,0,0)) # publicly visible, probably not publicly changeable, but not sure -- why not let it be?
        # in case it is or in case of bugs, never modify it in place (using +=) -- assume it might be a shared Numeric array.
        # Note: this needs to be change/usage tracked so that our drawing effects are invalidated when it changes.
        #k is it? It must be, since State has to be by default.

    # appearance
    delegate = Highlightable(
        Translate( obj, motion),
        sbar_text = "Draggable",
        on_press = _self.on_press, on_drag = _self.on_drag
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
        return
    def on_drag(self):###UNFINISHED re plane issue
        oldpoint = self.oldpoint # was saved by prior on_drag and by on_press
        point = self.current_event_mousepoint(plane = self.startpoint)
        self._cmd_drag_from_to( oldpoint, point) # use Draggable interface cmd
        self.oldpoint = point
        self.env.glpane.gl_update() ###k needed? i hope not, but i'm not sure; guess: no, provided self.motion is change/usage tracked
        return
    def on_release(self):
        pass
    
    pass

# examples

## testexpr_31 = DraggableObject(Rect())

# end
