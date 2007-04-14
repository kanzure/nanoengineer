"""
instance_helpers.py

$Id$

070129 moved still-nim GlueCodeMemoizer into new file Column_old_nim.py
"""

from basic import * # autoreload of basic is done before we're imported; this is a recursive import
from basic import _self

import lvals
reload_once(lvals)
from lvals import call_but_discard_tracked_usage, LvalError_ValueIsUnset
from lvals import LvalDict1 # only needed by obs code

import widget_env
reload_once(widget_env)
from widget_env import thisname_of_class #e refile import?? or make it an env method??

kluge070119 = True # this is permanent for now, but don't clean up the associated code yet, since it'll soon be replaced
    # by a better centralized instantiator. [070120]
    #
    # history:
    # True used to cause infrecur in delegate in testexpr_10a, not yet diagnosed; caused wrong _self for .ww in _5x,
    # which as of 070120 944p is understood and fixed. The _10a bug is also fixed (by the same fix in the code --
    # a more-correct _self assignment), but I don't know why there was infrecur before (and I guess I never will).

    #### Where i am 070120 1023p as I stop -- ...
    # I should still test more egs, and test non-EVAL_REFORM cases of all these egs to make sure that's ok too
    # (its code was also changed by these fixes).
    #### Then I should remove dprints and tons of comments and unused code cases from the
    # files modified today. Then fix the need for manual Instance in delegates. ####

debug070120 = False # some debug prints, useful if bugs come up again in stuff related to the above

# ==

# maybe merge this into InstanceOrExpr docstring:
"""Instances of subclasses of this can be unplaced or placed (aka "instantiated");
if placed, they might be formulas (dependent on aspects of drawing-env state)
for appearance and behavior (justifying the name Drawable),
or for some value used in that (e.g. a color, vector, string).
   Specific subclasses, e.g. Rect, contain code which will be used in placed instances (mainly drawing code)
unless the env provided an overriding expansion for exprs headed by that subclass.
If it did, the instance created by placing such an expr will (usually) have some other class.
"""

class InstanceOrExpr(Expr): # see docstring for discussion of the basic kluge of using one class for both
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
    model_state = StatePlace('model') # state that's part of the model (i.e. stored/copied with model objects) ### NOT YET USED [070213]
    untracked_model_state = StatePlace('untracked_model', tracked = False)
        # model state, not change/usage-tracked (e.g. counters for allocating unique index-components or name-components) [070213]
    # abbrevs for read-only state [#e should we make them a property or so, so we can set them too?]
    glname = glpane_state.glname # (note, most things don't have this)

    # instance variable defaults (names must start with _e_ or _i_, or they'll cause trouble for non-Instance getattr_Expr formation)
    _i_model_type = None # experimental, perhaps a kluge, 070206; WARNING: set externally on some specific Instances in world.py
    ## _e_model_type = None # 070215 (not sure if it supercedes the above) -- type of model obj an expr intends to construct (if known)
        # note: the value of _e_model_type can just be a string, or a fancier object (###NIM and probably not yet handled)
        # do we compute a type on exprs which can be _e_model_type or classname but only for ModelObjects? (else delegate to one?)
        # (or for pure graphicals can it be classname too? yes, they can be shapes in the model -- maybe their class needs to say so?)
        # do instances ever have a different model_type than their expr predicted?
        # (seems possible -- main use of expr one is for sbar_texts & cmenu item texts, ie UI predictions of what an expr can make)
        # sceptic: do exprs need this, or do we need special expr-like Instances to reside in eg PalletteWell, which have a special
        # interface "maker" and know the type of what they can make? But aren't exprs similar to makers anyway?
        # (even if so, must they be wrapped to be one? evidence for that might be if there are any params about how to make with them.
        #  but i think not, since they're useable to make things "out of the box"... what if each thing wants params, do you want
        #  to customize that beyond what the expr knows about args/state, and think of that as maker params??)
        # Is the real issue for determining the attrname/methodname not "model" or "expr" but "what you make vs what you are"?? ###k

    def _e_model_type_you_make(self): ###k 070215 very experimental #e move below init
        "#doc; overridden on some subclasses, notably DelegatingInstanceOrExpr"
        # but lots of specific DIorE don't delegate it...
        # model obj DIorE don't, but graphical ones do. For now assume we know by whether it's subclass of ModelObj.
        # This implem is meant for graphical prims like Rect.
        # ok for expr but wrong for instance! actually, not true - inst makes itself! so wrong for an explicit Maker I guess...
        return self.__class__.__name__.split('.')[-1] ##e see where else we have that code, maybe world.py; have classattr to override?
    
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
            self._e_init_e_serno() #070121 moved this before _destructive_make_in, so it sees serno in prints,
                # and since AFAIK the desire to have later serno than our kids only applies to pure exprs, not Instances ##k
            self._destructive_make_in(val)
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

