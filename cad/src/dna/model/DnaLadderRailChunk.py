# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaLadderRailChunk.py - Chunk subclasses for axis and strand rails of a DnaLadder

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.model.pam_conversion_mmp import DnaLadderRailChunk_writemmp_mapping_memo
from dna.model.pam_conversion_mmp import DnaStrandChunk_writemmp_mapping_memo

from model.chunk import Chunk

from model.elements import Singlet
from model.elements import Pl5

from files.mmp.files_mmp_writing import writemmp_mapping

from utilities.constants import gensym
from utilities.constants import black
from utilities.constants import ave_colors
from utilities.constants import diDEFAULT
from utilities.constants import MODEL_PAM5

from dna.model.dna_model_constants import LADDER_STRAND1_BOND_DIRECTION

from utilities import debug_flags

def _DEBUG_REUSE_CHUNKS():
    return debug_flags.DEBUG_DNA_UPDATER_VERBOSE

import foundation.env as env
from utilities.Log import orangemsg, graymsg

from PyQt4.Qt import QFont, QString # for debug code

from utilities.debug_prefs import debug_pref, Choice_boolean_False

from dna.updater.dna_updater_globals import rail_end_atom_to_ladder

# ==

_FAKENAME = '[fake name, bug if seen]' # should be permitted by Node.__init__ but should not "look correct"

_DEBUG_HIDDEN = False # soon, remove the code for this @@@@

_superclass = Chunk

