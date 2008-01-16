
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
void NXEntityManager::loadDataImportExportPlugins(NXProperties* properties) {
/*
	int pluginIndex = 0;
	std::string msg, pluginFormats;
	std::string pluginKey = "entityManager.importExport.0";
	std::string pluginLibrary =
		std::string(properties->getProperty(pluginKey + ".plugin"));

	if (pluginLibrary.length() == 0) {
		msg = "No Data Import/Export plugins to load.";
		std::cout << "WARNING: " << msg << std::endl;
		NXLOG_WARNING("NXEntityManager", msg);
	}

	NXDataImportExportPlugin* plugin;
	dataImpExpPluginGroup = new NXPluginGroup();
	while (pluginLibrary.length() != 0) {
		plugin = 0;
		if (dataImpExpPluginGroup->load(pluginLibrary.c_str()))
			plugin =
				(NXDataImportExportPlugin*)
					(dataImpExpPluginGroup->instantiate(pluginLibrary.c_str()));

		if (plugin == 0) {
			msg =
				"Couldn't load Data Import/Export plugin: " +
					pluginLibrary;
			NXLOG_WARNING("NXEntityManager", msg);
			std::cout << "WARNING: " << msg << std::endl;

		} else {
			plugin->setEntityManager(this);

			// Import formats
			pluginFormats =
				std::string(properties->getProperty(pluginKey +
							".importFormats"));
			NXStringTokenizer tokenizer(pluginFormats, ",");
			while (tokenizer.hasMoreTokens()) {
				dataImportTable[tokenizer.getNextToken()] = plugin;
			}

			// Export formats
			pluginFormats =
				std::string(properties->getProperty(pluginKey +
							".exportFormats"));
			tokenizer = NXStringTokenizer(pluginFormats, ",");
			while (tokenizer.hasMoreTokens()) {
				dataExportTable[tokenizer.getNextToken()] = plugin;
			}
		}
		pluginIndex++;
		pluginKey =
			std::string("entityManager.importExport.") +
			NXUtility::itos(pluginIndex);
		pluginLibrary =
			std::string(properties->getProperty(pluginKey + ".plugin"));
	}
	*/
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
									std::string& message) {
	return 0;
}


/* FUNCTION: exportToFile */
/**
 * Exports the system to the specified file with the appropriate
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
 * Creates a new molecule.
 *
 * @return The identifier of the new molecule.
 */
NXABMInt NXEntityManager::newMolecule(NXMoleculeSet* moleculeSet) {

	NXMoleculeData* moleculeData = new NXMoleculeData;
	moleculeData->moleculeSet = moleculeSet;

	moleculeId2Molecule.push_back(moleculeData);
	NXABMInt moleculeDataId = moleculeId2Molecule.size() - 1;
	
	moleculeSet2MoleculeIds[moleculeSet].push_back(moleculeDataId);

	return moleculeDataId;
}


/* FUNCTION: moleculesBegin */
/**
 * Returns an iterator to the first molecule identifier in the given
 * NXMoleculeSet. This iterator does not traverse the molecule identifiers
 * of the given NXMoleculeSet's child NXMoleculeSets.
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
 * @return The identifier of the new atom.
 */
NXABMInt NXEntityManager::newAtom(const NXABMInt& moleculeId,
								  const char* elementName,
								  const NXReal& x,
								  const NXReal& y,
								  const NXReal& z) {
	NXAtomData* atomData = new NXAtomData;
	atomData->moleculeId = moleculeId;
	atomData->elementName = new char[strlen(elementName) + 1];
	strcpy(atomData->elementName, elementName);
	atomData->position[0] = x;
	atomData->position[1] = y;
	atomData->position[2] = z;
	atomData->supplementalData = 0;
	
	atomId2Atom.push_back(atomData);
	NXABMInt atomDataId = atomId2Atom.size() - 1;
	
	moleculeId2AtomIds[moleculeId].push_back(atomDataId);
	
	NXMoleculeData* moleculeData = moleculeId2Molecule[moleculeId];
	moleculeSet2AtomIds[moleculeData->moleculeSet].push_back(atomDataId);
	
	return atomDataId;
}


/* FUNCTION: atomsBegin */
NXAtomIdIterator NXEntityManager::atomsBegin(NXMoleculeSet* moleculeSet) {
	return moleculeSet2AtomIds[moleculeSet].begin();
}
NXAtomIdIterator NXEntityManager::atomsBegin(const NXABMInt& moleculeId) {
	return moleculeId2AtomIds[moleculeId].begin();
}


/* FUNCTION: atomsEnd */
NXAtomIdIterator NXEntityManager::atomsEnd(NXMoleculeSet* moleculeSet) {
	return moleculeSet2AtomIds[moleculeSet].end();
}
NXAtomIdIterator NXEntityManager::atomsEnd(const NXABMInt& moleculeId) {
	return moleculeId2AtomIds[moleculeId].end();
}


/* FUNCTION: newBond */
/**
 * Creates a new bond with the given parameters.
 *
 * @return The identifier of the new bond.
 */
NXABMInt NXEntityManager::newBond(const NXABMInt& moleculeId,
								  const NXABMInt& a,
								  const NXABMInt& b) {
	NXBondData* bondData = new NXBondData;
	bondData->moleculeId = moleculeId;
	bondData->a = a;
	bondData->b = b;
	bondData->supplementalData = 0;
	
	bondId2Bond.push_back(bondData);
	NXABMInt bondDataId = bondId2Bond.size() - 1;
	
	moleculeId2BondIds[moleculeId].push_back(bondDataId);
	
	NXMoleculeData* moleculeData = moleculeId2Molecule[moleculeId];
	moleculeSet2BondIds[moleculeData->moleculeSet].push_back(bondDataId);
	
	return bondDataId;
}


/* FUNCTION: bondsBegin */
NXBondIdIterator NXEntityManager::bondsBegin(NXMoleculeSet* moleculeSet) {
	return moleculeSet2BondIds[moleculeSet].begin();
}
NXBondIdIterator NXEntityManager::bondsBegin(const NXABMInt& moleculeId) {
	return moleculeId2BondIds[moleculeId].begin();
}


/* FUNCTION: bondsEnd */
NXBondIdIterator NXEntityManager::bondsEnd(NXMoleculeSet* moleculeSet) {
	return moleculeSet2BondIds[moleculeSet].end();
}
NXBondIdIterator NXEntityManager::bondsEnd(const NXABMInt& moleculeId) {
	return moleculeId2BondIds[moleculeId].end();
}


} // Nanorex::
