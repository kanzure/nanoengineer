# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
ToggleShow.py

$Id$


#e needs cleanup
"""

##nim: [obs? maybe not]
##    StateRef, syntax and implem
## see comments from 061121
#
##e see also old code in ToggleShow-outtakes.py

# Hmm, I discovered by accident 061203 1007p that the following were not being processed by ExprsMeta:
##weird val (('open_icon', 'ToggleShow')): an Expr that is not free in _self <Overlay#3945(a)>
##weird val (('closed_icon', 'ToggleShow')): an Expr that is not free in _self <Overlay#3952(a)>
##weird val (('openclose', 'ToggleShow')): an Expr that is not free in _self <Highlightable#3959(a)>
# so I will make them processed by it, by removing the free in _self condition (needed for State too),
# but I wonder if that will break this, or maybe fix some of its occasional problems...

from exprs.Highlightable import Highlightable

from exprs.Rect import Rect

from exprs.TextRect import TextRect

from exprs.Column import SimpleRow, SimpleColumn

from exprs.Overlay import Overlay

from exprs.If_expr import If_kluge
from exprs.instance_helpers import InstanceMacro, _this
from exprs.attr_decl_macros import Arg
from exprs.widget2d import Widget2D
from exprs.StatePlace import set_default_attrs
from exprs.py_utils import printnim
from exprs.__Symbols__ import _self

## Set - not yet needed
# [see controls.py [moved to Set.py] for a prototype, 061130, which takes a stateref rather than an lval as arg1 -- might be wrong --
#  update 061204 -- yes, was wrong, revising, see Set.py ]

##e should try using State here once it's tested

# ==

StateRef = Automatic = State = 'needs import'
_my_node = 'needs implem'

class ToggleShow(InstanceMacro):
    # args
    thing = Arg(Widget2D)
    label = Arg(Widget2D, TextRect("label")) #e or coerce text into a 1-line TextRect -- how do we declare that intent??

    if 0: # first make it work with a self-made stateref only, imitating Highlightable, using transient state
        stateref = Arg(StateRef, Automatic) ###k assumes the dflt can be a way to make one, not a literal one

        ## Q: how does each stateref we have, e.g. the one here meant for 'open', relate to StatePlace args
        # we might make or get from a superclass? (like the ones now in Highlightable.py but to be moved to a super of it)
        # if caller passes one, no need for our own, but to make our own, we'd make it in a StatePlace of our own, I think. ##e 061117

    if 0 and 'maybe':
        ##e might need to also say it's supposed to be boolean
        # note, on 070115 I revised StateRef (still a stub) but might have broken it due to the arg being passed here (not tested)
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

    if 1: # works fine, but as of 061126 late, comment out the remaining stmt, since done in InstanceOrExpr superclass rather than here
        pass ## transient_state = StatePlace('transient') #e move into super along with the ones in Highlightable of which this is a copy
        #e rename stateref to be specific for open, maybe open_stateref, in that if 0 code above
        # devel scratch: transient_state is an attr_accessor, which lets you do getattr and setattr.
        # but what we want it to do for us is tell us an lval for the attr 'open'
        # so we can retain that, attached to self.open somehow -- as its actual lval, maybe? not sure.
        # but much like that, since get or set self.open should work that way.
        # so a stateref (instance of StateRef) is basically an instance which acts as an lval... and can be attached to an attr.
        # But ExprsMeta right now insists on making its own lval, being passed a formula. Should we kluge-adapt to that or change it?
        # Guess: better & maybe easier to change it. So we have a new kind of object, not a formula (or a special kind of one),
        # to use as an rhs and process by ExprsMeta. It's not an lval, that's per-Instance. Is it a formula for making an lval?###
        # But it might be semantically different, since we don't store the lval as the value for self.open,
        # but as the value for its lval. hmm.... can we tell ExprsMeta to do this by an assignment to open
        # of a wrapped formula? it means, get the lval not by making one whose vals come from this formula
        # but make a property whose lvals come from this formula (which should be per-instance but time-constant, maybe,
        # tho if not time constant, it might be ok -- not sure ##e).

        ## open = State('transient','open')
            ### hmm... maybe 'open' needn't be passed if it gets it like Arg or Option does... maybe the kind is also default something?
            # so: open = State()? bt say the type and dfault val -- like I did in this:
            # staterefs.py: 181:     LocalState( lambda x = State(int, 1): body(x.value, x.value = 1) ) #

        # see if this gets the expected asfail: it does! [061121 late]
        ## set_default_attrs( transient_state, open = True)

    if 0: # this will be real code someday when no longer nim, but use an easier way first.
        open = State(bool, True) # default 'kind' of state depends on which layer this object is in, or something else about its class
            # but for now make it always transient_state
            # this is a macro like Option
            # it takes exprs for type & initial val
            #  but those are only evalled in _init_instance or so -- not yet well defined what happens if they time-vary
            # and note, that form doesn't yet let you point the state into a storage place other than _self.ipath... should it??
            # but the importance is, now in python you use self.open for get and set, just as you'd expect for an instance var.

    else:
        def get_open(self): #k
            return self.transient_state.open
        def set_open(self, val): #k
            self.transient_state.open = val
            return
        open = property(get_open, set_open)
        pass

    def _init_instance(self):
        super(ToggleShow, self)._init_instance()
        set_default_attrs( self.transient_state, open = True)

    # constants
    # Note, + means openable (ie closed), - means closable (ie open) -- this is the Windows convention (I guess; not sure about Linux)
    # and until now I had them reversed. This is defined in two files and in more than one place in one of them. [bruce 070123]

    open_icon   = Overlay(Rect(0.4), TextRect('-',1,1))
    closed_icon = Overlay(Rect(0.4), TextRect('+',1,1))

    if 0:
        open_icon   = TextRect('-',1,1) #stub
        closed_icon = TextRect('+',1,1) #stub
    else:
        ####@@@@ I vaguely recall that Highlightable didn't work on text!
        # and indeed, highlighting doesn't seem to be working on those.
        # if so, the above'll need revision until that's fixed.
        # BUT, with these grays anyway, clicks on the text are working. But it might be because the grays are behind them. ###k
        if 0 and 'varying rect sizes':
            # how it was during debugging
            open_icon   = Overlay(Rect(0.5,1), TextRect('-',1,1)) # added 0.5 061120 1018p temp debug kluge
            closed_icon = Overlay(Rect(1,0.5), TextRect('+',1,1)) #061120 changed impicit 1 -> 0.5
        else:
            # easier on the mouse-hand and eye
            open_icon   = Overlay(Rect(0.4), TextRect('-',1,1)) # added 0.5 061120 1018p temp debug kluge
            closed_icon = Overlay(Rect(0.4), TextRect('+',1,1)) #061120 changed impicit 1 -> 0.5

    # _value, and helper formulae

    ## open = stateref.value # can we make it work to say Set(open, newval) after this?? ####k
        # the hard part would be: eval arg1, but not quite all the way. we'd need a special eval mode for lvals.
        # it'd be related to the one for simplify, but different, since for (most) subexprs it'd go all the way.
    ## openclose = If( open, open_icon, closed_icon )

    # Status as of 061121 421p: both if 0 and if 1 cases seem to work fine, provided you restart when changing between them.
    # (Testing was not extensive, so it might turn out that avoiding other reloads is also needed.)
    # The known bugfixes that led to this:
    # - selobj = None in some places (not sure which are needed).
    # - no usage/change tracking by stateplaces that get set during draw (or that contain glname -- don't know if that matters).
    # - no usage/change tracking by set_default_attrs.
    # And other changes that might be helping:
    # - don't recycle glnames.
    # - some others I forget, which are marked by 061120 (or maybe 061121)
    #   in comments or stringlits (in this or other files).
    #  - don't track_use on exception in Lval get_value (BUT, i suspect it's actually wrong not to; see cmt there 061121)
    #  - more conservative selobj_still_ok
    #  - mode.update_selobj(event) in leftClick and ReleasedOn
    #  - self.inval(mode) #k needed? (done in two places per method, guess is neither is needed)
    #
    # Soon, the needed or not of the above workarounds should be sorted out,
    # and most of the following debugging-log commentary should be removed. #e

    if 1:
        openclose = Highlightable( If_kluge( open, open_icon, closed_icon ),
                                   on_press = _self.toggle_open,
                                   sbar_text = _this(Highlightable).ipath # this line just for debugging
                                   )
            ##e we should optim Highlightable's gl_update eagerness
            # for when some of its states look the same as others!
            # (no gl_update needed then, at least not just for that change --
            #  note, this is a special case of the inval optim for when something was changed to an equal value)
            #e someday be able to say:
            # on_press = Set( open, not_Expr(open) )
            ## silly: on_press = lambda open = open: open = not open # no, open = not open can't work
            # in fact, you can't use "lambda open = open", since open has to be replaced by ExprsMeta

            ##k can on_press be an expr to eval, instead of a (constant expr for a) func to call?? ####k
            ## on_press = call_Expr( lambda xxx: self.open = not self.open, xxx) # no, no assignment in lambda
        pass
    else:
        # so try this form 155p - bug of not working is gone, but now, it always draws the + form! Is it drawing the old one
        # due to same glname? no (I guess), they should have different names!
        # is it drawing old one due to not realizing that one is obs? ######where i am
        # is it failing to invalidate the drawing effect of this instance? (after all, who is it that sees the usage of open?
        # it must be glpane as if we were using a prefs variable here! is that sufficient?? does it work ok re selobj system???###)
        # IS THE CHOICE OF DELEGATE being invalled? I think so, since I see the alignment calcs get updated,
        # or is that just the live gltranslate inside the draw method?
        # HEY, when I covered up the glpane with this app, then uncovered it, suddenly I see the new selobj,
        # then the conjunction of both! how can that be? thes are similar to whgat I sawe earlier. conclusion: weird update bugs
        # in selobj/highlight system, i guess. (maybe it does the main draw and highlight draw on different objects?
        # try altering color, or using 4 images not 2. ###)
        # now it sems that mouse around on the closed that looks like open is what makes it look like clsed, or like both.
        # yes, repeatable, for either change of state. Ok, try that in 'if 1' case of this. ### siilar but not identical
        # and that time is again does get stuck into the closed state, with the grayrect no longer optiming redraws re stencil buffer.
        # .. reviewing code in Highlightable, I see some things to try -- see its 061120 comments.
        # ... I did all that, and the 'gray becomes inactive bug' in 'if 1 openclose case' is still there. howbout the if 0 case?
        # [later: i think that still had some bad bugs too, not much changed.]
        # for more, see string lits containing 061120, and for a log see big cmt just below here.
        openclose = If_kluge( open,
##                              Highlightable(open_icon,   on_press = _self.toggle_open, sbar_text = _self.ipath),
##                              Highlightable(closed_icon, on_press = _self.toggle_open, sbar_text = _self.ipath),
                              ###BUG - same ipaths? NO, I USED _self BUT MEANT _this(Highlightable)!!! AAArgh! ##k works now?? yes
          Highlightable(open_icon,   on_press = _self.toggle_open, sbar_text = _this(Highlightable).ipath),
          Highlightable(closed_icon, on_press = _self.toggle_open, sbar_text = _this(Highlightable).ipath),
                    )
        pass

    def toggle_open(self):
        if 'yet another shot in the dark 061120 1001p':
            self.env.glpane.selobj = None ##### THIS SEEMS TO FIX THE BUG, at least together with other potshots and if 0 openclose.
            # theory: old selobjs are being drawn highlighted even when not drawn normally. they mask the real stuff.
            # but with if 1 openclose it doesn't fix the different bug (gets wedged into closed state). why not???
            # this is with no recycling of names, and also selobj=None in recycler.
            # guess: in if 1, the same glname is used... but it's same literal selobj too, right? and remaking is turned off.
            # I don't have a theory for 'if 1' bug cause, or for why it only affects the inner thing, not outer one.
            # Does it only affect that after it's once been hidden? ### if so, is it "you were selobj and then not drawn" that makes it
            # happen? that might fit the data but I don't see how that could work.
            # So I added a 2nd 0.5 so neither gray rect form covers the other. but first inner close hits the bug of making it
            # inactive and act non-highlighted. so i wondered if the glname really only covers the openclose? code says so.
            # I added a try/except to be sure the PopName occurs; not triggered during this if 1 bug.
            #
            # Stopping for night 061120 1027p, summary: I understand some bug causes but not all; wish I could see inside the glselect
            # reasoning, so plan to add debug prints to glpane. Need to think thru its assumptions re chaotic glname/selobj/size/
            # whether-drawn situation, see which are wrong, which might cause the bug. Also - can event processing occur during
            # paintGL? I hope not, but verify. Also maybe GLPane needs to track frame numbers for selobjs being drawn,
            # stencil bits being made, vs selobj state mods as tracked by inval....
            #
            # update 061121 953a, where I am: after basic fixes elsewhere [some stateplaces not tracked, some usage tracking disallowed],
            # and still using all kluge/workarounds from 061120, bug seems totally fixed for if 0 case, all or most for if 1 ##k.
            # IIRC it was slightly remaining before some usage tracking disallowed, but that is not complaining, which is suspicious.
            # Anyway, if if 1 works too, plan is to gradually remove the kluges and clean up and keep it working.
            # BUT it looks like if 1 (using reloaded code) has a bug of some disallowed usage... details to follow.
            # BUT after restart I don't see it. BTW I recently reenabled reloading -- could that have fixed some bugs (how???),
            # or could it be that they now occur after reloading but not before it?? indeed, this is after changing if 1->0 and reload,
            # and looks like it might relate to old state being there, and
            ###### WHAT IF RELOADED CODE USES THE SAME STATE DIFFERENTLY AND HAS A BUG? #####
            # [but, that bug aside, there is still a real problem with whatever usage tracking this
            #  set_default_attrs is doing. [fixed now]]


        if 0: #061121 822p i've been using if 1 forever, let's see if if 0 works here: it does! either is ok, given the open property.
            old = self.transient_state.open
            self.transient_state.open = new = not old
            ## print "toggle_open changed self.transient_state.open from %r to %r" % (old, new,)
        else:
            old = self.open
            self.open = new = not old
            ## print "toggle_open changed self.open from %r to %r" % (old, new,)
            # [obs cmt re open property, but was it talking about that or a partly working State decl? as of 061121 I can't remember:]
                # should work but doesn't, see bug in notesfile, it delegates self.open eval to _value: 061118 late
                # (or is it just because the val was not initialized? GUESS, YES ###k)
                ## self.open = not self.open ### can this work??? it will call set of self.open -- what does the descriptor do for that?
                # (asfail, or not have __set__ at all?? FIND OUT. the notesfile says the same thing but for a different Q, what was it?)
                ## WE SHOULD MAKE THIS WORK even if we also make on_press = Set( open, not_Expr(open) ) work, since it's so natural.
        ### BTW what is it that will notice the inval, and the usage of this when we drew, and know that gl_update is needed?
        # the same thing that would know a display list content was invalid -- but where is it in our current code (if anywhere)?
        # I vaguely recall a discussion of that issue, in the displist chunk code or notesfile, weeks ago.
        # some way to have lvals representing displist contents or frame buffer contents, whose inval means an update is needed.
        printnim("toggle_open might do a setattr which is not legal yet, and (once that's fixed) might not properly gl_update yet")
        return

    _value = SimpleRow(
        openclose,
        SimpleColumn(
            label,
            If_kluge( open,
                      thing,
                      TextRect("<closed>") #####BUG: I wanted None here, but it exposes a logic bug,
                          # not trivial to fix, discuss in If or Column [see also a discussion in demo_MT.py, 070302];
                          ##e Spacer(0) can also be tried here [##e should what to show here be an arg??]
                      )
        )
    )

##    if 0: # if 0 for now, since this happens, as semiexpected:
##        ## AssertionError: compute method asked for on non-Instance <SimpleRow#3566(a) at 0xe708cb0>
##
##        ##e do we want to make the height always act as if it's open? I think not... but having a public open_height attr
##        # (and another one for closed_height) might be useful for some callers (e.g. to draw a fixed-sized box that can hold either state).
##        # Would the following defns work:?
##
##        # (They might not work if SimpleRow(...).attr fails to create a getattr_Expr! I suspect it doesn't. ####k )
##
##        # [WARNING: too inefficient even if they work, due to extra instance of thing -- see comment for a fix]
##        open_height = SimpleRow(
##            open_icon,
##            SimpleColumn(
##                label,
##                thing
##            )).height   ##k if this works, it must mean the SimpleRow gets instantiated, or (unlikely)
##                        # can report its height even without that. As of 061116 I think it *will* get instantiated from this defn,
##                        # but I was recently doubting whether it *should* (see recent discussions of TestIterator etc).
##                        # If it won't, I think wrapping it with Instance() should solve the problem (assuming height is deterministic).
##                        # If height is not deterministic, the soln is to make open_instance and closed_instance (sharing instances
##                        # of label), then display one of them, report height of both. (More efficient, too -- only one instance of thing.)
##                        # (Will the shared instance of label have an ipath taken from one of its uses, or something else?
##                        #  Guess: from the code that creates it separately.)
##
##        closed_height = SimpleRow(
##            closed_icon,
##            SimpleColumn( # this entire subexpr is probably equivalent to label, but using this form makes it more clearly correct
##                label,
##                None
##            )).height

    pass # end of class ToggleShow

# end
