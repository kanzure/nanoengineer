# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
elements_data_PAM5.py -- data for PAM5 pseudoatom elements

@author: Mark, Eric D
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details. 

History:

Bruce 071105 revised init code, and split PAM3 and PAM5 data
out of elements_data.py into separate files.
"""

from elements_data import tetra4, flat, tetra2

_DIRECTIONAL_BOND_ELEMENTS_PAM5 = ('Ss5', 'Pl5', 'Sj5', 'Pe5', 'Sh5', 'Hp5')

# ==

# mark 060129. New default colors for Alpha 7.
_defaultRad_Color = {
    "Ax5" : (5.0, [0.4, 0.4, 0.8]),    # PAM5 DNA pseudo atom
    "Ss5" : (4.0, [0.4, 0.8, 0.4]),    # PAM5 DNA pseudo atom
    "Sj5" : (4.0, [0.4, 0.8, 0.8]),    # PAM5 DNA pseudo atom
    "Pl5" : (3.2, [0.4, 0.1, 0.5]),    # PAM5 DNA pseudo atom
    "Ae5" : (3.5, [0.4, 0.4, 0.8]),    # PAM5 DNA pseudo atom
    "Pe5" : (3.0, [0.4, 0.1, 0.5]),    # PAM5 DNA pseudo atom
    "Sh5" : (2.5, [0.4, 0.8, 0.4]),    # PAM5 DNA pseudo atom
    "Hp5" : (4.0, [0.3, 0.7, 0.3]),    # PAM5 DNA pseudo atom
    }
  
_altRad_Color = {
    }
                 
# Format of _mendeleev: see elements_data.py

_mendeleev = [
    # B-DNA PAM5 pseudo atoms (see also _DIRECTIONAL_BOND_ELEMENTS)
    ("Ax5", "PAM5-Axis", 200, 1.0, [[4, 200, tetra4]]),
    ("Ss5", "PAM5-Sugar", 201, 1.0, [[3, 210, flat]]),
    ("Pl5", "PAM5-Phosphate", 202, 1.0, [[2, 210, tetra2]]),
    ("Sj5", "PAM5-Sugar-Junction", 203, 1.0, [[3, 210, flat]]),
    ("Ae5", "PAM5-Axis-End", 204, 1.0, [[1, 200, None, 'sp']]),
    ("Pe5", "PAM5-Phosphate-End", 205, 1.0, [[1, 210, None, 'sp']]),
    ("Sh5", "PAM5-Sugar-Hydroxyl", 206, 1.0, [[1, 210, None, 'sp']]), #bruce 070415: End->Hydroxyl per ED email
    ("Hp5", "PAM5-Hairpin", 207, 1.0, [[2, 210, tetra2]]),
 ]

# ==

def init_PAM5_elements( periodicTable):
    periodicTable.addElements( _mendeleev, _defaultRad_Color, _altRad_Color,
                               _DIRECTIONAL_BOND_ELEMENTS_PAM5 )
    return

# end
