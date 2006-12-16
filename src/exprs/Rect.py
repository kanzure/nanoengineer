"""
Rect.py -- provide Rect, RectFrame, and other simple 2d shapes

$Id$

These are prototypes with imperfect arg syntaxes.

#e maybe rename this file to shapes.py?
#e also have shapes3d.py, or even put both in one file, when simple.

"""

from basic import *
from basic import _self

import draw_utils
reload_once(draw_utils)
from draw_utils import *

class Rect(Widget2D): # finally working as of 061106
    """Rect(width, height, color) renders as a filled x/y-aligned rectangle
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
        printfyi("not yet trying to trigger the error warning for 'bright = width'") # (since it's nim, even as of 061114 i think)
        bright = _self.width
        btop = _self.height
##    # fyi, these are not needed (same as the defaults in Widget2D):
##    bbottom = 0
##    bleft = 0
    
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, self.fix_color(self.color)) #e move fix_color into draw_filled_rect? 
        glEnable(GL_CULL_FACE)
    pass

##Position = 'Position' #e stub, wrong, doesn't matter yet
##Color = 'Color'# ditto, might differ from other stubs for this

class Sphere(Widget2D): # the superclass is to give it a 2D lbox. We'll need to think about whether it needs renaming.
        # or maybe this super will be Widget3D and that will inherit Widget2D?? hmm...
    """Sphere(radius, color, center) represents a spherical surface
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
        from drawer import drawsphere # drawsphere(color, pos, radius, detailLevel)
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
    "Accept same args as Rect, but draw as nothing. Equivalent to SpacerFor(Rect( same args))."
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
    """A spacer, the same size and position (ie same lbox) as its arg. ###e Should merge this with Spacer(dims),
    easier if dims can be a rect object which is also like a thing you could draw... maybe that's the same as a Rect object? #k
    See also Invisible, which unlike this will pick up mouseovers for highlighting. [##e And which is nim, in a cannib file.]
    """
    delegate = Arg(Widget2D)
    def draw(self):
        return
    pass

# ==

IsocelesTriangle = Rect  #e stub (implem as simple variant of Rect; find it in a cannib file)

# ==

class RectFrame(Widget2D):
    """RectFrame(width, height, thickness, color) is an empty rect (of the given outer dims)
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

# end
