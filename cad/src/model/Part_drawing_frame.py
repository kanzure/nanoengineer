# Copyright 2009 Nanorex, Inc.  See LICENSE file for details.
"""
Part_drawing_frame.py -- classes for use as a Part's drawing_frame

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 090218 wrote this in part.py, then split into its own file,
then added features related to DrawingSets.

Bruce 090219 moved everything related to DrawingSets elsewhere.
"""

# (todo: better name?)

# WARNING: The present scheme for Part._drawing_frame would not work
# if multiple threads could draw one Part, or if complex objects in
# a part (e.g. chunks) might be drawn twice in one frame. See comments
# near its use in Chunk.draw for ways we might need to generalize it.
# [bruce 070928/090218]

from utilities.debug import print_compact_stack
from utilities.prefs_constants import indicateOverlappingAtoms_prefs_key

from geometry.NeighborhoodGenerator import NeighborhoodGenerator

import foundation.env as env

# ==

class _Part_drawing_frame_superclass:
    """
    """
    # repeated_bonds_dict lets bonds (or ExternalBondSets) avoid being
    # drawn twice. It maps id(bond) to bond (for any Bond or ExternalBondSet)
    # for all bonds that might otherwise be drawn twice. It is public
    # for use and modification by anything that draws bonds, but only
    # during a single draw call (or a single draw of a subset of the model).
    #
    # Note that OpenGL drawing (draw methods) uses it only for external
    # bonds, but POV-Ray drawing (writepov methods) uses it for all
    # bonds; this is ok even if some writepov methods someday call some
    # draw methods.
    repeated_bonds_dict = None

    # These are for implementing optional indicators about overlapping atoms.
    _f_state_for_indicate_overlapping_atoms = None
    indicate_overlapping_atoms = False

    pass

# ==

class Part_drawing_frame(_Part_drawing_frame_superclass):
    """
    One of these is created whenever drawing all or part of a Part,
    provided Part.before_drawing_model is called as it should be.

    It holds attributes needed during a single draw of one Part
    (or, a draw of a portion of the model for one Part).

    See superclass code comments for documentation of attributes.

    For more info, see docstring of Part.before_drawing_model.
    """
    def __init__(self):

        self.repeated_bonds_dict = {}

        # Note: this env reference may cause undesirable usage tracking,
        # depending on when it occurs. This should cause no harm --
        # only a needless display list remake when the pref is changed.
        self.indicate_overlapping_atoms = \
            env.prefs[indicateOverlappingAtoms_prefs_key]

        if self.indicate_overlapping_atoms:
            TOO_CLOSE = 0.3 # stub, guess; needs to not be true even for
                # bonded atoms, or atoms and their bondpoints,
                # but big enough to catch "visually hard to separate" atoms.
                # (1.0 is far too large; 0.1 is ok but too small to be best.)
                # It would be much better to let this depend on the elements
                # and whether they're bonded, and not hard to implement
                # (each atom could be asked whether it's too close to each
                #  other one, and take all this into account). If we do that,
                # this value should be the largest tolerance for any pair
                # of atoms, and the code that uses this NeighborhoodGenerator
                # should do more filtering on the results. [bruce 080411]
            self._f_state_for_indicate_overlapping_atoms = \
                NeighborhoodGenerator( [], TOO_CLOSE, include_singlets = True )
            pass

        return

    pass

# ==

class fake_Part_drawing_frame(_Part_drawing_frame_superclass):
    """
    Use one of these "between draws" to avoid or mitigate bugs.
    """
    def __init__(self):
        print_compact_stack(
            "warning: fake_Part_drawing_frame is being instantiated: " )
        # done in superclass: self.repeated_bonds_dict = None
            # This is necessary to remove any chance of self surviving
            # for more than one draw of one object (since using an actual
            # dict then would make bonds sometimes fail to be drawn).
            # Client code must tolerate this value.
        return

    pass

# end
