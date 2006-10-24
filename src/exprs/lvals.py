'''
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
'''

###e Note: a few non-lval things in this file should probably be moved into a different file.

from basic import *

# ==

from changes import SelfUsageTrackingMixin, SubUsageTrackingMixin

# ==

class Lval(SelfUsageTrackingMixin, SubUsageTrackingMixin):
    """One invalidatable value of the most standard kind,
    containing its own fully bound compute method, passed to the constructor.
       Get the current value using .get_value() (this tells the dynenv that this value was used).
    Contains inval flag, subs to what it used to compute, recomputes as needed on access, propogates invals,
    all in standard ways. [#doc better]
    Change the compute method using .set_compute_method.
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
    valid = False
    # no need to have default values for _value, unless we add code to compare new values to old,
    # or for _compute_method, due to __init__
    def __init__(self, compute_method = None): #e rename compute_method -> recomputer?? prob not.
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
    def set_compute_method(self, compute_method): # might be untested since might not be presently used
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
            self._value = self._compute_value() # this catches exceptions in our compute_method
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
        assert self._compute_method is not None, "our compute_method is not yet set: %r" % self #e remove, as optim (redundant)
        match_checking_code = self.begin_tracking_usage()
        try:
            val = self._compute_method()
        except:
            print_compact_traceback("exception in _compute_value ignored: ")
            val = None
        self.end_tracking_usage( match_checking_code, self.inval )
            # that subscribes self.inval to lvals we used, and unsubs them before calling self.inval [###k verify that]
            #e optim (finalize) if set of used lvals is empty
            # (only if set_compute_method or direct inval won't be called; how do we know? we'd need client to "finalize" that for us.)
        # note: caller stores val and sets self.valid
        return val
    pass # end of class Lval

# ==

####@@@@

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

def LvalDict(wayfunc, lvalclass = Lval): #e option to not memoize for certain types of keys (like trivials or errors)?? this or Memo?
    """An extensible dict of lvals of the given lval class, whose memoized values will be recomputed from dict key using wayfunc(key)().
    It's an error (reported #nim in MemoDict) for computation of wk = wayfunc(key) to use any external usage-tracked lvalues,
    but it's ok if wk() does; subsequent inval of those lvals causes the lval created here to recompute and memoize wk() on demand.
    This is more useful than if the entire dict had to be recomputed (i.e. if a _C_ rule told how to recompute the whole thing),
    since only the specific items that become invalid need to be.
       Design note: DO WE RETURN THE LVALS or their values??
    For now, WE RETURN THE LVALS (partly since implem is easier, partly since it's more generally useful);
    this might be less convenient for the user.
    """
    #k Note:
    # I'm only 90% sure the "wayfunc = wayfunc, lvalclass = lvalclass" lambda closure kluge is still needed in Python, in this case.
    # I know it's needed in some cases, but maybe only when they are variables??
    # More likely, whenever the lambda is used outside their usual scope, as it is in this case.
    return MemoDict( lambda key, wayfunc = wayfunc, lvalclass = lvalclass:
                     lvalclass( wayfunc(key)) )

def LvalDict2(valfunc, lvalclass = Lval):
    """Like LvalDict but uses a different recompute-function API, which might be easier for most callers to supply;
    if it's always better, it'll replace LvalDict.
    In this variant, just pass valfunc, which will be applied to key in order to recompute the value at key.
    """
    return MemoDict( lambda key, valfunc = valfunc, lvalclass = lvalclass:
                     lvalclass( lambda valfunc=valfunc, key=key: valfunc(key)) )

# ==

class InvalidatableAttrsMixin(object): # object superclass is needed, to make this a new-style class, so a python property will work.
    ####@@@@ This class's behavior is likely to be merged into ExprsMeta.
    """Mixin class, for supporting "standard compute methods" in any client class.
    We support two kinds of compute methods:
    - _C_xxx methods, for recomputing values of individual attrs like self.xxx;
    - pairs of _CK_xxx and _CV_xxx methods, for recomputing the set of keys, and individual values, within dictlike attrs self.xxx.
    [Details to be explained. Features to be added: let client determine lval classes.]
    WARNING: entirely NIM or buggy as of 061020.
    """
    def __getattr__(self, attr):
        # return quickly for attrs that can't have compute rules
        if attr.startswith('__') or attr.startswith('_C'):
            raise AttributeError, attr # must be fast for __repr__, __eq__, __add__, etc
            # Notes:
            # - We only catch __xx here, not _xx, since _xx is permitted to have compute rules, e.g. _C__xx.
            #   Btw, __xx will only exist if it's really __xx__, since otherwise it would be name-mangled to _<classname>__xx.
            # - We exclude _Cxx so that no one tries to define a compute rule for a compute rule (hard to support, not very useful).

        # look for a compute method for attr, either _C_attr (used alone) or _CK_attr and/or _CV_attr (used together),
        # in self.__class__; if found, create and save a property in the class (so this only happens once per attr and class).
        # (#e should we grab the prefix out of the rule constructor, since it needs to know it anyway?)
        if _compile_compute_rule( self.__class__, attr, '_C_', _C_rule ) or \
           _compile_compute_rule( self.__class__, attr, '_CV_', _CV_rule ): # also incorporates _CK_ for same attr, if it exists
            # One of the above calls of _compile_compute_rule defined a property in self.__class__ for attr.
            # Use it now! [This will cause infrecur if the function said it's there and it's not! Fix sometime. #e]
            return getattr(self, attr)

        raise AttributeError, attr
    pass # end of class InvalidatableAttrsMixin

def _compile_compute_rule( clas, attr, prefix, propclass ):
    """[private helper function]
    Try to create a compute rule for accessing attr in clas (which needs to inherit from object for this to be possible),
    using a compute method named (prefix + attr) found in clas (if one is there).
       If you find that method, store a property (or similar object -- I forget the general name for them ###doc)
    implementing the compute rule in clas.attr, created by propclass(...), and return True. Otherwise return False.
    """
    assert isinstance( clas, object), "compute rules are only supported on new-style classes, not %r" % clas
    try:
        unbound_method = getattr( clas, prefix + attr)
    except AttributeError:
        return False
    assert callable(unbound_method), "prefix %r is reserved for use on compute methods, but .%s is not callable on %r" % \
           (prefix, prefix + attr, clas)
    prop = propclass( clas, attr, unbound_method, prefix ) # on error, this can raise an exception; or it can return None
    if prop is None:
        return False
    # assume prop is a suitable property object for use in a new-style class    
    setattr( clas, attr, prop)
    ###e improved design: propclass should instead be an object which can store a list of new properties (descriptors)
    # on a list of corresponding attrs;
    # that way it could know the prefixes itself, know how to look for the unbound methods,
    # and support the definition of more than one attr-descriptor, e.g. one for attr and one for associated values
    # like direct access to an LvalDict associated with a _CV_rule attr. When we need the latter, revise the design like that.
    return True

class _C_rule(object): ###e rename, since this is not a compute method? #e give it and _CV_rule a common superclass?
    "act like a property that implements a recompute rule using an Lval made from a _C_attr compute method"
    # note: the superclass "object" is required, for Python to recognize this as a descriptor.
    def __init__(self, clas, attr, unbound_method, prefix):
        assert prefix == '_C_' and unbound_method == getattr( clas, prefix + attr) # a sign of bad API design of _compile_compute_rule?
        #e store stuff
        self.attr = attr
        self.prefix = prefix
        return
    def __get__(self, instance, owner):
        if instance is None:
            # we're being accessed directly from clas
            return self
        # find the Lval object for our attr, which we store in instance.__dict__[attr]
        # (though in theory, we could store it anywhere, as long as we'd find a
        #  different one for each instance, and delete it when instance got deleted)
        attr = self.attr
        try:
            lval = instance.__dict__[attr]
        except KeyError:
            # make a new Lval object from the compute_method (happens once per attr per instance)
            mname = self.prefix + attr
            compute_method = getattr(instance, mname) # should always work
            # permit not only bound methods, but formulas on _self, or constants
            # (but formulas and constants will also be permitted directly on attr; see ExprsMeta for more info)
            compute_method = bound_compute_method_to_callable( compute_method,
                                                                 formula_symbols = (_self,),
                                                                 constants = True )
            lval = instance.__dict__[attr] = Lval(compute_method)
        return lval.get_value() # this does usage tracking, validation-checking, recompute if needed
            # Notes:
            # - There's a reference cycle between compute_method and instance, which is a memory leak.
            # This could be fixed by using a special Lval (stored in self, not instance, but with data stored in instance)
            # which we'd pass instance to on each use. (Or maybe a good solution is a C-coded metaclass, for making instance?)
            # - The __set__ below detects the error of the compute method setting the attr itself. Good enough for now.
            # Someday, if we use a special Lval object that is passed self and enough into to notice that itself,
            # then we could permit compute objects to do that, if desired. But the motivation to permit that is low.
            # - There is no provision for direct access to the Lval object (e.g. to directly call its .set_formula method).
            # We could add one if needed, but I don't know the best way. Maybe find this property (self) and use a get_lval method,
            # which is passed the instance? Or, setattr(instance, '_lval_' + attr, lval).
    def __set__(self, instance, val):
        # Note: the existence of this method means that this descriptor is recognized by Python as a "data descriptor",
        # and it overrides instance.__dict__ (that is, it's used for get, set, or del, even if instance.__dict__ contains a value).
        #k Q: can instance be None here??
        assert 0, "not allowed to set attr %r in %r" % (self.attr, instance)
    #e could make __delete__ do an inval... should we?? ###
    pass # end of class _C_rule

class _CV_rule(object):
    """Act like a property that implements a per-item recompute rule for a dictlike object
    stored at instance.attr, using an LvalDict made from a _CV_attr compute method for item values,
    and an optional _CK_attr compute method for the complete list of keys.
       If the _CK_attr method is not present, the set of keys is undefined and the dictlike object
    (value of instance.attr) will not support iteration over keys, items, or values.
       Whether or not iteration is supported, direct access to the LvalDict is provided [how? ###e, nim],
    which makes it possible to iterate over the dict items created so far.
    """
    def __init__(self, clas, attr, unbound_method, prefix):
        assert prefix == '_CV_' and unbound_method == getattr( clas, prefixV + attr)
        self.attr = attr
        self.prefixV = prefix
        self.prefixK = '_CK_'
        self.has_CK = not not getattr( clas, prefixK + attr, False)
        return
    def __get__(self, instance, owner):
        if instance is None:
            # we're being accessed directly from class
            return self
        # find the RecomputableDict object for our attr in instance
        attr = self.attr
        try:
            obj = instance.__dict__[attr]
            print "warning: obj was not found directly, but it should have been, since this is a non-data descriptor", self #e more?
        except KeyError:
            # make a new object from the compute_methods (happens once per attr per instance) 
            compute_methodV = getattr(instance, self.prefixV + attr) # should always work
            compute_methodV = bound_compute_method_to_callable( compute_methodV,
                                                                  formula_symbols = (_self, _i), ###IMPLEM _i
                                                                  constants = True )
                # also permit formulas in _self and _i, or constants (either will be converted to a callable)
            assert callable(compute_methodV)
            compute_methodK = getattr(instance, self.prefixK + attr, None)
                # optional method or formula or constant (None can mean missing, since legal constant values are sequences)
            if compute_methodK is not None:
                compute_methodK = bound_compute_method_to_callable( compute_methodK,
                                                                    formula_symbols = (_self,),
                                                                    constants = True )
                assert callable(compute_methodK)
            obj = instance.__dict__[attr] = RecomputableDict(compute_methodV, compute_methodK)
        return obj
    # Note: we have no __set__ method, so in theory (since Python will recognize us as a non-data descriptor),
    # once we've stored obj in instance.__dict__ above, it will be gotten directly
    # without going through __get__. We print a warning above if that fails.

    # Note: similar comments about memory leaks apply, as for _C_rule.
    
    pass # end of class _CV_rule

class DictFromKeysAndFunction(InvalidatableAttrsMixin): #e refile in py_utils? not sure -- recursive import problem re superclass?
    """Act like a read-only dict with a fixed set of keys (computed from a supplied function when first needed;
    if that func is not supplied, all keys are permitted and iteration over this dict is not supported),
    and with all values computed by another supplied function (not necessarily constant, thus not cached).
    """
    def __init__(self, compute_value_at_key, compute_key_sequence = None, validate_keys = False):
        self.compute_value_at_key = compute_value_at_key
        self.compute_key_sequence = compute_key_sequence # warning: might be None
        self.validate_keys = validate_keys
    def _C_key_sequence(self):
        # called at most once, when self.key_sequence is first accessed
        assert self.compute_key_sequence, "iteration not supported in %r, since compute_key_sequence was not supplied" % self
        return self.compute_key_sequence()
    def _C_key_set(self):
        return dict([(key,key) for key in self.key_sequence])
    def __getitem__(self, key):
        if self.validate_keys: #e [if this is usually False, it'd be possible to optim by skipping this check somehow]
            if not key in self.key_set:
                raise KeyError, key
        return self.compute_value_at_key(key) # not cached in self
    # dict methods, only supported when compute_key_sequence was supplied
    def keys(self):
        "note: unlike for an ordinary dict, this is ordered, if compute_key_sequence retval is ordered"
        return self.key_sequence
    iterkeys = keys
    def values(self):
        "note: unlike for an ordinary dict, this is ordered, if compute_key_sequence retval is ordered"
        compval = self.compute_value_at_key
        return map( compval, self.key_sequence )
    itervalues = values
    def items(self):
        "note: unlike for an ordinary dict, this is ordered, if compute_key_sequence retval is ordered"
        compval = self.compute_value_at_key
        return [(key, compval(key)) for key in self.key_sequence]
    iteritems = items
    pass # end of class DictFromKeysAndFunction

from idlelib.Delegator import Delegator

class RecomputableDict(Delegator):
    """Act like a read-only dict with variable (invalidatable/recomputable) values,
    and a fixed key sequence used only to support iteration
    (with iteration not supported if the key sequence compute function is not supplied).
       If validate_keys is True, every __getitem__ verifies the supplied key is in the specified key sequence.
       #e Someday, self.lvaldict might be a public attr -- not sure if this is needed;
    main use is "iterate over values defined so far".
    """
    def __init__(self, compute_methodV, compute_methodK = None, validate_keys = False):
        self.lvaldict = LvalDict2(compute_methodV)
        Delegator.__init__( self, DictFromKeysAndFunction( self.compute_value_at_key, compute_methodK, validate_keys = validate_keys))
        return
    def compute_value_at_key(self, key):
        return self.lvaldict[key].get_value()
    pass
        
# end
