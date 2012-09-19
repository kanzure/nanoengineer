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
from Numeric import dot

sys.setrecursionlimit(650) # 5000 is set in startup_funcs.py; this will ease debugging, but REMOVE WHEN DEVEL IS DONE [061121]

# == imports from cad/src

from geometry.VQT import V, A, Q, norm, vlen, cross
from math import sqrt #070225
from math import pi, sin, cos #070130

from foundation.state_utils import transclose, same_vals
## not yet needed: from state_utils import _UNSET_ # warning: not included in "import *"

from utilities.constants import noop # def noop(*args,**kws): pass

from utilities.debug import print_compact_traceback, print_compact_stack, safe_repr

from utilities.debug_prefs import debug_pref, Choice_boolean_False, Choice_boolean_True, Choice #070228

# consider also doing: import env as global_env  [070313 suggestion]


# == OpenGL imports -- for now, individual modules import things from submodules of OpenGL as needed; this might be revised

from exprs.reload import reload_once

# == low-level imports from this exprs package

import exprs.py_utils
reload_once(exprs.py_utils)
#from py_utils import * # includes printnim, identity, seen_before

from exprs.intern_ipath import intern_ipath # (it doesn't make sense to try to autoreload this module -- ###e it should say so in some attr)


# == ExprsMeta #e and whatever it requires

#from ExprsMeta import * ###e can this support autoreload?? ###e note -- this imports a few other modules - list those here ##doc

from exprs.__Symbols__ import _self, _my # (__Symbols__ module doesn't support reload) # warning: not included in "import *"
    # _this is imported below from somewhere else -- since it's not a Symbol! Maybe __Symbols__ should warn if we ask for it. #e


from exprs.__Symbols__ import _app # not included in import * [070108 in test.py, moved here 070122]


# == fundamental defs

import exprs.Exprs
reload_once(exprs.Exprs) # doesn't support reload, for now, so this is a noop
#from Exprs import * # Expr, lots of predicates and subclasses

import exprs.StatePlace
reload_once(exprs.StatePlace)
from exprs.StatePlace import StatePlace, set_default_attrs # revised 061203, and moved before instance_helpers & If_expr

import exprs.attr_decl_macros
reload_once(exprs.attr_decl_macros)
#from attr_decl_macros import * # Instance, Arg, Option, ArgOrOption, State, etc

import exprs.instance_helpers
reload_once(exprs.instance_helpers)
from exprs.instance_helpers import InstanceOrExpr, DelegatingMixin, DelegatingInstanceOrExpr, InstanceMacro
from exprs.instance_helpers import _this, ModelObject, WithModelType, WithAttributes

import exprs.If_expr # 061128
reload_once(exprs.If_expr)
#from If_expr import *

##import staterefs
##reload_once(staterefs)
##from staterefs import *

import exprs.iterator_exprs # 070302
reload_once(exprs.iterator_exprs)
#from iterator_exprs import *

# === higher-level defs, common enough to import for everything

import widget2d
reload_once(widget2d)
from widget2d import Widget, Widget2D

# == higher-level stubs

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
