# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
dna_updater_init.py --

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""


from dna.updater.dna_updater_globals import initialize_globals

from dna.updater.dna_updater_prefs import initialize_prefs

from dna.updater.dna_updater_commands import initialize_commands

# ==


def initialize():
    """
    Meant to be called only from master_model_updater.py.
    Do whatever one-time initialization is needed before our
    other public functions should be called.
    [Also called after this module is reloaded.]
    """
    initialize_globals()
    initialize_prefs()
    initialize_commands()
    return

# end
