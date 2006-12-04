"""
Set.py - provide the assignment action called Set. 

$Id$

Note: this operation name is important enough to override any worry about the potential
name conflict with something related to mathematical set-theory sets or Python dict-like sets.

History, status, plans:

first implem written in controls.py, moved here 061203

but it's not general enough, needs merge with other ideas for it
mentioned in various files #e
"""

from basic import * # might be recursive #e

# stub types
StateRef = Anything # fyi, StateRef is a different stub in ToggleShow.py, same as in controls.py

#  Set(choiceref, choiceval) - instantiates to a py function (or Action wrapping that) that when called does cr.value = cv
# note: compared to some other files' ideas, this takes a stateref rather than an lval as arg1 -- might be wrong
# [a suffix of that comment is duped in two files]
class Set(InstanceOrExpr): # experimental, 061130
    stateref = Arg(StateRef)
    val = Arg(Anything)
    def __call__(self, *args, **kws):
        ### NOTE: this method will be moved to a new superclass, Action
        if self._e_is_instance:
            self._i_do_action(*args, **kws) #k correct to pass args? or just assert them missing right here?
            return
        else:
            return super(Set, self).__call__(*args, **kws) # presumably a customized or arg-filled pure expr
                #k Q: could I also just say super(Set, self)(*args, **kws) ?? Same Q for .__getattr__('attr') vs .attr, etc.
                # I am not sure they're equiv if super doesn't explicitly define the special method (or for that matter, if it does).
                # For all I know, they'd be infrecurs. In fact that seems likely -- it seems to be what I know is true for getattr.
        pass
    def _i_do_action(self, *args, **kws):
        assert not args
        assert not kws
        print "%r: setting %r.value = %r" % (self, self.stateref , self.val)###
        if self.stateref == 0:
            # kluge: debug print for testexpr_16; this happens because Set is trying to be two things at once re arg1,
            # lval like _self.var to set, or stateref (this code, used in ToggleShow).
            print "that stateref of 0 came from this expr arg:", self._e_args[0]
        self.stateref.value = self.val
        return
    pass

# end
