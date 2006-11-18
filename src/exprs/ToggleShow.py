"""
ToggleShow.py

$Id$
"""

##nim: [obs? maybe not]
##    action on pressing open or closed
##    StateRef, syntax and implem
##    If [needs testing, and review of old code for it vs this new code, esp re OpExpr, and refiling]
##    get rid of this line: ## basic.py: 162: ToggleShow = Stub -- REMOVE THIS when we want to import this real one

##e see also old code in ToggleShow-outtakes.py



from basic import *
from basic import _self

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable

import TextRect
reload_once(TextRect)
from TextRect import TextRect

import Column
reload_once(Column)
from Column import SimpleRow, SimpleColumn


Automatic = StateRef = Stub

## Set - not yet needed
State # defined in Exprs.py but nim -- that's where i am 061117 445p, plus here where i use it


# ==

#e for If, see also:
# Exprs.py: 565: class If_expr(OpExpr): # so we can use If in formulas
# Exprs.py: 568: ## def If(): pass
# testdraw1_cannib.py: 1054: def If(cond, then, else_ = None):
# usage in ToggleShow-outtakes.py

class If_expr(InstanceMacro): #e refile ### WAIT A MINUTE, why does Exprs.py think it needs to be an OpExpr? for getattr & call?
    cond = Arg(bool) # WARNING: this is effectively a public attr; none of these argnames will be delegated to the value (I think)
    _then = Arg(Anything)
    _else  = Arg(Anything, None)
    ## _value = cond and _then or _else # needs and_Expr, but that's as hard internally as If_expr, so don't bother
    def _C__value(self):
        if self.cond:
            return self._then
        else:
            return self._else
        pass
    pass

def If(cond, _then, _else = None):
    if is_pure_expr(cond):
        return If_expr(cond, _then, _else)
            #e maybe this will typecheck cond someday (in a way that would complain if it was a pyclass)
    elif cond:
        return _then ##k whether or not it's an expr?? (I think so... this is then a primitive form of expr-simplification, I guess)
    else:
        return _else
    pass

    # Q: If cond is an Instance, do we want to check whether it says it's legal to get its boolean value?
    # A: We don't need to -- if it cares, let it define __bool__ (or whatever it's called, maybe __nonzero__) and raise an exception.
    # I think that would be ok, since even if we knew that would happen, what else would we want to do?
    # And besides, we could always catch the exception. (Or add a prior type-query to cond, if one is defined someday.)

# earlier overly conservative version:
##def If(cond, _then, _else = None):
##    if is_pure_expr(cond) or is_pure_expr(_then) or is_pure_expr(_else):
##        return If_expr(cond, _then, _else)
##    if cond:
##        return _then
##    else:
##        return _else
##    pass

# ==


