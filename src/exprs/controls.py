"""
controls.py - some simple controls

$Id$
"""

#e stub, nim; implem requires StateRef, some better type conversion (& filling it out below), Set action, on_press accepting that

#e imports
from basic import *
from basic import _self


import Rect
reload_once(Rect)
from Rect import Rect, Spacer

import Column
reload_once(Column)
from Column import SimpleColumn, SimpleRow

import Boxed
reload_once(Boxed)
from Boxed import Boxed

import TextRect
reload_once(TextRect)
from TextRect import TextRect

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable

import Overlay
reload_once(Overlay)
from Overlay import Overlay

If = If_kluge # until debugged

# stub types
stubtype = 'stubtype'
Type = StateRef = Function = Anything # fyi, StateRef is a different stub in ToggleShow.py

class SpacerFor(InstanceOrExpr, DelegatingMixin):
    """A spacer, the same size and position (ie same lbox) as its arg. ###e Should merge this with Spacer(dims),
    easier if dims can be a rect object which is also like a thing you could draw... maybe that's the same as a Rect object? #k
    See also Invisible, which unlike this will pick up mouseovers for highlighting. [##e And which is nim, in a cannib file.]
    """
    delegate = Arg(Widget2D)
    def draw(self):
        return
    pass

#  Set(choiceref, choiceval) - instantiates to a py function (or Action wrapping that) that when called does cr.value = cv
# note: compared to some other files' ideas, this takes a stateref rather than an lval as arg1 -- might be wrong
# [a suffix of that comment is duped in two files]
class Set(InstanceOrExpr): # experimental, 061130
    stateref = Arg(StateRef)
    val = Arg(Anything)
    def __call__(self, *args, **kws):
        if self._e_is_instance:
            # this will be moved to super Action with the specific thing to do put in a method in this subclass
            # but for now that thing is:
            print "%r: setting %r.value = %r" % (self, self.stateref , self.val)###
            self.stateref.value = self.val
            #e we might also want the func that does this available as an attr from any Action -- easy, just give it a public name
            return
        else:
            return super(Set, self).__call__(*args, **kws) # presumably a customized or arg-filled pure expr
                #k Q: could I also just say super(Set, self)(*args, **kws) ?? Same Q for .__getattr__('attr') vs .attr, etc.
                # I am not sure they're equiv if super doesn't explicitly define the special method (or for that matter, if it does).
                # For all I know, they'd be infrecurs. In fact that seems likely -- it seems to be what I know is true for getattr.
        pass
    pass
    
class ChoiceButton(InstanceMacro):
    """ChoiceButton(choiceval, choiceref, content, background, background_off) [most args optional]
    displays and permits control of a choice variable stored externally in choiceref,
    looking like Overlay(background, content) or Overlay(background_off, content)
    when its own choice value is chosen or unchosen (ie equal or unequal to the stored one), respectively.
       Most args are optional with useful defaults, or can be given as simpler convenience types (eg colors or text);
    all args but choiceval can be given as named options, which is useful for customization.
       (Example: it's useful to put several of these with the same choiceref but different choicevals into a Column.
    This can be done by mapping one customized variant over a list of choicevals.)
       The choosing-action occurs on_press of entire thing -- this is not yet changeable
    (to other kinds of button actions), but should be. #e
    """
    # args
    choiceval = Arg(Anything)
        #e declare it as having to be constant per-Instance? Or can it legally vary?? I guess it could;
        # and I guess it's no error, just weird, for two of these (eg in a column) to share the same choiceval;
        # in fact, if they're physically separated it's not even weird.

    choiceref = ArgOrOption(StateRef) ###k need value-type??

    content = ArgOrOption(stubtype, TextRect(format_Expr("%s", _self.choiceval)) ) # Widget2D or something "displayable" in one (eg text or color); defaults to displayed choiceval;
        # can caller pass a formula in terms of the other options to _self? Maybe but not by saying _self! _this(ChoiceButton) == _my?

    background = ArgOrOption(stubtype, Rect(_self.width, _self.height, lightblue) ) # Widget2D, or color (used in Rect a bit larger than content)
    
    background_off = ArgOrOption(stubtype, Spacer(_self.width, _self.height)) # ditto, defaults to transparent
        ##k problem: what we want is to compute an lbox and then use this here in the spacer... or align the content... or ....
        ##e note that a lot of people find it more convenient to pass around a size, or even pass around a rect,
        # than to always work with 4 or 6 rect-related attrs...

    # formulae
    chosen = eq_Expr( choiceref.value, choiceval) #k
    ## print "chosen is",chosen

    ###k assume useful conversions of named options happened already
    ###e use _value; is it as simple as renaming it delegate and using DelegatingMixin?? Can InstanceMacro do it for us??
    # [if we use one of those, be careful not to inherit from Widget2D here, due to its lbox defaults!]
    _value = Highlightable( Overlay( SpacerFor(Boxed(content)),
                                         # kluge to make room around content in _self.width and _self.height,
                                         # and make those non-circular; WRONG because won't be properly aligned with backgrounds,
                                         # even if content itself would be;
                                         # could fix by shifting, but better to figure out how to have better rectlike size options ###e
                                     Overlay( ###KLUGE since "Overlay is a stub which only works with exactly two args"
                                         If(chosen, background, background_off),
                                         content ),
                                     ),
                            on_press = Set(choiceref, choiceval)
                           )
    pass # end of class ChoiceButton

