"""
Boxed.py -- example of high-level layout expr

$Id$
"""

from basic import *
from basic import _self

import Rect
reload_once(Rect)
from Rect import RectFrame

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import transforms
reload_once(transforms)
from transforms import Translate

class Boxed(InstanceMacro):
    """Boxed(widget) is a boxed version of widget -- it looks like widget, centered inside a rectangular frame.
    Default options are pixelgap = 4 (in pixels), borderwidth = 4 (in pixels), bordercolor = white.
    [#e These can be changed in the env in the usual way. [nim]]
       WARNING: some deprecated but commonly used options are given in model units, not in pixels (probably a design flaw).
    """
    # WARNING: would not work if it inherited from Widget2D,
    # since it would pick up Widget2D default values for lbox attrs like btop. [unconfirmed but likely; 061127 comment]

    # args
    thing = Arg(Widget2D)
    
    # options
    borderwidth = Option(int, 4) # 070305 new feature -- specified in pixels
    borderthickness = Option(Width, borderwidth * PIXELS)
        # old alternative (worse since caller has to multiply by PIXELS); commonly used, but deprecated as of 070305
        # (warning: borderthickness is still used as an internal formula when not supplied)
        # (WARNING: supplying both forms is an error, but is not detected;
        #  this might cause bugs that are hard for the user to figure out
        #  if the different option forms were used in successive customizations of the same expr)
    
    pixelgap = Option(int, 4) # 070305 new feature [#e rename gap? bordergap? (change all gap options to being in pixels?)]
        # (maybe not yet tested with nonzero passed-in values)
    gap = Option(Width, pixelgap * PIXELS)
        # old alternative (worse since caller has to multiply by PIXELS), commonly used, but deprecated as of 070305
        # (see also the comments for borderthickness)
        # (warning: gap is still used as an internal formula when not supplied)
    
    bordercolor = Option(Color, white)
    
    # internal formulae
    extra1 = gap + borderthickness
    ww = thing.width  + 2 * extra1 #k I'm not sure that all Widget2Ds have width -- if not, make it so ##e [061114]
    hh = thing.height + 2 * extra1
    # appearance
    _value = Overlay( Translate( RectFrame( ww, hh, thickness = borderthickness, color = bordercolor),
                                 - V_expr( thing.bleft + extra1, thing.bbottom + extra1) ), #e can't we clarify this somehow?
                      thing)
    pass

# end
