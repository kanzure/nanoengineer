'''testdraw2_cannib.py - being cannibalized 
'''

from testdraw import *
from debug import print_compact_traceback
pt = print_compact_traceback

# ==

#e these Exprs will need a way to notice when they get deep enough (in attrs or calls) that they ought to have a value already...
# maybe just default "compiling rules" for that in the env? so they'll need to autocompile selves as they build... but in what env??

### Exprs.py, __Symbols__.py

# ==

# old constructors -- this will break drawing (silently, since <any expr>.draw will be callable!)
#####@@@@@ do we need to make expr.attr callable? not in the egs I can think of right now!

#####@@@@@ from __Symbols__ import Column, Rect, Row, Button, If

# constructors
from __Symbols__ import NamedLambda, Hidden, Centered

##NamedLambda = Stub
##Hidden = Invisible # not quite right (only issue is depth writing, i think; Invis wants it, we don't want it)
##Centered = Stub
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

old code for ToggleShow [nim] was here, now in its own outtakes file


# now how do we draw it?
# - set up rendering env, env for specific frame, approp places for state; then call something, using this expr
# and how does other code here use testexpr? it just calls testexpr.draw(), no args! clearly not enough,
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
        ### I think I'd rather say 8 * pixelwidth or 8 * pixelsize or 8 * pixel, not 8 * pixels
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

#print Boxed - above is WRONG in some ways: [060911, recalled, analyzed on paper some days ago]
# - we want to instantiate thing, then modify its interface with outside, altering bbox and adding drawing code, leaving rest same
#   - but not by thing(width = width + extra), since that risks internally modifying thing; we're more like Column in how we use thing;
#     i suppose we need "scenegraph prims" to draw by drawing various things at various places -- but Overlay is enough.
#     So the only hard issue is how we access bbox parts of thing instance, and let those differ for ourselves.
#     - How do we name that (bbox aspect of interface), for thing and for self, so we can set up the desired formula?
#     - And how do we say "instantiate thing"? (as opposed to using it as a widget expr, to make more than one subwidget.) Resolve??
# - thing.width can only work if thing is an instance -- do we say that in our arglist, or assume it somehow?

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


# moved to Rect.py: or an outtakes file for it:
### Rect_obs_eg,
### Rect_try2


class Overlay_try2(DelegatingWidget2D):
    def draw(self):
        for a in self.args: # does args get computed from _e_args by evalling formulas, removing None, etc? call it .kids instead?
            #try1 draws args in reverse order, i guess we will too ###@@@
            a.draw() # this assumes these draw methods don't change the coordinate system...
        pass
    pass

Point = Stub
from __Symbols__ import p1, p2 #k ok but not yet defined in this module, need to fix that
class Cylinder(WidgetExpr):
    ###e digr, wrong class, i mean things that have an axis-segment, hmm maybe cyl is the prototype; they need perp dir too;
    # one way it will often be called is for the edges in some kind of 3d network or polyhedron...
    # we'll pass (to such a network iterator) WEs for each type of part (vertex, edge, face, cell)... note that Table & Column
    # are special cases!! (And we might well want display/event bindings on inter-cell edges of those, as well as in cells.) #####@@@@@
    arglist = ((p1, Point), (p2, Point))###k more... actually the args could just as well be an edge, and need an alignment too...
    pass

# ==

class Column_try4orso(Stub):
    # kids
    # layoutboxes combine up, then cumulate down to make coord systems, each defined in terms of prior one (unless indices nest)
    # ie coords[i] = coords[i-1] translated down a bit
    pass

    kids = [] # kluge for import
    
    # [obs stuff removed]


        # it might be easier if things like coords are attrs of inter-kid objects, not of kids,
        # so rule for every kid is same (use input coords, define output coords)
        # e.g. for kid, kid.after.coords = kid.before.coords + kid.height
    pass

RandomPoints2D = Stub

class yyy:# drawable instance
    def _compute_delegate(self):
        #e look at arglist decl, compile from args [assuming there's a head and args, i guess] [also applies to options]
        self.expr.arglist_decl
            ### do all exprs have this??? do they have only one?
            # don't we really "eval the expr in this place", which does this for us, and does it even for helper-class exprs?
        #e expand rule body or instantiate helper class -- this too is part of evalling the expr
        return eval_expr( self.expr, self.place) # but why do i say "eval" since we don't yet assume formulas have curvals, do we?
            # maybe we do... it's that the retval is the drawable object's class and init data... we didn't need to descend inside...
            # if the class itself depended on curvals, we use curvals and record usage like with anything. [is this true? yes.]
    def draw(self):
        self.delegate.draw() # but it might be more common to forward, by callers using this value and depending on it... not sure

    kidpoints = [] ### kluge for import, should be RandomPoints2D(10, selfavoiding = True)
    for kidpoint in kidpoints:
        self.makekid(Line( _2dto3d(kidpoint), _2dto3d(kidpoint) + DZ * RandomFloatInRange(1,2), color = RandomColor)) # arb index
    
# end
