# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Rect.py -- provide Rect, RectFrame, and other simple 2d shapes

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

These are prototypes with imperfect arg syntaxes.

#e maybe rename this file to shapes.py?
#e also have shapes3d.py, or even put both in one file, when simple.

"""

from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GLU import gluNewQuadric
from OpenGL.GLU import GLU_SMOOTH
from OpenGL.GLU import gluQuadricNormals
from OpenGL.GLU import gluPartialDisk

from utilities import debug_flags

from utilities.constants import gray, white, black

from exprs.widget2d import Widget2D
from exprs.attr_decl_macros import Arg, ArgOrOption, Option
from exprs.instance_helpers import InstanceOrExpr, DelegatingMixin
from exprs.ExprsConstants import Width, Color, Position, ORIGIN, PIXELS, Point, DX, DY
from exprs.draw_utils import draw_filled_rect
from exprs.draw_utils import draw_filled_triangle
from exprs.draw_utils import draw_filled_rect_frame
from exprs.__Symbols__ import _self

from exprs.py_utils import printnim, printfyi

from graphics.drawing.CS_draw_primitives import drawsphere
from graphics.drawing.CS_draw_primitives import drawline

# ==

class Rect(Widget2D): # finally working as of 061106
    """
    Rect(width, height, color) renders as a filled x/y-aligned rectangle
    of the given dimensions and color, with the origin on bottomleft,
    and a layout box equal to its size (no margin).

    If color is not given, it will be gray [#e should be a default attrval from env].

    If height is not given, it will be a square (even if width is a formula and/or random).

    See also: RectFrame, ...
    """
    # args
    width = Arg(Width, 5) # changed 10 to 5 late on 061109
        # Note: Widget2D defines width & height, making this seem circular, but it's ok (see comment in RectFrame)
    height = Arg(Width, width)
    color = ArgOrOption(Color, gray)
    # formulas
    if 0:
        # use this to test whatever scheme we use to detect this error, once we put one in [disabled 061105 until other things work]
        bright = width ######@@@@@ PROBLEM: in ns, width and bright will have same value, no ordering possible -- how can it tell
            # which one should be used to name the arg? It can't, so it'll need to detect this error and make you use _self. prefix.
            # (in theory, if it could scan source code, or turn on debugging during class imports, it could figure this out...
            #  or you could put the argname in Arg or have an _args decl... but I think just using _self.attr in these cases is simpler.)
        printnim("make sure it complains about bright and width here")
        btop = height
    else:
        if debug_flags.atom_debug:
            printfyi("not yet trying to trigger the error warning for 'bright = width'") # (since it's nim, even as of 061114 i think)
        bright = _self.width
        btop = _self.height
    # bbottom and bleft are not needed (same as the defaults in Widget2D), except that we use them in the formula for center;
    # it would be more correct to say bleft = _self.bleft, but less efficient I think (not much), and hasn't been tested (should be #e).
    bbottom = 0
    bleft = 0
##    center = V_expr( (bright - bleft) / 2.0, (btop - bbottom) / 2.0, 0.0) #070211 #e someday this could be deduced from lbox, generally
        ###e should move this def into Spacer, RectFrame, etc -- or arrange to deduce it from lbox on any Widget2D, somehow...
        #  [070227] hmm, can't it just be moved from here into Widget2D itself? Yes, that works!
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, self.fix_color(self.color)) #e move fix_color into draw_filled_rect?
        glEnable(GL_CULL_FACE)
    pass

class Sphere(Widget2D): # the superclass is to give it a 2D lbox. We'll need to think about whether it needs renaming.
        # or maybe this super will be Widget3D and that will inherit Widget2D?? hmm...
    """
    Sphere(radius, color, center) represents a spherical surface
    of the given radius (default 1), color (default gray), and center (default the local origin) [partly nim if not #e].
    [There is also an undocumented option, detailLevel.]
    """
    # args
    radius = ArgOrOption(Width, 1)
    color = ArgOrOption(Color, gray)
    center = ArgOrOption(Position, ORIGIN) # this is not yet supported in determining the layout box,
        # since I'm tempted to say, if this is supplied, turn into a macro, Translate(Sphere(...))
        # so I won't need to uglify those calcs. Not yet sure quite how to most easily organize that --
        # best would be a general way to make some options or uses of them "turn into macros",
        # sort of like in a math paper saying "w/o loss of generality, assume center == ORIGIN". ###e
    detailLevel = Option(int, 2) #k guess: 1 or 2 or 3, i think -- undocumented since needs a better name and maybe arg meaning
    # formulae
    bright = _self.radius
    bleft = _self.radius
    btop = _self.radius
    bbottom = _self.radius
    def draw(self):
        drawsphere(self.fix_color(self.color), self.center, self.radius, self.detailLevel)
    pass

# ==

class Spacer_pre061205_obs(Rect): #061126
    # slight kluge, since accepts color arg but ignores it (harmless, esp since nothing yet warns about extra args or opts)
    # (note: we might decide that accepting all the same args as Rect is actually a feature)
    #e #k might need enhancement to declare that instantiation does nothing, ie makes no diff whether you reref after it --
    # but for that matter the same might be true of Rect itself, or anything that does pure drawing...
    #e see also: Invisible [nim], e.g. Invisible(Rect(...)) or Invisible(whatever) as a spacer sized to whatever you want

    ###e should change default dims to 0,0 -- now i did this by rewriting it below
    def draw(self):
        return
    pass

class Spacer(Widget2D): # rewritten 061205 to not inherit from Rect, so arg defaults can change --
        ###e it would be better if that was not the only safe way [tho I didn't even bother trying the simpler way, I admit]
    """
    Accept same args as Rect, but draw as nothing.
    Equivalent to SpacerFor(Rect( same args)).
    """
    width = Arg(Width, 0)
        # Note: Widget2D defines width & height, making this seem circular, but it's ok (see comment in RectFrame)
    height = Arg(Width, width)
    color = ArgOrOption(Color, gray) # not used, but should be accepted, since it's accepted as arg or public option name in Rect
    # formulas
    bright = _self.width
    btop = _self.height
    def draw(self):
        return
    pass

class SpacerFor(InstanceOrExpr, DelegatingMixin):
    """
    A spacer, the same size and position (ie same lbox) as its arg. ###e Should merge this with Spacer(dims),
    easier if dims can be a rect object which is also like a thing you could draw... maybe that's the same as a Rect object? #k
    See also Invisible, which unlike this will pick up mouseovers for highlighting. [##e And which is nim, in a cannib file.]
    """
    delegate = Arg(Widget2D)
    def draw(self):
        return
    pass

# ==

class IsocelesTriangle(Rect):
    """
    IsocelesTriangle(width, height, color) renders as a filled upright isoceles triangle
    (symmetric around a vertical line, apex centered on top), with local origin on bottomleft vertex.
    """
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_triangle(ORIGIN, DX * self.bright, DY * self.btop + DX * self.bright * 0.5, self.fix_color(self.color))
        glEnable(GL_CULL_FACE)
    pass

# ==

class RectFrame(Widget2D):
    """
    RectFrame(width, height, thickness, color) is an empty rect (of the given outer dims)
    with a filled border of the given thickness (like a picture frame with nothing inside).
    """
    # args
    width = Arg(Width, 10)
        # NOTE: Widget2D now [061114] defines width from bright & bleft (risking circularity), & similarly height;
        # I think that's ok, since we zap that def here, so the set of active defs is not circular
        # (and they're consistent in relations they produce, too, as it happens); a test (_7b) shows no problem.
    height = Arg(Width, width)
    thickness = ArgOrOption(Width, 4 * PIXELS)
    color = ArgOrOption(Color, white)
    # layout formulas
    bright = _self.width
    btop = _self.height
    ## debug code from 061110 removed, see rev 1.25 for commented-out version:
    ## override _e_eval to print _self (in all envs from inner to outer) to see if lexenv_Expr is working
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_rect_frame(ORIGIN, DX * self.width, DY * self.height, self.thickness, self.fix_color(self.color))
        glEnable(GL_CULL_FACE)
    pass

# ==

class Line(InstanceOrExpr): #070211; revised 070419 (Widget2D -> IorE, more options)
    end1 = Arg(Point)
    end2 = Arg(Point)
    color = ArgOrOption( Color, black)
    width = Option(int, 1) #e rename linewidth?
    dashed = Option(bool, False)
    def draw(self):
        color = self.fix_color(self.color)
        end1, end2 = self.end1, self.end2
        width = self.width
        dashed = self.dashed
        drawline(color[:3], end1, end2, width = width, dashEnabled = dashed) ###k dashEnabled untested here
    pass

# ==

class PartialDisk(Widget2D): # stub (no settable parameters), works (testexpr_38), 070401
    def _C_quadric(self):
        """
        set up self.quadric
        """
        # see PyOpenGL Demo/NeHe/lesson18.py
        quadric = gluNewQuadric() #e it may be that this object could be shared by all instances, or even more globally -- not sure
        gluQuadricNormals(quadric, GLU_SMOOTH) # Create Smooth Normals
##        gluQuadricTexture(quadric, GL_TRUE)    # Create Texture Coords
        return quadric
    def draw(self):
        gluPartialDisk(self.quadric,0.5,1.5,32,32,0,300) #e stub - should use named options
        return
    pass

# end
