"""
widget2d.py

$Id$
"""
###e rename module, to same caps? hmm, maybe just to widget, since it has that class too? or move that class?

from basic import * # autoreload of basic is done before we're imported
from basic import _self

# ==

class Widget(InstanceOrExpr):
    # Widget can also be used as a typename -- ok??
    # I guess that just means it can be used to coerce things... see docstring-comment in Widget2D. #####@@@@@
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
    # note: _e_decorate_draw is not defined here, but on InstanceOrExpr,
    # so that a delegating InstanceOrExpr can have a draw method and have it get decorated. [070104]
    def draw(self):
        "#doc"
        print "warning: no draw method in %r" % self
        return
    pass # end of class Widget

# ==

class Widget2D(Widget):
    """1. superclass for widget instances with 2D layout boxes (with default layout-box formulas).
    Also an expr-forming helper class, in this role
    (as is any InstanceOrExpr).
    2. can coerce most drawable instances into (1).
    WARNING: I DON'T YET KNOW IF THOSE TWO ROLES ARE COMPATIBLE.
    """
    # default layout-box formulas
    # bright is bbox size on right, bleft on left (both positive or zero) #e rename, bright is a word
    printnim("lbox defaults are not customizable -- wrong??")
        #k is this still true?? if so, is it wrong? IIRC old cmts suggest a fix... [070121]
    bright = 0
    btop = 0
    bleft = 0
    bbottom = 0
    width =  _self.bleft   + _self.bright
    height = _self.bbottom + _self.btop
##    width =  bleft   + bright
##    height = bbottom + btop
    pass # end of class Widget2D

# ==

class _misc_old_code: # not used now, maybe useful someday
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

# end
