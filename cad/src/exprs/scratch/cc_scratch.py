# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""

$Id$

"""

from exprs.basic import *


# stuff to set up the env... see what testdraw does

# a place to make instances, new ones have totally fresh state, but only keep one, or let caller supply index...



# ===

def find_or_make(cctype, mode):
    "Return a confirmation corner instance for mode, of the given cctype."
    if 1:
        return None # stub


    # We keep the instances in a global place shared by all modes, indexed by cc_data.
    # They have their own state & drawing env, separate from those of other expr Instances
    # (so far, that just means the ones made by and used in testmode).
    # For using reloaded code during devel, we can provide a cmenu item or the like, to clear that place. #e
    # (Thus no need for the index to contain a reload counter.)
    #
    # Do we need usage-tracking and remaking of instances? Only if they depend on env.prefs variables.
    # In theory they might, so we'll provide it.
    # This code may be split out and refiled...
##    LvalDict2()
        # ... hmm, what do i use for:
        # MT_try2 (self.Instance with computed index, thus indirectly uses LvalDict2 via _CV_)
        #   ### self.Instance needs optim - option to avoid expr compare, don't even bother with grabarg if instance is cached
        # and find_or_make_main_instance? (custom compare & cache)
        # and texture_holder? (texture_holder_for_filename = MemoDict(_texture_holder))


#e refile some of this into other files in exprs module: (might have to split pieces out, to do that)
class cc_memoizer(InstanceOrExpr):
    def find_or_make(self, cctype, mode):
        ""
        bgcolor_data = None #e this should be a function of mode.bgcolor which affects the look of the CC icons
        cc_data = (cctype, bgcolor_data) # this is everything which needs to affect the CC instance.
            ###e might fail if cctype is an expr, since it might not yet be hashable for use in a dict key...
            # should fix that! (by interning the expr to get its "hash", probably)
        return self.cached_instances[cc_data]
    def _CV_cached_instances(self, index):
        "compute self.cached_instances[cc_data]"
        cctype, bgcolor_data = index
        #e use bgcolor_data to help make the expr
        ccexpr = interpret_cctype(cctype, bgcolor_data) # None or an expr
            #e pkg above back into cc_data for passing in to that helper
##        return self.Instance(ccexpr, index, skip_expr_compare = True) ###IMPLEM skip_expr_compare
##            ###e needs the comparison optim; or, do our own make right here (might be better)
##        ## return ccexpr._e_make_in... - not enough, needs various checks, etc... need to split out some of that from .Instance
##        # and/or get env.make to do it (maybe it does already?) ###
        ipath = index #e or (index, self.ipath)?
        return self.env.make( ccexpr, ipath)
    pass

def kluge_get_glpane_cc_memoizer(glpane): #070414 ###@@@ CALL ME
    "Find or make a central place to store cached CC Instances."
    place = get_glpane_InstanceHolder(glpane)
    return place.Instance(cc_memoizer(), 'kluge_get_glpane_cc_memoizer', skip_expr_compare = True)


###e change that into: InstanceMemoizer subclass with methods to turn args to index, index to expr??
# in fact, best if we could dynamically separate it into an InstanceHolder(glpane)
# and a way for one thing inside that (findable at some index and using state at that index or inside self)
# to be a cc_memoizer. In fact, since cc_memoizer is an IorE, that might be required... ###k FIGURE OUT

# TODO:
#  ###IMPLEM skip_expr_compare - done, untested, maybe not needed here anymore
#  see what env.make does... just eval and _e_make_in; call it like env.make(expr, ipath).
# set up one of the above cc_memoizer objects
# set up its drawing env (with glpane & stateplace), initial ipath, etc -- hmm, is some of that needed in the data? no, to find the obj.

# set up cc_memoizer - needs glpane, so needs to be an attr of some object -- which one? glpane itself??? yes!
# or should glpane have a mixin which gives it this power to own an env and make objects in it?

