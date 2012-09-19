# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
py_utils.py

$Id$


simple utility functions for python built-in types
"""

# note: the module basic.py imports * from this module.

class attrholder: pass

def identity(arg):
    return arg

def interleave(elts, gaps):
    """Return an interleaved list of the given elements and gaps --
    e.g. elt[0] gap[0] elt[1] gap[1] elt[2], for 3 elts and 2 gaps.
    (Error if input list lengths are not properly related; special case for no elts.)
    """
    if len(elts) <= 1: # btw, code below would also work for len(elts) == 1
        assert not gaps
        return elts
    assert len(gaps) + 1 == len(elts)
    def elt_or_gap(i):
        if i % 2 == 0:
            return elts[i / 2]
        else:
            return gaps[int(i / 2)]
    return map(elt_or_gap, range(len(elts) + len(gaps)))

def interleave_by_func(elts, gapfunc):
    gaps = [gapfunc(e1,e2) for e1,e2 in zip(elts[:-1],elts[0:])]
    return interleave(elts, gaps)

def dict_ordered_values(d1): ##e rename (this name 'dict_ordered_values' is completely unrecallable) #e see also sorted_items
    "Return the values of the given dict, sorted by their key in the dict. [see also sorted_items]"
    items = d1.items()
    items.sort()
    return [v for (k,v) in items]

def sorted_items(d1): #070312
    "Return a list of all (key, value) pairs in the given dict, sorted by dict key. [see also dict_ordered_values]"
    items = d1.items()
    items.sort()
    return items

def sorted_by(seq, func): #070206 ##e do I have this under some other name, somewhere?
    "return the elements of the given sequence, sorted by func(element)"
    items = [(func(elt), elt) for elt in seq]
    items.sort()
    return [elt for (f, elt) in items]

from foundation.env import seen_before # public in this module

def printonce(msg, constpart = None):
    """print msg (which should be a constant), but only once per session.
    If msg is *not* a constant, pass its constant part (a nonempty string --
    not checked, bad errors if violated) in constpart.
       WARNING: If you pass nonconstant msg and forget to pass constpart, or if constpart is nonconstant or false,
    this might print msg on every call!
       WARNING: Nonconstant args can be a slowdown, due to the time to evaluate them before every call.
    Passing constpart can't help with this (of course), since all args are always evaluated.
    Consider direct use of env.seen_before instead.
    """
    constpart = constpart or msg
    if not seen_before(constpart):
        print msg
    return

printnim_enabled = False # 061114 -> False; turn on again when I feel like cleaning a lot of them up

def printnim(msg, constpart = None):
    if printnim_enabled:
        printonce("nim reminder: " + msg, constpart)
    return

def printfyi(msg, constpart = None):
    printonce("fyi (printonce): " + msg, constpart)
    return

def stub(*args, **kws): #e rename to stubfunc (too hard to search for 'stub', common in comments)
    assert 0, "stub called"

class MemoDict(dict): #k will inherit from dict work? ###e rename to extensibledict?? -- it doesn't have to memoize exactly...
    """Act like a transparently extensible dict,
    given a way to compute a new element (which we'll memoize) from the dict key;
    this way MUST NOT USE USAGE-TRACKED LVALS (WARNING: this error is not yet detected [actually I think it is, now]).
    (If you wish there was usage-tracking and update, see LvalDict2, or a proposed RecomputingMemoDict, in other files.)
    WARNING: typical uses are likely to involve cyclic refs, causing memory leaks.
    """
    ###e should provide an optional argfunc to canonicalize the key before using it to look up or call the wayfunc
    # (for use in texture_holder_for_filename in images.py) [061125 comment]
    def __init__(self, way):
        self._way = way
        dict.__init__(self)
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            import foundation.changes as changes
            mc = changes.begin_disallowing_usage_tracking(self) # note: argument is just explanation for use in error messages
            try:
                val = self._way(key)
                    # note, it needs to be legal for something during this to reallow using tracking for itself, locally
            except:
                # try not to hurt this object for use at other keys, but good to reraise exception to whoever accessed this key
                # (maybe something's wrong with this key, but good even if not, i think [061121])
                # Note: the exception might be an error being reported by begin_disallowing_usage_tracking!
                # So we should do the ending of that disallowing -- the initial raising of that exception should not do it.
                changes.end_disallowing_usage_tracking(mc)
                raise
            else:
                changes.end_disallowing_usage_tracking(mc)
                dict.__setitem__(self, key, val)
                return val
        pass
    pass # end of class MemoDict

def union(A,B): #k does this override anything that's standard in python? if so, rename it, perhaps to dict_union
    #note: presumably useful, but not yet used; may never end up being used.
    """Union, for sets represented as dicts from k to k,
    or (if you prefer) from k to f(k), for any pure function f
    (which need not be deterministic, and can even be entirely arbitrary).
       For even more general uses, we guarantee:
    when k occurs in both inputs, the value f(k) comes from B.
    But we might remove this guarantee as an optim, someday, so uses should comment if they depend on it
    (or should use an alias to this function, which carries a permanent guarantee #e).
       [It would be good if we could use some form of hashable (finalized or immutable) dict... #e]
    """
    # note: we might use this for tracking sets of free variables in exprs.
    if A:
        if B:
            #e is it worth optimizing for both len 1 and same key? note, it reduces memory usage w/o interning.
            #e relatedly: we could order them by len, check for subsetness.
            res = dict(A)
            res.update(B)
            #e intern res? this could help in making these sets hashable (usable as dict keys),
            # esp. if the result of interning was just a number, able to be looked up to get the dict...
            # it could be a serno, or actually a bitmap of the elements, permitting bitwise Or as union
            # (for uses in which the universe of all elements used in any set is very small,
            #  as will often be true for "free variables in exprs").
            return res
        else:
            return A
    else:
        return B
    pass

class delegated_state_attr(object): # 070103, moved from GLPane_overrider.py 070104
    """A descriptor (like a property) which delegates get and set of an attr into another object found at a specified attrpath.
    For example, to delegate self.quat to self.delegate.quat (for get and set), use
      quat = delegated_state_attr('delegate', 'quat')
    """
    def __init__(self, *attrpath):
        self.path_to_obj = tuple(attrpath[0:-1])
        self.attr = attrpath[-1]
        assert self.path_to_obj + (self.attr,) == attrpath
    def find_obj(self, obj):
        assert obj is not None
        for attr in self.path_to_obj:
            obj = getattr(obj, attr)
        return obj
    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj = self.find_obj(obj)
        attr = self.attr
        return getattr(obj, attr)
    def __set__(self, obj, val):
        if obj is None:
            return
        obj = self.find_obj(obj)
        attr = self.attr
        setattr(obj, attr, val)
        return
    pass

# end
