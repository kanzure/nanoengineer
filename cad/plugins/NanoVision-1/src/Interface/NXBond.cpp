
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXBond.h"

namespace Nanorex {

char* NXBond::NullString = "";
NXABMInt NXBond::ZeroABMInt = 0;
NXReal NXBond::ZeroRealValue = 0.0;


/* FUNCTION: GetMoleculeId */
const NXABMInt& NXBond::GetMoleculeId(const NXABMInt& id) {
	NXEntityManager* entityManager = GetEntityManager(id);
	if (entityManager)
		return entityManager->bondId2Bond[id]->moleculeId;
	else
		return ZeroABMInt;
}


/* FUNCTION: GetA */
const NXABMInt& NXBond::GetA(const NXABMInt& id) {
	NXEntityManager* entityManager = GetEntityManager(id);
	if (entityManager)
		return entityManager->bondId2Bond[id]->a;
	else
		return ZeroABMInt;
}


/* FUNCTION: GetB */
const NXABMInt& NXBond::GetB(const NXABMInt& id) {
	NXEntityManager* entityManager = GetEntityManager(id);
	if (entityManager)
		return entityManager->bondId2Bond[id]->b;
	else
		return ZeroABMInt;
}


/* FUNCTION: GetEntityManager */
NXEntityManager* NXBond::GetEntityManager(const NXABMInt& id) {
	NXEntityManager* entityManager = NXEntityManager::Instance();
	if (entityManager->bondId2Bond.size() > id)
		return entityManager;
	else
		return 0;
}


} // Nanorex::
