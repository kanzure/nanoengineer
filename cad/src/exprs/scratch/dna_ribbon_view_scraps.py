# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
dna_ribbon_view_scraps.py

$Id$

outtakes from dna_ribbon_view.py which are importable now [070201] ###UNTESTED
and might be worth finishing and testing, or salvaging useful code/ideas from.

Any old code from demo_dna-outtakes.py that was still in dna_ribbon_view.py
is now only here.
"""

# ==

from basic import *
from basic import _self

from Overlay import Overlay

from TextRect import TextRect

from OpenGL.GL import * #e move what needs this into draw_utils

from dna_ribbon_view import * ###e reloadable -- needed at least for IorE, probably more
from utilities import debug_flags
# ==

Corkscrew = Stub
class Ribbon_oldcode_for_edges(Corkscrew): # generates a sequence of rects (quads) from two corkscrews, then draws a ribbon using them
    def draw(self, **mods):
        if 1:
            # draw the ribbon-edges; looks slightly better this way in some ways, worse in other ways --
            # basically, looks good on egdes that face you, bad on edges that face away (if the ribbons had actual thickness)
            # (guess: some kluge with lighting and normals could fix this)
            Corkscrew.draw(self, color = interior_color)
            if 0:
                glTranslate(offset, 0,0)
                Corkscrew.draw(self, color = interior_color) ### maybe we should make the two edges look different, since they are (major vs minor groove)
                glTranslate(-offset, 0,0)

# ==

##class Ribbon2(Ribbon): # draws, using the same params needed for a corkscrew, a pair of ribbons that look like a DNA double helix
##    # radius, axis, turn, n
##    pass

class Rotate(IorE):#e refile with Translate -- in fact, reexpress it as interposing on draw and lbox methods, ignoring the rest...
        # (as discussed extensively elsewhere, not sure if in code or notesfile or paper, 1-3 days before 070131)
    # needs to transform other things too, like lbox -- same issue as Translate
    thing = Arg(Widget)
    angle = Arg(float)
    axis = ArgOrOption(Vector, DZ) ###e or LineSegment, then do translate too
    ###e should normalize axis and check for 0,0,0
    def draw(self):
        glRotatef(angle, axis[0], axis[1], axis[2]) # angle is in degrees, I guess
        self.drawkid( self.thing) ## self.thing.draw(self)
        glRotatef(-angle, axis[0], axis[1], axis[2]) # might be optional, I forget the semantics of things like Overlay ###k
    pass

call_lambda_Expr = Stub
lambda_Expr = Stub
ShareInstances = Stub

class Ribbon2_try1(Macro): ###e perhaps needs some axis -> axisvector
    """Ribbon2(thing1, thing2) draws a thing1 instance in red and a thing2 instance in blue.
    If thing2 is not supplied, a rotated thing1 instance is used for it, and also drawn in blue.
    """
    angle = 150.0
    arg1 = ArgExpr(Widget) # but it better have .axis if we use it to make arg2! BUT if it's an expr, how can it have that yet?
        #### are some attrs of exprs legal if they don't require instanceness to be computed, depending on the type?
        #### (typical for geometric stuff) or only if this kind of expr is "born an instance"? But if it's highlightable, it's not...
    # but it might have an axis anyway... but do we really mean arg2's axis? no... maybe a special instance of arg1 used in this expr alone? yes.
    _arg1_for_arg2 = Instance(arg1) # only used if arg2's dflt expr is needed; has to be an instance so we can ask for its .axis
        #e maybe this requirement can be relaxed since.axis does not depend on self?? not sure -- anyway it might... since it
        # might depend on local coords -- no, it's defined to be rel to local coords, so it doesn't.... ###k
    arg2 = ArgExpr(Widget, Rotate( _arg1_for_arg2, angle, _arg1_for_arg2.axis)) # in old code we passed a single Ribbon, used it twice
    delegate = Overlay(arg1(color = red), arg2(color = blue)) ###PROBLEM: too late to customize arg2 if it's an Instance!
        ## (unless this sets some state and is thereby possible on an instance... seems fishy even so.)
        # is the real intent of _arg1_for_arg2 to be an instance? what if arg2, using it, was made multiple times?
        # so no, that's the bug -- _arg1_for_arg2 is an expr which when made in those two places in arg2 dflt should be shared --
        # but it's not already an instance. It's like an ArgExpr with all ipath components added locally in this class already fixed
        # rather than coming from whatever gets built up -- as if we wrapped it when it came in and we did this,
        # then were able to strip off whatever ipath it got -- or equivly, we wrap it with "ignore outer ipath, just use this one".
        # As if I said _arg1_for_arg2 = ShareInstances(arg1) -- it gets an ipath but then ignores furtherly added ones. Hmm...
        # probably easy to implem if I decide it's right!
        #
        # [then I did Ribbon2_try2, then I extended this to say:]
        ### BUT IT'S WRONG, since if we use arg2 (expr) in several places here, how do we let each of *them* use different instances
        # of _arg1_for_arg2? We'd somehow have to say in arg2 dflt that we use the same instance of _arg1_for_arg2 for each inst of it --
        # but only for that, not for other instances of it. As if it had a quantifier for "what inst of arg1 to use in here".
        # As our lambda_Expr would make possible... ###DIGR can we let a call_Expr imply a lambda_Expr if arg1 is a lambda??
    if 'do this instead':
        dflt_arg2 = call_lambda_Expr( lambda myarg1: Rotate( myarg1, angle, myarg1.axis), arg1 )
        # or maybe a lambda_Expr is callable and doing so makes a call expr -- as opposed to being customizable (until called):
        dflt_arg2 = 0 and lambda_Expr( lambda arg1: Rotate( arg1, angle, arg1.axis))( arg1 ) # lambda is really called on an Instance
            # without '0 and', due to Stub bug, we get AssertionError: not permitted to re-supply already supplied positional args, in <Widget2D#17093(a)>

        arg2 = ArgExpr(Widget, dflt_arg2)
        _customized_arg2 = arg2(color=blue) ### PROBLEM: it might *still* be too late to customize,
        # since color=whatever won't burrow into things like localipathmod, let alone Rotate! #########
        # this current expr could only work if customizations on certain exprs would get passed into the interior
        # to be used by, or before, instantiations called for inside them. Hmm, same issue for If_expr(cond, expr1, expr2)(color=blue)
        # assuming expr[12] accept color customization. ####### if these custs became an OpExpr, eval could eval its arg1... might work.
        #
        # later, 070127: passthru customization seems unclear & hard but wanted:
        # maybe the feeling that customization ought to burrow into Rotate or localipathmod is related to them delegating to an arg --
        # since attr accesses delegate, so should attr definitions (but only for the attrs that actually delegate). That does make sense.
        # It's not easy to implement -- we have no list of attrs that don't delegate, we just try getattr and see if we get into __getattr__.
        # So to customize an attr -- wait, would it work to customize it at the outer level? No, because the draw call occurs inside.
        # It's as if we wanted to constrain X and Rotate(X) to have the same def and value of attr (if it delegates), e.g. color.
        # But the fact that X.draw uses X.color is not even dependent on whether Rotate delegates color! Ignoring that last point,
        # can customize mean "find the internal users of the def of color, and make them use this different def"? These internal users
        # are kid instances. They are self-contained in ability to use color. So parent would have to modify them -- presumably when it makes them.
        # So parent(color = cust) would have to instantiate, not its normal kid delegate, but kid(color = cust), I guess. I don't see an
        # easy implem, and I'm also suspicious it's the right idea.

        # So maybe the only soln is to do the color cust first, as the docstring had to say to describe the intent, anyway.
    pass

class Ribbon2_try2(Macro):###e perhaps needs some axis -> axisvector
    ###IMPLEM ShareInstances  - or not, if that lambda_Expr in _try1 makes it unneeded... it might be wrong anyway
    # if it provides no way to limit the sharing within the class that says to do it, or if doing that is too cumbersome or unclear.
    """Ribbon2(thing1, thing2) draws a thing1 instance in red and a thing2 instance in blue.
    If thing2 is not supplied, a rotated thing1 instance is used for it, and also drawn in blue.
    """
    angle = 150.0
    arg1 = ArgExpr(Widget)
    _drawn_arg1 = Instance(arg1(color=red)) ###e digr: could I have said Instance(arg1, color=red)? I bet people will try that...
    _arg1_for_arg2 = ShareInstances(arg1(color=blue)) # still an expr; in fact, this ASSUMES arg1 is passed in as an expr, not as an instance! Hmm#####
    ## arg2 = ArgExpr(Widget, Rotate( _arg1_for_arg2, angle, _arg1_for_arg2.axis))
    arg2 = ArgExpr(Widget, Rotate( _arg1_for_arg2, angle, getattr_Expr( _arg1_for_arg2, 'axis') ))
    _drawn_arg2 = Instance(arg2(color=blue)) ####KLUGE: add color here in case arg2 was supplied, but in dflt expr in case we used that
    delegate = Overlay(_drawn_arg1, _drawn_arg2)

class Ribbon2_try3(Macro): #070129 ###e perhaps needs some axis -> axisvector
    """Ribbon2(thing1, thing2) draws a thing1 instance in red and a thing2 instance in blue, assuming they are color-customizable.
    If thing2 is not supplied, a rotated thing1 instance (different drawable instance, same model object instance)
    is used for it (also drawn in blue).
    """
    angle = 150.0
    arg1 = Arg(ModelObject3D) ###k type implies that it has 3d shape etc, determines how much gets instantiated here (axis, not color??)
    arg2 = Arg(ModelObject3D, Rotate(arg1, angle, arg1.axis) ) # doesn't yet work... see below
        # Rotate works on a ModelObject3D instance which is like a Drawable expr
        # note: Rotate's default axis is the Z axis, not arg1.axis even if that exists
    delegate = Overlay(arg1(color = red), arg2(color = blue)) # doesn't yet work... see below
        # For all this to work requires two proposed semantic changes:
        # - Rotate delegation more like customization -- instance of Rotate produces no separate instance of its delegate
        # - partial instantiation by Arg, only of attrs that are part of its declared type (mentioned above)
        # (these changes make it likely that the 'delegate' attr will be renamed, too)
    pass


# very old cmt:
# Ribbon2 has: radius, axis (some sort of length - of one bp?), turn (angle??), n, color1, color2, and full position/orientation
# and it will have display modes, incl cyl with helix/base/groove texture, and flexible coloring;
# and ability to show the units in it, namely strands, or basepairs, or bases (selected/opd by type)
# and for us to add cmd bindings like "make neighbor strand" (if room) or "make crossover here" (maybe only on a base?)

# but as a first step, we can select it as a unit, copy/paste, deposit, move, etc.
# In this, it is sort of like an atom or set of co-selected atoms... some relation to chunk or jig too.
# I'd get best results by letting it be its own thing... but fastest, by borrowing one of those...


class obs:
    path = StateArg(Cylinder_HelicalPath)
    path.someattr = Option(Something, 'dflt') # set path.someattr to Option(...) -- ExprsMeta scanner would need to see this --
        # but what attrname would it use in the Option?? maybe the _try1 version is better since it says the name,
        # or maybe you can give it in Option as string arg1.

class todo:
    # might need other state, like some colors

    # and links to things made from this guide shape -- or a superclass or whatever that says we are a guide shape
    # (and all of them can have links like that)

    # and ops to make attached things like crossovers, to give posns for potential ones
    # and display styles for self and those things...
    # for now just have default drawing code, using the Ribbon classes above.
    pass

# ==

import Command_scratch_1

# ==

if 0:
    # old example usage
    Ribbon2(1, 0.2, 1/10.5, 50, blue, color2 = green), # this color2 arg stuff is a kluge
    Highlightable( Ribbon2(1, 0.2, 1/10.5, 50, yellow, color2 = red), sbar_text = "bottom ribbon2" ),

# end

