# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
pyrex_test.pyx

Experimental Pyrex code, for testing use of Pyrex in nE-1.

$Id$

For plans and status related to our use of Pyrex, see:

  http://www.nanoengineer-1.net/mediawiki/index.php?title=Integrating_Pyrex_into_the_Build_System

See README-Pyrex for the list of related files and their roles.

"""
__author__ = 'bruce' #k Is this ok in a .pyx file? I don't see why not.

def nbonds(mols):
    """Given a list of chunks, return the number of bonds on all their atoms
    (counting bonds twice if both their atoms are in chunks in the list).
    """
    cdef int tot, nn
    tot = 0
    for i from 0 <= i < len(mols):
        mol = mols[i]
        for atm in mol.atoms.itervalues():
            bonds = atm.bonds
            nn = len(bonds) # compute this separately so we can use C addition below
            tot = tot + nn
    return tot

# end
