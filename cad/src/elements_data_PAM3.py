# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
elements_data_PAM3.py -- data for PAM3 pseudoatom elements

@author: Mark
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details. 

History:

Bruce 071105 revised init code, and split PAM3 and PAM5 data
out of elements_data.py into separate files.
"""

from elements_data import tetra4, flat, tetra2, tetra3

_DIRECTIONAL_BOND_ELEMENTS_PAM3 = ('Ss3', 'Pl3', 'Sj3', 'Se3', 'Sh3', 'Hp3')

# ==

# mark 060129. New default colors for Alpha 7.
_defaultRad_Color = {
    "Ax3" : (4.5, [0.4, 0.4, 0.8]),    # PAM3 DNA pseudo atom
    "Ss3" : (4.5, [0.4, 0.8, 0.4]),    # PAM3 DNA pseudo atom
    "Sj3" : (4.5, [0.4, 0.8, 0.8]),    # PAM3 DNA pseudo atom
    "Pl3" : (3.0, [0.4, 0.1, 0.5]),    # PAM3 DNA pseudo atom (unused)
    "Ae3" : (4.5, [0.1, 0.1, 0.5]),    # PAM3 DNA pseudo atom
    "Se3" : (4.5, [0.4, 0.8, 0.4]),    # PAM3 DNA pseudo atom
    "Sh3" : (3.0, [0.6, 0.2, 0.6]),    # PAM3 DNA pseudo atom
    "Hp3" : (4.5, [0.3, 0.7, 0.3]),    # PAM3 DNA pseudo atom
    }
  
_altRad_Color = {}
                 
# Format of _mendeleev: see elements_data.py

_mendeleev = [
    # B-DNA PAM3 v2 pseudo atoms (see also _DIRECTIONAL_BOND_ELEMENTS)
    ("Ax3", "PAM3-Axis", 300, 1.0, [[4, 200, tetra4]]),
    ("Ss3", "PAM3-Sugar", 301, 1.0, [[3, 210, flat]]),
    ("Pl3", "PAM3-Phosphate", 302, 1.0, [[2, 210, tetra2]]),
    ("Sj3", "PAM3-Sugar-Junction", 303, 1.0, [[3, 210, flat]]),
    ("Ae3", "PAM3-Axis-End", 304, 1.0, [[3, 200, tetra3]]),
    ("Se3", "PAM3-Sugar-End", 305, 1.0, [[2, 210, tetra2]]),
    ("Sh3", "PAM3-Sugar-Hydroxyl", 306, 1.0, [[1, 210, None, 'sp']]),
    ("Hp3", "PAM3-Hairpin", 307, 1.0, [[2, 210, tetra2]])
 ]

# ==

def init_PAM3_elements( periodicTable):
    periodicTable.addElements( _mendeleev, _defaultRad_Color, _altRad_Color,
                               _DIRECTIONAL_BOND_ELEMENTS_PAM3 )
    return

# end
