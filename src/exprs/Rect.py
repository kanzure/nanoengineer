'''
Rect.py   [likely to be pulled into a larger file once it's done]

$Id$
'''

from basic import *
from basic import _self

import draw_utils
reload_once(draw_utils)
from draw_utils import *

# == class Rect

class Rect(Widget2D):
    """Rect(width, height, color) renders as a filled x/y-aligned rectangle
    of the given dimensions and color, with the origin on bottomleft,
    and a layout box equal to its size (no margin).
       If color is not given, it will be gray [#e should be a default attrval from env].
       If height is not given, it will be a square (even if width is a formula and/or random).
       See also: RectFrame, ...
    """
    # arguments (order, type, defaults)
    _args = ('width', 'height', 'color')
    _TYPE_width = _TYPE_height = Width
    _TYPE_color = Color
    _DEFAULT_color = gray #e (in future, these defaults can be overridden by the rule env)
    _DEFAULT_height = _self.width # (a formula involving attrs of _self)
    _DEFAULT_width = 10 # pixels (??)
    
    # formulas for layout box attrs
    bright = _self.width 
    btop = _self.height
    # fyi, these are not needed (same as the defaults in Widget2D): let's prove that by leaving them out, 061103 144p:
    # also I bet they need _DEFAULT_ or they won't be customizable! test sometime. #k
    # hmm, maybe they don't need to be customizable? decide sometime. that is, if they're "internal" then they shouldn't be custable.
##    bbottom = 0
##    bleft = 0
    
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, self.fix_color(self.color)) #e move fix_color into draw_filled_rect? 
        glEnable(GL_CULL_FACE)
    pass

class Rect2(Widget2D): # this is Rect in a newer syntax, not yet working as of 061031
    "#doc - grab from above"
    # args
    width = Arg(Width, 10)
    height = Arg(Width, width)
    color = ArgOrOption(Color, gray)
    # formulas
    if 0:
        # use this to test whatever scheme we use to detect this error, once we put one in [disabled 061105 until other things work]
        bright = width ######@@@@@ PROBLEM: in ns, width and bright will have same value, no ordering possible -- how can it tell
            # which one should be used to name the arg? It can't, so it'll need to detect this error and make you use _self. prefix.
            # (in theory, if it could scan source code, or turn on debugging during class imports, it could figure this out...
            #  or you could put the argname in Arg or have an _args decl... but I think just using _self.attr in these cases is simpler.)
        printnim("make sure it complains about bright and width here")
        btop = height
    else:
        printfyi("not yet trying to trigger the error warning for 'bright = width'")
        bright = _self.width
        btop = _self.height
##    # fyi, these are not needed (same as the defaults in Widget2D):
##    bbottom = 0
##    bleft = 0
    
    def draw(self): # same as in class Rect
        glDisable(GL_CULL_FACE)
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, self.fix_color(self.color)) #e move fix_color into draw_filled_rect? 
        glEnable(GL_CULL_FACE)
    pass


# old comments from Rect:
#
# a _C_attr can either be a method (compute rule), or a formula on _self (like here) --
# but if it's a formula, it can just be stored on the attr itself, as a descriptor! See notesfile 061024 for discussion.
####@@@@ _C_attr being formula is nim; if it's a py constant like 0 below (a degenerate formula), is that ambiguous?
# If so, maybe wrap it with something when it's a formula? (or when it's a callable but not a compute method?)
# related: if it's a callable, do we say it's a constant callable or do we treat that callable as the compute method?
# also related (but a digr): to denote a formula sin(_self.xx), can we replace sin with something.sin?
#
# [about layout box attrs:]
#####@@@@@ make these _DEFAULT_ so Rect can be customized to make them differ? #e If so, what's notation for pre-custom value?

##print "dir(Rect) is:",dir(Rect) #####@@@@@@
##for n1 in dir(Rect):
##    if not n1.startswith('_'):
##        print "Rect.%s =" % n1, getattr(Rect,n1)
##    pass

# == comment snippets from other variants of Rect

#obs comments here, but might be relevant elsewhere:
## - self.opts.width = float(width) # float() serves as a type decl -- it can still make a formula, not forcing eval yet
## - ... the real situation is, default formula for height is width.
##   ie the formula ends up like f.height = f.width, NOT f.height = same formula that f.width is. ####@@@@ FIX THIS.
##   maybe this means self.formulas and self.opts are the same thing??
## - QUESTIONS: if env has a rule, should it be used AFTER we coerce args, and supply defaults, incl height = width?    

#e let arg 2 or 3 be more drawable stuff, to center in the rect?
#e if color None, don't draw it, just the stuff?

#e Rect is an example, not general enough to be a good use of this name

### Widget2D gives us defaults for bright etc, and rules like width = bright + bleft

##        print "drawing Rect",self.xxxargs
### -- what could we print to indicate *which subexpr* we're drawing? esp which DebugDraw subexpr?
# once we have a drawing env, it should have an attr for whether to print debug info like this
# and its "address" or other sort of "posn in state".

##e need to fix: attr decls used here, which need rules from self's option formulas and arg formulas or exprs

# what about these attrnames they define -- methods with ordinary names? the expr version needs those as formulas, for data attrs,
# and as call-exprs or method-exprs, I suppose, for methods. Hmm... guess: define a helper class, not the Expr subclass itself. ###@@@

# end