# I'm not sure whether this unfinished _i_type and _e_delegate_type code will be used -- for now, leave it but comment it out [070206]
##    _e_delegate_type = False # subclass-specific constant -- whether Instance type determination should be delegated to self._delegate
##    
##    def _i_type(self): #070206
##        """Return something that represents the type of Instance or Expr we are.
##        (This is not the same as Python type. For more info on what we return, see ###doc.)
##           WARNING: preliminary implem, several implicit kluges.
##           NOTE: _e_delegate_type should be True in any delegating subclass, *if* the delegate's type
##        should be treated as self's type. This has to be determined by each specific subclass --
##        it's true for wrapper-like delegators (e.g. Translate)
##        but not true for Macro-like ones, and there is not yet a formal distinction between those
##        (though this makes it clear that there should be ###e).
##        """
##        if self._e_is_instance:
##            if self._e_delegate_type:
##                return self._delegate._i_type()
##            name = self.__class__.__name__
##        else:
##            name = "Expr" ###e include something about the predicted instance type? what if it's condition- or time-varying?
##                # maybe only include it if an outer level includes a type-coercer??
##        return name
    
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
            # in fact, reviewing the uses 070120, there are none left, and the last ones in widget2d went away long ago. ###e ZAP IT
        return formula._e_compute_method(self, '@' + attr) #k index arg is a guess, 061110
    
    # copy methods (used by __call__)
    def _copy(self, _instance_warning = True):
        ## assert not self._e_is_instance ## ??? [061019]
        if self._e_is_instance and _instance_warning:
            print "WARNING: copying an instance %r" % (self,) # this might be ok...
        return self.__class__(_copy_of = self) # this calls _destructive_copy on the new instance
    def copy(self):#061213 experiment, used in demo_drag.py, background.copy(color=green) ###k
        "copy an expr or instance to make a new expr with the same formulas [experimental]"
        return self._copy(_instance_warning = False)
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
        printnim("type coercion of args & optvals")
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
        """Instantiate self in env, at the given index-path [by default] [or return an existing instance at that ipath??].
        [Note [semi-obs]: as of some time before 061110, this is usually called via _e_eval;
         and as of 061110 it's probably always called that way;
         probably they'll be merged at some point, unless some subtle difference
         is discovered (e.g. related to finding memoized instances).]
        [Later note, 070115: soon the "eval reform" will mean this is no longer called by _e_eval.]
        """
        ##print "_e_make_in%r" % ((self, env, ipath),) #k is this ever called? [061215 Q] -- yes, lots of times in a single test.
        # of course it runs, _e_eval calls it... which will change when we do the eval/instantiate reform, maybe soon. [070112]
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
        ## assert not self._e_is_instance
        if self._e_is_instance:
            # new feature 070106, experimental but seems sensible/principled (since same as for constants like pyobjs) and desirable;
            # I'm sure about ignoring ipath but not completely sure about ignoring env, but it's my best guess,
            # and I don't know how *not* to ignore it. If you want a shared instance, this does it (see testexpr_26 for a demo
            # and some discussion); if you wanted mostly-shared but different instances, try something fancier.
            ## print "fyi: instantiating an instance returns it unchanged: %r" % self # works fine, no need to print for now
                # Q: Will we want to print this once per created main instance in which it happens, to warn about accidental use
                #    of this new feature?
                # A: I doubt we need to, since in a long time when this was an assertfail, I never saw it until I wanted to
                #    draw one instance twice (in testexpr_26).
            # [update 070117 re EVAL_REFORM -- we might do this in a caller, env.make, and perhaps make that the only caller,
            #  so it has the same noop special case for "numbers used as exprs" too ####e]
            if EVAL_REFORM:
                print("_e_make_in called on Instance even after EVAL_REFORM -- shouldn't widget_env.make or _i_instance intercept that?")
                #### in fact, _i_instance should intercept it, so it ought to never happen, so use print not printfyi. 070117
                return self
            else:
                return self
        ####e 070115: Here is where I think we need to ask self to decide what ipath a new instance should have,
        # and then if an old one is there and not out of date (which may involve comparing its init-expr to self??), return it.
        # (We may want to optimize the expr-compare by interning those exprs as we work. Maybe one could point to the other as equal?
        #  Is there any way that can optim the discovery that they're *not* equal, as full interning can? #e)
        # Alternatively, maybe the caller should ask about this first (perhaps using a larger containing expr)? No, I doubt it.
        printnim("optim (important): decide what ipath a new instance should have, and if a valid old one is there, return it")#070115
        return self.__class__(_make_in = (self,env,ipath)) # this calls _destructive_make_in on the new instance
            # note: if you accidentally define __init__ in your IorE subclass, instead of having it get its args using Arg etc,
            # you might get an exception here something like "TypeError: __init__ got an unexpected keyword argument _make_in". [070314]
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
            # update 070120: our caller _make_in wants to handle this -- by this time, a new self exists so it's too late or wasteful.
        
        expr, env, ipath = data ###@@@ might want to split env into rules (incl lexenv) & place (incl staterefs, glpane)
        assert env #061110
        assert not self._e_is_instance #e remove when works
        assert not expr._e_is_instance

        # copy all pure-expr things [order of several sections here revised, 070120]
        
        self._e_has_args = expr._e_has_args #k ??
        # copy references to _e_args & _e_kws
        # note: exprs passed to specific args or kws can be lazily type-coerced and instantiated by Arg or Option decls in subclasses
        self._e_args = expr._e_args
        self._e_kws = expr._e_kws # replaces _e_formula_dict as of 061106; WARNING: shared and mutable; WE MUST NEVER MODIFY IT

        # do pure-expr things that could (in theory) still leave us a pure expr, but are needed before instantiation
        
        ## assert expr._e_has_args, "this expr needs its arguments supplied: %r" % self
            # we might allow exceptions to this later, based on type decl, especially if it has no declared args
            # (how can we tell, here?? ###e),
            # tho there is then an ambiguity about whether you're only customizing it or not,
            # but OTOH that is tolerable if it takes no args, actually that's unclear if instantiation does something like
            # make a random choice! So we might want to detect that, warn at compile time, or so....
        if not expr._e_has_args:
            # try testexpr_9fx6. See comments near that test.
            ### update 070120: here is how I'd fix this, and propose to do it as soon as it won't confound other debugging/testing:
            # print "warning: this expr will get 0 arguments supplied implicitly: %r" % self ### remove when works [why no serno yet??]
            # 070323 -- removed the warning, since if it's ever an error, you'll find out when the missing args are accessed;
            # so far it's almost always been legit, so it's just been distracting.
            self._destructive_supply_args( () ) # supply a 0-tuple of args
                ##e in case having zero args is illegal and this [someday] detects it,
                # we should pass it a flag saying to use different error msgs in this "implicit supply args" case. (implicit = True)
                # WARNING: make sure we copied all expr stuff but set no Instance stuff before doing this!
                # And make sure the "destructive" here can't mess up expr._e_args which we share.
                # Maybe that flag we pass should also warn it not to destroy anything else (e.g. if it someday feels like
                # adding a generated keyword arg, it better copy _e_kws in this case). ##e
            assert self._e_has_args
                
        # set some Instance things
        
        self._e_is_instance = True

        self.env = env #k ok, or does it need modification of some kind?
            #e in fact we mod it every time with _self, in _e_compute_method -- can we cache that?
            # [much later: now we do, in env_for_formulae]
        ####@@@@
        self.ipath = ipath ###e does this need mixing into self.env somehow?
        ## print "assigned %r.ipath = %r" % (self,ipath) #061114 -- note, repr looks funny since fields it prints are not yet inited
        #e also set self.index??
        
        self._e_class = expr # for access to _e_kws and args #k needed? #e rename: self._e_expr? not sure. #k not yet used

        ## print "fyi my metaclass is",self.__metaclass__ # <class 'exprs.ExprsMeta.ExprsMeta'>

        #semi-obs cmts:
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
        self._i_instance_decl_env = {} # ditto, only for EVAL_REFORM kluge070119
        
        # call subclass-specific instantiation code (it should make kids, perhaps lazily, if above didn't; anything else?? ###@@@)
        self._init_instance()
        self._debug_init_instance()
        return # from _destructive_make_in
    
    def _init_class(self): ###@@@ CALL ME
        """called once per directly-instantiated python class, when its first python instance is created
        [subclasses should replace this]
        """
        pass
    def _init_expr(self): ###@@@ CALL ME
        """called once per Expr when it gets its args [details unclear, maybe not yet needed]
        [subclasses should replace this]
        """
        pass
    def _init_instance(self): #e let it be name-mangled, and call in mro order?
        """called once per python instance, but only when it represents a semantic Instance ###doc -- explain better
        [some subclasses should extend this, starting their versions with super(TheirName, self)._init_instance()]
        """
    def _debug_init_instance(self):
        if debug070120:
            #070120 debug code for _5x ER kluge070119 bug
            env = self.env
            print "%r.env has _self %r" % (self, getattr(env, '_self', '<none>'))
            assert self.env_for_formulae._self is self # remove when works -- inefficient (forces it to be made even if not needed)
        pass

    def _e_eval(self, env, ipath): # implem/behavior totally revised, late-061109; works - not sure it always will tho... ###k
        # handling of If: As of 061212 If_expr (a subclass of this) overrides _e_eval and seems to work; see comments there.
        # handling of _value: done at a higher level only -- see InstanceMacro.
        if EVAL_REFORM: #070117
            ## assert not self._e_is_instance, "EVAL_REFORM means we should not eval an instance: %r" % self
            if self._e_is_instance:
                # newly allowed 070122 for sake of _26g and _19g tests -- works
                # [guess: this would not be needed if canon_expr wrapped Instances; not confirmed, but why make it bother doing that?]
                # print "fyi: instance %r evals to itself after EVAL_REFORM" % self # remove if this is deemed fully ok and normal
                return self
            # exprs that need instantiation eval to themselves. ###k will there be exceptions that are subclasses of this?
            ## printfyi("probably normal: eval to self of a subclass of IorE: %s" % self.__class__.__name__) # find out which classes this happens to ###
            return self._e_eval_to_expr(env, ipath, self) ###e call from other _e_eval defs ??
                # not just "return self", in case we need to wrap it with a local-ipath-modifying expr
                # Q: will the point of the local ipath be eval to any pure expr wanting instantiation in future, ie "free in ipath",
                # not just eval to self? A: I think so.
        else:
            return self._e_make_in(env, ipath)
        pass
    
    # kid-instantiation, to support use of the macros Arg, Option, Instance, etc
    #k (not sure this is not needed in some other classes too, but all known needs are here)

    def _i_env_ipath_for_formula_at_index( self, index, env = None): # split out of Expr._e_compute_method 070117; revised 070120
        "#doc; semi-private helper method for Expr._e_compute_method and (after EVAL_REFORM) self._i_instance"
        ###e needs cleanup, once recent changes are tested and stable [070120]
        instance = self
        assert instance._e_is_instance
        if env is None:
            ## env0 = instance.env # fyi: AttributeError for a pure expr (ie a non-instance)
            env0 = instance.env_for_formulae
                # this change is related to bugfix [070120 935p (untested)] for bug in kluge070119 in testexpr_5x (wrong _self for ww),
                # but this is not the bugfix (since this case never happens when EVAL_REFORM),
                # but rather, compensates for not doing _self = instance below; the bugfix is to do it earlier when ER kluge070119.
        else:
            env0 = env # new feature for EVAL_REFORM for use by kluge070119
        ## env = env0.with_literal_lexmods(_self = instance) ###e could be memoized in instance, except for cyclic ref issue
            # this is done in the wrong place (here), as explained elsewhere re bug in kluge070119 [070120 924p, see 844p comment]
        env = env0
        assert env #061110
        ipath0 = instance.ipath
        ipath = (index, ipath0)
        return env, ipath

    def Instance(self, expr, index = None, permit_expr_to_vary = False, skip_expr_compare = False): #070207 added permit_expr_to_vary
        """toplevel interface (public for use in exprs) to self._i_instance; needs ##doc;
        similar to Instance macro for use in class assignments;
        except where that uses ipaths relative to _self, this uses them relative to self.
        WARNING: Index arg is required for now, and matters a lot (unintended nonuniqueness is allowed but causes bugs).
        """
        #070122; works, official for now; note relationship to Instance macro (also "def Instance")
        
        # allocating an index might be nice, but I don't see how we can do it yet
        # (the issue is when it changes due to history of prior allocs)
        # (wait, can we use the id of the child? not with this API since we have to pass it before making the child.
        #  Isn't using a unique value here equiv to that? Yes, if it's unique forever even when we're remade at same ipath --
        #  meaning it's either allocated globally, or contains our _e_serno -- no, that might get reset, not sure. Ok, globally. nim.)
        if index is None:
