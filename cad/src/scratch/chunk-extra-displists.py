# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
chunk-extra-displists.py - scratch file to help with extra_displist code in class chunk

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

from graphics.drawing.ColorSorter import ColorSorter
from graphics.drawing.ColorSorter import ColorSortedDisplayList

from utilities.Comparison import same_vals
from foundation.state_utils import copy_val

class ExtraChunkDisplayList(object):
    """
    Holds one ColorSortedDisplayList used for doing some kind of extra
    drawing associated with a Chunk but not drawn as part of its main
    CSDL, along with the state that determines whether this CSDL is invalid,
    and under what conditions it will remain valid.
    
    Helps figure out when to invalidate it, redraw it, etc.
    """
    
    # class constants
    
    _comparator_class = None # subclass must override, with a subclass of UsedValueTrackerAndComparator

    # default values of instance variables
    
    valid = False

    def __init__(self):
        self.csdl = ColorSortedDisplayList()
        self._drawing_functions = [] # needed?
        self.comparator = self._comparator_class()
        return

    # == methods related to the client compiling its *main* display list
    # (not this extra one, but that's when it finds out what goes into
    #  this extra one, or that it needs it at all)
    
    def _before_client_main_recompile(self): #e rename?
        self._drawing_functions = []
        return
    
    def add_another_drawing_function(self, func): # during client main recompile
        self._drawing_functions.append( func)
        return

    def _after_client_main_recompile(self): #e rename?
        return

    # == methods for drawing self (with or without recompiling)
    
    def draw_but_first_recompile_if_needed(self, glpane, selected = False, highlighted = False, wantlist = True):
        """
        Recompile self as needed, then draw.
        Only make internal display lists (in cases where we need to remake them)
        if wantlist is true.

        @param selected: whether to draw in selected or plain style. (The same csdl handles both.)

        @param highlighted: whether to draw highlighted, or not. (The same csdl handles both.)
        """
        if not self.valid or self.comparator.do_we_need_to_recompute(): ##### also compare havelist, if some data not tracked
            self._draw_by_remaking(glpane, selected, highlighted, wantlist)
        else:
            self._draw_by_reusing(glpane, selected, highlighted)
        return

    def _draw_by_remaking(self, glpane, selected, highlighted, wantlist):
        """
        """
        # modified from similar code in Chunk.draw
        if wantlist:
            match_checking_code = self.begin_tracking_usage() ##### REQUIRES superclass
            ColorSorter.start(self.csdl)
        try:
            self._do_drawing()
        except:
            print_compact_traceback("bug: exception in %r._do_drawing, skipping the rest: " % self)
            pass
        if wantlist:
            ColorSorter.finish()
            self._glpane = glpane # needed by self.inval_display_list for gl_update
            self.end_tracking_usage( match_checking_code, self.inval_display_list )
        return

    def _draw_by_reusing(self, glpane, selected, highlighted):
        """
        """
        # see also: code in Chunk.draw which uses its self.displist
        self.csdl.draw(selected = selected, highlighted = highlighted)
        return

    # ==

    def invalidate(self):
        self.valid = False
        return

    def inval_display_list(self):
        """
        This is meant to be called when something whose usage we tracked
        (while making our display list) next changes.
        """
        self.invalidate()
        self._glpane.gl_update() # self._glpane should always exist
        return
    
    # ==
    
    def _do_drawing(self):
        # drawsphere(...), drawcylinder(...), drawpolycone(...), and so on.
        for func in self._drawing_functions:
            func() ### args?? e.g. self? some drawing prefs??
        return

    ### REVIEW below here, probably obs
    
    def set_input_data(self, data):
        """
        The client chunk has computed new data which determines
        (along with its own state?) what we should draw.
        Store it, and if it differs from old data, invalidate.
        """
        if not same_vals( self._data, data):
            self._data = copy_val(data)
            self.invalidate()
        return
    def set_validity_data(self, vdata):
        # for havelist contents i guess?
        if not same_vals( self._vdata, vdata):
            self._vdata = copy_val(vdata)
            self.invalidate()
        return
    pass

# ==

class StrandEnd_ExtraChunkDisplayList(ExtraChunkDisplayList):
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
    
    _comparator_class = StrandEnd_UsedValueTrackerAndComparator
    
    pass # end of class

# ======

class UsedValueTrackerAndComparator(object):
    """
    Client code will have one of these...
    when worried, call self.do_we_need_to_recompute,
    then if true, call self.before_recompute,
    do the computation, call self.after_recompute.
    """

    _recomputing = False
    valid = False
    
    def __init__(self):
        # since not valid, no need to _reset
        return

    # == methods to use during a recomputation by the client
    
    def before_recompute(self): #e rename
        """
        Prepare for the client to do another recomputation
        which will call self.get_value for all keys whose values
        we need to track usage of.
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

    def get_value(self, key, context): ##### @@@@@ CALL THIS SOMEHOW in place of env.prefs when drawing extra displist contents
        """
        ... call this while redoing the client computation...
        It will record the value it returns, both to optimize repeated calls,
        and so it can be compared to the new current value
        by self.are_all_values_still_the_same()
        when the client next considers doing a recomputation.
        """
        if not self._keys_used.has_key(key):
            val = self._compute_current_value(key, context)
            # inline _track_use
            self._keys_used[key] = val
            self._ordered_key_val_pairs += [(key, val)]
        else:
            val = self._keys_used[key]
        return val

    def _compute_current_value(self, key, context):
        assert 0, "subclass must implement %r._compute_current_value for key %r" % \
                  (self, key)
        pass

    def _track_use(self, key, val): 
        """
        """
        # safe public version, ok to call more than once for same key;
        # inlined by get_value;
        # REVIEW: perhaps this has no direct calls and can be removed?
        if not self._keys_used.has_key(key):
            self._keys_used[key] = val
            self._ordered_key_val_pairs += [(key, val)]
        return

    def after_recompute(self):
        """
        ... must be called by the client after it finishes its recomputation ...
        """
        assert self._recomputing
        del self._recomputing
        self.valid = True
        return

    # ==

    ## def invalidate(self): #### ambiguous: cause recompute or cause decision?
    ##     # del self._keys_used and self._ordered_key_val_pairs ?
    ##     pass
    
    # == methods to use when deciding whether to do a recomputation
    
    def do_we_need_to_recompute(self, context):
        """
        Do we need to recompute, now that we're in the current state
        of the given context (for purposes of current values at keys,
        as computed by self._compute_current_value)?
        """
        assert not self._recomputing
        if not self.valid:
            # following code would be wrong in this case
            return True
        for key, val in self.ordered_key_val_pairs():
            newval = self._compute_current_value(key, context) # note: doesn't call _track_use, which would be a noop
            if not same_vals(val, newval):
                #e could optim the test for specific keys; probably not worth it though
                #e could optim self.before_recompute (for some callers) to leave the values
                # cached that were already found to be the same (by prior iterations
                # of this loop)
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

class StrandEnd_UsedValueTrackerAndComparator(UsedValueTrackerAndComparator):
    """
    ... if necessary, reset and re-track the values used this time... knows how to compute them... 
    """
    def __init__(self):
        UsedValueTrackerAndComparator.__init__(self)
        return
    
    def _compute_current_value(self, key, context):
        """
        Compute current value for key in context
        when needed by self.get_value
        (since it has no cached value for this key).
        """
        # require key to be in a hardcoded list??
        graphicsMode = context
        methodname = key
        method = getattr(graphicsMode, methodname)
        return method()

    pass
