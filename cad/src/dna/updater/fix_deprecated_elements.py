# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
fix_deprecated_elements.py - fix deprecated PAM elements in-place in models

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from model.elements import PeriodicTable

from utilities.constants import diDEFAULT

from utilities import debug_flags

from dna.updater.dna_updater_prefs import pref_fix_deprecated_PAM3_atoms
from dna.updater.dna_updater_prefs import pref_fix_deprecated_PAM5_atoms
from dna.updater.dna_updater_prefs import dna_updater_warn_when_transmuting_deprecated_elements

import foundation.env as env
from utilities.Log import orangemsg
from utilities.constants import MODEL_PAM3, MODEL_PAM5

# ==

def fix_deprecated_elements( changed_atoms):
    """
    scan for deprecated elements, and fix them
    """

    fix_PAM3 = pref_fix_deprecated_PAM3_atoms()
    fix_PAM5 = pref_fix_deprecated_PAM5_atoms()

    deprecated_atoms = []

    for atom in changed_atoms.itervalues():
        deprecated_to = atom.element.deprecated_to
            # an element symbol, or None, or 'remove'
        if deprecated_to:
            pam = atom.element.pam
            assert pam in (MODEL_PAM3, MODEL_PAM5)
            if pam == MODEL_PAM3:
                fix = fix_PAM3
            elif pam == MODEL_PAM5:
                fix = fix_PAM5
            else:
                fix = False
            if fix:
                deprecated_atoms.append(atom)
            elif debug_flags.DEBUG_DNA_UPDATER:
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
            atom.setDisplayStyle(diDEFAULT)
        if deprecated_to == 'remove' or deprecated_to == 'X':
            # (Atom.kill might be unideal behavior for 'remove',
            #  but that's only on Pl3 which never occurs AFAIK, so nevermind)
            # Kill the atom (and make sure that new bondpoints get into a good enough position).
            # REVIEW: does atom.kill make new bps immediately
            # (review whether ok if more than one needs making on one base atom)
            # or later
            # (review whether it's still going to happen in the current master_updater call)? ####

            if debug_flags.DEBUG_DNA_UPDATER_VERBOSE:
                print "dna updater: kill deprecated atom %r" % (atom,)
            summary_format = \
                "Warning: dna updater killed [N] deprecated %s pseudoatom(s)" % \
                (atom.element.symbol,)
            env.history.deferred_summary_message( orangemsg(summary_format) )

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
            if debug_flags.DEBUG_DNA_UPDATER_VERBOSE:
                print "dna updater: transmute deprecated atom %r to element %s" % \
                      (atom, elt.symbol)
            if dna_updater_warn_when_transmuting_deprecated_elements():
                summary_format = \
                    "Warning: dna updater transmuted [N] %s to %s pseudoatom(s)" % \
                    (atom.element.symbol, elt.symbol )
                env.history.deferred_summary_message( orangemsg(summary_format) )
                    # todo: refactor so orangemsg is replaced with a warning option
            atom.mvElement(elt)
            atom.make_enough_bondpoints()
                # REVIEW: do this later, if atom classes should be corrected first
                # to help this properly position bondpoints
                # (or perhaps, first set correct atom classes, then do this,
                #  making sure it sets correct bondpoint classes,
                #  or that we correct them separately afterwards)
        continue

    return # from fix_deprecated_elements

# end
