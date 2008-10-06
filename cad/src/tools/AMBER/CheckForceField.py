#!/usr/bin/env python

"""
Reads a set of ...nb.itp, ...bon.itp, and .rtp files representing a
GROMACS force field, and the info for translating a .pdb file into a
GROMACS .top file.  Where the .rtp file specifies a named set of
torsion parameters, those parameters are checked against the
parameters which would result from a 4-atom match of the torsion terms
defined in the ...bon.itp file.

The ...nb.itp file contains the following section:

[ atomtypes ]

The ...bon.itp file contains the following sections:

[ bondtypes ]
[ angletypes ]
[ dihedraltypes ]

The .rtp file contains the following sections nested within each
molecule section:

[ **molecule_name** ]
 [ atoms ]
 [ bonds ]
 [ dihedrals ]
 [ impropers ]

The terms we want to check are defined in the [ dihedrals ] and 
[ impropers ] sections of the .rtp file.  These reference specific atom
names which are defined for each residue in a .pdb file.  The [ atoms ]
section maps these pdb atom names into AMBER numeric atom types of
the form 'amber99_XX'.  The [ atomtypes ] section of the ...nb.itp
file is used to translate these into symbolic AMBER atom types, which
appear in the [ dihedraltypes ] sections of the ...bon.itp file.

The named parameters appear as #defines in the ...bon.itp file, but
these have been extracted into dictionaries which are hard-coded here.
"""

import sys
from ParseINI import ParseINI

def canonicalizeImproper(i, j, k, l):
    """
    Since the i, j, and l atoms are all interchangable in an improper
    torsion, we need to put them in a canonical order to look them up
    in a dictionary of torsions.  Here we just sort them.
    """
    a = [ i, j, l ]
    a.sort()
    can = [ a[0], a[1], k, a[2] ]
    return "-".join(can)

def canonicalizeProper(i, j, k, l):
    """
    Canonicalize a proper torsion.  First, sort the inner pair.  If
    they're the same, sort the outer pair.
    """
    if (cmp(j, k) < 0):
        can = [ i, j, k, l ]
    elif (cmp(j, k) == 0):
        if (cmp(i, l) <= 0):
            can = [ i, j, k, l ]
        else:
            can = [ l, k, j, i ]
    else:
        can = [ l, k, j, i ]
    return "-".join(can)

def findImproper(torsions, i, j, k, l):
    """
    Look up an improper torsion, where some of the atoms could be
    wildcards.  First match the exact set, then with one wildcard in
    each position, then with two.
    """
    can = canonicalizeImproper(i, j, k, l)
    if (torsions.has_key(can)):
        return can, torsions[can]
    can = canonicalizeImproper('X', j, k, l)
    if (torsions.has_key(can)):
        return can, torsions[can]
    can = canonicalizeImproper(i, 'X', k, l)
    if (torsions.has_key(can)):
        return can, torsions[can]
    can = canonicalizeImproper(i, j, k, 'X')
    if (torsions.has_key(can)):
        return can, torsions[can]
    can = canonicalizeImproper('X', 'X', k, l)
    if (torsions.has_key(can)):
        return can, torsions[can]
    can = canonicalizeImproper('X', j, k, 'X')
    if (torsions.has_key(can)):
        return can, torsions[can]
    can = canonicalizeImproper(i, 'X', k, 'X')
    if (torsions.has_key(can)):
        return can, torsions[can]
    return None, None

def findProper(torsions, i, j, k, l):
    """
    Look up a proper torsion.  The outer two atoms could both be
    wildcards.
    """
    can = canonicalizeProper(i, j, k, l)
    if (torsions.has_key(can)):
        return can, torsions[can]
    can = canonicalizeProper('X', j, k, 'X')
    if (torsions.has_key(can)):
        return can, torsions[can]
    return None, None

definedImpropers = {
    'urea_improper_1': '43.93200',
    'nucleic_imp_10': '4.18400',
    'nucleic_imp_11': '4.60240',
}

