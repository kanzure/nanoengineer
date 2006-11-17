"""
ToggleShow.py

$Id$
"""

nim:
    action on pressing open or closed
    StateRef, syntax and implem
    If [needs testing, and review of old code for it vs this new code, esp re OpExpr, and refiling]
    get rid of this line: ## basic.py: 162: ToggleShow = Stub -- REMOVE THIS when we want to import this real one

##e see also old code in ToggleShow-outtakes.py



from basic import *
from basic import _self

Automatic = StateRef = Stub

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
    stateref = Arg(StateRef, Automatic) ###k assumes the dflt can be a way to make one, not a literal one

    if 'maybe':
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

    # constants
    open_icon   = TextRect('+',1,1) #stub
    closed_icon = TextRect('-',1,1) #stub
    
    # _value, and helper formulae
    open = stateref.value # can we make it work to say Set(open, newval) after this?? ####k
        # the hard part would be: eval arg1, but not quite all the way. we'd need a special eval mode for lvals.
        # it'd be related to the one for simplify, but different, since for (most) subexprs it'd go all the way.
    openclose = If( open, open_icon, closed_icon )
    
    _value = SimpleRow(   
        openclose,
        SimpleColumn(
            label,
            If( open, thing)
        )
    )
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
