# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
fix_atom_classes.py - fix classes of PAM atoms

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.updater.dna_updater_utils import replace_atom_class

from model.chem import Atom

StrandAtom = Atom # stub
AxisAtom = Atom # stub
UnpairedBaseAtom = Atom # stub


##issues: bondpoint classes. need a separate func to fix them later?
##which ones do we fix, all new bps and all bps on changed atoms? (yes)
##for all these, fix all bps on on base at once, so store base in a dict
##after all transmutes and breaks.
##
##other issues:
##    Atom vs ChemAtom
##    code on Atom or on Element?
##    or Atomtype?
##
##guess: as we fix atoms colect bps and their base atoms into sep dict
##when it's full, incl of busted bonds,
##then fix all the bps of those base atoms.
##using a separate func, to fix bp classes and reposition them too.
##
##so this present code can ignore bps for now.

# ==

# obs cmt?
    # Give bondpoints and real atoms the desired Atom subclasses.
    # (Note: this can affect bondpoints and real atoms created by earlier steps
    #  of the same call of this function.)

    ## atom._f_actual_class_code != atom._f_desired_class_code:

def real_atom_desired_class(atom): #e refile into an Atom method? return classname only?
    """
    Which class do we wish a real atom was in, based on its element,
    and if it's a bondpoint, on its neighbor atom?
    """
    assert not atom.killed()

##    if atom.is_singlet():
##        # WRONG. true desire is for special atoms to have the right pattern of special bps...
##        base = atom.singlet_neighbor()
##        assert not base.killed()
##    else:
##        base = atom
##    element = base.element
    assert not atom.is_singlet()
    element = atom.element

    pam = element.pam # MODEL_PAM3 or MODEL_PAM5 or None ### use this?
    role = element.role # 'strand' or 'axis' or 'unpaired-base' or None
    if role == 'strand':
        return StrandAtom # PAM3_StrandAtom? subclass of StrandAtom? What about Pl?
    elif role == 'axis':
        return AxisAtom
    elif role == 'unpaired-base':
        return UnpairedBaseAtom
    else:
        return Atom # ChemAtom?

def fix_atom_classes( changed_atoms): #e rename, real_atom; call differently, see comment above ### @@@
    """
    Fix classes of PAM atoms in changed_atoms, ignoring bondpoints
    and/or killed atoms.
    (Also patch changed_atoms with replaced atoms if necessary.)
    """
    for atom in changed_atoms.itervalues():
        if not atom.killed() and not atom.is_singlet():
            old_class = atom.__class__
            ## new_class = atom._f_desired_class ### IMPLEM, maybe revise details
            new_class = real_atom_desired_class( atom)
            if old_class is not new_class:
                replace_atom_class( atom, new_class, changed_atoms)
                    # note: present implem is atom.__class__ = new_class;
                    # and any implem only changes changed_atoms
                    # at atom.key (which is unchanged),
                    # so is legal during itervalues.
        continue
    return
