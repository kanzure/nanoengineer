"""
instance_helpers.py

$Id$
"""

from basic import * # autoreload of basic is done before we're imported
from basic import _self

import lvals
reload_once(lvals)
from lvals import call_but_discard_tracked_usage, LvalError_ValueIsUnset
from lvals import LvalDict1 # only needed by obs code

##import Exprs
##reload_once(Exprs)
##from Exprs import * # at least Expr; note, basic now does this anyway, so this might not be needed

import widget_env
reload_once(widget_env)
from widget_env import thisname_of_class #e refile import?? or make it an env method??

# ==

class InstanceClass:#k super? meta? [#obs -- as of 061103 i am guessing this will completely disappear -- but i'm not sure]
    "support all behavior needed by pure Expr Instances #[doc better] (which may or may not also be Exprs)"
    # WARNING: much of the code in InstanceOrExpr might belong here. OTOH it might not make sense to split this out,
    # since no method here can assume self is not a noninstance expr, even a method of this class, since self might be InstanceOrExpr.
    #e call _init_instance, etc;
    # rename? Instance [no, it's a macro], FormulaInstance... note also Expr, ExprHelper can be instances
    pass

# maybe merge this into InstanceOrExpr docstring:
"""Instances of subclasses of this can be unplaced or placed (aka "instantiated");
if placed, they might be formulas (dependent on aspects of drawing-env state)
for appearance and behavior (justifying the name Drawable),
or for some value used in that (e.g. a color, vector, string).
   Specific subclasses, e.g. Rect, contain code which will be used in placed instances (mainly drawing code)
unless the env provided an overriding expansion for exprs headed by that subclass.
If it did, the instance created by placing such an expr will (usually) have some other class.
"""

class InstanceOrExpr(InstanceClass, Expr): # see docstring for discussion of the basic kluge of using one class for both
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
    #  [maybe, until i rename the term Instance, if i do... con side: most methods in each one are mainly for Instance, except arg decls,
    #   and even they can be thought of mostly as per-instance-evalled formulas. So when coding it, think Instance first.]
    # PatternOrThing?[no]
    ### WARNING: instantiate normally lets parent env determine kid env... if arg is inst this seems reversed...
    # may only be ok if parent doesn't want to modify lexenv for kid.

    # standard stateplaces (other ones can be set up in more specific subclasses)
    # [following 3 StatePlaces moved here from Highlightable & ToggleShow, 061126 late;
    #  these comments not yet reviewed for their new context: ###doc]
    #
    # refs to places to store state of different kinds, all of which is specific to this Instance (or more precisely to its ipath)
    ##e [these will probably turn out to be InstanceOrExpr default formulae] [note: their 2nd arg ipath defaults to _self.ipath]
    # OPTIM QUESTION: which of these actually need usage/mod tracking? They all have it at the moment [not anymore, 061121],
    # but my guess is, per_frame_state doesn't need it, and not providing it would be a big optim. [turned out to be a big bugfix too!]
    # (We might even decide we can store all per_frame_state in self, not needing a StatePlace at all -- bigger optim, I think.
    #  That can be done once reloading or reinstancemaking is not possible during one frame. I'm not sure if it can happen then,
    #  even now... so to be safe I want to store that state externally.)
    transient_state = StatePlace('transient') # state which matters during a drag; scroll-position state; etc
    glpane_state = StatePlace('glpane', tracked = False) # state which is specific to a given glpane [#e will some need tracked=True?]
    per_frame_state = StatePlace('per_frame', tracked = False)
        # state which is only needed while drawing one frame (someday, cleared often)
        # (this is probably also specific to our glpane; note that a given Instance has only one glpane)
    # abbrevs for read-only state [#e should we make them a property or so, so we can set them too?]
    glname = glpane_state.glname # (note, most things don't have this)

    def __init__(self, *args, **kws):
        # note: just before any return herein, we must call self._e_init_e_serno(), so it's called after any canon_expr we do;
        # also, the caller (if a private method in us) can then do one inside us; see comment where this is handled in __call__
        ###e does place (instanceness) come in from kws or any args?
        # initialize attrs of self to an owned empty state for an expr
        self._e_kws = {} # need a fresh dict, since we own it and alter it during subsequent parts of init (??)
        # handle special keywords (assume they all want self to be initialized as we just did above)
        val = kws.pop('_copy_of', None)
        if val:
            assert not args and not kws
            self._destructive_copy(val)
            self._e_init_e_serno()
            return
        val = kws.pop('_make_in', None)
        if val:
            assert not args and not kws
            self._destructive_make_in(val)
            self._e_init_e_serno()
            return
        # assume no special keywords remain
        self._destructive_init(args, kws)
        self._e_init_e_serno()
        return
    def __call__(self, *args, **kws):
        new = self._copy()
        new._destructive_init(args, kws)
        new._e_init_e_serno()
            # note, this "wastes a serno" by allocating a newer one that new.__init__ did;
            # this is necessary to make serno newer than any exprs produced by canon_expr during _destructive_init
        return new

    # deprecated public access to self._e_kws -- used by _DEFAULT_ decls
    def custom_compute_method(self, attr):###NAMECONFLICT?
        "return a compute method using our custom formula for attr, or None if we don't have one"
        try:
            formula = self._e_kws[attr]
        except KeyError:
            # caller will have to use the default case [#k i think]
            return None
        printnim("custom_compute_method likely BUG: uses wrong env for _self") # could fix by passing flag or env to _e_compute_method?
        printnim("assume it's a formula in _self; someday optim for when it's a constant, and/or support other symbols in it")
        #k guess: following printnim is wrong, should be in return None case -- verify then fix (or remove this entire feature)
        printfyi("something made use of deprecated _DEFAULT_ feature on attr %r" % (attr,)) ###e deprecated - remove uses, gradually
        return formula._e_compute_method(self, '@' + attr) #k index arg is a guess, 061110
    
    # copy methods (used by __call__)
    def _copy(self):
        ## assert not self._e_is_instance ## ??? [061019]
        if self._e_is_instance:
            print "WARNING: copying an instance %r" % (self,)
        return self.__class__(_copy_of = self) # this calls _destructive_copy on the new instance
    def _destructive_copy(self, old):
        """[private]
        Modify self to be a copy of old, an expr of the same class.
        """
        assert not self._e_is_instance
        # self has to own its own mutable copies of the expr data in old, or own objects which inherit from them on demand.
        self._e_kws = dict(old._e_kws) ###k too simple, but might work at first; make it a FormulaSet object??
        self._e_args = old._e_args # not mutable, needn't copy; always present even if not self._e_has_args (for convenience, here & in replace)
        self._e_has_args = old._e_has_args
        return

    # common private submethods of __init__ and __call__
    def _destructive_init(self, args, kws):
        """[private, called by __init__ or indirectly by __call__]
        Modify self to give it optional args and optional ordinary keyword args.
        """
