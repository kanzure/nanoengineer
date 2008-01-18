
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
	
	int pluginIndex = 0;
	string msg, pluginFormats;
	string pluginKey = "NXEntityManager.importExport.0";
	string pluginLibrary =
		string(properties->getProperty(pluginKey + ".plugin"));

	if (pluginLibrary.length() == 0) {
		msg = "No Data Import/Export plugins to load.";
		cout << "WARNING: " << msg << endl;
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
			cout << "WARNING: " << msg << endl;

		} else {
			// Import formats
			pluginFormats =
				string(properties->getProperty(pluginKey +
							".importFormats"));
			NXStringTokenizer tokenizer(pluginFormats, ",");
			while (tokenizer.hasMoreTokens()) {
				dataImportTable[tokenizer.getNextToken()] = plugin;
			}

			// Export formats
			pluginFormats =
				string(properties->getProperty(pluginKey +
							".exportFormats"));
			tokenizer = NXStringTokenizer(pluginFormats, ",");
			while (tokenizer.hasMoreTokens()) {
				dataExportTable[tokenizer.getNextToken()] = plugin;
			}
		}
		pluginIndex++;
		pluginKey =
			string("NXEntityManager.importExport.") +
			NXUtility::itos(pluginIndex);
		pluginLibrary =
			string(properties->getProperty(pluginKey + ".plugin"));
	}
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
/* FUNCTION: importFromFile */
NXCommandResult* NXEntityManager::importFromFile(NXMoleculeSet* moleculeSet,
												 const string& type,
												 const string& file) {

	NXCommandResult* result;
	//PR_Lock(importExportPluginsMutex);
	map<string, NXDataImportExportPlugin*>::iterator iter =
		dataImportTable.find(type);
	if (iter != dataImportTable.end()) {
		NXDataImportExportPlugin* plugin = iter->second;

		try {
			plugin->setMode(type);
			result = plugin->importFromFile(moleculeSet, file);

		} catch (...) {
			string msg = type;
			msg += "->importFromFile() threw exception";
			NXLOG_SEVERE("NXEntityManager", msg);

			result = new NXCommandResult();
			result->setResult(NX_PLUGIN_CAUSED_ERROR);
			vector<QString> resultVector;
			resultVector.push_back("NXEntityManager");
			QString pluginDescriptor = type.c_str();
			pluginDescriptor.append("->importFromFile()");
			resultVector.push_back(pluginDescriptor);
			resultVector.push_back("threw exception");
			result->setParamVector(resultVector);
		}

	} else {
		string msg =
			"importFromFile: no NXDataImportExportPlugin found to handle type: " +
			type;
		NXLOG_WARNING("NXEntityManager", msg);

		result = new NXCommandResult();
		result->setResult(NX_PLUGIN_NOT_FOUND);
		vector<QString> resultVector;
		resultVector.push_back("NXEntityManager");
		resultVector.push_back(type.c_str());
		resultVector.push_back("not found");
		result->setParamVector(resultVector);
	}
	//PR_Unlock(importExportPluginsMutex);
	return result;
}




/* FUNCTION: exportToFile */
/**
 * Exports the system to the specified file with the appropriate
 * import/export plugin.
 */
NXCommandResult* NXEntityManager::exportToFile(NXMoleculeSet* moleculeSet,
											   const string& type,
											   const string& file) {
	NXCommandResult* result;
	//PR_Lock(importExportPluginsMutex);
	map<string, NXDataImportExportPlugin*>::iterator iter =
		dataExportTable.find(type);
	if (iter != dataExportTable.end()) {
		NXDataImportExportPlugin* plugin = iter->second;
		try {
			plugin->setMode(type);
			result = plugin->exportToFile(moleculeSet, file);

		} catch (...) {
			string msg = type;
			msg += "->exportToFile() threw exception";
			NXLOG_SEVERE("NXEntityManager", msg);

			result = new NXCommandResult();
			result->setResult(NX_PLUGIN_CAUSED_ERROR);
			std::vector<QString> resultVector;
			resultVector.push_back("NXEntityManager");
			QString pluginDescriptor = type.c_str();
			pluginDescriptor.append("->exportToFile()");
			resultVector.push_back(pluginDescriptor);
			resultVector.push_back("threw exception");
			result->setParamVector(resultVector);
		}

	} else {
		std::string msg =
			"exportToFile: no DataImportExportPlugin found to handle type: " +
			type;
		NXLOG_WARNING("NXEntityManager", msg);

		result = new NXCommandResult();
		result->setResult(NX_PLUGIN_NOT_FOUND);
		// %1 Who is reporting
		// %2 The name of the plugin that was not found
		// %3 Why the plugin was not found
		std::vector<QString> resultVector;
		resultVector.push_back("NXEntityManager");
		resultVector.push_back(type.c_str());
		resultVector.push_back("not found");
		result->setParamVector(resultVector);
	}
	//PR_Unlock(importExportPluginsMutex);
	return result;
}

} // Nanorex::
