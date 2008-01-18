// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_MOLECULE_H
#define NX_MOLECULE_H

#include <openbabel/generic.h>
#define NXMoleculeDataType OBGenericDataType::CustomData0
using namespace OpenBabel;

namespace Nanorex {


/* CLASS: NXMoleculeData */
/**
 * A set of Nanorex-specific data stored in OBMol objects.
 *
 * @ingroup ChemistryDataModel, NanorexInterface
 */
class NXMoleculeData : public OBGenericData {
	public:
		NXMoleculeData() { _type = NXMoleculeDataType; }
		void SetIdx(int idx) { _idx = idx; }
		unsigned int GetIdx() { return _idx; }
	
	private:
		unsigned int _idx;
};


} // Nanorex::

#endif
