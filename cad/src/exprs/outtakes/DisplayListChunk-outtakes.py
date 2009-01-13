$Id$

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
this file should not remain in cvs once devel is done



class LvalForDisplistEffects(Lval): #stub -- see NewInval.py and paper notes
    """
    Lval variant, for when the value in question is the total drawing effect of calling an OpenGL display list
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

class DisplayListChunk(DelegatingWidget):
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
        """
        compile a call to our display list
        in a way which depends on whether we're compiling some other display list right now, in self.env.glpane --
        how to do that is handled by our displist owner / displist effects lval
        """
        self.displist_lval.call_displist() # this will call instance_of_arg1.draw() if it needs to compile that displist
    pass



# ==

class DisplistInvalidatable:
    pass ###
# several levels: opengl; invalidating a rewritable external subroutine; inval per se

from lvals.py:

class LvalForDrawingCode(Lval): #stub -- do we need this, or just pass an appropriate lambda to Lval? ##e
"""
[deal with get_value returning side effects? or using .draw instead -- just internally?]
"""
pass

"""
But when compiling another list, we're not *allowed* to do it that way, since we can't compile
        any other list (ours or one it calls) at the same time. Fortunately we don't have to, even if we don't
        discover which lists we call until we recompile ours, since it's safe to compile called lists
        later, as long as it happens before ours can next be called. So we add all lists we indirectly call
        (including our own) to a dict of lists maintained by the caller, which it will know it needs to recompile
        before calling ours. (In fact the caller is likely to run a recursive display list updating algorithm
        in which ours is not necessarily the top list; and the addition of our called lists has to occur lazily since they're
        not known until that algorithm recompiles ours


           To accomplish the above, we call 

        

        , since they differ in when our display list call
        will be executed. In immediate mode, we have to first separately compile the display list, in order
        to 
        
        (This might be executed immediately or compiled into another display list, depending on when we're called.)
        But a few extra effects are necessary:
        - If the contents of any display list used when ours is called are not up to date,
          we have to fix that before ours gets called. In immediate mode, this means, before emitting glCallList;
          if another list is being compiled, it means, sometime before that list's drawing effects are marked valid.
        ... tracking of two kinds, etc... explain recursion...

        list contents are not up to date, then before our list can be called,
        
        [Note: might be called when actual drawing is occurring, or when compiling another displist.]
"""

# ===

# Here are comments that might be up to date in main file, but even if so, might be redundant now,
# and in any case are old and have not been recently reviewed.
# So better to leave them out and rewrite them or review them later.


# ... maybe just write down the pseudocode for calling a display list in imm mode, which remakes some, which calls some in compiled mode?

"""
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

"""



in class DisplayListChunk:
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
    we would need a way of asking self.delegate.draw whether its output (i.e. the OpenGL commands it generates, usually reported only
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
    # has arg, self.delegate, can redraw it - it's an instance of a drawable
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

# ==

obs stuff

    def call_in_immediate_mode(self): #i think this is OBS
        self.ensure_ready_for_immediate_mode_call() ### change to external helper func, since it works on many objs of this class? yes.
        # or class method? (nah)
        self.call_our_displist() #### RENAME to make private

            old = glpane.begin_tracking_displist_calls(new_sublists_dict) ###IMPLEM
            try:
                self.recompile_our_displist() # render our contents into our displist using glNewList
            except:
                print_compact_traceback()
                pass
            glpane.end_tracking_displist_calls(old)

    def ensure_our_displist_gets_recompiled_asap(self):
        self.glpane.displists_needing_recompile_asap[ self.displist] = self
        return

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

--
        if 'self.delegate.draw() total effects changed': #####@@@@@ how to find out? not in usual way, that would draw it right now!
            # maybe: if self.delegate.draw_effects_version_counter > ... -- do we have to store version that got drawn, to make each
            # displist we call it in? no, just assume any inval tells us to remake it. inval propogate is enough, no counter needed,
            # i bet.
            ### or can we say, that would return a routine to draw it???
            ## also what need we do, to say that we've updated to use this info? will running thing.draw revalidate it?
            # not in all contexts, just this one! will it incr a counter, so we can look and see which draw effects are latest
            # and which ones we last grabbed? yes, i think so, esp since other inval objects need to "diff" results,
            # and the number would stand for the results, hash them as it were. maybe we need it too for some reason.
            #####@@@@
            if self.glpane.compiling_displist:
                self.do_glCallList()
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
            else:
                # immediate mode - don't call it until it's remade!
                ###e also need to recompile any lists listed in self.glpane.displists_needing_recompile_asap!!! i think...
                if 'oneway':
                    self.recompile_our_displist()
                    self.glpane.recompile_displists_that_need_it() # might do more lists than before prior statement added some ###
                    self.do_glCallList()
                else: # anotherway -- is this possible? only if we know in advance which lists will get used by the following!
                    assert 0, "nim, since we need to know more..."
                    #e recompile_displists_that_need_it, including ones we're about to call in following statement
                    self.recompile_and_execute_our_displist()
                pass
            pass
        else:
            self.do_glCallList()

--

the comments in the following now seem resolved, and the code correct, so removing most of them

    def invalidate_contents(self):
        "[private] called when something changes which might affect the sequence of OpenGL commands that should be compiled into self.displist" 
        ###e should propogate?? not sure -- this needs to inval the drawing effects of whatever drawing uses us...
        # but if something draws, does it track anything? what if the glpane itself calls us? this should tell it to gl_update!
        # but right now it doesn't... we'll need some fix for that! or a toplevel use of one of these for it... or an invalidator arg for this expr...
        # IN THEORY this means that glpane (or other pixmaps made from draw calls) should subs to total drawing effect,
        # whereas a dlist compile (calling the very same draw method) should only subs to opengl commands, not their effect!
        # THIS MAY PROVE THE NEED FOR TRACKING TWO DIFFERENT THINGS IN THE ENV for everything we can call in draw...
        # or maybe not, since if we use something, how could it know which to affect? it can't.
        # so only correct way is to switch effects over at the boundaries of compiling a list (smth like what we do)...
        # but not sure it's correct YET. Guess: it's fine if we change glpane to also notice dlist calls, and change this code to inval it
        # when a dlist runs in imm mode. This code should do that with a special routine in glpane, called in imm mode draw...
        # or maybe, easier, by "using a fake lval" then, and changing it when our drawing effects change...
        # then that lval would relate somehow to the flag we have and the subs to effects of sublist drawing. #####k DOIT - NEED TO FIGURE THIS OUT CLEARLY
        # ... ok: in general you have to track what you use with what in your env it would effect.
        # if you emit a calllist, then in imm mode, the total drawing effect of that affects the pixmap you draw onto and the other gl state...
        # but in compiling mode, only the opengl commands affect the gl state, but the other stuff they do has to be tracked in some other way
        # with the list owner. So we're assuming that the only opengl commands we do that have effects dependent on other gl state or other list contents
        # are the calllists, even though in general this might be false. But assuming that, all we need to do is "track different usage in those cases"
        # in self.draw. ###DOIT
        ## printnim("propogate inval from invalidate_contents") # but maybe the only one to really propogate is for our total drawing effects...
        if self.contents_valid:
            self.contents_valid = False
            self.invalidate_drawing_effects() #k I THINK this is all the propogation we need to do. NEED TO REVISE ABOVE COMMENT if so.
        else:
            # this clause would not be needed except for fear of bugs; it detects/complains/works around certain bugs.
            if self.drawing_effects_valid:
                print "bug: self.drawing_effects_valid when not self.contents_valid. Error, but invalidate_drawing_effects anyway."
                self.invalidate_drawing_effects()
            pass
        return

==

        # old cmt: prob wrong name [of method -- draw], see above

too obvious:
                    # (note: we pass self == self.displist owner, not self.displist)


