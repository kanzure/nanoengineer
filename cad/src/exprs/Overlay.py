# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Overlay.py

$Id$

"""

from OpenGL.GL import GL_LESS

from exprs.reload import reload_once

import exprs.TextRect
reload_once(exprs.TextRect)
from exprs.TextRect import TextRect

import exprs.Rect
reload_once(exprs.Rect)
from exprs.Rect import Spacer

from exprs.attr_decl_macros import Arg
from exprs.instance_helpers import InstanceOrExpr, DelegatingMixin
from exprs.widget2d import Widget2D
from exprs.Exprs import list_Expr, and_Expr, canon_expr, or_Expr
from exprs.py_utils import printfyi

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
        if self.env.glpane.current_glDepthFunc == GL_LESS: #070117; note: assumes displists are compiled & used in the same state!
            args = self.args[::-1]
            printfyi("Overlay in reverse order (need to override standard_glDepthFunc in your new mode??)")
        else: # GL_LEQUAL
            args = self.args
        for a in args:
            #e We'd like this to work properly for little filled polys drawn over big ones.
            # We might need something like z translation or depth offset or "decal mode"(??) or a different depth test.
            # [later 070404: "decal mode" is probably unrelated -- GL_DECAL is for combining a texture with a non-textured color/alpha,
            #  not related to using depth buffer when resulting textured object is drawn. Is "decal" used to mean anything else?? #k]
            # Different depth test would be best, but roundoff error might make it wrong...
            # This is definitely needed for overdrawing like that to work, but it's low priority for now.
            # Callers can kluge it using Closer, though that's imperfect in perspective mode (or when viewpoint is rotated).
            # But for now, let's just try drawing in the wrong order and see if that helps... yep!
##            if a is None:
##                continue # even for first arg # note: no longer needed, now that self.drawkid treats None as drawing nothing
            self.drawkid( a) ## a.draw() #e try/except
    pass # Overlay

# obs cmt from when we mistakenly inherited from Widget2D:
# #e remove '2D' so it can work in 3D too? if so, need type inference that also delegates??
#e see also FilledSquare
