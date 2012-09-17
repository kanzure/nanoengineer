# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
rules.py

$Id$

This is really a scratch/notes file, though it has some code near the end that might become real.
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


# ... what about some example rules?

# can an expr that needs one arg of a certain type, count as a rule?
# calling it means applying it... as expr or instance, maybe doesn't matter(??)...
# if the types don't match, it might raise an exception -- why not?
# so that might actually work.

Vertex # a type of model obj

class VertexViewer(...):
    vertex = Arg(Vertex) # requires arg to be a Vertex object... hmm, do we say it has to be an Instance of one, already??
        # that means it has a pos, rel to whatever obj the vertex type is rel to... but how do we capture that idea
        # that Vertex is really a parametrized type? well, put that off for now since it's not one in demo_drag.py (safe??)

    delegate = Translate( Rect(0.2, color = vertex.color), vertex.pos ) # or so
    pass

# my worries about the above include:
# - is the exception for argtype being wrong really the same (or a subclass) of the one for RuleFailedException?
#   in particular, is it "not an error" (unless it was your last rule in a series)?
# - is RuleFailedException a dangerous concept, since if it gets out of the inside of a rule (eg while running its body),
#   it might seem to apply to the rule itself?
# - how do we capture the idea that Vertex is really a parametrized type?
#   do we cheat and say "a vertex also has a host object"? (which determines the type of pos it has, including its coord sys)
#   actually that might be a good idea (ie not cheating) -- since we can select vertices of different hosts at one time!
#   So letting host (and pos type) just be another attr of each vertex (with optims someday when they're constant) does make sense.

# let's make another example rule where we explicitly list the argtype, avoiding some of the worries above.

Rule(Vertex, VertexViewer) # arg1 is a type, arg2 is a func from arg1 (of that type) to the result (error if it fails)

# worries about *that*:
# - does it use up the word Rule for a special case of argstyle which might not even be the most common one?
# - it seems to *prove* that either:
#   - argtype failure in VertexViewer should not raise RuleFailedException, or,
#   - if it does, Rule should not pass it on unchanged. (which is not hard, i guess, just slightly non-POLS.)

# Here is more evidence that argtype mismatch is not RuleFailedException -- it can happen arbitrary deep inside something,
# and percolate up w/o being transformed.
#
# One way out is to wrap VertexViewer with something to turn it into a rule, which turns argtype mismatch into RuleFailedException --
# but this is only ok if it can verify that the arg whose type did not match was an arg of its direct argument VertexViewer.
# But it could check that (if we defined the data of the argtype exception to include the object whose arg had the wrong type,
#  and if we ignore the possibility of cheating when constructing one to raise)... so we could define such a wrapper --
# and that wrapper could even be autoapplied to turn an expr needing one arg into a rule, in argslots needing a rule.

# ===

# Actually I think returning None is better than raising an exception, for a rule about what things should look like.
# Then you serially combine rules with Or, and exceptions are errors, so catching them is less often needed.
# But can None be the "no answer result" for *all* rules (regardless of purpose)? Surely not. So we need a special object,
# which will be boolean false, so in cases where all correct answers are true, we can still use "or" to combine them.
# But then the general rule utilities can't use "or". So another possibility is that they return None or a true thing,
# and the true thing contains the answer, but is not only the answer. E.g. they return (ok, res) or (bindings, res) or wrapped(res).
# On failure do they return (False, None) or just None or a weird object that acts like both? Failure is common -- just None.

class rules_in_series(RuleOp):
    #e doc; all correct rule results must be true; the convention for encoding arbitrary objects is up to the rule-user;
    # in the present app we're using them to encode exprs or exprheads or Instances, no all legit values are true
    def apply(self, thing):
        r1, r2 = self.args
        return r1(thing) or r2(thing)
    pass

# that's simpler!

# (maybe "in parallel" is more accurate -- no obj goes thru more than one of the rules. Just call it a "rule list" for now.)

