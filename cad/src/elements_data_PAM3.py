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
    "Ax3" : (4.5, [0.4, 0.4, 0.8]),
    "Ss3" : (4.5, [0.4, 0.8, 0.4]),
    "Sj3" : (4.5, [0.4, 0.8, 0.8]),
    "Pl3" : (3.0, [0.4, 0.1, 0.5]), # (unused)
    "Ae3" : (4.5, [0.1, 0.1, 0.5]),
    "Se3" : (4.5, [0.4, 0.8, 0.4]),
    "Sh3" : (3.0, [0.6, 0.2, 0.6]),
    "Hp3" : (4.5, [0.3, 0.7, 0.3]),
    }
  
_altRad_Color = {}
                 
# Format of _mendeleev: see elements_data.py

_mendeleev = [
    # B-DNA PAM3 v2 pseudo atoms (see also _DIRECTIONAL_BOND_ELEMENTS)
    # Note: the bond vector lists are mainly what we want in length,
    # not necessarily in geometry.
    #
    #bruce 071106: added option dicts; deprecated_to options are good or bad guesses or unfinished; the X ones might be WRONG

    ("Ax3", "PAM3-Axis",           300, 1.0, [[4, 200, tetra4]],     dict(role = 'axis')),
    ("Ss3", "PAM3-Sugar",          301, 1.0, [[3, 210, flat]],       dict(role = 'strand')),
    
    ("Pl3", "PAM3-Phosphate",      302, 1.0, [[2, 210, tetra2]],     dict(role = 'strand', deprecated_to = 'remove')), ### ?? unused atom?
    
    ("Sj3", "PAM3-Sugar-Junction", 303, 1.0, [[3, 210, flat]],       dict(role = 'strand', deprecated_to = 'Ss3')),
    ("Ae3", "PAM3-Axis-End",       304, 1.0, [[3, 200, tetra3]],     dict(role = 'axis',   deprecated_to = 'Ax3')),
    ("Se3", "PAM3-Sugar-End",      305, 1.0, [[2, 210, tetra2]],     dict(role = 'strand', deprecated_to = 'X')), # might be WRONG
    ("Sh3", "PAM3-Sugar-Hydroxyl", 306, 1.0, [[1, 210, None, 'sp']], dict(role = 'strand', deprecated_to = 'X')), # might be WRONG
    ("Hp3", "PAM3-Hairpin",        307, 1.0, [[2, 210, tetra2]],     dict(role = 'strand', deprecated_to = 'Ss3'))
 ]

# ==

def init_PAM3_elements( periodicTable):
    periodicTable.addElements( _mendeleev, _defaultRad_Color, _altRad_Color,
                               _DIRECTIONAL_BOND_ELEMENTS_PAM3,
                               default_options = dict(pam = 'PAM3')
                              )
    return

# end
