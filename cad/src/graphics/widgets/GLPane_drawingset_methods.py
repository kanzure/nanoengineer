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
        # occur between matched calls of _before/_after_drawing_csdls, since
        # drawing then is deprecated but needs to work,
        # so this class will work, but warn when created.
        # Its "normal" value is used between matched calls
        # of _before/_after_drawing_csdls.

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
        # accessed only in this class (as of 090317)

    def _has_csdl_collector(self): # not used as of 090317
        """
        @return: whether we presently have an allocated csdl_collector
                 (which would be returned by self.csdl_collector).
        @rtype: boolean
        """
        return self._csdl_collector is not None

    _current_drawingset_cache_policy = None # or a tuple of (temporary, cachename)

    def _before_drawing_csdls(self,
                             bare_primitives = False,
                             dset_change_indicator = None ):
        """
        [private submethod of _call_func_that_draws_model]

        Whenever some CSDLs are going to be drawn (or more precisely,
        collected for drawing, since they might be redrawn again later
        due to reuse_cached_drawingsets) by self.draw_csdl,
        call this first, draw them (I mean pass them to self.draw_csdl),
        and then call self._after_drawing_csdls.

        @param bare_primitives: when True, also open up a new CSDL
            and collect all "bare primitives" (not drawn into other CSDLs)
            into it, and draw it at the end. The new CSDL will be marked to
            permit reentrancy of ColorSorter.start, and will not be allowed
            to open up a "catchall display list" (an nfr for CSDL) since that
            might lead to nested display list compiles, not allowed by OpenGL.

        @param dset_change_indicator: if provided and not false,
            and if a certain debug_pref is enabled, then if _after_drawing_csdls
            would use a drawingset_cache and one already
            exists and has the same value of dset_change_indicator
            saved from our last use of that cache, we assume there
            is no need for the caller to remake the drawingsets in
            that cache, which we tell it (the caller) by returning True.
            (This is never fully correct -- for details see caller docstring.
             Soon [090313] we intend to add usage_tracking to make it much
             closer to being correct.)

        @return: usually False; True in special cases explained in the
            docstring for our dset_change_indicator parameter. WARNING:
            when we return true, our caller is REQUIRED (not just permitted)
            to immediately call _after_drawing_csdls (with certain options,
            see current calling code) without doing anything to its cached
            drawingsets/csdls -- i.e. to skip its usual "drawing".
        """
        # as of 090317, defined and used only in this class; will be refactored;
        # some other files have comments about it which will need revision then

        # someday we might take other args, e.g. an "intent map"
        del self.csdl_collector
        self._csdl_collector_class = GLPane_csdl_collector
            # instantiated the first time self.csdl_collector is accessed
            # (which might be just below, depending on prefs and options)

        self._remake_display_lists = self._compute_remake_display_lists_now()
            # note: this affects how we use both debug_prefs, below.

        res = False # return value, modified below

        cache = None # set to actual DrawingSetCache if we find or make one

        cache_began_usage_tracking = False # modified if it did that
            # [not yet fully implemented or used as of 090317, but should cause no harm]

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
                            # policy is None or a tuple of (temporary, cachename) [misnamed?]
                        cache = self._find_or_make_dset_cache_to_use(policy, make = False)
                        if cache:
                            if cache.saved_change_indicator == dset_change_indicator:
                                res = True
                        # NOTE: the following debug_pref is not yet implemented,
                        # and this method plus a few others will be heavily refactored
                        # before it is, since keeping track of (planned) usage tracking
                        # is getting too messy without that.
                        # So I if 0'd it (sort of) but left it in for illustration.
                        # [bruce 090317 comment]
                        if 0 and debug_pref("GLPane: usage-track cached DrawingSets?", #bruce 090313
                                      Choice_boolean_False, #####True,
                                      non_debug = True, # for now -- remove when works
                                      prefs_key = True
                                      ):
                            if not res:
                                # if we're reusing dset_cache, i.e. not remaking it,
                                # then no need to track usage "while remaking it";
                                # this must be synchronized with _after_drawing_csdls
                                # calling end_tracking_usage -- thus the requirements
                                # (new as of 090313) about caller honoring return value res
                                # (see our docstring); for robustness (since _after can't
                                # deduce this perfectly, at least not clearly) we also
                                # set a flag about whether we're doing this in the cache.
                                cache = self._find_or_make_dset_cache_to_use(policy, make = True)
                                    # (note make = True, different than earlier call)
                                cache.begin_tracking_usage() #### args?
                                #}
                                cache_began_usage_tracking = True
                                #} # fix word order (or just refactor this mess)
                                cache.track_use() ###### WRONG, do this when we draw it! (in _after I think)
                                #}
                                pass
                            pass
                        pass
                    pass
                pass
            pass
