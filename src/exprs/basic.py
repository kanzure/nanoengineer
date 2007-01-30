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

sys.setrecursionlimit(650) # 5000 is set in startup_funcs.py; this will ease debugging, but REMOVE WHEN DEVEL IS DONE [061121]

# == imports from cad/src

from VQT import V, A, Q, norm, vlen

from state_utils import transclose, same_vals
## not yet needed: from state_utils import _UNSET_ # warning: not included in "import *"

import platform # so all our code can refer to platform.atom_debug #e someday this should be renamed throughout NE1 (app.debug?)

from constants import noop # def noop(*args,**kws): pass

# (but color constants are imported lower down)

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
    print "EVAL_REFORM is %r" % EVAL_REFORM

from debug import reload_once_per_event, print_compact_traceback, print_compact_stack

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
    if not ENABLE_RELOAD:
        def printfyi(msg): # WARNING: dup code, inlining py_utils version since not yet imported
            msg = "fyi (printonce): " + msg
            from env import seen_before
            if not seen_before(msg):
                print msg
        if 1:
            printfyi( "DISABLED FOR DEBUG: reload_once(%r)" % module.__name__ )
            return
    from testdraw import vv
    reload_once_per_event(module, always_print = True, never_again = False, counter = vv.reload_counter, check_modtime = True)

def stub(*args, **kws): #e rename to stubfunc (too hard to search for 'stub', common in comments)
    assert 0, "stub called"


# == low-level imports from this exprs package

import py_utils
reload_once(py_utils)
from py_utils import * # includes printnim

from intern_ipath import intern_ipath # (it doesn't make sense to try to autoreload this module -- ###e it should say so in some attr)


# == ExprsMeta #e and whatever it requires

from ExprsMeta import * ###e can this support autoreload?? ###e note -- this imports a few other modules - list those here ##doc

from __Symbols__ import _self, _my # (__Symbols__ module doesn't support reload) # warning: not included in "import *"
    # _this is imported below from somewhere else -- since it's not a Symbol! Maybe __Symbols__ should warn if we ask for it. #e

from __Symbols__ import Anything #070115
from __Symbols__ import _app # not included in import * [070108 in test.py, moved here 070122]


# == colors (constants and simple functions; import them everywhere to discourage name conflicts that show up only later)

#e maybe import the following from a different file, but for now we need to define some here
#k need to make sure none of these are defined elsewhere in this module
from constants import black, red, green, blue, purple, magenta, violet, yellow, orange, pink, white, gray
    # note: various defs of purple I've seen:
    # ave_colors( 0.5, red, blue), or (0.5, 0.0, 0.5), or (0.7,0.0,0.7), or (0.6, 0.1, 0.9) == violet in constants.py
from constants import aqua, darkgreen, navy, darkred, lightblue
from constants import ave_colors

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

PIXELS = 0.035 #k guess; 0.05->0.035 061114, re testexpr_7b (which shows true value is between 0.035 and 0.034)
    #e Note: this implem will be obs someday, since true value depends on depth, but can be set to any desired constant in a given plane.
    # WARNING: in present implem, correct value depends not only on depth but on glpane window size!
    # 0.035 was best for my usual g4 setup. ###e A useful temporary kluge would be to compute the correct value
    # for the cov plane, much like drawfont2 probably does internally, perhaps using mymousepoints.

# == lower-level stubs -- these will probably be refiled when they are no longer stubs ###@@@

NullIpath = '.' ##k ok that it's not None? maybe not, we might test for None... seems to work for now tho.
    #e make it different per reload? [070121 changed from 'NullIpath' to '.' to shorten debug prints]

StubType = Anything # use this for stub Type symbols [new symbol and policy, 070115]

# stub types
Width = Color = Vector = Position = StateRef = StubType   # for Action, see below
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
from instance_helpers import InstanceOrExpr, DelegatingMixin, DelegatingInstanceOrExpr, InstanceMacro, _this

import If_expr # 061128
reload_once(If_expr)
from If_expr import *

##import staterefs
##reload_once(staterefs)
##from staterefs import * 

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


# layout prims and the like (but for the most part, layout prims probably won't be defined in basic.py at all)
# [none at the moment]

# == end
