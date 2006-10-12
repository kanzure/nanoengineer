'''
Rect.py   [likely to be pulled into a larger file once it's done]

$Id$
'''

from basic import * # autoreload of basic is done before we're imported

import draw_utils
reload_once(draw_utils)

from draw_utils import *

import widget2d
reload_once(widget2d)

from widget2d import Widget2D ###e rename module, to same caps?

# === old code for Rect

class Rect(Widget2D): #e example, not general enough to be a good use of this name
    "Rect(width, height, color) renders as a filled rect of that color, origin on bottomleft"
    def init(self):
        self.bright = self.args[0]
        self.btop = self.args[1]
        self.color = self.args[2] # or dflt color? note, it might be symbolic
        #e let arg 2 or 3 be more drawable stuff, to center in the rect?
        #e if color None, don't draw it, just the stuff?
    def draw(self):
        glDisable(GL_CULL_FACE)
##        print "drawing Rect",self.args ####@@@@
        ### -- what could we print to indicate *which subexpr* we're drawing? esp which DebugDraw subexpr?
        # once we have a drawing env, it should have an attr for whether to print debug info like this
        # and its "address" or other sort of "posn in state".
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, fix_color(self.color))
        glEnable(GL_CULL_FACE)
    pass

# ==

# let's grab code for Rect and try to make it look ok... remember, this code doesn't force it to work a certain way,
# rather it may force the type inference, but as an implem it only provides the default value;
# of course that might just mean it defines methods which don't have to be used...

# class Rect, copied from testdraw.py -- could things like this "just work", getting built into Exprs but knowing default implem?
# but what about these attrnames they define -- methods with ordinary names? the expr version needs those as formulas, for data attrs,
# and as call-exprs or method-exprs, I suppose, for methods. Hmm... guess: define a helper class, not the Expr subclass itself. ###@@@
class Rect_obs_eg(Widget2D): #e example, not general enough to be a good use of this name
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

# ==

class drawing_env:
    def __init__(self, glpane):
        #e needs what args? glpane; place to store stuff (assy or part, and transient state); initial state defaults or decls...
        pass
    def make(self, expr, tstateplace):
        #e look for rules
        #e Q: is this memoized? does it allocate anything like a state index, or was that already done by customizing this env?
        print "making",expr#####@@@@@
        return expr.make_in(self, tstateplace) #####@@@@@@ IMPLEM, see class xxx below
    def _e_eval_expr(self, expr):
        ###e look for _e_eval method; test for simple py type
        assert 0, "nim"####@@@@
    def _e_eval_symbol(self, expr):
        assert 0, "nim"####@@@@
    pass

class xxx: # widget expr head helper class, a kind of expr
    def make_in(self, tstateplace, env):
        return self.__class__(self, tstateplace, env, _make_in = True) #####@@@@@ tell __init__ about this
            # note: _make_in causes all args to be interpreted specially
    def __init__(self): ##### or merge with the one in Expr, same for __call__
        pass
    pass

class Rect_try3(xxx):
    def draw(self): ###e see comments in _try2;
        ##e need to fix: fix_color, and attr decls used here, which need rules from self's option formulas and arg formulas or exprs
        fix_color = self.env.fix_color # guess
        glDisable(GL_CULL_FACE)
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, fix_color(self.color))
        glEnable(GL_CULL_FACE)
    pass

#e above:
# code for a formula expr, to eval it in an env and object, to a definite value (number or widget or widget expr),
# which no longer depends on env (since nothing in env is symbolic)
# but doing this might well use attrs stored in env or rules/values stored in object, and we track usage of those, for two reasons:
# - the ones in env might change over time
# - the ones in the object might turn out to be general to some class object is in, thus the result might be sharable with others in it.
# so we have eval methods on expr subclasses, with env and object as args, or some similar equiv arg.


