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

class InvalidatableAttrsMixin: ### (object) needed, for property to work??
    "cause _C_xxx methods to work, in client class, using class Lval"
    def __getattr__(self, attr):
        # return quickly for __repr__, __eq__, __add__, etc
        if attr.startswith('_'):
            raise AttributeError, attr # must be fast ##e could use endswith if we also want to handle e.g. _lvaldict_...

        # look for _C_ (aka or formerly, _compute_) method
        try:
            compute_method = getattr(self, '_C_' + attr)
            ###e unlike InvalMixin, this method is not allowed to directly set the attr, or other attrs! Can we detect that error? ###
            # we'd have to check each time (or, first time, maybe good enough).
            # reason: we can't let the attr val be stored directly, since we have to track all uses of it and alert dynenv to them,
            # pointing it to us (the lval) so it can subscribe to our invals. This is another reason for a definite lval object.
        except AttributeError:
            #e also check for _get_ method? maybe not needed, just have client use getters instead?
            raise AttributeError, attr
        
        # create lval object, passing our compute method as its formula.
        # (MEMORY LEAK: circular ref to self via bound method compute_method;
        #  someday might not be needed, if getter could pass it;
        #  maybe easiest fast solution is a C-coded metaclass;
        #  alternatively, this __getattr__ could serve as the getter,
        #  and pass the compute method each time, memoizing only the lval's usage & invalsubs records. ###e)
        lval = Lval(FormulaFromCallable(compute_method))

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

        # no need to use it yet, since we have val
        return val
    pass

# ==

def LvalDict(wayfunc, lvalclass = Lval): #e option to not memoize for certain types of keys (like trivials or errors)?? this or Memo?
    """Act like a dict of lvals of the given class, whose values are recomputed from dict key using wayfunc(key)(),
    which CAN use usage-tracked things;
    if it does, their invalidation will cause specific lvals in this dict to become invalid (so they'll be recomputed when next needed).
       Design note: DO WE RETURN THE LVALS or their values??
    For now, WE RETURN THE LVALS (partly since implem is easier, partly since it's more generally useful);
    this might be less convenient for the user.
    """
    return MemoDict( lambda key: lvalclass( FormulaFromCallable( wayfunc(key) )))

# end
