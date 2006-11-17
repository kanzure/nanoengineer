"""
staterefs.py - facilities for defining and referencing state,
in widget exprs which display it, edit it, operate on it, produce it

$Id$
"""

from basic import * # all we really need is call_Expr & InstanceOrExpr, so far.
from basic import _self
    #k [digr: is there a reload bug caused by things we get from basic import *, since we don't reload basic??]

def StatePlace(kind, ipath_expr = _self.ipath): # experimental, but used and working in Highlightable; related to Arg/Option/Instance
    """In a class definition for an InstanceOrExpr subclass, use the assignment

        <kind>_state = StatePlace(<kind>, <ipath_expr>)

    (for a short string <kind>, usually one of a small set of conventional kinds of storage)
    to cause self.<kind>_state in each Instance to refer to external state specific to
    <ipath_expr> as evaluated in that Instance (by default, _self.ipath, meaning specific
    to that Instance, though usually more persistent than it, perhaps depending on <kind>).

    [Believe it or not, that docstring is a lot clearer than it was before... but I think it
    still has a long way to go.]
    
       StatePlace() works by turning into a formula which will eval to a permanent reference
    to a (found or created) attrholder for storing state of the given kind, at the given ipath
    (value of ipath_expr), relative to the env of the Instance this is used in (i.e. to _self.env).

       It's usually necessary to initialize the contents of the declared stateplaces
    using set_default_attrs in _init_instance, or the like. (Note that the stateplace is often
    found rather than created, and the same sometimes goes for individual attrs within it.
    Both this declaration and set_default_attrs take this into account by only initializing
    what's not already there.)
    """
    return call_Expr( _StatePlace_helper, _self, kind, ipath_expr )

def _StatePlace_helper( self, kind, ipath): # could become a method in InstanceOrExpr, if we revise StatePlace macro accordingly
    key = (kind,ipath) ##e kind should change which state obj we access, not just be in the key
    state = self.env.staterefs

    res = state.setdefault(key, None) 
        # I wanted to use {} as default and wrap it with attr interface before returning, e.g. return AttrDict(res),
        # but I can't find code for AttrDict right now, and I worry its __setattr__ is inefficient, so this is easier:
    if res is None:
        res = attrholder()
        state[key] = res
    return res

def set_default_attrs(obj, **kws): #e refile in py_utils, or into the new file mentioned above
    "for each attr=val pair in **kws, if attr is not set in obj, set it (using hasattr and setattr on obj)"
    for k, v in kws.iteritems():
        if not hasattr(obj, k):
            setattr(obj, k, v)
        continue
    return
    #e useful improvements to set_default_attrs might be: [061116]
    # - shorter name
    # - able to create new objs of a desired type
    #   (perhaps by using a kw prefix: _type_attr = type, or _init_attr = (type, dfltval aka initarg))
    # - or to check the type if the obj is found (same args and call, but ask the type if it agrees that obj is one of its type)
    # - if obj is wrong type, we might even coerce it, eg add glue code to improve the api, make it relative to our own coords, etc,
    #   if we can do this in our local proxy for the state rather than in the external state. BUT, if we're creating the object too,
    #   we'd better make it clear what type to create it as externally (for others to also see)
    #   vs what type to coerce/glue that too locally (for private use). So we really have to say both the external & local types,
    #   or the external type & local mapping from that, or something like that.
    #   In fact -- maybe even give the two versions different names; which probably implies,
    #   set up a dependency between different external data.
    # - be able to initialize subattrs, like self.state.x.y -- do by creating x of desired type, then doing x.y inside x --
    #   but Q, do you do this if x.y is not there in x, but x is already there, or only if even x is not already there?
    #   usually the first, meaning, use two separate calls of this, but can one notation do it all? (and do we need that?)
    # - we might want a toplevel (expr syntax) version of all this, for use in pure-expr-notation programs; related to LocalState
    #   (see notesfile), esp if that really sets up a local *ref* to perhaps-external state.

# ==

class LocalState(InstanceOrExpr): #e stub, just reserve the name and let searches find where to add code for it
    """Permit body exprs to reference specific external state using local names
    (and perhaps using specified proxy-wrappers,
     so the state is seen using locally desired types & in local coordinate systems).
       Usage:
       - if x is already defined as a Symbol, e.g. by from __Symbols__ import x : maybe:
       
           LocalState( (x,type/location/etc), body(x) )
           
       - otherwise: maybe:

           LocalState( lambda x = XXX(type/location/etc): body(x) )
             # might work if we never modify x directly, only use it or set attrs in it
    """
    _init_instance = stub # asfail if used
    pass

if 0: # e.g. code, scratch area
    LocalState( lambda x = State(int, 1): body(x.value, x.value = 1) ) # note, x.calue = 1 is not allowed in a lambda anyway!

    # in a class:
    def body(self, x):
        x.value
        x.value = 1

#e  see also ToggleShow.py

# == end of current code


# == old code

# kluge to test state toggling:

if 0:

    def bcolor(env, nextness = 0):
        n = vv.state.setdefault('buttoncolor',0)
        return (green, yellow, red)[(n + nextness) % 3]

    def next_bcolor(env):
        return bcolor(env, 1)

    def toggleit():
        n = vv.state.setdefault('buttoncolor',0)
        n += 1
        n = n % 3
        vv.state['buttoncolor'] = n
        return

    def getit(fakeenv): # note: the bug of saying getit() rather than getit in an expr was hard to catch; will be easier when env is real
        return "use displist? %s" % ('no', 'yes')[not not USE_DISPLAY_LIST_OPTIM]

    def setit(val = None):
        global USE_DISPLAY_LIST_OPTIM
        if val is None:
            # toggle it
            val = not USE_DISPLAY_LIST_OPTIM
        USE_DISPLAY_LIST_OPTIM = not not val
        vv.havelist = 0
        print "set USE_DISPLAY_LIST_OPTIM = %r" % USE_DISPLAY_LIST_OPTIM

    displist_expr_BUGGY = Button(Row(Rect(0.5,0.5,black),TextRect(18, 2, getit)), on_press = setit)
        # works, but has bug: not sensitive to baremotion or click on text if you drag onto it from empty space,
        # only if you drag onto it from the Rect.
        
    displist_expr = Row(
        Button( Rect(0.5,0.5,black), DebugDraw( Rect(0.5,0.5,gray), "grayguy"), on_press = setit),
        TextRect(18, 2, getit))

# end

