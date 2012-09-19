# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Overlay.py

@author: bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

"""

from exprs.TextRect import TextRect

from exprs.Rect import Spacer

from exprs.attr_decl_macros import Arg
from exprs.instance_helpers import InstanceOrExpr, DelegatingMixin
from exprs.widget2d import Widget2D
from exprs.Exprs import list_Expr, and_Expr, or_Expr

class Overlay(InstanceOrExpr, DelegatingMixin):
    "Overlay has the size of its first arg, but draws all its args in the same place, with the same origin."
    # Note: we can't inherit from Widget2D, or we'd fail to delegate
    # e.g. bright to self.delegate, and pick up the default value instead!
    # I'm not yet sure whether the proper fix is to handle those defaults in some other way
    # (e.g. as a last-resort delegate of some sort -- maybe we could say right here (to a fancier
    #  version of DelegatingMixin), if you don't find the attr in self.delegate, look in Widget2D).
    # See also comments in InstanceMacro, about the same issue for it.
    # [061210 grabbing SimpleColumn's scheme for permitting up to 10 args, though ArgList is nim]
    a0 = Arg(Widget2D, None) # so it's not a bug to call it with no args, as when applying it to a list of no elts [061205]
    a1 = Arg(Widget2D, None)
    a2 = Arg(Widget2D, None)
    a3 = Arg(Widget2D, None)
    a4 = Arg(Widget2D, None)
    a5 = Arg(Widget2D, None)
    a6 = Arg(Widget2D, None)
    a7 = Arg(Widget2D, None)
    a8 = Arg(Widget2D, None)
    a9 = Arg(Widget2D, None)
    a10 = Arg(Widget2D, None)
    a11 = Arg(Widget2D, None)
    args = list_Expr(a0,a1,a2,a3,a4,a5, a6,a7,a8,a9,a10, # could say or_Expr(a0, Spacer(0)) but here is not where it matters
                     and_Expr(a11, TextRect("too many args in Overlay"))
                     )

    delegate = or_Expr(a0, Spacer(0)) ## _self.a0 # needed by DelegatingMixin
##    args = list_Expr(arg0, arg1) # not sure if [arg0, arg1] would work, but I doubt it --
        ###e should make it work sometime, if possible (e.g. by delving inside all literal list ns-values in ExprsMeta)
    #e add an option to make each element slightly closer, maybe just as a depth increment? makes hover highlighting more complicated...
    def draw(self):
        args = self.args # this order is correct since we set glDepthFunc to GL_LEQUAL (not GL_LESS)
        for a in args:
            self.drawkid( a)
            #e We'd like this to work properly for little filled polys drawn over big ones.
            # We might need something like z translation or depth offset or "decal mode"(??).
            # [later 070404: "decal mode" is probably unrelated -- GL_DECAL is for combining a texture with a non-textured color/alpha,
            #  not related to using depth buffer when resulting textured object is drawn. Is "decal" used to mean anything else?? #k]
            # Different depth test would be best [done now -- GL_LEQUAL], but roundoff error might make it wrong...
            # This is definitely needed for overdrawing like that to work, but it's low priority for now.
            # Callers can kluge it using Closer, though that's imperfect in perspective mode (or when viewpoint is rotated).
            # [Or glDepthRange, now used for highlight drawing in GLPane as of 070921.]
    pass # Overlay

# obs cmt from when we mistakenly inherited from Widget2D:
# #e remove '2D' so it can work in 3D too? if so, need type inference that also delegates??
#e see also FilledSquare

# end