##            index = self._i_allocate_unique_kid_index(...)
            assert index is not None, "error: %r.Instance(%r) requires explicit index (automatic unique index is nim)" % (self, expr)
        return self._i_instance( expr, index, permit_expr_to_vary = permit_expr_to_vary, skip_expr_compare = skip_expr_compare)
    
    def _i_instance( self, expr, index, _lvalue_flag = False,  permit_expr_to_vary = False, skip_expr_compare = False ):
        # see also def Instance (the method, just above, not the macro)
        """[semi-private; used by macros like Instance, Arg, Option]
        Find or create (or perhaps recompute if invalid, but only the latest version is memoized) (and return)
        an Instance of expr, contained in self, at the given relative index, and in the same env [#e generalize env later?].
           Error (perhaps not detected) if called with same index and different other args;
        when a cached instance is returned, the other args are not used except perhaps to check for this error.
        (When an instance is recomputed, if this error happens, are new args used? undefined.)
        (#e Should we change this to make the expr effectively part of the index, for caching? Probably not; not sure.)
        (#e Should we change this to make it legal to pass a new expr? Probably not... hard for subsequent callers to be consistent...)
        WARNING: this docstring is probably out of date regarding whether expr can change and what happens if it does. [070301 comment]
        """
        # Note: Before EVAL_REFORM, this is used to do all evals, including instantiations (treated as how IorE evals).
        # It also does "eval to lval" when _lvalue_flag is true (passed only from LvalueArg, so far used only in Set).
        # After EVAL_REFORM, instantiation can't be done by eval (evals of IorE exprs return them unchanged);
        # evals are done before this is called, then this either returns constants (numbers, Instances) unchanged,
        # or instantiates exprs. It can no longer be called with _lvalue_flag when EVAL_REFORM (as of late 070119).
        def __debug_frame_repr__(locals):
            "return a string for inclusion in some calls of print_compact_stack"
            return "_i_instance(index = %r, expr = %r), self = %r" % (index,expr,self)
        assert self._e_is_instance
        if not EVAL_REFORM:
            # this is redundant with a later assert in _i_instance_CVdict in all cases (EVAL_REFORM or not),
            # and it causes trouble in the EVAL_REFORM case. To be conservative I'll only disable it in that case
            # (so I'll leave it untouched in this case). 070117
            assert is_pure_expr(expr), "who passed non-pure-expr %r to _i_instance? index %r, self %r, _e_args %r" % \
                   (expr, index, self, self._e_args)
                #k guess 061105
        else:
            if _lvalue_flag:
                print "SHOULD NEVER HAPPEN: saw _lvalue_flag: _i_instance(index = %r, expr = %r), self = %r" % (index,expr,self)
            # new behavior 070118; might be needed to fix "bug: expr or lvalflag for instance changed" in testexpr_9fx4 click,
            # or might just be hiding an underlying bug which will show up for pure exprs in If clauses -- not yet sure. #####k
            #   (Note that its only effects are an optim and to remove some error messages -- what's unknown is whether the detected
            # "errors" were real errors or not, in this case.
            #    Guess: we'll still have a ###BUG when exprs are involved, which to fix
            # will require noticing local ipath modifiers (lexenv_ipath_Expr's ipath) not only in _e_make_in but in the upcoming
            # determination of index; the best fix will be to dispense with the local cache of exprs per-index in favor of a global one
            # indexed by ipath, after those local ipath mods are included -- the same one needed for the "find" in the find or make
            # of instantiation (this find presently being nim, as mentioned somewhere else in this file in the last day or two),
            # meaning that it takes into account everything needed to create the ipath to find or make at (local mods,
            # state-sharing transforms, maybe more).)
            if is_constant_for_instantiation(expr): #revised 070131
                self._debug_i_instance_retval(expr) #070212
                return expr

        # [#k review whether this comment is still needed/correct; 061204 semiobs due to newdata change below; even more obs other ways]
        # hmm, calling Instance macro evals the expr first... can't it turn out that it changes over time?
        # I think yes... not only that, a lot of change in it should be buried inside the instance! (if it's in an arg formula)
        # as if we need to "instantiate the expr" before actually passing it... hmm, if so this is a SERIOUS LOGIC BUG. ####@@@@
        # WAIT -- can it be that the expr never changes? only its value does? and that we should pass the unevaluated expr? YES.
        # But i forgot, eval of an expr is that expr! I get confused since _e_eval evals an implicit instance -- rename it soon! ###@@@
        # [addendum 061212: see also the comments in the new overriding method If_expr._e_eval.]

        # 070119 Q: what if, right here, we burrowed into expr, and used a cvdict on a central object? as a kluge?
        # just since fast to code vs a central instantiator obj?
        # or at *least* we could do it locally -- no sharing but should fix bugs?
        if EVAL_REFORM and kluge070119:
            assert not _lvalue_flag # don't know how otherwise
            ## env = self.env # like in _i_env_ipath_for_formula_at_index [like in the old wrong version, that is]
            env = self.env_for_formulae # like in _i_env_ipath_for_formula_at_index [like in the new corrected version, 070120 940p]
            expr, env, ipath = expr, env, index
            oldstuff = expr, env, ipath
            expr, env, ipath = expr._e_burrow_for_find_or_make(env, ipath)
            if debug070120 and (expr, env, ipath) != oldstuff:
                print "fyi EVAL_REFORM kluge070119: worked, %r => %r" % (oldstuff, (expr, env, ipath))
            index = ipath
            del ipath
            self._i_instance_decl_env[index] = env
            del env
            pass
        newdata = (expr, _lvalue_flag) # revised 061204, was just expr, also renamed; cmt above is semiobs due to this
        olddata = self._i_instance_decl_data.get(index, None) # see above comment
        if skip_expr_compare:
            #070411 new optim option (public) ###UNTESTED; might or might not use in confirmation corner
            ###e should use in Arg, Option -- might be a big speedup -- but is it safe?? maybe only with IorE If, not eval If!! ###k
            expr_is_new = (olddata is None)
        else:
            expr_is_new = (olddata != newdata)
        if expr_is_new:
            if olddata is not None:
                if permit_expr_to_vary:
                    # new feature 070207
                    ### how do we remove the old instance so it gets remade?
                    ## del self._i_instance_CVdict[index] ##k guess at how -- but del might be nim in this object --
                        # good thing it was, since inval_at_key [new feature] is what we need -- del would fail to propogate invals
                        # to prior usage trackers of this now-obsolete instance!
                    ###BUG: changes to the info used to compute expr, by whatever decides to call this method (_i_instance),
                    # are usage tracked into that caller, not into our lval in our lvaldict. We depend on the caller
                    # someday getting recomputed before it will realize it wants to pass us a new expr and cause this inval.
                    # (Example of this use: a kid-column delegate in MT_try2.)
                    # THIS LATE PROPOGATION OF INVAL MIGHT LEAD TO BUGS -- not reviewed in detail.
                    # Much better would be for the callers "usage tracked so far" to somehow get subscribed to (for invals)
                    # by the thing we manually inval here. The potential bugs in the current scheme include:
                    # - inval during recompute can make more pieces of it need recompute than did when it started
                    # - if the caller's recompute never happens, the invals that need to propogate never occur at all,
                    #   though they need to.
                    # I am not sure if this can cause bugs in MT_try2 -- maybe not -- but surely it can in general!
                    ###FIX SOMEHOW (maybe as suggested above, by stealing or copying usage tracking info from caller --
                    # but it's not enough, we'd need our lval's recompute to get the caller to re-decide to call us
                    # so we'd know the new expr to recompute with! So, details of any fix are unclear.)
                    self._i_instance_CVdict.inval_at_key(index)
                    # print "fyi: made use of permit_expr_to_vary for index = %r, expr = %r" % (index, expr) # remove when works
                else:
                    print "bug: expr or lvalflag for instance changed: self = %r, index = %r, new data = %r, old data = %r" % \
                          (self,index,newdata,olddata) #e more info? i think this is an error and should not happen normally
                        # update 070122: it usually indicates an error, but it's a false alarm in the latest bugfixed testexpr_21g,
                        # since pure-expr equality should be based on formal structure, not pyobj identity. ###e
                    ####e need to print a diff of the exprs, so we see what the problem is... [070321 comment; happens with ArgList]
                    
                    #e if it does happen, should we inval that instance? yes, if this ever happens without error.
                    # [addendum 061212: see also the comments in the new overriding method If_expr._e_eval.]
                    # [one way to do that: have _i_instance_decl_data contain changetracked state vars, changed above,
                    #  usage-tracked by _CV__i_instance_CVdict. But the env matters too, so we might want to compare it too,
                    #  or compare the expr before burrowing into it, and do the
                    #  burrowing later then?? But we can't, due to the index... ###e 070122]

            self._i_instance_decl_data[index] = newdata
        else:
            # they're equal (or we were told not to bother comparing them, in which case, use the old one)
            if 0 and (not skip_expr_compare) and olddata[0] is not expr:
                # this print worked, but it's not usually useful (not enough is printed) so I disabled it
                # they're only equal because __eq__ is working on non-identical exprs [implemented in Expr late 070122]
                print "fyi: non-identical exprs compared equal (did we get it right?): %r and %r" % (olddata[0], expr) ### remove sometime
            pass
        res = self._i_instance_CVdict[index] # takes care of invals in making process? or are they impossible? ##k [see above]
        self._debug_i_instance_retval( res) #070212
        return res

    def _debug_i_instance_retval(self, res): #070212
        "[private] res is about to be returned from self._i_instance; perform debug checks [#e someday maybe do other things]"
