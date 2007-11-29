# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_chunks.py - enforce rules on chunks containing changed PAM atoms

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_updater_globals import get_changes_and_clear
from dna_updater_globals import ignore_new_changes

from dna_updater_utils import remove_killed_atoms

##from constants import noop as STUB_FUNCTION # FIX all uses

from dna_updater_constants import DEBUG_DNA_UPDATER

from bond_chains import abstract_bond_chain_analyzer

from dna_model.AtomChainOrRing import AtomChain, AtomRing
from dna_model.AtomChainOrRing import AtomChainOrRing # for isinstance

from dna_model.DnaChain import AxisChain, StrandChain
from dna_model.DnaChain import DnaChain # for isinstance

from dna_model.DnaAtomMarker import _f_get_homeless_dna_markers

# ==

# helper classes (will probably turn out to be private, or perhaps
#  even local to find_axis_and_strand_chains_or_rings)

class dna_bond_chain_analyzer(abstract_bond_chain_analyzer):
    """
    [private abstract helper class]
    For DNA, we like our found atom/bond chains or rings to be instances
    of one of AtomChainOrRing's subclasses, AtomChain or AtomRing.
    """
    _wrapper = None # a per-subclass constant, to wrap an AtomChainOrRing
    def make_chain(self, listb, lista):
        # also used for lone atoms
        return self._wrap(AtomChain(listb, lista))
    def make_ring(self, listb, lista):
        return self._wrap(AtomRing(listb, lista))
    def _wrap(self, chain_or_ring):
        if chain_or_ring is None:
            return None
        res = self._wrapper(chain_or_ring)
        # check effect of wrapper:
        assert isinstance( res, DnaChain) #e remove when works?
        return res
    def found_object_iteratoms(self, chain_or_ring):
        if chain_or_ring is None:
            return ()
        # check effect of wrapper:
        assert isinstance( chain_or_ring, DnaChain) #e remove when works?
        return chain_or_ring.iteratoms()
    pass
    
class axis_bond_chain_analyzer(dna_bond_chain_analyzer):
    _wrapper = AxisChain
    def atom_ok(self, atom):
        return atom.element.role == 'axis'
    pass

class strand_bond_chain_analyzer(dna_bond_chain_analyzer):
    _wrapper = StrandChain
    def atom_ok(self, atom):
        # note: can include Pl atoms in PAM5
        return atom.element.role == 'strand'
    pass

# singleton objects
# (todo: could be local to the main using function,
#  if they returned instances so axis_analyzer.found_object_iteratoms etc
#  was not needed by other functions here; now they do, so REVIEW whether they can be local ###)

axis_analyzer = axis_bond_chain_analyzer()

strand_analyzer = strand_bond_chain_analyzer()

# ==

