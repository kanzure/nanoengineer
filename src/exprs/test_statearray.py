"""
test_statearray.py

$Id$
"""

from basic import *
from basic import _self

SimpleRow

class _color_toggle(DelegatingInstanceOrExpr):
    pass ##Nim

class test_StateArray(DelegatingInstanceOrExpr):
    indices = range(4)
    colors = StateArray(Color, red)
        #e i want an arg for the index set... maybe even the initial set, or total set, so i can iter over it...
        # NOTE: at least one dictlike class has that feature - review the ones in py_utils, see what _CK_ uses
    # how to turn an index into 
    func = lambda index: colors.lvals[index]
    def _color_toggle_for_index(self, index):#e should we use _CV_ for this?? if not, it must be too hard to use!!!
            #k or is it that it defines a dict rather than a func, but we need a func in MapListToExpr?
        color_stateref = self.colors[index] #####KLUGE: this only works due to a bug in the initial stub implem for StateArray!!!
            # w/o that bug it'll be WRONG. What we need is to ask for an lval for that StateArray at that index!
            # or (less efficient) make one for a general dict. Or have a way to try the first and fall back to the 2nd --
            # which is maybe part of a "state array interface". ###e
        return self.Instance( _color_toggle( color_stateref),
                              ('_color_toggle_for_index', index) ) 
    delegate = MapListToExpr( _self._color_toggle_for_index, ###k _self needed??
                              indices,
                              KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleRow) )
    pass
