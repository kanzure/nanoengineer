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
    ## methods moved into superclass 070201
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
