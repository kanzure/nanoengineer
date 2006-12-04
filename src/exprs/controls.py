"""
controls.py - some simple controls, like ChoiceButton and ChoiceColumn

$Id$

###e also has some general things we need to refile
"""

#e stub, nim; implem requires StateRef, some better type conversion (& filling it out below), Set action, on_press accepting that

#e imports
from basic import *
from basic import _self

import Rect
reload_once(Rect)
from Rect import Rect, Spacer, SpacerFor

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

import images
reload_once(images)
from images import Image, IconImage

If = If_kluge # until debugged

# stub types
stubtype = 'stubtype'
StateRef = Anything # fyi, StateRef is a different stub in ToggleShow.py, same as in Set.py

import Set
reload_once(Set)
from Set import SetStateRefValue ###e move to basic, but maybe only import of Set, not of this semiobs variant [061204 comment]

import staterefs
reload_once(staterefs)
from staterefs import LocalVariable_StateRef ###e move to basic, if it doesn't become obs, but it probably will, once State works

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

    sbar_text = Option(str, format_Expr("%s", _self.choiceval)) # mouseover text for statusbar

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
                            on_press = SetStateRefValue(choiceref, choiceval),
                                ##e probably best to say Set(choiceref.value, choiceval), but I think that's nim -- not sure --
                                # should retest it after Set is revised later today to work with arg1 being lval eg getattr_Expr [061204]
                            sbar_text = sbar_text
                           )
    pass # end of class ChoiceButton

# ==

####e refile these:

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
            ## print "using False for extflag in %r from _i_grabarg_0%r" % ( (external_flag, res0), (self, attr, argpos, dflt_expr) ) 
            external_flag = False # special case for arg[0]: treat _self as internal, so it refers to our instance, not caller's
        return external_flag, res0
    pass

# ==

# test status 061130: works, except that a click is only noticed (or a mouseover sbar msg given) for the one that's currently chosen,
# so you can't change the current choice. hmm.

## def make_testexpr_for_ChoiceButton(): #e call me from test.py to make a [#e list of named?] testexprs for this
def ChoiceColumn( nchoices, dflt = 0, **kws): ##e should be an InstanceMacro, not a def! doesn't work to be customized this way.
    "#doc"
    #e nim: Column -- esp on list like this -- Column( map(...)) -- so use SimpleColumn
    return Apply(
        lambda stateref_expr, nchoices = nchoices, dflt = dflt, kws = kws:
            SimpleRow( # stateref_expr will be a Symbol when this lambda is run, to produce an expr, once only
                SimpleColumn( * map( ChoiceButton(choiceref = stateref_expr, **kws), range(nchoices) ) ), # choose
                TextRect( format_Expr( "choice is %%r (default %s)" % dflt, stateref_expr.value ), 1, 30) # show choice
            ),
        LocalVariable_StateRef(int, dflt)
            # LocalState, combining this an the Apply?
                # or, just a stateref to some fixed state somewhere... whose instance has .value I can get or set? use that for now.
                ##k is there any way to use the new-061203 State macro for this?
    )

# ==

checkbox_image = IconImage(ideal_width = 25, ideal_height = 21, size = Rect(25 * PIXELS, 21 * PIXELS))
    # WARNING: dup code & comment with tests.py, WHICH PROBABLY IMPORTS * from here
    
    # note, IconImage ought to use orig size in pixels but uses 22x22,
    # and ought to display with orig size but doesn't -- all those image options need reform, as its comments already know ###e

#e see also checkbox_v2 in tests.py for use in testexpr_16b

class checkbox_v3(InstanceMacro): #e rename
    stateref = Arg(StateRef, None) ### default? might not work with a default val yet
        ### IMPLEM: specify what external state to use, eg a prefs variable, PrefsKey_StateRef[displayOriginAxis_prefs_key]
    default_value = Option(bool, False)
    ## var = State(bool, default_value)
    var = stateref.value
    print "var = %r" % (var,) # TypeError: 'module' object is not callable - on line that says on_press = Set(var, not_Expr(var) )
    _value = Highlightable(
        If( var,
            checkbox_image('mac_checkbox_on.jpg'),
            checkbox_image('mac_checkbox_off.jpg'),
        ),
        on_press = Set(var, not_Expr(var) )
    )
    pass



 # compare to LocalVariable_StateRef


"""
1. Subject: where i am g5 504p; highlight/text debug ideas

the choicebutton bug might be entirely in highlightable vs textrect
and not in anything else, based on what it acts like
and my guesses in test.py comments about it.

next up: did i learn anything from the mess of lambda and localvar
and state related kluges in controls.py?

(and also debug this bug, or work around it more permanently,
eg always draw a rect just behind text, or a same-rect into the depth buffer)

(also test this bug for images, since they are drawn the same way as text is)

(also scan the code for drawing text or both for an accidental explan
like a depth shift, or some disable or mask i forgot about)

(also put in some closers into the overlays
to see if it's a bug caused by all the things being drawn at the same depth)

2. Subject: BAD CHOICE BUG - wrong one if you move mouse quickly!

if you move mouse from top to bot one or vice versa, fast,
then click at end w/o slowing down,
it can pick 2nd to last one sometimes,
as if it uses an old mouse pos without noticing it,
or uses an old stencil buffer contents or selobj or something like that.

how can it not correctly confirm the one under the click?
I'd think it'd update_selobj and find out if it's wrong.
does it do that and then see None for selobj and somehow
revert back to thinking about the prior value of selobj???

mitigation: make these things hover-highlight, then you'll probably
see if you're going too fast; it might help me debug it too.


3. TextRect uses drawfont2 which uses cad/src/testdraw.py: 766: def draw_textured_rect
Image says "from draw_utils import draw_textured_rect" which gets it from itself, nice simple def.
So is the one in testdraw.py buggy? No, it looks identical! They need "dup code" comments:
WARNING: this function is defined identically in both cad/src/testdraw.py and cad/src/exprs/draw_utils.py.

"""

# end
