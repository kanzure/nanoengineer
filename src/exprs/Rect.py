"""
Rect.py -- provide Rect, RectFrame

$Id$

These are prototypes with imperfect arg syntaxes.
They might be pulled into a larger file sometime.
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
        printfyi("not yet trying to trigger the error warning for 'bright = width'")
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

# ==

class RectFrame(Widget2D):
    """RectFrame(width, height, thickness, color) is an empty rect (of the given outer dims)
    with a filled border of the given thickness (like a picture frame with nothing inside).
    """
    # args
    width = Arg(Width, 10)
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
