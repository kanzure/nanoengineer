'''
ExprsMeta.py -- one metaclass, to take care of whatever is best handled using a metaclass,
and intended to be used for all or most classes in this module.

$Id$

===

Reasons we needed a metaclass:

- If there are ways of defining how self.attr behaves using different class attributes (e.g. attr or _C_attr or _CV_attr),
overriding by subclasses would not normally work as intended if subclasses tried to override different attrs
than the ones providing the superclass behavior. ExprsMeta solves this problem by detecting each class's contributions
to defining attr from any class attributes (attr or _xxx_attr), and encoding them as descriptors on attr itself.

- Some objects assigned to attr in a class don't have enough info to act well as descriptors, and/or might be shared
inappropriately on multiple attrs in the same or different classes. (Formulas on _self, assigned to attr, have both problems.)
ExprsMeta replaces such objects with unshared wrapped versions which know attr. (Note that it only does this in the class
in which they are defined -- they might still be used from either that class or a subclass of it, and if they replace
themselves again when used, they should worry about that. Python probably copies refs to them into each class's dict,
but these copies are all shared.)

What ExprsMeta handles specifically:

- ###doc; primary: attr formula, _C_, _CV_, as modified (lazily, not in here, due to inheritance, back and forward) _CK_,
  _TYPE_, _DEFAULT_

- what about _args and _options? Both of them are able to do things to attrs... ####k

- explain the problem w/ inheritance, back and forward; assert processed descriptors are class-unique whenever used ####DOIT


'''

###e nim or wrong as of 061024, also not yet used ####@@@@

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
