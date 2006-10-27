'''
ExprsMeta.py -- one metaclass, to take care of whatever is best handled using a metaclass,
and intended to be used for all or most classes in this module.

$Id$

===

####### need to insert improved text for the following, drafted 061025 in notesfile: ######@@@@@@

here it is, not quite done, but i might still edit it in the text file, and/or wikify it

==

Python provides several ways for class attributes to determine how instance attributes are computed.
To summarize: the class attributes can be constants, functions, or other descriptors,
with corresponding instance attribute accesses resulting in constants, bound methods, or fairly arbitrary behavior.

We want to add a few specific ways of our own:

- class attributes which are formulas in _self, 
  for which instance.attr should be a read-only per-instance memoized invalidatable/recomputable value
  computed by the formula

- class attributes which are like a "descriptor expression", but with the "descriptor" knowing the class and attr
it was assigned to (which ordinary ones don't know):

  - for example, resulting in instance.attr acting like a dict of individually invalidatable/recomputable values,
  defined by a method or formula on the key, extensible as new keys are used,
  with the permitted keys either unlimited, fitting some type or pattern, or listed explicitly by a
  once-computable method or formula
  
  [###e (details unclear -- does this mean all exprs include details of what gets memoized, at what level inside??)]

- specially-named methods, assigned to _prefix_attr rather than directly to attr, which nonetheless control what
instance.attr does (similarly to one of the ways mentioned above), with subclasses able to override superclasses
about attr even if they define its behavior by assigning to different class attributes (one to attr itself, 
one to _prefix1_attr, one to _prefix2_attr). (This way is most convenient when you want to express the behavior using
Python code rather than as formulas.)

We find a metaclass to be the simplest way of achieving certain key aspects of those desires:

- Descriptor exprs might be shared among attrs or between classes -- they don't know their cls/attr location,
and it's not even unique (meaning they'd be wrong to cache cls/attr info inside themselves, even if they knew it).

A metaclass can wrap descriptors (or the like) with this location info, with the resulting wrapped exprs
being unique (so they can be allowed to cache data which depends on this location info). Effectively, it can
wrap things that follow our own descriptor protocol to produce things that follow Python's.

- Overriding of attr assignments doesn't normally affect related attrs; if some class defines contradicting
values for attr and _prefix1_attr and _prefix2_attr, all meant to control instance.attr in different ways,
the defn to follow should be the one defined in the innermost class, but you can't easily tell which one that is.
(If Python copies superclass dicts into subclass dicts, maybe you can't tell at all, absent metaclasses, except by
something as klugy as comparing line numbers found inside function code objects and their classes.)

  - We could solve this just by recording the class and attr of each def, as we'll do to solve the prior problem...
  ### could we really use that info to solve this? should we?
  
  - But what we actually do is have the metaclass create something directly on the attr, 
  which says how it's supposed to be 
  defined in that class (and is a descriptor which causes that to actually happen in the right way). 
  
  This scheme has the advantage of dispensing with any need for __getattr__ (I think).
  
  (Note, it could also do it by creating a special prefix attr saying
   which other prefix attr controls the def. Should it?? ####)

The actual creation of the class/attr-specific descriptor for runtime use is best done lazily, 
on first use of that attr in an instance. This lets it more safely import code, more easily
access inherited class attrs, etc... and lets most of the system be more similar to non-metaclass-based code.

The metaclass just records enough info, and makes it active in the right places, to allow this to happen properly.


======= old text, not sure it's all obs/redundant now:

Reasons we needed a metaclass, and some implementation subtleties:

- If there are ways of defining how self.attr behaves using different class attributes (e.g. attr or _C_attr or _CV_attr),
overriding by subclasses would not normally work as intended if subclasses tried to override different attrs
than the ones providing the superclass behavior. (E.g., defining _C_attr in a subclass would not override a formula or constant
assigned directly to attr in a superclass.)

ExprsMeta solves this problem by detecting each class's contributions to the intended definition of attr (for any attr)
from any class attributes related to attr (e.g. attr or _xxx_attr), and encoding these as descriptors on attr itself.

(Those descriptors might later replace themselves when first used in a given class, but only with descriptors on the same attr.)

- Some objects assigned to attr in a class don't have enough info to act well as descriptors, and/or might be shared
inappropriately on multiple attrs in the same or different classes. (Formulas on _self, assigned to attr, can have both problems.)

ExprsMeta replaces such objects with unshared, wrapped versions which know the attr they're assigned to.

Note that it only does this in the class in which they are syntactically defined -- they might be used from either that class
or a subclass of it, and if they replace themselves again when used, they should worry about that. Python probably copies refs
to them into each class's __dict__, but these copies are all shared. This means they should not modify themselves in ways which
depend on which subclass they're used from.

For example, if a descriptor assigned by ExprsMeta makes use of other attributes besides its main definining attribute,
those other attributes might be overridden independently of the main one, which means their values need to be looked for
independently in each class the descriptor is used in. This means two things:

1. The descriptor needs to cache its knowledge about how to work in a specific class, in that class, not in itself
(not even if it's already attached to that class, since it might be attached to both a class and its subclass).
It should do this by creating a new descriptor (containing that class-specific knowledge) and assigning it only into one class.

2. In case I'm wrong about Python copying superclass __dict__ refs into subclass __dicts__, or in case this behavior changes,
or in case Python does this copying lazily rather than at class-definition time, each class-specific descriptor should verify
it's used from the correct class each time. If it wants to work correctly when that fails (rather than just assertfailing),
it should act just like a non-class-specific descriptor and create a new class-specific copy assigned to the subclass it's used from.

Note that the simplest scheme combines points 1 and 2 by making each of these descriptors the same -- it caches info for being used
from the class it's initially assigned to, but always checks this and creates a subclass-specific descriptor (and delegates that
use to it) if used from a subclass. All we lose by fully merging those points is the check on my beliefs about Python.
Hopefully a simple flag can handle that by asserting (warning when false) that the copying into a subclass happens at most once.


What ExprsMeta handles specifically:

- formulas on _self assigned directly to attr (in a class)

- _C_attr methods (or formulas??), making use of optional _TYPE_attr or _DEFAULT_attr declarations (#k can those decls be formulas??)

- _CV_attr methods (or formulas??), making use of optional _CK_attr methods (or formulas??), and/or other sorts of decls as above

- not sure: what about _args and _options? Both of them are able to do things to attrs... ####k
'''

