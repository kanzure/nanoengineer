# Copyright 2006-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
DisplayListChunk.py

@author: Bruce
@version: $Id$
@copyright: 2006-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

061231 prototyped this code in NewInval.py

070102 moved it here 1-2 days ago, and revised it to seem correct; imports/reloads ok, but otherwise untested

070103 works, with important caveats re Highlightable (described below)

080215 renamed from DisplistChunk to DisplayListChunk

==

Still needed:
- maybe: some renamings, as commented
- provisions for highlighting (see just below in this docstring)
- include texture/image contents in the same scheme -- analogous to displist contents.
  Requires giving them compatible owner objects and treating those like we treat the ones
  for directly called display lists, aka sublists.

==

caveats re Highlightable [as of 070103]:

a Highlightable inside a DisplayListChunk only works properly (without highlight-position errors)
if no coord transform occurs from the DisplayListChunk to the Highlightable,
and no trackballing or other motion of whole thing from the last time the instance was made.
The second condition is impossible to guarantee, so in practice,
you should not use a Highlightable inside a DisplayListChunk until this is fixed.

Theory: the gl matrix is saved only once and only as it was when the displist was compiled.
Note, the rules would be even weirder (I predict) if nested display lists were involved --
then we'd need no transforms in any of them, re their calls of the next, for current code to work.

The best fix is the one planned on paper a few weeks ago -- have ExprsMeta decorate draw methods
with something that can call only the needed ones in a special scan for implementing draw_in_abs_coords.
(Idea now: the tree whose paths from root need to be marked, to implem that, is the tree of original
calls of draw methods. This was supposed to equal the ipath-suffix tree. Hopefully it does. If not,
the decorated draw methods themselves could generate ipath-like things for this purpose -- or really,
just pointers to the draw-method-owning parents in each one, to be stored in the objects with the draw methods.)

Update, 081202:

If you suspect this bug causes some unwanted behavior, you can test that by
temporarily setting the debug_pref "disable DisplayListChunk?" and seeing if
that fixes the unwanted behavior. (But it might also cause a large slowdown.)

But if there are bugs from the other nesting order of interaction, i.e. a DisplayListChunk
inside a Highlightable, that would fix those too. I'm not sure whether there are.