# (it has some relation to or_Expr, but it can't be the same thing unless our instantiation env can supply the "thing"...
#  i.e. be different than usual in semantics. Save that idea for later.)

# when the time comes for optim for lots of rules, rules can have methods to add themselves to classifier trees
# which have questions and answer-keyed dicts as nodes.

# what we need for use_VertexView is just a simple way to say "in this env, if obj.type is X, then view obj using Y".
# And we want to use things like that to construct mappings for other purposes too.
#
# So we want a Rule object API (for rules and rulesets), ops like rule lists, a way to make a Mapping from a Rule,
# and a standard mapping in the env for model_object_viewers, and a standard way to locally incrementally pre-extend its rulelist.

WithRule(expr, rule) # this is fine if there is only one ruleset we need to extend, and if "in the dynenv" can be implicit.

WithEnv(expr, rule) # no, sounds like it's the whole env.

WithEnvRule(expr, rule) # explicit env, still assumes one ruleset in env. The rule would have to apply to all exprs for all purposes...

WithViewRule(expr, rule) # says the rule is for how to view something... implies it's in dynenv, since all viewing rules are.

LocalEnv(expr, view_rule = rule) # ....

  # I think I don't want to force this mod into a general form for other kinds of mods, now -- the relation to the general form
  # might change, and the namespace of different kinds doesn't have enough names in it to pick good names for specific ones.

UseViewRule # I guess I like With better than Use -- so far all forms of "with" mean "with local mods, not destructive to parent".

WithViewRule( expr, (Vertex, VertexView)) # 2-tuple (type, func) can be interpreted as Rule if you try... seems good.
    # But if we adopt that, and also for lists of rules, we better decide whether it has to be done to every value at runtime,
    # when the arg is a formula. It also makes the code harder to read, perhaps...

WithViewRule( expr, Rule(Vertex, VertexView)) # use this form

    # this form of Rule(type, func) can be general if we say that type can be fancy, as long as it returns False or (True, *args)
    # with *args passed as extra args to func! Not sure if that way of fancification makes sense... ok for now,
    # since there'll be few enough of these (for some time from now) that changing them all in name or syntax would be ok.

    # BTW can a func, or an exprhead needing one arg, be interchangeable here? I hope so and guess so, but don't know for sure,
    # and I doubt it's already implemented. It might require instantiating such an expr without its arg, getting a func
    # that wants an arg instance! But then I'd worry about whether erroneous uses of that feature could be detected.
    # Maybe they could by attr access too early... or maybe the argslot would have to specifically permit this kind of instantiation.

class Rule(FunctionExpr): # FunctionExpr means it instantiates into a function, and has the __call__ interface to self.apply
        #e or we might decide that any sort of expr can define apply, with that meaning on its instances
        # (if so should we rename apply to _e_apply or _i_apply or so? probably _i_apply.)
    """Rule(type, func) is an Expr for a rule which matches any Instance which has the given type, and wraps it with func.
    Once instantiated, it can be applied to an Instance (thing) by being called on it (Python __call__),
    returning None if it doesn't match, or func(thing) if it does. (That result is presumed to be an Instance,
    and is required to be true, though perhaps neither condition is checked.)
       Note that it is meant for use on Instances, and is hard to use on arbitrary Python values if any legal values can be false.
    """
    type = Arg(Type)
    func = Arg(Function)
    def apply(self, thing):
        "return None if it doesn't match, or func(thing) if it does"
        type = self.type
        func = self.func
        ## if type.matches(thing): ####k??? this assumes canon_type or other coercion to Type tames type and gives it this method
        if isa(type)(thing): # this (isa(), vs. x.matches()) is easier to support since it can work for python types too
            res = func(thing)
            assert res, "%r requires %r(%r) == %r to not be false" % (self, func, thing, res)
            return res
        return None
    pass

