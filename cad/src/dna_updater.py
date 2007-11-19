# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater.py -- enforce rules on DnaGroups, PAM atoms, etc, as needed.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from changedicts import refreshing_changedict_subscription
from changedicts import _cdproc_for_dictid # but it's private!

from chem import _changed_structure_Atoms, _changed_parent_Atoms # but they're private! refactor sometime

from dna_updater_utils import replace_atom_class, replace_bond_class

# _rcdp1 and _rcdp2 will be replaced in initialize()
# with refreshing_changedict_subscription instances:
_rcdp1 = None
_rcdp2 = None

def initialize():
    """
    Meant to be called only from master_model_updater.py.
    Set up our private global changedict subscription handlers.
    """
    global _rcdp1, _rcdp2
    _rcdp = _refreshing_changedict_subscription_for_dict
    _rcdp1 = _rcdp(_changed_structure_Atoms)
    _rcdp2 = _rcdp(_changed_parent_Atoms)
    return

def _refreshing_changedict_subscription_for_dict(dict1):
    cdp = _cdproc_for_dictid[id(dict1)] # error if not found; depends on import/initialize order
    rcdp = refreshing_changedict_subscription(cdp)
    return rcdp

def _get_changes_and_clear():
    """
    grab copies of the global atom changedicts we care about,
    returning them in a single changed atom dict,
    and resubscribe so we don't grab the same changes next time
    """
    dict1 = _rcdp1.get_changes_and_clear()
    dict2 = _rcdp2.get_changes_and_clear()
    # combine them into one dict to return (which caller will own)
    # optim: use the likely-bigger one, dict2 (from _changed_parent_Atoms),
    # to hold them all
    dict2.update(dict1)
    return dict2

# ==

def update_PAM_atoms(assy): # TODO: call this from _master_model_updater
    """
    """
    changed_atoms = _get_changes_and_clear()

    # scan for deprecated elements, and fix them

    for atom in changed_atoms.itervalues():
        xxx = atom.element.xxx
        if xxx:
            xxx

    # grab whatever new atoms the prior step made,
    # and include them in subsequent steps
    changed_atoms.update( _get_changes_and_clear() )


    #e filter out killed atoms?


    # Give bondpoints and real atoms the desired Atom subclasses.
    for atom in changed_atoms.itervalues():
        if not atom.killed():
            if atom._f_actual_class_code != atom._f_desired_class_code:
                newclass = ...
                replace_atom_class(assy, atom, newclass, changed_atoms)
                    # note: present implem is atom.__class__ = newclass
            pass
        continue

    # ...
                
    
    # fhkdhfsda


    #fh hdsfhsajd

    # fhdlkfhdsjhfsa


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

def xxx:
    ...
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


