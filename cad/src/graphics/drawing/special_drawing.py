# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
special_drawing.py - help class Chunk do special drawing in extra display lists

@author: Bruce
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

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
            # This happens 5 or 6 times when entering Build Atoms command;
            # not sure why, but probably ok.
            # Historical note: On 081003 I fixed what I thought was a typo below
            # (mainWindow -> mainwindow), here and in another place below,
            # and was surprised that this had no effect, and wondered why the
            # prior presumed exception had been silently discarded. In fact,
            # it was not a typo -- mainWindow is an alias for mainwindow in env.
            # So there was no exception and there is no mystery.
            # (An actual exception here causes, at least, a bug when hovering
            #  over a 3' strand end arrowhead, in Select Chunks mode.)
            # [bruce 081211 comment]            
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
# should be moved into foundation (it's related to changes.py),
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
    (independently of this object except for calls to self.get_value
     which the client does during its recomputation),
    then calls self.after_recompute().
    """

    _recomputing = False
    valid = False # whether client's recomputation is up to date,
        # as far as we know. Client should use this as *its* valid flag
        # and invalidate it as needed by calling self.invalidate().
    
    def __init__(self):
        # since not valid, no need to _reset
        return

    # == Methods to use during a recomputation by the client
    #    (or during a side effect treated as recomputation, such as drawing,
    #     where "whatever gets drawn" has the role of the computation output)
    
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
        self._recomputing = True
        return

    def get_value(self, key, context):
        """
        ... call this while redoing the client computation...
        ... it passes context along to self._compute_current_value ...
        It will record the value it returns, both to optimize repeated calls,
        and so it can be compared to the new current value
        by self.do_we_need_to_recompute()
        when the client next considers doing a recomputation.
        """
        # usage note: current code calls this (indirectly) in place of env.prefs
        # when drawing extra displist contents
        if not self._keys_used.has_key(key):
            val = self._compute_current_value(key, context)
            # review [081223]: should we track usage by that in changes.py manner,
            # into self.invalidate? NO! instead, either we or certain clients
            # ought to discard tracked usage from this! they can do that
            # since all worries about changes are taken care of by
            # our recording the value and comparing it.
            # (assuming, if side effects matter, they are uniquely
            #  labeled by the recorded value, e.g. it's a change_indicator
            #  or change_counter).
            # Guess: in current client code special_drawing) this is not done,
            # and it causes some unnecessary invals here, at least in principle.

            # inline our implementation of self._track_use
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

    # == methods to use between computations by the client

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
    
    # == methods to use when client is deciding whether to do a
    #    recomputation or reuse a cached value
    
    def do_we_need_to_recompute(self, context):
        """
        Assume the client is in a context in which it *could*
        safely/correctly recompute, in terms of _compute_current_value
        being safe to call and returning the correct value
        for whatever keys a recomputation would pass to it
        (when passed the given context parameter).

        @return: whether the client needs to do its recomputation (True)
                 or can reuse the result it got last time
                 (and presumably cached) (False)

        See class docstring for more info.
        """
        assert not self._recomputing
        if not self.valid:
            # the code below would be wrong in this case
            return True
        for key, val in self.ordered_key_val_pairs():
            # Note: doesn't call self._track_use, which would be a noop. ###todo: clarify
            newval = self._compute_current_value(key, context)
            if not same_vals(val, newval):
                #e Could optim the test for specific keys; probably not worth it
                #  though.
                ###TODO: OPTIM: Could optim self.before_recompute
                #    (for some callers -- REVIEW, which ones exactly?)
                #    to leave the values cached that were already found to be
                #    the same (by prior iterations of this loop).
                #    We'd do this by deleting the different values here
                #    (and the not yet compared ones);
                #    this would make the following note partly incorrect.
                # Note: We don't call self.invalidate() here, in case client
                # does nothing, current state changes, and it turns out we're
                # valid again. Clients doubting this matters, and which are not
                # going to recompute right away, and which want to optimize
                # repeated calls of this (by avoiding redoing the same_vals
                # tests) can call self.invalidate themselves. Most clients
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

    @note: this computes the same results as USE_CURRENT, but unlike it,
           does tracking with UsedValueTrackerAndComparator.
    """
    def __init__(self):
        UsedValueTrackerAndComparator.__init__(self)
        return
    
    def _compute_current_value(self, key, context):
        """
        Compute current value for key in context
        when needed by self.get_value implemented in superclass
        (which happens when superclass code has no cached value
         for this key in self).

        In this subclass, that value for key is computed
        by treating context as a GraphicsMode
        and calling its get_prefs_value method.
        """
##        print "compute current value:", key, context
        # require key to be in a hardcoded list??
        graphicsMode = context
        return graphicsMode.get_prefs_value(key) # see also USE_CURRENT

    def __getitem__(self, key):
        # KLUGE 1: provide this interface in this class
        # rather than in a wrapper class. (No harm, AFAIK, but only
        # because prefs key strings don't overlap any of our
        # public or private method or attribute names.)
        # KLUGE 2: get current global graphicsMode
        # instead of getting it from how we're called.
        # (See also USE_CURRENT, which also does this,
        #  but in its case it's not a kluge.)
        ### TODO to fix this kluge: make a "prefs value object" which
        # wraps this object but stores glpane, to use instead of this object.
        # But note that this would not work with glpane == a ThumbView
        # since ThumbView has no graphicsMode attribute! So we'd have to
        # wrap the "env-providing glpane" instead, i.e. the main one
        # for any ThumbView in current code.
        if debug_flags.atom_debug:
            print "fyi: getting %r from %r" % (key, self)
            # This happens a lot in Break Strands command, as expected.
            # See also the historical note about similar code above --
            # I mistakenly thought this code had an exception, but it didn't.
            # (An actual exception here causes Break Strands to not display
            #  strand-ending Ss atoms at all.)
            # [bruce 081211 comment]
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

    Has a public member, self.csdl, whose value is a
    ColorSortedDisplayList used for doing some kind of extra
    drawing associated with a Chunk, but not drawn as part of that chunk's main
    CSDL.

    Also holds the state that determines whether self.csdl is invalid,
    and under what conditions it will remain valid.
    
    Helps figure out when to invalidate it, redraw it, etc.

    External code can call self.csdl.draw(), but only when it knows
    that self.csdl is already valid. This probably means, only when
    highlighting self after it's already been drawn during the same frame.
    """
    
    # class constants
    
    # Subclass must override, with a subclass of UsedValueTrackerAndComparator.
    _comparator_class = None
    
    # default values of instance variables
    
    ## valid = False -- WRONG, we use self.comparator.valid for this.

    def __init__(self):
        self.csdl = ColorSortedDisplayList() # public member, see class docstring
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
            # needed by self._invalidate_display_lists for gl_update
            self._glpane = glpane
            self.end_tracking_usage( match_checking_code,
                                     self._invalidate_display_lists )
        return

    def _draw_by_reusing(self, glpane, selected, highlighted):
        """
        """
        # see also: code in Chunk.draw which uses its self.displist
        # and/or [ed.csdl for ed in self.extra_displists]
        self.csdl.draw(selected = selected, highlighted = highlighted)
        return

    # ==

    def invalidate(self):
        self.comparator.invalidate()
        return

    def _invalidate_display_lists(self):
        """
        This is meant to be called when something whose usage we tracked
        (while making our display list) next changes.
        """
        # print "fyi: called %r._invalidate_display_lists" % self # this happens
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
    is mainly the names of a few of its attributes we use and modify --
    I guess just chunk.extra_displists, a dict from special_drawing_kind
    to subclasses of ExtraChunkDisplayList.)

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