##        NumericArrayType = type(ORIGIN)
##        if isinstance(res, NumericArrayType):
##            return res # has no __class__, but legitimate
        try:
##            assert res.__class__.__name__ != 'lexenv_ipath_Expr', "should not be returned from _i_instance: %r" % (res,)
            assert not is_pure_expr(res), "pure exprs should not be returned from _i_instance: %r" % (res,)
        except:
            print "bug: exception in _debug_i_instance_retval for this res (reraising): %s" % safe_repr(res)
            raise
        return

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
        if not EVAL_REFORM:
            # three increasingly strict asserts:
            assert expr is not None
            assert is_Expr(expr), "not is_Expr: %r" % (expr,)
            assert is_pure_expr(expr) ###k?? what if someone passes an instance -- is that permitted, but a noop for instantiation??
            assert is_Expr_pyinstance(expr), "can't instantiate a class: %r" % (expr,) # new, 070117, untested### -- i'm not even sure it's correct
            # also assume expr is "canonicalized" and even "understood" -- not sure if this is justified
            printnim("don't we need understand_expr somewhere in here? (before kidmaking in IorE)") ###@@@
        else:
            # EVAL_REFORM case 070117
            if not (is_pure_expr(expr) and is_Expr_pyinstance(expr)):
                print "this should never happen as of 070118 since we handle it above: non pure expr %r in _CV__i_instance_CVdict" % (expr,)
                ## print "FYI: EVAL_REFORM: _CV__i_instance_CVdict is identity on %r" % (expr,)
                # this is routine on e.g. None, small ints, colors, other tuples... and presumably Instances (not tested)
                assert not lvalflag # see comments at start of _i_instance
                return expr
            pass
        ####e:  [061105] is _e_eval actually needing to be different from _e_make_in?? yes, _e_eval needs to be told _self
        # and the other needs to make one... no wait, wrong, different selves --
        # the _self told to eval is the one _make_in *should make something inside of*! (ie should make a kid of)
        # So it may be that these are actually the same thing. (See paper notes from today for more about this.)
        # For now, tho, we'll define _e_make_in on OpExpr to use eval. [not done, where i am]
        # actually this is even faster -- review sometime (note, in constant_Expr they're both there & equiv #k): ###@@@
        ## this is just the kid expr: print "_CV__i_instance_CVdict needs to make expr %r" % (expr,)
