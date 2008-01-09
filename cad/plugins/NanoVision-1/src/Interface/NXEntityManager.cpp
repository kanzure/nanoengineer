
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXEntityManager.h"

namespace Nanorex {

NXEntityManager* NXEntityManager::ThisInstance = 0;


/* CONSTRUCTOR */
NXEntityManager::NXEntityManager() {
	ThisInstance = this;
	rootMoleculeSet = new NXMoleculeSet();
}


/* DESTRUCTOR */
NXEntityManager::~NXEntityManager() {
	delete rootMoleculeSet;
}


/* FUNCTION: loadDataImportExportPlugins */
/**
 * Loads and initializes all the import/export plugins.
 */
void NXEntityManager::loadDataImportExportPlugins() {
}


/* FUNCTION: importFromFile */
/**
 * Imports the system from the specified file with the appropriate
 * import/export plugin.
 *
 * @param message 	[OUT] description of the error when a non-zero value is
 *					returned
 *
 * @return 0=successful or non-zero error code
 */
int NXEntityManager::importFromFile(const unsigned int& moleculeSetId,
									const std::string& fileType,
									const std::string& fileName,
									/*NXDataStore* dataStore,*/
									std::string& message) {
	return 0;
}


/* FUNCTION: exportToFile */
/**
 * Exports the system from the specified file with the appropriate
 * import/export plugin.
 */
int NXEntityManager::exportToFile(const unsigned int& moleculeSetId,
								  const std::string& fileType,
								  const std::string& fileName,
								  std::string& message) {
	return 0;
}
						 

/* FUNCTION: newMolecule */
/**
 * Creates a new NXMolecule.
 *
 * @return The identifier of the new NXMolecule.
 */
NXABMInt NXEntityManager::newMolecule(NXMoleculeSet* moleculeSet) {

	NXMoleculeData* moleculeData = new NXMoleculeData;
	moleculeData->moleculeSet = moleculeSet;

	moleculeId2Molecule.push_back(moleculeData);
	moleculeData->id = moleculeId2Molecule.size() - 1;
	
	moleculeSet2MoleculeIds[moleculeSet].push_back(moleculeData->id);

	return moleculeData->id;
}


/* FUNCTION: moleculesBegin */
/**
 * Returns an iterator to the first NXMolecule identifier in the given
 * NXMoleculeSet. This iterator does not traverse the NXMolecule identifiers
 * of this NXMoleculeSet's child NXMoleculeSets.
 *
 * @param moleculeSet 	A pointer to the NXMoleculeSet in which to traverse
 *						molecules.
 */
NXMoleculeIdIterator NXEntityManager::moleculesBegin
		(NXMoleculeSet* moleculeSet) {
	return moleculeSet2MoleculeIds[moleculeSet].begin();
}


/* FUNCTION: moleculesEnd */
/**
 * Returns an iterator to the end of the NXMoleculeSet with the given
 * identifier.
 *
 * @param moleculeSetId NXMoleculeSet identifier.
 */
NXMoleculeIdIterator NXEntityManager::moleculesEnd
		(NXMoleculeSet* moleculeSet) {
	return moleculeSet2MoleculeIds[moleculeSet].end();
}


/* FUNCTION: newAtom */
/**
 * Creates a new Atom with the given parameters.
 *
 * @return The identifier of the new Atom.
 */
NXABMInt NXEntityManager::newAtom(NXABMInt moleculeId) {/*,
									  const char* elementType,
									  const Real& x = 0,
									  const Real& y = 0,
									  const Real& z = 0) {*/
	NXAtomData* atomData = new NXAtomData;
	atomData->moleculeId = moleculeId;
	
	atomId2Atom.push_back(atomData);
	atomData->id = atomId2Atom.size() - 1;
	
	moleculeId2AtomIds[moleculeId].push_back(atomData->id);
	
	NXMoleculeData* moleculeData = moleculeId2Molecule[moleculeId];
	moleculeSet2AtomIds[moleculeData->moleculeSet].push_back(atomData->id);
	
	return atomData->id;
}


NXAtomIdIterator NXEntityManager::atomsBegin(NXMoleculeSet* moleculeSet) {
	return moleculeSet2AtomIds[moleculeSet].begin();
}
NXAtomIdIterator NXEntityManager::atomsEnd(NXMoleculeSet* moleculeSet) {
	return moleculeSet2AtomIds[moleculeSet].end();
}
NXAtomIdIterator NXEntityManager::atomsBegin(const NXABMInt& moleculeId) {
	return moleculeId2AtomIds[moleculeId].begin();
}
NXAtomIdIterator NXEntityManager::atomsEnd(const NXABMInt& moleculeId) {
	return moleculeId2AtomIds[moleculeId].end();
}


} // Nanorex::
