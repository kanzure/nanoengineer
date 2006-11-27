"""
controls.py - some simple controls

$Id$
"""

#e stub, nim; implem requires StateRef, some better type conversion (& filling it out below), Set action, on_press accepting that

#e imports

stubtype = 'stubtype'

class ChoiceButton(Widget2D):
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
    content = ArgOrOption(stubtype) # Widget2D or something "displayable" in one (eg text or color); defaults to displayed choiceval 
    background = ArgOrOption(stubtype) # Widget2D, or color (used in Rect a bit larger than content)
    background_off = ArgOrOption(stubtype) # ditto, defaults to transparent

    # formulae
    chosen = eq_Expr( choiceref.value, choiceval) ####

    ###k assume useful conversions of named options happened already
    ###e use _value; is it as simple as renaming it delegate and using DelegatingMixin?? Can InstanceMacro do it for us??
    _value = Highlightable( Overlay( If(chosen, background, background_off),
                                     content ),
                            on_press = Set(choiceref, choiceval)
                           )
    pass # end of class ChoiceButton

def testexpr_ChoiceButton(): #e call me
    xxxx # LocalState?
    #e nim: Column (esp on list like this)
    return SimpleRow(
        Column( map( ChoiceButton(choiceref = xxxx, etc), range(5) ) ), # choose
        TextRect( format_Expr( "choice is %r", xxxx.value )) # show choice
    )

# end