##        if hasattr(expr, '_e_make_in'):
##            print("REJECTED using _e_make_in case, on a pyinstance of class %s" % expr.__class__.__name__)###was printfyi til 061208 921p
##            ## res = expr._e_make_in(env, index_path)
##                #k we might have to fix bugs caused by not using this case, by defining (or modifying?) defs of _e_eval on some classes;
##                # addendum 061212, we now do that on If_expr.
        if not EVAL_REFORM:
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
        else:
            # EVAL_REFORM case, 070117
            if kluge070119:
                # also pass an env retrieved from...
                env = self._i_instance_decl_env[index]
                env, ipath = self._i_env_ipath_for_formula_at_index( index, env) # note: retval's env is modified from the one passed
                    # THIS MUST BE WHERE THE INCORRECT BINDING _self = self gets added, in the kluge070119 ###BUG in _5x! [070120 844p]
                    #   GUESS at basic bug: an Instance self really needs to know two envs: the one for its args (_self refers to
                    # whoeever lexically created the expr they were made from), and the one for their internal formulae (_self = self).
                    # self.env is the one for the args (since it's thought of as "self's (outer) environment"),
                    # and the one for internal formulae has (until now -- this should change #e) been recreated as needed in
                    # _e_compute_method and now in _i_env_ipath_for_formula_at_index, by extending self.env by _self = self.
                    #   But to be correct, this should be done BEFORE the burrowing and env-extension done by the kluge070119,
                    # but in this wrong current code it's done after it. The old code also had wrongness of order, in principle
                    # (doing this _self addition here rather than in env_for_args, with env_for_args done first when it should
                    # be done 2nd), but it didn't matter since env_for_args only added _this_xxx and _my. WAIT, THAT'S WRONG --
                    # env_for_args is for external (in lexenv) args, so it should have SAME _self as self.env, so it's correct now,
                    # and never gets or needs _self = self, either before or after its _my and _this_xxx bindings.
                    #   What we need here is NOT env_for_args but env_for_internal_formulae. It should be used for dflt exprs in Arg,
                    # and for all exprs sitting on class assignments. We've been making it before *using* those formulae
                    # (probably getting it onto dflt exprs only because they end up being *used* in the right place for that).
                    # We've been making it in each call of _i_env_ipath_for_formula_at_index or _e_compute_method, but we ought to
                    # make it once and let those use it, and make sure that happens before the env mods from the burrowing done by
                    # kluge070119. (We can't make it in the class (eg ExprsMeta) -- we have to wait until _init_instance or so,
                    # because it depends on self which is only known around then.)
                    # 
                    # SUGGESTED FIX ###e: make self.env_for_internal_formulae (#e shorter name -- env_for_formulae?)
                    # before (??) calling _init_instance [or after if _init_instance can modify self.env ##k];
                    # use it in _i_env_ipath_for_formula_at_index and some of our uses of _e_compute_method;
                    # and review all uses of self.env for whether they ought to be env_for_formulae.
                    # Doing it 070120 circa 942p -- I made _C_env_for_formulae instead of setting it in _init_instance
                    # (optim, since some Instances never need it (I hope -- not sure) and since it creates a cyclic ref.
            else:
                env, ipath = self._i_env_ipath_for_formula_at_index( index) # equivalent to how above other case computes them
            assert not lvalflag # see comments at start of _i_instance
            res = expr._e_make_in(env,ipath) # only pure IorE exprs have this method; should be ok since only they are returned from expr evals
        return res # from _CV__i_instance_CVdict

    def _i_eval_dfltval_expr(self, expr, index): ##e maybe unify with above, but unclear when we soon split eval from instantiate
        "evaluate a dfltval expr as used in State macro of 061203; using similar code as _CV__i_instance_CVdict for Instance..."
        # WARNING: similar code to end of _CV__i_instance_CVdict
        # note: this (used-to-be-redundantly) grabs env from self
        # Note about EVAL_REFORM: I think this needs no change, since these exprs can now be evalled to pure exprs,
        # then if desired passed through instantiation.
        try:
            computer = expr._e_compute_method(self, index) ##e optim someday: inline this
                # 061105 bug3, if bug2 was in held_dflt_expr and bug1 was 'dflt 10'
            res = call_but_discard_tracked_usage( computer) # see also docstring of eval_and_discard_tracked_usage
                # res is the same as if we did res = computer(), but that would track usage into caller which it doesn't want invals from
        except:
            print "following exception concerns self = %r, index = %r in *** _i_eval_dfltval_expr *** calling _e_compute_method" % \
                  (self, index)
            raise
        return res
        
    def _i_grabarg( self, attr, argpos, dflt_expr, _arglist = False): 
        "#doc, especially the special values for some of these args"
        debug = False ## _arglist
        if debug:
            print_compact_stack( "_i_grabarg called with ( self %r, attr %r, argpos %r, dflt_expr %r, _arglist %r): " % \
                                 (self, attr, argpos, dflt_expr, _arglist) )
            print " and the data it grabs from is _e_kws = %r, _e_args = %r" % (self._e_kws, self._e_args)
        #k below should not _e_eval or canon_expr without review -- should return an arg expr or dflt expr, not its value
        # (tho for now it also can return None on error -- probably causing bugs in callers)
        assert is_pure_expr(dflt_expr), "_i_grabarg dflt_expr should be an expr, not %r" % (dflt_expr,) #061105 - or use canon_expr?
        assert self._e_is_instance
        if not self._e_has_args:
            print "warning: possible bug: not self._e_has_args in _i_grabarg%r in %r" % ((attr, argpos), self)
        assert attr is None or isinstance(attr, str)
        assert argpos is None or (isinstance(argpos, int) and argpos >= 0)
        assert _arglist in (False, True)
        external_flag, res0 = self._i_grabarg_0(attr, argpos, dflt_expr, _arglist = _arglist)
        if external_flag:
            # flag and this condition added 061116 443p to try to fix '_self dflt_expr bug'; seems to work in testexpr_9a;
            # I'm guessing type_expr doesn't have a similar bug since it's applied outside this call. #k
            index = attr or argpos #k I guess, for now [070105 stub -- not always equal to index in ipath, esp for ArgOrOption]
            env_for_arg = self.env_for_arg(index) # revised 070105
            if debug070120:
                print "grabarg %r in %r is wrapping %r with %r containing _self %r" % \
                      ((attr, argpos), self, res0,  env_for_arg, getattr(env_for_arg,'_self','<none>'))
            res = lexenv_Expr(env_for_arg, res0) ##k lexenv_Expr is guess, 061110 late, seems confirmed; env_for_args 061114
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
        if debug:
            print "_i_grabarg returns %r" % (res,)
        return res

    def env_for_arg(self, index): # 070105 experiment -- for now, it only exists so we can override it in certain primitive subclasses
        """Return the env to use for the arg (or kid?) at the given index (attr or argpos, I guess, for now #k).
        By default this is just self.env_for_args.
        Certain subclasses [intended to be dynenv-modifying primitives, not user macros]
        can override this (for specific indices) to supply other envs based on self.env_for_args or self.env,
        using .with_lexmods(dict) to alter one of those envs. They should use self.env_for_args if they want to
        lexically bind _this(theirname) and _my, not otherwise. For OpExpr-like primitives it might be best to use self.env.
           Note that overriding this method in a user-level macro (e.g. one based on DelegatingInstanceOrExpr)
        may not work as expected, since this is only used to alter the env for exprs that come from outside as actual args,
        not those that are defined internally by formulae (not even the default value formula for an arg).
        """
        return self.env_for_args
        
    def _C_env_for_args(self):###NAMECONFLICT? i.e. an attr whose name doesn't start with _ (let alone __ _i_ or _e_) in some exprs
        "#doc"
        lexmods = {} # lexmods for the args, relative to our env
        thisname = thisname_of_class(self.__class__) ##e someday make it safe for duplicate-named classes
            # (Direct use of Symbol('_this_Xxx') will work now, but is pretty useless since those symbols need to be created/imported.
            #  The preferred way to do the same is _this(class), which for now [061114] evals to the same thing that symbol would,
            #  namely, to what we store here in lexmods for thisname. See "class _this".)
        
        lexmods[thisname] = self
            # WARNING: this creates a cyclic ref, from each child whose env contains lexmods, to self, to each child self still knows.
            # In fact, it also creates a cyclic ref from self to self, since the result (which contains lexmods) is memoized in self.

        lexmods['_my'] = self #061205
        
        return self.env.with_lexmods(lexmods)

    def _C_env_for_formulae(self):#070120 for fixing bug in kluge070119
        "compute method for self.env_for_formulae -- memoized environment for use by our internal formulae (class-assigned exprs)"
        res = self.env.with_literal_lexmods( _self = self)
            # This used to be done (each time needed) in _e_compute_method and _i_env_ipath_for_formula_at_index --
            # doing it there was wrong since it sometimes did it after env mods by kluge070119 that needed to be done after it
            # (in order to mask its effect).
            # WARNING: doing it here creates a cyclic ref from self to self, since the result is memoized in self.
        return res

    def _i_grabarg_0( self, attr, argpos, dflt_expr, _arglist = False):
        "[private helper for _i_grabarg] return the pair (external-flag, expr to use for this arg)"
        # i think dflt_expr can be _E_REQUIRED_ARG_, or any (other) expr
        from __Symbols__ import _E_REQUIRED_ARG_
        if dflt_expr is _E_REQUIRED_ARG_:
            required = True
        else:
            required = False
            if isinstance(dflt_expr, _E_REQUIRED_ARG_.__class__) and dflt_expr._e_name.startswith("_E_"):
                print "possible bug: dflt_expr for arg %r in %r is a Symbol %r named _E_* (suspicious internal symbol??)" % \
                      ( (attr, argpos), self, dflt_expr )
                # kluge sanity check for _E_ATTR or other internal symbols [revised 070131]
        if attr is not None and argpos is not None:
            printnim("should assert that no expr gets same arg twice (positionally and as named option)")###e
        if attr is not None:
            # try to find it in _e_kws; I suppose the cond is an optim or for clarity, since None won't be a key of _e_kws
            try:
                return True, self._e_kws[attr]
            except KeyError:
                pass
        if argpos is not None:
            try:
                res = self._e_args[argpos]
            except IndexError: # "tuple index out of range"
                pass
            else:
                # res was the arg provided at argpos
                if _arglist:
                    res = tuple_Expr(* self._e_args[argpos:])
                return True, res                
        # no arg was provided at argpos
        if _arglist:
            # [_arglist supports ArgList, a new feature 070321]
            # no args were provided for an ArgList -- use dflt_expr, or tuple_Expr().
            # (Note: we don't use list_Expr. See comments near def of ArgList.)
            if required:
                return False, tuple_Expr() #k probably equiv to canon_expr(())
                     ##k optim-related Q: what should external_flag be in this case? [070321 Q]
            else:
                return False, dflt_expr # note: nothing fundamental requires that dflt_expr evals/instantiates to a list or tuple,
                    # though it would usually be an error if it doesn't (depending on how the class body formulae were written).
                    # It's not an error per se, just likely to be one given how ArgList is conventionally used.
        else:
            # ordinary arg was not provided -- error or use dflt_expr
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
                return False, canon_expr(None)
                    ##k optim-related Q: what should external_flag be in this case? [070321 Q]
            else:
                return False, dflt_expr
        pass # above should not _e_eval or canon_expr without review -- should return an arg or dflt expr, not its value

    def drawkid(self, kid): # note: supersedes nim _e_decorate_draw [070210]
        #e plans: debug_pref for no-net-coord-change enforcement (for testing),
        # and most importantly, make possible a drawing pass which draws only a specified subset of drawables
        # but in their coord- or glstate- transforming containers, e.g. for a highlight-drawing pass.
        #
        # Update 070414:
        #    To accomplish that, we need to record a kid->parent map during draw (transient per-frame) or before it;
        # for kids with multiple parents, we hope (in evolving a simple API for this) that the parent-chains
        # have different glname-chains unless both kid copies can be co-highlighted;
        # for kids drawn twice by one parent (e.g. a stereo-viewer or a parent which does some sort of draw/overdraw scheme),
        # we'd probably like that parent to wrap each one differently, so no kid is really drawn twice by one parent,
        # and so the wrapper can give each one a different glname if necessary, or tell one not to record drawing-coords
        # (or equiv drawing-parent-chain info) for highlighting.
        #    For a prototype of related code from 070219 or earlier, see a scratch file, rendering.py.
        if kid is not None:
            try:
                if is_expr_Instance(kid):
                    kid.draw()
                else:
                    print "***BUG: drawkid in %r sees non-Instance (skipping it): %r" % (self, kid,)
                        #070226, worrying about self.delegate rather than self._delegate being passed --
                        # common but why does it work??####BUG?? in testexpr_33x I tried it and it fails here...
                        # I predict there are a bunch of bugs like this, that some used to work, and others were not tested
                        # since drawkid came in, and in others self.delegate happens to be an Instance (maybe not true bugs then,
                        # but unclear). Hmm, if delegate = Arg() then it is always an Instance -- a style decision is needed for that --
                        # it should be "always use _delegate" even then I think, otherwise the code is a bad example.
                        ###FIX all calls of drawkid
            except:
                print_compact_traceback("bug: exception in %r.drawkid(%r): " % (self, kid))
        return
    
    def _C__delegate(self): #070121
        delegate = self.delegate
        if is_pure_expr(delegate):
            # instantiate it, as if it was wrapped with Instance -- do exactly what Instance would do
            delegate = self._i_instance( delegate, 'delegate')
                # is that the same index Instance would use? I think so (it gets passed _E_ATTR which should get replaced with this).
        return delegate

    # == methods moved from class Widget (which is being merged into this one for now -- merge is not complete, it exists as an
    #  empty shell ###fix) [070201]

    # note: this is a method in case color is in local coords, BUT that won't work properly if subclass ought to delegate
    # this -- this def means it won't. Still, for now keep it here since implem never changes. Later clean up delegation for this
    # as discussed elsewhere. ###fix [070201]
    def fix_color(self, color): #e move to glpane??
        """Return the given color, suitably formatted for passing to low-level drawing code for the current drawing medium.
        The color is assumed to be evaluated (i.e. no longer a formula), but perhaps in some general data format
        and perhaps needing to be subjected to global color transformations stored transiently in the drawing medium object
        (e.g. a color warp or constant alpha, stored in the glpane).
        [#e If it proves unworkable for this method to know the current drawing medium,
         it will probably be replaced with more specific methods, eg fix_color_GL and fix_color_POVRay.]
        [#e Will we have to have variants of _GL for returning 3 tuples or 4 tuples as the color?]
        [#e Will we have to worry about material properties?]
        """
        #e first decode it and normalize it as needed
        color_orig = color # for error messages
        color = normalize_color(color)
        warpfuncs = getattr(self.env.glpane, '_exprs__warpfuncs', None) #070215 new feature
        while warpfuncs:
            func, warpfuncs = warpfuncs # pop next func from nested list
            try:
                # do color = normalize_color(func(color)), but don't change color if anything goes wrong
                color0 = '?' # for error message in case of exception
                color0 = func(color) # don't alter color itself until we're sure we had no exception in this try clause
                color = normalize_color(color0) # do this here (not in next while loop body), since errors in it are func's fault
            except:
                print_compact_traceback("exception in %r.fix_color(%r) warping color %r with func %r (color0 = %r): " % \
                                        ( self, color_orig, color, func, color0 ) )
                pass
            continue
        return color
            ###e guess: it comes from the glpane as a method on it. the glpane is in our env.
            # self.env.glpane.fix_color
        ### fix_color is a method on self, I guess, or maybe on env (and env may either be self.env or an arg to this method -- guess, arg)
        # or maybe it has contribs from env, class, and glpane -- glpane to know what kind of color it needs,
        # env or glpane to know about warps or alphas to apply, class maybe, and something to know about resolving formulas (env?)
        ### we'll have fix_ for the dims too, handling their units, perhaps in a way specific to this class
        ### we'll have memoization code for all these attrs
        ### and we'll need better control of gl state like GL_CULL_FACE, if we can run this while it's already disabled

    # note: draw can't be defined here since it masks the one provided by the delegate, if the subclass delegates! [070201]    
