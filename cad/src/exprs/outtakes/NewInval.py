# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
NewInval.py [to be cannibalized -- as of 061231, obs or mostly obs]

$Id$

061231 moved the displist comments and code from here to DisplayListChunk.py;
what remains here is obs or mostly obs
"""

# ==

# Tue 060919

# env + expr -> understood expr (in that env), an obj with attrs (oresmic?)
# expr + env/place -> placed expr;
#   done by a recompute rule, so it might get invalidated, and it's an attrval which is itself usage tracked
# env is divided up - for us, expr interp rules, state (model, transient, optim, displists), glpane & its state and coords
#   and we might yet have to declare or divide it based on what changes rarely, per drawable instance, or per frame (affects inval code)

# write these funcs so that their api does not preclude them from memoizing, or force them to

# they can be env methods, since env determines how they all work and holds the memos

# subenv for every expr level as i interpret, if necessary, or is it just a sub-place?
# but it might only exist during interp -- it's parallel to, but perhaps more transient than, yet more general than,
# transient-state container-hierarchy

# do that code walkthough for a simple example - simple MT with displists (on paper)

# then sort that code into methods on objects, then classes, then write it down in this style.

# overall - recompute rule in drawing env, from expr to its implem (where to send draw events)
# uses understood expr, which tells flags about whether it uses transient state, class or constructorfunc for creating drawable...

# expr object - return the head, and arglist incl options or that there is none, and lexical class from parser if any

# expr in env - understand it, incl how to make it, then make it (in place) (I guess place != env, env is that part of place
#    which affects understanding of expr, maybe not including the part that has changing vars at runtime, or even changing opt vals)
#    (but the understanding might say "opt X has type T" and then that might be what decided the val was in the other place,
#     for env opt vals? not sure.)

# ==

class _Lval: ####@@@@ compare to later version in scratch5.py
    "I own a resettable formula (like a recompute callable, but usage-tracks), and maintain a lazy invalidatable .value."
    _invalid = True ### ok? what about propogation?
    _memoized_value = None
    _version_counter = 1 ###k ??
    
    # ... [usual stuff removed]
    
    def get_value(self, args_each_time = None): # args_each_time can only be passed if you call this method explicitly
        "called whether or not we have the value"
        if self._invalid:
            self._recompute(args_each_time)
        return self._memoized_value
    def _recompute(self, args_each_time):
        "only called when we're invalid"
        new = self._compute_a_new_value(args_each_time)
        if new != self._memoized_value: # != ok? not for all numeric arrays? or is it? I forget. state_utils should say.
            self._version_counter += 1 ###k ??
            self._memoized_value = new
        self._invalid = False
        return
    def _compute_a_new_value(self, args_each_time):
        "return a newly computed value" ### what about usage tracking??
        return self._func(args_each_time)
            ###k actually call a formula, and let it usage-track for us, and we'll subscribe our inval to what we used.
            ### but does caller or this method do that? caller, since it might do funny things like choose memo place based on usage.    
    pass

class KidLval(_Lval):
    # this might have its own way to compute, ie a built-in python-coded formula-func, tho it might let superclass do usage tracking.
    # does that mean its own kind of formula, or an implicit builtin formula (since formulas do usage tracking)?
    def _raw_recompute(self, args_each_time): #####@@@@@ call me
        parent, index = args_each_time
        # this is where we put the code to ask the parent how to make that kid, and to make it,
        # but also, perhaps, to compare the inputs to last time and decide whether we really need to remake it (not sure).
        codeformula = parent._get_kid_codeformula(index) ####IMPLEM - this can change at runtime for the same kid, i think -- always remake then
        lexenv = parent._get_kid_lexenv(index) ####IMPLEM -- lexenv is an immutable and unchanging object, it's what we want here
        ###E compare codeformula to old value -- stored where??
        ## worse -- is it really a formula? how do we monitor changes? when do they mean we need a new kid? usually it's just 'code expr'...
        # lets assume that's what it is, for now.
        if 'need to recompute':
            'make a kid from lexenv, with index & code'
            code = codeformula
            kid = make_an_instance(code, lexenv, place)
                ####@@@@ also place? or, do we not even store that, but use it only at runtime? that might be a de-optim, but gives good flexibility --
                # lets instance run in multiple copies -- OTOH only if entire index chain is the same, so maybe it's a silly idea.
                #### wait, put in the index, relative to the parent... is it in the lexenv? I think so. no, only in spirit, as optim we separate it.
            return kid
        return None ##k??
    pass

def make_an_instance(code, lexenv, place):
    "somebody decided a new instance needs to be made, in a certain place (incl index_chain, storage)... make it."
    nim(pseudocode)
    return code(lexenv, place) # pseudocode ###@@@

# why not just pass the place-related make args, and decide locally what they contain (index, stores, etc), so we can change that later?
# and also the place-related each-frame args?? or do we have none of those? the old reasoning says none: they're often stable,
# so when they change we want to notice explicitly, so we optim for when they're stable.
# if we tried to let one instance live in two places, the optim data would all differ so we'd defeat the purpose.
# ... so the place-related args are all in make, and we might as well just call them the place!

class HelperClass:
    def __init__(self):
        self._kid_codeformulas = {} # convenience dict, of exceptions to whatever general rule we might have for these (??)
        self._kid_lexenvfuncs = {} # ditto, but missing or None ones are ok and mean "identity" (maybe)
        #e maybe one for coords? only in scenegraph model, not needed if we have _move
        self._kid_lvals = {} # this might define which kids we actually have (not sure, if set of kids could shrink & change back in one step)
        
    def _define_kid(self, index, codeformula = None, lexenvfunc = None): ### in general, is it best to pass these, or have a func to compute them?
        ####@@@@ decide by considering fancier-indexed iterators like Cube or Table.
        ### future note/digr:
        ### with fancy indexed sets with incremental inval, we'd need to receive inval signals for their pieces (values at indices).
        ### I imagine we could receive inval signals, new values, or mod-functions, or mod-func plus result
        ### (all of which are various portions of an "arrow" from old to new value of the piece in question).
        "[private] incremental make (or ensure made) of a kid"
        # pseudocode:
        new = not self._kid_lvals.has_key(index) # but even if not new, we might need to remake it... does that depend on code being new?
            # if so, is it automatic, from a diffing lval for the code, that will inval the kid-instance? #####@@@@@
        if new:
            self._kid_lvals[index] = KidLval(self, index) #### i don't like passing self (re cycles) -- maybe it won't need to store it??
            # what it might need it for is recomputing kid properties... maybe we can pass it self each time it needs that??
            # when it needs it is when we ask for the kid-value. hmm. Ditto for index I suppose?
        if codeformula is not None: # otherwise we're not preventing a subclass method from computing this (??)
            self._kid_codeformulas[index] = codeformula
        if lexenvfunc is not None: #### hmm, identity None is ambiguous with don't-change-it None, WRONG but tolerable for now ####@@@@
            self._kid_lexenvfuncs[index] = lexenvfunc
        #e something to be sure it's really made, or will be on demand; the kid needs to know its index
        #e something to see if we redefined those inputs? no, just guess we probably did if we called this
        self._kid_lvals[index].invalidate()
        #e how do we undefine a kid?
        return
    def _get_kid(self, index):
        ###e process saved-up kid index creations, if we ever buffer index creations from fancy indexed-set inputs
        lval = self._kid_lvals[index] # error if this does not exist, since keys define legal kids
        kid = lval.get_value( (self, index) ) # get the value -- the formula is assume to need this tuple of args, each time it runs,
            # and since we pass them, we're responsible for tracking invals in them and invalidating the kid
            # (as opposed to usage tracking occuring) ####@@@@ how does usage tracking fit in?
        return kid
    def _get_kid_lexenv(self, index):
        ###E memoize this -- really we want a recompute rule, i think... can it ever change? I don't think so...
        #e take parent lexenv, with localvars added, and use index to modify the various staterefs...
        # but how exactly does index interact, with different staterefs?
        # ... work that out later, ie write simple code now, quick to write & later read/revise.
        # uses of index: find transient state,
        # perhaps in various layers of differing permanence (ie same index-chain in different objects),
        # with varying sharing (ie different index-chains could point to same place, in some layer-objs but not others),
        # and also use it to get back to current coords: (index, parent) -> get to parent coords, then tell parent to get to mine via index.
        
        # something like: dict(_index = index, _inherit = parent-env) # where parent index chain is visible in _inherit, I guess... not sure & kluge.
        #### BTW it's so common for the index to be the only changing thing in the lexenv, that we might pass it in parallel as an optim/clarification.
        # then we ought to build up the chain explicitly as (local-index, parent-chain), and leave room for interning it as a key int, i suppose.
        # digr: do we intern it separately in separate layers? we might need to if they are persistent! (or intern it only in the most persistent one?)
        
        return self._lexenv # stub, and besides, are we supposed to store it? i suppose we might as well... could always zap if we finalize self...
    pass


# ==

