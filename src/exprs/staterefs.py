"""
staterefs.py - facilities for defining and referencing state,
in widget exprs which display it, edit it, operate on it, produce it

$Id$
"""

from basic import * # all we really need is call_Expr & InstanceOrExpr, so far.
    #k [digr: is there a reload bug caused by things we get this way?]
from basic import _self

def StatePlace(kind, ipath_expr): # experimental; sort of a sister to Arg/Option/Instance; likely to get revised a lot
    """turn into a formula (for use in class assignment)
    which will eval to a permanent reference to a (found or created) attrholder
    for storing state of the given kind, at the given ipath (value of ipath_expr),
    relative to the env of the Instance this is used in.
    """
    return call_Expr( _StatePlace_helper, _self, kind, ipath_expr )

def _StatePlace_helper( self, kind, ipath): # could become a method in InstanceOrExpr, if we revise StatePlace macro accordingly
    key = (kind,ipath) ##e kind should change which state obj we access, not just be in the key
    state = self.env.staterefs
        # I must have the name wrong [where i am 061115 late] --
        ## AttributeError: 'NoneType' object has no attribute 'state'
        ##  [lvals.py:160] [Exprs.py:193] [Exprs.py:413] [Highlightable.py:89] [Delegator.py:10]

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

    

    
