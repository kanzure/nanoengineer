'''
widget_env.py -- an environment for the instantiation and use of widget exprs

$Id$

The environment is used for lexical replacement & instantiation,
and then for "use/residence" (running & drawing & holding state).
Maybe someday we'll split these parts.
'''

#e rename module?? possible names: expr_env, instance_env, widget_env, drawing_env -- or something plural?

from idlelib.Delegator import Delegator

from basic import printnim

class widget_env(Delegator):
    "represent an environment for the instantiation and use of widget exprs (with rules and staterefs)"
    # I intend to add this soon here (default value): _self = None
    printnim("SOON I need to add _self = None to class widget_env")#####@@@@@
    def __init__(self, glpane, staterefs, delegate = None, lexmods = {}):
        #e rename glpane? type of staterefs? rules/lexenv too? ipath??
        self.glpane = glpane
        self.staterefs = staterefs ###k
        ###KLUGES, explained below [061028]:
        Delegator.__init__(self, delegate) # this will be None or the parent env
        for k,v in lexmods.iteritems():
            setattr(self, k,v) # worst part of the kluge -- dangerous if symnames overlap method names
            # next worst part: special methods like __repr__ end up delegating
        pass
    def __repr__(self): # without this, Delegator delegates __repr__ ultimately to None, so "%r" % self == "None"!!!
        return "<widget_env at %#x>" % id(self)
    __str__ = __repr__ #k guess: might be needed for same reason as __repr__
    def understand_expr(self, expr, lexmods = None):
        "#doc; retval contains env + lexmods, and can be trusted to understand itself."
        # only the "rules" in self are needed for this, not the glpane & staterefs! so put this method in a subobject! #e
        assert not lexmods, "lexmods are nim" ###@@@
        return expr ####@@@@ STUB but might sometimes work
    def make(self, expr, ipath): #k args?? ####@@@@
        """Make and return an instance of the given expr (understood or not) in self.
        The instance should store its state under the index-path ipath [#doc format].
        """
        #e ipath guess: a list of 2 or 3 elts, linked list inner first, maybe append an interning of it
        #e look for rules; check if understood;
        #e Q: is this memoized? does it allocate anything like a state obj ref, or was that already done by customizing this env?
        ## print "making",expr,ipath
        # assume it's an understood expr at this point
        return expr._e_make_in(self, ipath)
    def with_literal_lexmods(self, **lexmods):
        "Return a new rule-env inheriting from this one, different in the lexmods expressed as keyword arguments"
        return self.with_lexmods(lexmods)
    def with_lexmods(self, lexmods):
        "Return a new rule-env inheriting from this one, different in the given lexmods (a dict from symbolnames to values)"
        ###e need to know if env vars are accessed by attr, key, or private access function only, like lexval_of_symbol;
        # and whether glpane is a lexvar like the rest (and if so, its toplevel symbol name);
        # and about staterefs.
        # For now, to make tests work, it's enough if there's some way to grab syms with inheritance...
        # use Delegator? it caches, that's undesirable, and it uses attr not key, which seems wrong... otoh it's easy to try.
        # So I'll try it temporarily, but not depend on attr access to syms externally. [061028]
        return self.__class__(self.glpane, self.staterefs, delegate = self, lexmods = lexmods)
    def lexval_of_symbol(self, sym):
        # renamed _e_eval_symbol -> lexval_of_symbol
        # but I'm not sure it's really more lexenv than dynenv, at least as seen w/in env... [061028] ####@@@@
        # btw, so far this is probably only used for _self.
        # As of 061114, also for _this_whatever -- no, that uses our helper lexval_of_symbolname. 
        name = sym._e_name
        return self.lexval_of_symbolname(name)
    def lexval_of_symbolname(self, name):
        if name != '_self' and not name.startswith('_this_'):
            printnim("fyi: lexval_of_symbolname other than _self or _this_xxx: %s" % (name,) )
        # kluge:
        return getattr(self, name, sym)
    pass

def thisname_of_class(clas):
    thisname = "_this_%s" % clas.__name__ ##e [comment also in our caller:] someday make it safe for duplicate-named classes
            # (Direct use of Symbol('_this_Xxx') will work now, but is pretty useless since those symbols need to be created/imported.
            #  The preferred way to do the same is _this(class), which for now [061114] evals to the same thing that symbol would,
            #  namely, to what we store here in lexmods for thisname. See "class _this".)
    return thisname

# == end, except for obs code and maybe-not-obs comments

##
# drawing_env

class drawing_env: ###e cannibalize this above; only used in test.py, obs now
    def __init__(self, glpane):
        #e needs what args? glpane; place to store stuff (assy or part, and transient state); initial state defaults or decls...
        pass  
##    def _e_eval_expr(self, expr):
##        ###e look for _e_eval method; test for simple py type
##        assert 0, "nim"####@@@@ maybe obs too [guess 061108]
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
