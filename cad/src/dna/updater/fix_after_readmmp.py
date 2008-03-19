# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
fix_after_readmmp.py - helpers to fix dna-related structure after readmmp

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.updater.dna_updater_prefs import pref_fix_after_readmmp_before_updaters
from dna.updater.dna_updater_prefs import pref_fix_after_readmmp_after_updaters

def fix_after_readmmp_before_updaters(assy):
    if pref_fix_after_readmmp_before_updaters():
        print "doing fix_after_readmmp_before_updaters (nim)" ###
    pass

def fix_after_readmmp_after_updaters(assy):
    if pref_fix_after_readmmp_after_updaters():
        print "doing fix_after_readmmp_after_updaters (nim)" ###
    pass

# end