class ToggleShow(InstanceMacro):
    # args
    thing = Arg(Widget2D)
    label = Arg(Widget2D) #e or coerce text into a 1-line TextRect -- how do we declare that intent??
    if 0: # first make it work with a self-made stateref only, imitating Highlightable, using transient state
        stateref = Arg(StateRef, Automatic) ###k assumes the dflt can be a way to make one, not a literal one

        ## Q: how does each stateref we have, e.g. the one here meant for 'open', relate to StatePlace args
        # we might make or get from a superclass? (like the ones now in Highlightable.py but to be moved to a super of it)
        # if caller passes one, no need for our own, but to make our own, we'd make it in a StatePlace of our own, I think. ##e 061117

    if 0 and 'maybe':
        ##e might need to also say it's supposed to be boolean
        stateref = Arg(StateRef(bool), Automatic)

        ##e and also spell out the default location -- assume ipath itself can be coerced into the full stateref

        stateref = Arg(StateRef(bool), _self.ipath)

        ####k is ipath local to something like _self, or only rel to the entire model?? his matters if we name the statepath here!

        stateref = Arg(StateRef(bool), _my_node.open) ###k assumes _my_node.open can be an lval even after _my_node is bound! ####k
        
    
        ##e or we could spell out the default stateref as _self.ipath, assuming that can be coerced into one --
        # of course it can't, we also need to say it's boolean (openQ: open is true, closed is false) and with what encoding.
        # but come to think of it, that is not part of the arg, right? the arg is "some boolean state"... hmm, i guess it is.
        # but the arg can also be "where to store the state, of whatever kind you want". And we say the type and encoding
        # if the arg doesn't -- as if the caller can supply partial info in the arg, and we supply defaults rather than
        # making them get made up by the bare argtype -- which could work by just using a fancified argtype created here.
        # which the Arg macro could make for us somehow... but that can all wait for later. For now,
        # we can detect the boolean type by how we try to use the arg, i guess... not sure, maybe just say it right here.
        # and the default encoding for bools (known to the bool type, not custom to us) is fine.

    if 1:
        transient_state = StatePlace('transient') #e move into super along with the ones in Highlightable of which this is a copy
        #e rename stateref to be specific for open, maybe open_stateref, in that if 0 code above
        # devel scratch: transient_state is an attr_accessor, which lets you do getattr and setattr.
        # but what we want it to do for us is tell us an lval for the attr 'open'
        # so we can retain that, attached to self.open somehow -- as its actual lval, maybe? not sure.
        # but much like that, since get or set self.open should work that way.
        # so a stateref (instance of StateRef) is basically an instance which acts as an lval... and can be attached to an attr.
        # But ExprsMeta right now insists on making its own lval, being passed a formula. Should we kluge-adapt to that or change it?
        # Guess: better & maybe easier to change it. So we have a new kind of object, not a formula (or a special kind of one),
        # to use as an rhs and process by ExprsMeta. It's not an lval, that's per-Instance. Is it a formula for making an lval?###
        # But it might be semantically different, since we don't store the lval as the value for self.open,
        # but as the value for its lval. hmm.... can we tell ExprsMeta to do this by an assignment to open
        # of a wrapped formula? it means, get the lval not by making one whose vals come from this formula
        # but make a property whose lvals come from this formula (which should be per-instance but time-constant, maybe,
        # tho if not time constant, it might be ok -- not sure ##e).

        ## open = State('transient','open')
            ### hmm... maybe 'open' needn't be passed if it gets it like Arg or Option does... maybe the kind is also default something?
            # so: open = State()? bt say the type and dfault val -- like I did in this:
            # staterefs.py: 181:     LocalState( lambda x = State(int, 1): body(x.value, x.value = 1) ) #

    if 0: # this will be real code, but not quite yet -- use an easier way first.
        open = State(bool, True) # default 'kind' of state depends on which layer this object is in, or something else about its class
            # but for now make it always transient_state
            # this is a macro like Option
            # it takes exprs for type & initial val
            #  but those are only evalled in _init_instance or so -- not yet well defined what happens if they time-vary
            # and note, that form doesn't yet let you point the state into a storage place other than _self.ipath... should it??
            # but the importance is, now in python you use self.open for get and set, just as you'd expect for an instance var.

    if 1:
        def get_open(self): #k
            return self.transient_state.open
        def set_open(self, val): #k
            self.transient_state.open = val
            return
        open = property(get_open, set_open)
        pass
    
    # constants
    open_icon   = TextRect('+',1,1) #stub
    closed_icon = TextRect('-',1,1) #stub
    
    # _value, and helper formulae
    ## open = stateref.value # can we make it work to say Set(open, newval) after this?? ####k
        # the hard part would be: eval arg1, but not quite all the way. we'd need a special eval mode for lvals.
        # it'd be related to the one for simplify, but different, since for (most) subexprs it'd go all the way.
    ## openclose = If( open, open_icon, closed_icon )
    openclose = Highlightable( If( open, open_icon, closed_icon ),
                               ##e should optim its gl_update eagerness for when some of its states look the same as others!
                               #e someday be able to say:
                               # on_press = Set( open, not_Expr(open) )
                               ## silly: on_press = lambda open = open: open = not open # no, open = not open can't work
                               # in fact, you can't use "lambda open = open", since open has to be replaced by ExprsMeta

                               ##k can on_press be an expr to eval, instead of a (constant expr for a) func to call?? ####k
                               ## on_press = call_Expr( lambda xxx: self.open = not self.open, xxx) # no, no assignment in lambda
                               on_press = _self.toggle_open
                            )

    def toggle_open(self):
        self.open = not self.open ### can this work??? it will call set of self.open -- what does the descriptor do for that?
        # (asfail, or not have __set__ at all?? FIND OUT. the notesfile says the same thing but for a different Q, what was it?)
            ## WE SHOULD MAKE THIS WORK even if we also make on_press = Set( open, not_Expr(open) ) work, since it's so natural.
        ### BTW what is it that will notice the inval, and the usage of this when we drew, and know that gl_update is needed?
        # the same thing that would know a display list content was invalid -- but where is it in our current code (if anywhere)?
        # I vaguely recall a discussion of that issue, in the displist chunk code or notesfile, weeks ago.
        # some way to have lvals representing displist contents or frame buffer contents, whose inval means an update is needed.
        printnim("toggle_open might do a setattr which is not legal yet, and (once that's fixed) might not properly gl_update yet")
        return
    
    _value = SimpleRow(   
        openclose,
        SimpleColumn(
            label,
            If( open, thing)
        )
    )

    if 0: # if 0 for now, since this happens, as semiexpected:
        ## AssertionError: compute method asked for on non-Instance <SimpleRow#3566(a) at 0xe708cb0>

        ##e do we want to make the height always act as if it's open? I think not... but having a public open_height attr
        # (and another one for closed_height) might be useful for some callers (e.g. to draw a fixed-sized box that can hold either state).
        # Would the following defns work:?
        
        # (They might not work if SimpleRow(...).attr fails to create a getattr_Expr! I suspect it doesn't. ####k )

        # [WARNING: too inefficient even if they work, due to extra instance of thing -- see comment for a fix]
        open_height = SimpleRow(   
            open_icon,
            SimpleColumn(
                label,
                thing
            )).height   ##k if this works, it must mean the SimpleRow gets instantiated, or (unlikely)
                        # can report its height even without that. As of 061116 I think it *will* get instantiated from this defn,
                        # but I was recently doubting whether it *should* (see recent discussions of TestIterator etc).
                        # If it won't, I think wrapping it with Instance() should solve the problem (assuming height is deterministic).
                        # If height is not deterministic, the soln is to make open_instance and closed_instance (sharing instances
                        # of label), then display one of them, report height of both. (More efficient, too -- only one instance of thing.)
                        # (Will the shared instance of label have an ipath taken from one of its uses, or something else?
                        #  Guess: from the code that creates it separately.)
        
        closed_height = SimpleRow(   
            closed_icon,
            SimpleColumn( # this entire subexpr is probably equivalent to label, but using this form makes it more clearly correct
                label,
                None
            )).height

    pass # end of class ToggleShow

# end
