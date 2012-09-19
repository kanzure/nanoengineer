# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
pallettes.py

$Id$

"""

from exprs.Highlightable import Highlightable

from exprs.world import World

from exprs.Boxed import Boxed

from exprs.draggable import DraggableObject

from utilities.constants import blue, green

from exprs.Exprs import or_Expr, format_Expr
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.attr_decl_macros import ArgExpr, Option, State
from exprs.ExprsConstants import PIXELS, ORIGIN
from exprs.__Symbols__ import Anything, _self

class PalletteWell(DelegatingInstanceOrExpr):
    """A place in the UI which can make copies of its expr for dragging to whereever you want [not fully working yet]
    """
    # experimental, really a stub, 070212 -- but sort of works! (as tested in dna_ribbon_view.py)
    expr = ArgExpr(Anything) #e not really Anything, but some interface ##e should really be StateArg

    world = Option(World) ###e find in env, instead?? maybe not, since in typical cases we might rather make in some parent in
        # the model anyway, which depends on which kind of obj we are and which pallette we're in...
        # maybe we even need a make-function to be passed in.
        # If it was an arg, it'd be natural as arg1 (since this is like a method on the world);
        # but since it might become a dynamic env var, I'll use an option for now.
        # If it was a dynamic var by default but could be some container obj, an option would be good for that too (renamed #e).

    type = Option(str, doc = "type of thing to tell world we're making [type, api subject to change]")
        ###BUG: passing type to world.make_and_add is nim
    what_to_make_nickname = or_Expr(type, "something") #e classname of expr, after burrowing? some other namelike attr of expr?
        # (note, hard to have that, unless expr is a new special Instance type of "makable" rather than a bare expr --
        #  and it probably ought to be. ##e)

    sbar_text = Option(str, format_Expr("make %s", what_to_make_nickname) )

    _what_to_make = DraggableObject(_self.expr)
        ##e rename DraggableObject -> Draggable? I misrecalled it as that... and "object" is arguably redundant.

    _newobj = State(Anything, None) # set internally to an object we create during _self.on_press

    delegate = Highlightable(
        Boxed(expr, borderthickness = 2 * PIXELS), # plain
            ###BUG: Boxed fails with exprs that don't have bleft, with a very hard to decipher exception
        Boxed(expr, borderthickness = 2 * PIXELS, bordercolor = blue), # highlight
        Boxed(expr, borderthickness = 2 * PIXELS, bordercolor = green), # [pressed] green signifies "going" (mainly, green != blue)

        on_press = _self.on_press,
        on_drag = _newobj.on_drag,
        on_release = _newobj.on_release,
        sbar_text = sbar_text ###e UI DESIGN: need to also pass sbar text (or a func to get it from selobj) for use during the drag
    )

    def on_press(self):
        # make a new object
        self._newobj = self.world.make_and_add( self._what_to_make)
            ##e also pass the type option, taken from a new _self option?
            ###e UI DESIGN FLAW: we should probably not actually make the object until the drag starts...
            # better, make something now, but only a fake, cursor-like object (not placed in the model or its tree)
            # (maybe a thumbnail image made from expr? maybe use PixelGrabber on self, to get it?? #e)
            # and only make a real model object when the drag *ends* (in a suitable mouse position -- otherwise cancel the make).

        if 'kluge 070328, revised 070401': ###e see also comments in class World, 070401
            self._newobj.copy_saved_coordsys_from( self.world._coordsys_holder )
        # start a drag of the new object; first figure out where, in world coordinates, and in the depth plane
        # in which you want the new object to appear (and move the object there -- without that it'll be at the origin)
        point_in_newobj_coords = self._newobj.current_event_mousepoint(plane = ORIGIN)
            ### LOGIC BUG: this seems to work, but it presumbly has this bug: in current implem, self._newobj's local coordsys
            # can't be available yet, since it's never been drawn! So it presumably gives out a debug message I've been seeing
            # ("saved modelview_matrix is None, not using it")
            # and uses global modelview coords, which happen to be the same in the current test (in dna_ribbon_view.py).
            ###KLUGE: use ORIGIN (which we know) in place of center of view (which we don't) -- only correct when no trackballing
        self._newobj.motion = point_in_newobj_coords
            ###KLUGE since it centers new obj on mouse, even if mousedown was not centered on sample obj
            ###BUG (confirmed): I bet the point would be wrong in perspective view, unless we first corrected the depth plane,
            # then reasked for point.
        # trying that 070217 -- But how to fix? To correct the plane, we need to flush the DraggableObject in self._newobj, at least,
        # before current_event_mousepoint is likely to use correct coords (actually I'm not sure -- ###TEST)
        # but we can't since not all objects define .move (need to ###FIX sometime).
        ## self._newobj.flush()
        # so try this even though it might not work:
##        point_in_newobj_coords_2 = self._newobj.current_event_mousepoint(plane = ORIGIN)
        ### but now, what do we do with this point???
        # print "debug note: compare these points:",point_in_newobj_coords, point_in_newobj_coords_2 # result: identical coords.
        # so it doesn't work and doesn't even make sense yet... i probably can't proceed until the logic bug above is fixed.
            # There's also the issue of different object size on-screen if it's shown at a different depth.
            # (Unless that could help us somehow, in showing the depth? doubtful.)
            ### UI DESIGN FLAWS: the new obj is obscured, and there is no visual indication you "grabbed it", tho you did.
            # (actually there is one, if you wait long enough and didn't happen to grab it right on the center! but it's subtle --
            #  and worse, it's arguably due to a bug.)
            ##e would box border color change help? or box "dissolve"?? (ie temporarily remove the box)
            # or we might need to hide the pallette well (or make it translucent or not depth-writing)
            ###e need sbar messages, some message that you grabbed it (which would mitigate the visual flaw above)
        self._newobj.on_press() # needed so its on_drag and on_release behave properly when we delegate to them above
        return
    pass # end of class PalletteWell

# end
