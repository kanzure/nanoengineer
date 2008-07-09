# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
GROMACS.py - defines class GROMACS, for a temporary demo of
atomic-level-DNA GROMACS simulation

@author: Brian
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

Encapsulates the running of energy minimizations and molecular dynamics
simulations from NE1 using GROMACS and HK_Simulation (the visualization window
of HiveKeeper.

NOTE: THIS CODE IS DESIGNED JUST FOR THE FNANO 2007 DEMO, AND FOR PROTOTYPING,
IE, TO SEE HOW THE VARIOUS COMPONENTS WORK/BEHAVE. NONE OF IT WOULD SURVIVE TO
THE REAL SOLUTION.

Brian Helfrich 2007-03-31
"""

import os
from datetime import datetime


class GROMACS:
    
    def __init__(self, part):
        self.part = part
        
        # Note: This GROMACS build doesn't work if there are any spaces in its
        # path, so don't put any.
        #
        self.gmxHome = 'C:/11Nano/CVS-D/cad/plugins/GROMACS/'
        
        # These are the GROMACS AMBER03 atom types for nucleotide residues in
        # the order they are written out by the DNA generator. We can re-create
        # the PDB-style structure with these, and it works if nothing is done
        # to the structure of the DNA to change the order of the atoms.
        #
        self.adenineAtomTypes = ['P', 'O1P', 'O2P', 'O5\'', 'C5\'', 'C4\'',
            'O4\'', 'C3\'', 'C2\'', 'C1\'', 'N9', 'C8', 'N7', 'C5', 'C6', 'N6',
            'N1', 'C2', 'N3', 'C4', 'H5\'2', 'H5\'1', 'H4\'', 'H1\'', 'H2\'1',
            'H2\'2', 'H3\'', 'H8', 'H61', 'H62', 'H2', 'O3\'']
        self.cytosineAtomTypes = ['P', 'O1P', 'O2P', 'O5\'', 'C5\'', 'C4\'',
            'O4\'', 'C3\'', 'C2\'', 'C1\'', 'N1', 'C2', 'O', 'N3', 'C4', 'N4',
            'C5', 'C6', 'H5\'1', 'H5\'2', 'H4\'', 'H1\'', 'H2\'1', 'H2\'2',
            'H3\'', 'H6', 'H5', 'H41', 'H42', 'O3\'']
        self.guanineAtomTypes = ['P', 'O1P', 'O2P', 'O5\'', 'C5\'', 'C4\'',
            'O4\'', 'C3\'', 'C2\'', 'C1\'', 'N9', 'C8', 'N7', 'C5', 'C6', 'O6',
            'N1', 'C2', 'N2', 'N3', 'C4', 'H5\'1', 'H5\'2', 'H4\'', 'H1\'',
            'H2\'1', 'H2\'2', 'H3\'', 'H8', 'H1', 'H21', 'H22', 'O3\'']
        self.thymineAtomTypes = ['P', 'O1P', 'O2P', 'O5\'', 'C5\'', 'C4\'',
            'O4\'', 'C3\'', 'C2\'', 'C1\'', 'N1', 'C2', 'O', 'N3', 'C4', 'O4',
            'C5', 'C7', 'C6', 'H5\'1', 'H5\'2', 'H4\'', 'H1\'', 'H2\'1',
            'H2\'2', 'H3\'', 'H6', 'H71', 'H72', 'H73', 'H3', 'O3\'']
            
        # Pseudo-atom tables
        #
        self.pseudoAtomTypes = \
            ['??', 'Ax', 'Ae', 'Ss', 'Sj', 'Pl', 'Pe', 'Sh', 'Hp'] # BUG: element names have been changed since this code worked
        self.pseudoAtomCharges = \
            [0.0,  0.0,  0.0,  0.0,  0.0, -1.0, -2.0,  0.0,  0.0]
        self.pseudoAtomMasses = \
            [0.0,  100,  100,  100,  100,  100,  100,  100,  100]
            
        self.atomKeyToIndexMap = {}
        
        self.debug = False
        
        return
            
        
    def run(self, operation):
        """
        Creates a temp directory, generates a structure files from the part,
        pre-processes them with GROMACS tools, spawns the GROMACS simulation,
        and spawns an HK_Simulation process to view it with.
        
        operation - either "em" to perform an energy minimization, or "md" to
                    perform molecular dynamics simulation
        """
        
        # Create a unique directory under the Nanorex/SimFiles directory for our
        # files: Nanorex/SimFiles/GMX-<timestamp>
        #
        from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
        simFilesPath = find_or_make_Nanorex_subdir('SimFiles')
        timestamp = datetime.today()
        self.tempFilePath = \
            os.path.join(simFilesPath,
                         "GMX-%s" % timestamp.strftime("%Y%m%d%H%M%S"))
        os.mkdir(self.tempFilePath)
 
        # Create the structure files from our part.
        #
        self.atomIndex = 1
        self.residueIndex = 1
        self.pdbFileHandle = 0
        self.atomsFileHandle = 0
        self.confFileHandle = 0
        self.bondsFileHandle = 0
        self.anglesFileHandle = 0
        self.pseudoPass = 1
        partType = self.writeStructure_Helper(self.part.topnode)
        if partType == "pseudo":
            # The first pass was to process and index atoms, now we have
            # sufficient information to determine bonds and angles. It's
            # probably possible to do everything in one pass.
            #
            if self.atomsFileHandle != 0:
                self.atomsFileHandle.close()
            self.pseudoPass = 2
            self.residueIndex = 1
            self.writeStructure_Helper(self.part.topnode)

        if self.pdbFileHandle != 0:
            self.pdbFileHandle.close()
        if self.confFileHandle != 0:
            self.confFileHandle.close()
        if self.bondsFileHandle != 0:
            self.bondsFileHandle.close()
        if self.anglesFileHandle != 0:
            self.anglesFileHandle.close()
        
        script = ""
        if partType == "pseudo":
            # Combine the fragments of the topology into the topol.top file,
            # tweak with GROMACS tools, and run the operation.
            script = "pseudo_" + operation + ".bat"
            
        else:
            # Pre-process the .pdb file with the GROMACS tools and run the
            # operation.
            #
            script = "atomic_" + operation + ".bat"
            
        os.spawnl(os.P_NOWAIT, os.path.join(self.gmxHome, script),
                  os.path.join(self.gmxHome, script),
                  os.path.normpath(self.gmxHome),
                  '"' + os.path.normpath(self.tempFilePath) + '"')
        return

                
    def writeStructure_Helper(self, node):
        partType = "pseudo"
        if self.debug: print "node.name=%s" % node.name
        if node.name[0:6] == "strand":
            if self.debug: print "\t atomic helper"
            self.writeAtomicPDB(node)
            partType = "atomic"
            
        else:
            for childNode in node.members:
                if childNode.is_group():
                    partType = self.writeStructure_Helper(childNode)
                else:
                    if self.debug: print "\t p-atom write"
                    self.writePseudoAtomStructure(childNode)
        return partType
                    
                    
    def writePseudoAtomStructure(self, node):

        if self.pseudoPass == 1:
            # Process atoms
            #
            # Open the topol.top atoms fragment file if not already open
            #
            if self.atomsFileHandle == 0:
                self.atomsFileHandle = \
                    open(os.path.join(self.tempFilePath, "atoms.frag"), "w")
                self.atomsFileHandle.write("[ atoms ]\n")
                self.atomsFileHandle.write("; atomId  atomType  residue#  residue  atom  chargeGroup#     charge    mass\n")
            
            for atom in node.atoms_in_mmp_file_order():
                if atom.element.eltnum == 0:
                    continue
    
                atomTypeIndex = self.getAtomTypeIndex(atom.element.eltnum)
                    
                self.atomsFileHandle.write("%8d%10s%10d      BAS%6s%14d   %8.3f%8.3f\n" % \
                    (self.atomIndex, self.pseudoAtomTypes[atomTypeIndex],
                     self.residueIndex, self.pseudoAtomTypes[atomTypeIndex],
                     self.atomIndex, self.pseudoAtomCharges[atomTypeIndex],
                     self.pseudoAtomMasses[atomTypeIndex]))
    
                self.atomKeyToIndexMap[atom.key] = self.atomIndex
                self.atomIndex += 1
            self.residueIndex += 1
            
        else:
            # Process bonds, angles, and generate the conf.gro file
            #
            # Open the topol.top bonds fragment file if not already open
            #
            if self.bondsFileHandle == 0:
                self.bondsFileHandle = \
                    open(os.path.join(self.tempFilePath, "bonds.frag"), "w")
                self.bondsFileHandle.write("\n[ bonds ]\n")
                self.bondsFileHandle.write(";   ai    aj  function\n")
                
            # Open the topol.top angles fragment file if not already open
            #
            if self.anglesFileHandle == 0:
                self.anglesFileHandle = \
                    open(os.path.join(self.tempFilePath, "angles.frag"), "w")
                self.anglesFileHandle.write("\n[ angles ]\n")
                self.anglesFileHandle.write(";   ai    aj    ak  function\n")
                
            # Open the conf.gro file if not already open
            #
            if self.confFileHandle == 0:
                self.confFileHandle = \
                    open(os.path.join(self.tempFilePath, "conf.gro"), "w")
                self.confFileHandle.write("DNA\n")
                self.confFileHandle.write("  %d\n" % \
                    len(self.atomKeyToIndexMap))
                
            for atom_1 in node.atoms_in_mmp_file_order():
                if atom_1.element.eltnum == 0:
                    continue
    
                # Emit conf.gro coordinates
                #
                atomTypeIndex = self.getAtomTypeIndex(atom_1.element.eltnum)
                    
                self.confFileHandle.write("%5d%-5s%5s%5d%8.3f%8.3f%8.3f\n" % \
                    (self.residueIndex, "BAS", 
                     self.pseudoAtomTypes[atomTypeIndex],
                     self.atomKeyToIndexMap[atom_1.key],
                     atom_1.posn()[0]/10, atom_1.posn()[1]/10,
                     atom_1.posn()[2]/10))
    
                # Emit bonds
                #
                atom_1_Index = self.atomKeyToIndexMap[atom_1.key]
                if self.debug: print "atom [%s] %d" % (atom_1.key, atom_1_Index)
                
                bondCount = 0
                bondIndexes = []
                for bond in atom_1.bonds:
                    atom_2 = bond.other(atom_1)
                    if self.debug: print "atom_2.key=%s" % atom_2.key
                    if atom_2.key not in self.atomKeyToIndexMap:
                        continue
                        
                    atom_2_Index = self.atomKeyToIndexMap[atom_2.key]
                    if atom_2_Index > atom_1_Index:
                        self.bondsFileHandle.write("%6d%6d  1\n" % \
                            (atom_1_Index, atom_2_Index))
                        
                    bondIndexes += [atom_2_Index]
                    bondCount += 1
                        
               # Emit angles
                if bondCount > 1:
                    for index in range(1, bondCount):
                        self.anglesFileHandle.write("%6d%6d%6d  1\n" % \
                            (bondIndexes[index - 1], atom_1_Index,
                             bondIndexes[index]))
                    if bondCount > 2:
                        self.anglesFileHandle.write("%6d%6d%6d  1\n" % \
                            (bondIndexes[bondCount - 1], atom_1_Index,
                             bondIndexes[0]))
            self.residueIndex += 1

                    
    def writePseudoAtomPDB___(self, node):
        """
        This is dead code left here just in case pseudo-atom .pdb files need to
        be generated.
        """
        count_Ss = 1
        count_Pl = 1
        for atom in node.atoms_in_mmp_file_order():
            if atom.element.eltnum == 0:
                continue
                
            coordinates = atom.posn()
            coordinateFields = (coordinates[0], coordinates[1], coordinates[2])
            self.filehandle.write("%-6s" % "ATOM")
            self.filehandle.write("%5d" % self.atomIndex)
            self.filehandle.write(" ")
            
            if atom.element.eltnum == 200:
                self.filehandle.write("Ax   ")
                
            elif atom.element.eltnum == 201:
                self.filehandle.write("Ss%d  " % count_Ss)
                count_Ss += 1
                
            elif atom.element.eltnum == 202:
                self.filehandle.write("Pl%d  " % count_Pl)
                count_Pl += 1
                
            self.filehandle.write("BAS  ")
            self.filehandle.write("%4d" % self.residueIndex)
            self.filehandle.write("    ")
            self.filehandle.write("%8.3f%8.3f%8.3f" % coordinateFields)
            self.filehandle.write("  1.00  0.00\n");

            self.atomIndex += 1
        self.residueIndex += 1

                    
    def writeAtomicPDB(self, node):
        """
        Write down strand 1
          - first nucleotide: residue name gets a "5", no (P, OP1, OP2)
          - last nucleotide: residue name gets a "3"
        Write up strand 2
          - first (bottom) nucleotide: residue name gets a "5", no (P, OP1, OP2)
          - last (top) nucleotide: residue name gets a "3"
        """
                
        # Open the .pdb file if not already open
        #
        if self.pdbFileHandle == 0:
            self.pdbFileHandle = \
                open(os.path.join(self.tempFilePath, "dna.pdb"), "w")
        
        # Need to write residues down strand 1 and up strand 2.
        # Take note of the last nucleotide in each case.
        #
        nodeMembers = list(node.members) # Use a copy of the real list.
        if len(nodeMembers) > 0:
            lastNode = nodeMembers[len(nodeMembers) - 1]
            if node.name == 'strand 2':
                lastNode = nodeMembers[0]
                nodeMembers.reverse()
            
        nucleotideIndex = 1
        for childNode in nodeMembers:
            if self.debug:
                print "node=%s  nucleotideIndex=%d nucleotide=%s " % \
                    (node.name, nucleotideIndex, childNode.name),
                if childNode == lastNode:
                    print "last",
                print "\n"
            atomTypeIndex = 0
            for atom in childNode.atoms_in_mmp_file_order():
                if atom.element.eltnum == 0:
                    continue
                
                if (nucleotideIndex == 1) & (atomTypeIndex < 3):
                    atomTypeIndex += 1
                    continue # First nucleotide in a strand - no phosphate
            
                coordinates = atom.posn()
                coordinateFields = (coordinates[0], coordinates[1],
                    coordinates[2])
                self.pdbFileHandle.write("%-6s" % "ATOM")
                self.pdbFileHandle.write("%5d" % self.atomIndex)
                self.pdbFileHandle.write(" ")
                
                if childNode.name == 'adenine':
                    self.pdbFileHandle.write("%4s" %
                        self.adenineAtomTypes[atomTypeIndex])
                    self.pdbFileHandle.write(" DA")
                    
                elif childNode.name == 'cytosine':
                    self.pdbFileHandle.write("%4s" %
                        self.cytosineAtomTypes[atomTypeIndex])
                    self.pdbFileHandle.write(" DC")
                    
                elif childNode.name == 'guanine':
                    self.pdbFileHandle.write("%4s" %
                        self.guanineAtomTypes[atomTypeIndex])
                    self.pdbFileHandle.write(" DG")
                    
                elif childNode.name == 'thymine':
                    self.pdbFileHandle.write("%4s" %
                        self.thymineAtomTypes[atomTypeIndex])
                    self.pdbFileHandle.write(" DT")
                    
                # Handle strand ends
                if nucleotideIndex == 1:
                    self.pdbFileHandle.write("5")
                        
                elif childNode == lastNode:
                    self.pdbFileHandle.write("3")
                    
                else:
                    self.pdbFileHandle.write(" ")
                    
                self.pdbFileHandle.write("  ")
                self.pdbFileHandle.write("%4d" % self.residueIndex)
                self.pdbFileHandle.write("    ")
                self.pdbFileHandle.write("%8.3f%8.3f%8.3f" % coordinateFields)
                self.pdbFileHandle.write("  1.00  0.00\n");
                atomTypeIndex += 1
                self.atomIndex += 1
            self.residueIndex += 1
            nucleotideIndex += 1
        return

        
    def getAtomTypeIndex(self, elementNumber):
        atomTypeIndex = 0             # ??
        if elementNumber == 200:      # Ax
            atomTypeIndex = 1
        elif elementNumber == 201:    # Ss
            atomTypeIndex = 3
        elif elementNumber == 202:    # Pl
            atomTypeIndex = 5
        elif elementNumber == 203:    # Sj
            atomTypeIndex = 4
        elif elementNumber == 204:    # Ae
            atomTypeIndex = 2
        elif elementNumber == 205:    # Pe
            atomTypeIndex = 6
        elif elementNumber == 206:    # Sh
            atomTypeIndex = 7
        elif elementNumber == 207:    # Hp
            atomTypeIndex = 8
        
        return atomTypeIndex
        
