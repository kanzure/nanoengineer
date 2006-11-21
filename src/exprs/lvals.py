"""
lvals.py - various kinds of "lvalue" objects (slots for holding attribute values)
with special behavior such as usage-tracking and invalidation/update.

$Id$

===

Ways in which lval classes need to differ from each other:

- how the value they represent is "delivered" (on request of a caller, calling a get_value method or the like):

  - (e.g. as a return value, or as an externally stored value, or as side effects)

  - (e.g. with or without a version-counter)

- how the fact of their value's usage is recorded in the dynamic environment, and what kind of usage is recorded

  - kinds of usage:
    calls of display lists,
    uses of other external objects (qt widgets, opengl state),
    uses of ordinary usage-tracked variables

  (but if dynamic env wants to record usage in order of occurrence, I think it can do that without affecting the track_use API)

- how the decision of what needs recomputing is made

  - e.g. what kinds of inval flags, whether to diff input values before deciding, whether to do partial or incremental recomputes

- with what API the recomputing is accomplished (e.g. call a supplied function, perhaps with certain args)

- how invals of the current value can/should be propogated to previous users of the current value

Other differences, that should *not* be reflected directly in lval classes
(but that might have specific helper functions in this module):

- the specific formula being recomputed (whether expressed a python compute method, an interpreted HL math expr, or a draw method)

- whether some of the storage implied above (eg value caches, usage lists and their subs records, inval flags and their user lists)
  is stored separately from formula instances (to permit sharing of formulas) --
  because if it is, then just make an lval class that calls a different kind of formula (passing it more args when it runs),
  but let the lval class itself be per-storage-instance

- whether the lvalues reside in a single object-attr, or a dict of them -- just make an attr or dict of lvals,
  and have the owning class access them differently.

For examples, see the classes herein whose names contain Lval.
"""

# WARNING: the code in here needs to be safe for use in implementing ExprsMeta, which means it should not depend
# on using that as a metaclass.

# == imports

# from modules in cad/src

from changes import SelfUsageTrackingMixin, SubUsageTrackingMixin

# from this exprs package

from basic import *

MemoDict # comes from py_utils via basic; very simple, safe for use in ExprsMeta [061024]

class LvalError_ValueIsUnset(AttributeError): #061117 1030p not yet raised or caught in all places where it ought to be #####e
    """Exception for an lval whose value was never set (nor was a compute method or initval method set).
    This acts like AttributeError so (I hope) hasattr will treat it as an attr not being there.
    But it's our own subclass so we can catch it without catching other AttributeErrors caused by our own code's bugs.
    """
    pass

# ==

