# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
global_model_changedicts.py - global changedicts needed by master_model_updater
or the specific update functions it calls. These are public for access
and modification by those update functions, and for additions by all
low-level model-modification code.


@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.


TODO:

Maybe make their global names (here) and localvar names (in specific update functions) differ.

Maybe let them be created by changedict objects,
from which we'll assign them to these same globals?

This would also facilitate their use in ways that are
protected from undetected changes during their use,
related to how Undo uses its changedicts, but swapping
in new subscribing dicts each time an old one needs
to be looked at.

Maybe let them be attributes of one singleton object?

Related -- integrate these with the Undo changedicts
and in some cases reuse the same ones (subscribe to
them in master_model_updater or its update functions).

(For what to do to be clear, we need to see the details
of how higher-level updaters ever need to repeat lower-level
ones.)


History:

bruce 050627 started this as part of supporting higher-order bonds.

bruce 071108 split this out of bond_updater.py (which also got
split into itself and master_model_updater.py).
"""

# ==

# dict for atoms or singlets whose element, atomtype, or set of bonds (or neighbors) gets changed [bruce 050627]
#e (doesn't yet include all killed atoms or singlets, but maybe it ought to) [that comment might be obs!]
# (changing an atom's bond type does *not* itself update this dict -- see changed_bond_types for that)

changed_structure_atoms = {} # maps atom.key to atom, for atoms or singlets
    # WARNING: there is also a related but different global dict lower down in this file,
    # whose spelling differs only in 'A' vs 'a' in Atoms, and initial '_'.
    # See the comment there for more info. [bruce 060322]

# ==

# changedicts for class Atom, used by Undo and by dna updater
# [moved from chem.py (near class Atom) to this file, bruce 080510;
#  for comments and registrations, see chem.py]

# TODO: rename these to not appear to be private. They're all used in chem.py,
# and several of them are used in other files.

_changed_parent_Atoms = {}

_changed_structure_Atoms = {}
    # WARNING: there is also a related but different global dict earlier in this file,
    # whose spelling differs only in 'A' vs 'a' in Atoms, and in having no initial underscore,
    # namely, changed_structure_atoms. For more info, see the comment under the import
    # of this dict in chem.py.

_changed_posn_Atoms = {}

_changed_picked_Atoms = {}

_changed_otherwise_Atoms = {}

# ==

# dict for bonds whose bond-type gets changed
# (need not include newly created bonds)

changed_bond_types = {}

# ==

# status codes for updater runs of all kinds
# (not yet used for all updaters, though).

LAST_RUN_DIDNT_HAPPEN = 9 # due to all updaters skipped, or that updater disabled, or program just started
LAST_RUN_IS_ONGOING = 10
LAST_RUN_FAILED = 11 # i.e. raised an exception and ended early
LAST_RUN_SUCCEEDED = 12

status_of_last_dna_updater_run = LAST_RUN_DIDNT_HAPPEN

# end