class RuleList(...):
    args = ArgList(Rule) # assumes Rule is also usable as a type -- though above Rule class has no provision for that
        ###IMPLEM ArgList -- it makes args a list of instances, doing instantiation and type coercion on each one (lazy per elt??)
        # (note: this semantics is precisely the same as a few other files desiring ArgList, so it must be an ok design!)
        ###e do we want it to let args also be python lists of rules (or list_Exprs thast make them)? probably yes -- someday.
        # (just as in Column) (all it needs is a more flexible typecheck and a system like in Column to map the args...)
    def apply(self, thing):
        for rule in self.args:
            res = rule(thing)
            if res:
                return res
            assert res is None, "Rule %r applied to %r was %r -- should be None or something true" % (rule, thing, res)
            #e maybe weaken that to a warning, so we can treat it as None and continue? also file it centrally as a RuleOp method
            # (assuming this can be a subclass of RuleOp (#e rename?), which I guess is itself a subclass of FunctionExpr)
            continue
        return None
    pass

class WithViewRule( ...) # it's not a good sign that i keep deferring the superclass -- it probably means InstanceOrExpr spelling is too long
    """#doc; example:
    WithViewRule( expr, Rule(Vertex, VertexView))
    """
    #e modify env locally... turn into a special form of WithEnvMods. See other file for stub of that.
    pass

# ... the above needs ArgList, and might need working type coercion too.
# let's implement some iterators (like rect with corners) first, and both of those internal features.
# Just make another macro like Arg, make it get told its starting pos like Arg does,
# and let the type coercion in those macros *not* work by using type in direct call (like it may do now, not sure).
# [070112 morn]

# ==

# older stuff than the above, moved here from demo_drag.py 070123, and then with a new docstring

class WithViewerFunc(DelegatingInstanceOrExpr):#070105 stub experiment for use with use_VertexView option ### NOT YET USED non-stubbily
    """[docstring added much later, 070123 -- not sure it matches original intent, but who cares, the code was a stub]
    WithViewerFunc(world, viewerfunc) means show world using viewerfunc,
    which converts some kinds of objects into new ones which are more directly viewable (usually by wrapping them with glue code).
       (#k Is it an incremental addition in front of (and in series with, ie able to delegate to)
     the existing env.viewerfunc? I think so.)
       Note that viewerfunc is an example of a Rule or RuleSet or RuleOp (see rules.py) and is often a "memoizing mapping".
    (More precisely, a Rule expr is typically instantiated into a memoizing mapping which uses it, by code in its highest abstract
    superclass, perhaps RuleOp or MemoizingMapping.)
       Conventions about a viewerfunc:
    - When applied to a collection, it typically does nothing (as with any object it doesn't recognize),
    but the default collection-viewer will usually use the full env's viewerfunc to view its elements,
    so viewerfunc will end up getting applied to the collection's elements.
    - When applied to things it doesn't recognize, it leaves them alone. (So it is *not* the kind of rule that returns None then. Hmm.)
    - When it does recognize something, it should turn it into something more viewable, but perhaps still high-level
    ie requiring other viewerfuncs to view it.
    - Typically it turns some model objs into graphical objs, and leaves graphical objs alone,
    but the same scheme might be used to turn HL graphicals into LL ones, applying styles and prefs.
    """
    world = Arg(Anything)
    viewerfunc = Arg(Anything) ### NOT YET USED in this stub
    delegate = _self.world # stub
    #e what we actually want is to supply a different env to delegate == arg1, which contains a change from parent env,
    # which depends on viewerfunc. We want a standard way to ask env for viewers, and the change should override that way.
    # But we don't yet have a good way to tell this macro to override env for some arg.
    # We probably have some way to do that by overriding some method to find the env to use for an arg...
    # but we didn't, so i made one.
    def env_for_arg(self, index): # 070105 experiment -- for now, it only exists so we can override it in some subclasses
        env = self.env_for_args #e or could use super of this method [better #e]
        if index == 0: #KLUGE that we know index for that arg (world, delegate, arg1)
            env = env.with_lexmods({}) #### something to use viewerfunc
        return env
    pass

