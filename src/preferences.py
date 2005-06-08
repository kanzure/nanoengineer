# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
preferences.py

Preferences system.

[This module is owned by Bruce until further notice.
It is likely to be revised heavily at any time.]

$Id$

==

Prototype for Alpha.

See lower-down docstrings for usage.

==

Should be used with bsddb,
but works without it too, after printing a warning.
The module bsddb is present in our standard installations
of windows and linux python, but not yet Mac python;
but we can add it, since it's easily available from

  http://undefined.org/python/pimp/darwin-7.0.0-Power_Macintosh.html

(package bsddb3 4.1.6)

BUT WE SHOULD LOOK INTO THE LICENSE TO MAKE SURE IT'S OK! ###@@@
(It probably is.)
"""

__author__ = "Bruce"

import os, sys, time
import platform

"""
Some internal & client-code documentation, as of 050106:

We store prefs in a shelf. Restrictions imposed by the shelve module:
Keys must be strings, values can be any pickleable python exprs,
and neither can be extremely long (exact limits are not made clear).

When these restrictions become a problem, we will make our intermediating
layer handle them (for example, by translating long keys to short ones).

==

Concurrent access:

We usually keep the shelf closed, in case other processes want to access or modify it too.
This only works if we assume that these processes only open it briefly when processing
some user event (typed command or clicked button), and this doesn't happen in two processes
at once since the user can only give events to one process at a time. For this reason,
it's important to only open it briefly during a user event (and only at the beginning
if the processing takes a long time), and never any other time!

Also, if you (a process) start another process which might access the prefs when it starts,
you should only access them yourself just before it starts (and during subsequent user events,
assuming that subprocess follows the same rule).