def update_PAM_chunks( changed_atoms):
    """
    Update chunks containing changed PAM atoms, ensuring that
    PAM atoms remain divided into AxisChunks and StrandSegmentChunks
    in the right way.

    @param changed_atoms: an atom.key -> atom dict of all changed atoms
                          that this update function needs to consider,
                          which includes no killed atoms. WE ASSUME
                          OWNERSHIP OF THIS DICT and modify it in
                          arbitrary ways.
                          Note: in present calling code [071127]
                          this dict might include atoms from closed files.

    @return: None (??)
    """

    # see scratch file for comments to revise and bring back here...

    ignore_new_changes("as update_PAM_chunks starts", changes_ok = False )


    # Find the current axis and strand chains on which any changed atoms reside.
    
    axis_chains, strand_chains = find_axis_and_strand_chains_or_rings( changed_atoms)

    ignore_new_changes("from find_axis_and_strand_chains_or_rings", changes_ok = False )


    # Move the chain markers whose atoms got killed, onto atoms which remain alive
    # but were in the same old chains. (Their old chain objects still exist, in
    # the markers, to help the markers decide where and how to move.)

    # To help the moving markers know how to advise their new chains about
    # internal baseindex direction coming from their old chains, we first
    # make a dict from atom.key to (new chain id, atom's baseindex in new chain).
    # (We might use it later as well, not sure.)
    # (We keep axis and strand info in one dict for convenience, since both kinds
    #  of markers are in one list we iterate over.)
    
    new_chain_info = {} 

    for chain in axis_chains + strand_chains:
        for atom, index in chain.baseatom_index_pairs(): # skips non-base atoms like Pl
            info = (chain.chain_id(), index)
            new_chain_info[atom.key] = info

    homeless_markers = _f_get_homeless_dna_markers()
    
    for marker in homeless_markers:
        still_alive = marker._f_move_to_live_atom(new_chain_info)
            # Note: this also comes up with direction advice for the new chain,
            # stored in the marker and based on the direction of its new atoms
            # in its old chain (if enough of them remain adjacent, currently 2);
            # but the new chain will later take that advice from at most one marker.
        if DEBUG_DNA_UPDATER:
            print "dna updater: moved marker %r, still_alive = %r" % (marker, still_alive)
        # Note: we needn't record the markers whose atoms are still alive,
        # since we'll find them all later on a new chain. Any marker
        # that moves either finds new atoms whose chain has a change
        # somewhere that leads us to find it (otherwise that chain would
        # be unchanged and could have no new connection to whatever other
        # chain lost atoms which the marker was on), or finds none, and
        # can't move, and either dies or is of no concern to us.

    # Tell all new chains to take over their atoms and any markers on them,
    # deciding between competing markers for influencing base indexing
    # and other settings, and creating new markers as needed.
    #
    # (Maybe also save markers for use in later steps, like making or updating
    #  Segment & Strand objects, and storing all these in DNA Groups.)
    #
    # Do axis chains first, so strand chains which need new markers or
    # direction decisions (etc) can be influenced by their base numbering, order, etc.
    #
    # (Future: we might have a concept of "main" and "secondary" strands
    # (e.g. scaffold vs staples in origami), and if so, we might want to do
    # all main strands before all secondary ones for the same reason.)
    
    # [Possible optim: reuse old chains if nothing has changed.
    # Not done at present; I'm not sure how rare the opportunity will be,
    # but I suspect it's rare, in which case, it's not worth the bug risk.]
    
    for chain in axis_chains:
        chain._f_own_atoms()
        # note: if useful, this might record a list of all live markers
        # found on that chain in the chain, as well as whatever marker
        # is chosen or made to control it. (But note that markers might
        # get removed or made independently without the chain itself
        # changing. If so, some invalidation of those chain attributes
        # might be needed. #e move this comment to DnaChain)

    for chain in strand_chains:
        chain._f_own_atoms()# IMPLEM - now these are stubs which always remake markers @@@

    ignore_new_changes("from updating DnaAtomMarkers")
        # ignore changes caused by adding/removing marker jigs
        # to their atoms, when the jigs die/move/areborn
    
    # That figured out which markers control each chain (and stored the answers in the chains). ###IMPLEM

    # Now use new_chain_info and the new chains to find all properly structured
    # base pairs and base pair stacks, for several purposes:
    # - (future) help detect errors in bond direction, major/minor groove
    #   geometry, etc
    # - find sets of atoms to make into AxisChunks or StrandSegmentChunks,
    #   using the markers updated above to know when to reuse old chunks
    #   (if that matters -- it might not, chunks might be an internal concept)
    # - update existing & new Strand and Segment objects, using markers to
    #   maintain their identity & association in the best way.

    # Basic algorithm: scan each axis chain (or ring), and follow along its two
    # bound strands to see when one or both of them leave it or stop (i.e. when
    # the next atom along the strand is not bound to the next atom along the
    # axis). This should classify all strand atoms as well (since bare ones were
    # deleted earlier -- if they weren't, remaining strand fragments can also
    # be found).
    #
    # implem/devel notes (some can be removed/condensed when devel is done):
    #
    # The fundamental operation is to move from a stacked base pair, or a maximal
    # fragment of one on one axis bond, to the next one, deciding which base
    # stackings were present. This might use of next_directional_bond_in_chain
    # to scan the strands, or similar code, needing a strand bond and atom to go
    # from. So we want a data structure that knows all the atoms and bonds in a
    # base pair (or at least the sugar atoms and bonds from them, if Pl atoms
    # are also present for PAM5). Ideally it should work for mixed PAM3/PAM5
    # chains, so we'll try to code it to not care.
    #
    # (Should the stacked base pair object be retained, as a jig known to
    #  all its atoms? Then the unchanged ones needn't be remade now... not sure.
    #  For now just treat it as flyweight, or even mutable/scannable, perhaps
    #  made of two flyweight base pair objects and an adjacent-base-pair holder
    #  for them. Those objects and their ops might as well be made generally
    #  available. So they'll be coded in new dna_model modules.)
    


    # Now.... @@@ [below here might be obs]


    # replace old chain info with new chain info on all live atoms
    # (Q: is this chain info undoable state? guess: yes) (do we need it? could find it via chunks... more efficient.... ### @@@)

    
    #e use them (or make new) to determine id & index for each chain

    # revise indices & chunking

    # markers are really on base-pairs... even though on certain atoms too. indices are for base pairs...
    # so we need to find sections of axis whose strands have no nicks, and number these, and assign these to larger things.
    # one alg: assign new id & indices to every changed chain, effectively a jiglike thing on that chain just to index it...
    # maybe the returned objects above could even be these things. a quick check lets you see if the atom already has one;
    # only reuse it if every atom has same one and atom count matches (ie if its membership needn't change).
    # the atom class can have a field & method for this thing, even if it's also in jigs list... it's a chain id & index...
    # so it can be identical for both axis and strand chains. those atoms can be ChainAtoms.
    # (What about PAM5? i think we'd index only Ss and reuse same index on Pl...)

    # optim: sort bonds in atom classes, and sort atoms in bond classes, in special ways.
    
    return # from update_PAM_chunks

