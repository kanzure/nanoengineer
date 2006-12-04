"""
Set.py - provide the assignment action called Set, and (for now) the deprecated older variant SetStateRefValue.

$Id$

Note: this operation name is important enough to override any worry about the potential
name conflict with something related to mathematical set-theory sets or Python dict-like sets.

And the use on arg1 being an lvalue is important enough to not worry much if arg1 being a stateref is
harder to use -- now done in SetStateRefValue, might later be done in Set(stateref.value, ...).

History, status, plans:

first implem of SetStateRefValue written in controls.py, moved here 061203, renamed from Set to SetStateRefValue 061204.

adding Set with arg1 an lval eg a getattr_Expr, 061204
"""

from basic import * # might be recursive #e

# stub types
StateRef = Anything # fyi, StateRef is a different stub in ToggleShow.py, same as in controls.py



class Action(InstanceOrExpr): #061204 ; #e might refile to a new file actions.py
    """#doc; abstract superclass and coercion-type
    """
    def __call__(self, *args, **kws):
        if self._e_is_instance:
            assert not args
            assert not kws
            ## self._i_do_action(*args, **kws) #k correct to pass args?
            # or just assert them missing right here?
            # [the latter for now; could let subclass define _i_do_action_with_args later, or put the args into its env somehow;
            #  but for now i think no args will ever get passed, anyway.]
            self._i_do_action()
            return
        else:
            return super(Action, self).__call__(*args, **kws) # presumably a customized or arg-filled pure expr
                #k Q: could I also just say super(Action, self)(*args, **kws), without .__call__ ??
                # Same Q for .__getattr__('attr') vs .attr, etc.
                # I am not sure they're equiv if super doesn't explicitly define the special method (or for that matter, if it does).
                # For all I know, they'd be infrecurs. In fact that seems likely -- it seems to be what I know is true for getattr.
        pass
    def _i_do_action(self):
        "#doc"
        assert 0, "subclass must implement"
    pass

#  SetStateRefValue(choiceref, choiceval) - instantiates to a py function (or Action wrapping that) that when called does cr.value = cv
# note: compared to some other files' ideas (for Set), this takes a stateref rather than an lval as arg1 -- might be wrong [is wrong]
# [a suffix of that comment is duped in two files]
class SetStateRefValue(Action): # experimental, 061130; renamed from Set to SetStateRefValue 061204; deprecated
    """#doc
    """
    stateref = Arg(StateRef)
    val = Arg(Anything)
    def _i_do_action(self):
        print "%r: setting %r.value = %r" % (self, self.stateref , self.val)###
        if self.stateref == 0:
            # kluge: debug print for testexpr_16; this happens because SetStateRefValue is trying to be two things at once re arg1,
            # lval like _self.var to set, or stateref (this code, used in ToggleShow).
            print "that stateref of 0 came from this expr arg:", self._e_args[0]
        self.stateref.value = self.val
        return
    pass

class Set(Action): # adding Set with arg1 an lval eg a getattr_Expr, 061204; untested, see testexpr_16
    """Set( variable, value) is an Action which sets variable to value.
    More precisely, variable should be an expr that can "evaluate to a settable lvalue",
    e.g. _self.attr or obj.attr or obj-expr[index-expr] [latter case is nim as of 061204],
    and value can be any ordinary evaluatable expr. When this Action is performed, it calls lval.set_to(val)
    for lval the current lvalue-object corresponding to variable, and val the current value of value.
       See also SetStateRefValue (deprecated).
    """
    var = LvalueArg(Anything) # LvalueArg is so macro-writers can pull in lvalue args themselves, easily; experimental; Option version?
    val = Arg(Anything)
    def _i_do_action(self):
        var = self.var
        val = self.val
        print "%r: calling on our lval-object, %r.set_to(%r)" % (self, var , val)###
        var.set_to( val) # .set_to is in api for lval-objects of this kind -- not the same kind as "exprs plus _self" (for now)
        return
    pass

# end