__all__ = ['remove_prefix', 'ExprsMeta', 'ConstantComputeMethodMixin', 'DictFromKeysAndFunction', 'RecomputableDict']

# don't misspell it ExprMeta!
###e nim or wrong as of 061024, also not yet used ####@@@@

# plan: create some general descriptor classes corresponding to the general scheme described above, then fill them in

# == imports

# from python library
from idlelib.Delegator import Delegator

# from modules in cad/src
from env import seen_before
from debug import print_compact_traceback

# from this exprs package in cad/src
from lvals import Lval, LvalDict2 ### make reloadable? I'm not sure if *this* module supports reload. ##k

# kluge to avoid recursive import problem (done in modules which are imported by basic):
def printnim(*args):
    import basic
    basic.printnim(*args)
    return

# ==

def remove_prefix(str1, prefix):#e refile
    "if str1 starts with prefix, remove it (and return the result), else return str1 unchanged"
    if str1.startswith(prefix):
        return str1[len(prefix):]
    return str1

class ClassAttrSpecific_NonDataDescriptor(object):
    """Abstract class for descriptors which cache class- and attr- specific info
    (according to the scheme described in the ExprsMeta module's docstring).
       Actually, there's a pair of abstract classes, one each for Data and NonData descriptors.
       To make our implem of self.copy_for_subclass() correct in our subclasses (so they needn't
    override it), we encourage them to not redefine __init__, but to rely on our implem of __init__
    which stores all its arguments in fixed attrs of self, namely clsname, attr, args, and kws,
    and then calls self._init1(). [self.cls itself is not yet known, but must be set before first use,
    by calling _ExprsMeta__set_cls.]
    """
    __copycount = 0
    cls = None
    def __init__(self, clsname, attr, *args, **kws):
        # to simplify
        #e perhaps this got called from a subclass init method, which stored some additional info of its own,
        # but most subclasses can just let us store args/kws and use that, and not need to override copy_for_subclass. [#k]
        self.clsname = clsname #######@@@@@@ fix for this in CV_rule too
        ## self.cls = cls # assume this is the class we'll be assigned into (though we might be used from it or any subclass)
        self.attr = attr # assume this is the attr of that class we'll be assigned into
        self.args = args
        self.kws = kws
        self._init1()
        #e super init?
    def _init1(self):
        "subclasses can override this"
        pass
    def _ExprsMeta__set_cls(self, cls):
        "[private method for ExprsMeta to call when it knows the defining class]"
        self.cls = cls
        assert self.clsname == cls.__name__ #k
        #e should we store only the class id and name, to avoid ref cycles? Not very important since classes are not freed too often.
        return
    def check(self, cls2):
        ###e remove all calls of this when it works (need to optim)
        cls = self.cls
        assert cls is not None # need to call _ExprsMeta__set_cls before now
        assert self.clsname == cls.__name__ # make sure no one changed this since we last checked
        attr = self.attr
        assert cls.__dict__[attr] is self
        if cls2 is not None: #k can that ever fail??
            assert issubclass(cls2, cls), "cls2 should be subclass of cls (or same class): %r subclass of %r" % (cls2, cls)
        return
    def __get__(self, obj, cls):
        "subclasses should NOT override this -- override get_for_our_cls instead"
        self.check(cls) #e remove when works (need to optim)
        if obj is None:
            return self
        assert cls is not None, "I don't know if this ever happens, or what it means if it does, or how to handle it" #k in py docs
            #e remove when works (need to optim)
        if cls is not self.cls:
            copy = self.copy_for_subclass(cls)
            attr = self.attr
            cls.__dict__[attr] = copy
            return copy.__get__(obj, cls)
        return self.get_for_our_cls(obj)
    # we have no __set__ or __del__ methods, since we need to be a non-data descriptor.
    def get_for_our_cls(self, obj):
        "Subclass should implement -- do the __get__ for our class (initializing our class-specific info if necessary)"
        return None
    def copy_for_subclass(self, cls):
        copy = self.__class__(cls, self.attr, *self.args, **self.kws)
        copy.__copycount = self.__copycount + 1
        if copy.__copycount > 1:
            if not seen_before("ClassAttrSpecific_NonDataDescriptor copied again"):
                print "once-per-session developer warning: this copy got copied again:", self
        return copy
    pass # end of class ClassAttrSpecific_NonDataDescriptor

