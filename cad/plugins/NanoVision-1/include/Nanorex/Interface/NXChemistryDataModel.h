// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_CHEMISTRYDATAMODEL_H
#define NX_CHEMISTRYDATAMODEL_H

#include <list>
#include <string>

#include "Nanorex/Interface/NXNumbers.h"

namespace Nanorex {

class NXMoleculeSet;

typedef std::list<NXMoleculeSet*>::iterator NXMoleculeSetIterator;


struct NXSupplementalAtomData {
	NXReal velocity[3];
};


struct NXAtomData {
	NXABMInt id;
	NXABMInt moleculeId;
	char* elementName;
	NXReal position[3];
	NXSupplementalAtomData* supplementalData;
};


struct NXBondData {
	NXABMInt id, a, b;
};


struct NXSupplementalMoleculeData {
};


struct NXMoleculeData {
	NXABMInt id;
	NXMoleculeSet* moleculeSet;
	NXSupplementalMoleculeData* supplementalData;
};


class NXMolecule {
};


class NXMoleculeSet {
	public:
		NXMoleculeSet();
		~NXMoleculeSet();
		
		void addChild(NXMoleculeSet* child) { children.push_back(child); }
		NXMoleculeSetIterator childrenBegin() { return children.begin(); }
		NXMoleculeSetIterator childrenEnd() { return children.end(); }
		NXMSInt childCount() { return children.size(); }

	private:
		std::list<NXMoleculeSet*> children;
};


} // Nanorex::

#endif
