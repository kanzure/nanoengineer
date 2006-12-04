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

#  SetStateRefValue(choiceref, choiceval) - instantiates to a py function (or Action wrapping that) that when called does cr.value = cv
# note: compared to some other files' ideas (for Set), this takes a stateref rather than an lval as arg1 -- might be wrong [is wrong]
# [a suffix of that comment is duped in two files]
class SetStateRefValue(InstanceOrExpr): # experimental, 061130; renamed from Set to SetStateRefValue 061204; deprecated
    stateref = Arg(StateRef)
    val = Arg(Anything)
    def __call__(self, *args, **kws):
        ### NOTE: this method will be moved to a new superclass, Action
        if self._e_is_instance:
            self._i_do_action(*args, **kws) #k correct to pass args? or just assert them missing right here?
            return
        else:
            return super(SetStateRefValue, self).__call__(*args, **kws) # presumably a customized or arg-filled pure expr
                #k Q: could I also just say super(SetStateRefValue, self)(*args, **kws) ?? Same Q for .__getattr__('attr') vs .attr, etc.
                # I am not sure they're equiv if super doesn't explicitly define the special method (or for that matter, if it does).
                # For all I know, they'd be infrecurs. In fact that seems likely -- it seems to be what I know is true for getattr.
        pass
    def _i_do_action(self, *args, **kws):
        assert not args
        assert not kws
        print "%r: setting %r.value = %r" % (self, self.stateref , self.val)###
        if self.stateref == 0:
            # kluge: debug print for testexpr_16; this happens because SetStateRefValue is trying to be two things at once re arg1,
            # lval like _self.var to set, or stateref (this code, used in ToggleShow).
            print "that stateref of 0 came from this expr arg:", self._e_args[0]
        self.stateref.value = self.val
        return
    pass

class Set(InstanceOrExpr): pass #stub -- adding Set with arg1 an lval eg a getattr_Expr, 061204

# end
