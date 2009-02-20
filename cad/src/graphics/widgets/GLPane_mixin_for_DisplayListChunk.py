# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
GLPane_mixin_for_DisplayListChunk.py

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

bruce 080910 split this out of class GLPane
"""

from OpenGL.GL import glGenLists
from OpenGL.GL import glNewList
from OpenGL.GL import glEndList
from OpenGL.GL import glCallList

from utilities.debug_prefs import debug_pref
from utilities.debug_prefs import Choice_boolean_False

from foundation.state_utils import transclose

class GLPane_mixin_for_DisplayListChunk(object):
    #bruce 070110 moved this here from exprs/DisplayListChunk.py and made GLPane inherit it
    #bruce 080215 renamed this
    #bruce 080910 moved this into its own file
    """
    Private mixin class for GLPane. Attr and method names must not interfere with GLPane.
    Likely to be merged into class GLPane in future (as directly included methods rather than a mixin superclass).
    """
    compiling_displist = 0 #e rename to be private? probably not.
    compiling_displist_owned_by = None
    def glGenLists(self, *args):
        return glGenLists(*args)
    def glNewList(self, listname, mode, owner = None):
        """
        Execute glNewList, after verifying args are ok and we don't think we're compiling a display list now.
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
        self.compiling_displist_owned_by = owner # optional arg in general, but required for the tracking done in this module
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
        """
        Compile a call to the given display list.
        Note: most error checking and any extra tracking is responsibility of caller.
        """
        ##e in future, could merge successive calls into one call of multiple lists
        ## assert not self.compiling_displist # redundant with OpenGL only if we have no bugs in maintaining it, so worth checking
            # above was WRONG -- what was I thinking? This is permitted, and we'll need it whenever one displist can call another.
            # (And I'm surprised I didn't encounter it before -- did I still never try an MT with displists?)
            # (Did I mean to put this into some other method? or into only certain uses of this method??
            # For now, do an info print, in case sometimes this does indicate an error, and since it's useful
            # for analyzing whether nested displists are behaving as expected. [bruce 070203]
        if self.compiling_displist and \
           debug_pref("GLPane: print nested displist compiles?",
                      Choice_boolean_False,
                      prefs_key = True):
            print "debug: fyi: displist %r is compiling a call to displist %r" % \
                  (self.compiling_displist, listname)
        assert listname # redundant with following?
        glCallList(listname)
        return
    def ensure_dlist_ready_to_call( self, dlist_owner_1 ): #e rename the local vars, revise term "owner" in it [070102 cmt]
        """
        [private helper method for use by DisplayListChunk]
           This implements the recursive algorithm described in DisplayListChunk.__doc__.
        dlist_owner_1 should be a DisplistOwner ###term; we use private attrs and/or methods of that class,
        including _key, _recompile_if_needed_and_return_sublists_dict().
           What we do: make sure that dlist_owner_1's display list can be safely called (executed) right after we return,
        with all displists that will call (directly or indirectly) up to date (in their content).
           Note that, in general, we won't know which displists will be called by a given one
        until after we've updated its content (and thereby compiled calls to those displists as part of its content).
           Assume we are only called when our GL context is current and we're not presently compiling a displist in it.
        """
        ###e verify our GL context is current, or make it so; not needed now since only called during some widget's draw call
        assert self.compiling_displist == 0
        toscan = { dlist_owner_1._key : dlist_owner_1 }
        def collector( obj1, dict1):
            dlist_owner = obj1
            direct_sublists_dict = dlist_owner._recompile_if_needed_and_return_sublists_dict() # [renamed from _ensure_self_updated]
                # This says to dlist_owner: if your list is invalid, recompile it (and set your flag saying it's valid);
                # then you know your direct sublists, so we can ask you to return them.
                #   Note: it only has to include sublists whose drawing effects might be invalid.
                # This means, if its own effects are valid, it can optim by just returning {}.
                # [#e Someday it might maintain a dict of invalid sublists and return that. Right now it returns none or all of them.]
                #   Note: during that call, the glpane (self) is modified to know which dlist_owner's list is being compiled.
            dict1.update( direct_sublists_dict )
        seen = transclose(  toscan, collector )
        # now, for each dlist_owner we saw, tell it its drawing effects are valid.
        for dlist_owner in seen.itervalues():
            dlist_owner._your_drawing_effects_are_valid()
                # Q: this resets flags which cause inval propogation... does it retain consistency?
                # A: it does it in reverse logic dir and reverse arrow dir (due to transclose) as inval prop, so it's ok.
                # Note: that comment won't be understandable in a month [from 070102]. Need to explain it better. ###doc
        return
    pass # end of class GLPane_mixin_for_DisplayListChunk

# end
