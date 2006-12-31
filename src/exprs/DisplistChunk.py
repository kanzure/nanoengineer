"""
DisplistChunk.py

$Id$
"""

from lvals import Lval ##e make reloadable

##e during devel -- see also some comments in lvals-outtakes.py (not in cvs)

class LvalForDisplistEffects(Lval): #stub -- see NewInval.py and paper notes
    """Lval variant, for when the value in question is the total drawing effect of calling an OpenGL display list
    (which depends not only on the OpenGL commands in that display list, but on those in all display lists it calls,
    directly or indirectly).
       [The basic issues are the same as if the effect was of running an external subroutine, in a set of external subrs
    whose code we get to maintain, some of which call others. But there are a lot of OpenGL-specific details which affect
    the implementation. The analogous things (external Qt widgets, POV-Ray macros) are like that too, so it's unlikely
    a common superclass LvalForThingsLikeExternalSubroutines would be useful.]
    """
    def _compute_value(self):
        "[unlike in superclass Lval, we first make sure all necessary display list contents are up to date]"
        pass
    pass


##DelegatingWidget3D
DelegatingWidget # 2D or 3D -- I hope we don't have to say which one in the superclass! ###
# Can the Delegating part be a mixin? Even if it is, we still have to avoid having to say the 2D or 3D part... ###

class DisplistChunk(DelegatingWidget):
    def _init_instance(self):
        DelegatingWidget._init_instance(self)
        instance_of_arg1 # what is this? it needs to be set up by the prior statement, or by that time... see our make_in code... ###
        # allocate display list and its lval
        LvalForDisplistEffects # do what with this class? see below
        #e or could use _C_ rule for this kid-object, so it'd be lazy... but don't we need to pass it instantiation context? ####
        self.displist_lval = LvalForDisplistEffects( instance_of_arg1 )
        ####@@@@ like CLE, do we need to actually make one displist per instance of whatever we eval arg1 to??
        # problem is, there's >1 way to do that... so for now, assume no.
        pass
    def draw(self):
        """compile a call to our display list
        in a way which depends on whether we're compiling some other display list right now, in self.env.glpane --
        how to do that is handled by our displist owner / displist effects lval
        """
        self.displist_lval.call_displist() # this will call instance_of_arg1.draw() if it needs to compile that displist
    pass

# ===

# earlier code moved here 061231 from NewInval.py -- might be mostly right, but not recently reviewed

# ... maybe just write down the pseudocode for calling a display list in imm mode, which remakes some, which calls some in compiled mode?