class ClassAttrSpecific_DataDescriptor(ClassAttrSpecific_NonDataDescriptor):
    """Like our superclass, but has __set__ and __del__ methods so as to be a data descriptor.
    Our implems just assert 0; subclasses can override them, to work or not, but don't need to.
       WARNING: if subclasses did intend to override them, most likely they'd need overhead code like our superclass has in __get__,
    so in practice such overriding is not yet supported.
    (Either method would be enough to make Python treat us as a data descriptor,
     but we'd rather complain equally about either one running, so we define both.)
    """
    def __set__(self, *args):
        assert 0, "__set__ is not yet supported in this abstract class"
    def __del__(self, *args):
        assert 0, "__del__ is not yet supported in this abstract class"
    pass

# ==

class C_rule(ClassAttrSpecific_DataDescriptor):
    """One of these should be stored on attr by ExprsMeta when it finds a _C_attr compute method,
    formula (if supported #k), or constant,
    or when it finds a formula directly on attr.
    """
    # implem note: this class has to be a data descriptor, because it wants to store info of its own in instance.__dict__[attr],
    # without that info being retrieved as the value of instance.attr. If it would be less lazy (and probably less efficient too)
    # and store that info somewhere else, it wouldn't matter whether it was a data or non-data descriptor.
    def get_for_our_cls(self, instance):
        # make sure cls-specific info is present -- we might have some, in the form of _TYPE_ decls around compute rule?? not sure. ##e
        # (none for now)
        
        # now find instance-specific info --
        # namely an Lval object for instance.attr, which we store in instance.__dict__[attr]
        # (though in theory, we could store it anywhere, as long as we'd find a
        #  different one for each instance, and delete it when instance got deleted)
        attr = self.attr
        try:
            lval = instance.__dict__[attr]
        except KeyError:
            # make a new Lval object from the compute_method (happens once per attr per instance)
            compute_method = self.make_compute_method_for_instance(instance)
            lval = instance.__dict__[attr] = Lval(compute_method)
        return lval.get_value() # this does usage tracking, validation-checking, recompute if needed
            # Notes:
            # [from when this code was in class _C_rule used by InvalidatableAttrsMixin in lvals.py; probably still applicable now]
            # - There's a reference cycle between compute_method and instance, which is a memory leak.
            # This could be fixed by using a special Lval (stored in self, not instance, but with data stored in instance)
            # which we'd pass instance to on each use. (Or maybe a good solution is a C-coded metaclass, for making instance?)
            # - The __set__ in our superclass detects the error of the compute method setting the attr itself. Good enough for now.
            # Someday, if we use a special Lval object that is passed self and enough into to notice that itself,
            # then we could permit compute objects to do that, if desired. But the motivation to permit that is low.
            # - There is no provision for direct access to the Lval object (e.g. to directly call its .set_formula method).
            # We could add one if needed, but I don't know the best way. Maybe find this property (self) and use a get_lval method,
            # which is passed the instance? Or, setattr(instance, '_lval_' + attr, lval).
    def make_compute_method_for_instance(self, instance):
        assert 0, "subclass should implement this"
    pass # end of class C_rule

