// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_BOND_H
#define NX_BOND_H

#include "Nanorex/Interface/NXNumbers.h"
#include "Nanorex/Interface/NXEntityManager.h"

namespace Nanorex {


/* CLASS: NXBond */
/**
 * An interface to bond data.
 *
 * @ingroup ChemistryDataModel, NanorexInterface
 */
class NXBond {
	public:
		static const NXABMInt& GetMoleculeId(const NXABMInt& id);
		static const NXABMInt& GetA(const NXABMInt& id);
		static const NXABMInt& GetB(const NXABMInt& id);
	
	private:
		static char* NullString;
		static NXABMInt ZeroABMInt;
		static NXReal ZeroRealValue;

		static NXEntityManager* GetEntityManager(const NXABMInt& id);
};


} // Nanorex::

#endif