'''
Reviewing situation of lvals for displists, 061023:

- What's interesting about draw methods in general, vs ordinary "compute methods":
  - they return their main value in the form of side effects
  - there are really two values they implicitly return, and the set of things used by these (re usage tracking for inval) differs!
    - the set of OpenGL commands they emit -- inval of this means any display list containing these commands needs rewriting
    - the effects on the current frame buffers of running those OpenGL commands -- this also depends on some of the GL state,
      including the content of certain display lists which they call (directly or indirectly, but only direct calls should be recorded,
       since the set of indirect calls might change due only to changes in content of directly called displists).
  - if drawing commands affect other OpenGL state, is their effect on each aspect of that state another thing that needs tracking?
    If so, the above two things are special cases:
    - effect on content of displist currently being compiled
    - effect on framebuffer contents, assuming no displisp is being compiled, *or* at a future time when current one is run.
  - complete tracking of these things would have to consider how OpenGL commands can *move* state between aspects of GL context state.
    I think we can ignore that now, since we're not compiling such general OpenGL into display lists.
    (Except in coordinate systems, if we compile a translation... which we can handle in a specialcase way.)
  - it may be that, in general, we need to generalize "track usage" to "track usage, and what state it affects",
    so anything we do (that gets usage-tracked) could say "I used this to affect that", where "that" is e.g. a specific display list,
    or the opengl commands being emitted.
  - a Q that needs answering, and leads to the above: if several kinds of usage are tracked, which one is tracked "normally"
    and which in special ways? I thought it was "displist calls are tracked specially, not variable accesses", but I'm having
    trouble explaining this rationally within the above framework.
     But, ordinary variable access, if it affects anything, affects both things we're tracking our effect on,
    since it affects our output of OpenGL. Display lists we call are the only things with a different effect on each one.
    This justifies tracking variable access in usual way, and called displists specially, but these *don't* correspond directly
    to the two things we can affect. It's as if we tracked usage in two parallel but independent worlds (python vars and opengl state)
    and "in the end" know how to combine them: drawing effect depends on both, opengl output depends on only one.

Preliminary conclusions:
- draw methods do track two different things... and ordinary var access tracking can be totally standard,
unaffected by the parallel tracking of calls of displists. Not sure yet about tracking effects on other OpenGL state,
esp if they use other OpenGL state. (Should we track an effective function we're applying to OpenGL state, via state = f(state)??)
- we do need a special kind of Lval whose value is the OpenGL commands issued into a display list;
and maybe another one, whose value is the OpenGL commands issued by any draw method. The latter is special re side effect output
and need for a version number (when we need to store inputs to whoever used it, for diff old and new in them);
the former is also special in the concern about which displists were called, and corresponds to an op on draw methods,
one is "run a displist" and the inner one is "emit its contents when compiling it". Maybe this means two special lval classes,
each having one inval flag, rather than one, handling two flags? ####@@@@

'''

class GLPaneProxy: #######@@@@@@@ WRONG and/or OBS
    compiling_displist = 0
    def __init__(self):
        self.displists_needing_recompile_asap = {}
    def recompile_displists_that_need_it(self):
        while self.displists_needing_recompile_asap:
            listname, object = self.displists_needing_recompile_asap.popitem()
            if not self._not_needing_recompile.has_key(listname):
                # what we do next can add items to that dict, right? hmm, can they be the ones we already popped??? ######@@@@@@
                self._not_needing_recompile[listname] = object # maybe we have to store a counter (saying when they were up to date)??
                ### make sure that if they are in here, we don't think we need to remake them, or maybe check when we pull them out
                object.recompile_our_displist()
        return
    def glNewList(self, listname, mode):
        ###e assert current? no, callers already had to know that to safely call original form, so we can be the same way
        assert not self.compiling_displist
        glNewList(listname, mode)
        self.compiling_displist = listname #e also store the control object?
        return
    def glEndList(self, listname = None):
        if listname:
            assert listname == self.compiling_displist
        glEndList() # no arg
        self.compiling_displist = 0
        return
    def glCallList(self, listname):
        ###e in future, could merge successive calls into one call of multiple lists
        assert not self.compiling_displist # redundant with OpenGL only if we have no bugs in maintaining it, so worth checking
        glCallList(listname)
        return
    pass

######@@@@@@ Q: do we separate the object to own a displist, below, and the one to represent various Instances,
# like one for DisplistChunk and one for defining a displist-subroutine?
# (Do these even differ? [062023 addendum: One way they differ: whether highlighting treats their instances as separate objects.
#   But it might turn out this is just a matter of whether we use a DisplistChunk inside something for highlighting
#   which pushes its own glname for everything inside it, crossing it with whatever ones are inside it rather than being
#   overridden by them (just a flag on the name which matters when it's interpreted).])
# If we do, is the class below even an Instance with a draw method? (I doubt it. I bet it's an internal displist-owner helper object.)

# singleton object - layer of displist proxies

