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

# == class Rect

def coerce_to_color(color):#e refile; stub
    print 'used stub coerce_to_color on',color ####@@@@
    return color

class Rect(Widget2D):
    """Rect(width, height, color) renders as a filled x/y-aligned rectangle
    of the given dimensions and color, with the origin on bottomleft,
    and a layout box equal to its size (no margin).
       If color is not given, it will be black [#e should be a default attrval from env].
       If height is not given, it will be a square (even if width is a formula and/or random).
       See also: RectFrame, ...
    """
    #e declare arg/option types and defaults, similar to NamedLambda -- ###K NOT SURE THE FOLLOWING IS A GOOD WAY
    def _init_args(self, width, height = None, color = None): ####@@@@ CALL ME
        self.opts.width = float(width) # float() serves as a type decl -- it can still make a formula, not forcing eval yet
        if height is None:
            height = width #### WRONG -- the real situation is, default formula for height is width.
            # ie the formula ends up like f.height = f.width, NOT f.height = same formula that f.width is. ####@@@@ FIX THIS.
            # maybe this means self.formulas and self.opts are the same thing??
        self.opts.height = float(height)
        if color is None:
            color = black #####e better would be to grab a default Rect.color from the rule-env... which we don't have yet.
            # GENERAL PROBLEM: we don't usually want to type-coerce until we instantiate... tho we might record it now...
            # or do it at the formula level... hmm....
            # QUESTIONS: if env has a rule, should it be used AFTER we coerce args, and supply defaults, incl height = width?
        self.opts.color = coerce_to_color(color)
        return
    ###e set up formulas for bright and btop in terms of width & height
    # basically: bright = width, btop = height
    def _init_formulas(self): ####@@@@ CALL ME, or maybe this code should just be part of _init_instance
        f = self.formulas
        f.bright = f.width # automatically inherits from opts.width [or should those opts store right into formulas? I doubt it.]
        f.btop = f.height
        f.bbottom = 0 # same as default
        f.bleft = 0
        return
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, self.fix_color(self.color)) #e move fix_color into draw_filled_rect? 
        glEnable(GL_CULL_FACE)
    pass

# == comment snippets from other variants of Rect

#e let arg 2 or 3 be more drawable stuff, to center in the rect?
#e if color None, don't draw it, just the stuff?

#e Rect is an example, not general enough to be a good use of this name

### Widget2D gives us defaults for bright etc, and rules like width = bright + bleft

##        print "drawing Rect",self.args
### -- what could we print to indicate *which subexpr* we're drawing? esp which DebugDraw subexpr?
# once we have a drawing env, it should have an attr for whether to print debug info like this
# and its "address" or other sort of "posn in state".

##e need to fix: attr decls used here, which need rules from self's option formulas and arg formulas or exprs

# what about these attrnames they define -- methods with ordinary names? the expr version needs those as formulas, for data attrs,
# and as call-exprs or method-exprs, I suppose, for methods. Hmm... guess: define a helper class, not the Expr subclass itself. ###@@@

# end