# following will be done in a better way when we refactor [bruce 090317 comment]:
##        if cache:
##            cache.is_usage_tracking = cache_began_usage_tracking ####### how do we know it's false if it's not?
##            #}
##            pass

        if debug_pref("GLPane: highlight atoms in CSDLs?",
                      Choice_boolean_True, #bruce 090225 revised
                          # maybe: scrap the pref or make it not non_debug
                      non_debug = True,
                      prefs_key = "v1.2/GLPane: highlight atoms in CSDLs?" ):
            if bare_primitives and self._remake_display_lists:
                self.csdl_collector.setup_for_bare_primitives()

        return res

    def _compute_remake_display_lists_now(self): #bruce 090224
        """
        [can be overridden in subclasses, but isn't so far]
        """
        # as of 090317, defined and used only in this class
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
        """
        [can be overridden in subclasses, but isn't so far]
        """
        # as of 090317, defined and used only in this class
        return env.mainwindow().movie_is_playing #bruce 051209
            # warning: use of env.mainwindow is a KLUGE;
            # could probably be fixed, but needs review for thumbviews

    def draw_csdl(self, csdl, selected = False, highlight_color = None):
        """
        Depending on prefs, either draw csdl now (with the given draw options),
        or make sure it will be in a DrawingSet which will be drawn later
        with those options.
        """
        # as of 090317, called in many drawing methods elsewhere (and one here),
        # defined only here; calls and API won't change in planned upcoming
        # refactoring, but implem might.

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
        # as of 090317, defined and used only in this class,
        # but logically, could be overridden in subclasses;
        # will probably not be changed during planned upcoming refactoring

        selected, highlight_color = intent # must match the code in draw_csdl
        if highlight_color is None:
            return dict(selected = selected)
        else:
            return dict(selected = selected,
                        highlighted = True,
                        highlight_color = highlight_color )
        pass

    def _after_drawing_csdls(self,
                            error = False,
                            reuse_cached_dsets_unchanged = False,
                            dset_change_indicator = None ):
        """
        [private submethod of _call_func_that_draws_model]

        @see: _before_drawing_csdls

        @param error: if the caller knows, it can pass an error flag
                      to indicate whether drawing succeeded or failed.
                      If it's known to have failed, we might not do some
                      things we normally do. Default value is False
                      since most calls don't pass anything. (#REVIEW: good? true?)

        @param reuse_cached_dsets_unchanged: whether to do what it says.
            Typically equal to the return value of the preceding call
            of _before_drawing_csdls.

        @param dset_change_indicator: if true, store in the dset cache
            (whether found or made, modified or not) as .saved_change_indicator.
        """
        # as of 090317, defined and used only in this class; will be refactored

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
        [should be overridden in subclasses which want to cache drawingsets]
        """
        # as of 090317, overridden in one subclass, called only in this class
        # (in _call_func_that_draws_model); might remain unchanged after
        # planned upcoming refactoring

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

        Call func() between calls of self._before_drawing_csdls(**kws)
        and self._after_drawing_csdls(). Return whatever func() returns
        (or raise whatever exception it raises, but call
         _after_drawing_csdls even when raising an exception).

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
        _before_drawing_csdls and _after_drawing_csdls, so they
        should not use csdls for drawing. (If we need to revise this,
        we might want to pass a list of funcs rather than a single func,
        with each one optimized separately for sometimes not being
        called; or more likely, refactor this entirely to make each
        func and its redraw-vs-reuse conditions a GraphicsRule object.)

        @param bare_primitives: passed to _before_drawing_csdls.

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
        # as of 090317, defined only here, called here and elsewhere
        # (in many places); likely to remain unchanged in our API for other
        # methods and client objects, even after planned upcoming refactoring,
        # though we may replace *some* of its calls with something modified,
        # as if inlining the refactored form.

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
        skip_dset_remake = self._before_drawing_csdls(
                        bare_primitives = bare_primitives,
                        dset_change_indicator = dset_change_indicator
         )
        # WARNING: if skip_dset_remake, we are REQUIRED (as of 090313)
        # (not just permitted, as before)
        # [or at least we would have been if I had finished implementing
        #  usage tracking -- see comment elsewhere for status -- bruce 090317]
        # to do nothing to any of our cached dsets or csdl collectors
        # (i.e. to do no drawing) before calling _after_drawing_csdls.
        # Fortunately we call it just below, so it's easy to verify
        # this requirement -- just don't forget to think about this
        # if you modify the following code. (### Todo: refactor this to
        # make it more failsafe, e.g. pass func to a single method
        # which encapsulates _before_drawing_csdls and _after_drawing_csdls...
        # but wait, isn't *this* method that single method? Ok, just make
        # them private [done] and document them as only for use by this
        # method [done]. Or maybe a smaller part of this really *should* be
        # a single method.... [yes, or worse -- 090317])
        error = True
        res = None
        try:
            if not skip_dset_remake:
                res = func()
            error = False
        finally:
            # (note: this is usually what does much of the actual drawing
            #  requested by func())
            self._after_drawing_csdls(
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
        # as of 090317, called in many places, overridden in some;
        # this will remain true after planned upcoming refactoring
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
        # as of 090317, defined only here, called only elsewhere;
        # likely to remain unchanged in our API for other methods,
        # even after planned upcoming refactoring
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

        # as of 090317, defined and used only in this class (in _after_drawing_csdls)

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
            intent_to_csdls.clear() # [no longer needed as of 090313]

        # set dset_cache to the DrawingSetCache we should use;
        # if it's temporary, make sure not to store it in any dict
        if incremental:
            # figure out (temporary, cachename)
            cache_before = self._current_drawingset_cache_policy # chosen during _before_drawing_csdls
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


        ##### REVIEW: do this inside some method of dset_cache?
        # This might relate to its upcoming usage_tracking features. [090313]
        if dset_change_indicator:
            dset_cache.saved_change_indicator = dset_change_indicator
            ##### REVIEW: if not, save None?

        if not reuse_cached_dsets_unchanged:
            # (note: if not incremental, then dset_cache is empty, so the
            #  following method just fills it non-incrementally in that case,
            #  so we don't need to pass an incremental flag to the method)
            dset_cache.incrementally_set_contents_to(
                intent_to_csdls,
##                dset_change_indicator = dset_change_indicator
             )

        del intent_to_csdls

        # draw all current DrawingSets
        dset_cache.draw( self,
                         self._draw_options,
                         debug = _DEBUG_DSETS,
                         destroy_as_drawn = dset_cache.temporary or not incremental
                             # review (not urgent): can this value be simplified
                             # due to relations between
                             # dset_cache.temporary and incremental?
                       )

        if dset_cache.temporary:
            #### REVIEW: do this in dset_cache.draw when destroy_as_drawn is true,
            # or when some other option is passed?

            # note: dset_cache is guaranteed not to be in any dict we have
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
        # as of 090317, called only in this class, in _before_drawing_csdls and
        # (during _after_drawing_csdls) in _draw_drawingsets;
        # defined only in this class
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

        [overridden in subclasses of the class we mix into;
         for calling, private to this mixin class]
        """
        # as of 090317, called only in this class, in _before_drawing_csdls and
        # (during _after_drawing_csdls) in _draw_drawingsets;
        # defined here and overridden in one other class
        return False, None

    pass # end of mixin class GLPane_drawingset_methods

# end