# ==

def find_axis_and_strand_chains_or_rings( changed_atoms):
    """
    Find and return the lists (axis_chains, strand_chains)
    of connected sets of axis and strand atoms respectively,
    in the representation described below.

    @param changed_atoms: an atom.key -> atom dict of all changed atoms
                          that this function needs to consider,
                          which includes no killed atoms. WE ASSUME
                          OWNERSHIP OF THIS DICT and modify it in
                          arbitrary ways.
                          Note: in present calling code [071127]
                          this dict might include atoms from closed files.

    @return: (axis_chains, strand_chains), which are sequences of
    objects representing changed chains or rings (or lone atoms)
    of the specified element roles (axis or strand respectively).
    The chain or ring format is as returned by the make_* methods
    of the singleton objects axis_analyzer and strand_analyzer,
    which have methods for further use of those objects (in case
    they are just python data rather than class instances),
    e.g. for iterating over their atoms.
    Exception: None is never an element of the returned lists,
    since we remove it.
    """

    # Sort changed atoms into types we consider differently.

    axis_atoms = {}
    strand_atoms = {}

    def classify(atom):
        "put a live real atom into axis_atoms or strand_atoms, or discard it"
        # REVIEW: should we use atom classes or per-class methods here?
        # REVIEW: need to worry about atoms with too few bonds?
        element = atom.element
        role = element.role # 'axis' or 'strand' or None
        pam = element.pam # 'PAM3' or 'PAM5' or None
        if role == 'axis':
            axis_atoms[atom.key] = atom
            assert pam in ('PAM3', 'PAM5') # REVIEW: separate these too?
        elif role == 'strand':
            strand_atoms[atom.key] = atom
            assert pam in ('PAM3', 'PAM5') # REVIEW: separate these too?
        else:
            pass # ignore all other atoms
        return

    for atom in changed_atoms.itervalues():
        if atom.killed():
            print "bug: update_PAM_chunks: %r is killed (ignoring)", atom
        elif atom.is_singlet():
            # classify the real neighbor instead
            # (Note: I'm not sure if this is needed, but I'll do it to be safe.
            #  A possible need-case to review is when an earlier update step
            #  broke a bond.)
            classify(atom.singlet_neighbor())
        else:
            classify(atom)
        continue

    if not axis_atoms and not strand_atoms:
        return (), () # optimization

    if DEBUG_DNA_UPDATER:
        print "dna updater: %d axis atoms, %d strand atoms" % (len(axis_atoms), len(strand_atoms))
    
    axis_chains = axis_analyzer.find_chains_or_rings( axis_atoms )
        # NOTE: this takes ownership of axis_atoms and trashes it.
        # NOTE: this only finds chains or rings which contain at least one
        # atom in axis_atoms, but they often contain other axis atoms too
        # (which were not in axis_atoms since they were not recently changed).
        #
        # Result is a list of objects returned by the make_ methods in
        # analyzer (for doc, see abstract_bond_chain_analyzer, unless we
        # override them in axis_bond_chain_analyzer).

    assert not axis_atoms ### REMOVE WHEN WORKS

    ## del axis_atoms
    ##     SyntaxError: can not delete variable 'axis_atoms' referenced in nested scope
    axis_atoms = None # not a dict, bug if used

    if DEBUG_DNA_UPDATER:
        print "dna updater: found %d axis chains or rings" % len(axis_chains)
    
    # 
    strand_chains = strand_analyzer.find_chains_or_rings( strand_atoms )
    assert not strand_atoms ### REMOVE WHEN WORKS
    strand_atoms = None # not a dict, bug if used
    if DEBUG_DNA_UPDATER:
        print "dna updater: found %d strand chains or rings" % len(strand_chains)

    return axis_chains, strand_chains # from find_axis_and_strand_chains_or_rings

# end

