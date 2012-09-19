# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
ExprsConstants.py -- define constants and simple functions used by many files in this package

@author: bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

"""

# Note: most or all of the imports from cad/src are no longer needed here,
# since the exprs modules that want them import them directly.

from geometry.VQT import V

# compass positions, also usable for DrawInCorner

from utilities.prefs_constants import UPPER_RIGHT
from utilities.prefs_constants import UPPER_LEFT
from utilities.prefs_constants import LOWER_LEFT
from utilities.prefs_constants import LOWER_RIGHT

    # note: their values are ints -- perhaps hard to change since they might correspond to Qt radiobutton indices (guess)

# tell pylint we don't want unused import warnings about those:
UPPER_RIGHT

from exprs.py_utils import identity

# standard corners for various UI elements [070326, but some will be revised soon]
WORLD_MT_CORNER = UPPER_LEFT
##PM_CORNER = LOWER_RIGHT #e revise
##DEBUG_CORNER = LOWER_LEFT #e revise
PM_CORNER = LOWER_LEFT
DEBUG_CORNER = LOWER_RIGHT

# == other generally useful constants

# (but color constants are imported lower down)

# geometric (moved here from draw_utils.py, 070130)

ORIGIN = V(0,0,0)
DX = V(1,0,0)
DY = V(0,1,0)
DZ = V(0,0,1)

ORIGIN2 = V(0.0, 0.0)
D2X = V(1.0, 0.0) ##e rename to DX2?
D2Y = V(0.0, 1.0)

# type aliases (tentative; see canon_type [070131])
Int = int # warning: not the same as Numeric.Int, which equals 'l'
Float = float # warning: not the same as Numeric.Float, which equals 'd'
String = str # warning: not the same as parse_utils.String
Boolean = bool

# == Python and debug utilities, and low-level local defs

nevermind = lambda func: identity

# == colors (constants and simple functions; import them everywhere to discourage name conflicts that show up only later)

#e maybe import the following from a different file, but for now we need to define some here
#k need to make sure none of these are defined elsewhere in this module
from utilities.constants import red, green, blue, white
##from constants import black, purple, magenta, violet, yellow, orange, pink, gray
    # note: various defs of purple I've seen:
    # ave_colors( 0.5, red, blue), or (0.5, 0.0, 0.5), or (0.7,0.0,0.7), or (0.6, 0.1, 0.9) == violet in constants.py
##from constants import aqua, darkgreen, navy, darkred, lightblue
from utilities.constants import ave_colors
    ###e what does this do to alpha? A: uses zip, which means, weight it if present in both colors, discard it otherwise.
    ###k What *should* it do? Not that, but that is at least not going to cause "crashes" in non-alpha-using code.

def normalize_color(color): #070215; might be too slow; so far only used by fix_color method
    """
    Make sure color is a 4-tuple of floats.
    (Not a numeric array -- too likely to hit the == bug for those.)
    """
    if len(color) == 3:
        r,g,b = color
        a = 1.0
    elif len(color) == 4:
        r,g,b,a = color
    else:
        assert len(color) in (3,4)
    return ( float(r), float(g), float(b), float(a)) # alpha will get discarded by ave_colors for now, but shouldn't crash [070215]

#e define brown somewhere, and new funcs to lighten or darken a color

lightblue = ave_colors( 0.2, blue, white) # WARNING: differs from at least one version of this in constants.py
halfblue = ave_colors( 0.5, blue, white)

def translucent_color(color, opacity = 0.5): #e refile with ave_colors
    """
    Make color (a 3- or 4-tuple of floats) have the given opacity (default 0.5, might be revised);
    if it was already translucent, this multiplies the opacity it had.
    """
    if len(color) == 3:
        c1, c2, c3 = color
        c4 = 1.0
    else:
        c1, c2, c3, c4 = color
    return (c1, c2, c3, c4 * opacity)

trans_blue = translucent_color(halfblue)
trans_red = translucent_color(red)
trans_green = translucent_color(green)

# == other constants

PIXELS = 0.035 ###WRONG: rough approximation; true value depends on depth (in perspective view), glpane size, and zoomfactor!
    ###e A useful temporary kluge might be to compute the correct value for the cov plane, and change this constant to match
    # whenever entering testmode (or perhaps when resizing glpane), much like drawfont2 or mymousepoints does internally.
    # But if we do that, then rather than pretending it's a constant, we should rename it and make it an appropriate function
    # or method, e.g. glpane.cov_PIXELS for the correct value at the cov, updated as needed.
    #   We might also replace some uses of PIXELS
    # with fancier functions that compute this for some model object point... but the main use of it is for 2d widget display,
    # for which a single value ought to be correct anyway. (We could even artificially set the transformation matrices so that
    # this value happened to be the correct one -- in fact, we already do that in DrawInCorner, used for most 2d widgets!
    # To fully review that I'd need to include what's done in drawfont2 or mymousepoints via TextRect, too.)
    #   For model objects (at least in perspective view), there are big issues about what this really means, or should mean --
    # e.g. if you use it in making a displist and then the model object depth changes (in perspective view), or the glpane size
    # changes, or the zoom factor changes. Similar issues arise for "billboarding" (screen-parallel alignment) and x/y-alignment
    # to pixel boundaries. Ultimately we need a variety of new Drawable-interface features for this purpose.
    # We also need to start using glDrawPixels instead of textures for 2d widgets, at some point. [comment revised 070304]

# == lower-level stubs -- these will probably be refiled when they are no longer stubs ###@@@

NullIpath = '.' ##k ok that it's not None? maybe not, we might test for None... seems to work for now tho.
    #e make it different per reload? [070121 changed from 'NullIpath' to '.' to shorten debug prints]

from exprs.__Symbols__ import Anything ## TODO: remove this,
 # since it's our only remaining import of __Symbols__
 # and it causes a runtime import loop with Exprs.py

StubType = Anything # use this for stub Type symbols [new symbol and policy, 070115]

# stub types
Width    = StubType
Color    = StubType
Vector   = StubType
Quat     = StubType
Position = StubType
Point    = StubType
StateRef = StubType
Function = StubType
Drawable = StubType # warning: also defined as DelegatingInstanceOrExpr in one file
# note: class Action in Set.py is not in this list since it's not entirely a stub.

Type     = Anything

# end
