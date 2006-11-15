"""
widget2d.py

$Id$
"""
###e rename module, to same caps? hmm, maybe just to widget, since it has that class too? or move that class?

from basic import * # autoreload of basic is done before we're imported
from basic import _self

# ==

class Widget(InstanceOrExpr):
    # Widget can also be used as a typename for NamedLambda -- ok??
    # I guess it just means it can be used to coerce things... see docstring-comment in Widget2D. #####@@@@@
    """Class whose Instances will be drawable. [#doc more]"""
    def fix_color(self, color): #e move to glpane??
        """Return the given color, suitably formatted for passing to low-level drawing code for the current drawing medium.
        The color is assumed to be evaluated (i.e. no longer a formula), but perhaps in some general data format
        and perhaps needing to be subjected to global color transformations stored transiently in the drawing medium object
        (e.g. a color warp or constant alpha, stored in the glpane).
        [#e If it proves unworkable for this method to know the current drawing medium,
         it will probably be replaced with more specific methods, eg fix_color_GL and fix_color_POVRay.]
        [#e Will we have to have variants of _GL for returning 3 tuples or 4 tuples as the color?]
        [#e Will we have to worry about material properties?]
        """
        return color ### stub
            ###e guess: it comes from the glpane as a method on it. the glpane is in our env.
            # self.env.glpane.fix_color
        ### fix_color is a method on self, I guess, or maybe on env (and env may either be self.env or an arg to this method -- guess, arg)
        # or maybe it has contribs from env, class, and glpane -- glpane to know what kind of color it needs,
        # env or glpane to know about warps or alphas to apply, class maybe, and something to know about resolving formulas (env?)
        ### we'll have fix_ for the dims too, handling their units, perhaps in a way specific to this class
        ### we'll have memoization code for all these attrs
        ### and we'll need better control of gl state like GL_CULL_FACE, if we can run this while it's already disabled
    pass

class Widget2D(Widget):
    """1. superclass for widget instances with 2D layout boxes (with default layout-box formulas).
    Also an expr-forming helper class, in this role
    (as is any InstanceOrExpr).
    2. can coerce most drawable instances into (1).
    WARNING: I DON'T YET KNOW IF THOSE TWO ROLES ARE COMPATIBLE.
    """
    # default layout-box formulas; for now i think these need _DEFAULT_ so they're overridable by customization, but later they won't
    printnim("Widget2D formulas won't need _DEFAULT_, soon")
    # in fact, they don't now, if they're internal not public re customization -- ####@@@@ [061103]
    if 1:
        _DEFAULT_bright = 0
        _DEFAULT_btop = 0
        _DEFAULT_bleft = 0
        _DEFAULT_bbottom = 0
    else:
        # try just to see if it works - it did seem to work (didn't test customizability either way tho)
        printnim("lbox defaults are not customizable -- wrong??")
        bright = 0
        btop = 0
        bleft = 0
        bbottom = 0    
    pass ### make sure it has .btop. .bbottom, etc -- i.e. a layout box

## DelegatingWidget2D = Widget2D ###STUB, needs DelegatingMixin too
    #####@@@@@ this means, I think, Widget2D with arg1 used for layout... sort of like a "WidgetDecorator"...
    #e should we have a DelegatingMixin instead? yes, making one elsewhere 061109...
    # but we might end up defining DelegatingWidget2D for convenience, if we have a standard name for instantiated args
    # (either in general or in that class)

# this seems to have a logic bug it's not obviously possible to fix... so obs it; use DelegatingMixin directly instead. 061114
##class DelegatingWidget2D(Widget2D, DelegatingMixin): # 061110; test, then generalize
##    "#doc"
##    # devel-scratch comments, 061110:
##    # Provide a standard place to find arg-instances, but without precluding the client from declaring args itself...
##    # hmm, that doesn't seem possible, if client would redeclare the first one.
##    # So at least for now, we either declare them all (lazily, in case client class doesn't want some of them),
##    # or just declare the first one and let the client declare more.
##    # We'll do the latter, since ArgList doesn't work yet ###k.
##    # Bug: Limitations in ExprsMeta or Arg or both mean that the client can't easily declare
##    # more args... making this not very useful yet.###e
##    # (Note that if the client wants its own access to an instance of _e_args[0],
##    #  it would presumably want the same instance of that arg, not another instance of it.)
##    ## delegate = Arg(Widget2D)
##    # ... wait, it's ok to ask for the same instance twice if you use the same index and expr...
##    # so if we just ask for the delegate using a "standard index", it should be compatible with separate arg decls
##    # (which will overlap this use of arg[0]).
##    # The following is what we want, but we'll have to form the exprs manually until we decide on a toplevel way to make the
##    # pure-expr args accessible:
##    ## delegate = Instance( _self._e_args[0], 0 )
##    # needs _self, Instance, getattr_Expr
##    delegate = Instance( getattr_Expr(_self, '_e_args')[0], 0 )
##        #### I SUSPECT THIS IS WRONG and returns a non-instance delegate. This might be causing my weird bugs 061114 430p.
##        # It's only used in Overlay, who is apparently delegating to uninstantiated Translate.
##    pass

# ==

class WidgetExpr_OBS:##(InvalMixin): ###@@@ to become part of Widget2D, obs now, grabbed from testdraw1
        # InvalMixin is for _get_ methods -- replace later with getter/setter properties in each one,
        # or maybe make those from _get_ methods once per class
        # bright is bbox size on right, bleft on left (both positive or zero) #e rename, bright is a word
## ...
    # helper methods (some really belong on other objects)
    def disable_color(self): ### really should be a glpane method
        "don't draw color pixels (but keep drawing depth pixels, if you were)"
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        pass
    def enable_color(self):
        # nested ones would break, due to this in the inner one -- could be fixed by a counter, if we used them in matched pairs
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        pass
    def push_saved_names(self): # truer args would be: both glpane and transient_state object
        for glname in self.saved_glnames:
            glPushName(glname)
    def pop_saved_names(self):
        for glname in self.saved_glnames: # wrong order, but only the total number matters
            glPopName()
    pass
