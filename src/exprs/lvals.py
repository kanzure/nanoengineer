from basic import * # autoreload of basic is done before we're imported


# Lval(formula) -> standard lval for that formula, has .value, maybe has .set_formula, does inval flag/subs/propogate, tracks own usage
# may just do this by having a single attr .value that works like any standard invalidatable attr, plus set_formula used indirectly

class Lval:
    valid = False
    def __init__(self, formula = None):
        """For now, formula is either None (meaning no formula is set yet -- error to use),
        or any callable [?? or thing taking compute_value method?? ####]
        which does usage-tracking of whatever it uses into its dynenv in the standard way,
        and returns its value (perhaps None or another callable, treated as any other value).
        Note that unlike InvalMixin _recompute_ methods, it can't work by setting the value instead.
           In future, other special kinds of formulas might be permitted, and used differently.
           [WARNING: if we try to generalize by letting formula be a python value used as a constant,
        we'll have an ambiguity if that value happens to be callable, so we'd need a ConstantFormula constructor instead --
        or fix this by not passing a callable, but a Formula object with a compute_value method,
        and having a way to make one of those from a callable, when desired, and change the client call of Lval(compute_method). ###e]
        """
        self._usage_record = {} # or use begin_tracking_usage??
        self.set_formula(formula)
    def set_formula(self, formula):
        self._formula = formula
        self.inval() ###e only if different??
    def inval(self):
        if self.valid:
            self.valid = False
            ###e then propogate, but only if we were valid before this, I think
    def get_value(self):
        if not self.valid:
            self._value = self._C_value()
            self.valid = True
        ###e do standard usage tracking into env -- compatible with env.prefs (i forget if i have to bugfix that)
        return self._value
    def _C_value(self):
        """compute our value, tracking what it uses, subscribing our inval method to that.
        NOTE: does not yet handle diffing of prior values of what was used, or the "tracking in order" needed for that.
        Maybe a sister class (another kind of Lval) will do that.
        """
        #e handle various kinds of formulas, or objs that should be coerced into them -- make_formula(formula_arg)?
        assert self._formula is not None, "our formula is not yet set: %r" % self
        self._usage_record.clear() #k needed?
        val = self._formula.get_value( self._usage_record) ###e who checks for exceptions in this, it or us? it does.
        ###@@@e subscribe self.inval to members of self._usage_record
        #e optim (finalize) if that's empty (only if set_formula or direct inval won't be called; how do we know?)
        return val
    pass

class InvalidatableAttrsMixin(object): # object superclass is needed, to make this a new-style class, so a python property will work.
    """Mixin class, for supporting "standard compute methods" in any client class.
    We support two kinds of compute methods:
    - _C_xxx methods, for recomputing values of individual attrs like self.xxx;
    - pairs of _CK_xxx and _CV_xxx methods, for recomputing the set of keys, and individual values, within dictlike attrs self.xxx.
    [Details to be explained. Features to be added: let client determine lval classes.]
    WARNING: entirely NIM or buggy as of 061020.
    """
    # totally nim: '_CK_' '_CV_' ###@@@
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
    return True

class _C_rule(object):
    "act like a property that implements a recompute rule using a _C_attr compute method"
    def __init__(self, clas, attr, unbound_method, prefix):
        assert prefix == '_C_' and unbound_method == getattr( clas, prefix + attr) # a sign of bad API design of _compile_compute_rule?
        #e store stuff
        self.attr = attr

        ### PROBLEM: we need to create one Lval object per instance!!! #####@@@@@@ so below is WRONG.

        
        # create lval object, passing our compute method as its formula.
        # (MEMORY LEAK: circular ref to self via bound method compute_method;
        #  someday might not be needed, if getter could pass it;
        #  maybe easiest fast solution is a C-coded metaclass;
        #  alternatively, this __getattr__ could serve as the getter,
        #  and pass the compute method each time, memoizing only the lval's usage & invalsubs records. ###e)
        self.lval = Lval(FormulaFromCallable(compute_method))
        return
    def __get__(self, instance, owner):
        if instance is None:
            # we're being accessed directly from class
            return self
        ###e do usage tracking -- or is there an Lval object to do this for us? yes, that's what we want... ###@@@
        ###e recompute value if it's invalid
        ###e after compute method runs, check if it did its own setattr -- we might even be able to make that work!
        # but, would it call __set__ below? I think so! So at least, the __set__ below detects that error. Good for now.
        return self.value
    def __set__(self, instance, val):
        #e can instance be None here??
        assert 0, "not allowed to set attr %r in %r" % (self.attr, instance)
    #e could make __delete__ do an inval... should we?? ###
    pass
        
        
    # return property(fget, fset, fdel, doc)

    




    # use it for the first time -- is this ok, before we've set up the getter, etc?
    # doing this now makes it easier to detect an error below.
    val = lval.get_value() # this causes client code to track usage of this lval's value, and lval to track usage within its formula
    assert not self.__dict__.has_key('attr'), "error: compute method for %r apparently stored a direct value in %r" % (attr, self)
        # this would be an error any time we call compute_method, but it's only convenient to test for it the first time, but that's usually enough

    # store lval for direct access (usually never needed)
    assert not hasattr(self, '_lval_' + attr)
    setattr(self, '_lval_' + attr, lval)
    
    # create getter property which accesses lval
    getter_property = property(lval.get_value)
        #e could the lval itself serve in this role? not a good idea, probably, re direct access to lval.
        # property(getter, setter, deler, doc) -- later might want to make del act like inval??
    setattr(self, attr, getter_property)
    assert nim, "the above won't work, see comment at top of func"#061020 ####@@@@
    # no need to use it yet, since we have val
    return val
    pass

        ###e unlike InvalMixin, this method is not allowed to directly set the attr, or other attrs! Can we detect that error? ###
        # we'd have to check each time (or, first time, maybe good enough).
        # reason: we can't let the attr val be stored directly, since we have to track all uses of it and alert dynenv to them,
        # pointing it to us (the lval) so it can subscribe to our invals. This is another reason for a definite lval object.


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
    return MemoDict( lambda key, wayfunc = wayfunc, lvalclass = lvalclass: lvalclass( FormulaFromCallable( wayfunc(key))) )

# end