definedPropers = {
    'backbone_prop_1': '20.92000 0.00000 -20.92000 0.00000 0.00000 0.00000',
    'backbone_prop_2': '29.28800 -8.36800 -20.92000 0.00000 0.00000 0.00000',
    'backbone_prop_3': '9.82361 -1.36942 -7.39396 3.79907 0.00000 0.00000',
    'backbone_prop_4': '8.08349 -1.41503 -2.88780 -3.78066 0.00000 0.00000',
    'backbone_prop_5': '12.42271 -1.91418 -10.50853 0.00000 0.00000 0.00000',
    'backbone_prop_6': '4.43797 4.43797 0.09205 0.00000 0.00000 0.00000',
    'sidechain_prop_1': '20.08320 0.00000 -20.08320 0.00000 0.00000 0.00000',
    'proline_prop_1': '9.82361 -1.36942 -7.39396 3.79907 0.00000 0.00000',
    'hyp_prop_1': '0.65270 1.95811 12.46832 -2.61082 0.00000 0.00000',
    'aromatic_prop_1': '30.33400 0.00000 -30.33400 0.00000 0.00000 0.00000',
    'aromatic_prop_2': '19.24640 0.00000 -19.24640 0.00000 0.00000 0.00000',
    'aromatic_prop_3': '11.71520 0.00000 -11.71520 0.00000 0.00000 0.00000',
    'aromatic_prop_3a': '20.08320 0.00000 -20.08320 0.00000 0.00000 0.00000',
    'aromatic_prop_4': '12.55200 0.00000 -12.55200 0.00000 0.00000 0.00000',
    'aromatic_prop_4a': '20.08320 0.00000 -20.08320 0.00000 0.00000 0.00000',
    'aromatic_prop_5': '19.45560 0.00000 -19.45560 0.00000 0.00000 0.00000',
    'aromatic_prop_5a': '41.84000 0.00000 -41.84000 0.00000 0.00000 0.00000',
    'aromatic_prop_6': '44.97800 0.00000 -44.97800 0.00000 0.00000 0.00000',
    'aromatic_prop_6a': '43.09520 0.00000 -43.09520 0.00000 0.00000 0.00000',
    'aromatic_prop_7': '54.60120 0.00000 -54.60120 0.00000 0.00000 0.00000',
    'aromatic_prop_8': '14.01640 0.00000 -14.01640 0.00000 0.00000 0.00000',
    'aromatic_prop_9': '12.76120 0.00000 -12.76120 0.00000 0.00000 0.00000',
    'aromatic_prop_10': '25.10400 0.00000 -25.10400 0.00000 0.00000 0.00000',
    'aromatic_prop_11': '30.33400 0.00000 -30.33400 0.00000 0.00000 0.00000',
    'aromatic_prop_12': '29.28800 0.00000 -29.28800 0.00000 0.00000 0.00000',
    'proper_X_CT_N*_X': '0.00000 0.00000 0.00000 0.00000 0.00000 0.00000',
    'proper_X_CM_CT_X': '0.00000 0.00000 0.00000 0.00000 0.00000 0.00000',
    'proper_X_CK_N*_X': '14.22560 0.00000 -14.22560 0.00000 0.00000 0.00000',
    'proper_X_CB_N*_X': '13.80720 0.00000 -13.80720 0.00000 0.00000 0.00000',
    'proper_X_CA_NC_X': '40.16640 0.00000 -40.16640 0.00000 0.00000 0.00000',
    'proper_X_CQ_NC_X': '56.90240 0.00000 -56.90240 0.00000 0.00000 0.00000',
    'proper_X_C_N*_X': '12.13360 0.00000 -12.13360 0.00000 0.00000 0.00000',
    'proper_X_CM_CM_X': '55.64720 0.00000 -55.64720 0.00000 0.00000 0.00000',
    'proper_X_C_NC_X': '33.47200 0.00000 -33.47200 0.00000 0.00000 0.00000',
    'proper_X_CA_CM_X': '21.33840 0.00000 -21.33840 0.00000 0.00000 0.00000',
    'proper_X_C_NA_X': '11.29680 0.00000 -11.29680 0.00000 0.00000 0.00000',
    'proper_X_CA_NA_X': '12.55200 0.00000 -12.55200 0.00000 0.00000 0.00000',
    'proper_X_CK_NB_X': '83.68000 0.00000 -83.68000 0.00000 0.00000 0.00000',
    'proper_X_C_CM_X': '18.20040 0.00000 -18.20040 0.00000 0.00000 0.00000',
    'proper_CM_CM_C_O': '19.45560 3.76560 -18.20040 -5.02080 0.00000 0.00000',
    'proper_HC_CT_CM_CM': '6.40152 -9.58136 0.00000 6.35968 0.00000 0.00000',
    'proper_X_CA_N2_X': '20.08320 0.00000 -20.08320 0.00000 0.00000 0.00000',
    'proper_X_N*_CM_X': '15.48080 0.00000 -15.48080 0.00000 0.00000 0.00000',
    'proper_H_CT_CT_O': '1.696840 0.90653 0.00000 -2.60338 0.00000 0.00000',
}