# removed this 061212, since it never caught a bug:
##        for kw in kws:
##            if kw.startswith('_'):
##                printfyi( "warning or error: this kw is being treated normally as an option, " \
##                      "not as a special case, in spite of initial '_': %s" % kw) ###@@@ is this always an error?
##                    # so far, happened (but not as error) with _tmpmode, ...
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
        # self._e_kws dict is owned by every non-instance customized expr (inefficient?)
        # but it's shared by Instances and their expr templates
        # don't do this, since we need canon_expr:
        ## self._e_kws.update(kws)
        for k,v in kws.iteritems():
            self._e_kws[k] = canon_expr(v)
        return
    def _destructive_supply_args(self, args):
        """[private]
        Destructively modify self, an expr, supplying it with the given argument formulas.
        """
        assert not self._e_is_instance
        assert not self._e_has_args, "not permitted to re-supply already supplied positional args, in %r" % self # added message 061126
        self._e_has_args = True # needed in case args are supplied as ()

        args = tuple(map(canon_expr, args))
        self._e_args = args

        # also store the args in equivalent options, according to self._args declaration
        # Q: Should we do this on instantiation instead?
        # A: Probably not -- if you supply an option by positional arg, then later (i.e. in a later __call__) by named option,
        # maybe it should work (as it does now in the following code), or maybe it should be an error,
        # but it probably shouldn't be silently ignored.
        #  Note: right now, since internal & public options are not distinguished, you could do funny things like
        # customize the value of _args itself! That might even make sense, if documented.
        _args = getattr(self, '_args', None) #e make a class attr default for _args
        if _args and 'kluge 061113':
            if self._e_is_symbolic:
                # as of 061113 late: happens to _this when constructing _this(class) (I think) --
                # not yet sure whether/how to fix it in SymbolicExpr.__getattr__,
                # so fix it like this for now...
                # as of 061114 I think it will never happen, so also assert 0.
                printnim("better fix for _args when _e_is_symbolic??")##e
                assert 0 # see above comment
                _args = None
        if _args:
            printfyi( "_args is deprecated, but supported for now; in a pyinstance of %r it's %r" % (self.__class__, _args) )#061106
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
            args = self._e_args
            argnames = _args
            for i in range(min(len(argnames), len(args))):
                name = argnames[i]
                val = args[i]
                assert type(name) is type("")
                self._e_kws[name] = val
                continue
            pass
        
        # Q. When do we fill in defaults for missing args? A. We don't -- the above code + options code effectively handles that,
        # PROVIDED we access them by name, not by position in self._e_args. (Is it reasonable to require that?? ###k)
        # Q. When do we type-coerce all args? For now, I guess we'll wait til instantiation. [And it's nim.]
        # [later 061106: handled by Arg macro.]