We rely on the client code to follow these rules; we don't try to enforce them.
Breaking them might conceivably trash the entire prefs database, or perhaps more likely,
cause an error in the process trying to access it while another process is doing so.
(This depends on the db module, and I don't know what bsddb does in this case.)

We make no attempt yet to handle these errors or back up the prefs database.

==

Internal shelf key usage:

Current internal shelf key usage (this might change at any time,
without the client-code keys changing):

Keys starting "k " are translated versions of client-code keys;
see internal _attr2key method (which will be renamed).

Keys starting '_' or with a digit are reserved for use by this code.
In fact, all other keys are reserved. Presently used: see the code.
The most important one is _format_version.

==

High-level keys and values:

Keys supplied by client code (translated through _attr2key into shelf keys)
are presently just strings, using conventions still mostly to be invented,
but in the future will be able to be more kinds of objects.

Values supplied by client code will in the future be translated, and have
metainfo added, but this is not yet done. Values must be pickleable, and
also should not include instances of classes until we decide which of
those are ok. (But Numeric arrays are ok.)

For now, all modules use the same global namespace of high-level keys,
but this might change. To permit this, the module defining the key
needs to be detectable by this code... basically this means any given key
should be passed into this module from the same external module.
Details to be documented when they are implemented and become relevant.

==

Usage by client code (for now -- this might change!):

  from preferences import prefs_context
  
  prefs = prefs_context()
  
  key = "some string" # naming conventions to be introduced later
  
  prefs[key] = value
  
  value = prefs[key] # raises KeyError if not there
  
  # these dict-like operations might or might not work
  # (not yet tested; someday we will probably suppport them
  # and make them more efficient than individual operations
  # when several prefs are changed at once)
  
  prefs.get(key, defaultvalue)
  
  prefs.update(dict1)
  
  dict1.update(prefs)

"""

# ===

# This module wants bsddb, just to make sure the shelf is stored in a format
# that (we hope) all platforms can open. (It also might be more reliable,
# be better at concurrent access, and/or permit longer keys and (especially)
# values than other db packages.)

# But, we'll run without it, but use a different
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

# And this module requires shelve. We assume without checking that if bsddb is available,
# shelve will use it. (I don't know any straightforward way to check this. But the
# docs for shelve say it will use it, I think. #k check this ###@@@)

import shelve

# (For the actual filename of the prefs file, see the code of _make_prefs_shelf()
#  below, which specifies the basename only; the db module decides what extension
#  to add. This is one reason we store the prefs in a subdirectory.)

# ===

_shelfname = _shelf = _cache = None

def _make_prefs_shelf():
    """[private function]
    call this once per session,
    to create or find the shelf (whose name depends only on the dbm format we'll use for it),
    and create the cache of its contents,
    and store a comment there about this process,
    and close the shelf again in case a concurrent process is sharing the same shelf with us.
    """
    global _shelfname, _shelf, _cache
    nanorex = platform.find_or_make_Nanorex_directory()
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
    # zap obsolete contents
    obskeys = []
    for key in _cache.keys():
        if key.isdigit() or key in ['_session_counter']:
            obskeys.append(key)
    for key in obskeys:
        del _shelf[key]
        del _cache[key]
    ###@@@ following should be revised to handle junk contents gracefully,
    # and to notice the existing format version and handle older formats appropriately
    # or reject them gracefully.
    _store_while_open('_format_version', 'preferences.py/v050106')
        # storing this blindly is only ok since the only prior version is one
        # we can transparently convert to this one by the "zap obskeys" above.
    
    # store a comment about the last process to start using this shelf
    # (nothing yet looks at this comment)
    proc_info = "process: pid = %d, starttime = %r" % (os.getpid(), time.asctime())
    _store_while_open( '_fyi/last_proc', proc_info ) # (nothing yet looks at this)
    _close()
    return

def _close():
    global _shelf
    _shelf.close()
    _shelf = None
    return

def _reopen():
    _ensure_shelf_exists()
    global _shelf
    assert _shelf is None
    _shelf = shelve.open(_shelfname)
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

# ==

# Now make a prefs function, which returns a prefs object [someday] customized for the calling module,
# in which prefs can be accessed or stored using attributes, whose names are interpreted in a context
# which might differ for each module.

class _prefs_context:
    """Represents a symbol context for prefs names, possibly [someday] customized for one module.
    """
    def __init__(self, modname):
        # modname is not presently used
        _ensure_shelf_exists() # needed before __getattr__ and __getitem__ are called
    def _attr2key(self, attr):
        return "k " + attr # stub! (i guess)
    #e Someday we will support more complex keys,
    # which are like exprs whose heads (at all levels) are in our context.
    # For now, just support arbitrary strings as items.
    def __setitem__(self, key, val):
        assert type(key) == type("a") # not unicode, numbers, lists, ... for now
        pkey = self._attr2key(key) # but we might use a more general func for this, at some point
        if _shelf:
            _shelf[pkey] = _cache[pkey] = val
        else:
            try:
                _reopen()
                _shelf[pkey] = _cache[pkey] = val
            finally:
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
    def get(self, key, dflt = None): #bruce 050117
        #e probably i can replace this by something like DictMixin...
        try:
            return self[key]
        except KeyError:
            return dflt
        pass
    def update(self, dict1): #bruce 050117
        # note: unlike repeated setitem, this only opens and closes once.
        if _shelf:
            for key, val in dict1.items():
                #e (on one KeyError, should we store the rest?)
                #e (better, should we check all keys before storing anything?)
                self[key] = val #e could optimize, but at least this leaves it open
        else:
            try:
                _reopen()
                self.update(dict1)
            finally:
                _close()
        return
        
    pass # end of class _prefs_context

# for now, in this stub code, all modules use one context:
_global_context = _prefs_context("allmodules")

def prefs_context():
    ###@@@ stub: always use the same context, not customized to the calling module.
    return _global_context


'''
use this like:

prefs = prefs_context() # once per module which uses it (must then use it in the same module)

... prefs['atom_debug'] = 1

... if prefs['atom_debug']:
        ...

or make up keys as strings and use indexing, prefs[key],
but try to compute the strings in only one place
and use them from only one module.

We will gradually introduce naming conventions into the keys,
for example, module/subname, type:name. These will be documented
once they are formalized.

[these rules might be revised!]
'''

# == test code (very incomplete)

if __name__ == '__main__':
##    defaults = dict(hi=2,lo=1)
##    print "grabbing %r, got %r" % (defaults, grab_some_prefs_from_cache(defaults))
##    new = dict(hi = time.asctime())
##    print "now will store new values %r" % new
##    store_some_prefs(new)
##    print "now we grab in same way %r" % grab_some_prefs_from_cache(defaults) # this failed to get new value, but next proc gets it
##    print "done with this grossly incomplete test; the shelfname was", _shelfname

    # now try this:
    testprefs = prefs_context()
    testprefs.x = 7
    print "should be 7:",testprefs.x
    
# end