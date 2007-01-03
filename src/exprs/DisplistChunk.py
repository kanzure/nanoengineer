"""
DisplistChunk.py

$Id$
"""

from basic import *

from changes import SelfUsageTrackingMixin # defines track_use, track_inval
from changes import SubUsageTrackingMixin # defines begin_tracking_usage, end_tracking_usage; doesn't use self

##e comment during devel -- see also some comments in lvals-outtakes.py and DisplistChunk-outtakes.py (in cvs, only during devel)
# (including long docstrings/comments that might be correct, but are unreviewed and partly redundant now)

# ===

# what follows is earlier code, moved here 061231 from NewInval.py -- might be mostly right, but not recently reviewed;
# now being revised to become real code


class GLPaneProxy: #WRONG; 061231: this might become a mixin for use in GLPaneOverrider or GLPane; #e rename it ###e
    compiling_displist = 0 #e change to point to the owner or None ###e rename to be private
    compiling_displist_owned_by = None
    def glNewList(self, listname, mode, owner = None):
        """Execute glNewList, after verifying args are ok and we don't think we're compiling a display list now.
        (The OpenGL call is illegal if we're *actually* compiling one now. Even if it detects that error (as is likely),
        it's not a redundant check, since our internal flag about whether we're compiling one could be wrong.)
           If owner is provided, record it privately (until glEndList) as the owner of the display list being compiled.
        This allows information to be tracked in owner or using it, like the set of sublists directly called by owner's list.
        Any initialization of tracking info in owner is up to our caller.###k doit
        """
        #e make our GL context current? no need -- callers already had to know that to safely call the original form of glNewList
        #e assert it's current? yes -- might catch old bugs -- but not yet practical to do.
        assert self.compiling_displist == 0
        assert self.compiling_displist_owned_by is None
        assert listname
        glNewList(listname, mode)
        self.compiling_displist = listname
        self.compiling_displist_owned_by = owner # optional, I guess ###CALL ME with this arg
        return
    def glEndList(self, listname = None):
        assert self.compiling_displist != 0
        if listname is not None: # optional arg
            assert listname == self.compiling_displist
        glEndList() # no arg is permitted
        self.compiling_displist = 0
        self.compiling_displist_owned_by = None
        return
    def glCallList(self, listname):
        "Compile a call to the given display list. Note: most error checking and any extra tracking is responsibility of caller."
        ###e in future, could merge successive calls into one call of multiple lists
        assert not self.compiling_displist # redundant with OpenGL only if we have no bugs in maintaining it, so worth checking
        assert listname # redundant with following?
        glCallList(listname)
        return
    def ensure_dlist_ready_to_call( dlist_owner_1 ): #e rename this and its vars, revise term "owner" in it [070102 cmt] ###CALL ME
        """[private helper method for use by DisplistChunk]
           This implements the recursive algorithm described in DisplistChunk.__doc__.
        dlist_owner_1 should be a DisplistOwner ###term; we use private attrs and/or methods of that class,
        including _key, _recompile_if_needed_and_return_sublists_dict().
           What we do: make sure that dlist_owner_1's display list can be safely called (executed) right after we return,
        with all displists that will call (directly or indirectly) up to date (in their content).
           Note that, in general, we won't know which displists will be called by a given one
        until after we've updated its content (and thereby compiled calls to those displists as part of its content).
           Assume we are only called when our GL context is current and we're not presently compiling a displist in it.
        """
        ###e verify our GL context is current, or make it so
        ###e verify we're not presently compiling a displist in it
        toscan = { dlist_owner_1._key : dlist_owner_1 }
        def collector( obj1, dict1):
            dlist_owner = obj1
            direct_sublists_dict = dlist_owner._recompile_if_needed_and_return_sublists_dict() # [renamed from _ensure_self_updated]
                # This says to dlist_owner: if your list is invalid, recompile it (and set your flag saying it's valid);
                # then you know your direct sublists, so we can ask you to return them.
                #   Note: it only has to include sublists whose drawing effects might be invalid.
                # This means, if its own effects are valid, it can optim by just returning {}.
                # [#e Someday it might maintain a dict of invalid sublists and return that. Right now it returns none or all of them.]
                ###IMPLEM the return and making that sometimes {}
                #   Note: during that call, the glpane (self) is modified to know which dlist_owner's list is being compiled. ###IMPLEM
                ###k need to check that comment is accurate
                ###e tell it effects valid at the end
            dict1.update( direct_sublists_dict )
        transclose(  toscan, collector )
        ###e now, for each dlist_owner we saw, tell it its drawing effects are valid. Only needed if it optims for knowing that.
        # to implem that, find out if transclose returns (or keeps in toscan) the complete dict, or if the last obj1 is guaranteed it,
        # or if we need to keep one separately.
        return
    pass # end of class GLPaneProxy #e rename it

