# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
preferences.py

Preferences system.

[This module is owned by Bruce until further notice.
It is likely to be revised heavily at any time.]

Prototype for Alpha. Should be used with bsddb,
but works without it too, after printing a warning.
The module bsddb is present in our standard installations
of windows and linux python, but not yet Mac python;
but we can add it, since it's easily available from

  http://undefined.org/python/pimp/darwin-7.0.0-Power_Macintosh.html

(package bsddb3 4.1.6)

BUT WE SHOULD LOOK INTO THE LICENSE TO MAKE SURE IT'S OK! ###@@@
(It probably is.)

$Id$
'''

__author__ = "Bruce"

import os, sys, time
import platform

# We store prefs in a shelf. Restrictions imposed by the shelve module:
# Keys must be strings, values can be any pickleable python exprs,
# and neither can be extremely long (exact limits are not made clear).
#
# ###@@@ STUB CODE below tries to store other keys too... we'll repr them. ###FIX DOC FOR THIS
#
# Keys which are strings or numbers are reserved for private use by this module --
# specifically, numbers, and strings starting '_', have special meanings,
# and other strings are junk used for "comments in the file" or testing.
#
# "Official" preferences (seen by code outside this module) have keys and values
# which are translated into other forms by this module. The keys are turned into
# lists of numbers or strings, in a way which avoids collisions from reuse of
# symbols in different contexts (details to be determined, but basically, each
# module says which version of each key it uses, for any key for which it doesn't
# use the first-ever version of its meaning, over all modules in one product).
#
# The values are used unchanged, but we add metainfo (modtime, etc) to what we store.
# (Details also to be determined.)

# ===

# This package wants bsddb, just to make sure the shelf is stored in a format
# that (we hope) all platforms can open. But, we'll run without it, but use a different
# shelf name, in case the binary formats are incompatible. (Not a perfect solution,
# since there's no guarantee the db format without bsddb is always the same...
# but I don't know a good-enough way to find out which db module shelve is actually using.)

try:
    import bsddb as _junk
except:
    dbname = "somedb"
    print """\
Warning: import bsddb failed; using some other db format for preferences file;
 giving it a different name in case that uses an incompatible binary format;
 this means, when you upgrade to bsddb, you'll lose your preferences.
"""
else:
    dbname = "bsddb"

# And it requires shelve. We assume without checking that if bsddb is available,
# shelve will use it. (I don't know any straightforward way to check this. But the
# docs for shelve say it will use it, I think. ###k check this ###@@@)

import shelve

# for the actual filename of the prefs file,
# see the code of _make_prefs_shelf() below.

# ===

_shelfname = _shelf = _cache = _session_counter = None

def _make_prefs_shelf():
    """[private function]
    call this once per session,
    to create or find the shelf (whose name depends only on the dbm format we'll use for it),
    and create the cache of its contents,
    and choose a unique serial number to identify this session within that shelf,
    and store our info there,
    and close the shelf again in case a concurrent process is sharing the same shelf with us.
    """
    global _shelfname, _shelf, _cache, _session_counter, _proc_info
    nanorex = platform.find_or_make_Nanorex_prefs_directory()
    global dbname
    _shelfname = os.path.join( nanorex, "Preferences", "%s-shelf" % dbname )
        # This name should differ when db format differs.
        # Note: the actual filename used might have an extension added
        # by the db module (in theory, it might even create two files
        # with different extentions from the given basename).
        # By experiment, on the Mac, with bsddb there is no extension added,
        # and without it there is '.db' added. [bruce 050105]
    platform.mkdirs_in_filename(_shelfname)
    _shelf = shelve.open(_shelfname)
    _cache = {}
    _cache.update(_shelf) # will this work?
    ###@@@ following should be revised to handle junk contents gracefully,
    # and to store a format version in the shelf (not using one of an older format).
    if not _cache:
        # it's empty; presumably we are its creator (unless two processes are started at the same time)
        ## print "empty shelf"
        _session_counter = 1
    else:
        ## print "shelf contents:"
        ## print _cache
        try:
            _session_counter = _cache['_session_counter']
                # this is 1 or more, and always the most recent process to register in the shelf
            assert type(_session_counter) == type(1)
            otherguy_info = _cache[`_session_counter`]
            _session_counter += 1 # this will be our unique serial number in this shelf
        except:
            print "shelf error, unable to handle it:" #e this is not good, it means crashes destroy your shelf,
            # might as well remove it and start over... ###@@@
            raise # for now
    # now _session_counter is our unique serial number in this shelf, should not be in use
    _proc_info = "process: pid = %d, starttime = %r" % (os.getpid(), time.asctime()) ###@@@stub; should generalize the format
    _store_new_while_open( `_session_counter`, _proc_info )
    _store_while_open( '_session_counter', _session_counter )
    _close()
    return

# We usually keep the shelf closed, in case other processes want to access or modify it too.
# This only works if we assume that these processes only open it briefly when processing
# some user event (typed command or clicked button), and this doesn't happen in two processes
# at once since the user can only give events to one process at a time. For this reason,
# it's important to only open it briefly during a user event, and never any other time!
# We rely on the client code to follow this rule.

def _close():
    global _shelf
    _shelf.close()
    _shelf = None
    return

def _reopen():
    _ensure_shelf_exists()
    global _shelf
    assert _shelf == None
    _shelf = shelve.open(_shelfname)
    assert _proc_info == _shelf[`_session_counter`]
    # don't bother to re-update our _cache! This would be too slow to do every time.
    return

def _store_new_while_open(key, val):
    assert not _shelf.has_key(key) # checks _shelf, not merely _cache
    assert not _cache.has_key(key)
    _cache[key] = val
    _shelf[key] = val
    return

def _store_while_open(key, val):
    # don't assert _cache and _shelf are the same at this key -- it's not an error if they are not,
    # or if shelf has a value and cache does not, since a concurrent process is allowed to write
    # a prefs value on its own.
    _cache[key] = val
    _shelf[key] = val
    return

def _ensure_shelf_exists():
    if not _shelfname:
        _make_prefs_shelf()
    return

# == semi-public functions; these work whether or not the shelf is open
# (or has ever been created), and leave it open or closed as they found it;
# but (for now) they use raw shelf keys and values.
# Later (or sooner) we will add an intermediate layer which uses higher-level
# keys and values, includes modtimes and symbol contexts, etc. ##e

def store_some_prefs(dict1):
    "store the prefs in dict1, overwriting existing prefs if needed"
    _ensure_shelf_exists()
    if not _shelf:
        _reopen()
        assert _shelf # won't infrecur
        store_some_prefs(dict1)
        _close()
    else:
        _cache.update(dict1)
        _shelf.update(dict1)
        _assert_shelf_matches(dict1) # only for debug ###@@@ remove when works
    return

def _assert_shelf_matches(dict1):
    for key, val in dict1.items():
        assert _shelf[key] == val
    return

def _grab_from_dict(dict1, dict2):
    "return a dict with same keys as dict1, but values taken from dict2, using dict1 values as defaults"
    res = dict(dict1) # res has same values as dict1 by default, and same keys always
    for key in dict1.keys():
        try:
            val = dict2[key] # bug: i was setting dict1[key]!!! ###@@@
        except KeyError:
            pass
        else:
            res[key] = val            
    return res

def grab_some_prefs_from_cache(dict1):
    "return a new dict with the same keys as in dict1, but with values taken from the cache"
    _ensure_shelf_exists() # at least init the cache from the shelf, first!
    return _grab_from_dict(dict1, _cache)

def grab_some_prefs_from_shelf(dict1):
    # use this when _shelf might be newer than _cache and we need to update the _cache for this
    if not _shelf:
        _reopen()
        assert _shelf # won't infrecur
        res = grab_some_prefs_from_shelf(dict1)
        _close()
    else:
        res = _grab_from_dict(dict1, _shelf)
        _cache.update(res)
    return res

# ==

# Now make a prefs function, which returns a prefs object customized for the calling module,
# in which prefs can be accessed or stored using attributes, whose names are interpreted in a context
# which might differ for each module.

class _prefs_context:
    """Represents a symbol context for prefs names, possibly customized for one module.
    This is an object in which arbitrary client-code-defined attrs (not starting with '_')
    can be used, so all its own methods and attrs should start with '_'!
    """
    def __init__(self, modname):
        self._modname = modname # module name [is this needed?]
        _ensure_shelf_exists() # needed before __getattr__ and __getitem__ are called
    def _attr2key(self, attr):
        return "k " + attr # stub! (i guess)
    def __getattr__(self, attr):
        if attr.startswith('_'):
            # this happens often, for many attrnames like __xxx__
            raise AttributeError, attr
        # Grab the pref referred to by this attr in this context.
        # If it does not exist, raise AttributeError.
        # (Or can a default value for it have been stored separately, somehow?? ###e)
        #e In future we might record prefs usage here...
        pkey = self._attr2key(attr)
        try:
            return _cache[pkey]
        except KeyError:
            ## don't do this: try: val = _shelf[pkey] # maybe some other process stored it in the meantime...
            ## reason: having no value is like a value, should not be changed unless we update...
            ## (I'm not sure if this is right ###@@@)
            raise AttributeError, attr
        pass
    def __setattr__(self, attr, val):
        if attr.startswith('_'):
            # this can happen for _modname, for example!
            ## print "prefs context got __setattr__ for %r: can this ever happen?" % attr
            self.__dict__[attr] = val
            return
        pkey = self._attr2key(attr)
        if _shelf:
            _shelf[pkey] = _cache[pkey] = val
        else:
            _reopen()
            _shelf[pkey] = _cache[pkey] = val
            _close()
        return
    #e we might also provide getitem and setitem, for more complex keys,
    # which are like exprs whose heads (at all levels) are in our context.
    # For now, just support strings as items, the same ones as for attrs,
    # but also arbitrary strings whether or not they start with '_',
    # contain spaces, etc.
    def __setitem__(self, key, val):
        assert type(key) == type("a") # not unicode, numbers, lists, ... for now
        pkey = self._attr2key(key) # but we might use a more general func for this, at some point
        if _shelf:
            _shelf[pkey] = _cache[pkey] = val
        else:
            _reopen()
            _shelf[pkey] = _cache[pkey] = val
            _close()
        return
    def __getitem__(self, key):
        assert type(key) == type("a")
        pkey = self._attr2key(key)
        try:
            return _cache[pkey]
        except KeyError:
            raise KeyError, key # not pkey like the exception we're catching!
        pass
    pass # end of class _prefs_context

# for now, in this stub code, all modules use one context:
_global_context = _prefs_context("allmodules")

def prefs_context():
    ###@@@ stub: always use the context for *this* module. Or, just always use the same context, not for any module.
    modname = __name__ # in reality, get this from a code object on the stack
    module = sys.modules[modname]
    # now figure out the context for that module...
    context = _global_context
    return context

'''
use this like:

prefs = prefs_context() # once per module which uses it (must then use it in the same module)

... prefs.atom_debug = 1

... if prefs.atom_debug:
        ...

or make up keys as strings and use indexing, prefs[key],
but in this case try to compute the strings in only one place
and use them from only one module.

[these rules might be revised!]
'''

# == test code (very incomplete)

if __name__ == '__main__':
    defaults = dict(hi=2,lo=1)
    print "grabbing %r, got %r" % (defaults, grab_some_prefs_from_cache(defaults)) ###@@@ somehow this defaults dict got modified!
        # i must have a logic bug in which i update the wrong one, and that might be cause of the other bug as well. ###@@@
    new = dict(hi = time.asctime())
    print "now will store new values %r" % new
    store_some_prefs(new)
    print "now we grab in same way %r" % grab_some_prefs_from_cache(defaults) # this failed to get new value, but next proc gets it
    print "done with this grossly incomplete test; the shelfname was", _shelfname

    # now try this:
    testprefs = prefs_context()
    testprefs.x = 7
    print "should be 7:",testprefs.x
    
# end
