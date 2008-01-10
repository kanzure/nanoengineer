// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ATOM_H
#define NX_ATOM_H

#include "Nanorex/Interface/NXNumbers.h"
#include "Nanorex/Interface/NXEntityManager.h"
#include "Nanorex/Interface/NXChemistryDataModel.h"

namespace Nanorex {


class NXAtom {
	public:
		static const char* GetElementName(const NXABMInt& id);
		static const NXReal& GetPosition(const NXABMInt& id, const int& dimension);
};


} // Nanorex::

#endif
