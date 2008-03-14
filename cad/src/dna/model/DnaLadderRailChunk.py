# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaLadderRailChunk.py - 

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from model.chunk import Chunk

from model.elements import Singlet
from model.elements import Pl5

from utilities.constants import gensym
from utilities.constants import black
from utilities.constants import ave_colors
from utilities.constants import diDEFAULT

from utilities import debug_flags

def _DEBUG_REUSE_CHUNKS():
    return debug_flags.DEBUG_DNA_UPDATER_VERBOSE

import foundation.env as env
from utilities.Log import orangemsg, graymsg

from PyQt4.Qt import QFont, QString # for debug code

from utilities.debug_prefs import debug_pref, Choice_boolean_False

# see also:
## from dna_model.DnaLadder import _rail_end_atom_to_ladder
# (below, perhaps in a cycle)

# ==

_FAKENAME = '[fake name, bug if seen]' # should be permitted by Node.__init__ but should not "look correct"

_DEBUG_HIDDEN = False # soon, remove the code for this @@@@

_superclass = Chunk

class DnaLadderRailChunk(Chunk):
    """
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
    
    def __init__(self, assy, chain, reuse_old_chunk_if_possible = False):

        if _DEBUG_HIDDEN:
            self._atoms_were_hidden = []
            self._atoms_were_not_hidden = []
            self._num_extra_bondpoints = 0

        # TODO: check if this arg signature is ok re undo, copy, etc;
        # and if ok for rest of Node API if that matters for this kind of chunk;
        # for now just assume chain is a DnaChain

        # actual name is set below, only if we don't return early
        _superclass.__init__(self, assy, _FAKENAME )
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
                
                for chunk in other_old_chunks:
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
                    continue                
                # review:
                # - what about being (or containing) glpane.selobj?
            pass

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
        
        # following import is a KLUGE to avoid recursive import
        # (still has import cycle, ought to ### FIX -- should refile that func somehow)
        from dna.model.DnaLadder import _rail_end_atom_to_ladder
            # todo: make not private... or get by without it here (another init arg??)
            # review: make this import toplevel? right now it's probably in a cycle.
        self.ladder = _rail_end_atom_to_ladder( chain.baseatoms[0] )
        self._set_properties_from_grab_atom_info( use_disp, use_picked)
            # uses args and self attrs to set self.display and self.hidden
            # and possibly call self.pick()

        # name -- probably never seen by users, so don't spend lots of runtime
        # or coding time on it -- we use gensym only to make names unique
        # for debugging. (If it did become user-visible, we might want to derive
        # and reuse a common prefix, except that there's no fast way to do that.)
        self.name = gensym(self.__class__.__name__.split('.')[-1]) ## + ' (internal)'
        
        return # from __init__

    def _f_set_new_ladder(self, ladder):
        """
        We are being reused by a new ladder.
        Make sure the old one is invalid or missing (debug print if not).
        Then properly record the new one.
        """
        if self.ladder and self.ladder.valid:
            print "bug? but working around it: reusing %r but its old ladder %r was valid" % (self, self.ladder)
            self.ladder.invalidate()
        self.ladder = ladder
        # can't do this, no self.chain; could do it if passed the chain:
        ## from dna_model.DnaLadder import _rail_end_atom_to_ladder
        ## assert self.ladder == _rail_end_atom_to_ladder( self.chain.baseatoms[0] )
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
            assert not old_chunk.killed() # sanity check on old_chunk itself
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
    
    def _set_properties_from_grab_atom_info(self, use_disp, use_picked): # 080201
        """
        If *all* atoms were in hidden chunks, hide self.
        If any or all were hidden, emit an appropriate summary message.
        Set display style to a common old one or a new one.
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
            self.pick()
        
        return # from _set_properties_from_grab_atom_info
        
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
        self.invalidate_ladder() # review: sufficient? set it to None?
        self.ladder = None #bruce 080227 guess, based on comment where class constant default value is assigned
        for atom in self.atoms.itervalues():
            atom._changed_structure() #bruce 080227 precaution, might be redundant with invalidating the ladder... @@@
        _superclass._undo_update(self)
        return

    def invalidate_ladder(self): #bruce 071203
        """
        [overrides Chunk method]
        [only legal after init, not during it, thus not in self.addatom --
         that might be obs as of 080120 since i now check for self.ladder... not sure]
        """
        if self.ladder: # cond added 080120
            self.ladder.invalidate()
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
            if atom.element.eltnum != 0:
                print "dna updater, fyi: %r.addatom %r invals %r" % (self, atom, self.ladder)
            self.ladder.invalidate()
        return

    def delatom(self, atom):
        _superclass.delatom(self, atom)
        if self.ladder and self.ladder.valid:
            self.ladder.invalidate()
        return

    def merge(self, other): # overridden just for debug, 080120 9pm
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
            self.ladder.invalidate() # 080120 10pm bugfix
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

    # == other methods
    
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

    def get_ladder_rail(self): # todo: use more widely
        """
        """
        for rail in self.ladder.all_rails():
            if rail.baseatoms[0].molecule is self:
                return rail
        assert 0 # might happen if used during dna updater run
                
    def draw(self, glpane, dispdef):
        """
        [overrides Chunk.draw]
        """
        _superclass.draw(self, glpane, dispdef)
        if debug_pref("DNA: draw ladder rail atom indices?",
                      Choice_boolean_False,
                      prefs_key = True):
            font = QFont( QString("Helvetica"), 9)
                # WARNING: Anything smaller than 9 pt on Mac OS X results in 
                # un-rendered text.
            out = glpane.out * 3 # bug: 3 is too large
            rail = self.get_ladder_rail()
            baseatoms = rail.baseatoms
            for atom, i in zip(baseatoms, range(len(baseatoms))):
                text = "(%d)" % i # smaller when works
                pos = atom.posn() + out
                glpane.renderText(pos[0], pos[1], pos[2], \
                          QString(text), font)
                continue
            pass
        return
    
    pass # end of class DnaLadderRailChunk

# ==

def _make_or_reuse_DnaLadderRailChunk(constructor, assy, chain, ladder):
    """
    """
    new_chunk = constructor(assy, chain, reuse_old_chunk_if_possible = True)
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
        This should always return True. It directly returns True ... bypassing
        the things done in Chunk class ... thereby making this a little faster.
        @see: Chunk.isAxisChunk() , overridden here.  
        """
        return True
    
    def isStrandChunk(self):
        """
        This should always return False. It directly returns False ... bypassing
        the things done in Chunk class ... thereby making this a little faster.
        @see: Chunk.isStrandChunk() , overridden here.  
        """
        return False
    
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
    def isAxisChunk(self):
        """
        This should always return False. It directly returns False ... bypassing
        the things done in Chunk class ... thereby making this a little faster. 
        
        @see: Chunk.isAxisChunk() overridden here.          
        @see: DnaAxisChunk.isAxisChunk()
        """
        return False
    
    def isStrandChunk(self):
        """
        This should always return True. It directly returns True ... bypassing
        the things done in Chunk class ... thereby making this a little faster. 
        @see: Chunk.isStrandChunk() , overridden here.         
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
                elif atom2.element.role == 'unpaired-base':
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
    pass # end of class DnaStrandChunk

def make_or_reuse_DnaStrandChunk(assy, chain, ladder):
    """
    """
    return _make_or_reuse_DnaLadderRailChunk(DnaStrandChunk, assy, chain, ladder)

# end
