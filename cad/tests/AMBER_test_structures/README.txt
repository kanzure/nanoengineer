
This directory contains structures in two different forms, which are
used to test the pattern matching code for assigning AMBER atom types
to atoms prior to a GROMACS simulation.

To perform the tests:

Start NE1.

Open one of the files under the mmp subdirectory.

Choose the Tools->Check AMBER AtomTypes menu.  Atom type labels should
show up over each atom in the structure.

File->Import->IN file, and choose the corresponding .in_frag file in
the dot_in subdirectory.

  For mmp files in mmp/AminoAcids, look in dot_in/all_amino02.
  For mmp files in mmp/Nucleotides, look in dot_in/all_nuc02.

A similar structure should be loaded, and annotated with atomtype
labels.  Verify that the corresponding atoms in each structure have
the same atom type labels.

Open a new mmp file and repeat until you have examined all mmp files.

--

There may be some slight differences between the structures, as the
.mmp files are complete molecules, while the .in_frag files are
fragments of molecules, and are designed to be bonded together to form
complete molecules.  This changes the type of the Oxygen of the
sugar-phosphate bond on the sugar side of DNA and RNA nucleotides, as
the Phosphorus is replaced by a Hydrogen.

The .in_frag files do not specify all of the bonds in the structures,
so rings of atoms will remain unclosed.  Also, all .in_frag files will
have only single bonds between atoms when imported.  Note that running
the Check AMBER AtomTypes menu will not correctly assign types to such
fragments, as the bond information is not complete.
