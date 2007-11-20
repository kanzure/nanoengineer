
    # Give bondpoints and real atoms the desired Atom subclasses.
    # (Note: this can affect bondpoints and real atoms created by earlier steps
    #  of the same call of this function.)
    for atom in changed_atoms.itervalues():
        if not atom.killed():
            if atom._f_actual_class_code != atom._f_desired_class_code:
                newclass = '...'#stub
                replace_atom_class( atom, newclass, changed_atoms)
                    # note: present implem is atom.__class__ = newclass
            pass
        continue

    # ...
                
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

def _pop_arbitrary_real_atom_with_directional_real_bond(atoms_dict):
    """
    
    [and also discard non-qualifying atoms as you're looking]
    """
    while atoms_dict:
        key, atom = arbitrary_item(atoms_dict)
        del atoms_dict[key] # or implem pop_arbitrary_item
        if not atom.killed() and \
           not atom.element is Singlet: #k killed #e check elt flag?
            bonds = atom.directional_bonds() #e optim: just .bonds, check flag below, inlining is_directional
            for bond in bonds:
                if bond.is_open_bond(): #k
                    continue
                return atom, bond
    return None, None

def xxx():
    # ...
    while True:
        atom, bond = _pop_arbitrary_real_atom_with_directional_real_bond(unprocessed_atoms)
        if atom is None:
            assert not unprocessed_atoms
            break
        (ringQ, listb, lista) = res_element = grow_directional_bond_chain(bond, atom)
        ### BUG: only grows in one direction!
        # note: won't handle axis. need a different func for grow_bond_chain for that. next_axis_bond_in_chain
        for atom in lista:
            unprocessed_atoms.pop(atom.key, None)
        res.append( res_element)
        continue
    

    return ksddskj


def arbitrary_item(dict1):
    """
    If dict1 is not empty, efficiently return an arbitrary item
    (key, value pair) from it. Otherwise return None.
    """
    for item in dict1.iteritems():
        return item
    return None


# a lot of atom methods about directional bonds would also apply to axis bonds... almost unchanged, isomorphic
# but i guess i'll dup/revise the code
# also is it time to move these into subclasses of atom? i could introduce primitive updater that just keeps atom
# classes right... it might help with open bonds marked as directional... have to review all code that creates them.
# (and what about mmp reading? have to assume correct structure; for bare strand ends use geom or be arb if it is)


