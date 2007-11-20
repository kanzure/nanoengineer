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

from elements import PeriodicTable

from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False

from debug import register_debug_menu_command

import env

from constants import diDEFAULT

from utilities.Log import orangemsg, greenmsg

# ==

DEBUG_DNA_UPDATER = True # ok to commit with True for now [bruce 071119]

# ==

# _rcdp1 and _rcdp2 will be replaced in initialize()
# with refreshing_changedict_subscription instances:
_rcdp1 = None
_rcdp2 = None

# REVIEW: when we reload this module during development,
# do we need to preserve those global objects?
# I would guess so, but I didn't yet see a bug from not doing so.
# [bruce 071119]

def initialize():
    """
    Meant to be called only from master_model_updater.py.
    Do whatever one-time initialization is needed before our
    other public functions should be called.
    [Also called after this module is reloaded.]
    """
##    if DEBUG_DNA_UPDATER:
##        print "dna updater: initialize"

    # set up this module's private global changedict subscription handlers
    global _rcdp1, _rcdp2
    _rcdp = _refreshing_changedict_subscription_for_dict
    _rcdp1 = _rcdp(_changed_structure_Atoms)
    _rcdp2 = _rcdp(_changed_parent_Atoms)

    # make debug prefs appear in debug menu
    pref_fix_deprecated_PAM3_atoms()
    pref_fix_deprecated_PAM5_atoms()

    _register_our_debug_menu_commands()
    
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

# TODO: when these debug prefs change, have them rescan all atoms
# in the current part, or print a reminder to do that.

def pref_fix_deprecated_PAM3_atoms():
    res = debug_pref("DNA: fix deprecated PAM3 atoms?",
                     Choice_boolean_False,
                     ## SOON: Choice_boolean_True,
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_prefs )
    return res

def pref_fix_deprecated_PAM5_atoms():
    res = debug_pref("DNA: fix deprecated PAM5 atoms?",
                     Choice_boolean_False,
                     non_debug = True,
                     prefs_key = True,
                     call_with_new_value = _changed_prefs )
    return res

def _changed_prefs(val):
    if val:
        msg = "Note: to use new DNA prefs value on existing atoms, " \
              "run \"DNA: rescan all atoms\" in debug->other menu."
        env.history.message(orangemsg(msg))
    return

# ==

def rescan_atoms_in_current_part(assy, only_selected = False):
    oldlen = len(_changed_structure_Atoms)
    for mol in assy.molecules:
        for atom in mol.atoms.itervalues():
            if not only_selected or atom.picked or \
               (atom.is_singlet() and atom.singlet_neighbor().picked):
                _changed_structure_Atoms[atom.key] = atom
    newlen = len(_changed_structure_Atoms)
    msg = "len(_changed_structure_Atoms) %d -> %d" % (oldlen, newlen)
    env.history.message(greenmsg( "DNA debug command:") + " " + msg)
    return

def rescan_all_atoms(glpane):
    rescan_atoms_in_current_part( glpane.assy)

def rescan_selected_atoms(glpane):
    rescan_atoms_in_current_part( glpane.assy, only_selected = True)

def _register_our_debug_menu_commands():
    register_debug_menu_command( "DNA: rescan all atoms", rescan_all_atoms )
    register_debug_menu_command( "DNA: rescan selected atoms", rescan_selected_atoms )

# ==
    
def update_PAM_atoms(assy):
    """
    [called from _master_model_updater]
    """
    changed_atoms = _get_changes_and_clear()
    
    if not changed_atoms:
##        if DEBUG_DNA_UPDATER:
##            print "dna updater: update_PAM_atoms() has no work to do"
        return # optimization (might not be redundant with caller)

    # scan for deprecated elements, and fix them

    if DEBUG_DNA_UPDATER:
        print "dna updater: %d changed atoms to scan" % len(changed_atoms)

    deprecated_atoms = []
    
    for atom in changed_atoms.itervalues():
        deprecated_to = atom.element.deprecated_to
            # an element symbol, or None, or 'remove'
        if deprecated_to:
            pam = atom.element.pam
            assert pam in ('PAM3', 'PAM5')
            if pam == 'PAM3':
                fix = pref_fix_deprecated_PAM3_atoms()
            elif pam == 'PAM5':
                fix = pref_fix_deprecated_PAM5_atoms()
            else:
                fix = False
            if fix:
                deprecated_atoms.append(atom)
            elif DEBUG_DNA_UPDATER:
                print "dna updater: debug_pref says don't alter deprecated atom %r" % (atom,)
        continue

    for atom in deprecated_atoms:
        deprecated_to = atom.element.deprecated_to
            # an element symbol, or 'remove'
        if atom.display != diDEFAULT:
            # Atoms of deprecated elements sometimes have funny display modes
            # set by the DNA Duplex Generator. Remove these here.
            # (This may be needed even after we fix the generator,
            #  due to old mmp files. REVIEW: can it ever cause harm?)
            atom.setDisplay(diDEFAULT)
        if deprecated_to == 'remove' or deprecated_to == 'X':
            # (Atom.kill might be unideal behavior for 'remove',
            #  but that's only on Pl3 which never occurs AFAIK, so nevermind)
            # Kill the atom (and make sure that new bondpoints get into a good enough position).
            # REVIEW: does atom.kill make new bps immediately
            # (review whether ok if more than one needs making on one base atom)
            # or later
            # (review whether it's still going to happen in the current master_updater call)? ####

            if DEBUG_DNA_UPDATER:
                print "dna updater: kill atom %r" % (atom,)
            atom.kill()

            # TODO: worry about atom being a hotspot, or having a bondpoint which is a hotspot?
        else:
            # Transmute atom to a new element symbol -- assume its position,
            # bonds, and bondpoints are all ok and need no changes.
            # (Should be true of as 071119, since this is used only
            #  to make Ax and Ss PAM atoms from variant atomtypes
            #  used to mark them as being in special situations.)
            #
            # Use mvElement to avoid remaking existing bondpoints.
            elt = PeriodicTable.getElement(deprecated_to)
            if DEBUG_DNA_UPDATER:
                print "dna updater: transmute atom %r to element %s" % (atom, elt)
            atom.mvElement(elt)
            atom.make_enough_bondpoints()
                # REVIEW: do this later, if atom classes should be corrected first
                # to help this properly position bondpoints
                # (or perhaps, first set correct atom classes, then do this,
                #  making sure it sets correct bondpoint classes,
                #  or that we correct them separately afterwards)
        continue

    # Grab whatever new atoms the prior step made,
    # and include them in subsequent steps.
    # (Note that atoms we already had might have become killed
    #  and/or have different elements now.)
    changed_atoms.update( _get_changes_and_clear() )

    #e filter out killed atoms?



    ########### RETURN HERE, FOR INITIAL TESTING
    
    return

    ##########



    # Give bondpoints and real atoms the desired Atom subclasses.
    # (Note: this can affect bondpoints and real atoms created by earlier steps
    #  of the same call of this function.)
    for atom in changed_atoms.itervalues():
        if not atom.killed():
            if atom._f_actual_class_code != atom._f_desired_class_code:
                newclass = '...'#stub
                replace_atom_class(assy, atom, newclass, changed_atoms)
                    # note: present implem is atom.__class__ = newclass
            pass
        continue

    # ...
                
    
    # look at element fields:
    # pam = 'PAM3' or 'PAM5' or None
    # role = 'axis' or 'strand' or None


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


