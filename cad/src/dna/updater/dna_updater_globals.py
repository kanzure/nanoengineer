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

from model.global_model_changedicts import _changed_structure_Atoms # todo: rename to be non-private
from model.global_model_changedicts import _changed_parent_Atoms

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

# globals and accessors
# (some can be set outside of dna updater runs, noticed during them)

# (not yet here: _f_are_there_any_homeless_dna_markers, etc)

_f_invalid_dna_ladders = {} # moved here from DnaLadder.py, bruce 080413 [rename with _f_?]

def _f_get_invalid_dna_ladders(): # moved here from DnaLadder.py, bruce 080413
    """
    Return the invalid dna ladders,
    and clear the list so they won't be returned again
    (unless they are newly made invalid).

    Friend function for dna updater. Other calls
    would cause it to miss newly invalid ladders,
    causing serious bugs.
    """
    res = _f_invalid_dna_ladders.values()
    _f_invalid_dna_ladders.clear()
    res = filter( lambda ladder: not ladder.valid, res ) # probably not needed
    return res

def _f_clear_invalid_dna_ladders(): #bruce 080413; see comment in caller about need for review/testing
    if _f_invalid_dna_ladders:
        print "fyi: dna updater: ignoring %d newly invalid dnaladders" % \
              len( _f_invalid_dna_ladders)
    _f_invalid_dna_ladders.clear()
    return

_f_baseatom_wants_pam = {}
    # maps baseatom.key to a PAM_MODEL it wants updater to convert it to
    #bruce 080411, for use instead of chunk attrs like .display_as_pam
    # by commands for manual conversion of PAM model

# note: Pl atoms are not baseatoms! To use _f_baseatom_wants_pam on them,
# you need this function:

def _f_anyatom_wants_pam(atom): #bruce 080411
    # not counting its chunk attrs, just looking at _f_baseatom_wants_pam properly
    if atom.element.symbol == 'Pl5':
        atom = atom.Pl_preferred_Ss_neighbor()
        if atom is None:
            # that method printed a bug note already
            return None
    return _f_baseatom_wants_pam.get(atom.key)

# ==

# These should be cleared at the start and end of any dna updater run.

_f_DnaGroup_for_homeless_objects_in_Part = {}

_f_ladders_with_up_to_date_baseframes_at_ends = {}
    #bruce 080409, replacing ladders_dict params (whose passing into enough
    #  methods/functions was unfinished)

_f_atom_to_ladder_location_dict = {}
    #bruce 080411, to permit finding ladder/rail/index of atoms in freshly
    # made ladders which didn't yet remake their chunks
    # (needn't store all end atoms, since those can be found using
    #  rail_end_atom_to_ladder -- important for bridging Pls
    #  between fresh and old-untouched ladders)

DNALADDER_INVAL_IS_OK = 0
DNALADDER_INVAL_IS_ERROR = 1
DNALADDER_INVAL_IS_NOOP_BUT_OK = 2

dnaladder_inval_policy = DNALADDER_INVAL_IS_OK
    ### todo: make private; only used directly in this file
    # and this rule should be maintained
    # [bruce 080413]

def get_dnaladder_inval_policy():
    # (use this to prevent bugs from importing a mutable value
    # and having only the initial value defined globally in a
    # client module)
    return dnaladder_inval_policy

def clear_updater_run_globals(): #bruce 080218
    """
    Clear globals which are only used during individual runs of the dna updater.
    """
    # Note: perhaps not all such globals are here yet, which should be.
    # And there are some in fix_bond_directions (IIRC) which can't be here.
    _f_DnaGroup_for_homeless_objects_in_Part.clear()
    _f_ladders_with_up_to_date_baseframes_at_ends.clear()
    _f_atom_to_ladder_location_dict.clear()
    global dnaladder_inval_policy
    dnaladder_inval_policy = DNALADDER_INVAL_IS_OK
        # important in case of exceptions during updater
    return

def temporarily_set_dnaladder_inval_policy(new): # bruce 080413
    """
    Must be used in matching pairs with restore_dnaladder_inval_policy,
    and only within the dna updater.
    """
    global dnaladder_inval_policy
    old = dnaladder_inval_policy
    dnaladder_inval_policy = new
    return old

def restore_dnaladder_inval_policy(old): # bruce 080413
    global dnaladder_inval_policy
    dnaladder_inval_policy = old
    return

# ==

def rail_end_atom_to_ladder(atom):
    """
    Atom is believed to be the end-atom of a rail in a valid DnaLadder.
    Return that ladder. If anything looks wrong, either console print an error message
    and return None (which is likely to cause exceptions in the caller),
    or raise some kind of exception (which is what we do now, since easiest).
    """
    #bruce 080510 moved this from DnaLadder.py to avoid import cycles
    # various exceptions are possible from the following; all are errors
    try:
        ladder = atom._DnaLadder__ladder
            # note: this attribute name is hardcoded in several files
        ## assert isinstance(ladder, DnaLadder)
            # (not worth the trouble, since we don't want the DnaLadder import)
        assert ladder is not None
        assert ladder.valid, "%r not valid" % ladder
            # note: changes in _ladder_set_valid mean this will become common for bugs, attrerror will be rare [080413]
            # or: if not, print "likely bug: invalid ladder %r found on %r during merging" % (ladder, atom) #k
            # REVIEW: it might be better to return an invalid ladder than no ladder or raise an exception,
            # so we might change this to return one, provided the atom is in the end_baseatoms. ####
        assert atom in ladder.rail_end_baseatoms()
        return ladder
    except:
        error = atom._dna_updater__error and ("[%s]" % atom._dna_updater__error) or ""
        print "\nfollowing exception is an error in rail_end_atom_to_ladder(%r%s): " % \
              (atom, error)
        raise
    pass

# end