def ensure_ready_to_call( dlist_owner_1 ):
    """[private helper function]
    dlist_owner_1 should be a DisplistOwner; we use private attrs and/or methods of that class,
    including _key, _ensure_self_updated(), _direct_sublists_dict.
       Make sure that dlist_owner_1's displist can be safely called right after we return,
    with all displists that will call (directly or indirectly) up to date (in their content).
    Note that, in general, we won't know which displists will be called by a given one
    until after we've updated its content (and compiled calls to those displists as part of its content).
       Assume we are only called when our GL context is current and we're not presently compiling a displist in it.
    """
    toscan = { dlist_owner_1._key : dlist_owner_1 }
    def collector( obj1, dict1):
        dlist_owner = obj1
        dlist_owner._ensure_self_updated() # if necessary, sets or updates dlist_owner._direct_sublists_dict
        dict1.update( dlist_owner._direct_sublists_dict )
    transclose(  toscan, collector )
    return

class DisplistChunkInstance( ComputeRuleMixin): ######@@@@@ RENAME to DisplistOwner or so (or proxy? no, tho sort of.)
    """Each object of this class owns one OpenGL display list (initially unallocated) in a specific OpenGL context,
    and keeps track of whether its contents (OpenGL commands, as actually stored in our GL context) might be invalid,
    and whether any of its kids' contents might be invalid.
    (By "kids" here, we mean any displists ours calls, directly or indirectly.)
       We also need to know how to regenerate our displist's contents on demand, tracking all displists it directly calls,
    as well as doing the usual usage-tracking of modifiable values on which the contents depends.
    We record these things separately so we can be invalidated in the necessary ways.
       A main public method ensures that our contents and our kids' contents are up to date.
    The algorithm is to transclose on the set of displists we call (including self.displist),
    and by calling a private method of this class on each one, to ensure updatedness of its contents
    and of its record of its direct kids, allowing us to tranclose on the direct kids.
       We also have a public method to call our displist in immediate mode, which must first use the prior method
    to ensure updatedness of all displists that that would call. (That means it has to use GL_COMPILE followed by glCallList,
    not GL_COMPILE_AND_EXECUTE, since in the latter case, it might encounter an unexpected call to a kid displist which is not
    up to date, and have no way to make it up to date, since OpenGL doesn't permit recursive compiling of displists.)
       We also have a method to compile a call to self.displist, which although callable by arbitrary commands' drawing code,
    is semi-private in that it's only legally called while some object of this class is compiling a displist, 
    and it assumes there is a global place in which to record that displist call for use by that object's tracking of called displists.
    # ==
       To fit with the "maybe-inval" scheme for avoiding recomputes that we were warned might be needed, but turn out not to be
    (as detected by a recompute rule noticing old and new values of all inputs are equal, or "equal enough" for how it uses them),
    we would need a way of asking self.thing.draw whether its output (i.e. the OpenGL commands it generates, usually reported only
    by side effect on a GL context -- note that its direct kidlist is a function of that output) would actually be different than
    the last time we called it for compiling into our display list.
       This is not yet implemented... it would probably require separation of "asking for drawing code", "diffing that" (via a proxy
    version-counter, or perhaps by direct graph comparison of the code's rep), and executing that in some GL context. ###k
       BTW [digr], I think the maybe-inval scheme in general is just to pass on a maybe-inval signal, and later to be asked
    whether inval is really needed, and to ask kids the same, perhaps diffing their values... the hard part is that different
    users of one value need different answers, e.g. if one user used it so long ago that it changed and changed back since then,
    though other users used it when it was changed. This is why we can't only ask the kid -- we can, but even if it recomputes,
    we have to diff to really know. I suspect this means that it's equivalent to an ordinary inval scheme, with each function
    also optimizing by memoizing the answer given certain inputs, namely the last ones it used. I'm not sure of all this. ###k
       Summary of public methods:
    - call our displist in immediate mode
    - call it while compiling another displist
    [both of those are called by glpane when it's asked to call a displist, or an array of them; it switches on its flag of whether
     it's currently compiling a displist; if it is, it knows the owning object, so it can *ask that object* to make the record.]
    MAYBE WRONG?, they are called by self.draw... ok?? no, prob not... ######@@@@@@
    - report our displist name (this is just the public attribute self.displist, which has a recompute rule)
    """
    # maybe semi-obs comments:
    
    # belongs to one gl-displist-context
    # has self.displist (glpane displist id in that context)
    # has arg, self.thing, can redraw it - it's an instance of a drawable
    # maintains formula: thing's draw-effects is an input to this guy's draw-effects
    #  so if thing's draw-effects change, and something wants "return" (do, where specified) of self draw-effects,
    #  and that caller might or might not be itself making a displaylist,
    #  then we can do that (by emitting a call of this guy's displist, perhaps merged with other calls if we call several in a row)
    #  (that merging can be autodone by our glpane, if it records all gl commands -- hmm, that's errorprone, leave it for later,
    #   it doesn't affect this guy's code anyway)
    #  but for callers making a displist, only if we warn caller that before it runs that displist, it better have us recompile ours,
    #  which we do by adding ourself to a set in the calling env;
    #  whereas for callers not making a displist, only if we *first* remake ours, before emitting the call,
    #  *or* if we remake ours in compile-execute mode (equiv since when it later means smth else, that doesn't matter anymore
    #  since current cmds not being saved) (and i'm not sure it's always possible to first remake ours, then call it)
    #  (though we can try and see -- it's a user pref which is mainly for debugging, might affect speed or gl-bugs)
    
    # if thing's draw effects don't change, and smth wants us to draw, in either case we just emit a call of the displist.

    # default values of instance variables
    _direct_sublists_dict = 3 # intentional error if this default value is taken seriously
    
    def __init__(self):
        self._key = id(self)
        
    def _compute_displist(self): # compute method for self.displist ###IMPLEM compute methods
        ###NOTE usage tracking should turn up nothing -- we use nothing
        "allocate a new display list name (a 32-bit int) in our GL context"
        self.glpane.makeCurrent() # not sure when this compute method might get called, so make sure our GL context is current
        self.displist = self.glpane.glGenLists(1) # allocate the display list name [#k does this do makeCurrent??]
        # make sure it's a nonzero int or long
        assert type(self.displist) in (type(1), type(1L)) and self.displist
        return

    def _ensure_self_updated(self): #e rename, and revise to not run or not be called when only kidlists need remaking
        """[private]
        Ensure updatedness of our displist's contents
        and of our record of its direct kids (other displists it directly calls).
        [if necessary, sets or updates self._direct_sublists_dict]
        [might be called while compiling a displist, other or ours, or not?? ###k]
        """
        self._direct_sublists_dict = 3 # intentional error if this value is taken seriously
        ###e what's needed [061023 guess]:
        # set up self._direct_sublists_dict in the dynenv or glpane, so that calls to displists are recorded in it.
        # BTW it might be good for glpane to have a dict from allocated dlist names to their owning objects.
        # Could we use displist names as keys, for that purpose?
        new_sublists_dict = {}
        glpane ###
        old = glpane.begin_tracking_displist_calls(new_sublists_dict) ###IMPLEM
        try:
            self.recompile_our_displist() # render our contents into our displist using glNewList
        except:
            print_compact_traceback()
            pass
        glpane.end_tracking_displist_calls(old)
        self._direct_sublists_dict = new_sublists_dict
        ### now, subscribe something to inval of those, but not sure if we do that right here
        ### also unsub whatever was subbed to the last set of them -- is that ever needed? what about in ordinary lvals?? ####@@@@
        ### also our caller will use them for its scanning alg
        assert 0, 'nim' #######@@@@@@@
        return
        
    def call_in_immediate_mode(self):
        self.ensure_ready_for_immediate_mode_call() ### change to external helper func, since it works on many objs of this class? yes.
        # or class method? (nah)
        self.call_our_displist() #### RENAME to make private


    # == old, some obs or wrong
    def draw(self): ######@@@@@@ prob wrong name, see above; also, wrong code.
        # 061023 comments: analogous to Lval.get_value, both in .draw always being such, and in what's happening in following code.
        #
        # need to make sure we have a list allocated -- this is implicit in grabbing its opengl listname from self.displist
        self.displist
        assert self.displist
        if 'self.thing.draw() total effects changed': #####@@@@@ how to find out? not in usual way, that would draw it right now!
            # maybe: if self.thing.draw_effects_version_counter > ... -- do we have to store version that got drawn, to make each
            # displist we call it in? no, just assume any inval tells us to remake it. inval propogate is enough, no counter needed,
            # i bet.
            ### or can we say, that would return a routine to draw it???
            ## also what need we do, to say that we've updated to use this info? will running thing.draw revalidate it?
            # not in all contexts, just this one! will it incr a counter, so we can look and see which draw effects are latest
            # and which ones we last grabbed? yes, i think so, esp since other inval objects need to "diff" results,
            # and the number would stand for the results, hash them as it were. maybe we need it too for some reason.
            #####@@@@
            if self.glpane.compiling_displist:
                self.call_our_displist()
                self.ensure_our_displist_gets_recompiled_asap() # this schedules something which will soon, but not now, call thing.draw
                    # (asap means before drawing the one being compiled, eg before any immediate mode drawing)
                    # WRONG [061023 comments]: just because total effects changed, doesn't mean gl commands changed.
                    # What is right is: recompile of this one (or each one in the tree of diplist calls) might not be needed;
                    # instead, visit the entire tree, but recomp only the ones that got an inval, and that does revise
                    # their list of kids in the tree (really a dag; don't recomp one twice -- inval flag reset handles that),
                    # then (using list of kids, and only first time hit, via transclose), look at list of kids.
                    # So each one stores the list of kids, and uses it two ways: subs to total effects inval, and scan them.
                    # This is stored next to "an lval for a displist's total effects". Maybe that points to "lval for dlist contents".
                    # In other words, two new lval classes: Lval for a displist effects, Lval for opengl coming out of a draw method.
                    # Another issue - intermediate levels in a formula might need no lval objs, only ordinary compute calls,
                    # unless they have something to memoize or inval at that level... do ordinary draw methods, when shared,
                    # need this (their own capturing of inval flag, one for opengl and one for total effect,
                    # and their own pair of usage lists too, one of called lists which can be scanned)??
            else:
                # immediate mode - don't call it until it's remade!
                ###e also need to recompile any lists listed in self.glpane.displists_needing_recompile_asap!!! i think...
                if 'oneway':
                    self.recompile_our_displist()
                    self.glpane.recompile_displists_that_need_it() # might do more lists than before prior statement added some ###
                    self.call_our_displist()
                else: # anotherway -- is this possible? only if we know in advance which lists will get used by the following!
                    assert 0, "nim, since we need to know more..."
                    #e recompile_displists_that_need_it, including ones we're about to call in following statement
                    self.recompile_and_execute_our_displist()
                pass
            pass
        else:
            self.call_our_displist()
        return
    def recompile_and_execute_our_displist(self): ### who does usage tracking, general and displist?
        assert 0, "never called"
        self.glpane.glNewList(self.displist, GL_COMPILE_AND_EXECUTE)
            # note: not normally a glpane method, but we'll turn all gl calls into methods so that self.glpane can intercept
            # the ones it wants to (e.g. in this case, so it can update self.glpane.compiling_displist)
        self.thing.draw()
        self.glpane.glEndList(self.displist) # doesn't normally have an arg, but this lets glpane interception do more error-checking
        return
    def recompile_our_displist(self):
        self.glpane.glNewList(self.displist, GL_COMPILE)
        self.thing.draw()
        self.glpane.glEndList(self.displist)
        return
    def call_our_displist(self): ### immd mode or not? what do we vs caller do?
        self.glpane.glCallList(self.displist)
        return
    def ensure_our_displist_gets_recompiled_asap(self):
        self.glpane.displists_needing_recompile_asap[ self.displist] = self
        return
    pass # end of class DisplistChunkInstance #e misnamed

# ==

class DisplistInvalidatable:
    pass ###
# several levels: opengl; invalidating a rewritable external subroutine; inval per se

# end
