'''
instance_helpers.py

$Id$
'''

from basic import * # autoreload of basic is done before we're imported

import lvals
reload_once(lvals)

from lvals import InvalidatableAttrsMixin, LvalDict

import Exprs
reload_once(Exprs)

from Exprs import Expr

# ==

class Instance: pass # call _init_instance, etc; rename? Instance, FormulaInstance... note also Expr, ExprHelper can be instances

class InstanceOrExpr(Instance, Expr): pass ####@@@@ guess; act like one or other depending on how inited, whether args are insts
    ### WARNING: instantiate normally lets parent env determine kid env... if arg is inst this seems reversed...
    # may only be ok if parent doesn't want to modify lexenv for kid.
    def __init__(self, *args, **kws):
        ###e does place (instanceness) come in from kws or any args?
        print "InstanceOrExpr.__init__ nim, class %r" % self.__class__.__name__
        return
    pass

# these all need revision of how they're divided, and also, think about whether they are InstanceOrExpr things... ####@@@@

# next two are only used in this file, will get revised completely

class _ObjectMapper(Instance): # renamed from GlueCodeMemoizer; aka MemoizingObjectMapper; ObjectMapper; not useful alone
    #e rename this superclass; it memoizes helper objects made from arg objects (in lvals, so it can remake them if needed)
    "maintain an auto-extending dict (self._dict_of_lvals) of lvals of mapped objects, indexed by whatever objects are used as keys"
    ###e redoc -- more general? how is it not itself just the LvalDict?
    # i mean, what value does it add to that? just being a superclass??
    # well, it does transform _c_helper to _make_formula -- maybe it should turn into a trivial helper function calling LvalDict??
    def _init_instance( self): ### what about env? already in self.env? need Instance superclass?
        self._dict_of_lvals = LvalDict( self._make_formula)
            ##e pass arg to warn if any usage gets tracked (since i think none will be)??
            # actually this depends on the subclass's _c_helper method.
            # More generally -- we want schemes for requesting warnings if invals occur more often than they would
            # if we depended only on a given set of values. #e
            ####@@@@
        #######@@@@@@@@ why is this an lval? if it used env, should it be?
            ## was: MemoDict( self._make_lval_and_its_formula )
    def _make_formula( self, fixed_type_instance ): 
        """called when we need a new lval to hold the helper instance wrapped around some fixed_type_instance,
        to return formula_callable to make helper, which stores fixed_type_instance inside it
        """
        def formula_callable(_guard_ = None, fixed_type_instance = fixed_type_instance):
            assert _guard_ is None
            return self._c_helper( fixed_type_instance)
        return formula_callable
    pass


class DelegateToComputedDelegate(InvalidatableAttrsMixin): ##e client also must be an Instance... is this a mixin or a base class?
    "#doc: delegator, but self.delegate is recomputed by InvalidatableAttrsMixin using _C_delegate as defined by subclass"
    #e rename, ComputedDelegateInstance ?
    #e can subclass ever also be a "helper class", ie subclass of Expr?
    def _C_delegate(self):
        assert 0, "must be overridden by subclass to return object to delegate to at the moment"
    ###e delegate all attrs to self.delegate, w/o caching --
    ###  WAIT, how is that compatible with __getattr__ handling compute methods? hmm...
    ###e worst case - mix delegator functionality into InvalidatableAttrsMixin somehow.
    # but maybe it's easy - just use theirs, and if it fails, ours.
    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError, attr # not just an optim -- we don't want to delegate these.
        try:
            return InvalidatableAttrsMixin.__getattr__(self, attr) # handles _C_ methods
        except AttributeError:
            return getattr(self.delegate, attr)
    pass

####@@@@e revision guess: following should come from InstanceOrExpr, subclass DelegatingInstanceOrExpr (computed delegate),
# then subclass for how its computed, corr to _ObjectMapper, using a new dictlike util if desired.
class InstanceWrapper(_ObjectMapper, DelegateToComputedDelegate): ####e also inherit InstanceOrExpr somehow
    # renamed from DelegatingObjectMapper -- Wrapper? WrapAdder? Dynamic Wrapper? GlueCodeAdder? InstanceWrapper!
    """Superclass for an InstanceOrExpr which maps instances to memoized wrapped versions of themselves,
    constructed according to the method ###xxx in each subclass, and delegates to the wrapped versions.
    """
    ###e 061009 -- should be a single class, and renamed; known uses: CLE, value-type-coercers in general (but not all reasonable uses are coercers)
    def _C_delegate(self): # renamed from _eval_my_arg
        arg = self.args[0] # formula instance
        argval = arg.eval() ###k might need something passed to it (but prob not, it's an instance, it has an env)
            #### isn't this just get_value? well, not really, since it needs to do usage tracking into the env...
            # maybe that does if we don't pass another place?? or call its compute_value method??
            # argval might be arg, btw; it's an instance with a fixed type (or perhaps a python constant data value, e.g. None)
        #e might look at type now, be special if not recognized or for None, depending on memo policy for those funny types
        lval = self._dict_of_lvals[argval]
        return lval.get_value()
    pass

# HelperClass, LayoutWidget2D, etc -- some might be in another file if drawing-specific -- widgetexprs.py ? layout.py? widget2d.py?