class DnaLadderRailChunk(Chunk):
    """
    Abstract class for our two concrete Chunk subclasses
    for the axis and strand rails of a DnaLadder.
    """

    # initial values of instance variables:
    
    wholechain = None # will be a WholeChain once dna_updater is done;
        # set by update_PAM_chunks in the updater run that made self,
        # and again in each updater run that made a new wholechain
        # running through self. Can be set to None by Undo.
    
    ladder = None # will be a DnaLadder in finished instances;
        # can be set to None by Undo;
        # can be set to a new value (after self is modified or unmodified)
        # by _f_set_new_ladder.

    _num_old_atoms_hidden = 0
    _num_old_atoms_not_hidden = 0
    
    # review: undo, copy for those attrs? as of 080227 I think that is not needed
    # except for resetting some of them in _undo_update.
    
    # default value of variable used to return info from __init__:

    _please_reuse_this_chunk = None
    
    # == init methods
    
    def __init__(self, assy, name = None, chain = None, reuse_old_chunk_if_possible = False):
        """
        @note: init method signature is compatible with _superclass.__init__,
               since it needs to work in _superclass.copy_empty_shell_in_mapping
               passing just assy and name, expecting us to have no atoms.
        """
        # TODO: check if this arg signature is ok re undo, copy, etc;
        # and if ok for rest of Node API if that matters for this kind of chunk;
        # for now just assume chain is a DnaChain

        # actual name is set below, but only if we don't return early
        _superclass.__init__(self, assy, name or _FAKENAME )

        if chain is not None:
            self._init_atoms_from_chain( chain, reuse_old_chunk_if_possible)
            if self._please_reuse_this_chunk is not None:
                return

        if not name:
            # choose a name -- probably never seen by users, so don't spend
            # lots of runtime or coding time on it -- we use gensym only to
            # make names unique for debugging. (If it did become user-visible,
            # we might want to derive and reuse a common prefix, except that
            # there's no fast way to do that.)
            assy_to_pass_to_gensym = debug_flags.atom_debug and assy or None
            self.name = gensym(self.__class__.__name__.split('.')[-1],
                               assy_to_pass_to_gensym )
                # note 1: passing assy is only useful here if gensym is not yet
                # optimized to not look at node names never seen by user
                # when finding node names to avoid returning. If we do optim
                # it like that, give it an option to pass here to turn that off,
                # but, for speed, maybe only pass it when debugging.
                # note 2: since passing assy might be a bit slow, only do it in the
                # first place when debugging.
                # [bruce 080407 comment]
        return

    def _init_atoms_from_chain( self, chain, reuse_old_chunk_if_possible):
        """
        [private helper for __init__ when a chain is supplied]
        """
        if _DEBUG_HIDDEN:
            self._atoms_were_hidden = []
            self._atoms_were_not_hidden = []
            self._num_extra_bondpoints = 0

        # add atoms before setting self.ladder, so adding them doesn't invalidate it

        use_disp = diDEFAULT # display style to use at end of __init__, if not reset
        use_picked = False # ditto for self.picked

        if reuse_old_chunk_if_possible:
            # Decide whether to abandon self and tell caller to reuse an old
            # chunk instead (by setting self._please_reuse_this_chunk to the
            # old_chunk to reuse, and immediately returning, without adding
            # any atoms to self).
            #
            # (Ideally we'd refactor this to be decided by a helper function,
            #  modified from self._old_chunk_we_could_reuse and its submethods,
            #  and never create self in that case.)
            #
            # Details:
            # before we add our atoms, count the ones we would add (and how
            # many chunks they come from) to see if we can just reuse their
            # single old chunk; this is both an Undo bugfix (since when Undo
            # recreates an old state and might do so again from the same
            # Undo stack, it doesn't like it if we replace objects that
            # are used in that state without counting it as a change which
            # branches off that timeline and destroys the redo stack
            # [theory, not yet proven to cause the bugs being debugged now]),
            # and probably a general optimization (since atoms can change in
            # various ways, many of which make the dna updater run but don't
            # require different DnaLadders -- this will remake ladders and
            # chains anyway but let them share the same chunks) [bruce 080228]
            old_chunk = self._old_chunk_we_could_reuse(chain)
            if old_chunk is not None:
                if _DEBUG_REUSE_CHUNKS():
                    print "dna updater will reuse %r rather than new %r" % \
                          (old_chunk, self) 
                # to do this, set a flag and return early from __init__
                # (we have no atoms; caller must kill us, and call
                #  _f_set_new_ladder on the old chunk it's reusing).
                assert not self.atoms
                self._please_reuse_this_chunk = old_chunk
                
                return
            
            if _DEBUG_REUSE_CHUNKS():
                print "not reusing an old chunk for %r (will grab %d atoms)" % (self, self._counted_atoms)
                print " data: atoms were in these old chunks: %r" % (self._counted_chunks.values(),)

            # Now use the data gathered above to decide how to set some
            # properties in the new chunk. Logically we should do this even if
            # not reuse_old_chunk_if_possible, but the implem would need to
            # differ (even if only by gathering self._counted_chunks some other
            # way), so since that option is never false as of 080303, just do it
            # here.
            #
            # There might be one or more old chunks --
            # see if they all agree about properties, and if so,
            # use those for self; in some cases some per-atom work by _grab_atom
            # (below) might be needed.
            if self._counted_chunks:
                old_chunks = self._counted_chunks.values() # 1 or more
                one_old_chunk = old_chunks.pop() # faster than [0] and [1:]
                # for each property handled here, if all old_chunks same as
                # one_old_chunk, use that value, otherwise a default value.
                # Optimize for a single old chunk or a small number of them
                # (so have only one loop over them).
                other_old_chunks = old_chunks
                
                use_disp = one_old_chunk.display
                use_picked = one_old_chunk.picked
                use_display_as_pam = one_old_chunk.display_as_pam
                use_save_as_pam = one_old_chunk.save_as_pam
                
                for chunk in other_old_chunks:
                    # todo: make a helper method to do this loop over each attr;
                    # make decent error messages by knowing whether use_xxx was reset yet
                    # (use deferred_summary_message)
                    if chunk.display != use_disp:
                        use_disp = diDEFAULT
                            # review:
                            # - do we need atoms with individually set display styles
                            #   to not contribute their chunks to this calc?
                            # - (depending on what later code does)
                            #   do we need to distinguish this being result of
                            #   a conflict (like here) or an agreed value?
                    if not chunk.picked:
                        use_picked = False
                    if chunk.display_as_pam != use_display_as_pam:
                        # should never happen, since DnaLadder merging should be disallowed then
                        # (simplifies mmp read conversion)
                        use_display_as_pam = ""
                    if chunk.save_as_pam != use_save_as_pam:
                        # should never happen, since DnaLadder merging should be disallowed then
                        # (simplifies mmp save conversion)
                        use_save_as_pam = ""
                    continue                
                # review:
                # - what about being (or containing) glpane.selobj?

                # also set self.part. Ideally we ought to always do this,
                # but we only need it when use_picked is true, and we only
                # have a .part handy here, so for now just do it here
                # and assert we did it as needed. [bruce 080314]
                self.inherit_part(one_old_chunk.part)
                pass
            pass

        if use_picked:
            assert self.part is not None # see comment near inherit_part call
            
        self._grab_atoms_from_chain(chain, False) #e we might change when we call this, if we implem copy for this class

        if reuse_old_chunk_if_possible:
            # check that it counted correctly vs the atoms we actually grabbed
            ## assert self._counted_atoms == len(self.atoms), \
            if not (self._counted_atoms == len(self.atoms)):
                print \
                   "\n*** BUG: self._counted_atoms %r != len(self.atoms) %r" % \
                   ( self._counted_atoms, len(self.atoms) )
                # should print the missing atoms if we can, but for now print the present atoms:
                print " present atoms are", self.atoms.values()
        
        self.ladder = rail_end_atom_to_ladder( chain.baseatoms[0] )
        self._set_properties_from_grab_atom_info( use_disp, use_picked,
                                                  use_display_as_pam, use_save_as_pam)
            # uses args and self attrs to set self.display and self.hidden
            # and possibly call self.pick()
        
        return # from _init_atoms_from_chain

    def _f_set_new_ladder(self, ladder):
        """
        We are being reused by a new ladder.
        Make sure the old one is invalid or missing (debug print if not).
        Then properly record the new one.
        """
        if self.ladder and self.ladder.valid:
            print "bug? but working around it: reusing %r but its old ladder %r was valid" % (self, self.ladder)
            self.ladder.ladder_invalidate_and_assert_permitted()
        self.ladder = ladder
        # can't do this, no self.chain; could do it if passed the chain:
        ## assert self.ladder == rail_end_atom_to_ladder( self.chain.baseatoms[0] )
        return

    _counted_chunks = () # kluge, so len is always legal,
        # but adding an element is an error unless it's initialized
    
    def _old_chunk_we_could_reuse(self, chain): #bruce 080228
        """
        [it's only ok to call this during __init__, and early enough,
         i.e. before _grab_atoms_from_chain with justcount == False]
        
        If there is an old chunk we could reuse, find it and return it.
        (If we "just miss", debug print.)
        """
        self._counted_atoms = 0
        self._counted_chunks = {}
        self._grab_atoms_from_chain(chain, True)
        if len(self._counted_chunks) == 1:
            # all our atoms come from the same old chunk (but are they all of its atoms?)
            old_chunk = self._counted_chunks.values()[0]
            assert not old_chunk.killed(), "old_chunk %r should not be killed" % (old_chunk,)
                # sanity check on old_chunk itself
            if self._counted_atoms == len(old_chunk.atoms):
                for atom in old_chunk.atoms.itervalues(): # sanity check on old_chunk itself (also valid outside this if, but too slow)
                    assert atom.molecule is old_chunk # remove when works - slow - or put under SLOW_ASSERTS (otherfile baseatom check too?)
                # caller can reuse old_chunk in place of self, if class is correct
                if self.__class__ is old_chunk.__class__:
                    return old_chunk
                else:
                    # could reuse, except for class -- common in mmp read
                    # or after dna generator, but could happen other times too.
                    if _DEBUG_REUSE_CHUNKS():
                        print "fyi: dna updater could reuse, except for class: %r" % old_chunk
                    # todo: OPTIM: it might be a useful optim, for mmp read, to just change that chunk's class and reuse it.
                    # To decide if this would help, look at cumtime of _grab_atoms_from_chain in a profile.
                    # I think this is only safe if Undo never saw it in a snapshot. This should be true after mmp read,
                    # and maybe when using the Dna Generator, so it'd be useful. I'm not sure how to detect it -- we might
                    # need to add a specialcase flag for Undo to set, or notice a method it already calls. @@@
                    # [bruce 080228]
        return None

    def _grab_atoms_from_chain(self, chain, just_count):
        # if this is slow, see comment at end of _old_chunk_we_could_reuse
        # for a possible optimization [bruce 080228]
        """
        Assume we're empty of atoms;
        pull in all baseatoms from the given DnaChain,
        plus whatever bondpoints or Pl atoms are attached to them
        (but only Pl atoms which are not already in other DnaLadderRailChunks).
        """
        # common code -- just pull in baseatoms and their bondpoints.
        # subclass must extend as needed.
        assert not self._num_old_atoms_hidden #bruce 080227
        assert not self._num_old_atoms_not_hidden #bruce 080227
        for atom in chain.baseatoms:
            self._grab_atom(atom, just_count)
                # note: this immediately kills atom's old chunk if it becomes empty
        return

    def _grab_atom(self, atom, just_count):
        """
        Grab the given atom (and its bondpoints; atom itself must not be a bondpoint)
        to be one of our own, recording info about its old chunk which will be used later
        (in self._set_properties_from_grab_atom_info, called at end of __init__)
        in setting properties of self to imitate those of our atoms' old chunks.

        If just_count is true, don't really grab it, just count up some things
        that will help __init__ decide whether to abandon making self in favor
        of the caller just reusing an old chunk instead of self.
        """
        assert not atom.element is Singlet
        if just_count:
            self._count_atom(atom) # also counts chunks and bondpoints
            return
        # first grab info
        old_chunk = atom.molecule
        # maybe: self._old_chunks[id(old_chunk)] = old_chunk

        # could assert old_chunk is not None or _nullMol
        
        if old_chunk and old_chunk.hidden:
            self._num_old_atoms_hidden += 1
            if _DEBUG_HIDDEN:
                self._atoms_were_hidden.append( (atom, old_chunk) )
        else:
            self._num_old_atoms_not_hidden += 1
            if _DEBUG_HIDDEN:
                self._atoms_were_not_hidden.append( (atom, old_chunk) )