# what could cause the exception listed in the last line of the following? It looks like Python printed it while freeing a C_rule...
# could there be some problem with freeing things made using my metaclass??
'''
reloading exprs.Exprs
exception in testdraw.py's drawfunc call ignored: exceptions.NameError: global name 'args' is not defined
  [testdraw.py:274] [testdraw.py:308] [testdraw.py:437] [test.py:25] [Rect.py:15] [widget2d.py:10] [instance_helpers.py:222] [ExprsMeta.py:467] [ExprsMeta.py:384] [ExprsMeta.py:298] [ExprsMeta.py:177] [ExprsMeta.py:278]
Exception exceptions.AssertionError: <exceptions.AssertionError instance at 0xd487dc8> in <bound method C_rule_for_method.__del__ of <exprs.ExprsMeta.C_rule_for_method object at 0xd499d70>> ignored
'''

class C_rule_for_method(C_rule):
    def _init1(self):
        ## () = self.args is a syntax error!
        assert len(self.args) == 0
    def make_compute_method_for_instance(self, instance):
        return getattr(instance, '_C_' + self.attr) # kluge, slightly, but it's the simplest and most efficient way
        ###e maybe a better way is to grab the function from cls.__dict__ and call its __get__?
    pass

class C_rule_for_formula(C_rule):
    def _init1(self):
        (self.formula,) = self.args
    def make_compute_method_for_instance(self, instance):
        return self.formula._e_compute_method(instance)
    pass

def choose_C_rule_for_val(clsname, attr, val):
    "return the correct one of C_rule_for_method or C_rule_for_formula, depending on val"
    if hasattr(val, '_e_compute_method'):
        # assume val is a formula on _self
        return C_rule_for_formula(clsname, attr, val)
    #e support constant val?? not for now.
    else:
        return C_rule_for_method(clsname, attr)
        ###KLUGE (should change): they get val as a bound method directly from cls, knowing it came from _C_attr
    pass

# ==

class CV_rule(ClassAttrSpecific_NonDataDescriptor):
    """One of these should be stored by ExprsMeta when it finds a _CV_attr compute method,
    formula (if supported #k), or constant (if supported #k).
    """
    def get_for_our_cls(self, instance):
        attr = self.attr
        # Make sure cls-specific info is present -- we might have some, in the form of _TYPE_ decls around compute rule?? not sure. ##e
        # In principle, we certainly have some in the form of the optional _CK_ compute method...
        # but our current code finds it easier to make this instance-specific and just grab a bound method for each instance.
        if 0:
            # if it's ever class-specific we might do something like this:
            try:
                compute_methodK = self.compute_methodK
            except AttributeError:
                compute_methodK = getattr(self.cls, self.prefixK + attr, None)
                #e process it if it's a formula or constant sequence
                self.compute_methodK = compute_methodK
        
        # Now find instance-specific info --
        # which is a RecomputableDict object for our attr in instance, and our bound V and K methods.
        # (Formulas or constants for them are not yet supported. ###e nim)
        try:
            rdobj = instance.__dict__[attr]
            print "warning: rdobj was not found directly, but it should have been, since this is a non-data descriptor", self #e more?
        except KeyError:
            # make a new object from the compute_methods (happens once per attr per instance)
            rdobj = instance.__dict__[attr] = self.make_rdobj_for_instance(instance)
        return rdobj # this object is exactly what instance.attr retrieves (directly, from now on, or warning above gets printed)
    
    def make_rdobj_for_instance(self, instance):
        #e refile into a subclass?? (so some other subclass can use formulas)
        #e actually, splitting rhs types into subclasses would not work,
        # since main subclass can change whether it assigns formula or function to _CV_attr!!!
        # ditto for C_rule -- say so there... wait, i might be wrong for C_rule and for _CV_ here,
        # since self is remade for each one, but not for _CK_ (since indeply overridden) if that
        # needn't match _CV_ in type. hmm. #####@@@@@
        compute_methodV = getattr(instance, self.prefixV + attr) # should always work