class Lval(SelfUsageTrackingMixin, SubUsageTrackingMixin):
    """One invalidatable value of the most standard kind,
    containing its own fully bound compute method, passed to the constructor.
       Get the current value using .get_value() (this tells the dynenv that this value was used).
    Contains inval flag, subs to what it used to compute, recomputes as needed on access, propogates invals,
    all in standard ways. [#doc better]
       Change the compute method using .set_compute_method,
    or (use our subclass which permits you to) set new constant values using set_constant_value.
    """
    # Implem notes:
    #
    # - This object can't be a Python descriptor (in a useful way), because its storage has to be per-instance.
    #   [I suppose we could separate it from its storage, and then that might not be true.
    #    But it's simpler this way, especially since we sometimes store one in a visibly-indexed dict rather than an object-attr.]
    # - If a descriptor (which has to be per-class) uses one of these, it has to look up the one to use in each instance.
    #   So the only reason not to provide this Lval with a bound recompute method would be to avoid cyclic references.
    #   At the moment, that's not crucial.
    # - When we want that, this still has the storage, but it can be given an owner obj each time it runs.
    #   It could just as well be given the compute method each time; for either one, the owner has to give the same one each time
    #   or the inval flag etc won't be correct.
    # - The compute method it's given (once or each time) could be a bound instance method (from a _C_attr method),
    #   or something created from a formula on _self, also bound to a value for _self. Whatever it is, we don't care how it's made,
    #   so we might as well accept any callable. It might be made in various ways, by descriptors or helper functions like LvalDict.
    #
    # - The mixins provide these methods, for internal use:
    #   - SelfUsageTrackingMixin: track_use, track_change == track_inval --
    #       for tracking how our value is used, is changed, is indirectly invalled.
    #   - SubUsageTrackingMixin: begin_tracking_usage, end_tracking_usage -- for tracking which values we use when we recompute.
    #   - They're the same mixins used for displists used by chunk/GLPane and defined in chunk, and for changes to env.prefs, 
    #     so these Lvals will work with those (except for chunk not yet propogating invals or tracking changes to its display list).
    #   - See comments near those methods in changes.py for ways they'll someday need extension/optimization for this use.
    valid = False # public attribute
    # no need to have default values for _value, unless we add code to compare new values to old,
    # or for _compute_method, due to __init__
    def __init__(self, compute_method = None, debug_name = None): #e rename compute_method -> recomputer?? prob not.
        """For now, compute_method is either None (meaning no compute_method is set yet -- error to try to use it until it's set),
        or any callable which computes a value when called with no args,
        which does usage-tracking of whatever it uses into its dynenv in the standard way
        (which depends mainly on what the callable uses, rather than on how the callable itself is constructed),
        and which returns its computed value (perhaps None or another callable, treated as any other value).
        Note that unlike the old InvalMixin's _recompute_ methods, compute_method is not allowed to use setattr
        (like the one we plan to imitate for it) instead of returning a value. (The error of it doing that is detected. ###k verify)
           In future, other special kinds of compute_methods might be permitted, and used differently,
        but for now, we assume that the caller will convert whatever it has into this simple kind of compute_method.
           [Note: if we try to generalize by letting compute_method be a python value used as a constant,
        we'll have an ambiguity if that value happens to be callable, so it's better to just make clients pass lambda:val instead.]
        """
        ## optim of self.set_compute_method( compute_method), only ok in __init__:
        self._compute_method = compute_method
        self.debug_name = debug_name #061119
        ## if platform.atom_debug and not debug_name:
            #e can we use a scheme sort of like print_compact_stack to guess the object that is creating us,
            # since it'll have a localvar called self? I doubt it, since some helper objs are likely to be doing the work.
            # So just do the work myself of passing this in intelligently...
        return
    def __repr__(self): #061119
        return "<%s%s at %#x>" % (self.__class__.__name__, self.debug_name and ("(%s)" % self.debug_name) or '', id(self))
    def set_compute_method(self, compute_method):
        "#doc"
        # notes:
        # - this might be untested, since it might not be presently used
        # - note the different behavior of set_constant_value (in a variant subclass) -- it's not equivalent to using this method
        #   on a constant function, but is closer (or equiv?) to doing that and then immediately evaluating
        #   that new compute method. (It also diffs the values as opposed to the compute methods.)
        # - BUG: for this to be correct, we should also discard our usage-subscriptions stemming from the eval
        #   of the prior compute method. Not doing this might be a severe performance hit or even a bug.
        #   But it's not easy to do. Since this is never called, that's nim for now.
        assert 0, "if you call this, you better first implement discarding the prior usage-subscriptions"
            #e or modify this assert to not complain if there are none of them (eg if there is no prior compute method, or we're valid)
        old = self._compute_method
        self._compute_method = compute_method # always, even if equal, since different objects
        if old != compute_method:
            self.inval()
    def inval(self):
        """This can be called by the client, and is also subscribed internally to all invalidatable/usage-tracked lvalues
        we use to recompute our value (often not the same set of lvals each time, btw).
           Advise us (and whoever used our value) that our value might be different if it was recomputed now.
        Repeated redundant calls are ok, and are optimized to avoid redundantly advising whoever used our value
        about its invalidation.
           Note that this does not recompute the value, and it might even be called at a time
        when recomputing the value would be illegal. Therefore, users of the value should not (in general)
        recompute it in their own inval routines, but only when something next needs it. (This principle is not currently
        obeyed by the Formula object in changes.py. That object should probably be fixed (to register itself for
        a recompute later in the same user event handler) or deprecated. ###e)
        """
        if self.valid:
            self.valid = False
            # propogate inval to whoever used our value
            self.track_inval() # (defined in SelfUsageTrackingMixin)
    def get_value(self):
        """This is the only public method for getting the current value;
        it always usage-tracks the access, and recomputes the value if necessary.
        """
        if not self.valid:
            try:
                self._value = self._compute_value()
                    # this USED TO catch exceptions in our compute_method; as of 061118 it reraises them
            except:
                printnim("I need to figure out what usage to track, in what object, when a tracked attr is unset")
                pass ## self.track_use()
                    ### GUESS 061120 1112a: this track_use causes the duplicate track_inval bug, because we track when invalid.
                    # and (still guessing) we do this during hasattr seeing our value is unset. it's probably wrong, because when the
                    # val becomes set, why should something be invalled, unless it turned exception into a real value?
                    # what might be right is to merge all the usage at this point into whatever caller turns the exception
                    # into a real value, rather than just discarding it.
                    # surely we don't want to include it here, not only this one, but whatever was used before... but what
                    # do i mean by "here"? The real error is not in our mentioning the use here, i think, but in what
                    # the caller does with it... otoh our complaint stems entirely from what happens here, so that's wrong.
                    # I don't understand this well yet, but let's see what happens if I comment that out.
                raise
            self.valid = True
        # do standard usage tracking into env (whether or not it was invalid & recomputed) -- API is compatible with env.prefs
        # [do it after recomputing, in case the tracking wants to record _value immediately(?)]
        self.track_use() # (defined in SelfUsageTrackingMixin) ###e note: this will need optimization
        return self._value
    def _compute_value(self):
        """[private]
        Compute (or recompute) our value, using our compute_method but protecting ourselves from exceptions in it,
        tracking what it uses, subscribing our inval method to that.
        NOTE: does not yet handle diffing of prior values of what was used, or the "tracking in order of use" needed for that.
        Maybe a sister class (another kind of Lval) will do that.
        """
        #e future: _compute_value might also:
        # - do layer-prep things, like propogating inval signals from changedicts
        # - diff old & new
        if self._compute_method is None:
            raise LvalError_ValueIsUnset, "our compute_method is not yet set: %r" % self
                #k note: this is a subclass of AttributeError so hasattr can work in this case [061117 late]
        match_checking_code = self.begin_tracking_usage()
        try:
            val = self._compute_method() ###e should certain exceptions inside here raise AttributeError, for us to catch & reraise,
                # if val is legitimately not yet set? no - raise our own kind of exception, so bug doesn't act like it,
                # then catch that & convert to attrerror to reraise. #### SHOULD DOIT 061117 1022p [one place where i am]
            printnim("catch that & convert to attrerror...")#### here & above assert
        except LvalError_ValueIsUnset:
            # might happen from some lower layer if we're virtual (e.g. if our value is stored in some external array or dict)
            ## print "doing end_tracking_usage before reraising LvalError_ValueIsUnset [ok??]" # sometimes we get some subslist exception
                ######k TOTAL GUESS that it's fully legit, 061118 156p [but without it we got missing end-tracks, naturally]
                # note: should we set val to None and say it's valid? NO -- then of two hasattrs in a row, 2nd would be wrong.
                # 061121: seems ok, always happens whether or not bugs do, so stop printing it.
            self.end_tracking_usage( match_checking_code, self.inval )
            raise
        except:
            print_compact_traceback("exception in %r._compute_method NO LONGER ignored: " % self)
                ###e 061118 we still need to print more info from this; what to do to explain errors deep in evaling some expr?
                # catch them and turn them into std custom exceptions, then wrap with posn/val info on each step of going up? (maybe)
            val = None
