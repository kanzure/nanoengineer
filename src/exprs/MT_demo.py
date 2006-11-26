"""
$Id$
"""

#stub nim


from basic import *
from basic import _self

from ToggleShow import * # e.g. If, various other imports we should do explicitly #e

class MT(InstanceMacro):
    # compare to ToggleShow - lots of copied code

    # args
    node = Arg(Node) ### type?

    # state refs
    open
    
    # other formulae
    open_icon   = Overlay(Rect(0.4), TextRect('+',1,1))
    closed_icon = Overlay(Rect(0.4), TextRect('-',1,1))
    openclose_blankness = Rect(0.4) ##e make invisible, same size -- use Spacer [nim] #e rename _spacer
    
    openclose = Highlightable( If( open, open_icon, closed_icon ), on_press = _self.toggle_open )
    
    def toggle_open(self):
        pass###
    
    openclose_place = If( node.openable, openclose, openclose_blankness )
    
    _value = SimpleRow(
        openclose_place,
        SimpleColumn(
            label,
            If_kluge( open,
                      thing,
                      TextRect("<closed>")#####BUG: I wanted None here, but it exposes a logic bug; try Rect(0) later
                      )
        )
    )
    pass