##    def draw(self):
##        "#doc"
##        print "warning: no draw method in %r" % self # probably verbose enough to not be missed...
##        return

    def KLUGE_gl_update(self): #070213
        """###KLUGE: call our glpane.gl_update explicitly. Should never be needed (unless there are bugs),
        since any change that affects what we draw should be changed-tracked when made, and usage-tracked when some
        draw method (used directly or to make displist contents) uses it. But evidently there are such bugs [as of 070213],
        since some things apparently need to call this.
           Note: all calls of gl_update should go through this method, if possible,
        if they're needed due to changes in attrs of self.
        """
        self.env.glpane.gl_update()
        return
    
    pass # end of class InstanceOrExpr

# ===

_DELEGATION_DEBUG_ATTR = '' # you can set this to an attrname of interest, at runtime, for debugging

class DelegatingMixin(object): # 061109 # see also DelegatingInstanceOrExpr #070121 renamed delegate -> _delegate, let IorE relate them
    """#doc: like Delegator, but only legal in subclasses which also inherit from InstanceOrExpr;
    other differences from Delegator:
    - we delegate to self._delegate rather than self.delegate
    - we don't delegate any attrs that start with '_'
    - no caching, in case the delegate varies over time
    - self._delegate should be defined by the subclass rather than being an instance variable of this class
      (e.g. it might be recomputable from a formula or _C__delegate compute method handled by ExprsMeta,
       or assigned in __init__)
    - we only support subclasses which also inherit from InstanceOrExpr
      - note: they should include InstanceOrExpr before DelegatingMixin in their list of base classes
      - note: InstanceOrExpr defines a compute method for self._delegate from self.delegate (which instantiates it if needed)
    - we don't start delegating until self is an Instance; before that we print a warning to say it was tried. (#k is it an error??)
      [##e This is why we don't support use by non-IorE subclasses. Maybe we could generalize this class to use a more general way
       of asking the pyinstance whether to delegate yet, like some other optional flag attr or method.
       (But probably not just by testing self._delegate is None, since the point is to avoid running a compute method
        for self._delegate too early -- in IorE subclasses this would cause an error when they're a pure expr.)]
    """
    # Note: DelegatingMixin has always appeared after IorE (not before it) in the list of base classes.
    # I think this order can't matter, since it only defines __getattr__, which is not otherwise defined in any IorE
    # subclass or superclass, and DelegatingMixin is only legal in IorE (and I just now verified it's only used there, 070206).
    # The only "close calls" are that __getattr__ is defined in SymbolicExpr, and some obsolete code said
    #   "class _this(SymbolicInstanceOrExpr, DelegatingMixin)".
    # So if we wanted to require DelegatingMixin to come first (so it could override things defined in IorE
    # or its subclasses (like the experimental _i_type, if it survives)), we could probably make that change.

    ##e optim: do this instead of the assert about attr: _delegate = None # safer default -- prevent infrecur
    def __getattr__(self, attr): # in class DelegatingMixin
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
##                    # additional test hasattr(self._delegate, attr) doesn't work: AssertionError: compute method asked for on non-Instance
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
            assert attr != 'delegate', "DelegatingMixin refuses to delegate self.delegate (which would infrecur) in %r -- " \
                   "does its class lack a definition of delegate?" % self
                # that assert makes sense even though our low-level delegate is now self._delegate. [070121]
            if expr_is_Instance(self):
                recursing = self.__dict__.setdefault('__delegating_now', False) # note: would be name-mangled if set normally
                assert not recursing, "recursion in self._delegate computation in %r" % self #061121
                self.__dict__['__delegating_now'] = True
                try:
                    delegate = self._delegate
                finally:
                    self.__dict__['__delegating_now'] = False #e or could del it, presumed less efficient, not sure
                ##e could check that delegate is not None, is an Instance (??), etc (could print it if not)
                #k Should it be silently tolerated if delegate is None? Probably no need -- None won't usually have the attr,
                # so it will raise the same exception we would. Are there confusing cases where None *does* have the attr??
                # I doubt it (since we're excluding _attrs). But it's worth giving more info about likely errors, so I'm printing some.
                if delegate is None:
                    raise AttributeError, attr # new feature 070121: this means there is no delegate (more useful than a delegate of None).
                if is_pure_expr(delegate):
                    print_compact_stack( "likely-invalid _delegate %r for %r in self = %r: " % (delegate, attr, self)) #061114
                if attr == _DELEGATION_DEBUG_ATTR: # you can set that to any attr of current interest, for debugging
                    print "debug_attr: delegating %r from %r to %r" % (attr, self, delegate)
                try:
                    res = getattr(delegate, attr) # here is where we delegate. It's normal for this to raise AttributeError (I think).
                except AttributeError:
                    #### catching this is too expensive for routine use (since I think it's often legitimate and maybe common -- not sure),
                    # but it's useful for debugging -- so leave it in for now. 061114
                    printnim("too expensive for routine use")
                    msg = "no attr %r in delegate %r of self = %r" % (attr, delegate, self)
                    if attr == _DELEGATION_DEBUG_ATTR: 
                        print "debug_attr:", msg
                    raise AttributeError, msg
                else:
                    if attr == _DELEGATION_DEBUG_ATTR:
                        print "debug_attr: delegation of %r from %r is returning %r" % (attr, self, res) #070208
                    return res
            print "DelegatingMixin: too early to delegate %r from %r, which is still a pure Expr" % (attr, self)
                # it might be an error to try computing self._delegate this early, so don't print it even if you can compute it
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

