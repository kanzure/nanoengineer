'''
ExprsMeta.py -- one metaclass, to take care of whatever is best handled using a metaclass,
and intended to be used for all or most classes in this module.

$Id$

===

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



(as _CV_ makes use of _CK_, or various things
make use of _TYPE_attr or _DEFAULT_attr declarations), those  definining attribute

What ExprsMeta handles specifically:

- formulas on _self assigned directly to attr (in a class)

- _C_attr methods (or formulas??), making use of optional _TYPE_attr or _DEFAULT_attr declarations (#k can those decls be formulas??)

- _CV_attr methods (or formulas??), making use of optional _CK_attr methods (or formulas??), and/or other sorts of decls as above

- not sure: what about _args and _options? Both of them are able to do things to attrs... ####k
'''

###e nim or wrong as of 061024, also not yet used ####@@@@

# plan: create some general descriptor classes corresponding to the general scheme described above, then fill them in

# ==

#e imports

## _special_prefixes = ('_C_', '_CV_', '_CK_', ) #e get these from their wrapper-making classes, and make them point to those

_prefixes_and_handlers = {} # extended below

def remove_prefix(str1, prefix):#e refile
    "if str1 starts with prefix, remove it (and return the result), else return str1 unchanged"
    if str1.startswith(prefix):
        return str1[len(prefix):]
    return str1

def _wrapit(v,k):
    nim
    
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

# here is that example code, but remove it later


class MyFunkyDescriptor(object):
    def set_name(self, name):
        self.name = name
    # ...

class MyMeta(type):
    def __new__(cls, name, bases, ns):
        for k, v in ns.iteritems():
            if isinstance(v, MyFunkyDescriptor):
                v.set_name(k)
        return super(MyMeta, cls).__new__(cls, name, bases, ns)

class MyClass:
    __metaclass__ = MyMeta
    attr = MyFunkyDescriptor()


# end
