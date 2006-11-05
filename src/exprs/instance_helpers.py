'''
instance_helpers.py

$Id$
'''

from basic import * # autoreload of basic is done before we're imported

import lvals
reload_once(lvals)
from lvals import LvalDict

import Exprs
reload_once(Exprs)
from Exprs import * # at least Expr; note, basic now does this anyway

# ==

class Instance:#k super? meta? [#obs -- as of 061103 i am guessing this will completely disappear -- but i'm not sure]
    "support all behavior needed by pure instances #[doc better] (which may or may not also be Exprs)"
    # WARNING: much of the code in InstanceOrExpr might belong here. OTOH it might not make sense to split this out,
    # since no method here can assume self is not a noninstance expr, even a method of this class, since self might be InstanceOrExpr.
    #e call _init_instance, etc;
    # rename? Instance, FormulaInstance... note also Expr, ExprHelper can be instances
    pass

class InstanceOrExpr(Instance, Expr): # see docstring for discussion of the basic kluge of using one class for both
    """Main superclass for specific kinds of Instance classes whose python instances can be either Instances or Exprs,
    and (more importantly for the user) whose use as a constructor usually constructs an Expr.
    Used (for example) for Column, Rect, If, Widget2D, etc. See elsewhere for general explanation [#nim].
       The rest of this docstring discusses some fine points of the class semantics and implementation,
    and possible changes to them.
       Kluge: the same class is used to represent both Exprs and Instances of the same type; the difference is encoded
    in self._e_is_instance, and is constant throughout one python-instance's lifetime (after it's fully constructed,
    which means, after __init__ and perhaps after immediately subsequent private methods in another Expr which created it).
    Many methods either assert a specific state for self._e_is_instance, or branch on it (or ought to #e).
       Pro: developer can create and use just one class, e.g. Rect, needing no other setup/registration except defining it,
    to both hold the Rect Instance methods, and serve as the Rect Expr constructor. The Instance methods can be written
    (after an initial assertion) as if self is the Instance (as opposed to self.instance, or some argument they receive),
    and (to avoid unpleasant surprises) that's actually true. And the class as constructor always constructs a Python instance
    of itself, as one would expect.
       Con: the Instance methods could be accidently requested in an Expr version, or vice versa; their very presence
    might mess up some semantics, since it's generally bad if expr.attr does anything except construct a getattr_Expr.
    The motivations above are not obviously good enough to justify the bug risk and internal-method unclarity.
       Possible issues in present implem: constant_Expr(10) is in some sense both an Expr *and* an Instance. The predicates
    don't yet account for this. And logic bugs in the whole scheme may yet show up.
       Possible alternative: these classes could represent only Instances, but still be usable as Expr constructors,
    by having __new__ create a separate (nim) ExprForInstanceOrExpr object which is not a subclass of this class,
    but which knows which subclass of this class to create when it needs to make Instances from itself. If this was done,
    much of the code in this specific class InstanceOrExpr would be moved to ExprForInstanceOrExpr, which might be renamed
    to be more general since it would really apply to any Expr which can be called, remaining an Expr but having its
    option formulas customized or its arg formulas supplied, and can then later be instantiated in an env to produce
    a specific Instance based on those formulas.
    """
    __metaclass__ = ExprsMeta
    #e rename to: ExprOrInstance?
    #  [maybe, until i rename Instance, if i do... con side: most methods in each one are mainly for Instance, except arg decls,
    #   and even they can be thought of mostly as per-instance-evalled formulas. So when coding it, think Instance first.]
    # PatternOrThing?[no]
    ### WARNING: instantiate normally lets parent env determine kid env... if arg is inst this seems reversed...
    # may only be ok if parent doesn't want to modify lexenv for kid.
    ## _e_is_instance = False # now done in class Expr # usually overridden in certain python instances, not in subclasses
    ## _e_has_args = False # ditto
    args = () # convenient default
    def __init__(self, *args, **kws):
        # note: just before any return herein, we must call self._init_e_serno_(), so it's called after any canon_expr we do;
        # also, the caller (if a private method in us) can then do one inside us; see comment where this is handled in __call__
        ###e does place (instanceness) come in from kws or any args?
