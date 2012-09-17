# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
intern_ipath.py

$Id$

For now, this module doesn't officially support reload, though doing so won't erase its database --
since it might mix interned values with different intern-mappings into one database.
So basic.py doesn't try to reload it.
"""

# This may be refiled or renamed, since later we'll also intern exprs,
# and maybe not the same exact way. Maybe there can be interning objects of which these globals become members
# and two public ones for exprs and ipaths, and some using on-disk dbs too.

try:
    _uninterned_from_interned
except:
    # interning data is preserved across reloads [however, for now this module doesn't officially support reload at all]
    _uninterned_from_interned = {}
    _interned_from_uninterned = {}
    _next_interned_ipath = -101

assert len(_uninterned_from_interned) == len(_interned_from_uninterned) == (-101 - _next_interned_ipath)

# The map from uninterned to interned will be
#   int (always nonnegative in a fully uninterned ipath) -> itself
#   string or None or boolean -> itself
#   tuple -> intern the components, then allocate a negative int (less than -100); dict key is tuple of 0 or more ints and strings
#
# The inverse map is:
#   negative int -> through the dict
#   positive int or string or None or boolean -> itself
#
# Client code is free to mix uninterned and interned ipaths at will. [##doc this publicly]
#
# (The only overlap in the set of legal values comes from ipaths whose uninterned and interned forms are the same,
#  so this is unambiguous. To ignore the issue of overlap when wondering if an ipath is interned or not when it
#  could be either, think of strings and nonneg ints and None as "already interned".)
#
# One way this interning strategy could fail is if the common parts of ipaths in the form of (first, rest) tuple-linked-lists
# (innermost path component first) tend to be long sections of innermost components. Nothing will seem to be in common if the
# outermost components are unique.

# ==

#e the set of functions defined here (as an API into this module) may not be well-chosen.

def is_interned(ipath):
    "is ipath a legal interned ipath value? True if yes, False if no, exception if illegal as uninterned or interned ipath."
    if type(ipath) == type(0):
        if not (ipath < -100 or ipath >= 0):
            print "ERROR: this int is not allowed as an ipath:",ipath # not an assert in case someone uses -1 -- we'll change spec if so
        return True # true either way: < -100 is an interned tuple, >= 0 is an interned int
    if type(ipath) in (str, bool):
        return True
    if ipath is None:
        return True
    if type(ipath) == type(()):
        return False # in this case we don't bother checking element legality -- it'll happen if caller goes on to intern it
    assert 0, "wrong type for ipath, whether or not interned; object is %r" % (ipath,)
    pass

def _find_or_make_interned_ipath(ipath):
    "assume it's an uninterned tuple, but with all interned parts -- maybe not checked!"
    if 'check for now, remove when works':
        assert type(ipath) == type(())
        for elt in ipath:
            assert is_interned(elt)
    # find
    try:
        return _interned_from_uninterned[ ipath]
    except KeyError:
        pass
    # make
    global _next_interned_ipath
    interned = _next_interned_ipath
    _next_interned_ipath -= 1 # note the sign -- they grow down
    _uninterned_from_interned[ interned] = ipath
    _interned_from_uninterned[ ipath] = interned
    return interned

def intern_ipath(ipath):
    """Change ipath (hashable python data made of tuples, strings, ints, bools) into something shorter, but just as unique,
    which can't imitate an original (uninterned) one. To do this, use private knowledge about which ints and strings
    can be present in an original one. Be idempotent if ipath is already interned.
    """
    if is_interned(ipath):
        return ipath
    assert type(ipath) == type(())
    parts = map(intern_ipath, ipath)
    ipath = tuple(parts)
    return _find_or_make_interned_ipath(ipath)

# end

