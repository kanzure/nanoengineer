
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXAtom.h"

namespace Nanorex {

char* NXAtom::NullString = "";
NXABMInt NXAtom::ZeroABMInt = 0;
NXReal NXAtom::ZeroRealValue = 0.0;


/* FUNCTION: GetMoleculeId */
const NXABMInt& NXAtom::GetMoleculeId(const NXABMInt& id) {
	NXEntityManager* entityManager = GetEntityManager(id);
	if (entityManager)
		return entityManager->atomId2Atom[id]->moleculeId;
	else
		return ZeroABMInt;
}


/* FUNCTION: GetElementName */
const char* NXAtom::GetElementName(const NXABMInt& id) {
	NXEntityManager* entityManager = GetEntityManager(id);
	if (entityManager)
		return entityManager->atomId2Atom[id]->elementName;
	
	else
		return NullString;
}


/* FUNCTION: GetPosition */
const NXReal& NXAtom::GetPosition(const NXABMInt& id,
								  const unsigned int& dimension) {
	NXEntityManager* entityManager = GetEntityManager(id);
	if (entityManager)
		if (dimension < 3)
			return NXEntityManager::Instance()->atomId2Atom[id]
					->position[dimension];
		else
			return ZeroRealValue;
	else
		return ZeroRealValue;
}


/* FUNCTION: GetEntityManager */
NXEntityManager* NXAtom::GetEntityManager(const NXABMInt& id) {
	NXEntityManager* entityManager = NXEntityManager::Instance();
	if (entityManager->atomId2Atom.size() > id)
		return entityManager;
	else
		return 0;
}


} // Nanorex::
