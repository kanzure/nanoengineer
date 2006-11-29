"""
If_expr.py - provide the expr (or macro) If(cond, _then, _else) and related functions/classes

$Id$

Note: the current implem can't reside in Exprs.py since it uses higher-level features.
It's likely that this will be replaced someday with a lower-level implem,
but for now, it has to be in this separate file (maybe that's best anyway).

Note: file needs cleanup, and code needs reimplem.
"""

from basic import * # partial (recursive) import, since this is imported by basic

# ==

# If -- refiled from ToggleShow.py, 061128

##    If [needs +testing, and [still] review of old code for it vs this new code, esp re OpExpr, and refiling]

#e If_expr is probably wrongly implemed too

### see also class If_ in testdraw.py

#e for If, see also:
# Exprs.py: 565: class If_expr(OpExpr): # so we can use If in formulas
# testdraw1_cannib.py: 1054: def If(cond, then, else_ = None):
# usage in ToggleShow-outtakes.py

# ==

class If_expr(InstanceMacro): #e refile ### WAIT A MINUTE, why does Exprs.py think it needs to be an OpExpr? for getattr & call?
    cond = Arg(bool) # WARNING: this is effectively a public attr; none of these argnames will be delegated to the value (I think)
    _then = Arg(Anything)
    _else  = Arg(Anything, None) # note: the None default probably won't work here; the callers presently pass a TextRect
    def _C__value(self):
        if self.cond:
                # digr: I mistakenly thought _then & _else ipaths were same, in some debugging e.g. printing _self.ipath,
                # since I said _self where I meant _this(Highlightable).
                # THAT'S GOING TO BE A COMMON PROBLEM -- need to rethink the jargon...
                # maybe let _this.attr work (find innermost Instance with capitalized classname??) [061121]
            return self._then
        else:
            return self._else
        pass
    pass

def If_kluge(*args):###e zap or rename 
    """Use this in place of If when you know you want If to mean If_expr but you worry that the If code might not give it to you yet;
    this always does give it to you, but warns you if If would not have done so.
    [probably not needed anymore]
    """
    res1 = res = If(*args)
    if not isinstance(res, If_expr):
        res2 = res = If_expr(*args)
        assert isinstance(res, If_expr)
        msg = "bug: If() gave you %r instead of this If_expr %r I think you wanted (which I'll use)" % (res1, res2)
        print msg
        assert 0, msg #061121
    return res

def If(cond, _then, _else = None):
    # note: the default value None for _else doesn't yet work in most uses, due to a nontrivial logic bug
    # mentioned in ToggleShow.py (I think) and discussed in a notesfile (not in cvs). [IIRC 061128]
    cond = canon_expr(cond)
        # (but not on _then or _else to make this work better for immediate use. (might be deprecated, not sure))
    constflag, condval = expr_constant_value(cond)
    
    if not constflag:
        return If_expr(cond, _then, _else)
            #e maybe this will typecheck cond someday (in a way that would complain if it was a pyclass)
    elif condval:
        print "using then immediately"### leave these in awhile, since they're rare and might indicate a bug
        return _then ##k whether or not it's an expr?? (I think so... this is then a primitive form of expr-simplification, I guess)
    else:
        print "using else immediately"###
        return _else
    pass

    # Q: If cond is an Instance, do we want to check whether it says it's legal to get its boolean value?
    # A: We don't need to -- if it cares, let it define __bool__ (or whatever it's called, maybe __nonzero__) and raise an exception.
    # I think that would be ok, since even if we knew that would happen, what else would we want to do?
    # And besides, we could always catch the exception. (Or add a prior type-query to cond, if one is defined someday.)

# end