if (__name__ == '__main__'):
    prefix = sys.argv[1]

    # extract numeric to symbolic atom type mapping from nb.itp file
    nonbonded_tree = ParseINI(prefix + "nb.itp").parse()

    numeric2symbolic = {}
    atomtypes = nonbonded_tree.get(0)
    for elt in atomtypes.getElements():
        numeric = elt.getColumn(0)
        type = elt.getColumn(1)
        numeric2symbolic[numeric] = type

    bond_tree = ParseINI(prefix + "bon.itp").parse()

    # extract improper torsions from bon.itp file
    improperTorsions = {}
    impropers = bond_tree.get(2)
    for imp in impropers.getElements():
        i = imp.getColumn(0)
        j = imp.getColumn(1)
        k = imp.getColumn(2)
        l = imp.getColumn(3)
        kd = imp.getColumn(6)
        can = canonicalizeImproper(i, j, k, l)
        improperTorsions[can] = kd

    # extract proper torsions from bon.itp file
    properTorsions = {}
    propers = bond_tree.get(3)
    for prop in propers.getElements():
        i = prop.getColumn(0)
        j = prop.getColumn(1)
        k = prop.getColumn(2)
        l = prop.getColumn(3)
        a = prop.getColumn(5)
        b = prop.getColumn(6)
        c = prop.getColumn(7)
        d = prop.getColumn(8)
        e = prop.getColumn(9)
        f = prop.getColumn(10)
        can = canonicalizeProper(i, j, k, l)
        properTorsions[can] = " ".join([a, b, c, d, e, f])

    rtp_tree = ParseINI(prefix + ".rtp").parse()
    first = True
    for mol in rtp_tree.getElements():
        # ignore first section, it's not a molecule
        if (first):
            first = False
            continue
        name = mol.name
        print "[ %s ]" % name
        PDBName2AmberNumericType = {}
        for section in mol.getElements():
            sectionName = section.name
            if (sectionName == 'atoms'):
                PDBName2AmberNumericType['CB'] = 'amber99_11' # appears in GLY dihedral, but not defined there
                for atomRecord in section.getElements():
                    pdb = atomRecord.getColumn(0)
                    amber = atomRecord.getColumn(1)
                    PDBName2AmberNumericType[pdb] = amber
                # these represent atoms in neighboring residues:
                PDBName2AmberNumericType['+N'] = 'amber99_34'
                PDBName2AmberNumericType['+H'] = 'amber99_17'
                PDBName2AmberNumericType['+CA'] = 'amber99_11'
                PDBName2AmberNumericType['-CA'] = 'amber99_11'
                PDBName2AmberNumericType['-CH3'] = 'amber99_11'
                PDBName2AmberNumericType['-C'] = 'amber99_2'
                PDBName2AmberNumericType['-O'] = 'amber99_41'
            if (sectionName == 'dihedrals'):
                for properRecord in section.getElements():
                    i = properRecord.getColumn(0)
                    i = numeric2symbolic[PDBName2AmberNumericType[i]]
                    j = properRecord.getColumn(1)
                    j = numeric2symbolic[PDBName2AmberNumericType[j]]
                    k = properRecord.getColumn(2)
                    k = numeric2symbolic[PDBName2AmberNumericType[k]]
                    l = properRecord.getColumn(3)
                    l = numeric2symbolic[PDBName2AmberNumericType[l]]
                    if (properRecord.getColumnCount() > 4):
                        defined = properRecord.getColumn(4)
                        whichMatch, value = findProper(properTorsions, i, j, k, l)
                        rtpValue = definedPropers[defined]
                        if (value == None):
                            print "need to define proper: %s %s" % (canonicalizeProper(i, j, k, l), rtpValue)
                        else:
                            if (value != rtpValue):
                                print "proper mismatch: %s: %s != %s" % (canonicalizeProper(i, j, k, l), value, rtpValue)
                            else:
                                #print "proper match: %s %s %s" % (canonicalizeProper(i, j, k, l), whichMatch, value)
                                pass
            if (sectionName == 'impropers'):
                for improperRecord in section.getElements():
                    i = improperRecord.getColumn(0)
                    i = numeric2symbolic[PDBName2AmberNumericType[i]]
                    j = improperRecord.getColumn(1)
                    j = numeric2symbolic[PDBName2AmberNumericType[j]]
                    k = improperRecord.getColumn(2)
                    k = numeric2symbolic[PDBName2AmberNumericType[k]]
                    l = improperRecord.getColumn(3)
                    l = numeric2symbolic[PDBName2AmberNumericType[l]]
                    if (improperRecord.getColumnCount() > 4):
                        defined = improperRecord.getColumn(4)
                        whichMatch, value = findImproper(improperTorsions, i, j, k, l)
                        rtpValue = definedImpropers[defined]
                        if (value == None):
                            print "need to define improper: %s %s" % (canonicalizeImproper(i, j, k, l), rtpValue)
                        else:
                            if (value != rtpValue):
                                print "improper mismatch: %s: %s != %s" % (canonicalizeImproper(i, j, k, l), value, rtpValue)
                            else:
                                #print "improper match: %s %s %s" % (canonicalizeImproper(i, j, k, l), whichMatch, value)
                                pass