# let's try a more primitive, more general version:

class WithEnvMods(DelegatingInstanceOrExpr):#070105 stub experiment -- refile into instance_helpers.py if accepted ### NOT YET USED
    """WithEnvMods(something, var1 = val1, var2 = val2) delegates to something, but with something instantiated
    in a modified dynamic environment compared to self, in which env.var1 is defined by the formula val1, etc,
    with the formulae interpreted as usual in the lexical environment of self (e.g. they can directly contain
    Symbol objects which have bindings in env, or they can reference any symbol binding in env using _env.symbolname ###IMPLEM
    or maybe other notations not yet defined such as _the(classname) ###MAYBE IMPLEM).
    """
    # The goal is to just say things like WithEnvMods(model, viewer_for_object = bla)
    # in order to change env.viewer_for_object, with bla able to refer to the old one by _env.viewer_for_object, I guess.
    # This assumes env.viewer_for_object is by convention a function used by ModelObjects to get their views. (Why "viewer" not "view"?)
    delegate = Arg(Anything)
    var1 = Option(Anything) ###WRONG, but shows the idea for now...
    def env_for_arg(self, index):
        env = self.env # note: not self.env_for_args, since we'd rather not lexically bind _my.
            # But by convention that means we need a new lowercase name... ####e
        if index == 0: #KLUGE that we know index for that arg (delegate, arg1)
            mods = {} ###stub, WRONG
                #### how do we make these mods? _e_kws tells which, but what env/ipath for the formulae?
                # for that matter do we eval them all now, or (somehow) wait and see if env clients use them?
                # ... would it be easier if this was an OpExpr rather than an InstanceOrExpr?
            env = env.with_lexmods(mods)
        return env
    pass

# == trivial prototype of central cache of viewers for objects -- copied/modified from demo_MT.py, 070105, not yet used, stub

def _make_viewer_for_object(obj, essential_data):
    ###stub
    assert obj.__class__.__name__.endswith("Vertex")
    return VertexView(obj)

    # semiobs cmt (del or refile a bit below #e):
    # args are (object, essential-data) where data diffs should prevent sharing of an existing viewer
    # (this scheme means we'd find an existing but not now drawn viewer... but we only have one place to draw one at a time,
    #  so that won't come up as a problem for now.)
    # (this is reminiscent of the Qt3MT node -> TreeItem map...
    #  will it have similar problems? I doubt it, except a memory leak at first, solvable someday by a weak-key node,
    #  and a two-level dict, key1 = weak node, key2 = essentialdata.)

def _make_viewer_for_object_using_key(key):
    """[private, for use in a MemoDict or LvalDict2]
    #doc
    key is whatever should determine how to make the viewer and be used as the key for the dict of cached viewers
    so it includes whatever matters in picking which obj to make/cache/return
    but *not* things that determine current viewer
    but in which changes should invalidate and replace cached viewers.
    """
    obj, essential_data, reload_counter = key ###k assume key has this form
    print "make viewer for obj %r, reload_counter = %r" % (obj, reload_counter) ###
    # obj is any model object
    viewer = _make_viewer_for_object(obj)
    return viewer

_viewer_lvaldict = LvalDict2( _make_viewer_for_object_using_key )

def _viewer_for_object(obj, essential_data = None): #####@@@@@ CALL ME
    "Find or make a viewer for the given model object. Essential data is hashable data which should alter which viewer to find. ###k??"
    from exprs.reload import exprs_globals
    reload_counter = exprs_globals.reload_counter # this is so we clear this cache on reload (even if this module is not reloaded)
    # assume essential_data is already hashable (eg not dict but sorted items of one)
    key = (obj, essential_data, reload_counter)
    lval = _viewer_lvaldict[ key ]
    viewer = lval.get_value() ###k?
    return viewer



# end
