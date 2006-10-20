'''
widget_env.py -- an environment for the instantiation and use of widget exprs

$Id$

The environment is used for instantiation and then for "use/residence" (running & drawing & holding state).
Maybe someday we'll split these parts.
'''

#e rename module?? possible names: expr_env, instance_env, widget_env, drawing_env -- or something plural?

class widget_env:
    def __init__(self, glpane, staterefs): #e rename glpane? type of staterefs? rules/lexenv too? ipath??
        self.glpane = glpane
        self.staterefs = staterefs ###k
        pass
    def understand_expr(self, expr, lexmods = None):
        "#doc; retval contains env + lexmods, and can be trusted to understand itself."
        # only the "rules" in self are needed for this, not the glpane & staterefs! so put this method in a subobject! #e
        assert not lexmods, "lexmods are nim" ###@@@
        return expr ####@@@@ STUB but might sometimes work
    pass

# semi end

##
# drawing_env

class drawing_env: ###e cannibalize this above; only used in test.py, obs now
    def __init__(self, glpane):
        #e needs what args? glpane; place to store stuff (assy or part, and transient state); initial state defaults or decls...
        pass
    def make(self, expr, tstateplace):
        #e look for rules
        #e Q: is this memoized? does it allocate anything like a state index, or was that already done by customizing this env?
        print "making",expr#####@@@@@
        return expr.make_in(self, tstateplace) #####@@@@@@ IMPLEM, see class xxx below
    def _e_eval_expr(self, expr):
        ###e look for _e_eval method; test for simple py type
        assert 0, "nim"####@@@@
    def _e_eval_symbol(self, expr):
        assert 0, "nim"####@@@@
    pass

# things in the env:
# - rules for understanding exprs (can be empty even in practice)
#   - they are lexical
#   - contains exprhead macro-replacements
#   - contains lexical replacements while we're expanding rules -- passed separately since changes separately, but might just inherit
# - rules for instantiating
#   - a drawing env to attach the instance to
#     - glpane
#   - a model env in which the state resides, in layers
#     - staterefs
# - rules/state for running/drawing

# use GlueCodeMapper I mean GlueCodeMemoizer to map exprs to understood versions and then (with ipaths) to instances??
# but we already use it for finding kids, in some cases... maybe in all??
# - ipath is explicit so we can use it to make state in other layers, following structure of instances.
#   - so it has not only ints etc, but symbols corresponding to attrs... it should correspond to "find the instance using attr/index" path
#   - so we might want to make sure that always works... in fact we do. how? by a special member for storing kids or their defs...
#     self.kids.attr1[i]
#     we put compute rules in it, but also have a way to find attr/index paths in it...

# end
