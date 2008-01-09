
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXChemistryDataModel.h"

namespace Nanorex {


static char* NXAtomGetElementName(NXABMInt id) {
	return "foo";
}

static NXReal NXAtomGetPosition(NXABMInt id, int dimension) {
	return 5.0;
}


NXMoleculeSet::NXMoleculeSet() {
}


NXMoleculeSet::~NXMoleculeSet() {
	// TODO: Recursively delete sub-NXMSs
}


} // Nanorex::