For example, as of 081202 morning, disabling DisplayListChunks fixes the following bug:
mousewheel zoom makes checkboxes inside DrawInCorner (and perhaps other
checkboxes) either not highlight, or if they are close enough to the center
of the screen (I guess), highlight in the wrong size and place (only where
the highlight image overlaps the original image, which happens for the top two
checkboxes when you zoom in by one wheel click). The bug is "reset" by
"clear state and reload" even if the zoom is still in effect, but additional
zoom causes the bug again. But panning or rotating the view does not cause
the bug (for reasons I don't fully understand, except that it must be related
to the fact that those don't alter the projection matrix but zoom does).

But I don't fully understand what causes this bug, and I don't know for sure
in which order the nesting is or whether being inside DrawInCorner is part of
the bug's cause. I do know it's alternatively fixable by using projection = True
in the Highlightable, so I'm going to change that to default True
(see comments there for reasoning and related plans).
As for the cause, it's probably related that only zoom, not pan or trackball,
caused the bug, and only zoom modifies the projection matrix.
But I don't have a complete explanation of either the bug or the fix.

*If* this bug comes from Highlightable inside DisplayListChunk,
maybe it could be fixed more optimally by detecting when that happens at runtime,
and setting projection = True only then? Maybe try this someday.
"""

from OpenGL.GL import GL_COMPILE

from utilities.debug_prefs import Choice_boolean_False
from utilities.debug_prefs import debug_pref
from utilities.debug import print_compact_traceback

from foundation.changes import SelfUsageTrackingMixin # defines track_use, track_inval; maintains a private __subslist on self
from foundation.changes import SubUsageTrackingMixin # defines begin_tracking_usage, end_tracking_usage; doesn't use self

from exprs.attr_decl_macros import Arg, ArgOrOption
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.widget2d import Widget
from exprs.py_utils import printfyi

##e comment during devel -- see also some comments in lvals-outtakes.py and DisplayListChunk-outtakes.py (in cvs, only during devel)
# (including long docstrings/comments that might be correct, but are unreviewed and partly redundant now)

# ==

# moved class GLPane_mixin_for_DisplayListChunk from here into GLPane.py, bruce 070110

# ==

###@@@ Q: do we separate the object to own a displist, below, and the one to represent various Instances,
# like one for DisplayListChunk and one for defining a displist-subroutine?
# (Do these even differ? [062023 addendum: One way they differ: whether highlighting treats their instances as separate objects.
#   But it might turn out this is just a matter of whether we use a DisplayListChunk inside something for highlighting
#   which pushes its own glname for everything inside it, crossing it with whatever ones are inside it rather than being
#   overridden by them (just a flag on the name which matters when it's interpreted).])
# If we do, is the class below even an Instance with a draw method? (I doubt it. I bet it's an internal displist-owner helper object.)

#e digr: someday: it might be good for glpane to have a dict from allocated dlist names to their owning objects.
# Could we use displist names as keys, for that purpose?

class DisplayListChunk( DelegatingInstanceOrExpr, SelfUsageTrackingMixin, SubUsageTrackingMixin ):
    """
    #doc
    [Note: the implicit value for SelfUsageTrackingMixin is the total drawing effect of calling our displist in immediate mode.
     This has an inval flag and invalidator, but we also have another pair of those for our display list's OpenGL contents,
     making this more complicated a use of that mixin than class Lval or its other uses.]
    [old long docstring and comment moved to outtakes file since unreviewed and partly redundant, 070102]
    """
    # default values of instance variables
    _direct_sublists_dict = 2 # intentional error if this default value is taken seriously
    contents_valid = False
    drawing_effects_valid = False
        # we don't yet have a specific flag for validity of sublist drawing effects (unknown when not contents_valid);
        # that doesn't matter for now; a useful optim someday would be a dict of all invalid-effects direct sublists #e
    
    # args
    delegate = Arg(Widget)
    
    # options
    debug_prints = ArgOrOption(str, None) # flag to do debug prints, and (unless a boolean) name for doing them

    def _C__debug_print_name(self): # compute self._debug_print_name
        """
        return False (meaning don't do debug prints), or a name string to prefix them with
        """
        # use this to say when we emit a calllist (and if so, immediate or into what other displist), and/or recompile our list
        #e and use in repr
        if self.debug_prints:
            if self.debug_prints == True:
                return "%r" % self ###BUG (suspected): this looks like an infrecur. Not sure if ever tested. [070110 comment]
            return str(self.debug_prints)
        return False
    
    def _init_instance(self):
        self._key = id(self) # set attribute to use as dict key (could probably use display list name, but it's not allocated yet)
        self.glpane = self.env.glpane #e refile into superclass??
        self._disabled = not hasattr(self.glpane, 'glGenLists')
        if self._disabled:
            # this should never happen after the merge of GLPane_overrider into GLPane done today [070110]
            print "bug: %r is disabled since its GLPane is missing required methods" % self
        return
        
    def _C_displist(self): # compute method for self.displist
        ### WARNING: this doesn't recycle displists when instances are remade at same ipath (but it probably should),
        # and it never frees them. To recycle them, just change it to use transient_state.
        # When we start using more than one GL Context which share display lists, we'll have to revise this somehow.
        #
        ### NOTE: usage tracking should turn up nothing -- we use nothing
        """
        allocate a new display list name (a 32-bit int) in our GL context
        """
        if self.displist_disabled(): # revised this cond (true more often), 070215
            printfyi("bug: why does .displist get requested in a disabled DisplayListChunk??") # (i never saw this)
            return 0
        
        self.glpane.makeCurrent() # not sure when this compute method might get called, so make sure our GL context is current
        displist = self.glpane.glGenLists(1) # allocate the display list name [#k does this do makeCurrent??]
        # make sure it's a nonzero int or long
        assert type(displist) in (type(1), type(1L))
        assert displist, "error: allocated displist was zero"
        if self._debug_print_name:
            print "%s: allocated display list name %r" % (self._debug_print_name, displist)
        return displist

    def __repr__(self):
        try:
            if not self._e_is_instance:
                return super(DisplayListChunk, self).__repr__()
            _debug_print_name = self._debug_print_name # only legal on an instance
        except:
            print "exception in self._debug_print_name discarded" #e print more, at least id(self), maybe traceback, if this happens
            # (but don't print self or you might infrecur!!)
            ##e can we print self.displist and/or self.delegate?
            return "<%s at %#x>" % (self.__class__.__name__, id(self))
        else:
            return "<%s(%s) at %#x>" % (self.__class__.__name__, _debug_print_name or "<no name>", id(self))
        pass

    def displist_disabled(self): #070215 split this out, modified it to notice _exprs__warpfuncs
        """
        Is the use of our displist (or of all displists) disabled at the moment?
        """
        return self._disabled or \
               debug_pref("disable DisplayListChunk?", Choice_boolean_False, prefs_key = True) or \
               getattr(self.env.glpane, '_exprs__warpfuncs', None) ###BUG: this will be too inefficient a response for nice dragging.
    
    def draw(self):
        """
        Basically, we draw by emitting glCallList, whether our caller is currently
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
        
        _debug_print_name = self._debug_print_name
        
        if self.displist_disabled():
            self.drawkid( self.delegate) ## self.delegate.draw()
            # I hope it's ok that this has no explicit effect on usage tracking or inval propogation... I think so.
            # It's equivalent to wrapping the whole thing in an If on this cond, so it must be ok.
            return
        
        self.displist
            # make sure we have a display list allocated
            # (this calls the compute method to allocate one if necessary)
            # [probably not needed explicitly, but might as well get it over with at the beginning]
            
            ###e NOTE: if someday we keep more than one displist, compiled under different drawing conditions in dynenv
            # (e.g. different effective values of glpane._exprs__warpfuncs),
            # then some or all of our attrs need splitting by the case of which displist to use,
            # and we also have to avoid usage-tracking the attrs that eval that case in the same way
            # as those we use when compiling displists. (As if we're If(cond, displistchunk1, displistchunk2),
            #  but also making sure nothing in displistchunk1 tracks those same attrs in a way we see as our own usage,
            #  or if it does, making sure we don't subscribe inval of a displist to that, by adding new code
            #  to end_tracking_usage to handle those usages specially, having known what they were by tracking cond, perhaps --
            #  or by explicit description, in case cond also tracks other stuff which doesn't show up in its value.
            #  Or another way, if the cond-value-attrs are special (e.g. glpane._exprs__warpfuncs),
            #  is for them to not be natively usage-tracked, but only when we eval cond (not sure this is ok re outsider tracking
            #  of them -- maybe better to track them except when we set a specialcase dynenv flag next to them,
            #  which they notice to decide whether to track uses, which we set when inside the specific case for the cond-value.)
            #  [070215]

        # are we being compiled into another display list?
        parent_dlist = self.glpane.compiling_displist_owned_by # note: a dlist owner or None, not a dlist name
        
        if parent_dlist:
            # We're being compiled into a display list (owned by parent_dlist); tell parent that its list calls ours.
            # (Note: even if we're fully valid now, we have to tell it,
            #  since it uses this info not only now if we're invalid, but later,
            #  when we might have become invalid. If we ever have a concept of
            #  our content and/or drawing effects being "finalized", we can optim
            #  in that case, by reducing what we report here.)
            if _debug_print_name:
                print "%s: compiling glCallList into parent list %r" % (_debug_print_name, parent_dlist)

            parent_dlist.__you_called_dlist( self) #e optim: inline this
                # (note: this will also make sure the alg recompiles us and whatever lists we turn out to call,
                #  before calling any list that calls us, if our drawing effects are not valid now.)
            
        elif self.glpane.compiling_displist:
            print "warning: compiling dlist %r with no owner" % self.glpane.compiling_displist
            #e If this ever happens, decide then whether anything but glCallList is needed.
            # (Can it happen when compiling a "fixed display list"? Not likely if we define that using a widget expr.)
            
        else:
            # immediate mode -- do all needed recompiles before emitting the glCallList,
            # and make sure glpane will be updated if anything used by our total drawing effect changes.
            if _debug_print_name:
                print "%s: prepare to emit glCallList in immediate mode" % (_debug_print_name, )
            
            self.glpane.ensure_dlist_ready_to_call( self) # (this might print "compiling glCallList" for sublists)
                # note: does transclose starting with self, calls _recompile_if_needed_and_return_sublists_dict
            self.track_use() # defined in SelfUsageTrackingMixin; compare to class Lval
                # This makes sure the GLPane itself (or whatever GL context we're drawing into, if it has proper usage tracking)
                # knows it needs to redraw if our drawing effects change.
                # Note: this draw method only does track_use in immediate mode (since it would be wrong otherwise),
                # but when compiling displists, it can be done by the external recursive algorithm via track_use_of_drawing_effects.
        if _debug_print_name:
            print "%s: emit glCallList(%r)" % (_debug_print_name, self.displist)
        self.do_glCallList() #e optim: inline this
        return # from draw

        # some old comments which might still be useful:
            
            # 061023 comments: analogous to Lval.get_value, both in .draw always being such, and in what's happening in following code.

            # Another issue - intermediate levels in a formula might need no lval objs, only ordinary compute calls,
            # unless they have something to memoize or inval at that level... do ordinary draw methods, when shared,
            # need this (their own capturing of inval flag, one for opengl and one for total effect,
            # and their own pair of usage lists too, one of called lists which can be scanned)??

    # this doesn't work due to quirks of Python:
    ## track_use_of_drawing_effects = track_use # this is semipublic; track_use itself (defined in SelfUsageTrackingMixin) is private
    # so rather than slow it down by a def,
    # I'll just rename the calls track_use but comment them as really track_use_of_drawing_effects

    def _your_drawing_effects_are_valid(self): ##e should inline as optim
        """
        """
        assert self.contents_valid
            # this failed 070104 with the exception shown in long string below, when I used clear "button" (070103 kluge) on one node...
            # theory: the world.nodelist change (by clear button run inside draw method, which is illegal -- that's the kluge)
            # invalidated it right when it was being recompiled (or just after, but before the overall recomp alg sent this call).
            # So that kluge has to go [later: it's gone],
            # and the underlying error of changing an input to an ongoing recompute has to be better detected. ####e
        self.drawing_effects_valid = True
        return

# the exception mentioned above: 
    """
atom_debug: fyi: <OneTimeSubsList(<LvalForState(<World#16291(i)>|transient.nodelist|('world', (0, (0, 'NullIpath')))) at 0x101a7b98>) at 0x10583850>'s 
event already occurred, fulfilling new subs 
<bound method usage_tracker_obj.standard_inval of <usage_tracker_obj(<DisplayListChunk(<no name>) at 0x111b7670>) at 0x112086e8>> immediately: 

[atom.py:414] [GLPane.py:1847] [GLPane.py:1884] [testmode.py:67] [testdraw.py:251] [GLPane_overrider.py:127]
[GLPane_overrider.py:138] [GLPane_overrider.py:298] [testmode.py:75] [testdraw.py:275] [testdraw.py:385]
[testdraw.py:350] [testdraw.py:384] [testdraw.py:530] [test.py:1231] [Overlay.py:57] [Overlay.py:57]
[Overlay.py:57] [DisplayListChunk.py:286] [DisplayListChunk.py:124] [state_utils.py:156] [DisplayListChunk.py:116]
[DisplayListChunk.py:358] [changes.py:352] [changes.py:421] [changes.py:72]

exception in testdraw.py's drawfunc call ignored: exceptions.AssertionError:

[testdraw.py:350] [testdraw.py:384] [testdraw.py:530] [test.py:1231] [Overlay.py:57] [Overlay.py:57]
[Overlay.py:57] [DisplayListChunk.py:286] [DisplayListChunk.py:127] [DisplayListChunk.py:314]
"""
    def __you_called_dlist(self, dlist):
        self.__new_sublists_dict[ dlist._key ] = dlist
            # note: this will intentionally fail if called at wrong time, since self.__new_sublists_dict won't be a dict then
        return
    
    def _recompile_if_needed_and_return_sublists_dict(self):
        """
        [private helper method for glpane.ensure_dlist_ready_to_call()]
        Ensure updatedness of our displist's contents (i.e. the OpenGL instructions last emitted for it)
        and of our record of its direct sublists (a dict of owners of other displists it directly calls).
        Return the dict of direct sublists.
           As an optim [mostly nim], it's ok to return a subset of that, which includes all direct sublists
        whose drawing effects might be invalid. (In particular, if our own drawing effects are valid,
        except perhaps for our own displist's contents, it's ok to return {}. [That's the part of this optim we do.])
        """ 
        # doc revised 070102
        if not self.contents_valid:
            # we need to recompile our own displist.
            if self._debug_print_name:
                print "%s: compiling our displist(%r)" % (self._debug_print_name, self.displist)
            
            self._direct_sublists_dict = 3 # intentional error if this temporary value is used as a dict
                # (note: this might detect the error of a recursive direct or indirect call -- untested ##k)
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
                self.recompile_our_displist()
                    # render our contents into our displist using glNewList, self.drawkid( self.delegate), glEndList
                    # note: has try/except so always does endlist ##e make it tell us if error but no exception??
            finally:
                self.contents_valid = True
                    # Q: is it ok that we do this now but caller might look at it?
                    # A: yes, since caller never needs to see it -- it's effectively private.
                self.end_tracking_usage( mc, self.invalidate_contents) # same invalidator even if exception during recompile or its draw
                self._direct_sublists_dict = dict(new_sublists_dict)
                    #e optim: this copy is only for bug-safety in case something kept a ref and modifies it later
                self.__new_sublists_dict = 4 # illegal dict value

            mc2 = self.begin_tracking_usage() # this tracks how our drawing effects depend on those of the sublists we call
            try:
                for sublist in self._direct_sublists_dict.itervalues():
                    sublist.track_use() # really track_use_of_drawing_effects (note: that's tracked into the global env, as always for track_use)
            finally:
                self.end_tracking_usage( mc2, self.invalidate_drawing_effects )
                    # this subscribes invalidate_drawing_effects to inval of total effects of all sublists
                    # (effectively including indirectly called ones too);
                    # the only thing it doesn't cover is subscribing it to inval of our own displist's contents,
                    # so we manually call it in invalidate_contents.
        if self.drawing_effects_valid:
            if debug_pref("DisplayListChunk: permit optim 070204?", Choice_boolean_False):
                ###BUG: this old optim seems to cause the bug 070203 -- I don't know why, but disabling it seems to fix the bug ###k
                print "doing optim 070204"#e and listnames [#e only print if the optim makes a difference?]
                return {} # optim; only possible when self.contents_valid,
                    # tho if we had a separate flag for sublist contents alone,
                    # we could correctly use that here as a better optim #e
            else:
                pass ## print "not doing optim 070204"#e and listnames
        return self._direct_sublists_dict

    def invalidate_contents(self):
        """
        [private] 
        called when something changes which might affect 
        the sequence of OpenGL commands that should be compiled into self.displist
        """
        if self.contents_valid:
            self.contents_valid = False
            self.invalidate_drawing_effects()
        else:
            # this clause would not be needed except for fear of bugs; it detects/complains/works around certain bugs.
            if self.drawing_effects_valid:
                print "bug: self.drawing_effects_valid when not self.contents_valid. Error, but invalidate_drawing_effects anyway."
                self.invalidate_drawing_effects()
            pass
        return
    
    def invalidate_drawing_effects(self):
        # note: compare to class Lval
        if self.drawing_effects_valid:
            self.drawing_effects_valid = False
            # propogate inval to whoever used our drawing effects
            self.track_inval() # (defined in SelfUsageTrackingMixin)
        return

    def recompile_our_displist(self):
        """
        [private] call glNewList/draw/glEndList in the appropriate way, 
        but do no usage tracking or valid-setting
        """
        glpane = self.glpane
        displist = self.displist
        glpane.glNewList(displist, GL_COMPILE, owner = self)
            # note: not normally a glpane method, but we'll turn all gl calls into methods so that glpane can intercept
            # the ones it wants to (e.g. in this case, so it can update glpane.compiling_displist)
            # note: we have no correct way to use GL_COMPILE_AND_EXECUTE, as explained in draw docstring
        try:
            self.drawkid( self.delegate) ## self.delegate.draw()
        except:
            print_compact_traceback("exception while compiling display list for %r ignored, but terminates the list: " % self )
            ###e should restore both stack depths and as much gl state as we can
            # (but what if the list contents are not *supposed* to preserve stack depth? then it'd be better to imitate their intent re depths)
            pass
        glpane.glEndList(displist)
            # note: glEndList doesn't normally have an arg, but this arg lets glpane version of that method do more error-checking
        return
    
    def do_glCallList(self):
        """
        emit a call of our display list, whether or not we're called in immediate mode
        """
        self.glpane.glCallList( self.displist)
        return
    
    pass # end of class DisplayListChunk

# end