# ==

######@@@@@@ Q: do we separate the object to own a displist, below, and the one to represent various Instances,
# like one for DisplistChunk and one for defining a displist-subroutine?
# (Do these even differ? [062023 addendum: One way they differ: whether highlighting treats their instances as separate objects.
#   But it might turn out this is just a matter of whether we use a DisplistChunk inside something for highlighting
#   which pushes its own glname for everything inside it, crossing it with whatever ones are inside it rather than being
#   overridden by them (just a flag on the name which matters when it's interpreted).])
# If we do, is the class below even an Instance with a draw method? (I doubt it. I bet it's an internal displist-owner helper object.)

#e digr: someday: it might be good for glpane to have a dict from allocated dlist names to their owning objects.
# Could we use displist names as keys, for that purpose?

class DisplistChunk( DelegatingInstanceOrExpr, SelfUsageTrackingMixin, SubUsageTrackingMixin ):
    """#doc
    [Note: the implicit value for SelfUsageTrackingMixin is the total drawing effect of calling our displist in immediate mode. Compare to class Lval.]
    [old long docstring and comment moved to outtakes file since unreviewed and partly redundant, 070102]
    """
    # default values of instance variables
    _direct_sublists_dict = 2 # intentional error if this default value is taken seriously
    contents_valid = False ###IMPLEM the set and reset of each of these flags, and the use of the 2nd one
    drawing_effects_valid = False
        # we don't yet have a specific flag for validity of sublist drawing effects (unknown when not contents_valid);
        # that doesn't matter for now; a useful optim someday would be a dict of all invalid-effects direct sublists #e
    
    # args
    delegate = Arg(Widget)
    
    # options
    # (none for now, but some will be added later)
    
    def _init_instance(self):
        self._key = id(self) # set attribute to use as dict key (could probably use display list name, but it's not allocated yet)
        self.glpane = self.env.glpane #e refile into superclass??
        
    def _C_displist(self): # compute method for self.displist
        ### WARNING: this doesn't recycle displists when instances are remade at same ipath (but it probably should),
        # and it never frees them. To recycle them, just change it to use transient_state.
        # When we start using more than one GL Context which share display lists, we'll have to revise this somehow.
        #
        ### NOTE: usage tracking should turn up nothing -- we use nothing
        "allocate a new display list name (a 32-bit int) in our GL context"
        self.glpane.makeCurrent() # not sure when this compute method might get called, so make sure our GL context is current
        displist = self.glpane.glGenLists(1) # allocate the display list name [#k does this do makeCurrent??]
        # make sure it's a nonzero int or long
        assert type(displist) in (type(1), type(1L))
        assert displist, "error: allocated displist was zero"
        return displist

    def draw(self):
        """Basically, we draw by emitting glCallList, whether our caller is currently
        compiling another display list or executing OpenGL in immediate mode.
           But if our total drawing effects are invalid (i.e. our own list and/or some list it calls
        has invalid contents), we must do some extra things, and do them differently in those two cases.
           In immediate mode, if our own display list contents are invalid, we have to recompile it (without
        executing it) and only later emit the call, since compiling it is the only way to find out what other
        display lists it currently calls (when using the current widget expr .draw() API). Further, whether
        or not we recompiled it, we have to make sure any other lists it calls are valid, recompiling them
        if not, even though they too might call other lists we can't discover until we recompile them.
           Since OpenGL doesn't permit nested compiles of display lists, we use a helper function:
        given a set of display lists, make sure all of them are ok to call (by compiling zero or more of them,
        one at a time), extending this set recursively to all lists they indirectly call, as found out when
        recompiling them. This involves calling .draw methods of arbitrary widgets, with a glpane flag telling
        them we're compiling a display list. (In fact, we tell them its controller object, e.g. self,
        so they can record info that helps with later redrawing them for highlighting or transparency.)
           When not in immediate mode, it means we're inside the recursive algorithm described above,
        which is compiling some other display list that calls us. We can safely emit our glCallList before or after
        our other effects (since it's not executed immediately), but we also have to add ourselves to
        the set of displists directly called by whatever list is being compiled. (Doing that allows the
        recursive algorithm to add those to the set it needs to check for validity. That alg can optim by
        only doing that to the ones we know might be invalid, but it has to record them as sublists of
        the list being compiled whether or not we're valid now, since it might use that later when we're
        no longer valid.)
           We do all that via methods and/or private dynamic vars in self.glpane. ###doc which
           Note that the recursive algorithm may call us more than once. We should, of course, emit a glCallList
        every time, but get recompiled by the recursive algorithm at most once, whether that happens due to side effects
        here or in the algorithm or both. (Both might be possible, depending on what optims are implemented. ###k)
           Note that recursive display list calls are possible
        (due to bugs in client code), even though they are OpenGL errors if present when executed. (BTW, it's possible
        for cycles to exist transiently in display list contents without an error, if this only happens when
        some but not all display lists have been updated after a change. This needs no noticing or handling in the code.)
        """
        # docstring revised 070102.
        # old cmt: prob wrong name [of method], see above

        self.displist
            # make sure we have a display list allocated
            # (this calls the compute method to allocate one if necessary)
            # [probably not needed explicitly, but might as well get it over with at the beginning]

        # are we being compiled into another display list?
        parent_dlist = self.glpane.compiling_displist_owned_by # note: a dlist owner or None, not a dlist name
        
        if parent_dlist:
            # We're being compiled into a display list (owned by parent_dlist); tell parent that its list calls ours.
            # (Note: even if we're fully valid now, we have to tell it,
            #  since it uses this info not only now if we're invalid, but later,
            #  when we might have become invalid. If we ever have a concept of
            #  our content and/or drawing effects being "finalized", we can optim
            #  in that case, by reducing what we report here.)
            parent_dlist.__you_called_dlist( self) ##e optim: inline this
                # (note: we pass self == self.displist owner, not self.displist)
                # (note: this will also make sure the alg recompiles us and whatever lists we turn out to call,
                #  before calling any list that calls us, if our drawing effects are not valid now.)
        elif self.glpane.compiling_displist:
            print "warning: compiling dlist %r with no owner" % self.glpane.compiling_displist
            #e If this ever happens, decide then whether anything but glCallList is needed.
            # (Can it happen when compiling a "fixed display list"? Not likely if we define that using a widget expr.)
        else:
            # immediate mode -- do all needed recompiles before emitting the glCallList,
            # and [nim###e] make sure glpane will be updated if anything used by our total drawing effect changes.
            # [this means make it the top of a tree of invals of total drawing effects, parallel to displist call tree; #e use a fake lval?]
            # [how does this work now for chunks? hmm... in theory the same way should work here. so use SelfUsageTrackingMixin if not already a superclass.]
            self.glpane.ensure_dlist_ready_to_call( self)
                # note: does transclose starting with self, calls _recompile_if_needed_and_return_sublists_dict
            self.track_use() # defined in SelfUsageTrackingMixin; compare to class Lval
                # note: this draw method only does this in immediate mode,
                # but when compiling displists, it can be done by callers in certain cases... ####e use special method?
        # emit the glCallList
        self.do_glCallList() ##e optim: inline this
        return # from draw

        # some old comments which might still be useful:

            } ###e subs to total effects inval
            
            # 061023 comments: analogous to Lval.get_value, both in .draw always being such, and in what's happening in following code.

            # Another issue - intermediate levels in a formula might need no lval objs, only ordinary compute calls,
            # unless they have something to memoize or inval at that level... do ordinary draw methods, when shared,
            # need this (their own capturing of inval flag, one for opengl and one for total effect,
            # and their own pair of usage lists too, one of called lists which can be scanned)??

    track_use_of_drawing_effects = track_use # this is semipublic; track_use itself (defined in SelfUsageTrackingMixin) is private
    
    def __you_called_dlist(self, dlist):
        "[private]"
        self.__new_sublists_dict[ dlist._key ] = dlist
            # note: this will intentionally fail if called at wrong time, since self.__new_sublists_dict won't be a dict then
        return
    
    def _recompile_if_needed_and_return_sublists_dict(self): #e needs some implems and optims, see comments
        ###e obs cmt: revise to not run or not be called when only kidlists need remaking
        """[private helper method for glpane.ensure_dlist_ready_to_call()]
        Ensure updatedness of our displist's contents (i.e. the OpenGL instructions last emitted for it)
        and of our record of its direct sublists (a dict of owners of other displists it directly calls).
        Return the dict of direct sublists.
           As an optim, it's ok to return a subset of that, which includes all direct sublists
        whose drawing effects might be invalid. (In particular, if our own drawing effects are valid,
        except perhaps for our own displist's contents, it's ok to return {}.) ###e DO THAT OPTIM
        """ # doc revised 070102
        if not self.contents_valid:
            ###e someday: detect recursive call of this displist -- not sure if this is simple unless it's a direct call
            
            self._direct_sublists_dict = 3 # intentional error if this temporary value is used as a dict
                # (note: this might detect the error of a recursive direct or indirect call)
            self.__new_sublists_dict = new_sublists_dict = {}
                # this is added to by draw methods of owners of display lists we call
            mc = self.begin_tracking_usage()
                # Note: we use this twice here, for different implicit values, which is ok since it doesn't store anything on self.
                # [#e i should make these non-methods to clarify that.]
                # This begin/end pair is to track whatever affects the OpenGL commands we compile;
                # the one below is to track the total drawing effects of the display lists called during that
                # (or more generally, any other drawing effects not included in that, but tracking for any other
                #  kinds of effects, like contents of textures we draw to the screen ### WHICH MIGHT MATTER, is nim).
                #
                # Note that track_use and track_inval do NOT have that property -- they store self.__subslist.
            try:
                self.recompile_our_displist() # render our contents into our displist using glNewList, self.delegate.draw(), glEndList
                    # note: has try/except so always does endlist ##e make it tell us if error but no exception??
            finally:
                self.end_tracking_usage( mc, self.invalidate_contents) # same invalidator even if exception during recompile or its draw
                self._direct_sublists_dict = dict(new_sublists_dict)
                    #e optim: this copy is only for bug-safety in case something kept a ref and modifies it later
                self.__new_sublists_dict = 4 # illegal dict value

            mc2 = self.begin_tracking_usage() # this tracks how our drawing effects depend on those of the sublists we call
            try:
                for sublist in self._direct_sublists_dict.itervalues():
                    sublist.track_use_of_drawing_effects() # (note: that's tracked into the global env)
            finally:
                self.end_tracking_usage( mc2, self.invalidate_drawing_effects )
                    # this gets subscribed to inval of total effects of sublists (effectively includes all indirectly called sublists too)
            self.contents_valid = True
                #k is it ok that we do this now but caller might look at it?? I think so since I think caller never needs to see it.
        if self.drawing_effects_valid:
            return {} # optim
        return self._direct_sublists_dict

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
        self.contents_valid = False
        self.invalidate_drawing_effects() #k I THINK this is all the propogation we need to do. NEED TO REVISE ABOVE COMMENT if so.

    def invalidate_drawing_effects(self):
        # note: compare to class Lval
        if self.drawing_effects_valid: ######IMPLEM the set True -- and another use?? not sure.
            # plan: make checklist of all needs of both inval paths. that's where i am 070102 436p.
            self.drawing_effects_valid = False
            # propogate inval to whoever used our drawing effects
            self.track_inval() # (defined in SelfUsageTrackingMixin)
        return

    def recompile_our_displist(self):
        "call glNewList/draw/glEndList in the appropriate way [private]"
        glpane = self.glpane
        displist = self.displist
        glpane.glNewList(displist, GL_COMPILE)
            # note: not normally a glpane method, but we'll turn all gl calls into methods so that glpane can intercept
            # the ones it wants to (e.g. in this case, so it can update glpane.compiling_displist)
            # note: we have no correct way to use GL_COMPILE_AND_EXECUTE, as explained in draw docstring
        try:
            self.delegate.draw()
        except:
            print_compact_traceback("exception while compiling display list for %r ignored, but terminates the list: " % self )
            ###e should restore both stack depths and as much gl state as we can
            # (but what if the list contents are not *supposed* to preserve stack depth? then it'd be better to imitate their intent re depths)
            pass
        glpane.glEndList(displist)
            # note: glEndList doesn't normally have an arg, but this arg lets glpane version of that method do more error-checking
        ###e do some tracking or set valid flags, or let caller do that??
        return
    
    def do_glCallList(self):
        "emit a call of our display list, whether or not we're called in immediate mode"
        self.glpane.glCallList( self.displist)
        return

    #e def __repr__, print list name and delegate
    
    pass # end of class DisplistChunk

# end