##            if 0:
##                print_compact_stack("exiting right after lval exception, to see if it makes my errors more readable, from here: ",
##                                    ## frame_repr = lambda frame: " %s" % (frame.f_locals.keys(),),
##                                    frame_repr = _std_frame_repr,
##                                    linesep = '\n')
##                    ###k 061105; review; 061117 printfyi -> print_compact_stack
##                #e it would be nice to print self's formula (if it has one in the compute method), attr, etc,
##                # but we don't have good access to that info
##                ## import sys
##                ## sys.exit(1) # doesn't work, just raises SystemExit which gets caught in the same way (tho not infrecur):
##                import sys
##                sys.stderr.flush() #k prob not needed
##                sys.stdout.flush() #k prob needed
##                import os
##                os._exit(1) # from python doc for built-in exceptions, SystemExit
            if 1:
                ## print "doing end_tracking_usage before reraising some misc exception [ok??]" # seems to be ok when it occurs
                self.end_tracking_usage( match_checking_code, self.inval )
                raise
        self.end_tracking_usage( match_checking_code, self.inval )
            # that subscribes self.inval to lvals we used, and unsubs them before calling self.inval [###k verify that]
            #e optim (finalize) if set of used lvals is empty
            # (only if set_compute_method or direct inval won't be called; how do we know? we'd need client to "finalize" that for us.)
        # note: caller stores val and sets self.valid
        return val
    def can_get_value(self):
        """Ignoring the possibility of errors in any compute method we may have, can our get_value be expected to work right now?
        [WARNING: This also doesn't take into account the possibility (not an error) of the compute method raising
        LvalError_ValueIsUnset; this might happen if we're a virtual lval providing access to a real one known to the compute_method.
        If this matters, the only good test (at present) is to try the compute_method and see if it raises that exception.]
        """
        return self.valid or (self._compute_method is not None)
    def have_already_computed_value(self):
        return self.valid # even tho it's a public attr
    pass # end of class Lval

