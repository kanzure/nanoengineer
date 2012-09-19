# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
NeighborhoodGenerator.py -- linear time way to find overlapping or nearby atoms.

@author: Will
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Will wrote this in bonds.py for use in bond inference.

Bruce 080411 moved it into its own module, classifying it
as geometry (i.e. moving it into that source package)
since it's essentially purely geometric (and could easily
be generalized to be entirely so) -- all it assumes about
"atoms" is that they have a few methods like .posn()
and .is_singlet(), and it needs no imports from model.
"""

import struct

from numpy.oldnumeric import floor

from geometry.VQT import vlen

# ==


# This is an order(N) operation that produces a function which gets a
# list of potential neighbors in order(1) time. This is handy for
# inferring bonds for PDB files that lack any bonding information.
class NeighborhoodGenerator:
    """
    Given a list of atoms and a radius, be able to quickly take a
    point and generate a neighborhood, which is a list of the atoms
    within that radius of the point.

    Reading in the list of atoms is done in O(n) time, where n is the
    number of atoms in the list. Generating a neighborhood around a
    point is done in O(1) time. So this is a pretty efficient method
    for finding neighborhoods, especially if the same generator can
    be used many times.
    """
    def __init__(self, atomlist, maxradius, include_singlets = False):
        self._buckets = { }
        self._oldkeys = { }
        self._maxradius = 1.0 * maxradius
        self.include_singlets = include_singlets
        for atom in atomlist:
            self.add(atom)

    def _quantize(self, vec):
        """
        Given a point in space, partition space into little cubes
        so that when the time comes, it will be quick to locate and
        search the cubes right around a point.
        """
        maxradius = self._maxradius
        return (int(floor(vec[0] / maxradius)),
                int(floor(vec[1] / maxradius)),
                int(floor(vec[2] / maxradius)))

    def add(self, atom, _pack = struct.pack):
        buckets = self._buckets
        if self.include_singlets or not atom.is_singlet():
            # The keys of the _buckets dictionary are 12-byte strings.
            # Comparing them when doing lookups should be quicker than
            # comparisons between tuples of integers, so dictionary
            # lookups will go faster.
            i, j, k = self._quantize(atom.posn())
            key = _pack('lll', i, j, k)
            buckets.setdefault(key, []).append(atom)
            self._oldkeys[atom.key] = key

    def atom_moved(self, atom):
        """
        If an atom has been added to a neighborhood generator and
        is later moved, this method must be called to refresh the
        generator's position information. This only needs to be done
        during the useful lifecycle of the generator.
        """
        oldkey = self._oldkeys[atom.key]
        self._buckets[oldkey].remove(atom)
        self.add(atom)

    def region(self, center, _pack = struct.pack):
        """
        Given a position in space, return the list of atoms that
        are within the neighborhood radius of that position.
        """
        buckets = self._buckets
        def closeEnough(atm, radius = self._maxradius):
            return vlen(atm.posn() - center) < radius
        lst = [ ]
        x0, y0, z0 = self._quantize(center)
        for x in range(x0 - 1, x0 + 2):
            for y in range(y0 - 1, y0 + 2):
                for z in range(z0 - 1, z0 + 2):
                    # keys are 12-byte strings, see rationale above
                    key = _pack('lll', x, y, z)
                    if buckets.has_key(key):
                        lst += filter(closeEnough, buckets[key])
        return lst

    def remove(self, atom):
        key = self._quantize(atom.posn())
        try:
            self._buckets[key].remove(atom)
        except:
            pass

    pass # end of class NeighborhoodGenerator

# end
