# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
statearray.py

@author: bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""
###e still UNFINISHED in some ways, the worst being that our elements are staterefs
# (see StateArrayRefs_getitem_as_stateref,
# and ###BUG comment in test_statearray.py or related file, 070312) --
# this is now renamed a feature of StateArrayRefs rather than a bug of StateArray.

from exprs.lvals import LvalForState, LvalDict2

from exprs.Exprs import call_Expr
from exprs.widget2d import Stub
from exprs.attr_decl_macros import State
from exprs.ExprsConstants import StubType
from exprs.__Symbols__ import _self, _E_ATTR


# ==

# try 1 - works fine, but returns an array of StateRefs to its internal state elements, not lvalue-like state elements.
# This might be useful, and it works and is tested, so rather than altering it and its test code,
# I'll rename it to StateArrayRefs, and keep it around.
# Later I'll write the real StateArray and see if that's indeed easier to use, and/or more efficient, or whatever.

StateArrayRefs_type = StubType # rename to just StateArrayRefs if we can...

def StateArrayRefs(type_expr, dfltval_expr, **kws): #e refile?
    """An array (expandable, arbitrarily indexed -- really a dictionary) of individually tracked/resettable state variables --
    accessed as individual StateRefs to the variables.
    Usage: in a class definition that uses ExprsMeta,
      attr = StateArrayRefs( type_expr, dfltval_expr )
    creates an attribute in each Instance which is effectively a dictionary of individually change/usage-tracked values,
    each coerced to type_expr [nim] (which can't yet depend on the dictionary index ###FIX),
    and each set to the value of dfltval_expr if it is accessed before it's first set.
       Note: dfltval_expr is evaluated without usage tracking; it is not yet decided whether it's evaluated only once
    (and if so when) or each time it's needed (the latter is more useful, but less efficient in many cases).
    There is not yet any way for dfltval_expr to depend on the dictionary index. ###FIX
       ###e There is not yet a way to control the possible or actual dictionary indices, or to provide an initial default value
    for the array as a whole (it's always {}). See also _CK_ and _CV_ rules, which provide read-only versions of those abilities.
    A combo of a _CK_/_CV_ interface to a StateArray could, for now, do much of what a _CK_-like feature in StateArray should do,
    though much more clumsily. In my first use of this I said "i want an arg for the index set... maybe even the initial set,
    or total set, so i can iter over it..."
    [NOTE: at least one dictlike class has that feature - review the ones in py_utils, see what _CK_ uses]
       ###e there may not yet be a way to delete an element (effectively resetting it to the value of dfltval_expr, computed somewhen).
       ###e there is not yet an unambiguous record of which elements are present or not in the array.
       ###e There is not yet a way to subscribe to updates of the set of defined array element indices,
    nor to updates of all changes to the entire set of values,
    let alone the same features for specific subsets, defined by index preds or sets.
       ###e There is not yet an efficient way to invalidate a range of indices at once
    (letting smart-enoguh subscribers receive just one summary inval).
       ###e There is not yet a way for some of the array to be set to a virtual array (e.g. a view of part of another array or set).
    See also: MapListToExpr, ArgList [nim], InstanceDict [nim], StateArg [nim].
    """
    #e should change to descriptor class... [why is that not easier than it is?]
    #e implem of type_expr coercion: depending on type & options, wrap with glue code when set, or coerce in simple way when set
    #e options: doc, debug_name
    #e somehow the State finds out its argname -- i think (does it really?) -- we might want that in debug_name
    return State( StateArrayRefs_type, call_Expr(_make_StateArrayRefs, type_expr, dfltval_expr, _E_ATTR, _self, **kws)) #k this use of **kws
        ###k i *think* that this will eval dfltval_expr once per Instance (w/o tracking, since it's part of State's default val expr)
        # at the time the StateArrayRefs attr is first accessed (e.g. for set or get of an element).

def _make_StateArrayRefs(type_expr, dfltval_expr, attr, self, debug_name = None):
    "[private helper for StateArrayRefs]"
    # print "debug fyi: _make_StateArrayRefs type_expr = %r, dfltval_expr = %r, attr = %r, self = %r, debug_name = %r" % \
    #       (type_expr, dfltval_expr, attr, self, debug_name)
        ## example of what this prints:
        ## type_expr = <lexenv_ipath_Expr#20244: <widget_env at 0xf51d9e0 (_self = <test_StateArrayRefs_2#20226(i)>)>,
        ##       (1, ('heights', ((-108, 0), ((-104, 0), (-101, '.'))))), S.Anything>,
        ## dfltval_expr = array([ 0.,  0.,  0.]),
        ## attr = 'heights',
        ## self = <test_StateArrayRefs_2#20226(i)>,
        ## debug_name = None
    ###NOTE: dfltval_expr is probably always a constant_Expr or maybe even just a constant -- not sure -- might need to Hold it
    # in the call and eval it here (which would be best anyway) ####e
    if debug_name:
        attr ###e maybe get this passed in (as a positional arg, always supplied) [this will fail for now, so debug_name is nim]
        debug_name = "%s.%s" % (debug_name, attr) # if we know the attr ###k not sure this copied code makes sense here
    ## valfunc = f(dfltval_expr) ###e maybe eval this expr (or even instantiate it???) in the env... get the env passed in somehow
        #e digr: can call_Expr have a feature that the value of self it's evaluating within can be passed to it?
        #e       or should we just require the explicit use of _self in its arglist? (The latter.)
        ###e digr: getting a dflt passed in must relate to StateArg somehow
    # valfunc will be applied to key in order to recompute the value at key (only if it's accessed before first set)
    constant_default_val = dfltval_expr ####WRONG
    valfunc = lambda key: constant_default_val
    return LvalDict2(valfunc, LvalForState, debug_name = debug_name)
        ###BUG - elts of this are the lvals, not their values!!! But if not for that, how would we make setitem work in this?!?
        ### I think we need to return a new object which implements __setitem__ by passing it into the lvals properly.
        ###e But we also need access to per-element staterefs,
        # e.g. we need that in the first use of this in test_statearray.py or a related file.
        # [see also StateArrayRefs_getitem_as_stateref]

def StateArrayRefs_getitem_as_stateref(statearrayrefs, index): #070313 renamed getitem_stateref to StateArrayRefs_getitem_as_stateref
    "#doc; args are values not exprs in the present form, but maybe can also be exprs someday, returning an expr..."
    if 'arg1 is a StateArrayRefs, not a StateArray':
        return statearrayrefs[index] # WARNING:
            # this only works due to a bug in the initial stub implem for StateArray --
            # now declared a feature due to its being renamed to StateArrayRefs -- in which self.attr
            # is valued as a dict of LvalForState objects rather than of settable/gettable item values,
            # and *also* because I changed LvalForState to conform to the new StateRefInterface so it actually
            # has a settable/gettable .value attribute.
            ##### When that bug in StateArray is fixed, this code would be WRONG if applied to a real StateArray.
            # What we need is to ask for an lval or stateref for that StateArray at that index!
            # Can we do that using getitem_Expr (re semantics, reasonableness, and efficiency)? ##k
    else:
        StateRef_from_lvalue = 'nim'
        from exprs.Exprs import getitem_Expr # apparently the only use of that, and never runs, and requires an extension of it...
        return StateRef_from_lvalue( getitem_Expr(statearrayrefs, index))
            ###IMPLEM this getitem_Expr behavior (proposed, not yet decided for sure; easy, see getattr_Expr for how)
            ###IMPLEM StateRef_from_lvalue if I can think of a decent name for it, and if I really want it around
    pass

# ==

StateArray = Stub

# end