##        compute_methodV = bound_compute_method_to_callable( compute_methodV,
##                                                              formula_symbols = (_self, _i), ###IMPLEM _i
##                                                              constants = True )
##            # also permit formulas in _self and _i, or constants (either will be converted to a callable)
        assert callable(compute_methodV)
        compute_methodK = getattr(instance, self.prefixK + attr, None)
            # optional method or [nim] formula or constant, or None (None can mean missing, since legal constant values are sequences)
        if compute_methodK is not None:
##            compute_methodK = bound_compute_method_to_callable( compute_methodK,
##                                                                formula_symbols = (_self,),
##                                                                constants = True )
            assert callable(compute_methodK)
        obj = RecomputableDict(compute_methodV, compute_methodK)
        return obj
    # Note: we have no __set__ method, so in theory (since Python will recognize us as a non-data descriptor),
    # once we've stored obj in instance.__dict__ above, it will be gotten directly
    # without going through __get__. We print a warning above if that fails.

    # Note: similar comments about memory leaks apply, as for C_rule.
    
    pass # end of class CV_rule

def choose_CV_rule_for_val(clsname, attr, val):
    "return an appropriate CV_rule object, depending on val"
    if hasattr(val, '_e_compute_method'):
        assert 0, "formulas on _CV_attr are not yet supported"
        # when they are, we'll need _self and _i both passed to _e_compute_method
    else:
        # constants are not supported either, for now
        # so val is a python compute method (as a function)
        ###KLUGE: CV_rule gets val as a bound method, like C_rule does
        return CV_rule_for_val(clsname, attr)
    pass

# ==

# prefix_X_ routines process attr0, val on clsname, where attr was prefix _X_ plus attr0, and return val0
# where val0 can be directly assigned to attr0 in cls (not yet known); nothing else from defining cls should be assigned to it.

def prefix_C_(clsname, attr0, val):
    val0 = choose_C_rule_for_val(clsname, attr0, val)
    return val0

def prefix_CV_(clsname, attr0, val):
    val0 = choose_CV_rule_for_val(clsname, attr0, val)
    return val0

def prefix_nothing(clsname, attr0, val):
    # assume we're only called for a formula
    ## assert hasattr(val, '_e_compute_method')
    assert val_is_special(val), "why is this val not special? clsname %r, attr0 %r, val %r" % (clsname, attr0, val)
        #e rename val_is_special
    val0 = choose_C_rule_for_val(clsname, attr0, val)
    return val0

def prefix_DEFAULT_(clsname, attr0, val):
    "WARNING: caller has to also know something about _DEFAULT_, since it declares attr0 as an option"
    if not hasattr(val, '_e_compute_method'): ###e improve condition
        # if val is not a formula or any sort of expr, it can just be a constant. e.g. _DEFAULT_color = gray
        # what if it's a method?? that issue is ignored for now. (bug symptom: bound method might show up as the value. not sure.)
        # what if it's a "constant classname" for an expr? that's also ignored. that won't be in this condition...
        # (the bug symptom for that would be a complaint that it's not special (since it doesn't have _self).)
        # Q: if it's a formula or expr, not free in _self, should we just let that expr itself be the value??
        # This might make sense... it ought to mean, the value doesn't depend on self (unless it's a bound method, also ok maybe).
        #####@@@@@
        return val
    return prefix_nothing(clsname, attr0, val)

