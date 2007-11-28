
    # find directional bond chains (or rings) covering our atoms

    def func( atom1, dir1): # wrong, see below
        if atom1.killed(): ###k
            return ### best place to do this?
        for b in atom1.bonds:
            if b.is_directional():
                a1, a2 = b.atom1, b.atom2
                dir1[a1.key] = a1
                dir1[a2.key] = a2
        return
    all_atoms = transclose( initial_atoms, func )

    # wait, that only found all atoms, not their partition... ###

    # does transclose know when it has to go back to an initial atom to find more? probably not.
    # it does not even assume equiv relation, but on one-way relation this partition is not defined.

    # also when we do find these partitions, we probably want their chain lists, not just their sets.
    # so make new finding code to just grab the chains, then see which initial_atoms can be dropped (efficiently).
    # probably mark the atoms or store them in dicts, as well as making chains.
    # An easy way: grow_bond_chain, and a custom next function for it. It can remove from initial_atoms too, as it runs past.

    return

# ==

# obs - see pop_arbitrary_item and its caller in bond_chains.py
def _pop_arbitrary_atom_with_qualifying_bond(atoms_dict, bond_ok_func):
    """
    Return (atom, bond) (and pop atom from atoms_dict) where atom has bond
    and bond_ok_func(bond) is true, or return (None, None) if no remaining
    atoms have qualifying bonds.

    Also pop all atoms returned, and all atoms skipped since they have no
    qualifying bonds. This means that atoms_dict will be empty when we
    return (None, None). It also means any atom is returned at most once,
    during repeated calls using the same atoms_dict, even if it has more
    than one qualifying bond.

    Warning: there is no atom_ok_func, and we consider all atoms or bondpoints
    with no checks at all, not even of atom.killed().
    
    In typical usage, the caller might add atoms to or remove atoms from
    atoms_dict between repeated calls, terminating a loop when we return
    (None, None) and/or when atoms_dict becomes empty.
    """
    while atoms_dict:
        key_unused, atom = pop_arbitrary_item(atoms_dict)
        # Assume any atom with a qualifying bond is ok
        # (i.e. caller must exclude non-ok atoms).
        # [Someday we might need to add an atom_ok_func,
        #  or a func that looks at both atom and bond,
        #  if of two atoms on an ok bond, only one might be ok.
        #  But it's probably still easier to do it in a helper function
        #  (like this one) than directly in a caller loop, due to our
        #  desire to pop atom as soon as we return it with any bond,
        #  even if it qualifies with other bonds too.]
        for bond in atom.bonds:
            if bond_ok_func(bond):
                return atom, bond
        # REVIEW: should we return (atom, None) here?
    return None, None

# obs - see same-named method in class xxx in bond_chains.py
def find_chains_or_rings(unprocessed_atoms, atom_ok_func): # needs rewrite as in TODO @@@ ; REVIEW: discard lone atoms ok??
        # TODO: also needs a function to find one bond or test one bond;
        # if that func just returns the special bonds from an atom, up to 2, open bonds ok??,
        # then maybe it's enough and we can use it to make the next_bond_in_chain function too.
        # (Or the special func could just be an atom test...)
    # ...
    def bond_ok_func(bond):
        return atom_ok_func(bond.atom1) and \
               atom_ok_func(bond.atom2)
    def next_bond_in_chain(...):
        pass...
    while True:
        atom, bond = _pop_arbitrary_atom_with_qualifying_bond(unprocessed_atoms, bond_ok_func)
        if atom is None:
            assert not unprocessed_atoms
            break
        (ringQ, listb, lista) = res_element = grow_bond_chain(bond, atom, next_bond_in_chain)
        
        ### BUG: only grows in one direction!
        # see some caller
        #   of grow_bond_chain
        #   or grow_directional_bond_chain
        # which calls it twice...
        # ... hmm, make_pi_bond_obj calls twice grow_pi_sp_chain
        
        for atom in lista:
            unprocessed_atoms.pop(atom.key, None)
        res.append( res_element)
        continue
    

    return ksddskj




