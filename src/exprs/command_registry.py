"""
command_registry.py

$Id$

register the types & commands [stub]
"""

###e THIS WILL BE REFACTORED before it is ever used, probably into a plain old dict, fully global for now, for the app object later,
# (later to be replaced by a kind of dict that can track its changes)
# plus per-module funcs to add things to that dict (modifying their source info as needed)
# plus code to extract useful summaries from it, eventually used to make demo_ui toolbars,
# but first just used to make a command menu of some sort.
# (Initially, we might deepcopy the dict into _app in order to notice when the whole thing changes,
#  like we do with redraw_counter.)

# but for now, here's the code we have for this, imported & partly called but not yet usefully used.

# ===

# do dir() and globals() correspond?? yes, both 1244.
## print "len dir() = %d, len(globals()) = %d" % (len(dir()), len(globals()))

# ==

class registry: #e rename?
    def __init__(self):
        self.class_for_name = {}
        #e that should also register this registry with a more global one!
    def register(self, name, val, warn_if_not_registerable = True ):
        "#doc ... by default, warn if val is not registerable due to lacking some required decls"
        # figure out the kind of class val is, by its decls, and register as appropriate
        print "nim: register %s = %r" % (name, val)
        # now record the interesting decls which let something know what to do with the class
        motopic = getattr(val, '_e_model_object_topic', None)

        ###WRONG: only do following if we decide val is registerable
        self.class_for_name[name] = val # stub [btw should we be a UserDict? that depends -- are we dictlike in any sensible way?]
        pass #stub
    def command_for_toolname(self, toolname): #e rename to say "main"?
        nim # not possible, for subtools... might work for main tools. not sure!
    def subtools_for_command(self, command): #e rename command -> main_command? (in method, not arg)
        nim
        # for subtools, the alg needs to be, figure out the set you want, get their nicknames, disambiguate or discard dups...
        # return a name list and name->cmd mapping, but the mapping is not determined just from self
        # even given the set of cmds in it or set of names in it, so no method can do what this one says (except for fullnames).
    pass

def auto_register( registry, namespace, modulename = None):
    """Register with registry every public name/value pair in namespace (typically, globals() for the calling module)
    whose value is a registerable class which (in standard attrs such as __module__)
    says it was defined in a module with the given (dotted) modulename (namespace['__name__'] by default,
     which means passing globals() of some module works as a way of providing that module's name [###explain this better]).
    (The precise comparison, for val being worth considering, is val.__module__ == modulename.)
    (A public name is a name that doesn't start with '_'.)
    (A registerable class is one of a set of certain kinds of subclass of InstanceOrExpr (basically, ones which
     define any of several known interfaces for self-registration) -- see code comments for details.)
    """
    if modulename is None:
        # assume namespace is globals() of a module
        modulename = namespace['__name__']
    for name in dir():
        if not name.startswith('_'):
            try:
                # see if it's a registratable class defined in this module
                val = globals()[name]
                if issubclass(val, InstanceOrExpr) and val.__module__ == modulename:
                    pass # register val in the else clause
                else:
                    assert 0
            except:
                ##raise
                pass ### this will happen a lot (since issubclass raises an exception for a non-class val)
            else:
                registry.register(name, val, warn_if_not_registerable = False )
                    # the flag says it's ok if 
        continue
    return

# end
