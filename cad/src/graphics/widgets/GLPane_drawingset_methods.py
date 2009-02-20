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

    def __get_csdl_collector(self):
        """
        get method for self.csdl_collector property:
        
        Initialize self._csdl_collector if necessary, and return it.
        """
        if not self._csdl_collector:
            self._csdl_collector = self._csdl_collector_class()
            # note: self._csdl_collector_class changes dynamically
        return self._csdl_collector
    
    def __set_csdl_collector(self):
        """
        set method for self.csdl_collector property; should never be called
        """
        assert 0
    
    def __del_csdl_collector(self):
        """
        del method for self.csdl_collector property
        """
        self._csdl_collector = None

    csdl_collector = property(__get_csdl_collector, __set_csdl_collector, __del_csdl_collector)

    def _has_csdl_collector(self):
        """
        @return: whether we presently have an allocated csdl_collector
                 (which would be returned by self.csdl_collector).
        @rtype: boolean
        """
        return self._csdl_collector is not None

    def before_drawing_csdls(self):
        """
        Whenever some CSDLs are going to be drawn by self.draw_csdl,
        call this first, draw them, and then call self.after_drawing_csdls.
        """
        # someday we might take args, e.g. an "intent map"
        del self.csdl_collector 
        self._csdl_collector_class = GLPane_csdl_collector
            # instantiated the first time self.csdl_collector is accessed

        if debug_pref("GLPane: use DrawingSets to draw model?",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = True ):
            self.csdl_collector.setup_for_drawingsets()
                # sets self.csdl_collector.use_drawingsets, and more
            pass
        return

    def draw_csdl(self, csdl, selected = False):
        """
        """
        ##### CALL IN MORE PLACES, in ChunkDrawer and ExternalBondSetDrawer
        ##### WRONG RE TRANSFORM in current calling code
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
        if not error:
            if self.csdl_collector.use_drawingsets:
                self._draw_drawingsets()
                # note, the DrawingSets themselves last between draw calls,
                # and are stored elsewhere in self. self.csdl_collector has
                # attributes used to collect necessary info during a
                # draw call for updating the DrawingSets before drawing them.
        del self.csdl_collector
        del self._csdl_collector_class # expose class default value
        return

    def _call_func_that_draws_model(self, func, *args, **kws):
        """
        Call func() between calls of self.before_drawing_csdls(*args)
        and self.after_drawing_csdls(). Return whatever func() returns
        (or raise whatever exception it raises, but call
         after_drawing_csdls even when raising an exception).

        func should usually be something which calls before/after_drawing_model
        inside it, e.g. one of the standard functions for drawing the
        entire model (e.g. part.draw or graphicsMode.Draw).
        """
        kws.pop('cachename', None) # not yet used; will be used to specify which drawingset cache to use ####
            # (by default, use drawing_phase, or in event methods, same as when drawing main model)
        assert not kws # no other optional args permitted yet
        self.before_drawing_csdls(*args)
        error = True
        res = None
        try:
            res = func()
            error = False
        finally:
            # (note: this is sometimes what does the actual drawing
            #  requested by func())
            self.after_drawing_csdls(error) 
        return res

    def _call_func_that_draws_objects(self, func, part):
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
        self._call_func_that_draws_model( func2, cachename = 'temp')
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
            ## print "_draw_drawingsets stub: selected = %r, %d csdls" % (selected, len( csdls )) ####
            d = DrawingSet(csdls.itervalues())
            # future: d.addCSDL(csdl), d.removeCSDL(csdl)
            d.draw(selected = selected)
            d.destroy()
        return

    pass # end of class

# end