def _std_frame_repr(frame): #e refile into debug.py? warning: dup code with lvals.py and [g4?] changes.py
    "return a string for use in print_compact_stack"
    # older eg: frame_repr = lambda frame: " %s" % (frame.f_locals.keys(),), linesep = '\n'
    locals = frame.f_locals
    dfr = locals.get('__debug_frame_repr__')
    if dfr:
        return ' ' + dfr(locals)
    co_name = frame.f_code.co_name
    res = ' ' + co_name
    self = locals.get('self')
    if self is not None:
        res +=', self = %r' % (self,)
    return res
    # locals.keys() ##e sorted? limit to 25? include funcname of code object? (f_name?)
    # note: an example of dir(frame) is:
    ['__class__', '__delattr__', '__doc__', '__getattribute__', '__hash__',
    '__init__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
    '__setattr__', '__str__', 'f_back', 'f_builtins', 'f_code',
    'f_exc_traceback', 'f_exc_type', 'f_exc_value', 'f_globals', 'f_lasti',
    'f_lineno', 'f_locals', 'f_restricted', 'f_trace']
    # and of dir(frame.f_code) is:
    ['__class__', '__cmp__', '__delattr__', '__doc__', '__getattribute__',
    '__hash__', '__init__', '__new__', '__reduce__', '__reduce_ex__',
    '__repr__', '__setattr__', '__str__', 'co_argcount', 'co_cellvars',
    'co_code', 'co_consts', 'co_filename', 'co_firstlineno', 'co_flags',
    'co_freevars', 'co_lnotab', 'co_name', 'co_names', 'co_nlocals',
    'co_stacksize', 'co_varnames']

def call_but_discard_tracked_usage(compute_method): #061117
    "#doc [see obs func eval_and_discard_tracked_usage for a docstring to cannibalize]"
    lval = Lval(compute_method) # lval's only purpose is to discard the tracked usage that is done by compute_method()
    res = lval.get_value() # this calls compute_method()
    #e destroy lval? #e future: option to tell caller whether or not we tracked any usage??
    return res

def make_compute_method_discard_usage_if_ever_called(compute_method): #061117
    "change a compute_method into one which discards its tracked usage if it's ever called (but don't call it now!)"
    return lambda _guard = None, compute_method = compute_method: call_but_discard_tracked_usage(compute_method) #e and assert not _guard

