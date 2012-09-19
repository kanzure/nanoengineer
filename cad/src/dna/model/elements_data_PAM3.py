# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
elements_data_PAM3.py -- data for PAM3 pseudoatom elements

@author: Mark
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 071105 revised init code, and split PAM3 and PAM5 data
out of elements_data.py into separate files.
"""

from model.elements_data import tetra4, flat, tetra2, tetra3, onebond
from utilities.constants import MODEL_PAM3

_DIRECTIONAL_BOND_ELEMENTS_PAM3 = ('Ss3', 'Pl3', 'Sj3', 'Se3', 'Sh3', 'Hp3')

# ==

# mark 060129. New default colors for Alpha 7.
_defaultRadiusAndColor = {
    "Ax3" : (4.5, [0.4, 0.4, 0.8]),
    "Ss3" : (4.5, [0.4, 0.8, 0.4]),
    "Sj3" : (4.5, [0.4, 0.8, 0.8]),
    "Pl3" : (3.0, [0.4, 0.1, 0.5]), # (unused)
    "Ae3" : (4.5, [0.1, 0.1, 0.5]),
    "Se3" : (4.5, [0.4, 0.8, 0.4]),
    "Sh3" : (3.0, [0.6, 0.2, 0.6]),
    "Hp3" : (4.5, [0.3, 0.7, 0.3]),
    "Ub3" : (2.3, [0.428, 0.812, 0.808]), #bruce 080117 guess, "light blue"
    "Ux3" : (2.3, [0.428, 0.812, 0.808]), #bruce 080410 stub
    "Uy3" : (2.3, [0.812, 0.428, 0.808]), #bruce 080410 stub
    }

_alternateRadiusAndColor = {}

# Format of _mendeleev: see elements_data.py

_mendeleev = [
    # B-DNA PAM3 v2 pseudo atoms (see also _DIRECTIONAL_BOND_ELEMENTS)
    #
    # Note: the bond vector lists are mainly what we want in length,
    # not necessarily in geometry.
    #
    #bruce 071106: added option dicts; deprecated_to options are good or bad
    # guesses or unfinished; the X ones might be WRONG

    #bruce 080410 added Ux3 and Uy3 and updated all general comments below

    # axis and strand sugar -- these make up all the PAM atoms in a simple PAM3 duplex
    ("Ax3", "PAM3-Axis",           300, 1.0, [[4, 200, tetra4]],     dict(role = 'axis')),
    ("Ss3", "PAM3-Sugar",          301, 1.0, [[3, 210, flat]],       dict(role = 'strand')),

    # PAM3 version of Pl5 (never used, in past, present or future)
    ("Pl3", "PAM3-Phosphate",      302, 1.0, [[2, 210, tetra2]],     dict(role = 'strand', deprecated_to = 'remove')), ### ?? unused atom?

    # deprecated PAM3 elements
    # (btw, some of these say None, 'sp', which is probably wrong --
    #  don't imitate this in new elements) [bruce 080516 comment]
    ("Sj3", "PAM3-Sugar-Junction", 303, 1.0, [[3, 210, flat]],       dict(role = 'strand', deprecated_to = 'Ss3')),
    ("Ae3", "PAM3-Axis-End",       304, 1.0, [[3, 200, tetra3]],     dict(role = 'axis',   deprecated_to = 'Ax3')),
    ("Se3", "PAM3-Sugar-End",      305, 1.0, [[2, 210, tetra2]],     dict(role = 'strand', deprecated_to = 'X')), # might be WRONG
        # WARNING: Se3 is a confusing name, since Se with no '3' or '5' is Selenium (unrelated).
        # Fortunately Se3 is one of the deprecated PAM elements, and there is no Se5. [bruce 080320]
    ("Sh3", "PAM3-Sugar-Hydroxyl", 306, 1.0, [[1, 210, None, 'sp']], dict(role = 'strand', deprecated_to = 'X')), # might be WRONG
    ("Hp3", "PAM3-Hairpin",        307, 1.0, [[2, 210, tetra2]],     dict(role = 'strand', deprecated_to = 'Ss3')),

    # note: 308 and 309 are not used because they correspond to PAM5 atoms
    # with no PAM3 analogue.

    # unpaired base elements:

    # one-atom (besides backbone) unpaired base -- might be used, don't know yet
    ("Ub3", "PAM3-Unpaired-base",  310, 1.0, [[4, 200, tetra4]],     dict(role = 'unpaired-base')),

    # two-atom (besides backbone) unpaired base -- the PAM5 version of this
    # (see elements_data_PAM5.py for an explanation of these element symbols
    #  and names, and something about their purpose)
    # is a recent proposal under active development and is very likely to
    # be used; the PAM3 translation is undecided, and might be a single Ub3,
    # but seems a bit more likely to be a pair of these two, Ux3 and Uy3,
    # because that way their positions will transform properly with no extra
    # work when we rotate a set of atoms, and will define a PAM3+5 baseframe:
    ("Ux3", "PAM3-Unpaired-base-x",  311, 1.0, [[4, 200, tetra4]],     dict(role = 'unpaired-base')), # (likely to be revised)
    ("Uy3", "PAM3-Unpaired-base-y",  312, 1.0, [[4, 200, tetra4]],     dict(role = 'unpaired-base')), # (likely to be revised)

    # note: 313 won't be used unless we decide we want a PAM3-Axis-handle,
    # which is unlikely.

 ]

# Since these are not real chemical bonds, the electron accounting
# need not be based on filled shells.  We just specify that each atom
# provides the same number of electrons as the bond count, and that it
# needs twice that many.

# symbol name
# hybridization name
# formal charge
# number of electrons needed to fill shell
# number of valence electrons provided
# covalent radius (pm)
# geometry (array of vectors, one for each available bond)

#    symb   hyb   FC   need prov c-rad geometry
_PAM3AtomTypeData = [
    ["Ax3", None,  0,    8,  4,  2.00, tetra4],
    ["Ss3", None,  0,    6,  3,  2.10, flat],
    ["Pl3", None,  0,    4,  2,  2.10, tetra2],
    ["Sj3", None,  0,    6,  3,  2.10, flat],
    ["Ae3", None,  0,    6,  3,  2.00, tetra3],
    ["Se3", None,  0,    4,  2,  2.10, tetra2],
    ["Sh3", None,  0,    2,  1,  2.10, None],
    ["Hp3", None,  0,    4,  2,  2.10, tetra2],
    ["Ub3", None,  0,    8,  4,  2.00, tetra4],
    ["Ux3", None,  0,    8,  4,  2.00, tetra4],
    ["Uy3", None,  0,    8,  4,  2.00, tetra4],
]

# ==

def init_PAM3_elements( periodicTable):
    periodicTable.addElements( _mendeleev,
                               _defaultRadiusAndColor,
                               _alternateRadiusAndColor,
                               _PAM3AtomTypeData,
                               _DIRECTIONAL_BOND_ELEMENTS_PAM3,
                               default_options = dict(pam = MODEL_PAM3)
                              )
    return

# end
