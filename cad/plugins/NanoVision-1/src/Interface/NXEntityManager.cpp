
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXEntityManager.h"

namespace Nanorex {


/* CONSTRUCTOR */
NXEntityManager::NXEntityManager() {
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

} // Nanorex::
