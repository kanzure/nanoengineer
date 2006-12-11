"""
$Id$

might be renamed or merged

note: transforms.py was split out of here, 061115
"""

from basic import *
from basic import _self

import transforms
reload_once(transforms)
from transforms import Translate

class Center(InstanceMacro): # probably not currently used; not sure if it was ever tested, but looks correct AFAIK [as of 061115]
    "Center(thing) draws as thing (a Widget2D [#e should make work for 3D too]), but is centered on the origin"
    # args
    thing = Arg(Widget2D)
    # internal formulas - decide how much to translate thing
    dx = (thing.bleft - thing.bright)/2.0
    dy = (thing.bbottom - thing.btop)/2.0
    # value
    ###k for now, use V_expr instead of V when it has expr args... not sure we can get around this (maybe redef of V will be ok??)
    _value = Translate(thing, V_expr(dx,dy,0)) # this translates both thing and its layout box ###k might not work with V(expr...)
    pass

# status of Center, 061111:
# - untested
# - bbox motion in translate is nim, might matter later, not much for trivial tests tho [but it works now anyway, 061115]
# [as of 061211 i think those were both resolved long ago -- should verify #k]

class AlignmentExpr(DelegatingInstanceOrExpr): # doesn't work yet, see below
    thing = Arg(Widget2D)
    dx = 0 # override in some subclasses
    dy = 0
    delegate = Translate(thing, V_expr(dx,dy,0))
    pass

class TopRight(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = - thing.bright
    dy = - thing.btop
    delegate = Translate(thing, V_expr(dx,dy,0))

class TopRight_buggy(AlignmentExpr): # with AlignmentExpr -- doesn't work yet
    dx = - _self.thing.bright
    dy = - _self.thing.btop ###BUG [061211] -- for some reason these don't seem to be inherited into the formula for delegate.
        # guess: ExprsMeta stores it, then stores these new ones, but doesn't know it needs to "revisit" that one (for delegate)
        # and remake it for subclass with revised dx/dy. (Ideally it would remake it afresh for each subclass, I guess... how hard??)
        # conclusion: debug that, but for now, don't use the AlignmentExpr superclass, just spell out each subclass.

class CenterRight(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = (thing.bleft - thing.bright)/2.0
    dy = - thing.btop
    delegate = Translate(thing, V_expr(dx,dy,0))

class BottomRight(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = - thing.bright
    dy = + thing.bbottom
    delegate = Translate(thing, V_expr(dx,dy,0))


class TopLeft(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = + thing.bleft
    dy = - thing.btop
    delegate = Translate(thing, V_expr(dx,dy,0))

class BottomLeft(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = + thing.bleft
    dy = + thing.bbottom
    delegate = Translate(thing, V_expr(dx,dy,0))


class Left(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = + thing.bleft
    delegate = Translate(thing, V_expr(dx,0,0))

class Right(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = - thing.bright
    delegate = Translate(thing, V_expr(dx,0,0))

class Top(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dy = - thing.btop
    delegate = Translate(thing, V_expr(0,dy,0))

class Bottom(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dy = + thing.bbottom
    delegate = Translate(thing, V_expr(0,dy,0))
# end