##        printnim("type coercion of args & optvals")
        printnim("provision for multiple arglists,")
        printnim("* or ** argdecls,")
        printnim("checking for optnames being legal, or not internal attrnames")
        # Note: this scheme needs some modification once we have exprs that can accept multiple arglists...
        # one way would be for the above assert [which one? I guess the not self._e_has_args]
        # to change to an if, which stashed the old args somewhere else,
        # and made sure to ask instantiation if that was ok; but better is to have a typedecl, checked now, which knows if it is. ###@@@
        return # from _destructive_supply_args

    # instantiation methods
    def _e_make_in(self, env, ipath):
        """Instantiate self in env, at the given index-path.
        [Note: as of some time before 061110, this is usually called via _e_eval;
         and as of 061110 it's probably always called that way;
         probably they'll be merged at some point, unless some subtle difference
         is discovered (e.g. related to finding memoized instances).]
        """
        assert env #061110
        # no need to copy the formulas or args, since they're shared among all instances, so don't call self._copy. [###k still true?]
        # instead, make a new instance in a similar way.
        printnim("_e_make_in needs to replace _self with env._self in our externally-sourced formulas") #####@@@@@ 061110
            # or could it do this when running them, eg by having a different env to run them in? not sure, they might get further
            # modified when we get customized... but my guess is this would work... come to think of it, the env they need is the
            # one passed here, and what goes wrong is that we run them in a modified env with new self stored as _self,
            # btu that's only appropriate for the built-in formulas, not the passed ones, for which the passed env is the best.
            # but we have some formulas that combine builtin & passed parts...
            # should we just wrap these outside formulas by something to drop one layer from env,
            # knowing we always modify it by adding _self? Better would just be something to replace env.
            # Note I could store them shared, and wrap them as I retrieve them, I think -- in _i_grabarg.
            # BTW is it desirable for everything in env, or just _self? what about ipath? #####@@@@@
        assert not self._e_is_instance
        return self.__class__(_make_in = (self,env,ipath)) # this calls _destructive_make_in on the new instance
    def _destructive_make_in(self, data):
        """[private]
        This is the main internal instantiation-helper method.
        For expr, env, ipath = data, modify self (which initially knows nothing)
        to be an instance of expr, in the given env, at the given index-path.
        Called only from __init__, when self knows nothing except its class.
        """
        ## printnim("make_in needs to replace _self in customization formulas with _self from env")#061110 313p
            # 061113 Q: what's the status of this? does _e_eval or _e_compute_method do it somehow, making this obs?? 
            # or is it truly nim -- but if so, how does _self work in args inside _value in Boxed? oh, that's not customized,
            # rel to Boxed -- but it is, rel to the exprs in _value, which is what counts. hmm...
            # now I'm recalling something about lexenv_Expr fixing this (& it's dated later same day, 061110)...
            # yes, that fixes it inside grabarg; I am guessing it can be optimized to once per instance once we have
            # simplify to do that to most of grabarg; that scheme means instances of custom exprs can share formulas.
            # A: so I'll comment out this printnim.
            # Q: where & how should we replace _this(class) with the lexically innermost object of that class? ####@@@@
            # Can it be computed at runtime, so we can turn it into a macro? Does the debug code to print selfs of outer envs
            # do the right thing, or would that be too dynamic? Do we *want* it to be dynamic, so we can use it when writing
            # display mode customizations to refer to things in which our instances will be contained? If so, do instances
            # know their parents?
            # For initial uses, we might not care about these "details"! Possible initial kluge implem: let _this(class)
            # turn into an instance itself, which figures out at runtime what to delegate to. Doing this below, "class _this".
            # WRONG, next day 061114 I'm doing it differently: _this(class) turns into an internal_Expr. Still found as "class _this".
            
        printnim("should make_in worry about finding an existing instance at the same index?")
            # guess: no, it'd be obsolete; not sure. #061110 313p
        
        expr, env, ipath = data ###@@@ might want to split env into rules (incl lexenv) & place (incl staterefs, glpane)
        assert env #061110
        assert not self._e_is_instance #e remove when works
        assert not expr._e_is_instance
        self._e_is_instance = True

        self.env = env #k ok, or does it need modification of some kind?
            #e in fact we mod it every time with _self, in _e_compute_method -- can we cache that?
        ####@@@@
        self.ipath = ipath ###e does this need mixing into self.env somehow?
        ## print "assigned %r.ipath = %r" % (self,ipath) #061114 -- note, repr looks funny since fields it prints are not yet inited
        #e also set self.index??
        
        # set up self._e_args etc
        self._e_class = expr # for access to _e_kws and args #k needed? #e rename: self._e_expr? not sure. #k not yet used
        ## assert expr._e_has_args, "this expr needs its arguments supplied: %r" % self
            # we might allow exceptions to this later, based on type decl, especially if it has no declared args
            # (how can we tell, here?? ###e),
            # tho there is then an ambiguity about whether you're only customizing it or not,
            # but OTOH that is tolerable if it takes no args, actually that's unclear if instantiation does something like
            # make a random choice! So we might want to detect that, warn at compile time, or so....
        if not expr._e_has_args:
            print "warning: this expr might need its arguments supplied: %r" % self
                    ### addendum 061212: probably not a bug when all args are optional, so for now, permit with warning and
                    # examine the specific cases, such as testexpr_9fx6. At first I thought that using this always gets later
                    # bugs, but it turned out those were unrelated If_expr bugs, so now this can work. See comments near that test.
        self._e_has_args = expr._e_has_args #k ??
        # copy references to _e_args & _e_kws
        # note: exprs passed to specific args or kws can be lazily type-coerced and instantiated by Arg or Option decls in subclasses
        self._e_args = expr._e_args
        self._e_kws = expr._e_kws # replaces _e_formula_dict as of 061106

        ## print "fyi my metaclass is",self.__metaclass__ # <class 'exprs.ExprsMeta.ExprsMeta'>

        #semi-obs cmts:
        ### AND set up self.opts to access old._e_formula_dict, also perhaps adding effect of type coercers
        ## print "compare self #formulas %d vs expr #formulas %d" % (len(self._e_formula_dict), len( expr._e_formula_dict)) # 0,3
