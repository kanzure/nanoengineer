"""
the main code will replace __class__ of Atom or Bond with related classes,
since Python supports this. This is done in dna_updater_utils.replace_atom_class().

If Python ever stops supporting this,
here is some unfinished code which indicates the sort of thing we'd have to do.
The hard part is replacing one atom with another in all the various places it can appear.
All the ones I can remember [bruce 071117] are listed in the following comment.
"""

# when i replace an atom (to change its class), i have to update it if it appears in various places:

# in the model:
# - chunk.atoms
# - jig.atoms
# - in all its bonds
# - as a chunk hotspot (only for its own chunk, i think)

# in the selection:
# - part.selatoms for its part (?)

# in highlighting caches:
# - glpane.selobj
# - glpane.selatom
# - the glname allocator? maybe not, if atom only gets into it when it's drawn... (unlike now)

# in undo checkpoints? i can just treat it as a new object --
# provided the changes to objects above, that replace it inside them,
# are undoable and tracked! but wait, they shouldn't need to be,
# since if i replaced it, it was illegal in any checkpointed state,
# assuming i did this for "local reasons" -- hmm, can bps change base atoms? ###

# ... this is a pain -- see if setting __class__ actually works!

def _replace_atom(atom, newatom): # move into chem.py, at least in part
    key = atom.key
    newatom.key = key
    mol = atom.molecule
    assert None is newatom.molecule ###k if it's already set, this .atoms mod just below might be already done...
    newatom.molecule = mol
    mol.atoms[key] = newatom
    atom.molecule = None
    }# tell chunk to inval its atom list??
    assert not newatom.jigs
    newatom.jigs = atom.jigs
    atom.jigs = []
    for jig in newatom.jigs:
        replace_in_list(jig.atoms, atom, newatom) #IMPLEM in py utils
    assert not newatom.bonds
    newatom.bonds = atom.bonds
    atom.bonds = []
    for bond in newatom.bonds:
        if bond.atom1 is atom:
            bond.atom1 = newatom
        if bond.atom2 is atom:
            bond.atom2 = newatom
    if mol._hotspot is atom:
        mol._hotspot is newatom
    }# and more... see above
    return

def in_some_other_func():
    # put bondpoints and atoms into the right classes

    for atom in changed_atoms.itervalues():
        if not atom.killed():
            if atom._f_actual_class_code != atom._f_desired_class_code:
                newatom = newclass( atom) ### IMPLEM
                replace_atoms[atom.key] = (atom, newatom)

    for atom, newatom in replace_atoms.iteritems():
        _replace_atom(atom, newatom)

# ==

# for a bond:
# - copy pi_bond_obj
# - in atom.bonds for its atoms
# - glpane.selobj
# - the glname allocator

# ==

# for a chunk: (i might just make a new one and move atoms in the same way as separate/merge, obviating this)
# - fix atom.molecule for its atoms
# - make sure it's in the right part, gets added to it properly and old chunk removed
# - in its own group
# - selmols?
# - chunkjig refs, if i have that
# - the glname allocator, and selobj, in case we allow it there in future

# end
