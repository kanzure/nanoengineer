"""
ToggleShow.py

$Id$
"""

nim

##e see also old code in ToggleShow-outtakes.py

## basic.py: 162: ToggleShow = Stub -- REMOVE THIS when we want to import this real one

from basic import *
from basic import _self

Automatic = StateRef = If = Stub

#e for If, see also:
# Exprs.py: 565: class If_expr(OpExpr): # so we can use If in formulas
# Exprs.py: 568: ## def If(): pass
# testdraw1_cannib.py: 1054: def If(cond, then, else_ = None):
# usage in ToggleShow-outtakes.py


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
        
    # value
    openclose = ...
    
    _value = SimpleRow(
        openclose,
        SimpleColumn(
            label,
            If( ..., thing)
        )
    )

    pass # end of class ToggleShow

# end
