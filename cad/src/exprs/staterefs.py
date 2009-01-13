# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
staterefs.py - facilities for defining and referencing state,
in widget exprs which display it, edit it, operate on it, produce it

###e MIGHT RENAME, since widget_env has an attr or arg named this. state.py? might be confusing re State macro.

@author: bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

note: this used to define StatePlace and associated things, but those are now in StatePlace.py [as of 061203];
most things remaining here are nim

see also: class Set, and State macro, in other files
"""

from exprs.StatePlace import set_default_attrs
from exprs.instance_helpers import InstanceOrExpr
from exprs.attr_decl_macros import Arg, ArgOrOption
from exprs.ExprsConstants import Type
from exprs.py_utils import printnim, stub
from exprs.__Symbols__ import Anything

from utilities import debug_flags

# ==

class LocalVariable_StateRef(InstanceOrExpr): # guess, 061130
    # [moved here from controls.py, 061203; will probably become obs once State works]
    """
    return something which instantiates to something with .value which is settable state...
    """
    #e older name: StateRefFromIpath; is this almost the same as the proposed State() thing? it may differ in how to alter ipath
    # or some other arg saying where to store the ref, or in not letting you change how to store it (value encoding),
    # and worst, in whether it's an lval or not -- I think State is an lval (no need for .value) and this is a stateref.
    type = Arg(Type, Anything)
    defaultValue = ArgOrOption(Anything, None) ##e default of this should depend on type, in same way it does for Arg or Option
        # see comments in  about problems if this is a formula which uses anything usage-tracked -- same probably applies here.
    def get_value(self):
        #e should coerce this to self.type before returning it -- or add glue code wrt actual type, or....
        return self.transient_state.value ###e let transient_state not be the only option? does the stateplace even matter??
    def set_value(self, val): 
        self.transient_state.value = val #e should coerce that to self.type, or add glue code...
        return
    value = property(get_value, set_value)
    def _init_instance(self):
        super(LocalVariable_StateRef, self)._init_instance()
        set_default_attrs( self.transient_state, value = self.defaultValue) #e should coerce that to self.type
    pass

class PrefsKey_StateRef(InstanceOrExpr): # guess, 061204
    """
    return something which instantiates to something with .value which is settable state,
    shared with env.prefs[key],
    properly usage-tracked in a compatible way with the rest of NE1
    """
    prefs_key = Arg(str) # note: it's probably ok if this is a time-varying formula, tho I don't know why it would be useful.
    defaultValue = ArgOrOption(Anything, None) ##e default of this should depend on type, in same way it does for Arg or Option --
        # nonetheless it's so much more common to specify a default value than a type, that I decided to put default value first.
        #
        ##BUG (optimization issue only, and not yet important in practice):
        # [re-noticed 070228 -- also the topic of the printnim and older comment just below!]
        # this defaultValue should be evaluated with usage tracking discarded, unless prefs_key changes,
        # in which case it should be reevalled once (doable if its eval pretends to use prefs_key) -- except ideally the value
        # for older prefs_keys being reused again would be cached (eg using MemoDict) (not important in practice).
        # This bug is not yet serious since the actual args so far are constants [as of 070228].
        # It's purely an optimization issue; but the worst-case effects are that the default value changes a lot more
        # often than the prefs value itself, causing needless inval propogation into the get_value caller,
        # and thus needless recomputation of an arbitrary amount of memoized results which care about the prefs value.
        # (But for all I know, the usual constant case would slow down due to the overhead of discarding usage tracking.
        #  Actually that's not an issue since we'd also rarely recompute it, not nearly on every get_value.) 
    printnim("need a way to declare that this arg should not be usage-tracked, or have its use as default val do that for that use")
        # [older version of the comment above; contains still-useful suggestions:]
        ###e we need a way to declare that this arg should not be usage-tracked re time-variation!!! or to assert it uses nothing.
        # right now, if it uses something that will silently cause bugs, probably just invisible performance bugs from extra invals.
        # CAN THERE BE A GENERAL SOLN based on what we use this for (default vals of things that don't care about updates)?
        # that is more correct in principle, since that's what matters -- eg what if someone added another use of the same arg. ###e
    type = ArgOrOption(Type, Anything) # this arg is not yet passed by anything, or used in this implem;
        # moved type from arg2->arg3, and Arg -> ArgOrOption (as being after ArgOrOption arg2 ought to force anyway), 061211 night
    def get_value(self):
        #e should coerce this to self.type before returning it -- or add glue code wrt actual type, or....
        prefs_key = self.prefs_key
        assert type(prefs_key) == type("") #k redundant?
        import foundation.env as env
        return env.prefs.get( prefs_key, self.defaultValue ) # note: this computes defaultValue at least once, even if not needed.
    def set_value(self, val): 
        #e should coerce that to self.type, or add glue code...
        prefs_key = self.prefs_key
        assert type(prefs_key) == type("") #k redundant?
        import foundation.env as env
        env.prefs[prefs_key] = val
        if 0 and debug_flags.atom_debug:
            print "fyi: %r set env.prefs[%r] = %r" % (self, prefs_key, val)
        return
    value = property(get_value, set_value)
    def _init_instance(self):
        super(PrefsKey_StateRef, self)._init_instance()
        # also set default value of this prefs key (noting that it may or may not already have a saved value) --
        # i think this (since it does .get with default arg) is the official way:
        self.get_value()
    pass

# == end of current code

class InstanceOrExpr_Stub: pass ### kluge, permit early import of this file [061126 late] --
##e probably need to move LocalState into another file

class LocalState(InstanceOrExpr_Stub): #e stub, just reserve the name and let searches find where to add code for it
    """
    Permit body exprs to reference specific external state using local names
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

"""
    # e.g. code, scratch area [bruce 070817 made this a string, since as 'if 0' it was causing
    # a traceback in pychecker, according to Eric M mail to cad list.]
    
    LocalState( lambda x = State(int, 1): body(x.value, x.value = 1) ) # note, x.value = 1 is not allowed in a lambda anyway!

    # in a class:
    def body(self, x):
        x.value
        x.value = 1
"""

#e  see also ToggleShow.py

# end

