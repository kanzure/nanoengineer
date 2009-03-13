# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPane_drawingset_methods.py -- DrawingSet/CSDL helpers for GLPane_minimal

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 090219 refactored this out of yesterday's additions to
Part.after_drawing_model.
"""

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice_boolean_False, Choice_boolean_True

from utilities.debug import print_compact_traceback


import foundation.env as env


from graphics.drawing.DrawingSet import DrawingSet
from graphics.drawing.DrawingSetCache import DrawingSetCache

from graphics.widgets.GLPane_csdl_collector import GLPane_csdl_collector
from graphics.widgets.GLPane_csdl_collector import fake_GLPane_csdl_collector

_DEBUG_DSETS = False

# ==

class GLPane_drawingset_methods(object):
    """
    DrawingSet/CSDL helpers for GLPane_minimal, as a mixin class
    """
    # todo, someday: split our intended mixin-target, GLPane_minimal,
    # into a base class GLPane_minimal_base which doesn't inherit us,
    # which we can inherit to explain to pylint that we *do* have a
    # drawing_phase attribute, and the rest. These need to be in
    # separate modules to avoid an import cycle. We can't inherit
    # GLPane_minimal itself -- that is not only an import cycle
    # but a superclass-cycle! [bruce 090227 comment]
    
    _csdl_collector = None # allocated on demand

    _csdl_collector_class = fake_GLPane_csdl_collector
        # Note: this attribute is modified dynamically.
        # This default value is appropriate for drawing which does not
        # occur between matched calls of before/after_drawing_csdls, since
        # drawing then is deprecated but needs to work,
        # so this class will work, but warn when created.
        # Its "normal" value is used between matched calls
        # of before/after_drawing_csdls.

    _always_remake_during_movies = False # True in some subclasses

    _remake_display_lists = True # might change at start and end of each frame

    def __get_csdl_collector(self):
        """
        get method for self.csdl_collector property:
        
        Initialize self._csdl_collector if necessary, and return it.
        """
        try:
            ## print "__get_csdl_collector", self
            if not self._csdl_collector:
                ## print "alloc in __get_csdl_collector", self
                self._csdl_collector = self._csdl_collector_class( self)
                # note: self._csdl_collector_class changes dynamically
            return self._csdl_collector
        except:
            # without this try/except, python will report any exception in here
            # (or at least any AttributeError) as if it was an AttributeError
            # on self.csdl_collector, discarding all info about the nature
            # and code location of the actual error! [bruce 090220]
            ### TODO: flush all output streams in print_compact_traceback;
            # in current code, the following prints before we finish printing
            # whatever print statement had the exception partway through, if one did
            print_compact_traceback("\nfollowing exception is *really* this one, inside __get_csdl_collector: ")
            print
            raise
        pass
    
    def __set_csdl_collector(self):
        """
        set method for self.csdl_collector property; should never be called
        """
        assert 0
    
    def __del_csdl_collector(self):
        """
        del method for self.csdl_collector property
        """
        ## print "\ndel csdl_collector", self
        self._csdl_collector = None

    csdl_collector = property(__get_csdl_collector, __set_csdl_collector, __del_csdl_collector)

    def _has_csdl_collector(self):
        """
        @return: whether we presently have an allocated csdl_collector
                 (which would be returned by self.csdl_collector).
        @rtype: boolean
        """
        return self._csdl_collector is not None

    _current_drawingset_cache_policy = None # or a tuple of (temporary, cachename)
    
    def before_drawing_csdls(self,
                             bare_primitives = False,
                             dset_change_indicator = None ):
        """
        Whenever some CSDLs are going to be drawn by self.draw_csdl,
        call this first, draw them, and then call self.after_drawing_csdls.

        @param bare_primitives: when True, also open up a new CSDL
        and collect all "bare primitives" (not drawn into other CSDLs)
        into it, and draw it at the end. The new CSDL will be marked to
        permit reentrancy of ColorSorter.start, and will not be allowed
        to open up a "catchall display list" (an nfr for CSDL) since that
        might lead to nested display list compiles, not allowed by OpenGL.

        @param dset_change_indicator: if provided and not false,
            and if a certain debug_pref is enabled, then if after_drawing_csdls
            would use a drawingset_cache and one already
            exists and has the same value of dset_change_indicator
            saved from our last use of that cache, we assume there
            is no need for the caller to remake the drawingsets in
            that cache, which we tell it by returning True.
            (This is never fully correct -- for details see caller docstring.)

        @return: usually False; True in special cases explained in the
            docstring for our dset_change_indicator parameter.
        """
        # someday we might take other args, e.g. an "intent map"
        del self.csdl_collector 
        self._csdl_collector_class = GLPane_csdl_collector
            # instantiated the first time self.csdl_collector is accessed
            # (which might be just below, depending on prefs and options)

        self._remake_display_lists = self._compute_remake_display_lists_now()
            # note: this affects how we use both debug_prefs, below.

        res = False
        
        if debug_pref("GLPane: use DrawingSets to draw model?",
                      Choice_boolean_True, #bruce 090225 revised
                      non_debug = True,
                      prefs_key = "v1.2/GLPane: use DrawingSets?" ):
            if self._remake_display_lists:
                self.csdl_collector.setup_for_drawingsets()
                    # sets self.csdl_collector.use_drawingsets, and more
                    # (note: this is independent of self.permit_shaders,
                    #  since DrawingSets can be used even if shaders are not)
                self._current_drawingset_cache_policy = self._choose_drawingset_cache_policy()
                if debug_pref("GLPane: reuse cached DrawingSets? (has bugs)",
                              Choice_boolean_False,
                              non_debug = True,
                              prefs_key = True
                              ):
                    if dset_change_indicator:
                        policy = self._current_drawingset_cache_policy
                        cache = self._find_or_make_dset_cache_to_use(policy, make = False)
                        if cache:
                            if cache.saved_change_indicator == dset_change_indicator:
                                res = True

        if debug_pref("GLPane: highlight atoms in CSDLs?",
                      Choice_boolean_True, #bruce 090225 revised
                          # maybe: scrap the pref or make it not non_debug
                      non_debug = True,
                      prefs_key = "v1.2/GLPane: highlight atoms in CSDLs?" ):
            if bare_primitives and self._remake_display_lists:
                self.csdl_collector.setup_for_bare_primitives()

        return res

    def _compute_remake_display_lists_now(self): #bruce 090224
        remake_during_movies = debug_pref(
            "GLPane: remake display lists during movies?",
            Choice_boolean_True,
                # Historically this was hardcoded to False;
                # but I don't know whether it's still a speedup
                # to avoid remaking them (on modern graphics cards),
                # or perhaps a slowdown, so I'm making it optional.
                # Also, when active it will disable shader primitives,
                # forcing use of polygonal primitives instead;
                #### REVIEW whether it makes sense at all in that case.
                # [bruce 090224]
                # update: I'll make it default True, since that's more reliable,
                # and we might not have time to test it.
                # [bruce 090225]
            non_debug = True,
            prefs_key = "v1.2/GLPane: remake display lists during movies?" )

        # whether to actually remake is more complicated -- it depends on self
        # (thumbviews always remake) and on movie_is_playing flag (external).
        remake_during_movies = remake_during_movies or \
                               self._always_remake_during_movies
        remake_now = remake_during_movies or not self._movie_is_playing()
        if remake_now != self._remake_display_lists:
            # (kluge: knows how calling code uses value)
            # leave this in until we've tested the performance of movie playing
            # for both prefs values; it's not verbose
            print "fyi: setting _remake_display_lists = %r" % remake_now
        return remake_now

    def _movie_is_playing(self): #bruce 090224 split this out of ChunkDrawer
        return env.mainwindow().movie_is_playing #bruce 051209
            # warning: use of env.mainwindow is a KLUGE;
            # could probably be fixed, but needs review for thumbviews

    def draw_csdl(self, csdl, selected = False, highlight_color = None):
        """
        Depending on prefs, either draw csdl now (with the given draw options),
        or make sure it will be in a DrawingSet which will be drawn later
        with those options.
        """
        # future: to optimize rigid drag, options (aka "drawing intent")
        # will also include which dynamic transform (if any) to draw it inside.
        csdl_collector = self.csdl_collector
        intent = (bool(selected), highlight_color)
            # note: intent must match the "inverse code" in
            # self._draw_options(), and must be a suitable
            # dict key.
            # someday: include symbolic "dynamic transform" in intent,
            # to optimize rigid drag. (see scratch/TransformNode.py)
        if csdl_collector.use_drawingsets:
            csdl_collector.collect_csdl(csdl, intent)
        else:
            options = self._draw_options(intent)
            csdl.draw(**options)
        return

    def _draw_options(self, intent): #bruce 090226
        """
        Given a drawing intent (as created inside self.draw_csdl),
        return suitable options (as a dict) to be passed to either
        CSDL.draw or DrawingSet.draw.
        """
        selected, highlight_color = intent # must match the code in draw_csdl
        if highlight_color is None:
            return dict(selected = selected)
        else:
            return dict(selected = selected,
                        highlighted = True,
                        highlight_color = highlight_color )
        pass
    
    def after_drawing_csdls(self,
                            error = False,
                            reuse_cached_dsets_unchanged = False,
                            dset_change_indicator = None ):
        """
        @see: before_drawing_csdls

        @param error: if the caller knows, it can pass an error flag
                      to indicate whether drawing succeeded or failed.
                      If it's known to have failed, we might not do some
                      things we normally do. Default value is False
                      since most calls don't pass anything. (#REVIEW: good? true?)

        @param reuse_cached_dsets_unchanged: whether to do what it says.
            Typically equal to the return value of the preceding call
            of before_drawing_csdls.

        @param dset_change_indicator: if true, store in the dset cache
            (whether found or made, modified or not) as .saved_change_indicator.
        """
        self._remake_display_lists = self._compute_remake_display_lists_now()

        if not error:
            if self.csdl_collector.bare_primitives:
                # this must come before the _draw_drawingsets below
                csdl = self.csdl_collector.finish_bare_primitives()
                self.draw_csdl(csdl)
                pass
            if self.csdl_collector.use_drawingsets:
                self._draw_drawingsets(
                    reuse_cached_dsets_unchanged = reuse_cached_dsets_unchanged,
                    dset_change_indicator = dset_change_indicator
                 )
                # note, the DrawingSets themselves last between draw calls,
                # and are stored elsewhere in self. self.csdl_collector has
                # attributes used to collect necessary info during a
                # draw call for updating the DrawingSets before drawing them.
                pass
            pass
        del self.csdl_collector
        del self._csdl_collector_class # expose class default value
        return

    def _whole_model_drawingset_change_indicator(self):
        """
        """
        return None # disable this optim by default
    
    def _call_func_that_draws_model(self,
                                    func,
                                    prefunc = None,
                                    postfunc = None,
                                    bare_primitives = None,
                                    drawing_phase = None,
                                    whole_model = True
                                   ):
        """
        If whole_model is False (*not* the default):
        
        Call func() between calls of self.before_drawing_csdls(**kws)
        and self.after_drawing_csdls(). Return whatever func() returns
        (or raise whatever exception it raises, but call
         after_drawing_csdls even when raising an exception).

        func should usually be something which calls before/after_drawing_model
        inside it, e.g. one of the standard functions for drawing the
        entire model (e.g. part.draw or graphicsMode.Draw),
        or self._call_func_that_draws_objects which draws a portion of
        the model between those methods.

        If whole_model is True (default):

        Sometimes act as above, but other times do the same drawing
        that func would have done, without actually calling it,
        by reusing cached DrawingSets whenever nothing changed
        to make them out of date.

        Either way, always call prefunc (if provided) before, and
        postfunc (if provided) after, calling or not calling func.
        Those calls participate in the effect of our exception-protection
        and drawing_phase behaviors, but they stay out of the whole_model-
        related optimizations (so they are called even if func is not).
        
        @warning: prefunc and postfunc are not called between
        before_drawing_csdls and after_drawing_csdls, so they
        should not use csdls for drawing. (If we need to revise this,
        we might want to pass a list of funcs rather than a single func,
        with each one optimized separately for sometimes not being
        called; or more likely, refactor this entirely to make each
        func and its redraw-vs-reuse conditions a GraphicsRule object.)

        @param bare_primitives: passed to before_drawing_csdls.

        @param drawing_phase: if provided, drawing_phase must be '?'
            on entry; we'll set it as specified only during this call.
            If not provided, we don't check it or change it
            (typically, in that case, caller ought to do something
            to set it properly itself). The value of drawing_phase
            matters and needs to correspond to what's drawn by func,
            because it determines the "drawingset_cache" (see that
            term in the code for details).

        @param whole_model: whether func draws the whole model.
            Default True. Permits optimizations when the model appearance
            doesn't change since it was last drawn.
        """
        # todo: convert some older callers to pass drawing_phase
        # rather than implementing their own similar behavior.
        if drawing_phase is not None:
            assert self.drawing_phase == '?'
            self.set_drawing_phase(drawing_phase)
        if prefunc:
            try:
                prefunc()
            except:
                msg = "bug: exception in %r calling prefunc %r: skipping it" % (self, prefunc)
                print_compact_traceback(msg + ": ")
                pass
            pass
        if whole_model:
            dset_change_indicator = self._whole_model_drawingset_change_indicator()
            # note: if this is not false, then if a certain debug_pref is enabled,
            # then if we'd use a drawingset_cache and one already
            # exists and has the same value of dset_change_indicator
            # saved from our last use of that cache, we assume there
            # is no need to remake the drawingsets and therefore
            # no need to call func at all; instead we just redraw
            # the saved drawingsets. This is never correct -- in practice
            # some faster but nonnull alternative to func would need
            # to be called -- but is useful for testing the maximum
            # speedup possible from an "incremental remake of drawing"
            # optimization, and is a prototype for correct versions
            # of similar optimizations. [bruce 090309]
        else:
            dset_change_indicator = None
        skip_dset_remake = self.before_drawing_csdls(
                        bare_primitives = bare_primitives,
                        dset_change_indicator = dset_change_indicator
         )
        error = True
        res = None
        try:
            if not skip_dset_remake:
                res = func()
            error = False
        finally:
            # (note: this is usually what does much of the actual drawing
            #  requested by func())
            self.after_drawing_csdls(
                error,
                reuse_cached_dsets_unchanged = skip_dset_remake,
                dset_change_indicator = dset_change_indicator
             )
            if postfunc:
                try:
                    postfunc()
                except:
                    msg = "bug: exception in %r calling postfunc %r: skipping it" % (self, postfunc)
                    print_compact_traceback(msg + ": ")
                    pass
                pass
            if drawing_phase is not None:
                self.set_drawing_phase('?')
        return res

    def set_drawing_phase(self, drawing_phase):
        """
        [overridden in subclasses of the class we mix into;
         see those for doc]
        """
        return

    def _call_func_that_draws_objects(self, func, part, bare_primitives = None):
        """
        Like _call_func_that_draws_model,
        but also wraps func with the part methods
        before/after_drawing_model, necessary when drawing
        some portion of a Part (or when drawing all of it,
        but typical methods to draw all of it already do this
        themselves, e.g. part.draw or graphicsMode.Draw).

        This method's name is meant to indicate that you can pass us a func
        which draws one or more model objects, or even all of them,
        as long as it doesn't already bracket its individual object .draw calls
        with the Part methods before/after_drawing_model,
        like the standard functions for drawing the entire model do.
        """
        def func2():
            part.before_drawing_model()
            error = True
            try:
                func()
                error = False
            finally:
                part.after_drawing_model(error)
            return
        self._call_func_that_draws_model( func2,
                                          bare_primitives = bare_primitives,
                                          whole_model = False )
        return

    _dset_caches = None # or map from cachename to persistent DrawingSetCache
        ### review: make _dset_caches per-Part? Probably not -- might be a big
        # user of memory or VRAM, and the CSDLs persist so it might not matter
        # too much. OTOH, Part-switching will be slower without doing this.
        # Consider doing it only for the last two Parts, or so.
        # Be sure to delete it for destroyed Parts.
        #
        # todo: delete this when deleting an assy, or next using a new one
        # (not very important -- could reduce VRAM in some cases,
        #  but won't matter after loading a new similar file)
    
    def _draw_drawingsets(self,
                          reuse_cached_dsets_unchanged = False,
                          dset_change_indicator = None ):
        """
        Using info collected in self.csdl_collector,
        update our cached DrawingSets for this frame
        (unless reuse_cached_dsets_unchanged is true),
        then draw them.
        """
        ### REVIEW: move inside csdl_collector?
        # or into some new cooperating object, which keeps the DrawingSets?

        incremental = debug_pref("GLPane: use incremental DrawingSets?",
                          Choice_boolean_True, #bruce 090226, since it works
                          non_debug = True,
                          prefs_key = "v1.2/GLPane: incremental DrawingSets?" )

        csdl_collector = self.csdl_collector
        intent_to_csdls = \
            csdl_collector.grab_intent_to_csdls_dict()
            # grab (and reset) the current value of the
            # dict from intent (about how a csdl's drawingset should be drawn)
            # to a set of csdls (as a dict from their csdl_id's),
            # which includes exactly the CSDLs which should be drawn in this
            # frame (whether or not they were drawn in the last frame).
            # We own this dict, and can destructively modify it as convenient
            # (though ownership is needed only in our incremental case below).

        if reuse_cached_dsets_unchanged:
            # note: we assume reuse_cached_dsets_unchanged is never true
            # unless caller verified that the cached dsets in question
            # actually exist, so we don't need to check this
            assert incremental # simple sanity check of caller behavior
            intent_to_csdls.clear()

        # set dset_cache to the DrawingSetCache we should use;
        # if it's temporary, make sure not to store it in any dict
        if incremental:
            # figure out (temporary, cachename)
            cache_before = self._current_drawingset_cache_policy # chosen during before_drawing_csdls
            cache_after = self._choose_drawingset_cache_policy() # chosen now
            ## assert cache_after == cache_before
            if not (cache_after == cache_before):
                print "bug: _choose_drawingset_cache_policy differs: before %r vs after %r" % \
                      (cache_before, cache_after)
            dset_cache = self._find_or_make_dset_cache_to_use( cache_before)
        else:
            # not incremental:
            # destroy all old caches (matters after runtime prefs change)
            if self._dset_caches:
                for cachename, cache in self._dset_caches.items():
                    cache.destroy()
                self._dset_caches = None
                pass
            # make a new DrawingSetCache to use
            temporary, cachename = True, None
            dset_cache = DrawingSetCache(cachename, temporary)
            del temporary, cachename
            pass

        if dset_change_indicator:
            dset_cache.saved_change_indicator = dset_change_indicator
        
        persistent_dsets = dset_cache.dsets
            # review: consider refactoring to turn code around all uses of this
            # into methods in DrawingSetCache
        
        # handle existing dsets/intents
        if incremental and not reuse_cached_dsets_unchanged:
            # - if any prior DrawingSets are completely unused, get rid of them
            #   (note: this defeats optimizations based on intents which are
            #    "turned on and off", such as per-Part or per-graphicsMode
            #    intents)
            # - for the other prior DrawingSets, figure out csdls to remove and
            #   add; try to optimize for no change; try to do removals first,
            #   to save RAM in case cache updates during add are immediate
            for intent, dset in persistent_dsets.items(): # not iteritems!
                if intent not in intent_to_csdls:
                    # this intent is not needed at all for this frame
                    dset.destroy()
                    del persistent_dsets[intent]
                else:
                    # this intent is used this frame; update dset.CSDLs
                    # (using a method which optimizes that into the
                    #  minimal number of inlined removes and adds)
                    csdls_wanted = intent_to_csdls.pop(intent)
                    dset.set_CSDLs( csdls_wanted)
                    del csdls_wanted # junk now, since set_CSDLs owns it
                continue
            # - for completely new intents, make new DrawingSets in a quick way;
            #   we do this simply by running the non-incremental code outside
            #   this 'if' statement, but also persisting the new dsets.
            pass

        # handle new intents (incremental) or all intents (non-incremental):
        # make new DrawingSets for whatever intents remain in intent_to_csdls
        for intent, csdls in intent_to_csdls.items():
            del intent_to_csdls[intent]
                # (this might save temporary ram, depending on python optims)
            dset = DrawingSet(csdls.itervalues())
            persistent_dsets[intent] = dset
                # always store them here; remove them later if non-incremental
            del intent, csdls, dset
                # notice bug of reusing these below (it happened)
            continue

        del intent_to_csdls

        # draw all current DrawingSets
        if _DEBUG_DSETS:
            print
            print env.redraw_counter ,
            print "  cache %r%s" % (dset_cache.cachename,
                                     dset_cache.temporary and " (temporary)" or "") ,
            print "  (for phase %r)" % self.drawing_phase
            pass
        for intent, dset in persistent_dsets.items():
            if _DEBUG_DSETS:
                print "drawing dset, intent %r, %d items" % \
                      (intent, len(dset.CSDLs), )
                pass
            options = self._draw_options(intent)
            dset.draw(**options)
            if not incremental:
                # don't save them any longer than needed, to save RAM
                # (without this, we'd destroy them all at once near start
                #  of next frame, using code above, or later in this frame)
                dset.destroy()
                del persistent_dsets[intent]
            continue

        if dset_cache.temporary:
            # dset_cache is guaranteed not to be in any dict we have
            dset_cache.destroy()
        
        return

    def _find_or_make_dset_cache_to_use(self, policy, make = True):
        """
        Find, or make (if option permits), the DrawingSetCache to use,
        based on policy, which can be None if not make,
        or can be (temporary, cachename).

        @return: existing or new DrawingSetCache, or None if not make and
            no existing one is found.
        """
        # split out, bruce 090309
        if not make and not policy:
            return None
        temporary, cachename = policy
        if not make:
            return not temporary and \
                   self._dset_caches and \
                   self._dset_caches.get(cachename)
        else:
            if temporary:
                dset_cache = DrawingSetCache(cachename, temporary)
            else:
                if self._dset_caches is None:
                    self._dset_caches = {}
                dset_cache = self._dset_caches.get(cachename)
                if not dset_cache:
                    dset_cache = DrawingSetCache(cachename, temporary)
                    self._dset_caches[cachename] = dset_cache
                    pass
                pass
            return dset_cache
        pass

    def _choose_drawingset_cache_policy(self): #bruce 090227
        """
        Based on self.drawing_phase, decide which cache to keep DrawingSets in
        and whether it should be temporary.

        @return: (temporary, cachename)
        @rtype: (bool, string)

        [overridden in subclasses of the class we mix into]
        """
        return False, None

    pass # end of mixin class GLPane_drawingset_methods

# end