class InstanceMacro(InstanceOrExpr, DelegatingMixin): # ca. 061110; docstring revised 061127 & 070117; see also DelegatingInstanceOrExpr
    """Superclass for "macros" -- they should define a formula for _value which they should always look like.
    # WARNING: a defect in InstanceMacro means that "default defs" in its client class (e.g. thing, ww in Boxed),
    # or in a superclass of that, will override their defs in _value rather than being delegated to _value
    # (since they are already defined, so they're never seen by DelegatingMixin.__getattr__);
    # so be careful what you name those local defs, and what default values are defined in a superclass!
    #    This is also sometimes a feature, especially when the local defs occur in the same class that defines _value
    # (permitting you to override some of the otherwise-delegated attrs, e.g. bright or width),
    # tho at one time I thought delegate should let you do that, _value should not,
    # and this would be a useful distinction. I don't yet know how to make _value not do it,
    # nor whether that's desirable if possible, nor whether it's well-defined. ###@@@ [061114]
    #    It means, for example, that the InstanceMacro Boxed would not work if it inherited from Widget2D,
    # since it would pick up Widget2D default values for lbox attrs like btop. [unconfirmed but likely; 061127 comment]
    """
    #e might not work together with use by the macro of DelegatingMixin in its own way, if that's even possible [later: not sure what this comment means]
    if EVAL_REFORM:
        printnim("is this eval_Expr correct or not? does it even make any difference??")
        ## delegate = Instance( eval_Expr(_self._value), '!_value') #### guess about fixing testexpr_5 bug; didn't make any clear difference [070117]
        delegate = Instance( _self._value, '!_value') # innocent until proven guilty, even if suspected (more seriously, don't change what might not be wrong)
        # Note: as of 070121 late, due to changes in IorE, this explicit Instance() should no longer be needed (when EVAL_REFORM or not).
        # But that's only been tested in other classes and when EVAL_REFORM.
    else:
        # old code, worked for a long time
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
    def _e_model_type_you_make(self): ###k 070215 very experimental
        "#doc; overrides super version; see variant in DelegatingInstanceOrExpr"
        # assume we are a graphical DIorE (like a model obj decorator -- Overlay, Translate, DraggableObject...), so we do delegate it...
        # but wait, is code for this different if we're expr or instance? instance could go to _delegate, expr to _value
        if self._e_is_instance:
            return self._delegate._e_model_type_you_make() ###e check self._delegate not None??
        else:
            assert is_pure_expr(self._value)
            return self._value._e_model_type_you_make()
        pass
    pass # end of class InstanceMacro