##        self._e_formula_dict = expr._e_formula_dict # kluge, no protection from bug that modifies it, but nothing is supposed to
        ## print "self._e_formula_dict =",self._e_formula_dict
        ### AND have some way to get defaults from env
        ### AND take care of rules in env -- now is the time to decide this is not the right implem class -- or did caller do that?
        ### and did caller perhaps also handle adding of type coercers, using our decl??

        # 061020 hopes [rejargoned but not updated, 061106]:
        # maybe we can work for all, incl OpExprs & iterators, by only setting up RULES to instantiate,
        # which if not used, never happen. self.kids.<index/attr path> has to come from some self._e_args or self._e_kws member...
        # index always comes from <index/attr path> and *not* from which arg or opt, i think... sometimes they correspond,
        # and some predeclared members of kids could access those for you, e.g. self.kids.args or just self.args for short...
        # we could even say _e_args for the raw ones, .args for the cooked ones.

        # set up state refs
        printnim("instance_helpers needs setup state refs, init_class call, init_expr call")#####@@@@@

        #e call _init_class and/or _init_expr if needed [here or more likely earlier]

        self._i_instance_decl_data = {} # private storage for self._i_instance method [renamed from _i_instance_exprs, 061204]
        
        # call subclass-specific instantiation code (it should make kids, perhaps lazily, if above didn't; anything else?? ###@@@)
        self._init_instance()
        return # from _destructive_make_in
    
    def _init_class(self): #e move to InstanceClass superclass? ###@@@ CALL ME
        """called once per directly-instantiated python class, when its first python instance is created
        [subclasses should replace this]
        """
        pass
    def _init_expr(self): #e move to InstanceClass superclass? ###@@@ CALL ME
        """called once per Expr when it gets its args [details unclear, maybe not yet needed]
        [subclasses should replace this]
        """
        pass
    def _init_instance(self): #e move to InstanceClass superclass? let it be name-mangled, and call in mro order?
        """called once per python instance, but only when it represents a semantic Instance ###doc -- explain better
        [some subclasses should extend this, starting their versions with super(TheirName, self)._init_instance()]
        """
        pass

    def _e_eval(self, env, ipath): # implem/behavior totally revised, late-061109; works - not sure it always will tho... ###k
        # handling of If: As of 061212 If_expr (a subclass of this) overrides _e_eval and seems to work; see comments there.
        # handling of _value: done at a higher level only -- see InstanceMacro.
        return self._e_make_in(env, ipath)

    # kid-instantiation, to support use of the macros Arg, Option, Instance, etc
    #k (not sure this is not needed in some other classes too, but all known needs are here)
    
    def _i_instance( self, expr, index, _lvalue_flag = False ):
        """[semi-private; used by macros like Instance, Arg, Option]
        Find or create (or perhaps recompute if invalid, but only the latest version is memoized) (and return)
        an Instance of expr, contained in self, at the given relative index, and in the same env [#e generalize env later?].
           Error (perhaps not detected) if called with same index and different other args;
        when a cached instance is returned, the other args are not used except perhaps to check for this error.
        (When an instance is recomputed, if this error happens, are new args used? undefined.)
        (#e Should we change this to make the expr effectively part of the index, for caching? Probably not; not sure.)
        (#e Should we change this to make it legal to pass a new expr? Probably not... hard for subsequent callers to be consistent...)
        """
        def __debug_frame_repr__(locals):
            "return a string for inclusion in some calls of print_compact_stack"
            return "_i_instance(index = %r, expr = %r), self = %r" % (index,expr,self)
        assert self._e_is_instance
        assert is_pure_expr(expr), "who passed non-pure-expr %r to _i_instance? index %r, self %r, _e_args %r" % \
               (expr, index, self, self._e_args)
            #k guess 061105
        if 0 and self.__class__.__name__.endswith('If_expr'):#debug
            print "_i_instance called, expr %r, index %r, self %r, _e_args %r" % \
                   (expr, index, self, self._e_args)

        # [#k review whether this comment is still needed/correct; 061204 semiobs due to newdata change below; even more obs other ways]
        # hmm, calling Instance macro evals the expr first... can't it turn out that it changes over time?
        # I think yes... not only that, a lot of change in it should be buried inside the instance! (if it's in an arg formula)
        # as if we need to "instantiate the expr" before actually passing it... hmm, if so this is a SERIOUS LOGIC BUG. ####@@@@
        # WAIT -- can it be that the expr never changes? only its value does? and that we should pass the unevaluated expr? YES.
        # But i forgot, eval of an expr is that expr! I get confused since _e_eval evals an implicit instance -- rename it soon! ###@@@
        # [addendum 061212: see also the comments in the new overriding method If_expr._e_eval.]
        newdata = (expr, _lvalue_flag) # revised 061204, was just expr, also renamed; cmt above is semiobs due to this
        olddata = self._i_instance_decl_data.get(index, None) # see above comment
        if olddata != newdata:
            if olddata is not None:
                print "bug: expr or lvalflag for instance changed: self = %r, index = %r, new data = %r, old data = %r" % \
                      (self,index,newdata,olddata) #e more info? i think this is an error and should not happen normally
                #e if it does happen, should we inval that instance? yes, if this ever happens without error.
                # [addendum 061212: see also the comments in the new overriding method If_expr._e_eval.]

            self._i_instance_decl_data[index] = newdata
        return self._i_instance_CVdict[index] # takes care of invals in making process? or are they impossible? ##k [see above]
    def _CV__i_instance_CVdict(self, index):
        """[private] value-recomputing function for self._i_instance_CVdict.
        Before calling this, the caller must store an expr for this instance
        into self._i_instance_decl_data[index] (an ordinary dict).
           If it's permitted for that expr to change with time (which I doubt, but don't know yet for sure #k),
        then whenever the caller changes it (other than when initially setting it), the caller must invalidate
        the entry with the same key (our index arg) in the LvalDict2 that implements self._i_instance_CVdict
        (but the API for the caller to do that is not yet worked out #e).
           (Implem note: _CV_ stands for "compute value" to ExprsMeta, which implements the LvalDict2 associated with this.
        This method needs no corresponding _CK_ keylist function, since any key (instance index) asked for is assumed valid.)
        """
        assert self._e_is_instance
        # This method needs to create a new instance, by instantiating expr and giving it index.
        # Implem notes:
        # - the glue code added by _CV_ from self._i_instance_CVdict to this method (by ExprsMeta) uses LvalDict2
        #   to cache values computed by this method, and recompute them if needed (which may never happen, I'm not sure).
        # - the access to self._i_instance_decl_data[index] is not usage tracked;
        #   thus if we change it above w/o error, an inval is needed.
        data = self._i_instance_decl_data[index]
        expr, lvalflag = data # 061204
        ## print "fyi, using kid expr %r" % expr
        # (these tend to be longish, and start with eval_Expr -- what we'd rather print is the result of the first eval it does)
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
##        env = self.env #e with lexmods?
##        index_path = (index, self.ipath)
        ####e:  [061105] is _e_eval actually needing to be different from _e_make_in?? yes, _e_eval needs to be told _self
        # and the other needs to make one... no wait, wrong, different selves --
        # the _self told to eval is the one _make_in *should make something inside of*! (ie should make a kid of)
        # So it may be that these are actually the same thing. (See paper notes from today for more about this.)
        # For now, tho, we'll define _e_make_in on OpExpr to use eval. [not done, where i am]
        # actually this is even faster -- review sometime (note, in constant_Expr they're both there & equiv #k): ###@@@
        ## this is just the kid expr: print "_CV__i_instance_CVdict needs to make expr %r" % (expr,)
        if hasattr(expr, '_e_make_in'):
            print("REJECTED using _e_make_in case, on a pyinstance of class %s" % expr.__class__.__name__)###was printfyi til 061208 921p
            ## res = expr._e_make_in(env, index_path)
                #k we might have to fix bugs caused by not using this case, by defining (or modifying?) defs of _e_eval on some classes;
                # addendum 061212, we now do that on If_expr.
        if 1:
            # WARNING: following code is very similar to _i_eval_dfltval_expr as of 061203
            # printfyi("used _e_eval case (via _e_compute_method)") # this case is usually used, as of 061108 -- now always, 061110
            # note: this (used-to-be-redundantly) grabs env from self
            try:
                res = expr._e_compute_method(self, index, _lvalue_flag = lvalflag)() ##e optim someday: inline this
                    # 061105 bug3, if bug2 was in held_dflt_expr and bug1 was 'dflt 10'
            except:
                # we expect caller to exit now, so we might as well print this first: [061114]
                print "following exception concerns self = %r, index = %r in _CV__i_instance_CVdict calling _e_compute_method" % \
                      (self, index)
                raise
        return res # from _CV__i_instance_CVdict

    def _i_eval_dfltval_expr(self, expr, index): ##e maybe unify with above, but unclear when we soon split eval from instantiate
        "evaluate a dfltval expr as used in State macro of 061203; using similar code as _CV__i_instance_CVdict for Instance..."
        # WARNING: similar code to end of _CV__i_instance_CVdict
        # note: this (used-to-be-redundantly) grabs env from self
        try:
            computer = expr._e_compute_method(self, index) ##e optim someday: inline this
                # 061105 bug3, if bug2 was in held_dflt_expr and bug1 was 'dflt 10'
            if 1:
                res = call_but_discard_tracked_usage( computer) # see also docstring of eval_and_discard_tracked_usage
            else:
                res = computer()
        except:
            # we expect caller to exit now, so we might as well print this first: [061114]
            print "following exception concerns self = %r, index = %r in *** _i_eval_dfltval_expr *** calling _e_compute_method" % \
                  (self, index)
            raise
        return res
        
    def _i_grabarg( self, attr, argpos, dflt_expr): 
        "#doc, especially the special values for some of these args"
        if 0:
            print_compact_stack( "_i_grabarg called with ( self %r, attr %r, argpos %r, dflt_expr %r): " % \
                                 (self, attr, argpos, dflt_expr) )
            print " and the data it grabs from is _e_kws = %r, _e_args = %r" % (self._e_kws, self._e_args)
        #k below should not _e_eval or canon_expr without review -- should return an arg expr or dflt expr, not its value
        # (tho for now it also can return None on error -- probably causing bugs in callers)
        assert is_pure_expr(dflt_expr), "_i_grabarg dflt_expr should be an expr, not %r" % (dflt_expr,) #061105 - or use canon_expr?
        assert self._e_is_instance
        if not self._e_has_args:
            print "warning: possible bug: not self._e_has_args in _i_grabarg" ###k #e more info
        assert attr is None or isinstance(attr, str)
        assert argpos is None or (isinstance(argpos, int) and argpos >= 0)
        external_flag, res0 = self._i_grabarg_0(attr, argpos, dflt_expr)
        if external_flag:
            # flag and this condition added 061116 443p to try to fix '_self dflt_expr bug'; seems to work in testexpr_9a;
            # I'm guessing type_expr doesn't have a similar bug since it's applied outside this call. #k
            res = lexenv_Expr(self.env_for_args, res0) ##k lexenv_Expr is guess, 061110 late, seems confirmed; env_for_args 061114
            #e possible good optim: use self.env instead, unless res0 contains a use of _this;
            # or we could get a similar effect (slower when this runs, but better when the arg instance is used) by simplifying res,
            # so that only the used parts of the env provided by lexenv_Expr remained (better due to other effects of simplify)
        else:
            res = res0
            #k (I *think* it's right to not even add self.env here, tho I recall I had lexenv_Expr(self.env, res0) at first --
            #   because the self.env was for changing _self, which we want to avoid here, and the _for_args is for supporting _this.)
        # Note: there was a '_self dflt_expr bug' in the above, until i added 'if external_flag:'] [diagnosed & fixed 061116]:
        # it's wrong for the parts of this expr res0 that came from our class, i.e. dflt_expr and type_expr.
        # That is hard to fix here, since they're mixed into other parts of the same expr,
        # but nontrivial to fix where we supply them, since when we do, the specific env needed is not known --
        # we'd have to save it up or push it here, then access it there (or just say "escape from the most local lexenv_Expr"
        # if that's well-defined & possible & safe -- maybe the most local one of a certain type is better).
        # We also want whatever we do to be robust, and to not make it too hard to someday simplify the expr.
        #   So why not fix it by wrapping only the parts that actually come from _e_args and _e_kws, right when we access them?
        # I guess that is done inside _i_grabarg_0... ok, it's easy to add external_flag to its retval to tell us what to do. [done]
        ###k ARE THERE any other accesses of _e_args or _e_kws that need similar protection? Worry about this if I add
        # support for iterating specific args (tho that might just end up calling _i_grabarg and being fine).
        if 0:
            print "_i_grabarg returns %r" % (res,)
        return res

    def _C_env_for_args(self):###NAMECONFLICT? i.e. an attr whose name doesn't start with _ (let alone __ _i_ or _e_) in some exprs
        "#doc"
        lexmods = {} # lexmods for the args, relative to our env
        thisname = thisname_of_class(self.__class__) ##e someday make it safe for duplicate-named classes
            # (Direct use of Symbol('_this_Xxx') will work now, but is pretty useless since those symbols need to be created/imported.
            #  The preferred way to do the same is _this(class), which for now [061114] evals to the same thing that symbol would,
            #  namely, to what we store here in lexmods for thisname. See "class _this".)
        
        lexmods[thisname] = self
            # WARNING: this creates a cyclic ref, from each child whose env contains lexmods, to self, to each child self still knows.

        lexmods['_my'] = self #061205
        
        return self.env.with_lexmods(lexmods)

    def _i_grabarg_0( self, attr, argpos, dflt_expr):
        "[private helper for _i_grabarg] return the pair (external-flag, expr to use for this arg)"
        # i think dflt_expr can be _E_REQUIRED_ARG_, or any (other) expr
        from __Symbols__ import _E_REQUIRED_ARG_
        if dflt_expr is _E_REQUIRED_ARG_:
            required = True
        else:
            required = False
            assert not isinstance(dflt_expr, _E_REQUIRED_ARG_.__class__)
                # kluge sanity check -- not a Symbol #e remove when works, probably not even justified in general (eg _self??)
                #e or replace with "not a Symbol whose name starts _E_" ??
        if attr is not None and argpos is not None:
            printnim("should assert that no expr gets same arg twice (positionally and as named option)")###e
        if attr is not None:
            # try to find it in _e_kws; I suppose the cond is an optim or for clarity, since None won't be a key of _e_kws
            try:
                return 1, self._e_kws[attr]
            except KeyError:
                pass
        if argpos is not None:
            try:
                return 1, self._e_args[argpos]
            except IndexError: # "tuple index out of range"
                pass
        # arg was not provided -- error or use dflt_expr
        if required:
            print "error: required arg %r or %r not provided to %r. [#e Instance-maker should have complained!] Using None." % \
                  (attr, argpos, self)
            # Note: older code returned literally None, not an expr, which caused a bug in caller which tried to _e_eval the result.
            # Once we've printed the above, we might as well be easier to debug and not cause that bug right now,
            # so we'll return a legal expr -- in some few cases this will not cause an error, making this effectively a warning,
            # "missing args are interpreted as None". Review this later. [061118]
            printnim("a better error retval might be a visible error indicator, if the type happens to be a widget")###e
                #e I think we don't know the type here -- but we can return a general error-meaning-thing (incl error msg text)
                # and let the type-coercers do with it what they will. Or we could return something equivalent to an exception
                # (in our interpreted language) and revise our eval semantics to handle that kind of thing. [061118]
            return 0, canon_expr(None)
        else:
            return 0, dflt_expr
        pass # above should not _e_eval or canon_expr without review -- should return an arg or dflt expr, not its value
    
    pass # end of class InstanceOrExpr