##        val = kws.pop('_destructive_customize', None)
##        if val:
##            assert not args and not kws
##            self._destructive_customize(val)
##            return
        # initialize attrs of self to an owned empty state for an expr
        self._e_formula_dict = {} ####k is there some reason I can't rename this self.opts??
        # handle special keywords (assume they all want self to be initialized as we just did above)
        val = kws.pop('_copy_of', None)
        if val:
            assert not args and not kws
            self._destructive_copy(val)
            self._init_e_serno_()
            return
        val = kws.pop('_make_in', None)
        if val:
            assert not args and not kws
            self._destructive_make_in(val)
            self._init_e_serno_()
            return
        #e
        # assume no special keywords remain
        self._destructive_init(args, kws)
        self._init_e_serno_()
        return
    def __call__(self, *args, **kws):
        new = self._copy()
        new._destructive_init(args, kws)
        new._init_e_serno_()
            # note, this "wastes a serno" by allocating a newer one that new.__init__ did;
            # this is necessary to make serno newer than any exprs produced by canon_expr during _destructive_init
        return new

    # public access to self._e_formula_dict
    def custom_compute_method(self, attr):
        "#doc; return a compute method or None"
        try:
            formula = self._e_formula_dict[attr]
        except KeyError:
            return None
        printnim("assume it's a formula in _self; someday optim for when it's a constant, and/or support other symbols in it")
        return formula._e_compute_method(self)
    
    # copy methods (used by __call__)
    def _copy(self):
        assert not self._e_is_instance ## ??? [061019]
        return self.__class__(_copy_of = self) # this calls _destructive_copy on the new instance
    def _destructive_copy(self, old):
        """[private]
        Modify self to be a copy of old, an expr of the same class.
        """
        assert not self._e_is_instance
        # self has to own its own mutable copies of the expr data in old, or own objects which inherit from them on demand.
        self._e_formula_dict = dict(old._e_formula_dict) ###k too simple, but might work at first; make it a FormulaSet object??
        self.args = old.args # not mutable, needn't copy; always present even if not self._e_has_args (for convenience, here & in replace)
        self._e_has_args = old._e_has_args
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
        assert not self._e_is_instance
        # self._e_formula_dict dict is owned by every non-instance customized expr (inefficient?)
        # but it's shared by Instances and their expr templates
        from Exprs import canon_expr
        # don't do this, since we need canon_expr:
        ## self._e_formula_dict.update(kws)
        for k,v in kws.iteritems():
            self._e_formula_dict[k] = canon_expr(v)
        return
    def _destructive_supply_args(self, args):
        """[private]
        Destructively modify self, an expr, supplying it with the given argument formulas.
        """
        assert not self._e_is_instance
        assert not self._e_has_args
        self._e_has_args = True # useful in case args is (), though hasattr(self, 'args') might be good enough too #e

        from Exprs import canon_expr
        args = tuple(map(canon_expr, args))
        self.args = args

        # also store the args in equivalent options, according to self._args declaration
        # Q: Should we do this on instantiation instead?
        # A: Probably not -- if you supply an option by positional arg, then later (i.e. in a later __call__) by named option,
        # maybe it should work (as it does now in the following code), or maybe it should be an error,
        # but it probably shouldn't be silently ignored.
        #  Note: right now, since internal & public options are not distinguished, you could do funny things like
        # customize the value of _args itself! That might even make sense, if documented.
        _args = getattr(self, '_args', None) #e make a class attr default for _args
        if _args:
            if type(_args) is type(""):
                # permit this special case for convenience
                _args = (_args,)
            if not (type(_args) is type(())):
                # note: printed only once per value of _args (which might be lots of times, but not as many as for each error)
                printnim( "_args should have type(()) but doesn't; its value is %r" % (_args,) )
                    # this once happened since I said ('thing') when I meant ('thing',). Should the first case be allowed,
                    # as a special case for convenience? Probably yes, since the values have to be strings.
                    # We could even canonicalize it here.
            ###e also extend the decl format for equiv of * or **, and rename it _argnames or something else (see small paper note)
            args = self.args
            argnames = _args
            for i in range(min(len(argnames), len(args))):
                name = argnames[i]
                val = args[i]
                assert type(name) is type("")
                self._e_formula_dict[name] = val
                continue
            pass
        
        # Q. When do we fill in defaults for missing args? A. We don't -- the above code + options code effectively handles that,
        # PROVIDED we access them by name, not by position in self.args. (Is it reasonable to require that?? ###k)
        # Q. When do we type-coerce all args? For now, I guess we'll wait til instantiation. [And it's nim.]
        printnim("type coercion of args & optvals is nim")
        printnim("so is provision for multiple arglists,")
        printnim("so is * or ** argdecls,")
        printnim("so is checking for optnames being legal, or not internal attrnames")
        # Note: this scheme needs some modification once we have exprs that can accept multiple arglists...
        # one way would be for the above assert [which one? I guess the not self._e_has_args]
        # to change to an if, which stashed the old args somewhere else,
        # and made sure to ask instantiation if that was ok; but better is to have a typedecl, checked now, which knows if it is. ###@@@
        return # from _destructive_supply_args

    # instantiation methods
    def _e_make_in(self, env, ipath):
        "Instantiate self in env, at the given index-path."
        # no need to copy the formulas or args, since they're shared among all instances, so don't call self._copy.
        # instead, make a new instance in a similar way.
        assert not self._e_is_instance
        return self.__class__(_make_in = (self,env,ipath)) # this calls _destructive_make_in on the new instance
    def _destructive_make_in(self, data):
        """[private]
        This is the main internal instantiation-helper method.
        For expr, env, ipath = data, modify self to be an instance of expr, in the given env, at the given index-path.
        Called only from __init__, when self knows nothing except its class.
        """
        expr, env, ipath = data ###@@@ might want to split env into rules (incl lexenv) & place (incl staterefs, glpane)
        assert not self._e_is_instance #e remove when works
        assert not expr._e_is_instance
        self._e_is_instance = True

        self.env = env #k ok, or does it need modification of some kind? btw is a state index passed in separately? set self.index??
        ####@@@@
        self.ipath = ipath ###e does this need mixing into self.env somehow?
        
        # set up self.args and self.opts
        self._e_class = expr # for access to _e_formula_dict and args #k needed? #e rename: self.expr?? nah. well, not sure.
        assert expr._e_has_args # we might allow exceptions to this later, based on type decl
        self._e_has_args = expr._e_has_args #k ??
        self.args = expr.args # for convenient access ### is it ok that we're putting the bare ones here? Don't we want to hide those?
        # or can we do the type & instancing on these exprs, to get the declared specific args?

        ## print "fyi my metaclass is",self.__metaclass__ # <class 'exprs.ExprsMeta.ExprsMeta'>

        printonce("nim make in %r" % self.__class__)#####@@@@@
        ## assert 0, "nim make in %r" % self ##### SHOULD MODIFY ARGS BY ADDING TYPE COERCERS


        ### AND set up self.opts to access old._e_formula_dict, also perhaps adding effect of type coercers
        ## print "compare self #formulas %d vs expr #formulas %d" % (len(self._e_formula_dict), len( expr._e_formula_dict)) # 0,3
        self._e_formula_dict = expr._e_formula_dict # kluge, no protection from bug that modifies it, but nothing is supposed to
        ## print "self._e_formula_dict =",self._e_formula_dict
