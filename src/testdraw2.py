'''testdraw2.py - testdraw.py was getting too big to edit conveniently
'''

#e needs cvs add, file header

from testdraw import *
from debug import print_compact_traceback
pt = print_compact_traceback

# ==

#e these Exprs will need a way to notice when they get deep enough (in attrs or calls) that they ought to have a value already...
# maybe just default "compiling rules" for that in the env? so they'll need to autocompile selves as they build... but in what env??

class Expr:
    "abstract class for symbolic expressions that python parser can build for us, from Symbols and operations including x.a and x(a)"
    def __init__(self, *args):
        self._e_args = args ###@@@ was __args -- do we need/want this __? maybe _e_ would be better? yes, change it.
        self._e_init()
    def __getattr__(self, attr):
        if attr.startswith('__') or attr.startswith('_e_'):
            raise AttributeError, attr 
        return getattr_Expr(self, attr)
    def __call__(self, *args, **kws):
        # print '__call__ of %r with:' % self,args,kws###@@@
        return call_Expr(self, args, kws)
    def __repr__(self):
        return str(self) #k can this cause infrecur?? 
    def __rmul__( self, lhs ):
        """operator b * a"""
        return mul_Expr(lhs, self)
    def __mul__( self, rhs ):
        """operator a * b"""
        return mul_Expr(self, rhs)
    def __rdiv__( self, lhs ):
        """operator b / a"""
        return div_Expr(lhs, self)
    def __div__( self, rhs ):
        """operator a / b"""
        return div_Expr(self, rhs)
    def __radd__( self, lhs ):
        """operator b + a"""
        return add_Expr(lhs, self)
    def __add__( self, rhs ):
        """operator a + b"""
        return add_Expr(self, rhs)
    def __rsub__( self, lhs ):
        """operator b - a"""
        return sub_Expr(lhs, self)
    def __sub__( self, rhs ):
        """operator a - b"""
        return sub_Expr(self, rhs)
    def __neg__( self):
        """operator -a"""
        return neg_Expr(self)
    def __float__( self):
        """operator float(a)"""
        print "kluge: float(expr) -> 17.0"####@@@@
        return 17.0
    def _e_replace(self, reps):
        "perform replacements (reps) in self, and return the result [same as self if possible?] [some subclasses override this]"
        # for most kinds of exprs, just replace in the args, and in the option values [####@@@@ NIM].
        args = self._e_args
        modargs = tuple(map(reps, args)) ##k reps is callable??
        if args == modargs:
            ##k requires fast == on Expr, which unlike other ops is not meant as a formula
            # (could it be a formula, but with a boolean value too, stored independently???)
            return self
        return self.__class__(*modargs)
    pass

class getattr_Expr(Expr):
    def __call__(self, *args, **kws):
        print '__call__ of %r with:' % self,args,kws###@@@
        assert 0, "getattr exprs are not callable [ok??]"
    def _e_init(self):
        assert len(self._e_args) == 2 #e kind of useless and slow #e should also check types?
    def __str__(self):
        return str(self._e_args[0]) + '.' + self._e_args[1] #e need parens?
    pass

