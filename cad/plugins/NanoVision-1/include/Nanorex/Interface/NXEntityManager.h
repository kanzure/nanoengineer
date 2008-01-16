// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ENTITYMANAGER_H
#define NX_ENTITYMANAGER_H

#include <map>
#include <vector>

#include "Nanorex/Utility/NXUtility.h"
#include "Nanorex/Utility/NXProperties.h"
#include "Nanorex/Utility/NXPluginGroup.h"
#include "Nanorex/Utility/NXStringTokenizer.h"
#include "Nanorex/Interface/NXNumbers.h"
#include "Nanorex/Interface/NXMoleculeSet.h"
#include "Nanorex/Interface/NXDataImportExportPlugin.h"

namespace Nanorex {

class NXAtom;
class NXBond;
class NXMolecule;

typedef std::vector<NXABMInt>::iterator NXMoleculeIdIterator;
typedef std::vector<NXABMInt>::iterator NXAtomIdIterator;
typedef std::vector<NXABMInt>::iterator NXBondIdIterator;


/* STRUCT: NXSupplementalAtomData */
/**
 * A secondary set of atom data.
 * Used internally by NXEntityManager.
 */
struct NXSupplementalAtomData {
	NXReal velocity[3];
};


/* STRUCT: NXAtomData */
/**
 * The primary set of atom data.
 * Used internally by NXEntityManager.
 */
struct NXAtomData {
	NXABMInt moleculeId;
	char* elementName;
	NXReal position[3];
	NXSupplementalAtomData* supplementalData;
};


/* STRUCT: NXSupplementalBondData */
/**
 * A secondary set of bond data.
 * Used internally by NXEntityManager.
 */
struct NXSupplementalBondData {
};


/* STRUCT: NXBondData */
/**
 * The primary set of bond data.
 * Used internally by NXEntityManager.
 */
struct NXBondData {
	NXABMInt moleculeId;
	NXABMInt a, b;
	NXSupplementalBondData* supplementalData;
};


/* STRUCT: NXSupplementalMoleculeData */
/**
 * A secondary set of molecule data.
 * Used internally by NXEntityManager.
 */
struct NXSupplementalMoleculeData {
};


/* STRUCT: NXMoleculeData */
/**
 * The primary set of molecule data.
 * Used internally by NXEntityManager.
 */
struct NXMoleculeData {
	NXMoleculeSet* moleculeSet;
	NXSupplementalMoleculeData* supplementalData;
};


/* CLASS: NXEntityManager */
/**
 * Encapsulates the storage of molecular and related data.
 * @ingroup ChemistryDataModel, NanorexInterface
 *
 * TODO:
 * - Store/handle DNA strand direction information. This is the equivalent of
 *   bond direction data coming out of NE1.
 * - Molecule, atom, and bond data stuct ids are currently purely sequential
 *   and increasing. Should really have an id management/accounting mechanism.
 */
class NXEntityManager {
	friend class NXAtom;
	friend class NXBond;
	friend class NXMolecule;
	
	public:
		NXEntityManager();
		~NXEntityManager();
		
		static NXEntityManager* Instance() {
			return ThisInstance;
		}

		//
		// Import/export plugins
		//
		void loadDataImportExportPlugins(NXProperties* properties);
		int importFromFile(const unsigned int& moleculeSetId,
						   const std::string& fileType,
						   const std::string& fileName,
						   std::string& message);
		int exportToFile(const unsigned int& moleculeSetId,
						 const std::string& fileType,
						 const std::string& fileName,
						 std::string& message);


		//
		// MoleculeSet
		//
		NXMoleculeSet* getRootMoleculeSet() { return rootMoleculeSet; }


		//
		// Molecules
		//
		NXABMInt newMolecule(NXMoleculeSet* moleculeSet);
		NXMoleculeIdIterator moleculesBegin(NXMoleculeSet* moleculeSet);
		NXMoleculeIdIterator moleculesEnd(NXMoleculeSet* moleculeSet);


		//
		// Atoms
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


		//
		// Bonds
		//
		NXABMInt newBond(const NXABMInt& moleculeId,
						 const NXABMInt& a = 0,
						 const NXABMInt& b = 0);
		NXBondIdIterator bondsBegin(NXMoleculeSet* moleculeSet);
		NXBondIdIterator bondsEnd(NXMoleculeSet* moleculeSet);
		NXBondIdIterator bondsBegin(const NXABMInt& moleculeId);
		NXBondIdIterator bondsEnd(const NXABMInt& moleculeId);

	private:
		static NXEntityManager* ThisInstance;
		
		NXPluginGroup* dataImpExpPluginGroup;
		std::map<std::string, NXDataImportExportPlugin*> dataImportTable;
		std::map<std::string, NXDataImportExportPlugin*> dataExportTable;
		
		NXMoleculeSet* rootMoleculeSet;
		
 		// Maps molecule set pointers  to  a vector of its molecule data ids
		std::map<NXMoleculeSet*,
				 std::vector<NXABMInt> > moleculeSet2MoleculeIds;
		
		// Maps molecule set pointers  to  a vector of atom data ids
		std::map<NXMoleculeSet*, std::vector<NXABMInt> > moleculeSet2AtomIds;
		
		// Maps molecule set pointers  to  a vector of bond data ids
		std::map<NXMoleculeSet*, std::vector<NXABMInt> > moleculeSet2BondIds;
		
		// Maps molecule id with its data
		std::vector<NXMoleculeData*> moleculeId2Molecule;
		
		// Maps molecule data ids  to  a vector of its atom data ids
		std::map<NXABMInt, std::vector<NXABMInt> > moleculeId2AtomIds;
		
		// Maps molecule data ids  to  a vector of its bond data ids
		std::map<NXABMInt, std::vector<NXABMInt> > moleculeId2BondIds;
		
		// Maps atom id with its data
		std::vector<NXAtomData*> atomId2Atom;
		
		// Maps bond id with its data
		std::vector<NXBondData*> bondId2Bond;
};

} // Nanorex::

#endif
