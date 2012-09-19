# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
fix_after_readmmp.py - helpers to fix dna-related structure after readmmp

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.updater.dna_updater_prefs import pref_fix_after_readmmp_before_updaters
from dna.updater.dna_updater_prefs import pref_fix_after_readmmp_after_updaters

def will_special_updates_after_readmmp_do_anything(assy):
    """
    Permit callers to optimize for the likely usual case
    of these debug_prefs both being off.
    """
    del assy
    if pref_fix_after_readmmp_before_updaters() or \
       pref_fix_after_readmmp_after_updaters():
        return True
    return False

def fix_after_readmmp_before_updaters(assy):
    if pref_fix_after_readmmp_before_updaters():
        ## print "\ndoing fix_after_readmmp_before_updaters"

        # note: this happens before updaters like dna updater and bond updater,
        # but not before update_parts has fixed the .part structure of assy.

        for part in assy.all_parts():
            part.enforce_permitted_members_in_groups( pre_updaters = True )
        pass
    return

def fix_after_readmmp_after_updaters(assy):
    if pref_fix_after_readmmp_after_updaters():
        ## print "\ndoing fix_after_readmmp_after_updaters"

        for part in assy.all_parts():
            part.enforce_permitted_members_in_groups( pre_updaters = False )
                # notice the different options than in before_updaters version
        pass
    return

# end