# unused, unfinished, remove soon [080303]:
##        if len(self._counted_chunks) != 1:
##            # (condition is optim; otherwise it's easy)
##            if atom.display == diDEFAULT and old_chunk:
##                # usually true; if this is too slow, just do it from chunks alone
            
        # then grab the atom
        if _DEBUG_HIDDEN:
            have = len(self.atoms)
        atom.hopmol(self)
            # note: hopmol immediately kills old chunk if it becomes empty
        if _DEBUG_HIDDEN:
            extra = len(self.atoms) - (have + 1)
            self._num_extra_bondpoints += extra
        return

    def _count_atom(self, atom): #bruce 080312 revised to fix PAM5 bug
        """
        [private helper for _grab_atom when just_count is true]
        
        count atom and its bondpoints and their chunk
        """
        chunk = atom.molecule
        # no need to check chunk for being None, killed, _nullMol, etc --
        # caller will do that if necessary
        self._counted_chunks[id(chunk)] = chunk

        if 0:
            print "counted atom", atom, "from chunk", chunk

        bondpoints = atom.singNeighbors()

        self._counted_atoms += (1 + len(bondpoints))
        
        if 0 and bondpoints: ### slow & verbose debug code
            print "counted bondpoints", bondpoints
            print "their base atom lists are", [bp.neighbors() for bp in bondpoints]
            for bp in bondpoints:
                assert len(bp.neighbors()) == 1 and bp.neighbors()[0] is atom and bp.molecule is chunk
        return
    
    def _set_properties_from_grab_atom_info(self, use_disp, use_picked,
                                                  use_display_as_pam, use_save_as_pam): # 080201
        """
        If *all* atoms were in hidden chunks, hide self.
        If any or all were hidden, emit an appropriate summary message.
        Set other properties as given.
        """
        if self._num_old_atoms_hidden and not self._num_old_atoms_not_hidden:
            self.hide()
            if debug_flags.DEBUG_DNA_UPDATER:
                summary_format = "DNA updater: debug fyi: remade [N] hidden chunk(s)"
                env.history.deferred_summary_message( graymsg(summary_format) )
        elif self._num_old_atoms_hidden:
            summary_format = "Warning: DNA updater unhid [N] hidden atom(s)"
            env.history.deferred_summary_message( orangemsg(summary_format),
                                                  count = self._num_old_atoms_hidden
                                                 )
            if debug_flags.DEBUG_DNA_UPDATER:
                ## todo: summary_format2 = "Note: it unhid them due to [N] unhidden atom(s)"
                summary_format2 = "Note: DNA updater must unhide some hidden atoms due to [N] unhidden atom(s)"
                env.history.deferred_summary_message( graymsg(summary_format2),
                                                      ## todo: sort_after = summary_format, -- or orangemsg(summary_format)??
                                                      count = self._num_old_atoms_not_hidden
                                                     )
        if self._num_old_atoms_hidden + self._num_old_atoms_not_hidden > len(self.atoms):
            env.history.redmsg("Bug in DNA updater, see console prints")
            print "Bug in DNA updater: _num_old_atoms_hidden %r + self._num_old_atoms_not_hidden %r > len(self.atoms) %r, for %r" % \
                  ( self._num_old_atoms_hidden , self._num_old_atoms_not_hidden, len(self.atoms), self )

        if _DEBUG_HIDDEN:
            mixed = not not (self._atoms_were_hidden and self._atoms_were_not_hidden)
            if not len(self._atoms_were_hidden) + len(self._atoms_were_not_hidden) == len(self.atoms) - self._num_extra_bondpoints:
                print "\n***BUG: " \
                   "hidden %d, unhidden %d, sum %d, not equal to total %d - extrabps %d, in %r" % \
                   ( len(self._atoms_were_hidden) , len(self._atoms_were_not_hidden),
                     len(self._atoms_were_hidden) + len(self._atoms_were_not_hidden),
                     len(self.atoms),
                     self._num_extra_bondpoints,
                     self )
                missing_atoms = dict(self.atoms) # copy here, modify this copy below
                for atom, chunk in self._atoms_were_hidden + self._atoms_were_not_hidden:
                    del missing_atoms[atom.key] # always there? bad bug if not, i think!
                print "\n *** leftover atoms (including %d extra bondpoints): %r" % \
                      (self._num_extra_bondpoints, missing_atoms.values())
            else:
                if not ( mixed == (not not (self._num_old_atoms_hidden and self._num_old_atoms_not_hidden)) ):
                    print "\n*** BUG: mixed = %r but self._num_old_atoms_hidden = %d, len(self.atoms) = %d, in %r" % \
                          ( mixed, self._num_old_atoms_hidden , len(self.atoms), self)
            if mixed:
                print "\n_DEBUG_HIDDEN fyi: hidden atoms = %r \n unhidden atoms = %r" % \
                      ( self._atoms_were_hidden, self._atoms_were_not_hidden )

        # display style
        self.display = use_disp

        # selectedness
        if use_picked:
            assert self.part is not None # caller must guarantee this
                # motivation: avoid trouble in add_part from self.pick
            self.pick()

        if use_display_as_pam:
            self.display_as_pam = use_display_as_pam
        if use_save_as_pam:
            self.save_as_pam = use_save_as_pam
        
        return # from _set_properties_from_grab_atom_info

    # ==
    
    def set_wholechain(self, wholechain):
        """
        [to be called by dna updater]
        @param wholechain: a new WholeChain which owns us (not None)
        """
        assert wholechain is not None
        # note: self.wholechain might or might not be None when this is called
        # (it's None for new chunks, but not for old ones now on new wholechains)
        self.wholechain = wholechain

    # == invalidation-related methods overridden from superclass

    def _undo_update(self):
        if self.wholechain:
            self.wholechain.destroy()
            self.wholechain = None
        self.invalidate_ladder_and_assert_permitted() # review: sufficient? set it to None?
        self.ladder = None #bruce 080227 guess, based on comment where class constant default value is assigned
        for atom in self.atoms.itervalues():
            atom._changed_structure() #bruce 080227 precaution, might be redundant with invalidating the ladder... @@@
        _superclass._undo_update(self)
        return

    def invalidate_ladder(self): #bruce 071203
        # separated some calls into invalidate_ladder_and_assert_permitted, 080413;
        # it turns out nothing still calls this version, but something might in future,
        # so I left it in the API and in class Chunk
        """
        [overrides Chunk method]
        [only legal after init, not during it, thus not in self.addatom --
         that might be obs as of 080120 since i now check for self.ladder... not sure]
        """
        if self.ladder: # cond added 080120
            # possible optim: see comment in invalidate_ladder_and_assert_permitted
            self.ladder.ladder_invalidate_if_not_disabled()
        return

    def invalidate_ladder_and_assert_permitted(self): #bruce 080413
        """
        [overrides Chunk method]
        """
        if self.ladder:
            # possible optim: ' and not self.ladder.valid' above --
            # not added for now so that the debug prints and checks
            # in the following are more useful [bruce 080413]
            self.ladder.ladder_invalidate_and_assert_permitted()
        return

    def in_a_valid_ladder(self): #bruce 071203
        """
        Is this chunk a rail of a valid DnaLadder?
        [overrides Chunk method]
        """
        return self.ladder and self.ladder.valid

    def addatom(self, atom):
        _superclass.addatom(self, atom)
        if self.ladder and self.ladder.valid:
            # this happens for bondpoints (presumably when they're added since
            # we broke a bond); I doubt it happens for anything else,
            # but let's find out (in a very safe way, tho a bit unclear):
            # (update, 080120: I think it would happen in self.merge(other)
            #  except that we're inlined there! So it might happen if an atom
            #  gets deposited on self, too. ### REVIEW)
            # update 080413: I expect it to be an issue for adding bridging Pl
            # during conversion to PAM5, but didn't yet see it happen then. ###
            # when it does, disable the inval, for Pl. (not for bondpoints!)
            # Note the debug print was off for bondpoints, that might be why I didn't see it,
            # if there is a bug that causes one to be added... can't think why there would be tho.
            if atom.element.eltnum != 0:
                print "dna updater, fyi: addatom %r to %r invals_if_not_disabled %r" % (atom, self, self.ladder)
            self.ladder.ladder_invalidate_if_not_disabled()
        return

    def delatom(self, atom):
        _superclass.delatom(self, atom)
        if self.ladder and self.ladder.valid:
            print "dna updater, fyi: delatom %r from %r invals_if_not_disabled %r" % (atom, self, self.ladder)
            self.ladder.ladder_invalidate_if_not_disabled()
        return

    def merge(self, other): # overridden just for debug, 080120 9pm
        """
        [overrides Chunk.merge]
        """
        # note: this will work, but its work will be undone by the next
        # dna updater run, since our new atoms get into
        # _changed_parent_Atoms, which the dna updater is watching
        # for changed_atoms it needs to process. [bruce 080313 comment]
        if debug_flags.DEBUG_DNA_UPDATER:
            print "dna updater debug: fyi: calling %r.merge(%r)" % (self, other)
        return _superclass.merge(self, other)

    def invalidate_atom_lists(self):
        """
        override superclass method, to catch some inlinings of addatom/delatom:
        * in undo_archive
        * in chunk.merge
        * in chunk.copy_full_in_mapping (of the copy -- won't help unless we use self.__class__ to copy) ### REVIEW @@@@
        also catches addatom/delatom themselves (so above overrides are not needed??)
        """
        if self.ladder and self.ladder.valid:
            self.ladder.ladder_invalidate_if_not_disabled() # 080120 10pm bugfix
        return _superclass.invalidate_atom_lists(self)
        
    # == other invalidation-related methods
    
    def forget_wholechain(self, wholechain):
        """
        Remove any references we have to wholechain.
        
        @param wholechain: a WholeChain which refs us and is being destroyed
        """
        assert wholechain is not None
        if self.wholechain is wholechain:
            self.wholechain = None
        return

    # == convenience methods for external use, e.g. access methods

    def get_ladder_rail(self):
        # todo: use more widely (but only when safe!) # revised 080411
        """
        @warning: This is only legitimate to call if you know that self is a
                  chunk which was made by a valid DnaLadder's remake_chunks
                  method and that ladder was not subsequently invalidated.
                  When this is false (i.e. when not self.ladder and self.
                  ladder.valid), it ought to assert 0, but to mitigate
                  bugs in callers, it instead debug prints and does its best,
                  sometimes returning a rail in an invalid ladder and sometimes
                  returning None. It also prints and returns None if the rail
                  can't be found in self.ladder.
        """
        ladder = self.ladder
        if not ladder:
            print "BUG: %r.get_ladder_rail() but self.ladder is None" % self
            return None
        if not ladder.valid:
            print "BUG: %r.get_ladder_rail() but self.ladder %r is not valid" % \
                  (self, ladder)
            # but continue and return the rail if you can find it
        for rail in self.ladder.all_rails():
            if rail.baseatoms[0].molecule is self:
                return rail
        # This might be reached if this is called too early during a dna updater run.
        # Or, this can definitely be reached as of late 080405 by depositing Ss3 on an interior bondpoint
        # of a single strand chain of otherwise-bare Ss3's (making an Ss3 with 3 Ss3 neighbors).
        # guess about the cause: atoms in a DnaLadderRailChunk become erroneous
        # and get left behind in an "invalid" one... looks like its ladder does not even
        # get cleared in that case (though probably it gets marked invalid).
        # Probably we need to do something about those erroneous DnaLadderRailChunks --
        # they might cause all kinds of trouble (e.g. not all their ladder's baseatoms
        # are in them). This might be related to some existing bugs, maybe even undo bugs...
        # so we need to turn them into regular chunks, I think. (Not by class assignment,
        # due to Undo.) [bruce 080405 comment]
        print "BUG: %r.get_ladder_rail() can't find the rail using self.ladder %r" % \
              (self, ladder)
        return None

    def get_baseatoms(self):
        return self.get_ladder_rail().baseatoms

    def idealized_strand_direction(self):
        #bruce 080328; renamed/revised to permit self.error, 080406 (bugfix)
        """
        Return the bond_direction which this strand would have, relative to the
        internal base indices of self.ladder (which must exist) (i.e. to the
        order of self.get_ladder_rail().baseatoms), if it had the correct
        one for this ladder to be finished with no errors, based on which
        strand of self.ladder it is.

        (If self.ladder.valid and not self.ladder.error, then this corresponds
         to the actual strand bond_direction, assuming no bugs.)

        @note: it's not an error to call this if self.ladder.error or not
               self.ladder.valid, but for some kinds of self.ladder.error,
               the return value might not correspond to the *actual* strand
               direction in those cases (or that direction might not even be
               well defined -- not sure that can happen). Some callers depend
               on being allowed to call this under those conditions
               (e.g. writemmp, when writing ladders with errors).
        """
        ladder = self.ladder
        ## assert ladder and not ladder.error and ladder.valid, \
        ##        "%r.ladder = %r not valid and error-free" % \
        ##        (self, ladder)
        assert ladder # no way to avoid requiring this; might be an issue for
            # Ss3 left out of ladders due to atom errors, unless we fix
            # their chunk class or detect this sooner during writemmp (untested)
        rail = self.get_ladder_rail()
        assert rail in ladder.strand_rails
        if rail is ladder.strand_rails[0]:
            direction = LADDER_STRAND1_BOND_DIRECTION
        else:
            direction = - LADDER_STRAND1_BOND_DIRECTION
        return direction
    
    # == graphics methods
    
    def modify_color_for_error(self, color):
        """
        Given the drawing color for this chunk, or None if element colors
        should be used, either return it unchanged, or modify it to
        indicate an error or warning condition (if one exists on this chunk).
        """
        error = self.ladder and self.ladder.error
            # maybe: use self.ladder.drawing_color(), if not None??
        if error:
            # use black, or mix it into the selection color [bruce 080210]
            if self.picked and color is not None:
                # color is presumably the selection color
                color = ave_colors(0.75, black, color)
            else:
                color = black
        return color

    def draw(self, glpane, dispdef):
        """
        [overrides Chunk.draw]
        """
        _superclass.draw(self, glpane, dispdef)
        if not self.__ok():
            return
        if debug_pref("DNA: draw ladder rail atom indices?",
                      Choice_boolean_False,
                      prefs_key = True):
            font = QFont( QString("Helvetica"), 9)
                # WARNING: Anything smaller than 9 pt on Mac OS X results in 
                # un-rendered text.
            out = glpane.out * 3 # bug: 3 is too large
            baseatoms = self.get_baseatoms()
            for atom, i in zip(baseatoms, range(len(baseatoms))):
                baseLetter = atom.getDnaBaseName() # "" for axis
                if baseLetter == 'X':
                    baseLetter = ""
                text = "(%d%s)" % (i, baseLetter)
                pos = atom.posn() + out
                glpane.renderText(pos[0], pos[1], pos[2], \
                          QString(text), font)
                continue
            pass
        return

    def __ok(self): #bruce 080405 [todo: move this method earlier in class]
        # TODO: all uses of get_baseatoms or even self.ladder should test this @@@@@@
        # (review whether get_baseatoms should return [] when this is False)
        # (see also the comments in get_ladder_rail)
        # see also: self._ladder_is_fully_ok()
        ladder = self.ladder
        return ladder and ladder.valid # ok even if ladder.error
    
    # == mmp methods

    def atoms_in_mmp_file_order(self, mapping = None): #bruce 080321
        """
        [overrides Chunk method]

        @note: the objects returned can be of class Atom or
               (if mapping is provided, and permits) class Fake_Pl.
        """
        # basic idea: first write some of the atoms in a definite order,
        # including both real atoms and (if self and mapping options permit)
        # optional "conversion atoms" (fake Pl atomlike objects created just
        # for write operations that convert to PAM5); then write the
        # remaining atoms (all real) in the same order as the superclass
        # would have.
        #
        #update, bruce 080411:
        # We do this even if not mapping.write_bonds_compactly,
        # though AFAIK there is no need to in that case. But I'm not sure.
        # Need to review and figure out if doing it then is needed,
        # and if not, if it's good, and if not, if it's ok.
        # Also I heard of one bug from this, suspect it might be caused
        # by doing it in a chunk with errors, so I will add a check in
        # initial atoms for ladder to exist and be valid (not sure
        # about error-free), and if not, not do this. There was already
        # a check for that about not honoring write_bonds_compactly then
        # (which I split out and called self._ladder_is_fully_ok).

        if mapping is None:
            # We need a real mapping, in order to produce and use a
            # memo object, even though we'll make no conversion atoms,
            # since (if this happens to be a PAM5 chunk) we use the memo
            # to interleave the Pl atoms into the best order for writing
            # (one that permits an upcoming mmp format optimization).
            mapping = writemmp_mapping(self.assy)
        
        initial_atoms = self.indexed_atoms_in_order(mapping = mapping)
            # (implem is per-subclass; should be fast for repeated calls ###CHECK)
            
        # the initial_atoms need to be written in a definite order,
        # and (nim, elsewhere) we might also need to know their mmp encodings
        # for use in info records. (If we do, no need to worry
        # about that here -- just look them up from mapping for the
        # first and last atoms in this order, after writing them.)

        number_of_atoms = len(self.atoms) + \
                          self.number_of_conversion_atoms(mapping)

        if len(initial_atoms) == number_of_atoms:
            # optimization; might often be true for DnaAxisChunk
            # (when no open bonds are present),
            # and for DnaStrandChunk when not doing PAM3 -> PAM5 conversion
            return initial_atoms
        
        all_real_atoms = _superclass.atoms_in_mmp_file_order(self, mapping)
            # preserve this "standard order" for non-initial atoms (all are real).

        assert len(all_real_atoms) == len(self.atoms)
            # maybe not needed; assumes superclass contributes no conversion atoms

