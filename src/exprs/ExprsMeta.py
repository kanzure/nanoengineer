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

# ==
## _special_prefixes = ('_C_', '_CV_', '_CK_', ) #e get these from their wrapper-making classes, and make them point to those

_prefixes_and_handlers = {} # extended below ###DOIT ####@@@@

def remove_prefix(str1, prefix):#e refile
    "if str1 starts with prefix, remove it (and return the result), else return str1 unchanged"
    if str1.startswith(prefix):
        return str1[len(prefix):]
    return str1

class ClassAttrSpecific_NonDataDescriptor(object):
    """Abstract class for descriptors which cache class- and attr- specific info
    (according to the scheme described in the ExprsMeta module's docstring).
       Actually, there's a pair of abstract classes, one each for Data and NonData descriptors.
    """
    __copycount = 0
    def __init__(self, cls, attr, *args, **kws):
        #e perhaps this got called from a subclass init method, which stored some additional info of its own,
        # but most subclasses can just let us store args/kws and use that, and not need to override copy_for_subclass. [#k]
        self.cls = cls # assume this is the class we'll be assigned into (though we might be used from it or any subclass)
        self.attr = attr # assume this is the attr of that class we'll be assigned into
        self.args = args
        self.kws = kws
        self._init1()
        #e super init?
    def _init1(self):
        "subclasses can override this"
        pass
    def check(self, cls2):
        cls = self.cls
        attr = self.attr
        assert cls.__dict__[attr] is self
        if cls2 is not None: #k can that ever fail??
            assert isinstance(cls2, cls)
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
    """One of these should be stored by ExprsMeta when it finds a _C_attr compute method,
    formula (if supported #k), or constant.
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

class C_rule_for_method(C_rule):
    def make_compute_method_for_instance(self, instance):
        return getattr(instance, '_C_' + self.attr) # kluge, slightly, but it's the simplest and most efficient way
    pass

##class C_rule_for_formula(C_rule):
##    def make_compute_method_for_instance(self, instance):
##        assert 0, "we don't need to support this class, i think"
##    pass

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

# ==
    
def _wrapit(v,k):
    nim

#e main nim thing is what goes between ExprsMeta and the rules above... ####@@@@
    
class ExprsMeta(type):
    # follows 'MyMeta' metaclass example from http://starship.python.net/crew/mwh/hacks/oop-after-python22-1.txt
    def __new__(cls, name, bases, ns):
        data_for_attr = {}
        for k, v in ns.iteritems():
            # If v has a special value, or k has a special prefix, let them run code
            # which might create new items in this namespace (either replacing ns[k],
            # or adding or wrapping ns[f(k)] for f(k) being k without its prefix).
            # (If more than one object here wants to control the same descriptor,
            #  complain for now; later we might run them in a deterministic order somehow.)

            # Note: this code runs once per class, so it needn't be fast at all.
            if hasattr(v, __wrapme__): # __wrapme__ is ExprsMeta's extension to Python's descriptor protocol, more or less #e rename
                v = _wrapit(v, k) # even if k has a special prefix -- we'll process that below, perhaps for the same now-wrapped v
                ns[k] = v ###k verify allowed by iteritems
            for prefix, handler in _prefixes_and_handlers.iteritems():
                if k.startswith(prefix):
                    attr = remove_prefix(k, prefix)
                    lis = data_for_attr.setdefault(attr, [])
                    lis.append((prefix, handler, v))
                    break
            continue
        same_handler = None
        for attr, (prefix, handler, v) in data_for_attr.items():
            # error unless they all have the same handler
            if same_handler is None:
                same_handler = handler
            assert handler is same_handler, "illegal for more than one special prefix to try to control one attr"
                ### problem: this doesn't treat '' as a special prefix, for special v sitting there!!
                # sometimes we like the cooperation (formula in _C_, constant in _C_), but sometimes not (compute method in _C_
                #  should bump against formula in attr). Hmm. ######@@@@@@
            nim ####@@@@ tell handler to deal with prefix and v, setting ns[attr]
        return super(ExprsMeta, cls).__new__(cls, name, bases, ns)

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
