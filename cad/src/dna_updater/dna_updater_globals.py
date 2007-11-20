# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_globals.py -- global variables or mutables for dna_updater,
and their lowest-level accessors.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_updater_constants import DEBUG_DNA_UPDATER

from changedicts import refreshing_changedict_subscription
from changedicts import _cdproc_for_dictid # but it's private!

from chem import _changed_structure_Atoms, _changed_parent_Atoms # but they're private! refactor sometime

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

def ignore_new_changes( from_what):
    """
    Discard whatever changes occurred since the last time
    we called get_changes_and_clear,
    of the changes we normally monitor and respond to.

    @param from_what: a string for debug prints,
                      saying what the changes are from,
                      e.g. "from fixing classes".
    """    
    ignore_these = get_changes_and_clear()
    
    if DEBUG_DNA_UPDATER and ignore_these:
        print "dna updater: ignoring %d new changes %s" % (len(ignore_these), from_what)
    
    del ignore_these
    return


# end
