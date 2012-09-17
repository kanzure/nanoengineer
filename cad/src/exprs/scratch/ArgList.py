# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
ArgList.py

$Id$

scratch file to be merged into attr_decl_macros.py and instance_helpers.py

ABANDONED (tentatively) on 070321 -- replaced by a new def ArgList in attr_decl_macros.py, and support features in ExprsMeta.py.
"""

def ArgList(type_expr):
    "see rules.py for a docstring #doc"
    # Coding strategy: create an expr with just enough in it to let ExprsMeta's formula scanner do replacements
    # that only it can do (for argpos and attr); then let a helper method do most of the work (when self is known,
    # thus when arglist and its len are known, and type_expr can be evaluated); have it return the list of Instances.
    #
    # (#e In future, the helper might return a list-like object which makes Instances lazily, though I'd guess this
    #  rarely matters in practice -- but who knows, what if we use this for the textlines in a text editor?)
    global _arg_order_counter
    _arg_order_counter += 1
    required = True
    argpos_expr = _this_gets_replaced_with_argpos_for_current_attr( _arg_order_counter, required )
        #e pass an option to say we're the last, or error --
        # ie to say the next argpos is -1, or so, or to include an error flag with the counter,
        # and make that detected as an error in the class decls, maybe in the formula scanner
        # or whatever makes _this_gets_replaced_with_argpos_for_current_attr actually get replaced,
        # or the replacement method inside that...
        #e make it notice error of arg with dflt before arg w/o one too, *or* make that work!
        # all this can be done by making it accumulate more info than just the true argpos,
        # for passing from one to the next -- whereever it accums that, presumably in the scanner itself
        # or a mutable passed with it, maybe in the class's namespace as a kluge (see what the code does now)
    global _E_ATTR # fyi
    attr_expr = _E_ATTR
    res = call_Expr( getattr_Expr( self, '_i_arglist_helper'), attr_expr, argpos_expr, type_expr)
        # btw: if this returns list of instances, but for convenience uses _ArgOption_helper which returns expr in _self,
        # then it needs to eval that expr with _self = self.
        # Far more efficient would be to imitate it, just building the type coercion expr per arg, then making it.
    return res


# method of IorE:
def _i_arglist_helper(self, argpos):
    for pos in range(argpos, len(self._e_args)):
        ## arg = Arg(type_expr, expr, options)
        attr_expr = None ###k or use current attrname? yes see below -- assert not None, or if none, change it to argpos, modified
        dflt_expr = _E_REQUIRED_ARG_
        required = True
        argpos_expr = _this_gets_replaced_with_argpos_for_current_attr( _arg_order_counter, required )
        type_expr # pass this
        arg = _ArgOption_helper( attr_expr, argpos_expr, type_expr, dflt_expr)
            ### we want argpos_expr in caller, to use it here
            # we want this to let us separately give argpos for grabarg and index to use
            # or just use this behavior:
                ##if attr_expr is not None and argpos_expr is not None:
                ##    # for ArgOrOption, use a tuple of a string and int (attr and argpos) as the index
                ##    index_expr = tuple_Expr( attr_expr, argpos_expr )
            # or extend that case stmt if we need to
        res.append(arg)
    return [whatever_Arg(expr, index) for pos in range(argpos,








      map_Expr( func, remaining args - from which it uses argpos


                helper func

                runs on the arg exprs and argpos
                calls .Instance a lot
                uses same argpos index as if not in a list? no, uses its own plus the one in the list

      helper can wrap _i_instance


      does it call grabarg in usual way? I guess so





can we generate a bunch of Arg calls w/ special options for index, and return a list of evalexprs of them?
ie a list of instances as our value