# ===

_DELEGATION_DEBUG_ATTR = '' # you can set this to an attrname of interest, at runtime, for debugging

class DelegatingMixin(object): # 061109 # see also DelegatingInstanceOrExpr
    """#doc: like Delegator (with no caching, in case the delegate varies over time),
    but self.delegate should be defined by the subclass
    (e.g. it might be recomputable from a formula or _C_delegate method handled by ExprsMeta, or assigned in __init__).
    Also, doesn't start delegating until self is an Instance. [##e For now, prints fyi when asked to, tho that's not an error.]
    Also, DOESN'T DELEGATE attrs that start with '_'.
       Note that the Instance-related semantics mean it's only useful for Exprs.
    [##e Maybe we could generalize it to use a more general way of asking the pyinstance whether to delegate yet,
     like some other optional flag attr or method.
     (But probably not just by testing self.delegate is None, since the point is to avoid running a compute method
      for self.delegate too early.)]
    """
    ##e optim: do this instead of the assert about attr: delegate = None # safer default -- prevent infrecur
    def __getattr__(self, attr):
        try:
            return super(DelegatingMixin,self).__getattr__(attr)###k need to verify super args in python docs, and lack of self in __getattr__
                # note, _C__attr for _attr starting with _ is permitted, so we can't check whether attr starts '_' before doing this.
        except LvalError_ValueIsUnset:
            # 061205 new feature to prevent bugs: don't delegate in this case. UNTESTED! #####TEST
            print "fyi (maybe not always bug): " \
                  "don't delegate attr %r from %r when it raises LvalError_ValueIsUnset! reraising instead." % (attr, self)
            raise
        except AttributeError:
            if attr.startswith('_'):