##        if len(all_atoms) != number_of_atoms:
##            print "\n*** BUG: wrong number of conversion atoms in %r, %d + %d != %d" % \
##                  (self, len(self.atoms), self.number_of_conversion_atoms(mapping), len(all_atoms))
##            print " more info:"
##            print "self.atoms.values()", self.atoms.values()
##            print "initial_atoms", initial_atoms
##            print "all_atoms", all_atoms
        
        dict1 = {} # helps return each atom exactly once
        some_atom_occurred_twice = False
        for atom in initial_atoms:
            if dict1.has_key(atom.key): #bruce 080516 debug print (to keep)
                print "\n*** BUG: %r occurs twice in %r.indexed_atoms_in_order(%r)" % \
                      ( atom, self, mapping)
                if not some_atom_occurred_twice:
                    print "that entire list is:", initial_atoms
                some_atom_occurred_twice = True
            dict1[atom.key] = atom #e could optim: do directly from list of keys
        if some_atom_occurred_twice: # bruce 080516 bug mitigation
            print "workaround: remove duplicate atoms (may not work;"
            print " underlying bug needs fixing even if it works)"
            newlist = []
            dict1 = {}
            for atom in initial_atoms:
                if not dict1.has_key(atom.key):
                    dict1[atom.key] = atom
                    newlist.append(atom)
                continue
            print "changed length from %d to %d" % (len(initial_atoms), len(newlist))
            print
            initial_atoms = newlist
            pass
        res = list(initial_atoms) # extended below
        for atom in all_real_atoms: # in this order
            if not dict1.has_key(atom.key):
                res.append(atom)
        ## assert len(res) == number_of_atoms, \
            # can fail for ladder.error or atom errors, don't yet know why [080406 1238p];
            # also failed for Ninad reproducing Eric D bug (which I could not reproduce)
            # in saving 8x21RingB1.mmp after joining the last strand into a ring (I guess);
            # so I'll make it a debug print only [bruce 080516]
        if not ( len(res) == number_of_atoms ):
            print "\n*** BUG in atoms_in_mmp_file_order for %r: " % self, \
               "len(res) %r != number_of_atoms %r" % \
               (len(res), number_of_atoms) 
        return res

    def indexed_atoms_in_order(self, mapping): #bruce 080321
        """
        [abstract method of DnaLadderRailChunk]

        Return the atoms of self which need to be written in order
        of base index or interleaved between those atoms.
        This may or may not include all writable atoms of self,
        which consist of self.atoms plus possible "conversion atoms"
        (extra atoms due to pam conversion, written but not placed
        into self.atoms).
        """
        assert 0, "subclass must implement"

    def write_bonds_compactly_for_these_atoms(self, mapping): #bruce 080328
        """
        [overrides superclass method]
        """
        if not mapping.write_bonds_compactly:
            return {}
        if not self._ladder_is_fully_ok():
            # self.idealized_strand_direction might differ from actual
            # bond directions, so we can't abbreviate them this way
            return {} 
        atoms = self.indexed_atoms_in_order(mapping)
        return dict([(atom.key, atom) for atom in atoms])

    def _ladder_is_fully_ok(self): #bruce 080411 split this out; it might be redundant with other methods
        # see also: self.__ok()
        ladder = self.ladder
        return ladder and ladder.valid and not ladder.error
    
    def write_bonds_compactly(self, mapping): #bruce 080328
        """
        [overrides superclass method]
        """
        # write the new bond_chain and/or directional_bond_chain records --
        # subclass must decide which one.
        assert 0, "subclass must implement"

    def _compute_atom_range_for_write_bonds_compactly(self, mapping): #bruce 080328
        """
        [private helper for subclass write_bonds_compactly methods]
        """
        atoms = self.indexed_atoms_in_order(mapping)
        assert atoms
        if debug_flags.DNA_UPDATER_SLOW_ASSERTS:
            # warning: not well tested, since this flag was turned off
            # by default 080702, but write_bonds_compactly is not yet
            # used by default as of then.
            codes = [mapping.encode_atom_written(atom) for atom in atoms]
            for i in range(len(codes)):
                # it might be an int or a string version of an int
                assert int(codes[i]) > 0
                if i:
                    assert int(codes[i]) == 1 + int(codes[i-1])
                continue
            pass
        res = mapping.encode_atom_written(atoms[0]), \
              mapping.encode_atom_written(atoms[-1]) # ok if same atom, can happen
        # print "fyi, compact bond atom range for %r is %r" % (self, res)
        return res

    def _f_compute_baseatom_range(self, mapping): #bruce 080328
        """
        [friend method for mapping.get_memo_for(self.ladder),
         an object of class DnaLadder_writemmp_mapping_memo]
        """
        atoms = self.get_baseatoms()
        res = mapping.encode_atom_written(atoms[0]), \
              mapping.encode_atom_written(atoms[-1]) # ok if same atom, can happen
        return res
    
    def number_of_conversion_atoms(self, mapping): #bruce 080321
        """
        [abstract method of DnaLadderRailChunk]

        How many atoms are written to a file, when controlled by mapping,
        which are not in self.atoms? (Note: self.atoms may or may not
        contain more atoms than self.baseatoms. Being a conversion atom
        and being not in self.baseatoms are independent properties.)
        """
        assert 0, "subclass must implement"

    _class_for_writemmp_mapping_memo = DnaLadderRailChunk_writemmp_mapping_memo
        # subclass can override if needed (presumably with a subclass of this value)

    def _f_make_writemmp_mapping_memo(self, mapping):
        """
        [friend method for class writemmp_mapping.get_memo_for(self)]
        """
        # note: same code in some other classes that implement this method
        return self._class_for_writemmp_mapping_memo(mapping, self)
    
    def save_as_what_PAM_model(self, mapping): #bruce 080326
        """
        Return None or an element of PAM_MODELS
        which specifies into what PAM model, if any,
        self should be converted, when saving it
        as controlled by mapping.

        @param mapping: an instance of writemmp_mapping controlling the save.
        """
        assert mapping
        def doit():
            res = self._f_requested_pam_model_for_save(mapping)
            
            if not res:
                # optimize a simple case (though not the usual case);
                # only correct since self.ladder will return None
                # for its analogous decision if any of its chunks do.
                return None
            
            # memoize the rest in mapping, not for speed but to
            # prevent repeated error messages for same self and mapping
            # (and to enforce constant behavior as bug precaution)

            memo = mapping.get_memo_for(self)

            return memo._f_save_as_what_PAM_model()
        res = doit()
