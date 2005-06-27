# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
bond_updater.py

[unfinished]

Recompute structural bond orders when necessary.

$Id$

This is needed for bonds between atoms whose atomtypes make p orbitals
available for bonding, to check whether pi bonds are formed,
whether they're aromatic or double or triple, to check for
radicals (pi systems containing unpaired electrons),
and to notice graphite.

History:

bruce 050627 started this as part of supporting higher-order bonds.
'''

__author__ = 'bruce'

###e needs cvs add



import platform

def update_bonds_after_each_event( _changed_structure_atoms):
    """[should be called only from env.post_event_updates]
    #doc
    """
    #bruce 050627 #e might want arg for slow or fast... later will become part of a more general update scheme
    ###@@@ NIM
    if platform.atom_debug:
        print "atom_debug: update_bonds_after_each_event NIM; "\
              "not yet handling %d atoms or singlets in _changed_structure_atoms." % len(_changed_structure_atoms)
        for atm in _changed_structure_atoms.itervalues():
            print "eg this one",atm
    # now caller will do: _changed_structure_atoms.clear()
    return

# end