# useful debug code -- commented out, but keep around for now [061110]:
##                if not attr.startswith('__'):
##                    # additional test hasattr(self.delegate, attr) doesn't work: AssertionError: compute method asked for on non-Instance
##                    # we need that test but I don't know how to add it easily. __dict__ won't work, the attr might be defined on any class.
##                    # maybe look in __dict__ of both self and its class?? #e
##                    print "warning: not delegating missing attr %r in %r (don't know if defined in delegate)" % \
##                          (attr, self)#061110 - have to leave out ', tho it's defined in delegate %r'
##                        # before hasattr check, this happens for _args, _e_override_replace, _CK__i_instance_CVdict
##                        # (in notyetworking Boxed test, 061110 142p).
##                        #e could revise to only report if present in delegate... hard to do, see above.
                raise AttributeError, attr # not just an optim -- we don't want to delegate any attrs that start with '_'.
                ##k reviewing this 061109, I'm not sure this is viable; maybe we'll need to exclude only __ or _i_ or _e_,
                # or maybe even some of those need delegation sometimes -- we'll see.
                #e Maybe the subclass will need to declare what attrs we exclude, or what _attrs we include!
            assert attr != 'delegate', "DelegatingMixin refuses to delegate self.delegate (which would infrecur) in %r" % self 
            if expr_is_Instance(self):
                recursing = self.__dict__.setdefault('__delegating_now', False) # note: would be name-mangled if set normally
                assert not recursing, "recursion in self.delegate computation in %r" % self #061121
                self.__dict__['__delegating_now'] = True
                try:
                    delegate = self.delegate
                finally:
                    self.__dict__['__delegating_now'] = False #e or could del it, presumed less efficient, not sure
                ##e could check that delegate is not None, is an Instance (??), etc (could print it if not)
                #k Should it be silently tolerated if delegate is None? Probably no need -- None won't usually have the attr,
                # so it will raise the same exception we would. Are there confusing cases where None *does* have the attr??
                # I doubt it (since we're excluding _attrs). But it's worth giving more info about likely errors, so I'm printing some.
                if delegate is None or is_pure_expr(delegate): ##k is None in fact unlikely to be valid?
                    print_compact_stack( "likely-invalid delegate %r for %r in self = %r: " % (delegate, attr, self)) #061114
                try:
                    if attr == _DELEGATION_DEBUG_ATTR: 
                        print "fyi: delegating %r from %r to %r" % (attr, self, delegate)
                    return getattr(delegate, attr) # here is where we delegate. It's normal for this to raise AttributeError (I think).
                except AttributeError:
                    #### catching this is too expensive for routine use (since I think it's often legitimate and maybe common -- not sure),
                    # but it's useful for debugging -- so leave it in for now. 061114
                    printnim("too expensive for routine use")
                    msg = "no attr %r in delegate %r of self = %r" % (attr, delegate, self)
                    if attr == _DELEGATION_DEBUG_ATTR: 
                        print msg
                    raise AttributeError, msg
            print "DelegatingMixin: too early to delegate %r from %r, which is still a pure Expr" % (attr, self)
                # might be an error to try computing self.delegate this early, so don't print it even if you can compute it
                # (don't even try, in case it runs a compute method too early)
            raise AttributeError, attr
        pass
    pass # end of class DelegatingMixin