##        print "save_as_what_PAM_model(%r,...) -> %r" % (self, res)
        return res
    
    def _f_requested_pam_model_for_save(self, mapping):
        """
        Return whatever the mapping and self options are asking for
        (without checking whether it's doable).
        For no conversion, return None. For conversion to a PAM model,
        return an element of PAM_MODELS.
        """
##        print " mapping.options are", mapping.options
##        print " also self.save_as_pam is", self.save_as_pam
        if mapping.honor_save_as_pam:
            res = self.save_as_pam or mapping.convert_to_pam
        else:
            res = mapping.convert_to_pam
        if not res:
            res = None
        return res
        
    pass # end of class DnaLadderRailChunk

# ==

def _make_or_reuse_DnaLadderRailChunk(constructor, assy, chain, ladder):
    """
    """
    name = ""
    new_chunk = constructor(assy, name, chain, reuse_old_chunk_if_possible = True)
    res = new_chunk # tentative
    if new_chunk._please_reuse_this_chunk:
        res = new_chunk._please_reuse_this_chunk # it's an old chunk
        assert not new_chunk.atoms
        new_chunk.kill() # it has no atoms, but can't safely do this itself
            # review: is this needed, and safe? maybe it's not in the model yet?
        res._f_set_new_ladder(ladder)
    return res

