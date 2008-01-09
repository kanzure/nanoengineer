// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ENTITYMANAGER_H
#define NX_ENTITYMANAGER_H

#include <map>
#include <vector>

#include "Nanorex/Interface/NXNumbers.h"
#include "Nanorex/Interface/NXEntityManager.h"
#include "Nanorex/Interface/NXChemistryDataModel.h"

namespace Nanorex {

typedef std::vector<NXABMInt>::iterator NXMoleculeIdIterator;
typedef std::vector<NXABMInt>::iterator NXAtomIdIterator;


/* CLASS: NXEntityManager */
/**
 * Entity Manager interface.
 * @ingroup ChemistryObjectModel
 */
class NXEntityManager {
	public:
		NXEntityManager();
		~NXEntityManager();
		
		static NXEntityManager* getInstance() { return ThisInstance; }

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
		NXABMInt newAtom(NXABMInt moleculeId);/*,
							 const char* elementType,
							 const Real& x = 0,
							 const Real& y = 0,
							 const Real& z = 0);*/
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