# ==

# Implem notes for _value [061110, written when this was in Boxed.py]:
# - Q: make it have an implicit Instance, I think -- or use a convention of adding one explicitly?
#   A: the convention, so it can work with other formulas too? no, they'd also need instantiation to work... not sure actually.###@@@
#   - BTW that might mean we get in trouble trying to pure-eval (which is what?) an Expr made from InstanceOrExpr, e.g. for a formula
#   to figure an iterator-expr to use in something else! We'll have to try that, and understand the semantics more clearly...
#   could it be that we'll have to explicitly Hold the exprs assigned to class attrs in cases like that?!?
# - where we use that _value is probably in _e_eval in InstanceOrExpr. (I still don't know if that and make_in are exactly the same.)
# - so we could do the instantiation in the place where we use it... then (later) test what happens if it's a number or so. (##e)
#   - (or what if the entire macro with its value is supposed to come up with a pure expr? test that too. ##e)
# So for now, just run the instantiation in the place we use it, in InstanceOrExpr._e_eval.
# But worry about whether InstanceOrExpr._e_make_in sometimes gets called instead by the calling code.
# Maybe better do it in whichever one has precedence when they both exist... that's _e_make_in (used in _CV__i_instance_CVdict).
# _e_eval just calls it, so that way it'll work in both. Ok, do it. ###
# WAIT, is it possible for the _value formula to vary with time, so that we want an outer instance,
# delegating to a variable inner one? (Perhaps memoizing them all sort of like GlueCodeMemoizer would do... perhaps only last one.)
# hmm... #### note that _make_in should pick up the same instance anyway, if it exists, but it looks to me like it might not!!! ###BUG
#
# let's try an explicit experiment, InstanceMacro:

