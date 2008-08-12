# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
elements_data.py -- data for periodic table of elements
(for chemical elements and Singlet -- see other files for PAM pseudoatoms)

@author: Josh
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

History:

Initially by Josh as part of chem.py.

Bruce 041221 split elements.py out of chem.py,
and (around then) added support for alternate color/radius tables.

Bruce 050510 made some changes for "atomtypes" with their own bonding patterns.

Bruce 071101 split elements_data.py out of elements.py.

Bruce 071105 revised init code, and split PAM3 and PAM5 data into separate files.
"""

from geometry.VQT import V, A, norm
from utilities.constants import DIAMOND_BOND_LENGTH

_DIRECTIONAL_BOND_ELEMENTS_chemical = ('X',) # mark 071014

# ==

# the formations of bonds -- standard offsets

# (note: these are public symbols that can also be used in
#  element data files for pseudoatoms)

uvec = norm(V(1,1,1))
tetra4 = uvec * A([[1,1,1], [-1,1,-1], [-1,-1,1], [1,-1,-1]])
tetra3 = uvec * A([[-1,1,-1], [-1,-1,1], [1,-1,-1]])
oxy2 = A([[-1,0,0], [0.2588, -0.9659, 0]])
tetra2 = A([[-1,0,0], [0.342, -0.9396, 0]])
straight = A([[-1,0,0], [1,0,0]])
flat = A([[-0.5,0.866,0], [-0.5,-0.866,0], [1,0,0]])
onebond = A([[1,0,0]]) # for use with valence-1 elements

# mark 060129. New default colors for Alpha 7.
_defaultRadiusAndColor = {
    "X": (1.1,  [0.8, 0.0, 0.0]),
    "H" : (1.2,  [0.78, 0.78, 0.78]),
    "He" : (1.4,  [0.42, 0.45, 0.55]),
    "Li" : (4.0,  [0.0, 0.5, 0.5]),
    "Be" : (3.0,  [0.98, 0.67, 1.0]),
    "B" : (2.0,  [0.2, 0.2, 0.59]),
    "C" : (1.84, [0.39, 0.39, 0.39]),
    "N" : (1.55, [0.12, 0.12, 0.39]),
    "O" : (1.74, [0.5, 0.0, 0.0]),
    "F" : (1.65, [0.0, 0.39, 0.2]),
    "Ne" : (1.82, [0.42, 0.45, 0.55]),
    "Na" : (4.0,  [0.0, 0.4, 0.4]),
    "Mg" : (3.0,  [0.88, 0.6, 0.9]),
    "Al" : (2.5,  [0.5, 0.5, 1.0]),
    "Si" : (2.25, [0.16, 0.16, 0.16]),
    "P" : (2.11, [0.33, 0.08, 0.5]),
    "S" : (2.11, [0.86, 0.59, 0.0]),
    "Cl" : (2.03, [0.29, 0.39, 0.0]),
    "Ar" : (1.88, [0.42, 0.45, 0.55]),
    "K" : (5.0,  [0.0, 0.3, 0.3]),
    "Ca" : (4.0,  [0.79, 0.55, 0.8]),
    "Sc" : (3.7,  [0.417, 0.417, 0.511]),
    "Ti" : (3.5,  [0.417, 0.417, 0.511]),
    "V" : (3.3,  [0.417, 0.417, 0.511]),
    "Cr" : (3.1,  [0.417, 0.417, 0.511]),
    "Mn" : (3.0,  [0.417, 0.417, 0.511]),
    "Fe" : (3.0, [0.417, 0.417, 0.511]),
    "Co" : (3.0,  [0.417, 0.417, 0.511]),
    "Ni" : (3.0,  [0.417, 0.417, 0.511]),
    "Cu" : (3.0,  [0.417, 0.417, 0.511]),
    "Zn" : (2.9,  [0.417, 0.417, 0.511]),
    "Ga" : (2.7,  [0.6, 0.6, 0.8]),
    "Ge" : (2.5,  [0.4, 0.45, 0.1]),
    "As" : (2.2,  [0.6, 0.26, 0.7]),
    "Se" : (2.1,  [0.78, 0.31, 0.0]),
    "Br" : (2.0,  [0.0, 0.4, 0.3]),
    "Kr" : (1.9,  [0.42, 0.45, 0.55]),
    "Sb" : (2.2,  [0.6, 0.26, 0.7]),
    "Te" : (2.1,  [0.9, 0.35, 0.0]),
    "I" : (2.0,  [0.0, 0.5, 0.0]),
    "Xe" : (1.9,  [0.4, 0.45, 0.55]),
    }
  
_alternateRadiusAndColor = {
    "Al" : (2.050,),
    "As" : (2.050,),
    "B" :  (1.461,),
    "Be" :  (1.930,),
    "Br" :  ( 1.832,),
    "C" : (1.431, [0.4588, 0.4588, 0.4588]),
    "Ca" :  ( 1.274, ),
    "Cl" :  ( 1.688,),
    "Co" :  ( 1.970, ),
    "Cr" :  ( 2.150,),
    "Cu" :  ( 1.870,),
    "F" :  ( 1.293,),
    "Fe" :  ( 2.020,),
    "Ga" :  ( 2.300,),
    "Ge" : (1.980,),
    "H" :  (1.135, [1.0, 1.0, 1.0]),
    "I" :   ( 1.967,),
    "K" :  ( 1.592,),
    "Li" :  (  0.971,),
    "Mg" :  ( 1.154,),
    "Mn" :  (1.274,),
    "N" :  ( 1.392,),
    "Na" :  (1.287,),
    "Ni" :  ( 1.920,),
    "O" :  (1.322,),
    "P" :  ( 1.784,),
    "S" :  (1.741,),
    "Sb" :  ( 2.200,),
    "Se" :  (  1.881,),
    "Si" :  ( 1.825, [0.4353, 0.3647, 0.5216]),
    "Ti" :  ( 2.300,)
    }
                 
# Format of _mendeleev:
# Symbol, Element Name, NumberOfProtons, atomic mass in 10-27 kg,
# then a list of atomtypes, each of which is described by
# [ open bonds, covalent radius (pm), atomic geometry, hybridization ]
# (bruce adds: not sure about cov rad units; table values are 100 times this comment's values)

# covalent radii from Gamess FF [= means double bond, + means triple bond]
# Biassed to make bonds involving carbon come out right
## Cl - 1.02
## H -- 0.31
## F -- 0.7
## C -- 0.77 [compare to DIAMOND_BOND_LENGTH (1.544) in constants.py [bruce 051102 comment]]
#### 1.544 is a bond length, double the covalent radius, so pretty consistent - wware 060518
## B -- 0.8
## S -- 1.07
## P -- 1.08
## Si - 1.11
## O -- 0.69
## N -- 0.73

## C= - 0.66
## O= - 0.6
## N= - 0.61

## C+ - 0.6
## N+ - 0.56

# numbers changed below to match -- Josh 13Oct05
# [but this is problematic; see the following string-comment -- bruce 051014]
"""
[bruce 051014 revised the comments above, and adds:]

