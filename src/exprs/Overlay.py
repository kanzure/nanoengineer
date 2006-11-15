"""
Overlay.py

$Id$
"""

from basic import *
from basic import _self
 
class Overlay(Widget2D, DelegatingMixin): #e remove '2D' so it can work in 3D too? if so, need type inference that also delegates??
    "Overlay has the size of its first arg, but draws all its args in the same place, with the same origin."
    # stub, work only with exactly two args (though we could make them optional, add 3 more, and then it would be useful enough)
    arg0 = Arg(Widget2D)
    delegate = _self.arg0 # needed by DelegatingMixin
    arg1 = Arg(Widget2D)
    args = list_Expr(arg0, arg1) # not sure if [arg0, arg1] would work, but I doubt it --
        ###e should make it work sometime, if possible (e.g. by delving inside all literal list ns-values in ExprsMeta)
    #e add an option to make each element slightly closer, maybe just as a depth increment? makes hover highlighting more complicated...
    def _init_instance(self):
        super(Overlay, self)._init_instance()
        if not ( len(self._e_args) == 2):
            print("Overlay is a stub which only works with exactly two args")
        # sanity checks 061114
        ##[tmp disabled to ensure old bug comes back when I do -- yes! See explan in Boxed._init_instance comment, rev 1.20.]
##        assert self.arg0._e_is_instance
        assert self.arg1._e_is_instance
##        assert self.args[0] is self.arg0
##        assert self.args[1] is self.arg1
        return
    def draw(self):
        for a in self.args[::-1]:
            #e We'd like this to work properly for little filled polys drawn over big ones.
            # We might need something like z translation or depth offset or "decal mode"(??) or a different depth test.
            # Different depth test would be best, but roundoff error might make it wrong...
            # This is definitely needed for overdrawing like that to work, but it's low priority for now.
            # Callers can kluge it using Closer, though that's imperfect in perspective mode (or when viewpoint is rotated).
            # But for now, let's just try drawing in the wrong order and see if that helps... yep!
            if a is None:
                printfyi("some Overlay arg is None") #k I guess this is possible; when type coercion works, decide if it should be
                continue # even for first arg -- but that being None would fail in other ways, since it'd be our delegate
            a.draw() #e try/except
    pass # Overlay

#e see also FilledSquare
