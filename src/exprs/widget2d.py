'''
widget2d.py
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
