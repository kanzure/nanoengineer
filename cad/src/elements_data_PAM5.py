# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
elements_data_PAM5.py -- data for PAM5 pseudoatom elements

@author: Mark, Eric D
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

Bruce 071105 revised init code, and split PAM3 and PAM5 data
out of elements_data.py into separate files.

Bruce 080108 added Gv5 for use in Eric D's forthcoming PAM5 revision.
"""

from elements_data import tetra4, flat, tetra2

_DIRECTIONAL_BOND_ELEMENTS_PAM5 = ('Ss5', 'Pl5', 'Sj5', 'Pe5', 'Sh5', 'Hp5')

# ==

# mark 060129. New default colors for Alpha 7.
_defaultRad_Color = {
    "Ax5" : (5.0, [0.4, 0.4, 0.8]),
    "Ss5" : (4.0, [0.4, 0.8, 0.4]),
    "Pl5" : (3.2, [0.4, 0.1, 0.5]),
    "Sj5" : (4.0, [0.4, 0.8, 0.8]),
    "Ae5" : (3.5, [0.4, 0.4, 0.8]),
    "Pe5" : (3.0, [0.4, 0.1, 0.5]),
    "Sh5" : (2.5, [0.4, 0.8, 0.4]),
    "Hp5" : (4.0, [0.3, 0.7, 0.3]),
    "Gv5" : (5.0, [156./255, 83./255, 8./255]), #bruce 080108
    "Gr5" : (5.0, [156./255, 83./255, 8./255]),
    "Ub5" : (2.5, [0.428, 0.812, 0.808]), #bruce 080117 guess, "light blue"
    }
  
_altRad_Color = {
    }
                 
# Format of _mendeleev: see elements_data.py

_mendeleev = [
    # B-DNA PAM5 pseudo atoms (see also _DIRECTIONAL_BOND_ELEMENTS)
    # Note: the bond vector lists are mainly what we want in length,
    # not necessarily in geometry.
    #
    #bruce 070415: End->Hydroxyl per Eric D email, in "Sh5" == "PAM5-Sugar-Hydroxyl"
    #bruce 071106: added option dicts; deprecated_to options are good guesses but are untested
    
    ("Ax5", "PAM5-Axis",           200, 1.0, [[4, 200, tetra4]],     dict(role = 'axis')), # todo: convert to Gv5, moving it as you do
    
    ("Ss5", "PAM5-Sugar",          201, 1.0, [[3, 210, flat]],       dict(role = 'strand')),
    ("Pl5", "PAM5-Phosphate",      202, 1.0, [[2, 210, tetra2]],     dict(role = 'strand')),
    
    ("Sj5", "PAM5-Sugar-Junction", 203, 1.0, [[3, 210, flat]],       dict(role = 'strand', deprecated_to = 'Ss5')),
    ("Ae5", "PAM5-Axis-End",       204, 1.0, [[1, 200, None, 'sp']], dict(role = 'axis',   deprecated_to = 'X')),
    ("Pe5", "PAM5-Phosphate-End",  205, 1.0, [[1, 210, None, 'sp']], dict(role = 'strand', deprecated_to = 'Pl')), #bruce 080129 X->Pl; UNCONFIRMED
    ("Sh5", "PAM5-Sugar-Hydroxyl", 206, 1.0, [[1, 210, None, 'sp']], dict(role = 'strand', deprecated_to = 'X')),
    ("Hp5", "PAM5-Hairpin",        207, 1.0, [[2, 210, tetra2]],     dict(role = 'strand', deprecated_to = 'Ss5')), # REVIEW: Ss or Pl?

    ("Gv5", "PAM5-Major-Groove",   208, 1.0, [[4, 200, tetra4]],     dict(role = 'axis')), #bruce 080108
    ("Gr5", "PAM5-Major-Groove-End",209,1.0, [[3, 210, flat]],       dict(role = 'axis',   deprecated_to = 'Gv5')),

    ("Ub5", "PAM5-Unpaired-base",  210, 1.0, [[4, 200, tetra4]],     dict(role = 'unpaired-base')), # (likely to be revised)
 ]

# ==

def init_PAM5_elements( periodicTable):
    periodicTable.addElements( _mendeleev, _defaultRad_Color, _altRad_Color,
                               _DIRECTIONAL_BOND_ELEMENTS_PAM5,
                               default_options = dict(pam = 'PAM5')
                              )
    return

# end
