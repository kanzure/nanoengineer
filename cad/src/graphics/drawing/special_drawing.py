# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
special_drawing.py - help class Chunk do special drawing in extra display lists

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

TODO:

Eventually, this should be divided into general and specific modules,
with some parts refiled into foundations.
"""

from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.ColorSorter import ColorSortedDisplayList

from utilities.Comparison import same_vals
from foundation.state_utils import copy_val

import foundation.env as env

from foundation.changes import SubUsageTrackingMixin

from utilities.debug import print_compact_traceback

from utilities import debug_flags

from OpenGL.GL import glCallList

DEBUG_COMPARATOR = False

# ==

class _USE_CURRENT_class(object):
    """
    ###TODO: doc
    """
    def __getitem__(self, key):
        # get the "current glpane" and its graphicsMode
        # (for purposes of determining modes & prefs)
        # (how we do it is not necessarily a kluge, given that this is being
        #  used to define a constant value for use when a better one was
        #  not passed)
        if debug_flags.atom_debug:
            print "fyi: getting %r from %r" % (key, self)
            # does this ever happen? I just fixed a typo below that would have
            # caused an exception every time it happens. Conceivably, this
            # will cause new bugs by making subsequent calling code work
            # differently than it has been. [bruce 081003]
            # Yes, this happens 5 or 6 times when entering Build Atoms command.
            # Not sure why; not sure why exception got silently discarded before;
            # not sure if enabling this code might make anything slower. ###
        win = env.mainwindow()
        glpane = win.glpane
        graphicsMode = glpane.graphicsMode
        # let the graphicsMode interpret the prefs key,
        # in case it wants to override it with a local pref
        # (or conceivably, someday, track it in a different way)
        # (note, ThumbView has no graphicsMode, but that doesn't
        #  affect this code since it uses main glpane even when
        #  drawing into a ThumbView. [bruce 080606 comment])
        try:
            res = graphicsMode.get_prefs_value(key)
        except:
            msg = "bug: exception in %r.get_prefs_value(%r), %s" % \
                  (graphicsMode, key, "falling back to env.prefs")
            print_compact_traceback(msg + ": ")
            res = env.prefs[key]
        return res
    pass

USE_CURRENT = _USE_CURRENT_class() ### TODO: doc

# ==

# kinds of special drawing (only one so far)

SPECIAL_DRAWING_STRAND_END = 'SPECIAL_DRAWING_STRAND_END'

ALL_SPECIAL_DRAWING_KINDS = [SPECIAL_DRAWING_STRAND_END]


# ===

# usage tracking functions
#
# when the dust settles, the general class here
# should be moved into foundation (related to changes.py)
# and the specific one into a module for the strand-end-specific
# part of this, unless it turns out to be more general than that
# (applying potentially to all prefs values).

class UsedValueTrackerAndComparator(object):
    """
    Abstract class. Subclasses must define method _compute_current_value,
    which computes the current value associated with some sort of key,
    e.g. a prefs key. They must also have "recomputation code"
    which calls self.get_value as described below.

    ### REVIEW whether this later guess is correct:
    It is *not* necessary for _compute_current_value to do
    "standard usage tracking" of the kind defined in changes.py.
    This class is not directly related to that facility.
    However, clients may want it to do that for their own purposes,
    to track usage into the context in which they're called.
    NOTE THAT WE CACHE VALUES and this will defeat that tracking
    unless client code calls self.invalidate whenever they might
    have changed. ###

    Client code will have an instance of this class for each recomputation
    it wants to track separately for the need to be redone.
    
    When the client wants to use the result of the computation and is
    worried it might not be current, it calls self.do_we_need_to_recompute(),
    which checks whether self.invalidate() has been called, and if not,
    whether all keys that were used (i.e. passed to self.get_value)
    last time it recomputed still have the same value (according to same_vals).

    If that's false, our client can safely use its cached result from
    the last time it recomputed.
    
    But if that's true, the client calls self.before_recompute(),
    then does the computation and records the result
    (independently of this object except for calls to self.get_value),
    then calls self.after_recompute().
    """

    _recomputing = False
    valid = False # whether client's recomputation is up to date,
        # as far as we know. Client should use this as *its* valid flag
        # and invalidate it as needed by calling self.invalidate().
    
    def __init__(self):
        # since not valid, no need to _reset
        return

    # == Methods to use during a recomputation (or side effect, such as drawing)
    #    by the client.
    
    def before_recompute(self): #e rename?
        """
        Prepare for the client to do another recomputation
        which will call self.get_value for all keys whose values
        we need to track usage of.

        See class docstring for more info.
        """
        assert not self._recomputing
        self._ordered_key_val_pairs = [] # in order of usage
            # note: order can matter, if some keys' values are not safe
            # to access for comparison unless others before them
            # still have the same values
        self._keys_used = {} # maps key -> val, but unordered
        self.valid = False
        # review: del self.valid?
        self._recomputing = True
        return

    def get_value(self, key, context):
        """
        ... call this while redoing the client computation...
        It will record the value it returns, both to optimize repeated calls,
        and so it can be compared to the new current value
        by self.do_we_need_to_recompute()
        when the client next considers doing a recomputation.
        """
        # usage note: current code calls this (indirectly) in place of env.prefs
        # when drawing extra displist contents
        if not self._keys_used.has_key(key):
            val = self._compute_current_value(key, context)
            # inline our implementation of _track_use
            self._keys_used[key] = val
            self._ordered_key_val_pairs += [(key, val)]
        else:
            val = self._keys_used[key]
        return val

    def _compute_current_value(self, key, context):
        assert 0, "subclass must implement %r%s %r" % \
                  (self, "._compute_current_value for key", key)
        pass

    def _track_use(self, key, val): 
        """
        """
        # safe public version, ok to call more than once for same key;
        # inlined by get_value;
        # REVIEW: perhaps this has no direct calls and can be removed?
        # NOTE: not directly related to env.track_use or the associated
        # usage tracking system in changes.py.
        if not self._keys_used.has_key(key):
            self._keys_used[key] = val
            self._ordered_key_val_pairs += [(key, val)]
        return

    def after_recompute(self):
        """
        Must be called by the client after it finishes its recomputation.
        
        See class docstring for more info.
        """
        assert self._recomputing
        del self._recomputing
        self.valid = True
        return

    # ==

    def invalidate(self):
        """
        Client realizes its recomputation is invalid for "external reasons".
        """
        if self.valid:
            self.valid = False
            # and that means these attrs won't be needed ...
            del self._keys_used
            del self._ordered_key_val_pairs
        return
    
    # == methods to use when deciding whether to do a recomputation
    
    def do_we_need_to_recompute(self, context):
        """
        Do we need to recompute, now that we're in the current state
        of the given context (for purposes of current values at keys,
        as computed by self._compute_current_value)?

        See class docstring for more info.
        """
        assert not self._recomputing
        if not self.valid:
            # following code would be wrong in this case
            return True
        for key, val in self.ordered_key_val_pairs():
            # Note: doesn't call self._track_use, which would be a noop.
            newval = self._compute_current_value(key, context)
            if not same_vals(val, newval):
                #e Could optim the test for specific keys; probably not worth it
                #  though.
                #e Could optim self.before_recompute (for some callers) to leave
                #  the values cached that were already found to be the same (by
                #  prior iterations of this loop)
                # Note: We don't call self.invalidate() here, in case client
                # does nothing, current state changes, and it turns out we're
                # valid again. Clients doubting this matters and wanting to
                # optimize repeated calls of this (if they're not going to
                # recompute right away) can call it themselves. Most clients
                # needn't bother since they'll recompute right away.
                return True
        return False
    
    def ordered_key_val_pairs(self):
        """
        @return: a list of zero of more (key, val) pairs
        that were used by our client computation the last time it ran.
        
        @warning: caller must not modify the list we return.
        """
        return self._ordered_key_val_pairs
    
    pass # end of class UsedValueTrackerAndComparator

# ==

class SpecialDrawing_UsedValueTrackerAndComparator( UsedValueTrackerAndComparator):
    """
    ... if necessary, reset and re-track the values used this time... knows how
    to compute them...
    """
    def __init__(self):
        UsedValueTrackerAndComparator.__init__(self)
        return
    
    def _compute_current_value(self, key, context):
        """
        Compute current value for key in context
        when needed by self.get_value
        (since it has no cached value for this key).

        @note: called by superclass get_value method.
        """
##        print "compute current value:", key, context
        # require key to be in a hardcoded list??
        graphicsMode = context
        return graphicsMode.get_prefs_value(key) # see also USE_CURRENT

    def __getitem__(self, key):
        # KLUGE 1: provide this interface in this class
        # rather than in a wrapper class. (No harm, AFAIK.)
        # KLUGE 2: get current global graphicsMode
        # instead of getting it from how we're called.
        # (See also USE_CURRENT, which also does this,
        #  but in its case it's not a kluge.)
        ### TODO to fix this kluge: make a "prefs value object" which
        # wraps this object but stores glpane, to use instead of this object.
        # But note that ThumbView has no graphicsMode attribute!
        if debug_flags.atom_debug:
            print "fyi: getting %r from %r" % (key, self)
            # does this ever happen? I just fixed a typo below that would have
            # caused an exception every time it happens. Conceivably, this
            # will cause new bugs by making subsequent calling code work
            # differently than it has been. [bruce 081003]
            # Yes, it happens a lot in Break Strands command.
        win = env.mainwindow()
        glpane = win.glpane
        graphicsMode = glpane.graphicsMode

        context = graphicsMode
        return self.get_value(key, context)

    pass

# ===

class ExtraChunkDisplayList(object, SubUsageTrackingMixin):
    """
    Abstract class. Subclass must define method
    _construct_args_for_drawing_functions.
    
    Holds one ColorSortedDisplayList used for doing some kind of extra
    drawing associated with a Chunk but not drawn as part of its main
    CSDL, along with the state that determines whether this CSDL is invalid,
    and under what conditions it will remain valid.
    
    Helps figure out when to invalidate it, redraw it, etc.
    """
    
    # class constants
    
    # Subclass must override, with a subclass of UsedValueTrackerAndComparator.
    _comparator_class = None
    
    # default values of instance variables
    
    ## valid = False -- WRONG, we use self.comparator.valid for this.

    def __init__(self):
        self.csdl = ColorSortedDisplayList()
        self.comparator = self._comparator_class()
        self.before_client_main_recompile() # get ready right away
        return

    def deallocate_displists(self):
        self.csdl.deallocate_displists()
    
    # == methods related to the client compiling its *main* display list
    # (not this extra one, but that's when it finds out what goes into
    #  this extra one, or that it needs it at all)
    
    def before_client_main_recompile(self): #e rename?
        self._drawing_functions = []
        return
    
    # During client main recompile.
    def add_another_drawing_function(self, func):
        self._drawing_functions.append( func)
        return

    def after_client_main_recompile(self): #e rename?
        ### todo: CALL THIS (when I figure out where to call it from)
        # (not urgent until it needs to do something)
        return

    # == methods for drawing self (with or without recompiling)

    def draw_nocolor_dl(self):
        if self.csdl.nocolor_dl:
            glCallList(self.csdl.nocolor_dl)
        else:
            print "unexpected: %r.draw_nocolor_dl with no nocolor_dl" % self
        return
    
    def draw_but_first_recompile_if_needed(
        self, glpane, selected = False, highlighted = False, wantlist = True):
        """
        Recompile self as needed, then draw.
        Only make internal display lists (in cases where we need to remake them)
        if wantlist is true.

        @param selected: whether to draw in selected or plain style. (The same
          csdl handles both.)

        @param highlighted: whether to draw highlighted, or not. (The same csdl
          handles both.)
        """
        graphicsMode = glpane.graphicsMode
            # note: ThumbView lacks this attribute;
            # for now, client code in Chunk worries about this,
            # and won't call us then. [bruce 080606 comment]
        context = graphicsMode
        if self.comparator.do_we_need_to_recompute(context):
            # maybe: also compare havelist, if some data not tracked
            if DEBUG_COMPARATOR:
                print "_draw_by_remaking in %r; valid = %r" % \
                      (self, self.comparator.valid)
            self._draw_by_remaking(glpane, selected, highlighted, wantlist)
        else:
            if DEBUG_COMPARATOR:
                print "_draw_by_reusing in %r" % self
            self._draw_by_reusing(glpane, selected, highlighted)
        return

    def _draw_by_remaking(self, glpane, selected, highlighted, wantlist):
        """
        """
        # modified from similar code in Chunk.draw
        if wantlist:
            match_checking_code = self.begin_tracking_usage()
                # note: method defined in superclass, SubUsageTrackingMixin
            ColorSorter.start(self.csdl, selected)
                ### REVIEW: is selected arg needed? guess yes,
                # since .finish will draw it based on the csdl state
                # which is determined by that arg. If so, this point needs
                # correcting in the docstring for csdl.draw().
        self.comparator.before_recompute()
        try:
            self._do_drawing()
        except:
            print_compact_traceback(
                "bug: exception in %r._do_drawing, skipping the rest: " % self)
            self.comparator.after_recompute()
                # note: sets self.comparator.valid (in spite of error)
            pass
        else:
            self.comparator.after_recompute()
        if wantlist:
            ColorSorter.finish()
            # needed by self.inval_display_list for gl_update
            self._glpane = glpane
            self.end_tracking_usage( match_checking_code,
                                     self.inval_display_list )
        return

    def _draw_by_reusing(self, glpane, selected, highlighted):
        """
        """
        # see also: code in Chunk.draw which uses its self.displist
        self.csdl.draw(selected = selected, highlighted = highlighted)
        return

    # ==

    def invalidate(self):
        self.comparator.invalidate()
        return

    def inval_display_list(self):
        """
        This is meant to be called when something whose usage we tracked
        (while making our display list) next changes.
        """
        # print "fyi: called %r.inval_display_list" % self # this happens
        self.invalidate()
        self._glpane.gl_update() # self._glpane should always exist
        return
    
    # ==
    
    def _do_drawing(self):
        # drawsphere(...), drawcylinder(...), drawpolycone(...), and so on.
        args = self._construct_args_for_drawing_functions()
        for func in self._drawing_functions:
            func(*args)
        return

    def _construct_args_for_drawing_functions(self):
        assert 0, "subclass must implement"
    
    pass # end of class ExtraChunkDisplayList

# ==

class SpecialDrawing_ExtraChunkDisplayList(ExtraChunkDisplayList):
    """
    """
    # note about current usage by client code (chunk drawing code):
    # this will be created on demand when something being drawn
    # during a chunk's main displist (CSDL) compile
    # wants to put things into a StrandEnd display list instead,
    # since that might need recompiling more often than the main one.
    # The chunk knows which subclass of ExtraChunkDisplayList to use
    # for each type of extra drawing, and allocates one on demand.
    # Then the object doing the drawing will give us a function
    # to use for redrawing itself, passing it to add_another_drawing_function.

    # subclass constants
    
    _comparator_class = SpecialDrawing_UsedValueTrackerAndComparator

    # overridden methods

    def _construct_args_for_drawing_functions(self):
##        prefs_value_finder = USE_CURRENT # KLUGE, but should partly work --
##            # we should construct one that uses the current glpane,
##            # but this one knows how to find it...
##            # but WRONG since it fails to do tracking as it ought to...
##            # namely through our own get_value call, with context = the GM.
        # ideally (non klugy): know glpane, and wrap self.comparator with it,
        # and give that wrapper a __getitem__ interface.
        # actual code: use our comparator subclass directly, give it
        # __getitem__, and make it find glpane dynamically (KLUGE).
        prefs_value_finder = self.comparator
        return (prefs_value_finder,)

    pass # end of class

# ===

class Chunk_SpecialDrawingHandler(object):
    """
    A kind of SpecialDrawingHandler for a Chunk.
    (There is not yet any other kind; what we know about class Chunk
    is mainly the names of a few of its attributes we use and modify,
    namely ###doc.)

    A SpecialDrawingHandler is .... #doc
    """
    def __init__(self, chunk, classes):
        """
        @param classes: a dict from special_drawing_kinds to subclasses of
                        ExtraChunkDisplayList whose method
                        _construct_args_for_drawing_functions returns
                        a tuple of one argument, namely a prefs_value_finder
                        which maps __getitem__ to get_value of a
                        SpecialDrawing_UsedValueTrackerAndComparator;
                        the only suitable class as of 080605 is
                        SpecialDrawing_ExtraChunkDisplayList.
        """
        self.chunk = chunk
        self.classes = classes
        return 
    def should_defer(self, special_drawing_kind):
        assert special_drawing_kind in ALL_SPECIAL_DRAWING_KINDS
        return self.classes.has_key(special_drawing_kind)

    #e rename?
    def draw_by_calling_with_prefsvalues(self, special_drawing_kind, func):
        # print "fyi: draw_by_calling_with_prefsvalues got", \
        #     special_drawing_kind, func # This happens.
        extra_displist = self._get_extra_displist(special_drawing_kind)
        extra_displist.add_another_drawing_function( func)
        return
    def _get_extra_displist(self, special_drawing_kind):
        """
        Find or make, and return, the right kind of ExtraChunkDisplayList
        for the given special_drawing_kind.
        """
        extra_displists = self.chunk.extra_displists
            # a dict from kind to extra_displist
        try:
            return extra_displists[special_drawing_kind]
        except KeyError:
            class1 = self.classes[special_drawing_kind]
            new = class1() #k args?
            extra_displists[special_drawing_kind] = new
            return new
        pass
    pass # end of class

# end

