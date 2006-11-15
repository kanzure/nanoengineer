"""
$Id$

might be renamed or merged

note: transforms.py was split out of here, 061115
"""

from basic import *
from basic import _self

import transforms
reload_once(transforms)
from transforms import Translate

class Center(InstanceMacro): # probably not currently used; not sure if it was ever tested, but looks correct AFAIK [as of 061115]
    "Center(thing) draws as thing (a Widget2D [#e should make work for 3D too]), but is centered on the origin"
    # args
    thing = Arg(Widget2D)
    # internal formulas - decide how much to translate thing
    dx = (thing.bright - thing.bleft)/2.0
    dy = (thing.btop - thing.bbottom)/2.0
    # value
    ###k for now, use V_expr instead of V when it has expr args... not sure we can get around this (maybe redef of V will be ok??)
    _value = Translate(thing, -V_expr(dx,dy,0)) # this translates both thing and its layout box ###k might not work with V(expr...)
    pass

# status of Center, 061111:
# - untested
# - bbox motion in translate is nim, might matter later, not much for trivial tests tho [but it works now anyway, 061115]

# end