class LvalForState(Lval): #061117 -- NOT REVIEWED AS WELL AS I'D LIKE (esp since split out from its superclass, and initvals enabled)
    """A variant of Lval for containing mutable state.
    Can be given an initval compute method -- but that's required
    if and only if the first get comes before the first set;
    it's computed at most once, at the moment it's needed (even if it has a time-varying value).
    """
    # This differs from Lval because it has to discard tracked usage from its compute_method,
    # which it uses only to initialize its value in the event it's gotten-from before being set.
    # That's a semantic difference which invites bugs unless we make it a different class.
    #
    #e optim note: we could specialize _compute_value to not bother doing usage tracking.
    def __init__(self, initval_compute_method = None, debug_name = None):
        # make sure our initval compute method will discard usage it tracks, so we'll call it at most once
        # (only if and when we're gotten-from before we're first set)
        if initval_compute_method is not None:
            compute_method = make_compute_method_discard_usage_if_ever_called( initval_compute_method)
        else:
            compute_method = None
        Lval.__init__(self, compute_method = compute_method, debug_name = debug_name)
    def set_compute_method(self, compute_method):
        assert 0, "not supported in this class" #e i.e., Lval and this class should really inherit from a common abstract class
    def set_constant_value(self, val): #061117, for use in staterefs.py
        """#doc [for now, using this is strictly an alternative to using compute_methods --
        correctness of mixing them in one lval is not reviewed, and seems unlikely,
        with one exception: an initial compute_method can be provided for computing an initial value
        in case the value is asked for before being set, BUT IT'S AN ERROR IF THAT TRACKS ANY USAGE.
        So we enforce this by being in a variant subclass of Lval.]
        """
        if self.valid and self._value == val:
            pass # important optim, but in future, we might want to only sometimes do this
                 # (eg have another variant class which doesn't do it)
        else:
            self._value = val
                # do this first, in case an outsider (violating conventions? At least for Lval, maybe not for us)
                # happens to notice self.valid being true during track_inval, so they won't be misled by an incorrect self._value
            if self.valid:
                self.track_inval() # (defined in SelfUsageTrackingMixin)
                    # WARNING: self.valid is True for us during our call of track_inval,
                    # but is False for Lval's call of it.
                    # For our call, we only need to propogate invals if we were valid
                    # (since if not, we propogated them when we became invalid, or
                    #  (more likely, assuming we're not mixing this with compute methods) [###k review re initial value compmethod]
                    #  we were never valid); but during that propogation, we'll remain valid
                    # and have our new value available (permitting queries of it during inval propogation,
                    # though that violates the convention used for the compute_method style).
                    # [#e BTW isn't track_inval misnamed, since it's really to propogate or report our inval, not to track it?]
            else:
                self.valid = True
            pass
        return
    #k I think can_get_value and have_already_computed_value are correct for us as defined in the superclass Lval.
    pass # end of class LvalForState

# ==

###@@@

class LvalForDrawingCode(Lval): #stub -- do we need this, or just pass an appropriate lambda to Lval? ##e
    """[deal with get_value returning side effects? or using .draw instead -- just internally?]
    """
    pass

class LvalForUsingASharedFormula(Lval): #stub -- do we need this? for a formula on _self shared among several instances
    """[pass _self to _compute_value?]
    """
    pass

## class LvalForDisplistEffects -- see DisplistChunk.py

# ==

def LvalDict1(wayfunc, lvalclass = Lval): #e option to not memoize for certain types of keys (like trivials or errors)?? this or Memo?
    """An extensible dict of lvals of the given lval class, whose memoized values will be recomputed from dict key using wayfunc(key)().
    It's an error (reported [#nim] in MemoDict) for computation of wk = wayfunc(key) to use any external usage-tracked lvalues,
    but it's ok if wk() does; subsequent inval of those lvals causes the lval created here to recompute and memoize wk() on demand.
    This is more useful than if the entire dict had to be recomputed (i.e. if a _C_ rule told how to recompute the whole thing),
    since only the specific items that become invalid need to be recomputed.
       Design note: DO WE RETURN THE LVALS or their values??
    For now, WE RETURN THE LVALS (partly since implem is easier, partly since it's more generally useful);
    this might be less convenient for the user. [But as of 061117, staterefs.py will depend on this, in our variant LvalDict2.]
    """
    #k Note:
    # I'm only 90% sure the "wayfunc = wayfunc, lvalclass = lvalclass" lambda closure kluge is still needed in Python, in this case.
    # I know it's needed in some cases, but maybe only when they are variables??
    # More likely, whenever the lambda is used outside their usual scope, as it is in this case.
    return MemoDict( lambda key, wayfunc = wayfunc, lvalclass = lvalclass:
                     lvalclass( wayfunc(key)) )

def LvalDict2(valfunc, lvalclass = Lval, debug_name = None):
    """Like LvalDict1 but uses a different recompute-function API, which might be easier for most callers to supply;
    if it's always better, it'll replace LvalDict1. [not sure yet -- that has one semiobs use with a comment saying to try 2 instead]
    In this variant, just pass valfunc, which will be applied to key in order to recompute the value at key.
    """
    return MemoDict( lambda key, valfunc = valfunc, lvalclass = lvalclass, debug_name = debug_name:
                     lvalclass( lambda valfunc=valfunc, key=key: valfunc(key),
                                debug_name = debug_name and ("%s|%s" % (debug_name,key)) ) )
        
# end
