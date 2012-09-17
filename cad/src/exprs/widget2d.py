# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
widget2d.py

$Id$

"""
###e rename module, to same caps? hmm, maybe just to widget, since it has that class too? or move that class?

from OpenGL.GL import GL_FALSE
from OpenGL.GL import glColorMask
from OpenGL.GL import GL_TRUE
from OpenGL.GL import glPushName
from OpenGL.GL import glPopName

from exprs.instance_helpers import InstanceOrExpr
from exprs.py_utils import printnim
from exprs.__Symbols__ import _self
from exprs.Exprs import V_expr

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
##    width =  bleft   + bright # this would be ok if bleft etc were exprs; since they're constants we have to say _self explicitly
##    height = bbottom + btop
    width =  _self.bleft   + _self.bright
    height = _self.bbottom + _self.btop
    center = V_expr( (_self.bright - _self.bleft) / 2.0, (_self.btop - _self.bbottom) / 2.0, 0.0) # 070227 moved here from Rect
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


# lowercase stub doesn't work for the following, since they get called during import, so use uppercase Stub

# need InstanceOrExpr defined for this one:
Stub = Widget2D # use this for stub InstanceOrExpr subclasses

# end