class InstanceMacro(InstanceOrExpr, DelegatingMixin): # circa 061110; docstring revised 061127; see also DelegatingInstanceOrExpr
    """Superclass for "macros" -- they should define a formula for _value which they should always look like.
    # WARNING: a defect in InstanceMacro means no local defs in its client class (e.g. thing, ww in Boxed),
    # or in a superclass of that, will be delegated to _value (since they won't reach DelegatingMixin.__getattr__);
    # so be careful what you name those local defs, and what default values are defined in a superclass!
    #    This is also perhaps a feature
    # (permitting you to override some of the otherwise-delegated attrs, e.g. bright or width),
    # tho at one time I thought delegate should let you do that, _value should not,
    # and this would be a useful distinction. I don't yet know how to make _value not do it,
    # nor whether that's desirable if possible, nor whether it's well-defined. ###@@@ [061114]
    #    It means, for example, that the InstanceMacro Boxed would not work if it inherited from Widget2D,
    # since it would pick up Widget2D default values for lbox attrs like btop. [unconfirmed but likely; 061127 comment]
    """
    #e might not work together with use by the macro of DelegatingMixin in its own way, if that's even possible [later: not sure what this comment means]
    delegate = Instance( _self._value, '!_value') #k guess: this might eval it once too many times... ####k
        # [later, as of 061113 -- it works, but this point of too many evals has never been fully understood,
        #  so for all i now, it happens but causes no obvious harm in these examples -- should check sometime. ##e]
        
        # [much later, 061114: i think I know why it works -- Instance indeed does an eval, but it's the eval from _self._value
        #  to what's stored in self._value, which is *already* an Instance because evaling the rule makes one!
        #  see other comments about this in Boxed _init_instance dated today. as they say, it's all wrong and will probably change.
        #  in fact, if I said here delegate = _self._value, I think it ought to work fine! Try it sometime. ######TRYIT]
        
        #k Note: I used '!_value' as index, because I worried that using '_value' itself could collide with an index used to eval the expr version of _value,
        # in future examples which do that (though varying expr is not presently supported by Instance, I think -- OTOH
        # there can be two evals inside _i_instance due to eval_Expr, so the problem might arise that way, dep on what it does with
        # indices itself).
        
    ##e could add sanity check that self.delegate and self._value are instances
    # (probably the same one, tho not intended by orig code, and won't remain true when Instance is fixed) [061114]
    pass

# ==

class DelegatingInstanceOrExpr(InstanceOrExpr, DelegatingMixin): # moved here & basic 061211, created a few days before
    """#doc
    """
    #e this might replace most uses of DelegatingMixin and InstanceMacro, if I like it
    pass

# ==

class _this(SymbolicExpr): # it needs to be symbolic to support automatic getattr_Expr
    """_this(class) refers to the instance of the innermost lexically enclosing expr with the same name(?) as class.
    """
    #k will replacement in _e_args be ok? at first it won't matter, I think.
    def __init__(self, clas):
        assert is_Expr_pyclass(clas) #k
        self._e_class = clas
        self._e_thisname = thisname_of_class( self._e_class)
        return
    #e __str__ ?
    def __repr__(self):
        return "<%s#%d%s: %r>" % (self.__class__.__name__, self._e_serno, self._e_repr_info(), self._e_class,)
    def _e_eval(self, env, ipath):
        dflt = None ## 'stub default for ' + self._e_thisname #####e fix
        res = env.lexval_of_symbolname( self._e_thisname, dflt )
            # I don't think we need to do more eval and thus pass ipath;
            # indeed, the value is an Instance but not necessarily an expr
            # (at least not except by coincidence of how _this is defined).
            # Caller/client could arrange another eval if it needed to. [061114 guess]
        assert res, "_this failed to find referent for %r" % self._e_thisname ##e improve
        return res
    pass # end of class _this   

# === only obs code after this point

##class _this(SymbolicInstanceOrExpr_obs, DelegatingMixin): #061113; might work for now, prob not ok in the long run
#e [see an outtakes file, or cvs rev 1.57, for more of this obs code for _this, which might be useful someday]

# ==

class DelegatingInstanceOrExpr_obs(InstanceOrExpr): #061020; as of 061109 this looks obs since the _C_ prefix is deprecated;
    #e use, instead, DelegatingMixin or DelegatingInstanceOrExpr combined with formula on self.delegate
    """#doc: like Delegator, but self.delegate is recomputable from _C_delegate as defined by subclass.
    This is obsolete; use DelegatingMixin instead. [#e need to rewrite GlueCodeMemoizer to not use this; only other uses are stubs.]
    """
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

DelegatingInstance_obs = DelegatingInstanceOrExpr_obs #k ok? (for when you don't need the expr behavior, but (i hope) don't mind it either)

#e rewrite this to use DelegatingMixin [later 061212: nevermind, it's probably obs, tho not sure]
class GlueCodeMemoizer( DelegatingInstanceOrExpr_obs): ##e rename WrapperMemoizer? WrappedObjectMemoizer? WrappedInstanceMemoizer? probably yes [061020]
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
        printnim("self.args[0] needs review for _e_args or setup, in GlueCodeMemoizer; see DelegatingMixin")###e 061106
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
        return LvalDict1( self._recomputer_for_wrapped_version_of_one_instance)
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

# end
