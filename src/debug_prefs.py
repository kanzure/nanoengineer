# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
debug_prefs.py

Some prototype general-prefs code, useful now for "debugging prefs",
i.e. user-settable temporary flags to help with debugging.

$Id$
'''

__all__ = ['debug_pref', 'Choice', 'debug_prefs_menuspec'] # funcs to declare and access prefs; datatypes; UI funcs for prefs

__author__ = "bruce" # 050614

from constants import noop

debug_prefs = {} # maps names of debug prefs to "pref objects"

def debug_pref(name, dtype):
    """Public function for declaring and registering a debug pref and querying its value.
       Example call: chem.py rev 1.151 (might not  be present in later versions).
       Details: If debug_prefs[name] is known (so far in this session),
    return its current value, and perhaps record the fact that it was used.
       If it's not known, record its existence in the list of active debug prefs
    (visible in a submenu of the debug menu [#e and/or sometimes on the dock])
    and set it to have datatype dtype, with an initial value of dtype's default value.
    (And then record usage and return value, just as in the other case.)
       Possibly, arrange to store changes to its value in user prefs,
    and to use user-prefs value rather than default value when creating it.
    """
    if not debug_prefs.has_key(name):
        debug_prefs[name] = DebugPref(name, dtype)
    return debug_prefs[name].current_value()

class Pref:
    "Pref objects record all you need to know about a currently active preference setting"
    #e for now, just within a session
    def __init__(self, name, dtype):
        #e for now, name is used locally (for UI, etc, and maybe for prefs db);
        # whether/how to find this obj using name is up to the caller
        self.name = name
        self.dtype = dtype # a DataType object
        self.value = dtype.default_value()
    def current_value(self):
        return self.value
    def changer_menuspec(self):
        """return a menu_spec suitable for including in some larger menu (as item or submenu is up to us)
        which permits this pref's value to be seen and/or changed;
        how to do this depends on datatype (#e and someday on other prefs!)
        """
        def newval_receiver_func(newval):
            assert newval in self.dtype.values, "illegal value for %r: %r" % (self, newval)
                ###e change to ask dtype, since most of them won't have a list of values!!! this method is specific to Choice.
            self.value = newval
            print "changed %r to %r" % (self, newval) ###e should only print for debug prefs!
        return self.dtype.changer_menuspec(self.name, newval_receiver_func, self.current_value())
    def __repr__(self):
        return "<Pref %r at %#x>" % (self.name, id(self))
    pass

class DebugPref(Pref):
    pass

# == datatypes

class DataType:
    def short_name_of_value(self, value):
        return self.name_of_value(value)
    pass

def autoname(thing):
    return `thing` # for now

class Choice(DataType):
    "DataType for a choice between one of a few specific values, perhaps with names and comments and order and default"
    def __init__(self, values = None, names = None, names_to_values = None):
        #e names_to_values should be a dict from names to values; do we union these inits or require no redundant ones? Let's union.
        if values is not None:
            values = list(values) #e need more ways to use the init options
        else:
            values = []
        if names is not None:
            assert len(names) <= len(values)
            names = list(names)
        else:
            names = []
        while len(names) < len(values):
            i = len(names) # first index whose value needs a name
            names.append( autoname(values[i]) )
        if names_to_values:
            items = names_to_values.items()
            items.sort()
            for name, value in items:
                names.append(name)
                values.append(value)
        self.names = names
        self.values = values
        #e nim: comments, default
        self._default_value = self.values[0]
        self.values_to_comments = {}
        self.values_to_names = {}
        for name, value in zip(self.names, self.values):
            self.values_to_names[value] = name
    def name_of_value(self, value):
        return self.values_to_names[value]
    def default_value(self):
        return self._default_value
    def changer_menuspec( self, instance_name, newval_receiver_func, curval = None):
        #e could have special case for self.values == [True, False] or the reverse
        text = "%s: %s" % (instance_name, self.short_name_of_value(curval))
        submenu = []
        for name, value in zip(self.names, self.values):
            submenu.append(( name,
                             lambda event = None, func = newval_receiver_func, val = value: func(val),
                             (curval == value) and 'checked' or None
                            ))
        return ( text, submenu )
    pass

# ==

def debug_prefs_menuspec():
    "Return a single menu item (as a menu_spec tuple) usable to see and edit settings of all active debug prefs."
    text = "debug prefs submenu"
    submenu = []
    items = debug_prefs.items()
    items.sort()
    for name, pref in items:
        submenu.append( pref.changer_menuspec() )
    if submenu:
        return ( text, submenu)
    return ( text, noop, "disabled" )

# == test code

if __name__ == '__main__':
    spinsign = debug_pref("spinsign",Choice([1,-1]))
    print debug_prefs_menuspec()
    
# end
