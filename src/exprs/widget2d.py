'''
widget2d.py

$Id$
'''
###e rename module, to same caps?

from basic import * # autoreload of basic is done before we're imported

import instance_helpers
reload_once(instance_helpers)

from instance_helpers import InstanceOrExpr

# ==

class Widget2D(InstanceOrExpr):
    """1. superclass for widget instances with 2D layout boxes. Also an expr-forming helper class, in this role.
    2. can coerce most drawable instances into (1).
    I DON'T YET KNOW IF THOSE TWO ROLES ARE COMPATIBLE.
    """
    pass ### make sure it has .btop. .bbottom, etc -- i.e. a layout box

DelegatingWidget2D = Widget2D
    #####@@@@@ this means, I think, Widget2D with arg1 used for layout... sort of like a "WidgetDecorator"

# ==

class WidgetExpr:##(InvalMixin): ###@@@ to become part of Widget2D, obs now, grabbed from testdraw1
        # InvalMixin is for _get_ methods -- replace later with getter/setter properties in each one,
        # or maybe make those from _get_ methods once per class
##    bleft = 0
##    bbottom = 0
##    bright = 1 # reasonable default??
##    btop = 1
        # bright is bbox size on right, bleft on left (both positive or zero) #e rename, bright is a word
    def _get_bleft(self):
        return 0
    def _get_bbottom(self):
        return 0
    def _get_bright(self): # default is a _get_ method (formula) so it's overridable by another _get_ method
        return 1 # reasonable default??
    def _get_btop(self):
        return 1
    def __init__(self, *args, **kws):
        self.args = args #####@@@@@ maybe don't do this, but pass them to init, let it do it instead, into self.__args instead
        self.kws = kws
        try:
            self.init()
        except:
            print "info about exception in %r.init method: args = %r, kws = %r" % ( self, args, kws) #e use safe_repr for self
            raise
        return
    def init(self):
        pass
    def _get_width(self):
        return self.bright + self.bleft
    #e _get_height

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
