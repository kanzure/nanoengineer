"""
pallettes.py

$Id$
"""

from basic import *
from basic import _self

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable

import world
reload_once(world)
from world import World

import Boxed
reload_once(Boxed)
from Boxed import Boxed

import draggable
reload_once(draggable)
from draggable import DraggableObject

class PalletteWell(DelegatingInstanceOrExpr):
    """A place in the UI which can make copies of its expr for dragging to whereever you want [not fully working yet]
    """
    # experimental, really a stub, 070212 -- but sort of works! (as tested in dna_ribbon_view.py)
    expr = ArgExpr(Anything) #e not really Anything, but some interface ##e should really be StateArg

    world = Arg(World) ###e find in env, instead?? maybe not, since in typical cases we might rather make in some parent in
        # the model anyway, which depends on which kind of obj we are and which pallette we're in...
        # maybe we even need a make-function to be passed in.

    
    _what_to_make = DraggableObject(_self.expr)
        ##e rename DraggableObject -> Draggable? I misrecalled it as that... and "object" is arguably redundant.
    
    _newobj = State(Anything, None) # set internally to an object we create during _self.on_press
    
    delegate = Highlightable(
        Boxed(expr, borderthickness = 2 * PIXELS), ###BUG: fails with exprs that don't have bleft, with a very hard to decipher exception
        Boxed(expr, borderthickness = 2 * PIXELS, bordercolor = blue),
        expr,
        on_press = _self.on_press,
        on_drag = _newobj.on_drag,
        on_release = _newobj.on_release,
    )

    def on_press(self):
        self._newobj = self.world.make_and_add( self._what_to_make) ##e type option from _self option?
            ###e UI DESIGN FLAW: we should probably not actually make the object until the drag starts...
            # better, make something now, but only a fake, cursor-like object (not placed in the model or its tree)
            # (maybe a thumbnail image made from expr? maybe use PixelGrabber on self, to get it?? #e)
            # and only make a real model object when the drag *ends* (in a suitable mouse position -- otherwise cancel the make).
            ###BUG: this seems to be so slow, and takes time prop to number of objs in world or so (at least in other context of dna cyls),
            # that I suspect that whenever we make one object we have to remake displists (or something else timeconsuming) for all the
            # existing objects. probably a hypothetical bug mentioned in other comments, of inappropriate change tracking during commands,
            # or usage tracking of make-index-counter that should not be tracked. ###FIX -- important
        point_in_newobj_coords = self._newobj.current_event_mousepoint(plane = ORIGIN) ##### try this
        # print "point_in_newobj_coords is",point_in_newobj_coords ######
        ## point = self.current_event_mousepoint(plane = ORIGIN) ###KLUGE: use ORIGIN (which we know) for center of view (which we don't)
        # print "pallette.on_press got this point",point # this shows that it's in self-local coords -- how to ask for World coords??
        ## self._newobj.motion = point ###WRONG COORDS, and also a KLUGE since it centers new obj on mouse, offsetting it from sample
        self._newobj.motion = point_in_newobj_coords # this actually works!
            ###BUG (untested): I bet it would not work in perspective view, unless we corrected the plane, then reasked for point.
            ### UI DESIGN FLAW: the new obj is obscured, and there is no visual indication you "grabbed it", tho you did.
            # (actually there is one, if you wait long enough and didn't happen to grab it right on the center! but it's subtle --
            #  and worse, it's arguably due to a bug.)
            ##e would box border color change help? or box "dissolve"?? (ie temporarily remove the box)
            ###e need sbar messages, some message that you grabbed it (which would mitigate the visual flaw above)
            #
            # older note: we need to reinterpret the mouse motion in a better plane than that of the pallette itself (UI near front),
            # and to create the object here... I guess if we just move it here and in the right plane, things should work --
            # but we might need to hide the pallette well (or make it translucent or not depth-writing)
            # or it will obscure the new object! There's also the issue of relative object size if it's at a different depth.
        self._newobj.on_press() # needed so its on_drag and on_release behave properly when we delegate to them above
        return
    pass

