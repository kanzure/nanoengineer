# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
move_atoms_and_normalize_bondpoints.py -- post-simulation helper function

@author: Josh, Bruce
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

090112 renamed from move_alist_and_snuggle, moved into new file from chem.py

"""

from geometry.VQT import A

def move_atoms_and_normalize_bondpoints(alist, newPositions): 
    """
    Move the atoms in alist to the new positions in the given array or sequence
    (which must have the same length);
    then for any singlets in alist, correct their positions using Atom.snuggle.

    @warning: it would be wrong to call this on several alists in a row if they 
              might overlap or were connected by bonded atoms, for the same 
              reason that the snuggle has to be done in a separate loop
              (see snuggle docstring for details, re bug 1239).

    @warning: I'm not sure this does all required invals; doesn't do gl_update.
    """
    #bruce 051221 split this out of class Movie so its bug1239 fix can be used
    # in jig_Gamess. [later: Those callers have duplicated code which should be
    # cleaned up.]
    #bruce 090112 renamed from move_alist_and_snuggle
    #todo: refile into a new file in operations package
    assert len(alist) == len(newPositions)
    singlets = []
    for a, newPos in zip(alist, newPositions):
        #bruce 050406 this needs a special case for singlets, in case they are H
        # in the xyz file (and therefore have the wrong distance from their base
        # atom). Rather than needing to know whether or not they were H during 
        # the sim, we can just regularize the singlet-baseatom distance for all
        # singlets. For now I'll just use setposn to set the direction and 
        # snuggle to fix the distance.
        # REVIEW: should it also regularize the distance for H itself? Maybe
        # only if sim value is wildly wrong, and it should also complain. 
        # I won't do this for now.
        a.setposn(A(newPos))
        if a.is_singlet(): # same code as in movend()
            #bruce 051221 to fix bug 1239: do all snuggles after all moves; 
            # see snuggle docstring warning
            singlets.append(a)
        continue
    for a in singlets:
        a.snuggle() # includes a.setposn
    return

# end
