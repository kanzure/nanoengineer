
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
$Id$


this file won't be in cvs for long -- but it might be there temporarily, since it's not yet fully cannibalized

        #####@@@@@ need to decide whether we or the formula should do usage tracking and subscribe self.inval to what we use.
            # to decide -- what kinds of formulas can be ortho to kinds of invalidatable lvalues?
            # do we memo in formula or here? who decides? do we own formula? what does it have, other than ability to recompute?
            # how often is it made by FormulaFromCallable -- always? yes, ie in both _C_rule and _CV_rule (using LvalDict 1 or 2).
            # - The differentest kind of lval is the one for displists; it represents a pair of virtual values, the displist direct
            # contents and the effect of calling it (only the latter includes sublist effects), both represented by version numbers
            # which is what "diff old and new" would use. Instead of get_value we have emit_value i.e. draw. For inval propogation
            # it needs to separate the two virtual values. Maybe it could use two Lval objects.... [latest code for it is in NewInval.py]
            #   - It has to work with draw methods, which also emit side effects, have version numbers... do they, too,
            # distinguish between two virtual values, what OpenGL they emit vs what that will do when it runs??
            # - The other big issue is formulas with no storage of their own, and not owned. (E.g. those coded using _self.)
            #   - The biggest change in that is wanting to call its compute method with an arg, for use in grabbing attrs when evalling
            #     and for knowing where to store usage (tho latter could be in dynenv in usual way, and should be).
            # - Note that what I often call a formula is just an expr, and a formula instance is an expr instance, class InstanceOrExpr,
            # even if it's an OpExpr. That thing has its own memo, implemented by this class Lval. So all it provides us is a
            # compute method. This is suggesting that our _formula should be merely a compute method. Does that fit in displist case??
            #
            # ###

# ==

 some of the following will still be rewritten and used in ExprsMeta, i think


class InvalidatableAttrsMixin(object): # object superclass is needed, to make this a new-style class, so a python property will work.
    ####@@@@ This class's behavior is likely to be merged into ExprsMeta.
    """Mixin class, for supporting "standard compute methods" in any client class.
    We support two kinds of compute methods:
    - _C_xxx methods, for recomputing values of individual attrs like self.xxx;
    - pairs of _CK_xxx and _CV_xxx methods, for recomputing the set of keys, and individual values, within dictlike attrs self.xxx.
    [Details to be explained. Features to be added: let client determine lval classes.]
    WARNING: entirely NIM or buggy as of 061020.
    """
    def __getattr__(self, attr): # in class InvalidatableAttrsMixin
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

###
stuff after this is almost fully in ExprsMeta now, except maybe that big docstring, and some init code
###

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


debug code from LvalForState set_constant_value (after same_vals test says T)
            if isinstance(val, Q): #e could optim using flag set from default value?? (since test is not needed in all such cases)
                print "curval is %r, setting to quat %r, and same_vals says they're equal btw" % (self._value, val)
                assert self._value == val, "same_vals was wrong for %r == %r" % (self._value, val) #070227 (trying to catch a bug)


