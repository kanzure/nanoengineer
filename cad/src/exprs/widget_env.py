# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
widget_env.py -- an environment for the instantiation and use of widget exprs

@author: bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.


The environment is used for lexical replacement & instantiation,
and then for "use/residence" (running & drawing & holding state).
Maybe someday we'll split these parts. The ipath is already passed separately
for efficiency. [#doc -- this comment is not clear enough.]

070106 discussion of lexical/dynamic confusion: the env is mainly dynamic,
but also holds lexical bindings. At present, it holds both kinds as attributes
(distinguishing them only by convention), and also has class attrs and an instance
variable (delegate and whatever else Delegator has), with no means of distinguishing
them from variable bindings (which would lead to bugs if symbolnames overlapped class attrs --
so far that can't happen, since nothing creates arbitrary symbolnames and the fixed ones
don't overlap them). Finally, the implementation of lexical vs dynamic inheritance is
incorrect, since lexenv_Expr should grab only lexical vars from its contained env, but grabs
all vars from it -- this too has not yet led to bugs, since there is no provision for overriding
dynamic variables, so each one is the same in both envs seen by lexenv_Expr.

But all the confusions mentioned above will soon turn into real bugs, since we'll introduce
ways to declare and override both lexical and dynamic symbols of non-hardcoded names.
So we have to clean up the situation somehow. First, a survey of existing symbolnames in use:

Lexical:

_self
    [note: the _e_eval* methods on Expr act as operations on implicit instances of the Expr self
     owned by the real instance env._self; AFAIK this is an orthogonal issue to _self being lexical in formulae]
_this_<classname>
_my

Dynamic:

glpane
staterefs (rarely used directly)

And proposed names:

_the_<classname> (dynamic)
_env (unclear -- the intent is for _env.sym to be used in formulas to refer to dynamic sym,
      but it's probably short for _my.env.sym, thus _env is itself lexical.)

With the exception of the proposed dynamic variable _the_<classname>,
note that the lexical names start with one '_'
and the dynamic ones start with no '_'.

Of these, the only ones often accessed as env attrs by client code are _self and glpane.
If we changed how all env vars should be accessed, only those would lead to large numbers
of client code changes.Nothing is wrong with a fixed set of vars being accessible as env attrs,
so we might let those continue to be accessed that way even if general vars can't be.

We also may want formulas to access env vars of some object using <object>.env.<var>,
which is a harder issue since the vars could be arbitrary. I don't yet know if we want to
enforce a naming convention about which vars are dynamic vs lexical, and/or a fancier required
syntax for accessing non-hardcoded env var names.

The likely uses for dynamic variables are to refer to important GUI framework objects surrounding
specific drawables, including singleton model objects like the model or the current selection,
to display styles, to "the model object" being shown in drawables serving as its view, and probably
various containing or otherwise-related model objects of given types, and to the presence of
specific user-defined "tags" on those objects.

The likely uses for lexical variables are in user-defined rules, and the hardcoded _self, _this_X, _my.
"""

#e rename module?? possible names: expr_env, instance_env, widget_env, drawing_env -- or something plural?

from idlelib.Delegator import Delegator ###e we should use our own delegation code, since we don't need the key cache so it can be more efficient

from exprs.Exprs import canon_expr
from exprs.py_utils import printnim
##from exprs.py_utils import printfyi

class widget_env(Delegator):
    "represent an environment for the instantiation and use of widget exprs (with rules and staterefs)"
    # I intend to add this soon here (default value): _self = None
    printnim("SOON I need to add _self = None to class widget_env")#####@@@@@
    def __init__(self, glpane, staterefs, delegate = None, lexmods = {}):
        #e rename glpane?
        #e type of staterefs? [just an external dict, as of 061116 calling code; the 'refs' in the name is to remind you it's not owned]
        #e rules/lexenv too?
        #e ipath? [061116: no, that's separate, tho if we end up splitting it by state-layer,
        #    we might have to change that, or let env have ipaths per layer with the separately-passed one relative to all those ]
        self.glpane = glpane
        self.staterefs = staterefs ###k
        ###KLUGES, explained below [061028]:
        Delegator.__init__(self, delegate) # this will be None or the parent env
        for k,v in lexmods.iteritems():
            setattr(self, k,v) # worst part of the kluge -- dangerous if symnames overlap method names
            # next worst part: special methods like __repr__ end up delegating
        pass
    def __repr__(self): # without this, Delegator delegates __repr__ ultimately to None, so "%r" % self == "None"!!!
        return "<widget_env at %#x (_self = %r)>" % (id(self), getattr(self, '_self', '<none>')) # revised 070120
    __str__ = __repr__ #k guess: might be needed for same reason as __repr__
    def understand_expr(self, expr, lexmods = None):
        print "understand_expr ran"###070112 -- never happens
        "#doc; retval contains env + lexmods, and can be trusted to understand itself."
        # only the "rules" in self are needed for this, not the glpane & staterefs! so put this method in a subobject! #e
        assert not lexmods, "lexmods are nim" ###@@@
        return expr ####@@@@ STUB but might sometimes work
            #e [if we ever need this, can we just use something like lexenv_Expr?? but with dynenv bindings too? 070112 guess comment]
    def make(self, expr, ipath, eval = True): #k args?? ####@@@@
        """Make and return an instance of the given expr (understood or not) in self.
        The instance should store its state under the index-path ipath [#doc format].
        """
        # print "make ran (eval = %r)" % eval # happens before you make a new main instance... 070121 or when demo_drag makes a node
        #e ipath guess: a list of 2 or 3 elts, linked list inner first, maybe append an interning of it
        #e look for rules; check if understood;
        #e Q: is this memoized? does it allocate anything like a state obj ref, or was that already done by customizing this env?
        ## print "making",expr,ipath
        # assume it's an understood expr at this point
        #
        # update 070117 re EVAL_REFORM: maybe we'll need to be an explicit noop for numbers or Instances (non-pure-exprs) --
        # we will if some calls to _e_make_in are changed into calls to this, which seems likely. #k
        # The way to do that is to do what _i_instance does -- it calls some helper function to decide what's idempotent for make.
        if eval:
            # new feature 070118 -- fixes testexpr_19f when no testbed and when not EVAL_REFORM
            # (guess, unconfirmed: its failure then is an old bug predating EVAL_REFORM, not a new bug)
            eval_ipath = ('!env-eval', ipath) # I'm guessing this had better differ from the one passed to _e_make_in -- not sure
            expr = expr._e_eval(self, eval_ipath)
            #e it'd be nice to print a notice if this changed it, but it surely will by wrapping a new lexenv_Expr if nothing else,
            # so it's too hard to tell if it *really* did.
        try:
            res = expr._e_make_in(self, ipath)
        except:#070118
            print "following exception in env.make's _e_make_in call concerns expr %r and ipath %r: " % (expr, ipath)
            raise
        return res
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
        return self.lexval_of_symbolname(name, sym)
    def lexval_of_symbolname(self, name, dflt):
        #e default for dflt? used to be the sym, even now could be an imported (so identical) sym
# removed printfyi warning, 070131:
##        if name not in ('_self','_app') and not name.startswith('_this_'):
##            printfyi("lexval_of_symbolname other than _self, _app, or _this_xxx: %s" % (name,) )
        # kluge:
        return getattr(self, name, dflt)
    ## newenv = dynenv.dynenv_with_lexenv(lexenv) #e might be renamed; might be turned into a helper function rather than a method
    def dynenv_with_lexenv(self, lexenv):
        "#doc"
        return lexenv ##### 070109 is _app bug fixed even w/ this? yes, it was unrelated. WE STILL NEED NEW CODE HERE. ####BUG
        # kluge 070109: do just enough to see if using this fixes the bug i suspect it might -- ###WRONG IN GENERAL (and disabled too)
        if getattr(self, '_app', None) is not getattr(lexenv, '_app', None):
            print "fyi: dynenv_with_lexenv makes a difference for _app: %r vs %r" % \
                  ( getattr(self, '_app', None) , getattr(lexenv, '_app', None) ) ### remove when works
        if not hasattr(self, '_app'):
            return lexenv
        return lexenv.with_literal_lexmods(_app = self._app) # really this is a "dynamic mod" as hardcoded in the name _app (w/in current kluge)
    def _e_eval(self, expr, ipath):#070131
        "evaluate an expr (or constant) in this env, with given ipath"
        return canon_expr(expr)._e_eval( self, ipath)
    pass

def thisname_of_class(clas):
    thisname = "_this_%s" % clas.__name__ ##e [comment also in our caller:] someday make it safe for duplicate-named classes
            # (Direct use of Symbol('_this_Xxx') will work now, but is pretty useless since those symbols need to be created/imported.
            #  The preferred way to do the same is _this(class), which for now [061114] evals to the same thing that symbol would,
            #  namely, to what we store here in lexmods for thisname. See "class _this".)
    return thisname

# == end, except for obs code and maybe-not-obs comments

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
