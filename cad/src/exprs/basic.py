# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
basic.py -- define things to be imported by every module in this package (using import *)

$Id$

"""

# Import order issues --
# This module basic gets imported first, and it will be imported at the beginning of most modules.
# But it wants to define things of general interest to all modules.
#
# This can lead to recursive import problems. Here is how we will resolve them:
# - If a high-level def should be included here, import it last.
#   Then when it imports basic, it will find what it needs already defined in basic.
# - When we import several high-level defs, they should be lowest-level first; higher ones will find lower ones
#   defined in basic when they import it, but not vice versa (but they shouldn't need to find them).
# - When we import symbols like Expr or define symbols like Arg, also do this in order of level, in terms of import dependency.
#
# Note that this means we can't put all our import statements first --
# we have to interleave them with local defs, based on level.
#
# Specific problems:
# - ExprsMeta knows about special cases for some symbols defined in modules which have to import ExprsMeta for its metaclass.
#   Solution: ExprsMeta should only import those special-case symbols at runtime.
#   (And it should do so using reload_once, so their own modules can support runtime reload.)
#
# Approximate order of imports:
# - Python and debug utilities (especially the ones needed by ExprsMeta), including those defined outside this exprs package
# - ExprsMeta (needed as a metaclass by many classes we'll define)
# - abstract classes like Expr and InstanceOrExpr
# - widget classes, in order of lowest to highest level (most of them don't need to be imported by this module at all)


# == imports from python itself

import sys, os
import time # questionable, but try it
from Numeric import dot

sys.setrecursionlimit(650) # 5000 is set in startup_funcs.py; this will ease debugging, but REMOVE WHEN DEVEL IS DONE [061121]

# == imports from cad/src

from VQT import V, A, Q, norm, vlen, cross
from math import sqrt #070225
from math import pi, sin, cos #070130

from state_utils import transclose, same_vals
## not yet needed: from state_utils import _UNSET_ # warning: not included in "import *"

import platform # so all our code can refer to platform.atom_debug #e someday this should be renamed throughout NE1 (app.debug?)
import EndUser

from constants import noop # def noop(*args,**kws): pass

from prefs_constants import UPPER_RIGHT, UPPER_LEFT, LOWER_LEFT, LOWER_RIGHT # compass positions, also usable for DrawInCorner
    # note: their values are ints -- perhaps hard to change since they might correspond to Qt radiobutton indices (guess)

# standard corners for various UI elements [070326, but some will be revised soon]
WORLD_MT_CORNER = UPPER_LEFT
##PM_CORNER = LOWER_RIGHT #e revise
##DEBUG_CORNER = LOWER_LEFT #e revise
PM_CORNER = LOWER_LEFT
DEBUG_CORNER = LOWER_RIGHT

from debug import reload_once_per_event, print_compact_traceback, print_compact_stack, safe_repr

from debug_prefs import debug_pref, Choice_boolean_False, Choice_boolean_True, Choice #070228

# consider also doing: import env as global_env  [070313 suggestion]


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

# == OpenGL imports -- for now, individual modules import things from submodules of OpenGL as needed; this might be revised

# == Python and debug utilities, and low-level local defs

try:
    old_EVAL_REFORM = EVAL_REFORM
except NameError:
    old_EVAL_REFORM = None

EVAL_REFORM = True # 070115: False supposedly acts like old code, True like experimental new code which should become standard;
     # this affects all class defs, so to be safe, print a warning if it changes across reload

if old_EVAL_REFORM != EVAL_REFORM and old_EVAL_REFORM is not None:
    print "\n*** WARNING: EVAL_REFORM was %r before reload, is %r now -- might require restart of NE1 or testmode" % \
          (old_EVAL_REFORM, EVAL_REFORM)
else:
    if not EVAL_REFORM:
        print "EVAL_REFORM is %r" % EVAL_REFORM

ENABLE_RELOAD = True and platform.atom_debug

def reload_once(module):
    """This function is used to support automatic runtime reloading of modules within this package,
    for developer convenience. To use it, add this code before any import of symbols from a module
    (or use this code in place of any direct import of a module):

      import module
      reload_once(module)

    Warning: not all modules support runtime reload. Those that don't should say so in their docstrings.
    
    Warning: this system does not yet properly handle indirect imports, when only the inner module has
    been modified. See code comments for details, especially the docstring of debug.reload_once_per_event().
    As a workaround, if A imports B and you edit B.py, also edit A.py in order to trigger the desired runtime reload of B.py.
    
    Note: this function's module (exprs.basic itself) is fast and harmless enough to reload that it can be
    reloaded on every use, without bothering to use reload_once. Therefore, external callers of anything
    in the exprs package can always "import basic;reload(basic)" first, and if they do, all modules within
    exprs can just start with "from basic import *". But for clarity, some of them call reload_once on basic too.
    """
    if (not EndUser.enableDeveloperFeatures()): #070627 precaution; should improve by making this only affect default value of a debug_pref ###TODO
        return
    
    if not ENABLE_RELOAD:
        def printfyi(msg): # WARNING: dup code, inlining py_utils version since not yet imported
            msg = "fyi (printonce): " + msg
            from env import seen_before
            if not seen_before(msg):
                print msg
        if 1:
            ## printfyi( "exprs modules won't be reloaded during this session" ) # 070627 removed this
            return
    from testdraw import vv
    reload_once_per_event(module, always_print = True, never_again = False, counter = vv.reload_counter, check_modtime = True)

def stub(*args, **kws): #e rename to stubfunc (too hard to search for 'stub', common in comments)
    assert 0, "stub called"


# == low-level imports from this exprs package

import py_utils
reload_once(py_utils)
from py_utils import * # includes printnim, identity, seen_before

nevermind = lambda func: identity

from intern_ipath import intern_ipath # (it doesn't make sense to try to autoreload this module -- ###e it should say so in some attr)


# == ExprsMeta #e and whatever it requires

from ExprsMeta import * ###e can this support autoreload?? ###e note -- this imports a few other modules - list those here ##doc

from __Symbols__ import _self, _my # (__Symbols__ module doesn't support reload) # warning: not included in "import *"
    # _this is imported below from somewhere else -- since it's not a Symbol! Maybe __Symbols__ should warn if we ask for it. #e

from __Symbols__ import Anything #070115
from __Symbols__ import Automatic, Something #070131

# Symbol docstrings -- for now, just tack them on (not yet used AFAIK):

Anything.__doc__ = """Anything is a legitimate type to coerce to which means "don't change the value at all". """
Anything._e_sym_constant = True

Something.__doc__ = """Something is a stub for when we don't yet know a type or value or formula,
but plan to replace it with something specific (by editing the source code later). """
Something._e_eval_forward_to = Anything

Automatic.__doc__ = """Automatic [###NIM] can be coerced to most types to produce a default value.
By convention, when constructing certain classes of exprs, it can be passed as an arg or option value
to specify that a reasonable value should be chosen which might depend on the values provided for other
args or options. """
    ###e implem of that:
    #  probably the type should say "or Automatic" if it wants to let a later stage use other args to interpret it,
    #  or maybe the typedecl could give the specific rule for replacing Automatic, using a syntax not specific to Automatic.
Automatic._e_sym_constant = True


from __Symbols__ import _app # not included in import * [070108 in test.py, moved here 070122]


# == colors (constants and simple functions; import them everywhere to discourage name conflicts that show up only later)

#e maybe import the following from a different file, but for now we need to define some here
#k need to make sure none of these are defined elsewhere in this module
from constants import black, red, green, blue, purple, magenta, violet, yellow, orange, pink, white, gray
    # note: various defs of purple I've seen:
    # ave_colors( 0.5, red, blue), or (0.5, 0.0, 0.5), or (0.7,0.0,0.7), or (0.6, 0.1, 0.9) == violet in constants.py
from constants import aqua, darkgreen, navy, darkred, lightblue
from constants import ave_colors
    ###e what does this do to alpha? A: uses zip, which means, weight it if present in both colors, discard it otherwise.
    ###k What *should* it do? Not that, but that is at least not going to cause "crashes" in non-alpha-using code.

def normalize_color(color): #070215; might be too slow; so far only used by fix_color method
    """Make sure color is a 4-tuple of floats. (Not a numeric array -- too likely to hit the == bug for those.)"""
    if len(color) == 3:
        r,g,b = color
        a = 1.0
    elif len(color) == 4:
        r,g,b,a = color
    else:
        assert len(color) in (3,4)
    return ( float(r), float(g), float(b), float(a)) # alpha will get discarded by ave_colors for now, but shouldn't crash [070215]

#e define brown somewhere, and new funcs to lighten or darken a color

lightblue = ave_colors( 0.2, blue, white)
lightgreen = ave_colors( 0.2, green, white)
halfblue = ave_colors( 0.5, blue, white)

def translucent_color(color, opacity = 0.5): #e refile with ave_colors
    """Make color (a 3- or 4-tuple of floats) have the given opacity (default 0.5, might be revised);
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

StubType = Anything # use this for stub Type symbols [new symbol and policy, 070115]

# stub types
Width = Color = Vector = Quat = Position = Point = StateRef = Function = StubType   # for Action, see below
Type = Anything

# == fundamental defs

import Exprs
reload_once(Exprs) # doesn't support reload, for now, so this is a noop
from Exprs import * # Expr, lots of predicates and subclasses

import StatePlace
reload_once(StatePlace)
from StatePlace import StatePlace, set_default_attrs # revised 061203, and moved before instance_helpers & If_expr

import attr_decl_macros
reload_once(attr_decl_macros)
from attr_decl_macros import * # Instance, Arg, Option, ArgOrOption, State, etc

import instance_helpers
reload_once(instance_helpers)
from instance_helpers import InstanceOrExpr, DelegatingMixin, DelegatingInstanceOrExpr, InstanceMacro, \
     _this, ModelObject, WithModelType, WithAttributes

import If_expr # 061128
reload_once(If_expr)
from If_expr import *

##import staterefs
##reload_once(staterefs)
##from staterefs import * 

import iterator_exprs # 070302
reload_once(iterator_exprs)
from iterator_exprs import *

# === higher-level defs, common enough to import for everything

import widget2d
reload_once(widget2d)
from widget2d import Widget, Widget2D

# == higher-level stubs

# lowercase stub doesn't work for the following, since they get called during import, so use uppercase Stub

Stub = Widget2D # use this for stub InstanceOrExpr subclasses

# stub types which are also defined as classes in other files
import Set
reload_once(Set)
from Set import Action # import added 070115

    ###k hmm, is the Set module name a conflict with the proposal for class Set to be imported in this file, basic.py?

import statearray
reload_once(statearray)
from statearray import StateArray, StateArrayRefs


# layout prims and the like (but for the most part, layout prims probably won't be defined in basic.py at all)
# [none at the moment]

# == end
