
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXMoleculeSet.h"

namespace Nanorex {

unsigned int NXMoleculeSet::NextMoleculeIndex = 0;


/* CONSTRUCTOR */
NXMoleculeSet::NXMoleculeSet() {
}


/* DESTRUCTOR */
NXMoleculeSet::~NXMoleculeSet() {
	// TODO: Recursively delete sub-NXMSs
}


OBMol* NXMoleculeSet::newMolecule() {
	OBMol* molecule = new OBMol();
	NXMoleculeData* moleculeData = new NXMoleculeData();
	moleculeData->SetIdx(NextMoleculeIndex);
	NextMoleculeIndex++;
	molecule->SetData(moleculeData);
	molecules.push_back(molecule);
	return molecule;
}


} // Nanorex::
