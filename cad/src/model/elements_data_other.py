# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
elements_data_other.py -- data for miscellaneous kinds of elements
which are neither chemical nor PAM pseudoatoms
(for example, virtual site indicators)

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details. 

See also: the "handle" Ah5, which is defined as a PAM5 pseudoelement
for code-convenience reasons.
"""

## from model.elements_data import tetra4, flat, tetra2, onebond

_DIRECTIONAL_BOND_ELEMENTS_OTHER = ()

# ==

_defaultRadiusAndColor = {
    "Vs0" : (1.0, [0.8, 0.8, 0.8]), #bruce 080515 guess, "very light gray"
    }
  
_alternateRadiusAndColor = {
    }
                 
# Format of _mendeleev: see elements_data.py

_mendeleev = [
    # For indicators of virtual sites.
    # (We might add more, whose element names correspond to
    #  virtual site pattern names, but which have the same role value.)
    ("Vs0", "virtual-site",    400, 1.0, None, dict(role = 'virtual-site')),

 ]

# ==

def init_other_elements( periodicTable):
    periodicTable.addElements( _mendeleev, _defaultRadiusAndColor, _alternateRadiusAndColor,
                               _DIRECTIONAL_BOND_ELEMENTS_OTHER,
                               default_options = dict()
                              )
    return

# end