##        for k,v in self._e_formula_dict.items():
##            printnim("##HORRIBLE KLUGE just for testing - canon_expr every time")#######@@@@@@@@
##            from Exprs import canon_expr
##            self._e_formula_dict[k] = canon_expr(v)
        ### AND have some way to get defaults from env
        ### AND take care of rules in env -- now is the time to decide this is not the right implem class -- or did caller do that?
        ### and did caller perhaps also handle adding of type coercers, using our decl??

        # 061020 hopes:
        # maybe we can work for all, incl OpExprs & iterators, by only setting up RULES to instantiate,
        # which if not used, never happen. self.kids.<index/attr path> has to come from some self.arg or self.opt...
        # index always comes from <index/attr path> and *not* from which arg or opt, i think... sometimes they correspond,
        # and some predeclared members of kids could access those for you, e.g. self.kids.args or just self.args for short...
        # we could even say _e_args for the raw ones, .args for the cooked ones.

        # set up state refs
        ####
        printonce("setup state refs is nim in instance_helpers")#####@@@@@

        #e call _init_class and/or _init_expr if needed [here or more likely earlier]

        self._i_instance_exprs = {}
        
        # call subclass-specific instantiation code (it should make kids, perhaps lazily, if above didn't; anything else?? ###@@@)
        self._init_instance()
        return # from _destructive_make_in
    
    def _init_class(self): #e move to Instance superclass? ###@@@ CALL ME
        """called once per directly-instantiated python class, when its first python instance is created
        [subclasses should replace this]
        """
        pass
    def _init_expr(self): #e move to Instance superclass? ###@@@ CALL ME
        """called once per Expr when it gets its args [details unclear, maybe not yet needed]
        [subclasses should replace this]
        """
        pass
    def _init_instance(self): #e move to Instance superclass? let it be name-mangled, and call in mro order?
        """called once per python instance, but only when it represents a semantic Instance ###doc -- explain better
        [subclasses should replace this]
        """
        pass

    def _e_eval(self, env, ipath):
        assert self._e_is_instance, "%r._e_eval asserts it's an Instance... not sure this is an error, it's just unexpected" % self ###@@@
        printnim("Instance eval doesn't yet handle _value or If") ###@@@
        return self # true for most of them, false for the ones that have _value (like Boxed) or for If ####@@@@

    # kid-instantiation, to support use of Arg, Option, Instance, etc
    #k (not sure this is not needed in some other classes too, but all known needs are here)
    
    def _i_instance( self, expr, index ):
        """[semi-private; used by macros like Instance, Arg, Option]
        Find or create (or perhaps recompute if invalid, but only the latest version is memoized) (and return)
        an Instance of expr, contained in self, at the given relative index, and in the same env [#e generalize env later?].
           Error (perhaps not detected) if called with same index and different other args;
        when a cached instance is returned, the other args are not used except perhaps to check for this error.
        (When an instance is recomputed, if this error happens, are new args used? undefined.)
        (#e Should we change this to make the expr effectively part of the index, for caching? Probably not; not sure.)
        (#e Should we change this to make it legal to pass a new expr? Probably not... hard for subsequent callers to be consistent...)
        """
        assert is_pure_expr(expr), "who passed non-pure-expr %r to _i_instance? index %r, self %r, _e_args %r" % \
               (expr, index, self, self._e_args)
            #k guess 061105
        # hmm, calling Instance macro evals the expr first... can't it turn out that it changes over time?
        # I think yes... not only that, a lot of change in it should be buried inside the instance! (if it's in an arg formula)
        # as if we need to "instantiate the expr" before actually passing it... hmm, if so this is a SERIOUS LOGIC BUG. ####@@@@
        # WAIT -- can it be that the expr never changes? only its value does? and that we should pass the unevaluated expr? YES.
        # But i forgot, eval of an expr is that expr! I get confused since _e_eval evals an implicit instance -- rename it soon! ###@@@
        oldexpr = self._i_instance_exprs.get(index, None) # see above comment
        if oldexpr is not expr:
            if oldexpr is not None:
                print "bug: expr for instance changed",self,index,expr #e more info? i think this is an error and should not happen normally
                #e if it does happen, should we inval that instance? yes, if this ever happens without error.
            self._i_instance_exprs[index] = expr
        return self._i_instance_CVdict[index] # takes care of invals in making process? or are they impossible? ##k
    def _CV__i_instance_CVdict(self, index):
        """[private] value-recomputing function for self._i_instance_CVdict.
        Before calling this, the caller must store an expr for this instance
        into self._i_instance_exprs[index] (an ordinary dict).
           If it's permitted for that expr to change with time (which I doubt, but don't know yet for sure #k),
        then whenever the caller changes it (other than when initially setting it), the caller must invalidate
        the entry with the same key (our index arg) in the LvalDict2 that implements self._i_instance_CVdict
        (but the API for the caller to do that is not yet worked out #e).
           (Implem note: _CV_ stands for "compute value" to ExprsMeta, which implements the LvalDict2 associated with this.
        This method needs no corresponding _CK_ keylist function, since any key (instance index) asked for is assumed valid.)
        """
        print "fyi in %r, computing _i_instance(index = %r)" % (self, index)###@@@
        assert self._e_is_instance
        # This method needs to create a new instance, by instantiating expr and giving it index.
        # Implem notes:
        # - the glue code added by _CV_ from self._i_instance_CVdict to this method (by ExprsMeta) uses LvalDict2
        #   to cache values computed by this method, and recompute them if needed (which may never happen, I'm not sure).
        # - the access to self._i_instance_exprs[index] is not usage tracked;
        #   thus if we change it above w/o error, an inval is needed.
        expr = self._i_instance_exprs[index]
        print "fyi, using kid expr %r" % expr ###@@@
            # Note, this expr can be very simplifiable, if it came from an Arg macro,
            # but present code [061105] reevals the full macro expansion each time -- suboptimal.
            # To fix, we'd need an "expr simplify", whether we used it only once or not...
            # the reason to use it more than once is if it becomes partly final at some later point than when it starts out.
            # The simplify implem would need decls about finality of, e.g., getting of some bound methods and (determinism of)
            # their retvals -- namely (for Arg macro etc) for _i_instance and _i_grabarg and maybe more.
            # Feasible but not simple; worthwhile optim someday but not right away. ##e
        # three increasingly strict asserts:
        assert expr is not None
        assert is_Expr(expr), "not is_Expr: %r" % (expr,)
        assert is_pure_expr(expr) ###k?? what if someone passes an instance -- is that permitted, but a noop for instantiation??
        # also assume expr is "canonicalized" and even "understood" -- not sure if this is justified
        printnim("don't we need understand_expr somewhere in here? (before kidmaking in IorE)") ###@@@
        env = self.env #e with lexmods?
        index_path = (index, self.ipath)
        ####e: is _e_eval actually needing to be different from _e_make_in?? yes, _e_eval needs to be told _self
        # and the other needs to make one... no wait, wrong, different selves --
        # the _self told to eval is the one _make_in *should make something inside of*! (ie should make a kid of)
        # So it may be that these are actually the same thing. (See paper notes from today for more about this.)
        # For now, tho, we'll define _e_make_in on OpExpr to use eval. [not done, where i am]
        return expr._e_make_in(env, index_path)

    def _i_grabarg( self, attr, argpos, dflt): 
        "#doc, especially the special values for some of these args"
        #k below should not _e_eval or canon_expr without review -- should return an arg or dflt expr, not its value
        # (tho for now it also can return None on error -- probably causing bugs in callers)
        assert is_pure_expr(dflt), "_i_grabarg dflt should be an expr, not %r" % (dflt,) #061105 - or use canon_expr?
        assert self._e_is_instance
        if not self._e_has_args:
            print "warning: possible bug: not self._e_has_args in _i_grabarg" ###k #e more info
        assert attr is None or isinstance(attr, str)
        assert argpos is None or (isinstance(argpos, int) and argpos >= 0)
        # i think dflt can be _E_REQUIRED_ARG_, or any sort of python object
        from __Symbols__ import _E_REQUIRED_ARG_
        if dflt is _E_REQUIRED_ARG_:
            required = True
        else:
            required = False
            assert not isinstance(dflt, _E_REQUIRED_ARG_.__class__)
                # kluge sanity check -- not a Symbol #e remove when works, probably not even justified in general
                #e or replace with "not a Symbol whose name starts _E_" ??
        if attr is not None and argpos is not None:
            printnim("assert an arg is not provided in both ways")###e
        if attr is not None:
            # try to find it in _e_kws; I suppose the cond is an optim or for clarity, since None won't be a key of _e_kws
            try:
                return self._e_kws[attr]
            except KeyError:
                pass
        if argpos is not None:
            try:
                return self._e_args[argpos]
            except IndexError: # "tuple index out of range"
                pass
        # arg was not provided -- error or use dflt.
        if required:
            printnim( "error: required arg not provided. Instance maker should have complained! Using None.")
            return None ###k NOT canon_expr -- we're dealing in values, which needn't be exprs, tho they might be.
        else:
            ## ANTI_OPTIM OR BUG -- we were provided directly with dflt, not dflt_expr, due to semantics of call_Expr, etc.
            # ought to make the macro wrap it so it's not evalled... maybe even stick it on an attr to be memoized?
            # nah, the decision to use it is constant per instance! but OTOH, nothing memoizes what we return!
            # So we should in fact do that here, iff we ever compute it.
            printnim("don't eval dflt if not needed! and memoize it if needed. (Maybe required optim or bugfix.)")
            #e and eval it here in that case
            printnim("isn't there an issue with exprs for making, shouldn't be evalled... or not, if eval is themselves... ???")###k
            return dflt
        pass # above should not _e_eval or canon_expr without review -- should return an arg or dflt expr, not its value
    
    pass # end of class InstanceOrExpr

