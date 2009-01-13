# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
inval.py -- simple invalidation/update system for attributes within an object

@author: Bruce
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

bruce 050513 replaced some == with 'is' and != with 'is not', to avoid __getattr__
on __xxx__ attrs in python objects.
"""

from utilities.debug import print_compact_traceback

debug_counter = 0 # uncomment the related code (far below) to find out what's calling our __getattr__ [bruce 050513]

# For now, we only support formulas whose set of inputs is constant,
# in the sense that evaluating the formula always accesses all the inputs.
# (If this rule is violated, we won't detect that but it can cause bugs.)

# For usage instructions, see the example use in chunk.py.
# Later we should add documentation for how to use this in general.
# But I couldn't resist adding just a bit of that now, so here's a sketch...
# assuming you already fully understand the general inval/update pattern,
# which is not explained here.

# If it's not explained here, where is it explained?

# Basically, a formula for attr1 is a _recompute_attr1 method in a client object,
# with a class attribute _inputs_for_attr1 listing the names of other invalidatable attrs
# (in the same instance) used by this formula. The formula must always use all of
# the attrs in that list or bugs can result (described sketchily in comments
# in chunk.py). Whenever any of those "input attrs" is invalidated (and not already invalid),
# attr1 will be invalidated too.

# The formula can also use outside info, provided that attr1
# will be manually invalidated (by external code) whenever that outside info might have changed.

# Invalidation means: declaring (at runtime) that the currently assigned value
# (of some attr in some instance) might be wrong, and should therefore no longer be used,
# but should be recomputed when (or before) it's next needed.

# Invalidation in this system is represented by deleting the invalid attribute.

# (Terminology note:
# "Invalid" means an attr *should* be deleted; "invalidate" means *actually* deleting it.
# It's possible for an attribute to be invalid, but not be invalidated,
# if some external code changes it and doesn't invalidate it. That leads to bugs.)

# ... more info needed here (or, better, in an external doc.html file)
# about inval methods, updating, etc...


class inval_map:
    """
    Record info, for a given class, about which attributes
    (in a hypothetical instance) will need to be invalidated
    when a given one changes; it's ok if this contains cycles
    (I think), but this has never been tested.
    """
    def __init__(self):
        self.affected_by = {} # a public attribute
        
    def record_output_depends_on_inputs(self, output, inputs):
        """
        Record the fact that output (an attr name)
        always depends on each input in inputs (a list of attr names),
        and that output and each input are invalidatable attributes.
        (To just record that attr is an invalidatable attribute,
        call this with inputs == [].)
        """
        # first make sure they are all recorded as invalidatable attrs
        for attr in [output] + inputs:
            self.affected_by.setdefault(attr, [])
        # now record that each input affects output
        for input in inputs:
            lis = self.affected_by[input]
            if not output in lis:
                lis.append(output)
        return
    
    pass # end of class inval_map

# ==

def remove_prefix_func(prefix):
    """
    return a function which assumes its arg starts with prefix, and removes it
    """
    ll = len(prefix)
    def func(str):
        ## assert str.startswith(prefix)
        return str[ll:]
    return func

def filter_and_remove_prefix( lis, prefix):
    return map( remove_prefix_func( prefix), filter( lambda attr: attr.startswith( prefix), lis ) )

invalmap_per_class = {}

def make_invalmap_for(obj):
    """
    make and return a fresh inval_map for an object (or a class)
    """
    # check if all _recompute_xxx have _input_for_xxx defined!
    imap = inval_map()
    inputsfor_attrs = filter_and_remove_prefix( dir(obj), "_inputs_for_" )
    recompute_attrs = filter_and_remove_prefix( dir(obj), "_recompute_" )
    for attr in inputsfor_attrs:
        assert attr in recompute_attrs, "_inputs_for_%s should be defined only when _recompute_%s is defined" % (attr, attr)
        recompute_attrs.remove(attr)
        inputs = getattr(obj, "_inputs_for_" + attr)
        output = attr
        assert type(inputs) is type([])
        imap.record_output_depends_on_inputs( output, inputs)
    assert not recompute_attrs, \
           "some _recompute_ attrs lack _inputs_for_ attrs: %r" % recompute_attrs
    return imap

# ==

class InvalMixin:
    """
    Mixin class for supporting a simple invalidation/update scheme
    for certain attributes of each instance of the main class you use it with.
    Provides __getattr__ and a few other methods. Supports special
    attributes and methods in the main class whose names
    start with prefixes _inputs_for_, _get_, _recompute_.
    """
    
    # Recomputation methods. Certain attributes, whose values should always
    # equal the result of formulas which depend on other attributes (of the
    # same or different objects), are not always explicitly defined,
    # but instead are recomputed as needed by the following methods, which
    # should only be called by __getattr__ (which will save their results
    # for reuse until they become incorrect, as signalled by the
    # "invalidation methods" defined elsewhere).
    # [Sometime I should write a separate documentation file containing a
    #  more complete explanation. #e]
    # 
    # The recomputation method _recompute_xxx should compute the currently
    # correct value for the attribute self.xxx, and either return it, or store
    # it in self.xxx (and return None), as it prefers. (If the correct value
    # is None, then to avoid ambiguity the recomputation method must store it.
    # If it doesn't, some assertions might fail.)
    #
    # Exceptions raised by these
    # methods are errors, and result in a printed warning and self.xxx = None
    # (but self.xxx will be considered valid, in the hope that this will
    # delay the next call to the buggy recompute method).
    #
    # A recomputation method _recompute_xxx can also set the values of other
    # invalidatable attributes (besides xxx) which it happens to compute at
    # the same time as xxx, to avoid the need to redundantly compute them later;
    # but if it does that, it must call self.validate_attr on the names of those
    # attributes, or later invalidations of them might not be done properly.
    # (Actually, for now, that method is a noop except for checking assertions,
    #  and nothing will detect the failure to call it when it should be called.)
    #
    # self.validate_attr should never be called except when the attr was known
    # to be invalid, and was then set to the correct value (e.g. in a
    # recomputation method). This differs from self.changed_attr, which is
    # generally called outside of recomputation methods by code which sets
    # something to its new correct value regardless of whether it was previously
    # invalidated. Changed_attr has to invalidate whatever depends on attr, but
    # validate_attr doesn't.
    #
    # (We might or might not teach __getattr__ to detect the bug of not calling
    #  validate_attr; if we do and it's efficient, the requirement of calling it
    #  explicitly could be
    #  removed. Maybe scanning self.__dict__ before and after will be ok. #e)
    #
    # The set of invalidatable attributes needed by _recompute_xxx is determined
    # by .... or can be specified by... ###@@@
    # If the correct value of self.xxx depends on anything else, then any code
    # that changes those other things needs to either declare ... or call ... ###@@@.

    def __getattr__(self, attr): # in class InvalMixin; doesn't inherit _eq_id_mixin_ -- should it? ##e [060209]
        """
        Called to compute certain attrs which have not been recomputed since
        the other attrs they depend on were initialized or changed. Code which
        might change the value that these attrs should have (i.e. which might make
        them "invalid") is required to "invalidate them" (i.e. to declare them
        invalid, at runtime) by......
        """
        if attr.startswith('_'): # e.g. __repr__, __add__, etc -- be fast
##            #bruce 050513 debug code to see why this is called so many times (1.7M times for load/draw 4k atom part)
##            global debug_counter
##            debug_counter -= 1
##            if debug_counter < 0:
##                debug_counter = 38653
##                print_compact_stack("a random _xxx call of this, for %r of %r: " % (attr, self))
            raise AttributeError, attr
##        global debug_counter
##        debug_counter -= 1
##        if debug_counter < 0:
##            debug_counter = 38653
##            print_compact_stack("a random non-_xxx call of this, for %r of %r: " % (attr, self))
        return getattr_helper(self, attr)
    
    # invalidation methods for client objects to call manually
    # and/or for us to call automatically:
    
    def validate_attr(self, attr):
        # in the initial implem, just storing the attr's value is sufficient.
        # let's just make sure it was in fact stored.
        assert self.__dict__.has_key(attr), "validate_attr finds no attr %r was saved, in %r" % (attr, self)
        #e if it was not stored, we could also, instead, print a warning and store None here.
        pass

    def validate_attrs(self, attrs):
        map( self.validate_attr, attrs)
        
    def invalidate_attrs(self, attrs, **kws):
        """
        invalidate each attribute named in the given list of attribute names
        """
        if not kws:
            # optim:
            map( self.invalidate_attr, attrs)
        else:
            map( lambda attr: self.invalidate_attr(attr, **kws), attrs)
        
    def invalidate_attr(self, attr, skip = ()):
        """
        Invalidate the attribute with the given name.
        This requires also invalidating any attribute registered as depending on this one,
        but in doing that we won't invalidate the ones named in the optional list 'skip',
        or any which depend on attr only via the ones in 'skip'.
        """
        #e will we need to support special case invalidation methods for certain
        # attrs, like molecule.havelist?
        if attr in skip:
            return
        try:
            delattr(self, attr)
        except AttributeError:
            # already invalid -- we're done
            return
        # it was not already invalid; we have to invalidate its dependents too
        self.changed_attr(attr, skip = skip)
        return
        
    def changed_attr(self, attr, **kws):
        for dep in self.__imap[attr]:
            self.invalidate_attr(dep, **kws)
        return

    def changed_attrs(self, attrs):
        """
        You (the caller) are reporting that you changed all the given attrs;
        so we will validate these attrs and invalidate all their dependees,
        but when invalidating each one's dependees, we'll
        skip inval of *all* the attrs you say you directly changed,
        since we presume you changed them all to correct values.
        
        For example, if a affects b, b affects c, and you tell us you
        changed a and b, we'll end up invalling c but not b.
        Thus, this is not the same as calling changed_attr on each one --
        that would do too much invalidation.
        """
        self.validate_attrs(attrs)
        for attr in attrs:
            self.changed_attr( attr, skip = attrs )

    # init method:
    
    def init_InvalMixin(self): # used to be called 'init_invalidation_map'
        """
        call this in __init__ of each instance of each client class
        """
        # Set self.__inval_map. We assume the value depends only on the class,
        # so we only compute it the first time we see this class.
        key = id( self.__class__)
        imap = invalmap_per_class.get( key)
        if not imap:
            imap = make_invalmap_for( self.__class__)
            invalmap_per_class[key] = imap
        self.__imap = imap.affected_by
        return
    
    # debug methods (invalidatable_attrs is also used by some Undo update methods (not just for debugging) as of 060224)

    def invalidatable_attrs(self):
        res = self.__imap.keys()
        res.sort() #bruce 060224
        return res
    
    def invalidatableQ(self, attr):
        return attr in self.__imap #bruce 060224 revised this
        
    def invalidQ(self, attr):
        assert self.invalidatableQ(attr)
        return not self.__dict__.has_key(attr)
        
    def validQ(self, attr):
        assert self.invalidatableQ(attr)
        return self.__dict__.has_key(attr)

    def invalid_attrs(self):
        return filter( self.invalidQ, self.invalidatable_attrs() )

    def valid_attrs(self):
        return filter( self.validQ, self.invalidatable_attrs() )
    
    pass # end of class InvalMixin


def getattr_helper(self, attr):
    """
    [private helper function]
    self is an InvalMixin instance (but this is a function, not a method)
    """
    # assume caller has handled attrs starting with '_'.
    # be fast in this function, it's called often.

    # simplest first: look for a get method
    # (look in self.__class__, for speed; note that we get an unbound method then)
    ubmeth = getattr(self.__class__, "_get_" + attr, None)
    if ubmeth:
        # _get_ method is not part of the inval system -- just do it
        return ubmeth(self) # pass self since unbound method
    # then look for a recompute method
    ubmeth = getattr(self.__class__, "_recompute_" + attr, None)
    if not ubmeth:
        raise AttributeError, attr #bruce 060228 making this more conservative in case it's not always so rare
##        # rare enough to raise a nicer exception than our own __getattr__ does
##        ###e this should use a safe_repr function for self [bruce 051011 comment]
##        raise AttributeError, "%s has no %r: %r" % (self.__class__.__name__, attr, self)
    try:
        val = ubmeth(self)
    except:
        print_compact_traceback("exception (ignored, storing None) in _recompute_%s method for %r: " % (attr,self) )
        val = None
        setattr(self, attr, val) # store it ourselves
    # now either val is not None, and we need to store it ourselves
    # (and we'll be loose and not warn if it was already stored --
    #  I don't know if asserting it was not stored could be correct in theory);
    # or it's None and correct value should have been stored (and might also be None).
    if val is not None:
        setattr(self, attr, val) # store it ourselves
    else:
        val = self.__dict__.get(attr)# so we can return it from __getattr__
        if val is None and self.__dict__.get(attr,1):
            # (test is to see if get result depends on default value '1')
            # error: val was neither returned nor stored; always raise exception
            # (but store it ourselves to discourage recursion if exception ignored)
            setattr(self, attr, val) 
            msg = "bug: _recompute_%s returned None, and did not store any value" % attr
            print msg
            assert val is not None, msg # not sure if this will be seen
    ## self.validate_attr(attr) # noop except for asserts, so removed for now
    return val

# ==

# test code

class testclass(InvalMixin):
    def __init__(self):
        self.init_InvalMixin()
        
    _inputs_for_c = ['a','b']
    def _recompute_c(self):
        return self.a + self.b
    
    _inputs_for_d = ['c']
    def _recompute_d(self):
        return 100 + self.c
    
    _inputs_for_e = ['c']
    def _recompute_e(self):
        return 1000 + self.c

def testab(a,b,tobj):
    tobj.a = a
    tobj.b = b
    tobj.invalidate_attr('c')
    assert tobj.e == 1000 + a + b
    tobj.invalidate_attr('c')
    assert tobj.e == 1000 + a + b

if __name__ == '__main__':
    # if you need to import this from somewhere else for the test, use this code,
    # removed to avoid this warning:
    # .../cad/src/inval.py:0: SyntaxWarning: name
    # 'print_compact_traceback' is assigned to before global declaration
##    global print_compact_traceback
##    for mod in sys.modules.values(): # import it from somewhere...
##        try:
##            print_compact_traceback = mod.print_compact_traceback
##            break
##        except AttributeError:
##            pass
    tobj = testclass()
    testab(1,2,tobj)
    testab(3,4,tobj)
    tobj.a = 17
    tobj.c = 23 # might be inconsistent with the rule, that's ok
    print "about to tobj.changed_attrs(['a','c'])"
    tobj.changed_attrs(['a','c']) # should inval d,e but not c or b (even tho a affects c); how do we find out?
    print "this should inval d,e but not c or b (even tho a affects c); see what is now invalid:"
    print tobj.invalid_attrs()
    print "now confirm that unlike the rule, c != a + b; they are c,b,a = %r,%r,%r" % (tobj.c,tobj.b,tobj.a)
    print "and fyi here are d and e: %r and %r" % (tobj.d,tobj.e)
    print "and here are c,b,a again (should be unchanged): %r,%r,%r" % (tobj.c,tobj.b,tobj.a)

# this looks correct, need to put outputs into asserts, above:
"""
about to tobj.changed_attrs(['a','c'])
this should inval d,e but not c or b (even tho a affects c); see what is now invalid:
['e', 'd']
now confirm that unlike the rule, c != a + b; they are c,b,a = 23,4,17
and fyi here are d and e: 123 and 1023
and here are c,b,a again (should be unchanged): 23,4,17
"""

# end

