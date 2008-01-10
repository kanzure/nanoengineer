// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ENTITYMANAGER_H
#define NX_ENTITYMANAGER_H

#include <map>
#include <vector>

#include "Nanorex/Interface/NXNumbers.h"
#include "Nanorex/Interface/NXMoleculeSet.h"

namespace Nanorex {

class NXAtom;

typedef std::vector<NXABMInt>::iterator NXMoleculeIdIterator;
typedef std::vector<NXABMInt>::iterator NXAtomIdIterator;


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


struct NXSupplementalBondData {
};


struct NXBondData {
	NXABMInt id, a, b;
	NXSupplementalBondData* supplementalBond;
};


struct NXSupplementalMoleculeData {
};


struct NXMoleculeData {
	NXABMInt id;
	NXMoleculeSet* moleculeSet;
	NXSupplementalMoleculeData* supplementalData;
};


/* CLASS: NXEntityManager */
/**
 * Entity Manager interface.
 * @ingroup ChemistryObjectModel
 *
 * TODO:
 * - store/handle DNA strand direction information
 */
class NXEntityManager {
	friend class NXAtom;
	
	public:
		NXEntityManager();
		~NXEntityManager();
		
		static NXEntityManager* Instance() { return ThisInstance; }

		void loadDataImportExportPlugins();
		int importFromFile(const unsigned int& moleculeSetId,
						   const std::string& fileType,
						   const std::string& fileName,
						   std::string& message);
		int exportToFile(const unsigned int& moleculeSetId,
						 const std::string& fileType,
						 const std::string& fileName,
						 std::string& message);


		//
		// NXMoleculeSet
		//
		NXMoleculeSet* getRootMoleculeSet() { return rootMoleculeSet; }


		//
		// Molecule
		//
		NXABMInt newMolecule(NXMoleculeSet* moleculeSet);
		NXMoleculeIdIterator moleculesBegin(NXMoleculeSet* moleculeSet);
		NXMoleculeIdIterator moleculesEnd(NXMoleculeSet* moleculeSet);


		//
		// Atom
		//
		NXABMInt newAtom(const NXABMInt& moleculeId,
						 const char* elementName = "?",
						 const NXReal& x = 0,
						 const NXReal& y = 0,
						 const NXReal& z = 0);
		NXAtomIdIterator atomsBegin(NXMoleculeSet* moleculeSet);
		NXAtomIdIterator atomsEnd(NXMoleculeSet* moleculeSet);
		NXAtomIdIterator atomsBegin(const NXABMInt& moleculeId);
		NXAtomIdIterator atomsEnd(const NXABMInt& moleculeId);

	private:
		static NXEntityManager* ThisInstance;
		
		NXMoleculeSet* rootMoleculeSet;
		
 		// maps molecule set pointers  to  a vector of its molecule data ids
		std::map<NXMoleculeSet*,
				 std::vector<NXABMInt> > moleculeSet2MoleculeIds;
		
		// maps molecule set pointers  to  a vector of atom data ids
		std::map<NXMoleculeSet*, std::vector<NXABMInt> > moleculeSet2AtomIds;
		
		// maps molecule id with its data
		std::vector<NXMoleculeData*> moleculeId2Molecule;
		
		// maps molecule data ids  to  a vector of its atom data ids
		std::map<NXABMInt, std::vector<NXABMInt> > moleculeId2AtomIds;
		
		// maps atom id with its data
		std::vector<NXAtomData*> atomId2Atom;
};

} // Nanorex::

#endif