class mul_Expr(Expr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s * %s" % self._e_args #e need parens?
    pass

class div_Expr(Expr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s / %s" % self._e_args #e need parens?
    pass

class add_Expr(Expr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s + %s" % self._e_args #e need parens?
    pass

class sub_Expr(Expr):
    def _e_init(self):
        assert len(self._e_args) == 2
    def __str__(self):
        return "%s - %s" % self._e_args #e need parens?
    pass

class neg_Expr(Expr):
    def _e_init(self):
        assert len(self._e_args) == 1
    def __str__(self):
        return "- %s" % self._e_args #e need parens?
    pass

class call_Expr(Expr):
    def _e_init(self):
        assert len(self._e_args) == 3
        self._e_callee, self._e_call_args, self._e_call_kws = self._e_args
        #e might be useful to record line number, at least for some heads like NamedLambda; see Symbol compact_stack call for how
    def __str__(self):
        if self._e_call_kws:
            return "%s(*%r, **%r)" % self._e_args #e need parens?
        elif self._e_call_args:
            return "%s%r" % (self._e_callee, self._e_call_args)
        else:
            return "%s%r" % (self._e_callee, self._e_call_args) # works the same i hope
    pass

class Symbol(Expr):
    def _e_init(self):
        if len(self._e_args) == 0:
            self._e_name = "?%s" % compact_stack(skip_innermost_n = 3).split()[-1] # kluge - show line where it's defined
        else:
            (self._e_name,) = self._e_args
        return
    def __str__(self):
        return self._e_name
    def __repr__(self):
        ## return 'Symbol(%r)' % self._e_name
        return 'S.%s' % self._e_name
    pass

# ==

# support for "import __Symbols__" (necessary since we depend on python parser; even so it'll be a pain to define them all)

class FakeModule:
    #e when working stably, i could make it stable across reloads -- if Symbol (passed in) is also stable; so option should decide
    # make sure all of our private attrs or methods start with '__' (name-mangling is ok, so they needn't end with '__')
    def __init__(self, name, getattr_func):
        ## self.__name__ = name #k ok? not yet needed, anyway
        self.__path__ = "fakepath/" + name #k ok? maybe not, it might be some sort of dotted import path -- better look it up ####@@@@
        #e __file__?
        self.__getattr_func = getattr_func
    def __getattr__(self, attr):
        if attr.startswith('_'):
            print "fyi: fakemodule getattr got",attr # e.g. __path__
            if attr.startswith('__'):
                raise AttributeError, attr
            pass # let single-underscore names work normally as symbols, even though we warn about them for now
        # print "fyi: fakemodule getattr will make Symbol for",attr # this works
        res = self.__getattr_func(attr)
        setattr(self, attr, res) # don't ask me about this attr again!
        return res
    pass

import sys
sys.modules['__Symbols__'] = FakeModule('__Symbols__', Symbol)

# ==

# old constructors -- this will break drawing (silently, since <any expr>.draw will be callable!)
#####@@@@@ do we need to make expr.attr callable? not in the egs I can think of right now!

#####@@@@@ from __Symbols__ import Column, Rect, Row, Button, If

# constructors
from __Symbols__ import NamedLambda, Hidden, Centered, Set

##NamedLambda = Stub
##Hidden = Invisible # not quite right (only issue is depth writing, i think; Invis wants it, we don't want it)
##Centered = Stub
##Set = Stub # for an action that sets a stateref to the current value of a formula [what usage-tracking or subs effect does it have?]
##

def NamedLambda_OBS(name, arglist, body): #e more body args? options??
    """Return a code-object constructor which constructs code objects mostly equivalent to body,
    but with symbols in arglist lexically replaced in body by the arguments passed to the constructor.
       The code objects our return value constructs differ from body-with-replacements in these ways:
    the given name is used to find default option formulas from the using environment [#k details??];
    the argument values are preprocessed (type-coerced, defaulted) as specified in arglist;
    maybe the using environment can also specify processing on our return value, based on name (?).
    """
    ## res = Replace(body, arglist) # WRONG, we only do this when args are passed
    return Stub #e need a stub which is not so callable as Stub? maybe which prints its name once per event, when called?

NamedLambda = Symbol('NamedLambda') # or could import as usual

# If - needs rewrite; for that matter so does Row & Column

# types
##Widget = Stub
##StateRef = Stub
##ImageWidget = Widget # not sure if we want this to be a definite subtype
# could it be renamed to Image? possible name conflict (probably ok): import Image # from the PIL library
# I'll rename it.
from __Symbols__ import Widget, StateRef, Image

# constants
from __Symbols__ import Automatic

# == ToggleAction

from __Symbols__ import stateref

ToggleAction = NamedLambda( ###e need to initialize the state if not there? NO, that's the job of the stateref (formula) itself!
    'ToggleAction',
    ((stateref, StateRef),),
    Set(stateref, not stateref) ### will 'not' be capturable by a formula?
    )

# == ToggleButton

from __Symbols__ import stateref, false_icon, true_icon

ToggleButton = NamedLambda(
    'ToggleButton',
    ((stateref, StateRef),
     (false_icon, Image), #e add a default
     (true_icon, Image, false_icon), # same as false_icon, by default (default is a formula which can use prior symbols)
    ),
    Button(
        # plain image
        If(stateref,
           Overlay(Hidden(false_icon),Centered(true_icon)), # get the size of false_icon but the look of true_icon
               #e possible bugs: Centered might not work right if false_icon is not centered too; see also wrap/align options
               #e Overlay might work better outside, if otherwise something thinks the layout depends on the stateref state
           false_icon
        ),
        # highlighted image - ###e make this a lighter version of the plain image
        #e or a blue rect outlining the plain image -- I forget if Button assumes/implems the plain image always drawn under it...
        ###@@@ put this in somehow; missing things include my recollecting arg order of RectFrame, pixel units, dims of the icon, etc
        # actions -- for now, just do it immediately when pressed
        on_press = ToggleAction(stateref)
    ))

# == ToggleShow

ToggleFalseIcon = Rect(1,1,black) # stub
ToggleTrueIcon = Rect(1,1,gray) # stub

#e define default ToggleShow_stateref or StateRef value, in case env doesn't have one...

from __Symbols__ import thing, label, stateref
    
ToggleShow = NamedLambda(
    'ToggleShow',
    ((thing, Widget),
     (label, Widget, None),
     (stateref, StateRef, Automatic)),
        #e or should we specify a default stateref more explicitly? letting env override it as a feature of NamedLambda?
    Column( Row( ToggleButton(stateref, ToggleFalseIcon, ToggleTrueIcon),
                 label ),
            If( stateref, #k can you just plop in a stateref in place of asking for its value as a boolean? I guess so... it's a formula
                thing )
    ))

test_ToggleShow = ToggleShow( Rect(3,3,lightblue), "test_ToggleShow's label" )

#print test_ToggleShow

# now how do we draw it?
# - set up rendering env, env for specific frame, approp places for state; then call something, using this expr
# and how does other code here use textexpr? it just calls testexpr.draw(), no args! clearly not enough,
# but is this almost right (if args were put in), or do we need to do something other than "call draw method"??
# certainly we'd have to apply rules... then it's conceivable that could work; would it be ok? ###@@@
# - another poss: _e_run_in_env method.

# ==

from __Symbols__ import thing, gap, border, color, extra
from __Symbols__ import XXOverlay, XXRectFrame, Centered, With, pixels

Boxed = NamedLambda(
    'Boxed',
    ((thing, Widget),), # arglist
    dict(gap = 8 * pixels, border = 4 * pixels, color = white), # option defaults list, one poss form (not ordered, not general lhses)
##    gap,#?
##    border,#?
##    color,#? or have a way to pass in arb RectFrame options, like this one? and like border?
    With(dict(extra = 2 * gap + 2 * border), # alt syntax: With(extra = 2 * gap + 2 * border)(...) or With(opt=val, _arg = val)
        Overlay(
            RectFrame(thing.width + extra, thing.height + extra, thickness = border, color = color),
                ###e args not fully compatible, and maybe color should come first when not named,
                # and maybe border or borderwidth is better name
            thing,
            align = Centered # this can work by wrapping each element with Centered; should option name just be wrapper or wrap?
                # in some other uses of Centered or Row I used that option name... but I wonder if a difference is
                # in whether the alignment-shift is also seen from outside, or does outside still see the first elt as if unshifted?
        )
    ))

#print Boxed

# == some rules - obs stubs

def reduce_NamedLambda(expr): #e or a reducer class? to be used to wrap the expr??
    """a NamedLambda must always be used as a toplevel expr... and can be processed when encountered...
    this is supposed to run once on one being defined, which is then encountered as the head in other defs... probably the
    retval of this should be encountered as that head...
    """
    #e we might grab the pieces by pattern matching; for now do it by hand, let exceptions indicate syntax errors
    name, args, body = expr._e_args

class reduced_NamedLambda(Expr): # not sure of superclass
    def __init__(self, expr):
        name, args, body = expr._e_args
    def __call__(self, *args, **kws): #e overrides the one in Expr; now we can bind the args in the arglist - or can we?
            # no, we don't know lexenv yet, this is premature, unless done later...
        pass
    pass

# let's grab code for Rect and try to make it look ok... remember, this code doesn't force it to work a certain way,
# rather it may force the type inference, but as an implem it only provides the default value;
# of course that might just mean it defines methods which don't have to be used...

# class Rect, copied from testdraw.py -- could things like this "just work", getting built into Exprs but knowing default implem?
# but what about these attrnames they define -- methods with ordinary names? the expr version needs those as formulas, for data attrs,
# and as call-exprs or method-exprs, I suppose, for methods. Hmm... guess: define a helper class, not the Expr subclass itself. ###@@@
class Rect_obs_eg(WidgetExpr): #e example, not general enough to be a good use of this name
    "Rect(width, height, color) renders as a filled rect of that color, origin on bottomleft"
    def init(self):
        self.bright = self.args[0]
        self.btop = self.args[1]
        self.color = self.args[2] # or dflt color? note, it might be symbolic
        #e let arg 2 or 3 be more drawable stuff, to center in the rect?
        #e if color None, don't draw it, just the stuff?
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, fix_color(self.color))
        glEnable(GL_CULL_FACE)
    pass

#from __Symbols__ import Widget2D - following stubs are just to avoid import errors, totally wrong other than that
class Widget2D: pass
DelegatingWidget2D = Widget2D

class Rect_try2(Widget2D): ### Widget2D gives us defaults for bright etc, and rules like width = bright + bleft
    "Rect(width, height, color) renders as a filled rect of that color, origin on bottomleft"
    def init(self): ###e might replace this with some sort of arglist description, similar to the one in NamedLambda
        self.bright = self.args[0] ### these might be symbolic
        self.btop = self.args[1]
        self.color = self.args[2] # or dflt color? note, it might be symbolic
        #e let arg 2 or 3 be more drawable stuff, to center in the rect?
        #e if color None, don't draw it, just the stuff?
    def draw(self):
        ### fix_color is a method on self, I guess, or maybe on env (and env may either be self.env or an arg to this method -- guess, arg)
        # or maybe it has contribs from env, class, and glpane -- glpane to know what kind of color it needs,
        # env or glpane to know about warps or alphas to apply, class maybe, and something to know about resolving formulas (env?)
        ### we'll have fix_ for the dims too, handling their units, perhaps in a way specific to this class
        ### we'll have memoization code for all these attrs
        ### and we'll need better control of gl state like GL_CULL_FACE, if we can run this while it's already disabled
        glDisable(GL_CULL_FACE)
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, fix_color(self.color))
        glEnable(GL_CULL_FACE)
    pass

class Overlay_try2(DelegatingWidget2D): # this means, I think, Widget2D with arg1 used for layout... sort of like a "WidgetDecorator"
    def draw(self):
        for a in self.args: # does args get computed from _e_args by evalling formulas, removing None, etc? call it .kids instead?
            #try1 draws args in reverse order, i guess we will too ###@@@
            a.draw() # this assumes these draw methods don't change the coordinate system...
        pass
    pass

# end
