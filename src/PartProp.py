# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from PartPropDialog import *

class PartProp(PartPropDialog):
    def __init__(self, assy):
        PartPropDialog.__init__(self)
        self.assy = assy
        
        self.nameLineEdit.setText(self.assy.name)


        nchunks = 0
        natoms = 0
        nsinglets = 0
        nrmotors = 0
        nlmotors = 0
        ngrounds = 0
        nstats = 0

        # Determine the number of chunks and atoms in the part.         
        for mol in self.assy.molecules:
            nchunks += 1
            natoms += len(mol.atoms)
            for a in mol.atoms.itervalues():
                if a.element.symbol == "X": nsinglets +=1
        
        natoms = natoms - nsinglets # Subtract singlets from number of atoms

        self.statsView.setSorting( -1) # Turn off sorting

        item = QListViewItem(self.statsView,None)
        item.setText(0,"Singlets:")
        item.setText(1, str(nsinglets))

        item = QListViewItem(self.statsView,None)
        item.setText(0,"Atoms:")
        item.setText(1, str(natoms))
                        
        item = QListViewItem(self.statsView,None)
        item.setText(0,"Chunks:")
        item.setText(1, str(nchunks))

    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)