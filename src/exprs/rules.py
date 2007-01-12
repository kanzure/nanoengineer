"""
rules.py

$Id$
"""

# Coming out of this comment just added to demo_drag.py:

    # Summary of this and Vertex_new -- make use_VertexView work --
    # [long comment added 070111; devel on this code has been inactive for a few days]
    #
    # it's an example of dynamically mapping selobj thru toolstate to get looks & behavior,
    # so the model object itself can be split out and needs no graphics/interaction code of its own.
    # My general sense in hindsight is that it's too low-level -- I need to figure out how all this could/should look as toplevel exprs.
    #
    # See a new file rules.py for more on that.

# Basic idea is that we're modifying the env by incrementally adding a rule for how to view some objs.
# The rule knows what objs it handles and delegates the rest. It has to be applied in a localmost way --
# effectively it filters the entire env. We can implem it that way now and optim it later -- but the syntax should
# be how we think of it, which is "a rule that says what it applies to (at least roughly, ie with a typename)".
# The typename might as well be the Python class, even if we compare classname so as to not worry about reload.
#
# In general the env has a big mapping from model objs to their views... which is added to by many sources.
# But how is that mapping *used*, and what are semantics of an object which can be used to add to it?
# The obj is an expr, the outer layers can be a typefilter,
# that can be used two ways (dict key for optim, or predicate for test each time),
# so it's sort of logical or mathematical... it's a pattern operator; another one is a general condition (evals a pred formula).
# Another one not only evals, but makes some localvar bindings, probably in the form of an object with attrs (formulas) or a dict.
#
# So the outermost operation here is "modify env.whatever by preadding this rule to it";
# rule semantics are "match: succeed with data or fail", and for optim, maybe "match to some kinds of parts inside this thing",
# "get compiled in this way", etc.
#
# What we modify in env is "how to view model objs". is that just "how to view things?" The model obj type might be enough...
# we can ignore issues raised by "how to view graphical objs" for now.
#
# So the env has some general viewer mapping which gets applied to everything before we draw/lbox it... as memoized glue code...
# and which knows how to extract a suitable memo index (dict key) from the obj it looks at, guess maybe based on what the patterns
# in the rules ask about. Trivial version - rule asks about outer type, so mapping extracts that to classify,
# but rule rhs then applies to entire obj, so mapping extracts id of obj (really ipath, i guess) as index,
# whereas if rhs only cared about obj.attr1,
# maybe mapping would only extract ipath of obj.attr1 (not sure; optim, so can ignore at first).
#
# So we also (finally) need these mapping objects, which extract their own indexkeys, as if obj itself was the *given* index.
# And the mapping object is just called with a method with the passed input obj as arg -- or applied to it as if it's a func or dict.
# I guess __call__ is most flexible (eg it works with python map operation, with compose, etc).
# This fits with env.viewer_for_object as a func which takes obj to its view (or a default view for an unknown obj, if nec).
# I was thinking "it's identity for all but model objs", but really, it uses default glue for all but viewable objs!
# Then for *those*, it's id for non-model objs. So objs to it are unknown (default glue), or viewable, further divided
# into graphical (identity unless we're using weird rules not needed for now), or model (look up view in the rules).
# But as said, the rules can tell what's what, so it's all equiv to: try the model->view rules, else notice it's already viewable,
# else use default glue for foreign objs (which need a minimal interface like asking for their py class and py id, and/or repr).
#
# what about 3d vs MT view? these are just a very high classification of a display style, which also has lower classifications... right?
# but they can just as well be a difference in the rules themselves in different local envs... otoh we'd always like access to either one
# by name. hmm.
#
# Back to "the env has some general viewer mapping" -- given the old and new one of those, with what op do we combine them?
# just a "compose rules in series" op. But what's the __call__ interface -- how does it say "i don't apply" vs "i'm identity"?
# Maybe with an exception when it fails? Note the similarity to ParseRules, and indeed, they're very related.
# (They might get even more related if we use this to bind actions to event streams, and need different rules
#  to bind to different portions of it and leave the rest for more.)

def rules_in_series(r1, r2):
    # revise to a class, since otherwise it'll need that x=x in def arglist kluge, and return res; anyway it's really an expr
    def res(thing, r1=r1, r2=r2):
        try:
            return r1(thing)
        except RuleFailedException: # note this 
            return r2(thing)
        pass
    return res

class RuleOp(...):
    #e __init__ from Expr or similar superclass I guess
    #e something to set .args? or is a rule one of those pure exprs which is already enough of an instance?
    # sometimes no -- the instance can memoize!
    def __call__(self, arg, *args, **kws):
        #e do something uniform about more args & kws. so now there is only one arg
        res = self.apply(arg)
            #e might raise RuleFailedException (or other ones on errors)
        return res
    pass
class rules_in_series(RuleOp):
    #e doc; this form has only one more line, which is not a problem compared to its benefits
    def apply(self, thing):
        r1, r2 = self.args
        try:
            return r1(thing)
        except RuleFailedException:
            return r2(thing)
        pass
    pass

# Now a mapping is a just a big kind of rule-like thing... but it has all that index-finding and memoizing intelligence,
# all the stuff that old GlueCodeMemoizer had... don't code it until I decide how it should work.
# Note a lot of them will be modified views of a big main one in the env.
# Note someday it'll do compiling and other fancy stuff too... and something else I just forgot I wanted to say... oh yeah, weak index-part handling
# maybe type coercion too... and easy formation of incrly modified versions...
# 
