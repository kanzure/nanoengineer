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
from utilities.debug_prefs import Choice_boolean_False

from utilities.debug import print_compact_traceback


import foundation.env as env


from graphics.drawing.DrawingSet import DrawingSet

from graphics.widgets.GLPane_csdl_collector import GLPane_csdl_collector
from graphics.widgets.GLPane_csdl_collector import fake_GLPane_csdl_collector

# ==

class GLPane_drawingset_methods(object):
    """
    DrawingSet/CSDL helpers for GLPane_minimal
    """
    
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

    def before_drawing_csdls(self, bare_primitives = False, cachename = None):
        """
        Whenever some CSDLs are going to be drawn by self.draw_csdl,
        call this first, draw them, and then call self.after_drawing_csdls.

        @param bare_primitives: when True, also open up a new CSDL
        and collect all "bare primitives" (not drawn into other CSDLs)
        into it, and draw it at the end. The new CSDL will be marked to
        permit reentrancy of ColorSorter.start, and will not be allowed
        to open up a "catchall display list" (an nfr for CSDL) since that
        might lead to nested display list compiles, not allowed by OpenGL.
        """
        # someday we might take other args, e.g. an "intent map" (related to cachename?)
        #### TODO: use cachename, and call with it;
        # issue of using too much ram: all whole-model caches should be the same;
        # small ones don't matter too much but might be best temporary in case they are not always small;
        # at least use the same cache in all temp cases.
        del self.csdl_collector 
        self._csdl_collector_class = GLPane_csdl_collector
            # instantiated the first time self.csdl_collector is accessed
            # (which might be just below, depending on prefs and options)

        self._remake_display_lists = self._compute_remake_display_lists_now()
            # note: this affects how we use both debug_prefs, below.
        
        if debug_pref("GLPane: use DrawingSets to draw model?",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True ):
            if self._remake_display_lists:
                self.csdl_collector.setup_for_drawingsets()
                    # sets self.csdl_collector.use_drawingsets, and more
            pass

        if debug_pref("GLPane: highlight prims in csdls?",
                      Choice_boolean_False,
                          # todo: when it works reliably, make default True and soon scrap the pref
                      non_debug = True,
                      prefs_key = True ):
            if bare_primitives and self._remake_display_lists:
                self.csdl_collector.setup_for_bare_primitives()

        return

    def _compute_remake_display_lists_now(self): #bruce 090224
        remake_during_movies = debug_pref(
            "GLPane: remake display lists during movies?",
            Choice_boolean_False,
                # Historically this was hardcoded to False;
                # but I don't know whether it's still a speedup
                # to avoid remaking them (on modern graphics cards),
                # or perhaps a slowdown, so I'm making it optional.
                # Also, when active it will disable shader primitives,
                # forcing use of polygonal primitives instead;
                #### REVIEW whether it makes sense at all in that case.
                # [bruce 090224]
            non_debug = True,
            prefs_key = True )

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

    def draw_csdl(self, csdl, selected = False):
        """
        """
        print "draw_csdl", csdl #########
        ##### TODO: call for chunk highlighting, and in ExternalBondSetDrawer
        csdl_collector = self.csdl_collector
        if csdl_collector.use_drawingsets:
            intent = bool(selected) #### for now 
            csdl_collector.draw_csdl_in_drawingset(csdl, intent)
        else:
            csdl.draw(selected = selected)
        return
    
    def after_drawing_csdls(self, error = False):
        """
        @see: before_drawing_csdls

        @param error: if the caller knows, it can pass an error flag
                      to indicate whether drawing succeeded or failed.
                      If it's known to have failed, we might not do some
                      things we normally do. Default value is False
                      since most calls don't pass anything. (#REVIEW: good? true?)
        """
        self._remake_display_lists = self._compute_remake_display_lists_now()

        if not error:
            if self.csdl_collector.bare_primitives:
                # this must come before the _draw_drawingsets below
                csdl = self.csdl_collector.finish_bare_primitives()
                self.draw_csdl(csdl)
                pass
            if self.csdl_collector.use_drawingsets:
                self._draw_drawingsets()
                # note, the DrawingSets themselves last between draw calls,
                # and are stored elsewhere in self. self.csdl_collector has
                # attributes used to collect necessary info during a
                # draw call for updating the DrawingSets before drawing them.
                pass
            pass
        del self.csdl_collector
        del self._csdl_collector_class # expose class default value
        return

    def _call_func_that_draws_model(self, func, **kws):
        """
        Call func() between calls of self.before_drawing_csdls(**kws)
        and self.after_drawing_csdls(). Return whatever func() returns
        (or raise whatever exception it raises, but call
         after_drawing_csdls even when raising an exception).

        func should usually be something which calls before/after_drawing_model
        inside it, e.g. one of the standard functions for drawing the
        entire model (e.g. part.draw or graphicsMode.Draw).
        """
        self.before_drawing_csdls(**kws) # kws: bare_primitives, cachename
        error = True
        res = None
        try:
            res = func()
            error = False
        finally:
            # (note: this is sometimes what does the actual drawing
            #  requested by func())
            self.after_drawing_csdls( error) 
        return res

    def _call_func_that_draws_objects(self, func, part, **kws):
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
        use_kws = dict(cachename = 'temp') # default kws
        use_kws.update(kws)
        self._call_func_that_draws_model( func2, **use_kws)
        return
    
    def _draw_drawingsets(self):
        """
        Using info collected in self.csdl_collector,
        update our cached DrawingSets for this frame;
        then draw them.
        """
        ### REVIEW: move inside csdl_collector?
        # or into some new cooperating object, which keeps the DrawingSets?
        csdl_collector = self.csdl_collector
        for intent, csdls in csdl_collector.get_drawingset_intent_csdl_dicts().items():
            # stub: make drawingset from these csdls, then draw it based on intent.
            # - slow since not incremental
            # - incorrect since transforms are ignored
            #   (they're only present in gl state when csdl is added!)
            selected = intent
            ## print "_draw_drawingsets stub: selected = %r, %d csdls" % (selected, len( csdls ))
            d = DrawingSet(csdls.itervalues())
            # future: d.addCSDL(csdl), d.removeCSDL(csdl)
            d.draw(selected = selected)
            d.destroy()
        return

    pass # end of class

# end