# == these subclasses might be moved to separate files, if they get long

class DnaAxisChunk(DnaLadderRailChunk):
    """
    Chunk for holding part of a Dna Segment Axis (the part in a single DnaLadder).

    Internal model object; same comments as in DnaStrandChunk docstring apply.
    """
    def isAxisChunk(self):
        """
        [overrides Chunk method]
        """
        return True
    
    def isStrandChunk(self):
        """
        [overrides Chunk method]
        """
        return False

    def indexed_atoms_in_order(self, mapping): #bruce 080321
        """
        [implements abstract method of DnaLadderRailChunk]
        """
        del mapping
        if not self._ladder_is_fully_ok():
            # in this case, it's even possible get_baseatoms will fail
            # (if we are a leftover DnaLadderRailChunk full of error atoms
            #  rejected when making new ladders, and have no .ladder ourselves
            #  (not sure this is truly possible, needs review))
            # [bruce 080411 added this check]
            return []
        return self.get_baseatoms()
    
    def number_of_conversion_atoms(self, mapping): #bruce 080321
        """
        [implements abstract method of DnaLadderRailChunk]
        """
        del mapping
        return 0
        
    def write_bonds_compactly(self, mapping): #bruce 080328
        """
        [overrides superclass method]
        """
        # LOGIC BUG (fixable without revising mmp reading code):
        # we may have excluded more bonds from Atom.writemmp
        # than we ultimately write here, if the end atoms of
        # our rail are bonded together, or if there are other (illegal)
        # bonds between atoms in it besides the along-rail bonds.
        # (Applies to both axis and strand implems.)
        # To fix, just look for those bonds and write them directly,
        # or, be more specific about which bonds to exclude
        # (e.g. pass a set of atom pairs; maybe harder when fake_Pls are involved).
        # Not urgent, since rare and doesn't affect mmp reading code or mmpformat version.
        # I don't think the same issue affects the dna_rung_bonds record, but review.
        # [bruce 080328]
        
        # write the new bond_chain record
        code_start, code_end = \
            self._compute_atom_range_for_write_bonds_compactly(mapping)
        record = "bond_chain %s %s\n" % (code_start, code_end)
        mapping.write(record)
        # write compact rung bonds to previously-written strand chunks
        ladder_memo = mapping.get_memo_for(self.ladder) 
        for chunk in ladder_memo.wrote_strand_chunks:
            ladder_memo.write_rung_bonds(chunk, self)
        # make sure not-yet-written strand chunks can do the same with us
        ladder_memo.advise_wrote_axis_chunk(self)
        return

    pass

