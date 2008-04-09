# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_globals.py -- global variables or mutables for dna_updater,
and their lowest-level accessors.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from utilities import debug_flags

from foundation.changedicts import refreshing_changedict_subscription
from foundation.changedicts import _cdproc_for_dictid # but it's private!

from model.chem import _changed_structure_Atoms, _changed_parent_Atoms # but they're private! refactor sometime

from utilities.debug import print_compact_stack

_DEBUG_ATOM_KEY = None # None, or a value of atom.key for which all ignored changes should be printed

# ==

# _rcdp1 and _rcdp2 will be replaced in initialize_globals()
# with refreshing_changedict_subscription instances:
_rcdp1 = None
_rcdp2 = None

# REVIEW: when we reload this module during development,
# do we need to preserve those global objects?
# I would guess so, but I didn't yet see a bug from not doing so.
# [bruce 071119]

def initialize_globals():
    """
    Meant to be called only from master_model_updater.py
    (perhaps indirectly).
    
    Do whatever one-time initialization is needed before our
    other public functions should be called.
    
    [Also should be called if this module is reloaded.]
    """
    # set up this module's private global changedict subscription handlers
    global _rcdp1, _rcdp2
    
    _rcdp = _refreshing_changedict_subscription_for_dict
    
    _rcdp1 = _rcdp(_changed_structure_Atoms)
    _rcdp2 = _rcdp(_changed_parent_Atoms)
    return


def _refreshing_changedict_subscription_for_dict(dict1):
    cdp = _cdproc_for_dictid[ id(dict1)] # error if not found; depends on import/initialize order
    rcdp = refreshing_changedict_subscription( cdp)
    return rcdp


def get_changes_and_clear():
    """
    Grab copies of the global atom changedicts we care about,
    returning them in a single changed atom dict,
    and resubscribe so we don't grab the same changes next time.
    """
    dict1 = _rcdp1.get_changes_and_clear()
    dict2 = _rcdp2.get_changes_and_clear()
    # combine them into one dict to return (which caller will own)
    # optim: use the likely-bigger one, dict2 (from _changed_parent_Atoms),
    # to hold them all
    dict2.update(dict1)
    return dict2

def ignore_new_changes( from_what, changes_ok = True, debug_print_even_if_none = False):
    """
    Discard whatever changes occurred since the last time
    we called get_changes_and_clear,
    of the changes we normally monitor and respond to.

    @param from_what: a string for debug prints,
                      saying what the changes are from,
                      e.g. "from fixing classes".
    @type from_what: string
    
    @param changes_ok: whether it's ok (not an error) if we see changes.
    @type changes_ok: boolean
    
    @param debug_print_even_if_none: do our debug prints even if there were no changes
    @type debug_print_even_if_none: boolean
    """    
    ignore_these = get_changes_and_clear()

    if ignore_these or debug_print_even_if_none:
        if (not ignore_these) or changes_ok:
            if debug_flags.DEBUG_DNA_UPDATER:
                print "dna updater: ignoring %d new changes %s" % (len(ignore_these), from_what)
        else:
            msg = "\nBUG: dna updater: ignoring %d new changes %s -- any such changes are a bug: " % \
                  (len(ignore_these), from_what)
            print_compact_stack(msg)
            print

        if ignore_these.has_key(_DEBUG_ATOM_KEY):
            msg = "*** _DEBUG_ATOM_KEY %r: %r seen in those changes" % (_DEBUG_ATOM_KEY, ignore_these[_DEBUG_ATOM_KEY])
            if changes_ok:
                print_compact_stack(msg + ": ") # since we didn't print stack just above
            else:
                print msg
            
    del ignore_these
    return

# ==

# These should be cleared at the start and end of any dna updater run.

_f_DnaGroup_for_homeless_objects_in_Part = {}

_f_ladders_with_up_to_date_baseframes_at_ends = {}
    #bruce 080409, replacing ladders_dict params (whose passing into enough
    #  methods/functions was unfinished)

def clear_updater_run_globals(): #bruce 080218
    """
    Clear globals which are only used during individual runs of the dna updater.
    """
    # Note: perhaps not all such globals are here yet, which should be.
    # And there are some in fix_bond_directions (IIRC) which can't be here.
    _f_DnaGroup_for_homeless_objects_in_Part.clear()
    _f_ladders_with_up_to_date_baseframes_at_ends.clear()
    return

# end