# ==

class DelegatingInstanceOrExpr(InstanceOrExpr, DelegatingMixin): # moved here & basic 061211, created a few days before
    """#doc
    """
    #e this might replace most uses of DelegatingMixin and InstanceMacro, if I like it

    def _e_model_type_you_make(self): ###k 070215 very experimental
        "#doc; overrides super version; see variant in InstanceMacro"
        # assume we are a graphical DIorE (like a model obj decorator -- Overlay, Translate, DraggableObject...), so we do delegate it...
        # but wait, is code for this different if we're expr or instance? instance could go to _delegate, expr to delegate
        if self._e_is_instance:
            return self._delegate._e_model_type_you_make() ###e check self._delegate not None??
        else:
            assert is_pure_expr(self.delegate) # can this fail for glue-code-objs or helper-objs like the ones MT_try2 makes? ##k
            return self.delegate._e_model_type_you_make()
        pass
    pass

# new unfinished code, not sure useful, commented out, goes with other such code from today related to _i_type [070206]
##class InstanceWrapper(DelegatingInstanceOrExpr): #070206 ###e rename??? not yet used. see below for analysis of who should use this.
##    """[proposed] The standard superclass for an InstanceOrExpr which delegates to another one
##    (an instance of an expr defined by each subclass as self.delegate, which can be time-varying)
##    in such a way as to "wrap" or "decorate" it without changing its type.
##       (Note: It's possible that the implem of delegation in all such cases will be changed someday
##    so that self and its delegate are the same object, only differing in unbound method functions. ###e)
##    """
##    _e_delegate_type = True
##    pass

# Should the following delegating IorE subclasses delegate their type? [070206 survey]
# Note, this only matters if they are fed into a model-object-container and wrapped around a model object --
# if that can ever happen legitimately, say yes -- or if they are used as model object even if they're a graphics primitive
# like Cylinder (really a geometric object, not just a graphics prim). So for Overlay we'll say yes, in case it wraps
# a model obj, even though that should probably not occur directly in a model obj container. Same with Highlighting, etc.
# We'll only say no for things that might look like model objects themselves (whose type a user might want to see as the
# type of object they put in the model). So far most of the code here is not a model obj, so maybe I should make the default yes...
#
# SpacerFor - no (it takes the size of a model object, but it surely does not take other aspects of its nature)
#   [###e this suggests that what's really going on is that we need to be saying what interfaces we do and don't delegate,
#    and SpacerFor is delegating layout but not other graphics and not model nature, which this "type" is part of --
#    really it's not just plain type, but "model object type".]
# Highlightable(image) - no
# Highlightable(ModelObject) - maybe yes, but looks deprecated -- Highlightable should be used in a viewing macro. So no.
# ImageChunk [not yet used] - like Highlightable? no... unclear. Maybe this model/graphics-object distinction needs formalization...
# Overlay - 
# ==

class ModelObject(DelegatingInstanceOrExpr): #070201 moved here from demo_drag.py; see also ModelObject3D, Geom3D...
    ###WARNING: as of 070401 it's unclear if the value of _e_model_type_you_make is used for anything except other implems
    # of the same method.
    """#doc -- class for datalike objects within the model
    [this may diverge from DelegatingInstanceOrExpr somehow -- or i might be mistaken that it needs to differ,
    but if so, it might have a better name! ###e]
    """
    # One way it might diverge -- in having delegation to env.viewer_for_model_object [nim];
    # something like this:
    ###e delegate = something from env.viewer_for_model_object(self) or so
    #070203 for now, superclass provides a default delegate of None, since some subclasses have one (which will override that)
    # and some don't, and without this, the ones that don't have an assertfail when they ought to have an AttributeError.
    delegate = None
    def _e_model_type_you_make(self): ###k 070215 very experimental
        "#doc; overrides super version"
        # but lots of specific DIorE don't delegate it...
        # model obj DIorE don't [that's us], but graphical ones do. For now assume we know by whether it's subclass of ModelObj.
        return InstanceOrExpr._e_model_type_you_make(self) # that implem has the right idea for us -- use classname
    pass

class WithModelType(DelegatingInstanceOrExpr): # 070215 experimental, ###UNTESTED (except for not damaging delegate when instantiated)
    "#doc better -- be like arg1, but with arg2 specifying the model type -- note, arg2 has to be accessed even when we're an expr"
    delegate = Arg(InstanceOrExpr) #e first use of that as type -- ok in general? correct here?
    arg_for_model_type = Arg(str) #e wrong Arg type? #e have an option to say this Arg works even on exprs???? (very dubious idea)
    def _e_model_type_you_make(self): ###k 070215 very experimental
            # note: this would not be delegated even if overridden, I think, due to _e_ -- not sure! ####k
        if self._e_is_instance:
            return self.arg_for_model_type
        else:
            type_expr = self._e_args[1] # kluge? btw did this go thru canon_expr? yes...
            res = type_expr._e_constant_value ##k name ###e check for errors ##e use a helper function we have that does this (in If?)
            assert type(res) == type("") or res is None ##e remove when works, if we extend legal kinds of model_types
            return res
        pass
    pass

class WithAttributes(DelegatingInstanceOrExpr): # 070216 experimental, STUB
    "#doc better -- be like arg1, but with options specifying attrs you have (like customizations, but with new Option decls too)"
    delegate = Arg(InstanceOrExpr)
    def _init_instance(self):
        for k, v in self._e_kws.items():
            # we hope v is a constant_Expr
            ok, vv = expr_constant_value(v)
            assert ok, "WithAttributes only supports constant attribute values for now, not exprs like in %s = %r" % (k,v,)
            #e to support exprs, set up the same thing as if our class had k = Option(Anything) and v got passed in (as it did)
            # (note, vv is the eval of v, so we could just eval v here -- but need to wrap it in proper env...
            #  sometime see how much of needed work _i_grabarg already does for us -- maybe it's not hard to unstub this. ##e)
            setattr(self, k, vv)
        return
    pass

# ==

class _this(SymbolicExpr): # it needs to be symbolic to support automatic getattr_Expr
    """_this(class) refers to the instance of the innermost lexically enclosing expr with the same name(?) as class.
    """
    #### NOT YET REVIEWED FOR EVAL_REFORM 070117
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

    ##class _this(SymbolicInstanceOrExpr_obs, DelegatingMixin): #061113; might work for now, prob not ok in the long run
    #e [see an outtakes file, or cvs rev 1.57, for more of this obs code for _this, which might be useful someday]

# end
