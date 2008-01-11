// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_MOLECULESET_H
#define NX_MOLECULESET_H

#include <list>

#include "Nanorex/Interface/NXNumbers.h"

namespace Nanorex {

class NXMoleculeSet;

typedef std::list<NXMoleculeSet*>::iterator NXMoleculeSetIterator;


/* CLASS: NXMoleculeSet */
/**
 * @ingroup ChemistryDataModel, NanorexInterface
 */
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