prefix_map = {'':prefix_nothing,
              '_C_':prefix_C_,
              '_DEFAULT_': prefix_DEFAULT_,
              '_CV_':prefix_CV_,
              }
    #e this could be more modular, less full of duplicated prefix constants and glue code

def attr_prefix(attr): # needn't be fast
    for prefix in prefix_map: #.keys()
        if prefix and attr.startswith(prefix):
            return prefix
    return ''

def val_is_special(val):
    "val is special if it's a formula in _self, i.e. is an instance (not subclass!) of Expr, and contains _self as a free variable."
    from Exprs import Expr # let's hope it's reloaded by now, if it's going to be ... hmm, we run during import so we can't assume that.
    return isinstance(val, Expr) and val._e_free_in('_self')
        ## outtake: and val.has_args [or more likely, and val._e_has_args]
        ## outtake: hasattr(val, '_e_compute_method') # this was also true for classes

# ==
    
class ExprsMeta(type):
    # follows 'MyMeta' metaclass example from http://starship.python.net/crew/mwh/hacks/oop-after-python22-1.txt
    def __new__(cls, name, bases, ns):
        # Notes:
        # - this code runs once per class, so it needn't be fast.
        # - cls is NOT the class object being defined -- that doesn't exist yet, since it's our job to create it and return it!
        #   (It's the class ExprsMeta.)
        # - But we know which class is being defined, since we have its name in the argument <name>.
        data_for_attr = {}
        processed_vals = []
        orig_ns_keys = ns.keys() # only used in exception text, for debugging
        # handle _options
        _options = ns.pop('_options', None)
        if _options is not None:
            assert type(_options) is type({})
            for optname, optval in _options.items():
                # _DEFAULT_optname = optval
                attr = '_DEFAULT_' + optname
                assert not ns.has_key(attr), \
                       "error: can't define %r both as %r and inside _options in the same class %r (since ExprsMeta is its metaclass); ns contained %r" % \
                       ( optname, attr, name, orig_ns_keys )
                ns[attr] = optval
                # no need to check for ns[optname] here -- this will be caught below -- but the error message will be misleading
                # since it will pretend you defined it using _DEFAULT_; so we'll catch that case here, at least
                # (though this doesn't catch a conflict with some other way of defining optname; that'll still have misleading error
                #  msg below).
                assert not ns.has_key(optname), \
                       "error: can't define %r directly and inside _options in the same class %r (since ExprsMeta is its metaclass); ns contained %r" % \
                       ( optname, name, orig_ns_keys )
                del attr
                continue
            del optname, optval
        del _options
        # handle _args [not sure if this is the right place to do that]
        _args = ns.pop('_args', None)
        if _args is not None:
            ## assert type(_args) is type(()),
            if type(_args) is type(""):
                # permit this special case for convenience
                _args = (_args,)
            if not (type(_args) is type(())):
                # note: printed only once per value of _args (which might be lots of times, but not as many as for each error)
                printnim( "_args should have type(()) but doesn't; its value is %r" % (_args,) )
                    # this once happened since I said ('thing') when I meant ('thing',). Should the first case be allowed,
                    # as a special case for convenience? Probably yes, since the values have to be strings.
                    # We could even canonicalize it here.
            printnim("_args is nim in ExprsMeta")###@@@ actually we'll handle them when we instantiate, much later, other file
        for attr, val in ns.iteritems():
            # If attr has a special prefix, or val has a special value, run attr-prefix-specific code
            # for defining what value to actually store on attr-without-its-prefix. Error if we are told
            # to store more than one value on attr.

            #obs?:
            # which might create new items in this namespace (either replacing ns[attr],
            # or adding or wrapping ns[f(attr)] for f(attr) being attr without its prefix).
            # (If more than one object here wants to control the same descriptor,
            #  complain for now; later we might run them in a deterministic order somehow.)

            prefix = attr_prefix(attr)
            if prefix:
                attr0 = remove_prefix(attr, prefix)
                assert not ns.has_key(attr0), \
                       "error: can't define both %r and %r in the same class %r (since ExprsMeta is its metaclass); ns contained %r" % \
                       ( attr0, attr, name, orig_ns_keys )
                    #e change that to a less harmless warning?
                    # note: it's not redundant with the similar assert below, except when *both* prefix and val_is_special(val).
                    # note: ns contains just the symbols defined in class's scope in the source code, plus __doc__ and __module__.
            else:
                attr0 = attr
            if prefix or val_is_special(val):
                ok = True
                if not prefix and attr.startswith('_'):
                    # note: this scheme doesn't yet handle special vals on "helper prefixes" such as the following:
                    for helper_prefix in ('_CK_', '_TYPE_'):
                        ## assert not attr.startswith(helper_prefix), "special val not yet supported for %r: %r" % (attr, val)
                        if attr.startswith(helper_prefix):
                            print "WARNING: special val not yet supported for %r: %r" % (attr, val)
                                # this one we need to support:
                                #   _DEFAULT_height = _self.width [now it's in prefix_map]
                                # this one is a bug in my condition for detecting a formula:
                                #   _TYPE_thing = <class 'exprs.widget2d.Widget2D'>
                            ok = False
                            break
                        continue
                if prefix == '_DEFAULT_':
                    printnim("_DEFAULT_ needs to be handled differently before it will let named options override it")###@@@
                    # _DEFAULT_ needs to declare attr0 as an option, ie let it be overridden by named options
                    ### how we'll do this: leave it sitting there in the namespace, DON'T COPY IT TO ATTR (that's WRONG),
                    # instead make the DEFAULT thing a rule of its own, but also do the decl
                    # and also set up a rule on attr which grabs it from options and DEFAULT in the proper way.
                if ok:
                    lis = data_for_attr.setdefault(attr0, [])
                    lis.append((prefix, val))
                pass
            continue
        del attr, val
        for attr0, lis in data_for_attr.items():
            assert len(lis) == 1, "error: can't define %r and %r in the same class %r (when ExprsMeta is its metaclass); ns contained %r" % \
                       ( lis[0][0] + attr0,
                         lis[1][0] + attr0,
                         name, orig_ns_keys )
                #e change that to a less harmless warning?
            prefix, val = lis[0]
            # prefix might be anything in prefix_map (including ''), and should control how val gets processed for assignment to attr0.
            processor = prefix_map[prefix]
            val0 = processor(name, attr0, val) #e does it also need prefix?
            ns[attr0] = val0
            processed_vals.append(val0)
        res = super(ExprsMeta, cls).__new__(cls, name, bases, ns)
        assert res.__name__ == name #k
        for thing in processed_vals:
            try:
                if hasattr(thing, '_ExprsMeta__set_cls'):
                    # (note: that's a tolerable test, since name is owned by this class, but not sure if this scheme is best --
                    #  could we test for it at the time of processing, and only append to processed_vals then??
                    #  OTOH, what better way to indicate the desire for this info at this time, than to have this method? #k)
                    thing.__set_cls(res)
            except:
                print "data for following exception: res,thing =",res,thing
                    # fixed by testing for __set_cls presence:
                    ## res,thing = <class 'exprs.Rect.Rect'> (0.5, 0.5, 0.5)
                    ## AttributeError: 'tuple' object has no attribute 'set_cls' [when it had a different name, non-private]
                raise
        return res # from __new__ in ExprsMeta
    pass # end of class ExprsMeta

# ==

# helpers for CV_rule
# (generally useful, but placed here since this module is very fundamental so should be mostly self-contained;
#  we might relax this later #e, but files helping implement this need to say so, like lvals.py does,
#  since most files in this module assume they can depend on this one.)

class ConstantComputeMethodMixin:
    # use this when defining things used inside ExprsMeta [is this necessary?? maybe it's lazy enough to not need it? I doubt it. #k]
    # only ok when they don't need any recomputes after the first compute.
    # (maybe just use python properties instead? #e)
    def __getattr__(self, attr):
        # return quickly for attrs that can't have compute rules
        if attr.startswith('__') or attr.startswith('_C'):
            raise AttributeError, attr # must be fast for __repr__, __eq__, __add__, etc
        try:
            cmethod = getattr(self, '_C_' + attr)
        except AttributeError:
            raise AttributeError, attr
        try:
            val = cmethod()
        except:
            print_compact_traceback("bla: ") ###e
            val = None
        setattr(self, attr, val)
        return val
    pass
        
class DictFromKeysAndFunction(ConstantComputeMethodMixin):
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
