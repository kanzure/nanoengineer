# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
IorE_guest_mixin.py -- WILL BE RENAMED to fit class, when class is renamed

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

070815 split IorE_guest_mixin superclass out of InstanceOrExpr
and moved it into this new file
"""

from exprs.lvals import call_but_discard_tracked_usage

from exprs.widget_env import thisname_of_class, widget_env

from utilities.debug import safe_repr
from utilities.debug import print_compact_stack

from exprs.Exprs import Expr
from exprs.Exprs import is_pure_expr
from exprs.Exprs import is_constant_for_instantiation
from exprs.Exprs import is_Expr
from exprs.Exprs import is_Expr_pyinstance
from exprs.Exprs import lexenv_Expr
from exprs.Exprs import tuple_Expr
from exprs.Exprs import canon_expr
from exprs.Exprs import EVAL_REFORM

from exprs.ExprsMeta import ExprsMeta
from exprs.StatePlace import StatePlace
from exprs.py_utils import printnim
from exprs.__Symbols__ import _E_REQUIRED_ARG_

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

class IorE_guest_mixin(Expr): #bruce 070815 split this out of its InstanceOrExpr subclass
    """
    @note: This class will be renamed and probably further split.
           For most doc, see our InstanceOrExpr subclass.

    This is the part of InstanceOrExpr which supports sub-instance making
    (requiring self.env and self.ipath i think),
    and formula/Arg/Option/State eval in attr decl formulae in a subclass,
    and some standard stateplaces for use by State then;
    but not expr customization by __init__ or __call__, or _e_make_in,
    or drawing-specific things -- for those see InstanceOrExpr.
    """
    __metaclass__ = ExprsMeta

    transient_state = StatePlace('transient') # state which matters during a drag; scroll-position state; etc

    def __init__(self, _e_glpane = None, _e_env = None, _e_ipath = None, _e_state = None ):
        """
        [needs doc]
        Note: If we're born an Instance, then either _e_env or _e_glpane must be passed.
        (The keyword args are not meant to be passed from IorE itself, or its subclasses.)
        _e_glpane can be passed as a positional argument. We might rename these w/o _e_.
        """
        self._e_init_e_serno() #k needed?

        if self._e_is_instance:
            # This only happens for classes which set this class constant to indicate
            # their pyinstances should be born as Instances from the start.
            # They need to pass either _e_env or (_e_glpane and optionally _e_state).
            if _e_env is None:
                # make a widget_env
                if _e_state is None:
                    _e_state = {}
                assert _e_glpane
                _e_env = widget_env( _e_glpane, _e_state)

            if _e_ipath is None:
                _e_ipath = str(id(self)) #k??

            self._init_self_as_Instance( _e_env, _e_ipath)
        else:
            assert _e_env is None and _e_ipath is None
                # other values not yet supported; i doubt these make sense before we have an Instance

        return

    # no __call__ in this class

    def _init_self_as_Instance(self, env, ipath): #bruce 070815 split this out of IorE._destructive_make_in
        """
        (in principle, only needed if self should support formulae or subinstances)
        """
        assert self._e_is_instance

        self.env = env #k ok, or does it need modification of some kind?
            #e in fact we mod it every time with _self, in _e_compute_method -- can we cache that?
            # [much later: now we do, in env_for_formulae]
        ####@@@@
        self.ipath = ipath ###e does this need mixing into self.env somehow?
        ## print "assigned %r.ipath = %r" % (self,ipath) #061114 -- note, repr looks funny since fields it prints are not yet inited
        #e also set self.index??

        ## print "fyi my metaclass is",self.__metaclass__ # <class 'exprs.ExprsMeta.ExprsMeta'>

        # set up state refs
        ## printnim("instance_helpers needs setup state refs") [not necessarily implemented, but don't spend runtime to print that]

        self._i_instance_decl_data = {} # private storage for self._i_instance method [renamed from _i_instance_exprs, 061204]
        self._i_instance_decl_env = {} # ditto, only for EVAL_REFORM kluge070119

        # call subclass-specific instantiation code (it should make kids, perhaps lazily, if above didn't; anything else?? ###@@@)
        self._init_instance()
        self._debug_init_instance()
        return # from _init_self_as_Instance

    def _init_instance(self): #e let it be name-mangled, and call in mro order?
        """
        called once per python instance, but only when it represents
        a semantic Instance ###doc -- explain better
        [some subclasses should extend this, starting their versions
         with super(TheirName, self)._init_instance()]
        """
    def _debug_init_instance(self):
        if debug070120:
            #070120 debug code for _5x ER kluge070119 bug
            env = self.env
            print "%r.env has _self %r" % (self, getattr(env, '_self', '<none>'))
            assert self.env_for_formulae._self is self # remove when works -- inefficient (forces it to be made even if not needed)
        pass

    # might need to move the method custom_compute_method here, from our subclass IorE ###REVIEW

    # kid-instantiation support, to support use of the macros Arg, Option, Instance, etc
    #k (not sure this is not needed in some other classes too, but all known needs are here)

    def _i_env_ipath_for_formula_at_index( self, index, env = None): # split out of Expr._e_compute_method 070117; revised 070120
        """
        #doc; semi-private helper method for Expr._e_compute_method
        and (after EVAL_REFORM) self._i_instance
        """
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
        """
        toplevel interface (public for use in exprs) to self._i_instance;
        needs ##doc;
        similar to Instance macro for use in class assignments;
        except where that uses ipaths relative to _self, this uses them
        relative to self.

        @warning: Index arg is required for now, and matters a lot
                  (unintended nonuniqueness is allowed but causes bugs).
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
        """
        [semi-private; used by macros like Instance, Arg, Option]

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
            """
            return a string for inclusion in some calls of print_compact_stack
            """
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
        """
        [private]
        res is about to be returned from self._i_instance;
        perform debug checks [#e someday maybe do other things]
        """
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
        """
        [private]
        value-recomputing function for self._i_instance_CVdict.
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
        """
        evaluate a dfltval expr as used in State macro of 061203;
        using similar code as _CV__i_instance_CVdict for Instance...
        """
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
        """
        #doc, especially the special values for some of these args
        """
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
        """
        Return the env to use for the arg (or kid?) at the given index (attr or argpos, I guess, for now #k).
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
        """
        #doc
        """
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
        """
        compute method for self.env_for_formulae -- memoized environment
        for use by our internal formulae (class-assigned exprs)
        """
        res = self.env.with_literal_lexmods( _self = self)
            # This used to be done (each time needed) in _e_compute_method and _i_env_ipath_for_formula_at_index --
            # doing it there was wrong since it sometimes did it after env mods by kluge070119 that needed to be done after it
            # (in order to mask its effect).
            # WARNING: doing it here creates a cyclic ref from self to self, since the result is memoized in self.
        return res

    def _i_grabarg_0( self, attr, argpos, dflt_expr, _arglist = False):
        """
        [private helper for _i_grabarg]
        return the pair (external-flag, expr to use for this arg)
        """
        # i think dflt_expr can be _E_REQUIRED_ARG_, or any (other) expr
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

    def _StateRef__attr_ref(self, attr): #bruce 070815 experimental
        """
        Return a stateref for our attr of the given name,
        or None if we can't do that.
        (#e option for error if we can't?)

        Part of an API for objects which can return StateRefs
        for some of their attrs. See StateRef_API for more info.
        """
        descriptor = getattr( self.__class__, attr, None)
        # for devel, assume it should work, fail if not. ###FIX or REDOC
        # print "got descriptor: %r" % (descriptor,)
        assert descriptor is not None
        ## assert isinstance( descriptor, ClassAttrSpecific_DataDescriptor ) ###k??? in fact assume it is a subclass which can do following:
        ## return None if following method is not there
        return descriptor._StateRef__your_attr_in_obj_ref( self)

    pass # end of class IorE_guest_mixin

# end