class LocalVariable_StateRef(InstanceOrExpr): # guess, 061130
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

##class Apply(InstanceMacro): # guess, 061130
##    func = Arg(Function)
##    arg = Arg(Anything) # exactly 1 arg for now
##    if 1: # init instance? no, init_expr i think? but self.func is not defined by then, is it? it is, but self is not special...
##        func_expr = self.func( _self.arg)
##    _value = call_Expr()#...
##    pass

def Apply(func, arg1_expr): # exactly 1 arg for now
    arg1sym = _self._arg1 # make a symbol based on _self (not affected by arg1_expr in any way)
    func_expr = func(arg1sym) # feed it to the lambda to get the expr we want, relative to _self
    return _Apply_helper(func_expr, arg1_expr) ##e or could pass a list of args... and exprs like _self._args[i]
        # an expr which instantiates arg1_expr,
        # then acts as if its ._value = func_expr (with _self in func_expr captured by that instance), used by InstanceMacro(??),
        # and its ._arg1 = arg1_expr (but WAIT, how would that end up being visible to _self._arg1? Ah, by _self replacement...)

class _Apply_helper(InstanceOrExpr, DelegatingMixin):
    delegate = Arg(Anything) ### but unlike usual, _self in the arg passed in refers to the same as _self inside, so gets replaced...
    _arg1 = Arg(Anything)
    #e something to affect _self replacement
    def _i_grabarg_0( self, attr, argpos, dflt_expr):
        external_flag, res0 = super(_Apply_helper, self)._i_grabarg_0( attr, argpos, dflt_expr)
        if argpos == 0:
            print "using False for extflag in %r from _i_grabarg_0%r" % ( (external_flag, res0), (self, attr, argpos, dflt_expr) ) ###
            external_flag = False # special case for arg[0]: treat _self as internal, so it refers to our instance, not caller's
        return external_flag, res0
    pass

# test status 061130: works, except that a click is only noticed (or a mouseover sbar msg given) for the one that's currently chosen,
# so you can't change the current choice. hmm.
_DFLT = 3
def make_testexpr_for_ChoiceButton(): #e call me from test.py to make a [#e list of named?] testexprs for this
    #e nim: Column -- esp on list like this -- Column( map(...)) -- so use SimpleColumn
    return Apply(
        lambda stateref_expr: SimpleRow( # stateref_expr will be a Symbol when this lambda is run, to produce an expr, once only
             SimpleColumn( * map( ChoiceButton(choiceref = stateref_expr), range(5) ) ), # choose
             TextRect( format_Expr( "choice is %%r (default %s)" % _DFLT, stateref_expr.value ), 1, 30) # show choice
        ),
        LocalVariable_StateRef(int, _DFLT)
            # LocalState, combining this an the Apply?
                # or, just a stateref to some fixed state somewhere... whose instance has .value I can get or set? use that for now.
    )


# end