def make_or_reuse_DnaAxisChunk(assy, chain, ladder):
    """
    """
    return _make_or_reuse_DnaLadderRailChunk( DnaAxisChunk, assy, chain, ladder)

# ==

class DnaStrandChunk(DnaLadderRailChunk):
    """
    Chunk for holding part of a Dna Strand (the part in a single DnaLadder).

    Internal model object -- won't be directly user-visible (for MT, selection, etc)
    when dna updater is complete. But it's a normal member of the internal model tree for
    purposes of copy, undo, mmp file, internal selection, draw.
    (Whether copy implem makes another chunk of this class, or relies on dna
    updater to make one, is not yet decided. Likewise, whether self.draw is
    normally called is not yet decided.)
    """
    _class_for_writemmp_mapping_memo = DnaStrandChunk_writemmp_mapping_memo
    # overrides superclass version (with a subclass of it)

    def isAxisChunk(self):
        """
        [overrides Chunk method]
        """
        return False
    
    def isStrandChunk(self):
        """
        [overrides Chunk method]
        """
        return True
    
    def _grab_atoms_from_chain(self, chain, just_count): # misnamed, doesn't take them out of chain
        """
        [extends superclass version]
        """
        DnaLadderRailChunk._grab_atoms_from_chain(self, chain, just_count)
        for atom in chain.baseatoms:
            # pull in Pls too (if they prefer this Ss to their other one)
            # and also directly bonded unpaired base atoms (which should
            # never be bonded to more than one Ss)
            ### review: can't these atoms be in an older chunk of the same class
            # from a prior step?? I think yes... so always pull them in,
            # regardless of class of their current chunk.
            for atom2 in atom.neighbors():
                grab_atom2 = False # might be changed to True below
                is_Pl = atom2.element is Pl5
                if is_Pl:
                    # does it prefer to stick with atom (over its other Ss neighbors, if any)?
                    # (note: usually it sticks based on bond direction, but if
                    #  it has only one real neighbor it always sticks to that
                    #  one.)
                    if atom is atom2.Pl_preferred_Ss_neighbor(): # an Ss or None
                        grab_atom2 = True
                elif atom2.element.role in ('unpaired-base', 'handle'):
                    grab_atom2 = True
                if grab_atom2:
                    if atom2.molecule is self:
                        assert not just_count # since that implies no atoms yet in self
                        print "\n***BUG: dna updater: %r is already in %r" % \
                              (atom2, self)
                        # since self is new, just now being made,
                        # and since we think only one Ss can want to pull in atom2
                    else:
                        ## atom2.hopmol(self)
                        self._grab_atom(atom2, just_count)
                            # review: does this harm the chunk losing it if it too is new? @@@
                            # (guess: yes; since we overrode delatom to panic... not sure about Pl etc)
                            # academic for now, since it can't be new, afaik
                            # (unless some unpaired-base atom is bonded to two Ss atoms,
                            #  which we ought to prevent in the earlier bond-checker @@@@ NIM)
                            # (or except for inconsistent bond directions, ditto)
                        pass
                    pass
                continue
            continue
        return # from _grab_atoms_from_chain

    def indexed_atoms_in_order(self, mapping): #bruce 080321
        """
        [implements abstract method of DnaLadderRailChunk]
        """
        if not self._ladder_is_fully_ok():
            # in this case, it's even possible get_baseatoms will fail
            # (if we are a leftover DnaLadderRailChunk full of error atoms
            #  rejected when making new ladders, and have no .ladder ourselves
            #  (not sure this is truly possible, needs review))
            # [bruce 080411 added this check]
            return []
        # TODO: optimization: also include bondpoints at the end.
        # This can be done later without altering mmp reading code.
        # It's not urgent.
        # TODO: optimization: cache this in mapping.get_memo_for(self).
        baseatoms = self.get_baseatoms()
        # for PAM3+5:
        # now interleave between these (or before/after for end Pl atom)
        # the real and/or converted Pl atoms.
        # (Always do this, even if no conversion is active,
        #  so that real Pl atoms get into this list.)
        # (note: we cache the conversion atoms so they have constant keys;
        #  TODO: worry about undo of those atoms, etc;
        #  we cache them on their preferred Ss neighbor atoms)
        Pl_atoms = self._Pl_atoms_to_interleave(mapping)
            # len(baseatoms) + 1 atoms, can be None at the ends,
            # or in the middle when not converting to PAM5
            # (or can be None to indicate no Pl atoms -- rare)
        if Pl_atoms is None:
            return baseatoms
        assert len(Pl_atoms) == len(baseatoms) + 1
        def interleave(seq1, seq2):
            #e refile (py seq util)
            assert len(seq1) >= len(seq2)
            for i in range(len(seq1)):
                yield seq1[i]
                if i < len(seq2):
                    yield seq2[i]
                continue
            return            
        interleaved = interleave(Pl_atoms, baseatoms)
        return [atom for atom in interleaved if atom is not None]
    
    def number_of_conversion_atoms(self, mapping): #bruce 080321
        """
        [implements abstract method of DnaLadderRailChunk]
        """
        if self.save_as_what_PAM_model(mapping) != MODEL_PAM5:
            # optimization (conversion atoms are not needed
            # except when converting to PAM5).
            return 0

        assert mapping # otherwise, save_as_what_PAM_model should return None

        ### REVIEW: if not self._ladder_is_fully_ok(), should we return 0 here
        # and refuse to convert in other places? [bruce 080411 Q]
        
        # Our conversion atoms are whatever Pl atoms we are going to write
        # which are not in self.atoms (internally they are Fake_Pl objects).
        # For efficiency and simplicity we'll cache the answer in our chunk memo.
        memo = mapping.get_memo_for(self)
        return memo._f_number_of_conversion_atoms()

    def _Pl_atoms_to_interleave(self, mapping):
        """
        [private helper for mmp write methods]
        
        Assuming (not checked) that this chunk should be saved in PAM5
        (and allowing it to presently be in either PAM3 or PAM3+5 or PAM5),
        return a list of Pl atoms to interleave before/between/after our
        baseatoms. (Not necessarily in the right positions in 3d space,
         or properly bonded to our baseatoms, or atoms actually in self.atoms.)

        Length is always 1 more than len(baseatoms).
        First and last entries might be None if those Pl atoms should belong
        to different chunks or should not exist. Middle entries might be None
        if we're not converting to PAM5 and no real Pl atoms are present there,
        or if we're converting to PAM3 (maybe nim).

        The Pl atoms returned exist as Atom or Fake_Pl objects, but might be in self,
        or killed(??), or perhaps some of each. Don't alter this.

        It's ok to memoize data in mapping (index by self, private to self
        and/or self.ladder) which depends on our current state and can be
        used when writing every chunk in self.ladder.
        """
        # note: we must proceed even if not converting to PAM5 here,
        # since we interleave even real Pl atoms.
        assert mapping # needed for the memo... too hard to let it be None here
        memo = mapping.get_memo_for(self)
        return memo.Pl_atoms
        
    def write_bonds_compactly(self, mapping): #bruce 080328
        """
        Note: this also writes all dnaBaseName (sequence) info for our atoms.
        
        [overrides superclass method]
        """
        # write the new directional_bond_chain record
        code_start, code_end = \
            self._compute_atom_range_for_write_bonds_compactly(mapping)
            # todo: override that to assert the bond directions are as expected?
        bond_direction = self.idealized_strand_direction()
        sequence = self._short_sequence_string() # might be ""
        if sequence:
            record = "directional_bond_chain %s %s %d %s\n" % \
                     (code_start, code_end, bond_direction, sequence)
        else:
            # avoid trailing space, though our own parser wouldn't care about it
            record = "directional_bond_chain %s %s %d\n" % \
                     (code_start, code_end, bond_direction)
        mapping.write(record)
        # write compact rung bonds to previously-written axis chunk, if any
        ladder_memo = mapping.get_memo_for(self.ladder) 
        for chunk in ladder_memo.wrote_axis_chunks:
            ladder_memo.write_rung_bonds(chunk, self)
        # make sure not-yet-written axis chunk (if any) can do the same with us
        ladder_memo.advise_wrote_strand_chunk(self)
        return

    def _short_sequence_string(self):
        """
        [private helper for write_bonds_compactly]

        Return the dnaBaseNames (letters) of our base atoms,
        as a single string,
        in the same order as they appear in indexed_atoms_in_order,
        leaving off trailing X's.
        (If all sequence is unassigned == 'X', return "".)
        """
        baseatoms = self.get_baseatoms()
        n = len(baseatoms)
        while n and not baseatoms[n-1]._dnaBaseName:
            # KLUGE, optimization: access private attr ### TODO: make it a friend attr
            # (this inlines atom.getDnaBaseName() != 'X')
            n -= 1
        if not n:
            return "" # common optimization
        return "".join([atom.getDnaBaseName() for atom in baseatoms[:n]])
    
    pass # end of class DnaStrandChunk

def make_or_reuse_DnaStrandChunk(assy, chain, ladder):
    """
    """
    return _make_or_reuse_DnaLadderRailChunk(DnaStrandChunk, assy, chain, ladder)

# end
