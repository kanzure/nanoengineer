
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXAtom.h"

namespace Nanorex {

char* NXAtom::NullString = "";
NXReal NXAtom::ZeroRealValue = 0.0;


/* FUNCTION: GetElementName */
const char* NXAtom::GetElementName(const NXABMInt& id) {
	NXEntityManager* entityManager = NXEntityManager::Instance();
	if (entityManager->atomId2Atom.size() > id)
		return entityManager->atomId2Atom[id]->elementName;
	
	else
		return NullString;
}


/* FUNCTION: GetPosition */
const NXReal& NXAtom::GetPosition(const NXABMInt& id,
								  const unsigned int& dimension) {
	NXEntityManager* entityManager = NXEntityManager::Instance();
	if (entityManager->atomId2Atom.size() > id)
		if (dimension < 3)
			return NXEntityManager::Instance()->atomId2Atom[id]
					->position[dimension];
		else
			return ZeroRealValue;
	else
		return ZeroRealValue;
}


} // Nanorex::