##### CANNIBALIZE THESE RELATED SNIPPETS to fill in InstanceOrExpr: Drawable_obs, old class xxx

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

class DelegatingInstanceOrExpr(InstanceOrExpr): #061020
    "#doc: like Delegator, but self.delegate is recomputable from _C_delegate as defined by subclass"
    def _C_delegate(self):
        assert 0, "must be overridden by subclass to return object to delegate to at the moment"
    def __getattr__(self, attr):
        try:
            return InstanceOrExpr.__getattr__(self, attr) # handles _C_ methods via InvalidatableAttrsMixin
                # note, _C__attr for _attr starting with _ is permitted.
        except AttributeError:
            if attr.startswith('_'):
                raise AttributeError, attr # not just an optim -- we don't want to delegate these.
            return getattr(self.delegate, attr) # here is where we delegate.
    pass

DelegatingInstance = DelegatingInstanceOrExpr #k ok? (for when you don't need the expr behavior, but (i hope) don't mind it either)


class GlueCodeMemoizer( DelegatingInstanceOrExpr): ##e rename WrapperMemoizer? WrappedObjectMemoizer? WrappedInstanceMemoizer? probably yes [061020]
    """Superclass for an InstanceOrExpr which maps instances to memoized wrapped versions of themselves,
    constructed according to the method ###xxx (_make_wrapped_obj?) in each subclass, and delegates to the wrapped versions.
    """
    # renamed to InstanceWrapper from DelegatingObjectMapper -- Wrapper? WrapAdder? Dynamic Wrapper? GlueCodeAdder? InstanceWrapper!
    # but [061020] I keep remembering it as GlueCodeMapper or GlueCodeMemoizer, and GlueCodeMemoizer was an old name for a private superclass!
    # So I'll rename again, to GlueCodeMemoizer for now.
    ###e 061009 -- should be a single class, and renamed;
    # known uses: CLE, value-type-coercers in general (but not all reasonable uses are coercers);
    # in fact [061020], should it be the usual way to find all kids? maybe not, e.g. CL does not use this pattern, it puts CLE around non-fixed arginsts.
    def _C_delegate(self): # renamed from _eval_my_arg
        arg = self.args[0] # formula instance
        argval = arg.eval() ###k might need something passed to it (but prob not, it's an instance, it has an env)
        ####@@@@ might be arg.value instead; need to understand how it relates to _value in Boxed [061020]
            #### isn't this just get_value? well, not really, since it needs to do usage tracking into the env...
            # maybe that does, if we don't pass another place?? or call its compute_value method??
            # argval might be arg, btw; it's an instance with a fixed type (or perhaps a python constant data value, e.g. None)
        #e might look at type now, be special if not recognized or for None, depending on memo policy for those funny types
        lval = self._dict_of_lvals[argval]
        return lval.get_value()
    def _C__dict_of_lvals(self): #e rename self._dict_of_lvals -- it holds lvals for recomputing/memoizing our glue objects, keyed by inner objects
        ##e assert the value we're about to return will never need recomputing?
        # this method is just a way to init this constant (tho mutable) attr, without overriding _init_instance.
        assert self._e_is_instance
        return LvalDict( self._recomputer_for_wrapped_version_of_one_instance)
            #e make a variant of LvalDict that accepts _make_wrapped_obj directly?? I think I did, LvalDict2 -- try it here ####@@@@
        ## try this: return LvalDict2( self._make_wrapped_obj ) # then zap _recomputer_for_wrapped_version_of_one_instance ####e
            ##e pass arg to warn if any usage gets tracked within these lvals (since i think none will be)??
            # actually this depends on the subclass's _make_wrapped_obj method.
            # More generally -- we want schemes for requesting warnings if invals occur more often than they would
            # if we depended only on a given set of values. #e
            ####@@@@
    def _make_wrapped_obj( self, fixed_type_instance ):
        """Given an Instance of fixed type, wrap it with appropriate glue code."""
        assert 0, "subclass must implement this"
    def _recomputer_for_wrapped_version_of_one_instance( self, instance):
        """[private]
        This is what we do to _make_wrapped_obj so we can pass it to LvalDict, which wants us to return a recomputer that knows all its args.
        We return something that wants no args when called, but contains instance and can pass it to self._make_wrapped_obj.
        """
        # We use the lambda kluge always needed for closures in Python, with a guard to assert it is never passed any arguments.
        def _wrapped_recomputer(_guard_ = None, instance = instance):
            assert _guard_ is None
            return self._make_wrapped_obj( fixed_type_instance) # _make_wrapped_obj comes from subclass of GlueCodeMemoizer
        return _wrapped_recomputer
    # obs comments about whether _make_wrapped_obj and LvalDict should be packaged into a helper function or class:
    "maintain an auto-extending dict (self._dict_of_lvals) of lvals of mapped objects, indexed by whatever objects are used as keys"
    ###e redoc -- more general? how is it not itself just the LvalDict?
    # i mean, what value does it add to that? just being a superclass??
    # well, it does transform _make_wrapped_obj to _recomputer_for_wrapped_version_of_one_instance --
    # maybe it should turn into a trivial helper function calling LvalDict?? ie to the variant of LvalDict mentioned above??
    pass

# HelperClass, LayoutWidget2D, etc -- some might be in another file if drawing-specific -- widgetexprs.py ? layout.py? widget2d.py?

# end
