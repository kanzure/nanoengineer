# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Center.py - alignment primitives

$Id$

might be renamed or merged

note: transforms.py was split out of here, 061115
"""

from exprs.transforms import Translate

from exprs.Exprs import V_expr
from exprs.attr_decl_macros import Arg
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.widget2d import Widget2D
from exprs.__Symbols__ import _self

# There are 15 non-noop combos of dx & dy formulae, but only 13 have simple names, due to X/Y ambiguity of Center...
# even so, I spell them out like this, partly since the resulting classes are more efficient
# than the easy implems of a general version which takes args for what to do with x & y independently.
# Maybe the missing ones could be called CenterX and CenterY? (They do nothing to the not-named coordinate.) Done.
# See testexpr_21e for a table of all of them.

# BTW they need docstrings; here is an old one for Center:
"Center(thing) draws as thing (a Widget2D [#e should make work for 3D too]), but is centered on the origin"

class TopRight(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = - thing.bright
    dy = - thing.btop
    delegate = Translate(thing, V_expr(dx,dy,0))

class CenterRight(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = - thing.bright
    dy = (thing.bbottom - thing.btop)/2.0
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

class CenterLeft(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = + thing.bleft
    dy = (thing.bbottom - thing.btop)/2.0
    delegate = Translate(thing, V_expr(dx,dy,0))

class BottomLeft(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = + thing.bleft
    dy = + thing.bbottom
    delegate = Translate(thing, V_expr(dx,dy,0))


class TopCenter(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = (thing.bleft - thing.bright)/2.0
    dy = - thing.btop
    delegate = Translate(thing, V_expr(dx,dy,0))

class Center(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = (thing.bleft - thing.bright)/2.0
    dy = (thing.bbottom - thing.btop)/2.0
    delegate = Translate(thing, V_expr(dx,dy,0))

class BottomCenter(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = (thing.bleft - thing.bright)/2.0
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


class CenterX(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dx = (thing.bleft - thing.bright)/2.0
    delegate = Translate(thing, V_expr(dx,0,0))

class CenterY(DelegatingInstanceOrExpr):
    thing = Arg(Widget2D)
    dy = (thing.bbottom - thing.btop)/2.0
    delegate = Translate(thing, V_expr(0,dy,0))

# == not yet working: a form with less duplicated code

class AlignmentExpr(DelegatingInstanceOrExpr): # doesn't work yet, see below
    thing = Arg(Widget2D)
    dx = 0 # override in some subclasses
    dy = 0
    delegate = Translate(thing, V_expr(dx,dy,0))
    pass

class TopRight_buggy(AlignmentExpr): # with AlignmentExpr -- doesn't work yet
    dx = - _self.thing.bright
    dy = - _self.thing.btop ###BUG [061211] -- for some reason these don't seem to be inherited into the formula for delegate.
        # guess: ExprsMeta stores it, then stores these new ones, but doesn't know it needs to "revisit" that one (for delegate)
        # and remake it for subclass with revised dx/dy. (Ideally it would remake it afresh for each subclass, I guess... how hard??)
        # conclusion: debug that, but for now, don't use the AlignmentExpr superclass, just spell out each subclass.
        # update, 080514: obvious in hindsight: when the delegate formula in AlignmentExpr is executed by Python,
        # dx is 0 so it might as well be defining delegate = Translate(thing, V_expr(0,0,0)).
        # So there is no fix without revising that definition or the defs of dx, dy.

# pre-061211 version of Center, also worked fine:
##class Center(InstanceMacro):
##    "Center(thing) draws as thing (a Widget2D [#e should make work for 3D too]), but is centered on the origin"
##    # args
##    thing = Arg(Widget2D)
##    # internal formulas - decide how much to translate thing
##    dx = (thing.bleft - thing.bright)/2.0
##    dy = (thing.bbottom - thing.btop)/2.0
##    # value
##    ###k for now, use V_expr instead of V when it has expr args... not sure we can get around this (maybe redef of V will be ok??)
##    _value = Translate(thing, V_expr(dx,dy,0)) # this translates both thing and its layout box ###k might not work with V(expr...)
##    pass

# end
