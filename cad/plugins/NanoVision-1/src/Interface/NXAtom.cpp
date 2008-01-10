
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXAtom.h"

namespace Nanorex {


const char* NXAtom::GetElementName(const NXABMInt& id) {
	return NXEntityManager::Instance()->atomId2Atom[id]->elementName;
}

const NXReal& NXAtom::GetPosition(const NXABMInt& id, const int& dimension) {
	return NXEntityManager::Instance()->atomId2Atom[id]->position[dimension];
}


} // Nanorex::
