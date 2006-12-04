"""
staterefs.py - facilities for defining and referencing state,
in widget exprs which display it, edit it, operate on it, produce it

###e MIGHT RENAME, since widget_env has an attr or arg named this. state.py? might be confusing re State macro.

$Id$

note: this used to define StatePlace and associated things, but those are now in StatePlace.py [as of 061203];
most things remaining here are nim

see also: class Set, and State macro, in other files
"""

__all__ = []  # catch import errors after the file split (temporary) 


from basic import *
from basic import _self
    #k [digr: is there a reload bug caused by things we get from basic import *, since we don't reload basic??]

# ==

Type = Anything # stub type

class LocalVariable_StateRef(InstanceOrExpr): # guess, 061130
    # [moved here from controls.py, 061203; will probably become obs once State works]
    "return something which instantiates to something with .value which is settable state..."
    #e older name: StateRefFromIpath; is this almost the same as the proposed State() thing? it may differ in how to alter ipath
    # or some other arg saying where to store the ref, or in not letting you change how to store it (value encoding),
    # and worst, in whether it's an lval or not -- I think State is an lval (no need for .value) and this is a stateref.
    type = Arg(Type, Anything)
    default_value = ArgOrOption(Anything, None) ##e default of this should depend on type, in same way it does for Arg or Option
    def get_value(self):
        #e should coerce this to self.type before returning it -- or add glue code wrt actual type, or....
        return self.transient_state.value ###e let transient_state not be the only option? does the stateplace even matter??
    def set_value(self, val): 
        self.transient_state.value = val #e should coerce that to self.type, or add glue code...
        return
    value = property(get_value, set_value)
    def _init_instance(self):
        super(LocalVariable_StateRef, self)._init_instance()
        set_default_attrs( self.transient_state, value = self.default_value) #e should coerce that to self.type
    pass

# == end of current code

class InstanceOrExpr_Stub: pass ### kluge, permit early import of this file [061126 late] --
##e probably need to move LocalState into another file

class LocalState(InstanceOrExpr_Stub): #e stub, just reserve the name and let searches find where to add code for it
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
    LocalState( lambda x = State(int, 1): body(x.value, x.value = 1) ) # note, x.value = 1 is not allowed in a lambda anyway!

    # in a class:
    def body(self, x):
        x.value
        x.value = 1

#e  see also ToggleShow.py

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