Note that the covalent radii below are mainly used for two things: drawing bond
stretch indicators, and depositing atoms. There is a basic logic bug for both
uses: covalent radii ought to depend on bond type, but the table below is in
terms of atom type, and the atomtype only tells you which combinations of bond
types would be correct on an atom, not which bond is which. (And at the time an
atom is deposited, which bond is which is often not known, especially by the
current code which always makes single bonds.)

This means that no value in the table below is really correct (except for
atomtypes which imply all bonds should have the same type, i.e. for each
element's first atomtype), and even if we just want to pick the best compromise
value, it's not clear how best to do that.

For example, a good choice for C(sp2) covalent radius (given that it's required
to be the same for all bonds) might be one that would position the C between
its neighbors (and position the neighbors themselves, if they are subsequently
deposited) so that when its bond types are later changed to one of the legal
combos (112, 1aa, or ggg), and assuming its position is then adjusted, that the
neighbor atom positions need the least adjustment. This might be something like
an average of the bond lengths... so it's good that 71 (in the table below) is
between the single and double bond values of 77 and 66 (listed as 0.77 and 0.66
in the comment above), though I'm not aware of any specific formula having been
used to get 71. Perhaps we should adjust this value to match graphite (or
buckytubes if those are different), but this has probably not been done.

The hardest case to accomodate is the triple bond radius (C+ in the table
above), since this exists on C(sp) when one bond is single and one is triple
(i.e. -C+), so the table entry for C(sp) could be a compromise between those
values, but might as well instead just be the double bond value, since =C= is
also a legal form for C(sp). The result is that there is no place in this table
to put the C+ value.
"""
_mendeleev = [
    ("X",  "Singlet",      0,   0.001,  [[1, 0, None, 'sp']]), #bruce 050630 made X have atomtype name 'sp'; might revise again later
    ("H",  "Hydrogen",     1,   1.6737, [[1, 31, onebond]]),
    ("He", "Helium",       2,   6.646,  None),
    ("Li", "Lithium",      3,  11.525,  [[1, 152, None]]),
    ("Be", "Beryllium",    4,  14.964,  [[2, 114, None]]),
    ("B",  "Boron",        5,  17.949,  [[3, 80, flat, 'sp2']]), #bruce 050706 added 'sp2' name, though all bonds are single
    ("C",  "Carbon",       6,  19.925,  [[4, DIAMOND_BOND_LENGTH / 2 * 100, tetra4, 'sp3'],
                                      #bruce 051102 replaced 77 with constant expr, which evals to 77.2
                                         [3, 71, flat, 'sp2'],
                                         [2, 66, straight, 'sp'], # (this is correct for =C=, ie two double bonds)
                                      ## [1, 60, None] # what's this? I don't know how it could bond... removing it. [bruce 050510]
                                        ]),
    ("N",  "Nitrogen",     7,  23.257,  [[3, 73, tetra3, 'sp3'],
                                         [2, 61, flat[:2], 'sp2'], # bruce 050630 replaced tetra2 with flat[:2]
                                       # josh 0512013 made this radius 61, but this is only correct for a double bond,
                                       # whereas this will have one single and one double bond (or two aromatic bonds),
                                       # so 61 is probably not the best value here... 67 would be the average of single and double.
                                       # [bruce 051014]
                                         [1, 56, onebond, 'sp'],
                                         [3, 62, flat, 'sp2(graphitic)'],
                                       # this is just a guess! (for graphitic N, sp2(??) with 3 single bonds) (and the 62 is made up)
                                        ]),
    ("O",  "Oxygen",       8,  26.565,  [[2, 69, oxy2, 'sp3'],
                                         [1, 60, onebond, 'sp2']]), # sp2?
    ("F",  "Fluorine",     9,  31.545,  [[1, 70, onebond]]),
    ("Ne", "Neon",        10,  33.49,   None),
    ("Na", "Sodium",      11,  38.1726, [[1, 186, None]]),
    ("Mg", "Magnesium",   12,  40.356,  [[2, 160, None]]),
    ("Al", "Aluminum",    13,  44.7997, [[3, 143, flat]]),
    ("Si", "Silicon",     14,  46.6245, [[4, 111, tetra4]]),
    ("P",  "Phosphorus",  15,  51.429,  [[3, 108, tetra3, 'sp3'],
                                         [5, 100, tetra4, 'sp3(phosphate)']]), # 100 is made up
    ("S",  "Sulfur",      16,  53.233,  [[2, 107, tetra2, 'sp3'],
                                         [1, 88, onebond, 'sp2']]), #bruce 050706 added this, and both names; length chgd by Josh
    ("Cl", "Chlorine",    17,  58.867,  [[1, 102, onebond]]),
    ("Ar", "Argon",       18,  66.33,   None),
    ("K",  "Potassium",   19,  64.9256, [[1, 231, None]]),
    ("Ca", "Calcium",     20,  66.5495, [[2, 197, tetra2]]),
    ("Sc", "Scandium",    21,  74.646,  [[3, 160, tetra3]]),
    ("Ti", "Titanium",    22,  79.534,  [[4, 147, tetra4]]),
    ("V",  "Vanadium",    23,  84.584,  [[5, 132, None]]),
    ("Cr", "Chromium",    24,  86.335,  [[6, 125, None]]),
    ("Mn", "Manganese",   25,  91.22,   [[7, 112, None]]),
    ("Fe", "Iron",        26,  92.729,  [[3, 124, None]]),
    ("Co", "Cobalt",      27,  97.854,  [[3, 125, None]]),
    ("Ni", "Nickel",      28,  97.483,  [[3, 125, None]]),
    ("Cu", "Copper",      29, 105.513,  [[2, 128, None]]),
    ("Zn", "Zinc",        30, 108.541,  [[2, 133, None]]),
    ("Ga", "Gallium",     31, 115.764,  [[3, 135, None]]),
    ("Ge", "Germanium",   32, 120.53,   [[4, 122, tetra4]]),
    ("As", "Arsenic",     33, 124.401,  [[5, 119, tetra3]]),
    ("Se", "Selenium",    34, 131.106,  [[6, 120, tetra2]]),
    ("Br", "Bromine",     35, 132.674,  [[1, 119, onebond]]),
    ("Kr", "Krypton",     36, 134.429,  None),

    ("Sb", "Antimony",    51, 124.401,  [[3, 119, tetra3]]),
    ("Te", "Tellurium",   52, 131.106,  [[2, 120, tetra2]]),
    ("I",  "Iodine",      53, 132.674,  [[1, 119, onebond]]),
    ("Xe", "Xenon",       54, 134.429,  None),
 ]

# How to add a new hybridization type for an element:
#
# First, add it to the table below (or one of the similar ones
# wherever the element definition is found).  If an element has more
# than one hybridization, the hybridization name must be specified so
# they can be distinguished.  In general, hybridization names should
# start with the string "sp", possibly followed by a digit 2 or 3.  In
# general, the formal charge plus the number of electrons provided
# should equal the group number of the element.  The total bond order
# will be the electrons needed minus the electrons provided (this is
# the number of electrons shared with other atoms).  The number of
# individual bonds to distinct atoms is specified by the length of the
# geometry array.  The geometry array specifies how these bonds are
# arranged around the central atom.
#
# Next, check _init_permitted_v6_list() in class AtomType in
# atomtypes.py.  Make any adjustments necessary so that the correct
# list of available bond types is generated for the new hybridization.
#
# Next, add the new hybridization to the UI in PM_ElementChooser.py.
# See the comments there for how to do that.

# symbol name
# hybridization name
# formal charge
# number of electrons needed to fill shell
# number of valence electrons provided
# covalent radius (pm)
# geometry (array of vectors, one for each available bond)

#    symb  hybridization     FC   need prov c-rad geometry
_chemicalAtomTypeData = [
    ["X",  'sp',              0,    2,  1,  0.00, onebond],
    ["H",  None,              0,    2,  1,  0.31, onebond],
    ["He", None,              0,    2,  2,  0.00, None],
    ["Li", None,              0,    2,  1,  1.52, None],
    ["Be", None,              0,    4,  2,  1.14, None],
    ["B",  None,              0,    6,  3,  0.80, flat],
    ["C",  'sp3',             0,    8,  4,  DIAMOND_BOND_LENGTH / 2, tetra4],
    ["C",  'sp2',             0,    8,  4,  0.71, flat],
    ["C",  'sp',              0,    8,  4,  0.66, straight],
    ["N",  'sp3',             0,    8,  5,  0.73, tetra3],
    ["N",  'sp2',             0,    8,  5,  0.61, flat[:2]],
    ["N",  'sp',              0,    8,  5,  0.56, onebond],
    ["N",  'sp2(graphitic)',  0,    8,  5,  0.62, flat],
    ["O",  'sp3',             0,    8,  6,  0.69, oxy2],
    ["O",  'sp2',             0,    8,  6,  0.60, onebond],
    ["O",  'sp2(-)',         -1,    8,  7,  0.60, onebond], # bogus rcovalent
    ["O",  'sp2(-.5)',     -0.5,    8,6.5,  0.60, onebond], # bogus rcovalent
    ["F",  None,              0,    8,  7,  0.70, onebond],
    ["Ne", None,              0,    8,  8,  0.00, None],
    ["Na", None,              0,    2,  1,  1.86, None],
    ["Mg", None,              0,    4,  2,  1.60, None],
    ["Al", None,              0,    6,  3,  1.43, flat],
    ["Si", None,              0,    8,  4,  1.11, tetra4],
    ["P",  'sp3',             0,    8,  5,  1.08, tetra3],
    ["P",  'sp3(phosphate)',  0,   10,  5,  1.00, tetra4], # bogus rcovalent
    ["S",  'sp3',             0,    8,  6,  1.07, tetra2],
    ["S",  'sp2',             0,    8,  6,  0.88, onebond],
    ["Cl", None,              0,    8,  7,  1.02, onebond],
    ["Ar", None,              0,    8,  8,  0.00, None],
    ["K",  None,              0,    2,  1,  2.31, None],
    ["Ca", None,              0,    4,  2,  1.97, tetra2],
    ["Sc", None,              0,    6,  3,  1.60, tetra3],
    ["Ti", None,              0,    8,  4,  1.47, tetra4],
    ["V",  None,              0,   10,  5,  1.32, None],
    ["Cr", None,              0,   12,  6,  1.25, None],
    ["Mn", None,              0,   14,  7,  1.12, None],
    ["Fe", None,              0,    6,  3,  1.24, None],
    ["Co", None,              0,    6,  3,  1.25, None],
    ["Ni", None,              0,    6,  3,  1.25, None],
    ["Cu", None,              0,    4,  2,  1.28, None],
    ["Zn", None,              0,    4,  2,  1.33, None],
    ["Ga", None,              0,    6,  3,  1.35, None],
    ["Ge", None,              0,    8,  4,  1.22, tetra4],
    ["As", None,              0,    8,  5,  1.19, tetra3],
    ["Se", None,              0,    8,  6,  1.20, tetra2],
    ["Br", None,              0,    8,  7,  1.19, onebond],
    ["Kr", None,              0,    8,  8,  0.00, None],

    ["Sb", None,              0,    8,  5,  1.19, tetra3],
    ["Te", None,              0,    8,  6,  1.20, tetra2],
    ["I",  None,              0,    8,  7,  1.19, onebond],
    ["Xe", None,              0,    8,  8,  0.00, None],
]

# ==

def init_chemical_elements( periodicTable):
    periodicTable.addElements( _mendeleev,
                               _defaultRadiusAndColor,
                               _alternateRadiusAndColor,
                               _chemicalAtomTypeData,
                               _DIRECTIONAL_BOND_ELEMENTS_chemical )
    return

# end


