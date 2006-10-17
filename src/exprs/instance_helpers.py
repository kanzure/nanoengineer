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

class Instance:
    #e call _init_instance, etc;
    # rename? Instance, FormulaInstance... note also Expr, ExprHelper can be instances
    pass

class InstanceOrExpr(Instance, Expr): ####@@@@ guess; act like one or other depending on how inited, whether args are insts
    ### WARNING: instantiate normally lets parent env determine kid env... if arg is inst this seems reversed...
    # may only be ok if parent doesn't want to modify lexenv for kid.
    is_instance = False # usually overridden in certain python instances, not in subclasses
    has_args = False # ditto
    args = () # convenient default
    def __init__(self, *args, **kws):
        ###e does place (instanceness) come in from kws or any args?
##        val = kws.pop('_destructive_customize', None)
##        if val:
##            assert not args and not kws
##            self._destructive_customize(val)
##            return
        # initialize attrs of self to an owned empty state for an expr
        self._e_formula_dict = {}
        # handle special keywords (assume they all want self to be initialized as we just did above)
        val = kws.pop('_copy_of', None)
        if val:
            assert not args and not kws
            self._destructive_copy(val)
            return
        #e
        # assume no special keywords remain
        self._destructive_init(args, kws)
        return
    def __call__(self, *args, **kws):
        new = self._copy()
        new._destructive_init(args, kws)
        return new

    # copy methods (used by __call__)
    def _copy(self):
        return self.__class__(_copy_of = self) # this calls _destructive_copy on the new instance
    def _destructive_copy(self, old):
        """[private]
        Modify self to be a copy of old, an expr of the same class.
        """
        assert not self.is_instance
        # self has to own its own mutable copies of the expr data in old, or own objects which inherit from them on demand.
        self._e_formula_dict = dict(old._e_formula_dict) ###k too simple, but might work at first; make it a FormulaSet object??
        self.args = old.args # not mutable, needn't copy; always present even if not self.has_args (for convenience, here & in replace)
        self.has_args = old.has_args
        return

    # common private submethods of __init__ and __call__
    def _destructive_init(self, args, kws):
        """[private, called by __init__ or indirectly by __call__]
        Modify self to give it optional args and optional ordinary keyword args.
        """
        for kw in kws:
            if kw.startswith('_'):
                print "warning or error: this kw is being treated normally:", kw ###@@@ is this always an error?
        if kws:
            self._destructive_customize(kws)
        if args or not kws:
            self._destructive_supply_args(args)
        return
    def _destructive_customize(self, kws):
        """[private]
        Destructively modify self, an expr, customizing it with the formulas represented by the given keyword arguments.
        """
        assert not self.is_instance
        self._e_formula_dict.update(kws) # this dict is owned (inefficient?)
        return
    def _destructive_supply_args(self, args):
        """[private]
        Destructively modify self, an expr, supplying it with the given argument formulas.
        """
        assert not self.is_instance
        assert not self.has_args
        self.has_args = True # useful in case args is (), though hasattr(self, 'args') might be good enough too #e
        self.args = args
        #e when do we fill in defaults for missing args, and type-coerce all args? For now, I guess we'll wait til instantiation.
        # this scheme needs some modification once we have exprs that can accept multiple arglists...
        # one way would be for the above assert to change to an if, which stashed the old args somewhere else,
        # and made sure to ask instantiation if that was ok; but better is to have a typedecl, checked now, which knows if it is. ###@@@
        return

    # instantiation methods
    def _make_in(self, env):
        "Instantiate self in env."
        # no need to copy the formulas or args, since they're shared among all instances, so don't call self._copy.
        # instead, make a new instance in a similar way.
        return self.__class__(_make_in = (self,env)) # this calls _destructive_make_in on the new instance
    def _destructive_make_in(self, data):
        """[private]
        This is the main instantiation method.
        For old, env = data, modify self to be an instance of old, in the given env.
        """
        old, env = data ###@@@ might need more: ipath, and/or split env into rules & place
        assert not self.is_instance
        self.is_instance = True

        self.env = env #k ok, or does it need modification of some kind? btw is a state index passed in separately? set self.index??
        ####@@@@
        
        # set up self.args and self.opts
        self._e_class = old # for access to _e_formula_dict and args #k needed?
        assert old.has_args # we might allow exceptions to this later, based on type decl
        self.has_args = old.has_args #k ??
        self.args = old.args # for convenient access
        nim ##### SHOULD MODIFY ARGS BY ADDING DEFAULTS AND TYPE COERCERS
        ### AND set up self.opts to access old._e_formula_dict, also perhaps adding effect of type coercers
        ### AND have some way to get defaults from env
        ### AND take care of rules in env -- now is the time to decide this is not the right implem class -- or did caller do that?
        ### and did caller perhaps also handle adding of type coercers, using our decl??

        # set up state refs
        ####
        nim

        # call subclass-specific instantiation code (it should make kids, perhaps lazily; anything else?? ###@@@)
        self._init_instance()
        return
    def _init_instance(self): #e move to Instance superclass?
        "[subclasses should replace this]"
        pass
    pass # end of class InstanceOrExpr

##### CANNIBALIZE THESE RELATED SNIPPETS to fill in InstanceOrExpr:
    
class xxx_obs: # widget expr head helper class, a kind of expr 
    def make_in(self, tstateplace, env):
        return self.__class__(self, tstateplace, env, _make_in = True) #####@@@@@ tell __init__ about this
            # note: _make_in causes all args to be interpreted specially
    def __init__(self): ##### or merge with the one in Expr, same for __call__
        pass
    pass

class Drawable_obs(Expr): # like Rect or Color or If
    """Instances of subclasses of this can be unplaced or placed (aka "instantiated");
    if placed, they might be formulas (dependent on aspects of drawing-env state)
    for appearance and behavior (justifying the name Drawable),
    or for some value used in that (e.g. a color, vector, string).
       Specific subclasses, e.g. Rect, contain code which will be used in placed instances (mainly drawing code)
    unless the env provided an overriding expansion for exprs headed by that subclass.
    If it did, the instance created by placing such an expr will (usually) have some other class.
    """
    def __init__(self, *args, **kws):
        # decide whether to fill, customize, or (private access) copy or place; same for init and call, I think
        _place = kws.pop('_place', False)
        _call = kws.pop('_call', False)
        pass
    def __call__(self, *args, **kws):
        self.__class__(self, args, kws, _call = True)
    
    pass

# ===

# these all need revision of how they're divided, and also, think about whether they are InstanceOrExpr things... ####@@@@

# next two are only used in this file, will get revised completely

class _ObjectMapper(Instance): # renamed from GlueCodeMemoizer; aka MemoizingObjectMapper; ObjectMapper; not useful alone
    #e rename this superclass; it memoizes helper objects made from arg objects (in lvals, so it can remake them if needed)
    "maintain an auto-extending dict (self._dict_of_lvals) of lvals of mapped objects, indexed by whatever objects are used as keys"
    ###e redoc -- more general? how is it not itself just the LvalDict?
    # i mean, what value does it add to that? just being a superclass??
    # well, it does transform _c_helper to _make_formula -- maybe it should turn into a trivial helper function calling LvalDict??
    def _init_instance( self): ### what about env? already in self.env? YES. need Instance superclass?
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
