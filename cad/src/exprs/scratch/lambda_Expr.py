# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
lambda_Expr.py

$Id$

scratch so far, coming out of discussion of a better syntax for testexpr_19f,
but it's likely to be made real.
"""


if 0: # excerpt from test.py
    # later 070106: (syntax is a kluge; see also testexpr_26)
    testexpr_19f = eval_Expr( call_Expr( lambda thing:
                                         Overlay( thing,
                                                  DrawInCorner( Boxed(
                                                      eval_Expr( call_Expr( demo_drag_toolcorner_expr_maker, thing.world )) )) ),
                                         testexpr_19b ))
    ###EVAL_REFORM ###BUG: testexpr_19b is not instantiated (when we eval the call_Expr and ask for thing.world) but needs to be.


    # Since this whole syntax was a kluge, I should not worry much about making it or something similar still work,
    # but should instead make a better toplevel syntax for the desired effect, and make *that* work.
    # I guess that's a lambda wrapper which can have the effect of Arg/Instance decls on the lambda args...
    # btw, does that mean Arg & Instance need to be upgraded to be usable directly as Exprs?
    # or do the things they produce work when passed in a list, if we scan them in the same way as ExprsMeta does?

if 0:
    macro = lambda_Expr( [Arg(type, dflt), Instance(expr), Option('name',type,dflt)], lambda arg1, arg2, name = None: blabla )
    testexpr_xxx = macro(argexprs)

    thismacro = lambda_Expr( [Arg(Anything)],
                             lambda thing: # thing will be an Instance when this lambda runs
                                 Overlay( thing,
                                          DrawInCorner( Boxed(
                                              eval_Expr( call_Expr( demo_drag_toolcorner_expr_maker, thing.world )) )) )
                           )
    testexpr_xxx = thismacro(testexpr_19b)

    # if we could, would we want to implement the ability to mix the decls into the lambda, like this:?
    lambda_Expr( lambda thing = Arg(Anything): Overlay( thing, ... thing.world ...) )  (testexpr_19b)
    # guess: yes.
    # (would we want to make that the only allowed syntax? not sure.)
    # (would we want a default typedecl of Arg(Anything) (which gets instantiated)? Probably.)
    # (would the present example also be expressible by inserting testexpr_19b into the lambda arg decl,
    #  either as all of it, or inside Arg?? ####k)
    if 0:
        lambda_Expr( lambda thing = testexpr_19b:                Overlay( thing, ... thing.world ...) )  () # not sure ... ###
        lambda_Expr( lambda thing = Instance(testexpr_19b):      Overlay( thing, ... thing.world ...) )  () # *maybe* ought to work,
            # but can this then ever be a supplied arg to the lambda_Expr() as a whole? guess: no.
        lambda_Expr( lambda thing = Arg(Anything, testexpr_19b): Overlay( thing, ... thing.world ...) )  () # should be made to work.

    # (implem details: file lambda_Expr with Arg; the mixing in of decls can probably be reliably supported,
    #  even if only by extracting arg-defaults from the lambda and then calling it with a full arglist made using those,
    #  so no need to make a "modified lambda".)

    # [Should this influence the naming decision for the Python IorE subclass to replace DelegatingIorE and InstanceMacro?]
