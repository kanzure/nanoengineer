"""
iterator_exprs.py

$Id$
"""

from basic import *
from basic import _app, _self, _my

class MapListToExpr(DelegatingInstanceOrExpr): #e when this works, rewrite _MT_try2_kids_helper in terms of it! It uses the same algorithm. #e also refile
    # args (#e should some be ArgOrOption? Note: that doesn't work right if it comes before Arg.)
    ###KLUGE: use ArgExpr to avoid problems when passing expr classes as functions -- not sure if generally ok (eg when ordinary callable is passed)#####
    function = ArgExpr(Function, doc = "a python function which maps whatever you pass as elements to Instances")
    elements = Arg(list_Expr, doc = "a list of elements (of whatever data type you want, suitable for passing to _my.function)")
    exprhead = ArgExpr(Function, doc = """a python function which can be applied to a sequence of Instances
                    to produce an Expr we should instantiate as our _delegate, whenever our input list of elements changes.
                    Typical values include expr classes like SimpleColumn, or customized ones like SimpleRow(pixelgap = 2)."""
                )
    instance_function = Option(Function, _self.Instance,
                               doc = "a python function with the API of some IorE object's .Instance method, to produce the Instances we delegate to" )
        # I wanted to name this Instance, but I think that would cause infrecur when it used the default.
        # note: we pass it permit_expr_to_vary = True, which complicates the required API. But without this we could not pass someobj.Instance.
        # Maybe IorE needs a variant method of Instance with permit_expr_to_vary = True by default? VaryingInstance?
    # self._delegate recompute rule
    def _C__delegate(self):
        function = self.function
        elements = self.elements # usage tracked (that's important)
        exprhead = self.exprhead
        index = '_C__delegate'
        # compute the expr we need (see comment above for why we need a new one each time)
##        assert type(list(elements)) == type([])
##            # note: this does not assert type(elements) == type([]), only that list(elements) works and makes a list
##            # (i.e. it's redundant with error checking in the map call below)
        elts = map( function, elements)
        for elt in elts:
            assert is_expr_Instance(elt)
        expr = exprhead(*elts)
        # do we need to eval expr first? in theory i forget, but I think we do.
        # in practice it's very likely to eval to itself, so it doesn't matter for now. ###k
        ##e do we need to discard usage tracking during the following??
        res = self.instance_function( expr, index, permit_expr_to_vary = True)
        return res
    pass # end of class MapListToExpr

def KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr( exprclass ):
    return constant_Expr( exprclass( _KLUGE_fake_option = 1))
        # comment from when we tried everything simpler than this to pass SimpleColumn to MapListToExpr as its exprhead arg:
        # this kluge was not enough: passing constant_Expr(SimpleColumn) (several errors)
        # or was using ArgExpr in MapListToExpr
        # nor was this, by itself: exprclass( _KLUGE_fake_option = 1)
        # but using all three together, it works.
        # The things this klugetower avoids include:
        # - without ArgExpr we'd try to instantiate the function, ok for ordinary one but not for expr class let alone customized expr
        # - ArgExpr's grabarg wrapping the exprhead-as-function with a lexenv_ipath_Expr, which has no __call__:
        #   AssertionError: subclass 'lexenv_ipath_Expr' of Expr must implement __call__
        #   (and a trivial __call__ would be incorrect, as explained in demo_ui.py recently [070302]
        #   [thus the constant_Expr]
        # - AssertionError: pure exprs should not be returned from _i_instance: <class 'exprs.Column.SimpleColumn'> ) [thus the cust]

# end
