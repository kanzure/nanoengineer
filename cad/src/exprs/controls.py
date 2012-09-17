# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
controls.py - some simple controls, like ChoiceButton, ChoiceColumn/Row, checkbox_v3

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

TODO:

- also has some general things we need to refile

See also: toolbars.py
"""

#e stub, nim; implem requires StateRef, some better type conversion (& filling it out below), Set action, on_press accepting that

import time

from exprs.Rect import Rect, Spacer, SpacerFor

from exprs.Center import CenterY

from exprs.Column import SimpleColumn, SimpleRow

from exprs.Boxed import Boxed

from exprs.TextRect import TextRect

from exprs.Highlightable import Highlightable, print_Expr

from exprs.Overlay import Overlay

from exprs.images import IconImage

from exprs.staterefs import PrefsKey_StateRef

from exprs.DisplayListChunk import DisplayListChunk

from exprs.If_expr import If_kluge
If = If_kluge # until debugged

# stub types
from exprs.ExprsConstants import StubType
stubtype = StubType

from exprs.Set import Set

from exprs.staterefs import LocalVariable_StateRef ###e move to basic, if it doesn't become obs, but it probably will, once State works

##from exprs.debug_exprs import debug_evals_of_Expr

from utilities.constants import gray, blue, yellow, orange
from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice_boolean_False

from exprs.widget2d import Widget2D
from exprs.Exprs import format_Expr, eq_Expr, not_Expr, call_Expr, or_Expr
from exprs.instance_helpers import InstanceMacro, InstanceOrExpr
from exprs.instance_helpers import DelegatingMixin, DelegatingInstanceOrExpr
from exprs.attr_decl_macros import Arg, Option, ArgOrOption, State, Instance
from exprs.ExprsConstants import StateRef, lightblue, PIXELS
from exprs.Set import Action
from exprs.__Symbols__ import Anything, _self

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
        # can caller pass a formula in terms of the other options to _self?
        # Maybe, but not by saying _self! _this(ChoiceButton) == _my? [yes -- _my is now implemented, 061205]

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
                            ## old code: on_press = SetStateRefValue(choiceref, choiceval),
                            # try this code 061211 1113a -- it works, use it:
                            on_press = Set(choiceref.value, choiceval),
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
            # LocalState, combining this and the Apply?
                # or, just a stateref to some fixed state somewhere... whose instance has .value I can get or set? use that for now.
                ##k is there any way to use the new-061203 State macro for this?
    )

def ChoiceRow( nchoices, dflt = 0, **kws): ##e should be an InstanceMacro, not a def! doesn't work to be customized this way.
    "#doc"
    #e nim: Row -- esp on list like this -- Row( map(...)) -- so use SimpleRow
    return Apply(
        lambda stateref_expr, nchoices = nchoices, dflt = dflt, kws = kws:
            SimpleRow( # stateref_expr will be a Symbol when this lambda is run, to produce an expr, once only
                SimpleRow( * map( ChoiceButton(choiceref = stateref_expr, **kws), range(nchoices) ) ), # choose
                TextRect( format_Expr( "choice is %%r (default %s)" % dflt, stateref_expr.value ), 1, 30) # show choice
            ),
        LocalVariable_StateRef(int, dflt)
            # LocalState, combining this and the Apply?
                # or, just a stateref to some fixed state somewhere... whose instance has .value I can get or set? use that for now.
                ##k is there any way to use the new-061203 State macro for this?
    )

# ==

# how far are we from doing ChoiceRow as a class, nicely expressed? [061214 Q/exper]
# in light of the attempt below:
# - biggest need is dealings with iterated args of several kinds:
#   - OptionsDict
#   - Row over made list of things
#   - making those things, by iterating a ChoiceButton expr
# - we might also need a way to turn _self.var into a stateref we can pass into ChoiceButton as its choiceref
###e conclusion: too far to be held up by doing it, but worth thinking about, since we *DO* need to solve all those Qs pretty soon.

# One approach is to say
# - "assume we want *-expr and map-Expr for use in SimpleRow( * map( expr, varying args/opts for expr ))"
#   - and come up with simplest syntax for that we can.
#   - then we'd probably need to resolve "iterator expr" (eval/instantiate) issues too.
# - Another is to say "do that iteration in python methods or lambdas",
#   but make it easier to integrate those with toplevel formula exprs.
#   (An argument for this is that people already know how -- no need to learn new syntax.
#    A disadvantage is that the iteration won't be incrementally updated, only the whole thing at once will update.)
#   So the Apply above happens in some method of the class -- perhaps _C__value -- not sure that works if nchoices can vary,
#   but they can't vary anyway in the current def.

def OptionsDict(type = Anything):
    return Option(type) ###STUB just so parsing works, totally wrong in effect

class ChoiceRow_class(InstanceMacro): # stub, nim
    nchoices = Arg(int)
    dflt = Arg(int, 0)
    kws = OptionsDict() ###IMPLEM #e see if name is correct re other proposals, eg Options not Option?
        #e renamekws tosay what they are for -- the ChoiceButton --- note that we could ditch the OptionsDict and ask for
        # an explicit dict of them, but then they would not be indivly customizable. Should a new sub-option cust scheme be made? #e
    var = State(int, _self.dflt) ###k does _self.dflt work? Is this equiv to the above? NO, it's an lval not a stateref!
    _value = SimpleRow(
        0 ###stub -- the next hard thing is to apply this to a variable number of exprs or insts created by map over range(nchoices)
    )
    pass

# ==

checkbox_image = IconImage(ideal_width = 25, ideal_height = 21, size = Rect(25 * PIXELS, 21 * PIXELS)) # a pure expr
    # WARNING: dup code & comment with tests.py, WHICH PROBABLY IMPORTS * from here

    # note, IconImage ought to use orig size in pixels but uses 22x22,
    # and ought to display with orig size but doesn't -- all those image options need reform, as its comments already know ###e

#e see also checkbox_v2 in tests.py for use in testexpr_16b

class checkbox_v3(InstanceMacro): ##e rename # note: this can do something checkbox_pref can't yet do -- take an external stateref
    stateref = Arg(StateRef, None) ### default? might not work with a default val yet
        ### IMPLEM: specify what external state to use, eg a prefs variable, PrefsKey_StateRef(displayOriginAxis_prefs_key)
    defaultValue = Option(bool, False) ###BUG -- not used! [noticed 061215]
    ## var = State(bool, defaultValue)
    var = stateref.value
##    # print "var = %r" % (var,) # TypeError: 'module' object is not callable - on line that says on_press = Set(var, not_Expr(var) )
##        # solved: it's probably from above: import Set; from Set import something else but not Set
    _value = Highlightable(
        If( var,
            checkbox_image('mac_checkbox_on.png'),
            checkbox_image('mac_checkbox_off.png'),
        ),
        ## on_press = Set(var, not_Expr(var) ) # wanted (sort of), but doesn't work yet, as explained here:
            ## AssertionError:... <C_rule_for_formula at 0xff2de10 for 'var' in 'checkbox_v3'> should implement set_for_our_cls
            # ah, I was assuming "var = stateref.value" would alias var to obj.attr permitting set of obj.attr by set of var,
            # but of course, that should probably never be permitted to work, since it looks like we're changing self.var instead!
            # Unless, I either:
            # - implem a variant of "var = stateref.value"
            # - decide that since var would normally be unsettable when defined by a formula, that always aliasing it like that
            #   would be ok (often wanted, not too confusing).
            # PROBLEM WITH PERMITTING IT: you might start out var = State(), and it works to change self.var,
            # then change var to a formula, and forget you were directly setting it... causing an unwanted actual working set
            # of other state which you thought you were not touching or even able to touch.
            # SOLUTION:
            # - implem a variant of "var = stateref.value, sort of a "state alias"
            # - have a clear error message from this Set, suggesting to change that assignment to that alias form.
            # as of 061204 418p: tentatively decided I like that, but the alias variant syntax is not yet designed.
            # Maybe: ####@@@@
            # - var = Alias(stateref.value) ?? [sounds good]
            # - or just var = State(stateref.value), or is that too confusing?
            #   [yes, too confusing, that arg is for the type, and State is for new state, not an alias... latter is lesser problem]
            # - or var = StateRef(stateref.value)? no, it's an lval, not a stateref.
        on_press = Set(stateref.value, not_Expr(var) )
            # kluge: see if this works (I predict it will) -- workaround of not yet having that alias form of "var = stateref.value"
    )
    pass # end of class checkbox_v3

def checkbox_pref_OLDER(prefs_key, label, dflt = False): # renamed 061215 late, since newer one is better
    "#doc"
    if type(label) == type(""):
        label = TextRect(label,1,20)
    return SimpleRow(CenterY(checkbox_v3(PrefsKey_StateRef(prefs_key, dflt))), CenterY(label)) # align = CenterY is nim
    # note: adding CenterY also (probably coincidentally) improved the pixel-alignment (on g5 at least), so the label is no longer fuzzy.
    # [see also testexpr_16c, similar to this]

class checkbox_pref(InstanceMacro):
    #e rename -- Checkbox(...), with various kinds of args to say what state it uses in different ways?
    #e make it one of several prefs controls for other types of pref and control
    #e generalize to all named state -- e.g. see also LocalVariable_StateRef -- permit passing in the stateref?
    #e get dflt label from stateref??
    # note: this was split out of kluge_dragtool_state_checkbox_expr 061214,
    # extended here into a def (later renamed checkbox_pref_OLDER), then a class
    prefs_key = Arg(str)
    label = Arg(Anything) # string or Widget2D
    dflt = ArgOrOption(bool, False)
    sbar_text = Option(str, '')
    use_label = If( call_Expr(lambda label: type(label) == type(""), label), TextRect(label), label ) ## was TextRect(label,1,20)
    use_sbar_text = or_Expr( sbar_text, If( call_Expr(lambda label: type(label) == type(""), label), label, "" ))
    stateref = Instance(PrefsKey_StateRef(prefs_key, dflt))
        # note: without Instance here, next line stateref.value says (correctly):
        ## AssertionError: compute method asked for on non-Instance <PrefsKey_StateRef#47221(a)>
    var = stateref.value
    checkbox = If( var,
            checkbox_image('mac_checkbox_on.png'),
            checkbox_image('mac_checkbox_off.png'),
        )
    _value = DisplayListChunk( Highlightable( SimpleRow( CenterY(checkbox), CenterY(use_label)), # align = CenterY is nim
                               ## on_press = Set(debug_evals_of_Expr(stateref.value), not_Expr(var) ), #070119 debug_evals_of_Expr - worked
                               on_press = _self.on_press,
                                           # the following works too, but I wanted to intercept it to add some py code [070305]:
                                           ## Set( stateref.value, not_Expr(var) ),
                               sbar_text = use_sbar_text) )
        # note: using DisplayListChunk in _value works & is faster [070103]
        #070124 comment: the order DisplayListChunk( Highlightable( )) presumably means that the selobj
        # (which draws the highlightable's delegate) doesn't include the displist; doesn't matter much;
        # that CenterY(use_label) inside might be ok, or might be a bug which is made up for by the +0.5 I'm adding to drawfont2
        # in testdraw.py today -- not sure.
    incr_drawable = Instance( Boxed( CenterY(checkbox), pixelgap = 0, bordercolor = gray, borderwidth = 2 ))
        # I tried orange as a warning color -- means the checkbox reflects an intention but not yet the reality.
        # But it was annoyingly too visible. So I'll try gray.
        # If all colorboxeds are unpopular, then try an image that has a little spray of lines coming from the center, instead.
    def on_press(self):
        self.stateref.value = not self.stateref.value # was, in the expr: Set( stateref.value, not_Expr(var) )
        ###e revise this code to use self.draw_incrementally once that's refiled into Highlightable ###e
        def func(self = self):
            self.incr_drawable.draw()
            ## self.draw() # includes the label - probably a waste but who cares
            self.env.glpane.swapBuffers() # update display [needed]
        ran_already_flag, funcres = self.run_OpenGL_in_local_coords( func) # this method runs in the Highlightable made in _value
        assert ran_already_flag
        return
    pass # end of class checkbox_pref

###BUG: whatever I do, I can't get reloading of controls.py (this file) and test.py to cause code changes in on_press above
# to take effect -- not even modifying the _value expr before the reload, changing the current test by cmenu,
# or by editing testexpr assignment in test.py. sanity check -- try rerunning NE1 app - yep, that works. repeatable.
# So far it's a complete ###MYSTERY. I was wondering if the Instance that makes value hangs onto it, but altering expr
# ought to have either fixed that or warned me that it changed -- I hope. Nonetheless that's my best guess so far.
# Note (prob not related): recent NE1 startup times have sometimes been very long -- is it checking for sponsors??? [070305]

class ActionButton(DelegatingInstanceOrExpr): # 070104 quick prototype
    "ActionButton(command, text) is something the user can press to run command, which looks like a button."
    # args/options
    command = Arg(Action) #e default which prints?
    text = Arg(str, "<do it>") #e default text should be extracted from the command somehow
    button = Arg(Widget2D, Rect(15.*PIXELS)) # can it be left out so only text label is used? ideally we'd have text with special border...
    enabled = Option(bool, True) # whether the button should look enabled, and whether the command will run when the button is operated
    # formulae
    use_label = TextRect(text) ## TextRect(text,1,20)###e revise
    plain_button = CenterY(button)
    highlighted_button = Boxed( plain_button, # note: despite the name, this is only shown as the highlighted form when enabled is true
                        bordercolor = blue, # should color adapt to bg? is it a bad idea to put this over bg rather than over button?
                        borderthickness = 1.5 * PIXELS,
                        gap = 1 * PIXELS, ) ###k ????   -- note, this doesn't include the label -- ok?
    plain =       DisplayListChunk( SimpleRow( plain_button,       CenterY(use_label))) # align = CenterY is nim
    highlighted = DisplayListChunk( SimpleRow( highlighted_button, CenterY(use_label), pixelgap = 0.5))
            #k ok to wrap with DisplayListChunk? [seems so]
        ### KLUGE: without the pixelgap adjustment (to this particular weird-looking value, i guess),
        # the label moves to the right when highlighted, due to the Boxed being used to position it in the row.
        ### BUG: CenterY is not perfectly working. Guess -- lbox for TextRect is slightly wrong.
        ### IDEA: make the borderthickness for Boxed negative so the border is over the edge of the plain button. Might look better.
    ##e Note: we have no "pressed" appearance, since by the next time we get drawn, the command is already drawn and we ought to be
    # back to normal. Someday we should do a transient incremental redraw of just this button, with a "pressed and acting" appearance,
    # which can then go back to normal when the operation completes and does a regular full redraw.
    # Alternatively, we could switch to using buttons with an on_release_in action only,
    # and then have ordinarily-drawn pressed etc looks. [070227 comment]
    # update 070305: let's try to fix that:

    # appearances for optional willdoit-flicker (confirms unambiguously that the button was hit and will do something) [070307]
        # [ideally the computation & side effects could overlap the willdoit flicker in time,
        #  but they don't now, which is one reason the flicker is optional]
    incr_drawable_willdo1 = Instance( SimpleRow( highlighted_button( bordercolor = yellow), pixelgap = 0.5)) # label not needed here
    incr_drawable_willdo2 = Instance( SimpleRow( highlighted_button( bordercolor = blue ), pixelgap = 0.5))
        # note: yellow/blue (matching the usual ending & starting colors which bracket the flicker) looks much better than black/white

    # what it looks like while we're computing/doing its effects:
    incr_drawable_doing = Instance( SimpleRow( highlighted_button( bordercolor = orange),
                                               ## CenterY(use_label), [removed -- see comment for why -- might be added back]
                                               pixelgap = 0.5))
        # orange warns you that it's not yet done, is also bright & active for action;
        ### UI FLAW: the orange/yellow distinction is annoying, so it's really only desirable for debugging,
        # since it shows that the instantiation time is significant but only happens on the first use of a button.
        # Probably the distinction (and its redraw happening at all) should be a debug_pref or so. ###FIX
        # (But if there is no distinction, we may want to be sure to redraw the label now if there is any chance it can be different --
        #  but in current code there's not, since we haven't changed state it might depend on by the time we draw it.
        #  BTW I wonder if redrawing the label (i.e. instantiating this instance of it) ever takes significant time itself?? #k)

    # what it looks like while we're redrawing (after finishing its internal effects):
    incr_drawable_done = Instance( SimpleRow( highlighted_button( bordercolor = yellow), pixelgap = 0.5)) # label not needed here
        # yellow means done -- not sure makes sense -- note green means "can do" in some controls

    def doit(self):
        """This runs when the user clicks on the button.
        WARNING: it's NOT just self.do_action() (the public method self's clients, like scripts, can call to do the same action) --
        it calls that, but it also has graphical effects.
        [It may or may not be public (in the Action interface) in the end. If it is, it'll be renamed. #e]
        """
        if self.enabled:
            # do some incremental drawing [new feature 070305, revised 070307]
            ###BUG (in some client code of this class):
            # this won't be able to make clear button quickly show it's disabled until client code is revised and maybe selobj-bugfixed ###DOIT
            if debug_pref("testmode: ActionButton willdoit-flicker?",
                              # When set, this flickers the button, like how the mac confirms a menu item choice.
                              # Conclusion after testing: it works fine, and usually looks ok,
                              # but is redundant with "yellow during redraw",
                              # so as long as that's slow enough to see, this has no point and is also making it even slower,
                              # so leave it turned off by default.
                          Choice_boolean_False,
                          prefs_key = 'A9 devel/exprs/action flicker' ):
                # works [retest###], but I won't make it True by default [070307]
                ##e someday do this in a way that does not tie up the thread during this, e.g. by letting paintGL do it;
                # for now it's just experimental for its graphics effects and as a speed test,
                # and will probably be turned off after testing
                for i in range(4):
                    if i % 2 == 0:
                        self.draw_incrementally( self.incr_drawable_willdo1 )
                    else:
                        self.draw_incrementally( self.incr_drawable_willdo2 )
                    # print i, # very fast
                    # todo: delay, if needed to make this visible -- using time.time to delay only if draw timing was not long enough
                    # (with no delay it's almost too fast too see -- sometime I should write the code to measure the actual speed)
                    # (for now assume it's always very fast, so just delay a fixed amount using time.sleep)
                    time.sleep(1.0/3/4) # 1/3 sec, spread over 4 sleeps
            self.draw_incrementally( self.incr_drawable_doing ) # this method runs in the Highlightable made in delegate
            print "ActionButton: doing %r for %r" % (self.text, self) ### remove self?
                ##e optim note: this shows self is a different obj each time (at least for make dna cyl button)...
                # I guess this is due to dna_ribbon_view_toolcorner_expr_maker being a function that makes an expr
                # which runs again at least on every use of the button (maybe more -- not sure exactly how often).
                # Should fix that (and it's not this file's fault -- just that the print stmt above reveals the problem).
            self.do_action()
            self.draw_incrementally( self.incr_drawable_done )
            pass
        else:
            print "ActionButton: not enabled, so not doing %r for %r" % (self.text, self) # remove when works [reenabled 070307 ####]
            pass
        return
    def do_action(self):
        "#doc -- public, also used internally; see doit comment for doc, for now"
        res = self.command()
        if res is not None:
            print "unexpected: %r cmd %r retval was not None: %r" % (self, self.text, res,) #e remove if happens legitimately
        return
    ###e refile these:
    def draw_incrementally( self, thing):#070307 #e refile (as for next method below)
        "#doc"
        self._incrementally_draw_OpenGL( thing.draw ) #e or call a variant method of thing, which defaults to thing.draw?? nah, use an env var?
    def _incrementally_draw_OpenGL( self, func): #070307 #e rename ###e refile into IorE someday, and into Highlightable for now, i think
        """helper method for incremental drawing by user event handling methods (not part of self.draw called by paintGL).
        [#doc better]
        func should contain OpenGL commands for incrementally drawing, in self's coords (but not the swapbuffers at the end).
           Guess at a requirement within func: [which should be removed and is prob not real now, see below]
        # don't use drawkid! (because we're not inside a draw method)
        # (but will this cause trouble for draw methods inside this?? ### NEEDS REVIEW)
        [but instead we might as well make sure that drawkid's parent-seeing alg will not be messed up, since it'll be used
        inside whatever subthing draws we call, anyway]
        """
        ###e undefined in API so far: what if func says "draw later" (eg for transparency) -- do we do all that too, before we return??
        # guess: yes, but we'll need special drawing-env settings to tell primitives inside func that we're doing incremental drawing,
        # since it'll affect things like whether it's ok to write into the depth buffer for transparent objs obscuring visible ones
        # (useful for glselect code but would mess up subsequent incr drawing).
        def func1(self = self, func = func):
            res = func()
            self.env.glpane.swapBuffers() # update display [needed]
            return res
        ran_already_flag, funcres = self.run_OpenGL_in_local_coords( func1 )
            # note: this runs in self or first delegate that's a Highlightable, for now; that determines its gl state & coordsys
        assert ran_already_flag
        return funcres
    #e should we change to doing the action on_release_in, rather than on_press?
    delegate = Highlightable(
        plain, ##e should this depend on enabled? probably yes, but probably the caller has to pass in the disabled form.
            ###e at least for the Mac, maybe it also ought to depend on whether the application is active (frontmost) and will respond to clicks.
        If( enabled, highlighted, plain), # revised 070109 to depend on enabled [#k does this cause the delegate expr itself to be remade??]
        on_press = _self.doit,
            # note: there was a bug in the prior form of this, "on_press = command" -- command to do should depend on enabled --
            ##e but i'm not sure if If(enabled,command,None) will work properly ###k TRY IT -- nevermind, using _self.doit now [070208]
        sbar_text = text
            #e should sbar_text depend on enabled?? yes, but need to revise callers then too -- some of which make the text depend on it
     )
    pass # end of class ActionButton

PrintAction = print_Expr ###e refile (both names if kept) into an actions file

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
"""

# end