# a lot of atom methods about directional bonds would also apply to axis bonds... almost unchanged, isomorphic
# but i guess i'll dup/revise the code
# also is it time to move these into subclasses of atom? i could introduce primitive updater that just keeps atom
# classes right... it might help with open bonds marked as directional... have to review all code that creates them.
# (and what about mmp reading? have to assume correct structure; for bare strand ends use geom or be arb if it is)

===


    # Separate connected sets of axis atoms into AxisChunks, reusing existing
    # AxisChunks whereever possible; same with StrandSegmentChunks, but more complex...
    #
    # [REVIEW: also label the atoms with positional hints? Note that we need these
    #  (e.g. base indices) in order to decide which old chunks correspond to
    #  which new ones when they break or merge. For now we might just use atom.key,
    #  since for generated structures it may have sort of the right order.]

        # REVIEW/obs/scratch comments:

        # divide atoms into chunks of the right classes, in the right way

        # some bond classes can't be internal bonds... some must be...
        
        # (If any improper branching is found, complain, and let it break up
        #  the chunks so that each one is properly structured.)

    axis_chains, strand_chains = find_axis_and_strand_chains_or_rings( changed_atoms)

    # ... now we should recognize sections of axis on which both strands remain properly bonded...
    # assigning every atom an index ... probably the strand atoms look at their axis atom index...
    # PROBLEM: extent of axes and strands we have (the changed ones) does not correspond.
    # Ideally we'd like to ignore the unchanged parts. Even more ideally, not even scan them!
    # (tThough they have new indices and might be in different strands/segments, so in the end
    #  we at least have to scan thru them to change some settings about that.)
    #
    # If we have these ids on atoms, can't we just trust them and not scan them, for sections
    # with no atom changes? those sections get broken up, but the pieces ought to have trustable indices...
    # to implement the breakage we might have to reindex (all but one of them) somehow... ####

    # goals:
    # - low runtime when few changes -- take advantage of unchanged sections, even if we have to reindex them
    # - simplicity, robustness
    # - know how to copy segment and strand info, incl unique id, as things change in extent (does it slide along the chains?)
    # - recognize base pairs and properly stacked basepairs, assign indices that fit, use those for geom/direction error checking,
    #   direction assignment when unset
    # design Qs:
    # - how *do* we decide how to copy strand & segment info? note: pay more attention to basepair index than to strand direction.
    #   e.g. compare basepair index (or atom key) of the connected axis atoms of the base pairs.
    # - user-settable jigs for base index origin/direction?
    # - user-settable jigs or tags for subsequences on strands or segments?
    # implem Qs:
    # - are the indices undoable?
    #   (guess: no, they're always derived;
    #    but if we make arb choices like ring-origin, create undoable/mmp state for them, either fields/tags or jigs. ###)
    # - do they affect display? (eg in rainbow coloring mode) 

    # misc:
    # - if earlier stage assigns atom classes, it could also order the bonds in a definite way,
    #   e.g. a strand atom's first bond could be to the axis
    
    for axis_set in axis_chains:
        axis_set.ringQ
        axis_set.lista # or atoms_list or atoms_dict?
        axis_set.listb
        for atom in axis_analyzer.found_object_iteratoms(axis_set):
            bla

_changed_markers = {}

class ChainAtomMarker(Jig):
    _old_atom = None
    def needs_atoms_to_survive(self):
        # False, so that if our atom is removed, we don't die.
        # Problem: if we're selected and copied, but our atom isn't, this would copy us.
        # But this can't happen if we're at toplevel in a DNA Group, and hidden from user,
        # and thus only selected if entire DNA Group is.
        return False
    def confers_properties_on(self, atom):
        """
        [overrides Node method]
        Should this jig be partly copied (even if not selected)
        when this atom is individually selected and copied?
        (It's ok to assume without checking that atom is one of this jig's atoms.)
        """
        return True
    def remove_atom(self, atom):
        self._old_atom = atom
        _changed_markers[id(self)] = self # TODO: also do this when copied? not sure it's needed.
        Jig.remove_atom(atom)
        return
    pass

# should AtomChain itself also be a Jig? (only if it can store its atoms in a set, not a list...)


