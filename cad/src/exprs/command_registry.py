# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
command_registry.py

$Id$

register the types & commands [stub]
"""

from exprs.instance_helpers import InstanceOrExpr

###e THIS WILL BE REFACTORED before it is ever used, probably into a plain old dict, fully global for now, for the app object later,
# (later to be replaced by a kind of dict that can track its changes)
# plus per-module funcs to add things to that dict (modifying their source info as needed)
# plus code to extract useful summaries from it, eventually used to make demo_ui toolbars,
# but first just used to make a command menu of some sort.
# (Initially, we might deepcopy the dict into _app in order to notice when the whole thing changes,
#  like we do with redraw_counter.)


#e can't we just make a tree of exprs which do things like union some dicts and modify nicknames for uniqueness?
# then each module just sets the value of its own dict of names...
# and a recompute rule figures out what that means for the toplevel summary...

# ==

# but for now, here's the code we have for this, imported & partly called but not yet usefully used.

# do dir() and globals() correspond?? yes, both 1244.
## print "len dir() = %d, len(globals()) = %d" % (len(dir()), len(globals()))

# ==

class CommandRegistry: #e rename?
    def __init__(self):
        self.class_for_name = {}
        #e that should also register this registry with a more global one!
    def register(self, name, val, warn_if_not_registerable = True ):
        "#doc ... by default, warn if val is not registerable due to lacking some required decls"
        # figure out the kind of class val is, by its decls, and register as appropriate
        # print "nim: register %s = %r" % (name, val) # this gets called for what's expected, e.g. CommandWithItsOwnEditMode
        # now record the interesting decls which let something know what to do with the class
        motopic = getattr(val, '_e_model_object_topic', None)

        ###WRONG: only do following if we decide val is registerable
        self.class_for_name[name] = val # stub [btw should we be a UserDict? that depends -- are we dictlike in any sensible way?]
        pass #stub
    def command_for_toolname(self, toolname): #e rename to say "main"?
        assert 0 # nim # not possible, for subtools... might work for main tools. not sure!
    def subtools_for_command(self, command): #e rename command -> main_command? (in method, not arg)
        assert 0 # nim
        # for subtools, the alg needs to be, figure out the set you want, get their nicknames, disambiguate or discard dups...
        # return a name list and name->cmd mapping, but the mapping is not determined just from self
        # even given the set of cmds in it or set of names in it, so no method can do what this one says (except for fullnames).
    pass

def auto_register( namespace, registry = None, modulename = None): ###e this function needs a more explicit name
    """###doc this better -- it's correct and complete, but very unclear:
    Register with registry (or with a global registry, if registry arg is not provided)
    every public name/value pair in namespace (typically, globals() for the calling module)
    whose value is a registerable class which (according to standard attrs such as __module__)
    says it was defined in a module with the given (dotted) modulename (namespace['__name__'] by default).
    This means that passing globals() of some module works as a way of providing that module's name.
    (The precise comparison, for val being worth considering, is val.__module__ == modulename.)
    (A public name is a name that doesn't start with '_'.)
    (A registerable class is one of a set of certain kinds of subclass of InstanceOrExpr (basically, ones which
     define any of several known interfaces for self-registration) -- see code comments for details.)
    """
    #e permit namespace to be a list of names instead? but how would they be looked up? add another arg for the names?
    if modulename is None:
        # assume namespace is globals() of a module
        modulename = namespace['__name__']
    # print "auto_register, modulename = %r" % (modulename,)
    if registry is None:
        registry = find_or_make_global_command_registry()
    for name in namespace.keys():
        if not name.startswith('_'):
            wantit = False # set to True if name names a registratable class defined in the namespace (not just imported into it)
            try:
                val = 'bug' # for error message, in case of exception
                val = namespace[name] # should not fail
                if issubclass(val, InstanceOrExpr) and val.__module__ == modulename: # often fails for various reasons
                    wantit = True
            except:
                if 'Polyline' in name:
                    raise ####### show silly bugs like not importing InstanceOrExpr
                pass # note: this will happen a lot (since issubclass raises an exception for a non-class val)
            if wantit:
                registry.register(name, val, warn_if_not_registerable = False )
            else:
                if 'Polyline' in name:
                    print "not registering %r = %r" % (name,val,) #####
            pass
        continue
    return

# ==

def find_or_make_global_command_registry( remake = False ):
    """[with remake = True: to be called once per session, or per reload of exprs module; with it False - call as needed to find it]
    ###doc
    """
    # it doesn't really matter where we store __main__._exprs__registry --
    # a global in this module might make more sense, if reload issues are ok ... #k
    import __main__
    if remake:
        __main__._exprs__registry = None
        del __main__._exprs__registry
    try:
        return __main__._exprs__registry
    except AttributeError:
        __main__._exprs__registry = CommandRegistry()
        return __main__._exprs__registry
    pass

# end
